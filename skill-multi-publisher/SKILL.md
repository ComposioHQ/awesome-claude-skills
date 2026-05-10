---
name: skill-multi-publisher
description: One-command publish a Claude Code skill to ALL major marketplaces — GitHub (npx skills), ClawHub, and community directories (composiohq/awesome-claude-skills, anthropics/skills, daymade/claude-code-skills). Validates, auto-generates files, publishes, and submits PRs.
---

# Skill Multi-Publisher

Publish a skill to ALL major marketplaces with one command. Direct publish to GitHub + ClawHub, then auto-submit PRs to community directories.

## When to Use This Skill

- Publishing a new skill and want maximum reach
- Submitting to multiple community marketplaces at once
- Need to update a skill across all platforms
- Want automated PR submission to awesome-claude-skills, anthropics/skills, etc.

## What This Skill Does

1. **Validate**: Check SKILL.md frontmatter (name, version, description)
2. **Auto-Generate**: Create LICENSE and README.md if missing
3. **GitHub**: Create public repo and push (npx skills discoverable)
4. **ClawHub**: Publish via clawhub CLI
5. **Community PRs**: Fork and submit PRs to major directories:
   - composiohq/awesome-claude-skills (41K+ stars)
   - anthropics/skills (86K+ stars)
   - daymade/claude-code-skills (623 stars)
   - obra/superpowers-marketplace (595 stars)
6. **Report**: Show all published URLs and PR links

## Supported Platforms

| Platform | Stars | Method |
|----------|-------|--------|
| GitHub (npx skills) | - | Direct push |
| ClawHub | - | Direct publish |
| composiohq/awesome-claude-skills | 41K+ | PR |
| anthropics/skills | 86K+ | PR |
| daymade/claude-code-skills | 623 | PR |
| obra/superpowers-marketplace | 595 | PR |
| anthropics/claude-plugins-official | 9.3K | Form |

## How to Use

```
Publish this skill to all platforms
发布skill到所有市场
Submit to awesome-claude-skills
```

## Install

```
npx skills add dongsheng123132/skill-multi-publisher
clawhub install skill-multi-publisher
```
