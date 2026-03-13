---
name: claude-code-notify
description: Zero-dependency desktop notification system for Claude Code using native OS notifications via shell-based hooks.
---

# Claude Code Notify

Desktop notification system for Claude Code that alerts you when Claude needs attention or finishes a task. Uses native OS notifications with zero dependencies -- just two shell scripts totaling ~3 KB.

## When to Use This Skill

- When you switch away from the terminal while Claude Code works on a long task
- When you want to be notified the moment Claude Code needs your input
- When running multiple Claude Code sessions and need to track which one needs attention

## What This Skill Does

1. **Native Notifications**: Sends desktop notifications using macOS (terminal-notifier/osascript) or Linux (notify-send)
2. **Clickable Alerts**: Notifications are clickable and bring focus back to the terminal
3. **Notification Grouping**: Groups notifications to prevent spam when multiple events fire quickly
4. **One-Command Install**: Install with a single curl command

## How to Use

### Installation

```bash
curl -fsSL https://raw.githubusercontent.com/JadenChoi2k/claude-code-notify/main/install.sh | bash
```

### How It Works

Once installed, Claude Code's hook system automatically triggers desktop notifications when Claude Code needs user attention or completes tasks. No additional configuration is required.

## Example

**Scenario**: You start a long refactoring task in Claude Code and switch to your browser.

**Result**: A native desktop notification pops up when Claude finishes or needs your input, letting you click it to jump back to the terminal.

![Demo](https://raw.githubusercontent.com/JadenChoi2k/claude-code-notify/main/assets/demo.png)

## Tips

- Works out of the box on macOS with osascript; install terminal-notifier for richer notifications
- On Linux, ensure notify-send is available (usually pre-installed on GNOME/KDE desktops)
- Notifications are automatically grouped to avoid flooding your notification center

## Common Use Cases

- Long-running code generation or refactoring tasks
- Multi-session Claude Code workflows
- Background task monitoring while working in other applications
