# Batch Evaluation Workflow

## Step-by-Step Process

### **Step 1: Check Status**
```bash
python3 batch_evaluation_manager.py status
```
This shows which batches are pending/completed for each evaluator.

### **Step 2: Start a Batch (Evaluator 1)**
```bash
# Find next batch
python3 batch_evaluation_manager.py next evaluator_1

# Create template for that batch (e.g., Batch 1)
python3 batch_evaluation_manager.py template 1 evaluator_1
```

### **Step 3: Evaluate the Batch**
1. Open `evaluations/evaluator_1/batch_1_template.json`
2. For each thesis in the batch:
   - Read the source text (`texts/tesis[ID].txt`)
   - Read the WIT clauses (lines indicated in WIT file)
   - Evaluate each clause (accept/revise/reject with justification)
3. Fill in all TODO fields
4. Rename to `batch_1.json` when complete

### **Step 4: Same Batch for Evaluator 2**
```bash
# Create template for same batch
python3 batch_evaluation_manager.py template 1 evaluator_2
```
Evaluator 2 evaluates the **same exact clauses** as Evaluator 1.

### **Step 5: Repeat for All Batches**
Continue with batches 2, 3, 4, 5, 6...

### **Step 6: Merge Complete Evaluations**
After all batches are done:
```bash
# Merge evaluator 1's batches
python3 batch_evaluation_manager.py merge evaluator_1

# Merge evaluator 2's batches
python3 batch_evaluation_manager.py merge evaluator_2
```

This creates:
- `evaluations/evaluator_1_complete.json`
- `evaluations/evaluator_2_complete.json`

### **Step 7: Compute Cohen's Kappa**
```bash
python3 compute_cohens_kappa.py
```

## Batches Overview

| Batch | Theses | Status E1 | Status E2 |
|-------|--------|-----------|-----------|
| 1     | 10     | ⏳ Pending | ⏳ Pending |
| 2     | 10     | ⏳ Pending | ⏳ Pending |
| 3     | 10     | ⏳ Pending | ⏳ Pending |
| 4     | 10     | ⏳ Pending | ⏳ Pending |
| 5     | 10     | ⏳ Pending | ⏳ Pending |
| 6     | 8      | ⏳ Pending | ⏳ Pending |

**Total: 58 theses**

## Benefits of This Approach

✅ **Manageable chunks**: 10 theses at a time, won't lose context
✅ **Consistent data**: Both evaluators rate identical clauses
✅ **Trackable progress**: Clear status for each batch
✅ **Parallel work**: Different batches can be done independently
✅ **Reliable metrics**: Cohen's Kappa on matched data

