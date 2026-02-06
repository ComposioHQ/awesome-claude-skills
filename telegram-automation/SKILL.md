---
name: telegram-automation
description: "Automate Telegram tasks via Rube MCP (Composio): send messages, manage chats, share photos/documents, and handle bot commands. Always search tools first for current schemas."
requires:
  mcp: [rube]
---

# Telegram Automation via Rube MCP

Automate Telegram operations through Composio's Telegram toolkit via Rube MCP.

## Prerequisites

- Rube MCP must be connected (RUBE_SEARCH_TOOLS available)
- Active Telegram connection via `RUBE_MANAGE_CONNECTIONS` with toolkit `telegram`
- Always call `RUBE_SEARCH_TOOLS` first to get current tool schemas
- Telegram Bot Token required (created via @BotFather)

## Setup

**Get Rube MCP**: Add `https://rube.app/mcp` as an MCP server in your client configuration. No API keys needed — just add the endpoint and it works.


1. Verify Rube MCP is available by confirming `RUBE_SEARCH_TOOLS` responds
2. Call `RUBE_MANAGE_CONNECTIONS` with toolkit `telegram`
3. If connection is not ACTIVE, follow the returned auth link to configure the Telegram bot
4. Confirm connection status shows ACTIVE before running any workflows

## Core Workflows

### 1. Send Messages

**When to use**: User wants to send text messages to a Telegram chat

**Tool sequence**:
1. `TELEGRAM_GET_ME` - Verify bot identity and connection [Prerequisite]
2. `TELEGRAM_GET_CHAT` - Get chat details and verify access [Optional]
3. `TELEGRAM_SEND_MESSAGE` - Send a text message [Required]

**Key parameters**:
- `chat_id`: Numeric chat ID or channel username (e.g., '@channelname')
- `text`: Message text content
- `parse_mode`: 'HTML' or 'MarkdownV2' for formatting
- `disable_notification`: Send silently without notification sound
- `reply_to_message_id`: Message ID to reply to

**Pitfalls**:
- Bot must be a member of the chat/group to send messages
- MarkdownV2 requires escaping special characters: `_*[]()~>#+-=|{}.!`
- HTML mode supports limited tags: `<b>`, `<i>`, `<code>`, `<pre>`, `<a>`
- Messages have a 4096 character limit; split longer content

### 2. Send Photos and Documents

**When to use**: User wants to share images or files in a Telegram chat

**Tool sequence**:
1. `TELEGRAM_SEND_PHOTO` - Send an image [Optional]
2. `TELEGRAM_SEND_DOCUMENT` - Send a file/document [Optional]

**Key parameters**:
- `chat_id`: Target chat ID
- `photo`: Photo URL or file_id (for SEND_PHOTO)
- `document`: Document URL or file_id (for SEND_DOCUMENT)
- `caption`: Optional caption for the media

**Pitfalls**:
- Photo captions have a 1024 character limit
- Document captions also have a 1024 character limit
- Files up to 50MB can be sent via bot API
- Photos are compressed by Telegram; use SEND_DOCUMENT for uncompressed images

### 3. Manage Chats

**When to use**: User wants to get chat information or manage chat settings

**Tool sequence**:
1. `TELEGRAM_GET_CHAT` - Get detailed chat information [Required]
2. `TELEGRAM_GET_CHAT_ADMINISTRATORS` - List chat admins [Optional]
3. `TELEGRAM_GET_CHAT_MEMBERS_COUNT` - Get member count [Optional]
4. `TELEGRAM_EXPORT_CHAT_INVITE_LINK` - Generate invite link [Optional]

**Key parameters**:
- `chat_id`: Target chat ID or username

**Pitfalls**:
- Bot must be an administrator to export invite links
- GET_CHAT returns different fields for private chats vs groups vs channels
- Member count may be approximate for very large groups
- Admin list does not include regular members

### 4. Edit and Delete Messages

**When to use**: User wants to modify or remove previously sent messages

**Tool sequence**:
1. `TELEGRAM_EDIT_MESSAGE` - Edit a sent message [Optional]
2. `TELEGRAM_DELETE_MESSAGE` - Delete a message [Optional]

**Key parameters**:
- `chat_id`: Chat where the message is located
- `message_id`: ID of the message to edit or delete
- `text`: New text content (for edit)

**Pitfalls**:
- Bots can only edit their own messages
- Messages can only be deleted within 48 hours of sending
- In groups, bots with delete permissions can delete any message
- Editing a message removes its 'edited' timestamp history

### 5. Forward Messages and Get Updates

