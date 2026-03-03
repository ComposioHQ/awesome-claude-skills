# Storage and Authentication

> **When to use**: Managing cookies, localStorage, sessionStorage, browser storage state, saving and restoring authentication, or testing storage-dependent features.
> **Prerequisites**: [core-commands.md](core-commands.md) for basic CLI usage

## Quick Reference

```bash
# Save all browser state (cookies + localStorage) to file
playwright-cli state-save auth.json

# Restore state in a new session
playwright-cli state-load auth.json

# Quick cookie operations
playwright-cli cookie-list
playwright-cli cookie-set session_id abc123 --domain=example.com --httpOnly --secure
playwright-cli cookie-delete session_id
playwright-cli cookie-clear

# localStorage
playwright-cli localstorage-set theme dark
playwright-cli localstorage-get theme
playwright-cli localstorage-clear

# sessionStorage
playwright-cli sessionstorage-set step 3
playwright-cli sessionstorage-get step
playwright-cli sessionstorage-clear
```

## Storage State (Save & Restore)

The most powerful feature — save the entire browser state (cookies + localStorage for all origins) to a JSON file, then restore it later to skip login flows.

### Save Storage State

```bash
# Save to auto-generated filename (storage-state-{timestamp}.json)
playwright-cli state-save

# Save to specific file
playwright-cli state-save auth.json
playwright-cli state-save ./states/admin-session.json
```

### Restore Storage State

```bash
# Load state from file
playwright-cli state-load auth.json

# Navigate after loading — cookies and localStorage are already set
playwright-cli goto https://app.example.com/dashboard
# Already authenticated!
```

### Storage State File Format

The saved JSON contains both cookies and localStorage:

```json
{
  "cookies": [
    {
      "name": "session_id",
      "value": "abc123",
      "domain": "example.com",
      "path": "/",
      "expires": 1735689600,
      "httpOnly": true,
      "secure": true,
      "sameSite": "Lax"
    }
  ],
  "origins": [
    {
      "origin": "https://example.com",
      "localStorage": [
        { "name": "theme", "value": "dark" },
        { "name": "user_id", "value": "12345" },
        { "name": "auth_token", "value": "jwt.token.here" }
      ]
    }
  ]
}
```

## Authentication Pattern

The most common workflow — log in once, save state, reuse across sessions.

### Step 1: Log In and Save

```bash
playwright-cli open https://app.example.com/login
playwright-cli snapshot

playwright-cli fill e1 "admin@example.com"
playwright-cli fill e2 "secure-password"
playwright-cli click e3

# Wait for redirect to confirm login succeeded
playwright-cli run-code "async page => {
  await page.waitForURL('**/dashboard');
  return 'Login successful: ' + page.url();
}"

# Save the authenticated state
playwright-cli state-save auth.json
playwright-cli close
```

### Step 2: Reuse Auth State

```bash
# New session — skip login entirely
playwright-cli open https://app.example.com
playwright-cli state-load auth.json
playwright-cli goto https://app.example.com/dashboard
# Already logged in as admin!

playwright-cli snapshot    # See the dashboard
```

### Multi-Role Authentication

```bash
# Save state for each role
playwright-cli open https://app.example.com/login
playwright-cli fill e1 "admin@example.com"
playwright-cli fill e2 "admin-pass"
playwright-cli click e3
playwright-cli state-save admin-auth.json
playwright-cli close

playwright-cli open https://app.example.com/login
playwright-cli fill e1 "user@example.com"
playwright-cli fill e2 "user-pass"
playwright-cli click e3
playwright-cli state-save user-auth.json
playwright-cli close

# Now use them
playwright-cli -s=admin open https://app.example.com
playwright-cli -s=admin state-load admin-auth.json
playwright-cli -s=admin goto https://app.example.com/admin

playwright-cli -s=user open https://app.example.com
playwright-cli -s=user state-load user-auth.json
playwright-cli -s=user goto https://app.example.com/profile
```

### OAuth / SSO Authentication

For OAuth flows that involve redirects and popups:

```bash
playwright-cli run-code "async page => {
  await page.goto('https://app.example.com/login');

  // Click 'Login with Google'
  const [popup] = await Promise.all([
    page.waitForEvent('popup'),
    page.click('button:text(\"Login with Google\")')
  ]);

  // Fill credentials in the popup
  await popup.fill('input[type=email]', 'user@gmail.com');
  await popup.click('#identifierNext');
  await popup.fill('input[type=password]', 'password');
  await popup.click('#passwordNext');

  // Wait for popup to close and main page to redirect
  await popup.waitForEvent('close');
  await page.waitForURL('**/dashboard');

  // Save authenticated state
  await page.context().storageState({ path: 'oauth-auth.json' });
  return 'OAuth login complete';
}"
```

## Cookies

### List All Cookies

```bash
playwright-cli cookie-list
```

### Filter by Domain

```bash
playwright-cli cookie-list --domain=example.com
```

### Filter by Path

```bash
playwright-cli cookie-list --path=/api
```

### Get a Specific Cookie

```bash
playwright-cli cookie-get session_id
playwright-cli cookie-get __cf_bm
```

### Set a Cookie

```bash
# Basic cookie
playwright-cli cookie-set session abc123

# Cookie with full options
playwright-cli cookie-set session abc123 \
  --domain=example.com \
  --path=/ \
  --httpOnly \
  --secure \
  --sameSite=Lax

# Cookie with expiration (Unix timestamp)
playwright-cli cookie-set remember_me token123 --expires=1735689600
```

### Delete a Cookie

```bash
playwright-cli cookie-delete session_id
playwright-cli cookie-delete __cf_bm
```

### Clear All Cookies

