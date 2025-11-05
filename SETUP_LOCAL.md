# 🚀 Local Setup Guide - Running GP4U from GitHub

Complete guide to clone and run GP4U locally on your machine.

---

## Prerequisites

Before you begin, ensure you have the following installed:

- **Git** - [Download Git](https://git-scm.com/downloads)
- **Docker** & **Docker Compose** - [Download Docker](https://www.docker.com/products/docker-desktop/)
- **Node.js 18+** - [Download Node.js](https://nodejs.org/)
- **Python 3.11+** (optional, for local development without Docker)

---

## Quick Start (Docker - Recommended)

### 1. Clone the Repository

```bash
# Clone from GitHub
git clone https://github.com/djmistretta15/GP4U.git
cd GP4U
```

### 2. Configure Environment Variables

```bash
# Copy example environment file
cd backend
cp .env.example .env

# Edit .env with your settings (use nano, vim, or any text editor)
nano .env
```

**Minimum required settings:**
```bash
# Database
DATABASE_URL=postgresql+asyncpg://gp4u:password@db:5432/gp4u

# Redis
REDIS_URL=redis://redis:6379/0

# JWT Secret (change this!)
SECRET_KEY=your-super-secret-key-change-this-in-production-min-32-chars

# API Configuration
DEBUG=true
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

**Optional - Provider API Keys:**
```bash
# Add these if you have API keys (see PROVIDER_SETUP.md)
VASTAI_API_KEY=your_key_here
IONET_API_KEY=your_key_here
RENDER_API_KEY=your_key_here
```

### 3. Start the Application

```bash
# Return to project root
cd ..

# Start all services with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f
```

**Services will be available at:**
- 🌐 **Backend API:** http://localhost:8000
- 📘 **API Documentation:** http://localhost:8000/api/docs
- 💾 **PostgreSQL:** localhost:5432
- 🔴 **Redis:** localhost:6379

### 4. Initialize Database

```bash
# Run database migrations
docker-compose exec api alembic upgrade head

# Or if running locally:
cd backend
alembic upgrade head
```

### 5. Set Up Frontend

```bash
# Install frontend dependencies
npm install

# Copy frontend environment file
cp .env.example .env

# Start frontend development server
npm run dev
```

**Frontend will be available at:** http://localhost:5173

### 6. Create Your First User

Open your browser to http://localhost:5173 and:
1. Click **"Sign Up"**
2. Enter email and password
3. Login with your credentials
4. Explore the marketplace!

---

## Manual Setup (Without Docker)

### 1. Clone Repository

```bash
git clone https://github.com/djmistretta15/GP4U.git
cd GP4U
```

### 2. Set Up PostgreSQL Database

```bash
# Install PostgreSQL (if not already installed)
# macOS: brew install postgresql
# Ubuntu: sudo apt-get install postgresql
# Windows: Download from postgresql.org

# Create database
psql postgres
CREATE DATABASE gp4u;
CREATE USER gp4u WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE gp4u TO gp4u;
\q
```

### 3. Set Up Redis

```bash
# Install Redis (if not already installed)
# macOS: brew install redis
# Ubuntu: sudo apt-get install redis-server
# Windows: Download from redis.io

# Start Redis
redis-server
```

### 4. Set Up Backend

```bash
cd backend

# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your database settings

# Run migrations
alembic upgrade head

# Start FastAPI server
uvicorn app.main:app --reload --port 8000
```

### 5. Start Background Workers

```bash
# Terminal 2 - Celery Worker
cd backend
source venv/bin/activate
celery -A app.services.worker worker --loglevel=info

# Terminal 3 - Celery Beat (scheduler)
cd backend
source venv/bin/activate
celery -A app.services.worker beat --loglevel=info
```

### 6. Set Up Frontend

```bash
# Terminal 4 - Frontend
cd GP4U  # project root

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit .env: VITE_API_URL=http://localhost:8000

# Start development server
npm run dev
```

---

## Verifying Your Installation

### 1. Check Backend Health

```bash
curl http://localhost:8000/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "app": "GP4U",
  "version": "1.0.0"
}
```

### 2. Check API Documentation

Open http://localhost:8000/api/docs in your browser.

You should see the interactive Swagger UI with all 50+ endpoints.

### 3. Check Provider Health

```bash
curl http://localhost:8000/api/provider-health/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "providers": {
    "vastai": {"status": "HEALTHY", ...},
    "ionet": {"status": "HEALTHY", ...},
    "akash": {"status": "HEALTHY", ...},
    "render": {"status": "HEALTHY", ...}
  }
}
```

### 4. Test Authentication

```bash
# Sign up
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@gp4u.com",
    "password": "testpass123"
  }'

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@gp4u.com&password=testpass123"
```

### 5. Test GPU Search

```bash
# Get auth token from login response
TOKEN="your_token_here"