**When to use**: User wants to forward messages or retrieve recent updates

**Tool sequence**:
1. `TELEGRAM_FORWARD_MESSAGE` - Forward a message to another chat [Optional]
2. `TELEGRAM_GET_UPDATES` - Get recent bot updates/messages [Optional]
3. `TELEGRAM_GET_CHAT_HISTORY` - Get chat message history [Optional]

**Key parameters**:
- `from_chat_id`: Source chat for forwarding
- `chat_id`: Destination chat for forwarding
- `message_id`: Message to forward
- `offset`: Update offset for GET_UPDATES
- `limit`: Number of updates to retrieve

**Pitfalls**:
- Forwarded messages show the original sender attribution
- GET_UPDATES returns a limited window of recent updates
- Chat history access may be limited by bot permissions and chat type
- Use offset to avoid processing the same update twice

### 6. Manage Bot Commands

**When to use**: User wants to set or update bot command menu

**Tool sequence**:
1. `TELEGRAM_SET_MY_COMMANDS` - Set the bot's command list [Required]
2. `TELEGRAM_ANSWER_CALLBACK_QUERY` - Respond to inline button presses [Optional]

**Key parameters**:
- `commands`: Array of command objects with `command` and `description`
- `callback_query_id`: ID of the callback query to answer

**Pitfalls**:
- Commands must start with '/' and be lowercase
- Command descriptions have a 256 character limit
- Callback queries must be answered within 10 seconds or they expire
- Setting commands replaces the entire command list

## Common Patterns

### Chat ID Resolution

**From username**:
```
1. Use '@username' format as chat_id (for public channels/groups)
2. For private chats, numeric chat_id is required
3. Call GET_CHAT with username to retrieve numeric ID
```

**From GET_UPDATES**:
```
1. Call TELEGRAM_GET_UPDATES
2. Extract chat.id from message objects
3. Use numeric chat_id in subsequent calls
```

### Message Formatting

- Use `parse_mode: 'HTML'` for `<b>bold</b>`, `<i>italic</i>`, `<code>code</code>`
- Use `parse_mode: 'MarkdownV2'` for `*bold*`, `_italic_`, `` `code` ``
- Escape special chars in MarkdownV2: `_ * [ ] ( ) ~ > # + - = | { } . !`
- Omit parse_mode for plain text without formatting

## Known Pitfalls

**Bot Permissions**:
- Bots must be added to groups/channels to interact
- Admin permissions needed for: deleting messages, exporting invite links, managing members
- Bots cannot initiate conversations; users must start them first

**Rate Limits**:
- 30 messages per second to the same group
- 20 messages per minute to the same user in groups
- Bulk operations should implement delays between calls
- API returns 429 Too Many Requests when limits are hit

**Chat Types**:
- Private chat: One-on-one with the bot
- Group: Multi-user chat (bot must be added)
- Supergroup: Enhanced group with admin features
- Channel: Broadcast-only (bot must be admin to post)

**Message Limits**:
- Text messages: 4096 characters max
- Captions: 1024 characters max
- File uploads: 50MB max via bot API
- Inline keyboard buttons: 8 per row

## Quick Reference

| Task | Tool Slug | Key Params |
|------|-----------|------------|
| Verify bot | TELEGRAM_GET_ME | (none) |
| Send message | TELEGRAM_SEND_MESSAGE | chat_id, text, parse_mode |
| Send photo | TELEGRAM_SEND_PHOTO | chat_id, photo, caption |
| Send document | TELEGRAM_SEND_DOCUMENT | chat_id, document, caption |
| Edit message | TELEGRAM_EDIT_MESSAGE | chat_id, message_id, text |
| Delete message | TELEGRAM_DELETE_MESSAGE | chat_id, message_id |
| Forward message | TELEGRAM_FORWARD_MESSAGE | chat_id, from_chat_id, message_id |
| Get chat info | TELEGRAM_GET_CHAT | chat_id |
| Get chat admins | TELEGRAM_GET_CHAT_ADMINISTRATORS | chat_id |
| Get member count | TELEGRAM_GET_CHAT_MEMBERS_COUNT | chat_id |
| Export invite link | TELEGRAM_EXPORT_CHAT_INVITE_LINK | chat_id |
| Get updates | TELEGRAM_GET_UPDATES | offset, limit |
| Get chat history | TELEGRAM_GET_CHAT_HISTORY | chat_id |
| Set bot commands | TELEGRAM_SET_MY_COMMANDS | commands |
| Answer callback | TELEGRAM_ANSWER_CALLBACK_QUERY | callback_query_id |
