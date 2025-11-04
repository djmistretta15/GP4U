# 🚀 GP4U - The Kayak of GPUs

> **Decentralized GPU Brokerage Platform with Multi-Provider Arbitrage Detection**

GP4U is a full-stack web application that aggregates GPU offerings from multiple providers (Render, Akash, io.net, Vast.ai) and helps users find 15-40% savings through real-time arbitrage detection. Features time-block reservations and multi-GPU cluster orchestration with Dynamic Pooling Protocol (DPP).

[![Backend](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![Frontend](https://img.shields.io/badge/Frontend-React-61DAFB.svg)](https://reactjs.org/)
[![Database](https://img.shields.io/badge/Database-PostgreSQL-336791.svg)](https://www.postgresql.org/)

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
**Overall Completion: 90%**
- Backend: 85% (Production-ready)
- Frontend: 100% (Fully integrated)
- Testing: 50% (Core endpoints covered)

See [STATUS.md](STATUS.md) for detailed progress.

### **Code Statistics**
- **Backend**: ~9,500 lines (Python)
- **Frontend**: ~4,500 lines (React)
- **Tests**: ~800 lines
- **Total**: ~18,000 lines

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

### **Next**
- [ ] Phase 6: Web3 Integration (USDC blockchain)
- [ ] Phase 7: Real Provider API Integration
- [ ] Phase 8: Production Deployment

---

**Built with ❤️ by the GP4U Team**
