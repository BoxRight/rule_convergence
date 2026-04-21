# Computational Analysis of Judicial Consistency

Code and data for *Computational Analysis of Judicial Consistency through Satisfiability Theory* — formalizing Mexican Supreme Court theses in **Witness**, solving each thesis’s validation constraint with a **CUDA ZDD** workflow, and comparing **case structure** (shared legal facts from witness exports) with **resolution structure** (overlap of solution-space fingerprints).

## What this repository does

1. **`methods/analysis/unified_legal_conclusions.wit`** — single model: shared legal vocabulary plus one section per thesis with clauses and `asset tesis<ID>_valida = global();`.
2. **`witnessc`** (built under `methods/witness/`) compiles the model and, with **`tree_fold_cuda`** as external solver (run from **`results/zdd/`**), emits **`zdd_*.bin`** solution-space dumps and **`witness_export_*.json`** per global check (thesis order matches `global()` order in the `.wit` file).
3. Python tools convert binaries to text, aggregate **arrays** into CSVs, and compute **case vs resolution Jaccard similarity** plus per-thesis **mean/std of witness-vector lengths**, producing **tables and PNG plots** under **`results/analysis/`**.

## Repository layout

```
rule_convergence/
├── materials/               # Thesis extracts (texts), PDFs, human evaluations
├── methods/
│   ├── witness/             # witnessc + tree_fold_cuda (build with make)
│   ├── analysis/
│   │   └── unified_legal_conclusions.wit
│   ├── zdd_parser.py
│   ├── generate_thesis_documentation.py
│   └── tools/               # validate, ZDD→CSV, similarity, pipeline helpers
├── results/
│   ├── zdd/                 # Solver cwd: zdd_*.bin, zdd_*.txt, witness_export_*.json
│   ├── witness_exports/     # Copy of witness_export_*.json (used by analysis scripts)
│   ├── documentation/       # Generated LaTeX (optional)
│   └── analysis/
│       ├── case_resolution_similarity.txt    # Median resolution % by case-similarity band
│       ├── case_resolution_similarity.png    # Plot of that table
│       ├── thesis_tamano_medio_desviacion.csv / .png
│       └── zdd_correct_analysis/             # CSVs from zdd_to_csv_correct.py
├── run_pipeline.sh          # Main entry: build → solve → graphs & tables
├── requirements.txt
├── witnessc → methods/witness/witnessc
└── tree_fold_cuda → methods/witness/tree_fold_cuda
```

Run commands from the **repository root** unless noted otherwise.

## Main pipeline (recommended)

Builds **`witnessc`**, runs the unified model with the external solver, converts ZDD binaries to text, copies witness JSON for Python, generates **similarity plots** and **thesis-size plot**, and regenerates **ZDD CSV analysis**.

```bash
chmod +x run_pipeline.sh   # once
./run_pipeline.sh
```

- **`SKIP_WITNESS_BUILD=1`** — skip `make` if `witnessc` is already built.
- **`SKIP_SOLVER=1`** — skip the long `witnessc` run; reuse existing `results/zdd/*` (still runs conversion, plots, and CSV steps).

Dependencies: **`pip install -r requirements.txt`** (includes **matplotlib** for figures). The CUDA solver binary **`tree_fold_cuda`** must be built in `methods/witness/` (see `methods/witness/README.md`).

## Individual steps

| Step | Command |
|------|---------|
| Build compiler | `make -C methods/witness` |
| Validate / compile-only style check | `./methods/tools/validate_unified.sh` |
| Full solver run (same cwd convention as pipeline) | `cd results/zdd && ../methods/witness/witnessc --solver=external ../../methods/analysis/unified_legal_conclusions.wit` |
| Copy exports for tools | `cp results/zdd/witness_export_*.json results/witness_exports/` |
| Binaries → `zdd_*.txt` | `bash methods/tools/zdd_bins_to_txt.sh` |
| Similarity + thesis-size outputs | `python3 methods/tools/case_resolution_similarity.py` |
| ZDD → CSV tables | `python3 methods/tools/zdd_to_csv_correct.py results/zdd` |

## Other workflows

### PDF → text

```bash
./methods/tools/convert_pdfs.sh
```

### LaTeX documentation from the unified model

```bash
python3 methods/generate_thesis_documentation.py
```

Writes **`results/documentation/thesis_documentation.tex`**.

### Add a thesis stub

```bash
./methods/tools/add_thesis_to_unified.sh 2021246 "Your Short Title"
```

Then edit **`methods/analysis/unified_legal_conclusions.wit`** and remove placeholders.

### Human evaluations

See **`materials/evaluations/README.md`**.

## Building Witness and CUDA solver

```bash
cd methods/witness && make clean && make
```

Optional: build **`tree_fold_cuda`** per **`methods/witness/README.md`**. The pipeline expects **`tree_fold_cuda`** next to **`witnessc`** (repo root symlinks point there).

## Dependencies

```bash
pip install -r requirements.txt
```
