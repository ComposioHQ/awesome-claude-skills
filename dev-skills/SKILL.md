# Dev Skills

## Overview

A suite of 10 language-agnostic Claude Code skills that cover the full software development lifecycle, from brainstorming ideas to opening pull requests. Each skill auto-detects the project's language and stack, applying idiomatic practices without manual configuration.

## When to Use

- Starting a new feature and want a structured workflow from idea to PR
- Investigating a bug with disciplined root-cause analysis
- Implementing from a GitHub issue with a clear plan
- Reviewing code across multiple perspectives before committing
- Organizing messy changes into clean, atomic commits

## Key Features

1. **Language-agnostic** - Auto-detects Go, Python, TypeScript, Rust, Java, and more
2. **10 interconnected skills** - Each works standalone or chains into complete workflows
3. **Plan-driven execution** - Separates design from implementation with persistent, reviewable plans
4. **Parallel agents** - Uses simultaneous exploration and review to avoid tunnel vision
5. **Strict TDD support** - RED-GREEN-REFACTOR discipline with the test written first
6. **4-perspective code review** - Code quality, business logic, security, and test coverage
7. **Conventional Commits** - Auto-organizes changes into clean, bisectable commit history

## Skills

| Skill | Description |
|-------|-------------|
| `dev-brainstorm` | Validate ideas and design solutions before writing any code |
| `dev-plan` | Write a detailed implementation plan saved to `docs/plans/` |
| `dev-plan-issue` | Read a GitHub issue and produce an implementation plan from it |
| `dev-do` | Execute an approved plan task by task with test validation |
| `dev-tdd` | Implement features using RED-GREEN-REFACTOR discipline |
| `dev-debug` | Investigate bugs by finding root causes first |
| `dev-review` | Run a 4-perspective code review in parallel |
| `dev-commit` | Organize changes into clean, atomic Conventional Commits |
| `dev-pr` | Create a GitHub pull request with auto-generated title and description |
| `dev-explore` | Understand an unfamiliar codebase through parallel exploration |

## Typical Workflows

**New feature:**
```
/dev-brainstorm -> /dev-plan -> /dev-do -> /dev-review -> /dev-commit -> /dev-pr
```

**Bug fix:**
```
/dev-debug -> /dev-review -> /dev-commit -> /dev-pr
```

**From a GitHub issue:**
```
/dev-plan-issue 42 -> /dev-do -> /dev-review -> /dev-commit -> /dev-pr
```

**Quick implementation (small change):**
```
/dev-tdd -> /dev-review -> /dev-commit -> /dev-pr
```

**Starting in unfamiliar code:**
```
/dev-explore -> /dev-plan -> /dev-do
```

## Installation

Add to your `~/.claude/settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "phbpx": {
      "source": {
        "source": "github",
        "repo": "phbpx/dev-skills"
      }
    }
  },
  "enabledPlugins": {
    "dev-skills@phbpx": true
  }
}
```

Or clone manually:

```bash
git clone https://github.com/phbpx/dev-skills
cd dev-skills
for skill in dev-*/; do
  cp -r "$skill" ~/.claude/skills/
done
```

## Examples

### Example 1: Building a new API endpoint

```
User: I need to add a /users/:id/preferences endpoint
> /dev-brainstorm
(explores REST vs GraphQL, storage options, caching strategy)
> /dev-plan
(creates docs/plans/user-preferences.md with 5 tasks)
> /dev-do
(implements each task, running tests after each one)
> /dev-review
(4 parallel agents check quality, logic, security, tests)
> /dev-commit
(3 atomic commits: model, handler, tests)
> /dev-pr
(opens PR with auto-generated description linking to the plan)
```

### Example 2: Debugging a production issue

```
User: Users report 500 errors on the login endpoint
> /dev-debug
(reproduces with a failing test, traces to a nil pointer in session middleware)
> /dev-review
(verifies the fix doesn't introduce regressions)
> /dev-commit
(single commit: "fix: handle nil session in auth middleware")
> /dev-pr
```

### Example 3: Working from a GitHub issue

```
User: /dev-plan-issue 87
(reads issue #87, produces a plan with acceptance criteria mapped to tasks)
> /dev-do
(executes the plan, each task validated against "done when" criteria)
> /dev-review -> /dev-commit -> /dev-pr
```

### Example 4: Exploring before changing

```
User: I need to refactor the payment module but I don't know the code
> /dev-explore
(parallel agents map architecture, data flow, key files, and pitfalls)
> /dev-plan
(informed plan based on exploration findings)
> /dev-do
```

## Best Practices

- Start with `/dev-brainstorm` or `/dev-explore` when unsure about the approach
- Always run `/dev-review` before committing, even for small changes
- Use `/dev-plan-issue` to keep implementation aligned with issue requirements
- Each skill works standalone - skip steps that don't apply to your situation
- Plans in `docs/plans/` serve as documentation for future reference

## Source

Created by [@phbpx](https://github.com/phbpx) - [GitHub Repository](https://github.com/phbpx/dev-skills)
