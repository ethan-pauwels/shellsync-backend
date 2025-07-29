from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timezone
from dateutil.tz import tzlocal
from app.database import get_db
from app import models
from app.utils import get_current_user

router = APIRouter(prefix="/reservations", tags=["reservations"])

# 🚀 Define the request model
class ReservationRequest(BaseModel):
    boat_id: int
    start_time: datetime
    end_time: datetime

# 🆕 Request model for rescheduling
class RescheduleRequest(BaseModel):
    start_time: datetime
    end_time: datetime

# Rower creates a reservation
@router.post("/")
async def create_reservation(
    req: ReservationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Handle naive datetime from frontend and convert to aware UTC
    start = req.start_time
    if start.tzinfo is None:
        start = start.replace(tzinfo=tzlocal())
    start = start.astimezone(timezone.utc)

    end = req.end_time
    if end.tzinfo is None:
        end = end.replace(tzinfo=tzlocal())
    end = end.astimezone(timezone.utc)

    # Convert to naive UTC for SQLAlchemy/Postgres comparison
    naive_start = start.replace(tzinfo=None)
    naive_end = end.replace(tzinfo=None)

    # Check boat exists and is available
    result = await db.execute(
        select(models.Boat)
        .where(models.Boat.id == req.boat_id)
        .where(models.Boat.boathouse_id == current_user.boathouse_id)
    )
    boat = result.scalars().first()
    if not boat:
        raise HTTPException(status_code=404, detail="Boat not found")
    if boat.status != models.BoatStatus.available:
        raise HTTPException(status_code=400, detail="Boat not available")

    # 🚫 Check for overlapping reservations
    overlap_result = await db.execute(
        select(models.Reservation)
        .where(models.Reservation.boat_id == req.boat_id)
        .where(models.Reservation.status == "confirmed")
        .where(models.Reservation.start_time < naive_end)
        .where(models.Reservation.end_time > naive_start)
    )
    if overlap_result.scalars().first():
        raise HTTPException(status_code=409, detail="Boat already reserved during this time window.")

    # ✅ Create reservation
    reservation = models.Reservation(
        user_id=current_user.id,
        boat_id=req.boat_id,
        boathouse_id=current_user.boathouse_id,
        start_time=naive_start,
        end_time=naive_end,
        status="confirmed"
    )
    db.add(reservation)
    await db.commit()
    await db.refresh(reservation)
    return reservation

# View current user's reservations
@router.get("/me")
async def get_my_reservations(
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    result = await db.execute(
        select(models.Reservation)
        .where(models.Reservation.user_id == current_user.id)
        .where(models.Reservation.status == "confirmed")
        .order_by(models.Reservation.start_time.desc())
    )
    return result.scalars().all()

# Cancel a reservation
@router.delete("/{reservation_id}")
async def cancel_reservation(
    reservation_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    result = await db.execute(
        select(models.Reservation)
        .where(models.Reservation.id == reservation_id)
        .where(models.Reservation.user_id == current_user.id)
    )
    reservation = result.scalars().first()
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")

    reservation.status = "cancelled"

    boat = await db.get(models.Boat, reservation.boat_id)
    if boat:
        boat.status = models.BoatStatus.available

    await db.commit()
    return {"detail": "Reservation cancelled"}

# ✅ View all upcoming reservations at user's boathouse
@router.get("/upcoming")
async def get_upcoming_reservations(
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    now = datetime.utcnow()
    result = await db.execute(
        select(models.Reservation, models.Boat)
        .join(models.Boat, models.Reservation.boat_id == models.Boat.id)
        .where(models.Reservation.boathouse_id == current_user.boathouse_id)
        .where(models.Reservation.status == "confirmed")
        .where(models.Reservation.start_time > now)
        .order_by(models.Reservation.start_time)
    )
    reservations = result.all()

    return [
        {
            "reservation_id": res.id,
            "boat_id": res.boat_id,
            "boat_name": boat.name,
            "boat_type": boat.type,
            "start_time": res.start_time,
            "end_time": res.end_time
        }
        for res, boat in reservations
    ]

# 🔁 Reschedule a reservation
@router.patch("/{reservation_id}")
async def reschedule_reservation(
    reservation_id: int,
    req: RescheduleRequest,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Convert times to UTC
    start = req.start_time
    end = req.end_time
    if start.tzinfo is None:
        start = start.replace(tzinfo=tzlocal())
    start = start.astimezone(timezone.utc).replace(tzinfo=None)

    if end.tzinfo is None:
        end = end.replace(tzinfo=tzlocal())
    end = end.astimezone(timezone.utc).replace(tzinfo=None)

    result = await db.execute(
        select(models.Reservation)
        .where(models.Reservation.id == reservation_id)
        .where(models.Reservation.user_id == current_user.id)
        .where(models.Reservation.status == "confirmed")
    )
    reservation = result.scalars().first()
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")

    # ✅ Check for conflicts
    overlap_result = await db.execute(
        select(models.Reservation)
        .where(models.Reservation.boat_id == reservation.boat_id)
        .where(models.Reservation.status == "confirmed")
        .where(models.Reservation.id != reservation_id)
        .where(models.Reservation.start_time < end)
        .where(models.Reservation.end_time > start)
    )
    if overlap_result.scalars().first():
        raise HTTPException(status_code=409, detail="New time conflicts with an existing reservation.")

    reservation.start_time = start
    reservation.end_time = end
    await db.commit()
    return {"detail": "Reservation rescheduled"}
