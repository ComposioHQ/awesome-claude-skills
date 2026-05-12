#!/bin/bash

# ==============================================================================
# Tampermonkey Userscript Generator
# ==============================================================================
# Generates a new userscript from template
#
# Usage:
#   bash generate-userscript.sh <script-name> <target-url> [template]
#
# Arguments:
#   script-name  : Name of the userscript (e.g., "youtube-enhancer")
#   target-url   : Target URL pattern (e.g., "https://www.youtube.com/*")
#   template     : Template to use (basic|advanced|spa) [default: basic]
#
# Examples:
#   bash generate-userscript.sh my-script "https://example.com/*"
#   bash generate-userscript.sh my-script "https://example.com/*" advanced
# ==============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATES_DIR="$(dirname "$SCRIPT_DIR")/templates"

# Parse arguments
SCRIPT_NAME="$1"
TARGET_URL="$2"
TEMPLATE="${3:-basic}"

# Validation
if [ -z "$SCRIPT_NAME" ] || [ -z "$TARGET_URL" ]; then
    echo -e "${RED}Error: Missing required arguments${NC}"
    echo ""
    echo "Usage: bash generate-userscript.sh <script-name> <target-url> [template]"
    echo ""
    echo "Arguments:"
    echo "  script-name  : Name of the userscript (e.g., 'youtube-enhancer')"
    echo "  target-url   : Target URL pattern (e.g., 'https://www.youtube.com/*')"
    echo "  template     : Template to use (basic|advanced|spa) [default: basic]"
    echo ""
    echo "Examples:"
    echo "  bash generate-userscript.sh my-script 'https://example.com/*'"
    echo "  bash generate-userscript.sh my-script 'https://example.com/*' advanced"
    exit 1
fi

# Determine template file
case "$TEMPLATE" in
    basic)
        TEMPLATE_FILE="$TEMPLATES_DIR/basic-template.user.js"
        ;;
    advanced)
        TEMPLATE_FILE="$TEMPLATES_DIR/advanced-template.user.js"
        ;;
    spa)
        TEMPLATE_FILE="$TEMPLATES_DIR/spa-compatible.user.js"
        ;;
    *)
        echo -e "${RED}Error: Invalid template '$TEMPLATE'${NC}"
        echo "Available templates: basic, advanced, spa"
        exit 1
        ;;
esac

# Check if template exists
if [ ! -f "$TEMPLATE_FILE" ]; then
    echo -e "${RED}Error: Template file not found: $TEMPLATE_FILE${NC}"
    exit 1
fi

# Output filename
OUTPUT_FILE="${SCRIPT_NAME}.user.js"

# Check if output file already exists
if [ -f "$OUTPUT_FILE" ]; then
    echo -e "${YELLOW}Warning: $OUTPUT_FILE already exists${NC}"
    read -p "Overwrite? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 0
    fi
fi

# Extract domain from URL for favicon
DOMAIN=$(echo "$TARGET_URL" | sed -E 's|https?://([^/]+).*|\1|' | sed 's/\*/example.com/')

# Generate script from template
echo -e "${GREEN}Generating userscript...${NC}"

# Convert script name to title case
SCRIPT_TITLE=$(echo "$SCRIPT_NAME" | sed 's/-/ /g' | sed 's/\b\(.\)/\u\1/g')

# Copy template and replace placeholders
cp "$TEMPLATE_FILE" "$OUTPUT_FILE"

# Replace metadata
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    sed -i '' "s|@name.*|@name         $SCRIPT_TITLE|" "$OUTPUT_FILE"
    sed -i '' "s|@match.*|@match        $TARGET_URL|" "$OUTPUT_FILE"
    sed -i '' "s|@icon.*|@icon         https://www.google.com/s2/favicons?sz=64\&domain=$DOMAIN|" "$OUTPUT_FILE"
    sed -i '' "s|My Userscript|$SCRIPT_TITLE|g" "$OUTPUT_FILE"
    sed -i '' "s|Advanced Userscript Template|$SCRIPT_TITLE|g" "$OUTPUT_FILE"
    sed -i '' "s|SPA-Compatible Template|$SCRIPT_TITLE|g" "$OUTPUT_FILE"
else
    # Linux
    sed -i "s|@name.*|@name         $SCRIPT_TITLE|" "$OUTPUT_FILE"
    sed -i "s|@match.*|@match        $TARGET_URL|" "$OUTPUT_FILE"
    sed -i "s|@icon.*|@icon         https://www.google.com/s2/favicons?sz=64\&domain=$DOMAIN|" "$OUTPUT_FILE"
    sed -i "s|My Userscript|$SCRIPT_TITLE|g" "$OUTPUT_FILE"
    sed -i "s|Advanced Userscript Template|$SCRIPT_TITLE|g" "$OUTPUT_FILE"
    sed -i "s|SPA-Compatible Template|$SCRIPT_TITLE|g" "$OUTPUT_FILE"
fi

echo -e "${GREEN}✓ Successfully generated: $OUTPUT_FILE${NC}"
echo ""
echo "Template used: $TEMPLATE"
echo "Script name: $SCRIPT_TITLE"
echo "Target URL: $TARGET_URL"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Edit $OUTPUT_FILE to add your custom logic"
echo "2. Install in Tampermonkey"
echo "3. Test on $TARGET_URL"
echo ""
echo "To validate your script:"
echo "  bash scripts/validate-userscript.sh $OUTPUT_FILE"
