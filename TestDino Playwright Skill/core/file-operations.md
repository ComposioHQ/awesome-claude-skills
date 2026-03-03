# File Operations

> **When to use**: Testing file uploads, downloads, drag-and-drop file interactions, file type validation, and download verification.
> **Prerequisites**: [core/locators.md](locators.md), [core/assertions-and-waiting.md](assertions-and-waiting.md)

## Quick Reference

```typescript
// Upload — single file
await page.getByLabel('Upload').setInputFiles('fixtures/resume.pdf');

// Upload — multiple files
await page.getByLabel('Upload').setInputFiles(['fixtures/a.png', 'fixtures/b.png']);

// Upload — clear selection
await page.getByLabel('Upload').setInputFiles([]);

// Download — wait and save
const download = await page.waitForEvent('download');
await page.getByRole('button', { name: 'Export CSV' }).click();
const path = await download.path();           // temp path
await download.saveAs('test-results/export.csv'); // permanent path

// File chooser dialog — non-input uploads
const fileChooser = await page.waitForEvent('filechooser');
await page.getByRole('button', { name: 'Choose file' }).click();
await fileChooser.setFiles('fixtures/photo.jpg');
```

## Patterns

### Single File Upload

**Use when**: A form has a standard `<input type="file">` element.
**Avoid when**: The upload uses a drag-and-drop zone with no underlying file input.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';
import path from 'path';

