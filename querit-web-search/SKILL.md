---
name: querit-web-search
description: Advanced web search using the Querit API with support for site filtering, time ranges, geolocation, and language targeting.
homepage: https://querit.ai
metadata: { "openclaw": { "emoji": "🔍", "requires": { "bins": ["python3"], "env":["QUERIT_API_KEY"]}, "primaryEnv":"QUERIT_API_KEY" } }
---

# Querit Advanced Search Skill

This skill provides OpenClaw with real-time web search capabilities. It supports complex filtering to retrieve highly accurate information.

**Notes:**

- Needs `QUERIT_API_KEY` from https://querit.ai
- Each account receives 1,000 free search queries to experience the content and capabilities.

## Trigger Conditions

- When the user asks for real-time news, specific facts, or up-to-date data.
- When the search requires constraints like specific dates, languages, countries, or particular websites.

## Supported Parameters

You can construct a JSON payload to use this tool. The payload supports the following fields:

- `query` (string, Required): The search query term.
- `count` (integer, Optional): The maximum number of search results to return.
- `filters` (object, Optional): Filter conditions to refine results.
  - `sites` (object): Specify which websites to include or exclude.
    - `include` (array of strings): Only fetch data from these domains (e.g., `["wikipedia.org", "nytimes.com"]`).
    - `exclude` (array of strings): Do not fetch data from these domains.
  - `timeRange` (object):
    - `date` (string): Options include:
      - `d[number]`: Past X days (e.g., `d7` for past 7 days).
      - `w[number]`: Past X weeks (e.g., `w2`).
      - `m[number]`: Past X months (e.g., `m6`).
      - `y[number]`: Past X years (e.g., `y1`).
      - `YYYY-MM-DDtoYYYY-MM-DD`: Specific date range (e.g., `2023-01-01to2023-12-31`).
  - `geo` (object):
    - `countries` -> `include` (array of strings): E.g., `["united states", "japan", "germany"]`.
  - `languages` (object):
    - `include` (array of strings): E.g., `["english", "japanese", "german", "french", "spanish"]`.

## Execution Instructions

Execute the included `search.py` script by passing a strict JSON string as the argument. Wrap the JSON string in single quotes.

**Example 1: Simple Search**

```bash
python skills/querit-web-search/scripts/search.py 'quantum computing breakthroughs'
```

**Example 2: Advanced Filtered Search**

```bash
python skills/querit-web-search/scripts/search.py '{
    "query": "artificial intelligence regulations",
    "count": 10,
    "filters": {
        "sites": {
            "include": ["techcrunch.com", "mondaq.com","europa.eu"]
        },
        "timeRange": {
            "date": "m3"
        },
        "geo": {
            "countries": {
                "include": ["united states", "united kingdom"]
            }
        },
        "languages": {
            "include": ["english"]
        }
    }
}'
```
