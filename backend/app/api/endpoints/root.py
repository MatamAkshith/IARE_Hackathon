from fastapi import APIRouter
from app.core.config import settings

router = APIRouter()

@router.get("/")
def read_root():
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT
    }
