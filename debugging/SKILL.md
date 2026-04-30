---
name: debugging
description: Systematically diagnose and fix bugs, errors, and unexpected behavior in code. Use this skill when the user has a bug, error message, unexpected behavior, or broken code that needs investigation and resolution.
---

# Debugging

Systematically diagnose and resolve bugs using structured investigation rather than random trial and error.

## Debugging Philosophy

Debugging is hypothesis-driven. Each step should:
1. Form a hypothesis about the root cause
2. Design a minimal test to confirm or refute it
3. Act on the result — fix or form the next hypothesis

Avoid random changes. Each change should test a specific hypothesis.

## Step 1: Understand the Bug

Before touching code, gather complete information:

- **What is the expected behavior?**
- **What is the actual behavior?**
- **When does it happen?** Always? Under specific conditions?
- **When did it start?** After a recent change? Always present?
- **What's the error?** Exact error message, stack trace, log output
- **What's the environment?** OS, runtime version, dependencies, config

Ask the user for any missing context before guessing.

## Step 2: Reproduce the Bug

Always reproduce before fixing:
- Find the minimal reproduction case
- Confirm the bug is reproducible consistently
- Rule out environment-specific issues (works on my machine?)
- If flaky: identify the conditions that trigger it

## Step 3: Locate the Source

Narrow down where the bug lives:

**Read the error message carefully:**
- Stack traces point to the line — but the bug may be higher up the call stack
- Error types (TypeError, KeyError, etc.) hint at the category of problem

**Bisect the problem:**
- Comment out / disable sections to isolate the faulty component
- Use binary search on recent commits if regression: `git bisect`
- Add logging/print statements to trace execution flow

**Check common culprits first:**
- Off-by-one errors in loops/indices
- Null/undefined/None not handled
- Type mismatches (string vs int, etc.)
- Async/timing issues (race conditions, unresolved promises)
- Scope issues (variable shadowing, closures)
- Mutation of shared state
- Wrong assumptions about external data shape

## Step 4: Fix and Verify

Once the root cause is identified:
1. Write the fix — targeted and minimal; avoid refactoring while debugging
2. Verify the original bug is gone with the reproduction case
3. Check for regressions — does anything else break?
4. Consider edge cases: what related inputs might also fail?

## Step 5: Document

After fixing:
- Add a comment explaining WHY the fix works (not just what it does)
- Add a test that would have caught this bug
- Note if there are related areas that might have the same issue

## Debugging Tools by Context

**JavaScript/TypeScript:**
```js
console.log(), console.error(), console.trace()
debugger; // pause in browser/Node
// Chrome DevTools, VS Code debugger
```

**Python:**
```python
print(), logging.debug()
import pdb; pdb.set_trace()  # or breakpoint() in Python 3.7+
# VS Code debugger, pdb, ipdb
```

**Git bisect (for regressions):**
```bash
git bisect start
git bisect bad HEAD
git bisect good <last-known-good-commit>
# Run tests, mark good/bad, git will find the culprit commit
```

## Common Bug Patterns

| Symptom | Likely Cause |
|---------|-------------|
| Works sometimes, fails sometimes | Race condition, async issue, flaky dependency |
| Only fails on specific input | Edge case, boundary condition |
| Fails only in production | Environment difference, missing config, different data |
| Was working, now broken | Recent change introduced regression |
| Wrong output, no error | Logic error, wrong algorithm, off-by-one |
| Correct output but crash later | Side effect, state mutation |

## Notes for Claude

- Read the full stack trace — the error origin is often not where the exception is thrown
- If the user has tried things already, ask what they tried — avoid repeating dead ends
- Never guess and apply multiple changes at once — test one hypothesis at a time
- If unable to reproduce locally, ask the user to add logging/print statements and share output
