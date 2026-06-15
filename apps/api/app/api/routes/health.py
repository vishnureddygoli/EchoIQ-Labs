from fastapi import APIRouter
from app.core.database import database_health
from app.core.redis_client import redis_health

router = APIRouter()

@router.get("/health")
def health():
    return {"api": "ok", "database": database_health(), "redis": redis_health()}
