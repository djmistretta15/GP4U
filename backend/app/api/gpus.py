"""
GPU API Routes
GPU search, filtering, and comparison
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models import GPU
from app.schemas import GPU as GPUSchema, GPUSearch, GPUCompare

router = APIRouter()


@router.get("/search", response_model=List[GPUSchema])
async def search_gpus(
    model: Optional[str] = Query(None, description="GPU model filter"),
    min_vram: Optional[int] = Query(None, description="Minimum VRAM in GB"),
    max_price: Optional[float] = Query(None, description="Maximum price per hour"),
    provider: Optional[str] = Query(None, description="Provider filter"),
    location: Optional[str] = Query(None, description="Location filter"),
    available_only: bool = Query(True, description="Show only available GPUs"),
    limit: int = Query(100, description="Maximum results", le=500),
    db: AsyncSession = Depends(get_db)
):
    """
    Search for GPUs with filters

    Query Parameters:
        model: Filter by GPU model (partial match)
        min_vram: Minimum VRAM in GB
        max_price: Maximum price per hour
        provider: Filter by provider name
        location: Filter by location
        available_only: Show only available GPUs (default: true)
        limit: Maximum number of results (max: 500)

    Returns:
        List of GPUs matching criteria, sorted by price
    """
    # Build query
    query = select(GPU).where(
        GPU.last_synced > datetime.utcnow() - timedelta(hours=1)
    )

    # Apply filters
    if model:
        query = query.where(GPU.model.ilike(f"%{model}%"))

    if min_vram is not None:
        query = query.where(GPU.vram_gb >= min_vram)

    if max_price is not None:
        query = query.where(GPU.price_per_hour <= max_price)

    if provider:
        query = query.where(GPU.provider.ilike(f"%{provider}%"))

    if location:
        query = query.where(GPU.location.ilike(f"%{location}%"))

    if available_only:
        query = query.where(GPU.available == True)

    # Sort by price and limit results
    query = query.order_by(GPU.price_per_hour.asc()).limit(limit)

    # Execute query
    result = await db.execute(query)
    gpus = result.scalars().all()

    return gpus


@router.get("/{gpu_id}", response_model=GPUSchema)
async def get_gpu(
    gpu_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get GPU details by ID

    Args:
        gpu_id: GPU UUID

    Returns:
        GPU details
    """
    result = await db.execute(
        select(GPU).where(GPU.id == gpu_id)
    )
    gpu = result.scalar_one_or_none()

    if not gpu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="GPU not found"
        )

    return gpu


@router.post("/compare")
async def compare_gpus(
    compare_data: GPUCompare,
    db: AsyncSession = Depends(get_db)
):
    """
    Compare multiple GPUs side-by-side

    Args:
        compare_data: List of 2-3 GPU IDs to compare

    Returns:
        Comparison table with all GPU details
    """
    if len(compare_data.gpu_ids) < 2 or len(compare_data.gpu_ids) > 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only compare 2-3 GPUs at once"
        )

    # Fetch all GPUs
    result = await db.execute(
        select(GPU).where(GPU.id.in_(compare_data.gpu_ids))
    )
    gpus = result.scalars().all()

    if len(gpus) != len(compare_data.gpu_ids):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or more GPUs not found"
        )

    # Build comparison
    comparison = {
        "gpus": [
            {
                "id": str(gpu.id),
                "provider": gpu.provider,
                "model": gpu.model,
                "vram_gb": gpu.vram_gb,
                "price_per_hour": float(gpu.price_per_hour),
                "location": gpu.location,
                "uptime_percent": float(gpu.uptime_percent) if gpu.uptime_percent else None,
                "g_score": float(gpu.g_score) if gpu.g_score else None,
                "available": gpu.available
            }
            for gpu in gpus
        ],
        "best_price": min(float(gpu.price_per_hour) for gpu in gpus),
        "price_range": max(float(gpu.price_per_hour) for gpu in gpus) - min(float(gpu.price_per_hour) for gpu in gpus),
        "avg_price": sum(float(gpu.price_per_hour) for gpu in gpus) / len(gpus)
    }

    return comparison


@router.get("/models/available", response_model=List[str])
async def get_available_models(
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of all available GPU models

    Returns:
        Unique list of GPU models currently available
    """
    result = await db.execute(
        select(GPU.model)
        .where(
            and_(
                GPU.available == True,
                GPU.last_synced > datetime.utcnow() - timedelta(hours=1)
            )
        )
        .distinct()
    )

    models = result.scalars().all()
    return sorted(models)


@router.get("/providers/list", response_model=List[str])
async def get_providers(
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of all GPU providers

    Returns:
        Unique list of providers
    """
    result = await db.execute(
        select(GPU.provider)
        .where(GPU.last_synced > datetime.utcnow() - timedelta(hours=1))
        .distinct()
    )

    providers = result.scalars().all()
    return sorted(providers)
