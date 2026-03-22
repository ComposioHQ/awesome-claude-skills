# Contributing to Awesome Claude Skills

Thank you for your interest in contributing to the premier collection of Claude Skills! This guide will help you add new skills that benefit the entire Claude community.

## Before You Start

- Ensure your skill is based on a **real use case**, not a hypothetical scenario.
- Search existing skills to avoid duplicates.
- If possible, attribute the use case to the original person or source.

## Skill Requirements

All skills must:

1. **Solve a real problem** - Based on actual usage, not theoretical applications.
2. **Be well-documented** - Include clear instructions, examples, and use cases.
3. **Be accessible** - Written for non-technical users when possible.
4. **Include examples** - Show practical, real-world usage.
5. **Be tested** - Verify the skill works across Claude.ai, Claude Code, and/or API.
6. **Be safe** - Confirm before destructive operations.
7. **Be portable** - Work across Claude platforms when applicable.

## Skill Structure

Create a new folder with your skill name (use lowercase and hyphens):

```
skill-name/
└── SKILL.md
```

## SKILL.md Template

Use this template for your skill:

```markdown
---
name: skill-name
description: One-sentence description of what this skill does and when to use it.
---

# Skill Name

Detailed description of the skill and what it helps users accomplish.

## When to Use This Skill

- Bullet point use case 1
- Bullet point use case 2
- Bullet point use case 3

## What This Skill Does

1. **Capability 1**: Description
2. **Capability 2**: Description
3. **Capability 3**: Description

## How to Use

### Basic Usage

```
Simple example prompt
```

### Advanced Usage

```
More complex example prompt with options
```

## Example

**User**: "Example prompt"

**Output**:
```
Show what the skill produces
```

**Inspired by:** [Attribution to original source, if applicable]

## Tips

- Tip 1
- Tip 2
- Tip 3

## Common Use Cases

- Use case 1
- Use case 2
- Use case 3
```

## Adding Your Skill to README

1. Choose the appropriate category:
   - Business & Marketing
   - Communication & Writing
   - Creative & Media
   - Development
   - Productivity & Organization

2. Add your skill in alphabetical order within the category:

```markdown
- [Skill Name](./skill-name/) - One-sentence description. Inspired by [Person/Source].
```

3. Follow the existing format exactly - no emojis, consistent punctuation.

## Pull Request Process

1. Fork the repository
2. Create a branch: `git checkout -b add-skill-name`
3. Add your skill folder with SKILL.md
4. Update README.md with your skill in the appropriate category
5. Commit your changes: `git commit -m "Add [Skill Name] skill"`
6. Push to your fork: `git push origin add-skill-name`
7. Open a Pull Request

## Pull Request Guidelines

Your PR should:

- **Title**: "Add [Skill Name] skill"
- **Description**: Explain the real-world use case and include:
  - What problem it solves
  - Who uses this workflow
  - Attribution/inspiration source
  - Example of how it's used

## Code of Conduct

- Be respectful and constructive
- Credit original sources and inspirations
- Focus on practical, helpful skills
- Write clear, accessible documentation
- Test your skills before submitting

## Questions?

Open an issue if you have questions about contributing or need help structuring your skill.

## Attribution

When adding a skill based on someone's workflow or use case, include proper attribution:

```markdown
**Inspired by:** [Person Name]'s workflow
```

or

```markdown
**Credit:** Based on [Company/Team]'s process
```

Examples:
- **Inspired by:** Dan Shipper's meeting analysis workflow
- **Inspired by:** Teresa Torres's content research process
- **Credit:** Based on Notion's documentation workflow

## Skill Categories

### Business & Marketing
Skills for lead generation, competitive research, branding, and business development.

### Communication & Writing
Skills for improving communication, analyzing conversations, and creating content.

### Creative & Media
Skills for working with images, videos, audio, and creative content.

### Development
Skills for software development, documentation, and technical workflows.

### Productivity & Organization
Skills for organizing files, managing tasks, and personal productivity.

---

Thank you for contributing to Awesome Claude Skills!

