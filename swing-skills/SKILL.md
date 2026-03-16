---
name: swing
description: 6 cognitive firewalls that fix the most common AI reasoning failures — source verification, default challenging, reasoning exposure, stress testing, failure prediction, and exhaustive analysis.
---

# Swing

AI coding agents have a problem nobody talks about. They pick the safe default instead of the right answer. They agree when they should push back. They hide their reasoning behind confident conclusions. They assume everything will work on the first try.

I built Swing because I kept getting burned by these failures in real projects. Every skill in this set exists because I personally hit a wall where the default AI behavior gave me a wrong answer, a shallow review, or a plan that fell apart the moment it touched production.

## The 6 Firewalls

1. cross-verified-research — Forces the AI to verify claims across multiple sources and label each source by credibility tier, instead of giving you a single confident answer that might be completely wrong.

2. adversarial-review — Turns the AI into a Devil's Advocate that stress-tests your code, architecture, and decisions from three attack vectors. Finds the problems you would have discovered in production.

3. creativity-sampler — Generates probability-weighted alternative options instead of jumping to the obvious choice. Surfaces unconventional approaches that are often better than the default.

4. reasoning-tracer — Forces the AI to show its entire reasoning chain as an auditable artifact. No more opaque conclusions — you see every assumption, every branch point, every weak link.

5. pre-mortem — Assumes your plan has already failed and works backward to figure out why. Based on Gary Klein's technique. Catches failure modes that optimism bias would normally hide.

6. deep-dive-analyzer — Breaks any subject into atomic components and examines every facet. When you need to truly understand something before making changes, not just skim the surface.

## How to Use

Install all 6 at once:

```bash
npx skills add whynowlab/swing-skills --all
```

Or pick individual skills:

```bash
npx skills add whynowlab/swing-skills/cross-verified-research
```

Works with Claude Code and any agent that supports the Agent Skills open standard.

## Why This Exists

These skills came from 30+ prompt patterns I developed and refined in Korean over months of daily AI-assisted development. When I saw the same reasoning failures happening over and over, I turned the fixes into reusable skills so other developers would not have to learn these lessons the hard way.

Every firewall solves a specific, documented failure mode. Nothing is theoretical — each one was born from a real mistake.
