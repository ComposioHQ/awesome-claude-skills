---
name: systematic-debugging
description: "Debug by scientific method instead of guesswork: reproduce deterministically, write three hypotheses before pursuing any, isolate by binary search over code, commits, or input, fix the root cause rather than the crash site, and land a regression test. Use on any bug, error, crash, stack trace, failing or flaky test, regression, or a fix that did not hold."
---

# Systematic Debugging

Most debugging time is lost to guessing: change something, re-run, hope. This skill replaces that
with Zeller's scientific method. You form a theory that explains the bug, then test it.

The chain is DEFECT (in the code) to INFECTION (in the state) to FAILURE (the symptom you saw).
The line in the stack trace is the FAILURE. The bug is upstream of it. Everything below follows
from that one fact.

## When to Use This Skill

- A test, build, or request fails and you do not yet know why
- A stack trace points at a line that looks innocent
- Something works locally and fails in CI, or works for one input and not another
- A bug is intermittent and "sometimes fails" is the best reproduction you have
- You have already tried two or three fixes and it is still broken
- A bug you fixed last month came back

## What This Skill Does

1. **Forces reproduction first.** No edits until the failure is deterministic, or targeted logging is in place to catch the next occurrence.
2. **Forces three hypotheses.** Writing three before pursuing any is the anchoring-bias mitigation. Most wasted debugging is one wrong hypothesis pursued too long.
3. **Isolates in O(log n).** Binary search over the call chain, over commits with `git bisect`, or over the failing input, instead of reading everything.
4. **Separates root cause from crash site.** A null check at the crash site is a symptom fix and the skill names it as one.
5. **Requires a regression test** that fails before the fix and passes after, so the bug cannot silently return.
6. **Sets escalation thresholds** so you abandon a dead hypothesis on a clock instead of on a feeling.

## How to Use

### Basic Usage

```
There is a bug: <paste the full error and stack trace>. Debug it systematically.
```

### Advanced Usage

```
The auth test passes locally and fails in CI. Reproduce it first, bisect between the last green
commit and HEAD, and do not propose a fix until you can state the violated invariant in one sentence.
```

## The Method

<skill id="debug">

<purpose>
Debugging is forming and testing a THEORY that explains the bug.
Not random changes. Not guessing. Scientific method applied to code.
DEFECT (in code) → INFECTION (in state) → FAILURE (visible symptom).
The failure you see is NOT where the bug is. Binary search upstream.
Systematic methodology beats ad-hoc guessing. The process is the multiplier.
</purpose>

<prerequisite>Run `agentdb recall` with the exact error text, subsystem/library, failing
test, and known files/symbols. Recall again when the hypothesis changes or a new failure
appears; that is a new retrieval question. Reference on demand:
reference/debug-research.md.</prerequisite>

<steps>
1. **REPRODUCE**: get specific before touching code.
   - Document: exact input, expected output, actual output (full stack trace), environment, frequency.
   - "Sometimes fails" is not a reproduction. Get deterministic.
   - (gate: can reproduce consistently, OR have added targeted logging to wait for next occurrence)

2. **HYPOTHESIZE**: list 3 causes before pursuing any.
   - Read ALL error output first (anchoring bias mitigation).
   - Write each hypothesis to AgentDB. Prevents circular re-investigation.
   - (gate: 3 candidate hypotheses written; none pursued yet)

3. **ISOLATE**: binary search, O(log n) not O(n).
   - **Code**: call chain A→B→C→D→E fails → check midpoint C → recurse into failing half.
   - **Time**: `git bisect` between known-good and known-bad commit. ~10 tests for 1000 commits.
   - **Input**: large failing input → split in half → recurse to minimal reproduction case.
   - Instrument at boundaries: log inputs/outputs at each layer boundary.
   - Mock external dependencies to isolate which one causes failure.
   - (gate: failure localized to a specific function/commit/input subset)

4. **ROOT CAUSE**: the error line is the FAILURE. The DEFECT is upstream.
   - Ask: what assumption was violated? What invariant broke?
   - If you can't explain WHY it broke, you haven't found root cause.
   - Top causes by frequency: wrong input shape/type · off-by-one · missing null check · race condition · shared-state mutation · wrong comparison operator · variable scope · swallowed error · API contract mismatch · environment difference.
   - (gate: can state root cause in one sentence explaining the violated invariant)

