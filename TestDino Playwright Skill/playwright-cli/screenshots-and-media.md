# Screenshots and Media

> **When to use**: Capturing visual evidence of page state — screenshots for verification, video recordings for demos or debugging, PDF exports for documentation, viewport resizing for responsive testing.
> **Prerequisites**: [core-commands.md](core-commands.md) for basic CLI usage

## Quick Reference

```bash
# Screenshots
playwright-cli screenshot                         # Full page screenshot
playwright-cli screenshot e5                      # Element screenshot
playwright-cli screenshot --filename=checkout.png # Custom filename

# PDF
playwright-cli pdf --filename=report.pdf          # Save page as PDF

# Video
playwright-cli video-start                        # Start recording
playwright-cli video-stop demo.webm               # Stop and save

# Viewport
playwright-cli resize 1920 1080                   # Desktop
playwright-cli resize 375 812                     # Mobile
```

## Screenshots

### Page Screenshot

Capture the entire visible viewport:

```bash
# Auto-generated filename
playwright-cli screenshot

# Custom filename
playwright-cli screenshot --filename=homepage.png
playwright-cli screenshot --filename=screenshots/checkout-step3.png
```

### Element Screenshot

Capture a specific element only — useful for component-level verification:

```bash
# Screenshot a single element by ref
playwright-cli snapshot          # Get refs first
playwright-cli screenshot e5     # Capture just element e5

# With custom filename
playwright-cli screenshot e5 --filename=product-card.png
```

### Full-Page Screenshot

Capture the entire scrollable page, not just the viewport:

```bash
playwright-cli run-code "async page => {
  await page.screenshot({ path: 'full-page.png', fullPage: true });
  return 'Saved full-page screenshot';
}"
```

### Screenshot with Options

Use `run-code` for advanced screenshot options:

```bash
# Full page with quality settings (JPEG)
playwright-cli run-code "async page => {
  await page.screenshot({
    path: 'optimized.jpg',
    type: 'jpeg',
    quality: 80,
    fullPage: true
  });
}"

# Clip to specific region
playwright-cli run-code "async page => {
  await page.screenshot({
    path: 'header-region.png',
    clip: { x: 0, y: 0, width: 1280, height: 200 }
  });
}"

# With transparent background (for elements with transparency)
playwright-cli run-code "async page => {
  await page.screenshot({
    path: 'transparent.png',
    omitBackground: true
  });
}"

# Screenshot with mask (hide dynamic content)
playwright-cli run-code "async page => {
  await page.screenshot({
    path: 'masked.png',
    mask: [
      page.locator('.timestamp'),
      page.locator('.user-avatar'),
      page.locator('.ad-banner')
    ]
  });
}"

# Disable animations before screenshot
playwright-cli run-code "async page => {
  await page.evaluate(() => {
    document.querySelectorAll('*').forEach(el => {
      el.style.animation = 'none';
      el.style.transition = 'none';
    });
  });
  await page.screenshot({ path: 'no-animations.png' });
}"
```

### Element Screenshot with Options

```bash
playwright-cli run-code "async page => {
  const element = page.getByTestId('pricing-card');
  await element.screenshot({
    path: 'pricing-card.png',
    omitBackground: true
  });
}"
```

## Responsive Screenshots

Capture how the page looks at different viewport sizes:

```bash
# Desktop (1920x1080)
playwright-cli resize 1920 1080
playwright-cli screenshot --filename=desktop.png

# Laptop (1366x768)
playwright-cli resize 1366 768
playwright-cli screenshot --filename=laptop.png

# Tablet landscape (1024x768)
playwright-cli resize 1024 768
playwright-cli screenshot --filename=tablet-landscape.png

# Tablet portrait (768x1024)
playwright-cli resize 768 1024
playwright-cli screenshot --filename=tablet-portrait.png

# Mobile (375x812 — iPhone X)
playwright-cli resize 375 812
playwright-cli screenshot --filename=mobile.png

# Mobile small (320x568 — iPhone SE)
playwright-cli resize 320 568
playwright-cli screenshot --filename=mobile-small.png
```

### Automated Responsive Screenshots

```bash
playwright-cli run-code "async page => {
  const viewports = [
    { name: 'desktop', width: 1920, height: 1080 },
    { name: 'laptop', width: 1366, height: 768 },
    { name: 'tablet', width: 768, height: 1024 },
    { name: 'mobile', width: 375, height: 812 },
    { name: 'mobile-sm', width: 320, height: 568 }
  ];

  for (const vp of viewports) {
    await page.setViewportSize({ width: vp.width, height: vp.height });
    await page.waitForTimeout(500);  // Allow layout to settle
    await page.screenshot({ path: \`responsive-\${vp.name}.png\` });
  }
  return 'Captured ' + viewports.length + ' responsive screenshots';
}"
```

## PDF Export

Generate PDF documents from web pages — useful for reports, invoices, and documentation.

```bash
# Basic PDF
playwright-cli pdf --filename=page.pdf
```

### Advanced PDF Options

