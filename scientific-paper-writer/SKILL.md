---
name: scientific-paper-writer
description: Full-lifecycle scientific paper writing assistant. Fetches live journal guidelines, AI authorship policy, word limits, citation format, and LaTeX template for any journal before writing. Audits every draft for 25 AI writing patterns. Verifies every citation via web search. Produces publication-ready prose for Nature, Science, Cell, PNAS, NeurIPS, and any other venue.
allowed-tools: [Read, Write, Edit, Bash, WebSearch, WebFetch, Glob, Grep]
---

# Scientific Paper Writer

A full-lifecycle scientific writing assistant that produces publication-ready manuscripts grounded in live journal requirements and verified literature. Before writing a single sentence, it fetches the target journal's current submission guidelines, AI authorship disclosure policy, and LaTeX template. Every draft is audited against 25 AI writing patterns before delivery. Every citation is confirmed via web search — zero hallucinated references.

## When to Use This Skill

- Drafting or revising a scientific manuscript for any journal or conference
- Checking what a journal currently requires (word limits, AI policy, LaTeX template)
- Running an AI-voice audit on an existing draft to make it read as expert human prose
- Writing grant proposals (NIH R01, ARC Discovery, NSF)
- Writing peer review response letters
- Fixing statistical reporting (missing effect sizes, confidence intervals)
- Preparing a cover letter for journal submission

## What This Skill Does

1. **Journal Intelligence Gathering**: Fetches live author guidelines, AI authorship policy, and LaTeX template for any target journal via WebSearch/WebFetch. Stores results in `journal_profile.yaml` — the single source of truth for all formatting decisions.

2. **Two-Stage Writing**: First builds a structured outline per section, then converts every point to flowing scientific prose. Never delivers bullets in the final manuscript.

3. **Citation Verification**: Confirms every reference exists (author, year, title, journal, DOI) via WebSearch before including it. Flags unverifiable sources explicitly.

4. **AI-Voice Audit**: Checks every draft against 25 AI writing patterns — significance inflation, AI vocabulary (pivotal, landscape, crucial, leverage), synonym cycling, em-dash overuse, generic conclusions, stacked hedges, and more. Rewrites flagged sentences before delivery.

5. **Statistical Completeness**: Reports test statistic + df + exact P-value + effect size + 95% CI for every comparison. No "P < 0.05" without the full picture.

6. **Reporting Guideline Compliance**: Verifies the manuscript against CONSORT, PRISMA, STROBE, ARRIVE, TRIPOD-ML, CARE, STARD, or whichever checklist applies.

## How to Use

### Install

```bash
# From the full skill repo (recommended — includes all 996 lines of guidance):
curl -o ~/.claude/skills/scientific-paper-writer.md \
  https://raw.githubusercontent.com/eniktab/claude-scientific-paper-writer/main/skills/scientific-paper-writer/SKILL.md
```

### Basic Usage

```
Write an Article for Nature Biotechnology on our CRISPR base-editing method.
Data: efficiency.csv (5 cell lines, n=200 each).
Key finding: 94% efficiency in HEK293, 3.2-fold over Cas9 (P < 0.001).
```

### Advanced Usage

```
# AI-voice audit only
Run the AI-voice audit on this draft: [paste text].
List every pattern found with the specific sentence, then rewrite each one.

# Journal requirements lookup
What are the current submission requirements for Nucleic Acids Research, Database Issue?
I need word limits, AI policy, and the LaTeX template.

# Peer review response
Write a complete response letter to these reviewer comments
for my Genome Biology submission: [paste reviewer comments]

# Grant proposal
Write the Specific Aims page and Significance section of an NIH R01
on NAD+ metabolism in aging. FOA: PA-23-065.
```

## Example

**User**: "Write a Methods paper for Genome Biology on our DNA tokenization library. It benchmarks 10x faster than HuggingFace tokenizers on 6 genomic foundation models."

**Output**:
1. Fetches Genome Biology (BioMed Central) author guidelines live
2. Extracts: 4,000-word limit, structured abstract, CC-BY license requirement, AI policy
3. Downloads current BioMed Central LaTeX template
4. Builds `journal_profile.yaml` with all requirements
5. Drafts outline: Abstract → Background → Implementation → Results → Discussion
6. Writes full manuscript in IMRaD format to exact word and figure limits
7. Verifies all citations via WebSearch
8. Runs AI-voice audit: removes all significance inflation, AI vocabulary, synonym cycling
9. Delivers `main.tex` using the journal's template class + `main.bib` with verified BibTeX

**Inspired by:** Synthesized from Nature editorial guidelines, Wikipedia's Signs of AI Writing, blader/humanizer (10,800★), Galaxy-Dawn/claude-scholar (2,200★), and K-Dense-AI/claude-scientific-writer (1,300★).

## Tips

- Always name the journal and article type upfront — it triggers the live guidelines fetch
- For the AI-voice audit alone, paste text directly: "Run the AI-voice audit on: [text]"
- The skill distinguishes between biological replicates and technical replicates — specify which n refers to
- For ML papers, explicitly state the number of random seeds used; the skill will flag single-seed benchmarks
- Cover letters for Nature family journals should sound like scientific judgment, not marketing — the skill enforces this

## Common Use Cases

- Revising a draft that reviewers flagged as "reads like it was written by AI"
- Checking word count compliance before submission to a journal with strict limits
- Writing the Specific Aims page for an NIH grant in one session
- Converting a conference paper to a journal article with updated formatting
- Drafting a point-by-point response to major revision comments
