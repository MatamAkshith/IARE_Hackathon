from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.config import settings
from app.api.deps import get_db

router = APIRouter()

@router.get("", response_model=dict)
def health():
    return {
        "status": "healthy",
        "version": settings.PROJECT_VERSION
    }

@router.get("/ready", response_model=dict)
def ready(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "ready",
            "checks": {
                "app": "ok",
                "database": "ok"
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {str(e)}"
        )

@router.get("/live", response_model=dict)
def live():
    return {
        "status": "alive"
    }
