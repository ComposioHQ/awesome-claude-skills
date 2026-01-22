---
name: open-source-contribution
description: Guides developers through open source contributions including finding projects, writing PRs, conventional commits, and communicating with maintainers. Covers enterprise standards (Linux Kernel, Apache) and security disclosure. Use when contributing to GitHub/GitLab projects, writing commit messages, responding to code review, or reporting vulnerabilities.
---

# Contributing to Open Source

## Quick Navigation

| Topic | Description |
|-------|-------------|
| [Finding Projects](#finding-projects) | Resources and labels for finding issues |
| [Understanding Codebases](#understanding-large-codebases) | How to navigate unfamiliar code |
| [Writing PRs](#writing-effective-pull-requests) | Branch strategy, commits, descriptions |
| [Code Review](#responding-to-code-review) | How to handle feedback |
| [Communicating with Maintainers](#communicating-with-maintainers) | Principles and templates |
| [Maintainer Perspective](#understanding-maintainer-perspective) | What maintainers want |
| [Common Mistakes](#common-mistakes-to-avoid) | Anti-patterns to avoid |
| [What Counts as Meaningful](#what-counts-as-meaningful) | High-value contributions |

**Reference Files:**
- [Conventional Commits](reference/conventional-commits.md) - Complete commit message guide
- [Enterprise Practices](reference/enterprise-practices.md) - Linux Kernel, Apache standards
- [Security Disclosure](reference/security-disclosure.md) - Reporting vulnerabilities

**Templates:**
- [Pull Request Template](templates/pull-request.md)
- [Bug Report Template](templates/bug-report.md)
- [Feature Request Template](templates/feature-request.md)
- [Commit Messages Reference](templates/commit-messages.md)

---

## Finding Projects

### Resources

- **GitHub Contribute Page**: `github.com/<owner>/<repo>/contribute`
- [Good First Issue](https://goodfirstissue.dev/)
- [Up For Grabs](https://up-for-grabs.net/)
- [First Timers Only](https://www.firsttimersonly.com/)
- **GitHub Search**: `label:"good first issue" language:<your-language>`

### Labels to Look For

| Label | Meaning |
|-------|---------|
| `good first issue` | GitHub's official beginner label |
| `first-timers-only` | Reserved for first-time contributors |
| `help wanted` | Maintainers actively seeking help |
| `documentation` | Often good entry points |

### Evaluating a Project

Before contributing, verify:
- Has an OSI-approved open source license
- Recent commits (within last 3 months)
- Maintainers respond to issues/PRs
- Has CONTRIBUTING.md or contribution guidelines
- Automated tests (CI/CD) exist

---

## Understanding Large Codebases

### Step 1: Documentation First

Read in order: README.md → CONTRIBUTING.md → Architecture docs → API docs

### Step 2: Build and Run Locally

```bash
git clone https://github.com/<owner>/<repo>.git
cd <repo>
# Follow setup instructions, run tests
```

### Step 3: Explore Strategically

**Find important files**:
```bash
git log --pretty=format: --name-only | sort | uniq -c | sort -rg | head -20
```

**Understand entry points**: Look for `main`, `index`, `app`, or `server` files.

**Read tests**: They document expected behavior and show component usage.

### Step 4: Focus on Your Target

Don't try to understand everything:
1. Identify the module related to your issue
2. Read that module thoroughly
3. Trace dependencies one level up and down
4. Treat unrelated code as "black boxes"

### Step 5: Use Git as Documentation

```bash
git log --oneline <file>           # File history
git log --grep="<keyword>"         # Find relevant PRs
git blame <file>                   # Who to ask
```

---

## Writing Effective Pull Requests

### Before You Start

1. **Claim the issue**: Comment to let maintainers know you're working on it
2. **Ask questions**: If requirements are unclear, ask before coding
3. **Check for duplicates**: Search existing PRs

### Forking Workflow

For projects where you don't have write access:

```bash
# 1. Fork on GitHub, then clone your fork
git clone https://github.com/YOUR-USERNAME/<repo>.git
cd <repo>

# 2. Add upstream remote
git remote add upstream https://github.com/ORIGINAL-OWNER/<repo>.git

# 3. Keep fork updated
git fetch upstream
git checkout main
git merge upstream/main

# 4. Create feature branch and work
git checkout -b fix/your-fix
# ... make changes ...
git push origin fix/your-fix

# 5. Open PR from your fork to upstream
```

### Branch Strategy

```bash
git checkout -b <type>/<short-description>

# Examples:
git checkout -b fix/null-pointer-exception
git checkout -b feat/add-dark-mode
git checkout -b docs/update-readme
```

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>[scope]: <description>

[optional body]

[optional footer]
```

**Quick reference**:

| Type | Use For |
|------|---------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation |
| `refactor` | Code restructure |
| `test` | Tests |
| `chore` | Maintenance |

**Example**:
```
fix(auth): resolve token refresh race condition

Fixes #123
```

For complete guide: See [reference/conventional-commits.md](reference/conventional-commits.md)

### PR Description Template

```markdown
## Summary
Brief description of what this PR does and why.

## Changes
- Change 1
- Change 2

## Related Issues
Fixes #123

## Testing
- [ ] Existing tests pass
- [ ] Added new tests
- [ ] Manually tested
```

### PR Sizing Best Practices

Research shows smaller PRs get better reviews:

| Size | Lines Changed | Review Quality |
|------|---------------|----------------|
| Ideal | ~50 lines | Thorough review |
| Good | <200 lines | Good feedback |
| Acceptable | <400 lines | Adequate review |
| Too Large | 400+ lines | Likely to miss issues |

### PR Best Practices

- **One concern per PR**: Don't mix features, fixes, and refactors
- **Self-review first**: Read your own diff before requesting review
- **Use draft PRs**: Open early for feedback on approach
- **Include tests**: Maintainers rarely merge untested code
- **Respond promptly**: Don't let PRs go stale

### What NOT to Include in PRs

Remove before committing:
- `.env`, `.env.local`, credentials, API keys
- IDE/editor configs (`.idea/`, `.vscode/` unless project-standard)
- Personal notes, TODOs, planning files
- Debug code, console.logs, print statements
- Unrelated formatting changes
- Large binary files, screenshots (unless required)

**Check for secrets before pushing:**
```bash
# Search for common secret patterns
git diff --cached | grep -iE "(api_key|password|secret|token).*="
```

### GitHub CLI Essentials

```bash
# Create PR interactively
gh pr create

# Create PR with title and body
gh pr create --title "Fix: resolve null pointer" --body "Fixes #123"

# Create draft PR
gh pr create --draft

# Check PR status
gh pr status

# View PR in browser
gh pr view --web
```

---

## Responding to Code Review

### Mindset

Code review is collaborative, not adversarial. Reviewers want to help improve the code.

### Response Templates

**When you agree**:
```
Good catch! Fixed in [commit hash].
```

**When you need clarification**:
```
I want to make sure I understand—are you suggesting [X] because of [Y]?
```

**When you disagree**:
```
I went with [current approach] because:
- [Reason 1]
- [Reason 2]

Open to changing if you think [alternative] better serves the project.
```

**When asked for big changes**:
```
Great suggestion. Would it make sense to address this in a follow-up PR?
```

### Guidelines

- Address all comments
- Stay calm—step away if frustrated
- Re-request review after addressing feedback

---

## Communicating with Maintainers

### Principles

- Keep communication public (others benefit)
- Be concise (maintainers have limited time)
- Do homework first (search existing issues)
- Be patient (follow up after one week, politely)

### Bug Report Template

```markdown
## Description
Clear description of the bug.

## Steps to Reproduce
1. Step 1
2. Step 2
3. See error

## Expected vs Actual Behavior
Expected: X
Actual: Y

## Environment
- OS: [e.g., macOS 14.0]
- Version: [e.g., v2.1.0]
```

### Feature Request Template

```markdown
## Summary
What you're proposing.

## Problem
What problem this solves.

## Proposed Solution
How you envision it working.

## Alternatives Considered
Other approaches you considered.
```

---

## Understanding Maintainer Perspective

### What Maintainers Deal With

- **Overwhelm**: Popular projects receive hundreds of issues/PRs
- **Volunteer work**: Most maintainers aren't paid
- **Burnout**: Endless notifications and demanding users
- **Quality gates**: Must protect codebase from bugs and technical debt

### What Maintainers Want

1. Contributors who read the docs first
2. Well-tested code
3. Clear communication about what and why
4. Patience (days or weeks to respond is normal)
5. Follow-through (don't abandon PRs mid-review)

### Quotes from Experienced Maintainers

> "The best good first issue is the one you created yourself. Try going through the product, and in the process of testing and understanding it, you'll find your good first issue."

> "All the projects I've contributed to are things I've used in some way. I never saw the point of just 'showing up' to a project."

---

## Common Mistakes to Avoid

### Before Starting

1. **Skipping CONTRIBUTING.md**: Always read contribution guidelines first
2. **Not checking existing work**: Search PRs/issues for duplicates
3. **Working on assigned issues**: Check if someone is already on it
4. **Building unsolicited features**: Propose in an issue first, wait for approval
5. **Not understanding the project**: Use it before contributing to it

### During Development

6. **Working on main branch**: Always use feature branches
7. **Giant PRs**: Break into smaller, focused PRs (<200 lines ideal)
8. **No tests**: Maintainers rarely merge untested code
9. **Including secrets**: Check for API keys, passwords, tokens
10. **Committing debug code**: Remove console.logs and print statements

### When Submitting

11. **Vague PR titles**: Be specific (not "Fixed bug" but "Fix null pointer in auth handler")
12. **Ignoring templates**: Use provided issue/PR templates
13. **Ignoring CI failures**: Fix all failing checks before requesting review
14. **No description**: Explain what, why, and how to test

### After Submitting

15. **Going silent**: Respond to feedback within 48 hours
16. **Arguing in reviews**: Stay collaborative, assume good intent

### Low-Value Contributions

- Adding your name to README files
- Trivial changes (typo fixes in comments nobody reads)
- "Drive-by" contributions with no intention to follow through
- Opening issues that are already documented

---

## What Counts as Meaningful

### High-Value

- Bug fixes with tests
- Documentation that helps new users
- Test coverage for untested code paths
- Performance improvements with benchmarks
- Security fixes (reported responsibly)
- Triaging issues: Reproducing bugs, closing duplicates

### Best Strategy

1. **Use the project first**: Become a real user before contributing
2. **Solve your own problems**: Fix bugs you encounter
3. **Think long-term**: Build relationships, not just contribution counts
4. **Quality over quantity**: One thoughtful PR beats ten trivial ones

---

## External References

### Official Guides
- [GitHub Open Source Guide](https://opensource.guide/how-to-contribute/)
- [Conventional Commits v1.0.0](https://www.conventionalcommits.org/en/v1.0.0/)
- [Google Engineering Practices](https://google.github.io/eng-practices/review/)

### Finding Projects
- [Good First Issue](https://goodfirstissue.dev/)
- [First Timers Only](https://www.firsttimersonly.com/)
- [Up For Grabs](https://up-for-grabs.net/)
- [CodeTriage](https://www.codetriage.com/)

### Community Insights
- [7 Common Mistakes New Contributors Make](https://dev.to/codergirl1991/7-common-mistakes-new-contributors-make-in-open-source-software-2noo)
- [Lessons from Reviewing 200+ PRs](https://bhupesh.me/hacktoberfest-pr-review/)
- [Nadia Eghbal - Working in Public](https://press.stripe.com/working-in-public)
