# Core Commands

> **When to use**: Starting browser automation sessions, navigating pages, interacting with elements, filling forms, and performing basic browser operations via the CLI.
> **Prerequisites**: `playwright-cli install --skills && playwright-cli install-browser`

## Quick Reference

```bash
playwright-cli open https://example.com     # Launch + navigate
playwright-cli snapshot                      # See all interactive elements
playwright-cli fill e1 "user@example.com"   # Fill an input field
playwright-cli click e3                      # Click a button
playwright-cli screenshot --filename=pg.png # Capture the page
playwright-cli close                         # Done
```

## The Snapshot Workflow

Every interaction starts with a **snapshot**. The snapshot command renders the page's accessibility tree and assigns short refs (like `e1`, `e2`, `e3`) to each interactive element.

```bash
playwright-cli open https://example.com/login
playwright-cli snapshot
# Output:
# e1 [textbox "Email"]
# e2 [textbox "Password"]
# e3 [button "Sign In"]
# e4 [link "Forgot password?"]
# e5 [link "Create account"]
```

Use refs to target elements precisely:

```bash
playwright-cli fill e1 "user@example.com"
playwright-cli fill e2 "secretpassword"
playwright-cli click e3
```

**Always re-snapshot after page changes** — refs are only valid for the current page state. After navigation, form submission, or dynamic content updates, take a new snapshot.

```bash
playwright-cli click e3          # Submit form
playwright-cli snapshot          # Re-snapshot to see new page elements
```

### Saving Snapshots

Save snapshots to YAML files for later reference or comparison:

```bash
playwright-cli snapshot --filename=before-submit.yaml
playwright-cli click e3
playwright-cli snapshot --filename=after-submit.yaml
```

## Opening & Closing Browsers

### Basic Launch

```bash
# Open browser with blank page
playwright-cli open

# Open and navigate immediately
playwright-cli open https://example.com

# Open with specific browser engine
playwright-cli open --browser=chrome      # Google Chrome
playwright-cli open --browser=firefox     # Mozilla Firefox
playwright-cli open --browser=webkit      # Safari/WebKit
playwright-cli open --browser=msedge      # Microsoft Edge
```

### Persistent Profiles

By default, each session runs in-memory — no cookies or storage persist after closing. Use `--persistent` to keep state across restarts:

```bash
# Auto-generated profile directory
playwright-cli open https://example.com --persistent

# Custom profile directory
playwright-cli open https://example.com --profile=/tmp/my-profile

# With a config file
playwright-cli open https://example.com --config=my-config.json
```

### Browser Extension Mode

Connect to an existing browser via extension instead of launching a new one:

```bash
playwright-cli open --extension
```

### Closing

```bash
playwright-cli close              # Close the current browser
playwright-cli close-all          # Close all open browsers
playwright-cli kill-all           # Force kill zombie processes
playwright-cli delete-data        # Delete stored profile data
```

## Navigation

```bash
playwright-cli goto https://example.com/dashboard    # Navigate to URL
playwright-cli go-back                                # Browser back
playwright-cli go-forward                             # Browser forward
playwright-cli reload                                 # Refresh page
```

### Waiting for Navigation

After actions that trigger navigation (form submits, link clicks), the CLI waits for the page to reach `load` state before returning. If you need to wait for specific conditions, use `run-code`:

```bash
playwright-cli run-code "async page => {
  await page.waitForURL('**/dashboard');
}"

# Wait for network to settle
playwright-cli run-code "async page => {
  await page.waitForLoadState('networkidle');
}"
```

## Element Interaction

### Clicking

```bash
playwright-cli click e3            # Standard left click
playwright-cli dblclick e7         # Double click
playwright-cli hover e4            # Hover without clicking
```

### Form Input

```bash
# fill: clears existing value, then types the full value at once
playwright-cli fill e5 "user@example.com"

# type: sends keystrokes one by one (triggers keydown/keypress/keyup per char)
playwright-cli type "search query"

# select: choose dropdown option by value
playwright-cli select e9 "option-value"

# check/uncheck: toggle checkboxes
playwright-cli check e12
playwright-cli uncheck e12
```

**When to use `fill` vs `type`**:

| Command | Behavior | Use when |
|---------|----------|----------|
| `fill` | Clears field, sets value at once | Forms, login fields, standard inputs |
| `type` | Sends individual keystrokes | Autocomplete, search-as-you-type, custom inputs that listen for keydown events |

### File Upload

```bash
playwright-cli upload e8 ./document.pdf
playwright-cli upload e8 ./photo1.jpg ./photo2.jpg    # Multiple files
```

### Drag and Drop

```bash
playwright-cli drag e2 e8    # Drag element e2 onto element e8
```

### Viewport Resizing

```bash
playwright-cli resize 1920 1080    # Desktop
playwright-cli resize 375 812      # iPhone X viewport
playwright-cli resize 768 1024     # iPad viewport
```

## Keyboard Input

### Single Key Presses

```bash
playwright-cli press Enter
playwright-cli press Tab
playwright-cli press Escape
playwright-cli press Backspace
playwright-cli press Delete
playwright-cli press Space
```

