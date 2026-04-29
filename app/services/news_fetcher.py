"""
News API integration — fetch articles from NewsAPI.org
"""
import requests
from datetime import datetime, timedelta
from typing import Optional
from app.config import settings
from app.utils.logger import get_logger

log = get_logger(__name__)


def fetch_news(
    query: str = "technology",
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    page_size: int = 50,
    language: str = "en",
    sort_by: str = "publishedAt",
) -> list[dict]:
    """
    Fetch articles from NewsAPI /everything endpoint.

    Returns a list of article dicts ready for MongoDB insertion.
    """
    if not settings.NEWS_API_KEY or settings.NEWS_API_KEY == "YOUR_NEWS_API_KEY_HERE":
        log.warning("NEWS_API_KEY not set — returning demo data")
        return _demo_articles(query)

    if from_date is None:
        from_date = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d")
    if to_date is None:
        to_date = datetime.utcnow().strftime("%Y-%m-%d")

    url = f"{settings.NEWS_API_BASE_URL}/everything"
    params = {
        "q": query,
        "from": from_date,
        "to": to_date,
        "pageSize": min(page_size, 100),
        "language": language,
        "sortBy": sort_by,
        "apiKey": settings.NEWS_API_KEY,
    }

    log.info("Fetching news for query='%s' from %s to %s …", query, from_date, to_date)

    try:
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        if data.get("status") != "ok":
            log.error("NewsAPI error: %s", data.get("message", "unknown"))
            return []

        articles = []
        for art in data.get("articles", []):
            articles.append({
                "title": art.get("title", ""),
                "description": art.get("description", ""),
                "content": art.get("content", ""),
                "source": art.get("source", {}).get("name", "Unknown"),
                "author": art.get("author", "Unknown"),
                "url": art.get("url", ""),
                "image_url": art.get("urlToImage", ""),
                "published_at": art.get("publishedAt", ""),
                "fetched_at": datetime.utcnow().isoformat(),
                "query": query,
            })

        log.info("Fetched %d articles", len(articles))
        return articles

    except requests.RequestException as exc:
        log.error("Failed to fetch news: %s", exc)
        return []


