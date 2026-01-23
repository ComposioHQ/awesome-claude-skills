# Examples: Planning with Files in Action

This directory contains real-world examples showing how the 3-file planning pattern works in practice.

## Example: Building a Todo App

This walkthrough demonstrates a complete task from start to finish, showing how `task_plan.md`, `findings.md`, and `progress.md` evolve together.

### The Task

**User Request:** "Build a simple command-line todo app in Python that can add, list, and delete tasks."

---

## Phase 1: Initial Planning (Task Start)

### task_plan.md (Initial State)

```markdown
# Task Plan: Build Command-Line Todo App

## Goal
Create a Python CLI todo app with add, list, and delete functionality.

## Current Phase
Phase 1

## Phases

### Phase 1: Requirements & Discovery
- [ ] Understand user intent
- [ ] Identify constraints and requirements
- [ ] Document findings in findings.md
- **Status:** in_progress

### Phase 2: Planning & Structure
- [ ] Define technical approach
- [ ] Create project structure
- [ ] Document decisions with rationale
- **Status:** pending

### Phase 3: Implementation
- [ ] Write todo.py with core functions
- [ ] Implement add functionality
- [ ] Implement list functionality
- [ ] Implement delete functionality
- **Status:** pending

### Phase 4: Testing & Verification
- [ ] Test add operation
- [ ] Test list operation
- [ ] Test delete operation
- [ ] Verify error handling
- **Status:** pending

### Phase 5: Delivery
- [ ] Review code quality
- [ ] Ensure all features work
- [ ] Deliver to user
- **Status:** pending

## Key Questions
1. Should tasks persist between sessions? (Yes - need file storage)
2. What format for storing tasks? (JSON file)
3. Command-line interface style? (Simple argparse)

## Decisions Made
| Decision | Rationale |
|----------|-----------|
|          |           |

## Errors Encountered
| Error | Attempt | Resolution |
|-------|---------|------------|
|       | 1       |            |

## Notes
- Update phase status as you progress: pending → in_progress → complete
- Re-read this plan before major decisions (attention manipulation)
- Log ALL errors - they help avoid repetition
```

### findings.md (Initial State)

```markdown
# Findings & Decisions

## Requirements
- Command-line interface
- Add tasks
- List all tasks
- Delete tasks
- Python implementation
- Tasks should persist (survive app restart)

## Research Findings
- (To be filled as we explore)

## Technical Decisions
| Decision | Rationale |
|----------|-----------|
|          |           |

## Issues Encountered
| Issue | Resolution |
|-------|------------|
|       |            |

## Resources
- Python argparse documentation (to be referenced)

## Visual/Browser Findings
- (To be updated after research)

---
*Update this file after every 2 view/browser/search operations*
*This prevents visual information from being lost*
```

### progress.md (Initial State)

```markdown
# Progress Log

## Session: 2026-01-15

### Phase 1: Requirements & Discovery
- **Status:** in_progress
- **Started:** 2026-01-15 10:00
- Actions taken:
  - Created task_plan.md
  - Created findings.md
  - Created progress.md
- Files created/modified:
  - task_plan.md (created)
  - findings.md (created)
  - progress.md (created)

### Phase 2: Planning & Structure
- **Status:** pending
- Actions taken:
  -
- Files created/modified:
  -

## Test Results
| Test | Input | Expected | Actual | Status |
|------|-------|----------|--------|--------|
|      |       |          |        |        |

## Error Log
| Timestamp | Error | Attempt | Resolution |
|-----------|-------|---------|------------|
|           |       | 1       |            |

## 5-Question Reboot Check
| Question | Answer |
|----------|--------|
| Where am I? | Phase 1 - Requirements & Discovery |
| Where am I going? | Phase 2-5: Planning, Implementation, Testing, Delivery |
| What's the goal? | Build Python CLI todo app with add/list/delete |
| What have I learned? | See findings.md |
| What have I done? | Created planning files |

---
*Update after completing each phase or encountering errors*
```

---

## Phase 2: After Research & Planning

### task_plan.md (Updated)

