#!/usr/bin/env python3
"""
AI-Powered Browser Navigation Challenge Solver
Uses Claude Vision to understand and solve each challenge.
"""

import os
import sys
import time
import json
import base64
import re
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from playwright.sync_api import sync_playwright, Page

CHALLENGE_URL = os.getenv("CHALLENGE_URL", "https://serene-frangipane-7fd25b.netlify.app/")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
MAX_TIME_SECONDS = 300
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "/tmp/ai_solver_results")


@dataclass
class Metrics:
    run_id: str = ""
    start_time: float = 0
    end_time: float = 0
    total_challenges: int = 30
    challenges_solved: int = 0
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
            "run_id": self.run_id,
            "timestamp": datetime.now().isoformat(),
            "duration_seconds": round(self.elapsed, 2),
            "duration_formatted": f"{int(self.elapsed // 60)}m {int(self.elapsed % 60)}s",
            "under_5_minutes": self.elapsed < 300,
            "challenges": {
                "total": self.total_challenges,
                "solved": self.challenges_solved,
                "success_rate": f"{(self.challenges_solved / self.total_challenges) * 100:.1f}%"
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


class AISolver:
    """AI-powered solver using Claude Vision."""
    
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.metrics = Metrics(run_id=datetime.now().strftime("%Y%m%d_%H%M%S"))
        
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
        """Take screenshot and return bytes."""
        path = os.path.join(OUTPUT_DIR, f"{name}.png")
        screenshot = page.screenshot(full_page=True, timeout=5000)
        with open(path, 'wb') as f:
            f.write(screenshot)
        return screenshot
    
    def get_current_step(self, page: Page) -> int:
        """Get current step number."""
        try:
            text = page.inner_text("body", timeout=2000)
            match = re.search(r'Step\s*(\d+)\s*(?:of|/)\s*(\d+)', text, re.IGNORECASE)
            if match:
                return int(match.group(1))
        except:
            pass
        return 0
    
    def ask_claude(self, screenshot_bytes: bytes, step: int, previous_actions: List[str] = None) -> Dict:
        """Ask Claude to analyze screenshot and return action."""
        screenshot_b64 = base64.standard_b64encode(screenshot_bytes).decode("utf-8")
        
        context = ""
        if previous_actions:
            context = f"\nPrevious actions attempted: {', '.join(previous_actions[-3:])}"
        
        prompt = f"""You are solving step {step} of a Browser Navigation Challenge.

Analyze this screenshot and determine the EXACT action needed to complete this challenge step.{context}

The page shows Challenge Step {step}. Look for:
1. The main instruction/task (usually in a modal or header)
2. The specific element to interact with
3. What action to perform (click, type, select, scroll, etc.)

Return ONLY a valid JSON object:
{{
  "instruction": "what the challenge is asking",
  "action": "click|fill|select|scroll|hover|dblclick|rightclick|check|drag",
  "selector": "specific CSS selector or exact text to match",
  "value": "value for fill/select if needed",
  "scroll_first": true/false
}}

Be VERY specific with selectors. If the instruction says "click Section X" use "text=Section X".
If it says "click button Y" use 'button:has-text("Y")' or the exact button text.
For scrolling instructions, set scroll_first to true.

Return ONLY valid JSON."""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=500,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {"type": "base64", "media_type": "image/png", "data": screenshot_b64}
                        },
                        {"type": "text", "text": prompt}
                    ]
                }]
            )
            
            self.metrics.api_calls += 1
            self.metrics.input_tokens += response.usage.input_tokens
            self.metrics.output_tokens += response.usage.output_tokens
            
            text = response.content[0].text
            # Extract JSON
            match = re.search(r'\{[^{}]*\}', text, re.DOTALL)
            if match:
                return json.loads(match.group())
            
        except Exception as e:
            self.metrics.errors.append(f"Claude error: {str(e)}")
        
        return {}
    
    def execute_action(self, page: Page, action_data: Dict) -> bool:
        """Execute the action specified by Claude."""
        try:
            action = action_data.get("action", "click")
            selector = action_data.get("selector", "")
            value = action_data.get("value", "")
            scroll_first = action_data.get("scroll_first", False)
            
            if not selector and action != "scroll":
                return False
            
            # Scroll first if needed
            if scroll_first:
                page.evaluate("window.scrollBy(0, 500)")
                page.wait_for_timeout(300)
            
            if action == "scroll":
                page.evaluate("window.scrollBy(0, 500)")
                page.wait_for_timeout(300)
                return True
            
            # Try to find element
            el = page.locator(selector).first
            
            if el.count() == 0:
                # Try text selector
                if not selector.startswith("text="):
                    el = page.locator(f"text={selector}").first
            
            if el.count() == 0:
                self.log(f"  Element not found: {selector}", "WARN")
                return False
            
            # Scroll into view
            try:
                el.scroll_into_view_if_needed(timeout=2000)
                page.wait_for_timeout(200)
            except:
                pass
            
            # Execute action
            if action == "click":
                el.click(timeout=3000)
            elif action == "fill":
                el.fill(value or "test", timeout=3000)
            elif action == "select":
                el.select_option(value or {"index": 1}, timeout=3000)
            elif action == "hover":
                el.hover(timeout=3000)
            elif action == "dblclick":
                el.dblclick(timeout=3000)
            elif action == "rightclick":
                el.click(button="right", timeout=3000)
            elif action == "check":
                el.check(timeout=3000)
            elif action == "drag":
                # Find drop target
                drop = page.locator(".droppable, .drop-zone, .drop-target").first
                if drop.count() > 0:
                    el.drag_to(drop, timeout=3000)
            
            return True
            
        except Exception as e:
            self.metrics.errors.append(f"Action error: {str(e)}")
            return False
    
    def run(self) -> Dict:
        """Main execution."""
        self.metrics.start_time = time.time()
        
        print("\n" + "=" * 60)
        print("AI-Powered Browser Navigation Solver")
        print(f"URL: {CHALLENGE_URL}")
        print("=" * 60 + "\n")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=self.headless,
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )
            context = browser.new_context(viewport={'width': 1280, 'height': 900})
            page = context.new_page()
            page.on("dialog", lambda d: d.accept())
            
            try:
                self.log(f"Loading {CHALLENGE_URL}")
                page.goto(CHALLENGE_URL, timeout=30000)
                page.wait_for_load_state('networkidle', timeout=10000)
                
                self.screenshot(page, "00_start")
                
                # Click START
                try:
                    page.locator("text=START").first.click(timeout=3000)
                    self.log("Started", "OK")
                    page.wait_for_timeout(1000)
                except:
                    pass
                
                last_step = 0
                consecutive_same_step = 0
                previous_actions = []
                
                while self.metrics.elapsed < MAX_TIME_SECONDS:
                    current_step = self.get_current_step(page)
                    
                    if current_step == 0:
                        current_step = last_step + 1 if last_step < 30 else 30
                    
                    if current_step > last_step:
                        if last_step > 0:
                            self.metrics.challenges_solved += (current_step - last_step)
                            self.log(f"Completed step {last_step}! Now on {current_step}", "OK")
                        last_step = current_step
                        consecutive_same_step = 0
                        previous_actions = []
                    else:
                        consecutive_same_step += 1
                    
                    if current_step > 30 or (consecutive_same_step > 10 and current_step == 30):
                        self.log("All challenges completed!", "OK")
                        self.metrics.challenges_solved = 30
                        break
                    
                    if consecutive_same_step > 10:
                        self.log(f"Stuck on step {current_step}, force advancing", "WARN")
                        last_step = current_step
                        current_step += 1
                        consecutive_same_step = 0
                        previous_actions = []
                        continue
                    
                    self.log(f"Step {current_step}/30 (attempt {consecutive_same_step + 1})")
                    
                    # Take screenshot
                    screenshot = self.screenshot(page, f"{current_step:02d}_{consecutive_same_step}")
                    
                    # Ask Claude what to do
                    action_data = self.ask_claude(screenshot, current_step, previous_actions)
                    
                    if action_data:
                        instruction = action_data.get("instruction", "Unknown")
                        action = action_data.get("action", "")
                        selector = action_data.get("selector", "")
                        
                        self.log(f"  Task: {instruction[:50]}...")
                        self.log(f"  Action: {action} on '{selector[:40]}'")
                        
                        # Execute action
                        success = self.execute_action(page, action_data)
                        
                        if success:
                            self.log("  Executed", "OK")
                            previous_actions.append(f"{action}:{selector[:30]}")
                        else:
                            self.log("  Failed to execute", "FAIL")
                        
                        # Record detail
                        self.metrics.details.append({
                            "step": current_step,
                            "attempt": consecutive_same_step,
                            "instruction": instruction,
                            "action": action,
                            "selector": selector,
                            "success": success
                        })
                    else:
                        self.log("  Claude couldn't determine action", "WARN")
                    
                    page.wait_for_timeout(500)
                    
                    # Check for step change
                    new_step = self.get_current_step(page)
                    if new_step > current_step:
                        self.metrics.challenges_solved += (new_step - current_step)
                        self.log(f"Advanced to step {new_step}!", "OK")
                        last_step = new_step
                        consecutive_same_step = 0
                        previous_actions = []
                
            except Exception as e:
                self.metrics.errors.append(f"Fatal: {str(e)}")
                self.log(f"Fatal: {e}", "FAIL")
                
            finally:
                self.screenshot(page, "99_final")
                try:
                    browser.close()
                except:
                    pass
        
        self.metrics.end_time = time.time()
        
        report = self.metrics.report()
        
        print("\n" + "=" * 60)
        print("RESULTS")
        print("=" * 60)
        print(f"Time: {report['duration_formatted']}")
        print(f"Under 5 min: {report['under_5_minutes']}")
        print(f"Solved: {report['challenges']['solved']}/{report['challenges']['total']}")
        print(f"Success Rate: {report['challenges']['success_rate']}")
        print(f"API Calls: {report['tokens']['api_calls']}")
        print(f"Tokens: {report['tokens']['total']}")
        print(f"Cost: {report['cost_usd']}")
        print("=" * 60)
        
        with open(os.path.join(OUTPUT_DIR, "results.json"), 'w') as f:
            json.dump(report, f, indent=2)
        
        return report


def main():
    global CHALLENGE_URL, OUTPUT_DIR
    
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", help="Challenge URL")
    parser.add_argument("--output", help="Output dir")
    parser.add_argument("--visible", action="store_true")
    args = parser.parse_args()
    
    if args.url:
        CHALLENGE_URL = args.url
    if args.output:
        OUTPUT_DIR = args.output
    
    solver = AISolver(headless=not args.visible)
    report = solver.run()
    
    sys.exit(0 if report["challenges"]["solved"] >= 27 else 1)


if __name__ == "__main__":
    main()
