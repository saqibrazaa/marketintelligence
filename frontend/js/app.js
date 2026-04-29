/* ═══════════════════════════════════════════════════════════════
   AI-Powered Market Intelligence — Frontend Application
   ═══════════════════════════════════════════════════════════════ */

const API = '/api';
let charts = {};
let currentSearchPage = 1;
let currentSearchQuery = '';

// ── Navigation ────────────────────────────────────────────────

function navigate(page) {
    document.querySelectorAll('.page-section').forEach(s => s.classList.remove('active'));
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));

    document.getElementById(`page-${page}`).classList.add('active');
    document.querySelector(`.nav-item[data-page="${page}"]`).classList.add('active');

    // Close mobile sidebar
    document.getElementById('sidebar').classList.remove('open');

    // Load page data
    switch (page) {
        case 'dashboard': loadDashboard(); break;
        case 'trends': loadTrends('7d'); break;
        case 'insights': loadInsights('7d'); break;
        case 'analytics': loadAnalytics(); break;
    }
}

function toggleSidebar() {
    document.getElementById('sidebar').classList.toggle('open');
}

// ── Toast Notifications ───────────────────────────────────────

function toast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    const el = document.createElement('div');
    el.className = `toast ${type}`;
    const icons = { success: '✅', error: '❌', info: 'ℹ️' };
    el.innerHTML = `${icons[type] || '📢'} ${message}`;
    container.appendChild(el);
    setTimeout(() => { el.style.opacity = '0'; setTimeout(() => el.remove(), 300); }, 4000);
}

// ── API Helpers ───────────────────────────────────────────────

async function apiFetch(path, options = {}) {
    try {
        const resp = await fetch(`${API}${path}`, {
            headers: { 'Content-Type': 'application/json' },
            ...options,
        });
        if (!resp.ok) {
            const err = await resp.json().catch(() => ({ detail: resp.statusText }));
            throw new Error(err.detail || `HTTP ${resp.status}`);
        }
        return await resp.json();
    } catch (err) {
        console.error(`API error [${path}]:`, err);
        throw err;
    }
}

// ── Chart Defaults ────────────────────────────────────────────

Chart.defaults.color = '#94a3b8';
Chart.defaults.borderColor = 'rgba(255,255,255,0.06)';
Chart.defaults.font.family = "'Inter', sans-serif";
Chart.defaults.font.size = 12;
Chart.defaults.plugins.legend.labels.usePointStyle = true;
Chart.defaults.plugins.legend.labels.padding = 16;

function destroyChart(id) {
    if (charts[id]) { charts[id].destroy(); delete charts[id]; }
}

const COLORS = {
    blue: 'rgba(99, 102, 241, 0.8)',
    purple: 'rgba(139, 92, 246, 0.8)',
    cyan: 'rgba(6, 182, 212, 0.8)',
    green: 'rgba(16, 185, 129, 0.8)',
    amber: 'rgba(245, 158, 11, 0.8)',
    rose: 'rgba(244, 63, 94, 0.8)',
    blueFill: 'rgba(99, 102, 241, 0.15)',
    greenFill: 'rgba(16, 185, 129, 0.15)',
    roseFill: 'rgba(244, 63, 94, 0.15)',
};

// ── Dashboard ─────────────────────────────────────────────────

async function loadDashboard() {
    try {
        const data = await apiFetch('/analytics/summary');

        // Stats
        document.getElementById('statTotal').textContent = data.total_articles.toLocaleString();
        document.getElementById('statRecent').textContent = data.articles_last_24h.toLocaleString();
        document.getElementById('statTrend').textContent = data.avg_trend_score;
        document.getElementById('statSentiment').textContent = data.avg_sentiment >= 0
            ? `+${data.avg_sentiment}` : data.avg_sentiment;

        // Time Series Chart
        renderTimeSeriesChart('timeSeriesChart', data.time_series);

        // Sentiment Donut
        renderSentimentDonut('sentimentChart', data.sentiment_distribution);

        // Keywords
        renderKeywordCloud('dashKeywords', data.trends_7d);

    } catch (err) {
        toast('Failed to load dashboard data', 'error');
    }
}

// ── Trends ────────────────────────────────────────────────────

