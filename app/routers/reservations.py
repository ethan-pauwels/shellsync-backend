from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime
from app.database import get_db
from app import models
from app.utils import get_current_user

router = APIRouter(prefix="/reservations", tags=["reservations"])

# Rower creates a reservation
@router.post("/")
async def create_reservation(boat_id: int, start_time: datetime, end_time: datetime, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Check boat exists and is available
    result = await db.execute(select(models.Boat).where(models.Boat.id == boat_id).where(models.Boat.boathouse_id == current_user.boathouse_id))
    boat = result.scalars().first()
    if not boat:
        raise HTTPException(status_code=404, detail="Boat not found")
    if boat.status != models.BoatStatus.available:
        raise HTTPException(status_code=400, detail="Boat not available")

    # Create reservation
    reservation = models.Reservation(
        user_id=current_user.id,
        boat_id=boat_id,
        boathouse_id=current_user.boathouse_id,
        start_time=start_time,
        end_time=end_time,
        status="confirmed"
    )
    boat.status = models.BoatStatus.reserved
    db.add(reservation)
    await db.commit()
    await db.refresh(reservation)
    return reservation

# View current user's reservations
@router.get("/me")
async def get_my_reservations(db: AsyncSession = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    result = await db.execute(
        select(models.Reservation)
        .where(models.Reservation.user_id == current_user.id)
        .order_by(models.Reservation.start_time.desc())
    )
    return result.scalars().all()

# Cancel a reservation
@router.delete("/{reservation_id}")
async def cancel_reservation(reservation_id: int, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    result = await db.execute(select(models.Reservation).where(models.Reservation.id == reservation_id, models.Reservation.user_id == current_user.id))
    reservation = result.scalars().first()
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")

    reservation.status = "cancelled"

    # Optional: Free up boat status
    boat = await db.get(models.Boat, reservation.boat_id)
    if boat:
        boat.status = models.BoatStatus.available

    await db.commit()
    return {"detail": "Reservation cancelled"}
