---
name: github-summary
description: Generate an AI-synthesised summary of your GitHub activity (issues, PRs, commits) for a specified organisation and time period. Creates a natural language narrative with inline URL references. Use when user wants to summarise their work, review their contributions, or generate a work log.
---

# GitHub Summary

Generate a comprehensive, AI-written summary of your GitHub activity including issues, pull requests (authored and reviewed), and commits.

## Instructions

When the user wants a GitHub activity summary:

### 1. Check Data Source Availability

Check which data sources are available:

**Check GitHub MCP Server:**
Look for MCP tools: `search_issues`, `search_pull_requests`, `list_issues`, `issue_read`, `pull_request_read`, `list_commits`

**Check gh CLI:**

```bash
gh auth status
```

**Decision logic:**

1. **Both available:** Use `AskUserQuestion` to let the user choose:
   - "GitHub MCP Server (Recommended)" - richer context, faster for large queries
   - "GitHub CLI (gh)" - direct API access, useful for debugging

2. **Only MCP available:** Use MCP automatically, inform user

3. **Only gh CLI available:** Use gh CLI automatically, inform user

4. **Neither available:** Stop and guide user to either:
   - Configure GitHub MCP Server, or
   - Run `gh auth login` to authenticate the CLI

### 2. Fetch Available Organisations

**Using MCP:**

```bash
search_orgs or equivalent org listing tool
```

**Using gh CLI:**

```bash
gh api user/orgs --jq '.[].login'
```

Also get the authenticated username:

```bash
gh api user --jq '.login'
```

### 3. Ask for Organisation

Use `AskUserQuestion` to prompt the user to select an organisation.

Build options from the fetched organisations list, plus:

- "All organisations (no filter)" - search across all orgs
- "Personal account only" - only personal repos

Example question: "Which organisation would you like to summarise activity for?"

### 4. Ask for Time Period

Use `AskUserQuestion` to prompt for the time range.

Options:

- Last 7 days
- Last 14 days
- Last 30 days
- This month
- Custom range

If "Custom range" is selected, ask follow-up questions for:

- Start date (format: YYYY-MM-DD or natural language like "1 January 2026")
- End date (defaults to today if not specified)

Convert all dates to ISO 8601 format (YYYY-MM-DD) for API queries.

### 5. Phase 1: Discover Activity Items

Fetch lists of issues, PRs, and commits for the selected organisation and time period.

**Using MCP Server (preferred - use search tools for accurate filtering):**

```bash
# IMPORTANT: Use search tools, not list tools, for accurate author + date filtering

# Issues created by user in date range
search_issues(q: "author:<username> org:<org> created:<start>..<end>")

# Issues where user is involved (assigned, commented, mentioned) but didn't create
search_issues(q: "involves:<username> org:<org> updated:<start>..<end>")

# PRs authored by user in date range
search_pull_requests(q: "author:<username> org:<org> created:<start>..<end>")

# PRs reviewed by user in date range
search_pull_requests(q: "reviewed-by:<username> org:<org> updated:<start>..<end>")

# Commits by user
search_commits(q: "author:<username> org:<org> author-date:<start>..<end>")
```

**Important:** Merge results from `author:` and `involves:` queries, deduplicating by issue number.

**MCP Fallback (if search tools unavailable):**

If only `list_issues`/`list_pull_requests` are available:

- These tools may use `since` which filters by *update* time, not *creation* time
- They may not filter by author
- You MUST manually filter results by author and creation date after fetching
- Consider fetching more results and filtering client-side

```bash
# Less accurate - requires post-filtering
list_issues(owner: <org>, repo: <repo>, state: "all", since: <ISO-date>)
# Then filter: keep only items where creator == <username> AND created_at >= <start>

list_pull_requests(owner: <org>, repo: <repo>, state: "all")
# Then filter: keep only items where user.login == <username> AND created_at in range
```

**Using gh CLI:**

```bash
# Issues created by user
gh search issues --author @me --owner <org> --created "<start>..<end>" --json title,url,number,repository --limit 100

# Issues where user is involved (assigned, commented, mentioned) but didn't create
# This catches issues like tracking issues created by others that you work on
gh search issues --involves @me --owner <org> --updated "<start>..<end>" --json title,url,number,repository --limit 100

# PRs authored by user
gh search prs --author @me --owner <org> --created "<start>..<end>" --json title,url,number,repository,state --limit 100

# PRs reviewed by user
gh search prs --reviewed-by @me --owner <org> --updated "<start>..<end>" --json title,url,number,repository,state --limit 100

# Commits by user
gh search commits --author @me --owner <org> --author-date "<start>..<end>" --json sha,repository,commit --limit 100
```

**Important:** Merge results from `--author` and `--involves` queries, deduplicating by issue number. The `--involves` flag catches issues where you're assigned, commented, or mentioned but didn't create.

