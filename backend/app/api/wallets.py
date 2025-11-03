"""
Wallet API Endpoints

Handles all wallet and financial operations including:
- Balance inquiries
- Deposits and withdrawals
- Transaction history
- Spending analytics
"""

from typing import List, Optional
from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models import User, TransactionType
from app.services.wallet_service import WalletService, InsufficientFundsError
from app.schemas import (
    WalletResponse,
    TransactionResponse,
    DepositRequest,
    WithdrawalRequest,
    SpendingAnalyticsResponse
)

router = APIRouter()


@router.get("/balance", response_model=WalletResponse)
async def get_wallet_balance(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current wallet balance and totals

    Returns:
        - Current USDC balance
        - Total earned (lifetime)
        - Total spent (lifetime)
    """
    service = WalletService(db)
    wallet = await service.get_wallet(current_user.id)

    return WalletResponse(
        id=wallet.id,
        user_id=wallet.user_id,
        balance_usdc=wallet.balance_usdc,
        total_earned=wallet.total_earned,
        total_spent=wallet.total_spent,
        created_at=wallet.created_at,
        updated_at=wallet.updated_at
    )


@router.get("/transactions", response_model=List[TransactionResponse])
async def get_transaction_history(
    limit: int = Query(50, ge=1, le=100, description="Number of transactions to return"),
    offset: int = Query(0, ge=0, description="Number of transactions to skip"),
    transaction_type: Optional[TransactionType] = Query(None, description="Filter by transaction type"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get transaction history

    Query parameters:
        - limit: Number of transactions to return (1-100, default 50)
        - offset: Pagination offset
        - transaction_type: Filter by specific transaction type

    Returns:
        List of transactions ordered by most recent first
    """
    service = WalletService(db)
    transactions = await service.get_transaction_history(
        user_id=current_user.id,
        limit=limit,
        offset=offset,
        transaction_type=transaction_type
    )

    return [
        TransactionResponse(
            id=t.id,
            wallet_id=t.wallet_id,
            type=t.type,
            amount=t.amount,
            balance_after=t.balance_after,
            description=t.description,
            transaction_hash=t.transaction_hash,
            reservation_id=t.reservation_id,
            cluster_id=t.cluster_id,
            metadata=t.metadata,
            created_at=t.created_at
        )
        for t in transactions
    ]


@router.post("/deposit", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def deposit_funds(
    deposit_data: DepositRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Deposit USDC into wallet

    Request body:
        - amount: Amount to deposit (must be positive)
        - transaction_hash: Optional blockchain transaction hash
        - metadata: Optional additional data

    Note: In production, this would integrate with Web3/blockchain
    verification. For MVP, this is a simplified implementation.

    Returns:
        Transaction record with new balance
    """
    service = WalletService(db)

    try:
        transaction = await service.deposit(
            user_id=current_user.id,
            amount=deposit_data.amount,
            transaction_hash=deposit_data.transaction_hash,
            metadata=deposit_data.metadata
        )

        return TransactionResponse(
            id=transaction.id,
            wallet_id=transaction.wallet_id,
            type=transaction.type,
            amount=transaction.amount,
            balance_after=transaction.balance_after,
            description=transaction.description,
            transaction_hash=transaction.transaction_hash,
            reservation_id=transaction.reservation_id,
            cluster_id=transaction.cluster_id,
            metadata=transaction.metadata,
            created_at=transaction.created_at
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/withdraw", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def withdraw_funds(
    withdrawal_data: WithdrawalRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Withdraw USDC from wallet

    Request body:
        - amount: Amount to withdraw (must be positive)
        - destination_address: Optional crypto wallet address
        - metadata: Optional additional data

    Note: In production, this would initiate a blockchain transaction.
    For MVP, this is a simplified implementation.

    Returns:
        Transaction record with new balance

    Errors:
        - 400: Invalid amount
        - 402: Insufficient funds
    """
    service = WalletService(db)

    try:
        transaction = await service.withdraw(
            user_id=current_user.id,
            amount=withdrawal_data.amount,
            destination_address=withdrawal_data.destination_address,
            metadata=withdrawal_data.metadata
        )

        return TransactionResponse(
            id=transaction.id,
            wallet_id=transaction.wallet_id,
            type=transaction.type,
            amount=transaction.amount,
            balance_after=transaction.balance_after,
            description=transaction.description,
            transaction_hash=transaction.transaction_hash,
            reservation_id=transaction.reservation_id,
            cluster_id=transaction.cluster_id,
            metadata=transaction.metadata,
            created_at=transaction.created_at
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except InsufficientFundsError as e:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=str(e)
        )


@router.get("/analytics", response_model=SpendingAnalyticsResponse)
async def get_spending_analytics(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get spending analytics

    Query parameters:
        - days: Number of days to analyze (1-365, default 30)

    Returns:
        - Total spent in period
        - Spending breakdown by category (reservations, clusters)
        - Transaction counts
        - Current balance
        - Lifetime totals
    """
    service = WalletService(db)
    analytics = await service.get_spending_analytics(
        user_id=current_user.id,
        days=days
    )

    return SpendingAnalyticsResponse(**analytics)
