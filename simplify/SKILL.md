---
name: simplify
description: Review recently changed code for reuse, quality, and efficiency — then fix any issues found. Use this skill when the user wants to simplify or improve code they just wrote, or asks for a quality pass on their changes.
---

# Simplify

Review changed code for quality, then apply targeted improvements.

## When to Use

Use after writing or changing code when:
- The user asks to "simplify this" or "clean this up"
- Code was written quickly and needs a quality pass
- Refactoring opportunities are visible but not worth a full rewrite

## Review Checklist

Run through this checklist on the changed code:

### Duplication
- [ ] Is similar logic repeated that could be extracted into a function?
- [ ] Are there copy-pasted blocks that differ only in a variable?
- [ ] Could a loop or `.map()` replace repeated statements?

### Complexity
- [ ] Is there nesting deeper than 3 levels that could be flattened?
- [ ] Could early returns reduce nesting (guard clauses)?
- [ ] Is there a simpler algorithm or built-in that achieves the same result?
- [ ] Are there unnecessary variables or intermediate values?

### Naming
- [ ] Do variable and function names clearly describe what they hold/do?
- [ ] Are there single-letter variables (outside loops/lambdas) that should be named?
- [ ] Are there misleading names (e.g., `data`, `result`, `temp`)?

### Reuse
- [ ] Does this reimplement something that already exists in the codebase?
- [ ] Does this reimplement a standard library function?
- [ ] Could an existing utility or helper be used?

### Efficiency
- [ ] Are there unnecessary loops (O(n²) where O(n) is possible)?
- [ ] Are expensive operations repeated inside a loop that could be hoisted?
- [ ] Are there unnecessary re-renders or recomputations?

### Dead Code
- [ ] Are there unused variables or imports?
- [ ] Are there commented-out code blocks that should be removed?
- [ ] Are there debug `console.log` / `print` statements left in?

## Fix Strategy

For each issue found:
1. Make the smallest change that addresses it
2. Verify the behavior is unchanged (run tests if available)
3. Don't refactor parts of the code that weren't changed

## Output Format

Present improvements as:

```
## Simplification Review

### Issues Found

**Duplication** (lines 12-24, 40-52):
The same validation logic is repeated. Extracted into `validateInput()`.

**Naming** (line 8):
`d` renamed to `dueDate` for clarity.

**Dead code** (line 67):
Removed commented-out code block.

### Changes Applied
[List of specific changes made]

### Not Changed
[Note anything that could be improved but was left alone to stay in scope]
```

## Scope Boundaries

Only modify:
- The code the user recently changed (not the whole file)
- Code directly related to the user's change

Do not:
- Refactor unrelated code
- Change architecture or add features
- Add error handling for scenarios not in scope
- Add comments or docstrings unless the logic is non-obvious
