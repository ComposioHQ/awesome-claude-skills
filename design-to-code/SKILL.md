---
name: design-to-code
description: Convert Figma designs to pixel-perfect, production-ready React + TypeScript components using coderio. Features robust error handling, checkpoint recovery, and a streamlined helper script workflow.
---

# Design to Code

High-fidelity UI restoration from Figma designs to production-ready React + TypeScript components.
This skill uses a **robust helper script** to minimize manual errors and ensure pixel-perfect results with TailwindCSS V4.

## When to Use This Skill

- You have a Figma design URL and want to generate a working React component
- You need pixel-perfect conversion of UI designs to production code
- You want a guided, step-by-step process for extracting design structure and props before generating code

## What This Skill Does

1. **Setup**: Initializes the coderio helper script and project environment
2. **Protocol Extraction**: Analyzes the Figma design to generate component structure and extract props with visual accuracy
3. **Code Generation**: Produces production-ready React + TypeScript components that match the design exactly

## How to Use

### Prerequisites

1. **Figma API Token**: Get from Figma → Settings → Personal Access Tokens
2. **Node.js**: Version 18+
3. **coderio**: Installed in `scripts/` folder (handled by Setup phase)


### Basic Usage

```
Use design-to-code skill to convert this design: [Your Figma URL]
The Agent will guide you step-by-step through protocol extraction and code generation.
```

---

## Workflow Overview

```
Phase 0: SETUP    → Create helper script and script environment
Phase 1: PROTOCOL → Generate design protocol (Structure & Props)
Phase 2: CODE     → Generate components and assets
```

---

# Phase 0: Setup

## Step 0.1: Initialize Helper Script

**User Action**: Run these commands to create the execution helper and isolate its dependencies.

```bash
mkdir -p scripts

# 1. Copy script files
# Note: Ensure you have the 'skills/design-to-code/scripts' directory available
cp skills/design-to-code/scripts/package.json scripts/package.json
cp skills/design-to-code/scripts/coderio-skill.mjs scripts/coderio-skill.mjs

# 2. Install coderio in scripts directory (adjust version if needed)
cd scripts && pnpm install && cd ..
```

## Step 0.2: Scaffold Project (Optional)

If starting a new project:

1. Run: `node scripts/coderio-skill.mjs scaffold-prompt "MyApp"`
2. **AI Task**: Follow the instructions output by the command to create files.

---

# Phase 1: Protocol Generation

## Step 1.1: Fetch Data

```bash
# Replace with your URL and Token
node scripts/coderio-skill.mjs fetch-figma "https://figma.com/file/..." "figd_..."
```

**Verify**: `process/thumbnail.png` should exist.

## Step 1.2: Generate Structure

1. **Generate Prompt**:

    ```bash
    node scripts/coderio-skill.mjs structure-prompt > scripts/structure-prompt.md
    ```

2. **AI Task (Structure)**:
    - **ATTACH**: `process/thumbnail.png` (MANDATORY)
    - **READ**: `scripts/structure-prompt.md`
    - **INSTRUCTION**: "Generate the component structure JSON based on the prompt and the attached thumbnail. Focus on visual grouping. **Use text content to name components accurately (e.g. 'SafeProducts', not 'FAQ').**"
    - **SAVE**: Paste the JSON result into `scripts/structure-output.json`.

3. **Process Result**:
    ```bash
    node scripts/coderio-skill.mjs save-structure
    ```

## Step 1.3: Extract Props (Iterative)

1. **List Components**:

    ```bash
    node scripts/coderio-skill.mjs list-components
    ```

2. **For EACH component in the list**:

    a. **Generate Prompt**:

    ```bash
    node scripts/coderio-skill.mjs props-prompt "ComponentName" > scripts/current-props-prompt.md
    ```

    b. **AI Task (Props)**:
    - **ATTACH**: `process/thumbnail.png` (MANDATORY)
    - **READ**: `scripts/current-props-prompt.md`
    - **INSTRUCTION**: "Extract props and state data. Be pixel-perfect with text and image paths."
    - **SAVE**: Paste the JSON result into `scripts/ComponentName-props.json`.

    c. **Save & Validate**:

    ```bash
    node scripts/coderio-skill.mjs save-props "ComponentName"
    # If this fails, re-do step 'b' with better attention to the thumbnail
    ```

---

# Phase 2: Code Generation

## Step 2.1: Plan Tasks

```bash
node scripts/coderio-skill.mjs list-gen-tasks
```

This outputs a list of tasks with indices (0, 1, 2...).

## Step 2.2: Generate Components (Iterative)

**For EACH task index (starting from 0)**:

1. **Generate Prompt**:

    ```bash
    node scripts/coderio-skill.mjs code-prompt 0 > scripts/code-prompt.md
    # Replace '0' with current task index
    ```

2. **AI Task (Code)**:
    - **ATTACH**: `process/thumbnail.png` (MANDATORY)
    - **READ**: `scripts/code-prompt.md`
    - **INSTRUCTION**: "Generate the React component code. Match the thumbnail EXACTLY. **Use STRICT text content from input data, do not hallucinate.**"
    - **SAVE**: Paste the code block into `scripts/code-output.txt`.

3. **Save Code**:
    ```bash
    node scripts/coderio-skill.mjs save-code 0
    # Replace '0' with current task index
    ```

## Step 2.3: Final Integration

Inject the root component into `App.tsx`. Use the path found in the last task of Phase 2.1.

---

# Troubleshooting

- **"Props validation failed"**: The AI generated empty props. Check if `process/thumbnail.png` was attached and visible to the AI. Retry the props generation step.
- **"Module not found"**: Ensure `node scripts/coderio-skill.mjs save-code` was run for the child component before the parent component. Phase 2 must be done in order (0, 1, 2...).
- **"Visuals don't match"**: Did you attach the thumbnail? The AI relies on it for spacing and layout nuances not present in the raw data.
