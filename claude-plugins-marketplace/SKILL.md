---
name: claude-plugins-marketplace
description: A curated marketplace of 25+ open-source Claude Code plugins and MCP servers for development, testing, code review, and business workflows. Install the full registry or individual plugins.
---

# Claude Plugins Marketplace (2389 Research)

A curated registry of 25+ open-source Claude Code plugins and MCP servers maintained by [2389 Research](https://2389.ai). Covers development workflows, testing and quality, code review, business strategy, and utilities.

## When to Use This Skill

- You want a collection of production-tested Claude Code plugins instead of building from scratch
- You need testing and code review workflows (iterative refinement, parallel exploration, multi-agent review)
- You want MCP servers for journaling, social media, or Slack integration
- You're building multi-agent systems and want proven architecture patterns

## What This Skill Does

1. **Plugin Registry**: A `marketplace.json` catalog of all available plugins with metadata, keywords, and install URLs
2. **Development Plugins**: CSS workflows, Firebase development, landing page design, iOS development with xtool, multi-agent system architecture
3. **Testing & Quality Plugins**: Iterative artifact refinement (simmer), parallel approach exploration (test-kitchen), pre-commit sanity checks (fresh-eyes-review), multi-agent code review (review-squad), end-to-end scenario testing, documentation auditing
4. **Business Plugins**: Go-to-market strategy, product launch materials, meeting summarization, decision-making frameworks
5. **MCP Servers**: Private journaling, social media, Slack integration, and AI behavior modification

## Key Plugins

### simmer — Iterative Artifact Refinement
Runs an iterative refinement loop on any artifact using subagent judge feedback against user-defined criteria. Produces progressively better results through investigation-first evaluation.

### test-kitchen — Parallel Exploration
Explores multiple implementation approaches in parallel and lets you pick the best one. Useful when there are several valid ways to solve a problem.

### fresh-eyes-review — Pre-Commit Sanity Check
A final review before committing or creating a PR. Catches security issues, missing edge cases, and things that look off after you've been staring at code too long.

### review-squad — Multi-Agent Code Review
Dispatches panels of specialized subagents to review projects from different perspectives: expert reviewers, normie first impressions, task-based user testing, and pedantic nitpickers.

### prbuddy — PR Health Assistant
Monitors CI status, triages review comments, and fixes issues with systematic prevention. Keeps PRs moving toward merge.

## How to Use

### Install the Full Marketplace

```bash
claude /plugin marketplace add 2389-research/claude-plugins
```

### Install Individual Plugins

```bash
# Testing and quality
claude /install 2389-research/simmer
claude /install 2389-research/test-kitchen
claude /install 2389-research/fresh-eyes-review
claude /install 2389-research/review-squad

# Development
claude /install 2389-research/css-development
claude /install 2389-research/firebase-development
claude /install 2389-research/building-multiagent-systems
```

### Browse the Marketplace

Visit the marketplace site: [2389-research.github.io/claude-plugins](https://2389-research.github.io/claude-plugins)

Or browse the registry directly: [github.com/2389-research/claude-plugins](https://github.com/2389-research/claude-plugins)

## Example

**User**: "Review this project before I ship it"

With `review-squad` installed, Claude dispatches parallel expert reviewers — security, performance, UX, and architecture — each providing focused feedback from their specialty.

**User**: "Try three different approaches to this pagination system"

With `test-kitchen` installed, Claude explores multiple implementations in parallel and presents each for comparison before you commit to one.

## All Available Plugins

| Category | Plugins |
|----------|---------|
| Development | css-development, firebase-development, landing-page-design, xtool, building-multiagent-systems, speed-run, binary-re |
| Testing & Quality | test-kitchen, simmer, scenario-testing, fresh-eyes-review, documentation-audit, review-squad, prbuddy, git-repo-prep |
| Business & Strategy | ceo-personal-os, gtm-partner, product-launcher, worldview-synthesis, deliberation, summarize-meetings |
| Utilities | terminal-title, remote-system-maintenance |
| MCP Servers | agent-drugs, socialmedia, journal, slack-mcp |

## Tips

- Start with `simmer` and `fresh-eyes-review` — they improve any existing workflow
- `review-squad` works best on projects with multiple files and concerns
- `test-kitchen` shines when you're unsure which approach to take
- All plugins are open-source and individually installable — you don't need the full marketplace

**Credit:** Built by [2389 Research](https://2389.ai), an AI research and product company.
