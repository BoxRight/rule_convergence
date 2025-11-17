#!/usr/bin/env python3
"""
Generate Skeleton JSON Files for All Batches
Creates evaluation templates for both evaluators with proper structure
"""

import json
import re
from pathlib import Path
from datetime import datetime

def extract_thesis_info_from_wit(wit_content, thesis_id):
    """Extract thesis information and clauses from WIT file"""
    lines = wit_content.split('\n')
    
    # Find the thesis section
    thesis_start = None
    for i, line in enumerate(lines):
        if f"// THESIS {thesis_id}:" in line:
            thesis_start = i
            break
    
    if thesis_start is None:
        return None
    
    # Get title from comment line
    title_line = lines[thesis_start]
    title_match = re.search(r'// THESIS \d+: (.+)', title_line)
    thesis_title = title_match.group(1) if title_match else "Unknown Title"
    
    # Find all clauses for this thesis
    clauses = []
    current_line = thesis_start
    
    # Look for clause definitions until we hit the next thesis or end
    while current_line < len(lines):
        line = lines[current_line]
        
        # Stop if we hit next thesis
        if current_line > thesis_start and "// THESIS" in line and "// THESIS " in line:
            break
        
        # Look for clause definitions
        clause_match = re.match(rf'clause (tesis{thesis_id}_\w+)\s*=\s*(.+);', line)
        if clause_match:
            clause_id = clause_match.group(1)
            clause_content = clause_match.group(2)
            clauses.append({
                "clause_id": clause_id,
                "clause_line": current_line + 1,  # 1-indexed
                "clause_content": clause_content,
                "rating": "",  # To be filled by evaluator
                "justification": ""  # To be filled by evaluator
            })
        
        current_line += 1
    
    # Determine WIT line range
    wit_end = current_line
    wit_lines = f"{thesis_start + 1}-{wit_end}"
    
    return {
        "thesis_title": thesis_title,
        "wit_lines": wit_lines,
        "clauses": clauses
    }

def generate_skeleton_for_batch(batch_info, wit_content, evaluator_name):
    """Generate skeleton JSON for a specific batch"""
    batch_data = {
        "batch_number": batch_info["batch_number"],
        "evaluator": evaluator_name,
        "evaluation_date": datetime.now().strftime("%Y-%m-%d"),
        "thesis_ids": batch_info["thesis_ids"],
        "thesis_evaluations": []
    }
    
    for thesis_id in batch_info["thesis_ids"]:
        thesis_info = extract_thesis_info_from_wit(wit_content, thesis_id)
        
        if thesis_info:
            thesis_eval = {
                "thesis_id": thesis_id,
                "thesis_title": thesis_info["thesis_title"],
                "source_text": f"texts/tesis{thesis_id}.txt",
                "wit_lines": thesis_info["wit_lines"],
                "clauses": thesis_info["clauses"]
            }
        else:
            # Fallback if thesis not found in WIT
            thesis_eval = {
                "thesis_id": thesis_id,
                "thesis_title": f"Thesis {thesis_id} (not found in WIT)",
                "source_text": f"texts/tesis{thesis_id}.txt",
                "wit_lines": "unknown",
                "clauses": []
            }
        
        batch_data["thesis_evaluations"].append(thesis_eval)
    
    return batch_data

def main():
    """Main function to generate all skeleton files"""
    print("="*80)
    print("GENERATING BATCH SKELETON FILES")
    print("="*80)
    
    # Load batch index
    with open('evaluations/batch_index.json', 'r') as f:
        batch_index = json.load(f)
    
    # Load WIT file
    wit_file = Path('analysis/unified_legal_conclusions.wit')
    wit_content = wit_file.read_text()
    
    # Evaluator configurations
    evaluators = {
        "evaluator_1": "Claude Sonnet 4.5",
        "evaluator_2": "Gemini-2.5-Pro"
    }
    
    total_files = 0
    total_clauses = 0
    
    for evaluator_key, evaluator_name in evaluators.items():
        print(f"\n📝 Generating skeletons for {evaluator_name}...")
        evaluator_dir = Path(f'evaluations/{evaluator_key}')
        evaluator_dir.mkdir(exist_ok=True)
        
        for batch in batch_index['batches']:
            batch_num = batch['batch_number']
            
            # Generate skeleton
            skeleton = generate_skeleton_for_batch(batch, wit_content, evaluator_name)
            
            # Count clauses
            clause_count = sum(len(t['clauses']) for t in skeleton['thesis_evaluations'])
            total_clauses += clause_count
            
            # Save to file
            output_file = evaluator_dir / f"batch_{batch_num}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(skeleton, f, indent=2, ensure_ascii=False)
            
            print(f"  ✅ Batch {batch_num}: {len(skeleton['thesis_ids'])} theses, "
                  f"{clause_count} clauses → {output_file}")
            total_files += 1
    
    print(f"\n{'='*80}")
    print(f"✅ GENERATED {total_files} SKELETON FILES")
    print(f"   Total batches per evaluator: {len(batch_index['batches'])}")
    print(f"   Total clauses per evaluator: {total_clauses // len(evaluators)}")
    print(f"   Total clauses across both: {total_clauses}")
    print(f"{'='*80}")
    
    # Show instructions
    print(f"\n📋 NEXT STEPS:")
    print(f"   1. Open evaluations/evaluator_1/batch_1.json")
    print(f"   2. For each clause, fill in:")
    print(f"      - rating: 'accept', 'revise', or 'reject'")
    print(f"      - justification: detailed explanation")
    print(f"   3. Repeat for all batches")
    print(f"   4. Do the same for evaluator_2")
    print(f"   5. Run compute_cohens_kappa.py when complete")

if __name__ == "__main__":
    main()

