---
name: loop
description: Run a prompt or slash command on a recurring interval. Use this skill when the user wants to set up a recurring task, poll for status, or run something repeatedly (e.g., "/loop 5m /foo", "check the deploy every 5 minutes", "keep running /babysit-prs"). Do NOT invoke for one-off tasks.
---

# Loop

Run a command or prompt repeatedly on a timed interval.

## Syntax

```
/loop [interval] [command or prompt]
```

**Examples:**
- `/loop 5m /check-deploy` — run `/check-deploy` every 5 minutes
- `/loop 10m check if any new PRs need review` — check for PRs every 10 minutes
- `/loop 30s run tests and report results` — run tests every 30 seconds
- `/loop /my-skill` — run `/my-skill` every 10 minutes (default interval)

## Interval Format

| Format | Example | Meaning |
|--------|---------|---------|
| `Xs` | `30s` | Every 30 seconds |
| `Xm` | `5m` | Every 5 minutes |
| `Xh` | `1h` | Every 1 hour |
| (none) | — | Default: 10 minutes |

## How to Run a Loop

When the user invokes `/loop`:

1. **Parse the interval** — extract time from the command (default 10m if not specified)
2. **Parse the command** — everything after the interval is the recurring task
3. **Execute the task** immediately (first run)
4. **Report results** from the first run
5. **Wait** for the specified interval
6. **Execute again** and report
7. **Continue** until the user stops it (Ctrl+C or says "stop")

## Loop Execution Pattern

```
[Loop started: every 5m]

━━━ Run 1 — 14:32:00 ━━━
[Execute command and report results]

━━━ Run 2 — 14:37:00 ━━━
[Execute command and report results]

━━━ Run 3 — 14:42:00 ━━━
[Execute command and report results — highlight any changes from previous run]
```

## Change Detection

On each run after the first:
- Compare results to the previous run
- Highlight **changes** clearly: new items, resolved items, status changes
- If nothing changed: report "No changes since last run"

## Common Use Cases

**Monitor CI/CD:**
```
/loop 2m check if the GitHub Actions build has finished
```

**Watch for PR reviews:**
```
/loop 15m check if any PRs are waiting for my review
```

**Monitor a deployment:**
```
/loop 1m check if the deployment to staging is complete
```

**Poll an API or service:**
```
/loop 30s check the status of the background job
```

**Run tests repeatedly:**
```
/loop 5m run the test suite and report any failures
```

## Stopping a Loop

The loop stops when:
- User types "stop", "cancel", or "quit"
- User presses Ctrl+C
- A completion condition is met (optional — specify in the prompt)

To add a stop condition:
```
/loop 1m check if deploy is done — stop when status is "success" or "failed"
```

## Notes

- Loops should be used for genuinely recurring monitoring tasks
- Do not use for one-time tasks (just run the command directly)
- Keep loop intervals reasonable — very short intervals (< 10s) may rate-limit APIs
- If the recurring task takes longer than the interval, skip the next scheduled run and warn the user
