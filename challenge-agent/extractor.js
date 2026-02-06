// extractor.js - JavaScript injection module for hidden content extraction
// Contains 5 scripts that get injected into browser pages

const CONSOLE_CAPTURE_INIT = `
(function() {
  if (window.__consoleCaptured) return;
  window.__consoleCaptured = true;
  window.__capturedLogs = [];
  
  const originalLog = console.log;
  const originalWarn = console.warn;
  const originalError = console.error;
  const originalInfo = console.info;
  const originalDebug = console.debug;
  
  function capture(type, args) {
    try {
      const msg = Array.from(args).map(a => {
        if (typeof a === 'object') return JSON.stringify(a);
        return String(a);
      }).join(' ');
      window.__capturedLogs.push({ type, message: msg, timestamp: Date.now() });
    } catch(e) {}
  }
  
  console.log = function(...args) { capture('log', args); return originalLog.apply(console, args); };
  console.warn = function(...args) { capture('warn', args); return originalWarn.apply(console, args); };
  console.error = function(...args) { capture('error', args); return originalError.apply(console, args); };
  console.info = function(...args) { capture('info', args); return originalInfo.apply(console, args); };
  console.debug = function(...args) { capture('debug', args); return originalDebug.apply(console, args); };
})();
`;

const GET_CONSOLE_LOGS = `
(function() {
  return window.__capturedLogs || [];
})();
`;

