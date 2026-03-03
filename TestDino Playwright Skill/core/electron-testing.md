# Electron Testing

> **When to use**: When your application is an Electron desktop app and you need end-to-end tests covering the renderer process, main process, IPC communication, native dialogs, system tray, and multi-window workflows.
> **Prerequisites**: [core/configuration.md](configuration.md), [core/fixtures-and-hooks.md](fixtures-and-hooks.md)

## Quick Reference

```typescript
import { _electron as electron } from 'playwright';

// Launch the Electron app
const app = await electron.launch({ args: ['./main.js'] });

// Get the first window (renderer process)
const window = await app.firstWindow();

// Access the main process for evaluation
const appPath = await app.evaluate(async ({ app }) => {
  return app.getPath('userData');
});

// Close the app
await app.close();
```

## Patterns

### Basic Electron App Setup

**Use when**: Starting to test an Electron app with Playwright for the first time.
**Avoid when**: Your app is a web app, not an Electron app.

**TypeScript**
```typescript
import { test, expect, _electron as electron, ElectronApplication, Page } from '@playwright/test';

let app: ElectronApplication;
let window: Page;

test.beforeAll(async () => {
  // Launch the Electron app from your project directory
  app = await electron.launch({
    args: ['./dist/main.js'],
    env: {
      ...process.env,
      NODE_ENV: 'test',
    },
  });

  // Wait for the first BrowserWindow to open
  window = await app.firstWindow();

  // Optional: wait for the app to be fully loaded
  await window.waitForLoadState('domcontentloaded');
});

test.afterAll(async () => {
  await app.close();
});

test('app window has correct title', async () => {
  const title = await window.title();
  expect(title).toBe('My Electron App');
});

test('main page renders', async () => {
  await expect(window.getByRole('heading', { name: 'Welcome' })).toBeVisible();
});
```

**JavaScript**
```javascript
const { test, expect, _electron: electron } = require('@playwright/test');

let app;
let window;

test.beforeAll(async () => {
  app = await electron.launch({
    args: ['./dist/main.js'],
    env: {
      ...process.env,
      NODE_ENV: 'test',
    },
  });
  window = await app.firstWindow();
  await window.waitForLoadState('domcontentloaded');
});

test.afterAll(async () => {
  await app.close();
});

test('app window has correct title', async () => {
  const title = await window.title();
  expect(title).toBe('My Electron App');
});

test('main page renders', async () => {
  await expect(window.getByRole('heading', { name: 'Welcome' })).toBeVisible();
});
```

### Electron App Fixture (Recommended)

**Use when**: You want isolated, reusable Electron app instances across test files.
**Avoid when**: All tests can share a single app instance (rare in practice).

**TypeScript**
```typescript
// fixtures.ts
import { test as base, expect, _electron as electron, ElectronApplication, Page } from '@playwright/test';

type ElectronFixtures = {
  electronApp: ElectronApplication;
  window: Page;
};

export const test = base.extend<ElectronFixtures>({
  electronApp: async ({}, use) => {
    const app = await electron.launch({
      args: ['./dist/main.js'],
      env: { ...process.env, NODE_ENV: 'test' },
    });
    await use(app);
    await app.close();
  },

  window: async ({ electronApp }, use) => {
    const window = await electronApp.firstWindow();
    await window.waitForLoadState('domcontentloaded');
    await use(window);
  },
});

export { expect };
```

```typescript
// app.spec.ts
import { test, expect } from './fixtures';

test('navigate to settings', async ({ window }) => {
  await window.getByRole('link', { name: 'Settings' }).click();
  await expect(window.getByRole('heading', { name: 'Settings' })).toBeVisible();
});
```

**JavaScript**
```javascript
// fixtures.js
const { test: base, expect, _electron: electron } = require('@playwright/test');

const test = base.extend({
  electronApp: async ({}, use) => {
    const app = await electron.launch({
      args: ['./dist/main.js'],
      env: { ...process.env, NODE_ENV: 'test' },
    });
    await use(app);
    await app.close();
  },

  window: async ({ electronApp }, use) => {
    const window = await electronApp.firstWindow();
    await window.waitForLoadState('domcontentloaded');
    await use(window);
  },
});

module.exports = { test, expect };
```

