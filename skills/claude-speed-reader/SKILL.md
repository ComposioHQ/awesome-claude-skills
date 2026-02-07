---
name: claude-speed-reader
description: Speed read Claude's responses at 600+ WPM using RSVP with Spritz-style ORP highlighting.
---

# Claude Speed Reader

Speed read any text using Rapid Serial Visual Presentation (RSVP) with Spritz-style Optimal Recognition Point (ORP) highlighting.

## When to Use This Skill

- After receiving a long Claude response you want to read quickly
- When reviewing documentation or articles
- When you want to improve reading speed with proven speed-reading techniques

## What This Skill Does

1. **RSVP Display**: Shows one word at a time at high speed (100-1500 WPM)
2. **ORP Highlighting**: Red focus letter positioned ~1/3 into each word where eyes naturally focus
3. **Fixed Focus Point**: Words flow around the stationary ORP, eliminating eye movement

## How to Use

### Basic Usage

```
/speed
```

Launches the speed reader with Claude's last response.

### Custom Text

```
/speed "Your text here"
```

## Controls

- **Space**: Play/Pause
- **← →**: Adjust speed (±50 WPM)
- **R**: Restart
- **V**: Paste new text

## Example

**User**: `/speed`

**Output**: Opens browser with RSVP reader displaying the previous response at 600 WPM.

**Inspired by:** Spritz speed reading technology and the ORP algorithm from [speedread](https://github.com/pasky/speedread).

## Tips

- Start at 400-500 WPM and gradually increase
- The red letter is the Optimal Recognition Point - keep your eyes fixed there
- Punctuation automatically adds slight pauses for comprehension

## Common Use Cases

- Reading long Claude explanations quickly
- Reviewing documentation
- Speed-reading articles or text files
