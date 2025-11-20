# Log Schema Documentation

## Overview

This document defines the structured logging schema for both GP4U and Lease Ledger MVPs. All logs follow a consistent JSON structure for easy parsing and analysis.

## Standard Log Format

```json
{
  "timestamp": "2025-11-20T00:00:00.000Z",
  "level": "INFO|WARN|ERROR|DEBUG",
  "component": "arbitrage|gpu|auth|reservation|provenance|blockchain",
  "action": "search|book|sync|calculate|register|update",
  "user_id": "uuid-or-null",
  "session_id": "uuid",
  "duration_ms": 123,
  "status": "success|failure|partial",
  "details": {
    "custom": "fields"
  },
  "error": "error message if status=failure"
}
```

---

## GP4U MVP - Log Events

### 1. User Authentication

**Event:** `auth.login`
```json
{
  "timestamp": "2025-11-20T00:00:00.000Z",
  "level": "INFO",
  "component": "auth",
  "action": "login",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "session_id": "660e8400-e29b-41d4-a716-446655440001",
  "duration_ms": 45,
  "status": "success",
  "details": {
    "email": "user@example.com",
    "ip_address": "192.168.1.1"
  }
}
```

### 2. GPU Search

**Event:** `gpu.search`
```json
{
  "timestamp": "2025-11-20T00:00:00.000Z",
  "level": "INFO",
  "component": "gpu",
  "action": "search",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "session_id": "660e8400-e29b-41d4-a716-446655440001",
  "duration_ms": 1250,
  "status": "success",
  "details": {
    "query": {
      "model": "RTX 4090",
      "min_vram": 24
    },
    "results_count": 42,
    "providers_searched": ["vastai", "ionet", "akash", "render"],
    "cache_hit": false
  }
}
```

### 3. Arbitrage Calculation

**Event:** `arbitrage.calculate`
```json
{
  "timestamp": "2025-11-20T00:00:00.000Z",
  "level": "INFO",
  "component": "arbitrage",
  "action": "calculate",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "session_id": "660e8400-e29b-41d4-a716-446655440001",
  "duration_ms": 234,
  "status": "success",
  "details": {
    "gpu_model": "RTX 4090",
    "opportunities_found": 5,
    "best_spread_pct": 28.5,
    "cheapest_provider": "akash",
    "cheapest_price": 2.45,
    "expensive_provider": "vastai",
    "expensive_price": 3.15,
    "potential_savings_24h": 16.80
  }
}
```

### 4. GPU Reservation

**Event:** `reservation.create`
```json
{
  "timestamp": "2025-11-20T00:00:00.000Z",
  "level": "INFO",
  "component": "reservation",
  "action": "create",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "session_id": "660e8400-e29b-41d4-a716-446655440001",
  "duration_ms": 567,
  "status": "success",
  "details": {
    "reservation_id": "770e8400-e29b-41d4-a716-446655440002",
    "gpu_id": "880e8400-e29b-41d4-a716-446655440003",
    "provider": "akash",
    "model": "RTX 4090",
    "start_time": "2025-11-20T10:00:00Z",
    "end_time": "2025-11-20T18:00:00Z",
    "hours": 8,
    "price_per_hour": 2.45,
    "total_cost": 19.60,
    "savings_vs_market": 28.5
  }
}
```

### 5. Provider Sync

**Event:** `provider.sync`
```json
{
  "timestamp": "2025-11-20T00:00:00.000Z",
  "level": "INFO",
  "component": "provider",
  "action": "sync",
  "user_id": null,
  "session_id": "system",
  "duration_ms": 4523,
  "status": "partial",
  "details": {
    "providers_synced": {
      "vastai": {
        "status": "success",
        "gpus_fetched": 145,
        "new": 12,
        "updated": 28,
        "duration_ms": 1200
      },
      "akash": {
        "status": "success",
        "gpus_fetched": 89,
        "new": 5,
        "updated": 15,
        "duration_ms": 980
      },
      "ionet": {
        "status": "failure",
        "error": "API timeout after 10s"
      },
      "render": {
        "status": "success",
        "gpus_fetched": 234,
        "new": 45,
        "updated": 67,
        "duration_ms": 2343
      }
    },
    "total_gpus": 468,
    "failed_providers": ["ionet"]
  }
}
```

### 6. Wallet Transaction

**Event:** `wallet.transaction`
```json
{
  "timestamp": "2025-11-20T00:00:00.000Z",
  "level": "INFO",
  "component": "wallet",
  "action": "deposit",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "session_id": "660e8400-e29b-41d4-a716-446655440001",
  "duration_ms": 3456,
  "status": "success",
  "details": {
    "transaction_id": "990e8400-e29b-41d4-a716-446655440004",
    "type": "deposit",
    "amount_usdc": 100.00,
    "blockchain": "polygon",
    "tx_hash": "0x1234567890abcdef",
    "balance_before": 50.00,
    "balance_after": 150.00
  }
}
```

---

## Lease Ledger MVP - Log Events

### 1. GPU Registration

