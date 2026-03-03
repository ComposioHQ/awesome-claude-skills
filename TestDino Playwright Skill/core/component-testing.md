# Component Testing

> **When to use**: When you need to test UI components in isolation — verifying rendering, interactions, and behavior without spinning up your full application. Ideal for design systems, shared component libraries, and complex interactive widgets.
> **Prerequisites**: [core/configuration.md](configuration.md), [core/fixtures-and-hooks.md](fixtures-and-hooks.md)

## Quick Reference

```typescript
// Install for your framework:
// npm init playwright@latest -- --ct          (interactive)
// npm install -D @playwright/experimental-ct-react
// npm install -D @playwright/experimental-ct-vue
// npm install -D @playwright/experimental-ct-svelte

// Mount a component, interact, assert:
import { test, expect } from '@playwright/experimental-ct-react';
import { Button } from './Button';

test('button renders and responds to click', async ({ mount }) => {
  let clicked = false;
  const component = await mount(
    <Button label="Save" onClick={() => { clicked = true; }} />
  );
  await expect(component).toContainText('Save');
  await component.click();
  expect(clicked).toBe(true);
});
```

## Patterns

### 1. Setup and Configuration

**Use when**: Starting component testing in an existing Playwright project.
**Avoid when**: You only need full E2E tests against a running application — component testing adds build complexity that is not justified for pure integration tests.

Component testing uses a separate config file (`playwright-ct.config.ts`) and a dedicated `playwright/index.html` entry point. Playwright bundles your component with Vite under the hood.

**TypeScript**
```typescript
// playwright-ct.config.ts
import { defineConfig, devices } from '@playwright/experimental-ct-react';

export default defineConfig({
  testDir: './src',
  testMatch: '**/*.ct.tsx',
  use: {
    ctPort: 3100,
    // Vite config for component bundling
    ctViteConfig: {
      resolve: {
        alias: {
          '@': '/src',
        },
      },
    },
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
  ],
});
```

```html
<!-- playwright/index.html — entry point for component tests -->
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Component Tests</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="./index.ts"></script>
  </body>
</html>
```

```typescript
// playwright/index.ts — global styles and providers for all component tests
import '../src/styles/globals.css';
```

**JavaScript**
```javascript
// playwright-ct.config.js
const { defineConfig, devices } = require('@playwright/experimental-ct-react');

module.exports = defineConfig({
  testDir: './src',
  testMatch: '**/*.ct.jsx',
  use: {
    ctPort: 3100,
    ctViteConfig: {
      resolve: {
        alias: {
          '@': '/src',
        },
      },
    },
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
  ],
});
```

Run component tests with:
```bash
npx playwright test -c playwright-ct.config.ts
```

### 2. Mounting Components

**Use when**: You need to render a component in a real browser with full DOM, CSS, and event handling.
**Avoid when**: The component is trivial (a pure function that returns a string) — use a unit test instead.

The `mount()` fixture renders your component into a real browser page. It returns a `Locator` pointed at the mounted component root.

**TypeScript**
```typescript
import { test, expect } from '@playwright/experimental-ct-react';
import { Card } from './Card';

test('mount a component with props', async ({ mount }) => {
  const component = await mount(
    <Card title="Welcome" description="Get started with Playwright" />
  );

  await expect(component.getByRole('heading', { name: 'Welcome' })).toBeVisible();
  await expect(component.getByText('Get started with Playwright')).toBeVisible();
});

test('mount with children', async ({ mount }) => {
  const component = await mount(
    <Card title="Actions">
      <button>Click me</button>
    </Card>
  );

  await expect(component.getByRole('button', { name: 'Click me' })).toBeVisible();
});

test('update props after mount', async ({ mount }) => {
  const component = await mount(<Card title="Initial" description="First" />);
  await expect(component.getByRole('heading', { name: 'Initial' })).toBeVisible();

  // Re-render with new props
  await component.update(<Card title="Updated" description="Second" />);
  await expect(component.getByRole('heading', { name: 'Updated' })).toBeVisible();
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/experimental-ct-react');
const { Card } = require('./Card');

test('mount a component with props', async ({ mount }) => {
  const component = await mount(
    <Card title="Welcome" description="Get started with Playwright" />
  );

  await expect(component.getByRole('heading', { name: 'Welcome' })).toBeVisible();
  await expect(component.getByText('Get started with Playwright')).toBeVisible();
});

test('mount with children', async ({ mount }) => {
  const component = await mount(
    <Card title="Actions">
      <button>Click me</button>
    </Card>
  );

  await expect(component.getByRole('button', { name: 'Click me' })).toBeVisible();
});

test('update props after mount', async ({ mount }) => {
  const component = await mount(<Card title="Initial" description="First" />);
  await expect(component.getByRole('heading', { name: 'Initial' })).toBeVisible();

  await component.update(<Card title="Updated" description="Second" />);
  await expect(component.getByRole('heading', { name: 'Updated' })).toBeVisible();
});
```

### 3. Testing Interactions

