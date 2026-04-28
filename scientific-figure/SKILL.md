---
name: scientific-figure
description: Generate polished scientific illustrations (method overviews, conceptual diagrams, barrel/iceberg metaphors) for academic papers via OpenAI-images-compatible endpoints. Not for matplotlib data charts.
---

# Scientific Figure

Generates AI-rendered scientific figures for academic papers. Wraps an OpenAI-images-compatible endpoint and persists every iteration's prompt, request body, response, and decoded PNG for reproducibility.

## When to Use This Skill

- User asks for a "method overview figure", "teaser figure", "conceptual diagram", "barrel diagram", or any single-panel scientific illustration for a paper.
- User wants to iterate on an existing figure (e.g., "make the right plank shorter", "add labels X, Y").
- User explicitly asks for AI-rendered / diffusion-based figure generation.

**Do NOT use** for:
- matplotlib / seaborn / plotly data charts
- TikZ / PGF / ASCII diagrams

## What This Skill Does

1. **Structured prompt drafting**: Uses a template with abstract, methodology, critical structural rules, labels, style, and composition sections.
2. **Image generation**: Calls an OpenAI-images-compatible endpoint (default: `gpt-image-2`).
3. **Audit trail**: Saves timestamped prompt, request payload, response, and PNG to `reports/scientific_illustrations/`.
4. **Iteration support**: Supports diff-based prompt refinement across versions.

## How to Use

### Setup

```bash
# Install the skill
mkdir -p ~/.claude/skills/scientific-figure
git clone https://github.com/Dominic789654/scientific-figure.git
cp scientific-figure/skills/scientific-figure/* ~/.claude/skills/scientific-figure/

# Set API key
export IMAGE_API_KEY="your-api-key"
```

### Basic Usage

```
Generate a method overview figure for my paper on token economics. 
The key idea is a wooden barrel where each stave represents a different 
compute constraint (memory bandwidth, peak FLOPS, chip area).
```

### Advanced Usage

```
Render a cannikin's-law barrel diagram. 
CRITICAL STRUCTURAL RULE: The barrel has EXACTLY THREE VISIBLE STAVES. 
Left stave (blue): "Memory BW" mid-height. 
Middle stave (green): "Peak FLOPS" tallest. 
Right stave (red): "Chip Area" shortest. 
Water fills to the top of the shortest stave.
```

## Example

**User**: "Generate a figure showing the three token production bottlenecks as a barrel diagram"

**Output**: A publication-ready PNG saved to `reports/scientific_illustrations/` with matching prompt, request, and response files for reproducibility.

## Tips

- Put constraints as prohibitions, not aspirations. "NO third wooden plank" works; "clean minimal barrel" does not.
- Restate violated rules in ALL CAPS on retry for better compliance.
- Put label text in double quotes to reduce paraphrasing.
- One novelty per figure — multiple ideas collapse into generic flow diagrams.
- Increment version slugs (`v1`, `v2`, `v3`) for each iteration to keep the audit trail clean.

## Environment Variables

| Variable | Default | Meaning |
|---|---|---|
| `IMAGE_API_KEY` | — (required) | Bearer token for the image endpoint |
| `IMAGE_API_HOST` | `vip.yi-zhan.top` | Host (no scheme) |
| `IMAGE_API_PATH` | `/v1/images/generations` | Path |
| `IMAGE_API_MODEL` | `gpt-image-2` | Model |
| `IMAGE_API_SIZE` | `1824x1024` | Canvas size |

**Install from:** [github.com/Dominic789654/scientific-figure](https://github.com/Dominic789654/scientific-figure)
