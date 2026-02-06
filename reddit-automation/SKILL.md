---
name: reddit-automation
description: "Automate Reddit tasks via Rube MCP (Composio): search subreddits, create posts, manage comments, and browse top content. Always search tools first for current schemas."
requires:
  mcp: [rube]
---

# Reddit Automation via Rube MCP

Automate Reddit operations through Composio's Reddit toolkit via Rube MCP.

## Prerequisites

- Rube MCP must be connected (RUBE_SEARCH_TOOLS available)
- Active Reddit connection via `RUBE_MANAGE_CONNECTIONS` with toolkit `reddit`
- Always call `RUBE_SEARCH_TOOLS` first to get current tool schemas

## Setup

**Get Rube MCP**: Add `https://rube.app/mcp` as an MCP server in your client configuration. No API keys needed — just add the endpoint and it works.


1. Verify Rube MCP is available by confirming `RUBE_SEARCH_TOOLS` responds
2. Call `RUBE_MANAGE_CONNECTIONS` with toolkit `reddit`
3. If connection is not ACTIVE, follow the returned auth link to complete Reddit OAuth
4. Confirm connection status shows ACTIVE before running any workflows

## Core Workflows

### 1. Search Reddit

**When to use**: User wants to find posts across subreddits

**Tool sequence**:
1. `REDDIT_SEARCH_ACROSS_SUBREDDITS` - Search for posts matching a query [Required]

**Key parameters**:
- `query`: Search terms
- `subreddit`: Limit search to a specific subreddit (optional)
- `sort`: Sort results by 'relevance', 'hot', 'top', 'new', 'comments'
- `time_filter`: Time range ('hour', 'day', 'week', 'month', 'year', 'all')
- `limit`: Number of results to return

**Pitfalls**:
- Search results may not include very recent posts due to indexing delay
- The `time_filter` parameter only works with certain sort options
- Results are paginated; use after/before tokens for additional pages
- NSFW content may be filtered based on account settings

### 2. Create Posts

**When to use**: User wants to submit a new post to a subreddit

**Tool sequence**:
1. `REDDIT_LIST_SUBREDDIT_POST_FLAIRS` - Get available post flairs [Optional]
2. `REDDIT_CREATE_REDDIT_POST` - Submit the post [Required]

**Key parameters**:
- `subreddit`: Target subreddit name (without 'r/' prefix)
- `title`: Post title
- `text`: Post body text (for text posts)
- `url`: Link URL (for link posts)
- `flair_id`: Flair ID from the subreddit's flair list

**Pitfalls**:
- Some subreddits require flair; use LIST_SUBREDDIT_POST_FLAIRS first
- Subreddit posting rules vary widely; karma/age restrictions may apply
- Text and URL are mutually exclusive; a post is either text or link
- Rate limits apply; avoid rapid successive post creation
- The subreddit name should not include 'r/' prefix

### 3. Manage Comments

**When to use**: User wants to comment on posts or manage existing comments

**Tool sequence**:
1. `REDDIT_RETRIEVE_POST_COMMENTS` - Get comments on a post [Optional]
2. `REDDIT_POST_REDDIT_COMMENT` - Add a comment to a post or reply to a comment [Required]
3. `REDDIT_EDIT_REDDIT_COMMENT_OR_POST` - Edit an existing comment [Optional]
4. `REDDIT_DELETE_REDDIT_COMMENT` - Delete a comment [Optional]

**Key parameters**:
- `post_id`: ID of the post (for retrieving or commenting on)
- `parent_id`: Full name of the parent (e.g., 't3_abc123' for post, 't1_xyz789' for comment)
- `body`: Comment text content
- `thing_id`: Full name of the item to edit or delete

**Pitfalls**:
- Reddit uses 'fullname' format: 't1_' prefix for comments, 't3_' for posts
- Editing replaces the entire comment body; include all desired content
- Deleted comments show as '[deleted]' but the tree structure remains
- Comment depth limits may apply in some subreddits

### 4. Browse Subreddit Content

**When to use**: User wants to view top or trending content from a subreddit

**Tool sequence**:
1. `REDDIT_GET_R_TOP` - Get top posts from a subreddit [Required]
2. `REDDIT_GET` - Get posts from a subreddit endpoint [Alternative]
3. `REDDIT_RETRIEVE_REDDIT_POST` - Get full details for a specific post [Optional]

