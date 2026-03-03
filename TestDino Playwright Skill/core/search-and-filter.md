# Search and Filter Recipes

> **When to use**: You need to test search inputs, filters (category, multi-select, date range), autocomplete suggestions, pagination with filters, or "no results" states.

---

## Recipe 1: Search Input with Results

### Complete Example

**TypeScript**

```typescript
import { test, expect } from '@playwright/test';

test('searches for a product and displays matching results', async ({ page }) => {
  await page.goto('/products');

  const searchInput = page.getByRole('searchbox', { name: /search/i });

  // Type a search query
  await searchInput.fill('wireless keyboard');

  // Submit the search (press Enter or click the search button)
  await searchInput.press('Enter');

  // Wait for results to load
  await expect(page.getByRole('row').filter({ hasNot: page.getByRole('columnheader') }).first())
    .toBeVisible();

  // Verify results match the query
  const rows = page.getByRole('row').filter({ hasNot: page.getByRole('columnheader') });
  const count = await rows.count();
  expect(count).toBeGreaterThan(0);

  // Each result should contain the search term
  for (let i = 0; i < count; i++) {
    await expect(rows.nth(i)).toContainText(/wireless|keyboard/i);
  }

  // Verify the search query is preserved in the input
  await expect(searchInput).toHaveValue('wireless keyboard');

  // Verify result count is displayed
  await expect(page.getByText(/\d+ results? found/i)).toBeVisible();

  // Verify the URL reflects the search
  await expect(page).toHaveURL(/[?&]q=wireless\+keyboard/);
});

test('search is case-insensitive', async ({ page }) => {
  await page.goto('/products');

  const searchInput = page.getByRole('searchbox', { name: /search/i });

  // Search with different cases
  await searchInput.fill('WIRELESS KEYBOARD');
  await searchInput.press('Enter');

  const uppercaseResults = await page
    .getByRole('row')
    .filter({ hasNot: page.getByRole('columnheader') })
    .count();

  await searchInput.clear();
  await searchInput.fill('wireless keyboard');
  await searchInput.press('Enter');

  const lowercaseResults = await page
    .getByRole('row')
    .filter({ hasNot: page.getByRole('columnheader') })
    .count();

  expect(uppercaseResults).toBe(lowercaseResults);
});

test('search preserves query on page reload', async ({ page }) => {
  await page.goto('/products');

  const searchInput = page.getByRole('searchbox', { name: /search/i });
  await searchInput.fill('keyboard');
  await searchInput.press('Enter');

  await expect(page).toHaveURL(/[?&]q=keyboard/);

  // Reload the page
  await page.reload();

  // Search input should still have the query
  await expect(searchInput).toHaveValue('keyboard');

  // Results should still be filtered
  const rows = page.getByRole('row').filter({ hasNot: page.getByRole('columnheader') });
  await expect(rows.first()).toBeVisible();
});
```

**JavaScript**

```javascript
const { test, expect } = require('@playwright/test');

test('searches for a product and displays matching results', async ({ page }) => {
  await page.goto('/products');

  const searchInput = page.getByRole('searchbox', { name: /search/i });

  await searchInput.fill('wireless keyboard');
  await searchInput.press('Enter');

  const rows = page.getByRole('row').filter({ hasNot: page.getByRole('columnheader') });
  const count = await rows.count();
  expect(count).toBeGreaterThan(0);

  for (let i = 0; i < count; i++) {
    await expect(rows.nth(i)).toContainText(/wireless|keyboard/i);
  }

  await expect(searchInput).toHaveValue('wireless keyboard');
  await expect(page).toHaveURL(/[?&]q=wireless\+keyboard/);
});
```

---

## Recipe 2: Search with Debounce (Waiting for Results)

### Complete Example

**TypeScript**

```typescript
import { test, expect } from '@playwright/test';

test('debounced search triggers after user stops typing', async ({ page }) => {
  await page.goto('/products');

  const searchInput = page.getByRole('searchbox', { name: /search/i });
  const resultsList = page.getByRole('row').filter({ hasNot: page.getByRole('columnheader') });

  // Track API calls to verify debounce behavior
  let apiCallCount = 0;
  await page.route('**/api/products?*', async (route) => {
    apiCallCount++;
    await route.continue();
  });

  // Type quickly (simulating real user typing)
  await searchInput.pressSequentially('keyboard', { delay: 50 });

  // Wait for debounce to settle and results to appear
  // The debounce delay is typically 300-500ms after the last keystroke
  await page.waitForResponse('**/api/products?*');

  // Only one API call should have been made (debounced), not one per keystroke
  expect(apiCallCount).toBeLessThanOrEqual(2); // Allow for at most 2 calls

  // Verify results loaded
  await expect(resultsList.first()).toBeVisible();
});

test('shows loading indicator during debounced search', async ({ page }) => {
  // Slow down the search API to observe loading state
  await page.route('**/api/products?*', async (route) => {
    await new Promise((resolve) => setTimeout(resolve, 1000));
    await route.continue();
  });

  await page.goto('/products');

  const searchInput = page.getByRole('searchbox', { name: /search/i });

  await searchInput.fill('keyboard');

  // Loading indicator should appear while waiting for results
  await expect(page.getByRole('progressbar').or(page.getByText(/loading|searching/i))).toBeVisible();

  // After results load, loading indicator disappears
  await expect(page.getByRole('progressbar').or(page.getByText(/loading|searching/i))).not.toBeVisible({
    timeout: 5000,
  });

  // Results should be visible
  await expect(
    page.getByRole('row').filter({ hasNot: page.getByRole('columnheader') }).first()
  ).toBeVisible();
});

test('clears search results when input is emptied', async ({ page }) => {
  await page.goto('/products');

  const searchInput = page.getByRole('searchbox', { name: /search/i });

  // Search for something specific
  await searchInput.fill('keyboard');
  await searchInput.press('Enter');

  const filteredCount = await page
    .getByRole('row')
    .filter({ hasNot: page.getByRole('columnheader') })
    .count();

  // Clear the search
  await searchInput.clear();

  // Wait for results to reset (debounce + API call)
  await page.waitForResponse('**/api/products?*');

  const unfilteredCount = await page
    .getByRole('row')
    .filter({ hasNot: page.getByRole('columnheader') })
    .count();

  // Unfiltered should have more or equal results
  expect(unfilteredCount).toBeGreaterThanOrEqual(filteredCount);
});
```

