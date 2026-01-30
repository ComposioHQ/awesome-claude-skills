---
name: npm-mastery
description: Comprehensive npm workflows for dependency management, security auditing, safe upgrades, publishing, and troubleshooting. Use when working with package.json, node_modules, npm scripts, or resolving dependency issues.
---

# npm Mastery

A comprehensive guide for managing npm dependencies safely and efficiently. This skill covers the most common and critical npm workflows that developers face daily.

## When to Use This Skill

- Upgrading dependencies without breaking the project
- Auditing and fixing security vulnerabilities
- Publishing packages to npm
- Debugging dependency resolution issues
- Managing monorepo workspaces
- Optimizing npm scripts and performance
- Troubleshooting common npm errors

## What This Skill Does

1. **Safe Dependency Upgrades**: Systematic approach to updating packages without breaking changes
2. **Security Auditing**: Finding and fixing vulnerabilities in dependencies
3. **Publishing Workflows**: Proper versioning, changelogs, and npm publish process
4. **Troubleshooting**: Resolving common npm errors and conflicts
5. **Workspace Management**: Monorepo patterns with npm workspaces

## Safe Dependency Upgrades

### Pre-Upgrade Checklist

Before upgrading any dependencies:

```bash
# 1. Ensure clean git state
git status

# 2. Check current outdated packages
npm outdated

# 3. Review what would change
npm outdated --json | jq 'to_entries | map(select(.value.current != .value.wanted))'
```

### Upgrade Strategy by Risk Level

**Low Risk (Patch versions)**
```bash
# Update all patches (1.0.0 -> 1.0.1)
npm update

# Verify nothing broke
npm test
npm run build
```

**Medium Risk (Minor versions)**
```bash
# Check changelogs before upgrading
# Update one package at a time
npm install package-name@latest

# Run full test suite
npm test
npm run lint
npm run build
```

**High Risk (Major versions)**
```bash
# 1. Read migration guide first
# 2. Create dedicated branch
git checkout -b upgrade/package-name-v2

# 3. Install new version
npm install package-name@2

# 4. Check for breaking changes
npm ls package-name

# 5. Run tests, fix issues incrementally
npm test
```

### Interactive Upgrade Tools

```bash
# npm-check-updates: Preview all available updates
npx npm-check-updates

# Update package.json without installing
npx npm-check-updates -u

# Interactive mode for selective updates
npx npm-check-updates -i
```

## Security Auditing

### Quick Audit

```bash
# View vulnerabilities
npm audit

# JSON output for parsing
npm audit --json

# Only show production vulnerabilities
npm audit --omit=dev
```

### Fixing Vulnerabilities

```bash
# Auto-fix where possible (safe)
npm audit fix

# Force fixes (may include breaking changes - review first!)
npm audit fix --force --dry-run  # Preview changes
npm audit fix --force            # Apply changes

# Fix specific package
npm update vulnerable-package
```

### When Auto-Fix Fails

1. **Check if vulnerability is in devDependency** - Lower risk, may be acceptable
2. **Check if vulnerability is exploitable** - Some vulns require specific conditions
3. **Override transitive dependencies**:

```json
{
  "overrides": {
    "vulnerable-package": "^2.0.0"
  }
}
```

4. **Use npm-force-resolutions** for complex cases

### Continuous Security

```bash
# Add to CI pipeline
npm audit --audit-level=high

# Exit codes: 0 = no vulns at level, non-zero = vulns found
```

## Publishing to npm

### Pre-Publish Checklist

```bash
# 1. Ensure tests pass
npm test

# 2. Build if needed
npm run build

# 3. Check what will be published
npm pack --dry-run

# 4. Verify package.json fields
npm pkg get name version main types files
```

### Versioning

```bash
# Bump version (updates package.json and creates git tag)
npm version patch  # 1.0.0 -> 1.0.1 (bug fixes)
npm version minor  # 1.0.0 -> 1.1.0 (new features, backward compatible)
npm version major  # 1.0.0 -> 2.0.0 (breaking changes)

# Preview without making changes
npm version patch --dry-run

# Custom version
npm version 2.0.0-beta.1
```

### Publishing

```bash
# Login (one-time)
npm login

# Publish public package
npm publish

# Publish scoped package publicly
npm publish --access public

# Publish with tag (beta, next, etc.)
npm publish --tag beta
```

