# System Architecture

## High-Level Overview

GP4U is a decentralized GPU brokerage platform with two integrated MVPs:

1. **GP4U Core** - Multi-provider GPU marketplace with arbitrage detection
2. **Lease Ledger** - Blockchain-anchored provenance tracking for GPU leases

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (React)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Marketplace  │  │ GPU Ledger   │  │    Wallet    │      │
│  │  Component   │  │  Component   │  │  Component   │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                  │                  │              │
└─────────┼──────────────────┼──────────────────┼──────────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│                    API Layer (FastAPI)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Arbitrage    │  │ Provenance   │  │    Auth      │      │
│  │   Router     │  │   Router     │  │   Router     │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
└─────────┼──────────────────┼──────────────────┼──────────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│                   Service Layer                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Arbitrage   │  │  Provenance  │  │    Wallet    │      │
│  │   Engine     │  │   Tracker    │  │   Service    │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
└─────────┼──────────────────┼──────────────────┼──────────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│                    Data Layer                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  PostgreSQL  │  │     Redis    │  │  Blockchain  │      │
│  │  (Primary)   │  │   (Cache)    │  │   (Stub)     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
          ▲
          │
┌─────────┴─────────────────────────────────────────────────┐
│               External Providers                           │
│  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐        │
│  │Vastai│  │io.net│  │Akash │  │Render│  │Ledger│        │
│  └──────┘  └──────┘  └──────┘  └──────┘  └──────┘        │
└────────────────────────────────────────────────────────────┘
```

---

## Component Breakdown

### Frontend Architecture

**Technology:** React 18, Vite, Tailwind CSS

**Structure:**
```
src/
├── components/          # Reusable UI components
│   ├── GPUManagement.jsx
│   ├── SmartGPUFinder.jsx
│   ├── GPUComparison.jsx
│   └── WalletManager.jsx
├── pages/              # Page-level components
│   ├── Home.jsx
│   ├── Dashboard.jsx
│   ├── EnhancedMarketplace.jsx
│   └── Settings.jsx
├── context/            # React Context providers
│   ├── AuthContext.jsx
│   ├── ThemeContext.jsx
│   └── Web3Context.jsx
└── services/           # API client layer
    └── api.js
```

**Key Features:**
- Single-page app with React Router
- Dark/light theme support
- Real-time data refresh (30s intervals)
- Optimistic UI updates
- Error boundary for resilience

---

### Backend Architecture

**Technology:** FastAPI, Python 3.12

**Structure:**
```
backend/app/
├── api/                # API route handlers
│   ├── auth.py
│   ├── gpus.py
│   ├── arbitrage.py
│   ├── reservations.py
│   └── anchors.py
├── services/           # Business logic
│   ├── arbitrage_engine.py
│   ├── provider_aggregator.py
│   └── reservation_service.py
├── models.py           # SQLAlchemy ORM models
├── schemas.py          # Pydantic schemas
├── core/               # Core utilities
│   ├── config.py
│   ├── database.py
│   └── security.py
└── providers/          # External provider integrations
    ├── vastai_provider.py
    ├── ionet_provider.py
    ├── akash_provider.py
    └── render_provider.py
```

---

## Data Flow

### GP4U Arbitrage Flow

```
1. User searches for "RTX 4090"
   ↓
2. Frontend → API: GET /api/gpus/search?model=RTX+4090
   ↓
3. API → Service: arbitrage_engine.find_opportunities()
   ↓
4. Service queries PostgreSQL (cached GPU data)
   ↓
5. Service calculates price spreads
   ↓
6. Service returns sorted opportunities
   ↓
7. API → Frontend: JSON response with arbitrage data
   ↓
8. Frontend renders comparison table
```

### Lease Ledger Provenance Flow

```
1. Operator registers GPU with price
   ↓
2. Frontend → API: POST /api/gpus/?model=RTX+4090&price=2.50
   ↓
3. API creates GPU record in PostgreSQL
   ↓
4. API creates ProvenanceEvent ("registered")
   ↓
5. API returns GPU object
   ↓
6. Frontend confirms registration
   ↓
[Later: Status Update]
7. Frontend → API: PATCH /api/gpus/{id} {"status": "leased"}
   ↓
8. API updates GPU status
   ↓
9. API creates ProvenanceEvent ("status_changed")
   ↓
10. API returns updated GPU
```

### Blockchain Anchor Flow

```
1. User requests anchor for events
   ↓
2. Frontend → API: POST /api/anchors/hash {"event_ids": [...]}
   ↓
3. API fetches events from PostgreSQL
   ↓
4. API concatenates event payloads
   ↓
5. API calculates SHA256 hash
   ↓
6. API returns hash + metadata
   ↓
