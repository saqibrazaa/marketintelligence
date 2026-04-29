"""
FastAPI Application — AI-Powered Market Intelligence Platform
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from app.routers import ingest, trends, insights, search, analytics
from app.utils.logger import get_logger

log = get_logger("market_intelligence")

# ── App Setup ──────────────────────────────────────────────────────

app = FastAPI(
    title="AI-Powered Market Intelligence",
    description=(
        "A comprehensive market intelligence platform that ingests news articles, "
        "processes them with NLP (keyword extraction, sentiment analysis), and "
        "provides actionable insights through analytics APIs and a modern dashboard."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ────────────────────────────────────────────────────────

app.include_router(ingest.router, prefix="/api")
app.include_router(trends.router, prefix="/api")
app.include_router(insights.router, prefix="/api")
app.include_router(search.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")

# ── Static Files (Frontend) ───────────────────────────────────────

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.isdir(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/", include_in_schema=False)
async def serve_frontend():
    """Serve the frontend dashboard."""
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.isfile(index_path):
        return FileResponse(index_path)
    return {"message": "AI-Powered Market Intelligence API", "docs": "/docs"}


# ── Startup ────────────────────────────────────────────────────────

@app.on_event("startup")
async def startup():
    log.info("🚀 Market Intelligence API starting up …")
    try:
        from app.database import get_client
        get_client()
        log.info("✓ All systems ready")
    except Exception as exc:
        log.warning("⚠ MongoDB not available: %s — API will start but DB operations will fail", exc)


@app.on_event("shutdown")
async def shutdown():
    log.info("🛑 Market Intelligence API shutting down …")


# ── Health Check ───────────────────────────────────────────────────

@app.get("/health", tags=["System"])
async def health_check():
    """Basic health check endpoint."""
    try:
        from app.database import get_client
        get_client().admin.command("ping")
        db_status = "connected"
    except Exception:
        db_status = "disconnected"

    return {
        "status": "ok",
        "database": db_status,
        "version": "1.0.0",
    }
