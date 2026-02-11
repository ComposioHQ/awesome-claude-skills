---
name: rube-connect
description: "Connect any of 78+ SaaS apps to your AI agent via Rube MCP (Composio). Handles setup, authentication, and suggests matching automation skills for Gmail, Slack, GitHub, Jira, and more."
requires:
  mcp: [rube]
---

# Connect Apps via Rube MCP

Universal entry point for connecting any supported SaaS application to your AI agent through Rube MCP (powered by Composio). This skill handles MCP setup, walks through OAuth/API-key authentication, and recommends the matching automation skill for each app.

## When This Skill Triggers

Activate this skill when the user says things like:
- "Connect my Gmail" / "Connect Slack" / "Set up Jira integration"
- "Link my GitHub account" / "Add Notion" / "Authenticate Salesforce"
- "Set up [app name]" / "Integrate [app name]" / "Log in to [app name]"
- "Connect an app" / "What apps can I connect?" / "List supported integrations"

## Prerequisites

- Rube MCP server must be configured in the user's MCP client
- If not yet configured, walk the user through setup first (see Step 1 below)

## Connection Flow

### Step 1: Ensure Rube MCP Is Available

Check whether `RUBE_SEARCH_TOOLS` is available. If it is, Rube MCP is already configured -- skip to Step 2.

If Rube MCP is NOT configured yet, instruct the user:

> **Add Rube MCP to your client.** Add `https://rube.app/mcp` as an MCP server in your configuration. No API keys needed -- just add the endpoint and it works.
>
> **For Claude Code users**, run:
> ```
> claude mcp add rube https://rube.app/mcp
> ```
>
> **For other MCP clients** (Cursor, Windsurf, etc.), add to your MCP config:
> ```json
> {
>   "mcpServers": {
>     "rube": {
>       "url": "https://rube.app/mcp"
>     }
>   }
> }
> ```
>
> After adding, restart the client or reload MCP servers, then try again.

### Step 2: Identify the App to Connect

Match the user's request to the correct **toolkit slug** from the reference table below. If the user says a general name like "Google Calendar", resolve it to the toolkit slug `googlecalendar`. If the user is unsure which app they want, show them the categorized list from the Supported Apps section.

### Step 3: Initiate the Connection

Call `RUBE_SEARCH_TOOLS` first to establish a session, then call `RUBE_MANAGE_CONNECTIONS` with the resolved toolkit slug:

```
RUBE_MANAGE_CONNECTIONS({
  "toolkits": ["<toolkit_slug>"],
  "session_id": "<session_id_from_search>"
})
```

**Interpret the response:**

- **If the connection is already ACTIVE**: Inform the user they are already connected and ready to go. Skip to Step 5.
- **If a `redirect_url` is returned**: Present the URL as a clickable markdown link and ask the user to complete authentication in their browser:

> Click this link to authenticate: [Connect <App Name>](<redirect_url>)
>
> After completing the sign-in in your browser, come back here and let me know.

### Step 4: Verify the Connection

After the user says they have completed authentication, call `RUBE_MANAGE_CONNECTIONS` again with the same toolkit slug to confirm the connection status is now ACTIVE.

- **If ACTIVE**: Confirm success and proceed to Step 5.
- **If still not ACTIVE**: See the Troubleshooting section below.

### Step 5: Suggest the Matching Automation Skill

Once the connection is active, suggest installing the matching automation skill so the user can start working with the app immediately:

> Your **<App Name>** connection is active. To get full automation capabilities, install the matching skill:
> ```
> npx skills add ComposioHQ/awesome-claude-skills --skill <skill-name>-automation
> ```
>
> This will give you pre-built workflows for common <App Name> tasks.

Use the **Skill Name** column from the reference table below to construct the install command.

If no matching automation skill exists for the requested app, skip this suggestion and instead tell the user they can use `RUBE_SEARCH_TOOLS` to discover available tools for that toolkit directly.

## Supported Apps Reference

### Email and Communication

