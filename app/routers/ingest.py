"""
POST /ingest — Fetch, store, and process news articles.
"""
from fastapi import APIRouter, BackgroundTasks, HTTPException
from app.models import IngestRequest, IngestResponse
from app.services.news_fetcher import fetch_news
from app.services.data_processor import process_articles
from app.database import get_collection, RAW_DATA, PROCESSED_DATA
from app.utils.logger import get_logger

router = APIRouter(tags=["Ingestion"])
log = get_logger(__name__)


def _run_ingestion(query: str, page_size: int, from_date, to_date):
    """Background ingestion task."""
    try:
        articles = fetch_news(query, from_date, to_date, page_size)
        if not articles:
            log.warning("No articles fetched for query='%s'", query)
            return 0, 0

        # Store raw data
        raw_col = get_collection(RAW_DATA)
        raw_col.insert_many(articles)
        log.info("Stored %d raw articles", len(articles))

        # Process and store
        processed = process_articles(articles)
        if processed:
            proc_col = get_collection(PROCESSED_DATA)
            proc_col.insert_many(processed)
            log.info("Stored %d processed articles", len(processed))

        return len(articles), len(processed)
    except Exception as exc:
        log.error("Ingestion failed: %s", exc)
        return 0, 0


@router.post("/ingest", response_model=IngestResponse)
async def ingest_articles(req: IngestRequest, background_tasks: BackgroundTasks):
    """
    Fetch news articles, store raw data, process and store insights.

    Optionally runs additional background ingestion for related queries.
    """
    try:
        articles = fetch_news(req.query, req.from_date, req.to_date, req.page_size)

        if not articles:
            raise HTTPException(status_code=404, detail="No articles found for the given query")

        # Store raw data
        raw_col = get_collection(RAW_DATA)
        raw_col.insert_many(articles)

        # Process and store
        processed = process_articles(articles)
        if processed:
            proc_col = get_collection(PROCESSED_DATA)
            proc_col.insert_many(processed)

        # Schedule background task for related queries
        related_queries = [f"{req.query} market", f"{req.query} industry"]
        for rq in related_queries:
            background_tasks.add_task(_run_ingestion, rq, 20, req.from_date, req.to_date)

        return IngestResponse(
            message="Ingestion successful",
            articles_fetched=len(articles),
            articles_processed=len(processed),
            query=req.query,
        )

    except HTTPException:
        raise
    except Exception as exc:
        log.error("Ingestion endpoint error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))
