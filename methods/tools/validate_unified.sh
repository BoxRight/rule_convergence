#!/bin/bash

# Validate Unified Model — runs Witness from results/zdd so solver artifacts stay under results/

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

UNIFIED_FILE="$REPO_ROOT/methods/analysis/unified_legal_conclusions.wit"
WITNESSC="$REPO_ROOT/methods/witness/witnessc"
OUT_DIR="$REPO_ROOT/results/zdd"

if [ ! -f "$UNIFIED_FILE" ]; then
    echo "Error: Unified file $UNIFIED_FILE not found"
    exit 1
fi

mkdir -p "$OUT_DIR"
# CUDA solver is invoked as ./tree_fold_cuda from current working directory
if [ ! -e "$OUT_DIR/tree_fold_cuda" ]; then
    ln -sf ../../methods/witness/tree_fold_cuda "$OUT_DIR/tree_fold_cuda"
fi

echo "Validating unified legal conclusions model..."
echo "=============================================="

echo "1. Testing compilation (cwd: $OUT_DIR)..."
cd "$OUT_DIR"
if "$WITNESSC" --solver=external --quiet "$UNIFIED_FILE" > /dev/null 2>&1; then
    echo "   ✓ Model compiles successfully"
else
    echo "   ✗ Compilation failed"
    "$WITNESSC" --solver=external "$UNIFIED_FILE"
    exit 1
fi

echo ""
echo "2. Analyzing structure..."
THESIS_COUNT=$(grep -c "// THESIS [0-9]" "$UNIFIED_FILE")
echo "   Thesis sections found: $THESIS_COUNT"

echo ""
echo "3. Thesis sections:"
grep "// THESIS [0-9]" "$UNIFIED_FILE" | sed 's/^/   /'

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

echo ""
echo "5. Checking for incomplete sections..."
PLACEHOLDERS=$(grep -c "\[.*\]" "$UNIFIED_FILE")
if [ "$PLACEHOLDERS" -gt 0 ]; then
    echo "   ⚠ Warning: $PLACEHOLDERS placeholders found"
    echo "   Incomplete sections:"
    grep -n "\[.*\]" "$UNIFIED_FILE" | sed 's/^/     /'
else
    echo "   ✓ No placeholders found - all sections complete"
fi

echo ""
echo "6. Validation points:"
GLOBAL_COUNT=$(grep -c "global()" "$UNIFIED_FILE")
echo "   Global validations: $GLOBAL_COUNT"

echo ""
echo "=============================================="
echo "Validation complete"

if [ "$PLACEHOLDERS" -gt 0 ]; then
    echo "⚠ Model has incomplete sections - fill placeholders before analysis"
    exit 1
else
    echo "✓ Model is ready for comparative analysis"
    exit 0
fi