const EXTRACT_PAGE_DATA = `
(function() {
  const result = {
    url: window.location.href,
    title: document.title,
    bodyText: '',
    comments: [],
    hiddenElements: [],
    dataAttributes: [],
    ariaLabels: [],
    pseudoContent: [],
    cssVariables: [],
    camouflaged: [],
    microFont: [],
    offscreen: [],
    metaTags: [],
    inlineScripts: [],
    storage: { localStorage: {}, sessionStorage: {}, cookies: '' },
    globalVars: {},
    inputFields: [],
    buttons: [],
    links: [],
    imageText: [],
    shadowDOM: [],
    noscript: [],
    styleContent: [],
    iframes: [],
    canvas: [],
    customElements: [],
    pageStructure: ''
  };
  
  try {
    // Body text
    result.bodyText = document.body ? document.body.innerText.substring(0, 10000) : '';
    
    // HTML comments
    const walker = document.createTreeWalker(document, NodeFilter.SHOW_COMMENT, null, false);
    while (walker.nextNode()) {
      const text = walker.currentNode.textContent.trim();
      if (text) result.comments.push(text);
    }
    
    // Hidden elements (display:none, visibility:hidden, opacity:0, etc.)
    const allElements = document.querySelectorAll('*');
    allElements.forEach(el => {
      try {
        const style = window.getComputedStyle(el);
        const isHidden = 
          style.display === 'none' ||
          style.visibility === 'hidden' ||
          style.opacity === '0' ||
          el.getAttribute('aria-hidden') === 'true' ||
          style.clipPath === 'inset(100%)' ||
          parseInt(style.textIndent) < -9000 ||
          style.transform === 'scale(0)' ||
          (style.position === 'absolute' && style.clip === 'rect(0px, 0px, 0px, 0px)');
        
        if (isHidden && el.textContent.trim()) {
          result.hiddenElements.push({
            tag: el.tagName,
            text: el.textContent.trim().substring(0, 500),
            reason: style.display === 'none' ? 'display:none' : 
                   style.visibility === 'hidden' ? 'visibility:hidden' :
                   style.opacity === '0' ? 'opacity:0' : 'other'
          });
        }
      } catch(e) {}
    });
    
    // Data attributes
    allElements.forEach(el => {
      try {
        for (const attr of el.attributes) {
          if (attr.name.startsWith('data-')) {
            result.dataAttributes.push({
              element: el.tagName,
              attr: attr.name,
              value: attr.value
            });
          }
        }
      } catch(e) {}
    });
    
    // Aria labels, titles, placeholders, alt text
    allElements.forEach(el => {
      try {
        const ariaLabel = el.getAttribute('aria-label');
        const title = el.getAttribute('title');
        const placeholder = el.getAttribute('placeholder');
        const alt = el.getAttribute('alt');
        
        if (ariaLabel) result.ariaLabels.push({ tag: el.tagName, ariaLabel });
        if (title) result.ariaLabels.push({ tag: el.tagName, title });
        if (placeholder) result.ariaLabels.push({ tag: el.tagName, placeholder });
        if (alt) result.imageText.push({ tag: el.tagName, alt });
      } catch(e) {}
    });
    
    // CSS ::before/::after pseudo-content
    allElements.forEach(el => {
      try {
        const before = window.getComputedStyle(el, '::before').content;
        const after = window.getComputedStyle(el, '::after').content;
        if (before && before !== 'none' && before !== 'normal') {
          result.pseudoContent.push({ element: el.tagName, pseudo: 'before', content: before });
        }
        if (after && after !== 'none' && after !== 'normal') {
          result.pseudoContent.push({ element: el.tagName, pseudo: 'after', content: after });
        }
      } catch(e) {}
    });
    
    // CSS custom properties (variables)
    const styleSheets = document.styleSheets;
    for (let i = 0; i < styleSheets.length; i++) {
      try {
        const rules = styleSheets[i].cssRules || styleSheets[i].rules;
        for (let j = 0; j < rules.length; j++) {
          const rule = rules[j];
          if (rule.style) {
            for (let k = 0; k < rule.style.length; k++) {
              const prop = rule.style[k];
              if (prop.startsWith('--')) {
                result.cssVariables.push({
                  property: prop,
                  value: rule.style.getPropertyValue(prop)
                });
              }
            }
          }
        }
      } catch(e) {} // CORS may block external stylesheets
    }
    
    // Root CSS variables
    const rootStyle = getComputedStyle(document.documentElement);
    ['--answer', '--secret', '--code', '--password', '--key', '--flag', '--hidden'].forEach(varName => {
      const val = rootStyle.getPropertyValue(varName);
      if (val) result.cssVariables.push({ property: varName, value: val.trim() });
    });
    
    // Camouflaged text (same color as background)
    allElements.forEach(el => {
      try {
        const style = window.getComputedStyle(el);
        const color = style.color;
        const bgColor = style.backgroundColor;
        if (color === bgColor && el.textContent.trim() && color !== 'rgba(0, 0, 0, 0)') {
          result.camouflaged.push({
            tag: el.tagName,
            text: el.textContent.trim().substring(0, 200),
            color
          });
        }
      } catch(e) {}
    });
    
    // Micro-font elements (<4px)
    allElements.forEach(el => {
      try {
        const style = window.getComputedStyle(el);
        const fontSize = parseFloat(style.fontSize);
        if (fontSize > 0 && fontSize < 4 && el.textContent.trim()) {
          result.microFont.push({
            tag: el.tagName,
            text: el.textContent.trim().substring(0, 200),
            fontSize
          });
        }
      } catch(e) {}
    });
    
    // Offscreen elements
    allElements.forEach(el => {
      try {
        const rect = el.getBoundingClientRect();
        const style = window.getComputedStyle(el);
        const left = parseFloat(style.left) || 0;
        const top = parseFloat(style.top) || 0;
        
        if ((rect.right < 0 || rect.bottom < 0 || left < -5000 || top < -5000) && el.textContent.trim()) {
          result.offscreen.push({
            tag: el.tagName,
            text: el.textContent.trim().substring(0, 200)
          });
        }
      } catch(e) {}
    });
    
    // Meta tags
    document.querySelectorAll('meta').forEach(meta => {
      result.metaTags.push({
        name: meta.getAttribute('name') || meta.getAttribute('property') || '',
        content: meta.getAttribute('content') || ''
      });
    });
    
    // Inline scripts (look for variable assignments)
    document.querySelectorAll('script:not([src])').forEach(script => {
      const text = script.textContent;
      // Look for patterns like: var answer = "X", const secret = 'Y', let code = \`Z\`
      const patterns = [
        /(?:var|let|const)\s+(\w*(?:answer|secret|code|key|flag|password|hidden)\w*)\s*=\s*['"\`]([^'"\`]+)['"\`]/gi,
        /['"]?(?:answer|secret|code|key|flag|password)['"]?\s*[:=]\s*['"\`]([^'"\`]+)['"\`]/gi
      ];
      patterns.forEach(pattern => {
        let match;
        while ((match = pattern.exec(text)) !== null) {
          result.inlineScripts.push({ match: match[0], value: match[1] || match[2] });
        }
      });
    });
    
    // Storage
    try {
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        result.storage.localStorage[key] = localStorage.getItem(key);
      }
    } catch(e) {}
    
    try {
      for (let i = 0; i < sessionStorage.length; i++) {
        const key = sessionStorage.key(i);
        result.storage.sessionStorage[key] = sessionStorage.getItem(key);
      }
    } catch(e) {}
    
    try {
      result.storage.cookies = document.cookie;
    } catch(e) {}
    
    // Global JS variables
    const globalVarNames = ['answer', 'secret', 'code', 'key', 'flag', 'password', 'hidden', 
                           'secretAnswer', 'theAnswer', 'correctAnswer', 'solution', 'result'];
    globalVarNames.forEach(name => {
      try {
        if (window[name] !== undefined) {
          result.globalVars[name] = String(window[name]);
        }
      } catch(e) {}
    });
    
    // Input fields with context
    document.querySelectorAll('input, textarea').forEach(input => {
      const label = document.querySelector(\`label[for="\${input.id}"]\`);
      result.inputFields.push({
        type: input.type || 'text',
        id: input.id,
        name: input.name,
        placeholder: input.placeholder,
        value: input.value,
        label: label ? label.textContent.trim() : '',
        selector: input.id ? \`#\${input.id}\` : (input.name ? \`[name="\${input.name}"]\` : 'input')
      });
    });
    
    // Buttons
    document.querySelectorAll('button, input[type="submit"], input[type="button"], [role="button"]').forEach(btn => {
      result.buttons.push({
        text: btn.textContent.trim() || btn.value || '',
        type: btn.type,
        id: btn.id,
        selector: btn.id ? \`#\${btn.id}\` : (btn.textContent.trim() ? \`button:has-text("\${btn.textContent.trim().substring(0,30)}")\` : 'button')
      });
    });
    
    // Links
    document.querySelectorAll('a').forEach(a => {
      result.links.push({
        text: a.textContent.trim().substring(0, 100),
        href: a.href
      });
    });
    
    // SVG text
    document.querySelectorAll('svg text, svg tspan').forEach(el => {
      if (el.textContent.trim()) {
        result.imageText.push({ tag: 'SVG', text: el.textContent.trim() });
      }
    });
    
    // Shadow DOM
    allElements.forEach(el => {
      try {
        if (el.shadowRoot) {
          result.shadowDOM.push({
            host: el.tagName,
            content: el.shadowRoot.innerHTML.substring(0, 500)
          });
        }
      } catch(e) {}
    });
    
    // Noscript
    document.querySelectorAll('noscript').forEach(el => {
      result.noscript.push(el.textContent.trim());
    });
    
    // Style tag content (look for strings)
    document.querySelectorAll('style').forEach(style => {
      const text = style.textContent;
      // Look for content: "..." patterns
      const matches = text.match(/content:\s*['"]([^'"]+)['"]/g);
      if (matches) result.styleContent.push(...matches);
    });
    
    // Iframes
    document.querySelectorAll('iframe').forEach(iframe => {
      try {
        result.iframes.push({
          src: iframe.src,
          content: iframe.contentDocument ? iframe.contentDocument.body.innerText.substring(0, 500) : ''
        });
      } catch(e) {
        result.iframes.push({ src: iframe.src, content: '[cross-origin]' });
      }
    });
    
    // Canvas detection
    document.querySelectorAll('canvas').forEach(canvas => {
      result.canvas.push({
        id: canvas.id,
        width: canvas.width,
        height: canvas.height
      });
    });
    
    // Custom elements
    allElements.forEach(el => {
      if (el.tagName.includes('-')) {
        result.customElements.push({
          tag: el.tagName,
          text: el.textContent.trim().substring(0, 200)
        });
      }
    });
    
    // Page structure summary
    const headings = Array.from(document.querySelectorAll('h1,h2,h3')).map(h => h.textContent.trim()).join(' | ');
    result.pageStructure = headings.substring(0, 500);
    
  } catch(e) {
    result.error = e.message;
  }
  
  return result;
})();
`;

