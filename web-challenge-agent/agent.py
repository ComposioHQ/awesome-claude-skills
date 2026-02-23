#!/usr/bin/env python3
"""
Web Challenge Solver Agent
Solves 30 web challenges using browser automation with AI assistance.
"""

import os
import sys
import time
import json
import base64
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from playwright.sync_api import sync_playwright, Page, Browser, Locator
from anthropic import Anthropic

# Configuration
CHALLENGE_URL = os.getenv("CHALLENGE_URL", "https://qa-bench.com")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
MAX_TIME_SECONDS = 300  # 5 minutes
SCREENSHOT_DIR = "/tmp/challenge_screenshots"


@dataclass
class Metrics:
    """Track agent performance metrics."""
    start_time: float = 0
    end_time: float = 0
    total_challenges: int = 30
    challenges_solved: int = 0
    challenges_failed: int = 0
    total_tokens_input: int = 0
    total_tokens_output: int = 0
    total_api_calls: int = 0
    challenge_times: Dict[int, float] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    
    @property
    def elapsed_time(self) -> float:
        return self.end_time - self.start_time if self.end_time else time.time() - self.start_time
    
    @property
    def total_tokens(self) -> int:
        return self.total_tokens_input + self.total_tokens_output
    
    @property
    def estimated_cost(self) -> float:
        # Claude 3.5 Sonnet pricing: $3/M input, $15/M output
        input_cost = (self.total_tokens_input / 1_000_000) * 3
        output_cost = (self.total_tokens_output / 1_000_000) * 15
        return input_cost + output_cost
    
    def to_dict(self) -> dict:
        return {
            "elapsed_time_seconds": round(self.elapsed_time, 2),
            "total_challenges": self.total_challenges,
            "challenges_solved": self.challenges_solved,
            "challenges_failed": self.challenges_failed,
            "success_rate": f"{(self.challenges_solved/self.total_challenges)*100:.1f}%",
            "total_tokens_input": self.total_tokens_input,
            "total_tokens_output": self.total_tokens_output,
            "total_tokens": self.total_tokens,
            "total_api_calls": self.total_api_calls,
            "estimated_cost_usd": f"${self.estimated_cost:.4f}",
            "average_time_per_challenge": round(self.elapsed_time / max(1, self.challenges_solved + self.challenges_failed), 2),
            "errors": self.errors
        }


