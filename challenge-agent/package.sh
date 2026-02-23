#!/bin/bash
# Package the challenge agent for distribution

set -e

OUTPUT_DIR="challenge-agent-dist"
ZIP_NAME="challenge-agent.zip"

echo "=== Packaging Challenge Agent ==="

# Create distribution directory
rm -rf $OUTPUT_DIR
mkdir -p $OUTPUT_DIR

# Copy source files
cp main.py $OUTPUT_DIR/
cp runner.py $OUTPUT_DIR/
cp solver.py $OUTPUT_DIR/
cp browser.py $OUTPUT_DIR/
cp llm_client.py $OUTPUT_DIR/
cp extractor.js $OUTPUT_DIR/
cp requirements.txt $OUTPUT_DIR/
cp setup.sh $OUTPUT_DIR/
cp run.sh $OUTPUT_DIR/
cp .env.example $OUTPUT_DIR/
cp README.md $OUTPUT_DIR/

# Copy latest run stats if available
if [ -f run_stats.json ]; then
    cp run_stats.json $OUTPUT_DIR/
fi

# Create zip
rm -f $ZIP_NAME
cd $OUTPUT_DIR
zip -r ../$ZIP_NAME .
cd ..

echo "=== Package created: $ZIP_NAME ==="
echo "Contents:"
unzip -l $ZIP_NAME

# Cleanup
rm -rf $OUTPUT_DIR

echo ""
echo "To use:"
echo "1. unzip $ZIP_NAME"
echo "2. cd challenge-agent-dist"
echo "3. ./setup.sh"
echo "4. export ANTHROPIC_API_KEY='your-key'"
echo "5. python main.py"
