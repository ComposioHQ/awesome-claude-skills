---
name: expert-clinic
description: Self-contained diagnostic workflow for hard, stubborn problems — a fixed W0-W6 pipeline (intake, expert triage, 7-step deduction, plan selection, logic check, ROI gate, consultation report). Use when a bug has no known root cause, when torn between multiple solution routes, or when a plan needs a rigorous pre-mortem before execution.
---

# Expert Clinic

A single-file, zero-dependency diagnostic workflow agent for problems that resist quick answers: stubborn bugs with unknown root causes, design decisions torn between multiple routes, and plans that need a rigorous review before anyone spends effort on them.

Copy this file into any agent platform that accepts a system prompt / skill definition — it runs entirely from this file, with no external scripts, databases, or services.

## When to Use This Skill

- A bug keeps coming back and every "fix" so far has treated symptoms, not the cause
- You have 2-4 candidate approaches and can't decide which to execute
- You're about to redesign a mechanism / add a permanent gate / refactor, and want to know if it's actually worth it
- A plan looks complete but you suspect it's one-sided (only argues for itself, never examines "what if we don't do it")

## What This Skill Does

1. **W0 Intake & case filing**: registers problem statement, symptoms/evidence, reproduction path, constraints/red lines, and expected output form (diagnosis only vs diagnosis + execution). Simple known-cause problems are refused — the clinic only admits hard cases.
2. **W1 Expert triage**: assembles a 4-8 member virtual expert panel matched to the problem domain (root-cause hunter, system architect, boundary-condition examiner, data-consistency auditor, performance sentinel, ops-cost accountant, user-perspective reviewer). Each expert states the question they most want to ask.
3. **W2 Seven-step complete deduction**: locate the gap → trace the mechanism → benefit-cost matrix → ALL candidate fixes A/B/C (offering a single "best" solution is forbidden) → pseudo-solution elimination → converge & decide with boundary notes → one-sentence essence. Conclusion-first openings are forbidden.
4. **W3 Three-dimension plan selection**: candidates are mapped into fixed slots (native built-in optimal / historical reuse optimal / iteration efficiency optimal) and ranked mechanically by real step count — fewest steps wins. Unbuildable slots are filtered out, never zero-scored. Every plan must hard-write its objective failure criterion ("verify") upfront.
5. **W4 Four-force logic check**: analysis → pros-and-cons comparison (doing AND not doing, side by side) → closed loop (goal → execution → monitoring → correction → retrospective) → decision (what is chosen, what is abandoned, stop-loss red lines). Any missing force = rejection and re-routing.
6. **W5 ROI assessment** (mandatory for redesigns/new mechanisms): five benefit factors + a four-question decision tree that rations permanent mechanisms — a one-off problem gets no permanent checkpoint.
7. **W6 Consultation report**: a fixed-format report with diagnosis conclusion, full candidate queue, check blocks, execution plan, residual boundary defects, and stop-loss red lines. Final ruling always stays with the user.

## How to Use

### Basic Usage

```
/expert-clinic My webhook handler randomly drops events under load. Three fixes attempted, none worked. Diagnose only.
```

### Advanced Usage

```
/expert-clinic I need to add rate limiting to our public API. Option A: middleware bucket; option B: gateway plugin; option C: per-route decorator. Constraints: no new infra services, must ship this week. I want diagnosis + execution of the selected plan.
```

## Example

**User**: "/expert-clinic Our nightly ETL silently skips failed rows. Retry or fail-fast? Diagnosis only."

**Output** (abridged):

```
[Expert Clinic · Consultation Report] ETL silent-skip
Diagnosis conclusion: The skip path was designed as a soft fallback for transient
errors, but it swallows permanent data errors too — the hole is not "missing retry",
it's the absence of a failure-classification step.
Candidate plans: A. retry-with-backoff (S=4, pseudo-solution — retries permanent errors
forever) | B. fail-fast (S=3) | C. classify-then-route: transient→retry, permanent→dead-letter
(S=5) ← selected
Four-force check: [full block with evidence]
ROI assessment: failure frequency=every run · loss=high (silent data loss) ·
redesign cost=2 files · verdict: fix now
Boundary defects: dead-letter replay remains manual (documented, accepted)
Final ruling: left to the user
```

**Inspired by:** [xu-jin-cs/dsh-skills](https://github.com/xu-jin-cs/dsh-skills) — mechanical gates that make LLM agents keep their promises.

## Tips

- State "diagnosis only" vs "diagnosis + execution" upfront — the workflow behaves differently at W5/W6.
- The more concrete the symptoms and evidence in W0, the sharper the deduction; vague input gets clarifying questions, not guesses.
- Don't skip the ROI gate for mechanism changes — that's exactly the case it exists for.

## Common Use Cases

- Root-causing flaky tests / intermittent production bugs
- Choosing between competing implementation routes for the same feature
- Pre-mortem review of a refactor or a new permanent mechanism ("is this gate worth its cost?")
- Reviewing an AI-generated plan for one-sided reasoning before executing it
