---
name: hyprland
description: Control the Hyprland Wayland desktop and interact with any running application — click buttons, type text, take screenshots, manage windows, and automate GUI workflows on Linux.
---

# Hyprland Desktop Control

See, control, and interact with everything on a Hyprland Wayland desktop — both the applications running inside it and the desktop environment itself.

## When to Use This Skill

- You need to click a button or type text inside a running app
- You want to take a screenshot or inspect what's on screen
- You need to move, resize, close, or focus windows
- You want to switch workspaces or manage multiple monitors
- You're automating a GUI workflow (e.g., sending a message, filling a form)
- You hear "the screen", "the window", "this app", or any desktop interaction

## What This Skill Does

1. **App interaction via AT-SPI2**: Semantically interact with accessible apps (Firefox, Chrome, GTK apps) — click elements by name, type into inputs, read UI trees — no coordinates needed.
2. **Universal input via ydotool**: Move the mouse, click, and type (including CJK) in any app regardless of whether it's native Wayland or XWayland.
3. **Screenshot-based interaction**: Capture the full screen or a specific window, visually identify elements, and compute click coordinates.
4. **Window and workspace management**: Focus, move, resize, close windows; switch workspaces; query window state — all via `hyprctl`.
5. **App-specific knowledge**: Remembers the best interaction method per app and updates after each task.

## How to Use

### Interact with an app

```
Click the "Send" button in Slack
```

```
Type "hello" into the search box in Firefox
```

### Take a screenshot

```
Take a screenshot of the current screen
```

### Manage windows

```
Move the Firefox window to workspace 2 and make it fullscreen
```

### Automate a workflow

```
Open WeChat, find contact "Alice", and send her "I'll be 5 minutes late"
```

## Example

**User**: "Click the compose button in the Gmail tab in Chrome"

**What the skill does**:
1. Checks Chrome's AT-SPI2 tree: `atspi_interact.py check "chrome"`
2. Dumps the tree to find "Compose" button by name
3. Clicks it: `atspi_interact.py click "chrome" --name "Compose"`

If AT-SPI isn't available, falls back to: screenshot → identify button coordinates → `ydotool mousemove --absolute -x X -y Y && ydotool click 0xC0`

## Tips

- AT-SPI2 is the most reliable method — no coordinates needed. Try it first for GTK/Qt apps and browsers.
- ydotool works universally at the kernel level, for both Wayland and XWayland apps.
- Before any screenshot-based click, verify the target window is focused with `hyprctl activewindow -j` and check coordinates fall within window bounds.
- After each action, take a fresh screenshot to confirm the result before the next step.
- For IM apps: if a contact isn't visible, use the app's search box rather than scrolling.

## Common Use Cases

- Sending messages in Slack, WeChat, or other IM apps
- Clicking through browser workflows (forms, buttons, navigation)
- Taking screenshots for debugging or inspection
- Automating repetitive GUI tasks on a Linux Wayland desktop
- Managing window layouts and workspaces during development
