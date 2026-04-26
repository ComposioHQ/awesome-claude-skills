---
name: naksha-studio-design
description: A virtual design studio with 58 UI/UX commands, 26 specialist roles, and 7 AI agents — covering design, Figma, QA, social, email, data-viz, print, motion, and more.
---

# Naksha Studio — Virtual Design Team for Claude Code

A comprehensive design skill suite that gives Claude Code a full virtual design team. 58 commands across 11 categories, 26 specialist roles (UI Designer, UX Researcher, Motion Designer, Content Designer, etc.), and 7 autonomous agents — all orchestrated through a single `/design` entry point.

## When to Use

- You need to **design UI components, pages, dashboards, or full apps** with production-quality code output
- You want a **design system** generated from scratch, extracted from Figma, or audited from existing code
- You need a **UX audit**, **accessibility review**, or **quantitative design score** (0–100) for an existing design
- You want to **create or manipulate Figma files** programmatically (frames, components, prototypes, variables)
- You need **social media assets**, **email templates**, **print layouts**, **data visualizations**, or **presentations**
- You want AI-assisted **image/video/audio generation prompts** or **moodboards**
- You need **compliance checks** (GDPR, HIPAA, PCI, ADA) on UI designs
- You want to **convert HTML designs** to React, Vue, Svelte, Next.js, or Astro components

## Capabilities

### Core Design (10 commands)
| Command | Description |
|---------|-------------|
| `/design` | Design anything — the main orchestrator. Assembles the right specialists for the task |
| `/design-review` | Visual AI critique + code-level audit (accessibility, usability, consistency, content, motion) |
| `/design-critique` | Heuristic UX review against Nielsen's 10 principles |
| `/design-qa` | Visual QA across breakpoints, tokens, and interactive states |
| `/design-system` | Generate, extract, or audit a design token system (CSS vars, Tailwind, Style Dictionary) |
| `/design-score` | Quantitative 0–100 score: Accessibility (25) + Usability (25) + Visual Quality (25) + Token Compliance (25) |
| `/brand-kit` | Build a full brand identity from a single color |
| `/brand-strategy` | Develop brand positioning and voice guidelines |
| `/design-sprint` | Run a structured 5-day design sprint |
| `/design-present` | Create presentation-ready design decks |

### Figma Integration (8 commands)
| Command | Description |
|---------|-------------|
| `/figma` | General Figma operations |
| `/figma-create` | Create frames, components, and layouts directly in Figma |
| `/figma-responsive` | Add responsive variants to Figma components |
| `/figma-prototype` | Build interactive prototypes in Figma |
| `/figma-sync` | Sync code design tokens ↔ Figma variables |
| `/figma-component-library` | Build a full Figma component library |
| `/ab-variants` | Create A/B design variants in Figma |
| `/site-to-figma` | Convert a live website URL into a Figma frame |

### Quality & Audit (4 commands)
| Command | Description |
|---------|-------------|
| `/ux-audit` | Full Figma compliance audit against a design brief |
| `/accessibility-audit` | WCAG AA compliance audit |
| `/lint-design` | Lint for spacing, color, and typography inconsistencies |
| `/component-docs` | Generate component documentation |

### Social Media (3 commands)
| Command | Description |
|---------|-------------|
| `/social-content` | Design posts for Instagram, LinkedIn, X |
| `/social-campaign` | Plan a multi-platform campaign |
| `/social-analytics` | Build a social performance dashboard |

### Email Design (3 commands)
| Command | Description |
|---------|-------------|
| `/email-template` | Build production HTML email templates (MJML/table) |
| `/email-campaign` | Plan a multi-email campaign sequence |
| `/email-audit` | Audit emails for deliverability and rendering |

### Data Visualization (3 commands)
| Command | Description |
|---------|-------------|
| `/chart-design` | Design accessible charts (bar, line, pie, scatter) |
| `/dashboard-layout` | Build KPI dashboards and analytics layouts |
| `/data-viz-audit` | Audit data visualizations for accuracy and clarity |

### AI Generation (5 commands)
| Command | Description |
|---------|-------------|
| `/gen-image` | Generate image prompts for AI art tools |
| `/gen-video` | Write AI video briefs (Sora, Runway, Pika) |
| `/gen-audio` | Create sound design specs and audio UI guidance |
| `/gen-moodboard` | Generate moodboard directions and visual references |
| `/prompt-refine` | Refine and improve AI generation prompts |

### Print & PDF (3 commands)
| Command | Description |
|---------|-------------|
| `/print-layout` | Build print layouts (business cards, brochures, posters) |
| `/pdf-report` | Generate multi-page PDF reports |
| `/print-audit` | Preflight audit for CMYK, bleed, font embedding |

### Frontier (8 commands)
| Command | Description |
|---------|-------------|
| `/design-chatbot` | Design chatbot UIs — dialog flows, bubbles, quick replies |
| `/design-voice-ui` | Design voice interfaces — wake word, VUI, hybrid layouts |
| `/design-spatial` | Design for visionOS / WebXR — depth hierarchy, spatial windows |
| `/design-ar-overlay` | Design AR overlays — anchoring, world tracking, scan states |
| `/design-gdpr` | Generate GDPR/CCPA consent flows and privacy controls |
| `/design-compliance` | Compliance audit (HIPAA, PCI, ADA) |
| `/design-compare` | Side-by-side visual analysis of two URLs |
| `/competitive-audit` | Extract design patterns from a competitor URL |

