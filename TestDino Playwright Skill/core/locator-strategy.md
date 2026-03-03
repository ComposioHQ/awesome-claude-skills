# Choosing a Locator Strategy

> **When to use**: When deciding which Playwright locator method to use for an element

## Quick Answer

Use `getByRole()` for everything that has a semantic HTML role (buttons, links, headings, form fields, dialogs). Fall back to `getByLabel()` for form fields, `getByText()` for plain content, and `getByTestId()` only as a last resort for custom components with no accessible role.

## Decision Flowchart

```
Start: You need to locate an element
  |
  v
Does the element have a semantic role?
(button, link, heading, textbox, checkbox, combobox, dialog, img, row, cell, navigation...)
  |
  +-- YES --> Use getByRole('role', { name: 'accessible name' })
  |             |
  |             +-- Need to narrow scope? Chain from a parent role locator:
  |                   getByRole('navigation').getByRole('link', { name: '...' })
  |
  +-- NO
       |
       v
     Is it a form field with a visible <label>?
       |
       +-- YES --> Use getByLabel('label text')
       |
       +-- NO
            |
            v
          Is it static text content (paragraph, span, div with text)?
            |
            +-- YES --> Use getByText('text content')
            |             Prefer { exact: true } when text is short or common
            |
            +-- NO
                 |
                 v
               Does it have a placeholder?
                 |
                 +-- YES --> Use getByPlaceholder('placeholder text')
                 |             (Less preferred -- placeholders disappear on input)
                 |
                 +-- NO
                      |
                      v
                    Does it have a title attribute or alt text?
                      |
                      +-- YES --> Use getByTitle('...') or getByAltText('...')
                      |
                      +-- NO
                           |
                           v
                         Add data-testid="..." to the markup
                         Use getByTestId('identifier')
                         |
                         +--> NEVER fall back to CSS selectors or XPath.
                              Fix the markup instead.
```

## Decision Matrix

| Element Type | Recommended Locator | Fallback | Example |
|---|---|---|---|
| Button | `getByRole('button', { name })` | `getByText()` if role missing | `getByRole('button', { name: 'Submit' })` |
| Link | `getByRole('link', { name })` | `getByText()` for anchor text | `getByRole('link', { name: 'Sign up' })` |
| Text input | `getByLabel('...')` | `getByRole('textbox', { name })` | `getByLabel('Email address')` |
| Checkbox | `getByRole('checkbox', { name })` | `getByLabel()` | `getByRole('checkbox', { name: 'Accept terms' })` |
| Radio button | `getByRole('radio', { name })` | `getByLabel()` | `getByRole('radio', { name: 'Express shipping' })` |
| Dropdown / Select | `getByRole('combobox', { name })` | `getByLabel()` | `getByLabel('Country')` |
| Heading | `getByRole('heading', { name, level })` | `getByText()` | `getByRole('heading', { name: 'Dashboard', level: 1 })` |
| Nav link | chain: `getByRole('navigation').getByRole('link', { name })` | scope with `locator('nav')` | see detailed example below |
| Table cell | chain: `getByRole('row').filter().getByRole('cell')` | `locator('td')` scoped | see detailed example below |
| Image | `getByRole('img', { name })` | `getByAltText()` | `getByRole('img', { name: 'Company logo' })` |
| Modal / Dialog | `getByRole('dialog')` then chain within | `locator('[role="dialog"]')` | `getByRole('dialog').getByRole('button', { name: 'Confirm' })` |
| Dynamic list item | `.filter({ hasText })` or `.filter({ has })` | `nth()` as last resort | `getByRole('listitem').filter({ hasText: 'Milk' })` |
| Custom component | `getByTestId('...')` | Add `data-testid` to markup | `getByTestId('color-picker')` |

## Detailed Analysis

### Tier 1: `getByRole()` -- Use by Default

The strongest locator. It mirrors how assistive technology and real users perceive the page.

**Pros**
- Resilient to markup refactors (class names, tag changes)
- Enforces accessible markup -- if the locator breaks, your accessibility broke too
- Works across frameworks (React, Vue, Angular, plain HTML)
- Supports filtering by `name`, `level`, `checked`, `pressed`, `expanded`, `selected`

**Cons**
- Requires the element to have a valid ARIA role (implicit or explicit)
- Can match multiple elements when names are duplicated -- scope with chaining

**When it fails**: Custom components with `<div>` soup and no ARIA roles. Fix the component first; add `getByTestId()` only if you cannot change the markup.

---

### Tier 2: `getByLabel()` -- Form Fields

Queries by the associated `<label>` text. This is often the most readable locator for form fields.

**Pros**
- Extremely readable: `getByLabel('Password')` tells you exactly what field
- Works with `<label for="...">`, wrapping `<label>`, and `aria-labelledby`

