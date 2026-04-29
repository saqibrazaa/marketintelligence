"""
Analysis engine — trend detection, sentiment aggregation, time series.
"""
from datetime import datetime, timedelta
from app.database import get_collection, PROCESSED_DATA
from app.utils.logger import get_logger

log = get_logger(__name__)


def get_trending_keywords(period: str = "7d", limit: int = 20) -> list[dict]:
    """
    Get top keywords from processed articles within a time period.

    period: "24h" | "7d" | "30d"
    Returns: [{keyword, count, trend_score_avg}]
    """
    hours_map = {"24h": 24, "7d": 168, "30d": 720}
    hours = hours_map.get(period, 168)
    cutoff = (datetime.utcnow() - timedelta(hours=hours)).isoformat()

    col = get_collection(PROCESSED_DATA)

    pipeline = [
        {"$match": {"processed_at": {"$gte": cutoff}}},
        {"$unwind": "$keywords"},
        {
            "$group": {
                "_id": "$keywords",
                "count": {"$sum": 1},
                "avg_trend_score": {"$avg": "$trend_score"},
                "avg_sentiment": {"$avg": "$sentiment.polarity"},
            }
        },
        {"$sort": {"count": -1}},
        {"$limit": limit},
        {
            "$project": {
                "_id": 0,
                "keyword": "$_id",
                "count": 1,
                "avg_trend_score": {"$round": ["$avg_trend_score", 2]},
                "avg_sentiment": {"$round": ["$avg_sentiment", 4]},
            }
        },
    ]

    results = list(col.aggregate(pipeline))
    log.info("Trending keywords (%s): %d results", period, len(results))
    return results


def get_sentiment_distribution(period: str = "7d") -> dict:
    """
    Count positive / negative / neutral articles.

    Returns: {positive, negative, neutral, total, avg_polarity}
    """
    hours_map = {"24h": 24, "7d": 168, "30d": 720}
    hours = hours_map.get(period, 168)
    cutoff = (datetime.utcnow() - timedelta(hours=hours)).isoformat()

    col = get_collection(PROCESSED_DATA)

    pipeline = [
        {"$match": {"processed_at": {"$gte": cutoff}}},
        {
            "$group": {
                "_id": "$sentiment.label",
                "count": {"$sum": 1},
                "avg_polarity": {"$avg": "$sentiment.polarity"},
            }
        },
    ]

    results = list(col.aggregate(pipeline))

    dist = {"positive": 0, "negative": 0, "neutral": 0, "total": 0, "avg_polarity": 0.0}
    total_polarity = 0.0
    for r in results:
        label = r["_id"]
        count = r["count"]
        if label in dist:
            dist[label] = count
        dist["total"] += count
        total_polarity += r["avg_polarity"] * count

    if dist["total"] > 0:
        dist["avg_polarity"] = round(total_polarity / dist["total"], 4)

    log.info("Sentiment distribution (%s): %s", period, dist)
    return dist


def get_time_series(period: str = "7d") -> list[dict]:
    """
    Articles per day with growth trend.

    Returns: [{date, count, growth_pct}]
    """
    hours_map = {"24h": 24, "7d": 168, "30d": 720}
    hours = hours_map.get(period, 168)
    cutoff = (datetime.utcnow() - timedelta(hours=hours)).isoformat()

    col = get_collection(PROCESSED_DATA)

    pipeline = [
        {"$match": {"processed_at": {"$gte": cutoff}}},
        {
            "$addFields": {
                "pub_date": {
                    "$substr": ["$published_at", 0, 10]   # "YYYY-MM-DD"
                }
            }
        },
        {
            "$group": {
                "_id": "$pub_date",
                "count": {"$sum": 1},
                "avg_sentiment": {"$avg": "$sentiment.polarity"},
            }
        },
        {"$sort": {"_id": 1}},
        {
            "$project": {
                "_id": 0,
                "date": "$_id",
                "count": 1,
                "avg_sentiment": {"$round": ["$avg_sentiment", 4]},
            }
        },
    ]

    results = list(col.aggregate(pipeline))

    # Calculate growth percentages
    for i, day in enumerate(results):
        if i == 0:
            day["growth_pct"] = 0.0
        else:
            prev = results[i - 1]["count"]
            if prev > 0:
                day["growth_pct"] = round(((day["count"] - prev) / prev) * 100, 2)
            else:
                day["growth_pct"] = 0.0

    log.info("Time series (%s): %d data points", period, len(results))
    return results


def get_analytics_summary() -> dict:
    """
    Comprehensive analytics summary combining all analysis.
    """
    col = get_collection(PROCESSED_DATA)
    total_articles = col.count_documents({})

    # Recent articles (24h)
    cutoff_24h = (datetime.utcnow() - timedelta(hours=24)).isoformat()
    recent_count = col.count_documents({"processed_at": {"$gte": cutoff_24h}})

    # Top sources
    source_pipeline = [
        {"$group": {"_id": "$source", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10},
        {"$project": {"_id": 0, "source": "$_id", "count": 1}},
    ]
    top_sources = list(col.aggregate(source_pipeline))

    # Top queries
    query_pipeline = [
        {"$group": {"_id": "$query", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10},
        {"$project": {"_id": 0, "query": "$_id", "count": 1}},
    ]
    top_queries = list(col.aggregate(query_pipeline))

    # Average trend score
    avg_pipeline = [
        {"$group": {"_id": None, "avg_trend": {"$avg": "$trend_score"}, "avg_sentiment": {"$avg": "$sentiment.polarity"}}},
    ]
    avg_result = list(col.aggregate(avg_pipeline))
    avg_trend = round(avg_result[0]["avg_trend"], 2) if avg_result else 0.0
    avg_sentiment = round(avg_result[0]["avg_sentiment"], 4) if avg_result else 0.0

    return {
        "total_articles": total_articles,
        "articles_last_24h": recent_count,
        "avg_trend_score": avg_trend,
        "avg_sentiment": avg_sentiment,
        "top_sources": top_sources,
        "top_queries": top_queries,
        "trends_24h": get_trending_keywords("24h", 10),
        "trends_7d": get_trending_keywords("7d", 10),
        "sentiment_distribution": get_sentiment_distribution("7d"),
        "time_series": get_time_series("7d"),
    }
