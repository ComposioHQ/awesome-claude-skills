---
name: linear
description: Interact with Linear via the linear-cli. Query your work queue, pick up tasks, report progress, close issues with proof.
---

# linear-cli skill

You have access to the `linear` CLI — a Linear task manager built for AI agents. Config lives at `~/.linear-cli/config.json`. Team and API key are pre-configured via `linear setup`.

## When to Use This Skill

- User asks what tasks are assigned to them
- User wants to pick up, update, or close a Linear issue
- User wants to drop a progress comment on an issue
- User wants to create a new issue
- User wants to view team or cycle boards

## Prerequisites

### Install linear-cli

```bash
curl -sSL https://raw.githubusercontent.com/phnx-labs/linear-cli/main/install.sh | bash
```

### Configure

```bash
linear setup
```

Provide your Linear API key (Full access) and team identifier when prompted.

## Core workflow

```
linear tasks                        # your assigned queue in the active cycle
linear tasks --board                # whole team board, grouped by assignee/agent
linear tasks ANT-42                  # detail view for one issue
linear update ANT-42 --pickup        # move to In Progress
linear update ANT-42 --comment "..."  # drop a progress note
linear update ANT-42 --done --proof <url-or-file> --proof "deployed at X"
linear create "Title" --label foo --priority high --description "..."
linear cycles                       # list cycles
```

## Filters

```
linear tasks --status todo         # backlog | todo | progress | done | open
linear tasks --label security      # by any label
linear tasks --cycle next          # active | next
linear tasks --json                # machine-readable
linear tasks --all                 # ignore default agent filter
```

## Output mode for agent use

Always prefer `--json` when parsing output programmatically:

```
linear tasks --json | jq '.issues[] | {id: .identifier, title, state: .state.name}'
```

## Assignee-as-queue model

- `linear tasks` without flags returns issues assigned to the identity that owns the API key.
- If `cfg.agent` is set at setup time (e.g. `claude`, `codex`), `linear tasks` additionally filters by a matching label — the "agent lane" pattern. Override with `--all`.
- `linear update <id> --pickup` = claim the task. Follow with `--done --proof` when shipped.

## Proof-of-completion

`--proof` is repeatable and accepts:
- File paths (uploaded to Linear as attachments)
- URLs (rendered as links)
- Plain text (appended as a line)

Use it on `update --done` so reviewers see evidence without digging.

## Common mistakes

- Don't call the Linear GraphQL API directly — the CLI handles auth, uploads, cycle math, and state resolution.
- Don't hand-edit `~/.linear-cli/config.json` — use `linear setup` to re-configure.
- If you see `Error: Invalid scope: read required`, the API key was created write-only. Regenerate it with Full access at linear.app/settings/account/security.
