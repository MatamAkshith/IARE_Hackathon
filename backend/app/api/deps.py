from typing import Generator
from app.db.session import SessionLocal

from app.repositories import (
    domain_repo,
    scan_repo,
    campaign_repo,
    feature_repo,
    risk_score_repo,
)

def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
