# Internationalization and Localization Testing

> **When to use**: Verifying your application works correctly across locales, languages, text directions, date/number formats, and timezones. Catches layout breaks, missing translations, and format errors before they reach international users.
> **Prerequisites**: [core/configuration.md](configuration.md), [core/locators.md](locators.md)

## Quick Reference

```typescript
// Set locale and timezone per context
const context = await browser.newContext({
  locale: 'de-DE',
  timezoneId: 'Europe/Berlin',
});

// Or in playwright.config.ts for project-level locale testing
projects: [
  { name: 'english', use: { locale: 'en-US', timezoneId: 'America/New_York' } },
  { name: 'german',  use: { locale: 'de-DE', timezoneId: 'Europe/Berlin' } },
  { name: 'arabic',  use: { locale: 'ar-SA', timezoneId: 'Asia/Riyadh' } },
],
```

## Patterns

### Setting Browser Locale

**Use when**: Testing locale-dependent rendering -- date formats, number formatting, currency, sorting, and browser-level localization.
**Avoid when**: Your app does not use the browser locale and instead relies on a user preference stored server-side.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test.describe('locale-specific formatting', () => {
  test('US locale formats dates as MM/DD/YYYY', async ({ browser }) => {
    const context = await browser.newContext({ locale: 'en-US' });
    const page = await context.newPage();
    await page.goto('/dashboard');

    // Verify date format matches US convention
    await expect(page.getByTestId('last-updated')).toHaveText(/\d{1,2}\/\d{1,2}\/\d{4}/);
    await context.close();
  });

  test('German locale formats dates as DD.MM.YYYY', async ({ browser }) => {
    const context = await browser.newContext({ locale: 'de-DE' });
    const page = await context.newPage();
    await page.goto('/dashboard');

    await expect(page.getByTestId('last-updated')).toHaveText(/\d{1,2}\.\d{1,2}\.\d{4}/);
    await context.close();
  });

  test('Japanese locale formats numbers with commas', async ({ browser }) => {
    const context = await browser.newContext({ locale: 'ja-JP' });
    const page = await context.newPage();
    await page.goto('/pricing');

    // Japanese yen: no decimal places, uses comma grouping
    await expect(page.getByTestId('price')).toHaveText(/[\d,]+円/);
    await context.close();
  });
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('German locale formats dates as DD.MM.YYYY', async ({ browser }) => {
  const context = await browser.newContext({ locale: 'de-DE' });
  const page = await context.newPage();
  await page.goto('/dashboard');

  await expect(page.getByTestId('last-updated')).toHaveText(/\d{1,2}\.\d{1,2}\.\d{4}/);
  await context.close();
});
```

### Multi-Locale Project Configuration

**Use when**: Running the full test suite across multiple locales in CI.
**Avoid when**: You only need to test a single locale or the app does not vary by locale.

**TypeScript**
```typescript
// playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  projects: [
    {
      name: 'en-US',
      use: {
        locale: 'en-US',
        timezoneId: 'America/New_York',
      },
    },
    {
      name: 'de-DE',
      use: {
        locale: 'de-DE',
        timezoneId: 'Europe/Berlin',
      },
    },
    {
      name: 'ar-SA',
      use: {
        locale: 'ar-SA',
        timezoneId: 'Asia/Riyadh',
      },
    },
    {
      name: 'ja-JP',
      use: {
        locale: 'ja-JP',
        timezoneId: 'Asia/Tokyo',
      },
    },
  ],
});
```

**JavaScript**
```javascript
// playwright.config.js
const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  projects: [
    { name: 'en-US', use: { locale: 'en-US', timezoneId: 'America/New_York' } },
    { name: 'de-DE', use: { locale: 'de-DE', timezoneId: 'Europe/Berlin' } },
    { name: 'ar-SA', use: { locale: 'ar-SA', timezoneId: 'Asia/Riyadh' } },
    { name: 'ja-JP', use: { locale: 'ja-JP', timezoneId: 'Asia/Tokyo' } },
  ],
});
```

### RTL Layout Testing

**Use when**: Your app supports right-to-left languages (Arabic, Hebrew, Persian, Urdu) and you need to verify layout direction, text alignment, and mirrored UI.
**Avoid when**: Your app has no RTL support.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test.describe('RTL layout', () => {
  test('Arabic locale renders RTL layout', async ({ browser }) => {
    const context = await browser.newContext({ locale: 'ar-SA' });
    const page = await context.newPage();
    await page.goto('/');

    // Verify the document direction
    const dir = await page.getAttribute('html', 'dir');
    expect(dir).toBe('rtl');

    // Verify navigation is right-aligned
    const nav = page.getByRole('navigation', { name: 'Main' });
    const navBox = await nav.boundingBox();
    const viewportWidth = page.viewportSize()!.width;
    // Nav should start from the right side
    expect(navBox!.x + navBox!.width).toBeGreaterThan(viewportWidth * 0.5);

    // Verify text alignment
    const heading = page.getByRole('heading', { level: 1 });
    const textAlign = await heading.evaluate((el) =>
      window.getComputedStyle(el).textAlign
    );
    expect(textAlign).toMatch(/right|start/);

    await context.close();
  });

  test('RTL layout does not cause horizontal overflow', async ({ browser }) => {
    const context = await browser.newContext({ locale: 'ar-SA' });
    const page = await context.newPage();
    await page.goto('/dashboard');

    // Check for horizontal scrollbar (content overflow)
    const hasHorizontalOverflow = await page.evaluate(() => {
      return document.documentElement.scrollWidth > document.documentElement.clientWidth;
    });
    expect(hasHorizontalOverflow).toBe(false);

    await context.close();
  });

  test('icons and directional elements are mirrored in RTL', async ({ browser }) => {
    const context = await browser.newContext({ locale: 'ar-SA' });
    const page = await context.newPage();
    await page.goto('/dashboard');

    // Back arrow should point right in RTL
    const backButton = page.getByRole('button', { name: /back|رجوع/i });
    const transform = await backButton.evaluate((el) =>
      window.getComputedStyle(el).transform
    );
    // CSS transform for horizontal flip: matrix(-1, 0, 0, 1, 0, 0) or scaleX(-1)
    // Or check the logical property direction
    expect(transform).not.toBe('none');

    await context.close();
  });
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('Arabic locale renders RTL layout', async ({ browser }) => {
  const context = await browser.newContext({ locale: 'ar-SA' });
  const page = await context.newPage();
  await page.goto('/');

  const dir = await page.getAttribute('html', 'dir');
  expect(dir).toBe('rtl');

  const hasHorizontalOverflow = await page.evaluate(() =>
    document.documentElement.scrollWidth > document.documentElement.clientWidth
  );
  expect(hasHorizontalOverflow).toBe(false);

  await context.close();
});
```

