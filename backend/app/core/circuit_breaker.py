"""
Circuit Breaker Pattern Implementation
Prevents cascading failures by tracking provider health
"""

import time
import logging
from enum import Enum
from typing import Callable, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Failures exceeded threshold
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class CircuitBreakerStats:
    """Circuit breaker statistics"""
    failure_count: int = 0
    success_count: int = 0
    last_failure_time: Optional[float] = None
    last_success_time: Optional[float] = None
    state_changes: list[tuple[CircuitState, float]] = field(default_factory=list)

    def record_success(self):
        """Record a successful call"""
        self.success_count += 1
        self.last_success_time = time.time()
        self.failure_count = 0  # Reset failure count on success

    def record_failure(self):
        """Record a failed call"""
        self.failure_count += 1
        self.last_failure_time = time.time()

    def record_state_change(self, state: CircuitState):
        """Record a state transition"""
        self.state_changes.append((state, time.time()))


class CircuitBreakerOpen(Exception):
    """Raised when circuit breaker is open"""
    def __init__(self, provider: str, retry_after: float):
        self.provider = provider
        self.retry_after = retry_after
        super().__init__(
            f"Circuit breaker OPEN for {provider}. "
            f"Retry after {retry_after:.1f} seconds"
        )


class CircuitBreaker:
    """
    Circuit Breaker implementation for provider reliability

    States:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Too many failures, block all requests
    - HALF_OPEN: Testing recovery, allow limited requests
    """

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        success_threshold: int = 2,
    ):
        """
        Initialize circuit breaker

        Args:
            name: Circuit breaker name (usually provider name)
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds to wait before attempting recovery
            success_threshold: Successful calls needed to close circuit from half-open
        """
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold

        self.state = CircuitState.CLOSED
        self.stats = CircuitBreakerStats()
        self._last_state_change = time.time()

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to try recovery"""
        return time.time() - self._last_state_change >= self.recovery_timeout

    def _transition_to(self, new_state: CircuitState):
        """Transition to a new state"""
        old_state = self.state
        self.state = new_state
        self._last_state_change = time.time()
        self.stats.record_state_change(new_state)

        logger.info(
            f"Circuit breaker '{self.name}' transitioned: "
            f"{old_state.value} -> {new_state.value}"
        )

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute a function through the circuit breaker

        Args:
            func: Function to execute
            *args, **kwargs: Arguments to pass to the function

        Returns:
            Result of the function call

        Raises:
            CircuitBreakerOpen: If circuit is open
            Exception: Any exception from the function
        """
        # Check current state
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self._transition_to(CircuitState.HALF_OPEN)
            else:
                retry_after = self.recovery_timeout - (time.time() - self._last_state_change)
                raise CircuitBreakerOpen(self.name, retry_after)

        # Attempt the call
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e

    def _on_success(self):
        """Handle successful call"""
        self.stats.record_success()

        if self.state == CircuitState.HALF_OPEN:
            if self.stats.success_count >= self.success_threshold:
                self._transition_to(CircuitState.CLOSED)
                logger.info(f"Circuit breaker '{self.name}' recovered after {self.success_threshold} successes")

    def _on_failure(self):
        """Handle failed call"""
        self.stats.record_failure()

        if self.state == CircuitState.HALF_OPEN:
            # Failed during recovery test, go back to open
            self._transition_to(CircuitState.OPEN)
            logger.warning(f"Circuit breaker '{self.name}' failed recovery test")

        elif self.state == CircuitState.CLOSED:
            if self.stats.failure_count >= self.failure_threshold:
                self._transition_to(CircuitState.OPEN)
                logger.error(
                    f"Circuit breaker '{self.name}' opened after "
                    f"{self.stats.failure_count} failures"
                )

    def get_state(self) -> CircuitState:
        """Get current circuit state"""
        return self.state

    def get_stats(self) -> CircuitBreakerStats:
        """Get circuit breaker statistics"""
        return self.stats

    def reset(self):
        """Manually reset the circuit breaker"""
        self.state = CircuitState.CLOSED
        self.stats = CircuitBreakerStats()
        self._last_state_change = time.time()
        logger.info(f"Circuit breaker '{self.name}' manually reset")

    def is_healthy(self) -> bool:
        """Check if circuit is allowing requests"""
        return self.state in (CircuitState.CLOSED, CircuitState.HALF_OPEN)


class CircuitBreakerRegistry:
    """Registry to manage multiple circuit breakers"""

    def __init__(self):
        self._breakers: dict[str, CircuitBreaker] = {}

    def get_or_create(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        success_threshold: int = 2,
    ) -> CircuitBreaker:
        """Get existing circuit breaker or create new one"""
        if name not in self._breakers:
            self._breakers[name] = CircuitBreaker(
                name=name,
                failure_threshold=failure_threshold,
                recovery_timeout=recovery_timeout,
                success_threshold=success_threshold,
            )
        return self._breakers[name]

    def get(self, name: str) -> Optional[CircuitBreaker]:
        """Get circuit breaker by name"""
        return self._breakers.get(name)

    def get_all_stats(self) -> dict[str, tuple[CircuitState, CircuitBreakerStats]]:
        """Get stats for all circuit breakers"""
        return {
            name: (breaker.get_state(), breaker.get_stats())
            for name, breaker in self._breakers.items()
        }

    def reset_all(self):
        """Reset all circuit breakers"""
        for breaker in self._breakers.values():
            breaker.reset()

    def get_healthy_count(self) -> int:
        """Get count of healthy circuits"""
        return sum(1 for breaker in self._breakers.values() if breaker.is_healthy())

    def get_unhealthy_providers(self) -> list[str]:
        """Get list of providers with open circuits"""
        return [
            name for name, breaker in self._breakers.items()
            if breaker.get_state() == CircuitState.OPEN
        ]


# Global registry
_circuit_breaker_registry = CircuitBreakerRegistry()


def get_circuit_breaker_registry() -> CircuitBreakerRegistry:
    """Get the global circuit breaker registry"""
    return _circuit_breaker_registry
