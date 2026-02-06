---
name: slack-automation
description: Automate Slack messaging, channel management, search, reactions, and threads via Rube MCP (Composio). Send messages, search conversations, manage channels/users, and react to messages programmatically.
requires:
  mcp: [rube]
---

# Slack Automation via Rube MCP

Automate Slack workspace operations including messaging, search, channel management, and reaction workflows through Composio's Slack toolkit.

## Prerequisites

- Rube MCP must be connected (RUBE_SEARCH_TOOLS available)
- Active Slack connection via `RUBE_MANAGE_CONNECTIONS` with toolkit `slack`
- Always call `RUBE_SEARCH_TOOLS` first to get current tool schemas

## Setup

**Get Rube MCP**: Add `https://rube.app/mcp` as an MCP server in your client configuration. No API keys needed — just add the endpoint and it works.


1. Verify Rube MCP is available by confirming `RUBE_SEARCH_TOOLS` responds
2. Call `RUBE_MANAGE_CONNECTIONS` with toolkit `slack`
3. If connection is not ACTIVE, follow the returned auth link to complete Slack OAuth
4. Confirm connection status shows ACTIVE before running any workflows

## Core Workflows

### 1. Send Messages to Channels

**When to use**: User wants to post a message to a Slack channel or DM

**Tool sequence**:
1. `SLACK_FIND_CHANNELS` - Resolve channel name to channel ID [Prerequisite]
2. `SLACK_LIST_ALL_CHANNELS` - Fallback if FIND_CHANNELS returns empty/ambiguous results [Fallback]
3. `SLACK_FIND_USERS` - Resolve user for DMs or @mentions [Optional]
4. `SLACK_OPEN_DM` - Open/reuse a DM channel if messaging a user directly [Optional]
5. `SLACK_SEND_MESSAGE` - Post the message with resolved channel ID [Required]
6. `SLACK_UPDATES_A_SLACK_MESSAGE` - Edit the posted message if corrections needed [Optional]

**Key parameters**:
- `channel`: Channel ID or name (without '#' prefix)
- `markdown_text`: Preferred field for formatted messages (supports headers, bold, italic, code blocks)
- `text`: Raw text fallback (deprecated in favor of markdown_text)
- `thread_ts`: Timestamp of parent message to reply in a thread
- `blocks`: Block Kit layout blocks (deprecated, use markdown_text)

**Pitfalls**:
- `SLACK_FIND_CHANNELS` requires `query` param; missing it errors with "Invalid request data provided"
- `SLACK_SEND_MESSAGE` requires valid channel plus one of markdown_text/text/blocks/attachments
- Invalid block payloads return error=invalid_blocks (max 50 blocks)
- Replies become top-level posts if `thread_ts` is omitted
- Persist `response.data.channel` and `response.data.message.ts` from SEND_MESSAGE for edit/thread operations

### 2. Search Messages and Conversations

**When to use**: User wants to find specific messages across the workspace

**Tool sequence**:
1. `SLACK_FIND_CHANNELS` - Resolve channel for scoped search with `in:#channel` [Optional]
2. `SLACK_FIND_USERS` - Resolve user for author filter with `from:@user` [Optional]
3. `SLACK_SEARCH_MESSAGES` - Run keyword search across accessible conversations [Required]
4. `SLACK_FETCH_MESSAGE_THREAD_FROM_A_CONVERSATION` - Expand threads for relevant hits [Required]

**Key parameters**:
- `query`: Search string supporting modifiers (`in:#channel`, `from:@user`, `before:YYYY-MM-DD`, `after:YYYY-MM-DD`, `has:link`, `has:file`)
- `count`: Results per page (max 100), or total with auto_paginate=true
- `sort`: 'score' (relevance) or 'timestamp' (chronological)
- `sort_dir`: 'asc' or 'desc'

**Pitfalls**:
- Validation fails if `query` is missing/empty
- `ok=true` can still mean no hits (`response.data.messages.total=0`)
- Matches are under `response.data.messages.matches` (sometimes also `response.data_preview.messages.matches`)
- `match.text` may be empty/truncated; key info can appear in `matches[].attachments[]`
- Thread expansion via FETCH_MESSAGE_THREAD can truncate when `response.data.has_more=true`; paginate via `response_metadata.next_cursor`

### 3. Manage Channels and Users

**When to use**: User wants to list channels, users, or workspace info

**Tool sequence**:
1. `SLACK_FETCH_TEAM_INFO` - Validate connectivity and get workspace identity [Required]
2. `SLACK_LIST_ALL_CHANNELS` - Enumerate public channels [Required]
3. `SLACK_LIST_CONVERSATIONS` - Include private channels and DMs [Optional]
4. `SLACK_LIST_ALL_USERS` - List workspace members [Required]
5. `SLACK_RETRIEVE_CONVERSATION_INFORMATION` - Get detailed channel metadata [Optional]
6. `SLACK_LIST_USER_GROUPS_FOR_TEAM_WITH_OPTIONS` - List user groups [Optional]

**Key parameters**:
- `cursor`: Pagination cursor from `response_metadata.next_cursor`
- `limit`: Results per page (default varies; set explicitly for large workspaces)
- `types`: Channel types filter ('public_channel', 'private_channel', 'im', 'mpim')

**Pitfalls**:
- Workspace metadata is nested under `response.data.team`, not top-level
- `SLACK_LIST_ALL_CHANNELS` returns public channels only; use `SLACK_LIST_CONVERSATIONS` for private/IM coverage
- `SLACK_LIST_ALL_USERS` can hit HTTP 429 rate limits; honor Retry-After header
- Always paginate via `response_metadata.next_cursor` until empty; de-duplicate by `id`

