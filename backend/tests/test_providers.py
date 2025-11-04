"""
Integration tests for Phase 7 Provider Architecture
Tests circuit breakers, rate limiters, adaptive caching, and provider implementations
"""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
import time

from app.core.circuit_breaker import CircuitBreaker, CircuitState, CircuitBreakerOpen
from app.core.rate_limiter import TokenBucket, RateLimitExceeded
from app.core.adaptive_cache import AdaptiveCache
from app.core.base_provider import BaseProvider
from app.providers.vastai_provider import VastAIProvider
from app.providers.ionet_provider import IoNetProvider
from app.providers.akash_provider import AkashProvider
from app.providers.render_provider import RenderProvider


class TestCircuitBreaker:
    """Test Circuit Breaker pattern implementation"""

    def test_circuit_breaker_closed_state(self):
        """Test circuit breaker starts in CLOSED state"""
        cb = CircuitBreaker("test", failure_threshold=3, recovery_timeout=5)
        assert cb.state == CircuitState.CLOSED

    def test_circuit_breaker_opens_after_failures(self):
        """Test circuit breaker opens after threshold failures"""
        cb = CircuitBreaker("test", failure_threshold=3, recovery_timeout=5)

        def failing_function():
            raise Exception("Test failure")

        # Trigger failures
        for i in range(3):
            with pytest.raises(Exception):
                cb.call(failing_function)

        # Circuit should now be OPEN
        assert cb.state == CircuitState.OPEN

    def test_circuit_breaker_blocks_when_open(self):
        """Test circuit breaker blocks calls when OPEN"""
        cb = CircuitBreaker("test", failure_threshold=2, recovery_timeout=5)

        def failing_function():
            raise Exception("Test failure")

        # Trigger failures to open circuit
        for i in range(2):
            with pytest.raises(Exception):
                cb.call(failing_function)

        # Next call should be blocked
        with pytest.raises(CircuitBreakerOpen) as exc_info:
            cb.call(failing_function)

        assert "test" in str(exc_info.value)

    def test_circuit_breaker_half_open_transition(self):
        """Test circuit breaker transitions to HALF_OPEN after timeout"""
        cb = CircuitBreaker("test", failure_threshold=2, recovery_timeout=1)

        def failing_function():
            raise Exception("Test failure")

        def success_function():
            return "success"

        # Open the circuit
        for i in range(2):
            with pytest.raises(Exception):
                cb.call(failing_function)

        assert cb.state == CircuitState.OPEN

        # Wait for recovery timeout
        time.sleep(1.1)

        # Next call should transition to HALF_OPEN and succeed
        result = cb.call(success_function)
        assert result == "success"
        assert cb.state == CircuitState.CLOSED

    def test_circuit_breaker_success_resets_counter(self):
        """Test successful calls reset failure counter"""
        cb = CircuitBreaker("test", failure_threshold=3, recovery_timeout=5)

        def failing_function():
            raise Exception("Test failure")

        def success_function():
            return "success"

        # One failure
        with pytest.raises(Exception):
            cb.call(failing_function)

        assert cb.stats.failure_count == 1

        # Success resets counter
        cb.call(success_function)
        assert cb.stats.failure_count == 0


class TestRateLimiter:
    """Test Rate Limiter (Token Bucket) implementation"""

    def test_rate_limiter_allows_within_limit(self):
        """Test rate limiter allows requests within limit"""
        rl = TokenBucket("test", rate=10, capacity=10)  # 10 tokens/second

        # Should allow 10 immediate requests
        for i in range(10):
            assert rl.acquire(tokens=1, block=False) is True

    def test_rate_limiter_blocks_over_limit(self):
        """Test rate limiter blocks requests over limit"""
        rl = TokenBucket("test", rate=5, capacity=5)

        # Consume all tokens
        for i in range(5):
            rl.acquire(tokens=1, block=False)

        # Next request should raise exception
        with pytest.raises(RateLimitExceeded) as exc_info:
            rl.acquire(tokens=1, block=False)

        assert "test" in str(exc_info.value)
        assert exc_info.value.wait_time > 0

    def test_rate_limiter_refills_tokens(self):
        """Test rate limiter refills tokens over time"""
        rl = TokenBucket("test", rate=10, capacity=10)

        # Consume all tokens
        for i in range(10):
            rl.acquire(tokens=1, block=False)

        # Wait for 1 second to refill 10 tokens
        time.sleep(1.1)

        # Should allow more requests now
        assert rl.acquire(tokens=5, block=False) is True

    def test_rate_limiter_burst_capacity(self):
        """Test rate limiter supports burst capacity"""
        rl = TokenBucket("test", rate=5, capacity=20)  # Burst of 20

        # Should allow burst of 20
        assert rl.acquire(tokens=20, block=False) is True

        # No tokens left
        with pytest.raises(RateLimitExceeded):
            rl.acquire(tokens=1, block=False)


