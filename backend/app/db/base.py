# Import all the models, so that Base has them before being
# imported by Alembic target_metadata
from app.db.base_class import Base  # noqa
from app.models.domain import Domain  # noqa
from app.models.campaign import Campaign  # noqa
from app.models.scan import Scan  # noqa
from app.models.feature import Feature  # noqa
from app.models.risk_score import RiskScore  # noqa
