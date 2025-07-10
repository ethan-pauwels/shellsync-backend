from fastapi import APIRouter, Request, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import async_session

router = APIRouter()

@router.post("/query")
async def run_query(request: Request):
    data = await request.json()
    query = data.get("query")

    # Only allow SELECT statements for safety
    if not query or not query.strip().lower().startswith("select"):
        raise HTTPException(status_code=400, detail="Only SELECT statements are allowed.")

    try:
        async with async_session() as session:
            result = await session.execute(text(query))
            rows = result.mappings().all()  # ✅ correct way to fetch dict-style rows
            return {"rows": rows}
    except Exception as e:
        # For debugging, you could log this or return it in dev mode
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")
