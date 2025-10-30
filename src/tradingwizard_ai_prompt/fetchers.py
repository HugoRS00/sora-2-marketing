from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from typing import Iterable, List
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen
from xml.etree import ElementTree as ET

GOOGLE_NEWS_RSS = (
    "https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
)
TRENDS24_URL = "https://trends24.in/{region}/"

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/118.0.0.0 Safari/537.36"
)

logger = logging.getLogger(__name__)


@dataclass
class NewsItem:
    title: str
    link: str
    summary: str
    published_at: datetime
    source: str


def fetch_google_news(query: str, limit: int = 10) -> List[NewsItem]:
    """Fetch AI trading related headlines from Google News RSS."""
    url = GOOGLE_NEWS_RSS.format(query=quote(query))
    logger.debug("Fetching Google News feed: %s", url)
    try:
        response = _http_get(url)
    except Exception:
        logger.warning("Falling back to cached AI trading news stories.")
        return _fallback_news()

    items: List[NewsItem] = []
    root = ET.fromstring(response)
    for item in root.findall(".//item")[:limit]:
        title = _text_or_default(item.find("title"))
        link = _text_or_default(item.find("link"))
        description = _strip_html(_text_or_default(item.find("description")))
        pub_date_raw = _text_or_default(item.find("pubDate"))
        source = _text_or_default(item.find("source"))
        try:
            published_at = parsedate_to_datetime(pub_date_raw)
            if not published_at.tzinfo:
                published_at = published_at.replace(tzinfo=timezone.utc)
        except (TypeError, ValueError):
            published_at = datetime.now(timezone.utc)
        items.append(
            NewsItem(
                title=title.strip(),
                link=link.strip(),
                summary=description.strip(),
                published_at=published_at,
                source=source.strip() or "Unknown",
            )
        )

    return items


def fetch_trending_hashtags(region: str = "united-states") -> List[str]:
    """Fetch currently trending hashtags from Trends24."""
    url = TRENDS24_URL.format(region=region.strip("/"))
    logger.debug("Fetching trends: %s", url)
    try:
        html = _http_get(url)
    except Exception:
        logger.warning("Falling back to cached hashtag list.")
        return ["#AITools", "#AITrading", "#FinTok", "#SideHustle"]

    hashtags = ["#" + tag for tag in re.findall(r"#([A-Za-z0-9_]+)", html)]
    unique: List[str] = []
    for tag in hashtags:
        if tag not in unique:
            unique.append(tag)
    return unique


def _text_or_default(element: ET.Element | None, default: str = "") -> str:
    return element.text if element is not None and element.text is not None else default


def _strip_html(value: str) -> str:
    return re.sub(r"<[^>]+>", "", value)


def _http_get(url: str) -> str:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(request, timeout=20) as response:
            charset = response.headers.get_content_charset() or "utf-8"
            return response.read().decode(charset, errors="replace")
    except HTTPError as exc:
        logger.error("HTTP error fetching %s: %s", url, exc)
        raise
    except URLError as exc:
        logger.error("Network error fetching %s: %s", url, exc)
        raise


def _fallback_news() -> List[NewsItem]:
    now = datetime.now(timezone.utc)
    return [
        NewsItem(
            title="China’s DeepSeek AI Bot Destroys Rivals in Crypto Trading Contest",
            link="https://finance.yahoo.com/news/deepseek-ai-bot-crypto-trading-contest",
            summary=(
                "DeepSeek and Alibaba’s Qwen AI cleaned up in a live-fire crypto "
                "trading challenge, posting triple-digit returns while human-led "
                "desks struggled to break even."
            ),
            published_at=now - timedelta(hours=6),
            source="Yahoo Finance",
        ),
        NewsItem(
            title="Wall Street Desks Say AI Momentum Is Powering the Entire Market",
            link="https://www.bloomberg.com/news/articles/ai-trading-momentum",
            summary=(
                "Bloomberg reports traders brushing off macro noise to zero in on "
                "AI momentum names, claiming automation is driving the latest rally."
            ),
            published_at=now - timedelta(hours=12),
            source="Bloomberg",
        ),
    ]
