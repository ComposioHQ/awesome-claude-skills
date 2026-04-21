#!/bin/bash
set -e
echo "=== Browser Challenge Agent Setup ==="

# Create venv if not exists
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate

pip install -r requirements.txt
playwright install chromium

echo "=== Setup complete ==="
echo "Run: source venv/bin/activate && python main.py"
