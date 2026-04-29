# 🧠 AI-Powered Market Intelligence Platform

A comprehensive market intelligence system that ingests news articles, processes them with NLP (keyword extraction, sentiment analysis), and delivers actionable insights through a modern FastAPI backend and interactive dashboard.

![Dashboard](frontend/screenshots/dashboard.png)

---

## 🏗 Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   News API   │────▶│  Ingestion   │────▶│  MongoDB     │
│  (NewsAPI)   │     │  Pipeline    │     │  raw_data    │
└──────────────┘     └──────┬───────┘     └──────────────┘
                            │
                     ┌──────▼───────┐     ┌──────────────┐
                     │  Processing  │────▶│  MongoDB     │
                     │  RAKE + NLP  │     │  processed   │
                     └──────────────┘     └──────┬───────┘
                                                 │
                     ┌──────────────┐     ┌──────▼───────┐
                     │  Frontend    │◀────│  FastAPI     │
                     │  Dashboard   │     │  REST API    │
                     └──────────────┘     └──────────────┘
```

---

## ⚡ Features

| Feature | Description |
|---------|-------------|
| **Data Ingestion** | Fetch news from NewsAPI with configurable queries and date ranges |
| **NLP Processing** | RAKE keyword extraction + TextBlob sentiment analysis |
| **Trend Detection** | Top keywords by frequency across 24h / 7d / 30d windows |
| **Sentiment Analysis** | Positive / Negative / Neutral classification with polarity scores |
| **Time Series** | Articles per day with growth percentage tracking |
| **Full-Text Search** | Regex-based search with pagination and sorting |
| **Background Tasks** | Auto-ingestion of related queries via FastAPI BackgroundTasks |
| **Structured Logging** | Rotating file logger (5MB × 3 backups) |
| **Interactive Dashboard** | Dark-theme glassmorphism UI with Chart.js visualizations |
| **Health Monitoring** | Real-time MongoDB connection status |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- MongoDB (local via Compass or Atlas cloud)
- News API key from [newsapi.org](https://newsapi.org) *(optional — demo data works without it)*

### Setup

```bash
# 1. Navigate to project
cd marketintelligence

# 2. Create virtual environment
python -m venv venv

# 3. Activate it
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Configure environment
# Edit .env with your API key and MongoDB URI

# 6. Start the server
uvicorn app.main:app --reload --port 8000
```

### Access
- **Dashboard**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/ingest` | Ingest news articles for a given query |
| `GET` | `/api/trends` | Get trending keywords (24h/7d/30d) |
| `GET` | `/api/insights` | Combined sentiment & trend insights |
| `GET` | `/api/search` | Full-text search with pagination |
| `GET` | `/api/analytics/summary` | Comprehensive analytics dashboard data |
| `GET` | `/health` | System health check |

### Example: Ingest Articles
```bash
curl -X POST http://localhost:8000/api/ingest \
  -H "Content-Type: application/json" \
  -d '{"query": "artificial intelligence", "page_size": 50}'
```

### Example: Get Trends
```bash
curl http://localhost:8000/api/trends?period=7d&limit=20
```

### Example: Search
```bash
curl http://localhost:8000/api/search?q=AI&page=1&page_size=10
```

---

## 📂 Project Structure

```
marketintelligence/
├── app/
│   ├── main.py              # FastAPI entrypoint
│   ├── config.py             # Settings from .env
│   ├── database.py           # MongoDB connection
│   ├── models.py             # Pydantic models
│   ├── routers/
│   │   ├── ingest.py         # POST /ingest
│   │   ├── trends.py         # GET /trends
│   │   ├── insights.py       # GET /insights
│   │   ├── search.py         # GET /search
│   │   └── analytics.py      # GET /analytics/summary
│   ├── services/
│   │   ├── news_fetcher.py   # NewsAPI integration
│   │   ├── data_processor.py # NLP pipeline
│   │   └── analyzer.py       # MongoDB aggregations
│   └── utils/
│       └── logger.py         # Rotating file logger
├── frontend/
│   ├── index.html            # SPA Dashboard
│   ├── css/style.css         # Design system
│   └── js/app.js             # Frontend logic
├── .env                      # Environment config
├── requirements.txt          # Python dependencies
├── Procfile                  # Deployment config
└── README.md
```

---

## 🛠 Tech Stack

- **Backend**: FastAPI, Uvicorn
- **Database**: MongoDB (PyMongo)
- **NLP**: TextBlob (sentiment), RAKE-NLTK (keywords)
- **Data Source**: NewsAPI.org
- **Frontend**: Vanilla HTML/CSS/JS, Chart.js
- **Design**: Dark theme, glassmorphism, Inter font

---

## 🌐 Deployment

### Render / Railway

1. Push code to GitHub
2. Create new Web Service on Render
3. Set environment variables (`NEWS_API_KEY`, `MONGODB_URI`, `DATABASE_NAME`)
4. Build command: `pip install -r requirements.txt`
5. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

---

## 📄 License

MIT License — feel free to use and modify.
