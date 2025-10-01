import pandas as pd
from itertools import combinations

def parse_assignment(array_sig):
    """Convert '[2,7,8]' to [2,7,8]"""
    clean = array_sig.strip('[]')
    if not clean:
        return []
    return [int(x.strip()) for x in clean.split(',')]

def assignment_to_clause(assignment, all_variables):
    """Convert assignment to logical clause"""
    clause_parts = []
    for var in sorted(all_variables):
        if var in assignment:
            clause_parts.append(f"{var}=T")
        else:
            clause_parts.append(f"{var}=F")
    return "(" + " ∧ ".join(clause_parts) + ")"

def assignment_to_positive_clause(assignment):
    """Convert to clause with only positive literals (more readable)"""
    if not assignment:
        return "(all_variables=F)"
    positive_vars = " ∧ ".join(f"{var}=T" for var in sorted(assignment))
    return f"({positive_vars} ∧ others=F)"

# Your data
data = [
    ("[2]", 20, 16),
    ("[1]", 14, 10), 
    ("[1,7]", 9, 6),
    ("[2,17]", 6, 6),
    ("[1,18]", 5, 5),
    ("[1,8]", 5, 5),
    ("[2,4]", 4, 4),
    ("[2,4]", 4, 4),
    ("[1,7,8]", 4, 4),
    ("[2,7,8]", 4, 4),
    ("[1,7,9]", 4, 4),
]

# Process assignments
assignments = []
for array_sig, freq, thesis_count in data:
    assignment = parse_assignment(array_sig)
    assignments.append((assignment, array_sig, freq, thesis_count))

# Get all variables mentioned
all_variables = set()
for assignment, _, _, _ in assignments:
    all_variables.update(assignment)
all_variables = sorted(all_variables)

print("=== INDIVIDUAL CLAUSES ===")
for assignment, array_sig, freq, thesis_count in assignments:
    readable_clause = assignment_to_positive_clause(assignment)
    full_clause = assignment_to_clause(assignment, all_variables)
    print(f"{array_sig:<11} (freq={freq}, thesis={thesis_count})")
    print(f"  Readable: {readable_clause}")
    print(f"  Full:     {full_clause}")
    print()

print("=== COMBINED PROPOSITION (DNF) ===")
print("High consensus legal patterns agree on:")
print()

# Readable version (positive literals only)
readable_clauses = []
for assignment, array_sig, freq, thesis_count in assignments:
    clause = assignment_to_positive_clause(assignment)
    readable_clauses.append(f"{clause}")

readable_dnf = " ∨\n".join(readable_clauses)
print("READABLE VERSION:")
print(readable_dnf)
print()

# Complete logical version
complete_clauses = []
for assignment, array_sig, freq, thesis_count in assignments:
    clause = assignment_to_clause(assignment, all_variables)
    complete_clauses.append(clause)

complete_dnf = " ∨\n".join(complete_clauses)
print("COMPLETE LOGICAL VERSION:")
print(complete_dnf)

print("\n=== SUMMARY ===")
print(f"This proposition captures {len(assignments)} high-consensus patterns")
print(f"involving variables: {all_variables}")
print(f"Agreement: When multiple thesis address the same legal question,")
print(f"they converge on one of these {len(assignments)} logical outcomes")