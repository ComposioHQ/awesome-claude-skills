// ==UserScript==
// @name         Advanced Userscript Template
// @namespace    http://tampermonkey.net/
// @version      1.0.0
// @description  Full-featured template with utilities, error handling, and modern patterns
// @author       Your Name
// @match        https://example.com/*
// @icon         https://www.google.com/s2/favicons?sz=64&domain=example.com
// @grant        GM_setValue
// @grant        GM_getValue
// @grant        GM_addStyle
// @grant        GM_xmlhttpRequest
// @run-at       document-end
// ==/UserScript==

(function() {
    'use strict';

    // ========================================
    // Configuration
    // ========================================
    const CONFIG = {
        DEBUG: true,
        SCRIPT_NAME: 'Advanced Userscript',
        VERSION: '1.0.0'
    };

    // ========================================
    // Utilities
    // ========================================
    const Utils = {
        // Logging with script prefix
        log: (...args) => {
            if (CONFIG.DEBUG) {
                console.log(`[${CONFIG.SCRIPT_NAME}]`, ...args);
            }
        },

        error: (...args) => {
            console.error(`[${CONFIG.SCRIPT_NAME}]`, ...args);
        },

        // Wait for element with timeout
        waitForElement: (selector, timeout = 10000) => {
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
                        reject(new Error(`Timeout waiting for: ${selector}`));
                    }
                });

                observer.observe(document.body, {
                    childList: true,
                    subtree: true
                });
            });
        },

        // Debounce function
        debounce: (func, wait) => {
            let timeout;
            return function executedFunction(...args) {
                clearTimeout(timeout);
                timeout = setTimeout(() => func.apply(this, args), wait);
            };
        },

        // Create element with attributes
        createElement: (tag, attrs = {}, children = []) => {
            const element = document.createElement(tag);

            Object.entries(attrs).forEach(([key, value]) => {
                if (key === 'style' && typeof value === 'object') {
                    Object.assign(element.style, value);
                } else if (key === 'dataset' && typeof value === 'object') {
                    Object.entries(value).forEach(([dataKey, dataValue]) => {
                        element.dataset[dataKey] = dataValue;
                    });
                } else {
                    element.setAttribute(key, value);
                }
            });

            children.forEach(child => {
                if (typeof child === 'string') {
                    element.appendChild(document.createTextNode(child));
                } else {
                    element.appendChild(child);
                }
            });

            return element;
        }
    };

    // ========================================
    // Settings Manager
    // ========================================
    class Settings {
        constructor(defaults = {}) {
            this.defaults = defaults;
        }

        get(key) {
            const value = GM_getValue(key);
            return value !== undefined ? value : this.defaults[key];
        }

        set(key, value) {
            GM_setValue(key, value);
            Utils.log(`Setting updated: ${key} = ${value}`);
        }

        getAll() {
            const settings = {};
            for (const key in this.defaults) {
                settings[key] = this.get(key);
            }
            return settings;
        }
    }

    const settings = new Settings({
        enabled: true,
        theme: 'dark'
    });

    // ========================================
    // Style Injection
    // ========================================
    GM_addStyle(`
        .userscript-element {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            transition: all 0.2s ease;
        }
    `);

    // ========================================
    // Main Script Logic
    // ========================================
    class ScriptMain {
        constructor() {
            this.initialized = false;
        }

        async init() {
            try {
                Utils.log(`Initializing v${CONFIG.VERSION}`);

                if (!settings.get('enabled')) {
                    Utils.log('Script is disabled in settings');
                    return;
                }

                await this.setupEventListeners();
                await this.modifyPage();

                this.initialized = true;
                Utils.log('Initialization complete');
            } catch (error) {
                Utils.error('Initialization failed:', error);
            }
        }

        async setupEventListeners() {
            // Add your event listeners here
            Utils.log('Event listeners setup complete');
        }

        async modifyPage() {
            // Add your page modification logic here
            Utils.log('Page modifications applied');
        }

        destroy() {
            // Cleanup logic
            this.initialized = false;
            Utils.log('Script destroyed');
        }
    }

    // ========================================
    // Initialization
    // ========================================
    const script = new ScriptMain();

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => script.init());
    } else {
        script.init();
    }

    // Expose to window for debugging
    if (CONFIG.DEBUG) {
        window.UserScript = {
            script,
            settings,
            utils: Utils,
            config: CONFIG
        };
        Utils.log('Debug mode: window.UserScript available');
    }
})();
