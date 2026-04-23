---
name: dependency-auditor
description: Multi-ecosystem dependency security auditor with noise filtering, auto-remediation, and license compliance. Runs real audit tools across 7 ecosystems and classifies findings into actionable priority tiers.
---

# Dependency Auditor

Runs real security audit tools (npm audit, pip-audit, cargo audit, govulncheck, bundle-audit) across multiple ecosystems, then classifies findings into four priority tiers so you fix what matters and skip the noise.

## When to Use This Skill

- Before merging a PR that updates dependencies
- During security reviews or compliance checks
- When onboarding to an unfamiliar codebase to assess dependency health
- Before deploying to production
- When checking license compatibility for your project
- In monorepos where phantom dependencies hide between packages

## What This Skill Does

1. **Multi-Ecosystem Audit**: Detects and runs the right audit tool for each ecosystem (Node.js, Python, Rust, Go, Ruby, Java, .NET)
2. **Priority Classification**: Groups findings into four tiers:
   - **Critical-runtime**: Exploitable vulnerabilities in production code paths
   - **Dev-only**: Vulnerabilities in devDependencies that never ship
   - **Transitive-unreachable**: Deep transitive dependencies with no reachable code path
   - **Disputed/withdrawn**: CVEs that were retracted or disputed by maintainers
3. **Auto-Remediation**: Applies safe version bumps for non-breaking upgrades automatically
4. **License Compliance**: Checks all dependencies against your project's license requirements
5. **SBOM Generation**: Creates a Software Bill of Materials for compliance reporting
6. **Monorepo Support**: Detects phantom dependencies (used but not declared) across workspace packages

## How to Use

### Basic Audit

```
audit my deps
```

Claude runs the appropriate audit tools, classifies findings, and presents only actionable items.

### License Check

```
check licenses, we're MIT
```

Claude scans all dependency licenses and flags any that are incompatible with MIT.

### Generate SBOM

```
generate an SBOM for this project
```

Claude creates a structured bill of materials listing all direct and transitive dependencies.

### Full Security Review

```
full security audit — we're deploying to production tomorrow
```

Claude runs audit, checks licenses, identifies phantom dependencies, and provides a go/no-go recommendation.

## Example Output

```
## Dependency Audit Results

### Critical (fix before deploy): 2
- lodash@4.17.15 → Prototype Pollution (CVE-2020-28500) — fix: upgrade to 4.17.21
- express@4.17.1 → Open Redirect (CVE-2024-29041) — fix: upgrade to 4.19.2

### Dev-only (low priority): 5
- jest@27.0.0 has 3 transitive vulns — only in test runner, never ships

### Noise filtered: 12 findings
- 8 transitive-unreachable, 4 disputed/withdrawn

### Auto-fixed: 2
- Applied lodash 4.17.15 → 4.17.21 (non-breaking)
- Applied express 4.17.1 → 4.19.2 (non-breaking)
```

## Source Code

[github.com/manja316/claude-dependency-auditor](https://github.com/manja316/claude-dependency-auditor) (MIT License)
