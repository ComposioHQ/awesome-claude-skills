---
name: multi-ai-agents
description: Distribute tasks across Claude, Gemini CLI, and Codex CLI in parallel. Use x3/x5/x7 shorthand to spawn multi-agent workloads where Claude orchestrates, Gemini analyzes, and Codex generates code.
---

# Multi-AI Agent Dispatcher

Distribute complex tasks across three AI engines simultaneously — **Claude** (orchestrator + critical decisions), **Gemini CLI** (analysis + review), and **Codex CLI** (code generation + refactoring). Use simple shorthand commands to spawn parallel workloads.

## When to Use This Skill

- You have a complex task that benefits from multiple AI perspectives
- You want to offload read-only/analysis work to Gemini (free tier) to save Claude tokens
- You need fast code scaffolding from Codex while Claude handles architecture
- You want cross-validation between different AI models
- You're working on a large feature that can be decomposed into parallel subtasks

## Prerequisites

Install Gemini CLI and Codex CLI:

```bash
npm install -g @google/gemini-cli
npm install -g @openai/codex
```

Authenticate both:
```bash
gemini  # Follow OAuth flow
codex login  # Follow login flow
```

## What This Skill Does

1. **Task Decomposition**: Breaks your task into subtasks matched to each AI's strength
2. **Parallel Dispatch**: Runs Claude subagents, Gemini CLI, and Codex CLI simultaneously
3. **Result Synthesis**: Claude collects all outputs, resolves conflicts, picks the best parts
4. **Quality Gate**: Runs verification (e.g., `tsc`, `lint`) before reporting final result

## Agent Distribution

```
┌─────────────────────────────────────────┐
│          CLAUDE (Orchestrator)          │
│   Decompose → Dispatch → Synthesize    │
└────────┬──────────────┬────────────────┘
         │              │
 ┌───────▼──────┐  ┌───▼───────────┐
 │  GEMINI CLI  │  │  CODEX CLI    │
 │  Analysis &  │  │  Code gen &   │
 │  Review      │  │  Refactoring  │
 └───────┬──────┘  └───┬───────────┘
         │              │
┌────────▼──────────────▼────────────────┐
│          CLAUDE (Synthesis)            │
│   Merge → Quality gate → Report       │
└────────────────────────────────────────┘
```

### Distribution Table

| Shorthand | Total | Claude | Gemini | Codex |
|-----------|-------|--------|--------|-------|
| `x3`      | 3     | 1      | 1      | 1     |
| `x5`      | 5     | 2      | 2      | 1     |
| `x7`      | 7     | 3      | 2      | 2     |

### Who Gets What

| Agent | Best For | Avoid |
|-------|----------|-------|
| **Claude** | Architecture, critical logic, edge cases, final decisions | Repetitive bulk work |
| **Gemini** | Read-only analysis, summaries, docs, code review, second opinions | Write operations, critical code |
| **Codex** | Scaffolding, boilerplate, mechanical refactoring, pattern transforms | Complex architecture decisions |

## How to Use

### Basic Usage

```
/x 3 find and fix all type errors in the auth module
```

This spawns:
- **Claude**: Analyzes root causes of type errors, fixes critical ones
- **Gemini**: Scans the module for patterns and suggests improvements
- **Codex**: Generates type-safe replacements for `as any` casts

### Advanced Usage

```
/x 5 build a complete authentication system with JWT, refresh tokens, and role-based access
```

This spawns:
- **Claude #1**: Designs the auth architecture and middleware
- **Claude #2**: Writes tests and handles edge cases
- **Gemini #1**: Reviews security implications, checks OWASP compliance
- **Gemini #2**: Generates API documentation
- **Codex**: Scaffolds the boilerplate (routes, types, config files)

### Heavy Workload

```
/x 7 refactor the entire data layer from Prisma to Drizzle ORM
```

## Example

**User**: `/x 3 review this API module for security issues and fix them`

**Output**:

```
## x3 Task Report

### Task: Review API module for security issues and fix them
### Distribution: 3 agents (1 Claude + 1 Gemini + 1 Codex)

| # | Agent  | Subtask                    | Result          |
|---|--------|----------------------------|-----------------|
| 1 | Claude | Fix SQL injection in query  | 2 files patched |
| 2 | Gemini | Security audit + OWASP scan | 4 findings      |
| 3 | Codex  | Add input validation        | 3 validators    |

### Synthesis:
- Gemini found 4 issues, Claude confirmed 3 as real vulnerabilities
- Codex generated validators, Claude reviewed and approved 2 of 3
- 1 Gemini finding was false positive (dismissed)

### Changes Applied:
- `src/api/users.ts`: Parameterized SQL query (was string concat)
- `src/api/middleware.ts`: Added rate limiting
- `src/lib/validators.ts`: New input validation schemas

### Quality Gate:
- TypeScript: 0 errors ✓
- Tests: All passing ✓

### Next Action:
Run integration tests to verify auth flow end-to-end
```

## Quality Control

After every multi-agent run:
1. All outputs are synthesized by Claude (never blindly applied)
2. Conflicts between agents are flagged and resolved
3. Code changes pass through quality gate (`tsc`, `lint`, tests)
4. If quality drops → tighten task descriptions, move critical work back to Claude

## Tips

- Start with `x3` for most tasks — only scale up for genuinely large workloads
- Gemini works best with clear, specific prompts (not vague "improve this")
- Codex `--full-auto` runs in sandbox mode — safe for code generation
- Claude always has final say — other agents provide input, not decisions
- If Gemini or Codex fails (API error, rate limit), Claude automatically takes over that subtask
- Add project-specific context to your `CLAUDE.md` so all agents benefit from it

## Common Use Cases

- **Feature development**: Claude architects, Codex scaffolds, Gemini reviews
- **Bug investigation**: Gemini scans logs/code, Claude diagnoses, Codex patches
- **Refactoring**: Codex does mechanical transforms, Claude handles tricky parts, Gemini validates
- **Security audit**: Gemini scans for vulnerabilities, Claude prioritizes, Codex generates fixes
- **Documentation**: Gemini drafts docs, Claude reviews accuracy, Codex formats/structures
