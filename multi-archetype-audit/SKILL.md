---
name: multi-archetype-audit
description: Run comprehensive code audits using FENRIR 2.0 (6-pass scanner) + NILE system with unified pipeline. 20 specialized archetypes with 45+ detection patterns covering API, Performance, Security, AI Safety, Silent Failures, and Parallel Implementation Blindness.
version: 4.0.0
---

# Multi-Archetype Code Audit (NILE Integration)

A comprehensive code audit system with **unified pipeline**:

```
┌──────────────────────────────────────────────────────┐
│              UNIFIED AUDIT PIPELINE                  │
├──────────────────────────────────────────────────────┤
│  1. FENRIR 2.0  → 6-pass scanner (4776 LOC)          │
│     ├── P1-P5   → Regex + AST + Ruff                 │
│     ├── GARM    → Zombie/leak detection              │
│     └── 20 Archetypes (45+ patterns)                 │
│  2. OUROBOROS   → Anti self-detection filter         │
│  3. RAG         → Lucioles context enrichment        │
│  4. MEMORY      → Past verdicts lookup               │
│  5. MEMNARCH    → SPO triplets + decisions (opt)     │
│  6. OSIRIS      → Final verdict + score              │
└──────────────────────────────────────────────────────┘
```

No external LLM required - Claude Code does the intelligent triage.

## When to Use This Skill

- Before releases to catch issues across multiple dimensions
- During code reviews for comprehensive analysis
- When onboarding to a new codebase
- For AI/LLM projects: prompt injection, cost optimization, data leakage
- Pre-commit checks to block critical issues

## The 20 Archetypes

### Core 7 (Greek Mythology)

| Archetype | Domain | What It Finds |
|-----------|--------|---------------|
| **HERMES** | API | Endpoint naming, auth gaps, HTTP methods |
| **RA** | Performance | Blocking calls, N+1 patterns, missing caches |
| **CASSANDRA** | Warnings | TODOs, FIXMEs, deprecated code, bare excepts |
| **SISYPHUS** | Repetition | Duplicate functions, DRY violations |
| **ICARUS** | Complexity | God classes, over-abstraction |
| **DIONYSUS** | Robustness | Missing error handling, injection risks |
| **HEPHAESTUS** | Build | Unpinned deps, Docker issues, CI gaps |

### Extended 12 (Security, AI, Quality)

| Archetype | Domain | What It Finds |
|-----------|--------|---------------|
| **PANDORA** | Security | Hardcoded secrets, CORS wildcards |
| **DELPHI** | AI Safety | Prompt injection, missing LLM validation |
| **MIDAS** | LLM Costs | Missing caching, expensive model usage |
| **LETHE** | Data Leakage | Sensitive data in logs, debug mode |
| **ANTAEUS** | Resilience | Missing retries, timeouts |
| **TIRESIAS** | Testing | Low coverage, weak assertions |
| **PROTEUS** | State | Mutable defaults, global state |
| **MNEMOSYNE** | Context | Correlation IDs, tracing |
| **ARIADNE** | Dependencies | Circular imports, unpinned versions |
| **JANUS** | Versioning | API versions, deprecation markers |
| **ARGUS** | Observability | Logging, metrics, health checks |

### Nordic Hunters (Silent Failure Specialists)

| Archetype | Domain | What It Finds |
|-----------|--------|---------------|
| **FENRIR** | Silent Failures | `except: pass`, swallowed errors |
| **GARM** | Zombie Patterns | Zombie subprocess, orphan threads, resource leaks, async orphans |

### Meta Archetype (Architecture)

| Archetype | Domain | What It Finds |
|-----------|--------|---------------|
| **ORPHEUS** | Parallel Blindness | Versioned modules without DEPRECATED, orphan candidates |

## Instructions

### Full NILE Audit (Recommended)

When user invokes `/audit [path]`, execute the unified pipeline:

