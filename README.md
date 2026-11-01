# ![Awesome Claude Skills](assets/header.svg)

Find a skill for the task at hand. A community directory for
[Claude Code](https://code.claude.com/docs/en/skills),
[Claude.ai and the API][anthropic-install].

**[Browse skills](#browse-skills)** · [Install your first skill](#quick-start) ·
[Collections](#skill-collections) · [Contribute](CONTRIBUTING.md)

<a id="featured-skills"></a>

## Pick a starting point

| Your next task | Try this |
| --- | --- |
| Extract tables from a PDF | [pdf][pdf] |
| Find why a test keeps failing | [systematic-debugging][debugging] |
| Build a feature with tests first | [test-driven-development][tdd] |
| Create a Word document | [docx][docx] |
| Turn a repeated task into a skill | [skill-creator][creator] |

## Browse skills

| Code | Create | Work |
| --- | --- | --- |
| [Testing](#testing--quality) | [Files](#document--file-processing) | [Workflow](#collaboration--workflow) |
| [Debugging](#debugging--troubleshooting) | [Media](#media--content-creation) | [Data](#data--analysis) |
| [Build apps](#development--architecture) | [Writing](#writing--research) | [Finance & tax](#finance--tax) |
| [Security](#security--performance) | [Skills](#meta-skills) | [Automation](#documentation--automation) |

Skill names link to their source. Read the install guide there before enabling
a skill. Inclusion is not a security audit. Use **Cmd+F** or **Ctrl+F** to search.

<a id="skill-categories"></a>
<a id="-document--file-processing"></a>

### Document & File Processing

| Skill | Use it to |
| --- | --- |
| [cue-omni-reader](https://github.com/sensedeal/cue-skills/tree/main/cue-omni-reader) | Parse documents and web sources into text through the Cue Omni Reader MCP service. |
| [docx][docx] | Create and edit Word documents with tracked changes and comments. |
| [equalang](https://github.com/equalang/equalang-skill) | Translate files or transcribe recordings through Equalang using an API key and credits. |
| [humanpen](https://github.com/humanpen/humanpen-skill) | Rewrite, translate, shorten, and restyle citations in files through paid HumanPen APIs. |
| [mubu-integration](https://github.com/liuboacean/mubu-integration) | Import, export, and organize Mubu outlines and Markdown through an unofficial API. |
| [pdf][pdf] | Extract text and tables, combine PDFs, and fill forms. |
| [pptx][pptx] | Create, edit, and inspect PowerPoint presentations. |
| [rtl-slides](https://github.com/darajoukar/reveal-rtl/tree/main/plugins/reveal-rtl/skills/rtl-slides) | Build right-to-left Persian and Arabic reveal.js presentations with localized digits, Jalali/Hijri dates, and PDF/PNG export. |
| [translate-book](https://github.com/kcy4334-lgtm/translate-book-arxiv) | Translate papers and books with a LaTeX-source route for preserving arXiv equations and tables. |
| [xlsx][xlsx] | Build and edit spreadsheets with formulas and formatting. |

<a id="-testing--quality"></a>

### Testing & Quality

| Skill | Use it to |
| --- | --- |
| [aeo-check](https://github.com/pchewlo/aeo-check/tree/main/.claude/skills/aeo-check) | Lint a site's code or live URL for what blocks AI search and agents, fix findings in framework order, then re-run to confirm. |
| [agent-qa-authoring](https://github.com/vostride/agent-qa/tree/main/skills/agent-qa-authoring) | Author and validate agent-qa tests and IDs; source license restricts competing use. |
| [align](https://github.com/ggrigo/align/tree/main/skills/align) | Collect structured feedback on generated claims in an HTML form and archive corrections for later review. |
| [benchmark-yylo](https://github.com/yylo-dev/yylo-skills/tree/main/skills/benchmark-yylo) | Prepare reusable cases, compare models/harnesses and independently evaluate retained outputs. |
| [checkup](https://github.com/agentvitals/checkup/tree/main/checkup) | Run hosted probes and retrieve server-scored results; full mode uploads approved conversation logs. |
| [clousd](https://github.com/Clousd-Android/clousd-sdk/tree/main/skills/clousd) | Test Android apps on cloud phones: run plain-language tasks or drive the screen step by step. |
| [crosscheck](https://github.com/moveju112/skill_verify/tree/main/skills/crosscheck) | Compare independent Claude and Codex analysis, reconcile findings, and verify completed work. |
| [design-fidelity-verify](https://github.com/jeltehomminga/figma-design-skills/tree/main/skills/design-fidelity-verify) | Compare measured values in a running app with a Figma design specification. |
| [fresh-review](https://github.com/roman-s8o/workflow-pack-free/tree/main/.claude/skills/fresh-review) | Review code or a plan against acceptance criteria with an agent that has not seen the conversation, then label each finding. |
| [ironloop](https://github.com/edouard-claude/ironloop/tree/main/skills/engineering/ironloop) | Plan Rust work through specifications, tests, simulation, and authorized security checks. |
| [never-again](https://github.com/malaysherasia-ai/claude-never-again/tree/main/skills/never-again) | Capture repaired bugs as enforceable hooks or brief lessons for future sessions. |
| [pdp-audit](https://github.com/llizell/pdp-audit) | Audit ecommerce product pages with desktop/mobile evidence and prioritized UX findings. |
| [playwright-expert](https://github.com/jeffallan/claude-skills/tree/main/skills/playwright-expert) | Write and debug Playwright browser tests with fixtures, page objects, visual checks, and CI integration. |
| [prove-it-ran](https://github.com/agentkitco/agentkit-dev-skills/tree/main/skills/prove-it-ran) | Show evidence that tests and builds actually ran and covered the change before calling work done. |
| [sim (interview-sim)](https://github.com/chrisjacksonn/interview-sim/tree/main/skills/sim) | Practice timed coding interviews with script-managed clocks and hidden-test grading. |
| [test-checklist](https://github.com/Ifeanyiejindu/qarunbook/tree/main/plugins/qarunbook/skills/test-checklist) | Derive a QA plan from app code with steps and expected results for each platform. |
| [test-driven-development][tdd] | Write a failing test, implement the change, then refactor. |
| [test-master](https://github.com/jeffallan/claude-skills/tree/main/skills/test-master) | Plan and implement unit, integration, performance, and security tests with coverage and defect analysis. |
| [webapp-testing][webapp-testing] | Exercise a local web app with Playwright and inspect its behavior. |
| [what-could-break](https://github.com/stas4000/what-could-break/tree/main/what-could-break) | Trace a change through consumers, stored data and duplicated rules, then design a concrete check for the critical assumption. |
| [wreck-it](https://github.com/miyannishar/wreck-it/tree/main/skills/wreck-it) | Test a local web app like real users and chaos monkeys, then report reproduced bugs with screenshots, source locations and regression tests. |

<a id="-debugging--troubleshooting"></a>

### Debugging & Troubleshooting

| Skill | Use it to |
| --- | --- |
| [agenttrace-session-audit](https://github.com/luoyuctl/agenttrace) | Inspect agent sessions for cost, tokens, failures, and latency. |
| [debugging-wizard](https://github.com/jeffallan/claude-skills/tree/main/skills/debugging-wizard) | Reproduce failures, test hypotheses, identify root causes, and verify fixes. |
| [solidping-monitoring](https://github.com/fclairamb/solidping-plugin/tree/main/skills/solidping-monitoring) | Find why an uptime check fails, read incidents, and add checks through the SolidPing MCP server. |
| [systematic-debugging][debugging] | Investigate a bug's cause before attempting a fix. |
| [verification-before-completion][verification] | Run checks and inspect their output before calling work done. |

<a id="-collaboration--workflow"></a>

### Collaboration & Workflow

| Skill | Use it to |
| --- | --- |
| [a2ui-ask](https://github.com/YuniqueUnic/a2ui-ask) | Collect structured user input through a browser form and JSON answer files. |
| [ai-agency-os-starter](https://github.com/CalebAnderson-Coder/ai-agency-os-starter) | Keep each client's voice, claims and scope isolated, and check client requests against the SOW before doing unbilled work. |
| [ai-code-review-triage](https://github.com/laulauraluo/ai-code-review-triage/tree/main/skills/ai-code-review-triage) | Review AI-written PRs in three passes: fresh-context bug hunt, context checks (units, history, callers), and a scoped sign-off. |
| [ai-meeting](https://github.com/bin1874/ai-meeting-skill/tree/main/ai-meeting) | Run structured proposal reviews with CLI agents and preserve each agent session between rounds. |
| [ax-extract-workflow](https://github.com/Necmttn/ax) | Reconstruct a shipped feature's workflow from local ax session history. |
| [before-you-build](https://github.com/bin1874/before-you-build-skill) | Check demand, distribution, scope, and failure risks before building a product or feature. |
| [brainstorming][brainstorming] | Work through requirements and design choices before implementation. |
| [breather](https://github.com/ilandahan/breather/tree/main/skills/breather) | Offer session stopping points with attended-time context and a written handoff. |
| [call-me](https://github.com/radres/call-me/tree/main/skill) | Call or text the user's iPhone to ask or report, then act on the reply; needs the paid /call-me iPhone app. |
| [clueless](https://github.com/ADanMan/clueless/tree/main/skills/clueless) | Name assumptions, irreversible steps, and review gaps when a user needs extra guidance. |
| [communication-protocol-setup](https://github.com/cez0060405/communication-protocol-setup) | Agree on assistant communication preferences and export a reusable protocol. |
| [cooper-email](https://github.com/cooper-email/cooper-email/tree/main/skills/cooper-email) | Send, read, and search mail from the agent's own inbox, and wait for replies or verification codes, through Cooper Email MCP or HTTP. |
| [delegate](https://github.com/aayushpokhrel1/delegation-pipeline/tree/master/skills/delegate) | Delegate a precisely specified coding task to a worker, then review its diff and tests. |
| [dialog-tree](https://github.com/ikotelkin/claude-skills/tree/main/skills/dialog-tree) | Track conversation branches in an interactive dialogue tree. |
| [executing-plans][executing-plans] | Carry out an implementation plan with review checkpoints. |
| [fabling](https://github.com/gncdev/fabling/tree/main/fabling) | Apply a work profile for proportionate investigation, visual checks, and task completion. |
| [finishing-a-development-branch][finishing] | Decide how to integrate finished work and clean up the branch. |
| [forward-deployed-selling](https://github.com/vonarmen-wq/forward-deployed-selling) | Structure enterprise sales discovery, stakeholder analysis, deal qualification, and account plans. |
| [golden-frijoles](https://github.com/danybgoode/golden-frijoles) | Turn ideas into bets with a target and read date, ship them behind flags and A/B tests, and report whether each paid off. |
| [guashuai / junshi](https://github.com/DENGYUFAN0/guashuai-junshi/tree/main/adapters/claude-code/skills) | Coordinate model tiers with either an orchestrator or an occasional expert advisor. |
| [guided-goal](https://github.com/luchasarie/guided-goal/tree/main/skills/guided-goal) | Turn rough intent into a completion contract with success criteria, verification, boundaries and stop conditions before work starts. |
| [karpathy-guidelines](https://github.com/swarmclawai/andrej-karpathy-skills/tree/main/skills/karpathy-guidelines) | Surface assumptions, keep coding changes small, and define checks before implementation. |
| [kgai knowledge-graph](https://github.com/kgaidev/kgai) | Capture project decisions and domain knowledge in a linked graph through the kgai CLI. |
| [least-cost-capable](https://github.com/kanibal-studio/least-cost-capable) | Pick the lowest declared cost rank among models that have the capabilities a task needs. |
| [mindpalace](https://github.com/aashutosh396/mindpalace-skill) | Organize a local knowledge vault around resources, project pointers, logs, and runbooks. |
| [OrcaReplay](https://github.com/Continuum-AI-Corp/OrcaReplay) | Inspect recorded agent runs and replay or fork them through Orca MCP. |
| [orchestrating-subagents](https://github.com/PapiScholz/symphony/tree/main/skills/orchestrating-subagents) | Choose model tiers for delegated work and review dispatch cost and duration. |
| [planning-with-files](https://github.com/OthmanAdi/planning-with-files/tree/master/skills/planning-with-files) | Persist plans, findings, and progress across long tasks and context resets. |
| [pr-review](https://github.com/priyank766/OpenSource-SKILL) | Filter a pull request review down to actionable findings. |
| [product-decision-agent](https://github.com/atdy/maoxuan-product-agent/tree/main/product-decision-agent) | Review product priorities, growth problems, and delivery constraints in Chinese. |
| [product-manager-skills](https://github.com/Digidai/product-manager-skills) | Critique PRDs, diagnose SaaS metrics, plan roadmaps, and run discovery; source license is CC BY-NC-SA 4.0. |
| [pro-launch](https://github.com/jack-reson8/pro-launch) | Take a product from idea to launch with gated phases for naming, references, UI and GTM. |
| [punchcard](https://github.com/Maksim-Burtsev/punchcard/tree/master/skills/punchcard) | Review a code change for module boundaries, dependencies, data models, and error paths. |
| [puzzle-activity-planner](https://github.com/fruitwyatt/puzzle-activity-planner) | Plan puzzle-based activities with timing, difficulty, preparation steps, and links to printable puzzle tools. |
| [receiving-code-review][receiving-review] | Evaluate review feedback and work through requested changes. |
| [requesting-code-review][requesting-review] | Request a review before work proceeds or merges. |
| [Satori](https://github.com/MetcalfSolutions/Satori) | Guide reflective conversations about emotions, relationships, and purpose, with professional-care boundaries. |
| [session-handoff](https://github.com/alapha888/session-handoff-kit) | Toolkit for coding agents providing a SKILL.md protocol, context-hygiene checklist, and handoff-note template for structured session transitions. |
| [shipreel](https://github.com/theBstar/shipreel/tree/main/plugins/shipreel/skills/shipreel) | Render a narrated PR walkthrough with diagrams, code panels, and optional app recordings. |
| [simple-man](https://github.com/Maksim-Burtsev/simple-man/tree/master/skills/simple-man) | Shorten agent replies while preserving findings, fixes, checks, and required facts. |
| [slop-post](https://github.com/useslop/claude-plugins/tree/main/plugins/slop/skills/slop-post) | Create a private Slop draft from a session with a receipt of model, tools, and commits. |
| [tlgr](https://github.com/tlgrcli/tlgr/tree/main/plugin/skills/tlgr) | Read, search, and manage a personal Telegram account through a JSON CLI. |
| [unpaid-intern](https://github.com/kevinmmiddleton/unpaid-intern/tree/main/skills/unpaid-intern) | Turn meeting transcripts, docs, and tickets into a morning briefing, meeting prep, and follow-ups in plain files you own. |
| [using-git-worktrees][worktrees] | Work in isolated checkouts for separate development tasks. |
| [using-lwc](https://github.com/JanYork/llm-wiki-cli/tree/main/skills/using-lwc) | Recall and preserve source-grounded project knowledge with LWC wiki and graph tools. |
| [wise-men-flash](https://github.com/Ali-expandings/wise-men-flash) | Put a hard decision to three subagents, one a Devil's Advocate, and get one checked memo that keeps the best case against it. |
| [workflow-design](https://github.com/ghorbanies/workflow-design) | Model workflow states, test guards, analyze transition logs, and plan safe flow changes. |
| [working-memory](https://github.com/ikotelkin/claude-skills/tree/main/skills/working-memory) | Preserve a bounded work checkpoint across context compaction. |
| [writing-plans][writing-plans] | Break a specification into implementation steps. |

<a id="️-development--architecture"></a>

### Development & Architecture

| Skill | Use it to |
| --- | --- |
| [anti-slop-design](https://github.com/wwewtech/anti-slop-design/tree/main/skills/anti-slop-design) | Review and refine UI typography, color tokens, interactions, and accessibility. |
| [anti-ui-slop](https://github.com/uizze/uizze/tree/main/skills/anti-ui-slop) | Define product-specific UI decisions, cover required states, and review rendered interfaces. |
| [api-designer](https://github.com/jeffallan/claude-skills/tree/main/skills/api-designer) | Design REST and GraphQL contracts with resource models, OpenAPI specifications, and validation. |
| [aria-icons](https://github.com/LeulAria/Aria-Icons/tree/main/skills) | Search ~1.4M open-source SVG icons and add them as SVG or React/Vue/Svelte/Solid components |
| [AuraKit](https://github.com/smorky850612/Aurakit/tree/main/skills/aura) | Coordinate build, fix, review, and deployment modes with state snapshots and optional local hooks. |
| [auteur](https://github.com/agiwhitelist/auteur) | Build websites from a written art direction and check design consistency and rendered output. |
| [birdview](https://github.com/Qiuner/birdview) | Map architecture, constraints, and planned changes back to source evidence. |
| [brewpage-publish](https://github.com/kochetkov-ma/claude-brewcode/tree/main/skills/brewpage-publish) | Publish text, Markdown, HTML, a file or a folder as a site to brewpage.app and return a shareable link, no account. |
| [build-with-better-design](https://github.com/better-designs/better-design-plugin/tree/main/skills/build-with-better-design) | Select and install a design system through the Better Design MCP service. |
| [building-blog](https://github.com/BuildShipGrowRepeat/nextjs-sanity-blog-skill/tree/main/skills/building-blog) | Add a Next.js and Sanity blog with project discovery, an implementation plan, and SEO guidance. |
| [clone-team](https://github.com/Varalix-Digitech-Solutions/clone-team/tree/main/skills/clone-team) | Rebuild website interfaces with an agent team, visual checks, and architecture notes. |
| [cohesivity](https://github.com/cohesivity-org/cohesivity-plugin/tree/main/packages/claude/skills/cohesivity) | Provision and manage application backend services through Cohesivity APIs and MCP. |
| [deacon-install](https://github.com/heydeacon/skills/tree/main/skills/deacon-install) | Add the Deacon AI support widget to a site or app, pass in the signed-in user, and check a live page loads it. |
| [dropthehassle-publish](https://github.com/bosmdavid-gif/dropthehassle-skill/tree/main/skills/dropthehassle-publish) | Publish built static sites through DropTheHassle and connect an existing backend. |
| [easy-auto-research](https://github.com/wjc2830/Easy-AutoResearch-for-DeepLearning/tree/main/easy-auto-research) | Run a supervised deep-learning experiment loop with versioned code and persistent progress. |
| [embedded-iot-mentor](https://github.com/mh-mansouri/embedded-iot-mentor/tree/main/embedded-iot-mentor) | Plan embedded and IoT projects, compare hardware, and work from breadboard to firmware. |
| [EmblemAI Agent Wallet](https://github.com/EmblemCompany/Agent-skills/tree/main/skills/emblem-ai-agent-wallet) | Query wallets and prepare explicitly confirmed transactions through the EmblemAI CLI. |
| [enterprise-architect](https://github.com/rafalr100/enterprise-architect-skill/tree/main/skills/enterprise-architect) | Plan target architectures, capability maps, decision records, and technology roadmaps. |
| [erupt-admin](https://github.com/plinian/erupt-skill) | Scaffold a Java admin app with the erupt framework, H2, CRUD, and permission models. |
| [figma-design-extract](https://github.com/jeltehomminga/figma-design-skills/tree/main/skills/figma-design-extract) | Extract Figma values into a design specification mapped to the project tokens. |
| [game-build-team](https://github.com/Varalix-Digitech-Solutions/game-build-team-skill/tree/main/skills/game-build-team) | Build Godot game features with agent roles, headless tests, visual review, and resumable progress. |
| [impresario](https://github.com/Shushant17711/impresario) | Invent a subject-specific concept and build an animated website from one sentence, then screenshot and revise it. |
| [keyboard-shortcuts](https://github.com/nparashar150/claude-keyboard-shortcuts/tree/main/skills/keyboard-shortcuts) | Audit and implement web-app shortcuts, command palettes, and keyboard help. |
| [legacy-modernizer](https://github.com/jeffallan/claude-skills/tree/main/skills/legacy-modernizer) | Plan incremental migrations and refactor legacy systems with dependency maps and behavior checks. |
| [light-cloud-deploy](https://github.com/light-cloud-com/skills/tree/main/skills/light-cloud-deploy) | Deploy a repo or local folder to Light Cloud, add a database, and read logs or roll back. |
| [mcp-builder][mcp-builder] | Build Model Context Protocol servers that connect tools and APIs to Claude. |
| [multi-stack-mcp](https://github.com/VovikP/multi-stack-mcp) | Generate hero, pricing, features, and CTA sections for Next.js, Flutter, WordPress, or Vue from shared tokens. |
| [nopekit](https://github.com/neuman/nopekit/tree/main/skills/nopekit) | Turn physical design claims into checks that must prove they can fail, for CAD, 3D printing, structures, and thermal. |
| [pit-stop](https://github.com/Finn763/pit-stop) | Find a small repository maintenance fix, support it with evidence, and review the patch. |
| [postgres-pro](https://github.com/jeffallan/claude-skills/tree/main/skills/postgres-pro) | Analyze PostgreSQL queries, replication, JSONB, extensions, and database maintenance. |
| [regulex-plus](https://github.com/PipeDream941/regulex-plus) | Render JavaScript regular expressions as SVG, PNG, or Mermaid diagrams through a CLI. |
| [scrollytelling-brand-site](https://github.com/abdelrhman2007/scrollytelling-brand-site/tree/main/skills/scrollytelling-brand-site) | Build scroll-told company websites with WebGL print-on-scroll 3D, performance budgets, responsive QA, and an optional CMS. |
| [tastegate](https://github.com/stas4000/tastegate/tree/main/tastegate) | Build a frontend from a design brief, then check layout, contrast and other visible defects with a bundled Playwright browser gate. |
| [tree-ring-memory](https://github.com/TerminallyLazy/tree-ring-memory-skill) | Recall, capture, audit, and forget durable project memory through Tree Ring Memory. |
| [unflat](https://github.com/merturl4576/unflat) | Add visual depth to web marketing pages through a bounded CSS treatment. |
| [web-artifacts-builder][artifacts] | Build web artifacts with React, Tailwind CSS, and shadcn/ui. |

<a id="-security--performance"></a>

### Security & Performance

| Skill | Use it to |
| --- | --- |
| [16-eyes](https://github.com/kigiela/16-eyes/tree/main/skills/16-eyes) | Audit a repository or PR diff through saved investigation lenses and skeptical verification. |
| [awesome-bug-bounty](https://github.com/YangTech-gh/Awesome-Bug-Bounty/tree/main/skills/awesome-bug-bounty) | Plan authorized bug-bounty research with scope checks, vulnerability guides, and report templates. |
| [cra-vulnerability-obligations](https://github.com/Ansvar-Systems/cra-vulnerability-obligations-skill) | Screen CRA scope and vulnerability-reporting questions using cited provisions through Ansvar Gateway. |
| [deep-security-audit](https://github.com/ravindrakele/claude-skills/tree/main/plugins/deep-security-audit/skills/deep-security-audit) | Map code attack surfaces and review candidate vulnerabilities with independent verification. |
| [deep-security-check](https://github.com/give-jd/deep-security-check/tree/main/skills/deep-security-check) | Run local static code, dependency, and secret scans and report their evidence and coverage. |
| [gedik](https://github.com/onur-kesim/gedik/tree/main/skills/gedik) | Audit authorized project surfaces and attach reproducible evidence to security findings. |
| [incident-reporting-navigator](https://github.com/Ansvar-Systems/incident-reporting-navigator-skill) | Map EU incident-notification questions to cited duties, authorities, and deadlines through Ansvar Gateway. |
| [regulatory-threat-model](https://github.com/Ansvar-Systems/regulatory-threat-model-skill) | Build evidence-cited threat models and selected EU obligation screens through Ansvar Gateway. |
| [SecHelix](https://github.com/omarmohelal/SecHelix/tree/main/skills/sechelix) | Review authorized local code for security issues with evidence and a refutation pass. |
| [secure-code-guardian](https://github.com/jeffallan/claude-skills/tree/main/skills/secure-code-guardian) | Implement authentication, authorization, input validation, and secure coding controls. |
| [security-reviewer](https://github.com/jeffallan/claude-skills/tree/main/skills/security-reviewer) | Review code and infrastructure for security issues and produce prioritized remediation guidance. |
| [unthrottled-route-check](https://github.com/edtrackai/ship-ready-skills/tree/main/skills/unthrottled-route-check) | Flag Next.js API routes that call OpenAI, Anthropic or Stripe Checkout with no rate limiter before abuse runs up the bill. |
| [wp-security-audit](https://github.com/mwstech/wp-security-audit-skill) | Audit WordPress configuration, plugin vulnerabilities, and indicators of compromise. |

<a id="-documentation--automation"></a>

### Documentation & Automation

| Skill | Use it to |
| --- | --- |
| [brickwise](https://github.com/JCPetrelli/brickwise) | Explain a codebase or topic as an interactive 3D brick model in one HTML page. |
| [code-documenter](https://github.com/jeffallan/claude-skills/tree/main/skills/code-documenter) | Write docstrings, API specifications, documentation portals, and developer guides. |
| [devops-engineer](https://github.com/jeffallan/claude-skills/tree/main/skills/devops-engineer) | Configure CI/CD, containers, infrastructure templates, deployment checks, and rollback plans. |
| [docs-to-book](https://github.com/EliaTolin/docs-to-book-skills/tree/main/docs-to-book) | Crawl technical documentation and compile an offline PDF book with Typst, optionally translated. |
| [famulor-assistants-history](https://github.com/bekservice/Famulor-Skill/tree/main/claude-store/skills/famulor-assistants-history) | Read Famulor assistant settings and interaction history through its restricted MCP profile. |
| [linkedin-outreach](https://github.com/vanshyadav1408/Omentir/tree/main/plugins/omentir/skills/linkedin-outreach) | Research prospects, draft outreach, and inspect campaigns through Omentir MCP. |
| [llm-wiki](https://github.com/praneybehl/llm-wiki-plugin/tree/main/skills/llm-wiki) | Ingest sources into a linked Markdown wiki, answer with citations, and check consistency across sessions. |
| [okf](https://github.com/mattjoyce/okf-skill/tree/master/skills/okf) | Author and validate Open Knowledge Format bundles of linked Markdown concept files. |
| [process-builder](https://github.com/Castaldo-Solutions/process-builder) | Turn a process interview into a BPMN swimlane diagram in a .drawio file. |
| [project-planning-journaling](https://github.com/mh-mansouri/Project-Planning-Journaling/tree/main/project-planning-journaling) | Scope a project and maintain a resumable journal of decisions, progress, and open work. |
| [readme-atlas](https://github.com/chromoany/readme-atlas) | Write, rewrite, review, and translate project READMEs from repository evidence, dropping claims the repository cannot support. |
| [swarmvault](https://github.com/swarmclawai/swarmvault/tree/main/skills/swarmvault) | Maintain a local Markdown knowledge vault with graph navigation, search, review, and optional model-backed synthesis. |
| [trace-my-code](https://github.com/kgohil/trace-my-code/tree/main/skills/trace-my-code) | Maintain domain flows, architecture notes, and reuse patterns with code-drift checks. |

<a id="-media--content-creation"></a>

### Media & Content Creation

| Skill | Use it to |
| --- | --- |
| [3d-logo](https://github.com/hasuwini77/3d-logo-skill/tree/main/skills/3d-logo) | Build a rotating 3D logo component with React Three Fiber. |
| [algorithmic-art][algorithmic-art] | Create generative art with p5.js. |
| [bria-ai](https://github.com/Bria-AI/bria-skill/tree/dev/skills/bria-ai) | Generate and edit images or remove backgrounds through the Bria API. |
| [canvas-design][canvas-design] | Create visual designs as PNG and PDF files. |
| [cliptude-plan](https://github.com/cliptude/cliptude/tree/main/mcp_server/skills/cliptude-plan) | Plan every shot of a YouTube documentary, then have Cliptude voice, source and render it. |
| [collage-design](https://github.com/polgarp/collage-design) | Compose collage artwork from licensed or supplied imagery and keep an attribution ledger. |
| [comment-to-dm-cta](https://github.com/commentkeyword/agent-toolkit/tree/main/skills/comment-to-dm-cta) | Plan the "comment KEYWORD" CTA of an Instagram Reel and create its auto-DM in CommentKeyword, which requires an account and API token. |
| [harmonic-mixing](https://github.com/songfinder-dev/songfinder-skills/tree/main/skills/harmonic-mixing) | Look up tempo and musical key to plan playlists and DJ transitions. |
| [hitpost](https://github.com/Lihaila/hitpost-skill/tree/main/skills/hitpost) | Write three X posts or threads per idea, length-checked the way X counts, with share links. |
| [identify-song](https://github.com/songfinder-dev/songfinder-skills/tree/main/skills/identify-song) | Identify a track from a link or audio file through Song Finder. |
| [kavel-image](https://github.com/hanshs474/kavel-image-skill) | Generate images through Kavel's anonymous submit-and-poll API within its free allowance; photo edits require a Kavel API key. |
| [keyword-icons](https://github.com/ruthless-coder-ai/keyword-icons) | Create several simple SVG icon concepts and inspect transparent PNG renders at small sizes. |
| [ltx2-video](https://github.com/patraxo/ltx2-vidgen-skill/tree/main/skills/ltx2-video) | Generate clips from text, images, or video through an LTX-2.3 backend deployed to the user Modal account. |
| [make-faceless-video](https://github.com/airdropfi/autoshort-skills/tree/main/skills/make-faceless-video) | Draft, price-check and render faceless short videos through the AutoShort or StoryShort MCP server; needs an account with credits. |
| [meshy-pose-rigging](https://github.com/rickyworld/rigmeshy-by-ricky/tree/master/meshy-pose-rigging) | Prepare character references and work through Meshy auto-rigging and export troubleshooting. |
| [pro-motion](https://github.com/jack-reson8/pro-motion/tree/main/plugins/pro-motion/skills/pro-motion) | Audio-first motion-graphics launch, brand and TVC films rendered to MP4 in code, cut to a planned music track. |
| [publishport](https://github.com/karuha-m/publishport-skill/tree/main/skills/publishport) | Publish and cross-post through connected accounts in the user's PublishPort browser app. |
| [puzzlegenio](https://github.com/fruitwyatt/puzzlegenio-claude-skill) | Choose a puzzle type and build prefilled links to PuzzleGenio browser tools for creating printable puzzles. |
| [reels-setup](https://github.com/VishiATChoudhary/reels/tree/main/skills/reels-setup) | Install and verify a Remotion studio that builds 9:16 story reels cut to a song's drop. |
| [runapi-cli](https://github.com/runapi-ai/cli-skill/tree/main/skills/runapi-cli) | Generate media and run model jobs through the RunAPI CLI; requires configured billing and authentication. |
| [ruxi-skill](https://github.com/swaylq/ruxi-skill) | Build a single-file visual novel from selected book scenes with source-linked choices. |
| [screenbrowser](https://github.com/screenbrowser/skill/tree/main/skills/screenbrowser) | Produce narrated web-app tutorials through the Screen Browser MCP service. |
| [seedance-25-prompting](https://github.com/gbeyrouti/seedance-prompting-claude-skill/tree/main/seedance-25-prompting) | Write and troubleshoot Seedance video prompts, reference roles, audio, and shot timing. |
| [slack-gif-creator][slack-gif-creator] | Make animated GIFs sized for Slack. |
| [SocialClaw](https://github.com/ndesv21/socialclaw/tree/main/skill) | Schedule and publish social posts through SocialClaw; requires a configured workspace and active plan. |
| [table-sheet](https://github.com/netmobster/unstuck-games/tree/main/plugins/table-sheet) | Turn a D&D Beyond character sheet into a play guide and pre-session checklist. |
| [vox-director](https://github.com/Alisa0808/vox-director) | Plan and assemble narrated collage videos through paid Atlas Cloud APIs and local ffmpeg. |
| [watch-igaming](https://github.com/igamingsychov/watch-igaming) | Review a video link or local screen recording with transcript and scene-change frames, then build a QA table, UX audit or meeting minutes. |
| [youtube-transcript](https://github.com/tubeagentkit/youtube-transcript-skills/tree/main/skills/youtube-transcript) | Fetch transcripts, video search results, and playlists through the YouTube Transcript API. |

<a id="-data--analysis"></a>

### Data & Analysis

| Skill | Use it to |
| --- | --- |
| [adhx](https://github.com/itsmemeworks/adhx/tree/main/skills/adhx) | Read X posts and articles as structured JSON through the ADHX API. |
| [aligned-delivery](https://github.com/ahnbingbing/aligned-delivery) | Analyze sprint and delivery metrics, diagnose team workload, and forecast completion dates. |
| [apify-account-mapping](https://github.com/johnisanerd/claude-skill-account-mapping/tree/main/apify-account-mapping) | Map the people currently in named roles at each target account through paid Apify actors. |
| [apify-linkedin-post-engagement](https://github.com/johnisanerd/claude-skill-linkedin-post-engagement/tree/main/apify-linkedin-post-engagement) | Compare LinkedIn post reactions, comments, and shares through paid Apify data. |
| [apify-linkedin-posts-scraper](https://github.com/johnisanerd/claude-skill-linkedin-posts-scraper/tree/main/apify-linkedin-posts-scraper) | Collect public LinkedIn post records through a paid Apify actor. |
| [apify-remote-startup-jobs](https://github.com/johnisanerd/claude-skill-remote-startup-jobs/tree/main/apify-remote-startup-jobs) | Fetch structured remote startup job listings through a paid Apify actor. |
| [apify-yc-startup-jobs](https://github.com/johnisanerd/claude-skill-yc-startup-jobs/tree/main/apify-yc-startup-jobs) | Compare published startup salary and equity ranges through a paid Apify actor. |
| [apify-youtube-transcript-api](https://github.com/johnisanerd/claude-skill-youtube-transcript-api/tree/main/apify-youtube-transcript-api) | Fetch YouTube captions and subtitle formats through a paid Apify actor. |
| [apify-youtube-transcripts-llm-training-data](https://github.com/johnisanerd/claude-skill-youtube-transcripts-llm-training-data/tree/main/apify-youtube-transcripts-llm-training-data) | Build transcript datasets with provenance, language policy, error filtering, and paid Apify usage. |
| [apitube-news-api](https://github.com/apitube/news-api-skills/tree/main/skills/apitube-news-api) | Search and filter news through APITube, with API authentication, pagination, and error handling. |
| [claude-ecom](https://github.com/takechanman1228/claude-ecom) | Review ecommerce order CSVs for revenue, retention, and margin patterns. |
| [claude-persona](https://github.com/takechanman1228/claude-persona/tree/main/skills/persona) | Simulate persona panels and concept interviews, then summarize themes and comparisons for exploratory research. |
| [converly](https://github.com/converlyio/converly-agent) | Configure Converly conversion flows and inspect test events and delivered conversions. |
| [datawebot](https://github.com/datawebot/datawebot-mcp/tree/main/skills/datawebot) | Find products across online shops and every seller's price with direct links through the hosted datawebot MCP server. |
| [formo-analytics](https://github.com/getformo/cli/tree/main/skills/formo-analytics) | Query Formo product and onchain analytics through MCP, CLI, or REST. |
| [invoice-winning-numbers](https://github.com/tahodev/baodao-skill/tree/main/invoice-winning-numbers) | Look up Taiwan invoice winning numbers by period from official sources. |
| [market-mirror](https://github.com/DarkWorldCoder/market-mirror/tree/main/plugin/skills/market-mirror) | Test ads, prices and sales pitches on simulated buyers and get a go / iterate / no-go report. |
| [octav-api](https://github.com/Octav-Labs/octav-api-skill) | Integrate wallet balances, history and DeFi positions using an API key; selected agent endpoints also support x402 payments. |
| [pandas-pro](https://github.com/jeffallan/claude-skills/tree/main/skills/pandas-pro) | Clean, join, aggregate, and transform pandas DataFrames and time-series data. |
| [polymarket-tennis](https://github.com/livetennisapi/polymarket-tennis/tree/main/skills/polymarket-tennis) | Build an observe-only tennis market watcher joining market prices to live match scores. |
| [pvr-inox-radar](https://github.com/karanb192/pvr-inox-radar/tree/main/skills/pvr-inox-radar) | Map PVR INOX showtimes in India with seats-together counts and travel-time estimates. |
| [shopify-review-triage](https://github.com/alfredtech2026/shopify-app-review-brief/tree/main/docs/skills/shopify-review-triage) | Turn supplied Shopify reviews into source-linked incident, friction, pricing, and feature triage. |
| [site-traffic-teardown](https://github.com/zhuyansen/site-traffic-teardown/tree/main/skills/site-traffic-teardown) | Find a site's competitors and compare traffic, channel mix, keywords, backlinks, and DR, then name three growth opportunities; paid AIsa data. |
| [sql-pro](https://github.com/jeffallan/claude-skills/tree/main/skills/sql-pro) | Write and optimize SQL queries, inspect execution plans, and compare database dialects. |
| [weread-trial-card-list](https://github.com/C-s-salute/weread-trial-card-list) | Scrape WeRead category and rank pages into a deduplicated list of trial-card readable books, exported as HTML and Excel. |
| [youtube-full](https://github.com/ZeroPointRepo/youtube-skills/tree/main/skills/youtube-full) | Fetch YouTube transcripts, search results, channel data, and playlists through TranscriptAPI; requires an API key. |

<a id="-finance--tax"></a>

### Finance & Tax

| Skill | Use it to |
| --- | --- |
| [file-itr](https://github.com/shivprime94/file-itr) | Follow a guided walkthrough of India's income-tax filing portal. |
| [furusato-nozei](https://github.com/tahodev/kurashi-skill/tree/main/furusato-nozei) | Estimate Japan's hometown-tax donation cap with stated assumptions and official sources. |
| [ipo-offer-document-review](https://github.com/parinshahAIbuilder/ipo-offer-document-review) | Review Indian IPO offer documents (DRHP/RHP) against SEBI ICDR, LODR, Companies Act and Ind AS for disclosure gaps. |
| [itr-wala](https://github.com/karanb192/itr-wala) | Prepare Indian income-tax returns using document extraction and Python calculations. |
| [open-finance-skills](https://github.com/levelcfo/open-finance-skills) | Review SMB month-end closes, bank reconciliations, 13-week cash forecasts, and 1099 readiness with 20 finance skills. |
| [simmer-tennis-live-gate](https://github.com/livetennisapi/simmer-tennis-live-gate) | Gate simulated tennis market entries on live match state without placing orders. |
| [stipend](https://github.com/stipend-sh/stipend) | Manage a self-custodied USDC wallet and x402 payments with configurable spending policies. |
| [stock-analysis](https://github.com/AlenSarangSatheesh/Indian-Stocks-Fundamental-Analysis-SKILL/tree/main/stock-analysis) | Analyze listed companies using primary filings, sector comparisons, and accounting-quality checks. |
| [verify-polish-company](https://github.com/bartosz-kuc/skanfirmy-mcp/tree/main/skill) | Look up Polish company registrations, VAT status, bank accounts, and EU VAT numbers. |

<a id="️-writing--research"></a>

### Writing & Research

| Skill | Use it to |
| --- | --- |
| [ai-tell-detector](https://github.com/aragossa/ai-tell-detector/tree/main/en/ai-tell-detector) | Audit English or Russian drafts for generic writing patterns and suggest precise edits. |
| [berlin-job-search](https://github.com/umutyesildal/berlin-job-search/tree/main/skills/berlin-job-search) | Search Berlin and German job boards, check German and Blue Card requirements, and draft a Lebenslauf or English CV without inventing claims. |
| [brand-guidelines][brand-guidelines] | Apply Anthropic's brand colors and typography to artifacts. |
| [business-name-fit](https://github.com/Elham-Farajnejad/business-name-fit) | Assess a business name across cultures, languages, and target markets. |
| [buyer-eval-skill](https://github.com/salespeak-ai/buyer-eval-skill) | Evaluate B2B software vendors by checking claims, contradictions, unanswered questions, and purchase requirements. |
| [check-blindspot](https://github.com/AlexanderCato/check-blindspot) | Check a belief against the evidence: argue both sides, name the fact that would settle it, and flag overconfidence. |
| [diasporic-intelligence](https://github.com/MinistaJazz/diasporic-intelligence/tree/main/skills/diasporic-intelligence) | Apply an attribution and consent framework to writing about cultural and lineage knowledge. |
| [fact-check-x-complete](https://github.com/ASI2030/Fact-Check-X/tree/main/skills/fact-check-x-complete) | Capture AI answers and citations, compare atomic claims, and preserve evidence during verification. |
| [feynman-pdf](https://github.com/TadTheFisherman/feynman-it) | Create illustrated PDF explainers with plain-language analogies and rendered-page checks. |
| [goethecoach](https://github.com/janosszaboaipm-design/goethecoach-claude-skill/tree/main/goethecoach) | Practise Goethe exam writing, reading, and speaking with rubric-based feedback. |
| [grill](https://github.com/mtangoz/grill/tree/main/skills/grill) | Challenge a decision with an outside model and name tests that could settle the doubts. |
| [grounded](https://github.com/jostelzer/grounded/tree/main/skills/grounded) | Draft scientific literature reviews with live source discovery and citation checks. |
| [humanize-chinese](https://github.com/swaylq/humanize-chinese) | Edit Chinese prose with rewriting, phrase cleanup, and local checks; non-commercial license. |
| [humanize-pro](https://github.com/msdanyg/humanize-pro) | Rewrite or audit prose against a saved voice profile and publishing-channel rules. |
| [humanizer-ru](https://github.com/ilyautov/humanizer-ru) | Edit Russian prose for its audience while preserving facts, voice, and protected text. |
| [humanizer-zh-tw](https://github.com/nagameTW/formosa-humanizer) | Remove AI writing patterns from Traditional Chinese text, replace mainland Chinese terms with Taiwan usage, and keep full-width punctuation. |
| [humanizing-writing](https://github.com/AshwinSathian/humanize-writing-skill) | Edit prose for generic structure, filler, weak claims, and repeated writing patterns. |
| [internal-comms][internal-comms] | Draft updates, newsletters, and other internal communications. |
| [jd-decoder](https://github.com/landedjobs/ai-job-hunt-os/tree/main/skills/jd-decoder) | Read a job posting for real requirements, salary signals, and ghost-listing risk before applying. |
| [kochab](https://github.com/btmoriarty/kochab/tree/main/skills/kochab) | Run a resume-based job search with tailored drafts, interview preparation, and pipeline tracking. |
| [niubiskill](https://github.com/nathanskill/niubiskill/tree/main/skills/niubiskill) | Review business ideas and choose a next monetization test with explicit evidence and assumptions. |
| [no-slop](https://github.com/Byk3y/no-slop) | Review prose for vague attribution, promotional phrasing, repetitive structures, and other writing patterns. |
| [prospeak](https://github.com/giorgiozamboni/prospeak) | Rewrite existing text for professional audiences with English and Italian register controls. |
| [publora-post-ideas](https://github.com/publora-team/publora-post-ideas/tree/main/skills/publora-post-ideas) | Choose among three social-post angles, then draft the one the user selects. |
| [reading-analysis](https://github.com/shenquan520/reading-analysis) | Analyse English exam passages, answer choices, and recurring errors. Noncommercial license. |
| [renwei](https://github.com/dbhosbu-dotcom/renwei) | Edit Chinese manuscripts for syntax, chapter rhythm, factual consistency, and generic prose. |
| [resume-claim-guard](https://github.com/korey2028-prog/resume-claim-guard) | Interviews candidates to lock a verified fact sheet before tailoring resumes to job descriptions. |
| [resume-studio](https://github.com/Sidgit11/resume-studio) | Maintain a career evidence corpus and tailor resumes to job requirements without inventing claims. |
| [sales-framework](https://github.com/KudoMetrics-Techologies-Private-Limited/sales-framework/tree/main/skills/sales-framework) | Review sales copy, pitches, and objections against a published persuasion framework. |
| [Say it plainly](https://github.com/adjustleads/provenskills-free-packs/tree/main/plain-writing/say-it-plainly) | Rewrite prose for a reader without changing its claims. Noncommercial license. |
| [seo-translator](https://github.com/Skillproofdev/seo-translator) | Localize content with market-specific registers while preserving keywords, links, and structure. |
| [signs-of-ai](https://github.com/peopleworks/SignsofAI) | Edit English and Spanish writing patterns and interpret optional analysis-tool results with limits. |
| [structured-gist](https://github.com/domattioli/structured-gist/tree/main/skills/structured-gist) | Format explanations and process recaps as nested outlines for skimming. |
| [swedish_mentor](https://github.com/mh-mansouri/help_with_swedish/tree/master/swedish_mentor) | Plan Swedish practice with level-matched video, podcast, and speaking exercises. |
| [tldr](https://github.com/SurefireStudios/tldr/tree/main/skills/tldr) | Lead with a short summary while preserving full details and critical caveats. |
| [trade-show-prep](https://github.com/DataOrigin/trade-show-prep-skill/tree/main/skills/trade-show-prep) | Plan a B2B trade show, draft meeting requests, qualify booth leads, and write follow-ups. |
| [unslop](https://github.com/MohamedAbdallah-14/unslop/tree/main/skills/unslop) | Rewrite prose to remove repeated AI writing patterns while preserving technical content. |
| [upwork-job-hunter](https://github.com/droopboop/flconsole-upwork-mcp/tree/main/skills/upwork-job-hunter) | Check new Upwork jobs through the flconsole MCP server, shortlist the ones that fit, and draft a proposal for review. |
| [zh-tw-humanizer](https://github.com/acchuang/zh-tw-humanizer) | Edit Traditional Chinese prose with Taiwan terminology and protected-fact rules. |

<a id="-meta-skills"></a>

### Meta Skills

| Skill | Use it to |
| --- | --- |
| [CERA Project Memory](https://github.com/miketepUR/cera-reasoning-harness) | Preserve project session maps and curate a shared index for later conversations. |
| [claude-memory-manager](https://github.com/jau123/claude-memory-manager) | Organize Claude Code auto-memory with placement rules, update guidance, and index-size checks. |
| [danshari-skill](https://github.com/swaylq/danshari-skill) | Audit installed skills and archive redundant ones after user approval, with a restore path. |
| [emulo](https://github.com/ohad6k/emulo/tree/main/.agents/skills/emulo) | Mine local agent-session history into a personal working profile after approving the scope and cost. |
| [feedback](https://github.com/luchasarie/feedback-loop/tree/main/skills/feedback) | Turn frustration with an agent into an evidence-backed improvement plan that changes nothing until you approve it. |
| [prime-worker](https://github.com/alperiox/prime-worker) | Delegate multi-turn tasks to persistent local prime-agent worker sessions. |
| [reap (skillreaper)](https://github.com/thousandflowers/skillreaper/tree/main/plugins/skillreaper/skills/reap) | Measure unused loaded context from local agent transcripts and review reversible cleanup. |
| [rule-architect](https://github.com/moveju112/rule-architect) | Generate modular project rules with a shared index and runtime-specific entrypoints. |
| [sijiao-skill](https://github.com/swaylq/sijiao-skill) | Build a stateful learning tutor with researched lessons, exercises, and spaced review. |
| [skill-creator][creator] | Create skills, evaluate them, and refine their descriptions. |
| [skill-freshness](https://github.com/kvozianov/skill-freshness) | Audit skills across Claude Code, Codex, Cursor and other agents for broken, outdated, duplicate or now built-in ones, with sources. |
| [skill-skill](https://github.com/jack-reson8/skill-skill/tree/main/plugins/skill-skill/skills/skill-skill) | Write skills that change the output, then lint them against the Agent Skills spec with a health score. |
| [skill-tuner](https://github.com/DENGYUFAN0/skill-forge/tree/main/skill-tuner) | Refine an installed skill through a small baseline, focused edits, and a rollback decision. |
| [subagent-driven-development][subagents] | Implement a plan through delegated tasks and review steps. |
| [task-observer](https://github.com/rebelytics/one-skill-to-rule-them-all) | Capture task friction and propose reviewed changes to reusable skills. |
| [template-skill][template] | Start a skill from a minimal `SKILL.md` template. |
| [whetstone](https://github.com/TbusOS/whetstone) | Distil session lessons into reviewable skill proposals with evidence and duplication checks. |
| [writing-skills][writing-skills] | Write and test skill instructions before distributing them. |

[Back to categories ↑](#browse-skills)

## Skill Collections

Browse these repositories when you want a related set of skills.

| Collection | Focus |
| --- | --- |
| [Anthropic skills](https://github.com/anthropics/skills) | Document processing, design, development, and skill examples. |
| [Superpowers](https://github.com/obra/superpowers) | Planning, testing, debugging, and development workflows. |
| [adologyai/content-intelligence-plugin](https://github.com/adologyai/content-intelligence-plugin) | Competitive ad research, brand tracking, and audience analysis through Adology hosted MCP tools. |
| [Affiliate Skills](https://github.com/Affitor/affiliate-skills) | Affiliate research, content, distribution, and analytics. |
| [Agent Skills English Productivity Pack](https://github.com/alapha888/agent-skills-en) | Meeting notes, proofreading, research, code review, and commit messages. |
| [agent-pilot-skills](https://github.com/babyGao/agent-pilot-skills) | Cross-model review, parallel research, outbound sales, illustrations, and Chinese-platform workflows. |
| [agentsvc.io skills](https://github.com/agentsvc/skills) | Speech to text, web pages to Markdown, email checks, token safety, and document text through paid agentsvc.io APIs. |
| [AI sales skills](https://github.com/Marchenko-sales/ai-sales-skills) | Company research, sales qualification, and business outreach workflows in Russian. |
| [aigent-OS](https://github.com/wrg32786/aigent-os) | Persistent vault memory, session routines, delegation, hooks, and local maintenance workflows. |
| [Baodao skills](https://github.com/tahodev/baodao-skill) | Taiwan public-service lookups for invoices, weather, alerts, transit, and public data. |
| [ChatCrystal](https://github.com/ZengLiangYi/ChatCrystal/tree/main/skills) | Local memory recall and writeback for coding sessions. |
| [Chisanan232/requirement-zero](https://github.com/Chisanan232/requirement-zero) | Review requirement necessity and audit whether existing code still earns its upkeep. |
| [claude-fable-5-skills](https://github.com/kpab/claude-fable-5-skills) | Effort calibration, scope control, and subagent orchestration. |
| [Cogny Marketing Skills](https://github.com/cognyai/claude-code-marketing-skills) | Marketing audits and copywriting; live account integrations require a Cogny subscription. |
| [Cowork Tasks](https://github.com/sabbah13/cowork-tasks) | Create and triage a local task board from authorized Cowork connectors; includes prioritization and board-review skills. |
| [CreatorSkills Free Skills](https://github.com/calebvbi/creatorskills-free-skills) | Blog outlines, short-video scripts, show notes, chapters, newsletter planning, and social copy. |
| [dbhq-uk/marketplace](https://github.com/dbhq-uk/marketplace) | Remote diagnostics, code search, repository checks, research, writing, and work-service integrations. |
| [Design Engineer Skills](https://github.com/modeinspect/design-engineer-skills) | Repo setup, component impact, visual QA, reviewable UI pull requests, design review of PRs and design system scoring for designers. |
| [DurdeuVlad/persona-write](https://github.com/DurdeuVlad/persona-write) | Persona-based drafting, rewriting, sample-based voice extraction, and independent review. |
| [E-commerce skills](https://github.com/mardab96/ecommerce-claude-skills) | Review checkout, product content, margin, inventory, retention, and disputes from store data. |
| [Growth Cab GTM Skills](https://github.com/federicodon/growthcab-gtm-skills) | Sending-domain checks, cold-email grading, lead-list QA, and meeting benchmarks. |
| [iOS agents and skills](https://github.com/apexbymanish/claude-ai-agents-ios) | Swift/iOS implementation, testing, accessibility, performance, security, and release checks. |
| [Kudosity skills](https://github.com/kudosity/skills) | SMS, MMS, WhatsApp, RCS, contact lists, and delivery webhooks through Kudosity. |
| [Kurashi skills](https://github.com/tahodev/kurashi-skill) | Japan public-service lookups for weather, alerts, holidays, taxes, and libraries. |
| [leechen298/Code2Skill](https://github.com/leechen298/Code2Skill) | Extract source-based agent tools and independently review generated workflow and source fidelity. |
| [Lesile-Yin/agent-skills](https://github.com/Lesile-Yin/agent-skills) | Prompt engineering, multi-lens reviews, token budgets, and batch PowerPoint automation. |
| [Linked API Skills](https://github.com/Linked-API/linkedin-skills) | Read and manage LinkedIn profiles and lead pipelines through Linked API; requires configured credentials. |
| [Mamba Labs Skills](https://github.com/mambalabsdev/mamba-labs-skills) | Prospect research, CRM operations, email deliverability, and go-to-market workflows; some use Apify. |
| [MarchTalk/ai-content-skills](https://github.com/MarchTalk/ai-content-skills) | Chinese concept analysis, conversation-to-draft organization, and source-based content review. |
| [Marketing Skills](https://github.com/coreyhaines31/marketingskills) | SEO, copywriting, email, pricing, advertising, and analytics. |
| [mblode/agent-skills](https://github.com/mblode/agent-skills) | UI, typography, developer experience, documentation, review, and release workflows. |
| [minxnnu-cloud/make-new-things](https://github.com/minxnnu-cloud/make-new-things) | Claude/Codex visual handoffs, representative frame approval, rework limits, and skill-tree sync. |
| [Nero1688/claude-academic-skills](https://github.com/Nero1688/claude-academic-skills) | Academic planning, literature checks, research methods, and replication workflows; mixed licenses. |
| [noizai/skills](https://github.com/noizai/skills) | Text-to-speech dubbing and companion voice presets. |
| [NotFair](https://github.com/nowork-studio/notfair-plugin) | SEO, search visibility, advertising, and analytics workflows with service-specific MCP integrations. |
| [Novu skills](https://github.com/novuhq/skills) | Build Novu notification workflows, inboxes, preferences, and hosted agent channels. |
| [Ontoly skills](https://github.com/0xsarwagya/ontoly/tree/main/skills) | Architecture, dependency, refactoring, and documentation workflows grounded in Ontoly graph evidence. |
| [Pathmode](https://github.com/pathmodeio/claude-plugin) | Turn product ideas into intent specifications, challenge assumptions, and verify implementation evidence. |
| [prompt-to-asset](https://github.com/MohamedAbdallah-14/prompt-to-asset) | Route image briefs, create software assets, and export platform bundles through a CLI and MCP server. |
| [RouterBase Agent Skills](https://github.com/zenlee123/routerbase-agent-skills) | Integrate the RouterBase gateway, choose models, and handle media-generation API jobs; requires a RouterBase key. |
| [Sequenzy skills](https://github.com/Sequenzy/skills) | Run lifecycle, campaign, and transactional email work through the Sequenzy CLI or MCP server; requires a Sequenzy account. |
| [Shipwise](https://github.com/harmansidhudev/shipwise) | Plan and review webapp launches across validation, design, architecture, quality, security, and operations. |
| [sjh9714/skill-receipts](https://github.com/sjh9714/skill-receipts) | Small code-scope and reproduction-first skills with published admission and rejection evidence. |
| [suede-creator-skills](https://github.com/JasonColapietro/suede-creator-skills) | Code quality, design, marketing, and shipping. |
| [superseo-skills](https://github.com/inhouseseo/superseo-skills) | SEO audits, content writing, and link building. |
| [Vibe Coding Rules skills](https://github.com/getvibekits/vibe-coding-rules/tree/main/skills) | Explain errors, add a page, commit, review changes, apply design rules, guard database changes, and run an SEO check. |
| [Wondel.ai Skills](https://github.com/wondelai/skills) | Apply product, UX, marketing, and software frameworks from published books and style guides. |
| [YouTube Skills](https://github.com/sergebulaev/youtube-skills) | Draft YouTube titles, descriptions, hooks, thumbnail briefs, and upload plans; optional Publora publishing. |
| [YYLO skills](https://github.com/yylo-dev/yylo-skills) | Manage tasks, artifacts, benchmarks, and durable work records through the YYLO CLI. |

<a id="how-to-install-skills"></a>

## Quick Start

Install Anthropic's document skills in Claude Code from your terminal.

```bash
claude plugin marketplace add anthropics/skills
claude plugin install document-skills@anthropic-agent-skills
```

Provide a PDF, then ask Claude to extract its form fields. Compare the result
with your file. [Read Anthropic's installation guide][anthropic-install].

<details>
<summary><strong>Other collections, standalone skills, and updates</strong></summary>

Use each source repository's install guide. Collections may ship as plugins,
individual folders, or both. Choose one route for each collection.

For a standalone Claude Code skill, put its folder in
`~/.claude/skills/<skill-name>/` for personal use, or
`.claude/skills/<skill-name>/` for one project. Keep `SKILL.md` and its supporting
files together. See the [Claude Code skill guide][skill-guide].

Follow the [plugin update guide][plugin-updates] for plugin installs.
For standalone folders, use the source repository's update instructions.
Cloning this directory does not install the listed skills.

</details>

## FAQ

<a id="what-are-skills"></a>

<details>
<summary><strong>What is a skill?</strong></summary>

A skill is a folder containing instructions in `SKILL.md`, with optional
scripts and resources. Claude loads it when relevant to a task, or you can
invoke it directly. See the [skill guide][skill-guide].

</details>

<details>
<summary><strong>Does every skill work in every Claude app?</strong></summary>

The format is shared, but tools and installation differ by host. A Claude Code
plugin does not install itself in Claude.ai or the API. Check the source's
supported environments and [Anthropic's separate install routes][anthropic-install].

</details>

<a id="skills-vs-mcp-vs-system-prompts"></a>

<details>
<summary><strong>Skills, MCP, or project instructions?</strong></summary>

| You need | Use |
| --- | --- |
| A repeatable task or workflow | [Skills][skill-guide] |
| Access to an external service or tool | [Model Context Protocol (MCP)][mcp-guide] |
| Conventions Claude reads for a project | [Project instructions][memory-guide] |

</details>

<details>
<summary><strong>Are the listed skills tested or audited?</strong></summary>

This is a community directory, not a certification program. Read the source
instructions and scripts, then try the skill on a task whose result you can
check. Report broken links or incorrect descriptions through [issues][suggest].

</details>

<details>
<summary><strong>Can I create or contribute a skill?</strong></summary>

Start with [skill-creator][creator] or the [template][template]. To add a
listing, follow the [contribution guide](CONTRIBUTING.md).

</details>

## Skill ideas

These are requests for contributions, not skills you can install.
Know an implementation? [Suggest its source][suggest].

<details>
<summary><strong>Browse ideas by category</strong></summary>

| Category | Ideas awaiting a source |
| --- | --- |
| Testing | e2e-testing-skill, snapshot-testing |
| Debugging | performance-profiling |
| Development | api-development, database-migration, refactoring-patterns |
| Security & performance | security-review, dependency-audit, performance-optimization, load-testing |
| Documentation | documentation-generator, changelog-automation, ci-cd-integration |
| Media | video-editing-helper |
| Data | data-visualization, sql-query-builder, csv-processing |
| Writing | research-assistant, technical-writing |

</details>

<details>
<summary><strong>Looking for an entry from an older version of this list?</strong></summary>

Some entries now live inside other skills or use a different name.

| Earlier entry | Current source |
| --- | --- |
| artifacts-builder | [web-artifacts-builder][artifacts] |
| condition-based-waiting | [Supporting guide in systematic-debugging][waiting] |
| defense-in-depth | [Supporting guide in systematic-debugging][defense] |
| root-cause-tracing | [Supporting guide in systematic-debugging][tracing] |
| testing-skills-with-subagents | [Supporting guide in writing-skills][testing-skills] |
| testing-anti-patterns, sharing-skills | No standalone skill found in the [current Superpowers catalog][superpowers-catalog]. |

</details>

## Resources

- [Claude Code skill guide][skill-guide]
- [Agent Skills specification](https://agentskills.io/specification)
- [How Anthropic designed Skills][skills-deep-dive]
- [Skills announcement](https://www.anthropic.com/news/skills)
- [Simon Willison on Claude Skills][simon-skills]
- [awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code)
- [awesome-claude](https://github.com/alvinunreal/awesome-claude)
- [Claude Skills Hub](https://claudeskills.info/)
- [Claudebin](https://claudebin.com) and its
  [source](https://github.com/wunderlabs-dev/claudebin.com/)
- [AgentHub](https://myagenthub.cn): offers a Chinese-language directory of MCP
  servers and agent skills.
- [Hypit video guide](https://hypit.video/guides/how-to-clone-a-video/): walks
  through planning and rendering a video from a reference format.
-
  [awesome-claude-code-hooks](https://github.com/loqimean/awesome-claude-code-hooks):
  Related directory of Claude Code hook workflows.
- [500k.io Skills Bank](https://500k.io/skills): Related directory of skills,
  MCP servers, GPTs, and agent tools.
- [PolySkill](https://polyskill.ai): Skill registry and CLI with [public
  source](https://github.com/MrSpacemann/polyskill).
- [Claude Skills 中文市集](https://claudeskill.me): Read Chinese-language tutorials
  for Claude skills and plugins.

<a id="contributors"></a>

## Contributing

Add a skill, fix a link, or improve a description. Read the
[contribution guide](CONTRIBUTING.md), then open a pull request.

Built with contributions from the [community][contributors], including skills
from [Anthropic](https://github.com/anthropics/skills) and
[obra](https://github.com/obra/superpowers).
Maintained by [Karan Bansal](https://karanbansal.in) · [Blog][blog].

## License

[MIT](LICENSE) covers this directory. Each listed skill has its own license.

[pdf]: https://github.com/anthropics/skills/tree/main/skills/pdf
[docx]: https://github.com/anthropics/skills/tree/main/skills/docx
[pptx]: https://github.com/anthropics/skills/tree/main/skills/pptx
[xlsx]: https://github.com/anthropics/skills/tree/main/skills/xlsx
[webapp-testing]: https://github.com/anthropics/skills/tree/main/skills/webapp-testing
[mcp-builder]: https://github.com/anthropics/skills/tree/main/skills/mcp-builder
[artifacts]: https://github.com/anthropics/skills/tree/main/skills/web-artifacts-builder
[algorithmic-art]: https://github.com/anthropics/skills/tree/main/skills/algorithmic-art
[canvas-design]: https://github.com/anthropics/skills/tree/main/skills/canvas-design
[slack-gif-creator]: https://github.com/anthropics/skills/tree/main/skills/slack-gif-creator
[brand-guidelines]: https://github.com/anthropics/skills/tree/main/skills/brand-guidelines
[internal-comms]: https://github.com/anthropics/skills/tree/main/skills/internal-comms
[creator]: https://github.com/anthropics/skills/tree/main/skills/skill-creator
[template]: https://github.com/anthropics/skills/tree/main/template
[tdd]: https://github.com/obra/superpowers/tree/main/skills/test-driven-development
[debugging]: https://github.com/obra/superpowers/tree/main/skills/systematic-debugging
[verification]: https://github.com/obra/superpowers/tree/main/skills/verification-before-completion
[brainstorming]: https://github.com/obra/superpowers/tree/main/skills/brainstorming
[executing-plans]: https://github.com/obra/superpowers/tree/main/skills/executing-plans
[finishing]: https://github.com/obra/superpowers/tree/main/skills/finishing-a-development-branch
[receiving-review]: https://github.com/obra/superpowers/tree/main/skills/receiving-code-review
[requesting-review]: https://github.com/obra/superpowers/tree/main/skills/requesting-code-review
[worktrees]: https://github.com/obra/superpowers/tree/main/skills/using-git-worktrees
[writing-plans]: https://github.com/obra/superpowers/tree/main/skills/writing-plans
[subagents]: https://github.com/obra/superpowers/tree/main/skills/subagent-driven-development
[writing-skills]: https://github.com/obra/superpowers/tree/main/skills/writing-skills
[waiting]: https://raw.githubusercontent.com/obra/superpowers/main/skills/systematic-debugging/condition-based-waiting.md
[defense]: https://raw.githubusercontent.com/obra/superpowers/main/skills/systematic-debugging/defense-in-depth.md
[tracing]: https://raw.githubusercontent.com/obra/superpowers/main/skills/systematic-debugging/root-cause-tracing.md
[testing-skills]: https://raw.githubusercontent.com/obra/superpowers/main/skills/writing-skills/references/testing-skills-with-subagents.md
[superpowers-catalog]: https://github.com/obra/superpowers/tree/main/skills
[anthropic-install]: https://github.com/anthropics/skills#try-in-claude-code-claudeai-and-the-api
[skill-guide]: https://code.claude.com/docs/en/skills
[plugin-updates]: https://code.claude.com/docs/en/discover-plugins#keep-plugins-updated
[mcp-guide]: https://code.claude.com/docs/en/mcp
[memory-guide]: https://code.claude.com/docs/en/memory
[skills-deep-dive]: https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
[simon-skills]: https://simonwillison.net/2025/Oct/16/claude-skills/
[suggest]: https://github.com/karanb192/awesome-claude-skills/issues/new/choose
[contributors]: https://github.com/karanb192/awesome-claude-skills/graphs/contributors
[blog]: https://karanbansal.in/blog/