**JavaScript**

```javascript
const { test, expect } = require('@playwright/test');

test('debounced search triggers after user stops typing', async ({ page }) => {
  await page.goto('/products');

  const searchInput = page.getByRole('searchbox', { name: /search/i });

  let apiCallCount = 0;
  await page.route('**/api/products?*', async (route) => {
    apiCallCount++;
    await route.continue();
  });

  await searchInput.pressSequentially('keyboard', { delay: 50 });

  await page.waitForResponse('**/api/products?*');

  expect(apiCallCount).toBeLessThanOrEqual(2);
});

test('shows loading indicator during debounced search', async ({ page }) => {
  await page.route('**/api/products?*', async (route) => {
    await new Promise((resolve) => setTimeout(resolve, 1000));
    await route.continue();
  });

  await page.goto('/products');

  const searchInput = page.getByRole('searchbox', { name: /search/i });
  await searchInput.fill('keyboard');

  await expect(page.getByRole('progressbar').or(page.getByText(/loading|searching/i))).toBeVisible();

  await expect(page.getByRole('progressbar').or(page.getByText(/loading|searching/i))).not.toBeVisible({
    timeout: 5000,
  });
});
```

---

## Recipe 3: Filter by Category

### Complete Example

**TypeScript**

```typescript
import { test, expect } from '@playwright/test';

test('filters products by a single category', async ({ page }) => {
  await page.goto('/products');

  // Get total count before filtering
  const totalRows = page.getByRole('row').filter({ hasNot: page.getByRole('columnheader') });
  const totalCount = await totalRows.count();

  // Select a category filter
  await page.getByLabel('Category').selectOption('Electronics');

  // Wait for filtered results
  await page.waitForResponse('**/api/products?*');

  // Verify fewer results (or at minimum, a different set)
  const filteredRows = page.getByRole('row').filter({ hasNot: page.getByRole('columnheader') });
  const filteredCount = await filteredRows.count();

  expect(filteredCount).toBeLessThanOrEqual(totalCount);
  expect(filteredCount).toBeGreaterThan(0);

  // Verify all results belong to the selected category
  for (let i = 0; i < filteredCount; i++) {
    await expect(filteredRows.nth(i)).toContainText('Electronics');
  }

  // Verify URL updated
  await expect(page).toHaveURL(/[?&]category=electronics/i);

  // Verify active filter is displayed
  await expect(page.getByText(/filtered by.*electronics/i).or(
    page.locator('[data-testid="active-filter"]').filter({ hasText: 'Electronics' })
  )).toBeVisible();
});

test('filters by category using sidebar checkboxes', async ({ page }) => {
  await page.goto('/products');

  // Click a category checkbox in the sidebar
  const sidebar = page.getByRole('complementary');
  await sidebar.getByLabel('Electronics').check();

  await page.waitForResponse('**/api/products?*');

  const rows = page.getByRole('row').filter({ hasNot: page.getByRole('columnheader') });
  const count = await rows.count();

  for (let i = 0; i < count; i++) {
    await expect(rows.nth(i)).toContainText('Electronics');
  }
});

test('changing category replaces previous filter', async ({ page }) => {
  await page.goto('/products');

  // Select first category
  await page.getByLabel('Category').selectOption('Electronics');
  await page.waitForResponse('**/api/products?*');

  const electronicsCount = await page
    .getByRole('row')
    .filter({ hasNot: page.getByRole('columnheader') })
    .count();

  // Change to a different category
  await page.getByLabel('Category').selectOption('Clothing');
  await page.waitForResponse('**/api/products?*');

  const clothingCount = await page
    .getByRole('row')
    .filter({ hasNot: page.getByRole('columnheader') })
    .count();

  // Results should be different
  const rows = page.getByRole('row').filter({ hasNot: page.getByRole('columnheader') });
  for (let i = 0; i < clothingCount; i++) {
    await expect(rows.nth(i)).toContainText('Clothing');
    await expect(rows.nth(i)).not.toContainText('Electronics');
  }
});
```

**JavaScript**

```javascript
const { test, expect } = require('@playwright/test');

test('filters products by a single category', async ({ page }) => {
  await page.goto('/products');

  const totalRows = page.getByRole('row').filter({ hasNot: page.getByRole('columnheader') });
  const totalCount = await totalRows.count();

  await page.getByLabel('Category').selectOption('Electronics');

  await page.waitForResponse('**/api/products?*');

  const filteredRows = page.getByRole('row').filter({ hasNot: page.getByRole('columnheader') });
  const filteredCount = await filteredRows.count();

  expect(filteredCount).toBeLessThanOrEqual(totalCount);

  for (let i = 0; i < filteredCount; i++) {
    await expect(filteredRows.nth(i)).toContainText('Electronics');
  }

  await expect(page).toHaveURL(/[?&]category=electronics/i);
});
```

