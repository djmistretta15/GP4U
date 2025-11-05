"""
Pydantic Schemas
Request/Response models for API validation
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from uuid import UUID
from app.models import (
    SkillLevel, ThemePreference, ReservationStatus,
    ClusterStatus, TransactionType, TransactionStatus
)


# User Schemas
class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(min_length=8)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    skill_level: Optional[SkillLevel] = None
    theme_preference: Optional[ThemePreference] = None


class User(UserBase):
    id: UUID
    skill_level: SkillLevel
    theme_preference: ThemePreference
    created_at: datetime
    last_login: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# GPU Schemas
class GPUBase(BaseModel):
    provider: str
    model: str
    vram_gb: int
    price_per_hour: Decimal
    location: str


class GPU(GPUBase):
    id: UUID
    available: bool
    g_score: Optional[Decimal] = None
    uptime_percent: Optional[Decimal] = None
    last_synced: datetime

    model_config = ConfigDict(from_attributes=True)


class GPUSearch(BaseModel):
    model: Optional[str] = None
    min_vram: Optional[int] = None
    max_price: Optional[Decimal] = None
    provider: Optional[str] = None
    location: Optional[str] = None


class GPUCompare(BaseModel):
    gpu_ids: List[UUID] = Field(min_length=2, max_length=3)


# Reservation Schemas
class ReservationCreate(BaseModel):
    gpu_id: UUID
    start_time: datetime
    end_time: datetime


class ReservationUpdate(BaseModel):
    end_time: Optional[datetime] = None
    status: Optional[ReservationStatus] = None


class Reservation(BaseModel):
    id: UUID
    user_id: UUID
    gpu_id: UUID
    start_time: datetime
    end_time: datetime
    total_cost: Decimal
    status: ReservationStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Cluster Schemas
class ClusterCreate(BaseModel):
    job_name: str
    compute_intensity: int = Field(description="Required TFLOPS")
    vram_gb: int
    deadline_hours: int
    gpu_count: Optional[int] = None


class ClusterMember(BaseModel):
    id: UUID
    gpu_id: UUID
    contribution_score: Decimal
    earnings: Decimal

    model_config = ConfigDict(from_attributes=True)


class Cluster(BaseModel):
    id: UUID
    user_id: UUID
    job_name: str
    gpu_count: int
    total_cost: Decimal
    status: ClusterStatus
    created_at: datetime
    completed_at: Optional[datetime] = None
    members: List[ClusterMember] = []

    model_config = ConfigDict(from_attributes=True)


# Wallet Schemas
class WalletResponse(BaseModel):
    id: UUID
    user_id: UUID
    balance_usdc: Decimal
    total_earned: Decimal
    total_spent: Decimal
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DepositRequest(BaseModel):
    amount: Decimal = Field(gt=0, description="Amount to deposit (must be positive)")
    transaction_hash: Optional[str] = Field(None, description="Blockchain transaction hash")
    metadata: Optional[dict] = Field(default_factory=dict)


class WithdrawalRequest(BaseModel):
    amount: Decimal = Field(gt=0, description="Amount to withdraw (must be positive)")
    destination_address: Optional[str] = Field(None, description="Crypto wallet address")
    metadata: Optional[dict] = Field(default_factory=dict)


class TransactionResponse(BaseModel):
    id: UUID
    wallet_id: UUID
    type: TransactionType
    amount: Decimal
    balance_after: Decimal
    description: str
    transaction_hash: Optional[str] = None
    reservation_id: Optional[UUID] = None
    cluster_id: Optional[UUID] = None
    metadata: dict
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SpendingAnalyticsResponse(BaseModel):
    period_days: int
    total_spent: Decimal
    total_transactions: int
    breakdown: dict
    current_balance: Decimal
    lifetime_spent: Decimal
    lifetime_earned: Decimal


# Arbitrage Schemas
class ArbitrageOpportunity(BaseModel):
    gpu_type: str
    cheapest_provider: str
    cheapest_price: Decimal
    expensive_provider: str
    expensive_price: Decimal
    spread_pct: Decimal
    savings_per_hour: Decimal
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


# Auth Schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    email: Optional[str] = None


# Analytics Schemas
class DashboardStats(BaseModel):
    total_gpus: int
    available_gpus: int
    total_users: int
    active_reservations: int
    total_arbitrage_opportunities: int
    best_arbitrage_pct: Decimal


class EarningsHistory(BaseModel):
    date: datetime
    amount: Decimal
    source: str