# Search GPUs
curl http://localhost:8000/api/gpus/search \
  -H "Authorization: Bearer $TOKEN"
```

---

## Environment Variables Reference

### Backend (.env)

```bash
# Database
DATABASE_URL=postgresql+asyncpg://gp4u:password@db:5432/gp4u
DATABASE_POOL_SIZE=20

# Redis
REDIS_URL=redis://redis:6379/0

# JWT Authentication
SECRET_KEY=your-secret-key-min-32-characters-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Configuration
API_V1_PREFIX=/api
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
DEBUG=true

# Provider API Keys (optional)
VASTAI_API_KEY=
VASTAI_ENABLED=true
IONET_API_KEY=
IONET_ENABLED=true
AKASH_ENABLED=true
RENDER_API_KEY=
RENDER_ENABLED=true

# Circuit Breaker
PROVIDER_CIRCUIT_BREAKER_THRESHOLD=5
PROVIDER_CIRCUIT_BREAKER_TIMEOUT=60

# Cache
PROVIDER_CACHE_ENABLED=true
PROVIDER_CACHE_TTL=30

# Celery
CELERY_BROKER_URL=redis://redis:6379/1
CELERY_RESULT_BACKEND=redis://redis:6379/2

# Web3 (optional - for blockchain integration)
WEB3_PROVIDER_URL=https://eth-mainnet.g.alchemy.com/v2/your-api-key
USDC_CONTRACT_ADDRESS=0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48
```

### Frontend (.env)

```bash
# Backend API URL
VITE_API_URL=http://localhost:8000

# Optional: Web3 Settings
VITE_ENABLE_WEB3=true
VITE_DEFAULT_CHAIN_ID=1  # Ethereum Mainnet
```

---

## Common Issues & Solutions

### Issue: "Database connection failed"

**Solution:**
```bash
# Check PostgreSQL is running
docker-compose ps  # with Docker
# OR
pg_isready  # local PostgreSQL

# Verify database exists
psql -U gp4u -d gp4u -c "SELECT version();"

# Check DATABASE_URL in .env is correct
```

### Issue: "Redis connection refused"

**Solution:**
```bash
# Check Redis is running
docker-compose ps  # with Docker
# OR
redis-cli ping  # should return "PONG"

# Start Redis if not running
redis-server  # local
# OR
docker-compose up -d redis  # Docker
```

### Issue: "Module not found" errors

**Solution:**
```bash
# Backend - reinstall dependencies
cd backend
pip install -r requirements.txt

# Frontend - reinstall dependencies
cd ..
npm install
```

### Issue: "Port already in use"

**Solution:**
```bash
# Find process using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill process or change port
uvicorn app.main:app --port 8001  # use different port
```

### Issue: "Alembic migration failed"

**Solution:**
```bash
# Drop and recreate database
psql postgres
DROP DATABASE gp4u;
CREATE DATABASE gp4u;
\q