**Key parameters**:
- `subreddit`: Subreddit name
- `time_filter`: Time range for top posts ('hour', 'day', 'week', 'month', 'year', 'all')
- `limit`: Number of posts to retrieve
- `post_id`: Specific post ID for full details

**Pitfalls**:
- Top posts with time_filter='all' returns all-time top content
- Post details include the body text but comments require a separate call
- Some posts may be removed or hidden based on subreddit rules
- NSFW posts are included unless filtered at the account level

### 5. Manage Posts

**When to use**: User wants to edit or delete their own posts

**Tool sequence**:
1. `REDDIT_EDIT_REDDIT_COMMENT_OR_POST` - Edit a post's text content [Optional]
2. `REDDIT_DELETE_REDDIT_POST` - Delete a post [Optional]
3. `REDDIT_GET_USER_FLAIR` - Get user's flair in a subreddit [Optional]

**Key parameters**:
- `thing_id`: Full name of the post (e.g., 't3_abc123')
- `body`: New text content (for editing)
- `subreddit`: Subreddit name (for flair)

**Pitfalls**:
- Only text posts can have their body edited; link posts cannot be modified
- Post titles cannot be edited after submission
- Deletion is permanent; deleted posts show as '[deleted]'
- User flair is per-subreddit and may be restricted

## Common Patterns

### Reddit Fullname Format

**Prefixes**:
```
t1_ = Comment (e.g., 't1_abc123')
t2_ = Account (e.g., 't2_xyz789')
t3_ = Post/Link (e.g., 't3_def456')
t4_ = Message
t5_ = Subreddit
```

**Usage**:
```
1. Retrieve a post to get its fullname (t3_XXXXX)
2. Use fullname as parent_id when commenting
3. Use fullname as thing_id when editing/deleting
```

### Pagination

- Reddit uses cursor-based pagination with 'after' and 'before' tokens
- Set `limit` for items per page (max 100)
- Check response for `after` token
- Pass `after` value in subsequent requests to get next page

### Flair Resolution

```
1. Call REDDIT_LIST_SUBREDDIT_POST_FLAIRS with subreddit name
2. Find matching flair by text or category
3. Extract flair_id
4. Include flair_id when creating the post
```

## Known Pitfalls

**Rate Limits**:
- Reddit enforces rate limits per account and per OAuth app
- Posting is limited to approximately 1 post per 10 minutes for new accounts
- Commenting has similar but less restrictive limits
- 429 errors should trigger exponential backoff

**Content Rules**:
- Each subreddit has its own posting rules and requirements
- Some subreddits are restricted or private
- Karma requirements may prevent posting in certain subreddits
- Auto-moderator rules may remove posts that match certain patterns

**ID Formats**:
- Always use fullname format (with prefix) for parent_id and thing_id
- Raw IDs without prefix will cause 'Invalid ID' errors
- Post IDs from search results may need 't3_' prefix added

**Text Formatting**:
- Reddit uses Markdown for post and comment formatting
- Code blocks, tables, and headers are supported
- Links use `[text](url)` format
- Mention users with `u/username`, subreddits with `r/subreddit`

## Quick Reference

| Task | Tool Slug | Key Params |
|------|-----------|------------|
| Search Reddit | REDDIT_SEARCH_ACROSS_SUBREDDITS | query, subreddit, sort, time_filter |
| Create post | REDDIT_CREATE_REDDIT_POST | subreddit, title, text/url |
| Get post comments | REDDIT_RETRIEVE_POST_COMMENTS | post_id |
| Add comment | REDDIT_POST_REDDIT_COMMENT | parent_id, body |
| Edit comment/post | REDDIT_EDIT_REDDIT_COMMENT_OR_POST | thing_id, body |
| Delete comment | REDDIT_DELETE_REDDIT_COMMENT | thing_id |
| Delete post | REDDIT_DELETE_REDDIT_POST | thing_id |
| Get top posts | REDDIT_GET_R_TOP | subreddit, time_filter, limit |
| Browse subreddit | REDDIT_GET | subreddit |
| Get post details | REDDIT_RETRIEVE_REDDIT_POST | post_id |
| Get specific comment | REDDIT_RETRIEVE_SPECIFIC_COMMENT | comment_id |
| List post flairs | REDDIT_LIST_SUBREDDIT_POST_FLAIRS | subreddit |
| Get user flair | REDDIT_GET_USER_FLAIR | subreddit |