**Use when**: The component has clickable elements, form inputs, keyboard handling, or hover states.
**Avoid when**: You are testing browser-level behavior (navigation, cookies) — use E2E tests for that.

Component test interactions use the same Playwright locator API as E2E tests. The `mount()` return value is a `Locator`, so all standard methods work.

**TypeScript**
```typescript
import { test, expect } from '@playwright/experimental-ct-react';
import { Counter } from './Counter';
import { SearchInput } from './SearchInput';
import { Dropdown } from './Dropdown';

test('click interactions', async ({ mount }) => {
  const component = await mount(<Counter initialCount={0} />);

  await component.getByRole('button', { name: 'Increment' }).click();
  await component.getByRole('button', { name: 'Increment' }).click();
  await expect(component.getByText('Count: 2')).toBeVisible();

  await component.getByRole('button', { name: 'Decrement' }).click();
  await expect(component.getByText('Count: 1')).toBeVisible();
});

test('typing interactions', async ({ mount }) => {
  const component = await mount(<SearchInput placeholder="Search..." />);

  const input = component.getByRole('textbox', { name: 'Search' });
  await input.fill('playwright');
  await expect(component.getByText('Showing results for: playwright')).toBeVisible();

  // Clear and type again
  await input.clear();
  await input.fill('testing');
  await expect(component.getByText('Showing results for: testing')).toBeVisible();
});

test('keyboard interactions', async ({ mount }) => {
  const component = await mount(<SearchInput placeholder="Search..." />);

  const input = component.getByRole('textbox', { name: 'Search' });
  await input.fill('playwright');
  await input.press('Enter');
  await expect(component.getByText('Searched: playwright')).toBeVisible();
});

test('select from dropdown', async ({ mount }) => {
  const component = await mount(
    <Dropdown
      label="Color"
      options={['Red', 'Green', 'Blue']}
    />
  );

  await component.getByRole('combobox', { name: 'Color' }).click();
  await component.getByRole('option', { name: 'Green' }).click();
  await expect(component.getByText('Selected: Green')).toBeVisible();
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/experimental-ct-react');
const { Counter } = require('./Counter');
const { SearchInput } = require('./SearchInput');
const { Dropdown } = require('./Dropdown');

test('click interactions', async ({ mount }) => {
  const component = await mount(<Counter initialCount={0} />);

  await component.getByRole('button', { name: 'Increment' }).click();
  await component.getByRole('button', { name: 'Increment' }).click();
  await expect(component.getByText('Count: 2')).toBeVisible();

  await component.getByRole('button', { name: 'Decrement' }).click();
  await expect(component.getByText('Count: 1')).toBeVisible();
});

test('typing interactions', async ({ mount }) => {
  const component = await mount(<SearchInput placeholder="Search..." />);

  const input = component.getByRole('textbox', { name: 'Search' });
  await input.fill('playwright');
  await expect(component.getByText('Showing results for: playwright')).toBeVisible();

  await input.clear();
  await input.fill('testing');
  await expect(component.getByText('Showing results for: testing')).toBeVisible();
});

test('keyboard interactions', async ({ mount }) => {
  const component = await mount(<SearchInput placeholder="Search..." />);

  const input = component.getByRole('textbox', { name: 'Search' });
  await input.fill('playwright');
  await input.press('Enter');
  await expect(component.getByText('Searched: playwright')).toBeVisible();
});

test('select from dropdown', async ({ mount }) => {
  const component = await mount(
    <Dropdown label="Color" options={['Red', 'Green', 'Blue']} />
  );

  await component.getByRole('combobox', { name: 'Color' }).click();
  await component.getByRole('option', { name: 'Green' }).click();
  await expect(component.getByText('Selected: Green')).toBeVisible();
});
```

### 4. Testing Props

**Use when**: You need to verify a component renders correctly with different prop combinations — states, variants, edge cases.
**Avoid when**: The prop differences are purely visual with no DOM change — use visual regression instead.

