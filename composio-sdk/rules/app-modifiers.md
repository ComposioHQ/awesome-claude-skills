---
title: Tool Modifiers
impact: MEDIUM
description: Advanced patterns for customizing tool behavior with schema modifications and execution hooks
tags: [modifiers, hooks, customization, schema, execution]
---

# Tool Modifiers

Modifiers customize tool behavior through schema transformations, pre-execution hooks, and post-execution hooks.

## Schema Modification

Customize tool descriptions or parameters at fetch time:

```typescript
const tools = await composio.tools.get(
  'default',
  { toolkits: ['github'] },
  {
    modifySchema: ({ toolSlug, toolkitSlug, schema }) => {
      // Enhance descriptions for AI
      schema.description = `[Enhanced] ${schema.description}`;

      // Customize specific parameters
      if (toolSlug === 'GITHUB_GET_REPO') {
        schema.inputParameters.properties.owner.description =
          'GitHub organization or user name (e.g., "composio")';
      }

      return schema;
    },
  }
);
```

## Pre-Execution Hooks (beforeExecute)

Modify parameters before execution:

```typescript
const result = await composio.tools.execute(
  'GITHUB_GET_REPO',
  {
    userId: 'default',
    arguments: { owner: 'Composio', repo: 'sdk' },
  },
  {
    beforeExecute: ({ toolSlug, params }) => {
      // Normalize inputs
      params.arguments.owner = params.arguments.owner.toLowerCase();

      // Add defaults
      params.arguments.branch = params.arguments.branch || 'main';

      return params;
    },
  }
);
```

**Common uses:**
- Parameter validation and normalization
- Adding default values
- Logging and tracing

## Post-Execution Hooks (afterExecute)

Transform outputs after execution:

```typescript
const result = await composio.tools.execute(
  'GITHUB_GET_REPO',
  {
    userId: 'default',
    arguments: { owner: 'composio', repo: 'sdk' },
  },
  {
    afterExecute: ({ result }) => {
      if (result.successful) {
        // Remove sensitive data
        delete result.data.token;

        // Add metadata
        result.data.fetchedAt = new Date().toISOString();
      }

      return result;
    },
  }
);
```

**Common uses:**
- Filtering sensitive data
- Data transformation and formatting
- Adding metadata

## Common Patterns

### Sensitive Data Filtering

```typescript
const filterSensitive = ({ result }) => {
  if (result.successful) {
    ['token', 'secret', 'password', 'api_key'].forEach(field => {
      delete result.data[field];
    });
  }
  return result;
};
```

### Logging & Monitoring

```typescript
const monitor = {
  beforeExecute: ({ toolSlug, params }) => {
    console.log(`[START] ${toolSlug}`, params.arguments);
    return params;
  },
  afterExecute: ({ toolSlug, result }) => {
    console.log(`[END] ${toolSlug} - Success: ${result.successful}`);
    return result;
  },
};
```

### Reusable Modifiers

```typescript
const addTimestamps = ({ result }) => {
  if (result.successful) result.data.executedAt = new Date().toISOString();
  return result;
};

// Use in multiple executions
await composio.tools.execute('GITHUB_GET_REPO', { ... }, {
  afterExecute: addTimestamps
});
```

## Key Points

- Schema modifiers apply at fetch time, execution modifiers at runtime
- Always return modified object (don't just mutate)
- Modifiers are synchronous - keep operations lightweight
- Must pass modifiers to each execute() call (not persisted)
