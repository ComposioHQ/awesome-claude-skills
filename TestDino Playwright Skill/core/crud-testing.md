# CRUD Testing Recipes

> **When to use**: You need to test create, read, update, or delete operations on any resource -- forms, tables, lists, cards, inline edits, or bulk actions.

---

## Recipe 1: Creating a Resource (Fill Form, Submit, Verify)

### Complete Example

**TypeScript**

```typescript
import { test, expect } from '@playwright/test';

test('creates a new product via form', async ({ page }) => {
  await page.goto('/products');

  // Click the create button
  await page.getByRole('button', { name: 'Add product' }).click();

  // Fill out the creation form
  await page.getByLabel('Product name').fill('Wireless Keyboard');
  await page.getByLabel('SKU').fill('KB-WIRELESS-001');
  await page.getByLabel('Price').fill('79.99');
  await page.getByLabel('Description').fill('Ergonomic wireless keyboard with backlit keys');
  await page.getByLabel('Category').selectOption('Electronics');
  await page.getByLabel('In stock').check();

  // Submit
  await page.getByRole('button', { name: 'Save product' }).click();

  // Verify success notification
  await expect(page.getByRole('alert')).toContainText('Product created successfully');

  // Verify the new item appears in the list
  await expect(page.getByRole('row', { name: /Wireless Keyboard/ })).toBeVisible();
  await expect(page.getByRole('row', { name: /Wireless Keyboard/ })).toContainText('$79.99');
  await expect(page.getByRole('row', { name: /Wireless Keyboard/ })).toContainText('KB-WIRELESS-001');
});

test('shows validation errors for invalid form data', async ({ page }) => {
  await page.goto('/products');
  await page.getByRole('button', { name: 'Add product' }).click();

  // Submit empty form
  await page.getByRole('button', { name: 'Save product' }).click();

  // Verify field-level validation messages
  await expect(page.getByText('Product name is required')).toBeVisible();
  await expect(page.getByText('Price is required')).toBeVisible();

  // Fill in invalid data
  await page.getByLabel('Product name').fill('A'); // too short
  await page.getByLabel('Price').fill('-5');

  await page.getByRole('button', { name: 'Save product' }).click();

  await expect(page.getByText('Name must be at least 3 characters')).toBeVisible();
  await expect(page.getByText('Price must be a positive number')).toBeVisible();
});

test('prevents duplicate resource creation', async ({ page }) => {
  await page.goto('/products');
  await page.getByRole('button', { name: 'Add product' }).click();

  // Try to create a product with a SKU that already exists
  await page.getByLabel('Product name').fill('Duplicate Product');
  await page.getByLabel('SKU').fill('EXISTING-SKU-001');
  await page.getByLabel('Price').fill('29.99');
  await page.getByRole('button', { name: 'Save product' }).click();

  await expect(page.getByRole('alert')).toContainText(/already exists|duplicate/i);
});
```

**JavaScript**

```javascript
const { test, expect } = require('@playwright/test');

test('creates a new product via form', async ({ page }) => {
  await page.goto('/products');

  await page.getByRole('button', { name: 'Add product' }).click();

  await page.getByLabel('Product name').fill('Wireless Keyboard');
  await page.getByLabel('SKU').fill('KB-WIRELESS-001');
  await page.getByLabel('Price').fill('79.99');
  await page.getByLabel('Description').fill('Ergonomic wireless keyboard with backlit keys');
  await page.getByLabel('Category').selectOption('Electronics');
  await page.getByLabel('In stock').check();

  await page.getByRole('button', { name: 'Save product' }).click();

  await expect(page.getByRole('alert')).toContainText('Product created successfully');
  await expect(page.getByRole('row', { name: /Wireless Keyboard/ })).toBeVisible();
  await expect(page.getByRole('row', { name: /Wireless Keyboard/ })).toContainText('$79.99');
});
```

---

## Recipe 2: Reading / Listing Resources (Table, Cards, Pagination)

### Complete Example

**TypeScript**

