import logging
from app.db.engine import engine
from app.db.base import Base

logger = logging.getLogger("app.db.init_db")

def init_models():
    logger.info("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized successfully.")
