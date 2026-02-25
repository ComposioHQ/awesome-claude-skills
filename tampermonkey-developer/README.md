# Tampermonkey Developer Skill

A comprehensive Claude skill for developing professional Tampermonkey userscripts with modern JavaScript patterns, best practices, and debugging capabilities.

## What is this skill?

This skill teaches Claude how to help you create, debug, and optimize Tampermonkey userscripts. Whether you're automating repetitive tasks, enhancing web pages, or building custom browser tools, this skill provides templates, utilities, and best practices.

## When to use this skill

Use this skill when you want to:
- Build Tampermonkey/Greasemonkey userscripts
- Automate browser tasks on specific websites
- Enhance or modify web pages (DOM manipulation, styling)
- Integrate external APIs with web pages
- Create custom browser automation tools
- Debug existing userscripts

## Quick Start

### Generate a new userscript

```bash
cd tampermonkey-developer
bash scripts/generate-userscript.sh my-script "https://example.com/*"
```

This creates a new `.user.js` file with proper metadata and structure.

### Choose a template

**Basic Template** - Minimal starter for simple scripts:
```bash
bash scripts/generate-userscript.sh my-script "https://example.com/*" basic
```

**Advanced Template** - Full-featured with utilities, settings, error handling:
```bash
bash scripts/generate-userscript.sh my-script "https://example.com/*" advanced
```

**SPA Template** - For Single Page Applications (React, Vue, Angular):
```bash
bash scripts/generate-userscript.sh my-script "https://example.com/*" spa
```

### Validate your script

```bash
bash scripts/validate-userscript.sh my-script.user.js
```

Checks for:
- Missing metadata fields
- Incorrect @grant declarations
- Performance anti-patterns
- Security issues
- Best practice violations

## Features

### Templates
- **basic-template.user.js** - Minimal starter template
- **advanced-template.user.js** - Full-featured with utilities and settings
- **spa-compatible.user.js** - SPA navigation detection and routing

### Scripts
- **generate-userscript.sh** - Generate new userscripts from templates
- **validate-userscript.sh** - Validate scripts for common issues

### Examples
- **youtube-timestamp-bookmarker.user.js** - Complete example showing:
  - DOM manipulation
  - GM storage API
  - Draggable UI panels
  - Event handling
  - Styling injection

## What you'll learn

This skill covers:
- **Metadata blocks** - Proper @grant, @match, @run-at declarations
- **DOM manipulation** - Waiting for elements, MutationObserver patterns
- **API integration** - Cross-origin requests with GM_xmlhttpRequest
- **Storage** - Persistent settings with GM_setValue/getValue
- **Styling** - CSS injection with GM_addStyle
- **SPA support** - Navigation detection for React/Vue/Angular apps
- **Performance** - Debouncing, caching, efficient selectors
- **Security** - Avoiding XSS, CSP compliance, safe patterns
- **Debugging** - Console logging, error handling, testing

## Common patterns included

1. **Waiting for elements** - MutationObserver with timeout
2. **Cross-origin requests** - Promise-based GM_xmlhttpRequest wrapper
3. **Settings management** - localStorage-like API with defaults
4. **Style injection** - CSP-safe CSS with GM_addStyle
5. **SPA navigation** - Detecting route changes without page reload
6. **XHR/Fetch interception** - Modifying requests/responses
7. **Draggable UI** - Creating movable panels
8. **Keyboard shortcuts** - Global hotkey registration

## Best practices enforced

- Always declare @grant (even if using 'none')
- Use MutationObserver for dynamic content
- Cache DOM queries for performance
- Handle errors gracefully with try-catch
- Prefix console logs for easy filtering
- Version scripts with @version
- Test in incognito to catch extension conflicts
- Respect site performance (don't block rendering)

## Example: Using this skill in Claude Code

```
User: "Create a Tampermonkey script that adds a dark mode toggle to GitHub"

Claude: I'll help you create a GitHub dark mode userscript. Let me use the
tampermonkey-developer skill to generate a professional script with proper
structure.

[Generates script with:]
- Proper metadata (@match github.com/*)
- Dark mode CSS injection
- Toggle button UI
- Settings persistence with GM_setValue
- MutationObserver for SPA navigation
```

## Requirements

- Tampermonkey browser extension
- Modern browser (Chrome, Firefox, Edge, Safari)
- Basic JavaScript knowledge

## License

Apache 2.0

## Contributing

This skill is part of the awesome-claude-skills repository. Contributions welcome!
