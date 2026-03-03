# Running Custom Playwright Code

> **When to use**: When CLI commands aren't sufficient — geolocation, permissions, media emulation, waiting strategies, iframe interaction, file downloads, clipboard access, complex multi-step workflows, or any scenario requiring the full Playwright API.
> **Prerequisites**: [core-commands.md](core-commands.md) for basic CLI usage

## Quick Reference

```bash
# Syntax: run-code accepts an async function with page as argument
playwright-cli run-code "async page => {
  // Full Playwright API available here
  // page.context() for browser context operations
  // Return a value to see it in output
  return await page.title();
}"
```

## Geolocation

Override the browser's reported location — essential for testing location-based features like store locators, delivery zones, and weather apps.

```bash
# Grant permission and set location to New York
playwright-cli run-code "async page => {
  await page.context().grantPermissions(['geolocation']);
  await page.context().setGeolocation({ latitude: 40.7128, longitude: -74.0060 });
}"

# London
playwright-cli run-code "async page => {
  await page.context().grantPermissions(['geolocation']);
  await page.context().setGeolocation({ latitude: 51.5074, longitude: -0.1278 });
}"

# San Francisco
playwright-cli run-code "async page => {
  await page.context().grantPermissions(['geolocation']);
  await page.context().setGeolocation({ latitude: 37.7749, longitude: -122.4194 });
}"

# Tokyo
playwright-cli run-code "async page => {
  await page.context().grantPermissions(['geolocation']);
  await page.context().setGeolocation({ latitude: 35.6762, longitude: 139.6503 });
}"

# Update location mid-session (simulates user moving)
playwright-cli run-code "async page => {
  await page.context().setGeolocation({ latitude: 34.0522, longitude: -118.2437 });
}"

# Clear geolocation override
playwright-cli run-code "async page => {
  await page.context().clearPermissions();
}"
```

## Permissions

Control browser permission grants — notifications, camera, microphone, clipboard, etc.

```bash
# Grant multiple permissions
playwright-cli run-code "async page => {
  await page.context().grantPermissions([
    'geolocation',
    'notifications',
    'camera',
    'microphone'
  ]);
}"

# Grant permissions for a specific origin only
playwright-cli run-code "async page => {
  await page.context().grantPermissions(['clipboard-read', 'clipboard-write'], {
    origin: 'https://example.com'
  });
}"

# Revoke all permissions
playwright-cli run-code "async page => {
  await page.context().clearPermissions();
}"
```

Available permissions: `geolocation`, `notifications`, `camera`, `microphone`, `clipboard-read`, `clipboard-write`, `payment-handler`, `midi`, `midi-sysex`, `ambient-light-sensor`, `accelerometer`, `gyroscope`, `magnetometer`, `accessibility-events`, `background-sync`

## Media Emulation

Test how your app behaves under different media conditions — dark mode, reduced motion, print layout.

### Color Scheme

```bash
# Dark mode
playwright-cli run-code "async page => {
  await page.emulateMedia({ colorScheme: 'dark' });
}"

# Light mode
playwright-cli run-code "async page => {
  await page.emulateMedia({ colorScheme: 'light' });
}"

# System preference (no override)
playwright-cli run-code "async page => {
  await page.emulateMedia({ colorScheme: 'no-preference' });
}"
```

### Reduced Motion

```bash
# Simulate prefers-reduced-motion: reduce
playwright-cli run-code "async page => {
  await page.emulateMedia({ reducedMotion: 'reduce' });
}"

# Reset to no preference
playwright-cli run-code "async page => {
  await page.emulateMedia({ reducedMotion: 'no-preference' });
}"
```

### Forced Colors (High Contrast)

```bash
playwright-cli run-code "async page => {
  await page.emulateMedia({ forcedColors: 'active' });
}"
```

### Print Media

```bash
# Emulate print stylesheet (useful before taking PDF)
playwright-cli run-code "async page => {
  await page.emulateMedia({ media: 'print' });
}"

# Reset to screen
playwright-cli run-code "async page => {
  await page.emulateMedia({ media: 'screen' });
}"
```

### Combine Multiple Emulations

```bash
playwright-cli run-code "async page => {
  await page.emulateMedia({
    colorScheme: 'dark',
    reducedMotion: 'reduce',
    forcedColors: 'none'
  });
}"
```

## Locale and Timezone

Override browser locale and timezone to test internationalization:

```bash
# Set locale (affects number formatting, date display, etc.)
playwright-cli run-code "async page => {
  // Locale is set at context creation; for existing context, use evaluate
  return await page.evaluate(() => navigator.language);
}"

# For new contexts, set locale and timezone at open time:
# playwright-cli open --config=locale-config.json
# where locale-config.json contains: { "locale": "de-DE", "timezoneId": "Europe/Berlin" }
```

## Wait Strategies

When the page needs time to load, render, or settle after an action.

### Wait for Load States

