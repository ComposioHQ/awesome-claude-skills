---
description: Set up connect-apps - let Claude perform real actions in 500+ apps
allowed-tools: [Bash, Write, AskUserQuestion]
---

# Connect Apps Setup

Set up the connect-apps plugin so Claude can take real actions in external apps (Gmail, Slack, GitHub, etc). Uses Composio for auth and app connections.

## Instructions

### Step 1: Ask for API Key

Ask the user for their Composio API key. If they don't have one, tell them to get a free key at: https://platform.composio.dev/?utm_source=Github&utm_content=AwesomeSkills

Just ask for the key directly. Don't ask if they have one first.

### Step 2: Validate & Get MCP URL

Run this command (replace API_KEY_HERE with the actual key):

```bash
/opt/homebrew/bin/python3.11 -c "
from composio import Composio
composio = Composio(api_key='API_KEY_HERE')
session = composio.create(user_id='claude_user')
print(session.mcp.url)
"
```

If it fails with import error, first run: `pip3 install composio`

### Step 3: Write Config

Write directly to `~/.mcp.json` with this exact format:

```json
{
  "connect-apps": {
    "type": "http",
    "url": "THE_MCP_URL_FROM_STEP_2",
    "headers": {
      "x-api-key": "THE_API_KEY"
    }
  }
}
```

If ~/.mcp.json already exists with other servers, merge the "connect-apps" key into the existing JSON.

### Step 4: Confirm

Tell the user:
```
Setup complete!

To activate: exit and run `claude` again

Then try: "Send me a test email at your@email.com"
```

## Important

- Do NOT try to edit settings.local.json - MCP servers go in ~/.mcp.json
- Do NOT search for config locations - just write to ~/.mcp.json
- Do NOT ask multiple questions - just ask for the API key once
- Be fast - this should take under 30 seconds
