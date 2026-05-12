---
name: tampermonkey-developer
description: Comprehensive toolkit for developing, testing, and debugging Tampermonkey userscripts. Supports DOM manipulation, API integration, XHR/fetch interception, styling injection, and modern JavaScript patterns. Use for building browser automation scripts, web page enhancements, and custom browser extensions.
license: Apache 2.0
---

# Tampermonkey Developer

A comprehensive skill for developing professional Tampermonkey userscripts with modern JavaScript patterns, best practices, and debugging capabilities.

## Quick Start

### Step 1: Understand the Requirements

Before building a userscript:
1. Identify target website(s) and URL patterns
2. Determine what DOM elements need manipulation
3. Understand timing requirements (DOMContentLoaded vs window.onload)
4. Check for SPA (Single Page Application) requirements

### Step 2: Generate Userscript Structure

Use the template generator to create a new userscript:
```bash
bash scripts/generate-userscript.sh <script-name> <target-url>
```

This creates a fully structured userscript with:
- ✅ Complete metadata block with proper @grant declarations
- ✅ Modern ES6+ JavaScript structure
- ✅ Mutation observer for dynamic content handling
- ✅ Error handling and logging framework
- ✅ Common utility functions

### Step 3: Develop the Userscript

Edit the generated `.user.js` file following these principles:

**DOM Manipulation Best Practices:**
- Always wait for DOM ready state
- Use `MutationObserver` for dynamic content
- Prefer `querySelector`/`querySelectorAll` over jQuery
- Cache DOM references for performance
- Use `requestAnimationFrame` for visual changes

**Timing Considerations:**
- `@run-at document-start` - Before any DOM elements exist
- `@run-at document-body` - When `<body>` exists (default)
- `@run-at document-end` - After DOM is loaded (like DOMContentLoaded)
- `@run-at document-idle` - After page fully loaded (like window.onload)

**Security & Permissions:**
Only request grants you actually need:
- `GM_setValue` / `GM_getValue` - Persistent storage
- `GM_xmlhttpRequest` - Cross-origin requests
- `GM_addStyle` - Inject CSS
- `GM_setClipboard` - Clipboard access
- `GM_notification` - Browser notifications
- `GM_openInTab` - Open new tabs
- `unsafeWindow` - Access page's window object (use with caution)

### Step 4: Testing & Debugging

**Local Testing:**
1. Install in Tampermonkey
2. Enable debug mode in script settings
3. Use `console.log` with script prefix for filtering
4. Monitor with browser DevTools

**Common Debugging Commands:**
```javascript
// Script info logging
console.log('[YourScript]', 'Initialized');

// DOM element checking
console.assert(element, 'Element not found!');

// Performance monitoring
console.time('operation');
// ... your code
console.timeEnd('operation');
```

**Anti-Pattern Detection:**
Use the validator script to check for common issues:
```bash
bash scripts/validate-userscript.sh your-script.user.js
```

Checks for:
- Missing @grant declarations
- Inefficient selectors
- Memory leaks (unremoved event listeners)
- CSP violations
- Insecure patterns (eval, innerHTML with user input)

### Step 5: Optimization

**Performance Tips:**
1. Debounce/throttle event handlers
2. Use event delegation for dynamic elements
3. Minimize DOM queries (cache results)
4. Avoid synchronous XHR
5. Use `GM_addStyle` instead of inline styles

**Example - Debounce Function:**
```javascript
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}

// Usage
const handleScroll = debounce(() => {
    console.log('Scrolled!');
}, 250);
window.addEventListener('scroll', handleScroll);
```

## Common Patterns

### Pattern 1: Waiting for Elements

```javascript
// Using Mutation Observer (recommended for dynamic content)
function waitForElement(selector, callback, timeout = 10000) {
    const startTime = Date.now();

    // Check if element already exists
    const element = document.querySelector(selector);
    if (element) return callback(element);

    // Setup observer
    const observer = new MutationObserver((mutations, obs) => {
        const element = document.querySelector(selector);
        if (element) {
            obs.disconnect();
            callback(element);
        } else if (Date.now() - startTime > timeout) {
            obs.disconnect();
            console.warn(`Timeout waiting for: ${selector}`);
        }
    });

    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
}

// Usage
waitForElement('.target-class', (element) => {
    element.style.backgroundColor = 'yellow';
});
```

