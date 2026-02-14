---
name: meeting-insights-analyzer
description: Analyzes meeting transcripts and recordings to uncover behavioral patterns, communication insights, and actionable feedback. Identifies when you avoid conflict, use filler words, dominate conversations, or miss opportunities to listen. Perfect for professionals seeking to improve their communication and leadership skills.
---

# Meeting Insights Analyzer

This skill transforms your meeting transcripts into actionable insights about your communication patterns, helping you become a more effective communicator and leader.

## When to Use This Skill

- Analyzing your communication patterns across multiple meetings
- Getting feedback on your leadership and facilitation style
- Identifying when you avoid difficult conversations
- Understanding your speaking habits and filler words
- Tracking improvement in communication skills over time
- Preparing for performance reviews with concrete examples
- Coaching team members on their communication style

## What This Skill Does

1. **Pattern Recognition**: Identifies recurring behaviors across meetings like:
   - Conflict avoidance or indirect communication
   - Speaking ratios and turn-taking
   - Question-asking vs. statement-making patterns
   - Active listening indicators
   - Decision-making approaches

2. **Communication Analysis**: Evaluates communication effectiveness:
   - Clarity and directness
   - Use of filler words and hedging language
   - Tone and sentiment patterns
   - Meeting control and facilitation

3. **Actionable Feedback**: Provides specific, timestamped examples with:
   - What happened
   - Why it matters
   - How to improve

4. **Trend Tracking**: Compares patterns over time when analyzing multiple meetings

## How to Use

### Basic Setup

1. Download your meeting transcripts to a folder (e.g., `~/meetings/`)
2. Navigate to that folder in Claude Code
3. Ask for the analysis you want

### Quick Start Examples

```
Analyze all meetings in this folder and tell me when I avoided conflict.
```

```
Look at my meetings from the past month and identify my communication patterns.
```

```
Compare my facilitation style between these two meeting folders.
```

### Advanced Analysis

```
Analyze all transcripts in this folder and:
1. Identify when I interrupted others
2. Calculate my speaking ratio
3. Find moments I avoided giving direct feedback
4. Track my use of filler words
5. Show examples of good active listening
```

## Instructions

When a user requests meeting analysis:

1. **Discover Available Data**
   - Scan the folder for transcript files (.txt, .md, .vtt, .srt, .docx)
   - Check if files contain speaker labels and timestamps
   - Confirm the date range of meetings
   - Identify the user's name/identifier in transcripts

2. **Clarify Analysis Goals**
   
   If not specified, ask what they want to learn:
   - Specific behaviors (conflict avoidance, interruptions, filler words)
   - Communication effectiveness (clarity, directness, listening)
   - Meeting facilitation skills
   - Speaking patterns and ratios
   - Growth areas for improvement
   
3. **Analyze Patterns**

   For each requested insight:
   
   **Conflict Avoidance**:
   - Look for hedging language ("maybe", "kind of", "I think")
   - Indirect phrasing instead of direct requests
   - Changing subject when tension arises
   - Agreeing without commitment ("yeah, but...")
   - Not addressing obvious problems
   
   **Speaking Ratios**:
   - Calculate percentage of meeting spent speaking
   - Count interruptions (by and of the user)
   - Measure average speaking turn length
   - Track question vs. statement ratios
   
   **Filler Words**:
   - Count "um", "uh", "like", "you know", "actually", etc.
   - Note frequency per minute or per speaking turn
   - Identify situations where they increase (nervous, uncertain)
   
   **Active Listening**:
   - Questions that reference others' previous points
   - Paraphrasing or summarizing others' ideas
   - Building on others' contributions
   - Asking clarifying questions
   
   **Leadership & Facilitation**:
   - Decision-making approach (directive vs. collaborative)
   - How disagreements are handled
   - Inclusion of quieter participants
   - Time management and agenda control
   - Follow-up and action item clarity

4. **Provide Specific Examples**

   For each pattern found, include:
   
   ```markdown
   ### [Pattern Name]
   
   **Finding**: [One-sentence summary of the pattern]
   
   **Frequency**: [X times across Y meetings]
   
   **Examples**:
   
   1. **[Meeting Name/Date]** - [Timestamp]
      
      **What Happened**:
      > [Actual quote from transcript]
      
      **Why This Matters**:
      [Explanation of the impact or missed opportunity]
      
      **Better Approach**:
      [Specific alternative phrasing or behavior]
   
   [Repeat for 2-3 strongest examples]
   ```

