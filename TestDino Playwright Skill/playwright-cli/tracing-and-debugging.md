# Tracing and Debugging

> **When to use**: Debugging failing actions, analyzing performance bottlenecks, capturing execution evidence, understanding why an interaction didn't work, or inspecting network and console activity during automation.
> **Prerequisites**: [core-commands.md](core-commands.md) for basic CLI usage

## Quick Reference

```bash
# Trace a session
playwright-cli tracing-start
playwright-cli open https://example.com
playwright-cli click e4
playwright-cli fill e7 "test"
playwright-cli tracing-stop

# View console messages
playwright-cli console                # All levels
playwright-cli console error          # Errors only
playwright-cli console warning        # Warnings only

# View network activity
playwright-cli network
```

## Tracing

Traces capture **everything** — DOM snapshots, screenshots, network activity, console logs, and timing — for every action during a session.

### Basic Usage

```bash
# Start recording before the flow you want to debug
playwright-cli tracing-start

# Perform actions
playwright-cli open https://example.com
playwright-cli snapshot
playwright-cli click e4
playwright-cli fill e7 "test data"
playwright-cli click e9

# Stop and save the trace
playwright-cli tracing-stop
```

### What Traces Capture

| Category | Details |
|----------|---------|
| **Actions** | Every click, fill, hover, keyboard input, navigation — with timing |
| **DOM Snapshots** | Full DOM state before and after each action |
| **Screenshots** | Visual state at each step |
| **Network** | All HTTP requests, responses, headers, bodies, timing |
| **Console** | All `console.log`, `console.warn`, `console.error` messages |
| **Timing** | Precise duration for each operation |
| **Source** | Which command triggered each action |

### Trace Output Files

When tracing is active, Playwright creates a `traces/` directory:

**`trace-{timestamp}.trace`** — Main trace file containing:
- Action log with DOM snapshots
- Screenshots at each step
- Timing information
- Console messages

**`trace-{timestamp}.network`** — Network activity:
- All HTTP requests and responses
- Request/response headers and bodies
- DNS, connect, TLS, TTFB, download timing
- Resource sizes and failed requests

**`resources/`** — Cached assets for trace replay:
- Images, fonts, stylesheets, scripts
- Response bodies for offline replay

### Viewing Traces

Open traces in Playwright's Trace Viewer — a rich GUI for step-by-step debugging:

```bash
# Open trace in the Trace Viewer web app
npx playwright show-trace traces/trace-123456.trace

# Or use the online Trace Viewer
# Upload trace file to: https://trace.playwright.dev
```

The Trace Viewer shows:
- **Timeline**: Step-by-step actions with screenshots
- **DOM Snapshot**: Inspect elements at each step (like DevTools)
- **Network**: Waterfall view of all requests
- **Console**: Log messages with timestamps
- **Source**: The code that triggered each action

## Console Monitoring

View JavaScript console output from the page — essential for catching errors:

```bash
# Show all console messages
playwright-cli console

# Filter by severity level
playwright-cli console error         # Only errors
playwright-cli console warning       # Only warnings
playwright-cli console info          # Only info messages
playwright-cli console log           # Only log messages
```

### Common Debugging Pattern

```bash
playwright-cli open https://app.example.com
playwright-cli snapshot
playwright-cli click e5              # Something unexpected happens

# Check if there were JavaScript errors
playwright-cli console error
# Output might show:
# [error] TypeError: Cannot read properties of undefined (reading 'map')
# [error] Uncaught ReferenceError: processData is not defined
```

### Watch Console During Interaction

Use `run-code` to set up continuous console monitoring:

```bash
playwright-cli run-code "async page => {
  page.on('console', msg => {
    if (msg.type() === 'error' || msg.type() === 'warning') {
      console.log(\`[\${msg.type()}] \${msg.text()}\`);
    }
  });
}"
# Now interact — errors and warnings will print as they occur
playwright-cli click e5
playwright-cli fill e3 "test"
```

### Capture Uncaught Exceptions

```bash
playwright-cli run-code "async page => {
  page.on('pageerror', error => {
    console.log('Uncaught exception:', error.message);
  });
}"
```

## Network Monitoring

View all network requests made by the page:

```bash
playwright-cli network
```

### Watch Network in Real-Time

```bash
playwright-cli run-code "async page => {
  page.on('request', request => {
    console.log(\`>> \${request.method()} \${request.url()}\`);
  });
  page.on('response', response => {
    console.log(\`<< \${response.status()} \${response.url()}\`);
  });
}"

# Now interact — requests will print as they happen
playwright-cli click e5
```

### Monitor Failed Requests

```bash
playwright-cli run-code "async page => {
  page.on('requestfailed', request => {
    console.log(\`FAILED: \${request.method()} \${request.url()} - \${request.failure()?.errorText}\`);
  });
}"
```

### Inspect a Specific Response

```bash
playwright-cli run-code "async page => {
  const response = await page.waitForResponse('**/api/users');
  return {
    status: response.status(),
    statusText: response.statusText(),
    headers: response.headers(),
    body: await response.json()
  };
}"
```

## Debugging Strategies

### Strategy 1: Snapshot Before and After

The simplest debugging approach — see what changed:

```bash
playwright-cli snapshot --filename=before.yaml
playwright-cli click e5
playwright-cli snapshot --filename=after.yaml
# Compare the two snapshots to understand what changed
```

### Strategy 2: Trace the Failing Flow

Start tracing before the step that fails:

```bash
playwright-cli tracing-start

# Reproduce the issue
playwright-cli goto https://app.example.com/checkout
playwright-cli fill e1 "Jane Doe"
playwright-cli click e5    # This step fails

playwright-cli tracing-stop
# Open trace to see DOM state when the click was attempted
```

### Strategy 3: Check Element State

