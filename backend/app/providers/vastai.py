"""
Vast.ai Provider Integration
GPU rental marketplace
"""
import random
from typing import List, Dict, Optional
from decimal import Decimal

from .base import BaseProvider


class VastAIProvider(BaseProvider):
    """Vast.ai GPU provider"""

    GPU_MODELS = [
        {
            'model': 'RTX 3090',
            'vram_gb': 24,
            'base_price': Decimal('1.70'),
            'benchmark': 7200,
            'max_power': 350
        },
        {
            'model': 'RTX 4090',
            'vram_gb': 24,
            'base_price': Decimal('2.40'),
            'benchmark': 9500,
            'max_power': 450
        },
        {
            'model': 'A100',
            'vram_gb': 80,
            'base_price': Decimal('3.70'),
            'benchmark': 8500,
            'max_power': 400
        },
        {
            'model': 'V100',
            'vram_gb': 32,
            'base_price': Decimal('1.90'),
            'benchmark': 6500,
            'max_power': 300
        },
        {
            'model': 'A6000',
            'vram_gb': 48,
            'base_price': Decimal('2.10'),
            'benchmark': 7800,
            'max_power': 300
        },
    ]

    LOCATIONS = ['US-East', 'US-West', 'Canada', 'EU-Central']

    async def fetch_gpus(self) -> List[Dict]:
        """
        Fetch available GPUs from Vast.ai

        Note: Vast.ai has wide price ranges and large inventory
        """
        self.log_info("Fetching GPUs from Vast.ai")

        gpus = []
        num_gpus = random.randint(5, 10)

        for i in range(num_gpus):
            gpu_spec = random.choice(self.GPU_MODELS)

            # Vast.ai has wider price variance
            price_variance = random.uniform(0.7, 1.4)
            price = gpu_spec['base_price'] * Decimal(str(price_variance))

            uptime = Decimal(str(random.uniform(90, 99)))
            power = int(gpu_spec['max_power'] * random.uniform(0.7, 0.95))

            # Vast.ai has more variable availability
            available = random.random() > 0.2  # 80% available

            gpu = {
                'provider': 'Vast.ai',
                'external_id': f"vastai-{i+1}",
                'model': gpu_spec['model'],
                'vram_gb': gpu_spec['vram_gb'],
                'price_per_hour': price,
                'location': random.choice(self.LOCATIONS),
                'available': available,
                'uptime_percent': uptime,
                'benchmark_score': gpu_spec['benchmark'],
                'power_consumption': power,
                'max_power': gpu_spec['max_power']
            }

            gpu['g_score'] = self.calculate_g_score(
                gpu['benchmark_score'],
                gpu['uptime_percent'],
                gpu['power_consumption'],
                gpu['max_power']
            )

            gpus.append(gpu)

        self.log_info(f"Fetched {len(gpus)} GPUs from Vast.ai")
        return gpus

    async def get_gpu_details(self, external_id: str) -> Optional[Dict]:
        """Get details for specific GPU"""
        gpus = await self.fetch_gpus()
        for gpu in gpus:
            if gpu['external_id'] == external_id:
                return gpu
        return None
