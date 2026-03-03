# File Upload and Download Recipes

> **When to use**: You need to test file uploads (single, multiple, drag-and-drop), file downloads (verify content, filename, type), upload progress, or file type restrictions.

---

## Recipe 1: Single File Upload via Input

### Complete Example

**TypeScript**

```typescript
import { test, expect } from '@playwright/test';
import path from 'path';

test('uploads a single file via file input', async ({ page }) => {
  await page.goto('/documents');

  // Click the upload button which triggers the hidden file input
  const fileInput = page.locator('input[type="file"]');

  // Upload a file from the test fixtures directory
  await fileInput.setInputFiles(path.resolve(__dirname, '../fixtures/report.pdf'));

  // Verify the file name appears in the UI
  await expect(page.getByText('report.pdf')).toBeVisible();

  // Click the submit/upload button
  await page.getByRole('button', { name: 'Upload' }).click();

  // Wait for the upload to complete
  await expect(page.getByRole('alert')).toContainText('File uploaded successfully');

  // Verify the file appears in the documents list
  await expect(page.getByRole('link', { name: 'report.pdf' })).toBeVisible();
});

test('uploads a file created in-memory (no fixture file needed)', async ({ page }) => {
  await page.goto('/documents');

  const fileInput = page.locator('input[type="file"]');

  // Create a file from a buffer -- no fixture file required
  await fileInput.setInputFiles({
    name: 'test-data.csv',
    mimeType: 'text/csv',
    buffer: Buffer.from('name,email,role\nJane,jane@example.com,admin\nBob,bob@example.com,user'),
  });

  await expect(page.getByText('test-data.csv')).toBeVisible();

  await page.getByRole('button', { name: 'Upload' }).click();

  await expect(page.getByRole('alert')).toContainText('File uploaded successfully');
});

test('clears a selected file before uploading', async ({ page }) => {
  await page.goto('/documents');

  const fileInput = page.locator('input[type="file"]');

  // Select a file
  await fileInput.setInputFiles({
    name: 'wrong-file.txt',
    mimeType: 'text/plain',
    buffer: Buffer.from('wrong content'),
  });

  await expect(page.getByText('wrong-file.txt')).toBeVisible();

  // Clear the selection
  await fileInput.setInputFiles([]);

  // Or click a "Remove" button in the UI
  // await page.getByRole('button', { name: 'Remove' }).click();

  await expect(page.getByText('wrong-file.txt')).not.toBeVisible();
});
```

**JavaScript**

```javascript
const { test, expect } = require('@playwright/test');
const path = require('path');

test('uploads a single file via file input', async ({ page }) => {
  await page.goto('/documents');

  const fileInput = page.locator('input[type="file"]');
  await fileInput.setInputFiles(path.resolve(__dirname, '../fixtures/report.pdf'));

  await expect(page.getByText('report.pdf')).toBeVisible();

  await page.getByRole('button', { name: 'Upload' }).click();

  await expect(page.getByRole('alert')).toContainText('File uploaded successfully');
  await expect(page.getByRole('link', { name: 'report.pdf' })).toBeVisible();
});

test('uploads a file created in-memory', async ({ page }) => {
  await page.goto('/documents');

  const fileInput = page.locator('input[type="file"]');

  await fileInput.setInputFiles({
    name: 'test-data.csv',
    mimeType: 'text/csv',
    buffer: Buffer.from('name,email,role\nJane,jane@example.com,admin'),
  });

  await expect(page.getByText('test-data.csv')).toBeVisible();
  await page.getByRole('button', { name: 'Upload' }).click();
  await expect(page.getByRole('alert')).toContainText('File uploaded successfully');
});
```

---

## Recipe 2: Multiple File Upload

### Complete Example

**TypeScript**

