#!/usr/bin/env python3
"""
Fast Browser Navigation Challenge Solver
Optimized for speed - target: 30 challenges in under 5 minutes.
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
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "/tmp/fast_solver_results")


@dataclass
class Metrics:
    start_time: float = 0
    end_time: float = 0
    steps_completed: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    api_calls: int = 0
    errors: List[str] = field(default_factory=list)
    step_times: List[float] = field(default_factory=list)
    
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
            "avg_time_per_step": round(sum(self.step_times) / max(1, len(self.step_times)), 2),
            "errors": self.errors[:10]
        }


class FastSolver:
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
        data = page.screenshot(timeout=3000)
        with open(path, 'wb') as f:
            f.write(data)
        return data
    
    def get_step(self, page: Page) -> int:
        try:
            # Fast regex on page content
            html = page.content()
            match = re.search(r'Step\s*(\d+)\s*(?:of|/)\s*30', html, re.IGNORECASE)
            if match:
                return int(match.group(1))
        except:
            pass
        return 0
    
    def close_real_popups(self, page: Page) -> int:
        """Close popups that have REAL close buttons (say 'Click X to close')."""
        closed = 0
        try:
            # Find popups that say "Click X to close" - these have real X buttons
            popups = page.locator("text=Click X to close").all()
            for popup in popups:
                try:
                    # Find the X button near this popup
                    parent = popup.locator("xpath=ancestor::div[contains(@class,'popup') or contains(@class,'modal') or contains(@class,'dialog')]").first
                    if parent.count() > 0:
                        x_btn = parent.locator("button:has-text('×'), button:has-text('X'), .close, [aria-label='Close']").first
                        if x_btn.count() > 0 and x_btn.is_visible():
                            x_btn.click(timeout=500)
                            closed += 1
                            page.wait_for_timeout(100)
                except:
                    pass
            
            # Also try clicking visible X buttons that are red (likely real)
            x_buttons = page.locator("button:visible").all()
            for btn in x_buttons:
                try:
                    text = btn.inner_text(timeout=100)
                    if text.strip() in ['×', 'X', '✕']:
                        btn.click(timeout=300)
                        closed += 1
                        page.wait_for_timeout(100)
                except:
                    pass
                    
        except:
            pass
        return closed
    
    def scroll_modal(self, page: Page) -> bool:
        """Scroll inside any visible modal."""
        try:
            modals = page.locator(".modal, [role='dialog'], .popup, .dialog").all()
            for modal in modals:
                try:
                    if modal.is_visible():
                        modal.evaluate("el => el.scrollTop += 200")
                        return True
                except:
                    pass
        except:
            pass
        return False
    
    def find_and_click_radio(self, page: Page) -> bool:
        """Find and click radio buttons."""
        try:
            radios = page.locator("input[type='radio']:visible").all()
            for radio in radios:
                try:
                    if radio.is_visible() and not radio.is_checked():
                        radio.click(timeout=500)
                        return True
                except:
                    pass
        except:
            pass
        return False
    
    def ask_claude_fast(self, screenshot: bytes, step: int, attempt: int) -> Dict:
        """Quick Claude query for action."""
        b64 = base64.standard_b64encode(screenshot).decode("utf-8")
        
        prompt = f"""Browser challenge Step {step}/30, attempt {attempt}.

QUICK ANALYSIS NEEDED:
1. What is the MAIN challenge/instruction visible?
2. What SINGLE action will advance to next step?

RULES:
- If popup says "Click X to close" -> click the X button
- If popup says "close button is fake" -> DON'T click dismiss, find alternative
- If you see radio buttons -> select one and submit
- If you see a form -> fill and submit
- Look for "Next", "Submit", "Continue" buttons

Return ONLY JSON:
{{"action": "click|fill|scroll|check", "selector": "CSS or text=Text", "value": "if needed"}}

