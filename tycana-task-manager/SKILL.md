---
name: tycana-task-manager
description: Persistent task management and productivity intelligence via MCP. Captures tasks from conversation, plans your day, tracks patterns, and gives personalized recommendations that improve over time.
---

# Tycana Task Manager

Tycana gives Claude persistent memory about your work across conversations. Connect once via MCP, and every session includes your tasks, projects, deadlines, blockers, and computed intelligence from your patterns. No app to open — the conversation is the interface.

## When to Use This Skill

- You want to capture tasks, ideas, and follow-ups without leaving your conversation
- You need your morning planned based on what's actually due and overdue
- You want honest progress reviews that surface slipping work and blocked items
- You need a recommendation for what to work on next, factoring in energy and deadlines
- You want your AI to remember your work context between conversations

## What This Skill Does

1. **Persistent memory** — Tasks, projects, deadlines, notes, and blockers persist across every conversation. Nothing is forgotten between sessions.
2. **Day planning** — Pulls your tasks, factors in what's overdue, considers deadlines, and suggests a prioritized plan calibrated to your actual completion patterns.
3. **Capture in context** — Mention something you need to do mid-conversation and it's captured instantly with effort, energy, and project inferred from context.
4. **Computed intelligence** — Tracks your velocity, detects stalled work, calibrates effort estimates to your actual pace, and surfaces what needs attention. Gets smarter over time.
5. **Progress reviews** — Summarizes what got done, what carried over, what slipped, and patterns worth noting.

## How to Use

### Basic Usage

Tycana connects via MCP. After connecting your account at https://www.tycana.com/getting-started/, the skill activates automatically whenever you discuss tasks, planning, or productivity.

```
"Plan my day"
"Remind me to update the deployment docs before Friday"
"How's the infrastructure project going?"
"What should I work on next? I have about an hour and low energy"
"Review my week"
```

### Advanced Usage

```
"Brain dump — I've got a bunch of things rattling around in my head"
"What's blocking the most work right now?"
"Compare my velocity this week to last week"
"Clean up the completed items in Project X"
```

## Example

**User:** Plan my day — I've got about 6 hours of focus time

**Output:** You've got 5 things due today. The API migration is the big one — that's been sitting for 3 days and it's blocking the staging deploy. I'd start there while you're fresh, then knock out the two quick doc updates after lunch. The design review can probably push to tomorrow if you run out of time — it's not due until Thursday.

## Tips

- Just talk naturally about your work. Tycana captures from conversation context — no special syntax needed.
- Say "what should I work on next?" when you're unsure. It factors in deadlines, energy, and your patterns.
- Mention energy level for better recommendations: "I'm low energy" gets you routine tasks, not deep work.
- Use "review my week" on Fridays to catch slipping work before it becomes a problem.

## Common Use Cases

- Morning planning sessions that account for overdue items and realistic capacity
- Capturing follow-ups during code reviews, meetings, or brainstorming without context switching
- Weekly reviews that surface patterns and stalled projects
- Energy-aware task recommendations throughout the day
- Tracking project progress with awareness of blocking chains and dependencies
