#!/usr/bin/env python3
"""
Optimized Browser Navigation Challenge Solver
Uses Claude Vision with better element targeting.
"""

import os
import sys
import time
import json
import base64
import re
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from playwright.sync_api import sync_playwright, Page

CHALLENGE_URL = "https://serene-frangipane-7fd25b.netlify.app/"
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
MAX_TIME_SECONDS = 300
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "/tmp/optimized_results")


@dataclass
class Metrics:
    start_time: float = 0
    end_time: float = 0
    steps_completed: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    api_calls: int = 0
    details: List[Dict] = field(default_factory=list)
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
            "challenges": {
                "total": 30,
                "solved": self.steps_completed,
                "success_rate": f"{(self.steps_completed / 30) * 100:.1f}%"
            },
            "tokens": {
                "input": self.input_tokens,
                "output": self.output_tokens,
                "total": self.input_tokens + self.output_tokens,
                "api_calls": self.api_calls
            },
            "cost_usd": f"${self.cost:.4f}",
            "details": self.details,
            "errors": self.errors[:20]
        }


class OptimizedSolver:
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
    
    def close_cookie(self, page: Page):
        """Close cookie consent."""
        try:
            page.locator("text=Accept").first.click(timeout=1000)
        except:
            pass
    
    def get_page_elements(self, page: Page) -> str:
        """Get list of clickable elements."""
        elements = []
        
        try:
            # Get all buttons
            buttons = page.locator("button:visible").all()
            for i, btn in enumerate(buttons[:20]):
                try:
                    text = btn.inner_text(timeout=200).strip()[:50]
                    if text:
                        elements.append(f"Button {i}: '{text}'")
                except:
                    pass
            
            # Get all links
            links = page.locator("a:visible").all()
            for i, link in enumerate(links[:20]):
                try:
                    text = link.inner_text(timeout=200).strip()[:50]
                    if text:
                        elements.append(f"Link {i}: '{text}'")
                except:
                    pass
            
            # Get dialog/modal content
            for sel in [".modal", "[role='dialog']", ".popup", ".dialog"]:
                try:
                    dialog = page.locator(sel).first
                    if dialog.count() > 0 and dialog.is_visible():
                        content = dialog.inner_text(timeout=500)[:500]
                        elements.append(f"DIALOG CONTENT: {content}")
                except:
                    pass
            
        except:
            pass
        
        return "\n".join(elements)
    
    def ask_claude(self, screenshot: bytes, step: int, elements: str, prev_actions: List[str]) -> Dict:
        """Ask Claude for the action to take."""
        b64 = base64.standard_b64encode(screenshot).decode("utf-8")
        
        prev_str = ", ".join(prev_actions[-5:]) if prev_actions else "None"
        
        prompt = f"""You are solving step {step} of a 30-step Browser Navigation Challenge.

AVAILABLE ELEMENTS ON PAGE:
{elements}

PREVIOUS ACTIONS (avoid repeating): {prev_str}

CRITICAL INSTRUCTIONS:
1. DO NOT click Close, Dismiss, Cancel, or X buttons - these will NOT advance the challenge
2. Look for the MAIN CHALLENGE INSTRUCTION on the page
3. Find and click the CORRECT OPTION that completes the challenge
4. The challenge often requires clicking on specific Section buttons, navigation links, or option selections

If you see a dialog, look for options like:
- "Select 1 - Click here for navigation lovers"
- "Section 1 - Subscription"
- "Visit the site" links
- Numbered section buttons
- Navigation elements

Return ONLY valid JSON:
{{"action": "click", "target": "exact text of the element to click"}}

DO NOT close dialogs. SELECT the correct option to advance.

Return ONLY the JSON object."""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=200,
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
        target = action_data.get("target", "")
        
        if not action:
            return False
        
        try:
            if action == "scroll":
                page.evaluate("window.scrollBy(0, 400)")
                return True
            
            if action == "click" and target:
                # Try multiple selector strategies
                selectors = [
                    f"text={target}",
                    f"text='{target}'",
                    f'text="{target}"',
                    f"button:has-text('{target}')",
                    f"a:has-text('{target}')",
                    f"*:has-text('{target}')"
                ]
                
                for sel in selectors:
                    try:
                        el = page.locator(sel).first
                        if el.count() > 0 and el.is_visible():
                            el.click(timeout=2000)
                            return True
                    except:
                        continue
                
                # Try partial match
                try:
                    # Find element containing the text
                    page.click(f"text=/{re.escape(target[:20])}/i", timeout=2000)
                    return True
                except:
                    pass
            
            return False
        except Exception as e:
            self.metrics.errors.append(f"Execute error: {str(e)}")
            return False
    
    def run(self) -> Dict:
        self.metrics.start_time = time.time()
        
        print("\n" + "=" * 60)
        print("Optimized Browser Navigation Solver")
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
                
                # Close cookie
                self.close_cookie(page)
                
                last_step = 0
                prev_actions = []
                stuck = 0
                
                while self.metrics.elapsed < MAX_TIME_SECONDS:
                    current_step = self.get_step(page)
                    
                    if current_step > last_step:
                        self.metrics.steps_completed = current_step
                        self.log(f"ADVANCED TO STEP {current_step}!", "OK")
                        last_step = current_step
                        stuck = 0
                        prev_actions = []
                        
                        if current_step >= 30:
                            self.log("ALL STEPS COMPLETED!", "OK")
                            break
                    else:
                        stuck += 1
                    
                    if stuck > 15:
                        self.log(f"Stuck on step {current_step} too long", "WARN")
                        stuck = 0
                        prev_actions = []
                        page.evaluate("window.scrollTo(0, 0)")
                    
                    self.log(f"Step {current_step or 1}/30 (attempt {stuck})")
                    
                    # Screenshot
                    screenshot = self.screenshot(page, f"{current_step:02d}_{stuck}")
                    
                    # Get elements
                    elements = self.get_page_elements(page)
                    
                    # Ask Claude
                    action_data = self.ask_claude(screenshot, current_step or 1, elements, prev_actions)
                    
                    if action_data:
                        target = action_data.get("target", "")
                        action = action_data.get("action", "")
                        self.log(f"  Action: {action} -> '{target[:40]}'")
                        
                        success = self.execute_action(page, action_data)
                        
                        if success:
                            self.log("  Executed", "OK")
                            prev_actions.append(f"{action}:{target[:20]}")
                        else:
                            self.log("  Failed", "FAIL")
                        
                        self.metrics.details.append({
                            "step": current_step,
                            "action": action,
                            "target": target,
                            "success": success
                        })
                    
                    page.wait_for_timeout(500)
                    
                    # Check for step change
                    new_step = self.get_step(page)
                    if new_step > current_step:
                        self.metrics.steps_completed = new_step
                        self.log(f"Step advanced to {new_step}!", "OK")
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
    
    solver = OptimizedSolver(headless=not args.visible)
    report = solver.run()
    sys.exit(0 if report["challenges"]["solved"] >= 25 else 1)


if __name__ == "__main__":
    main()
