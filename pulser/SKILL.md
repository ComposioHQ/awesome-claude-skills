---
name: pulser
description: Diagnose Claude Code skills against Anthropic's 7 principles. Scans SKILL.md files, checks 8 rules (gotchas, description, allowed-tools, file-size, structure, frontmatter, conflicts, usage-hooks), classifies skill types, and generates prescriptions. Use when checking skill quality, auditing skills, or before publishing skills. Triggers on "스킬 점검", "스킬 진단", "check skills", "audit skills", "skill health", "pulser".
disable-model-invocation: false
allowed-tools: Bash(pulser *), Bash(npx pulser-cli *), Read, Edit
---

# Pulser — Skill Diagnostics

Run pulser to diagnose Claude Code skills, then present results conversationally.

## How to Run

```bash
pulser --format json ~/.claude/skills/
```

If `pulser` is not installed globally, use:
```bash
npx pulser-cli --format json ~/.claude/skills/
```

For a single skill:
```bash
pulser --format json --skill <name> ~/.claude/skills/
```

## How to Present Results

1. Run the command above and capture JSON output
2. Parse the JSON result
3. Present a **conversational summary**:
   - Total skills, score, healthy/warning/error counts
   - Top issues (max 5) with skill name + issue
   - "Fix these issues?" prompt
4. If user says yes, apply prescriptions one by one:
   - Show the before/after diff
   - Ask for confirmation
   - Apply via Edit tool (NOT via --fix flag — you have more context than the CLI)

## Summary Format

```
스킬 진단 완료:

📊 30개 스킬 스캔 | Score: 76/100
✓ 22 healthy  ⚠ 6 warnings  ✗ 2 errors

주요 이슈:
1. cardnews — Gotchas 없음, allowed-tools 미설정
2. geo-audit — 338줄 단일파일, Gotchas 없음
3. detailpage — Gotchas 없음, allowed-tools 미설정

고칠까요?
```

## When Fixing

Use the prescription data from JSON. For each fix:
- Read the actual SKILL.md file
- Apply the suggested change using Edit tool
- Verify the change makes sense in context
- You can improve on the template prescriptions — you understand the skill's purpose

## Gotchas

1. Do not dump raw JSON to the user — always summarize conversationally
2. If pulser is not installed, suggest `npm install -g pulser-cli` first
3. For --fix operations, use Edit tool directly rather than CLI --fix (you have better context)
4. Score below 50 is critical — highlight urgently
5. Don't fix all skills at once — group by priority, confirm with user
