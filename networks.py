"""
GPU Network Integrations - Connect to multiple decentralized GPU providers
"""
import asyncio
import aiohttp
import random
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class GPUListing:
    """Represents a GPU available for rent"""
    provider: str
    gpu_model: str
    vram_gb: int
    price_per_hour: float
    location: str
    availability: str
    uptime_percent: float
    provider_fee: float
    gp4u_fee: float
    total_price: float
    
@dataclass
class ArbitrageOpportunity:
    """Represents a pricing arbitrage opportunity"""
    gpu_model: str
    cheapest_provider: str
    cheapest_price: float
    expensive_provider: str
    expensive_price: float
    savings_percent: float
    savings_amount: float

class NetworkIntegration:
    """Base class for GPU network integrations"""
    
    def __init__(self, config: Dict, network_name: str):
        self.config = config
        self.network_name = network_name
        self.network_config = config.get('networks', {}).get(network_name, {})
        self.enabled = self.network_config.get('enabled', False)
        self.broker_fee = config.get('broker_fee_percent', 1.0)
        
    async def fetch_gpus(self) -> List[GPUListing]:
        """Fetch available GPUs from this network"""
        raise NotImplementedError
        
    def calculate_total_price(self, base_price: float) -> Dict[str, float]:
        """Calculate total price including fees"""
        provider_fee_pct = self.network_config.get('commission_percent', 20.0)
        provider_fee = base_price * (provider_fee_pct / 100)
        gp4u_fee = base_price * (self.broker_fee / 100)
        total = base_price + provider_fee + gp4u_fee
        
        return {
            'base_price': base_price,
            'provider_fee': provider_fee,
            'gp4u_fee': gp4u_fee,
            'total_price': total
        }

class RenderNetworkIntegration(NetworkIntegration):
    """Render Network integration"""
    
    def __init__(self, config: Dict):
        super().__init__(config, 'render')
        
    async def fetch_gpus(self) -> List[GPUListing]:
        """Fetch GPUs from Render Network"""
        if not self.enabled:
            return []
            
        # Simulate API call with mock data
        gpu_models = ['rtx_4090', 'rtx_3090', 'a100', 'h100']
        locations = ['US-East', 'US-West', 'EU-Central', 'Asia-Pacific']
        gpus = []
        
        gpu_specs = self.config.get('gpu_specs', {})
        
        for _ in range(random.randint(3, 6)):
            model = random.choice(gpu_models)
            specs = gpu_specs.get(model, {})
            base_price = specs.get('base_price_per_hour', 2.0)
            
            # Add some variance
            base_price *= random.uniform(0.85, 1.15)
            
            pricing = self.calculate_total_price(base_price)
            
            gpu = GPUListing(
                provider='Render',
                gpu_model=model.replace('_', ' ').upper(),
                vram_gb=specs.get('vram_gb', 24),
                price_per_hour=base_price,
                location=random.choice(locations),
                availability='Available',
                uptime_percent=random.uniform(95, 99.9),
                provider_fee=pricing['provider_fee'],
                gp4u_fee=pricing['gp4u_fee'],
                total_price=pricing['total_price']
            )
            gpus.append(gpu)
            
        return gpus

class AkashNetworkIntegration(NetworkIntegration):
    """Akash Network integration"""
    
    def __init__(self, config: Dict):
        super().__init__(config, 'akash')
        
    async def fetch_gpus(self) -> List[GPUListing]:
        """Fetch GPUs from Akash Network"""
        if not self.enabled:
            return []
            
        gpu_models = ['rtx_3090', 'a100', 'v100', 'a6000']
        locations = ['US-East', 'EU-West', 'Asia']
        gpus = []
        
        gpu_specs = self.config.get('gpu_specs', {})
        
        for _ in range(random.randint(4, 8)):
            model = random.choice(gpu_models)
            specs = gpu_specs.get(model, {})
            base_price = specs.get('base_price_per_hour', 2.0)
            
            # Akash tends to be cheaper
            base_price *= random.uniform(0.75, 1.05)
            
            pricing = self.calculate_total_price(base_price)
            
            gpu = GPUListing(
                provider='Akash',
                gpu_model=model.replace('_', ' ').upper(),
                vram_gb=specs.get('vram_gb', 24),
                price_per_hour=base_price,
                location=random.choice(locations),
                availability='Available',
                uptime_percent=random.uniform(92, 98),
                provider_fee=pricing['provider_fee'],
                gp4u_fee=pricing['gp4u_fee'],
                total_price=pricing['total_price']
            )
            gpus.append(gpu)
            
        return gpus

