from fastapi import APIRouter, Request, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import async_session

router = APIRouter()

@router.post("/query")
async def run_query(request: Request):
    data = await request.json()
    query = data.get("query")

    if not query:
        raise HTTPException(status_code=400, detail="No query provided.")

    try:
        async with async_session() as session:
            result = await session.execute(text(query.strip()))

            # If it's a SELECT, return the rows
            if query.strip().lower().startswith("select"):
                rows = result.mappings().all()
                return {"rows": rows}
            else:
                await session.commit()
                return {"message": "✅ Query executed successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")
