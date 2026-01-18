# Multi-Archetype Code Audit

A comprehensive code audit skill using 7 specialized archetypes, each providing a unique perspective on code quality.

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

### As a Standalone Script

```bash
# Quick audit (3 archetypes: HERMES, DIONYSUS, HEPHAESTUS)
python scripts/audit.py /path/to/project --quick

# Full audit (all 7 archetypes)
python scripts/audit.py /path/to/project

# Security-focused audit
python scripts/audit.py /path/to/project --security

# Performance-focused audit
python scripts/audit.py /path/to/project --performance

# Custom archetype selection
python scripts/audit.py /path/to/project --archetypes cassandra sisyphus icarus

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
    archetypes=["dionysus", "hephaestus"],
    severity_threshold=Severity.HIGH
)
```

## The 7 Archetypes

| Icon | Name | Domain | What It Finds |
|------|------|--------|---------------|
| ⚡ | **HERMES** | API | Endpoint naming, auth gaps, response models |
| ☀️ | **RA** | Performance | Blocking calls, N+1 patterns, cache opportunities |
| 🔮 | **CASSANDRA** | Warnings | TODOs, FIXMEs, deprecated code, bare excepts |
| 🪨 | **SISYPHUS** | Repetition | Duplicate functions, DRY violations |
| 🌞 | **ICARUS** | Complexity | God classes, over-abstraction, pattern overuse |
| 🍷 | **DIONYSUS** | Robustness | Injection risks, null handling, edge cases |
| 🔨 | **HEPHAESTUS** | Build | Unpinned deps, Docker issues, CI/CD gaps |

## Audit Presets

| Preset | Archetypes | Use Case |
|--------|------------|----------|
| `--quick` | HERMES, DIONYSUS, HEPHAESTUS | Fast pre-commit check |
| `--security` | DIONYSUS, HEPHAESTUS, HERMES | Security review |
| `--performance` | RA, ICARUS | Performance optimization |
| (default) | All 7 | Comprehensive audit |

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

## License

MIT

## Credits

Inspired by the multi-perspective audit methodology from the Smash Coach AI project.
