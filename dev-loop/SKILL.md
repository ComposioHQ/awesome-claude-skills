---
name: dev-loop
description: Autonomous development loop that takes a feature description and delivers a reviewed PR - brainstorm, plan, implement, and iteratively review until clean.
---

# Dev Loop

An autonomous development loop that goes from a feature description to a reviewed pull request in one command. It composes existing Claude Code commands into a full lifecycle: brainstorm, plan, implement, create PR, then iteratively review (simplify + code review + security review) until clean.

## When to Use This Skill

- You have a feature to build and want to go from idea to reviewed PR without manual orchestration.
- You want automated, iterative code review that catches security issues, code quality problems, and simplification opportunities.
- You want to run a review loop on an existing PR.

## What This Skill Does

1. **Brainstorm** (interactive): Explores requirements and design with you before any code is written.
2. **Plan** (interactive): Produces a step-by-step implementation plan, creates a GitHub issue.
3. **Implement** (autonomous): Executes the plan in an isolated git worktree, runs quality gates (lint, typecheck, tests), creates a PR.
4. **Review Loop** (autonomous, iterative): Runs `/simplify`, `/code-review`, and `/security-review` in parallel, waits for CI, then either fixes issues and loops or marks the PR as ready. Up to 5 iterations by default.

Each phase uses the appropriate model and effort level (Opus for implementation and review, Sonnet for lightweight decisions).

## How to Use

### Installation

This is a Claude Code plugin, not a standalone skill file. Install via the plugin marketplace:

```bash
claude plugin marketplace add yorrick/claude-code-plugins
claude plugin install dev-loop@yorrick
```

### Prerequisites

- [superpowers](https://github.com/obra/superpowers) plugin (brainstorming, planning, executing skills)
- [code-review](https://github.com/anthropics/claude-code-plugins) plugin (`/code-review:code-review`)
- `/simplify` and `/security-review` (built-in Claude Code commands)
- `gh` CLI (for creating issues and PRs)

### Basic Usage

```
/dev-loop Add a rate limiting middleware that throttles API requests per user
```

### Review an Existing PR

```
/review-loop
```

## Example

**User**: `/dev-loop Add CSV export to the reports page`

**What happens**:
1. Claude brainstorms the approach with you (interactive).
2. A plan is written and a GitHub issue is created.
3. Implementation runs autonomously in a worktree - code is written, tests pass, PR is opened.
4. The review loop kicks in: simplify, code review, security review, CI check. If issues are found, they are fixed and the loop repeats.
5. You get a notification when the PR is ready for human review.

## Tips

- The brainstorm and plan phases are interactive - this is where you shape the design. The rest is autonomous.
- Use `--max-iterations N` to control how many review cycles run.
- Use `--continue-pr` to resume work on an existing branch/PR.
- Monitor progress live: `watch -n1 cat .dev-loop/latest/status.txt`

**By:** [Yorrick Jansen](https://github.com/yorrick)
