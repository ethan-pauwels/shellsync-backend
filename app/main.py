from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import async_session, get_db
from app.routers import auth, users, boats, reservations, query  # ⬅️ added query
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
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(boats.router)
app.include_router(reservations.router)
app.include_router(query.router)  # ⬅️ mount query endpoint

@app.get("/")
def read_root():
    return {"message": "Welcome to ShellSync!"}
