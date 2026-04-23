from __future__ import annotations

from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime

import feedparser
import requests
from dateutil import parser as date_parser
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.config import settings
from app.models import Article
from app.services.medical_research import fetch_medical_research_articles
from app.services.news_sources import FeedSource, GENERAL_FEED_SOURCES, MEDICAL_FEED_SOURCES


def _normalize_text(value: str | None) -> str:
    return (value or "").strip()


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None

    try:
        parsed = parsedate_to_datetime(value)
    except (TypeError, ValueError, IndexError):
        parsed = None

    if parsed is None:
        try:
            parsed = date_parser.parse(value)
        except (TypeError, ValueError):
            return None

    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)

    return parsed.astimezone(timezone.utc)


def _cutoff_for_source(source: FeedSource) -> datetime:
    days = settings.news_recency_days if source in GENERAL_FEED_SOURCES else settings.medical_feed_recency_days
    return datetime.now(timezone.utc) - timedelta(days=days)


def fetch_json_source(source: FeedSource) -> list[dict]:
    response = requests.get(source.url, timeout=settings.request_timeout_seconds)
    response.raise_for_status()
    payload = response.json()
    hits = payload.get("hits", [])
    articles = []
    cutoff = _cutoff_for_source(source)

    for item in hits:
        title = _normalize_text(item.get(source.title_field))
        url = _normalize_text(item.get("url"))
        timestamp = _parse_datetime(item.get("created_at"))

        if not title or not url or timestamp is None or timestamp < cutoff:
            continue

        articles.append(
            {
                "title": title,
                "source": source.name,
                "category": source.category,
                "url": url,
                "timestamp": timestamp,
                "summary": _normalize_text(item.get(source.summary_field)),
            }
        )

    return articles


def fetch_rss_source(source: FeedSource) -> list[dict]:
    parsed = feedparser.parse(source.url)
    articles = []
    cutoff = _cutoff_for_source(source)

    for entry in parsed.entries:
        title = _normalize_text(getattr(entry, "title", None))
        url = _normalize_text(getattr(entry, "link", None))

        if not title or not url:
            continue

        published = (
            getattr(entry, "published", None)
            or getattr(entry, "updated", None)
            or getattr(entry, "created", None)
        )
        summary = getattr(entry, "summary", None) or getattr(entry, "description", None)
        timestamp = _parse_datetime(published)

        if not title or not url or timestamp is None or timestamp < cutoff:
            continue

        articles.append(
            {
                "title": title,
                "source": source.name,
                "category": source.category,
                "url": url,
                "timestamp": timestamp,
                "summary": _normalize_text(summary),
            }
        )

    return articles


def fetch_all_articles() -> list[dict]:
    collected: list[dict] = []

    for source in [*GENERAL_FEED_SOURCES, *MEDICAL_FEED_SOURCES]:
        try:
            if source.kind == "json":
                collected.extend(fetch_json_source(source))
            else:
                collected.extend(fetch_rss_source(source))
        except Exception:
            # We keep the dashboard usable even if one source is temporarily down.
            continue

    try:
        collected.extend(fetch_medical_research_articles())
    except Exception:
        pass

    deduped: dict[str, dict] = {}
    for article in collected:
        deduped[article["url"]] = article

    return sorted(deduped.values(), key=lambda item: item["timestamp"], reverse=True)


def prune_stale_articles(db: Session) -> None:
    now = datetime.now(timezone.utc)
    default_cutoff = now - timedelta(days=settings.pubmed_default_recency_days)
    category_cutoffs = {
        "tech": now - timedelta(days=settings.news_recency_days),
        "hacker-news": now - timedelta(days=settings.news_recency_days),
        "computer-news": now - timedelta(days=settings.news_recency_days),
        "politics": now - timedelta(days=settings.news_recency_days),
        "latest-events": now - timedelta(days=settings.news_recency_days),
        "iq": now - timedelta(days=120),
        "neuropsychology": now - timedelta(days=120),
        "diet": now - timedelta(days=90),
        "peptides": now - timedelta(days=120),
        "antiaging": now - timedelta(days=180),
        "longevity": now - timedelta(days=180),
    }

    for category, cutoff in category_cutoffs.items():
        db.execute(delete(Article).where(Article.category == category, Article.timestamp < cutoff))

    db.execute(delete(Article).where(~Article.category.in_(list(category_cutoffs.keys())), Article.timestamp < default_cutoff))
    db.commit()


def refresh_articles(db: Session) -> tuple[int, int]:
    prune_stale_articles(db)
    articles = fetch_all_articles()
    inserted = 0

    existing_urls = set(db.scalars(select(Article.url)).all())

    for item in articles:
        if item["url"] in existing_urls:
            continue

        db.add(Article(**item))
        inserted += 1

    db.commit()
    total = db.query(Article).count()
    return inserted, total
