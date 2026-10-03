---
name: writing-standards
description: Selects the right writing standard for a writing task (ASD-STE100, BLUF / Minto Pyramid, assertion-evidence, plain language, PLS, GB/T 9704) and returns a portable style specification. Use when a text needs a style decision, when a named standard is requested, or when a writing task in any format (txt, md, HTML, PPT) should be constrained to a language style.
---

# Writing Standards

This skill answers one question: which writing standard fits this task? It asks three questions. It selects a standard. It returns a style specification. The calling task then writes the content in that style.

The skill does not write content and does not handle file format. That scope boundary keeps it composable: any task (txt, md, HTML, PPT) can call it the same way.

## When to Use This Skill

- A report, paper, slide deck, science post, technical document, official document, or email needs a style decision.
- The user asks which standard or framework fits a scenario.
- The user names a standard (ASD-STE100, Simplified Technical English, plain language, BLUF, Minto Pyramid, assertion-evidence, PLS).
- A larger task must first pick a language style, then write in it.

## What This Skill Does

1. Asks three questions: purpose and reader; scenario; context (format, tone, length).
2. Selects one main standard for structure and one secondary standard for sentences.
3. Returns a style specification: standard name, structure rules, sentence rules, term rules, isolation rules, acceptance checks.

## How to Use

### Basic Usage

```
Which writing standard fits a progress report to my research advisor?
```

### Advanced Usage

```
Write an HTML tutorial about SSH. For the language style, use ASD-STE100
Simplified Technical English. Run this skill first and return the style
specification. Then write the tutorial in that style.
```

## Example

**User**: "I need to present my experiment results to my professor. Pick the style."

**Output**:
```
【style specification】
- Standard: BLUF / Minto Pyramid (structure) + one idea per sentence (sentences)
- Structure: first sentence states the conclusion and the request. Then three
  supporting points. Details last.
- Sentence rules: one idea per sentence. Active voice. Defined terms.
- Acceptance: the reader identifies the decision request within 10 seconds.
```

**Inspired by:** [Andrej Karpathy's ASD-STE100 prompting tip](https://x.com/karpathy/status/2105819303471976479). Full standards archive and sources: [BryleXia/writing-standards](https://github.com/BryleXia/writing-standards).

## Tips

- Name the standard in full when prompting a language model. Full names trigger reliable style transfer.
- Use the "80% path" for ASD-STE100 when the strict word list is too limiting: keep the sentence discipline, drop the vocabulary limit.
- The skill skips its three questions when the context already states the scenario or names the standard.

## Common Use Cases

- A progress report to an advisor: BLUF / Minto Pyramid.
- A slide deck: Assertion-Evidence (one claim per slide plus visual evidence).
- A technical document or handover: ASD-STE100 or its 80% path.
- A plain-language summary of a paper: PLS conventions.
- A Chinese official document: GB/T 9704-2012.