---

## Recipe 4: Multi-Select Filter

### Complete Example

**TypeScript**

```typescript
import { test, expect } from '@playwright/test';

test('filters by multiple categories simultaneously', async ({ page }) => {
  await page.goto('/products');

  const sidebar = page.getByRole('complementary');

  // Select multiple category checkboxes
  await sidebar.getByLabel('Electronics').check();
  await sidebar.getByLabel('Clothing').check();

  // Wait for results to update
  await page.waitForResponse('**/api/products?*');

  // Verify results include items from both categories
  const rows = page.getByRole('row').filter({ hasNot: page.getByRole('columnheader') });
  const count = await rows.count();
  expect(count).toBeGreaterThan(0);

  // Collect all categories from results
  const categories = new Set<string>();
  for (let i = 0; i < count; i++) {
    const text = await rows.nth(i).textContent();
    if (text?.includes('Electronics')) categories.add('Electronics');
    if (text?.includes('Clothing')) categories.add('Clothing');
  }

  // Should have results from both categories
  expect(categories.has('Electronics')).toBe(true);
  expect(categories.has('Clothing')).toBe(true);

  // URL should reflect both filters
  await expect(page).toHaveURL(/category=electronics/i);
  await expect(page).toHaveURL(/category=clothing/i);

  // Active filter chips should be visible
  await expect(page.getByRole('button', { name: /Electronics.*×|Remove Electronics/i })).toBeVisible();
  await expect(page.getByRole('button', { name: /Clothing.*×|Remove Clothing/i })).toBeVisible();
});

test('removes one filter from a multi-select filter', async ({ page }) => {
  await page.goto('/products');

  const sidebar = page.getByRole('complementary');

  // Apply two filters
  await sidebar.getByLabel('Electronics').check();
  await sidebar.getByLabel('Clothing').check();
  await page.waitForResponse('**/api/products?*');

  const bothCount = await page
    .getByRole('row')
    .filter({ hasNot: page.getByRole('columnheader') })
    .count();

  // Remove one filter by clicking the filter chip's remove button
  await page.getByRole('button', { name: /Clothing.*×|Remove Clothing/i }).click();
  await page.waitForResponse('**/api/products?*');

  // Verify only Electronics results remain
  const rows = page.getByRole('row').filter({ hasNot: page.getByRole('columnheader') });
  const electronicsOnlyCount = await rows.count();

  expect(electronicsOnlyCount).toBeLessThanOrEqual(bothCount);

  for (let i = 0; i < electronicsOnlyCount; i++) {
    await expect(rows.nth(i)).toContainText('Electronics');
  }

  // Clothing checkbox should be unchecked
  await expect(sidebar.getByLabel('Clothing')).not.toBeChecked();
  await expect(sidebar.getByLabel('Electronics')).toBeChecked();
});

test('multi-select dropdown filter', async ({ page }) => {
  await page.goto('/products');

  // Open the multi-select dropdown
  await page.getByRole('combobox', { name: 'Tags' }).click();

  // Select multiple options from the dropdown
  await page.getByRole('option', { name: 'Featured' }).click();
  await page.getByRole('option', { name: 'On Sale' }).click();

  // Close the dropdown
  await page.keyboard.press('Escape');

  // Verify selected values displayed
  await expect(page.getByText('Featured')).toBeVisible();
  await expect(page.getByText('On Sale')).toBeVisible();

  // Wait for results
  await page.waitForResponse('**/api/products?*');

  const rows = page.getByRole('row').filter({ hasNot: page.getByRole('columnheader') });
  await expect(rows.first()).toBeVisible();
});
```

**JavaScript**

```javascript
const { test, expect } = require('@playwright/test');

test('filters by multiple categories simultaneously', async ({ page }) => {
  await page.goto('/products');

  const sidebar = page.getByRole('complementary');

  await sidebar.getByLabel('Electronics').check();
  await sidebar.getByLabel('Clothing').check();

  await page.waitForResponse('**/api/products?*');

  const rows = page.getByRole('row').filter({ hasNot: page.getByRole('columnheader') });
  const count = await rows.count();
  expect(count).toBeGreaterThan(0);

  await expect(page).toHaveURL(/category=electronics/i);
  await expect(page).toHaveURL(/category=clothing/i);
});

test('removes one filter from a multi-select filter', async ({ page }) => {
  await page.goto('/products');

  const sidebar = page.getByRole('complementary');

  await sidebar.getByLabel('Electronics').check();
  await sidebar.getByLabel('Clothing').check();
  await page.waitForResponse('**/api/products?*');

  await page.getByRole('button', { name: /Clothing.*×|Remove Clothing/i }).click();
  await page.waitForResponse('**/api/products?*');

  const rows = page.getByRole('row').filter({ hasNot: page.getByRole('columnheader') });
  const count = await rows.count();

  for (let i = 0; i < count; i++) {
    await expect(rows.nth(i)).toContainText('Electronics');
  }
});
```

---

## Recipe 5: Date Range Filter

### Complete Example

**TypeScript**

