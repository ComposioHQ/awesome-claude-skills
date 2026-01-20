---
name: multi-archetype-audit
description: Run comprehensive code audits using FENRIR (static analysis) + Claude Code (intelligent triage). 19 specialized archetypes covering API, Performance, Security, AI Safety, and Observability. No external LLM required.
version: 3.0.0
---

# Multi-Archetype Code Audit

A two-stage code audit system:
1. **FENRIR** - Fast static analysis (regex + AST)
2. **Claude Code** - Intelligent triage (you, the AI assistant)

No Ollama, no DeepSeek, no external LLM. Claude Code does the smart work.

## When to Use This Skill

- Before releases to catch issues across multiple dimensions
- During code reviews for comprehensive analysis
- When onboarding to a new codebase
- For AI/LLM projects: prompt injection, cost optimization, data leakage
- Pre-commit checks to block critical issues

## The 19 Archetypes

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
| **MENTOR** | Documentation | Missing docstrings, type hints |
| **PROTEUS** | State | Mutable defaults, global state |
| **MNEMOSYNE** | Context | Missing correlation IDs |
| **ARIADNE** | Dependencies | Circular imports, unpinned versions |
| **JANUS** | Versioning | API versions, deprecation markers |
| **ARGUS** | Observability | Logging, metrics, health checks |

### Nordic Hunters (Silent Failure Specialists)

| Archetype | Domain | What It Finds |
|-----------|--------|---------------|
| **FENRIR** | Silent Failures | `except: pass`, swallowed errors |
| **GARM** | Zombie Patterns | Dead code creating problems |

## Instructions

### Step 1: Run FENRIR (Static Analysis)

```bash
# In the project directory
python scripts/audit.py {path} --fenrir-only --json
```

This runs in ~2 seconds and produces raw findings.

### Step 2: Triage Findings (You, Claude Code)

For each finding from FENRIR:
1. Read the file context (±10 lines around the finding)
2. Determine if it's a **TRUE_POSITIVE** or **FALSE_POSITIVE**
3. Classify severity: CRITICAL, HIGH, MEDIUM, LOW, INFO

**False Positive Indicators:**
- Pattern is inside a docstring or `example_code` string
- It's defensive parsing code (AST, JSON, XML)
- It's a status/health check function
- It's intentionally permissive (catch-all for graceful degradation)
- It's in test fixtures

### Step 3: Generate Report

Output a Markdown report with:
- Summary stats (by severity)
- True positives only (sorted by severity)
- Suggested fixes

## Example Triage

```
FENRIR Finding:
  File: semantic_sentinelles.py:91
  Pattern: except_pass
  Code: except Exception: pass

Claude Code Analysis:
  Context: This is inside an `example_code=""" ... """` string
  Verdict: FALSE_POSITIVE
  Reason: Documentation example, not real code
```

## Severity Levels

| Level | Meaning | Action |
|-------|---------|--------|
| CRITICAL | Security vulnerability | Fix immediately |
| HIGH | Significant issue | Fix before release |
| MEDIUM | Technical debt | Plan to fix |
| LOW | Minor improvement | Fix when convenient |
| INFO | Informational | Review and decide |

## Standalone Usage (CI/CD)

For automated pipelines without Claude Code interactive session:

```bash
# FENRIR only (free, instant)
python scripts/audit.py /path --fenrir-only --ci

# With Claude API triage (requires ANTHROPIC_API_KEY)
python scripts/audit.py /path --ci
```

Exit codes:
- 0: No critical/high issues
- 1: High issues found
- 2: Critical issues found

## Pre-commit Hook

```bash
# Install
ln -sf scripts/pre-commit .git/hooks/pre-commit

# Blocks commit if MORTEL (critical) findings detected
# Warns on GRAVE (high) findings
```

## Best Practices

1. **Start with FENRIR only** - Get fast feedback
2. **Focus on CRITICAL/HIGH** - Triage those first
3. **Trust the context** - Read surrounding code before judging
4. **Don't over-filter** - When in doubt, it's a true positive
5. **Update patterns** - Add new archetypes for recurring issues
