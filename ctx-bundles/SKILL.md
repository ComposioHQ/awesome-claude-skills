---
name: ctx-bundles
description: Deep context bundles that give Claude Code instant operational knowledge for popular technology stacks -- architecture patterns, correct idioms, commands, and real failure modes.
---

# ctx-bundles

Context bundles give Claude Code instant operational knowledge for a technology stack. Instead of Claude rediscovering your framework's quirks through trial and error, load a bundle and get expert-level output from the first prompt.

Each bundle is a curated 100-200 line briefing covering architecture patterns, correct idioms, copy-paste commands, and real failure modes (gotchas). 14 pre-made bundles ship for popular stacks, and you can create your own from any codebase.

## When to Use This Skill

- Starting work on a project that uses a specific stack (NestJS, FastAPI, Rails, Kubernetes, etc.) and you want Claude to know the correct patterns immediately
- Avoiding common framework gotchas that Claude would otherwise hit through trial and error
- Onboarding Claude to a new codebase by generating a custom bundle from your project
- Working across multiple technology stacks in the same session without context confusion

## What This Skill Does

1. **Loads Stack Knowledge**: Injects curated domain briefings into Claude's context covering architecture, file layout, correct patterns, failure modes, and ready-to-run commands
2. **Prevents Common Mistakes**: Each bundle includes a "Gotchas" section documenting real failure modes -- the highest-value content that saves debugging time
3. **Generates Custom Bundles**: Explores a codebase and produces a tailored bundle capturing its specific architecture, configuration, and operational knowledge
4. **Stays Token-Efficient**: Each bundle uses only 1.5-2.5K tokens. Loading 3 bundles simultaneously uses under 4% of a 200K context window

## How to Use

### Basic Usage

```
/ctx fastapi              # Load a single bundle
/ctx catalog              # Browse all available bundles
/ctx list                 # List installed bundles
/ctx show nestjs          # Preview a bundle without loading it
```

### Advanced Usage

```
/ctx fastapi postgresql   # Load multiple bundles at once
/ctx install nestjs       # Copy bundle to ~/.claude/contexts/ for customization
/ctx new myproject ~/src  # Generate a bundle from an existing codebase
/ctx update myproject     # Update a bundle after a work session
```

## Available Bundles

| Bundle | Stack | What it covers |
|--------|-------|---------------|
| `nestjs` | NestJS + TypeScript | Decorators, DI, module patterns, testing, circular dep fixes |
| `spring-boot` | Spring Boot + Java | Annotations, JPA, profiles, transactional gotchas, testing |
| `postgresql` | PostgreSQL | Index strategy, EXPLAIN ANALYZE, query antipatterns, tuning |
| `react-nextjs` | Next.js App Router | Server vs Client Components, data fetching, routing conventions |
| `fastapi` | FastAPI + Python | Pydantic v2, async patterns, dependency injection, testing |
| `kubernetes` | Kubernetes Ops | kubectl patterns, Helm, debugging, resource limits, HPA |
| `aws-lambda` | AWS Serverless | SAM/CDK, cold starts, layers, event sources, monitoring |
| `django` | Django + Python | ORM gotchas, DRF, migrations, Celery, admin patterns |
| `rails` | Ruby on Rails | ActiveRecord, Hotwire/Turbo, RSpec, convention patterns |
| `golang-api` | Go API Services | Project layout, error handling, goroutines, stdlib patterns |
| `docker-compose` | Docker Compose | Multi-service dev, volumes, networking, health checks |
| `github-actions` | GitHub Actions CI/CD | Workflows, matrix builds, caching, reusable workflows |
| `rust-cli` | Rust CLI Tools | Clap, error handling, async runtime, cross-compilation |
| `flutter` | Flutter Mobile | Widgets, state management, navigation, platform channels |

## Installation

```bash
npx skills add puretensor/ctx-bundles
```

Or manually:

```bash
git clone https://github.com/puretensor/ctx-bundles ~/.claude/skills/ctx-bundles
```

## Example

**User**: `/ctx fastapi postgresql`

**Output**: Claude loads both bundles and now knows FastAPI's Pydantic v2 patterns, async dependency injection, correct test fixtures, PostgreSQL index strategy, EXPLAIN ANALYZE usage, and common query antipatterns -- all before you write your first prompt.

## Tips

- Load bundles at the start of a session before asking Claude to write code
- Combine related bundles (e.g., `fastapi` + `postgresql` for a Python API with a database)
- Use `/ctx new` to generate a custom bundle for your own project -- it captures architecture, config, and operational knowledge specific to your codebase
- Customize installed bundles in `~/.claude/contexts/` to add your team's conventions

## Common Use Cases

- Loading stack knowledge before a coding session
- Generating a bundle for a new team member's onboarding
- Combining framework + database + infrastructure bundles for full-stack work
- Creating project-specific bundles that capture deployment, debugging, and testing knowledge

**Credit:** Built by [PureTensor, Inc.](https://github.com/puretensor)
