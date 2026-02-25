---
name: shift-left-reliability
description: Generates OpenSRM reliability manifests, suggests SLOs, and validates dependency contracts during development so reliability decisions happen before deployment — not after incidents.
---

# Shift-Left Reliability

Define service reliability requirements as code using the [OpenSRM](https://github.com/rsionnach/opensrm) (Open Service Reliability Manifest) specification. Generate reliability manifests, suggest appropriate SLOs, validate dependency contracts, and ensure reliability decisions happen during development.

## When to Use This Skill

- Creating a new service or microservice
- Adding reliability requirements to an existing service
- Building AI-powered features that make decisions (AI gates)
- Reviewing code for reliability implications
- Planning deployments and wanting to check error budget
- Defining contracts between services

## What This Skill Does

1. **Generates Manifests**: Creates `service.reliability.yaml` files declaring SLOs, ownership, dependencies, observability, and deployment gates
2. **Suggests SLO Targets**: Recommends availability, latency, and error rate targets based on service tier (critical/high/standard/low)
3. **Validates Dependencies**: Calculates achievable availability from dependency chains and warns when targets are infeasible
4. **Supports AI Gates**: Adds judgment SLOs (reversal rate, high-confidence failure, calibration, feedback latency) for AI decision services
5. **Checks Contracts**: Ensures internal SLO targets are tighter than external contract promises
6. **Covers All Service Types**: Handles api, worker, stream, ai-gate, batch, and database services

## How to Use

### Basic Usage

Ask Claude to generate a reliability manifest for your service:

```
Create a reliability manifest for my payment API service
```

### Advanced Usage

```
Review my service.reliability.yaml and check if my SLO targets are achievable given my dependencies
```

```
Add judgment SLOs to my AI code review bot — it should track reversal rate and high-confidence failures
```

```
What tier should my service be? It processes payments and has 24/7 on-call
```

## Example

**User**: "Create a reliability manifest for a standard API service called user-service owned by the platform team"

**Output**:
```yaml
apiVersion: srm/v1
kind: ServiceReliabilityManifest
metadata:
  name: user-service
  team: platform
  tier: standard
  template: api-standard
spec:
  type: api

  slos:
    availability:
      target: 0.995
      window: 30d
    latency:
      p99: 500ms
      target: 0.99

  ownership:
    team: platform
    slack: "#platform-oncall"
```

**User**: "Add a critical dependency on postgresql and a non-critical one on redis"

**Output**:
```yaml
  dependencies:
    - service: postgresql
      type: database
      critical: true
      expects:
        availability: 0.9995
    - service: redis
      type: cache
      critical: false
```

## Tips

- Start with a template (`api-standard`, `worker-standard`, etc.) and override specific values
- Always set `metadata.team` — it's required by the schema
- Internal SLO targets should be tighter than contract promises to provide margin
- Use `type` on dependencies (`service`, `database`, `cache`, `queue`, `external`) for clarity
- For AI services, start with `reversal_rate` — it requires no ground truth, just tracking overrides
- Validate manifests against the schema: `npx ajv validate -s spec/v1/schema.json -d service.reliability.yaml`

## Common Use Cases

- Generating manifests for new microservices during project scaffolding
- Adding reliability requirements to existing services that lack formal SLOs
- Reviewing whether SLO targets are achievable given dependency availability chains
- Defining AI gate judgment SLOs for code review bots, security scanners, or content moderation
- Setting up deployment gates that block releases when error budgets are exhausted
- Declaring observability requirements (metrics, dashboards, alerts) as code

## References

- [OpenSRM Specification](https://github.com/rsionnach/opensrm) — Full spec, schema, and examples
- [OpenSRM JSON Schema](https://github.com/rsionnach/opensrm/blob/main/spec/v1/schema.json) — For validation tooling
