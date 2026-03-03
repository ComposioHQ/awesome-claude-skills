# Session Management

> **When to use**: Running multiple isolated browser sessions concurrently, managing persistent profiles, comparing different browser states side by side, parallel scraping, or A/B testing flows.
> **Prerequisites**: [core-commands.md](core-commands.md) for basic CLI usage

## Quick Reference

```bash
# Named sessions: each has independent cookies, storage, tabs
playwright-cli -s=auth open https://app.example.com/login
playwright-cli -s=public open https://example.com

# Interact within a session
playwright-cli -s=auth fill e1 "user@example.com"
playwright-cli -s=public snapshot

# List all active sessions
playwright-cli list

# Clean up
playwright-cli -s=auth close
playwright-cli close-all             # Close everything
playwright-cli kill-all              # Force kill zombie processes
```

## Named Sessions

Use the `-s=<name>` flag to create isolated browser instances. Each named session has its own:

- Cookies
- localStorage / sessionStorage
- IndexedDB
- Cache
- Browsing history
- Open tabs

### Creating Sessions

```bash
# Create a session for authentication testing
playwright-cli -s=admin open https://app.example.com/login

# Create a separate session for a different user
playwright-cli -s=viewer open https://app.example.com/login

# All commands in a session are isolated
playwright-cli -s=admin fill e1 "admin@company.com"
playwright-cli -s=admin fill e2 "admin-password"
playwright-cli -s=admin click e3

playwright-cli -s=viewer fill e1 "viewer@company.com"
playwright-cli -s=viewer fill e2 "viewer-password"
playwright-cli -s=viewer click e3
```

### Default Session

When `-s` is omitted, all commands share a single default session:

```bash
# These all use the same default session
playwright-cli open https://example.com
playwright-cli snapshot
playwright-cli click e1
playwright-cli close
```

## Session Isolation

Sessions are fully independent — actions in one session never affect another:

```bash
# Session A logs in as admin
playwright-cli -s=admin open https://app.example.com
playwright-cli -s=admin fill e1 "admin@example.com"
playwright-cli -s=admin fill e2 "admin-pass"
playwright-cli -s=admin click e3

# Session B visits the same site — NOT logged in
playwright-cli -s=guest open https://app.example.com
playwright-cli -s=guest snapshot
# Shows the login page, not the admin dashboard

# Session C can use a completely different browser
playwright-cli -s=firefox-test open https://app.example.com --browser=firefox
```

## Session Commands

```bash
# List all active sessions with their status
playwright-cli list

# Close a specific named session
playwright-cli -s=mysession close

# Close the default session
playwright-cli close

# Close ALL sessions at once
playwright-cli close-all

# Force kill all browser daemon processes (for stuck/zombie browsers)
playwright-cli kill-all

# Delete persistent profile data for a session
playwright-cli -s=mysession delete-data

# Delete default session data
playwright-cli delete-data
```

## Persistent Profiles

By default, sessions run **in-memory** — all cookies, storage, and browsing data are lost when the session closes. Use `--persistent` to save state to disk.

### Auto-Generated Profile

```bash
# Playwright-cli manages the profile directory automatically
playwright-cli -s=myapp open https://example.com --persistent

# Close and reopen — cookies and storage are preserved
playwright-cli -s=myapp close
playwright-cli -s=myapp open https://example.com --persistent
# Still logged in!
```

### Custom Profile Directory

```bash
# Specify exactly where to store profile data
playwright-cli -s=myapp open https://example.com --profile=/tmp/my-browser-profile

# Useful for sharing profiles between sessions
playwright-cli -s=session-a open https://example.com --profile=/shared/profile
playwright-cli -s=session-a close
playwright-cli -s=session-b open https://example.com --profile=/shared/profile
```

### Cleaning Up Persistent Data

```bash
# Remove stored profile data (must close the session first)
playwright-cli -s=myapp close
playwright-cli -s=myapp delete-data
```

## Session Configuration

Configure browser engine and options per session:

```bash
# Different browsers for different sessions
playwright-cli -s=chrome-test open https://example.com --browser=chrome
playwright-cli -s=firefox-test open https://example.com --browser=firefox
playwright-cli -s=webkit-test open https://example.com --browser=webkit
playwright-cli -s=edge-test open https://example.com --browser=msedge

# With config file
playwright-cli -s=configured open https://example.com --config=my-config.json

# Headed mode (visible browser window)
playwright-cli -s=visible open https://example.com --headed

# Connect to existing browser via extension
playwright-cli -s=extension open --extension
```

## Environment Variable

Set a default session name so all commands use it without the `-s` flag:

```bash
export PLAYWRIGHT_CLI_SESSION="mysession"

# These now use "mysession" automatically
playwright-cli open https://example.com
playwright-cli snapshot
playwright-cli close
```

