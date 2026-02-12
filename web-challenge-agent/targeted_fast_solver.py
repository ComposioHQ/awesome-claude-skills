#!/usr/bin/env python3
"""
Targeted Fast Solver - handles the specific popup patterns.
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
MAX_TIME = 300
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "/tmp/targeted_fast_results")


@dataclass
class Metrics:
    start: float = 0
    end: float = 0
    solved: int = 0
    in_tokens: int = 0
    out_tokens: int = 0
    calls: int = 0
    errors: List[str] = field(default_factory=list)
    
    @property
    def elapsed(self):
        return (self.end if self.end else time.time()) - self.start
    
    @property
    def cost(self):
        return (self.in_tokens / 1e6 * 3) + (self.out_tokens / 1e6 * 15)
    
    def report(self):
        return {
            "duration_seconds": round(self.elapsed, 2),
            "duration_formatted": f"{int(self.elapsed//60)}m {int(self.elapsed%60)}s",
            "under_5_minutes": self.elapsed < 300,
            "challenges": {"total": 30, "solved": self.solved, 
                          "rate": f"{self.solved/30*100:.1f}%"},
            "tokens": {"input": self.in_tokens, "output": self.out_tokens,
                      "total": self.in_tokens + self.out_tokens, "calls": self.calls},
            "cost_usd": f"${self.cost:.4f}",
            "errors": self.errors[:5]
        }


class TargetedFastSolver:
    def __init__(self, headless=True):
        self.headless = headless
        self.m = Metrics()
        if not ANTHROPIC_API_KEY:
            sys.exit("ANTHROPIC_API_KEY required")
        from anthropic import Anthropic
        self.claude = Anthropic(api_key=ANTHROPIC_API_KEY)
        os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    def log(self, msg, ok=False, fail=False, warn=False):
        sym = "✓ " if ok else "✗ " if fail else "! " if warn else "  "
        print(f"[{self.m.elapsed:5.1f}s] {sym}{msg}")
    
    def get_step(self, page):
        try:
            match = re.search(r'Step\s*(\d+)\s*(?:of|/)\s*30', page.content(), re.I)
            return int(match.group(1)) if match else 0
        except:
            return 0
    
    def handle_popups(self, page):
        """Handle the specific popup patterns on this site."""
        closed = 0
        
        # 1. Close popups that say "Click X to close" - these have REAL X buttons
        try:
            # The red X buttons are real close buttons
            red_x = page.locator("button:visible").all()
            for btn in red_x:
                try:
                    # Check if button looks like an X and is red-ish or the popup says "Click X"
                    classes = btn.get_attribute("class") or ""
                    style = btn.get_attribute("style") or ""
                    text = btn.inner_text(timeout=100).strip()
                    
                    if text in ['×', 'X', '✕', '✖']:
                        # Check if parent popup says "Click X to close"
                        parent = btn.locator("xpath=ancestor::div[contains(@class,'fixed') or contains(@class,'absolute')]").first
                        if parent.count() > 0:
                            parent_text = parent.inner_text(timeout=200)
                            if "Click X to close" in parent_text:
                                btn.click(timeout=500)
                                closed += 1
                                page.wait_for_timeout(100)
                except:
                    pass
        except:
            pass
        
        # 2. For popups with "fake" close button, click outside
        try:
            fake_popups = page.locator("text=close button is fake").all()
            for fp in fake_popups:
                try:
                    # Click outside the popup to close it
                    page.mouse.click(5, 5)
                    closed += 1
                    page.wait_for_timeout(100)
                except:
                    pass
        except:
            pass
        
        return closed
    
    def accept_cookies(self, page):
        try:
            page.locator("button:has-text('Accept')").first.click(timeout=500)
            return True
        except:
            return False
    
    def try_form_actions(self, page):
        """Try common form actions."""
        # Radio buttons
        try:
            radios = page.locator("input[type='radio']:visible").all()
            for r in radios:
                if r.is_visible() and not r.is_checked():
                    r.click(timeout=300)
                    return True
        except:
            pass
        
        # Checkboxes
        try:
            cbs = page.locator("input[type='checkbox']:visible").all()
            for cb in cbs:
                if cb.is_visible() and not cb.is_checked():
                    cb.click(timeout=300)
                    return True
        except:
            pass
        
        # Text inputs
        try:
            inputs = page.locator("input[type='text']:visible, input:not([type]):visible").all()
            for inp in inputs:
                if inp.is_visible() and not inp.input_value():
                    inp.fill("test", timeout=300)
                    return True
        except:
            pass
        
        # Submit buttons
        for text in ["Submit", "Next", "Continue", "OK", "Done", "Confirm"]:
            try:
                btn = page.locator(f"button:has-text('{text}'):visible").first
                if btn.count() > 0:
                    btn.click(timeout=500)
                    return True
            except:
                pass
        
        return False
    
    def scroll_in_modal(self, page):
        """Scroll inside modals to reveal content."""
        try:
            # Find scrollable modals
            modals = page.locator("[style*='overflow'], .modal, [role='dialog']").all()
            for m in modals:
                try:
                    if m.is_visible():
                        m.evaluate("el => { el.scrollTop += 150; }")
                        return True
                except:
                    pass
        except:
            pass
        return False
    
    def ask_ai(self, page, step, attempt):
        """Quick AI query."""
        try:
            screenshot = page.screenshot(timeout=2000)
            b64 = base64.standard_b64encode(screenshot).decode()
            
            # Save screenshot
            with open(f"{OUTPUT_DIR}/s{step}_a{attempt}.png", 'wb') as f:
                f.write(screenshot)
            
            resp = self.claude.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=100,
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": b64}},
                        {"type": "text", "text": f"Step {step}/30. What ONE element should I click to advance? Return ONLY: {{\"click\": \"exact button text or CSS selector\"}}"}
                    ]
                }]
            )
            
            self.m.calls += 1
            self.m.in_tokens += resp.usage.input_tokens
            self.m.out_tokens += resp.usage.output_tokens
            
            match = re.search(r'\{[^}]+\}', resp.content[0].text)
            if match:
                data = json.loads(match.group())
                return data.get("click", "")
        except Exception as e:
            self.m.errors.append(str(e)[:30])
        return ""
    
    def click_target(self, page, target):
        """Click target element."""
        if not target:
            return False
        
        selectors = [
            f"text={target}",
            f"button:has-text('{target}')",
            f"a:has-text('{target}')",
            target  # Try as-is (might be CSS selector)
        ]
        
        for sel in selectors:
            try:
                el = page.locator(sel).first
                if el.count() > 0 and el.is_visible():
                    el.click(timeout=1000)
                    return True
            except:
                pass
        return False
    
    def run(self):
        self.m.start = time.time()
        
        print("\n" + "="*60)
        print("TARGETED FAST SOLVER")
        print("="*60 + "\n")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless, args=['--no-sandbox'])
            page = browser.new_context(viewport={'width': 1280, 'height': 900}).new_page()
            page.on("dialog", lambda d: d.accept())
            
            try:
                self.log("Loading...")
                page.goto(CHALLENGE_URL, timeout=15000)
                page.wait_for_timeout(500)
                
                # Start
                try:
                    page.locator("text=START").click(timeout=2000)
                    self.log("Started", ok=True)
                except:
                    pass
                
                page.wait_for_timeout(300)
                self.accept_cookies(page)
                
                last_step = 0
                attempts = 0
                
                while self.m.elapsed < MAX_TIME:
                    step = self.get_step(page)
                    
                    if step > last_step:
                        self.m.solved = step
                        self.log(f"STEP {step}/30", ok=True)
                        last_step = step
                        attempts = 0
                        if step >= 30:
                            self.log("ALL DONE!", ok=True)
                            break
                    
                    attempts += 1
                    
                    # Handle popups first
                    self.handle_popups(page)
                    
                    # Try form actions
                    if self.try_form_actions(page):
                        page.wait_for_timeout(200)
                        continue
                    
                    # Scroll in modals
                    if attempts % 3 == 0:
                        self.scroll_in_modal(page)
                    
                    # Ask AI every few attempts
                    if attempts % 2 == 0:
                        target = self.ask_ai(page, step or 1, attempts)
                        if target:
                            self.log(f"AI: {target[:30]}")
                            self.click_target(page, target)
                    
                    page.wait_for_timeout(200)
                    
                    if attempts > 15:
                        self.log("Resetting...", warn=True)
                        attempts = 0
                        page.evaluate("window.scrollTo(0,0)")
                
            except Exception as e:
                self.m.errors.append(str(e))
                self.log(str(e), fail=True)
            
            finally:
                page.screenshot(path=f"{OUTPUT_DIR}/final.png")
                browser.close()
        
        self.m.end = time.time()
        r = self.m.report()
        
        print("\n" + "="*60)
        print("RESULTS")
        print("="*60)
        print(f"Time: {r['duration_formatted']}")
        print(f"Under 5 min: {'YES' if r['under_5_minutes'] else 'NO'}")
        print(f"Solved: {r['challenges']['solved']}/30 ({r['challenges']['rate']})")
        print(f"Tokens: {r['tokens']['total']} | Cost: {r['cost_usd']}")
        print("="*60)
        
        with open(f"{OUTPUT_DIR}/results.json", 'w') as f:
            json.dump(r, f, indent=2)
        
        return r


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--visible", action="store_true")
    ap.add_argument("--output")
    args = ap.parse_args()
    
    if args.output:
        OUTPUT_DIR = args.output
    
    solver = TargetedFastSolver(headless=not args.visible)
    r = solver.run()
    
    success = r["challenges"]["solved"] >= 30 and r["under_5_minutes"]
    print(f"\n{'🎉 SUCCESS!' if success else '❌ Not complete'}")
    sys.exit(0 if success else 1)
