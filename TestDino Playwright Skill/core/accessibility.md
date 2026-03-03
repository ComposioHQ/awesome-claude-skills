# Accessibility Testing

> **When to use**: Every project. Accessibility is not a feature — it is a quality baseline. Integrate automated checks (axe-core) into every test suite and supplement with manual keyboard/screen-reader verification for critical flows.
> **Prerequisites**: [core/configuration.md](configuration.md), [core/locators.md](locators.md)

## Quick Reference

```typescript
// Install: npm install -D @axe-core/playwright
import AxeBuilder from '@axe-core/playwright';

// Full page scan
const results = await new AxeBuilder({ page }).analyze();
expect(results.violations).toEqual([]);

// Scoped scan — only the main content area
const results = await new AxeBuilder({ page }).include('#main-content').analyze();

// WCAG AA only
const results = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa']).analyze();

// Exclude known issues during migration
const results = await new AxeBuilder({ page }).disableRules(['color-contrast']).analyze();
```

## Patterns

### axe-core/playwright Integration

**Use when**: You want automated WCAG violation detection on any page or component. This is your first line of defense and should run in every test suite.
**Avoid when**: You need to verify subjective UX quality (reading order, cognitive load, plain language). axe-core catches structural violations, not usability problems.

axe-core detects roughly 30-40% of WCAG issues automatically. That 30-40% includes the most common and egregious violations: missing alt text, broken label associations, invalid ARIA, and contrast failures. Catching these automatically frees you to spend manual effort on the harder problems.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test.describe('accessibility', () => {
  test('home page has no accessibility violations', async ({ page }) => {
    await page.goto('/');

    const results = await new AxeBuilder({ page }).analyze();

    expect(results.violations).toEqual([]);
  });

  test('dashboard has no accessibility violations after login', async ({ page }) => {
    await page.goto('/login');
    await page.getByLabel('Email').fill('user@example.com');
    await page.getByLabel('Password').fill('password123');
    await page.getByRole('button', { name: 'Sign in' }).click();
    await page.waitForURL('/dashboard');

    // Scan after the page is fully interactive
    const results = await new AxeBuilder({ page }).analyze();

    expect(results.violations).toEqual([]);
  });

  test('report violations with helpful details on failure', async ({ page }) => {
    await page.goto('/products');

    const results = await new AxeBuilder({ page }).analyze();

    // Format violations for readable test output
    const violationSummary = results.violations.map((v) => ({
      rule: v.id,
      impact: v.impact,
      description: v.description,
      nodes: v.nodes.length,
      help: v.helpUrl,
    }));

    expect(results.violations, JSON.stringify(violationSummary, null, 2)).toEqual([]);
  });
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');
const AxeBuilder = require('@axe-core/playwright').default;

test.describe('accessibility', () => {
  test('home page has no accessibility violations', async ({ page }) => {
    await page.goto('/');

    const results = await new AxeBuilder({ page }).analyze();

    expect(results.violations).toEqual([]);
  });

  test('report violations with helpful details on failure', async ({ page }) => {
    await page.goto('/products');

    const results = await new AxeBuilder({ page }).analyze();

    const violationSummary = results.violations.map((v) => ({
      rule: v.id,
      impact: v.impact,
      description: v.description,
      nodes: v.nodes.length,
      help: v.helpUrl,
    }));

    expect(results.violations, JSON.stringify(violationSummary, null, 2)).toEqual([]);
  });
});
```

### Scanning Specific Regions

**Use when**: You want to focus axe-core on a specific component (new feature, redesigned section) or exclude areas you do not control (third-party widgets, ads, embedded iframes).
**Avoid when**: You want a full-page baseline. Scan everything first, then narrow down.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test.describe('scoped accessibility scans', () => {
  test('scan only the checkout form', async ({ page }) => {
    await page.goto('/checkout');

    const results = await new AxeBuilder({ page })
      .include('#checkout-form')
      .analyze();

    expect(results.violations).toEqual([]);
  });

  test('scan page excluding third-party chat widget', async ({ page }) => {
    await page.goto('/support');

    const results = await new AxeBuilder({ page })
      .exclude('#intercom-widget')
      .exclude('.third-party-ads')
      .analyze();

    expect(results.violations).toEqual([]);
  });

  test('scan multiple specific regions', async ({ page }) => {
    await page.goto('/dashboard');

    // Include multiple areas — each is scanned independently
    const results = await new AxeBuilder({ page })
      .include('#navigation')
      .include('#main-content')
      .include('#footer')
      .exclude('.ad-banner')
      .analyze();

    expect(results.violations).toEqual([]);
  });

  test('scan a modal after it opens', async ({ page }) => {
    await page.goto('/settings');
    await page.getByRole('button', { name: 'Delete account' }).click();

    // Wait for the modal to be fully rendered
    await expect(page.getByRole('dialog', { name: 'Confirm deletion' })).toBeVisible();

    const results = await new AxeBuilder({ page })
      .include('[role="dialog"]')
      .analyze();

    expect(results.violations).toEqual([]);
  });
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');
const AxeBuilder = require('@axe-core/playwright').default;

test.describe('scoped accessibility scans', () => {
  test('scan only the checkout form', async ({ page }) => {
    await page.goto('/checkout');

    const results = await new AxeBuilder({ page })
      .include('#checkout-form')
      .analyze();

    expect(results.violations).toEqual([]);
  });

  test('scan page excluding third-party chat widget', async ({ page }) => {
    await page.goto('/support');

    const results = await new AxeBuilder({ page })
      .exclude('#intercom-widget')
      .exclude('.third-party-ads')
      .analyze();

    expect(results.violations).toEqual([]);
  });

  test('scan a modal after it opens', async ({ page }) => {
    await page.goto('/settings');
    await page.getByRole('button', { name: 'Delete account' }).click();
    await expect(page.getByRole('dialog', { name: 'Confirm deletion' })).toBeVisible();

    const results = await new AxeBuilder({ page })
      .include('[role="dialog"]')
      .analyze();

    expect(results.violations).toEqual([]);
  });
});
```

### WCAG Compliance Levels

**Use when**: Your project targets a specific WCAG compliance level (most target AA). Use tags to limit axe-core to the rules that matter for your compliance requirement.
**Avoid when**: You want the broadest possible scan. Omitting `withTags()` runs all rules, including best practices beyond WCAG.

Tag reference:
- `wcag2a` — WCAG 2.0 Level A (minimum)
- `wcag2aa` — WCAG 2.0 Level AA (standard target for most organizations)
- `wcag2aaa` — WCAG 2.0 Level AAA (strict; rarely required)
- `wcag21a`, `wcag21aa`, `wcag21aaa` — WCAG 2.1 additions
- `wcag22aa` — WCAG 2.2 additions
- `best-practice` — not WCAG, but recommended patterns

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test.describe('WCAG compliance levels', () => {
  test('meets WCAG 2.1 AA (standard compliance target)', async ({ page }) => {
    await page.goto('/');

    const results = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
      .analyze();

    expect(results.violations).toEqual([]);
  });

  test('meets WCAG 2.2 AA (latest standard)', async ({ page }) => {
    await page.goto('/');

    const results = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa'])
      .analyze();

    expect(results.violations).toEqual([]);
  });

  test('meets WCAG AAA (strict — use for government or healthcare)', async ({ page }) => {
    await page.goto('/');

    const results = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag2aaa', 'wcag21a', 'wcag21aa', 'wcag21aaa'])
      .analyze();

    expect(results.violations).toEqual([]);
  });

  test('best practices beyond WCAG', async ({ page }) => {
    await page.goto('/');

    const results = await new AxeBuilder({ page })
      .withTags(['best-practice'])
      .analyze();

    // Use soft assertion — best practices are advisory, not blocking
    expect.soft(results.violations).toEqual([]);
  });
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');
const AxeBuilder = require('@axe-core/playwright').default;

test.describe('WCAG compliance levels', () => {
  test('meets WCAG 2.1 AA (standard compliance target)', async ({ page }) => {
    await page.goto('/');

    const results = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
      .analyze();

    expect(results.violations).toEqual([]);
  });

  test('meets WCAG 2.2 AA (latest standard)', async ({ page }) => {
    await page.goto('/');

    const results = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa'])
      .analyze();

    expect(results.violations).toEqual([]);
  });
});
```

### Disabling Specific Rules

**Use when**: Migrating a legacy app to accessibility compliance incrementally. You have known violations documented in a tracking system and want the test suite to catch new regressions without failing on existing known issues.
**Avoid when**: Hiding violations you do not intend to fix. Every disabled rule should have a tracking ticket.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

// Centralize known exceptions — makes them visible and trackable
const KNOWN_ISSUES = {
  // JIRA-1234: Legacy header component, scheduled for redesign Q2
  rules: ['color-contrast'],
  // JIRA-1235: Third-party date picker has no label association
  selectors: ['#legacy-datepicker'],
};

test.describe('accessibility with known exceptions', () => {
  test('no new violations (excluding tracked known issues)', async ({ page }) => {
    await page.goto('/dashboard');

    const results = await new AxeBuilder({ page })
      .disableRules(KNOWN_ISSUES.rules)
      .exclude(KNOWN_ISSUES.selectors[0])
      .analyze();

    expect(results.violations).toEqual([]);
  });

  test('verify known issues still exist (remove when fixed)', async ({ page }) => {
    await page.goto('/dashboard');

    // Scan ONLY for the known issues to confirm they still exist
    // When this test fails (violations disappear), remove the exception
    const results = await new AxeBuilder({ page })
      .withRules(KNOWN_ISSUES.rules)
      .analyze();

    if (results.violations.length === 0) {
      console.warn(
        'Known accessibility issues appear to be fixed. ' +
        'Remove exceptions from KNOWN_ISSUES and close tracking tickets.'
      );
    }
  });
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');
const AxeBuilder = require('@axe-core/playwright').default;

const KNOWN_ISSUES = {
  rules: ['color-contrast'],
  selectors: ['#legacy-datepicker'],
};

test.describe('accessibility with known exceptions', () => {
  test('no new violations (excluding tracked known issues)', async ({ page }) => {
    await page.goto('/dashboard');

    const results = await new AxeBuilder({ page })
      .disableRules(KNOWN_ISSUES.rules)
      .exclude(KNOWN_ISSUES.selectors[0])
      .analyze();

    expect(results.violations).toEqual([]);
  });

  test('verify known issues still exist (remove when fixed)', async ({ page }) => {
    await page.goto('/dashboard');

    const results = await new AxeBuilder({ page })
      .withRules(KNOWN_ISSUES.rules)
      .analyze();

    if (results.violations.length === 0) {
      console.warn(
        'Known accessibility issues appear to be fixed. ' +
        'Remove exceptions from KNOWN_ISSUES and close tracking tickets.'
      );
    }
  });
});
```

### Keyboard Navigation Testing

**Use when**: Verifying that all interactive elements are reachable and operable via keyboard alone. This is critical for motor-impaired users and power users who navigate without a mouse.
**Avoid when**: Never skip this. Automated tools cannot fully verify keyboard navigation — this requires behavioral tests.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test.describe('keyboard navigation', () => {
  test('tab order follows logical reading order', async ({ page }) => {
    await page.goto('/login');

    // Tab through interactive elements and verify focus order
    await page.keyboard.press('Tab');
    await expect(page.getByLabel('Email')).toBeFocused();

    await page.keyboard.press('Tab');
    await expect(page.getByLabel('Password')).toBeFocused();

    await page.keyboard.press('Tab');
    await expect(page.getByRole('link', { name: 'Forgot password?' })).toBeFocused();

    await page.keyboard.press('Tab');
    await expect(page.getByRole('button', { name: 'Sign in' })).toBeFocused();

    // Verify Enter activates the focused button
    await page.getByLabel('Email').fill('user@example.com');
    await page.getByLabel('Password').fill('password123');
    await page.getByRole('button', { name: 'Sign in' }).focus();
    await page.keyboard.press('Enter');
    await page.waitForURL('/dashboard');
  });

  test('skip navigation link moves focus to main content', async ({ page }) => {
    await page.goto('/');

    // First Tab should land on the skip link (visually hidden until focused)
    await page.keyboard.press('Tab');
    const skipLink = page.getByRole('link', { name: 'Skip to main content' });
    await expect(skipLink).toBeFocused();

    // Activating the skip link moves focus past the nav
    await page.keyboard.press('Enter');
    await expect(page.locator('#main-content')).toBeFocused();
  });

  test('dropdown menu operates with keyboard', async ({ page }) => {
    await page.goto('/dashboard');

    const menuButton = page.getByRole('button', { name: 'User menu' });
    await menuButton.focus();

    // Open menu with Enter or Space
    await page.keyboard.press('Enter');
    const menu = page.getByRole('menu');
    await expect(menu).toBeVisible();

    // Arrow keys navigate menu items
    await page.keyboard.press('ArrowDown');
    await expect(page.getByRole('menuitem', { name: 'Profile' })).toBeFocused();

    await page.keyboard.press('ArrowDown');
    await expect(page.getByRole('menuitem', { name: 'Settings' })).toBeFocused();

    // Escape closes the menu and returns focus to the trigger
    await page.keyboard.press('Escape');
    await expect(menu).not.toBeVisible();
    await expect(menuButton).toBeFocused();
  });

  test('keyboard shortcuts work correctly', async ({ page }) => {
    await page.goto('/editor');

    // Ctrl+S / Cmd+S triggers save
    const modifier = process.platform === 'darwin' ? 'Meta' : 'Control';
    const saveResponse = page.waitForResponse('**/api/save');
    await page.keyboard.press(`${modifier}+s`);
    await saveResponse;

    await expect(page.getByText('Saved')).toBeVisible();
  });

  test('no keyboard traps in form navigation', async ({ page }) => {
    await page.goto('/complex-form');

    // Tab through every field — focus should never get stuck
    const interactiveElements = page.locator(
      'a[href], button, input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    const count = await interactiveElements.count();

    for (let i = 0; i < count; i++) {
      await page.keyboard.press('Tab');
      // Verify something is focused (focus did not get trapped or lost)
      const focused = page.locator(':focus');
      await expect(focused).toBeAttached();
    }
  });
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test.describe('keyboard navigation', () => {
  test('tab order follows logical reading order', async ({ page }) => {
    await page.goto('/login');

    await page.keyboard.press('Tab');
    await expect(page.getByLabel('Email')).toBeFocused();

    await page.keyboard.press('Tab');
    await expect(page.getByLabel('Password')).toBeFocused();

    await page.keyboard.press('Tab');
    await expect(page.getByRole('link', { name: 'Forgot password?' })).toBeFocused();

    await page.keyboard.press('Tab');
    await expect(page.getByRole('button', { name: 'Sign in' })).toBeFocused();
  });

  test('dropdown menu operates with keyboard', async ({ page }) => {
    await page.goto('/dashboard');

    const menuButton = page.getByRole('button', { name: 'User menu' });
    await menuButton.focus();

    await page.keyboard.press('Enter');
    const menu = page.getByRole('menu');
    await expect(menu).toBeVisible();

    await page.keyboard.press('ArrowDown');
    await expect(page.getByRole('menuitem', { name: 'Profile' })).toBeFocused();

    await page.keyboard.press('Escape');
    await expect(menu).not.toBeVisible();
    await expect(menuButton).toBeFocused();
  });

  test('no keyboard traps in form navigation', async ({ page }) => {
    await page.goto('/complex-form');

    const interactiveElements = page.locator(
      'a[href], button, input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    const count = await interactiveElements.count();

    for (let i = 0; i < count; i++) {
      await page.keyboard.press('Tab');
      const focused = page.locator(':focus');
      await expect(focused).toBeAttached();
    }
  });
});
```

### Screen Reader Testing Patterns

**Use when**: Verifying that ARIA attributes, live regions, and roles produce the correct accessible experience. You cannot run a real screen reader in CI, but you can verify the semantic structure that screen readers depend on.
**Avoid when**: You want to test actual screen reader output (use manual testing with NVDA/VoiceOver for that).

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test.describe('screen reader semantics', () => {
  test('ARIA labels provide meaningful context', async ({ page }) => {
    await page.goto('/dashboard');

    // Navigation landmarks must have distinct labels
    const mainNav = page.getByRole('navigation', { name: 'Main' });
    const footerNav = page.getByRole('navigation', { name: 'Footer' });
    await expect(mainNav).toBeVisible();
    await expect(footerNav).toBeVisible();

    // Regions should have accessible names
    const mainRegion = page.getByRole('main');
    await expect(mainRegion).toBeAttached();

    // Buttons with icons must have accessible names
    const closeButton = page.getByRole('button', { name: 'Close' });
    await expect(closeButton).toBeAttached();

    // Images must have alt text (getByRole('img') only matches with accessible name)
    const logo = page.getByRole('img', { name: 'Company logo' });
    await expect(logo).toBeVisible();
  });

  test('live regions announce dynamic content changes', async ({ page }) => {
    await page.goto('/notifications');

    // Verify the live region exists before triggering content
    const statusRegion = page.locator('[aria-live="polite"]');
    await expect(statusRegion).toBeAttached();

    // Trigger an action that updates the live region
    await page.getByRole('button', { name: 'Save' }).click();

    // Verify the live region received the update
    await expect(statusRegion).toHaveText('Changes saved successfully');
  });

  test('alert live region announces errors immediately', async ({ page }) => {
    await page.goto('/checkout');

    // aria-live="assertive" or role="alert" interrupts the screen reader
    await page.getByRole('button', { name: 'Place order' }).click();

    const alert = page.getByRole('alert');
    await expect(alert).toBeVisible();
    await expect(alert).toHaveText('Payment method is required');
  });

  test('expandable sections announce their state', async ({ page }) => {
    await page.goto('/faq');

    const faqButton = page.getByRole('button', { name: 'How do I reset my password?' });

    // aria-expanded should reflect the current state
    await expect(faqButton).toHaveAttribute('aria-expanded', 'false');

    await faqButton.click();
    await expect(faqButton).toHaveAttribute('aria-expanded', 'true');

    // The controlled panel should be visible
    const panel = page.locator(`#${await faqButton.getAttribute('aria-controls')}`);
    await expect(panel).toBeVisible();
  });

  test('page headings form a logical hierarchy', async ({ page }) => {
    await page.goto('/about');

    // There should be exactly one h1
    await expect(page.getByRole('heading', { level: 1 })).toHaveCount(1);

    // Heading levels should not skip (h1 -> h3 without h2 is a violation)
    const headings = page.getByRole('heading');
    const count = await headings.count();
    let previousLevel = 0;

    for (let i = 0; i < count; i++) {
      const heading = headings.nth(i);
      const tagName = await heading.evaluate((el) => el.tagName.toLowerCase());
      const level = parseInt(tagName.replace('h', ''), 10);

      // Level can go up by 1 or drop to any lower level, but never skip forward
      if (level > previousLevel + 1 && previousLevel !== 0) {
        throw new Error(
          `Heading hierarchy skipped from h${previousLevel} to h${level}: "${await heading.textContent()}"`
        );
      }
      previousLevel = level;
    }
  });

  test('table has proper headers and caption', async ({ page }) => {
    await page.goto('/reports');

    const table = page.getByRole('table', { name: 'Monthly revenue' });
    await expect(table).toBeVisible();

    // Column headers
    const columnHeaders = table.getByRole('columnheader');
    await expect(columnHeaders).toHaveCount(4);
    await expect(columnHeaders.first()).toHaveText('Month');

    // Row headers (if applicable)
    const rowHeaders = table.getByRole('rowheader');
    await expect(rowHeaders.first()).toHaveText('January');
  });
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test.describe('screen reader semantics', () => {
  test('ARIA labels provide meaningful context', async ({ page }) => {
    await page.goto('/dashboard');

    const mainNav = page.getByRole('navigation', { name: 'Main' });
    const footerNav = page.getByRole('navigation', { name: 'Footer' });
    await expect(mainNav).toBeVisible();
    await expect(footerNav).toBeVisible();

    const closeButton = page.getByRole('button', { name: 'Close' });
    await expect(closeButton).toBeAttached();

    const logo = page.getByRole('img', { name: 'Company logo' });
    await expect(logo).toBeVisible();
  });

  test('live regions announce dynamic content changes', async ({ page }) => {
    await page.goto('/notifications');

    const statusRegion = page.locator('[aria-live="polite"]');
    await expect(statusRegion).toBeAttached();

    await page.getByRole('button', { name: 'Save' }).click();
    await expect(statusRegion).toHaveText('Changes saved successfully');
  });

  test('expandable sections announce their state', async ({ page }) => {
    await page.goto('/faq');

    const faqButton = page.getByRole('button', { name: 'How do I reset my password?' });
    await expect(faqButton).toHaveAttribute('aria-expanded', 'false');

    await faqButton.click();
    await expect(faqButton).toHaveAttribute('aria-expanded', 'true');
  });
});
```

### Color Contrast Verification

**Use when**: Ensuring text and UI components meet WCAG contrast ratio requirements. axe-core checks contrast automatically, but you may need explicit checks for dynamic themes, dark mode, or brand color changes.
**Avoid when**: axe-core's built-in contrast rule covers your use case. Only add explicit checks for dynamic color changes axe cannot observe in a single scan.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test.describe('color contrast', () => {
  test('light theme meets contrast requirements', async ({ page }) => {
    await page.goto('/');

    const results = await new AxeBuilder({ page })
      .withRules(['color-contrast'])
      .analyze();

    expect(results.violations).toEqual([]);
  });

  test('dark theme meets contrast requirements', async ({ page }) => {
    await page.goto('/');

    // Activate dark mode
    await page.getByRole('button', { name: 'Toggle dark mode' }).click();

    // Wait for theme transition to complete
    await expect(page.locator('html')).toHaveAttribute('data-theme', 'dark');

    const results = await new AxeBuilder({ page })
      .withRules(['color-contrast'])
      .analyze();

    expect(results.violations).toEqual([]);
  });

  test('high contrast mode meets AAA contrast requirements', async ({ page }) => {
    await page.goto('/settings/display');
    await page.getByRole('checkbox', { name: 'High contrast' }).check();

    // AAA requires 7:1 for normal text, 4.5:1 for large text
    const results = await new AxeBuilder({ page })
      .withTags(['wcag2aaa'])
      .withRules(['color-contrast'])
      .analyze();

    expect(results.violations).toEqual([]);
  });

  test('focus indicators are visible', async ({ page }) => {
    await page.goto('/');

    // Tab to an element and verify focus outline has sufficient contrast
    await page.keyboard.press('Tab');
    const focusedElement = page.locator(':focus');

    // Verify the outline is not transparent or zero-width
    const outline = await focusedElement.evaluate((el) => {
      const styles = window.getComputedStyle(el);
      return {
        outlineStyle: styles.outlineStyle,
        outlineWidth: styles.outlineWidth,
        outlineColor: styles.outlineColor,
        boxShadow: styles.boxShadow,
      };
    });

    // Focus must be visible — either outline or box-shadow
    const hasVisibleFocus =
      (outline.outlineStyle !== 'none' && outline.outlineWidth !== '0px') ||
      outline.boxShadow !== 'none';

    expect(hasVisibleFocus, 'Focused element must have a visible focus indicator').toBe(true);
  });
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');
const AxeBuilder = require('@axe-core/playwright').default;

test.describe('color contrast', () => {
  test('light theme meets contrast requirements', async ({ page }) => {
    await page.goto('/');

    const results = await new AxeBuilder({ page })
      .withRules(['color-contrast'])
      .analyze();

    expect(results.violations).toEqual([]);
  });

  test('dark theme meets contrast requirements', async ({ page }) => {
    await page.goto('/');
    await page.getByRole('button', { name: 'Toggle dark mode' }).click();
    await expect(page.locator('html')).toHaveAttribute('data-theme', 'dark');

    const results = await new AxeBuilder({ page })
      .withRules(['color-contrast'])
      .analyze();

    expect(results.violations).toEqual([]);
  });

  test('focus indicators are visible', async ({ page }) => {
    await page.goto('/');
    await page.keyboard.press('Tab');
    const focusedElement = page.locator(':focus');

    const outline = await focusedElement.evaluate((el) => {
      const styles = window.getComputedStyle(el);
      return {
        outlineStyle: styles.outlineStyle,
        outlineWidth: styles.outlineWidth,
        boxShadow: styles.boxShadow,
      };
    });

    const hasVisibleFocus =
      (outline.outlineStyle !== 'none' && outline.outlineWidth !== '0px') ||
      outline.boxShadow !== 'none';

    expect(hasVisibleFocus, 'Focused element must have a visible focus indicator').toBe(true);
  });
});
```

### Focus Trap Testing

**Use when**: Testing modals, dialogs, dropdown menus, slide-over panels, and any overlay that must trap focus within itself to prevent users from accidentally interacting with background content.
**Avoid when**: The component does not overlay content (inline expandable sections do not need focus traps).

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test.describe('focus trap', () => {
  test('modal traps focus within itself', async ({ page }) => {
    await page.goto('/settings');

    // Open the modal
    await page.getByRole('button', { name: 'Delete account' }).click();
    const dialog = page.getByRole('dialog', { name: 'Confirm deletion' });
    await expect(dialog).toBeVisible();

    // Focus should move into the dialog automatically
    const firstFocusable = dialog.getByRole('button', { name: 'Cancel' });
    await expect(firstFocusable).toBeFocused();

    // Tab should cycle within the dialog
    await page.keyboard.press('Tab');
    await expect(dialog.getByRole('button', { name: 'Delete' })).toBeFocused();

    // Tab again wraps back to the first focusable element
    await page.keyboard.press('Tab');
    await expect(dialog.getByRole('button', { name: 'Cancel' })).toBeFocused();

    // Shift+Tab wraps to the last focusable element
    await page.keyboard.press('Shift+Tab');
    await expect(dialog.getByRole('button', { name: 'Delete' })).toBeFocused();

    // Escape closes the dialog
    await page.keyboard.press('Escape');
    await expect(dialog).not.toBeVisible();

    // Focus returns to the trigger element
    await expect(page.getByRole('button', { name: 'Delete account' })).toBeFocused();
  });

  test('dropdown menu traps focus and returns it on close', async ({ page }) => {
    await page.goto('/dashboard');

    const trigger = page.getByRole('button', { name: 'Actions' });
    await trigger.click();

    const menu = page.getByRole('menu');
    await expect(menu).toBeVisible();

    // First menu item receives focus
    await expect(page.getByRole('menuitem').first()).toBeFocused();

    // ArrowDown moves through items
    await page.keyboard.press('ArrowDown');
    await expect(page.getByRole('menuitem').nth(1)).toBeFocused();

    // Escape closes and returns focus
    await page.keyboard.press('Escape');
    await expect(menu).not.toBeVisible();
    await expect(trigger).toBeFocused();
  });

  test('background content is inert when modal is open', async ({ page }) => {
    await page.goto('/settings');
    await page.getByRole('button', { name: 'Delete account' }).click();

    const dialog = page.getByRole('dialog');
    await expect(dialog).toBeVisible();

    // Background content should have aria-hidden="true" or be inert
    const mainContent = page.locator('main');
    const isHidden = await mainContent.evaluate((el) => {
      return el.getAttribute('aria-hidden') === 'true' || el.hasAttribute('inert');
    });

    expect(isHidden, 'Background content must be hidden from assistive technology').toBe(true);
  });
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test.describe('focus trap', () => {
  test('modal traps focus within itself', async ({ page }) => {
    await page.goto('/settings');
    await page.getByRole('button', { name: 'Delete account' }).click();

    const dialog = page.getByRole('dialog', { name: 'Confirm deletion' });
    await expect(dialog).toBeVisible();

    const firstFocusable = dialog.getByRole('button', { name: 'Cancel' });
    await expect(firstFocusable).toBeFocused();

    await page.keyboard.press('Tab');
    await expect(dialog.getByRole('button', { name: 'Delete' })).toBeFocused();

    await page.keyboard.press('Tab');
    await expect(dialog.getByRole('button', { name: 'Cancel' })).toBeFocused();

    await page.keyboard.press('Escape');
    await expect(dialog).not.toBeVisible();
    await expect(page.getByRole('button', { name: 'Delete account' })).toBeFocused();
  });

  test('background content is inert when modal is open', async ({ page }) => {
    await page.goto('/settings');
    await page.getByRole('button', { name: 'Delete account' }).click();
    await expect(page.getByRole('dialog')).toBeVisible();

    const mainContent = page.locator('main');
    const isHidden = await mainContent.evaluate((el) => {
      return el.getAttribute('aria-hidden') === 'true' || el.hasAttribute('inert');
    });

    expect(isHidden, 'Background content must be hidden from assistive technology').toBe(true);
  });
});
```

### Accessible Forms

**Use when**: Testing that forms are usable by assistive technology. Every form field must have an associated label, error messages must be programmatically linked, and required fields must be announced.
**Avoid when**: Never skip this for any form.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test.describe('accessible forms', () => {
  test('all form fields have associated labels', async ({ page }) => {
    await page.goto('/register');

    // Every input should be reachable via getByLabel (proves label association)
    await expect(page.getByLabel('First name')).toBeVisible();
    await expect(page.getByLabel('Last name')).toBeVisible();
    await expect(page.getByLabel('Email')).toBeVisible();
    await expect(page.getByLabel('Password')).toBeVisible();

    // Run axe to catch any we missed
    const results = await new AxeBuilder({ page })
      .include('form')
      .withRules(['label', 'label-title-only'])
      .analyze();

    expect(results.violations).toEqual([]);
  });

  test('required fields are announced to screen readers', async ({ page }) => {
    await page.goto('/register');

    // Required fields must have aria-required="true" or the required attribute
    const emailField = page.getByLabel('Email');
    const hasRequired = await emailField.evaluate((el) => {
      return el.hasAttribute('required') || el.getAttribute('aria-required') === 'true';
    });

    expect(hasRequired, 'Email field must be marked as required').toBe(true);
  });

  test('error messages are linked to their fields via aria-describedby', async ({ page }) => {
    await page.goto('/register');

    // Submit empty form to trigger validation
    await page.getByRole('button', { name: 'Create account' }).click();

    // The error message should be visible
    const errorMessage = page.getByText('Email is required');
    await expect(errorMessage).toBeVisible();

    // The error must be linked to the field via aria-describedby
    const emailField = page.getByLabel('Email');
    const describedBy = await emailField.getAttribute('aria-describedby');
    expect(describedBy).toBeTruthy();

    // The id of the error message matches the aria-describedby value
    const errorId = await errorMessage.getAttribute('id');
    expect(describedBy).toContain(errorId);

    // The field should also indicate invalid state
    await expect(emailField).toHaveAttribute('aria-invalid', 'true');
  });

  test('form error summary is announced and links to fields', async ({ page }) => {
    await page.goto('/register');
    await page.getByRole('button', { name: 'Create account' }).click();

    // Error summary should appear with role="alert" for immediate announcement
    const errorSummary = page.getByRole('alert');
    await expect(errorSummary).toBeVisible();
    await expect(errorSummary).toContainText('Please fix the following errors');

    // Error summary links should move focus to the corresponding field
    await errorSummary.getByRole('link', { name: 'Email is required' }).click();
    await expect(page.getByLabel('Email')).toBeFocused();
  });

  test('autocomplete attributes are set for common fields', async ({ page }) => {
    await page.goto('/checkout');

    // Autocomplete helps password managers and assistive tech fill forms
    await expect(page.getByLabel('Full name')).toHaveAttribute('autocomplete', 'name');
    await expect(page.getByLabel('Email')).toHaveAttribute('autocomplete', 'email');
    await expect(page.getByLabel('Street address')).toHaveAttribute('autocomplete', 'street-address');
    await expect(page.getByLabel('Postal code')).toHaveAttribute('autocomplete', 'postal-code');
  });

  test('fieldsets group related fields with legends', async ({ page }) => {
    await page.goto('/checkout');

    // Related fields should be grouped in fieldsets with legends
    const shippingGroup = page.getByRole('group', { name: 'Shipping address' });
    await expect(shippingGroup).toBeVisible();
    await expect(shippingGroup.getByLabel('Street address')).toBeVisible();

    const billingGroup = page.getByRole('group', { name: 'Billing address' });
    await expect(billingGroup).toBeVisible();
  });
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');
const AxeBuilder = require('@axe-core/playwright').default;

test.describe('accessible forms', () => {
  test('all form fields have associated labels', async ({ page }) => {
    await page.goto('/register');

    await expect(page.getByLabel('First name')).toBeVisible();
    await expect(page.getByLabel('Last name')).toBeVisible();
    await expect(page.getByLabel('Email')).toBeVisible();
    await expect(page.getByLabel('Password')).toBeVisible();

    const results = await new AxeBuilder({ page })
      .include('form')
      .withRules(['label', 'label-title-only'])
      .analyze();

    expect(results.violations).toEqual([]);
  });

  test('error messages are linked to their fields via aria-describedby', async ({ page }) => {
    await page.goto('/register');
    await page.getByRole('button', { name: 'Create account' }).click();

    const errorMessage = page.getByText('Email is required');
    await expect(errorMessage).toBeVisible();

    const emailField = page.getByLabel('Email');
    const describedBy = await emailField.getAttribute('aria-describedby');
    expect(describedBy).toBeTruthy();

    const errorId = await errorMessage.getAttribute('id');
    expect(describedBy).toContain(errorId);

    await expect(emailField).toHaveAttribute('aria-invalid', 'true');
  });

  test('autocomplete attributes are set for common fields', async ({ page }) => {
    await page.goto('/checkout');

    await expect(page.getByLabel('Full name')).toHaveAttribute('autocomplete', 'name');
    await expect(page.getByLabel('Email')).toHaveAttribute('autocomplete', 'email');
    await expect(page.getByLabel('Street address')).toHaveAttribute('autocomplete', 'street-address');
  });
});
```

### Accessibility in CI

**Use when**: You want accessibility violations to fail builds, preventing regressions from reaching production. Every team should gate their CI pipeline on accessibility.
**Avoid when**: Never. If you only run accessibility checks locally, they will be skipped.

**TypeScript**
```typescript
// playwright.config.ts — dedicated accessibility project
import { defineConfig } from '@playwright/test';

export default defineConfig({
  projects: [
    {
      name: 'accessibility',
      testMatch: '**/*.a11y.spec.ts',
      use: {
        browserName: 'chromium', // axe-core works best with Chromium
      },
    },
    {
      name: 'e2e-chromium',
      testMatch: '**/*.spec.ts',
      testIgnore: '**/*.a11y.spec.ts',
      use: { browserName: 'chromium' },
    },
  ],
});
```

```typescript
// tests/pages.a11y.spec.ts — scan all critical pages
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

const PAGES_TO_SCAN = [
  { name: 'Home', path: '/' },
  { name: 'Login', path: '/login' },
  { name: 'Register', path: '/register' },
  { name: 'Dashboard', path: '/dashboard' },
  { name: 'Products', path: '/products' },
  { name: 'Checkout', path: '/checkout' },
  { name: 'Contact', path: '/contact' },
];

for (const { name, path } of PAGES_TO_SCAN) {
  test(`${name} page (${path}) has no WCAG AA violations`, async ({ page }) => {
    await page.goto(path);

    const results = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
      .analyze();

    // Attach violation details to the test report
    await test.info().attach('accessibility-scan-results', {
      body: JSON.stringify(results.violations, null, 2),
      contentType: 'application/json',
    });

    expect(results.violations).toEqual([]);
  });
}
```

```typescript
// tests/helpers/a11y-fixture.ts — reusable axe-core fixture
import { test as base, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

type A11yFixtures = {
  makeAxeBuilder: () => AxeBuilder;
};

export const test = base.extend<A11yFixtures>({
  makeAxeBuilder: async ({ page }, use) => {
    const makeAxeBuilder = () =>
      new AxeBuilder({ page })
        .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa']);
    await use(makeAxeBuilder);
  },
});

export { expect };
```

```typescript
// tests/dashboard.a11y.spec.ts — using the fixture
import { test, expect } from './helpers/a11y-fixture';

test('dashboard has no violations after data loads', async ({ page, makeAxeBuilder }) => {
  await page.goto('/dashboard');
  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();

  const results = await makeAxeBuilder().analyze();

  await test.info().attach('a11y-results', {
    body: JSON.stringify(results.violations, null, 2),
    contentType: 'application/json',
  });

  expect(results.violations).toEqual([]);
});
```

**JavaScript**
```javascript
// playwright.config.js
const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  projects: [
    {
      name: 'accessibility',
      testMatch: '**/*.a11y.spec.js',
      use: { browserName: 'chromium' },
    },
    {
      name: 'e2e-chromium',
      testMatch: '**/*.spec.js',
      testIgnore: '**/*.a11y.spec.js',
      use: { browserName: 'chromium' },
    },
  ],
});
```

```javascript
// tests/pages.a11y.spec.js
const { test, expect } = require('@playwright/test');
const AxeBuilder = require('@axe-core/playwright').default;

const PAGES_TO_SCAN = [
  { name: 'Home', path: '/' },
  { name: 'Login', path: '/login' },
  { name: 'Dashboard', path: '/dashboard' },
  { name: 'Products', path: '/products' },
];

for (const { name, path } of PAGES_TO_SCAN) {
  test(`${name} page (${path}) has no WCAG AA violations`, async ({ page }) => {
    await page.goto(path);

    const results = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
      .analyze();

    await test.info().attach('accessibility-scan-results', {
      body: JSON.stringify(results.violations, null, 2),
      contentType: 'application/json',
    });

    expect(results.violations).toEqual([]);
  });
}
```

**GitHub Actions integration:**

```yaml
# .github/workflows/accessibility.yml
name: Accessibility Tests
on: [push, pull_request]

jobs:
  accessibility:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - run: npm ci
      - run: npx playwright install --with-deps chromium

      - name: Run accessibility tests
        run: npx playwright test --project=accessibility

      - name: Upload accessibility report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: accessibility-report
          path: playwright-report/
          retention-days: 30
```

## Decision Guide

| What to Check | Automated (axe-core) | Manual (Keyboard/Screen Reader) | Why |
|---|---|---|---|
| Missing alt text | Yes | No | axe-core detects this reliably |
| Color contrast ratios | Yes | No | Computed automatically from CSS |
| Missing form labels | Yes | No | Detects missing `<label>` and aria associations |
| Invalid ARIA attributes | Yes | No | Validates against WAI-ARIA spec |
| Duplicate IDs | Yes | No | DOM analysis |
| Tab order / logical flow | No | Yes | Requires understanding of page layout and user intent |
| Focus management in modals | Partial (axe checks `aria-hidden`) | Yes | Focus trapping behavior requires behavioral testing |
| Screen reader UX quality | No | Yes | Whether announcements are helpful is subjective |
| Cognitive load / readability | No | Yes | Cannot be automated — requires human judgment |
| Touch target size (mobile) | Yes (WCAG 2.2) | Yes | axe checks minimum size; real-device feel needs manual testing |
| Dynamic content announcements | No | Yes | Live region behavior depends on timing and screen reader |
| Keyboard shortcut conflicts | No | Yes | Requires knowing OS/browser/AT shortcuts |
| Reading order vs visual order | No | Yes | CSS reordering (flexbox `order`, grid) can break this |
| Error recovery flow | No | Yes | Whether error guidance is understandable requires human judgment |
| Video captions / audio descriptions | Partial (checks `<track>`) | Yes | Quality of captions must be verified manually |

**Rule of thumb**: Automate everything axe-core can catch (run it in CI on every page), then spend your manual testing budget on keyboard navigation, focus management, and screen reader announcements for your most critical user flows.

## Anti-Patterns

| Don't Do This | Problem | Do This Instead |
|---|---|---|
| Only test with axe-core | Catches ~30-40% of WCAG issues. Misses keyboard navigation, focus management, reading order, and UX quality. | Combine axe-core with keyboard navigation tests and periodic manual screen reader audits |
| Ignore keyboard navigation | ~8% of users rely on keyboard-only navigation. Inaccessible keyboard UX blocks real users. | Test Tab order, Enter/Space activation, Escape to close, and arrow key navigation for every interactive component |
| Skip focus management in modals | Users Tab into background content behind the modal, lose context, or cannot close the dialog. | Test focus trap, Escape to close, and focus return to trigger element |
| Test accessibility once | Regressions creep in with every PR. A passing audit today means nothing next sprint. | Run axe-core in CI on every build; schedule quarterly manual audits |
| Use `tabindex` > 0 | Overrides natural tab order, creating unpredictable navigation. Extremely difficult to maintain. | Use `tabindex="0"` to make elements focusable and `tabindex="-1"` for programmatic focus; never use positive values |
| Rely on `title` attribute for accessibility | Screen readers handle `title` inconsistently — many ignore it. | Use `aria-label`, `aria-labelledby`, or visible text labels |
| Add `role="button"` to `<div>` without keyboard support | Creates a "button" that only works with a mouse. Screen reader announces it as a button, but Enter/Space does nothing. | Use `<button>` elements. If you must use a `<div>`, add `tabindex="0"`, `role="button"`, and `keydown` handlers for Enter and Space |
| Hide content with `display: none` and expect screen readers to read it | `display: none` hides content from everyone, including assistive technology. | Use `.sr-only` / visually-hidden CSS pattern to hide visually while keeping content accessible |
| Use `aria-label` on non-interactive `<div>` or `<span>` | `aria-label` is ignored on elements without a role. Screen readers will not announce it. | Add an appropriate role (`role="region"`) or use `aria-labelledby` pointing to a visible heading |
| Test only the happy path | Missing error states, empty states, and loading states that may have different accessibility characteristics. | Test forms with validation errors, empty search results, loading skeletons, and timeout states |
| Disable `color-contrast` rule permanently | Users with low vision cannot read your content. | Fix the contrast. If migrating, track exceptions with tickets and set a deadline |

## Troubleshooting

### axe-core reports no violations but screen reader experience is poor

**Cause**: axe-core tests the structural HTML/ARIA correctness, not the quality of the user experience. An element can have a technically valid `aria-label` that is unhelpful ("button", "click here", "x").

**Fix**: Audit your most critical flows with a real screen reader (VoiceOver on macOS: Cmd+F5; NVDA on Windows: free download). Listen to the announcements and ask: would a user who cannot see the screen understand what to do?

### "color-contrast" violation on elements that look fine

**Cause**: axe-core computes contrast against the actual background, which may involve overlapping elements, gradients, or background images. The computed background may differ from what you see.

**Fix**:
- Inspect the element in DevTools: check the computed background color including any overlapping elements.
- For text on images/gradients, add a semi-transparent background behind the text.
- If axe reports a false positive (rare), verify with a manual contrast checker and use `disableRules` with a documented justification.

### Focus is lost after a dynamic content change

**Cause**: When an element is removed from the DOM (closing a modal, deleting a list item, navigating a SPA), focus falls back to `<body>`, leaving keyboard users stranded.

**Fix**:
```typescript
// After closing a modal, return focus to the trigger
await page.getByRole('button', { name: 'Close' }).click();
await expect(page.getByRole('button', { name: 'Open modal' })).toBeFocused();

// After deleting an item, move focus to the next item or a logical landmark
await page.getByRole('button', { name: 'Delete item 3' }).click();
await expect(page.getByRole('listitem').nth(2)).toBeFocused(); // next item
```

### axe-core scan returns incomplete results (not violations)

**Cause**: `results.incomplete` contains checks axe could not determine automatically. These are not failures — they are items that need manual review. Common for color contrast on complex backgrounds.

**Fix**:
```typescript
const results = await new AxeBuilder({ page }).analyze();

// Log incomplete checks for manual review
if (results.incomplete.length > 0) {
  console.log('Needs manual review:', results.incomplete.map((i) => i.id));
}

// Still fail on definite violations
expect(results.violations).toEqual([]);
```

### Tab order test fails intermittently

**Cause**: Focus behavior depends on the page being fully loaded and interactive. Animations, lazy-loaded content, or auto-focus scripts can interfere.

**Fix**:
```typescript
// Wait for the page to be fully interactive before testing tab order
await page.goto('/login');
await expect(page.getByLabel('Email')).toBeVisible();

// Click the body first to ensure focus starts from a known position
await page.locator('body').click();

// Now test tab order
await page.keyboard.press('Tab');
await expect(page.getByLabel('Email')).toBeFocused();
```

## Related

- [core/locators.md](locators.md) — role-based locators align with accessibility best practices
- [core/forms-and-validation.md](forms-and-validation.md) — form interaction patterns including accessible error handling
- [ci/ci-github-actions.md](../ci/ci-github-actions.md) — CI setup for running accessibility tests
- [core/i18n-and-localization.md](i18n-and-localization.md) — accessibility considerations for multilingual apps
- [core/component-testing.md](component-testing.md) — test individual component accessibility in isolation