```typescript
import { test, expect } from '@playwright/test';

test.describe('reading resources in a table', () => {
  test('displays resources in a table with correct columns', async ({ page }) => {
    await page.goto('/products');

    // Verify table headers
    const headers = page.getByRole('columnheader');
    await expect(headers).toContainText(['Name', 'SKU', 'Price', 'Category', 'Status']);

    // Verify at least one row of data exists
    const rows = page.getByRole('row').filter({ hasNot: page.getByRole('columnheader') });
    await expect(rows.first()).toBeVisible();

    // Verify specific data in a row
    const firstRow = rows.first();
    await expect(firstRow.getByRole('cell').nth(0)).not.toBeEmpty();
    await expect(firstRow.getByRole('cell').nth(2)).toContainText('$');
  });

  test('sorts table by column', async ({ page }) => {
    await page.goto('/products');

    // Click the Price header to sort
    await page.getByRole('columnheader', { name: 'Price' }).click();

    // Get all prices from the table
    const priceCells = page.getByRole('row')
      .filter({ hasNot: page.getByRole('columnheader') })
      .getByRole('cell')
      .nth(2);

    const prices = await priceCells.allTextContents();
    const numericPrices = prices.map((p) => parseFloat(p.replace(/[$,]/g, '')));

    // Verify sorted ascending
    for (let i = 1; i < numericPrices.length; i++) {
      expect(numericPrices[i]).toBeGreaterThanOrEqual(numericPrices[i - 1]);
    }

    // Click again for descending
    await page.getByRole('columnheader', { name: 'Price' }).click();

    const pricesDesc = await priceCells.allTextContents();
    const numericDesc = pricesDesc.map((p) => parseFloat(p.replace(/[$,]/g, '')));

    for (let i = 1; i < numericDesc.length; i++) {
      expect(numericDesc[i]).toBeLessThanOrEqual(numericDesc[i - 1]);
    }
  });

  test('paginates through results', async ({ page }) => {
    await page.goto('/products');

    // Verify pagination controls are visible
    const pagination = page.getByRole('navigation', { name: /pagination/i });
    await expect(pagination).toBeVisible();

    // Get first page content
    const firstPageFirstRow = await page
      .getByRole('row')
      .filter({ hasNot: page.getByRole('columnheader') })
      .first()
      .textContent();

    // Go to page 2
    await pagination.getByRole('button', { name: '2' }).click();

    // Wait for data to load
    await expect(page.getByRole('row').filter({ hasNot: page.getByRole('columnheader') }).first())
      .not.toHaveText(firstPageFirstRow!);

    // Verify page 2 is active
    await expect(pagination.getByRole('button', { name: '2' })).toHaveAttribute(
      'aria-current',
      'page'
    );

    // Verify URL updated with page parameter
    await expect(page).toHaveURL(/[?&]page=2/);
  });

  test('shows correct item count', async ({ page }) => {
    await page.goto('/products');

    // Verify the total count display
    await expect(page.getByText(/showing \d+.+of \d+/i)).toBeVisible();
  });
});

test.describe('reading resources as cards', () => {
  test('displays resources in a card grid', async ({ page }) => {
    await page.goto('/products?view=grid');

    // Verify cards are displayed
    const cards = page.getByRole('article');
    await expect(cards.first()).toBeVisible();

    // Verify card content
    const firstCard = cards.first();
    await expect(firstCard.getByRole('heading')).toBeVisible();
    await expect(firstCard.getByText('$')).toBeVisible();
    await expect(firstCard.getByRole('img')).toBeVisible();
  });

  test('switches between list and grid view', async ({ page }) => {
    await page.goto('/products');

    // Start in table/list view
    await expect(page.getByRole('table')).toBeVisible();

    // Switch to grid
    await page.getByRole('button', { name: /grid view/i }).click();
    await expect(page.getByRole('article').first()).toBeVisible();
    await expect(page.getByRole('table')).not.toBeVisible();

    // Switch back to list
    await page.getByRole('button', { name: /list view/i }).click();
    await expect(page.getByRole('table')).toBeVisible();
  });
});
```

