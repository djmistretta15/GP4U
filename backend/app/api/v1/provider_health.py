"""
Provider Health Monitoring API
Real-time provider status, metrics, and diagnostics
"""

from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from ...core.base_provider import get_provider_registry, ProviderStatus
from ...core.circuit_breaker import get_circuit_breaker_registry
from ...core.rate_limiter import get_rate_limiter_registry
from ...core.adaptive_cache import get_adaptive_cache


router = APIRouter()


class ProviderHealthResponse(BaseModel):
    """Provider health status response"""
    provider: str
    status: str
    metrics: Dict[str, Any]
    circuit_breaker_state: str
    rate_limiter_available: float
    last_updated: str


class SystemHealthResponse(BaseModel):
    """Overall system health response"""
    healthy_providers: int
    total_providers: int
    degraded_providers: int
    unavailable_providers: int
    overall_status: str
    providers: List[ProviderHealthResponse]


class CircuitBreakerStatsResponse(BaseModel):
    """Circuit breaker statistics"""
    provider: str
    state: str
    failure_count: int
    success_count: int
    last_failure_time: str = None
    last_success_time: str = None


class CacheStatsResponse(BaseModel):
    """Cache statistics"""
    total_requests: int
    hits: int
    misses: int
    hit_rate: float
    connected: bool


@router.get("/health", response_model=SystemHealthResponse)
async def get_system_health():
    """
    Get overall system health status

    Returns:
        System-wide health metrics including all providers
    """
    registry = get_provider_registry()
    providers = registry.get_all()

    if not providers:
        raise HTTPException(
            status_code=503,
            detail="No providers registered"
        )

    provider_health = []
    healthy_count = 0
    degraded_count = 0
    unavailable_count = 0

    for provider in providers:
        status = provider.get_status()
        metrics = provider.get_metrics()

        # Count by status
        if status == ProviderStatus.HEALTHY:
            healthy_count += 1
        elif status == ProviderStatus.DEGRADED:
            degraded_count += 1
        else:
            unavailable_count += 1

        provider_health.append(
            ProviderHealthResponse(
                provider=provider.name,
                status=status.value,
                metrics=metrics,
                circuit_breaker_state=metrics.get("circuit_breaker_state", "unknown"),
                rate_limiter_available=metrics.get("rate_limiter_tokens", 0),
                last_updated=metrics.get("last_request_time", "never"),
            )
        )

    # Determine overall status
    if unavailable_count == len(providers):
        overall_status = "critical"
    elif unavailable_count > 0 or degraded_count > 0:
        overall_status = "degraded"
    else:
        overall_status = "healthy"

    return SystemHealthResponse(
        healthy_providers=healthy_count,
        total_providers=len(providers),
        degraded_providers=degraded_count,
        unavailable_providers=unavailable_count,
        overall_status=overall_status,
        providers=provider_health,
    )


@router.get("/providers/{provider_name}/health", response_model=ProviderHealthResponse)
async def get_provider_health(provider_name: str):
    """
    Get health status for a specific provider

    Args:
        provider_name: Provider name (vastai, ionet, akash, render)

    Returns:
        Detailed health metrics for the provider
    """
    registry = get_provider_registry()
    provider = registry.get(provider_name)

    if not provider:
        raise HTTPException(
            status_code=404,
            detail=f"Provider '{provider_name}' not found"
        )

    status = provider.get_status()
    metrics = provider.get_metrics()

    return ProviderHealthResponse(
        provider=provider.name,
        status=status.value,
        metrics=metrics,
        circuit_breaker_state=metrics.get("circuit_breaker_state", "unknown"),
        rate_limiter_available=metrics.get("rate_limiter_tokens", 0),
        last_updated=metrics.get("last_request_time", "never"),
    )


@router.post("/providers/{provider_name}/health-check")
async def run_health_check(provider_name: str):
    """
    Manually trigger a health check for a provider

    Args:
        provider_name: Provider name

    Returns:
        Health check result
    """
    registry = get_provider_registry()
    provider = registry.get(provider_name)

    if not provider:
        raise HTTPException(
            status_code=404,
            detail=f"Provider '{provider_name}' not found"
        )

    try:
        is_healthy = await provider.health_check()

        return {
            "provider": provider_name,
            "healthy": is_healthy,
            "status": provider.get_status().value,
            "message": "Health check completed successfully" if is_healthy else "Health check failed",
        }
    except Exception as e:
        return {
            "provider": provider_name,
            "healthy": False,
            "status": "unavailable",
            "message": f"Health check error: {str(e)}",
        }


