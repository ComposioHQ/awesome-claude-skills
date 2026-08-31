---
name: business-chain-diagnosis
description: Assesses whether a digital product or SaaS design closes the business loop: market research first, 7-stage 0-10 scoring, complete fix plans, and re-checks.
---

# Business Loop Diagnosis

Assesses whether a digital product / SaaS / software / App / subscription design closes the business loop, helping creators build business thinking. Strictness is about depth of thinking and demand alignment — not about having interviews or usage data, which a solo founder naturally lacks at the start. Clearly flag missing evidence for projects of others; never speculate.

## When to Use This Skill

- You want to check whether your own digital product / SaaS design closes the business loop, or want the AI to help build business thinking
- You provide a GitHub repo, a local project directory, or a product description and ask whether its business loop holds
- After a diagnosis you want a complete, executable fix plan per problem (goal, concrete changes, steps, acceptance criteria)
- You want a self-check Q&A, deeper evidence via interview, unit-economics (LTV/CAC) calculation, or productization output (pitch / landing page)
- Not for: pure technical implementation, code review, or questions unrelated to business model

## What This Skill Does

1. **Market research first**: runs `references/market_research.py` to search the web for 8 market metrics (user persona, market scope, pain points, willingness to pay, payment habits, competitors, market size, channels) and scores each 0-10 with evidence; when no API key is set it degrades to a search plan + agent-filled evidence form, and adds a free Hacker News community capture.
2. **Two modes**: Self-Check (the creator answers one question at a time across the 7 stages) and Project Inspection (inspects a GitHub repo / local project / product description, then asks an ownership gate — your own project vs someone else's — and branches accordingly).
3. **7-stage scoring**: Market Research → Real Demand → Value Proposition → Acquisition → Paid Conversion → Delivery & Experience → Retention & Referral, each 0-10, with strict verdict rules (Loop Closed / Nearly Closed / Not Closed) and hard gates (e.g., no retention or referral design at all → no higher than 2).
4. **Complete repair plans**: outputs a full fix plan per problem (goal, concrete changes, steps, acceptance criteria) for the user to execute; the AI refines plans, answers questions, and re-checks — it never modifies the product directly.
5. **Evidence-first**: stages without evidence are capped at 3 and flagged; low scores on others' projects distinguish "insufficient evidence" from "missing design", never declaring the product a failure.
6. **Extras**: Mom Test interview coach, community-signal capture, unit-economics calculator (LTV/CAC, margin, payback), growth-experiment templates, productization (pitch / landing hero / pricing cards), and a shareable Markdown report with a re-check baseline.

## How to Use

### Basic Usage

```
Use the business-chain-diagnosis skill to review my product: <one-line description>
```

### Advanced Usage

```
Use the business-chain-diagnosis skill to inspect this project: <GitHub repo URL or local directory>
```

## Example

**User**: "Check whether this project closes the business loop: https://github.com/QundaiCai314/pufa-hackathon-ai"

**Output**:
```
Report: per-stage diagnosis, seven 0-10 scores, verdict, problem list, and a complete fix plan per problem.
Ownership gate: "Is this your project or someone else's?" → your own → one-question-at-a-time follow-up; others → report from public evidence only.
Re-check: after fixes, re-run and compare score changes against the saved baseline.
```

**Inspired by:** Lean Canvas, the Mom Test, and the AARRR framework.

## Tips

- Run `references/market_research.py` before scoring; Market Research scores at most 3 without it
- Check demand alignment precisely: "segment + decision state + scenario" (e.g., "undecided about going overseas" vs "decided, choosing a tool" are different needs and cannot be conflated)
- No interviews or usage data at the start is normal — not a low-score reason; being unable to state the user or misaligning the demand is
- Fixes proceed one item at a time; the user executes, the AI designs plans and re-checks
- Output language follows the user's language; the full repo (Dandelion) ships bilingual docs

## Common Use Cases

- Pre-launch self-check: a creator sanity-checks their SaaS/App via Q&A before launch and gets scores, weak spots, and fix priorities
- Evaluating someone else's open-source repo from public evidence only
- Demand alignment clarification (segment + decision state + scenario)
- Retention & referral design checks with complete fix plans
- Pre-launch / pre-pitch business-loop health check with a shareable report
