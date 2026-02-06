<h1 align="center">Awesome Claude Skills</h1>

<p align="center">
<a href="https://platform.composio.dev/?utm_source=Github&utm_medium=Youtube&utm_campaign=2025-11&utm_content=AwesomeSkills">
  <img width="1280" height="640" alt="Composio banner" src="https://github.com/user-attachments/assets/e91255af-e4ba-4d71-b1a8-bd081e8a234a">
</a>


</p>

<p align="center">
  <a href="https://awesome.re">
    <img src="https://awesome.re/badge.svg" alt="Awesome" />
  </a>
  <a href="https://makeapullrequest.com">
    <img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square" alt="PRs Welcome" />
  </a>
  <a href="https://www.apache.org/licenses/LICENSE-2.0">
    <img src="https://img.shields.io/badge/License-Apache_2.0-blue.svg?style=flat-square" alt="License: Apache-2.0" />
  </a>
</p>
<div>
<p align="center">
  <a href="https://twitter.com/composio">
    <img src="https://img.shields.io/badge/Follow on X-000000?style=for-the-badge&logo=x&logoColor=white" alt="Follow on X" />
  </a>
  <a href="https://www.linkedin.com/company/composiohq/">
    <img src="https://img.shields.io/badge/Follow on LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" alt="Follow on LinkedIn" />
  </a>
  <a href="https://discord.com/invite/composio">
    <img src="https://img.shields.io/badge/Join our Discord-5865F2?style=for-the-badge&logo=discord&logoColor=white" alt="Join our Discord" />
  </a>
  </p>
</div>

A curated list of practical Claude Skills for enhancing productivity across Claude.ai, Claude Code, and the Claude API.


> **Want skills that do more than generate text?** Claude can send emails, create issues, post to Slack, and take actions across 1000+ apps. [See how →](./connect/)

---

## Quickstart: Connect Claude to 500+ Apps

The **connect-apps** plugin lets Claude perform real actions - send emails, create issues, post to Slack. It handles auth and connects to 500+ apps using Composio under the hood.

### 1. Install the Plugin

```bash
claude --plugin-dir ./connect-apps-plugin
```

### 2. Run Setup

```
/connect-apps:setup
```

