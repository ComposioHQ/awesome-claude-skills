---
name: multi-archetype-audit
description: Run comprehensive code audits using 7 specialized archetypes (API, Performance, Warnings, DRY, Complexity, Chaos, Build). Each archetype provides a unique perspective on code quality. Activate with /audit command.
---

# Multi-Archetype Code Audit

A multi-perspective code audit system where each archetype represents a different aspect of code quality. Run all archetypes together or select specific ones based on your needs.

## Activation

### Option 1: Slash Command (Recommended)

Create `.claude/commands/audit.md` in your project:

```markdown
# /audit - Multi-Archetype Code Audit

Run comprehensive code audits with 7 specialized archetypes.

## Usage
- `/audit` - Full audit (7 archetypes)
- `/audit --quick` - Quick audit (3 archetypes)
- `/audit --security` - Security focus
- `/audit --performance` - Performance focus

## Command
python path/to/audit.py . [options]
```

Then add to `.claude/settings.local.json`:
```json
{
  "permissions": {
    "allow": ["Skill(audit)"]
  }
}
```

### Option 2: Direct Script

```bash
python scripts/audit.py /path/to/project --quick
```

### Option 3: Python Import

```python
from audit import run_full_audit
report = run_full_audit()
```

## When to Use This Skill

- Before major releases to catch issues across multiple dimensions
- During code reviews for comprehensive analysis
- When onboarding to a new codebase to understand technical debt
- To identify security, performance, and maintainability issues
- When you need more than just linting - you need architectural insight

## The 7 Archetypes

| Archetype | Domain | What It Finds |
|-----------|--------|---------------|
| **HERMES** | API | Endpoint naming, auth gaps, response models, HTTP methods |
| **RA** | Performance | Blocking calls in async, N+1 patterns, missing caches |
| **CASSANDRA** | Warnings | TODOs, FIXMEs, deprecated code, stale dates, bare excepts |
| **SISYPHUS** | Repetition | Duplicate functions, copy-paste code, DRY violations |
| **ICARUS** | Complexity | God classes, over-abstraction, pattern overuse |
| **DIONYSUS** | Robustness | Missing error handling, edge cases, injection risks |
| **HEPHAESTUS** | Build | Unpinned deps, Docker issues, CI/CD gaps, env config |

## Instructions

### Quick Audit (3 essential archetypes)

Run HERMES, DIONYSUS, and HEPHAESTUS for a fast overview:

```python
from audit import run_quick_audit

report = run_quick_audit()
print(report.to_markdown())
```

### Full Audit (all 7 archetypes)

```python
from audit import run_full_audit

report = run_full_audit()
print(f"Found {len(report.findings)} issues")
print(report.to_markdown())
```

### Specialized Audits

```python
from audit import run_security_audit, run_performance_audit

# Security focus: DIONYSUS + HEPHAESTUS + HERMES
security_report = run_security_audit()

# Performance focus: RA + ICARUS
perf_report = run_performance_audit()
```

### Custom Selection

```python
from audit import AuditOrchestrator, Severity

orchestrator = AuditOrchestrator()

# List available archetypes
for arch in orchestrator.list_archetypes():
    print(f"{arch['icon']} {arch['name']}: {arch['description']}")

# Run specific archetypes
report = orchestrator.run_audit(
    archetypes=["cassandra", "sisyphus"],
    severity_threshold=Severity.MEDIUM
)
```

## Output Format

The audit produces a `UnifiedAuditReport` with:

- **Summary**: High-level overview of findings
- **Individual reports**: Per-archetype results
- **Findings**: Sorted by severity (CRITICAL > HIGH > MEDIUM > LOW > INFO)
- **Markdown export**: Ready for documentation

### Finding Structure

```python
AuditFinding(
    archetype="DIONYSUS",
    severity=Severity.HIGH,
    category="injection_risk",
    title="String interpolation in query",
    description="Potential SQL/Cypher injection",
    file_path="src/db/queries.py",
    line_number=42,
    code_snippet="query = f\"SELECT * FROM users WHERE id = {user_id}\"",
    suggestion="Use parameterized queries"
)
```

## Severity Levels

| Level | Meaning | Action |
|-------|---------|--------|
| CRITICAL | Security vulnerability or data loss risk | Fix immediately |
| HIGH | Significant issue affecting reliability | Fix before release |
| MEDIUM | Technical debt or maintainability issue | Plan to fix |
| LOW | Minor improvement opportunity | Fix when convenient |
| INFO | Informational, may not need action | Review and decide |

## Example Output

```markdown
# Multi-Archetype Audit Report

**Date**: 2026-01-18 14:30:00
**Duration**: 4823ms
**Archetypes**: HERMES, RA, CASSANDRA, SISYPHUS, ICARUS, DIONYSUS, HEPHAESTUS

## Summary

Found 127 issues across 7 archetypes. Severity: 2 critical, 15 high, 45 medium.
Most findings: CASSANDRA: 42, DIONYSUS: 35, SISYPHUS: 23.

## Critical & High Severity Findings

### [CRITICAL] Potential SQL injection
**Archetype**: DIONYSUS
**Location**: `src/api/users.py:156`

String interpolation used in database query...
```

## Extending with Custom Archetypes

Create a new archetype by extending `BaseArchetype`:

```python
from audit import BaseArchetype, AuditReport, AuditFinding, Severity

class MyCustomAuditor(BaseArchetype):
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
                category="custom_issue",
                title="Found pattern",
                file_path=str(file_path),
                line_number=line_num,
            ))

        return AuditReport(
            archetype=self.name,
            timestamp=datetime.now(),
            findings=findings,
            summary=f"Found {len(findings)} issues"
        )
```

## Best Practices

1. **Start with quick audit** - Get fast feedback before deep analysis
2. **Filter by severity** - Focus on CRITICAL/HIGH first
3. **Run before commits** - Catch issues early
4. **Export to markdown** - Share findings with team
5. **Customize thresholds** - Adjust for your project's maturity

## Integration Ideas

- **Pre-commit hook**: Run quick audit before each commit
- **CI/CD pipeline**: Fail builds on CRITICAL findings
- **Weekly reports**: Schedule full audits for tech debt tracking
- **Code review**: Include audit report in PR descriptions
