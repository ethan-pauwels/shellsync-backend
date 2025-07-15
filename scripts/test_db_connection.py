import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import asyncio

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
print(f"📦 Loaded DATABASE_URL: {DATABASE_URL}")

async def test_connection():
    try:
        engine = create_async_engine(DATABASE_URL, echo=True)
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT current_database();"))
            db_name = result.scalar()
            print(f"✅ Connected successfully to database: {db_name}")
    except Exception as e:
        print("❌ Connection failed:", e)

asyncio.run(test_connection())
