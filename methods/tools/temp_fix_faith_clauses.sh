#!/bin/bash

# Replace all complex faith exclusivity clauses with simplified XOR version
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
WIT="$REPO_ROOT/methods/analysis/unified_legal_conclusions.wit"
sed -i 's/clause \(tesis[0-9]*_exclusividad_fe\) = claim(demanda_prescripcion) IMPLIES (oblig(ejercicio_buena_fe) XOR oblig(ejercicio_mala_fe));/clause \1 = oblig(ejercicio_buena_fe) XOR oblig(ejercicio_mala_fe);/g' "$WIT"

echo "Updated all faith exclusivity clauses to simplified XOR format" 