```typescript
import { test, expect } from '@playwright/test';
import path from 'path';

test('uploads multiple files at once', async ({ page }) => {
  await page.goto('/documents');

  const fileInput = page.locator('input[type="file"]');

  // Pass an array to upload multiple files
  await fileInput.setInputFiles([
    path.resolve(__dirname, '../fixtures/report.pdf'),
    path.resolve(__dirname, '../fixtures/photo.jpg'),
    path.resolve(__dirname, '../fixtures/data.csv'),
  ]);

  // Verify all file names appear
  await expect(page.getByText('report.pdf')).toBeVisible();
  await expect(page.getByText('photo.jpg')).toBeVisible();
  await expect(page.getByText('data.csv')).toBeVisible();

  // Verify the count indicator
  await expect(page.getByText('3 files selected')).toBeVisible();

  await page.getByRole('button', { name: 'Upload all' }).click();

  await expect(page.getByRole('alert')).toContainText('3 files uploaded');
});

test('uploads multiple files with in-memory buffers', async ({ page }) => {
  await page.goto('/documents');

  const fileInput = page.locator('input[type="file"]');

  await fileInput.setInputFiles([
    {
      name: 'notes.txt',
      mimeType: 'text/plain',
      buffer: Buffer.from('Meeting notes for Q4 planning'),
    },
    {
      name: 'config.json',
      mimeType: 'application/json',
      buffer: Buffer.from(JSON.stringify({ theme: 'dark', lang: 'en' })),
    },
  ]);

  await expect(page.getByText('notes.txt')).toBeVisible();
  await expect(page.getByText('config.json')).toBeVisible();

  await page.getByRole('button', { name: 'Upload all' }).click();
  await expect(page.getByRole('alert')).toContainText('2 files uploaded');
});

test('removes one file from a multi-file selection', async ({ page }) => {
  await page.goto('/documents');

  const fileInput = page.locator('input[type="file"]');

  await fileInput.setInputFiles([
    { name: 'keep.txt', mimeType: 'text/plain', buffer: Buffer.from('keep') },
    { name: 'remove.txt', mimeType: 'text/plain', buffer: Buffer.from('remove') },
    { name: 'also-keep.txt', mimeType: 'text/plain', buffer: Buffer.from('keep') },
  ]);

  // Remove a specific file from the preview list
  const removeItem = page.getByText('remove.txt').locator('..');
  await removeItem.getByRole('button', { name: /remove|delete|×/i }).click();

  await expect(page.getByText('remove.txt')).not.toBeVisible();
  await expect(page.getByText('keep.txt')).toBeVisible();
  await expect(page.getByText('also-keep.txt')).toBeVisible();
  await expect(page.getByText('2 files selected')).toBeVisible();
});
```

**JavaScript**

```javascript
const { test, expect } = require('@playwright/test');
const path = require('path');

test('uploads multiple files at once', async ({ page }) => {
  await page.goto('/documents');

  const fileInput = page.locator('input[type="file"]');

  await fileInput.setInputFiles([
    path.resolve(__dirname, '../fixtures/report.pdf'),
    path.resolve(__dirname, '../fixtures/photo.jpg'),
    path.resolve(__dirname, '../fixtures/data.csv'),
  ]);

  await expect(page.getByText('report.pdf')).toBeVisible();
  await expect(page.getByText('photo.jpg')).toBeVisible();
  await expect(page.getByText('data.csv')).toBeVisible();

  await page.getByRole('button', { name: 'Upload all' }).click();
  await expect(page.getByRole('alert')).toContainText('3 files uploaded');
});
```

---

## Recipe 3: Drag-and-Drop File Upload

### Complete Example

**TypeScript**

```typescript
import { test, expect } from '@playwright/test';
import path from 'path';

test('uploads a file via drag-and-drop zone', async ({ page }) => {
  await page.goto('/documents');

  const dropZone = page.locator('[data-testid="drop-zone"]');
  await expect(dropZone).toContainText(/drag.*here|drop.*files/i);

  // Drag-and-drop from the OS is not natively supported in Playwright,
  // but drop zones always have an underlying input[type=file] -- use that
  const fileInput = page.locator('input[type="file"]');

  await fileInput.setInputFiles(path.resolve(__dirname, '../fixtures/report.pdf'));

  // File preview should appear in the drop zone
  await expect(dropZone.getByText('report.pdf')).toBeVisible();

  // Trigger upload
  await page.getByRole('button', { name: 'Upload' }).click();

  await expect(page.getByRole('alert')).toContainText('uploaded successfully');
});

test('shows visual feedback during drag-over', async ({ page }) => {
  await page.goto('/documents');

  const dropZone = page.locator('[data-testid="drop-zone"]');

  // Simulate dragenter to show visual feedback
  await dropZone.dispatchEvent('dragenter', {
    dataTransfer: { types: ['Files'], files: [] },
  });

  // Drop zone should show an active state
  await expect(dropZone).toHaveClass(/active|highlight|drag-over/);
  await expect(dropZone).toContainText(/release|drop now/i);

  // Simulate dragleave to reset
  await dropZone.dispatchEvent('dragleave');

  await expect(dropZone).not.toHaveClass(/active|highlight|drag-over/);
});

test('handles multiple files dropped at once', async ({ page }) => {
  await page.goto('/documents');

  const fileInput = page.locator('input[type="file"]');

  await fileInput.setInputFiles([
    { name: 'image1.png', mimeType: 'image/png', buffer: Buffer.from('fake-png-1') },
    { name: 'image2.png', mimeType: 'image/png', buffer: Buffer.from('fake-png-2') },
    { name: 'image3.png', mimeType: 'image/png', buffer: Buffer.from('fake-png-3') },
  ]);

  await expect(page.getByText('image1.png')).toBeVisible();
  await expect(page.getByText('image2.png')).toBeVisible();
  await expect(page.getByText('image3.png')).toBeVisible();
});
```

