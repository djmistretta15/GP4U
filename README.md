# 🚀 GP4U - The Kayak of GPUs

> **Decentralized GPU Brokerage Platform with Multi-Provider Arbitrage Detection**

GP4U is a full-stack web application that aggregates GPU offerings from multiple providers (Render, Akash, io.net, Vast.ai) and helps users find 15-40% savings through real-time arbitrage detection. Features time-block reservations and multi-GPU cluster orchestration with Dynamic Pooling Protocol (DPP).

[![Backend](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![Frontend](https://img.shields.io/badge/Frontend-React-61DAFB.svg)](https://reactjs.org/)
[![Database](https://img.shields.io/badge/Database-PostgreSQL-336791.svg)](https://www.postgresql.org/)

## 📚 Documentation

- **[README.md](README.md)** - Project overview and quick start
- **[STATUS.md](STATUS.md)** - Detailed project status and progress
- **[PROVIDER_SETUP.md](PROVIDER_SETUP.md)** - Provider configuration and monitoring guide
- **[TESTING.md](TESTING.md)** - Complete testing guide and best practices

---

## ✨ Features

### **For GPU Renters**
- 🔍 **Multi-Provider Search** - Browse GPUs from 4+ providers in one place
- 💰 **Arbitrage Detection** - Find 15-40% savings automatically
- 📅 **Time-Block Reservations** - Book GPUs by the hour with calendar view
- 🎯 **Cluster Mode** - Create multi-GPU clusters with DPP algorithm
- 💳 **USDC Wallet** - Deposit, withdraw, and track spending
- 🔗 **Web3 Integration** - Connect MetaMask for real blockchain transactions
- 📊 **Analytics** - Transaction history and spending insights
- 🌙 **Dark Mode** - Full theme support

### **For GPU Providers**
- 💵 **Earn Passive Income** - List your GPUs and earn USDC
- 🏆 **Fair Compensation** - Contribution-based earnings distribution
- 📈 **G-Score Ranking** - Performance × Reliability × Efficiency
- 🔄 **Auto-Earnings** - Distributed on cluster completion

### **Technical Features**
- 🔐 JWT Authentication with bcrypt password hashing
- ⛓️ Web3 wallet connectivity (MetaMask, WalletConnect)
- 💎 Real USDC blockchain transactions (Ethereum & Polygon)
- 🚀 Real-time data sync every 30 seconds
- ♻️ Background workers for automation
- 📱 Responsive design (mobile-first)
- 🔔 Toast notifications for user feedback
- 🛡️ Protected routes with auth guards

---

## 🛠️ Tech Stack

### **Backend**
- **FastAPI** - Modern async Python framework
- **PostgreSQL** - Production-grade database
- **Redis** - Caching and message broker
- **Celery + Beat** - Background task processing
- **SQLAlchemy** - Async ORM
- **Alembic** - Database migrations
- **Pytest** - API testing

### **Frontend**
- **React 18** - UI library
- **React Router** - Client-side routing
- **Axios** - HTTP client
- **Tailwind CSS** - Utility-first styling
- **Vite** - Build tool
- **Lucide React** - Icon library

### **Web3 Integration**
- **Ethers.js v6** - Ethereum library for blockchain interactions
- **MetaMask** - Web3 wallet connectivity
- **USDC (ERC-20)** - Stablecoin for payments
- **Multi-Chain Support** - Ethereum Mainnet & Polygon PoS
- **Smart Contract Integration** - Real blockchain transactions

### **DevOps**
- **Docker & Docker Compose** - Containerization

---

## 🚀 Quick Start

### Prerequisites
- **Docker** & **Docker Compose** (recommended)
- OR **Python 3.11+** & **Node.js 18+** & **PostgreSQL 15+**

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/GP4U.git
cd GP4U

# Start backend services
docker-compose up

# In a separate terminal, start frontend
npm install
npm run dev

# Access the application
# - Frontend: http://localhost:5173
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/api/v1/docs
```

### Option 2: Local Development

#### **Backend Setup**
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run database migrations
alembic upgrade head

# Start FastAPI server
uvicorn app.main:app --reload --port 8000

# In separate terminals, start workers:
celery -A app.services.worker worker --loglevel=info
celery -A app.services.worker beat --loglevel=info
```

#### **Frontend Setup**
```bash
# Install dependencies
npm install

# Set up environment variables
cp .env.example .env
# Edit .env with VITE_API_URL=http://localhost:8000

# Start development server
npm run dev

# Access at http://localhost:5173
```

---

## 🔗 Web3 Integration Setup

GP4U supports real blockchain transactions using MetaMask and USDC. Follow these steps to enable Web3 features:

### **1. Install MetaMask**
- Install [MetaMask browser extension](https://metamask.io/)
- Create a wallet or import an existing one
- Ensure you have some ETH or MATIC for gas fees

### **2. Supported Networks**
GP4U works on the following networks:

| Network | Chain ID | USDC Contract Address |
|---------|----------|-----------------------|
| **Ethereum Mainnet** | 1 | `0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48` |
| **Polygon PoS** | 137 | `0x3c499c542cef5e3811e1192ce70d8cc03d5c3359` |
| Sepolia Testnet | 11155111 | `0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238` |
| Mumbai Testnet | 80001 | `0x0FA8781a83E46826621b3BC094Ea2A0212e71B23` |

### **3. Get Test USDC (Testnets)**
For development and testing:
- **Sepolia**: Use [Circle Faucet](https://faucet.circle.com/) for test USDC
- **Mumbai**: Bridge test USDC from Sepolia using [Polygon Bridge](https://wallet.polygon.technology/bridge)

### **4. Connect Your Wallet**
1. Open GP4U application
2. Navigate to **Wallet** page
3. Click **"Connect Wallet"** button
4. Approve MetaMask connection request
5. Your blockchain balance will display automatically

### **5. Making Deposits**
Once connected:
1. Ensure you're on Ethereum or Polygon network
2. Make sure you have USDC in your wallet
3. Enter deposit amount
4. Click **"Deposit via Blockchain"**
5. Approve the transaction in MetaMask (2 transactions: approve + transfer)
6. Wait for blockchain confirmation (~15 seconds on Polygon, ~1 minute on Ethereum)
7. Your GP4U balance updates automatically

### **6. Making Withdrawals**
1. Enter withdrawal amount
2. Optionally specify destination address (defaults to connected wallet)
3. Click **"Withdraw Funds"**
4. Platform processes withdrawal and sends USDC to your address

### **Troubleshooting**
- **"Please install MetaMask"**: Install the browser extension and refresh
- **"Unsupported network"**: Switch to Ethereum or Polygon in MetaMask
- **"Insufficient USDC"**: Buy USDC on an exchange or use test faucets
- **"Transaction failed"**: Check you have enough ETH/MATIC for gas fees
- **Transaction stuck**: Increase gas price in MetaMask settings

### **Gas Fees**
- **Ethereum**: ~$5-20 per transaction (varies with network congestion)
- **Polygon**: ~$0.01-0.10 per transaction (recommended for frequent transactions)

### **Hybrid Mode**
GP4U works in hybrid mode:
- **With Web3 connected**: Real blockchain transactions
- **Without Web3**: Simulated transactions for testing/demo purposes

---

## 📚 API Documentation

### **Authentication**
```bash
# Sign up
POST /api/v1/auth/signup
{
  "email": "user@example.com",
  "password": "secure123"
}

# Login
POST /api/v1/auth/login
username=user@example.com&password=secure123

# Get profile
GET /api/v1/auth/me
Authorization: Bearer <token>
```

### **GPU Marketplace**
```bash
# Search GPUs
GET /api/v1/gpus/search?model=RTX&max_price=5.0

# Get arbitrage opportunities
GET /api/v1/arbitrage/opportunities?min_spread_pct=15
```

### **Reservations**
```bash
# Create reservation
POST /api/v1/reservations/
{
  "gpu_id": "uuid",
  "start_time": "2025-11-04T10:00:00Z",
  "end_time": "2025-11-04T18:00:00Z"
}

# Cancel (with refund)
DELETE /api/v1/reservations/{id}/cancel
```

### **Clusters**
```bash
# Create cluster with DPP
POST /api/v1/clusters/
{
  "job_name": "AI Training",
  "compute_intensity": 5000,
  "vram_gb": 24,
  "deadline_hours": 48
}
```

### **Wallet**
```bash
# Get balance
GET /api/v1/wallets/balance

# Deposit USDC
POST /api/v1/wallets/deposit
{
  "amount": "1000.00"
}
```

**Full API Docs:** http://localhost:8000/api/v1/docs

---

## 💻 Development

### **Project Status**
**Overall Completion: 95%**
- Backend: 95% (Production-ready)
- Frontend: 100% (Fully integrated)
- Web3: 80% (MetaMask + USDC transactions)
- Testing: 50% (Core endpoints covered)

See [STATUS.md](STATUS.md) for detailed progress.

### **Code Statistics**
- **Backend**: ~12,600 lines (Python)
- **Frontend**: ~5,500 lines (React)
- **Web3**: ~1,000 lines
- **Tests**: ~800 lines
- **Total**: ~23,400 lines

---

## 🏗️ Provider Architecture (Phase 7)

GP4U features an **enterprise-grade provider integration architecture** with production-level reliability patterns:

### **Core Patterns**

#### **1. Circuit Breaker Pattern**
Prevents cascading failures by tracking provider health:
- **CLOSED** (Normal) → **OPEN** (Too many failures) → **HALF_OPEN** (Testing recovery)
- Automatic failure detection (default: 5 failures)
- Recovery timeout with gradual testing (default: 60s)
- Per-provider isolation

```python
# Example: Circuit breaker automatically protects against failing providers
try:
    gpus = await provider.get_gpus()
except CircuitBreakerOpen as e:
    # Provider is temporarily disabled, retry after e.retry_after seconds
    pass
```

#### **2. Token Bucket Rate Limiting**
Respects API quotas and prevents service bans:
- Configurable rates per provider (50-150 requests/minute)
- Burst capacity support
- Thread-safe operations
- Wait time estimation

```python
# Rate limiter ensures we stay within provider API limits
await rate_limiter.acquire(tokens=1)  # Blocks if rate limit reached
```

#### **3. Exponential Backoff with Jitter**
Prevents thundering herd problem during retries:
- Exponential retry delays: 2s → 4s → 8s → 16s → 32s
- Random jitter to spread retry attempts
- Automatic retry on transient failures

#### **4. Adaptive Caching**
Dynamic TTL based on provider reliability:
- **Reliable providers** (90%+ success): 300s TTL
- **Moderate providers** (70-90% success): 45s TTL
- **Unreliable providers** (<70% success): 10s TTL
- Stale-while-revalidate pattern
- Redis-backed distributed cache

### **Provider Implementations**

GP4U integrates with 4 major GPU providers:

| Provider | GPUs | Focus | G-Score Formula |
|----------|------|-------|----------------|
| **Vast.ai** | 10,000+ | Deep Learning | Performance (40%) + Reliability (40%) + Efficiency (20%) |
| **io.net** | 327,000+ | AI/ML Clusters | Performance (50%) + Reliability (30%) + Efficiency (20%) |
| **Akash** | 5,000+ | Decentralized Cloud | Performance (30%) + Reliability (30%) + Efficiency (40%) |
| **Render** | 8,000+ | GPU Rendering | Performance (50%) + Reliability (30%) + Efficiency (20%) |

### **Health Monitoring**

10 dedicated endpoints for real-time monitoring:

```bash
# System-wide health
GET /api/v1/provider-health/health

# Provider-specific health
GET /api/v1/provider-health/providers/vastai/health

# Circuit breaker status
GET /api/v1/provider-health/circuit-breakers

# Rate limiter utilization
GET /api/v1/provider-health/rate-limiters

# Cache performance
GET /api/v1/provider-health/cache/stats

# Comprehensive metrics dashboard
GET /api/v1/provider-health/metrics/summary
```

### **Reliability Metrics**

Each provider tracks:
- **Success rate** (%)
- **Average response time** (ms)
- **Circuit breaker trips**
- **Rate limit hits**
- **Cache hit ratio**
- **Slow request count**
- **Uptime** (seconds)

### **Configuration**

Provider settings via environment variables:

```bash
# Vast.ai
VASTAI_API_KEY=your_key_here
VASTAI_RATE_LIMIT=100  # requests per minute
VASTAI_TIMEOUT=30      # seconds

# Circuit Breaker (global)
PROVIDER_CIRCUIT_BREAKER_THRESHOLD=5   # failures before opening
PROVIDER_CIRCUIT_BREAKER_TIMEOUT=60    # recovery timeout in seconds

# Cache (global)
PROVIDER_CACHE_TTL=30  # base TTL in seconds
```

See `backend/app/core/provider_config.py` for full configuration options.

---

## 🧪 Testing

```bash
cd backend

# Run all tests
pytest

# With coverage
pytest --cov=app tests/
```

---

## 🚀 Deployment

### **Production Build**

```bash
# Frontend
npm run build
# Output in /dist folder

# Backend
docker build -t gp4u-backend backend/
docker run -p 8000:8000 gp4u-backend
```

---

## 📝 License

This project is licensed under the MIT License.

---

## 🗺️ Roadmap

### **Completed**
- [x] Phase 1: Foundation & Database
- [x] Phase 2: Authentication & Core Backend
- [x] Phase 3: Reservations & Clusters
- [x] Phase 4: Financial System
- [x] Phase 5: Frontend Integration
- [x] Phase 6: Web3 Integration (80% - MetaMask & USDC)
- [x] Phase 7: Real Provider API Integration (100% - Enterprise Architecture)

### **Next**
- [ ] Phase 8: Production Deployment (CI/CD, hosting, monitoring)

---

**Built with ❤️ by the GP4U Team**
