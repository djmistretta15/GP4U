# 🔧 Provider Setup Guide

Complete guide for configuring and using GP4U's enterprise-grade GPU provider integrations.

---

## Overview

GP4U integrates with 4 major GPU providers using production-grade reliability patterns:

| Provider | GPUs | Best For | API Key Required |
|----------|------|----------|------------------|
| **Vast.ai** | 10,000+ | Deep Learning, Training | ✅ Yes |
| **io.net** | 327,000+ | Distributed AI/ML, Clusters | ✅ Yes |
| **Akash Network** | 5,000+ | Cost-effective Cloud | ❌ No (Public RPC) |
| **Render Network** | 8,000+ | GPU Rendering, Generative AI | ✅ Yes |

---

## Quick Start

### 1. Configure Environment Variables

Copy the example environment file:

```bash
cd backend
cp .env.example .env
```

Edit `.env` with your provider API keys:

```bash
# Vast.ai
VASTAI_API_KEY=your_vastai_api_key_here
VASTAI_ENABLED=true

# io.net
IONET_API_KEY=your_ionet_api_key_here
IONET_ENABLED=true

# Akash Network (no API key needed!)
AKASH_ENABLED=true

# Render Network
RENDER_API_KEY=your_render_api_key_here
RENDER_ENABLED=true
```

### 2. Start the Application

```bash
# With Docker
docker-compose up

# Or manually
uvicorn app.main:app --reload
```

Providers initialize automatically on startup! Look for:
```
✅ Initialized 4 GPU providers
```

---

## Obtaining API Keys

### Vast.ai

