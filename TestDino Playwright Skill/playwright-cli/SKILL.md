---
name: playwright-cli
description: Automates browser interactions for web testing, form filling, screenshots, and data extraction using playwright-cli. Use when the user needs to navigate websites, interact with web pages, fill forms, take screenshots, test web applications, extract information from web pages, mock network requests, manage browser sessions, or generate test code.
allowed-tools: Bash(playwright-cli:*)
---

# Browser Automation with playwright-cli

> Comprehensive CLI-driven browser automation — navigate, interact, mock, debug, record, and generate tests without writing a single script file.

## Quick Start

```bash
# Install and set up
playwright-cli install --skills
playwright-cli install-browser

# Open a browser and navigate
playwright-cli open https://playwright.dev

# Take a snapshot to see interactive elements (refs like e1, e2, e3...)
playwright-cli snapshot

# Interact using element refs from the snapshot
playwright-cli click e15
playwright-cli fill e5 "search query"
playwright-cli press Enter

# Take a screenshot
playwright-cli screenshot

# Close the browser
playwright-cli close
```

## Golden Rules

1. **Always `snapshot` first** — identify element refs before interacting; never guess ref numbers
2. **Use `fill` for inputs, `click` for buttons** — `type` sends keystrokes one-by-one, `fill` replaces the entire value
3. **Named sessions for parallel work** — `-s=name` isolates cookies, storage, and tabs per session
4. **Save auth state** — `state-save auth.json` after login, `state-load auth.json` to skip login next time
5. **Trace before debugging** — `tracing-start` before the failing step, not after
6. **`run-code` for advanced scenarios** — when CLI commands aren't enough, drop into full Playwright API
7. **Clean up sessions** — `close` or `close-all` when done; `kill-all` for zombie processes
8. **Descriptive filenames** — `screenshot --filename=checkout-step3.png` not `screenshot`
9. **Mock external APIs only** — use `route` to intercept third-party services, not your own app
10. **Persistent profiles for stateful flows** — `--persistent` keeps cookies and storage across restarts

## Command Reference

### Core Interaction

```bash
playwright-cli open [url]                    # Launch browser, optionally navigate
playwright-cli goto <url>                    # Navigate to URL
playwright-cli snapshot                      # Show page elements with refs
playwright-cli snapshot --filename=snap.yaml # Save snapshot to file
playwright-cli click <ref>                   # Click an element
playwright-cli dblclick <ref>                # Double-click
playwright-cli fill <ref> "value"            # Clear and fill input
playwright-cli type "text"                   # Type keystroke by keystroke
playwright-cli select <ref> "option-value"   # Select dropdown option
playwright-cli check <ref>                   # Check a checkbox
playwright-cli uncheck <ref>                 # Uncheck a checkbox
playwright-cli hover <ref>                   # Hover over element
playwright-cli drag <src-ref> <dst-ref>      # Drag and drop
playwright-cli upload <ref> ./file.pdf       # Upload a file
playwright-cli eval "document.title"         # Evaluate JS expression
playwright-cli eval "el => el.textContent" <ref>  # Evaluate on element
playwright-cli close                         # Close the browser
```

### Navigation

```bash
playwright-cli go-back                       # Browser back button
playwright-cli go-forward                    # Browser forward button
playwright-cli reload                        # Reload current page
```

### Keyboard & Mouse

```bash
playwright-cli press Enter                   # Press a key
playwright-cli press ArrowDown               # Arrow keys
playwright-cli keydown Shift                 # Hold key down
playwright-cli keyup Shift                   # Release key
playwright-cli mousemove 150 300             # Move mouse to coordinates
playwright-cli mousedown [right]             # Mouse button down
playwright-cli mouseup [right]               # Mouse button up
playwright-cli mousewheel 0 100              # Scroll (deltaX, deltaY)
```

### Dialogs

```bash
playwright-cli dialog-accept                 # Accept alert/confirm/prompt
playwright-cli dialog-accept "text"          # Accept prompt with input
playwright-cli dialog-dismiss                # Dismiss/cancel dialog
```

### Tabs