### Accessing the Main Process

**Use when**: You need to read Electron app state, check paths, get app version, or verify main process behavior.
**Avoid when**: Everything you need is in the renderer (UI). Prefer testing through the UI.

`app.evaluate()` runs code in the main process with access to all Electron APIs.

**TypeScript**
```typescript
import { test, expect } from './fixtures';

test('verify app version and paths', async ({ electronApp }) => {
  // Evaluate in the main process — receives the Electron module
  const appInfo = await electronApp.evaluate(async ({ app }) => {
    return {
      version: app.getVersion(),
      name: app.getName(),
      userData: app.getPath('userData'),
      locale: app.getLocale(),
      isPackaged: app.isPackaged,
    };
  });

  expect(appInfo.version).toMatch(/^\d+\.\d+\.\d+$/);
  expect(appInfo.name).toBe('my-electron-app');
  expect(appInfo.userData).toBeTruthy();
  expect(appInfo.isPackaged).toBe(false); // false during development
});

test('main process environment variables are set', async ({ electronApp }) => {
  const nodeEnv = await electronApp.evaluate(async () => {
    return process.env.NODE_ENV;
  });

  expect(nodeEnv).toBe('test');
});
```

**JavaScript**
```javascript
const { test, expect } = require('./fixtures');

test('verify app version and paths', async ({ electronApp }) => {
  const appInfo = await electronApp.evaluate(async ({ app }) => {
    return {
      version: app.getVersion(),
      name: app.getName(),
      userData: app.getPath('userData'),
      isPackaged: app.isPackaged,
    };
  });

  expect(appInfo.version).toMatch(/^\d+\.\d+\.\d+$/);
  expect(appInfo.name).toBe('my-electron-app');
});
```

### Testing IPC Communication

**Use when**: Your app uses `ipcMain` / `ipcRenderer` for communication between the main and renderer processes.
**Avoid when**: IPC is an implementation detail and the behavior is fully testable through the UI.

**TypeScript**
```typescript
import { test, expect } from './fixtures';

test('renderer sends IPC message and gets response', async ({ electronApp, window }) => {
  // Trigger an IPC call from the renderer
  const result = await window.evaluate(async () => {
    // Assumes your preload script exposes ipcRenderer via contextBridge
    return await (window as any).electronAPI.getSystemInfo();
  });

  expect(result).toHaveProperty('platform');
  expect(result).toHaveProperty('arch');
  expect(result.platform).toBeTruthy();
});

test('main process handles IPC file-read request', async ({ electronApp, window }) => {
  // Set up a listener in the main process first
  await electronApp.evaluate(async ({ ipcMain }) => {
    ipcMain.handle('test-ping', async () => {
      return { pong: true, timestamp: Date.now() };
    });
  });

  // Send from renderer
  const response = await window.evaluate(async () => {
    return await (window as any).electronAPI.invoke('test-ping');
  });

  expect(response.pong).toBe(true);
  expect(response.timestamp).toBeGreaterThan(0);
});

test('IPC event triggers UI update', async ({ window }) => {
  // Simulate the main process sending an event to the renderer
  await window.evaluate(() => {
    // Trigger a custom event that the app listens for
    window.dispatchEvent(new CustomEvent('app:notification', {
      detail: { message: 'Update available', version: '2.0.0' },
    }));
  });

  await expect(window.getByText('Update available')).toBeVisible();
  await expect(window.getByText('Version 2.0.0')).toBeVisible();
});
```

**JavaScript**
```javascript
const { test, expect } = require('./fixtures');

test('renderer sends IPC message and gets response', async ({ electronApp, window }) => {
  const result = await window.evaluate(async () => {
    return await window.electronAPI.getSystemInfo();
  });

  expect(result).toHaveProperty('platform');
  expect(result).toHaveProperty('arch');
});

test('IPC event triggers UI update', async ({ window }) => {
  await window.evaluate(() => {
    window.dispatchEvent(new CustomEvent('app:notification', {
      detail: { message: 'Update available', version: '2.0.0' },
    }));
  });

  await expect(window.getByText('Update available')).toBeVisible();
});
```