1. **Sign up** at [https://vast.ai](https://vast.ai)
2. Navigate to **Account** → **API Keys**
3. Click **"Create API Key"**
4. Copy the key and add to `.env`:
   ```bash
   VASTAI_API_KEY=your_key_here
   ```

**Rate Limit:** 100 requests/minute (default)
**Cost:** Free tier available
**Documentation:** [Vast.ai API Docs](https://vast.ai/docs/api)

### io.net

1. **Sign up** at [https://io.net](https://io.net)
2. Complete KYC verification (required)
3. Navigate to **Developer** → **API Access**
4. Generate API key
5. Add to `.env`:
   ```bash
   IONET_API_KEY=your_key_here
   ```

**Rate Limit:** 150 requests/minute (default)
**Cost:** $99/month API access
**Documentation:** [io.net API Docs](https://docs.io.net/api)

### Akash Network

**No API key required!** Akash uses public RPC endpoints:

```bash
AKASH_RPC_URL=https://rpc.cosmos.directory/akash
AKASH_ENABLED=true
```

**Rate Limit:** 50 requests/minute (public RPC limit)
**Cost:** Free
**Documentation:** [Akash Docs](https://docs.akash.network)

### Render Network

1. **Sign up** at [https://render.network](https://render.network)
2. Navigate to **Settings** → **API**
3. Generate API token
4. Add to `.env`:
   ```bash
   RENDER_API_KEY=your_key_here
   ```

**Rate Limit:** 100 requests/minute (default)
**Cost:** Contact sales
**Documentation:** [Render API Docs](https://docs.render.network)

---

## Configuration Options

### Provider-Specific Settings

Each provider has customizable settings:

```bash
# Vast.ai Configuration
VASTAI_API_KEY=your_key
VASTAI_BASE_URL=https://console.vast.ai/api/v0
VASTAI_RATE_LIMIT=100        # requests per minute
VASTAI_TIMEOUT=30            # seconds
VASTAI_ENABLED=true          # enable/disable provider

# io.net Configuration
IONET_API_KEY=your_key
IONET_BASE_URL=https://api.io.net/v1
IONET_RATE_LIMIT=150
IONET_TIMEOUT=30
IONET_ENABLED=true

# Akash Configuration
AKASH_RPC_URL=https://rpc.cosmos.directory/akash
AKASH_RATE_LIMIT=50
AKASH_TIMEOUT=30
AKASH_ENABLED=true

# Render Configuration
RENDER_API_KEY=your_key
RENDER_BASE_URL=https://api.render.network/v1
RENDER_RATE_LIMIT=100
RENDER_TIMEOUT=30
RENDER_ENABLED=true
```

### Circuit Breaker Settings

Control automatic failure isolation:

```bash
PROVIDER_CIRCUIT_BREAKER_THRESHOLD=5        # failures before opening
PROVIDER_CIRCUIT_BREAKER_TIMEOUT=60         # seconds before retry
PROVIDER_CIRCUIT_BREAKER_HALF_OPEN_MAX_CALLS=3  # test calls when recovering
```

**How it works:**
- **CLOSED** (Normal): All requests pass through
- **OPEN** (Failing): Blocks all requests after 5 failures
- **HALF_OPEN** (Testing): Allows 3 test requests after 60s timeout

### Rate Limiter Settings

Prevent API quota violations:

```bash
PROVIDER_RATE_LIMITER_ENABLED=true
```

Individual provider limits set via `*_RATE_LIMIT` variables above.

**Algorithm:** Token Bucket with burst capacity support

### Cache Settings

Optimize API usage with adaptive caching:

```bash
PROVIDER_CACHE_ENABLED=true
PROVIDER_CACHE_TTL=30           # base TTL in seconds
PROVIDER_CACHE_MAX_TTL=300      # max TTL for reliable providers
PROVIDER_CACHE_MIN_TTL=10       # min TTL for unreliable providers
```

**Adaptive TTL Strategy:**
- **90%+ success rate** → 300s TTL (5 minutes)
- **70-90% success rate** → 45s TTL
- **50-70% success rate** → 30s TTL
- **<50% success rate** → 10s TTL

### Retry Configuration

Control automatic retry behavior:

```bash
PROVIDER_MAX_RETRIES=3              # maximum retry attempts
PROVIDER_RETRY_BASE_DELAY=2         # initial delay in seconds
PROVIDER_RETRY_MAX_DELAY=32         # maximum delay in seconds
PROVIDER_RETRY_JITTER=1             # jitter in seconds
```

**Retry delays:** 2s → 4s → 8s → 16s → 32s (exponential backoff)
**Jitter:** Prevents thundering herd problem

---

## Monitoring & Health

### Health Check Endpoints

Check provider status in real-time:

```bash
# System-wide health
curl http://localhost:8000/api/v1/provider-health/health

# Response:
{
  "status": "healthy",
  "providers": {
    "vastai": {
      "status": "HEALTHY",
      "success_rate": 0.98,
      "avg_response_time": 245,
      "circuit_breaker": "CLOSED",
      "rate_limit_utilization": 0.45
    },
    "ionet": {...},
    "akash": {...},
    "render": {...}
  },
  "summary": {
    "total_providers": 4,
    "healthy": 4,
    "degraded": 0,
    "unavailable": 0
  }
}
```

### Provider-Specific Health

```bash
# Detailed health for specific provider
curl http://localhost:8000/api/v1/provider-health/providers/vastai/health

# Manual health check (tests API connectivity)
curl -X POST http://localhost:8000/api/v1/provider-health/providers/vastai/health-check
```

### Circuit Breaker Status

```bash
# View all circuit breakers
curl http://localhost:8000/api/v1/provider-health/circuit-breakers

# Response:
{
  "vastai": {
    "state": "CLOSED",
    "failure_count": 0,
    "success_count": 1523,
    "last_failure_time": null,
    "trip_count": 0
  },
  "ionet": {...}
}

# Manual reset (if needed)
curl -X POST http://localhost:8000/api/v1/provider-health/circuit-breakers/vastai/reset
```

### Rate Limiter Stats

```bash
# View rate limiter utilization
curl http://localhost:8000/api/v1/provider-health/rate-limiters

# Response:
{
  "vastai": {
    "rate": 100,
    "capacity": 100,
    "available_tokens": 87,
    "utilization": 0.13,
    "requests_blocked": 0
  }
}
```

### Cache Performance

```bash
# Cache statistics
curl http://localhost:8000/api/v1/provider-health/cache/stats

# Response:
{
  "total_hits": 4521,
  "total_misses": 892,
  "hit_ratio": 0.835,
  "providers": {
    "vastai": {
      "hits": 1234,
      "misses": 234,
      "hit_ratio": 0.84,
      "current_ttl": 300
    }
  }
}

# Invalidate cache (force fresh data)
curl -X POST http://localhost:8000/api/v1/provider-health/cache/invalidate?provider=vastai
```

### Comprehensive Metrics Dashboard

```bash
# All metrics in one call
curl http://localhost:8000/api/v1/provider-health/metrics/summary
```

---

## Testing Configuration

### Verify Provider Setup

1. **Check startup logs:**
   ```
   ✅ Initialized 4 GPU providers
   ```

2. **Test health endpoint:**
   ```bash
   curl http://localhost:8000/api/v1/provider-health/health
   ```

3. **Manual health check:**
   ```bash
   curl -X POST http://localhost:8000/api/v1/provider-health/providers/vastai/health-check
   ```

4. **Fetch GPUs:**
   ```bash
   curl http://localhost:8000/api/v1/providers/sync
   ```

### Run Integration Tests

```bash
cd backend
pytest tests/test_providers.py -v
```

Tests cover:
- ✅ Circuit breaker pattern (CLOSED → OPEN → HALF_OPEN)
- ✅ Rate limiter (token bucket algorithm)
- ✅ Adaptive caching (dynamic TTL)
- ✅ Provider implementations
- ✅ Error isolation
- ✅ Metrics tracking

---

## Troubleshooting

### Provider Not Initializing

**Symptom:** `⚠️ Provider initialization failed`

**Solutions:**
1. Check API key is valid:
   ```bash
   echo $VASTAI_API_KEY  # Should not be empty
   ```

2. Verify provider is enabled:
   ```bash
   grep VASTAI_ENABLED .env  # Should be true
   ```

3. Test API connectivity:
   ```bash
   curl -H "Authorization: Bearer $VASTAI_API_KEY" \
     https://console.vast.ai/api/v0/bundles
   ```

### Circuit Breaker Stuck Open

**Symptom:** `CircuitBreakerOpen` errors

**Solutions:**
1. Check provider health:
   ```bash
   curl http://localhost:8000/api/v1/provider-health/providers/vastai/health
   ```

2. Manual reset:
   ```bash
   curl -X POST http://localhost:8000/api/v1/provider-health/circuit-breakers/vastai/reset
   ```

3. Increase failure threshold:
   ```bash
   PROVIDER_CIRCUIT_BREAKER_THRESHOLD=10  # default: 5
   ```

### Rate Limit Exceeded

**Symptom:** `RateLimitExceeded` errors

**Solutions:**
1. Check rate limiter stats:
   ```bash
   curl http://localhost:8000/api/v1/provider-health/rate-limiters
   ```

2. Increase rate limit:
   ```bash
   VASTAI_RATE_LIMIT=200  # default: 100
   ```

3. Enable caching to reduce API calls:
   ```bash
   PROVIDER_CACHE_ENABLED=true
   PROVIDER_CACHE_TTL=60  # cache for 60 seconds
   ```

### Slow Response Times

**Solutions:**
1. Check metrics:
   ```bash
   curl http://localhost:8000/api/v1/provider-health/metrics/summary
   ```

2. Increase cache TTL:
   ```bash
   PROVIDER_CACHE_TTL=60  # default: 30
   PROVIDER_CACHE_MAX_TTL=600  # default: 300
   ```

3. Reduce timeout:
   ```bash
   VASTAI_TIMEOUT=15  # default: 30
   ```

### API Key Issues

**Invalid API Key:**
```
⚠️ Provider vastai initialization failed: 401 Unauthorized
```

**Solution:** Verify API key at provider dashboard

**API Key Expired:**
```
⚠️ Provider vastai initialization failed: 403 Forbidden
```

**Solution:** Regenerate API key

**Rate Limit Exceeded:**
```
⚠️ Provider vastai initialization failed: 429 Too Many Requests
```

**Solution:** Wait for rate limit reset or upgrade plan

---

## Production Recommendations

### Security

1. **Never commit API keys:**
   ```bash
   echo ".env" >> .gitignore
   ```

2. **Use environment variables in production:**
   ```bash
   export VASTAI_API_KEY="..."
   ```

3. **Rotate API keys regularly** (every 90 days)

### Performance

1. **Enable caching:**
   ```bash
   PROVIDER_CACHE_ENABLED=true
   PROVIDER_CACHE_TTL=60
   ```

2. **Tune rate limits:**
   - Start with conservative limits
   - Monitor `requests_blocked` in metrics
   - Gradually increase if needed

3. **Circuit breaker tuning:**
   - **High availability:** Increase threshold to 10
   - **Cost sensitive:** Decrease threshold to 3
   - **Fast recovery:** Decrease timeout to 30s

### Monitoring

1. **Set up health check monitoring:**
   ```bash
   # Cron job every 5 minutes
   */5 * * * * curl http://your-api/api/v1/provider-health/health
   ```

2. **Alert on degraded providers:**
   - Success rate < 70%
   - Circuit breaker OPEN for > 5 minutes
   - Rate limit utilization > 90%

3. **Track key metrics:**
   - Provider uptime
   - Average response time
   - Cache hit ratio
   - G-Score distribution

---

## Advanced Configuration

### Custom Provider Implementation

Create a new provider by extending `BaseProvider`:

```python
from app.core.base_provider import BaseProvider
from typing import List, Dict, Any

class MyCustomProvider(BaseProvider):
    def __init__(self):
        super().__init__("my_provider")
        self.api_key = config.my_provider_api_key
        self.base_url = config.my_provider_base_url

    async def fetch_gpus(self) -> List[Dict[str, Any]]:
        """Fetch GPUs from provider API"""
        response = await self.client.get(
            f"{self.base_url}/gpus",
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        return response.json()

    def normalize_gpu_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize to GP4U format"""
        return {
            "provider": "My Provider",
            "model": raw_data["gpu_model"],
            "vram_gb": raw_data["memory_gb"],
            "price_per_hour": raw_data["price"],
            "g_score": self._calculate_g_score(raw_data),
            # ... more fields
        }
```

Register in `provider_init.py`:
```python
custom = MyCustomProvider()
registry.register(custom)
```

### Load Balancing

Distribute requests across providers:

```python
from app.core.provider_registry import get_provider_registry

registry = get_provider_registry()
providers = registry.get_all_healthy()  # Only HEALTHY providers

# Round-robin
provider = providers[request_count % len(providers)]

# Weighted by G-Score
weights = [p.get_metrics().get_success_rate() for p in providers]
provider = random.choices(providers, weights=weights)[0]
```

---

## Support

- **Documentation:** [README.md](README.md)
- **Status:** [STATUS.md](STATUS.md)
- **Issues:** [GitHub Issues](https://github.com/yourusername/GP4U/issues)

---

**Built with ❤️ by the GP4U Team**
