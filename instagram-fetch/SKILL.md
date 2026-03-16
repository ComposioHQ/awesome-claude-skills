---
name: instagram-fetch
description: Fetch and analyze Instagram posts, reels, and stories. Use when a user shares an Instagram URL (post, reel, or story) and wants to extract content, captions, metadata, or download media. Uses yt-dlp for media download and metadata extraction. Requires yt-dlp and optionally Instagram credentials for private content.
---

# Instagram Fetch Skill

Fetch metadata, captions, and media from Instagram posts, reels, and stories using yt-dlp.

## When to Use This Skill

Activate when the user shares an Instagram URL such as:
- `https://www.instagram.com/reel/...`
- `https://www.instagram.com/p/...`
- `https://www.instagram.com/stories/...`
- Any Instagram URL and asks to "fetch", "download", "analyze", or "summarize" it

## Prerequisites

### Install yt-dlp
```bash
pip install yt-dlp
# or
brew install yt-dlp
# or
sudo apt install yt-dlp
```

**Verify:**
```bash
yt-dlp --version
```

### (Optional) Instagram Login for Private Content
For private accounts or stories that require login:
```bash
# Login via browser cookies (recommended - no password needed)
yt-dlp --cookies-from-browser chrome "INSTAGRAM_URL"

# Or using username/password
yt-dlp -u YOUR_USERNAME -p YOUR_PASSWORD "INSTAGRAM_URL"
```

## Core Workflows

### Workflow 1: Fetch Reel/Post Metadata Only

**When user shares a URL and wants caption/info without downloading:**

```bash
yt-dlp --dump-json --no-download "INSTAGRAM_URL" 2>/dev/null
```

**Parse and report:**
1. `title` / `description` — caption text
2. `uploader` / `uploader_id` — account name
3. `timestamp` — post date
4. `like_count`, `comment_count`, `view_count` — engagement
5. `duration` — video length (reels)
6. `thumbnail` — cover image URL

**Example response format:**
```
Instagram Reel — @username

Caption: "Check out this amazing sunset! 🌅 #travel #photography"

Stats:
- Views: 1.2M
- Likes: 45,000
- Comments: 892
- Duration: 0:32
- Posted: 2025-03-10

Direct URL: https://www.instagram.com/reel/ABC123/
```

---

### Workflow 2: Download Reel/Post Video

**When user wants to save the video:**

```bash
# Download best quality to current directory
yt-dlp -o "%(uploader)s_%(id)s.%(ext)s" "INSTAGRAM_URL"

# Download to specific output folder
yt-dlp -o "/mnt/user-data/outputs/%(uploader)s_%(id)s.%(ext)s" "INSTAGRAM_URL"

# Download with cookies from browser (for private content)
yt-dlp --cookies-from-browser chrome -o "%(uploader)s_%(id)s.%(ext)s" "INSTAGRAM_URL"
```

**Report:**
```
Downloaded: username_DVwYONVAVfj.mp4
Size: 12.4 MB
Quality: 1080x1920 (1080p)
Saved to: /mnt/user-data/outputs/
```

---

### Workflow 3: Extract Caption/Text Only

**When user wants just the caption text:**

```bash
yt-dlp --dump-json --no-download "INSTAGRAM_URL" 2>/dev/null | python3 -c "
import json, sys
data = json.load(sys.stdin)
print('Caption:', data.get('description', data.get('title', 'No caption found')))
print('Posted by:', data.get('uploader', 'Unknown'))
print('Date:', data.get('upload_date', 'Unknown'))
"
```

---

### Workflow 4: Download Thumbnail/Cover Image

**When user wants the cover image:**

```bash
yt-dlp --write-thumbnail --skip-download -o "%(uploader)s_%(id)s" "INSTAGRAM_URL"
```

---

### Workflow 5: Batch Fetch Multiple URLs

**When user provides multiple Instagram links:**