**JavaScript**

```javascript
const { test, expect } = require('@playwright/test');
const path = require('path');

test('uploads a file via drag-and-drop zone', async ({ page }) => {
  await page.goto('/documents');

  const dropZone = page.locator('[data-testid="drop-zone"]');
  const fileInput = page.locator('input[type="file"]');

  await fileInput.setInputFiles(path.resolve(__dirname, '../fixtures/report.pdf'));

  await expect(dropZone.getByText('report.pdf')).toBeVisible();

  await page.getByRole('button', { name: 'Upload' }).click();
  await expect(page.getByRole('alert')).toContainText('uploaded successfully');
});
```

---

## Recipe 4: Download and Verify File Content

### Complete Example

**TypeScript**

```typescript
import { test, expect } from '@playwright/test';
import fs from 'fs';
import path from 'path';

test('downloads a file and verifies its content', async ({ page }) => {
  await page.goto('/documents');

  // Start waiting for the download event BEFORE clicking
  const downloadPromise = page.waitForEvent('download');

  await page.getByRole('link', { name: 'report.csv' }).click();

  const download = await downloadPromise;

  // Save to a temporary location
  const downloadPath = path.join(__dirname, '../downloads', download.suggestedFilename());
  await download.saveAs(downloadPath);

  // Read and verify the content
  const content = fs.readFileSync(downloadPath, 'utf-8');

  expect(content).toContain('name,email,role');
  expect(content).toContain('Jane,jane@example.com,admin');

  // Verify line count
  const lines = content.trim().split('\n');
  expect(lines.length).toBeGreaterThan(1); // header + at least one data row

  // Clean up
  fs.unlinkSync(downloadPath);
});

test('downloads a JSON file and verifies structure', async ({ page }) => {
  await page.goto('/api-docs');

  const downloadPromise = page.waitForEvent('download');
  await page.getByRole('button', { name: 'Export API spec' }).click();

  const download = await downloadPromise;
  const downloadPath = path.join(__dirname, '../downloads', download.suggestedFilename());
  await download.saveAs(downloadPath);

  const content = JSON.parse(fs.readFileSync(downloadPath, 'utf-8'));

  expect(content).toHaveProperty('openapi');
  expect(content.paths).toBeDefined();
  expect(Object.keys(content.paths).length).toBeGreaterThan(0);

  fs.unlinkSync(downloadPath);
});

test('downloads a file via the stream (no disk save needed)', async ({ page }) => {
  await page.goto('/documents');

  const downloadPromise = page.waitForEvent('download');
  await page.getByRole('link', { name: 'report.csv' }).click();

  const download = await downloadPromise;

  // Read directly from the download stream without saving to disk
  const readable = await download.createReadStream();
  const chunks: Buffer[] = [];

  for await (const chunk of readable!) {
    chunks.push(Buffer.from(chunk));
  }

  const content = Buffer.concat(chunks).toString('utf-8');
  expect(content).toContain('name,email,role');
});
```

**JavaScript**

