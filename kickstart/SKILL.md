---
name: kickstart
description: Start any new project with a structured co-founder session. Claude asks 5 critical questions, builds a master plan, creates knowledge base directories with context files, and sets up the development skeleton for 10x faster execution.
---

# Project Kickstart

Turn Claude into your technical co-founder for the first hour of any new project. Instead of jumping straight into code, this skill runs a structured planning session that produces a master plan, knowledge base, context files, and development skeleton — everything Claude Code needs to build 10x faster.

## When to Use This Skill

- Starting a brand new project from scratch
- Adding a major module/feature to an existing project
- Onboarding Claude to an unfamiliar codebase
- When you feel stuck and need structured direction
- Beginning any project where "where do I start?" is the first question

## What This Skill Does

1. **Understand**: Asks you 5 critical questions to deeply understand the project
2. **Plan**: Creates a master plan with roadmap, directory structure, and execution order
3. **Context**: Generates knowledge base markdown files for every major area
4. **Skeleton**: Sets up CLAUDE.md, skill files, directory structure, and boilerplate
5. **Route**: Tells you which AI mode/tool to use for each task phase
6. **Launch**: Gives you the first concrete action to start building

## How to Use

### Basic Usage

```
/kickstart my-saas-app
```

Claude will ask 5 questions, then build the entire project skeleton.

### For a new module

```
/kickstart authentication-system
```

Same process but scoped to a module within an existing project.

### Quick mode (if you already have answers)

```
/kickstart e-commerce platform - target: small businesses, stack: Next.js + Stripe + Supabase, MVP: product listing + checkout in 1 week
```

## The 5 Questions

Claude always asks these before planning:

1. **Goal & Value**: What exactly will this build and for whom?
2. **Current State**: Starting from zero or building on something existing?
3. **Technical Constraints**: Required technologies, APIs, databases?
4. **Priority & MVP**: What should be working within the first week?
5. **Scale & Future**: Expected users and 3-month goal?

> Don't rush these answers — the foundation is built here.

## Example

**User**: `/kickstart invoice-management-app`

**Output** (after Q&A):

```
## Project Understanding

Project: Invoice Management App
Goal: Small business invoice creation, tracking, and payment reminders
User: Freelancers and small business owners (1-10 employees)
Stack: Next.js 15, Supabase, Resend (email), Stripe
MVP: Create invoice + send PDF via email (Week 1)

## Roadmap

Week 1: Invoice CRUD + PDF generation + email sending
Week 2: Dashboard, payment tracking, recurring invoices
Week 3: Stripe integration, client portal, polish

## Directory Tree

invoice-app/
├── CLAUDE.md
├── .claude/skills/
├── docs/
│   ├── architecture.md
│   ├── api-spec.md
│   ├── data-model.md
│   └── decisions/
│       └── 001-pdf-library-choice.md
├── src/
│   ├── app/
│   ├── features/
│   │   ├── invoices/
│   │   ├── clients/
│   │   └── payments/
│   └── shared/
...

## Context Files Created

| File | Purpose |
|------|---------|
| CLAUDE.md | Project rules, stack, conventions |
| docs/architecture.md | System overview, component relationships |
| docs/data-model.md | Database schema, entity relationships |
| docs/api-spec.md | API endpoints reference |

## Automation & Tooling

| Tool | Why | Impact | Effort |
|------|-----|--------|--------|
| Supabase CLI | Type-safe DB queries | 5x | Low |
| Resend + react-email | Invoice email templates | 3x | Low |
| /typefix skill | Catch type errors early | 2x | Already installed |

## Mode Routing

| Task | Use |
|------|-----|
| DB schema design | Claude Code (interactive) |
| API endpoint generation | Codex CLI (bulk scaffolding) |
| UI component review | Gemini CLI (second opinion) |
| Payment flow logic | Claude Code (critical path) |

## First Action

Create the Supabase project and define the invoices table schema.
Run: `npx supabase init && npx supabase db reset`
```

## Output Format

Everything is saved as files, not just chat messages:

```
docs/architecture.md    → System design
docs/data-model.md      → Database schema
docs/api-spec.md        → API reference
docs/decisions/*.md     → Architecture Decision Records
CLAUDE.md               → Project context (auto-loaded every session)
.claude/skills/         → Custom project skills
```

## Tips

- Give detailed answers to the 5 questions — vague input = vague plan
- If you already have a partial codebase, mention it so Claude adapts
- The generated `CLAUDE.md` is loaded automatically in every future session
- Re-run `/kickstart` when pivoting or adding a major new area
- Combine with `/x 5` after kickstart to parallelize the first batch of tasks
- The master plan is a living document — update it as the project evolves

## Common Use Cases

- SaaS product from idea to MVP
- Open source library setup with proper docs structure
- Freelance client project with tight deadline
- Hackathon project (use quick mode for speed)
- Adding a complex feature (auth, payments, AI pipeline) to existing app
- Team onboarding — share the generated docs with new developers
