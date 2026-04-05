---
name: ansible-idempotency-check
description: Use when an Ansible role under roles/ has been modified and needs testing for idempotency. Triggers on changed roles detected via git status, test role, verify role, check idempotent.
---

# Ansible Idempotency Check

## Overview

Tests modified Ansible roles for idempotency by running them twice using `ansible localhost -m include_role`. A correct role should produce no changes on the second run.

**Safety warning:** This skill runs roles against the live host -- it will install or modify real software on your machine. Review the role's diff before running.

## When to Use This Skill

- After modifying any role under `roles/`
- When asked to test, verify, or validate a role
- Before committing role changes

## What This Skill Does

1. **Detects changed roles** from `git status`, supporting any `roles/` directory depth (e.g., `roles/docker` or `infra/ansible/roles/nodejs`)
2. **Runs each role once** to apply changes and verify it succeeds
3. **Runs each role a second time** and checks for `CHANGED` output -- any changed tasks indicate non-idempotency
4. **Reports results** per role: success/failure on first run, idempotent or not on second run

## How to Use

### 1. Detect Changed Roles and Roles Directory

Run `git status --short` and extract both the roles directory path and role names from paths matching `<prefix>/roles/<name>/`.

```bash
git status --short | sed -n 's|.* \(.*/\)\{0,1\}roles/\([^/]*\)/.*|\1roles \2|p' | sort -u
```

Example output (the first field is the roles directory, the second is the role name):

- `roles docker` -- roles dir is `roles`, role name is `docker`
- `infra/ansible/roles nodejs` -- roles dir is `infra/ansible/roles`, role name is `nodejs`

Extract the roles directory (all changed roles share the same one):

```bash
roles_dir=$(git status --short | sed -n 's|.* \(.*/\)\{0,1\}roles/[^/]*/.*|\1roles|p' | sort -u | head -1)
```

If `roles_dir` is empty, default to `roles`. This captures all statuses (modified, added, renamed, untracked). Deleted roles are included in the output but should be skipped -- there is nothing to test.

The `ANSIBLE_ROLES_PATH` env var must be set to the detected roles directory so Ansible can find roles by name.

### 2. First Run -- Apply the Role

For each changed role, run it using `include_role`:

```bash
ANSIBLE_ROLES_PATH=./$roles_dir ansible localhost -m include_role -a name=<role-name> -vv
```

Replace `<role-name>` with the actual role name, e.g. `docker`.

**Check the exit code.** If the first run fails (non-zero exit), stop and report the failure. Do not proceed to the second run.

Some roles may require sudo. If you see permission errors, re-run with `--become -K` (or just `--become` if passwordless sudo is configured).

### 3. Second Run -- Check Idempotency

Run the same command again, capturing output:

```bash
output=$(ANSIBLE_ROLES_PATH=./$roles_dir ansible localhost -m include_role -a name=<role-name> -vv 2>&1)
echo "$output"
```

Check idempotency by looking for `CHANGED` in the output:

```bash
echo "$output" | grep -c 'CHANGED'
```

- **Count is 0** -- Role is idempotent. All tasks report `SUCCESS`.
- **Count > 0** -- Role is NOT idempotent. Find which tasks changed:

```bash
echo "$output" | grep 'CHANGED'
```

**Output format reference (`ansible -m include_role` at `-vv`):**

The first result block is always the `include_role` task itself -- it always shows `"changed": false` and can be ignored. Subsequent result blocks are the actual role tasks:

- Unchanged tasks: `localhost | SUCCESS => {"changed": false, ...}`
- Changed tasks: `localhost | CHANGED => {"changed": true, ...}`

## Reporting

For each role tested, report:
- Role name
- First run: success/failure (with error summary if failed)
- Second run: idempotent (no changes) or non-idempotent (list which tasks changed)

## Common Causes of Non-Idempotency

- Using `shell`/`command` modules without `creates`/`removes` guards
- Using `state: latest` with Homebrew, pip, or npm (may re-download or report changed when already at latest)
- File operations without proper `when` conditions
- Missing `changed_when: false` on read-only commands (but audit existing uses -- `changed_when: false` on a task that actually makes changes hides real non-idempotency)

## Example

**User**: "Test the docker role for idempotency"

**Output**:
```
Role: docker
  First run:  SUCCESS (0 failures)
  Second run: IDEMPOTENT (0 changed tasks)
```

**User**: "I modified the nodejs role, verify it"

**Output**:
```
Role: nodejs
  First run:  SUCCESS (0 failures)
  Second run: NOT IDEMPOTENT (2 changed tasks)
    - CHANGED: Install global npm packages
    - CHANGED: Set npm config prefix
```
