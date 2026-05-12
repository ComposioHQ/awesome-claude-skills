#!/bin/bash
set -euo pipefail

# Only run in remote (Claude Code on the web) environments
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

# Install Python packages used across skills
pip install --quiet \
  cffi \
  openpyxl \
  pypdf \
  defusedxml \
  lxml \
  python-pptx \
  Pillow \
  six \
  pdf2image \
  imageio \
  imageio-ffmpeg \
  numpy \
  playwright \
  pytest

# Install Playwright browser for webapp-testing skill
playwright install --with-deps chromium

# Install Node.js deps for MCP builder skill
pip install --quiet anthropic mcp
