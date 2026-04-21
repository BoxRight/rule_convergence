#!/bin/bash

# Rule Convergence Analysis Tool
# Wrapper script for analyzing ZDD files and generating cross-thesis pattern analysis

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
ANALYZER="$SCRIPT_DIR/zdd_to_csv_correct.py"
ZDD_DIR="$REPO_ROOT/results/zdd"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}Rule Convergence Analysis Tool${NC}"
echo "======================================"

if [[ ! -f "$ANALYZER" ]]; then
    echo -e "${RED}Error: ZDD analyzer script not found at $ANALYZER${NC}"
    exit 1
fi

cd "$REPO_ROOT" || exit 1

ZDD_COUNT=$(find "$ZDD_DIR" -maxdepth 1 -name "zdd_*.bin" -type f 2>/dev/null | wc -l)

if [[ $ZDD_COUNT -eq 0 ]]; then
    echo -e "${RED}No ZDD binary files found in $ZDD_DIR${NC}"
    echo "Run methods/tools/validate_unified.sh (or witnessc from results/zdd) first."
    exit 1
fi

echo -e "${GREEN}Found $ZDD_COUNT ZDD binary files in results/zdd/${NC}"
echo

echo "Analyzing ZDD files for rule convergence patterns..."
python3 "$ANALYZER" "$ZDD_DIR"

# Check if analysis was successful
if [[ $? -eq 0 ]]; then
    echo
    echo -e "${YELLOW}Analysis Results Summary:${NC}"
    echo "========================"
    echo "• Output directory: results/analysis/zdd_correct_analysis/"
    echo "• Generated CSV files:"
    echo "  - all_arrays_complete_correct.csv"
    echo "  - arrays_summary_correct.csv"
    echo "  - pattern_analysis_correct.csv"
    
    echo
    echo "Generated analysis files:"
    ls -lh "$REPO_ROOT/results/analysis/zdd_correct_analysis/"*.csv 2>/dev/null | awk '{print "  " $9 " (" $5 ")"}'
    
    echo
    echo -e "${BLUE}Next Steps:${NC}"
    echo "• Import CSV files into your preferred analysis tool (R, Python, Excel)"
    echo "• Use pattern_analysis_correct.csv for cross-ZDD pattern frequencies"
    
else
    echo -e "${RED}Analysis failed. Check error messages above.${NC}"
    exit 1
fi

echo
echo -e "${GREEN}✓ Rule convergence analysis complete${NC}" 