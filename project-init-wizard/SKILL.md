---
name: project-init-wizard
description: Auto-detects a project's tech stack and generates an optimized CLAUDE.md with project-specific conventions, recommended skills, hooks, and settings. Turns any repo from zero to fully configured in seconds.
---

# Project Init Wizard

Scans your project for languages, frameworks, databases, CI/CD pipelines, and infrastructure tooling, then generates a tailored CLAUDE.md that teaches Claude your project's specific conventions and patterns.

## When to Use This Skill

- Setting up Claude Code in a new or existing project for the first time
- After cloning an unfamiliar repo to get Claude up to speed quickly
- When onboarding team members who use Claude Code
- After major architectural changes that shift the project's tech stack
- When you want Claude to follow your project's specific conventions without manually writing instructions

## What This Skill Does

1. **Stack Detection**: Identifies languages, frameworks, package managers, databases, CI/CD tools, and monorepo structures from config files and directory patterns
2. **CLAUDE.md Generation**: Creates a project-specific instruction file with:
   - Build and test commands
   - Code conventions detected from existing code
   - Architecture overview
   - Important files and their purposes
   - Do's and don'ts specific to the tech stack
3. **Skill Recommendations**: Suggests which Claude Code skills match your detected stack (e.g., detects Next.js → recommends nextjs-app-router skill)
4. **Hook Configuration**: Sets up pre-commit hooks, lint checks, and test runners appropriate for your stack
5. **Settings Optimization**: Configures Claude Code settings for your project's needs

## How to Use

### Quick Setup

Navigate to any project and run:

```
/project-init-wizard
```

Claude scans the project and generates all configuration files.

### Review and Customize

After generation, Claude presents the detected stack and generated CLAUDE.md for review. You can:

```
The test command should be "pnpm test:unit" not "npm test"
```

```
Add a rule: never use default exports in this project
```

Claude updates the configuration based on your feedback.

## Supported Technologies

- **Languages**: TypeScript, JavaScript, Python, Go, Rust, Java, Ruby, C#, PHP, Swift, Kotlin
- **Frameworks**: Next.js, React, Vue, Svelte, Django, FastAPI, Flask, Spring Boot, Rails, Express, Nest.js
- **Databases**: PostgreSQL, MySQL, MongoDB, Redis, SQLite, Supabase, Prisma, Drizzle
- **Infrastructure**: Docker, Kubernetes, Terraform, AWS CDK, Vercel, Netlify
- **CI/CD**: GitHub Actions, GitLab CI, CircleCI, Jenkins
- **Monorepos**: Turborepo, Nx, pnpm workspaces, Lerna

## Example Output

For a Next.js + Prisma + Supabase project:

```markdown
# CLAUDE.md

## Build & Test
- `pnpm dev` — start development server
- `pnpm build` — production build
- `pnpm test` — run Vitest test suite
- `pnpm db:push` — push Prisma schema changes

## Conventions
- App Router (not Pages Router)
- Server Components by default, 'use client' only when needed
- Prisma for database access (schema at prisma/schema.prisma)
- Supabase for auth (configured in lib/supabase.ts)
- Tailwind CSS for styling, no CSS modules

## Architecture
- app/ — Next.js App Router pages and layouts
- components/ — Shared React components
- lib/ — Utility functions and database client
- prisma/ — Database schema and migrations
```

## Source Code

[github.com/manja316/claude-project-init-wizard](https://github.com/manja316/claude-project-init-wizard) (MIT License)
