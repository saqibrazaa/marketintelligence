"""
Application configuration — loads settings from .env
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    NEWS_API_KEY: str = os.getenv("NEWS_API_KEY", "")
    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "market_intelligence")
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    NEWS_API_BASE_URL: str = "https://newsapi.org/v2"


settings = Settings()
