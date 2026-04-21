---
name: zip-code-and-county
description: Look up any US ZIP code with full Census ACS demographics, county FIPS, timezone, area codes, home prices, rent, property tax, broadband, and cost of living via the hosted zipcodeandcounty.com MCP server. Use whenever the user asks about a US ZIP, county, or wants to compare locations.
---

# ZIP Code and County

Adds **comprehensive US geographic data** to Claude via the hosted MCP
server at `https://zipcodeandcounty.com/api/mcp`. No API key required
for low-volume use, no scraping, no hallucinated demographics — every
fact comes from US government public-domain sources (Census ACS 5-year,
USPS, HUD, NANPA, NCES, BEA, IANA).

## When to Use This Skill

- User asks about a specific US ZIP code ("what's in 90210", "median income in 78701")
- User asks about a US county ("Los Angeles County stats", "what counties does area code 310 cover")
- User asks for a relocation comparison between two ZIPs ("compare cost of living between Beverly Hills and Austin")
- User asks for distance, drive time, or radius searches between US ZIPs
- User asks about US demographics, home prices, rent, property tax, broadband coverage, or cost of living for any geographic area smaller than a state

## What This Skill Does

1. **Single-ZIP lookup**: Returns full record (city, county FIPS, lat/lng, timezone, area codes, congressional district, metro, ACS demographics).
2. **Search & autocomplete**: Find ZIPs by city name, county name, or ZIP prefix.
3. **Distance + travel time**: Straight-line + driving estimate between two ZIPs, with travel modes (walk/bike/drive/bus/train/flight).
4. **Radius search**: Every ZIP within N miles of a center, sorted by distance.
5. **County rollup**: County summary by 5-digit FIPS — pop, ZIPs, timezones, area codes, adjacent counties.
6. **State summary**: ZIP count, county count, top counties by population for any US state.
7. **Nearest airports**: 10 closest major US airports to any ZIP.

## How to Use

### Installation

Pick the install path for your client:

**Claude Code (CLI):**
```bash
claude mcp add --transport http zipcodeandcounty https://zipcodeandcounty.com/api/mcp
```

**Claude Desktop:**

Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "zipcodeandcounty": {
      "type": "http",
      "url": "https://zipcodeandcounty.com/api/mcp"
    }
  }
}
```

**Cursor / Zed / Windsurf:**

See full setup guide at <https://github.com/qileza/zip-code-free-api/tree/main/examples/mcp>.

### Basic Usage

After install, prompts like these will trigger Claude to call the tools:

- *"What's the median household income in ZIP code 78701?"*
- *"What county is 73505 in, and what other ZIPs are in that county?"*
- *"Find every ZIP within 25 miles of Beverly Hills (90210)."*
- *"Compare cost of living between 02108 (Boston) and 78701 (Austin)."*
- *"Which counties does the 213 area code cover?"*

### Higher Quotas (Optional)

The hosted MCP is free for **5 requests/day per anonymous IP**, **200/month with a free key**. Grab a key at <https://zipcodeandcounty.com/auth/signup> and pass it in the headers:

```bash
claude mcp add --transport http zipcodeandcounty \
  https://zipcodeandcounty.com/api/mcp \
  --header "X-API-Key: zb_live_your_key_here"
```

Paid tiers up to 500k/month at <https://zipcodeandcounty.com/pricing>.

## Example Conversations

**Real-estate research:**
> User: I'm thinking of moving from Brooklyn (11201) to Austin. Pull comparable demographics, median home value, and median rent for ZIP 78701.
>
> Claude calls `lookup_zip` for both, returns side-by-side: Brooklyn ~$1.2M median home / $3,200 rent vs Austin 78701 ~$650k / $2,400. Cost-of-living index 95 vs 168.

**FIPS-keyed analytics:**
> User: I have a CSV of ZIP codes. For each, what county FIPS does it belong to?
>
> Claude calls `lookup_zip` for each, returns the FIPS code so the user can join against any federal dataset.

**Phone-number context:**
> User: Someone called from 213-555-0100. Where is area code 213 from and is it a known scam zone?
>
> Claude calls `lookup_zip` chains via the area-code → city mapping, explains 213 = central LA, notes that any area code can be spoofed by robocallers.

## Source Repository & Docs

- **Repo:** <https://github.com/qileza/zip-code-free-api>
- **Skill manifest (this file):** <https://github.com/qileza/zip-code-free-api/blob/main/skills/zipcodeandcounty/SKILL.md>
- **MCP server endpoint:** `https://zipcodeandcounty.com/api/mcp`
- **OpenAPI spec:** <https://zipcodeandcounty.com/openapi.json>
- **Documentation:** <https://zipcodeandcounty.com/mcp>

## Tested With

- Claude Desktop (macOS, Windows, Linux)
- Claude Code (CLI)
- Cursor
- Zed
- Windsurf
- ChatGPT (developer-mode connectors)

## License

MIT for the skill bundle. Underlying data is US government public domain
(CC0-equivalent). Use freely in any product. Maintained by [zipcodeandcounty.com](https://zipcodeandcounty.com).