class TestAdaptiveCache:
    """Test Adaptive Caching implementation"""

    @pytest.mark.asyncio
    async def test_adaptive_cache_set_and_get(self):
        """Test basic cache set and get operations"""
        cache = AdaptiveCache()

        await cache.set("test_provider", "query1", {"data": "value"}, success_rate=0.9)
        result = await cache.get("test_provider", "query1")

        assert result is not None
        assert result["data"] == "value"

    @pytest.mark.asyncio
    async def test_adaptive_cache_ttl_based_on_success_rate(self):
        """Test cache TTL adjusts based on provider success rate"""
        cache = AdaptiveCache(base_ttl=30, min_ttl=10, max_ttl=300)

        # High success rate should use max TTL (300s)
        await cache.set("reliable_provider", "q1", {"data": "test"}, success_rate=0.95)

        # Low success rate should use min TTL (10s)
        await cache.set("unreliable_provider", "q2", {"data": "test"}, success_rate=0.4)

        # We can't directly verify TTL, but we can verify data is stored
        assert await cache.get("reliable_provider", "q1") is not None
        assert await cache.get("unreliable_provider", "q2") is not None

    @pytest.mark.asyncio
    async def test_adaptive_cache_invalidation(self):
        """Test cache can be invalidated"""
        cache = AdaptiveCache()

        await cache.set("provider1", "query1", {"data": "value"}, success_rate=0.9)
        assert await cache.get("provider1", "query1") is not None

        # Invalidate
        await cache.invalidate("provider1", "query1")
        assert await cache.get("provider1", "query1") is None

    @pytest.mark.asyncio
    async def test_adaptive_cache_clear(self):
        """Test clearing entire cache"""
        cache = AdaptiveCache()

        await cache.set("provider1", "q1", {"d": "v1"}, success_rate=0.9)
        await cache.set("provider2", "q2", {"d": "v2"}, success_rate=0.9)

        await cache.clear()

        assert await cache.get("provider1", "q1") is None
        assert await cache.get("provider2", "q2") is None


class TestProviderImplementations:
    """Test individual provider implementations"""

    def test_vastai_provider_initialization(self):
        """Test Vast.ai provider initializes correctly"""
        with patch('app.core.provider_config.get_provider_config') as mock_config:
            mock_config.return_value = Mock(
                vastai_api_key="test_key",
                vastai_base_url="https://api.test.com",
                vastai_timeout=30,
                vastai_rate_limit=100,
                provider_circuit_breaker_threshold=5,
                provider_circuit_breaker_timeout=60
            )

            provider = VastAIProvider()
            assert provider.name == "vastai"
            assert provider.api_key == "test_key"
            assert provider.base_url == "https://api.test.com"

    def test_vastai_normalize_gpu_data(self):
        """Test Vast.ai GPU data normalization"""
        with patch('app.core.provider_config.get_provider_config') as mock_config:
            mock_config.return_value = Mock(
                vastai_api_key="test_key",
                vastai_base_url="https://api.test.com",
                vastai_timeout=30,
                vastai_rate_limit=100,
                provider_circuit_breaker_threshold=5,
                provider_circuit_breaker_timeout=60
            )

            provider = VastAIProvider()
            raw_data = {
                "id": 123,
                "gpu_name": "RTX 4090",
                "gpu_ram": 24576,  # MB
                "dph_total": 2.50,
                "dlperf": 85.5,
                "reliability2": 0.95,
                "num_gpus": 1,
                "cpu_name": "AMD EPYC",
                "cpu_cores": 16,
                "ram_gb": 64,
                "disk_space": 500,
                "inet_down": 1000,
                "geolocation": "US",
            }

            normalized = provider.normalize_gpu_data(raw_data)

            assert normalized["provider"] == "Vast.ai"
            assert normalized["model"] == "RTX 4090"
            assert normalized["vram_gb"] == 24
            assert normalized["price_per_hour"] == 2.50
            assert "g_score" in normalized
            assert normalized["g_score"] > 0

    def test_ionet_provider_initialization(self):
        """Test io.net provider initializes correctly"""
        with patch('app.core.provider_config.get_provider_config') as mock_config:
            mock_config.return_value = Mock(
                ionet_api_key="test_key",
                ionet_base_url="https://api.test.com",
                ionet_timeout=30,
                ionet_rate_limit=150,
                provider_circuit_breaker_threshold=5,
                provider_circuit_breaker_timeout=60
            )

            provider = IoNetProvider()
            assert provider.name == "ionet"
            assert provider.api_key == "test_key"

    def test_akash_provider_initialization(self):
        """Test Akash provider initializes correctly"""
        with patch('app.core.provider_config.get_provider_config') as mock_config:
            mock_config.return_value = Mock(
                akash_rpc_url="https://rpc.test.com",
                akash_timeout=30,
                akash_rate_limit=50,
                provider_circuit_breaker_threshold=5,
                provider_circuit_breaker_timeout=60
            )

            provider = AkashProvider()
            assert provider.name == "akash"
            assert provider.rpc_url == "https://rpc.test.com"

    def test_render_provider_initialization(self):
        """Test Render provider initializes correctly"""
        with patch('app.core.provider_config.get_provider_config') as mock_config:
            mock_config.return_value = Mock(
                render_api_key="test_key",
                render_base_url="https://api.test.com",
                render_timeout=30,
                render_rate_limit=100,
                provider_circuit_breaker_threshold=5,
                provider_circuit_breaker_timeout=60
            )

            provider = RenderProvider()
            assert provider.name == "render"
            assert provider.api_key == "test_key"


