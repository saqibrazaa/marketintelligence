"""
GET /analytics/summary — Comprehensive analytics dashboard data.
"""
from fastapi import APIRouter, HTTPException
from app.services.analyzer import get_analytics_summary
from app.utils.logger import get_logger

router = APIRouter(tags=["Analytics"])
log = get_logger(__name__)


@router.get("/analytics/summary")
async def analytics_summary():
    """
    Get a comprehensive analytics summary including:
    - Total articles & recent count
    - Top sources and queries
    - Trending keywords (24h & 7d)
    - Sentiment distribution
    - Time series data
    """
    try:
        summary = get_analytics_summary()
        return summary
    except Exception as exc:
        log.error("Analytics endpoint error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))