```typescript
import { test, expect } from '@playwright/test';

test('filters records by date range', async ({ page }) => {
  await page.goto('/orders');

  // Fill in the date range inputs
  await page.getByLabel('From date').fill('2024-01-01');
  await page.getByLabel('To date').fill('2024-03-31');

  // Apply the filter
  await page.getByRole('button', { name: 'Apply filter' }).click();

  // Wait for filtered results
  await page.waitForResponse('**/api/orders?*');

  // Verify all results fall within the date range
  const rows = page.getByRole('row').filter({ hasNot: page.getByRole('columnheader') });
  const count = await rows.count();
  expect(count).toBeGreaterThan(0);

  // Check that each row's date is within the range
  for (let i = 0; i < count; i++) {
    const dateCell = rows.nth(i).getByRole('cell').nth(3); // Assuming date is the 4th column
    const dateText = await dateCell.textContent();
    const date = new Date(dateText!.trim());
    expect(date.getTime()).toBeGreaterThanOrEqual(new Date('2024-01-01').getTime());
    expect(date.getTime()).toBeLessThanOrEqual(new Date('2024-03-31T23:59:59').getTime());
  }

  // Verify URL updated with date params
  await expect(page).toHaveURL(/from=2024-01-01/);
  await expect(page).toHaveURL(/to=2024-03-31/);
});

test('filters using a date picker component', async ({ page }) => {
  await page.goto('/orders');

  // Open the date picker
  await page.getByRole('button', { name: /date range|calendar/i }).click();

  // Navigate to January 2024
  const calendar = page.getByRole('dialog');
  await expect(calendar).toBeVisible();

  // Select the month/year via navigation
  while (!(await calendar.getByText('January 2024').isVisible())) {
    await calendar.getByRole('button', { name: /previous month/i }).click();
  }

  // Click start date
  await calendar.getByRole('gridcell', { name: '15' }).click();

  // Click end date
  await calendar.getByRole('gridcell', { name: '28' }).click();

  // Apply
  await calendar.getByRole('button', { name: 'Apply' }).click();
  await expect(calendar).not.toBeVisible();

  // Verify the date range is displayed
  await expect(page.getByText(/Jan 15.*Jan 28/i)).toBeVisible();

  await page.waitForResponse('**/api/orders?*');

  const rows = page.getByRole('row').filter({ hasNot: page.getByRole('columnheader') });
  await expect(rows.first()).toBeVisible();
});

test('shows error for invalid date range', async ({ page }) => {
  await page.goto('/orders');

  // Set end date before start date
  await page.getByLabel('From date').fill('2024-06-01');
  await page.getByLabel('To date').fill('2024-01-01');

  await page.getByRole('button', { name: 'Apply filter' }).click();

  await expect(page.getByText(/end date.*before.*start date|invalid.*range/i)).toBeVisible();
});

test('uses preset date ranges', async ({ page }) => {
  await page.goto('/orders');

  // Click a preset date range shortcut
  await page.getByRole('button', { name: 'Last 30 days' }).click();

  await page.waitForResponse('**/api/orders?*');

  // Verify the from date input reflects approximately 30 days ago
  const fromValue = await page.getByLabel('From date').inputValue();
  const fromDate = new Date(fromValue);
  const now = new Date();
  const diffDays = Math.round((now.getTime() - fromDate.getTime()) / (1000 * 60 * 60 * 24));

  expect(diffDays).toBeGreaterThanOrEqual(29);
  expect(diffDays).toBeLessThanOrEqual(31);

  const rows = page.getByRole('row').filter({ hasNot: page.getByRole('columnheader') });
  await expect(rows.first()).toBeVisible();
});
```

**JavaScript**

```javascript
const { test, expect } = require('@playwright/test');

test('filters records by date range', async ({ page }) => {
  await page.goto('/orders');

  await page.getByLabel('From date').fill('2024-01-01');
  await page.getByLabel('To date').fill('2024-03-31');
  await page.getByRole('button', { name: 'Apply filter' }).click();

  await page.waitForResponse('**/api/orders?*');

  const rows = page.getByRole('row').filter({ hasNot: page.getByRole('columnheader') });
  const count = await rows.count();
  expect(count).toBeGreaterThan(0);

  await expect(page).toHaveURL(/from=2024-01-01/);
  await expect(page).toHaveURL(/to=2024-03-31/);
});

test('uses preset date ranges', async ({ page }) => {
  await page.goto('/orders');

  await page.getByRole('button', { name: 'Last 30 days' }).click();

  await page.waitForResponse('**/api/orders?*');

  const rows = page.getByRole('row').filter({ hasNot: page.getByRole('columnheader') });
  await expect(rows.first()).toBeVisible();
});
```

---

## Recipe 6: Clear All Filters

### Complete Example

**TypeScript**

