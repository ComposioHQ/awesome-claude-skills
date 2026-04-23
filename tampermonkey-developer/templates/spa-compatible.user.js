// ==UserScript==
// @name         SPA-Compatible Template
// @namespace    http://tampermonkey.net/
// @version      1.0.0
// @description  Template for Single Page Applications (React, Vue, Angular)
// @author       Your Name
// @match        https://example.com/*
// @icon         https://www.google.com/s2/favicons?sz=64&domain=example.com
// @grant        none
// @run-at       document-end
// ==/UserScript==

(function() {
    'use strict';

    const SCRIPT_NAME = 'SPA Script';
    let lastUrl = location.href;

    // Log helper
    const log = (...args) => console.log(`[${SCRIPT_NAME}]`, ...args);

    // ========================================
    // Navigation Detection
    // ========================================
    function onLocationChange(callback) {
        // Watch for URL changes in SPAs
        new MutationObserver(() => {
            const currentUrl = location.href;
            if (currentUrl !== lastUrl) {
                lastUrl = currentUrl;
                log('Navigation detected:', currentUrl);
                callback(currentUrl);
            }
        }).observe(document, {
            subtree: true,
            childList: true
        });

        // Also listen to popstate for back/forward navigation
        window.addEventListener('popstate', () => {
            const currentUrl = location.href;
            if (currentUrl !== lastUrl) {
                lastUrl = currentUrl;
                log('Navigation detected (popstate):', currentUrl);
                callback(currentUrl);
            }
        });
    }

    // ========================================
    // Wait for Element (SPA-safe)
    // ========================================
    function waitForElement(selector, timeout = 10000) {
        return new Promise((resolve, reject) => {
            const startTime = Date.now();
            const element = document.querySelector(selector);

            if (element) {
                return resolve(element);
            }

            const observer = new MutationObserver(() => {
                const element = document.querySelector(selector);
                if (element) {
                    observer.disconnect();
                    resolve(element);
                } else if (Date.now() - startTime > timeout) {
                    observer.disconnect();
                    reject(new Error(`Timeout: ${selector}`));
                }
            });

            observer.observe(document.body, {
                childList: true,
                subtree: true
            });
        });
    }

    // ========================================
    // Route Matcher
    // ========================================
    class RouteHandler {
        constructor() {
            this.routes = [];
        }

        // Add route with pattern and handler
        add(pattern, handler) {
            this.routes.push({ pattern, handler });
            return this;
        }

        // Match current URL against routes
        match(url) {
            for (const route of this.routes) {
                let regex;

                if (route.pattern instanceof RegExp) {
                    regex = route.pattern;
                } else {
                    // Convert simple pattern to regex
                    // Example: "/user/:id" -> /^\/user\/([^\/]+)$/
                    const regexPattern = route.pattern
                        .replace(/:[^\s/]+/g, '([^/]+)')
                        .replace(/\*/g, '.*');
                    regex = new RegExp(`^${regexPattern}$`);
                }

                const match = url.match(regex);
                if (match) {
                    return { handler: route.handler, params: match.slice(1) };
                }
            }
            return null;
        }

        // Execute handler for current URL
        handle(url) {
            const result = this.match(url);
            if (result) {
                log('Route matched:', url);
                result.handler(...result.params);
                return true;
            }
            return false;
        }
    }

    // ========================================
    // Initialize Router
    // ========================================
    const router = new RouteHandler();

    // Define your routes
    router
        .add('/home', async () => {
            log('Home page handler');
            // Your home page logic
        })
        .add('/user/:id', async (userId) => {
            log('User page handler, ID:', userId);
            // Your user page logic
        })
        .add('/posts/:postId/comments', async (postId) => {
            log('Post comments handler, Post ID:', postId);
            // Your comments page logic
        })
        .add(/^\/search\?.*/, async () => {
            log('Search page handler');
            // Your search page logic
        });

    // ========================================
    // Main Script Logic
    // ========================================
    async function initPage() {
        try {
            log('Initializing page:', location.pathname);

            // Try to handle current route
            const handled = router.handle(location.pathname);

            if (!handled) {
                // Default handler for unmatched routes
                log('No specific route handler, running default logic');
                await defaultPageLogic();
            }
        } catch (error) {
            console.error(`[${SCRIPT_NAME}]`, 'Error initializing page:', error);
        }
    }

    async function defaultPageLogic() {
        // Your default page modification logic
        log('Default page logic executed');
    }

    // ========================================
    // Cleanup on Navigation
    // ========================================
    function cleanup() {
        // Remove event listeners, clear intervals, etc.
        log('Cleaning up previous page');
    }

    // ========================================
    // Start
    // ========================================
    log('Script loaded');

    // Initial page load
    initPage();

    // Watch for navigation changes
    onLocationChange((url) => {
        cleanup();
        initPage();
    });
})();
