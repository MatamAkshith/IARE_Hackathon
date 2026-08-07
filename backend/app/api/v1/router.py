from fastapi import APIRouter
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.domains import router as domains_router
from app.api.v1.endpoints.scans import router as scans_router
from app.api.v1.endpoints.campaigns import router as campaigns_router
from app.api.v1.endpoints.features import router as features_router
from app.api.v1.endpoints.risk_scores import router as risk_scores_router
from app.api.v1.endpoints.extraction import router as extraction_router
from app.api.v1.endpoints.threat_intel import router as threat_intel_router
from app.api.v1.endpoints.unified_evidence import router as unified_evidence_router
from app.api.v1.endpoints.risk import router as risk_router
from app.api.v1.endpoints.ai_assistant import router as ai_assistant_router
from app.api.v1.endpoints.investigations import router as investigations_router

v1_router = APIRouter()
v1_router.include_router(health_router, prefix="/health", tags=["Health"])
v1_router.include_router(domains_router, prefix="/domains", tags=["Domains"])
v1_router.include_router(scans_router, prefix="/scans", tags=["Scans"])
# Campaign Correlation Engine
v1_router.include_router(campaigns_router, prefix="/campaigns", tags=["Campaigns"])
v1_router.include_router(features_router, prefix="/features", tags=["Features"])
v1_router.include_router(risk_scores_router, prefix="/risk-scores", tags=["Risk Scores"])
v1_router.include_router(extraction_router, prefix="/extract", tags=["Feature Extraction"])
v1_router.include_router(threat_intel_router, prefix="/threat-intel", tags=["Threat Intelligence"])
v1_router.include_router(unified_evidence_router, prefix="/unified-evidence", tags=["Unified Evidence"])
v1_router.include_router(risk_router, prefix="/risk", tags=["Risk Engine"])
v1_router.include_router(ai_assistant_router, prefix="/ai", tags=["AI Assistant"])
v1_router.include_router(investigations_router, prefix="/investigations", tags=["Investigations"])






