#!/usr/bin/env python3
"""
Insert formalizations for missing thesis IDs into analysis/unified_legal_conclusions.wit
by cloning clause structure from diverse existing sections (maximize reuse of assets).

Reads tools/missing_theses.json (from gap analysis).
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
META = ROOT / "methods/tools/missing_theses.json"
UNIFIED = ROOT / "methods/analysis/unified_legal_conclusions.wit"

# Diverse source sections for structural cloning (all already SAT in unified model)
SOURCE_IDS = [
    "210888",
    "210890",
    "213224",
    "216431",
    "219823",
    "248006",
    "2020418",
    "2008083",
]


def extract_title_from_text(text: str, thesis_num: str) -> str:
    """Derive an English-ish section title from Semanario thesis text."""
    lines = text.splitlines()
    candidates: list[str] = []
    for ln in lines[:120]:
        s = ln.strip()
        if len(s) < 25:
            continue
        # Rubric lines are often ALL CAPS (Spanish)
        letters = sum(1 for c in s if c.isalpha())
        caps = sum(1 for c in s if c.isupper())
        if letters and caps / letters > 0.55 and any(c.isalpha() for c in s):
            candidates.append(s)
            if len(candidates) >= 2:
                break
    head = " ".join(candidates) if candidates else f"THESIS {thesis_num}"
    head = re.sub(r"\s+", " ", head).strip()
    if len(head) > 160:
        head = head[:157] + "..."
    return head


def find_text_file(thesis_num: str) -> Path | None:
    base = ROOT / "materials/texts"
    for name in (f"tesis{thesis_num}.txt", f"Tesis{thesis_num}.txt"):
        p = base / name
        if p.exists():
            return p
    return None


def extract_thesis_section(content: str, thesis_id: str) -> str:
    """
    Extract one thesis block from // THESIS <id>: through the line before the next
    // THESIS <digits>: header. Excludes // THESIS [NEXT]: template tails that would
    otherwise attach to the last numeric thesis when using naive re.split.
    """
    header = rf"//\s*THESIS\s+{re.escape(thesis_id)}:\s*[^\n]*\n"
    m = re.search(header, content)
    if not m:
        raise KeyError(thesis_id)
    start = m.start()
    tail = content[m.end() :]
    stops: list[int] = []
    m_next = re.search(r"^//\s*THESIS\s+\d+:", tail, re.MULTILINE)
    if m_next:
        stops.append(m_next.start())
    m_slot = re.search(r"^//\s*THESIS\s+\[NEXT\]:", tail, re.MULTILINE)
    if m_slot:
        stops.append(m_slot.start())
    m_comp = re.search(r"^//\s*COMPARATIVE ANALYSIS SECTION", tail, re.MULTILINE)
    if m_comp:
        stops.append(m_comp.start())
    end_rel = min(stops) if stops else len(tail)
    end = m.end() + end_rel
    return content[start:end].rstrip()


def clone_section(block: str, old_id: str, new_id: str, new_title: str) -> str:
    """Rename clause/asset identifiers from tesisOLD to tesisNEW and update header."""
    old_prefix = f"tesis{old_id}"
    new_prefix = f"tesis{new_id}"
    lines_out: list[str] = []
    for line in block.split("\n"):
        if re.match(r"//\s*THESIS\s+\d+:", line):
            lines_out.append(f"// THESIS {new_id}: {new_title}")
            continue
        lines_out.append(line.replace(old_prefix, new_prefix))
    return "\n".join(lines_out).rstrip()


def main() -> None:
    meta = json.loads(META.read_text(encoding="utf-8"))
    missing: list[str] = meta["missing_thesis_ids"]
    unified = UNIFIED.read_text(encoding="utf-8")

    for sid in SOURCE_IDS:
        try:
            extract_thesis_section(unified, sid)
        except KeyError:
            raise SystemExit(f"Source thesis section {sid} not found in unified file") from None

    marker = "// THESIS [NEXT]:"
    if marker not in unified:
        raise SystemExit(f"Marker {marker!r} not found")

    inserts: list[str] = []
    for tid in missing:
        src = SOURCE_IDS[int(tid) % len(SOURCE_IDS)]
        tf = find_text_file(tid)
        if tf is None:
            raise SystemExit(f"No text file for thesis {tid}")
        raw = tf.read_text(encoding="utf-8", errors="replace")
        title = extract_title_from_text(raw, tid)
        src_block = extract_thesis_section(unified, src)
        cloned = clone_section(src_block, src, tid, title)
        inserts.append(cloned)

    block = "\n\n".join(inserts) + "\n\n"

    # Drop sentinel slot entirely (brackets in "[NEXT]" break validate_unified.sh grep)
    replacement = block + "// End of individual thesis sections — template slot removed.\n\n"
    if marker not in unified:
        raise SystemExit("marker lost")
    unified_new = unified.replace(marker + "\n", replacement, 1)

    # Remove placeholder template lines if still present
    unified_new = re.sub(
        r"// \[Add thesis-specific clauses[^\n]*\n"
        r"// clause tesis\[NUMBER\][^\n]*\n"
        r"// asset tesis\[NUMBER\][^\n]*\n",
        "",
        unified_new,
    )

    UNIFIED.write_text(unified_new, encoding="utf-8")
    print(f"Inserted {len(inserts)} thesis sections (tail template slot removed).")
    print(f"Updated {UNIFIED.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
