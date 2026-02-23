#!/usr/bin/env python3
"""
Smart AI Browser Navigation Challenge Solver
Handles specific challenge patterns like hidden DOM, fake buttons, etc.
"""

import os
import sys
import time
import json
import base64
import re
from datetime import datetime
from typing import Dict, List
from dataclasses import dataclass, field
from playwright.sync_api import sync_playwright, Page

CHALLENGE_URL = "https://serene-frangipane-7fd25b.netlify.app/"
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
MAX_TIME_SECONDS = 300
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "/tmp/smart_ai_results")


@dataclass
class Metrics:
    start_time: float = 0
    end_time: float = 0
    steps_completed: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    api_calls: int = 0
    errors: List[str] = field(default_factory=list)
    
    @property
    def elapsed(self) -> float:
        return (self.end_time if self.end_time else time.time()) - self.start_time
    
    @property
    def cost(self) -> float:
        return (self.input_tokens / 1e6 * 3) + (self.output_tokens / 1e6 * 15)
    
    def report(self) -> dict:
        return {
            "timestamp": datetime.now().isoformat(),
            "duration_seconds": round(self.elapsed, 2),
            "duration_formatted": f"{int(self.elapsed // 60)}m {int(self.elapsed % 60)}s",
            "under_5_minutes": self.elapsed < 300,
            "challenges": {"total": 30, "solved": self.steps_completed, 
                          "success_rate": f"{(self.steps_completed / 30) * 100:.1f}%"},
            "tokens": {"input": self.input_tokens, "output": self.output_tokens,
                      "total": self.input_tokens + self.output_tokens, "api_calls": self.api_calls},
            "cost_usd": f"${self.cost:.4f}",
            "errors": self.errors[:20]
        }


