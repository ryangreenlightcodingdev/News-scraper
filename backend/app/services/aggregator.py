from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

import feedparser
import requests
from dateutil import parser as date_parser
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.models import Article


@dataclass(frozen=True)
class FeedSource:
    name: str
    category: str
    kind: str
    url: str
    title_field: str = "title"
    summary_field: str = "summary"


FEED_SOURCES = [
    FeedSource(
        name="Hacker News",
        category="hacker-news",
        kind="json",
        url="https://hn.algolia.com/api/v1/search_by_date?tags=story&hitsPerPage=25",
        title_field="title",
        summary_field="story_text",
    ),
    FeedSource(
        name="TechCrunch",
        category="tech",
        kind="rss",
        url="https://techcrunch.com/feed/",
    ),
    FeedSource(
        name="The Verge",
        category="tech",
        kind="rss",
        url="https://www.theverge.com/rss/index.xml",
    ),
    FeedSource(
        name="Ars Technica",
        category="computer-news",
        kind="rss",
        url="https://feeds.arstechnica.com/arstechnica/index",
    ),
    FeedSource(
        name="Wired",
        category="computer-news",
        kind="rss",
        url="https://www.wired.com/feed/rss",
    ),
    FeedSource(
        name="Politico",
        category="politics",
        kind="rss",
        url="https://www.politico.com/rss/politicopicks.xml",
    ),
    FeedSource(
        name="AP Politics",
        category="politics",
        kind="rss",
        url="https://apnews.com/hub/politics/rss",
    ),
]


def _normalize_text(value: str | None) -> str:
    return (value or "").strip()


def _parse_datetime(value: str | None) -> datetime:
    if not value:
        return datetime.now(timezone.utc)

    try:
        parsed = parsedate_to_datetime(value)
    except (TypeError, ValueError, IndexError):
        parsed = None

    if parsed is None:
        try:
            parsed = date_parser.parse(value)
        except (TypeError, ValueError):
            return datetime.now(timezone.utc)

    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)

    return parsed.astimezone(timezone.utc)


def fetch_json_source(source: FeedSource) -> list[dict]:
    response = requests.get(source.url, timeout=settings.request_timeout_seconds)
    response.raise_for_status()
    payload = response.json()
    hits = payload.get("hits", [])
    articles = []

    for item in hits:
        title = _normalize_text(item.get(source.title_field))
        url = _normalize_text(item.get("url"))

        if not title or not url:
            continue

        articles.append(
            {
                "title": title,
                "source": source.name,
                "category": source.category,
                "url": url,
                "timestamp": _parse_datetime(item.get("created_at")),
                "summary": _normalize_text(item.get(source.summary_field)),
            }
        )

    return articles


def fetch_rss_source(source: FeedSource) -> list[dict]:
    parsed = feedparser.parse(source.url)
    articles = []

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

        articles.append(
            {
                "title": title,
                "source": source.name,
                "category": source.category,
                "url": url,
                "timestamp": _parse_datetime(published),
                "summary": _normalize_text(summary),
            }
        )

    return articles


def fetch_all_articles() -> list[dict]:
    collected: list[dict] = []

    for source in FEED_SOURCES:
        try:
            if source.kind == "json":
                collected.extend(fetch_json_source(source))
            else:
                collected.extend(fetch_rss_source(source))
        except Exception:
            # We keep the dashboard usable even if one source is temporarily down.
            continue

    deduped: dict[str, dict] = {}
    for article in collected:
        deduped[article["url"]] = article

    return sorted(deduped.values(), key=lambda item: item["timestamp"], reverse=True)


def refresh_articles(db: Session) -> tuple[int, int]:
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
