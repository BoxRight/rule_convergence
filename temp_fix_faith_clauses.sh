#!/bin/bash

# Replace all complex faith exclusivity clauses with simplified XOR version
sed -i 's/clause \(tesis[0-9]*_exclusividad_fe\) = claim(demanda_prescripcion) IMPLIES (oblig(ejercicio_buena_fe) XOR oblig(ejercicio_mala_fe));/clause \1 = oblig(ejercicio_buena_fe) XOR oblig(ejercicio_mala_fe);/g' analysis/unified_legal_conclusions.wit

echo "Updated all faith exclusivity clauses to simplified XOR format" 