```bash
# Save URLs to a file
cat > instagram_urls.txt << 'EOF'
https://www.instagram.com/reel/URL1/
https://www.instagram.com/reel/URL2/
https://www.instagram.com/p/URL3/
EOF

# Fetch metadata for all
yt-dlp --dump-json --no-download -a instagram_urls.txt 2>/dev/null
```

---

## Handling Common Issues

### 403 Forbidden / Login Required

Instagram often blocks unauthenticated requests. Solutions:

```bash
# Option 1: Use browser cookies (best method)
yt-dlp --cookies-from-browser chrome "INSTAGRAM_URL"
yt-dlp --cookies-from-browser firefox "INSTAGRAM_URL"

# Option 2: Export cookies manually and use cookie file
# In Chrome: use a cookies.txt extension, save to cookies.txt
yt-dlp --cookies cookies.txt "INSTAGRAM_URL"

# Option 3: Username/password (less reliable due to 2FA)
yt-dlp -u your@email.com -p yourpassword "INSTAGRAM_URL"
```

### Rate Limiting

```bash
# Add delays between requests
yt-dlp --sleep-interval 3 --max-sleep-interval 10 "INSTAGRAM_URL"
```

### Private Content

```bash
# Must use cookies from a logged-in browser session
yt-dlp --cookies-from-browser chrome "INSTAGRAM_URL"
```

### CSRF Token Warning

The warning `No csrf token set by Instagram API` is common and usually harmless. The download often still succeeds.

---

## Output Parsing (Python Helper)

When you get JSON from `--dump-json`, parse it like this:

```python
import json, subprocess

result = subprocess.run(
    ["yt-dlp", "--dump-json", "--no-download", "INSTAGRAM_URL"],
    capture_output=True, text=True
)

if result.returncode == 0:
    data = json.loads(result.stdout)
    print(f"Title: {data.get('title', 'N/A')}")
    print(f"Caption: {data.get('description', 'N/A')}")
    print(f"Uploader: {data.get('uploader', 'N/A')} (@{data.get('uploader_id', 'N/A')})")
    print(f"Views: {data.get('view_count', 'N/A'):,}")
    print(f"Likes: {data.get('like_count', 'N/A'):,}")
    print(f"Comments: {data.get('comment_count', 'N/A'):,}")
    print(f"Duration: {data.get('duration', 0)}s")
    print(f"Upload date: {data.get('upload_date', 'N/A')}")
    print(f"Thumbnail: {data.get('thumbnail', 'N/A')}")
else:
    print("Error:", result.stderr)
```

---

## Quick Reference

```bash
# Metadata only (no download)
yt-dlp --dump-json --no-download "URL"

# Download video
yt-dlp "URL"

# Download with browser cookies
yt-dlp --cookies-from-browser chrome "URL"

# Caption only
yt-dlp --dump-json --no-download "URL" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('description',''))"

# Thumbnail only
yt-dlp --write-thumbnail --skip-download "URL"

# Save to specific folder
yt-dlp -o "/path/to/folder/%(uploader)s_%(id)s.%(ext)s" "URL"
```

---

## Notes for Claude

- Always try `--dump-json --no-download` first to avoid unnecessary downloads
- If 403 error occurs, suggest using `--cookies-from-browser chrome` or `firefox`
- Instagram blocks sandbox/server environments — this skill works best when run locally by the user
- For reels: key fields are `description` (caption), `uploader`, `view_count`, `like_count`
- The reel ID is in the URL: `instagram.com/reel/{REEL_ID}/`
- Always show the extracted caption prominently — that's usually what users want
- If network is blocked (proxy/sandbox), explain this clearly and provide the commands for the user to run locally

---

**Version:** 1.0.0
**Requires:** yt-dlp (`pip install yt-dlp`)
**Works with:** Instagram Reels, Posts (photos & carousels), IGTV
**Does NOT work with:** Instagram Stories (requires login + they expire)
