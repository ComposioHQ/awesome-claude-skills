---
name: SDLC Wizard
description: Full software development lifecycle enforcement for Claude Code — TDD, planning, self-review, CI shepherd, and cross-model review
---

# SDLC Wizard

A self-evolving Software Development Life Cycle (SDLC) enforcement system for AI coding agents. Makes Claude plan before coding, test before shipping, and ask when uncertain.

## What It Does

- **Enforces TDD** — hooks block code edits until tests exist
- **Requires planning** — confidence levels gate autonomous vs. supervised work
- **Self-review** — automated code review before presenting to user
- **CI shepherd** — watches CI, reads logs, fixes failures autonomously
- **Cross-model review** — independent review via competing AI models

## Install

```bash
npx agentic-sdlc-wizard init
```

Then restart Claude Code (`/exit` then `claude`). Setup auto-invokes on first prompt.

## Repository

https://github.com/BaseInfinity/agentic-ai-sdlc-wizard

Built on 15+ years of SDET and QA engineering experience.
