---
name: data-scraper-agent
description: Builds a fully automated AI-powered data collection agent for any public source — job listings, prices, news, GitHub repos, sports scores, events, and more. Scrapes on a schedule using GitHub Actions (free), enriches each result with an AI score and summary using Gemini Flash (free), stores to Notion or Sheets, and learns from your decisions over time. Zero hosting cost.
---

# Data Scraper Agent

Build a personal AI agent that monitors any public data source for you — automatically, on a schedule, for free.

Tell it what to watch (job boards, price pages, GitHub repos, news feeds, sports tables), and it scrapes the data, scores each result against your preferences, writes a plain-English summary of each item, and pushes everything into a Notion database or Google Sheet. Every time you mark something as "interested" or "skip", the agent learns and improves its scoring.

**Works with:** Claude Code · Python · GitHub Actions · Gemini Flash (free tier) · Notion

## When to Use This Skill

- You want to monitor a website or API for new listings without checking manually
- You're job hunting and want every relevant posting collected automatically
- You want to track product prices and know when they drop
- You want a daily digest of GitHub repos, news articles, or research papers on a topic
- You want AI to filter the noise — score and summarise each result so you only read what matters
- You want the agent to learn your taste over time based on what you save or skip

## What This Skill Does

1. **Designs the full agent architecture**: Generates a ready-to-run project structure with scrapers, an AI enrichment pipeline, and a storage layer — customisable via a single `config.yaml` file.

2. **Writes the scraper code**: Handles REST APIs, HTML pages, RSS feeds, and paginated sources. Each source is a single Python file with a `fetch()` function.

3. **Adds AI scoring and summarisation**: Every item gets a relevance score (0–100), a 2–3 sentence summary, and a personalised "why this matches you" note — using Gemini Flash via its free REST API. Batches 5 items per API call to stay within free tier limits.

4. **Builds a feedback learning loop**: Reads your decisions (Saved / Skipped / Rejected) from Notion after each run and biases future scoring based on your patterns. Gets smarter the more you use it.

5. **Deploys on GitHub Actions**: Generates a workflow file that runs the agent on a cron schedule — free for public repos, no server needed.

6. **Handles quota gracefully**: Auto-falls back across 4 Gemini models when one hits its rate limit, so runs never fail silently.

## How to Use

### Basic Usage

```
Build me an agent that scrapes Chief of Staff job listings from LinkedIn and Cutshort,
scores them against my resume, and pushes results to a Notion database every 3 hours.
```

```
Create a data scraper agent that monitors Product Hunt for new AI tools daily,
scores each by relevance to developer productivity, and saves top results to a Notion page.
```

```
Build an agent that watches Hacker News for posts mentioning "Series A" or "fundraising",
summarises each one, and pushes them to a Google Sheet every morning.
```

### Advanced Usage

```
Build a price monitoring agent that scrapes 3 e-commerce URLs for a product I'm watching,
tracks price history in Notion, and flags when the price drops more than 10%.
```

```
Create an agent that tracks new arXiv papers on LLM reasoning daily, scores each paper
by relevance to my research interests (in profile/context.md), and sends me the top 5
as a Notion digest. Deploy it free on GitHub Actions.
```

## Instructions

When a user asks to build a data scraper agent:

### Step 1: Understand the Goal

Ask these questions if not already clear:

1. **What to collect**: "What data source? A website URL, a public API, an RSS feed?"
2. **What fields to extract**: "What matters — title, price, URL, date, score, description?"
3. **How to filter**: "Any keywords to include or exclude?"
4. **How to enrich**: "Should the AI score relevance, summarise, or compare against your profile?"
5. **Where to store**: "Notion (recommended), Google Sheets, or local file?"
6. **How often**: "Hourly, every 3 hours, daily, weekly?"

Common targets to prompt for:
- Job boards (LinkedIn, Cutshort, Indeed, RemoteOK, Wellfound)
- Product listings (e-commerce, marketplaces)
- News and RSS feeds (Hacker News, TechCrunch, arXiv, Reddit)
- GitHub activity (new repos, releases, trending)
- Sports results and fixtures
- Events and conference listings
- Real estate listings

### Step 2: Generate the Project Structure

