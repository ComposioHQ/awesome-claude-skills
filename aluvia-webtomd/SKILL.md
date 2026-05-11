---
name: webtomd
description: Scrapes a webpage and saves it as a clean Markdown file with frontmatter. Use when the user provides a URL and wants to scrape, save, archive, or convert a page to Markdown. Triggers on "scrape this", "save this page", "convert to markdown", "download docs from", or any URL with intent to save.
---

# Web to Markdown

Two modes:
- **fast** — `WebFetch`. Quick, may summarize. Best for articles and blog posts.
- **precise** — `urllib` + `markdownify`. Verbatim content. Best for technical docs and API references.

Mode is **auto-detected** in Step 2. User can override anytime by saying "use fast" or "use precise".

## Workflow

Copy and track progress:

```
[ ] 1. Resolve proxy (if ALUVIA_API_KEY set)
[ ] 2. Fetch raw HTML + JS-render check
[ ] 3. Auto-detect mode
[ ] 4. Detect and filter nav links
[ ] 5. Ask user which pages to scrape
[ ] 6. Convert and save each page
[ ] 7. Print summary
```

---

### 1. Resolve proxy

Check for `ALUVIA_API_KEY` in the environment:

```python
import os, urllib.request, json

api_key = os.environ.get("ALUVIA_API_KEY")
proxy_url = None

if api_key:
    req = urllib.request.Request(
        "https://api.aluvia.io/v1/account/connections",
        headers={"Authorization": f"Bearer {api_key}"}
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        data = json.loads(r.read())
    connections = data.get("data", [])
    if connections:
        proxy_url = connections[0]["proxy_urls"]["url"]
```

If `proxy_url` is set, use it for all subsequent `urllib` requests via `ProxyHandler`:

```python
handlers = [urllib.request.ProxyHandler({"http": proxy_url, "https": proxy_url})] if proxy_url else []
opener = urllib.request.build_opener(*handlers)
```

Use `opener.open(req)` instead of `urllib.request.urlopen()` for every fetch in Steps 2 and 6.

If `ALUVIA_API_KEY` is not set or the call fails, proceed without proxy — do not error.

---

### 2. Fetch raw HTML

Use `python3` + `urllib` with a browser User-Agent. Extract `<title>`, strip trailing `| site name`.

**JS-render check** — flag only if BOTH are true:
- Raw HTML < 2000 chars, OR `<body>` has < 3 block tags (`p`, `h1-h6`, `li`, `section`, `div`)
- AND content is clearly empty (not just a Next.js/Nuxt SSR wrapper)

If flagged, warn and offer:
> "⚠️ Appears JS-rendered. Options: (1) continue anyway (2) retry via Jina Reader — `https://r.jina.ai/<url>` (3) cancel"

If user picks Jina, replace URL and use fast mode. Skip nav detection.

---

### 3. Auto-detect mode

Using the URL and raw HTML already fetched, pick the mode silently then inform the user:

**Use `precise` if any of these match:**
- URL path contains `/docs/`, `/api/`, `/reference/`, `/guide/`, `/manual/`, `/sdk/`
- Page has high code density: more than 5 `<code>` or `<pre>` blocks in the HTML
- Domain is a known dev-docs site (e.g. `platform.claude.com`, `docs.`, `developer.`)

**Use `fast` otherwise** (blogs, marketing, articles, landing pages).

Inform the user:
> "Auto-selected **[mode]** mode based on [reason: URL pattern / code density / domain]. Reply 'fast' or 'precise' to override, or press Enter to continue."

Wait for reply. If Enter or no override, proceed.

---

### 4. Nav links

Use the raw HTML already fetched in Step 2 — do not re-fetch the URL.

Scan the HTML and identify all navigation and sidebar links that look like documentation or content pages. Extract ALL matching `(title, url)` pairs — do not truncate or summarize.

- Normalize relative URLs: if a URL starts with `/`, prepend the base domain (e.g. `/docs/guide` → `https://example.com/docs/guide`)
- Exclude: login, signup, home, about, contact, changelog, status, tags, and any external domains
- Only include same-domain, non-anchor links

If no links are found → scrape main URL only.

---

### 5. Ask user

If nav links found:
```
Found N related pages. Which to scrape?
1. Title — url
2. Title — url
Reply: "all", "none", or "1 3 5"
```
If "all" and N > 10: confirm — "That's N pages with ~1s delays between each. Proceed?"

---

### 6. Convert and save

For each URL — check if file exists first:
> "⚠️ `./scraped/file.md` exists. Overwrite? (yes / no / skip)"

**Rate limit:** 1–2s delay between requests when scraping multiple URLs.

**fast mode:**
Use `WebFetch`. If response says "Output too large... saved to: /path/file.txt", read it with `bash` (`cat`).

If result < 500 chars or has no headings and no lists, suggest:
> "⚠️ Fast mode returned thin content. Retry with precise? (yes / no)"

**precise mode:**
Reuse HTML from step 2 for the main URL. For nav pages, fetch fresh using `opener` (with proxy if set).
- Check `markdownify`: `python3 -c "import markdownify" 2>/dev/null || pip install markdownify -q --break-system-packages`
- Strip `<script>`, `<style>`, `<nav>`, `<footer>`, `<header>`, `<aside>`
- Isolate content: `<main>` → `<article>` → element with class/id `content|docs|prose` → largest `<div>` → `<body>`
- Convert with `markdownify` (ATX headings, tables, no images), clean blank lines

**Quality check (both modes):**
- No `#` heading → warn `⚠️ No headings`
- No blank lines → warn `⚠️ Single text block`
- Both warnings → prepend `> ⚠️ JS-rendered page — structure may be lost`

Save to `./scraped/<slug>.md`:
```markdown
---
title: "Page Title"
source: "https://..."
scraped: "YYYY-MM-DD"
mode: fast | precise
---
```

---

### 7. Summary

```
Done. Saved N file(s) [mode: fast|precise]:
  - ./scraped/page.md (4,200 chars)
  - ./scraped/other.md (skipped — already exists)
  - ./scraped/broken.md ⚠️ No headings
```

## Errors
- WebFetch fails or empty → skip, report
- markdownify install fails → regex tag-strip fallback, warn user
- Non-200 or timeout → skip, report
- Aluvia API unreachable or returns no connections → proceed without proxy, warn user