const DETECT_INTERACTIONS = `
(function() {
  const interactions = [];
  
  // Clickable elements
  document.querySelectorAll('button, a, [onclick], [role="button"], .clickable, .btn').forEach(el => {
    if (el.offsetParent !== null) { // visible
      interactions.push({
        type: 'click',
        selector: el.id ? \`#\${el.id}\` : (el.className ? \`.\${el.className.split(' ')[0]}\` : el.tagName.toLowerCase()),
        text: el.textContent.trim().substring(0, 50)
      });
    }
  });
  
  // Hoverable elements
  document.querySelectorAll('[onmouseover], [onmouseenter], .hover, .tooltip').forEach(el => {
    if (el.offsetParent !== null) {
      interactions.push({
        type: 'hover',
        selector: el.id ? \`#\${el.id}\` : el.tagName.toLowerCase(),
        text: el.textContent.trim().substring(0, 50)
      });
    }
  });
  
  // Draggable elements
  document.querySelectorAll('[draggable="true"], .draggable, .drag').forEach(el => {
    interactions.push({
      type: 'drag',
      selector: el.id ? \`#\${el.id}\` : el.tagName.toLowerCase()
    });
  });
  
  // Select elements
  document.querySelectorAll('select').forEach(el => {
    const options = Array.from(el.options).map(o => ({ value: o.value, text: o.text }));
    interactions.push({
      type: 'select',
      selector: el.id ? \`#\${el.id}\` : 'select',
      options
    });
  });
  
  // Elements with keyboard handlers
  document.querySelectorAll('[onkeydown], [onkeyup], [onkeypress]').forEach(el => {
    interactions.push({
      type: 'keyboard',
      selector: el.id ? \`#\${el.id}\` : el.tagName.toLowerCase()
    });
  });
  
  return interactions;
})();
`;

