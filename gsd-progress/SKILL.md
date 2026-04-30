---
name: gsd-progress
description: Track and report progress on a GSD (Get Stuff Done) workflow — show what's done, what's in progress, and what's next. Use this skill when the user wants a status update on their current task or project, or needs to see where they are in a plan.
---

# GSD: Progress

Surface a clear, actionable progress snapshot of the current GSD workflow.

## Progress Report Format

When asked for progress, produce a report like:

```
## Progress: [Feature/Task Name]

**Status:** In Progress | Blocked | Review | Done
**Completed:** X/Y steps

### ✅ Done
- [Step 1] — [brief note if relevant]
- [Step 2]

### 🔄 In Progress
- [Current step] — [what's happening]

### ⏳ Up Next
- [Next step]
- [Step after that]

### ❌ Blocked
- [Blocked step] — [what's blocking it]

### 📝 Notes / Deviations from Plan
- [Any changes from original plan]
- [Decisions made]
- [Open questions]

### Next Action
[Single most important thing to do right now]
```

## How to Assess Progress

To generate an accurate progress report:

1. **Review the plan** — re-read the original plan steps
2. **Check completed work** — review git commits, file changes
3. **Check test status** — are tests passing?
4. **Identify blockers** — what (if anything) is stopping progress?
5. **Update the plan** — mark completed steps, flag new issues

```bash
# Review recent commits
git log --oneline -10

# See what files have changed
git diff --stat HEAD~5 HEAD

# Check test status
npm test 2>&1 | tail -20
```

## Keeping Progress Visible

Update progress inline in the plan document:

```
Steps:
1. [x] Initialize database schema — done
2. [x] Create API endpoint — done
3. [~] Add authentication — 50% done (middleware done, tests pending)
4. [ ] Write integration tests
5. [ ] Update API documentation
```

Legend:
- `[x]` — Done
- `[~]` — In progress
- `[ ]` — Not started
- `[!]` — Blocked

## When Progress is Stalled

If progress has stalled:
1. Identify the exact stall point
2. Determine if it's a blocker (external) or a struggle (internal)
3. For blockers: escalate or work around
4. For struggles: break the step into smaller sub-steps, get help

## End of Session Summary

At the end of a work session, produce a summary:

```
## Session Summary

**Time:** [duration]
**Completed today:** [list]
**State:** [where things stand]
**Next session start:** [exactly what to pick up with]
**Open questions:** [anything that needs a decision]
```

This makes it easy to resume work without context loss.
