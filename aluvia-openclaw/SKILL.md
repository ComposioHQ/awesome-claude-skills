---
name: aluvia
description: "Stop your AI agent from getting blocked. Aluvia routes traffic through real US mobile carrier IPs (AT&T, T-Mobile, Verizon) so websites treat your agent like a human. Bypasses Cloudflare, DataDome, PerimeterX, Akamai Bot Manager, and other anti-bot systems automatically. Use when your agent hits 403 Forbidden, Cloudflare challenges, CAPTCHAs, rate limits (429), IP bans, empty responses, or WAF blocks. Features auto block detection and bypass, one-command IP rotation, US geo-targeting, dynamic proxy routing rules, and managed headless Chromium via Playwright — all through a JSON-first CLI built for AI agents."
metadata:
  {
    "openclaw":
      {
        "requires": { "bins": ["aluvia"], "env": ["ALUVIA_API_KEY"] },
        "primaryEnv": "ALUVIA_API_KEY",
        "emoji": "🌐",
      },
  }
---

# Aluvia Proxy: Unblock agent browser with proxies + playwright

## The Problem

Your OpenClaw agent gets blocked because anti-bot systems are built to stop cloud-based agent/bot traffic with datacenter IP addresses. You get 403 Forbidden, CAPTCHAs, 429 rate limits, IP bans, empty responses.

## The Solution

Aluvia routes your agent's traffic through **real US mobile carrier IPs** — the same IPs used by millions of real people on their phones. Websites cannot distinguish your agent from a legitimate user browsing on a mobile device.

Aluvia's proxies + Playwright + Chrome stack: detects website blocks and routes your agent's traffic through a clean mobile IP when necessary. All automatically. All without proxy configs. All without building custom routing rules.

## Features

- **Mobile carrier residential proxies** — Not datacenter or shared residential IPs. Real mobile carrier IPs that websites inherently trust. Highest-quality proxy tier available.
- **Automatic block detection and bypass** — Every page load is scored 0.0–1.0. Detects Cloudflare challenges, CAPTCHAs, 403/429 responses, soft blocks, and empty pages. With `--auto-unblock`, blocks are remediated automatically by rerouting through proxy and reloading.
- **One-command IP rotation** — Rotate to a fresh mobile IP mid-session without restarting the browser. Break through persistent blocks and rate limits instantly.
- **US geo-targeting** — Pin your exit IP to a specific US state (California, New York, Texas, etc.) for location-sensitive scraping and content access.
- **Dynamic proxy routing rules** — Proxy only the domains that need it. Add or remove hostnames on the fly as your agent navigates across sites and discovers new endpoints.
- **Managed headless Chromium with Playwright** — Full browser sessions with Chrome DevTools Protocol (CDP) access. No browser setup, no stealth plugins, no fingerprint patching required.
- **JSON-first CLI built for agents** — Every command returns structured JSON to stdout. Designed for programmatic use by AI agents, not for humans typing in a terminal.

## Installation

```bash
npm install -g @aluvia/sdk
```

Or use directly with npx (no install needed):

```bash
npx aluvia help
```

## CLI Interface

- Every command outputs a single JSON object to stdout. Parse it with your JSON tool.
- Exit code `0` = success, `1` = error. Errors return `{"error": "message"}`.
- The CLI manages long-running browser daemons — start a session, interact via the `exec` tool, close when done.
- Block detection scores pages 0.0-1.0: `blocked` >= 0.7, `suspected` >= 0.4, `clear` < 0.4.
- `--auto-unblock` handles most blocks automatically by adding hostnames to proxy rules and reloading.

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

