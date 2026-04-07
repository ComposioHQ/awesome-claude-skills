---
name: polanyi-design
description: Frontend design cognitive engine that surfaces expert-level visual judgment for UI design, layout, and aesthetic decisions.
---

# Polanyi Design

A frontend design cognitive engine grounded in Michael Polanyi's tacit knowledge theory. It surfaces the visual judgment that senior designers *know* but rarely articulate — operating at the implicit/tacit knowledge boundary where documentation ends and judgment begins.

## When to Use This Skill

- UI design, layout, visual hierarchy, or "why does this look off" questions
- Design system work, component API design, responsive strategy
- Color, typography, and spacing decisions requiring aesthetic judgment
- Design review or diagnosis beyond rule-following

## What This Skill Does

1. **Knowledge Filter**: Skips what tutorials teach, extracts what senior designers know but haven't written down, and approximates embodied design intuition
2. **Five Design Lenses**: Gestalt diagnostics, subsidiary-focal awareness, token hierarchy, tacit translation (feeling → fix), and convention judgment (when to break rules)
3. **Aesthetic Judgment Encoding**: Six patterns that prevent AI from converging on generic defaults — negation over assertion, polarization over compromise, anti-convergence

## How to Use

### Basic Usage

```
/polanyi-design 设计一个登录页面
```

### Advanced Usage

```
/polanyi-design Review this dashboard layout — something feels off but I can't name it
```

The skill also auto-activates on design-related keywords: "design", "layout", "UI", "looks like a template", "feels off", etc.

## Example

**User**: "Why does this landing page feel like a template?"

**Output**: Gestalt diagnosis identifying that every decision is the statistical mode of its category (Inter + blue-500 + rounded-lg), followed by 2-3 structural fixes with exact values that create a distinctive visual identity.

## Tips

- Works best when you describe what *feels* wrong rather than what *is* wrong — the skill translates tacit reactions into structural fixes
- Pair with the official `frontend-design` skill for maximum effect — they complement each other
- The skill calibrates depth to the asker: beginners get explicit guidance with implicit reasoning, experts get post-critical engagement

## Common Use Cases

- Diagnosing why a design "feels off" or "looks like a template"
- Making deliberate anti-template decisions (font pairing, color relationships, layout breaks)
- Design system review with tacit knowledge articulation
- Translating expert design intuition into concrete specs with values

**Credit:** Based on [Michael Polanyi](https://en.wikipedia.org/wiki/Michael_Polanyi)'s tacit knowledge framework (*Personal Knowledge*, 1958; *The Tacit Dimension*, 1966), with insights from Harry Collins's tacit knowledge taxonomy and the Dreyfus skill acquisition model.