### Pattern 2: Cross-Origin API Requests

```javascript
// Using GM_xmlhttpRequest for CORS-free requests
function fetchAPI(url, options = {}) {
    return new Promise((resolve, reject) => {
        GM_xmlhttpRequest({
            method: options.method || 'GET',
            url: url,
            headers: options.headers || {},
            data: options.body,
            onload: (response) => {
                if (response.status >= 200 && response.status < 300) {
                    try {
                        resolve(JSON.parse(response.responseText));
                    } catch {
                        resolve(response.responseText);
                    }
                } else {
                    reject(new Error(`HTTP ${response.status}`));
                }
            },
            onerror: (error) => reject(error),
            ontimeout: () => reject(new Error('Request timeout'))
        });
    });
}

// Usage
fetchAPI('https://api.example.com/data')
    .then(data => console.log(data))
    .catch(err => console.error('API Error:', err));
```

### Pattern 3: Persistent Settings

```javascript
// Settings manager with defaults
class ScriptSettings {
    constructor(defaults = {}) {
        this.defaults = defaults;
    }

    get(key) {
        const value = GM_getValue(key);
        return value !== undefined ? value : this.defaults[key];
    }

    set(key, value) {
        GM_setValue(key, value);
    }

    getAll() {
        const settings = {};
        for (const key in this.defaults) {
            settings[key] = this.get(key);
        }
        return settings;
    }
}

// Usage
const settings = new ScriptSettings({
    enabled: true,
    theme: 'dark',
    maxItems: 50
});

if (settings.get('enabled')) {
    // Run script logic
}
```

### Pattern 4: Style Injection

```javascript
// Inject CSS with GM_addStyle (CSP-safe)
GM_addStyle(`
    .custom-element {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 12px 24px;
        border-radius: 8px;
        color: white;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s;
    }

    .custom-element:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 8px rgba(0, 0, 0, 0.15);
    }
`);
```

### Pattern 5: SPA Navigation Detection

```javascript
// Detect route changes in Single Page Applications
let lastUrl = location.href;

function onLocationChange(callback) {
    new MutationObserver(() => {
        const currentUrl = location.href;
        if (currentUrl !== lastUrl) {
            lastUrl = currentUrl;
            callback(currentUrl);
        }
    }).observe(document, { subtree: true, childList: true });
}

// Usage
onLocationChange((url) => {
    console.log('Navigation detected:', url);
    // Re-initialize script logic for new page
    initializeScript();
});
```

## Advanced Techniques

### Intercepting XHR/Fetch Requests

```javascript
// Intercept and modify fetch requests
(function(fetch) {
    window.fetch = function(...args) {
        console.log('Fetch intercepted:', args[0]);

        // Modify request if needed
        if (args[0].includes('api.example.com')) {
            const modifiedInit = args[1] || {};
            modifiedInit.headers = {
                ...modifiedInit.headers,
                'X-Custom-Header': 'MyValue'
            };
            args[1] = modifiedInit;
        }

        return fetch.apply(this, args)
            .then(response => {
                console.log('Fetch response:', response.url, response.status);
                return response;
            });
    };
})(window.fetch);
```

### Creating Draggable UI Panels

