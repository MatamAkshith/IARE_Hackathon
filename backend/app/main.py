from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import setup_logging
from app.api.router import api_router
from app.middleware.request_id import RequestIDMiddleware
from app.middleware.logging_middleware import LoggingMiddleware

# Initialize logging before FastAPI app instantiation
setup_logging()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="Enterprise Phishing & Brand Impersonation Detection Platform"
)

# CORS Middleware (added first, meaning it wraps everything else and runs first/last)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging and Request ID Middlewares
# Added in this order so that RequestIDMiddleware executes first on incoming requests
app.add_middleware(LoggingMiddleware)
app.add_middleware(RequestIDMiddleware)

app.include_router(api_router)