### Date, Number, and Currency Format Verification

**Use when**: Your app uses `Intl.DateTimeFormat`, `Intl.NumberFormat`, or similar locale-sensitive APIs.
**Avoid when**: Formats are hardcoded and do not depend on locale.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

const FORMAT_EXPECTATIONS = {
  'en-US': {
    date: /\d{1,2}\/\d{1,2}\/\d{4}/,            // 1/15/2025
    number: /1,234,567\.89/,                       // 1,234,567.89
    currency: /\$[\d,]+\.\d{2}/,                   // $1,234.56
  },
  'de-DE': {
    date: /\d{1,2}\.\d{1,2}\.\d{4}/,             // 15.1.2025
    number: /1\.234\.567,89/,                      // 1.234.567,89
    currency: /[\d.,]+\s?€/,                       // 1.234,56 €
  },
  'ja-JP': {
    date: /\d{4}\/\d{1,2}\/\d{1,2}/,             // 2025/1/15
    number: /1,234,567\.89/,                       // 1,234,567.89
    currency: /[¥￥][\d,]+/,                        // ¥1,235
  },
} as const;

for (const [locale, expected] of Object.entries(FORMAT_EXPECTATIONS)) {
  test.describe(`${locale} formatting`, () => {
    test(`dates match ${locale} format`, async ({ browser }) => {
      const context = await browser.newContext({ locale });
      const page = await context.newPage();
      await page.goto('/account');

      const dateText = await page.getByTestId('member-since').textContent();
      expect(dateText).toMatch(expected.date);
      await context.close();
    });

    test(`currency matches ${locale} format`, async ({ browser }) => {
      const context = await browser.newContext({ locale });
      const page = await context.newPage();
      await page.goto('/pricing');

      const priceText = await page.getByTestId('monthly-price').textContent();
      expect(priceText).toMatch(expected.currency);
      await context.close();
    });
  });
}
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

