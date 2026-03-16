---
name: gsd-execute-phase
description: Execute a planned implementation — work through steps systematically, write code, run tests, and ship. Use this skill when the user has a plan (from gsd-plan-phase or similar) and is ready to implement it, or wants help executing a specific implementation task.
---

# GSD: Execute Phase

Work through an implementation plan systematically to produce working, tested code.

## Before Starting

Ensure there's a clear plan. If not, use `gsd-plan-phase` first. At minimum, know:
- What feature/change is being implemented?
- What are the steps?
- What files need to change?

## Execution Principles

- **One step at a time** — complete each step before moving to the next
- **Run tests frequently** — catch regressions early
- **Commit incrementally** — small, logical commits (not one giant commit at the end)
- **Don't scope-creep** — if you notice unrelated improvements, note them but don't do them now

## Execution Loop

For each step in the plan:

```
1. Read the relevant existing code
2. Implement the change
3. Run tests → fix if failing
4. Commit with a clear message
5. Mark the step done
6. Move to next step
```

## Step Execution Pattern

### Before writing code for each step:
- Re-read the plan step
- Read the files that will change
- Understand the existing patterns (follow them)
- Confirm the approach is still correct given what you've learned

### While writing code:
- Follow existing code style and patterns
- Write the simplest code that works
- Handle error cases
- Add/update types

### After writing code:
```bash
# Run tests
npm test
# or
pytest

# Run linter
npm run lint
# or
ruff check .

# Check types
npx tsc --noEmit
# or
mypy src/
```

### Commit pattern:
```bash
git add [specific files]
git commit -m "type: description"
```

Commit types: `feat`, `fix`, `refactor`, `test`, `chore`, `docs`

## Handling Blockers

If a step is blocked:
1. **Try to unblock** — investigate the issue, check docs, look for similar patterns
2. **Note the blocker** — write down what's blocking and what was tried
3. **Continue with other steps** if the blocker doesn't affect them
4. **Escalate** — if completely stuck, pause and ask/research

Never silently skip a step. Always explicitly note what was done and why.

## Progress Tracking

Use the `gsd-progress` skill to track which steps are done. Update the plan:
```
Steps:
1. [x] Set up X — done
2. [x] Implement Y — done
3. [ ] Add tests — IN PROGRESS
4. [ ] Update docs
```

## Testing Strategy During Execution

After each logical unit of work:
- Run the existing test suite — ensure no regressions
- Add tests for new behavior before or immediately after implementing it
- Test the happy path first, then edge cases

## Pre-Completion Checklist

Before calling a feature "done":
- [ ] All plan steps completed
- [ ] All tests pass
- [ ] Linter passes
- [ ] Types check out
- [ ] No debug code or console.logs left in
- [ ] Error cases handled
- [ ] README or docs updated if needed
- [ ] PR description written (if opening a PR)

## Git Workflow During Execution

```bash
# Start on a feature branch
git checkout -b feature/my-feature

# Commit often
git add src/specific-file.ts tests/specific-file.test.ts
git commit -m "feat: add X functionality"

# Push to remote regularly
git push origin feature/my-feature

# When done, open PR
gh pr create --title "feat: add X functionality" --body "..."
```

## Notes for Claude

- Read files before editing them — never make blind edits
- Prefer editing existing patterns over introducing new ones
- If the implementation diverges from the plan, note the deviation and why
- When multiple implementation steps are independent, they can be done in parallel (multiple file edits in one turn)
