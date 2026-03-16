---
name: cybrscan
description: AI-powered website inspector that opens any URL in a real browser, captures full-page screenshots, and analyzes design, UX, performance, and technical issues using vision models. Use when you need to visually audit a website, QA a build, or generate a professional site review.
---

# CybrScan — AI Website Inspector

Scan any website visually and technically using Playwright and AI vision models. Opens real browser sessions, captures full-page screenshots, and sends them to a vision model for comprehensive analysis.

## When to Use This Skill

- Review a website's design, UX, or conversion quality
- Visual QA on a site you're building (before/after deploy)
- Compare mobile vs desktop views
- Generate a professional site audit for clients
- Debug visual issues or layout problems
- Screenshot and analyze competitor websites

## What This Skill Does

1. **Browser Rendering**: Opens the URL in a real Chromium browser via Playwright (not just fetching HTML)
2. **Full-Page Screenshots**: Captures the entire page, not just the viewport
3. **AI Vision Analysis**: Sends screenshots to a vision model (Gemini, GPT-4o, etc.) for design/UX/technical analysis
4. **Mobile Support**: Can emulate mobile viewports for responsive testing
5. **Report Generation**: Saves analysis reports and screenshots to disk

## How to Use

### Prerequisites

```bash
pip install playwright
playwright install chromium
```

You'll also need an OpenRouter API key (or adapt for any OpenAI-compatible vision API).

### Basic Usage

```
Scan https://example.com and tell me what needs improvement.
```

### Advanced Usage

```
Scan https://example.com on both desktop and mobile. Save the report. Focus on conversion optimization and accessibility issues.
```

### CLI Reference

```bash
# Basic scan (uses Gemini Flash by default — ~$0.003/scan)
python3 cybrscan.py https://example.com

# Save report + screenshots
python3 cybrscan.py https://example.com --save ./reports/example

# Mobile viewport
python3 cybrscan.py https://example.com --mobile

# Use a different model
python3 cybrscan.py https://example.com --model google/gemini-2.5-pro

# Custom viewport size
python3 cybrscan.py https://example.com --width 1440 --height 900
```

## Example

**User**: "Scan https://stripe.com and rate the landing page"

**Output**:

```
🔍 CybrScan Report — stripe.com
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Overall Score: 92/100

✅ Strengths:
- Clean, focused hero with clear value proposition
- Excellent use of whitespace and visual hierarchy
- Smooth animations that enhance without distracting
- Mobile-responsive layout renders perfectly
- Fast perceived load time with optimized assets

⚠️ Improvements:
- Secondary CTA could have more visual contrast
- Footer link density is high — consider grouping
- Some decorative images lack alt text

🎯 Conversion Analysis:
- Primary CTA is prominent and action-oriented
- Trust signals (logos, security badges) well-placed
- Pricing page link could be more discoverable
```

**Inspired by:** [Cybrflux AI Marketing](https://cybrflux.online) — built for automated client website audits.

## Tips

- Run both desktop AND mobile scans for a complete picture
- Use cheaper models (Gemini Flash) for routine QA, premium models (GPT-4o, Gemini Pro) for client-facing reports
- Save reports to track changes over time (before/after redesigns)
- Combine with SEO auditing for a comprehensive site review

## Common Use Cases

- Pre-launch QA for new websites
- Client website audits (sell as a service)
- Competitor analysis and benchmarking
- Accessibility and UX reviews
- Design system compliance checks
