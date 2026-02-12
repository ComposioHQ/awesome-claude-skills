"""
llm_client.py - Multi-provider LLM client with token tracking
"""

import os
import json
import re
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass, field

# System prompts
SOLVER_SYSTEM_PROMPT = """You are an expert at solving browser-based challenges. Analyze extracted page data to find the hidden code/answer.

CRITICAL: Look for a 6-character code (letters and numbers) that should be entered in the input field.

WHERE TO FIND THE ANSWER:
1. Look in bodyText for patterns like "Code: ABC123" or "The code is: XYZ789" or just standalone 6-char codes
2. Check hidden elements for revealed codes
3. Check console logs
4. Check data attributes
5. Check global variables
6. Look for text that appeared after interactions (scroll, click)

The answer is typically:
- A 6-character alphanumeric code
- Visible in the page text after performing the required action (scroll/click/hover)
- Sometimes encoded (base64, reversed, etc.) - decode it before answering

OUTPUT FORMAT (JSON only):
{
  "answer": "ABC123",
  "confidence": 0.9,
  "reasoning": "Found code in bodyText after scrolling",
  "submit_selector": "input[placeholder*='code']",
  "submit_button": null
}

If you cannot find a code, return:
{
  "answer": null,
  "confidence": 0.0,
  "reasoning": "No code visible - may need interaction first",
  "submit_selector": null,
  "submit_button": null,
  "interaction_needed": {"type": "scroll", "amount": 500}
}
"""

VISION_SYSTEM_PROMPT = """You are analyzing a screenshot of a browser challenge. Find the answer that should be submitted.

Look for:
- Text that stands out or looks like an answer/code
- Hidden text revealed by interactions
- Visual puzzles or patterns
- Canvas-rendered text
- Any text that looks like it should be typed into an input field

Return ONLY valid JSON:
{
  "answer": "THE_ANSWER_YOU_SEE",
  "confidence": 0.0-1.0,
  "reasoning": "What you see in the image",
  "submit_selector": "input or [type='text']",
  "submit_button": null
}
"""


@dataclass
class LLMStats:
    """Track LLM usage statistics"""
    total_calls: int = 0
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_cost_usd: float = 0.0
    calls_by_model: Dict[str, int] = field(default_factory=dict)
    
    def add_call(self, model: str, input_tokens: int, output_tokens: int, cost: float):
        self.total_calls += 1
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.total_cost_usd += cost
        self.calls_by_model[model] = self.calls_by_model.get(model, 0) + 1


