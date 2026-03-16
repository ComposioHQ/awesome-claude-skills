---
name: ad-ready
description: Generate professional advertising images from product URLs using a multi-phase AI pipeline. Provide a product URL, and the skill handles product scraping, brand analysis, creative direction, and image generation. Supports 70+ brand profiles, funnel stage targeting, and multi-format output for Meta, Google, TikTok, and more.
---

# Ad-Ready — AI Ad Creative Generator

Generate professional advertising images from product URLs using a multi-phase AI pipeline. Give it a product page, and it handles everything: scraping product details, analyzing the brand, directing the creative, and generating publication-ready ad images.

## When to Use This Skill

- Generate ad creatives from any product URL
- Create platform-specific ads (Meta, Google, TikTok, Instagram Stories)
- Produce brand-consistent visuals without a designer
- A/B test different creative directions quickly
- Scale ad production for multiple products or campaigns

## What This Skill Does

1. **Product Scraping**: Extracts product name, description, price, and hero image from any URL
2. **Brand Analysis**: Identifies or generates a brand profile (colors, tone, visual style) from 70+ pre-built profiles
3. **Creative Direction**: Selects layout, typography, and composition based on campaign objective and funnel stage
4. **Image Generation**: Produces publication-ready ad images via AI image generation APIs
5. **Multi-Format Output**: Generates for different aspect ratios (4:5 for Meta, 9:16 for Stories, 1:1 for Google, etc.)

## How to Use

### Basic Usage

```
Create an ad for https://example.com/product-page
```

### Advanced Usage

```
Generate 3 ad variations for https://example.com/product using the Nike brand profile. Target top-of-funnel awareness. Output in 9:16 for Instagram Stories and 4:5 for Meta feed. Use a dark cinematic style with bold typography.
```

### Workflow

```
1. Provide: product URL + brand name + campaign objective
2. Skill scrapes product details and downloads hero image
3. Brand profile loaded (or generated via brand analyzer)
4. Creative direction selected based on funnel stage
5. AI generates the ad image(s)
6. Output delivered in requested format(s)
```

### Supported Aspect Ratios

- **4:5** — Meta/Instagram feed (default)
- **9:16** — Instagram/TikTok Stories
- **1:1** — Google Display, social posts
- **16:9** — YouTube thumbnails, landscape ads
- **1.91:1** — Google Display Network

### Funnel Stage Profiles

- **Awareness** — Bold visuals, brand storytelling, aspirational imagery
- **Consideration** — Feature highlights, social proof, comparison angles
- **Conversion** — Price emphasis, urgency, clear CTA, trust signals
- **Retention** — Loyalty messaging, upsell visuals, community feel

## Example

**User**: "Make an ad for https://allbirds.com/products/wool-runners"

**Output**:

```
🎨 Ad-Ready — Creative Generated
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📦 Product: Allbirds Wool Runners ($110)
🏷️ Brand: Allbirds (eco-minimal profile loaded)
🎯 Funnel: Consideration
📐 Format: 4:5 (Meta feed)

🖼️ Creative Direction:
- Clean white background with natural textures
- Product hero shot with subtle shadow
- "Comfort that doesn't cost the earth" headline
- Muted earth-tone palette matching brand guidelines
- Price badge with sustainability callout

✅ Image generated → saved to ./output/allbirds-wool-runners-4x5.png
```

**Inspired by:** [Cybrflux AI Marketing](https://cybrflux.online) — built for automated ad creative production at scale.

## Tips

- Always provide a reference image when possible — it dramatically improves output quality
- Use brand profiles for consistency across campaigns (don't generate "generic" ads)
- Generate 3-5 variations and A/B test — the first creative is rarely the best performer
- Match aspect ratio to platform: 4:5 for Meta feed, 9:16 for Stories/Reels/TikTok
- Rotate between 5 layout styles to avoid ad fatigue: dark cinematic, bright editorial, center card, split layout, text-heavy

## Common Use Cases

- E-commerce product ad generation at scale
- Agency creative production (multiple clients, fast turnaround)
- A/B test creative variations without a designer
- Social media ad campaigns across platforms
- Dropshipping product marketing
