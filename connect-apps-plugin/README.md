# Connect Apps Plugin

Let Claude perform real actions in 500+ apps. Handles auth and connections using Composio under the hood.

## Install

```bash
claude --plugin-dir ./connect-apps-plugin
```

Then run the setup:
```
/connect-apps:setup
```

## What You Get

Once installed, Claude can:
- **Send emails** via Gmail, Outlook
- **Create issues** on GitHub, GitLab, Jira, Linear
- **Post messages** to Slack, Discord, Teams
- **Update docs** in Notion, Google Docs
- **Manage data** in Sheets, Airtable, databases
- **And 500+ more actions**

## How It Works

1. Get a free API key from [platform.composio.dev](https://platform.composio.dev/?utm_source=Github&utm_content=AwesomeSkills)
2. Run `/connect-apps:setup` and paste your key
3. Restart Claude Code
4. First time using an app, you'll authorize via OAuth
5. That's it - Claude can now take real actions

## Try It

After setup, ask Claude:
```
Send me a test email at myemail@example.com
```

---

<p align="center">
  <a href="https://platform.composio.dev/?utm_source=Github&utm_content=AwesomeSkills">
    <img src="https://img.shields.io/badge/Get_API_Key-4F46E5?style=for-the-badge" alt="Get API Key"/>
  </a>
</p>
