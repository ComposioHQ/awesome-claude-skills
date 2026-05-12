---
name: finnish-humanizer
description: Detects and removes AI-generated markers from Finnish text, making it sound natural and human-written.
---

# Finnish Humanizer

Detects and removes AI-generated markers from Finnish text, making it sound natural and human-written. Identifies 26 patterns (12 Finnish-specific + 14 universal) and 4 style markers that make AI text recognizable, then rewrites the text to sound like a native Finnish speaker wrote it.

## When to Use This Skill

- You've generated Finnish content with AI and it sounds robotic or unnatural
- You need AI-written Finnish marketing copy, documentation, or communications to pass as human-written
- You want to learn what makes AI-generated Finnish text recognizable

## What This Skill Does

1. **Pattern Detection**: Identifies 26 AI patterns in Finnish text — passive overuse, missing particles, translation structures, excessive hedging, flattery, filler phrases, and more
2. **Natural Rewriting**: Replaces detected patterns with natural Finnish constructions while preserving meaning
3. **Register Preservation**: Keeps formal text formal and casual text casual — only removes AI markers
4. **Adaptive Workflow**: Short texts (<500 words) are processed directly; longer texts get an analysis phase first

## How to Use

### Basic Usage

```
Humanize this Finnish text:

Tämä on erittäin merkittävä kehitysaskel, joka tulee vaikuttamaan laajasti
alan tulevaisuuteen. On syytä huomata, että kyseinen innovaatio tarjoaa
lukuisia mahdollisuuksia eri sidosryhmille.
```

### Advanced Usage

```
Humanize this Finnish text. Keep the formal register but remove AI patterns:

[your text here]
```

## Example

**Input**:
> Tämä on erittäin merkittävä kehitysaskel, joka tulee vaikuttamaan laajasti alan tulevaisuuteen. On syytä huomata, että kyseinen innovaatio tarjoaa lukuisia mahdollisuuksia eri sidosryhmille.

**Output**:
> Iso juttu alalle. Tästä hyötyvät monet.

**Changes made**: Removed significance inflation (#13), filler phrases (#17), bureaucratic language (#10), and pronoun overuse (#3).

## Tips

- Provide context about your target audience (professional, casual, marketing, technical) for better results
- For long texts, the skill will ask about ambiguous cases before rewriting
- The skill preserves code examples, technical terms, and English passages unchanged
- If text is already natural, the skill will tell you instead of making unnecessary changes

## Common Use Cases

- Marketing copy and blog posts for Finnish audiences
- AI-generated documentation that needs to sound human
- Email communications and internal memos
- Website content and product descriptions
- Academic or journalistic text cleanup

## Limitations

- Works only with Finnish text (mixed fi/en text: only Finnish parts are processed)
- Does not change factual content — only presentation
- Does not simplify — formal text stays formal
- Does not replace human editing — removes AI markers, doesn't make text "good"

## Platform Compatibility

- ✅ Claude Code
- ✅ Claude.ai
- ✅ Claude API
- ✅ Cursor (via .mdc rules)
- ✅ GitHub Copilot (via .instructions.md)

**Created by:** [@Hakku](https://github.com/Hakku) — [Repository](https://github.com/Hakku/finnish-humanizer)
