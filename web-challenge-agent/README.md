# Web Challenge Solver Agent

An AI-powered browser automation agent designed to solve web challenges (specifically the Browser Navigation Challenge at https://serene-frangipane-7fd25b.netlify.app/) in under 5 minutes.

## Challenge

Solve all 30 challenges on the Browser Navigation Challenge website in under 5 minutes, tracking:
- Time taken
- Token usage
- Token cost

## Quick Start

```bash
# 1. Set your Anthropic API key
export ANTHROPIC_API_KEY="your-api-key-here"

# 2. Install dependencies
pip install -r requirements.txt
playwright install chromium

# 3. Run the AI-powered solver (recommended)
python ai_solver.py

# Or run without AI (heuristics only)
python browser_nav_solver.py --no-ai
```

## Solvers Available

### 1. AI Solver (`ai_solver.py`) - Recommended
Uses Claude Vision to understand each challenge and determine the correct action.

```bash
python ai_solver.py [--url URL] [--output DIR] [--visible]
```

### 2. Browser Navigation Solver (`browser_nav_solver.py`)
Specialized solver using heuristics with optional AI fallback.

```bash
python browser_nav_solver.py [--url URL] [--output DIR] [--visible] [--no-ai]
```

### 3. QA Bench Solver (`qa_bench_solver.py`)
General-purpose solver for QA Bench style challenges.

```bash
python qa_bench_solver.py [--url URL] [--output DIR] [--visible] [--no-ai]
```

### 4. Generic Agent (`agent.py`)
Basic browser automation agent.

```bash
python agent.py [--url URL] [--headless] [--visible]
```

## Command Line Options

| Option | Description |
|--------|-------------|
| `--url URL` | Challenge website URL (default: https://serene-frangipane-7fd25b.netlify.app/) |
| `--output DIR` | Output directory for screenshots and results |
| `--visible` | Show browser window (for debugging) |
| `--no-ai` | Disable AI assistance (heuristics only) |

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | Yes (for AI solver) | Claude API key |
| `CHALLENGE_URL` | No | Override default challenge URL |
| `OUTPUT_DIR` | No | Override default output directory |

## Output

Each run generates:

1. **Screenshots**: `{step}_{attempt}_before.png` and after for each challenge
2. **Results JSON**: `results.json` with metrics

### Results Format

```json
{
  "run_id": "20240115_143022",
  "timestamp": "2024-01-15T14:30:45",
  "duration_seconds": 187.34,
  "duration_formatted": "3m 7s",
  "under_5_minutes": true,
  "challenges": {
    "total": 30,
    "solved": 28,
    "success_rate": "93.3%"
  },
  "tokens": {
    "input": 125000,
    "output": 5000,
    "total": 130000,
    "api_calls": 35
  },
  "cost_usd": "$0.45"
}
```

## Architecture

### AI Solver Strategy

1. **Screenshot Capture**: Take full-page screenshot
2. **Claude Analysis**: Send screenshot to Claude Vision with context
3. **Action Extraction**: Parse Claude's JSON response for action type and selector
4. **Execution**: Perform the action using Playwright
5. **Verification**: Check if step number advanced
6. **Retry**: If stuck, provide previous actions context to Claude

### Supported Actions

- `click` - Click an element
- `fill` - Type text into input
- `select` - Choose dropdown option
- `hover` - Hover over element
- `dblclick` - Double-click
- `rightclick` - Right-click (context menu)
- `check` - Check checkbox/radio
- `scroll` - Scroll page
- `drag` - Drag and drop

## Performance Tips

1. **Use AI Solver**: Heuristics alone struggle with complex challenges
2. **Ensure Good Network**: Both website and Claude API need stable connection
3. **Run Headless**: Faster execution without GUI overhead
4. **Sufficient API Quota**: May need 30-50 API calls for all 30 challenges

## Files

```
web-challenge-agent/
├── ai_solver.py           # AI-powered solver (recommended)
├── browser_nav_solver.py  # Specialized solver with AI fallback
├── qa_bench_solver.py     # General QA Bench solver
├── agent.py               # Basic automation agent
├── requirements.txt       # Python dependencies
├── run.sh                 # Runner script
├── package.sh             # Create zip package
└── README.md              # This file
```

## Requirements

- Python 3.8+
- Playwright
- Anthropic API key (Claude access)
- ~$0.50-1.00 in API credits per full run

## Installation

```bash
# Clone the repository
git clone <repo-url>
cd web-challenge-agent

# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Set API key
export ANTHROPIC_API_KEY="your-key"

# Run
python ai_solver.py
```

## Troubleshooting

### "ANTHROPIC_API_KEY required"
Set your Claude API key: `export ANTHROPIC_API_KEY="sk-..."`

### Browser crashes
Install system dependencies: `playwright install-deps chromium`

### Stuck on same step
The solver will automatically retry with different approaches and eventually skip if stuck for too long.

### Timeout errors
Increase timeout or check network connectivity.

## License

MIT License
