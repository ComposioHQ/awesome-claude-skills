#!/usr/bin/env python3
"""
QA Bench Challenge Solver
Specialized agent for solving QA Bench web challenges (https://qa-bench.com)
Designed to complete all 30 challenges in under 5 minutes.
"""

import os
import sys
import time
import json
import base64
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from playwright.sync_api import sync_playwright, Page, Browser, ElementHandle
from anthropic import Anthropic

# Configuration
CHALLENGE_URL = os.getenv("CHALLENGE_URL", "https://qa-bench.com")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
MAX_TIME_SECONDS = 300  # 5 minutes
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "/tmp/qa_bench_results")


@dataclass 
class RunMetrics:
    """Comprehensive metrics tracking."""
    run_id: str = ""
    start_time: float = 0
    end_time: float = 0
    total_challenges: int = 30
    challenges_attempted: int = 0
    challenges_solved: int = 0
    challenges_failed: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    api_calls: int = 0
    per_challenge_metrics: Dict[int, Dict] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    
    @property
    def elapsed_seconds(self) -> float:
        end = self.end_time if self.end_time else time.time()
        return end - self.start_time
    
    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens
    
    @property
    def estimated_cost_usd(self) -> float:
        # Claude 3.5 Sonnet: $3/M input, $15/M output
        return (self.input_tokens / 1_000_000 * 3) + (self.output_tokens / 1_000_000 * 15)
    
    def to_report(self) -> dict:
        return {
            "run_id": self.run_id,
            "timestamp": datetime.now().isoformat(),
            "duration_seconds": round(self.elapsed_seconds, 2),
            "duration_formatted": f"{int(self.elapsed_seconds // 60)}m {int(self.elapsed_seconds % 60)}s",
            "under_5_minutes": self.elapsed_seconds < 300,
            "challenges": {
                "total": self.total_challenges,
                "attempted": self.challenges_attempted,
                "solved": self.challenges_solved,
                "failed": self.challenges_failed,
                "success_rate": f"{(self.challenges_solved / max(1, self.challenges_attempted)) * 100:.1f}%"
            },
            "tokens": {
                "input": self.input_tokens,
                "output": self.output_tokens,
                "total": self.total_tokens,
                "api_calls": self.api_calls
            },
            "cost": {
                "estimated_usd": f"${self.estimated_cost_usd:.4f}",
                "per_challenge_avg": f"${self.estimated_cost_usd / max(1, self.challenges_attempted):.6f}"
            },
            "per_challenge": self.per_challenge_metrics,
            "errors_count": len(self.errors),
            "errors": self.errors[:10]  # First 10 errors
        }


