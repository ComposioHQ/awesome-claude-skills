# Test Generation

> **When to use**: Generating Playwright test code from interactive CLI sessions — recording user flows, building test scaffolds, converting manual testing into automated tests.
> **Prerequisites**: [core-commands.md](core-commands.md) for basic CLI usage

## Quick Reference

```bash
# Every CLI action outputs the equivalent Playwright code
playwright-cli open https://example.com/login
playwright-cli snapshot
playwright-cli fill e1 "user@example.com"
# Output: await page.getByRole('textbox', { name: 'Email' }).fill('user@example.com');

playwright-cli fill e2 "password123"
# Output: await page.getByRole('textbox', { name: 'Password' }).fill('password123');

playwright-cli click e3
# Output: await page.getByRole('button', { name: 'Sign In' }).click();
```

## How It Works

Every action you perform with `playwright-cli` automatically generates the corresponding Playwright TypeScript code in the output. This code uses the same **role-based locators** that Playwright recommends for production tests.

The workflow:

1. **Open a page** → generates `await page.goto(url)`
2. **Take a snapshot** → see element refs and their accessible roles
3. **Interact** → each action generates one line of Playwright code
4. **Collect the code** → assemble generated lines into a complete test

## Recording a Flow

### Example: Login Flow

```bash
playwright-cli open https://example.com/login
# Ran Playwright code:
# await page.goto('https://example.com/login');

playwright-cli snapshot
# Output:
# e1 [textbox "Email"]
# e2 [textbox "Password"]
# e3 [button "Sign In"]
# e4 [link "Forgot password?"]

playwright-cli fill e1 "user@example.com"
# Ran Playwright code:
# await page.getByRole('textbox', { name: 'Email' }).fill('user@example.com');

playwright-cli fill e2 "password123"
# Ran Playwright code:
# await page.getByRole('textbox', { name: 'Password' }).fill('password123');

playwright-cli click e3
# Ran Playwright code:
# await page.getByRole('button', { name: 'Sign In' }).click();
```

### Assemble into a Test

Collect the generated code and wrap it in a Playwright test:

```typescript
import { test, expect } from '@playwright/test';

test('user can log in', async ({ page }) => {
  await page.goto('https://example.com/login');
  await page.getByRole('textbox', { name: 'Email' }).fill('user@example.com');
  await page.getByRole('textbox', { name: 'Password' }).fill('password123');
  await page.getByRole('button', { name: 'Sign In' }).click();

  // Add assertions (not generated — you add these)
  await expect(page).toHaveURL(/.*dashboard/);
  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
});
```

```javascript
const { test, expect } = require('@playwright/test');

test('user can log in', async ({ page }) => {
  await page.goto('https://example.com/login');
  await page.getByRole('textbox', { name: 'Email' }).fill('user@example.com');
  await page.getByRole('textbox', { name: 'Password' }).fill('password123');
  await page.getByRole('button', { name: 'Sign In' }).click();

  await expect(page).toHaveURL(/.*dashboard/);
  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
});
```

## Locator Strategies in Generated Code

The generated code uses Playwright's recommended locator hierarchy:

| Priority | Locator Type | Example | When used |
|----------|-------------|---------|-----------|
| 1 | Role-based | `getByRole('button', { name: 'Submit' })` | Elements with ARIA roles |
| 2 | Label-based | `getByLabel('Email')` | Form inputs with labels |
| 3 | Placeholder | `getByPlaceholder('Search...')` | Inputs with placeholder text |
| 4 | Text-based | `getByText('Welcome back')` | Static text content |
| 5 | Test ID | `getByTestId('submit-btn')` | Elements with `data-testid` |

These locators are **resilient to markup changes** — they mirror how users perceive the page rather than relying on CSS selectors or XPath.

## Recording Complex Flows

### E-Commerce Checkout

```bash
playwright-cli open https://shop.example.com

# Browse products
playwright-cli snapshot
playwright-cli click e5                # "Add to Cart" button
# await page.getByRole('button', { name: 'Add to Cart' }).click();

playwright-cli click e12               # Cart icon
# await page.getByRole('link', { name: 'Cart' }).click();

playwright-cli snapshot
playwright-cli click e3                # "Proceed to Checkout"
# await page.getByRole('button', { name: 'Proceed to Checkout' }).click();

# Shipping info
playwright-cli snapshot
playwright-cli fill e1 "Jane Doe"
# await page.getByRole('textbox', { name: 'Full Name' }).fill('Jane Doe');
playwright-cli fill e2 "123 Main St"
# await page.getByRole('textbox', { name: 'Address' }).fill('123 Main St');
playwright-cli fill e3 "Springfield"
# await page.getByRole('textbox', { name: 'City' }).fill('Springfield');
playwright-cli select e4 "IL"
# await page.getByRole('combobox', { name: 'State' }).selectOption('IL');
playwright-cli fill e5 "62701"
# await page.getByRole('textbox', { name: 'ZIP Code' }).fill('62701');
playwright-cli click e6               # "Continue to Payment"
```

### Multi-Step Wizard

```bash
playwright-cli open https://example.com/onboarding

# Step 1
playwright-cli snapshot
playwright-cli fill e1 "Acme Corp"
playwright-cli select e2 "technology"
playwright-cli click e3    # Next

# Step 2
playwright-cli snapshot
playwright-cli check e1    # Feature checkbox
playwright-cli check e3    # Another feature
playwright-cli click e5    # Next

# Step 3
playwright-cli snapshot
playwright-cli click e2    # "Complete Setup"
```

