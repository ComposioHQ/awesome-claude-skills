---
name: spawn-tasks
description: Spawn parallel Claude Code sessions from planned subtasks. Each session gets its own isolated git worktree and tmux pane with full task context. Use when you have multiple independent subtasks that can run concurrently.
---

# Spawn Tasks — Parallel Session Launcher

## When to Use This Skill

- You've broken down a feature or project into independent subtasks in a Claude Code conversation
- Tasks don't have sequential dependencies and can run in parallel
- You want each task to run in an isolated git worktree to avoid conflicts

## What This Skill Does

1. Collects confirmed subtasks from the current conversation
2. Writes a self-contained `.tasks/spawn/{task-name}.md` file for each task
3. Spawns an independent `claude` session per task via `claude -w <name> --tmux`
4. Each session gets its own git worktree — no merge conflicts between parallel sessions

## How to Use

### Basic Usage

1. In a Claude Code session, plan and confirm your subtasks with Claude
2. Run `/spawn-tasks`
3. Claude shows the task list and asks for confirmation
4. Sessions open as new tmux panes (falls back to Terminal.app windows on macOS)

### Smart Spawning

`/spawn-tasks` doesn't blindly parallelize. If tasks have sequential dependencies (e.g. a schema migration must land before other work can follow), Claude will say so and recommend running them in order instead.

## Example

**User Prompt:**
> We've confirmed 3 independent features: auth system, dashboard UI, and REST API. Spawn them.

**Output:**
```
Writing task files...
  ✓ .tasks/spawn/auth-system.md
  ✓ .tasks/spawn/dashboard-ui.md
  ✓ .tasks/spawn/rest-api.md

Spawning 3 sessions in isolated worktrees...
  $ claude -w auth-system --tmux ...
  $ claude -w dashboard-ui --tmux ...
  $ claude -w rest-api --tmux ...

✓ 3 sessions running in parallel.
Each has its own git worktree — changes don't conflict.
```

## Installation

```bash
git clone https://github.com/theradengai/spawn-tasks ~/.claude/skills/spawn-tasks
```

Or copy just the skill file:

```bash
mkdir -p ~/.claude/skills/spawn-tasks
curl -o ~/.claude/skills/spawn-tasks/SKILL.md \
  https://raw.githubusercontent.com/theradengai/spawn-tasks/main/SKILL.md
```

## Requirements

- [Claude Code](https://claude.ai/code) CLI (`claude`)
- tmux (recommended) or macOS Terminal.app as fallback
- A git repository (worktrees require git)
- **Platform:** macOS and Linux only (requires tmux or a compatible terminal emulator; not supported on Windows)

## Tips

- Task files in `.tasks/spawn/` are kept after spawning for reference and re-use
- Each task file must be fully self-contained — spawned sessions have no access to the main conversation
- Include references to project docs (e.g. `docs/final-consensus/`) in task context so spawned sessions know to check them
- Use `Ctrl+B <number>` (tmux) or `Cmd+[` (iTerm2) to switch between sessions

## Credit

By [@theradengai](https://github.com/theradengai) — [github.com/theradengai/spawn-tasks](https://github.com/theradengai/spawn-tasks)
