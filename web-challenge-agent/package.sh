#!/bin/bash
# Package the Web Challenge Solver Agent into a zip file

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

VERSION="1.0.0"
PACKAGE_NAME="web-challenge-agent-v${VERSION}"
OUTPUT_FILE="${PACKAGE_NAME}.zip"

echo "Packaging Web Challenge Solver Agent..."

# Create a temporary directory for packaging
TEMP_DIR=$(mktemp -d)
PACKAGE_DIR="$TEMP_DIR/$PACKAGE_NAME"
mkdir -p "$PACKAGE_DIR"

# Copy files
cp requirements.txt "$PACKAGE_DIR/"
cp agent.py "$PACKAGE_DIR/"
cp qa_bench_solver.py "$PACKAGE_DIR/"
cp browser_nav_solver.py "$PACKAGE_DIR/"
cp smart_solver.py "$PACKAGE_DIR/"
cp targeted_solver.py "$PACKAGE_DIR/"
cp final_solver.py "$PACKAGE_DIR/"
cp ai_solver.py "$PACKAGE_DIR/"
cp solve.py "$PACKAGE_DIR/"
cp run.sh "$PACKAGE_DIR/"
cp README.md "$PACKAGE_DIR/"

# Make scripts executable
chmod +x "$PACKAGE_DIR/run.sh"
chmod +x "$PACKAGE_DIR/agent.py"
chmod +x "$PACKAGE_DIR/qa_bench_solver.py"

# Create the zip
cd "$TEMP_DIR"
zip -r "$SCRIPT_DIR/$OUTPUT_FILE" "$PACKAGE_NAME"

# Cleanup
rm -rf "$TEMP_DIR"

echo "Package created: $OUTPUT_FILE"
echo ""
echo "Contents:"
unzip -l "$SCRIPT_DIR/$OUTPUT_FILE"