const CHECK_RESULT = `
(function() {
  const bodyText = document.body.innerText.toLowerCase();
  const html = document.documentElement.innerHTML.toLowerCase();
  
  const successPatterns = [
    /correct/i, /success/i, /well done/i, /congratulations/i, /✅/, /✓/,
    /passed/i, /completed/i, /solved/i, /great job/i, /right answer/i,
    /you got it/i, /that's right/i, /perfect/i, /excellent/i
  ];
  
  const failurePatterns = [
    /incorrect/i, /wrong/i, /try again/i, /failed/i, /❌/, /✗/,
    /not correct/i, /nope/i, /error/i, /invalid/i
  ];
  
  const completionPatterns = [
    /challenge complete/i, /all challenges/i, /finished/i, /final/i,
    /you've completed/i, /all done/i
  ];
  
  let success = false;
  let failure = false;
  let completion = false;
  
  for (const p of successPatterns) {
    if (p.test(bodyText) || p.test(html)) { success = true; break; }
  }
  
  for (const p of failurePatterns) {
    if (p.test(bodyText) || p.test(html)) { failure = true; break; }
  }
  
  for (const p of completionPatterns) {
    if (p.test(bodyText) || p.test(html)) { completion = true; break; }
  }
  
  // Check for challenge number change
  const challengeMatch = bodyText.match(/(?:challenge|step|level)\\s*(\\d+)/i);
  const challengeNumber = challengeMatch ? parseInt(challengeMatch[1]) : null;
  
  return { success, failure, completion, challengeNumber, bodyTextSample: bodyText.substring(0, 500) };
})();
`;

// Export for Node.js (used by browser.py to read these)
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    CONSOLE_CAPTURE_INIT,
    GET_CONSOLE_LOGS,
    EXTRACT_PAGE_DATA,
    DETECT_INTERACTIONS,
    CHECK_RESULT
  };
}
