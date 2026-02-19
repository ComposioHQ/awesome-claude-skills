# CLAUDE.md - Project Instructions for Claude Code

## Project Overview

This is the **awesome-claude-skills** repository — a curated collection of practical Claude Skills for enhancing productivity across Claude.ai, Claude Code, and the Claude API. It is maintained by ComposioHQ.

## Repository Structure

```
awesome-claude-skills/
├── .claude-plugin/          # Marketplace plugin metadata
│   └── marketplace.json     # Plugin registry with all skill entries
├── connect-apps-plugin/     # Plugin for connecting Claude to 500+ apps via Composio
├── <skill-name>/            # Individual skill directories
│   └── SKILL.md             # Skill definition and documentation
├── CONTRIBUTING.md          # Contribution guidelines
└── README.md                # Main project README with skill catalog
```

## Skill Categories

- **Business & Marketing** — lead generation, competitive research, branding
- **Communication & Writing** — content creation, meeting analysis, comms
- **Creative & Media** — design, images, video, GIFs, themes
- **Development** — artifacts, changelogs, MCP servers, testing
- **Productivity & Organization** — file management, documents, invoices

## Contributing a New Skill

1. Create a new directory: `skill-name/` (lowercase, hyphenated)
2. Add a `SKILL.md` file following the template in `CONTRIBUTING.md`
3. Register the skill in `.claude-plugin/marketplace.json`
4. Add the skill entry to `README.md` in the appropriate category (alphabetical order)
5. No emojis in README entries; follow existing format exactly

## Key Files to Know

- `README.md` — The main catalog listing all skills with descriptions and links
- `CONTRIBUTING.md` — Full guide on how to add new skills
- `.claude-plugin/marketplace.json` — Machine-readable registry of all plugins
- `template-skill/` — Reference template for creating new skills

## Conventions

- Skill directories use lowercase with hyphens (e.g., `lead-research-assistant`)
- Every skill must have a `SKILL.md` as its entry point
- Skills should solve real problems, not hypothetical ones
- Include practical examples and real-world use cases
- Always attribute original sources with "Inspired by:" or "Credit:"