# Run migrations again
cd backend
alembic upgrade head
```

### Issue: "CORS errors in browser"

**Solution:**
```bash
# Add your frontend URL to ALLOWED_ORIGINS in backend/.env
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# Restart backend
docker-compose restart api  # Docker
# OR
# Ctrl+C and restart uvicorn
```

---

## Development Workflow

### Making Changes

1. **Create a new branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**

3. **Run tests:**
   ```bash
   cd backend
   pytest
   ```

4. **Commit and push:**
   ```bash
   git add .
   git commit -m "feat: your feature description"
   git push origin feature/your-feature-name
   ```

### Hot Reload

Both backend and frontend support hot reload during development:

- **Backend:** Automatically reloads on file changes (uvicorn --reload)
- **Frontend:** Automatically reloads on file changes (Vite HMR)

### Viewing Logs

```bash
# Docker logs
docker-compose logs -f api      # Backend
docker-compose logs -f worker   # Celery worker
docker-compose logs -f beat     # Celery beat

# Local development
# Logs appear in terminal where services are running
```

---

## Running Tests

```bash
# Backend tests
cd backend
pytest                          # All tests
pytest -v                       # Verbose
pytest --cov=app tests/         # With coverage
pytest tests/test_auth.py       # Specific file

# Frontend tests (if configured)
npm test
```

See [TESTING.md](TESTING.md) for comprehensive testing guide.

---

## Production Deployment

For production deployment, see:
- **[DEPLOY.md](DEPLOY.md)** - Production deployment guide
- **[PROVIDER_SETUP.md](PROVIDER_SETUP.md)** - Provider configuration

**Production checklist:**
- ✅ Set strong SECRET_KEY (min 32 characters)
- ✅ Set DEBUG=false
- ✅ Use environment variables (not .env file)
- ✅ Set up SSL/TLS certificates
- ✅ Configure firewall rules
- ✅ Set up monitoring (Sentry, etc.)
- ✅ Configure backup strategy
- ✅ Set up CI/CD pipeline

---

## Getting Help

- **Documentation:** See [README.md](README.md)
- **API Docs:** http://localhost:8000/api/docs
- **Issues:** [GitHub Issues](https://github.com/djmistretta15/GP4U/issues)
- **Status:** See [STATUS.md](STATUS.md)

---

## Quick Command Reference

```bash
# Docker
docker-compose up -d              # Start all services
docker-compose down               # Stop all services
docker-compose logs -f            # View logs
docker-compose restart api        # Restart backend

# Backend
uvicorn app.main:app --reload     # Start FastAPI
alembic upgrade head              # Run migrations
pytest                            # Run tests

# Frontend
npm install                       # Install dependencies
npm run dev                       # Start dev server
npm run build                     # Build for production

# Database
psql -U gp4u -d gp4u             # Connect to database
alembic revision -m "message"     # Create migration

# Celery
celery -A app.services.worker worker --loglevel=info   # Start worker
celery -A app.services.worker beat --loglevel=info     # Start beat
```

---

## Project Structure

```
GP4U/
├── backend/
│   ├── app/
│   │   ├── api/           # API endpoints
│   │   ├── core/          # Core functionality (providers, circuit breakers)
│   │   ├── models.py      # Database models
│   │   ├── schemas.py     # Pydantic schemas
│   │   └── services/      # Business logic
│   ├── tests/             # Test suite
│   ├── alembic/           # Database migrations
│   └── requirements.txt   # Python dependencies
├── frontend/
│   └── src/               # React components
├── src/                   # Additional React components
├── docker-compose.yml     # Docker orchestration
├── README.md             # Project overview
├── STATUS.md             # Project status
├── PROVIDER_SETUP.md     # Provider configuration
├── TESTING.md            # Testing guide
└── SETUP_LOCAL.md        # This file
```

---

## Next Steps

1. ✅ **Clone and set up** the project locally
2. ✅ **Explore the API** at http://localhost:8000/api/docs
3. ✅ **Create test user** and explore features
4. ✅ **Read documentation:**
   - [README.md](README.md) - Project overview
   - [STATUS.md](STATUS.md) - Current status
   - [PROVIDER_SETUP.md](PROVIDER_SETUP.md) - Provider setup
   - [TESTING.md](TESTING.md) - Testing guide
5. ✅ **Configure providers** with API keys (optional)
6. ✅ **Start building!** 🚀

---

**Welcome to GP4U - The Kayak of GPUs! Happy coding! 🎉**
