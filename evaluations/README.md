# Batch Evaluation System

## Structure

```
evaluations/
├── batch_index.json          # Master index of all batches
├── evaluator_1/              # Evaluator 1 (Claude Sonnet 4.5) evaluations
│   ├── batch_1.json
│   ├── batch_2.json
│   └── ...
└── evaluator_2/              # Evaluator 2 (Gemini-2.5-Pro) evaluations
    ├── batch_1.json
    ├── batch_2.json
    └── ...
```

## Batches

- **Total Theses**: 58
- **Batch Size**: 10 theses per batch
- **Total Batches**: 6 batches

## Workflow

1. **Evaluator 1** evaluates Batch N → saves to `evaluator_1/batch_N.json`
2. **Evaluator 2** evaluates same Batch N → saves to `evaluator_2/batch_N.json`
3. Both evaluations for same batch ensure **identical clause sets**
4. After all batches complete, compute **Cohen's Kappa** on all common clauses

## Batch File Format

Each batch file contains:
```json
{
  "batch_number": 1,
  "evaluator": "Claude Sonnet 4.5",
  "evaluation_date": "2025-11-15",
  "thesis_evaluations": [
    {
      "thesis_id": "2020418",
      "thesis_title": "...",
      "source_text": "texts/tesis2020418.txt",
      "wit_lines": "144-158",
      "clauses": [
        {
          "clause_id": "tesis2020418_principio_fundamental",
          "clause_line": 150,
          "clause_content": "...",
          "rating": "accept|revise|reject",
          "justification": "..."
        }
      ]
    }
  ]
}
```

## Status Tracking

Use `batch_index.json` to track completion status for each evaluator.

