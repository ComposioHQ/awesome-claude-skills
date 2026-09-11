---
name: call-notes-to-actions
description: Turns a meeting transcript or rough call notes into a short summary, decisions, an action-item table with owners and due dates, open questions, and a ready-to-send follow-up email. Use when someone asks to summarize a call or meeting, extract action items, write meeting minutes, or draft a follow-up email after a client call.
---

# Call Notes to Actions

Turns a messy transcript or rough notes into a clear record of what was agreed, who does what by when, and a follow-up email that matches it. Built for freelancers, consultants and small teams who run client calls without a dedicated note-taker.

## When to Use This Skill

- After a client or team call, to send a recap with next steps the same day
- When you have a raw transcript (exported from a meeting tool) or rough notes and need clean minutes
- When commitments on a call were vague ("we should look into...") and need owners and dates
- Before a follow-up meeting, to list what is still open

## What This Skill Does

1. **Summarizes the call**: at most three bullets with the outcomes that matter
2. **Separates decisions from open questions**: nothing still under discussion is recorded as agreed
3. **Builds an action table**: owner, verb-first action, due date and status for every commitment
4. **Converts dates**: relative dates like "next Friday" become real dates based on the meeting date
5. **Drafts the follow-up email**: grouped into "We agreed", "I'll", "Could you" and "Still open", matching the action table exactly
6. **Flags assumptions**: inferred owners or dates are marked (proposed) and listed for review before sending

## How to Use

### Basic Usage

```
Summarize this call and draft the follow-up email.
[paste transcript or notes]
```

### Advanced Usage

```
I'm Lina, the freelance copywriter. The call was on Thursday 10 September 2026.
Summarize it, extract action items with owners and due dates, and draft my follow-up email to the client.
[paste transcript with timestamps]
```

## Instructions

### 1. Gather inputs

**Required**: a transcript, notes, or a description of the call.

**Helpful**: meeting date, participants and their roles, which side the user is on (e.g. freelancer vs. client).

Do not ask questions before the first draft. Put unknowns in "To confirm".

### 2. Rules

- **Only extract what was actually said.** Do not invent decisions, owners, or dates.
- If an owner or due date is implied but not stated, fill it in and mark it **(proposed)**.
- Turn vague intentions ("we should look into…", "let's think about…") into action items with owner **TBD** so they don't get lost.
- A **decision** is something agreed; a **question** is something still open. Don't mix them.
- Merge duplicates. Use participants' real names as they appear.
- Relative dates ("next Friday") become real dates computed from the meeting date, or from today if the meeting date is unknown (note this in "To confirm").
- Keep the user's side's commitments and the other side's commitments clearly separated in the email.
- If a transcript includes timestamps, add the timestamp next to each decision.

### 3. Output format

```markdown
# [Meeting title / topic] · [Date]
**Participants:** [Names (role)]

## Summary
- [Most important outcome]
- [Second]
- [Third]

## Decisions
1. [Decision] [timestamp if available]

## Action items
| # | Owner | Action | Due | Status |
|---|---|---|---|---|
| 1 | [Name] | [Verb-first, specific action] | [Date or (proposed) date] | Open |

## Open questions
- [Question]: who will answer: [Name/TBD]

## Risks & concerns raised
- [Concern]: raised by [Name]

---

## Follow-up email

**Subject:** Recap & next steps: [topic], [date]

Hi [Names],

Thanks for your time today. Here's a quick recap so we're aligned.

**We agreed**
- [Decision]

**I'll**
- [User's actions with dates]

**Could you**
- [Other side's actions with dates]

**Still open**
- [Question]

Let me know if I've missed or misunderstood anything.
[Your name]

---
**To confirm** (delete before sending)
- [Proposed owners/dates, unclear points in the notes]
```

### 4. Quality checklist

Verify silently before responding:
- Every action item starts with a verb and has an owner (name, or TBD) and a due date (real, proposed, or TBD)
- Nothing appears that isn't supported by the notes; inferences are marked (proposed)
- Decisions and open questions are not mixed
- Relative dates are converted to real dates
- The email matches the action table exactly
- The summary has at most three bullets

## Example

**User**: "Summarize this call and give me the follow-up email. I'm Lina (freelance copywriter). Call was Thursday 10 September 2026."

```
[00:40] Marc (Head of Marketing): The launch is 1 October, the page has to be ready for the ads team a week before.
[02:30] Marc: Let's go with the free trial as the main headline angle, price second. Unless legal says no.
[03:10] Lina: OK. I'll write two headline options for that angle plus the full first draft.
[04:05] Priya (Product Manager): I can send the feature list and the three customer quotes, I think by Monday.
[05:20] Marc: We should probably look into a comparison table against competitors at some point.
[08:10] Marc: Let's all review the draft together next Friday.
[08:45] Lina: Great, I'll send the draft Wednesday so you have time to read before.
```

**Output** (excerpt):
```markdown
## Decisions
1. Launch is 1 October; page copy ready for the ads team by Thursday 24 September [00:40]
2. Headline angle: free trial first, price second, unless legal says no [02:30]
3. Review the draft together on Friday 18 September [08:10]

## Action items
| # | Owner | Action | Due | Status |
|---|---|---|---|---|
| 1 | Lina | Write two headline options for the free-trial angle and the full first draft | Wed 16 Sept 2026 | Open |
| 2 | Priya | Send the feature list and three customer quotes to Lina | Mon 14 Sept 2026 | Open |
| 3 | Marc (proposed) | Send a calendar invite for the Friday 18 September draft review | Mon 14 Sept 2026 (proposed) | Open |
| 4 | TBD | Look into a competitor comparison table | TBD | Open |

**To confirm**
- The calendar invite owner (Marc) is proposed; nobody was named on the call
- "Next Friday" read as 18 September and "Wednesday" as 16 September
```

## Tips

- Include the meeting date so relative dates convert correctly
- Say which side you are on so the email splits "I'll" and "Could you" correctly
- Keep timestamps in the transcript; they are carried next to each decision
- Review the "To confirm" list before sending: proposed owners were not named on the call

## Common Use Cases

- Client discovery and kickoff call recaps
- Weekly project check-ins
- Sales calls where the prospect agreed next steps
- Internal meetings without a note-taker
