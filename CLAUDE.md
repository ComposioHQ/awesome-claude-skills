# CLAUDE.md

This file provides guidance for AI assistants working with the **Awesome Claude Skills** repository.

## Project Overview

A curated collection of practical Claude Skills maintained by ComposioHQ. Skills are modular, self-contained packages that extend Claude's capabilities with specialized workflows, tool integrations, and domain expertise. This is a **documentation-driven** repository, not a compiled software project.

Skills work across Claude.ai, Claude Code, and the Claude API.

## Repository Structure

```
awesome-claude-skills/
├── CLAUDE.md                  # This file
├── README.md                  # Skills index, quickstart, getting started guide
├── CONTRIBUTING.md            # Contribution guidelines and PR process
├── .claude-plugin/
│   └── marketplace.json       # Plugin marketplace metadata (25 plugins)
├── template-skill/            # Minimal SKILL.md template for new skills
├── skill-creator/             # Meta-skill: guide for creating new skills
│   └── scripts/               # init_skill.py, package_skill.py
├── connect-apps-plugin/       # Plugin with .claude-plugin/plugin.json manifest
│   └── .claude-plugin/
│       └── plugin.json
├── document-skills/           # Nested sub-skills (docx, pdf, pptx, xlsx)
└── <skill-name>/              # 30+ individual skill directories
    ├── SKILL.md               # Required: skill instructions + YAML frontmatter
    ├── scripts/               # Optional: executable Python/Bash code
    ├── references/            # Optional: documentation for Claude context
    ├── assets/                # Optional: templates, fonts, images for output
    └── LICENSE.txt            # Optional: skill-specific license
```

There are **32 skill directories** at the root level plus supporting files.

## Skill Anatomy (Required Knowledge)

Every skill must contain a `SKILL.md` with YAML frontmatter:

```yaml
---
name: skill-name            # Required, lowercase-hyphenated
description: One sentence.  # Required, third-person ("This skill should be used when...")
license: ...                # Optional
---
```

The body contains Markdown instructions written in **imperative/infinitive form** (not second person). Standard sections: purpose, "When to Use", capabilities, "How to Use", examples, tips.

### Bundled Resources

| Directory      | Purpose                                       | Loaded into context? |
|---------------|-----------------------------------------------|---------------------|
| `scripts/`    | Deterministic, reusable code (Python/Bash)    | Executed directly   |
| `references/` | Documentation Claude reads as needed          | On demand           |
| `assets/`     | Files used in output (templates, fonts, etc.) | No                  |

## Languages Used

- **Markdown** — All skill definitions (primary)
- **Python** — Helper scripts (MCP builder, document skills, GIF creator, webapp testing)
- **Bash** — Shell scripts (artifact bundling, video downloading)
- **JavaScript/TypeScript** — Frontend artifacts (React + Vite), PPTX generation

## No Build System

There is no package.json, Makefile, CI/CD pipeline, or test runner at the repository level. Each skill is self-contained. Some skills have their own `requirements.txt` for Python dependencies.

## Naming Conventions

- Skill directory names: **lowercase with hyphens** (e.g., `slack-gif-creator`)
- SKILL.md `name` field must match the directory name
- Branch naming for contributions: `add-skill-name`
- Commit messages: `Add [Skill Name] skill` or `feat: description`

## Commit Message Style

The repository uses a mix of conventional and descriptive styles:

```
Add jules, deep-research, outline, and google-workspace skills (#77)
feat: add twitter algo skill
feat: Add LangSmith Fetch - First AI observability skill (#21)
fix: fix video downloader skill
```

Use descriptive messages. Conventional commits (`feat:`, `fix:`) are acceptable but not mandatory.

## Adding a New Skill

1. Create a directory with a lowercase-hyphenated name
2. Add a `SKILL.md` with proper YAML frontmatter and Markdown body
3. Optionally add `scripts/`, `references/`, `assets/` directories
4. Add the skill to `README.md` in the appropriate category, **in alphabetical order**
5. Follow the template in `template-skill/SKILL.md` or use `skill-creator/scripts/init_skill.py`

### Validation

Use `skill-creator/scripts/package_skill.py <path/to/skill>` to validate:
- YAML frontmatter format and required fields
- Naming conventions and directory structure
- Description completeness

## README.md Categories

Skills are organized into these categories in README.md:

- Document Processing
- Development & Code Tools
- Data & Analysis
- Business & Marketing
- Communication & Writing
- Creative & Media
- Productivity & Organization
- Collaboration & Project Management
- Security & Systems

Format for entries: `- [Skill Name](./skill-name/) - One-sentence description.`

External skills link to their GitHub repos instead of local paths.

## Quality Standards

All skills must:

1. Solve a real problem (not hypothetical)
2. Be well-documented with clear examples
3. Be accessible to non-technical users
4. Include practical, real-world usage examples
5. Be tested across Claude platforms
6. Confirm before destructive operations
7. Be portable across Claude.ai, Claude Code, and API

## Key Files to Know

| File | Purpose |
|------|---------|
| `README.md` | Main index of all skills with categories and quickstart |
| `CONTRIBUTING.md` | Contribution workflow, PR process, skill requirements |
| `.claude-plugin/marketplace.json` | Plugin marketplace metadata for 25 published plugins |
| `template-skill/SKILL.md` | Minimal starting template for new skills |
| `skill-creator/SKILL.md` | Comprehensive guide for skill creation process |
| `skill-creator/scripts/init_skill.py` | Generates new skill directory from template |
| `skill-creator/scripts/package_skill.py` | Validates and packages skills into zip files |

## License

Repository: Apache License 2.0. Individual skills may have their own license — check each skill's `LICENSE.txt`.
