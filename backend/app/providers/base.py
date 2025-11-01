"""
Base Provider Class
Abstract base for GPU provider integrations
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class BaseProvider(ABC):
    """
    Abstract base class for GPU providers

    Each provider integration should inherit from this class
    and implement the required methods.
    """

    def __init__(self, api_key: Optional[str] = None, config: Optional[Dict] = None):
        """
        Initialize provider

        Args:
            api_key: API key for provider (if required)
            config: Additional configuration
        """
        self.api_key = api_key
        self.config = config or {}
        self.provider_name = self.__class__.__name__.replace("Provider", "")

    @abstractmethod
    async def fetch_gpus(self) -> List[Dict]:
        """
        Fetch available GPUs from provider

        Returns:
            List of GPU dictionaries with standardized format:
            {
                'external_id': str,
                'model': str,
                'vram_gb': int,
                'price_per_hour': Decimal,
                'location': str,
                'available': bool,
                'uptime_percent': Decimal,
                'benchmark_score': int,
                'power_consumption': int,
                'max_power': int
            }
        """
        pass

    @abstractmethod
    async def get_gpu_details(self, external_id: str) -> Optional[Dict]:
        """
        Get detailed information about a specific GPU

        Args:
            external_id: Provider's GPU identifier

        Returns:
            GPU details dictionary or None if not found
        """
        pass

    def calculate_g_score(
        self,
        benchmark_score: int,
        uptime_percent: Decimal,
        power_consumption: int,
        max_power: int
    ) -> Decimal:
        """
        Calculate G-Score (GPU performance score)

        G-Score = Performance × Reliability × Efficiency
        Range: 0.0 to 1.0

        Args:
            benchmark_score: GPU benchmark score
            uptime_percent: Uptime percentage
            power_consumption: Current power consumption in watts
            max_power: Maximum power consumption in watts

        Returns:
            G-Score between 0.0 and 1.0
        """
        # Normalize components
        GPU_MAX_BENCHMARK = 10000  # Arbitrary max for normalization

        performance = min(benchmark_score / GPU_MAX_BENCHMARK, 1.0)
        reliability = uptime_percent / 100
        efficiency = 1 - (power_consumption / max_power) if max_power > 0 else 0.5

        # Weighted average
        g_score = (
            performance * 0.5 +
            reliability * 0.3 +
            efficiency * 0.2
        )

        return Decimal(str(round(g_score, 2)))

    async def validate_connection(self) -> bool:
        """
        Test connection to provider API

        Returns:
            True if connection successful, False otherwise
        """
        try:
            gpus = await self.fetch_gpus()
            return len(gpus) >= 0
        except Exception as e:
            logger.error(f"{self.provider_name} connection failed: {e}")
            return False

    def log_info(self, message: str):
        """Log info message with provider name"""
        logger.info(f"[{self.provider_name}] {message}")

    def log_error(self, message: str):
        """Log error message with provider name"""
        logger.error(f"[{self.provider_name}] {message}")
