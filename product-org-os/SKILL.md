---
name: product-org-os
description: An entire product organization as AI agents — 133 skills, 13 agents, and 2 gateways for product management, strategy, GTM, competitive intelligence, and more.
---

# Product Org OS

An entire product organization that becomes your superpower. 13 specialized agents collaborate like a real product team — each with a distinct role, perspective, and expertise. Built on the Agent Skills open standard — works with Claude Code, Cursor, Copilot, Gemini CLI, and other compatible tools.

## When to Use This Skill

- You need to write PRDs, feature specs, or user stories
- You want strategic analysis — pricing, positioning, competitive landscape
- You're planning a product launch or GTM strategy
- You need a business case, roadmap, or portfolio review
- You want multiple product perspectives on a decision (e.g., PM vs. VP Product vs. Marketing)

## What This Skill Does

1. **13 product agents** with distinct roles: Product Manager, CPO, VP Product, Director PM, Director PMM, PMM, Product Mentor, BizOps, BizDev, Competitive Intelligence, Product Operations, Value Realization, and UX Lead
2. **133 skills** covering strategy, requirements, GTM, competitive analysis, business operations, and organizational learning
3. **2 gateways** that route requests to the right agent(s) — Product Gateway and Product Leadership Team (multi-stakeholder mode)
4. **10 knowledge packs** providing domain expertise agents draw from
5. **Context system** that tracks decisions, assumptions, and learnings across sessions

## How to Use

### Install

Point your agent at the [agent guide](https://github.com/yohayetsion/product-org-os/blob/main/product-org-plugin/agent-guide.md) — it handles the rest.

Or install directly in Claude Code:
```bash
claude plugins install github:yohayetsion/product-org-os
```

### Basic Examples

```
# Write a PRD
/pm write a PRD for user authentication

# Get strategic perspective
@vp-product evaluate our pricing strategy

# Competitive analysis
@competitive-intelligence analyze the CRM market landscape
```

### Advanced Examples

```
# Multi-stakeholder product decision
@product-leadership-team should we build or buy this capability?

# Route to the right agent automatically
@product we need to plan the Q3 launch

# Business case analysis
@bizops build a business case for expanding into the SMB segment
```

## Practical Example

**User prompt:**
```
@pm write a PRD for adding SSO support to our platform
```

**What happens:**
The Product Manager agent activates, checks for relevant context from prior decisions, and produces a structured PRD with problem statement, user stories, acceptance criteria, and success metrics — written in a conversational, first-person voice as a colleague would deliver it.

## Tips

- Use `@agent-name` to spawn a specific agent autonomously
- Use `/skill-name` to invoke a skill inline (Claude adopts the persona)
- Use `@product` to let the gateway route to the right agent
- Use `@product-leadership-team` for decisions that need multiple perspectives
- Agents remember context across sessions — prior decisions inform future work

## Common Use Cases

| Use Case | Agent/Skill |
|----------|-------------|
| Write a PRD | `@pm` or `/prd` |
| Pricing strategy | `@vp-product` or `/pricing-strategy` |
| Competitive analysis | `@competitive-intelligence` or `/competitive-landscape` |
| Launch planning | `/launch-plan` or `@product-operations` |
| Business case | `@bizops` or `/business-case` |
| GTM strategy | `@director-product-marketing` or `/gtm-strategy` |
| Portfolio review | `@product-leadership-team` |

## Attribution

Created by [Yohay Etsion](https://github.com/yohayetsion). Open source under MIT license.

Learn more: [Product Org OS](https://yohayetsion.github.io/product-org-os/) | [GitHub](https://github.com/yohayetsion/product-org-os)
