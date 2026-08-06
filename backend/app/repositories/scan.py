from app.repositories.base import CRUDBase
from app.models.scan import Scan
from app.schemas.scan import ScanCreate, ScanUpdate

class CRUDScan(CRUDBase[Scan, ScanCreate, ScanUpdate]):
    pass

scan_repo = CRUDScan(Scan)