### File System Dialogs

**Use when**: Your app uses Electron's `dialog.showOpenDialog`, `dialog.showSaveDialog`, or similar native file dialogs.
**Avoid when**: File selection is handled by a web input (`<input type="file">`). Use standard Playwright file chooser for that.

Native dialogs cannot be interacted with directly. Mock them in the main process.

**TypeScript**
```typescript
import { test, expect } from './fixtures';

test('open file dialog and load a document', async ({ electronApp, window }) => {
  // Mock the dialog to return a specific file path
  await electronApp.evaluate(async ({ dialog }) => {
    dialog.showOpenDialog = async () => ({
      canceled: false,
      filePaths: ['/tmp/test-document.txt'],
    });
  });

  // Click the "Open File" button in the renderer
  await window.getByRole('button', { name: 'Open File' }).click();

  // Verify the app loaded the file
  await expect(window.getByTestId('file-name')).toHaveText('test-document.txt');
});

test('save file dialog returns selected path', async ({ electronApp, window }) => {
  await electronApp.evaluate(async ({ dialog }) => {
    dialog.showSaveDialog = async () => ({
      canceled: false,
      filePath: '/tmp/exported-report.pdf',
    });
  });

  await window.getByRole('button', { name: 'Export PDF' }).click();
  await expect(window.getByText('Saved to /tmp/exported-report.pdf')).toBeVisible();
});

test('handle canceled file dialog', async ({ electronApp, window }) => {
  await electronApp.evaluate(async ({ dialog }) => {
    dialog.showOpenDialog = async () => ({
      canceled: true,
      filePaths: [],
    });
  });

  await window.getByRole('button', { name: 'Open File' }).click();

  // App should not crash or change state
  await expect(window.getByTestId('file-name')).toHaveText('No file selected');
});
```

**JavaScript**
```javascript
const { test, expect } = require('./fixtures');

test('open file dialog and load a document', async ({ electronApp, window }) => {
  await electronApp.evaluate(async ({ dialog }) => {
    dialog.showOpenDialog = async () => ({
      canceled: false,
      filePaths: ['/tmp/test-document.txt'],
    });
  });

  await window.getByRole('button', { name: 'Open File' }).click();
  await expect(window.getByTestId('file-name')).toHaveText('test-document.txt');
});

test('handle canceled file dialog', async ({ electronApp, window }) => {
  await electronApp.evaluate(async ({ dialog }) => {
    dialog.showOpenDialog = async () => ({
      canceled: true,
      filePaths: [],
    });
  });

  await window.getByRole('button', { name: 'Open File' }).click();
  await expect(window.getByTestId('file-name')).toHaveText('No file selected');
});
```

### System Tray Testing

**Use when**: Your app has a system tray icon with context menus or status indicators.
**Avoid when**: Your app has no tray functionality.

Playwright cannot directly click system tray icons. Test the tray logic by evaluating in the main process.

**TypeScript**
```typescript
import { test, expect } from './fixtures';

test('tray icon is created on app launch', async ({ electronApp }) => {
  const hasTray = await electronApp.evaluate(async ({ BrowserWindow }) => {
    // Access the tray via a reference your app stores
    const { tray } = require('./tray-manager');
    return tray !== null && !tray.isDestroyed();
  });

  expect(hasTray).toBe(true);
});

test('tray tooltip shows unread count', async ({ electronApp }) => {
  const tooltip = await electronApp.evaluate(async () => {
    const { tray } = require('./tray-manager');
    return tray.getToolTip();
  });

  expect(tooltip).toMatch(/\d+ unread messages?/);
});

test('clicking tray "Show" menu item opens the window', async ({ electronApp }) => {
  // Simulate clicking a tray menu item by invoking its callback
  await electronApp.evaluate(async ({ BrowserWindow }) => {
    const { trayMenu } = require('./tray-manager');
    // Find the "Show" menu item and invoke its click handler
    const showItem = trayMenu.items.find((item: any) => item.label === 'Show');
    if (showItem && showItem.click) {
      showItem.click();
    }
  });

  // The main window should now be visible
  const window = await electronApp.firstWindow();
  const isVisible = await window.evaluate(() => {
    return document.visibilityState === 'visible';
  });
  expect(isVisible).toBe(true);
});
```

