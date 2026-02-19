---
name: SEMrush Automation
description: "Automate SEO analysis with SEMrush -- research keywords, analyze domain organic rankings, audit backlinks, assess keyword difficulty, and discover related terms through the Composio SEMrush integration."
requires:
  mcp:
    - rube
---

# SEMrush Automation

Run **SEMrush** SEO analytics directly from Claude Code. Analyze domain keywords, audit backlink profiles, research keyword difficulty, discover related terms, and track organic page performance without leaving your terminal.

**Toolkit docs:** [composio.dev/toolkits/semrush](https://composio.dev/toolkits/semrush)

---

## Setup

1. Add the Composio MCP server to your configuration:
   ```
   https://rube.app/mcp
   ```
2. Connect your SEMrush account when prompted. The agent will provide an authentication link.
3. All SEMrush tools require a `database` parameter specifying the regional database (e.g., `us`, `uk`, `de`). Choose the correct region for your target audience.

---

## Core Workflows

### 1. Domain Organic Keywords Analysis

Retrieve all organic search keywords for a domain, including positions, traffic estimates, CPC, and keyword difficulty.

**Tool:** `SEMRUSH_DOMAIN_ORGANIC_SEARCH_KEYWORDS`

Key parameters:
- `domain` (required) -- e.g., `example.com`
- `database` (required) -- regional database code (e.g., `us`, `uk`, `de`)
- `display_limit` (default 10000) and `display_offset` (default 0) -- pagination
- `display_sort` -- sort by position, traffic, volume, etc. (e.g., `tr_desc` for traffic descending)
- `display_date` -- historical data in `YYYYMM15` format (monthly) or `YYYYMMDD` (daily)
- `export_columns` -- specify columns like `Ph` (phrase), `Po` (position), `Nq` (volume), `Tr` (traffic), `Kd` (difficulty)
- `display_filter` -- filter by specific columns

Example prompt: *"Get the top 100 organic keywords for example.com in the US database, sorted by traffic"*

---

### 2. Keyword Overview and Batch Analysis

Get detailed metrics for individual keywords or analyze up to 100 keywords at once.

**Tools:** `SEMRUSH_KEYWORD_OVERVIEW_ONE_DATABASE`, `SEMRUSH_BATCH_KEYWORD_OVERVIEW`

For single keyword:
- `phrase` (required) -- keyword to investigate
- `database` (required) -- regional database

For batch (up to 100 keywords):
- `phrase` (required) -- semicolon-separated keywords (max 255 chars total)
- `database` (required) -- regional database
- `export_columns` -- `Ph` (phrase), `Nq` (volume), `Cp` (CPC), `Co` (competition), `Kd` (difficulty), `In` (intent)

Example prompt: *"Get keyword metrics for 'seo services;content marketing;link building' in the US database"*

---

### 3. Domain Organic Pages Report

Discover which URLs on a domain drive the most organic traffic and visibility.

**Tool:** `SEMRUSH_DOMAIN_ORGANIC_PAGES`

Key parameters:
- `domain` (required) -- target domain
- `database` (required) -- regional database
- `display_sort` -- e.g., `pc_desc` for traffic share descending
- `display_limit` and `display_offset` -- pagination
- `export_columns` -- `Ur` (URL), `Pc` (traffic %), `Tg` (traffic), `Tr` (traffic cost)

Example prompt: *"Show the top 50 organic pages for example.com ranked by traffic share"*

---

### 4. Backlink Profile Overview

Get a summary of backlinks for a domain including Authority Score, link types, and referring domain counts.

**Tool:** `SEMRUSH_BACKLINKS_OVERVIEW`

Key parameters:
- `target` (required) -- domain, subdomain, or full URL
- `target_type` (required) -- `root_domain`, `domain`, or `url`
- `export_columns` -- `ascore` (Authority Score), `total` (total backlinks), `domains_num` (referring domains), `follows_num`, `nofollows_num`, etc.

Example prompt: *"Get the backlink overview for example.com including Authority Score and referring domain count"*

---

### 5. Keyword Difficulty Assessment

Score how hard it is to rank in the top 10 for specific keywords (0-100 scale).

**Tool:** `SEMRUSH_KEYWORD_DIFFICULTY`

Key parameters:
- `phrase` (required) -- keyword to analyze
- `database` (required) -- regional database
- `export_columns` -- `Ph` (phrase), `Kd` (difficulty score)

Example prompt: *"What is the keyword difficulty for 'best project management software' in the US?"*

---

### 6. Discover Related Keywords

Find synonyms, variations, and related terms for a seed keyword to expand your content strategy.

**Tool:** `SEMRUSH_RELATED_KEYWORDS`

Key parameters:
- `phrase` (required) -- seed keyword
- `database` (required) -- regional database
- `display_limit` (default 10000) -- max results
- `display_sort` -- e.g., `nq_desc` for volume descending, `kd_asc` for easiest first
- `export_columns` -- `Ph`, `Nq`, `Kd`, `Cp`, `Co`, `Rr` (relatedness score)

Example prompt: *"Find related keywords for 'project management' in the US, sorted by search volume"*

---

## Known Pitfalls

- **Pagination is essential:** `SEMRUSH_DOMAIN_ORGANIC_SEARCH_KEYWORDS` and `SEMRUSH_DOMAIN_ORGANIC_PAGES` can return very large datasets. Always use `display_limit` and `display_offset` instead of assuming a single page is complete.
- **CSV-style responses:** Many SEMrush tools return data as CSV-style text in a single field (e.g., `data/keyword_data`). You must parse rows and columns before analysis or joining reports.
- **"ERROR 50 :: NOTHING FOUND":** This literal string means the domain or keyword has no data in that database. Treat it as a valid zero-result response, not a transport error.
- **Batch keyword limits:** `SEMRUSH_BATCH_KEYWORD_OVERVIEW` may return HTTP 400 for problematic or oversized batches (max 255 chars total for the `phrase` field). Shrink batches or fall back to `SEMRUSH_KEYWORD_OVERVIEW_ONE_DATABASE` for individual lookups.
- **Date format:** Historical dates must use `YYYYMM15` format for monthly data (e.g., `20231015`). Using an incorrect format will return unexpected results.
- **Regional database matters:** Always use the correct regional database for your target audience. Results for `us` vs `uk` can differ dramatically in volume, CPC, and rankings.
- **Column codes:** Export columns use short codes (`Ph`, `Nq`, `Kd`, etc.). Avoid over-narrowing `export_columns` so key metrics like traffic, CPC, position, and difficulty are retained.

---

## Quick Reference

| Tool Slug | Description |
|---|---|
| `SEMRUSH_DOMAIN_ORGANIC_SEARCH_KEYWORDS` | Organic keywords for a domain with positions and traffic |
| `SEMRUSH_KEYWORD_OVERVIEW_ONE_DATABASE` | Single keyword metrics (volume, CPC, difficulty) |
| `SEMRUSH_BATCH_KEYWORD_OVERVIEW` | Batch metrics for up to 100 keywords |
| `SEMRUSH_DOMAIN_ORGANIC_PAGES` | Top organic pages for a domain by traffic |
| `SEMRUSH_BACKLINKS_OVERVIEW` | Backlink profile summary with Authority Score |
| `SEMRUSH_BACKLINKS` | Detailed backlinks list for a target |
| `SEMRUSH_KEYWORD_DIFFICULTY` | Keyword difficulty score (0-100) |
| `SEMRUSH_RELATED_KEYWORDS` | Related/similar keywords for a seed phrase |
| `SEMRUSH_CATEGORIES` | Domain categories with confidence ratings |
| `SEMRUSH_DOMAIN_ORGANIC_SUBDOMAINS` | Subdomain-level organic rankings breakdown |

---

*Powered by [Composio](https://composio.dev)*
