---
name: skill-lifecycle-manager
description: Comprehensive skill lifecycle management system for managing skill states, publishing workflows, deprecation, and usage metrics tracking.
---

# Skill Lifecycle Manager

A comprehensive system for managing the complete lifecycle of Claude Skills from creation through deprecation and archival. Provides state machine management, automated workflows, and metrics tracking to ensure skills are properly maintained and users are informed of status changes.

## When to Use This Skill

- Managing skill development from draft to production
- Publishing new skills with proper validation
- Deprecating outdated skills with user notifications
- Tracking skill usage and adoption metrics
- Generating lifecycle transition reports
- Archiving discontinued skills

## What This Skill Does

1. **State Machine Management**: Manages skill states (draft → beta → stable → deprecated → archived)
2. **Publishing Workflow**: Validates and publishes skills with proper checks
3. **Deprecation Management**: Handles skill sunsetting with migration guides
4. **Usage Metrics Tracking**: Monitors skill adoption and usage patterns
5. **Lifecycle Reports**: Generates transition and status reports
6. **Automated Notifications**: Alerts users of status changes

## How to Use

### Basic Usage

```
Initialize lifecycle management for skill my-new-skill
```

### Advanced Usage

```
Transition skill from draft to beta, run validation checks, generate usage report for the last 30 days
```

## Example

**User**: "Manage lifecycle for api-documentation-generator skill"

**Output**:
```yaml
Skill: api-documentation-generator
Current Status: draft

Lifecycle Actions Available:
1. Transition to beta (run validation suite)
2. Publish to stable (requires approval)
3. View usage metrics
4. Generate status report

Recommended Next Step: Transition to beta
- Validation passed: 12/12 checks
- Documentation complete
- Examples provided
```

**Inspired by:** npm package lifecycle and Python PEP workflow management

## Tips

- Always validate skills before state transitions
- Provide migration guides when deprecating
- Monitor usage metrics before archiving
- Keep deprecation notices visible for at least 3 months

## Common Use Cases

- New skill development and publishing
- Maintenance mode for stable skills
- End-of-life planning for deprecated skills
- Usage analytics for skill portfolio management
