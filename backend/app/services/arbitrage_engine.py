"""
GP4U Arbitrage Engine
Core algorithm for finding price differentials across GPU providers
"""
import asyncio
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from collections import defaultdict
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from redis.asyncio import Redis

from app.models import GPU, ArbitrageCache
from app.schemas import ArbitrageOpportunity
from app.core.config import settings

logger = logging.getLogger(__name__)


class ArbitrageEngine:
    """
    Arbitrage detection engine
    Finds price differentials across GPU providers
    """

    def __init__(self, db: AsyncSession, redis: Optional[Redis] = None):
        self.db = db
        self.redis = redis
        self.providers = ['Render', 'Akash', 'io.net', 'Vast.ai']
        self.cache_ttl = settings.ARBITRAGE_CACHE_TTL
        self.min_spread = settings.ARBITRAGE_MIN_SPREAD_PCT

    async def find_opportunities(
        self,
        min_spread_pct: Optional[float] = None,
        gpu_model: Optional[str] = None
    ) -> List[ArbitrageOpportunity]:
        """
        Find arbitrage opportunities across providers

        Args:
            min_spread_pct: Minimum price spread percentage (default from settings)
            gpu_model: Filter by specific GPU model (optional)

        Returns:
            List of arbitrage opportunities sorted by spread percentage
        """
        min_spread = min_spread_pct or self.min_spread

        # Check cache first
        if self.redis:
            cached = await self._get_cached_opportunities(gpu_model)
            if cached:
                logger.info(f"Returning {len(cached)} cached opportunities")
                return cached

        # Fetch fresh opportunities
        opportunities = await self._calculate_opportunities(min_spread, gpu_model)

        # Cache results
        if self.redis and opportunities:
            await self._cache_opportunities(opportunities, gpu_model)

        logger.info(f"Found {len(opportunities)} arbitrage opportunities")
        return opportunities

    async def _calculate_opportunities(
        self,
        min_spread: float,
        gpu_model: Optional[str] = None
    ) -> List[ArbitrageOpportunity]:
        """Calculate fresh arbitrage opportunities"""

        # Fetch available GPUs from last hour
        query = select(GPU).where(
            and_(
                GPU.available == True,
                GPU.last_synced > datetime.utcnow() - timedelta(hours=1)
            )
        )

        if gpu_model:
            query = query.where(GPU.model == gpu_model)

        result = await self.db.execute(query)
        gpus = result.scalars().all()

        if not gpus:
            logger.warning("No GPUs available for arbitrage calculation")
            return []

        # Group GPUs by model
        by_model = defaultdict(list)
        for gpu in gpus:
            by_model[gpu.model].append(gpu)

        # Find price differentials
        opportunities = []
        for model, listings in by_model.items():
            if len(listings) < 2:
                continue

            # Sort by price
            sorted_listings = sorted(listings, key=lambda x: x.price_per_hour)
            cheapest = sorted_listings[0]
            most_expensive = sorted_listings[-1]

            # Calculate spread
            spread_amount = most_expensive.price_per_hour - cheapest.price_per_hour
            spread_pct = (spread_amount / most_expensive.price_per_hour) * 100

            if spread_pct >= min_spread:
                opportunity = ArbitrageOpportunity(
                    gpu_type=model,
                    cheapest_provider=cheapest.provider,
                    cheapest_price=cheapest.price_per_hour,
                    expensive_provider=most_expensive.provider,
                    expensive_price=most_expensive.price_per_hour,
                    spread_pct=Decimal(str(spread_pct)),
                    savings_per_hour=spread_amount,
                    timestamp=datetime.utcnow()
                )
                opportunities.append(opportunity)

                # Save to database cache
                await self._save_to_db(opportunity)

        # Sort by spread percentage (best opportunities first)
        opportunities.sort(key=lambda x: x.spread_pct, reverse=True)
        return opportunities

    async def _save_to_db(self, opportunity: ArbitrageOpportunity):
        """Save opportunity to database cache"""
        cache_entry = ArbitrageCache(
            gpu_type=opportunity.gpu_type,
            cheapest_provider=opportunity.cheapest_provider,
            cheapest_price=opportunity.cheapest_price,
            expensive_provider=opportunity.expensive_provider,
            expensive_price=opportunity.expensive_price,
            spread_pct=opportunity.spread_pct
        )
        self.db.add(cache_entry)
        await self.db.commit()

    async def _get_cached_opportunities(
        self,
        gpu_model: Optional[str] = None
    ) -> Optional[List[ArbitrageOpportunity]]:
        """Get opportunities from Redis cache"""
        if not self.redis:
            return None

        cache_key = f"arbitrage:opportunities:{gpu_model or 'all'}"

        try:
            cached_data = await self.redis.get(cache_key)
            if cached_data:
                # Parse cached JSON and convert to ArbitrageOpportunity objects
                import json
                data = json.loads(cached_data)
                return [ArbitrageOpportunity(**item) for item in data]
        except Exception as e:
            logger.error(f"Cache retrieval error: {e}")

        return None

    async def _cache_opportunities(
        self,
        opportunities: List[ArbitrageOpportunity],
        gpu_model: Optional[str] = None
    ):
        """Cache opportunities in Redis"""
        if not self.redis:
            return

        cache_key = f"arbitrage:opportunities:{gpu_model or 'all'}"

        try:
            import json
            # Convert to JSON-serializable format
            data = [opp.model_dump(mode='json') for opp in opportunities]
            await self.redis.setex(
                cache_key,
                self.cache_ttl,
                json.dumps(data)
            )
            logger.info(f"Cached {len(opportunities)} opportunities for {self.cache_ttl}s")
        except Exception as e:
            logger.error(f"Cache storage error: {e}")

    async def get_best_deal(
        self,
        gpu_model: str,
        min_vram: Optional[int] = None
    ) -> Optional[GPU]:
        """
        Find the best deal for a specific GPU model

        Args:
            gpu_model: GPU model to search for
            min_vram: Minimum VRAM requirement (optional)

        Returns:
            GPU with lowest price, or None if not found
        """
        query = select(GPU).where(
            and_(
                GPU.model == gpu_model,
                GPU.available == True,
                GPU.last_synced > datetime.utcnow() - timedelta(hours=1)
            )
        )

        if min_vram:
            query = query.where(GPU.vram_gb >= min_vram)

        query = query.order_by(GPU.price_per_hour.asc()).limit(1)

        result = await self.db.execute(query)
        best_gpu = result.scalar_one_or_none()

        if best_gpu:
            logger.info(f"Best deal for {gpu_model}: {best_gpu.provider} at ${best_gpu.price_per_hour}/hr")

        return best_gpu

    async def get_provider_comparison(
        self,
        gpu_model: str
    ) -> Dict[str, Dict]:
        """
        Get price comparison across all providers for a GPU model

        Returns:
            Dict with provider statistics
        """
        query = select(GPU).where(
            and_(
                GPU.model == gpu_model,
                GPU.available == True,
                GPU.last_synced > datetime.utcnow() - timedelta(hours=1)
            )
        )

        result = await self.db.execute(query)
        gpus = result.scalars().all()

        # Group by provider
        by_provider = defaultdict(list)
        for gpu in gpus:
            by_provider[gpu.provider].append(gpu)

        # Calculate stats
        comparison = {}
        for provider, provider_gpus in by_provider.items():
            prices = [gpu.price_per_hour for gpu in provider_gpus]
            comparison[provider] = {
                'count': len(provider_gpus),
                'avg_price': sum(prices) / len(prices) if prices else 0,
                'min_price': min(prices) if prices else 0,
                'max_price': max(prices) if prices else 0,
                'avg_uptime': sum(gpu.uptime_percent for gpu in provider_gpus if gpu.uptime_percent) / len(provider_gpus)
            }

        return comparison

    async def calculate_monthly_savings(
        self,
        gpu_model: str,
        hours_per_day: int = 24
    ) -> Dict:
        """
        Calculate potential monthly savings by using cheapest provider

        Args:
            gpu_model: GPU model
            hours_per_day: Expected usage hours per day

        Returns:
            Dict with savings analysis
        """
        opportunities = await self.find_opportunities(gpu_model=gpu_model)

        if not opportunities:
            return {
                'gpu_model': gpu_model,
                'savings_possible': False,
                'message': 'No arbitrage opportunities found'
            }

        best_opp = opportunities[0]  # Best opportunity

        hourly_savings = best_opp.savings_per_hour
        daily_savings = hourly_savings * hours_per_day
        monthly_savings = daily_savings * 30

        return {
            'gpu_model': gpu_model,
            'savings_possible': True,
            'cheapest_provider': best_opp.cheapest_provider,
            'cheapest_price': float(best_opp.cheapest_price),
            'expensive_provider': best_opp.expensive_provider,
            'expensive_price': float(best_opp.expensive_price),
            'hourly_savings': float(hourly_savings),
            'daily_savings': float(daily_savings),
            'monthly_savings': float(monthly_savings),
            'spread_percent': float(best_opp.spread_pct),
            'hours_per_day': hours_per_day
        }
