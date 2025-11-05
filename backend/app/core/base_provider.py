"""
Base Provider Class
Abstract base class for all GPU provider integrations
with retry logic, circuit breaker, rate limiting, and metrics
"""

import time
import logging
import random
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Type
from datetime import datetime
from enum import Enum

import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)

from .circuit_breaker import get_circuit_breaker_registry, CircuitBreakerOpen
from .rate_limiter import get_rate_limiter_registry, RateLimitExceeded
from .provider_config import get_provider_config


logger = logging.getLogger(__name__)


class ProviderStatus(Enum):
    """Provider health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"


class ProviderMetrics:
    """Track provider performance metrics"""

    def __init__(self, provider_name: str):
        self.provider_name = provider_name
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.total_response_time = 0.0
        self.slow_requests = 0
        self.circuit_breaker_trips = 0
        self.rate_limit_hits = 0
        self.last_request_time: Optional[float] = None
        self.first_request_time: Optional[float] = None

    def record_request(self, duration: float, success: bool, slow_threshold: float = 5.0):
        """Record a request"""
        if self.first_request_time is None:
            self.first_request_time = time.time()

        self.total_requests += 1
        self.last_request_time = time.time()
        self.total_response_time += duration

        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1

        if duration > slow_threshold:
            self.slow_requests += 1

    def record_circuit_breaker_trip(self):
        """Record circuit breaker opening"""
        self.circuit_breaker_trips += 1

    def record_rate_limit_hit(self):
        """Record rate limit exceeded"""
        self.rate_limit_hits += 1

    def get_stats(self) -> Dict[str, Any]:
        """Get metrics as dictionary"""
        avg_response_time = (
            self.total_response_time / self.total_requests
            if self.total_requests > 0
            else 0
        )

        success_rate = (
            self.successful_requests / self.total_requests * 100
            if self.total_requests > 0
            else 0
        )

        uptime = (
            time.time() - self.first_request_time
            if self.first_request_time
            else 0
        )

        return {
            "provider": self.provider_name,
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "success_rate": round(success_rate, 2),
            "avg_response_time": round(avg_response_time, 3),
            "slow_requests": self.slow_requests,
            "circuit_breaker_trips": self.circuit_breaker_trips,
            "rate_limit_hits": self.rate_limit_hits,
            "uptime_seconds": round(uptime, 2),
            "last_request_time": (
                datetime.fromtimestamp(self.last_request_time).isoformat()
                if self.last_request_time
                else None
            ),
        }


class BaseProvider(ABC):
    """
    Abstract base class for GPU providers

    Provides:
    - Automatic retry with exponential backoff
    - Circuit breaker pattern
    - Rate limiting
    - Performance metrics
    - Request logging
    - Error handling
    """

    def __init__(self, name: str):
        """
        Initialize provider

        Args:
            name: Provider name (vastai, akash, render, ionet)
        """
        self.name = name
        self.config = get_provider_config()

        # Get provider-specific configuration
        self.timeout = getattr(self.config, f"{name}_timeout", 30)
        self.max_retries = getattr(self.config, f"{name}_max_retries", 3)
        self.rate_limit = getattr(self.config, f"{name}_rate_limit", 100)

        # Initialize circuit breaker
        cb_registry = get_circuit_breaker_registry()
        self.circuit_breaker = cb_registry.get_or_create(
            name=name,
            failure_threshold=self.config.provider_circuit_breaker_threshold,
            recovery_timeout=self.config.provider_circuit_breaker_timeout,
        )

        # Initialize rate limiter
        rl_registry = get_rate_limiter_registry()
        self.rate_limiter = rl_registry.get_or_create(
            name=name,
            requests_per_minute=self.rate_limit,
        )

        # Initialize metrics
        self.metrics = ProviderMetrics(name)

        # HTTP client
        self.client = httpx.AsyncClient(timeout=self.timeout)

        logger.info(f"Provider '{name}' initialized")

    async def close(self):
        """Close provider resources"""
        await self.client.aclose()

    @abstractmethod
    async def fetch_gpus(self) -> List[Dict[str, Any]]:
        """
        Fetch available GPUs from provider

        Returns:
            List of GPU data dictionaries

        Raises:
            Exception: On fetch failure
        """
        pass

    @abstractmethod
    def normalize_gpu_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize provider-specific GPU data to common format

        Args:
            raw_data: Raw GPU data from provider

        Returns:
            Normalized GPU dictionary with standard fields
        """
        pass

    async def get_gpus(self) -> List[Dict[str, Any]]:
        """
        Get GPUs with all reliability patterns applied

        Returns:
            List of normalized GPU dictionaries
        """
        start_time = time.time()

        try:
            # Apply rate limiting
            try:
                self.rate_limiter.acquire(tokens=1, block=False)
            except RateLimitExceeded as e:
                self.metrics.record_rate_limit_hit()
                logger.warning(f"{self.name}: Rate limit exceeded, retry after {e.retry_after:.2f}s")
                raise

            # Apply circuit breaker
            try:
                raw_gpus = await self.circuit_breaker.call(self._fetch_with_retry)
            except CircuitBreakerOpen as e:
                self.metrics.record_circuit_breaker_trip()
                logger.warning(f"{self.name}: {str(e)}")
                raise

            # Normalize data
            normalized_gpus = [self.normalize_gpu_data(gpu) for gpu in raw_gpus]

            # Record success
            duration = time.time() - start_time
            self.metrics.record_request(duration, success=True)

            if self.config.provider_log_requests:
                logger.info(
                    f"{self.name}: Fetched {len(normalized_gpus)} GPUs "
                    f"in {duration:.2f}s"
                )

            return normalized_gpus

        except Exception as e:
            duration = time.time() - start_time
            self.metrics.record_request(duration, success=False)
            logger.error(f"{self.name}: Failed to fetch GPUs: {str(e)}")
            raise

    async def _fetch_with_retry(self) -> List[Dict[str, Any]]:
        """
        Fetch with retry logic

        Uses tenacity for exponential backoff with jitter
        """

        @retry(
            stop=stop_after_attempt(self.max_retries),
            wait=wait_exponential(multiplier=1, min=2, max=30) +
                 wait_exponential(multiplier=0.5, min=0, max=2),  # Add jitter
            retry=retry_if_exception_type((httpx.HTTPError, TimeoutError)),
            before_sleep=before_sleep_log(logger, logging.WARNING),
        )
        async def _fetch():
            return await self.fetch_gpus()

        return await _fetch()

    def get_status(self) -> ProviderStatus:
        """Get current provider health status"""
        circuit_state = self.circuit_breaker.get_state()

        if not self.circuit_breaker.is_healthy():
            return ProviderStatus.UNAVAILABLE

        # Check success rate
        stats = self.metrics.get_stats()
        if stats["total_requests"] > 10:  # Need minimum requests for stats
            if stats["success_rate"] < 50:
                return ProviderStatus.UNAVAILABLE
            elif stats["success_rate"] < 90:
                return ProviderStatus.DEGRADED

        return ProviderStatus.HEALTHY

    def get_metrics(self) -> Dict[str, Any]:
        """Get provider metrics"""
        return {
            **self.metrics.get_stats(),
            "status": self.get_status().value,
            "circuit_breaker_state": self.circuit_breaker.get_state().value,
            "rate_limiter_tokens": self.rate_limiter.get_available_tokens(),
        }

    async def health_check(self) -> bool:
        """
        Perform health check

        Returns:
            True if provider is healthy
        """
        try:
            gpus = await self.get_gpus()
            return len(gpus) >= 0  # Successful fetch, even if empty
        except Exception as e:
            logger.error(f"{self.name}: Health check failed: {str(e)}")
            return False

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name='{self.name}', status='{self.get_status().value}')>"


