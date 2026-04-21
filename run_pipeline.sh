#!/usr/bin/env bash
#
# End-to-end pipeline: build Witness, run unified model + CUDA solver, derive analysis.
# Run from repository root (or anywhere — script cd’s internally).
#
# Steps:
#   1. make witnessc (methods/witness)
#   2. witnessc --solver=external unified_legal_conclusions.wit (cwd: results/zdd)
#      → zdd_*.bin, witness_export_*.json written under results/zdd/
#   3. Copy witness_export_*.json → results/witness_exports/ (for Python tools)
#   4. zdd_*.bin → zdd_*.txt
#   5. Case vs resolution similarity plots + thesis size CSV/PNG
#   6. ZDD binaries → CSV tables (arrays_summary_correct, …)
#
# Environment (optional):
#   SKIP_WITNESS_BUILD=1   Skip `make` (reuse existing witnessc binary)
#   SKIP_SOLVER=1          Skip witnessc run (reuse existing results/zdd/*)
#

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UNIFIED="$ROOT/methods/analysis/unified_legal_conclusions.wit"
WITNESSC="$ROOT/methods/witness/witnessc"
OUT_ZDD="$ROOT/results/zdd"
EXPORTS="$ROOT/results/witness_exports"

die() { echo "Error: $*" >&2; exit 1; }

[[ -f "$UNIFIED" ]] || die "missing $UNIFIED"

if [[ "${SKIP_WITNESS_BUILD:-0}" != "1" ]]; then
  echo "== [1/6] Build Witness compiler (witnessc) =="
  make -C "$ROOT/methods/witness"
else
  echo "== [1/6] Skipped build (SKIP_WITNESS_BUILD=1) =="
fi

[[ -x "$WITNESSC" ]] || die "witnessc not executable (run make -C methods/witness)"

mkdir -p "$OUT_ZDD" "$EXPORTS"
if [[ ! -e "$OUT_ZDD/tree_fold_cuda" ]]; then
  ln -sf ../../methods/witness/tree_fold_cuda "$OUT_ZDD/tree_fold_cuda"
fi

if [[ "${SKIP_SOLVER:-0}" != "1" ]]; then
  echo "== [2/6] Witness + external CUDA solver (writes zdd_*.bin and witness_export_*.json in results/zdd/) =="
  echo "    (this can take a long time)"
  (
    cd "$OUT_ZDD"
    "$WITNESSC" --solver=external "$UNIFIED"
  )
else
  echo "== [2/6] Skipped solver (SKIP_SOLVER=1) — using existing artifacts in results/zdd/ =="
fi

echo "== [3/6] Copy witness_export_*.json → results/witness_exports/ =="
shopt -s nullglob
copied=0
for f in "$OUT_ZDD"/witness_export_*.json; do
  cp -f "$f" "$EXPORTS/"
  copied=$((copied + 1))
done
shopt -u nullglob
if [[ "$copied" -eq 0 ]]; then
  echo "    Warning: no witness_export_*.json found under results/zdd/ (case/resolution analysis may be empty)."
else
  echo "    Copied $copied file(s)."
fi

echo "== [4/6] ZDD binaries → text (zdd_*.txt) =="
bash "$ROOT/methods/tools/zdd_bins_to_txt.sh" "$OUT_ZDD"

echo "== [5/6] Case vs resolution similarity + thesis size statistics (plots + CSV) =="
python3 "$ROOT/methods/tools/case_resolution_similarity.py"

echo "== [6/6] ZDD → analysis CSVs (arrays_summary_correct, …) =="
python3 "$ROOT/methods/tools/zdd_to_csv_correct.py" "$OUT_ZDD"

echo ""
echo "Pipeline finished."
echo "  Plots:  $ROOT/results/analysis/case_resolution_similarity.png"
echo "          $ROOT/results/analysis/thesis_tamano_medio_desviacion.png"
echo "  Tables: $ROOT/results/analysis/case_resolution_similarity.txt"
echo "          $ROOT/results/analysis/thesis_tamano_medio_desviacion.csv"
echo "          $ROOT/results/analysis/zdd_correct_analysis/"
