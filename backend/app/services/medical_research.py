from __future__ import annotations

from datetime import datetime, timedelta, timezone
from html import unescape
import re
import xml.etree.ElementTree as ET

import requests

from app.config import settings


PUBMED_SEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PUBMED_FETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

MEDICAL_CATEGORY_QUERIES = {
    "iq": [
        "IQ",
        "intelligence quotient",
        "cognitive ability",
        "working memory",
        "executive function",
        "cognitive neuroscience",
    ],
    "longevity": ["longevity", "healthy aging", "lifespan"],
    "peptides": ["peptide therapy", "BPC-157", "thymosin"],
    "antiaging": ["anti-aging", "anti aging", "geroprotection"],
    "diet": ["best diet", "nutrition", "Mediterranean diet"],
    "neuropsychology": [
        "neuropsychology",
        "neuropsychological assessment",
        "cognitive neuroscience",
        "executive function",
        "working memory",
        "attention",
    ],
}

PUBMED_CATEGORY_RECENCY_DAYS = {
    "iq": 120,
    "neuropsychology": 120,
    "diet": 90,
    "peptides": 120,
    "antiaging": 180,
    "longevity": 180,
}

PUBMED_MIN_RESULTS_PER_CATEGORY = 8


def _clean_text(value: str | None) -> str:
    if not value:
        return ""
    return re.sub(r"\s+", " ", unescape(value)).strip()


def _summarize_text(text: str, title: str, category: str) -> str:
    sentences = re.split(r"(?<=[.!?])\s+", text)
    clipped = [sentence.strip() for sentence in sentences if sentence.strip()][:2]

    if clipped:
        return " ".join(clipped)

    return f"PubMed research item on {category} titled '{title}'."


def _parse_pub_date(article: ET.Element) -> datetime:
    year = article.findtext(".//PubDate/Year")
    month = article.findtext(".//PubDate/Month")
    day = article.findtext(".//PubDate/Day")

    month_lookup = {
        "Jan": 1,
        "Feb": 2,
        "Mar": 3,
        "Apr": 4,
        "May": 5,
        "Jun": 6,
        "Jul": 7,
        "Aug": 8,
        "Sep": 9,
        "Oct": 10,
        "Nov": 11,
        "Dec": 12,
    }

    try:
        parsed_month = int(month) if (month or "").isdigit() else month_lookup.get((month or "")[:3], 1)
        return datetime(
            year=int(year or datetime.now(timezone.utc).year),
            month=parsed_month,
            day=int(day or 1),
            tzinfo=timezone.utc,
        )
    except ValueError:
        return datetime.now(timezone.utc)


def _search_pubmed_ids_with_window(query: str, recency_days: int, retmax: int = 5) -> list[str]:
    response = requests.get(
        PUBMED_SEARCH_URL,
        params={
            "db": "pubmed",
            "term": query,
            "retmode": "json",
            "sort": "pub date",
            "retmax": retmax,
            "datetype": "pdat",
            "reldate": recency_days,
        },
        timeout=settings.request_timeout_seconds,
    )
    response.raise_for_status()
    payload = response.json()
    return payload.get("esearchresult", {}).get("idlist", [])


def _fetch_pubmed_records(pmids: list[str]) -> list[ET.Element]:
    if not pmids:
        return []

    response = requests.get(
        PUBMED_FETCH_URL,
        params={"db": "pubmed", "id": ",".join(pmids), "retmode": "xml"},
        timeout=settings.request_timeout_seconds,
    )
    response.raise_for_status()
    root = ET.fromstring(response.text)
    return root.findall(".//PubmedArticle")


def _parse_pubmed_article(article: ET.Element, category: str) -> dict | None:
    pmid = _clean_text(article.findtext(".//PMID"))
    title = _clean_text(article.findtext(".//ArticleTitle"))

    if not pmid or not title:
        return None

    abstract_parts = [
        _clean_text("".join(node.itertext()))
        for node in article.findall(".//Abstract/AbstractText")
    ]
    abstract = " ".join(part for part in abstract_parts if part)

    return {
        "title": title,
        "source": "PubMed",
        "category": category,
        "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
        "timestamp": _parse_pub_date(article),
        "summary": _summarize_text(abstract, title, category),
    }


def fetch_medical_research_articles() -> list[dict]:
    articles: list[dict] = []
    now = datetime.now(timezone.utc)

    for category, queries in MEDICAL_CATEGORY_QUERIES.items():
        pmids: list[str] = []
        base_window = PUBMED_CATEGORY_RECENCY_DAYS.get(category, settings.pubmed_default_recency_days)
        candidate_windows = list(dict.fromkeys([base_window, min(base_window * 2, 365), 365]))

        for recency_days in candidate_windows:
            pmids = []
            cutoff = now - timedelta(days=recency_days)

            for query in queries:
                try:
                    pmids.extend(_search_pubmed_ids_with_window(query, recency_days))
                except Exception:
                    continue

            unique_pmids = list(dict.fromkeys(pmids))
            if len(unique_pmids) >= PUBMED_MIN_RESULTS_PER_CATEGORY or recency_days == candidate_windows[-1]:
                break

        unique_pmids = list(dict.fromkeys(pmids))

        try:
            records = _fetch_pubmed_records(unique_pmids)
        except Exception:
            continue

        for record in records:
            parsed = _parse_pubmed_article(record, category)
            if parsed and parsed["timestamp"] >= cutoff:
                articles.append(parsed)

    deduped: dict[str, dict] = {}
    for article in articles:
        deduped[article["url"]] = article

    return sorted(deduped.values(), key=lambda item: item["timestamp"], reverse=True)
