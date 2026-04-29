#!/bin/bash
# Web Challenge Solver Runner Script

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Web Challenge Solver Agent${NC}"
echo -e "${GREEN}========================================${NC}"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is required${NC}"
    exit 1
fi

# Check/install dependencies
echo -e "${YELLOW}Checking dependencies...${NC}"
pip install -q -r requirements.txt

# Install Playwright browsers if needed
if ! python3 -c "from playwright.sync_api import sync_playwright" 2>/dev/null; then
    echo -e "${YELLOW}Installing Playwright browsers...${NC}"
    playwright install chromium
fi

# Check for API key
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo -e "${YELLOW}Warning: ANTHROPIC_API_KEY not set. AI assistance will be disabled.${NC}"
    echo -e "${YELLOW}Set it with: export ANTHROPIC_API_KEY='your-key-here'${NC}"
fi

# Parse arguments
URL="${CHALLENGE_URL:-https://qa-bench.com}"
OUTPUT_DIR="${OUTPUT_DIR:-/tmp/qa_bench_results}"
EXTRA_ARGS=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --url)
            URL="$2"
            shift 2
            ;;
        --output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        --visible)
            EXTRA_ARGS="$EXTRA_ARGS --visible"
            shift
            ;;
        --no-ai)
            EXTRA_ARGS="$EXTRA_ARGS --no-ai"
            shift
            ;;
        *)
            EXTRA_ARGS="$EXTRA_ARGS $1"
            shift
            ;;
    esac
done

# Create output directory
mkdir -p "$OUTPUT_DIR"

echo -e "${GREEN}Starting challenge solver...${NC}"
echo -e "URL: $URL"
echo -e "Output: $OUTPUT_DIR"

# Run the solver
python3 qa_bench_solver.py --url "$URL" --output "$OUTPUT_DIR" $EXTRA_ARGS

# Check results
if [ -f "$OUTPUT_DIR/results.json" ]; then
    echo -e "\n${GREEN}Results saved to: $OUTPUT_DIR/results.json${NC}"
    echo -e "\n${GREEN}Summary:${NC}"
    python3 -c "
import json
with open('$OUTPUT_DIR/results.json') as f:
    r = json.load(f)
print(f\"Time: {r['duration_formatted']}\")
print(f\"Challenges: {r['challenges']['solved']}/{r['challenges']['total']} ({r['challenges']['success_rate']})\")
print(f\"Tokens: {r['tokens']['total']}\")
print(f\"Cost: {r['cost']['estimated_usd']}\")
"
fi