**JavaScript**

```javascript
const { test, expect } = require('@playwright/test');

test('displays resources in a table with correct columns', async ({ page }) => {
  await page.goto('/products');

  const headers = page.getByRole('columnheader');
  await expect(headers).toContainText(['Name', 'SKU', 'Price', 'Category', 'Status']);

  const rows = page.getByRole('row').filter({ hasNot: page.getByRole('columnheader') });
  await expect(rows.first()).toBeVisible();
});

test('paginates through results', async ({ page }) => {
  await page.goto('/products');

  const pagination = page.getByRole('navigation', { name: /pagination/i });
  await expect(pagination).toBeVisible();

  const firstPageFirstRow = await page
    .getByRole('row')
    .filter({ hasNot: page.getByRole('columnheader') })
    .first()
    .textContent();

  await pagination.getByRole('button', { name: '2' }).click();

  await expect(page.getByRole('row').filter({ hasNot: page.getByRole('columnheader') }).first())
    .not.toHaveText(firstPageFirstRow);

  await expect(page).toHaveURL(/[?&]page=2/);
});
```

---

## Recipe 3: Updating a Resource (Edit Form, Save, Verify Changes)

### Complete Example

**TypeScript**

```typescript
import { test, expect } from '@playwright/test';

test('updates an existing product', async ({ page }) => {
  await page.goto('/products');

  // Find the target row and click edit
  const row = page.getByRole('row', { name: /Wireless Keyboard/ });
  await row.getByRole('button', { name: 'Edit' }).click();

  // Verify the edit form is pre-filled with existing data
  await expect(page.getByLabel('Product name')).toHaveValue('Wireless Keyboard');
  await expect(page.getByLabel('Price')).toHaveValue('79.99');

  // Update the fields
  await page.getByLabel('Product name').clear();
  await page.getByLabel('Product name').fill('Wireless Keyboard Pro');
  await page.getByLabel('Price').clear();
  await page.getByLabel('Price').fill('99.99');

  // Save changes
  await page.getByRole('button', { name: 'Save changes' }).click();

  // Verify success notification
  await expect(page.getByRole('alert')).toContainText('Product updated successfully');

  // Verify the list reflects the changes
  await expect(page.getByRole('row', { name: /Wireless Keyboard Pro/ })).toBeVisible();
  await expect(page.getByRole('row', { name: /Wireless Keyboard Pro/ })).toContainText('$99.99');

  // Verify old name is gone
  await expect(page.getByRole('row', { name: /^Wireless Keyboard$/ })).not.toBeVisible();
});

test('edit form preserves data when navigating away and back', async ({ page }) => {
  await page.goto('/products');

  const row = page.getByRole('row', { name: /Wireless Keyboard/ });
  await row.getByRole('button', { name: 'Edit' }).click();

  // Make changes but do not save
  await page.getByLabel('Product name').clear();
  await page.getByLabel('Product name').fill('Modified Name');

  // Try navigating away
  await page.getByRole('link', { name: 'Dashboard' }).click();

  // Expect unsaved changes warning
  page.on('dialog', async (dialog) => {
    expect(dialog.message()).toContain('unsaved changes');
    await dialog.dismiss(); // Stay on page
  });

  // Verify data is still there after dismissing navigation
  await expect(page.getByLabel('Product name')).toHaveValue('Modified Name');
});

test('cancelling edit discards changes', async ({ page }) => {
  await page.goto('/products');

  const row = page.getByRole('row', { name: /Wireless Keyboard/ });
  await row.getByRole('button', { name: 'Edit' }).click();

  // Make changes
  await page.getByLabel('Product name').clear();
  await page.getByLabel('Product name').fill('Should Not Save');

  // Cancel
  await page.getByRole('button', { name: 'Cancel' }).click();

  // Verify original data is preserved
  await expect(page.getByRole('row', { name: /Wireless Keyboard/ })).toBeVisible();
  await expect(page.getByRole('row', { name: /Should Not Save/ })).not.toBeVisible();
});
```

