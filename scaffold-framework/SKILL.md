---
name: Scaffold Framework
description: Structured Claude Code development with persistent Obsidian memory, multi-agent decision enforcement, and 3-tier model routing (~75% token savings). 17 skills.
---

## When to Use

Use Scaffold when:
- You're tired of re-explaining your project to Claude every session
- You need structured architecture decisions, not vibes
- Your token costs are too high from routing everything to Opus
- Claude keeps stopping mid-task or ignoring your CLAUDE.md rules

## What This Skill Does

Scaffold is a 17-skill framework that solves the four biggest Claude Code pain points:

**1. Persistent Memory + Obsidian Integration**
`/project-setup` generates a full Obsidian vault for your project (7-folder knowledge base, session logs, architecture decision log). `/preload` reads it all at session start — Claude knows your project, decisions, and rules without any recap.

**2. Decision Enforcement**
`/decide` deploys scaled research and debate agents (2-12 agents depending on decision size) with real WebSearch, then logs the verdict permanently. No more winging architecture choices.

**3. 3-Tier Model Routing (~75% token savings)**
Every skill automatically routes to the cheapest capable model: Haiku for search/retrieval, Sonnet for code generation, Opus for architecture and security. Applied across all 17 skills.

**4. Workflow & Recovery**
Hard workflow gates, TDD iron law, systematic debugging, context save/restore before compaction, loop guard for mid-task stops.

## How to Use

### Basic

```bash
# Install globally
git clone https://github.com/alexxenn/scaffold && cd scaffold && ./install.sh

# Or install via Claude Code plugin marketplace — search "scaffold"
```

### First session

```
/preload                              # warm-start: reads memory + vault + decisions
/project-setup my-app --tech nextjs  # bootstrap project with Obsidian vault
/decide "database: postgres vs mysql" # research + debate + permanent log
```

### Daily workflow

```
/preload          # every session start — no recap needed
/workflow-gate    # before any new feature
/tdd              # before writing code
/decide           # before any architecture choice
/review --diff    # before committing
/context-save     # before closing
```

## All 17 Skills

| Skill | Purpose |
|---|---|
| `/preload` | Warm-start: reads all memory, decisions, rules → execution brief |
| `/project-setup` | Bootstrap Obsidian vault, CLAUDE.md, memory, custom project skills |
| `/decide` | Multi-agent research + debate, permanent Architecture Decision Record |
| `/sync-context` | Loop-compatible drift detection, runs every 15min |
| `/workflow-gate` | Hard gates: brainstorm → plan → execute → review |
| `/sparc` | Spec → Pseudocode → Architecture → Refinement → Completion |
| `/tdd` | Test-first iron law: RED → GREEN → REFACTOR |
| `/review` | Two-stage: Sonnet auto-pass + Opus deep-review (flagged files only) |
| `/debug-systematic` | 4-phase scientific debugging, 3-failure escalation |
| `/verify` | Hard gate before marking work done |
| `/route-model` | 3-tier routing reference: Haiku/Sonnet/Opus protocol |
| `/dispatch` | Parallel agent dispatch with automatic model routing |
| `/worktree` | Git worktree isolation for safe experiments |
| `/skill-create` | Meta-skill: creates new skills with routing baked in |
| `/loop-guard` | Detects incomplete work, forces completion |
| `/context-save` | Saves state before compaction, writes RESUME.md |
| `/agents-md` | Generates universal AGENTS.md for Claude Code, Cursor, Copilot |

## Tips

- Always run `/preload` first in every session — it replaces the 10-minute recap
- Use `/decide --size major` for architecture choices, `--size minor` for naming
- The Stop hook reminds you to run `/context-save` before closing
- Marketplace install namespaces skills as `/scaffold:preload` etc.

## Common Use Cases

- Starting a new SaaS project with full context management from day one
- Reducing Claude Code token costs on projects with many agent spawns
- Maintaining architectural coherence across a long-running project
- Recovering from context compaction without losing session state

*By [@alexxenn](https://github.com/alexxenn)*
