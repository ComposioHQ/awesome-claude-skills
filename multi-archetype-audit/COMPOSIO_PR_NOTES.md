# PR Notes for ComposioHQ/awesome-claude-skills

## PR #65

**Version**: 4.0.0 (FENRIR 2.0 + Unified NILE Pipeline)

## Key Points

- **FENRIR 2.0**: 6-pass scanner (4776 LOC) with Regex → AST → Ruff → GARM → ORPHEUS
- **20 archetypes** with **45+ detection patterns**
- Unified pipeline: FENRIR → OUROBOROS → RAG → MEMORY → MEMNARCH (opt) → OSIRIS
- Two-stage approach: Static scan + Claude Code intelligent triage
- Score-based verdicts: WORTHY / CURSED / FORBIDDEN
- Zero external dependencies (optional Claude API for CI)

## Category

**Development & Code Tools**

## README Entry

```markdown
- [multi-archetype-audit](./multi-archetype-audit) - Comprehensive code audit using FENRIR 2.0 (6-pass scanner) + Claude Code (intelligent triage). 20 archetypes covering API, Security, AI Safety, Performance, Silent Failures, and Parallel Implementation Blindness. No external LLM required.
```

## PR Description (Updated)

```markdown
# Multi-Archetype Code Audit

**Version**: 4.0.0 (January 2026)

A comprehensive code audit skill with **unified pipeline** and **full NILE integration**:

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

- **20 Archetypes**: Core 7 + Extended 12 + Nordic Hunters (FENRIR, GARM) + Meta (ORPHEUS)
- **45+ Detection Patterns**: Silent failures, zombies, parallel blindness
- **Unified Pipeline**: FENRIR → OUROBOROS → RAG → MEMORY → MEMNARCH → OSIRIS
- **Zero dependencies**: Pure Python + optional Claude API
- **CI/CD ready**: Exit codes, JSON output, pre-commit hook

## The 20 Archetypes

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

### Extended 12 + Nordic Hunters + Meta
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
| 🎭 | ORPHEUS | Parallel Blindness |

### New in V4.0

**GARM Patterns** (Zombie Detection):
- `zombie_subprocess` - Popen without communicate/wait
- `orphan_thread` - Thread without join
- `infinite_loop` - while True without break
- `resource_leak` - open() without context manager
- `async_orphan` - create_task without await

**ORPHEUS Patterns** (Parallel Blindness):
- `versioned_no_deprecation` - `_v2`, `_v3` without DEPRECATED marker
- `parallel_implementations` - Multiple versions of same module
- `orphan_candidate` - Module with 0 imports (potential dead code)

```

## Commit Message

```
feat: update multi-archetype-audit skill to v4.0.0

FENRIR 2.0 + Unified NILE Pipeline:
- 6-pass scanner (4776 LOC): Regex → AST → Ruff → GARM → ORPHEUS
- 20 archetypes (added ORPHEUS for parallel blindness)
- 45+ detection patterns (added GARM zombie patterns)
- Optional MEMNARCH integration (SPO triplets + decisions)
- Unified pipeline: FENRIR → OUROBOROS → RAG → MEMORY → MEMNARCH → OSIRIS

Features:
- Pre-commit hook included
- CI/CD ready with exit codes
- Zero external dependencies
```

## Files to Update

```
multi-archetype-audit/
├── SKILL.md           # Updated skill metadata (V4.0)
├── README.md          # Updated documentation (V4.0)
├── COMPOSIO_PR_NOTES.md # This file
└── scripts/
    ├── audit.py       # Unified audit script
    └── pre-commit     # Pre-commit hook
```

## Dependencies

**None** - Pure Python stdlib. Optional: `anthropic` for Claude API triage in CI/CD.

## Testing Done

- ✅ FENRIR 2.0 scan on 500+ file project - 2.1s
- ✅ GARM detects zombie patterns
- ✅ ORPHEUS detects parallel implementations
- ✅ Claude Code triage - filters false positives
- ✅ Pre-commit hook blocks MORTEL findings
- ✅ CI mode exit codes work correctly
- ✅ JSON output for pipeline integration
