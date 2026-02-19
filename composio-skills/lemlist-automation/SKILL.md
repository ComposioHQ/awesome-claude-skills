---
name: Lemlist Automation
description: "Automate Lemlist multichannel outreach -- manage campaigns, enroll leads, add personalization variables, export campaign data, and handle unsubscribes via the Composio MCP integration."
requires:
  mcp:
    - rube
---

# Lemlist Automation

Automate your Lemlist multichannel outreach workflows -- manage campaigns, enroll leads at scale, enrich with custom variables, export campaign data, and clean up unsubscribes.

**Toolkit docs:** [composio.dev/toolkits/lemlist](https://composio.dev/toolkits/lemlist)

---

## Setup

1. Add the Composio MCP server to your client: `https://rube.app/mcp`
2. Connect your Lemlist account when prompted (API key authentication)
3. Start using the workflows below

---

## Core Workflows

### 1. List and Discover Campaigns

Use `LEMLIST_GET_LIST_CAMPAIGNS` to enumerate all campaigns by status, with pagination support.

```
Tool: LEMLIST_GET_LIST_CAMPAIGNS
Inputs:
  - status: "running" | "draft" | "archived" | "ended" | "paused" | "errors" (optional)
  - limit: integer (max 100, default 100)
  - offset: integer (pagination offset)
  - sortBy: "createdAt"
  - sortOrder: "asc" | "desc"
```

**Important:** The response may be wrapped as `{campaigns: [...], pagination: {...}}` instead of a flat list. Always extract from the `campaigns` key.

### 2. Get Campaign Details

Use `LEMLIST_GET_CAMPAIGN_BY_ID` to validate campaign configuration before writes.

```
Tool: LEMLIST_GET_CAMPAIGN_BY_ID
Inputs:
  - campaignId: string (required) -- e.g., "cam_A1B2C3D4E5F6G7H8I9"
```

### 3. Enroll Leads into a Campaign

Use `LEMLIST_POST_CREATE_LEAD_IN_CAMPAIGN` to add leads with optional email finding, phone lookup, and LinkedIn enrichment.

```
Tool: LEMLIST_POST_CREATE_LEAD_IN_CAMPAIGN
Inputs:
  - campaignId: string (required)
  - email: string (required)
  - firstName, lastName, companyName, companyDomain: string (optional)
  - jobTitle, phone, linkedinUrl, icebreaker: string (optional)
  - deduplicate: boolean (prevents cross-campaign duplicates)
  - findEmail, findPhone, verifyEmail, linkedinEnrichment: boolean (optional)
  - timezone: string (IANA format, e.g., "America/New_York")
```

**Bulk pattern:** Chunk leads into batches of ~50 and checkpoint progress between batches.

### 4. Add Custom Variables to a Lead

Use `LEMLIST_POST_ADD_VARIABLES_TO_LEAD` to enrich leads with personalization fields after enrollment.

```
Tool: LEMLIST_POST_ADD_VARIABLES_TO_LEAD
Inputs:
  - leadId: string (required) -- internal Lemlist lead ID (NOT email)
  - company: string (required) -- must match your company name in Lemlist
  - variables: object (required) -- key-value pairs, e.g., {"score": "42", "color": "yellow"}
```

**Important:** This is NOT an upsert -- attempting to add variables that already exist will fail. Resolve the internal `leadId` via `LEMLIST_GET_RETRIEVE_LEAD_BY_EMAIL` if you only have the email address.

### 5. Export Campaign Leads

Use `LEMLIST_GET_EXPORT_CAMPAIGN_LEADS` to download leads with state filtering for reporting or QA.

```
Tool: LEMLIST_GET_EXPORT_CAMPAIGN_LEADS
Inputs:
  - campaignId: string (required)
  - (supports state filtering and JSON/CSV output)
```

### 6. Unsubscribe Lead from Campaign

Use `LEMLIST_DELETE_UNSUBSCRIBE_LEAD_FROM_CAMPAIGN` to stop outreach by removing a lead from a campaign.

```
Tool: LEMLIST_DELETE_UNSUBSCRIBE_LEAD_FROM_CAMPAIGN
Inputs:
  - campaignId: string (required)
  - leadId or email: string (required)
```

---

## Known Pitfalls

| Pitfall | Detail |
|---------|--------|
| Wrapped campaign list | `LEMLIST_GET_LIST_CAMPAIGNS` may return `{campaigns: [...], pagination: {...}}` instead of a flat array. Always extract from the `campaigns` key. |
| Cross-campaign deduplication | `LEMLIST_POST_CREATE_LEAD_IN_CAMPAIGN` with deduplication enabled fails with HTTP 500 "Lead already in other campaign" -- disable deduplication for intentional cross-campaign enrollment. |
| Bulk import failures | Chunk bulk imports to ~50 per batch with checkpoints to avoid losing partial progress on intermittent failures. |
| Invalid leadId | `LEMLIST_POST_ADD_VARIABLES_TO_LEAD` returns HTTP 400 "Invalid leadId" when using an email as the leadId -- resolve the internal ID via `LEMLIST_GET_RETRIEVE_LEAD_BY_EMAIL` first. |
| Variable collisions | `LEMLIST_POST_ADD_VARIABLES_TO_LEAD` is not an upsert. Adding keys that already exist returns HTTP 400 "Variables X already exist". |

---

## Quick Reference

| Tool Slug | Description |
|-----------|-------------|
| `LEMLIST_GET_LIST_CAMPAIGNS` | List all campaigns with status filter and pagination |
| `LEMLIST_GET_CAMPAIGN_BY_ID` | Get detailed campaign info by ID |
| `LEMLIST_POST_CREATE_LEAD_IN_CAMPAIGN` | Create and enroll a lead into a campaign |
| `LEMLIST_POST_ADD_VARIABLES_TO_LEAD` | Add custom personalization variables to a lead |
| `LEMLIST_GET_RETRIEVE_LEAD_BY_EMAIL` | Look up a lead by email address |
| `LEMLIST_GET_EXPORT_CAMPAIGN_LEADS` | Export leads from a campaign with state filtering |
| `LEMLIST_DELETE_UNSUBSCRIBE_LEAD_FROM_CAMPAIGN` | Remove a lead from a campaign |

---

*Powered by [Composio](https://composio.dev)*
