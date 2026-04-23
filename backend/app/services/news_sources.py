from dataclasses import dataclass


@dataclass(frozen=True)
class FeedSource:
    name: str
    category: str
    kind: str
    url: str
    title_field: str = "title"
    summary_field: str = "summary"


GENERAL_FEED_SOURCES = [
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
    FeedSource(
        name="BBC Politics",
        category="politics",
        kind="rss",
        url="http://newsrss.bbc.co.uk/rss/newsonline_uk_edition/uk_politics/rss.xml",
    ),
    FeedSource(
        name="BBC Latest Stories",
        category="latest-events",
        kind="rss",
        url="http://news.bbc.co.uk/rss/newsonline_uk_edition/latest_published_stories/rss.xml",
    ),
    FeedSource(
        name="BBC World",
        category="latest-events",
        kind="rss",
        url="http://newsrss.bbc.co.uk/rss/newsonline_uk_edition/world/rss.xml",
    ),
]


MEDICAL_FEED_SOURCES = [
    FeedSource(
        name="ScienceDaily Intelligence",
        category="iq",
        kind="rss",
        url="https://www.sciencedaily.com/rss/mind_brain/intelligence.xml",
    ),
    FeedSource(
        name="ScienceDaily Memory",
        category="neuropsychology",
        kind="rss",
        url="https://www.sciencedaily.com/rss/mind_brain/memory.xml",
    ),
    FeedSource(
        name="ScienceDaily Neuroscience",
        category="neuropsychology",
        kind="rss",
        url="https://www.sciencedaily.com/rss/mind_brain/neuroscience.xml",
    ),
    FeedSource(
        name="ScienceDaily Healthy Aging",
        category="longevity",
        kind="rss",
        url="https://www.sciencedaily.com/rss/health_medicine/healthy_aging.xml",
    ),
    FeedSource(
        name="ScienceDaily Nutrition",
        category="diet",
        kind="rss",
        url="https://www.sciencedaily.com/rss/health_medicine/nutrition.xml",
    ),
    FeedSource(
        name="ScienceDaily Supplements",
        category="peptides",
        kind="rss",
        url="https://www.sciencedaily.com/rss/health_medicine/dietary_supplements.xml",
    ),
]
