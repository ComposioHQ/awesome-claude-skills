---
name: mintlify
description: Build, manage, and optimize Mintlify documentation sites. Use this skill when the user wants to create or update documentation using Mintlify — adding pages, configuring navigation, writing MDX content, customizing themes, or deploying a Mintlify docs site.
---

# Mintlify

Build and manage documentation sites using Mintlify.

## What is Mintlify?

Mintlify is a modern documentation platform that:
- Converts MDX files into beautiful docs sites
- Supports API reference generation (OpenAPI)
- Has built-in search, analytics, and theming
- Deploys automatically from Git

## Project Structure

```
docs/
  mint.json              # Main configuration file
  introduction.mdx       # Pages as MDX files
  quickstart.mdx
  api-reference/
    introduction.mdx
    endpoint/
      get-users.mdx
  guides/
    authentication.mdx
  _snippets/             # Reusable content snippets
    common-params.mdx
  images/                # Static assets
  logo/
    light.svg
    dark.svg
```

## mint.json Configuration

The `mint.json` file controls everything:

```json
{
  "$schema": "https://mintlify.com/schema.json",
  "name": "Your Docs",
  "logo": {
    "dark": "/logo/dark.svg",
    "light": "/logo/light.svg"
  },
  "favicon": "/favicon.svg",
  "colors": {
    "primary": "#2563EB",
    "light": "#3B82F6",
    "dark": "#1D4ED8"
  },
  "topbarLinks": [
    { "name": "Support", "url": "mailto:support@yourcompany.com" }
  ],
  "topbarCtaButton": {
    "name": "Get Started",
    "url": "https://yourapp.com/signup"
  },
  "navigation": [
    {
      "group": "Get Started",
      "pages": ["introduction", "quickstart", "installation"]
    },
    {
      "group": "Guides",
      "pages": ["guides/authentication", "guides/webhooks"]
    },
    {
      "group": "API Reference",
      "pages": ["api-reference/introduction", "api-reference/endpoint/get-users"]
    }
  ],
  "footerSocials": {
    "twitter": "https://twitter.com/yourcompany",
    "github": "https://github.com/yourcompany"
  }
}
```

## MDX Page Format

Every page is an MDX file with frontmatter:

```mdx
---
title: 'Page Title'
description: 'Short description for SEO and card previews'
icon: 'rocket'
---

# Introduction

Content goes here. MDX supports React components inline.

## Section Heading

Regular markdown works as expected.

<Note>
  This is a callout note.
</Note>

<Warning>
  This is a warning callout.
</Warning>

<Tip>
  This is a tip callout.
</Tip>

<Info>
  This is an info callout.
</Info>
```

## Mintlify Components

### Callouts
```mdx
<Note>Informational note</Note>
<Warning>Warning message</Warning>
<Tip>Helpful tip</Tip>
<Info>General info</Info>
```

### Code Blocks
````mdx
```python
def hello():
    print("Hello, world!")
```
````

With filename:
````mdx
```python hello.py
def hello():
    print("Hello, world!")
```
````

### Tabs
```mdx
<Tabs>
  <Tab title="npm">
    ```bash
    npm install package-name
    ```
  </Tab>
  <Tab title="yarn">
    ```bash
    yarn add package-name
    ```
  </Tab>
</Tabs>
```

### Cards
```mdx
<CardGroup cols={2}>
  <Card title="Quickstart" icon="bolt" href="/quickstart">
    Get up and running in 5 minutes.
  </Card>
  <Card title="API Reference" icon="code" href="/api-reference">
    Explore the full API.
  </Card>
</CardGroup>
```

### Steps
```mdx
<Steps>
  <Step title="Install the SDK">
    ```bash
    npm install @yourcompany/sdk
    ```
  </Step>
  <Step title="Initialize">
    Create your client with your API key.
  </Step>
  <Step title="Make your first call">
    Use the SDK to make your first API call.
  </Step>
</Steps>
```

### API Reference Pages (OpenAPI)
```mdx
---
title: 'Get Users'
openapi: 'GET /users'
---
```

Configure OpenAPI source in mint.json:
```json
{
  "openapi": "https://yourapi.com/openapi.json"
}
```

## Local Development

```bash
# Install Mintlify CLI
npm install -g mintlify

# Start local dev server (run from docs directory)
mintlify dev

# Opens at http://localhost:3000
```

## Deployment

Mintlify deploys automatically from Git:
1. Connect GitHub/GitLab repo at dashboard.mintlify.com
2. Point to docs directory in settings
3. Every push to main triggers a deploy

Manual deploy:
```bash
mintlify deploy
```

## Writing Good Documentation

Structure docs pages as:
1. **What it is** — one clear sentence
2. **Why use it** — the problem it solves
3. **Prerequisites** — what they need first
4. **Steps** — numbered, actionable
5. **Examples** — real code that works
6. **Troubleshooting** — common errors and solutions
7. **Next steps** — where to go from here

## Navigation Best Practices

- Group pages logically: "Get Started" → "Guides" → "API Reference"
- Keep navigation shallow (max 2 levels deep)
- Put the most important pages first
- Use clear, descriptive group names

## Notes for Claude

- Always check `mint.json` exists before adding pages — the page must be listed in `navigation`
- MDX files must be referenced in `mint.json` navigation or they won't appear
- Icons use Fontawesome names (e.g., `"rocket"`, `"code"`, `"database"`)
- Images go in the `/images/` or `/logo/` directory and are referenced with absolute paths
