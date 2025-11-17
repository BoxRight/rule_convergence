# Evaluation Criteria for WIT Clauses

**Evaluator**: Claude Sonnet 4.5 (Evaluator 1)  
**Date**: November 2025  
**Task**: Evaluate whether WIT (Web Ontology Language for Legal Knowledge) clauses accurately model Mexican legal thesis texts on adverse possession (usucapión).

---

## Rating Scale

### ✓ ACCEPT
The clause **accurately captures** the legal principle from the source thesis.

**Criteria:**
- The logical structure (implications, conjunctions, negations) correctly models the legal reasoning
- All essential elements from the thesis are present
- The predicates (obligations, claims, etc.) match the source meaning
- No significant omissions or additions
- Minor stylistic variations acceptable if logically equivalent

**Example:**
- Source: "Knowledge of INFONAVIT mortgage does not vitiate just title"
- Clause: `oblig(conocimiento_hipoteca_infonavit) IMPLIES oblig(causa_generadora_probada)`
- Rating: **ACCEPT** - correctly captures that mortgage knowledge doesn't destroy title validity

---

### ⚠ REVISE
The clause has **issues that need correction** but captures some correct elements.

**Criteria for "revise":**

1. **Oversimplification**: Omits necessary conditions or qualifications
   - Example: States `A IMPLIES B` when source requires `A AND C IMPLIES B`

2. **Overgeneralization**: Claims broader than source supports
   - Example: "All legal exercise is good faith" when source only says "typically" or "in agrarian context"

3. **Incomplete Logic**: Missing essential conjuncts or disjuncts
   - Example: Thesis gives dual reasoning (X OR Y) but clause only models X

4. **Unnecessary Complexity**: Logically equivalent but could be clearer
   - Example: Using triple nested negations when simpler form exists
   - **Note**: Double negatives like `not(not(X))` are acceptable - they're logically equivalent to X

5. **Ambiguous Predicates**: Uses unclear or overly abstract terms not directly traceable to source

6. **Wrong Operator**: Uses AND when should be OR, or vice versa

7. **Temporal Issues**: Doesn't capture timing/sequencing that source emphasizes

**Example:**
- Source: "Adverse possession fails because BOTH lack of opposability AND owner has perfect title"
- Clause: `not(oblig(contrato_inscrito)) IMPLIES not(oblig(prescripcion_procedente))`
- Rating: **REVISE** - only captures one reason, omits perfect title requirement

---

### ✗ REJECT
The clause is **logically incorrect** or **contradicts** the source.

**Criteria for "reject":**

1. **Logical Contradiction**: The clause states something that contradicts itself or the source
   - Example: `oblig(buena_fe) AND oblig(reconocimiento) IMPLIES oblig(mala_fe)` (good faith implies bad faith - nonsensical)

2. **Wrong Direction**: Reverses the implication
   - Example: Source says "no title → no possession" but clause says "no possession → no title"

3. **Factually Wrong**: Misrepresents the legal holding
   - Example: Source says "10 years for good faith" but clause models 30 years

4. **Missing Critical Element**: Omits the core legal principle entirely
   - Example: Thesis about "proof requirements" but clause doesn't mention proof at all

5. **Invents Requirements**: Adds conditions not in source
   - Example: Source has no temporal requirement but clause adds one

6. **Category Error**: Confuses different legal concepts
   - Example: Treats "nullity" as equivalent to "voidability"

**Example:**
- Source: "Recognition interrupts possession, ending good faith period"
- Clause: `oblig(ejercicio_buena_fe) AND oblig(reconocimiento) IMPLIES oblig(ejercicio_mala_fe)`
- Rating: **REJECT** - logically states good faith implies bad faith (contradiction)

---

## Evaluation Process

### 1. Read Source Thesis
- Identify the core legal principle (*principio fundamental*)
- Note all supporting reasoning and qualifications
- Extract key legal requirements, exceptions, and conditions

### 2. Analyze WIT Clause
- Parse the logical structure (operators: AND, OR, IMPLIES, NOT)
- Identify predicates and their meanings
- Map to source text elements

