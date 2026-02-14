# Commit Message Reference

Quick reference for writing conventional commit messages based on [Conventional Commits v1.0.0](https://www.conventionalcommits.org/en/v1.0.0/).

## Format

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

## Types

| Type       | Description                                      | SemVer Bump |
|------------|--------------------------------------------------|-------------|
| `feat`     | Add, adjust, or remove a feature                 | **MINOR**   |
| `fix`      | Fix a bug                                        | **PATCH**   |
| `docs`     | Documentation only changes                       | None        |
| `style`    | Formatting, whitespace (no code change)          | None        |
| `refactor` | Restructure code without changing behavior       | None        |
| `perf`     | Performance improvements                         | None        |
| `test`     | Add or correct tests                             | None        |
| `build`    | Build system or external dependencies            | None        |
| `ci`       | CI/CD configuration                              | None        |
| `ops`      | Infrastructure, deployment, monitoring           | None        |
| `chore`    | Maintenance tasks (e.g., .gitignore)             | None        |
| `revert`   | Revert a previous commit                         | Depends     |

## Rules

1. **Imperative mood**: "add" not "added" or "adds"
2. **Lowercase**: Start description with lowercase (after colon)
3. **No period**: Don't end description with a period
4. **50/72 rule**: Subject line ≤50 chars, body wrapped at 72 chars
5. **Blank line**: Separate subject from body with blank line

## Scope

Scope provides context about what section of the codebase is affected:

```
feat(parser): add ability to parse arrays
fix(auth): resolve token refresh race condition
```

**Common scopes** (project-specific):
- Component names: `auth`, `parser`, `api`, `ui`
- Modules: `core`, `utils`, `config`
- Features: `login`, `search`, `export`

**Rules**:
- Optional but recommended for larger projects
- Should be a noun describing the section
- Don't use issue identifiers as scopes

## Breaking Changes

Breaking changes trigger a **MAJOR** version bump.

**Two ways to indicate breaking changes**:

### 1. Exclamation mark notation
```
feat!: remove deprecated endpoints

feat(api)!: change authentication flow
```

### 2. Footer notation
```
feat(api): change response format

BREAKING CHANGE: Response now returns nested object.
Previously { name, email }. Now { user: { name, email } }.
```

**BREAKING CHANGE rules**:
- Must be uppercase
- `BREAKING-CHANGE` (with hyphen) is also valid
- Can be combined with `!` notation
- Can span multiple lines

## Examples

### Simple fix
```
fix: prevent crash when input is empty
```

### Feature with scope
```
feat(auth): add OAuth2 login support
```

### With body
```
fix(parser): handle nested arrays correctly

The previous implementation failed when arrays contained
more than 3 levels of nesting. This fix recursively
processes all nesting levels.
```

### With issue reference
```
fix(api): return 404 for missing resources

Previously returned 500 which confused error handling
on the client side.

Fixes #123
```

### Breaking change (exclamation)
```
feat(api)!: change authentication endpoint

The /auth endpoint now requires a JSON body instead of
form data.

BREAKING CHANGE: Update all clients to send
Content-Type: application/json header.

Closes #456
```

### Multiple issues
```
fix(validation): improve email regex pattern

- Added support for plus addressing (user+tag@domain.com)
- Fixed false positives for domains with hyphens
- Added comprehensive test cases

Fixes #101
Fixes #102
Related to #99
```

### Revert
```
revert: feat(auth): add OAuth2 login with Google

This reverts commit abc1234def5678.

Reason: Causing issues with existing SSO customers.
```

## Footer Keywords

| Keyword            | Effect                              |
|--------------------|-------------------------------------|
| `Fixes #N`         | Closes issue N when PR is merged    |
| `Closes #N`        | Closes issue N when PR is merged    |
| `Resolves #N`      | Closes issue N when PR is merged    |
| `Related to #N`    | Links to issue without closing      |
| `Reviewed-by`      | Credit reviewers                    |
| `Refs`             | Reference commits/issues            |
| `BREAKING CHANGE:` | Marks as breaking (**MAJOR** bump)  |

## Anti-Patterns

Avoid these common mistakes:

```
# Too vague
fix: fix bug                          # What bug?

# Past tense (should be imperative)
feat: added new feature               # Use "add"

# Capitalized (should be lowercase)
Fix: Handle null input                # Lowercase after colon

# With period
fix: resolve issue.                   # Remove the period

# Too long (>50 chars in subject)
feat(authentication-system): add comprehensive OAuth2 support with refresh tokens

# No type
update readme with new instructions   # Add type: "docs: ..."

# Mixing concerns (one commit = one change)
feat: add login and fix header and update docs
```

## Tooling

- **[commitlint](https://commitlint.js.org/)**: Lint commit messages
- **[commitizen](https://commitizen-tools.github.io/commitizen/)**: Interactive CLI
- **[husky](https://typicode.github.io/husky/)**: Git hooks
- **[semantic-release](https://semantic-release.gitbook.io/)**: Automate versioning
