#!/usr/bin/env python3
"""
Case vs resolution similarity — one summary table only.

Case similarity: Jaccard on global fact ID sets from witness_export_<n>.json (field assets).
Resolution similarity: Jaccard on sets of ZDD solution lines from zdd_<n>.txt.

Writes:
  - results/analysis/case_resolution_similarity.txt — table (case band vs median resolution %)
  - results/analysis/case_resolution_similarity.png — same data as a line chart
  - results/analysis/thesis_tamano_medio_desviacion.csv — por tesis: hechos en el caso,
    número de líneas ZDD, tamaño medio de cada solución (cardinal del vector testigo),
    desviación estándar de esos tamaños
  - results/analysis/thesis_tamano_medio_desviacion.png — gráfico del tamaño medio ± σ por tesis

Band definitions (raw case Jaccard c), no overlap:
  - Rows 100 and 90: same value — median resolution among all pairs with c >= 0.9
  - 80: [0.8, 0.9)   70: [0.7, 0.8)  …  0: [0.0, 0.1)

  python3 methods/tools/case_resolution_similarity.py
"""
from __future__ import annotations

import ast
import csv
import json
import math
import re
import statistics
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

ROOT = Path(__file__).resolve().parents[2]
WIT = ROOT / "methods" / "analysis" / "unified_legal_conclusions.wit"
WITNESS_EXPORT_DIR = ROOT / "results" / "witness_exports"
ZDD_TXT_DIR = ROOT / "results" / "zdd"
OUT_TABLE = ROOT / "results" / "analysis" / "case_resolution_similarity.txt"
OUT_PNG = ROOT / "results" / "analysis" / "case_resolution_similarity.png"
OUT_THESIS_STATS = ROOT / "results" / "analysis" / "thesis_tamano_medio_desviacion.csv"
OUT_THESIS_PNG = ROOT / "results" / "analysis" / "thesis_tamano_medio_desviacion.png"

_THESIS_ORDER_RE = re.compile(
    r"asset\s+tesis(\d+)_valida\s*=\s*global\(\s*\)\s*;",
    re.MULTILINE,
)


def load_thesis_ids_in_global_order(wit_path: Path) -> List[str]:
    return _THESIS_ORDER_RE.findall(wit_path.read_text(encoding="utf-8", errors="replace"))


def canonical_solution_signature(vals: List[int]) -> str:
    if not vals:
        return "[]"
    s = sorted(vals)
    return f"[{','.join(map(str, s))}]"


def parse_zdd_solution_lengths(path: Path) -> List[int]:
    """Longitud (número de literales positivos) de cada línea solución en zdd_*.txt."""
    lengths: List[int] = []
    text = path.read_text(encoding="utf-8", errors="replace")
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        try:
            v = ast.literal_eval(s)
        except (SyntaxError, ValueError):
            continue
        if not isinstance(v, list):
            continue
        if not v:
            lengths.append(0)
            continue
        if not all(isinstance(x, int) for x in v):
            continue
        lengths.append(len(v))
    return lengths


def parse_zdd_txt(path: Path) -> Set[str]:
    sigs: Set[str] = set()
    text = path.read_text(encoding="utf-8", errors="replace")
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        try:
            v = ast.literal_eval(s)
        except (SyntaxError, ValueError):
            continue
        if not isinstance(v, list):
            continue
        if not v:
            sigs.add("[]")
            continue
        if not all(isinstance(x, int) for x in v):
            continue
        sigs.add(canonical_solution_signature(v))
    return sigs


