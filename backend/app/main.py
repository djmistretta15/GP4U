"""
GP4U FastAPI Application
Main entry point for the API server
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import init_db, close_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan events
    Handles startup and shutdown tasks
    """
    # Startup
    print("🚀 GP4U API Starting...")
    print(f"📋 Version: {settings.VERSION}")
    print(f"🔧 Debug Mode: {settings.DEBUG}")
    await init_db()
    print("✅ Database initialized")

    yield

    # Shutdown
    print("🛑 Shutting down GP4U API...")
    await close_db()
    print("✅ Database connections closed")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="The Kayak of GPUs - Decentralized GPU Brokerage Platform",
    lifespan=lifespan,
    docs_url=f"{settings.API_V1_PREFIX}/docs",
    redoc_url=f"{settings.API_V1_PREFIX}/redoc",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.VERSION
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to GP4U - The Kayak of GPUs",
        "version": settings.VERSION,
        "docs": f"{settings.API_V1_PREFIX}/docs"
    }


# Include API routers
from app.api import auth, gpus, arbitrage, providers, reservations, clusters, wallets

app.include_router(auth.router, prefix=f"{settings.API_V1_PREFIX}/auth", tags=["Authentication"])
app.include_router(gpus.router, prefix=f"{settings.API_V1_PREFIX}/gpus", tags=["GPUs"])
app.include_router(arbitrage.router, prefix=f"{settings.API_V1_PREFIX}/arbitrage", tags=["Arbitrage"])
app.include_router(providers.router, prefix=f"{settings.API_V1_PREFIX}/providers", tags=["Providers"])
app.include_router(reservations.router, prefix=f"{settings.API_V1_PREFIX}/reservations", tags=["Reservations"])
app.include_router(clusters.router, prefix=f"{settings.API_V1_PREFIX}/clusters", tags=["Clusters"])
app.include_router(wallets.router, prefix=f"{settings.API_V1_PREFIX}/wallets", tags=["Wallets"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