**Note:** If "All organisations" was selected, omit the `--owner`/`org:` filter from commands.

### 6. Phase 2: Fetch Deep Context

For each issue and PR discovered, fetch rich context to enable meaningful summarisation.

**For Issues (using gh CLI):**

```bash
# Full issue details
gh api repos/<owner>/<repo>/issues/<number>

# Comments on the issue
gh api repos/<owner>/<repo>/issues/<number>/comments

# Timeline (shows linked PRs, cross-references, sub-issues)
gh api repos/<owner>/<repo>/issues/<number>/timeline
```

**For PRs Authored (using gh CLI):**

```bash
# Full PR details
gh api repos/<owner>/<repo>/pulls/<number>

# Review comments
gh api repos/<owner>/<repo>/pulls/<number>/reviews

# Inline comments
gh api repos/<owner>/<repo>/pulls/<number>/comments

# Files changed (summary)
gh api repos/<owner>/<repo>/pulls/<number>/files --jq 'length'
```

**For PRs Reviewed (using gh CLI):**

```bash
# Your review on this PR
gh api repos/<owner>/<repo>/pulls/<number>/reviews --jq '[.[] | select(.user.login == "<username>")]'
```

**For Commits:**

```bash
# Check if commit is associated with a PR
gh api repos/<owner>/<repo>/commits/<sha>/pulls
```

**Using MCP Server:**

```bash
issue_read(owner, repo, issue_number)  # Returns body, comments, sub-issues, labels, linked PRs
pull_request_read(owner, repo, pr_number)  # Returns body, review comments, files, status
```

### 7. Synthesise and Write Summary

Using all the collected data, write a natural language summary document.

**Determine Output Location:**

1. Look for an `Inbox/` folder in the current working directory or parent directories
2. If a pillar structure exists (e.g., `GitHub/`, `Personal/`, `Work/`), use the most appropriate pillar's Inbox
3. If working in a specific pillar already, use that pillar's Inbox
4. If no clear structure exists, save in the current directory

