---
name: notion-create-task
description: Create a new task or entry in a Notion database. Use this skill when the user wants to add a task, to-do item, project entry, or any record to a Notion database.
---

# Notion: Create Task

Add a new entry (task, to-do, record) to a Notion database.

## When to Use

Use when the user:
- Says "add a task to Notion" or "create a to-do in Notion"
- Wants to add an entry to a specific Notion database
- Needs to log something (a bug, a lead, a project entry)

## Process

### Step 1: Identify the Target Database

Ask or infer which database the task should go into:
- "Which database should this go in? (e.g., Tasks, Projects, Backlog)"
- Or search for it: use `API-post-search` with `filter: { value: "data_source" }`

Get the database ID.

### Step 2: Retrieve Database Schema

Before creating an entry, understand what properties the database has:

```
API-retrieve-a-data-source: { "data_source_id": "database-id" }
```

This returns the database's `properties` object, which defines:
- Property names
- Property types (title, rich_text, select, multi_select, date, checkbox, number, etc.)

### Step 3: Gather Task Details

Collect from the user what's needed based on the database schema:
- **Title** (always required)
- **Status** (if the database has a status property)
- **Due date** (if relevant)
- **Assignee** (if relevant)
- **Priority** / **Tags** / other fields

### Step 4: Create the Entry

Use `API-post-page` with the database as parent:

```json
{
  "parent": {
    "type": "database_id",
    "database_id": "database-id"
  },
  "properties": {
    "Name": {
      "title": [{ "type": "text", "text": { "content": "Task title" } }]
    },
    "Status": {
      "select": { "name": "To Do" }
    },
    "Due Date": {
      "date": { "start": "2025-03-20" }
    },
    "Priority": {
      "select": { "name": "High" }
    },
    "Tags": {
      "multi_select": [{ "name": "Engineering" }]
    }
  }
}
```

## Property Type Reference

| Type | Format |
|------|--------|
| `title` | `[{ "type": "text", "text": { "content": "..." } }]` |
| `rich_text` | `[{ "type": "text", "text": { "content": "..." } }]` |
| `select` | `{ "name": "option name" }` |
| `multi_select` | `[{ "name": "tag1" }, { "name": "tag2" }]` |
| `date` | `{ "start": "YYYY-MM-DD" }` |
| `checkbox` | `true` or `false` |
| `number` | `42` |
| `url` | `"https://..."` |

## Response Format

On success:
```
✅ Task created: **[Task Title]**
Database: [database name]
URL: [notion url]
```

Include any relevant properties that were set (status, due date, etc.).

## Notes

- Always retrieve the database schema first — property names are case-sensitive
- Select options must match existing options in the database (or will create new ones if allowed)
- If the user didn't provide required fields, ask before creating
- After creating, offer to add body content to the task page if needed
