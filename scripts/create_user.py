# scripts/create_user.py

import sys
import os
import asyncio

# Add the parent directory (your project root) to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import async_session
from app.models import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_user():
    async with async_session() as session:
        user = User(
            name="Ethan Pauwels",
            email="ethanpauwels@gmail.com",
            password_hash=pwd_context.hash("boats123"),
            boathouse_id=1,
            role="admin"  # or "member" if you prefer
        )
        session.add(user)
        await session.commit()
        print("✅ User created: test@example.com")

if __name__ == "__main__":
    asyncio.run(create_user())
