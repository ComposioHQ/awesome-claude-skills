---
name: sudoku-api
description: Generate Sudoku puzzle images through the free Sudoku100 API. Use when the user wants a Sudoku puzzle image, such as "generate a hard Sudoku puzzle", "give me Sudoku puzzle #500", "add a medium Sudoku to this document", or "list Sudoku difficulty levels". Supports 6 difficulty levels, puzzle retrieval by ID, custom width (100-1000px), and PNG/WebP/SVG/JPG output with no API key required.
---

# Sudoku API

Generate and retrieve Sudoku puzzle images through the free Sudoku100 API (`https://www.sudoku100.com`) and embed them in documents, web pages, or chat responses. Every puzzle has a guaranteed unique solution.

## When to Use This Skill

- The user asks for a Sudoku puzzle of any difficulty ("give me an easy Sudoku", "generate an expert-level puzzle")
- The user wants a specific puzzle by ID ("show me puzzle #238")
- The user wants a custom size or format ("800px wide SVG Sudoku")
- The user asks what difficulty levels are available
- Content needs a puzzle illustration (blog posts, worksheets, newsletters, educational material)

## What This Skill Does

1. **Generate puzzles**: Random puzzles or by difficulty (beginner/easy/medium/hard/expert/extreme), each with a unique solution
2. **Retrieve by ID**: Fetch a specific puzzle (1-10000) that always returns the same puzzle
3. **Customize output**: Image width 100-1000px in PNG, WebP, SVG, or JPG
4. **List difficulties**: Show all 6 levels with their hint-count ranges

## How to Use

Run the bundled script via Node.js (>= 16). `invoke` accepts a params object or an OpenAI-style JSON string and validates all inputs.

### Basic Usage

```bash
# Random puzzle (default 500px PNG)
node scripts/sudoku-api-skill.js
```

```
User: "Generate a medium difficulty Sudoku puzzle"
Action: invoke({ action: "generate", difficulty: "medium" })
Result:  https://www.sudoku100.com/sudoku-img/medium?width=500&format=png
```

### Advanced Usage

```javascript
const SudokuApiSkill = require("./scripts/sudoku-api-skill");

// Hard puzzle, 800px, WebP
await SudokuApiSkill.invoke({ action: "generate", difficulty: "hard", width: 800, format: "webp" });
// -> https://www.sudoku100.com/sudoku-img/hard?width=800&format=webp

// Specific puzzle by ID
await SudokuApiSkill.invoke({ action: "get_by_id", id: 238, width: 720, format: "png" });
// -> https://www.sudoku100.com/img-id/238?width=720&format=png

// List difficulty levels
await SudokuApiSkill.invoke({ action: "list_difficulties" });
```

The module also provides LLM tool definitions: `getToolDefinition("openai")`, `getToolDefinition("anthropic")`, or `getToolDefinition("generic")`.

## Example

**User**: "Add an expert Sudoku puzzle to this Markdown doc, 600px wide"

**Output**:
```markdown
![Expert Sudoku Puzzle](https://www.sudoku100.com/sudoku-img/expert?width=600&format=png)
```

**User**: "给我一个中等难度的数独"

**Output**:
```markdown
![Medium Sudoku](https://www.sudoku100.com/sudoku-img/medium?width=500&format=png)
```

## Tips

- The returned URL serves an image directly — embed it in Markdown/HTML as-is or hand it to the user
- No API key or registration is needed; the API is public
- Same `id` always returns the same puzzle; omit `id` for a fresh random puzzle each call
- Difficulty ↔ hint counts: beginner 45-50, easy 38-44, medium 32-37, hard 26-31, expert 20-25, extreme 17-19
- Handle failures by checking `result.success` and surfacing `result.error.message` (error codes: `INVALID_DIFFICULTY`, `INVALID_ID`, `INVALID_WIDTH`, `INVALID_FORMAT`, `MISSING_ID`)

## Common Use Cases

- Educational worksheets and print materials with puzzle images
- Blog posts and newsletters that include a "puzzle of the day"
- Apps or prototypes needing placeholder puzzle images
- Testing layout with grid-based image content
