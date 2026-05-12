// ==UserScript==
// @name         YouTube Timestamp Bookmarker
// @namespace    http://tampermonkey.net/
// @version      1.0.0
// @description  Add bookmarks to YouTube videos at specific timestamps
// @author       Example Author
// @match        https://www.youtube.com/watch?v=*
// @icon         https://www.google.com/s2/favicons?sz=64&domain=youtube.com
// @grant        GM_setValue
// @grant        GM_getValue
// @grant        GM_addStyle
// @run-at       document-end
// ==/UserScript==

(function() {
    'use strict';

    const log = (...args) => console.log('[YT Bookmarker]', ...args);

    // Inject styles
    GM_addStyle(`
        .bookmark-panel {
            position: fixed;
            top: 80px;
            right: 20px;
            width: 300px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            z-index: 9999;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }

        .bookmark-header {
            background: #ff0000;
            color: white;
            padding: 12px 16px;
            border-radius: 8px 8px 0 0;
            font-weight: 600;
            cursor: move;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .bookmark-close {
            background: none;
            border: none;
            color: white;
            font-size: 20px;
            cursor: pointer;
            padding: 0;
            width: 24px;
            height: 24px;
        }

        .bookmark-content {
            padding: 16px;
            max-height: 400px;
            overflow-y: auto;
        }

        .bookmark-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 0;
            border-bottom: 1px solid #eee;
        }

        .bookmark-time {
            color: #065fd4;
            cursor: pointer;
            font-weight: 500;
        }

        .bookmark-time:hover {
            text-decoration: underline;
        }

        .bookmark-delete {
            background: #ff0000;
            color: white;
            border: none;
            padding: 4px 8px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
        }

        .add-bookmark-btn {
            background: #065fd4;
            color: white;
            border: none;
            padding: 10px 16px;
            border-radius: 4px;
            cursor: pointer;
            width: 100%;
            margin-top: 8px;
            font-weight: 500;
        }

        .toggle-panel-btn {
            position: fixed;
            top: 80px;
            right: 20px;
            background: #ff0000;
            color: white;
            border: none;
            padding: 12px 16px;
            border-radius: 8px;
            cursor: pointer;
            z-index: 9998;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
        }
    `);

    // Get video ID from URL
    function getVideoId() {
        const params = new URLSearchParams(window.location.search);
        return params.get('v');
    }

    // Get current video time
    function getCurrentTime() {
        const video = document.querySelector('video');
        return video ? Math.floor(video.currentTime) : 0;
    }

    // Jump to specific time
    function jumpToTime(seconds) {
        const video = document.querySelector('video');
        if (video) {
            video.currentTime = seconds;
            video.play();
        }
    }

    // Format seconds to MM:SS
    function formatTime(seconds) {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    }

    // Storage key for current video
    function getStorageKey() {
        return `bookmarks_${getVideoId()}`;
    }

    // Get bookmarks for current video
    function getBookmarks() {
        const stored = GM_getValue(getStorageKey(), '[]');
        return JSON.parse(stored);
    }

    // Save bookmarks for current video
    function saveBookmarks(bookmarks) {
        GM_setValue(getStorageKey(), JSON.stringify(bookmarks));
    }

    // Add bookmark at current time
    function addBookmark() {
        const time = getCurrentTime();
        const bookmarks = getBookmarks();

        // Check if bookmark already exists at this time
        if (bookmarks.some(b => b.time === time)) {
            alert('Bookmark already exists at this time!');
            return;
        }

        bookmarks.push({ time, note: '' });
        bookmarks.sort((a, b) => a.time - b.time);
        saveBookmarks(bookmarks);

        log('Bookmark added at', formatTime(time));
        renderBookmarks();
    }

    // Delete bookmark
    function deleteBookmark(time) {
        let bookmarks = getBookmarks();
        bookmarks = bookmarks.filter(b => b.time !== time);
        saveBookmarks(bookmarks);
        renderBookmarks();
    }

    // Create panel UI
    function createPanel() {
        const panel = document.createElement('div');
        panel.className = 'bookmark-panel';
        panel.innerHTML = `
            <div class="bookmark-header">
                <span>⏱️ Bookmarks</span>
                <button class="bookmark-close">×</button>
            </div>
            <div class="bookmark-content">
                <button class="add-bookmark-btn">➕ Add Bookmark at Current Time</button>
                <div id="bookmarks-list"></div>
            </div>
        `;

        document.body.appendChild(panel);

        // Close button
        panel.querySelector('.bookmark-close').addEventListener('click', () => {
            panel.style.display = 'none';
        });

        // Add bookmark button
        panel.querySelector('.add-bookmark-btn').addEventListener('click', addBookmark);

        // Make draggable
        makeDraggable(panel, panel.querySelector('.bookmark-header'));

        return panel;
    }

    // Render bookmarks list
    function renderBookmarks() {
        const list = document.getElementById('bookmarks-list');
        if (!list) return;

        const bookmarks = getBookmarks();

        if (bookmarks.length === 0) {
            list.innerHTML = '<p style="text-align: center; color: #999; margin-top: 16px;">No bookmarks yet</p>';
            return;
        }

        list.innerHTML = bookmarks.map(bookmark => `
            <div class="bookmark-item">
                <span class="bookmark-time" data-time="${bookmark.time}">
                    ${formatTime(bookmark.time)}
                </span>
                <button class="bookmark-delete" data-time="${bookmark.time}">Delete</button>
            </div>
        `).join('');

        // Add click handlers
        list.querySelectorAll('.bookmark-time').forEach(el => {
            el.addEventListener('click', () => {
                jumpToTime(parseInt(el.dataset.time));
            });
        });

        list.querySelectorAll('.bookmark-delete').forEach(el => {
            el.addEventListener('click', () => {
                deleteBookmark(parseInt(el.dataset.time));
            });
        });
    }

    // Make element draggable
    function makeDraggable(element, handle) {
        let isDragging = false;
        let currentX, currentY, initialX, initialY;

        handle.addEventListener('mousedown', (e) => {
            isDragging = true;
            initialX = e.clientX - element.offsetLeft;
            initialY = e.clientY - element.offsetTop;
        });

        document.addEventListener('mousemove', (e) => {
            if (isDragging) {
                e.preventDefault();
                currentX = e.clientX - initialX;
                currentY = e.clientY - initialY;
                element.style.left = currentX + 'px';
                element.style.top = currentY + 'px';
                element.style.right = 'auto';
            }
        });

        document.addEventListener('mouseup', () => {
            isDragging = false;
        });
    }

    // Create toggle button
    function createToggleButton() {
        const btn = document.createElement('button');
        btn.className = 'toggle-panel-btn';
        btn.textContent = '⏱️ Bookmarks';
        btn.addEventListener('click', () => {
            const panel = document.querySelector('.bookmark-panel');
            if (panel) {
                panel.style.display = panel.style.display === 'none' ? 'block' : 'none';
            }
        });
        document.body.appendChild(btn);
    }

    // Initialize
    async function init() {
        if (!getVideoId()) {
            log('Not on a video page');
            return;
        }

        log('Initializing for video:', getVideoId());

        // Wait for video player
        const waitForVideo = setInterval(() => {
            if (document.querySelector('video')) {
                clearInterval(waitForVideo);

                createToggleButton();
                const panel = createPanel();
                renderBookmarks();

                log('Ready!');
            }
        }, 500);
    }

    // Run on page load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
