#!/usr/bin/env python3
"""
Smart Browser Navigation Challenge Solver
Reads and executes specific challenge instructions.
Target: https://serene-frangipane-7fd25b.netlify.app/
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
from playwright.sync_api import sync_playwright, Page, Browser

# Configuration
CHALLENGE_URL = os.getenv("CHALLENGE_URL", "https://serene-frangipane-7fd25b.netlify.app/")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
MAX_TIME_SECONDS = 300
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "/tmp/smart_solver_results")


@dataclass
class Metrics:
    run_id: str = ""
    start_time: float = 0
    end_time: float = 0
    total_challenges: int = 30
    challenges_solved: int = 0
    challenges_failed: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    api_calls: int = 0
    details: Dict[int, Dict] = field(default_factory=dict)
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
                "failed": self.challenges_failed,
                "success_rate": f"{(self.challenges_solved / max(1, self.challenges_solved + self.challenges_failed)) * 100:.1f}%"
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


class SmartSolver:
    """Intelligent solver that reads and follows challenge instructions."""
    
    def __init__(self, headless: bool = True, use_ai: bool = True):
        self.headless = headless
        self.use_ai = use_ai and bool(ANTHROPIC_API_KEY)
        self.metrics = Metrics(run_id=datetime.now().strftime("%Y%m%d_%H%M%S"))
        self.client = None
        if self.use_ai:
            from anthropic import Anthropic
            self.client = Anthropic(api_key=ANTHROPIC_API_KEY)
        os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    def log(self, msg: str, level: str = "INFO"):
        elapsed = self.metrics.elapsed
        symbols = {"INFO": "  ", "OK": "✓ ", "FAIL": "✗ ", "WARN": "! "}
        print(f"[{elapsed:5.1f}s] {symbols.get(level, '  ')}{msg}")
    
    def screenshot(self, page: Page, name: str):
        try:
            page.screenshot(path=os.path.join(OUTPUT_DIR, f"{name}.png"), full_page=True, timeout=3000)
        except:
            pass
    
    def get_step_number(self, page: Page) -> int:
        """Extract current step number from page."""
        try:
            text = page.inner_text("body", timeout=1000)
            match = re.search(r'Step\s*(\d+)\s*(?:of|/)\s*\d+', text, re.IGNORECASE)
            if match:
                return int(match.group(1))
        except:
            pass
        return 0
    
    def get_challenge_instruction(self, page: Page) -> str:
        """Extract the current challenge instruction."""
        instruction = ""
        
        # Try modal/popup content first
        modal_selectors = [
            ".modal-content", ".modal-body", ".dialog-content",
            ".popup-content", ".challenge-modal", ".instruction-modal",
            "[role='dialog']", ".modal"
        ]
        
        for sel in modal_selectors:
            try:
                el = page.locator(sel).first
                if el.count() > 0 and el.is_visible():
                    instruction = el.inner_text(timeout=1000).strip()
                    if instruction and len(instruction) > 10:
                        return instruction
            except:
                pass
        
        # Try instruction-like elements
        instruction_selectors = [
            ".instruction", ".challenge-instruction", ".task",
            ".step-instruction", ".prompt", "h2", "h3",
            "p:has-text('Click')", "p:has-text('Find')",
            "p:has-text('Select')", "p:has-text('Enter')"
        ]
        
        for sel in instruction_selectors:
            try:
                el = page.locator(sel).first
                if el.count() > 0 and el.is_visible():
                    text = el.inner_text(timeout=500).strip()
                    if text and len(text) > 5 and len(text) < 500:
                        return text
            except:
                pass
        
        # Get any visible text that looks like an instruction
        try:
            body_text = page.inner_text("body", timeout=1000)
            lines = body_text.split('\n')
            for line in lines:
                line = line.strip()
                if len(line) > 10 and len(line) < 200:
                    if any(word in line.lower() for word in ['click', 'find', 'enter', 'select', 'hover', 'scroll', 'drag', 'type', 'navigate']):
                        return line
        except:
            pass
        
        return instruction
    
    def parse_instruction(self, instruction: str) -> Dict[str, Any]:
        """Parse instruction to determine required action."""
        instruction_lower = instruction.lower()
        
        result = {
            "action": "click",
            "target_type": "button",
            "target_text": "",
            "target_number": None,
            "section_number": None,
            "input_value": "",
            "raw": instruction
        }
        
        # Extract section number
        section_match = re.search(r'section\s*(\d+)', instruction_lower)
        if section_match:
            result["section_number"] = int(section_match.group(1))
        
        # Extract button/link number
        num_match = re.search(r'(?:button|link|item|option)\s*(\d+)', instruction_lower)
        if num_match:
            result["target_number"] = int(num_match.group(1))
        
        # Determine action type
        if 'hover' in instruction_lower:
            result["action"] = "hover"
        elif 'double' in instruction_lower and 'click' in instruction_lower:
            result["action"] = "dblclick"
        elif 'right' in instruction_lower and 'click' in instruction_lower:
            result["action"] = "rightclick"
        elif 'drag' in instruction_lower:
            result["action"] = "drag"
        elif 'scroll' in instruction_lower:
            result["action"] = "scroll"
        elif 'type' in instruction_lower or 'enter' in instruction_lower or 'fill' in instruction_lower:
            result["action"] = "fill"
            # Extract what to type
            type_match = re.search(r'(?:type|enter|fill)[:\s]+["\']?([^"\']+)["\']?', instruction_lower)
            if type_match:
                result["input_value"] = type_match.group(1).strip()
        elif 'select' in instruction_lower:
            result["action"] = "select"
        elif 'check' in instruction_lower:
            result["action"] = "check"
        
        # Determine target type
        if 'link' in instruction_lower:
            result["target_type"] = "link"
        elif 'input' in instruction_lower or 'field' in instruction_lower:
            result["target_type"] = "input"
        elif 'dropdown' in instruction_lower or 'select' in instruction_lower:
            result["target_type"] = "select"
        elif 'checkbox' in instruction_lower:
            result["target_type"] = "checkbox"
        elif 'radio' in instruction_lower:
            result["target_type"] = "radio"
        
        # Extract target text (text in quotes or specific words)
        text_match = re.search(r'["\']([^"\']+)["\']', instruction)
        if text_match:
            result["target_text"] = text_match.group(1)
        
        return result
    
    def execute_action(self, page: Page, parsed: Dict[str, Any]) -> bool:
        """Execute the parsed action."""
        action = parsed["action"]
        section_num = parsed.get("section_number")
        target_num = parsed.get("target_number")
        target_text = parsed.get("target_text")
        target_type = parsed.get("target_type")
        input_value = parsed.get("input_value", "test")
        
        try:
            # If section specified, scroll to it first
            if section_num:
                section_sel = f"text=Section {section_num}"
                try:
                    section = page.locator(section_sel).first
                    if section.count() > 0:
                        section.scroll_into_view_if_needed(timeout=2000)
                        page.wait_for_timeout(200)
                except:
                    pass
            
            # Build selector based on target
            selectors = []
            
            if target_text:
                selectors.append(f"text={target_text}")
                selectors.append(f"button:has-text('{target_text}')")
                selectors.append(f"a:has-text('{target_text}')")
            
            if target_type == "button":
                if target_num:
                    selectors.append(f"button >> nth={target_num - 1}")
                selectors.append("button:visible")
            elif target_type == "link":
                if target_num:
                    selectors.append(f"a >> nth={target_num - 1}")
                selectors.append("a:visible")
            elif target_type == "input":
                selectors.append("input:visible:not([type='hidden'])")
            elif target_type == "select":
                selectors.append("select:visible")
            elif target_type == "checkbox":
                selectors.append("input[type='checkbox']:visible")
            elif target_type == "radio":
                selectors.append("input[type='radio']:visible")
            
            # Add generic selectors as fallback
            selectors.extend([
                "button:visible",
                ".btn:visible",
                "[role='button']:visible"
            ])
            
            # Execute action
            for sel in selectors:
                try:
                    el = page.locator(sel).first
                    if el.count() > 0 and el.is_visible():
                        if action == "click":
                            el.click(timeout=2000)
                        elif action == "hover":
                            el.hover(timeout=2000)
                        elif action == "dblclick":
                            el.dblclick(timeout=2000)
                        elif action == "rightclick":
                            el.click(button="right", timeout=2000)
                        elif action == "fill":
                            el.fill(input_value or "test", timeout=2000)
                        elif action == "select":
                            el.select_option(index=1, timeout=2000)
                        elif action == "check":
                            el.check(timeout=2000)
                        elif action == "scroll":
                            el.scroll_into_view_if_needed(timeout=2000)
                        
                        return True
                except:
                    continue
            
            # Special handling for scroll action
            if action == "scroll":
                page.evaluate("window.scrollBy(0, 500)")
                return True
            
            # Special handling for drag
            if action == "drag":
                try:
                    draggable = page.locator("[draggable='true'], .draggable").first
                    droppable = page.locator(".droppable, .drop-zone").first
                    if draggable.count() > 0 and droppable.count() > 0:
                        draggable.drag_to(droppable, timeout=3000)
                        return True
                except:
                    pass
            
            return False
            
        except Exception as e:
            self.metrics.errors.append(f"Action error: {str(e)}")
            return False
    
    def solve_with_ai(self, page: Page, step: int) -> bool:
        """Use Claude to solve the challenge."""
        if not self.client:
            return False
        
        try:
            screenshot = base64.standard_b64encode(
                page.screenshot(full_page=True, timeout=5000)
            ).decode("utf-8")
            
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=512,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {"type": "base64", "media_type": "image/png", "data": screenshot}
                        },
                        {
                            "type": "text",
                            "text": f"""This is step {step} of a Browser Navigation Challenge. 