```javascript
const { test, expect } = require('@playwright/test');
const fs = require('fs');
const path = require('path');

test('downloads a file and verifies its content', async ({ page }) => {
  await page.goto('/documents');

  const downloadPromise = page.waitForEvent('download');
  await page.getByRole('link', { name: 'report.csv' }).click();

  const download = await downloadPromise;

  const downloadPath = path.join(__dirname, '../downloads', download.suggestedFilename());
  await download.saveAs(downloadPath);

  const content = fs.readFileSync(downloadPath, 'utf-8');
  expect(content).toContain('name,email,role');
  expect(content).toContain('Jane,jane@example.com,admin');

  fs.unlinkSync(downloadPath);
});

test('downloads a file via the stream', async ({ page }) => {
  await page.goto('/documents');

  const downloadPromise = page.waitForEvent('download');
  await page.getByRole('link', { name: 'report.csv' }).click();

  const download = await downloadPromise;

  const readable = await download.createReadStream();
  const chunks = [];

  for await (const chunk of readable) {
    chunks.push(Buffer.from(chunk));
  }

  const content = Buffer.concat(chunks).toString('utf-8');
  expect(content).toContain('name,email,role');
});
```

---

## Recipe 5: Download and Verify Filename

### Complete Example

**TypeScript**

```typescript
import { test, expect } from '@playwright/test';

test('download has correct filename and extension', async ({ page }) => {
  await page.goto('/reports');

  const downloadPromise = page.waitForEvent('download');
  await page.getByRole('button', { name: 'Export as PDF' }).click();

  const download = await downloadPromise;

  // Verify filename pattern
  expect(download.suggestedFilename()).toMatch(/^report-\d{4}-\d{2}-\d{2}\.pdf$/);
});

test('download filename changes based on selected format', async ({ page }) => {
  await page.goto('/reports');

  // Select CSV format
  await page.getByLabel('Export format').selectOption('csv');

  const csvDownload = page.waitForEvent('download');
  await page.getByRole('button', { name: 'Download' }).click();
  const csv = await csvDownload;
  expect(csv.suggestedFilename()).toMatch(/\.csv$/);

  // Select Excel format
  await page.getByLabel('Export format').selectOption('xlsx');

  const xlsxDownload = page.waitForEvent('download');
  await page.getByRole('button', { name: 'Download' }).click();
  const xlsx = await xlsxDownload;
  expect(xlsx.suggestedFilename()).toMatch(/\.xlsx$/);
});

test('download has correct MIME type via response headers', async ({ page }) => {
  await page.goto('/reports');

  // Intercept the download request to check response headers
  const responsePromise = page.waitForResponse('**/api/reports/export**');
  const downloadPromise = page.waitForEvent('download');

  await page.getByRole('button', { name: 'Export as PDF' }).click();

  const response = await responsePromise;
  expect(response.headers()['content-type']).toContain('application/pdf');
  expect(response.headers()['content-disposition']).toContain('attachment');

  await downloadPromise; // Consume the download event
});

test('download failure shows error to user', async ({ page }) => {
  // Mock the download endpoint to fail
  await page.route('**/api/reports/export**', async (route) => {
    await route.fulfill({
      status: 500,
      contentType: 'application/json',
      body: JSON.stringify({ error: 'Report generation failed' }),
    });
  });

  await page.goto('/reports');
  await page.getByRole('button', { name: 'Export as PDF' }).click();

  await expect(page.getByRole('alert')).toContainText(/failed|error/i);
});
```

**JavaScript**

```javascript
const { test, expect } = require('@playwright/test');

test('download has correct filename and extension', async ({ page }) => {
  await page.goto('/reports');

  const downloadPromise = page.waitForEvent('download');
  await page.getByRole('button', { name: 'Export as PDF' }).click();

  const download = await downloadPromise;
  expect(download.suggestedFilename()).toMatch(/^report-\d{4}-\d{2}-\d{2}\.pdf$/);
});

test('download filename changes based on selected format', async ({ page }) => {
  await page.goto('/reports');

  await page.getByLabel('Export format').selectOption('csv');

  const csvDownload = page.waitForEvent('download');
  await page.getByRole('button', { name: 'Download' }).click();
  const csv = await csvDownload;
  expect(csv.suggestedFilename()).toMatch(/\.csv$/);
});
```

---

## Recipe 6: Large File Upload with Progress

### Complete Example

**TypeScript**