**Cons**
- Only works for form elements with labels
- Breaks if someone changes label text (but that is usually intentional)

**Use over `getByRole('textbox')`** when the label text is clear and unique. Use `getByRole()` when you need to differentiate between multiple fields with similar labels by role type.

---

### Tier 3: `getByText()` -- Static Content

Finds elements by their visible text content.

**Pros**
- Intuitive for non-interactive text (paragraphs, spans, badges, status messages)
- Supports exact and substring matching

**Cons**
- Fragile if text is dynamic, translated, or duplicated
- Can match parent elements unintentionally -- use `{ exact: true }` or scope the query

**Rule of thumb**: Use `getByText()` for assertions and content verification, not for interactive elements. Interactive elements should use `getByRole()`.

---

### Tier 4: `getByPlaceholder()` -- Inputs Without Labels

Locates by placeholder attribute value.

**Pros**
- Works when labels are missing (search bars, minimal UIs)

**Cons**
- Placeholders disappear when the user types -- poor UX foundation
- Signals missing accessibility (no label)

**Treat as a yellow flag**: If you use this, consider filing a ticket to add a proper label.

---

### Tier 5: `getByTestId()` -- Last Resort

Locates by `data-testid` attribute.

**Pros**
- Fully decoupled from user-facing text and structure
- Stable under UI redesigns

**Cons**
- Invisible to users and assistive technology
- Pollutes production markup (unless stripped in build)
- Tells you nothing about what the element looks like or does

**Use only when**: The component has no semantic role, no label, no text, and you cannot change the markup. Common cases: canvas elements, third-party widgets, complex custom components.

---

### Never Use: Raw CSS Selectors or XPath

```
// DO NOT do this
page.locator('.btn-primary');           // class names change
page.locator('#submit-btn');            // IDs are brittle
page.locator('div > span:nth-child(2)'); // structure changes break this
page.locator('xpath=//div[@class="foo"]'); // unreadable, fragile
```

If you are reaching for a CSS selector, stop. Walk back up the flowchart and find a semantic locator. If none exists, add `data-testid`.

## Real-World Examples

### 1. Buttons

```typescript
// TypeScript
// Standard button
await page.getByRole('button', { name: 'Submit' }).click();

// Icon-only button (uses aria-label)
await page.getByRole('button', { name: 'Close' }).click();

// Button inside a specific section
await page.getByRole('region', { name: 'Billing' })
  .getByRole('button', { name: 'Update' }).click();
```

```javascript
// JavaScript
// Standard button
await page.getByRole('button', { name: 'Submit' }).click();

// Icon-only button (uses aria-label)
await page.getByRole('button', { name: 'Close' }).click();

// Button inside a specific section
await page.getByRole('region', { name: 'Billing' })
  .getByRole('button', { name: 'Update' }).click();
```

---

### 2. Links

```typescript
// TypeScript
// Standard link
await page.getByRole('link', { name: 'Sign up' }).click();

// Link inside navigation
await page.getByRole('navigation')
  .getByRole('link', { name: 'Pricing' }).click();

// Link with exact match (avoid partial hits)
await page.getByRole('link', { name: 'Log in', exact: true }).click();
```

```javascript
// JavaScript
await page.getByRole('link', { name: 'Sign up' }).click();

await page.getByRole('navigation')
  .getByRole('link', { name: 'Pricing' }).click();

await page.getByRole('link', { name: 'Log in', exact: true }).click();
```

---

### 3. Text Inputs

```typescript
// TypeScript
// Input with a visible label -- preferred
await page.getByLabel('Email address').fill('user@example.com');

// When multiple textboxes exist and you need role specificity
await page.getByRole('textbox', { name: 'Email address' }).fill('user@example.com');

// Textarea
await page.getByLabel('Message').fill('Hello, world');

// Search input (role = searchbox)
await page.getByRole('searchbox', { name: 'Search' }).fill('playwright');
```

```javascript
// JavaScript
await page.getByLabel('Email address').fill('user@example.com');

await page.getByRole('textbox', { name: 'Email address' }).fill('user@example.com');

await page.getByLabel('Message').fill('Hello, world');

await page.getByRole('searchbox', { name: 'Search' }).fill('playwright');
```

---

### 4. Checkboxes and Radios

```typescript
// TypeScript
// Checkbox
await page.getByRole('checkbox', { name: 'Accept terms' }).check();

// Verify checked state
await expect(page.getByRole('checkbox', { name: 'Accept terms' })).toBeChecked();

// Radio button
await page.getByRole('radio', { name: 'Express shipping' }).check();

// Radio within a group (fieldset with legend)
await page.getByRole('group', { name: 'Shipping method' })
  .getByRole('radio', { name: 'Express' }).check();
```

