---
name: dev-card
description: >
  Generate a shareable Developer Identity Card from any git repo. Analyzes commit history,
  language breakdown, coding hours, and commit patterns to assign a developer archetype
  (e.g. "The Midnight Architect", "The Dawn Deployer", "The Firefighter") with a personality
  tagline and stats. Use when the user says: "make my dev card", "generate my dev card",
  "what's my developer archetype", "analyze my coding patterns", "dev card", "who am I as
  a developer", or anything implying a shareable developer identity or personality profile.
---

# Dev Card

Generate a shareable Developer Identity Card — archetype, tagline, and stats — from any git repo.

## Workflow

### Step 1 — Identify the repo root

If the user didn't specify a path, use the current working directory. Confirm it's a git repo. Store as `<repo_root>`.

### Step 2 — Run the analyzer

```bash
cd <skill_dir>/scripts
uv run analyze.py <repo_root> --debug
```

> If `uv` is not available, fall back to: `python3 analyze.py <repo_root> --debug`

This emits a JSON object with three top-level keys: `languages`, `commits`, and `signals`. Copy the full JSON — you'll need it in Step 3.

### Step 3 — Classify the archetype

Open `references/archetypes.md` and:
1. Follow the **Priority Order** table to find the first matching archetype.
2. Pick the **tagline** that best fits the actual data (not just the first listed).
3. Note the **stat to highlight** — this anchors the card in specifics.

### Step 4 — Write the card

Using the **Card Template** from `references/archetypes.md`:
1. Fill in all fields with real values from the JSON. No vague placeholders.
2. Write the **"What the data says"** paragraph: 2–3 sentences, specific numbers, personality read.
3. Write the card to `<repo_root>/dev_card_YYYY-MM-DD.md`.

### Step 5 — Present the card

Display the full card inline in the conversation immediately after writing the file. Tell the user the file path.

## Key Rules

- **Always use real data**: real numbers, real language names, real commit counts. Vagueness kills the effect.
- **Tagline must fit**: don't just pick the first tagline. Read all options and choose the one that resonates with the actual data.
- **The personality paragraph is the payoff**: this is what people screenshot and share. Make it feel like an accurate read, not a generic horoscope.
- **Tone**: confident and a little cheeky — like a personality test written by someone who reads commit logs for fun.

## Resources

- `scripts/analyze.py` — git + language analyzer; outputs JSON metrics to stdout
- `references/archetypes.md` — classification rules, archetype copy, card template, and formatting guide
