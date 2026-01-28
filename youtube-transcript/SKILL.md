---
name: youtube-transcript
description: Use when user provides a YouTube URL and wants transcript, subtitles, captions, or to create notes from video content. Use when user says "transcribe", "get transcript", "fetch subtitles", or wants to process YouTube video text.
---

# YouTube Transcript

Fetch transcripts from YouTube videos without API keys.

## When to Use

- User provides YouTube URL and wants transcript
- User wants to create notes from a video
- User needs video content as text for analysis
- Keywords: "transcribe", "transcript", "subtitles", "captions"

## Quick Reference

| Task | Command |
|------|---------|
| Fetch transcript | `python fetch.py <URL_OR_ID>` |
| Specific language | `python fetch.py <URL> --lang en` |
| List languages | `python fetch.py <URL> --list` |

## Usage

```bash
# From URL
python fetch.py "https://www.youtube.com/watch?v=VIDEO_ID"

# From video ID only
python fetch.py VIDEO_ID

# Specify language (prioritizes en, falls back to others)
python fetch.py VIDEO_ID --lang de

# List available transcript languages
python fetch.py VIDEO_ID --list
```

## Output Format

Plain text with timestamps stripped. Ready for note-taking or analysis.

## Common Issues

| Issue | Solution |
|-------|----------|
| "Transcripts disabled" | Video owner disabled captions |
| "No transcript found" | Try `--list` to see available languages |
| IP blocked (cloud/VPN) | Run from local machine, not server |

## Workflow

1. User provides YouTube URL
2. Run fetch script to get transcript
3. Process transcript text as needed (summarize, create notes, etc.)

## Prerequisites

Install the required Python library:

```bash
pip install youtube-transcript-api
```