```markdown
# Task Plan: Build Command-Line Todo App

## Goal
Create a Python CLI todo app with add, list, and delete functionality.

## Current Phase
Phase 2

## Phases

### Phase 1: Requirements & Discovery
- [x] Understand user intent ✓
- [x] Identify constraints and requirements ✓
- [x] Document findings in findings.md ✓
- **Status:** complete

### Phase 2: Planning & Structure
- [x] Define technical approach ✓
- [x] Create project structure ✓
- [x] Document decisions with rationale ✓
- **Status:** complete

### Phase 3: Implementation
- [ ] Write todo.py with core functions
- [ ] Implement add functionality
- [ ] Implement list functionality
- [ ] Implement delete functionality
- **Status:** in_progress

### Phase 4: Testing & Verification
- [ ] Test add operation
- [ ] Test list operation
- [ ] Test delete operation
- [ ] Verify error handling
- **Status:** pending

### Phase 5: Delivery
- [ ] Review code quality
- [ ] Ensure all features work
- [ ] Deliver to user
- **Status:** pending

## Key Questions
1. Should tasks persist between sessions? ✓ Yes - using JSON file
2. What format for storing tasks? ✓ JSON file (todos.json)
3. Command-line interface style? ✓ argparse with subcommands

## Decisions Made
| Decision | Rationale |
|----------|-----------|
| Use JSON for storage | Simple, human-readable, built-in Python support |
| argparse with subcommands | Clean CLI: `python todo.py add "task"`, `python todo.py list` |
| Store in todos.json | Standard location, easy to find and debug |

## Errors Encountered
| Error | Attempt | Resolution |
|-------|---------|------------|
|       | 1       |            |

## Notes
- Update phase status as you progress: pending → in_progress → complete
- Re-read this plan before major decisions (attention manipulation)
- Log ALL errors - they help avoid repetition
```

### findings.md (Updated)

```markdown
# Findings & Decisions

## Requirements
- Command-line interface
- Add tasks
- List all tasks
- Delete tasks
- Python implementation
- Tasks should persist (survive app restart)

## Research Findings
- Python's `argparse` module is perfect for CLI subcommands
- `json` module handles file persistence easily
- Standard pattern: `python todo.py <command> [args]`
- File structure: Single `todo.py` file is sufficient for this scope

## Technical Decisions
| Decision | Rationale |
|----------|-----------|
| Use JSON for storage | Simple, human-readable, built-in Python support |
| argparse with subcommands | Clean CLI: `python todo.py add "task"`, `python todo.py list` |
| Store in todos.json | Standard location, easy to find and debug |
| Single file structure | Simple enough for one file, can refactor later if needed |

## Issues Encountered
| Issue | Resolution |
|-------|------------|
|       |            |

## Resources
- Python argparse documentation: https://docs.python.org/3/library/argparse.html
- Python json module: https://docs.python.org/3/library/json.html

## Visual/Browser Findings
- Reviewed argparse examples - subcommand pattern is straightforward
- JSON file format: array of objects with `id` and `task` fields

---
*Update this file after every 2 view/browser/search operations*
*This prevents visual information from being lost*
```

### progress.md (Updated)

```markdown
# Progress Log

## Session: 2026-01-15

### Phase 1: Requirements & Discovery
- **Status:** complete
- **Started:** 2026-01-15 10:00
- **Completed:** 2026-01-15 10:15
- Actions taken:
  - Created task_plan.md
  - Created findings.md
  - Created progress.md
  - Researched Python CLI patterns
  - Decided on JSON storage
- Files created/modified:
  - task_plan.md (created, updated)
  - findings.md (created, updated)
  - progress.md (created)

### Phase 2: Planning & Structure
- **Status:** complete
- **Started:** 2026-01-15 10:15
- **Completed:** 2026-01-15 10:20
- Actions taken:
  - Defined technical approach (argparse + JSON)
  - Documented decisions in findings.md
  - Updated task_plan.md with decisions
- Files created/modified:
  - task_plan.md (updated)
  - findings.md (updated)

### Phase 3: Implementation
- **Status:** in_progress
- **Started:** 2026-01-15 10:20
- Actions taken:
  - Starting to write todo.py
- Files created/modified:
  - (todo.py will be created)

## Test Results
| Test | Input | Expected | Actual | Status |
|------|-------|----------|--------|--------|
|      |       |          |        |        |

## Error Log
| Timestamp | Error | Attempt | Resolution |
|-----------|-------|---------|------------|
|           |       | 1       |            |

## 5-Question Reboot Check
| Question | Answer |
|----------|--------|
| Where am I? | Phase 3 - Implementation |
| Where am I going? | Phase 4-5: Testing, Delivery |
| What's the goal? | Build Python CLI todo app with add/list/delete |
| What have I learned? | argparse subcommands, JSON storage pattern (see findings.md) |
| What have I done? | Completed planning, starting implementation |

---
*Update after completing each phase or encountering errors*
```

