---
name: opening-quiz
description: Opens a specific quiz by filename or generates a quiz from JSON content for immediate study.
---

# Open Quiz

Opens a quiz in the browser using the web application. This skill bridges the gap between generating quiz content and interactively taking the quiz, supporting both existing files and dynamic content.

## When to Use This Skill

- You want to immediately start a quiz session from an existing file.
- You have generated quiz questions and want to preview them interactively.

## What This Skill Does

1.  **Opens Files**: Launches existing JSON quiz files from the application's examples directory.
2.  **Generates Dynamic Quizzes**: Accepts direct JSON content to create and open a quiz on the fly.
3.  **Handles Localization**: Supports opening quizzes in English, French, and Arabic.

## How to Use

### Basic Usage

Use the helper script to open an existing quiz file by name.

```bash
./.claude/opening-quiz/scripts/open-quiz.sh math-quiz.json
```

### Advanced Usage

Pass a JSON string directly to generate a quiz dynamically.

```bash
./.claude/opening-quiz/scripts/open-quiz.sh '{"version":"1.0","metadata":{"title":"Sample Quiz"},"questions":[{"id":"q1","type":"single","question":"Question 1?","options":[{"id":"a","text":"Option A"},{"id":"b","text":"Option B"}],"correctAnswer":"a","explanation":"Explanation for A."},{"id":"q2","type":"multiple","question":"Question 2?","options":[{"id":"a","text":"Option A"},{"id":"b","text":"Option B"}],"correctAnswer":["a","b"],"hint":"Hint text.","explanation":"Explanation for A and B."}]}'
```

You can also specify a locale (en, fr, ar) as a second argument:

```bash
./.claude/opening-quiz/scripts/open-quiz.sh history.json fr
```

## Example

**User**: "Create a brief quiz about [Topic]"

**Output**:

```bash
./.claude/opening-quiz/scripts/open-quiz.sh '{"version":"1.0","metadata":{"title":"[Topic] Quiz"},"questions":[{"id":"1","type":"single","question":"Question text?","options":[{"id":"a","text":"Option A"},{"id":"b","text":"Option B"}],"correctAnswer":"b"}]}'
```

## JSON Template

ALWAYS use this structure when generating a new quiz:

```json
{
  "version": "1.0",
  "metadata": {
    "title": "[Topic] Quiz",
    "description": "Short description"
  },
  "questions": [
    {
      "id": "q1",
      "type": "single", // or "multiple"
      "question": "Question text?",
      "options": [
        { "id": "a", "text": "Option A" },
        { "id": "b", "text": "Option B" }
      ],
      "correctAnswer": "a", // or ["a", "b"] for multiple
      "hint": "Optional hint text",
      "explanation": "Why the answer is correct."
    }
  ]
}
```

## Tips

- **JSON Formatting**: When passing JSON directly, it **must** be minified into a single line string.
- **Large Payloads**: For quiz content exceeding 6000 characters, save it to a file in the `opening-quiz/quizzes` folder (e.g. `opening-quiz/quizzes/YYYY-MM-DD-<quiz-name>.json`).

- **Schema Structure**: The JSON must follow the standard schema with `version`, `metadata`, and `questions` array.

## Common Use Cases

- **Study Sessions**: Quickly spinning up a quiz on a specific topic for revision.
- **Content Creation**: Teachers or creators previewing their quiz content before publishing.
- **Interview Preparation**: Preparing for interviews.
