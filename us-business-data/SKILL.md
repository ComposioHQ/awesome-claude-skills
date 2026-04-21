---
name: us-business-data
description: "Search US business entity registrations, Yellow Pages leads, and building permits directly from Claude Code"
---

# US Business Data Lookup

Search US Secretary of State business records, Yellow Pages business listings, and building permits across the United States -- all from within Claude Code.

## When to Use This Skill

- You need to look up a company's registration status, officers, or formation date
- You want to find businesses by category and location for lead generation
- You need building permit data for construction industry research
- You're doing KYC/compliance checks and need official state records
- You want structured business data without leaving your IDE

## What This Skill Does

1. Searches Secretary of State business entity databases across 17 US states (NY, TX, CA, FL, IL, and more)
2. Looks up Yellow Pages business listings by category, location, and keyword
3. Retrieves building permit records from 47 US cities via Socrata open data APIs
4. Returns structured JSON with entity details, officer names, addresses, and status

## How to Use

### Setup

Add to your Claude Code MCP config (`~/.claude/claude_mcp_config.json`):

```json
{
  "mcpServers": {
    "us-business-data": {
      "command": "npx",
      "args": ["-y", "@avabuildsdata/mcp-us-business-data"]
    }
  }
}
```

Or clone and build from source:

```bash
git clone https://github.com/avabuildsdata/mcp-us-business-data
cd mcp-us-business-data
go build -o mcp-server ./cmd/server
```

### Basic Usage

Ask Claude Code naturally:

- "Look up Tesla's business registration in Texas"
- "Find plumbers in Chicago on Yellow Pages"
- "Get recent building permits in San Francisco"

### Advanced Usage

- "Search for all LLCs named 'Pinnacle' across NY, TX, and FL"
- "Find dentists in Miami and export their contact info"
- "Get building permits filed this month in Austin, TX"

## Example

**User prompt:** "Look up Goldman Sachs in New York Secretary of State records"

**Output:**
```json
{
  "entityName": "GOLDMAN SACHS GROUP INC",
  "state": "NY",
  "status": "ACTIVE",
  "formationDate": "1998-05-07",
  "entityType": "DOMESTIC BUSINESS CORPORATION",
  "jurisdiction": "NEW YORK",
  "registeredAgent": "CT CORPORATION SYSTEM",
  "address": "200 WEST STREET, NEW YORK, NY 10282"
}
```

## Tips

- State coverage: NY, TX, CA, CO, FL, OR, IA, MD, WA, NV, AZ, PA, MA, GA, NC, VA, OH
- Yellow Pages searches work best with specific categories (e.g., "plumbers" not "services")
- Building permits data comes from official city open data portals
- All data is from public government sources -- no API keys required

## Common Use Cases

- Sales prospecting and lead generation
- KYC and compliance verification
- Competitive analysis and market research
- Real estate and construction industry intelligence
- Due diligence for M&A or investment research

## Attribution

Built by [avabuildsdata](https://github.com/avabuildsdata). Data sourced from US Secretary of State offices, Yellow Pages, and municipal open data portals.