```javascript
function createDraggablePanel(content) {
    const panel = document.createElement('div');
    panel.innerHTML = `
        <div class="panel-header" style="cursor: move; background: #333; color: white; padding: 10px;">
            Drag Me
            <button class="close-btn" style="float: right;">×</button>
        </div>
        <div class="panel-content" style="background: white; padding: 15px;">
            ${content}
        </div>
    `;

    panel.style.cssText = 'position: fixed; top: 50px; right: 50px; width: 300px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.3); z-index: 99999;';

    // Make draggable
    const header = panel.querySelector('.panel-header');
    let isDragging = false;
    let currentX, currentY, initialX, initialY;

    header.addEventListener('mousedown', (e) => {
        isDragging = true;
        initialX = e.clientX - panel.offsetLeft;
        initialY = e.clientY - panel.offsetTop;
    });

    document.addEventListener('mousemove', (e) => {
        if (isDragging) {
            e.preventDefault();
            currentX = e.clientX - initialX;
            currentY = e.clientY - initialY;
            panel.style.left = currentX + 'px';
            panel.style.top = currentY + 'px';
            panel.style.right = 'auto';
        }
    });

    document.addEventListener('mouseup', () => isDragging = false);

    // Close button
    panel.querySelector('.close-btn').addEventListener('click', () => panel.remove());

    document.body.appendChild(panel);
    return panel;
}

// Usage
createDraggablePanel('<h3>Settings</h3><p>Your content here</p>');
```

### Keyboard Shortcuts

```javascript
// Register keyboard shortcuts
function registerHotkey(keys, callback) {
    const keysArray = keys.toLowerCase().split('+').map(k => k.trim());

    document.addEventListener('keydown', (e) => {
        const pressed = [];
        if (e.ctrlKey) pressed.push('ctrl');
        if (e.altKey) pressed.push('alt');
        if (e.shiftKey) pressed.push('shift');
        if (e.metaKey) pressed.push('meta');
        pressed.push(e.key.toLowerCase());

        if (pressed.sort().join('+') === keysArray.sort().join('+')) {
            e.preventDefault();
            callback(e);
        }
    });
}

// Usage
registerHotkey('ctrl+shift+x', () => {
    console.log('Hotkey triggered!');
    // Your action here
});
```

## Troubleshooting

### Script Not Running

1. Check @match or @include patterns match current URL
2. Verify @run-at timing is appropriate
3. Check console for JavaScript errors
4. Ensure Tampermonkey is enabled for the site
5. Try incognito mode to rule out conflicts

### Element Not Found

1. Check if page is SPA (needs navigation detection)
2. Increase wait timeout
3. Verify selector is correct (use DevTools)
4. Check if element is in iframe
5. Use MutationObserver instead of fixed delays

### Performance Issues

1. Remove unused @grant declarations
2. Debounce/throttle event handlers
3. Cache DOM queries
4. Use event delegation
5. Check for memory leaks (console → Memory profiler)

### CSP (Content Security Policy) Errors

1. Use `GM_addStyle` instead of inline styles
2. Use `@grant unsafeWindow` if accessing page context
3. Avoid inline event handlers (use addEventListener)
4. Use `GM_xmlhttpRequest` for external requests

## Best Practices Summary

1. **Always declare @grant** - Even if using `none`
2. **Use MutationObserver** - For dynamic content
3. **Cache DOM references** - Query once, use many times
4. **Handle errors gracefully** - Wrap in try-catch blocks
5. **Prefix console logs** - Easy filtering in DevTools
6. **Version your scripts** - Use @version for updates
7. **Document dependencies** - List in @description or comments
8. **Test in incognito** - Catch extension conflicts
9. **Respect site performance** - Don't block rendering
10. **Follow site ToS** - Don't abuse automation

## Templates Available

- `templates/basic-template.user.js` - Minimal starter template
- `templates/advanced-template.user.js` - Full-featured with utilities
- `templates/api-integration.user.js` - Cross-origin API requests
- `templates/ui-enhancement.user.js` - DOM manipulation & styling
- `templates/spa-compatible.user.js` - Single Page Application support

## Scripts Available

- `scripts/generate-userscript.sh` - Generate new userscript from template
- `scripts/validate-userscript.sh` - Validate script for common issues
- `scripts/extract-metadata.sh` - Extract and validate metadata block
- `scripts/bundle-library.sh` - Bundle external libraries into script

## Reference

- **Tampermonkey Documentation**: https://www.tampermonkey.net/documentation.php
- **GreasyFork Best Practices**: https://greasyfork.org/help/code-rules
- **GM API Reference**: https://wiki.greasespot.net/Greasemonkey_Manual:API
- **UserScript Examples**: `examples/` directory
