# Advanced Workflows

> **When to use**: Complex multi-step automation scenarios — multi-page scraping, popup and new window handling, accessibility auditing, file downloads, authentication flows with OAuth, infinite scroll extraction, form wizard automation, and combining multiple CLI features together.
> **Prerequisites**: [core-commands.md](core-commands.md), [running-custom-code.md](running-custom-code.md), [session-management.md](session-management.md)

## Quick Reference

```bash
# Multi-page scraping
playwright-cli run-code "async page => {
  const data = [];
  for (let i = 1; i <= 5; i++) {
    await page.goto(\`https://example.com/page/\${i}\`);
    const items = await page.locator('.item').allTextContents();
    data.push(...items);
  }
  return data;
}"

# Handle popup window
playwright-cli run-code "async page => {
  const [popup] = await Promise.all([
    page.waitForEvent('popup'),
    page.click('a[target=_blank]')
  ]);
  return await popup.title();
}"

# Accessibility snapshot
playwright-cli run-code "async page => {
  return await page.accessibility.snapshot();
}"
```

## Popup and New Window Handling

When clicking links that open new windows or popups:

### Capture Popup Content

```bash
playwright-cli run-code "async page => {
  const [popup] = await Promise.all([
    page.waitForEvent('popup'),
    page.click('a[target=_blank]')
  ]);

  await popup.waitForLoadState();
  const title = await popup.title();
  const url = popup.url();

  return { title, url };
}"
```

### Interact with Popup

```bash
playwright-cli run-code "async page => {
  const [popup] = await Promise.all([
    page.waitForEvent('popup'),
    page.click('#open-settings')
  ]);

  // Fill a form in the popup
  await popup.fill('input[name=email]', 'user@example.com');
  await popup.click('button:text(\"Save\")');

  // Wait for popup to close
  await popup.waitForEvent('close');
  return 'Popup handled';
}"
```

### OAuth Login with Popup

```bash
playwright-cli run-code "async page => {
  await page.goto('https://app.example.com/login');

  const [popup] = await Promise.all([
    page.waitForEvent('popup'),
    page.click('button:text(\"Sign in with Google\")')
  ]);

  // Handle Google OAuth in the popup
  await popup.fill('input[type=email]', 'user@gmail.com');
  await popup.click('#identifierNext');
  await popup.waitForSelector('input[type=password]', { state: 'visible' });
  await popup.fill('input[type=password]', 'password');
  await popup.click('#passwordNext');

  // Popup closes after auth, main page redirects
  await popup.waitForEvent('close');
  await page.waitForURL('**/dashboard');

  return 'OAuth login complete: ' + page.url();
}"
```

## Multi-Page Navigation and Scraping

### Paginated Data Extraction

```bash
playwright-cli run-code "async page => {
  await page.goto('https://example.com/products');
  const allProducts = [];

  while (true) {
    // Extract data from current page
    const products = await page.locator('.product-card').evaluateAll(cards =>
      cards.map(card => ({
        name: card.querySelector('.name')?.textContent?.trim(),
        price: card.querySelector('.price')?.textContent?.trim(),
        rating: card.querySelector('.rating')?.getAttribute('data-score')
      }))
    );
    allProducts.push(...products);

    // Check for next page
    const nextBtn = page.locator('a.next-page');
    if (await nextBtn.isVisible()) {
      await nextBtn.click();
      await page.waitForLoadState('networkidle');
    } else {
      break;
    }
  }

  return { total: allProducts.length, products: allProducts };
}"
```

### Infinite Scroll Extraction

```bash
playwright-cli run-code "async page => {
  await page.goto('https://example.com/feed');
  const seen = new Set();
  const items = [];
  const maxItems = 100;

  while (items.length < maxItems) {
    // Collect visible items
    const newItems = await page.locator('.feed-item').evaluateAll(
      els => els.map(el => ({
        id: el.getAttribute('data-id'),
        text: el.textContent.trim()
      }))
    );

    for (const item of newItems) {
      if (item.id && !seen.has(item.id)) {
        seen.add(item.id);
        items.push(item);
      }
    }

    // Scroll to bottom
    const previousHeight = await page.evaluate(() => document.body.scrollHeight);
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    await page.waitForTimeout(2000);

    // Check if we've reached the end
    const newHeight = await page.evaluate(() => document.body.scrollHeight);
    if (newHeight === previousHeight) break;
  }

  return { collected: items.length, items: items.slice(0, maxItems) };
}"
```

### Multi-Site Data Aggregation

