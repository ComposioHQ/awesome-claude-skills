---
title: Creating Custom Tools
impact: MEDIUM
description: Build standalone and toolkit-based custom tools with proper authentication and validation
tags: [custom-tools, extensibility, authentication, zod, development]
---

# Creating Custom Tools

Create your own tools that integrate with Composio:
- **Standalone tools** - No external authentication required
- **Toolkit-based tools** - Use toolkit credentials for API requests

## Standalone Tools

For tools that don't need external authentication:

```typescript
import { z } from 'zod';

const tool = await composio.tools.createCustomTool({
  slug: 'CALCULATE_SQUARE',
  name: 'Calculate Square',
  description: 'Calculates the square of a number',
  inputParams: z.object({
    number: z.number().describe('The number to calculate the square of'),
  }),
  execute: async (input) => {
    return {
      data: { result: input.number * input.number },
      error: null,
      successful: true,
    };
  },
});
```

**Use for:** Math, string operations, data transformations, internal logic.

## Toolkit-Based Tools

For tools that call authenticated APIs.

### Using executeToolRequest (Recommended)

Automatically handles authentication and baseURL:

```typescript
const tool = await composio.tools.createCustomTool({
  slug: 'GITHUB_STAR_REPOSITORY',
  name: 'Star GitHub Repository',
  toolkitSlug: 'github',
  description: 'Star a repository under composiohq',
  inputParams: z.object({
    repository: z.string().describe('Repository name'),
    page: z.number().optional().describe('Page number'),
  }),
  execute: async (input, connectionConfig, executeToolRequest) => {
    return await executeToolRequest({
      endpoint: `/user/starred/composiohq/${input.repository}`,
      method: 'PUT',
      parameters: [
        {
          name: 'page',
          value: input.page?.toString() || '1',
          in: 'query', // Adds ?page=1
        },
      ],
    });
  },
});
```

### Using connectionConfig (Direct API Calls)

For custom HTTP requests:

```typescript
const tool = await composio.tools.createCustomTool({
  slug: 'GITHUB_DIRECT_API',
  name: 'Direct GitHub API',
  toolkitSlug: 'github',
  inputParams: z.object({
    repo: z.string().describe('Repository name'),
  }),
  execute: async (input, connectionConfig) => {
    const response = await fetch(`https://api.github.com/repos/${input.repo}`, {
      headers: {
        Authorization: `Bearer ${connectionConfig.val?.access_token}`,
      },
    });

    const data = await response.json();

    return {
      data: data,
      error: response.ok ? null : 'API request failed',
      successful: response.ok,
    };
  },
});
```

## Input Validation with Zod

Define and validate parameters using Zod:

```typescript
inputParams: z.object({
  // Required string
  name: z.string().describe('User name'),

  // Optional with default
  count: z.number().optional().default(10).describe('Number of items'),

  // With validation
  email: z.string().email().describe('Email address'),

  // Enum
  status: z.enum(['active', 'inactive']).describe('Status'),

  // Array
  tags: z.array(z.string()).describe('Tags'),

  // Nested object
  metadata: z.object({
    key: z.string(),
    value: z.string(),
  }).optional().describe('Metadata'),
})
```

**Always use `.describe()`** - helps AI understand parameter purpose.

## Headers and Query Parameters

Add headers and query params via `parameters` array:

```typescript
execute: async (input, connectionConfig, executeToolRequest) => {
  return await executeToolRequest({
    endpoint: '/search/repositories',
    method: 'GET',
    parameters: [
      // Query parameters
      {
        name: 'q',
        value: input.query,
        in: 'query', // ?q=value
      },
      // Headers
      {
        name: 'Accept',
        value: 'application/vnd.github.v3+json',
        in: 'header',
      },
    ],
  });
}
```

## Executing Custom Tools

```typescript
// Standalone tool
await composio.tools.execute('CALCULATE_SQUARE', {
  userId: 'default',
  arguments: { number: 5 },
});

// Toolkit-based tool (uses userId to find account)
await composio.tools.execute('GITHUB_STAR_REPOSITORY', {
  userId: 'user_123',
  arguments: { repository: 'composio' },
});

// With explicit connected account
await composio.tools.execute('GITHUB_STAR_REPOSITORY', {
  userId: 'user_123',
  connectedAccountId: 'conn_abc123',
  arguments: { repository: 'composio' },
});
```

## Error Handling

Always return structured responses:

```typescript
execute: async (input) => {
  try {
    const result = performOperation(input);
    return {
      data: result,
      error: null,
      successful: true,
    };
  } catch (error) {
    return {
      data: null,
      error: error.message,
      successful: false,
    };
  }
}
```

## Key Points

- **Naming:** Use `TOOLKIT_ACTION_DESCRIPTION` format for slugs
- **Prefer executeToolRequest:** Handles auth and baseURL automatically
- **Describe parameters:** AI agents need clear descriptions
- **Not persisted:** Custom tools exist in memory only, recreate on restart
- **Single toolkit scope:** executeToolRequest only works within same toolkit
