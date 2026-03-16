---
name: seo-auditor
description: Comprehensive SEO audit tool that analyzes any website and generates a scored, client-ready report with actionable recommendations. Use when you need to check a site's SEO health, prepare for a sales call, or deliver SEO reports as a service.
---

# SEO Auditor

Perform comprehensive SEO audits on any website and generate professional, scored reports with actionable recommendations.

## When to Use This Skill

- Analyze a website's SEO health before a sales call
- Generate SEO audit reports as a paid service
- Quick competitive analysis of competitor websites
- Validate your own site's technical SEO
- Identify quick-win improvements for any URL

## What This Skill Does

1. **Technical SEO Analysis**: Title tags, meta descriptions, canonical URLs, SSL, schema markup
2. **On-Page SEO**: Heading hierarchy, image alt tags, keyword usage, content structure
3. **Performance Signals**: Resource hints, script loading, mobile meta tags
4. **Social & Sharing**: Open Graph tags, Twitter cards, social optimization
5. **Scored Report**: Each category scored 0-100 with letter grades (A-F)

## How to Use

### Basic Usage

```
Run an SEO audit on https://example.com
```

### Advanced Usage

```
Run a full SEO audit on https://example.com. Compare against https://competitor.com. Focus on technical SEO and content structure. Generate a client-ready PDF report.
```

### CLI Reference

```bash
# Run audit
python3 audit.py https://example.com

# Output is a structured report with scores per category
```

### What Gets Analyzed

- **Title Tags** — Presence, length (50-60 chars), keyword optimization
- **Meta Descriptions** — Presence, length (150-160 chars), click-through optimization
- **Headings (H1-H6)** — Structure, hierarchy, keyword usage
- **Image Alt Tags** — Accessibility and SEO optimization
- **Page Speed Indicators** — Resource hints, script loading patterns
- **Mobile Meta Tags** — Viewport configuration, responsive signals
- **SSL/HTTPS** — Security certificate validation
- **Canonical URLs** — Duplicate content prevention
- **Open Graph Tags** — Social media optimization
- **Schema Markup** — Structured data presence and validity

## Example

**User**: "Audit https://shopify.com"

**Output**:

```
🔍 SEO Audit Report — shopify.com
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Overall Score: 88/100 (Grade: B+)

📋 Category Breakdown:
  ✅ Title Tag: 95/100 (A) — Optimized length, includes primary keyword
  ✅ Meta Description: 90/100 (A) — Compelling, within character limit
  ✅ Headings: 85/100 (B) — Good hierarchy, H1 present
  ⚠️ Image Alt Tags: 72/100 (C) — 15 of 42 images missing alt text
  ✅ SSL/HTTPS: 100/100 (A) — Valid certificate
  ✅ Schema Markup: 92/100 (A) — Organization + Product schemas found
  ⚠️ Page Speed: 78/100 (C) — 3 render-blocking scripts detected

🎯 Top 3 Quick Wins:
  1. Add alt text to 15 missing images (+8 points)
  2. Defer render-blocking scripts (+5 points)
  3. Add FAQ schema to pricing page (+3 points)
```

### Scoring System

| Grade | Score | Meaning |
|-------|-------|---------|
| A | 90-100 | Excellent — Industry leading |
| B | 80-89 | Good — Minor improvements needed |
| C | 70-79 | Average — Noticeable issues |
| D | 60-69 | Below Average — Significant issues |
| F | 0-59 | Poor — Critical issues requiring attention |

**Inspired by:** [Cybrflux AI Marketing](https://cybrflux.online) — built for automated client SEO audits and lead generation.

## Tips

- Run audits on competitor sites before sales calls — show prospects how they compare
- Combine with CybrScan (visual audit) for a comprehensive review
- Schedule periodic audits to track SEO improvements over time
- Export reports as Markdown or HTML for client delivery

## Common Use Cases

- Agency client onboarding (baseline audit)
- Lead generation (free audit → paid services)
- Monthly SEO health monitoring
- Competitive analysis and benchmarking
- Pre-launch technical SEO checklist