**Event:** `ledger.gpu.register`
```json
{
  "timestamp": "2025-11-20T00:00:00.000Z",
  "level": "INFO",
  "component": "provenance",
  "action": "register",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "session_id": "660e8400-e29b-41d4-a716-446655440001",
  "duration_ms": 234,
  "status": "success",
  "details": {
    "gpu_id": "aa0e8400-e29b-41d4-a716-446655440005",
    "model": "RTX 4090",
    "vram_gb": 24,
    "organization_id": "bb0e8400-e29b-41d4-a716-446655440006",
    "marketplace_enabled": true,
    "price_per_hour": 2.50,
    "location": "US-East",
    "provider": "lease-ledger",
    "event_id": "cc0e8400-e29b-41d4-a716-446655440007"
  }
}
```

### 2. Status Update

**Event:** `ledger.gpu.status_update`
```json
{
  "timestamp": "2025-11-20T00:00:00.000Z",
  "level": "INFO",
  "component": "provenance",
  "action": "update",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "session_id": "660e8400-e29b-41d4-a716-446655440001",
  "duration_ms": 156,
  "status": "success",
  "details": {
    "gpu_id": "aa0e8400-e29b-41d4-a716-446655440005",
    "old_status": "available",
    "new_status": "leased",
    "event_type": "status_changed",
    "event_id": "dd0e8400-e29b-41d4-a716-446655440008",
    "payload": {
      "old_status": "available",
      "new_status": "leased"
    }
  }
}
```

### 3. Provenance Query

**Event:** `ledger.provenance.query`
```json
{
  "timestamp": "2025-11-20T00:00:00.000Z",
  "level": "INFO",
  "component": "provenance",
  "action": "query",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "session_id": "660e8400-e29b-41d4-a716-446655440001",
  "duration_ms": 45,
  "status": "success",
  "details": {
    "gpu_id": "aa0e8400-e29b-41d4-a716-446655440005",
    "events_returned": 12,
    "date_range": {
      "start": "2025-11-01T00:00:00Z",
      "end": "2025-11-20T00:00:00Z"
    }
  }
}
```

### 4. Blockchain Anchor

**Event:** `ledger.blockchain.hash`
```json
{
  "timestamp": "2025-11-20T00:00:00.000Z",
  "level": "INFO",
  "component": "blockchain",
  "action": "hash",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "session_id": "660e8400-e29b-41d4-a716-446655440001",
  "duration_ms": 23,
  "status": "success",
  "details": {
    "event_ids": [
      "cc0e8400-e29b-41d4-a716-446655440007",
      "dd0e8400-e29b-41d4-a716-446655440008"
    ],
    "event_count": 2,
    "hash_algorithm": "SHA256",
    "hash": "1dc5fddf668296cea12a325397de1c0427868d9189a848f978d192382820fc73",
    "payload_size_bytes": 456
  }
}
```

---

## Error Logging

### Format
```json
{
  "timestamp": "2025-11-20T00:00:00.000Z",
  "level": "ERROR",
  "component": "arbitrage",
  "action": "calculate",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "session_id": "660e8400-e29b-41d4-a716-446655440001",
  "duration_ms": 10234,
  "status": "failure",
  "error": "Provider timeout: vastai did not respond within 10s",
  "details": {
    "provider": "vastai",
    "timeout_ms": 10000,
    "retry_attempt": 3,
    "circuit_breaker": "open"
  },
  "stack_trace": "..." 
}
```

---

## Performance Metrics

### Logged for Every Request
- `duration_ms`: Total request time
- `db_query_ms`: Database query time
- `cache_hit`: Boolean for cache hits
- `provider_latency_ms`: Per-provider response time

### Aggregated Metrics (Per Minute)
- Request count by component
- Average duration by action
- Error rate by component
- Cache hit rate

---

## Log Retention

- **INFO logs:** 30 days
- **WARN logs:** 90 days
- **ERROR logs:** 1 year
- **DEBUG logs:** 7 days (disabled in production)

---

## Log Analysis Queries

### Find Slow Requests
```sql
SELECT * FROM logs 
WHERE duration_ms > 2000 
ORDER BY duration_ms DESC 
LIMIT 100;
```

### Calculate Success Rate
```sql
SELECT 
  component,
  action,
  COUNT(*) as total,
  SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successes,
  SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END)::float / COUNT(*) as success_rate
FROM logs
WHERE timestamp > NOW() - INTERVAL '1 day'
GROUP BY component, action;
```

### Provider Health
```sql
SELECT 
  details->>'provider' as provider,
  COUNT(*) as requests,
  AVG((details->>'duration_ms')::int) as avg_latency_ms,
  SUM(CASE WHEN status = 'failure' THEN 1 ELSE 0 END) as failures
FROM logs
WHERE component = 'provider'
GROUP BY provider;
```

---

## Implementation

Logs are written using Python's `structlog` library with JSON formatting:

```python
import structlog

logger = structlog.get_logger()

logger.info(
    "gpu.search",
    component="gpu",
    action="search",
    user_id=str(user.id),
    duration_ms=duration,
    status="success",
    details={
        "query": query_params,
        "results_count": len(results)
    }
)
```

All logs are written to:
- `stdout` (captured by Docker)
- `logs/app.log` (file rotation daily)
- Optional: External logging service (not implemented in MVP)
