"""
GP4U FastAPI Application
Main entry point for the API server
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import init_db, close_db
from app.services.provider_init import initialize_providers, shutdown_providers

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan events
    Handles startup and shutdown tasks
    """
    # Startup
    logger.info("🚀 GP4U API Starting...")
    logger.info(f"📋 Version: {settings.VERSION}")
    logger.info(f"🔧 Debug Mode: {settings.DEBUG}")

    # Initialize database
    await init_db()
    logger.info("✅ Database initialized")

    # Initialize providers (Phase 7)
    try:
        providers = await initialize_providers()
        logger.info(f"✅ Initialized {len(providers)} GPU providers")
    except Exception as e:
        logger.error(f"⚠️ Provider initialization failed: {e}")
        logger.warning("Continuing without providers - they can be initialized via API")

    logger.info("🎉 GP4U API Ready!")
    yield

    # Shutdown
    logger.info("🛑 Shutting down GP4U API...")

    # Shutdown providers
    try:
        await shutdown_providers()
        logger.info("✅ Providers shut down gracefully")
    except Exception as e:
        logger.error(f"⚠️ Provider shutdown error: {e}")

    # Close database
    await close_db()
    logger.info("✅ Database connections closed")
    logger.info("👋 GP4U API Stopped")


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
from app.api.v1 import provider_health

app.include_router(auth.router, prefix=f"{settings.API_V1_PREFIX}/auth", tags=["Authentication"])
app.include_router(gpus.router, prefix=f"{settings.API_V1_PREFIX}/gpus", tags=["GPUs"])
app.include_router(arbitrage.router, prefix=f"{settings.API_V1_PREFIX}/arbitrage", tags=["Arbitrage"])
app.include_router(providers.router, prefix=f"{settings.API_V1_PREFIX}/providers", tags=["Providers"])
app.include_router(reservations.router, prefix=f"{settings.API_V1_PREFIX}/reservations", tags=["Reservations"])
app.include_router(clusters.router, prefix=f"{settings.API_V1_PREFIX}/clusters", tags=["Clusters"])
app.include_router(wallets.router, prefix=f"{settings.API_V1_PREFIX}/wallets", tags=["Wallets"])
app.include_router(provider_health.router, prefix=f"{settings.API_V1_PREFIX}/provider-health", tags=["Provider Health"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