### Search with Dynamic Results

```bash
playwright-cli open https://example.com
playwright-cli snapshot

playwright-cli fill e1 "playwright testing"
# await page.getByRole('searchbox', { name: 'Search' }).fill('playwright testing');

playwright-cli press Enter
# await page.keyboard.press('Enter');

playwright-cli snapshot    # See search results — new refs assigned

playwright-cli click e3    # First result
# await page.getByRole('link', { name: 'Getting Started with Playwright' }).click();
```

## Adding Assertions

Generated code captures **actions** but not **assertions**. Always add assertions manually to create meaningful tests.

### Common Assertions to Add

```typescript
// URL changed after navigation
await expect(page).toHaveURL(/.*dashboard/);
await expect(page).toHaveURL('https://example.com/success');

// Element is visible
await expect(page.getByRole('heading', { name: 'Welcome' })).toBeVisible();
await expect(page.getByText('Order confirmed')).toBeVisible();

// Element contains text
await expect(page.getByTestId('total')).toHaveText('$99.99');
await expect(page.getByRole('alert')).toContainText('saved');

// Element has specific attribute
await expect(page.getByRole('button', { name: 'Submit' })).toBeDisabled();
await expect(page.getByRole('checkbox')).toBeChecked();

// Element count
await expect(page.getByRole('listitem')).toHaveCount(5);

// Page title
await expect(page).toHaveTitle(/Dashboard/);

// Screenshot comparison
await expect(page).toHaveScreenshot('checkout.png');
```

### Where to Place Assertions

```typescript
test('complete checkout flow', async ({ page }) => {
  await page.goto('https://shop.example.com/products');

  // Action: Add item to cart
  await page.getByRole('button', { name: 'Add to Cart' }).click();

  // Assertion: Cart badge updates
  await expect(page.getByTestId('cart-count')).toHaveText('1');

  // Action: Go to cart
  await page.getByRole('link', { name: 'Cart' }).click();

  // Assertion: Correct page
  await expect(page).toHaveURL(/.*cart/);
  await expect(page.getByRole('heading', { name: 'Your Cart' })).toBeVisible();

  // Action: Proceed to checkout
  await page.getByRole('button', { name: 'Checkout' }).click();

  // Action: Fill shipping
  await page.getByRole('textbox', { name: 'Full Name' }).fill('Jane Doe');
  await page.getByRole('textbox', { name: 'Address' }).fill('123 Main St');
  await page.getByRole('button', { name: 'Place Order' }).click();

  // Assertion: Order confirmed
  await expect(page.getByText('Order confirmed')).toBeVisible();
  await expect(page.getByTestId('order-number')).toBeVisible();
});
```

## Best Practices

### 1. Explore Before Recording

Take a snapshot first to understand the page structure. Don't blindly click — know what elements are available:

```bash
playwright-cli open https://example.com
playwright-cli snapshot
# Review the elements, plan your flow, then start interacting
```

### 2. Use Semantic Locators

The generated code already prefers role-based locators. If you see CSS selectors in generated output, consider filing an issue — role-based locators are more resilient:

```typescript
// Generated (good — semantic, resilient)
await page.getByRole('button', { name: 'Submit' }).click();

// Avoid writing manually (fragile — breaks if CSS changes)
await page.locator('#submit-btn').click();
await page.locator('.btn.btn-primary').click();
```

### 3. Keep Tests Focused

One test = one user behavior. Don't record an entire session into a single test:

```typescript
// Good: Focused test
test('user can add item to cart', async ({ page }) => {
  // Just the add-to-cart flow
});

test('user can complete checkout', async ({ page }) => {
  // Just the checkout flow (use auth state to skip login)
});

// Bad: Monolith test
test('user journey', async ({ page }) => {
  // Login + browse + add to cart + checkout + verify email...
});
```

### 4. Parameterize Test Data

Replace hardcoded values from the recording with variables or test data:

```typescript
// Instead of hardcoded values from recording
test('registration', async ({ page }) => {
  const user = {
    name: 'Jane Doe',
    email: `test+${Date.now()}@example.com`,
    password: 'SecurePass123!'
  };

  await page.goto('/register');
  await page.getByRole('textbox', { name: 'Name' }).fill(user.name);
  await page.getByRole('textbox', { name: 'Email' }).fill(user.email);
  await page.getByRole('textbox', { name: 'Password' }).fill(user.password);
  await page.getByRole('button', { name: 'Create Account' }).click();

  await expect(page).toHaveURL(/.*welcome/);
});
```

### 5. Add Wait Strategies for Flaky Steps

If a recorded action depends on async content loading, add explicit waits:

```typescript
// Before clicking a dynamically loaded element
await page.waitForSelector('.results-loaded');
await page.getByRole('link', { name: 'First Result' }).click();

// Or use Playwright's auto-waiting (preferred)
await expect(page.getByRole('link', { name: 'First Result' })).toBeVisible();
await page.getByRole('link', { name: 'First Result' }).click();
```

## Tips

- **Generated code is a starting point** — always review, add assertions, and parameterize before committing to your test suite
- **Re-snapshot after dynamic changes** — refs change when the DOM updates
- **Combine with `state-save`** — record a login flow once, save state, then start all other recordings from the authenticated state
- **Use `--filename` for snapshots** — save before/after snapshots for complex flows to help write assertions later
