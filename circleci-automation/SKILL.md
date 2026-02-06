---
name: circleci-automation
description: "Automate CircleCI tasks via Rube MCP (Composio): trigger pipelines, monitor workflows/jobs, retrieve artifacts and test metadata. Always search tools first for current schemas."
requires:
  mcp: [rube]
---

# CircleCI Automation via Rube MCP

Automate CircleCI CI/CD operations through Composio's CircleCI toolkit via Rube MCP.

## Prerequisites

- Rube MCP must be connected (RUBE_SEARCH_TOOLS available)
- Active CircleCI connection via `RUBE_MANAGE_CONNECTIONS` with toolkit `circleci`
- Always call `RUBE_SEARCH_TOOLS` first to get current tool schemas

## Setup

**Get Rube MCP**: Add `https://rube.app/mcp` as an MCP server in your client configuration. No API keys needed — just add the endpoint and it works.


1. Verify Rube MCP is available by confirming `RUBE_SEARCH_TOOLS` responds
2. Call `RUBE_MANAGE_CONNECTIONS` with toolkit `circleci`
3. If connection is not ACTIVE, follow the returned auth link to complete CircleCI authentication
4. Confirm connection status shows ACTIVE before running any workflows

## Core Workflows

### 1. Trigger a Pipeline

**When to use**: User wants to start a new CI/CD pipeline run

**Tool sequence**:
1. `CIRCLECI_TRIGGER_PIPELINE` - Trigger a new pipeline on a project [Required]
2. `CIRCLECI_LIST_WORKFLOWS_BY_PIPELINE_ID` - Monitor resulting workflows [Optional]

**Key parameters**:
- `project_slug`: Project identifier in format `gh/org/repo` or `bb/org/repo`
- `branch`: Git branch to run the pipeline on
- `tag`: Git tag to run the pipeline on (mutually exclusive with branch)
- `parameters`: Pipeline parameter key-value pairs

**Pitfalls**:
- `project_slug` format is `{vcs}/{org}/{repo}` (e.g., `gh/myorg/myrepo`)
- `branch` and `tag` are mutually exclusive; providing both causes an error
- Pipeline parameters must match those defined in `.circleci/config.yml`
- Triggering returns a pipeline ID; workflows start asynchronously

### 2. Monitor Pipelines and Workflows

**When to use**: User wants to check the status of pipelines or workflows

**Tool sequence**:
1. `CIRCLECI_LIST_PIPELINES_FOR_PROJECT` - List recent pipelines for a project [Required]
2. `CIRCLECI_LIST_WORKFLOWS_BY_PIPELINE_ID` - List workflows within a pipeline [Required]
3. `CIRCLECI_GET_PIPELINE_CONFIG` - View the pipeline configuration used [Optional]

**Key parameters**:
- `project_slug`: Project identifier in `{vcs}/{org}/{repo}` format
- `pipeline_id`: UUID of a specific pipeline
- `branch`: Filter pipelines by branch name
- `page_token`: Pagination cursor for next page of results

**Pitfalls**:
- Pipeline IDs are UUIDs, not numeric IDs
- Workflows inherit the pipeline ID; a single pipeline can have multiple workflows
- Workflow states include: success, running, not_run, failed, error, failing, on_hold, canceled, unauthorized
- `page_token` is returned in responses for pagination; continue until absent

### 3. Inspect Job Details

**When to use**: User wants to drill into a specific job's execution details

**Tool sequence**:
1. `CIRCLECI_LIST_WORKFLOWS_BY_PIPELINE_ID` - Find workflow containing the job [Prerequisite]
2. `CIRCLECI_GET_JOB_DETAILS` - Get detailed job information [Required]

**Key parameters**:
- `project_slug`: Project identifier
- `job_number`: Numeric job number (not UUID)

**Pitfalls**:
- Job numbers are integers, not UUIDs (unlike pipeline and workflow IDs)
- Job details include executor type, parallelism, start/stop times, and status
- Job statuses: success, running, not_run, failed, retried, timedout, infrastructure_fail, canceled

### 4. Retrieve Build Artifacts

**When to use**: User wants to download or list artifacts produced by a job

**Tool sequence**:
1. `CIRCLECI_GET_JOB_DETAILS` - Confirm job completed successfully [Prerequisite]
2. `CIRCLECI_GET_JOB_ARTIFACTS` - List all artifacts from the job [Required]

**Key parameters**:
- `project_slug`: Project identifier
- `job_number`: Numeric job number

**Pitfalls**:
- Artifacts are only available after job completion
- Each artifact has a `path` and `url` for download
- Artifact URLs may require authentication headers to download
- Large artifacts may have download size limits

### 5. Review Test Results

**When to use**: User wants to check test outcomes for a specific job

**Tool sequence**:
1. `CIRCLECI_GET_JOB_DETAILS` - Verify job ran tests [Prerequisite]
2. `CIRCLECI_GET_TEST_METADATA` - Retrieve test results and metadata [Required]

**Key parameters**:
- `project_slug`: Project identifier
- `job_number`: Numeric job number

**Pitfalls**:
- Test metadata requires the job to have uploaded test results (JUnit XML format)
- If no test results were uploaded, the response will be empty
- Test metadata includes classname, name, result, message, and run_time fields
- Failed tests include failure messages in the `message` field

## Common Patterns

### Project Slug Format

```
Format: {vcs_type}/{org_name}/{repo_name}
- GitHub:    gh/myorg/myrepo
- Bitbucket: bb/myorg/myrepo
```

### Pipeline -> Workflow -> Job Hierarchy

```
1. Call CIRCLECI_LIST_PIPELINES_FOR_PROJECT to get pipeline IDs
2. Call CIRCLECI_LIST_WORKFLOWS_BY_PIPELINE_ID with pipeline_id
3. Extract job numbers from workflow details
4. Call CIRCLECI_GET_JOB_DETAILS with job_number
```

### Pagination

- Check response for `next_page_token` field
- Pass token as `page_token` in next request
- Continue until `next_page_token` is absent or null

## Known Pitfalls

**ID Formats**:
- Pipeline IDs: UUIDs (e.g., `5034460f-c7c4-4c43-9457-de07e2029e7b`)
- Workflow IDs: UUIDs
- Job numbers: Integers (e.g., `123`)
- Do NOT mix up UUIDs and integers between different endpoints

**Project Slugs**:
- Must include VCS prefix: `gh/` for GitHub, `bb/` for Bitbucket
- Organization and repo names are case-sensitive
- Incorrect slug format causes 404 errors

**Rate Limits**:
- CircleCI API has per-endpoint rate limits
- Implement exponential backoff on 429 responses
- Avoid rapid polling; use reasonable intervals (5-10 seconds)

## Quick Reference

| Task | Tool Slug | Key Params |
|------|-----------|------------|
| Trigger pipeline | CIRCLECI_TRIGGER_PIPELINE | project_slug, branch, parameters |
| List pipelines | CIRCLECI_LIST_PIPELINES_FOR_PROJECT | project_slug, branch |
| List workflows | CIRCLECI_LIST_WORKFLOWS_BY_PIPELINE_ID | pipeline_id |
| Get pipeline config | CIRCLECI_GET_PIPELINE_CONFIG | pipeline_id |
| Get job details | CIRCLECI_GET_JOB_DETAILS | project_slug, job_number |
| Get job artifacts | CIRCLECI_GET_JOB_ARTIFACTS | project_slug, job_number |
| Get test metadata | CIRCLECI_GET_TEST_METADATA | project_slug, job_number |
