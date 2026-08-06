# Import all the models, so that Base has them before being
# imported by Alembic target_metadata
from app.db.base_class import Base  # noqa
