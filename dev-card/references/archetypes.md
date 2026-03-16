# Dev Card Archetypes

Classification rules for assigning a developer archetype from `analyze.py` JSON output,
plus personality copy and card output format.

---

## Table of Contents

1. [Classification Algorithm](#classification-algorithm)
2. [Archetypes](#archetypes)
3. [Card Template](#card-template)

---

## Classification Algorithm

Use `signals` and `commits` from the JSON output. Apply rules **in priority order** — first match wins.

```
signals.is_polyglot = language_count >= 4
signals.is_sprinter = small_commit_ratio >= 0.65  (tiny+small commits)
signals.is_marathon_coder = epic_commit_ratio >= 0.15  (commits ≥500 lines)
commits.is_night_owl = ≥30% of commits between 9pm–4am
commits.is_early_bird = ≥30% of commits between 5am–9am
commits.is_weekend_warrior = ≥40% of commits on Sat/Sun
message_patterns.fix_ratio, feat_ratio, refactor_ratio, wip_ratio
```

### Priority Order

| Priority | Condition | Archetype |
|---|---|---|
| 1 | `wip_ratio >= 0.20` | The Chaos Engineer |
| 2 | `refactor_ratio >= 0.25` | The Refactoring Monk |
| 3 | `fix_ratio >= 0.40` | The Firefighter |
| 4 | `is_polyglot AND language_count >= 4` | The Polyglot |
| 5 | `is_night_owl AND is_marathon_coder` | The Midnight Architect |
| 6 | `is_night_owl` | The Night Owl |
| 7 | `is_early_bird` | The Dawn Deployer |
| 8 | `is_weekend_warrior` | The Weekend Warrior |
| 9 | `is_marathon_coder AND feat_ratio >= 0.4` | The Feature Machine |
| 10 | `is_sprinter` | The Atomic Committer |
| 11 | _(no strong signal — default)_ | The Craftsperson |

---

## Archetypes

### The Chaos Engineer
**When:** `wip_ratio >= 0.20`

> "Your commit history reads like a stream of consciousness. 'wip', 'temp', 'ok this for real this time'. You ship. The question is: does it ship?"

**Tagline examples (pick the most fitting):**
- *"Commits first. Names things later."*
- *"Every branch is an experiment. Every merge is a prayer."*
- *"The test is production. You know this."*

**Stat to highlight:** wip_ratio as %, peak commit hour, avg commit size.

---

### The Refactoring Monk
**When:** `refactor_ratio >= 0.25`

> "You see mess and cannot rest. You have renamed the same variable three times. Each time felt right. The codebase is cleaner for it, even if no feature shipped."

**Tagline examples:**
- *"Leaves code cleaner than they found it. Always."*
- *"Rename. Extract. Simplify. Repeat."*
- *"Features are temporary. Naming conventions are forever."*

**Stat to highlight:** refactor_ratio as %, language depth.

---

### The Firefighter
**When:** `fix_ratio >= 0.40`

> "Your commit history is a blaze you keep running toward. Hotfix. Patch. Bugfix. You are the reason production is still up."

**Tagline examples:**
- *"On call. Always."*
- *"Bug whisperer. Production's last line of defense."*
- *"Fixes things before people know they're broken."*

**Stat to highlight:** fix_ratio as %, commit frequency (total_commits / repo_age_days).

---

### The Polyglot
**When:** `is_polyglot AND language_count >= 4`

> "No language is a stranger. You've shipped in four. You have opinions about all of them."

**Tagline examples:**
- *"Speaks {top_lang}. Also {lang2}, {lang3}, and {lang4}."*
- *"Multilingual. No framework is off limits."*
- *"Collects programming languages like other people collect regrets."*

**Stat to highlight:** language_count, language_percentages (top 3).

---

### The Midnight Architect
**When:** `is_night_owl AND is_marathon_coder`

> "Your best work happens after the world goes to sleep. Large commits, late hours, the quiet of 2am. You don't sprint — you excavate."

**Tagline examples:**
- *"Designs systems at midnight. Ships at 3am."*
- *"Peak performance: when everyone else is asleep."*
- *"Large commits. Late hours. No regrets."*

**Stat to highlight:** peak_hour formatted as time (e.g. "2am"), avg_lines_per_commit.

---

### The Night Owl
**When:** `is_night_owl`

> "Daylight is for meetings. Real work begins after 9pm."

**Tagline examples:**
- *"Commits after midnight like it's a personality trait. (It is.)"*
- *"The standup is at 10am. The code was written at 1am."*
- *"Night mode: always."*

**Stat to highlight:** peak_hour formatted, night commit percentage.

---

### The Dawn Deployer
**When:** `is_early_bird`

> "You're already three commits deep before most people have coffee. The 5am version of you is frighteningly productive."

**Tagline examples:**
- *"Ships before standup. Commits at dawn."*
- *"5am: already in flow. 9am: already done."*
- *"Early riser. First to push. First to merge."*

**Stat to highlight:** peak_hour formatted (e.g. "5am"), peak_day.

---

### The Weekend Warrior
**When:** `is_weekend_warrior`

> "The 9-to-5 is for other people. Your most productive hours are Saturday morning, coffee in hand, no Slack notifications."

**Tagline examples:**
- *"Weekends are for shipping."*
- *"Saturday commits. Sunday deploys."*
- *"The standup is Monday. The work is the weekend before."*

**Stat to highlight:** weekend commit % (day_distribution Sat+Sun / total), peak_day.

---

### The Feature Machine
**When:** `is_marathon_coder AND feat_ratio >= 0.40`

> "You don't fix things — you build things. Large commits. New features. Each PR a milestone."

**Tagline examples:**
- *"Ships big. Ships often."*
- *"Add. Build. Ship. Repeat."*
- *"Commits that move the product forward, not the lint score."*

**Stat to highlight:** feat_ratio as %, avg_lines_per_commit.

---

### The Atomic Committer
**When:** `is_sprinter`

> "Small commits. Clear intent. The git log reads like a story. You have internalized 'commit early, commit often' at a cellular level."

**Tagline examples:**
- *"One commit. One purpose. Always."*
- *"The git log is a changelog. By design."*
- *"Commits like a surgeon: precise, frequent, deliberate."*

**Stat to highlight:** small_commit_ratio as %, total_commits.

---

### The Craftsperson
**When:** _(default — no dominant signal)_

> "Balanced. Consistent. Does the work. The commit history is a quiet record of professionalism. No drama. No chaos. Just shipping."

**Tagline examples:**
- *"Shows up. Writes code. Ships."*
- *"No extremes. Just craft."*
- *"The kind of developer every team wants."*

**Stat to highlight:** dominant_intent (formatted), repo_age_days.

---

## Card Template

Write the card to `dev_card_YYYY-MM-DD.md` in the repo root, then display it inline.

```markdown
# 🃏 Dev Card: {author_name}

## {Archetype Name}

> *"{Tagline — pick the most fitting one for the actual data}"*

---

| | |
|---|---|
| **Languages** | {top languages with %} |
| **Peak Window** | {peak time window, e.g. "5am – 8am" or "11pm – 2am"} |
| **Most Active** | {peak_day} |
| **Commit Style** | {Sprinter / Marathon / Balanced} · avg {avg_lines_per_commit} lines/commit |
| **Dominant Intent** | {feat→ Feature builder / fix→ Bug fixer / refactor→ Refactorer / etc.} |
| **Commits** | {total_commits} across {repo_age_days} days |

---

### What the data says

{2–3 sentences synthesizing the developer's patterns in plain English.
Be specific. Use real numbers. Make it feel like a personality read, not a report.
Example: "K ships big — average commit size is 518 lines. The work happens early,
peaking at 5am on Saturdays. Features dominate (67% of commits), which means
the focus is on building, not maintaining."}

---

*🃏 Generated by `/dev-card` · [Share on X →](https://x.com/intent/tweet?text=Just+got+my+Dev+Card%21+I%27m+%22{URL-encoded archetype name}%22+%23DevCard)*
```

### Formatting Rules

- **Languages**: Show top 3 max. Format as `TypeScript 68% · Python 22% · Shell 10%`. If only 1 language, show it with 100%.
- **Peak Window**: Convert `peak_hour` to a human-readable 2-hour window. E.g. hour 5 → "5am – 7am", hour 23 → "11pm – 1am".
- **Commit Style label**: sprinter → "Sprinter", marathon_coder → "Marathon", both false → "Balanced".
- **Dominant Intent labels**: feat → "Feature builder", fix → "Bug fixer", refactor → "Refactorer", wip → "Chaos mode", docs → "Documentarian", chore → "Maintainer".
- **What the data says**: Always use real numbers from the JSON. Never be vague. Aim for 2–3 punchy sentences.
- **Tone**: Confident, a little cheeky. Like a personality test result written by someone who actually reads code.
