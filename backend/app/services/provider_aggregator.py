"""
Provider Aggregator Service
Manages data synchronization from all GPU providers
"""
import asyncio
import logging
from typing import List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.providers import RenderProvider, AkashProvider, IoNetProvider, VastAIProvider
from app.models import GPU
from app.core.config import settings

logger = logging.getLogger(__name__)


class ProviderAggregator:
    """
    Aggregates GPU data from all providers
    Handles periodic synchronization to database
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.providers = [
            RenderProvider(api_key=settings.RENDER_API_KEY),
            AkashProvider(api_key=settings.AKASH_API_KEY),
            IoNetProvider(api_key=settings.IONET_API_KEY),
            VastAIProvider(api_key=settings.VASTAI_API_KEY),
        ]

    async def sync_all_providers(self) -> dict:
        """
        Sync GPU data from all providers to database

        Returns:
            Dictionary with sync statistics
        """
        logger.info("Starting provider sync...")
        start_time = datetime.utcnow()

        total_gpus = 0
        total_new = 0
        total_updated = 0
        provider_stats = {}

        # Fetch from all providers in parallel
        tasks = [provider.fetch_gpus() for provider in self.providers]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        for provider, result in zip(self.providers, results):
            if isinstance(result, Exception):
                logger.error(f"Error fetching from {provider.provider_name}: {result}")
                provider_stats[provider.provider_name] = {
                    'success': False,
                    'error': str(result)
                }
                continue

            # Save GPUs to database
            stats = await self._save_gpus(result)
            total_gpus += stats['total']
            total_new += stats['new']
            total_updated += stats['updated']

            provider_stats[provider.provider_name] = {
                'success': True,
                'gpus_fetched': stats['total'],
                'new': stats['new'],
                'updated': stats['updated']
            }

        duration = (datetime.utcnow() - start_time).total_seconds()

        summary = {
            'success': True,
            'duration_seconds': duration,
            'total_gpus': total_gpus,
            'total_new': total_new,
            'total_updated': total_updated,
            'providers': provider_stats,
            'timestamp': datetime.utcnow().isoformat()
        }

        logger.info(
            f"Provider sync complete: {total_gpus} GPUs "
            f"({total_new} new, {total_updated} updated) in {duration:.2f}s"
        )

        return summary

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

    async def sync_single_provider(self, provider_name: str) -> dict:
        """
        Sync data from a single provider

        Args:
            provider_name: Name of provider (Render, Akash, io.net, Vast.ai)

        Returns:
            Sync statistics for that provider
        """
        provider = next(
            (p for p in self.providers if p.provider_name == provider_name),
            None
        )

        if not provider:
            return {
                'success': False,
                'error': f'Provider {provider_name} not found'
            }

        try:
            gpus = await provider.fetch_gpus()
            stats = await self._save_gpus(gpus)

            return {
                'success': True,
                'provider': provider_name,
                'gpus_fetched': stats['total'],
                'new': stats['new'],
                'updated': stats['updated']
            }
        except Exception as e:
            logger.error(f"Error syncing {provider_name}: {e}")
            return {
                'success': False,
                'provider': provider_name,
                'error': str(e)
            }

    async def get_provider_status(self) -> dict:
        """
        Check connection status of all providers

        Returns:
            Status dictionary for each provider
        """
        status = {}

        tasks = [provider.validate_connection() for provider in self.providers]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for provider, result in zip(self.providers, results):
            status[provider.provider_name] = {
                'connected': result if isinstance(result, bool) else False,
                'error': str(result) if isinstance(result, Exception) else None
            }

        return status