If the API key is missing, direct the user to create one at the [Aluvia dashboard](https://dashboard.aluvia.io) and set `ALUVIA_API_KEY`. If `aluvia` is not found, run `npm install @aluvia/sdk`. If Playwright is missing, run `npm install playwright`.

## Core Commands Quick Reference

| Command                     | Purpose                                                 | Common Usage                                                                        |
| --------------------------- | ------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| `session start <url>`       | Launch a headless browser session                       | `aluvia session start https://example.com --auto-unblock --browser-session my-task` |
| `session close`             | Stop a running session                                  | `aluvia session close --browser-session my-task`                                    |
| `session list`              | List all active sessions                                | `aluvia session list`                                                               |
| `session get`               | Get session details + block detection + connection info | `aluvia session get --browser-session my-task`                                      |
| `session rotate-ip`         | Rotate to a new upstream IP                             | `aluvia session rotate-ip --browser-session my-task`                                |
| `session set-geo <geo>`     | Target IPs from a specific US region                    | `aluvia session set-geo us_ca --browser-session my-task`                            |
| `session set-rules <rules>` | Add hostnames to proxy routing                          | `aluvia session set-rules "example.com,api.example.com" --browser-session my-task`  |
| `account`                   | Show account info and balance                           | `aluvia account`                                                                    |
| `account usage`             | Show bandwidth usage stats                              | `aluvia account usage`                                                              |
| `geos`                      | List available geo-targeting regions                    | `aluvia geos`                                                                       |
| `help`                      | Show help (use `--json` for structured output)          | `aluvia help --json`                                                                |

## Standard Workflow

### 1. Start a session

Always use `--browser-session` to name your session. Always use `--auto-unblock` unless you need manual block control.

```bash
aluvia session start https://example.com --auto-unblock --browser-session my-task
```

### 2. Parse the JSON output

The start command returns:

```json
{
  "browserSession": "my-task",
  "pid": 12345,
  "startUrl": "https://example.com",
  "cdpUrl": "http://127.0.0.1:38209",
  "connectionId": 3449,
  "blockDetection": true,
  "autoUnblock": true
}
```

Save `browserSession` — you need it for every subsequent command.

**If the agent uses the OpenClaw browser tool:** create a remote CDP profile with this session's `cdpUrl` and use that profile for all browser commands. See [OpenClaw browser integration](https://github.com/aluvia-connect/aluvia-skills/blob/main/docs/integrations/openclaw-browser.md).

### 3. Monitor for blocks

Check session status including the latest block detection result:

```bash
aluvia session get --browser-session my-task
```

Look at the `lastDetection` object in the response. If `blockStatus` is `"blocked"` and `--auto-unblock` is on, the SDK already handled it. If blocks persist, escalate:

### 4. Rotate IP if blocked

```bash
aluvia session rotate-ip --browser-session my-task
```

Returns a new `sessionId` (UUID). The next request through the proxy uses a fresh IP.

### 5. Set geo-targeting if needed

Some sites serve different content or apply different blocks by region:

```bash
aluvia session set-geo us_ca --browser-session my-task
```

### 6. Expand routing rules

If your agent navigates to new domains that need proxying, add them dynamically:

```bash
aluvia session set-rules "newsite.com,api.newsite.com" --browser-session my-task
```

Rules are appended to existing rules (not replaced).

### 7. Close the session when done

**Always close your session.** Sessions consume resources until explicitly closed.

```bash
aluvia session close --browser-session my-task
```

## Safety Constraints

Follow these rules in every interaction:

1. **Always close sessions.** When your task finishes — success or failure — run `session close`. If uncertain whether a session exists, run `session list` first.
2. **Never expose the API key.** Reference `ALUVIA_API_KEY` by name only. Never log, print, or include its value in output.
3. **Check balance before expensive operations.** Run `aluvia account` and inspect `balance_gb` before long scraping tasks.
4. **Limit IP rotation retries to 3.** If rotating IP three times doesn't resolve a block, stop and report the issue — the site may use fingerprinting beyond IP.
5. **Prefer `--auto-unblock`.** Let the SDK handle block detection and remediation automatically. Only disable it when you need manual control over routing decisions.
6. **Prefer headless mode.** Only use `--headful` for debugging. Headless is faster and uses fewer resources.
7. **Parse exit codes.** Always check the exit code. On exit code 1, parse the `error` field and handle it — do not blindly retry.
8. **Use named sessions.** Always pass `--browser-session <name>` to avoid ambiguity errors when multiple sessions run.
9. **Clean up on failure.** If any step fails, close the session before retrying or aborting. Use `session close --all` as a last resort.
10. **One session per task.** Do not start multiple sessions unless the task explicitly requires parallel browsing of different sites.

## References

For detailed command specs, workflows, and troubleshooting:

- **Command reference:** [docs/command-reference.md](https://github.com/aluvia-connect/aluvia-skills/blob/main/docs/command-reference.md) — every flag, output schema, and error for all 11 commands
- **Workflow recipes:** [docs/workflows.md](https://github.com/aluvia-connect/aluvia-skills/blob/main/docs/workflows.md) — step-by-step patterns for common scenarios
- **Troubleshooting:** [docs/troubleshooting.md](https://github.com/aluvia-connect/aluvia-skills/blob/main/docs/troubleshooting.md) — error messages, block score interpretation, signal names, recovery steps
- **agent-browser integration:** [docs/integrations/agent-browser.md](https://github.com/aluvia-connect/aluvia-skills/blob/main/docs/integrations/agent-browser.md) — using Aluvia CDP with [agent-browser](https://www.npmjs.com/package/agent-browser) CLI
- **OpenClaw browser integration:** [docs/integrations/openclaw-browser.md](https://github.com/aluvia-connect/aluvia-skills/blob/main/docs/integrations/openclaw-browser.md) — using Aluvia CDP with [OpenClaw browser tool](https://docs.openclaw.ai/tools/browser)