**Filename:** `YYYY-MM-DD GitHub Summary.md` (using today's date)

**Writing Guidelines:**

**CRITICAL: Write narrative prose, NOT tables or bullet lists.**

The output must be natural language paragraphs that tell a story. This is a summary for humans to read, not a data dump.

**DO NOT:**

- Use ASCII tables or box-drawing characters
- Create bullet-point lists of PRs/issues (except TLDR)
- Output metrics tables or counts
- List items without context or explanation
- Use sub-headers within sections (no "### Bug Fixes" under "## Issues")
- Group items with bold labels like "**Repository X:**"

**DO:**

- Write flowing paragraphs that explain what happened and why
- Connect related items into coherent narratives
- Reference URLs inline within sentences
- Explain the significance, not just the facts

**EXAMPLE - BAD (DO NOT DO THIS):**

```bash
## Pull Requests

### Authored

**acme-corp/api-gateway (4 PRs merged)**
- Fix: Token refresh logic — Fixed token expiry handling...
- Feature: Add rate limiting configuration...

**acme-corp/web-app (2 PRs merged)**
- Update: Migrate to new auth provider...
```

**EXAMPLE - GOOD (DO THIS INSTEAD):**

```bash
## Pull Requests

### Authored

I focused heavily on the API gateway this week. The most significant fix addressed [token refresh logic](url), which was causing intermittent authentication failures when tokens expired mid-request. This required understanding how the OAuth flow handles edge cases around clock skew. I also submitted [rate limiting configuration improvements](url) to give operators more control over throttling behaviour.

On the web application, I completed the [auth provider migration](url) that had been planned since Q3. The new provider offers better SSO support and simplified our session management code.
```

1. **Voice:** Write in first person ("I worked on...", "I submitted...")

2. **Structure:**
   - TLDR section first (3-5 bullet points only - this is the ONLY place for bullets)
   - Brief Overview paragraph summarising the main themes/focus areas
   - Issues section (Priority 1 - most context-rich) - PARAGRAPHS, not lists
   - Pull Requests section with Authored and Reviewed subsections (Priority 2) - PARAGRAPHS
   - Commits section for notable direct commits (Priority 3) - PARAGRAPHS

3. **TLDR Section:**
   - 3-5 bullet points maximum (the ONLY bullets in the document)
   - Focus on outcomes and impact, not activities
   - Use action verbs: "Fixed", "Merged", "Implemented", "Reviewed", "Shipped"
   - Include quantitative data where meaningful (e.g., "Merged 4 PRs", "Resolved 3 critical bugs")
   - Keep each bullet to one line
   - Prioritise the most significant accomplishments

4. **URLs:** Reference URLs inline within sentences, not as separate items
   - Good: "I opened [#1234: Safari login failures](url) to address user reports of..."
   - Bad: "- Issue #1234: Safari login failures [link]"
   - Bad: "| #1234 | Safari login failures | Open |"

5. **Context:** Explain the significance and context in prose
   - Mention why issues were opened
   - Describe what PRs addressed and key feedback received
   - Connect related items (issues linked to PRs, discussions that led to decisions)
   - Write complete sentences that flow into paragraphs

6. **Grouping:** Group by theme or project when natural, maintain chronological order within groups

7. **Metadata:** Include at the top:
   - Period (human-readable date range)
   - Organisation

8. **Tags:** End with relevant tags (e.g., `#context/github #type/note`)

**Template Structure:**

```markdown
# GitHub Summary

**Period:** <start-date> to <end-date>
**Organisation:** <org-name or "All">

---

## TLDR

- Fixed critical bug in URL transformation affecting readme rendering
- Merged 4 PRs improving API stability and documentation
- Reviewed 2 PRs for new feature implementations

---

## Overview

This week centred on stability improvements and documentation clarity. The main focus was resolving URL handling issues in the registry service that had been causing broken links in rendered readmes. I also contributed to the ongoing API modernisation effort and provided review feedback on upcoming features.

## Issues

I opened [#234: Blob URLs incorrectly generated for relative paths](url) after noticing broken images in several MCP server readmes. Investigation revealed the transformation logic assumed absolute URLs, but many repositories use relative paths for their assets. This led directly to the fix in PR #312.

## Pull Requests

### Authored

The URL transformation fix required careful handling of edge cases. In [#312: Fix blob URL generation](url), I updated the path resolution to detect relative URLs and prepend the repository's raw content base. The review feedback highlighted a missed edge case with nested directories, which I addressed in a follow-up commit.

I also submitted [#318: Update API deprecation notices](url) to clarify migration paths for external consumers. This involved updating both code comments and the public documentation.

### Reviewed

I reviewed [#320: Add rate limiting middleware](url), suggesting improvements to the backoff algorithm. The original implementation used fixed delays, but I recommended exponential backoff to better handle burst traffic.

## Commits

A few documentation fixes went directly to main without PRs: typo corrections in the contributing guide and updated contact information in the security policy.

---

#context/github #type/note
```

### 8. Report Completion

After saving the file, tell the user:

- Where the file was saved (full path)
- A brief summary of what was found (e.g., "Summarised 3 issues, 5 PRs, and 12 commits")
- Any notable items or limitations (e.g., "Some items had limited context due to API restrictions")

## Edge Cases

### No Organisations Found

If the user has no organisation memberships:

- Offer to search their personal account repositories
- Allow manual entry of an organisation name

### No Activity Found

If all queries return empty results:

- Still create the summary file
- Write: "No GitHub activity found for this period in the selected organisation."
- Suggest expanding the date range or selecting a different organisation

### API Rate Limits

If you encounter rate limit errors (HTTP 403):

- Inform the user about the rate limit
- Suggest trying again later or narrowing the time range/scope
- Continue with partial data if some queries succeeded

### Large Result Sets

If results exceed 100 items:

- Process what was retrieved
- Note in the summary: "Note: Results may be truncated. For complete data, consider narrowing the date range."

### Deep Fetch Failures

If individual item fetches fail:

- Include the item with basic information (title, URL, date)
- Note that full context was unavailable
- Continue processing other items

### Authentication Issues

If gh CLI is not authenticated:

- Inform the user
- Guide them to run: `gh auth login`
- Do not proceed until authentication is resolved

## Example

User: "Summarise my GitHub activity for the last two weeks"

Steps:

1. Check for MCP tools (not available) -> use gh CLI
2. Fetch orgs: returns `["github", "microsoft"]`
3. Ask user to select org -> user selects "github"
4. Ask for time period -> user confirms "Last 14 days"
5. Calculate dates: 2025-12-26 to 2026-01-09
6. Fetch issues, PRs authored, PRs reviewed, commits
7. For each item, fetch comments, reviews, linked items
8. Synthesise into natural language narrative
9. Determine location: working in obsidian vault with GitHub/ pillar -> save to `GitHub/Inbox/2026-01-09 GitHub Summary.md`
10. Report: "Summary saved to GitHub/Inbox/2026-01-09 GitHub Summary.md. Summarised 2 issues, 4 PRs authored, 3 PRs reviewed, and 15 commits."

## Notes

- The `--author @me` and `@me` syntax automatically uses the authenticated GitHub user
- Date format must be YYYY-MM-DD for GitHub API queries
- PRs reviewed may overlap with time period differently than authored PRs (uses "updated" vs "created")
- Commit search may return fewer results for private repositories
- The skill prioritises depth over breadth - better to summarise fewer items well than many items superficially
