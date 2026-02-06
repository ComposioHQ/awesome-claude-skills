"""
solver.py - Per-challenge solver with anti-loop mechanisms
"""

import asyncio
import time
import re
from typing import Dict, Any, Optional, Set
from dataclasses import dataclass, field

from browser import BrowserController
from llm_client import LLMClient


def extract_code_from_text(text: str) -> Optional[str]:
    """Try to extract a 6-character code from text"""
    # Skip common English words and measurement patterns
    skip_words = {
        'button', 'scroll', 'window', 'screen', 'number', 'string', 'submit', 'reveal',
        'hidden', 'secret', 'answer', 'please', 'should', 'cannot', 'object', 'before',
        'loaded', 'appear', 'unique', 'random', 'update', 'return', 'result', 'format',
        'normal', 'simple', 'double', 'single', 'change', 'select', 'option', 'middle',
        'center', 'bottom', 'yellow', 'purple', 'orange', 'border', 'shadow', 'height',
        'length', 'inside', 'output', 'source', 'target', 'before', 'status', 'cookie',
        'accept', 'signup', 'labels', 'forward', 'block1', 'block2', 'block3', 'content'
    }
    
    # Skip patterns that look like measurements (e.g., "3308px", "1500ms")
    skip_patterns = [
        r'\d+px',  # pixels
        r'\d+ms',  # milliseconds
        r'\d+em',  # em units
        r'\d+rem', # rem units
    ]
    
    # Look for explicit code patterns first (standalone on their own line or after colon)
    patterns = [
        r'(?:^|\n)\s*([A-Z0-9]{6})\s*(?:\n|$)',  # Standalone on a line
        r'code[:\s]+([A-Za-z0-9]{6})\b',
        r'answer[:\s]+([A-Za-z0-9]{6})\b',
        r'(?:the |your )?code is[:\s]+([A-Za-z0-9]{6})\b',
        r'revealed[:\s]*([A-Za-z0-9]{6})\b',
        r'secret[:\s]+([A-Za-z0-9]{6})\b',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            code = match.group(1)
            if code.lower() not in skip_words:
                # Check if it matches a skip pattern
                is_skip = False
                for sp in skip_patterns:
                    if re.match(sp, code, re.IGNORECASE):
                        is_skip = True
                        break
                if not is_skip:
                    return code.upper()
    
    # Look for codes with BOTH letters and numbers (more likely to be real codes)
    # But skip anything that ends with px, ms, etc.
    codes = re.findall(r'\b([A-Za-z0-9]{6})\b', text)
    for code in codes:
        if code.lower() not in skip_words:
            # Skip measurement patterns
            if code.lower().endswith(('px', 'ms', 'em', 'pt', 'vh', 'vw')):
                continue
            # Skip if all digits (likely a measurement or timestamp)
            if code.isdigit():
                continue
            has_letter = re.search(r'[A-Za-z]', code)
            has_number = re.search(r'[0-9]', code)
            if has_letter and has_number:
                return code.upper()
    
    return None


@dataclass
class SolveResult:
    """Result of solving a challenge"""
    success: bool = False
    answer_submitted: Optional[str] = None
    attempts: int = 0
    time_seconds: float = 0.0
    error: Optional[str] = None
    tried_answers: Set[str] = field(default_factory=set)
    

class ChallengeSolver:
    """Solves individual challenges with 3-attempt escalation strategy"""
    
    MAX_ATTEMPTS = 3
    PER_CHALLENGE_TIMEOUT = 25  # seconds
    
    def __init__(self, browser: BrowserController, llm: LLMClient, verbose: bool = True):
        self.browser = browser
        self.llm = llm
        self.verbose = verbose
        
    def log(self, msg: str):
        if self.verbose:
            print(f"  [Solver] {msg}")
            
    async def solve(self, challenge_url: str, challenge_number: int = None,
                   timeout: float = None, is_spa: bool = False) -> SolveResult:
        """
        Solve a single challenge with escalating strategy:
        - Attempt 1: Text extraction → LLM → submit
        - Attempt 2: Interactions → re-extract → LLM → submit  
        - Attempt 3: Screenshot → vision LLM → submit
        """
        
        timeout = timeout or self.PER_CHALLENGE_TIMEOUT
        start_time = time.time()
        result = SolveResult()
        
        try:
            # For SPA mode, we stay on the current page - route discovery already put us there
            if is_spa:
                # Just check current state, don't navigate
                current_url = await self.browser.get_current_url()
                self.log(f"SPA mode - URL: {current_url[:60]}...")
                
                # Small delay if not first challenge (for page transition)
                if challenge_number > 1:
                    await asyncio.sleep(0.3)
            else:
                # Standard navigation to specific challenge URL
                current_url = await self.browser.get_current_url()
                if challenge_url not in current_url:
                    await self.browser.navigate(challenge_url)
            
            for attempt in range(1, self.MAX_ATTEMPTS + 1):
                # Check timeout
                elapsed = time.time() - start_time
                if elapsed > timeout:
                    result.error = "Timeout"
                    break
                    
                result.attempts = attempt
                self.log(f"Attempt {attempt}/{self.MAX_ATTEMPTS}")
                
                # Go directly to interactions - text extraction alone never works
                if attempt == 1:
                    solution = await self._attempt_with_interactions(
                        challenge_number, result.tried_answers
                    )
                elif attempt == 2:
                    solution = await self._attempt_with_vision(
                        challenge_number, result.tried_answers
                    )
                else:
                    # Third attempt: try interactions again with more aggressive approach
                    solution = await self._attempt_with_interactions(
                        challenge_number, result.tried_answers
                    )
                    
                # Check if we got an answer
                if not solution or not solution.get('answer'):
                    self.log("No answer found")
                    # DON'T reload page - it can cause 404 in SPA mode
                    continue
                    
                answer = str(solution['answer']).strip()
                
                # Skip if we already tried this answer
                if answer in result.tried_answers:
                    self.log(f"Already tried: {answer}")
                    continue
                    
                result.tried_answers.add(answer)
                
                # Submit the answer
                submit_ok = await self._submit_answer(
                    answer,
                    solution.get('submit_selector'),
                    solution.get('submit_button')
                )
                
                if not submit_ok:
                    self.log("Failed to submit")
                    # DON'T reload - just continue to next attempt
                    continue
                    
                result.answer_submitted = answer
                
                # Wait longer for page update and check result
                await asyncio.sleep(1.5)
                check = await self.browser.check_result()
                
                # Check if step number changed (most reliable indicator)
                new_num = check.get('challengeNumber')
                if new_num and challenge_number and new_num > challenge_number:
                    self.log(f"✓ Advanced to step {new_num}")
                    result.success = True
                    break
                elif check.get('success') and not check.get('failure'):
                    self.log(f"✓ SUCCESS: {answer}")
                    result.success = True
                    break
                elif check.get('completion'):
                    self.log(f"✓ CHALLENGE COMPLETE")
                    result.success = True
                    break
                elif check.get('failure') and not check.get('success'):
                    self.log(f"✗ Failed: {answer}")
                else:
                    # Ambiguous - check body text for step change
                    body_sample = check.get('bodyTextSample', '')
                    if f'step {challenge_number + 1}' in body_sample:
                        self.log(f"✓ Detected step {challenge_number + 1} in body")
                        result.success = True
                        break
                    self.log(f"Result unclear, continuing...")
                        
        except Exception as e:
            result.error = str(e)
            self.log(f"Error: {e}")
            
        result.time_seconds = time.time() - start_time
        return result
        
    async def _attempt_text_extraction(self, challenge_number: int,
                                       tried_answers: Set[str]) -> Optional[Dict]:
        """Attempt 1: Pure text extraction"""
        self.log("Strategy: Text extraction")
        
        # Extract all page data
        data = await self.browser.extract_page_data()
        logs = await self.browser.get_console_logs()
        
        # Add console logs to data
        data['consoleLogs'] = logs
        
        # Log what we found
        self._log_extraction_summary(data)
        
        body_text = data.get('bodyText', '')
        self.log(f"Body text: {body_text[:150]}...")
        
        # FAST PATH: Try to extract code directly from text
        code = extract_code_from_text(body_text)
        if code and code not in tried_answers:
            self.log(f"Fast extracted code: {code}")
            return {
                'answer': code,
                'confidence': 0.8,
                'reasoning': 'Extracted directly from page text',
                'submit_selector': 'input[placeholder*="code"]',
                'submit_button': None
            }
        
        # Check console logs for codes
        for log in logs:
            log_code = extract_code_from_text(log.get('msg', ''))
            if log_code and log_code not in tried_answers:
                self.log(f"Found code in console: {log_code}")
                return {
                    'answer': log_code,
                    'confidence': 0.9,
                    'reasoning': 'Found in console log',
                    'submit_selector': 'input',
                    'submit_button': None
                }
        
        # Check hidden elements
        for hidden in data.get('hiddenElements', []):
            hidden_code = extract_code_from_text(hidden.get('text', ''))
            if hidden_code and hidden_code not in tried_answers:
                self.log(f"Found code in hidden element: {hidden_code}")
                return {
                    'answer': hidden_code,
                    'confidence': 0.85,
                    'reasoning': 'Found in hidden DOM element',
                    'submit_selector': 'input',
                    'submit_button': None
                }
        
        # SLOW PATH: Use LLM if fast extraction failed
        self.log("Fast extraction failed, using LLM")
        solution = self.llm.solve_challenge(
            extracted_data=data,
            tried_answers=tried_answers,
            challenge_number=challenge_number
        )
        
        self.log(f"LLM answer: {solution.get('answer')} (confidence: {solution.get('confidence', 0):.1%})")
        
        return solution
        
    async def _dismiss_popups(self):
        """Try to dismiss any blocking popups - be careful not to navigate away"""
        try:
            # Press Escape once to close popups (not multiple times)
            await self.browser.page.keyboard.press('Escape')
            await asyncio.sleep(0.1)
            
            # Scroll back to top where the form usually is
            await self.browser.page.evaluate('window.scrollTo(0, 0)')
            await asyncio.sleep(0.1)
            
            # DON'T click in the corner or on close buttons - this can cause navigation
        except:
            pass
    
    async def _attempt_with_interactions(self, challenge_number: int,
                                         tried_answers: Set[str]) -> Optional[Dict]:
        """Attempt 2: Try interactions then re-extract"""
        self.log("Strategy: Interactions + re-extract")
        
        # Dismiss any popups first
        await self._dismiss_popups()
        
        # First get current page state
        data = await self.browser.extract_page_data()
        body_text = data.get('bodyText', '').lower()
        
        # Debug: log detection keys and body sample
        self.log(f"Body sample: {body_text[:100]}...")
        self.log(f"Detection: scroll={'scroll' in body_text}, reveal={'reveal' in body_text}, hidden={'hidden dom' in body_text}")
        
        # TRY ALL INTERACTION TYPES - challenge types are randomized
        self.log("Interactions...")
        
        # Check for Delayed Reveal challenge - wait for timer
        data = await self.browser.extract_page_data()
        body = data.get('bodyText', '').lower()
        if 'delayed reveal' in body or 'waiting' in body:
            self.log("Delayed Reveal detected - waiting 5s...")
            await asyncio.sleep(5)
        
        # 1. Scroll down (for Scroll to Reveal)
        await self.browser.page.evaluate('window.scrollBy(0, 700)')
        await asyncio.sleep(0.4)
        await self.browser.page.evaluate('window.scrollBy(0, 700)')
        await asyncio.sleep(0.4)
        
        # 2. Try clicking "Reveal Code" via JS (for Click to Reveal)
        try:
            clicked = await self.browser.page.evaluate("""
                () => {
                    const btns = Array.from(document.querySelectorAll('button'));
                    const revealBtn = btns.find(b => b.textContent.includes('Reveal'));
                    if (revealBtn) { revealBtn.click(); return true; }
                    return false;
                }
            """)
            if clicked:
                self.log("Clicked Reveal Code (JS)")
                await asyncio.sleep(0.5)
        except:
            pass
        
        # 3. Click cursor-pointer divs (for Hidden DOM challenge)
        for i in range(5):
            try:
                await self.browser.page.keyboard.press('Escape')
                await asyncio.sleep(0.05)
                clicked = await self.browser.page.evaluate("""
                    () => {
                        const el = document.querySelector('.cursor-pointer');
                        if (el) { el.click(); return true; }
                        return false;
                    }
                """)
                if clicked:
                    self.log(f"Click #{i+1}")
                    await asyncio.sleep(0.25)
                else:
                    break
            except:
                break
        
        # 4. Hover (for hover challenges)
        try:
            await self.browser.page.evaluate("document.querySelectorAll('*').forEach(el => el.dispatchEvent(new MouseEvent('mouseenter', {bubbles: true})))")
        except:
            pass
        
        # 5. Drag-and-drop (for drag challenges)
        if 'drag' in body:
            self.log("Drag-and-Drop detected - performing drag...")
            try:
                # Find source and target elements
                drag_result = await self.browser.page.evaluate("""
                    () => {
                        const source = document.querySelector('[draggable="true"]');
                        const target = document.querySelector('[data-drop], .drop-zone, .drop-target, [class*="drop"]');
                        if (source && target) {
                            const sourceRect = source.getBoundingClientRect();
                            const targetRect = target.getBoundingClientRect();
                            return {
                                source: { x: sourceRect.x + sourceRect.width/2, y: sourceRect.y + sourceRect.height/2 },
                                target: { x: targetRect.x + targetRect.width/2, y: targetRect.y + targetRect.height/2 }
                            };
                        }
                        return null;
                    }
                """)
                
                if drag_result:
                    await self.browser.page.mouse.move(drag_result['source']['x'], drag_result['source']['y'])
                    await self.browser.page.mouse.down()
                    await asyncio.sleep(0.1)
                    await self.browser.page.mouse.move(drag_result['target']['x'], drag_result['target']['y'])
                    await asyncio.sleep(0.1)
                    await self.browser.page.mouse.up()
                    self.log("Drag performed")
                    await asyncio.sleep(0.5)
            except Exception as e:
                self.log(f"Drag failed: {e}")
        
        # Re-extract after interactions
        data = await self.browser.extract_page_data()
        body_text = data.get('bodyText', '')
        
        # Debug: show what we got
        self.log(f"Re-extracted body: {body_text[:150]}...")
        
        # Try fast extraction first
        code = extract_code_from_text(body_text)
        if code and code not in tried_answers:
            self.log(f"Fast extracted code after interaction: {code}")
            return {
                'answer': code,
                'confidence': 0.85,
                'reasoning': 'Extracted after interaction',
                'submit_selector': 'input[placeholder*="code"]',
                'submit_button': None
            }
        
        # Fall back to LLM
        logs = await self.browser.get_console_logs()
        data['consoleLogs'] = logs
        
        solution = self.llm.solve_challenge(
            extracted_data=data,
            tried_answers=tried_answers,
            challenge_number=challenge_number
        )
        
        self.log(f"LLM answer: {solution.get('answer')} (confidence: {solution.get('confidence', 0):.1%})")
        
        return solution
        
    async def _attempt_with_vision(self, challenge_number: int,
                                   tried_answers: Set[str]) -> Optional[Dict]:
        """Attempt 3: Screenshot + vision model"""
        self.log("Strategy: Vision model (screenshot)")
        
        screenshot = await self.browser.take_screenshot_base64()
        
        if not screenshot:
            self.log("Failed to take screenshot")
            return None
            
        solution = self.llm.solve_with_vision(
            screenshot_base64=screenshot,
            tried_answers=tried_answers,
            challenge_number=challenge_number
        )
        
        self.log(f"Vision answer: {solution.get('answer')} (confidence: {solution.get('confidence', 0):.1%})")
        
        return solution
        
    async def _submit_answer(self, answer: str, 
                            input_selector: Optional[str],
                            button_selector: Optional[str]) -> bool:
        """Submit an answer to the challenge"""
        
        self.log(f"Submitting answer: {answer}")
        
        # First dismiss any blocking popups
        await self._dismiss_popups()
        
        # Try multiple input selectors
        input_selectors = [
            input_selector,
            'input[placeholder*="code"]',
            'input[placeholder*="Code"]',
            'input[type="text"]',
            'input:not([type="hidden"]):not([type="submit"])',
            'textarea',
            '#answer',
            '#code'
        ]
        
        # Use Playwright's fill() method for proper React compatibility
        try:
            # Fill input using Playwright (this properly triggers React events)
            await self.browser.page.fill('input[placeholder*="code"]', answer, force=True, timeout=2000)
            self.log(f"Filled input with Playwright")
            
            # Wait for React to update and enable button
            await asyncio.sleep(0.3)
            
            # Click submit button using JS to ensure it finds the right one
            clicked = await self.browser.page.evaluate("""
                () => {
                    const btns = Array.from(document.querySelectorAll('button'));
                    // Look for the form submit button specifically
                    const form = document.querySelector('form');
                    if (form) {
                        const formBtn = form.querySelector('button');
                        if (formBtn) { formBtn.click(); return 'form_button'; }
                    }
                    // Fallback: find button with "Submit" text
                    const submitBtn = btns.find(b => b.textContent.includes('Submit'));
                    if (submitBtn && !submitBtn.disabled) { submitBtn.click(); return 'submit_text'; }
                    return 'not_found';
                }
            """)
            self.log(f"Clicked submit: {clicked}")
            return clicked != 'not_found'
        except Exception as e:
            self.log(f"Fill/click failed: {e}")
            
            if submitted.get('success'):
                self.log(f"Submitted via JS ({submitted.get('method')})")
                return True
            else:
                self.log(f"JS submit failed: {submitted.get('error')}")
        except Exception as e:
            self.log(f"JS submit error: {e}")
        
        # Fallback to Playwright methods
        typed = False
        for sel in input_selectors:
            if not sel:
                continue
            try:
                await self.browser.page.fill(sel, answer, timeout=2000)
                typed = True
                self.log(f"Typed into: {sel}")
                break
            except:
                pass
                
        if not typed:
            self.log("Could not find input field")
            return False
        
        # Dismiss popups and submit
        await self._dismiss_popups()
        
        try:
            await self.browser.page.click('button:has-text("Submit")', timeout=2000, force=True)
            self.log("Clicked submit: button:has-text('Submit')")
            return True
        except:
            pass
        
        # Fallback: press Enter
        await self.browser.page.keyboard.press('Enter')
        self.log("Pressed Enter to submit")
        return True
            
    def _log_extraction_summary(self, data: Dict):
        """Log summary of what was extracted"""
        summary = []
        
        if data.get('consoleLogs'):
            summary.append(f"Console: {len(data['consoleLogs'])} logs")
        if data.get('comments'):
            summary.append(f"Comments: {len(data['comments'])}")
        if data.get('hiddenElements'):
            summary.append(f"Hidden: {len(data['hiddenElements'])}")
        if data.get('dataAttributes'):
            summary.append(f"Data attrs: {len(data['dataAttributes'])}")
        if data.get('globalVars'):
            summary.append(f"JS vars: {len(data['globalVars'])}")
        if data.get('storage', {}).get('localStorage'):
            summary.append(f"localStorage: {len(data['storage']['localStorage'])}")
        if data.get('pseudoContent'):
            summary.append(f"Pseudo: {len(data['pseudoContent'])}")
        if data.get('cssVariables'):
            summary.append(f"CSS vars: {len(data['cssVariables'])}")
            
        if summary:
            self.log(f"Extracted: {', '.join(summary)}")
