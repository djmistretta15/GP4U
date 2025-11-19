# Mist GPU Lease Ledger MVP

> Investor-ready MVP for GPU lease tracking with blockchain provenance

A complete FastAPI + PostgreSQL + Next.js (React) application for tracking GPU leases with blockchain-anchored provenance events.

## ✨ Features

### Core Functionality
- ✅ User authentication (login/register)
- ✅ Organization management
- ✅ GPU registration and tracking
- ✅ GPU status management (available, leased, maintenance)
- ✅ Provenance event timeline
- ✅ Blockchain anchor stub (SHA256 hashing)
- ✅ Clean dashboard UI with Tailwind CSS

### Tech Stack
- **Backend**: FastAPI, PostgreSQL, SQLAlchemy, Alembic
- **Frontend**: React 18, Vite, Tailwind CSS, React Router
- **Infrastructure**: Docker, Docker Compose

## 🚀 Quick Start (15 Minutes)

### Prerequisites
- Docker & Docker Compose installed
- Git

### Option 1: Docker (Recommended - Fastest)

```bash
# Clone the repository
git clone https://github.com/djmistretta15/GP4U.git
cd GP4U

# Start all services
docker-compose up -d

# Wait for services to be ready (~30 seconds)
# Access the application:
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/api/docs
```

### Option 2: Local Development

#### Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start PostgreSQL and Redis (using Docker)
docker-compose up -d db redis

# Run migrations
alembic upgrade head

# Start FastAPI server
uvicorn app.main:app --reload --port 8000
```

#### Frontend Setup
```bash
# In a new terminal, from project root
npm install

# Start development server
npm run dev

# Access at http://localhost:3000
```

## 📚 API Endpoints

### Authentication
```bash
POST /api/auth/signup
POST /api/auth/login
```

### GPUs
```bash
GET  /api/gpus/              # List all GPUs
POST /api/gpus/              # Register new GPU
GET  /api/gpus/{id}          # Get GPU details
PATCH /api/gpus/{id}         # Update GPU status
GET  /api/gpus/{id}/provenance  # Get provenance timeline
POST /api/gpus/{id}/events   # Add provenance event
```

### Blockchain Anchors
```bash
POST /api/anchors/hash       # Create SHA256 hash of events
```

## 💻 Usage Examples

### Register a GPU
```bash
curl -X POST "http://localhost:8000/api/gpus/?model=RTX%204090&vram_gb=24"
```

### Update GPU Status
```bash
curl -X PATCH "http://localhost:8000/api/gpus/{gpu_id}" \
  -H "Content-Type: application/json" \
  -d '{"status": "leased"}'
```

### Get Provenance Timeline
```bash
curl "http://localhost:8000/api/gpus/{gpu_id}/provenance"
```

### Create Blockchain Anchor
```bash
curl -X POST "http://localhost:8000/api/anchors/hash" \
  -H "Content-Type: application/json" \
  -d '{"event_ids": ["event-id-1", "event-id-2"]}'
```

## 🎯 Frontend Features

### Dashboard (`/dashboard/gpus`)
- View all registered GPUs
- See status at a glance (available, leased, maintenance)
- Quick stats overview
- Register new GPUs with simple form

### GPU Detail Page (`/dashboard/gpus/{id}`)
- Complete GPU information
- Status update buttons
- Full provenance timeline with:
  - Event type icons
  - Timestamps
  - JSON payload details
  - Event IDs for blockchain anchoring

## 🗄️ Database Schema

### Models
- **User**: id, email, hashed_password, organization_id
- **Organization**: id, name, created_at
- **GPU**: id, model, vram_gb, status, organization_id, created_at
- **ProvenanceEvent**: id, gpu_id, event_type, payload_json, created_at

### Event Types
- `registered` - GPU first registered
- `status_changed` - Status updated
- `leased` - GPU leased to customer
- `returned` - GPU returned
- `maintenance_start` - Entered maintenance
- `maintenance_end` - Maintenance completed

## 🔒 Security

- JWT-based authentication
- Password hashing with bcrypt
- CORS protection
- SQL injection prevention (SQLAlchemy ORM)
- Input validation (Pydantic)

## 📊 Monitoring

Access API documentation at:
- Swagger UI: `http://localhost:8000/api/docs`
- ReDoc: `http://localhost:8000/api/redoc`

## 🧪 Testing

```bash
cd backend
pytest
```

## 📝 Environment Variables

Create `.env` file in backend directory:

```env
DATABASE_URL=postgresql+asyncpg://gp4u:password@localhost:5432/gp4u
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-change-this
DEBUG=true
```

## 🎨 UI Screenshots

The MVP features a clean, professional Tailwind CSS design:
- Simple navigation
- Responsive tables
- Status badges with color coding
- Timeline visualization for provenance
- Modal forms for data entry

## 🚢 Deployment

For production deployment:

1. Update environment variables
2. Set `DEBUG=false`
3. Configure proper SECRET_KEY
4. Use production database
5. Enable HTTPS
6. Set up proper CORS origins

## 📄 License

MIT

## 👥 Contributing

This is an MVP demonstration. For production use, consider:
- Real blockchain integration (replace SHA256 stub)
- Advanced authentication (OAuth, 2FA)
- Rate limiting
- Monitoring and logging
- Backup strategies
- Load balancing

---

**Built for investors** - Demo-ready in 15 minutes! 🚀
