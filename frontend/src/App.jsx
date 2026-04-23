import { useEffect, useState } from "react";

const API_BASE = "http://127.0.0.1:8000";

function App() {
  const [articles, setArticles] = useState([]);
  const [filters, setFilters] = useState({ categories: [], sources: [] });
  const [selectedCategory, setSelectedCategory] = useState("");
  const [selectedSource, setSelectedSource] = useState("");
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");

  async function loadFilters() {
    const response = await fetch(`${API_BASE}/api/filters`);
    if (!response.ok) {
      throw new Error("Unable to load filter options.");
    }
    const data = await response.json();
    setFilters(data);
  }

  async function loadArticles(category = selectedCategory, source = selectedSource) {
    setLoading(true);
    setError("");

    try {
      const params = new URLSearchParams();
      if (category) params.set("category", category);
      if (source) params.set("source", source);
      params.set("limit", "120");

      const response = await fetch(`${API_BASE}/api/articles?${params.toString()}`);
      if (!response.ok) {
        throw new Error("Unable to load articles.");
      }

      const data = await response.json();
      setArticles(data);
    } catch (err) {
      setError(err.message || "Something went wrong while loading the dashboard.");
    } finally {
      setLoading(false);
    }
  }

  async function handleRefresh() {
    setRefreshing(true);
    setError("");

    try {
      const response = await fetch(`${API_BASE}/api/refresh`, { method: "POST" });
      if (!response.ok) {
        throw new Error("Refresh failed.");
      }

      await Promise.all([loadFilters(), loadArticles()]);
    } catch (err) {
      setError(err.message || "Unable to refresh feeds.");
    } finally {
      setRefreshing(false);
    }
  }

  useEffect(() => {
    Promise.all([loadFilters(), loadArticles()]).catch((err) => {
      setError(err.message || "Unable to initialize the dashboard.");
      setLoading(false);
    });
  }, []);

  useEffect(() => {
    loadArticles();
  }, [selectedCategory, selectedSource]);

  return (
    <div className="page-shell">
      <header className="hero">
        <div>
          <p className="eyebrow">Unified Newsroom</p>
          <h1>One dashboard for tech, politics, and medical research.</h1>
          <p className="hero-copy">
            Fresh articles are stored locally, normalized into one schema, and refreshed
            automatically every 10 minutes by the FastAPI backend, including PubMed-powered
            research on IQ, neuropsychology, longevity, peptides, antiaging, and diet,
            with stricter recency windows for news and wider rolling windows for science.
          </p>
        </div>
        <button className="refresh-button" onClick={handleRefresh} disabled={refreshing}>
          {refreshing ? "Refreshing..." : "Refresh now"}
        </button>
      </header>

      <section className="filters-panel">
        <label>
          Category
          <select value={selectedCategory} onChange={(event) => setSelectedCategory(event.target.value)}>
            <option value="">All categories</option>
            {filters.categories.map((category) => (
              <option key={category} value={category}>
                {category}
              </option>
            ))}
          </select>
        </label>

        <label>
          Source
          <select value={selectedSource} onChange={(event) => setSelectedSource(event.target.value)}>
            <option value="">All sources</option>
            {filters.sources.map((source) => (
              <option key={source} value={source}>
                {source}
              </option>
            ))}
          </select>
        </label>
      </section>

      {error ? <div className="status-card error">{error}</div> : null}
      {loading ? <div className="status-card">Loading articles...</div> : null}

      <section className="grid">
        {!loading &&
          articles.map((article) => (
            <article key={article.id} className="article-card">
              <div className="meta-row">
                <span className="pill">{article.category}</span>
                <span className="source">{article.source}</span>
              </div>
              <h2>{article.title}</h2>
              <p>{article.summary || "No summary available for this article."}</p>
              <div className="card-footer">
                <time dateTime={article.timestamp}>
                  {new Date(article.timestamp).toLocaleString()}
                </time>
                <a href={article.url} target="_blank" rel="noreferrer">
                  Read article
                </a>
              </div>
            </article>
          ))}
      </section>
    </div>
  );
}

export default App;
