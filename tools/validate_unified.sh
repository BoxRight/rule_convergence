#!/bin/bash

# Validate Unified Model
# Tests the unified legal conclusions file and reports on structure

UNIFIED_FILE="analysis/unified_legal_conclusions.wit"

if [ ! -f "$UNIFIED_FILE" ]; then
    echo "Error: Unified file $UNIFIED_FILE not found"
    exit 1
fi

echo "Validating unified legal conclusions model..."
echo "=============================================="

# Test compilation
echo "1. Testing compilation..."
if ./witnessc --solver=external --quiet "$UNIFIED_FILE" > /dev/null 2>&1; then
    echo "   ✓ Model compiles successfully"
else
    echo "   ✗ Compilation failed"
    echo "   Running with verbose output:"
    ./witnessc --solver=external "$UNIFIED_FILE"
    exit 1
fi

# Count thesis sections
echo ""
echo "2. Analyzing structure..."
THESIS_COUNT=$(grep -c "// THESIS [0-9]" "$UNIFIED_FILE")
echo "   Thesis sections found: $THESIS_COUNT"

# List thesis sections
echo ""
echo "3. Thesis sections:"
grep "// THESIS [0-9]" "$UNIFIED_FILE" | sed 's/^/   /'

# Count shared assets
echo ""
echo "4. Shared foundation:"
OBJECTS_COUNT=$(grep -c "^object " "$UNIFIED_FILE")
SERVICES_COUNT=$(grep -c "^service " "$UNIFIED_FILE")
SUBJECTS_COUNT=$(grep -c "^subject " "$UNIFIED_FILE")
ACTIONS_COUNT=$(grep -c "^action " "$UNIFIED_FILE")
ASSETS_COUNT=$(grep -c "^asset " "$UNIFIED_FILE")

echo "   Objects: $OBJECTS_COUNT"
echo "   Services: $SERVICES_COUNT"
echo "   Subjects: $SUBJECTS_COUNT"
echo "   Actions: $ACTIONS_COUNT"
echo "   Assets: $ASSETS_COUNT"

# Check for placeholders
echo ""
echo "5. Checking for incomplete sections..."
PLACEHOLDERS=$(grep -c "\[.*\]" "$UNIFIED_FILE")
if [ $PLACEHOLDERS -gt 0 ]; then
    echo "   ⚠ Warning: $PLACEHOLDERS placeholders found"
    echo "   Incomplete sections:"
    grep -n "\[.*\]" "$UNIFIED_FILE" | sed 's/^/     /'
else
    echo "   ✓ No placeholders found - all sections complete"
fi

# Count global validations
echo ""
echo "6. Validation points:"
GLOBAL_COUNT=$(grep -c "global()" "$UNIFIED_FILE")
echo "   Global validations: $GLOBAL_COUNT"

echo ""
echo "=============================================="
echo "Validation complete"

if [ $PLACEHOLDERS -gt 0 ]; then
    echo "⚠ Model has incomplete sections - fill placeholders before analysis"
    exit 1
else
    echo "✓ Model is ready for comparative analysis"
    exit 0
fi 