#!/usr/bin/env python3
"""
Generate LaTeX documentation for legal theses with:
1. Original thesis text
2. Intermediate Representation (IR) of formalization
3. Witness clause code

Usage:
    python generate_thesis_documentation.py [thesis_number]
    python generate_thesis_documentation.py  # generates for all theses
"""

import re
import sys
import os
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class Clause:
    """Represents a Witness clause"""
    name: str
    expression: str
    comment: str
    thesis_number: str
    line_number: int

@dataclass
class Thesis:
    """Represents a thesis with its clauses"""
    number: str
    title: str
    clauses: List[Clause]
    text_file: Optional[str] = None

class WitnessParser:
    """Parser for Witness language clauses"""
    
    # Asset name mappings for better IR readability
    ASSET_DESCRIPTIONS = {
        'titularidad_registral': 'registered ownership',
        'contrato_no_inscrito': 'unregistered contract',
        'demanda_prescripcion': 'adverse possession claim',
        'oponibilidad_terceros': 'opposability to third parties',
        'ejercicio_buena_fe': 'good faith exercise',
        'ejercicio_mala_fe': 'bad faith exercise',
        'posesion_como_propietario': 'possession as owner',
        'causa_generadora_probada': 'proven generating cause',
        'posesion_temporal': 'temporal possession',
        'allanamiento_demandado': 'defendant acquiescence',
        'posesion_pacifico_continuo_publico': 'peaceful, continuous, and public possession',
        'proteccion_terceros': 'third party protection',
    }
    
    def __init__(self):
        self.assets = {}  # Will be populated from asset definitions
    
    def parse_clause_expression(self, expr: str) -> str:
        """Parse a clause expression and generate IR"""
        expr = expr.strip()
        if not expr:
            return ""
        
        # Remove trailing semicolon if present
        expr = expr.rstrip(';')
        
        # Parse the expression recursively
        return self._parse_expression(expr)
    
    def _parse_expression(self, expr: str) -> str:
        """Recursively parse an expression"""
        expr = expr.strip()
        if not expr:
            return ""
        
        # Handle parentheses - but only if the entire expression is parenthesized
        # Otherwise, let operator parsing handle the structure
        if expr.startswith('('):
            # Find matching closing parenthesis
            depth = 0
            fully_parenthesized = False
            for i, char in enumerate(expr):
                if char == '(':
                    depth += 1
                elif char == ')':
                    depth -= 1
                    if depth == 0:
                        # Check if this closes the opening parenthesis and it's the end
                        if i == len(expr) - 1:
                            # Entire expression is parenthesized
                            inner = expr[1:i]
                            parsed_inner = self._parse_expression(inner)
                            return f"({parsed_inner})"
                        else:
                            # There's more after - don't treat as fully parenthesized
                            break
        
        # Handle logical operators (order matters: IMPLIES, EQUIV, AND, OR, NOT)
        # We need to find operators at the top level (not inside parentheses)
        implies_pos = self._find_operator_at_level(expr, ' IMPLIES ')
        if implies_pos >= 0:
            left = expr[:implies_pos].strip()
            right = expr[implies_pos + len(' IMPLIES '):].strip()
            parsed_left = self._parse_expression(left)
            parsed_right = self._parse_expression(right)
            return f"If {parsed_left}, then {parsed_right}"
        
        equiv_pos = self._find_operator_at_level(expr, ' EQUIV ')
        if equiv_pos >= 0:
            left = expr[:equiv_pos].strip()
            right = expr[equiv_pos + len(' EQUIV '):].strip()
            parsed_left = self._parse_expression(left)
            parsed_right = self._parse_expression(right)
            return f"{parsed_left} if and only if {parsed_right}"
        
        # For AND, OR, XOR - find all occurrences at top level
        and_parts = self._split_by_operator_at_level(expr, ' AND ')
        if len(and_parts) > 1:
            parsed_parts = [self._parse_expression(p) for p in and_parts]
            return " and ".join(parsed_parts)
        
        or_parts = self._split_by_operator_at_level(expr, ' OR ')
        if len(or_parts) > 1:
            parsed_parts = [self._parse_expression(p) for p in or_parts]
            return " or ".join(parsed_parts)
        
        xor_parts = self._split_by_operator_at_level(expr, ' XOR ')
        if len(xor_parts) > 1:
            parsed_left = self._parse_expression(xor_parts[0])
            parsed_right = self._parse_expression(xor_parts[1])
            return f"either {parsed_left} or {parsed_right} (exclusive)"
        
        # Handle function calls: oblig, claim, not
        if expr.startswith('oblig('):
            match = re.match(r'oblig\(([^)]+)\)', expr)
            if match:
                asset = match.group(1).strip()
                asset_desc = self._get_asset_description(asset)
                return f"{asset_desc} is obligated"
        
        if expr.startswith('claim('):
            match = re.match(r'claim\(([^)]+)\)', expr)
            if match:
                asset = match.group(1).strip()
                asset_desc = self._get_asset_description(asset)
                return f"{asset_desc} is claimed"
        
        if expr.startswith('not('):
            match = re.match(r'not\((.+)\)', expr, re.DOTALL)
            if match:
                inner = match.group(1).strip()
                parsed_inner = self._parse_expression(inner)
                return f"not ({parsed_inner})"
        
        # Handle identifiers (assets)
        if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', expr):
            asset_desc = self._get_asset_description(expr)
            return asset_desc
        
        return expr
    
    def _find_operator_at_level(self, expr: str, op: str) -> int:
        """Find operator at top level (not inside parentheses)"""
        depth = 0
        i = 0
        while i < len(expr) - len(op) + 1:
            if expr[i] == '(':
                depth += 1
            elif expr[i] == ')':
                depth -= 1
            elif depth == 0 and expr[i:i+len(op)] == op:
                # Check it's a complete operator
                # Operator starts with space, so check character before that space
                # Allow: start of string, space, or closing parenthesis
                before_ok = (i == 0) or (expr[i-1] in ' )')
                # Operator ends with space, so check character after that space
                # Allow: end of string, space, or opening parenthesis
                after_ok = (i+len(op) >= len(expr)) or (expr[i+len(op)] in ' (')
                if before_ok and after_ok:
                    return i
            i += 1
        return -1
    
    def _split_by_operator_at_level(self, expr: str, op: str) -> List[str]:
        """Split expression by operator at top level, respecting parentheses"""
        parts = []
        depth = 0
        current = ""
        
        i = 0
        while i < len(expr):
            if expr[i] == '(':
                depth += 1
                current += expr[i]
            elif expr[i] == ')':
                depth -= 1
                current += expr[i]
            elif depth == 0 and i <= len(expr) - len(op) and expr[i:i+len(op)] == op:
                # Check it's a complete operator match
                # Operator has spaces on both sides, so check boundaries
                # Before: allow start, space, or closing parenthesis
                before_ok = (i == 0) or (expr[i-1] in ' )')
                # After: allow end, space, opening parenthesis, or any identifier char (since op ends with space)
                # Actually, since operator ends with space, next char can be anything (it's the start of next token)
                after_ok = True  # Operator ends with space, so next char is always valid
                if before_ok and after_ok:
                    if current.strip():
                        parts.append(current.strip())
                    current = ""
                    i += len(op)
                    continue
                else:
                    current += expr[i]
            else:
                current += expr[i]
            i += 1
        
        if current.strip():
            parts.append(current.strip())
        
        return parts if parts else [expr]
    
    def _get_asset_description(self, asset_name: str) -> str:
        """Get human-readable description of an asset"""
        # Replace underscores with spaces and capitalize
        if asset_name in self.ASSET_DESCRIPTIONS:
            return self.ASSET_DESCRIPTIONS[asset_name]
        
        # Fallback: convert snake_case to readable text
        readable = asset_name.replace('_', ' ')
        return readable

