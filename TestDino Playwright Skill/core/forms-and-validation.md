# Forms and Validation

> **When to use**: Testing form filling, submission, validation messages, multi-step wizards, dynamic fields, and auto-complete interactions.
> **Prerequisites**: [core/locators.md](locators.md), [core/assertions-and-waiting.md](assertions-and-waiting.md)

## Quick Reference

```typescript
// Text input
await page.getByLabel('Name').fill('Jane Doe');

// Select dropdown
await page.getByLabel('Country').selectOption('US');
await page.getByLabel('Country').selectOption({ label: 'United States' });

// Checkbox and radio
await page.getByLabel('Remember me').check();
await page.getByLabel('Express shipping').click();

// Date input
await page.getByLabel('Start date').fill('2025-03-15');

// Clear a field
await page.getByLabel('Name').clear();

// Submit
await page.getByRole('button', { name: 'Submit' }).click();

// Verify validation error
await expect(page.getByText('Email is required')).toBeVisible();
```

## Patterns

### Filling Basic Form Fields

**Use when**: Testing any form with standard HTML inputs — text, email, password, number, textarea, select, checkbox, radio.
**Avoid when**: Never. This is the foundation pattern.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('fill and submit a registration form', async ({ page }) => {
  await page.goto('/register');

  // Text inputs — use fill() which clears first, not type()
  await page.getByLabel('First name').fill('Jane');
  await page.getByLabel('Last name').fill('Doe');
  await page.getByLabel('Email').fill('jane@example.com');
  await page.getByLabel('Password', { exact: true }).fill('S3cureP@ss!');
  await page.getByLabel('Confirm password').fill('S3cureP@ss!');

  // Textarea
  await page.getByLabel('Bio').fill('Software engineer with 10 years of experience.');

  // Number input
  await page.getByLabel('Age').fill('32');

  // Native <select>
  await page.getByLabel('Country').selectOption('US');

  // Select by visible label text (when value differs from display text)
  await page.getByLabel('State').selectOption({ label: 'California' });

  // Multi-select
  await page.getByLabel('Interests').selectOption(['coding', 'testing', 'devops']);

  // Checkbox — use check() not click() (idempotent: won't uncheck if already checked)
  await page.getByLabel('I agree to the terms').check();
  await expect(page.getByLabel('I agree to the terms')).toBeChecked();

  // Radio button
  await page.getByLabel('Monthly billing').check();
  await expect(page.getByLabel('Monthly billing')).toBeChecked();

  // Submit
  await page.getByRole('button', { name: 'Create account' }).click();
  await expect(page.getByRole('heading', { name: 'Welcome' })).toBeVisible();
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('fill and submit a registration form', async ({ page }) => {
  await page.goto('/register');

  await page.getByLabel('First name').fill('Jane');
  await page.getByLabel('Last name').fill('Doe');
  await page.getByLabel('Email').fill('jane@example.com');
  await page.getByLabel('Password', { exact: true }).fill('S3cureP@ss!');
  await page.getByLabel('Confirm password').fill('S3cureP@ss!');

  await page.getByLabel('Bio').fill('Software engineer with 10 years of experience.');
  await page.getByLabel('Age').fill('32');
  await page.getByLabel('Country').selectOption('US');
  await page.getByLabel('State').selectOption({ label: 'California' });
  await page.getByLabel('Interests').selectOption(['coding', 'testing', 'devops']);

  await page.getByLabel('I agree to the terms').check();
  await expect(page.getByLabel('I agree to the terms')).toBeChecked();

  await page.getByLabel('Monthly billing').check();
  await expect(page.getByLabel('Monthly billing')).toBeChecked();

  await page.getByRole('button', { name: 'Create account' }).click();
  await expect(page.getByRole('heading', { name: 'Welcome' })).toBeVisible();
});
```

### Date and Time Inputs

**Use when**: Testing native `<input type="date">`, `<input type="time">`, `<input type="datetime-local">`, or third-party date pickers.
**Avoid when**: The date picker is a simple text field with no special input type. Just use `fill()`.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('fill native date and time inputs', async ({ page }) => {
  await page.goto('/booking');

  // Native date input — use ISO format YYYY-MM-DD
  await page.getByLabel('Check-in date').fill('2025-06-15');
  await expect(page.getByLabel('Check-in date')).toHaveValue('2025-06-15');

  // Native time input — use HH:MM format
  await page.getByLabel('Arrival time').fill('14:30');

  // datetime-local — use YYYY-MM-DDTHH:MM format
  await page.getByLabel('Event start').fill('2025-06-15T09:00');
});

test('interact with a third-party date picker', async ({ page }) => {
  await page.goto('/booking');

  // Click to open the date picker
  await page.getByLabel('Departure date').click();

  // Navigate months if needed
  await page.getByRole('button', { name: 'Next month' }).click();

  // Select a specific day
  await page.getByRole('gridcell', { name: '20' }).click();

  // Verify the selected date appears in the input
  await expect(page.getByLabel('Departure date')).toHaveValue(/2025/);
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('fill native date and time inputs', async ({ page }) => {
  await page.goto('/booking');

  await page.getByLabel('Check-in date').fill('2025-06-15');
  await expect(page.getByLabel('Check-in date')).toHaveValue('2025-06-15');

  await page.getByLabel('Arrival time').fill('14:30');
  await page.getByLabel('Event start').fill('2025-06-15T09:00');
});

test('interact with a third-party date picker', async ({ page }) => {
  await page.goto('/booking');

  await page.getByLabel('Departure date').click();
  await page.getByRole('button', { name: 'Next month' }).click();
  await page.getByRole('gridcell', { name: '20' }).click();

  await expect(page.getByLabel('Departure date')).toHaveValue(/2025/);
});
```

### Required Field Validation

**Use when**: Testing that the form shows appropriate error messages when required fields are empty.
**Avoid when**: You only care about the happy path. Validation tests should complement, not replace, success path tests.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('shows validation errors for empty required fields', async ({ page }) => {
  await page.goto('/contact');

  // Submit without filling anything
  await page.getByRole('button', { name: 'Send message' }).click();

  // Verify all required field errors appear
  await expect(page.getByText('Name is required')).toBeVisible();
  await expect(page.getByText('Email is required')).toBeVisible();
  await expect(page.getByText('Message is required')).toBeVisible();

  // Verify the form was NOT submitted (still on the same page)
  await expect(page).toHaveURL(/\/contact/);
});

test('clears validation errors when fields are filled', async ({ page }) => {
  await page.goto('/contact');

  // Trigger errors
  await page.getByRole('button', { name: 'Send message' }).click();
  await expect(page.getByText('Name is required')).toBeVisible();

  // Fill the field — error should disappear
  await page.getByLabel('Name').fill('Jane Doe');

  // Use tab or click away to trigger blur validation
  await page.getByLabel('Email').focus();

  await expect(page.getByText('Name is required')).not.toBeVisible();
});

test('native HTML5 validation with required attribute', async ({ page }) => {
  await page.goto('/simple-form');

  await page.getByRole('button', { name: 'Submit' }).click();

  // Check for native validation message via the :invalid pseudo-class
  const emailInput = page.getByLabel('Email');
  const validationMessage = await emailInput.evaluate(
    (el: HTMLInputElement) => el.validationMessage
  );
  expect(validationMessage).toBeTruthy();
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('shows validation errors for empty required fields', async ({ page }) => {
  await page.goto('/contact');

  await page.getByRole('button', { name: 'Send message' }).click();

  await expect(page.getByText('Name is required')).toBeVisible();
  await expect(page.getByText('Email is required')).toBeVisible();
  await expect(page.getByText('Message is required')).toBeVisible();

  await expect(page).toHaveURL(/\/contact/);
});

test('clears validation errors when fields are filled', async ({ page }) => {
  await page.goto('/contact');

  await page.getByRole('button', { name: 'Send message' }).click();
  await expect(page.getByText('Name is required')).toBeVisible();

  await page.getByLabel('Name').fill('Jane Doe');
  await page.getByLabel('Email').focus();

  await expect(page.getByText('Name is required')).not.toBeVisible();
});

test('native HTML5 validation with required attribute', async ({ page }) => {
  await page.goto('/simple-form');

  await page.getByRole('button', { name: 'Submit' }).click();

  const emailInput = page.getByLabel('Email');
  const validationMessage = await emailInput.evaluate(
    (el) => el.validationMessage
  );
  expect(validationMessage).toBeTruthy();
});
```

### Format Validation and Custom Rules

**Use when**: Testing email format, phone number format, password strength, and business-specific validation rules.
**Avoid when**: The validation is purely server-side with no client-side feedback. Test via API instead.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('validates email format', async ({ page }) => {
  await page.goto('/register');

  const emailField = page.getByLabel('Email');

  // Invalid formats
  const invalidEmails = ['not-an-email', 'missing@', '@no-local.com', 'spaces in@email.com'];

  for (const email of invalidEmails) {
    await emailField.fill(email);
    await emailField.blur();
    await expect(page.getByText('Please enter a valid email')).toBeVisible();
  }

  // Valid format clears the error
  await emailField.fill('valid@example.com');
  await emailField.blur();
  await expect(page.getByText('Please enter a valid email')).not.toBeVisible();
});

test('validates password strength rules', async ({ page }) => {
  await page.goto('/register');

  const passwordField = page.getByLabel('Password', { exact: true });

  // Too short
  await passwordField.fill('Ab1!');
  await passwordField.blur();
  await expect(page.getByText('At least 8 characters')).toBeVisible();

  // Missing uppercase
  await passwordField.fill('abcdefg1!');
  await passwordField.blur();
  await expect(page.getByText('At least one uppercase letter')).toBeVisible();

  // Strong password — all checks pass
  await passwordField.fill('Str0ngP@ss!');
  await passwordField.blur();
  await expect(page.getByText(/At least/)).not.toBeVisible();
});

test('validates custom business rule — age range', async ({ page }) => {
  await page.goto('/insurance/quote');

  await page.getByLabel('Age').fill('15');
  await page.getByLabel('Age').blur();
  await expect(page.getByText('Must be 18 or older')).toBeVisible();

  await page.getByLabel('Age').fill('150');
  await page.getByLabel('Age').blur();
  await expect(page.getByText('Please enter a valid age')).toBeVisible();

  await page.getByLabel('Age').fill('30');
  await page.getByLabel('Age').blur();
  await expect(page.getByText(/Must be|valid age/)).not.toBeVisible();
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('validates email format', async ({ page }) => {
  await page.goto('/register');

  const emailField = page.getByLabel('Email');

  const invalidEmails = ['not-an-email', 'missing@', '@no-local.com', 'spaces in@email.com'];

  for (const email of invalidEmails) {
    await emailField.fill(email);
    await emailField.blur();
    await expect(page.getByText('Please enter a valid email')).toBeVisible();
  }

  await emailField.fill('valid@example.com');
  await emailField.blur();
  await expect(page.getByText('Please enter a valid email')).not.toBeVisible();
});

test('validates password strength rules', async ({ page }) => {
  await page.goto('/register');

  const passwordField = page.getByLabel('Password', { exact: true });

  await passwordField.fill('Ab1!');
  await passwordField.blur();
  await expect(page.getByText('At least 8 characters')).toBeVisible();

  await passwordField.fill('abcdefg1!');
  await passwordField.blur();
  await expect(page.getByText('At least one uppercase letter')).toBeVisible();

  await passwordField.fill('Str0ngP@ss!');
  await passwordField.blur();
  await expect(page.getByText(/At least/)).not.toBeVisible();
});

test('validates custom business rule — age range', async ({ page }) => {
  await page.goto('/insurance/quote');

  await page.getByLabel('Age').fill('15');
  await page.getByLabel('Age').blur();
  await expect(page.getByText('Must be 18 or older')).toBeVisible();

  await page.getByLabel('Age').fill('150');
  await page.getByLabel('Age').blur();
  await expect(page.getByText('Please enter a valid age')).toBeVisible();

  await page.getByLabel('Age').fill('30');
  await page.getByLabel('Age').blur();
  await expect(page.getByText(/Must be|valid age/)).not.toBeVisible();
});
```

### Multi-Step Forms and Wizards

**Use when**: The form spans multiple pages or steps, with next/previous navigation and per-step validation.
**Avoid when**: The form is a single page. Use the basic form filling pattern.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('complete a multi-step checkout wizard', async ({ page }) => {
  await page.goto('/checkout');

  // Step 1: Shipping
  await test.step('fill shipping information', async () => {
    await expect(page.getByRole('heading', { name: 'Shipping' })).toBeVisible();

    await page.getByLabel('Address').fill('123 Main St');
    await page.getByLabel('City').fill('Portland');
    await page.getByLabel('State').selectOption('OR');
    await page.getByLabel('ZIP code').fill('97201');

    await page.getByRole('button', { name: 'Continue' }).click();
  });

  // Step 2: Payment
  await test.step('fill payment details', async () => {
    await expect(page.getByRole('heading', { name: 'Payment' })).toBeVisible();

    await page.getByLabel('Card number').fill('4242424242424242');
    await page.getByLabel('Expiration').fill('12/28');
    await page.getByLabel('CVC').fill('123');

    await page.getByRole('button', { name: 'Continue' }).click();
  });

  // Step 3: Review
  await test.step('review and confirm order', async () => {
    await expect(page.getByRole('heading', { name: 'Review' })).toBeVisible();

    // Verify data from previous steps is shown
    await expect(page.getByText('123 Main St')).toBeVisible();
    await expect(page.getByText('ending in 4242')).toBeVisible();

    await page.getByRole('button', { name: 'Place order' }).click();
  });

  // Confirmation
  await expect(page.getByRole('heading', { name: 'Order confirmed' })).toBeVisible();
});

test('wizard validates each step before proceeding', async ({ page }) => {
  await page.goto('/checkout');

  // Try to skip step 1 without filling required fields
  await page.getByRole('button', { name: 'Continue' }).click();

  // Should stay on step 1 with validation errors
  await expect(page.getByRole('heading', { name: 'Shipping' })).toBeVisible();
  await expect(page.getByText('Address is required')).toBeVisible();
});

test('wizard supports going back without losing data', async ({ page }) => {
  await page.goto('/checkout');

  // Fill step 1
  await page.getByLabel('Address').fill('123 Main St');
  await page.getByLabel('City').fill('Portland');
  await page.getByLabel('State').selectOption('OR');
  await page.getByLabel('ZIP code').fill('97201');
  await page.getByRole('button', { name: 'Continue' }).click();

  // Go back from step 2
  await page.getByRole('button', { name: 'Back' }).click();

  // Verify step 1 data is preserved
  await expect(page.getByLabel('Address')).toHaveValue('123 Main St');
  await expect(page.getByLabel('City')).toHaveValue('Portland');
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('complete a multi-step checkout wizard', async ({ page }) => {
  await page.goto('/checkout');

  await test.step('fill shipping information', async () => {
    await expect(page.getByRole('heading', { name: 'Shipping' })).toBeVisible();

    await page.getByLabel('Address').fill('123 Main St');
    await page.getByLabel('City').fill('Portland');
    await page.getByLabel('State').selectOption('OR');
    await page.getByLabel('ZIP code').fill('97201');

    await page.getByRole('button', { name: 'Continue' }).click();
  });

  await test.step('fill payment details', async () => {
    await expect(page.getByRole('heading', { name: 'Payment' })).toBeVisible();

    await page.getByLabel('Card number').fill('4242424242424242');
    await page.getByLabel('Expiration').fill('12/28');
    await page.getByLabel('CVC').fill('123');

    await page.getByRole('button', { name: 'Continue' }).click();
  });

  await test.step('review and confirm order', async () => {
    await expect(page.getByRole('heading', { name: 'Review' })).toBeVisible();

    await expect(page.getByText('123 Main St')).toBeVisible();
    await expect(page.getByText('ending in 4242')).toBeVisible();

    await page.getByRole('button', { name: 'Place order' }).click();
  });

  await expect(page.getByRole('heading', { name: 'Order confirmed' })).toBeVisible();
});

test('wizard validates each step before proceeding', async ({ page }) => {
  await page.goto('/checkout');

  await page.getByRole('button', { name: 'Continue' }).click();

  await expect(page.getByRole('heading', { name: 'Shipping' })).toBeVisible();
  await expect(page.getByText('Address is required')).toBeVisible();
});

test('wizard supports going back without losing data', async ({ page }) => {
  await page.goto('/checkout');

  await page.getByLabel('Address').fill('123 Main St');
  await page.getByLabel('City').fill('Portland');
  await page.getByLabel('State').selectOption('OR');
  await page.getByLabel('ZIP code').fill('97201');
  await page.getByRole('button', { name: 'Continue' }).click();

  await page.getByRole('button', { name: 'Back' }).click();

  await expect(page.getByLabel('Address')).toHaveValue('123 Main St');
  await expect(page.getByLabel('City')).toHaveValue('Portland');
});
```

### Auto-Complete and Typeahead Fields

**Use when**: Testing search fields, address lookups, mention pickers, or any input that shows suggestions as the user types.
**Avoid when**: The field is a plain text input with no suggestions.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('select from auto-complete suggestions', async ({ page }) => {
  await page.goto('/search');

  const searchField = page.getByRole('combobox', { name: 'Search' });

  // Type slowly enough for suggestions to appear
  // pressSequentially simulates real keystrokes (triggers keydown/keyup/input events)
  await searchField.pressSequentially('playw', { delay: 100 });

  // Wait for the suggestion list to appear
  const suggestions = page.getByRole('listbox');
  await expect(suggestions).toBeVisible();

  // Select a specific suggestion
  await suggestions.getByRole('option', { name: 'Playwright Testing' }).click();

  // Verify the selection populated the field
  await expect(searchField).toHaveValue('Playwright Testing');
});

test('auto-complete with API-driven suggestions', async ({ page }) => {
  await page.goto('/address-form');

  const addressField = page.getByLabel('Address');
  await addressField.pressSequentially('123 Ma', { delay: 50 });

  // Wait for the API-driven suggestion list
  const responsePromise = page.waitForResponse('**/api/address-suggest*');
  await responsePromise;

  await page.getByRole('option', { name: /123 Main St/ }).click();

  // Verify dependent fields were auto-populated
  await expect(page.getByLabel('City')).toHaveValue('Portland');
  await expect(page.getByLabel('State')).toHaveValue('OR');
  await expect(page.getByLabel('ZIP code')).toHaveValue('97201');
});

test('dismiss auto-complete and use custom value', async ({ page }) => {
  await page.goto('/tags');

  const tagInput = page.getByLabel('Add tag');
  await tagInput.pressSequentially('custom-tag');

  // Dismiss suggestions with Escape
  await tagInput.press('Escape');
  await expect(page.getByRole('listbox')).not.toBeVisible();

  // Submit custom value with Enter
  await tagInput.press('Enter');
  await expect(page.getByText('custom-tag')).toBeVisible();
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('select from auto-complete suggestions', async ({ page }) => {
  await page.goto('/search');

  const searchField = page.getByRole('combobox', { name: 'Search' });
  await searchField.pressSequentially('playw', { delay: 100 });

  const suggestions = page.getByRole('listbox');
  await expect(suggestions).toBeVisible();

  await suggestions.getByRole('option', { name: 'Playwright Testing' }).click();
  await expect(searchField).toHaveValue('Playwright Testing');
});

test('auto-complete with API-driven suggestions', async ({ page }) => {
  await page.goto('/address-form');

  const addressField = page.getByLabel('Address');
  await addressField.pressSequentially('123 Ma', { delay: 50 });

  const responsePromise = page.waitForResponse('**/api/address-suggest*');
  await responsePromise;

  await page.getByRole('option', { name: /123 Main St/ }).click();

  await expect(page.getByLabel('City')).toHaveValue('Portland');
  await expect(page.getByLabel('State')).toHaveValue('OR');
  await expect(page.getByLabel('ZIP code')).toHaveValue('97201');
});

test('dismiss auto-complete and use custom value', async ({ page }) => {
  await page.goto('/tags');

  const tagInput = page.getByLabel('Add tag');
  await tagInput.pressSequentially('custom-tag');

  await tagInput.press('Escape');
  await expect(page.getByRole('listbox')).not.toBeVisible();

  await tagInput.press('Enter');
  await expect(page.getByText('custom-tag')).toBeVisible();
});
```

### Dynamic Forms — Conditional Fields

**Use when**: Form fields appear, disappear, or change based on the value of other fields.
**Avoid when**: All fields are always visible. Use the basic form filling pattern.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('conditional fields appear based on selection', async ({ page }) => {
  await page.goto('/insurance/apply');

  // Selecting "Business" shows additional fields
  await page.getByLabel('Account type').selectOption('business');

  // Wait for conditional fields to appear
  await expect(page.getByLabel('Company name')).toBeVisible();
  await expect(page.getByLabel('Tax ID')).toBeVisible();

  await page.getByLabel('Company name').fill('Acme Corp');
  await page.getByLabel('Tax ID').fill('12-3456789');

  // Switching back to "Personal" hides them
  await page.getByLabel('Account type').selectOption('personal');
  await expect(page.getByLabel('Company name')).not.toBeVisible();
  await expect(page.getByLabel('Tax ID')).not.toBeVisible();
});

test('checkbox toggles additional section', async ({ page }) => {
  await page.goto('/shipping');

  // "Different billing address" reveals billing fields
  await page.getByLabel('Use different billing address').check();

  const billingSection = page.getByRole('group', { name: 'Billing address' });
  await expect(billingSection).toBeVisible();

  await billingSection.getByLabel('Street').fill('456 Oak Ave');
  await billingSection.getByLabel('City').fill('Seattle');

  // Unchecking hides the section
  await page.getByLabel('Use different billing address').uncheck();
  await expect(billingSection).not.toBeVisible();
});

test('dependent dropdown chains', async ({ page }) => {
  await page.goto('/location-picker');

  // Country selection populates the state dropdown
  await page.getByLabel('Country').selectOption('US');

  // Wait for the dependent dropdown to be populated
  const stateDropdown = page.getByLabel('State');
  await expect(stateDropdown.getByRole('option')).not.toHaveCount(0);

  await stateDropdown.selectOption('CA');

  // State selection populates the city dropdown
  const cityDropdown = page.getByLabel('City');
  await expect(cityDropdown.getByRole('option')).not.toHaveCount(0);

  await cityDropdown.selectOption({ label: 'Los Angeles' });
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('conditional fields appear based on selection', async ({ page }) => {
  await page.goto('/insurance/apply');

  await page.getByLabel('Account type').selectOption('business');

  await expect(page.getByLabel('Company name')).toBeVisible();
  await expect(page.getByLabel('Tax ID')).toBeVisible();

  await page.getByLabel('Company name').fill('Acme Corp');
  await page.getByLabel('Tax ID').fill('12-3456789');

  await page.getByLabel('Account type').selectOption('personal');
  await expect(page.getByLabel('Company name')).not.toBeVisible();
  await expect(page.getByLabel('Tax ID')).not.toBeVisible();
});

test('checkbox toggles additional section', async ({ page }) => {
  await page.goto('/shipping');

  await page.getByLabel('Use different billing address').check();

  const billingSection = page.getByRole('group', { name: 'Billing address' });
  await expect(billingSection).toBeVisible();

  await billingSection.getByLabel('Street').fill('456 Oak Ave');
  await billingSection.getByLabel('City').fill('Seattle');

  await page.getByLabel('Use different billing address').uncheck();
  await expect(billingSection).not.toBeVisible();
});

test('dependent dropdown chains', async ({ page }) => {
  await page.goto('/location-picker');

  await page.getByLabel('Country').selectOption('US');

  const stateDropdown = page.getByLabel('State');
  await expect(stateDropdown.getByRole('option')).not.toHaveCount(0);

  await stateDropdown.selectOption('CA');

  const cityDropdown = page.getByLabel('City');
  await expect(cityDropdown.getByRole('option')).not.toHaveCount(0);

  await cityDropdown.selectOption({ label: 'Los Angeles' });
});
```

### Form Submission and Response Handling

**Use when**: Testing what happens after a form is submitted — success messages, redirects, error responses from the server, and loading states during submission.
**Avoid when**: You only care about client-side validation. Test submission separately from validation.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('successful form submission shows confirmation', async ({ page }) => {
  await page.goto('/contact');

  await page.getByLabel('Name').fill('Jane Doe');
  await page.getByLabel('Email').fill('jane@example.com');
  await page.getByLabel('Message').fill('Hello from Playwright');

  // Wait for the API response during submission
  const responsePromise = page.waitForResponse('**/api/contact');
  await page.getByRole('button', { name: 'Send message' }).click();
  const response = await responsePromise;

  expect(response.status()).toBe(200);
  await expect(page.getByText('Message sent successfully')).toBeVisible();
});

test('form submission shows server-side validation errors', async ({ page }) => {
  await page.goto('/register');

  await page.getByLabel('Email').fill('taken@example.com');
  await page.getByLabel('Password', { exact: true }).fill('ValidP@ss1');
  await page.getByRole('button', { name: 'Register' }).click();

  // Server responds with a 409 — email already taken
  await expect(page.getByText('An account with this email already exists')).toBeVisible();
});

test('form shows loading state during submission', async ({ page }) => {
  await page.goto('/contact');

  await page.getByLabel('Name').fill('Jane');
  await page.getByLabel('Email').fill('jane@example.com');
  await page.getByLabel('Message').fill('Test');

  await page.getByRole('button', { name: 'Send message' }).click();

  // Button should be disabled during submission
  await expect(page.getByRole('button', { name: /Sending/ })).toBeDisabled();

  // After completion, button returns to normal
  await expect(page.getByRole('button', { name: 'Send message' })).toBeEnabled();
});

test('form redirects after successful submission', async ({ page }) => {
  await page.goto('/login');

  await page.getByLabel('Email').fill('user@example.com');
  await page.getByLabel('Password').fill('password123');
  await page.getByRole('button', { name: 'Sign in' }).click();

  // Verify redirect
  await page.waitForURL('/dashboard');
  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('successful form submission shows confirmation', async ({ page }) => {
  await page.goto('/contact');

  await page.getByLabel('Name').fill('Jane Doe');
  await page.getByLabel('Email').fill('jane@example.com');
  await page.getByLabel('Message').fill('Hello from Playwright');

  const responsePromise = page.waitForResponse('**/api/contact');
  await page.getByRole('button', { name: 'Send message' }).click();
  const response = await responsePromise;

  expect(response.status()).toBe(200);
  await expect(page.getByText('Message sent successfully')).toBeVisible();
});

test('form submission shows server-side validation errors', async ({ page }) => {
  await page.goto('/register');

  await page.getByLabel('Email').fill('taken@example.com');
  await page.getByLabel('Password', { exact: true }).fill('ValidP@ss1');
  await page.getByRole('button', { name: 'Register' }).click();

  await expect(page.getByText('An account with this email already exists')).toBeVisible();
});

test('form shows loading state during submission', async ({ page }) => {
  await page.goto('/contact');

  await page.getByLabel('Name').fill('Jane');
  await page.getByLabel('Email').fill('jane@example.com');
  await page.getByLabel('Message').fill('Test');

  await page.getByRole('button', { name: 'Send message' }).click();

  await expect(page.getByRole('button', { name: /Sending/ })).toBeDisabled();
  await expect(page.getByRole('button', { name: 'Send message' })).toBeEnabled();
});

test('form redirects after successful submission', async ({ page }) => {
  await page.goto('/login');

  await page.getByLabel('Email').fill('user@example.com');
  await page.getByLabel('Password').fill('password123');
  await page.getByRole('button', { name: 'Sign in' }).click();

  await page.waitForURL('/dashboard');
  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
});
```

### Form Reset Testing

**Use when**: Testing "clear form" or "reset" functionality, verifying that fields return to their default values.
**Avoid when**: The form has no reset mechanism.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('reset button clears all fields to defaults', async ({ page }) => {
  await page.goto('/settings');

  // Change fields from defaults
  await page.getByLabel('Display name').fill('New Name');
  await page.getByLabel('Theme').selectOption('dark');
  await page.getByLabel('Notifications').uncheck();

  // Click reset
  await page.getByRole('button', { name: 'Reset' }).click();

  // Verify fields returned to original values
  await expect(page.getByLabel('Display name')).toHaveValue('');
  await expect(page.getByLabel('Theme')).toHaveValue('light');
  await expect(page.getByLabel('Notifications')).toBeChecked();
});

test('confirmation dialog before resetting a dirty form', async ({ page }) => {
  await page.goto('/editor');

  await page.getByLabel('Title').fill('Draft post');

  // Reset triggers a confirmation dialog
  page.on('dialog', (dialog) => dialog.accept());
  await page.getByRole('button', { name: 'Discard changes' }).click();

  await expect(page.getByLabel('Title')).toHaveValue('');
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('reset button clears all fields to defaults', async ({ page }) => {
  await page.goto('/settings');

  await page.getByLabel('Display name').fill('New Name');
  await page.getByLabel('Theme').selectOption('dark');
  await page.getByLabel('Notifications').uncheck();

  await page.getByRole('button', { name: 'Reset' }).click();

  await expect(page.getByLabel('Display name')).toHaveValue('');
  await expect(page.getByLabel('Theme')).toHaveValue('light');
  await expect(page.getByLabel('Notifications')).toBeChecked();
});

test('confirmation dialog before resetting a dirty form', async ({ page }) => {
  await page.goto('/editor');

  await page.getByLabel('Title').fill('Draft post');

  page.on('dialog', (dialog) => dialog.accept());
  await page.getByRole('button', { name: 'Discard changes' }).click();

  await expect(page.getByLabel('Title')).toHaveValue('');
});
```

## Decision Guide

| Scenario | Approach | Key API |
|---|---|---|
| Standard text input | `fill()` (clears, then types) | `page.getByLabel('Name').fill('Jane')` |
| Need keystroke events (autocomplete) | `pressSequentially()` with delay | `locator.pressSequentially('text', { delay: 100 })` |
| Native `<select>` dropdown | `selectOption()` by value or label | `locator.selectOption('US')` or `{ label: 'United States' }` |
| Custom dropdown (ARIA listbox) | Click trigger, then select option role | `getByRole('option', { name: '...' }).click()` |
| Checkbox | `check()` / `uncheck()` (idempotent) | `locator.check()` — safe to call even if already checked |
| Radio button | `check()` on the target radio | `page.getByLabel('Express').check()` |
| Date input (native) | `fill()` with ISO format | `locator.fill('2025-03-15')` |
| Date picker (third-party) | Click to open, navigate, select day | `getByRole('gridcell', { name: '15' }).click()` |
| Validation errors | Submit, then assert error text | `expect(page.getByText('Required')).toBeVisible()` |
| Multi-step wizard | `test.step()` per step, assert heading | `await test.step('Step 1', async () => { ... })` |
| Conditional/dynamic fields | Change trigger field, assert new field visibility | `expect(locator).toBeVisible()` / `.not.toBeVisible()` |
| Form submission | `waitForResponse` + click submit | Register response listener before click |
| Auto-complete | `pressSequentially()`, wait for listbox, select option | `getByRole('option', { name }).click()` |
| Form reset | Click reset, assert default values | `expect(locator).toHaveValue('')` |

## Anti-Patterns

| Don't Do This | Problem | Do This Instead |
|---|---|---|
| `await page.getByLabel('Name').type('Jane')` | `type()` appends to existing content; does not clear first | `await page.getByLabel('Name').fill('Jane')` |
| `await page.getByLabel('Agree').click()` | `click()` toggles — if already checked, it unchecks | `await page.getByLabel('Agree').check()` |
| `await page.fill('#email', 'test@test.com')` | CSS selector is fragile | `await page.getByLabel('Email').fill('test@test.com')` |
| `await page.selectOption('select', 'US')` without label | Targets first `<select>` on page; ambiguous | `await page.getByLabel('Country').selectOption('US')` |
| Testing every invalid input in one test | Test becomes huge, slow, and hard to debug | One test per validation rule or group related rules |
| `expect(await input.inputValue()).toBe('Jane')` | Resolves once — no retry. Race condition. | `await expect(input).toHaveValue('Jane')` |
| Filling fields with `page.evaluate()` | Bypasses event handlers (no `input`, `change` events fire) | Use `fill()` or `pressSequentially()` |
| Not waiting for conditional fields before filling | `fill()` fails on hidden/detached elements | `await expect(field).toBeVisible()` first |
| Hardcoding wait after selecting a dropdown | `waitForTimeout(500)` is flaky and slow | Wait for the dependent element to appear |
| Skipping server-side validation tests | Client-side validation can be bypassed | Test both client-side UX and server response |

## Troubleshooting

### `fill()` does nothing or clears but doesn't type

**Cause**: The input field uses a contenteditable div (rich text editors), not a real `<input>` or `<textarea>`.

```typescript
// Check if it is contenteditable
const isContentEditable = await page.getByTestId('editor').evaluate(
  (el) => el.getAttribute('contenteditable')
);

// For contenteditable, use pressSequentially or type
if (isContentEditable) {
  await page.getByTestId('editor').click();
  await page.getByTestId('editor').pressSequentially('Hello world');
}
```

### Date picker does not accept `fill()` value

**Cause**: Third-party date pickers often render custom UI over a hidden input. `fill()` sets the hidden input but the UI does not update.

```typescript
// Interact with the date picker UI instead
await page.getByLabel('Date').click();  // Opens the picker
await page.getByRole('button', { name: 'Next month' }).click();
await page.getByRole('gridcell', { name: '15' }).click();

// Alternatively, if the library reads from the input on change:
await page.getByLabel('Date').fill('2025-06-15');
await page.getByLabel('Date').dispatchEvent('change');
```

### `selectOption()` throws "not a <select> element"

**Cause**: The dropdown is a custom component (ARIA listbox), not a native `<select>`.

```typescript
// For custom dropdowns: click to open, then select from the listbox
await page.getByRole('combobox', { name: 'Country' }).click();
await page.getByRole('option', { name: 'United States' }).click();
```

### Validation errors do not appear after `fill()` and submit

**Cause**: The validation triggers on `blur` (focus leaving the field), but `fill()` does not trigger blur automatically.

```typescript
// Trigger blur explicitly
await page.getByLabel('Email').fill('invalid');
await page.getByLabel('Email').blur();
await expect(page.getByText('Please enter a valid email')).toBeVisible();

// Or move focus to the next field
await page.getByLabel('Password').focus();
```

## Related

- [core/locators.md](locators.md) -- locator strategies for finding form elements
- [core/assertions-and-waiting.md](assertions-and-waiting.md) -- assertion patterns for verifying form state
- [core/file-operations.md](file-operations.md) -- file upload fields in forms
- [core/error-and-edge-cases.md](error-and-edge-cases.md) -- testing form error states and edge cases
- [core/accessibility.md](accessibility.md) -- ensuring forms are accessible (label associations, ARIA attributes)
- [core/network-mocking.md](network-mocking.md) -- mocking form submission API responses
