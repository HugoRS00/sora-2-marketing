from __future__ import annotations

import json
import logging
from dataclasses import asdict
from pathlib import Path
from typing import Dict, List

from .analyzer import pick_hot_topic
from .fetchers import fetch_google_news, fetch_trending_hashtags
from .script_builder import DailyPackage, build_script

DEFAULT_QUERY = "AI trading"
FALLBACK_HASHTAGS = ["#AITools", "#TradingTips", "#SideHustle", "#FutureOfMoney"]

logger = logging.getLogger(__name__)


def generate_daily_package(
    query: str = DEFAULT_QUERY,
    region: str = "united-states",
    output_dir: str | Path = "output",
) -> DailyPackage:
    """Fetch data, pick the hottest topic, and build the video script package."""
    news_items = fetch_google_news(query=query)
    hashtags = fetch_trending_hashtags(region=region)
    if not hashtags:
        hashtags = FALLBACK_HASHTAGS

    topic = pick_hot_topic(news_items, hashtags)
    if topic is None:
        raise RuntimeError("No trending AI trading stories found today.")

    package = build_script(topic, fallback_hashtags=FALLBACK_HASHTAGS)
    _persist_package(package, output_dir)
    return package


def _persist_package(package: DailyPackage, output_dir: str | Path) -> None:
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)

    text_output = path / "latest_prompt.txt"
    json_output = path / "latest_prompt.json"

    with text_output.open("w", encoding="utf-8") as f:
        f.write("=== TikTok Title ===\n")
        f.write(f"{package.tik_tok_title}\n\n")
        f.write("=== Viral Prompt ===\n")
        f.write(f"{package.script}\n\n")
        f.write("=== Recommended Hashtags ===\n")
        f.write(" ".join(package.recommended_hashtags) + "\n\n")
        f.write("=== Source ===\n")
        f.write(f"{package.source_name}: {package.source_link}\n")

    with json_output.open("w", encoding="utf-8") as f:
        json.dump(_package_to_json(package), f, indent=2, default=str)


def _package_to_json(package: DailyPackage) -> Dict[str, object]:
    data = asdict(package)
    data["created_at"] = package.created_at.isoformat()
    return data


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    pkg = generate_daily_package()
    logger.info("Generated new prompt: %s", pkg.tik_tok_title)
