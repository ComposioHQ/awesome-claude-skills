---
name: gsd-plan-phase
description: Run the planning phase of a GSD (Get Stuff Done) workflow — break down a feature or task into a concrete implementation plan before writing code. Use this skill when the user wants to plan how to implement a specific feature, task, or change before starting to code.
---

# GSD: Plan Phase

Transform a feature request or task into a concrete, actionable implementation plan.

## When to Use

Run the plan phase before any significant implementation:
- New features (more than a few lines of code)
- Architectural changes
- Refactors
- Bug fixes that require design decisions

Skip for truly trivial changes (typo fix, one-line change).

## Plan Phase Process

### 1. Understand the Requirement

Re-state the requirement in your own words. Identify:
- **Goal**: What user problem does this solve?
- **Scope**: What's in scope? What's explicitly out of scope?
- **Acceptance criteria**: How will you know it's done?
- **Constraints**: Performance targets, backward compatibility, deadlines

If anything is unclear, ask before planning.

### 2. Explore the Codebase

Before planning the implementation, understand the existing system:
- Where does the change live? Which files/modules?
- What existing code can be reused or extended?
- What are the relevant data models and APIs?
- Are there existing patterns to follow?

```bash
# Find relevant files
grep -r "relevant_term" src/
# or use Glob/search tools
```

### 3. Identify Approach Options

For non-trivial features, consider 2-3 implementation approaches:
- **Option A**: [approach] — pros, cons
- **Option B**: [approach] — pros, cons
- **Recommended**: [which and why]

### 4. Define Implementation Steps

Break the work into concrete, ordered steps. Each step should:
- Be completable in a single focused session
- Have a clear done state
- Be in dependency order (what must happen first?)

**Plan format:**
```
Feature: [name]

Approach: [chosen approach and why]

Steps:
1. [ ] [Specific task] — [files/components affected]
2. [ ] [Specific task] — [files/components affected]
3. [ ] [Write tests for X]
4. [ ] [Update docs/types if needed]

Edge cases to handle:
- [edge case 1]
- [edge case 2]

Open questions:
- [anything that needs decision before or during implementation]
```

### 5. Identify Risks and Unknowns

Flag before starting:
- **Breaking changes**: Will this affect existing functionality?
- **Dependencies**: Does this require other changes first?
- **Assumptions**: What are you assuming is true?
- **Unknowns**: What might you discover that changes the plan?

### 6. Estimate Complexity

Tag each plan with complexity:
- **S** (Small): <2 hours, straightforward
- **M** (Medium): 2-8 hours, some complexity
- **L** (Large): 1-3 days, significant work
- **XL** (X-Large): 3+ days, consider breaking down further

XL tasks should be broken into multiple M or L tasks.

## Output Format

Produce a plan document like:

```
# Plan: [Feature Name]

**Goal:** [one sentence]
**Complexity:** M
**Branch:** feature/[name]

## Approach
[1-2 paragraphs explaining the implementation approach]

## Steps
1. [ ] Set up [X] in [file]
2. [ ] Implement [Y] — extends existing [Z]
3. [ ] Add tests for [scenarios]
4. [ ] Update [types/docs/API]

## Files to Change
- `src/components/Foo.tsx` — add new prop
- `src/api/bar.ts` — new endpoint
- `tests/foo.test.ts` — new test cases

## Edge Cases
- Empty state
- Error state
- Concurrent requests

## Open Questions
- [ ] Should X be configurable or hardcoded?
```

## Transition to Execute Phase

After the plan is approved:
1. Create a feature branch: `git checkout -b feature/[name]`
2. Use `gsd-execute-phase` skill to work through the steps
3. Check off steps as completed
