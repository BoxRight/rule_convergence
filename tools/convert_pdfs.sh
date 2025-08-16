#!/bin/bash

# PDF to Text Conversion Script
# Converts all PDF files in PDFs/ directory to text files in texts/ directory

echo "Starting PDF to text conversion..."

# Create texts directory if it doesn't exist
mkdir -p texts

# Counter for tracking progress
count=0
total=$(ls PDFs/*.pdf 2>/dev/null | wc -l)

if [ $total -eq 0 ]; then
    echo "No PDF files found in PDFs/ directory"
    exit 1
fi

echo "Found $total PDF files to convert"

# Convert each PDF file
for pdf_file in PDFs/*.pdf; do
    if [ -f "$pdf_file" ]; then
        # Extract filename without path and extension
        filename=$(basename "$pdf_file" .pdf)
        
        # Convert to lowercase for consistency
        text_file="texts/${filename,,}.txt"
        
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
ls -la texts/

echo ""
echo "You can now analyze the text files and create .wit models in the models/ directory" 