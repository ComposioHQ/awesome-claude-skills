# Conventional Commits Reference

Complete guide to the [Conventional Commits v1.0.0](https://www.conventionalcommits.org/en/v1.0.0/) specification.

## Format

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

## Types

| Type | Description | SemVer Impact |
|------|-------------|---------------|
| `feat` | Add, adjust, or remove a feature | **MINOR** bump |
| `fix` | Fix a bug | **PATCH** bump |
| `docs` | Documentation only changes | None |
| `style` | Code style (whitespace, formatting, semicolons) | None |
| `refactor` | Restructure code without changing behavior | None |
| `perf` | Performance improvements | None |
| `test` | Add or correct tests | None |
| `build` | Build tools, dependencies, project version | None |
| `ci` | CI/CD configuration changes | None |
| `chore` | Maintenance (e.g., .gitignore updates) | None |
| `revert` | Revert a previous commit | Depends |

## Scope

Provides context about what section of the codebase is affected:

```
feat(parser): add ability to parse arrays
fix(auth): resolve token refresh race condition
```

**Rules**: Optional, noun describing the section (e.g., `api`, `auth`, `parser`), don't use issue identifiers.

## Description

- **Required** - immediately follows colon and space
- **Imperative, present tense**: "add" not "added"
- **No capitalization** of first letter
- **No period** at end
- **Under 50 characters**

## Body

- **Optional** - separated by blank line
- Explain **what** and **why**, not how
- Wrap at **72 characters**

## Footer

| Token | Purpose | Example |
|-------|---------|---------|
| `Fixes` | Closes issue when merged | `Fixes #123` |
| `Closes` | Closes issue when merged | `Closes #456` |
| `Resolves` | Closes issue when merged | `Resolves #789` |
| `Related to` | Links without closing | `Related to #101` |
| `Reviewed-by` | Credit reviewers | `Reviewed-by: Name` |
| `BREAKING CHANGE` | Documents breaking change | See below |

## Breaking Changes

Triggers **MAJOR** version bump. Two ways to indicate:

**1. Exclamation mark**:
```
feat!: remove deprecated endpoints
feat(api)!: change authentication flow
```

**2. Footer notation**:
```
feat(api): change response format

BREAKING CHANGE: Response now returns nested object.
```

## Examples

**Simple fix**:
```
fix: prevent null pointer when config is missing
```

**Feature with scope**:
```
feat(auth): add OAuth2 login with Google provider
```

**With body and footer**:
```
fix(parser): handle deeply nested arrays

The previous implementation failed with stack overflow
when arrays exceeded 10 levels of nesting.

Fixes #892
```

**Breaking change**:
```
feat(api)!: migrate to v2 authentication

Replaced session-based auth with JWT tokens.

BREAKING CHANGE: Requires Bearer token in Authorization header.
Session cookies no longer supported.

Fixes #234
```

**Revert**:
```
revert: feat(auth): add OAuth2 login

This reverts commit abc1234.
Reason: Causing issues with SSO customers.
```

## Common Mistakes

```
fix: fix bug                    # Too vague
feat: added new feature         # Past tense (use "add")
Fix: Handle null input          # Capitalized after colon
docs: update readme.            # Period at end
update readme                   # Missing type
feat: add login and fix header  # Mixing concerns
```

## Tooling

- [commitlint](https://commitlint.js.org/) - Lint commit messages
- [commitizen](https://commitizen-tools.github.io/commitizen/) - Interactive CLI
- [husky](https://typicode.github.io/husky/) - Git hooks
- [semantic-release](https://semantic-release.gitbook.io/) - Automated versioning