**JavaScript**

```javascript
const { test, expect } = require('@playwright/test');

test('updates an existing product', async ({ page }) => {
  await page.goto('/products');

  const row = page.getByRole('row', { name: /Wireless Keyboard/ });
  await row.getByRole('button', { name: 'Edit' }).click();

  await expect(page.getByLabel('Product name')).toHaveValue('Wireless Keyboard');
  await expect(page.getByLabel('Price')).toHaveValue('79.99');

  await page.getByLabel('Product name').clear();
  await page.getByLabel('Product name').fill('Wireless Keyboard Pro');
  await page.getByLabel('Price').clear();
  await page.getByLabel('Price').fill('99.99');

  await page.getByRole('button', { name: 'Save changes' }).click();

  await expect(page.getByRole('alert')).toContainText('Product updated successfully');
  await expect(page.getByRole('row', { name: /Wireless Keyboard Pro/ })).toBeVisible();
  await expect(page.getByRole('row', { name: /Wireless Keyboard Pro/ })).toContainText('$99.99');
});

test('cancelling edit discards changes', async ({ page }) => {
  await page.goto('/products');

  const row = page.getByRole('row', { name: /Wireless Keyboard/ });
  await row.getByRole('button', { name: 'Edit' }).click();

  await page.getByLabel('Product name').clear();
  await page.getByLabel('Product name').fill('Should Not Save');

  await page.getByRole('button', { name: 'Cancel' }).click();

  await expect(page.getByRole('row', { name: /Wireless Keyboard/ })).toBeVisible();
  await expect(page.getByRole('row', { name: /Should Not Save/ })).not.toBeVisible();
});
```

---

## Recipe 4: Deleting a Resource (Delete, Confirm Dialog, Verify Removal)

### Complete Example

**TypeScript**

```typescript
import { test, expect } from '@playwright/test';

test('deletes a product with confirmation dialog', async ({ page }) => {
  await page.goto('/products');

  // Count items before deletion
  const rowsBefore = page.getByRole('row').filter({ hasNot: page.getByRole('columnheader') });
  const countBefore = await rowsBefore.count();

  // Click delete on a specific product
  const targetRow = page.getByRole('row', { name: /Wireless Keyboard/ });
  await expect(targetRow).toBeVisible();
  await targetRow.getByRole('button', { name: 'Delete' }).click();

  // Confirmation dialog should appear
  const dialog = page.getByRole('dialog');
  await expect(dialog).toBeVisible();
  await expect(dialog).toContainText('Are you sure you want to delete');
  await expect(dialog).toContainText('Wireless Keyboard');
  await expect(dialog.getByText(/cannot be undone/i)).toBeVisible();

  // Confirm the deletion
  await dialog.getByRole('button', { name: 'Delete' }).click();

  // Verify the dialog closes
  await expect(dialog).not.toBeVisible();

  // Verify success notification
  await expect(page.getByRole('alert')).toContainText('Product deleted');

  // Verify the item is removed from the list
  await expect(page.getByRole('row', { name: /Wireless Keyboard/ })).not.toBeVisible();

  // Verify count decreased
  const rowsAfter = page.getByRole('row').filter({ hasNot: page.getByRole('columnheader') });
  await expect(rowsAfter).toHaveCount(countBefore - 1);
});

test('cancel delete preserves the resource', async ({ page }) => {
  await page.goto('/products');

  const targetRow = page.getByRole('row', { name: /Wireless Keyboard/ });
  await targetRow.getByRole('button', { name: 'Delete' }).click();

  const dialog = page.getByRole('dialog');
  await expect(dialog).toBeVisible();

  // Cancel the deletion
  await dialog.getByRole('button', { name: 'Cancel' }).click();

  // Dialog closes, item is still present
  await expect(dialog).not.toBeVisible();
  await expect(page.getByRole('row', { name: /Wireless Keyboard/ })).toBeVisible();
});

test('handles delete error gracefully', async ({ page }) => {
  // Mock the delete endpoint to fail
  await page.route('**/api/products/*', async (route) => {
    if (route.request().method() === 'DELETE') {
      await route.fulfill({
        status: 409,
        contentType: 'application/json',
        body: JSON.stringify({
          error: 'Cannot delete product with active orders',
        }),
      });
    } else {
      await route.continue();
    }
  });

  await page.goto('/products');

  const targetRow = page.getByRole('row', { name: /Wireless Keyboard/ });
  await targetRow.getByRole('button', { name: 'Delete' }).click();

  const dialog = page.getByRole('dialog');
  await dialog.getByRole('button', { name: 'Delete' }).click();

  // Verify error is shown to user
  await expect(page.getByRole('alert')).toContainText('Cannot delete product with active orders');

  // Item should still be in the list
  await expect(page.getByRole('row', { name: /Wireless Keyboard/ })).toBeVisible();
});
```

