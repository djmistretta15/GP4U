"""
Provider Aggregator Service
Manages data synchronization from all GPU providers with advanced reliability patterns
"""
import asyncio
import logging
from typing import List, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..providers import VastAIProvider, IONetProvider, AkashProvider, RenderProvider
from ..models import GPU
from ..core.base_provider import get_provider_registry, ProviderStatus
from ..core.adaptive_cache import get_adaptive_cache
from ..core.circuit_breaker import CircuitBreakerOpen
from ..core.rate_limiter import RateLimitExceeded

logger = logging.getLogger(__name__)


class ProviderAggregator:
    """
    Aggregates GPU data from all providers with enterprise reliability

    Features:
    - Automatic retry with exponential backoff
    - Circuit breaker pattern
    - Rate limiting
    - Adaptive caching
    - Comprehensive metrics
    - Parallel fetching with error isolation
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.registry = get_provider_registry()

        # Initialize all providers if not already registered
        if not self.registry.get_all():
            self._initialize_providers()

    def _initialize_providers(self):
        """Initialize and register all provider instances"""
        providers = [
            VastAIProvider(),
            IONetProvider(),
            AkashProvider(),
            RenderProvider(),
        ]

        for provider in providers:
            self.registry.register(provider)
            logger.info(f"Registered provider: {provider.name}")

    async def sync_all_providers(self) -> Dict[str, Any]:
        """
        Sync GPU data from all providers to database

        Uses BaseProvider architecture with:
        - Automatic retry
        - Circuit breaker protection
        - Rate limiting
        - Adaptive caching

        Returns:
            Dictionary with sync statistics
        """
        logger.info("Starting provider sync with enterprise reliability patterns...")
        start_time = datetime.utcnow()

        total_gpus = 0
        total_new = 0
        total_updated = 0
        total_errors = 0
        provider_stats = {}

        providers = self.registry.get_all()

        # Fetch from all providers in parallel (with error isolation)
        tasks = []
        for provider in providers:
            tasks.append(self._fetch_provider_gpus(provider))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        for provider, result in zip(providers, results):
            if isinstance(result, Exception):
                total_errors += 1
                error_type = type(result).__name__
                logger.error(f"{provider.name}: Fetch failed - {error_type}: {result}")

                provider_stats[provider.name] = {
                    'success': False,
                    'error': str(result),
                    'error_type': error_type,
                    'status': provider.get_status().value,
                }
                continue

            # result is the list of normalized GPUs
            gpus = result

            # Save GPUs to database
            try:
                stats = await self._save_gpus(gpus)
                total_gpus += stats['total']
                total_new += stats['new']
                total_updated += stats['updated']

                provider_stats[provider.name] = {
                    'success': True,
                    'gpus_fetched': stats['total'],
                    'new': stats['new'],
                    'updated': stats['updated'],
                    'status': provider.get_status().value,
                    'metrics': provider.get_metrics(),
                }

                logger.info(f"{provider.name}: Synced {stats['total']} GPUs ({stats['new']} new, {stats['updated']} updated)")

            except Exception as e:
                total_errors += 1
                logger.error(f"{provider.name}: Database save failed: {e}")
                provider_stats[provider.name] = {
                    'success': False,
                    'error': f"Database error: {str(e)}",
                    'error_type': 'DatabaseError',
                }

        duration = (datetime.utcnow() - start_time).total_seconds()

        # Calculate success rate
        success_count = sum(1 for p in provider_stats.values() if p.get('success'))
        success_rate = (success_count / len(providers) * 100) if providers else 0

        summary = {
            'success': total_errors == 0,
            'duration_seconds': round(duration, 2),
            'total_gpus': total_gpus,
            'total_new': total_new,
            'total_updated': total_updated,
            'total_providers': len(providers),
            'successful_providers': success_count,
            'failed_providers': total_errors,
            'success_rate': round(success_rate, 2),
            'providers': provider_stats,
            'timestamp': datetime.utcnow().isoformat(),
        }

        logger.info(
            f"Provider sync complete: {total_gpus} GPUs "
            f"({total_new} new, {total_updated} updated) "
            f"from {success_count}/{len(providers)} providers in {duration:.2f}s"
        )

        return summary

    async def _fetch_provider_gpus(self, provider) -> List[Dict[str, Any]]:
        """
        Fetch GPUs from a single provider using BaseProvider architecture

        Handles:
        - Circuit breaker (raises CircuitBreakerOpen)
        - Rate limiting (raises RateLimitExceeded)
        - Automatic retry
        - Caching

        Args:
            provider: BaseProvider instance

        Returns:
            List of normalized GPU dictionaries

        Raises:
            Various exceptions from provider fetch
        """
        try:
            # BaseProvider.get_gpus() handles retry, circuit breaker, rate limiting
            gpus = await provider.get_gpus()
            return gpus

        except CircuitBreakerOpen as e:
            logger.warning(f"{provider.name}: Circuit breaker open, skipping")
            raise

        except RateLimitExceeded as e:
            logger.warning(f"{provider.name}: Rate limit exceeded, skipping")
            raise

        except Exception as e:
            logger.error(f"{provider.name}: Unexpected error: {e}")
            raise

    async def _save_gpus(self, gpu_data: List[dict]) -> dict:
        """
        Save GPU data to database

        Args:
            gpu_data: List of GPU dictionaries from provider

        Returns:
            Statistics about saved GPUs
        """
        stats = {'total': 0, 'new': 0, 'updated': 0}

        for gpu_dict in gpu_data:
            stats['total'] += 1

            # Check if GPU already exists
            result = await self.db.execute(
                select(GPU).where(
                    GPU.external_id == gpu_dict['external_id']
                )
            )
            existing_gpu = result.scalar_one_or_none()

            if existing_gpu:
                # Update existing GPU
                for key, value in gpu_dict.items():
                    if key != 'provider':  # Don't change provider
                        setattr(existing_gpu, key, value)
                existing_gpu.last_synced = datetime.utcnow()
                stats['updated'] += 1
            else:
                # Create new GPU
                new_gpu = GPU(**gpu_dict, last_synced=datetime.utcnow())
                self.db.add(new_gpu)
                stats['new'] += 1

        await self.db.commit()
        return stats

    async def sync_single_provider(self, provider_name: str) -> Dict[str, Any]:
        """
        Sync data from a single provider

        Args:
            provider_name: Name of provider (vastai, ionet, akash, render)

        Returns:
            Sync statistics for that provider
        """
        provider = self.registry.get(provider_name)

        if not provider:
            return {
                'success': False,
                'error': f'Provider {provider_name} not found',
                'available_providers': [p.name for p in self.registry.get_all()]
            }

        start_time = datetime.utcnow()

        try:
            # Fetch GPUs using BaseProvider (includes retry, circuit breaker, rate limiting)
            gpus = await self._fetch_provider_gpus(provider)

            # Save to database
            stats = await self._save_gpus(gpus)

            duration = (datetime.utcnow() - start_time).total_seconds()

            return {
                'success': True,
                'provider': provider_name,
                'gpus_fetched': stats['total'],
                'new': stats['new'],
                'updated': stats['updated'],
                'duration_seconds': round(duration, 2),
                'status': provider.get_status().value,
                'metrics': provider.get_metrics(),
                'timestamp': datetime.utcnow().isoformat(),
            }

        except CircuitBreakerOpen as e:
            return {
                'success': False,
                'provider': provider_name,
                'error': str(e),
                'error_type': 'CircuitBreakerOpen',
                'status': provider.get_status().value,
            }

        except RateLimitExceeded as e:
            return {
                'success': False,
                'provider': provider_name,
                'error': str(e),
                'error_type': 'RateLimitExceeded',
                'status': provider.get_status().value,
            }

        except Exception as e:
            logger.error(f"Error syncing {provider_name}: {e}")
            return {
                'success': False,
                'provider': provider_name,
                'error': str(e),
                'error_type': type(e).__name__,
                'status': provider.get_status().value,
            }

    async def get_provider_status(self) -> Dict[str, Any]:
        """
        Check health status of all providers

        Returns:
            Status dictionary for each provider with health metrics
        """
        providers = self.registry.get_all()
        status = {}

        for provider in providers:
            provider_status = provider.get_status()
            metrics = provider.get_metrics()

            status[provider.name] = {
                'status': provider_status.value,
                'healthy': provider_status == ProviderStatus.HEALTHY,
                'metrics': {
                    'success_rate': metrics.get('success_rate', 0),
                    'total_requests': metrics.get('total_requests', 0),
                    'avg_response_time': metrics.get('avg_response_time', 0),
                    'circuit_breaker_state': metrics.get('circuit_breaker_state', 'unknown'),
                },
                'last_request': metrics.get('last_request_time', 'never'),
            }

        # Calculate summary
        healthy_count = sum(1 for s in status.values() if s['healthy'])
        total_count = len(status)

        return {
            'providers': status,
            'summary': {
                'total': total_count,
                'healthy': healthy_count,
                'degraded': sum(1 for s in status.values() if s['status'] == 'degraded'),
                'unavailable': sum(1 for s in status.values() if s['status'] == 'unavailable'),
                'overall_health': 'healthy' if healthy_count == total_count else 'degraded',
            },
            'timestamp': datetime.utcnow().isoformat(),
        }

    async def close_all(self):
        """Close all provider connections"""
        await self.registry.close_all()
        logger.info("All provider connections closed")
