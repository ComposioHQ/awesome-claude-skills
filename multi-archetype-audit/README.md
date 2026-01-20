# Multi-Archetype Code Audit

A comprehensive code audit skill using **19 specialized archetypes**, each providing a unique perspective on code quality. From API contracts to AI safety, from security boundaries to observability - get a 360° view of your codebase.

## Installation

Copy the `multi-archetype-audit` folder to your Claude Code skills directory:

```bash
cp -r multi-archetype-audit ~/.claude/skills/
```

Or add directly to your project's `.claude/skills/` directory.

## Usage

### As a Skill

When active, Claude will use this skill to perform comprehensive code audits. Just ask:

- "Run a quick code audit on this project"
- "Check for security issues in the codebase"
- "Find technical debt and TODOs"
- "Audit the API endpoints"
- "Check for AI/LLM safety issues"
- "Review observability and monitoring"

### As a Standalone Script

```bash
# Quick audit (3 archetypes: HERMES, DIONYSUS, HEPHAESTUS)
python scripts/audit.py /path/to/project --quick

# Full audit (all 19 archetypes)
python scripts/audit.py /path/to/project

# Security-focused audit
python scripts/audit.py /path/to/project --security

# Performance-focused audit
python scripts/audit.py /path/to/project --performance

# Custom archetype selection
python scripts/audit.py /path/to/project --archetypes delphi midas pandora argus

# JSON output for CI/CD integration
python scripts/audit.py /path/to/project --json
```

### As a Python Library

```python
from audit import run_full_audit, run_quick_audit, AuditOrchestrator

# Quick audit
report = run_quick_audit()
print(report.to_markdown())

# Full audit
report = run_full_audit()
print(f"Found {len(report.findings)} issues")

# Custom audit
orchestrator = AuditOrchestrator()
report = orchestrator.run_audit(
    archetypes=["delphi", "midas", "pandora"],  # AI-focused
    severity_threshold=Severity.HIGH
)
```

## The 19 Archetypes

### Core 7 (Greek Mythology)

| Icon | Name | Domain | What It Finds |
|------|------|--------|---------------|
| ⚡ | **HERMES** | API | Endpoint naming, auth gaps, response models |
| ☀️ | **RA** | Performance | Blocking calls, N+1 patterns, cache opportunities |
| 🔮 | **CASSANDRA** | Warnings | TODOs, FIXMEs, deprecated code, bare excepts |
| 🪨 | **SISYPHUS** | Repetition | Duplicate functions, DRY violations |
| 🌞 | **ICARUS** | Complexity | God classes, over-abstraction, pattern overuse |
| 🍷 | **DIONYSUS** | Robustness | Injection risks, null handling, edge cases |
| 🔨 | **HEPHAESTUS** | Build | Unpinned deps, Docker issues, CI/CD gaps |

### Extended 12 (Security, AI, Resilience, Quality)

| Icon | Name | Domain | What It Finds |
|------|------|--------|---------------|
| 📦 | **PANDORA** | Security | Hardcoded secrets, CORS issues, auth boundaries |
| 🔮 | **DELPHI** | AI Safety | Prompt injection, output validation, LLM guardrails |
| 💰 | **MIDAS** | LLM Costs | Missing caching, expensive models, token optimization |
| 🌊 | **LETHE** | Data Leakage | Sensitive data in logs, debug mode, PII exposure |
| 🏔️ | **ANTAEUS** | Resilience | Missing retries, timeouts, circuit breakers |
| 👁️‍🗨️ | **TIRESIAS** | Testing | Test coverage gaps, weak assertions, flaky tests |
| 📚 | **MENTOR** | Documentation | Missing docstrings, type hints, README |
| 🌀 | **PROTEUS** | State | Mutable defaults, global state, thread safety |
| 🧠 | **MNEMOSYNE** | Context | Correlation IDs, context propagation, logging context |
| 🧵 | **ARIADNE** | Dependencies | Unpinned versions, circular imports, unused deps |
| 🚪 | **JANUS** | Versioning | API versions, deprecation markers, migrations |
| 👁️ | **ARGUS** | Observability | Structured logging, metrics, tracing, health checks |

## Audit Presets

| Preset | Archetypes | Use Case |
|--------|------------|----------|
| `--quick` | HERMES, DIONYSUS, HEPHAESTUS | Fast pre-commit check |
| `--security` | DIONYSUS, HEPHAESTUS, HERMES, PANDORA, LETHE | Security review |
| `--performance` | RA, ICARUS, ANTAEUS | Performance & resilience |
| (default) | All 19 | Comprehensive audit |

## Severity Levels

| Level | Meaning |
|-------|---------|
| 🔴 CRITICAL | Security vulnerability - fix immediately |
| 🟠 HIGH | Significant issue - fix before release |
| 🟡 MEDIUM | Technical debt - plan to fix |
| 🟢 LOW | Minor improvement |
| ⚪ INFO | Informational only |

## CI/CD Integration

Add to your GitHub Actions:

```yaml
- name: Code Audit
  run: |
    python skills/multi-archetype-audit/scripts/audit.py . --json > audit.json
    if grep -q '"severity": "CRITICAL"' audit.json; then
      echo "Critical issues found!"
      exit 1
    fi
```

## Extending

Create custom archetypes by extending `BaseArchetype`:

```python
from audit import BaseArchetype, AuditReport, AuditFinding, Severity

class MyAuditor(BaseArchetype):
    name = "CUSTOM"
    description = "My Custom Auditor"
    domain = "custom"
    icon = "🔧"

    def audit(self) -> AuditReport:
        findings = []
        # Your audit logic here
        matches = self._grep_files(r"pattern", "*.py")
        for file_path, line_num, line in matches:
            findings.append(AuditFinding(
                archetype=self.name,
                severity=Severity.MEDIUM,
                category="custom",
                title="Found pattern",
                file_path=str(file_path),
                line_number=line_num,
            ))
        return AuditReport(...)
```

## AI/LLM-Specific Archetypes

Three archetypes are specifically designed for AI/LLM applications:

- **DELPHI** - Checks for prompt injection vulnerabilities, missing output validation, and LLM guardrails
- **MIDAS** - Identifies cost optimization opportunities: missing caching, expensive model usage, token waste
- **LETHE** - Detects data leakage risks: sensitive data in logs, debug mode enabled, PII exposure

Use them together for AI projects:
```bash
python scripts/audit.py . --archetypes delphi midas lethe pandora
```

## Ouroboros Guard (False Positive Protection)

The audit includes built-in protection against false positives when scanning its own code or detection patterns:

1. **Directory Exclusion** - Automatically skips `audit/`, `skills/`, `patterns/`, `detectors/` directories
2. **Detection Variable Recognition** - Ignores lines defining `*_PATTERNS`, `*_RULES`, `*_SIGNATURES` variables
3. **Annotation Support** - Respects `# nosec`, `# noqa`, `# audit-ignore` comments

```python
# This is flagged (real vulnerability):
password = "hardcoded123"

# This is NOT flagged (detection pattern):
DANGEROUS_PATTERNS = ["password", "secret", "api_key"]

# This is NOT flagged (suppressed):
test_password = "test123"  # nosec - test fixture
```

## License

MIT

## Credits

Inspired by the multi-perspective audit methodology from the Smash Coach AI project (Phase 301.5).