**JavaScript**

```javascript
const { test, expect } = require('@playwright/test');

test('deletes a product with confirmation dialog', async ({ page }) => {
  await page.goto('/products');

  const rowsBefore = page.getByRole('row').filter({ hasNot: page.getByRole('columnheader') });
  const countBefore = await rowsBefore.count();

  const targetRow = page.getByRole('row', { name: /Wireless Keyboard/ });
  await targetRow.getByRole('button', { name: 'Delete' }).click();

  const dialog = page.getByRole('dialog');
  await expect(dialog).toBeVisible();
  await expect(dialog).toContainText('Wireless Keyboard');

  await dialog.getByRole('button', { name: 'Delete' }).click();

  await expect(dialog).not.toBeVisible();
  await expect(page.getByRole('alert')).toContainText('Product deleted');
  await expect(page.getByRole('row', { name: /Wireless Keyboard/ })).not.toBeVisible();

  const rowsAfter = page.getByRole('row').filter({ hasNot: page.getByRole('columnheader') });
  await expect(rowsAfter).toHaveCount(countBefore - 1);
});

test('cancel delete preserves the resource', async ({ page }) => {
  await page.goto('/products');

  const targetRow = page.getByRole('row', { name: /Wireless Keyboard/ });
  await targetRow.getByRole('button', { name: 'Delete' }).click();

  const dialog = page.getByRole('dialog');
  await dialog.getByRole('button', { name: 'Cancel' }).click();

  await expect(dialog).not.toBeVisible();
  await expect(page.getByRole('row', { name: /Wireless Keyboard/ })).toBeVisible();
});
```

---

## Recipe 5: Inline Editing

### Complete Example

**TypeScript**

```typescript
import { test, expect } from '@playwright/test';

test('edits a field inline by double-clicking', async ({ page }) => {
  await page.goto('/products');

  const row = page.getByRole('row', { name: /Wireless Keyboard/ });
  const nameCell = row.getByRole('cell').first();

  // Double-click to enter edit mode
  await nameCell.dblclick();

  // The cell should now contain an input
  const inlineInput = nameCell.getByRole('textbox');
  await expect(inlineInput).toBeVisible();
  await expect(inlineInput).toHaveValue('Wireless Keyboard');

  // Edit the value
  await inlineInput.clear();
  await inlineInput.fill('Wireless Keyboard v2');

  // Press Enter to save
  await inlineInput.press('Enter');

  // Verify the cell shows the updated value (no longer an input)
  await expect(nameCell.getByRole('textbox')).not.toBeVisible();
  await expect(nameCell).toHaveText('Wireless Keyboard v2');

  // Verify a success indicator appears
  await expect(page.getByRole('alert')).toContainText(/saved|updated/i);
});

test('cancels inline edit with Escape key', async ({ page }) => {
  await page.goto('/products');

  const row = page.getByRole('row', { name: /Wireless Keyboard/ });
  const nameCell = row.getByRole('cell').first();

  await nameCell.dblclick();

  const inlineInput = nameCell.getByRole('textbox');
  await inlineInput.clear();
  await inlineInput.fill('Temporary Value');

  // Press Escape to cancel
  await inlineInput.press('Escape');

  // Verify original value is restored
  await expect(nameCell).toHaveText('Wireless Keyboard');
  await expect(nameCell.getByRole('textbox')).not.toBeVisible();
});

test('inline edit with click-away saves changes', async ({ page }) => {
  await page.goto('/products');

  const row = page.getByRole('row', { name: /Wireless Keyboard/ });
  const nameCell = row.getByRole('cell').first();

  await nameCell.dblclick();

  const inlineInput = nameCell.getByRole('textbox');
  await inlineInput.clear();
  await inlineInput.fill('Keyboard Updated');

  // Click somewhere else on the page to trigger save
  await page.getByRole('heading').first().click();

  await expect(nameCell).toHaveText('Keyboard Updated');
});

test('inline edit shows validation error', async ({ page }) => {
  await page.goto('/products');

  const row = page.getByRole('row', { name: /Wireless Keyboard/ });
  const priceCell = row.getByRole('cell').nth(2);

  await priceCell.dblclick();

  const inlineInput = priceCell.getByRole('textbox');
  await inlineInput.clear();
  await inlineInput.fill('-10');
  await inlineInput.press('Enter');

  // Validation error should appear inline
  await expect(priceCell.getByText(/positive number|invalid/i)).toBeVisible();

  // Input should remain visible for correction
  await expect(inlineInput).toBeVisible();
});
```