```typescript
import { test, expect } from '@playwright/test';

test('clears all active filters at once', async ({ page }) => {
  await page.goto('/products');

  const sidebar = page.getByRole('complementary');

  // Apply multiple filters
  await sidebar.getByLabel('Electronics').check();
  await page.getByLabel('Min price').fill('50');
  await page.getByLabel('Max price').fill('200');
  await page.getByRole('searchbox', { name: /search/i }).fill('keyboard');
  await page.getByRole('searchbox', { name: /search/i }).press('Enter');

  // Wait for filtered results
  await page.waitForResponse('**/api/products?*');

  const filteredCount = await page
    .getByRole('row')
    .filter({ hasNot: page.getByRole('columnheader') })
    .count();

  // Verify filters are active
  await expect(page.getByText(/\d+ active filter/i)).toBeVisible();

  // Click "Clear all filters"
  await page.getByRole('button', { name: /clear all|reset filters/i }).click();

  // Wait for unfiltered results
  await page.waitForResponse('**/api/products?*');

  // Verify all filters are reset
  await expect(sidebar.getByLabel('Electronics')).not.toBeChecked();
  await expect(page.getByLabel('Min price')).toHaveValue('');
  await expect(page.getByLabel('Max price')).toHaveValue('');
  await expect(page.getByRole('searchbox', { name: /search/i })).toHaveValue('');

  // Verify more results are shown
  const unfilteredCount = await page
    .getByRole('row')
    .filter({ hasNot: page.getByRole('columnheader') })
    .count();

  expect(unfilteredCount).toBeGreaterThanOrEqual(filteredCount);

  // Verify URL is clean
  await expect(page).toHaveURL('/products');

  // Verify "active filters" indicator is gone
  await expect(page.getByText(/active filter/i)).not.toBeVisible();
});

test('clear all button only appears when filters are active', async ({ page }) => {
  await page.goto('/products');

  // No filters active -- clear button should not be visible
  await expect(page.getByRole('button', { name: /clear all|reset filters/i })).not.toBeVisible();

  // Apply a filter
  await page.getByRole('complementary').getByLabel('Electronics').check();
  await page.waitForResponse('**/api/products?*');

  // Clear button should now be visible
  await expect(page.getByRole('button', { name: /clear all|reset filters/i })).toBeVisible();

  // Remove the filter manually
  await page.getByRole('complementary').getByLabel('Electronics').uncheck();
  await page.waitForResponse('**/api/products?*');

  // Clear button should disappear again
  await expect(page.getByRole('button', { name: /clear all|reset filters/i })).not.toBeVisible();
});
```

**JavaScript**

```javascript
const { test, expect } = require('@playwright/test');

test('clears all active filters at once', async ({ page }) => {
  await page.goto('/products');

  const sidebar = page.getByRole('complementary');

  await sidebar.getByLabel('Electronics').check();
  await page.getByLabel('Min price').fill('50');
  await page.getByLabel('Max price').fill('200');
  await page.getByRole('searchbox', { name: /search/i }).fill('keyboard');
  await page.getByRole('searchbox', { name: /search/i }).press('Enter');

  await page.waitForResponse('**/api/products?*');

  await page.getByRole('button', { name: /clear all|reset filters/i }).click();

  await page.waitForResponse('**/api/products?*');

  await expect(sidebar.getByLabel('Electronics')).not.toBeChecked();
  await expect(page.getByLabel('Min price')).toHaveValue('');
  await expect(page.getByLabel('Max price')).toHaveValue('');
  await expect(page.getByRole('searchbox', { name: /search/i })).toHaveValue('');

  await expect(page).toHaveURL('/products');
});
```

---

## Recipe 7: Search with Autocomplete / Suggestions

### Complete Example

**TypeScript**

```typescript
import { test, expect } from '@playwright/test';

test('shows autocomplete suggestions while typing', async ({ page }) => {
  await page.goto('/products');

  const searchInput = page.getByRole('combobox', { name: /search/i });

  // Type a partial query
  await searchInput.fill('key');

  // Suggestions dropdown should appear
  const suggestions = page.getByRole('listbox');
  await expect(suggestions).toBeVisible();

  // Verify suggestions contain the typed text
  const options = suggestions.getByRole('option');
  const count = await options.count();
  expect(count).toBeGreaterThan(0);

  for (let i = 0; i < count; i++) {
    await expect(options.nth(i)).toContainText(/key/i);
  }
});

test('selects a suggestion with click', async ({ page }) => {
  await page.goto('/products');

  const searchInput = page.getByRole('combobox', { name: /search/i });
  await searchInput.fill('key');

  const suggestions = page.getByRole('listbox');
  await expect(suggestions).toBeVisible();

  // Click a specific suggestion
  await suggestions.getByRole('option', { name: /Wireless Keyboard/i }).click();

  // Suggestions should close
  await expect(suggestions).not.toBeVisible();

  // Search input should contain the selected suggestion
  await expect(searchInput).toHaveValue('Wireless Keyboard');

  // Results should be filtered to the selected item
  await expect(page.getByRole('row', { name: /Wireless Keyboard/i })).toBeVisible();
});

test('navigates suggestions with keyboard', async ({ page }) => {
  await page.goto('/products');

  const searchInput = page.getByRole('combobox', { name: /search/i });
  await searchInput.fill('key');

  const suggestions = page.getByRole('listbox');
  await expect(suggestions).toBeVisible();

  // Navigate down with arrow keys
  await searchInput.press('ArrowDown');
  const firstOption = suggestions.getByRole('option').first();
  await expect(firstOption).toHaveAttribute('aria-selected', 'true');

  await searchInput.press('ArrowDown');
  const secondOption = suggestions.getByRole('option').nth(1);
  await expect(secondOption).toHaveAttribute('aria-selected', 'true');
  await expect(firstOption).toHaveAttribute('aria-selected', 'false');

  // Select with Enter
  await searchInput.press('Enter');

  // Suggestions should close and value should be selected
  await expect(suggestions).not.toBeVisible();

  const selectedText = await searchInput.inputValue();
  expect(selectedText.length).toBeGreaterThan(3); // More than just "key"
});

test('closes suggestions with Escape key', async ({ page }) => {
  await page.goto('/products');

  const searchInput = page.getByRole('combobox', { name: /search/i });
  await searchInput.fill('key');

  const suggestions = page.getByRole('listbox');
  await expect(suggestions).toBeVisible();

  await searchInput.press('Escape');

  await expect(suggestions).not.toBeVisible();

  // Input should retain the typed text
  await expect(searchInput).toHaveValue('key');
});

test('shows recent searches when input is focused', async ({ page }) => {
  await page.goto('/products');

  const searchInput = page.getByRole('combobox', { name: /search/i });

  // Focus the input without typing
  await searchInput.click();

  // Should show recent searches or popular suggestions
  const suggestions = page.getByRole('listbox');
  await expect(suggestions).toBeVisible();
  await expect(suggestions.getByText(/recent|popular/i)).toBeVisible();
});
```

