---
name: MemStack
description: Persistent project context framework that auto-loads tech stack, file structure, coding patterns, and task history into every Claude Code session.
author: Claude Weidner (@cwinvestments)
category: Collaboration & Project Management
tags: [context-management, session-persistence, developer-tools, workflow-automation, claude-code]
---

# MemStack

A lightweight, zero-config framework that eliminates context loss between Claude Code sessions by auto-loading your full project context — tech stack, file structure, coding patterns, task history, and development workflows — into every new session.

## When to Use This Skill

- Starting a new Claude Code session and needing full project context immediately
- Managing multiple projects where each has different tech stacks and conventions
- Working across multiple devices and needing consistent context everywhere
- Running long development sprints where session continuity is critical
- Onboarding Claude Code to an existing codebase quickly

## What This Skill Does

MemStack installs a `.claude/` directory into your project containing structured markdown files that Claude Code auto-reads at session start. Instead of spending the first 10 minutes re-explaining your project, Claude immediately understands your stack, patterns, and what you were working on.

### Built-in Skills (17 automated workflows):

1. **Seal** — Analyzes staged changes and generates structured atomic commit messages
2. **Work** — Plans coding sessions with prioritized task lists
3. **Diary** — Logs session progress with structured handoff for next session
4. **Monitor** — Reports project status across all tracked metrics
5. **Scan** — Audits codebase for issues, tech debt, and security concerns
6. **Ship** — Pre-deployment checklist and verification
7. **Snap** — Creates project snapshots for rollback points
8. **Tidy** — Code cleanup and formatting standardization
9. **Map** — Generates and updates project file structure maps
10. **Sync** — Keeps context files in sync with actual project state
11. **Guide** — Generates onboarding docs for new contributors
12. **Review** — Code review with project-specific conventions
13. **Test** — Test generation following project patterns
14. **Deploy** — Deployment workflow automation
15. **Humanize** — Removes AI-generated writing patterns from content
16. **State** — Maintains living state document tracking current position and decisions
17. **Verify** — Checks completed work against stated goals before committing

## How to Use

### Installation

```bash
# Clone into your project
git clone https://github.com/cwinvestments/memstack.git
cp -r memstack/.claude/ your-project/.claude/
```

### Configuration

Edit the context files in `.claude/` to match your project:

- `CLAUDE.md` — Project overview, tech stack, key patterns
- `SKILLS.md` — Available skill definitions and invocations
- `STATE.md` — Current project state and session continuity

### Invocation

Skills are invoked naturally in Claude Code:

```
Use the Seal skill to commit these changes
Use the Work skill to plan this session
Use the Diary skill to log what we accomplished
Use the Verify skill to check this work
```

## Example

**Without MemStack:**
```
You: "We're building a Next.js 14 app with TypeScript, Tailwind CSS,
Supabase for the database, Zustand for state management. The project
structure is... [10 minutes of context-setting]"
```

**With MemStack:**
```
You: "Use the Work skill to plan today's session"
Claude: [Already knows your entire stack, file structure, conventions,
and picks up exactly where last session ended]
```

## Tips

- Run `Use the Sync skill` periodically to keep context files aligned with your actual codebase
- Use `State` skill at the end of every session for seamless next-session pickup
- Each project gets its own `.claude/` directory — context is always project-specific
- Works across multiple devices when `.claude/` is committed to your repo
- Combine with Headroom proxy for additional token optimization

## Common Use Cases

| Scenario | Skills Used |
|----------|------------|
| Starting a new session | Work, State |
| End of session | Diary, State, Seal |
| Pre-deployment | Ship, Verify, Scan |
| Code cleanup sprint | Tidy, Review, Seal |
| Writing content/docs | Humanize, Guide |
| Onboarding to existing project | Map, Sync, Guide |

## Links

- **Repository:** [github.com/cwinvestments/memstack](https://github.com/cwinvestments/memstack)
- **Author:** [@cwinvestments](https://github.com/cwinvestments)
- **License:** MIT
