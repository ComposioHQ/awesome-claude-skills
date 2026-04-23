---
name: tokrepo-search
description: Find installable AI skills, MCP servers, prompts, and workflows from TokRepo when a user asks to discover or install an AI tool.
---

# TokRepo Search

TokRepo Search helps Claude find practical, installable AI assets from TokRepo, an open registry for skills, prompts, MCP configs, scripts, and workflows.

## When to Use This Skill

- The user asks to find or discover an AI tool, Claude skill, MCP server, prompt, or workflow
- The user wants an install command instead of a long manual setup
- The user wants options for a specific use case such as code review, database access, or content creation
- The user mentions TokRepo directly

## What This Skill Does

1. **Searches TokRepo**: Finds relevant AI assets by keyword or use case.
2. **Summarizes matches**: Explains what each asset does in plain language.
3. **Provides install paths**: Gives the right `npx tokrepo install` command or product link.
4. **Shows alternatives**: Offers a small shortlist when more than one asset could fit.

## How to Use

### Basic Usage

If command execution is available, search with:

```bash
npx tokrepo search "<query>"
```

Examples:

```bash
npx tokrepo search "claude code review"
npx tokrepo search "mcp postgres"
npx tokrepo search "prompt writing"
```

### Advanced Usage

After finding a match, install it with:

```bash
npx tokrepo install <uuid-or-name>
```

If terminal access is not available, use https://tokrepo.com to inspect the asset page and explain the setup steps clearly.

## Example

**User**: "Find me a Claude skill for code review and show me how to install it."

**Output**:

```text
I found a few relevant TokRepo entries for code review.

1. <Asset title>
   - What it does: Reviews code changes and highlights likely issues
   - Install: npx tokrepo install <uuid>

2. <Asset title>
   - What it does: Focuses on security-oriented code review
   - Install: npx tokrepo install <uuid>
```

**Inspired by:** TokRepo's search-and-install workflow for AI assets.

## Tips

- Prefer a short shortlist over a long dump of results
- Always include the install command when available
- If the user is unsure, suggest the most broadly useful option first

## Common Use Cases

- Finding a Claude Code skill for a specific engineering task
- Discovering an MCP server for databases, GitHub, or chat tools
- Recommending prompts or workflows that can be installed quickly
