#!/bin/bash

# Rule Convergence Analysis Tool
# Wrapper script for analyzing ZDD files and generating cross-thesis pattern analysis

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ANALYZER="$SCRIPT_DIR/zdd_analysis.py"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}Rule Convergence Analysis Tool${NC}"
echo "======================================"

# Check if Python script exists
if [[ ! -f "$ANALYZER" ]]; then
    echo -e "${RED}Error: ZDD analyzer script not found at $ANALYZER${NC}"
    exit 1
fi

# Change to project root
cd "$PROJECT_ROOT" || exit 1

# Check for ZDD files
ZDD_COUNT=$(find . -name "zdd_*.bin" -type f | wc -l)

if [[ $ZDD_COUNT -eq 0 ]]; then
    echo -e "${RED}No ZDD binary files found in project directory${NC}"
    echo "Make sure to run witnessc on your .wit files first to generate ZDD files"
    exit 1
fi

echo -e "${GREEN}Found $ZDD_COUNT ZDD binary files${NC}"
echo

# Run the analysis
echo "Analyzing ZDD files for rule convergence patterns..."
python3 "$ANALYZER" .

# Check if analysis was successful
if [[ $? -eq 0 ]]; then
    echo
    echo -e "${YELLOW}Analysis Results Summary:${NC}"
    echo "========================"
    echo "• Output directory: analysis/zdd_analysis/"
    echo "• Generated CSV files:"
    echo "  - zdd_summary.csv (ZDD-level statistics)"
    echo "  - array_patterns.csv (cross-ZDD pattern repetitions)"
    echo "  - variable_frequency.csv (legal concept frequency)"
    echo "  - co_occurrence_matrix.csv (concept co-occurrence)"
    
    # Show file sizes
    echo
    echo "Generated analysis files:"
    ls -lh analysis/zdd_analysis/*.csv 2>/dev/null | awk '{print "  " $9 " (" $5 ")"}'
    
    echo
    echo -e "${GREEN}Key Insights for Rule Convergence:${NC}"
    echo "=================================="
    
    # Extract key insights from variable_frequency.csv
    if [[ -f "analysis/zdd_analysis/variable_frequency.csv" ]]; then
        echo "Most Universal Legal Concepts (present in most thesis):"
        tail -n +2 analysis/zdd_analysis/variable_frequency.csv | head -5 | while IFS=',' read -r var_id total_occ zdd_count array_count zdds_present freq_pct; do
            echo "  • Variable $var_id: appears in $zdd_count/$ZDD_COUNT thesis ($freq_pct%)"
        done
    fi
    
    echo
    
    # Extract key insights from array_patterns.csv
    if [[ -f "analysis/zdd_analysis/array_patterns.csv" ]]; then
        echo "Most Common Cross-Thesis Patterns:"
        tail -n +2 analysis/zdd_analysis/array_patterns.csv | head -3 | while IFS=',' read -r signature frequency zdds first_seen length elements; do
            echo "  • Pattern $signature: appears $frequency times across thesis $zdds"
        done
    fi
    
    echo
    echo -e "${BLUE}Next Steps:${NC}"
    echo "• Import CSV files into your preferred analysis tool (R, Python, Excel)"
    echo "• Use array_patterns.csv to identify convergent legal principles"
    echo "• Use variable_frequency.csv to find core legal concepts"
    echo "• Use co_occurrence_matrix.csv to discover concept dependencies"
    
else
    echo -e "${RED}Analysis failed. Check error messages above.${NC}"
    exit 1
fi

echo
echo -e "${GREEN}✓ Rule convergence analysis complete${NC}" 