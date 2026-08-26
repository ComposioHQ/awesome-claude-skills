# Debug Skill Reference: Research & Best Practices

Reference document for the debug skill. Read when deeper context is needed.
Not auto-loaded; read on demand via progressive disclosure.

## Sources

Andreas Zeller "Why Programs Fail" (ACM, Jolt Award), Eisenstadt debugging studies,
UkrPROG 2025 taxonomy, Atlassian cognitive bias research, ICSE 2026 Cognitive Biases
in LLM-Assisted Development (arXiv 2601.08045), Microsoft debug-gym (arXiv 2503.21557),
BugLens v2 (Jan 2026), DDMIN-LOC (Jan 2026), Visual Studio 2026 Debugger Agent,
ChatDBG (ACM FSE 2025).

---

## The Scientific Method of Debugging (Zeller)

Andreas Zeller, ACM Fellow, established the definitive framework. His process
maps directly to the scientific method:

1. OBSERVE the failure (what happened?)
2. HYPOTHESIZE a cause (why might this happen?)
3. PREDICT consequences of the hypothesis (if this is the cause, then...)
4. TEST the prediction (does the prediction hold?)
5. REFINE or REJECT the hypothesis based on results
6. Repeat until the cause is isolated

Key insight from Zeller: "Debugging then consists of obtaining a theory that
explains the bug." Not random changes. Not guessing. A theory, tested
systematically, like any scientific investigation.

The debugging logbook: Zeller advocates writing down each hypothesis, prediction,
and test result. This prevents circular investigation (re-testing the same thing)
and creates a record for future similar bugs. In our system, AgentDB serves this
function; write learnings after every debug session.

---

## The Defect-Infection-Failure Chain (Zeller)

Bugs propagate through a causal chain:

DEFECT (in code) → INFECTION (in program state) → FAILURE (visible symptom)

Critical insight: the failure you see is NOT where the bug is. It's the end of
a chain. The defect that caused it may be far away in both code location and
execution time.

Eisenstadt's research (cited by Zeller) found that HALF of all debugging
difficulties came from just two sources:
1. Large temporal or spatial chasms between root cause and symptom.
2. Bugs that rendered debugging tools inapplicable.

This is why "jumping to the error line" fails. The error line is the FAILURE.
The DEFECT is upstream. Binary search along the cause-effect chain is how you
find it.

---

## Delta Debugging (Zeller)

Formal technique for minimizing failure-inducing input:

Given a failing input and a passing input, systematically reduce the difference
until you find the minimal change that causes failure. This is binary search
applied to input space.

The algorithm (ddmin) works by:
1. Split the difference between passing and failing into halves.
2. Test each half.
3. The half that still fails contains the cause.
4. Recurse until you can't reduce further.

Practical application (without formal tooling):
- If a feature worked yesterday and fails today, git bisect applies delta
  debugging to commit history.
- If a large input causes failure, reduce the input by halves until you find
  the minimal failing case.
- If commenting out code fixes the bug, binary search the commented-out
  section to find the exact culprit.

---

## Binary Search Isolation

The single most effective debugging technique. O(log n) vs O(n) for linear
scanning. Applied to three domains:

Code: if a call chain A → B → C → D → E fails, check C first. Works? Bug
is in D or E. Fails? Bug is in A, B, or C. Recurse.

Time: git bisect automates binary search across commits. Given a known-good
and known-bad commit, it finds the exact commit that introduced the bug in
O(log n) steps. For a 1000-commit range, that's ~10 tests instead of 1000.

Input: given a large failing input, split in half. Which half still triggers
failure? Recurse until you have the minimal failing input.

Research validation: BugLens (2025, arxiv 2506.23281) confirmed bisection as
the primary criterion for deduplicating compiler bugs, saving 27% of human
debugging effort compared to state-of-the-art analysis-based techniques.

---

## Cognitive Biases in Debugging

Research from Atlassian, ACM studies, and cognitive science identifies specific
biases. **NEW ICSE 2026 research** (arXiv 2601.08045) adds LLM-specific findings:
- **48.8% of programmer actions** exhibited bias
- **56.4% bias rate** in LLM-related interactions (higher than non-LLM work)
- 15 new bias categories identified specific to developer-LLM interactions
- 90 total biases catalogued in human-AI programming contexts

