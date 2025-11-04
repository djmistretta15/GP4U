"""
Rate Limiter Implementation
Token Bucket algorithm for API rate limiting
"""

import time
import logging
from typing import Optional
from dataclasses import dataclass
from threading import Lock

logger = logging.getLogger(__name__)


@dataclass
class RateLimitExceeded(Exception):
    """Raised when rate limit is exceeded"""
    provider: str
    retry_after: float

    def __str__(self):
        return (
            f"Rate limit exceeded for {self.provider}. "
            f"Retry after {self.retry_after:.2f} seconds"
        )


class TokenBucket:
    """
    Token Bucket Rate Limiter

    Tokens are added to the bucket at a constant rate.
    Each request consumes a token.
    When bucket is empty, requests are rate limited.
    """

    def __init__(
        self,
        name: str,
        rate: float,  # tokens per second
        capacity: Optional[int] = None,
    ):
        """
        Initialize token bucket

        Args:
            name: Bucket name (usually provider name)
            rate: Tokens added per second
            capacity: Maximum bucket size (defaults to rate)
        """
        self.name = name
        self.rate = rate
        self.capacity = capacity or int(rate)

        self._tokens = float(self.capacity)
        self._last_update = time.time()
        self._lock = Lock()

        logger.info(
            f"Rate limiter '{name}' initialized: "
            f"{rate} tokens/sec, capacity {self.capacity}"
        )

    def _refill(self):
        """Refill tokens based on elapsed time"""
        now = time.time()
        elapsed = now - self._last_update

        # Add tokens based on elapsed time
        new_tokens = elapsed * self.rate
        self._tokens = min(self.capacity, self._tokens + new_tokens)
        self._last_update = now

    def acquire(self, tokens: int = 1, block: bool = True, timeout: Optional[float] = None) -> bool:
        """
        Acquire tokens from the bucket

        Args:
            tokens: Number of tokens to acquire
            block: If True, wait for tokens to become available
            timeout: Maximum time to wait (only if block=True)

        Returns:
            True if tokens acquired, False if not available and block=False

        Raises:
            RateLimitExceeded: If tokens not available and block=False
        """
        start_time = time.time()

        while True:
            with self._lock:
                self._refill()

                if self._tokens >= tokens:
                    self._tokens -= tokens
                    return True

                if not block:
                    wait_time = (tokens - self._tokens) / self.rate
                    raise RateLimitExceeded(self.name, wait_time)

                # Calculate wait time
                wait_time = (tokens - self._tokens) / self.rate

                # Check timeout
                if timeout is not None:
                    elapsed = time.time() - start_time
                    if elapsed >= timeout:
                        raise RateLimitExceeded(self.name, wait_time)
                    wait_time = min(wait_time, timeout - elapsed)

            # Sleep and retry
            time.sleep(min(wait_time, 0.1))  # Sleep max 100ms at a time

    def get_available_tokens(self) -> float:
        """Get current number of available tokens"""
        with self._lock:
            self._refill()
            return self._tokens

    def get_wait_time(self, tokens: int = 1) -> float:
        """Get estimated wait time for tokens to become available"""
        with self._lock:
            self._refill()
            if self._tokens >= tokens:
                return 0.0
            return (tokens - self._tokens) / self.rate

    def reset(self):
        """Reset the bucket to full capacity"""
        with self._lock:
            self._tokens = float(self.capacity)
            self._last_update = time.time()
        logger.info(f"Rate limiter '{self.name}' reset")


class RateLimiterRegistry:
    """Registry to manage multiple rate limiters"""

    def __init__(self):
        self._limiters: dict[str, TokenBucket] = {}
        self._lock = Lock()

    def get_or_create(
        self,
        name: str,
        requests_per_minute: int,
    ) -> TokenBucket:
        """Get existing rate limiter or create new one"""
        with self._lock:
            if name not in self._limiters:
                # Convert requests per minute to tokens per second
                rate = requests_per_minute / 60.0
                self._limiters[name] = TokenBucket(
                    name=name,
                    rate=rate,
                    capacity=requests_per_minute,  # Allow burst up to 1 minute worth
                )
            return self._limiters[name]

    def get(self, name: str) -> Optional[TokenBucket]:
        """Get rate limiter by name"""
        return self._limiters.get(name)

    def get_all_stats(self) -> dict[str, dict]:
        """Get stats for all rate limiters"""
        return {
            name: {
                "available_tokens": limiter.get_available_tokens(),
                "capacity": limiter.capacity,
                "rate": limiter.rate,
                "utilization": 1.0 - (limiter.get_available_tokens() / limiter.capacity),
            }
            for name, limiter in self._limiters.items()
        }

    def reset_all(self):
        """Reset all rate limiters"""
        for limiter in self._limiters.values():
            limiter.reset()


# Global registry
_rate_limiter_registry = RateLimiterRegistry()


def get_rate_limiter_registry() -> RateLimiterRegistry:
    """Get the global rate limiter registry"""
    return _rate_limiter_registry