test('upload a single document', async ({ page }) => {
  await page.goto('/settings/profile');

  const filePath = path.join(__dirname, '../fixtures/avatar.png');
  await page.getByLabel('Profile picture').setInputFiles(filePath);

  // Verify the file name appears in the UI
  await expect(page.getByText('avatar.png')).toBeVisible();

  await page.getByRole('button', { name: 'Save' }).click();
  await expect(page.getByText('Profile updated')).toBeVisible();
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');
const path = require('path');

test('upload a single document', async ({ page }) => {
  await page.goto('/settings/profile');

  const filePath = path.join(__dirname, '../fixtures/avatar.png');
  await page.getByLabel('Profile picture').setInputFiles(filePath);

  await expect(page.getByText('avatar.png')).toBeVisible();

  await page.getByRole('button', { name: 'Save' }).click();
  await expect(page.getByText('Profile updated')).toBeVisible();
});
```

### Multiple File Upload

**Use when**: The file input accepts `multiple` and you need to attach several files at once.
**Avoid when**: The UI only allows one file. Use single file upload.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';
import path from 'path';

test('upload multiple attachments', async ({ page }) => {
  await page.goto('/tickets/new');

  const fixtures = ['doc1.pdf', 'doc2.pdf', 'screenshot.png'].map(
    (f) => path.join(__dirname, '../fixtures', f)
  );

  await page.getByLabel('Attachments').setInputFiles(fixtures);

  // Verify all files are listed
  await expect(page.getByTestId('file-list').getByRole('listitem')).toHaveCount(3);

  // Remove one file by clearing and re-setting
  await page.getByLabel('Attachments').setInputFiles(fixtures.slice(0, 2));
  await expect(page.getByTestId('file-list').getByRole('listitem')).toHaveCount(2);
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');
const path = require('path');

test('upload multiple attachments', async ({ page }) => {
  await page.goto('/tickets/new');

  const fixtures = ['doc1.pdf', 'doc2.pdf', 'screenshot.png'].map(
    (f) => path.join(__dirname, '../fixtures', f)
  );

  await page.getByLabel('Attachments').setInputFiles(fixtures);
  await expect(page.getByTestId('file-list').getByRole('listitem')).toHaveCount(3);

  await page.getByLabel('Attachments').setInputFiles(fixtures.slice(0, 2));
  await expect(page.getByTestId('file-list').getByRole('listitem')).toHaveCount(2);
});
```

### File Chooser Dialog

**Use when**: The upload is triggered by a button click that opens the native file picker, not by a visible `<input type="file">`. Common with drag-and-drop libraries and custom upload components.
**Avoid when**: There is a visible `<input type="file">` — use `setInputFiles` directly.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('upload via file chooser dialog', async ({ page }) => {
  await page.goto('/documents');

  // Register the listener BEFORE the click that opens the dialog
  const fileChooserPromise = page.waitForEvent('filechooser');
  await page.getByRole('button', { name: 'Upload document' }).click();
  const fileChooser = await fileChooserPromise;

  // Verify dialog properties
  expect(fileChooser.isMultiple()).toBe(false);

  await fileChooser.setFiles('fixtures/report.pdf');
  await expect(page.getByText('report.pdf')).toBeVisible();
});

test('upload multiple via file chooser', async ({ page }) => {
  await page.goto('/gallery');

  const fileChooserPromise = page.waitForEvent('filechooser');
  await page.getByRole('button', { name: 'Add photos' }).click();
  const fileChooser = await fileChooserPromise;

  expect(fileChooser.isMultiple()).toBe(true);
  await fileChooser.setFiles(['fixtures/photo1.jpg', 'fixtures/photo2.jpg']);

  await expect(page.getByRole('img')).toHaveCount(2);
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('upload via file chooser dialog', async ({ page }) => {
  await page.goto('/documents');

  const fileChooserPromise = page.waitForEvent('filechooser');
  await page.getByRole('button', { name: 'Upload document' }).click();
  const fileChooser = await fileChooserPromise;

  expect(fileChooser.isMultiple()).toBe(false);

  await fileChooser.setFiles('fixtures/report.pdf');
  await expect(page.getByText('report.pdf')).toBeVisible();
});

test('upload multiple via file chooser', async ({ page }) => {
  await page.goto('/gallery');

  const fileChooserPromise = page.waitForEvent('filechooser');
  await page.getByRole('button', { name: 'Add photos' }).click();
  const fileChooser = await fileChooserPromise;

  expect(fileChooser.isMultiple()).toBe(true);
  await fileChooser.setFiles(['fixtures/photo1.jpg', 'fixtures/photo2.jpg']);

  await expect(page.getByRole('img')).toHaveCount(2);
});
```

### Drag-and-Drop File Upload

**Use when**: The UI has a drop zone that accepts files via the HTML5 Drag and Drop API and has no `<input type="file">` fallback.
**Avoid when**: A file input exists — even hidden ones work with `setInputFiles`.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';
import fs from 'fs';
import path from 'path';

test('drop file onto upload zone', async ({ page }) => {
  await page.goto('/upload');

  // Read the file into a buffer
  const filePath = path.join(__dirname, '../fixtures/data.csv');
  const buffer = fs.readFileSync(filePath);

  // Create a DataTransfer with the file and dispatch drop event
  const dropZone = page.getByTestId('drop-zone');

  await dropZone.dispatchEvent('drop', {
    dataTransfer: {
      files: [
        { name: 'data.csv', mimeType: 'text/csv', buffer },
      ],
    },
  });

  await expect(page.getByText('data.csv')).toBeVisible();
  await expect(page.getByText('Upload complete')).toBeVisible();
});

test('drag-and-drop with hidden input fallback', async ({ page }) => {
  await page.goto('/upload');

  // Many drag-and-drop libraries still use a hidden <input type="file">
  // Check for it first — this is more reliable than simulating DnD events
  const hiddenInput = page.locator('input[type="file"]');

  if (await hiddenInput.count() > 0) {
    await hiddenInput.setInputFiles('fixtures/data.csv');
  }

  await expect(page.getByText('data.csv')).toBeVisible();
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');
const fs = require('fs');
const path = require('path');

test('drop file onto upload zone', async ({ page }) => {
  await page.goto('/upload');

  const filePath = path.join(__dirname, '../fixtures/data.csv');
  const buffer = fs.readFileSync(filePath);

  const dropZone = page.getByTestId('drop-zone');

  await dropZone.dispatchEvent('drop', {
    dataTransfer: {
      files: [
        { name: 'data.csv', mimeType: 'text/csv', buffer },
      ],
    },
  });

  await expect(page.getByText('data.csv')).toBeVisible();
  await expect(page.getByText('Upload complete')).toBeVisible();
});

test('drag-and-drop with hidden input fallback', async ({ page }) => {
  await page.goto('/upload');

  const hiddenInput = page.locator('input[type="file"]');

  if (await hiddenInput.count() > 0) {
    await hiddenInput.setInputFiles('fixtures/data.csv');
  }

  await expect(page.getByText('data.csv')).toBeVisible();
});
```

### File Download — Wait and Verify

**Use when**: Testing export buttons, report generation, or any action that triggers a browser download.
**Avoid when**: The file is served as a page navigation (opens in a new tab). Use multi-tab patterns instead.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';
import fs from 'fs';

test('download and verify file content', async ({ page }) => {
  await page.goto('/reports');

  // Register BEFORE the click that triggers the download
  const downloadPromise = page.waitForEvent('download');
  await page.getByRole('button', { name: 'Export CSV' }).click();
  const download = await downloadPromise;

  // Verify download metadata
  expect(download.suggestedFilename()).toBe('report-2025.csv');

  // Save to a known location
  const savePath = 'test-results/report.csv';
  await download.saveAs(savePath);

  // Read and verify content
  const content = fs.readFileSync(savePath, 'utf-8');
  expect(content).toContain('Name,Email,Status');
  expect(content).toContain('Jane Doe,jane@example.com,Active');

  // Verify file size is reasonable
  const stats = fs.statSync(savePath);
  expect(stats.size).toBeGreaterThan(100);
});

test('download triggered by a link', async ({ page }) => {
  await page.goto('/files');

  const downloadPromise = page.waitForEvent('download');
  await page.getByRole('link', { name: 'Download invoice' }).click();
  const download = await downloadPromise;

  expect(download.suggestedFilename()).toMatch(/invoice-\d+\.pdf/);

  // Use download.path() for the temp file path
  const tempPath = await download.path();
  expect(tempPath).toBeTruthy();
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');
const fs = require('fs');

test('download and verify file content', async ({ page }) => {
  await page.goto('/reports');

  const downloadPromise = page.waitForEvent('download');
  await page.getByRole('button', { name: 'Export CSV' }).click();
  const download = await downloadPromise;

  expect(download.suggestedFilename()).toBe('report-2025.csv');

  const savePath = 'test-results/report.csv';
  await download.saveAs(savePath);

  const content = fs.readFileSync(savePath, 'utf-8');
  expect(content).toContain('Name,Email,Status');
  expect(content).toContain('Jane Doe,jane@example.com,Active');

  const stats = fs.statSync(savePath);
  expect(stats.size).toBeGreaterThan(100);
});

test('download triggered by a link', async ({ page }) => {
  await page.goto('/files');

  const downloadPromise = page.waitForEvent('download');
  await page.getByRole('link', { name: 'Download invoice' }).click();
  const download = await downloadPromise;

  expect(download.suggestedFilename()).toMatch(/invoice-\d+\.pdf/);

  const tempPath = await download.path();
  expect(tempPath).toBeTruthy();
});
```

### Configuring Download Paths

**Use when**: You need downloads to go to a specific directory, or you need to disable the download dialog prompt.
**Avoid when**: Default temp paths via `download.path()` or `download.saveAs()` are sufficient.

**TypeScript**
```typescript
// playwright.config.ts — global download behavior
import { defineConfig } from '@playwright/test';

export default defineConfig({
  use: {
    // Accept all downloads without prompting
    acceptDownloads: true, // default is true
  },
});
```

```typescript
import { test, expect } from '@playwright/test';
import fs from 'fs';
import path from 'path';

// Per-test download directory via a custom fixture
const downloadTest = test.extend<{ downloadDir: string }>({
  downloadDir: async ({}, use, testInfo) => {
    const dir = path.join('test-results', 'downloads', testInfo.title.replace(/\s+/g, '-'));
    fs.mkdirSync(dir, { recursive: true });
    await use(dir);
  },
});

downloadTest('save downloads to organized directories', async ({ page, downloadDir }) => {
  await page.goto('/exports');

  const downloadPromise = page.waitForEvent('download');
  await page.getByRole('button', { name: 'Export' }).click();
  const download = await downloadPromise;

  const savePath = path.join(downloadDir, download.suggestedFilename());
  await download.saveAs(savePath);

  expect(fs.existsSync(savePath)).toBe(true);
});
```

**JavaScript**
```javascript
// playwright.config.js
const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  use: {
    acceptDownloads: true,
  },
});
```

```javascript
const { test, expect } = require('@playwright/test');
const fs = require('fs');
const path = require('path');

const downloadTest = test.extend({
  downloadDir: async ({}, use, testInfo) => {
    const dir = path.join('test-results', 'downloads', testInfo.title.replace(/\s+/g, '-'));
    fs.mkdirSync(dir, { recursive: true });
    await use(dir);
  },
});

downloadTest('save downloads to organized directories', async ({ page, downloadDir }) => {
  await page.goto('/exports');

  const downloadPromise = page.waitForEvent('download');
  await page.getByRole('button', { name: 'Export' }).click();
  const download = await downloadPromise;

  const savePath = path.join(downloadDir, download.suggestedFilename());
  await download.saveAs(savePath);

  expect(fs.existsSync(savePath)).toBe(true);
});
```

### File Type Validation

**Use when**: Testing that the application rejects invalid file types and accepts valid ones.
**Avoid when**: The application does no client-side validation and relies entirely on server-side checks (test via API instead).

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('rejects unsupported file types', async ({ page }) => {
  await page.goto('/upload');

  // Upload an invalid file type
  await page.getByLabel('Upload image').setInputFiles({
    name: 'malware.exe',
    mimeType: 'application/octet-stream',
    buffer: Buffer.from('fake-exe-content'),
  });

  await expect(page.getByText('Only JPG, PNG, and GIF files are allowed')).toBeVisible();
  await expect(page.getByRole('button', { name: 'Submit' })).toBeDisabled();
});

test('accepts valid file types', async ({ page }) => {
  await page.goto('/upload');

  await page.getByLabel('Upload image').setInputFiles({
    name: 'photo.jpg',
    mimeType: 'image/jpeg',
    buffer: Buffer.from('fake-jpg-content'),
  });

  await expect(page.getByText('photo.jpg')).toBeVisible();
  await expect(page.getByRole('button', { name: 'Submit' })).toBeEnabled();
});

test('validates file size limits', async ({ page }) => {
  await page.goto('/upload');

  // Create a buffer that exceeds the 5MB limit
  const largeBuffer = Buffer.alloc(6 * 1024 * 1024, 'x');

  await page.getByLabel('Upload document').setInputFiles({
    name: 'huge-file.pdf',
    mimeType: 'application/pdf',
    buffer: largeBuffer,
  });

  await expect(page.getByText('File size must be under 5MB')).toBeVisible();
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('rejects unsupported file types', async ({ page }) => {
  await page.goto('/upload');

  await page.getByLabel('Upload image').setInputFiles({
    name: 'malware.exe',
    mimeType: 'application/octet-stream',
    buffer: Buffer.from('fake-exe-content'),
  });

  await expect(page.getByText('Only JPG, PNG, and GIF files are allowed')).toBeVisible();
  await expect(page.getByRole('button', { name: 'Submit' })).toBeDisabled();
});

test('accepts valid file types', async ({ page }) => {
  await page.goto('/upload');

  await page.getByLabel('Upload image').setInputFiles({
    name: 'photo.jpg',
    mimeType: 'image/jpeg',
    buffer: Buffer.from('fake-jpg-content'),
  });

  await expect(page.getByText('photo.jpg')).toBeVisible();
  await expect(page.getByRole('button', { name: 'Submit' })).toBeEnabled();
});

test('validates file size limits', async ({ page }) => {
  await page.goto('/upload');

  const largeBuffer = Buffer.alloc(6 * 1024 * 1024, 'x');

  await page.getByLabel('Upload document').setInputFiles({
    name: 'huge-file.pdf',
    mimeType: 'application/pdf',
    buffer: largeBuffer,
  });

  await expect(page.getByText('File size must be under 5MB')).toBeVisible();
});
```

### Large File Handling

**Use when**: Testing uploads or downloads of large files where timeouts and progress indicators matter.
**Avoid when**: Every test. Large file tests are slow. Run them in a separate suite or tag them for nightly runs.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';
import fs from 'fs';
import path from 'path';

test.describe('large file operations', () => {
  // Increase timeout for the entire describe block
  test.slow(); // Triples the default timeout

  test('upload large file with progress tracking', async ({ page }) => {
    await page.goto('/upload');

    // Create a test file on disk (avoid Buffer.alloc for very large files)
    const largePath = path.join('test-results', 'large-test-file.bin');
    const stream = fs.createWriteStream(largePath);
    for (let i = 0; i < 100; i++) {
      stream.write(Buffer.alloc(1024 * 1024, 'a')); // 100MB total
    }
    stream.end();
    await new Promise((resolve) => stream.on('finish', resolve));

    await page.getByLabel('Upload file').setInputFiles(largePath);

    // Wait for progress indicator
    await expect(page.getByRole('progressbar')).toBeVisible();

    // Wait for completion — extended timeout
    await expect(page.getByText('Upload complete')).toBeVisible({ timeout: 120_000 });

    // Cleanup
    fs.unlinkSync(largePath);
  });

  test('download large file', async ({ page }) => {
    await page.goto('/exports');

    const downloadPromise = page.waitForEvent('download');
    await page.getByRole('button', { name: 'Export full dataset' }).click();
    const download = await downloadPromise;

    const savePath = 'test-results/large-export.zip';
    await download.saveAs(savePath);

    // Verify file size is reasonable (at least 10MB)
    const stats = fs.statSync(savePath);
    expect(stats.size).toBeGreaterThan(10 * 1024 * 1024);

    fs.unlinkSync(savePath);
  });
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');
const fs = require('fs');
const path = require('path');

test.describe('large file operations', () => {
  test.slow();

  test('upload large file with progress tracking', async ({ page }) => {
    await page.goto('/upload');

    const largePath = path.join('test-results', 'large-test-file.bin');
    const stream = fs.createWriteStream(largePath);
    for (let i = 0; i < 100; i++) {
      stream.write(Buffer.alloc(1024 * 1024, 'a'));
    }
    stream.end();
    await new Promise((resolve) => stream.on('finish', resolve));

    await page.getByLabel('Upload file').setInputFiles(largePath);

    await expect(page.getByRole('progressbar')).toBeVisible();
    await expect(page.getByText('Upload complete')).toBeVisible({ timeout: 120_000 });

    fs.unlinkSync(largePath);
  });

  test('download large file', async ({ page }) => {
    await page.goto('/exports');

    const downloadPromise = page.waitForEvent('download');
    await page.getByRole('button', { name: 'Export full dataset' }).click();
    const download = await downloadPromise;

    const savePath = 'test-results/large-export.zip';
    await download.saveAs(savePath);

    const stats = fs.statSync(savePath);
    expect(stats.size).toBeGreaterThan(10 * 1024 * 1024);

    fs.unlinkSync(savePath);
  });
});
```

## Decision Guide

| Scenario | Approach | Key API |
|---|---|---|
| Standard `<input type="file">` | `setInputFiles()` on the locator | `locator.setInputFiles(path)` |
| Hidden file input | Find the input even if hidden, call `setInputFiles()` | `page.locator('input[type="file"]').setInputFiles()` |
| Custom button opens file picker | Listen for `filechooser` event before clicking | `page.waitForEvent('filechooser')` |
| Drag-and-drop zone with no input | Dispatch `drop` event with `DataTransfer` | `locator.dispatchEvent('drop', ...)` |
| DnD zone with hidden input fallback | Prefer `setInputFiles()` on the hidden input | Check `input[type="file"]` count first |
| Multiple files at once | Pass array to `setInputFiles()` | `setInputFiles([path1, path2])` |
| In-memory test file (no disk) | Pass object with `name`, `mimeType`, `buffer` | `setInputFiles({ name, mimeType, buffer })` |
| Download — verify filename | `download.suggestedFilename()` | `page.waitForEvent('download')` |
| Download — verify content | `download.saveAs()` then read with `fs` | `fs.readFileSync()` |
| Download — temp file only | `download.path()` returns temp location | Auto-deleted after test |
| Large file upload/download | Use `test.slow()`, increase assertion timeouts | `{ timeout: 120_000 }` |

## Anti-Patterns

| Don't Do This | Problem | Do This Instead |
|---|---|---|
| `await page.waitForTimeout(3000)` after upload | Arbitrary delay; flaky | `await expect(page.getByText('Upload complete')).toBeVisible()` |
| `await page.setInputFiles('#file', path)` using CSS selector | Fragile selector; breaks on ID changes | `await page.getByLabel('Upload').setInputFiles(path)` |
| Clicking download then immediately reading the file | Race condition; file may not be written yet | Use `page.waitForEvent('download')` then `download.saveAs()` |
| Creating large test files in `beforeAll` and never cleaning up | Fills disk in CI, slows down subsequent runs | Clean up in `afterAll` or use fixture teardown |
| Using `page.on('filechooser')` for every upload | Unnecessary complexity when `<input type="file">` exists | Use `setInputFiles()` directly |
| Hardcoding absolute file paths | Breaks across machines and CI | Use `path.join(__dirname, ...)` or relative to project root |
| Testing file upload with empty buffer | Does not test real validation behavior | Use realistic file content or minimum valid file size |
| Using `download.path()` for permanent storage | Temp files are cleaned up after test context closes | Use `download.saveAs()` for permanent paths |
| Uploading real 100MB files in every test run | Slows entire suite, wastes CI resources | Tag large file tests separately; run on schedule, not every PR |

## Troubleshooting

### "FileChooser event was not emitted"

**Cause**: The click did not open a native file picker dialog. The upload component may use a different mechanism.

```typescript
// Debug: check if there is a hidden <input type="file"> you can target directly
const fileInputCount = await page.locator('input[type="file"]').count();
console.log(`Found ${fileInputCount} file inputs`);

// If input exists, skip the file chooser approach entirely
if (fileInputCount > 0) {
  await page.locator('input[type="file"]').setInputFiles('fixtures/file.pdf');
}
```

### "Download event was not emitted"

**Cause**: The link opens in a new tab or navigates to the file URL instead of triggering a download.

```typescript
// Fix 1: Ensure acceptDownloads is true in config
// Fix 2: Check if the link opens a new tab — handle it as a new page
const pagePromise = page.context().waitForEvent('page');
await page.getByRole('link', { name: 'Download' }).click();
const newPage = await pagePromise;
// Then wait for the download event on the new page
const download = await newPage.waitForEvent('download');
```

### Upload works locally but fails in CI

**Cause**: File paths are wrong in CI, or the fixture files are not included in the repo/build.

```typescript
// Fix: always resolve paths relative to the test file
import path from 'path';
const fixturePath = path.join(__dirname, '..', 'fixtures', 'test-file.pdf');

// Verify the file exists before uploading
import fs from 'fs';
if (!fs.existsSync(fixturePath)) {
  throw new Error(`Fixture file missing: ${fixturePath}`);
}
```

### `setInputFiles` does nothing — no file appears

**Cause**: The input element is detached, inside a Shadow DOM, or in an iframe.

```typescript
// Check for iframe
const frame = page.frameLocator('iframe[title="Upload"]');
await frame.locator('input[type="file"]').setInputFiles('fixtures/file.pdf');

// Check for Shadow DOM — Playwright pierces open shadow roots automatically
// but the input may be in a closed shadow root (rare). Use the file chooser approach instead.
```

## Related

- [core/locators.md](locators.md) -- locator strategies for finding upload/download elements
- [core/assertions-and-waiting.md](assertions-and-waiting.md) -- assertion patterns for verifying upload/download results
- [core/fixtures-and-hooks.md](fixtures-and-hooks.md) -- creating reusable download directory fixtures
- [core/network-mocking.md](network-mocking.md) -- mocking upload endpoints for faster tests
- [core/error-and-edge-cases.md](error-and-edge-cases.md) -- testing upload failure states and error handling