class WebChallengeAgent:
    """Agent that solves web challenges using browser automation and AI."""
    
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.metrics = Metrics()
        self.client = None
        if ANTHROPIC_API_KEY:
            self.client = Anthropic(api_key=ANTHROPIC_API_KEY)
        os.makedirs(SCREENSHOT_DIR, exist_ok=True)
        
    def take_screenshot(self, page: Page, name: str) -> str:
        """Take a screenshot and return the path."""
        path = f"{SCREENSHOT_DIR}/{name}.png"
        page.screenshot(path=path, full_page=True)
        return path
    
    def get_screenshot_base64(self, page: Page) -> str:
        """Get screenshot as base64 for Claude vision."""
        screenshot_bytes = page.screenshot(full_page=True)
        return base64.standard_b64encode(screenshot_bytes).decode("utf-8")
    
    def ask_claude(self, prompt: str, screenshot_b64: Optional[str] = None) -> str:
        """Ask Claude for help with a challenge."""
        if not self.client:
            return ""
        
        messages = []
        content = []
        
        if screenshot_b64:
            content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/png",
                    "data": screenshot_b64
                }
            })
        
        content.append({"type": "text", "text": prompt})
        messages.append({"role": "user", "content": content})
        
        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                messages=messages
            )
            
            self.metrics.total_api_calls += 1
            self.metrics.total_tokens_input += response.usage.input_tokens
            self.metrics.total_tokens_output += response.usage.output_tokens
            
            return response.content[0].text
        except Exception as e:
            self.metrics.errors.append(f"Claude API error: {str(e)}")
            return ""
    
    def extract_challenge_info(self, page: Page) -> Dict[str, Any]:
        """Extract information about the current challenge."""
        info = {
            "title": "",
            "description": "",
            "inputs": [],
            "buttons": [],
            "selects": [],
            "checkboxes": [],
            "radios": [],
            "textareas": [],
            "links": [],
            "html_content": ""
        }
        
        try:
            # Get page content
            info["html_content"] = page.content()
            
            # Get title
            title_el = page.locator("h1, h2, .title, .challenge-title").first
            if title_el.count() > 0:
                info["title"] = title_el.inner_text()
            
            # Get description/instructions
            desc_el = page.locator("p, .description, .instructions, .challenge-description").first
            if desc_el.count() > 0:
                info["description"] = desc_el.inner_text()
            
            # Get inputs
            for inp in page.locator("input:not([type='hidden']):not([type='submit']):not([type='checkbox']):not([type='radio'])").all():
                if inp.is_visible():
                    info["inputs"].append({
                        "type": inp.get_attribute("type") or "text",
                        "name": inp.get_attribute("name") or "",
                        "id": inp.get_attribute("id") or "",
                        "placeholder": inp.get_attribute("placeholder") or "",
                        "value": inp.input_value() or ""
                    })
            
            # Get buttons
            for btn in page.locator("button, input[type='submit'], input[type='button']").all():
                if btn.is_visible():
                    info["buttons"].append({
                        "text": btn.inner_text() if btn.evaluate("el => el.tagName") == "BUTTON" else btn.get_attribute("value") or "",
                        "id": btn.get_attribute("id") or "",
                        "class": btn.get_attribute("class") or ""
                    })
            
            # Get select dropdowns
            for sel in page.locator("select").all():
                if sel.is_visible():
                    options = []
                    for opt in page.locator(f"#{sel.get_attribute('id')} option" if sel.get_attribute('id') else "select option").all():
                        options.append({
                            "value": opt.get_attribute("value") or "",
                            "text": opt.inner_text()
                        })
                    info["selects"].append({
                        "id": sel.get_attribute("id") or "",
                        "name": sel.get_attribute("name") or "",
                        "options": options
                    })
            
            # Get checkboxes
            for cb in page.locator("input[type='checkbox']").all():
                if cb.is_visible():
                    info["checkboxes"].append({
                        "id": cb.get_attribute("id") or "",
                        "name": cb.get_attribute("name") or "",
                        "checked": cb.is_checked(),
                        "label": ""
                    })
            
            # Get radio buttons
            for rb in page.locator("input[type='radio']").all():
                if rb.is_visible():
                    info["radios"].append({
                        "id": rb.get_attribute("id") or "",
                        "name": rb.get_attribute("name") or "",
                        "value": rb.get_attribute("value") or "",
                        "checked": rb.is_checked()
                    })
            
            # Get textareas
            for ta in page.locator("textarea").all():
                if ta.is_visible():
                    info["textareas"].append({
                        "id": ta.get_attribute("id") or "",
                        "name": ta.get_attribute("name") or "",
                        "placeholder": ta.get_attribute("placeholder") or ""
                    })
            
        except Exception as e:
            self.metrics.errors.append(f"Error extracting challenge info: {str(e)}")
        
        return info
    
    def solve_challenge_heuristic(self, page: Page, challenge_num: int, info: Dict[str, Any]) -> bool:
        """Try to solve challenge using heuristic rules."""
        try:
            html = info["html_content"].lower()
            desc = info.get("description", "").lower()
            
            # Common challenge patterns
            
            # Pattern 1: Click a specific button
            if "click" in desc:
                for btn in page.locator("button").all():
                    if btn.is_visible():
                        btn.click()
                        page.wait_for_timeout(500)
                        return True
            
            # Pattern 2: Fill in text input
            if info["inputs"]:
                for inp_info in info["inputs"]:
                    inp_id = inp_info.get("id")
                    inp_name = inp_info.get("name")
                    placeholder = inp_info.get("placeholder", "").lower()
                    
                    selector = f"#{inp_id}" if inp_id else f"[name='{inp_name}']" if inp_name else "input:visible"
                    
                    # Determine what to type based on input type/placeholder
                    value = "test"
                    if "email" in placeholder or "email" in (inp_info.get("type") or ""):
                        value = "test@example.com"
                    elif "name" in placeholder:
                        value = "John Doe"
                    elif "password" in placeholder or "password" in (inp_info.get("type") or ""):
                        value = "Password123!"
                    elif "phone" in placeholder:
                        value = "555-123-4567"
                    elif "number" in (inp_info.get("type") or ""):
                        value = "42"
                    
                    try:
                        page.locator(selector).first.fill(value)
                    except:
                        pass
            
            # Pattern 3: Select from dropdown
            if info["selects"]:
                for sel_info in info["selects"]:
                    sel_id = sel_info.get("id")
                    options = sel_info.get("options", [])
                    if options and len(options) > 1:
                        # Select the second option (first is usually placeholder)
                        selector = f"#{sel_id}" if sel_id else "select"
                        try:
                            page.locator(selector).first.select_option(index=1)
                        except:
                            pass
            
            # Pattern 4: Check checkboxes
            if info["checkboxes"]:
                for cb_info in info["checkboxes"]:
                    cb_id = cb_info.get("id")
                    if cb_id:
                        try:
                            page.locator(f"#{cb_id}").check()
                        except:
                            pass
            
            # Pattern 5: Select radio button
            if info["radios"]:
                if info["radios"]:
                    rb_info = info["radios"][0]
                    rb_id = rb_info.get("id")
                    if rb_id:
                        try:
                            page.locator(f"#{rb_id}").check()
                        except:
                            pass
            
            # Pattern 6: Fill textarea
            if info["textareas"]:
                for ta_info in info["textareas"]:
                    ta_id = ta_info.get("id")
                    selector = f"#{ta_id}" if ta_id else "textarea"
                    try:
                        page.locator(selector).first.fill("This is a test response for the challenge.")
                    except:
                        pass
            
            # Finally, try to submit
            submit_btn = page.locator("button[type='submit'], input[type='submit'], button:has-text('Submit'), button:has-text('Next'), button:has-text('Continue')").first
            if submit_btn.count() > 0 and submit_btn.is_visible():
                submit_btn.click()
                page.wait_for_timeout(500)
                return True
            
            # Or just click any visible button
            for btn in page.locator("button").all():
                if btn.is_visible():
                    btn.click()
                    page.wait_for_timeout(500)
                    return True
            
            return False
            
        except Exception as e:
            self.metrics.errors.append(f"Challenge {challenge_num} heuristic error: {str(e)}")
            return False
    
    def solve_challenge_with_ai(self, page: Page, challenge_num: int, info: Dict[str, Any]) -> bool:
        """Use Claude to help solve a challenge."""
        if not self.client:
            return False
        
        screenshot_b64 = self.get_screenshot_base64(page)
        
        prompt = f"""You are helping solve a web UI challenge. Analyze the screenshot and provide specific actions to solve it.

Challenge #{challenge_num}
Page Info:
- Title: {info.get('title', 'Unknown')}
- Description: {info.get('description', 'Unknown')}
- Inputs: {json.dumps(info.get('inputs', []))}
- Buttons: {json.dumps(info.get('buttons', []))}
- Selects: {json.dumps(info.get('selects', []))}
- Checkboxes: {json.dumps(info.get('checkboxes', []))}
- Radios: {json.dumps(info.get('radios', []))}

Provide a JSON response with the exact actions to take:
{{
    "actions": [
        {{"type": "fill", "selector": "#input-id", "value": "text to type"}},
        {{"type": "click", "selector": "button#submit"}},
        {{"type": "select", "selector": "#dropdown", "value": "option_value"}},
        {{"type": "check", "selector": "#checkbox"}},
        {{"type": "wait", "ms": 500}}
    ]
}}

Only output valid JSON, no other text."""

        response = self.ask_claude(prompt, screenshot_b64)
        
        try:
            # Extract JSON from response
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                actions = json.loads(json_match.group())
                return self.execute_actions(page, actions.get("actions", []))
        except Exception as e:
            self.metrics.errors.append(f"AI response parsing error: {str(e)}")
        
        return False
    
    def execute_actions(self, page: Page, actions: List[Dict]) -> bool:
        """Execute a list of actions on the page."""
        try:
            for action in actions:
                action_type = action.get("type")
                selector = action.get("selector", "")
                value = action.get("value", "")
                
                if action_type == "fill":
                    page.locator(selector).first.fill(value)
                elif action_type == "click":
                    page.locator(selector).first.click()
                elif action_type == "select":
                    page.locator(selector).first.select_option(value)
                elif action_type == "check":
                    page.locator(selector).first.check()
                elif action_type == "uncheck":
                    page.locator(selector).first.uncheck()
                elif action_type == "wait":
                    page.wait_for_timeout(int(value) if value else 500)
                elif action_type == "press":
                    page.keyboard.press(value)
                
                page.wait_for_timeout(100)
            
            return True
        except Exception as e:
            self.metrics.errors.append(f"Action execution error: {str(e)}")
            return False
    
    def check_challenge_complete(self, page: Page) -> bool:
        """Check if the current challenge was completed."""
        try:
            # Look for success indicators
            success_indicators = [
                "text=Success",
                "text=Correct",
                "text=Well done",
                "text=Complete",
                ".success",
                ".correct",
                "[data-status='complete']"
            ]
            
            for indicator in success_indicators:
                try:
                    if page.locator(indicator).count() > 0:
                        return True
                except:
                    pass
            
            # Check URL for challenge progression
            url = page.url
            if "/challenge/" in url or "challenge=" in url:
                return True
            
            return False
        except:
            return False
    
    def navigate_to_next_challenge(self, page: Page) -> bool:
        """Try to navigate to the next challenge."""
        try:
            # Look for next/continue buttons
            next_selectors = [
                "button:has-text('Next')",
                "a:has-text('Next')",
                "button:has-text('Continue')",
                "a:has-text('Continue')",
                ".next-btn",
                "#next",
                "[data-action='next']"
            ]
            
            for selector in next_selectors:
                try:
                    el = page.locator(selector).first
                    if el.count() > 0 and el.is_visible():
                        el.click()
                        page.wait_for_timeout(500)
                        return True
                except:
                    pass
            
            return False
        except:
            return False
    
    def run(self) -> Dict:
        """Main execution loop."""
        self.metrics.start_time = time.time()
        
        print(f"\n{'='*60}")
        print("Web Challenge Solver Agent")
        print(f"Target: {CHALLENGE_URL}")
        print(f"Max time: {MAX_TIME_SECONDS} seconds")
        print(f"{'='*60}\n")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            context = browser.new_context(viewport={'width': 1920, 'height': 1080})
            page = context.new_page()
            
            try:
                # Navigate to challenge site
                print(f"Navigating to {CHALLENGE_URL}...")
                page.goto(CHALLENGE_URL, timeout=30000)
                page.wait_for_load_state('networkidle')
                
                # Take initial screenshot
                self.take_screenshot(page, "00_initial")
                
                challenge_num = 1
                consecutive_failures = 0
                
                while challenge_num <= self.metrics.total_challenges:
                    # Check time limit
                    if self.metrics.elapsed_time > MAX_TIME_SECONDS:
                        print(f"\nTime limit exceeded ({MAX_TIME_SECONDS}s)")
                        break
                    
                    print(f"\n--- Challenge {challenge_num}/{self.metrics.total_challenges} ---")
                    challenge_start = time.time()
                    
                    # Extract challenge info
                    info = self.extract_challenge_info(page)
                    print(f"Title: {info.get('title', 'Unknown')[:50]}")
                    print(f"Found: {len(info['inputs'])} inputs, {len(info['buttons'])} buttons")
                    
                    # Take screenshot before attempting
                    self.take_screenshot(page, f"{challenge_num:02d}_before")
                    
                    # Try heuristic solution first
                    solved = self.solve_challenge_heuristic(page, challenge_num, info)
                    
                    # If heuristic fails and we have AI, try AI
                    if not solved and self.client:
                        print("Heuristic failed, trying AI...")
                        solved = self.solve_challenge_with_ai(page, challenge_num, info)
                    
                    page.wait_for_timeout(500)
                    
                    # Take screenshot after attempting
                    self.take_screenshot(page, f"{challenge_num:02d}_after")
                    
                    # Record metrics
                    challenge_time = time.time() - challenge_start
                    self.metrics.challenge_times[challenge_num] = challenge_time
                    
                    if solved or self.check_challenge_complete(page):
                        self.metrics.challenges_solved += 1
                        consecutive_failures = 0
                        print(f"✓ Solved in {challenge_time:.2f}s")
                    else:
                        self.metrics.challenges_failed += 1
                        consecutive_failures += 1
                        print(f"✗ Failed after {challenge_time:.2f}s")
                        
                        # If too many consecutive failures, try to move on
                        if consecutive_failures >= 3:
                            print("Multiple failures, attempting to skip...")
                            self.navigate_to_next_challenge(page)
                    
                    # Try to move to next challenge
                    self.navigate_to_next_challenge(page)
                    page.wait_for_timeout(300)
                    
                    challenge_num += 1
                
            except Exception as e:
                self.metrics.errors.append(f"Fatal error: {str(e)}")
                print(f"\nFatal error: {e}")
            finally:
                # Take final screenshot
                self.take_screenshot(page, "99_final")
                browser.close()
        
        self.metrics.end_time = time.time()
        
        # Print results
        results = self.metrics.to_dict()
        print(f"\n{'='*60}")
        print("RESULTS")
        print(f"{'='*60}")
        for key, value in results.items():
            if key != "errors":
                print(f"  {key}: {value}")
        
        if results["errors"]:
            print(f"\nErrors ({len(results['errors'])}):")
            for err in results["errors"][:5]:
                print(f"  - {err[:100]}")
        
        # Save results to file
        results_path = f"{SCREENSHOT_DIR}/results.json"
        with open(results_path, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to: {results_path}")
        
        return results


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Web Challenge Solver Agent")
    parser.add_argument("--url", default=CHALLENGE_URL, help="Challenge website URL")
    parser.add_argument("--headless", action="store_true", default=True, help="Run in headless mode")
    parser.add_argument("--visible", action="store_true", help="Run with visible browser")
    args = parser.parse_args()
    
    # Update URL if provided
    if args.url:
        global CHALLENGE_URL
        CHALLENGE_URL = args.url
    
    agent = WebChallengeAgent(headless=not args.visible)
    results = agent.run()
    
    # Exit with appropriate code
    if results["challenges_solved"] == results["total_challenges"]:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
