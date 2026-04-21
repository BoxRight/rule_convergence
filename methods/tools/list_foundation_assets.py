#!/usr/bin/env python3
"""List shared foundation definitions in unified_legal_conclusions.wit (asset reuse audit)."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WIT = ROOT / "methods/analysis/unified_legal_conclusions.wit"


def main() -> None:
    text = WIT.read_text(encoding="utf-8")
    first_thesis = re.search(r"^//\s*THESIS\s+\d+:", text, re.MULTILINE)
    head = text[: first_thesis.start()] if first_thesis else text
    kinds = ("object", "service", "subject", "action", "asset")
    print(f"Foundation region (before first // THESIS <digits>:): {len(head)} chars\n")
    for k in kinds:
        names = re.findall(rf"^{k}\s+(\w+)\s*=", head, re.MULTILINE)
        print(f"{k}: {len(names)}")
        for n in sorted(names)[:15]:
            print(f"  - {n}")
        if len(names) > 15:
            print(f"  ... and {len(names) - 15} more")


if __name__ == "__main__":
    main()
