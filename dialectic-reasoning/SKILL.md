---
name: dialectic-reasoning
description: Structure complex decisions through Hegelian thesis-antithesis-synthesis dialectic
---

# Dialectic Reasoning

Transform complex decisions from single-answer responses into structured deliberation through the Hegelian dialectic method.

## Philosophical Foundation

This skill is grounded in the phenomenology of Martin Heidegger and the dialectics of G.W.F. Hegel.

### Core Concepts

| Term | German | Meaning |
|------|--------|---------|
| **Ready-to-hand** | *Zuhandenheit* | Tools used transparently, without conscious thought—the hammer we wield |
| **Present-at-hand** | *Vorhandenheit* | Tools examined consciously, made visible through questioning |
| **Being-there** | *Dasein* | Existence with awareness—the human condition of caring about meaning |
| **Care** | *Sorge* | The fundamental stance of concern toward outcomes and consequences |
| **Being-with** | *Mitsein* | Co-existence with others; dialectic as dialogue between perspectives |
| **Clearing** | *Lichtung* | The open space where truth can reveal itself—a pause in the dense forest of action |
| **Unveiling** | *Aletheia* | Truth as active revelation, not static correspondence |
| **Breakdown** | *Zusammenbruch* | When tools fail, we finally see them as tools—the moment of insight |
| **Sublation** | *Aufheben* | To cancel, preserve, and elevate simultaneously—the engine of synthesis |

### Why This Matters

Most AI interactions operate in *Zuhandenheit*—transparent tool use. You ask, Claude answers. Efficient, but shallow.

**This skill creates a *Lichtung***—a clearing where opposing ideas can appear, coexist, and illuminate each other before resolution. The dialectic *forces a breakdown* of easy answers, making the problem visible in its full complexity.

When we engage dialectically, we embody *Dasein*—being that cares about its own existence and choices. We exercise *Sorge* (care) toward outcomes that matter. The thesis and antithesis become a *Mitsein*—a being-with opposing perspectives, not against them.

> *"The clearing is never a fixed stage with a permanently raised curtain on which the play of beings unfolds."*
> — Martin Heidegger, *Zur Sache des Denkens*

The thesis and antithesis must both be seen clearly before *Aufheben* (sublation) can occur—canceling what's limited, preserving what's valuable, elevating to higher understanding.

---

## When to Use This Skill

Activate dialectic reasoning when:
- Facing either/or decisions with valid arguments on both sides
- Evaluating architectural choices (monolith vs microservices, SQL vs NoSQL)
- Analyzing strategic options (build vs buy, hire vs outsource)
- Debating design tradeoffs (performance vs readability, flexibility vs simplicity)
- Any situation where "it depends" is the honest answer

## The Dialectic Process

### Phase 1: THESIS
Present the first position as strongly as possible:
- State the position clearly
- List all supporting arguments
- Identify ideal conditions where this position wins
- Acknowledge its strongest advocates
- Steel-man the argument (present it better than its proponents might)

### Phase 2: ANTITHESIS
Present the opposing position with equal rigor:
- State the counter-position clearly
- List all supporting arguments
- Identify conditions where this position wins
- Acknowledge its strongest advocates
- Steel-man this argument too (no straw men)

### Phase 3: SYNTHESIS (Aufheben)
The German "Aufheben" means simultaneously to cancel, preserve, and elevate. The synthesis:
- Identifies the kernel of truth in both positions
- Finds conditions where each applies
- Creates a higher-order solution that transcends the binary
- Preserves what's valuable from both while canceling what's limited
- Elevates the discussion to a new level of understanding

## Output Format

```markdown
## Dialectic Analysis: [Topic]

### THESIS: [Position A]
**Core Claim**: [One sentence]

**Arguments**:
1. [Argument 1]
2. [Argument 2]
3. [Argument 3]

**Ideal Conditions**: [When this position is clearly correct]

**Steel-man**: [The strongest possible version of this argument]

---

### ANTITHESIS: [Position B]
**Core Claim**: [One sentence]

**Arguments**:
1. [Counter-argument 1]
2. [Counter-argument 2]
3. [Counter-argument 3]

**Ideal Conditions**: [When this position is clearly correct]

**Steel-man**: [The strongest possible version of this argument]

---

### SYNTHESIS: [Transcendent Position]
**Resolution**: [How both are partially right]

**The Higher Truth**:
- From Thesis, we preserve: [X]
- From Antithesis, we preserve: [Y]
- The transcendent insight: [Z]

**Practical Guidance**:
- When to lean Thesis: [conditions]
- When to lean Antithesis: [conditions]
- The default recommendation: [synthesis]

**New Questions Raised**: [What this synthesis now asks]
```