### Confirmation Bias (most dangerous)
You suspect module X is the cause. You look for evidence that X is broken.
You find it (because complex code always has something wrong). You "fix" X.
The real bug was in Y.

Mitigation: actively seek DISCONFIRMING evidence. Ask: "What would I expect
to see if my hypothesis were WRONG?" Test that prediction first.

### Anchoring Bias
The first error message you see anchors your investigation. You spend hours
in that area. The actual cause is elsewhere.

Mitigation: before investigating, read ALL error output. List 3 possible
causes before pursuing any single one. The first idea is rarely correct.

### Availability Bias
"Last time this happened, it was a database connection issue." You jump to
the database. But this time it's a completely different cause with a similar
symptom.

Mitigation: check AgentDB for past failure patterns, but treat them as
hypotheses to test, not conclusions to assume.

### Sunk Cost Fallacy
You've spent 2 hours investigating hypothesis A. Surely you're close. You
keep digging. But the evidence doesn't support A.

Mitigation: set time-boxes. If a hypothesis yields no supporting evidence
in 15 minutes of focused investigation, abandon it and try the next.
Write down what you tested so you don't return to it.

### Optimism Bias
"It probably works now." You make a change, it seems to work, you ship it.
You didn't actually test the original failing case, or you tested only the
happy path.

Mitigation: ALWAYS re-run the exact original failing case. Then test edge
cases. Then run regression suite. "It seems to work" is not evidence.

---

## The Taxonomy of Debugging (UkrPROG 2025)

The 2025 UkrPROG conference published a formal taxonomy categorizing debugging
across six dimensions:

WHAT: the objects of debugging (code, data, config, environment, state)
WHICH: tools employed (debuggers, loggers, profilers, tracers, analyzers)
HOW: methods applied (systematic, heuristic, tool-assisted, automated)
WHO: human factors (experience, bias, fatigue, domain knowledge)
WHEN: temporal aspects (during development, in production, post-mortem)
WHERE: environment (local, CI, staging, production, distributed)

Key finding: debugging is not a single activity. It's a complex process
influenced by all six dimensions simultaneously. Focusing only on HOW
(technique) while ignoring WHO (human factors) or WHERE (environment)
leads to incomplete debugging strategies.

---

## Common Root Causes (Ranked by Frequency)

From aggregated research and industry data:

1. Wrong assumption about input shape or type (most common)
2. Off-by-one errors (loop bounds, array indices, string slicing)
3. Missing null/undefined/None check
4. Race condition or async timing issue
5. Mutating shared state (aliasing bugs)
6. Wrong comparison operator (=, ==, ===, >, >=)
7. Variable scope issue (closure captures, shadowing)
8. Swallowed error (catch block that does nothing)
9. API contract mismatch (expected response vs actual)
10. Environment difference (works on my machine)
11. Timezone, locale, or character encoding issue
12. Stale cache or memoized value
13. Dependency version mismatch
14. Config value wrong or missing (env var, feature flag)
15. Integer overflow or floating point precision

---

## Debugging Heuristics That Work

### Read the Error Message (Seriously)
Research and practitioner surveys consistently find that the error message
contains the answer approximately 80% of the time. Developers skip over
them because of anchoring bias (they already have a hypothesis) or because
the message seems generic. Read the ENTIRE message. Read the stack trace
from bottom to top (call origin) AND top to bottom (failure point).

### Minimal Reproduction Case
Reduce the failing scenario to the absolute minimum code that triggers
the bug. This is delta debugging applied informally. If you can reproduce
the bug in 10 lines, you've already identified 90% of what's irrelevant.

### "What Changed?" Method
If it worked before, something changed. Check:
- git log: recent commits
- git diff: uncommitted changes
- Dependency updates (lock file diff)
- Environment changes (node version, env vars, config)
- Data changes (database state, API responses)

