// ==UserScript==
// @name         My Userscript
// @namespace    http://tampermonkey.net/
// @version      1.0.0
// @description  Brief description of what this script does
// @author       Your Name
// @match        https://example.com/*
// @icon         https://www.google.com/s2/favicons?sz=64&domain=example.com
// @grant        none
// @run-at       document-end
// ==/UserScript==

(function() {
    'use strict';

    // Your code here
    console.log('[My Userscript] Script loaded successfully');

    // Wait for DOM to be ready
    function init() {
        // Add your initialization code here
        console.log('[My Userscript] Initialized');
    }

    // Run initialization
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
