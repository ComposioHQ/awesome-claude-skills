---
name: notion-find
description: Find a specific Notion page by title or partial title match. Use this skill when the user wants to locate a specific Notion page, asks "find my X page in Notion", or needs the page ID of a known page.
---

# Notion: Find Page

Locate a specific Notion page by title using the Notion MCP integration.

## When to Use

Use when the user:
- Says "find my [page name] in Notion"
- Needs to retrieve a specific page to read or update it
- Wants to confirm a page exists before creating a new one

## How to Find a Page

Use the `API-post-search` tool to search by title:

```json
{
  "query": "page title or keywords",
  "filter": {
    "property": "object",
    "value": "page"
  }
}
```

## Process

1. **Extract the search query** from the user's request
2. **Call `API-post-search`** with the title keywords
3. **Review results** — check `results[].properties.title` or `results[].title` for matches
4. **Handle multiple results**:
   - If one clear match: return the page ID and title
   - If multiple matches: list them and ask the user to confirm which one
   - If no match: inform the user and suggest searching with different terms

## Result Parsing

Notion search results have this structure:
```json
{
  "results": [
    {
      "id": "page-id-here",
      "object": "page",
      "url": "https://notion.so/...",
      "properties": {
        "title": {
          "title": [{ "plain_text": "Page Title" }]
        }
      }
    }
  ]
}
```

Extract the page title with: `result.properties.title.title[0].plain_text`

## Response Format

When a page is found:
```
Found: **[Page Title]**
ID: `[page-id]`
URL: [notion url]
```

When multiple results:
```
Found multiple pages matching "[query]":
1. [Title 1] — [url]
2. [Title 2] — [url]

Which one did you mean?
```

When not found:
```
No page found matching "[query]".

Try:
- Different keywords
- Checking if the page is in a database (use notion-database-query)
- Using notion-search for broader content search
```

## Notes

- Notion search only covers pages the integration has access to
- Search matches against page titles, not content
- For content search, use the `notion-search` skill
- Always confirm the right page before making changes to it
