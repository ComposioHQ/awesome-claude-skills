# Workflow Diagram

This diagram shows how the three files work together and how hooks interact with them.

---

## Visual Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                    TASK START                                    │
│  User requests a complex task (>5 tool calls expected)          │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
         ┌───────────────────────────────┐
         │  STEP 1: Create task_plan.md │
         │  (NEVER skip this step!)      │
         └───────────────┬───────────────┘
                         │
                         ▼
         ┌───────────────────────────────┐
         │  STEP 2: Create findings.md   │
         │  STEP 3: Create progress.md   │
         └───────────────┬───────────────┘
                         │
                         ▼
    ┌────────────────────────────────────────────┐
    │         WORK LOOP (Iterative)              │
    │                                            │
    │  ┌──────────────────────────────────────┐ │
    │  │  PreToolUse Hook (Automatic)         │ │
    │  │  → Reads task_plan.md before        │ │
    │  │    Write/Edit/Bash operations       │ │
    │  │  → Refreshes goals in attention      │ │
    │  └──────────────┬───────────────────────┘ │
    │                 │                          │
    │                 ▼                          │
    │  ┌──────────────────────────────────────┐ │
    │  │  Perform work (tool calls)          │ │
    │  │  - Research → Update findings.md    │ │
    │  │  - Implement → Update progress.md    │ │
    │  │  - Make decisions → Update both     │ │
    │  └──────────────┬───────────────────────┘ │
    │                 │                          │
    │                 ▼                          │
    │  ┌──────────────────────────────────────┐ │
    │  │  PostToolUse Hook (Automatic)        │ │
    │  │  → Reminds to update task_plan.md   │ │
    │  │    if phase completed               │ │
    │  └──────────────┬───────────────────────┘ │
    │                 │                          │
    │                 ▼                          │
    │  ┌──────────────────────────────────────┐ │
    │  │  After 2 view/browser operations:    │ │
    │  │  → MUST update findings.md           │ │
    │  │    (2-Action Rule)                   │ │
    │  └──────────────┬───────────────────────┘ │
    │                 │                          │
    │                 ▼                          │
    │  ┌──────────────────────────────────────┐ │
    │  │  After completing a phase:            │ │
    │  │  → Update task_plan.md status        │ │
    │  │  → Update progress.md with details   │ │
    │  └──────────────┬───────────────────────┘ │
    │                 │                          │
    │                 ▼                          │
    │  ┌──────────────────────────────────────┐ │
    │  │  If error occurs:                    │ │
    │  │  → Log in task_plan.md               │ │
    │  │  → Log in progress.md                │ │
    │  │  → Document resolution               │ │
    │  └──────────────┬───────────────────────┘ │
    │                 │                          │
    │                 └──────────┐               │
    │                            │               │
    │                            ▼               │
    │              ┌──────────────────────┐     │
    │              │  More work to do?    │     │
    │              └──────┬───────────────┘     │
    │                     │                     │
    │              YES ───┘                     │
    │              │                            │
    │              └──────────┐                 │
    │                         │                 │
    └─────────────────────────┘                 │
                                                 │
                         NO                      │
                         │                       │
                         ▼                       │
         ┌──────────────────────────────────────┐
         │  Stop Hook (Automatic)               │
         │  → Checks if all phases complete     │
         │  → Verifies task_plan.md status      │
         └──────────────┬───────────────────────┘
                         │
                         ▼
         ┌──────────────────────────────────────┐
         │  All phases complete?                │
         └──────────────┬───────────────────────┘
                         │
              ┌──────────┴──────────┐
              │                     │
            YES                    NO
              │                     │
              ▼                     ▼
    ┌─────────────────┐    ┌─────────────────┐
    │  TASK COMPLETE  │    │  Continue work  │
    │  Deliver files  │    │  (back to loop) │
    └─────────────────┘    └─────────────────┘
```

---

## Key Interactions

### Hooks

| Hook | When It Fires | What It Does |
|------|---------------|--------------|
| **SessionStart** | When Claude Code session begins | Notifies skill is ready |
| **PreToolUse** | Before Write/Edit/Bash operations | Reads `task_plan.md` to refresh goals |
| **PostToolUse** | After Write/Edit operations | Reminds to update phase status |
| **Stop** | When Claude tries to stop | Verifies all phases are complete |

### The 2-Action Rule

After every 2 view/browser/search operations, you MUST update `findings.md`.

```
Operation 1: WebSearch → Note results
Operation 2: WebFetch → MUST UPDATE findings.md NOW
Operation 3: Read file → Note findings
Operation 4: Grep search → MUST UPDATE findings.md NOW
```

### Phase Completion

When a phase is complete:

1. Update `task_plan.md`:
   - Change status: `in_progress` → `complete`
   - Mark checkboxes: `[ ]` → `[x]`

2. Update `progress.md`:
   - Log actions taken
   - List files created/modified
   - Note any issues encountered

### Error Handling

When an error occurs:

1. Log in `task_plan.md` → Errors Encountered table
2. Log in `progress.md` → Error Log with timestamp
3. Document the resolution
4. Never repeat the same failed action

---

## File Relationships

```
┌─────────────────────────────────────────────────────────────────┐
│                         task_plan.md                             │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Goal: What you're trying to achieve                    │   │
│  │  Phases: 3-7 steps with status tracking                 │   │
│  │  Decisions: Major choices made                          │   │
│  │  Errors: Problems encountered                           │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                   │
│              PreToolUse hook reads this                         │
│              before every Write/Edit/Bash                       │
└─────────────────────────────────────────────────────────────────┘
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                    │
          ▼                    │                    ▼
┌─────────────────┐            │          ┌─────────────────┐
│   findings.md   │            │          │   progress.md   │
│                 │            │          │                 │
│  Research       │◄───────────┘          │  Session log    │
│  Discoveries    │                       │  Actions taken  │
│  Tech decisions │                       │  Test results   │
│  Resources      │                       │  Error log      │
└─────────────────┘                       └─────────────────┘
```

---

## The 5-Question Reboot Test

If you can answer these questions, your context management is solid:

| Question | Answer Source |
|----------|---------------|
| Where am I? | Current phase in `task_plan.md` |
| Where am I going? | Remaining phases in `task_plan.md` |
| What's the goal? | Goal statement in `task_plan.md` |
| What have I learned? | `findings.md` |
| What have I done? | `progress.md` |

---

## Next Steps

- [Quick Start Guide](quickstart.md) - Step-by-step tutorial
- [Troubleshooting](troubleshooting.md) - Common issues and solutions
