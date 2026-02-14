---
name: composio
description: Build AI agents and apps with Composio - access 200+ external tools with Tool Router or direct execution
tags: [composio, tool-router, agents, mcp, tools, api, automation]
---

# Composio

Comprehensive guide to building AI agents and applications with Composio. Choose between:
- **Tool Router** - Create isolated, secure MCP sessions for AI agents with automatic authentication
- **Direct Execution** - Build traditional apps with manual tool execution and CRUD operations

## When to use

Use this skill when:

**Building AI Agents:**
- Building chat-based or autonomous agents that need access to external tools (Gmail, Slack, GitHub, etc.)
- Creating multi-user applications with isolated tool access per session
- Implementing automatic authentication flows for external services
- Integrating with AI frameworks (Vercel AI SDK, LangChain, OpenAI Agents, Claude)
- Using MCP (Model Context Protocol) for dynamic tool discovery
- Building event-driven agents with triggers

**Building Traditional Applications:**
- Creating CRUD applications that execute tools directly
- Building automation workflows without agent frameworks
- Managing connected accounts and authentication configurations
- Creating custom tools with specific authentication requirements
- Implementing multi-tenant applications with session isolation
- Building tools with pre/post-execution hooks and modifiers

### 1. Building Agents

Use **Tool Router** to build interactive chat-based agents or autonomous long-running task agents. Tool Router creates isolated MCP sessions for users with scoped access to toolkits and tools.

**Key Features:**
- Session-based isolation per user
- Dynamic toolkit and tool configuration
- Automatic authentication management
- MCP-compatible server URLs for any AI framework
- Connection state querying for UI building
- Real-time event handling with triggers

#### 1.1 Session Management & Configuration

Essential patterns for creating agent sessions and configuring tools:

- [User ID Best Practices](rules/tr-userid-best-practices.md) - Choose user IDs for security and isolation
- [Creating Basic Sessions](rules/tr-session-basic.md) - Initialize Tool Router sessions
- [Session Lifecycle Best Practices](rules/tr-session-lifecycle.md) - When to create new sessions vs reuse
- [Session Configuration](rules/tr-session-config.md) - Configure toolkits, tools, and filters
- [Using Native Tools](rules/tr-mcp-vs-native.md) - Prefer native tools for performance and control
- [Framework Integration](rules/tr-framework-integration.md) - Connect with Vercel AI, LangChain, OpenAI Agents

#### 1.2 Authentication Flows

Authentication patterns for seamless user experiences:

- [Auto Authentication in Chat](rules/tr-auth-auto.md) - Enable in-chat authentication flows
- [Manual Authorization](rules/tr-auth-manual.md) - Use session.authorize() for explicit flows
- [Connection Management](rules/tr-auth-connections.md) - Configure manageConnections, waitForConnections, and custom callback URLs

#### 1.3 Toolkit Querying & UI Building

Build connection UIs and check toolkit states:

- [Building Chat UIs](rules/tr-building-chat-ui.md) - Build chat applications with toolkit selection, connection management, and session handling
- [Query Toolkit States](rules/tr-toolkit-query.md) - Use session.toolkits() to check connections, filter toolkits, and build connection UIs

#### 1.4 Event-Driven Agents (Triggers)

Real-time event handling and webhook integration patterns:

- [Creating Triggers](rules/triggers-create.md) - Set up trigger instances for real-time events
- [Subscribing to Events](rules/triggers-subscribe.md) - Listen to trigger events in real-time
- [Webhook Verification](rules/triggers-webhook.md) - Verify and process incoming webhook payloads
- [Managing Triggers](rules/triggers-manage.md) - Enable, disable, update, and list triggers

### 2. Building Apps with Composio Tools

Use Composio for traditional applications where tools are executed manually without agent frameworks. This approach gives you full control over tool execution, authentication, and resource management.