Paste your API key when asked. (Get a free key at [platform.composio.dev](https://platform.composio.dev/?utm_source=Github&utm_content=AwesomeSkills))

### 3. Restart & Try It

```bash
exit
claude
```

> **Want skills that do more than generate text?** Claude can send emails, create issues, post to Slack, and take actions across 1000+ apps. [See how →](./connect/)

If you receive the email, Claude is now connected to 500+ apps.

**[See all supported apps →](https://composio.dev/toolkits)**

---

## Contents

- [What Are Claude Skills?](#what-are-claude-skills)
- [Skills](#skills)
  - [Document Processing](#document-processing)
  - [Development & Code Tools](#development--code-tools)
  - [Data & Analysis](#data--analysis)
  - [Business & Marketing](#business--marketing)
  - [Communication & Writing](#communication--writing)
  - [Creative & Media](#creative--media)
  - [Productivity & Organization](#productivity--organization)
  - [Collaboration & Project Management](#collaboration--project-management)
  - [Security & Systems](#security--systems)
  - [App Automation via Composio](#app-automation-via-composio)
- [Getting Started](#getting-started)
- [Creating Skills](#creating-skills)
- [Contributing](#contributing)
- [Resources](#resources)
- [License](#license)

## What Are Claude Skills?

Claude Skills are customizable workflows that teach Claude how to perform specific tasks according to your unique requirements. Skills enable Claude to execute tasks in a repeatable, standardized manner across all Claude platforms.

## Skills

### Document Processing

- [docx](https://github.com/anthropics/skills/tree/main/skills/docx) - Create, edit, analyze Word docs with tracked changes, comments, formatting.
- [pdf](https://github.com/anthropics/skills/tree/main/skills/pdf) - Extract text, tables, metadata, merge & annotate PDFs.
- [pptx](https://github.com/anthropics/skills/tree/main/skills/pptx) - Read, generate, and adjust slides, layouts, templates.
- [xlsx](https://github.com/anthropics/skills/tree/main/skills/xlsx) - Spreadsheet manipulation: formulas, charts, data transformations.
- [Markdown to EPUB Converter](https://github.com/smerchek/claude-epub-skill) - Converts markdown documents and chat summaries into professional EPUB ebook files. *By [@smerchek](https://github.com/smerchek)*

### Development & Code Tools

- [artifacts-builder](https://github.com/anthropics/skills/tree/main/skills/web-artifacts-builder) - Suite of tools for creating elaborate, multi-component claude.ai HTML artifacts using modern frontend web technologies (React, Tailwind CSS, shadcn/ui).
- [aws-skills](https://github.com/zxkane/aws-skills) - AWS development with CDK best practices, cost optimization MCP servers, and serverless/event-driven architecture patterns.
- [Changelog Generator](./changelog-generator/) - Automatically creates user-facing changelogs from git commits by analyzing history and transforming technical commits into customer-friendly release notes.
- [Claude Code Terminal Title](https://github.com/bluzername/claude-code-terminal-title) - Gives each Claud-Code terminal window a dynamic title that describes the work being done so you don't lose track of what window is doing what.
- [D3.js Visualization](https://github.com/chrisvoncsefalvay/claude-d3js-skill) - Teaches Claude to produce D3 charts and interactive data visualizations. *By [@chrisvoncsefalvay](https://github.com/chrisvoncsefalvay)*
- [FFUF Web Fuzzing](https://github.com/jthack/ffuf_claude_skill) - Integrates the ffuf web fuzzer so Claude can run fuzzing tasks and analyze results for vulnerabilities. *By [@jthack](https://github.com/jthack)*
- [finishing-a-development-branch](https://github.com/obra/superpowers/tree/main/skills/finishing-a-development-branch) - Guides completion of development work by presenting clear options and handling chosen workflow.
- [iOS Simulator](https://github.com/conorluddy/ios-simulator-skill) - Enables Claude to interact with iOS Simulator for testing and debugging iOS applications. *By [@conorluddy](https://github.com/conorluddy)*
- [jules](https://github.com/sanjay3290/ai-skills/tree/main/skills/jules) - Delegate coding tasks to Google Jules AI agent for async bug fixes, documentation, tests, and feature implementation on GitHub repos. *By [@sanjay3290](https://github.com/sanjay3290)*
- [LangSmith Fetch](./langsmith-fetch/) - Debug LangChain and LangGraph agents by automatically fetching and analyzing execution traces from LangSmith Studio. First AI observability skill for Claude Code. *By [@OthmanAdi](https://github.com/OthmanAdi)*
- [MCP Builder](./mcp-builder/) - Guides creation of high-quality MCP (Model Context Protocol) servers for integrating external APIs and services with LLMs using Python or TypeScript.
- [move-code-quality-skill](https://github.com/1NickPappas/move-code-quality-skill) - Analyzes Move language packages against the official Move Book Code Quality Checklist for Move 2024 Edition compliance and best practices.
- [Playwright Browser Automation](https://github.com/lackeyjb/playwright-skill) - Model-invoked Playwright automation for testing and validating web applications. *By [@lackeyjb](https://github.com/lackeyjb)*
- [prompt-engineering](https://github.com/NeoLabHQ/context-engineering-kit/tree/master/plugins/customaize-agent/skills/prompt-engineering) - Teaches well-known prompt engineering techniques and patterns, including Anthropic best practices and agent persuasion principles.
- [pypict-claude-skill](https://github.com/omkamal/pypict-claude-skill) - Design comprehensive test cases using PICT (Pairwise Independent Combinatorial Testing) for requirements or code, generating optimized test suites with pairwise coverage.
- [reddit-fetch](https://github.com/ykdojo/claude-code-tips/tree/main/skills/reddit-fetch) - Fetches Reddit content via Gemini CLI when WebFetch is blocked or returns 403 errors.
- [Skill Creator](./skill-creator/) - Provides guidance for creating effective Claude Skills that extend capabilities with specialized knowledge, workflows, and tool integrations.
- [Skill Seekers](https://github.com/yusufkaraaslan/Skill_Seekers) - Automatically converts any documentation website into a Claude AI skill in minutes. *By [@yusufkaraaslan](https://github.com/yusufkaraaslan)*
- [software-architecture](https://github.com/NeoLabHQ/context-engineering-kit/tree/master/plugins/ddd/skills/software-architecture) - Implements design patterns including Clean Architecture, SOLID principles, and comprehensive software design best practices.
- [subagent-driven-development](https://github.com/NeoLabHQ/context-engineering-kit/tree/master/plugins/sadd/skills/subagent-driven-development) - Dispatches independent subagents for individual tasks with code review checkpoints between iterations for rapid, controlled development.
- [test-driven-development](https://github.com/obra/superpowers/tree/main/skills/test-driven-development) - Use when implementing any feature or bugfix, before writing implementation code.
- [using-git-worktrees](https://github.com/obra/superpowers/blob/main/skills/using-git-worktrees/) - Creates isolated git worktrees with smart directory selection and safety verification.
- [Connect](./connect/) - Connect Claude to any app. Send emails, create issues, post messages, update databases - take real actions across Gmail, Slack, GitHub, Notion, and 1000+ services.
- [Webapp Testing](./webapp-testing/) - Tests local web applications using Playwright for verifying frontend functionality, debugging UI behavior, and capturing screenshots.

### Data & Analysis

- [CSV Data Summarizer](https://github.com/coffeefuelbump/csv-data-summarizer-claude-skill) - Automatically analyzes CSV files and generates comprehensive insights with visualizations without requiring user prompts. *By [@coffeefuelbump](https://github.com/coffeefuelbump)*
- [deep-research](https://github.com/sanjay3290/ai-skills/tree/main/skills/deep-research) - Execute autonomous multi-step research using Gemini Deep Research Agent for market analysis, competitive landscaping, and literature reviews. *By [@sanjay3290](https://github.com/sanjay3290)*
- [postgres](https://github.com/sanjay3290/ai-skills/tree/main/skills/postgres) - Execute safe read-only SQL queries against PostgreSQL databases with multi-connection support and defense-in-depth security. *By [@sanjay3290](https://github.com/sanjay3290)*
- [root-cause-tracing](https://github.com/obra/superpowers/tree/main/skills/root-cause-tracing) - Use when errors occur deep in execution and you need to trace back to find the original trigger.

### Business & Marketing

- [Brand Guidelines](./brand-guidelines/) - Applies Anthropic's official brand colors and typography to artifacts for consistent visual identity and professional design standards.
- [Competitive Ads Extractor](./competitive-ads-extractor/) - Extracts and analyzes competitors' ads from ad libraries to understand messaging and creative approaches that resonate.
- [Domain Name Brainstormer](./domain-name-brainstormer/) - Generates creative domain name ideas and checks availability across multiple TLDs including .com, .io, .dev, and .ai extensions.
- [Internal Comms](./internal-comms/) - Helps write internal communications including 3P updates, company newsletters, FAQs, status reports, and project updates using company-specific formats.
- [Lead Research Assistant](./lead-research-assistant/) - Identifies and qualifies high-quality leads by analyzing your product, searching for target companies, and providing actionable outreach strategies.

### Communication & Writing

- [article-extractor](https://github.com/michalparkola/tapestry-skills-for-claude-code/tree/main/article-extractor) - Extract full article text and metadata from web pages.
- [brainstorming](https://github.com/obra/superpowers/tree/main/skills/brainstorming) - Transform rough ideas into fully-formed designs through structured questioning and alternative exploration.
- [Content Research Writer](./content-research-writer/) - Assists in writing high-quality content by conducting research, adding citations, improving hooks, and providing section-by-section feedback.
- [family-history-research](https://github.com/emaynard/claude-family-history-research-skill) - Provides assistance with planning family history and genealogy research projects.
- [Meeting Insights Analyzer](./meeting-insights-analyzer/) - Analyzes meeting transcripts to uncover behavioral patterns including conflict avoidance, speaking ratios, filler words, and leadership style.
- [NotebookLM Integration](https://github.com/PleasePrompto/notebooklm-skill) - Lets Claude Code chat directly with NotebookLM for source-grounded answers based exclusively on uploaded documents. *By [@PleasePrompto](https://github.com/PleasePrompto)*
- [Twitter Algorithm Optimizer](./twitter-algorithm-optimizer/) - Analyze and optimize tweets for maximum reach using Twitter's open-source algorithm insights. Rewrite and edit tweets to improve engagement and visibility.

### Creative & Media

- [Canvas Design](./canvas-design/) - Creates beautiful visual art in PNG and PDF documents using design philosophy and aesthetic principles for posters, designs, and static pieces.
- [imagen](https://github.com/sanjay3290/ai-skills/tree/main/skills/imagen) - Generate images using Google Gemini's image generation API for UI mockups, icons, illustrations, and visual assets. *By [@sanjay3290](https://github.com/sanjay3290)*
- [Image Enhancer](./image-enhancer/) - Improves image and screenshot quality by enhancing resolution, sharpness, and clarity for professional presentations and documentation.
- [Slack GIF Creator](./slack-gif-creator/) - Creates animated GIFs optimized for Slack with validators for size constraints and composable animation primitives.
- [Theme Factory](./theme-factory/) - Applies professional font and color themes to artifacts including slides, docs, reports, and HTML landing pages with 10 pre-set themes.
- [Video Downloader](./video-downloader/) - Downloads videos from YouTube and other platforms for offline viewing, editing, or archival with support for various formats and quality options.
- [youtube-transcript](https://github.com/michalparkola/tapestry-skills-for-claude-code/tree/main/youtube-transcript) - Fetch transcripts from YouTube videos and prepare summaries.

### Productivity & Organization

- [File Organizer](./file-organizer/) - Intelligently organizes files and folders by understanding context, finding duplicates, and suggesting better organizational structures.
- [Invoice Organizer](./invoice-organizer/) - Automatically organizes invoices and receipts for tax preparation by reading files, extracting information, and renaming consistently.
- [kaizen](https://github.com/NeoLabHQ/context-engineering-kit/tree/master/plugins/kaizen/skills/kaizen) - Applies continuous improvement methodology with multiple analytical approaches, based on Japanese Kaizen philosophy and Lean methodology.
- [n8n-skills](https://github.com/haunchen/n8n-skills) - Enables AI assistants to directly understand and operate n8n workflows.
- [Raffle Winner Picker](./raffle-winner-picker/) - Randomly selects winners from lists, spreadsheets, or Google Sheets for giveaways and contests with cryptographically secure randomness.
- [Tailored Resume Generator](./tailored-resume-generator/) - Analyzes job descriptions and generates tailored resumes that highlight relevant experience, skills, and achievements to maximize interview chances.
- [ship-learn-next](https://github.com/michalparkola/tapestry-skills-for-claude-code/tree/main/ship-learn-next) - Skill to help iterate on what to build or learn next, based on feedback loops.
- [tapestry](https://github.com/michalparkola/tapestry-skills-for-claude-code/tree/main/tapestry) - Interlink and summarize related documents into knowledge networks.

### Collaboration & Project Management

- [git-pushing](https://github.com/mhattingpete/claude-skills-marketplace/tree/main/engineering-workflow-plugin/skills/git-pushing) - Automate git operations and repository interactions.
- [google-workspace-skills](https://github.com/sanjay3290/ai-skills/tree/main/skills) - Suite of Google Workspace integrations: Gmail, Calendar, Chat, Docs, Sheets, Slides, and Drive with cross-platform OAuth. *By [@sanjay3290](https://github.com/sanjay3290)*
- [outline](https://github.com/sanjay3290/ai-skills/tree/main/skills/outline) - Search, read, create, and manage documents in Outline wiki instances (cloud or self-hosted). *By [@sanjay3290](https://github.com/sanjay3290)*
- [review-implementing](https://github.com/mhattingpete/claude-skills-marketplace/tree/main/engineering-workflow-plugin/skills/review-implementing) - Evaluate code implementation plans and align with specs.
- [test-fixing](https://github.com/mhattingpete/claude-skills-marketplace/tree/main/engineering-workflow-plugin/skills/test-fixing) - Detect failing tests and propose patches or fixes.

### Security & Systems

- [computer-forensics](https://github.com/mhattingpete/claude-skills-marketplace/tree/main/computer-forensics-skills/skills/computer-forensics) - Digital forensics analysis and investigation techniques.
- [file-deletion](https://github.com/mhattingpete/claude-skills-marketplace/tree/main/computer-forensics-skills/skills/file-deletion) - Secure file deletion and data sanitization methods.
- [metadata-extraction](https://github.com/mhattingpete/claude-skills-marketplace/tree/main/computer-forensics-skills/skills/metadata-extraction) - Extract and analyze file metadata for forensic purposes.
- [threat-hunting-with-sigma-rules](https://github.com/jthack/threat-hunting-with-sigma-rules-skill) - Use Sigma detection rules to hunt for threats and analyze security events.

### App Automation via Composio

Pre-built workflow skills for 78 SaaS apps via [Rube MCP (Composio)](https://composio.dev). Each skill includes tool sequences, parameter guidance, known pitfalls, and quick reference tables — all using real tool slugs discovered from Composio's API.

**CRM & Sales**
- [Close Automation](./close-automation/) - Automate Close CRM: leads, contacts, opportunities, activities, and pipelines.
- [HubSpot Automation](./hubspot-automation/) - Automate HubSpot CRM: contacts, deals, companies, tickets, and email engagement.
- [Pipedrive Automation](./pipedrive-automation/) - Automate Pipedrive: deals, contacts, organizations, activities, and pipelines.
- [Salesforce Automation](./salesforce-automation/) - Automate Salesforce: objects, records, SOQL queries, and bulk operations.
- [Zoho CRM Automation](./zoho-crm-automation/) - Automate Zoho CRM: leads, contacts, deals, accounts, and modules.

**Project Management**
- [Asana Automation](./asana-automation/) - Automate Asana: tasks, projects, sections, assignments, and workspaces.
- [Basecamp Automation](./basecamp-automation/) - Automate Basecamp: to-do lists, messages, people, groups, and projects.
- [ClickUp Automation](./clickup-automation/) - Automate ClickUp: tasks, lists, spaces, goals, and time tracking.
- [Jira Automation](./jira-automation/) - Automate Jira: issues, projects, boards, sprints, and JQL queries.
- [Linear Automation](./linear-automation/) - Automate Linear: issues, projects, cycles, teams, and workflows.
- [Monday Automation](./monday-automation/) - Automate Monday.com: boards, items, columns, groups, and workspaces.
- [Notion Automation](./notion-automation/) - Automate Notion: pages, databases, blocks, comments, and search.
- [Todoist Automation](./todoist-automation/) - Automate Todoist: tasks, projects, sections, labels, and filters.
- [Trello Automation](./trello-automation/) - Automate Trello: boards, cards, lists, members, and checklists.
- [Wrike Automation](./wrike-automation/) - Automate Wrike: tasks, folders, projects, comments, and workflows.

**Communication**
- [Discord Automation](./discord-automation/) - Automate Discord: messages, channels, servers, roles, and reactions.
- [Intercom Automation](./intercom-automation/) - Automate Intercom: conversations, contacts, companies, tickets, and articles.
- [Microsoft Teams Automation](./microsoft-teams-automation/) - Automate Teams: messages, channels, teams, chats, and meetings.
- [Slack Automation](./slack-automation/) - Automate Slack: messages, channels, search, reactions, threads, and scheduling.
- [Telegram Automation](./telegram-automation/) - Automate Telegram: messages, chats, media, groups, and bots.
- [WhatsApp Automation](./whatsapp-automation/) - Automate WhatsApp: messages, media, templates, groups, and business profiles.

**Email**
- [Gmail Automation](./gmail-automation/) - Automate Gmail: send/reply, search, labels, drafts, and attachments.
- [Outlook Automation](./outlook-automation/) - Automate Outlook: emails, folders, contacts, and calendar integration.
- [Postmark Automation](./postmark-automation/) - Automate Postmark: transactional emails, templates, servers, and delivery stats.
- [SendGrid Automation](./sendgrid-automation/) - Automate SendGrid: emails, templates, contacts, lists, and campaign stats.

**Code & DevOps**
- [Bitbucket Automation](./bitbucket-automation/) - Automate Bitbucket: repos, PRs, branches, issues, and workspaces.
- [CircleCI Automation](./circleci-automation/) - Automate CircleCI: pipelines, workflows, jobs, and project configuration.
- [Datadog Automation](./datadog-automation/) - Automate Datadog: monitors, dashboards, metrics, incidents, and alerts.
- [GitHub Automation](./github-automation/) - Automate GitHub: issues, PRs, repos, branches, actions, and code search.
- [GitLab Automation](./gitlab-automation/) - Automate GitLab: issues, MRs, projects, pipelines, and branches.
- [PagerDuty Automation](./pagerduty-automation/) - Automate PagerDuty: incidents, services, schedules, escalation policies, and on-call.
- [Render Automation](./render-automation/) - Automate Render: services, deploys, and project management.
- [Sentry Automation](./sentry-automation/) - Automate Sentry: issues, events, projects, releases, and alerts.
- [Supabase Automation](./supabase-automation/) - Automate Supabase: SQL queries, table schemas, edge functions, and storage.
- [Vercel Automation](./vercel-automation/) - Automate Vercel: deployments, projects, domains, environment variables, and logs.

**Storage & Files**
- [Box Automation](./box-automation/) - Automate Box: files, folders, search, sharing, collaborations, and sign requests.
- [Dropbox Automation](./dropbox-automation/) - Automate Dropbox: files, folders, search, sharing, and batch operations.
- [Google Drive Automation](./google-drive-automation/) - Automate Google Drive: upload, download, search, share, and organize files.
- [OneDrive Automation](./one-drive-automation/) - Automate OneDrive: files, folders, search, sharing, permissions, and versioning.

**Spreadsheets & Databases**
- [Airtable Automation](./airtable-automation/) - Automate Airtable: records, tables, bases, views, and field management.
- [Coda Automation](./coda-automation/) - Automate Coda: docs, tables, rows, formulas, and automations.
- [Google Sheets Automation](./googlesheets-automation/) - Automate Google Sheets: read/write cells, formatting, formulas, and batch operations.

**Calendar & Scheduling**
- [Cal.com Automation](./cal-com-automation/) - Automate Cal.com: event types, bookings, availability, and scheduling.
- [Calendly Automation](./calendly-automation/) - Automate Calendly: events, invitees, event types, scheduling links, and availability.
- [Google Calendar Automation](./google-calendar-automation/) - Automate Google Calendar: events, attendees, free/busy, and recurring schedules.
- [Outlook Calendar Automation](./outlook-calendar-automation/) - Automate Outlook Calendar: events, attendees, reminders, and recurring schedules.

**Social Media**
- [Instagram Automation](./instagram-automation/) - Automate Instagram: posts, stories, comments, media, and business insights.
- [LinkedIn Automation](./linkedin-automation/) - Automate LinkedIn: posts, profiles, companies, images, and comments.
- [Reddit Automation](./reddit-automation/) - Automate Reddit: posts, comments, subreddits, voting, and moderation.
- [TikTok Automation](./tiktok-automation/) - Automate TikTok: video uploads, queries, and creator management.
- [Twitter Automation](./twitter-automation/) - Automate Twitter/X: tweets, search, users, lists, and engagement.
- [YouTube Automation](./youtube-automation/) - Automate YouTube: videos, channels, playlists, comments, and subscriptions.

**Marketing & Email Marketing**
- [ActiveCampaign Automation](./activecampaign-automation/) - Automate ActiveCampaign: contacts, deals, campaigns, lists, and automations.
- [Brevo Automation](./brevo-automation/) - Automate Brevo: contacts, email campaigns, transactional emails, and lists.
- [ConvertKit Automation](./convertkit-automation/) - Automate ConvertKit (Kit): subscribers, tags, sequences, broadcasts, and forms.
- [Klaviyo Automation](./klaviyo-automation/) - Automate Klaviyo: profiles, lists, segments, campaigns, and events.
- [Mailchimp Automation](./mailchimp-automation/) - Automate Mailchimp: audiences, campaigns, templates, segments, and reports.

**Support & Helpdesk**
- [Freshdesk Automation](./freshdesk-automation/) - Automate Freshdesk: tickets, contacts, agents, groups, and canned responses.
- [Freshservice Automation](./freshservice-automation/) - Automate Freshservice: tickets, assets, changes, problems, and service catalog.
- [Help Scout Automation](./helpdesk-automation/) - Automate Help Scout: conversations, customers, mailboxes, and tags.
- [Zendesk Automation](./zendesk-automation/) - Automate Zendesk: tickets, users, organizations, search, and macros.

**E-commerce & Payments**
- [Shopify Automation](./shopify-automation/) - Automate Shopify: products, orders, customers, inventory, and GraphQL queries.
- [Square Automation](./square-automation/) - Automate Square: payments, customers, catalog, orders, and locations.
- [Stripe Automation](./stripe-automation/) - Automate Stripe: charges, customers, products, subscriptions, and refunds.

**Design & Collaboration**
- [Canva Automation](./canva-automation/) - Automate Canva: designs, templates, assets, folders, and brand kits.
- [Confluence Automation](./confluence-automation/) - Automate Confluence: pages, spaces, search, CQL, labels, and versions.
- [DocuSign Automation](./docusign-automation/) - Automate DocuSign: envelopes, templates, signing, and document management.
- [Figma Automation](./figma-automation/) - Automate Figma: files, components, comments, projects, and team management.
- [Miro Automation](./miro-automation/) - Automate Miro: boards, sticky notes, shapes, connectors, and items.
- [Webflow Automation](./webflow-automation/) - Automate Webflow: CMS collections, items, sites, publishing, and assets.

**Analytics & Data**
- [Amplitude Automation](./amplitude-automation/) - Automate Amplitude: events, cohorts, user properties, and analytics queries.
- [Google Analytics Automation](./google-analytics-automation/) - Automate Google Analytics: reports, dimensions, metrics, and property management.
- [Mixpanel Automation](./mixpanel-automation/) - Automate Mixpanel: events, funnels, cohorts, annotations, and JQL queries.
- [PostHog Automation](./posthog-automation/) - Automate PostHog: events, persons, feature flags, insights, and annotations.
- [Segment Automation](./segment-automation/) - Automate Segment: sources, destinations, tracking, and warehouse connections.

**HR & People**
- [BambooHR Automation](./bamboohr-automation/) - Automate BambooHR: employees, time off, reports, and directory management.

**Automation Platforms**
- [Make Automation](./make-automation/) - Automate Make (Integromat): scenarios, connections, and execution management.

**Zoom & Meetings**
- [Zoom Automation](./zoom-automation/) - Automate Zoom: meetings, recordings, participants, webinars, and reports.

## Getting Started

### Using Skills in Claude.ai

1. Click the skill icon (🧩) in your chat interface.
2. Add skills from the marketplace or upload custom skills.
3. Claude automatically activates relevant skills based on your task.

### Using Skills in Claude Code

1. Place the skill in `~/.config/claude-code/skills/`:
   ```bash
   mkdir -p ~/.config/claude-code/skills/
   cp -r skill-name ~/.config/claude-code/skills/
   ```

2. Verify skill metadata:
   ```bash
   head ~/.config/claude-code/skills/skill-name/SKILL.md
   ```

3. Start Claude Code:
   ```bash
   claude
   ```

4. The skill loads automatically and activates when relevant.

### Using Skills via API

Use the Claude Skills API to programmatically load and manage skills:

```python
import anthropic

client = anthropic.Anthropic(api_key="your-api-key")

response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    skills=["skill-id-here"],
    messages=[{"role": "user", "content": "Your prompt"}]
)
```

See the [Skills API documentation](https://docs.claude.com/en/api/skills-guide) for details.

## Creating Skills

### Skill Structure

Each skill is a folder containing a `SKILL.md` file with YAML frontmatter:

```
skill-name/
├── SKILL.md          # Required: Skill instructions and metadata
├── scripts/          # Optional: Helper scripts
├── templates/        # Optional: Document templates
└── resources/        # Optional: Reference files
```

### Basic Skill Template

```markdown
---
name: my-skill-name
description: A clear description of what this skill does and when to use it.
---

# My Skill Name

Detailed description of the skill's purpose and capabilities.

## When to Use This Skill

- Use case 1
- Use case 2
- Use case 3

## Instructions

[Detailed instructions for Claude on how to execute this skill]

## Examples

[Real-world examples showing the skill in action]
```

### Skill Best Practices

- Focus on specific, repeatable tasks
- Include clear examples and edge cases
- Write instructions for Claude, not end users
- Test across Claude.ai, Claude Code, and API
- Document prerequisites and dependencies
- Include error handling guidance

## Contributing

We welcome contributions! Please read our [Contributing Guidelines](CONTRIBUTING.md) for details on:

- How to submit new skills
- Skill quality standards
- Pull request process
- Code of conduct

### Quick Contribution Steps

1. Ensure your skill is based on a real use case
2. Check for duplicates in existing skills
3. Follow the skill structure template
4. Test your skill across platforms
5. Submit a pull request with clear documentation

## Resources

### Official Documentation

- [Claude Skills Overview](https://www.anthropic.com/news/skills) - Official announcement and features
- [Skills User Guide](https://support.claude.com/en/articles/12512180-using-skills-in-claude) - How to use skills in Claude
- [Creating Custom Skills](https://support.claude.com/en/articles/12512198-creating-custom-skills) - Skill development guide
- [Skills API Documentation](https://docs.claude.com/en/api/skills-guide) - API integration guide
- [Agent Skills Blog Post](https://anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) - Engineering deep dive

### Community Resources

- [Anthropic Skills Repository](https://github.com/anthropics/skills) - Official example skills
- [Claude Community](https://community.anthropic.com) - Discuss skills with other users
- [Skills Marketplace](https://claude.ai/marketplace) - Discover and share skills

### Inspiration & Use Cases

- [Lenny's Newsletter](https://www.lennysnewsletter.com/p/everyone-should-be-using-claude-code) - 50 ways people use Claude Code
- [Notion Skills](https://www.notion.so/notiondevs/Notion-Skills-for-Claude-28da4445d27180c7af1df7d8615723d0) - Notion integration skills


## Join the Community

- [Join our Discord](https://discord.com/invite/composio) - Chat with other developers building Claude Skills
- [Follow on Twitter/X](https://x.com/composio) - Stay updated on new skills and features
- Questions? [support@composio.dev](mailto:support@composio.dev)

---

<p align="center">
  <b>Join 20,000+ developers building agents that ship</b>
</p>

<p align="center">
  <a href="https://platform.composio.dev/?utm_source=Github&utm_content=AwesomeSkills">
    <img src="https://img.shields.io/badge/Get_Started_Free-4F46E5?style=for-the-badge" alt="Get Started"/>
  </a>
</p>

## License

This repository is licensed under the Apache License 2.0.

Individual skills may have different licenses - please check each skill's folder for specific licensing information.

---

**Note**: Claude Skills work across Claude.ai, Claude Code, and the Claude API. Once you create a skill, it's portable across all platforms, making your workflows consistent everywhere you use Claude.

- [AgentsKB](https://agentskb.com) - Upgrade your AI with researched answers. We did the research so your AI gets it right the first time.