```bash
# Wait for all network requests to finish
playwright-cli run-code "async page => {
  await page.waitForLoadState('networkidle');
}"

# Wait for DOM content loaded
playwright-cli run-code "async page => {
  await page.waitForLoadState('domcontentloaded');
}"

# Wait for full load (including images, stylesheets)
playwright-cli run-code "async page => {
  await page.waitForLoadState('load');
}"
```

### Wait for Elements

```bash
# Wait for a loading spinner to disappear
playwright-cli run-code "async page => {
  await page.waitForSelector('.loading-spinner', { state: 'hidden' });
}"

# Wait for content to appear
playwright-cli run-code "async page => {
  await page.waitForSelector('.search-results', { state: 'visible', timeout: 10000 });
}"

# Wait for element to be removed from DOM entirely
playwright-cli run-code "async page => {
  await page.waitForSelector('.skeleton-loader', { state: 'detached' });
}"
```

### Wait for URL Changes

```bash
playwright-cli run-code "async page => {
  await page.waitForURL('**/dashboard');
}"

playwright-cli run-code "async page => {
  await page.waitForURL(/.*\/order\/\d+/);
}"
```

### Wait for Custom Conditions

```bash
# Wait for a JavaScript variable to be set
playwright-cli run-code "async page => {
  await page.waitForFunction(() => window.appReady === true);
}"

# Wait for specific number of elements
playwright-cli run-code "async page => {
  await page.waitForFunction(() => document.querySelectorAll('.item').length >= 10);
}"

# Wait with polling
playwright-cli run-code "async page => {
  await page.waitForFunction(
    () => document.querySelector('.status')?.textContent === 'Complete',
    { polling: 500, timeout: 30000 }
  );
}"
```

### Wait for Network Requests

```bash
# Wait for a specific API call to complete
playwright-cli run-code "async page => {
  const responsePromise = page.waitForResponse('**/api/users');
  await page.click('button#load-users');
  const response = await responsePromise;
  return { status: response.status(), url: response.url() };
}"

# Wait for a request to be made
playwright-cli run-code "async page => {
  const requestPromise = page.waitForRequest('**/api/submit');
  await page.click('button#submit');
  const request = await requestPromise;
  return request.postDataJSON();
}"
```

## Frames and Iframes

Interact with content inside iframes:

```bash
# Click a button inside an iframe
playwright-cli run-code "async page => {
  const frame = page.locator('iframe#my-iframe').contentFrame();
  await frame.locator('button.submit').click();
}"

# Fill a form inside an iframe
playwright-cli run-code "async page => {
  const frame = page.locator('iframe[name=\"checkout\"]').contentFrame();
  await frame.locator('input[name=\"card-number\"]').fill('4111111111111111');
  await frame.locator('input[name=\"expiry\"]').fill('12/25');
  await frame.locator('input[name=\"cvc\"]').fill('123');
}"

# Get all frame URLs
playwright-cli run-code "async page => {
  const frames = page.frames();
  return frames.map(f => ({ name: f.name(), url: f.url() }));
}"

# Nested iframes
playwright-cli run-code "async page => {
  const outerFrame = page.locator('iframe#outer').contentFrame();
  const innerFrame = outerFrame.locator('iframe#inner').contentFrame();
  await innerFrame.locator('button').click();
}"
```

## File Downloads

```bash
# Trigger download and save the file
playwright-cli run-code "async page => {
  const [download] = await Promise.all([
    page.waitForEvent('download'),
    page.click('a.download-link')
  ]);
  const filename = download.suggestedFilename();
  await download.saveAs('./downloads/' + filename);
  return 'Downloaded: ' + filename;
}"

# Download with custom path
playwright-cli run-code "async page => {
  const [download] = await Promise.all([
    page.waitForEvent('download'),
    page.getByRole('button', { name: 'Export CSV' }).click()
  ]);
  await download.saveAs('/tmp/export.csv');
  return 'Saved to /tmp/export.csv';
}"

# Get download URL without saving
playwright-cli run-code "async page => {
  const [download] = await Promise.all([
    page.waitForEvent('download'),
    page.click('#download-btn')
  ]);
  return download.url();
}"
```

## Clipboard

```bash
# Read clipboard content
playwright-cli run-code "async page => {
  await page.context().grantPermissions(['clipboard-read']);
  return await page.evaluate(() => navigator.clipboard.readText());
}"

# Write to clipboard
playwright-cli run-code "async page => {
  await page.evaluate(text => navigator.clipboard.writeText(text), 'Hello clipboard!');
}"

# Copy text from an element to clipboard
playwright-cli run-code "async page => {
  const text = await page.locator('.api-key').textContent();
  await page.evaluate(t => navigator.clipboard.writeText(t), text);
  return 'Copied: ' + text;
}"
```

## Page Information

