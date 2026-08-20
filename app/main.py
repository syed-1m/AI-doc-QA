from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.database import get_db

app = FastAPI(title=settings.app_name)


@app.get("/health")
async def health_check():
    return {"status": "ok", "environment": settings.environment}


@app.get("/health/db")
async def health_check_db(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT 1"))
    return {"status": "ok", "db_result": result.scalar()}