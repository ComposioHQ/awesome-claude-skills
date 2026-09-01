---
name: anti-slop-pr
description: Enforce high-signal, zero-slop pull request descriptions grounded directly in technical code diffs. Eliminates AI buzzwords and enforces the Two-Sentence Rule.
---

# Anti-Slop PR Description

Generates concise, senior-engineer grade Pull Request descriptions by eliminating conversational AI filler, architectural hyperbole, and buzzwords.

## When to Use This Skill

- When drafting or summarizing a GitHub pull request description from git diffs
- When preparing release summaries or technical changelogs
- When writing clean, factual code changes without conversational filler

## What This Skill Does

1. **Enforces The Two-Sentence Rule**: Summarizes the entire PR in maximum 2 plain sentences (Sentence 1: What changed technically, Sentence 2: Why it was needed).
2. **Eliminates AI Buzzwords**: Filters out over-represented AI clichés based on empirical cluster analysis of 461k+ PRs (Louis Abraham, 2026).
3. **Strict Diff Grounding**: Names only exact files, functions, and code mechanisms present in the git diff.

### Banned Lexicon Reference

| Banned AI Term | Empirical Lift | Plain Engineering Replacement |
| :--- | :--- | :--- |
| `load-bearing` | **123×** | `critical`, `required`, `core` |
| `quietly` | **95×** | `defaults to`, `omits without throwing` |
| `delve` | **88×** | `inspects`, `traverses`, `parses` |
| `seam` | **84×** | `interface`, `module boundary` |
| `genuine` | **71×** | `valid`, `verified` |
| `robust` | **66×** | `error-handled`, `tested` |
| `latent` | **62×** | `hidden bug`, `unhandled condition` |
| `survived` | **58×** | `persisted`, `remained` |
| `seamless` | **59×** | `direct`, `automated` |
| `orchestrate` | **45×** | `coordinates`, `calls`, `runs` |

## How to Use

### Basic Usage

```text
Write a pull request description for my current git changes.
```

### Advanced Usage

```text
Summarize the staged git diff following the 2-sentence anti-slop rule and list verification steps.
```

## Example

**User**: "Write a PR description for the recent auth concurrency fix."

**Output**:
```markdown
## Summary
Adds a mutex lock to `RefreshToken` to prevent race conditions during concurrent token refreshes.

## Changes
- `auth/token.go`: Wrapped store lookup with `s.mu.Lock()` and `defer s.mu.Unlock()`.

## Verification
- `go test -race ./auth/...`
```

**Inspired by:** [Louis Abraham's empirical PR research](https://louisabraham.github.io/load-bearing/) and [VernSG/anti-slop](https://github.com/VernSG/anti-slop).

## Tips

- Focus on the technical mechanism rather than narrative prose.
- State facts, not philosophy: a 5-line bugfix is just a bugfix, not a system redesign.
- For breaking changes, list explicit migration steps under `## Breaking Changes` without dramatic words like *"tectonic shift"*.
- Pair with the `@vernsg/anti-slop` CLI linter for automated CI enforcement.

## Related Use Cases

- Daily GitHub pull request authoring
- Open-source repository contribution hygiene
- Automated CI/CD PR description linting
