# Evaluation Analysis Report

Generated: analyze_evaluations.py

## 1. Inter-Rater Reliability (Cohen's Kappa)

**Cohen's Kappa: 0.4094** (Moderate)

- Common rated clauses: 268
- This measures whether both evaluators see the same issues consistently.

### Interpretation:
⚠ **Moderate agreement** - Some inconsistency between evaluators.

## 2. WIT Model Quality

This measures how well the WIT clauses reflect the actual theses.

### Evaluator 1

| Rating | Count | Percentage |
|--------|-------|------------|
| Accept | 168 |  62.7% |
| Revise |  57 |  21.3% |
| Reject |  43 |  16.0% |
| **Total** | **268** | **100.0%** |

**Model Error Rate: 37.3%** (clauses needing revision/rejection)

**Model Quality Metrics:**
- **Precision**: 79.6% (of clauses made, how many correct?)
- **Recall**: 74.7% (of what should be correct, how many are?)
- **F1 Score**: 77.1% (harmonic mean of precision & recall)

### Evaluator 2

| Rating | Count | Percentage |
|--------|-------|------------|
| Accept | 126 |  47.0% |
| Revise |  38 |  14.2% |
| Reject | 104 |  38.8% |
| **Total** | **268** | **100.0%** |

**Model Error Rate: 53.0%** (clauses needing revision/rejection)

**Model Quality Metrics:**
- **Precision**: 54.8% (of clauses made, how many correct?)
- **Recall**: 76.8% (of what should be correct, how many are?)
- **F1 Score**: 64.0% (harmonic mean of precision & recall)

### Overall Assessment

⚠ **Moderate model** (54.9% average acceptance) - Significant improvements needed.

## 3. Disagreement Analysis

Total disagreements: 97

### Disagreement Patterns

| Pattern | Count |
|---------|-------|
| accept → reject | 35 |
| revise → reject | 31 |
| accept → revise | 18 |
| revise → accept | 8 |
| reject → accept | 3 |
| reject → revise | 2 |

See `disagreements_report.json` for detailed clause-by-clause analysis.

## 4. Detailed Statistical Analysis


### Confusion Matrix (Evaluator 1 vs Evaluator 2)
```
                 accept     revise     reject
accept              115         18         35
revise                8         18         31
reject                3          2         38
```

### Classification Report
```
              precision    recall  f1-score   support

      accept       0.91      0.68      0.78       168
      revise       0.47      0.32      0.38        57
      reject       0.37      0.88      0.52        43

    accuracy                           0.64       268
   macro avg       0.58      0.63      0.56       268
weighted avg       0.73      0.64      0.65       268
```
## 5. Recommendations

- **Inter-rater reliability**: Review evaluation guidelines - evaluators need better alignment.
- **Model quality (Eval 1)**: High error rate suggests WIT clauses need significant revision.
- **Model quality (Eval 2)**: High error rate suggests WIT clauses need significant revision.
- **Disagreements**: >30% disagreement rate - consider third evaluator for disputed clauses.
