"""
Vast.ai Provider Implementation
Direct GPU instance rental marketplace
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

import httpx

from ..core.base_provider import BaseProvider
from ..core.provider_config import get_provider_config


logger = logging.getLogger(__name__)


class VastAIProvider(BaseProvider):
    """
    Vast.ai GPU Provider

    API Documentation: https://docs.vast.ai/api

    Features:
    - Direct GPU instance rental
    - Real-time availability
    - Detailed GPU specifications
    - Competitive pricing
    """

    def __init__(self):
        super().__init__("vastai")

        config = get_provider_config()
        self.api_key = config.vastai_api_key
        self.base_url = config.vastai_base_url

        # Update client headers with API key
        if self.api_key:
            self.client.headers.update({
                "Authorization": f"Bearer {self.api_key}"
            })

        logger.info("Vast.ai provider initialized")

    async def fetch_gpus(self) -> List[Dict[str, Any]]:
        """
        Fetch available GPUs from Vast.ai

        Endpoint: GET /bundles

        Returns:
            List of raw GPU data from Vast.ai
        """
        try:
            # Vast.ai search endpoint
            url = f"{self.base_url}/bundles"

            params = {
                "order": "score-",  # Order by score descending
                "type": "on-demand",  # Only on-demand instances
            }

            response = await self.client.get(url, params=params)
            response.raise_for_status()

            data = response.json()

            # Vast.ai returns {"offers": [...]}
            offers = data.get("offers", [])

            logger.info(f"Vast.ai: Fetched {len(offers)} GPU offers")

            return offers

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                logger.error("Vast.ai: Invalid API key")
                raise Exception("Vast.ai authentication failed - check API key")
            elif e.response.status_code == 429:
                logger.warning("Vast.ai: Rate limit exceeded")
                raise Exception("Vast.ai rate limit exceeded")
            else:
                logger.error(f"Vast.ai HTTP error: {e}")
                raise

        except Exception as e:
            logger.error(f"Vast.ai fetch error: {str(e)}")
            raise

    def normalize_gpu_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize Vast.ai GPU data to common format

        Vast.ai fields:
        - gpu_name: GPU model (e.g., "RTX 4090")
        - cpu_name: CPU model
        - num_gpus: Number of GPUs
        - gpu_ram: VRAM in GB
        - dph_total: Price per hour
        - dlperf: Deep learning performance score
        - reliability2: Reliability score (0-1)
        - inet_down: Download speed Mbps
        - inet_up: Upload speed Mbps
        - geolocation: Location
        - machine_id: Unique machine ID
        - storage_cost: Storage price
        - disk_space: Available disk GB
        """
        # Calculate G-Score (Performance × Reliability × Efficiency)
        performance = float(raw_data.get("dlperf", 0)) / 100.0  # Normalize to 0-1
        reliability = float(raw_data.get("reliability2", 0.5))

        # Efficiency: inverse of price (lower price = higher efficiency)
        price = float(raw_data.get("dph_total", 1.0))
        efficiency = 1.0 / (price + 0.1)  # Add 0.1 to prevent division by zero
        efficiency = min(efficiency, 1.0)  # Cap at 1.0

        g_score = (performance * 0.4 + reliability * 0.4 + efficiency * 0.2) * 100

        # Determine availability (Vast.ai shows only available machines)
        available = True

        return {
            "provider": "Vast.ai",
            "external_id": str(raw_data.get("id")),
            "model": raw_data.get("gpu_name", "Unknown"),
            "vram_gb": int(raw_data.get("gpu_ram", 0) / 1024),  # Convert MB to GB
            "price_per_hour": round(float(raw_data.get("dph_total", 0)), 4),
            "available": available,
            "location": raw_data.get("geolocation", "Unknown"),
            "g_score": round(g_score, 2),
            "specs": {
                "num_gpus": int(raw_data.get("num_gpus", 1)),
                "cpu_name": raw_data.get("cpu_name", "Unknown"),
                "cpu_ram_gb": int(raw_data.get("cpu_ram", 0) / 1024),  # MB to GB
                "disk_space_gb": float(raw_data.get("disk_space", 0)),
                "download_speed_mbps": float(raw_data.get("inet_down", 0)),
                "upload_speed_mbps": float(raw_data.get("inet_up", 0)),
                "cuda_version": raw_data.get("cuda_max_good", "Unknown"),
                "performance_score": performance,
                "reliability_score": reliability,
            },
            "metadata": {
                "machine_id": raw_data.get("machine_id"),
                "storage_cost": float(raw_data.get("storage_cost", 0)),
                "verification": raw_data.get("verification", "unverified"),
                "direct_port_count": int(raw_data.get("direct_port_count", 0)),
            },
            "last_updated": datetime.utcnow().isoformat(),
        }

    async def get_gpu_details(self, gpu_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific GPU

        Args:
            gpu_id: Vast.ai machine ID

        Returns:
            Detailed GPU information or None if not found
        """
        try:
            url = f"{self.base_url}/bundles/{gpu_id}"
            response = await self.client.get(url)
            response.raise_for_status()

            data = response.json()
            return self.normalize_gpu_data(data)

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning(f"Vast.ai: GPU {gpu_id} not found")
                return None
            raise

        except Exception as e:
            logger.error(f"Vast.ai: Error fetching GPU {gpu_id}: {str(e)}")
            raise

    async def create_instance(
        self,
        gpu_id: str,
        image: str = "pytorch/pytorch:latest",
        disk_space: int = 10,
    ) -> Dict[str, Any]:
        """
        Create a Vast.ai GPU instance

        Args:
            gpu_id: Machine ID to rent
            image: Docker image to use
            disk_space: Disk space in GB

        Returns:
            Instance creation response
        """
        try:
            url = f"{self.base_url}/asks/{gpu_id}"

            payload = {
                "image": image,
                "disk": disk_space,
                "onstart": "echo 'Instance started'",
            }

            response = await self.client.put(url, json=payload)
            response.raise_for_status()

            result = response.json()

            logger.info(f"Vast.ai: Created instance {result.get('new_contract')}")

            return result

        except Exception as e:
            logger.error(f"Vast.ai: Error creating instance: {str(e)}")
            raise

    async def destroy_instance(self, instance_id: str) -> bool:
        """
        Destroy a Vast.ai GPU instance

        Args:
            instance_id: Contract ID to destroy

        Returns:
            True if successful
        """
        try:
            url = f"{self.base_url}/instances/{instance_id}"
            response = await self.client.delete(url)
            response.raise_for_status()

            logger.info(f"Vast.ai: Destroyed instance {instance_id}")
            return True

        except Exception as e:
            logger.error(f"Vast.ai: Error destroying instance: {str(e)}")
            raise

    def __repr__(self) -> str:
        return f"<VastAIProvider(status='{self.get_status().value}', api_key={'set' if self.api_key else 'not set'})>"