async function loadTrends(period) {
    // Update period buttons
    document.querySelectorAll('#page-trends .period-btn').forEach(b => {
        b.classList.toggle('active', b.dataset.period === period);
    });

    try {
        const data = await apiFetch(`/trends?period=${period}&limit=20`);
        const keywords = data.keywords || [];

        // Bar Chart
        renderTrendsBar(keywords);

        // Keyword Cloud
        renderKeywordCloud('trendsKeywords', keywords);

        // Table
        const tbody = document.getElementById('trendsTable');
        if (keywords.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="empty-state">No trends data. Ingest articles first.</td></tr>';
            return;
        }
        tbody.innerHTML = keywords.map((k, i) => `
            <tr>
                <td style="color:var(--text-muted)">${i + 1}</td>
                <td style="color:var(--text-primary);font-weight:500">${k.keyword}</td>
                <td><span style="font-family:'JetBrains Mono',monospace">${k.count}</span></td>
                <td>
                    <span class="trend-score-bar"><span class="trend-score-fill" style="width:${k.avg_trend_score}%"></span></span>
                    <span style="font-family:'JetBrains Mono',monospace;font-size:0.8rem">${k.avg_trend_score}</span>
                </td>
                <td>
                    <span class="sentiment-badge ${k.avg_sentiment > 0.1 ? 'positive' : k.avg_sentiment < -0.1 ? 'negative' : 'neutral'}">
                        ${k.avg_sentiment > 0.1 ? '😊' : k.avg_sentiment < -0.1 ? '😞' : '😐'} ${k.avg_sentiment}
                    </span>
                </td>
            </tr>
        `).join('');

    } catch (err) {
        toast('Failed to load trends', 'error');
    }
}

// ── Insights ──────────────────────────────────────────────────

async function loadInsights(period) {
    document.querySelectorAll('#page-insights .period-btn').forEach(b => {
        b.classList.toggle('active', b.dataset.period === period);
    });

    try {
        const data = await apiFetch(`/insights?period=${period}`);

        // Summary
        document.getElementById('insightSummary').textContent = data.summary || 'No insights available yet. Ingest some articles first.';

        // Sentiment Chart
        renderSentimentDonut('insightSentimentChart', data.sentiment);

        // Sentiment Bars
        const total = data.sentiment.total || 1;
        document.getElementById('sentimentBars').innerHTML = ['positive', 'negative', 'neutral'].map(label => `
            <div class="sentiment-row">
                <span class="sentiment-label">${label === 'positive' ? '😊' : label === 'negative' ? '😞' : '😐'} ${label}</span>
                <div class="sentiment-bar-bg">
                    <div class="sentiment-bar ${label}" style="width:${(data.sentiment[label] / total * 100).toFixed(1)}%"></div>
                </div>
                <span class="sentiment-count">${data.sentiment[label]}</span>
            </div>
        `).join('');

        // Time chart
        renderSentimentTimeline(data.time_series);

    } catch (err) {
        toast('Failed to load insights', 'error');
    }
}

// ── Search ────────────────────────────────────────────────────

async function searchArticles(page = 1) {
    const q = document.getElementById('searchInput').value.trim();
    if (!q) { toast('Enter a search term', 'info'); return; }

    currentSearchQuery = q;
    currentSearchPage = page;

    try {
        const data = await apiFetch(`/search?q=${encodeURIComponent(q)}&page=${page}&page_size=10`);

        const container = document.getElementById('searchResults');
        if (!data.items || data.items.length === 0) {
            container.innerHTML = `<div class="empty-state"><div class="empty-icon">🔍</div><p>No results found for "${q}"</p></div>`;
            document.getElementById('searchPagination').style.display = 'none';
            return;
        }

        container.innerHTML = data.items.map(art => `
            <div class="article-card">
                <h4><a href="${art.url}" target="_blank" rel="noopener">${art.title || 'Untitled'}</a></h4>
                <div class="article-meta">
                    <span>📰 ${art.source}</span>
                    <span>✍️ ${art.author}</span>
                    <span>📅 ${formatDate(art.published_at)}</span>
                    <span class="sentiment-badge ${art.sentiment?.label}">${sentimentIcon(art.sentiment?.label)} ${art.sentiment?.label || 'neutral'} (${art.sentiment?.polarity?.toFixed(2) || 0})</span>
                    <span>🔥 Trend: ${art.trend_score || 0}</span>
                </div>
                <p class="article-description">${art.description || ''}</p>
                ${art.keywords?.length ? `<div class="article-keywords">${art.keywords.map(k => `<span class="keyword-tag">${k}</span>`).join('')}</div>` : ''}
            </div>
        `).join('');

        // Pagination
        const pagination = document.getElementById('searchPagination');
        pagination.style.display = 'flex';
        document.getElementById('pageInfo').textContent = `Page ${data.page} of ${data.total_pages} (${data.total} results)`;
        document.getElementById('prevPageBtn').disabled = data.page <= 1;
        document.getElementById('nextPageBtn').disabled = data.page >= data.total_pages;

    } catch (err) {
        toast('Search failed', 'error');
    }
}