Look at the screenshot carefully and identify what action needs to be performed.

Return ONLY a JSON object with these fields:
{{"action": "click|fill|select|hover|scroll|dblclick", "selector": "CSS selector or text=Text", "value": "optional value for fill/select"}}

Be specific with the selector. Look for the main instruction on the page and determine what element to interact with.
Only return valid JSON."""
                        }
                    ]
                }]
            )
            
            self.metrics.api_calls += 1
            self.metrics.input_tokens += response.usage.input_tokens
            self.metrics.output_tokens += response.usage.output_tokens
            
            text = response.content[0].text
            match = re.search(r'\{[^}]+\}', text)
            if match:
                data = json.loads(match.group())
                sel = data.get("selector", "")
                action = data.get("action", "click")
                value = data.get("value", "")
                
                el = page.locator(sel).first
                if el.count() > 0:
                    if action == "click":
                        el.click(timeout=2000)
                    elif action == "fill":
                        el.fill(value or "test", timeout=2000)
                    elif action == "select":
                        el.select_option(value, timeout=2000)
                    elif action == "hover":
                        el.hover(timeout=2000)
                    elif action == "dblclick":
                        el.dblclick(timeout=2000)
                    return True
                    
        except Exception as e:
            self.metrics.errors.append(f"AI error: {str(e)}")
        
        return False
    
    def try_common_actions(self, page: Page) -> bool:
        """Try common actions that often work."""
        # Click any "Next" or "Continue" button
        for text in ["Next", "Continue", "Submit", "OK", "Done", "Go", "Start"]:
            try:
                btn = page.locator(f"button:has-text('{text}')").first
                if btn.count() > 0 and btn.is_visible():
                    btn.click(timeout=1000)
                    return True
            except:
                pass
        
        # Click first visible button in a modal
        try:
            modal_btn = page.locator(".modal button:visible, [role='dialog'] button:visible").first
            if modal_btn.count() > 0:
                modal_btn.click(timeout=1000)
                return True
        except:
            pass
        
        # Fill any empty input
        try:
            inp = page.locator("input:visible:not([type='hidden']):not([type='submit'])").first
            if inp.count() > 0 and inp.is_visible() and not inp.input_value():
                inp.fill("test@example.com", timeout=1000)
                return True
        except:
            pass
        
        return False
    
    def run(self) -> Dict:
        """Main execution."""
        self.metrics.start_time = time.time()
        
        print("\n" + "=" * 60)
        print("Smart Browser Navigation Solver")
        print(f"URL: {CHALLENGE_URL}")
        print(f"AI: {self.use_ai}")
        print("=" * 60 + "\n")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=self.headless,
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )
            context = browser.new_context(viewport={'width': 1280, 'height': 720})
            page = context.new_page()
            page.on("dialog", lambda d: d.accept())
            
            try:
                self.log(f"Loading {CHALLENGE_URL}")
                page.goto(CHALLENGE_URL, timeout=30000)
                page.wait_for_load_state('networkidle', timeout=10000)
                
                self.screenshot(page, "00_start")
                
                # Click START
                try:
                    start = page.locator("text=START").first
                    if start.count() > 0:
                        start.click(timeout=3000)
                        self.log("Started challenge", "OK")
                        page.wait_for_timeout(1000)
                except:
                    pass
                
                last_step = 0
                step = 1
                attempts = 0
                max_attempts_per_step = 5
                
                while step <= self.metrics.total_challenges:
                    if self.metrics.elapsed > MAX_TIME_SECONDS:
                        self.log("TIME LIMIT!", "WARN")
                        break
                    
                    current_step = self.get_step_number(page)
                    if current_step > 0:
                        if current_step > step:
                            # Progressed!
                            self.metrics.challenges_solved += (current_step - step)
                            self.log(f"Advanced to step {current_step}", "OK")
                            step = current_step
                            attempts = 0
                        elif current_step == last_step and attempts >= max_attempts_per_step:
                            self.log(f"Stuck on step {step}, skipping", "WARN")
                            self.metrics.challenges_failed += 1
                            step += 1
                            attempts = 0
                            continue
                    
                    last_step = current_step
                    
                    self.log(f"Step {step}/30 (attempt {attempts + 1})")
                    self.screenshot(page, f"{step:02d}_{attempts}_before")
                    
                    start_time = time.time()
                    
                    # Get and parse instruction
                    instruction = self.get_challenge_instruction(page)
                    if instruction:
                        self.log(f"  Instruction: {instruction[:60]}...")
                        parsed = self.parse_instruction(instruction)
                        
                        # Execute parsed action
                        success = self.execute_action(page, parsed)
                        if success:
                            self.log("  Action executed", "OK")
                    else:
                        self.log("  No instruction found", "WARN")
                        success = self.try_common_actions(page)
                    
                    page.wait_for_timeout(500)
                    
                    # If heuristics failed, try AI
                    if not success and self.use_ai and attempts >= 2:
                        self.log("  Using AI...", "INFO")
                        success = self.solve_with_ai(page, step)
                    
                    # Try common actions as fallback
                    if not success:
                        success = self.try_common_actions(page)
                    
                    page.wait_for_timeout(300)
                    self.screenshot(page, f"{step:02d}_{attempts}_after")
                    
                    # Check if we advanced
                    new_step = self.get_step_number(page)
                    if new_step > step:
                        self.metrics.challenges_solved += (new_step - step)
                        elapsed = time.time() - start_time
                        self.log(f"  Completed in {elapsed:.2f}s", "OK")
                        step = new_step
                        attempts = 0
                    else:
                        attempts += 1
                        if attempts >= max_attempts_per_step:
                            self.metrics.challenges_failed += 1
                            self.log(f"  Failed after {max_attempts_per_step} attempts", "FAIL")
                            step += 1
                            attempts = 0
                
            except Exception as e:
                self.metrics.errors.append(f"Fatal: {str(e)}")
                self.log(f"Fatal: {e}", "FAIL")
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
        print(f"Solved: {report['challenges']['solved']}/{report['challenges']['total']}")
        print(f"Success Rate: {report['challenges']['success_rate']}")
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
    parser.add_argument("--no-ai", action="store_true")
    args = parser.parse_args()
    
    if args.url:
        CHALLENGE_URL = args.url
    if args.output:
        OUTPUT_DIR = args.output
    
    solver = SmartSolver(headless=not args.visible, use_ai=not args.no_ai)
    report = solver.run()
    
    sys.exit(0 if report["challenges"]["solved"] >= 27 else 1)


if __name__ == "__main__":
    main()
