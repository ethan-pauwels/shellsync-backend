from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime
from app.database import get_db
from app import models
from app.utils import get_current_user
from app.models import BoatStatus  # ✅ Import enum for type safety

router = APIRouter(prefix="/boats", tags=["boats"])

# ✅ Get available boats for current user's boathouse
@router.get("/available")
async def get_available_boats(
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    result = await db.execute(
        select(models.Boat)
        .where(models.Boat.boathouse_id == current_user.boathouse_id)
        .where(models.Boat.status == models.BoatStatus.available)
    )
    boats = result.scalars().all()
    return boats

# 🔓 TEMP: Get all boats (no auth) for dev/testing
@router.get("/")
async def get_all_boats(
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(models.Boat))
    boats = result.scalars().all()
    return boats

# ✅ Admin: Add a new boat
@router.post("/")
async def add_boat(
    name: str,
    type: str,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can add boats")

    boat = models.Boat(name=name, type=type, boathouse_id=current_user.boathouse_id)
    db.add(boat)
    await db.commit()
    await db.refresh(boat)
    return boat

# ✅ Member/Admin: Check out a boat with reservation conflict check
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

# ✅ Member/Admin: Check in a boat
@router.post("/{boat_id}/checkin")
async def checkin_boat(
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
    if boat.status != models.BoatStatus.checked_out:
        raise HTTPException(status_code=400, detail="Boat is not currently checked out")

    boat.status = models.BoatStatus.available
    await db.commit()
    return {"message": f"Boat '{boat.name}' checked in successfully"}

# ✅ Admin: Update boat status (used by admin dashboard dropdown)
@router.patch("/{boat_id}")
async def update_boat_status(
    boat_id: int,
    status: BoatStatus = Query(...),
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

    boat.status = status
    await db.commit()
    return {"message": f"Boat status updated to '{status}'"}

# ✅ Admin: Delete boat (used by admin dashboard delete modal)
@router.delete("/{boat_id}")
async def delete_boat(
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

    await db.delete(boat)
    await db.commit()
    return {"message": f"Boat '{boat.name}' has been deleted."}

# ✅ Admin/Coach: Mark broken boat as fixed (set status to 'available')
@router.post("/{boat_id}/mark-fixed")
async def mark_boat_fixed(
    boat_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role not in ("admin", "coach"):
        raise HTTPException(status_code=403, detail="Only coaches or admins can mark boats as fixed")

    result = await db.execute(
        select(models.Boat)
        .where(models.Boat.id == boat_id)
        .where(models.Boat.boathouse_id == current_user.boathouse_id)
    )
    boat = result.scalar_one_or_none()
    if not boat:
        raise HTTPException(status_code=404, detail="Boat not found")

    boat.status = BoatStatus.available
    await db.commit()
    return {"message": f"Boat '{boat.name}' marked as fixed"}