function searchPage(delta) {
    searchArticles(currentSearchPage + delta);
}

// ── Analytics ─────────────────────────────────────────────────

async function loadAnalytics() {
    try {
        const data = await apiFetch('/analytics/summary');

        // Stats cards
        document.getElementById('analyticsStats').innerHTML = `
            <div class="stat-card blue">
                <div class="stat-icon blue">📰</div>
                <div class="stat-info"><h3>${data.total_articles.toLocaleString()}</h3><p>Total Articles</p></div>
            </div>
            <div class="stat-card green">
                <div class="stat-icon green">🕐</div>
                <div class="stat-info"><h3>${data.articles_last_24h}</h3><p>Last 24h</p></div>
            </div>
            <div class="stat-card amber">
                <div class="stat-icon amber">📊</div>
                <div class="stat-info"><h3>${data.top_sources?.length || 0}</h3><p>Sources</p></div>
            </div>
            <div class="stat-card rose">
                <div class="stat-icon rose">🔎</div>
                <div class="stat-info"><h3>${data.top_queries?.length || 0}</h3><p>Queries Tracked</p></div>
            </div>
        `;

        // Sources chart
        renderHorizontalBar('sourcesChart', data.top_sources || [], 'source', 'count', COLORS.blue);

        // Queries chart
        renderHorizontalBar('queriesChart', data.top_queries || [], 'query', 'count', COLORS.purple);

        // Growth chart
        renderGrowthChart(data.time_series || []);

    } catch (err) {
        toast('Failed to load analytics', 'error');
    }
}

// ── Chart Renderers ───────────────────────────────────────────

function renderTimeSeriesChart(canvasId, ts) {
    destroyChart(canvasId);
    const ctx = document.getElementById(canvasId);
    if (!ts || ts.length === 0) return;

    charts[canvasId] = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ts.map(d => d.date),
            datasets: [{
                label: 'Articles',
                data: ts.map(d => d.count),
                borderColor: COLORS.blue,
                backgroundColor: COLORS.blueFill,
                fill: true,
                tension: 0.4,
                pointRadius: 4,
                pointHoverRadius: 6,
                pointBackgroundColor: COLORS.blue,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: { grid: { display: false } },
                y: { beginAtZero: true, grid: { color: 'rgba(255,255,255,0.04)' } }
            }
        }
    });
}

function renderSentimentDonut(canvasId, sentiment) {
    destroyChart(canvasId);
    const ctx = document.getElementById(canvasId);
    if (!sentiment) return;

    charts[canvasId] = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Positive', 'Negative', 'Neutral'],
            datasets: [{
                data: [sentiment.positive || 0, sentiment.negative || 0, sentiment.neutral || 0],
                backgroundColor: [COLORS.green, COLORS.rose, 'rgba(100,116,139,0.6)'],
                borderColor: 'transparent',
                borderWidth: 0,
                hoverOffset: 8,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '65%',
            plugins: {
                legend: { position: 'bottom' }
            }
        }
    });
}

function renderTrendsBar(keywords) {
    destroyChart('trendsBarChart');
    const ctx = document.getElementById('trendsBarChart');
    if (!keywords || keywords.length === 0) return;

    const top10 = keywords.slice(0, 10);
    charts['trendsBarChart'] = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: top10.map(k => k.keyword.length > 18 ? k.keyword.slice(0, 18) + '…' : k.keyword),
            datasets: [{
                label: 'Frequency',
                data: top10.map(k => k.count),
                backgroundColor: top10.map((_, i) => {
                    const palette = [COLORS.blue, COLORS.purple, COLORS.cyan, COLORS.green, COLORS.amber];
                    return palette[i % palette.length];
                }),
                borderRadius: 6,
                barPercentage: 0.6,
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: { grid: { color: 'rgba(255,255,255,0.04)' }, beginAtZero: true },
                y: { grid: { display: false } }
            }
        }
    });
}

function renderSentimentTimeline(ts) {
    destroyChart('insightTimeChart');
    const ctx = document.getElementById('insightTimeChart');
    if (!ts || ts.length === 0) return;

    charts['insightTimeChart'] = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ts.map(d => d.date),
            datasets: [{
                label: 'Avg Sentiment',
                data: ts.map(d => d.avg_sentiment),
                borderColor: COLORS.green,
                backgroundColor: COLORS.greenFill,
                fill: true,
                tension: 0.4,
                pointRadius: 4,
                pointBackgroundColor: COLORS.green,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: { grid: { display: false } },
                y: { grid: { color: 'rgba(255,255,255,0.04)' },
                     suggestedMin: -1, suggestedMax: 1 }
            }
        }
    });
}

