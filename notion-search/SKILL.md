---
name: notion-search
description: Search Notion for pages and databases matching a query. Use this skill when the user wants to search across their Notion workspace, find pages or databases by keyword, or explore what's available in their Notion.
---

# Notion: Search Workspace

Search across the Notion workspace for pages and databases matching a query.

## When to Use

Use when the user:
- Wants to search across all of Notion (not just find one specific page)
- Asks "search Notion for X" or "what's in my Notion about Y"
- Wants to find both pages and databases matching a term
- Is exploring what exists in their workspace

## How to Search

Use `API-post-search` with optional filters:

**Search everything:**
```json
{
  "query": "search terms"
}
```

**Search only pages:**
```json
{
  "query": "search terms",
  "filter": { "property": "object", "value": "page" }
}
```

**Search only databases:**
```json
{
  "query": "search terms",
  "filter": { "property": "object", "value": "data_source" }
}
```

**Sort by most recently edited:**
```json
{
  "query": "search terms",
  "sort": { "direction": "descending", "timestamp": "last_edited_time" }
}
```

## Process

1. **Identify search intent** — does the user want pages, databases, or both?
2. **Run the search** with appropriate filters
3. **Parse results** — group by type (pages vs databases)
4. **Present results** clearly with titles, types, and URLs
5. **Offer next actions** — open a page, read content, etc.

## Result Parsing

```json
{
  "results": [
    {
      "object": "page",
      "id": "...",
      "url": "...",
      "properties": {
        "title": {
          "title": [{ "plain_text": "Page Title" }]
        }
      },
      "last_edited_time": "2025-01-15T10:00:00Z"
    },
    {
      "object": "database",
      "id": "...",
      "url": "...",
      "title": [{ "plain_text": "Database Name" }]
    }
  ]
}
```

For pages: `result.properties.title.title[0]?.plain_text`
For databases: `result.title[0]?.plain_text`

## Response Format

```
Search results for "[query]":

📄 Pages (X)
- [Title 1] — last edited [date] — [url]
- [Title 2] — last edited [date] — [url]

🗄 Databases (X)
- [Database Name] — [url]

No results? Try:
- Broader keywords
- Different spelling
- Checking workspace permissions
```

## Pagination

If there are many results, use `start_cursor` to paginate:
```json
{
  "query": "...",
  "start_cursor": "[cursor from previous result]",
  "page_size": 10
}
```

## Notes

- Notion search works on page/database titles, not full content
- Results are limited to pages the integration has access to
- If the user has large workspaces, suggest more specific search terms
- After finding relevant pages, offer to read their content using `API-get-block-children`