### Rubber Duck Debugging
Explaining the problem forces you to articulate your assumptions. The act
of explaining often reveals the false assumption. This works because it
engages slow cognition (Kahneman's System 2) instead of fast cognition
(System 1), which is more susceptible to bias.

### The "Sleep On It" Method
Atlassian's research: "After a night's rest or a spell away from the
keyboard, I return to my desk and immediately arrive at the answer."
This isn't mysticism. Disengaging from the problem allows your brain to
process it without the anchoring and confirmation biases that accumulate
during sustained focus.

---

## Anti-Patterns in Debugging

### Shotgun Debugging
Making random changes and seeing if the bug disappears. Even if it works,
you don't understand WHY, which means the fix is fragile and might mask
a deeper issue.

### Fix and Pray
Making a change that seems related, not testing the original failing case,
and declaring victory. The bug reappears days later.

### Symptom Fixing
Adding a null check where the crash happens instead of asking why the value
is null in the first place. The defect-infection-failure chain means the
real problem is upstream.

### Printf Flooding
Adding logging everywhere instead of using binary search to narrow the
location first. You drown in output and can't find the signal.

### "Works On My Machine"
Dismissing a bug because you can't reproduce it locally. The bug is real;
your environment is different. Investigate the difference.

### Debugging by Diffing
Copying a working version of the code and diffing without understanding
the functional difference. You might find what changed, but you won't
understand why the change causes failure.

### Blaming the Framework
Assuming the bug is in the library, not your code. Statistically, the bug
is almost always in your code. Check your usage first. Check the library's
issue tracker only after you've confirmed correct usage.

---

## When to Stop Debugging and Escalate

- 30+ minutes on a single hypothesis with no supporting evidence: abandon it.
- 3+ hypotheses tested and rejected: step back, re-examine assumptions.
- Bug only reproduces in production with no local reproduction: add targeted
  logging/monitoring and wait for next occurrence.
- Bug is in third-party code you can't modify: document workaround, file issue,
  move on.
- Bug is a known platform limitation: document, work around, move on.

In KERNEL terms: if the surgeon agent's debug cycles exceed 2 fix attempts on
the same bug, the orchestrator should re-evaluate. The bug may indicate a
design problem (invoke tearitapart) rather than an implementation problem.

---

## LLM-Induced Biases (ICSE 2026)

Over-acceptance: Accepting AI suggestions without verification because "it looks right."
Mitigation: Treat every AI suggestion as a hypothesis requiring evidence.

Explanation Anchoring: Trusting AI-generated explanations over independent analysis.
Mitigation: Form your own hypothesis BEFORE asking the AI. Compare.

Evaluation Fatigue: Reduced scrutiny of later AI suggestions after accepting earlier ones.
Mitigation: Fresh review for each suggestion. No cumulative trust.

Suggester Preference: Adopting LLM suggestions without questioning, especially for
complex tasks. Mitigation: Always verify with evidence.

---

## AI-Assisted Debugging Tools (2026)

### ChatDBG (ACM FSE 2025)
AI-powered debugging assistant integrating LLMs with pdb, lldb, gdb.
Allows open-ended questions ("why is x null?") with autonomous investigation.
Achieves **67-85% root cause accuracy**. Download: github.com/plasma-umass/ChatDBG

### debug-gym (Microsoft Research, arXiv 2503.21557)
LLMs with interactive debugging tools (breakpoints, variable inspection)
outperform static error-message approaches.
- Claude 3.7 improved from 37.2% to **48.4%** with tool access.
- OpenAI o1-preview jumped from 10.7% to **30.2%** (182% improvement).

### VS 2026 Debugger Agent
IDE-integrated agent automating unit test fixes: hypothesizes causes, edits code,
reruns until success. Analyzes exceptions across entire repository including
historical bugs. "Debug with Copilot" on right-click.

### When to Use AI Tools
- Use for initial hypothesis generation (AI is fast at pattern matching).
- Always verify AI root cause claims with evidence (reproduce, observe).
- AI excels at "where to look" but not always "what it means."
- Complex bugs with large temporal chasms still require human binary search.

---

## 2026 Benchmark Reality Check

SWE-bench Verified: ~80% (Claude Opus 4.6, GPT-5).
SWE-bench Pro (realistic bugs): Only **23%** for best models.
Gap indicates current benchmarks overstate real-world debugging capability.

---

## Integration with KERNEL System

The debug skill enhances the surgeon agent during bug work. Key integration
points:

- AgentDB as debugging logbook: write hypotheses, test results, and learnings
  after every debug session. This prevents circular investigation across sessions.
- git bisect for temporal isolation: surgeon should use bisect when the bug is
  a regression (worked before, fails now).
- Regression test requirement: every bug fix MUST include a test that reproduces
  the original bug. This is non-negotiable. The test is evidence that the fix
  addresses the actual cause, not a symptom.
- Error recovery circuit breaker: 2 failed fix attempts on the same bug triggers
  orchestrator escalation. The surgeon should not spiral.
- **2026**: Consider ChatDBG or debug-gym methodology for initial hypothesis
  generation, but verify all AI-suggested root causes with evidence.

---

## Parallel Debug Strategy (Competing Hypothesis Agents)

For bugs with multiple plausible causes, spawn separate agents per hypothesis.
Each investigates independently with a fresh, unpolluted context window.
Agents with fresh context catch what a single long session anchors past.

```
Agent A: Hypothesis — race condition in cache layer
Agent B: Hypothesis — API contract mismatch on response shape
Agent C: Hypothesis — off-by-one in pagination cursor

Each reports: evidence_for | evidence_against | confidence (0-1)
Coroner agent synthesizes findings.
```

**Fresh context advantage**: Long debugging sessions accumulate cognitive anchoring.
A fresh agent given only the minimal reproduction case (not 200 lines of chat history)
reasons more clearly. When stuck >30 min, spawn a fresh agent with only:
- The exact input that triggers the bug
- The expected vs actual output
- The relevant code section (not the whole file)

**AgentDB as debug log**: Write each hypothesis and its test result to AgentDB before
abandoning it. Prevents the same hypothesis being re-investigated in the next session.

<!-- Source: parallel_debug_strategy section, 2026-05-28 -->

---

## Persistent Investigation File Template

Create `_meta/context/DEBUG.md` at session start. Update throughout.
Achieves ~95% first-time fix rate vs ~40% for ad-hoc debugging (structured persistent
investigation prevents circular re-investigation across context compression boundaries).
<!-- Evidence: https://allierays.com/posts/5-techniques-to-debug-claude-code/ -->

Instruct Claude: "Read _meta/context/DEBUG.md before each attempt. Update it after each attempt."

```markdown
# Debugging Session: [Issue Title]

## Problem Statement
[Concise problem + exact error message]

## What We Know
- [confirmed fact 1]
- [confirmed fact 2]

## Approaches Tried
- [ ] Approach A: [description] → Failed because [reason]
- [ ] Approach B: [description] → Failed because [reason]
- [x] Approach C: [description] → Partially works, need to [next step]

## Current Hypothesis
[Best current theory of root cause]

## Next Steps
1. [specific action]
```

<!-- Source: persistent_truth_file section, 2026-05-28 -->

---

## 2026 Tooling Landscape

### Plan Mode
Use for complex or multi-file bugs before touching code.
Paste stack traces and error messages. Scope exploration, form hypotheses, get
approval — then switch to Act mode for fixes.

### Auto-Compaction
Auto-manages context window limits in 2026. No longer need to manually `/compact`
during debug sessions. But instruct compaction to preserve `_meta/context/DEBUG.md`
so investigation state survives.

### Agent Tool for Parallel Exploration
Spawn competing-hypothesis agents without polluting the main context.
Each agent gets only the minimal reproduction, not 200 lines of chat history.

**Root cause over fast fix**: Claude solves the immediate problem by finding the fastest
path to making the error go away. The fastest fix is frequently wrong — it patches the
symptom and breaks something downstream. When a fix "works" but you can't explain
*why the bug occurred*, you haven't fixed it.

<!-- Source: tooling_2026 section, Updated 2026-05-14 — https://gitnation.com/contents/advanced-claude-code-techniques-for-2026 -->

---

## MCP Debugger Integration

MCP debugger tools let Claude Code set breakpoints, step through code, and evaluate
expressions at runtime — rather than relying solely on print-based logging.

**When to use**: binary search isolation isn't sufficient, or the bug only manifests
under specific runtime state that's hard to reproduce via logging alone.

Reference implementation: github.com/AlmogBaku/debug-skill

**Advantage over logging**: Claude sees exact variable state at each execution step.
Faster convergence on root cause for state-mutation bugs, closure bugs, and async
timing issues where print-based debugging distorts timing.

<!-- Source: debugger_mcp_integration section, Updated 2026-05-17 -->

---

## --verbose Flag

Use `--verbose` when running Claude Code during active debugging sessions to see tool
calls, file reads, and intermediate reasoning in real time. Turn it off in production
or CI runs — the overhead is significant and the output is for human diagnosis only.

When a debugging session produces an unexpected fix or Claude explains reasoning you
can't follow, `--verbose` output is the receipt. Read it before accepting the fix.

<!-- Source: verbose_flag section, Updated 2026-05-17 -->
