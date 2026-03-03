# Request Mocking

> **When to use**: Intercepting, mocking, modifying, or blocking network requests during browser automation — API stubbing, simulating errors, testing offline behavior, removing tracking, or speeding up pages by blocking heavy assets.
> **Prerequisites**: [core-commands.md](core-commands.md) for basic CLI usage

## Quick Reference

```bash
# Block all images
playwright-cli route "**/*.jpg" --status=404

# Mock API response with JSON body
playwright-cli route "**/api/users" --body='[{"id":1,"name":"Alice"}]' --content-type=application/json

# Add custom response headers
playwright-cli route "**/api/data" --body='{"ok":true}' --header="X-Custom: value"

# Strip request headers (e.g., remove auth for testing)
playwright-cli route "**/*" --remove-header=cookie,authorization

# List active routes
playwright-cli route-list

# Remove a specific route
playwright-cli unroute "**/*.jpg"

# Remove all routes
playwright-cli unroute
```

## URL Patterns

playwright-cli uses glob patterns for URL matching:

| Pattern | Matches | Example URLs |
|---------|---------|-------------|
| `**/api/users` | Exact path on any origin | `https://api.example.com/api/users` |
| `**/api/*/details` | Wildcard in path segment | `https://api.example.com/api/123/details` |
| `**/*.{png,jpg,jpeg}` | Multiple file extensions | `https://cdn.example.com/hero.png` |
| `**/search?q=*` | Query parameters | `https://example.com/search?q=test` |
| `https://api.example.com/**` | All requests to a specific origin | `https://api.example.com/v2/users` |
| `**/*` | All requests | Everything |

## CLI Route Commands

### Mock with Status Code

```bash
# Return 404 for all image requests
playwright-cli route "**/*.jpg" --status=404

# Return 503 Service Unavailable
playwright-cli route "**/api/health" --status=503

# Return 401 Unauthorized
playwright-cli route "**/api/protected" --status=401
```

### Mock with JSON Response

```bash
# Simple JSON body
playwright-cli route "**/api/users" --body='[{"id":1,"name":"Alice"},{"id":2,"name":"Bob"}]' --content-type=application/json

# Mock a single resource
playwright-cli route "**/api/users/1" --body='{"id":1,"name":"Alice","email":"alice@example.com"}' --content-type=application/json

# Return empty array (no results scenario)
playwright-cli route "**/api/search*" --body='[]' --content-type=application/json
```

### Mock with Custom Headers

```bash
# Set CORS headers for testing
playwright-cli route "**/api/**" --body='{"ok":true}' --header="Access-Control-Allow-Origin: *" --header="X-Request-Id: mock-123"

# Set caching headers
playwright-cli route "**/static/**" --header="Cache-Control: max-age=3600"
```

### Remove Request Headers

Strip headers from outgoing requests — useful for testing unauthenticated access:

```bash
# Remove authentication headers
playwright-cli route "**/*" --remove-header=cookie,authorization

# Remove tracking headers
playwright-cli route "**/*" --remove-header=x-tracking-id
```

### Manage Active Routes

```bash
# See what's currently being intercepted
playwright-cli route-list

# Remove a specific route
playwright-cli unroute "**/*.jpg"

# Clear all routes
playwright-cli unroute
```

## Advanced Mocking with run-code

For conditional responses, request body inspection, response modification, or timed delays, use `run-code` to access the full Playwright route API.

### Conditional Response Based on Request Body

```bash
playwright-cli run-code "async page => {
  await page.route('**/api/login', route => {
    const body = route.request().postDataJSON();
    if (body.username === 'admin' && body.password === 'secret') {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ token: 'mock-jwt-token', user: { role: 'admin' } })
      });
    } else {
      route.fulfill({
        status: 401,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Invalid credentials' })
      });
    }
  });
}"
```

### Conditional Response Based on HTTP Method

```bash
playwright-cli run-code "async page => {
  await page.route('**/api/users', route => {
    const method = route.request().method();
    switch (method) {
      case 'GET':
        route.fulfill({
          contentType: 'application/json',
          body: JSON.stringify([{ id: 1, name: 'Alice' }])
        });
        break;
      case 'POST':
        route.fulfill({
          status: 201,
          contentType: 'application/json',
          body: JSON.stringify({ id: 2, name: 'New User' })
        });
        break;
      case 'DELETE':
        route.fulfill({ status: 204 });
        break;
      default:
        route.continue();
    }
  });
}"
```

### Modify a Real Response

Let the real request go through, then modify the response before the page sees it:

```bash
playwright-cli run-code "async page => {
  await page.route('**/api/user/profile', async route => {
    const response = await route.fetch();
    const json = await response.json();

    // Override specific fields
    json.isPremium = true;
    json.subscription = 'enterprise';

    await route.fulfill({ response, json });
  });
}"
```

### Add Headers to Real Response

