---
title: Fetching Tools for Applications
impact: HIGH
description: Essential patterns for discovering and retrieving tools from Composio for direct execution in traditional applications
tags: [tools, fetch, discovery, apps, providers]
---

# Fetching Tools for Applications

When building traditional applications (non-agent workflows), use direct tool fetching methods to discover and retrieve tools from Composio.

## Methods Overview

- **`tools.get()`** - Use when working with a provider (OpenAI, Vercel, etc.). Returns tools wrapped in provider-specific format.
- **`tools.getRawComposioTools()`** - Use for standalone applications and building UIs. Returns raw tool metadata without provider wrapping.

### 1. tools.get() - For Provider-Based Applications

Use `tools.get()` when you're using Composio with a provider like OpenAI, Vercel AI SDK, or LangChain. This method wraps tools in the format expected by your provider.

**Get tools from a toolkit:**
```typescript
// Get important tools only (auto-applies important filter)
const importantGithubTools = await composio.tools.get('default', {
  toolkits: ['github']
});

// Get a limited number of tools (does NOT auto-apply important filter)
const githubTools = await composio.tools.get('default', {
  toolkits: ['github'],
  limit: 10
});
```

**Get a specific tool by slug:**
```typescript
const tool = await composio.tools.get('default', 'GITHUB_GET_REPO');
```

### 2. tools.getRawComposioTools() - For Standalone Applications & UIs

Use `getRawComposioTools()` for standalone applications and building UIs. This method returns raw tool metadata without provider-specific wrapping, making it ideal for:
- Building tool selection UIs
- Creating tool catalogs or documentation
- Direct tool execution workflows (without providers)
- Custom tool management interfaces

```typescript
// Get important tools (auto-applies important filter)
const importantTools = await composio.tools.getRawComposioTools({
  toolkits: ['github']
});

// Get specific tools by slug
const specificTools = await composio.tools.getRawComposioTools({
  tools: ['GITHUB_GET_REPOS', 'SLACK_SEND_MESSAGE']
});

// Get limited tools (does NOT auto-apply important)
const limitedTools = await composio.tools.getRawComposioTools({
  toolkits: ['slack'],
  limit: 5
});
```

## Important Filter Behavior

The `important` filter auto-applies to show only the most commonly used tools.

**Auto-applies when:**
- Only `toolkits` filter is provided (no other filters)

**Does NOT auto-apply when:**
- `limit` is specified
- `search` is used
- `tools` (specific slugs) are provided
- `tags` are specified
- `important` is explicitly set to `false`

```typescript
// Auto-applies important=true
await composio.tools.get('default', { toolkits: ['github'] });

// Does NOT auto-apply important (limit specified)
await composio.tools.get('default', { toolkits: ['github'], limit: 10 });

// Does NOT auto-apply important (search used)
await composio.tools.get('default', { search: 'repo' });

// Explicitly disable important filter
await composio.tools.get('default', { toolkits: ['github'], important: false });
```

## Filter Parameters

Available filters for both `tools.get()` and `tools.getRawComposioTools()`:

- `toolkits`: Array of toolkit names (e.g., `['github', 'slack']`)
- `tools`: Array of specific tool slugs (e.g., `['GITHUB_GET_REPO']`)
- `search`: Search string for tool names/descriptions
- `limit`: Maximum number of tools to return
- `tags`: Array of tags to filter by
- `scopes`: Array of scopes to filter by
- `authConfigIds`: Array of auth config IDs to filter tools by specific auth configs
- `important`: Boolean to explicitly control important filter (auto-applies in some cases)

**Note:** You cannot use `tools` and `toolkits` filters together.

## Schema Modification

Customize tool schemas at fetch time:

```typescript
const customizedTools = await composio.tools.get('default', {
  toolkits: ['github']
}, {
  modifySchema: ({ toolSlug, toolkitSlug, schema }) => {
    return { ...schema, description: 'Custom description' };
  }
});
```

## Best Practices

1. **Choose the right method:**
   - Use `tools.get()` when working with providers (OpenAI, Vercel, LangChain)
   - Use `tools.getRawComposioTools()` for standalone apps, UIs, and catalogs

2. **Use important filter for UIs**: Show important tools first, then allow users to discover all tools

3. **Cache tool metadata**: Tools don't change frequently, cache the results

4. **Filter by toolkit**: Group tools by toolkit for better organization

5. **Don't mix tools and toolkits filters**: Cannot use both filters together
