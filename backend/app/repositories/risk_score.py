from app.repositories.base import CRUDBase
from app.models.risk_score import RiskScore
from app.schemas.risk_score import RiskScoreCreate, RiskScoreUpdate

class CRUDRiskScore(CRUDBase[RiskScore, RiskScoreCreate, RiskScoreUpdate]):
    pass

risk_score_repo = CRUDRiskScore(RiskScore)
