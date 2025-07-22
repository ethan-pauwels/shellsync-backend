from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from passlib.context import CryptContext
from jose import JWTError, jwt
from app.database import get_db
from app import models
import os

router = APIRouter(prefix="/users", tags=["users"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ✅ Create new user (now supports role)
@router.post("/")
async def create_user(
    name: str,
    email: str,
    password: str,
    boathouse_id: int,
    role: str = "member",  # 👈 default role is 'member'
    db: AsyncSession = Depends(get_db)
):
    existing_user = await db.execute(select(models.User).where(models.User.email == email))
    if existing_user.scalars().first():
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = pwd_context.hash(password)
    user = models.User(
        name=name,
        email=email,
        password_hash=hashed_password,
        boathouse_id=boathouse_id,
        role=role  # 👈 set the role
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return {
        "id": user.id,
        "email": user.email,
        "boathouse_id": user.boathouse_id,
        "role": user.role  # 👈 return role
    }

# ✅ Get current user from token
from fastapi.security import OAuth2PasswordBearer
from app.utils import get_current_user

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

@router.get("/me")
async def read_users_me(current_user: models.User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "boathouse_id": current_user.boathouse_id,
        "role": current_user.role
    }

# ✅ TEMP ROUTE to promote yourself back to admin
@router.post("/promote-me")
async def promote_me(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.User).where(models.User.email == "ethanpauwels@gmail.com"))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.role = "admin"
    await db.commit()
    return {"message": f"{user.email} promoted to admin"}
