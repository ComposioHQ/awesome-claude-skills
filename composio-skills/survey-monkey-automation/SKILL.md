---
name: SurveyMonkey Automation
description: "Automate SurveyMonkey survey creation, response collection, collector management, and survey discovery through natural language commands"
requires:
  mcp:
    - rube
---

# SurveyMonkey Automation

Automate SurveyMonkey survey workflows -- create surveys, list and search existing surveys, manage collectors and distribution links, retrieve responses, and inspect survey details -- all through natural language.

**Toolkit docs:** [composio.dev/toolkits/survey_monkey](https://composio.dev/toolkits/survey_monkey)

---

## Setup

1. Add the Rube MCP server to your environment: `https://rube.app/mcp`
2. Connect your SurveyMonkey account when prompted (OAuth flow via Composio)
3. Start issuing natural language commands for SurveyMonkey automation

---

## Core Workflows

### 1. Create a New Survey

Create a new empty survey that can be further configured with questions and pages.

**Tool:** `SURVEY_MONKEY_CREATE_SURVEY`

Key parameters:
- `title` -- survey title displayed to respondents (required)
- `nickname` -- optional internal name for organizing surveys (not shown to respondents)
- `language` -- ISO 639-1 language code (default `en`); examples: `es`, `fr`, `de`
- `footer` -- whether to display SurveyMonkey branding footer (default `true`)

> The created survey starts with one empty page and no questions. Use the returned `survey_id` with other actions to add content and configure collectors.

Example prompt:
> "Create a new survey titled 'Customer Satisfaction Q1 2026'"

---

### 2. List and Search Surveys

Enumerate all surveys in your account with filtering, sorting, and pagination.

**Tool:** `SURVEY_MONKEY_GET_SURVEYS`

Key parameters:
- `title` -- search by survey title (partial match)
- `sort_by` -- sort by `title`, `date_modified`, or `num_responses`
- `sort_order` -- `ASC` or `DESC`
- `page` / `per_page` -- pagination controls (default 50 per page, max 100)
- `include` -- additional fields: `response_count`, `date_modified`, `date_created`, `question_count`, `page_count`, `category`, `language`, `folder_id`
- `folder_id` -- filter to surveys in a specific folder
- `start_modified_at` / `end_modified_at` -- date range filter (format: `YYYY-MM-DDTHH:MM:SS`)

Example prompt:
> "List all my surveys sorted by most recent modification, include response counts"

---

### 3. Get Survey Details

Retrieve comprehensive metadata for a specific survey including configuration, question/page counts, response counts, and all relevant URLs.

**Tool:** `SURVEY_MONKEY_GET_SURVEY_DETAILS`

Key parameters:
- `survey_id` -- the unique survey identifier (required)

Returns: title, language, question_count, page_count, response_count, URLs for preview/edit/analyze/collect, button text, and timestamps.

Example prompt:
> "Show me the full details and response count for survey 123456789"

---

### 4. Manage Collectors and Distribution Links

Retrieve collectors (distribution channels) for a survey to get shareable links and monitor response progress.

**Tool:** `SURVEY_MONKEY_GET_COLLECTORS`

Key parameters:
- `survey_id` -- the survey to get collectors for (required)
- `include` -- additional fields: `type`, `status`, `response_count`, `date_created`, `date_modified`, `url`
- `name` -- partial match filter on collector name
- `sort_by` -- sort by `id`, `date_modified`, `type`, `status`, or `name`
- `sort_order` -- `ASC` or `DESC`
- `page` / `per_page` -- pagination (default 50, max 1000)
- `start_date` / `end_date` -- filter by creation date (format: `YYYY-MM-DDTHH:MM:SS`)

Example prompt:
> "Get all collectors for survey 123456789, include URLs and response counts"

---

### 5. Retrieve Survey Responses

Fetch response data for a specific survey with comprehensive filtering options.

**Tool:** `SURVEY_MONKEY_GET_RESPONSES`

Key parameters:
- `survey_id` -- the survey to retrieve responses from (required)
- `status` -- filter by `completed`, `partial`, `overquota`, or `disqualified`
- `page` / `per_page` -- pagination (default 50, max 1000)
- `sort_order` -- `ASC` or `DESC` (sorted by `date_modified`)
- `start_created_at` / `end_created_at` -- filter by creation date range (ISO 8601)
- `start_modified_at` / `end_modified_at` -- filter by modification date range
- `email` -- filter by respondent email
- `first_name` / `last_name` -- filter by respondent name
- `ip` -- filter by IP address
- `total_time_min` / `total_time_max` / `total_time_units` -- filter by completion time

Example prompt:
> "Get all completed responses for survey 123456789 from the last 30 days"

---

### 6. Full Survey Lifecycle Workflow

Combine tools for end-to-end survey management:

1. **Create**: `SURVEY_MONKEY_CREATE_SURVEY` -- create the survey, store the `survey_id`
2. **Distribute**: `SURVEY_MONKEY_GET_COLLECTORS` -- retrieve the collector link to share with respondents
3. **Monitor**: `SURVEY_MONKEY_GET_SURVEY_DETAILS` -- check response counts and survey status
4. **Collect**: `SURVEY_MONKEY_GET_RESPONSES` -- retrieve completed responses, filter by `status=completed`
5. **Audit**: `SURVEY_MONKEY_GET_SURVEYS` -- browse and find surveys if `survey_id` is lost

Example prompt:
> "Create a survey called 'Event Feedback', then show me how to distribute it"

---

## Known Pitfalls

| Pitfall | Details |
|---------|---------|
| Pagination required | `SURVEY_MONKEY_GET_COLLECTORS` and `SURVEY_MONKEY_GET_RESPONSES` require managing `page`/`per_page` for large surveys to avoid missing data |
| Status filtering critical | `SURVEY_MONKEY_GET_RESPONSES` returns partial, overquota, and disqualified entries unless filtered -- use `status=completed` for reliable data |
| No shareable link on create | `SURVEY_MONKEY_CREATE_SURVEY` does not create a distribution link -- use `SURVEY_MONKEY_GET_COLLECTORS` to get shareable URLs |
| Survey ID storage | Losing track of `survey_id` forces reliance on `SURVEY_MONKEY_GET_SURVEYS` which is slower -- store IDs immediately after creation |
| Question ID mapping | Question IDs and answer formats from responses must be carefully mapped; use `SURVEY_MONKEY_GET_SURVEY_DETAILS` to understand the structure |
| Date format | Date filters use `YYYY-MM-DDTHH:MM:SS` format, not ISO 8601 with timezone |
| Empty survey on create | New surveys start with one empty page and no questions -- further configuration is needed |

---

## Quick Reference

| Action | Tool Slug | Key Params |
|--------|-----------|------------|
| Create survey | `SURVEY_MONKEY_CREATE_SURVEY` | `title`, `language`, `nickname` |
| List surveys | `SURVEY_MONKEY_GET_SURVEYS` | `title`, `sort_by`, `include`, `page` |
| Get survey details | `SURVEY_MONKEY_GET_SURVEY_DETAILS` | `survey_id` |
| List collectors | `SURVEY_MONKEY_GET_COLLECTORS` | `survey_id`, `include`, `sort_by` |
| Get responses | `SURVEY_MONKEY_GET_RESPONSES` | `survey_id`, `status`, `start_created_at` |

---

*Powered by [Composio](https://composio.dev)*
