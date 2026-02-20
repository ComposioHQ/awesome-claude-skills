---
description: Auto-create user-facing changelogs from git commits - transforms technical commits into customer-friendly release notes
argument-hint: Optional version tag, date range, or branch
---

# Changelog Generator

Load the `awesome-claude-skills:changelog-generator` skill and follow its workflow to generate a changelog.

If `$ARGUMENTS` is provided, use it as the version, date range, or branch to generate the changelog for.

Otherwise, analyze recent git history and generate a changelog from the latest commits.