def load_case_and_resolution_per_thesis(
    wit_path: Path, exports_dir: Path, zdd_txt_dir: Path
) -> Tuple[
    Dict[str, Set[int]],
    Dict[str, Set[str]],
    List[int],
    Dict[str, int],
]:
    ordered_ids = load_thesis_ids_in_global_order(wit_path)
    case_map: Dict[str, Set[int]] = {}
    res_map: Dict[str, Set[str]] = {}
    thesis_zdd_index: Dict[str, int] = {}
    used_zdd: List[int] = []

    for path in sorted(zdd_txt_dir.glob("zdd_*.txt")):
        m = re.fullmatch(r"zdd_(\d+)", path.stem)
        if not m:
            continue
        zdd_id = int(m.group(1))
        if zdd_id < 1 or zdd_id > len(ordered_ids):
            print(
                f"Warning: {path.name} out of range (no matching thesis slot in .wit order).",
                file=sys.stderr,
            )
            continue
        registry_id = ordered_ids[zdd_id - 1]
        wjson = exports_dir / f"witness_export_{zdd_id}.json"
        if not wjson.is_file():
            print(f"Warning: skip {registry_id}: missing {wjson.name}", file=sys.stderr)
            continue
        data = json.loads(wjson.read_text(encoding="utf-8"))
        raw_assets = data.get("assets")
        if not isinstance(raw_assets, list):
            print(f"Warning: skip {registry_id}: witness export has no list 'assets'", file=sys.stderr)
            continue
        case_map[registry_id] = set(int(x) for x in raw_assets)
        res_map[registry_id] = parse_zdd_txt(path)
        thesis_zdd_index[registry_id] = zdd_id
        used_zdd.append(zdd_id)

    return case_map, res_map, used_zdd, thesis_zdd_index


def jaccard(a: Set, b: Set) -> float:
    if not a and not b:
        return 1.0
    u = len(a | b)
    if u == 0:
        return 0.0
    return len(a & b) / u