### Post-Publish Verification

```bash
# Verify it's live
npm view package-name

# Test install in fresh directory
cd /tmp && mkdir test && cd test
npm init -y
npm install package-name
```

## Troubleshooting Common Issues

### "ERESOLVE unable to resolve dependency tree"

**Cause**: Peer dependency conflicts

**Solutions**:
```bash
# 1. See what's conflicting
npm install --legacy-peer-deps --dry-run

# 2. Option A: Use legacy resolution (quick fix)
npm install --legacy-peer-deps

# 3. Option B: Force (may cause issues)
npm install --force

# 4. Option C: Fix properly with overrides in package.json
{
  "overrides": {
    "conflicting-package": "^version"
  }
}
```

### "ENOENT: no such file or directory"

**Cause**: Corrupted node_modules or cache

**Solutions**:
```bash
# Clean reinstall
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

### "EACCES: permission denied"

**Cause**: npm trying to write to system directories

**Solutions**:
```bash
# Fix npm prefix (recommended)
mkdir ~/.npm-global
npm config set prefix '~/.npm-global'
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc
source ~/.bashrc

# Or use nvm/fnm to manage Node versions (best practice)
```

### "npm ERR! code EINTEGRITY"

**Cause**: Package integrity check failed

**Solutions**:
```bash
# Clear cache and reinstall
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

### Slow Installs

```bash
# Check what's taking time
npm install --timing

# Use faster registry mirror
npm config set registry https://registry.npmmirror.com

# Or switch to pnpm/yarn for faster installs
```

## npm Workspaces (Monorepos)

### Setup

```json
// package.json (root)
{
  "name": "my-monorepo",
  "private": true,
  "workspaces": [
    "packages/*",
    "apps/*"
  ]
}
```

### Common Commands

```bash
# Install all workspace dependencies
npm install

# Run command in specific workspace
npm run build -w packages/core

# Run command in all workspaces
npm run build --workspaces

# Add dependency to specific workspace
npm install lodash -w packages/utils

# Add dependency to root (dev tools)
npm install typescript -D --ignore-scripts
```

### Cross-Workspace Dependencies

```json
// packages/app/package.json
{
  "dependencies": {
    "@myorg/core": "*"  // References workspace package
  }
}
```

## npm Scripts Best Practices

### Script Organization

```json
{
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",

    "test": "vitest",
    "test:ui": "vitest --ui",
    "test:coverage": "vitest --coverage",

    "lint": "eslint . --ext .ts,.tsx",
    "lint:fix": "eslint . --ext .ts,.tsx --fix",

    "typecheck": "tsc --noEmit",

    "validate": "npm run lint && npm run typecheck && npm run test",
    "prepare": "husky install"
  }
}
```

### Pre/Post Hooks

```json
{
  "scripts": {
    "prebuild": "rm -rf dist",
    "build": "tsc",
    "postbuild": "echo 'Build complete!'",

    "preversion": "npm run validate",
    "postversion": "git push && git push --tags"
  }
}
```

### Running Multiple Scripts

```bash
# Sequential (use &&)
npm run lint && npm run test

# Parallel (use npm-run-all or concurrently)
npx npm-run-all --parallel lint test typecheck
```

## Quick Reference

| Task | Command |
|------|---------|
| Check outdated | `npm outdated` |
| Update all (safe) | `npm update` |
| Update to latest | `npx npm-check-updates -i` |
| Security audit | `npm audit` |
| Auto-fix vulns | `npm audit fix` |
| Clean reinstall | `rm -rf node_modules package-lock.json && npm install` |
| See package info | `npm view package-name` |
| Check what's installed | `npm ls package-name` |
| Find duplicates | `npm dedupe` |
| Bump version | `npm version patch/minor/major` |
| Publish | `npm publish` |

## Tips

- Always commit `package-lock.json` - it ensures reproducible builds
- Use `npm ci` in CI/CD for faster, deterministic installs
- Set `engine-strict=true` in `.npmrc` to enforce Node version requirements
- Use `npx` for one-off commands to avoid global installs
- Run `npm doctor` to diagnose common environment issues

## Common Use Cases

- Upgrading React from v17 to v18 with breaking changes
- Fixing critical security vulnerabilities before deployment
- Publishing a TypeScript library with proper type definitions
- Setting up a monorepo with shared dependencies
- Debugging "works on my machine" dependency issues