function renderHorizontalBar(canvasId, items, labelKey, valueKey, color) {
    destroyChart(canvasId);
    const ctx = document.getElementById(canvasId);
    if (!items || items.length === 0) return;

    charts[canvasId] = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: items.map(i => i[labelKey]),
            datasets: [{
                data: items.map(i => i[valueKey]),
                backgroundColor: color,
                borderRadius: 6,
                barPercentage: 0.5,
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: { grid: { color: 'rgba(255,255,255,0.04)' }, beginAtZero: true },
                y: { grid: { display: false } }
            }
        }
    });
}

function renderGrowthChart(ts) {
    destroyChart('growthChart');
    const ctx = document.getElementById('growthChart');
    if (!ts || ts.length === 0) return;

    charts['growthChart'] = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ts.map(d => d.date),
            datasets: [
                {
                    type: 'bar',
                    label: 'Articles',
                    data: ts.map(d => d.count),
                    backgroundColor: COLORS.blueFill,
                    borderColor: COLORS.blue,
                    borderWidth: 1,
                    borderRadius: 6,
                    barPercentage: 0.5,
                    yAxisID: 'y',
                },
                {
                    type: 'line',
                    label: 'Growth %',
                    data: ts.map(d => d.growth_pct),
                    borderColor: COLORS.amber,
                    backgroundColor: 'transparent',
                    tension: 0.4,
                    pointRadius: 4,
                    pointBackgroundColor: COLORS.amber,
                    yAxisID: 'y1',
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { position: 'top' } },
            scales: {
                x: { grid: { display: false } },
                y: { beginAtZero: true, grid: { color: 'rgba(255,255,255,0.04)' }, title: { display: true, text: 'Count' } },
                y1: { position: 'right', grid: { display: false }, title: { display: true, text: 'Growth %' } },
            }
        }
    });
}

function renderKeywordCloud(containerId, keywords) {
    const container = document.getElementById(containerId);
    if (!keywords || keywords.length === 0) {
        container.innerHTML = '<div class="empty-state"><p>No keywords yet. Ingest articles to see trends.</p></div>';
        return;
    }
    container.innerHTML = keywords.map(k => {
        const size = Math.min(1.2, 0.7 + k.count * 0.05);
        return `<span class="keyword-tag" style="font-size:${size}rem">${k.keyword} <span class="tag-count">×${k.count}</span></span>`;
    }).join('');
}

// ── Ingest Data ───────────────────────────────────────────────

async function ingestData() {
    const query = document.getElementById('ingestQuery').value.trim();
    if (!query) { toast('Enter a topic to ingest', 'info'); return; }

    const pageSize = parseInt(document.getElementById('ingestCount').value) || 50;
    const btn = document.getElementById('ingestBtn');
    btn.disabled = true;
    btn.innerHTML = '⏳ Ingesting...';

    try {
        const data = await apiFetch('/ingest', {
            method: 'POST',
            body: JSON.stringify({ query, page_size: pageSize }),
        });
        toast(`Ingested ${data.articles_fetched} articles, processed ${data.articles_processed}`, 'success');
        loadDashboard(); // Refresh
    } catch (err) {
        toast(`Ingestion failed: ${err.message}`, 'error');
    } finally {
        btn.disabled = false;
        btn.innerHTML = '⚡ Ingest Data';
    }
}

// ── Helpers ───────────────────────────────────────────────────

function formatDate(isoStr) {
    if (!isoStr) return '—';
    try {
        const d = new Date(isoStr);
        return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
    } catch { return isoStr.slice(0, 10); }
}

function sentimentIcon(label) {
    return label === 'positive' ? '😊' : label === 'negative' ? '😞' : '😐';
}

// ── Health Check ──────────────────────────────────────────────

async function checkHealth() {
    try {
        const resp = await fetch('/health');
        const data = await resp.json();
        const dot = document.getElementById('dbStatusDot');
        const text = document.getElementById('dbStatusText');
        if (data.database === 'connected') {
            dot.classList.remove('disconnected');
            text.textContent = 'MongoDB Connected';
        } else {
            dot.classList.add('disconnected');
            text.textContent = 'DB Disconnected';
        }
    } catch {
        document.getElementById('dbStatusDot').classList.add('disconnected');
        document.getElementById('dbStatusText').textContent = 'API Unreachable';
    }
}

// ── Init ──────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
    checkHealth();
    loadDashboard();
    setInterval(checkHealth, 30000); // Check every 30s
});