| App | Toolkit Slug | Skill Name | Auth Type |
|-----|-------------|------------|-----------|
| Gmail | `gmail` | gmail-automation | OAuth 2.0 |
| Outlook | `outlook` | outlook-automation | OAuth 2.0 |
| Slack | `slack` | slack-automation | OAuth 2.0 |
| Discord | `discord` | discord-automation | OAuth 2.0 |
| Microsoft Teams | `microsoft_teams` | microsoft-teams-automation | OAuth 2.0 |
| Telegram | `telegram` | telegram-automation | API Key |
| WhatsApp | `whatsapp` | whatsapp-automation | API Key |
| SendGrid | `sendgrid` | sendgrid-automation | API Key |
| Postmark | `postmark` | postmark-automation | API Key |
| Mailchimp | `mailchimp` | mailchimp-automation | OAuth 2.0 |
| Brevo | `brevo` | brevo-automation | API Key |
| ConvertKit | `kit` | convertkit-automation | API Key |
| ActiveCampaign | `active_campaign` | activecampaign-automation | API Key |
| Intercom | `intercom` | intercom-automation | OAuth 2.0 |

### Project Management and Productivity

| App | Toolkit Slug | Skill Name | Auth Type |
|-----|-------------|------------|-----------|
| Jira | `jira` | jira-automation | OAuth 2.0 |
| Asana | `asana` | asana-automation | OAuth 2.0 |
| Linear | `linear` | linear-automation | OAuth 2.0 |
| Trello | `trello` | trello-automation | OAuth 2.0 |
| ClickUp | `clickup` | clickup-automation | OAuth 2.0 |
| Monday.com | `monday` | monday-automation | OAuth 2.0 |
| Notion | `notion` | notion-automation | OAuth 2.0 |
| Todoist | `todoist` | todoist-automation | OAuth 2.0 |
| Wrike | `wrike` | wrike-automation | OAuth 2.0 |
| Basecamp | `basecamp` | basecamp-automation | OAuth 2.0 |
| Coda | `coda` | coda-automation | API Key |
| Confluence | `confluence` | confluence-automation | OAuth 2.0 |
| Miro | `miro` | miro-automation | OAuth 2.0 |

### Developer Tools and DevOps

| App | Toolkit Slug | Skill Name | Auth Type |
|-----|-------------|------------|-----------|
| GitHub | `github` | github-automation | OAuth 2.0 |
| GitLab | `gitlab` | gitlab-automation | OAuth 2.0 |
| Bitbucket | `bitbucket` | bitbucket-automation | OAuth 2.0 |
| Vercel | `vercel` | vercel-automation | OAuth 2.0 |
| Render | `render` | render-automation | API Key |
| CircleCI | `circleci` | circleci-automation | API Key |
| Sentry | `sentry` | sentry-automation | OAuth 2.0 |
| Datadog | `datadog` | datadog-automation | API Key |
| PagerDuty | `pagerduty` | pagerduty-automation | OAuth 2.0 |
| Supabase | `supabase` | supabase-automation | API Key |

### CRM and Sales

| App | Toolkit Slug | Skill Name | Auth Type |
|-----|-------------|------------|-----------|
| Salesforce | `salesforce` | salesforce-automation | OAuth 2.0 |
| HubSpot | `hubspot` | hubspot-automation | OAuth 2.0 |
| Pipedrive | `pipedrive` | pipedrive-automation | OAuth 2.0 |
| Close | `close` | close-automation | API Key |
| Zoho CRM | `zoho` | zoho-crm-automation | OAuth 2.0 |

### File Storage and Documents

| App | Toolkit Slug | Skill Name | Auth Type |
|-----|-------------|------------|-----------|
| Google Drive | `googledrive` | google-drive-automation | OAuth 2.0 |
| Google Sheets | `googlesheets` | googlesheets-automation | OAuth 2.0 |
| Dropbox | `dropbox` | dropbox-automation | OAuth 2.0 |
| Box | `box` | box-automation | OAuth 2.0 |
| OneDrive | `one_drive` | one-drive-automation | OAuth 2.0 |
| Airtable | `airtable` | airtable-automation | OAuth 2.0 |
| DocuSign | `docusign` | docusign-automation | OAuth 2.0 |
| Canva | `canva` | canva-automation | OAuth 2.0 |

