---
name: loop
description: Runs a prompt or slash command on a recurring interval. Useful for polling, monitoring, or repeating a task automatically.
---

## loop
**Category:** Utility

**What it does:**
Runs a prompt or slash command on a recurring interval. Useful for polling, monitoring, or repeating a task automatically.

**Examples:**
- `/loop 5m /foo` — run `/foo` every 5 minutes
- Defaults to 10-minute interval if not specified

**When to trigger:**
- Check a deploy every 5 minutes
- Keep running `/babysit-prs` repeatedly
- Poll for status on an interval

**Do NOT use for one-off tasks** — only for recurring work.

**How to install:**
```bash
npx claude install superpowers
```

**Trigger phrase:** `/loop [interval] [command]`
