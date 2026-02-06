---
name: tiktok-automation
description: "Automate TikTok tasks via Rube MCP (Composio): upload/publish videos, post photos, manage content, and view user profiles/stats. Always search tools first for current schemas."
requires:
  mcp: [rube]
---

# TikTok Automation via Rube MCP

Automate TikTok content creation and profile operations through Composio's TikTok toolkit via Rube MCP.

## Prerequisites

- Rube MCP must be connected (RUBE_SEARCH_TOOLS available)
- Active TikTok connection via `RUBE_MANAGE_CONNECTIONS` with toolkit `tiktok`
- Always call `RUBE_SEARCH_TOOLS` first to get current tool schemas

## Setup

**Get Rube MCP**: Add `https://rube.app/mcp` as an MCP server in your client configuration. No API keys needed — just add the endpoint and it works.


1. Verify Rube MCP is available by confirming `RUBE_SEARCH_TOOLS` responds
2. Call `RUBE_MANAGE_CONNECTIONS` with toolkit `tiktok`
3. If connection is not ACTIVE, follow the returned auth link to complete TikTok OAuth
4. Confirm connection status shows ACTIVE before running any workflows

## Core Workflows

### 1. Upload and Publish a Video

**When to use**: User wants to upload a video and publish it to TikTok

**Tool sequence**:
1. `TIKTOK_UPLOAD_VIDEO` or `TIKTOK_UPLOAD_VIDEOS` - Upload video file(s) [Required]
2. `TIKTOK_FETCH_PUBLISH_STATUS` - Check upload/processing status [Required]
3. `TIKTOK_PUBLISH_VIDEO` - Publish the uploaded video [Required]

**Key parameters for upload**:
- `video`: Video file object with `s3key`, `mimetype`, `name`
- `title`: Video title/caption

**Key parameters for publish**:
- `publish_id`: ID returned from upload step
- `title`: Video caption text
- `privacy_level`: 'PUBLIC_TO_EVERYONE', 'MUTUAL_FOLLOW_FRIENDS', 'FOLLOWER_OF_CREATOR', 'SELF_ONLY'
- `disable_duet`: Disable duet feature
- `disable_stitch`: Disable stitch feature
- `disable_comment`: Disable comments

**Pitfalls**:
- Video upload and publish are TWO separate steps; upload first, then publish
- After upload, poll FETCH_PUBLISH_STATUS until processing is complete before publishing
- Video must meet TikTok requirements: MP4/WebM format, max 10 minutes, max 4GB
- Caption/title has character limits; check current TikTok guidelines
- Privacy level strings are case-sensitive and must match exactly
- Processing may take 30-120 seconds depending on video size

### 2. Post a Photo

**When to use**: User wants to post a photo to TikTok

**Tool sequence**:
1. `TIKTOK_POST_PHOTO` - Upload and post a photo [Required]
2. `TIKTOK_FETCH_PUBLISH_STATUS` - Check processing status [Optional]

**Key parameters**:
- `photo`: Photo file object with `s3key`, `mimetype`, `name`
- `title`: Photo caption text
- `privacy_level`: Privacy setting for the post

**Pitfalls**:
- Photo posts are a newer TikTok feature; availability may vary by account type
- Supported formats: JPEG, PNG, WebP
- Image size and dimension limits apply; check current TikTok guidelines

### 3. List and Manage Videos

**When to use**: User wants to view their published videos

**Tool sequence**:
1. `TIKTOK_LIST_VIDEOS` - List user's published videos [Required]

**Key parameters**:
- `max_count`: Number of videos to return per page
- `cursor`: Pagination cursor for next page

**Pitfalls**:
- Only returns the authenticated user's own videos
- Response includes video metadata: id, title, create_time, share_url, duration, etc.
- Pagination uses cursor-based approach; check for `has_more` and `cursor` in response
- Recently published videos may not appear immediately in the list

### 4. View User Profile and Stats

**When to use**: User wants to check their TikTok profile info or account statistics

**Tool sequence**:
1. `TIKTOK_GET_USER_PROFILE` - Get full profile information [Required]
2. `TIKTOK_GET_USER_STATS` - Get account statistics [Optional]
3. `TIKTOK_GET_USER_BASIC_INFO` - Get basic user info [Alternative]

**Key parameters**: (no required parameters; returns data for authenticated user)

**Pitfalls**:
- Profile data is for the authenticated user only; cannot view other users' profiles
- Stats include follower count, following count, video count, likes received
- `GET_USER_PROFILE` returns more details than `GET_USER_BASIC_INFO`
- Stats may have slight delays; not real-time

### 5. Check Publish Status

**When to use**: User wants to check the status of a content upload or publish operation

**Tool sequence**:
1. `TIKTOK_FETCH_PUBLISH_STATUS` - Poll for status updates [Required]

**Key parameters**:
- `publish_id`: The publish ID from a previous upload/publish operation

**Pitfalls**:
- Status values include processing, success, and failure states
- Poll at reasonable intervals (5-10 seconds) to avoid rate limits
- Failed publishes include error details in the response
- Content moderation may cause delays or rejections after processing

## Common Patterns

### Video Publish Flow

```
1. Upload video via TIKTOK_UPLOAD_VIDEO -> get publish_id
2. Poll TIKTOK_FETCH_PUBLISH_STATUS with publish_id until complete
3. If status is ready, call TIKTOK_PUBLISH_VIDEO with final settings
4. Optionally poll status again to confirm publication
```

### Pagination

- Use `cursor` from previous response for next page
- Check `has_more` boolean to determine if more results exist
- `max_count` controls page size

## Known Pitfalls

**Content Requirements**:
- Videos: MP4/WebM, max 4GB, max 10 minutes
- Photos: JPEG/PNG/WebP
- Captions: Character limits vary by region
- Content must comply with TikTok community guidelines

**Authentication**:
- OAuth tokens have scopes; ensure video.upload and video.publish are authorized
- Tokens expire; re-authenticate if operations fail with 401

**Rate Limits**:
- TikTok API has strict rate limits per application
- Implement exponential backoff on 429 responses
- Upload operations have daily limits

**Response Parsing**:
- Response data may be nested under `data` or `data.data`
- Parse defensively with fallback patterns
- Publish IDs are strings; use exactly as returned

## Quick Reference

| Task | Tool Slug | Key Params |
|------|-----------|------------|
| Upload video | TIKTOK_UPLOAD_VIDEO | video, title |
| Upload multiple videos | TIKTOK_UPLOAD_VIDEOS | videos |
| Publish video | TIKTOK_PUBLISH_VIDEO | publish_id, title, privacy_level |
| Post photo | TIKTOK_POST_PHOTO | photo, title, privacy_level |
| List videos | TIKTOK_LIST_VIDEOS | max_count, cursor |
| Get profile | TIKTOK_GET_USER_PROFILE | (none) |
| Get user stats | TIKTOK_GET_USER_STATS | (none) |
| Get basic info | TIKTOK_GET_USER_BASIC_INFO | (none) |
| Check publish status | TIKTOK_FETCH_PUBLISH_STATUS | publish_id |
