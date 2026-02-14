---
name: design-principles
description: Enforce a precise, minimal design system inspired by Linear, Notion, and Stripe. Use this skill when building dashboards, admin interfaces, or any UI that needs Jony Ive-level precision - clean, modern, minimalist with taste. Every pixel matters.
---

# Design Principles

This skill enforces precise, crafted design for enterprise software, SaaS dashboards, admin interfaces, and web applications. The philosophy is Jony Ive-level precision with intentional personality — every interface is polished, and each is designed for its specific context.

## When to Use This Skill

- Building dashboards or admin interfaces for SaaS products
- Creating data-heavy analytics or business intelligence tools
- Designing enterprise software with complex information hierarchies
- Developing collaborative tools that need to feel approachable yet professional
- Crafting developer tools that require precision and density
- Building financial applications that demand trust and sophistication

## What This Skill Does

1. **Establishes context-driven design direction** — Guides you through choosing the right aesthetic personality based on your product's function, users, and emotional goals
2. **Enforces pixel-perfect craft standards** — Applies a 4px grid system, symmetrical padding, consistent border radius, and intentional depth strategies
3. **Creates perceptual hierarchy** — Implements four-level contrast systems using typography, spacing, and color with purpose
4. **Optimizes for content type** — Adapts layouts, density, and information architecture based on whether users need to scan, focus, compare, or analyze
5. **Prevents generic AI aesthetics** — Ensures every interface has appropriate personality while maintaining professional quality
6. **Builds design systems** — Creates cohesive component libraries with consistent surface treatment, iconography, and animation timing

## How to Use

### Basic Usage

When building any UI component or interface:

```
/design-principles

I need to build a project management dashboard for software teams.
```

Claude will:
1. Ask about the product context and users
2. Recommend a design direction (e.g., "Precision & Density" for power users)
3. Apply craft principles: 4px grid, consistent spacing, appropriate depth strategy
4. Generate code with polished details: proper typography hierarchy, thoughtful color usage, intentional animations

### Advanced Usage

For specific design decisions:

```
/design-principles

I'm building a fintech dashboard. Should I use shadows or borders for card depth?
What color foundation would establish trust?
```

The skill will analyze your context and recommend:
- Cool gray foundations for professional trust
- Layered shadow approach for premium feel
- Appropriate spacing density for financial data
- Monospace typography for numbers and IDs

## Example

**Prompt:**
```
/design-principles

Build a metrics card showing monthly recurring revenue with a sparkline trend
```

**Output:**
```tsx
export function RevenueCard() {
  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">MRR</p>
          <p className="mt-2 font-mono text-3xl font-semibold tracking-tight text-gray-900">
            $127,450
          </p>
          <p className="mt-1 text-sm text-gray-500">
            <span className="font-medium text-green-600">+12.5%</span> vs last month
          </p>
        </div>
        <Sparkline data={revenueData} className="h-16 w-24" />
      </div>
    </div>
  )
}
```

Note the craft details:
- 4px border radius (sharp, technical feel)
- Symmetrical 16px padding
- Monospace font for the number (signals "this is data")
- Four-level hierarchy: heading (gray-600) → primary value (gray-900) → supporting text (gray-500)
- Color only for semantic meaning (green for positive change)

## Tips

- **Always establish context first** — Don't default to warm neutrals or soft shadows. Ask what the product needs to feel like
- **Commit to a depth strategy** — Choose borders-only, single shadows, or layered shadows and apply consistently
- **Vary card layouts, not surface treatment** — A metric card can have different internal structure than a settings card, but they should share border weight, shadow depth, padding scale
- **Use color sparingly** — Gray builds structure. Color only appears for status, actions, or errors
- **Typography creates hierarchy** — Let size do the heavy lifting. Bold weights should emphasize, not define hierarchy
- **Dense where users scan, spacious where they orient** — 8px gaps in data tables, 64px between major sections

## Common Use Cases

- **Analytics dashboards** — Data-first layouts with monospace numbers, tabular alignment, and chart-optimized color palettes
- **Admin interfaces** — Dense grids for scanning records with appropriate filters and bulk actions
- **Collaborative tools** — Generous spacing with warm foundations for approachable, human-feeling products
- **Developer tools** — Monospace influence, borders over shadows, utility-focused with minimal chrome
- **Financial applications** — Cool tones, layered depth, sophisticated typography for trust and gravitas
- **SaaS product dashboards** — Context-appropriate personality with enterprise-grade craft standards

## Inspired By

Inspired by the design systems of Linear (precision and density), Notion (warmth and approachability), Stripe (sophistication and trust), and Vercel (boldness and clarity). This skill synthesizes principles from companies known for exceptional interface craft.