### 3. Compare
- Does the clause capture the principle? (Yes → Accept/Revise, No → Reject)
- Are all essential conditions present? (Missing → Revise)
- Are there logical errors? (Yes → Reject, Minor → Revise)
- Is it unnecessarily complex? (Yes → Revise if significantly harder to parse)

### 4. Justify Rating
Provide specific evidence from source text:
- Quote exact phrases that support or contradict the clause
- Explain what's missing, wrong, or needs clarification
- Suggest correction for "revise" ratings when possible

---

## Special Considerations

### Logical Equivalences (Acceptable)
- `not(not(X))` = `X` (double negative)
- `A IMPLIES B` = `not(A) OR B` (material conditional)
- `not(A AND B)` = `not(A) OR not(B)` (De Morgan's law)

These are logically equivalent and should **not** be marked down for style.

### Cultural/Legal Context
- Mexican civil law system
- Adverse possession (usucapión) requires:
  - **Good faith**: 5-10 years with just title
  - **Bad faith**: 10-30 years without title or with knowledge of defects
  - **Ownership character** (*concepto de propietario*): possessor acts as if they own
  - **Generating cause** (*causa generadora*): origin of possession must be proven

### Predicate Conventions
- `oblig(X)`: Obligation or state that holds
- `claim(X)`: Legal claim or demand
- `perm(X)`: Permission (rare in these theses)
- Predicates are in Spanish (original legal language)

---

## Quality Control

### Consistency Checks
- Similar legal principles should receive similar ratings across theses
- Compare with Evaluator 2's ratings (Cohen's Kappa should be ≥0.60)
- Review disagreements - if >30%, re-examine criteria

### Bias Awareness
- **Don't favor complexity**: Simple clear clauses are good
- **Don't penalize valid simplifications**: If thesis provides examples but clause captures general rule, that's acceptable
- **Respect logical equivalence**: Don't mark down different but equivalent formulations

### Calibration
After each batch, check:
- Am I being too harsh? (Error rate >40% suggests over-criticism)
- Am I being too lenient? (Error rate <5% suggests under-scrutiny)
- Target: ~10-20% error rate for a quality model with room for improvement

---

## Examples from Batch 1

### Example 1: ACCEPT
**Thesis 2021246**: "Bad faith adverse possession requires proof of generating cause demonstrating ownership character"

**Clause**: 
```
oblig(causa_generadora) AND oblig(prueba_causa) IMPLIES oblig(posesion_como_propietario)
```

**Rating**: ACCEPT  
**Justification**: Perfectly captures that proving generating cause is necessary to establish ownership character. Source: "debe acreditar... la causa generadora de su posesión... a título de dueño"

---

### Example 2: REVISE
**Thesis 2020418**: "Adverse possession fails because lack of opposability AND owner has perfect title"

**Clause**:
```
not(oblig(contrato_inscrito)) IMPLIES not(oblig(prescripcion_procedente))
```

**Rating**: REVISE  
**Justification**: Oversimplifies dual reasoning - only captures lack of opposability, omits perfect title requirement. Source gives TWO reasons: "falta de oponibilidad... Y... perfecto título de propiedad del demandado"

---

### Example 3: REJECT
**Thesis 2029251**: "Recognition interrupts good faith possession time"

**Clause**:
```
oblig(ejercicio_buena_fe) AND oblig(reconocimiento) IMPLIES oblig(ejercicio_mala_fe)
```

**Rating**: REJECT  
**Justification**: Logical error - states that good faith PLUS recognition IMPLIES bad faith, which is contradictory. Source says recognition "interrumpe el tiempo de posesión de buena fe" (interrupts time), not that it transforms good faith into bad faith.

---

## Version History

- **v1.0** (2025-11-17): Initial criteria after Batch 1 completion
  - 49 clauses evaluated: 42 accept (85.7%), 6 revise (12.2%), 1 reject (2.0%)
  - Error rate: 14.3% (reasonable for initial model)

