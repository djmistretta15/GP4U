#!/usr/bin/env python3
"""
Seed Data Script for GP4U MVP
Populates database with sample GPUs and users for demos
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import uuid

from app.models import GPU, User, Organization
from app.core.security import get_password_hash
from app.core.config import settings

async def seed_database():
    """Seed database with demo data"""
    
    # Create async engine
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False
    )
    
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        print("🌱 Seeding database...")
        
        # Create demo organization
        org = Organization(
            id=uuid.uuid4(),
            name="Demo Organization"
        )
        session.add(org)
        
        # Create demo users
        users = [
            User(
                id=uuid.uuid4(),
                email="demo@gp4u.com",
                hashed_password=get_password_hash("demo123"),
                username="demo_user",
                organization_id=org.id
            ),
            User(
                id=uuid.uuid4(),
                email="admin@gp4u.com",
                hashed_password=get_password_hash("admin123"),
                username="admin",
                organization_id=org.id
            ),
        ]
        for user in users:
            session.add(user)
        
        print(f"✓ Created {len(users)} users")
        
        # Create sample GPUs from different providers
        sample_gpus = [
            # Vast.ai GPUs
            {
                "provider": "vastai",
                "model": "RTX 4090",
                "vram_gb": 24,
                "price_per_hour": 3.15,
                "location": "US-West",
                "available": True,
                "g_score": 0.88,
                "uptime_percent": 98.5,
            },
            {
                "provider": "vastai",
                "model": "RTX 3090",
                "vram_gb": 24,
                "price_per_hour": 2.90,
                "location": "US-East",
                "available": True,
                "g_score": 0.82,
                "uptime_percent": 97.2,
            },
            {
                "provider": "vastai",
                "model": "A100",
                "vram_gb": 80,
                "price_per_hour": 8.50,
                "location": "EU-Central",
                "available": True,
                "g_score": 0.95,
                "uptime_percent": 99.1,
            },
            
            # io.net GPUs
            {
                "provider": "ionet",
                "model": "RTX 4090",
                "vram_gb": 24,
                "price_per_hour": 2.85,
                "location": "US-East",
                "available": True,
                "g_score": 0.91,
                "uptime_percent": 99.3,
            },
            {
                "provider": "ionet",
                "model": "H100",
                "vram_gb": 80,
                "price_per_hour": 12.00,
                "location": "US-West",
                "available": True,
                "g_score": 0.97,
                "uptime_percent": 99.7,
            },
            
            # Akash GPUs
            {
                "provider": "akash",
                "model": "RTX 4090",
                "vram_gb": 24,
                "price_per_hour": 2.45,
                "location": "US-East",
                "available": True,
                "g_score": 0.92,
                "uptime_percent": 99.8,
            },
            {
                "provider": "akash",
                "model": "RTX 3090",
                "vram_gb": 24,
                "price_per_hour": 2.20,
                "location": "Asia-Pacific",
                "available": True,
                "g_score": 0.85,
                "uptime_percent": 98.9,
            },
            
            # Render GPUs
            {
                "provider": "render",
                "model": "RTX 4090",
                "vram_gb": 24,
                "price_per_hour": 3.50,
                "location": "US-Central",
                "available": True,
                "g_score": 0.90,
                "uptime_percent": 99.5,
            },
            {
                "provider": "render",
                "model": "A100",
                "vram_gb": 40,
                "price_per_hour": 7.25,
                "location": "US-East",
                "available": True,
                "g_score": 0.93,
                "uptime_percent": 99.2,
            },
            
            # Some unavailable GPUs (for realism)
            {
                "provider": "vastai",
                "model": "RTX 4090",
                "vram_gb": 24,
                "price_per_hour": 2.95,
                "location": "EU-West",
                "available": False,
                "g_score": 0.87,
                "uptime_percent": 98.0,
            },
        ]
        
        for gpu_data in sample_gpus:
            gpu = GPU(
                id=uuid.uuid4(),
                external_id=f"{gpu_data['provider']}-{uuid.uuid4().hex[:8]}",
                created_at=datetime.utcnow() - timedelta(days=30),
                last_synced=datetime.utcnow(),
                **gpu_data
            )
            session.add(gpu)
        
        print(f"✓ Created {len(sample_gpus)} sample GPUs")
        
        await session.commit()
        print("✅ Database seeded successfully!")
        print("")
        print("Demo credentials:")
        print("  User: demo@gp4u.com / demo123")
        print("  Admin: admin@gp4u.com / admin123")
        print("")
        print("Sample data:")
        print(f"  - {len(sample_gpus)} GPUs across 4 providers")
        print("  - RTX 4090 arbitrage opportunity: $2.45-$3.50 (43% spread)")
        print("  - A100 options from $7.25-$12.00")
        print("")

if __name__ == "__main__":
    asyncio.run(seed_database())
