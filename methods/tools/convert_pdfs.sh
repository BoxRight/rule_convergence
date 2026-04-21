#!/bin/bash

# PDF to Text Conversion Script
# Converts all PDF files in materials/PDFs/ to materials/texts/

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

PDF_DIR="$REPO_ROOT/materials/PDFs"
TEXT_DIR="$REPO_ROOT/materials/texts"

echo "Starting PDF to text conversion..."

mkdir -p "$TEXT_DIR"

count=0
total=$(ls "$PDF_DIR"/*.pdf 2>/dev/null | wc -l)

if [ "$total" -eq 0 ]; then
    echo "No PDF files found in $PDF_DIR/"
    exit 1
fi

echo "Found $total PDF files to convert"

for pdf_file in "$PDF_DIR"/*.pdf; do
    if [ -f "$pdf_file" ]; then
        # Extract filename without path and extension
        filename=$(basename "$pdf_file" .pdf)
        
        # Convert to lowercase for consistency
        text_file="$TEXT_DIR/${filename,,}.txt"
        
        echo "Converting: $pdf_file -> $text_file"
        
        # Use pdftotext to convert PDF to text
        # -layout preserves layout, -enc UTF-8 ensures proper encoding
        pdftotext -layout -enc UTF-8 "$pdf_file" "$text_file"
        
        if [ $? -eq 0 ]; then
            ((count++))
            echo "  ✓ Success ($count/$total)"
        else
            echo "  ✗ Failed to convert $pdf_file"
        fi
    fi
done

echo ""
echo "Conversion complete: $count/$total files converted successfully"

# List the converted files
echo ""
echo "Converted text files:"
ls -la "$TEXT_DIR"

echo ""
echo "You can now analyze the text files and extend methods/analysis/unified_legal_conclusions.wit" 