const locales = [
  { locale: 'en-US', datePattern: /\d{1,2}\/\d{1,2}\/\d{4}/, currencyPattern: /\$[\d,]+\.\d{2}/ },
  { locale: 'de-DE', datePattern: /\d{1,2}\.\d{1,2}\.\d{4}/, currencyPattern: /[\d.,]+\s?€/ },
];

for (const { locale, datePattern, currencyPattern } of locales) {
  test(`${locale} date format`, async ({ browser }) => {
    const context = await browser.newContext({ locale });
    const page = await context.newPage();
    await page.goto('/account');

    const dateText = await page.getByTestId('member-since').textContent();
    expect(dateText).toMatch(datePattern);
    await context.close();
  });
}
```

### Language Switcher Testing

**Use when**: Your app has an in-app language selector that changes the UI language without depending on browser locale.
**Avoid when**: Language is determined purely by browser locale with no user override.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('language switcher changes UI language', async ({ page }) => {
  await page.goto('/');

  // Default language
  await expect(page.getByRole('heading', { level: 1 })).toContainText('Welcome');
  await expect(page.getByRole('button', { name: 'Sign in' })).toBeVisible();

  // Switch to French
  await page.getByRole('combobox', { name: /language|langue/i }).selectOption('fr');

  // UI should update to French
  await expect(page.getByRole('heading', { level: 1 })).toContainText('Bienvenue');
  await expect(page.getByRole('button', { name: 'Se connecter' })).toBeVisible();

  // Verify language persists after navigation
  await page.getByRole('link', { name: /about|à propos/i }).click();
  await expect(page.getByRole('heading', { level: 1 })).not.toContainText('About');
});

test('language preference persists across sessions', async ({ page, context }) => {
  await page.goto('/');
  await page.getByRole('combobox', { name: /language/i }).selectOption('es');
  await expect(page.getByRole('button', { name: 'Iniciar sesión' })).toBeVisible();

  // Reload page — language should persist (cookie/localStorage)
  await page.reload();
  await expect(page.getByRole('button', { name: 'Iniciar sesión' })).toBeVisible();
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('language switcher changes UI language', async ({ page }) => {
  await page.goto('/');

  await expect(page.getByRole('heading', { level: 1 })).toContainText('Welcome');

  await page.getByRole('combobox', { name: /language/i }).selectOption('fr');

  await expect(page.getByRole('heading', { level: 1 })).toContainText('Bienvenue');
  await expect(page.getByRole('button', { name: 'Se connecter' })).toBeVisible();
});
```

### Translation Completeness Checks

**Use when**: Verifying that all visible UI strings are translated and no fallback keys leak into the UI.
**Avoid when**: You have a build-time translation validation step that already catches missing keys.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

const LANGUAGES = ['en', 'fr', 'de', 'es', 'ja'];
const PAGES_TO_CHECK = ['/', '/login', '/dashboard', '/settings', '/pricing'];

for (const lang of LANGUAGES) {
  test.describe(`${lang} translation completeness`, () => {
    for (const pagePath of PAGES_TO_CHECK) {
      test(`no missing translations on ${pagePath}`, async ({ page }) => {
        // Set language via URL param, cookie, or language switcher
        await page.goto(`${pagePath}?lang=${lang}`);

        // Check for common translation key leak patterns
        const pageText = await page.textContent('body');

        // Translation keys typically look like: key.subkey, UPPER_SNAKE_CASE, or {{key}}
        expect(pageText).not.toMatch(/\b[a-z]+\.[a-z]+\.[a-z]+\b/); // dot.notation.keys
        expect(pageText).not.toContain('{{');                          // Unresolved templates
        expect(pageText).not.toContain('}}');
        expect(pageText).not.toMatch(/\bTODO\b/i);                    // Placeholder text

        // Check for untranslated English text when in non-English locale
        if (lang !== 'en') {
          // These common English strings should be translated
          const untranslated = ['Sign in', 'Log out', 'Settings', 'Dashboard', 'Submit'];
          for (const text of untranslated) {
            const count = await page.getByText(text, { exact: true }).count();
            // Allow 0 matches (element not on page) but flag exact English matches
            if (count > 0) {
              console.warn(`Possible untranslated text "${text}" found on ${pagePath} for ${lang}`);
            }
          }
        }
      });
    }
  });
}
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

const LANGUAGES = ['en', 'fr', 'de'];
const PAGES = ['/', '/login', '/dashboard'];

