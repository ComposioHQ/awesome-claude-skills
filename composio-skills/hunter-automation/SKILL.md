---
name: Hunter Automation
description: "Automate Hunter.io email intelligence -- search domains for email addresses, find specific contacts, verify email deliverability, manage leads, and monitor account usage -- using natural language through the Composio MCP integration."
category: email-intelligence
requires:
  mcp:
    - rube
---

# Hunter Automation

Power your outreach with Hunter.io -- discover email addresses by domain, find specific people's emails, verify deliverability, save leads, and track your API usage -- all through natural language commands.

**Toolkit docs:** [composio.dev/toolkits/hunter](https://composio.dev/toolkits/hunter)

---

## Setup

1. Add the Composio MCP server to your client configuration:
   ```
   https://rube.app/mcp
   ```
2. Connect your Hunter.io account when prompted (API key authentication).
3. Start issuing natural language commands to find and verify emails.

---

## Core Workflows

### 1. Search Domain for Email Addresses
Discover all publicly available email addresses for a given domain or company, with filtering by department, seniority, and type.

**Tool:** `HUNTER_DOMAIN_SEARCH`

**Example prompt:**
> "Find all executive email addresses at stripe.com using Hunter"

**Key parameters:**
- `domain` -- Domain to search (e.g., "stripe.com"). Required if `company` not provided.
- `company` -- Company name to search (e.g., "Stripe"). Required if `domain` not provided.
- `type` -- Filter by "personal" or "generic" emails
- `seniority` -- Filter by levels: "junior", "senior", "executive" (array)
- `department` -- Filter by departments: "executive", "it", "finance", "sales", etc. (array)
- `required_field` -- Require specific fields: "full_name", "position", "phone_number" (array)
- `limit` -- Max results per request (1-100, default 10; free/basic plans limited to 10)
- `offset` -- Skip results for pagination (default 0)

---

### 2. Find a Specific Person's Email
Infer the most likely email address for a person given their name and domain or company.

**Tool:** `HUNTER_EMAIL_FINDER`

**Example prompt:**
> "Find the email for Alexis Ohanian at reddit.com using Hunter"

**Key parameters:**
- `domain` -- Target domain (e.g., "reddit.com"). Takes precedence over `company`.
- `company` -- Company name (e.g., "Reddit"). Used if domain not provided.
- Name (one of these combinations required):
  - `first_name` + `last_name` (e.g., "Alexis" + "Ohanian")
  - `full_name` (e.g., "Alexis Ohanian")
- `max_duration` -- Max request duration in seconds (3-20, default 10). Longer durations yield more accurate results.

---

### 3. Verify Email Deliverability
Check whether an email address is valid, deliverable, and safe to send to.

**Tool:** `HUNTER_EMAIL_VERIFIER`

**Example prompt:**
> "Verify if john.doe@example.com is a valid email address"

**Key parameters:**
- `email` (required) -- The email address to verify (e.g., "john.doe@example.com")

**Response includes:** verification status, deliverability score, MX record validation, and risk assessment.

---

### 4. Get Email Volume Estimates
Check how many email addresses Hunter has for a domain or company -- this call is free and does not consume API credits.

**Tool:** `HUNTER_EMAIL_COUNT`

**Example prompt:**
> "How many email addresses does Hunter have for stripe.com?"

**Key parameters:**
- `domain` -- Domain to query (e.g., "stripe.com"). Required if `company` not provided.
- `company` -- Company name (min 3 characters). Required if `domain` not provided.
- `type` -- Filter count by "personal" or "generic" emails

**Returns:** Total count with breakdowns by type, department, and seniority level.

---

### 5. Save and Manage Leads
Create or update leads by email in a single upsert call -- no need to check existence first.

**Tool:** `HUNTER_UPSERT_LEAD`

**Example prompt:**
> "Save john@stripe.com as a lead in Hunter with name John Doe, position CTO"

**Key parameters:**
- `email` -- Lead's email address (primary identifier for upsert)
- Name, position, company, and other lead metadata

---

### 6. Check Account Usage and Limits
Review your Hunter account plan details, remaining searches, and verification quotas before running bulk operations.

**Tool:** `HUNTER_ACCOUNT_INFORMATION`

**Example prompt:**
> "How many Hunter API searches do I have left this month?"

**Key parameters:** None required.

---

## Known Pitfalls

- **HTTP 401 means invalid credentials**: `authentication_failed` errors indicate an invalid or expired API key. Fix before attempting bulk operations.
- **Email counts are estimates**: `HUNTER_EMAIL_COUNT` returns approximate numbers for sizing and prioritization, not guaranteed retrievable email counts.
- **Domain search uses offset pagination**: `HUNTER_DOMAIN_SEARCH` paginates via `limit`/`offset`. Do not assume the first page is complete -- continue fetching until results are empty or you hit a cap.
- **Empty results are not errors**: `HUNTER_DOMAIN_SEARCH` can return `emails: []` with no error. Treat as "no data found" and continue, rather than retrying as a failure.
- **Verification status nuances**: `accept_all` or `risky` statuses from `HUNTER_EMAIL_VERIFIER` indicate uncertainty. Exclude these from strict deliverability workflows or handle them separately.
- **Free/basic plan limits**: Free and basic plans limit `HUNTER_DOMAIN_SEARCH` to 10 results per request. Higher limits require a paid plan.
- **Domain format matters**: Use bare domains like "stripe.com" -- do not include protocol ("https://") or "www." prefix.

---

## Quick Reference

| Action | Tool Slug | Required Params |
|---|---|---|
| Search domain emails | `HUNTER_DOMAIN_SEARCH` | `domain` or `company` |
| Find person's email | `HUNTER_EMAIL_FINDER` | Name + (`domain` or `company`) |
| Verify email | `HUNTER_EMAIL_VERIFIER` | `email` |
| Get email count | `HUNTER_EMAIL_COUNT` | `domain` or `company` |
| Save/update lead | `HUNTER_UPSERT_LEAD` | `email` |
| Check account | `HUNTER_ACCOUNT_INFORMATION` | None |

---

*Powered by [Composio](https://composio.dev)*