**JavaScript**

```javascript
const { test, expect } = require('@playwright/test');

test('shows autocomplete suggestions while typing', async ({ page }) => {
  await page.goto('/products');

  const searchInput = page.getByRole('combobox', { name: /search/i });
  await searchInput.fill('key');

  const suggestions = page.getByRole('listbox');
  await expect(suggestions).toBeVisible();

  const options = suggestions.getByRole('option');
  const count = await options.count();
  expect(count).toBeGreaterThan(0);

  for (let i = 0; i < count; i++) {
    await expect(options.nth(i)).toContainText(/key/i);
  }
});

test('selects a suggestion with click', async ({ page }) => {
  await page.goto('/products');

  const searchInput = page.getByRole('combobox', { name: /search/i });
  await searchInput.fill('key');

  const suggestions = page.getByRole('listbox');
  await suggestions.getByRole('option', { name: /Wireless Keyboard/i }).click();

  await expect(suggestions).not.toBeVisible();
  await expect(searchInput).toHaveValue('Wireless Keyboard');
});

test('navigates suggestions with keyboard', async ({ page }) => {
  await page.goto('/products');

  const searchInput = page.getByRole('combobox', { name: /search/i });
  await searchInput.fill('key');

  const suggestions = page.getByRole('listbox');
  await expect(suggestions).toBeVisible();

  await searchInput.press('ArrowDown');
  await searchInput.press('ArrowDown');
  await searchInput.press('Enter');

  await expect(suggestions).not.toBeVisible();
});
```

---

## Recipe 8: No Results State

### Complete Example

**TypeScript**

```typescript
import { test, expect } from '@playwright/test';

test('shows "no results" state for unmatched search', async ({ page }) => {
  await page.goto('/products');

  const searchInput = page.getByRole('searchbox', { name: /search/i });
  await searchInput.fill('xyznonexistentproduct123');
  await searchInput.press('Enter');

  // Wait for the API response
  await page.waitForResponse('**/api/products?*');

  // Verify no results message is displayed
  await expect(page.getByText(/no results|no products found|nothing found/i)).toBeVisible();

  // Table/list should be empty (no data rows)
  const rows = page.getByRole('row').filter({ hasNot: page.getByRole('columnheader') });
  await expect(rows).toHaveCount(0);

  // Verify helpful suggestions are shown
  await expect(
    page.getByText(/try different|broaden your search|check spelling/i)
  ).toBeVisible();

  // Verify a "clear search" link or button is available
  await expect(
    page.getByRole('button', { name: /clear search|show all/i }).or(
      page.getByRole('link', { name: /clear search|show all/i })
    )
  ).toBeVisible();
});

test('no results state with active filters offers to clear them', async ({ page }) => {
  await page.goto('/products');

  // Apply a very restrictive filter combination
  await page.getByRole('complementary').getByLabel('Electronics').check();
  await page.getByLabel('Min price').fill('99999');
  await page.getByRole('button', { name: 'Apply filter' }).click();

  await page.waitForResponse('**/api/products?*');

  // Verify the no results state mentions the active filters
  await expect(page.getByText(/no results|no products found/i)).toBeVisible();
  await expect(page.getByRole('button', { name: /clear filters|reset/i })).toBeVisible();

  // Click clear filters and verify results appear
  await page.getByRole('button', { name: /clear filters|reset/i }).click();

  await page.waitForResponse('**/api/products?*');

  const rows = page.getByRole('row').filter({ hasNot: page.getByRole('columnheader') });
  expect(await rows.count()).toBeGreaterThan(0);
});

test('no results state illustration is displayed', async ({ page }) => {
  await page.goto('/products');

  await page.getByRole('searchbox', { name: /search/i }).fill('zzzznotfound');
  await page.getByRole('searchbox', { name: /search/i }).press('Enter');

  await page.waitForResponse('**/api/products?*');

  // Verify an illustration or icon is shown
  await expect(
    page.getByRole('img', { name: /no results|empty/i }).or(
      page.locator('[data-testid="empty-state-illustration"]')
    )
  ).toBeVisible();
});
```

**JavaScript**

