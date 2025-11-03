"""
Celery Worker Configuration
Background tasks for GP4U platform
"""
from celery import Celery
from celery.schedules import crontab
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.services.provider_aggregator import ProviderAggregator

# Create Celery app
celery_app = Celery(
    'gp4u_worker',
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes max
    worker_prefetch_multiplier=1,
)


def run_async(coro):
    """Helper to run async functions in Celery tasks"""
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coro)


@celery_app.task(name='sync_all_providers')
def sync_all_providers():
    """
    Sync GPU data from all providers

    This task runs every 30 seconds to keep GPU data fresh
    """
    async def _sync():
        async with AsyncSessionLocal() as db:
            aggregator = ProviderAggregator(db)
            result = await aggregator.sync_all_providers()
            return result

    return run_async(_sync())


@celery_app.task(name='sync_single_provider')
def sync_single_provider(provider_name: str):
    """
    Sync data from a single provider

    Args:
        provider_name: Provider to sync (Render, Akash, io.net, Vast.ai)
    """
    async def _sync():
        async with AsyncSessionLocal() as db:
            aggregator = ProviderAggregator(db)
            result = await aggregator.sync_single_provider(provider_name)
            return result

    return run_async(_sync())


@celery_app.task(name='cleanup_old_data')
def cleanup_old_data():
    """
    Clean up old GPU listings and arbitrage cache

    Removes data older than 24 hours
    """
    async def _cleanup():
        from datetime import datetime, timedelta
        from sqlalchemy import delete

        async with AsyncSessionLocal() as db:
            from app.models import GPU, ArbitrageCache

            cutoff = datetime.utcnow() - timedelta(hours=24)

            # Delete old arbitrage cache
            await db.execute(
                delete(ArbitrageCache).where(ArbitrageCache.timestamp < cutoff)
            )

            # Mark old GPUs as unavailable
            result = await db.execute(
                select(GPU).where(GPU.last_synced < cutoff)
            )
            old_gpus = result.scalars().all()

            for gpu in old_gpus:
                gpu.available = False

            await db.commit()

            return {
                'old_gpus_marked_unavailable': len(old_gpus),
                'timestamp': datetime.utcnow().isoformat()
            }

    return run_async(_cleanup())


@celery_app.task(name='update_reservation_statuses')
def update_reservation_statuses():
    """
    Update reservation statuses based on time

    Activates pending reservations that have started
    Completes active reservations that have ended
    """
    async def _update():
        async with AsyncSessionLocal() as db:
            from app.services.reservation_service import ReservationService

            service = ReservationService(db)

            activated = await service.activate_pending_reservations()
            completed = await service.complete_finished_reservations()

            return {
                'activated': activated,
                'completed': completed,
                'timestamp': datetime.utcnow().isoformat()
            }

    return run_async(_update())


# Celery Beat Schedule (Periodic Tasks)
celery_app.conf.beat_schedule = {
    'sync-providers-every-30-seconds': {
        'task': 'sync_all_providers',
        'schedule': 30.0,  # Every 30 seconds
    },
    'update-reservations-every-minute': {
        'task': 'update_reservation_statuses',
        'schedule': 60.0,  # Every minute
    },
    'cleanup-old-data-daily': {
        'task': 'cleanup_old_data',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
    },
}


if __name__ == '__main__':
    celery_app.start()