```
my-agent/
├── config.yaml              ← User edits this (keywords, filters, priorities, AI settings)
├── profile/
│   └── context.md           ← User's resume, interests, or criteria for AI matching
├── scraper/
│   ├── main.py              ← Orchestrator: scrape → deduplicate → AI enrich → store
│   ├── filters.py           ← Fast rule-based pre-filter (runs before AI)
│   └── sources/
│       └── source_name.py   ← One file per data source, each returns list[dict]
├── ai/
│   ├── client.py            ← Gemini REST client with 4-model fallback chain
│   ├── pipeline.py          ← Batch AI analysis (5 items per API call)
│   └── memory.py            ← Feedback learning from user decisions
├── storage/
│   └── notion_sync.py       ← Deduplicates by URL, pushes AI-enriched rows
├── data/
│   └── feedback.json        ← Auto-updated after each run (user decision history)
├── .env.example             ← Template for required credentials
├── setup.py                 ← One-time Notion database creation
├── enrich_existing.py       ← Backfill AI scores on rows added before AI was enabled
├── requirements.txt
└── .github/
    └── workflows/
        └── scraper.yml      ← GitHub Actions cron job (free)
```

### Step 3: Write the config.yaml

Always generate this file — it's the only thing users need to edit:

```yaml
# What to collect
filters:
  required_keywords:
    - "keyword users care about"
  blocked_keywords:
    - "junior"
    - "intern"

# AI scoring priorities
priorities:
  - "what the user cares about most"
  - "second priority"

# How often and from where
schedule: "every 3 hours"

# Feedback learning
feedback:
  positive_statuses: ["Saved", "Applied", "Interested"]
  negative_statuses: ["Skip", "Rejected", "Not relevant"]

# AI settings (free Gemini Flash)
ai:
  enabled: true
  model: "gemini-2.5-flash"
  min_score: 0
  batch_size: 5
  rate_limit_seconds: 7
```

### Step 4: Write the Scraper Source

One file per data source. Must return `list[dict]` with consistent fields:

```python
# scraper/sources/source_name.py
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from scraper.filters import is_relevant

HEADERS = {"User-Agent": "Mozilla/5.0"}

def fetch() -> list[dict]:
    results = []

    # REST API example
    resp = requests.get("https://api.example.com/items", headers=HEADERS, timeout=15)
    if resp.status_code == 200:
        for item in resp.json().get("results", []):
            title = item.get("title", "")
            if not is_relevant(title):
                continue
            results.append({
                "name": title,
                "url": item.get("link", ""),
                "source": "SourceName",
                "date_found": datetime.utcnow().date().isoformat(),
                # Add domain-specific fields (price, company, location, etc.)
            })

    return results
```

Include the right pattern for each source type:

**HTML scraping:**
```python
soup = BeautifulSoup(resp.text, "lxml")
for card in soup.select(".listing-card"):
    title = card.select_one("h2, h3").get_text(strip=True)
    url = card.select_one("a")["href"]
    if not url.startswith("http"):
        url = f"https://example.com{url}"
```

**RSS feed:**
```python
import xml.etree.ElementTree as ET
root = ET.fromstring(resp.text)
for item in root.findall(".//item"):
    title = item.findtext("title", "")
    url = item.findtext("link", "")
```

**Paginated API:**
```python
page = 1
while True:
    data = requests.get(url, params={"page": page}).json()
    items = data.get("results", [])
    if not items or not data.get("has_more"):
        break
    results.extend([_normalise(i) for i in items])
    page += 1
```

### Step 5: Write the AI Client

```python
# ai/client.py — Gemini REST API with auto-fallback, no SDK needed
import os, json, time, requests

_last_call = 0.0
MODEL_FALLBACK = [
    "gemini-2.0-flash-lite",  # 30 RPM — try first
    "gemini-2.0-flash",       # 15 RPM
    "gemini-2.5-flash",       # 10 RPM
    "gemini-flash-lite-latest",
]

def generate(prompt: str, model: str = "", rate_limit: float = 7.0) -> dict:
    global _last_call
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        return {}
    elapsed = time.time() - _last_call
    if elapsed < rate_limit:
        time.sleep(rate_limit - elapsed)
    models = [model] + [m for m in MODEL_FALLBACK if m != model] if model else MODEL_FALLBACK
    _last_call = time.time()
    for m in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={api_key}"
        try:
            resp = requests.post(url, json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"responseMimeType": "application/json", "temperature": 0.3, "maxOutputTokens": 2048},
            }, timeout=30)
            if resp.status_code == 200:
                return _parse(resp)
            if resp.status_code in (429, 404):
                time.sleep(1); continue
        except requests.RequestException:
            return {}
    return {}

def _parse(resp) -> dict:
    try:
        text = resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[-1].rsplit("```", 1)[0]
        return json.loads(text)
    except (json.JSONDecodeError, KeyError):
        return {}
