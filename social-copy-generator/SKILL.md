---
name: social-copy-generator
description: Generate platform-optimized social media copy for product launches. One input, six platform outputs (Twitter/X, Jike, Xiaohongshu, WeChat Moments, Video Account, LinkedIn). Auto-generates an HTML page with one-click copy buttons.
---

# Social Copy Generator

Generate social media copy for multiple platforms from a single product description. Output as an HTML page with one-click copy buttons.

## When to Use This Skill

- Launching an open source project and need social media posts
- Promoting a product across multiple platforms at once
- Need platform-specific marketing copy (Twitter vs Xiaohongshu vs WeChat)
- Want copy-paste-ready text without terminal whitespace issues

## What This Skill Does

1. **Multi-Platform Copy**: Generate optimized copy for 6 platforms in one go
2. **Platform Rules**: Respect each platform's character limits, style, and conventions
3. **HTML Output**: Create a styled webpage with copy buttons — no whitespace issues
4. **Bilingual**: Support Chinese and English content
5. **One-Click Copy**: Each platform card has a copy button using clipboard API

## Supported Platforms

| Platform | Style | Limits |
|----------|-------|--------|
| Twitter/X | Concise, technical, hashtags | 280 chars |
| Jike | Developer community, dry content | No limit |
| Xiaohongshu | Casual, emoji-rich, comparison data | No limit |
| WeChat Moments | Personal, conversational | No limit |
| Video Account | Title + description | Title < 30 chars |
| LinkedIn | Professional, achievement-focused | No limit |

## How to Use

```
Generate social media posts for my new project
Write copy to promote this tool on all platforms
帮我写社交媒体推广文案
```

## Install

```
npx skills add dongsheng123132/social-copy-generator
clawhub install social-copy-generator
```
