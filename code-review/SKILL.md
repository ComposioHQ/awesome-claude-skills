---
name: code-review
description: Perform thorough, constructive code reviews covering correctness, security, performance, maintainability, and style. Use this skill when the user wants code reviewed, asks for feedback on their code, or needs a diff/PR reviewed.
---

# Code Review

Perform thorough, actionable code reviews that improve code quality, catch bugs, and share knowledge.

## Review Dimensions

Review code across these dimensions, in order of importance:

### 1. Correctness
Does the code do what it's supposed to do?
- Does it handle edge cases? (empty input, null/undefined, zero, large values)
- Are there off-by-one errors in loops or indices?
- Is the logic correct for all branches?
- Does error handling cover all failure paths?
- Are async operations handled correctly? (race conditions, unresolved promises)
- Are there any infinite loops or missing loop termination conditions?

### 2. Security
Does the code introduce security vulnerabilities?
- **Injection** — SQL injection, XSS, command injection, template injection
- **Authentication/Authorization** — are permissions checked? Can users access others' data?
- **Input validation** — is user input sanitized/validated before use?
- **Secrets** — are credentials, tokens, or keys hardcoded or leaked in logs?
- **Sensitive data** — is PII/sensitive data logged, exposed in errors, or stored insecurely?
- **Dependencies** — are new dependencies vetted for known vulnerabilities?

### 3. Performance
Does the code perform well at scale?
- **N+1 queries** — database queries inside loops
- **Unnecessary computation** — repeated calculations that could be cached
- **Memory leaks** — unreleased resources, growing collections
- **Blocking operations** — sync I/O in async contexts
- **Inefficient data structures** — O(n) lookups where O(1) is possible

### 4. Maintainability
Will this code be easy to understand and change?
- Is the code readable? Would another developer understand it quickly?
- Are variable/function names descriptive and accurate?
- Is there duplication that should be extracted?
- Are functions/methods doing too much? (single responsibility)
- Is complexity appropriate? (avoid over-engineering)
- Are there magic numbers or strings that should be named constants?

### 5. Tests
Is the change adequately tested?
- Are new features covered by tests?
- Are edge cases and error paths tested?
- Are tests meaningful? (not just asserting implementation details)
- Does test coverage actually test the behavior that matters?

### 6. Style and Conventions
Does the code follow team/project conventions?
- Naming conventions (camelCase, snake_case, etc.)
- File and module organization
- Comment style and quality
- Import ordering

## Review Output Format

Structure reviews as:

```
## Summary
[1-3 sentence overview of the change and overall assessment]

## Critical Issues (must fix)
- [issue]: [explanation] [line reference if applicable]
  Suggestion: [how to fix]

## Minor Issues (should fix)
- [issue]: [explanation]
  Suggestion: [how to fix]

## Nits (optional)
- [style/preference items]

## Positives
- [things done well — always include at least one]
```

## Tone and Approach

- **Be specific** — "this could be cleaner" is not useful; explain what and why
- **Explain the why** — don't just flag issues, explain why they matter
- **Suggest, don't dictate** — for style/preference: "consider X" not "do X"
- **Acknowledge good work** — point out what's done well, not just problems
- **Prioritize** — distinguish blocking issues from minor suggestions

## Review Checklist

Before submitting the review, verify:
- [ ] Correctness checked for all code paths
- [ ] Security vulnerabilities checked (injection, auth, input validation, secrets)
- [ ] Performance issues checked (N+1, unnecessary computation)
- [ ] Tests are present and meaningful
- [ ] Variable/function names are clear
- [ ] No debug code, console.logs, or TODOs left in
- [ ] Breaking changes identified
- [ ] Documentation updated if needed

## Common Issues Quick Reference

| Category | Pattern to Flag |
|----------|----------------|
| Security | `eval()`, string concatenation in SQL, `innerHTML =`, hardcoded credentials |
| Performance | Query inside loop, `.find()` in inner loop, sync file I/O |
| Correctness | Missing null check, uncaught promise, off-by-one in slice |
| Maintainability | Function >50 lines, nesting >3 levels, magic number |
| Tests | No error path test, mock returning wrong shape |

## Notes for Claude

- Read the full diff before commenting — context from other changes matters
- Check if tests were updated to cover the change
- Flag security issues as Critical regardless of other context
- If reviewing a PR, understand the PR description and intended goal first
