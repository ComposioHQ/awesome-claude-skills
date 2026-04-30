---
name: figma-code-connect
description: Set up and manage Figma Code Connect — link Figma components to real code components so devs see actual code snippets in Figma Dev Mode. Use this skill when the user wants to connect their Figma design system to their React/other framework component library using Figma's Code Connect feature.
---

# Figma: Code Connect

Link Figma components to real code components using Figma Code Connect.

## What is Code Connect?

Figma Code Connect maps Figma design components to their code implementations. When developers inspect a component in Figma Dev Mode, they see real code snippets from the actual codebase instead of generated CSS.

## Prerequisites

- Figma account with Dev Mode access
- Node.js project with a component library
- Figma personal access token

## Installation

```bash
npm install --save-dev @figma/code-connect
# or
npx figma connect
```

## Setup

### 1. Authenticate

```bash
npx figma connect login
# Enter your Figma personal access token when prompted
# Token: https://www.figma.com/settings → Personal access tokens
```

Or set via environment variable:
```bash
export FIGMA_ACCESS_TOKEN=figd_...
```

### 2. Initialize

```bash
npx figma connect create
```

This creates a `figma.config.json`:
```json
{
  "codeConnect": {
    "include": ["src/**/*.figma.tsx"],
    "exclude": ["node_modules/**"]
  }
}
```

## Creating Code Connect Files

For each Figma component, create a `.figma.tsx` (or `.figma.ts`) file:

### Basic Example — Button

```tsx
// src/components/Button/Button.figma.tsx
import figma from '@figma/code-connect'
import { Button } from './Button'

figma.connect(Button, 'https://www.figma.com/design/FILE_ID/DESIGN_NAME?node-id=COMPONENT_NODE_ID', {
  props: {
    variant: figma.enum('Variant', {
      Default: 'default',
      Primary: 'primary',
      Destructive: 'destructive',
    }),
    size: figma.enum('Size', {
      Small: 'sm',
      Medium: 'md',
      Large: 'lg',
    }),
    disabled: figma.boolean('Disabled'),
    label: figma.string('Label'),
  },
  example: ({ variant, size, disabled, label }) => (
    <Button variant={variant} size={size} disabled={disabled}>
      {label}
    </Button>
  ),
})
```

### Input Component Example

```tsx
import figma from '@figma/code-connect'
import { Input } from './Input'

figma.connect(Input, 'FIGMA_URL?node-id=NODE_ID', {
  props: {
    placeholder: figma.string('Placeholder'),
    disabled: figma.boolean('Disabled'),
    error: figma.boolean('Error'),
  },
  example: ({ placeholder, disabled, error }) => (
    <Input
      placeholder={placeholder}
      disabled={disabled}
      className={error ? 'input-error' : ''}
    />
  ),
})
```

## Figma URL Format

Get the component URL from Figma:
1. Open Figma file
2. Right-click the component in the canvas
3. "Copy link to selection"
4. URL format: `https://www.figma.com/design/FILE_ID/NAME?node-id=X-Y`

## Publishing Code Connect

```bash
# Preview what will be published
npx figma connect publish --dry-run

# Publish to Figma
npx figma connect publish
```

## Prop Mappers Reference

| Figma Prop Type | Code Connect Mapper |
|----------------|---------------------|
| Enum/Variant | `figma.enum('Prop Name', { FigmaOption: 'codeValue' })` |
| Boolean | `figma.boolean('Prop Name')` |
| String | `figma.string('Prop Name')` |
| Number | `figma.number('Prop Name')` |
| Instance swap | `figma.instance('Prop Name')` |
| Nested instance | `figma.nestedProps('Layer Name', { ... })` |

## CI Integration

Add to CI pipeline to keep Code Connect up to date:
```yaml
# .github/workflows/figma-code-connect.yml
- name: Publish Code Connect
  run: npx figma connect publish
  env:
    FIGMA_ACCESS_TOKEN: ${{ secrets.FIGMA_ACCESS_TOKEN }}
```

## Process for Connecting a Component Library

1. Get component node IDs from Figma (right-click → copy link)
2. Create `.figma.tsx` file for each component
3. Map Figma property names to code prop names
4. Write the `example` render function
5. Run `npx figma connect publish --dry-run` to verify
6. Run `npx figma connect publish` to push live

## Notes

- Component node IDs change if components are moved between files
- Keep `.figma.tsx` files co-located with their components
- Test locally with `--dry-run` before publishing
- Figma Dev Mode must be enabled on the file to see Code Connect snippets