### Memory & Pipeline (5 commands)
| Command | Description |
|---------|-------------|
| `/naksha-init` | Set up project memory (brand, font, framework, tokens) |
| `/naksha-status` | View current project context and recent decisions |
| `/pipeline` | Chain commands into multi-step workflows |
| `/design-framework` | Convert HTML to React/Vue/Svelte/Next.js/Astro |
| `/design-template` | Browse and use production-ready layout templates |

### Meta (6 commands)
| Command | Description |
|---------|-------------|
| `/design-tutorial` | Interactive guided tour (12 tracks) |
| `/naksha-help` | Quick-reference for all commands |
| `/illustration-system` | Build a consistent illustration style guide |
| `/motion-design` | Create motion design specs and animation guidelines |
| `/presentation-design` | Design presentation slides and decks |
| `/video-script` | Write video scripts and storyboards |

## The 26 Specialist Roles

Naksha assembles teams from these roles based on the task:

- **Product Designer** — End-to-end product features, business strategy
- **UI Designer** — Visual design, layout, typography, color
- **UX Designer** — Flows, wireframes, information architecture
- **UX Researcher** — Usability review, accessibility, heuristics (Nielsen + WCAG)
- **Content Designer** — Microcopy, labels, error messages, CTAs
- **Design System Lead** — Tokens, theming, consistency, dark mode
- **Motion Designer** — Animations, transitions, micro-interactions
- And 19 more domain-specific specialists

## Usage Examples

### Basic: Design a landing page
```
/design a SaaS landing page for a project management tool — dark theme, modern, hero with 3D illustration
```

### Intermediate: Score an existing design
```
/design-score https://myapp.com/dashboard
```

Output:
```
╔══════════════════════════════════════════════════════════╗
║  Design Score                                            ║
╚══════════════════════════════════════════════════════════╝

  Overall:   82/100   B

  Accessibility:       20/25  ████████████████░░░░  80%
  Usability:           22/25  ██████████████████░░  88%
  Visual Quality:      21/25  █████████████████░░░  84%
  Token Compliance:    19/25  ███████████████░░░░░  76%

  Grade: B — Minor polish needed
```

### Advanced: Full design-to-code pipeline
```
/naksha-init              # Set up brand memory (colors, fonts, framework)
/design a pricing page    # Design with assembled specialist team
/design-review            # Audit accessibility, usability, visual quality
/design-framework react   # Convert HTML output to React + Tailwind components
/figma-create             # Push the design to Figma for the team
```

## Example Output

Running `/design a hero section for a fintech app`:

1. **Research phase** — UX Researcher analyzes fintech hero patterns
2. **Strategy phase** — Product Designer defines scope, UX Designer creates wireframe
3. **Creative phase** — UI Designer builds visual, Content Designer writes copy, Design System Lead generates tokens
4. **Polish phase** — Motion Designer adds entrance animations, consistency review
5. **Delivery** — Outputs `design-output.html` (semantic HTML + Tailwind + CSS custom properties), responsive at 375px/768px/1280px+

## Installation

```bash
# Clone the Naksha Studio repository
git clone https://github.com/anthropics/naksha-studio.git

# Copy skills to your Claude Code project
cp -r naksha-studio/skills/naksha .claude/skills/naksha
cp -r naksha-studio/skills/design .claude/skills/design
```

Or add to an existing project:
```bash
# In your project's .claude/ directory
git submodule add https://github.com/anthropics/naksha-studio.git skills/naksha
```

## Tips

- Start with `/naksha-init` to configure project memory (brand colors, fonts, framework) — all subsequent commands inherit these defaults
- Use `/design-score` to get a quantitative baseline before and after design changes
- Chain commands with `/pipeline` for repeatable multi-step workflows (e.g., design → review → framework conversion → Figma sync)
- The `/design` command caps at ~4 specialist roles per task for efficiency — it picks the most relevant ones
- All commands fall back gracefully when MCP integrations (Figma, Playwright, Stitch) are unavailable
- Use `prefers-reduced-motion` support is built into all motion-related output

## Common Use Cases

- **Startup MVP** — Go from idea to production-ready UI with `/design` + `/design-framework`
- **Design System Bootstrap** — Extract tokens from existing code with `/design-system extract from project`
- **Pre-launch Audit** — Score your app with `/design-score` + `/accessibility-audit` + `/ux-audit`
- **Figma-to-Code** — Pull designs from Figma and convert with `/figma-sync` + `/design-framework`
- **Social Launch** — Create campaign assets with `/social-campaign` + `/social-content`
- **Client Presentations** — Build polished decks with `/design-present` + `/presentation-design`

---

*Created by [@devsarigom](https://github.com/devsarigom) — Source: [naksha-studio](https://github.com/anthropics/naksha-studio)*