```

### Step 6: Write the AI Pipeline (Batch)

Always batch — never call the API once per item:

```python
# ai/pipeline.py
from ai.client import generate

BATCH_SIZE = 5  # items per API call

def analyse_batch(items: list[dict], context: str = "", preference_prompt: str = "") -> list[dict]:
    batches = [items[i:i + BATCH_SIZE] for i in range(0, len(items), BATCH_SIZE)]
    print(f"  [AI] {len(items)} items → {len(batches)} API calls")
    enriched = []
    for i, batch in enumerate(batches):
        print(f"  [AI] Batch {i + 1}/{len(batches)}...")
        prompt = _build_prompt(batch, context, preference_prompt)
        result = generate(prompt)
        analyses = result.get("analyses", [])
        for j, item in enumerate(batch):
            ai = analyses[j] if j < len(analyses) else {}
            enriched.append({
                **item,
                "ai_score": max(0, min(100, int(ai.get("score", 0)))),
                "ai_summary": ai.get("summary", ""),
                "ai_notes": ai.get("notes", ""),
            } if ai else item)
    return enriched

def _build_prompt(batch, context, preference_prompt):
    items_text = "\n".join(
        f"Item {i+1}: {item.get('name','')} | {item.get('source','')} | {item.get('url','')}"
        for i, item in enumerate(batch)
    )
    return f"""Analyse these {len(batch)} items for the user.

Items:
{items_text}

User context: {context[:600]}

{preference_prompt}

Return: {{"analyses": [{{"score": <0-100>, "summary": "<2 sentences>", "notes": "<why relevant or not>"}} for each item in order]}}"""
```

### Step 7: Build Feedback Learning

```python
# ai/memory.py
import json
from pathlib import Path

FEEDBACK_PATH = Path(__file__).parent.parent / "data" / "feedback.json"

def load_feedback() -> dict:
    if FEEDBACK_PATH.exists():
        try: return json.loads(FEEDBACK_PATH.read_text())
        except: pass
    return {"positive": [], "negative": []}

def save_feedback(fb: dict):
    FEEDBACK_PATH.parent.mkdir(parents=True, exist_ok=True)
    FEEDBACK_PATH.write_text(json.dumps(fb, indent=2))

def build_preference_prompt(feedback: dict) -> str:
    lines = []
    if feedback.get("positive"):
        lines.append("Items the user LIKED:")
        lines.extend(f"- {e}" for e in feedback["positive"][-15:])
    if feedback.get("negative"):
        lines.append("\nItems the user SKIPPED:")
        lines.extend(f"- {e}" for e in feedback["negative"][-15:])
    if lines:
        lines.append("\nBias scoring based on these patterns.")
    return "\n".join(lines)
```

Pull user decisions from Notion before each run and call `save_feedback()` to persist the learning.

### Step 8: Write the GitHub Actions Workflow

```yaml
# .github/workflows/scraper.yml
name: Data Scraper Agent

on:
  schedule:
    - cron: "0 */3 * * *"  # Every 3 hours — adjust to your needs
  workflow_dispatch:        # Also allow manual trigger from GitHub UI

jobs:
  scrape:
    runs-on: ubuntu-latest
    timeout-minutes: 20
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11", cache: "pip" }
      - run: pip install -r requirements.txt
      - name: Run agent
        env:
          NOTION_TOKEN: ${{ secrets.NOTION_TOKEN }}
          NOTION_DATABASE_ID: ${{ secrets.NOTION_DATABASE_ID }}
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
        run: python -m scraper.main
      - name: Save feedback history
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add data/feedback.json || true
          git diff --cached --quiet || git commit -m "chore: update feedback"
          git push || true
```

### Step 9: Provide Setup Instructions

Always generate these final steps for the user:

```
1. pip install -r requirements.txt
2. Copy .env.example to .env and fill in credentials
3. python setup.py              # creates the Notion database
4. python -m scraper.main       # first local test run
5. python enrich_existing.py    # backfill AI scores if needed

