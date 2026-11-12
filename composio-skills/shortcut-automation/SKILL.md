---
name: Shortcut Automation
description: "Automate project management workflows in Shortcut -- create stories, manage tasks, track epics, and organize workflows through natural language commands."
requires:
  mcp:
    - rube
---

# Shortcut Automation

Automate your Shortcut project management operations directly from Claude Code. Create and list stories, add tasks and comments, batch-create stories, and navigate workflows -- all without leaving your terminal.

**Toolkit docs:** [composio.dev/toolkits/shortcut](https://composio.dev/toolkits/shortcut)

---

## Setup

1. Add the Rube MCP server to your Claude Code config with URL: `https://rube.app/mcp`
2. When prompted, authenticate your Shortcut account through the connection link provided
3. Start automating your project management workflows with natural language

---

## Core Workflows

### 1. Create Stories

Add new stories to your Shortcut workspace with full configuration.

**Tool:** `SHORTCUT_CREATE_STORY`

```
Create a feature story called "Add dark mode support" in workflow state 500000001 with estimate 5 and label "frontend"
```

Key parameters for `SHORTCUT_CREATE_STORY`:
- `name` (required) -- the story title
- `workflow_state_id` -- the workflow state to place the story in (recommended over `project_id`)
- `story_type` -- `"feature"`, `"bug"`, or `"chore"`
- `description` -- story body/description
- `estimate` -- numeric point estimate (or null for unestimated)
- `epic_id` -- associate with an epic
- `iteration_id` -- associate with an iteration
- `labels` -- array of label objects with `name` (and optional `color`, `description`)
- `owner_ids` -- array of member UUIDs to assign
- `deadline` -- due date in ISO 8601 format
- `tasks` -- inline task array with `description` and optional `complete`, `owner_ids`
- `comments` -- inline comment array with `text`
- `story_links` -- link stories with `verb` (`"blocks"`, `"duplicates"`, `"relates to"`)

**Important:** Either `workflow_state_id` or `project_id` must be provided, but not both. `workflow_state_id` is recommended as Projects are being sunset in Shortcut.

### 2. Batch Create Stories

Create multiple stories in a single API call.

**Tool:** `SHORTCUT_CREATE_MULTIPLE_STORIES`

```
Create 3 bug stories: "Login page 500 error", "Cart total rounding issue", and "Search results empty state broken"
```

- Requires `stories` array where each element follows the same schema as `SHORTCUT_CREATE_STORY`
- Each story in the array requires `name`
- Efficient for bulk imports, sprint planning, or template-based story creation

### 3. List Stories in a Project

Retrieve all stories within a specific project.

**Tool:** `SHORTCUT_LIST_STORIES`

```
List all stories in project 42 with their descriptions
```

- Requires `project__public__id` (integer project ID)
- Optional `includes_description: true` to include story descriptions in the response
- Returns all stories with their attributes (status, type, estimate, etc.)

### 4. Manage Story Tasks

Create tasks (checklists) within stories for tracking sub-work.

**Tool:** `SHORTCUT_CREATE_TASK`

```
Add a task "Write unit tests for dark mode toggle" to story 12345
```

Key parameters:
- `story__public__id` (required) -- the parent story ID
- `description` (required) -- the task description
- `complete` -- boolean, defaults to false
- `owner_ids` -- array of member UUIDs to assign the task
- `external_id` -- ID from an external tool if imported

### 5. Add Story Comments

Post comments on stories for discussion and documentation.

**Tool:** `SHORTCUT_CREATE_STORY_COMMENT`

```
Add a comment to story 12345: "Reviewed the implementation -- looks good, but needs accessibility testing"
```

Key parameters:
- `story__public__id` (required) -- the story ID
- `text` (required) -- the comment body
- `author_id` -- member UUID (defaults to API token owner)
- `parent_id` -- ID of parent comment for threaded replies

### 6. Workflow and Project Discovery

List workflows and projects to resolve IDs for story creation.

**Tools:** `SHORTCUT_LIST_WORKFLOWS`, `SHORTCUT_LIST_PROJECTS`

```
Show me all workflows in our Shortcut workspace so I can find the right workflow state ID
```

- `SHORTCUT_LIST_WORKFLOWS` returns all workflows with their states (IDs, names, types)
- `SHORTCUT_LIST_PROJECTS` returns all projects with their attributes
- Use these to discover valid `workflow_state_id` and `project_id` values before creating stories

---

## Known Pitfalls

- **`workflow_state_id` vs `project_id`:** `SHORTCUT_CREATE_STORY` requires exactly one of these. Providing both or neither causes a rejection. Prefer `workflow_state_id` since Projects are being sunset.
- **Projects are being sunset:** Shortcut is deprecating Projects in favor of workflow-based organization. Use `workflow_state_id` for new stories.
- **Label creation is inline:** Labels in the `labels` array are created on-the-fly if they do not exist. The `name` field is required for each label object.
- **Story type defaults:** If `story_type` is omitted, it defaults to `"feature"`. Always set it explicitly for bugs and chores.
- **Batch limits:** `SHORTCUT_CREATE_MULTIPLE_STORIES` processes all stories in a single request. Very large batches may time out -- keep batches under 25 stories.
- **Integer IDs for stories/projects:** Story and project IDs are integers, not UUIDs. Member and group IDs are UUIDs. Mixing these formats causes errors.
- **`move_to` positioning:** The `move_to` field (`"first"` or `"last"`) moves the story within its workflow state, not across states.

---

## Quick Reference

| Tool Slug | Description |
|---|---|
| `SHORTCUT_CREATE_STORY` | Create a single story (requires `name` + `workflow_state_id` or `project_id`) |
| `SHORTCUT_CREATE_MULTIPLE_STORIES` | Batch-create multiple stories (requires `stories` array) |
| `SHORTCUT_LIST_STORIES` | List stories in a project (requires `project__public__id`) |
| `SHORTCUT_CREATE_TASK` | Create a task in a story (requires `story__public__id`, `description`) |
| `SHORTCUT_CREATE_STORY_COMMENT` | Add a comment to a story (requires `story__public__id`, `text`) |
| `SHORTCUT_CREATE_STORY_FROM_TEMPLATE` | Create a story from a template |
| `SHORTCUT_LIST_WORKFLOWS` | List all workflows and their states |
| `SHORTCUT_LIST_PROJECTS` | List all projects |

---

*Powered by [Composio](https://composio.dev)*