**JavaScript**

```javascript
const { test, expect } = require('@playwright/test');

test('edits a field inline by double-clicking', async ({ page }) => {
  await page.goto('/products');

  const row = page.getByRole('row', { name: /Wireless Keyboard/ });
  const nameCell = row.getByRole('cell').first();

  await nameCell.dblclick();

  const inlineInput = nameCell.getByRole('textbox');
  await expect(inlineInput).toBeVisible();
  await expect(inlineInput).toHaveValue('Wireless Keyboard');

  await inlineInput.clear();
  await inlineInput.fill('Wireless Keyboard v2');
  await inlineInput.press('Enter');

  await expect(nameCell.getByRole('textbox')).not.toBeVisible();
  await expect(nameCell).toHaveText('Wireless Keyboard v2');
});

test('cancels inline edit with Escape key', async ({ page }) => {
  await page.goto('/products');

  const row = page.getByRole('row', { name: /Wireless Keyboard/ });
  const nameCell = row.getByRole('cell').first();

  await nameCell.dblclick();
  const inlineInput = nameCell.getByRole('textbox');
  await inlineInput.clear();
  await inlineInput.fill('Temporary Value');
  await inlineInput.press('Escape');

  await expect(nameCell).toHaveText('Wireless Keyboard');
});
```

---

## Recipe 6: Bulk Operations

### Complete Example

**TypeScript**

