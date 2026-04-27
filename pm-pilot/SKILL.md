---
name: pm-pilot
description: Claude Code configured as a product management copilot. 25 ready-to-install skills for meeting prep, PRDs, stakeholder intel, bug triage, and product discovery.
---

# PM Pilot

A complete product management skill pack for Claude Code. PM Pilot gives product managers 25 purpose-built skills that handle the repetitive, time-consuming parts of the job - so you can focus on decisions, not deliverables.

## When to Use This Skill

- Preparing for meetings with stakeholder context and talking points
- Writing or reviewing PRDs, one-pagers, and product specs
- Triaging bugs and prioritizing backlogs
- Researching competitors, market sizing, or customer segments
- Translating technical docs into PM-friendly language
- Running product discovery workflows
- Generating weekly status updates from git history and project tools

## What This Skill Does

1. **Meeting Prep**: Pulls context from calendars, notes, and project tools to generate briefing docs with talking points, open questions, and attendee intel.
2. **PRD Writing**: Guides you through braindump-first product specs - surfaces tensions and assumptions before applying structure.
3. **Bug Triage**: Reads bug backlogs, groups by theme, identifies quick wins, and suggests priority order based on impact and effort.
4. **Stakeholder Intel**: Builds context profiles for people you work with - their priorities, communication style, and recent interactions.
5. **Product Discovery**: Structured discovery workflows including customer journey mapping, user story mapping, and market sizing.
6. **Status Generation**: Auto-generates weekly accomplishment reports from commit history, meeting notes, and task completions.
7. **Tech-to-PM Translation**: Converts developer documentation, architecture diagrams, and technical RFCs into language product teams can act on.

## How to Use

### Basic Usage

```
Prep me for my 2pm meeting with the engineering leads. Pull context from recent notes and open issues.
```

### Advanced Usage

```
I need a PRD for a new onboarding flow. Start with a braindump session - ask me the hard questions before we write anything. Then structure it using our standard template.
```

```
Analyze our bug backlog. Group by theme, flag quick wins under 2 hours, and give me a recommended priority order for the next sprint.
```

## Example

**User**: "I have a meeting with the VP of Engineering in 30 minutes. What should I know?"

**Output**:
```
Meeting Brief: VP Engineering Sync

Context:
- Last meeting (Mar 28): discussed API latency concerns, agreed on 
  performance audit timeline
- Open items: 3 PRs awaiting review from their team, deployment 
  freeze ends Friday
- Recent activity: their team shipped the caching layer last week, 
  2 incidents in monitoring

Suggested talking points:
1. Performance audit results - are we on track for the April deadline?
2. PR review bottleneck - 3 PRs older than 5 days
3. Post-incident review from Tuesday's outage

Open questions to prepare for:
- They may ask about Q3 roadmap priorities
- Likely follow-up on headcount request from last month
```

**Inspired by:** Shadman Rahman's PM workflow - built from 14 years of product leadership across B2B and B2C teams.

## Tips

- Start with meeting prep and PRD writing - these save the most time on day one
- The braindump-first approach for PRDs surfaces better requirements than jumping straight to a template
- Combine with calendar and note-taking integrations (Granola, Google Calendar) for richer context
- Skills work independently - install only the ones that match your workflow
- Bug triage works best when pointed at a real backlog export or issue tracker

## Common Use Cases

- Daily meeting prep across multiple stakeholder groups
- Writing product specs and one-pagers from rough ideas
- Sprint planning support with bug triage and priority recommendations
- Competitive research and market sizing for new initiatives
- Translating engineering RFCs into product impact summaries
- Generating weekly status updates for leadership
- Customer journey mapping for discovery workshops