**TypeScript**
```typescript
import { test, expect } from '@playwright/experimental-ct-react';
import { Alert } from './Alert';
import { Badge } from './Badge';
import { Avatar } from './Avatar';

test('alert renders different severity levels', async ({ mount }) => {
  const success = await mount(<Alert severity="success" message="Saved!" />);
  await expect(success.getByRole('alert')).toContainText('Saved!');
  await expect(success.getByRole('alert')).toHaveAttribute('data-severity', 'success');

  const error = await mount(<Alert severity="error" message="Failed to save" />);
  await expect(error.getByRole('alert')).toContainText('Failed to save');
  await expect(error.getByRole('alert')).toHaveAttribute('data-severity', 'error');
});

test('badge renders count and caps at 99+', async ({ mount }) => {
  const low = await mount(<Badge count={5} />);
  await expect(low).toContainText('5');

  const high = await mount(<Badge count={150} />);
  await expect(high).toContainText('99+');

  const zero = await mount(<Badge count={0} />);
  await expect(zero).toBeHidden();
});

test('avatar shows initials when no image provided', async ({ mount }) => {
  const withImage = await mount(
    <Avatar src="/photo.jpg" name="Jane Doe" />
  );
  await expect(withImage.getByRole('img', { name: 'Jane Doe' })).toBeVisible();

  const withoutImage = await mount(<Avatar name="Jane Doe" />);
  await expect(withoutImage.getByText('JD')).toBeVisible();
  await expect(withoutImage.getByRole('img')).toHaveCount(0);
});

test('disabled button is not interactive', async ({ mount }) => {
  const component = await mount(
    <button disabled>Submit</button>
  );
  await expect(component.getByRole('button', { name: 'Submit' })).toBeDisabled();
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/experimental-ct-react');
const { Alert } = require('./Alert');
const { Badge } = require('./Badge');
const { Avatar } = require('./Avatar');

test('alert renders different severity levels', async ({ mount }) => {
  const success = await mount(<Alert severity="success" message="Saved!" />);
  await expect(success.getByRole('alert')).toContainText('Saved!');
  await expect(success.getByRole('alert')).toHaveAttribute('data-severity', 'success');

  const error = await mount(<Alert severity="error" message="Failed to save" />);
  await expect(error.getByRole('alert')).toContainText('Failed to save');
  await expect(error.getByRole('alert')).toHaveAttribute('data-severity', 'error');
});

test('badge renders count and caps at 99+', async ({ mount }) => {
  const low = await mount(<Badge count={5} />);
  await expect(low).toContainText('5');

  const high = await mount(<Badge count={150} />);
  await expect(high).toContainText('99+');

  const zero = await mount(<Badge count={0} />);
  await expect(zero).toBeHidden();
});

test('avatar shows initials when no image provided', async ({ mount }) => {
  const withImage = await mount(<Avatar src="/photo.jpg" name="Jane Doe" />);
  await expect(withImage.getByRole('img', { name: 'Jane Doe' })).toBeVisible();

  const withoutImage = await mount(<Avatar name="Jane Doe" />);
  await expect(withoutImage.getByText('JD')).toBeVisible();
  await expect(withoutImage.getByRole('img')).toHaveCount(0);
});

test('disabled button is not interactive', async ({ mount }) => {
  const component = await mount(<button disabled>Submit</button>);
  await expect(component.getByRole('button', { name: 'Submit' })).toBeDisabled();
});
```

### 5. Testing Events

**Use when**: A component emits events or calls callback props — form submissions, toggle changes, custom events.
**Avoid when**: You only care that something renders — use a prop/snapshot test instead.

Capture events by passing callback props to `mount()`. Use closures or arrays to collect values for assertion.

**TypeScript**
```typescript
import { test, expect } from '@playwright/experimental-ct-react';
import { Toggle } from './Toggle';
import { ContactForm } from './ContactForm';
import { TagInput } from './TagInput';

test('toggle fires onChange with new value', async ({ mount }) => {
  const events: boolean[] = [];
  const component = await mount(
    <Toggle
      label="Dark mode"
      onChange={(checked: boolean) => { events.push(checked); }}
    />
  );

  await component.getByRole('switch', { name: 'Dark mode' }).click();
  expect(events).toEqual([true]);

  await component.getByRole('switch', { name: 'Dark mode' }).click();
  expect(events).toEqual([true, false]);
});

test('form calls onSubmit with field values', async ({ mount }) => {
  let submittedData: Record<string, string> | null = null;
  const component = await mount(
    <ContactForm
      onSubmit={(data: Record<string, string>) => { submittedData = data; }}
    />
  );

  await component.getByLabel('Name').fill('Jane Doe');
  await component.getByLabel('Email').fill('jane@example.com');
  await component.getByLabel('Message').fill('Hello!');
  await component.getByRole('button', { name: 'Send' }).click();

  expect(submittedData).toEqual({
    name: 'Jane Doe',
    email: 'jane@example.com',
    message: 'Hello!',
  });
});

test('tag input fires onTagAdd and onTagRemove', async ({ mount }) => {
  const added: string[] = [];
  const removed: string[] = [];
  const component = await mount(
    <TagInput
      onTagAdd={(tag: string) => { added.push(tag); }}
      onTagRemove={(tag: string) => { removed.push(tag); }}
    />
  );

  const input = component.getByRole('textbox');
  await input.fill('playwright');
  await input.press('Enter');
  expect(added).toEqual(['playwright']);

  // Remove the tag
  await component.getByRole('button', { name: 'Remove playwright' }).click();
  expect(removed).toEqual(['playwright']);
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/experimental-ct-react');
const { Toggle } = require('./Toggle');
const { ContactForm } = require('./ContactForm');
const { TagInput } = require('./TagInput');

test('toggle fires onChange with new value', async ({ mount }) => {
  const events = [];
  const component = await mount(
    <Toggle
      label="Dark mode"
      onChange={(checked) => { events.push(checked); }}
    />
  );

  await component.getByRole('switch', { name: 'Dark mode' }).click();
  expect(events).toEqual([true]);

  await component.getByRole('switch', { name: 'Dark mode' }).click();
  expect(events).toEqual([true, false]);
});

test('form calls onSubmit with field values', async ({ mount }) => {
  let submittedData = null;
  const component = await mount(
    <ContactForm
      onSubmit={(data) => { submittedData = data; }}
    />
  );

  await component.getByLabel('Name').fill('Jane Doe');
  await component.getByLabel('Email').fill('jane@example.com');
  await component.getByLabel('Message').fill('Hello!');
  await component.getByRole('button', { name: 'Send' }).click();

  expect(submittedData).toEqual({
    name: 'Jane Doe',
    email: 'jane@example.com',
    message: 'Hello!',
  });
});

test('tag input fires onTagAdd and onTagRemove', async ({ mount }) => {
  const added = [];
  const removed = [];
  const component = await mount(
    <TagInput
      onTagAdd={(tag) => { added.push(tag); }}
      onTagRemove={(tag) => { removed.push(tag); }}
    />
  );

  const input = component.getByRole('textbox');
  await input.fill('playwright');
  await input.press('Enter');
  expect(added).toEqual(['playwright']);

  await component.getByRole('button', { name: 'Remove playwright' }).click();
  expect(removed).toEqual(['playwright']);
});
```

