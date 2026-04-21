---
name: concise
description: Chinese-first concise mode. Makes Claude replies shorter and denser without losing technical precision. Use when the user asks for brevity, fewer tokens, or uses the /concise command.
---

# Concise

Chinese-first concise mode for Claude. Makes Claude replies shorter and denser without sacrificing technical accuracy. Two-level compression (expression + content) with automatic relaxation in ambiguous or safety-critical situations.

## When to Use This Skill

- You get annoyed by verbose AI replies with long introductions and recaps
- You work in Chinese where CJK tokens accumulate faster than English
- You want a "be brief" prompt that actually compresses structure, not just wording
- You want compression that auto-relaxes for multi-step, safety, and parameter-heavy cases
- You use `/concise`, `/concise lite`, `/concise ultra`, or say "be brief", "less tokens", "少废话", "简洁模式"

## What This Skill Does

1. **Expression-layer compression**: Removes filler, hedging, transitions ("的其实", "换句话说"), redundant connectors. Prefers sentence fragments over full sentences. Uses direct `X → Y` causal notation. Keeps technical terms verbatim (`API`, `DB`, `auth`, `hook`).

2. **Content-layer compression** (ultra only): Leads with the conclusion. Does not restate the user's instruction as preamble. Expands only when the user asks for analysis, reasoning, or edge cases. File lists default to directory + count.

3. **Automatic clarity relaxation**: Backs off compression for safety warnings, irreversible operations, multi-step procedures where order matters, parameter-heavy explanations, cases where the user has misunderstood, and explicit requests for analysis.

4. **Code and output preservation**: Code blocks, error messages, command output, commit messages, and PR bodies stay in normal formatting. The skill never compresses content that users need verbatim for debugging or copy-paste.

## How to Use

### Basic Usage

In any Claude chat:

```
/concise
```

This enables `ultra` (both layers). To enable only expression compression:

```
/concise lite
```

To turn it off for the current chat:

```
stop concise
```

### Advanced Usage

Install as a default for every new chat across Claude Code, Codex CLI, and Cursor:

```bash
curl -fsSL https://raw.githubusercontent.com/Cpp1022/concise/main/install.sh | sh -s -- --default ultra
```

## Example

**User**: Why does this React component re-render?

**Normal Claude**:
> This component is probably re-rendering because a new object reference is being created on each render, which causes React to treat the prop as changed and trigger an update in the child component.

**Concise ultra**:
> inline obj prop → new ref → re-render. Wrap with `useMemo`.

Same information. About half the tokens. The causal chain is actually easier to see.

## Upstream

Full cross-agent source, installer, FAQ, and Codex `marketplace.json`:
[github.com/Cpp1022/concise](https://github.com/Cpp1022/concise)

MIT licensed, no network calls at runtime, no telemetry.