```javascript
const { test, expect } = require('@playwright/test');

test('shows "no results" state for unmatched search', async ({ page }) => {
  await page.goto('/products');

  const searchInput = page.getByRole('searchbox', { name: /search/i });
  await searchInput.fill('xyznonexistentproduct123');
  await searchInput.press('Enter');

  await page.waitForResponse('**/api/products?*');

  await expect(page.getByText(/no results|no products found|nothing found/i)).toBeVisible();

  const rows = page.getByRole('row').filter({ hasNot: page.getByRole('columnheader') });
  await expect(rows).toHaveCount(0);

  await expect(page.getByText(/try different|broaden your search/i)).toBeVisible();
});

test('no results state with filters offers to clear them', async ({ page }) => {
  await page.goto('/products');

  await page.getByRole('complementary').getByLabel('Electronics').check();
  await page.getByLabel('Min price').fill('99999');
  await page.getByRole('button', { name: 'Apply filter' }).click();

  await page.waitForResponse('**/api/products?*');

  await expect(page.getByText(/no results|no products found/i)).toBeVisible();

  await page.getByRole('button', { name: /clear filters|reset/i }).click();
  await page.waitForResponse('**/api/products?*');

  const rows = page.getByRole('row').filter({ hasNot: page.getByRole('columnheader') });
  expect(await rows.count()).toBeGreaterThan(0);
});
```

---

## Recipe 9: Pagination with Filters

### Complete Example

**TypeScript**

```typescript
import { test, expect } from '@playwright/test';

test('pagination resets to page 1 when a filter is applied', async ({ page }) => {
  await page.goto('/products');

  const pagination = page.getByRole('navigation', { name: /pagination/i });

  // Navigate to page 3
  await pagination.getByRole('button', { name: '3' }).click();
  await expect(page).toHaveURL(/page=3/);

  // Apply a filter
  await page.getByRole('complementary').getByLabel('Electronics').check();
  await page.waitForResponse('**/api/products?*');

  // Should reset to page 1
  await expect(page).toHaveURL(/page=1|(?!.*page=)/);
  await expect(pagination.getByRole('button', { name: '1' })).toHaveAttribute(
    'aria-current',
    'page'
  );
});

test('filters persist across pagination', async ({ page }) => {
  await page.goto('/products');

  // Apply a filter
  await page.getByRole('complementary').getByLabel('Electronics').check();
  await page.waitForResponse('**/api/products?*');

  // Get page 1 results
  const page1FirstItem = await page
    .getByRole('row')
    .filter({ hasNot: page.getByRole('columnheader') })
    .first()
    .textContent();

  // Navigate to page 2
  const pagination = page.getByRole('navigation', { name: /pagination/i });
  await pagination.getByRole('button', { name: '2' }).click();
  await page.waitForResponse('**/api/products?*');

  // Verify the filter is still applied (URL has both params)
  await expect(page).toHaveURL(/category=electronics/i);
  await expect(page).toHaveURL(/page=2/);

  // Verify checkbox is still checked
  await expect(page.getByRole('complementary').getByLabel('Electronics')).toBeChecked();

  // Verify page 2 data is different from page 1
  const page2FirstItem = await page
    .getByRole('row')
    .filter({ hasNot: page.getByRole('columnheader') })
    .first()
    .textContent();

  expect(page2FirstItem).not.toBe(page1FirstItem);

  // All results on page 2 should still match the filter
  const rows = page.getByRole('row').filter({ hasNot: page.getByRole('columnheader') });
  const count = await rows.count();
  for (let i = 0; i < count; i++) {
    await expect(rows.nth(i)).toContainText('Electronics');
  }
});

test('total result count updates with filters', async ({ page }) => {
  await page.goto('/products');

  // Get unfiltered total
  const totalText = await page.getByText(/showing.*of \d+/i).textContent();
  const totalMatch = totalText?.match(/of (\d+)/);
  const totalCount = parseInt(totalMatch?.[1] || '0');

  // Apply a filter
  await page.getByRole('complementary').getByLabel('Electronics').check();
  await page.waitForResponse('**/api/products?*');

  // Total count should be less or equal
  const filteredText = await page.getByText(/showing.*of \d+/i).textContent();
  const filteredMatch = filteredText?.match(/of (\d+)/);
  const filteredCount = parseInt(filteredMatch?.[1] || '0');

  expect(filteredCount).toBeLessThanOrEqual(totalCount);

  // Number of pagination buttons may also decrease
  const paginationButtons = page
    .getByRole('navigation', { name: /pagination/i })
    .getByRole('button')
    .filter({ hasNotText: /previous|next|prev|›|‹/i });

  const pageCount = await paginationButtons.count();
  expect(pageCount).toBeGreaterThan(0);
});

test('deep link with filters and page works correctly', async ({ page }) => {
  // Navigate directly to a filtered, paginated URL
  await page.goto('/products?category=electronics&q=wireless&page=2');

  // Verify all filter controls reflect the URL state
  await expect(page.getByRole('complementary').getByLabel('Electronics')).toBeChecked();
  await expect(page.getByRole('searchbox', { name: /search/i })).toHaveValue('wireless');

  const pagination = page.getByRole('navigation', { name: /pagination/i });
  await expect(pagination.getByRole('button', { name: '2' })).toHaveAttribute(
    'aria-current',
    'page'
  );

  // Verify results match the filters
  const rows = page.getByRole('row').filter({ hasNot: page.getByRole('columnheader') });
  await expect(rows.first()).toBeVisible();
});
```

**JavaScript**