```bash
#!/bin/bash
# Use named sessions for concurrent site scraping

playwright-cli -s=site1 open https://news.example.com &
playwright-cli -s=site2 open https://blog.example.com &
playwright-cli -s=site3 open https://docs.example.com &
wait

# Extract headlines from each
playwright-cli -s=site1 run-code "async page => {
  return await page.locator('h2.headline').allTextContents();
}"

playwright-cli -s=site2 run-code "async page => {
  return await page.locator('.post-title').allTextContents();
}"

playwright-cli -s=site3 run-code "async page => {
  return await page.locator('.doc-title').allTextContents();
}"

playwright-cli close-all
```

## File Upload and Download

### Download Files

```bash
playwright-cli run-code "async page => {
  const [download] = await Promise.all([
    page.waitForEvent('download'),
    page.click('a.download-link')
  ]);

  const filename = download.suggestedFilename();
  await download.saveAs('./downloads/' + filename);
  return {
    filename,
    url: download.url()
  };
}"
```

### Download Multiple Files

```bash
playwright-cli run-code "async page => {
  const downloadLinks = await page.locator('a.download').all();
  const files = [];

  for (const link of downloadLinks) {
    const [download] = await Promise.all([
      page.waitForEvent('download'),
      link.click()
    ]);
    const name = download.suggestedFilename();
    await download.saveAs('./downloads/' + name);
    files.push(name);
  }

  return files;
}"
```

### Upload Files

```bash
# Simple upload via ref
playwright-cli snapshot
playwright-cli upload e5 ./document.pdf

# Upload multiple files
playwright-cli upload e5 ./photo1.jpg ./photo2.jpg ./photo3.jpg

# Programmatic upload (for hidden file inputs)
playwright-cli run-code "async page => {
  const fileInput = page.locator('input[type=file]');
  await fileInput.setInputFiles('./report.pdf');
}"

# Upload multiple files programmatically
playwright-cli run-code "async page => {
  const fileInput = page.locator('input[type=file]');
  await fileInput.setInputFiles([
    './document1.pdf',
    './document2.pdf',
    './image.png'
  ]);
}"

# Clear file input
playwright-cli run-code "async page => {
  await page.locator('input[type=file]').setInputFiles([]);
}"
```

### Drag-and-Drop File Upload

```bash
playwright-cli run-code "async page => {
  // Create a fake file for drag-and-drop zones
  const dataTransfer = await page.evaluateHandle(() => new DataTransfer());
  await page.dispatchEvent('.dropzone', 'drop', { dataTransfer });
}"
```

## Accessibility Auditing

### Accessibility Tree Snapshot

```bash
playwright-cli run-code "async page => {
  const snapshot = await page.accessibility.snapshot();
  return JSON.stringify(snapshot, null, 2);
}"
```

### Check for Missing ARIA Labels

```bash
playwright-cli run-code "async page => {
  return await page.evaluate(() => {
    const issues = [];

    // Images without alt text
    document.querySelectorAll('img:not([alt])').forEach(img => {
      issues.push({ type: 'img-no-alt', src: img.src.substring(0, 50) });
    });

    // Buttons without accessible names
    document.querySelectorAll('button').forEach(btn => {
      if (!btn.textContent.trim() && !btn.getAttribute('aria-label')) {
        issues.push({ type: 'button-no-name', html: btn.outerHTML.substring(0, 80) });
      }
    });

    // Form inputs without labels
    document.querySelectorAll('input:not([type=hidden])').forEach(input => {
      const id = input.id;
      const hasLabel = id && document.querySelector(\`label[for=\${id}]\`);
      const hasAriaLabel = input.getAttribute('aria-label') || input.getAttribute('aria-labelledby');
      if (!hasLabel && !hasAriaLabel) {
        issues.push({ type: 'input-no-label', name: input.name, type: input.type });
      }
    });

    // Links without text
    document.querySelectorAll('a').forEach(link => {
      if (!link.textContent.trim() && !link.getAttribute('aria-label')) {
        issues.push({ type: 'link-no-text', href: link.href.substring(0, 50) });
      }
    });

    return { issueCount: issues.length, issues };
  });
}"
```

### Color Contrast Check

```bash
playwright-cli run-code "async page => {
  return await page.evaluate(() => {
    const getContrast = (rgb1, rgb2) => {
      const luminance = (r, g, b) => {
        const [rs, gs, bs] = [r, g, b].map(c => {
          c = c / 255;
          return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
        });
        return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
      };
      const l1 = luminance(...rgb1);
      const l2 = luminance(...rgb2);
      const lighter = Math.max(l1, l2);
      const darker = Math.min(l1, l2);
      return (lighter + 0.05) / (darker + 0.05);
    };

    const parseRGB = (str) => {
      const match = str.match(/\d+/g);
      return match ? match.slice(0, 3).map(Number) : [0, 0, 0];
    };

    const lowContrast = [];
    document.querySelectorAll('p, span, a, button, label, h1, h2, h3, h4, h5, h6').forEach(el => {
      const style = window.getComputedStyle(el);
      const fg = parseRGB(style.color);
      const bg = parseRGB(style.backgroundColor);
      const ratio = getContrast(fg, bg);
      if (ratio < 4.5) {
        lowContrast.push({
          text: el.textContent.trim().substring(0, 30),
          ratio: ratio.toFixed(2),
          fg: style.color,
          bg: style.backgroundColor
        });
      }
    });

    return { lowContrastCount: lowContrast.length, elements: lowContrast.slice(0, 20) };
  });
}"
```

