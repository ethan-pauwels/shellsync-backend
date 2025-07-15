import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import asyncio

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_async_engine(DATABASE_URL, echo=True)

async def update_enum():
    print("🔧 Connecting to database...")
    async with engine.begin() as conn:
        await conn.execute(text("""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_enum
                    WHERE enumlabel = 'checked_out'
                    AND enumtypid = (
                        SELECT oid FROM pg_type WHERE typname = 'boatstatus'
                    )
                ) THEN
                    ALTER TYPE boatstatus ADD VALUE 'checked_out';
                END IF;
            END
            $$;
        """))
        print("✅ 'checked_out' added if it was missing.")

asyncio.run(update_enum())
