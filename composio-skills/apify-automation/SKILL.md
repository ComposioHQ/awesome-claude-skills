---
name: Apify Automation
description: "Automate web scraping and data extraction with Apify -- run Actors, manage datasets, create reusable tasks, and retrieve crawl results through the Composio Apify integration."
requires:
  mcp:
    - rube
---

# Apify Automation

Run **Apify** web scraping Actors and manage datasets directly from Claude Code. Execute crawlers synchronously or asynchronously, retrieve structured data, create reusable tasks, and inspect run logs without leaving your terminal.

**Toolkit docs:** [composio.dev/toolkits/apify](https://composio.dev/toolkits/apify)

---

## Setup

1. Add the Composio MCP server to your configuration:
   ```
   https://rube.app/mcp
   ```
2. Connect your Apify account when prompted. The agent will provide an authentication link.
3. Browse available Actors at [apify.com/store](https://apify.com/store). Each Actor has its own unique input schema -- always check the Actor's documentation before running.

---

## Core Workflows

### 1. Run an Actor Synchronously and Get Results

Execute an Actor and immediately retrieve its dataset items in a single call. Best for quick scraping jobs.

**Tool:** `APIFY_RUN_ACTOR_SYNC_GET_DATASET_ITEMS`

Key parameters:
- `actorId` (required) -- Actor ID in format `username/actor-name` (e.g., `compass/crawler-google-places`)
- `input` -- JSON input object matching the Actor's schema. Each Actor has unique field names -- check [apify.com/store](https://apify.com/store) for the exact schema.
- `limit` -- max items to return
- `offset` -- skip items for pagination
- `format` -- `json` (default), `csv`, `jsonl`, `html`, `xlsx`, `xml`
- `timeout` -- run timeout in seconds
- `waitForFinish` -- max wait time (0-300 seconds)
- `fields` -- comma-separated list of fields to include
- `omit` -- comma-separated list of fields to exclude

Example prompt: *"Run the Google Places scraper for 'restaurants in New York' and return the first 50 results"*

---

### 2. Run an Actor Asynchronously

Trigger an Actor run without waiting for completion. Use for long-running scraping jobs.

**Tool:** `APIFY_RUN_ACTOR`

Key parameters:
- `actorId` (required) -- Actor slug or ID
- `body` -- JSON input object for the Actor
- `memory` -- memory limit in MB (must be power of 2, minimum 128)
- `timeout` -- run timeout in seconds
- `maxItems` -- cap on returned items
- `build` -- specific build tag (e.g., `latest`, `beta`)

Follow up with `APIFY_GET_DATASET_ITEMS` to retrieve results using the run's `datasetId`.

Example prompt: *"Start the web scraper Actor for example.com asynchronously with 1024MB memory"*

---

### 3. Retrieve Dataset Items

Fetch data from a specific dataset with pagination, field selection, and filtering.

**Tool:** `APIFY_GET_DATASET_ITEMS`

Key parameters:
- `datasetId` (required) -- dataset identifier
- `limit` (default/max 1000) -- items per page
- `offset` (default 0) -- pagination offset
- `format` -- `json` (recommended), `csv`, `xlsx`
- `fields` -- include only specific fields
- `omit` -- exclude specific fields
- `clean` -- remove Apify-specific metadata
- `desc` -- reverse order (newest first)

Example prompt: *"Get the first 500 items from dataset myDatasetId in JSON format"*

---

### 4. Inspect Actor Details

View Actor metadata, input schema, and configuration before running it.

**Tool:** `APIFY_GET_ACTOR`

Key parameters:
- `actorId` (required) -- Actor ID in format `username/actor-name` or hex ID

Example prompt: *"Show me the details and input schema for the apify/web-scraper Actor"*

---

### 5. Create Reusable Tasks

Configure reusable Actor tasks with preset inputs for recurring scraping jobs.

**Tool:** `APIFY_CREATE_TASK`

Configure a task once, then trigger it repeatedly with consistent input parameters. Useful for scheduled or recurring data collection workflows.

Example prompt: *"Create an Apify task for the Google Search scraper with default query 'AI startups' and US location"*

---

### 6. Manage Runs and Datasets

List Actor runs, browse datasets, and inspect run details for monitoring and debugging.

**Tools:** `APIFY_GET_LIST_OF_RUNS`, `APIFY_DATASETS_GET`, `APIFY_DATASET_GET`, `APIFY_GET_LOG`

For listing runs:
- Filter by Actor and optionally by status
- Get `datasetId` from run details for data retrieval

For dataset management:
- `APIFY_DATASETS_GET` -- list all your datasets with pagination
- `APIFY_DATASET_GET` -- get metadata for a specific dataset

For debugging:
- `APIFY_GET_LOG` -- retrieve execution logs for a run or build

Example prompt: *"List the last 10 runs for the web scraper Actor and show logs for the most recent one"*

---

## Known Pitfalls

- **Actor input schemas vary wildly:** Every Actor has its own unique input fields. Generic field names like `queries` or `search_terms` will be rejected. Always check the Actor's page on [apify.com/store](https://apify.com/store) for exact field names (e.g., `searchStringsArray` for Google Maps, `startUrls` for web scrapers).
- **URL format requirements:** Always include the full protocol (`https://` or `http://`) in URLs. Many Actors require URLs as objects with a `url` property: `{"startUrls": [{"url": "https://example.com"}]}`.
- **Dataset pagination cap:** `APIFY_GET_DATASET_ITEMS` has a max `limit` of 1000 per call. For large datasets, loop with `offset` to collect all items.
- **Enum values are lowercase:** Most Actors expect lowercase enum values (e.g., `relevance` not `RELEVANCE`, `all` not `ALL`).
- **Sync timeout at 5 minutes:** `APIFY_RUN_ACTOR_SYNC_GET_DATASET_ITEMS` has a maximum `waitForFinish` of 300 seconds. For longer runs, use `APIFY_RUN_ACTOR` (async) and poll with `APIFY_GET_DATASET_ITEMS`.
- **Data volume costs:** Large datasets can be expensive to fetch. Prefer moderate limits and incremental processing to avoid timeouts or memory pressure.
- **JSON format recommended:** While CSV/XLSX formats are available, JSON is the most reliable for automated processing. Avoid CSV/XLSX for downstream automation.

---

## Quick Reference

| Tool Slug | Description |
|---|---|
| `APIFY_RUN_ACTOR_SYNC_GET_DATASET_ITEMS` | Run Actor synchronously and get results immediately |
| `APIFY_RUN_ACTOR` | Run Actor asynchronously (trigger and return) |
| `APIFY_RUN_ACTOR_SYNC` | Run Actor synchronously, return output record |
| `APIFY_GET_ACTOR` | Get Actor metadata and input schema |
| `APIFY_GET_DATASET_ITEMS` | Retrieve items from a dataset (paginated) |
| `APIFY_DATASET_GET` | Get dataset metadata (item count, etc.) |
| `APIFY_DATASETS_GET` | List all user datasets |
| `APIFY_CREATE_TASK` | Create a reusable Actor task |
| `APIFY_GET_TASK_INPUT` | Inspect a task's stored input |
| `APIFY_GET_LIST_OF_RUNS` | List runs for an Actor |
| `APIFY_GET_LOG` | Get execution logs for a run |

---

*Powered by [Composio](https://composio.dev)*