### Calendar and Scheduling

| App | Toolkit Slug | Skill Name | Auth Type |
|-----|-------------|------------|-----------|
| Google Calendar | `googlecalendar` | google-calendar-automation | OAuth 2.0 |
| Outlook Calendar | `outlook` | outlook-calendar-automation | OAuth 2.0 |
| Calendly | `calendly` | calendly-automation | OAuth 2.0 |
| Cal.com | `cal` | cal-com-automation | API Key |
| Zoom | `zoom` | zoom-automation | OAuth 2.0 |

### Social Media

| App | Toolkit Slug | Skill Name | Auth Type |
|-----|-------------|------------|-----------|
| Twitter / X | `twitter` | twitter-automation | OAuth 2.0 |
| LinkedIn | `linkedin` | linkedin-automation | OAuth 2.0 |
| Instagram | `instagram` | instagram-automation | OAuth 2.0 |
| Reddit | `reddit` | reddit-automation | OAuth 2.0 |
| TikTok | `tiktok` | tiktok-automation | OAuth 2.0 |
| YouTube | `youtube` | youtube-automation | OAuth 2.0 |

### Analytics

| App | Toolkit Slug | Skill Name | Auth Type |
|-----|-------------|------------|-----------|
| Google Analytics | `google_analytics` | google-analytics-automation | OAuth 2.0 |
| Amplitude | `amplitude` | amplitude-automation | API Key |
| Mixpanel | `mixpanel` | mixpanel-automation | API Key |
| PostHog | `posthog` | posthog-automation | API Key |
| Segment | `segment` | segment-automation | API Key |

### E-Commerce and Payments

| App | Toolkit Slug | Skill Name | Auth Type |
|-----|-------------|------------|-----------|
| Shopify | `shopify` | shopify-automation | OAuth 2.0 |
| Stripe | `stripe` | stripe-automation | API Key |
| Square | `square` | square-automation | OAuth 2.0 |

### Customer Support

| App | Toolkit Slug | Skill Name | Auth Type |
|-----|-------------|------------|-----------|
| Zendesk | `zendesk` | zendesk-automation | OAuth 2.0 |
| Freshdesk | `freshdesk` | freshdesk-automation | API Key |
| Freshservice | `freshservice` | freshservice-automation | API Key |
| HelpDesk | `helpdesk` | helpdesk-automation | API Key |
| Klaviyo | `klaviyo` | klaviyo-automation | API Key |

### Design and Website

| App | Toolkit Slug | Skill Name | Auth Type |
|-----|-------------|------------|-----------|
| Figma | `figma` | figma-automation | OAuth 2.0 |
| Webflow | `webflow` | webflow-automation | OAuth 2.0 |

### HR and Operations

| App | Toolkit Slug | Skill Name | Auth Type |
|-----|-------------|------------|-----------|
| BambooHR | `bamboohr` | bamboohr-automation | API Key |
| Make | `make` | make-automation | API Key |

## App Name Aliases

When matching user input, recognize these common aliases:

| User Might Say | Resolves To |
|----------------|-------------|
| "Google Mail" | Gmail (`gmail`) |
| "GCal" | Google Calendar (`googlecalendar`) |
| "GDrive" | Google Drive (`googledrive`) |
| "Sheets", "Google Spreadsheets" | Google Sheets (`googlesheets`) |
| "Teams", "MS Teams" | Microsoft Teams (`microsoft_teams`) |
| "X", "Twitter" | Twitter / X (`twitter`) |
| "OneDrive", "One Drive" | OneDrive (`one_drive`) |
| "Outlook Mail" | Outlook (`outlook`) |
| "Outlook Calendar" | Outlook Calendar (`outlook`) -- same toolkit, different skill |
| "GA4", "Google Analytics 4" | Google Analytics (`google_analytics`) |
| "IG", "Insta" | Instagram (`instagram`) |
| "GH", "GitHub" | GitHub (`github`) |
| "GL", "GitLab" | GitLab (`gitlab`) |
| "ActiveCampaign" | ActiveCampaign (`active_campaign`) |
| "Kit", "ConvertKit" | ConvertKit (`kit`) |
| "Zoho" | Zoho CRM (`zoho`) |
| "Cal", "Cal dot com" | Cal.com (`cal`) |

