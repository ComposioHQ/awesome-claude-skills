---
name: design-auditor
description: Audit and check designs against 17 professional design rules. Use when reviewing Figma files, HTML/CSS/React/Vue code, screenshots, or design descriptions for issues with typography, contrast, spacing, accessibility, iconography, navigation, tokens, and more.
---

# Design Auditor

A skill for auditing designs against 17 professional design rules. Gives scored, actionable feedback with plain-language explanations — built for developers who don't have a design background and designers who want a fast second opinion.

## When to Use This Skill

- Reviewing a Figma file, screenshot, or UI code for design issues
- Checking accessibility and WCAG contrast compliance
- Auditing a design system for token health
- Getting feedback before shipping a UI to production
- Learning why a design feels "off" without knowing the specific rule

## What This Skill Does

1. **Scores the design out of 100**: Deterministic formula — Critical issues (-8pts), Warnings (-4pts), Tips (-1pt)
2. **Audits across 17 categories**: Typography, color, spacing, hierarchy, consistency, accessibility, forms, motion, dark mode, responsive, states, microcopy, i18n, corner radius, elevation, iconography, navigation, design tokens
3. **Explains every issue**: Plain-language reasoning for why each rule matters, not just what is wrong
4. **Declares audit confidence**: High (Figma MCP or code), Medium (screenshot), Low (description only)
5. **Offers to fix directly**: Applies fixes in code or Figma after the audit

## How to Use

### Basic Usage

Share a Figma link, paste HTML/CSS/React/Vue code, or upload a screenshot:

```
"Check my design"
"Review my UI for accessibility issues"
"Audit this component for spacing and contrast"
"Does this follow WCAG?"
```

### Korean Usage

The skill detects Korean input and responds entirely in Korean:

```
"디자인 검토해줘"
"접근성 확인해줘"
"UI 검토해줘"
```

### Figma MCP

When Figma is connected via MCP, share a Figma URL directly. The skill pulls full layer data, typography, colors, and spacing — then runs the audit and offers to apply fixes in Figma.

## Tips

- Share code or a Figma link for the highest confidence audit — screenshots limit what can be verified
- Ask for a focused audit (e.g. "just check accessibility") to get faster, targeted feedback
- After the audit, ask Claude to fix specific issues directly in the code
- Use the token health score to assess design system maturity in larger codebases

## Common Use Cases

- Developer building a UI who wants to catch issues before design review
- Designer running a quick WCAG check before handoff
- Team auditing a new component library for consistency
- Learning what design rules apply to a specific UI pattern
