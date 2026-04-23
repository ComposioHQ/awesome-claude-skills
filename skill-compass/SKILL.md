---
name: skill-compass
description: Local-first skill quality evaluator for Claude Code and OpenClaw. Scores skills across six dimensions (Structure, Trigger, Security, Functional, Comparative, Uniqueness), identifies the weakest dimension, suggests targeted fixes, and tracks quality over time.
---

# SkillCompass

A local-first skill quality evaluator that turns "tweak and hope" into a directed improvement loop. Scores skills across six dimensions, identifies the weakest one, suggests targeted fixes, and tracks quality over time.

## When to Use This Skill

- Evaluating a new skill before publishing or sharing
- Finding the weakest dimension in an existing skill to improve it
- Running a security audit on skills that handle sensitive data
- Comparing skill quality across your entire skill library
- Tracking skill quality improvement over successive iterations

## What This Skill Does

1. **Six-Dimension Scoring**: Evaluates skills across Structure, Trigger, Security, Functional, Comparative, and Uniqueness dimensions
2. **Weakest Link Detection**: Identifies the single lowest-scoring dimension so you know exactly what to fix next
3. **Directed Improvement**: Suggests specific fixes for the weakest dimension, not generic advice
4. **Version Tracking**: Records scores over time so you can prove quality improved after each change
5. **Batch Audit**: Evaluates all installed skills at once to spot stale or risky ones
6. **Security Audit**: Dedicated security-focused evaluation for skills handling sensitive operations
## How to Use

### Basic Usage

```
/eval-skill {path-to-skill}
```

Instant quality report showing scores across all six dimensions and what to improve next.

### Dashboard

```
/skillcompass
```

See your overall skill health at a glance.

### Improve the Weakest Dimension

```
/eval-improve {path-to-skill}
```

### Security Audit

```
/eval-security {path-to-skill}
```

### Audit All Skills

```
/eval-audit
```
## Example

**User**: `/eval-skill ./skills/my-custom-skill`

**Output**:
```
SkillCompass Evaluation: my-custom-skill
=========================================
Structure:    8.2 / 10
Trigger:      7.5 / 10
Security:     4.1 / 10  <-- WEAKEST
Functional:   7.8 / 10
Comparative:  6.9 / 10
Uniqueness:   8.0 / 10
-----------------------------------------
Overall:      7.1 / 10

Weakest dimension: Security (4.1)
Top suggestion: Add input validation for user-supplied file paths
                before passing them to shell commands.
```

## Tips

- Run `/eval-skill` after every significant change to a skill to track improvement
- Use `/eval-audit` periodically to catch skills that have gone stale
- The weakest-link approach means you always know the single most impactful thing to fix next
- Works with any skill that follows the SKILL.md convention

## Installation

```bash
npx skills add Evol-ai/SkillCompass
```

Or see the [full installation guide](https://github.com/Evol-ai/SkillCompass#quick-start).

## Common Use Cases

- Quality gate before publishing a skill
- Continuous improvement loop for skill maintainers
- Security review for skills that interact with external services
- Team-wide skill quality visibility