```typescript
import { test, expect } from '@playwright/test';

test('shows upload progress for a large file', async ({ page }) => {
  await page.goto('/documents');

  const fileInput = page.locator('input[type="file"]');

  // Create a large in-memory file (5 MB)
  const largeBuffer = Buffer.alloc(5 * 1024 * 1024, 'x');

  await fileInput.setInputFiles({
    name: 'large-dataset.bin',
    mimeType: 'application/octet-stream',
    buffer: largeBuffer,
  });

  await page.getByRole('button', { name: 'Upload' }).click();

  // Verify progress bar appears
  const progressBar = page.getByRole('progressbar');
  await expect(progressBar).toBeVisible();

  // Verify progress percentage updates
  // Use polling to check that progress increases
  await expect(async () => {
    const value = await progressBar.getAttribute('aria-valuenow');
    expect(Number(value)).toBeGreaterThan(0);
  }).toPass({ timeout: 10000 });

  // Wait for upload to complete
  await expect(progressBar).not.toBeVisible({ timeout: 60000 });
  await expect(page.getByRole('alert')).toContainText('uploaded successfully');
});

test('cancels an in-progress upload', async ({ page }) => {
  // Slow down the upload API to simulate a long upload
  await page.route('**/api/documents/upload', async (route) => {
    // Delay for 10 seconds to give us time to cancel
    await new Promise((resolve) => setTimeout(resolve, 10000));
    await route.continue();
  });

  await page.goto('/documents');

  const fileInput = page.locator('input[type="file"]');
  const largeBuffer = Buffer.alloc(5 * 1024 * 1024, 'x');

  await fileInput.setInputFiles({
    name: 'large-file.bin',
    mimeType: 'application/octet-stream',
    buffer: largeBuffer,
  });

  await page.getByRole('button', { name: 'Upload' }).click();

  // Wait for upload to start
  await expect(page.getByRole('progressbar')).toBeVisible();

  // Cancel the upload
  await page.getByRole('button', { name: 'Cancel upload' }).click();

  // Verify upload was cancelled
  await expect(page.getByRole('progressbar')).not.toBeVisible();
  await expect(page.getByText(/cancelled|aborted/i)).toBeVisible();

  // Verify the file did not appear in the documents list
  await expect(page.getByRole('link', { name: 'large-file.bin' })).not.toBeVisible();
});

test('retries a failed upload', async ({ page }) => {
  let attempt = 0;

  await page.route('**/api/documents/upload', async (route) => {
    attempt++;
    if (attempt === 1) {
      // First attempt fails
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Server error' }),
      });
    } else {
      // Second attempt succeeds
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ id: '123', name: 'data.csv' }),
      });
    }
  });

  await page.goto('/documents');

  const fileInput = page.locator('input[type="file"]');
  await fileInput.setInputFiles({
    name: 'data.csv',
    mimeType: 'text/csv',
    buffer: Buffer.from('col1,col2\nval1,val2'),
  });

  await page.getByRole('button', { name: 'Upload' }).click();

  // First attempt fails
  await expect(page.getByText(/upload failed|error/i)).toBeVisible();

  // Retry
  await page.getByRole('button', { name: /retry/i }).click();

  // Second attempt succeeds
  await expect(page.getByRole('alert')).toContainText('uploaded successfully');
  expect(attempt).toBe(2);
});
```

**JavaScript**

```javascript
const { test, expect } = require('@playwright/test');

test('shows upload progress for a large file', async ({ page }) => {
  await page.goto('/documents');

  const fileInput = page.locator('input[type="file"]');

  const largeBuffer = Buffer.alloc(5 * 1024 * 1024, 'x');

  await fileInput.setInputFiles({
    name: 'large-dataset.bin',
    mimeType: 'application/octet-stream',
    buffer: largeBuffer,
  });

  await page.getByRole('button', { name: 'Upload' }).click();

  const progressBar = page.getByRole('progressbar');
  await expect(progressBar).toBeVisible();

  await expect(progressBar).not.toBeVisible({ timeout: 60000 });
  await expect(page.getByRole('alert')).toContainText('uploaded successfully');
});

test('cancels an in-progress upload', async ({ page }) => {
  await page.route('**/api/documents/upload', async (route) => {
    await new Promise((resolve) => setTimeout(resolve, 10000));
    await route.continue();
  });

  await page.goto('/documents');

  const fileInput = page.locator('input[type="file"]');
  await fileInput.setInputFiles({
    name: 'large-file.bin',
    mimeType: 'application/octet-stream',
    buffer: Buffer.alloc(5 * 1024 * 1024, 'x'),
  });

  await page.getByRole('button', { name: 'Upload' }).click();
  await expect(page.getByRole('progressbar')).toBeVisible();

  await page.getByRole('button', { name: 'Cancel upload' }).click();

  await expect(page.getByRole('progressbar')).not.toBeVisible();
  await expect(page.getByText(/cancelled|aborted/i)).toBeVisible();
});
```

