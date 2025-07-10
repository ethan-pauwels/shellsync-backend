# create_tables.py
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv
from app.models import Base

# Load environment variables
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Strip +asyncpg to use sync psycopg2 connection
DATABASE_URL = DATABASE_URL.replace("+asyncpg", "")

# Create sync engine
engine = create_engine(DATABASE_URL, echo=True)

def init_models():
    Base.metadata.create_all(engine)
    print("✅ Tables created (sync mode)")

if __name__ == "__main__":
    init_models()
