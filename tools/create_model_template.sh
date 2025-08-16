#!/bin/bash

# Model Template Generator
# Creates a .wit model template for a given thesis text file

if [ $# -ne 1 ]; then
    echo "Usage: $0 <thesis_number>"
    echo "Example: $0 2020418"
    exit 1
fi

THESIS_NUM=$1
TEXT_FILE="texts/tesis${THESIS_NUM,,}.txt"
MODEL_FILE="models/tesis${THESIS_NUM,,}_conclusion.wit"

# Check if text file exists
if [ ! -f "$TEXT_FILE" ]; then
    echo "Error: Text file $TEXT_FILE not found"
    echo "Available text files:"
    ls texts/
    exit 1
fi

# Check if model already exists
if [ -f "$MODEL_FILE" ]; then
    echo "Warning: Model file $MODEL_FILE already exists"
    read -p "Overwrite? (y/N): " confirm
    if [[ ! $confirm =~ ^[Yy]$ ]]; then
        echo "Aborted"
        exit 1
    fi
fi

echo "Creating model template for Tesis $THESIS_NUM..."

# Create the template
cat > "$MODEL_FILE" << EOF
// ==========================================
// LEGAL CONCLUSION: TESIS $THESIS_NUM
// Abstract principle from Mexican Supreme Court
// ==========================================

// ==========================================
// CORE LEGAL CONCEPTS
// ==========================================

// Legal objects
object [DEFINE_OBJECT] = "[DESCRIPTION]", [movable/immovable];

// Legal services  
service [DEFINE_SERVICE] = "[DESCRIPTION]", positive;

// ==========================================
// LEGAL SUBJECTS
// ==========================================

subject [DEFINE_SUBJECT1] = "[DESCRIPTION]";
subject [DEFINE_SUBJECT2] = "[DESCRIPTION]";

// ==========================================
// FUNDAMENTAL ACTIONS
// ==========================================

action [DEFINE_ACTION] = "[DESCRIPTION]", [SERVICE];

// ==========================================
// CORE LEGAL ASSETS
// ==========================================

// [DESCRIPTION]
asset [ASSET_NAME] = [SUBJECT], [ACTION], [TARGET_SUBJECT];

// ==========================================
// FUNDAMENTAL LEGAL PRINCIPLE
// ==========================================

// Core conclusion: [DESCRIBE THE MAIN LEGAL RULE]
clause principio_fundamental = [LOGICAL_EXPRESSION];

// ==========================================
// VALIDATION
// ==========================================

asset conclusion_legal_valida = global();
EOF

echo "Template created: $MODEL_FILE"
echo ""
echo "Next steps:"
echo "1. Read the text file: $TEXT_FILE"
echo "2. Identify the core legal principle"
echo "3. Fill in the template placeholders"
echo "4. Test with: ./witnessc --solver=external --quiet $MODEL_FILE"
echo ""
echo "Template placeholders to replace:"
echo "- [DEFINE_OBJECT], [DEFINE_SERVICE], [DEFINE_SUBJECT1/2], [DEFINE_ACTION]"
echo "- [DESCRIPTION] fields"
echo "- [ASSET_NAME], [LOGICAL_EXPRESSION]" 