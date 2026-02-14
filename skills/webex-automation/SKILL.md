---
name: Webex Automation
description: "Automate Cisco Webex messaging, rooms, teams, webhooks, and people management through natural language commands"
requires:
  mcp:
    - rube
---

# Webex Automation

Automate Cisco Webex collaboration workflows -- send messages, manage rooms and teams, configure webhooks, and look up people -- all through natural language.

**Toolkit docs:** [composio.dev/toolkits/webex](https://composio.dev/toolkits/webex)

---

## Setup

1. Add the Rube MCP server to your environment: `https://rube.app/mcp`
2. Connect your Webex account when prompted (OAuth flow via Composio)
3. Start issuing natural language commands for Webex automation

---

## Core Workflows

### 1. Send a Message to a Room or Person

Post plain text, markdown, file attachments, or Adaptive Cards to any Webex room or directly to a person.

**Tool:** `WEBEX_MESSAGING_CREATE_MESSAGE`

Key parameters:
- `roomId` -- target room ID (use `WEBEX_MESSAGING_LIST_ROOMS` to find it)
- `toPersonEmail` -- send a private 1:1 message instead (mutually exclusive with `roomId`)
- `text` -- plain text content (max 7439 bytes)
- `markdown` -- markdown-formatted content (takes precedence over `text`)
- `files` -- list of public URLs for file attachments (one file per message)
- `attachments` -- Adaptive Card JSON (one card per message)
- `parentId` -- reply to a specific message as a threaded response

Example prompt:
> "Send a markdown message to room Y2lz... saying **Deploy completed** with a link to the release notes"

---

### 2. List and Discover Rooms

Browse all rooms you belong to, filtered by type, team, or sorted by activity.

**Tool:** `WEBEX_MESSAGING_LIST_ROOMS`

Key parameters:
- `type` -- filter by `direct` (1:1) or `group`
- `teamId` -- limit to rooms in a specific team
- `sortBy` -- sort by `id`, `lastactivity`, or `created`
- `max` -- limit results (1-1000, default 100)

Follow-up with `WEBEX_MESSAGING_GET_ROOM_DETAILS` to get full metadata for a specific room including title, type, lock status, creator, and timestamps.

Example prompt:
> "List my 10 most recently active group rooms in Webex"

---

### 3. Manage Webhooks for Event-Driven Automation

Create webhooks to receive real-time HTTP POST notifications when Webex resources change.

**Tool:** `WEBEX_WEBHOOKS_CREATE_WEBHOOK`

Key parameters:
- `name` -- human-friendly webhook name (required)
- `targetUrl` -- URL that receives POST notifications (required)
- `resource` -- what to monitor: `messages`, `rooms`, `memberships`, `meetings`, `recordings`, `meetingParticipants`, `telephony_calls`, etc. (required)
- `event` -- trigger type: `created`, `updated`, `deleted`, `started`, `ended`, `joined`, `left` (required)
- `filter` -- scope notifications (e.g., `roomId=<id>` or `hostEmail=<email>`)
- `secret` -- optional HMAC secret for payload signature verification
- `ownedBy` -- `creator` for personal or `org` for organization-wide webhooks

Supporting tools:
- `WEBEX_LIST_WEBHOOKS` -- list all registered webhooks with optional `max` and `ownedBy` filters
- `WEBEX_WEBHOOKS_GET_WEBHOOK` -- inspect a specific webhook by `webhookId`

Example prompt:
> "Create a webhook called 'New Messages' that POSTs to https://my-app.com/hook whenever a message is created in room Y2lz..."

---

### 4. Manage Team Memberships

Add people to Webex teams and optionally grant moderator privileges.

**Tool:** `WEBEX_MESSAGING_CREATE_TEAM_MEMBERSHIP`

Key parameters:
- `teamId` -- the team to add the person to (required)
- `personEmail` -- email of the person to add
- `personId` -- Webex person ID (alternative to email)
- `isModerator` -- set to `true` for moderator access (default `false`)

Use `WEBEX_LIST_TEAMS` to discover available teams first.

Example prompt:
> "Add alice@example.com as a moderator to team Y2lz..."

---

### 5. Audit Room Memberships

Check who is in a room, verify a specific person's membership, or list memberships across teams.

**Tool:** `WEBEX_MESSAGING_LIST_MEMBERSHIPS`

Key parameters:
- `roomId` -- list all members of a specific room
- `personEmail` -- check if a person is a member (requires `roomId`)
- `personId` -- check by Webex person ID (requires `roomId`)
- `teamId` -- filter by team association
- `max` -- limit results

Example prompt:
> "List all members of room Y2lz... and tell me who the moderators are"

---

### 6. Search and Look Up People

Look up people in your Webex organization by email, display name, or ID.

**Tool:** `WEBEX_PEOPLE_LIST_PEOPLE`

Use to resolve names to person IDs before sending direct messages or adding team members.

Example prompt:
> "Find the Webex person ID for bob@company.com"

---

## Known Pitfalls

| Pitfall | Details |
|---------|---------|
| Webhook auto-disable | Target URL must respond with HTTP 2xx; 100 failures in 5 minutes disables the webhook automatically |
| Message size limit | Both `text` and `markdown` have a 7439-byte maximum |
| One file per message | The `files` array accepts a list but only one attachment is actually supported per message |
| One card per message | Only one Adaptive Card attachment is supported per message |
| Mutually exclusive targets | `roomId` and `toPersonEmail`/`toPersonId` cannot be used together when sending messages |
| Room update requires title | `WEBEX_UPDATE_ROOM` always requires the `title` parameter, even when only changing lock status or team |
| orgPublicSpaces conflicts | Cannot combine `orgPublicSpaces` with `teamId`, `type`, or `sortBy` when listing rooms |
| Webhook read scope | Creating a webhook requires `read` scope on the monitored resource type |
| Membership filter requires roomId | `personEmail` and `personId` filters in list memberships require `roomId` unless you are a Compliance Officer |

---

## Quick Reference

| Action | Tool Slug | Key Params |
|--------|-----------|------------|
| Send message | `WEBEX_MESSAGING_CREATE_MESSAGE` | `roomId`, `text`/`markdown`, `toPersonEmail` |
| List rooms | `WEBEX_MESSAGING_LIST_ROOMS` | `type`, `sortBy`, `max` |
| Get room details | `WEBEX_MESSAGING_GET_ROOM_DETAILS` | `roomId` |
| Update room | `WEBEX_UPDATE_ROOM` | `roomId`, `title` |
| Delete message | `WEBEX_MESSAGING_DELETE_MESSAGE` | `messageId` |
| Get message details | `WEBEX_MESSAGING_GET_MESSAGE_DETAILS` | `messageId` |
| Create webhook | `WEBEX_WEBHOOKS_CREATE_WEBHOOK` | `name`, `targetUrl`, `resource`, `event` |
| List webhooks | `WEBEX_LIST_WEBHOOKS` | `max`, `ownedBy` |
| Get webhook | `WEBEX_WEBHOOKS_GET_WEBHOOK` | `webhookId` |
| Add team member | `WEBEX_MESSAGING_CREATE_TEAM_MEMBERSHIP` | `teamId`, `personEmail`, `isModerator` |
| List memberships | `WEBEX_MESSAGING_LIST_MEMBERSHIPS` | `roomId`, `personEmail`, `max` |
| List people | `WEBEX_PEOPLE_LIST_PEOPLE` | email, displayName, ID filters |
| List teams | `WEBEX_LIST_TEAMS` | `max` |

---

*Powered by [Composio](https://composio.dev)*
