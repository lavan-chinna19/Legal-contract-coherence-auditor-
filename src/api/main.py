"""
src/api/main.py — FastAPI application entry point with Security & Hardening (Prompt 16)
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.api.v1.router import router as v1_router
from src.api.dependencies import get_ml_segmenter, get_dual_channel_scorer
from src.api.retention import cleanup_expired_artifacts

# Configure logging (Rule 4: Confidentiality)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: run data retention startup cleanup."""
    try:
        cleanup_expired_artifacts()
    except Exception as e:
        logger.warning(f"Startup retention cleanup encountered an issue: {e}")
    yield


app = FastAPI(
    title="Legal Contract Coherence Auditor API",
    version="1.0.0",
    description="API for dual-channel anomaly scoring pipeline with Prompt 16 security hardening.",
    lifespan=lifespan
)

app.include_router(v1_router)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Middleware to log requests while respecting confidentiality.
    We NEVER log request bodies or authorization headers to prevent plaintext/token leakage.
    """
    logger.info(f"Incoming request: {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"Request completed: {request.method} {request.url.path} - Status: {response.status_code}")
    return response


@app.get("/health", tags=["System"])
async def health_check():
    """Lightweight liveness check (Unauthenticated, Gate 1)."""
    return {"status": "ok"}


@app.get("/ready", tags=["System"])
async def readiness_check():
    """
    Checks if dependencies (Segmenter, Models) can be loaded.
    Unauthenticated system check.
    """
    try:
        get_ml_segmenter()
        get_dual_channel_scorer()
        return {"status": "ready"}
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        return JSONResponse(status_code=503, content={"status": "not_ready", "error": str(e)})
