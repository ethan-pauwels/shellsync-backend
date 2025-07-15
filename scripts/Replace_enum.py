from sqlalchemy import create_engine, text

# Use your external DB URL
DATABASE_URL = "postgresql://shellsync_db_user:DZxVMoPM6463j9WzwfX2LzTkYxKiaBEa@dpg-d110rq6mcj7s739o28k0-a.oregon-postgres.render.com/shellsync_db"

engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    print("🚀 Connected to database. Replacing enum...")

    conn.execute(text("ALTER TYPE boatstatus RENAME TO boatstatus_old;"))

    conn.execute(text(
        "CREATE TYPE boatstatus AS ENUM ('available', 'reserved', 'maintenance', 'checked_out');"
    ))

    conn.execute(text(
        "ALTER TABLE boats ALTER COLUMN status TYPE boatstatus USING status::text::boatstatus;"
    ))

    conn.execute(text("DROP TYPE boatstatus_old;"))

    print("✅ Enum replaced with 'checked_out' value.")
