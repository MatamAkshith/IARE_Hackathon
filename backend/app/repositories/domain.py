from app.repositories.base import CRUDBase
from app.models.domain import Domain
from app.schemas.domain import DomainCreate, DomainUpdate

class CRUDDomain(CRUDBase[Domain, DomainCreate, DomainUpdate]):
    pass

domain_repo = CRUDDomain(Domain)