**JavaScript**
```javascript
const { test, expect } = require('./fixtures');

test('tray icon is created on app launch', async ({ electronApp }) => {
  const hasTray = await electronApp.evaluate(async () => {
    const { tray } = require('./tray-manager');
    return tray !== null && !tray.isDestroyed();
  });

  expect(hasTray).toBe(true);
});
```

### Multiple Windows

**Use when**: Your Electron app opens multiple windows (preferences, about, detached panels).
**Avoid when**: Your app uses a single window.

**TypeScript**
```typescript
import { test, expect } from './fixtures';

test('open and interact with preferences window', async ({ electronApp, window }) => {
  // Click the menu item or button that opens the preferences window
  await window.getByRole('menuitem', { name: 'Preferences' }).click();

  // Wait for the new window to appear
  const prefsWindow = await electronApp.waitForEvent('window');
  await prefsWindow.waitForLoadState('domcontentloaded');

  // Interact with the preferences window
  await prefsWindow.getByLabel('Theme').selectOption('dark');
  await prefsWindow.getByRole('button', { name: 'Save' }).click();

  // Verify the main window reflects the change
  await expect(window.locator('html')).toHaveAttribute('data-theme', 'dark');

  // Close the preferences window
  await prefsWindow.close();
});

test('get all open windows', async ({ electronApp, window }) => {
  // Open a second window
  await window.getByRole('button', { name: 'New Window' }).click();

  // Get all windows
  const allWindows = electronApp.windows();
  expect(allWindows.length).toBe(2);

  // Find the new window (not the main one)
  const newWindow = allWindows.find((w) => w !== window)!;
  await expect(newWindow.getByRole('heading')).toBeVisible();
});
```

**JavaScript**
```javascript
const { test, expect } = require('./fixtures');

test('open and interact with preferences window', async ({ electronApp, window }) => {
  await window.getByRole('menuitem', { name: 'Preferences' }).click();

  const prefsWindow = await electronApp.waitForEvent('window');
  await prefsWindow.waitForLoadState('domcontentloaded');

  await prefsWindow.getByLabel('Theme').selectOption('dark');
  await prefsWindow.getByRole('button', { name: 'Save' }).click();

  await expect(window.locator('html')).toHaveAttribute('data-theme', 'dark');
  await prefsWindow.close();
});
```

### Testing Packaged/Built Apps

**Use when**: You want to test the production build of your Electron app (after `electron-builder`, `electron-forge`, etc.).
**Avoid when**: Development mode testing is sufficient for your CI pipeline.

**TypeScript**
```typescript
import { test, expect, _electron as electron } from '@playwright/test';
import path from 'path';

test('packaged app launches and works', async () => {
  // Path to the packaged app executable
  const appPath = process.platform === 'darwin'
    ? path.join(__dirname, '../dist/mac/MyApp.app/Contents/MacOS/MyApp')
    : process.platform === 'win32'
      ? path.join(__dirname, '../dist/win-unpacked/MyApp.exe')
      : path.join(__dirname, '../dist/linux-unpacked/my-app');

  const app = await electron.launch({
    executablePath: appPath,
  });

  const window = await app.firstWindow();
  await window.waitForLoadState('domcontentloaded');

  // Verify the packaged app works correctly
  const title = await window.title();
  expect(title).toBe('My Electron App');

  await expect(window.getByRole('heading', { name: 'Welcome' })).toBeVisible();

  // Verify it reports as packaged
  const isPackaged = await app.evaluate(async ({ app }) => app.isPackaged);
  expect(isPackaged).toBe(true);

  await app.close();
});
```

