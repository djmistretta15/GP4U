"""
Wallet Service - Handles all financial operations

Features:
- USDC balance management
- Transaction ledger with double-entry bookkeeping
- Deposit and withdrawal processing
- Payment processing for reservations and clusters
- Earnings distribution to GPU providers
- Transaction history and analytics
"""

from decimal import Decimal
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from uuid import UUID
import logging

from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    Wallet, Transaction, TransactionType, User, Reservation,
    ReservationStatus, Cluster, ClusterStatus, ClusterMember, GPU
)
from app.core.config import settings

logger = logging.getLogger(__name__)


class InsufficientFundsError(Exception):
    """Raised when wallet has insufficient balance"""
    pass


class WalletService:
    """Service for managing wallet operations and transactions"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_wallet(self, user_id: UUID) -> Wallet:
        """Get or create wallet for user"""
        stmt = select(Wallet).where(Wallet.user_id == user_id)
        result = await self.db.execute(stmt)
        wallet = result.scalar_one_or_none()

        if not wallet:
            # Create wallet if it doesn't exist
            wallet = Wallet(
                user_id=user_id,
                balance_usdc=Decimal("0.00"),
                total_earned=Decimal("0.00"),
                total_spent=Decimal("0.00")
            )
            self.db.add(wallet)
            await self.db.commit()
            await self.db.refresh(wallet)
            logger.info(f"Created wallet for user {user_id}")

        return wallet

    async def get_balance(self, user_id: UUID) -> Decimal:
        """Get current wallet balance"""
        wallet = await self.get_wallet(user_id)
        return wallet.balance_usdc

    async def deposit(
        self,
        user_id: UUID,
        amount: Decimal,
        transaction_hash: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Transaction:
        """
        Deposit USDC into wallet

        Args:
            user_id: User's UUID
            amount: Amount to deposit (must be positive)
            transaction_hash: Blockchain transaction hash (for Web3 integration)
            metadata: Additional transaction metadata

        Returns:
            Transaction record
        """
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")

        wallet = await self.get_wallet(user_id)

        # Create transaction record
        transaction = Transaction(
            wallet_id=wallet.id,
            type=TransactionType.DEPOSIT,
            amount=amount,
            balance_after=wallet.balance_usdc + amount,
            description=f"Deposit of {amount} USDC",
            transaction_hash=transaction_hash,
            metadata=metadata or {}
        )

        # Update wallet balance
        wallet.balance_usdc += amount
        wallet.updated_at = datetime.utcnow()

        self.db.add(transaction)
        await self.db.commit()
        await self.db.refresh(transaction)

        logger.info(f"Deposited {amount} USDC to wallet {wallet.id}")
        return transaction

    async def withdraw(
        self,
        user_id: UUID,
        amount: Decimal,
        destination_address: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Transaction:
        """
        Withdraw USDC from wallet

        Args:
            user_id: User's UUID
            amount: Amount to withdraw (must be positive)
            destination_address: Crypto wallet address for withdrawal
            metadata: Additional transaction metadata

        Returns:
            Transaction record

        Raises:
            InsufficientFundsError: If wallet balance is insufficient
        """
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")

        wallet = await self.get_wallet(user_id)

        # Check sufficient funds
        if wallet.balance_usdc < amount:
            raise InsufficientFundsError(
                f"Insufficient funds: balance={wallet.balance_usdc}, requested={amount}"
            )

        # Create transaction record
        transaction_metadata = metadata or {}
        if destination_address:
            transaction_metadata["destination_address"] = destination_address

        transaction = Transaction(
            wallet_id=wallet.id,
            type=TransactionType.WITHDRAWAL,
            amount=amount,
            balance_after=wallet.balance_usdc - amount,
            description=f"Withdrawal of {amount} USDC",
            metadata=transaction_metadata
        )

        # Update wallet balance
        wallet.balance_usdc -= amount
        wallet.updated_at = datetime.utcnow()

        self.db.add(transaction)
        await self.db.commit()
        await self.db.refresh(transaction)

        logger.info(f"Withdrew {amount} USDC from wallet {wallet.id}")
        return transaction

    async def process_reservation_payment(
        self,
        user_id: UUID,
        reservation_id: UUID,
        amount: Decimal
    ) -> Transaction:
        """
        Process payment for a reservation

        This charges the user's wallet and records the transaction.
        Called when a reservation transitions to ACTIVE status.
        """
        if amount <= 0:
            raise ValueError("Payment amount must be positive")

        wallet = await self.get_wallet(user_id)

        # Check sufficient funds
        if wallet.balance_usdc < amount:
            raise InsufficientFundsError(
                f"Insufficient funds for reservation: balance={wallet.balance_usdc}, cost={amount}"
            )

        # Create transaction
        transaction = Transaction(
            wallet_id=wallet.id,
            type=TransactionType.RESERVATION_PAYMENT,
            amount=amount,
            balance_after=wallet.balance_usdc - amount,
            reservation_id=reservation_id,
            description=f"Payment for reservation {reservation_id}",
            metadata={"reservation_id": str(reservation_id)}
        )

        # Update wallet
        wallet.balance_usdc -= amount
        wallet.total_spent += amount
        wallet.updated_at = datetime.utcnow()

        self.db.add(transaction)
        await self.db.commit()
        await self.db.refresh(transaction)

        logger.info(f"Processed reservation payment: {amount} USDC for reservation {reservation_id}")
        return transaction

    async def refund_reservation(
        self,
        user_id: UUID,
        reservation_id: UUID,
        amount: Decimal
    ) -> Transaction:
        """
        Refund a cancelled reservation

        Returns funds to user's wallet with a refund transaction.
        """
        if amount <= 0:
            raise ValueError("Refund amount must be positive")

        wallet = await self.get_wallet(user_id)

        # Create refund transaction
        transaction = Transaction(
            wallet_id=wallet.id,
            type=TransactionType.RESERVATION_REFUND,
            amount=amount,
            balance_after=wallet.balance_usdc + amount,
            reservation_id=reservation_id,
            description=f"Refund for cancelled reservation {reservation_id}",
            metadata={"reservation_id": str(reservation_id)}
        )

        # Update wallet
        wallet.balance_usdc += amount
        wallet.updated_at = datetime.utcnow()

        self.db.add(transaction)
        await self.db.commit()
        await self.db.refresh(transaction)

        logger.info(f"Refunded {amount} USDC for reservation {reservation_id}")
        return transaction

    async def process_cluster_payment(
        self,
        user_id: UUID,
        cluster_id: UUID,
        amount: Decimal
    ) -> Transaction:
        """
        Process payment for a cluster

        Charges user's wallet when cluster is created.
        """
        if amount <= 0:
            raise ValueError("Payment amount must be positive")

        wallet = await self.get_wallet(user_id)

        # Check sufficient funds
        if wallet.balance_usdc < amount:
            raise InsufficientFundsError(
                f"Insufficient funds for cluster: balance={wallet.balance_usdc}, cost={amount}"
            )

        # Create transaction
        transaction = Transaction(
            wallet_id=wallet.id,
            type=TransactionType.CLUSTER_PAYMENT,
            amount=amount,
            balance_after=wallet.balance_usdc - amount,
            cluster_id=cluster_id,
            description=f"Payment for cluster {cluster_id}",
            metadata={"cluster_id": str(cluster_id)}
        )

        # Update wallet
        wallet.balance_usdc -= amount
        wallet.total_spent += amount
        wallet.updated_at = datetime.utcnow()

        self.db.add(transaction)
        await self.db.commit()
        await self.db.refresh(transaction)

        logger.info(f"Processed cluster payment: {amount} USDC for cluster {cluster_id}")
        return transaction

    async def distribute_cluster_earnings(
        self,
        cluster_id: UUID
    ) -> List[Transaction]:
        """
        Distribute earnings to GPU providers in a cluster

        Called when cluster is completed. Distributes payment based on
        contribution scores calculated by ClusterOrchestrator.

        Returns:
            List of earning transactions for each provider
        """
        # Get cluster and its members
        stmt = select(Cluster).where(Cluster.id == cluster_id)
        result = await self.db.execute(stmt)
        cluster = result.scalar_one_or_none()

        if not cluster:
            raise ValueError(f"Cluster {cluster_id} not found")

        if cluster.status != ClusterStatus.COMPLETED:
            raise ValueError(f"Can only distribute earnings for completed clusters")

        # Get cluster members with their GPUs
        stmt = (
            select(ClusterMember, GPU)
            .join(GPU, ClusterMember.gpu_id == GPU.id)
            .where(ClusterMember.cluster_id == cluster_id)
        )
        result = await self.db.execute(stmt)
        members = result.all()

        transactions = []
        total_distributed = Decimal("0.00")

        for member, gpu in members:
            # Calculate earnings based on contribution score
            earnings = cluster.total_cost * member.contribution_score

            # Get GPU owner's wallet
            owner_wallet = await self.get_wallet(gpu.provider_user_id)

            # Create earning transaction
            transaction = Transaction(
                wallet_id=owner_wallet.id,
                type=TransactionType.CLUSTER_EARNINGS,
                amount=earnings,
                balance_after=owner_wallet.balance_usdc + earnings,
                cluster_id=cluster_id,
                description=f"Earnings from cluster {cluster_id} (contribution: {member.contribution_score:.2%})",
                metadata={
                    "cluster_id": str(cluster_id),
                    "gpu_id": str(gpu.id),
                    "contribution_score": float(member.contribution_score)
                }
            )

            # Update wallet
            owner_wallet.balance_usdc += earnings
            owner_wallet.total_earned += earnings
            owner_wallet.updated_at = datetime.utcnow()

            self.db.add(transaction)
            transactions.append(transaction)
            total_distributed += earnings

            logger.info(
                f"Distributed {earnings} USDC to provider {gpu.provider_user_id} "
                f"for GPU {gpu.id} (contribution: {member.contribution_score:.2%})"
            )

        await self.db.commit()

        logger.info(
            f"Completed earnings distribution for cluster {cluster_id}: "
            f"{total_distributed} USDC to {len(transactions)} providers"
        )

        return transactions

    async def get_transaction_history(
        self,
        user_id: UUID,
        limit: int = 50,
        offset: int = 0,
        transaction_type: Optional[TransactionType] = None
    ) -> List[Transaction]:
        """Get transaction history for a user"""
        wallet = await self.get_wallet(user_id)

        stmt = select(Transaction).where(Transaction.wallet_id == wallet.id)

        if transaction_type:
            stmt = stmt.where(Transaction.type == transaction_type)

        stmt = stmt.order_by(Transaction.created_at.desc()).limit(limit).offset(offset)

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_spending_analytics(
        self,
        user_id: UUID,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get spending analytics for a user

        Returns:
            Dictionary with spending breakdown by category
        """
        wallet = await self.get_wallet(user_id)
        since_date = datetime.utcnow() - timedelta(days=days)

        # Get spending by type
        stmt = (
            select(
                Transaction.type,
                func.sum(Transaction.amount).label('total'),
                func.count(Transaction.id).label('count')
            )
            .where(
                and_(
                    Transaction.wallet_id == wallet.id,
                    Transaction.created_at >= since_date,
                    Transaction.type.in_([
                        TransactionType.RESERVATION_PAYMENT,
                        TransactionType.CLUSTER_PAYMENT
                    ])
                )
            )
            .group_by(Transaction.type)
        )

        result = await self.db.execute(stmt)
        spending_breakdown = {row.type: {"total": row.total, "count": row.count} for row in result}

        # Calculate totals
        total_spent = sum(item["total"] for item in spending_breakdown.values())
        total_transactions = sum(item["count"] for item in spending_breakdown.values())

        return {
            "period_days": days,
            "total_spent": total_spent,
            "total_transactions": total_transactions,
            "breakdown": spending_breakdown,
            "current_balance": wallet.balance_usdc,
            "lifetime_spent": wallet.total_spent,
            "lifetime_earned": wallet.total_earned
        }