### 6. Testing Slots and Children

**Use when**: Your component accepts children, named slots (Vue), or render props — layout components, wrappers, modals.
**Avoid when**: The component has no slot/children API.

**TypeScript**
```typescript
import { test, expect } from '@playwright/experimental-ct-react';
import { Modal } from './Modal';
import { Accordion } from './Accordion';
import { Layout } from './Layout';

test('modal renders children in the dialog', async ({ mount }) => {
  const component = await mount(
    <Modal open={true} title="Confirm">
      <p>Are you sure you want to delete this item?</p>
      <button>Delete</button>
      <button>Cancel</button>
    </Modal>
  );

  await expect(component.getByRole('dialog', { name: 'Confirm' })).toBeVisible();
  await expect(component.getByText('Are you sure you want to delete this item?')).toBeVisible();
  await expect(component.getByRole('button', { name: 'Delete' })).toBeVisible();
  await expect(component.getByRole('button', { name: 'Cancel' })).toBeVisible();
});

test('accordion renders multiple sections', async ({ mount }) => {
  const component = await mount(
    <Accordion>
      <Accordion.Item title="Section 1">Content for section 1</Accordion.Item>
      <Accordion.Item title="Section 2">Content for section 2</Accordion.Item>
    </Accordion>
  );

  // First section collapsed by default
  await expect(component.getByText('Content for section 1')).toBeHidden();

  // Expand first section
  await component.getByRole('button', { name: 'Section 1' }).click();
  await expect(component.getByText('Content for section 1')).toBeVisible();

  // Second section remains collapsed
  await expect(component.getByText('Content for section 2')).toBeHidden();
});

test('layout component renders header and body slots', async ({ mount }) => {
  const component = await mount(
    <Layout
      header={<h1>Dashboard</h1>}
      sidebar={<nav><a href="/settings">Settings</a></nav>}
    >
      <p>Main content goes here</p>
    </Layout>
  );

  await expect(component.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
  await expect(component.getByRole('link', { name: 'Settings' })).toBeVisible();
  await expect(component.getByText('Main content goes here')).toBeVisible();
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/experimental-ct-react');
const { Modal } = require('./Modal');
const { Accordion } = require('./Accordion');
const { Layout } = require('./Layout');

test('modal renders children in the dialog', async ({ mount }) => {
  const component = await mount(
    <Modal open={true} title="Confirm">
      <p>Are you sure you want to delete this item?</p>
      <button>Delete</button>
      <button>Cancel</button>
    </Modal>
  );

  await expect(component.getByRole('dialog', { name: 'Confirm' })).toBeVisible();
  await expect(component.getByText('Are you sure you want to delete this item?')).toBeVisible();
  await expect(component.getByRole('button', { name: 'Delete' })).toBeVisible();
  await expect(component.getByRole('button', { name: 'Cancel' })).toBeVisible();
});

test('accordion renders multiple sections', async ({ mount }) => {
  const component = await mount(
    <Accordion>
      <Accordion.Item title="Section 1">Content for section 1</Accordion.Item>
      <Accordion.Item title="Section 2">Content for section 2</Accordion.Item>
    </Accordion>
  );

  await expect(component.getByText('Content for section 1')).toBeHidden();
  await component.getByRole('button', { name: 'Section 1' }).click();
  await expect(component.getByText('Content for section 1')).toBeVisible();
  await expect(component.getByText('Content for section 2')).toBeHidden();
});

test('layout component renders header and body slots', async ({ mount }) => {
  const component = await mount(
    <Layout
      header={<h1>Dashboard</h1>}
      sidebar={<nav><a href="/settings">Settings</a></nav>}
    >
      <p>Main content goes here</p>
    </Layout>
  );

  await expect(component.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
  await expect(component.getByRole('link', { name: 'Settings' })).toBeVisible();
  await expect(component.getByText('Main content goes here')).toBeVisible();
});
```

