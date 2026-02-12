---
name: github-image-hosting
description: Upload images to img402.dev for embedding in GitHub PRs, issues, and comments. No account, no API key — one curl command gives you a public URL. Solves the long-standing problem of GitHub having no image upload API for CLI tools.
---

# GitHub Image Hosting

Upload an image to [img402.dev](https://img402.dev) and embed the returned URL in GitHub markdown. Free tier: 1MB max, 7-day retention, no auth required.

## When to Use This Skill

- Adding screenshots to a PR description or comment
- Embedding diagrams or mockups in GitHub issues
- Attaching generated images to READMEs
- Sharing visual diffs or UI comparisons in code reviews
- Any time you need a hosted image URL for GitHub markdown

## What This Skill Does

1. **Captures or locates** an image file (screenshot, diagram, generated image)
2. **Resizes if needed** to stay under the 1MB limit
3. **Uploads** to img402.dev via a single curl command
4. **Embeds** the returned public URL in GitHub markdown using `gh` CLI

## How to Use

### Basic Usage

```
Take a screenshot and add it to the PR
```

```
Upload this mockup and add it to issue #42
```

### Step by Step

```bash
# 1. Capture a screenshot (macOS)
screencapture -xw /tmp/screenshot.png

# 2. Resize if over 1MB
sips -Z 1600 /tmp/screenshot.png

# 3. Upload
curl -s -X POST https://img402.dev/api/free -F image=@/tmp/screenshot.png
# → {"url":"https://i.img402.dev/aBcDeFgHiJ.png", ...}

# 4. Embed in a PR comment
gh pr comment --body "![Screenshot](https://i.img402.dev/aBcDeFgHiJ.png)"
```

## Example

**User**: "Take a screenshot of the app and add it to the PR"

**Output**:

```
Captured screenshot to /tmp/screenshot.png (340KB)
Uploaded to https://i.img402.dev/aBcDeFgHiJ.png
Added screenshot to PR #47 as a comment.
```

## Tips

- Prefer PNG for UI screenshots (sharp text). Use JPEG for photos.
- If a screenshot is too large, resize with `sips -Z 1600` before uploading.
- Use `gh pr edit --body` to add to the PR description, or `gh pr comment` for a comment.
- Images persist for 7 days — plenty for PR reviews.

**Inspired by:** [github.com/cli/cli#1895](https://github.com/cli/cli/issues/1895) — long-standing request for image uploads in the GitHub CLI

## Related Use Cases

- Documenting UI changes in pull requests
- Adding architecture diagrams to issues
- Sharing test results as screenshots in CI comments
- Embedding charts and visualizations in GitHub discussions
