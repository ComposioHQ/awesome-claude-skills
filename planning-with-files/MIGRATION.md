# Migration Guide: v1.x to v2.0.0

## Overview

Version 2.0.0 adds hooks integration and enhanced templates while maintaining backward compatibility with existing workflows.

## What's New

### 1. Hooks (Automatic Behaviors)

v2.0.0 adds Claude Code hooks that automate key Manus principles:

| Hook | Trigger | Behavior |
|------|---------|----------|
| `PreToolUse` | Before Write/Edit/Bash | Reads `task_plan.md` to refresh goals |
| `Stop` | Before stopping | Verifies all phases are complete |

**Benefit:** You no longer need to manually remember to re-read your plan. The hook does it automatically.

### 2. Templates Directory

New templates provide structured starting points:

```
templates/
├── task_plan.md    # Phase tracking with status fields
├── findings.md     # Research storage with 2-action reminder
└── progress.md     # Session log with 5-question reboot test
```

### 3. Scripts Directory

Helper scripts for common operations:

```
scripts/
├── init-session.sh     # Creates all 3 planning files
└── check-complete.sh   # Verifies task completion
```

## Migration Steps

### Step 1: Update the Plugin

```bash
# If installed via marketplace
/plugin update planning-with-files

# If installed manually
cd .claude/plugins/planning-with-files
git pull origin master
```

### Step 2: Existing Files Continue Working

Your existing `task_plan.md` files will continue to work. The hooks look for this file and gracefully handle its absence.

### Step 3: Adopt New Templates (Optional)

To use the new structured templates, you can either:

1. **Start fresh** with `./scripts/init-session.sh`
2. **Copy templates** from `templates/` directory
3. **Keep your existing format** - it still works

### Step 4: Update Phase Status Format (Recommended)

v2.0.0 templates use a more structured status format:

**v1.x format:**
```markdown
- [x] Phase 1: Setup ✓
- [ ] Phase 2: Implementation (CURRENT)
```

**v2.0.0 format:**
```markdown
### Phase 1: Setup
- **Status:** complete

### Phase 2: Implementation
- **Status:** in_progress
```

The new format enables the `check-complete.sh` script to automatically verify completion.

## Breaking Changes

**None.** v2.0.0 is fully backward compatible.

If you prefer the v1.x behavior without hooks, use the `legacy` branch:

```bash
git checkout legacy
```

## New Features to Adopt

### The 2-Action Rule

After every 2 view/browser/search operations, save findings to files:

```
WebSearch → WebSearch → MUST Write findings.md
```

### The 3-Strike Error Protocol

Structured error recovery:

1. Diagnose & Fix
2. Alternative Approach
3. Broader Rethink
4. Escalate to User

### The 5-Question Reboot Test

Your planning files should answer:

1. Where am I? → Current phase
2. Where am I going? → Remaining phases
3. What's the goal? → Goal statement
4. What have I learned? → findings.md
5. What have I done? → progress.md

## Questions?

Open an issue: https://github.com/OthmanAdi/planning-with-files/issues