**Vue Slots Example (TypeScript)**
```typescript
import { test, expect } from '@playwright/experimental-ct-vue';
import Card from './Card.vue';

test('vue named slots', async ({ mount }) => {
  const component = await mount(Card, {
    props: { title: 'My Card' },
    slots: {
      default: '<p>Card body content</p>',
      footer: '<button>Save</button>',
    },
  });

  await expect(component.getByText('Card body content')).toBeVisible();
  await expect(component.getByRole('button', { name: 'Save' })).toBeVisible();
});
```

### 7. Providing Context (Wrappers and Providers)

**Use when**: Your components depend on React context, Vue provide/inject, or global state (theme, auth, i18n, store).
**Avoid when**: The component has no context dependencies — do not wrap unnecessarily.

Use the `playwright/index.ts` file to register global wrappers, or wrap per-test using a wrapper component.

**TypeScript**
```typescript
// playwright/index.tsx — global wrapper for ALL component tests
import '../src/styles/globals.css';
import { ThemeProvider } from '../src/providers/ThemeProvider';
import { IntlProvider } from '../src/providers/IntlProvider';

// beforeMount runs before every component is mounted
// Use it to wrap all components with global providers
import { beforeMount } from '@playwright/experimental-ct-react/hooks';

beforeMount(async ({ App }) => {
  return (
    <IntlProvider locale="en">
      <ThemeProvider theme="light">
        <App />
      </ThemeProvider>
    </IntlProvider>
  );
});
```

```typescript
// Per-test provider wrapping — for tests that need specific context
import { test, expect } from '@playwright/experimental-ct-react';
import { UserProfile } from './UserProfile';
import { AuthContext } from '../contexts/AuthContext';

// Create a test wrapper component
function AuthWrapper({ children, user }: { children: React.ReactNode; user: any }) {
  return (
    <AuthContext.Provider value={{ user, isAuthenticated: true }}>
      {children}
    </AuthContext.Provider>
  );
}

test('profile shows authenticated user info', async ({ mount }) => {
  const user = { name: 'Jane Doe', email: 'jane@example.com', role: 'admin' };

  const component = await mount(
    <AuthWrapper user={user}>
      <UserProfile />
    </AuthWrapper>
  );

  await expect(component.getByText('Jane Doe')).toBeVisible();
  await expect(component.getByText('admin')).toBeVisible();
});
```

```typescript
// Redux/Zustand store wrapping
import { test, expect } from '@playwright/experimental-ct-react';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import { cartReducer } from '../store/cartSlice';
import { CartSummary } from './CartSummary';

test('cart summary shows item count from store', async ({ mount }) => {
  const store = configureStore({
    reducer: { cart: cartReducer },
    preloadedState: {
      cart: {
        items: [
          { id: '1', name: 'Widget', quantity: 2, price: 9.99 },
          { id: '2', name: 'Gadget', quantity: 1, price: 24.99 },
        ],
      },
    },
  });

  const component = await mount(
    <Provider store={store}>
      <CartSummary />
    </Provider>
  );

  await expect(component.getByText('3 items')).toBeVisible();
  await expect(component.getByText('$44.97')).toBeVisible();
});
```

**JavaScript**
```javascript
// playwright/index.jsx — global wrapper
import '../src/styles/globals.css';
import { ThemeProvider } from '../src/providers/ThemeProvider';
import { IntlProvider } from '../src/providers/IntlProvider';
import { beforeMount } from '@playwright/experimental-ct-react/hooks';

beforeMount(async ({ App }) => {
  return (
    <IntlProvider locale="en">
      <ThemeProvider theme="light">
        <App />
      </ThemeProvider>
    </IntlProvider>
  );
});
```

```javascript
// Per-test store wrapping
const { test, expect } = require('@playwright/experimental-ct-react');
const { Provider } = require('react-redux');
const { configureStore } = require('@reduxjs/toolkit');
const { cartReducer } = require('../store/cartSlice');
const { CartSummary } = require('./CartSummary');

test('cart summary shows item count from store', async ({ mount }) => {
  const store = configureStore({
    reducer: { cart: cartReducer },
    preloadedState: {
      cart: {
        items: [
          { id: '1', name: 'Widget', quantity: 2, price: 9.99 },
          { id: '2', name: 'Gadget', quantity: 1, price: 24.99 },
        ],
      },
    },
  });

  const component = await mount(
    <Provider store={store}>
      <CartSummary />
    </Provider>
  );

  await expect(component.getByText('3 items')).toBeVisible();
  await expect(component.getByText('$44.97')).toBeVisible();
});
```

### 8. Mocking Imports

**Use when**: A component imports modules that should not run in tests — API clients, analytics, heavy third-party libraries.
**Avoid when**: You can provide the dependency via props or context instead — explicit injection is always better than import mocking.

Use the `beforeMount` hook in `playwright/index.ts` to intercept and replace modules.

**TypeScript**
```typescript
// playwright/index.tsx — mock modules globally
import { beforeMount } from '@playwright/experimental-ct-react/hooks';

beforeMount(async ({ hooksConfig }) => {
  // hooksConfig is passed from individual tests via mount options
  if (hooksConfig?.mockApi) {
    // Mock the API module before the component loads
    const apiModule = await import('../src/api/client');
    apiModule.fetchUser = async () => hooksConfig.mockUser;
    apiModule.fetchProducts = async () => hooksConfig.mockProducts;
  }
});
```

