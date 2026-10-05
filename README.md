<h1 align="center">Awesome Claude Skills</h1>

<p align="center">
<a href="https://dashboard.composio.dev/login?utm_source=Github&utm_medium=Youtube&utm_campaign=2025-11&utm_content=AwesomeSkills">
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

A comprehensive and curated list of 1000+ production ready and practical Claude Skills and Plugins for enhancing productivity across usecases on not just Claude.ai, Claude Code, but also across coding agents like Codex, Cursor, Gemini CLI, Antigravity and more.

## Give your skills real-world actions

Skills tell your agent **how** to work. An MCP Gateway gives it secure access to the tools it needs.

Composio [MCP Gateway](https://composio.dev/mcp-gateway) provides a single MCP endpoint for 1,000+ integrations with built-in authentication, team-based access controls, audit logs, and production-ready reliability.

---

## Quickstart: Connect Claude to 1000+ Apps

The **connect-apps** plugin lets Claude perform real actions - send emails, create issues, post to Slack. It handles auth and connects to 1000+ apps using Composio under the hood.

### 1. Install the Plugin

```bash
claude --plugin-dir ./connect-apps-plugin
```

### 2. Run Setup

```
/connect-apps:setup
```

Paste your API key when asked. (Get a free key at [dashboard.composio.dev](https://dashboard.composio.dev/login?utm_source=Github&utm_content=AwesomeSkills))

### 3. Restart & Try It

```bash
exit
claude
```

> **Want skills that do more than generate text?** Claude can send emails, create issues, post to Slack, and take actions across 1000+ apps. [See how →](./connect/)

If you receive the email, Claude is now connected to 1000+ apps.

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

Claude Skills are reusable instruction packages that teach an AI agent how to handle a specific class of tasks. Each skill is a folder containing a `SKILL.md` file with YAML frontmatter (name, description) and Markdown instructions, optionally bundled with scripts, references, and assets. Anthropic introduced the format in October 2025 and released it as an [open standard](https://github.com/anthropics/skills) in December 2025; it's now supported by Claude Code, Claude.ai, the Claude API, OpenAI Codex, Cursor, Gemini CLI, Antigravity, and Windsurf.

Skills load progressively. At session start, the agent sees only each skill's name and description — roughly 100 tokens per skill. The full SKILL.md body (typically under 5,000 tokens) loads only when the agent decides the skill is relevant to the current task. Auxiliary files in `scripts/` and `references/` load on demand. This is what lets a single agent host hundreds of skills without bloating its context window.

Skills are not MCP servers and not tools. MCP defines how an agent connects to external systems — auth, transport, tool discovery. Tools are the individual functions an agent invokes. Skills define the workflow — what to do, in what order, with what guardrails — once the agent has the connections and tools it needs. In production, all three layers run together: MCP for access, tools for actions, skills for behavior.

## Skills

### Document Processing

- [docx](https://github.com/anthropics/skills/tree/main/skills/docx) - Create, edit, analyze Word docs with tracked changes, comments, formatting.
- [pdf](https://github.com/anthropics/skills/tree/main/skills/pdf) - Extract text, tables, metadata, merge & annotate PDFs.
- [pptx](https://github.com/anthropics/skills/tree/main/skills/pptx) - Read, generate, and adjust slides, layouts, templates.
- [xlsx](https://github.com/anthropics/skills/tree/main/skills/xlsx) - Spreadsheet manipulation: formulas, charts, data transformations.
- [Markdown to EPUB Converter](https://github.com/smerchek/claude-epub-skill) - Converts markdown documents and chat summaries into professional EPUB ebook files. *By [@smerchek](https://github.com/smerchek)*
- [Master Claude for Legal](https://github.com/sboghossian/master-claude-for-legal) - Skill pack for legal teams. NDA triage, multi-party version diff, citation verifier, meeting brief, and the Friday-newsletter status synthesis pattern. Includes 10 reference docs (privilege, verification, long documents, practice areas) and 3 firm templates. Built from the public Anthropic Claude for Legal Teams webinar dataset. *By [@sboghossian](https://github.com/sboghossian)*
- [Document Content Search](https://github.com/ninggui/document-content-search) - 按内容片段找回用户文档：ima 检索 + 飞书全文检索 + 下载提取正文。 *By [@ninggui](https://github.com/ninggui)*
- [ima Knowledge Base](https://github.com/ninggui/ima-knowledge-base) - 腾讯 ima 知识库 API 操作：搜索、读取、检索品牌研报与订阅库内容。 *By [@ninggui](https://github.com/ninggui)*

### Development & Code Tools

- [artifacts-builder](https://github.com/anthropics/skills/tree/main/skills/web-artifacts-builder) - Suite of tools for creating elaborate, multi-component claude.ai HTML artifacts using modern frontend web technologies (React, Tailwind CSS, shadcn/ui).
- [aws-skills](https://github.com/zxkane/aws-skills) - AWS development with CDK best practices, cost optimization MCP servers, and serverless/event-driven architecture patterns.
- [building-blog](https://github.com/BuildShipGrowRepeat/nextjs-sanity-blog-skill) - Adds an SEO-first, i18n-ready blog to a Next.js + Sanity site via a 40-question intake, a one-page plan, and a 20-section spec. Includes a generator for AI hero images via Gemini 3 Pro Image (Nano Banana Pro). *By [@BuildShipGrowRepeat](https://github.com/BuildShipGrowRepeat)*
- [Changelog Generator](./changelog-generator/) - Automatically creates user-facing changelogs from git commits by analyzing history and transforming technical commits into customer-friendly release notes.
- [Chrome Relay](https://chrome-relay.kushalsm.com/) - Drives the user's already-open Chrome session — cookies, SSO, extensions, localhost — through a local CLI bridge. Real-Chrome counterpart to Playwright Browser Automation; install via `npx skills add chrome-relay` + a [Chrome Web Store extension](https://chromewebstore.google.com/detail/chrome-relay/cpdiapbifblhlcpnmlmfpgfjlacebokb). No remote relay, no Playwright fixtures, no MCP server needed.
- [Claude Code Terminal Title](https://github.com/bluzername/claude-code-terminal-title) - Gives each Claud-Code terminal window a dynamic title that describes the work being done so you don't lose track of what window is doing what.
- [Connect](./connect/) - Connect Claude to any app. Send emails, create issues, post messages, update databases - take real actions across Gmail, Slack, GitHub, Notion, and 1000+ services.
- [D3.js Visualization](https://github.com/chrisvoncsefalvay/claude-d3js-skill) - Teaches Claude to produce D3 charts and interactive data visualizations. *By [@chrisvoncsefalvay](https://github.com/chrisvoncsefalvay)*
- [FFUF Web Fuzzing](https://github.com/jthack/ffuf_claude_skill) - Integrates the ffuf web fuzzer so Claude can run fuzzing tasks and analyze results for vulnerabilities. *By [@jthack](https://github.com/jthack)*
- [finishing-a-development-branch](https://github.com/obra/superpowers/tree/main/skills/finishing-a-development-branch) - Guides completion of development work by presenting clear options and handling chosen workflow.
- [Full-Page Screenshot](https://github.com/LewisLiu007/full-page-screenshot) - Captures full-page screenshots of web pages via Chrome DevTools Protocol with zero dependencies. *By [@LewisLiu007](https://github.com/LewisLiu007)*
- [great_cto](https://github.com/avelikiy/great_cto) - Claude Code plugin: 7 specialised subagents (tech-lead, senior-dev, qa-engineer, security-officer, devops, l3-support, project-auditor) orchestrating a full SDLC pipeline — architecture, TDD, 12-angle code review, QA, security audit, deploy. 11 project archetypes auto-detected, 13 compliance frameworks (GDPR/PCI-DSS/HIPAA/SOC2/ISO 27001), self-improving knowledge layer that learns from every incident. *By [@avelikiy](https://github.com/avelikiy)*
- [iOS Simulator](https://github.com/conorluddy/ios-simulator-skill) - Enables Claude to interact with iOS Simulator for testing and debugging iOS applications. *By [@conorluddy](https://github.com/conorluddy)*
- [jules](https://github.com/sanjay3290/ai-skills/tree/main/skills/jules) - Delegate coding tasks to Google Jules AI agent for async bug fixes, documentation, tests, and feature implementation on GitHub repos. *By [@sanjay3290](https://github.com/sanjay3290)*
- [LangSmith Fetch](./langsmith-fetch/) - Debug LangChain and LangGraph agents by automatically fetching and analyzing execution traces from LangSmith Studio. First AI observability skill for Claude Code. *By [@OthmanAdi](https://github.com/OthmanAdi)*
- [lean-ctx](https://github.com/yvgude/lean-ctx) - MCP server and context runtime for AI coding agents: session caching, AST-aware compression, and 90+ shell patterns to reduce token usage. Supports Claude Code, Cursor, Copilot, and other integrations. Install the Claude Code skill with `lean-ctx init --agent claude-code`; docs at [leanctx.com](https://leanctx.com). *By [@yvgude](https://github.com/yvgude)*
- [MCP Builder](./mcp-builder/) - Guides creation of high-quality MCP (Model Context Protocol) servers for integrating external APIs and services with LLMs using Python or TypeScript.
- [move-code-quality-skill](https://github.com/1NickPappas/move-code-quality-skill) - Analyzes Move language packages against the official Move Book Code Quality Checklist for Move 2024 Edition compliance and best practices.
- [OpenWeb](https://github.com/openweb-org/openweb) - Agent-native way to access any website. Calls the same APIs the website calls (JSON in, JSON out) with auth (cookies, JWT, CSRF, signing) auto-resolved per request. 90+ sites built in. *By [@openweb-org](https://github.com/openweb-org)*
- [overkill](https://github.com/santiago-vargas-de-kruijf/claude-overkill) - Surfaces advanced, maximalist alternatives to whatever solution is being discussed — advanced data structures, distributed-systems algorithms, niche frameworks, design patterns, and frontier tooling — each ranked on a calibrated complexity scale with learning links and the scenario in which the path pays off. *By [@santiago-vargas-de-kruijf](https://github.com/santiago-vargas-de-kruijf)*
- [Playwright Browser Automation](https://github.com/lackeyjb/playwright-skill) - Model-invoked Playwright automation for testing and validating web applications. *By [@lackeyjb](https://github.com/lackeyjb)*
- [prompt-engineering](https://github.com/NeoLabHQ/context-engineering-kit/tree/master/plugins/customaize-agent/skills/prompt-engineering) - Teaches well-known prompt engineering techniques and patterns, including Anthropic best practices and agent persuasion principles.
- [pypict-claude-skill](https://github.com/omkamal/pypict-claude-skill) - Design comprehensive test cases using PICT (Pairwise Independent Combinatorial Testing) for requirements or code, generating optimized test suites with pairwise coverage.
- [reddit-fetch](https://github.com/ykdojo/claude-code-tips/tree/main/skills/reddit-fetch) - Fetches Reddit content via Gemini CLI when WebFetch is blocked or returns 403 errors.
- [Septim Agents Pack](https://septimlabs.com/tools/agents?utm_source=awesome-claude-skills&utm_medium=awesome-list&utm_campaign=oss-backlink) - 10 named Claude Code sub-agents (Atlas, Luca, Canon, Ember, Tally, Nova, Ward, Mira, Juno, Pip) covering planning, architecture, brand, marketing, finance, design, legal, customer, research, and coordination. Drop into `.claude/agents/`. *By [@septimlabs-code](https://github.com/septimlabs-code)*
- [Skill Creator](./skill-creator/) - Provides guidance for creating effective Claude Skills that extend capabilities with specialized knowledge, workflows, and tool integrations.
- [Skill Seekers](https://github.com/yusufkaraaslan/Skill_Seekers) - Automatically converts any documentation website into a Claude AI skill in minutes. *By [@yusufkaraaslan](https://github.com/yusufkaraaslan)*
- [software-architecture](https://github.com/NeoLabHQ/context-engineering-kit/tree/master/plugins/ddd/skills/software-architecture) - Implements design patterns including Clean Architecture, SOLID principles, and comprehensive software design best practices.
- [subagent-driven-development](https://github.com/NeoLabHQ/context-engineering-kit/tree/master/plugins/sadd/skills/subagent-driven-development) - Dispatches independent subagents for individual tasks with code review checkpoints between iterations for rapid, controlled development.
- [test-driven-development](https://github.com/obra/superpowers/tree/main/skills/test-driven-development) - Use when implementing any feature or bugfix, before writing implementation code.
- [using-git-worktrees](https://github.com/obra/superpowers/blob/main/skills/using-git-worktrees/) - Creates isolated git worktrees with smart directory selection and safety verification.
- [Webapp Testing](./webapp-testing/) - Tests local web applications using Playwright for verifying frontend functionality, debugging UI behavior, and capturing screenshots.
- [Bilibili API Patterns](https://github.com/ninggui/bilibili-api-patterns) - B站 API 抓取模式：feed 聚合、cookie 坑、anti-412 处理。 *By [@ninggui](https://github.com/ninggui)*
- [Cron Timezone Pitfall](https://github.com/ninggui/cron-timezone-pitfall) - Cron 时区陷阱排查：调度器用 UTC 导致北京时间错位 8 小时的根因与修复。 *By [@ninggui](https://github.com/ninggui)*
- [Docker Container Ops](https://github.com/ninggui/docker-container-ops) - Docker 容器运维速查：exec/cp/restart、只读挂载修改、config 热更新。 *By [@ninggui](https://github.com/ninggui)*
- [External Skill Adoption](https://github.com/ninggui/external-skill-adoption) - 评估外部插件/技能并决定是否采纳：学习 X 插件、比选 GitHub skill。 *By [@ninggui](https://github.com/ninggui)*
- [Hermes Config Workflow](https://github.com/ninggui/hermes-config-workflow) - 查看/设置/更新 Hermes config.yaml：web 后端、provider keys、平台工具集、agent 选项。 *By [@ninggui](https://github.com/ninggui)*
- [n8n Dify DeepSeek Workflow](https://github.com/ninggui/n8n-dify-deepseek-workflow) - n8n + Dify + DeepSeek 最小闭环工作流：节点选择、MCP 集成、记忆系统、实战链路。 *By [@ninggui](https://github.com/ninggui)*

### Data & Analysis

- [CSV Data Summarizer](https://github.com/coffeefuelbump/csv-data-summarizer-claude-skill) - Automatically analyzes CSV files and generates comprehensive insights with visualizations without requiring user prompts. *By [@coffeefuelbump](https://github.com/coffeefuelbump)*
- [deep-research](https://github.com/sanjay3290/ai-skills/tree/main/skills/deep-research) - Execute autonomous multi-step research using Gemini Deep Research Agent for market analysis, competitive landscaping, and literature reviews. *By [@sanjay3290](https://github.com/sanjay3290)*
- [postgres](https://github.com/sanjay3290/ai-skills/tree/main/skills/postgres) - Execute safe read-only SQL queries against PostgreSQL databases with multi-connection support and defense-in-depth security. *By [@sanjay3290](https://github.com/sanjay3290)*
- [recursive-research](https://github.com/Anjos2/recursive-research) - Recursive research up to PhD level across any domain (science, tech, business, arts, humanities) with source tiering, WDM + Munger inversion for autonomous decisions, and disk checkpointing to survive context compaction. *By [@Anjos2](https://github.com/Anjos2)*
- [root-cause-tracing](https://github.com/obra/superpowers/tree/main/skills/root-cause-tracing) - Use when errors occur deep in execution and you need to trace back to find the original trigger.
- [Call Recording Analysis](https://github.com/ninggui/call-recording-analysis-system) - 批量转写与分析通话录音：飞书妙记转写、按联系人归档、人物画像/意图风险/复盘、知识库沉淀。 *By [@ninggui](https://github.com/ninggui)*
- [EV News Briefing](https://github.com/ninggui/ev-news-briefing) - 新能源行业早报自动化：定时推送、行业新闻摘要。 *By [@ninggui](https://github.com/ninggui)*
- [Travel Deal Research](https://github.com/ninggui/travel-deal-research) - 机票/酒店/火车比价与盯价，含往返组合计算与特殊线路处理。 *By [@ninggui](https://github.com/ninggui)*
- [Web Intelligence Reports](https://github.com/ninggui/web-intelligence-reports) - web 检索情报→验证→生成结构化报告→发布飞书文档：舆情监控、品牌分析、竞品调研。 *By [@ninggui](https://github.com/ninggui)*

### Business & Marketing

- [Brand Build Skills](https://github.com/rampstackco/claude-skills) - 59-skill library covering the full website lifecycle: brand, design, content, SEO, dev, ops, growth, and research. Stack-agnostic with an Ahrefs MCP-powered SEO audit suite. Includes a meta-skill for writing your own. *By [@rampstackco](https://github.com/rampstackco)*
- [Brand Guidelines](./brand-guidelines/) - Applies Anthropic's official brand colors and typography to artifacts for consistent visual identity and professional design standards.
- [Competitive Ads Extractor](./competitive-ads-extractor/) - Extracts and analyzes competitors' ads from ad libraries to understand messaging and creative approaches that resonate.
- [Domain Name Brainstormer](./domain-name-brainstormer/) - Generates creative domain name ideas and checks availability across multiple TLDs including .com, .io, .dev, and .ai extensions.
- [Internal Comms](./internal-comms/) - Helps write internal communications including 3P updates, company newsletters, FAQs, status reports, and project updates using company-specific formats.
- [Lead Research Assistant](./lead-research-assistant/) - Identifies and qualifies high-quality leads by analyzing your product, searching for target companies, and providing actionable outreach strategies.
- [Automotive Job Hunting Framework](https://github.com/ninggui/automotive-job-hunting-framework) - 新能源汽车求职定位与面试框架：主机厂JD拆解、STAR应答、简历分品牌优化、求职行动清单。 *By [@ninggui](https://github.com/ninggui)*
- [Brand Style Research](https://github.com/ninggui/brand-style-research) - 研究品牌风格/文化/体系/KOL表达时使用，以品牌为主体产出全景文档。 *By [@ninggui](https://github.com/ninggui)*
- [Douyin Real Estate Research](https://github.com/ninggui/douyin-realestate-research) - 抖音平台自动化与房产推广：能力地图、平台风控、推广路径。 *By [@ninggui](https://github.com/ninggui)*
- [KOL Content Research](https://github.com/ninggui/kol-content-research) - 深度学习/研究某博主帖子：定位账号→全量拉取→内涵提炼（观点/方法论）。 *By [@ninggui](https://github.com/ninggui)*
- [XHS Style Imitation](https://github.com/ninggui/xhs-style-imitation) - 小红书风格模仿写作：分析原笔记风格指纹，按指纹写新文章。 *By [@ninggui](https://github.com/ninggui)*
- [Xiaohongshu Account Operations](https://github.com/ninggui/xiaohongshu-account-operations) - 小红书账号评论运营框架：LLM 评论生成（去AI味前置）、频率安全、自动停轮降频、质量闭环。 *By [@ninggui](https://github.com/ninggui)*
- [Xiaohongshu Comment Leads](https://github.com/ninggui/xiaohongshu-comment-leads) - 小红书评论区引流策略：关键词搜索、评论话术去AI味、频率风控、被 ban 处置。 *By [@ninggui](https://github.com/ninggui)*

### Communication & Writing

- [article-extractor](https://github.com/michalparkola/tapestry-skills-for-claude-code/tree/main/article-extractor) - Extract full article text and metadata from web pages.
- [brainstorming](https://github.com/obra/superpowers/tree/main/skills/brainstorming) - Transform rough ideas into fully-formed designs through structured questioning and alternative exploration.
- [Content Research Writer](./content-research-writer/) - Assists in writing high-quality content by conducting research, adding citations, improving hooks, and providing section-by-section feedback.
- [family-history-research](https://github.com/emaynard/claude-family-history-research-skill) - Provides assistance with planning family history and genealogy research projects.
- [Meeting Insights Analyzer](./meeting-insights-analyzer/) - Analyzes meeting transcripts to uncover behavioral patterns including conflict avoidance, speaking ratios, filler words, and leadership style.
- [NotebookLM Integration](https://github.com/PleasePrompto/notebooklm-skill) - Lets Claude Code chat directly with NotebookLM for source-grounded answers based exclusively on uploaded documents. *By [@PleasePrompto](https://github.com/PleasePrompto)*
- [Twitter Algorithm Optimizer](./twitter-algorithm-optimizer/) - Analyze and optimize tweets for maximum reach using Twitter's open-source algorithm insights. Rewrite and edit tweets to improve engagement and visibility.
- [Humanizer-zh](https://github.com/ninggui/humanizer-zh) - 去除中文文本中的 AI 生成痕迹，使其自然如真人书写，保留事实与作者声音。 *By [@ninggui](https://github.com/ninggui)*

### Creative & Media

- [anydesign](https://github.com/uxKero/anydesign) - Analyzes any image, URL, or Figma file and generates a structured `design.md` with the full design system, component inventory, and reconstruction notes — portable to v0, Lovable, Cursor or any AI builder. *By [@uxKero](https://github.com/uxKero)*
- [Canvas Design](./canvas-design/) - Creates beautiful visual art in PNG and PDF documents using design philosophy and aesthetic principles for posters, designs, and static pieces.
- [imagen](https://github.com/sanjay3290/ai-skills/tree/main/skills/imagen) - Generate images using Google Gemini's image generation API for UI mockups, icons, illustrations, and visual assets. *By [@sanjay3290](https://github.com/sanjay3290)*
- [Image Enhancer](./image-enhancer/) - Improves image and screenshot quality by enhancing resolution, sharpness, and clarity for professional presentations and documentation.
- [Slack GIF Creator](./slack-gif-creator/) - Creates animated GIFs optimized for Slack with validators for size constraints and composable animation primitives.
- [Theme Factory](./theme-factory/) - Applies professional font and color themes to artifacts including slides, docs, reports, and HTML landing pages with 10 pre-set themes.
- [Video Downloader](./video-downloader/) - Downloads videos from YouTube and other platforms for offline viewing, editing, or archival with support for various formats and quality options.
- [youtube-transcript](https://github.com/michalparkola/tapestry-skills-for-claude-code/tree/main/youtube-transcript) - Fetch transcripts from YouTube videos and prepare summaries.
- [swiftui-design-skill](https://github.com/wholiver/swiftui-design-skill) - SwiftUI 前端设计 skill — 反 AI Slop 六条铁律、设计方向顾问、品牌资产协议、五维评审。支持 Claude Code / Cursor / Codex / OpenCode 等全部 AI agent 平台。 *By [@wholiver](https://github.com/wholiver)*
- [Pixelbin-Media-Generation](https://github.com/anandpareek-hub/pixelbin-claude-skill) - Generate and edit images & videos with 85+ API portfolio and build visually appealing website pages
- [Media Resource Automation](https://github.com/ninggui/media-resource-automation) - 影视资源自动化：资源站搜片/提取磁力→网盘离线缓存→在线观看。 *By [@ninggui](https://github.com/ninggui)*
- [Movie Resource Automation](https://github.com/ninggui/movie-resource-automation) - 电影资源站自动搜索筛选磁力链接：登录→筛选→API 提取磁力→115/qBittorrent 缓存。 *By [@ninggui](https://github.com/ninggui)*

### Productivity & Organization

- [File Organizer](./file-organizer/) - Intelligently organizes files and folders by understanding context, finding duplicates, and suggesting better organizational structures.
- [Invoice Organizer](./invoice-organizer/) - Automatically organizes invoices and receipts for tax preparation by reading files, extracting information, and renaming consistently.
- [kaizen](https://github.com/NeoLabHQ/context-engineering-kit/tree/master/plugins/kaizen/skills/kaizen) - Applies continuous improvement methodology with multiple analytical approaches, based on Japanese Kaizen philosophy and Lean methodology.
- [n8n-skills](https://github.com/haunchen/n8n-skills) - Enables AI assistants to directly understand and operate n8n workflows.
- [Raffle Winner Picker](./raffle-winner-picker/) - Randomly selects winners from lists, spreadsheets, or Google Sheets for giveaways and contests with cryptographically secure randomness.
- [solo-skills](https://github.com/rockscy/solo-skills) - 7 bilingual (EN+中文) skills for solo founders and indie devs: launch tweets, customer emails, decision frameworks, postmortems. Each skill includes an explicit "When NOT to use" section.
- [Tailored Resume Generator](./tailored-resume-generator/) - Analyzes job descriptions and generates tailored resumes that highlight relevant experience, skills, and achievements to maximize interview chances.
- [ship-learn-next](https://github.com/michalparkola/tapestry-skills-for-claude-code/tree/main/ship-learn-next) - Skill to help iterate on what to build or learn next, based on feedback loops.
- [tapestry](https://github.com/michalparkola/tapestry-skills-for-claude-code/tree/main/tapestry) - Interlink and summarize related documents into knowledge networks.
- [Autonomous Problem Solving](https://github.com/ninggui/autonomous-problem-solving) - 遭遇问题先搜索再执行，失败后分析原因，只在确实需要用户介入时才回传。 *By [@ninggui](https://github.com/ninggui)*
- [EV After-sales Knowledge Management](https://github.com/ninggui/ev-after-sales-knowledge-management) - 新能源售后知识管理方法论：三电维修市场数据、培训体系搭建、知识库运营 SOP、AI 落地路径。 *By [@ninggui](https://github.com/ninggui)*
- [Rules Audit](https://github.com/ninggui/guining-rules-audit) - 规则审计：检查近期约定的规则是否已固化到 memory/skill，缺失自动补。 *By [@ninggui](https://github.com/ninggui)*
- [Task Queue Protocol](https://github.com/ninggui/guining-task-queue-protocol) - 用户待办队列协议：高峰时段任务先入队闲时再跑。 *By [@ninggui](https://github.com/ninggui)*
- [Mijia Cloud Control](https://github.com/ninggui/mijia-cloud-control) - 米家智能家居云 API 控制：查设备状态、开关灯、调空调窗帘。 *By [@ninggui](https://github.com/ninggui)*
- [Psycho Career Coach Model](https://github.com/ninggui/psycho-career-coach-model) - 用心理咨询师+职业规划师双角色对语音/聊天记录做全量评估，产出结构化报告链。 *By [@ninggui](https://github.com/ninggui)*
- [Research First Protocol](https://github.com/ninggui/research-first-protocol) - 遇到新领域要求先通盘联网研究再给方法论，避免凭空臆断。 *By [@ninggui](https://github.com/ninggui)*
- [User Rules Audit](https://github.com/ninggui/rules-audit) - 规则审计：检查近期约定的规则是否已固化，缺失自动补。 *By [@ninggui](https://github.com/ninggui)*
- [Session Task Audit](https://github.com/ninggui/session-task-audit) - 盘点最近 N 天对话确认未完成任务。 *By [@ninggui](https://github.com/ninggui)*
- [User Task Queue Protocol](https://github.com/ninggui/task-queue-protocol) - 待办队列协议：高峰时段任务先入队闲时再跑。 *By [@ninggui](https://github.com/ninggui)*

### Collaboration & Project Management

- [git-pushing](https://github.com/mhattingpete/claude-skills-marketplace/tree/main/engineering-workflow-plugin/skills/git-pushing) - Automate git operations and repository interactions.
- [google-workspace-skills](https://github.com/sanjay3290/ai-skills/tree/main/skills) - Suite of Google Workspace integrations: Gmail, Calendar, Chat, Docs, Sheets, Slides, and Drive with cross-platform OAuth. *By [@sanjay3290](https://github.com/sanjay3290)*
- [mercury-mcp](https://www.teamoffsite.ai/proton/docs/skill) - Cheatsheet for the Mercury (Proton) MCP tools. Message agent teammates, manage threads, create tasks, and schedule automations across coordinated agent teams. *By [Mercury](https://mercury.build)*
- [outline](https://github.com/sanjay3290/ai-skills/tree/main/skills/outline) - Search, read, create, and manage documents in Outline wiki instances (cloud or self-hosted). *By [@sanjay3290](https://github.com/sanjay3290)*
- [review-implementing](https://github.com/mhattingpete/claude-skills-marketplace/tree/main/engineering-workflow-plugin/skills/review-implementing) - Evaluate code implementation plans and align with specs.
- [test-fixing](https://github.com/mhattingpete/claude-skills-marketplace/tree/main/engineering-workflow-plugin/skills/test-fixing) - Detect failing tests and propose patches or fixes.

### Security & Systems

- [computer-forensics](https://github.com/mhattingpete/claude-skills-marketplace/tree/main/computer-forensics-skills/skills/computer-forensics) - Digital forensics analysis and investigation techniques.
- [file-deletion](https://github.com/mhattingpete/claude-skills-marketplace/tree/main/computer-forensics-skills/skills/file-deletion) - Secure file deletion and data sanitization methods.
- [metadata-extraction](https://github.com/mhattingpete/claude-skills-marketplace/tree/main/computer-forensics-skills/skills/metadata-extraction) - Extract and analyze file metadata for forensic purposes.
- [threat-hunting-with-sigma-rules](https://github.com/jthack/threat-hunting-with-sigma-rules-skill) - Use Sigma detection rules to hunt for threats and analyze security events.

### Assistive Technology

- [ASD-AuDHD-PAI-Skills](https://github.com/emory/ASD-AuDHD-PAI-Skills) - New collection, first skill [pda-reframing](https://github.com/emory/ASD-AuDHD-PAI-Skills/blob/main/Skills/pda-reframing/SKILL.md) can reframe requests or decisions to defeat Persistent Demand Avoidance flavors of autism spectrum disorders, or people with ADHD that struggle to Start tasks and need help aligning with a task.

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
- [Top Claude Skills](https://composio.dev/content/top-claude-skills)


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
