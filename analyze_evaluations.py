#!/usr/bin/env python3
"""
Comprehensive Evaluation Analysis Script

Computes:
1. Cohen's Kappa - Inter-rater reliability (do evaluators agree?)
2. Model Quality Metrics - WIT model accuracy (do clauses reflect theses?)
3. Per-class Analysis - Which rating categories have most issues?
4. Disagreement Analysis - Where do evaluators differ?
"""

import json
import os
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Tuple
import numpy as np
from sklearn.metrics import cohen_kappa_score, confusion_matrix, classification_report


def load_batch_evaluations(evaluator_dir: Path) -> Dict[str, Dict]:
    """Load all batch evaluations for an evaluator."""
    evaluations = {}
    
    for batch_file in sorted(evaluator_dir.glob("batch_*.json")):
        with open(batch_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for thesis in data['thesis_evaluations']:
                for clause in thesis['clauses']:
                    clause_id = clause['clause_id']
                    evaluations[clause_id] = {
                        'rating': clause['rating'],
                        'justification': clause['justification'],
                        'thesis_id': thesis['thesis_id'],
                        'thesis_title': thesis['thesis_title']
                    }
    
    return evaluations


def compute_cohens_kappa(eval1: Dict, eval2: Dict) -> Tuple[float, List, List]:
    """Compute Cohen's Kappa for inter-rater reliability."""
    # Find common clauses
    common_clauses = set(eval1.keys()) & set(eval2.keys())
    
    if not common_clauses:
        return None, [], []
    
    # Extract ratings for common clauses
    ratings1 = []
    ratings2 = []
    
    for clause_id in sorted(common_clauses):
        r1 = eval1[clause_id]['rating']
        r2 = eval2[clause_id]['rating']
        
        # Only include if both have rated (not empty)
        if r1 and r2:
            ratings1.append(r1)
            ratings2.append(r2)
    
    if not ratings1:
        return None, [], []
    
    kappa = cohen_kappa_score(ratings1, ratings2)
    return kappa, ratings1, ratings2


def compute_model_quality(evaluations: Dict) -> Dict:
    """Compute model quality metrics from evaluation ratings."""
    ratings = [e['rating'] for e in evaluations.values() if e['rating']]
    
    total = len(ratings)
    if total == 0:
        return {}
    
    counter = Counter(ratings)
    
    return {
        'total_clauses': total,
        'accept_count': counter['accept'],
        'revise_count': counter['revise'],
        'reject_count': counter['reject'],
        'accept_rate': counter['accept'] / total * 100,
        'revise_rate': counter['revise'] / total * 100,
        'reject_rate': counter['reject'] / total * 100,
        'error_rate': (counter['revise'] + counter['reject']) / total * 100
    }


def analyze_disagreements(eval1: Dict, eval2: Dict) -> List[Dict]:
    """Find and categorize disagreements between evaluators."""
    common_clauses = set(eval1.keys()) & set(eval2.keys())
    disagreements = []
    
    for clause_id in sorted(common_clauses):
        r1 = eval1[clause_id]['rating']
        r2 = eval2[clause_id]['rating']
        
        if r1 and r2 and r1 != r2:
            disagreements.append({
                'clause_id': clause_id,
                'thesis_id': eval1[clause_id]['thesis_id'],
                'thesis_title': eval1[clause_id]['thesis_title'],
                'evaluator_1': r1,
                'evaluator_2': r2,
                'justification_1': eval1[clause_id]['justification'][:100] + '...',
                'justification_2': eval2[clause_id]['justification'][:100] + '...'
            })
    
    return disagreements


def compute_confusion_matrix_stats(ratings1: List, ratings2: List) -> str:
    """Generate confusion matrix and classification report."""
    labels = ['accept', 'revise', 'reject']
    
    cm = confusion_matrix(ratings1, ratings2, labels=labels)
    report = classification_report(ratings1, ratings2, labels=labels, 
                                   target_names=labels, zero_division=0)
    
    output = "\n### Confusion Matrix (Evaluator 1 vs Evaluator 2)\n"
    output += "```\n"
    output += f"{'':12} {'accept':>10} {'revise':>10} {'reject':>10}\n"
    for i, label in enumerate(labels):
        output += f"{label:12} {cm[i][0]:10d} {cm[i][1]:10d} {cm[i][2]:10d}\n"
    output += "```\n\n"
    
    output += "### Classification Report\n"
    output += "```\n"
    output += report
    output += "```\n"
    
    return output


def interpret_kappa(kappa: float) -> str:
    """Interpret Cohen's Kappa value."""
    if kappa < 0:
        return "Poor (worse than chance)"
    elif kappa < 0.20:
        return "Slight"
    elif kappa < 0.40:
        return "Fair"
    elif kappa < 0.60:
        return "Moderate"
    elif kappa < 0.80:
        return "Substantial"
    else:
        return "Almost Perfect"


def main():
    base_dir = Path("/home/maitreya/rule_convergence/evaluations")
    
    print("=" * 80)
    print("EVALUATION ANALYSIS REPORT")
    print("=" * 80)
    
    # Load evaluations
    print("\n[1/5] Loading evaluations...")
    eval1_dir = base_dir / "evaluator_1"
    eval2_dir = base_dir / "evaluator_2"
    
    eval1 = load_batch_evaluations(eval1_dir)
    eval2 = load_batch_evaluations(eval2_dir)
    
    print(f"  - Evaluator 1: {len(eval1)} clauses loaded")
    print(f"  - Evaluator 2: {len(eval2)} clauses loaded")
    
    # Compute Cohen's Kappa
    print("\n[2/5] Computing Cohen's Kappa (inter-rater reliability)...")
    kappa, ratings1, ratings2 = compute_cohens_kappa(eval1, eval2)
    
    if kappa is not None:
        print(f"\n  Cohen's Kappa: {kappa:.4f}")
        print(f"  Interpretation: {interpret_kappa(kappa)}")
        print(f"  Common rated clauses: {len(ratings1)}")
    else:
        print("  ⚠ Cannot compute - no common rated clauses yet")
    
    # Compute Model Quality
    print("\n[3/5] Computing WIT Model Quality Metrics...")
    
    quality1 = compute_model_quality(eval1)
    quality2 = compute_model_quality(eval2)
    
    print("\n  Evaluator 1 Ratings:")
    if quality1:
        print(f"    - Accept:  {quality1['accept_count']:3d} ({quality1['accept_rate']:5.1f}%)")
        print(f"    - Revise:  {quality1['revise_count']:3d} ({quality1['revise_rate']:5.1f}%)")
        print(f"    - Reject:  {quality1['reject_count']:3d} ({quality1['reject_rate']:5.1f}%)")
        print(f"    - Error Rate: {quality1['error_rate']:.1f}% (clauses needing revision/rejection)")
    else:
        print("    ⚠ No ratings yet")
    
    print("\n  Evaluator 2 Ratings:")
    if quality2:
        print(f"    - Accept:  {quality2['accept_count']:3d} ({quality2['accept_rate']:5.1f}%)")
        print(f"    - Revise:  {quality2['revise_count']:3d} ({quality2['revise_rate']:5.1f}%)")
        print(f"    - Reject:  {quality2['reject_count']:3d} ({quality2['reject_rate']:5.1f}%)")
        print(f"    - Error Rate: {quality2['error_rate']:.1f}% (clauses needing revision/rejection)")
    else:
        print("    ⚠ No ratings yet")
    
    # Analyze disagreements
    print("\n[4/5] Analyzing disagreements...")
    disagreements = analyze_disagreements(eval1, eval2)
    
    if disagreements:
        print(f"\n  Found {len(disagreements)} disagreements")
        
        # Categorize disagreements
        disagreement_types = defaultdict(int)
        for d in disagreements:
            key = f"{d['evaluator_1']} → {d['evaluator_2']}"
            disagreement_types[key] += 1
        
        print("\n  Disagreement patterns:")
        for pattern, count in sorted(disagreement_types.items(), key=lambda x: -x[1]):
            print(f"    - {pattern}: {count} cases")
        
        # Save detailed disagreements
        output_file = base_dir / "disagreements_report.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(disagreements, f, indent=2, ensure_ascii=False)
        print(f"\n  Detailed report saved to: {output_file}")
    else:
        print("  No disagreements found (or no common rated clauses)")
    
    # Generate detailed report
    print("\n[5/5] Generating detailed statistical report...")
    
    report_path = base_dir / "ANALYSIS_REPORT.md"
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# Evaluation Analysis Report\n\n")
        f.write(f"Generated: {Path(__file__).name}\n\n")
        
        f.write("## 1. Inter-Rater Reliability (Cohen's Kappa)\n\n")
        if kappa is not None:
            f.write(f"**Cohen's Kappa: {kappa:.4f}** ({interpret_kappa(kappa)})\n\n")
            f.write(f"- Common rated clauses: {len(ratings1)}\n")
            f.write(f"- This measures whether both evaluators see the same issues consistently.\n\n")
            
            f.write("### Interpretation:\n")
            if kappa >= 0.80:
                f.write("✓ **Excellent agreement** - Both evaluators are very consistent.\n\n")
            elif kappa >= 0.60:
                f.write("✓ **Good agreement** - Both evaluators are reasonably consistent.\n\n")
            elif kappa >= 0.40:
                f.write("⚠ **Moderate agreement** - Some inconsistency between evaluators.\n\n")
            else:
                f.write("✗ **Poor agreement** - Evaluators have significant disagreements.\n\n")
        else:
            f.write("⚠ Cannot compute yet - need common rated clauses from both evaluators.\n\n")
        
        f.write("## 2. WIT Model Quality\n\n")
        f.write("This measures how well the WIT clauses reflect the actual theses.\n\n")
        
        if quality1:
            f.write("### Evaluator 1\n\n")
            f.write(f"| Rating | Count | Percentage |\n")
            f.write(f"|--------|-------|------------|\n")
            f.write(f"| Accept | {quality1['accept_count']:3d} | {quality1['accept_rate']:5.1f}% |\n")
            f.write(f"| Revise | {quality1['revise_count']:3d} | {quality1['revise_rate']:5.1f}% |\n")
            f.write(f"| Reject | {quality1['reject_count']:3d} | {quality1['reject_rate']:5.1f}% |\n")
            f.write(f"| **Total** | **{quality1['total_clauses']}** | **100.0%** |\n\n")
            f.write(f"**Model Error Rate: {quality1['error_rate']:.1f}%** (clauses needing revision/rejection)\n\n")
        
        if quality2:
            f.write("### Evaluator 2\n\n")
            f.write(f"| Rating | Count | Percentage |\n")
            f.write(f"|--------|-------|------------|\n")
            f.write(f"| Accept | {quality2['accept_count']:3d} | {quality2['accept_rate']:5.1f}% |\n")
            f.write(f"| Revise | {quality2['revise_count']:3d} | {quality2['revise_rate']:5.1f}% |\n")
            f.write(f"| Reject | {quality2['reject_count']:3d} | {quality2['reject_rate']:5.1f}% |\n")
            f.write(f"| **Total** | **{quality2['total_clauses']}** | **100.0%** |\n\n")
            f.write(f"**Model Error Rate: {quality2['error_rate']:.1f}%** (clauses needing revision/rejection)\n\n")
        
        if quality1 and quality2:
            f.write("### Overall Assessment\n\n")
            avg_accept = (quality1['accept_rate'] + quality2['accept_rate']) / 2
            if avg_accept >= 85:
                f.write(f"✓ **Excellent model** ({avg_accept:.1f}% average acceptance) - WIT clauses accurately reflect theses.\n\n")
            elif avg_accept >= 70:
                f.write(f"✓ **Good model** ({avg_accept:.1f}% average acceptance) - Most clauses are accurate.\n\n")
            elif avg_accept >= 50:
                f.write(f"⚠ **Moderate model** ({avg_accept:.1f}% average acceptance) - Significant improvements needed.\n\n")
            else:
                f.write(f"✗ **Poor model** ({avg_accept:.1f}% average acceptance) - Major revisions required.\n\n")
        
        f.write("## 3. Disagreement Analysis\n\n")
        if disagreements:
            f.write(f"Total disagreements: {len(disagreements)}\n\n")
            f.write("### Disagreement Patterns\n\n")
            f.write("| Pattern | Count |\n")
            f.write("|---------|-------|\n")
            for pattern, count in sorted(disagreement_types.items(), key=lambda x: -x[1]):
                f.write(f"| {pattern} | {count} |\n")
            f.write(f"\nSee `disagreements_report.json` for detailed clause-by-clause analysis.\n\n")
        else:
            f.write("No disagreements found.\n\n")
        
        if kappa is not None and len(ratings1) > 0:
            f.write("## 4. Detailed Statistical Analysis\n\n")
            f.write(compute_confusion_matrix_stats(ratings1, ratings2))
        
        f.write("## 5. Recommendations\n\n")
        
        if kappa is not None:
            if kappa < 0.60:
                f.write("- **Inter-rater reliability**: Review evaluation guidelines - evaluators need better alignment.\n")
            
        if quality1 and quality1['error_rate'] > 30:
            f.write("- **Model quality (Eval 1)**: High error rate suggests WIT clauses need significant revision.\n")
        
        if quality2 and quality2['error_rate'] > 30:
            f.write("- **Model quality (Eval 2)**: High error rate suggests WIT clauses need significant revision.\n")
        
        if disagreements and len(disagreements) > len(ratings1) * 0.3:
            f.write("- **Disagreements**: >30% disagreement rate - consider third evaluator for disputed clauses.\n")
        
        if not (kappa and kappa < 0.60) and not (quality1 and quality1['error_rate'] > 30):
            f.write("- Continue with current evaluation process.\n")
    
    print(f"\n  Detailed report saved to: {report_path}")
    
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    
    # Summary interpretation
    print("\n### Quick Interpretation:")
    if kappa is not None and quality1:
        print(f"\n1. Agreement: {interpret_kappa(kappa)} (κ={kappa:.3f})")
        print(f"2. Model Quality: {quality1['accept_rate']:.1f}% acceptance rate")
        if kappa >= 0.60 and quality1['accept_rate'] >= 70:
            print("3. ✓ Both metrics look good - reliable evaluation of a quality model")
        elif kappa >= 0.60 and quality1['accept_rate'] < 70:
            print("3. ⚠ Evaluators agree BUT model has many errors - reliable detection of problems")
        elif kappa < 0.60 and quality1['accept_rate'] >= 70:
            print("3. ⚠ Model seems good BUT evaluators disagree - need to resolve evaluation process")
        else:
            print("3. ✗ Both poor - model has issues AND evaluation needs improvement")
    
    print("\n")


if __name__ == "__main__":
    main()

