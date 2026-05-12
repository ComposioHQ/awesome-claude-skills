---
name: session-continuity
description: Anti-amnesia skill that auto-checkpoints working state to survive context compaction and session restarts. Creates structured state files so Claude resumes with full context instead of starting from scratch.
---

# Session Continuity

Prevents Claude from losing context when sessions restart or context windows compact. Automatically saves decisions, progress, modified files, and next steps to a `.claude/session-state.md` file that Claude reads on resume.

## When to Use This Skill

- Working on multi-step refactors that span multiple sessions
- Before long-running operations that might hit context limits
- When you need to hand off work between Claude sessions
- During complex debugging where you've built up significant context
- Before deployments or test suites that produce large output

## What This Skill Does

1. **Initialize**: Creates a session state file at the start of a work session, capturing the task description and initial plan
2. **Checkpoint**: Saves current progress including decisions made, files modified, problems encountered, and explicit next steps
3. **Resume**: Reads the state file at session start so Claude picks up exactly where it left off
4. **Auto-trigger**: Suggests checkpoints before operations that risk context loss (large refactors, long test runs, deployments)

## How to Use

### Start a Session

```
/session-continuity
```

Claude reads any existing state file and resumes context, or initializes a new session.

### Manual Checkpoint

```
checkpoint
```

Claude writes current progress to the state file. Use this before stepping away or before a risky operation.

### Resume After Restart

Start a new Claude Code session in the same project and run:

```
/session-continuity
```

Claude reads the saved state and knows exactly what was being worked on, what decisions were made, and what to do next.

## Example Workflow

1. Start working on a database migration refactor
2. After 15 messages of analysis and partial implementation, type `checkpoint`
3. Claude saves: "Migrating from Prisma to Drizzle. Completed: schema conversion for User, Post, Comment models. In progress: relation mapping. Next: convert query layer in src/lib/db.ts"
4. Session expires or you close the terminal
5. Next session: `/session-continuity` — Claude reads the checkpoint and continues from the relation mapping step

## State File Format

The state file at `.claude/session-state.md` contains:

- **Task**: What we're working on
- **Decisions**: Key choices made and why
- **Progress**: What's done and what's in progress
- **Modified files**: Files changed in this session
- **Blockers**: Any issues encountered
- **Next steps**: Explicit numbered list of what to do next

## Source Code

[github.com/manja316/claude-session-continuity](https://github.com/manja316/claude-session-continuity) (MIT License)