Be specific. One action only."""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=150,
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
            self.metrics.errors.append(str(e)[:50])
        
        return {}
    
    def execute(self, page: Page, action_data: Dict) -> bool:
        """Execute action quickly."""
        action = action_data.get("action", "")
        selector = action_data.get("selector", "")
        value = action_data.get("value", "")
        
        if not action or not selector:
            return False
        
        try:
            if action == "scroll":
                if "modal" in selector.lower():
                    return self.scroll_modal(page)
                page.evaluate("window.scrollBy(0, 300)")
                return True
            
            if action == "check":
                el = page.locator(selector).first
                if el.count() > 0:
                    el.check(timeout=1000)
                    return True
            
            if action == "fill":
                el = page.locator(selector).first
                if el.count() > 0:
                    el.fill(value or "test", timeout=1000)
                    return True
            
            if action == "click":
                # Try direct selector
                try:
                    el = page.locator(selector).first
                    if el.count() > 0 and el.is_visible():
                        el.click(timeout=1000)
                        return True
                except:
                    pass
                
                # Try text variations
                if "text=" in selector:
                    text = selector.split("text=")[1].strip("'\"")
                    for sel in [f"text={text}", f"button:has-text('{text}')", f"a:has-text('{text}')", f"*:has-text('{text}')"]:
                        try:
                            el = page.locator(sel).first
                            if el.count() > 0 and el.is_visible():
                                el.click(timeout=1000)
                                return True
                        except:
                            pass
            
            return False
        except:
            return False
    
    def quick_actions(self, page: Page) -> bool:
        """Try quick heuristic actions."""
        # Close real popups first
        self.close_real_popups(page)
        
        # Try radio buttons
        if self.find_and_click_radio(page):
            return True
        
        # Try common submit buttons
        for text in ["Submit", "Next", "Continue", "OK", "Confirm", "Done"]:
            try:
                btn = page.locator(f"button:has-text('{text}'):visible").first
                if btn.count() > 0:
                    btn.click(timeout=500)
                    return True
            except:
                pass
        
        return False
    
    def run(self) -> Dict:
        self.metrics.start_time = time.time()
        
        print("\n" + "=" * 60)
        print("FAST Browser Navigation Solver")
        print(f"Target: 30 challenges in under 5 minutes")
        print("=" * 60 + "\n")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless, args=['--no-sandbox'])
            context = browser.new_context(viewport={'width': 1280, 'height': 900})
            page = context.new_page()
            page.on("dialog", lambda d: d.accept())
            
            try:
                self.log("Loading...")
                page.goto(CHALLENGE_URL, timeout=20000)
                page.wait_for_load_state('domcontentloaded', timeout=5000)
                
                # Click START
                try:
                    page.locator("text=START").first.click(timeout=2000)
                    self.log("Started!", "OK")
                except:
                    pass
                
                page.wait_for_timeout(500)
                
                # Accept cookies
                try:
                    page.locator("text=Accept").first.click(timeout=1000)
                except:
                    pass
                
                last_step = 0
                step_start = time.time()
                attempts = 0
                max_attempts = 8
                
                while self.metrics.elapsed < MAX_TIME_SECONDS:
                    current_step = self.get_step(page)
                    
                    # Check for progress
                    if current_step > last_step:
                        step_time = time.time() - step_start
                        self.metrics.step_times.append(step_time)
                        self.metrics.steps_completed = current_step
                        self.log(f"STEP {current_step}/30 ✓ ({step_time:.1f}s)", "OK")
                        last_step = current_step
                        step_start = time.time()
                        attempts = 0
                        
                        if current_step >= 30:
                            self.log("ALL 30 STEPS COMPLETE!", "OK")
                            break
                    
                    attempts += 1
                    
                    if attempts > max_attempts:
                        self.log(f"Stuck on step {current_step}, trying harder...", "WARN")
                        attempts = 0
                        # Reset view
                        page.evaluate("window.scrollTo(0, 0)")
                        self.close_real_popups(page)
                    
                    # Screenshot for AI
                    screenshot = self.screenshot(page, f"s{current_step}_a{attempts}")
                    
                    # Try quick heuristics first
                    if self.quick_actions(page):
                        page.wait_for_timeout(200)
                        continue
                    
                    # Ask Claude
                    action = self.ask_claude_fast(screenshot, current_step or 1, attempts)
                    
                    if action:
                        selector = action.get("selector", "")[:30]
                        self.log(f"  {action.get('action', '?')} -> {selector}")
                        self.execute(page, action)
                    
                    page.wait_for_timeout(300)
                
            except Exception as e:
                self.metrics.errors.append(str(e))
                self.log(f"Error: {e}", "FAIL")
            
            finally:
                self.screenshot(page, "final")
                browser.close()
        
        self.metrics.end_time = time.time()
        report = self.metrics.report()
        
        print("\n" + "=" * 60)
        print("FINAL RESULTS")
        print("=" * 60)
        print(f"Time: {report['duration_formatted']}")
        print(f"Under 5 min: {'YES ✓' if report['under_5_minutes'] else 'NO ✗'}")
        print(f"Solved: {report['challenges']['solved']}/30")
        print(f"Success Rate: {report['challenges']['success_rate']}")
        print(f"API Calls: {report['tokens']['api_calls']}")
        print(f"Total Tokens: {report['tokens']['total']}")
        print(f"Cost: {report['cost_usd']}")
        if report['avg_time_per_step'] > 0:
            print(f"Avg time/step: {report['avg_time_per_step']}s")
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
    
    solver = FastSolver(headless=not args.visible)
    report = solver.run()
    
    success = report["challenges"]["solved"] >= 30 and report["under_5_minutes"]
    print(f"\n{'🎉 CHALLENGE COMPLETE!' if success else '❌ Challenge not completed'}")
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
