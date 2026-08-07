from sqlalchemy.orm import Session
from app.repositories.base import CRUDBase
from app.models.domain import Domain
from app.schemas.domain import DomainCreate, DomainUpdate

class CRUDDomain(CRUDBase[Domain, DomainCreate, DomainUpdate]):
    def create(self, db: Session, *, obj_in: DomainCreate) -> Domain:
        existing = db.query(self.model).filter(self.model.url == obj_in.url).first()
        if existing:
            return existing
        return super().create(db, obj_in=obj_in)

domain_repo = CRUDDomain(Domain)