### 4. React to and Thread Messages

**When to use**: User wants to add reactions or manage threaded conversations

**Tool sequence**:
1. `SLACK_SEARCH_MESSAGES` or `SLACK_FETCH_CONVERSATION_HISTORY` - Find the target message [Prerequisite]
2. `SLACK_ADD_REACTION_TO_AN_ITEM` - Add an emoji reaction [Required]
3. `SLACK_FETCH_ITEM_REACTIONS` - List reactions on a message [Optional]
4. `SLACK_REMOVE_REACTION_FROM_ITEM` - Remove a reaction [Optional]
5. `SLACK_SEND_MESSAGE` - Reply in thread using `thread_ts` [Optional]
6. `SLACK_FETCH_MESSAGE_THREAD_FROM_A_CONVERSATION` - Read full thread [Optional]

**Key parameters**:
- `channel`: Channel ID where the message lives
- `timestamp` / `ts`: Message timestamp (unique identifier like '1234567890.123456')
- `name`: Emoji name without colons (e.g., 'thumbsup', 'wave::skin-tone-3')
- `thread_ts`: Parent message timestamp for threaded replies

**Pitfalls**:
- Reactions require exact channel ID + message timestamp pair
- Emoji names use Slack's naming convention without colons
- `SLACK_FETCH_CONVERSATION_HISTORY` only returns main channel timeline, NOT threaded replies
- Use `SLACK_FETCH_MESSAGE_THREAD_FROM_A_CONVERSATION` with parent's `thread_ts` to get thread replies

### 5. Schedule Messages

**When to use**: User wants to schedule a message for future delivery

**Tool sequence**:
1. `SLACK_FIND_CHANNELS` - Resolve channel ID [Prerequisite]
2. `SLACK_SCHEDULE_MESSAGE` - Schedule the message with `post_at` timestamp [Required]

**Key parameters**:
- `channel`: Resolved channel ID
- `post_at`: Unix timestamp for delivery (up to 120 days in advance)
- `text` / `blocks`: Message content

**Pitfalls**:
- Scheduling is limited to 120 days in advance
- `post_at` must be a Unix timestamp, not ISO 8601

## Common Patterns

### ID Resolution
Always resolve display names to IDs before operations:
- **Channel name -> Channel ID**: `SLACK_FIND_CHANNELS` with `query` param
- **User name -> User ID**: `SLACK_FIND_USERS` with `search_query` or `email`
- **DM channel**: `SLACK_OPEN_DM` with resolved user IDs

### Pagination
Most list endpoints use cursor-based pagination:
- Follow `response_metadata.next_cursor` until empty
- Set explicit `limit` values (e.g., 100-200) for reliable paging
- De-duplicate results by `id` across pages

### Message Formatting
- Prefer `markdown_text` over `text` or `blocks` for formatted messages
- Use `<@USER_ID>` format to mention users (not @username)
- Use `\n` for line breaks in markdown_text

## Known Pitfalls

- **Channel resolution**: `SLACK_FIND_CHANNELS` can return empty results if channel is private and bot hasn't been invited
- **Rate limits**: `SLACK_LIST_ALL_USERS` and other list endpoints can hit HTTP 429; honor Retry-After header
- **Nested responses**: Results may be nested under `response.data.results[0].response.data` in wrapped executions
- **Thread vs channel**: `SLACK_FETCH_CONVERSATION_HISTORY` returns main timeline only; use `SLACK_FETCH_MESSAGE_THREAD_FROM_A_CONVERSATION` for thread replies
- **Message editing**: Requires both `channel` and original message `ts`; persist these from SEND_MESSAGE response
- **Search delays**: Recently posted messages may not appear in search results immediately
- **Scope limitations**: Missing OAuth scopes can cause 403 errors; check with `SLACK_GET_APP_PERMISSION_SCOPES`

## Quick Reference

| Task | Tool Slug | Key Params |
|------|-----------|------------|
| Find channels | `SLACK_FIND_CHANNELS` | `query` |
| List all channels | `SLACK_LIST_ALL_CHANNELS` | `limit`, `cursor`, `types` |
| Send message | `SLACK_SEND_MESSAGE` | `channel`, `markdown_text` |
| Edit message | `SLACK_UPDATES_A_SLACK_MESSAGE` | `channel`, `ts`, `markdown_text` |
| Search messages | `SLACK_SEARCH_MESSAGES` | `query`, `count`, `sort` |
| Get thread | `SLACK_FETCH_MESSAGE_THREAD_FROM_A_CONVERSATION` | `channel`, `ts` |
| Add reaction | `SLACK_ADD_REACTION_TO_AN_ITEM` | `channel`, `name`, `timestamp` |
| Find users | `SLACK_FIND_USERS` | `search_query` or `email` |
| List users | `SLACK_LIST_ALL_USERS` | `limit`, `cursor` |
| Open DM | `SLACK_OPEN_DM` | user IDs |
| Schedule message | `SLACK_SCHEDULE_MESSAGE` | `channel`, `post_at`, `text` |
| Get channel info | `SLACK_RETRIEVE_CONVERSATION_INFORMATION` | channel ID |
| Channel history | `SLACK_FETCH_CONVERSATION_HISTORY` | `channel`, `oldest`, `latest` |
| Workspace info | `SLACK_FETCH_TEAM_INFO` | (none) |
