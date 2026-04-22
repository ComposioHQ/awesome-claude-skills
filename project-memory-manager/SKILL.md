---
name: project-memory-manager
description: Manages persistent project memory for AI coding agents using MemClaw. Creates isolated memory workspaces per project so context never bleeds between codebases, and lets you review what your agent remembers via a web dashboard.
---

# Project Memory Manager

This skill gives your AI coding agent a persistent, project-isolated memory system. Instead of losing context between sessions or mixing up details from different projects, each project gets its own memory workspace that persists across sessions and can be shared with teammates.

Powered by [MemClaw](https://memclaw.me) ([GitHub](https://github.com/Felo-Inc/memclaw)).

## When to Use This Skill

- You work on multiple projects and your agent keeps mixing up context
- You want your agent to remember architecture decisions, conventions, and progress across sessions
- You're collaborating with teammates and need shared project context
- You want to review and manage what your AI agent remembers about each project
- You're switching between clients and need strict context isolation

## What This Skill Does

1. **Creates Isolated Workspaces**: Each project gets its own persistent memory workspace — Client A's context never touches Client B's
2. **Maintains Project Memory**: Automatically tracks tasks, saves artifacts, and maintains a living project README with background, preferences, and progress
3. **Enables Cross-Session Recall**: Load any workspace and pick up exactly where you left off, even days later
4. **Supports Team Collaboration**: Invite teammates to shared project workspaces so everyone has the same context
5. **Provides Visual Dashboard**: Review, edit, and manage all project memories at memclaw.me

## How to Use

### Basic Usage

```
Create a workspace called "client-acme"
```

```
Open the acme workspace
```

```
What's in my workspace?
```

```
Save that architecture report to the workspace
```

### Advanced Usage

```
List all my project workspaces
```

```
Search the acme workspace for the database schema decision we made last week
```

```
Switch to the mobile-app project and show me the current progress
```

```
Refresh the workspace to sync changes from my teammate
```

## Example

**User**: "I'm starting work on a new client project for Acme Corp. Create a workspace for it."

**Output**:
```
Project 'client-acme' created.
https://felo.ai/livedoc/abc123?from=claw

You can now:
- Work naturally and I'll track tasks and save important artifacts
- Ask me to save reports, documents, or research to the workspace
- View everything on the web dashboard
- Share the workspace with teammates
```

**User** (next day, new session): "Open the acme workspace"

**Output**:
```
Project 'client-acme' loaded. Here's what we have:

## What This Project Is
Client project for Acme Corp — B2B SaaS integration work

## Current Progress
- Completed initial architecture review
- Database schema finalized (PostgreSQL)
- API endpoints documented in workspace
Last updated: 2026-04-14

3 artifacts saved, 5 tasks tracked.
```

## Tips

- Start by creating a workspace when you begin any new project — the earlier the agent starts building memory, the more useful it becomes
- The agent updates the project README automatically as it learns about your preferences and progress
- Use the web dashboard at memclaw.me to review what your agent remembers and make corrections
- When collaborating, shared workspaces are read-only for teammates to prevent accidental overwrites
- Workspaces are identified by name, so use clear, descriptive names like "client-acme" or "mobile-app-v2"

## Installation

Get your API key from [felo.ai](https://felo.ai/settings/api-keys), then:

```bash
export FELO_API_KEY="your-api-key-here"
```

### Claude Code
```bash
/plugin marketplace add Felo-Inc/memclaw
/plugin install memclaw@memclaw
```

### Manual
```bash
git clone https://github.com/Felo-Inc/memclaw.git
cp -r memclaw/memclaw ~/.claude/skills/
```

## Common Use Cases

- **Multi-client consulting**: Keep each client's context completely separate
- **Multi-repo development**: Each repo gets its own workspace with architecture notes, constraints, and TODOs
- **Research projects**: Accumulate papers, insights, and notes into project-specific knowledge bases
- **Team handoffs**: Share workspace so a colleague can pick up where you left off with full context