for (const lang of LANGUAGES) {
  for (const pagePath of PAGES) {
    test(`${lang}: no missing translations on ${pagePath}`, async ({ page }) => {
      await page.goto(`${pagePath}?lang=${lang}`);

      const pageText = await page.textContent('body');
      expect(pageText).not.toMatch(/\b[a-z]+\.[a-z]+\.[a-z]+\b/);
      expect(pageText).not.toContain('{{');
      expect(pageText).not.toContain('}}');
    });
  }
}
```

### Timezone Testing

**Use when**: Your app displays time-sensitive data (event times, deadlines, scheduling) and you need to verify correct timezone rendering.
**Avoid when**: All times are displayed in UTC with no local conversion.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test.describe('timezone rendering', () => {
  test('event times adjust to user timezone', async ({ browser }) => {
    // Event stored as 2025-03-15T14:00:00Z (2 PM UTC)
    const contextNY = await browser.newContext({
      locale: 'en-US',
      timezoneId: 'America/New_York', // UTC-5 in March (EST)
    });
    const pageNY = await contextNY.newPage();
    await pageNY.goto('/events/123');
    // Should display 9:00 AM
    await expect(pageNY.getByTestId('event-time')).toContainText('9:00 AM');
    await contextNY.close();

    const contextTokyo = await browser.newContext({
      locale: 'en-US',
      timezoneId: 'Asia/Tokyo', // UTC+9
    });
    const pageTokyo = await contextTokyo.newPage();
    await pageTokyo.goto('/events/123');
    // Should display 11:00 PM
    await expect(pageTokyo.getByTestId('event-time')).toContainText('11:00 PM');
    await contextTokyo.close();
  });

  test('deadline displays correctly across DST boundary', async ({ browser }) => {
    const context = await browser.newContext({
      locale: 'en-US',
      timezoneId: 'America/Los_Angeles',
    });
    const page = await context.newPage();

    // Test a deadline that crosses DST (March second Sunday)
    await page.goto('/tasks?deadline=2025-03-10T07:00:00Z');
    // Before DST: UTC-8, so 11 PM on March 9
    await expect(page.getByTestId('deadline')).toContainText('Mar 9');

    await context.close();
  });
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('event times adjust to user timezone', async ({ browser }) => {
  const context = await browser.newContext({
    locale: 'en-US',
    timezoneId: 'America/New_York',
  });
  const page = await context.newPage();
  await page.goto('/events/123');
  await expect(page.getByTestId('event-time')).toContainText('9:00 AM');
  await context.close();
});
```

### Multi-Language Screenshot Comparison

**Use when**: Catching visual layout regressions caused by text expansion, RTL mirroring, or font rendering differences across locales.
**Avoid when**: Visual regression testing is handled separately and locale is not a layout risk.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

const LOCALES_TO_SCREENSHOT = [
  { locale: 'en-US', name: 'english' },
  { locale: 'de-DE', name: 'german' },     // German text is ~30% longer than English
  { locale: 'ja-JP', name: 'japanese' },    // CJK characters, different font metrics
  { locale: 'ar-SA', name: 'arabic' },      // RTL layout
];

for (const { locale, name } of LOCALES_TO_SCREENSHOT) {
  test(`visual snapshot for ${name} (${locale})`, async ({ browser }) => {
    const context = await browser.newContext({
      locale,
      viewport: { width: 1280, height: 720 },
    });
    const page = await context.newPage();
    await page.goto('/');

    // Wait for fonts and images to load
    await page.waitForLoadState('networkidle');

    await expect(page).toHaveScreenshot(`homepage-${name}.png`, {
      maxDiffPixelRatio: 0.02, // Allow 2% pixel difference for font rendering
      fullPage: true,
    });

    await context.close();
  });
}

