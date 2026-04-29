"""
MongoDB connection manager.
"""
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from app.config import settings
from app.utils.logger import get_logger

log = get_logger(__name__)

_client: MongoClient | None = None


def get_client() -> MongoClient:
    """Return a singleton MongoClient."""
    global _client
    if _client is None:
        log.info("Connecting to MongoDB at %s …", settings.MONGODB_URI)
        _client = MongoClient(settings.MONGODB_URI, serverSelectionTimeoutMS=5000)
        # Verify the connection
        try:
            _client.admin.command("ping")
            log.info("MongoDB connection successful ✓")
        except ConnectionFailure as exc:
            log.error("MongoDB connection failed: %s", exc)
            raise
    return _client


def get_database():
    """Return the application database."""
    return get_client()[settings.DATABASE_NAME]


def get_collection(name: str):
    """Return a specific collection."""
    return get_database()[name]


# Collection name constants
RAW_DATA = "raw_data"
PROCESSED_DATA = "processed_data"