```javascript
// JavaScript
await page.getByRole('checkbox', { name: 'Accept terms' }).check();

await expect(page.getByRole('checkbox', { name: 'Accept terms' })).toBeChecked();

await page.getByRole('radio', { name: 'Express shipping' }).check();

await page.getByRole('group', { name: 'Shipping method' })
  .getByRole('radio', { name: 'Express' }).check();
```

---

### 5. Dropdowns and Selects

```typescript
// TypeScript
// Native <select> element
await page.getByLabel('Country').selectOption('Canada');

// Custom combobox (ARIA combobox role)
await page.getByRole('combobox', { name: 'Country' }).click();
await page.getByRole('option', { name: 'Canada' }).click();

// Listbox pattern
await page.getByRole('combobox', { name: 'Font size' }).click();
await page.getByRole('listbox').getByRole('option', { name: '16px' }).click();
```

```javascript
// JavaScript
await page.getByLabel('Country').selectOption('Canada');

await page.getByRole('combobox', { name: 'Country' }).click();
await page.getByRole('option', { name: 'Canada' }).click();

await page.getByRole('combobox', { name: 'Font size' }).click();
await page.getByRole('listbox').getByRole('option', { name: '16px' }).click();
```

---

### 6. Headings

```typescript
// TypeScript
// Specific heading level
await expect(page.getByRole('heading', { name: 'Dashboard', level: 1 })).toBeVisible();

// Any heading with that name (when level does not matter)
await expect(page.getByRole('heading', { name: 'Recent activity' })).toBeVisible();

// Heading within a section
await page.getByRole('region', { name: 'Sidebar' })
  .getByRole('heading', { name: 'Categories' });
```

```javascript
// JavaScript
await expect(page.getByRole('heading', { name: 'Dashboard', level: 1 })).toBeVisible();

await expect(page.getByRole('heading', { name: 'Recent activity' })).toBeVisible();

await page.getByRole('region', { name: 'Sidebar' })
  .getByRole('heading', { name: 'Categories' });
```

---

### 7. Navigation Items

```typescript
// TypeScript
// Link inside the main nav
await page.getByRole('navigation')
  .getByRole('link', { name: 'Pricing' }).click();

// When there are multiple navs, narrow by aria-label
await page.getByRole('navigation', { name: 'Main menu' })
  .getByRole('link', { name: 'Pricing' }).click();

// Breadcrumb navigation
await page.getByRole('navigation', { name: 'Breadcrumb' })
  .getByRole('link', { name: 'Products' }).click();
```

```javascript
// JavaScript
await page.getByRole('navigation')
  .getByRole('link', { name: 'Pricing' }).click();

await page.getByRole('navigation', { name: 'Main menu' })
  .getByRole('link', { name: 'Pricing' }).click();

await page.getByRole('navigation', { name: 'Breadcrumb' })
  .getByRole('link', { name: 'Products' }).click();
```

---

### 8. Table Cells

```typescript
// TypeScript
// Find a cell in a specific row
await page.getByRole('row', { name: /Jane Smith/ })
  .getByRole('cell', { name: '$120.00' });

// Click an action button in a specific row
await page.getByRole('row', { name: /Jane Smith/ })
  .getByRole('button', { name: 'Edit' }).click();

// Filter rows using .filter() for complex matching
const row = page.getByRole('row').filter({ hasText: 'Pending' });
await row.getByRole('button', { name: 'Approve' }).click();

// Verify table header exists
await expect(page.getByRole('columnheader', { name: 'Status' })).toBeVisible();
```

```javascript
// JavaScript
await page.getByRole('row', { name: /Jane Smith/ })
  .getByRole('cell', { name: '$120.00' });

await page.getByRole('row', { name: /Jane Smith/ })
  .getByRole('button', { name: 'Edit' }).click();

const row = page.getByRole('row').filter({ hasText: 'Pending' });
await row.getByRole('button', { name: 'Approve' }).click();

await expect(page.getByRole('columnheader', { name: 'Status' })).toBeVisible();
```

---

### 9. Images

```typescript
// TypeScript
// Image with alt text
await expect(page.getByRole('img', { name: 'Company logo' })).toBeVisible();

// Alternative: getByAltText (same result, less preferred)
await expect(page.getByAltText('Company logo')).toBeVisible();

// Avatar image inside a card
await page.locator('article').filter({ hasText: 'Jane Smith' })
  .getByRole('img', { name: "Jane Smith's avatar" });
```

```javascript
// JavaScript
await expect(page.getByRole('img', { name: 'Company logo' })).toBeVisible();

await expect(page.getByAltText('Company logo')).toBeVisible();

await page.locator('article').filter({ hasText: 'Jane Smith' })
  .getByRole('img', { name: "Jane Smith's avatar" });
```