```bash
# Page title
playwright-cli run-code "async page => {
  return await page.title();
}"

# Current URL
playwright-cli run-code "async page => {
  return page.url();
}"

# Full page HTML content
playwright-cli run-code "async page => {
  return await page.content();
}"

# Viewport size
playwright-cli run-code "async page => {
  return page.viewportSize();
}"

# Browser information
playwright-cli run-code "async page => {
  return await page.evaluate(() => ({
    userAgent: navigator.userAgent,
    language: navigator.language,
    languages: navigator.languages,
    cookiesEnabled: navigator.cookieEnabled,
    onLine: navigator.onLine,
    platform: navigator.platform,
    screenSize: { width: screen.width, height: screen.height }
  }));
}"
```

## JavaScript Execution

```bash
# Execute and return result
playwright-cli run-code "async page => {
  return await page.evaluate(() => {
    return {
      title: document.title,
      url: window.location.href,
      elementCount: document.querySelectorAll('*').length,
      scripts: document.querySelectorAll('script').length
    };
  });
}"

# Pass arguments to evaluate
playwright-cli run-code "async page => {
  const selector = '.product-card';
  const count = await page.evaluate(
    sel => document.querySelectorAll(sel).length,
    selector
  );
  return count + ' products found';
}"

# Modify the DOM
playwright-cli run-code "async page => {
  await page.evaluate(() => {
    document.querySelector('.banner')?.remove();
    document.body.style.zoom = '80%';
  });
}"
```

## Error Handling

```bash
# Try-catch for optional elements
playwright-cli run-code "async page => {
  try {
    await page.click('.cookie-consent-accept', { timeout: 2000 });
    return 'Cookie banner dismissed';
  } catch (e) {
    return 'No cookie banner found';
  }
}"

# Retry pattern
playwright-cli run-code "async page => {
  for (let attempt = 1; attempt <= 3; attempt++) {
    try {
      await page.click('.flaky-button', { timeout: 3000 });
      return 'Clicked on attempt ' + attempt;
    } catch (e) {
      if (attempt === 3) throw e;
      await page.waitForTimeout(1000);
    }
  }
}"
```

## Complex Workflows

### Login and Save Authentication State

```bash
playwright-cli run-code "async page => {
  await page.goto('https://example.com/login');
  await page.fill('input[name=email]', 'user@example.com');
  await page.fill('input[name=password]', 'secret');
  await page.click('button[type=submit]');
  await page.waitForURL('**/dashboard');
  await page.context().storageState({ path: 'auth.json' });
  return 'Login successful, state saved to auth.json';
}"
```

### Scrape Data from Multiple Pages

```bash
playwright-cli run-code "async page => {
  const results = [];
  for (let i = 1; i <= 5; i++) {
    await page.goto(\`https://example.com/products?page=\${i}\`);
    await page.waitForSelector('.product-card');
    const items = await page.locator('.product-card').evaluateAll(cards =>
      cards.map(card => ({
        name: card.querySelector('.title')?.textContent?.trim(),
        price: card.querySelector('.price')?.textContent?.trim(),
        rating: card.querySelector('.rating')?.getAttribute('data-value')
      }))
    );
    results.push(...items);
  }
  return JSON.stringify(results, null, 2);
}"
```

### Fill Multi-Step Form (Wizard)

```bash
playwright-cli run-code "async page => {
  // Step 1: Personal info
  await page.fill('#firstName', 'Jane');
  await page.fill('#lastName', 'Doe');
  await page.fill('#email', 'jane@example.com');
  await page.click('button:text(\"Next\")');

  // Step 2: Address
  await page.waitForSelector('#street');
  await page.fill('#street', '123 Main St');
  await page.fill('#city', 'Springfield');
  await page.selectOption('#state', 'IL');
  await page.fill('#zip', '62701');
  await page.click('button:text(\"Next\")');

  // Step 3: Confirm and submit
  await page.waitForSelector('.review-summary');
  await page.click('button:text(\"Submit\")');
  await page.waitForURL('**/confirmation');

  return 'Form submitted successfully';
}"
```

### Infinite Scroll Data Extraction

```bash
playwright-cli run-code "async page => {
  await page.goto('https://example.com/feed');
  const items = [];

  while (items.length < 50) {
    const newItems = await page.locator('.feed-item').evaluateAll(
      els => els.map(el => el.textContent.trim())
    );
    items.push(...newItems.filter(item => !items.includes(item)));

    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    await page.waitForTimeout(1000);

    // Check if we've reached the end
    const hasMore = await page.locator('.load-more').isVisible().catch(() => false);
    if (!hasMore && newItems.length === items.length) break;
  }

  return items.slice(0, 50);
}"
```

## Tips

- **Return values**: Always `return` data from `run-code` to see it in the CLI output
- **`page.context()`**: Access browser context for permissions, cookies, storage, geolocation
- **Error messages**: Playwright errors include element snapshots and call logs — read them carefully
- **Combine with CLI**: Use `run-code` for setup (permissions, routes) then CLI commands for interaction
- **Async/await**: All Playwright operations are async — always `await` them