```typescript
// UserDashboard.ct.tsx
import { test, expect } from '@playwright/experimental-ct-react';
import { UserDashboard } from './UserDashboard';

test('dashboard renders with mocked API data', async ({ mount }) => {
  const component = await mount(<UserDashboard />, {
    hooksConfig: {
      mockApi: true,
      mockUser: { name: 'Jane Doe', email: 'jane@example.com' },
      mockProducts: [
        { id: '1', name: 'Widget', price: 9.99 },
        { id: '2', name: 'Gadget', price: 24.99 },
      ],
    },
  });

  await expect(component.getByText('Jane Doe')).toBeVisible();
  await expect(component.getByRole('listitem')).toHaveCount(2);
});
```

```typescript
// Alternative: mock at the network level using page.route()
import { test, expect } from '@playwright/experimental-ct-react';
import { ProductList } from './ProductList';

test('product list with network-level mocking', async ({ mount, page }) => {
  // Intercept fetch/XHR calls made by the component
  await page.route('**/api/products', (route) =>
    route.fulfill({
      json: [
        { id: '1', name: 'Widget', price: 9.99 },
        { id: '2', name: 'Gadget', price: 24.99 },
      ],
    })
  );

  const component = await mount(<ProductList />);
  await expect(component.getByRole('listitem')).toHaveCount(2);
  await expect(component.getByText('Widget')).toBeVisible();
});
```

**JavaScript**
```javascript
// playwright/index.jsx — mock modules globally
const { beforeMount } = require('@playwright/experimental-ct-react/hooks');

beforeMount(async ({ hooksConfig }) => {
  if (hooksConfig?.mockApi) {
    const apiModule = await import('../src/api/client');
    apiModule.fetchUser = async () => hooksConfig.mockUser;
    apiModule.fetchProducts = async () => hooksConfig.mockProducts;
  }
});
```

```javascript
// Alternative: network-level mocking
const { test, expect } = require('@playwright/experimental-ct-react');
const { ProductList } = require('./ProductList');

test('product list with network-level mocking', async ({ mount, page }) => {
  await page.route('**/api/products', (route) =>
    route.fulfill({
      json: [
        { id: '1', name: 'Widget', price: 9.99 },
        { id: '2', name: 'Gadget', price: 24.99 },
      ],
    })
  );

  const component = await mount(<ProductList />);
  await expect(component.getByRole('listitem')).toHaveCount(2);
  await expect(component.getByText('Widget')).toBeVisible();
});
```

### 9. Visual Component Testing

**Use when**: You need pixel-level verification of component appearance — design system components, theme variants, responsive states.
**Avoid when**: The component is purely functional with no meaningful visual output.

Component tests support `toHaveScreenshot()` just like E2E tests. This is powerful for testing individual component states without needing a full application.

**TypeScript**
```typescript
import { test, expect } from '@playwright/experimental-ct-react';
import { Button } from './Button';
import { Card } from './Card';

test('button visual variants', async ({ mount }) => {
  const primary = await mount(<Button variant="primary">Save</Button>);
  await expect(primary).toHaveScreenshot('button-primary.png');

  const secondary = await mount(<Button variant="secondary">Cancel</Button>);
  await expect(secondary).toHaveScreenshot('button-secondary.png');

  const danger = await mount(<Button variant="danger">Delete</Button>);
  await expect(danger).toHaveScreenshot('button-danger.png');
});

test('button states', async ({ mount }) => {
  const component = await mount(<Button variant="primary">Save</Button>);

  // Default state
  await expect(component).toHaveScreenshot('button-default.png');

  // Hover state
  await component.hover();
  await expect(component).toHaveScreenshot('button-hover.png');

  // Focus state
  await component.focus();
  await expect(component).toHaveScreenshot('button-focus.png');
});

test('card renders consistently', async ({ mount }) => {
  const component = await mount(
    <Card title="Product" description="A great product for testing.">
      <Button variant="primary">Buy now</Button>
    </Card>
  );

  await expect(component).toHaveScreenshot('card-with-button.png', {
    maxDiffPixelRatio: 0.01,
  });
});

test('responsive component at different widths', async ({ mount, page }) => {
  const component = await mount(<Card title="Responsive" description="Adapts to width" />);

  await page.setViewportSize({ width: 1200, height: 800 });
  await expect(component).toHaveScreenshot('card-desktop.png');

  await page.setViewportSize({ width: 375, height: 667 });
  await expect(component).toHaveScreenshot('card-mobile.png');
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/experimental-ct-react');
const { Button } = require('./Button');
const { Card } = require('./Card');

test('button visual variants', async ({ mount }) => {
  const primary = await mount(<Button variant="primary">Save</Button>);
  await expect(primary).toHaveScreenshot('button-primary.png');

  const secondary = await mount(<Button variant="secondary">Cancel</Button>);
  await expect(secondary).toHaveScreenshot('button-secondary.png');

  const danger = await mount(<Button variant="danger">Delete</Button>);
  await expect(danger).toHaveScreenshot('button-danger.png');
});

test('button states', async ({ mount }) => {
  const component = await mount(<Button variant="primary">Save</Button>);

  await expect(component).toHaveScreenshot('button-default.png');

  await component.hover();
  await expect(component).toHaveScreenshot('button-hover.png');

  await component.focus();
  await expect(component).toHaveScreenshot('button-focus.png');
});

test('responsive component at different widths', async ({ mount, page }) => {
  const component = await mount(<Card title="Responsive" description="Adapts to width" />);

  await page.setViewportSize({ width: 1200, height: 800 });
  await expect(component).toHaveScreenshot('card-desktop.png');

  await page.setViewportSize({ width: 375, height: 667 });
  await expect(component).toHaveScreenshot('card-mobile.png');
});
```