1. **FENRIR 2.0**: 6-pass static analysis (Regex → AST → Ruff → GARM → ORPHEUS)
2. **OUROBOROS**: Anti self-detection (audit code doesn't flag itself)
3. **RAG**: Lucioles context enrichment (350 indexed docs)
4. **MEMORY**: Past verdicts lookup (skip known false positives)
5. **MEMNARCH** (optional): SPO triplets + decision correlation
6. **OSIRIS**: Final verdict (WORTHY/CURSED/FORBIDDEN) + score

```python
# Python API
from app.core.audit_unified import run_unified_audit

# Standard audit
result = await run_unified_audit("app/", use_rag=True)

# With Memnarch (SPO triplets + decision correlation)
result = await run_unified_audit("app/", use_rag=True, use_memnarch=True)
```

### Quick Mode (FENRIR Only)

```bash
# Just static analysis, no NILE components
python scripts/audit.py {path} --fenrir-only
```

### Triage Findings (You, Claude Code)

For each finding from FENRIR:
1. Read the file context (±10 lines around the finding)
2. Check if a Sentinelle applies (cross-reference)
3. Determine if it's a **TRUE_POSITIVE** or **FALSE_POSITIVE**
4. Classify severity: CRITICAL, HIGH, MEDIUM, LOW, INFO

**False Positive Indicators:**
- Pattern is inside a docstring or `example_code` string
- It's defensive parsing code (AST, JSON, XML)
- It's a status/health check function
- It's intentionally permissive (catch-all for graceful degradation)
- It's in test fixtures

### Generate Report

Output a Markdown report with:
- OSIRIS Verdict (WORTHY/CURSED/FORBIDDEN)
- Sentinelles applied
- FENRIR stats by severity
- True positives only (sorted by severity)
- Detailed score calculation

## Score Calculation

```
Score = 100 - (MORTEL × 10) - (GRAVE × 3) - (SUSPECT × 1)
        + (Sentinelles_applied × 2)
        + (ANKH_blessing × 5)
        - (SERPENT_danger × 5)
```

**Verdict Mapping:**
- `WORTHY`: Score >= 80
- `CURSED`: Score 50-79
- `FORBIDDEN`: Score < 50

## Severity Levels

| Level | Points | Action |
|-------|--------|--------|
| MORTEL | -10 | Fix immediately |
| GRAVE | -3 | Fix before release |
| SUSPECT | -1 | Plan to fix |
| INFO | 0 | Optional |

## Technical Features

- **FENRIR 2.0**: 6-pass scanner (4776 LOC, 20 archetypes, 45+ patterns)
- **Ouroboros**: Self-exclusion of audit files (audit code doesn't flag itself)
- **AST String Filter**: Eliminates FP in docstrings/example_code
- **GARM Pass**: Zombie subprocess, orphan threads, resource leaks, async orphans
- **ORPHEUS Pass**: Parallel implementation blindness detection
- **Graph RAG**: Neo4j relations between Lucioles (if available)
- **MEMNARCH**: Optional SPO triplet extraction + decision correlation
- **Direct Import Detection**: Handles modules using `from X.submodule import Y` style

## Standalone Usage (CI/CD)

For automated pipelines without Claude Code interactive session:

```bash
# FENRIR only (free, instant)
python scripts/audit.py /path --fenrir-only --ci

# With Claude API triage (requires ANTHROPIC_API_KEY)
python scripts/audit.py /path --ci

# JSON output
python scripts/audit.py /path --fenrir-only --json
```

Exit codes:
- 0: No critical/high issues (WORTHY)
- 1: High issues found (CURSED)
- 2: Critical issues found (FORBIDDEN)

## Pre-commit Hook

```bash
# Install
ln -sf scripts/pre-commit .git/hooks/pre-commit

# Blocks commit if MORTEL (critical) findings detected
# Warns on GRAVE (high) findings
```

## Best Practices

1. **Use full NILE audit** for releases - Gets Sentinelle context
2. **Use quick mode** for pre-commit - Fast feedback
3. **Focus on MORTEL/GRAVE first** - Triage high severity
4. **Trust the context** - Read surrounding code before judging
5. **Don't over-filter** - When in doubt, it's a true positive
6. **Update patterns** - Add new archetypes for recurring issues
