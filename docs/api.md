# API Documentation

## Base URL

**Development:** `http://localhost:8000`
**Production:** `https://api.gp4u.com` (not yet deployed)

All endpoints are prefixed with `/api`

---

## Authentication

### Register User
```http
POST /api/auth/signup
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "username": "optional_username"
}
```

**Response:** `201 Created`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "username": "optional_username",
  "created_at": "2025-11-20T00:00:00Z"
}
```

### Login
```http
POST /api/auth/login
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com"
  }
}
```

**Authentication Header for Protected Routes:**
```
Authorization: Bearer {access_token}
```

---

## GPU Endpoints (GP4U)

### Search GPUs
```http
GET /api/gpus/search
```

**Query Parameters:**
- `model` (optional): GPU model filter (e.g., "RTX 4090")
- `min_vram` (optional): Minimum VRAM in GB
- `max_price` (optional): Maximum price per hour
- `provider` (optional): Filter by provider (vastai, ionet, akash, render)
- `location` (optional): Geographic location
- `available` (default: true): Only available GPUs

**Response:** `200 OK`
```json
[
  {
    "id": "880e8400-e29b-41d4-a716-446655440003",
    "model": "RTX 4090",
    "vram_gb": 24,
    "provider": "akash",
    "price_per_hour": 2.45,
    "location": "US-East",
    "available": true,
    "g_score": 0.92,
    "uptime_percent": 99.8
  }
]
```

### Get GPU Details
```http
GET /api/gpus/{gpu_id}
```

**Response:** `200 OK`
```json
{
  "id": "880e8400-e29b-41d4-a716-446655440003",
  "model": "RTX 4090",
  "vram_gb": 24,
  "provider": "akash",
  "price_per_hour": 2.45,
  "location": "US-East",
  "available": true,
  "g_score": 0.92,
  "uptime_percent": 99.8,
  "benchmark_score": 8500,
  "power_consumption": 450,
  "last_synced": "2025-11-20T00:00:00Z"
}
```

---

## Arbitrage Endpoints

### Get Arbitrage Opportunities
```http
GET /api/arbitrage/opportunities
```

**Query Parameters:**
- `min_spread` (optional): Minimum spread percentage (default: 15)
- `gpu_model` (optional): Filter by GPU model

**Response:** `200 OK`
```json
[
  {
    "gpu_model": "RTX 4090",
    "cheapest_provider": "akash",
    "cheapest_price": 2.45,
    "expensive_provider": "vastai",
    "expensive_price": 3.15,
    "spread_pct": 28.5,
    "potential_savings_24h": 16.80,
    "gpu_count": 5
  }
]
```

### Get Best Deal
```http
GET /api/arbitrage/best-deal/{gpu_model}
```

**Query Parameters:**
- `min_vram` (optional): Minimum VRAM requirement

**Response:** `200 OK`
```json
{
  "id": "880e8400-e29b-41d4-a716-446655440003",
  "provider": "akash",
  "model": "RTX 4090",
  "vram_gb": 24,
  "price_per_hour": 2.45,
  "location": "US-East",
  "uptime_percent": 99.8,
  "g_score": 0.92
}
```

### Compare Providers
```http
GET /api/arbitrage/compare/{gpu_model}
```

**Response:** `200 OK`
```json
{
  "gpu_model": "RTX 4090",
  "providers": [
    {
      "name": "akash",
      "count": 12,
      "avg_price": 2.50,
      "min_price": 2.30,
      "max_price": 2.70
    },
    {
      "name": "vastai",
      "count": 45,
      "avg_price": 3.15,
      "min_price": 2.90,
      "max_price": 3.50
    }
  ]
}
```

---

## Reservation Endpoints

### Create Reservation
```http
POST /api/reservations/
```

**Request Body:**
```json
{
  "gpu_id": "880e8400-e29b-41d4-a716-446655440003",
  "start_time": "2025-11-20T10:00:00Z",
  "end_time": "2025-11-20T18:00:00Z"
}
```

**Response:** `201 Created`
```json
{
  "id": "770e8400-e29b-41d4-a716-446655440002",
  "gpu_id": "880e8400-e29b-41d4-a716-446655440003",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "start_time": "2025-11-20T10:00:00Z",
  "end_time": "2025-11-20T18:00:00Z",
  "hours": 8,
  "price_per_hour": 2.45,
  "total_cost": 19.60,
  "status": "pending",
  "created_at": "2025-11-20T00:00:00Z"
}
```

### Get My Reservations
```http
GET /api/reservations/my-bookings
```

**Query Parameters:**
- `status` (optional): Filter by status (pending, active, completed, cancelled)
- `upcoming_only` (optional): Boolean, only future reservations

**Response:** `200 OK`
```json
[
  {
    "id": "770e8400-e29b-41d4-a716-446655440002",
    "gpu": {
      "id": "880e8400-e29b-41d4-a716-446655440003",
      "model": "RTX 4090",
      "provider": "akash"
    },
    "start_time": "2025-11-20T10:00:00Z",
    "end_time": "2025-11-20T18:00:00Z",
    "total_cost": 19.60,
    "status": "active"
  }
]
```

---

## Lease Ledger Endpoints

### Register GPU (Lease Ledger)
```http
POST /api/gpus/
```

**Query Parameters:**
- `model` (required): GPU model name
- `vram_gb` (required): VRAM in GB
- `organization_id` (optional): Organization UUID
- `price_per_hour` (optional): Enables marketplace
- `location` (optional): Enables arbitrage

**Response:** `201 Created`
```json
{
  "id": "aa0e8400-e29b-41d4-a716-446655440005",
  "model": "RTX 4090",
  "vram_gb": 24,
  "provider": "lease-ledger",
  "status": "available",
  "organization_id": null,
  "price_per_hour": 2.50,
  "location": "US-East",
  "created_at": "2025-11-20T00:00:00Z",
  "g_score": 0.85,
  "uptime_percent": 99.9
}
```

### Update GPU Status
```http
PATCH /api/gpus/{gpu_id}
```

**Request Body:**
```json
{
  "status": "leased"
}
```

**Valid statuses:** `available`, `leased`, `maintenance`

**Response:** `200 OK`
```json
{
  "id": "aa0e8400-e29b-41d4-a716-446655440005",
  "model": "RTX 4090",
  "status": "leased",
  "available": false
}
```

### Get Provenance Timeline
```http
GET /api/gpus/{gpu_id}/provenance
```

**Response:** `200 OK`
```json
[
  {
    "id": "cc0e8400-e29b-41d4-a716-446655440007",
    "gpu_id": "aa0e8400-e29b-41d4-a716-446655440005",
    "event_type": "registered",
    "payload_json": "{\"model\": \"RTX 4090\", \"vram_gb\": 24}",
    "created_at": "2025-11-20T00:00:00Z"
  },
  {
    "id": "dd0e8400-e29b-41d4-a716-446655440008",
    "gpu_id": "aa0e8400-e29b-41d4-a716-446655440005",
    "event_type": "status_changed",
    "payload_json": "{\"old_status\": \"available\", \"new_status\": \"leased\"}",
    "created_at": "2025-11-20T00:05:00Z"
  }
]
```

### Create Blockchain Anchor
```http
POST /api/anchors/hash
```

**Request Body:**
```json
{
  "event_ids": [
    "cc0e8400-e29b-41d4-a716-446655440007",
    "dd0e8400-e29b-41d4-a716-446655440008"
  ]
}
```

**Response:** `200 OK`
```json
{
  "hash": "1dc5fddf668296cea12a325397de1c0427868d9189a848f978d192382820fc73",
  "event_count": 2,
  "timestamp": "2025-11-20T00:10:00Z"
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid status transition: maintenance → available not allowed"
}
```

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

### 404 Not Found
```json
{
  "detail": "GPU not found"
}
```

### 409 Conflict
```json
{
  "detail": "Time slot conflicts with existing reservation"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Database connection failed"
}
```

---

## Rate Limiting

**MVP:** No rate limiting implemented

**Recommended for Production:**
- 100 requests/minute per user
- 1000 requests/minute per IP
- 10 bookings/minute per user

---

## Webhook Support

**MVP:** Not implemented

**Planned:** Webhooks for reservation status changes

---

## API Versioning

Current version: `v1` (implicit)

Future versions will use URL prefix: `/api/v2/...`