7. Frontend displays hash for verification
```

---

## Database Schema

### Core Tables (GP4U)

**users**
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    organization_id UUID REFERENCES organizations(id),
    created_at TIMESTAMP DEFAULT NOW()
);
```

**gpus**
```sql
CREATE TABLE gpus (
    id UUID PRIMARY KEY,
    provider VARCHAR(50) NOT NULL,
    external_id VARCHAR(255),
    model VARCHAR(100) NOT NULL,
    vram_gb INTEGER NOT NULL,
    organization_id UUID REFERENCES organizations(id),
    status gpustatus DEFAULT 'available',
    price_per_hour DECIMAL(10, 2),
    location VARCHAR(255),
    available BOOLEAN DEFAULT true,
    g_score DECIMAL(5, 2),
    uptime_percent DECIMAL(5, 2),
    benchmark_score INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    last_synced TIMESTAMP DEFAULT NOW(),
    INDEX idx_provider (provider),
    INDEX idx_available (available),
    INDEX idx_model (model)
);
```

**reservations**
```sql
CREATE TABLE reservations (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id) NOT NULL,
    gpu_id UUID REFERENCES gpus(id) NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    price_per_hour DECIMAL(10, 2) NOT NULL,
    total_cost DECIMAL(10, 2) NOT NULL,
    status reservationstatus DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Lease Ledger Tables

**organizations**
```sql
CREATE TABLE organizations (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**provenance_events**
```sql
CREATE TABLE provenance_events (
    id UUID PRIMARY KEY,
    gpu_id UUID REFERENCES gpus(id) NOT NULL,
    event_type provenanceeventtype NOT NULL,
    payload_json TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_gpu_id (gpu_id),
    INDEX idx_created_at (created_at)
);
```

---

## External Integrations

### Provider APIs

**Vast.ai**
- Base URL: `https://console.vast.ai/api/v0/`
- Auth: API key
- Rate limit: 100 req/min
- Sync interval: 60 seconds

**io.net**
- Base URL: `https://api.io.net/v1/`
- Auth: API key
- Rate limit: 50 req/min
- Sync interval: 60 seconds

**Akash**
- Base URL: `https://api.akash.network/`
- Auth: None (public)
- Rate limit: 60 req/min
- Sync interval: 60 seconds

**Render**
- Base URL: `https://api.render.com/v1/`
- Auth: API key
- Rate limit: Unlimited (MVP)
- Sync interval: 60 seconds

### Blockchain (Stub)

**Current:** SHA256 hashing only
**Future:** Ethereum/Polygon smart contracts

---

## Caching Strategy

**Redis Cache:**
- Arbitrage opportunities: 30 second TTL
- GPU search results: 60 second TTL
- Provider health status: 5 minute TTL

**PostgreSQL:**
- GPU data synced every 30 seconds from providers
- Provenance events: Never cached (always fresh)

---

## Security Architecture

**Authentication:**
- JWT tokens with 30-minute expiration
- Bcrypt password hashing (cost factor 12)
- Refresh tokens not implemented (MVP)

**Authorization:**
- Organization-level isolation
- Users see only their own data
- Admins can view organization data

**Data Protection:**
- HTTPS only (production)
- No hard-coded secrets
- Environment variables for config
- SQL injection prevention (ORM)

---

## Scalability Considerations

**Current MVP Limits:**
- 100 concurrent users
- 1,000 GPUs in database
- 50 searches/second
- Single-region deployment

**Scaling Plan:**
- Horizontal scaling: Add more API containers
- Database: Read replicas for queries
- Cache: Redis cluster
- CDN: Static assets

---

## Deployment Architecture

**Docker Compose Stack:**
```yaml
services:
  - db (PostgreSQL)
  - redis (Redis)
  - api (FastAPI backend)
  - web (React frontend)
```

**Networking:**
- Internal network for db/redis
- External network for api/web
- CORS for frontend-backend communication

---

## Monitoring & Observability

**Logging:**
- Structured JSON logs
- Log aggregation: Stdout → Docker
- Retention: 30 days

**Metrics:**
- Request count
- Response time
- Error rate
- Cache hit rate

**Health Checks:**
- `/health` endpoint
- Database connectivity
- Redis connectivity
- Provider availability

---

## Future Architecture Enhancements

1. **Microservices:** Split arbitrage engine into separate service
2. **Event Sourcing:** Use event log for all state changes
3. **CQRS:** Separate read/write models
4. **GraphQL:** Alternative to REST API
5. **WebSockets:** Real-time price updates
6. **Kubernetes:** Container orchestration
7. **Service Mesh:** Istio for inter-service communication
8. **Distributed Tracing:** Jaeger or Zipkin
