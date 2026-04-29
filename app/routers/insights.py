"""
GET /insights — Sentiment analysis & combined insights.
"""
from fastapi import APIRouter, Query, HTTPException
from app.services.analyzer import get_sentiment_distribution, get_trending_keywords, get_time_series
from app.utils.logger import get_logger

router = APIRouter(tags=["Insights"])
log = get_logger(__name__)


@router.get("/insights")
async def insights(
    period: str = Query("7d", regex="^(24h|7d|30d)$", description="Time period"),
):
    """
    Get combined insights: sentiment distribution, top trends, and time series.
    """
    try:
        sentiment = get_sentiment_distribution(period)
        keywords = get_trending_keywords(period, 10)
        ts = get_time_series(period)

        # Generate summary text
        dominant = max(["positive", "negative", "neutral"], key=lambda k: sentiment.get(k, 0))
        summary = (
            f"Over the past {period}, {sentiment['total']} articles were analyzed. "
            f"Overall sentiment is {dominant} (avg polarity: {sentiment['avg_polarity']}). "
        )
        if keywords:
            top_kw = ", ".join(k["keyword"] for k in keywords[:5])
            summary += f"Top trending topics: {top_kw}."

        return {
            "period": period,
            "sentiment": sentiment,
            "trending_keywords": keywords,
            "time_series": ts,
            "summary": summary,
        }
    except Exception as exc:
        log.error("Insights endpoint error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))
