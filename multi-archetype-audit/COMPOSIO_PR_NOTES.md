# PR Notes for ComposioHQ/awesome-claude-skills

## PR #65

**Version**: 3.1.0 (FENRIR + Claude Code)

## Key Points

- Two-stage approach: FENRIR (static) + Claude Code (triage)
- ~400 lines, zero external dependencies
- No external LLM required

## Category

**Development & Code Tools**

## README Entry

```markdown
- [multi-archetype-audit](./multi-archetype-audit) - Comprehensive code audit using FENRIR (static analysis) + Claude Code (intelligent triage). 19 archetypes covering API, Security, AI Safety, Performance, and Observability. No external LLM required.
```

## PR Description (Updated)

```markdown
# Multi-Archetype Code Audit

**Version**: 3.0.0 (January 2026)

A comprehensive code audit skill with a two-stage approach:
1. **FENRIR** - Fast static analysis (regex + AST, ~2s)
2. **Claude Code** - Intelligent triage (filters false positives)

**No external LLM required** - Claude Code does the smart work.

## Installation

```bash
cp -r multi-archetype-audit ~/.claude/skills/
```

## Usage

### Interactive
Ask Claude: "Run an audit on app/core/"

### Slash Command
```
/audit [path]       # Full audit
/audit --quick      # FENRIR only (fast)
```

### CI/CD
```bash
python scripts/audit.py . --fenrir-only --ci
```

## Key Features

- **19 Archetypes**: Core 7 + Extended 12 + Nordic Hunters (FENRIR, GARM)
- **Two-stage pipeline**: Static scan → Intelligent triage
- **Zero dependencies**: Pure Python + optional Claude API
- **CI/CD ready**: Exit codes, JSON output, pre-commit hook

## The 19 Archetypes

### Core 7
| Icon | Name | Domain |
|------|------|--------|
| ⚡ | HERMES | API |
| ☀️ | RA | Performance |
| 🔮 | CASSANDRA | Warnings |
| 🪨 | SISYPHUS | DRY |
| 🌞 | ICARUS | Complexity |
| 🍷 | DIONYSUS | Robustness |
| 🔨 | HEPHAESTUS | Build |

### Extended 12 + Nordic Hunters
| Icon | Name | Domain |
|------|------|--------|
| 📦 | PANDORA | Security |
| 🔮 | DELPHI | AI Safety |
| 💰 | MIDAS | LLM Costs |
| 🌊 | LETHE | Data Leakage |
| 🏔️ | ANTAEUS | Resilience |
| 👁️ | TIRESIAS | Testing |
| 📚 | MENTOR | Documentation |
| 🌀 | PROTEUS | State |
| 🧠 | MNEMOSYNE | Context |
| 🧵 | ARIADNE | Dependencies |
| 🚪 | JANUS | Versioning |
| 👁️ | ARGUS | Observability |
| 🐺 | FENRIR | Silent Failures |
| 🐕 | GARM | Zombie Patterns |

```

## Commit Message

```
feat: add multi-archetype-audit skill v3.0.0

Two-stage code audit:
- FENRIR: Fast static analysis (regex + AST)
- Claude Code: Intelligent triage (filters FPs)

Features:
- 19 archetypes (Core 7 + Extended 12 + Nordic Hunters)
- Pre-commit hook included
- CI/CD ready with exit codes
- Zero external dependencies
```

## Files to Update

```
multi-archetype-audit/
├── SKILL.md           # Updated skill metadata
├── README.md          # Updated documentation
└── scripts/
    ├── audit.py       # Simplified audit script (~400 lines)
    └── pre-commit     # New pre-commit hook
```

## Dependencies

**None** - Pure Python stdlib. Optional: `anthropic` for Claude API triage in CI/CD.

## Testing Done

- ✅ FENRIR scan on 500+ file project - 2.1s
- ✅ Claude Code triage - 135 findings → 12 actionable
- ✅ Pre-commit hook blocks MORTEL findings
- ✅ CI mode exit codes work correctly
- ✅ JSON output for pipeline integration