**JavaScript**
```javascript
const { test, expect, _electron: electron } = require('@playwright/test');
const path = require('path');

test('packaged app launches and works', async () => {
  const appPath = process.platform === 'darwin'
    ? path.join(__dirname, '../dist/mac/MyApp.app/Contents/MacOS/MyApp')
    : process.platform === 'win32'
      ? path.join(__dirname, '../dist/win-unpacked/MyApp.exe')
      : path.join(__dirname, '../dist/linux-unpacked/my-app');

  const app = await electron.launch({
    executablePath: appPath,
  });

  const window = await app.firstWindow();
  await window.waitForLoadState('domcontentloaded');

  const title = await window.title();
  expect(title).toBe('My Electron App');

  await expect(window.getByRole('heading', { name: 'Welcome' })).toBeVisible();
  await app.close();
});
```

## Decision Guide

| Scenario | Approach | Why |
|---|---|---|
| Launch Electron app for testing | `_electron.launch({ args: ['./main.js'] })` | Playwright's built-in Electron support |
| Get the main window | `app.firstWindow()` | Returns the first `BrowserWindow` as a Playwright `Page` |
| Read main process state | `app.evaluate(({ app }) => ...)` | Runs code in the main process with Electron APIs |
| Test IPC round-trips | `window.evaluate` (renderer) + `app.evaluate` (main) | Cover both sides of the IPC bridge |
| Mock native file dialogs | Override `dialog.showOpenDialog` via `app.evaluate` | Native dialogs cannot be automated directly |
| Test system tray | `app.evaluate` to invoke tray callbacks | Tray icons are OS-native; not clickable via Playwright |
| Multiple windows | `app.waitForEvent('window')` | Captures new `BrowserWindow` instances as they open |
| Test packaged builds | `electron.launch({ executablePath })` | Points to the built binary instead of source |

## Anti-Patterns

| Don't Do This | Problem | Do This Instead |
|---|---|---|
| `const { app } = require('electron')` in test files | Electron APIs are not available in Playwright's Node process | Use `electronApp.evaluate(({ app }) => ...)` |
| Directly import renderer code into tests | Bypasses the actual app lifecycle and IPC | Test through the UI via the `window` (Page) object |
| Skip `waitForLoadState` after `firstWindow()` | Window may not be fully rendered | Always `await window.waitForLoadState('domcontentloaded')` |
| Test tray by clicking system-level UI | Playwright cannot interact with native OS chrome | Mock tray menu callbacks via `app.evaluate` |
| Share a single `ElectronApplication` across all tests without cleanup | State leaks between tests | Use fixtures with `app.close()` in teardown |
| Forget to close the app in `afterAll` | Leaves Electron processes running, eating CI resources | Always `await app.close()` in teardown |

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `electron.launch()` throws "cannot find module" | `args` path does not point to your main entry file | Verify the path: `args: ['./dist/main.js']` relative to the working directory |
| `firstWindow()` times out | App does not open a `BrowserWindow` in time | Check that the app creates a window on startup; increase timeout |
| `app.evaluate` cannot access Electron modules | Destructuring the wrong parameter | Destructure correctly: `evaluate(async ({ app, dialog, BrowserWindow }) => ...)` |
| Dialog mock does not take effect | Mock applied after the dialog was already called | Set up mocks before triggering the UI action that opens the dialog |
| Second window not captured | `waitForEvent('window')` registered after the window opened | Register the event listener before triggering the action that opens the window |
| Tests hang after `app.close()` | Child processes spawned by the app are still running | Ensure your Electron app cleans up child processes on quit |
| Packaged app test fails with path error | Executable path varies by OS and build tool | Use `process.platform` to compute the correct path |
| `window.evaluate` throws context destroyed | Window was closed or navigated during evaluation | Ensure the window is stable before evaluating |

## Related

- [core/fixtures-and-hooks.md](fixtures-and-hooks.md) -- wrapping Electron app launch in fixtures
- [core/assertions-and-waiting.md](assertions-and-waiting.md) -- all standard assertions work on Electron windows
- [core/iframes-and-shadow-dom.md](iframes-and-shadow-dom.md) -- Electron apps often embed web components or iframes
- [core/browser-apis.md](browser-apis.md) -- localStorage, IndexedDB, and other APIs work the same in Electron
