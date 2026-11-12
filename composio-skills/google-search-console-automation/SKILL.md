---
name: google-search-console-automation
description: "Automate Google Search Console tasks via Rube MCP (Composio): query search analytics, list sites, inspect URLs, submit sitemaps, monitor search performance. Always search tools first for current schemas."
requires:
  mcp: [rube]
---

# Google Search Console Automation via Rube MCP

Query search analytics, inspect URLs, manage sitemaps, and monitor search performance using Google Search Console via Rube MCP (Composio).

**Toolkit docs**: [composio.dev/toolkits/google_search_console](https://composio.dev/toolkits/google_search_console)

## Prerequisites
- Rube MCP must be connected (RUBE_SEARCH_TOOLS available)
- Active connection via `RUBE_MANAGE_CONNECTIONS` with toolkit `google_search_console`
- Verified site ownership or appropriate permissions in Google Search Console
- Always call `RUBE_SEARCH_TOOLS` first to get current tool schemas

## Setup
**Get Rube MCP**: Add `https://rube.app/mcp` as an MCP server in your client configuration. No API keys needed — just add the endpoint and it works.

1. Verify Rube MCP is available by confirming `RUBE_SEARCH_TOOLS` responds
2. Call `RUBE_MANAGE_CONNECTIONS` with toolkit `google_search_console`
3. If connection is not ACTIVE, follow the returned auth link to complete setup
4. Confirm connection status shows ACTIVE before running any workflows

## Core Workflows

### 1. List All Verified Sites
Use `GOOGLE_SEARCH_CONSOLE_LIST_SITES` to retrieve all sites the authenticated user owns or has access to.
```
Tool: GOOGLE_SEARCH_CONSOLE_LIST_SITES
Parameters: (none required)
Returns: List of site entries with siteUrl and permissionLevel
```

### 2. Query Search Analytics
Use `GOOGLE_SEARCH_CONSOLE_SEARCH_ANALYTICS_QUERY` to get search performance data including clicks, impressions, CTR, and position.
```
Tool: GOOGLE_SEARCH_CONSOLE_SEARCH_ANALYTICS_QUERY
Parameters:
  - site_url (required): Site URL (e.g., "https://www.example.com/" or "sc-domain:example.com")
  - start_date (required): Start date in YYYY-MM-DD format
  - end_date (required): End date in YYYY-MM-DD format
  - dimensions: Group by ["query", "page", "country", "device", "date", "searchAppearance"]
  - search_type: "web" (default), "image", "video", "news", "discover", "googleNews"
  - dimension_filter_groups: Filters for dimensions (operator: equals, notEquals, contains, notContains, includingRegex, excludingRegex)
  - row_limit: Max rows (1-25000, default 1000)
  - start_row: Pagination offset (default 0)
  - aggregation_type: "auto", "byPage", "byProperty", "byNewsShowcasePanel"
  - data_state: "final" (default), "all", "hourly_all"
```

### 3. Inspect a URL
Use `GOOGLE_SEARCH_CONSOLE_INSPECT_URL` to check the indexing status and issues for a specific URL.
```
Tool: GOOGLE_SEARCH_CONSOLE_INSPECT_URL
Parameters:
  - inspection_url (required): Full URL to inspect (e.g., "https://www.example.com/page")
  - site_url (required): Property URL (e.g., "https://www.example.com/")
  - language_code: BCP-47 language (default: "en-US")
```

### 4. List Sitemaps
Use `GOOGLE_SEARCH_CONSOLE_LIST_SITEMAPS` to retrieve all sitemaps submitted for a site.
```
Tool: GOOGLE_SEARCH_CONSOLE_LIST_SITEMAPS
Parameters:
  - site_url (required): Site URL (e.g., "https://www.example.com/")
  - sitemap_index: Specific sitemap index URL to list sitemaps from
```

### 5. Submit a Sitemap
Use `GOOGLE_SEARCH_CONSOLE_SUBMIT_SITEMAP` to register or resubmit a sitemap for indexing.
```
Tool: GOOGLE_SEARCH_CONSOLE_SUBMIT_SITEMAP
Parameters:
  - site_url (required): Site URL or domain property (e.g., "sc-domain:example.com")
  - feedpath (required): Full sitemap URL (e.g., "https://www.example.com/sitemap.xml")
```

### 6. Get Sitemap Details
Use `GOOGLE_SEARCH_CONSOLE_GET_SITEMAP` to retrieve information about a specific submitted sitemap.
```
Tool: GOOGLE_SEARCH_CONSOLE_GET_SITEMAP
Parameters:
  - site_url (required): Site URL
  - feedpath (required): Sitemap URL to retrieve details for
```

## Common Patterns

- **Performance monitoring**: Use `GOOGLE_SEARCH_CONSOLE_SEARCH_ANALYTICS_QUERY` with `dimensions: ["date"]` over a date range to track daily search performance trends.
- **Top queries report**: Use `GOOGLE_SEARCH_CONSOLE_SEARCH_ANALYTICS_QUERY` with `dimensions: ["query"]` to find the most clicked search terms.
- **Page-level analysis**: Use `dimensions: ["page"]` to identify top-performing pages, then `dimensions: ["query", "page"]` to see which queries drive traffic to each page.
- **Indexing audit**: Use `GOOGLE_SEARCH_CONSOLE_INSPECT_URL` to check the indexing status of important pages.
- **Sitemap management**: Use `GOOGLE_SEARCH_CONSOLE_LIST_SITEMAPS` to verify submitted sitemaps, then `GOOGLE_SEARCH_CONSOLE_SUBMIT_SITEMAP` to submit new or updated ones.
- **Country/device breakdown**: Use `dimensions: ["country", "device"]` to understand geographic and device-type distribution of search traffic.
- **Filter for specific queries**: Use `dimension_filter_groups` with `contains` or `includingRegex` operators to focus on specific keyword groups.

## Known Pitfalls

- **Site URL format matters**: URL-prefix properties use the full URL with protocol and trailing slash (e.g., `https://www.example.com/`). Domain properties use the `sc-domain:` prefix (e.g., `sc-domain:example.com`). Using the wrong format will return empty results or errors.
- **Date range limits**: Data is typically available with a 2-3 day delay. `data_state: "all"` includes fresher data that may still change. `hourly_all` only works for dates within the last 3 days.
- **Row limit pagination**: The API returns top results sorted by clicks (or by date when grouping by date). For complete data, paginate using `start_row` with the `row_limit`.
- **Max 25,000 rows per request**: Even with pagination, each request returns at most 25,000 rows. For very large datasets, narrow your date range or add dimension filters.
- **Inspection URL must match site**: The `inspection_url` must be a page under the `site_url` property. Cross-property inspections will fail.
- **Sitemap must be accessible**: `GOOGLE_SEARCH_CONSOLE_SUBMIT_SITEMAP` requires the sitemap file to be publicly accessible at the specified URL and properly formatted as XML.
- **Results sorted by clicks**: By default, analytics results are sorted by click count descending, except when grouping by `date` (which sorts by date ascending).

## Quick Reference
| Action | Tool | Key Parameters |
|--------|------|----------------|
| List sites | `GOOGLE_SEARCH_CONSOLE_LIST_SITES` | (none) |
| Search analytics | `GOOGLE_SEARCH_CONSOLE_SEARCH_ANALYTICS_QUERY` | `site_url`, `start_date`, `end_date`, `dimensions` |
| Inspect URL | `GOOGLE_SEARCH_CONSOLE_INSPECT_URL` | `inspection_url`, `site_url` |
| List sitemaps | `GOOGLE_SEARCH_CONSOLE_LIST_SITEMAPS` | `site_url` |
| Submit sitemap | `GOOGLE_SEARCH_CONSOLE_SUBMIT_SITEMAP` | `site_url`, `feedpath` |
| Get sitemap info | `GOOGLE_SEARCH_CONSOLE_GET_SITEMAP` | `site_url`, `feedpath` |

---
*Powered by [Composio](https://composio.dev)*
