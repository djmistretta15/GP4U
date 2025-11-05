# GP4U Backend - FastAPI

Production-ready FastAPI backend for the GP4U GPU brokerage platform.

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (for local development)

### Start with Docker
```bash
# Start all services
docker-compose up

# API will be available at http://localhost:8000
# API docs: http://localhost:8000/api/docs
```

### Local Development Setup
```bash
# Install dependencies
cd backend
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Run database migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload

# API runs on http://localhost:8000
```

## 📁 Project Structure

```
backend/
├── app/
│   ├── api/              # API route handlers
│   ├── core/             # Core configuration
│   ├── models.py         # SQLAlchemy models
│   ├── schemas.py        # Pydantic schemas
│   ├── providers/        # GPU provider integrations
│   └── services/         # Business logic
├── database/
│   └── migrations/       # Alembic migrations
├── requirements.txt
├── Dockerfile
└── alembic.ini
```

## 🔧 Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/
```

## 📚 API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc
