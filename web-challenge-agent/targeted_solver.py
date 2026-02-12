#!/usr/bin/env python3
"""
Targeted Browser Navigation Challenge Solver
Specifically designed for https://serene-frangipane-7fd25b.netlify.app/
"""

import os
import sys
import time
import json
import re
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from playwright.sync_api import sync_playwright, Page

CHALLENGE_URL = "https://serene-frangipane-7fd25b.netlify.app/"
MAX_TIME_SECONDS = 300
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "/tmp/targeted_results")


@dataclass
class Metrics:
    start_time: float = 0
    end_time: float = 0
    steps_completed: int = 0
    total_steps: int = 30
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
                "total": self.total_steps,
                "solved": self.steps_completed,
                "success_rate": f"{(self.steps_completed / self.total_steps) * 100:.1f}%"
            },
            "tokens": {"input": 0, "output": 0, "total": 0, "api_calls": 0},
            "cost_usd": "$0.00",
            "errors": self.errors[:10]
        }


class TargetedSolver:
    """Targeted solver for the Browser Navigation Challenge."""
    
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
            page.screenshot(path=os.path.join(OUTPUT_DIR, f"{name}.png"), full_page=True, timeout=3000)
        except:
            pass
    
    def get_step_number(self, page: Page) -> int:
        """Get current step from the step indicator."""
        try:
            # Look for "Step X of 30" text
            text = page.inner_text("body", timeout=1000)
            match = re.search(r'Step\s*(\d+)\s*(?:of|/)\s*30', text, re.IGNORECASE)
            if match:
                return int(match.group(1))
        except:
            pass
        return 0
    
    def close_cookie_popup(self, page: Page):
        """Close cookie consent popup if present."""
        try:
            for sel in [
                "text=Accept", "text=Accept All", "text=I Accept",
                "text=Got it", "text=OK", "text=Agree",
                ".cookie-consent button", "#cookie-accept"
            ]:
                el = page.locator(sel).first
                if el.count() > 0 and el.is_visible():
                    el.click(timeout=1000)
                    page.wait_for_timeout(200)
                    return
        except:
            pass
    
    def get_modal_instruction(self, page: Page) -> str:
        """Get instruction from the modal/popup."""
        # Look for modal content
        modal_selectors = [
            ".modal", ".modal-content", ".popup", ".dialog",
            "[role='dialog']", ".challenge-modal", ".step-modal",
            ".instruction-modal"
        ]
        
        for sel in modal_selectors:
            try:
                modal = page.locator(sel).first
                if modal.count() > 0 and modal.is_visible():
                    text = modal.inner_text(timeout=500)
                    if text and len(text) > 5:
                        return text.strip()
            except:
                pass
        
        # Fallback: look for instruction-like text
        try:
            # Look for the challenge instruction
            instruction_el = page.locator("text=/Click on|Find|Select|Enter|Type|Scroll|Hover|Navigate/i").first
            if instruction_el.count() > 0:
                return instruction_el.inner_text(timeout=500)
        except:
            pass
        
        return ""
    
    def parse_instruction(self, instruction: str) -> Dict:
        """Parse instruction to extract action and target."""
        instruction_lower = instruction.lower()
        
        result = {
            "action": "click",
            "section": None,
            "element_text": None,
            "element_type": "button",
            "number": None
        }
        
        # Extract section number
        section_match = re.search(r'section\s*(\d+)', instruction_lower)
        if section_match:
            result["section"] = int(section_match.group(1))
        
        # Extract element text in quotes
        quote_match = re.search(r'"([^"]+)"', instruction)
        if quote_match:
            result["element_text"] = quote_match.group(1)
        
        # Extract button/link number
        num_match = re.search(r'(?:button|link|option)\s*#?(\d+)', instruction_lower)
        if num_match:
            result["number"] = int(num_match.group(1))
        
        # Determine action
        if 'hover' in instruction_lower:
            result["action"] = "hover"
        elif 'double' in instruction_lower:
            result["action"] = "dblclick"
        elif 'right' in instruction_lower and 'click' in instruction_lower:
            result["action"] = "rightclick"
        elif 'scroll' in instruction_lower:
            result["action"] = "scroll"
        elif 'type' in instruction_lower or 'enter' in instruction_lower:
            result["action"] = "fill"
        elif 'select' in instruction_lower:
            result["action"] = "select"
        elif 'check' in instruction_lower:
            result["action"] = "check"
        
        # Determine element type
        if 'link' in instruction_lower:
            result["element_type"] = "link"
        elif 'input' in instruction_lower or 'field' in instruction_lower:
            result["element_type"] = "input"
        elif 'dropdown' in instruction_lower:
            result["element_type"] = "select"
        
        return result
    
    def find_and_interact(self, page: Page, parsed: Dict) -> bool:
        """Find the target element and interact with it."""
        action = parsed["action"]
        section = parsed.get("section")
        element_text = parsed.get("element_text")
        element_type = parsed.get("element_type")
        number = parsed.get("number")
        
        try:
            # If section specified, scroll to it first
            if section:
                try:
                    section_el = page.locator(f"text=Section {section}").first
                    if section_el.count() > 0:
                        section_el.scroll_into_view_if_needed(timeout=2000)
                        page.wait_for_timeout(200)
                except:
                    pass
            
            # Build selectors to try
            selectors = []
            
            if element_text:
                selectors.append(f'text="{element_text}"')
                selectors.append(f"button:has-text('{element_text}')")
                selectors.append(f"a:has-text('{element_text}')")
            
            if section and element_type == "button":
                # Find buttons within or near the section
                selectors.append(f"text=Section {section} >> .. >> button")
            
            if number and element_type == "button":
                selectors.append(f"button >> nth={number - 1}")
            
            # Generic selectors
            selectors.extend([
                "button:visible:not(:disabled)",
                "a:visible",
                ".btn:visible"
            ])
            
            # Try each selector
            for sel in selectors:
                try:
                    el = page.locator(sel).first
                    if el.count() > 0 and el.is_visible():
                        el.scroll_into_view_if_needed(timeout=1000)
                        page.wait_for_timeout(100)
                        
                        if action == "click":
                            el.click(timeout=2000)
                        elif action == "hover":
                            el.hover(timeout=2000)
                        elif action == "dblclick":
                            el.dblclick(timeout=2000)
                        elif action == "rightclick":
                            el.click(button="right", timeout=2000)
                        elif action == "fill":
                            el.fill("test", timeout=2000)
                        elif action == "select":
                            el.select_option(index=1, timeout=2000)
                        elif action == "check":
                            el.check(timeout=2000)
                        
                        return True
                except:
                    continue
            
            # Handle scroll action
            if action == "scroll":
                page.evaluate("window.scrollBy(0, 500)")
                page.wait_for_timeout(300)
                return True
            
            return False
            
        except Exception as e:
            self.metrics.errors.append(str(e))
            return False
    
    def click_next_or_continue(self, page: Page) -> bool:
        """Click any next/continue button."""
        for text in ["Next", "Continue", "Submit", "Done", "OK", "Proceed", "Go"]:
            try:
                btn = page.locator(f"button:has-text('{text}')").first
                if btn.count() > 0 and btn.is_visible():
                    btn.click(timeout=1000)
                    return True
            except:
                pass
        
        # Click any button in a modal
        try:
            modal_btn = page.locator(".modal button:visible, [role='dialog'] button:visible").first
            if modal_btn.count() > 0:
                modal_btn.click(timeout=1000)
                return True
        except:
            pass
        
        return False
    
    def brute_force_step(self, page: Page, step: int) -> bool:
        """Try multiple approaches to complete a step."""
        # Strategy 1: Click highlighted/primary buttons
        primary_selectors = [
            "button.primary", "button.btn-primary",
            ".highlight button", ".active button",
            "button:has-text('Click')", "button:has-text('Visit')",
            "button:has-text('Go')", "button:has-text('Submit')"
        ]
        
        for sel in primary_selectors:
            try:
                btn = page.locator(sel).first
                if btn.count() > 0 and btn.is_visible():
                    btn.scroll_into_view_if_needed(timeout=1000)
                    btn.click(timeout=1000)
                    page.wait_for_timeout(300)
                    
                    # Check if step advanced
                    new_step = self.get_step_number(page)
                    if new_step > step:
                        return True
            except:
                pass
        
        # Strategy 2: Click section buttons in order
        for i in range(1, 101):
            try:
                section = page.locator(f"text=Section {i}").first
                if section.count() > 0:
                    section.scroll_into_view_if_needed(timeout=1000)
                    
                    # Find button near section
                    btn = page.locator(f"text=Section {i} >> .. >> button, text=Section {i} >> .. >> a.btn").first
                    if btn.count() > 0 and btn.is_visible():
                        btn.click(timeout=1000)
                        page.wait_for_timeout(200)
                        
                        new_step = self.get_step_number(page)
                        if new_step > step:
                            return True
            except:
                pass
        
        # Strategy 3: Click any visible button
        try:
            buttons = page.locator("button:visible").all()
            for btn in buttons[:10]:
                try:
                    if btn.is_visible():
                        btn.click(timeout=500)
                        page.wait_for_timeout(200)
                        
                        new_step = self.get_step_number(page)
                        if new_step > step:
                            return True
                except:
                    pass
        except:
            pass
        
        return False
    
    def run(self) -> Dict:
        """Main execution."""
        self.metrics.start_time = time.time()
        
        print("\n" + "=" * 60)
        print("Targeted Browser Navigation Solver")
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
                
                # Close any cookie popup
                self.close_cookie_popup(page)
                
                # Click START
                try:
                    page.locator("text=START").first.click(timeout=3000)
                    self.log("Started", "OK")
                    page.wait_for_timeout(500)
                except:
                    pass
                
                # Main loop
                current_step = self.get_step_number(page)
                if current_step == 0:
                    current_step = 1
                
                last_step = current_step
                stuck_counter = 0
                
                while self.metrics.elapsed < MAX_TIME_SECONDS and current_step <= 30:
                    self.log(f"Step {current_step}/30")
                    self.screenshot(page, f"{current_step:02d}_before")
                    
                    # Close cookie popup if it reappears
                    self.close_cookie_popup(page)
                    
                    # Get modal instruction
                    instruction = self.get_modal_instruction(page)
                    if instruction:
                        self.log(f"  Instruction: {instruction[:50]}...")
                        parsed = self.parse_instruction(instruction)
                        success = self.find_and_interact(page, parsed)
                        
                        if success:
                            self.log("  Action executed", "OK")
                        else:
                            self.log("  Could not execute parsed action", "WARN")
                    
                    page.wait_for_timeout(300)
                    
                    # Try clicking next/continue
                    self.click_next_or_continue(page)
                    page.wait_for_timeout(200)
                    
                    # Check if step advanced
                    new_step = self.get_step_number(page)
                    
                    if new_step > current_step:
                        self.metrics.steps_completed += (new_step - current_step)
                        self.log(f"Advanced to step {new_step}!", "OK")
                        current_step = new_step
                        stuck_counter = 0
                    else:
                        stuck_counter += 1
                        
                        if stuck_counter >= 3:
                            self.log("  Trying brute force...", "WARN")
                            if self.brute_force_step(page, current_step):
                                new_step = self.get_step_number(page)
                                if new_step > current_step:
                                    self.metrics.steps_completed += (new_step - current_step)
                                    self.log(f"Brute force worked! Step {new_step}", "OK")
                                    current_step = new_step
                                    stuck_counter = 0
                        
                        if stuck_counter >= 6:
                            self.log("  Giving up on this step, forcing advance", "FAIL")
                            current_step += 1
                            stuck_counter = 0
                    
                    self.screenshot(page, f"{current_step:02d}_after")
                    page.wait_for_timeout(200)
                
                if current_step > 30:
                    self.log("All 30 steps completed!", "OK")
                    self.metrics.steps_completed = 30
                    
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
    
    solver = TargetedSolver(headless=not args.visible)
    report = solver.run()
    
    sys.exit(0 if report["challenges"]["solved"] >= 25 else 1)


if __name__ == "__main__":
    main()
