---
title: Configure Tool Router Sessions Properly
impact: MEDIUM
description: Use session configuration options to control toolkit access, tools, and behavior
tags: [tool-router, configuration, toolkits, tools, session]
---

# Configure Tool Router Sessions Properly

Tool Router sessions support rich configuration for fine-grained control over toolkit and tool access.

## ❌ Incorrect

```typescript
// DON'T: Enable all toolkits without restrictions
const session = await composio.create('user_123', {
  // No toolkit restrictions - exposes everything!
});

// DON'T: Mix incompatible configuration patterns
const session = await composio.create('user_123', {
  toolkits: { enable: ['gmail'] },
  toolkits: ['slack']  // This will override the first one!
});
```

```python
# DON'T: Enable all toolkits without restrictions
session = composio.tool_router.create(
    user_id="user_123"
    # No toolkit restrictions - exposes everything!
)
```

## ✅ Correct - Basic Configuration

```typescript
// DO: Explicitly specify toolkits
import { Composio } from '@composio/core';

const composio = new Composio();

// Simple toolkit list
const session = await composio.create('user_123', {
  toolkits: ['gmail', 'slack', 'github']
});

// Explicit enable
const session2 = await composio.create('user_123', {
  toolkits: { enable: ['gmail', 'slack'] }
});

// Disable specific toolkits (enable all others)
const session3 = await composio.create('user_123', {
  toolkits: { disable: ['calendar'] }
});
```

```python
# DO: Explicitly specify toolkits
from composio import Composio

composio = Composio()

# Simple toolkit list
session = composio.tool_router.create(
    user_id="user_123",
    toolkits=["gmail", "slack", "github"]
)

# Explicit enable
session2 = composio.tool_router.create(
    user_id="user_123",
    toolkits={"enable": ["gmail", "slack"]}
)
```

## ✅ Correct - Fine-Grained Tool Control

```typescript
// DO: Control specific tools per toolkit
const session = await composio.create('user_123', {
  toolkits: ['gmail', 'slack'],
  tools: {
    // Only allow reading emails, not sending
    gmail: ['GMAIL_FETCH_EMAILS', 'GMAIL_SEARCH_EMAILS'],

    // Or use enable/disable
    slack: {
      disable: ['SLACK_DELETE_MESSAGE'] // Safety: prevent deletions
    }
  }
});
```

```python
# DO: Control specific tools per toolkit
session = composio.tool_router.create(
    user_id="user_123",
    toolkits=["gmail", "slack"],
    tools={
        # Only allow reading emails, not sending
        "gmail": ["GMAIL_FETCH_EMAILS", "GMAIL_SEARCH_EMAILS"],

        # Or use enable/disable
        "slack": {
            "disable": ["SLACK_DELETE_MESSAGE"]  # Safety: prevent deletions
        }
    }
)
```

## ✅ Correct - Tag-Based Filtering

```typescript
// DO: Use tags to filter by behavior
const session = await composio.create('user_123', {
  toolkits: ['gmail', 'github'],
  // Global tags: only read-only tools
  tags: ['readOnlyHint'],

  // Override tags per toolkit
  tools: {
    github: {
      tags: ['readOnlyHint', 'idempotentHint']
    }
  }
});
```

```python
# DO: Use tags to filter by behavior
session = composio.tool_router.create(
    user_id="user_123",
    toolkits=["gmail", "github"],
    # Global tags: only read-only tools
    tags=["readOnlyHint"],

    # Override tags per toolkit
    tools={
        "github": {
            "tags": ["readOnlyHint", "idempotentHint"]
        }
    }
)
```

## Available Tags

- `readOnlyHint` - Tools that only read data
- `destructiveHint` - Tools that modify or delete data
- `idempotentHint` - Tools safe to retry
- `openWorldHint` - Tools operating in open contexts

## Configuration Best Practices

1. **Least Privilege**: Only enable toolkits/tools needed
2. **Tag Filtering**: Use tags to restrict dangerous operations
3. **Per-Toolkit Tools**: Fine-tune access per toolkit
4. **Auth Configs**: Map toolkits to specific auth configurations

## Reference

- [Configuration Options](https://docs.composio.dev/sdk/typescript/api/tool-router#configuration-options)
- [Tool Tags](https://docs.composio.dev/sdk/typescript/api/tool-router#tags)
