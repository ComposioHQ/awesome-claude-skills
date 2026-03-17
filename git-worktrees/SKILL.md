---
name: git-worktrees
description: Manage multiple Git working trees to work on multiple branches simultaneously without stashing or switching. Use this skill when the user wants to work on multiple branches at the same time, review code in one branch while developing in another, or set up parallel development workflows.
---

# Git Worktrees

Work on multiple branches simultaneously using `git worktree` — each branch gets its own working directory.

## What is a Worktree?

A Git worktree is an additional working directory linked to the same repository. Each worktree:
- Has its own checked-out branch
- Has its own working directory and index
- Shares the same `.git` object store (efficient — no duplication)

Use case: work on a feature in one worktree while hotfixing in another, without stashing or losing context.

## Core Commands

### List existing worktrees
```bash
git worktree list
```

### Add a new worktree
```bash
# Checkout existing branch into new directory
git worktree add ../feature-branch feature-branch

# Create new branch and worktree together
git worktree add -b new-feature ../new-feature main

# Add worktree at a specific path
git worktree add /path/to/directory branch-name
```

### Remove a worktree
```bash
# After you're done with the worktree
git worktree remove ../feature-branch

# Force remove (if worktree has uncommitted changes)
git worktree remove --force ../feature-branch

# Prune stale worktree references
git worktree prune
```

### Move a worktree
```bash
git worktree move ../old-path ../new-path
```

## Common Workflows

### Workflow 1: Parallel Feature Development

```bash
# Main work: currently on feature-a
cd ~/projects/my-app

# Start working on feature-b in parallel
git worktree add ../my-app-feature-b feature-b

# Open feature-b in editor
code ../my-app-feature-b

# Later, clean up
git worktree remove ../my-app-feature-b
```

### Workflow 2: Hotfix While Feature is In Progress

```bash
# You're deep in feature work — don't stash, use a worktree
git worktree add ../hotfix-123 main

cd ../hotfix-123
git checkout -b hotfix/critical-bug-123

# Fix the bug, commit, push, open PR
git commit -am "fix: resolve critical login bug"
git push origin hotfix/critical-bug-123

# Back to feature work without losing context
cd ../my-app
```

### Workflow 3: Code Review Without Leaving Current Work

```bash
# Review a PR branch without disrupting your work
git fetch origin
git worktree add ../review-pr-456 origin/feature/some-feature

# Review the code in ../review-pr-456
# Run tests, inspect changes

# Clean up after review
git worktree remove ../review-pr-456
```

### Workflow 4: Testing Multiple Versions

```bash
# Compare behavior between main and a branch
git worktree add ../test-main main
git worktree add ../test-feature feature/new-algorithm

# Run both side by side
cd ../test-main && npm test
cd ../test-feature && npm test
```

## Directory Naming Convention

Keep worktrees organized with a consistent naming pattern:
```
~/projects/
  my-app/              # main worktree (primary branch)
  my-app-feature-x/   # feature worktree
  my-app-hotfix/      # hotfix worktree
  my-app-review/      # PR review worktree
```

Or use a subdirectory approach:
```
~/projects/
  my-app/
    .git/
    src/
  worktrees/
    my-app-feature-x/
    my-app-hotfix/
```

## Important Notes

- **One branch per worktree** — you cannot check out the same branch in two worktrees simultaneously
- **Shared objects** — all worktrees share the `.git` database; disk usage is minimal
- **Independent index** — each worktree has its own staging area (index)
- **Node modules / builds** — each worktree needs its own `node_modules`, `.venv`, build artifacts, etc. Run install commands after creating each worktree
- **IDE project files** — some IDEs may need to be opened separately for each worktree

## Cleanup Reminders

Orphaned worktrees (deleted directory without `git worktree remove`) leave stale metadata:
```bash
# Clean up stale references
git worktree prune

# View all worktrees including stale ones
git worktree list --porcelain
```

## Integration with Claude Code

When working in Claude Code across multiple worktrees:
- Each worktree is a separate project directory — open them independently
- Use `git worktree list` to see all active worktrees and their branches
- Prefer worktrees over stashing for context-switch heavy workflows
