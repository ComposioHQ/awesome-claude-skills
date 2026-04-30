---
name: figma-implement-design
description: Implement a Figma design as production-ready frontend code. Use this skill when the user shares a Figma design link or screenshot and wants it converted to HTML/CSS, React, or another frontend framework.
---

# Figma: Implement Design

Convert a Figma design into production-ready frontend code.

## When to Use

Use when the user:
- Shares a Figma link or screenshot and asks to "implement this"
- Says "build this design" / "code this mockup"
- Wants to convert a visual design to working code

## Process

### Step 1: Gather Design Information

The user must provide one of:
- **Figma URL**: `https://www.figma.com/design/...` or `https://www.figma.com/file/...`
- **Screenshot/image**: Visual of the design to implement
- **Figma Dev Mode export**: CSS properties, component specs

If only a URL is provided and no Figma MCP is configured, ask the user to:
1. Open Figma Dev Mode (Shift+D or bottom bar → Dev)
2. Share relevant CSS properties, spacing values, colors, and font specs
3. Export relevant assets (icons, images)

### Step 2: Extract Design Tokens

Before coding, identify and document:
- **Colors**: Background, text, border, accent colors (as hex/rgb)
- **Typography**: Font family, sizes, weights, line heights
- **Spacing**: Padding, margin, gap values
- **Border radius**: Corner radius values
- **Shadows**: Box shadow values
- **Breakpoints**: Responsive design specs if provided

Example CSS variables to set up:
```css
:root {
  --color-primary: #2563EB;
  --color-text: #1F2937;
  --color-bg: #F9FAFB;
  --font-heading: 'Inter', sans-serif;
  --radius-md: 8px;
  --spacing-md: 16px;
}
```

### Step 3: Identify Components

Break the design into reusable components:
- Identify repeated UI patterns
- Define component hierarchy (what contains what)
- Note interactive states: hover, active, focus, disabled

### Step 4: Implement

Implement using the stack the user specifies. Defaults:
- **No preference**: HTML + CSS (no framework)
- **React asked**: React with CSS modules or Tailwind
- **Vue asked**: Vue 3 SFCs
- **Tailwind available**: Use Tailwind utility classes

**Implementation priorities:**
1. Layout (flexbox/grid structure matches design)
2. Typography (font, size, weight, color)
3. Colors and backgrounds
4. Spacing (padding, margin, gaps)
5. Border radius and shadows
6. Hover/interactive states
7. Responsive behavior

### Step 5: Asset Handling

For images and icons:
- Use placeholder images if real assets aren't provided: `https://placehold.co/400x300`
- For icons: use Lucide React, Heroicons, or inline SVG
- Note which assets need to be replaced with real ones

## Code Quality Standards

- Semantic HTML (`<header>`, `<nav>`, `<main>`, `<section>`, `<button>`, not `<div>` for everything)
- Accessible (ARIA labels on interactive elements, alt text on images)
- Responsive (mobile-first or explicit breakpoints)
- Pixel-accurate where possible (spacing, sizing matching design)

## When Design is Partial or Unclear

If parts of the design are unclear:
- Make reasonable assumptions and note them
- Comment `/* TODO: Confirm with designer */` for uncertain parts
- Ask about critical ambiguities (interactions, responsive behavior)

## Notes

- Without Figma MCP integration, implement from screenshots or exported specs
- Always match the design's aesthetic intent, not just layout
- For complex designs, implement the most visible/important section first and iterate
- Use the `frontend-design` skill for creative freedom; use this skill when fidelity to a specific design is the goal