5. **Synthesize Insights**

   After analyzing all patterns, provide:
   
   ```markdown
   # Meeting Insights Summary
   
   **Analysis Period**: [Date range]
   **Meetings Analyzed**: [X meetings]
   **Total Duration**: [X hours]
   
   ## Key Patterns Identified
   
   ### 1. [Primary Pattern]
   - **Observed**: [What you saw]
   - **Impact**: [Why it matters]
   - **Recommendation**: [How to improve]
   
   ### 2. [Second Pattern]
   [Same structure]
   
   ## Communication Strengths
   
   1. [Strength 1 with example]
   2. [Strength 2 with example]
   3. [Strength 3 with example]
   
   ## Growth Opportunities
   
   1. **[Area 1]**: [Specific, actionable advice]
   2. **[Area 2]**: [Specific, actionable advice]
   3. **[Area 3]**: [Specific, actionable advice]
   
   ## Speaking Statistics
   
   - Average speaking time: [X% of meeting]
   - Questions asked: [X per meeting average]
   - Filler words: [X per minute]
   - Interruptions: [X given / Y received per meeting]
   
   ## Next Steps
   
   [3-5 concrete actions to improve communication]
   ```

6. **Offer Follow-Up Options**
   - Track these same metrics in future meetings
   - Deep dive into specific meetings or patterns
   - Compare to industry benchmarks
   - Create a personal communication development plan
   - Generate a summary for performance reviews

## Examples

### Example 1: Conflict Avoidance Analysis (Inspired by Dan Shipper)

**User**: "I download all of my meeting recordings and put them in a folder. Tell me all the times I've subtly avoided conflict."

**Output**: 
```markdown
# Conflict Avoidance Patterns

Found 23 instances across 15 meetings where you used indirect 
communication or avoided addressing tensions directly.

## Pattern: Hedging on Critical Feedback

**Frequency**: 8 times across 7 meetings

**Example 1: 1:1 with Sarah** - 00:14:32

**What Happened**:
> "So, I was thinking... maybe we could, like, potentially 
> consider looking at the timeline again? I mean, if you 
> think that makes sense. But whatever you think is best!"

**Why This Matters**:
You needed to address that Sarah's project was behind schedule, 
but the hedging language ("maybe", "potentially", "if you think") 
and the deflection at the end ("whatever you think") made it easy 
for her to miss the urgency.

**Better Approach**:
"Sarah, the project is two weeks behind schedule. We need to 
discuss what's blocking progress and create a new timeline 
today."

[Additional examples...]

## Recommendations

1. **Name the issue directly** in the first sentence
2. **Remove hedging words** like "maybe," "kind of," "sort of"
3. **Ask specific questions** instead of hinting
4. **Schedule difficult conversations** instead of raising them casually
```

### Example 2: Leadership Facilitation

**User**: "Analyze my team meetings and tell me about my facilitation style."

**Output**: Provides insights on:
- How much you speak vs. team members (60% vs. 40%)
- Whether you ask questions or make statements (3:1 ratio)
- How you handle disagreements (tendency to resolve too quickly)
- Who speaks least and whether you draw them in
- Examples of good and missed facilitation moments

### Example 3: Personal Development Tracking

**User**: "Compare my meetings from Q1 vs. Q2 to see if I've improved my listening skills."

**Output**: Creates a comparative analysis showing:
- Decrease in interruptions (8 per meeting → 3 per meeting)
- Increase in clarifying questions (2 → 7 per meeting)
- Improvement in building on others' ideas
- Specific examples showing the difference
- Remaining areas for growth

## Setup Tips

### Getting Meeting Transcripts

**From Granola** (free with Lenny's newsletter subscription):
- Granola auto-transcribes your meetings
- Export transcripts to a folder: [Instructions on how]
- Point Claude Code to that folder

**From Zoom**:
- Enable cloud recording with transcription
- Download VTT or SRT files after meetings
- Store in a dedicated folder

**From Google Meet**:
- Use Google Docs auto-transcription
- Save transcript docs to a folder
- Download as .txt files or give Claude Code access

**From Fireflies.ai, Otter.ai, etc.**:
- Export transcripts in bulk
- Store in a local folder
- Run analysis on the folder

### Best Practices

1. **Consistent naming**: Use `YYYY-MM-DD - Meeting Name.txt` format
2. **Regular analysis**: Review monthly or quarterly for trends
3. **Specific queries**: Ask about one behavior at a time for depth
4. **Privacy**: Keep sensitive meeting data local
5. **Action-oriented**: Focus on one improvement area at a time

## Common Analysis Requests

- "When do I avoid difficult conversations?"
- "How often do I interrupt others?"
- "What's my speaking vs. listening ratio?"
- "Do I ask good questions?"
- "How do I handle disagreement?"
- "Am I inclusive of all voices?"
- "Do I use too many filler words?"
- "How clear are my action items?"
- "Do I stay on agenda or get sidetracked?"
- "How has my communication changed over time?"

## Related Use Cases

- Creating a personal development plan from insights
- Preparing performance review materials with examples
- Coaching direct reports on their communication
- Analyzing customer calls for sales or support patterns
- Studying negotiation tactics and outcomes