---

## Phase 3: During Implementation (With Error)

### task_plan.md (After Error Encountered)

```markdown
# Task Plan: Build Command-Line Todo App

## Goal
Create a Python CLI todo app with add, list, and delete functionality.

## Current Phase
Phase 3

## Phases

### Phase 1: Requirements & Discovery
- [x] Understand user intent ✓
- [x] Identify constraints and requirements ✓
- [x] Document findings in findings.md ✓
- **Status:** complete

### Phase 2: Planning & Structure
- [x] Define technical approach ✓
- [x] Create project structure ✓
- [x] Document decisions with rationale ✓
- **Status:** complete

### Phase 3: Implementation
- [x] Write todo.py with core functions ✓
- [x] Implement add functionality ✓
- [ ] Implement list functionality (CURRENT)
- [ ] Implement delete functionality
- **Status:** in_progress

### Phase 4: Testing & Verification
- [ ] Test add operation
- [ ] Test list operation
- [ ] Test delete operation
- [ ] Verify error handling
- **Status:** pending

### Phase 5: Delivery
- [ ] Review code quality
- [ ] Ensure all features work
- [ ] Deliver to user
- **Status:** pending

## Key Questions
1. Should tasks persist between sessions? ✓ Yes - using JSON file
2. What format for storing tasks? ✓ JSON file (todos.json)
3. Command-line interface style? ✓ argparse with subcommands

## Decisions Made
| Decision | Rationale |
|----------|-----------|
| Use JSON for storage | Simple, human-readable, built-in Python support |
| argparse with subcommands | Clean CLI: `python todo.py add "task"`, `python todo.py list` |
| Store in todos.json | Standard location, easy to find and debug |
| Use incremental IDs | Simple counter, easier than UUIDs for this use case |

## Errors Encountered
| Error | Attempt | Resolution |
|-------|---------|------------|
| FileNotFoundError when reading todos.json | 1 | Check if file exists, create empty list if not |
| JSONDecodeError on empty file | 2 | Handle empty file case explicitly |

## Notes
- Update phase status as you progress: pending → in_progress → complete
- Re-read this plan before major decisions (attention manipulation)
- Log ALL errors - they help avoid repetition
```

### progress.md (With Error Logged)

```markdown
# Progress Log

## Session: 2026-01-15

### Phase 1: Requirements & Discovery
- **Status:** complete
- **Started:** 2026-01-15 10:00
- **Completed:** 2026-01-15 10:15
- Actions taken:
  - Created task_plan.md
  - Created findings.md
  - Created progress.md
  - Researched Python CLI patterns
  - Decided on JSON storage
- Files created/modified:
  - task_plan.md (created, updated)
  - findings.md (created, updated)
  - progress.md (created)

### Phase 2: Planning & Structure
- **Status:** complete
- **Started:** 2026-01-15 10:15
- **Completed:** 2026-01-15 10:20
- Actions taken:
  - Defined technical approach (argparse + JSON)
  - Documented decisions in findings.md
  - Updated task_plan.md with decisions
- Files created/modified:
  - task_plan.md (updated)
  - findings.md (updated)

### Phase 3: Implementation
- **Status:** in_progress
- **Started:** 2026-01-15 10:20
- Actions taken:
  - Created todo.py with basic structure
  - Implemented add functionality
  - Encountered FileNotFoundError (handled)
  - Encountered JSONDecodeError on empty file (handled)
  - Working on list functionality
- Files created/modified:
  - todo.py (created, modified)
  - todos.json (created by app)

## Test Results
| Test | Input | Expected | Actual | Status |
|------|-------|----------|--------|--------|
| Add task | `python todo.py add "Buy milk"` | Task added to todos.json | Task added successfully | ✓ |
| List tasks | `python todo.py list` | Shows all tasks | FileNotFoundError (fixed) | Fixed |

## Error Log
| Timestamp | Error | Attempt | Resolution |
|-----------|-------|---------|------------|
| 2026-01-15 10:35 | FileNotFoundError when reading todos.json | 1 | Added file existence check, create empty list if not exists |
| 2026-01-15 10:37 | JSONDecodeError on empty file | 2 | Added explicit empty file handling before json.load() |

## 5-Question Reboot Check
| Question | Answer |
|----------|--------|
| Where am I? | Phase 3 - Implementation (working on list functionality) |
| Where am I going? | Phase 4-5: Testing, Delivery |
| What's the goal? | Build Python CLI todo app with add/list/delete |
| What have I learned? | Need to handle file not existing, empty file edge cases (see findings.md) |
| What have I done? | Completed add functionality, fixed file handling errors, working on list |

---
*Update after completing each phase or encountering errors*
```

