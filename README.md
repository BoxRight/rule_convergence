# Rule Convergence: Legal Thesis Analysis

A principled approach to modeling Mexican Supreme Court legal conclusions using formal logic.

## 📁 Project Structure

```
rule_convergence/
├── PDFs/          # Original thesis PDF files (11 files)
├── texts/         # Converted text files
├── models/        # Individual .wit models (deprecated - use unified)
├── analysis/      # Unified analysis
│   └── unified_legal_conclusions.wit  # Main model file
├── tools/         # Automation scripts
├── tests/         # Test cases
└── README.md      # This file
```

## 🎯 Principled Modeling Approach

### Core Principles

1. **Reusable Assets**: All thesis models share the same foundational legal concepts
2. **Consistent Structure**: Each thesis follows the same logical pattern
3. **Unified Model**: All conclusions in one file, separated by `global()` operations
4. **Comparative Analysis**: Enables cross-thesis pattern identification

### Shared Foundation

The unified model defines reusable components:

- **Objects**: `inmueble`, `contrato_compraventa`, `titulo_propiedad`, etc.
- **Services**: `posesion_legal`, `inscripcion_registral`, `oponibilidad`, etc.
- **Subjects**: `demandante`, `titular_registral`, `tercero`, `tribunal`, etc.
- **Actions**: `poseer_como_propietario`, `estar_inscrito_registro`, etc.
- **Assets**: `titularidad_registral`, `contrato_no_inscrito`, etc.

### Thesis-Specific Sections

Each thesis adds only:
- Specific legal clauses using shared assets
- Unique logical relationships
- `global()` validation point

## 🛠️ Workflow Tools

### 1. PDF Conversion
```bash
./tools/convert_pdfs.sh
```
Converts all PDFs in `PDFs/` to text files in `texts/`

### 2. Add New Thesis
```bash
./tools/add_thesis_to_unified.sh 2021246 "Contract Interpretation"
```
Adds a new thesis section to the unified model

### 3. Validate Model
```bash
./tools/validate_unified.sh
```
Tests compilation and reports structure statistics

## 📊 Current Status

- ✅ **11 PDF files** converted to text
- ✅ **Unified model structure** established
- ✅ **Thesis 2020418** modeled (adverse possession)
- ⏳ **10 remaining thesis** to be modeled

## 🔄 Adding New Thesis Models

### Step-by-Step Process

1. **Add thesis section**:
   ```bash
   ./tools/add_thesis_to_unified.sh 2021246 "Your Thesis Title"
   ```

2. **Read the text file**:
   ```bash
   cat texts/tesis2021246.txt
   ```

3. **Edit the unified model**:
   ```bash
   nano analysis/unified_legal_conclusions.wit
   ```

4. **Replace placeholders** with actual legal logic using shared assets

5. **Validate**:
   ```bash
   ./tools/validate_unified.sh
   ```

### Template Structure

Each thesis section follows this pattern:

```wit
// ==========================================
// THESIS XXXXXX: TITLE
// ==========================================

// Main legal principle
clause tesisXXXXXX_principio_fundamental = [LOGIC_USING_SHARED_ASSETS];

// Supporting rules (as needed)
clause tesisXXXXXX_regla_secundaria = [SUPPORTING_LOGIC];

// Validation
asset tesisXXXXXX_valida = global();
```

## 🎯 Benefits of This Approach

1. **Consistency**: All models use the same vocabulary and structure
2. **Comparability**: Easy to identify patterns across different legal conclusions
3. **Maintainability**: Changes to shared concepts propagate automatically
4. **Scalability**: Adding new thesis models is standardized
5. **Analysis-Ready**: Structure enables automated comparative analysis

## 📈 Future Analysis

Once all thesis models are complete, the unified structure will enable:

- **Rule convergence identification**
- **Legal principle evolution tracking**
- **Pattern analysis across different legal domains**
- **Automated consistency checking**

## 🔧 Technical Notes

- Uses `.wit` domain-specific language for legal modeling
- Compiled with `witnessc` solver
- Each `global()` operation creates a validation checkpoint
- Shared assets prevent duplication and ensure consistency 