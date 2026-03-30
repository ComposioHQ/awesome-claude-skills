---
name: jarvis-orb
description: Persistent 4-tier AI memory system with temporal scoring, contradiction detection, entity tracking, and real-time desktop visualization via MCP.
---

# Jarvis Orb

A persistent memory layer for AI coding assistants that remembers context across sessions. Provides 4-tier memory (episodic, semantic, project, procedural) with temporal relevance scoring, automatic contradiction detection, and entity relationship tracking. Includes a real-time desktop visualization orb that shows the AI's thinking process.

## When to Use This Skill

- When you need persistent memory across Claude Code sessions
- When working on long-running projects that require context retention
- When you want automatic entity tracking and relationship mapping
- When you need contradiction detection in stored knowledge
- When you want real-time visualization of AI memory operations

## What This Skill Does

1. **4-Tier Memory**: Organizes knowledge into episodic (events), semantic (facts), project (context), and procedural (how-to) tiers
2. **Temporal Scoring**: Automatically ranks memory relevance based on recency, frequency, and importance
3. **Contradiction Detection**: Identifies and resolves conflicting information across memory tiers
4. **Entity Tracking**: Maps relationships between people, projects, decisions, and concepts
5. **Desktop Visualization**: Real-time orb animation showing memory read/write operations

## How to Use

### Setup

**macOS (Apple Silicon) / Linux:**
```bash
curl -fsSL https://raw.githubusercontent.com/TheStack-ai/jarvis-orb/main/install.sh | bash
```

**Windows (PowerShell):**
```powershell
irm https://raw.githubusercontent.com/TheStack-ai/jarvis-orb/main/install.ps1 | iex
```

The installer configures the MCP server and launches the desktop orb automatically.

### Basic Usage

Once configured as an MCP server, Jarvis Orb automatically:
- Stores important context from conversations
- Retrieves relevant memories when needed
- Tracks entities and their relationships
- Displays real-time activity via the desktop orb

## Compatibility

- Claude Code
- Cursor
- Any MCP-compatible AI tool

## Tips

- Start with project-level memory for focused context retention
- Use the visualization orb to monitor memory operations in real-time
- Review contradiction alerts to keep knowledge base consistent

## Common Use Cases

- Multi-session project development with full context retention
- Team knowledge management across AI-assisted workflows
- Long-term decision tracking and rationale preservation