test('long German text does not overflow buttons', async ({ browser }) => {
  const context = await browser.newContext({ locale: 'de-DE' });
  const page = await context.newPage();
  await page.goto('/dashboard');

  // Check that no button has overflowing text
  const buttons = page.getByRole('button');
  const count = await buttons.count();
  for (let i = 0; i < count; i++) {
    const button = buttons.nth(i);
    const overflow = await button.evaluate((el) => {
      const style = window.getComputedStyle(el);
      return el.scrollWidth > el.clientWidth && style.overflow !== 'hidden';
    });
    if (overflow) {
      const text = await button.textContent();
      expect(overflow, `Button "${text}" overflows in German`).toBe(false);
    }
  }

  await context.close();
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

const LOCALES = [
  { locale: 'en-US', name: 'english' },
  { locale: 'de-DE', name: 'german' },
  { locale: 'ar-SA', name: 'arabic' },
];

for (const { locale, name } of LOCALES) {
  test(`visual snapshot for ${name}`, async ({ browser }) => {
    const context = await browser.newContext({ locale, viewport: { width: 1280, height: 720 } });
    const page = await context.newPage();
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    await expect(page).toHaveScreenshot(`homepage-${name}.png`, {
      maxDiffPixelRatio: 0.02,
      fullPage: true,
    });
    await context.close();
  });
}
```

## Decision Guide

| Scenario | Approach | Why |
|---|---|---|
| Test locale-dependent formatting | Set `locale` in browser context | Playwright sets `navigator.language` and affects `Intl` APIs |
| Test app language switcher | Interact with the switcher UI directly | Tests the actual user workflow, not just browser locale |
| Test timezone rendering | Set `timezoneId` in browser context | Overrides `Date` and `Intl.DateTimeFormat` timezone |
| Catch text overflow from long translations | Visual regression + bounding box checks | German/Finnish text is 30-40% longer than English |
| Verify RTL layout | Set Arabic/Hebrew locale + assert `dir="rtl"` | Tests both browser signal and app response |
| Catch missing translations | Scan page text for key patterns (`{{`, dot notation) | Catches build/deploy issues where translation files are missing |
| Compare layouts across locales | `toHaveScreenshot` per locale with project-based config | Captures visual differences automatically |
| Test DST edge cases | Set specific `timezoneId` + known date boundaries | DST boundaries cause the most timezone bugs |

## Anti-Patterns

| Don't Do This | Problem | Do This Instead |
|---|---|---|
| Hardcoding translated text in assertions | Breaks when translations change | Use `getByRole` with `name` regex, or test IDs for locale-independent selection |
| Testing only `en-US` | Misses RTL, text overflow, and format bugs | Test at least one LTR, one RTL, and one CJK locale |
| Setting `locale` on the page instead of context | `locale` is a context-level option, not page-level | Set locale when creating the context or in project config |
| Ignoring text expansion for German/Finnish | Buttons and labels overflow in longer languages | Use visual regression or bounding box assertions |
| Using `toHaveScreenshot` without `maxDiffPixelRatio` | Font rendering differs slightly across OS/CI | Set `maxDiffPixelRatio: 0.02` or higher for cross-platform tolerance |
| Testing timezone only in UTC | Masks timezone conversion bugs | Test with at least 3 timezones: UTC-negative, UTC, UTC-positive |
| Relying on browser locale for app language | Many apps use server-side or cookie-based language | Test via the app's own language switching mechanism |
| Not testing DST boundaries | Time displayed can be off by 1 hour at transitions | Test dates near DST transitions for your target timezones |

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---|---|---|
| `locale` option has no effect | App ignores `navigator.language` and uses server-side locale | Set locale through the app's own mechanism (cookie, URL param, API) |
| Date format does not change with locale | App hardcodes date format instead of using `Intl.DateTimeFormat` | This is an app bug to fix, not a test issue |
| RTL page still renders LTR | App checks locale but does not set `dir="rtl"` | Verify the app's RTL detection logic; may need to set `Accept-Language` header |
| Visual screenshots fail across OS | Font rendering differs between macOS, Linux, Windows | Run visual tests in Docker for consistency, or increase `maxDiffPixelRatio` |
| `timezoneId` does not affect page | App uses server time, not client `Date` | Timezone testing only works for client-side date rendering |
| Translation key appears briefly then disappears | Translation files load asynchronously | Wait for `networkidle` or a specific translated element before asserting |
| Character encoding issues (garbled text) | Incorrect charset in HTML or missing font | Verify `<meta charset="utf-8">` and that CJK/Arabic fonts are available |

## Related

- [core/locators.md](locators.md) -- locator strategies that work across locales
- [core/configuration.md](configuration.md) -- project-level locale and timezone configuration
- [core/visual-regression.md](visual-regression.md) -- screenshot comparison fundamentals
- [core/clock-and-time-mocking.md](clock-and-time-mocking.md) -- mocking time for date-dependent testing
- [ci/docker-and-containers.md](../ci/docker-and-containers.md) -- consistent font rendering in CI with Docker
