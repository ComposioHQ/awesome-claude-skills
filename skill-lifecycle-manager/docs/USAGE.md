# Skill Lifecycle Manager - Usage Guide

A comprehensive system for managing the complete lifecycle of Claude Skills from creation through deprecation and archival.

## Features

- **State Machine Management**: Draft → Beta → Stable → Deprecated → Archived
- **Publishing Workflow**: Automated validation and release processes
- **Deprecation Management**: Sunset planning with migration guides
- **Usage Metrics Tracking**: Monitor adoption and performance
- **Lifecycle Reports**: Comprehensive status and health reports

## Quick Start

### Installation

No installation required. The lifecycle manager is a set of Python scripts that work directly with your skills.

```bash
cd skill-lifecycle-manager/scripts
chmod +x *.py
```

### Initialize a New Skill

```bash
./skillctl.py lifecycle init my-new-skill \
  --description "Description of my skill" \
  --author "Your Name"
```

This creates:
- Lifecycle metadata entry
- Initial draft status
- Tracking for future transitions

### Check Skill Status

```bash
./skillctl.py lifecycle status my-skill
```

### Transition Between States

```bash
# Move from draft to beta
./skillctl.py lifecycle transition my-skill beta --reason "Ready for testing"

# Move from beta to stable
./skillctl.py lifecycle transition my-skill stable --reason "Tested and approved"
```

## Publishing Workflow

### Pre-Publish Checks

Before publishing, run validation:

```bash
./skillctl.py publish check my-skill
```

This checks:
- ✅ SKILL.md structure and completeness
- ✅ Required sections present
- ✅ Examples provided
- ✅ Lifecycle status appropriate

### Publish a Skill

```bash
./skillctl.py publish my-skill --version 1.0.0
```

This will:
1. Run all pre-publish checks
2. Update version metadata
3. Generate release notes
4. Record the publish event

### Dry Run

Test without making changes:

```bash
./skillctl.py publish my-skill --version 1.0.0 --dry-run
```

## Deprecation Workflow

### Deprecate a Skill

```bash
./skillctl.py deprecate my-skill \
  --migration-guide "path/to/migration.md" \
  --reason "Replaced by better-skill" \
  --replacement "better-skill" \
  --months-until-eol 6
```

This will:
1. Create a deprecation plan with EOL date
2. Update skill status to deprecated
3. Add deprecation notice to SKILL.md
4. Generate deprecation announcement

### Check Deprecation Status

```bash
./skillctl.py deprecate status my-skill
```

### Check Upcoming EOLs

```bash
./skillctl.py deprecate eol-check --days 30
```

## Usage Metrics

### Record Usage Events

```bash
# Record an invocation
./skillctl.py metrics record my-skill --type invoke --user user123

# Record a completion
./skillctl.py metrics record my-skill --type complete --duration 1500

# Record an error
./skillctl.py metrics record my-skill --type error
```

### Generate Metrics Report

```bash
# Report for all skills (last 30 days)
./skillctl.py metrics report

# Report for specific skill
./skillctl.py metrics report --skill my-skill --days 30
```

### View Trending Skills

```bash
./skillctl.py metrics trending --days 7 --limit 10
```

## Lifecycle Reports

### Full Lifecycle Report

```bash
# Markdown format (default)
./skillctl.py report full --output lifecycle-report.md

# JSON format
./skillctl.py report full --format json --output report.json

# Print to stdout
./skillctl.py report full
```

### Summary Only

```bash
./skillctl.py report summary
```

### Health Metrics

```bash
./skillctl.py report health
```

### Recommendations

```bash
./skillctl.py report recommendations
```

## State Machine

The lifecycle manager enforces valid state transitions:

```
┌─────────┐     ┌─────────┐     ┌─────────┐
│  DRAFT  │────▶│  BETA   │────▶│ STABLE  │
└────┬────┘     └───┬─────┘     └────┬────┘
     │              │                │
     │              ▼                ▼
     │         ┌─────────┐     ┌───────────┐
     └────────▶│ARCHIVED │     │DEPRECATED │
               └─────────┘     └─────┬─────┘
                                     │
                                     ▼
                               ┌───────────┐
                               │ ARCHIVED  │
                               └───────────┘
```

### Valid Transitions

- **DRAFT** → BETA, ARCHIVED
- **BETA** → STABLE, DEPRECATED, DRAFT
- **STABLE** → DEPRECATED
- **DEPRECATED** → ARCHIVED, STABLE
- **ARCHIVED** → (terminal state)

## Validation Requirements

Each status has specific requirements:

| Status | Requirements |
|--------|-------------|
| DRAFT | SKILL.md exists, basic structure |
| BETA | Complete SKILL.md, examples, documentation |
| STABLE | All beta checks + tested + community feedback (3+ ratings) |
| DEPRECATED | Deprecation notice, migration guide |
| ARCHIVED | Archival notice, final backup |

## Data Files

The lifecycle manager creates these tracking files:

- `.skill-lifecycle.json` - Skill metadata and status history
- `.publish-workflow.json` - Publishing history
- `.deprecation-plans.json` - Deprecation plans and EOL dates
- `.metrics/` - Usage metrics data

## Best Practices

1. **Initialize Early**: Create lifecycle entry when starting skill development
2. **Validate Before Transitions**: Always run checks before status changes
3. **Document Changes**: Include reasons for all transitions
4. **Plan Deprecations**: Give users 3-6 months notice before EOL
5. **Monitor Metrics**: Track usage to inform deprecation decisions
6. **Regular Reports**: Generate monthly lifecycle reports

## CLI Reference

### Commands

| Command | Description |
|---------|-------------|
| `lifecycle init` | Initialize a new skill |
| `lifecycle status` | Check skill status |
| `lifecycle transition` | Change skill status |
| `lifecycle list` | List all skills |
| `publish check` | Run pre-publish validation |
| `publish` | Publish a skill |
| `publish notes` | Generate release notes |
| `deprecate` | Deprecate a skill |
| `deprecate status` | Check deprecation status |
| `deprecate eol-check` | List upcoming EOLs |
| `metrics record` | Record usage event |
| `metrics report` | Generate metrics report |
| `metrics trending` | Get trending skills |
| `report full` | Generate full lifecycle report |
| `report summary` | Get summary only |
| `report health` | Get health metrics |
| `report recommendations` | Get actionable recommendations |

## Examples

### Complete Skill Lifecycle

```bash
# 1. Initialize
./skillctl.py lifecycle init payment-processor \
  --description "Process payments via Stripe"

# 2. Develop skill...

# 3. Move to beta
./skillctl.py lifecycle transition payment-processor beta \
  --reason "Core features implemented"

# 4. Test and gather feedback...

# 5. Move to stable
./skillctl.py lifecycle transition payment-processor stable \
  --reason "Tested with 10+ users, positive feedback"

# 6. Publish
./skillctl.py publish payment-processor --version 1.0.0

# 7. Later: Create better version
# 8. Deprecate old version
./skillctl.py deprecate payment-processor \
  --migration-guide "./migrating-to-v2.md" \
  --replacement "payment-processor-v2" \
  --months-until-eol 6

# 9. After EOL, archive
./skillctl.py lifecycle transition payment-processor archived \
  --reason "EOL reached, migration period ended"
```

### Monthly Maintenance

```bash
# Generate health report
./skillctl.py report full --output monthly-report.md

# Check for stale skills
./skillctl.py report health

# Review recommendations
./skillctl.py report recommendations

# Check upcoming EOLs
./skillctl.py deprecate eol-check --days 60
```