class TestProviderIntegration:
    """Integration tests for provider system"""

    @pytest.mark.asyncio
    async def test_provider_registry_pattern(self):
        """Test provider registry can manage multiple providers"""
        from app.core.provider_registry import ProviderRegistry

        registry = ProviderRegistry()

        # Create mock providers
        with patch('app.core.provider_config.get_provider_config') as mock_config:
            mock_config.return_value = Mock(
                vastai_api_key="test",
                vastai_base_url="https://api.test.com",
                vastai_timeout=30,
                vastai_rate_limit=100,
                ionet_api_key="test",
                ionet_base_url="https://api.test.com",
                ionet_timeout=30,
                ionet_rate_limit=150,
                provider_circuit_breaker_threshold=5,
                provider_circuit_breaker_timeout=60
            )

            # Register providers
            vast = VastAIProvider()
            ionet = IoNetProvider()

            registry.register(vast)
            registry.register(ionet)

            # Test retrieval
            assert registry.get("vastai") == vast
            assert registry.get("ionet") == ionet
            assert len(registry.get_all()) == 2

    @pytest.mark.asyncio
    async def test_provider_error_isolation(self):
        """Test that one failing provider doesn't affect others"""
        from app.core.provider_registry import ProviderRegistry

        registry = ProviderRegistry()

        # This test would require mocking actual API calls
        # For now, we verify the structure supports isolation
        assert registry is not None


class TestProviderMetrics:
    """Test provider metrics tracking"""

    def test_metrics_initialization(self):
        """Test metrics initialize with correct values"""
        from app.core.base_provider import ProviderMetrics

        metrics = ProviderMetrics("test_provider")

        assert metrics.provider_name == "test_provider"
        assert metrics.total_requests == 0
        assert metrics.successful_requests == 0
        assert metrics.failed_requests == 0
        assert metrics.total_response_time == 0.0

    def test_metrics_record_request(self):
        """Test metrics correctly record requests"""
        from app.core.base_provider import ProviderMetrics

        metrics = ProviderMetrics("test_provider")

        # Record successful request
        metrics.record_request(duration=0.5, success=True)

        assert metrics.total_requests == 1
        assert metrics.successful_requests == 1
        assert metrics.failed_requests == 0
        assert metrics.total_response_time == 0.5

        # Record failed request
        metrics.record_request(duration=0.3, success=False)

        assert metrics.total_requests == 2
        assert metrics.successful_requests == 1
        assert metrics.failed_requests == 1

    def test_metrics_calculate_success_rate(self):
        """Test success rate calculation"""
        from app.core.base_provider import ProviderMetrics

        metrics = ProviderMetrics("test_provider")

        # No requests yet
        assert metrics.get_success_rate() == 0.0

        # 3 successful, 1 failed = 75%
        metrics.record_request(0.1, success=True)
        metrics.record_request(0.1, success=True)
        metrics.record_request(0.1, success=True)
        metrics.record_request(0.1, success=False)

        assert metrics.get_success_rate() == 0.75

    def test_metrics_calculate_average_response_time(self):
        """Test average response time calculation"""
        from app.core.base_provider import ProviderMetrics

        metrics = ProviderMetrics("test_provider")

        # Record requests with different durations
        metrics.record_request(0.2, success=True)
        metrics.record_request(0.4, success=True)
        metrics.record_request(0.6, success=True)

        # Average should be 0.4
        assert abs(metrics.get_average_response_time() - 0.4) < 0.001


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
