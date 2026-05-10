---
name: mac-ai-optimizer
description: Optimize macOS for AI workloads (OpenClaw, Docker, Ollama). Reduce idle memory from 6GB to 2.5GB by disabling background services, reducing UI overhead, configuring Docker limits, and enabling SSH. Turn an 8GB Mac into a lean AI server node.
---

# Mac AI Optimizer

Optimize macOS for AI workloads. Turn an 8GB Mac into a lean AI server node with near-16GB performance for Agent tasks.

## When to Use This Skill

- Running OpenClaw, Ollama, or Docker on a low-memory Mac
- Building a Mac mini AI compute cluster
- Need maximum available RAM for AI Agent workloads
- Docker keeps running out of memory (OOM)

## What This Skill Does

1. **Optimize Memory**: Disable Spotlight, Siri, photo analysis, iCloud sync, analytics — saves ~1.5GB
2. **Reduce UI**: Disable animations, transparency, Dock effects — saves ~400MB
3. **Docker Tuning**: Auto-set CPU/RAM/swap limits based on actual system RAM
4. **SSH Setup**: Enable remote login, output connection info and SSH config snippet
5. **System Report**: Show current memory, CPU, swap, disk, and background service count
6. **Full Optimize**: Run all above in sequence — one command to server-ify a Mac
7. **Revert All**: One command to restore all macOS defaults

## Expected Results (8GB Mac)

| State | Memory Used | Available |
|-------|-------------|-----------|
| Default macOS | ~6GB | ~2GB |
| After optimization | ~2.5GB | ~5.5GB |
| Headless mode | ~1.8GB | ~6.2GB |

## How to Use

```
Optimize this Mac for AI workloads
```

Or run individual tools:
```
Show system resource report
Optimize memory for AI
Reduce UI overhead
Optimize Docker for this Mac
Enable SSH remote access
```

## Install

```
npx skills add dongsheng123132/mac-ai-optimizer
clawhub install mac-ai-optimizer
```

## Examples

- "My Mac only has 8GB RAM, make it run AI better"
- "Turn this Mac mini into an AI server"
- "Reduce memory usage so Docker runs better"
