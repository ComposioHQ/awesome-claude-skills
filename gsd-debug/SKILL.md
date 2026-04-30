---
name: gsd-debug
description: Run a focused GSD (Get Stuff Done) debugging session — identify the root cause of a specific bug and fix it systematically. Use this skill when actively working through a bug with a clear reproduce case, within a larger GSD workflow.
---

# GSD: Debug

Run a focused debugging session to identify and fix a specific bug.

## Quick Debug Process

This is a streamlined version of full debugging, optimized for speed within a GSD workflow.

### Phase 1: Lock Down the Bug (2-5 min)

Answer these before touching code:
1. **What is the exact error?** (message, stack trace, screenshot)
2. **What is the expected behavior?**
3. **Can you reproduce it consistently?** If not, what are the conditions?
4. **When did it start?** (recent change? always existed?)

```bash
# If it's a regression, find the culprit commit fast
git log --oneline -20
git bisect start
git bisect bad HEAD
git bisect good <last-known-good>
```

### Phase 2: Locate (5-10 min)

**Read the stack trace top-to-bottom.** The error message usually tells you exactly where.

```bash
# Find relevant code
grep -rn "functionName\|ErrorType\|error message" src/

# Check recent changes to relevant files
git log --oneline src/relevant-file.ts
git diff HEAD~3 src/relevant-file.ts
```

Add targeted logging to trace execution:
```js
console.log('[DEBUG] variable:', JSON.stringify(variable, null, 2))
```

```python
print(f"[DEBUG] variable: {variable!r}")
```

### Phase 3: Fix (5-15 min)

Once the root cause is known:
1. Write the smallest possible fix
2. Test the exact reproduction case
3. Remove all debug logging
4. Run the full test suite

```bash
npm test
# or pytest
```

### Phase 4: Commit

```bash
git add [specific files]
git commit -m "fix: [what was broken and why]"
```

## Common Bug Patterns (Quick Reference)

| Error | First thing to check |
|-------|---------------------|
| `TypeError: Cannot read properties of undefined` | Null check missing; trace where value comes from |
| `KeyError` / `AttributeError` (Python) | Check dict keys exist; check object shape |
| `404 Not Found` | API route path, trailing slash, method (GET vs POST) |
| Test passes locally, fails in CI | Environment variable missing, timezone difference, hardcoded path |
| Works once, breaks on retry | State not reset between calls; mutation of shared object |
| `CORS error` | Backend missing CORS headers for that origin |
| Async operation completes but result not used | Missing `await`, unhandled promise |

## If Stuck After 15 Minutes

Stop guessing. Do one of:
1. **Rubber duck** — explain the bug out loud step by step
2. **Minimal reproduction** — strip everything down to the smallest failing case
3. **Check git blame** — who changed the relevant code last?
4. **Search the error message** — exact message in quotes + technology name
5. **Ask for help** — provide: expected behavior, actual behavior, code, what was tried

## After Fixing

- Add a test that would have caught this bug
- Check if the same pattern exists elsewhere: `grep -rn "same-pattern" src/`
- Note in the commit message what caused the bug (helps future you)