def main() -> None:
    if not WIT.is_file():
        print(f"Missing unified model: {WIT}", file=sys.stderr)
        sys.exit(1)
    if not ZDD_TXT_DIR.is_dir():
        print(f"Missing ZDD text directory: {ZDD_TXT_DIR}", file=sys.stderr)
        sys.exit(1)
    if not WITNESS_EXPORT_DIR.is_dir():
        print(f"Missing witness exports directory: {WITNESS_EXPORT_DIR}", file=sys.stderr)
        sys.exit(1)

    case_assets, zdd_sigs, used_zdd, thesis_zdd_index = load_case_and_resolution_per_thesis(
        WIT, WITNESS_EXPORT_DIR, ZDD_TXT_DIR
    )

    ids = sorted(set(case_assets.keys()) & set(zdd_sigs.keys()), key=lambda x: int(x))
    print(
        f"Loaded {len(ids)} thesis(es) (zdd {min(used_zdd)}…{max(used_zdd)}, {len(used_zdd)} files).",
        file=sys.stderr,
    )

    if not ids:
        print("No overlapping thesis data; exiting.", file=sys.stderr)
        sys.exit(1)

    stat_rows: List[Dict[str, object]] = []
    for tid in ids:
        zid = thesis_zdd_index[tid]
        zpath = ZDD_TXT_DIR / f"zdd_{zid}.txt"
        lengths = parse_zdd_solution_lengths(zpath)
        n_facts = len(case_assets[tid])
        n_lines = len(lengths)
        if lengths:
            mean_sz = statistics.mean(lengths)
            dev_sz = statistics.stdev(lengths) if len(lengths) > 1 else 0.0
        else:
            mean_sz = 0.0
            dev_sz = 0.0
        stat_rows.append(
            {
                "tesis_numero_registro": tid,
                "indice_zdd": zid,
                "numero_hechos_caso": n_facts,
                "numero_soluciones_zdd": n_lines,
                "tamano_medio_vector_testigo": round(mean_sz, 6),
                "desviacion_estandar_tamano_vector": round(dev_sz, 6),
            }
        )

    with open(OUT_THESIS_STATS, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(stat_rows[0].keys()))
        w.writeheader()
        w.writerows(stat_rows)
    print(str(OUT_THESIS_STATS.relative_to(ROOT)))

    ge_090: List[float] = []
    by_band: Dict[int, list] = defaultdict(list)
    for i, ti in enumerate(ids):
        for tj in ids[i + 1 :]:
            ai, aj = case_assets[ti], case_assets[tj]
            si, sj = zdd_sigs[ti], zdd_sigs[tj]
            cj = jaccard(ai, aj)
            rj = jaccard(si, sj)
            if cj >= 0.9 - 1e-15:
                ge_090.append(rj)
                continue
            idx = min(9, int(math.floor(cj * 10.0 + 1e-15)))
            lab = idx * 10
            by_band[lab].append(rj)

    def median_resolution_pct(vals: List[float]) -> Optional[float]:
        if not vals:
            return None
        return round(statistics.median(vals) * 100.0)

    top_pct = median_resolution_pct(ge_090)

    def y_for_label(lab: int) -> float:
        if lab == 100 or lab == 90:
            return float("nan") if top_pct is None else float(top_pct)
        p = median_resolution_pct(by_band.get(lab, []))
        return float("nan") if p is None else float(p)

    # Table: median resolution similarity (percent), rows 100 down to 0
    lines_out: List[str] = []
    for lab in range(100, -1, -10):
        if lab in (100, 90):
            cell = "n/a" if top_pct is None else f"{top_pct}%"
        else:
            p = median_resolution_pct(by_band.get(lab, []))
            cell = "n/a" if p is None else f"{p}%"
        lines_out.append(f"{lab} - {cell}")

    OUT_TABLE.parent.mkdir(parents=True, exist_ok=True)
    OUT_TABLE.write_text("\n".join(lines_out) + "\n", encoding="utf-8")
    print(str(OUT_TABLE.relative_to(ROOT)))

    try:
        import matplotlib.pyplot as plt

        xs = list(range(0, 101, 10))
        ys = [y_for_label(k) for k in xs]
        plt.figure(figsize=(10, 5))
        plt.plot(xs, ys, marker="o", linewidth=2, markersize=8, color="C0")
        plt.xlabel("Case similarity band (% Jaccard on witness fact IDs)")
        plt.ylabel("Median resolution similarity (%)")
        plt.title("Resolution similarity vs case-similarity band")
        plt.xticks(xs)
        plt.xlim(-5, 105)
        plt.ylim(0, 105)
        plt.grid(True, alpha=0.35)
        plt.tight_layout()
        plt.savefig(OUT_PNG, dpi=150)
        plt.close()
        print(str(OUT_PNG.relative_to(ROOT)))

        stat_sorted = sorted(stat_rows, key=lambda r: int(r["indice_zdd"]))
        xz = [int(r["indice_zdd"]) for r in stat_sorted]
        means = [float(r["tamano_medio_vector_testigo"]) for r in stat_sorted]
        stdevs = [float(r["desviacion_estandar_tamano_vector"]) for r in stat_sorted]
        plt.figure(figsize=(14, 5))
        plt.errorbar(
            xz,
            means,
            yerr=stdevs,
            fmt="o",
            markersize=3,
            capsize=1.5,
            elinewidth=0.85,
            color="C0",
            alpha=0.88,
            label="Media ± σ",
        )
        plt.xlabel("Índice ZDD (orden de global() en el modelo)")
        plt.ylabel("Longitud del vector testigo (literales por solución)")
        plt.title(
            "Tamaño medio y desviación estándar del vector testigo por tesis "
            "(sobre todas las líneas del zdd_*.txt correspondiente)"
        )
        plt.grid(True, alpha=0.35)
        plt.legend(loc="upper left")
        plt.tight_layout()
        plt.savefig(OUT_THESIS_PNG, dpi=150)
        plt.close()
        print(str(OUT_THESIS_PNG.relative_to(ROOT)))
    except ImportError:
        print("matplotlib not installed; skipped plot. pip install matplotlib", file=sys.stderr)


if __name__ == "__main__":
    main()
