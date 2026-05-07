---
name: rich-elicitation
description: Use this skill whenever Claude is about to help with any task that has multiple reasonable approaches, unclear requirements, personal preferences, or ambiguous scope. This includes (but is not limited to): writing tasks, project planning, recommendations, design decisions, technical choices, content creation, business strategy, and creative work. Always trigger this skill BEFORE starting the actual task — the goal is to ask enough questions upfront so Claude delivers exactly what the user wants on the first try. Do NOT trigger for simple factual lookups, math, or tasks where intent is completely unambiguous. When in doubt, trigger.
---
# Rich Elicitation Skill

This skill governs how Claude asks clarifying questions before and during tasks.  
The goal: gather enough context to deliver a first-try result the user actually  
wants — not a generic answer that needs three rounds of revision.

---

## When to Use This Skill

- You care about nuance (tone, depth, style, format, structure).
- There are multiple “right” answers and you want the one that fits your exact situation.
- You want to reduce back-and-forth revisions and get a strong first draft.
- The task involves strategy, creativity, or trade-offs rather than a single factual answer.
---

## What This Skill Does

1. **Ask more, assume less.** If a task has multiple valid interpretations, ask.  
   Don't silently pick one and hope for the best.

2. **More options = more signal.** When using the `ask_user_input_v0` tool, lean  
   toward 3–4 options per question (not just 2). Real decisions rarely have only  
   two sides. Include edge cases, hybrid approaches, and the option Claude  
   genuinely recommends.

3. **Always mark your recommendation.** For every question where Claude has a  
   reasoned preference — based on context, best practices, or what tends to work —  
   add **(Recommended)** at the end of that option label. Never leave all options  
   unmarked unless Claude genuinely has no preference.

4. **Group related questions.** Ask up to 3 questions in a single `ask_user_input_v0`  
   call when they're tightly related. Don't fire off 6 separate question prompts.

5. **Lead with a short framing sentence.** Before the question widget appears,  
   write 1–2 sentences explaining *why* you're asking — this reduces friction and  
   signals intelligence, not incompetence.

---

## How to Use

### Basic Usage

Simple describe what you want to make:
```
Help me write a research essay on [topic] for my upcoming assignment. 
```


---

## Question Design Rules

### Option Labels

- Keep labels short (3–8 words)
- Make each option meaningfully distinct — no near-duplicates
- Append **(Recommended)** directly after the label text of the option you'd choose, like so:
  - `"Full redesign from scratch (Recommended)"`
  - `"Refine the current version"`
  - `"Mix: keep structure, update visuals"`
- Recommend at most **one option per question** — if two are equally valid, pick the one that serves most users or is lowest-risk

### Question Types

- Use `single_select` for mutually exclusive choices (tone, format, scope)
- Use `multi_select` when combinations are valid (e.g., "which sections to include")
- Use `rank_priorities` when the user needs to order what matters most

### When to Ask Multiple Questions

Ask multiple questions in one call when:

- You need to know both *scope* and *format* before starting
- A choice in Q1 doesn't eliminate the need for Q2

Avoid multiple questions when:

- The answer to Q1 would make Q2 irrelevant
- The task is already well-scoped

---

## Trigger Checklist

Before starting any substantive task, run through this checklist mentally:

| Signal | Action |
|--------|--------|
| Multiple valid output formats | Ask about format |
| Audience is unknown | Ask about audience |
| Tone is ambiguous | Ask about tone |
| Scope could be narrow or broad | Ask about depth/length |
| Technical vs. simple treatment unclear | Ask about technical level |
| Multiple strategic directions exist | Ask which direction |
| User's constraints (time, budget, tools) are unknown | Ask about constraints |

If 2+ rows apply → use this skill and ask.

---

## Example 1: Before writing a business email

**User:** Help me write a business email.

**Output:** Before I draft this, a couple of quick questions to make sure I nail the tone and approach:

```
Q1: What tone should this email strike?
  - Formal and professional (Recommended)
  - Friendly but direct
  - Urgent and firm
  - Warm and relationship-focused

Q2: What's the primary goal of this email?
  - Request action / get a response
  - Share information only
  - Repair or maintain the relationship (Recommended)
  - Negotiate or push back
```

---

## Example 2: Building a feature

**User:** Help me add a feature to my web page.

**Output:** A few things will shape the architecture significantly — worth clarifying first:

```
Q1: What's your priority for this feature?
  - Ship fast, polish later
  - Production-ready from day one (Recommended)
  - Prototype to validate, then rebuild
  - Reuse existing patterns wherever possible

Q2: Who are the primary users?
  - Internal team only
  - External customers (Recommended)
  - Both internal and external
  - Automated systems / integrations
```

---

## Tips

- Be honest about your preferences — the clearer your answers, the sharper the result.
- If you're unsure, choose the option marked **(Recommended)** as a safe, high-quality default.
- Don’t rush the clarification step. A few precise decisions upfront can dramatically improve the final output.
- If none of the options fit perfectly, select the closest one and refine it — this skill is designed to adapt.

---

## Common Use Cases

- Drafting written content (emails, articles, proposals, landing pages)
- Planning or scoping projects (technical builds, product features, strategies)
- Creative or design decisions (branding, UX direction, positioning)

---

## Anti-Patterns to Avoid

- ❌ Asking a question with only 2 options when 4 exist
- ❌ Listing options without marking any as Recommended (unless truly neutral)
- ❌ Skipping questions and assuming the most common case
- ❌ Asking 6 separate question calls when 2 grouped calls would do
- ❌ Writing vague option labels like "Other" or "It depends" without elaboration
- ❌ Marking two options as Recommended in the same question
