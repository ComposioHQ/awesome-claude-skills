---
name: instagram-automation
description: "Automate Instagram tasks via Rube MCP (Composio): create posts, carousels, manage media, get insights, and publishing limits. Always search tools first for current schemas."
requires:
  mcp: [rube]
---

# Instagram Automation via Rube MCP

Automate Instagram operations through Composio's Instagram toolkit via Rube MCP.

## Prerequisites

- Rube MCP must be connected (RUBE_SEARCH_TOOLS available)
- Active Instagram connection via `RUBE_MANAGE_CONNECTIONS` with toolkit `instagram`
- Always call `RUBE_SEARCH_TOOLS` first to get current tool schemas
- Instagram Business or Creator account required (personal accounts not supported)

## Setup

**Get Rube MCP**: Add `https://rube.app/mcp` as an MCP server in your client configuration. No API keys needed — just add the endpoint and it works.


1. Verify Rube MCP is available by confirming `RUBE_SEARCH_TOOLS` responds
2. Call `RUBE_MANAGE_CONNECTIONS` with toolkit `instagram`
3. If connection is not ACTIVE, follow the returned auth link to complete Instagram/Facebook OAuth
4. Confirm connection status shows ACTIVE before running any workflows

## Core Workflows

### 1. Create a Single Image/Video Post

**When to use**: User wants to publish a single photo or video to Instagram

**Tool sequence**:
1. `INSTAGRAM_GET_USER_INFO` - Get Instagram user ID [Prerequisite]
2. `INSTAGRAM_CREATE_MEDIA_CONTAINER` - Create a media container with the image/video URL [Required]
3. `INSTAGRAM_GET_POST_STATUS` - Check if the media container is ready [Optional]
4. `INSTAGRAM_CREATE_POST` or `INSTAGRAM_POST_IG_USER_MEDIA_PUBLISH` - Publish the container [Required]

**Key parameters**:
- `image_url`: Public URL of the image to post
- `video_url`: Public URL of the video to post
- `caption`: Post caption text
- `ig_user_id`: Instagram Business account user ID

**Pitfalls**:
- Media URLs must be publicly accessible; private/authenticated URLs will fail
- Video containers may take time to process; poll GET_POST_STATUS before publishing
- Caption supports hashtags and mentions but has a 2200 character limit
- Publishing a container that is not yet finished processing returns an error

### 2. Create a Carousel Post

**When to use**: User wants to publish multiple images/videos in a single carousel post

**Tool sequence**:
1. `INSTAGRAM_CREATE_MEDIA_CONTAINER` - Create individual containers for each media item [Required, repeat per item]
2. `INSTAGRAM_CREATE_CAROUSEL_CONTAINER` - Create the carousel container referencing all media containers [Required]
3. `INSTAGRAM_GET_POST_STATUS` - Check carousel container readiness [Optional]
4. `INSTAGRAM_POST_IG_USER_MEDIA_PUBLISH` - Publish the carousel [Required]

**Key parameters**:
- `children`: Array of media container IDs for the carousel
- `caption`: Carousel post caption
- `ig_user_id`: Instagram Business account user ID

**Pitfalls**:
- Carousels require 2-10 media items; fewer or more will fail
- Each child container must be created individually before the carousel container
- All child containers must be fully processed before creating the carousel
- Mixed media (images + videos) is supported in carousels

### 3. Get Media and Insights

**When to use**: User wants to view their posts or analyze post performance

**Tool sequence**:
1. `INSTAGRAM_GET_IG_USER_MEDIA` or `INSTAGRAM_GET_USER_MEDIA` - List user's media [Required]
2. `INSTAGRAM_GET_IG_MEDIA` - Get details for a specific post [Optional]
3. `INSTAGRAM_GET_POST_INSIGHTS` or `INSTAGRAM_GET_IG_MEDIA_INSIGHTS` - Get metrics for a post [Optional]
4. `INSTAGRAM_GET_USER_INSIGHTS` - Get account-level insights [Optional]

**Key parameters**:
- `ig_user_id`: Instagram Business account user ID
- `media_id`: ID of the specific media post
- `metric`: Metrics to retrieve (e.g., impressions, reach, engagement)
- `period`: Time period for insights (e.g., day, week, lifetime)