### Tab Order Verification

```bash
playwright-cli run-code "async page => {
  return await page.evaluate(() => {
    const focusable = Array.from(document.querySelectorAll(
      'a[href], button, input, select, textarea, [tabindex]:not([tabindex=\"-1\"])'
    ));
    return focusable.map((el, i) => ({
      order: i + 1,
      tag: el.tagName.toLowerCase(),
      text: (el.textContent || el.getAttribute('aria-label') || el.name || '').trim().substring(0, 40),
      tabIndex: el.tabIndex
    }));
  });
}"
```

## Form Wizard Automation

### Multi-Step Form

```bash
# Step 1: Personal Info
playwright-cli open https://example.com/apply
playwright-cli snapshot
playwright-cli fill e1 "Jane"              # First name
playwright-cli fill e2 "Doe"               # Last name
playwright-cli fill e3 "jane@example.com"  # Email
playwright-cli fill e4 "+1-555-0123"       # Phone
playwright-cli click e5                     # Next

# Step 2: Address
playwright-cli snapshot
playwright-cli fill e1 "123 Main Street"
playwright-cli fill e2 "Apt 4B"
playwright-cli fill e3 "Springfield"
playwright-cli select e4 "IL"
playwright-cli fill e5 "62701"
playwright-cli click e6                     # Next

# Step 3: Upload Documents
playwright-cli snapshot
playwright-cli upload e1 ./resume.pdf
playwright-cli upload e2 ./cover-letter.pdf
playwright-cli click e3                     # Next

# Step 4: Review and Submit
playwright-cli snapshot
playwright-cli screenshot --filename=review-page.png
playwright-cli check e1                     # Accept terms
playwright-cli click e2                     # Submit
playwright-cli snapshot                     # Confirmation page
```

### Dynamic Form with Conditional Fields

```bash
playwright-cli run-code "async page => {
  await page.goto('https://example.com/registration');

  // Select account type — this shows/hides fields
  await page.selectOption('#account-type', 'business');

  // Wait for business fields to appear
  await page.waitForSelector('#company-name', { state: 'visible' });

  // Fill business-specific fields
  await page.fill('#company-name', 'Acme Corp');
  await page.fill('#tax-id', '12-3456789');
  await page.fill('#company-size', '50-100');

  // Fill common fields
  await page.fill('#contact-name', 'Jane Doe');
  await page.fill('#contact-email', 'jane@acme.com');

  await page.click('button:text(\"Register\")');
  await page.waitForURL('**/welcome');

  return 'Registration complete';
}"
```

## Data Extraction Patterns

### Table Data Extraction

```bash
playwright-cli run-code "async page => {
  await page.goto('https://example.com/reports');

  const data = await page.evaluate(() => {
    const table = document.querySelector('table.data-table');
    const headers = Array.from(table.querySelectorAll('thead th'))
      .map(th => th.textContent.trim());
    const rows = Array.from(table.querySelectorAll('tbody tr'))
      .map(tr => {
        const cells = Array.from(tr.querySelectorAll('td'))
          .map(td => td.textContent.trim());
        return Object.fromEntries(headers.map((h, i) => [h, cells[i]]));
      });
    return { headers, rowCount: rows.length, rows };
  });

  return JSON.stringify(data, null, 2);
}"
```

### Extract Structured Data (JSON-LD, Meta Tags)

```bash
playwright-cli run-code "async page => {
  return await page.evaluate(() => {
    // JSON-LD structured data
    const jsonLd = Array.from(document.querySelectorAll('script[type=\"application/ld+json\"]'))
      .map(s => JSON.parse(s.textContent));

    // Open Graph meta tags
    const og = {};
    document.querySelectorAll('meta[property^=\"og:\"]').forEach(m => {
      og[m.getAttribute('property')] = m.content;
    });

    // Standard meta tags
    const meta = {};
    document.querySelectorAll('meta[name]').forEach(m => {
      meta[m.name] = m.content;
    });

    return { jsonLd, openGraph: og, meta };
  });
}"
```

