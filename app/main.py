from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncEngine

from app.database import async_session, get_db, engine
from app.models import Base
from app.routers import auth, users, boats, reservations, query

app = FastAPI(title="ShellSync - Multi-Boathouse Rowing Checkout System")

# ✅ CORS middleware to allow both deployed and preview Vercel frontend URLs
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://shellsync-frontend.vercel.app",  # main deployed frontend
        "https://shellsync-frontend-f4hejs116-ethan-pauwels-projects.vercel.app",  # Vercel preview/staging
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Register all routers
app.include_router(auth)
app.include_router(users)
app.include_router(boats)
app.include_router(reservations)
app.include_router(query)

@app.get("/")
def read_root():
    return {"message": "Welcome to ShellSync!"}
