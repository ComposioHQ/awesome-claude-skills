---
name: html-docs-publisher
description: Turn source material into a polished, source-grounded HTML document and publish it to HTML Docs for review, comments, and later updates.
---

# HTML Docs Publisher

Create a self-contained HTML document from the user's source material, verify
it, and publish it through [HTML Docs](https://www.html-docs.com). Use the
active Claude session to research, write, and design the page; use the HTML Docs
CLI only to publish the finished artifact.

## When to Use This Skill

- Publish a report, guide, research brief, or technical explanation as a web page.
- Turn a folder, codebase, website, PDF, document, or pasted material into a reviewable artifact.
- Share AI-generated HTML with collaborators who need inline comments or later revisions.
- Create a durable URL for an explanation without setting up a website project.

## What This Skill Does

1. **Grounds the document** in the supplied material and cites substantive claims.
2. **Authors one portable HTML file** with responsive layout, accessible markup,
   inline CSS, and no required build step.
3. **Checks the artifact** for factual accuracy, readability, keyboard access,
   responsive behavior, and accidental secret exposure.
4. **Publishes the page** with the official CLI and returns the resulting HTML
   Docs URL.

## How to Use

### 1. Define the document

Identify the audience, purpose, desired action, source boundaries, and any facts
that need verification. Preserve links to primary sources and clearly label
inferences or limitations.

### 2. Author the HTML

Create a complete HTML file with semantic headings, short readable sections,
useful diagrams or tables when they clarify the subject, responsive styles, and
descriptive link text. Keep CSS and small SVG illustrations inline. Do not put
credentials, private source material, analytics secrets, or API keys in the
artifact.

### 3. Review before publishing

Open the file locally and verify:

- every substantive claim is supported by the provided material or a cited source;
- the page works at narrow and wide viewport sizes;
- headings, focus states, contrast, and alternative text are accessible;
- all links work; and
- no secret or unintended personal information is present.

### 4. Publish

For a single HTML file:

```bash
npx @html-docs/cli publish page.html
```

For a multi-page folder:

```bash
npx @html-docs/cli publish ./site --slug my-site
```

Authenticate first when the user needs an owned artifact that can be managed
later:

```bash
npx @html-docs/cli auth
```

Return the published URL and briefly state what was verified. Ask before making
an artifact public when the user's intended access level is not explicit.

## Example

**User:** "Turn this architecture folder into a visual onboarding guide and
publish it for my team to review."

**Workflow:**

1. Read the relevant source files while excluding credentials, dependencies,
   build output, and version-control internals.
2. Build a teaching sequence around the system boundary, request flow, data
   model, and common maintenance tasks.
3. Cite the source files behind each technical claim.
4. Create and inspect a responsive `onboarding.html` document.
5. Publish it with `npx @html-docs/cli publish onboarding.html` and return the
   review URL.

## Safety Rules

- Confirm before destructive changes or overwriting an existing document.
- Keep provider keys and HTML Docs credentials local.
- Never publish secrets, private repositories, or personal data without explicit authorization.
- Prefer a private or owned preview when publication scope is unclear.
- Do not claim a page was published until the CLI returns a working URL.

## Official Resources

- [Agent guide](https://www.html-docs.com/agents)
- [Developer and API documentation](https://www.html-docs.com/developers)
- [Examples and finished artifacts](https://www.html-docs.com/showcase)
- [Open-source skill and tooling](https://github.com/raunaqbn/html-docs-skill)

**Credit:** Based on Raunaq Naidu's HTML Docs publishing workflow.
