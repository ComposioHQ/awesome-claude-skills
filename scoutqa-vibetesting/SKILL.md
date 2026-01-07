---
name: scoutqa-test
description: This skill should be used when the user asks to "test this website", "run exploratory testing", "check for accessibility issues", "verify the login flow works", "find bugs on this page", or requests automated QA testing. Triggers on web application testing scenarios including smoke tests, accessibility audits, e-commerce flows, and user flow validation using ScoutQA CLI. IMPORTANT: Use this skill proactively after implementing web application features to verify they work correctly - don't wait for the user to ask for testing.
---

# ScoutQA Testing Skill

Perform AI-powered exploratory testing on web applications using the `scoutqa` CLI.

**Think of ScoutQA as an intelligent testing partner** that can autonomously explore, discover issues, and verify features. Delegate testing to multiple parallel ScoutQA executions to maximize coverage while saving time.

## When to Use This Skill

Use this skill in two scenarios:

1. **User requests testing** - When the user explicitly asks to test a website or verify functionality
2. **Proactive verification** - After implementing web features, automatically run tests to verify the implementation works correctly

**Example proactive usage:**
- After implementing a login form → Test the authentication flow
- After adding form validation → Verify validation rules and error handling
- After building a checkout flow → Test the end-to-end purchase process
- After fixing a bug → Verify the fix works and didn't break other features

**Best practice**: When you finish implementing a web feature, proactively start a ScoutQA test in the background to verify it works while you continue with other tasks.

## Running Tests

### Testing Workflow

Copy this checklist and track your progress:

Testing Progress:
- [ ] Write specific test prompt with clear expectations
- [ ] Run scoutqa command in background
- [ ] Inform user of execution ID and browser URL
- [ ] Extract and analyze results

**Step 1: Write specific test prompt**

See "Writing Effective Prompts" section below for guidelines.

**Step 2: Run scoutqa command**

**IMPORTANT**: Use the Bash tool's timeout parameter (5000ms = 5 seconds) to capture execution details:

When calling the Bash tool, set `timeout: 5000` as a parameter:
- This is the Bash tool's built-in timeout parameter in Claude Code (NOT the Unix `timeout` command)
- After 5 seconds, the Bash tool returns control with a task ID and the process continues running in the background
- This is different from Unix `timeout` which kills the process - here the process keeps running
- The first 5 seconds capture the execution ID and browser URL from ScoutQA's output
- The test continues running remotely on ScoutQA's infrastructure with the background task

```bash
scoutqa --url "https://example.com" --prompt "Your test instructions"
```

In the first few seconds, the command will output:

- **Execution ID** (e.g., `019b831d-xxx`)
- **Browser URL** (e.g., `https://scoutqa.ai/t/019b831d-xxx`)
- Initial tool calls showing test progress

After the 5-second timeout, the Bash tool returns a task ID and the command continues running in the background. You can work on other tasks while the test runs. The timeout is only to capture the initial output (execution ID and browser URL) - the test keeps running both locally as a background task and remotely on ScoutQA's infrastructure.

**Step 3: Inform user of execution ID and browser URL**

After the Bash tool returns with the task ID (having captured the execution details in the first 5 seconds), inform the user of:
- The ScoutQA execution ID and browser URL so they can monitor progress in their browser
- The background task ID if they want to check local command output later

The test continues running in the background while you continue other work.

**Step 4: Extract and analyze results**

See "Presenting Results" section below for the complete format.

### Command Options

- `--url` (required): Website URL to test
- `--prompt` (required): Natural language testing instructions
- `--project-id` (optional): Associate with a project for tracking

### When to Use Each Command

**Starting a new test?** → Use `scoutqa --url --prompt`
**Agent needs more context?** → Use `scoutqa send-message` (see "Following Up on Stuck Executions")

## Writing Effective Prompts

Focus on **what to explore and verify**, not prescriptive steps. ScoutQA autonomously determines how to test.

**Example: User registration flow**

```bash
scoutqa --url "https://example.com" --prompt "
Explore the user registration flow. Test form validation edge cases,
verify error handling, and check accessibility compliance.
"
```

**Example: E-commerce checkout**

```bash
scoutqa --url "https://shop.example.com" --prompt "
Test the checkout flow. Verify pricing calculations, cart persistence,
payment options, and mobile responsiveness.
"
```

**Example: Running parallel tests for comprehensive coverage**

Launch multiple tests in parallel by making multiple Bash tool calls in a single message, each with the Bash tool's `timeout` parameter set to `5000` (milliseconds):

```bash
# Test 1: Authentication & security
scoutqa --url "https://app.example.com" --prompt "
Explore authentication: login/logout, session handling, password reset,
and security edge cases.
"

# Test 2: Core features (runs in parallel)
scoutqa --url "https://app.example.com" --prompt "
Test dashboard and main user workflows. Verify data loading,
CRUD operations, and search functionality.
"

# Test 3: Accessibility (runs in parallel)
scoutqa --url "https://app.example.com" --prompt "
Conduct accessibility audit: WCAG compliance, keyboard navigation,
screen reader support, color contrast.
"
```