## Connecting Multiple Apps at Once

If the user wants to connect several apps simultaneously, `RUBE_MANAGE_CONNECTIONS` accepts an array of toolkit slugs:

```
RUBE_MANAGE_CONNECTIONS({
  "toolkits": ["gmail", "slack", "github"],
  "session_id": "<session_id>"
})
```

Present each auth link separately and clearly label which app each link is for. Verify all connections after the user completes authentication.

## Troubleshooting

### Connection Shows Non-Active After Auth

1. **Re-check the connection**: Call `RUBE_MANAGE_CONNECTIONS` again -- the status sometimes takes a moment to propagate.
2. **Re-initiate authentication**: If still not active, call `RUBE_MANAGE_CONNECTIONS` with `reinitiate_all: true` to force a fresh auth flow:
   ```
   RUBE_MANAGE_CONNECTIONS({
     "toolkits": ["<toolkit_slug>"],
     "reinitiate_all": true,
     "session_id": "<session_id>"
   })
   ```
3. **Browser issues**: Ask the user to try a different browser or clear cookies for the auth provider.

### OAuth Scope Errors

Some apps require specific OAuth scopes. If the user sees permissions errors after connecting:

1. The app may need additional scopes not granted during the initial OAuth flow.
2. Re-initiate the connection with `reinitiate_all: true` and ask the user to approve all requested permissions.
3. For Google apps specifically, the user should ensure they check all permission checkboxes during the consent screen.

### API Key Authentication Issues

For apps that use API keys instead of OAuth:

1. Verify the user entered the correct API key (no trailing spaces or newlines).
2. Ensure the API key has the necessary permissions/scopes for the intended operations.
3. Check if the API key has expired or been revoked.
4. Some apps (like Datadog, Amplitude) require both an API key and an application key.

### "Toolkit Not Found" Errors

If `RUBE_MANAGE_CONNECTIONS` returns an error about the toolkit:

1. Verify the toolkit slug is spelled exactly as listed in the reference table above.
2. Toolkit slugs are case-sensitive and use underscores (not hyphens) where applicable.
3. Run `RUBE_SEARCH_TOOLS` with a query about the app to confirm the correct toolkit name.

### Expired or Stale Connections

Connections can expire over time (OAuth tokens expire, API keys get rotated):

1. Call `RUBE_MANAGE_CONNECTIONS` to check current status.
2. If the connection was previously active but is now broken, use `reinitiate_all: true` to force re-authentication.
3. For OAuth apps, the user may need to re-authorize if they revoked access from the app's settings.

## Quick Reference: Connection Commands

| Action | Command |
|--------|---------|
| Check/initiate connection | `RUBE_MANAGE_CONNECTIONS({"toolkits": ["<slug>"]})` |
| Force re-authentication | `RUBE_MANAGE_CONNECTIONS({"toolkits": ["<slug>"], "reinitiate_all": true})` |
| Connect multiple apps | `RUBE_MANAGE_CONNECTIONS({"toolkits": ["slug1", "slug2", ...]})` |
| Discover tools for an app | `RUBE_SEARCH_TOOLS({"queries": [{"use_case": "list available tools for <app>"}]})` |
| Install automation skill | `npx skills add ComposioHQ/awesome-claude-skills --skill <skill-name>-automation` |

---
*Powered by [Composio](https://composio.dev)*
