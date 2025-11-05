"""
Arbitrage API Routes
Price comparison and arbitrage opportunity detection
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas import ArbitrageOpportunity
from app.services.arbitrage_engine import ArbitrageEngine

router = APIRouter()


@router.get("/opportunities", response_model=List[ArbitrageOpportunity])
async def get_arbitrage_opportunities(
    min_spread: Optional[float] = Query(None, description="Minimum spread percentage", ge=0, le=100),
    gpu_model: Optional[str] = Query(None, description="Filter by GPU model"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current arbitrage opportunities

    Finds price differentials across GPU providers.
    Results are cached for 30 seconds for performance.

    Query Parameters:
        min_spread: Minimum price spread percentage (default: 15%)
        gpu_model: Filter by specific GPU model (e.g., "RTX 4090")

    Returns:
        List of arbitrage opportunities sorted by spread percentage
    """
    engine = ArbitrageEngine(db)
    opportunities = await engine.find_opportunities(
        min_spread_pct=min_spread,
        gpu_model=gpu_model
    )

    return opportunities


@router.get("/best-deal/{gpu_model}")
async def get_best_deal(
    gpu_model: str,
    min_vram: Optional[int] = Query(None, description="Minimum VRAM in GB"),
    db: AsyncSession = Depends(get_db)
):
    """
    Find the best deal for a specific GPU model

    Args:
        gpu_model: GPU model to search for (e.g., "RTX 4090")
        min_vram: Minimum VRAM requirement in GB (optional)

    Returns:
        GPU with the lowest price, or 404 if not found
    """
    engine = ArbitrageEngine(db)
    best_gpu = await engine.get_best_deal(gpu_model, min_vram)

    if not best_gpu:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No available GPUs found for {gpu_model}"
        )

    return {
        "id": str(best_gpu.id),
        "provider": best_gpu.provider,
        "model": best_gpu.model,
        "vram_gb": best_gpu.vram_gb,
        "price_per_hour": float(best_gpu.price_per_hour),
        "location": best_gpu.location,
        "uptime_percent": float(best_gpu.uptime_percent) if best_gpu.uptime_percent else None,
        "g_score": float(best_gpu.g_score) if best_gpu.g_score else None
    }


@router.get("/compare/{gpu_model}")
async def compare_providers(
    gpu_model: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Compare prices across all providers for a GPU model

    Args:
        gpu_model: GPU model to compare (e.g., "RTX 4090")

    Returns:
        Provider statistics with pricing information
    """
    engine = ArbitrageEngine(db)
    comparison = await engine.get_provider_comparison(gpu_model)

    if not comparison:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No data available for {gpu_model}"
        )

    return {
        "gpu_model": gpu_model,
        "providers": comparison
    }


@router.get("/savings/{gpu_model}")
async def calculate_savings(
    gpu_model: str,
    hours_per_day: int = Query(24, description="Expected usage hours per day", ge=1, le=24),
    db: AsyncSession = Depends(get_db)
):
    """
    Calculate potential monthly savings by using cheapest provider

    Args:
        gpu_model: GPU model (e.g., "RTX 4090")
        hours_per_day: Expected usage hours per day (1-24)

    Returns:
        Detailed savings analysis
    """
    engine = ArbitrageEngine(db)
    savings = await engine.calculate_monthly_savings(gpu_model, hours_per_day)

    return savings
