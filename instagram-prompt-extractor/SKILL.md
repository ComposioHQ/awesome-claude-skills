---
name: instagram-prompt-extractor
description: Extract the AI prompt or creative brief behind an Instagram post — reverse-engineer what prompt or concept was used to create AI-generated images, designs, or content. Use this skill when the user shares an Instagram post (image or caption) and wants to know the likely prompt or creative direction behind it.
---

# Instagram Prompt Extractor

Reverse-engineer the AI prompt or creative brief behind Instagram content.

## When to Use

Use when the user:
- Shares an Instagram image or post and asks "what prompt was used for this?"
- Wants to recreate a visual style they saw on Instagram
- Asks "how would I recreate this?" for AI-generated content
- Wants to understand the creative direction behind a post

## Process

### Step 1: Analyze the Visual Content

When an image is provided, analyze:

**Subject & Composition:**
- Main subject (person, object, scene, abstract)
- Composition style (rule of thirds, centered, symmetrical, dynamic)
- Foreground/background relationship
- Camera angle (eye-level, aerial, low-angle, POV)

**Lighting & Mood:**
- Lighting type (natural, studio, golden hour, neon, moody)
- Shadows and highlights
- Overall mood (dramatic, soft, cheerful, mysterious)

**Style & Aesthetic:**
- Photography style vs AI-generated vs illustration
- Art style if applicable (hyperrealistic, cinematic, anime, oil painting, etc.)
- Color grading (warm, cool, desaturated, high contrast, pastel)
- Post-processing style (film grain, vignette, sharp, soft focus)

**Technical Details:**
- Apparent camera/lens (wide angle, telephoto, macro, fisheye)
- Depth of field (shallow bokeh vs everything in focus)
- Resolution/clarity impression

### Step 2: Analyze the Caption (if provided)

Extract from caption:
- Key themes and concepts
- Brand voice and tone
- Hashtags as topic signals
- Product or service context
- Target audience cues

### Step 3: Construct the Likely Prompt

Build the reverse-engineered prompt in layers:

**For AI Image Generation (Midjourney, DALL-E, Stable Diffusion):**
```
[Subject description], [style/aesthetic], [lighting], [mood], [technical specs], [quality modifiers]
```

Example:
```
A young woman in a flowing white dress standing in a field of sunflowers at golden hour,
cinematic photography, warm soft lighting, bokeh background, shot on Canon 5D,
8k resolution, hyperrealistic, editorial style
```

**For Midjourney specifically:**
```
/imagine [subject] [style] [mood] [lighting] --ar 4:5 --style raw --v 6
```

**For content/caption prompts:**
```
Write an Instagram caption for [subject] with [tone] voice targeting [audience].
Include relevant hashtags for [niche]. Keep it [length].
```

### Step 4: Provide Recreation Instructions

Give the user:
1. **Extracted prompt** — ready to copy-paste into an AI image tool
2. **Style parameters** — specific settings for the tool (aspect ratio, style version)
3. **Key elements** — the most important visual elements to preserve
4. **Variations to try** — tweaks that might improve results

## Output Format

```
## Prompt Analysis: [Post description]

### Likely AI Tool
[Midjourney / DALL-E / Stable Diffusion / Not AI-generated / Unclear]

### Reverse-Engineered Prompt

**Ready to use:**
```
[Full prompt ready to copy-paste]
```

**For Midjourney:**
```
/imagine [prompt] --ar 4:5 --v 6
```

### Key Visual Elements
- **Subject**: [description]
- **Style**: [aesthetic description]
- **Lighting**: [lighting description]
- **Color**: [color grading]
- **Mood**: [emotional quality]

### Recreation Tips
1. [Specific tip for getting the same result]
2. [Another tip]
3. [Variation to try]

### Caption Prompt (if applicable)
```
[Prompt to generate a similar caption]
```
```

## Visual Style Vocabulary

Use these terms when constructing prompts:

**Photography styles:** editorial, documentary, fine art, street photography, fashion photography, product photography, portrait, landscape, macro

**Lighting:** golden hour, blue hour, studio lighting, rembrandt lighting, dramatic side lighting, flat lay, backlit, neon, cinematic

**Moods:** ethereal, moody, dark academia, cottagecore, minimalist, maximalist, retro, futuristic, dreamy, raw

**Technical:** bokeh, shallow depth of field, wide angle, telephoto compression, film grain, 35mm, medium format, drone shot, fisheye

**AI art styles:** hyperrealistic, photorealistic, cinematic, oil painting, watercolor, digital art, concept art, anime, illustration, 3D render

## Notes

- Be clear when a post is likely NOT AI-generated (real photography)
- For real photography, describe it as a "creative brief" rather than an "AI prompt"
- Include both the image generation prompt AND the caption prompt if both are relevant
- If image is not provided, work from caption and hashtag analysis only