```bash
playwright-cli run-code "async page => {
  await page.route('**/api/**', async route => {
    const response = await route.fetch();
    const headers = { ...response.headers(), 'x-mock': 'true' };
    await route.fulfill({ response, headers });
  });
}"
```

### Simulate Network Failures

```bash
# Internet disconnected
playwright-cli run-code "async page => {
  await page.route('**/api/offline', route => route.abort('internetdisconnected'));
}"

# Connection refused
playwright-cli run-code "async page => {
  await page.route('**/api/down', route => route.abort('connectionrefused'));
}"

# Timeout
playwright-cli run-code "async page => {
  await page.route('**/api/slow', route => route.abort('timedout'));
}"

# Connection reset
playwright-cli run-code "async page => {
  await page.route('**/api/reset', route => route.abort('connectionreset'));
}"
```

Available abort reasons: `connectionrefused`, `timedout`, `connectionreset`, `internetdisconnected`, `blockedbyclient`, `failed`

### Simulate Slow Responses (Latency)

```bash
playwright-cli run-code "async page => {
  await page.route('**/api/slow-endpoint', async route => {
    await new Promise(resolve => setTimeout(resolve, 3000));
    route.fulfill({
      contentType: 'application/json',
      body: JSON.stringify({ data: 'finally loaded' })
    });
  });
}"
```

### Mock with Response from File

```bash
playwright-cli run-code "async page => {
  const fs = require('fs');
  await page.route('**/api/config', route => {
    const body = fs.readFileSync('./fixtures/mock-config.json', 'utf8');
    route.fulfill({
      contentType: 'application/json',
      body
    });
  });
}"
```

### Request Counting and Verification

```bash
playwright-cli run-code "async page => {
  let apiCallCount = 0;
  await page.route('**/api/analytics', route => {
    apiCallCount++;
    route.continue();
  });

  // ... perform actions ...
  // Later, check count:
  return \`API was called \${apiCallCount} times\`;
}"
```

## Common Patterns

### Block Heavy Assets for Speed

```bash
# Block images, fonts, and stylesheets
playwright-cli route "**/*.{png,jpg,jpeg,gif,svg,webp}" --status=404
playwright-cli route "**/*.{woff,woff2,ttf,eot}" --status=404
playwright-cli route "**/*.css" --status=404
```

### Block Third-Party Scripts

```bash
# Block analytics and tracking
playwright-cli run-code "async page => {
  await page.route('**/*', route => {
    const url = route.request().url();
    const blocked = [
      'google-analytics.com',
      'googletagmanager.com',
      'facebook.net',
      'hotjar.com',
      'segment.io'
    ];
    if (blocked.some(domain => url.includes(domain))) {
      route.abort('blockedbyclient');
    } else {
      route.continue();
    }
  });
}"
```

### Mock GraphQL Requests

```bash
playwright-cli run-code "async page => {
  await page.route('**/graphql', route => {
    const { query } = route.request().postDataJSON();

    if (query.includes('GetUser')) {
      route.fulfill({
        contentType: 'application/json',
        body: JSON.stringify({
          data: { user: { id: '1', name: 'Alice', email: 'alice@example.com' } }
        })
      });
    } else if (query.includes('ListProducts')) {
      route.fulfill({
        contentType: 'application/json',
        body: JSON.stringify({
          data: { products: [{ id: '1', name: 'Widget', price: 9.99 }] }
        })
      });
    } else {
      route.continue();
    }
  });
}"
```

### HAR-Based Replay

Record real network traffic and replay it later — perfect for deterministic testing:

```bash
# Record all network traffic to a HAR file
playwright-cli run-code "async page => {
  await page.routeFromHAR('./recordings/api-traffic.har', {
    update: true,
    url: '**/api/**'
  });
  await page.goto('https://example.com');
  // Interact with the page — all matching requests are recorded
}"

# Later, replay from the HAR file (no real network needed)
playwright-cli run-code "async page => {
  await page.routeFromHAR('./recordings/api-traffic.har', {
    url: '**/api/**'
  });
  await page.goto('https://example.com');
  // API responses come from the HAR file
}"
```

### Mock WebSocket Messages

```bash
playwright-cli run-code "async page => {
  const ws = await page.waitForEvent('websocket');
  ws.on('framereceived', event => {
    console.log('WS received:', event.payload);
  });
  ws.on('framesent', event => {
    console.log('WS sent:', event.payload);
  });
}"
```

## Tips

- **Order matters**: Routes are evaluated in the order they were added. More specific patterns should be added before catch-all patterns.
- **`route.continue()`**: Lets the request proceed to the real server — use this in conditional routes for the "pass-through" case.
- **`route.fetch()`**: Makes the real request and returns the response, so you can inspect or modify it before fulfilling.
- **Performance**: Blocking images and third-party scripts can dramatically speed up page loads during automation.
- **Cleanup**: Always `unroute` when done, or routes persist for the entire session and may interfere with later operations.
