# Multi-Archetype Code Audit

**Version**: 3.0.0 (January 2026)

A comprehensive code audit skill using **19 specialized archetypes** with a two-stage approach:
1. **FENRIR** (static analysis) - Fast regex + AST scanning
2. **Claude Code** (intelligent triage) - Filters false positives, prioritizes issues

**No external LLM required** - Claude Code does the intelligent triage.

## Installation

```bash
# Copy to Claude Code skills directory
cp -r multi-archetype-audit ~/.claude/skills/

# Or add to your project
cp -r multi-archetype-audit .claude/skills/
```

## Usage

### Interactive (with Claude Code)

Just ask Claude:
- "Run an audit on app/core/"
- "Check for security issues"
- "Find silent failures in the codebase"

Claude will:
1. Run FENRIR for fast static analysis
2. Triage findings intelligently (filter false positives)
3. Report prioritized issues

### Slash Command

```
/audit                    # Audit current directory
/audit app/core/          # Audit specific path
/audit --quick            # FENRIR only (fast, no triage)
```

### Standalone Script (CI/CD)

```bash
# FENRIR only (no API needed, instant)
python scripts/audit.py /path/to/project --fenrir-only

# With Claude API triage (requires ANTHROPIC_API_KEY)
python scripts/audit.py /path/to/project

# CI mode (exit 1 if critical issues found)
python scripts/audit.py /path/to/project --ci

# JSON output
python scripts/audit.py /path/to/project --json
```

### Pre-commit Hook

```bash
# Install hook
ln -sf skills/multi-archetype-audit/scripts/pre-commit .git/hooks/pre-commit

# Behavior:
# - MORTEL findings → blocks commit
# - GRAVE findings → warning (allows commit)
# - SUSPECT → info only
```

## The 19 Archetypes

### Core 7 (Greek Mythology)

| Icon | Name | Domain | What It Finds |
|------|------|--------|---------------|
| ⚡ | **HERMES** | API | Endpoint naming, auth gaps, response models |
| ☀️ | **RA** | Performance | Blocking calls, N+1 patterns, cache misses |
| 🔮 | **CASSANDRA** | Warnings | TODOs, FIXMEs, deprecated code |
| 🪨 | **SISYPHUS** | Repetition | DRY violations, duplicate code |
| 🌞 | **ICARUS** | Complexity | God classes, over-abstraction |
| 🍷 | **DIONYSUS** | Robustness | Silent failures, injection risks |
| 🔨 | **HEPHAESTUS** | Build | Unpinned deps, Docker issues |

### Extended 12 (Security, AI, Quality)

| Icon | Name | Domain | What It Finds |
|------|------|--------|---------------|
| 📦 | **PANDORA** | Security | Hardcoded secrets, CORS issues |
| 🔮 | **DELPHI** | AI Safety | Prompt injection, LLM guardrails |
| 💰 | **MIDAS** | LLM Costs | Missing caching, token waste |
| 🌊 | **LETHE** | Data Leakage | Sensitive data in logs, PII |
| 🏔️ | **ANTAEUS** | Resilience | Missing retries, timeouts |
| 👁️ | **TIRESIAS** | Testing | Coverage gaps, weak assertions |
| 📚 | **MENTOR** | Documentation | Missing docstrings, types |
| 🌀 | **PROTEUS** | State | Mutable defaults, globals |
| 🧠 | **MNEMOSYNE** | Context | Correlation IDs, tracing |
| 🧵 | **ARIADNE** | Dependencies | Circular imports, versions |
| 🚪 | **JANUS** | Versioning | API versions, migrations |
| 👁️ | **ARGUS** | Observability | Logging, metrics, health |

### Nordic Hunters (Silent Failure Specialists)

| Icon | Name | Domain | What It Finds |
|------|------|--------|---------------|
| 🐺 | **FENRIR** | Silent Failures | `except: pass`, swallowed errors |
| 🐕 | **GARM** | Zombie Patterns | Dead code that creates problems |

## Severity Levels

| Level | Icon | Meaning |
|-------|------|---------|
| CRITICAL | 🔴 | Security vulnerability - fix immediately |
| HIGH | 🟠 | Significant issue - fix before release |
| MEDIUM | 🟡 | Technical debt - plan to fix |
| LOW | 🟢 | Minor improvement |
| INFO | ⚪ | Informational only |

## How It Works

```
┌─────────────────────────────────────────────────────────┐
│                    AUDIT PIPELINE                        │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  1. FENRIR (Static Analysis)          ~2 seconds         │
│     ├── Regex patterns (19 archetypes)                  │
│     ├── AST analysis (Python)                           │
│     └── Ruff TRY rules (exception handling)             │
│                                                          │
│  2. Claude Code (Intelligent Triage)  ~5 seconds         │
│     ├── Read context (±10 lines per finding)            │
│     ├── Classify: TRUE_POSITIVE / FALSE_POSITIVE        │
│     └── Prioritize by actual risk                       │
│                                                          │
│  3. Report                                               │
│     ├── Stats by severity                               │
│     ├── Actionable findings only                        │
│     └── Markdown or JSON output                         │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## False Positive Handling

Claude Code automatically filters:
- **Example code**: Patterns in docstrings, `example_code` strings
- **Defensive parsing**: AST/JSON parsing with graceful fallback
- **Status functions**: Health checks that intentionally catch all
- **Test fixtures**: Intentionally bad code for testing

## CI/CD Integration

### GitHub Actions

```yaml
name: Code Audit
on: [push, pull_request]

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run FENRIR
        run: python skills/multi-archetype-audit/scripts/audit.py . --fenrir-only --json > fenrir.json

      - name: Claude Triage (optional)
        if: github.event_name == 'pull_request'
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: python skills/multi-archetype-audit/scripts/audit.py . --ci
```

### Pre-commit

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: fenrir
        name: FENRIR Audit
        entry: python skills/multi-archetype-audit/scripts/audit.py
        language: python
        args: [--fenrir-only, --ci]
        types: [python]
```

## Cost

| Mode | Cost | Speed |
|------|------|-------|
| FENRIR only | Free | ~2s |
| + Claude triage | ~$0.02/audit | ~7s |

## License

MIT

## Credits

Inspired by the multi-perspective audit methodology from the Smash Coach AI project.
Archetypes named after figures from Greek mythology and Norse legends.
