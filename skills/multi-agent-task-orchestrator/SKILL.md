---
name: multi-agent-task-orchestrator
description: Coordinate multiple Claude Code agents through a single orchestrator with anti-duplication and quality gates
tags: [orchestration, multi-agent, delegation, quality-assurance]
author: milkomida77
source: https://github.com/milkomida77/guardian-agent-prompts
---

# Multi-Agent Task Orchestrator

A production-tested skill for coordinating multiple Claude Code agents through a single orchestrator that routes tasks, prevents duplicates, and enforces quality gates.

## What it does

- **Task routing**: Routes tasks to specialized agents using keyword scoring (security → hak agent, trading → trading agent, code → codex agent)
- **Anti-duplication**: SQLite registry with 55% similarity threshold prevents the same task from being assigned twice
- **Quality gates**: 5-step verification before marking any task "done" (file diff, tests, secrets scan, build, scope check)
- **Heartbeat monitoring**: 30-minute cycles catch stale or abandoned assignments

## Usage

Add to your  directory:



## Key patterns

### Delegation format


### Quality gate checklist


## Results

- Battle-tested across 10,000+ production tasks
- Coordinates 57 specialized agents
- ~8% rejection rate on unverified "done" claims
- 55% similarity threshold catches near-duplicates without false positives

## Source

Open source: [guardian-agent-prompts](https://github.com/milkomida77/guardian-agent-prompts)