---

## Recipe 7: Testing File Type Restrictions

### Complete Example

**TypeScript**

```typescript
import { test, expect } from '@playwright/test';

test('accepts allowed file types', async ({ page }) => {
  await page.goto('/documents');

  const fileInput = page.locator('input[type="file"]');

  // Verify the accept attribute on the file input
  await expect(fileInput).toHaveAttribute('accept', /\.pdf|\.doc|\.docx|\.txt/);

  // Upload an allowed file type
  await fileInput.setInputFiles({
    name: 'valid-document.pdf',
    mimeType: 'application/pdf',
    buffer: Buffer.from('fake-pdf-content'),
  });

  // Should be accepted without error
  await expect(page.getByText('valid-document.pdf')).toBeVisible();
  await expect(page.getByText(/not allowed|invalid/i)).not.toBeVisible();
});

test('rejects disallowed file types with clear error message', async ({ page }) => {
  await page.goto('/documents');

  const fileInput = page.locator('input[type="file"]');

  // Upload a disallowed file type
  // Note: setInputFiles bypasses the browser's accept attribute filter,
  // so the app's JavaScript validation is what we are testing here
  await fileInput.setInputFiles({
    name: 'script.exe',
    mimeType: 'application/x-msdownload',
    buffer: Buffer.from('fake-exe-content'),
  });

  // App should show a rejection message
  await expect(page.getByRole('alert')).toContainText(
    /not allowed|unsupported file type|only .pdf, .doc/i
  );

  // File should not appear in the upload queue
  await expect(page.getByText('script.exe')).not.toBeVisible();
});

test('enforces maximum file size', async ({ page }) => {
  await page.goto('/documents');

  const fileInput = page.locator('input[type="file"]');

  // Create a file that exceeds the max size (e.g., 11 MB when limit is 10 MB)
  const oversizedBuffer = Buffer.alloc(11 * 1024 * 1024, 'x');

  await fileInput.setInputFiles({
    name: 'huge-file.pdf',
    mimeType: 'application/pdf',
    buffer: oversizedBuffer,
  });

  await expect(page.getByRole('alert')).toContainText(/file.*too large|exceeds.*10 ?MB/i);
  await expect(page.getByText('huge-file.pdf')).not.toBeVisible();
});

test('enforces maximum number of files', async ({ page }) => {
  await page.goto('/documents');

  const fileInput = page.locator('input[type="file"]');

  // Try to upload more files than the limit (e.g., limit is 5)
  const files = Array.from({ length: 6 }, (_, i) => ({
    name: `file-${i + 1}.txt`,
    mimeType: 'text/plain' as const,
    buffer: Buffer.from(`content ${i + 1}`),
  }));

  await fileInput.setInputFiles(files);

  await expect(page.getByRole('alert')).toContainText(/maximum.*5 files|too many files/i);
});

test('validates image dimensions for avatar upload', async ({ page }) => {
  await page.goto('/settings/profile');

  const fileInput = page.locator('input[type="file"]');

  // Create a tiny 1x1 PNG (valid format but too small)
  // Minimal PNG buffer
  const tinyPng = Buffer.from(
    'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==',
    'base64'
  );

  await fileInput.setInputFiles({
    name: 'tiny-avatar.png',
    mimeType: 'image/png',
    buffer: tinyPng,
  });

  await expect(page.getByRole('alert')).toContainText(/minimum.*dimensions|too small/i);
});
```

**JavaScript**

