"""
io.net Provider Integration
Decentralized GPU network
"""
import random
from typing import List, Dict, Optional
from decimal import Decimal

from .base import BaseProvider


class IoNetProvider(BaseProvider):
    """io.net GPU provider"""

    GPU_MODELS = [
        {
            'model': 'RTX 4090',
            'vram_gb': 24,
            'base_price': Decimal('2.30'),
            'benchmark': 9500,
            'max_power': 450
        },
        {
            'model': 'H100',
            'vram_gb': 80,
            'base_price': Decimal('6.00'),
            'benchmark': 9800,
            'max_power': 700
        },
        {
            'model': 'A100',
            'vram_gb': 80,
            'base_price': Decimal('3.80'),
            'benchmark': 8500,
            'max_power': 400
        },
    ]

    LOCATIONS = ['US-Central', 'EU-North', 'Singapore']

    async def fetch_gpus(self) -> List[Dict]:
        """
        Fetch available GPUs from io.net

        Note: io.net focuses on high-end GPUs
        """
        self.log_info("Fetching GPUs from io.net")

        gpus = []
        num_gpus = random.randint(2, 5)

        for i in range(num_gpus):
            gpu_spec = random.choice(self.GPU_MODELS)

            price_variance = random.uniform(0.9, 1.2)
            price = gpu_spec['base_price'] * Decimal(str(price_variance))

            uptime = Decimal(str(random.uniform(94, 99)))
            power = int(gpu_spec['max_power'] * random.uniform(0.75, 0.95))

            gpu = {
                'provider': 'io.net',
                'external_id': f"ionet-{i+1}",
                'model': gpu_spec['model'],
                'vram_gb': gpu_spec['vram_gb'],
                'price_per_hour': price,
                'location': random.choice(self.LOCATIONS),
                'available': random.random() > 0.2,  # 80% available
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

        self.log_info(f"Fetched {len(gpus)} GPUs from io.net")
        return gpus

    async def get_gpu_details(self, external_id: str) -> Optional[Dict]:
        """Get details for specific GPU"""
        gpus = await self.fetch_gpus()
        for gpu in gpus:
            if gpu['external_id'] == external_id:
                return gpu
        return None