## Examples

### Example 1: Technical Architecture

**User**: Should we use microservices or a monolith?

**Dialectic Response**:

#### THESIS: Microservices
**Core Claim**: Decomposed services enable scalability and team autonomy.

**Arguments**:
1. Independent scaling of components
2. Technology diversity per service
3. Team ownership and accountability
4. Fault isolation
5. Easier continuous deployment per service

**Ideal Conditions**: Large teams, varying scale requirements, polyglot needs

**Steel-man**: In a 500-person engineering org with 50 teams, microservices let each team own their destiny. They can scale, deploy, and evolve independently. The coordination overhead is worth the autonomy gained.

---

#### ANTITHESIS: Monolith
**Core Claim**: Unified codebase enables simplicity and consistency.

**Arguments**:
1. Simpler local development
2. Easier debugging and tracing
3. No network latency between components
4. Consistent tooling and patterns
5. Lower operational complexity

**Ideal Conditions**: Small teams, early-stage products, unclear domain boundaries

**Steel-man**: A 10-person startup with a monolith can move 10x faster than one wrestling with Kubernetes. Every minute spent on service mesh configuration is a minute not spent on product. Ship first, decompose later.

---

#### SYNTHESIS: Modular Monolith → Evolutionary Architecture
**Resolution**: The binary is false. Architecture should evolve with understanding.

**The Higher Truth**:
- From Microservices: The importance of clear boundaries and team ownership
- From Monolith: The value of simplicity and fast iteration
- Transcendent insight: **Start with a modular monolith with clear internal boundaries, extract services only at proven pain points**

**Practical Guidance**:
- Start monolith when: Team < 20, domain unclear, speed critical
- Extract services when: Clear bounded context, scaling bottleneck proven, team needs autonomy
- Default: Monolith with service-ready module boundaries

**New Questions Raised**: How do we identify the right extraction points? What's the cost of premature extraction vs late extraction?

---

### Example 2: Process Decision

**User**: Should we document everything or move fast?

**Dialectic Response**:

#### THESIS: Document Everything
**Core Claim**: Documentation enables scaling and reduces bus factor.

**Arguments**:
1. Onboarding becomes self-serve
2. Decisions are traceable
3. Knowledge survives turnover
4. Reduces "that's how we've always done it"

**Steel-man**: Amazon's 6-pager culture forces clarity of thought. The act of writing IS thinking. Documentation isn't overhead—it's the work.

---

#### ANTITHESIS: Move Fast
**Core Claim**: Documentation is waste; working software is truth.

**Arguments**:
1. Docs become stale immediately
2. Time documenting = time not building
3. Code is the real documentation
4. Startups die from slowness, not lack of docs

**Steel-man**: Every successful startup moved fast and broke things. Google's early code had zero documentation. The documentation was the product working.

---

#### SYNTHESIS: Document Decisions, Not Implementations
**Resolution**: Document the WHY, not the HOW. Code documents HOW.

**The Higher Truth**:
- From Documentation: Capture irreplaceable context (decisions, constraints, tradeoffs)
- From Speed: Don't duplicate what code already says
- Transcendent: **ADRs (Architecture Decision Records) + self-documenting code + living diagrams**

**Practical Guidance**:
- Always document: Decisions, constraints, non-obvious tradeoffs
- Never document: Implementation details the code shows
- Default: ADR for every significant decision, nothing else

---

## Advanced Patterns

### Recursive Dialectic
When the synthesis itself becomes contested, apply the dialectic again:
- Synthesis becomes new Thesis
- New opposition emerges as Antithesis
- Higher synthesis emerges

### Multi-Polar Dialectic
For decisions with more than two positions:
1. Identify all distinct positions
2. Run pairwise dialectics
3. Synthesize the syntheses
4. Continue until convergence

### Temporal Dialectic
When positions are right at different times:
- Thesis: Right now
- Antithesis: Right later
- Synthesis: Evolution path from now to later

## Anti-Patterns to Avoid

1. **False Balance**: Don't create artificial opposition where one side is clearly wrong
2. **Weak Steel-men**: Present each position at its strongest, not its weakest
3. **Premature Synthesis**: Let the tension exist; don't rush to resolution
4. **Binary Trap**: Sometimes there are 3+ valid positions
5. **Analysis Paralysis**: The goal is better decisions, not endless deliberation

## Integration with Other Skills

- Use with `sparc-methodology` for architectural decisions
- Use with `socratic-questioning` to clarify the question first
- Use with `session-memory` to track dialectic evolution over time

---

*"The owl of Minerva spreads its wings only with the falling of the dusk."*
— G.W.F. Hegel

Understanding comes from working through contradiction, not avoiding it.