class WitFileParser:
    """Parser for .wit files"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.content = ""
        self.theses: Dict[str, Thesis] = {}
    
    def parse(self) -> Dict[str, Thesis]:
        """Parse the .wit file and extract theses with clauses"""
        with open(self.file_path, 'r', encoding='utf-8') as f:
            self.content = f.read()
        
        # Find all thesis sections
        thesis_pattern = r'//\s*THESIS\s+(\d+):\s*(.+?)\n'
        
        lines = self.content.split('\n')
        current_thesis = None
        current_clauses = []
        current_comment = ""
        
        for i, line in enumerate(lines, 1):
            # Check for thesis header
            thesis_match = re.match(r'//\s*THESIS\s+(\d+):\s*(.+?)$', line)
            if thesis_match:
                # Save previous thesis if exists
                if current_thesis:
                    self.theses[current_thesis.number] = Thesis(
                        number=current_thesis.number,
                        title=current_thesis.title,
                        clauses=current_clauses.copy()
                    )
                
                # Start new thesis
                thesis_num = thesis_match.group(1)
                thesis_title = thesis_match.group(2).strip()
                current_thesis = Thesis(
                    number=thesis_num,
                    title=thesis_title,
                    clauses=[]
                )
                current_clauses = []
                current_comment = ""
                continue
            
            # Check for clause definition
            clause_match = re.match(r'clause\s+(\w+)\s*=\s*(.+?);', line)
            if clause_match and current_thesis:
                clause_name = clause_match.group(1)
                clause_expr = clause_match.group(2).strip()
                
                clause = Clause(
                    name=clause_name,
                    expression=clause_expr,
                    comment=current_comment.strip(),
                    thesis_number=current_thesis.number,
                    line_number=i
                )
                current_clauses.append(clause)
                current_comment = ""
                continue
            
            # Collect comments (lines starting with //)
            if line.strip().startswith('//') and current_thesis:
                comment_text = line.strip()[2:].strip()
                if comment_text and not comment_text.startswith('='):
                    if current_comment:
                        current_comment += " " + comment_text
                    else:
                        current_comment = comment_text
        
        # Save last thesis
        if current_thesis:
            self.theses[current_thesis.number] = Thesis(
                number=current_thesis.number,
                title=current_thesis.title,
                clauses=current_clauses.copy()
            )
        
        return self.theses

class LaTeXGenerator:
    """Generate LaTeX documentation"""
    
    def __init__(self, parser: WitnessParser):
        self.parser = parser
    
    def generate_document(self, theses: Dict[str, Thesis], output_file: str, 
                         texts_dir: str = "texts"):
        """Generate LaTeX document for all theses"""
        
        with open(output_file, 'w', encoding='utf-8') as f:
            # Write LaTeX preamble
            f.write(self._latex_preamble())
            
            # Generate content for each thesis (numeric order by thesis ID)
            for thesis_num in sorted(theses.keys(), key=lambda k: int(k)):
                thesis = theses[thesis_num]
                f.write(self._generate_thesis_section(thesis, texts_dir))
            
            # Write LaTeX closing
            f.write(self._latex_closing())
    
    def _latex_preamble(self) -> str:
        """Generate LaTeX document preamble"""
        return r"""\documentclass[11pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{geometry}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{listings}
\usepackage{xcolor}
\usepackage{hyperref}
\usepackage{fancyhdr}
\usepackage{titlesec}

\geometry{margin=2.5cm}

% Code listing style for Witness
\lstdefinestyle{witnessstyle}{
    language=C++,
    basicstyle=\ttfamily\small,
    keywordstyle=\color{blue}\bfseries,
    commentstyle=\color{gray}\itshape,
    stringstyle=\color{red},
    numbers=left,
    numberstyle=\tiny\color{gray},
    stepnumber=1,
    numbersep=5pt,
    frame=single,
    breaklines=true,
    breakatwhitespace=true,
    tabsize=2,
    showstringspaces=false
}

\lstdefinelanguage{Witness}{
    keywords={asset, clause, subject, action, object, service, oblig, claim, not, AND, OR, IMPLIES, EQUIV, global},
    sensitive=true,
    comment=[l]{//},
    morecomment=[s]{/*}{*/},
    morestring=[b]"
}

\title{Legal Theses Formalization Documentation}
\author{Computational Analysis of Judicial Consistency}
\date{\today}

\begin{document}
\maketitle
\tableofcontents
\newpage

"""
    
    def _latex_closing(self) -> str:
        """Generate LaTeX document closing"""
        return r"""
\end{document}
"""
    
    def _generate_thesis_section(self, thesis: Thesis, texts_dir: str) -> str:
        """Generate LaTeX section for a single thesis"""
        content = []
        
        # Section header
        content.append(f"\\section{{Thesis {thesis.number}: {thesis.title}}}\n")
        content.append(f"\\label{{thesis:{thesis.number}}}\n\n")
        
        # Thesis text
        content.append("\\subsection{Original Thesis Text}\n\n")
        thesis_text = self._load_thesis_text(thesis.number, texts_dir)
        if thesis_text:
            content.append("\\begin{quote}\n")
            content.append(self._escape_latex(thesis_text))
            content.append("\n\\end{quote}\n\n")
        else:
            content.append("\\textit{Thesis text file not found.}\n\n")
        
        # Formalization section
        content.append("\\subsection{Formalization}\n\n")
        
        if not thesis.clauses:
            content.append("\\textit{No clauses defined for this thesis.}\n\n")
        else:
            for clause in thesis.clauses:
                content.append(self._generate_clause_subsection(clause))
        
        content.append("\\newpage\n\n")
        
        return "".join(content)
    
    def _generate_clause_subsection(self, clause: Clause) -> str:
        """Generate LaTeX subsection for a clause"""
        content = []
        
        # Clause name as subsubsection
        clause_display_name = clause.name.replace('_', '\\_')
        content.append(f"\\subsubsection{{Clause: {clause_display_name}}}\n\n")
        
        # Comment if available
        if clause.comment:
            content.append(f"\\textit{{{self._escape_latex(clause.comment)}}}\n\n")
        
        # Intermediate Representation
        try:
            ir = self.parser.parse_clause_expression(clause.expression)
        except Exception as e:
            ir = f"[Error parsing expression: {str(e)}]"
            print(f"Warning: Could not parse clause {clause.name}: {e}", file=sys.stderr)
        
        content.append("\\textbf{Intermediate Representation:}\n\n")
        content.append("\\begin{quote}\n")
        content.append(self._escape_latex(ir))
        content.append("\n\\end{quote}\n\n")
        
        # Witness code
        content.append("\\textbf{Witness Clause:}\n\n")
        content.append("\\begin{lstlisting}[style=witnessstyle, language=Witness]\n")
        witness_code = f"clause {clause.name} = {clause.expression};"
        content.append(witness_code)
        content.append("\n\\end{lstlisting}\n\n")
        
        return "".join(content)
    
    def _load_thesis_text(self, thesis_num: str, texts_dir: str) -> Optional[str]:
        """Load thesis text from file (try lowercase then capitalized filename)."""
        base = Path(texts_dir)
        for name in (f"tesis{thesis_num}.txt", f"Tesis{thesis_num}.txt"):
            text_file = base / name
            if text_file.exists():
                try:
                    with open(text_file, 'r', encoding='utf-8') as f:
                        return f.read()
                except Exception as e:
                    print(f"Warning: Could not read {text_file}: {e}", file=sys.stderr)
                    return None
        return None
    
    def _escape_latex(self, text: str) -> str:
        """Escape special LaTeX characters"""
        replacements = {
            '\\': r'\textbackslash{}',
            '{': r'\{',
            '}': r'\}',
            '$': r'\$',
            '&': r'\&',
            '%': r'\%',
            '#': r'\#',
            '^': r'\textasciicircum{}',
            '_': r'\_',
            '~': r'\textasciitilde{}',
        }
        for char, replacement in replacements.items():
            text = text.replace(char, replacement)
        return text

def main():
    """Main function"""
    if len(sys.argv) > 1:
        thesis_numbers = [sys.argv[1]]
    else:
        # Generate for all theses
        thesis_numbers = None
    
    repo_root = Path(__file__).resolve().parents[1]
    wit_file = repo_root / "methods" / "analysis" / "unified_legal_conclusions.wit"
    texts_dir = str(repo_root / "materials" / "texts")
    output_file = str(repo_root / "results" / "documentation" / "thesis_documentation.tex")
    
    if not wit_file.is_file():
        print(f"Error: {wit_file} not found", file=sys.stderr)
        sys.exit(1)
    
    # Parse .wit file
    print(f"Parsing {wit_file}...")
    wit_parser = WitFileParser(str(wit_file))
    theses = wit_parser.parse()
    
    # Filter by thesis number if specified
    if thesis_numbers:
        theses = {num: theses[num] for num in thesis_numbers if num in theses}
        if not theses:
            print(f"Error: No theses found for numbers: {thesis_numbers}", file=sys.stderr)
            sys.exit(1)
    
    print(f"Found {len(theses)} thesis(es)")
    
    # Generate IR parser
    witness_parser = WitnessParser()
    
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # Generate LaTeX
    print(f"Generating LaTeX document: {output_file}")
    latex_gen = LaTeXGenerator(witness_parser)
    latex_gen.generate_document(theses, output_file, texts_dir)
    
    print(f"Done! Generated {output_file}")
    print(f"Compile with: pdflatex {output_file}")

if __name__ == "__main__":
    main()

