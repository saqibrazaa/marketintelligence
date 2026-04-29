"""
Pydantic models for request/response validation.
"""
from pydantic import BaseModel, Field
from typing import Optional


# ── Request Models ─────────────────────────────────────────────────

class IngestRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=200, description="Search query for news articles")
    page_size: int = Field(50, ge=1, le=100, description="Number of articles to fetch")
    from_date: Optional[str] = Field(None, description="Start date (YYYY-MM-DD)")
    to_date: Optional[str] = Field(None, description="End date (YYYY-MM-DD)")


# ── Response Models ────────────────────────────────────────────────

class SentimentInfo(BaseModel):
    label: str
    polarity: float
    subjectivity: float


class ArticleResponse(BaseModel):
    title: str
    description: str
    source: str
    author: str
    url: str
    published_at: str
    keywords: list[str] = []
    sentiment: SentimentInfo
    trend_score: float


class TrendItem(BaseModel):
    keyword: str
    count: int
    avg_trend_score: float
    avg_sentiment: float


class SentimentSummary(BaseModel):
    positive: int
    negative: int
    neutral: int
    total: int
    avg_polarity: float


class TimeSeriesPoint(BaseModel):
    date: str
    count: int
    avg_sentiment: float
    growth_pct: float


class SourceCount(BaseModel):
    source: str
    count: int


class QueryCount(BaseModel):
    query: str
    count: int


class AnalyticsSummary(BaseModel):
    total_articles: int
    articles_last_24h: int
    avg_trend_score: float
    avg_sentiment: float
    top_sources: list[SourceCount]
    top_queries: list[QueryCount]
    trends_24h: list[TrendItem]
    trends_7d: list[TrendItem]
    sentiment_distribution: SentimentSummary
    time_series: list[TimeSeriesPoint]


class PaginatedResponse(BaseModel):
    items: list
    total: int
    page: int
    page_size: int
    total_pages: int


class IngestResponse(BaseModel):
    message: str
    articles_fetched: int
    articles_processed: int
    query: str


class InsightResponse(BaseModel):
    sentiment: SentimentSummary
    trending_keywords: list[TrendItem]
    time_series: list[TimeSeriesPoint]
    summary: str
