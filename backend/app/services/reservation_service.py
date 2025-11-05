"""
Reservation Service
Handles GPU time-block booking logic
"""
import logging
from datetime import datetime, timedelta
from typing import List, Optional
from decimal import Decimal
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from fastapi import HTTPException, status

from app.models import Reservation, GPU, User, ReservationStatus

logger = logging.getLogger(__name__)


class ReservationService:
    """
    Service for managing GPU reservations
    Handles booking, cancellation, extension, and conflict detection
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_reservation(
        self,
        user_id: UUID,
        gpu_id: UUID,
        start_time: datetime,
        end_time: datetime
    ) -> Reservation:
        """
        Create a new GPU reservation

        Args:
            user_id: User making the reservation
            gpu_id: GPU to reserve
            start_time: Reservation start time
            end_time: Reservation end time

        Returns:
            Created reservation

        Raises:
            HTTPException: If validation fails or GPU unavailable
        """
        # Validate times
        if start_time >= end_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="End time must be after start time"
            )

        if start_time < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot book in the past"
            )

        # Check GPU exists and is available
        gpu = await self._get_gpu(gpu_id)
        if not gpu.available:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="GPU is not available"
            )

        # Check for conflicts
        has_conflict = await self._check_conflicts(gpu_id, start_time, end_time)
        if has_conflict:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Time slot conflicts with existing reservation"
            )

        # Calculate cost
        duration_hours = (end_time - start_time).total_seconds() / 3600
        total_cost = gpu.price_per_hour * Decimal(str(duration_hours))

        # Create reservation
        reservation = Reservation(
            user_id=user_id,
            gpu_id=gpu_id,
            start_time=start_time,
            end_time=end_time,
            total_cost=total_cost,
            status=ReservationStatus.PENDING
        )

        self.db.add(reservation)
        await self.db.commit()
        await self.db.refresh(reservation)

        logger.info(
            f"Created reservation {reservation.id} for user {user_id} "
            f"on GPU {gpu_id} from {start_time} to {end_time}"
        )

        return reservation

    async def get_user_reservations(
        self,
        user_id: UUID,
        status_filter: Optional[ReservationStatus] = None,
        upcoming_only: bool = False
    ) -> List[Reservation]:
        """
        Get all reservations for a user

        Args:
            user_id: User ID
            status_filter: Filter by status (optional)
            upcoming_only: Only show future reservations

        Returns:
            List of reservations
        """
        query = select(Reservation).where(Reservation.user_id == user_id)

        if status_filter:
            query = query.where(Reservation.status == status_filter)

        if upcoming_only:
            query = query.where(Reservation.end_time > datetime.utcnow())

        query = query.order_by(Reservation.start_time.desc())

        result = await self.db.execute(query)
        reservations = result.scalars().all()

        return list(reservations)

    async def get_reservation(self, reservation_id: UUID) -> Reservation:
        """Get reservation by ID"""
        result = await self.db.execute(
            select(Reservation).where(Reservation.id == reservation_id)
        )
        reservation = result.scalar_one_or_none()

        if not reservation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reservation not found"
            )

        return reservation

    async def cancel_reservation(
        self,
        reservation_id: UUID,
        user_id: UUID
    ) -> Reservation:
        """
        Cancel a reservation

        Args:
            reservation_id: Reservation to cancel
            user_id: User requesting cancellation

        Returns:
            Updated reservation

        Raises:
            HTTPException: If unauthorized or already started
        """
        reservation = await self.get_reservation(reservation_id)

        # Check ownership
        if reservation.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to cancel this reservation"
            )

        # Check if already started
        if reservation.start_time < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot cancel reservation that has already started"
            )

        # Check if already cancelled
        if reservation.status == ReservationStatus.CANCELLED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reservation is already cancelled"
            )

        # Process refund if reservation was already paid (ACTIVE status)
        if reservation.status == ReservationStatus.ACTIVE:
            from app.services.wallet_service import WalletService
            wallet_service = WalletService(self.db)

            await wallet_service.refund_reservation(
                user_id=user_id,
                reservation_id=reservation_id,
                amount=reservation.total_cost
            )

            logger.info(
                f"Refunded {reservation.total_cost} USDC for cancelled reservation {reservation_id}"
            )

        # Update status
        reservation.status = ReservationStatus.CANCELLED
        await self.db.commit()
        await self.db.refresh(reservation)

        logger.info(f"Cancelled reservation {reservation_id}")

        return reservation

    async def extend_reservation(
        self,
        reservation_id: UUID,
        user_id: UUID,
        new_end_time: datetime
    ) -> Reservation:
        """
        Extend a reservation's end time

        Args:
            reservation_id: Reservation to extend
            user_id: User requesting extension
            new_end_time: New end time

        Returns:
            Updated reservation

        Raises:
            HTTPException: If validation fails
        """
        reservation = await self.get_reservation(reservation_id)

        # Check ownership
        if reservation.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to extend this reservation"
            )

        # Check if can be extended
        if reservation.status != ReservationStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can only extend active reservations"
            )

        # Validate new end time
        if new_end_time <= reservation.end_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New end time must be later than current end time"
            )

        # Check for conflicts with new time
        has_conflict = await self._check_conflicts(
            reservation.gpu_id,
            reservation.end_time,
            new_end_time,
            exclude_reservation_id=reservation_id
        )

        if has_conflict:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Extension conflicts with another reservation"
            )

        # Get GPU for pricing
        gpu = await self._get_gpu(reservation.gpu_id)

        # Calculate additional cost
        additional_hours = (new_end_time - reservation.end_time).total_seconds() / 3600
        additional_cost = gpu.price_per_hour * Decimal(str(additional_hours))

        # Update reservation
        reservation.end_time = new_end_time
        reservation.total_cost += additional_cost

        await self.db.commit()
        await self.db.refresh(reservation)

        logger.info(
            f"Extended reservation {reservation_id} to {new_end_time}, "
            f"additional cost: ${additional_cost}"
        )

        return reservation

    async def get_available_slots(
        self,
        gpu_id: UUID,
        date: datetime,
        slot_duration_hours: int = 1
    ) -> List[dict]:
        """
        Get available time slots for a GPU on a specific date

        Args:
            gpu_id: GPU to check
            date: Date to check (time will be set to start of day)
            slot_duration_hours: Duration of each slot in hours

        Returns:
            List of available time slots
        """
        # Get start and end of day
        day_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)

        # Get all reservations for this GPU on this day
        result = await self.db.execute(
            select(Reservation).where(
                and_(
                    Reservation.gpu_id == gpu_id,
                    Reservation.status.in_([ReservationStatus.PENDING, ReservationStatus.ACTIVE]),
                    or_(
                        and_(
                            Reservation.start_time >= day_start,
                            Reservation.start_time < day_end
                        ),
                        and_(
                            Reservation.end_time > day_start,
                            Reservation.end_time <= day_end
                        ),
                        and_(
                            Reservation.start_time < day_start,
                            Reservation.end_time > day_end
                        )
                    )
                )
            )
        )
        reservations = result.scalars().all()

        # Generate all possible slots
        slots = []
        current_time = max(day_start, datetime.utcnow())

        while current_time < day_end:
            slot_end = current_time + timedelta(hours=slot_duration_hours)

            # Check if slot conflicts with any reservation
            is_available = True
            for reservation in reservations:
                if (current_time < reservation.end_time and
                    slot_end > reservation.start_time):
                    is_available = False
                    break

            if is_available and current_time >= datetime.utcnow():
                slots.append({
                    'start_time': current_time.isoformat(),
                    'end_time': slot_end.isoformat(),
                    'available': True
                })

            current_time += timedelta(hours=slot_duration_hours)

        return slots

    async def _get_gpu(self, gpu_id: UUID) -> GPU:
        """Get GPU by ID"""
        result = await self.db.execute(
            select(GPU).where(GPU.id == gpu_id)
        )
        gpu = result.scalar_one_or_none()

        if not gpu:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="GPU not found"
            )

        return gpu

    async def _check_conflicts(
        self,
        gpu_id: UUID,
        start_time: datetime,
        end_time: datetime,
        exclude_reservation_id: Optional[UUID] = None
    ) -> bool:
        """
        Check if time range conflicts with existing reservations

        Args:
            gpu_id: GPU to check
            start_time: Proposed start time
            end_time: Proposed end time
            exclude_reservation_id: Reservation to exclude from check (for extensions)

        Returns:
            True if conflict exists, False otherwise
        """
        query = select(Reservation).where(
            and_(
                Reservation.gpu_id == gpu_id,
                Reservation.status.in_([ReservationStatus.PENDING, ReservationStatus.ACTIVE]),
                or_(
                    # New reservation starts during existing reservation
                    and_(
                        Reservation.start_time <= start_time,
                        Reservation.end_time > start_time
                    ),
                    # New reservation ends during existing reservation
                    and_(
                        Reservation.start_time < end_time,
                        Reservation.end_time >= end_time
                    ),
                    # New reservation completely contains existing reservation
                    and_(
                        start_time <= Reservation.start_time,
                        end_time >= Reservation.end_time
                    )
                )
            )
        )

        if exclude_reservation_id:
            query = query.where(Reservation.id != exclude_reservation_id)

        result = await self.db.execute(query)
        conflicts = result.scalars().first()

        return conflicts is not None

    async def activate_pending_reservations(self) -> int:
        """
        Activate reservations that have reached their start time

        This should be called by a background worker periodically
        Processes payment when activating reservation

        Returns:
            Number of reservations activated
        """
        from app.services.wallet_service import WalletService, InsufficientFundsError

        result = await self.db.execute(
            select(Reservation).where(
                and_(
                    Reservation.status == ReservationStatus.PENDING,
                    Reservation.start_time <= datetime.utcnow()
                )
            )
        )
        pending_reservations = result.scalars().all()
        activated_count = 0

        wallet_service = WalletService(self.db)

        for reservation in pending_reservations:
            try:
                # Process payment
                await wallet_service.process_reservation_payment(
                    user_id=reservation.user_id,
                    reservation_id=reservation.id,
                    amount=reservation.total_cost
                )

                # Activate reservation
                reservation.status = ReservationStatus.ACTIVE
                activated_count += 1

                logger.info(
                    f"Activated reservation {reservation.id} and processed payment of "
                    f"{reservation.total_cost} USDC"
                )
            except InsufficientFundsError as e:
                # Cancel reservation if insufficient funds
                reservation.status = ReservationStatus.CANCELLED
                logger.warning(
                    f"Cancelled reservation {reservation.id} due to insufficient funds: {e}"
                )
            except Exception as e:
                logger.error(
                    f"Failed to activate reservation {reservation.id}: {e}"
                )

        await self.db.commit()

        logger.info(f"Activated {activated_count} reservations")
        return activated_count

    async def complete_finished_reservations(self) -> int:
        """
        Mark reservations as completed when they reach end time

        Returns:
            Number of reservations completed
        """
        result = await self.db.execute(
            select(Reservation).where(
                and_(
                    Reservation.status == ReservationStatus.ACTIVE,
                    Reservation.end_time <= datetime.utcnow()
                )
            )
        )
        active_reservations = result.scalars().all()

        for reservation in active_reservations:
            reservation.status = ReservationStatus.COMPLETED

        await self.db.commit()

        logger.info(f"Completed {len(active_reservations)} reservations")
        return len(active_reservations)
