---
name: dotld
description: Search domain name availability and registration prices across popular TLDs using the Dynadot API.
---

# dotld — Domain Availability & Pricing

Search domain name availability and registration prices. Type a keyword, get every TLD that matters. Available domains show price and a link to buy.

## When to Use This Skill

- Checking if a specific domain name is available
- Exploring TLD options for a brand name or keyword
- Comparing domain prices across extensions
- Brainstorming domain names in bulk

## What This Skill Does

1. **Keyword Expansion**: Automatically checks a keyword across 10 popular TLDs (com, net, org, io, ai, co, app, dev, sh, so)
2. **Exact Lookup**: Checks availability and price for a specific domain
3. **Batch Search**: Checks multiple domains or keywords at once
4. **Structured Output**: JSON output for scripts and pipelines

## Installation

```bash
curl -fsSL https://raw.githubusercontent.com/tedstonne/dotld/main/scripts/install.sh | bash
```

Requires a [Dynadot production API key](https://www.dynadot.com/account/domain/setting/api.html) (free with any account).

```bash
dotld --dynadot-key YOUR_KEY acme
```

The key is saved locally after first use. Every run after that is just `dotld <keyword>`.

## How to Use

### Basic Usage — Keyword Search

```
dotld acme
```

### Exact Domain Lookup

```
dotld acme.xyz
```

### Batch Search

```
dotld coolstartup launchpad rocketship
```

### JSON Output

```
dotld acme --json
```

## Example

**User**: "Check if any good domains are available for the name acme"

**Output**:
```
acme
├─ acme.com · Taken
├─ acme.net · Taken
├─ acme.org · Taken
├─ acme.io  · $39.99 · https://www.dynadot.com/domain/search?domain=acme.io&rscreg=github
├─ acme.ai  · Taken
├─ acme.co  · Taken
├─ acme.app · Taken
├─ acme.dev · Taken
├─ acme.sh  · Taken
└─ acme.so  · Taken
```

## Tips

- Use keyword mode (no dot) to explore all popular TLDs at once
- Use `--json` for structured output in automation pipelines
- Use `--file domains.txt` to check a list of domains from a file
- Prices are in USD from the Dynadot API

## Common Use Cases

- Checking availability before registering a new project or brand domain
- Comparing prices across TLDs to find the best deal
- Batch-checking a brainstorm list of potential names
- Quick availability checks during naming conversations
