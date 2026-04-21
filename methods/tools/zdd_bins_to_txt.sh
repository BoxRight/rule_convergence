#!/usr/bin/env bash
# Convert each results/zdd/zdd_<n>.bin to zdd_<n>.txt (one witness line per array).
# Required for methods/tools/case_resolution_similarity.py resolution side.
#
# Usage (from repo root):
#   bash methods/tools/zdd_bins_to_txt.sh
#   bash methods/tools/zdd_bins_to_txt.sh /path/to/results/zdd

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
ZDD_DIR="${1:-$REPO_ROOT/results/zdd}"
CONV="$REPO_ROOT/methods/zdd_binary_to_text.py"

if [[ ! -d "$ZDD_DIR" ]]; then
  echo "Directory not found: $ZDD_DIR" >&2
  exit 1
fi

mapfile -t bins < <(find "$ZDD_DIR" -maxdepth 1 -name 'zdd_*.bin' | sort -V)
if [[ ${#bins[@]} -eq 0 ]]; then
  echo "No zdd_*.bin files under $ZDD_DIR" >&2
  exit 1
fi

echo "Converting ${#bins[@]} binary ZDD file(s) in $ZDD_DIR ..."
for bin in "${bins[@]}"; do
  python3 "$CONV" "$bin"
done

echo "Done. Run similarity analysis:"
echo "  python3 methods/tools/case_resolution_similarity.py"
