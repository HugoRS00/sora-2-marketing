from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable, List, Sequence

from .fetchers import NewsItem

RELEVANT_KEYWORDS = {
    "ai": 3.0,
    "trading": 3.0,
    "bot": 2.0,
    "auto": 1.2,
    "automated": 1.5,
    "autopilot": 1.7,
    "crypto": 1.7,
    "stocks": 1.5,
    "equities": 1.2,
    "retail": 1.0,
    "paper": 0.5,
    "side hustle": 1.5,
    "future": 1.0,
    "deepseek": 2.2,
    "qwen": 1.8,
    "options": 1.5,
    "momentum": 1.0,
    "hedge": 0.8,
    "volatility": 1.0,
    "robot": 1.2,
}

HASHTAG_KEYWORDS = {
    "ai": 2.0,
    "trading": 2.0,
    "fintech": 1.5,
    "crypto": 1.7,
    "sidehustle": 1.3,
    "automation": 1.5,
    "fintok": 1.8,
    "wealth": 1.0,
    "stocks": 1.2,
    "investing": 1.4,
    "quants": 1.0,
}


@dataclass
class TopicPick:
    news: NewsItem
    score: float
    matched_keywords: List[str]
    matched_hashtags: List[str]


def pick_hot_topic(
    items: Sequence[NewsItem], hashtags: Sequence[str], now: datetime | None = None
) -> TopicPick | None:
    """Score news items and return the best fit for a viral clip."""
    if not items:
        return None

    now = now or datetime.now(timezone.utc)
    hashtag_terms = [tag.strip("#").lower() for tag in hashtags]

    best: TopicPick | None = None
    for item in items:
        score, matched_words = _score_news_item(item, now)
        matched_tags = _match_hashtags(item, hashtag_terms)
        boost = sum(HASHTAG_KEYWORDS.get(tag, 1.0) for tag in matched_tags)
        total_score = score + boost
        if best is None or total_score > best.score:
            best = TopicPick(
                news=item,
                score=total_score,
                matched_keywords=matched_words,
                matched_hashtags=["#" + tag for tag in matched_tags],
            )
    return best


def _score_news_item(item: NewsItem, now: datetime) -> tuple[float, List[str]]:
    text = f"{item.title} {item.summary}".lower()
    matched: List[str] = []
    base_score = 0.0

    for keyword, weight in RELEVANT_KEYWORDS.items():
        if keyword in text:
            base_score += weight
            matched.append(keyword)

    hours_old = (now - item.published_at).total_seconds() / 3600 if item.published_at else 24
    freshness_bonus = max(0.0, 48 - hours_old) * 0.15
    momentum_bonus = math.log(len(text.split()) + 1, 10)

    total = base_score + freshness_bonus + momentum_bonus
    return total, matched


def _match_hashtags(item: NewsItem, hashtags_lower: Iterable[str]) -> List[str]:
    text = f"{item.title} {item.summary}".lower()
    matches: List[str] = []
    for tag in hashtags_lower:
        if not tag:
            continue
        if tag in text and tag not in matches:
            matches.append(tag)
    return matches
