---
title: Use Native Tools for Performance and Control
impact: HIGH
description: Prefer native tools over MCP for faster execution, full control, and modifier support
tags: [tool-router, mcp, integration, providers, performance]
---

# Use Native Tools for Performance and Control

Tool Router supports two approaches: **Native tools (recommended)** for performance and control, or MCP clients for framework independence.

## ❌ Incorrect

```typescript
// DON'T: Use MCP when you need logging, modifiers, or performance
const composio = new Composio(); // No provider
const { mcp } = await composio.create('user_123', {
  toolkits: ['gmail']
});

const client = await createMCPClient({
  transport: { type: 'http', url: mcp.url }
});

// ❌ No control over tool execution
// ❌ No modifier support
// ❌ Extra API calls via MCP server
// ❌ Slower execution
const tools = await client.tools();
```

```python
# DON'T: Use MCP when you need logging, modifiers, or performance
composio = Composio()  # No provider
session = composio.tool_router.create(user_id="user_123")

# ❌ No control over tool execution
# ❌ No modifier support
# ❌ Extra API calls via MCP server
# ❌ Slower execution
```

## ✅ Correct - Use Native Tools (Recommended)

```typescript
// DO: Use native tools for performance and control
import { Composio } from '@composio/core';
import { VercelProvider } from '@composio/vercel';

// Add provider for native tools
const composio = new Composio({
  provider: new VercelProvider()
});

const session = await composio.create('user_123', {
  toolkits: ['gmail', 'slack']
});

// ✅ Direct tool execution (no MCP overhead)
// ✅ Full modifier support
// ✅ Logging and telemetry
// ✅ Faster performance
const tools = await session.tools();
```

```python
# DO: Use native tools for performance and control
from composio import Composio
from composio_openai import OpenAIProvider

# Add provider for native tools
composio = Composio(provider=OpenAIProvider())

session = composio.tool_router.create(
    user_id="user_123",
    toolkits=["gmail", "slack"]
)

# ✅ Direct tool execution (no MCP overhead)
# ✅ Full modifier support
# ✅ Logging and telemetry
# ✅ Faster performance
tools = session.tools()
```

## ✅ Correct - Native Tools with Modifiers

```typescript
// DO: Use modifiers for logging and control
import { Composio } from '@composio/core';
import { VercelProvider } from '@composio/vercel';
import { SessionExecuteMetaModifiers } from '@composio/core';

const composio = new Composio({
  provider: new VercelProvider()
});

const session = await composio.create('user_123', {
  toolkits: ['gmail']
});

// Add modifiers for logging during execution
const modifiers: SessionExecuteMetaModifiers = {
  beforeExecute: ({ toolSlug, sessionId, params }) => {
    console.log(`[${sessionId}] Executing ${toolSlug}`);
    console.log('Parameters:', JSON.stringify(params, null, 2));
    return params;
  },
  afterExecute: ({ toolSlug, sessionId, result }) => {
    console.log(`[${sessionId}] Completed ${toolSlug}`);
    console.log('Success:', result.successful);
    return result;
  }
};

const tools = await session.tools(modifiers);

// Now when agent executes tools, you see:
// [session_abc123] Executing GMAIL_FETCH_EMAILS
// Parameters: { "maxResults": 10, "query": "from:user@example.com" }
// [session_abc123] Completed GMAIL_FETCH_EMAILS
// Success: true
```

```typescript
// Advanced: Add telemetry and schema customization
const advancedModifiers: SessionExecuteMetaModifiers = {
  beforeExecute: ({ toolSlug, sessionId, params }) => {
    // Send to analytics
    analytics.track('tool_execution_started', {
      tool: toolSlug,
      session: sessionId,
      params
    });

    // Validate parameters
    if (!params) {
      throw new Error(`Missing parameters for ${toolSlug}`);
    }

    return params;
  },
  afterExecute: ({ toolSlug, sessionId, result }) => {
    // Track completion and duration
    analytics.track('tool_execution_completed', {
      tool: toolSlug,
      session: sessionId,
      success: result.successful
    });

    // Handle errors
    if (!result.successful) {
      console.error(`Tool ${toolSlug} failed:`, result.error);
    }

    return result;
  },
  modifySchema: ({ toolSlug, schema }) => {
    // Simplify schemas for better AI understanding
    if (toolSlug === 'GMAIL_SEND_EMAIL') {
      // Remove optional fields for simpler usage
      delete schema.parameters.properties.cc;
      delete schema.parameters.properties.bcc;
    }
    return schema;
  }
};
```

```python
# DO: Use modifiers for logging, validation, and telemetry
from composio import Composio
from composio_openai import OpenAIProvider

composio = Composio(provider=OpenAIProvider())

session = composio.tool_router.create(
    user_id="user_123",
    toolkits=["gmail"]
)

# Add modifiers for full control over tool execution
def before_execute(context):
    print(f"[{context['session_id']}] Executing {context['tool_slug']}")
    print(f"Parameters: {context['params']}")
    # Add custom validation, logging, telemetry
    return context['params']

def after_execute(context):
    print(f"[{context['session_id']}] Completed {context['tool_slug']}")
    print(f"Result: {context['result']}")
    # Transform results, handle errors, track metrics
    return context['result']

tools = session.tools(
    modifiers={
        "before_execute": before_execute,
        "after_execute": after_execute
    }
)
```

## Performance Comparison

| Feature | Native Tools | MCP |
|---------|-------------|-----|
| Execution Speed | **Fast** (direct) | Slower (extra HTTP calls) |
| API Overhead | **Minimal** | Additional MCP server roundtrips |
| Modifier Support | **✅ Full support** | ❌ Not available |
| Logging & Telemetry | **✅ beforeExecute/afterExecute** | ❌ Limited visibility |
| Schema Customization | **✅ modifySchema** | ❌ Not available |
| Framework Lock-in | Yes (provider-specific) | No (universal) |

## When to Use Each

### ✅ Use Native Tools (Recommended) When:
- **Performance matters**: Direct execution, no MCP overhead
- **Need logging**: Track tool execution, parameters, results
- **Need control**: Validate inputs, transform outputs, handle errors
- **Production apps**: Telemetry, monitoring, debugging
- **Single framework**: You're committed to one AI framework

### Use MCP Only When:
- **Multiple frameworks**: Switching between Claude, Vercel AI, LangChain
- **Framework flexibility**: Not committed to one provider yet
- **Prototyping**: Quick testing across different AI tools

## Modifier Use Cases

With native tools, modifiers enable:

1. **Logging**: Track every tool execution with parameters and results
2. **Telemetry**: Send metrics to Datadog, New Relic, etc.
3. **Validation**: Check parameters before execution
4. **Error Handling**: Catch and transform errors
5. **Rate Limiting**: Control tool execution frequency
6. **Caching**: Cache results for repeated calls
7. **Schema Customization**: Simplify schemas for specific AI models

## Key Insight

**Native tools eliminate the MCP server middleman**, resulting in faster execution and giving you full control over the tool execution lifecycle. The only trade-off is framework lock-in, which is acceptable in production applications where you've already chosen your AI framework.

## Reference

- [Session Modifiers](https://docs.composio.dev/sdk/typescript/api/tool-router#using-modifiers)
- [SessionExecuteMetaModifiers](https://docs.composio.dev/sdk/typescript/api/tool-router#sessionexecutemetamodifiers-v040)
- [Tool Router Performance](https://docs.composio.dev/sdk/typescript/api/tool-router#best-practices)