```typescript
import { test, expect } from '@playwright/test';

test('selects multiple items and performs bulk delete', async ({ page }) => {
  await page.goto('/products');

  // Select multiple items via checkboxes
  const rows = page.getByRole('row').filter({ hasNot: page.getByRole('columnheader') });

  await rows.nth(0).getByRole('checkbox').check();
  await rows.nth(1).getByRole('checkbox').check();
  await rows.nth(2).getByRole('checkbox').check();

  // Verify selection count is shown
  await expect(page.getByText('3 items selected')).toBeVisible();

  // Verify bulk action toolbar appears
  const bulkToolbar = page.getByRole('toolbar', { name: /bulk actions/i });
  await expect(bulkToolbar).toBeVisible();

  // Click bulk delete
  await bulkToolbar.getByRole('button', { name: 'Delete selected' }).click();

  // Confirm in dialog
  const dialog = page.getByRole('dialog');
  await expect(dialog).toContainText('Delete 3 products');
  await dialog.getByRole('button', { name: 'Delete' }).click();

  // Verify items removed
  await expect(page.getByRole('alert')).toContainText('3 products deleted');

  // Verify selection count is cleared
  await expect(page.getByText('items selected')).not.toBeVisible();
  await expect(bulkToolbar).not.toBeVisible();
});

test('select all and deselect all', async ({ page }) => {
  await page.goto('/products');

  // Click "Select all" checkbox in the header
  const selectAllCheckbox = page
    .getByRole('row')
    .filter({ has: page.getByRole('columnheader') })
    .getByRole('checkbox');

  await selectAllCheckbox.check();

  // All row checkboxes should be checked
  const rowCheckboxes = page
    .getByRole('row')
    .filter({ hasNot: page.getByRole('columnheader') })
    .getByRole('checkbox');

  const count = await rowCheckboxes.count();
  for (let i = 0; i < count; i++) {
    await expect(rowCheckboxes.nth(i)).toBeChecked();
  }

  await expect(page.getByText(`${count} items selected`)).toBeVisible();

  // Deselect all
  await selectAllCheckbox.uncheck();

  for (let i = 0; i < count; i++) {
    await expect(rowCheckboxes.nth(i)).not.toBeChecked();
  }

  await expect(page.getByText('items selected')).not.toBeVisible();
});

test('bulk status change', async ({ page }) => {
  await page.goto('/products');

  const rows = page.getByRole('row').filter({ hasNot: page.getByRole('columnheader') });
  await rows.nth(0).getByRole('checkbox').check();
  await rows.nth(1).getByRole('checkbox').check();

  const bulkToolbar = page.getByRole('toolbar', { name: /bulk actions/i });
  await bulkToolbar.getByRole('button', { name: 'Change status' }).click();

  // Select new status from dropdown
  await page.getByRole('menuitem', { name: 'Archived' }).click();

  await expect(page.getByRole('alert')).toContainText('2 products archived');

  // Verify status changed in the rows
  await expect(rows.nth(0)).toContainText('Archived');
  await expect(rows.nth(1)).toContainText('Archived');
});

test('bulk export selected items', async ({ page }) => {
  await page.goto('/products');

  const rows = page.getByRole('row').filter({ hasNot: page.getByRole('columnheader') });
  await rows.nth(0).getByRole('checkbox').check();
  await rows.nth(1).getByRole('checkbox').check();

  const bulkToolbar = page.getByRole('toolbar', { name: /bulk actions/i });

  // Start waiting for download before clicking
  const downloadPromise = page.waitForEvent('download');
  await bulkToolbar.getByRole('button', { name: 'Export' }).click();

  const download = await downloadPromise;
  expect(download.suggestedFilename()).toMatch(/products.*\.csv$/);
});
```

**JavaScript**

```javascript
const { test, expect } = require('@playwright/test');

test('selects multiple items and performs bulk delete', async ({ page }) => {
  await page.goto('/products');

  const rows = page.getByRole('row').filter({ hasNot: page.getByRole('columnheader') });
  await rows.nth(0).getByRole('checkbox').check();
  await rows.nth(1).getByRole('checkbox').check();
  await rows.nth(2).getByRole('checkbox').check();

  await expect(page.getByText('3 items selected')).toBeVisible();

  const bulkToolbar = page.getByRole('toolbar', { name: /bulk actions/i });
  await bulkToolbar.getByRole('button', { name: 'Delete selected' }).click();

  const dialog = page.getByRole('dialog');
  await expect(dialog).toContainText('Delete 3 products');
  await dialog.getByRole('button', { name: 'Delete' }).click();

  await expect(page.getByRole('alert')).toContainText('3 products deleted');
});

test('select all and deselect all', async ({ page }) => {
  await page.goto('/products');

  const selectAllCheckbox = page
    .getByRole('row')
    .filter({ has: page.getByRole('columnheader') })
    .getByRole('checkbox');

  await selectAllCheckbox.check();

  const rowCheckboxes = page
    .getByRole('row')
    .filter({ hasNot: page.getByRole('columnheader') })
    .getByRole('checkbox');

  const count = await rowCheckboxes.count();
  for (let i = 0; i < count; i++) {
    await expect(rowCheckboxes.nth(i)).toBeChecked();
  }
});
```

---

## Variations

### Create with Multi-Step Wizard

