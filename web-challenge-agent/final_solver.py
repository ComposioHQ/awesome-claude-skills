#!/usr/bin/env python3
"""
Final Browser Navigation Challenge Solver
Handles the modal/dialog-based challenge structure.
"""

import os
import sys
import time
import json
import re
from datetime import datetime
from typing import Dict, List
from dataclasses import dataclass, field
from playwright.sync_api import sync_playwright, Page

CHALLENGE_URL = "https://serene-frangipane-7fd25b.netlify.app/"
MAX_TIME_SECONDS = 300
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "/tmp/final_results")


@dataclass
class Metrics:
    start_time: float = 0
    end_time: float = 0
    steps_completed: int = 0
    actions_taken: int = 0
    errors: List[str] = field(default_factory=list)
    
    @property
    def elapsed(self) -> float:
        return (self.end_time if self.end_time else time.time()) - self.start_time
    
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
            "tokens": {"input": 0, "output": 0, "total": 0, "api_calls": 0},
            "cost_usd": "$0.00",
            "actions_taken": self.actions_taken,
            "errors": self.errors[:10]
        }


class FinalSolver:
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.metrics = Metrics()
        os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    def log(self, msg: str, level: str = "INFO"):
        elapsed = self.metrics.elapsed
        sym = {"INFO": "  ", "OK": "✓ ", "FAIL": "✗ ", "WARN": "! "}
        print(f"[{elapsed:5.1f}s] {sym.get(level, '  ')}{msg}")
    
    def screenshot(self, page: Page, name: str):
        try:
            page.screenshot(path=os.path.join(OUTPUT_DIR, f"{name}.png"), timeout=3000)
        except:
            pass
    
    def get_step(self, page: Page) -> int:
        try:
            text = page.inner_text("body", timeout=1000)
            match = re.search(r'Step\s*(\d+)\s*(?:of|/)\s*30', text, re.IGNORECASE)
            if match:
                return int(match.group(1))
        except:
            pass
        return 0
    
    def close_popups(self, page: Page):
        """Close any blocking popups."""
        # Cookie consent
        for sel in ["text=Accept", "text=Accept All", "text=Got it", "text=OK", ".cookie-accept", "#accept-cookies"]:
            try:
                el = page.locator(sel).first
                if el.count() > 0 and el.is_visible():
                    el.click(timeout=500)
                    self.log("Closed popup", "OK")
                    page.wait_for_timeout(200)
            except:
                pass
    
    def find_dialog_options(self, page: Page) -> List:
        """Find clickable options in any dialog/modal."""
        options = []
        
        # Look for dialog/modal
        dialog_selectors = [
            ".modal", ".dialog", ".popup", "[role='dialog']",
            ".modal-content", ".popup-content"
        ]
        
        for dialog_sel in dialog_selectors:
            try:
                dialog = page.locator(dialog_sel).first
                if dialog.count() > 0 and dialog.is_visible():
                    # Find clickable elements inside
                    clickables = dialog.locator("button, a, [role='button'], .option, .clickable, li").all()
                    for el in clickables:
                        try:
                            if el.is_visible():
                                text = el.inner_text(timeout=300).strip()
                                if text and len(text) > 0:
                                    options.append({"element": el, "text": text})
                        except:
                            pass
            except:
                pass
        
        return options
    
    def click_dialog_option(self, page: Page, step: int) -> bool:
        """Click an option in the dialog."""
        options = self.find_dialog_options(page)
        
        if not options:
            return False
        
        self.log(f"Found {len(options)} dialog options")
        
        # Priority: click options that match patterns or just the first one
        for opt in options:
            try:
                text = opt["text"].lower()
                # Skip if it's just navigation text
                if any(skip in text for skip in ["close", "cancel", "skip", "back"]):
                    continue
                
                self.log(f"  Clicking: {opt['text'][:40]}...")
                opt["element"].click(timeout=2000)
                self.metrics.actions_taken += 1
                page.wait_for_timeout(300)
                return True
            except:
                continue
        
        return False
    
    def click_any_button(self, page: Page) -> bool:
        """Click any visible interactive button."""
        # First try buttons with positive text
        positive_texts = ["Select", "Click", "Go", "Next", "Continue", "Submit", "Confirm", "OK", "Yes", "Accept"]
        
        for text in positive_texts:
            try:
                btn = page.locator(f"button:has-text('{text}'), a:has-text('{text}')").first
                if btn.count() > 0 and btn.is_visible():
                    self.log(f"  Clicking button: {text}")
                    btn.click(timeout=1000)
                    self.metrics.actions_taken += 1
                    return True
            except:
                pass
        
        # Try any visible button
        try:
            buttons = page.locator("button:visible").all()
            for btn in buttons:
                try:
                    btn_text = btn.inner_text(timeout=300)
                    if btn_text and "skip" not in btn_text.lower():
                        self.log(f"  Clicking: {btn_text[:30]}")
                        btn.click(timeout=1000)
                        self.metrics.actions_taken += 1
                        return True
                except:
                    pass
        except:
            pass
        
        return False
    
    def try_section_buttons(self, page: Page) -> bool:
        """Try clicking buttons in sections."""
        try:
            # Find all sections
            sections = page.locator("text=/Section \\d+/").all()
            
            for section in sections[:20]:  # Limit to first 20
                try:
                    # Scroll to section
                    section.scroll_into_view_if_needed(timeout=1000)
                    page.wait_for_timeout(100)
                    
                    # Find nearby button
                    parent = section.locator("..").first
                    if parent.count() > 0:
                        btn = parent.locator("button, a.btn, .button").first
                        if btn.count() > 0 and btn.is_visible():
                            self.log(f"  Clicking section button")
                            btn.click(timeout=1000)
                            self.metrics.actions_taken += 1
                            page.wait_for_timeout(200)
                            return True
                except:
                    continue
        except:
            pass
        
        return False
    
    def scroll_and_find(self, page: Page) -> bool:
        """Scroll page and look for interactive elements."""
        try:
            # Scroll down
            page.evaluate("window.scrollBy(0, 500)")
            page.wait_for_timeout(200)
            
            # Look for highlighted or actionable elements
            highlight_selectors = [
                ".highlight button", ".active button",
                ".selected button", "[data-action] button",
                "button.primary", "button.action"
            ]
            
            for sel in highlight_selectors:
                try:
                    el = page.locator(sel).first
                    if el.count() > 0 and el.is_visible():
                        self.log(f"  Found highlighted element")
                        el.click(timeout=1000)
                        self.metrics.actions_taken += 1
                        return True
                except:
                    pass
            
            return True  # Scrolled at least
        except:
            return False
    
    def solve_step(self, page: Page, step: int) -> bool:
        """Attempt to solve current step."""
        # Close any popups first
        self.close_popups(page)
        
        # Strategy 1: Click dialog option
        if self.click_dialog_option(page, step):
            return True
        
        # Strategy 2: Click any positive button
        if self.click_any_button(page):
            return True
        
        # Strategy 3: Try section buttons
        if self.try_section_buttons(page):
            return True
        
        # Strategy 4: Scroll and find
        self.scroll_and_find(page)
        
        return False
    
    def run(self) -> Dict:
        self.metrics.start_time = time.time()
        
        print("\n" + "=" * 60)
        print("Final Browser Navigation Solver")
        print(f"URL: {CHALLENGE_URL}")
        print("=" * 60 + "\n")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=self.headless,
                args=['--no-sandbox']
            )
            context = browser.new_context(viewport={'width': 1400, 'height': 900})
            page = context.new_page()
            page.on("dialog", lambda d: d.accept())
            
            try:
                self.log("Loading page...")
                page.goto(CHALLENGE_URL, timeout=30000)
                page.wait_for_load_state('networkidle', timeout=10000)
                self.screenshot(page, "00_start")
                
                # Close popups
                self.close_popups(page)
                
                # Click START
                try:
                    start = page.locator("text=START").first
                    if start.count() > 0 and start.is_visible():
                        start.click(timeout=3000)
                        self.log("Clicked START", "OK")
                        page.wait_for_timeout(1000)
                except:
                    pass
                
                last_step = 0
                stuck = 0
                max_stuck = 10
                
                while self.metrics.elapsed < MAX_TIME_SECONDS:
                    current_step = self.get_step(page)
                    
                    # Check for progress
                    if current_step > last_step:
                        self.metrics.steps_completed = current_step
                        self.log(f"Step {current_step}/30", "OK")
                        last_step = current_step
                        stuck = 0
                        
                        if current_step >= 30:
                            self.log("All steps completed!", "OK")
                            break
                    else:
                        stuck += 1
                    
                    self.screenshot(page, f"{current_step:02d}_{stuck}")
                    
                    # Try to solve
                    self.solve_step(page, current_step)
                    page.wait_for_timeout(300)
                    
                    # Check again
                    new_step = self.get_step(page)
                    if new_step > current_step:
                        self.metrics.steps_completed = new_step
                        self.log(f"Advanced to step {new_step}!", "OK")
                        last_step = new_step
                        stuck = 0
                    
                    if stuck >= max_stuck:
                        self.log(f"Stuck on step {current_step} after {max_stuck} tries", "WARN")
                        # Try aggressive scrolling
                        page.evaluate("window.scrollTo(0, 0)")
                        page.wait_for_timeout(200)
                        stuck = 0
                
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
        print(f"Actions: {report['actions_taken']}")
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
    
    solver = FinalSolver(headless=not args.visible)
    report = solver.run()
    sys.exit(0 if report["challenges"]["solved"] >= 25 else 1)


if __name__ == "__main__":
    main()
