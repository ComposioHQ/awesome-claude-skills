---
name: edu-role-play
description: Generate self-contained HTML role-play training simulations with rubric-graded transcripts for sales, customer service, compliance, and soft-skills practice — embeddable in any LMS or SCORM course.
---

# Edu Role-Play

Edu Role-Play turns a brief description of a training scenario into a fully functional, self-contained HTML role-play activity. The learner has a live conversation with an AI character (an upset customer, a hesitant prospect, a compliance auditor, a difficult patient), then receives a rubric-graded transcript with feedback against the learning objectives.

The output is a single HTML file you can host anywhere, embed in an iframe, or drop into an LMS or SCORM package. No backend setup, no platform lock-in — just a portable practice block.

## When to Use This Skill

- You need conversation practice for sales, support, leadership, healthcare, or compliance training.
- You want learners to *do* rather than watch — practice a tough conversation instead of reading about it.
- You're authoring an LMS or SCORM course and need an interactive role-play block that scores against a rubric.
- You want a quick prototype to validate a scenario before investing in a full simulation platform.

## What This Skill Does

1. **Designs the persona**: Builds a realistic AI character with a backstory, emotional state, hidden objections, and conversational style.
2. **Writes the rubric**: Generates measurable criteria (e.g., "acknowledged the customer's frustration before offering a solution") that drive the post-session grade.
3. **Produces a working HTML file**: Self-contained simulation with chat UI, transcript capture, and rubric scoring — ready to host or embed.

## How to Use

### Basic Usage

```
Create a role-play where the learner is a CSM handling an angry enterprise customer
who just got a surprise invoice. Grade them on empathy, clarification, and de-escalation.
```

### Advanced Usage

```
Build a role-play for new pharmaceutical reps practicing a first call with a skeptical
oncologist. The character should push back on efficacy data, mention a competitor study,
and only open up if the rep acknowledges patient outcomes first. Rubric: 5 criteria,
weighted, with specific transcript quotes required in feedback. Output a single HTML
file embeddable in SCORM 1.2.
```

## Example

**User**: "Make a role-play for retail managers practicing a tough performance conversation with a chronically late employee."

**Output**:
```
role-play.html  ← single self-contained file

When opened:
  - Scenario brief shown to the learner ("You're meeting with Jordan, who has been
    15+ minutes late 9 times in the last month...")
  - Live chat with "Jordan" — defensive at first, opens up about a childcare issue
    if the learner asks open questions
  - On "End session": rubric-graded transcript
      Stated the specific behavior and impact          [pass]
      Asked at least one open question before advising [pass]
      Agreed on a measurable follow-up                 [fail]
      Score: 7/10 — with quoted lines from the transcript as evidence
```

**Inspired by:** Mini Course Generator's open-source learning-skills project, used by L&D teams to ship LMS-ready practice blocks without building a custom simulation platform. See skills.minicoursegenerator.com/role-play/.

## Tips

- **Be specific about the persona's resistance.** "Skeptical doctor" is weak; "skeptical because she's been burned by three reps overselling Phase II data" is the part that makes practice feel real.
- **Write rubric criteria as observable behaviors**, not traits. "Showed empathy" is hard to grade; "named the emotion the character expressed before pivoting to a solution" is gradable from a transcript.
- **Set a turn limit** (e.g., 8–12 exchanges). Open-ended role-plays drift; bounded ones force the learner to make decisions.
- **Test the HTML in the target LMS** before rolling out — SCORM wrappers sometimes block external API calls; if so, host the file standalone and embed via iframe.

## Common Use Cases

- Sales discovery and objection-handling practice
- Customer support de-escalation drills
- Manager 1:1s, feedback conversations, and performance discussions
- Healthcare communication (breaking bad news, motivational interviewing)
- Compliance and ethics scenarios (harassment reporting, conflict of interest)
- Onboarding simulations for new hires before they face real customers
