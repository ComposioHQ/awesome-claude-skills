---
name: Spotify Automation
description: "Automate Spotify workflows including playlist management, music search, playback control, and user profile access via Composio"
requires:
  mcp:
    - rube
---

# Spotify Automation

Automate Spotify operations -- manage playlists, search the music catalog, control playback, browse albums and tracks, and access user profiles -- all orchestrated through the Composio MCP integration.

**Toolkit docs:** [composio.dev/toolkits/spotify](https://composio.dev/toolkits/spotify)

---

## Setup

1. Connect your Spotify account through the Composio MCP server at `https://rube.app/mcp`
2. The agent will prompt you with an authentication link if no active connection exists
3. Once connected, all `SPOTIFY_*` tools become available for execution
4. **Note:** Some features (playback control) require a Spotify Premium subscription

---

## Core Workflows

### 1. Get Current User Profile
Retrieve comprehensive profile information for the authenticated Spotify user.

**Tool:** `SPOTIFY_GET_CURRENT_USER_S_PROFILE`

```
No parameters required.
Returns: display name, email, country, subscription level (premium/free),
explicit content settings, profile images, follower count, and Spotify URIs.
Required scopes: user-read-private, user-read-email.
```

---

### 2. Search the Spotify Catalog
Find albums, artists, playlists, tracks, shows, episodes, or audiobooks by keyword.

**Tool:** `SPOTIFY_SEARCH_FOR_ITEM`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `q` | string | Yes | Search query keywords |
| `type` | array | Yes | Item types: `album`, `artist`, `playlist`, `track`, `show`, `episode`, `audiobook` |
| `limit` | integer | No | Results to return (default: 20) |
| `offset` | integer | No | Offset for pagination (default: 0) |
| `market` | string | No | ISO 3166-1 alpha-2 country code |
| `include_external` | string | No | Set to `audio` to include external content |

**Note:** Audiobooks are only available in US, UK, Canada, Ireland, New Zealand, and Australia.

---

### 3. Manage Playlists
Browse, create, modify, and populate playlists.

**Get a user's playlists:**

**Tool:** `SPOTIFY_GET_USER_S_PLAYLISTS`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_id` | string | Yes | Spotify user ID |
| `limit` | integer | No | Max playlists, 1-50 (default: 20) |
| `offset` | integer | No | Pagination offset, 0-100000 (default: 0) |

**Get current user's playlists:**

**Tool:** `SPOTIFY_GET_CURRENT_USER_S_PLAYLISTS`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `limit` | integer | No | Max playlists, 1-50 (default: 20) |
| `offset` | integer | No | Pagination offset, 0-100000 (default: 0) |

**Get playlist details:**

**Tool:** `SPOTIFY_GET_PLAYLIST`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `playlist_id` | string | Yes | Spotify playlist ID (e.g., `3cEYpjA9oz9GiPac4AsH4n`) |
| `fields` | string | No | Comma-separated field filter to reduce response size |
| `market` | string | No | ISO country code for market-specific content |
| `additional_types` | string | No | `track,episode` to include podcast episodes |

**Update playlist details:**

**Tool:** `SPOTIFY_CHANGE_PLAYLIST_DETAILS`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `playlist_id` | string | Yes | Playlist ID (must be owned by current user) |
| `name` | string | No | New playlist name |
| `description` | string | No | New playlist description |
| `public` | boolean | No | Public/private toggle |
| `collaborative` | boolean | No | Collaborative mode (only on non-public playlists) |

---

### 4. Browse Playlist Items & Add Tracks
View tracks in a playlist and add new items.

**Tool:** `SPOTIFY_GET_PLAYLIST_ITEMS`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `playlist_id` | string | Yes | Spotify playlist ID |
| `limit` | integer | No | Items per page, 1-50 (default: 20) |
| `offset` | integer | No | Pagination offset (default: 0) |
| `fields` | string | No | Field filter (e.g., `items(track(name,id))`) |
| `market` | string | No | ISO country code |
| `additional_types` | string | No | `track,episode` for podcast episodes |

**Tool:** `SPOTIFY_ADD_ITEMS_TO_PLAYLIST`

Add tracks or episodes to a playlist using Spotify URIs.

---

### 5. Get Track & Album Details
Retrieve catalog information for individual tracks and albums.

**Tool:** `SPOTIFY_GET_TRACK` -- Get details for a single track by Spotify ID.

**Tool:** `SPOTIFY_GET_ALBUM` -- Get comprehensive album data including track listing, artist info, cover art, and popularity.

---

### 6. Control Playback
Start, resume, or change playback on the user's active device.

**Tool:** `SPOTIFY_START_RESUME_PLAYBACK`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `context_uri` | string | No | Spotify URI of album, artist, or playlist (cannot combine with `uris`) |
| `uris` | array | No | List of track URIs to play (cannot combine with `context_uri`) |
| `offset` | object | No | Starting position: `{position: 5}` or `{uri: 'spotify:track:...'}` |
| `position_ms` | integer | No | Start position in milliseconds |
| `device_id` | string | No | Target device ID (defaults to active device) |

**Requirements:** Spotify Premium subscription and at least one active device.

---

## Known Pitfalls

| Pitfall | Details |
|---------|---------|
| **Premium required for playback** | `SPOTIFY_START_RESUME_PLAYBACK` returns 403 if the user does not have Spotify Premium |
| **Active device required** | Playback control returns 404 if no Spotify device (mobile, desktop, web, speaker) is active |
| **context_uri vs uris are exclusive** | Cannot use both `context_uri` and `uris` in the same playback call |
| **Collaborative playlists** | `collaborative` can only be set to `true` on non-public playlists (`public` must be `false`) |
| **Playlist ownership** | `SPOTIFY_CHANGE_PLAYLIST_DETAILS` only works on playlists owned by the authenticated user |
| **Audiobook market restrictions** | Audiobooks via search are only available in US, UK, Canada, Ireland, New Zealand, and Australia |
| **Max 11000 playlists** | Users are limited to approximately 11,000 playlists via `SPOTIFY_CREATE_PLAYLIST` |

---

## Quick Reference

| Tool Slug | Purpose |
|-----------|---------|
| `SPOTIFY_GET_CURRENT_USER_S_PROFILE` | Get authenticated user's profile |
| `SPOTIFY_SEARCH_FOR_ITEM` | Search catalog for tracks, albums, artists, etc. |
| `SPOTIFY_GET_USER_S_PLAYLISTS` | Get playlists for any user |
| `SPOTIFY_GET_CURRENT_USER_S_PLAYLISTS` | Get current user's playlists |
| `SPOTIFY_GET_PLAYLIST` | Get detailed playlist info |
| `SPOTIFY_GET_PLAYLIST_ITEMS` | List tracks/episodes in a playlist |
| `SPOTIFY_CHANGE_PLAYLIST_DETAILS` | Update playlist name, description, visibility |
| `SPOTIFY_CREATE_PLAYLIST` | Create a new playlist |
| `SPOTIFY_ADD_ITEMS_TO_PLAYLIST` | Add tracks/episodes to a playlist |
| `SPOTIFY_GET_TRACK` | Get track details by ID |
| `SPOTIFY_GET_ALBUM` | Get album details by ID |
| `SPOTIFY_START_RESUME_PLAYBACK` | Start or resume playback on a device |

---

*Powered by [Composio](https://composio.dev)*
