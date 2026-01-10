---
name: sparc-methodology
description: Systematic software development through Specification-Pseudocode-Architecture-Refinement-Completion phases
---

# SPARC Methodology

A structured approach to software development that ensures every feature moves through five deliberate phases: Specification, Pseudocode, Architecture, Refinement, and Completion.

## Philosophical Foundation

SPARC is more than a methodology—it is a **passage from darkness to light**.

### The Heideggerian Connection

Martin Heidegger distinguished between two modes of engagement with tools:

| Term | German | Meaning |
|------|--------|---------|
| **Ready-to-hand** | *Zuhandenheit* | Tools used transparently, flowing in action |
| **Present-at-hand** | *Vorhandenheit* | Tools examined consciously, made visible |
| **Thrownness** | *Geworfenheit* | We are "thrown" into projects with pre-existing constraints and contexts |
| **Understanding** | *Verstehen* | Comprehension that grows through engagement with the work |
| **Care** | *Sorge* | The fundamental concern for quality and outcomes that drives craftsmanship |
| **Dwelling** | *Wohnen* | To reside thoughtfully in what we build |
| **Clearing** | *Lichtung* | The open space where truth can appear |
| **Unconcealment** | *Aletheia* | Truth as active revelation from hiddenness |

### Why This Matters

Every project begins in *Geworfenheit*—we are "thrown" into existing codebases, constraints, and contexts we didn't choose. Most development operates in pure *Zuhandenheit*—we code without seeing what we're building. Requirements remain hidden. Architecture stays implicit. We dwell in darkness.

SPARC transforms this through *Verstehen* (understanding) that deepens at each phase, driven by *Sorge* (care) for craftsmanship and quality.

**SPARC creates a structured passage through the Lichtung**:

```
DARKNESS (undefined)          LIGHT (delivered)
      │                             │
      │  S ─────────────────────▶  │
      │    Problem visible         │
      │                            │
      │  P ─────────────────────▶  │
      │    Logic visible           │
      │                            │
      │  A ─────────────────────▶  │
      │    Structure visible       │
      │                            │
      │  R ─────────────────────▶  │
      │    Quality visible         │
      │                            │
      │  C ─────────────────────▶  │
      │    Value delivered         │
      └────────────────────────────┘
```

Each phase is a *Lichtung*—a clearing where what was hidden becomes unconcealed. Specification reveals the true problem. Pseudocode reveals the logic. Architecture reveals the structure. Refinement reveals the quality. Completion reveals the value.

> *"We attain to dwelling, so it seems, only by means of building."*
> — Martin Heidegger, *Building Dwelling Thinking*

SPARC is how we **build thoughtfully** so we may **dwell confidently** in what we create.

---

## Why SPARC?

Most development fails not from lack of skill but from lack of structure:
- Features start coding before requirements are clear
- Architecture emerges accidentally rather than deliberately
- Testing is an afterthought rather than a driver
- Integration surprises appear at the worst time

SPARC prevents these failures by making each phase explicit and sequential.

## The Five Phases

### S - Specification
**Goal**: Know exactly what to build before building anything.