GitHub Secrets to add (Settings → Secrets → Actions):
  NOTION_TOKEN         — from notion.so/my-integrations
  NOTION_DATABASE_ID   — printed by setup.py
  GEMINI_API_KEY       — free at aistudio.google.com/app/apikey
```

## Examples

### Example 1: Job Hunt Agent

**User**: "Build an agent that scrapes Chief of Staff and Founder's Office job listings from LinkedIn and Cutshort every 3 hours, scores each against my resume, and pushes to Notion."

**Output**:

The agent generates a complete project. After `python -m scraper.main`, Notion fills with rows like:

```
Rancho Labs — Founders Office
  AI Score:    90 / 100
  Match Score: 95 / 100
  Summary:     Early-stage B2B SaaS startup looking for a right-hand to the founder.
               Cross-functional role covering ops, GTM, and strategy.
  Why Fit:     Robin's 6-year ops background at sploot, with direct founder exposure
               and 200+ automations shipped, aligns precisely with this role.
  Status:      New
```

**Inspired by:** [imrobinsingh/job-hunt-agent](https://github.com/imrobinsingh/job-hunt-agent)

### Example 2: Product Price Monitor

**User**: "Watch these 3 URLs for a laptop I want to buy. Alert me in Notion when the price drops below ₹80,000."

**Output**: Agent scrapes all 3 URLs on a daily cron, extracts the current price, stores each reading with date, and sets Status to "Price Drop Alert" whenever it dips below the threshold.

### Example 3: GitHub Trending Tracker

**User**: "Every morning, collect the top 20 GitHub trending repos tagged with 'llm' or 'agent', summarise each one, and push to a Notion database sorted by stars."

**Output**: Agent calls the GitHub API, filters by topic, batches Gemini for summaries, and syncs to Notion. Each row has a 2-sentence summary and a relevance score against the user's stated interests.

### Example 4: News Digest Builder

**User**: "Build an agent that checks Hacker News and TechCrunch daily for posts about AI funding, summarises each article, classifies sentiment, and saves the top 10 to a Notion page."

**Output**: RSS + HN API scrapers, Gemini batch analysis with sentiment field, Notion DB with Score, Sentiment (Positive/Neutral/Negative), and Summary columns.

## Tips

- **Always use `config.yaml`** — never hardcode keywords or filters in code. Users will want to change them without touching Python.
- **Profile file beats a long prompt** — put the user's resume, interests, or criteria in `profile/context.md` and read it into the AI prompt. Keeps the main config clean.
- **Batch strictly** — 5 items per Gemini call is the sweet spot. Fewer wastes quota; more risks JSON truncation.
- **Set `maxOutputTokens: 2048`** — JSON responses for a 5-item batch need room. Too low = truncated JSON = parse error.
- **Test locally first** — run `python -m scraper.main` before pushing to GitHub Actions. Easier to debug.
- **Add `enrich_existing.py`** — users often enable AI after their first run. This script backfills scores on rows that missed enrichment.
- **Commit `feedback.json`** in the GitHub Actions workflow — this is how learning persists across runs without any external database.
- **JS-rendered sites** — if `requests` returns empty content, the page is rendered by JavaScript. Suggest `playwright` as an alternative.

## Common Use Cases

- Job hunting: collect and score listings across multiple boards automatically
- Price tracking: monitor e-commerce pages and alert on drops
- Research: daily digest of arXiv papers, GitHub repos, or blog posts on a topic
- News monitoring: filter, classify, and summarise news feeds by relevance
- Event tracking: scrape conference listings, meetups, or calendar feeds
- Sports: auto-update a results table from a public fixture API
- Real estate: watch listing sites for properties matching your criteria
- Competitive intel: monitor competitors' blog posts, job listings, or product pages

## Free Tier Limits

| Service | Free Limit | Typical Usage |
|---|---|---|
| Gemini Flash Lite | 30 RPM, 1,500 req/day | ~56 req/day at 3-hr runs |
| Gemini 2.0 Flash | 15 RPM, 1,500 req/day | Good fallback |
| GitHub Actions | Unlimited (public repos) | ~20 min/day |
| Notion API | Unlimited | ~200 writes/day |

This architecture is designed to run comfortably within all free limits indefinitely.
