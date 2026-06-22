from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.core.config import settings
from app.db.database import Base, engine
from app.api.routes import auth, ideas, analysis, reports, dashboard
import logging
import sys

logger = logging.getLogger(__name__)

# Check OpenAI API key configuration
api_key_config_warning = False
if not settings.openai_api_key or \
   "replace-with-real-key" in settings.openai_api_key or \
   "sk-test" in settings.openai_api_key or \
   settings.openai_api_key.strip() == "":
    logger.warning("=" * 80)
    logger.warning("CONFIGURATION WARNING: OpenAI API Key")
    logger.warning("=" * 80)
    logger.warning("Invalid or placeholder OPENAI_API_KEY detected in .env file")
    logger.warning("Current value: %s", settings.openai_api_key[:20] + "..." if settings.openai_api_key else "EMPTY")
    logger.warning("")
    logger.warning("NOTE: AI analysis features require a valid API key:")
    logger.warning("1. Get a valid key from https://platform.openai.com/api-keys")
    logger.warning("2. Update backend/.env with: OPENAI_API_KEY=sk-...")
    logger.warning("3. Restart the application")
    logger.warning("")
    logger.warning("Application starting in DEMO MODE - AI features will fail gracefully")
    logger.warning("=" * 80)
    api_key_config_warning = True
else:
    logger.info("✓ Valid OpenAI API key configuration detected")

# Create tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered business idea validator",
    debug=settings.debug
)

# Rate Limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request, exc):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Maximum 100 requests per minute allowed."}
    )

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "app": settings.app_name}

# Include routers
app.include_router(
    auth.router,
    prefix=f"{settings.api_v1_prefix}/auth",
    tags=["Authentication"]
)

app.include_router(
    ideas.router,
    prefix=f"{settings.api_v1_prefix}/ideas",
    tags=["Ideas"]
)

app.include_router(
    analysis.router,
    prefix=f"{settings.api_v1_prefix}/analysis",
    tags=["Analysis"]
)

app.include_router(
    reports.router,
    tags=["Reports"]
)

app.include_router(
    dashboard.router,
    tags=["Dashboard"]
)

# root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "api_prefix": settings.api_v1_prefix
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
