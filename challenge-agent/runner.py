"""
runner.py - Orchestrator with route discovery, time budget, and metrics
"""

import asyncio
import re
import time
import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field, asdict

from browser import BrowserController
from llm_client import LLMClient
from solver import ChallengeSolver, SolveResult


@dataclass
class ChallengeMetrics:
    """Metrics for a single challenge"""
    number: int
    url: str
    success: bool = False
    answer: Optional[str] = None
    attempts: int = 0
    time_seconds: float = 0.0
    error: Optional[str] = None
    tried_answers: List[str] = field(default_factory=list)


@dataclass  
class RunMetrics:
    """Aggregate metrics for entire run"""
    start_time: float = 0.0
    end_time: float = 0.0
    total_challenges: int = 30
    challenges_completed: int = 0
    challenges_failed: int = 0
    challenges_skipped: int = 0
    total_time_seconds: float = 0.0
    under_5_minutes: bool = False
    aborted: bool = False
    llm_stats: Dict[str, Any] = field(default_factory=dict)
    challenge_metrics: List[ChallengeMetrics] = field(default_factory=list)
    route_pattern: str = ""
    

class ChallengeRunner:
    """Orchestrates solving all challenges"""
    
    BASE_URL = "https://serene-frangipane-7fd25b.netlify.app"
    TOTAL_CHALLENGES = 30
    TOTAL_TIMEOUT = 300  # 5 minutes
    
    def __init__(self, provider: str = 'anthropic', model: str = None,
                 headless: bool = True, verbose: bool = True):
        self.browser = BrowserController(headless=headless)
        self.llm = LLMClient(provider=provider, model=model)
        self.solver = ChallengeSolver(self.browser, self.llm, verbose=verbose)
        self.verbose = verbose
        self.metrics = RunMetrics()
        
    def log(self, msg: str):
        if self.verbose:
            print(f"[Runner] {msg}")
            
    async def run(self, timeout: float = None) -> RunMetrics:
        """Run all challenges within time budget"""
        
        timeout = timeout or self.TOTAL_TIMEOUT
        self.metrics.start_time = time.time()
        
        try:
            await self.browser.start()
            
            # Discover route pattern
            route_pattern = await self._discover_route()
            if not route_pattern:
                self.log("ERROR: Could not detect route pattern")
                self.metrics.error = "Route discovery failed"
                return self.metrics
                
            self.metrics.route_pattern = route_pattern
            self.log(f"Route pattern: {route_pattern}")
            
            # Check if this is a SPA
            is_spa = route_pattern.startswith("SPA:")
            if is_spa:
                spa_url = route_pattern[4:]  # Remove "SPA:" prefix
                self.log(f"Running in SPA mode on: {spa_url}")
            
            # Solve challenges
            for i in range(1, self.TOTAL_CHALLENGES + 1):
                # Check time budget
                elapsed = time.time() - self.metrics.start_time
                remaining = timeout - elapsed
                
                if remaining <= 0:
                    self.log(f"Time budget exhausted at challenge {i}")
                    self.metrics.aborted = True
                    self.metrics.challenges_skipped = self.TOTAL_CHALLENGES - i + 1
                    break
                    
                # Calculate adaptive timeout per challenge - minimum 8 seconds
                challenges_left = self.TOTAL_CHALLENGES - i + 1
                per_challenge_timeout = max(8, min(15, remaining / challenges_left))
                
                self.log(f"\n{'='*50}")
                self.log(f"Challenge {i}/{self.TOTAL_CHALLENGES} (budget: {per_challenge_timeout:.1f}s)")
                self.log(f"{'='*50}")
                
                # Build challenge URL (for SPA, we stay on the same page)
                if is_spa:
                    url = spa_url
                else:
                    url = route_pattern.format(n=i)
                
                # Solve
                result = await self.solver.solve(
                    challenge_url=url,
                    challenge_number=i,
                    timeout=per_challenge_timeout,
                    is_spa=is_spa
                )
                
                # Record metrics
                cm = ChallengeMetrics(
                    number=i,
                    url=url,
                    success=result.success,
                    answer=result.answer_submitted,
                    attempts=result.attempts,
                    time_seconds=result.time_seconds,
                    error=result.error,
                    tried_answers=list(result.tried_answers)
                )
                self.metrics.challenge_metrics.append(cm)
                
                if result.success:
                    self.metrics.challenges_completed += 1
                    self.log(f"✓ Challenge {i} SOLVED in {result.time_seconds:.1f}s")
                else:
                    self.metrics.challenges_failed += 1
                    self.log(f"✗ Challenge {i} FAILED after {result.attempts} attempts")
                    
                # Check for completion
                check = await self.browser.check_result()
                if check.get('completion'):
                    self.log("🎉 ALL CHALLENGES COMPLETE!")
                    break
                    
        except Exception as e:
            self.log(f"Error: {e}")
            self.metrics.error = str(e)
            
        finally:
            await self.browser.close()
            
        # Finalize metrics
        self.metrics.end_time = time.time()
        self.metrics.total_time_seconds = self.metrics.end_time - self.metrics.start_time
        self.metrics.under_5_minutes = self.metrics.total_time_seconds < 300
        self.metrics.llm_stats = self.llm.get_stats()
        
        return self.metrics
        
    async def _discover_route(self) -> Optional[str]:
        """Discover the URL pattern for challenges"""
        
        self.log("Discovering route pattern...")
        
        # Navigate to landing page
        await self.browser.navigate(self.BASE_URL)
        await asyncio.sleep(1)
        
        # Click START button quickly
        try:
            await self.browser.page.click('text=START', timeout=3000)
            self.log("Clicked START")
            await asyncio.sleep(1.0)
        except:
            self.log("Could not find START button")
                
        # Check current URL
        current_url = await self.browser.get_current_url()
        self.log(f"Current URL: {current_url}")
        
        # Check page content for Step/Challenge indicator
        check = await self.browser.check_result()
        self.log(f"Challenge number detected: {check.get('challengeNumber')}")
        
        # This specific site is a SPA where we stay on step1 and the content changes
        # as we solve challenges. The version parameter is session-specific.
        if '/step' in current_url or check.get('challengeNumber'):
            self.log(f"SPA detected - staying on current URL for all challenges")
            return "SPA:" + current_url
        
        # Try to detect pattern from URL
        patterns = [
            (r'/challenge/(\d+)', f'{self.BASE_URL}/challenge/{{n}}'),
            (r'/level/(\d+)', f'{self.BASE_URL}/level/{{n}}'),
            (r'/q/(\d+)', f'{self.BASE_URL}/q/{{n}}'),
        ]
        
        for pattern, template in patterns:
            if re.search(pattern, current_url):
                self.log(f"Detected pattern: {template}")
                return template
                    
        # Fallback: assume current URL is the challenge page
        self.log("Using current URL as challenge base")
        return current_url
        
    def save_metrics(self, filepath: str = 'run_stats.json'):
        """Save metrics to JSON file"""
        
        # Convert to dict
        metrics_dict = {
            'start_time': self.metrics.start_time,
            'end_time': self.metrics.end_time,
            'total_time_seconds': round(self.metrics.total_time_seconds, 2),
            'total_time_formatted': f"{int(self.metrics.total_time_seconds // 60)}m {int(self.metrics.total_time_seconds % 60)}s",
            'under_5_minutes': self.metrics.under_5_minutes,
            'total_challenges': self.metrics.total_challenges,
            'challenges_completed': self.metrics.challenges_completed,
            'challenges_failed': self.metrics.challenges_failed,
            'challenges_skipped': self.metrics.challenges_skipped,
            'success_rate': f"{self.metrics.challenges_completed / self.metrics.total_challenges * 100:.1f}%",
            'aborted': self.metrics.aborted,
            'route_pattern': self.metrics.route_pattern,
            'llm_stats': self.metrics.llm_stats,
            'challenges': [
                {
                    'number': cm.number,
                    'url': cm.url,
                    'success': cm.success,
                    'answer': cm.answer,
                    'attempts': cm.attempts,
                    'time_seconds': round(cm.time_seconds, 2),
                    'error': cm.error,
                    'tried_answers': cm.tried_answers
                }
                for cm in self.metrics.challenge_metrics
            ]
        }
        
        with open(filepath, 'w') as f:
            json.dump(metrics_dict, f, indent=2)
            
        self.log(f"Metrics saved to {filepath}")
        
    def print_summary(self):
        """Print run summary"""
        
        print("\n" + "="*60)
        print("RUN SUMMARY")
        print("="*60)
        print(f"Total time: {self.metrics.total_time_seconds:.1f}s ({int(self.metrics.total_time_seconds // 60)}m {int(self.metrics.total_time_seconds % 60)}s)")
        print(f"Under 5 minutes: {'✓ YES' if self.metrics.under_5_minutes else '✗ NO'}")
        print(f"Challenges completed: {self.metrics.challenges_completed}/{self.metrics.total_challenges}")
        print(f"Challenges failed: {self.metrics.challenges_failed}")
        print(f"Challenges skipped: {self.metrics.challenges_skipped}")
        print(f"Success rate: {self.metrics.challenges_completed / self.metrics.total_challenges * 100:.1f}%")
        print(f"\nLLM Stats:")
        print(f"  Total calls: {self.metrics.llm_stats.get('total_calls', 0)}")
        print(f"  Total tokens: {self.metrics.llm_stats.get('total_tokens', 0)}")
        print(f"  Total cost: ${self.metrics.llm_stats.get('total_cost_usd', 0):.4f}")
        print("="*60)
        
        if self.metrics.challenges_completed >= 30 and self.metrics.under_5_minutes:
            print("\n🎉 SUCCESS! All 30 challenges solved in under 5 minutes!")
        elif self.metrics.challenges_completed >= 25:
            print("\n✓ Good run! Consider optimizing for remaining challenges.")
        else:
            print("\n⚠️ Needs improvement. Check run_stats.json for failed challenge details.")