### Screenshot Every Link Target

```bash
playwright-cli run-code "async page => {
  await page.goto('https://example.com');
  const links = await page.locator('nav a').evaluateAll(
    anchors => anchors.map(a => ({ text: a.textContent.trim(), href: a.href }))
  );

  for (const link of links) {
    const safeName = link.text.toLowerCase().replace(/[^a-z0-9]/g, '-');
    await page.goto(link.href);
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: \`screenshots/\${safeName}.png\` });
  }

  return links.map(l => l.text);
}"
```

## Error Recovery Patterns

### Retry on Failure

```bash
playwright-cli run-code "async page => {
  const maxRetries = 3;
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      await page.goto('https://flaky-site.example.com', { timeout: 15000 });
      await page.waitForSelector('.content', { timeout: 5000 });
      return 'Success on attempt ' + attempt;
    } catch (error) {
      if (attempt === maxRetries) throw error;
      console.log(\`Attempt \${attempt} failed, retrying...\`);
      await page.waitForTimeout(2000 * attempt); // Exponential backoff
    }
  }
}"
```

### Dismiss Cookie Banners Automatically

```bash
playwright-cli run-code "async page => {
  // Try common cookie consent selectors
  const selectors = [
    'button:text(\"Accept\")',
    'button:text(\"Accept All\")',
    'button:text(\"Accept Cookies\")',
    'button:text(\"I Agree\")',
    '#cookie-accept',
    '.cookie-consent-accept',
    '[data-testid=cookie-accept]'
  ];

  for (const sel of selectors) {
    try {
      const btn = page.locator(sel).first();
      if (await btn.isVisible({ timeout: 1000 })) {
        await btn.click();
        return 'Dismissed cookie banner with: ' + sel;
      }
    } catch (e) {
      // Try next selector
    }
  }
  return 'No cookie banner found';
}"
```

### Handle Unexpected Dialogs

```bash
# Set up auto-dismiss for any dialogs
playwright-cli run-code "async page => {
  page.on('dialog', async dialog => {
    console.log(\`Auto-handled \${dialog.type()} dialog: \${dialog.message()}\`);
    await dialog.dismiss();
  });
}"
```

## Combining CLI Features

### Full E2E Test Workflow

```bash
#!/bin/bash
set -e

# 1. Start fresh session
playwright-cli open https://app.example.com --persistent

# 2. Set up monitoring
playwright-cli run-code "async page => {
  page.on('console', msg => {
    if (msg.type() === 'error') console.log('[ERROR]', msg.text());
  });
}"

# 3. Start tracing
playwright-cli tracing-start

# 4. Log in
playwright-cli goto https://app.example.com/login
playwright-cli snapshot
playwright-cli fill e1 "test@example.com"
playwright-cli fill e2 "password123"
playwright-cli click e3
playwright-cli state-save auth-state.json

# 5. Verify dashboard
playwright-cli snapshot
playwright-cli screenshot --filename=dashboard.png

# 6. Test a feature
playwright-cli click e5    # Navigate to feature
playwright-cli snapshot
playwright-cli fill e1 "test data"
playwright-cli click e3    # Submit
playwright-cli screenshot --filename=feature-result.png

# 7. Stop tracing and clean up
playwright-cli tracing-stop
playwright-cli close

echo "Test complete. Check screenshots/ and traces/"
```

### Comparison Testing Script

```bash
#!/bin/bash
# Compare two environments

STAGING="https://staging.example.com"
PROD="https://www.example.com"
PAGES=("/" "/pricing" "/about" "/features")

for path in "${PAGES[@]}"; do
  safePath=$(echo "$path" | tr '/' '-' | sed 's/^-//')
  [ -z "$safePath" ] && safePath="home"

  playwright-cli -s=staging open "${STAGING}${path}"
  playwright-cli -s=staging screenshot --filename="compare-staging-${safePath}.png"

  playwright-cli -s=prod open "${PROD}${path}"
  playwright-cli -s=prod screenshot --filename="compare-prod-${safePath}.png"
done

playwright-cli close-all
echo "Screenshots saved. Compare staging vs prod visually."
```

## Tips

- **Start simple, add complexity** — begin with basic CLI commands, drop into `run-code` only when needed
- **Save state checkpoints** — `state-save checkpoint.json` at key points so you can restore if something goes wrong
- **Use named sessions for isolation** — never mix concerns in a single session
- **Monitor console and network** — set up listeners early to catch errors as they happen
- **Trace complex flows** — always trace when debugging multi-step workflows
- **Error recovery is essential** — websites are flaky; build retry logic into complex scripts
- **Clean up resources** — `close-all` at the end of every script; `kill-all` if things go wrong