@router.get("/circuit-breakers")
async def get_circuit_breaker_stats():
    """
    Get circuit breaker statistics for all providers

    Returns:
        Circuit breaker stats for each provider
    """
    cb_registry = get_circuit_breaker_registry()
    all_stats = cb_registry.get_all_stats()

    results = []
    for provider_name, (state, stats) in all_stats.items():
        results.append({
            "provider": provider_name,
            "state": state.value,
            "failure_count": stats.failure_count,
            "success_count": stats.success_count,
            "last_failure_time": stats.last_failure_time,
            "last_success_time": stats.last_success_time,
            "state_changes": len(stats.state_changes),
        })

    unhealthy = cb_registry.get_unhealthy_providers()

    return {
        "circuit_breakers": results,
        "unhealthy_providers": unhealthy,
        "healthy_count": cb_registry.get_healthy_count(),
        "total_count": len(all_stats),
    }


@router.post("/circuit-breakers/{provider_name}/reset")
async def reset_circuit_breaker(provider_name: str):
    """
    Manually reset a circuit breaker

    Args:
        provider_name: Provider name

    Returns:
        Reset confirmation
    """
    cb_registry = get_circuit_breaker_registry()
    breaker = cb_registry.get(provider_name)

    if not breaker:
        raise HTTPException(
            status_code=404,
            detail=f"Circuit breaker for '{provider_name}' not found"
        )

    breaker.reset()

    return {
        "provider": provider_name,
        "status": "reset",
        "new_state": breaker.get_state().value,
        "message": "Circuit breaker manually reset",
    }


@router.get("/rate-limiters")
async def get_rate_limiter_stats():
    """
    Get rate limiter statistics for all providers

    Returns:
        Rate limiter stats for each provider
    """
    rl_registry = get_rate_limiter_registry()
    all_stats = rl_registry.get_all_stats()

    return {
        "rate_limiters": all_stats,
        "total_count": len(all_stats),
    }


@router.post("/rate-limiters/reset-all")
async def reset_all_rate_limiters():
    """
    Reset all rate limiters

    Returns:
        Reset confirmation
    """
    rl_registry = get_rate_limiter_registry()
    rl_registry.reset_all()

    return {
        "status": "success",
        "message": "All rate limiters reset",
    }


@router.get("/cache/stats", response_model=CacheStatsResponse)
async def get_cache_stats():
    """
    Get cache statistics

    Returns:
        Cache performance metrics
    """
    cache = await get_adaptive_cache()
    stats = cache.get_stats()

    return CacheStatsResponse(**stats)


@router.post("/cache/invalidate/{provider_name}")
async def invalidate_provider_cache(
    provider_name: str,
    query: str = Query(None, description="Specific query to invalidate (None = all)")
):
    """
    Invalidate cache for a provider

    Args:
        provider_name: Provider name
        query: Optional specific query to invalidate

    Returns:
        Invalidation confirmation
    """
    cache = await get_adaptive_cache()
    await cache.invalidate(provider_name, query)

    return {
        "provider": provider_name,
        "query": query or "all",
        "status": "invalidated",
        "message": f"Cache invalidated for {provider_name}",
    }


@router.get("/metrics/summary")
async def get_metrics_summary():
    """
    Get comprehensive metrics summary

    Returns:
        Aggregated metrics across all systems
    """
    # Provider metrics
    registry = get_provider_registry()
    provider_metrics = registry.get_all_metrics()

    # Circuit breaker stats
    cb_registry = get_circuit_breaker_registry()
    cb_stats = cb_registry.get_all_stats()

    # Rate limiter stats
    rl_registry = get_rate_limiter_registry()
    rl_stats = rl_registry.get_all_stats()

    # Cache stats
    cache = await get_adaptive_cache()
    cache_stats = cache.get_stats()

    # Calculate aggregates
    total_requests = sum(m.get("total_requests", 0) for m in provider_metrics.values())
    total_successful = sum(m.get("successful_requests", 0) for m in provider_metrics.values())
    total_failed = sum(m.get("failed_requests", 0) for m in provider_metrics.values())

    avg_success_rate = (
        sum(m.get("success_rate", 0) for m in provider_metrics.values()) / len(provider_metrics)
        if provider_metrics else 0
    )

    return {
        "overview": {
            "total_requests": total_requests,
            "successful_requests": total_successful,
            "failed_requests": total_failed,
            "average_success_rate": round(avg_success_rate, 2),
            "providers_count": len(provider_metrics),
        },
        "providers": provider_metrics,
        "circuit_breakers": {
            "healthy_count": cb_registry.get_healthy_count(),
            "unhealthy_providers": cb_registry.get_unhealthy_providers(),
        },
        "rate_limiters": rl_stats,
        "cache": cache_stats,
    }
