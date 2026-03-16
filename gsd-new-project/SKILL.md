---
name: gsd-new-project
description: Bootstrap a new project from scratch — scaffold structure, set up tooling, configure environments, and get to a working first commit. Use this skill when the user wants to start a new software project and needs help with initial setup, structure, and configuration.
---

# GSD: New Project

Bootstrap a new project efficiently to reach a working, well-structured starting point.

## Philosophy

Get to a working state fast. Avoid over-engineering the foundation. The best new project setup is one that can be built on immediately.

## Step 1: Understand What's Being Built

Before scaffolding anything, clarify:
- **Type**: Web app? API? CLI? Library? Script? Mobile?
- **Stack**: Language, framework, runtime
- **Scale**: Solo project? Team? Production? Prototype?
- **Existing constraints**: Must use specific tools, deploy targets, org standards?

## Step 2: Initialize the Repository

```bash
# Create directory and initialize git
mkdir project-name && cd project-name
git init

# Set up .gitignore immediately
curl -sL https://www.gitignore.io/api/node,python,macos,vscode > .gitignore
# Or manually create based on stack
```

## Step 3: Project Structure

Establish a clear directory structure based on project type:

**Node.js / TypeScript:**
```
project/
  src/
    index.ts
  tests/
  dist/
  package.json
  tsconfig.json
  .env.example
  README.md
```

**Python:**
```
project/
  src/
    package_name/
      __init__.py
  tests/
  pyproject.toml (or setup.py)
  requirements.txt
  .env.example
  README.md
```

**Full-stack web:**
```
project/
  client/          # frontend
  server/          # backend API
  shared/          # shared types/utils
  docker-compose.yml
  .env.example
  README.md
```

## Step 4: Initialize Package Manager

**Node.js:**
```bash
npm init -y
# or
pnpm init
```

**Python:**
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Step 5: Configure Essential Tooling

At minimum, configure:
- **Linter**: ESLint, Flake8, Ruff
- **Formatter**: Prettier, Black
- **Type checking**: TypeScript, mypy
- **Testing**: Jest, pytest, Vitest

Add to `package.json` scripts:
```json
{
  "scripts": {
    "dev": "...",
    "build": "...",
    "test": "...",
    "lint": "...",
    "format": "..."
  }
}
```

## Step 6: Environment Configuration

Create `.env.example` with all required variables (no values):
```env
DATABASE_URL=
API_KEY=
PORT=3000
NODE_ENV=development
```

Add `.env` to `.gitignore`. Never commit real secrets.

## Step 7: First Commit

```bash
git add .
git commit -m "chore: initial project setup"
```

## Step 8: Connect to Remote

```bash
# Create repo on GitHub/GitLab first, then:
git remote add origin https://github.com/user/project.git
git branch -M main
git push -u origin main
```

## Project README Template

Every project should have a README covering:
```md
# Project Name

One sentence description.

## Setup
## Usage
## Development
## Deployment
## Contributing
```

## Common Stacks Quick Setup

**Express + TypeScript API:**
```bash
npm init -y
npm install express
npm install -D typescript ts-node @types/node @types/express nodemon
npx tsc --init
```

**Next.js:**
```bash
npx create-next-app@latest project-name --typescript --tailwind --app
```

**FastAPI (Python):**
```bash
pip install fastapi uvicorn python-dotenv
```

**React + Vite:**
```bash
npm create vite@latest project-name -- --template react-ts
```

## Notes

- Resist adding dependencies that aren't immediately needed
- Set up CI/CD early — even a simple lint/test on push pays off
- Document the setup process in README as you go, not after
