---
name: figma-design-system-rules
description: Extract, document, and enforce design system rules from a Figma design system. Use this skill when the user wants to document their design system, create design tokens, establish component usage rules, or ensure code follows a Figma design system.
---

# Figma: Design System Rules

Extract and document design system rules from Figma for use in code implementation.

## When to Use

Use when the user:
- Wants to document their Figma design system for developers
- Needs to create a design tokens file from Figma specs
- Wants rules for how components should be used
- Is setting up a new codebase to match an existing Figma design system

## Design System Components to Document

### 1. Color Tokens

Extract all color styles from Figma:

```ts
// design-tokens/colors.ts
export const colors = {
  // Brand
  primary: {
    50: '#EFF6FF',
    100: '#DBEAFE',
    500: '#3B82F6',
    600: '#2563EB',
    700: '#1D4ED8',
  },
  // Semantic
  text: {
    primary: '#111827',
    secondary: '#6B7280',
    disabled: '#D1D5DB',
  },
  background: {
    default: '#FFFFFF',
    subtle: '#F9FAFB',
    muted: '#F3F4F6',
  },
  status: {
    success: '#10B981',
    warning: '#F59E0B',
    error: '#EF4444',
    info: '#3B82F6',
  },
} as const;
```

### 2. Typography Tokens

```ts
export const typography = {
  fonts: {
    heading: '"Inter", system-ui, sans-serif',
    body: '"Inter", system-ui, sans-serif',
    mono: '"JetBrains Mono", monospace',
  },
  sizes: {
    xs: '0.75rem',    // 12px
    sm: '0.875rem',   // 14px
    base: '1rem',     // 16px
    lg: '1.125rem',   // 18px
    xl: '1.25rem',    // 20px
    '2xl': '1.5rem',  // 24px
    '3xl': '1.875rem',// 30px
    '4xl': '2.25rem', // 36px
  },
  weights: {
    normal: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
  },
  lineHeights: {
    tight: 1.25,
    normal: 1.5,
    relaxed: 1.75,
  },
} as const;
```

### 3. Spacing Scale

```ts
export const spacing = {
  0: '0',
  1: '4px',
  2: '8px',
  3: '12px',
  4: '16px',
  5: '20px',
  6: '24px',
  8: '32px',
  10: '40px',
  12: '48px',
  16: '64px',
  20: '80px',
  24: '96px',
} as const;
```

### 4. Border Radius

```ts
export const radius = {
  none: '0',
  sm: '4px',
  md: '8px',
  lg: '12px',
  xl: '16px',
  '2xl': '24px',
  full: '9999px',
} as const;
```

### 5. Shadows

```ts
export const shadows = {
  sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
  md: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
  lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
  xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1)',
} as const;
```

### 6. Breakpoints

```ts
export const breakpoints = {
  sm: '640px',
  md: '768px',
  lg: '1024px',
  xl: '1280px',
  '2xl': '1536px',
} as const;
```

## Component Usage Rules

For each component in the design system, document:

### Component Rule Template
```md
## [ComponentName]

**Usage:** When to use this component
**Don't use when:** When NOT to use this component

### Variants
- `default` — Standard usage
- `primary` — Main CTA
- `destructive` — Dangerous actions

### Sizes
- `sm` — Compact layouts
- `md` — Default
- `lg` — Hero sections

### States
- `default`, `hover`, `focus`, `disabled`, `loading`

### Dos and Don'ts
✅ Do: [correct usage]
❌ Don't: [incorrect usage]
```

## CSS Custom Properties Export

For use in CSS/Tailwind projects:
```css
:root {
  /* Colors */
  --color-primary: #2563EB;
  --color-primary-light: #DBEAFE;
  --color-text: #111827;
  --color-text-muted: #6B7280;
  --color-bg: #FFFFFF;
  --color-bg-subtle: #F9FAFB;

  /* Typography */
  --font-sans: 'Inter', system-ui, sans-serif;
  --text-sm: 0.875rem;
  --text-base: 1rem;
  --text-lg: 1.125rem;

  /* Spacing */
  --space-4: 1rem;
  --space-8: 2rem;

  /* Radius */
  --radius-md: 0.5rem;
  --radius-lg: 0.75rem;

  /* Shadows */
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}
```

## Notes

- Ask the user to share Figma design system pages, color styles, and text styles
- Create tokens as a single source of truth — import everywhere
- Document rules that are NOT obvious from the tokens (e.g., "never use red for non-error states")
- For Tailwind projects, translate tokens into `tailwind.config.js` theme extensions