```bash
playwright-cli tab-list                      # List all open tabs
playwright-cli tab-new [url]                 # Open new tab
playwright-cli tab-select <index>            # Switch to tab by index
playwright-cli tab-close [index]             # Close tab (current or by index)
```

### Screenshots & Media

```bash
playwright-cli screenshot                    # Screenshot current page
playwright-cli screenshot <ref>              # Screenshot specific element
playwright-cli screenshot --filename=pg.png  # Save with custom filename
playwright-cli pdf --filename=page.pdf       # Save page as PDF
playwright-cli video-start                   # Start video recording
playwright-cli video-stop output.webm        # Stop and save video
playwright-cli resize 1920 1080              # Resize viewport
```

### Storage & Auth

```bash
playwright-cli state-save [file.json]        # Save cookies + localStorage
playwright-cli state-load <file.json>        # Restore saved state
playwright-cli cookie-list [--domain=...]    # List cookies
playwright-cli cookie-get <name>             # Get specific cookie
playwright-cli cookie-set <name> <value> [opts]  # Set a cookie
playwright-cli cookie-delete <name>          # Delete a cookie
playwright-cli cookie-clear                  # Clear all cookies
playwright-cli localstorage-list             # List localStorage items
playwright-cli localstorage-get <key>        # Get localStorage value
playwright-cli localstorage-set <key> <val>  # Set localStorage value
playwright-cli localstorage-delete <key>     # Delete localStorage item
playwright-cli localstorage-clear            # Clear all localStorage
playwright-cli sessionstorage-list           # List sessionStorage
playwright-cli sessionstorage-get <key>      # Get sessionStorage value
playwright-cli sessionstorage-set <key> <val>    # Set sessionStorage value
playwright-cli sessionstorage-delete <key>   # Delete sessionStorage item
playwright-cli sessionstorage-clear          # Clear all sessionStorage
```

### Network Mocking

```bash
playwright-cli route "<pattern>" [opts]      # Intercept matching requests
playwright-cli route-list                    # List active route overrides
playwright-cli unroute "<pattern>"           # Remove specific route
playwright-cli unroute                       # Remove all routes
```

### DevTools & Debugging

```bash
playwright-cli console [level]              # Show console messages
playwright-cli network                      # Show network requests
playwright-cli tracing-start                # Start trace recording
playwright-cli tracing-stop                 # Stop and save trace
playwright-cli run-code "async page => {}"  # Execute Playwright API code
```

### Sessions & Configuration

```bash
playwright-cli -s=<name> <command>          # Run command in named session
playwright-cli list                         # List all active sessions
playwright-cli close-all                    # Close all browsers
playwright-cli kill-all                     # Force kill all processes
playwright-cli delete-data                  # Delete session user data
playwright-cli open --browser=firefox       # Use specific browser
playwright-cli open --persistent            # Persist profile to disk
playwright-cli open --profile=/path         # Custom profile directory
playwright-cli open --config=config.json    # Use config file
playwright-cli open --extension             # Connect via extension
```

## Guide Index

### Getting Started

| What you're doing | Guide |
|---|---|
| Core browser interaction | [core-commands.md](core-commands.md) |
| Generating test code | [test-generation.md](test-generation.md) |
| Screenshots, video, PDF | [screenshots-and-media.md](screenshots-and-media.md) |

### Testing & Debugging

| What you're doing | Guide |
|---|---|
| Tracing and debugging | [tracing-and-debugging.md](tracing-and-debugging.md) |
| Network mocking & interception | [request-mocking.md](request-mocking.md) |
| Running custom Playwright code | [running-custom-code.md](running-custom-code.md) |

### State & Sessions

| What you're doing | Guide |
|---|---|
| Cookies, localStorage, auth state | [storage-and-auth.md](storage-and-auth.md) |
| Multi-session management | [session-management.md](session-management.md) |

### Advanced

| What you're doing | Guide |
|---|---|
| Device & environment emulation | [device-emulation.md](device-emulation.md) |
| Complex multi-step workflows | [advanced-workflows.md](advanced-workflows.md) |
