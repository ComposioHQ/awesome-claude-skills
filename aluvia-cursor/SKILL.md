---
name: aluvia-cursor
description: "Unblock web requests using Aluvia mobile carrier proxies. Use when hitting 403 Forbidden, Cloudflare challenges, CAPTCHAs, rate limits (429), IP bans, WAF blocks, empty responses, or when websites detect and block automated traffic. Routes traffic through real US mobile carrier IPs (AT&T, T-Mobile, Verizon) so websites treat your agent like a human."
---

# Aluvia Proxy: Unblock Web Requests with Mobile Carrier Proxies

## The Problem

Anti-bot systems block cloud-based and datacenter traffic. You get 403 Forbidden, CAPTCHAs, 429 rate limits, IP bans, or empty responses.

## The Solution

Aluvia routes traffic through **real US mobile carrier IPs** — the same IPs used by millions of people on their phones. Websites cannot distinguish your requests from legitimate mobile users.

The CLI manages headless Chromium sessions with automatic block detection and bypass. Every command returns structured JSON to stdout.

## Prerequisites Check

Before using any command, verify the environment:

```bash
# 1. Check API key is set (never log the full value)
echo "${ALUVIA_API_KEY:0:8}..."

# 2. Verify the CLI binary is available
aluvia help --json

# 3. Verify Playwright is installed (required for browser sessions)
node -e "require('playwright')"
```

If the API key is missing, tell the user to set `ALUVIA_API_KEY` from the [Aluvia dashboard](https://dashboard.aluvia.io). If `aluvia` is not found, run `npm install @aluvia/sdk`. If Playwright is missing, run `npm install playwright`.

## Core Commands Quick Reference

| Command                     | Purpose                              | Example                                                                             |
| --------------------------- | ------------------------------------ | ----------------------------------------------------------------------------------- |
| `session start <url>`       | Launch a headless browser session    | `aluvia session start https://example.com --auto-unblock --browser-session my-task` |
| `session close`             | Stop a running session               | `aluvia session close --browser-session my-task`                                    |
| `session list`              | List all active sessions             | `aluvia session list`                                                               |
| `session get`               | Get session details + block status   | `aluvia session get --browser-session my-task`                                      |
| `session rotate-ip`         | Rotate to a new upstream IP          | `aluvia session rotate-ip --browser-session my-task`                                |
| `session set-geo <geo>`     | Target IPs from a US region          | `aluvia session set-geo us_ca --browser-session my-task`                            |
| `session set-rules <rules>` | Add hostnames to proxy routing       | `aluvia session set-rules "example.com,api.example.com" --browser-session my-task`  |
| `account`                   | Show account info and balance        | `aluvia account`                                                                    |
| `account usage`             | Show bandwidth usage stats           | `aluvia account usage`                                                              |
| `geos`                      | List available geo-targeting regions | `aluvia geos`                                                                       |

## Standard Workflow

### 1. Start a session

Always use `--browser-session` to name your session. Always use `--auto-unblock` unless you need manual block control.

```bash
aluvia session start https://example.com --auto-unblock --browser-session my-task
```

The start command returns JSON with `browserSession`, `pid`, `cdpUrl`, `connectionId`, `blockDetection`, and `autoUnblock` fields. Save `browserSession` for subsequent commands.

### 2. Monitor for blocks

```bash
aluvia session get --browser-session my-task
```

Check the `lastDetection` object. Block scores: `blocked` >= 0.7, `suspected` >= 0.4, `clear` < 0.4. With `--auto-unblock`, blocks are remediated automatically.

### 3. Rotate IP if blocked

```bash
aluvia session rotate-ip --browser-session my-task
```

Returns a new `sessionId` (UUID). The next request uses a fresh IP.

### 4. Set geo-targeting if needed

```bash
aluvia session set-geo us_ca --browser-session my-task
```

### 5. Expand routing rules

If navigating to new domains that need proxying:

```bash
aluvia session set-rules "newsite.com,api.newsite.com" --browser-session my-task
```

Rules are appended to existing rules (not replaced).

### 6. Close the session when done

**Always close your session.** Sessions consume resources until explicitly closed.

```bash
aluvia session close --browser-session my-task
```

## Safety Constraints

1. **Always close sessions.** When your task finishes — success or failure — run `session close`. If uncertain whether a session exists, run `session list` first.
2. **Never expose the API key.** Reference `ALUVIA_API_KEY` by name only. Never log, print, or include its value in output.
3. **Check balance before expensive operations.** Run `aluvia account` and inspect `balance_gb` before long scraping tasks.
4. **Limit IP rotation retries to 3.** If rotating IP three times doesn't resolve a block, stop and report the issue — the site may use fingerprinting beyond IP.
5. **Prefer `--auto-unblock`.** Let the SDK handle block detection and remediation automatically.
6. **Prefer headless mode.** Only use `--headful` for debugging.
7. **Parse exit codes.** Exit code `0` = success, `1` = error with `{"error": "message"}`. Do not blindly retry on failure.
8. **Use named sessions.** Always pass `--browser-session <name>` to avoid ambiguity.
9. **Clean up on failure.** Close the session before retrying or aborting. Use `session close --all` as a last resort.
10. **One session per task.** Do not start multiple sessions unless the task explicitly requires parallel browsing.

## References

For detailed command specs, workflows, and troubleshooting:

- **Command reference:** [docs/command-reference.md](https://github.com/aluvia-connect/aluvia-skills/blob/main/docs/command-reference.md) — every flag, output schema, and error for all commands
- **Workflow recipes:** [docs/workflows.md](https://github.com/aluvia-connect/aluvia-skills/blob/main/docs/workflows.md) — step-by-step patterns for common scenarios
- **Troubleshooting:** [docs/troubleshooting.md](https://github.com/aluvia-connect/aluvia-skills/blob/main/docs/troubleshooting.md) — error messages, block score interpretation, recovery steps
