"""
Render Network Provider Implementation
Decentralized GPU rendering platform
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

import httpx

from ..core.base_provider import BaseProvider
from ..core.provider_config import get_provider_config


logger = logging.getLogger(__name__)


class RenderProvider(BaseProvider):
    """
    Render Network GPU Provider

    Documentation: https://rendernetwork.com/

    Features:
    - Specialized for 3D rendering and AI imaging
    - OctaneRender, Redshift, Blender Cycles support
    - Generative AI tools (Runway, Stability AI)
    - RNDR/RENDER token payment
    - Node operator earnings system
    """

    def __init__(self):
        super().__init__("render")

        config = get_provider_config()
        self.api_key = config.render_api_key
        self.base_url = config.render_base_url

        # Update client headers with API key
        if self.api_key:
            self.client.headers.update({
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            })

        logger.info("Render Network provider initialized")

    async def fetch_gpus(self) -> List[Dict[str, Any]]:
        """
        Fetch available GPUs from Render Network

        Endpoint: GET /api/nodes

        Returns:
            List of raw GPU data from Render Network
        """
        try:
            url = f"{self.base_url}/nodes"

            params = {
                "status": "active",  # Only active nodes
                "tier": "all",  # All tiers
            }

            response = await self.client.get(url, params=params)
            response.raise_for_status()

            data = response.json()

            # Render returns {"nodes": [...]}
            nodes = data.get("nodes", [])

            logger.info(f"Render: Fetched {len(nodes)} render nodes")

            return nodes

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                logger.error("Render: Invalid API key")
                raise Exception("Render Network authentication failed - check API key")
            elif e.response.status_code == 429:
                logger.warning("Render: Rate limit exceeded")
                raise Exception("Render Network rate limit exceeded")
            else:
                logger.error(f"Render HTTP error: {e}")
                raise

        except Exception as e:
            logger.error(f"Render fetch error: {str(e)}")
            raise

    def normalize_gpu_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize Render Network GPU data to common format

        Render Network fields:
        - node_id: Unique node identifier
        - gpu_model: GPU model name
        - gpu_memory: VRAM in GB
        - octanebench_score: OctaneBench performance score
        - tier: Node tier (1-4, with 1 being highest)
        - price_per_obh: Price per OctaneBench hour
        - location: Geographic location
        - supported_engines: Rendering engines supported
        - ai_capabilities: AI/ML features available
        - uptime: Node uptime percentage
        - reputation: Node operator reputation
        """
        # Calculate G-Score
        # Render focuses on rendering performance
        octanebench_score = float(raw_data.get("octanebench_score", 100))
        performance = min(octanebench_score / 1000.0, 1.0)  # Normalize (1000+ is excellent)

        uptime = float(raw_data.get("uptime", 95)) / 100.0
        reputation = float(raw_data.get("reputation", 80)) / 100.0
        reliability = (uptime + reputation) / 2.0

        price = float(raw_data.get("price_per_obh", 0.01))
        # Convert OctaneBench hours to regular hours (approximate)
        price_per_hour = price * (octanebench_score / 100.0)
        efficiency = 1.0 / (price_per_hour + 0.1)
        efficiency = min(efficiency, 1.0)

        g_score = (performance * 0.5 + reliability * 0.3 + efficiency * 0.2) * 100

        # Boost for AI capabilities
        if raw_data.get("ai_capabilities", False):
            g_score *= 1.05
            g_score = min(g_score, 100)

        # Tier affects availability (Tier 1 is most reliable)
        tier = int(raw_data.get("tier", 3))
        available = tier <= 3  # Tiers 1-3 are generally available

        return {
            "provider": "Render Network",
            "external_id": str(raw_data.get("node_id")),
            "model": raw_data.get("gpu_model", "Unknown"),
            "vram_gb": int(raw_data.get("gpu_memory", 0)),
            "price_per_hour": round(price_per_hour, 4),
            "available": available,
            "location": raw_data.get("location", "Unknown"),
            "g_score": round(g_score, 2),
            "specs": {
                "octanebench_score": int(octanebench_score),
                "tier": tier,
                "supported_engines": raw_data.get("supported_engines", []),
                "ai_capabilities": raw_data.get("ai_capabilities", False),
                "cuda_version": raw_data.get("cuda_version", "Unknown"),
                "driver_version": raw_data.get("driver_version", "Unknown"),
                "performance_score": performance,
                "reliability_score": reliability,
                "uptime_percentage": float(raw_data.get("uptime", 0)),
            },
            "metadata": {
                "node_operator": raw_data.get("operator_id"),
                "reputation": float(raw_data.get("reputation", 0)),
                "jobs_completed": int(raw_data.get("jobs_completed", 0)),
                "average_render_time": float(raw_data.get("average_render_time", 0)),
                "payment_method": "RENDER_token",
                "rendering_focus": True,
                "generative_ai": raw_data.get("ai_capabilities", False),
            },
            "last_updated": datetime.utcnow().isoformat(),
        }

    async def get_node_details(self, node_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific node

        Args:
            node_id: Render Network node ID

        Returns:
            Detailed node information or None if not found
        """
        try:
            url = f"{self.base_url}/nodes/{node_id}"
            response = await self.client.get(url)
            response.raise_for_status()

            data = response.json()
            return self.normalize_gpu_data(data)

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning(f"Render: Node {node_id} not found")
                return None
            raise

        except Exception as e:
            logger.error(f"Render: Error fetching node {node_id}: {str(e)}")
            raise

    async def submit_render_job(
        self,
        node_id: str,
        scene_file: str,
        engine: str = "octane",
        frames: int = 1,
    ) -> Dict[str, Any]:
        """
        Submit a rendering job to Render Network

        Args:
            node_id: Node ID to use for rendering
            scene_file: Scene file URL or path
            engine: Rendering engine (octane, redshift, cycles)
            frames: Number of frames to render

        Returns:
            Job submission response
        """
        try:
            url = f"{self.base_url}/jobs"

            payload = {
                "node_id": node_id,
                "scene_file": scene_file,
                "engine": engine,
                "frames": frames,
                "priority": "normal",
            }

            response = await self.client.post(url, json=payload)
            response.raise_for_status()

            result = response.json()

            logger.info(f"Render: Submitted job {result.get('job_id')}")

            return result

        except Exception as e:
            logger.error(f"Render: Error submitting job: {str(e)}")
            raise

    async def generate_ai_image(
        self,
        prompt: str,
        model: str = "stability-xl",
        width: int = 1024,
        height: int = 1024,
    ) -> Dict[str, Any]:
        """
        Generate an AI image using Render Network

        Args:
            prompt: Text prompt for generation
            model: AI model (stability-xl, runway, flux)
            width: Image width
            height: Image height

        Returns:
            Generation response with image URL
        """
        try:
            url = f"{self.base_url}/ai/generate"

            payload = {
                "prompt": prompt,
                "model": model,
                "width": width,
                "height": height,
                "steps": 30,
            }

            response = await self.client.post(url, json=payload)
            response.raise_for_status()

            result = response.json()

            logger.info(f"Render: Generated AI image {result.get('image_id')}")

            return result

        except Exception as e:
            logger.error(f"Render: Error generating AI image: {str(e)}")
            raise

    async def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """
        Get rendering job status

        Args:
            job_id: Job ID

        Returns:
            Job status and progress
        """
        try:
            url = f"{self.base_url}/jobs/{job_id}"
            response = await self.client.get(url)
            response.raise_for_status()

            return response.json()

        except Exception as e:
            logger.error(f"Render: Error getting job status: {str(e)}")
            raise

    def __repr__(self) -> str:
        return f"<RenderProvider(status='{self.get_status().value}', api_key={'set' if self.api_key else 'not set'})>"