class SmartAISolver:
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.metrics = Metrics()
        
        if not ANTHROPIC_API_KEY:
            print("ERROR: ANTHROPIC_API_KEY required")
            sys.exit(1)
        
        from anthropic import Anthropic
        self.client = Anthropic(api_key=ANTHROPIC_API_KEY)
        os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    def log(self, msg: str, level: str = "INFO"):
        elapsed = self.metrics.elapsed
        sym = {"INFO": "  ", "OK": "✓ ", "FAIL": "✗ ", "WARN": "! "}
        print(f"[{elapsed:5.1f}s] {sym.get(level, '  ')}{msg}")
    
    def screenshot(self, page: Page, name: str) -> bytes:
        path = os.path.join(OUTPUT_DIR, f"{name}.png")
        data = page.screenshot(timeout=5000)
        with open(path, 'wb') as f:
            f.write(data)
        return data
    
    def get_step(self, page: Page) -> int:
        try:
            text = page.inner_text("body", timeout=1000)
            match = re.search(r'Step\s*(\d+)\s*(?:of|/)\s*30', text, re.IGNORECASE)
            if match:
                return int(match.group(1))
        except:
            pass
        return 0
    
    def ask_claude(self, screenshot: bytes, step: int, page_text: str, prev_actions: List[str]) -> Dict:
        """Ask Claude for precise action."""
        b64 = base64.standard_b64encode(screenshot).decode("utf-8")
        prev_str = ", ".join(prev_actions[-3:]) if prev_actions else "None"
        
        prompt = f"""Analyze this browser challenge screenshot carefully.

CURRENT STEP: {step} of 30
PREVIOUS ACTIONS (do not repeat): {prev_str}

PAGE TEXT EXCERPT:
{page_text[:1500]}

CHALLENGE TYPES YOU MAY SEE:
1. Hidden DOM Challenge - Click on a specific area multiple times
2. Fake close button popup - Find the REAL way to close (not the X or Dismiss)
3. Click specific section/button
4. Form filling
5. Navigation challenges

INSTRUCTIONS:
- Look at the main challenge instruction
- Identify what SPECIFIC action is needed
- If a popup says "close button is fake", look for alternative close methods (maybe click outside, or find hidden button)
- If it says "click here X times", click on that element
- Ignore cookie consent - focus on the actual challenge

Return ONLY a JSON object:
{{"action": "click|fill|scroll|dblclick|clickOutside", "selector": "CSS selector or text", "value": "value if fill", "clicks": 1}}

For clicking multiple times: {{"action": "click", "selector": "text=Code hidden", "clicks": 3}}
For clicking outside popup: {{"action": "clickOutside", "selector": "body"}}

Be VERY specific with selectors. Return ONLY valid JSON."""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=300,
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": b64}},
                        {"type": "text", "text": prompt}
                    ]
                }]
            )
            
            self.metrics.api_calls += 1
            self.metrics.input_tokens += response.usage.input_tokens
            self.metrics.output_tokens += response.usage.output_tokens
            
            text = response.content[0].text
            match = re.search(r'\{[^}]+\}', text)
            if match:
                return json.loads(match.group())
        except Exception as e:
            self.metrics.errors.append(str(e))
        
        return {}
    
    def execute_action(self, page: Page, action_data: Dict) -> bool:
        """Execute the action."""
        action = action_data.get("action", "")
        selector = action_data.get("selector", "")
        value = action_data.get("value", "")
        clicks = action_data.get("clicks", 1)
        
        if not action:
            return False
        
        try:
            if action == "scroll":
                page.evaluate("window.scrollBy(0, 400)")
                return True
            
            if action == "clickOutside":
                # Click outside any modal
                page.mouse.click(10, 10)
                return True
            
            if action == "fill":
                el = page.locator(selector).first
                if el.count() > 0:
                    el.fill(value, timeout=2000)
                    return True
            
            if action == "dblclick":
                el = page.locator(selector).first
                if el.count() > 0:
                    el.dblclick(timeout=2000)
                    return True
            
            if action == "click":
                # Try multiple selector strategies
                selectors_to_try = [selector]
                
                if selector.startswith("text="):
                    text = selector[5:]
                    selectors_to_try.extend([
                        f'text="{text}"',
                        f"text='{text}'",
                        f"*:has-text('{text}')",
                        f"button:has-text('{text}')",
                        f"a:has-text('{text}')"
                    ])
                
                for sel in selectors_to_try:
                    try:
                        el = page.locator(sel).first
                        if el.count() > 0 and el.is_visible():
                            for _ in range(clicks):
                                el.click(timeout=2000)
                                page.wait_for_timeout(200)
                            return True
                    except:
                        continue
                
                return False
            
            return False
        except Exception as e:
            self.metrics.errors.append(f"Execute: {str(e)}")
            return False
    
    def handle_cookie_consent(self, page: Page):
        """Handle cookie consent popup."""
        try:
            accept = page.locator("text=Accept").first
            if accept.count() > 0 and accept.is_visible():
                accept.click(timeout=1000)
                self.log("Accepted cookies", "OK")
        except:
            pass
    
    def run(self) -> Dict:
        self.metrics.start_time = time.time()
        
        print("\n" + "=" * 60)
        print("Smart AI Browser Navigation Solver")
        print(f"URL: {CHALLENGE_URL}")
        print("=" * 60 + "\n")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless, args=['--no-sandbox'])
            context = browser.new_context(viewport={'width': 1280, 'height': 900})
            page = context.new_page()
            page.on("dialog", lambda d: d.accept())
            
            try:
                self.log("Loading page...")
                page.goto(CHALLENGE_URL, timeout=30000)
                page.wait_for_load_state('networkidle', timeout=10000)
                
                # Click START
                try:
                    page.locator("text=START").first.click(timeout=3000)
                    self.log("Started", "OK")
                    page.wait_for_timeout(1000)
                except:
                    pass
                
                # Handle cookies
                self.handle_cookie_consent(page)
                
                last_step = 0
                prev_actions = []
                stuck = 0
                
                while self.metrics.elapsed < MAX_TIME_SECONDS:
                    current_step = self.get_step(page)
                    
                    if current_step > last_step:
                        self.metrics.steps_completed = current_step
                        self.log(f"STEP {current_step} REACHED!", "OK")
                        last_step = current_step
                        stuck = 0
                        prev_actions = []
                        
                        if current_step >= 30:
                            self.log("ALL 30 STEPS COMPLETED!", "OK")
                            break
                    else:
                        stuck += 1
                    
                    if stuck > 12:
                        self.log(f"Stuck, resetting...", "WARN")
                        stuck = 0
                        prev_actions = []
                        page.evaluate("window.scrollTo(0, 0)")
                    
                    self.log(f"Step {current_step or 1}/30 (try {stuck})")
                    
                    # Screenshot
                    screenshot = self.screenshot(page, f"{current_step:02d}_{stuck}")
                    
                    # Get page text
                    try:
                        page_text = page.inner_text("body", timeout=1000)
                    except:
                        page_text = ""
                    
                    # Ask Claude
                    action_data = self.ask_claude(screenshot, current_step or 1, page_text, prev_actions)
                    
                    if action_data:
                        action = action_data.get("action", "")
                        selector = action_data.get("selector", "")
                        clicks = action_data.get("clicks", 1)
                        
                        self.log(f"  {action} -> '{selector[:35]}' (x{clicks})")
                        
                        success = self.execute_action(page, action_data)
                        
                        if success:
                            self.log("  Done", "OK")
                            prev_actions.append(f"{action}:{selector[:20]}")
                        else:
                            self.log("  Failed", "FAIL")
                    else:
                        self.log("  No action from Claude", "WARN")
                    
                    page.wait_for_timeout(500)
                    
                    # Check step change
                    new_step = self.get_step(page)
                    if new_step > current_step:
                        self.metrics.steps_completed = new_step
                        self.log(f"Advanced to step {new_step}!", "OK")
                        last_step = new_step
                        stuck = 0
                        prev_actions = []
                
            except Exception as e:
                self.metrics.errors.append(str(e))
                self.log(f"Error: {e}", "FAIL")
            
            finally:
                self.screenshot(page, "99_final")
                browser.close()
        
        self.metrics.end_time = time.time()
        report = self.metrics.report()
        
        print("\n" + "=" * 60)
        print("RESULTS")
        print("=" * 60)
        print(f"Time: {report['duration_formatted']}")
        print(f"Under 5 min: {report['under_5_minutes']}")
        print(f"Solved: {report['challenges']['solved']}/30")
        print(f"Success Rate: {report['challenges']['success_rate']}")
        print(f"API Calls: {report['tokens']['api_calls']}")
        print(f"Tokens: {report['tokens']['total']}")
        print(f"Cost: {report['cost_usd']}")
        print("=" * 60)
        
        with open(os.path.join(OUTPUT_DIR, "results.json"), 'w') as f:
            json.dump(report, f, indent=2)
        
        return report


def main():
    global OUTPUT_DIR
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", help="Output dir")
    parser.add_argument("--visible", action="store_true")
    args = parser.parse_args()
    
    if args.output:
        OUTPUT_DIR = args.output
    
    solver = SmartAISolver(headless=not args.visible)
    report = solver.run()
    sys.exit(0 if report["challenges"]["solved"] >= 25 else 1)


if __name__ == "__main__":
    main()
