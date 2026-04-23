# News Intelligence Dashboard

A full-stack web app that aggregates technology, politics, and medical research into one dashboard.

## Features

- News from tech, Hacker News, computer news, and politics
- Medical research topics added to the same board and filters:
  - `iq`
  - `neuropsychology`
  - `longevity`
  - `peptides`
  - `antiaging`
  - `diet`
- Sources include PubMed plus selected ScienceDaily topic feeds
- Unified article format: `title`, `source`, `url`, `timestamp`, `summary`
- FastAPI backend with SQLite storage and 10-minute refreshes
- React frontend with category and source filters

## Run Locally

Backend:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Frontend:

```powershell
cd frontend
npm install
npm run dev
```

Open `http://127.0.0.1:5173`.

## Notes

- The dashboard layout stays the same; the new medical topics appear through the existing category and source filters.
- PubMed papers are pulled through NCBI E-utilities, then summarized from abstract text when available.
- Additional medical-related feed coverage comes from ScienceDaily topic RSS feeds for intelligence, memory, neuroscience, healthy aging, nutrition, and supplements.
- Freshness is now enforced with rolling windows: news is kept tighter, while science categories use wider category-specific windows so slower-moving research areas still surface the latest meaningful work.
