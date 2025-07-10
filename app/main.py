from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import async_session, get_db
from app.routers import auth, users, boats, reservations, query  # already actual routers
from app.models import Base
from sqlalchemy.ext.asyncio import AsyncEngine
from app.database import engine

app = FastAPI(title="ShellSync - Multi-Boathouse Rowing Checkout System")

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all the route modules
app.include_router(auth)
app.include_router(users)
app.include_router(boats)
app.include_router(reservations)
app.include_router(query)  # ✅ no more .router

@app.get("/")
def read_root():
    return {"message": "Welcome to ShellSync!"}
