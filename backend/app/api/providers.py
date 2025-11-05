"""
Provider Management API Routes
Manual sync triggers and status checks
"""
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.provider_aggregator import ProviderAggregator
from app.core.dependencies import get_current_active_user
from app.models import User

router = APIRouter()


@router.post("/sync")
async def trigger_sync(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Manually trigger provider synchronization

    Requires authentication.
    Runs sync in background.

    Returns:
        Confirmation message
    """
    async def sync_task():
        aggregator = ProviderAggregator(db)
        await aggregator.sync_all_providers()

    background_tasks.add_task(sync_task)

    return {
        "message": "Provider sync triggered",
        "status": "running_in_background"
    }


@router.post("/sync/{provider_name}")
async def trigger_single_provider_sync(
    provider_name: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Manually sync a single provider

    Args:
        provider_name: Provider to sync (Render, Akash, io.net, Vast.ai)

    Returns:
        Confirmation message
    """
    valid_providers = ['Render', 'Akash', 'io.net', 'Vast.ai']

    if provider_name not in valid_providers:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid provider. Must be one of: {', '.join(valid_providers)}"
        )

    async def sync_task():
        aggregator = ProviderAggregator(db)
        await aggregator.sync_single_provider(provider_name)

    background_tasks.add_task(sync_task)

    return {
        "message": f"{provider_name} sync triggered",
        "status": "running_in_background"
    }


@router.get("/status")
async def get_provider_status(
    db: AsyncSession = Depends(get_db)
):
    """
    Check connection status of all providers

    Returns:
        Status for each provider
    """
    aggregator = ProviderAggregator(db)
    status = await aggregator.get_provider_status()

    return {
        "providers": status,
        "total_providers": len(status),
        "connected": sum(1 for p in status.values() if p['connected'])
    }
