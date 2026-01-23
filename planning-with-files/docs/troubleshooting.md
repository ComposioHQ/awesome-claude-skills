# Troubleshooting

Common issues and their solutions.

---

## Planning files created in wrong directory

**Issue:** When using `/planning-with-files`, the files (`task_plan.md`, `findings.md`, `progress.md`) are created in the skill installation directory instead of your project.

**Why this happens:** When the skill runs as a subagent, it may not inherit your terminal's current working directory.

**Solutions:**

### Solution 1: Specify your project path when invoking

```
/planning-with-files - I'm working in /path/to/my-project/, create all files there
```

### Solution 2: Add context before invoking

```
I'm working on the project at /path/to/my-project/
```
Then run `/planning-with-files`.

### Solution 3: Create a CLAUDE.md in your project root

```markdown
# Project Context

All planning files (task_plan.md, findings.md, progress.md)
should be created in this directory.
```

### Solution 4: Use the skill directly without subagent

```
Help me plan this task using the planning-with-files approach.
Create task_plan.md, findings.md, and progress.md here.
```

**Note:** This was fixed in v2.0.1. The skill instructions now explicitly specify that planning files should be created in your project directory, not the skill installation folder.

---

## Files not persisting between sessions

**Issue:** Planning files seem to disappear or aren't found when resuming work.

**Solution:** Make sure the files are in your project root, not in a temporary location.

Check with:
```bash
ls -la task_plan.md findings.md progress.md
```

If files are missing, they may have been created in:
- The skill installation folder (`~/.claude/skills/planning-with-files/`)
- A temporary directory
- A different working directory

---

## Hooks not triggering

**Issue:** The PreToolUse hook (which reads task_plan.md before actions) doesn't seem to run.

**Solution:**

1. **Check Claude Code version:**
   ```bash
   claude --version
   ```
   Hooks require Claude Code v2.1.0 or later for full support.

2. **Verify skill installation:**
   ```bash
   ls ~/.claude/skills/planning-with-files/
   ```
   or
   ```bash
   ls .claude/plugins/planning-with-files/
   ```

3. **Check that task_plan.md exists:**
   The PreToolUse hook runs `cat task_plan.md`. If the file doesn't exist, the hook silently succeeds (by design).

4. **Check for YAML errors:**
   Run Claude Code with debug mode:
   ```bash
   claude --debug
   ```
   Look for skill loading errors.

---

## SessionStart hook not showing message

**Issue:** The "Ready" message doesn't appear when starting Claude Code.

**Solution:**

1. SessionStart hooks require Claude Code v2.1.0+
2. The hook only fires once per session
3. If you've already started a session, restart Claude Code

---

## PostToolUse hook not running

**Issue:** The reminder message after Write/Edit doesn't appear.

**Solution:**

1. PostToolUse hooks require Claude Code v2.1.0+
2. The hook only fires after successful Write/Edit operations
3. Check the matcher pattern: it's set to `"Write|Edit"` only

---

## Skill not auto-detecting complex tasks

**Issue:** Claude doesn't automatically use the planning pattern for complex tasks.

**Solution:**

1. **Manually invoke:**
   ```
   /planning-with-files
   ```

2. **Trigger words:** The skill auto-activates based on its description. Try phrases like:
   - "complex multi-step task"
   - "research project"
   - "task requiring many steps"

3. **Be explicit:**
   ```
   This is a complex task that will require >5 tool calls.
   Please use the planning-with-files pattern.
   ```

---

## Stop hook blocking completion

**Issue:** Claude won't stop because the Stop hook says phases aren't complete.

**Solution:**

1. **Check task_plan.md:** All phases should have `**Status:** complete`

2. **Manual override:** If you need to stop anyway:
   ```
   Override the completion check - I want to stop now.
   ```

3. **Fix the status:** Update incomplete phases to `complete` if they're actually done.

---

## YAML frontmatter errors

**Issue:** Skill won't load due to YAML errors.

**Solution:**

1. **Check indentation:** YAML requires spaces, not tabs
2. **Check the first line:** Must be exactly `---` with no blank lines before it
3. **Validate YAML:** Use an online YAML validator

Common mistakes:
```yaml
# WRONG - tabs
hooks:
	PreToolUse:

# CORRECT - spaces
hooks:
  PreToolUse:
```

---

## Windows-specific issues

See [docs/windows.md](windows.md) for Windows-specific troubleshooting.

---

## Cursor-specific issues

See [docs/cursor.md](cursor.md) for Cursor IDE troubleshooting.

---

## Still stuck?

Open an issue at [github.com/OthmanAdi/planning-with-files/issues](https://github.com/OthmanAdi/planning-with-files/issues) with:

- Your Claude Code version (`claude --version`)
- Your operating system
- The command you ran
- What happened vs what you expected
- Any error messages
