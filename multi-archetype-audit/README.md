# Multi-Archetype Code Audit

A comprehensive code audit skill using **19 specialized archetypes**, each providing a unique perspective on code quality. From API contracts to AI safety, from security boundaries to observability - get a 360° view of your codebase.

## Installation

Copy the `multi-archetype-audit` folder to your Claude Code skills directory:

```bash
cp -r multi-archetype-audit ~/.claude/skills/
```

Or add directly to your project's `.claude/skills/` directory.

## Usage

### Simple Commands

```bash
python scripts/audit.py /path/to/project           # Full audit (19 archetypes + filtering)
python scripts/audit.py /path/to/project --quick   # Fast pre-commit (3 archetypes)
python scripts/audit.py /path/to/project --raw     # No filtering (debug mode)
python scripts/audit.py /path/to/project --json    # JSON output for CI/CD
```

That's it. **V2 filtering runs automatically** - no extra flags needed.

### As a Claude Code Skill

Just ask Claude:
- "Run a code audit"
- "Quick audit before commit"
- "Check for security issues"

### As a Python Library

```python
from audit import run_full_audit, run_quick_audit

# Quick audit (3 archetypes)
report = run_quick_audit()
print(report.to_markdown())

# Full audit (19 archetypes)
report = run_full_audit()
print(f"Found {len(report.findings)} issues")
```

## The 19 Archetypes

### Core 7

| Icon | Name | Domain | What It Finds |
|------|------|--------|---------------|
| ⚡ | **HERMES** | API | Endpoint naming, auth gaps, response models |
| ☀️ | **RA** | Performance | Blocking calls, N+1 patterns, cache opportunities |
| 🔮 | **CASSANDRA** | Warnings | TODOs, FIXMEs, deprecated code, bare excepts |
| 🪨 | **SISYPHUS** | Repetition | Duplicate functions, DRY violations |
| 🌞 | **ICARUS** | Complexity | God classes, over-abstraction, pattern overuse |
| 🍷 | **DIONYSUS** | Robustness | Injection risks, null handling, edge cases |
| 🔨 | **HEPHAESTUS** | Build | Unpinned deps, Docker issues, CI/CD gaps |

### Extended 12

| Icon | Name | Domain | What It Finds |
|------|------|--------|---------------|
| 📦 | **PANDORA** | Security | Hardcoded secrets, CORS issues, auth boundaries |
| 🔮 | **DELPHI** | AI Safety | Prompt injection, output validation, LLM guardrails |
| 💰 | **MIDAS** | LLM Costs | Missing caching, expensive models, token optimization |
| 🌊 | **LETHE** | Data Leakage | Sensitive data in logs, debug mode, PII exposure |
| 🏔️ | **ANTAEUS** | Resilience | Missing retries, timeouts, circuit breakers |
| 👁️ | **TIRESIAS** | Testing | Test coverage gaps, weak assertions, flaky tests |
| 📚 | **MENTOR** | Documentation | Missing docstrings, type hints, README |
| 🌀 | **PROTEUS** | State | Mutable defaults, global state, thread safety |
| 🧠 | **MNEMOSYNE** | Context | Correlation IDs, context propagation, logging context |
| 🧵 | **ARIADNE** | Dependencies | Unpinned versions, circular imports, unused deps |
| 🚪 | **JANUS** | Versioning | API versions, deprecation markers, migrations |
| 👁️ | **ARGUS** | Observability | Structured logging, metrics, tracing, health checks |

## Severity Levels

| Level | Meaning |
|-------|---------|
| 🔴 CRITICAL | Security vulnerability - fix immediately |
| 🟠 HIGH | Significant issue - fix before release |
| 🟡 MEDIUM | Technical debt - plan to fix |
| 🟢 LOW | Minor improvement |
| ⚪ INFO | Informational only |

## Ouroboros Guard (Automatic FP Protection)

The audit includes built-in protection against false positives:

1. **Directory Exclusion** - Skips `audit/`, `skills/`, `patterns/`, `detectors/`
2. **Detection Variable Recognition** - Ignores `*_PATTERNS`, `*_RULES`, `*_SIGNATURES` definitions
3. **Annotation Support** - Respects `# nosec`, `# noqa`, `# audit-ignore` comments

```python
# This is flagged (real vulnerability):
password = "hardcoded123"

# This is NOT flagged (detection pattern):
DANGEROUS_PATTERNS = ["password", "secret", "api_key"]

# This is NOT flagged (suppressed):
test_password = "test123"  # nosec - test fixture
```

## CI/CD Integration

```yaml
- name: Code Audit
  run: |
    python scripts/audit.py . --json > audit.json
    if grep -q '"severity": "CRITICAL"' audit.json; then
      echo "Critical issues found!"
      exit 1
    fi
```

## License

MIT

## Credits

From the Smash Coach AI project (Phase 301.5).
