---
name: steel-browser
description: Use Steel cloud browsers and CLI commands for session-backed web automation, scraping, screenshots, PDFs, and multi-step browser workflows.
---

# Steel Browser

Use this skill when a task needs a real browser instead of plain fetches or one-off scripts. It gives Claude a reliable path for navigation, extraction, screenshots, PDFs, and multi-step flows with persistent browser state.

## When to Use This Skill

- The task involves navigating websites, clicking buttons, filling forms, or logging in.
- The page is dynamic or JS-heavy and basic HTTP fetches are incomplete or brittle.
- The user wants screenshots or PDFs as artifacts.
- The workflow spans multiple browser steps and needs persistent session state.

## What This Skill Does

1. **Session-backed browsing**: Starts named browser sessions so a workflow can keep state across steps.
2. **Extraction and artifacts**: Uses `steel scrape`, screenshots, and PDFs to capture content and evidence.
3. **Interactive automation**: Opens pages, inspects interactive elements, clicks, fills, waits, and verifies outcomes.

## How to Use

### Basic Usage

```text
Use the steel-browser skill to log into this site, navigate to the billing page, and save a screenshot.
```

### Advanced Usage

```text
Use the steel-browser skill to extract the product list from this JS-heavy page, then capture a PDF and a screenshot of the final state.
```

## Example

**User**: "Use the steel-browser skill to open the dashboard, export the report, and save evidence."

**Output**:
```bash
npm i -g @steel-dev/cli
steel login
SESSION="report-job"
steel browser start --session "$SESSION"
steel browser open https://example.com/dashboard --session "$SESSION"
steel browser snapshot -i --session "$SESSION"
steel browser click @e1 --session "$SESSION"
steel browser wait --text "Export complete" --session "$SESSION"
steel browser screenshot ./report.png --session "$SESSION"
steel browser pdf ./report.pdf --session "$SESSION"
steel browser stop --session "$SESSION"
```

**Credit:** Based on Steel's browser automation workflow in `steel-dev/cli`.

## Tips

- Use `steel scrape <url> --format markdown` first when the goal is content extraction, not interaction.
- Reuse the same `--session <name>` across all browser commands in one workflow.
- Re-run `steel browser snapshot -i --session <name>` after major page changes before clicking again.

## Common Use Cases

- Browser automation for login flows, forms, and dashboards.
- Capturing screenshots or PDFs for QA, compliance, or evidence.
- Extracting content from dynamic websites that need a live browser session.
