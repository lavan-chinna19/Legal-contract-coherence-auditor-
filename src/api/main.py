"""
src/api/main.py — FastAPI application entry point with Security & Hardening (Prompt 16)
"""
import logging
import os
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.api.v1.router import router as v1_router
from src.api.release_routes import router as release_router
from src.api.upload_limits import UploadLimitMiddleware
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
    async def retention_loop():
        while True:
            await asyncio.sleep(300)
            await asyncio.to_thread(cleanup_expired_artifacts)
    retention_task = asyncio.create_task(retention_loop())
    try:
        yield
    finally:
        retention_task.cancel()
        try:
            await retention_task
        except asyncio.CancelledError:
            pass


from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Legal Contract Coherence Auditor API",
    version="1.0.0",
    description="API for dual-channel anomaly scoring pipeline with Prompt 16 security hardening.",
    lifespan=lifespan
)

# Enable CORS for frontend applications (Prompt 17)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[v.strip() for v in os.environ.get("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",") if v.strip()],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(UploadLimitMiddleware)

app.include_router(v1_router)
app.include_router(release_router)


@app.middleware("http")
async def private_response_headers(request: Request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/v1/"):
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
    return response


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
def readiness_check():
    """
    Checks if dependencies (Segmenter, Models) can be loaded.
    Unauthenticated system check.
    """
    try:
        get_ml_segmenter()
        scorer = get_dual_channel_scorer()
        if scorer.channel_a.centroid_matrix is None:
            raise RuntimeError("Missing centroid fixture")
        scorer.channel_a.embedder._load_model()
        return {"status": "ready"}
    except Exception as e:
        logger.error("Readiness check failed: local models or dependencies unavailable")
        return JSONResponse(status_code=503, content={"status": "not_ready", "error": "Local models or dependencies unavailable"})
