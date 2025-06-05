from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app import models
from app.utils import get_current_user

router = APIRouter(prefix="/boats", tags=["boats"])

# Get list of available boats for current user's boathouse
@router.get("/available")
async def get_available_boats(db: AsyncSession = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    result = await db.execute(
        select(models.Boat)
        .where(models.Boat.boathouse_id == current_user.boathouse_id)
        .where(models.Boat.status == models.BoatStatus.available)
    )
    boats = result.scalars().all()
    return boats

# Admin: add a new boat
@router.post("/")
async def add_boat(name: str, type: str, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can add boats")

    boat = models.Boat(name=name, type=type, boathouse_id=current_user.boathouse_id)
    db.add(boat)
    await db.commit()
    await db.refresh(boat)
    return boat
