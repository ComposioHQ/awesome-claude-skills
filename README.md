# Awesome Claude Skills

A curated list of practical Claude Skills for enhancing productivity across Claude.ai, Claude Code, and the Claude API.

## Contents

- [What Are Claude Skills?](#what-are-claude-skills)
- [Skills](#skills)
  - [Business & Marketing](#business--marketing)
  - [Communication & Writing](#communication--writing)
  - [Creative & Media](#creative--media)
  - [Development](#development)
  - [Productivity & Organization](#productivity--organization)
- [Getting Started](#getting-started)
- [Creating Skills](#creating-skills)
- [Contributing](#contributing)
- [Resources](#resources)
- [License](#license)

## What Are Claude Skills?

Claude Skills are customizable workflows that teach Claude how to perform specific tasks according to your unique requirements. Skills enable Claude to execute tasks in a repeatable, standardized manner across all Claude platforms.

### Key Features

- **Composable** - Combine multiple skills for complex workflows.
- **Portable** - Use the same skill across Claude.ai, Claude Code, and the API.
- **Efficient** - Claude loads only what's needed for optimal performance.
- **Powerful** - Include executable code for technical reliability.

Skills can codify your organization's processes, brand guidelines, workflows, and expertise into reusable components that Claude applies automatically when needed.

## Skills

### Business & Marketing

- [Brand Guidelines](./brand-guidelines/) - Applies Anthropic's official brand colors and typography to artifacts for consistent visual identity and professional design standards.
- [Competitive Ads Extractor](./competitive-ads-extractor/) - Extracts and analyzes competitors' ads from ad libraries to understand messaging and creative approaches that resonate.
- [Domain Name Brainstormer](./domain-name-brainstormer/) - Generates creative domain name ideas and checks availability across multiple TLDs including .com, .io, .dev, and .ai extensions.
- [Internal Comms](./internal-comms/) - Helps write internal communications including 3P updates, company newsletters, FAQs, status reports, and project updates using company-specific formats.
- [Lead Research Assistant](./lead-research-assistant/) - Identifies and qualifies high-quality leads by analyzing your product, searching for target companies, and providing actionable outreach strategies.

### Communication & Writing

- [Content Research Writer](./content-research-writer/) - Assists in writing high-quality content by conducting research, adding citations, improving hooks, and providing section-by-section feedback.
- [Meeting Insights Analyzer](./meeting-insights-analyzer/) - Analyzes meeting transcripts to uncover behavioral patterns including conflict avoidance, speaking ratios, filler words, and leadership style.

### Creative & Media

- [Canvas Design](./canvas-design/) - Creates beautiful visual art in PNG and PDF documents using design philosophy and aesthetic principles for posters, designs, and static pieces.
- [Image Enhancer](./image-enhancer/) - Improves image and screenshot quality by enhancing resolution, sharpness, and clarity for professional presentations and documentation.
- [Slack GIF Creator](./slack-gif-creator/) - Creates animated GIFs optimized for Slack with validators for size constraints and composable animation primitives.
- [Theme Factory](./theme-factory/) - Applies professional font and color themes to artifacts including slides, docs, reports, and HTML landing pages with 10 pre-set themes.
- [Video Downloader](./video-downloader/) - Downloads videos from YouTube and other platforms for offline viewing, editing, or archival with support for various formats and quality options.

### Development

- [Artifacts Builder](./artifacts-builder/) - Builds elaborate, multi-component Claude.ai HTML artifacts using modern frontend technologies including React, Tailwind CSS, and shadcn/ui.
- [Changelog Generator](./changelog-generator/) - Automatically creates user-facing changelogs from git commits by analyzing history and transforming technical commits into customer-friendly release notes.
- [D3.js Visualization](https://github.com/chrisvoncsefalvay/claude-d3js-skill) - Teaches Claude to produce D3 charts and interactive data visualizations. *By [@chrisvoncsefalvay](https://github.com/chrisvoncsefalvay)*
- [FFUF Web Fuzzing](https://github.com/jthack/ffuf_claude_skill) - Integrates the ffuf web fuzzer so Claude can run fuzzing tasks and analyze results for vulnerabilities. *By [@jthack](https://github.com/jthack)*
- [iOS Simulator](https://github.com/conorluddy/ios-simulator-skill) - Enables Claude to interact with iOS Simulator for testing and debugging iOS applications. *By [@conorluddy](https://github.com/conorluddy)*
- [MCP Builder](./mcp-builder/) - Guides creation of high-quality MCP (Model Context Protocol) servers for integrating external APIs and services with LLMs using Python or TypeScript.
- [Playwright Browser Automation](https://github.com/lackeyjb/playwright-skill) - Model-invoked Playwright automation for testing and validating web applications. *By [@lackeyjb](https://github.com/lackeyjb)*
- [Skill Creator](./skill-creator/) - Provides guidance for creating effective Claude Skills that extend capabilities with specialized knowledge, workflows, and tool integrations.
- [Skill Seekers](https://github.com/yusufkaraaslan/Skill_Seekers) - Automatically converts any documentation website into a Claude AI skill in minutes. *By [@yusufkaraaslan](https://github.com/yusufkaraaslan)*
- [Webapp Testing](./webapp-testing/) - Tests local web applications using Playwright for verifying frontend functionality, debugging UI behavior, and capturing screenshots.

### Productivity & Organization

- [CSV Data Summarizer](https://github.com/coffeefuelbump/csv-data-summarizer-claude-skill) - Automatically analyzes CSV files and generates comprehensive insights with visualizations without requiring user prompts. *By [@coffeefuelbump](https://github.com/coffeefuelbump)*
- [File Organizer](./file-organizer/) - Intelligently organizes files and folders by understanding context, finding duplicates, and suggesting better organizational structures.
- [Invoice Organizer](./invoice-organizer/) - Automatically organizes invoices and receipts for tax preparation by reading files, extracting information, and renaming consistently.
- [Markdown to EPUB Converter](https://github.com/smerchek/claude-epub-skill) - Converts markdown documents and chat summaries into professional EPUB ebook files. *By [@smerchek](https://github.com/smerchek)*
- [NotebookLM Integration](https://github.com/PleasePrompto/notebooklm-skill) - Lets Claude Code chat directly with NotebookLM for source-grounded answers based exclusively on uploaded documents. *By [@PleasePrompto](https://github.com/PleasePrompto)*
- [Raffle Winner Picker](./raffle-winner-picker/) - Randomly selects winners from lists, spreadsheets, or Google Sheets for giveaways and contests with cryptographically secure randomness.

## Getting Started

### Using Skills in Claude.ai

1. Navigate to your Claude.ai account
2. Go to Settings → Skills
3. Upload or create a new skill
4. The skill will be available automatically when relevant to your conversations

### Using Skills in Claude Code

1. Install Claude Code:
   ```bash
   # Mac
   curl -fsSL https://claude.ai/install.sh | bash
   
   # Windows
   irm https://claude.ai/install.ps1 | iex
   ```

2. Navigate to the skill folder:
   ```bash
   cd awesome-claude-skills/lead-research-assistant
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

## License

This repository is licensed under the Apache License 2.0.

Individual skills may have different licenses - please check each skill's folder for specific licensing information.

---

**Note**: Claude Skills work across Claude.ai, Claude Code, and the Claude API. Once you create a skill, it's portable across all platforms, making your workflows consistent everywhere you use Claude.
