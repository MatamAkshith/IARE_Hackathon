from app.repositories.base import CRUDBase
from app.models.feature import Feature
from app.schemas.feature import FeatureCreate, FeatureUpdate

class CRUDFeature(CRUDBase[Feature, FeatureCreate, FeatureUpdate]):
    pass

feature_repo = CRUDFeature(Feature)