### 10. Component Test vs E2E Test

**Use when**: Deciding whether to write a component test, an E2E test, or both for a piece of UI.
**Avoid when**: You already have a clear testing strategy for your project.

The core distinction: component tests verify **how a component behaves in isolation**, while E2E tests verify **how the whole system works together**. They complement each other.

**TypeScript — Component test (isolated behavior)**
```typescript
// Button.ct.tsx — tests the Button component in isolation
import { test, expect } from '@playwright/experimental-ct-react';
import { Button } from './Button';

test('button shows loading spinner when loading prop is true', async ({ mount }) => {
  const component = await mount(<Button loading={true}>Save</Button>);

  await expect(component.getByRole('button', { name: 'Save' })).toBeDisabled();
  await expect(component.getByRole('progressbar')).toBeVisible();
  await expect(component.getByText('Save')).toBeVisible();
});

test('button calls onClick when clicked', async ({ mount }) => {
  let clicked = false;
  const component = await mount(
    <Button onClick={() => { clicked = true; }}>Save</Button>
  );

  await component.click();
  expect(clicked).toBe(true);
});
```

```typescript
// checkout.spec.ts — E2E test verifying the full flow
import { test, expect } from '@playwright/test';

test('complete checkout flow', async ({ page }) => {
  await page.goto('/products');
  await page.getByRole('button', { name: 'Add to cart' }).first().click();
  await page.getByRole('link', { name: 'Cart' }).click();
  await page.getByRole('button', { name: 'Checkout' }).click();

  // Fill shipping form
  await page.getByLabel('Address').fill('123 Main St');
  await page.getByLabel('City').fill('Springfield');
  await page.getByRole('button', { name: 'Continue to payment' }).click();

  // The Save button's loading state is tested in the component test.
  // Here we test the real user flow end-to-end.
  await page.getByRole('button', { name: 'Place order' }).click();
  await expect(page.getByRole('heading', { name: 'Order confirmed' })).toBeVisible();
});
```

**JavaScript — Component test (isolated behavior)**
```javascript
// Button.ct.jsx
const { test, expect } = require('@playwright/experimental-ct-react');
const { Button } = require('./Button');

test('button shows loading spinner when loading prop is true', async ({ mount }) => {
  const component = await mount(<Button loading={true}>Save</Button>);

  await expect(component.getByRole('button', { name: 'Save' })).toBeDisabled();
  await expect(component.getByRole('progressbar')).toBeVisible();
});

test('button calls onClick when clicked', async ({ mount }) => {
  let clicked = false;
  const component = await mount(
    <Button onClick={() => { clicked = true; }}>Save</Button>
  );

  await component.click();
  expect(clicked).toBe(true);
});
```

```javascript
// checkout.spec.js — E2E test
const { test, expect } = require('@playwright/test');

test('complete checkout flow', async ({ page }) => {
  await page.goto('/products');
  await page.getByRole('button', { name: 'Add to cart' }).first().click();
  await page.getByRole('link', { name: 'Cart' }).click();
  await page.getByRole('button', { name: 'Checkout' }).click();

  await page.getByLabel('Address').fill('123 Main St');
  await page.getByLabel('City').fill('Springfield');
  await page.getByRole('button', { name: 'Continue to payment' }).click();

  await page.getByRole('button', { name: 'Place order' }).click();
  await expect(page.getByRole('heading', { name: 'Order confirmed' })).toBeVisible();
});
```

## Decision Guide

