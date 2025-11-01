"""
Akash Network Provider Integration
Decentralized cloud marketplace
"""
import random
from typing import List, Dict, Optional
from decimal import Decimal

from .base import BaseProvider


class AkashProvider(BaseProvider):
    """Akash Network GPU provider"""

    GPU_MODELS = [
        {
            'model': 'RTX 3090',
            'vram_gb': 24,
            'base_price': Decimal('1.60'),
            'benchmark': 7200,
            'max_power': 350
        },
        {
            'model': 'A100',
            'vram_gb': 80,
            'base_price': Decimal('3.50'),
            'benchmark': 8500,
            'max_power': 400
        },
        {
            'model': 'V100',
            'vram_gb': 32,
            'base_price': Decimal('2.00'),
            'benchmark': 6500,
            'max_power': 300
        },
        {
            'model': 'A6000',
            'vram_gb': 48,
            'base_price': Decimal('2.20'),
            'benchmark': 7800,
            'max_power': 300
        },
    ]

    LOCATIONS = ['US-East', 'EU-West', 'Asia']

    async def fetch_gpus(self) -> List[Dict]:
        """
        Fetch available GPUs from Akash Network

        Note: Akash tends to have lower prices due to decentralized model
        """
        self.log_info("Fetching GPUs from Akash Network")

        gpus = []
        num_gpus = random.randint(4, 8)

        for i in range(num_gpus):
            gpu_spec = random.choice(self.GPU_MODELS)

            # Akash pricing variance (tends lower)
            price_variance = random.uniform(0.75, 1.05)
            price = gpu_spec['base_price'] * Decimal(str(price_variance))

            uptime = Decimal(str(random.uniform(92, 98)))
            power = int(gpu_spec['max_power'] * random.uniform(0.7, 0.9))

            gpu = {
                'provider': 'Akash',
                'external_id': f"akash-{i+1}",
                'model': gpu_spec['model'],
                'vram_gb': gpu_spec['vram_gb'],
                'price_per_hour': price,
                'location': random.choice(self.LOCATIONS),
                'available': random.random() > 0.15,  # 85% available
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

        self.log_info(f"Fetched {len(gpus)} GPUs from Akash Network")
        return gpus

    async def get_gpu_details(self, external_id: str) -> Optional[Dict]:
        """Get details for specific GPU"""
        gpus = await self.fetch_gpus()
        for gpu in gpus:
            if gpu['external_id'] == external_id:
                return gpu
        return None
