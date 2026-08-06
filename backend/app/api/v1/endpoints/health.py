from fastapi import APIRouter
from app.core.config import settings

router = APIRouter()

@router.get("", response_model=dict)
def health():
    return {
        "status": "healthy",
        "version": settings.PROJECT_VERSION
    }

@router.get("/ready", response_model=dict)
def ready():
    return {
        "status": "ready",
        "checks": {
            "app": "ok"
        }
    }

@router.get("/live", response_model=dict)
def live():
    return {
        "status": "alive"
    }