```javascript
const { test, expect } = require('@playwright/test');

test('rejects disallowed file types with clear error message', async ({ page }) => {
  await page.goto('/documents');

  const fileInput = page.locator('input[type="file"]');

  await fileInput.setInputFiles({
    name: 'script.exe',
    mimeType: 'application/x-msdownload',
    buffer: Buffer.from('fake-exe-content'),
  });

  await expect(page.getByRole('alert')).toContainText(
    /not allowed|unsupported file type|only .pdf, .doc/i
  );
  await expect(page.getByText('script.exe')).not.toBeVisible();
});

test('enforces maximum file size', async ({ page }) => {
  await page.goto('/documents');

  const fileInput = page.locator('input[type="file"]');

  const oversizedBuffer = Buffer.alloc(11 * 1024 * 1024, 'x');

  await fileInput.setInputFiles({
    name: 'huge-file.pdf',
    mimeType: 'application/pdf',
    buffer: oversizedBuffer,
  });

  await expect(page.getByRole('alert')).toContainText(/file.*too large|exceeds.*10 ?MB/i);
});

test('enforces maximum number of files', async ({ page }) => {
  await page.goto('/documents');

  const fileInput = page.locator('input[type="file"]');

  const files = Array.from({ length: 6 }, (_, i) => ({
    name: `file-${i + 1}.txt`,
    mimeType: 'text/plain',
    buffer: Buffer.from(`content ${i + 1}`),
  }));

  await fileInput.setInputFiles(files);

  await expect(page.getByRole('alert')).toContainText(/maximum.*5 files|too many files/i);
});
```

---

## Variations

### Upload via File Chooser Dialog

```typescript
test('uploads via the native file chooser dialog', async ({ page }) => {
  await page.goto('/documents');

  // Listen for the file chooser event before clicking the trigger
  const fileChooserPromise = page.waitForEvent('filechooser');
  await page.getByRole('button', { name: 'Choose file' }).click();

  const fileChooser = await fileChooserPromise;

  // Verify it accepts only certain types
  expect(fileChooser.isMultiple()).toBe(false);

  await fileChooser.setFiles({
    name: 'chosen-file.pdf',
    mimeType: 'application/pdf',
    buffer: Buffer.from('pdf-content'),
  });

  await expect(page.getByText('chosen-file.pdf')).toBeVisible();
});
```

### Upload with Image Preview

```typescript
test('shows image preview after selecting a file', async ({ page }) => {
  await page.goto('/settings/profile');

  const fileInput = page.locator('input[type="file"]');

  await fileInput.setInputFiles(path.resolve(__dirname, '../fixtures/avatar.jpg'));

  // Verify the image preview is displayed
  const preview = page.getByRole('img', { name: /preview|avatar/i });
  await expect(preview).toBeVisible();

  // Verify the preview src is a blob or data URL
  const src = await preview.getAttribute('src');
  expect(src).toMatch(/^(blob:|data:image)/);
});
```

### Download with Authentication

```typescript
test('downloads a file that requires authentication', async ({ page, request }) => {
  // Some downloads go through an API that needs auth cookies
  await page.goto('/documents');

  // The UI download works because the browser sends cookies
  const downloadPromise = page.waitForEvent('download');
  await page.getByRole('link', { name: 'confidential-report.pdf' }).click();

  const download = await downloadPromise;
  expect(download.suggestedFilename()).toBe('confidential-report.pdf');

  // Alternatively, verify via API request (which carries the auth context)
  const response = await request.get('/api/documents/123/download');
  expect(response.ok()).toBeTruthy();
  expect(response.headers()['content-type']).toContain('application/pdf');
});
```

---

## Tips

1. **Use `setInputFiles` for upload testing**. Even if the UI uses a drag-and-drop zone, there is always an underlying `input[type="file"]` element. Target it directly with `setInputFiles()` instead of trying to simulate OS-level drag events.

2. **Prefer in-memory buffers over fixture files**. Creating files with `Buffer.from()` keeps tests self-contained and eliminates dependencies on external fixture files. Use fixture files only when you need real file content (e.g., a valid PDF that your app parses).

3. **Always set up the download listener before clicking**. Call `page.waitForEvent('download')` before the click that triggers the download. If you click first, you may miss the event.

4. **Use `createReadStream()` to verify content without disk I/O**. The `download.createReadStream()` method lets you read file content directly in memory, which is faster and avoids cleanup of temporary files.

5. **Test the accept attribute AND the JavaScript validation separately**. The HTML `accept` attribute only filters the OS file dialog -- it does not prevent uploads via other means. Your app's JavaScript validation is the real gatekeeper, and `setInputFiles()` bypasses the `accept` filter, which is exactly what you want to test.

---

## Related

- [Playwright Upload Docs](https://playwright.dev/docs/input#upload-files)
- [Playwright Download Docs](https://playwright.dev/docs/downloads)
- `recipes/drag-and-drop.md` -- General drag and drop patterns
- `recipes/crud-testing.md` -- File uploads as part of resource creation
- `foundations/actions.md` -- Input interaction fundamentals
