# app/main.py (FastAPI backend)

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.database import SessionLocal

app = FastAPI()

# Allow CORS for frontend testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your frontend domain in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/query")
async def run_query(request: Request):
    data = await request.json()
    query = data.get("query")

    # Basic protection: only allow SELECTs
    if not query or not query.strip().lower().startswith("select"):
        raise HTTPException(status_code=400, detail="Only SELECT statements are allowed.")

    session = SessionLocal()
    try:
        result = session.execute(text(query))
        rows = [dict(row._mapping) for row in result]  # SQLAlchemy row to dict
        return {"rows": rows}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()
