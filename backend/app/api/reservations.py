"""
Reservation API Routes
GPU time-block booking system
"""
from typing import List, Optional
from datetime import datetime
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models import User, ReservationStatus
from app.schemas import (
    ReservationCreate, Reservation as ReservationSchema,
    ReservationUpdate
)
from app.services.reservation_service import ReservationService

router = APIRouter()


@router.post("/", response_model=ReservationSchema, status_code=201)
async def create_reservation(
    reservation_data: ReservationCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new GPU reservation

    Books a GPU for a specific time block.
    Validates availability and checks for conflicts.

    Args:
        reservation_data: Reservation details (gpu_id, start_time, end_time)
        current_user: Authenticated user

    Returns:
        Created reservation with cost calculation

    Raises:
        400: Invalid time range or GPU unavailable
        409: Time slot conflicts with existing reservation
    """
    service = ReservationService(db)
    reservation = await service.create_reservation(
        user_id=current_user.id,
        gpu_id=reservation_data.gpu_id,
        start_time=reservation_data.start_time,
        end_time=reservation_data.end_time
    )

    return reservation


@router.get("/my-bookings", response_model=List[ReservationSchema])
async def get_my_reservations(
    status: Optional[ReservationStatus] = Query(None, description="Filter by status"),
    upcoming_only: bool = Query(False, description="Show only upcoming reservations"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all reservations for current user

    Query Parameters:
        status: Filter by reservation status (pending, active, completed, cancelled)
        upcoming_only: Only show future reservations

    Returns:
        List of user's reservations
    """
    service = ReservationService(db)
    reservations = await service.get_user_reservations(
        user_id=current_user.id,
        status_filter=status,
        upcoming_only=upcoming_only
    )

    return reservations


@router.get("/{reservation_id}", response_model=ReservationSchema)
async def get_reservation(
    reservation_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get details of a specific reservation

    Args:
        reservation_id: Reservation UUID

    Returns:
        Reservation details
    """
    service = ReservationService(db)
    reservation = await service.get_reservation(reservation_id)

    # Only allow owner to view
    if reservation.user_id != current_user.id:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this reservation"
        )

    return reservation


@router.delete("/{reservation_id}/cancel", response_model=ReservationSchema)
async def cancel_reservation(
    reservation_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Cancel a reservation

    Can only cancel if:
    - User owns the reservation
    - Reservation hasn't started yet
    - Reservation isn't already cancelled

    Args:
        reservation_id: Reservation to cancel

    Returns:
        Updated reservation with cancelled status

    Raises:
        400: Reservation already started or cancelled
        403: Not authorized
    """
    service = ReservationService(db)
    reservation = await service.cancel_reservation(
        reservation_id=reservation_id,
        user_id=current_user.id
    )

    return reservation


@router.post("/{reservation_id}/extend", response_model=ReservationSchema)
async def extend_reservation(
    reservation_id: UUID,
    new_end_time: datetime = Query(..., description="New end time"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Extend a reservation's end time

    Extends an active reservation and calculates additional cost.
    Checks for conflicts with other reservations.

    Args:
        reservation_id: Reservation to extend
        new_end_time: New end time (must be later than current end)

    Returns:
        Updated reservation with new end time and cost

    Raises:
        400: Invalid end time or reservation not active
        403: Not authorized
        409: Extension conflicts with another reservation
    """
    service = ReservationService(db)
    reservation = await service.extend_reservation(
        reservation_id=reservation_id,
        user_id=current_user.id,
        new_end_time=new_end_time
    )

    return reservation


@router.get("/gpu/{gpu_id}/available-slots")
async def get_available_slots(
    gpu_id: UUID,
    date: datetime = Query(..., description="Date to check (YYYY-MM-DD)"),
    duration_hours: int = Query(1, description="Slot duration in hours", ge=1, le=24),
    db: AsyncSession = Depends(get_db)
):
    """
    Get available time slots for a GPU on a specific date

    Useful for displaying a booking calendar.
    Shows all available time slots of specified duration.

    Args:
        gpu_id: GPU to check availability for
        date: Date to check (time will be ignored)
        duration_hours: Duration of each slot (1-24 hours)

    Returns:
        List of available time slots with start/end times
    """
    service = ReservationService(db)
    slots = await service.get_available_slots(
        gpu_id=gpu_id,
        date=date,
        slot_duration_hours=duration_hours
    )

    return {
        "gpu_id": str(gpu_id),
        "date": date.date().isoformat(),
        "slot_duration_hours": duration_hours,
        "available_slots": slots,
        "total_slots": len(slots)
    }


@router.get("/gpu/{gpu_id}/calendar")
async def get_reservation_calendar(
    gpu_id: UUID,
    start_date: datetime = Query(..., description="Calendar start date"),
    days: int = Query(7, description="Number of days to show", ge=1, le=30),
    db: AsyncSession = Depends(get_db)
):
    """
    Get reservation calendar for a GPU

    Shows booked and available periods over multiple days.

    Args:
        gpu_id: GPU to get calendar for
        start_date: Starting date
        days: Number of days to include (1-30)

    Returns:
        Calendar with daily availability
    """
    from datetime import timedelta

    service = ReservationService(db)
    calendar = []

    current_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)

    for _ in range(days):
        slots = await service.get_available_slots(
            gpu_id=gpu_id,
            date=current_date,
            slot_duration_hours=1
        )

        calendar.append({
            "date": current_date.date().isoformat(),
            "total_hours_available": len([s for s in slots if s['available']]),
            "slots": slots
        })

        current_date += timedelta(days=1)

    return {
        "gpu_id": str(gpu_id),
        "calendar": calendar
    }
