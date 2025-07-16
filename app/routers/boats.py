from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime  # ✅ NEW
from app.database import get_db
from app import models
from app.utils import get_current_user

router = APIRouter(prefix="/boats", tags=["boats"])

# ... [other routes unchanged] ...

# ✅ Member/Admin: Check out a boat
@router.post("/{boat_id}/checkout")
async def checkout_boat(
    boat_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    result = await db.execute(
        select(models.Boat)
        .where(models.Boat.id == boat_id)
        .where(models.Boat.boathouse_id == current_user.boathouse_id)
    )
    boat = result.scalar_one_or_none()
    if not boat:
        raise HTTPException(status_code=404, detail="Boat not found")
    if boat.status != models.BoatStatus.available:
        raise HTTPException(status_code=400, detail="Boat not available")

    # ✅ Check if the boat has a current reservation
    now = datetime.utcnow()
    conflict = await db.execute(
        select(models.Reservation)
        .where(models.Reservation.boat_id == boat.id)
        .where(models.Reservation.status == "confirmed")
        .where(models.Reservation.start_time <= now)
        .where(models.Reservation.end_time >= now)
    )
    if conflict.scalars().first():
        raise HTTPException(status_code=403, detail="Boat is currently reserved and cannot be checked out.")

    boat.status = models.BoatStatus.checked_out
    await db.commit()
    return {"message": f"Boat '{boat.name}' checked out successfully"}