---

### 10. Custom Components (No ARIA Role)

```typescript
// TypeScript
// Third-party color picker with no semantic role
await page.getByTestId('color-picker').click();

// Custom drag-and-drop zone
await page.getByTestId('drop-zone').dispatchEvent('drop', { dataTransfer });

// Canvas-based chart
const chart = page.getByTestId('revenue-chart');
await expect(chart).toBeVisible();
```

```javascript
// JavaScript
await page.getByTestId('color-picker').click();

await page.getByTestId('drop-zone').dispatchEvent('drop', { dataTransfer });

const chart = page.getByTestId('revenue-chart');
await expect(chart).toBeVisible();
```

**Before reaching for `getByTestId`, ask yourself**: Can I add `role` and `aria-label` to this component instead? If yes, do that and use `getByRole()`.

---

### 11. Dynamic Lists

```typescript
// TypeScript
// Filter a list item by text
const item = page.getByRole('listitem').filter({ hasText: 'Milk' });
await item.getByRole('button', { name: 'Remove' }).click();

// Filter by a child locator
const card = page.locator('.product-card').filter({
  has: page.getByText('Out of stock'),
});
await expect(card).toHaveCount(3);

// Count items in a list
await expect(page.getByRole('listitem')).toHaveCount(5);

// Iterate over list items for complex assertions
for (const item of await page.getByRole('listitem').all()) {
  await expect(item).toContainText('$');
}
```

```javascript
// JavaScript
const item = page.getByRole('listitem').filter({ hasText: 'Milk' });
await item.getByRole('button', { name: 'Remove' }).click();

const card = page.locator('.product-card').filter({
  has: page.getByText('Out of stock'),
});
await expect(card).toHaveCount(3);

await expect(page.getByRole('listitem')).toHaveCount(5);

for (const item of await page.getByRole('listitem').all()) {
  await expect(item).toContainText('$');
}
```

---

### 12. Modals and Dialogs

```typescript
// TypeScript
// Wait for dialog to appear, then interact within it
const dialog = page.getByRole('dialog', { name: 'Confirm deletion' });
await expect(dialog).toBeVisible();
await dialog.getByRole('button', { name: 'Delete' }).click();

// Fill a form inside a dialog
const modal = page.getByRole('dialog', { name: 'Edit profile' });
await modal.getByLabel('Display name').fill('Jane');
await modal.getByRole('button', { name: 'Save' }).click();

// Verify dialog closed
await expect(dialog).toBeHidden();
```

```javascript
// JavaScript
const dialog = page.getByRole('dialog', { name: 'Confirm deletion' });
await expect(dialog).toBeVisible();
await dialog.getByRole('button', { name: 'Delete' }).click();

const modal = page.getByRole('dialog', { name: 'Edit profile' });
await modal.getByLabel('Display name').fill('Jane');
await modal.getByRole('button', { name: 'Save' }).click();

await expect(dialog).toBeHidden();
```

## Anti-Patterns to Avoid

| Anti-Pattern | Why It Fails | Use Instead |
|---|---|---|
| `page.locator('.btn-primary')` | Class names change during refactors and redesigns | `getByRole('button', { name: '...' })` |
| `page.locator('#email-input')` | IDs are implementation details, not user-visible | `getByLabel('Email')` |
| `page.locator('div > form > input:first-child')` | Any structural change breaks the selector | `getByLabel('...')` or `getByRole('textbox', { name: '...' })` |
| `page.locator('[data-testid="submit"]')` | Raw CSS for test IDs -- use the built-in method | `getByTestId('submit')` |
| `page.getByText('Submit')` for a button | Matches any element with that text, not just the button | `getByRole('button', { name: 'Submit' })` |
| `page.locator('button').nth(2)` | Index-based -- breaks when order changes | `getByRole('button', { name: '...' })` |

## Scoping Strategy: When Multiple Elements Match

When a locator matches more than one element, narrow scope rather than using `nth()`:

```typescript
// BAD: fragile index
page.getByRole('button', { name: 'Edit' }).nth(0);

// GOOD: scope to a parent section
page.getByRole('region', { name: 'Billing' })
  .getByRole('button', { name: 'Edit' });

// GOOD: scope to a table row
page.getByRole('row', { name: /Order #1234/ })
  .getByRole('button', { name: 'Edit' });

// GOOD: scope with filter
page.locator('article').filter({ hasText: 'Draft' })
  .getByRole('button', { name: 'Edit' });
```

## Related

- [Playwright Locators documentation](https://playwright.dev/docs/locators)
- [Playwright Best Practices](https://playwright.dev/docs/best-practices)
- [ARIA Roles reference (MDN)](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Roles)
