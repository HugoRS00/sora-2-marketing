from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import datetime, timezone
from textwrap import wrap
from typing import List, Sequence

from .analyzer import TopicPick

BRAND_SIGN_OFF = "TradingWizard AI"


@dataclass
class DailyPackage:
    created_at: datetime
    tik_tok_title: str
    script: str
    talking_points: List[str]
    recommended_hashtags: List[str]
    source_link: str
    source_name: str


def build_script(topic: TopicPick, fallback_hashtags: Sequence[str]) -> DailyPackage:
    now = datetime.now(timezone.utc)
    news = topic.news
    hook = _compose_hook(news.title)

    core_story = _summarise_story(news.summary, news.source)
    why_it_matters = _why_it_matters(topic.matched_keywords)
    action = _action_tip(topic.matched_keywords)
    outro = _call_to_action()

    body_sections = [core_story, why_it_matters, action, outro]
    script = "\n\n".join([hook, *body_sections])

    hashtags = _select_hashtags(topic, fallback_hashtags)
    title = _build_title(news.title)
    talking_points = [
        core_story,
        why_it_matters,
        action,
        f"Trending hashtags: {' '.join(hashtags) if hashtags else 'n/a'}",
    ]

    return DailyPackage(
        created_at=now,
        tik_tok_title=title,
        script=script,
        talking_points=talking_points,
        recommended_hashtags=hashtags,
        source_link=news.link,
        source_name=news.source,
    )


def _compose_hook(headline: str) -> str:
    headline_clean = headline.replace(" - ", ": ").split(":")[0].strip()
    hook_templates = [
        "Stop scrolling—{} just flipped the script for everyday traders.",
        "You won’t believe how {} is rewriting the side-hustle playbook.",
        "Did you catch this? {} is the cheat code FinTok can’t stop buzzing about.",
        "Hold up—{} might be the fastest way to future-proof your money right now.",
    ]
    template = random.choice(hook_templates)
    return template.format(headline_clean)


def _summarise_story(summary: str, source: str) -> str:
    trimmed = " ".join(summary.split())
    if len(trimmed) > 260:
        trimmed = " ".join(" ".join(wrap(trimmed, 250))[:250].split())
    if not trimmed:
        trimmed = f"{source} reports a breakout move in AI-driven trading today."
    return f"Here’s the headline: {trimmed}"


def _why_it_matters(keywords: Sequence[str]) -> str:
    if "side hustle" in keywords:
        return (
            "Why it matters: this trend lets anyone stack an extra income stream "
            "without babysitting charts 24/7."
        )
    options = [
        "Why it matters: AI-backed momentum like this can level the playing field for solo traders.",
        "Why it matters: the smartest money is pricing this into their next moves, and retail can ride along.",
        "Why it matters: whenever AI beats human desks, the volatility magnet turns on for side hustlers.",
    ]
    if "crypto" in keywords:
        options.append(
            "Why it matters: crypto moves fastest on social chatter, and AI just spotted the rotation first."
        )
    if "stocks" in keywords or "equities" in keywords:
        options.append(
            "Why it matters: Wall Street is repricing growth plays around this story as we speak."
        )
    return random.choice(options)


def _action_tip(keywords: Sequence[str]) -> str:
    tips = [
        "Action tip: screenshot the key datapoints, set price alerts, and paper trade it before risking cash.",
        "Action tip: copy the setup into a sandbox account and grade it with position sizing you can sleep on.",
        "Action tip: plug it into your watchlist, set AI sentiment alerts, and track it for 3 sessions straight.",
    ]
    if "crypto" in keywords:
        tips.append(
            "Action tip: backtest it on a low-fee exchange with limit orders and automate your take-profit."
        )
    if "options" in keywords:
        tips.append(
            "Action tip: map the IV crush window and plan a debit spread so theta doesn’t eat you alive."
        )
    if "deepseek" in keywords or "bot" in keywords:
        tips.append(
            "Action tip: mirror the bot’s logic with a rules-based checklist and let automation handle the entries."
        )
    return random.choice(tips)


def _call_to_action() -> str:
    outros = [
        "If you’re chasing wizard-level setups daily, drop a ⚡️ and keep riding with TradingWizard AI.",
        "Tag your accountability buddy—TradingWizard AI drops plays like this every sunrise.",
        "Stay tuned with TradingWizard AI if you want tomorrow’s edge before the bell rings.",
    ]
    return random.choice(outros)


def _select_hashtags(topic: TopicPick, fallback_hashtags: Sequence[str]) -> List[str]:
    unique = list(topic.matched_hashtags)
    for tag in fallback_hashtags:
        if tag not in unique:
            unique.append(tag)
        if len(unique) >= 4:
            break
    return unique[:4]


def _build_title(headline: str) -> str:
    cleaned = headline.strip()
    endings = [
        "TradingWizard AI Daily Run",
        "TradingWizard AI Signal Drop",
        "TradingWizard AI Playbook",
    ]
    suffix = random.choice(endings)
    if len(cleaned) > 60:
        cleaned = cleaned[:57].rstrip() + "..."
    return f"{cleaned} | {suffix}"
