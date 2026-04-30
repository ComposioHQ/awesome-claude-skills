---
name: Apollo Automation
description: "Automate Apollo.io lead generation -- search organizations, discover contacts, enrich prospect data, manage contact stages, and build targeted outreach lists -- using natural language through the Composio MCP integration."
category: sales-intelligence
requires:
  mcp:
    - rube
---

# Apollo Automation

Supercharge your sales prospecting with Apollo.io -- search companies, discover decision-makers, enrich contact data with emails and phone numbers, and manage your sales pipeline stages -- all through natural language commands.

**Toolkit docs:** [composio.dev/toolkits/apollo](https://composio.dev/toolkits/apollo)

---

## Setup

1. Add the Composio MCP server to your client configuration:
   ```
   https://rube.app/mcp
   ```
2. Connect your Apollo.io account when prompted (API key authentication).
3. Start issuing natural language commands to prospect and enrich leads.

---

## Core Workflows

### 1. Search Organizations
Find target companies using filters like name, location, employee count, and industry keywords.

**Tool:** `APOLLO_ORGANIZATION_SEARCH`

**Example prompt:**
> "Find SaaS companies in Texas with 50-500 employees on Apollo"

**Key parameters:**
- `q_organization_name` -- Partial name match (e.g., "Apollo" matches "Apollo Inc.")
- `organization_locations` -- HQ locations to include (e.g., "texas", "tokyo")
- `organization_not_locations` -- HQ locations to exclude
- `organization_num_employees_ranges` -- Employee ranges in "min,max" format (e.g., "50,500")
- `q_organization_keyword_tags` -- Industry keywords (e.g., "software", "healthcare")
- `page` / `per_page` -- Pagination (max 100 per page, max 500 pages)

---

### 2. Discover People at Companies
Search Apollo's contact database for people matching title, seniority, location, and company criteria.

**Tool:** `APOLLO_PEOPLE_SEARCH`

**Example prompt:**
> "Find VPs of Sales at microsoft.com and apollo.io"

**Key parameters:**
- `person_titles` -- Job titles (e.g., "VP of Sales", "CTO")
- `person_seniorities` -- Seniority levels (e.g., "director", "vp", "senior")
- `person_locations` -- Geographic locations of people
- `q_organization_domains` -- Company domains (e.g., "apollo.io" -- exclude "www.")
- `organization_ids` -- Apollo company IDs from Organization Search
- `contact_email_status` -- Filter by email status: "verified", "unverified", "likely to engage"
- `page` / `per_page` -- Pagination (max 100 per page)

---

### 3. Enrich Individual Contacts
Get comprehensive data (email, phone, LinkedIn, company info) for a single person using their email, LinkedIn URL, or name + company.

**Tool:** `APOLLO_PEOPLE_ENRICHMENT`

**Example prompt:**
> "Enrich Tim Zheng at Apollo.io on Apollo"

**Key parameters (at least one identifier required):**
- `email` -- Person's email address
- `linkedin_url` -- Full LinkedIn profile URL
- `first_name` + `last_name` + (`organization_name` or `domain`) -- Name-based matching
- `domain` -- Bare hostname without protocol (e.g., "apollo.io", not "https://apollo.io")
- `reveal_personal_emails` -- Set true to get personal emails (may use extra credits)
- `reveal_phone_number` -- Set true for phone numbers (requires `webhook_url`)

---

### 4. Bulk Enrich Prospects
Enrich up to 10 people simultaneously for efficient batch processing.

**Tool:** `APOLLO_BULK_PEOPLE_ENRICHMENT`

**Example prompt:**
> "Bulk enrich these 5 leads with their Apollo data: [list of names/emails]"

**Key parameters:**
- `details` (required) -- Array of 1-10 person objects, each with identifiers like `email`, `linkedin_url`, `first_name`, `last_name`, `domain`, `company_name`
- `reveal_personal_emails` -- Include personal emails (extra credits)
- `reveal_phone_number` -- Include phone numbers (requires `webhook_url`)

---

### 5. Manage Contact Pipeline Stages
List available stages and update contacts through your sales funnel.

**Tools:** `APOLLO_LIST_CONTACT_STAGES`, `APOLLO_UPDATE_CONTACT_STAGE`

**Example prompt:**
> "Move contacts X and Y to the 'Qualified' stage in Apollo"

**Key parameters for listing stages:** None required.

**Key parameters for updating stage:**
- `contact_ids` (required) -- Array of contact IDs to update
- `contact_stage_id` (required) -- Target stage ID (from List Contact Stages)

---

### 6. Create and Search Saved Contacts
Create new contact records and search your existing Apollo contact database.

**Tools:** `APOLLO_CREATE_CONTACT`, `APOLLO_SEARCH_CONTACTS`

**Example prompt:**
> "Search my Apollo contacts for anyone at Stripe"

**Key parameters for search:**
- Keyword search, stage ID filtering, sorting options
- `page` / `per_page` -- Pagination

**Key parameters for create:**
- `first_name`, `last_name`, `email`, `organization_name`
- `account_id` -- Link to an organization
- `contact_stage_id` -- Initial sales stage

---

## Known Pitfalls

- **Organization domains can be empty**: Some organizations from `APOLLO_ORGANIZATION_SEARCH` return missing or empty domain fields. Use `APOLLO_ORGANIZATION_ENRICHMENT` to validate domains before relying on them.
- **HTTP 403 means config issues**: A 403 response indicates API key or plan access problems -- do not retry. Fix your credentials or plan first.
- **People search returns obfuscated data**: `APOLLO_PEOPLE_SEARCH` may show `has_email`/`has_direct_phone` flags or obfuscated fields instead of full contact details. Use `APOLLO_PEOPLE_ENRICHMENT` to get complete information.
- **Pagination limits are strict**: People search supports `per_page` up to 100 and max 500 pages. Stopping early can miss large portions of the result set.
- **Bulk enrichment has small batch limits**: `APOLLO_BULK_PEOPLE_ENRICHMENT` accepts only 10 items per call. It can return `status='success'` with `missing_records > 0` when identifiers are insufficient -- retry individual records with `APOLLO_PEOPLE_ENRICHMENT`.
- **No automatic deduplication**: `APOLLO_CREATE_CONTACT` does not deduplicate. Check for existing contacts first with `APOLLO_SEARCH_CONTACTS`.
- **Domain format matters**: Always use bare hostnames (e.g., "apollo.io") without protocol prefixes ("https://") or "www." prefix.

---

## Quick Reference

| Action | Tool Slug | Required Params |
|---|---|---|
| Search organizations | `APOLLO_ORGANIZATION_SEARCH` | None (optional filters) |
| Enrich organization | `APOLLO_ORGANIZATION_ENRICHMENT` | `domain` |
| Bulk enrich orgs | `APOLLO_BULK_ORGANIZATION_ENRICHMENT` | `domains` |
| Search people | `APOLLO_PEOPLE_SEARCH` | None (optional filters) |
| Enrich person | `APOLLO_PEOPLE_ENRICHMENT` | One of: `email`, `linkedin_url`, or name+company |
| Bulk enrich people | `APOLLO_BULK_PEOPLE_ENRICHMENT` | `details` (1-10 person objects) |
| List contact stages | `APOLLO_LIST_CONTACT_STAGES` | None |
| Update contact stage | `APOLLO_UPDATE_CONTACT_STAGE` | `contact_ids`, `contact_stage_id` |
| Create contact | `APOLLO_CREATE_CONTACT` | Name + identifiers |
| Search contacts | `APOLLO_SEARCH_CONTACTS` | None (optional filters) |

---

*Powered by [Composio](https://composio.dev)*