**Key Capabilities:**
- Direct tool execution with manual control
- CRUD operations on connected accounts, auth configs, and toolkits
- Custom tool creation with authentication
- Session isolation for multi-tenant apps
- Pre/post-execution hooks and modifiers
- Event-driven workflows with triggers

#### 2.1 Core Operations

Fundamental patterns for fetching and executing tools:

- [Fetching Tools](rules/app-fetch-tools.md) - Get tools with filters and search
- [Direct Tool Execution](rules/app-execute-tools.md) - Execute tools manually with parameters
- [Tool Version Management](rules/app-tool-versions.md) - Version pinning strategies for stability

#### 2.2 Resource Management (CRUD Patterns)

Manage authentication and connections programmatically:

- [Connected Accounts CRUD](rules/app-connected-accounts.md) - Create, read, update, delete connected accounts
- [Auth Config Management](rules/app-auth-configs.md) - Manage authentication configurations
- [Toolkit Management](rules/app-toolkits.md) - Query toolkits, categories, and auth requirements

#### 2.3 Extensibility & Customization

Extend Composio with custom tools and behavior:

- [Creating Custom Tools](rules/app-custom-tools.md) - Build standalone and toolkit-based tools
- [Tool Modifiers](rules/app-modifiers.md) - Schema modification and execution hooks

#### 2.4 Event-Driven Applications

Build reactive applications with triggers (shared with agents):

- [Creating Triggers](rules/triggers-create.md) - Set up trigger instances for real-time events
- [Subscribing to Events](rules/triggers-subscribe.md) - Listen to trigger events in real-time
- [Webhook Verification](rules/triggers-webhook.md) - Verify and process incoming webhooks
- [Managing Triggers](rules/triggers-manage.md) - Enable, disable, update, and list triggers

#### 2.5 User Context & Multi-Tenancy

Manage user context and multi-tenant isolation:

- [User ID Patterns](rules/app-user-context.md) - User vs organization IDs, shared vs isolated connections

## Quick Start Examples

### Building an Agent with Tool Router

```typescript
import { Composio } from '@composio/core';

const composio = new Composio();

// Create a session with Gmail tools
const session = await composio.create('user_123', {
  toolkits: ['gmail'],
  manageConnections: true
});

// Use MCP URL with any AI framework
console.log('MCP URL:', session.mcp.url);
```

### Building an App with Direct Execution

```typescript
import { Composio } from '@composio/core';

const composio = new Composio({
  apiKey: 'your-api-key',
  toolkitVersions: { github: '12082025_00' }
});

// Fetch tools
const tools = await composio.tools.get('user_123', {
  toolkits: ['github']
});

// Execute a tool
const result = await composio.tools.execute('GITHUB_GET_REPO', {
  userId: 'user_123',
  arguments: { owner: 'composio', repo: 'sdk' },
});

console.log(result.data);
```

## References

**Tool Router (Agents):**
- [Tool Router Docs](https://docs.composio.dev/sdk/typescript/api/tool-router)
- [MCP Protocol](https://modelcontextprotocol.io)
- [Framework Integration Examples](https://github.com/composiohq/composio/tree/main/ts/examples/tool-router)

**Direct Execution (Apps):**
- [Tools API](https://docs.composio.dev/sdk/typescript/api/tools)
- [Connected Accounts API](https://docs.composio.dev/sdk/typescript/api/connected-accounts)
- [Auth Configs API](https://docs.composio.dev/sdk/typescript/api/auth-configs)
- [Toolkits API](https://docs.composio.dev/sdk/typescript/api/toolkits)
- [Custom Tools Guide](https://docs.composio.dev/sdk/typescript/api/custom-tools)
- [Modifiers](https://docs.composio.dev/sdk/typescript/advanced/modifiers)
- [Core Concepts](https://docs.composio.dev/sdk/typescript/core-concepts)

**Shared:**
- [Triggers API](https://docs.composio.dev/sdk/typescript/api/triggers)
- [Webhook Verification](https://docs.composio.dev/sdk/typescript/advanced/webhook-verification)