class QABenchSolver:
    """
    Intelligent solver for QA Bench challenges.
    Uses pattern matching and AI vision for complex challenges.
    """
    
    # Common challenge patterns and their solutions
    CHALLENGE_PATTERNS = {
        # Text input challenges
        "enter your name": {"action": "fill", "selector": "input", "value": "John Doe"},
        "enter email": {"action": "fill", "selector": "input[type='email'],input", "value": "test@example.com"},
        "type password": {"action": "fill", "selector": "input[type='password'],input", "value": "SecurePass123!"},
        "enter a number": {"action": "fill", "selector": "input[type='number'],input", "value": "42"},
        "enter text": {"action": "fill", "selector": "input,textarea", "value": "Hello World"},
        
        # Click challenges
        "click the button": {"action": "click", "selector": "button"},
        "click submit": {"action": "click", "selector": "button[type='submit'],button"},
        "click here": {"action": "click", "selector": "a,button"},
        
        # Dropdown challenges
        "select": {"action": "select", "selector": "select", "index": 1},
        "choose": {"action": "select", "selector": "select", "index": 1},
        "dropdown": {"action": "select", "selector": "select", "index": 1},
        
        # Checkbox/Radio challenges
        "check": {"action": "check", "selector": "input[type='checkbox']"},
        "agree": {"action": "check", "selector": "input[type='checkbox']"},
        "accept": {"action": "check", "selector": "input[type='checkbox']"},
        "radio": {"action": "check", "selector": "input[type='radio']"},
        
        # Special interactions
        "hover": {"action": "hover", "selector": "button,.hover-target,a"},
        "double click": {"action": "dblclick", "selector": "button,.dblclick-target"},
        "right click": {"action": "rightclick", "selector": "button,.context-target"},
        "drag": {"action": "drag", "selector": ".draggable", "target": ".droppable"},
        "slider": {"action": "slider", "selector": "input[type='range']", "value": "50"},
        "upload": {"action": "upload", "selector": "input[type='file']"},
    }
    
    def __init__(self, headless: bool = True, use_ai: bool = True):
        self.headless = headless
        self.use_ai = use_ai and bool(ANTHROPIC_API_KEY)
        self.metrics = RunMetrics(run_id=datetime.now().strftime("%Y%m%d_%H%M%S"))
        self.client = Anthropic(api_key=ANTHROPIC_API_KEY) if self.use_ai else None
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
    def log(self, msg: str, level: str = "INFO"):
        """Log a message with timestamp."""
        elapsed = self.metrics.elapsed_seconds
        print(f"[{elapsed:6.1f}s] [{level}] {msg}")
    
    def screenshot(self, page: Page, name: str) -> str:
        """Save screenshot and return path."""
        path = os.path.join(OUTPUT_DIR, f"{name}.png")
        page.screenshot(path=path, full_page=True)
        return path
    
    def get_page_context(self, page: Page) -> Dict[str, Any]:
        """Extract comprehensive page context for solving."""
        ctx = {
            "url": page.url,
            "title": "",
            "instructions": "",
            "visible_text": "",
            "elements": {
                "inputs": [],
                "buttons": [],
                "selects": [],
                "checkboxes": [],
                "radios": [],
                "textareas": [],
                "links": [],
                "sliders": [],
                "file_inputs": []
            }
        }
        
        try:
            # Get page title
            title_el = page.locator("h1, h2, h3, .title, .challenge-title").first
            if title_el.count() > 0:
                ctx["title"] = title_el.inner_text().strip()
            
            # Get instructions/description
            for selector in ["p", ".description", ".instructions", ".challenge-text", ".prompt"]:
                try:
                    el = page.locator(selector).first
                    if el.count() > 0 and el.is_visible():
                        text = el.inner_text().strip()
                        if text and len(text) > 5:
                            ctx["instructions"] = text
                            break
                except:
                    pass
            
            # Get visible text
            ctx["visible_text"] = page.inner_text("body")[:2000]
            
            # Extract interactive elements
            # Inputs
            for el in page.locator("input:visible:not([type='hidden']):not([type='submit']):not([type='checkbox']):not([type='radio']):not([type='file']):not([type='range'])").all():
                try:
                    ctx["elements"]["inputs"].append({
                        "type": el.get_attribute("type") or "text",
                        "id": el.get_attribute("id") or "",
                        "name": el.get_attribute("name") or "",
                        "placeholder": el.get_attribute("placeholder") or "",
                        "class": el.get_attribute("class") or ""
                    })
                except:
                    pass
            
            # Buttons
            for el in page.locator("button:visible, input[type='submit']:visible").all():
                try:
                    ctx["elements"]["buttons"].append({
                        "text": el.inner_text().strip() if el.evaluate("e => e.tagName") == "BUTTON" else el.get_attribute("value") or "",
                        "id": el.get_attribute("id") or "",
                        "class": el.get_attribute("class") or "",
                        "type": el.get_attribute("type") or ""
                    })
                except:
                    pass
            
            # Selects
            for el in page.locator("select:visible").all():
                try:
                    options = []
                    for opt in el.locator("option").all():
                        options.append({
                            "value": opt.get_attribute("value") or "",
                            "text": opt.inner_text().strip()
                        })
                    ctx["elements"]["selects"].append({
                        "id": el.get_attribute("id") or "",
                        "name": el.get_attribute("name") or "",
                        "options": options
                    })
                except:
                    pass
            
            # Checkboxes
            for el in page.locator("input[type='checkbox']:visible").all():
                try:
                    label = ""
                    el_id = el.get_attribute("id")
                    if el_id:
                        label_el = page.locator(f"label[for='{el_id}']")
                        if label_el.count() > 0:
                            label = label_el.inner_text().strip()
                    ctx["elements"]["checkboxes"].append({
                        "id": el_id or "",
                        "name": el.get_attribute("name") or "",
                        "label": label,
                        "checked": el.is_checked()
                    })
                except:
                    pass
            
            # Radio buttons
            for el in page.locator("input[type='radio']:visible").all():
                try:
                    ctx["elements"]["radios"].append({
                        "id": el.get_attribute("id") or "",
                        "name": el.get_attribute("name") or "",
                        "value": el.get_attribute("value") or "",
                        "checked": el.is_checked()
                    })
                except:
                    pass
            
            # Textareas
            for el in page.locator("textarea:visible").all():
                try:
                    ctx["elements"]["textareas"].append({
                        "id": el.get_attribute("id") or "",
                        "name": el.get_attribute("name") or "",
                        "placeholder": el.get_attribute("placeholder") or ""
                    })
                except:
                    pass
            
            # Sliders
            for el in page.locator("input[type='range']:visible").all():
                try:
                    ctx["elements"]["sliders"].append({
                        "id": el.get_attribute("id") or "",
                        "min": el.get_attribute("min") or "0",
                        "max": el.get_attribute("max") or "100",
                        "value": el.input_value() or "50"
                    })
                except:
                    pass
            
            # File inputs
            for el in page.locator("input[type='file']:visible").all():
                try:
                    ctx["elements"]["file_inputs"].append({
                        "id": el.get_attribute("id") or "",
                        "accept": el.get_attribute("accept") or ""
                    })
                except:
                    pass
            
            # Links
            for el in page.locator("a:visible").all()[:10]:  # Limit to first 10
                try:
                    ctx["elements"]["links"].append({
                        "text": el.inner_text().strip(),
                        "href": el.get_attribute("href") or ""
                    })
                except:
                    pass
                    
        except Exception as e:
            self.metrics.errors.append(f"Context extraction error: {str(e)}")
        
        return ctx
    
    def match_pattern(self, text: str) -> Optional[Dict]:
        """Match text against known challenge patterns."""
        text_lower = text.lower()
        for pattern, solution in self.CHALLENGE_PATTERNS.items():
            if pattern in text_lower:
                return solution.copy()
        return None
    
    def solve_with_heuristics(self, page: Page, ctx: Dict) -> bool:
        """Attempt to solve using pattern matching and heuristics."""
        instructions = ctx.get("instructions", "").lower()
        title = ctx.get("title", "").lower()
        combined_text = f"{title} {instructions}"
        
        actions_taken = False
        
        # Try pattern matching first
        pattern_match = self.match_pattern(combined_text)
        if pattern_match:
            try:
                action = pattern_match["action"]
                selector = pattern_match["selector"]
                
                if action == "fill":
                    value = pattern_match.get("value", "test")
                    el = page.locator(selector).first
                    if el.count() > 0 and el.is_visible():
                        el.fill(value)
                        actions_taken = True
                        
                elif action == "click":
                    el = page.locator(selector).first
                    if el.count() > 0 and el.is_visible():
                        el.click()
                        actions_taken = True
                        
                elif action == "select":
                    el = page.locator(selector).first
                    if el.count() > 0 and el.is_visible():
                        el.select_option(index=pattern_match.get("index", 1))
                        actions_taken = True
                        
                elif action == "check":
                    el = page.locator(selector).first
                    if el.count() > 0 and el.is_visible():
                        el.check()
                        actions_taken = True
                        
                elif action == "hover":
                    el = page.locator(selector).first
                    if el.count() > 0 and el.is_visible():
                        el.hover()
                        actions_taken = True
                        
                elif action == "dblclick":
                    el = page.locator(selector).first
                    if el.count() > 0 and el.is_visible():
                        el.dblclick()
                        actions_taken = True
                        
                elif action == "slider":
                    el = page.locator(selector).first
                    if el.count() > 0 and el.is_visible():
                        el.fill(pattern_match.get("value", "50"))
                        actions_taken = True
                        
            except Exception as e:
                self.metrics.errors.append(f"Pattern action error: {str(e)}")
        
        # Fill any visible inputs intelligently
        elements = ctx.get("elements", {})
        
        for inp in elements.get("inputs", []):
            if not actions_taken or "fill" not in str(pattern_match):
                try:
                    selector = f"#{inp['id']}" if inp['id'] else f"[name='{inp['name']}']" if inp['name'] else "input:visible"
                    el = page.locator(selector).first
                    if el.count() > 0 and el.is_visible() and not el.input_value():
                        inp_type = inp.get("type", "text").lower()
                        placeholder = inp.get("placeholder", "").lower()
                        
                        # Determine appropriate value
                        value = "test"
                        if inp_type == "email" or "email" in placeholder:
                            value = "test@example.com"
                        elif inp_type == "password" or "password" in placeholder:
                            value = "Password123!"
                        elif inp_type == "number" or "number" in placeholder:
                            value = "42"
                        elif inp_type == "tel" or "phone" in placeholder:
                            value = "555-123-4567"
                        elif "name" in placeholder:
                            value = "John Doe"
                        elif "url" in placeholder or inp_type == "url":
                            value = "https://example.com"
                        elif "date" in inp_type:
                            value = "2024-01-15"
                        
                        el.fill(value)
                        actions_taken = True
                except:
                    pass
        
        # Handle textareas
        for ta in elements.get("textareas", []):
            try:
                selector = f"#{ta['id']}" if ta['id'] else f"[name='{ta['name']}']" if ta['name'] else "textarea:visible"
                el = page.locator(selector).first
                if el.count() > 0 and el.is_visible() and not el.input_value():
                    el.fill("This is a test response for the challenge.")
                    actions_taken = True
            except:
                pass
        
        # Handle selects if not already handled
        for sel in elements.get("selects", []):
            try:
                selector = f"#{sel['id']}" if sel['id'] else f"[name='{sel['name']}']" if sel['name'] else "select:visible"
                el = page.locator(selector).first
                if el.count() > 0 and el.is_visible():
                    options = sel.get("options", [])
                    if len(options) > 1:
                        el.select_option(index=1)
                        actions_taken = True
            except:
                pass
        
        # Handle checkboxes
        for cb in elements.get("checkboxes", []):
            if not cb.get("checked"):
                try:
                    selector = f"#{cb['id']}" if cb['id'] else f"[name='{cb['name']}']" if cb['name'] else "input[type='checkbox']:visible"
                    el = page.locator(selector).first
                    if el.count() > 0 and el.is_visible():
                        el.check()
                        actions_taken = True
                except:
                    pass
        
        # Handle radios - select first option if none selected
        radio_groups = {}
        for rb in elements.get("radios", []):
            name = rb.get("name", "default")
            if name not in radio_groups:
                radio_groups[name] = []
            radio_groups[name].append(rb)
        
        for name, radios in radio_groups.items():
            if not any(r.get("checked") for r in radios):
                try:
                    first_radio = radios[0]
                    selector = f"#{first_radio['id']}" if first_radio['id'] else f"input[type='radio'][name='{name}']:visible"
                    el = page.locator(selector).first
                    if el.count() > 0 and el.is_visible():
                        el.check()
                        actions_taken = True
                except:
                    pass
        
        # Handle sliders
        for slider in elements.get("sliders", []):
            try:
                selector = f"#{slider['id']}" if slider['id'] else "input[type='range']:visible"
                el = page.locator(selector).first
                if el.count() > 0 and el.is_visible():
                    # Set to middle value or specific value if mentioned in instructions
                    min_val = int(slider.get("min", 0))
                    max_val = int(slider.get("max", 100))
                    target = (min_val + max_val) // 2
                    
                    # Look for specific number in instructions
                    nums = re.findall(r'\b(\d+)\b', combined_text)
                    for n in nums:
                        n_int = int(n)
                        if min_val <= n_int <= max_val:
                            target = n_int
                            break
                    
                    el.fill(str(target))
                    actions_taken = True
            except:
                pass
        
        # Finally, look for submit button and click it
        page.wait_for_timeout(200)
        
        submit_selectors = [
            "button[type='submit']",
            "input[type='submit']",
            "button:has-text('Submit')",
            "button:has-text('Next')",
            "button:has-text('Continue')",
            "button:has-text('Done')",
            "button:has-text('OK')",
            "#submit",
            ".submit-btn"
        ]
        
        for sel in submit_selectors:
            try:
                el = page.locator(sel).first
                if el.count() > 0 and el.is_visible():
                    el.click()
                    actions_taken = True
                    break
            except:
                pass
        
        # If no submit found, click any visible button
        if not actions_taken:
            for btn in elements.get("buttons", []):
                try:
                    selector = f"#{btn['id']}" if btn['id'] else f"button:has-text('{btn['text']}')" if btn['text'] else "button:visible"
                    el = page.locator(selector).first
                    if el.count() > 0 and el.is_visible():
                        el.click()
                        actions_taken = True
                        break
                except:
                    pass
        
        return actions_taken
    
    def solve_with_ai(self, page: Page, ctx: Dict) -> bool:
        """Use Claude Vision to solve complex challenges."""
        if not self.client:
            return False
        
        try:
            # Get screenshot
            screenshot_bytes = page.screenshot(full_page=True)
            screenshot_b64 = base64.standard_b64encode(screenshot_bytes).decode("utf-8")
            
            prompt = f"""Analyze this web challenge and provide the exact steps to solve it.

Page Context:
- Title: {ctx.get('title', 'Unknown')}
- Instructions: {ctx.get('instructions', 'None visible')}
- Available elements: {json.dumps(ctx.get('elements', {}), indent=2)}

Return a JSON object with actions to perform:
{{
  "reasoning": "brief explanation",
  "actions": [
    {{"type": "fill", "selector": "CSS selector", "value": "text to enter"}},
    {{"type": "click", "selector": "CSS selector"}},
    {{"type": "select", "selector": "CSS selector", "value": "option value"}},
    {{"type": "check", "selector": "CSS selector"}},
    {{"type": "hover", "selector": "CSS selector"}},
    {{"type": "dblclick", "selector": "CSS selector"}},
    {{"type": "press", "key": "Enter"}}
  ]
}}

Only return valid JSON."""

            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": screenshot_b64
                            }
                        },
                        {"type": "text", "text": prompt}
                    ]
                }]
            )
            
            # Track tokens
            self.metrics.api_calls += 1
            self.metrics.input_tokens += response.usage.input_tokens
            self.metrics.output_tokens += response.usage.output_tokens
            
            # Parse response
            response_text = response.content[0].text
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                data = json.loads(json_match.group())
                actions = data.get("actions", [])
                
                # Execute actions
                for action in actions:
                    try:
                        a_type = action.get("type")
                        selector = action.get("selector", "")
                        value = action.get("value", "")
                        
                        el = page.locator(selector).first
                        if el.count() == 0 or not el.is_visible():
                            continue
                        
                        if a_type == "fill":
                            el.fill(value)
                        elif a_type == "click":
                            el.click()
                        elif a_type == "select":
                            el.select_option(value)
                        elif a_type == "check":
                            el.check()
                        elif a_type == "hover":
                            el.hover()
                        elif a_type == "dblclick":
                            el.dblclick()
                        elif a_type == "press":
                            page.keyboard.press(action.get("key", "Enter"))
                        
                        page.wait_for_timeout(100)
                    except Exception as e:
                        self.metrics.errors.append(f"AI action error: {str(e)}")
                
                return len(actions) > 0
                
        except Exception as e:
            self.metrics.errors.append(f"AI solving error: {str(e)}")
        
        return False
    
    def is_challenge_complete(self, page: Page, prev_url: str) -> bool:
        """Check if the current challenge was completed."""
        try:
            # URL changed (moved to next challenge)
            if page.url != prev_url:
                return True
            
            # Success message visible
            success_selectors = [
                ".success", ".correct", ".complete", ".passed",
                "[data-status='success']", "[data-status='complete']",
                "text=Success", "text=Correct", "text=Well done",
                "text=Complete", "text=Passed"
            ]
            
            for sel in success_selectors:
                try:
                    el = page.locator(sel)
                    if el.count() > 0 and el.first.is_visible():
                        return True
                except:
                    pass
            
            return False
        except:
            return False
    
    def try_next_challenge(self, page: Page) -> bool:
        """Try to navigate to the next challenge."""
        next_selectors = [
            "button:has-text('Next')",
            "a:has-text('Next')",
            "button:has-text('Continue')",
            "a:has-text('Continue')",
            ".next", "#next", "[data-action='next']",
            "button:has-text('Start')",
            "a:has-text('Start')"
        ]
        
        for sel in next_selectors:
            try:
                el = page.locator(sel).first
                if el.count() > 0 and el.is_visible():
                    el.click()
                    page.wait_for_timeout(500)
                    return True
            except:
                pass
        
        return False
    
    def run(self) -> Dict:
        """Execute the challenge solver."""
        self.metrics.start_time = time.time()
        
        print("\n" + "=" * 60)
        print("QA Bench Challenge Solver")
        print(f"URL: {CHALLENGE_URL}")
        print(f"AI Enabled: {self.use_ai}")
        print(f"Max Time: {MAX_TIME_SECONDS}s")
        print("=" * 60 + "\n")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            page = context.new_page()
            
            try:
                # Navigate to site
                self.log(f"Navigating to {CHALLENGE_URL}")
                page.goto(CHALLENGE_URL, timeout=30000)
                page.wait_for_load_state('networkidle')
                self.screenshot(page, "00_start")
                
                # Try to start challenges if there's a start button
                self.try_next_challenge(page)
                page.wait_for_timeout(500)
                
                # Main solving loop
                for challenge_num in range(1, self.metrics.total_challenges + 1):
                    # Time check
                    if self.metrics.elapsed_seconds > MAX_TIME_SECONDS:
                        self.log("TIME LIMIT REACHED", "WARN")
                        break
                    
                    self.log(f"Challenge {challenge_num}/{self.metrics.total_challenges}")
                    self.metrics.challenges_attempted += 1
                    
                    challenge_start = time.time()
                    prev_url = page.url
                    
                    # Get page context
                    ctx = self.get_page_context(page)
                    self.log(f"  Title: {ctx.get('title', 'Unknown')[:40]}")
                    self.log(f"  Elements: {sum(len(v) for v in ctx['elements'].values())} found")
                    
                    # Screenshot before
                    self.screenshot(page, f"{challenge_num:02d}_before")
                    
                    # Try heuristic solution
                    solved = self.solve_with_heuristics(page, ctx)
                    page.wait_for_timeout(300)
                    
                    # Check if solved
                    if not self.is_challenge_complete(page, prev_url) and self.use_ai:
                        self.log("  Trying AI...", "INFO")
                        solved = self.solve_with_ai(page, ctx)
                        page.wait_for_timeout(300)
                    
                    # Screenshot after
                    self.screenshot(page, f"{challenge_num:02d}_after")
                    
                    # Record metrics
                    challenge_time = time.time() - challenge_start
                    is_complete = self.is_challenge_complete(page, prev_url)
                    
                    self.metrics.per_challenge_metrics[challenge_num] = {
                        "time_seconds": round(challenge_time, 2),
                        "solved": is_complete,
                        "used_ai": self.metrics.api_calls > 0
                    }
                    
                    if is_complete:
                        self.metrics.challenges_solved += 1
                        self.log(f"  ✓ SOLVED in {challenge_time:.2f}s", "SUCCESS")
                    else:
                        self.metrics.challenges_failed += 1
                        self.log(f"  ✗ FAILED after {challenge_time:.2f}s", "ERROR")
                    
                    # Try to move to next challenge
                    self.try_next_challenge(page)
                    page.wait_for_timeout(300)
                
            except Exception as e:
                self.metrics.errors.append(f"Fatal error: {str(e)}")
                self.log(f"Fatal error: {e}", "ERROR")
                
            finally:
                self.screenshot(page, "99_final")
                browser.close()
        
        self.metrics.end_time = time.time()
        
        # Generate report
        report = self.metrics.to_report()
        
        # Print summary
        print("\n" + "=" * 60)
        print("RESULTS SUMMARY")
        print("=" * 60)
        print(f"Time: {report['duration_formatted']} (under 5 min: {report['under_5_minutes']})")
        print(f"Challenges: {report['challenges']['solved']}/{report['challenges']['total']} solved ({report['challenges']['success_rate']})")
        print(f"Tokens: {report['tokens']['total']} ({report['tokens']['api_calls']} API calls)")
        print(f"Cost: {report['cost']['estimated_usd']}")
        print("=" * 60 + "\n")
        
        # Save report
        report_path = os.path.join(OUTPUT_DIR, "results.json")
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"Results saved to: {report_path}")
        
        return report


def main():
    global CHALLENGE_URL, OUTPUT_DIR
    
    import argparse
    
    parser = argparse.ArgumentParser(description="QA Bench Challenge Solver")
    parser.add_argument("--url", default=None, help="Challenge website URL")
    parser.add_argument("--headless", action="store_true", default=True, help="Run headless")
    parser.add_argument("--visible", action="store_true", help="Run with visible browser")
    parser.add_argument("--no-ai", action="store_true", help="Disable AI assistance")
    parser.add_argument("--output", default=None, help="Output directory")
    args = parser.parse_args()
    
    if args.url:
        CHALLENGE_URL = args.url
    if args.output:
        OUTPUT_DIR = args.output
    
    solver = QABenchSolver(
        headless=not args.visible,
        use_ai=not args.no_ai
    )
    
    report = solver.run()
    
    # Exit code based on success
    if report["challenges"]["solved"] >= report["challenges"]["total"]:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