```bash
playwright-cli cookie-clear
```

### Advanced: Multiple Cookies at Once

```bash
playwright-cli run-code "async page => {
  await page.context().addCookies([
    {
      name: 'session_id',
      value: 'sess_abc123',
      domain: 'example.com',
      path: '/',
      httpOnly: true,
      secure: true,
      sameSite: 'Strict'
    },
    {
      name: 'preferences',
      value: JSON.stringify({ theme: 'dark', lang: 'en' }),
      domain: 'example.com',
      path: '/'
    },
    {
      name: 'tracking_opt_out',
      value: 'true',
      domain: '.example.com',
      path: '/'
    }
  ]);
}"
```

### Advanced: Read All Cookies Programmatically

```bash
playwright-cli run-code "async page => {
  const cookies = await page.context().cookies();
  return cookies.map(c => ({
    name: c.name,
    value: c.value.substring(0, 20) + '...',
    domain: c.domain,
    httpOnly: c.httpOnly,
    secure: c.secure,
    expires: new Date(c.expires * 1000).toISOString()
  }));
}"
```

## Local Storage

### List All Items

```bash
playwright-cli localstorage-list
```

### Get a Value

```bash
playwright-cli localstorage-get theme
playwright-cli localstorage-get auth_token
```

### Set a Value

```bash
playwright-cli localstorage-set theme dark
playwright-cli localstorage-set language en-US

# Set JSON values (quote the JSON)
playwright-cli localstorage-set user_settings '{"theme":"dark","fontSize":14,"sidebar":true}'
```

### Delete an Item

```bash
playwright-cli localstorage-delete auth_token
```

### Clear All

```bash
playwright-cli localstorage-clear
```

### Advanced: Bulk Operations

```bash
playwright-cli run-code "async page => {
  await page.evaluate(() => {
    localStorage.setItem('token', 'jwt_abc123');
    localStorage.setItem('user_id', '12345');
    localStorage.setItem('user_name', 'Jane Doe');
    localStorage.setItem('preferences', JSON.stringify({
      theme: 'dark',
      notifications: true,
      language: 'en'
    }));
    localStorage.setItem('onboarding_complete', 'true');
  });
}"
```

### Advanced: Read All localStorage

```bash
playwright-cli run-code "async page => {
  return await page.evaluate(() => {
    const items = {};
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      items[key] = localStorage.getItem(key);
    }
    return items;
  });
}"
```

## Session Storage

Session storage is per-tab and cleared when the tab closes.

### List All Items

```bash
playwright-cli sessionstorage-list
```

### Get / Set / Delete

```bash
playwright-cli sessionstorage-get form_step
playwright-cli sessionstorage-set form_step 3
playwright-cli sessionstorage-set form_data '{"name":"Jane","email":"jane@example.com"}'
playwright-cli sessionstorage-delete form_step
playwright-cli sessionstorage-clear
```

## IndexedDB

IndexedDB requires `run-code` for access:

### List Databases

```bash
playwright-cli run-code "async page => {
  return await page.evaluate(async () => {
    const databases = await indexedDB.databases();
    return databases.map(db => ({ name: db.name, version: db.version }));
  });
}"
```

### Delete a Database

```bash
playwright-cli run-code "async page => {
  await page.evaluate(dbName => {
    indexedDB.deleteDatabase(dbName);
  }, 'myDatabase');
  return 'Database deleted';
}"
```

### Read Data from an Object Store

```bash
playwright-cli run-code "async page => {
  return await page.evaluate(() => {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open('myDatabase');
      request.onsuccess = () => {
        const db = request.result;
        const tx = db.transaction('myStore', 'readonly');
        const store = tx.objectStore('myStore');
        const getAll = store.getAll();
        getAll.onsuccess = () => resolve(getAll.result);
        getAll.onerror = () => reject(getAll.error);
      };
      request.onerror = () => reject(request.error);
    });
  });
}"
```

## Common Patterns

### Token Refresh Testing

```bash
# Set an expired token to test refresh logic
playwright-cli localstorage-set auth_token "expired-jwt-token"
playwright-cli localstorage-set token_expiry "1609459200"

# Navigate to trigger token refresh
playwright-cli goto https://app.example.com/dashboard

# Check if token was refreshed
playwright-cli localstorage-get auth_token
```

### Feature Flag Testing

```bash
# Enable a feature flag via localStorage
playwright-cli localstorage-set feature_flags '{"newCheckout":true,"darkMode":true,"betaFeatures":false}'

# Reload to apply
playwright-cli reload
playwright-cli snapshot
```

### Clear Everything and Start Fresh

```bash
playwright-cli cookie-clear
playwright-cli localstorage-clear
playwright-cli sessionstorage-clear
playwright-cli reload
```

### Save and Restore Roundtrip

```bash
# Set up state manually
playwright-cli open https://example.com
playwright-cli cookie-set session abc123 --domain=example.com
playwright-cli localstorage-set user john
playwright-cli localstorage-set theme dark

# Save everything
playwright-cli state-save my-session.json

# Later — restore state in a new session
playwright-cli open https://example.com
playwright-cli state-load my-session.json
playwright-cli reload
# Cookies and localStorage are restored
```

## Security Notes

- **Never commit auth state files** — add `*.auth-state.json` and `auth.json` to `.gitignore`
- **Delete state files after use** — `rm auth.json` when done with automation
- **Use environment variables for credentials** — never hardcode passwords in scripts
- **In-memory sessions are safer** — default sessions don't persist to disk, reducing exposure
- **Rotate saved states** — auth tokens expire; regenerate state files regularly
- **Avoid saving state on shared machines** — storage state files contain session tokens and personal data
