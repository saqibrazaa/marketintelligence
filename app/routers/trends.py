"""
GET /trends — Trending keywords analysis.
"""
from fastapi import APIRouter, Query, HTTPException
from app.services.analyzer import get_trending_keywords
from app.utils.logger import get_logger

router = APIRouter(tags=["Trends"])
log = get_logger(__name__)


@router.get("/trends")
async def trends(
    period: str = Query("7d", regex="^(24h|7d|30d)$", description="Time period: 24h, 7d, or 30d"),
    limit: int = Query(20, ge=1, le=100, description="Max keywords to return"),
):
    """
    Get trending keywords with frequency and sentiment.
    """
    try:
        results = get_trending_keywords(period, limit)
        return {
            "period": period,
            "total": len(results),
            "keywords": results,
        }
    except Exception as exc:
        log.error("Trends endpoint error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))