---

## Phase 4: Task Complete

### task_plan.md (Final State)

```markdown
# Task Plan: Build Command-Line Todo App

## Goal
Create a Python CLI todo app with add, list, and delete functionality.

## Current Phase
Phase 5 (Complete)

## Phases

### Phase 1: Requirements & Discovery
- [x] Understand user intent ✓
- [x] Identify constraints and requirements ✓
- [x] Document findings in findings.md ✓
- **Status:** complete

### Phase 2: Planning & Structure
- [x] Define technical approach ✓
- [x] Create project structure ✓
- [x] Document decisions with rationale ✓
- **Status:** complete

### Phase 3: Implementation
- [x] Write todo.py with core functions ✓
- [x] Implement add functionality ✓
- [x] Implement list functionality ✓
- [x] Implement delete functionality ✓
- **Status:** complete

### Phase 4: Testing & Verification
- [x] Test add operation ✓
- [x] Test list operation ✓
- [x] Test delete operation ✓
- [x] Verify error handling ✓
- **Status:** complete

### Phase 5: Delivery
- [x] Review code quality ✓
- [x] Ensure all features work ✓
- [x] Deliver to user ✓
- **Status:** complete

## Key Questions
1. Should tasks persist between sessions? ✓ Yes - using JSON file
2. What format for storing tasks? ✓ JSON file (todos.json)
3. Command-line interface style? ✓ argparse with subcommands

## Decisions Made
| Decision | Rationale |
|----------|-----------|
| Use JSON for storage | Simple, human-readable, built-in Python support |
| argparse with subcommands | Clean CLI: `python todo.py add "task"`, `python todo.py list` |
| Store in todos.json | Standard location, easy to find and debug |
| Use incremental IDs | Simple counter, easier than UUIDs for this use case |

## Errors Encountered
| Error | Attempt | Resolution |
|-------|---------|------------|
| FileNotFoundError when reading todos.json | 1 | Check if file exists, create empty list if not |
| JSONDecodeError on empty file | 2 | Handle empty file case explicitly |

## Notes
- Update phase status as you progress: pending → in_progress → complete
- Re-read this plan before major decisions (attention manipulation)
- Log ALL errors - they help avoid repetition
```

---

## Key Takeaways

### How Files Work Together

1. **task_plan.md** = Your roadmap
   - Created first, before any work begins
   - Updated after each phase completes
   - Re-read before major decisions (automatic via hooks)
   - Tracks what's done, what's next, what went wrong

2. **findings.md** = Your knowledge base
   - Captures research and discoveries
   - Stores technical decisions with rationale
   - Updated after every 2 view/browser operations (2-Action Rule)
   - Prevents losing important information

3. **progress.md** = Your session log
   - Records what you did and when
   - Tracks test results
   - Logs ALL errors (even ones you fixed)
   - Answers the "5-Question Reboot Test"

### The Workflow Pattern

```
START TASK
  ↓
Create task_plan.md (NEVER skip this!)
  ↓
Create findings.md
  ↓
Create progress.md
  ↓
[Work on task]
  ↓
Update files as you go:
  - task_plan.md: Mark phases complete, log errors
  - findings.md: Save discoveries (especially after 2 view/browser ops)
  - progress.md: Log actions, tests, errors
  ↓
Re-read task_plan.md before major decisions
  ↓
COMPLETE TASK
```

### Common Patterns

- **Error occurs?** → Log it in `task_plan.md` AND `progress.md`
- **Made a decision?** → Document in `findings.md` with rationale
- **Viewed 2 things?** → Save findings to `findings.md` immediately
- **Starting new phase?** → Update status in `task_plan.md` and `progress.md`
- **Uncertain what to do?** → Re-read `task_plan.md` to refresh goals

---

## More Examples

Want to see more examples? Check out:
- [examples.md](../skills/planning-with-files/examples.md) - Additional patterns and use cases

---

*Want to contribute an example? Open a PR!*
