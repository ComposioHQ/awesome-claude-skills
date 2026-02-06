"""
browser.py - Playwright wrapper with SPA awareness and hidden content extraction
"""

import asyncio
import re
import os
from typing import Optional, Dict, List, Any
from playwright.async_api import async_playwright, Page, Browser, BrowserContext

# Inline JavaScript for extraction (to avoid parsing issues)
CONSOLE_CAPTURE_INIT = """
(function() {
  if (window.__consoleCaptured) return;
  window.__consoleCaptured = true;
  window.__capturedLogs = [];
  const origLog = console.log;
  const origWarn = console.warn;
  const origError = console.error;
  console.log = function(...args) { window.__capturedLogs.push({type:'log',msg:args.map(String).join(' ')}); origLog.apply(console, args); };
  console.warn = function(...args) { window.__capturedLogs.push({type:'warn',msg:args.map(String).join(' ')}); origWarn.apply(console, args); };
  console.error = function(...args) { window.__capturedLogs.push({type:'error',msg:args.map(String).join(' ')}); origError.apply(console, args); };
})();
"""

GET_CONSOLE_LOGS = "(function() { return window.__capturedLogs || []; })();"

EXTRACT_PAGE_DATA = """
(function() {
  const result = {
    url: window.location.href,
    title: document.title,
    bodyText: document.body ? document.body.innerText : '',
    comments: [],
    hiddenElements: [],
    dataAttributes: [],
    pseudoContent: [],
    cssVariables: [],
    globalVars: {},
    storage: {},
    inputFields: [],
    buttons: [],
    links: [],
    dialog_messages: []
  };
  
  // HTML comments
  const walker = document.createTreeWalker(document, NodeFilter.SHOW_COMMENT, null, false);
  while (walker.nextNode()) {
    const text = walker.currentNode.textContent.trim();
    if (text) result.comments.push(text);
  }
  
  // Hidden elements
  document.querySelectorAll('*').forEach(el => {
    try {
      const style = window.getComputedStyle(el);
      if ((style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0') && el.textContent.trim()) {
        result.hiddenElements.push({tag: el.tagName, text: el.textContent.trim().slice(0,200)});
      }
    } catch(e) {}
  });
  
  // Data attributes
  document.querySelectorAll('*').forEach(el => {
    for (const attr of el.attributes || []) {
      if (attr.name.startsWith('data-')) {
        result.dataAttributes.push({attr: attr.name, value: attr.value});
      }
    }
  });
  
  // Global JS vars
  ['answer', 'secret', 'code', 'key', 'flag', 'password'].forEach(name => {
    try { if (window[name] !== undefined) result.globalVars[name] = String(window[name]); } catch(e) {}
  });
  
  // Storage
  try { result.storage.cookies = document.cookie; } catch(e) {}
  try {
    const ls = {};
    for (let i = 0; i < localStorage.length; i++) {
      const k = localStorage.key(i);
      ls[k] = localStorage.getItem(k);
    }
    result.storage.localStorage = ls;
  } catch(e) {}
  
  // Input fields
  document.querySelectorAll('input, textarea').forEach(input => {
    const label = document.querySelector('label[for="' + input.id + '"]');
    result.inputFields.push({
      type: input.type || 'text',
      id: input.id,
      name: input.name,
      placeholder: input.placeholder,
      selector: input.id ? '#' + input.id : (input.name ? '[name="' + input.name + '"]' : 'input'),
      label: label ? label.textContent.trim() : ''
    });
  });
  
  // Buttons
  document.querySelectorAll('button, input[type="submit"], [role="button"]').forEach(btn => {
    const text = btn.textContent.trim() || btn.value || '';
    if (text) {
      result.buttons.push({text: text.slice(0,50), id: btn.id});
    }
  });
  
  // Links
  document.querySelectorAll('a').forEach(a => {
    result.links.push({text: a.textContent.trim().slice(0,50), href: a.href});
  });
  
  return result;
})();
"""

DETECT_INTERACTIONS = """
(function() {
  const interactions = [];
  document.querySelectorAll('button, a, [onclick], [role="button"]').forEach(el => {
    if (el.offsetParent !== null) {
      interactions.push({type: 'click', text: el.textContent.trim().slice(0,50)});
    }
  });
  document.querySelectorAll('select').forEach(el => {
    const options = Array.from(el.options).map(o => ({value: o.value, text: o.text}));
    interactions.push({type: 'select', options});
  });
  return interactions;
})();
"""

CHECK_RESULT = """
(function() {
  const text = (document.body.innerText || '').toLowerCase();
  const success = /correct|success|well done|congratulations|passed|solved/.test(text);
  const failure = /incorrect|wrong|try again|failed|invalid/.test(text);
  const match = text.match(/step\\s*(\\d+)/i);
  const stepNumber = match ? parseInt(match[1]) : null;
  return {success, failure, challengeNumber: stepNumber, bodyTextSample: text.slice(0,300)};
})();
"""


