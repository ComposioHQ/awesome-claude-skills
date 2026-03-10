---
name: progressive-estimation
description: "Estimate AI-assisted and hybrid human+agent development work with research-backed formulas, PERT statistics, and calibration feedback loops."
---

## Progressive Estimation

An AI skill for estimating AI-assisted and hybrid human+agent development work. Adapts to your team's working mode — human-only, hybrid, or agent-first — with the right velocity model for each.

## When to Use This Skill

- When you need time/effort estimates for AI-assisted development tasks
- When sizing a backlog of issues (batch mode handles 5 or 500)
- When planning staffing with a mix of humans and AI agents
- When you want PERT-based statistical estimates instead of gut feelings
- When you need estimates formatted for your tracker (Linear, JIRA, ClickUp, GitHub Issues, Monday, GitLab)

## What This Skill Does

1. Detects your team's working mode (human-only, hybrid, or fully-agentic)
2. Applies research-backed multipliers for AI-assisted work (grounded in empirical studies)
3. Produces PERT expected values with confidence bands (P50, P75, P90)
4. Separates "expected" from "committed" estimates at your chosen confidence level
5. Supports batch estimation — paste a list of issues, get estimates for all
6. Outputs in formats ready for your project tracker
7. Includes a calibration system to improve accuracy over time with actuals

## How to Use

### Basic Usage
Ask Claude to estimate a task:
> "Estimate how long it will take to build a REST API with authentication"

### Advanced Usage
Paste a batch of issues:
> "Estimate these 12 JIRA tickets for our next sprint"

The skill will ask clarifying questions about team composition, complexity, and working mode before producing estimates.

## Example

**Input:** "Estimate building a user authentication system with OAuth2"

**Output:** The skill produces a structured estimate including:
- Task classification (size, complexity, risk)
- PERT expected value (e.g., 3.2 days)
- Confidence bands (P50: 2.8d, P75: 4.1d, P90: 5.5d)
- Committed estimate at chosen confidence level
- Formatted output for your tracker

## Tips

- Start with a single task to calibrate, then move to batch mode
- Feed back actuals to improve future estimates via the calibration system
- Use "instant mode" for quick T-shirt sizing without full PERT analysis
- The skill adapts formulas based on whether agents handle 30%, 60%, or 90%+ of work

## Common Use Cases

- Sprint planning with AI-assisted development teams
- Backlog grooming and story point assignment
- Staffing and capacity planning with agent multipliers
- Comparing human-only vs hybrid vs agent-first timelines
- Release date forecasting with confidence intervals
