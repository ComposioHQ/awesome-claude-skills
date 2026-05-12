---
name: keybindings
description: Customize Claude Code keyboard shortcuts — add, change, or remove keybindings in ~/.claude/keybindings.json. Use this skill when the user wants to rebind keys, add chord shortcuts, change the submit key, or customize any Claude Code keyboard shortcuts.
---

# Keybindings

Customize Claude Code keyboard shortcuts by editing `~/.claude/keybindings.json`.

## Keybindings File Location

```
~/.claude/keybindings.json
```

Create it if it doesn't exist.

## File Format

```json
[
  {
    "key": "ctrl+enter",
    "command": "sendMessage"
  },
  {
    "key": "ctrl+shift+n",
    "command": "newChat"
  }
]
```

## Available Commands

| Command | Description |
|---------|-------------|
| `sendMessage` | Send the current message |
| `newChat` | Start a new chat session |
| `clearChat` | Clear the current chat |
| `cancelMessage` | Cancel the current in-progress response |
| `focusInput` | Focus the message input |
| `toggleSidebar` | Toggle the sidebar |

## Key Format

Keys are specified as strings with modifiers separated by `+`:

**Modifiers:**
- `ctrl` — Control key
- `cmd` — Command key (macOS)
- `shift` — Shift key
- `alt` — Alt/Option key
- `meta` — Meta/Windows key

**Examples:**
- `"ctrl+enter"` — Ctrl + Enter
- `"cmd+shift+k"` — Cmd + Shift + K
- `"ctrl+k ctrl+c"` — Chord: Ctrl+K then Ctrl+C (two-key sequence)

## Common Customizations

### Change submit key to Ctrl+Enter (keep Enter for newlines)
```json
[
  {
    "key": "ctrl+enter",
    "command": "sendMessage"
  }
]
```

### Add chord shortcut
```json
[
  {
    "key": "ctrl+k n",
    "command": "newChat"
  }
]
```

### Multiple custom bindings
```json
[
  {
    "key": "ctrl+enter",
    "command": "sendMessage"
  },
  {
    "key": "escape",
    "command": "cancelMessage"
  },
  {
    "key": "ctrl+shift+c",
    "command": "clearChat"
  }
]
```

## Process for Updating Keybindings

1. Read the current `~/.claude/keybindings.json` (or note it doesn't exist)
2. Apply the requested changes
3. Write the updated file
4. Confirm with the user what was changed

## Notes

- Changes take effect after restarting Claude Code
- If the file doesn't exist, create it with just the new bindings
- Multiple keys can bind to the same command
- Chord bindings (two-key sequences) are supported with a space: `"ctrl+k n"`
- On macOS, prefer `cmd` over `ctrl` for Mac-native feel
