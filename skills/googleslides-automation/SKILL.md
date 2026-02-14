---
name: googleslides-automation
description: "Automate Google Slides tasks via Rube MCP (Composio): create presentations, add slides from Markdown, batch update, copy from templates, get thumbnails. Always search tools first for current schemas."
requires:
  mcp: [rube]
---

# Google Slides Automation via Rube MCP

Create, edit, and manage Google Slides presentations programmatically using Rube MCP (Composio).

**Toolkit docs**: [composio.dev/toolkits/googleslides](https://composio.dev/toolkits/googleslides)

## Prerequisites
- Rube MCP must be connected (RUBE_SEARCH_TOOLS available)
- Active connection via `RUBE_MANAGE_CONNECTIONS` with toolkit `googleslides`
- Always call `RUBE_SEARCH_TOOLS` first to get current tool schemas

## Setup
**Get Rube MCP**: Add `https://rube.app/mcp` as an MCP server in your client configuration. No API keys needed — just add the endpoint and it works.

1. Verify Rube MCP is available by confirming `RUBE_SEARCH_TOOLS` responds
2. Call `RUBE_MANAGE_CONNECTIONS` with toolkit `googleslides`
3. If connection is not ACTIVE, follow the returned auth link to complete setup
4. Confirm connection status shows ACTIVE before running any workflows

## Core Workflows

### 1. Create a Blank Presentation
Use `GOOGLESLIDES_PRESENTATIONS_CREATE` to initialize a new blank presentation.
```
Tool: GOOGLESLIDES_PRESENTATIONS_CREATE
Parameters:
  - title (required): Title for the new presentation
  - presentationId (optional): Specific ID to assign (usually auto-generated)
```

### 2. Create Slides from Markdown
Use `GOOGLESLIDES_CREATE_SLIDES_MARKDOWN` to generate a full presentation from Markdown text. Content is automatically split into slides.
```
Tool: GOOGLESLIDES_CREATE_SLIDES_MARKDOWN
Parameters:
  - title (required): Presentation title
  - markdown_text (required): Markdown content (auto-split into slides)
```

### 3. Batch Update a Presentation
Use `GOOGLESLIDES_PRESENTATIONS_BATCH_UPDATE` to apply updates to an existing presentation using Markdown or raw API requests.
```
Tool: GOOGLESLIDES_PRESENTATIONS_BATCH_UPDATE
Parameters:
  - presentationId (required): Target presentation ID
  - markdown_text: Markdown content to update slides
  - requests: Raw Google Slides API batch update requests
  - writeControl: Write control settings
```

### 4. Copy from Template
Use `GOOGLESLIDES_PRESENTATIONS_COPY_FROM_TEMPLATE` to duplicate an existing presentation as a template.
```
Tool: GOOGLESLIDES_PRESENTATIONS_COPY_FROM_TEMPLATE
Parameters:
  - template_presentation_id (required): Source template presentation ID
  - new_title (required): Title for the new copy
  - parent_folder_id (optional): Google Drive folder for the copy
```

### 5. Get Presentation Details
Use `GOOGLESLIDES_PRESENTATIONS_GET` to retrieve the current state of a presentation including all slides and elements.
```
Tool: GOOGLESLIDES_PRESENTATIONS_GET
Parameters:
  - presentationId (required): Presentation ID to retrieve
  - fields (optional): Specific fields to return
```

### 6. Generate Slide Thumbnails
Use `GOOGLESLIDES_PRESENTATIONS_PAGES_GET_THUMBNAIL` to generate a thumbnail image URL for a specific slide.
```
Tool: GOOGLESLIDES_PRESENTATIONS_PAGES_GET_THUMBNAIL
Parameters:
  - presentationId (required): Presentation ID
  - pageObjectId (required): Page/slide object ID
  - thumbnailProperties.mimeType: Image format (e.g., PNG)
  - thumbnailProperties.thumbnailSize: Thumbnail size
```

## Common Patterns

- **Markdown-first workflow**: Use `GOOGLESLIDES_CREATE_SLIDES_MARKDOWN` to quickly generate presentations from structured text. The tool auto-splits content into separate slides.
- **Template-based generation**: Use `GOOGLESLIDES_PRESENTATIONS_COPY_FROM_TEMPLATE` to copy a styled template, then `GOOGLESLIDES_PRESENTATIONS_BATCH_UPDATE` to fill in content.
- **Retrieve then modify**: Use `GOOGLESLIDES_PRESENTATIONS_GET` to inspect slide structure and object IDs, then `GOOGLESLIDES_PRESENTATIONS_BATCH_UPDATE` to make targeted changes.
- **Export thumbnails**: Use `GOOGLESLIDES_PRESENTATIONS_PAGES_GET` to list page object IDs, then `GOOGLESLIDES_PRESENTATIONS_PAGES_GET_THUMBNAIL` to generate preview images.
- **Share presentations**: Combine with `GOOGLEDRIVE_ADD_FILE_SHARING_PREFERENCE` (googledrive toolkit) to share after creation.

## Known Pitfalls

- `GOOGLESLIDES_CREATE_SLIDES_MARKDOWN` creates a brand-new presentation each time -- it cannot append to an existing one.
- `GOOGLESLIDES_PRESENTATIONS_BATCH_UPDATE` with raw `requests` requires knowledge of the Google Slides API request format. Prefer `markdown_text` for simpler updates.
- Page object IDs must be obtained from `GOOGLESLIDES_PRESENTATIONS_GET` before using thumbnail or page-get tools.
- The `presentationId` is the long alphanumeric string from the Google Slides URL (between `/d/` and `/edit`).
- Copying from a template requires the authenticated user to have at least read access to the template presentation.

## Quick Reference
| Action | Tool | Key Parameters |
|--------|------|----------------|
| Create blank presentation | `GOOGLESLIDES_PRESENTATIONS_CREATE` | `title` |
| Create from Markdown | `GOOGLESLIDES_CREATE_SLIDES_MARKDOWN` | `title`, `markdown_text` |
| Batch update slides | `GOOGLESLIDES_PRESENTATIONS_BATCH_UPDATE` | `presentationId`, `markdown_text` or `requests` |
| Copy from template | `GOOGLESLIDES_PRESENTATIONS_COPY_FROM_TEMPLATE` | `template_presentation_id`, `new_title` |
| Get presentation | `GOOGLESLIDES_PRESENTATIONS_GET` | `presentationId` |
| Get page details | `GOOGLESLIDES_PRESENTATIONS_PAGES_GET` | `presentationId`, `pageObjectId` |
| Get slide thumbnail | `GOOGLESLIDES_PRESENTATIONS_PAGES_GET_THUMBNAIL` | `presentationId`, `pageObjectId` |

---
*Powered by [Composio](https://composio.dev)*
