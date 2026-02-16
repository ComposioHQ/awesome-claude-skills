---
name: ios-hig-design-guide
description: Build, update, and apply iOS design specifications using Apple Human Interface Guidelines (HIG) source data. Use when a task asks for iOS UI/UX rules, Apple design standards, component behavior, accessibility constraints, interaction patterns, or feature-level design-spec writing grounded in official HIG pages.
---

# iOS HIG Design Guide

Use this skill to produce iOS design recommendations that stay close to official Apple guidance.

## Quick start

1. Sync official sources.
2. Read only relevant sections.
3. Produce a feature-specific spec (not a generic style dump).

Run:

```bash
python3 scripts/sync_apple_hig_sources.py --skill-dir .
```

## Source of truth

- Full raw index with links and abstracts: `references/apple-hig-ios-raw.md`
- Consolidated text dump of all downloaded pages: `references/apple-hig-ios-fulltext.md`
- Curated text dump for iOS spec writing: `references/apple-hig-ios-curated.md`
- Workflow for selecting relevant HIG pages: `references/ios-design-spec-workflow.md`
- Per-page JSON sources: `references/raw/pages/design/human-interface-guidelines/*.json`
- Crawl metadata and fetch status: `references/raw/catalog.json`

## Workflow

### 1) Sync and verify

- Run sync script before answering "latest" or "current" requests.
- Confirm `download_error` is 0 in `references/raw/catalog.json`.
- If errors exist, report failed paths and continue with successfully downloaded pages.

### 2) Narrow scope

- Start from `/design/human-interface-guidelines/designing-for-ios`.
- Add only sections directly related to the requested feature.
- Prioritize foundational constraints (accessibility, layout, typography, color, writing, privacy).
- Prefer `references/apple-hig-ios-curated.md` for day-to-day use; use full dump only when needed.

### 3) Extract constraints

For each selected page, pull concrete rules into implementable statements:

- When to use component/pattern
- Required states (loading, empty, error, destructive confirmation)
- Accessibility behavior (labels, hints, touch target, dynamic type)
- Localization/layout behavior (RTL, truncation, multiline)
- Platform-specific caveats (iOS-only vs cross-platform)

### 4) Produce deliverable

Default output structure:

1. Feature goal and user scenario
2. Information architecture and screen inventory
3. Interaction and state model
4. Component specification
5. Accessibility and localization checklist
6. Open questions and tradeoffs

## Output style rules

- Cite source page paths for each major rule.
- Translate HIG guidance into actionable product decisions.
- Avoid copying large raw passages.
- Mark inferred recommendations explicitly as inference.

## Maintenance

- Re-run sync script whenever Apple updates HIG content.
- Keep generated raw files in `references/`; do not hand-edit generated outputs.
- Update this SKILL.md only for workflow or quality improvements.
