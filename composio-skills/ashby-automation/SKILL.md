---
name: Ashby Automation
description: "Automate recruiting and hiring workflows in Ashby -- manage candidates, jobs, applications, interviews, and notes through natural language commands."
requires:
  mcp:
    - rube
---

# Ashby Automation

Automate your Ashby ATS recruiting operations directly from Claude Code. Create candidates, post jobs, manage applications, view interview schedules, and search your talent pipeline -- all without leaving your terminal.

**Toolkit docs:** [composio.dev/toolkits/ashby](https://composio.dev/toolkits/ashby)

---

## Setup

1. Add the Rube MCP server to your Claude Code config with URL: `https://rube.app/mcp`
2. When prompted, authenticate your Ashby account through the connection link provided
3. Start automating your recruiting workflows with natural language

---

## Core Workflows

### 1. Manage Candidates

Create, list, search, update, and retrieve detailed candidate information.

**Tools:** `ASHBY_CREATE_CANDIDATE`, `ASHBY_LIST_CANDIDATES`, `ASHBY_SEARCH_CANDIDATES`, `ASHBY_GET_CANDIDATE_INFO`, `ASHBY_UPDATE_CANDIDATE`

```
Create a candidate named "Jane Smith" with email jane@example.com and LinkedIn profile https://linkedin.com/in/janesmith
```

Key parameters for `ASHBY_CREATE_CANDIDATE`:
- `name` (required) -- full name of the candidate
- `email` -- primary email address
- `phoneNumber`, `linkedInUrl`, `githubUrl`, `websiteUrl` -- contact/social profiles

Key parameters for `ASHBY_SEARCH_CANDIDATES`:
- `email` -- exact email match
- `name` -- partial name match

Key parameters for `ASHBY_LIST_CANDIDATES`:
- `perPage` (max 100) / `cursor` -- pagination
- `syncToken` -- for incremental updates since last sync

### 2. Create and List Jobs

Post new job openings and browse existing positions.

**Tools:** `ASHBY_CREATE_JOB`, `ASHBY_LIST_JOBS`, `ASHBY_GET_JOB_INFO`

```
Create a new "Senior Software Engineer" job in team dept-123 at location loc-456 with brand brand-789
```

Key parameters for `ASHBY_CREATE_JOB`:
- `title` (required) -- job title
- `teamId` (required) -- department/team ID (from list departments)
- `locationId` (required) -- office location ID (from list locations)
- `brandId` (required) -- employer brand ID (from list brands)
- `defaultInterviewPlanId` -- required to open the job for applications
- `jobTemplateId` -- pre-populate from a template

Key parameters for `ASHBY_LIST_JOBS`:
- `perPage` (max 100) / `cursor` / `syncToken` -- pagination and incremental sync

**Note:** Newly created jobs start in "Draft" status. You must set a `defaultInterviewPlanId` to open/publish the job.

### 3. Manage Applications

Create applications to connect candidates to jobs and track their progress.

**Tools:** `ASHBY_CREATE_APPLICATION`, `ASHBY_LIST_APPLICATIONS`

```
Apply candidate cand-abc123 to job job-xyz789 with source src-referral
```

Key parameters for `ASHBY_CREATE_APPLICATION`:
- `candidateId` (required) -- UUID of an existing candidate
- `jobId` (required) -- UUID of an existing job
- `sourceId` -- UUID of the application source (LinkedIn, Referral, etc.)
- `creditedToUserId` -- UUID of recruiter/referrer to credit
- `interviewStageId` -- place directly into a specific stage (defaults to first stage)

Key parameters for `ASHBY_LIST_APPLICATIONS`:
- `perPage` (max 100) / `cursor` / `syncToken` -- pagination and incremental sync

### 4. View Interview Schedules

List scheduled interviews with timing, interviewer, and candidate details.

**Tool:** `ASHBY_LIST_INTERVIEW_SCHEDULES`

```
Show me all upcoming interview schedules
```

Key parameters:
- `perPage` (max 100) / `cursor` -- pagination
- `syncToken` -- incremental sync for changed schedules

### 5. Candidate Notes

View internal notes, observations, and recruiter comments on candidates.

**Tool:** `ASHBY_LIST_CANDIDATE_NOTES`

```
Show me all notes for candidate cand-abc123
```

- Retrieves all notes added by recruiters and hiring team members
- Useful for reviewing interview feedback and internal assessments

### 6. Pipeline Reporting

Combine listing tools to build hiring pipeline reports.

**Tools:** `ASHBY_LIST_CANDIDATES`, `ASHBY_LIST_APPLICATIONS`, `ASHBY_LIST_JOBS`

```
List all applications to see the current state of our hiring pipeline
```

- Use `syncToken` for incremental data fetches (efficient for recurring reports)
- Combine candidate, application, and job data for full pipeline visibility
- Paginate through all results with `cursor` for complete datasets

---

## Known Pitfalls

- **Jobs start in Draft:** Newly created jobs via `ASHBY_CREATE_JOB` start in "Draft" status and cannot accept applications until a `defaultInterviewPlanId` is set and the job is opened.
- **Four required fields for jobs:** `ASHBY_CREATE_JOB` requires `title`, `teamId`, `locationId`, and `brandId`. Use list departments, locations, and brands endpoints to discover valid IDs.
- **Candidate before application:** A candidate must exist before creating an application. Always create or find the candidate first, then create the application.
- **Cursor-based pagination:** All list endpoints use cursor-based pagination with `perPage` (max 100) and `cursor`. You cannot jump to arbitrary pages -- you must iterate sequentially.
- **`syncToken` for efficiency:** Use `syncToken` from previous responses to fetch only changed records. This dramatically reduces API calls for recurring workflows.
- **UUID format everywhere:** All IDs (candidates, jobs, applications, stages) are UUIDs. Passing malformed IDs returns 400 errors.
- **Search limitations:** `ASHBY_SEARCH_CANDIDATES` supports exact email match or partial name match, but not combined queries or other fields. For broader searches, use `ASHBY_LIST_CANDIDATES` with pagination.

---

## Quick Reference

| Tool Slug | Description |
|---|---|
| `ASHBY_CREATE_CANDIDATE` | Create a new candidate (requires `name`) |
| `ASHBY_LIST_CANDIDATES` | List all candidates with pagination and sync |
| `ASHBY_SEARCH_CANDIDATES` | Search candidates by email or name |
| `ASHBY_GET_CANDIDATE_INFO` | Get full candidate details (requires `candidateId`) |
| `ASHBY_UPDATE_CANDIDATE` | Update candidate profile information |
| `ASHBY_LIST_CANDIDATE_NOTES` | List internal notes for a candidate |
| `ASHBY_CREATE_JOB` | Create a job opening (requires `title`, `teamId`, `locationId`, `brandId`) |
| `ASHBY_LIST_JOBS` | List all jobs with pagination and sync |
| `ASHBY_GET_JOB_INFO` | Get full job details by ID |
| `ASHBY_CREATE_APPLICATION` | Apply a candidate to a job (requires `candidateId`, `jobId`) |
| `ASHBY_LIST_APPLICATIONS` | List all applications with pagination and sync |
| `ASHBY_LIST_INTERVIEW_SCHEDULES` | List scheduled interviews with pagination |

---

*Powered by [Composio](https://composio.dev)*
