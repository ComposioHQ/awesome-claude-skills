---
name: detect-user-preferences
description: Use when starting a new conversation or when the user mentions timezone, locale, language, date format, or system preferences. Also use when Claude gives times in UTC instead of local time, or uses the wrong language or date format.
---

# Detect User Preferences

Auto-detect and remember system preferences (timezone, locale, language, date format, OS, shell) so Claude always communicates in the right context.

## When to Use This Skill

- First conversation with a new user (no preferences in memory yet)
- User complains about wrong timezone, language, or date format
- User asks to update their preferences

## What This Skill Does

1. **Detects system settings** via shell commands (`date +%z`, `$LANG`, `uname -s`, `$SHELL`)
2. **Saves to persistent memory** in Claude Code's MEMORY.md
3. **Applies automatically** in all future sessions — correct timezone, language, date format

## How to Use

### Basic Usage

Just start a Claude Code conversation. The skill triggers automatically when:
- No preferences are saved yet
- You mention timezone, locale, or language
- Claude shows you UTC times instead of local time

### Manual Trigger

Say: "Bitte erkenne meine Systemeinstellungen" or "Detect my system preferences"

### What Gets Detected

| Setting | Command | Example |
|---------|---------|---------|
| Timezone | `date +%z` | `+0700` (UTC+7) |
| Locale | `echo $LANG` | `en_US.UTF-8` |
| OS | `uname -s` | `Darwin` (macOS) |
| Shell | `echo $SHELL` | `/bin/zsh` |

### What Gets Saved

```markdown
## User System Preferences
- Timezone: UTC+7 — always show times in this timezone
- Locale: en_US.UTF-8
- Preferred language: German (detected from conversation)
- OS: macOS (Darwin)
- Shell: zsh
```

## Examples

**Before:** "The task starts at 08:00 UTC on 2026-03-07"
**After:** "Die Aufgabe startet um 15:00 (UTC+7) am 07.03.2026"

## Key Design Decisions

- **Language ≠ Locale**: A German speaker may have `en_US` locale. Language is detected from conversation, not system settings.
- **Detect once, apply forever**: Preferences persist in Claude Code's auto-memory across all sessions.
- **UTC offset over timezone name**: `+0700` is unambiguous; timezone abbreviations like `ICT` vary by system.

## Installation

```bash
npx skills add held0/claude-skill-detect-preferences -g -y
```

Or via GitHub: [held0/claude-skill-detect-preferences](https://github.com/held0/claude-skill-detect-preferences)
