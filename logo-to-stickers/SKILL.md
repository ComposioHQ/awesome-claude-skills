---
name: logo-to-stickers
license: MIT
description: "Turn a logo, brand mark, or existing IP into a consistent set of playful die-cut paper stickers. Use for brand character extensions, logo personification, website sticker assets, or sticker variations that need actual transparent images; not for redesigning the logo itself."
---

# Logo to Stickers

Give a brand a small cast, a useful ability, and something slightly surprising to do. Keep the recognisable brand DNA. Let paper texture and a thin die-cut white edge make the illustration feel like a physical sticker.

## Start with the actual brand

Inspect the supplied logo or the real project assets before inventing a character. The user's latest visual feedback takes priority over an older brief. Identify three anchors: a recognisable silhouette or component count; a restrained colour relationship; a characteristic product verb, such as researching, publishing, or animating.

Choose a translation that fits:

- **Shape → cast.** Let the actual logo fragments become bodies. A few eyes and ink-line limbs may be enough. Keep their distinct silhouettes and let their relationships create the scene.
- **Meaning → ability.** Turn a product behaviour into a character's useful, occasionally troublesome ability. Keep the original palette, a local shape, or a small brand mark. Explain why the metaphor fits; do not give every brand the same animal.
- **Existing character → action.** Preserve the identity that is already there. Change what the character does without automatically redesigning it.

Read [the worked examples](https://github.com/huyanxius/logo-to-stickers/blob/main/references/design-method.md), then inspect the original mark and a relevant finished sticker. Borrow a technique, not another brand's identity. A character newly invented for this task is a proposed extension, not an already-official mascot.

## Give each sticker a tiny plot

Write one sentence per image: **who does what → a small unexpected consequence → a readable reaction**. Let the brand's ability participate in the joke. Awkward collaboration, disproportionate tools, a gentle accident, or a well-earned nap are useful possibilities, not a fixed scene checklist.

Prefer one principal action and one principal prop. Use posture, balance, gaze, and scale to convey personality. Keep a compact overall silhouette that remains readable around 160–240 px. A character standing with a different prop in every image rarely makes an interesting set.

## Generate a consistent set

Use an available image-generation tool that supports image references and real transparent output. In Codex, use the built-in image-generation tool and the environment's `imagegen` guidance. In other agents, use their configured image-generation capability. This skill does not provide a model, API key, or image-generation service. If no suitable generator is available, explain the missing capability and provide the prepared prompts without claiming that images were produced.

Generate and inspect one scene first, then use it as the identity anchor for the rest. When the user asked for a full set, continue after your own inspection; do not add an approval checkpoint unless requested.

Assign each reference an explicit role and match the prompt's image numbers to the actual upload order:

- Original logo / IP: recognisable brand structure.
- First sticker of the current series: face, proportions, palette, line quality, print texture.
- Optional external style reference: the specific paper finish or drawing technique to borrow.

Keep **who the character is** consistent while changing **what it is doing**. A giant eye behind a magnifying glass is a temporary lens joke, not a permanent character feature. The first scene's props need not appear in every subsequent scene. See [the prompt recipe](https://github.com/huyanxius/logo-to-stickers/blob/main/references/prompt-template.md).

## Make the paper convincing

Use matte printed illustration, subtle paper grain, and a narrow continuous white die-cut border around the whole scene. Start around 1–2% of canvas width and adjust to the detail. Keep the sheet front-facing and flat, with only a little cut-edge thickness. Avoid swollen rubber, glossy CGI, or converting everything into a toy product photo.

Centre the complete scene with usable margins. Ask for true alpha outside the sticker, not a rectangular card, scenery, tabletop, or a drawn checkerboard. Omit captions and watermarks unless the user requests text. Small emotion strokes can support an action.

## Inspect and deliver

Inspect each actual result and the set together. Check brand recognition, an understandable situation, stable character identity, different poses and silhouettes, and an intact white border. Simplify unreadable scenes. Regenerate individual failures without discarding the successful character design.

Verify the saved image's actual dimensions and alpha. A requested size in a prompt is not proof of output size. Use only mechanical padding or resizing when needed for delivery, preserving originals; make visual changes through the image tool.

Save each requested sticker as its own file in the user's destination. Use descriptive versioned names rather than overwriting a prior batch by default. Deliver clickable paths, a contact sheet when helpful, the actual prompt set, and the generation mode used. For an image request, a sheet or a list of prompts alone is not the requested set of independent images.

## Source and worked outputs

Based on [huyanxius/logo-to-stickers](https://github.com/huyanxius/logo-to-stickers), developed from a real portfolio sticker session with Qunxue, MultiPush and Windup. The public repository includes fifteen actual outputs, original marks, a live gallery and the generation records. Tested with Codex’s built-in image tool; other hosts need their own reference-capable image generator.
