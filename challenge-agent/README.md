# Browser Challenge Agent

A browser automation agent that solves 30 browser-based challenges at `https://serene-frangipane-7fd25b.netlify.app` using Playwright and Claude AI.

## Current Performance

| Metric | Value |
|--------|-------|
| Challenges Solved | 4-5 out of 30 per run |
| Success Rate | ~15-20% |
| Time | ~5 minutes |
| Cost | ~$0.40-0.50 per run |

**Supported Challenge Types:**
- ✅ Scroll to Reveal
- ✅ Click to Reveal  
- ✅ Hidden DOM (cursor-pointer click)
- ✅ Delayed Reveal (timed wait)
- ⚠️ Memory Challenge (partial)
- ❌ Hover Challenge
- ❌ Drag-and-Drop

## Quick Start

```bash
# Setup
./setup.sh

# Set API key
export ANTHROPIC_API_KEY="your-key-here"

# Run
python main.py --timeout 300
```

## Features

- **Multi-strategy solving**: Text extraction, DOM interaction, and vision-based fallback
- **Challenge detection**: Automatically detects and handles different challenge types:
  - Scroll to Reveal
  - Click to Reveal
  - Hidden DOM (click multiple times)
  - Hover to reveal
- **Anti-loop mechanisms**: Tracks tried answers, per-challenge timeouts
- **Metrics tracking**: Detailed JSON output with timing, token usage, and cost

## Files

- `main.py` - CLI entry point
- `runner.py` - Orchestrator with route discovery and time budget management
- `solver.py` - Per-challenge solver with 3-attempt escalation strategy
- `browser.py` - Playwright wrapper with SPA awareness
- `llm_client.py` - Multi-provider LLM client (Anthropic/OpenAI)
- `extractor.js` - JavaScript injection for hidden content extraction

## Usage

```bash
# Full 5-minute run (default)
python main.py

# With visible browser for debugging
python main.py --visible

# Custom timeout
python main.py --timeout 180

# Use OpenAI instead of Anthropic
python main.py --provider openai
```

## Output

After each run, check `run_stats.json` for detailed metrics:
- Total time and whether it was under 5 minutes
- Challenges completed, failed, and skipped
- Per-challenge details (time, attempts, tried answers)
- LLM token usage and cost

## Challenge Types

The site uses randomized challenge types:

1. **Scroll to Reveal**: Scroll down 500px to reveal the code
2. **Click to Reveal**: Click a "Reveal Code" button
3. **Hidden DOM**: Click "click here" 3 times to reveal
4. **Various other hidden content patterns**

## Architecture

```
main.py (CLI)
    └── runner.py (Orchestrator)
            ├── Route Discovery (detects URL pattern)
            ├── Time Budget Manager
            └── solver.py (Per-Challenge)
                    ├── Attempt 1: Text extraction + fast code detection
                    ├── Attempt 2: Interactions (scroll/click) + re-extraction
                    └── Attempt 3: Vision model fallback
```

## Requirements

- Python 3.8+
- Playwright
- Anthropic API key (or OpenAI)

## Environment Variables

- `ANTHROPIC_API_KEY` - Required for Claude models
- `OPENAI_API_KEY` - Required if using OpenAI provider