class LLMClient:
    """Multi-provider LLM client"""
    
    # Cost per 1K tokens (approximate)
    COST_PER_1K = {
        'claude-sonnet-4-20250514': {'input': 0.003, 'output': 0.015},
        'claude-3-5-sonnet-20241022': {'input': 0.003, 'output': 0.015},
        'claude-3-haiku-20240307': {'input': 0.00025, 'output': 0.00125},
        'gpt-4o': {'input': 0.005, 'output': 0.015},
        'gpt-4o-mini': {'input': 0.00015, 'output': 0.0006},
    }
    
    def __init__(self, provider: str = 'anthropic', model: str = None):
        self.provider = provider
        self.stats = LLMStats()
        
        if provider == 'anthropic':
            import anthropic
            self.client = anthropic.Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))
            self.model = model or 'claude-sonnet-4-20250514'
        elif provider == 'openai':
            import openai
            self.client = openai.OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
            self.model = model or 'gpt-4o'
        else:
            raise ValueError(f"Unknown provider: {provider}")
            
    def _estimate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost for a call"""
        costs = self.COST_PER_1K.get(model, {'input': 0.01, 'output': 0.03})
        return (input_tokens / 1000 * costs['input']) + (output_tokens / 1000 * costs['output'])
        
    def solve_challenge(self, extracted_data: Dict[str, Any], 
                        tried_answers: set = None,
                        challenge_number: int = None) -> Dict[str, Any]:
        """Analyze extracted data and return solution"""
        
        # Build the prompt
        prompt_parts = []
        
        if challenge_number:
            prompt_parts.append(f"Challenge #{challenge_number}")
            
        if tried_answers:
            prompt_parts.append(f"\n⚠️ ALREADY TRIED AND FAILED: {list(tried_answers)}")
            prompt_parts.append("Find a DIFFERENT answer or try format variations!")
            
        prompt_parts.append("\n\nEXTRACTED PAGE DATA:")
        prompt_parts.append(json.dumps(extracted_data, indent=2, default=str)[:15000])
        prompt_parts.append("\n\nAnalyze the data above and find the hidden answer. Return JSON only.")
        
        user_prompt = "\n".join(prompt_parts)
        
        return self._call_llm(SOLVER_SYSTEM_PROMPT, user_prompt)
        
    def solve_with_vision(self, screenshot_base64: str,
                         tried_answers: set = None,
                         challenge_number: int = None) -> Dict[str, Any]:
        """Analyze screenshot and return solution"""
        
        prompt_parts = []
        if challenge_number:
            prompt_parts.append(f"Challenge #{challenge_number}")
        if tried_answers:
            prompt_parts.append(f"\n⚠️ ALREADY TRIED: {list(tried_answers)}")
        prompt_parts.append("\nLook at the screenshot and find the answer to submit.")
        
        user_prompt = "\n".join(prompt_parts)
        
        return self._call_llm_vision(VISION_SYSTEM_PROMPT, user_prompt, screenshot_base64)
        
    def _call_llm(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """Make LLM call and parse response"""
        
        try:
            if self.provider == 'anthropic':
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=1024,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_prompt}]
                )
                content = response.content[0].text
                input_tokens = response.usage.input_tokens
                output_tokens = response.usage.output_tokens
                
            else:  # openai
                response = self.client.chat.completions.create(
                    model=self.model,
                    max_tokens=1024,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ]
                )
                content = response.choices[0].message.content
                input_tokens = response.usage.prompt_tokens
                output_tokens = response.usage.completion_tokens
                
            # Track stats
            cost = self._estimate_cost(self.model, input_tokens, output_tokens)
            self.stats.add_call(self.model, input_tokens, output_tokens, cost)
            
            # Parse JSON from response
            return self._parse_json_response(content)
            
        except Exception as e:
            return {"error": str(e), "answer": None, "confidence": 0}
            
    def _call_llm_vision(self, system_prompt: str, user_prompt: str, 
                         image_base64: str) -> Dict[str, Any]:
        """Make vision LLM call"""
        
        try:
            if self.provider == 'anthropic':
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=1024,
                    system=system_prompt,
                    messages=[{
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/png",
                                    "data": image_base64
                                }
                            },
                            {"type": "text", "text": user_prompt}
                        ]
                    }]
                )
                content = response.content[0].text
                input_tokens = response.usage.input_tokens
                output_tokens = response.usage.output_tokens
                
            else:  # openai
                response = self.client.chat.completions.create(
                    model=self.model,
                    max_tokens=1024,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": user_prompt},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/png;base64,{image_base64}"
                                    }
                                }
                            ]
                        }
                    ]
                )
                content = response.choices[0].message.content
                input_tokens = response.usage.prompt_tokens
                output_tokens = response.usage.completion_tokens
                
            cost = self._estimate_cost(self.model, input_tokens, output_tokens)
            self.stats.add_call(self.model, input_tokens, output_tokens, cost)
            
            return self._parse_json_response(content)
            
        except Exception as e:
            return {"error": str(e), "answer": None, "confidence": 0}
            
    def _parse_json_response(self, content: str) -> Dict[str, Any]:
        """Extract JSON from LLM response"""
        try:
            # Try direct parse first
            return json.loads(content)
        except:
            pass
            
        # Try to find JSON in the response
        try:
            match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', content, re.DOTALL)
            if match:
                return json.loads(match.group())
        except:
            pass
            
        return {
            "error": "Failed to parse LLM response",
            "raw_response": content[:500],
            "answer": None,
            "confidence": 0
        }
        
    def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics"""
        return {
            "total_calls": self.stats.total_calls,
            "total_input_tokens": self.stats.total_input_tokens,
            "total_output_tokens": self.stats.total_output_tokens,
            "total_tokens": self.stats.total_input_tokens + self.stats.total_output_tokens,
            "total_cost_usd": round(self.stats.total_cost_usd, 4),
            "calls_by_model": self.stats.calls_by_model
        }
