"""
GET /search — Full-text search across processed articles.
"""
import math
from fastapi import APIRouter, Query, HTTPException
from app.database import get_collection, PROCESSED_DATA
from app.utils.logger import get_logger

router = APIRouter(tags=["Search"])
log = get_logger(__name__)


@router.get("/search")
async def search_articles(
    q: str = Query(..., min_length=1, max_length=200, description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=50, description="Results per page"),
    sort_by: str = Query("trend_score", regex="^(trend_score|published_at|sentiment\\.polarity)$"),
):
    """
    Search processed articles by title, content, or keywords.
    Supports pagination and sorting.
    """
    try:
        col = get_collection(PROCESSED_DATA)

        # Build search filter — regex-based text search
        search_filter = {
            "$or": [
                {"title": {"$regex": q, "$options": "i"}},
                {"content": {"$regex": q, "$options": "i"}},
                {"keywords": {"$regex": q, "$options": "i"}},
                {"source": {"$regex": q, "$options": "i"}},
            ]
        }

        # Count total results
        total = col.count_documents(search_filter)
        total_pages = math.ceil(total / page_size) if total > 0 else 1

        # Sort direction
        sort_dir = -1  # descending
        sort_field = sort_by

        # Fetch paginated results
        skip = (page - 1) * page_size
        cursor = col.find(search_filter, {"_id": 0}).sort(sort_field, sort_dir).skip(skip).limit(page_size)
        items = list(cursor)

        return {
            "query": q,
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        }

    except Exception as exc:
        log.error("Search endpoint error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))