class ProviderRegistry:
    """Registry for managing multiple providers"""

    def __init__(self):
        self._providers: Dict[str, BaseProvider] = {}

    def register(self, provider: BaseProvider):
        """Register a provider"""
        self._providers[provider.name] = provider
        logger.info(f"Registered provider: {provider.name}")

    def get(self, name: str) -> Optional[BaseProvider]:
        """Get provider by name"""
        return self._providers.get(name)

    def get_all(self) -> List[BaseProvider]:
        """Get all providers"""
        return list(self._providers.values())

    def get_healthy(self) -> List[BaseProvider]:
        """Get all healthy providers"""
        return [
            p for p in self._providers.values()
            if p.get_status() == ProviderStatus.HEALTHY
        ]

    def get_all_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get metrics for all providers"""
        return {
            name: provider.get_metrics()
            for name, provider in self._providers.items()
        }

    async def health_check_all(self) -> Dict[str, bool]:
        """Health check all providers"""
        results = {}
        for name, provider in self._providers.items():
            results[name] = await provider.health_check()
        return results

    async def close_all(self):
        """Close all providers"""
        for provider in self._providers.values():
            await provider.close()


# Global registry
_provider_registry = ProviderRegistry()


def get_provider_registry() -> ProviderRegistry:
    """Get the global provider registry"""
    return _provider_registry
