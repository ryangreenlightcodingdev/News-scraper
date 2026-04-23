# News Aggregator Dashboard

A full-stack news dashboard that aggregates:

- Tech news
- Hacker News
- General computer news
- Political news

The backend uses FastAPI, SQLite, SQLAlchemy, and APScheduler. The frontend uses React with Vite.

## Features

- Normalized article format: `title`, `source`, `url`, `timestamp`
- Additional metadata for `category` and `summary`
- Background refresh every 10 minutes
- Manual refresh endpoint and UI button
- Source and category filters
- SQLite persistence with deduplication by URL

## Project Structure

```text
backend/
  app/
    main.py
    config.py
    database.py
    models.py
    schemas.py
    services/
frontend/
  src/
```

## Backend Setup

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API will run at `http://127.0.0.1:8000`.

Useful endpoints:

- `GET /api/articles`
- `GET /api/filters`
- `POST /api/refresh`
- `GET /health`

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The React app will run at `http://127.0.0.1:5173`.

## Notes

- The backend refreshes feeds on startup and then every 10 minutes.
- The frontend expects the backend at `http://127.0.0.1:8000` by default.
- You can change feed behavior in `backend/app/services/aggregator.py`.

