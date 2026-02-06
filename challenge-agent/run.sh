#!/bin/bash
# Quick runner for Browser Challenge Agent

# Check if venv exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run with default settings
python main.py "$@"