## Common Patterns

### Multi-User Role Testing

Test the same application as different user roles simultaneously:

```bash
# Admin session
playwright-cli -s=admin open https://app.example.com/login
playwright-cli -s=admin snapshot
playwright-cli -s=admin fill e1 "admin@company.com"
playwright-cli -s=admin fill e2 "admin-pass"
playwright-cli -s=admin click e3

# Regular user session
playwright-cli -s=user open https://app.example.com/login
playwright-cli -s=user fill e1 "user@company.com"
playwright-cli -s=user fill e2 "user-pass"
playwright-cli -s=user click e3

# Compare what each role sees
playwright-cli -s=admin snapshot     # Should show admin panel
playwright-cli -s=user snapshot      # Should NOT show admin panel

playwright-cli -s=admin screenshot --filename=admin-view.png
playwright-cli -s=user screenshot --filename=user-view.png
```

### Concurrent Scraping

Scrape multiple sites in parallel for speed:

```bash
#!/bin/bash

# Launch all browsers concurrently
playwright-cli -s=site1 open https://site1.example.com &
playwright-cli -s=site2 open https://site2.example.com &
playwright-cli -s=site3 open https://site3.example.com &
wait

# Collect data from each
playwright-cli -s=site1 snapshot --filename=site1.yaml
playwright-cli -s=site2 snapshot --filename=site2.yaml
playwright-cli -s=site3 snapshot --filename=site3.yaml

# Take screenshots
playwright-cli -s=site1 screenshot --filename=site1.png
playwright-cli -s=site2 screenshot --filename=site2.png
playwright-cli -s=site3 screenshot --filename=site3.png

# Clean up
playwright-cli close-all
```

### A/B Testing Comparison

```bash
# Variant A
playwright-cli -s=variant-a open "https://app.example.com?variant=a"
playwright-cli -s=variant-a screenshot --filename=variant-a.png

# Variant B
playwright-cli -s=variant-b open "https://app.example.com?variant=b"
playwright-cli -s=variant-b screenshot --filename=variant-b.png

# Compare side by side
playwright-cli close-all
```

### Cross-Browser Testing

Run the same flow in multiple browsers to verify compatibility:

```bash
#!/bin/bash

for browser in chrome firefox webkit; do
  playwright-cli -s=$browser open https://example.com --browser=$browser
  playwright-cli -s=$browser snapshot
  playwright-cli -s=$browser screenshot --filename="$browser-home.png"

  playwright-cli -s=$browser goto https://example.com/features
  playwright-cli -s=$browser screenshot --filename="$browser-features.png"
done

playwright-cli close-all
```

### Authenticated State Sharing Across Sessions

```bash
# Log in once and save state
playwright-cli -s=login open https://app.example.com/login
playwright-cli -s=login fill e1 "user@example.com"
playwright-cli -s=login fill e2 "password123"
playwright-cli -s=login click e3
playwright-cli -s=login state-save auth.json
playwright-cli -s=login close

# Reuse auth state in multiple sessions
playwright-cli -s=session-a open https://app.example.com
playwright-cli -s=session-a state-load auth.json
playwright-cli -s=session-a goto https://app.example.com/dashboard

playwright-cli -s=session-b open https://app.example.com
playwright-cli -s=session-b state-load auth.json
playwright-cli -s=session-b goto https://app.example.com/settings
```

## Best Practices

### 1. Name Sessions Semantically

```bash
# Good: Clear purpose
playwright-cli -s=github-auth open https://github.com
playwright-cli -s=docs-scrape open https://docs.example.com
playwright-cli -s=checkout-flow open https://shop.example.com

# Avoid: Generic names
playwright-cli -s=s1 open https://github.com
playwright-cli -s=test open https://docs.example.com
```

### 2. Always Clean Up

```bash
# Close individual sessions when done
playwright-cli -s=auth close
playwright-cli -s=scrape close

# Or close all at once
playwright-cli close-all

# If browsers become unresponsive
playwright-cli kill-all
```

### 3. Delete Stale Persistent Data

```bash
# Remove old persistent profiles to free disk space
playwright-cli -s=old-session delete-data
```

### 4. Use Default Session for Single-Task Work

Don't create named sessions when you only need one browser:

```bash
# Simple single-session workflow — no -s flag needed
playwright-cli open https://example.com
playwright-cli snapshot
playwright-cli click e1
playwright-cli close
```

### 5. Combine with State Management

For long-running tasks, save state periodically:

```bash
playwright-cli -s=long-task open https://app.example.com --persistent
# ... many interactions ...
playwright-cli -s=long-task state-save checkpoint.json
# ... more interactions ...
# If something goes wrong, restore:
playwright-cli -s=long-task state-load checkpoint.json
```
