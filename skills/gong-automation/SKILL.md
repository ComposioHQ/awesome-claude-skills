---
name: Gong Automation
description: "Automate Gong conversation intelligence -- retrieve call recordings, transcripts, detailed analytics, speaker stats, and workspace data -- using natural language through the Composio MCP integration."
category: conversation-intelligence
requires:
  mcp:
    - rube
---

# Gong Automation

Unlock insights from your sales calls -- retrieve transcripts, analyze call data by date range, access detailed conversation analytics with topics and trackers, and manage workspaces -- all through natural language commands.

**Toolkit docs:** [composio.dev/toolkits/gong](https://composio.dev/toolkits/gong)

---

## Setup

1. Add the Composio MCP server to your client configuration:
   ```
   https://rube.app/mcp
   ```
2. Connect your Gong account when prompted (OAuth / Bearer token authentication).
3. Start issuing natural language commands to analyze your call data.

---

## Core Workflows

### 1. Retrieve Call Transcripts by Date Range
Get transcripts for all calls within a specified time period, with optional filtering by specific call IDs or workspace.

**Tool:** `GONG_RETRIEVE_TRANSCRIPTS_OF_CALLS_V2_CALLS_TRANSCRIPT`

**Example prompt:**
> "Get Gong transcripts for all calls from February 1-10, 2025"

**Key parameters:**
- `filter__fromDateTime` -- ISO-8601 start date (e.g., `2025-02-01T00:00:00Z`)
- `filter__toDateTime` -- ISO-8601 end date (e.g., `2025-02-10T23:59:59Z`)
- `filter__callIds` -- Optional array of specific call IDs to filter
- `filter__workspaceId` -- Optional workspace ID filter
- `cursor` -- Pagination cursor from previous response

**Required scope:** `api:calls:read:transcript`

---

### 2. Get Transcript for Specific Calls
Retrieve transcripts with speaker information, timestamps, and topic categorization using a filter object.

**Tool:** `GONG_GET_CALL_TRANSCRIPT`

**Example prompt:**
> "Get the Gong transcript for call ID 555785916001072125"

**Key parameters (filter required):**
- `filter.callIds` -- Array of specific call IDs (e.g., `["555785916001072125"]`)
- `filter.fromDateTime` -- ISO-8601 start date
- `filter.toDateTime` -- ISO-8601 end date
- `filter.workspaceId` -- Optional workspace filter
- `cursor` -- Pagination cursor

---

### 3. List Calls by Date Range
Retrieve basic call metadata (participants, duration, timing) for calls within a date range.

**Tool:** `GONG_RETRIEVE_CALL_DATA_BY_DATE_RANGE_V2_CALLS`

**Example prompt:**
> "List all Gong calls from last week"

**Key parameters (both required):**
- `fromDateTime` -- ISO-8601 start date (e.g., `2025-02-03T00:00:00Z`)
- `toDateTime` -- ISO-8601 end date (e.g., `2025-02-10T00:00:00Z`)
- `workspaceId` -- Optional workspace filter
- `cursor` -- Pagination cursor

**Required scope:** `api:calls:read:basic`

---

### 4. Get Detailed Call Analytics
Retrieve extensive call details including highlights, key points, topics, trackers, speaker stats, questions, and media URLs.

**Tool:** `GONG_RETRIEVE_FILTERED_CALL_DETAILS`

**Example prompt:**
> "Get detailed analytics for Gong calls this week including topics, key points, and speaker stats"

**Key parameters:**
- `filter__fromDateTime` / `filter__toDateTime` -- Date range filter
- `filter__callIds` -- Specific call IDs
- `filter__primaryUserIds` -- Filter by call host user IDs
- Content selectors (all boolean):
  - `contentSelector__exposedFields__content__keyPoints` -- Key points of the call
  - `contentSelector__exposedFields__content__topics` -- Topic durations
  - `contentSelector__exposedFields__content__highlights` -- Call highlights
  - `contentSelector__exposedFields__content__outline` -- Call outline
  - `contentSelector__exposedFields__content__brief` -- Spotlight call brief
  - `contentSelector__exposedFields__content__callOutcome` -- Call outcome
  - `contentSelector__exposedFields__content__trackers` -- Smart/keyword trackers
  - `contentSelector__exposedFields__content__trackerOccurrences` -- Tracker timing and speaker (requires trackers=true)
  - `contentSelector__exposedFields__interaction__speakers` -- Time each participant spoke
  - `contentSelector__exposedFields__interaction__questions` -- Question counts
  - `contentSelector__exposedFields__interaction__personInteractionStats` -- Host statistics
  - `contentSelector__exposedFields__media` -- Audio/video URLs (valid 8 hours)
  - `contentSelector__exposedFields__parties` -- Party information
  - `contentSelector__exposedFields__collaboration__publicComments` -- Public comments
- `contentSelector__context` -- "Basic", "Extended", or "None" for CRM/external system links

**Required scope:** `api:calls:read:extensive` (plus `api:calls:read:media-url` for media)

---

### 5. Get a Specific Call by ID
Retrieve basic data for a single call using its unique Gong ID.

**Tool:** `GONG_RETRIEVE_DATA_FOR_A_SPECIFIC_CALL_V2_CALLS_ID`

**Example prompt:**
> "Get details for Gong call 1223781272986876929"

**Key parameters (required):**
- `id` -- Gong's unique numeric identifier for the call (up to 20 digits)

**Required scope:** `api:calls:read:basic`

---

### 6. List Company Workspaces
Retrieve all workspaces in your Gong organization to get workspace IDs for filtering.

**Tool:** `GONG_LIST_ALL_COMPANY_WORKSPACES_V2_WORKSPACES`

**Example prompt:**
> "List all Gong workspaces in my company"

**Key parameters:** None required.

**Required scope:** `api:workspaces:read`

---

## Known Pitfalls

- **ISO-8601 date format is mandatory**: All date parameters must use ISO-8601 format with timezone: `2025-02-01T00:00:00Z` or `2025-02-01T02:30:00-07:00`. Plain dates will fail.
- **Date range is exclusive on toDateTime**: The `toDateTime` parameter returns calls started UP TO BUT EXCLUDING the specified time. To include calls on a specific day, set `toDateTime` to the next day.
- **Pagination is required for large result sets**: All list endpoints return paginated results. Use the `cursor` value from the previous response to fetch the next page. Continue until no cursor is returned.
- **Scope requirements vary by endpoint**: Different endpoints require different API scopes. Transcript access needs `api:calls:read:transcript`, basic call data needs `api:calls:read:basic`, and detailed analytics need `api:calls:read:extensive`.
- **Media URLs expire after 8 hours**: Audio and video URLs returned by the detailed call endpoint are temporary and expire after 8 hours.
- **Tracker occurrence data availability**: Tracker occurrence data (timing and speaker ID) is only available for calls recorded since January 1, 2023. Contact Gong support for backfill.
- **Web-conference vs. regular calls**: For web-conference calls recorded by Gong, the date represents the scheduled time. For other calls, it represents the actual start time.

---

## Quick Reference

| Action | Tool Slug | Required Params |
|---|---|---|
| Get transcripts by date | `GONG_RETRIEVE_TRANSCRIPTS_OF_CALLS_V2_CALLS_TRANSCRIPT` | None (date range recommended) |
| Get call transcript | `GONG_GET_CALL_TRANSCRIPT` | `filter` object |
| List calls by date | `GONG_RETRIEVE_CALL_DATA_BY_DATE_RANGE_V2_CALLS` | `fromDateTime`, `toDateTime` |
| Get detailed call analytics | `GONG_RETRIEVE_FILTERED_CALL_DETAILS` | None (date range or call IDs recommended) |
| Get specific call | `GONG_RETRIEVE_DATA_FOR_A_SPECIFIC_CALL_V2_CALLS_ID` | `id` |
| List workspaces | `GONG_LIST_ALL_COMPANY_WORKSPACES_V2_WORKSPACES` | None |

---

*Powered by [Composio](https://composio.dev)*