**Pitfalls**:
- Insights are only available for Business/Creator accounts
- Some metrics require minimum follower counts
- Insight data may have a delay of up to 48 hours
- The `period` parameter must match the metric type

### 4. Check Publishing Limits

**When to use**: User wants to verify they can publish before attempting a post

**Tool sequence**:
1. `INSTAGRAM_GET_IG_USER_CONTENT_PUBLISHING_LIMIT` - Check remaining publishing quota [Required]

**Key parameters**:
- `ig_user_id`: Instagram Business account user ID

**Pitfalls**:
- Instagram enforces a 25 posts per 24-hour rolling window limit
- Publishing limit resets on a rolling basis, not at midnight
- Check limits before bulk posting operations to avoid failures

### 5. Get Media Comments and Children

**When to use**: User wants to view comments on a post or children of a carousel

**Tool sequence**:
1. `INSTAGRAM_GET_IG_MEDIA_COMMENTS` - List comments on a media post [Required]
2. `INSTAGRAM_GET_IG_MEDIA_CHILDREN` - List children of a carousel post [Optional]

**Key parameters**:
- `media_id`: ID of the media post
- `ig_media_id`: Alternative media ID parameter

**Pitfalls**:
- Comments may be paginated; follow pagination cursors for complete results
- Carousel children are returned as individual media objects
- Comment moderation settings on the account affect what is returned

## Common Patterns

### ID Resolution

**Instagram User ID**:
```
1. Call INSTAGRAM_GET_USER_INFO
2. Extract ig_user_id from response
3. Use in all subsequent API calls
```

**Media Container Status Check**:
```
1. Call INSTAGRAM_CREATE_MEDIA_CONTAINER
2. Extract container_id from response
3. Poll INSTAGRAM_GET_POST_STATUS with container_id
4. Wait until status is 'FINISHED' before publishing
```

### Two-Phase Publishing

- Phase 1: Create media container(s) with content URLs
- Phase 2: Publish the container after it finishes processing
- Always check container status between phases for video content
- For carousels, all children must complete Phase 1 before creating the carousel container

## Known Pitfalls

**Media URLs**:
- All image/video URLs must be publicly accessible HTTPS URLs
- URLs behind authentication, CDN restrictions, or that require cookies will fail
- Temporary URLs (pre-signed S3, etc.) may expire before processing completes

**Rate Limits**:
- 25 posts per 24-hour rolling window
- API rate limits apply separately from publishing limits
- Implement exponential backoff for 429 responses

**Account Requirements**:
- Only Business or Creator Instagram accounts are supported
- Personal accounts cannot use the Instagram Graph API
- The account must be connected to a Facebook Page

**Response Parsing**:
- Media IDs are numeric strings
- Insights data may be nested under different response keys
- Pagination uses cursor-based tokens

## Quick Reference

| Task | Tool Slug | Key Params |
|------|-----------|------------|
| Get user info | INSTAGRAM_GET_USER_INFO | (none) |
| Create media container | INSTAGRAM_CREATE_MEDIA_CONTAINER | image_url/video_url, caption |
| Create carousel | INSTAGRAM_CREATE_CAROUSEL_CONTAINER | children, caption |
| Publish post | INSTAGRAM_CREATE_POST | ig_user_id, creation_id |
| Publish media | INSTAGRAM_POST_IG_USER_MEDIA_PUBLISH | ig_user_id, creation_id |
| Check post status | INSTAGRAM_GET_POST_STATUS | ig_container_id |
| List user media | INSTAGRAM_GET_IG_USER_MEDIA | ig_user_id |
| Get media details | INSTAGRAM_GET_IG_MEDIA | ig_media_id |
| Get post insights | INSTAGRAM_GET_POST_INSIGHTS | media_id, metric |
| Get user insights | INSTAGRAM_GET_USER_INSIGHTS | ig_user_id, metric, period |
| Get publishing limit | INSTAGRAM_GET_IG_USER_CONTENT_PUBLISHING_LIMIT | ig_user_id |
| Get media comments | INSTAGRAM_GET_IG_MEDIA_COMMENTS | ig_media_id |
| Get carousel children | INSTAGRAM_GET_IG_MEDIA_CHILDREN | ig_media_id |