def _demo_articles(query: str) -> list[dict]:
    """Return sample articles when no API key is configured."""
    now = datetime.utcnow()
    samples = [
        {
            "title": f"AI Revolution in {query.title()} Industry Accelerates",
            "description": f"Major breakthroughs in {query} are reshaping the industry landscape with unprecedented growth.",
            "content": f"The {query} sector is experiencing a transformative period driven by artificial intelligence and machine learning innovations. Companies are reporting significant improvements in efficiency and cost reduction. Market analysts predict continued growth through 2026, with investment in AI-powered solutions reaching new highs. Industry leaders emphasize the importance of adapting to these technological changes.",
            "source": "Tech Daily",
            "author": "Sarah Johnson",
            "url": "https://example.com/article-1",
            "image_url": "",
            "published_at": (now - timedelta(hours=2)).isoformat(),
            "fetched_at": now.isoformat(),
            "query": query,
        },
        {
            "title": f"Global Markets React to {query.title()} Trends",
            "description": f"Stock markets show strong positive sentiment toward {query}-related companies.",
            "content": f"Global financial markets are responding positively to developments in the {query} space. Investors are increasingly optimistic as key players announce strategic partnerships and product launches. Trading volumes have surged, reflecting growing confidence in the sector's long-term potential. Analysts note that consumer demand remains robust despite macroeconomic uncertainties.",
            "source": "Market Watch",
            "author": "Michael Chen",
            "url": "https://example.com/article-2",
            "image_url": "",
            "published_at": (now - timedelta(hours=5)).isoformat(),
            "fetched_at": now.isoformat(),
            "query": query,
        },
        {
            "title": f"Regulatory Changes Impact {query.title()} Sector",
            "description": f"New regulations could reshape how {query} companies operate globally.",
            "content": f"Regulatory bodies worldwide are introducing new frameworks that could significantly affect the {query} industry. These changes aim to balance innovation with consumer protection. Industry stakeholders are actively engaging with policymakers to ensure balanced regulation. The impact of these regulatory shifts is expected to create both challenges and opportunities for market participants.",
            "source": "Business Insider",
            "author": "Emma Williams",
            "url": "https://example.com/article-3",
            "image_url": "",
            "published_at": (now - timedelta(hours=8)).isoformat(),
            "fetched_at": now.isoformat(),
            "query": query,
        },
        {
            "title": f"Startups Disrupting the {query.title()} Market",
            "description": f"Innovative startups are challenging established players in the {query} arena.",
            "content": f"A new wave of startups is disrupting the traditional {query} market with innovative solutions. Venture capital funding has reached record levels, with investors betting on next-generation technologies. These companies are leveraging cloud computing, big data, and AI to deliver superior products. The competitive landscape is rapidly evolving as incumbents respond with their own digital transformation initiatives.",
            "source": "Startup Weekly",
            "author": "David Park",
            "url": "https://example.com/article-4",
            "image_url": "",
            "published_at": (now - timedelta(hours=12)).isoformat(),
            "fetched_at": now.isoformat(),
            "query": query,
        },
        {
            "title": f"Consumer Behavior Shifts in {query.title()} Domain",
            "description": f"Survey reveals changing consumer preferences in the {query} market.",
            "content": f"A comprehensive survey reveals significant shifts in consumer behavior within the {query} sector. Digital adoption continues to accelerate, with mobile-first experiences becoming the norm. Sustainability and ethical practices are increasingly influencing purchasing decisions. Brands that fail to adapt to these changing preferences risk losing market share to more agile competitors.",
            "source": "Consumer Trends",
            "author": "Lisa Anderson",
            "url": "https://example.com/article-5",
            "image_url": "",
            "published_at": (now - timedelta(days=1)).isoformat(),
            "fetched_at": now.isoformat(),
            "query": query,
        },
        {
            "title": f"Investment Opportunities in {query.title()} for 2026",
            "description": f"Analysts highlight top investment picks in the {query} sector.",
            "content": f"Financial analysts have identified promising investment opportunities in the {query} market for 2026. Key growth drivers include digital transformation, sustainability initiatives, and emerging market expansion. Portfolio managers recommend a diversified approach, combining established market leaders with high-growth potential players. Risk factors include geopolitical tensions and supply chain disruptions.",
            "source": "Finance Today",
            "author": "Robert Kim",
            "url": "https://example.com/article-6",
            "image_url": "",
            "published_at": (now - timedelta(days=1, hours=6)).isoformat(),
            "fetched_at": now.isoformat(),
            "query": query,
        },
        {
            "title": f"Sustainability Drives Innovation in {query.title()}",
            "description": f"Green initiatives are creating new opportunities in the {query} industry.",
            "content": f"Sustainability is becoming a core driver of innovation in the {query} sector. Companies are investing heavily in green technologies and sustainable practices to meet growing consumer demand and regulatory requirements. Carbon-neutral commitments and circular economy principles are reshaping business models. Industry experts predict that sustainability-focused companies will outperform peers in the long term.",
            "source": "Green Review",
            "author": "Anna Martinez",
            "url": "https://example.com/article-7",
            "image_url": "",
            "published_at": (now - timedelta(days=2)).isoformat(),
            "fetched_at": now.isoformat(),
            "query": query,
        },
        {
            "title": f"Digital Transformation Accelerates in {query.title()}",
            "description": f"Cloud and AI adoption surge across the {query} industry.",
            "content": f"Digital transformation in the {query} sector is accelerating at an unprecedented pace. Cloud computing adoption has reached critical mass, enabling organizations to scale operations and reduce costs. Artificial intelligence and machine learning are being integrated across value chains, from supply chain optimization to customer experience personalization. Companies that embrace these technologies are seeing measurable improvements in productivity and revenue growth.",
            "source": "Digital Trends",
            "author": "James Wilson",
            "url": "https://example.com/article-8",
            "image_url": "",
            "published_at": (now - timedelta(days=3)).isoformat(),
            "fetched_at": now.isoformat(),
            "query": query,
        },
    ]
    log.info("Generated %d demo articles for query='%s'", len(samples), query)
    return samples
