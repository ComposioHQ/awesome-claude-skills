# Cursor IDE Setup

How to use planning-with-files with Cursor IDE.

---

## Installation

### Option 1: Copy rules directory

```bash
git clone https://github.com/OthmanAdi/planning-with-files.git
cp -r planning-with-files/.cursor .cursor
```

### Option 2: Manual setup

Create `.cursor/rules/planning-with-files.mdc` in your project with the content from this repo.

---

## Important Limitations

> **Note:** Hooks (PreToolUse, PostToolUse, Stop, SessionStart) are **Claude Code specific** and will NOT work in Cursor.

### What works in Cursor:

- Core 3-file planning pattern
- Templates (task_plan.md, findings.md, progress.md)
- All planning rules and guidelines
- The 2-Action Rule
- The 3-Strike Error Protocol
- Read vs Write Decision Matrix

### What doesn't work in Cursor:

- SessionStart hook (no startup notification)
- PreToolUse hook (no automatic plan re-reading)
- PostToolUse hook (no automatic reminders)
- Stop hook (no automatic completion verification)

---

## Manual Workflow for Cursor

Since hooks don't work in Cursor, you'll need to follow the pattern manually:

### 1. Create planning files first

Before any complex task:
```
Create task_plan.md, findings.md, and progress.md using the planning-with-files templates.
```

### 2. Re-read plan before decisions

Periodically ask:
```
Please read task_plan.md to refresh the goals before continuing.
```

### 3. Update files after phases

After completing work:
```
Update task_plan.md to mark this phase complete.
Update progress.md with what was done.
```

### 4. Verify completion manually

Before finishing:
```
Check task_plan.md - are all phases marked complete?
```

---

## Cursor Rules File

The `.cursor/rules/planning-with-files.mdc` file contains all the planning guidelines formatted for Cursor's rules system.

### File location

```
your-project/
├── .cursor/
│   └── rules/
│       └── planning-with-files.mdc
├── task_plan.md
├── findings.md
├── progress.md
└── ...
```

### Activating rules

Cursor automatically loads rules from `.cursor/rules/` when you open a project.

---

## Templates

The templates in `skills/planning-with-files/templates/` work in Cursor:

- `task_plan.md` - Phase tracking template
- `findings.md` - Research storage template
- `progress.md` - Session logging template

Copy them to your project root when starting a new task.

---

## Tips for Cursor Users

1. **Pin the planning files:** Keep task_plan.md open in a split view for easy reference.

2. **Add to .cursorrules:** You can also add planning guidelines to your project's `.cursorrules` file.

3. **Use explicit prompts:** Since there's no auto-detection, be explicit:
   ```
   This is a complex task. Let's use the planning-with-files pattern.
   Start by creating task_plan.md with the goal and phases.
   ```

4. **Check status regularly:** Without the Stop hook, manually verify completion before finishing.

---

## Migrating from Cursor to Claude Code

If you want full hook support, consider using Claude Code CLI:

1. Install Claude Code
2. Run `/plugin install planning-with-files@planning-with-files`
3. All hooks will work automatically

Your existing planning files (task_plan.md, etc.) are compatible with both.

---

## Need Help?

Open an issue at [github.com/OthmanAdi/planning-with-files/issues](https://github.com/OthmanAdi/planning-with-files/issues).
