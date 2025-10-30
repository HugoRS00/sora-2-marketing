from __future__ import annotations

import argparse
import logging
import os

from .main import DEFAULT_QUERY, generate_daily_package


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate TradingWizard AI daily prompt.")
    parser.add_argument(
        "--query",
        default=os.getenv("TW_QUERY", DEFAULT_QUERY),
        help="Google News search query (default: %(default)s)",
    )
    parser.add_argument(
        "--region",
        default=os.getenv("TW_REGION", "united-states"),
        help="Trends24 region slug (default: %(default)s)",
    )
    parser.add_argument(
        "--output",
        default=os.getenv("TW_OUTPUT_DIR", "output"),
        help="Output directory for generated files (default: %(default)s)",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    package = generate_daily_package(
        query=args.query,
        region=args.region,
        output_dir=args.output,
    )
    logging.info("Generated prompt: %s", package.tik_tok_title)


if __name__ == "__main__":
    main()
