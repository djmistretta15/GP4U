"""
io.net Provider Implementation
Decentralized GPU cloud for AI/ML workloads
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

import httpx

from ..core.base_provider import BaseProvider
from ..core.provider_config import get_provider_config


logger = logging.getLogger(__name__)


class IONetProvider(BaseProvider):
    """
    io.net GPU Provider

    API Documentation: https://developers.io.net/docs

    Features:
    - Decentralized GPU cloud
    - AI/ML optimized
    - 327,000+ verified GPUs
    - Up to 70% cost savings vs AWS/GCP
    - Cluster-ready GPUs
    """

    def __init__(self):
        super().__init__("ionet")

        config = get_provider_config()
        self.api_key = config.ionet_api_key
        self.base_url = config.ionet_base_url

        # Update client headers with API key
        if self.api_key:
            self.client.headers.update({
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            })

        logger.info("io.net provider initialized")

    async def fetch_gpus(self) -> List[Dict[str, Any]]:
        """
        Fetch available GPUs from io.net

        Endpoint: GET /v1/devices

        Returns:
            List of raw GPU data from io.net
        """
        try:
            url = f"{self.base_url}/devices"

            params = {
                "status": "available",  # Only available devices
                "verified": "true",  # Only verified GPUs
                "limit": 1000,  # Max results
            }

            response = await self.client.get(url, params=params)
            response.raise_for_status()

            data = response.json()

            # io.net returns {"devices": [...], "total": N}
            devices = data.get("devices", [])

            logger.info(f"io.net: Fetched {len(devices)} GPU devices")

            return devices

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                logger.error("io.net: Invalid API key")
                raise Exception("io.net authentication failed - check API key")
            elif e.response.status_code == 429:
                logger.warning("io.net: Rate limit exceeded (150 req/10s)")
                raise Exception("io.net rate limit exceeded")
            else:
                logger.error(f"io.net HTTP error: {e}")
                raise

        except Exception as e:
            logger.error(f"io.net fetch error: {str(e)}")
            raise

    def normalize_gpu_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize io.net GPU data to common format

        io.net fields:
        - device_id: Unique device ID
        - gpu_model: GPU model name
        - gpu_memory: VRAM in GB
        - price_per_hour: Hourly rate in USD
        - compute_capability: CUDA compute capability
        - availability: Availability status
        - location: Geographic location
        - cluster_ready: Whether GPU is cluster-ready
        - performance_score: Performance rating
        - provider_reputation: Provider reliability score
        - bandwidth_gbps: Network bandwidth
        """
        # Calculate G-Score
        # io.net focuses on AI/ML, so prioritize compute capability
        performance = float(raw_data.get("performance_score", 50)) / 100.0
        reliability = float(raw_data.get("provider_reputation", 80)) / 100.0

        price = float(raw_data.get("price_per_hour", 1.0))
        efficiency = 1.0 / (price + 0.1)
        efficiency = min(efficiency, 1.0)

        g_score = (performance * 0.5 + reliability * 0.3 + efficiency * 0.2) * 100

        # Availability
        available = raw_data.get("availability") == "available"

        # Boost score for cluster-ready GPUs
        if raw_data.get("cluster_ready", False):
            g_score *= 1.1  # 10% boost
            g_score = min(g_score, 100)  # Cap at 100

        return {
            "provider": "io.net",
            "external_id": str(raw_data.get("device_id")),
            "model": raw_data.get("gpu_model", "Unknown"),
            "vram_gb": int(raw_data.get("gpu_memory", 0)),
            "price_per_hour": round(float(raw_data.get("price_per_hour", 0)), 4),
            "available": available,
            "location": raw_data.get("location", "Unknown"),
            "g_score": round(g_score, 2),
            "specs": {
                "compute_capability": raw_data.get("compute_capability", "Unknown"),
                "cuda_cores": int(raw_data.get("cuda_cores", 0)),
                "tensor_cores": int(raw_data.get("tensor_cores", 0)),
                "memory_bandwidth_gbps": float(raw_data.get("memory_bandwidth", 0)),
                "network_bandwidth_gbps": float(raw_data.get("bandwidth_gbps", 0)),
                "cluster_ready": raw_data.get("cluster_ready", False),
                "performance_score": performance,
                "reliability_score": reliability,
                "max_power_draw": int(raw_data.get("max_power_draw", 0)),
            },
            "metadata": {
                "provider_id": raw_data.get("provider_id"),
                "provider_reputation": float(raw_data.get("provider_reputation", 0)),
                "uptime_percentage": float(raw_data.get("uptime_percentage", 0)),
                "supported_frameworks": raw_data.get("supported_frameworks", []),
                "container_support": raw_data.get("container_support", False),
                "bare_metal": raw_data.get("bare_metal", False),
            },
            "last_updated": datetime.utcnow().isoformat(),
        }

    async def get_gpu_details(self, gpu_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific GPU

        Args:
            gpu_id: io.net device ID

        Returns:
            Detailed GPU information or None if not found
        """
        try:
            url = f"{self.base_url}/devices/{gpu_id}"
            response = await self.client.get(url)
            response.raise_for_status()

            data = response.json()
            return self.normalize_gpu_data(data)

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning(f"io.net: GPU {gpu_id} not found")
                return None
            raise

        except Exception as e:
            logger.error(f"io.net: Error fetching GPU {gpu_id}: {str(e)}")
            raise

    async def create_cluster(
        self,
        gpu_ids: List[str],
        framework: str = "pytorch",
        cluster_type: str = "distributed",
    ) -> Dict[str, Any]:
        """
        Create an io.net GPU cluster

        Args:
            gpu_ids: List of device IDs to include in cluster
            framework: ML framework (pytorch, tensorflow, jax)
            cluster_type: Cluster type (distributed, ray, kubernetes)

        Returns:
            Cluster creation response
        """
        try:
            url = f"{self.base_url}/clusters"

            payload = {
                "device_ids": gpu_ids,
                "framework": framework,
                "cluster_type": cluster_type,
                "auto_scaling": False,
            }

            response = await self.client.post(url, json=payload)
            response.raise_for_status()

            result = response.json()

            logger.info(f"io.net: Created cluster {result.get('cluster_id')}")

            return result

        except Exception as e:
            logger.error(f"io.net: Error creating cluster: {str(e)}")
            raise

    async def deploy_container(
        self,
        gpu_id: str,
        image: str,
        command: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Deploy a container on io.net GPU

        Args:
            gpu_id: Device ID
            image: Docker image
            command: Command to run

        Returns:
            Deployment response
        """
        try:
            url = f"{self.base_url}/deployments"

            payload = {
                "device_id": gpu_id,
                "image": image,
                "command": command or [],
                "auto_restart": True,
            }

            response = await self.client.post(url, json=payload)
            response.raise_for_status()

            result = response.json()

            logger.info(f"io.net: Deployed container {result.get('deployment_id')}")

            return result

        except Exception as e:
            logger.error(f"io.net: Error deploying container: {str(e)}")
            raise

    async def get_cluster_status(self, cluster_id: str) -> Dict[str, Any]:
        """
        Get cluster status and metrics

        Args:
            cluster_id: Cluster ID

        Returns:
            Cluster status information
        """
        try:
            url = f"{self.base_url}/clusters/{cluster_id}"
            response = await self.client.get(url)
            response.raise_for_status()

            return response.json()

        except Exception as e:
            logger.error(f"io.net: Error getting cluster status: {str(e)}")
            raise

    def __repr__(self) -> str:
        return f"<IONetProvider(status='{self.get_status().value}', api_key={'set' if self.api_key else 'not set'})>"