**Outputs**:
- Clear problem statement
- Acceptance criteria (testable conditions for "done")
- Constraints (performance, security, compatibility)
- Non-goals (explicitly what we're NOT building)
- Edge cases identified

**Template**:
```markdown
## Specification: [Feature Name]

### Problem Statement
[What problem does this solve? For whom?]

### Acceptance Criteria
- [ ] [Criterion 1 - testable]
- [ ] [Criterion 2 - testable]
- [ ] [Criterion 3 - testable]

### Constraints
- Performance: [requirements]
- Security: [requirements]
- Compatibility: [requirements]

### Non-Goals
- [What we explicitly won't do]
- [What's out of scope]

### Edge Cases
1. [Edge case 1]: Expected behavior
2. [Edge case 2]: Expected behavior
```

**Exit Criteria**: All acceptance criteria are testable. A stranger could verify if the feature is "done."

---

### P - Pseudocode
**Goal**: Design the algorithm before implementing it.

**Outputs**:
- High-level logic flow
- Data structures needed
- Key algorithms identified
- Complexity analysis (if relevant)

**Template**:
```markdown
## Pseudocode: [Feature Name]

### Main Flow
```
FUNCTION main_feature(input):
    validated = validate(input)
    IF not validated:
        RETURN error

    processed = process(validated)
    result = transform(processed)

    RETURN result
```

### Key Algorithms
```
FUNCTION process(data):
    # Step 1: [description]
    # Step 2: [description]
    # Step 3: [description]
```

### Data Structures
- [Structure 1]: [purpose]
- [Structure 2]: [purpose]

### Complexity
- Time: O(?)
- Space: O(?)
```

**Exit Criteria**: Logic is clear enough that implementation is "just" translation to code.

---

### A - Architecture
**Goal**: Design how components interact before coding them.

**Outputs**:
- Component diagram
- Interface definitions
- Data flow
- Integration points
- Error handling strategy

**Template**:
```markdown
## Architecture: [Feature Name]

### Component Diagram
```
┌─────────────┐     ┌─────────────┐
│  Component A │────▶│ Component B │
└─────────────┘     └─────────────┘
       │                   │
       ▼                   ▼
┌─────────────┐     ┌─────────────┐
│  Component C │◀────│ Component D │
└─────────────┘     └─────────────┘
```

### Interfaces
```typescript
interface ComponentA {
  method1(input: Type): ReturnType
  method2(input: Type): ReturnType
}
```

### Data Flow
1. User action triggers [X]
2. [X] calls [Y] with [data]
3. [Y] returns [result]
4. [result] updates [state]

### Integration Points
- External API: [description]
- Database: [description]
- Cache: [description]

### Error Handling
- [Error type 1]: [strategy]
- [Error type 2]: [strategy]
```

**Exit Criteria**: A new team member could implement this without architectural questions.

---

### R - Refinement
**Goal**: Build through iterative test-driven development.

**Process**:
1. Write failing test for smallest piece
2. Write minimal code to pass
3. Refactor while tests pass
4. Repeat

**Template**:
```markdown
## Refinement: [Feature Name]

### Iteration 1: [Smallest Testable Unit]
- Test: [what we're testing]
- Implementation: [minimal code]
- Refactor: [improvements]

### Iteration 2: [Next Unit]
- Test: [what we're testing]
- Implementation: [minimal code]
- Refactor: [improvements]

### Iteration N: [Final Unit]
- Test: [what we're testing]
- Implementation: [minimal code]
- Refactor: [improvements]

### Test Coverage
- Unit tests: X%
- Integration tests: [list]
- Edge cases covered: [list]
```

**Exit Criteria**: All acceptance criteria have passing tests. Code is clean and refactored.

---

### C - Completion
**Goal**: Integrate, document, and deploy.

**Outputs**:
- Integrated with main codebase
- Documentation updated
- Deployment verified
- Monitoring in place

**Template**:
```markdown
## Completion: [Feature Name]

### Integration
- [ ] PR created and reviewed
- [ ] CI/CD passing
- [ ] Merged to main branch

### Documentation
- [ ] README updated (if needed)
- [ ] API docs updated (if needed)
- [ ] Architecture diagrams updated (if needed)

### Deployment
- [ ] Deployed to staging
- [ ] Staging verification passed
- [ ] Deployed to production
- [ ] Production verification passed

### Monitoring
- [ ] Logs configured
- [ ] Metrics configured
- [ ] Alerts configured (if needed)

### Handoff
- [ ] Team notified
- [ ] Stakeholders updated
- [ ] Feature flag configured (if needed)
```

**Exit Criteria**: Feature is live, monitored, and documented.

---

## Phase Flow

```
┌───────────────┐
│ SPECIFICATION │ ──▶ Clear requirements
└───────┬───────┘
        │
        ▼
┌───────────────┐
│  PSEUDOCODE   │ ──▶ Algorithm designed
└───────┬───────┘
        │
        ▼
┌───────────────┐
│ ARCHITECTURE  │ ──▶ Components defined
└───────┬───────┘
        │
        ▼
┌───────────────┐
│  REFINEMENT   │ ──▶ Code built (TDD)
└───────┬───────┘
        │
        ▼
┌───────────────┐
│  COMPLETION   │ ──▶ Shipped & monitored
└───────────────┘
```

## When to Use Each Phase

| Situation | Start Phase | Skip Phases? |
|-----------|-------------|--------------|
| New feature | Specification | Never skip |
| Bug fix | Refinement | S, P, A often implicit |
| Refactor | Architecture | S implicit, P optional |
| Hotfix | Refinement | All others post-hoc |
| Spike/POC | Pseudocode | A, C deferred |

## Anti-Patterns

### 1. Specification Avoidance
**Symptom**: "Let's just start coding and see where it goes"
**Problem**: Wasted effort on wrong features
**Fix**: Spend 10% of time on specification; save 50% on rework

### 2. Pseudocode Skipping
**Symptom**: "I'll figure out the algorithm while coding"
**Problem**: Spaghetti logic, hard to test
**Fix**: 30 minutes of pseudocode saves hours of debugging

### 3. Architecture Afterthought
**Symptom**: "We'll refactor later"
**Problem**: Technical debt compounds
**Fix**: Architecture phase IS the refactoring, done upfront

### 4. Test-Last Development
**Symptom**: "I'll add tests after it works"
**Problem**: Tests never get written; bugs ship
**Fix**: Refinement phase is TDD by definition

### 5. Completion Shortcuts
**Symptom**: "It works on my machine, ship it"
**Problem**: Production surprises, missing docs
**Fix**: Completion checklist is non-negotiable

## Integration with Other Skills

- **Before SPARC**: Use `socratic-questioning` to validate the problem is worth solving
- **During Specification**: Use `dialectic-reasoning` for tradeoff decisions
- **Across Sessions**: Use `session-memory` to track SPARC progress
- **For Teams**: Use `multi-agent-patterns` to parallelize phases

## Example: Complete SPARC Walkthrough

### Feature: User Authentication Rate Limiting

**SPECIFICATION**:
```markdown
Problem: Prevent brute-force attacks on login endpoint

Acceptance Criteria:
- [ ] Max 5 attempts per IP per 15 minutes
- [ ] Clear error message on rate limit hit
- [ ] Legitimate users unaffected
- [ ] Admin can see rate limit metrics

Constraints:
- Performance: < 5ms added latency
- Security: No information leakage about valid accounts

Non-Goals:
- CAPTCHA (separate feature)
- Account lockout (separate feature)
```

**PSEUDOCODE**:
```
FUNCTION check_rate_limit(ip_address):
    key = "ratelimit:" + ip_address
    count = cache.get(key) or 0

    IF count >= MAX_ATTEMPTS:
        RETURN RateLimitExceeded

    cache.increment(key)
    cache.expire(key, WINDOW_SECONDS)

    RETURN Allowed
```

**ARCHITECTURE**:
```
┌──────────┐     ┌─────────────┐     ┌───────┐
│  Client  │────▶│ Rate Limiter│────▶│ Auth  │
└──────────┘     └─────────────┘     └───────┘
                        │
                        ▼
                 ┌─────────────┐
                 │    Redis    │
                 └─────────────┘
```

**REFINEMENT**:
```python
# Test 1: Under limit passes
def test_under_limit_passes():
    limiter = RateLimiter(max=5, window=900)
    for i in range(5):
        assert limiter.check("1.2.3.4") == Allowed

# Test 2: Over limit blocks
def test_over_limit_blocks():
    limiter = RateLimiter(max=5, window=900)
    for i in range(5):
        limiter.check("1.2.3.4")
    assert limiter.check("1.2.3.4") == RateLimitExceeded
```

**COMPLETION**:
- ✅ PR #1234 merged
- ✅ Docs updated: security/rate-limiting.md
- ✅ Deployed to production
- ✅ Grafana dashboard configured

---

*"For every complex problem there is an answer that is clear, simple, and wrong."*
— H.L. Mencken

SPARC ensures we find the answer that is clear, simple, and **right**.
