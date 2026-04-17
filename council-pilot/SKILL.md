---
name: council-pilot
description: Build an expert council from public sources and autonomously drive projects to production maturity. Give it a one-liner, it works for hours through build-score-debug loops until 100/100.
license: MIT
---

# Council Pilot

Give Claude Code a one-liner. Get a production-quality project.

Council Pilot builds an expert council from public sources, then autonomously drives your project through build-score-debug loops until it reaches **100/100 maturity**. No micromanagement. No prompt-chaining. One sentence, hours of focused work.

## Quick Start

```
/council-pilot "Build a real-time collaborative whiteboard with WebSocket sync"
```

## How It Works

**Phases 1-4** (setup): Parse your idea into a domain spec. Web-search for real domain experts. Distill their public work into reasoning lenses. Form an expert council with chair/reviewer/advocate/skeptic roles.

**Phases 5-9** (loop): Build project code guided by expert lenses. Run 6-stage verification (build, types, lint, tests, security, diff). Rescore through adversarial council debate. Fill gaps by adding new experts or targeting weak axes. Repeat.

**Phase 10** (submit): Push branch, create PR with full maturity report.

## Why This Is Different

1. **It works autonomously for hours.** A typical run takes 2-3 hours and produces a complete version iteration.
2. **It self-critiques like a senior engineer.** The council debates every scoring decision. Points are earned, not given.
3. **It's infinitely adaptable.** Swap domains, get a completely different expert council.

## The Scoring Rubric

Each axis is scored 0-25 by the expert council. Convergence requires 100/100:

| Axis | What It Measures |
|------|-----------------|
| **Breadth** | Domain coverage completeness |
| **Depth** | Expert profile richness and detail |
| **Thickness** | Practical implementability |
| **Effectiveness** | Problem-solution fit |

## Source Gates

- **Tier A**: Official pages, papers, books — defines core beliefs
- **Tier B**: Interviews, essays, course notes — shapes reasoning patterns
- **Tier C**: Social posts, forums — context only, cannot define core claims

## CLI

15 standalone CLI commands for manual operation:

```bash
python3 scripts/expert_distiller.py init --root ./forum --domain "AI Reliability" --topic "LLM hallucination detection"
python3 scripts/expert_distiller.py council create --root ./forum --domain "AI Reliability"
python3 scripts/expert_distiller.py score --root ./forum --domain "AI Reliability"
python3 scripts/expert_distiller.py report --root ./forum --domain "AI Reliability" --format markdown
```

## Trust Model

Expert profiles are **analysis lenses**, not primary evidence. Council Pilot never fabricates quotes, invents private beliefs, or uses Tier C sources to define core claims. Current data and user constraints always outrank expert memory.

## Repository

https://github.com/wd041216-bit/council-pilot