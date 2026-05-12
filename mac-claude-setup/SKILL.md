---
name: mac-claude-setup
description: Set up a new Mac for Claude Code development. Installs Homebrew, Node.js, Claude CLI, GitHub CLI, and configures the Claude Launchpad (terminal command center) and Remote Tasks system (give Claude instructions from your phone via GitHub Issues). Use when setting up a fresh Mac or onboarding a new machine.
---

# Mac Claude Setup

Set up a new Mac for Claude Code development with a launchpad and remote task system.

## What Gets Installed

1. **Homebrew** - macOS package manager
2. **Node.js** - Required for Claude Code CLI
3. **GitHub CLI (gh)** - For remote task system
4. **Claude Code CLI** - The main Claude tool
5. **Claude Launchpad** - Terminal-based command center (`lp` command)
6. **Remote Tasks** - GitHub Issues as a task queue (`ct` command)

## Quick Setup

Run the setup script from the claude-code-templates repo:

```bash
git clone https://github.com/Infiniteyieldai/claude-code-templates.git
cd claude-code-templates
bash scripts/mac-setup.sh
```

Or if you already have curl and want a one-liner:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/Infiniteyieldai/claude-code-templates/main/scripts/mac-setup.sh)
```

## After Setup

### Launchpad

Type `lp` or `launchpad` to open the command center:

```
  ╔══════════════════════════════════════════╗
  ║         CLAUDE  LAUNCHPAD                ║
  ╚══════════════════════════════════════════╝

  Quick Actions
  1  Start Claude in current directory
  2  Start Claude in workspace
  3  Resume last Claude session

  Projects
  4  Open a project (pick from workspace)
  5  Clone a repo and start Claude

  Remote Tasks
  6  Check for remote tasks
  7  Create a new remote task
  8  Run next pending task
```

### Remote Tasks

Give Claude instructions from your phone, tablet, or any browser:

```bash
# Set your task repo
export CLAUDE_TASKS_REPO='your-username/claude-tasks'

# Create a task
ct quick "Fix the login bug" "owner/my-app"

# List pending tasks
ct list

# Run the next task
ct run-next
```

Create tasks from anywhere:
- **Phone**: GitHub mobile app (create issue + `claude-task` label)
- **iOS Shortcut**: POST to GitHub Issues API
- **Browser**: Any GitHub issue form

### Auto-Runner

Automatically poll for and execute remote tasks:

```bash
# Install (checks every 5 minutes, notifies on new tasks)
bash scripts/claude-auto-runner.sh install

# Full auto mode (runs tasks without asking)
CLAUDE_AUTO_RUN=true bash scripts/claude-auto-runner.sh install
```

## File Locations

| Item | Path |
|------|------|
| Launchpad | `~/.claude-launchpad/launchpad.sh` |
| Remote tasks | `~/.claude-launchpad/remote-tasks.sh` |
| Auto-runner logs | `~/.claude-launchpad/logs/` |
| Workspace | `~/claude-workspace/` |
| Claude config | `~/.claude/CLAUDE.md` |