class BrowserController:
    """Playwright browser wrapper with extraction capabilities"""
    
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.dialog_messages: List[str] = []
        
    async def start(self):
        """Start browser with console capture init script"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )
        self.context = await self.browser.new_context(
            viewport={'width': 1280, 'height': 900},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        
        # Install console capture BEFORE any page JavaScript runs
        await self.context.add_init_script(CONSOLE_CAPTURE_INIT)
        
        self.page = await self.context.new_page()
        
        # Handle dialogs (alert, confirm, prompt)
        self.page.on("dialog", self._handle_dialog)
        
    async def _handle_dialog(self, dialog):
        """Capture dialog messages and dismiss"""
        self.dialog_messages.append({
            'type': dialog.type,
            'message': dialog.message
        })
        await dialog.accept()
        
    async def close(self):
        """Close browser"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
            
    async def navigate(self, url: str, timeout: int = 30000):
        """Navigate to URL with wait for render"""
        self.dialog_messages = []  # Clear dialogs
        await self.page.goto(url, wait_until='networkidle', timeout=timeout)
        # Extra render delay for SPAs
        await asyncio.sleep(1.5)
        # Wait for any spinners to disappear
        try:
            await self.page.wait_for_selector('.loading, .spinner, [class*="load"]', 
                                              state='hidden', timeout=3000)
        except:
            pass
            
    async def reload_page(self):
        """Full reload to clear stale state"""
        self.dialog_messages = []
        await self.page.reload(wait_until='networkidle')
        await asyncio.sleep(1.0)
        
    async def get_current_url(self) -> str:
        """Get current page URL"""
        return self.page.url
        
    async def extract_page_data(self) -> Dict[str, Any]:
        """Run the 25-category extractor"""
        try:
            data = await self.page.evaluate(EXTRACT_PAGE_DATA)
            data['dialog_messages'] = self.dialog_messages
            return data
        except Exception as e:
            return {'error': str(e), 'dialog_messages': self.dialog_messages}
            
    async def get_console_logs(self) -> List[Dict]:
        """Get captured console output"""
        try:
            return await self.page.evaluate(GET_CONSOLE_LOGS)
        except:
            return []
            
    async def detect_interactions(self) -> List[Dict]:
        """Find interactive elements"""
        try:
            return await self.page.evaluate(DETECT_INTERACTIONS)
        except:
            return []
            
    async def check_result(self) -> Dict[str, Any]:
        """Check for success/failure/completion indicators"""
        try:
            return await self.page.evaluate(CHECK_RESULT)
        except Exception as e:
            return {'error': str(e)}
            
    async def click(self, selector: str, timeout: int = 5000) -> bool:
        """Click an element"""
        try:
            await self.page.click(selector, timeout=timeout)
            await asyncio.sleep(0.3)
            return True
        except Exception as e:
            return False
            
    async def type_text(self, selector: str, text: str, timeout: int = 5000) -> bool:
        """Type text into an input field"""
        try:
            await self.page.fill(selector, text, timeout=timeout)
            return True
        except Exception as e:
            # Try clicking first then typing
            try:
                await self.page.click(selector, timeout=timeout)
                await self.page.keyboard.type(text)
                return True
            except:
                return False
                
    async def submit_form(self, input_selector: str = None) -> bool:
        """Submit form by pressing Enter or clicking submit button"""
        try:
            if input_selector:
                await self.page.click(input_selector)
            await self.page.keyboard.press('Enter')
            await asyncio.sleep(0.5)
            return True
        except:
            return False
            
    async def click_button(self, button_selector: str, timeout: int = 5000) -> bool:
        """Click a submit/action button"""
        try:
            await self.page.click(button_selector, timeout=timeout)
            await asyncio.sleep(0.5)
            return True
        except:
            return False
            
    async def hover(self, selector: str, timeout: int = 5000) -> bool:
        """Hover over an element"""
        try:
            await self.page.hover(selector, timeout=timeout)
            await asyncio.sleep(0.5)
            return True
        except:
            return False
            
    async def press_key(self, key: str) -> bool:
        """Press a keyboard key"""
        try:
            await self.page.keyboard.press(key)
            await asyncio.sleep(0.3)
            return True
        except:
            return False
            
    async def scroll(self, direction: str = 'down', amount: int = 500) -> bool:
        """Scroll the page"""
        try:
            delta = amount if direction == 'down' else -amount
            await self.page.evaluate(f'window.scrollBy(0, {delta})')
            await asyncio.sleep(0.3)
            return True
        except:
            return False
            
    async def select_option(self, selector: str, value: str) -> bool:
        """Select an option from a dropdown"""
        try:
            await self.page.select_option(selector, value)
            await asyncio.sleep(0.3)
            return True
        except:
            return False
            
    async def drag(self, source_selector: str, target_selector: str) -> bool:
        """Drag element to target"""
        try:
            await self.page.drag_and_drop(source_selector, target_selector)
            await asyncio.sleep(0.5)
            return True
        except:
            return False
            
    async def take_screenshot_base64(self) -> str:
        """Take screenshot and return as base64"""
        try:
            screenshot = await self.page.screenshot(type='png')
            import base64
            return base64.b64encode(screenshot).decode('utf-8')
        except:
            return ""
            
    async def execute_js(self, script: str) -> Any:
        """Run arbitrary JavaScript"""
        try:
            return await self.page.evaluate(script)
        except Exception as e:
            return {'error': str(e)}
            
    async def wait_for_navigation(self, timeout: int = 10000):
        """Wait for navigation to complete"""
        try:
            await self.page.wait_for_load_state('networkidle', timeout=timeout)
        except:
            pass
            
    async def get_page_content(self) -> str:
        """Get full page HTML"""
        try:
            return await self.page.content()
        except:
            return ""