5. **FIX**: root cause, not symptom.
   - Fix the DEFECT, not the FAILURE site. (Null check at crash site = symptom fix.)
   - Write regression test that fails before fix, passes after.
   - Run: original failing case + edge cases + full regression suite.
   - Commit fix + test together.
   - (gate: regression test green; original failing case passes)
</steps>

<anti_patterns>
Shotgun (random changes until it works) · fix-and-pray (never re-run the original case) ·
symptom fixing (null check at the crash site) · printf flooding (binary search first, then
targeted logging) · blame-the-framework (it's almost never the library) · unscoped
"investigate" (scope narrowly or use a subagent so the file reads don't fill context).
</anti_patterns>

<when_stuck>
Explain the problem in writing · re-read the error message (the answer is there most of
the time) · reduce to a minimal reproduction · ask "what changed?" (git log/diff, deps,
env) · search the exact error message in quotes · step away, bias accumulates. Re-run the
EXACT original failing case before declaring victory; "seems to work" is not evidence.
</when_stuck>

<escalation>
30+ min on one hypothesis with no evidence → abandon it. 3+ hypotheses rejected → step
back, re-examine assumptions. 2 failed fix attempts → invoke tearitapart; it may be a
design problem. Repeated failed corrections in one session → /clear with a minimal
reproduction. Bug only in production → add targeted monitoring, document, move on.
For 3+ plausible causes, spawn one fresh-context agent per hypothesis (evidence_for /
evidence_against / confidence); fresh context catches what a long session anchors past.
</escalation>

<on_complete>
agentdb write-end '{"skill":"debug","bug":"<description>","root_cause":"<what_broke>","fix":"<what_fixed>","test":"<regression_test_name>","learned":"<pattern_for_future>"}'
</on_complete>

</skill>

## Example

**User**: "TypeError: cannot read property 'id' of undefined at handlers/order.js:340. Fix it."

**Output**:

```
REPRODUCE
  POST /orders with {items: [], customer: null} - fails every time. Deterministic.

HYPOTHESES (3 before pursuing any)
  1. customer is null because the session middleware short-circuits on an expired token
  2. the order mapper drops customer when items is empty
  3. the client genuinely omits customer on guest checkout

ISOLATE
  Logged at each layer boundary. customer is present entering the mapper and absent leaving it.
  H1 and H3 rejected. H2 localized to mapOrder().

ROOT CAUSE
  mapOrder() builds its output by reducing over items. With an empty items array the reduce
  returns the seed, which never carried customer. Violated invariant: mapOrder is supposed to be
  total over its input, and it is only defined for non-empty items.

FIX
  Seed the reduce with the customer fields rather than reattaching them per item.
  NOT a null check at order.js:340 - that is the FAILURE site, not the DEFECT.

REGRESSION TEST
  maps a guest order with zero items - failed before the fix, passes after.
```

## Tips

- Read the entire error output before forming any hypothesis. The answer is in it more often than not.
- If you cannot explain WHY it broke, you have not found the root cause yet. You found a change that made the symptom go away.
- "What changed?" is the highest-yield question in debugging. `git log`, dependency updates, environment.
- Thirty minutes on one hypothesis with no supporting evidence means abandon it, not push harder.
- Re-run the exact original failing case before declaring victory. "Seems to work" is not evidence.
- For three or more plausible causes, run one fresh-context investigation per hypothesis. A long session anchors; a fresh one does not.

## Common Use Cases

- Triaging a production stack trace with no local reproduction
- Finding which of 400 commits broke a test, with `git bisect`
- Reducing a 10MB failing input to the minimal case that still fails
- Breaking out of a fix-and-pray loop after several failed attempts
- Root-causing a flaky test instead of retrying it in CI

## Attribution and License

Extracted from the `debug` skill in [KERNEL](https://github.com/ariaxhan/kernel-claude), a plugin
for Claude Code and Codex by Aria Han. MIT licensed; see `LICENSE.txt`.

The methodology follows Andreas Zeller, *Why Programs Fail: A Guide to Systematic Debugging*.

This skill is standalone and needs no part of KERNEL to run. The two `agentdb` lines in the method
above are optional persistence from that plugin: with it installed they recall prior failures and
record this one; without it, keep the hypothesis list in your working notes and the method is
unchanged.