```typescript
test('creates a resource through a multi-step wizard', async ({ page }) => {
  await page.goto('/products');
  await page.getByRole('button', { name: 'Add product' }).click();

  // Step 1: Basic info
  await expect(page.getByText('Step 1 of 3')).toBeVisible();
  await page.getByLabel('Product name').fill('Wireless Keyboard');
  await page.getByLabel('Category').selectOption('Electronics');
  await page.getByRole('button', { name: 'Next' }).click();

  // Step 2: Pricing
  await expect(page.getByText('Step 2 of 3')).toBeVisible();
  await page.getByLabel('Price').fill('79.99');
  await page.getByLabel('Tax rate').selectOption('Standard (20%)');
  await page.getByRole('button', { name: 'Next' }).click();

  // Step 3: Review and confirm
  await expect(page.getByText('Step 3 of 3')).toBeVisible();
  await expect(page.getByText('Wireless Keyboard')).toBeVisible();
  await expect(page.getByText('$79.99')).toBeVisible();
  await page.getByRole('button', { name: 'Create product' }).click();

  await expect(page.getByRole('alert')).toContainText('Product created');
});
```

### CRUD with API Verification

```typescript
test('create and verify via API', async ({ page, request }) => {
  await page.goto('/products');
  await page.getByRole('button', { name: 'Add product' }).click();

  await page.getByLabel('Product name').fill('API Verified Product');
  await page.getByLabel('Price').fill('49.99');
  await page.getByRole('button', { name: 'Save product' }).click();

  await expect(page.getByRole('alert')).toContainText('Product created');

  // Also verify via API that the data was persisted correctly
  const response = await request.get('/api/products?search=API+Verified+Product');
  const data = await response.json();

  expect(data.products).toHaveLength(1);
  expect(data.products[0].name).toBe('API Verified Product');
  expect(data.products[0].price).toBe(49.99);
});
```

### Optimistic UI Updates

```typescript
test('shows optimistic update then confirms', async ({ page }) => {
  // Slow down the API response to observe optimistic behavior
  await page.route('**/api/products/*', async (route) => {
    if (route.request().method() === 'PATCH') {
      await new Promise((resolve) => setTimeout(resolve, 2000));
      await route.continue();
    } else {
      await route.continue();
    }
  });

  await page.goto('/products');
  const row = page.getByRole('row', { name: /Wireless Keyboard/ });

  await row.getByRole('button', { name: 'Toggle status' }).click();

  // Verify UI updates immediately (optimistic)
  await expect(row.getByText('Active')).toBeVisible();

  // Verify loading indicator while API catches up
  await expect(row.getByRole('progressbar')).toBeVisible();

  // After API responds, loading indicator disappears
  await expect(row.getByRole('progressbar')).not.toBeVisible({ timeout: 5000 });
  await expect(row.getByText('Active')).toBeVisible();
});
```

---

## Tips

1. **Always verify state after mutations**. After a create, update, or delete, assert that the UI reflects the change. Do not assume the success notification alone means the operation worked. Check that the list, table, or card actually changed.

2. **Use unique identifiers in test data**. Include timestamps or random strings in test data to prevent collisions: `Keyboard-${Date.now()}`. This avoids flaky tests from leftover data.

3. **Test the full lifecycle**. Write a single test that creates, reads, updates, and then deletes a resource. This catches integration issues between operations that isolated tests miss.

4. **Clean up test data via API**. Use `test.afterEach` or `test.afterAll` with the `request` fixture to delete resources created during tests, so tests remain independent and repeatable.

5. **Prefer `getByRole('row', { name: ... })` for table operations**. This targets accessible row content and is resilient to column reordering. Avoid relying on `nth()` indices for specific data rows since ordering can change.

---

## Related

- `recipes/search-and-filter.md` -- Filter and search within resource lists
- `recipes/file-upload-download.md` -- Upload files as part of resource creation
- `patterns/page-objects.md` -- Encapsulate CRUD forms in page objects
- `foundations/selectors.md` -- Best practices for selecting table cells and form fields
