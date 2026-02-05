---
name: typefix
description: Detect, categorize, and systematically fix TypeScript type errors. Filter by file/folder or scan the entire project. Reports errors by category and file, then fixes them one by one with verification.
---

# TypeScript Type Error Fixer

A systematic pipeline for finding and fixing TypeScript compilation errors. Runs `tsc --noEmit`, categorizes errors, fixes them with minimal changes, and verifies the result — like a dedicated type-safety CI that also fixes what it finds.

## When to Use This Skill

- After a large refactor that introduced type errors
- When upgrading dependencies or TypeScript versions
- After code generation (AI or scaffolding tools) that may have type issues
- When inheriting a codebase with many `as any` casts to clean up
- As a regular maintenance pass on your project

## What This Skill Does

1. **Detect**: Runs `npx tsc --noEmit` and parses all errors
2. **Categorize**: Groups errors by type (missing import, type mismatch, property not found, etc.)
3. **Report**: Shows error counts by category and file (most errors first)
4. **Fix**: Applies minimal, targeted fixes — reads each file before editing
5. **Verify**: Re-runs `tsc` to confirm zero errors in scope
6. **Side-effect check**: Ensures fixes didn't break imports or compatibility elsewhere

## How to Use

### Basic Usage — Fix everything

```
/typefix
```

Scans entire `src/` directory and fixes all TypeScript errors.

### Scoped — Fix specific area

```
/typefix src/features/auth
```

Only fixes errors in files matching the given path pattern.

### After a refactor

```
/typefix orchestrator
```

Fixes errors in any file containing "orchestrator" in its path.

## Example

**User**: `/typefix src/features/sites`

**Output**:

```
## Type Error Report

Total: 8 errors in 4 files

### By Category:
- Type mismatch (TS2322): 3
- Property not found (TS2339): 2
- Cannot find name (TS2304): 2
- Missing module (TS2307): 1

### By File (most errors first):
1. `src/features/sites/lib/site-data.ts` — 3 errors
2. `src/features/sites/components/HeroSection.tsx` — 2 errors
3. `src/features/sites/components/Footer.tsx` — 2 errors
4. `src/features/sites/types.ts` — 1 error

---

## Fix Report

Before: 8 errors
After: 0 errors
Fixed: 8 errors

### Changes:
- `site-data.ts`: Added proper Project type import, removed 3x `as any` casts
- `HeroSection.tsx`: Made `stats` prop optional with fallback
- `Footer.tsx`: Fixed `services` type from `string[]` to `Service[]`
- `types.ts`: Added missing `SitePageData` interface export
```

## Fix Strategies

| Error Type | Strategy |
|------------|----------|
| Missing module/import | Create the file or fix the import path |
| Type mismatch | Compare source and target types, apply proper conversion |
| Property not found | Extend interface/type or add optional chaining |
| Cannot find name | Add import or create definition |
| Unused variable | Remove or prefix with `_` |
| `'use client'` mid-file | Split into separate server/client component files |
| `as any` cleanup | Determine correct type, remove cast |

## Rules

These rules are enforced during fixing:

- **Never** suppress errors with `as any`, `@ts-ignore`, or `@ts-expect-error`
- **Always** read a file before editing it
- **Minimal changes only** — fix the error, don't refactor surrounding code
- **Check import chains** — if you change an export, verify all importers
- **Respect framework rules** — e.g., Next.js `'use client'` must be first line of file

## Tips

- Run `/typefix` after every major refactor or dependency upgrade
- Use scoped mode (`/typefix src/api`) to fix one area at a time in large codebases
- Combine with `/check-build` for a full project health check
- The skill never introduces new errors — it verifies after every fix pass
- Works with any TypeScript project (Next.js, Node, React, etc.)

## Common Use Cases

- Cleaning up AI-generated code that has type issues
- Post-migration type fixes (e.g., Prisma → Drizzle, CJS → ESM)
- Removing all `as any` casts from a codebase
- Fixing errors after `npx payload generate:types` regenerates types
- CI-like type checking before committing
