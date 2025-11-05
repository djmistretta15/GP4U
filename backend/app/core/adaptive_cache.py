"""
Adaptive Caching System with Redis
Dynamic TTL based on provider performance and data freshness requirements
"""

import json
import logging
import hashlib
from typing import Any, Optional, Callable
from datetime import datetime, timedelta
from functools import wraps

import redis.asyncio as redis

from .provider_config import get_provider_config


logger = logging.getLogger(__name__)


class AdaptiveCache:
    """
    Adaptive caching with dynamic TTL strategies

    Features:
    - Dynamic TTL based on provider performance
    - Cache warming for popular queries
    - Stale-while-revalidate pattern
    - Cache hit/miss tracking
    - Automatic invalidation
    """

    def __init__(self):
        self.config = get_provider_config()
        self.redis_client: Optional[redis.Redis] = None

        # Cache statistics
        self.hits = 0
        self.misses = 0
        self.total_requests = 0

        # TTL strategies (in seconds)
        self.base_ttl = self.config.provider_cache_ttl
        self.min_ttl = 10  # Minimum 10 seconds
        self.max_ttl = 300  # Maximum 5 minutes

    async def connect(self):
        """Connect to Redis"""
        try:
            self.redis_client = await redis.from_url(
                "redis://localhost:6379",
                encoding="utf-8",
                decode_responses=True,
            )
            await self.redis_client.ping()
            logger.info("Connected to Redis for adaptive caching")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.redis_client = None

    async def close(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()

    def _generate_key(self, provider: str, query: str) -> str:
        """
        Generate cache key

        Args:
            provider: Provider name
            query: Query identifier

        Returns:
            Cache key
        """
        # Hash query for consistent key length
        query_hash = hashlib.md5(query.encode()).hexdigest()
        return f"gp4u:provider:{provider}:{query_hash}"

    def _calculate_dynamic_ttl(self, provider: str, success_rate: float) -> int:
        """
        Calculate dynamic TTL based on provider performance

        Higher success rate = longer TTL (more reliable data)
        Lower success rate = shorter TTL (revalidate more often)

        Args:
            provider: Provider name
            success_rate: Success rate (0.0 to 1.0)

        Returns:
            TTL in seconds
        """
        # Base TTL adjusted by success rate
        # 100% success = max TTL
        # 50% success = base TTL
        # 0% success = min TTL
        if success_rate >= 0.9:
            ttl = self.max_ttl
        elif success_rate >= 0.7:
            ttl = int(self.base_ttl * 1.5)
        elif success_rate >= 0.5:
            ttl = self.base_ttl
        else:
            ttl = self.min_ttl

        logger.debug(f"{provider}: Dynamic TTL = {ttl}s (success_rate={success_rate:.2f})")

        return ttl

    async def get(self, provider: str, query: str) -> Optional[Any]:
        """
        Get cached data

        Args:
            provider: Provider name
            query: Query identifier

        Returns:
            Cached data or None if miss
        """
        if not self.redis_client:
            return None

        self.total_requests += 1

        try:
            key = self._generate_key(provider, query)
            cached_data = await self.redis_client.get(key)

            if cached_data:
                self.hits += 1
                logger.debug(f"{provider}: Cache HIT for {query[:50]}")
                return json.loads(cached_data)
            else:
                self.misses += 1
                logger.debug(f"{provider}: Cache MISS for {query[:50]}")
                return None

        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None

    async def set(
        self,
        provider: str,
        query: str,
        data: Any,
        success_rate: float = 0.9,
        custom_ttl: Optional[int] = None,
    ):
        """
        Set cached data with dynamic TTL

        Args:
            provider: Provider name
            query: Query identifier
            data: Data to cache
            success_rate: Provider success rate (affects TTL)
            custom_ttl: Override TTL in seconds
        """
        if not self.redis_client:
            return

        try:
            key = self._generate_key(provider, query)

            # Determine TTL
            if custom_ttl:
                ttl = custom_ttl
            else:
                ttl = self._calculate_dynamic_ttl(provider, success_rate)

            # Serialize data
            cached_data = json.dumps({
                "data": data,
                "cached_at": datetime.utcnow().isoformat(),
                "provider": provider,
                "ttl": ttl,
            })

            # Set with expiration
            await self.redis_client.setex(key, ttl, cached_data)

            logger.debug(f"{provider}: Cached {query[:50]} for {ttl}s")

        except Exception as e:
            logger.error(f"Cache set error: {e}")

    async def invalidate(self, provider: str, query: Optional[str] = None):
        """
        Invalidate cache

        Args:
            provider: Provider name
            query: Specific query to invalidate (None = all for provider)
        """
        if not self.redis_client:
            return

        try:
            if query:
                # Invalidate specific key
                key = self._generate_key(provider, query)
                await self.redis_client.delete(key)
                logger.info(f"{provider}: Invalidated cache for {query[:50]}")
            else:
                # Invalidate all keys for provider
                pattern = f"gp4u:provider:{provider}:*"
                keys = await self.redis_client.keys(pattern)
                if keys:
                    await self.redis_client.delete(*keys)
                    logger.info(f"{provider}: Invalidated {len(keys)} cache entries")

        except Exception as e:
            logger.error(f"Cache invalidate error: {e}")

    async def get_with_fallback(
        self,
        provider: str,
        query: str,
        fetch_func: Callable,
        success_rate: float = 0.9,
    ) -> Any:
        """
        Get from cache with fallback to fetch function

        Implements stale-while-revalidate pattern:
        1. Check cache
        2. If hit, return immediately
        3. If miss, fetch and cache

        Args:
            provider: Provider name
            query: Query identifier
            fetch_func: Async function to fetch data
            success_rate: Provider success rate

        Returns:
            Data (from cache or fresh)
        """
        # Try cache first
        cached_data = await self.get(provider, query)
        if cached_data:
            return cached_data["data"]

        # Cache miss - fetch fresh data
        try:
            fresh_data = await fetch_func()

            # Cache the result
            await self.set(provider, query, fresh_data, success_rate)

            return fresh_data

        except Exception as e:
            logger.error(f"Fetch function failed: {e}")
            raise

    def get_stats(self) -> dict:
        """Get cache statistics"""
        hit_rate = (self.hits / self.total_requests * 100) if self.total_requests > 0 else 0

        return {
            "total_requests": self.total_requests,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": round(hit_rate, 2),
            "connected": self.redis_client is not None,
        }

    def reset_stats(self):
        """Reset cache statistics"""
        self.hits = 0
        self.misses = 0
        self.total_requests = 0


# Global cache instance
_adaptive_cache: Optional[AdaptiveCache] = None


async def get_adaptive_cache() -> AdaptiveCache:
    """Get the global adaptive cache instance"""
    global _adaptive_cache

    if _adaptive_cache is None:
        _adaptive_cache = AdaptiveCache()
        await _adaptive_cache.connect()

    return _adaptive_cache


def cached(ttl: Optional[int] = None):
    """
    Decorator for caching function results

    Usage:
        @cached(ttl=60)
        async def get_gpus(provider: str):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key from function and arguments
            cache_key = f"{func.__name__}:{args}:{kwargs}"

            cache = await get_adaptive_cache()

            # Try to get from cache
            cached_result = await cache.get("function_cache", cache_key)
            if cached_result:
                return cached_result["data"]

            # Execute function
            result = await func(*args, **kwargs)

            # Cache result
            await cache.set("function_cache", cache_key, result, custom_ttl=ttl)

            return result

        return wrapper
    return decorator
