---
name: founder-os
description: Multi-agent primitives for Claude Code: consensus, debate, fanout research, skill building, and measured optimization.
---

# founder-os

`founder-os` helps Claude Code users get a more reliable answer than a single pass by coordinating multiple agent runs and synthesizing where they agree, disagree, and notice outliers.

## When to Use This Skill

- You need a second opinion on an architecture, API, product, or debugging decision.
- You want several independent research passes before synthesizing the answer.
- You want a debate-room style critique before committing to a plan.
- You want a measured optimization loop for a numeric metric.

## What This Skill Does

1. **Stochastic consensus**: Poll N agents with the same prompt and aggregate consensus, divergences, and outliers.
2. **Debate synthesis**: Spawn several agents into a shared debate room, then merge the strongest arguments.
3. **Fanout research**: Run researchers in parallel so different angles are covered before synthesis.
4. **Skill building**: Build Claude Code skills that exploit variance, parallelism, measurement, or another concrete advantage.
5. **Measured optimization**: Hill-climb improvements when there is a numeric automatable metric.

## How to Use

Install as a Claude Code plugin:

```bash
claude plugin install rhinehart514/founder-os
```

Then try:

```text
/founder-os:stochastic n=10 Should we use Postgres or SQLite for this project?
```

## Example

**User**: `/founder-os:stochastic n=10 Should this app use Postgres or SQLite?`

**Output**:

```text
Consensus
- Postgres is safer for concurrent users, backups, and analytics.
- SQLite is better for a local-first prototype or single-user workflow.

Divergences
- 6/10 agents preferred Postgres immediately.
- 3/10 preferred SQLite until there is real multi-user pressure.
- 1/10 suggested starting SQLite with a planned migration boundary.

Outliers
- Add a repository layer now so the storage decision stays reversible.
- Use the first paying/team user as the migration trigger.
```

**Inspired by:** Claude Code subagent workflows where one confident answer is not enough.
