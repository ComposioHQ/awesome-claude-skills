---
name: auto-co-autonomous-company
description: Run an autonomous AI company with 14 specialized agents (CEO, CTO, CFO, Marketing, QA, etc.) that collaborate through structured workflows. Use when you want Claude Code to operate as a full product team — making decisions, writing code, deploying, and iterating without human intervention.
---

# Auto-Co: Autonomous AI Company Framework

Transform Claude Code into a fully autonomous AI company with 14 specialized agents modeled on world-class experts.

## What It Does

Auto-Co gives Claude Code a complete organizational structure:

- **14 AI agents** — CEO (Bezos), CTO (Vogels), CFO (Campbell), Marketing (Godin), QA (Bach), and 9 more
- **6 collaboration workflows** — New Product Evaluation, Feature Development, Product Launch, Pricing, Weekly Review, Opportunity Discovery
- **Autonomous loop** — Bash script that runs cycles continuously, each producing artifacts (code, deployments, docs)
- **Shared memory** — Cross-cycle consensus relay, human escalation protocol, structured document management
- **Safety red lines** — Hard guardrails preventing destructive operations

## When to Use This Skill

- You want Claude Code to run as a product team, not just a coding assistant
- You're building a product and want AI-driven decisions on strategy, pricing, marketing, and engineering
- You want structured multi-agent collaboration (not just one prompt)
- You're exploring autonomous AI systems

## Quick Start

```bash
git clone https://github.com/NikitaDmitrieff/auto-co-meta.git
cd auto-co-meta
cp .env.example .env
./auto-loop.sh
```

## How It Works

Each cycle:
1. Reads shared consensus (cross-cycle memory)
2. Forms a team of 3-5 relevant agents
3. Executes the next action (code, deploy, research, etc.)
4. Updates consensus with results and next steps

## Links

- **Repository**: [github.com/NikitaDmitrieff/auto-co-meta](https://github.com/NikitaDmitrieff/auto-co-meta)
- **Landing page**: [runautoco.com](https://runautoco.com)
- **License**: MIT
