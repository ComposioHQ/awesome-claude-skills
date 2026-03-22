---
name: Firecrawl Automation
description: "Automate web crawling and data extraction with Firecrawl -- scrape pages, crawl sites, extract structured data, batch scrape URLs, and map website structures through the Composio Firecrawl integration."
requires:
  mcp:
    - rube
---

# Firecrawl Automation

Run **Firecrawl** web crawling and extraction directly from Claude Code. Scrape individual pages, crawl entire sites, extract structured data with AI, batch process URL lists, and map website structures without leaving your terminal.

**Toolkit docs:** [composio.dev/toolkits/firecrawl](https://composio.dev/toolkits/firecrawl)

---

## Setup

1. Add the Composio MCP server to your configuration:
   ```
   https://rube.app/mcp
   ```
2. Connect your Firecrawl account when prompted. The agent will provide an authentication link.
3. Be mindful of credit consumption -- scope your crawls tightly and test on small URL sets before scaling.

---

## Core Workflows

### 1. Scrape a Single Page

Fetch content from a URL in multiple formats with optional browser actions for dynamic pages.

**Tool:** `FIRECRAWL_SCRAPE`

Key parameters:
- `url` (required) -- fully qualified URL to scrape
- `formats` -- output formats: `markdown` (default), `html`, `rawHtml`, `links`, `screenshot`, `json`
- `onlyMainContent` (default true) -- extract main content only, excluding nav/footer/ads
- `waitFor` -- milliseconds to wait for JS rendering (default 0)
- `timeout` -- max wait in ms (default 30000)
- `actions` -- browser actions before scraping (click, write, wait, press, scroll)
- `includeTags` / `excludeTags` -- filter by HTML tags
- `jsonOptions` -- for structured extraction with `schema` and/or `prompt`

Example prompt: *"Scrape the main content from https://example.com/pricing as markdown"*

---

### 2. Crawl an Entire Site

Discover and scrape multiple pages from a website with configurable depth, path filters, and concurrency.

**Tool:** `FIRECRAWL_CRAWL_V2`

Key parameters:
- `url` (required) -- starting URL for the crawl
- `limit` (default 10) -- max pages to crawl
- `maxDiscoveryDepth` -- depth limit from the root page
- `includePaths` / `excludePaths` -- regex patterns for URL paths
- `allowSubdomains` -- include subdomains (default false)
- `crawlEntireDomain` -- follow sibling/parent links, not just children (default false)
- `sitemap` -- `include` (default), `skip`, or `only`
- `prompt` -- natural language to auto-configure crawler settings
- `scrapeOptions_formats` -- output format for each page
- `scrapeOptions_onlyMainContent` -- main content extraction per page

Example prompt: *"Crawl the docs section of firecrawl.dev, max 50 pages, only paths matching docs"*

---

### 3. Extract Structured Data

Extract structured JSON data from web pages using AI with a natural language prompt or JSON schema.

**Tool:** `FIRECRAWL_EXTRACT`

Key parameters:
- `urls` (required) -- array of URLs to extract from (max 10 in beta). Supports wildcards like `https://example.com/blog/*`
- `prompt` -- natural language description of what to extract
- `schema` -- JSON Schema defining the desired output structure
- `enable_web_search` -- allow crawling links outside initial domains (default false)

At least one of `prompt` or `schema` must be provided.

Check extraction status with `FIRECRAWL_EXTRACT_GET` using the returned job `id`.

Example prompt: *"Extract company name, pricing tiers, and feature lists from https://example.com/pricing"*

---

### 4. Batch Scrape Multiple URLs

Scrape many URLs concurrently with shared configuration for efficient bulk data collection.

**Tool:** `FIRECRAWL_BATCH_SCRAPE`

Key parameters:
- `urls` (required) -- array of URLs to scrape
- `formats` -- output format for all pages (default `markdown`)
- `onlyMainContent` (default true) -- main content extraction
- `maxConcurrency` -- parallel scrape limit
- `ignoreInvalidURLs` (default true) -- skip bad URLs instead of failing the batch
- `location` -- geolocation settings with `country` code
- `actions` -- browser actions applied to each page
- `blockAds` (default true) -- block advertisements

Example prompt: *"Batch scrape these 20 product page URLs as markdown with ad blocking"*

---

### 5. Map Website Structure

Discover all URLs on a website from a starting URL, useful for planning crawls or auditing site structure.

**Tool:** `FIRECRAWL_MAP_MULTIPLE_URLS_BASED_ON_OPTIONS`

Key parameters:
- `url` (required) -- starting URL (must be `https://` or `http://`)
- `search` -- guide URL discovery toward specific page types
- `limit` (default 5000, max 100000) -- max URLs to return
- `includeSubdomains` (default true) -- include subdomains
- `ignoreQueryParameters` (default true) -- dedupe URLs differing only by query params
- `sitemap` -- `include`, `skip`, or `only`

Example prompt: *"Map all URLs on docs.example.com, focusing on API reference pages"*

---

### 6. Monitor and Manage Crawl Jobs

Track crawl progress, retrieve results, and cancel runaway jobs.

**Tools:** `FIRECRAWL_CRAWL_GET`, `FIRECRAWL_GET_THE_STATUS_OF_A_CRAWL_JOB`, `FIRECRAWL_CANCEL_A_CRAWL_JOB`

- `FIRECRAWL_CRAWL_GET` -- get status, progress, credits used, and crawled page data
- `FIRECRAWL_CANCEL_A_CRAWL_JOB` -- stop an active or queued crawl

Both require the crawl job `id` (UUID) returned when the crawl was initiated.

Example prompt: *"Check the status of crawl job 019b0806-b7a1-7652-94c1-e865b5d2e89a"*

---

## Known Pitfalls

- **Rate limiting:** Firecrawl can trigger "Rate limit exceeded" errors (429). Prefer `FIRECRAWL_BATCH_SCRAPE` over many individual `FIRECRAWL_SCRAPE` calls, and implement backoff on 429/5xx responses.
- **Credit consumption:** `FIRECRAWL_EXTRACT` can fail with "Insufficient credits." Scope tightly and avoid broad homepage URLs that yield sparse fields. Test on small URL sets first.
- **Nested error responses:** Per-page failures may be nested in `response.data.code` (e.g., `SCRAPE_DNS_RESOLUTION_ERROR`) even when the outer API call succeeds. Always validate inner status/error fields.
- **JS-heavy pages:** Non-rendered fetches may miss key content. Use `waitFor` (e.g., 1000-5000ms) for dynamic pages, or configure `scrapeOptions_actions` to interact with the page before scraping.
- **Extraction schema precision:** Vague or shifting schemas/prompts produce noisy, inconsistent output. Freeze your schema and test on a small sample before scaling to many URLs.
- **Crawl jobs are async:** `FIRECRAWL_CRAWL_V2` returns immediately with a job ID. Use `FIRECRAWL_CRAWL_GET` to poll for results. Cancel stuck crawls with `FIRECRAWL_CANCEL_A_CRAWL_JOB` to avoid wasting credits.
- **Extract job polling:** `FIRECRAWL_EXTRACT` is also async for larger jobs. Retrieve final output with `FIRECRAWL_EXTRACT_GET`.
- **URL batching for extract:** Keep extract URL batches small (~10 URLs) to avoid 429 rate limit errors.
- **Deeply nested responses:** Results are often nested under `data.data` or deeper. Inspect the returned shape rather than assuming flat keys.

---

## Quick Reference

| Tool Slug | Description |
|---|---|
| `FIRECRAWL_SCRAPE` | Scrape a single URL with format/action options |
| `FIRECRAWL_CRAWL_V2` | Crawl a website with depth/path control |
| `FIRECRAWL_EXTRACT` | Extract structured data with AI prompt/schema |
| `FIRECRAWL_BATCH_SCRAPE` | Batch scrape multiple URLs concurrently |
| `FIRECRAWL_MAP_MULTIPLE_URLS_BASED_ON_OPTIONS` | Discover/map all URLs on a site |
| `FIRECRAWL_CRAWL_GET` | Get crawl job status and results |
| `FIRECRAWL_GET_THE_STATUS_OF_A_CRAWL_JOB` | Check crawl job progress |
| `FIRECRAWL_CANCEL_A_CRAWL_JOB` | Cancel an active crawl job |
| `FIRECRAWL_EXTRACT_GET` | Get extraction job status and results |
| `FIRECRAWL_CRAWL_PARAMS_PREVIEW` | Preview crawl parameters before starting |
| `FIRECRAWL_SEARCH` | Web search + scrape top results |

---

*Powered by [Composio](https://composio.dev)*
