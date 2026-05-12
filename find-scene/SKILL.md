---
name: find-scene
description: Search movie and TV show scenes by dialog, time, or visual description using the FindScene API. Use when the user wants to find, download, or identify a scene from a film or TV series, extract a frame, search for a quote, or get movie information.
---

# Find Scene

Search and download movie/TV show scenes by dialog, time, or visual description via the [FindScene API](https://find-scene.com).

## Authentication

Every API request requires a `_token` field in the JSON body. Get a token by visiting [find-scene.com](https://find-scene.com), signing in, and asking the bot to "generate an API token".

```json
{ "_token": "your-api-token", ...other fields }
```

## Base URL

```
https://api.find-scene.com
```

All endpoints are `POST` with `Content-Type: application/json`, except `GET /api/operation/{id}`.

## Key Concepts

- **Video Source Hash**: Internal ID for a video file. Get it from `get_best_video_source`. Required for downloads and frame extraction.
- **Text Source Hash**: Internal ID for a subtitle file. Get it from `get_text_source`. Required for phrase search.
- **Async Operations**: `download_by_time` and `extract_frame` return an operation ID. Poll `GET /api/operation/{id}` until `status` is `completed`, then use the `url` field.

## Common Workflows

### Find and download a scene by quote

```
1. quote_to_movie        -> identify the movie
2. get_best_video_source -> get videoHash
3. get_text_source       -> get textSource hash
4. search_phrase         -> find exact timestamp
5. download_by_time      -> returns operation ID
6. GET /api/operation/id -> poll until completed, get download URL
```

### Search by visual scene description

```
1. find_by_scene_description -> describe what happens visually
2. get_best_video_source     -> get videoHash for the result
3. download_by_time          -> download the scene
4. GET /api/operation/id     -> poll until completed
```

### Extract a frame / screenshot

```
1. get_best_video_source -> get videoHash
2. extract_frame         -> returns operation ID
3. GET /api/operation/id -> poll until completed, get image URL
```

## Example

**Identify a movie from a quote:**

```bash
curl -s https://api.find-scene.com/api/quote_to_movie \
  -H "Content-Type: application/json" \
  -d '{"_token": "...", "quote": "I am the one who knocks"}'
# -> {"result": "Breaking Bad"}
```

**Check remaining credits:**

```bash
curl -s https://api.find-scene.com/api/check_quota \
  -H "Content-Type: application/json" \
  -d '{"_token": "..."}'
# -> {"result": "The user has 18 credits remaining this month."}
```

## Available Endpoints

| Endpoint | Description |
|----------|-------------|
| `quote_to_movie` | Identify which movie a quote is from |
| `find_episode_by_phrase` | Find which TV episode contains a phrase |
| `search_phrase` | Search for a phrase in subtitles with timestamps |
| `find_by_scene_description` | Search by visual scene description |
| `get_best_video_source` | Get video source hash for a title |
| `get_text_source` | Get subtitle source hash |
| `get_high_accuracy_text_source` | Get subtitle source with accurate timing |
| `download_by_time` | Download a video clip (async) |
| `extract_frame` | Extract a screenshot (async) |
| `transcribe_by_time` | Transcribe a video segment |
| `query_imdb` | Get IMDB information |
| `popular_quotes_from_title` | Get popular quotes from a title |
| `is_string_a_movie_name` | Check if a string is a movie name |
| `check_quota` | Check remaining monthly credits |
| `youtube_url_to_video_source` | Convert YouTube URL to video source |

## Tips

- Always get the video source hash before downloads or frame extraction.
- `download_by_time` and `extract_frame` return operation IDs, not URLs. You must poll.
- Keep clip durations under 60 seconds for faster processing.
- For TV series, use `find_episode_by_phrase` to identify the episode first.
- Full OpenAPI spec: `https://api.find-scene.com/api/openapi.json`
- Full skill with detailed parameter schemas: [github.com/uriva/find-scene-skill](https://github.com/uriva/find-scene-skill)