| UI Element | Component Test | E2E Test | Unit Test |
|---|---|---|---|
| **Button** (variants, states, loading) | Yes — test all visual variants, disabled state, loading state, click handlers | Only as part of a larger flow | No — needs real DOM for styling and accessibility |
| **Form field** (validation, masking) | Yes — test validation messages, input masking, error states in isolation | Yes — test the full form submission flow with backend | Validate-only logic (regex, format functions) |
| **Modal/Dialog** (open, close, content) | Yes — test open/close behavior, focus trap, content rendering | Yes — test the trigger flow that opens the modal | No — needs real DOM |
| **Data table** (sorting, filtering, pagination) | Yes — test sort, filter, pagination with mock data | Yes — test with real API data and URL sync | Pure sort/filter logic on arrays |
| **Navigation/Menu** | Partially — test dropdown behavior, active states | Yes — test actual route changes and page loads | No |
| **Full page** (dashboard, settings) | No — too much context required; defeats isolation purpose | Yes — this is what E2E tests are for | No |
| **Layout** (sidebar, header, grid) | Yes — test responsive behavior, slot rendering | Only if layout affects user flows (e.g., mobile nav) | No |
| **Chart/Graph** | Yes — visual regression of rendered output | Only if charts are part of a critical flow | Data transformation logic only |
| **Toast/Notification** | Yes — test appearance, auto-dismiss, action buttons | Yes — test that real actions trigger correct toasts | No |
| **Design system primitives** | Yes — this is the primary use case for component testing | No — not needed for primitives | No |

**Rule of thumb**: Component tests for **behavior and appearance in isolation**. E2E tests for **user journeys across multiple components and pages**. Unit tests for **pure logic with no DOM**.

## Anti-Patterns

| Don't Do This | Problem | Do This Instead |
|---|---|---|
| Check internal state (`component.state.count`) | Couples test to implementation; breaks on any refactor | Assert on visible output: `expect(component.getByText('Count: 5')).toBeVisible()` |
| Mount an entire page in a component test | Requires too many providers, mock data, and context; slow; defeats isolation purpose | Use E2E tests for full pages; component test only the individual widgets |
| Skip required providers/context | Component crashes with "Cannot read property of undefined" or "useContext must be inside Provider" | Wrap with required providers in `playwright/index.tsx` or per-test wrapper |
| Test framework internals (React lifecycle, Vue watchers) | You are testing the framework, not your code; these are already tested by React/Vue | Test user-visible behavior: what renders, what happens on click |
| Mount and immediately screenshot without waiting | Screenshot captures loading/transition state | `await expect(component.getByText('...')).toBeVisible()` before screenshot |
| Duplicate E2E coverage in component tests | Same behavior tested twice adds maintenance cost with no new confidence | Component tests: isolated behavior. E2E tests: integrated flows. Overlap only at critical boundaries |
| Test CSS class names or inline styles | Implementation detail; breaks on any styling refactor | Use `toHaveScreenshot()` for visual verification or `toBeVisible()`/`toBeHidden()` for behavior |
| Create one giant test file per component | Hard to debug, slow feedback loop, poor test isolation | One test file per component, grouped by behavior with `test.describe()` |
| Pass mock data that does not match real API shape | Tests pass but component breaks with real data | Define shared TypeScript types or use a factory function for consistent test data |
| Use `page.goto()` in component tests | Component tests do not navigate — `mount()` renders directly | Use `mount(<Component />)` only; use `page.goto()` in E2E tests |

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `Cannot find module '@playwright/experimental-ct-react'` | Package not installed | `npm install -D @playwright/experimental-ct-react` (or `-vue`, `-svelte`) |
| Component renders blank | Missing CSS imports or provider wrappers | Add global styles to `playwright/index.ts` and wrap with required providers |
| `Error: No tests found` | Test file does not match `testMatch` pattern in `playwright-ct.config.ts` | Ensure files use the configured suffix (e.g., `*.ct.tsx`) and `testDir` is correct |
| `Cannot use JSX` in test file | TypeScript/Vite not configured for JSX | Ensure test files use `.ct.tsx`/`.ct.jsx` extension and `tsconfig.json` has `"jsx": "react-jsx"` |
| `useContext returns undefined` | Component depends on a context provider that was not wrapped | Add the provider in `playwright/index.tsx` via `beforeMount` hook or wrap per-test |
| `hooksConfig` values are undefined | The `playwright/index.ts` hooks file is not set up or not reading `hooksConfig` | Ensure `beforeMount` destructures `{ hooksConfig }` and the file is at `playwright/index.ts` |
| Screenshots differ between CI and local | Different OS renders fonts differently | Run screenshot tests in Docker or use `maxDiffPixelRatio` tolerance; generate baselines in CI |
| Component test is slow (>5s per test) | Mounting a large component tree with many providers or importing heavy modules | Reduce provider scope; mock heavy imports; use `page.route()` instead of real API calls |
| `mount()` returns but component is not visible | Component renders off-screen or with `display: none` by default | Check CSS and props; use `await expect(component).toBeVisible()` to debug |
| `Error: page.route is not available` | Using `page` fixture without requesting it | Destructure `{ mount, page }` in the test function signature |

## Related

- [core/fixtures-and-hooks.md](fixtures-and-hooks.md) — fixtures work inside component tests the same way
- [core/visual-regression.md](visual-regression.md) — screenshot comparison patterns applicable to component tests
- [core/network-mocking.md](network-mocking.md) — `page.route()` works inside component tests for mocking API calls
- [core/test-architecture.md](test-architecture.md) — when to use component vs E2E vs API tests
- [core/react.md](react.md) — React-specific component testing setup
- [core/vue.md](vue.md) — Vue-specific component testing with slots and provide/inject