```javascript
const { test, expect } = require('@playwright/test');

test('pagination resets to page 1 when a filter is applied', async ({ page }) => {
  await page.goto('/products');

  const pagination = page.getByRole('navigation', { name: /pagination/i });

  await pagination.getByRole('button', { name: '3' }).click();
  await expect(page).toHaveURL(/page=3/);

  await page.getByRole('complementary').getByLabel('Electronics').check();
  await page.waitForResponse('**/api/products?*');

  await expect(page).toHaveURL(/page=1|(?!.*page=)/);
});

test('filters persist across pagination', async ({ page }) => {
  await page.goto('/products');

  await page.getByRole('complementary').getByLabel('Electronics').check();
  await page.waitForResponse('**/api/products?*');

  const pagination = page.getByRole('navigation', { name: /pagination/i });
  await pagination.getByRole('button', { name: '2' }).click();
  await page.waitForResponse('**/api/products?*');

  await expect(page).toHaveURL(/category=electronics/i);
  await expect(page).toHaveURL(/page=2/);

  await expect(page.getByRole('complementary').getByLabel('Electronics')).toBeChecked();

  const rows = page.getByRole('row').filter({ hasNot: page.getByRole('columnheader') });
  const count = await rows.count();
  for (let i = 0; i < count; i++) {
    await expect(rows.nth(i)).toContainText('Electronics');
  }
});

test('deep link with filters and page works correctly', async ({ page }) => {
  await page.goto('/products?category=electronics&q=wireless&page=2');

  await expect(page.getByRole('complementary').getByLabel('Electronics')).toBeChecked();
  await expect(page.getByRole('searchbox', { name: /search/i })).toHaveValue('wireless');

  const pagination = page.getByRole('navigation', { name: /pagination/i });
  await expect(pagination.getByRole('button', { name: '2' })).toHaveAttribute(
    'aria-current',
    'page'
  );
});
```

---

## Variations

### Search with Highlight of Matching Terms

```typescript
test('highlights matching terms in search results', async ({ page }) => {
  await page.goto('/products');

  await page.getByRole('searchbox', { name: /search/i }).fill('wireless');
  await page.getByRole('searchbox', { name: /search/i }).press('Enter');

  await page.waitForResponse('**/api/products?*');

  // Verify matching text is wrapped in a highlight element
  const highlights = page.locator('mark, .highlight, [data-highlight]');
  const count = await highlights.count();
  expect(count).toBeGreaterThan(0);

  // Each highlight should contain the search term
  for (let i = 0; i < count; i++) {
    await expect(highlights.nth(i)).toContainText(/wireless/i);
  }
});
```

### Search with URL Query Params for Sharing

```typescript
test('search results are shareable via URL', async ({ page, context }) => {
  await page.goto('/products');

  await page.getByRole('searchbox', { name: /search/i }).fill('keyboard');
  await page.getByRole('complementary').getByLabel('Electronics').check();
  await page.getByRole('searchbox', { name: /search/i }).press('Enter');

  await page.waitForResponse('**/api/products?*');

  // Get the current URL
  const searchUrl = page.url();

  // Open the same URL in a new page (simulating sharing the link)
  const newPage = await context.newPage();
  await newPage.goto(searchUrl);

  // Verify the same filters and results are shown
  await expect(newPage.getByRole('searchbox', { name: /search/i })).toHaveValue('keyboard');
  await expect(newPage.getByRole('complementary').getByLabel('Electronics')).toBeChecked();

  const rows = newPage.getByRole('row').filter({ hasNot: newPage.getByRole('columnheader') });
  await expect(rows.first()).toBeVisible();

  await newPage.close();
});
```

### Faceted Search with Result Counts

```typescript
test('filter options show result counts', async ({ page }) => {
  await page.goto('/products');

  const sidebar = page.getByRole('complementary');

  // Verify each filter option shows a count
  await expect(sidebar.getByText(/Electronics \(\d+\)/)).toBeVisible();
  await expect(sidebar.getByText(/Clothing \(\d+\)/)).toBeVisible();
  await expect(sidebar.getByText(/Books \(\d+\)/)).toBeVisible();

  // Apply a filter and verify counts update
  await sidebar.getByLabel('Electronics').check();
  await page.waitForResponse('**/api/products?*');

  // Other category counts should update to reflect cross-filtering
  const clothingText = await sidebar.getByText(/Clothing \(\d+\)/).textContent();
  const clothingCount = parseInt(clothingText?.match(/\((\d+)\)/)?.[1] || '0');

  // The counts should reflect what would happen if that filter were added
  expect(clothingCount).toBeGreaterThanOrEqual(0);
});
```

---

## Tips

1. **Always verify the URL reflects the filter state**. Search queries, category selections, date ranges, and pagination should all be encoded in query parameters. This ensures deep linking, bookmarking, and browser back/forward work correctly. If your app does not do this, file a bug.

2. **Use `waitForResponse` instead of arbitrary waits**. After applying a filter or search, wait for the specific API call to complete: `await page.waitForResponse('**/api/products?*')`. This is deterministic and faster than `waitForTimeout`.

3. **Test filter combinations, not just individual filters**. Users apply multiple filters simultaneously -- category + price range + search term. Test that filters compose correctly and that the resulting URL contains all parameters.

4. **Verify the controls reflect the state, not just the results**. After filtering, check that the checkbox is checked, the dropdown shows the right value, and the search input still contains the query. After clearing, verify they all reset. This catches one-way binding bugs.

5. **Test deep links for every filter combination**. Paste a URL with filter parameters directly (`/products?category=electronics&q=keyboard&page=2`) and verify the page renders correctly. This catches bugs where filters only work when set via the UI but not from URL params.

---

## Related

- `recipes/crud-testing.md` -- Filter and search within CRUD resource lists
- `foundations/assertions.md` -- Assertion patterns for dynamic content
- `patterns/page-objects.md` -- Encapsulate search and filter controls
- `foundations/waiting.md` -- Waiting strategies for async search results
