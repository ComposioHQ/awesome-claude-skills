---
name: notion-database-query
description: Query a Notion database to retrieve, filter, and sort records. Use this skill when the user wants to list items in a Notion database, filter tasks by status/date/property, or get data out of a Notion database.
---

# Notion: Database Query

Retrieve and filter records from a Notion database.

## When to Use

Use when the user:
- Says "show me all my tasks in Notion"
- Wants to filter database entries ("show me tasks that are In Progress")
- Wants to sort database records
- Needs to read data out of a Notion database

## Process

### Step 1: Identify the Database

Find the database ID:
- Ask the user which database (by name)
- Use `API-post-search` with `filter: { value: "data_source" }` to find it
- Or use a known database ID if the user provides one

### Step 2: (Optional) Retrieve Schema

To understand what properties are filterable/sortable:
```
API-retrieve-a-data-source: { "data_source_id": "database-id" }
```

### Step 3: Query the Database

Use `API-query-data-source`:

**Basic query (all records):**
```json
{
  "data_source_id": "database-id"
}
```

**Filter by select property:**
```json
{
  "data_source_id": "database-id",
  "filter": {
    "property": "Status",
    "select": { "equals": "In Progress" }
  }
}
```

**Filter by checkbox:**
```json
{
  "data_source_id": "database-id",
  "filter": {
    "property": "Done",
    "checkbox": { "equals": false }
  }
}
```

**Filter by date:**
```json
{
  "data_source_id": "database-id",
  "filter": {
    "property": "Due Date",
    "date": { "on_or_before": "2025-03-31" }
  }
}
```

**Sort results:**
```json
{
  "data_source_id": "database-id",
  "sorts": [
    { "property": "Priority", "direction": "descending" },
    { "property": "Due Date", "direction": "ascending" }
  ]
}
```

**Combined filter and sort:**
```json
{
  "data_source_id": "database-id",
  "filter": {
    "and": [
      { "property": "Status", "select": { "equals": "To Do" } },
      { "property": "Priority", "select": { "equals": "High" } }
    ]
  },
  "sorts": [{ "property": "Due Date", "direction": "ascending" }]
}
```

## Filter Types Reference

| Property Type | Filter Options |
|--------------|----------------|
| `select` | `equals`, `does_not_equal`, `is_empty`, `is_not_empty` |
| `multi_select` | `contains`, `does_not_contain`, `is_empty`, `is_not_empty` |
| `checkbox` | `equals: true/false` |
| `date` | `equals`, `before`, `after`, `on_or_before`, `on_or_after`, `is_empty`, `is_not_empty` |
| `title` / `rich_text` | `equals`, `contains`, `starts_with`, `ends_with`, `is_empty`, `is_not_empty` |
| `number` | `equals`, `greater_than`, `less_than`, `greater_than_or_equal_to`, `less_than_or_equal_to` |

## Parsing Results

Results are in `results[]`, each with `properties`:
```json
{
  "results": [
    {
      "id": "page-id",
      "url": "https://notion.so/...",
      "properties": {
        "Name": { "title": [{ "plain_text": "Task title" }] },
        "Status": { "select": { "name": "In Progress" } },
        "Due Date": { "date": { "start": "2025-03-20" } }
      }
    }
  ]
}
```

## Response Format

Present results as a clear list:

```
Found X records in [Database Name]:

1. **[Title]** — Status: [status] | Due: [date]
2. **[Title]** — Status: [status] | Due: [date]
...

[If filtered]: Showing tasks filtered by [filter description].
```

## Pagination

If `has_more: true`, use `next_cursor` to get more results:
```json
{
  "data_source_id": "database-id",
  "start_cursor": "cursor-from-previous-response"
}
```

## Notes

- Filter property names are case-sensitive — match exactly what's in the schema
- Maximum page_size is 100 per request
- Combine `and`/`or` arrays for complex filters
- If the user doesn't know filter values, retrieve a few records first to see what options exist
