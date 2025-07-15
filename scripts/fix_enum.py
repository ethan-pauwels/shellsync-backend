from sqlalchemy import create_engine, text

# Inside fix_enum.py
DATABASE_URL = "postgresql://shellsync_db_user:DZxVMoPM6463j9WzwfX2LzTkYxKiaBEa@dpg-d110rq6mcj7s739o28k0-a.oregon-postgres.render.com/shellsync_db"

engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    print("🔧 Connected to database. Checking enum values...")

    try:
        conn.execute(text("ALTER TYPE boatstatus ADD VALUE 'checked_out'"))
        print("✅ 'checked_out' added to boatstatus enum.")
    except Exception as e:
        if "already exists" in str(e):
            print("ℹ️ 'checked_out' already exists in enum. No action needed.")
        else:
            print("❌ Failed to alter enum:", e)