### Arrow Keys

```bash
playwright-cli press ArrowUp
playwright-cli press ArrowDown
playwright-cli press ArrowLeft
playwright-cli press ArrowRight
```

### Modifier Key Combos

```bash
playwright-cli press Control+a        # Select all
playwright-cli press Control+c        # Copy
playwright-cli press Control+v        # Paste
playwright-cli press Control+z        # Undo
playwright-cli press Meta+a           # Select all (macOS Cmd+A)
playwright-cli press Shift+Tab        # Reverse tab
playwright-cli press Alt+Enter        # Alt+Enter
```

### Hold and Release Keys

For drag operations or multi-key sequences:

```bash
playwright-cli keydown Shift
playwright-cli click e5              # Shift+click
playwright-cli click e8              # Shift+click (range selection)
playwright-cli keyup Shift
```

## Mouse Control

For pixel-precise operations (canvas, maps, custom widgets):

```bash
playwright-cli mousemove 150 300     # Move cursor to coordinates
playwright-cli mousedown             # Press left button
playwright-cli mouseup               # Release left button
playwright-cli mousedown right       # Right click down
playwright-cli mouseup right         # Right click up
playwright-cli mousewheel 0 100      # Scroll down 100px
playwright-cli mousewheel 0 -100     # Scroll up 100px
playwright-cli mousewheel 100 0      # Scroll right 100px
```

### Drawing on Canvas

```bash
playwright-cli open https://example.com/canvas-app
playwright-cli mousemove 100 100
playwright-cli mousedown
playwright-cli mousemove 200 200
playwright-cli mousemove 300 150
playwright-cli mouseup
```

## Dialog Handling

Dialogs (`alert`, `confirm`, `prompt`) block browser interaction. Handle them immediately:

```bash
# Accept an alert or confirm dialog
playwright-cli dialog-accept

# Accept a prompt dialog with input text
playwright-cli dialog-accept "my response"

# Dismiss/cancel a dialog
playwright-cli dialog-dismiss
```

**Tip**: If you expect a dialog to appear from a click, configure handling via `run-code` before triggering the action:

```bash
playwright-cli run-code "async page => {
  page.on('dialog', dialog => dialog.accept('confirmed'));
}"
playwright-cli click e5    # This triggers the dialog
```

## JavaScript Evaluation

Execute JavaScript expressions directly in the page context:

```bash
# Simple expressions
playwright-cli eval "document.title"
playwright-cli eval "window.location.href"
playwright-cli eval "document.querySelectorAll('li').length"

# Evaluate on a specific element
playwright-cli eval "el => el.textContent" e5
playwright-cli eval "el => el.getAttribute('href')" e3
playwright-cli eval "el => el.getBoundingClientRect()" e1

# Complex evaluation
playwright-cli eval "JSON.stringify(performance.timing)"
playwright-cli eval "window.innerWidth + 'x' + window.innerHeight"
```

## Example Workflows

### Login Flow

```bash
playwright-cli open https://app.example.com/login
playwright-cli snapshot

playwright-cli fill e1 "admin@example.com"
playwright-cli fill e2 "password123"
playwright-cli click e3
playwright-cli snapshot             # See the dashboard
playwright-cli screenshot --filename=dashboard.png
playwright-cli close
```

### Form Submission with Validation

```bash
playwright-cli open https://example.com/contact
playwright-cli snapshot

# Fill form fields
playwright-cli fill e1 "Jane Doe"
playwright-cli fill e2 "jane@example.com"
playwright-cli fill e3 "+1-555-0123"
playwright-cli select e4 "support"
playwright-cli fill e5 "I need help with my account"
playwright-cli check e6             # Agree to terms

# Submit
playwright-cli click e7
playwright-cli snapshot             # Verify success message
playwright-cli close
```

### Search and Navigate Results

```bash
playwright-cli open https://example.com
playwright-cli snapshot

playwright-cli fill e1 "playwright automation"
playwright-cli press Enter
playwright-cli snapshot             # See search results

playwright-cli click e5             # Click first result
playwright-cli snapshot             # See result page
playwright-cli go-back              # Return to results
playwright-cli close
```

### Multi-Tab Research

```bash
playwright-cli open https://docs.example.com
playwright-cli tab-new https://api.example.com/reference
playwright-cli tab-new https://github.com/example/repo

playwright-cli tab-list             # See all 3 tabs
playwright-cli tab-select 0         # Go to docs tab
playwright-cli snapshot
playwright-cli tab-select 2         # Go to GitHub tab
playwright-cli snapshot

playwright-cli close                # Closes all tabs
```

## Tips

- **Snapshot frequently**: After every action that changes the page, re-snapshot to get fresh refs
- **Use `fill` for forms**: It's faster and more reliable than `type` for standard inputs
- **Viewport matters**: Use `resize` to test responsive layouts before taking screenshots
- **Chain with `run-code`**: When CLI commands feel limiting, drop into the full Playwright API
- **Check `console`**: Run `playwright-cli console` to see JavaScript errors that might explain unexpected behavior
