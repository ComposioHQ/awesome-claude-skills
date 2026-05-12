---
name: add-agent-driven-development
description: Structured SDLC methodology plugin for Claude Code where AI agents are first-class development team members, with spec-driven workflows, strict TDD enforcement, away mode for autonomous work, and a 3-tier learning system.
---

# ADD (Agent Driven Development)

ADD is a methodology plugin for Claude Code — like TDD or BDD, but designed for the reality that AI agents do the development work while humans architect, interview, decide, and verify. It provides a complete structured SDLC with specifications, test-driven development, quality gates, and continuous learning.

## When to Use This Skill

- Starting a new project where AI agents will handle most of the coding
- Enforcing spec-driven development so nothing gets built without a specification
- Running strict TDD cycles (RED → GREEN → REFACTOR → VERIFY) with AI
- Stepping away from your computer and letting Claude work autonomously with guardrails
- Managing project maturity from proof-of-concept through general availability
- Accumulating and reusing knowledge across projects through a 3-tier learning system

## What This Skill Does

1. **Spec-Driven Workflows**: Everything flows from specifications — no code without a spec, no spec without an interview
2. **Strict TDD Enforcement**: RED → GREEN → REFACTOR → VERIFY cycle with independent verification by a separate sub-agent
3. **Away Mode**: Step away and let Claude work autonomously within defined boundaries, then get a structured briefing when you return
4. **Maturity Lifecycle**: Automatically adjusts rigor levels (poc → alpha → beta → ga) across all quality gates
5. **3-Tier Learning System**: Plugin-global, user-local, and project-specific knowledge tiers that cascade and persist across sessions
6. **Quality Gates**: 5-level quality gate system that scales with project maturity
7. **Environment-Aware Deployment**: Skills adapt to your deployment tier with automatic promotion ladders

## How to Use

### Installation

```bash
claude plugin install add
```

### Initialize a Project

```
/add:init
```

This runs a structured interview to create your PRD and project configuration.

### Create a Feature Spec

```
/add:spec
```

Walks you through a feature interview and generates a specification document.

### Plan and Build

```
/add:plan specs/my-feature.md
/add:tdd-cycle specs/my-feature.md
```

Generates an implementation plan from the spec, then executes the full TDD cycle.

### Away Mode

```
/add:away 2h
```

Step away from your computer. Claude works autonomously — committing, pushing, fixing quality gates — within defined boundaries (no production deploys, no merging to main without approval).

### Return and Review

```
/add:back
```

Get a structured briefing on everything that happened while you were away.

### Retrospective

```
/add:retro
```

Run a retrospective to capture lessons learned and promote knowledge up the tier system.

## Example

**User**: `/add:init`

**Claude**: Runs a structured interview asking about the project's purpose, target users, key features, maturity level, and deployment targets. Produces:

```
docs/prd.md          — Product Requirements Document
.add/config.json     — Project configuration (maturity level, environments, quality gates)
.add/learnings.md    — Project-specific knowledge store
```

**User**: `/add:spec`

**Claude**: Interviews you about the feature, then generates:

```
specs/user-auth.md   — Feature specification with acceptance criteria and test cases
```

**User**: `/add:tdd-cycle specs/user-auth.md`

**Output**:
```
RED phase:    Writing failing tests from spec test cases...
              5 tests written, all failing (as expected)

GREEN phase:  Implementing minimum code to pass tests...
              5/5 tests passing

REFACTOR:     Improving code quality while keeping tests green...
              5/5 tests still passing

VERIFY:       Independent sub-agent verifying against spec...
              All acceptance criteria met
              Quality gates passed (Level 3 - Beta)
              Checkpoint saved to .add/learnings.md
```

## Tips

- Start with `/add:init` to bootstrap — it sets up the entire document hierarchy
- Use `/add:cycle` to plan batches of work within milestones
- The maturity level (poc/alpha/beta/ga) controls how strict quality gates are — start with `poc` for prototypes
- Away mode defaults to 2 hours; always review the briefing from `/add:back`
- Knowledge accumulates automatically — checkpoints fire after every verify, TDD cycle, and deployment
- Use `/add:retro` to promote project discoveries to your cross-project library

## Key Commands

| Command | Purpose |
|---------|---------|
| `/add:init` | Bootstrap ADD in a new project |
| `/add:spec` | Create a feature spec via interview |
| `/add:plan` | Generate implementation plan from spec |
| `/add:tdd-cycle` | Execute full TDD cycle (RED, GREEN, REFACTOR, VERIFY) |
| `/add:verify` | Run quality gates |
| `/add:away` | Autonomous work mode with guardrails |
| `/add:back` | Get briefing after away mode |
| `/add:retro` | Retrospective and knowledge promotion |
| `/add:deploy` | Environment-aware deployment |
| `/add:cycle` | Plan and track work cycles within milestones |

## Common Use Cases

- Solo developers who want AI to handle implementation while they focus on architecture
- Teams adopting AI-assisted development with structured guardrails
- Projects that need strict TDD enforcement with independent verification
- Long-running sessions where the developer steps away and Claude continues working
- Multi-project workflows where learnings from one project benefit the next
