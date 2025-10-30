# TradingWizard AI Trend Prompt Generator

Daily script generator that scrapes fresh AI-trading headlines and social buzz so you can drop a TikTok-ready prompt for the TradingWizard AI brand in seconds.

## What it does
- Pulls the hottest `"AI trading"` stories from Google News.
- Collects the latest trending hashtags from X (via Trends24).
- Scores the stories for retail relevance, freshness, and hashtag overlap.
- Writes an energetic 30–60 second video script, plus a high-converting TikTok title.
- Saves the output to `output/latest_prompt.txt` and `output/latest_prompt.json` so you can copy-paste straight into Sora 2 or your post scheduler.
- If the network is blocked, it leans on a cached DeepSeek-vs-human-traders headline so you still get a draft script.

## Quick start
```bash
python3 -m venv .venv
source .venv/bin/activate
# Option A: install the CLI (requires internet access)
pip install -e .
tradingwizard-prompt

# Option B: run without installing
python run.py
cat output/latest_prompt.txt
```

## Output format
```
=== TikTok Title ===
<Headline remix> | TradingWizard AI Playbook

=== Viral Prompt ===
Stop scrolling—...

=== Recommended Hashtags ===
#AITools #TradingTips ...

=== Source ===
Bloomberg: https://...
```

The JSON version mirrors the same data for automation workflows.

## Configuration knobs
- **Query**: default is `"AI trading"`. Override with `TW_QUERY` env var or pass `--query` when you wire it into automation.
- **Region**: default Trends24 region is `united-states`. Override with `TW_REGION` env var or `--region`.
- **Output directory**: default `output/`. Change via `TW_OUTPUT_DIR` or `--output`.

Example manual run with overrides:
```bash
tradingwizard-prompt --query "quant trading AI" --region "canada" --output "daily-drops"
```

## GitHub Actions (optional daily run)
Add the following workflow to `.github/workflows/daily-prompt.yml` to generate and archive a fresh prompt every morning UTC:

```yaml
name: Daily TradingWizard Prompt

on:
  schedule:
    - cron: '15 11 * * *'  # 11:15 UTC every day
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -e .
      - run: tradingwizard-prompt
      - uses: actions/upload-artifact@v4
        with:
          name: tradingwizard-prompt
          path: output/
```

This stores the generated files as an artifact you can grab from the Actions tab. If you want it committed, add a commit-and-push step with a PAT.

## Brand tone guidelines baked in
- Conversational hooks that stop the scroll (`Stop scrolling`, `Hold up`, `Did you catch this?`).
- Explains the “why” for retail traders, side hustlers, and future-tech fans.
- Gives one actionable step (paper trade, set alerts, automate entries, etc.).
- Ends with a playful TradingWizard AI call-to-action.

Feel free to tweak `src/tradingwizard_ai_prompt/script_builder.py` if you want a different cadence or sign-off.
