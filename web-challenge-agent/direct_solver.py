#!/usr/bin/env python3
"""
Direct solver - handles the specific challenge patterns directly.
"""

import os
import sys
import time
import json
import base64
import re
from datetime import datetime
from playwright.sync_api import sync_playwright, Page

CHALLENGE_URL = "https://serene-frangipane-7fd25b.netlify.app/"
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
MAX_TIME = 300
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "/tmp/direct_results")

class DirectSolver:
    def __init__(self, headless=True):
        self.headless = headless
        self.start_time = 0
        self.solved = 0
        self.tokens = 0
        self.calls = 0
        self.cost = 0
        
        if ANTHROPIC_API_KEY:
            from anthropic import Anthropic
            self.claude = Anthropic(api_key=ANTHROPIC_API_KEY)
        else:
            self.claude = None
        
        os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    def elapsed(self):
        return time.time() - self.start_time
    
    def log(self, msg, level=""):
        sym = {"ok": "✓", "fail": "✗", "warn": "!"}.get(level, " ")
        print(f"[{self.elapsed():5.1f}s] {sym} {msg}")
    
    def get_step(self, page):
        try:
            match = re.search(r'Step\s*(\d+)\s*of\s*30', page.content(), re.I)
            return int(match.group(1)) if match else 0
        except:
            return 0
    
    def close_popups_with_real_x(self, page):
        """Close popups that explicitly say 'Click X to close'."""
        closed = 0
        try:
            # Find all visible elements
            page.wait_for_timeout(100)
            
            # Look for red X buttons (usually have specific styling)
            x_buttons = page.query_selector_all("button")
            for btn in x_buttons:
                try:
                    text = btn.inner_text().strip()
                    if text in ['×', 'X', '✕', '✖', 'x']:
                        # Check if visible
                        box = btn.bounding_box()
                        if box:
                            btn.click()
                            closed += 1
                            page.wait_for_timeout(50)
                except:
                    pass
        except:
            pass
        return closed
    
    def press_escape(self, page):
        """Press Escape to close popups."""
        try:
            page.keyboard.press("Escape")
            page.wait_for_timeout(100)
        except:
            pass
    
    def click_outside(self, page):
        """Click outside popups to close them."""
        try:
            page.mouse.click(10, 10)
            page.wait_for_timeout(100)
        except:
            pass
    
    def fill_code_field(self, page):
        """Fill any code/text input fields."""
        try:
            # Find code input
            inputs = page.query_selector_all("input[type='text'], input:not([type])")
            for inp in inputs:
                try:
                    placeholder = inp.get_attribute("placeholder") or ""
                    if inp.is_visible():
                        # Fill with test value
                        inp.fill("TEST12")  # 6 characters
                        return True
                except:
                    pass
        except:
            pass
        return False
    
    def click_submit(self, page):
        """Click submit/continue buttons."""
        for text in ["Submit & Continue", "Submit", "Continue", "Next", "OK", "Done"]:
            try:
                btn = page.locator(f"button:has-text('{text}')").first
                if btn.count() > 0 and btn.is_visible():
                    btn.click(timeout=500)
                    return True
            except:
                pass
        return False
    
    def select_radio(self, page):
        """Select radio buttons."""
        try:
            radios = page.query_selector_all("input[type='radio']")
            for r in radios:
                try:
                    if r.is_visible() and not r.is_checked():
                        r.click()
                        return True
                except:
                    pass
        except:
            pass
        return False
    
    def scroll_modal(self, page):
        """Scroll inside modals."""
        try:
            page.evaluate("""
                document.querySelectorAll('[style*="overflow"], .modal, [role="dialog"]').forEach(el => {
                    el.scrollTop += 100;
                });
            """)
        except:
            pass
    
    def accept_cookies(self, page):
        try:
            page.locator("button:has-text('Accept')").first.click(timeout=500)
            return True
        except:
            return False
    
    def ask_ai(self, page, step):
        """Quick AI consultation."""
        if not self.claude:
            return None
        
        try:
            screenshot = page.screenshot(timeout=2000)
            b64 = base64.standard_b64encode(screenshot).decode()
            
            with open(f"{OUTPUT_DIR}/s{step}_{int(self.elapsed())}.png", 'wb') as f:
                f.write(screenshot)
            
            resp = self.claude.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=80,
                messages=[{
                    "role": "user", 
                    "content": [
                        {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": b64}},
                        {"type": "text", "text": f"Step {step}. What's the ONE action to advance? Reply: {{\"do\": \"click X button\" or \"fill CODE123\" or \"select radio\" or \"click Submit\"}}"}
                    ]
                }]
            )
            
            self.calls += 1
            self.tokens += resp.usage.input_tokens + resp.usage.output_tokens
            self.cost = self.tokens / 1e6 * 10  # Approx cost
            
            text = resp.content[0].text
            match = re.search(r'"do"\s*:\s*"([^"]+)"', text)
            return match.group(1) if match else None
        except Exception as e:
            return None
    
    def execute_ai_action(self, page, action):
        """Execute AI suggested action."""
        if not action:
            return False
        
        action_lower = action.lower()
        
        if "x button" in action_lower or "close" in action_lower:
            return self.close_popups_with_real_x(page) > 0
        
        if "fill" in action_lower:
            # Extract value
            match = re.search(r'fill\s+(\w+)', action_lower)
            value = match.group(1) if match else "TEST12"
            try:
                inp = page.locator("input:visible").first
                if inp.count() > 0:
                    inp.fill(value[:6] if len(value) > 6 else value)
                    return True
            except:
                pass
        
        if "radio" in action_lower or "select" in action_lower:
            return self.select_radio(page)
        
        if "submit" in action_lower or "continue" in action_lower:
            return self.click_submit(page)
        
        # Try clicking text
        try:
            page.locator(f"text={action}").first.click(timeout=500)
            return True
        except:
            pass
        
        return False
    
    def run(self):
        self.start_time = time.time()
        
        print("\n" + "="*60)
        print("DIRECT SOLVER - Target: 30 steps in 5 minutes")
        print("="*60 + "\n")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless, args=['--no-sandbox'])
            page = browser.new_context(viewport={'width': 1280, 'height': 900}).new_page()
            page.on("dialog", lambda d: d.accept())
            
            try:
                self.log("Loading...")
                page.goto(CHALLENGE_URL, timeout=15000)
                
                # Start
                try:
                    page.locator("text=START").click(timeout=2000)
                    self.log("Started", "ok")
                except:
                    pass
                
                page.wait_for_timeout(300)
                
                last_step = 0
                ai_interval = 3
                iteration = 0
                
                while self.elapsed() < MAX_TIME:
                    step = self.get_step(page)
                    
                    if step > last_step:
                        self.solved = step
                        self.log(f"STEP {step}/30", "ok")
                        last_step = step
                        iteration = 0
                        if step >= 30:
                            self.log("COMPLETE!", "ok")
                            break
                    
                    iteration += 1
                    
                    # Strategy: cycle through actions
                    
                    # 1. Close real X popups
                    self.close_popups_with_real_x(page)
                    
                    # 2. Press Escape for fake popups
                    if iteration % 2 == 0:
                        self.press_escape(page)
                    
                    # 3. Click outside
                    if iteration % 3 == 0:
                        self.click_outside(page)
                    
                    # 4. Accept cookies
                    self.accept_cookies(page)
                    
                    # 5. Fill code field
                    self.fill_code_field(page)
                    
                    # 6. Select radios
                    self.select_radio(page)
                    
                    # 7. Scroll in modal
                    if iteration % 4 == 0:
                        self.scroll_modal(page)
                    
                    # 8. Try submit
                    self.click_submit(page)
                    
                    # 9. AI help periodically
                    if iteration % ai_interval == 0 and self.claude:
                        action = self.ask_ai(page, step or 1)
                        if action:
                            self.log(f"AI: {action[:30]}")
                            self.execute_ai_action(page, action)
                    
                    page.wait_for_timeout(150)
                    
                    # Reset if stuck
                    if iteration > 20:
                        self.log("Resetting...", "warn")
                        iteration = 0
                        page.evaluate("window.scrollTo(0,0)")
                        page.keyboard.press("Escape")
                
            except Exception as e:
                self.log(str(e), "fail")
            
            finally:
                page.screenshot(path=f"{OUTPUT_DIR}/final.png")
                browser.close()
        
        # Report
        elapsed = self.elapsed()
        report = {
            "duration_seconds": round(elapsed, 2),
            "duration_formatted": f"{int(elapsed//60)}m {int(elapsed%60)}s",
            "under_5_minutes": elapsed < 300,
            "challenges": {"total": 30, "solved": self.solved, "rate": f"{self.solved/30*100:.1f}%"},
            "tokens": {"total": self.tokens, "calls": self.calls},
            "cost_usd": f"${self.cost:.4f}"
        }
        
        print("\n" + "="*60)
        print("RESULTS")
        print("="*60)
        for k, v in report.items():
            if isinstance(v, dict):
                print(f"{k}: {v}")
            else:
                print(f"{k}: {v}")
        print("="*60)
        
        with open(f"{OUTPUT_DIR}/results.json", 'w') as f:
            json.dump(report, f, indent=2)
        
        return report


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--visible", action="store_true")
    ap.add_argument("--output")
    args = ap.parse_args()
    
    if args.output:
        OUTPUT_DIR = args.output
    
    solver = DirectSolver(headless=not args.visible)
    r = solver.run()
    
    success = r["challenges"]["solved"] >= 30 and r["under_5_minutes"]
    print(f"\n{'🎉 SUCCESS!' if success else '❌ Not complete'}")
    sys.exit(0 if success else 1)