class IoNetIntegration(NetworkIntegration):
    """io.net integration"""
    
    def __init__(self, config: Dict):
        super().__init__(config, 'ionet')
        
    async def fetch_gpus(self) -> List[GPUListing]:
        """Fetch GPUs from io.net"""
        if not self.enabled:
            return []
            
        gpu_models = ['rtx_4090', 'h100', 'a100']
        locations = ['US-Central', 'EU-North', 'Singapore']
        gpus = []
        
        gpu_specs = self.config.get('gpu_specs', {})
        
        for _ in range(random.randint(2, 5)):
            model = random.choice(gpu_models)
            specs = gpu_specs.get(model, {})
            base_price = specs.get('base_price_per_hour', 2.0)
            
            # io.net pricing
            base_price *= random.uniform(0.9, 1.2)
            
            pricing = self.calculate_total_price(base_price)
            
            gpu = GPUListing(
                provider='io.net',
                gpu_model=model.replace('_', ' ').upper(),
                vram_gb=specs.get('vram_gb', 24),
                price_per_hour=base_price,
                location=random.choice(locations),
                availability='Available',
                uptime_percent=random.uniform(94, 99),
                provider_fee=pricing['provider_fee'],
                gp4u_fee=pricing['gp4u_fee'],
                total_price=pricing['total_price']
            )
            gpus.append(gpu)
            
        return gpus

class VastAIIntegration(NetworkIntegration):
    """Vast.ai integration"""
    
    def __init__(self, config: Dict):
        super().__init__(config, 'vastai')
        
    async def fetch_gpus(self) -> List[GPUListing]:
        """Fetch GPUs from Vast.ai"""
        if not self.enabled:
            return []
            
        gpu_models = ['rtx_3090', 'rtx_4090', 'a100', 'v100', 'a6000']
        locations = ['US-East', 'US-West', 'Canada', 'EU-Central']
        gpus = []
        
        gpu_specs = self.config.get('gpu_specs', {})
        
        for _ in range(random.randint(5, 10)):
            model = random.choice(gpu_models)
            specs = gpu_specs.get(model, {})
            base_price = specs.get('base_price_per_hour', 2.0)
            
            # Vast.ai has wide price ranges
            base_price *= random.uniform(0.7, 1.4)
            
            pricing = self.calculate_total_price(base_price)
            
            gpu = GPUListing(
                provider='Vast.ai',
                gpu_model=model.replace('_', ' ').upper(),
                vram_gb=specs.get('vram_gb', 24),
                price_per_hour=base_price,
                location=random.choice(locations),
                availability='Available' if random.random() > 0.2 else 'Reserved',
                uptime_percent=random.uniform(90, 99),
                provider_fee=pricing['provider_fee'],
                gp4u_fee=pricing['gp4u_fee'],
                total_price=pricing['total_price']
            )
            gpus.append(gpu)
            
        return gpus

class GP4UNetworkAggregator:
    """Aggregates GPU listings from all networks"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.integrations = [
            RenderNetworkIntegration(config),
            AkashNetworkIntegration(config),
            IoNetIntegration(config),
            VastAIIntegration(config)
        ]
        
    async def fetch_all_gpus(self) -> List[GPUListing]:
        """Fetch GPUs from all enabled networks"""
        tasks = [integration.fetch_gpus() for integration in self.integrations]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_gpus = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Error fetching GPUs: {result}")
            else:
                all_gpus.extend(result)
        
        return all_gpus
    
    def find_arbitrage_opportunities(self, gpus: List[GPUListing]) -> List[ArbitrageOpportunity]:
        """Find pricing arbitrage opportunities"""
        opportunities = []
        
        # Group by GPU model
        by_model = {}
        for gpu in gpus:
            if gpu.availability != 'Available':
                continue
            model = gpu.gpu_model
            if model not in by_model:
                by_model[model] = []
            by_model[model].append(gpu)
        
        # Find price differences
        min_savings_pct = self.config.get('arbitrage', {}).get('min_savings_percent', 15.0)
        
        for model, listings in by_model.items():
            if len(listings) < 2:
                continue
            
            # Sort by total price
            sorted_listings = sorted(listings, key=lambda x: x.total_price)
            cheapest = sorted_listings[0]
            most_expensive = sorted_listings[-1]
            
            savings_amount = most_expensive.total_price - cheapest.total_price
            savings_percent = (savings_amount / most_expensive.total_price) * 100
            
            if savings_percent >= min_savings_pct:
                opp = ArbitrageOpportunity(
                    gpu_model=model,
                    cheapest_provider=cheapest.provider,
                    cheapest_price=cheapest.total_price,
                    expensive_provider=most_expensive.provider,
                    expensive_price=most_expensive.total_price,
                    savings_percent=savings_percent,
                    savings_amount=savings_amount
                )
                opportunities.append(opp)
        
        return sorted(opportunities, key=lambda x: x.savings_percent, reverse=True)
    
    def get_network_stats(self, gpus: List[GPUListing]) -> Dict:
        """Get statistics by network"""
        stats = {}
        
        for gpu in gpus:
            provider = gpu.provider
            if provider not in stats:
                stats[provider] = {
                    'count': 0,
                    'avg_price': 0,
                    'min_price': float('inf'),
                    'max_price': 0
                }
            
            stats[provider]['count'] += 1
            stats[provider]['min_price'] = min(stats[provider]['min_price'], gpu.total_price)
            stats[provider]['max_price'] = max(stats[provider]['max_price'], gpu.total_price)
        
        # Calculate averages
        for provider, data in stats.items():
            provider_gpus = [g for g in gpus if g.provider == provider]
            if provider_gpus:
                data['avg_price'] = sum(g.total_price for g in provider_gpus) / len(provider_gpus)
        
        return stats
