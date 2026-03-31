---
name: opensource-pipeline
description: Safely open-source any private project through a 3-stage automated pipeline: fork (strip secrets), sanitize (verify clean), and package (generate CLAUDE.md, setup.sh, README, LICENSE, CONTRIBUTING). Use when preparing a private project for public GitHub release.
---

# Open-Source Pipeline

This skill guides a private project through a safe, automated 3-stage pipeline before publishing it publicly on GitHub. It chains three specialized agents — forker, sanitizer, and packager — and requires explicit user approval before any GitHub push.

## When to Use This Skill

- Preparing a private project for its first public GitHub release
- Stripping API keys, passwords, and internal references from a codebase
- Generating professional open-source scaffolding (README, LICENSE, CONTRIBUTING, setup.sh)
- Auditing an existing repo for accidentally committed secrets before open-sourcing
- Forking a platform-specific project into a standalone, portable open-source version

## What This Skill Does

1. **Forks**: Copies the project to a staging directory, strips secrets and credentials, replaces internal hostnames and paths with placeholders, and generates a `.env.example`
2. **Sanitizes**: Independently audits the fork across 6 scan categories and 30+ regex patterns — secrets, PII, internal references, dangerous files, configuration completeness, and git history — then produces a PASS/FAIL verdict before proceeding
3. **Packages**: Generates complete open-source scaffolding: `CLAUDE.md`, `setup.sh` (one-command bootstrap), `README.md`, `LICENSE`, `CONTRIBUTING.md`, and GitHub issue templates
4. **Reviews**: Presents a summary to the user before any GitHub operation
5. **Publishes**: Creates the public GitHub repo and pushes only after explicit user approval

## How to Use

### Basic Usage

```
/opensource fork my-project
```

```
Open source this project
```

```
Make this public — strip secrets and generate docs
```

### Verify an Existing Staged Fork

```
/opensource verify ~/opensource-staging/my-project
```

### Generate Docs Only

```
/opensource package my-project
```

### List All Staged Projects

```
/opensource list
```

## Example

**User**: `/opensource fork invoice-service`

**Output**:
```
Open-Source Fork Ready: invoice-service

Location: ~/opensource-staging/invoice-service
License: MIT
Files generated:
  - CLAUDE.md (87 lines)
  - setup.sh (executable)
  - README.md
  - LICENSE
  - CONTRIBUTING.md
  - .env.example (12 variables)

Sanitization: PASS
Secrets found and stripped: 4 (DATABASE_URL, STRIPE_KEY, JWT_SECRET, SMTP_PASSWORD)
Internal references replaced: 7

Proceed with GitHub creation? (yes/no/review first)
```

**Inspired by:** The Hercules platform open-source workflow at [herakles-dev/opensource-pipeline](https://github.com/herakles-dev/opensource-pipeline)

## Tips

- Always run the full pipeline (`/opensource fork`) for new releases — never skip the sanitizer
- The skill stages everything in `~/opensource-staging/` so you can review before any public push
- If the sanitizer returns FAIL, the pipeline halts and shows exactly what needs to be fixed
- Use `/opensource verify` to re-audit after applying manual fixes
- The packager infers project architecture from the codebase — review `CLAUDE.md` before pushing

## Common Use Cases

- Open-sourcing internal developer tools and CLI utilities
- Releasing platform-specific scaffolds as reusable templates
- Auditing legacy repos before adding them to a public GitHub organization
- Automating the repetitive docs-and-license step for every new open-source release
