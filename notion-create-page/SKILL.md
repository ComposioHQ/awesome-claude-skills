---
name: notion-create-page
description: Create a new Notion page with content. Use this skill when the user wants to create a new page in Notion, add a document, write a note, or create a wiki entry.
---

# Notion: Create Page

Create a new Notion page with a title and content.

## When to Use

Use when the user:
- Says "create a page in Notion"
- Wants to add a new note, document, or wiki entry
- Needs to write content to Notion
- Wants to create a sub-page under an existing page

## Process

### Step 1: Determine Where to Create the Page

Ask or infer:
- **Parent page**: Should this live under an existing page? If yes, get the parent page ID using `notion-find`.
- **Workspace root**: If no parent is specified, create at the workspace level.
- **Database**: If it should be an entry in a database, use `notion-create-task` instead.

### Step 2: Prepare the Content

Gather from the user:
- **Title**: The page title (required)
- **Content**: Body text, structured content, etc.

### Step 3: Create the Page

Use `API-post-page`:

**Create at workspace root:**
```json
{
  "parent": { "type": "workspace" },
  "properties": {
    "title": {
      "title": [{ "type": "text", "text": { "content": "Page Title" } }]
    }
  }
}
```

**Create under a parent page:**
```json
{
  "parent": { "page_id": "parent-page-id" },
  "properties": {
    "title": {
      "title": [{ "type": "text", "text": { "content": "Page Title" } }]
    }
  }
}
```

### Step 4: Add Content (if any)

The `API-post-page` endpoint creates the page with a title. To add body content, use `API-patch-block-children` with the new page's ID:

**Add paragraph blocks:**
```json
{
  "block_id": "new-page-id",
  "children": [
    {
      "type": "paragraph",
      "paragraph": {
        "rich_text": [{ "type": "text", "text": { "content": "Your content here." } }]
      }
    }
  ]
}
```

**Add bulleted list:**
```json
{
  "block_id": "new-page-id",
  "children": [
    {
      "type": "bulleted_list_item",
      "bulleted_list_item": {
        "rich_text": [{ "type": "text", "text": { "content": "List item" } }]
      }
    }
  ]
}
```

## Response Format

On success:
```
✅ Page created: **[Title]**
URL: [notion url]
ID: [page-id]
```

## Multi-Block Content

For pages with multiple sections, append blocks sequentially. Keep each `API-patch-block-children` call to <100 blocks.

## Notes

- The Notion API only supports `paragraph` and `bulleted_list_item` block types in this integration
- For richer content (headings, code blocks, etc.), the page can be edited manually in Notion after creation
- Always confirm with the user before creating the page if the intent was ambiguous
- Page IDs are UUIDs — save them if the user will want to reference the page again
