# Reference: Manus Context Engineering Principles

This skill is based on context engineering principles from Manus, the AI agent company acquired by Meta for $2 billion in December 2025.

## The 6 Manus Principles

### Principle 1: Design Around KV-Cache

> "KV-cache hit rate is THE single most important metric for production AI agents."

**Statistics:**
- ~100:1 input-to-output token ratio
- Cached tokens: $0.30/MTok vs Uncached: $3/MTok
- 10x cost difference!

**Implementation:**
- Keep prompt prefixes STABLE (single-token change invalidates cache)
- NO timestamps in system prompts
- Make context APPEND-ONLY with deterministic serialization

### Principle 2: Mask, Don't Remove

Don't dynamically remove tools (breaks KV-cache). Use logit masking instead.

**Best Practice:** Use consistent action prefixes (e.g., `browser_`, `shell_`, `file_`) for easier masking.

### Principle 3: Filesystem as External Memory

> "Markdown is my 'working memory' on disk."

**The Formula:**
```
Context Window = RAM (volatile, limited)
Filesystem = Disk (persistent, unlimited)
```

**Compression Must Be Restorable:**
- Keep URLs even if web content is dropped
- Keep file paths when dropping document contents
- Never lose the pointer to full data

### Principle 4: Manipulate Attention Through Recitation

> "Creates and updates todo.md throughout tasks to push global plan into model's recent attention span."

**Problem:** After ~50 tool calls, models forget original goals ("lost in the middle" effect).

**Solution:** Re-read `task_plan.md` before each decision. Goals appear in the attention window.

```
Start of context: [Original goal - far away, forgotten]
...many tool calls...
End of context: [Recently read task_plan.md - gets ATTENTION!]
```

### Principle 5: Keep the Wrong Stuff In

> "Leave the wrong turns in the context."

**Why:**
- Failed actions with stack traces let model implicitly update beliefs
- Reduces mistake repetition
- Error recovery is "one of the clearest signals of TRUE agentic behavior"

### Principle 6: Don't Get Few-Shotted

> "Uniformity breeds fragility."

**Problem:** Repetitive action-observation pairs cause drift and hallucination.

**Solution:** Introduce controlled variation:
- Vary phrasings slightly
- Don't copy-paste patterns blindly
- Recalibrate on repetitive tasks

---

## The 3 Context Engineering Strategies

Based on Lance Martin's analysis of Manus architecture.

### Strategy 1: Context Reduction

**Compaction:**
```
Tool calls have TWO representations:
├── FULL: Raw tool content (stored in filesystem)
└── COMPACT: Reference/file path only

RULES:
- Apply compaction to STALE (older) tool results
- Keep RECENT results FULL (to guide next decision)
```

**Summarization:**
- Applied when compaction reaches diminishing returns
- Generated using full tool results
- Creates standardized summary objects

### Strategy 2: Context Isolation (Multi-Agent)

**Architecture:**
```
┌─────────────────────────────────┐
│         PLANNER AGENT           │
│  └─ Assigns tasks to sub-agents │
├─────────────────────────────────┤
│       KNOWLEDGE MANAGER         │
│  └─ Reviews conversations       │
│  └─ Determines filesystem store │
├─────────────────────────────────┤
│      EXECUTOR SUB-AGENTS        │
│  └─ Perform assigned tasks      │
│  └─ Have own context windows    │
└─────────────────────────────────┘
```

**Key Insight:** Manus originally used `todo.md` for task planning but found ~33% of actions were spent updating it. Shifted to dedicated planner agent calling executor sub-agents.

### Strategy 3: Context Offloading

**Tool Design:**
- Use <20 atomic functions total
- Store full results in filesystem, not context
- Use `glob` and `grep` for searching
- Progressive disclosure: load information only as needed

---

## The Agent Loop

Manus operates in a continuous 7-step loop:

```
┌─────────────────────────────────────────┐
│  1. ANALYZE CONTEXT                      │
│     - Understand user intent             │
│     - Assess current state               │
│     - Review recent observations         │
├─────────────────────────────────────────┤
│  2. THINK                                │
│     - Should I update the plan?          │
│     - What's the next logical action?    │
│     - Are there blockers?                │
├─────────────────────────────────────────┤
│  3. SELECT TOOL                          │
│     - Choose ONE tool                    │
│     - Ensure parameters available        │
├─────────────────────────────────────────┤
│  4. EXECUTE ACTION                       │
│     - Tool runs in sandbox               │
├─────────────────────────────────────────┤
│  5. RECEIVE OBSERVATION                  │
│     - Result appended to context         │
├─────────────────────────────────────────┤
│  6. ITERATE                              │
│     - Return to step 1                   │
│     - Continue until complete            │
├─────────────────────────────────────────┤
│  7. DELIVER OUTCOME                      │
│     - Send results to user               │
│     - Attach all relevant files          │
└─────────────────────────────────────────┘
```

---

## File Types Manus Creates

| File | Purpose | When Created | When Updated |
|------|---------|--------------|--------------|
| `task_plan.md` | Phase tracking, progress | Task start | After completing phases |
| `findings.md` | Discoveries, decisions | After ANY discovery | After viewing images/PDFs |
| `progress.md` | Session log, what's done | At breakpoints | Throughout session |
| Code files | Implementation | Before execution | After errors |

---

## Critical Constraints

- **Single-Action Execution:** ONE tool call per turn. No parallel execution.
- **Plan is Required:** Agent must ALWAYS know: goal, current phase, remaining phases
- **Files are Memory:** Context = volatile. Filesystem = persistent.
- **Never Repeat Failures:** If action failed, next action MUST be different
- **Communication is a Tool:** Message types: `info` (progress), `ask` (blocking), `result` (terminal)

---

## Manus Statistics

| Metric | Value |
|--------|-------|
| Average tool calls per task | ~50 |
| Input-to-output token ratio | 100:1 |
| Acquisition price | $2 billion |
| Time to $100M revenue | 8 months |
| Framework refactors since launch | 5 times |

---

## Key Quotes

> "Context window = RAM (volatile, limited). Filesystem = Disk (persistent, unlimited). Anything important gets written to disk."

> "if action_failed: next_action != same_action. Track what you tried. Mutate the approach."

> "Error recovery is one of the clearest signals of TRUE agentic behavior."

> "KV-cache hit rate is the single most important metric for a production-stage AI agent."

> "Leave the wrong turns in the context."

---

## Source

Based on Manus's official context engineering documentation:
https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus
