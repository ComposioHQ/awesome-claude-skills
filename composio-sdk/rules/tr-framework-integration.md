---
title: Integrate Tool Router with AI Frameworks
impact: HIGH
description: Connect Tool Router sessions with popular AI frameworks using MCP or native tools
tags: [tool-router, frameworks, integration, vercel, openai, langchain, claude, crewai]
---

# Integrate Tool Router with AI Frameworks

Tool Router works with any AI framework through two methods: **Native Tools** (recommended for speed) or **MCP** (for framework flexibility). Choose native tools when available for better performance and control.

## Integration Methods

| Method | Pros | Cons | When to Use |
|--------|------|------|-------------|
| **Native Tools** | ✅ Faster execution<br>✅ Full control with modifiers<br>✅ No MCP overhead | ❌ Framework lock-in | Single framework, production apps |
| **MCP** | ✅ Framework independent<br>✅ Works with any MCP client<br>✅ Easy framework switching | ⚠️ Slower (extra API roundtrip)<br>⚠️ Less control | Multi-framework, prototyping |

## MCP Headers Configuration

When using MCP, the `session.mcp.headers` object contains the authentication headers required to connect to the Composio MCP server:

```typescript
{
  "x-api-key": "your_composio_api_key"
}
```

### Using with MCP Clients

When configuring MCP clients (like Claude Desktop), you need to provide the Composio API key in the headers:

```json
{
  "mcpServers": {
    "composio": {
      "type": "http",
      "url": "https://mcp.composio.dev/session/your_session_id",
      "headers": {
        "x-api-key": "your_composio_api_key"
      }
    }
  }
}
```

**Where to find your Composio API key:**
- Login to [Composio Platform](https://platform.composio.dev)
- Select your project
- Navigate to Settings to find your API keys
- Or set it via environment variable: `COMPOSIO_API_KEY`

When using Tool Router sessions programmatically, the headers are automatically included in `session.mcp.headers`.

## ❌ Incorrect - Using Tools Without Tool Router

```typescript
// DON'T: Use tools directly without session isolation
import { Composio } from '@composio/core';
import { VercelProvider } from '@composio/vercel';

const composio = new Composio({ provider: new VercelProvider() });

// ❌ No user isolation
// ❌ Tools not scoped per user
// ❌ All users share same tools
const tools = await composio.tools.get('default', {
  toolkits: ['gmail']
});
```

```python
# DON'T: Use tools directly without session isolation
from composio import Composio
from composio_openai_agents import OpenAIAgentsProvider

composio = Composio(provider=OpenAIAgentsProvider())

# ❌ No user isolation
# ❌ Tools not scoped per user
# ❌ All users share same tools
tools = composio.tools.get(
    user_id="default",
    toolkits=["gmail"]
)
```

## ✅ Correct - Vercel AI SDK (Native Tools)

```typescript
// DO: Use Tool Router with native tools for best performance
import { openai } from '@ai-sdk/openai';
import { Composio } from '@composio/core';
import { VercelProvider } from '@composio/vercel';
import { streamText } from 'ai';

// Initialize Composio with Vercel provider
const composio = new Composio({
  provider: new VercelProvider()
});

async function runAgent(userId: string, prompt: string) {
  // Create isolated session for user
  const session = await composio.create(userId, {
    toolkits: ['gmail'],
    manageConnections: true
  });

  // Get native Vercel-formatted tools
  const tools = await session.tools();

  // Stream response with tools
  const stream = await streamText({
    model: openai('gpt-4o'),
    prompt,
    tools,
    maxSteps: 10
  });

  // ✅ Fast execution (no MCP overhead)
  // ✅ User-isolated tools
  // ✅ Native Vercel format

  for await (const textPart of stream.textStream) {
    process.stdout.write(textPart);
  }
}

await runAgent('user_123', 'Fetch my last email from Gmail');
```

```python
# DO: Use Tool Router with native tools for best performance
from composio import Composio
from composio_vercel import VercelProvider
from ai import streamText, openai

# Initialize Composio with Vercel provider
composio = Composio(provider=VercelProvider())

async def run_agent(user_id: str, prompt: str):
    # Create isolated session for user
    session = composio.create(
        user_id=user_id,
        toolkits=["gmail"],
        manage_connections=True
    )

    # Get native Vercel-formatted tools
    tools = session.tools()

    # Stream response with tools
    stream = streamText(
        model=openai("gpt-4o"),
        prompt=prompt,
        tools=tools,
        max_steps=10
    )

    # ✅ Fast execution (no MCP overhead)
    # ✅ User-isolated tools
    # ✅ Native Vercel format

    async for text_part in stream.text_stream:
        print(text_part, end="")

await run_agent("user_123", "Fetch my last email from Gmail")
```

## ✅ Correct - Vercel AI SDK (MCP)

```typescript
// DO: Use MCP when framework flexibility is needed
import { openai } from '@ai-sdk/openai';
import { experimental_createMCPClient as createMCPClient } from '@ai-sdk/mcp';
import { Composio } from '@composio/core';
import { streamText } from 'ai';

const composio = new Composio();

async function runAgentMCP(userId: string, prompt: string) {
  // Create session (MCP URL only, no provider needed)
  const session = await composio.create(userId, {
    toolkits: ['gmail'],
    manageConnections: true
  });

  // Create MCP client
  const client = await createMCPClient({
    transport: {
      type: 'http',
      url: session.mcp.url,
      headers: session.mcp.headers
    }
  });

  // Get tools from MCP server
  const tools = await client.tools();

  // Stream response
  const stream = await streamText({
    model: openai('gpt-4o'),
    prompt,
    tools,
    maxSteps: 10
  });

  // ✅ Framework independent
  // ✅ User-isolated tools
  // ⚠️ Slower (MCP overhead)

  for await (const textPart of stream.textStream) {
    process.stdout.write(textPart);
  }
}

await runAgentMCP('user_123', 'Fetch my last email');
```

## ✅ Correct - OpenAI Agents SDK (Native Tools)

```typescript
// DO: Use native tools with OpenAI Agents
import { Composio } from '@composio/core';
import { OpenAIAgentsProvider } from '@composio/openai-agents';
import { Agent, run } from '@openai/agents';

const composio = new Composio({
  provider: new OpenAIAgentsProvider()
});

async function createAssistant(userId: string) {
  // Create session with native tools
  const session = await composio.create(userId, {
    toolkits: ['gmail', 'slack']
  });

  // Get native OpenAI Agents formatted tools
  const tools = await session.tools();

  // Create agent with tools
  const agent = new Agent({
    name: 'Personal Assistant',
    model: 'gpt-4o',
    instructions: 'You are a helpful assistant. Use tools to help users.',
    tools
  });

  // ✅ Fast execution
  // ✅ Native OpenAI Agents format
  // ✅ Full control

  return agent;
}

const agent = await createAssistant('user_123');
const result = await run(agent, 'Check my emails and send a summary to Slack');
console.log(result.finalOutput);
```

```python
# DO: Use native tools with OpenAI Agents
from composio import Composio
from composio_openai_agents import OpenAIAgentsProvider
from agents import Agent, Runner

composio = Composio(provider=OpenAIAgentsProvider())

async def create_assistant(user_id: str):
    # Create session with native tools
    session = composio.create(
        user_id=user_id,
        toolkits=["gmail", "slack"]
    )

    # Get native OpenAI Agents formatted tools
    tools = session.tools()

    # Create agent with tools
    agent = Agent(
        name="Personal Assistant",
        model="gpt-4o",
        instructions="You are a helpful assistant. Use tools to help users.",
        tools=tools
    )

    # ✅ Fast execution
    # ✅ Native OpenAI Agents format
    # ✅ Full control

    return agent

agent = await create_assistant("user_123")
result = await Runner.run(
    starting_agent=agent,
    input="Check my emails and send a summary to Slack"
)
print(result.final_output)
```

## ✅ Correct - OpenAI Agents SDK (MCP)

```typescript
// DO: Use MCP with OpenAI Agents for flexibility
import { Composio } from '@composio/core';
import { Agent, run, hostedMcpTool } from '@openai/agents';

const composio = new Composio();

async function createAssistantMCP(userId: string) {
  // Create session
  const { mcp } = await composio.create(userId, {
    toolkits: ['gmail']
  });

  // Create agent with MCP tool
  const agent = new Agent({
    name: 'Gmail Assistant',
    model: 'gpt-4o',
    instructions: 'Help users manage their Gmail.',
    tools: [
      hostedMcpTool({
        serverLabel: 'composio',
        serverUrl: mcp.url,
        headers: mcp.headers
      })
    ]
  });

  // ✅ Framework independent
  // ⚠️ Slower execution

  return agent;
}

const agent = await createAssistantMCP('user_123');
const result = await run(agent, 'Fetch my last email');
```

```python
# DO: Use MCP with OpenAI Agents for flexibility
from composio import Composio
from agents import Agent, Runner, HostedMCPTool

composio = Composio()

def create_assistant_mcp(user_id: str):
    # Create session
    session = composio.create(user_id=user_id, toolkits=["gmail"])

    # Create agent with MCP tool
    composio_mcp = HostedMCPTool(
        tool_config={
            "type": "mcp",
            "server_label": "composio",
            "server_url": session.mcp.url,
            "require_approval": "never",
            "headers": session.mcp.headers
        }
    )

    agent = Agent(
        name="Gmail Assistant",
        instructions="Help users manage their Gmail.",
        tools=[composio_mcp]
    )

    # ✅ Framework independent
    # ⚠️ Slower execution

    return agent

agent = create_assistant_mcp("user_123")
result = Runner.run_sync(starting_agent=agent, input="Fetch my last email")
print(result.final_output)
```

## ✅ Correct - LangChain (MCP)

```typescript
// DO: Use LangChain with MCP
import { MultiServerMCPClient } from '@langchain/mcp-adapters';
import { ChatOpenAI } from '@langchain/openai';
import { createAgent } from 'langchain';
import { Composio } from '@composio/core';

const composio = new Composio();

async function createLangChainAgent(userId: string) {
  // Create session
  const session = await composio.create(userId, {
    toolkits: ['gmail']
  });

  // Create MCP client
  const client = new MultiServerMCPClient({
    composio: {
      transport: 'http',
      url: session.mcp.url,
      headers: session.mcp.headers
    }
  });

  // Get tools
  const tools = await client.getTools();

  // Create agent
  const llm = new ChatOpenAI({ model: 'gpt-4o' });

  const agent = createAgent({
    name: 'Gmail Assistant',
    systemPrompt: 'You help users manage their Gmail.',
    model: llm,
    tools
  });

  return agent;
}

const agent = await createLangChainAgent('user_123');
const result = await agent.invoke({
  messages: [{ role: 'user', content: 'Fetch my last email' }]
});
console.log(result);
```

```python
# DO: Use LangChain with MCP
from composio import Composio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from langchain_openai.chat_models import ChatOpenAI

composio = Composio()

async def create_langchain_agent(user_id: str):
    # Create session
    session = composio.create(user_id=user_id, toolkits=["gmail"])

    # Create MCP client
    mcp_client = MultiServerMCPClient({
        "composio": {
            "transport": "streamable_http",
            "url": session.mcp.url,
            "headers": session.mcp.headers
        }
    })

    # Get tools
    tools = await mcp_client.get_tools()

    # Create agent
    agent = create_agent(
        tools=tools,
        model=ChatOpenAI(model="gpt-4o")
    )

    return agent

agent = await create_langchain_agent("user_123")
result = await agent.ainvoke({
    "messages": [
        {"role": "user", "content": "Fetch my last email"}
    ]
})
print(result)
```

## ✅ Correct - Claude Agent SDK (Native Tools)

```typescript
// DO: Use Claude Agent SDK with native tools
import { query } from '@anthropic-ai/claude-agent-sdk';
import { Composio } from '@composio/core';
import { ClaudeAgentSDKProvider } from '@composio/claude-agent-sdk';

const composio = new Composio({
  provider: new ClaudeAgentSDKProvider()
});

async function runClaudeAgent(userId: string, prompt: string) {
  // Create session with native tools
  const session = await composio.create(userId, {
    toolkits: ['gmail']
  });

  // Get native Claude tools format
  const tools = await session.tools();

  // Query with tools
  const stream = await query({
    prompt,
    options: {
      model: 'claude-sonnet-4-5-20250929',
      permissionMode: 'bypassPermissions',
      tools
    }
  });

  for await (const event of stream) {
    if (event.type === 'result' && event.subtype === 'success') {
      process.stdout.write(event.result);
    }
  }
}

await runClaudeAgent('user_123', 'Fetch my last email');
```

```python
# DO: Use Claude Agent SDK with native tools
from composio import Composio
from composio_claude_agent_sdk import ClaudeAgentSDKProvider
from claude_agent_sdk import query, ClaudeAgentOptions

composio = Composio(provider=ClaudeAgentSDKProvider())

async def run_claude_agent(user_id: str, prompt: str):
    # Create session with native tools
    session = composio.create(user_id=user_id, toolkits=["gmail"])

    # Get native Claude tools format
    tools = session.tools()

    # Query with tools
    options = ClaudeAgentOptions(
        model="claude-sonnet-4-5-20250929",
        permission_mode="bypassPermissions",
        tools=tools
    )

    async for message in query(prompt=prompt, options=options):
        print(message, end="")

await run_claude_agent("user_123", "Fetch my last email")
```

## ✅ Correct - Claude Agent SDK (MCP)

```typescript
// DO: Use Claude Agent SDK with MCP
import { query } from '@anthropic-ai/claude-agent-sdk';
import { Composio } from '@composio/core';

const composio = new Composio();

async function runClaudeAgentMCP(userId: string, prompt: string) {
  // Create session
  const session = await composio.create(userId, {
    toolkits: ['gmail']
  });

  // Query with MCP server
  const stream = await query({
    prompt,
    options: {
      model: 'claude-sonnet-4-5-20250929',
      permissionMode: 'bypassPermissions',
      mcpServers: {
        composio: {
          type: 'http',
          url: session.mcp.url,
          headers: session.mcp.headers
        }
      }
    }
  });

  for await (const event of stream) {
    if (event.type === 'result' && event.subtype === 'success') {
      process.stdout.write(event.result);
    }
  }
}

await runClaudeAgentMCP('user_123', 'Fetch my last email');
```

```python
# DO: Use Claude Agent SDK with MCP
from composio import Composio
from claude_agent_sdk import query, ClaudeAgentOptions

composio = Composio()

async def run_claude_agent_mcp(user_id: str, prompt: str):
    # Create session
    session = composio.create(user_id=user_id, toolkits=["gmail"])

    # Query with MCP server
    options = ClaudeAgentOptions(
        model="claude-sonnet-4-5-20250929",
        permission_mode="bypassPermissions",
        mcp_servers={
            "composio": {
                "type": session.mcp.type,
                "url": session.mcp.url,
                "headers": session.mcp.headers
            }
        }
    )

    async for message in query(prompt=prompt, options=options):
        print(message, end="")

await run_claude_agent_mcp("user_123", "Fetch my last email")
```

## ✅ Correct - CrewAI (MCP)

```python
# DO: Use CrewAI with MCP
from crewai import Agent, Task, Crew
from crewai.mcp import MCPServerHTTP
from composio import Composio

composio = Composio()

def create_crewai_agent(user_id: str):
    # Create session
    session = composio.create(user_id=user_id, toolkits=["gmail"])

    # Create agent with MCP server
    agent = Agent(
        role="Gmail Assistant",
        goal="Help with Gmail related queries",
        backstory="You are a helpful assistant.",
        mcps=[
            MCPServerHTTP(
                url=session.mcp.url,
                headers=session.mcp.headers
            )
        ]
    )

    return agent

# Create agent
agent = create_crewai_agent("user_123")

# Define task
task = Task(
    description="Find the last email and summarize it.",
    expected_output="A summary including sender, subject, and key points.",
    agent=agent
)

# Execute
crew = Crew(agents=[agent], tasks=[task])
result = crew.kickoff()
print(result)
```

## Using Modifiers with Native Tools

```typescript
// Add logging and telemetry with modifiers
import { Composio } from '@composio/core';
import { VercelProvider } from '@composio/vercel';
import { SessionExecuteMetaModifiers } from '@composio/core';

const composio = new Composio({
  provider: new VercelProvider()
});

async function getToolsWithLogging(userId: string) {
  const session = await composio.create(userId, {
    toolkits: ['gmail']
  });

  // Add modifiers for logging
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

  // Get tools with modifiers
  const tools = await session.tools(modifiers);

  return tools;
}
```

```python
# Add logging and telemetry with modifiers
from composio import Composio, before_execute, after_execute
from composio_openai_agents import OpenAIAgentsProvider
from composio.types import ToolExecuteParams, ToolExecutionResponse

composio = Composio(provider=OpenAIAgentsProvider())

async def get_tools_with_logging(user_id: str):
    session = composio.create(user_id=user_id, toolkits=["gmail"])

    # Define logging modifiers
    @before_execute(tools=[])
    def log_before(
        tool: str,
        toolkit: str,
        params: ToolExecuteParams
    ) -> ToolExecuteParams:
        print(f"🔧 Executing {toolkit}.{tool}")
        print(f"   Arguments: {params.get('arguments', {})}")
        return params

    @after_execute(tools=[])
    def log_after(
        tool: str,
        toolkit: str,
        response: ToolExecutionResponse
    ) -> ToolExecutionResponse:
        print(f"✅ Completed {toolkit}.{tool}")
        if "data" in response:
            print(f"   Response: {response['data']}")
        return response

    # Get tools with modifiers
    tools = session.tools(modifiers=[log_before, log_after])

    return tools
```

## Framework Comparison

| Framework | Native Tools | MCP | Provider Package | Best For |
|-----------|--------------|-----|------------------|----------|
| **Vercel AI SDK** | ✅ | ✅ | `@composio/vercel` | Modern web apps, streaming |
| **OpenAI Agents SDK** | ✅ | ✅ | `@composio/openai-agents` | Production agents |
| **LangChain** | ❌ | ✅ | N/A (MCP only) | Complex chains, memory |
| **Claude Agent SDK** | ✅ | ✅ | `@composio/claude-agent-sdk` | Claude-specific features |
| **CrewAI** | ❌ | ✅ | N/A (MCP only) | Multi-agent teams |

## Pattern: Framework Switching

```typescript
// Same session, different frameworks
const composio = new Composio();
const session = await composio.create('user_123', { toolkits: ['gmail'] });

// Use with Vercel AI SDK
const client1 = await createMCPClient({
  transport: { type: 'http', url: session.mcp.url, headers: session.mcp.headers }
});

// Use with LangChain
const client2 = new MultiServerMCPClient({
  composio: { transport: 'http', url: session.mcp.url, headers: session.mcp.headers }
});

// Use with OpenAI Agents
const client3 = hostedMcpTool({
  serverUrl: session.mcp.url,
  headers: session.mcp.headers
});

// ✅ Same tools, different frameworks
// ✅ Framework flexibility with MCP
```

## Best Practices

### 1. **Choose Native Tools When Available**
- Faster execution (no MCP overhead)
- Better performance for production
- Full control with modifiers

### 2. **Use MCP for Flexibility**
- When using multiple frameworks
- During prototyping phase
- When native tools unavailable

### 3. **Always Create User Sessions**
- Never share sessions across users
- Use proper user IDs (not 'default')
- Isolate tools per user

### 4. **Enable Connection Management**
- Set `manageConnections: true`
- Let agent handle authentication
- Better user experience

### 5. **Add Logging with Modifiers**
- Use beforeExecute/afterExecute
- Track tool execution
- Debug agent behavior

### 6. **Handle Streaming Properly**
- Use framework's streaming APIs
- Process events as they arrive
- Better UX for long operations

## Key Principles

1. **Native tools recommended** - Faster and more control
2. **MCP for flexibility** - Framework independent
3. **User isolation** - Create sessions per user
4. **Connection management** - Enable auto-authentication
5. **Logging and monitoring** - Use modifiers for observability
6. **Framework agnostic** - Same session works with any framework

## Reference

- [Tool Router Documentation](https://docs.composio.dev/sdk/typescript/api/tool-router)
- [Vercel AI SDK](https://sdk.vercel.ai)
- [OpenAI Agents SDK](https://github.com/openai/agents)
- [LangChain](https://langchain.com)
- [Claude Agent SDK](https://github.com/anthropics/anthropic-sdk-typescript)
- [CrewAI](https://www.crewai.com)
