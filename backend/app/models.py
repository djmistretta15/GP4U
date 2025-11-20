"""
SQLAlchemy Models
Database tables for GP4U platform
"""
from datetime import datetime
from decimal import Decimal
from sqlalchemy import (
    Column, String, Integer, Boolean, DateTime, Numeric, Text,
    ForeignKey, Enum as SQLEnum
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.core.database import Base


# Enums
class SkillLevel(str, enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    EXPERT = "expert"


class ThemePreference(str, enum.Enum):
    PROFESSIONAL = "professional"
    GAMING = "gaming"
    CREATIVE = "creative"
    DEVELOPER = "developer"
    MINIMAL = "minimal"
    CORPORATE = "corporate"
    ACADEMIC = "academic"


class ReservationStatus(str, enum.Enum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ClusterStatus(str, enum.Enum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"


class TransactionType(str, enum.Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    PAYMENT = "payment"
    REFUND = "refund"
    EARNING = "earning"


class TransactionStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class GPUStatus(str, enum.Enum):
    """GPU status for lease tracking (MVP)"""
    AVAILABLE = "available"
    LEASED = "leased"
    MAINTENANCE = "maintenance"


class ProvenanceEventType(str, enum.Enum):
    """Provenance event types for blockchain ledger (MVP)"""
    REGISTERED = "registered"
    STATUS_CHANGED = "status_changed"
    LEASED = "leased"
    RETURNED = "returned"
    MAINTENANCE_START = "maintenance_start"
    MAINTENANCE_END = "maintenance_end"


# Models
class User(Base):
    """User accounts"""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(Text, nullable=False)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True)
    skill_level = Column(SQLEnum(SkillLevel), default=SkillLevel.BEGINNER)
    theme_preference = Column(SQLEnum(ThemePreference), default=ThemePreference.PROFESSIONAL)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    reservations = relationship("Reservation", back_populates="user")
    clusters = relationship("Cluster", back_populates="user")
    wallet = relationship("Wallet", back_populates="user", uselist=False)
    organization = relationship("Organization", back_populates="users")


class Organization(Base):
    """Organizations for GPU lease tracking (MVP)"""
    __tablename__ = "organizations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    users = relationship("User", back_populates="organization")
    gpus = relationship("GPU", back_populates="organization")


class GPU(Base):
    """GPU inventory cache from providers"""
    __tablename__ = "gpus"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    provider = Column(String(50), nullable=False, index=True)
    external_id = Column(String(255), index=True)
    model = Column(String(100), nullable=False, index=True)
    vram_gb = Column(Integer)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True)
    status = Column(SQLEnum(GPUStatus), default=GPUStatus.AVAILABLE, index=True, nullable=True)
    price_per_hour = Column(Numeric(10, 2))
    location = Column(String(100))
    available = Column(Boolean, default=True, index=True)
    g_score = Column(Numeric(5, 2))  # Performance score 0-1
    uptime_percent = Column(Numeric(5, 2))
    benchmark_score = Column(Integer)  # For G-Score calculation
    power_consumption = Column(Integer)  # Watts
    max_power = Column(Integer)  # Max watts
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_synced = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    reservations = relationship("Reservation", back_populates="gpu")
    cluster_members = relationship("ClusterMember", back_populates="gpu")
    organization = relationship("Organization", back_populates="gpus")
    provenance_events = relationship("ProvenanceEvent", back_populates="gpu")


class Reservation(Base):
    """Time-block GPU reservations"""
    __tablename__ = "reservations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    gpu_id = Column(UUID(as_uuid=True), ForeignKey("gpus.id"), nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    total_cost = Column(Numeric(10, 2))
    status = Column(SQLEnum(ReservationStatus), default=ReservationStatus.PENDING, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="reservations")
    gpu = relationship("GPU", back_populates="reservations")


class Cluster(Base):
    """Multi-GPU clusters for distributed compute"""
    __tablename__ = "clusters"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    job_name = Column(String(255))
    gpu_count = Column(Integer)
    total_cost = Column(Numeric(10, 2))
    status = Column(SQLEnum(ClusterStatus), default=ClusterStatus.PENDING, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="clusters")
    members = relationship("ClusterMember", back_populates="cluster")


class ClusterMember(Base):
    """Individual GPUs in a cluster"""
    __tablename__ = "cluster_members"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cluster_id = Column(UUID(as_uuid=True), ForeignKey("clusters.id"), nullable=False)
    gpu_id = Column(UUID(as_uuid=True), ForeignKey("gpus.id"), nullable=False)
    contribution_score = Column(Numeric(5, 2))  # Performance contribution
    earnings = Column(Numeric(10, 2))

    # Relationships
    cluster = relationship("Cluster", back_populates="members")
    gpu = relationship("GPU", back_populates="cluster_members")


class Wallet(Base):
    """User crypto wallets"""
    __tablename__ = "wallets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True)
    address = Column(String(255), unique=True, index=True)
    balance = Column(Numeric(20, 8), default=0)
    currency = Column(String(10), default="USDC")

    # Relationships
    user = relationship("User", back_populates="wallet")
    transactions = relationship("Transaction", back_populates="wallet")


class Transaction(Base):
    """Wallet transactions"""
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    wallet_id = Column(UUID(as_uuid=True), ForeignKey("wallets.id"), nullable=False)
    amount = Column(Numeric(20, 8), nullable=False)
    type = Column(SQLEnum(TransactionType), nullable=False, index=True)
    status = Column(SQLEnum(TransactionStatus), default=TransactionStatus.PENDING, index=True)
    tx_hash = Column(String(255), nullable=True)  # Blockchain transaction hash
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    wallet = relationship("Wallet", back_populates="transactions")


class ArbitrageCache(Base):
    """Real-time arbitrage opportunities cache"""
    __tablename__ = "arbitrage_cache"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    gpu_type = Column(String(100), nullable=False, index=True)
    cheapest_provider = Column(String(50))
    cheapest_price = Column(Numeric(10, 2))
    expensive_provider = Column(String(50))
    expensive_price = Column(Numeric(10, 2))
    spread_pct = Column(Numeric(5, 2))
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)


class ProvenanceEvent(Base):
    """GPU provenance events for blockchain ledger (MVP)"""
    __tablename__ = "provenance_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    gpu_id = Column(UUID(as_uuid=True), ForeignKey("gpus.id"), nullable=False, index=True)
    event_type = Column(SQLEnum(ProvenanceEventType), nullable=False, index=True)
    payload_json = Column(Text, nullable=True)  # JSON string with event details
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationships
    gpu = relationship("GPU", back_populates="provenance_events")


class UserFeedback(Base):
    """User feedback for MVP validation"""
    __tablename__ = "user_feedback"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    rating = Column(Integer, nullable=False)  # 1-5 stars
    feature = Column(String(100), nullable=False, index=True)  # search, arbitrage, booking, etc.
    comment = Column(Text, nullable=True)
    page = Column(String(255), nullable=True)  # URL/page where feedback was given
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationships
    user = relationship("User")

