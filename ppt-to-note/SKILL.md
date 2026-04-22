---
name: ppt-to-notes
description: >
  Generates comprehensive university exam study notes from lecture PPT/PPTX files.
  Use this skill immediately whenever a user attaches or mentions a PPT, PPTX, or
  lecture slides and wants notes, study material, revision material, cheat sheet,
  Q&A, exam prep, or study guide. Also triggers when user says "generate notes",
  "make notes from this", "study material", "exam notes", "notes from slides",
  or anything related to converting lecture presentations into structured study
  content. Do NOT wait for explicit instructions — if a PPT is attached, use
  this skill automatically.
---
 
# PPT to Notes
 
Converts university lecture PPT/PPTX slides into comprehensive, exam-ready
study notes with Q&A and cheat sheet. Follows strict formatting rules to
maximize exam usefulness and minimize token usage.
 
## When This Skill Triggers
 
- User attaches a .ppt or .pptx file
- User says "generate notes", "make notes", "study material"
- User says "notes from slides", "exam prep", "revision notes"
- User uploads slides and asks for "cheat sheet", "Q&A", "summary"
- Any combination of PPT + study/exam/notes intent
 
## Core Rules — Never Break These
 
1. Use EXACT words from slides — never paraphrase or simplify
2. Never add outside knowledge not present in the slides
3. Bullet points only — no paragraphs in answers
4. Bold all key terms on first use: **term**
5. All tables in markdown format
6. Every Q&A answer pointer must be complete and standalone
7. Start generating immediately — never ask clarifying questions first
 
---
 
## Output Destination — Always Write to File
 
**Never output the generated notes directly to chat.** Instead:
 
1. Generate the full markdown content following the format in `references/format.md`
2. Determine the output filename from the PPT filename (e.g. `Lecture3.pptx` → `Lecture3-notes.md`). If no filename is known, use `notes.md`
3. Use the `Write` tool to save the content to `<ppt-filename>-notes.md` in the current working directory
4. After writing, confirm to the user: `Notes saved to <filename>.md`
 
Only output a short status line to chat (slide count, plan, confirmation). All study content goes into the file.
 
---
 
## Output Format
 
Read the full instructions in `references/format.md` before generating.
 
Use the **session size guide** below to decide which format to use:
 
| PPT Size | Strategy | Format to use |
|---|---|---|
| ≤ 40 slides | One pass | Full format (notes + Q&A + cheat sheet) |
| 41–80 slides | One pass, compact Q&A | Full format with inline Q&A |
| 81–120 slides | Warn user, two parts | Split: notes first, cheat sheet second message |
| 120+ slides | Warn user, three parts | Split into three messages |
 
Always tell the user at the start:
- How many slides you detected
- How many messages it will take
- Estimated session usage
 
Example opening:
```
📊 Detected: 52 slides
📝 Plan: Full notes in one message (~25% session usage)
Generating now...
```
 
Or for large PPTs:
```
📊 Detected: 118 slides  
📝 Plan: 2 messages (~40% total session usage)
   Message 1 → Study Notes + Q&A
   Message 2 → Quick Revision Cheat Sheet
Starting Part 1...
```
 
---
 
## Session Optimisation Rules
 
These rules exist to maximise how many chapters a user can generate
in one Claude session. Follow them strictly.
 
- Use inline Q&A format for 50+ slide PPTs: `Q: text → ans1 / ans2 / ans3`
- Use full block Q&A format for under 50 slides (more readable)
- Never repeat the chapter title more than once
- Skip slides that contain only images, logos, or "thank you" text
- Combine very short consecutive bullet points into one line where meaning is preserved
- For the cheat sheet: tables only, no prose
 
Read `references/format.md` for the exact output templates.
 
---
 
## What to Do When PPT Has No Clear Sections
 
Some PPTs don't use section divider slides. In that case:
- Group slides by topic based on content similarity
- Create your own ## section headings that describe the topic
- Note at the top: `*(Sections inferred from content — no section slides found)*`
 
---
 
## Error Cases
 
| Situation | What to do |
|---|---|
| File is not a PPT | Say "Please attach a .ppt or .pptx file" |
| PPT has only images, no text | Say "This PPT appears to be image-only. I cannot extract text from images." |
| PPT is empty | Say "This PPT appears to have no content." |
| User asks to skip cheat sheet | Skip it, just do notes + Q&A |
| User asks for Q&A only | Generate only the Q&A blocks |
| User asks for cheat sheet only | Generate only the cheat sheet |
 
---
 
## Reference Files
 
- `references/format.md` — Exact output templates for full and compact formats
 