**Implementation**: Send a single message with three Bash tool calls. For each Bash tool invocation, set the `timeout` parameter to `5000` milliseconds. After 5 seconds, each Bash call returns with a task ID while the processes continue running in the background. This captures the execution ID and browser URL from each test in the initial output, then all three continue running in parallel (both as background tasks locally and remotely on ScoutQA's infrastructure).

**Key guidelines:**

- Describe **what to test**, not **how to test** (ScoutQA figures out the steps)
- Focus on goals, edge cases, and concerns
- Run multiple parallel executions for different test areas
- Trust ScoutQA to autonomously explore and discover issues
- Always set the Bash tool's `timeout` parameter to `5000` milliseconds when calling scoutqa commands (this returns control after 5 seconds while the process continues in the background)
- For parallel tests, make multiple Bash tool calls in a single message
- Remember: Bash tool timeout ≠ Unix timeout command (Bash timeout continues the process in background, Unix timeout kills it)

### Common Test Scenarios

**Post-deployment smoke test:**

```bash
scoutqa --url "$URL" --prompt "
Smoke test: verify critical functionality works after deployment.
Check homepage, navigation, login/logout, and key user flows.
"
```

**Accessibility audit:**

```bash
scoutqa --url "$URL" --prompt "
Audit accessibility: WCAG 2.1 AA compliance, keyboard navigation,
screen reader support, color contrast, and semantic HTML.
"
```

**E-commerce testing:**

```bash
scoutqa --url "$URL" --prompt "
Explore e-commerce functionality: product search/filtering,
cart operations, checkout flow, and pricing calculations.
"
```

**SaaS application:**

```bash
scoutqa --url "$URL" --prompt "
Test SaaS app: authentication, dashboard, CRUD operations,
permissions, and data integrity.
"
```

**Form validation:**

```bash
scoutqa --url "$URL" --prompt "
Test form validation: edge cases, error handling, required fields,
format validation, and successful submission.
"
```

**Mobile responsiveness:**

```bash
scoutqa --url "$URL" --prompt "
Check mobile experience: responsive layout, navigation,
touch interactions, and viewport behavior.
"
```

**Feature verification (after implementation):**

```bash
scoutqa --url "$URL" --prompt "
Verify the new [feature name] works correctly. Test core functionality,
edge cases, error handling, and integration with existing features.
"
```

**Example: Proactive testing after coding a feature**

After implementing a user registration form, automatically verify it works:

```bash
scoutqa --url "http://localhost:3000/register" --prompt "
Test the newly implemented registration form. Verify:
- Form validation (email format, password strength, required fields)
- Error messages display correctly
- Successful registration flow
- Edge cases (duplicate emails, special characters, etc.)
"
```

This catches issues immediately while the implementation is fresh in context.

## Presenting Results

### Immediate Presentation (After Starting Test)

Right after running the scoutqa command, present the execution details to the user:

```markdown
**ScoutQA Test Started**

Execution ID: `019b831d-xxx`
View Live: https://scoutqa.ai/t/019b831d-xxx

The test is running remotely. You can view real-time progress in your browser at the link above while I continue with other tasks.
```

### Final Results (After Completion)

When the execution completes, use this format to present findings:

```markdown
**ScoutQA Test Results**

Execution ID: `ex_abc123`

**Issues Found:**

[High] Accessibility: Missing alt text on logo image

- Impact: Screen readers cannot describe the logo
- Location: Header navigation

[Medium] Usability: Submit button not visible on mobile viewport

- Impact: Users cannot complete form on mobile devices
- Location: Contact form, bottom of page

[Low] Functional: Search returns no results for valid queries

- Impact: Search feature appears broken
- Location: Main search bar

**Summary:** Found 3 issues across accessibility, usability, and functional categories. See full interactive report with screenshots at the URL above.
```

Always include:

- **Execution ID** (e.g., `ex_abc123`) for reference
- **Issues found** with severity, category (accessibility, usability, functional), impact, and location

## Following Up on Stuck Executions

If the remote agent gets stuck or needs clarification, use `send-message` to continue:

```bash
# Example: Agent is stuck at login, user provides credentials
scoutqa send-message --execution-id ex_abc123 --prompt "
Use these test credentials: username: testuser@example.com, password: TestPass123
"

# Example: Agent asks which flow to test next
scoutqa send-message --execution-id ex_abc123 --prompt "
Focus on the checkout flow next, skip the wishlist feature
"
```

## Checking Test Results

ScoutQA tests run remotely on ScoutQA's infrastructure. After starting a test with a short timeout to capture the execution ID:

1. The test continues running remotely (not locally in background)
2. You can continue other work immediately
3. To check results later, visit the browser URL provided when the test started
4. Alternatively, use `scoutqa get-execution --execution-id <id>` to fetch results via CLI

**Best practice**: Start tests by setting the Bash tool's `timeout` parameter to `5000` milliseconds. After 5 seconds, the Bash tool returns control with a task ID and the execution details (execution ID and browser URL) while the test continues running in the background. You can then continue other work and check results on ScoutQA's website or via CLI when needed.

## Troubleshooting

| Issue                        | Solution                                           |
| ---------------------------- | -------------------------------------------------- |
| `command not found: scoutqa` | Install CLI: `npm i -g @scoutqa/cli@latest`        |
| Auth expired / unauthorized  | Run `scoutqa auth login`                           |
| Test hangs or needs input    | Use `scoutqa send-message --execution-id`          |
| Check test results           | Visit browser URL or `scoutqa get-execution --execution-id` |