When an interaction fails, check what state the element is actually in:

```bash
# Is the element visible?
playwright-cli eval "el => window.getComputedStyle(el).display" e5
playwright-cli eval "el => window.getComputedStyle(el).visibility" e5
playwright-cli eval "el => el.getBoundingClientRect()" e5

# Is it covered by another element?
playwright-cli eval "el => {
  const rect = el.getBoundingClientRect();
  const topEl = document.elementFromPoint(rect.x + rect.width/2, rect.y + rect.height/2);
  return topEl === el ? 'Element is on top' : 'Covered by: ' + topEl?.tagName + '.' + topEl?.className;
}" e5

# Is it disabled?
playwright-cli eval "el => el.disabled" e5
playwright-cli eval "el => el.getAttribute('aria-disabled')" e5
```

### Strategy 4: Console + Network Combined

```bash
# Set up monitoring for both console and network
playwright-cli run-code "async page => {
  page.on('console', msg => {
    if (msg.type() === 'error') console.log('[CONSOLE]', msg.text());
  });
  page.on('requestfailed', req => {
    console.log('[NETWORK]', req.method(), req.url(), req.failure()?.errorText);
  });
  page.on('response', resp => {
    if (resp.status() >= 400) {
      console.log('[HTTP ERROR]', resp.status(), resp.url());
    }
  });
}"

# Now interact and watch for errors
playwright-cli click e5
playwright-cli fill e3 "test"
```

### Strategy 5: Wait and Retry

If actions fail due to timing, add explicit waits:

```bash
# Wait for element to be actionable
playwright-cli run-code "async page => {
  await page.locator('#dynamic-button').waitFor({ state: 'visible', timeout: 10000 });
}"
playwright-cli snapshot
playwright-cli click e5

# Wait for page to settle
playwright-cli run-code "async page => {
  await page.waitForLoadState('networkidle');
}"
playwright-cli snapshot
```

## Performance Analysis

### Measure Page Load Time

```bash
playwright-cli run-code "async page => {
  const timing = await page.evaluate(() => {
    const t = performance.timing;
    return {
      dns: t.domainLookupEnd - t.domainLookupStart,
      tcp: t.connectEnd - t.connectStart,
      ttfb: t.responseStart - t.requestStart,
      download: t.responseEnd - t.responseStart,
      domParsing: t.domInteractive - t.domLoading,
      domComplete: t.domComplete - t.domLoading,
      total: t.loadEventEnd - t.navigationStart
    };
  });
  return timing;
}"
```

### Analyze with Navigation Timing API

```bash
playwright-cli run-code "async page => {
  const entries = await page.evaluate(() => {
    return performance.getEntriesByType('navigation').map(e => ({
      type: e.type,
      redirectTime: e.redirectEnd - e.redirectStart,
      dnsTime: e.domainLookupEnd - e.domainLookupStart,
      connectTime: e.connectEnd - e.connectStart,
      tlsTime: e.secureConnectionStart > 0 ? e.connectEnd - e.secureConnectionStart : 0,
      requestTime: e.responseStart - e.requestStart,
      responseTime: e.responseEnd - e.responseStart,
      domProcessing: e.domComplete - e.domInteractive,
      loadTime: e.loadEventEnd - e.loadEventStart,
      totalTime: e.loadEventEnd - e.startTime
    }));
  });
  return entries;
}"
```

### List Slow Resources

```bash
playwright-cli run-code "async page => {
  const resources = await page.evaluate(() => {
    return performance.getEntriesByType('resource')
      .map(r => ({ name: r.name.split('/').pop(), duration: Math.round(r.duration), size: r.transferSize }))
      .sort((a, b) => b.duration - a.duration)
      .slice(0, 10);
  });
  return resources;
}"
```

## Trace vs Video vs Screenshot

Choose the right capture method:

| Feature | Trace | Video | Screenshot |
|---------|-------|-------|------------|
| **Format** | `.trace` file | `.webm` video | `.png` image |
| **DOM inspection** | Yes | No | No |
| **Network details** | Yes | No | No |
| **Step-by-step replay** | Yes | Continuous | Single frame |
| **Console logs** | Yes | No | No |
| **File size** | Medium | Large | Small |
| **Best for** | Debugging | Demos, documentation | Quick capture |

### Decision Guide

- **Something failed and you don't know why** → Trace
- **Need to show a flow to someone** → Video
- **Need to verify visual state** → Screenshot
- **Need to analyze performance** → Trace (has network waterfall)
- **CI artifact for failed test** → Trace + Screenshot

## Best Practices

### 1. Start Tracing BEFORE the Problem

Trace the entire flow leading up to the failure, not just the failing step:

```bash
playwright-cli tracing-start
# Reproduce the full flow from the beginning
playwright-cli open https://app.example.com
playwright-cli fill e1 "user@example.com"
playwright-cli click e3
# ... all steps leading to the failure ...
playwright-cli tracing-stop
```

### 2. Use Console Monitoring Proactively

Start console monitoring at the beginning of any debugging session:

```bash
playwright-cli run-code "async page => {
  page.on('console', msg => console.log(\`[\${msg.type()}] \${msg.text()}\`));
  page.on('pageerror', err => console.log('[EXCEPTION]', err.message));
}"
```

### 3. Clean Up Old Traces

Traces consume significant disk space:

```bash
# Remove traces older than 7 days
find .playwright-cli/traces -mtime +7 -delete
```

### 4. Combine Techniques

The most effective debugging combines multiple approaches:

```bash
playwright-cli tracing-start           # Capture everything
playwright-cli console error           # Watch for JS errors
playwright-cli network                 # Watch for failed requests
playwright-cli snapshot                # See current state
# ... interact and debug ...
playwright-cli tracing-stop            # Save trace for detailed analysis
```