```bash
# PDF with custom options
playwright-cli run-code "async page => {
  await page.pdf({
    path: 'report.pdf',
    format: 'A4',
    printBackground: true,
    margin: { top: '1cm', right: '1cm', bottom: '1cm', left: '1cm' }
  });
  return 'PDF saved';
}"

# Letter format with header/footer
playwright-cli run-code "async page => {
  await page.pdf({
    path: 'document.pdf',
    format: 'Letter',
    printBackground: true,
    displayHeaderFooter: true,
    headerTemplate: '<div style=\"font-size:10px; text-align:center; width:100%;\">Company Report</div>',
    footerTemplate: '<div style=\"font-size:10px; text-align:center; width:100%;\">Page <span class=\"pageNumber\"></span> of <span class=\"totalPages\"></span></div>',
    margin: { top: '2cm', bottom: '2cm', left: '1cm', right: '1cm' }
  });
}"

# Landscape PDF
playwright-cli run-code "async page => {
  await page.pdf({
    path: 'landscape.pdf',
    landscape: true,
    format: 'A4',
    printBackground: true
  });
}"

# Specific pages only
playwright-cli run-code "async page => {
  await page.pdf({
    path: 'partial.pdf',
    pageRanges: '1-3',
    format: 'A4'
  });
}"
```

**Note**: PDF generation only works with Chromium-based browsers, not Firefox or WebKit.

### Print Stylesheet Preview

Before generating a PDF, switch to print media to see the print layout:

```bash
playwright-cli run-code "async page => {
  await page.emulateMedia({ media: 'print' });
}"
playwright-cli screenshot --filename=print-preview.png
playwright-cli pdf --filename=output.pdf
```

## Video Recording

Record browser sessions as WebM video files.

### Basic Recording

```bash
# Start recording
playwright-cli video-start

# Perform actions (everything is recorded)
playwright-cli open https://example.com
playwright-cli snapshot
playwright-cli click e1
playwright-cli fill e2 "test input"
playwright-cli click e5

# Stop and save
playwright-cli video-stop demo.webm
```

### Recording with Descriptive Names

```bash
playwright-cli video-start
# ... login flow ...
playwright-cli video-stop recordings/login-flow-2024-01-15.webm

playwright-cli video-start
# ... checkout flow ...
playwright-cli video-stop recordings/checkout-happy-path.webm
```

### Use Cases

| Scenario | Benefit |
|----------|---------|
| Bug reproduction | Share exact steps with developers |
| Demo creation | Show feature flows to stakeholders |
| Documentation | Record UI walkthroughs |
| QA evidence | Prove a test scenario was completed |
| Debugging | Watch what happened frame-by-frame |

## Viewport Management

Control the browser viewport for responsive testing:

```bash
# Common desktop sizes
playwright-cli resize 1920 1080    # Full HD
playwright-cli resize 1440 900     # MacBook Pro 15"
playwright-cli resize 1366 768     # Common laptop
playwright-cli resize 1280 720     # HD

# Tablet sizes
playwright-cli resize 1024 768     # iPad landscape
playwright-cli resize 768 1024     # iPad portrait
playwright-cli resize 834 1194     # iPad Pro 11"

# Mobile sizes
playwright-cli resize 430 932      # iPhone 14 Pro Max
playwright-cli resize 390 844      # iPhone 14
playwright-cli resize 375 812      # iPhone X/11/12/13
playwright-cli resize 360 800      # Galaxy S21
playwright-cli resize 320 568      # iPhone SE
```

## Common Patterns

### Before/After Comparison

```bash
# Before action
playwright-cli screenshot --filename=before.png
playwright-cli click e5
# After action
playwright-cli screenshot --filename=after.png
```

### Full Documentation Suite

```bash
playwright-cli open https://app.example.com

# Login page
playwright-cli screenshot --filename=docs/01-login.png

# Fill and submit
playwright-cli fill e1 "demo@example.com"
playwright-cli fill e2 "demo-password"
playwright-cli screenshot --filename=docs/02-login-filled.png

playwright-cli click e3
playwright-cli screenshot --filename=docs/03-dashboard.png

# Navigate to settings
playwright-cli goto https://app.example.com/settings
playwright-cli screenshot --filename=docs/04-settings.png

# Generate PDF of documentation page
playwright-cli goto https://app.example.com/docs
playwright-cli pdf --filename=docs/user-guide.pdf
```

### Dark Mode vs Light Mode Screenshots

```bash
playwright-cli open https://example.com

# Light mode
playwright-cli run-code "async page => { await page.emulateMedia({ colorScheme: 'light' }); }"
playwright-cli screenshot --filename=light-mode.png

# Dark mode
playwright-cli run-code "async page => { await page.emulateMedia({ colorScheme: 'dark' }); }"
playwright-cli screenshot --filename=dark-mode.png
```

### Cross-Browser Screenshot Comparison

```bash
#!/bin/bash
URL="https://example.com"

for browser in chrome firefox webkit; do
  playwright-cli -s=$browser open $URL --browser=$browser
  playwright-cli -s=$browser screenshot --filename="comparison-$browser.png"
done

playwright-cli close-all
```

## Tips

- **Always set viewport before screenshotting** — `resize` before `screenshot` for consistent dimensions
- **Use descriptive filenames** — `checkout-step3-error.png` not `screenshot-1.png`
- **Create output directories first** — `mkdir -p screenshots/` before using subdirectory paths
- **Full-page for long content** — use `fullPage: true` via `run-code` for scrollable pages
- **Mask dynamic content** — hide timestamps, avatars, and ads to get deterministic screenshots
- **Print media before PDF** — `emulateMedia({ media: 'print' })` to see what the PDF will look like
- **Video adds overhead** — only record when needed; tracing is lighter for debugging
