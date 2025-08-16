#!/bin/bash

# Add Thesis to Unified Model
# Adds a new thesis section to the unified legal conclusions file

if [ $# -ne 2 ]; then
    echo "Usage: $0 <thesis_number> <thesis_title>"
    echo "Example: $0 2021246 'Contract Interpretation and Good Faith'"
    exit 1
fi

THESIS_NUM=$1
THESIS_TITLE=$2
TEXT_FILE="texts/tesis${THESIS_NUM,,}.txt"
UNIFIED_FILE="analysis/unified_legal_conclusions.wit"

# Check if text file exists
if [ ! -f "$TEXT_FILE" ]; then
    echo "Error: Text file $TEXT_FILE not found"
    echo "Available text files:"
    ls texts/
    exit 1
fi

# Check if unified file exists
if [ ! -f "$UNIFIED_FILE" ]; then
    echo "Error: Unified file $UNIFIED_FILE not found"
    echo "Please ensure the unified model file exists"
    exit 1
fi

# Check if thesis already exists in unified file
if grep -q "THESIS $THESIS_NUM:" "$UNIFIED_FILE"; then
    echo "Warning: Thesis $THESIS_NUM already exists in unified file"
    read -p "Continue anyway? (y/N): " confirm
    if [[ ! $confirm =~ ^[Yy]$ ]]; then
        echo "Aborted"
        exit 1
    fi
fi

echo "Adding Thesis $THESIS_NUM to unified model..."

# Create temporary file with new thesis section
TEMP_SECTION=$(mktemp)

cat > "$TEMP_SECTION" << EOF

// ==========================================
// THESIS $THESIS_NUM: $THESIS_TITLE
// ==========================================

// Thesis-specific principle: [DESCRIBE THE MAIN LEGAL RULE]
clause tesis${THESIS_NUM,,}_principio_fundamental = [LOGICAL_EXPRESSION_USING_SHARED_ASSETS];

// Supporting legal logic (add as needed)
clause tesis${THESIS_NUM,,}_regla_secundaria = [SUPPORTING_LOGIC];

// Additional thesis-specific assets (only if shared assets are insufficient)
// asset tesis${THESIS_NUM,,}_asset_especifico = [SUBJECT], [ACTION], [TARGET];

// Thesis validation
asset tesis${THESIS_NUM,,}_valida = global();
EOF

# Find the insertion point (before the template section)
INSERTION_LINE=$(grep -n "// THESIS \[NEXT\]:" "$UNIFIED_FILE" | cut -d: -f1)

if [ -z "$INSERTION_LINE" ]; then
    echo "Error: Could not find insertion point in unified file"
    rm "$TEMP_SECTION"
    exit 1
fi

# Insert the new section
head -n $((INSERTION_LINE - 1)) "$UNIFIED_FILE" > "${UNIFIED_FILE}.tmp"
cat "$TEMP_SECTION" >> "${UNIFIED_FILE}.tmp"
tail -n +$INSERTION_LINE "$UNIFIED_FILE" >> "${UNIFIED_FILE}.tmp"

# Replace the original file
mv "${UNIFIED_FILE}.tmp" "$UNIFIED_FILE"
rm "$TEMP_SECTION"

echo "✓ Thesis $THESIS_NUM section added to unified model"
echo ""
echo "Next steps:"
echo "1. Read the text file: $TEXT_FILE"
echo "2. Edit the unified file: $UNIFIED_FILE"
echo "3. Replace placeholders:"
echo "   - [DESCRIBE THE MAIN LEGAL RULE]"
echo "   - [LOGICAL_EXPRESSION_USING_SHARED_ASSETS]"
echo "   - [SUPPORTING_LOGIC] (if needed)"
echo "4. Test with: ./witnessc --solver=external --quiet $UNIFIED_FILE"
echo ""
echo "Available shared assets to use:"
echo "  Objects: inmueble, contrato_compraventa, titulo_propiedad, etc."
echo "  Services: posesion_legal, inscripcion_registral, oponibilidad, etc."
echo "  Subjects: demandante, titular_registral, tercero, tribunal, etc."
echo "  Assets: titularidad_registral, contrato_no_inscrito, demanda_prescripcion, etc." 