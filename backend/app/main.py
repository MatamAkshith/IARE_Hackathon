from fastapi import FastAPI
from app.api.router import api_router

app = FastAPI(
    title="ThreatLens API",
    version="0.1.0",
    description="Enterprise Phishing & Brand Impersonation Detection Platform"
)

app.include_router(api_router)
