---
name: ai-slop-detection
description: Analyze text for AI-generated writing patterns using a research-backed corpus of 300+ linguistic markers. Detects vocabulary overuse, templated phrases, structural tells, and grammatical fingerprints across four severity levels.
---

# AI Slop Detection

Analyze any text for signs of AI generation using a corpus of 300+ linguistic markers compiled from peer-reviewed research. Returns a scored breakdown across vocabulary, phrasing, structure, and grammar — with specific evidence from the text.

**Inspired by:** Sujay Choubey's [Slop Detector](https://slop-detector-six.vercel.app) and the LLM Slop Detection Corpus (February 2026).

## When to Use This Skill

- Reviewing submitted content for AI generation before publishing
- Auditing your own writing to strip AI-sounding patterns
- Evaluating AI-assisted drafts before sending to clients
- Fact-checking whether a piece was written by the claimed author
- Training yourself to write less like an LLM

## What This Skill Does

1. **Vocabulary scan**: Flags overused words with documented frequency spikes post-ChatGPT (delve, landscape, robust, pivotal, seamless, etc.)
2. **Phrase detection**: Identifies templated openings and transitions ("in today's fast-paced world", "it's worth noting that", "let's dive in")
3. **Structural analysis**: Checks em dash frequency, rule-of-three overuse, sentence length uniformity, chatbot salutations
4. **Grammatical fingerprinting**: Flags present participial clause density (GPT-4o uses these 5.3× more than humans, per PNAS 2025), nominalization preference, and pronoun/auxiliary ratios

## How to Use

### Basic Usage

```
Analyze this text for AI writing patterns: [paste text]
```

### Full Scored Analysis

```
Run an AI slop detection analysis on the following text. Score it 0–100 and break down findings by: vocabulary overuse, templated phrases, structural patterns, and grammatical markers. Flag specific examples from the text.

[paste text]
```

### Targeted Check

```
Check this text specifically for: [e.g., "significance inflation and chatbot artifacts"]

[paste text]
```

### Rewrite Mode

```
Identify the top 5 AI slop patterns in this text, then rewrite each flagged sentence to sound human:

[paste text]
```

## Example

**User**: "Analyze this for AI slop: In today's fast-paced digital landscape, it's important to note that robust solutions are pivotal for seamless operations. Moreover, organizations must leverage cutting-edge technology to unlock their full potential."

**Output**:
```
AI Slop Score: 78/100 — High confidence (94 words analyzed)

CRITICAL
- Chatbot metacommentary: "it's important to note that" (1×) — 5 pts

HIGH
- Templated opening: "In today's fast-paced digital landscape" (1×) — 3 pts
- Significance inflation: "pivotal" (1×) — 3 pts
- Verb overuse: "leverage", "unlock" (2×) — 3 pts

MODERATE
- Emphatic adjectives: "robust", "seamless", "cutting-edge" (3×) — 2 pts each
- Transition overuse: "Moreover" (1×) — 2 pts

Vocabulary: 38/50 | Structure: 20/30 | Grammar: 8/20
```

## Scoring Rubric

| Range | Label | Meaning |
|-------|-------|---------|
| 0–25 | Likely human | Low pattern frequency |
| 26–50 | Possibly AI-assisted | Some markers present |
| 51–75 | Likely AI-generated | Multiple pattern clusters |
| 76–100 | Almost certainly AI | Heavy pattern density |

Confidence scales with word count: 50+ words = low, 100+ = medium, 250+ = high.

## Pattern Reference

### Critical markers (5 pts each)
- Technical artifacts: `turn0search0` placeholder codes
- Chatbot closings: "hope this helps", "feel free to ask", "let me know if you need anything"
- Chatbot openings: "dear reader", "dear wikipedia editors"
- The delve cluster: "delve into", "dive into", "deep dive" (spiked 50%+ post-ChatGPT, FSU 2025)

### High confidence markers (3 pts each)
- Significance inflation: "stands as a testament to", "plays a vital role", "underscores the importance"
- Templated openings: "in today's fast-paced world", "in a world where", "with the rise of"
- Action verb overuse: "unlock the power of", "harness", "leverage", "transform"
- Abstract nouns: "landscape", "realm", "tapestry", "journey", "paradigm shift"
- Emphatic adjectives: "robust", "pivotal", "seamless", "comprehensive", "cutting-edge"

### Moderate markers (2 pts each)
- Transition overuse: "moreover", "furthermore", "additionally", "consequently"
- Faux-conversational: "let's dive in", "here's the thing", "let's face it"
- Metacommentary: "it's worth noting", "it's important to note", "no discussion would be complete without"

### Structural markers (variable)
- Em dash density > 5 per 1,000 words (humans average 0–3)
- Sentence length variance < 0.3 coefficient of variation (uniform = AI)
- Rule-of-three clustering: repeated X, Y, and Z groupings
- Uniform paragraph length (AI tends toward equal-sized blocks)

### Grammatical markers
- Present participial clause density > 3 per paragraph
- Nominalization preference: "the implementation of" over "implementing"
- Pronoun + auxiliary verb stacking

## Research Basis

| Finding | Source |
|---------|--------|
| GPT-4o uses participial clauses 5.3× more than humans | PNAS, 2025 |
| "Delve" spiked 50%+ in published essays since ChatGPT | FSU Research, February 2025 |
| "Robust", "pivotal" usage up 50%+ in academic writing | Academic corpus studies, 2024 |
| Transformer-based detection: 38× lower error than rule-based | Pangram Technical Report, arXiv 2402.14873 |
| AI text emotionally flattened (more joy, less fear/disgust) | PMC Contrasting Linguistic Patterns, 2024 |
| LLMs have distinct, persistent stylistic fingerprints | arXiv 2503.01659, 2025 |

## Tips

- Minimum 50 words for reliable analysis; 250+ for high confidence
- Short texts (tweets, headlines) produce false positives — adjust expectations
- Technical documentation and academic writing have higher baseline scores; calibrate accordingly
- Patterns decay over time: "delve" and em dash overuse are declining in GPT-5.x models; grammatical fingerprints (participial clauses, nominalization) are more durable
- Absence of negative emotion and personal uncertainty is often more diagnostic than vocabulary alone

## Common Use Cases

- Content agencies validating freelancer submissions
- Academic integrity review (supplement, not replacement, for institutional tools)
- Self-editing: paste your AI-assisted draft and strip the flagged patterns before sending
- Journalism: checking PR-submitted quotes and press releases
- Hiring: reviewing AI-polished cover letters for authentic voice

## Sources

1. [PNAS: Do LLMs write like humans?](https://www.pnas.org/doi/10.1073/pnas.2422455122) — 2025
2. [FSU: Why Does ChatGPT "Delve" So Much?](https://news.fsu.edu/news/science-technology/2025/02/17/why-does-chatgpt-delve-so-much-fsu-researchers-begin-to-uncover-why-chatgpt-overuses-certain-words/) — February 2025
3. [Pangram Technical Report](https://arxiv.org/abs/2402.14873) — arXiv 2402.14873
4. [PMC: Contrasting Linguistic Patterns in Human and LLM Text](https://pmc.ncbi.nlm.nih.gov/articles/PMC11422446/) — 2024
5. [Wikipedia: Signs of AI Writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing) — 2025
6. [Blake Stockton: Don't Write Like AI](https://www.blakestockton.com/red-flag-words/) — 2025
7. [arXiv: Detecting Stylistic Fingerprints of LLMs](https://arxiv.org/html/2503.01659v1) — 2025
