from contextlib import asynccontextmanager

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import distinct, select
from sqlalchemy.orm import Session

from app.config import settings
from app.database import Base, SessionLocal, engine, get_db
from app.models import Article
from app.schemas import ArticleRead, FiltersResponse, RefreshResponse
from app.services.aggregator import refresh_articles


scheduler = BackgroundScheduler(timezone="UTC")


def refresh_job() -> None:
    db = SessionLocal()
    try:
        refresh_articles(db)
    finally:
        db.close()


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    refresh_job()
    scheduler.add_job(
        refresh_job,
        "interval",
        minutes=settings.refresh_interval_minutes,
        id="refresh_articles",
        replace_existing=True,
    )
    scheduler.start()

    try:
        yield
    finally:
        if scheduler.running:
            scheduler.shutdown(wait=False)


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin, "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/articles", response_model=list[ArticleRead])
def list_articles(
    category: str | None = None,
    source: str | None = None,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    query = db.query(Article)

    if category:
        query = query.filter(Article.category == category)
    if source:
        query = query.filter(Article.source == source)

    articles = query.order_by(Article.timestamp.desc()).limit(min(limit, 250)).all()
    return articles


@app.get("/api/filters", response_model=FiltersResponse)
def get_filters(db: Session = Depends(get_db)):
    categories = db.scalars(select(distinct(Article.category)).order_by(Article.category)).all()
    sources = db.scalars(select(distinct(Article.source)).order_by(Article.source)).all()
    return FiltersResponse(categories=categories, sources=sources)


@app.post("/api/refresh", response_model=RefreshResponse)
def manual_refresh(db: Session = Depends(get_db)):
    inserted, total = refresh_articles(db)
    return RefreshResponse(inserted=inserted, total=total)
