---
name: agentkit-seo
description: AI agent skill for auditing and optimizing professional digital identity across GitHub, LinkedIn, CV/ATS, and portfolios.
---

# AgentKit SEO

AgentKit SEO is a framework that gives AI agents a source of truth, platform-specific rules, and a repeatable workflow for professional identity optimization. It ensures that AI-generated career content is grounded in verified facts rather than hallucinations.

## When to Use This Skill

- When preparing for a job search or promotion cycle.
- When you need to optimize your GitHub profile and repositories for recruiter visibility.
- When you want to ensure your LinkedIn profile is searchable and recruiter-readable.
- When tailoring a CV or resume for ATS (Applicant Tracking System) parsing.
- When improving the SEO and indexability of a professional web portfolio.

## What This Skill Does

1. **Context Grounding**: Uses a private `agent-context-file` as a single source of truth for verified career facts.
2. **Platform Auditing**: Provides specialized audits for LinkedIn, GitHub, CV/ATS, Portfolios, and X/Twitter.
3. **Optimized Rewriting**: Suggests evidence-backed rewrites that align with platform-specific ranking and discovery algorithms.
4. **Action Planning**: Generates prioritized next actions ranked by impact and missing evidence.

## How to Use

### Basic Usage

```
Use the agentkit-seo-github skill to audit my GitHub profile for hiring visibility.
```

### Advanced Usage

```
Use agentkit-seo-linkedin to rewrite my "About" section using my personal context file at ~/.agentkit-seo/my-context.md. Focus on technical leadership and cloud architecture.
```

## Example

**User**: "Audit my GitHub profile for SEO."

**Output**:
```markdown
### GitHub SEO Audit: [User]

**1. Repository Metadata (High Impact)**
- [x] Description missing for repo "ai-research"
- [ ] Topic tags missing for repo "vector-db-wrapper" (suggested: #ai #vector-db #python)

**2. README Proof Points (Medium Impact)**
- [ ] No direct link to live demo in "portfolio-v2" README.

**Next Actions:**
1. Add descriptions to 3 pinned repos.
2. Add up to 20 topic tags to the main research repo.
```

**Inspired by:** [agentkit-seo](https://github.com/agentkit-seo/agentkit-seo)

## Tips

- Start by creating an `agent-context-file` to keep all platform edits consistent and factual.
- Use specific platform modules (e.g., `agentkit-seo-linkedin`) for more focused rules.
- Provide public URLs for direct inspection when possible.

## Common Use Cases

- Preparing a developer-focused GitHub profile.
- Restructuring a LinkedIn profile for a career pivot.
- Auditing a personal portfolio for AI-engine discovery.
