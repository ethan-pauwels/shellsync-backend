# seed_data.py

import pandas as pd
import os
from dotenv import load_dotenv, find_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, Boat, User, BoatStatus, Boathouse  # ⬅️ Added Boathouse
from passlib.context import CryptContext

# Load environment variables
load_dotenv(find_dotenv())
DATABASE_URL = os.getenv("DATABASE_URL")
print("Loaded DATABASE_URL:", DATABASE_URL)

# Use sync engine (strip +asyncpg from DATABASE_URL and add SSL mode)
DATABASE_URL = DATABASE_URL.replace("+asyncpg", "")
engine = create_engine(DATABASE_URL + "?sslmode=require", echo=True)

# Create tables
Base.metadata.create_all(engine)

SessionLocal = sessionmaker(bind=engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
DEFAULT_PASSWORD = "arc2024"

# Load CSVs
boats_df = pd.read_csv("Boat list for Ethan - BOATS.csv")
members_df = pd.read_csv("Mailing_List-22.csv")

# 🔧 Replace NaN in 'Brand' with None and convert to string
boats_df["Brand"] = boats_df["Brand"].apply(lambda x: str(x).strip() if pd.notna(x) else None)

def seed():
    print("🚧 Previewing boats CSV:")
    print(boats_df.head())

    print("🚧 Previewing members CSV:")
    print(members_df.head())

    session = SessionLocal()

    # ✅ Seed Boathouse if not exists
    existing_boathouse = session.query(Boathouse).filter_by(id=1).first()
    if not existing_boathouse:
        print("📦 Inserting boathouse ID=1 (Austin Rowing Club)")
        boathouse = Boathouse(
            id=1,
            name="Austin Rowing Club",
            contact_email="paddle@austinrowing.org",
            location="74 Trinity St, Austin TX"
        )
        session.add(boathouse)
        session.commit()

    # Seed Boats
    for _, row in boats_df.iterrows():
        try:
            print("Inserting boat:", row["Boat Name"])
            boat = Boat(
                name=row["Boat Name"],
                type=row["Type"],
                status=BoatStatus.available,
                brand=row["Brand"],
                boathouse_id=1
            )
            session.add(boat)
        except Exception as e:
            print(f"⚠️ Error inserting boat row: {row} — {e}")

    # Seed Users
    for _, row in members_df.iterrows():
        try:
            email = row.get("Email")
            if pd.isna(email):
                continue
            full_name = f"{row['First name']} {row['Last name']}"
            print("Inserting user:", full_name)
            hashed_pw = pwd_context.hash(DEFAULT_PASSWORD)
            user = User(
                name=full_name,
                email=email,
                password_hash=hashed_pw,
                role="rower",
                boathouse_id=1
            )
            session.add(user)
        except Exception as e:
            print(f"⚠️ Error inserting user row: {row} — {e}")

    session.commit()

    # Confirm how many were inserted
    boat_count = session.query(Boat).count()
    user_count = session.query(User).count()
    session.close()

    print(f"✅ Seeded {boat_count} boats and {user_count} members (sync mode)")

if __name__ == "__main__":
    seed()
