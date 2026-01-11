#!/bin/bash

# ==============================================================================
# Tampermonkey Userscript Validator
# ==============================================================================
# Validates userscripts for common issues and best practices
#
# Usage:
#   bash validate-userscript.sh <script-file>
#
# Checks:
#   - Required metadata fields
#   - Common anti-patterns
#   - Performance issues
#   - Security concerns
# ==============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_FILE="$1"
ERRORS=0
WARNINGS=0

if [ -z "$SCRIPT_FILE" ]; then
    echo -e "${RED}Error: No script file specified${NC}"
    echo "Usage: bash validate-userscript.sh <script-file>"
    exit 1
fi

if [ ! -f "$SCRIPT_FILE" ]; then
    echo -e "${RED}Error: File not found: $SCRIPT_FILE${NC}"
    exit 1
fi

echo -e "${BLUE}=== Validating Userscript ===${NC}"
echo "File: $SCRIPT_FILE"
echo ""

# ==============================================================================
# Check 1: Required Metadata
# ==============================================================================
echo -e "${BLUE}[1] Checking required metadata...${NC}"

required_fields=("@name" "@version" "@match")
for field in "${required_fields[@]}"; do
    if ! grep -q "^// $field" "$SCRIPT_FILE"; then
        echo -e "${RED}✗ Missing required field: $field${NC}"
        ((ERRORS++))
    else
        echo -e "${GREEN}✓ Found $field${NC}"
    fi
done

# ==============================================================================
# Check 2: Grant Declarations
# ==============================================================================
echo ""
echo -e "${BLUE}[2] Checking @grant declarations...${NC}"

# Check if using GM functions without grant
gm_functions=("GM_setValue" "GM_getValue" "GM_xmlhttpRequest" "GM_addStyle" "GM_notification" "GM_setClipboard" "GM_openInTab")

for func in "${gm_functions[@]}"; do
    if grep -q "$func" "$SCRIPT_FILE"; then
        grant_line="@grant        $func"
        if ! grep -q "$grant_line" "$SCRIPT_FILE"; then
            echo -e "${RED}✗ Using $func without @grant declaration${NC}"
            ((ERRORS++))
        fi
    fi
done

# Check for unsafeWindow
if grep -q "unsafeWindow" "$SCRIPT_FILE"; then
    if ! grep -q "@grant.*unsafeWindow" "$SCRIPT_FILE"; then
        echo -e "${YELLOW}⚠ Using unsafeWindow without @grant declaration${NC}"
        ((WARNINGS++))
    fi
fi

echo -e "${GREEN}✓ Grant declarations check complete${NC}"

# ==============================================================================
# Check 3: Performance Anti-Patterns
# ==============================================================================
echo ""
echo -e "${BLUE}[3] Checking for performance anti-patterns...${NC}"

# Check for querySelector in loops
if grep -E 'for.*querySelector|while.*querySelector' "$SCRIPT_FILE"; then
    echo -e "${YELLOW}⚠ querySelector in loop detected - consider caching results${NC}"
    ((WARNINGS++))
fi

# Check for setInterval without clear
if grep -q "setInterval" "$SCRIPT_FILE" && ! grep -q "clearInterval" "$SCRIPT_FILE"; then
    echo -e "${YELLOW}⚠ setInterval used without clearInterval - potential memory leak${NC}"
    ((WARNINGS++))
fi

# Check for addEventListener without cleanup
if grep -q "addEventListener" "$SCRIPT_FILE" && ! grep -q "removeEventListener" "$SCRIPT_FILE"; then
    echo -e "${YELLOW}⚠ addEventListener used without cleanup - check if removeEventListener needed${NC}"
    ((WARNINGS++))
fi

echo -e "${GREEN}✓ Performance check complete${NC}"

# ==============================================================================
# Check 4: Security Issues
# ==============================================================================
echo ""
echo -e "${BLUE}[4] Checking for security issues...${NC}"

# Check for eval
if grep -q "eval(" "$SCRIPT_FILE"; then
    echo -e "${RED}✗ Using eval() - security risk!${NC}"
    ((ERRORS++))
fi

# Check for innerHTML with variables
if grep -E '\.innerHTML\s*=.*[\+\$]' "$SCRIPT_FILE"; then
    echo -e "${YELLOW}⚠ Using innerHTML with variables - potential XSS risk${NC}"
    ((WARNINGS++))
fi

# Check for document.write
if grep -q "document.write" "$SCRIPT_FILE"; then
    echo -e "${YELLOW}⚠ Using document.write - can cause issues in modern browsers${NC}"
    ((WARNINGS++))
fi

echo -e "${GREEN}✓ Security check complete${NC}"

# ==============================================================================
# Check 5: Best Practices
# ==============================================================================
echo ""
echo -e "${BLUE}[5] Checking best practices...${NC}"

# Check for strict mode
if ! grep -q "'use strict'" "$SCRIPT_FILE" && ! grep -q '"use strict"' "$SCRIPT_FILE"; then
    echo -e "${YELLOW}⚠ Missing 'use strict' declaration${NC}"
    ((WARNINGS++))
fi

# Check for IIFE
if ! grep -q "(function()" "$SCRIPT_FILE" && ! grep -q "(() => {" "$SCRIPT_FILE"; then
    echo -e "${YELLOW}⚠ Not wrapped in IIFE - may pollute global scope${NC}"
    ((WARNINGS++))
fi

# Check for console.log (should be prefixed or removed in production)
log_count=$(grep -c "console.log" "$SCRIPT_FILE" || true)
if [ "$log_count" -gt 5 ]; then
    echo -e "${YELLOW}⚠ Found $log_count console.log statements - consider removing or reducing${NC}"
    ((WARNINGS++))
fi

echo -e "${GREEN}✓ Best practices check complete${NC}"

# ==============================================================================
# Summary
# ==============================================================================
echo ""
echo -e "${BLUE}=== Validation Summary ===${NC}"
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✓ No issues found! Script looks good.${NC}"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠ $WARNINGS warning(s) found${NC}"
    echo "Consider addressing warnings for better code quality."
    exit 0
else
    echo -e "${RED}✗ $ERRORS error(s) found${NC}"
    echo -e "${YELLOW}⚠ $WARNINGS warning(s) found${NC}"
    echo ""
    echo "Please fix errors before deploying your userscript."
    exit 1
fi
