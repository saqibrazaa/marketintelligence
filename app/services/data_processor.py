"""
Data processing pipeline — clean, extract keywords, sentiment, scores.
"""
import re
import math
from datetime import datetime
from app.utils.logger import get_logger

log = get_logger(__name__)

# ── Lazy-loaded NLP tools ──────────────────────────────────────────
_rake = None
_textblob_loaded = False


def _get_rake():
    global _rake
    if _rake is None:
        from rake_nltk import Rake
        import nltk
        try:
            nltk.data.find("tokenizers/punkt_tab")
        except LookupError:
            nltk.download("punkt_tab", quiet=True)
        try:
            nltk.data.find("corpora/stopwords")
        except LookupError:
            nltk.download("stopwords", quiet=True)
        _rake = Rake()
    return _rake


def _ensure_textblob():
    global _textblob_loaded
    if not _textblob_loaded:
        import nltk
        try:
            nltk.data.find("tokenizers/punkt_tab")
        except LookupError:
            nltk.download("punkt_tab", quiet=True)
        _textblob_loaded = True


# ── Text Cleaning ──────────────────────────────────────────────────

def clean_text(text: str | None) -> str:
    """Remove HTML tags, excess whitespace, and special characters."""
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", text)          # strip HTML
    text = re.sub(r"\[?\+\d+ chars\]?", "", text)  # remove NewsAPI truncation markers
    text = re.sub(r"http\S+", "", text)             # remove URLs
    text = re.sub(r"[^\w\s.,!?'-]", " ", text)     # keep basic punctuation
    text = re.sub(r"\s+", " ", text).strip()        # normalize whitespace
    return text


# ── Keyword Extraction ─────────────────────────────────────────────

def extract_keywords(text: str, top_n: int = 10) -> list[str]:
    """Extract top-N keywords using RAKE algorithm."""
    if not text or len(text) < 20:
        return []
    try:
        rake = _get_rake()
        rake.extract_keywords_from_text(text)
        phrases = rake.get_ranked_phrases()[:top_n]
        # Keep only phrases with ≤ 3 words for cleaner keywords
        return [p for p in phrases if len(p.split()) <= 3]
    except Exception as exc:
        log.warning("Keyword extraction failed: %s", exc)
        return []


# ── Sentiment Analysis ─────────────────────────────────────────────

def analyze_sentiment(text: str) -> dict:
    """
    Analyze sentiment using TextBlob.
    Returns: {label, polarity, subjectivity}
    """
    if not text:
        return {"label": "neutral", "polarity": 0.0, "subjectivity": 0.0}
    try:
        _ensure_textblob()
        from textblob import TextBlob
        blob = TextBlob(text)
        polarity = round(blob.sentiment.polarity, 4)
        subjectivity = round(blob.sentiment.subjectivity, 4)

        if polarity > 0.1:
            label = "positive"
        elif polarity < -0.1:
            label = "negative"
        else:
            label = "neutral"

        return {"label": label, "polarity": polarity, "subjectivity": subjectivity}
    except Exception as exc:
        log.warning("Sentiment analysis failed: %s", exc)
        return {"label": "neutral", "polarity": 0.0, "subjectivity": 0.0}


# ── Trend Score ─────────────────────────────────────────────────────

def calculate_trend_score(article: dict, keyword_freq: dict | None = None) -> float:
    """
    Compute a trend score (0-100) based on recency and keyword popularity.
    More recent articles and articles with popular keywords score higher.
    """
    score = 50.0  # base

    # Recency boost — articles < 24h get higher scores
    try:
        pub = article.get("published_at", "")
        if pub:
            pub_dt = datetime.fromisoformat(pub.replace("Z", "+00:00"))
            hours_ago = (datetime.now(pub_dt.tzinfo) - pub_dt).total_seconds() / 3600
            recency = max(0, 50 - hours_ago * 0.5)  # decays ~0.5 per hour
            score += recency
    except Exception:
        pass

    # Keyword popularity boost
    if keyword_freq:
        keywords = article.get("keywords", [])
        kw_score = sum(keyword_freq.get(kw, 0) for kw in keywords[:5])
        score += min(kw_score * 2, 30)

    return round(min(score, 100), 2)


# ── Main Pipeline ──────────────────────────────────────────────────

def process_articles(raw_articles: list[dict]) -> list[dict]:
    """
    Full processing pipeline: clean → keywords → sentiment → score.
    Returns a list of processed article dicts.
    """
    log.info("Processing %d articles …", len(raw_articles))

    # First pass — extract keywords and build frequency map
    processed = []
    keyword_freq: dict[str, int] = {}

    for art in raw_articles:
        full_text = clean_text(
            f"{art.get('title', '')}. {art.get('description', '')}. {art.get('content', '')}"
        )
        keywords = extract_keywords(full_text)
        for kw in keywords:
            keyword_freq[kw] = keyword_freq.get(kw, 0) + 1

        sentiment = analyze_sentiment(full_text)

        processed.append({
            "title": art.get("title", ""),
            "description": art.get("description", ""),
            "content": full_text,
            "source": art.get("source", "Unknown"),
            "author": art.get("author", "Unknown"),
            "url": art.get("url", ""),
            "image_url": art.get("image_url", ""),
            "published_at": art.get("published_at", ""),
            "fetched_at": art.get("fetched_at", ""),
            "query": art.get("query", ""),
            "keywords": keywords,
            "sentiment": sentiment,
            "trend_score": 0.0,  # placeholder — set in second pass
            "processed_at": datetime.utcnow().isoformat(),
        })

    # Second pass — calculate trend scores using keyword frequencies
    for art in processed:
        art["trend_score"] = calculate_trend_score(art, keyword_freq)

    log.info("Processing complete — %d articles processed", len(processed))
    return processed
