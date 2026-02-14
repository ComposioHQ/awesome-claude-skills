---
title: Direct Tool Execution for Applications
impact: HIGH
description: Core patterns for manually executing Composio tools in traditional applications without agent frameworks
tags: [tools, execute, execution, apps, manual]
---

# Direct Tool Execution for Applications

When building traditional applications without agent frameworks, use `composio.tools.execute()` to manually execute tools.

## Basic Execution

```typescript
// Execute with a specific version (REQUIRED)
const result = await composio.tools.execute('GITHUB_GET_ISSUES', {
  userId: 'default',
  arguments: { owner: 'composio', repo: 'sdk' },
  version: '12082025_00', // Specific version required
});
```

## Version Management

**CRITICAL**: When manually executing tools (especially in workflows), a **specific version is required**. Using `'latest'` will throw an error.

**Why version pinning is required:**
- Tool argument schemas can change between versions
- Using `'latest'` in workflows can cause runtime errors when tools are updated
- Pinned versions ensure workflow stability and predictability
- Version validation prevents production issues from schema mismatches

See [Tool Version Management](app-tool-versions.md) for detailed version strategies.

## Parameters

### ExecuteParams Object

```typescript
{
  userId: string,           // User ID for connected account lookup
  arguments: object,        // Tool-specific input parameters
  version?: string,         // Toolkit version (required for manual execution)
  dangerouslySkipVersionCheck?: boolean  // Bypass version validation (NOT recommended)
}
```

### Execution Modifiers

Transform requests and responses with modifiers:

```typescript
const result = await composio.tools.execute(
  'GITHUB_GET_ISSUES',
  {
    userId: 'default',
    arguments: { owner: 'composio', repo: 'sdk' },
    version: '12082025_00',
  },
  {
    beforeExecute: ({ toolSlug, toolkitSlug, params }) => {
      // Modify params before execution
      console.log('Executing:', toolSlug);
      return {
        ...params,
        arguments: {
          ...params.arguments,
          per_page: 100 // Add default parameter
        }
      };
    },
    afterExecute: ({ toolSlug, toolkitSlug, result }) => {
      // Transform result after execution
      console.log('Completed:', toolSlug);
      return {
        ...result,
        timestamp: new Date().toISOString()
      };
    },
  }
);
```

## Response Format

```typescript
interface ToolExecuteResponse {
  data: any;           // Tool-specific response data
  error: string | null;  // Error message if execution failed
  successful: boolean;   // Whether execution succeeded
}
```

## Error Handling

```typescript
try {
  const result = await composio.tools.execute('GITHUB_GET_ISSUES', {
    userId: 'user_123',
    arguments: { owner: 'composio', repo: 'sdk' },
    version: '12082025_00',
  });

  if (!result.successful) {
    console.error('Tool execution failed:', result.error);
    // Handle error case
    return;
  }

  // Process successful result
  console.log('Issues:', result.data);
} catch (error) {
  if (error.name === 'ComposioToolNotFoundError') {
    console.error('Tool not found');
  } else if (error.name === 'ComposioToolExecutionError') {
    console.error('Execution error:', error.message);
  } else {
    console.error('Unexpected error:', error);
  }
}
```

## Common Error Types

- `ComposioCustomToolsNotInitializedError`: Custom tools instance not initialized
- `ComposioToolNotFoundError`: Tool with the given slug not found
- `ComposioToolExecutionError`: Error during tool execution
- Version validation errors: Thrown when version is missing or `'latest'` is used

## Best Practices

1. **Always specify versions**: Use explicit versions or configure at initialization
2. **Handle errors gracefully**: Check `successful` flag and handle `error` field
3. **Validate arguments**: Ensure all required parameters are provided
4. **Use modifiers sparingly**: Only add modifiers when necessary for transformation
5. **Log execution details**: Track which tools are executed for debugging
6. **Test with real data**: Validate execution with actual connected accounts
7. **Handle authentication errors**: User may not have connected account for toolkit

## Common Patterns

### Execute with retry logic

```typescript
async function executeWithRetry(slug, params, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      const result = await composio.tools.execute(slug, params);
      if (result.successful) return result;

      console.log(`Retry ${i + 1}/${maxRetries}`);
      await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)));
    } catch (error) {
      if (i === maxRetries - 1) throw error;
    }
  }
}
```

### Execute multiple tools in sequence

```typescript
async function executeWorkflow(userId) {
  // Step 1: Get repository
  const repo = await composio.tools.execute('GITHUB_GET_REPO', {
    userId,
    arguments: { owner: 'composio', repo: 'sdk' },
    version: '12082025_00',
  });

  if (!repo.successful) {
    throw new Error(`Failed to get repo: ${repo.error}`);
  }

  // Step 2: Create issue using data from step 1
  const issue = await composio.tools.execute('GITHUB_CREATE_ISSUE', {
    userId,
    arguments: {
      owner: 'composio',
      repo: 'sdk',
      title: `Update for ${repo.data.name}`,
      body: 'Automated issue creation'
    },
    version: '12082025_00',
  });

  return { repo: repo.data, issue: issue.data };
}
```

### Execute with parameter validation

```typescript
async function sendSlackMessage(userId, channel, text) {
  // Validate inputs
  if (!channel.startsWith('#')) {
    throw new Error('Channel must start with #');
  }
  if (text.length > 4000) {
    throw new Error('Message too long');
  }

  const result = await composio.tools.execute('SLACK_SEND_MESSAGE', {
    userId,
    arguments: { channel, text },
    version: '10082025_01',
  });

  return result;
}
```
