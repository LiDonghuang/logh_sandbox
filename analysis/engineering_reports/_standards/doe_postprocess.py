#!/usr/bin/env python3
"""
DOE postprocess utility.

Generates mandatory DOE summary sections:
1) Cell-level main effects table
2) Factor main-effect check (FR/MB/PD)
3) Opponent hardness table
4) Censoring/cap sensitivity note
5) Standards compliance block
"""

from __future__ import annotations

import argparse
import csv
import math
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any


SCRIPT_VERSION = "1.0.0"
TOL = 1e-9


def _pick_col(columns: list[str], candidates: list[str]) -> str | None:
    lower_map = {c.lower(): c for c in columns}
    for cand in candidates:
        key = cand.lower()
        if key in lower_map:
            return lower_map[key]
    return None


def _to_float(raw: Any) -> float | None:
    if raw is None:
        return None
    text = str(raw).strip()
    if text == "" or text.upper() == "N/A":
        return None
    try:
        value = float(text)
    except ValueError:
        return None
    if not math.isfinite(value):
        return None
    return value


def _to_int(raw: Any) -> int | None:
    fv = _to_float(raw)
    if fv is None:
        return None
    iv = int(fv)
    return iv


def _mean(values: list[float | None]) -> float | None:
    data = [v for v in values if v is not None]
    if not data:
        return None
    return sum(data) / len(data)


def _median(values: list[float | None]) -> float | None:
    data = [v for v in values if v is not None]
    if not data:
        return None
    return float(statistics.median(data))


def _rate_true(rows: list[dict], pred) -> float | None:
    if not rows:
        return None
    return (100.0 * sum(1 for row in rows if pred(row))) / len(rows)


def _fmt(value: float | int | None, digits: int = 3) -> str:
    if value is None:
        return "N/A"
    if isinstance(value, int):
        return str(value)
    if abs(value - round(value)) <= 1e-12:
        return f"{value:.0f}"
    return f"{value:.{digits}f}"


def _safe_sorted_keys(keys: list[tuple]) -> list[tuple]:
    def _key(x: tuple):
        out = []
        for v in x:
            if v is None:
                out.append((1, 0))
            else:
                out.append((0, v))
        return tuple(out)

    return sorted(keys, key=_key)


def _signature_close(a: list[tuple], b: list[tuple], tol: float = 1e-6) -> bool:
    if len(a) != len(b):
        return False
    for (ka, va), (kb, vb) in zip(a, b):
        if ka != kb:
            return False
        if va is None and vb is None:
            continue
        if (va is None) != (vb is None):
            return False
        if abs(float(va) - float(vb)) > tol:
            return False
    return True


def _load_run_rows(run_table_path: Path) -> list[dict]:
    with run_table_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows_raw = list(reader)
        if not rows_raw:
            raise ValueError("run table is empty")
        cols = list(reader.fieldnames or [])

    col_fr = _pick_col(cols, ["cell_FR", "FR", "fr"])
    col_mb = _pick_col(cols, ["cell_MB", "MB", "mb"])
    col_pd = _pick_col(cols, ["cell_PD", "PD", "pd"])
    col_model = _pick_col(cols, ["movement_model", "model"])
    col_opp = _pick_col(
        cols,
        ["opponent_archetype_id", "opponent_id", "archetype_B", "B_id", "opponent"],
    )
    col_winner = _pick_col(cols, ["winner", "Winner"])
    col_end = _pick_col(cols, ["end_tick", "EndTick"])
    col_ra = _pick_col(cols, ["remaining_units_A", "final_alive_A", "remaining_A"])
    col_rb = _pick_col(cols, ["remaining_units_B", "final_alive_B", "remaining_B"])
    col_fc = _pick_col(cols, ["first_contact_tick", "FirstContact", "first_contact"])
    col_fk = _pick_col(cols, ["first_kill_tick", "FirstKill", "first_kill"])
    col_cut = _pick_col(
        cols,
        ["tactical_cut_tick_T", "TacticalCutTick", "cut_tick_T", "formation_cut_tick"],
    )
    col_pocket = _pick_col(
        cols,
        [
            "tactical_pocket_tick_T",
            "TacticalPocketTick",
            "pocket_tick_T",
            "pocket_formation_tick",
        ],
    )

    required = [("FR", col_fr), ("MB", col_mb), ("PD", col_pd), ("end_tick", col_end)]
    missing = [name for name, col in required if col is None]
    if missing:
        raise ValueError(f"run table missing required columns: {missing}")

    rows: list[dict] = []
    for raw in rows_raw:
        rows.append(
            {
                "fr": _to_int(raw.get(col_fr)),
                "mb": _to_int(raw.get(col_mb)),
                "pd": _to_int(raw.get(col_pd)),
                "model": str(raw.get(col_model, "all")).strip() if col_model else "all",
                "opp": str(raw.get(col_opp, "N/A")).strip() if col_opp else "N/A",
                "winner": str(raw.get(col_winner, "")).strip() if col_winner else "",
                "end_tick": _to_float(raw.get(col_end)),
                "remain_a": _to_float(raw.get(col_ra)),
                "remain_b": _to_float(raw.get(col_rb)),
                "first_contact": _to_float(raw.get(col_fc)),
                "first_kill": _to_float(raw.get(col_fk)),
                "cut_tick_t": _to_float(raw.get(col_cut)),
                "pocket_tick_t": _to_float(raw.get(col_pocket)),
            }
        )
    return rows


def _load_delta_rows(delta_table_path: Path) -> list[dict]:
    with delta_table_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows_raw = list(reader)
        if not rows_raw:
            return []
        cols = list(reader.fieldnames or [])

    col_fr = _pick_col(cols, ["cell_FR", "FR", "fr"])
    col_mb = _pick_col(cols, ["cell_MB", "MB", "mb"])
    col_pd = _pick_col(cols, ["cell_PD", "PD", "pd"])
    col_opp = _pick_col(cols, ["opponent_archetype_id", "opponent_id", "archetype_B", "B_id"])
    col_d_end = _pick_col(cols, ["delta_end_tick_v3a_minus_v1", "delta_end_tick"])
    col_d_cut = _pick_col(cols, ["delta_tactical_cut_tick_T_v3a_minus_v1", "delta_cut_tick"])
    col_d_pocket = _pick_col(
        cols,
        ["delta_tactical_pocket_tick_T_v3a_minus_v1", "delta_pocket_tick"],
    )

    required = [("FR", col_fr), ("MB", col_mb), ("PD", col_pd), ("d_end", col_d_end)]
    missing = [name for name, col in required if col is None]
    if missing:
        return []

    rows: list[dict] = []
    for raw in rows_raw:
        rows.append(
            {
                "fr": _to_int(raw.get(col_fr)),
                "mb": _to_int(raw.get(col_mb)),
                "pd": _to_int(raw.get(col_pd)),
                "opp": str(raw.get(col_opp, "N/A")).strip() if col_opp else "N/A",
                "d_end": _to_float(raw.get(col_d_end)),
                "d_cut": _to_float(raw.get(col_d_cut)),
                "d_pocket": _to_float(raw.get(col_d_pocket)),
            }
        )
    return rows


def _infer_delta_rows(run_rows: list[dict]) -> list[dict]:
    grouped: dict[tuple, list[dict]] = defaultdict(list)
    for row in run_rows:
        key = (row["fr"], row["mb"], row["pd"], row["opp"])
        grouped[key].append(row)

    out: list[dict] = []
    for (fr, mb, pd, opp), rows in grouped.items():
        by_model = {r["model"].lower(): r for r in rows if r.get("model")}
        if "v1" not in by_model or "v3a" not in by_model:
            continue
        v1 = by_model["v1"]
        v3 = by_model["v3a"]
        out.append(
            {
                "fr": fr,
                "mb": mb,
                "pd": pd,
                "opp": opp,
                "d_end": (v3["end_tick"] - v1["end_tick"])
                if v3["end_tick"] is not None and v1["end_tick"] is not None
                else None,
                "d_cut": (v3["cut_tick_t"] - v1["cut_tick_t"])
                if v3["cut_tick_t"] is not None and v1["cut_tick_t"] is not None
                else None,
                "d_pocket": (v3["pocket_tick_t"] - v1["pocket_tick_t"])
                if v3["pocket_tick_t"] is not None and v1["pocket_tick_t"] is not None
                else None,
            }
        )
    return out


def build_summary_markdown(
    *,
    title: str,
    run_rows: list[dict],
    delta_rows: list[dict],
    standards_version: str,
    deviations: str,
) -> str:
    md: list[str] = []
    md.append(f"# {title}")
    md.append("")
    md.append("## Standards Compliance")
    md.append(f"- Standards version: `{standards_version}`")
    md.append(f"- Stats script: `doe_postprocess.py v{SCRIPT_VERSION}`")
    md.append(f"- Deviations: `{deviations}`")
    md.append("")

    # Section 1: Cell-level main effects.
    md.append("## 1. Cell-level Main Effects")
    md.append(
        "| Cell | n | A win rate (%) | Mean survivors A | Mean survivors B | Median end_tick | Mean Cut_T | Mean Pocket_T | Delta end (v3a-v1) | Delta Cut_T (v3a-v1) | Delta Pocket_T (v3a-v1) |"
    )
    md.append("| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")

    delta_by_cell: dict[tuple, list[dict]] = defaultdict(list)
    for dr in delta_rows:
        delta_by_cell[(dr["fr"], dr["mb"], dr["pd"])].append(dr)

    cell_map: dict[tuple, list[dict]] = defaultdict(list)
    for row in run_rows:
        cell_map[(row["fr"], row["mb"], row["pd"])].append(row)
    for cell in _safe_sorted_keys(list(cell_map.keys())):
        rows = cell_map[cell]
        drs = delta_by_cell.get(cell, [])
        md.append(
            "| FR{fr}_MB{mb}_PD{pd} | {n} | {w} | {sa} | {sb} | {med_end} | {cut} | {pocket} | {de} | {dc} | {dp} |".format(
                fr=cell[0],
                mb=cell[1],
                pd=cell[2],
                n=len(rows),
                w=_fmt(_rate_true(rows, lambda r: str(r["winner"]).upper() == "A"), 1),
                sa=_fmt(_mean([r["remain_a"] for r in rows])),
                sb=_fmt(_mean([r["remain_b"] for r in rows])),
                med_end=_fmt(_median([r["end_tick"] for r in rows])),
                cut=_fmt(_mean([r["cut_tick_t"] for r in rows])),
                pocket=_fmt(_mean([r["pocket_tick_t"] for r in rows])),
                de=_fmt(_mean([d["d_end"] for d in drs])),
                dc=_fmt(_mean([d["d_cut"] for d in drs])),
                dp=_fmt(_mean([d["d_pocket"] for d in drs])),
            )
        )
    md.append("")

    # Section 2: Factor main-effect check.
    md.append("## 2. Factor Main-Effect Check")
    factors = [("FR", "fr"), ("MB", "mb"), ("PD", "pd")]
    for factor_name, fk in factors:
        md.append(f"### {factor_name}")
        levels = sorted({r[fk] for r in run_rows if r[fk] is not None})
        if len(levels) < 2:
            md.append(f"- Status: not testable (single level: {levels[0] if levels else 'N/A'}).")
            md.append("")
            continue

        md.append("| Level | n | A win rate (%) | Mean survivors A | Median end_tick | Mean Cut_T | Mean Pocket_T |")
        md.append("| --- | ---: | ---: | ---: | ---: | ---: | ---: |")
        level_rows: dict[int, list[dict]] = defaultdict(list)
        for r in run_rows:
            level_rows[r[fk]].append(r)
        per_level_metrics: dict[int, dict[str, float | None]] = {}
        for lv in levels:
            rows = level_rows[lv]
            met = {
                "win": _rate_true(rows, lambda r: str(r["winner"]).upper() == "A"),
                "surv_a": _mean([r["remain_a"] for r in rows]),
                "med_end": _median([r["end_tick"] for r in rows]),
                "cut": _mean([r["cut_tick_t"] for r in rows]),
                "pocket": _mean([r["pocket_tick_t"] for r in rows]),
            }
            per_level_metrics[lv] = met
            md.append(
                "| {lv} | {n} | {w} | {sa} | {me} | {cut} | {pocket} |".format(
                    lv=lv,
                    n=len(rows),
                    w=_fmt(met["win"], 1),
                    sa=_fmt(met["surv_a"]),
                    me=_fmt(met["med_end"]),
                    cut=_fmt(met["cut"]),
                    pocket=_fmt(met["pocket"]),
                )
            )

        no_effect_metrics: list[str] = []
        for mkey, mlabel in [
            ("win", "win_rate"),
            ("surv_a", "mean_survivors_A"),
            ("med_end", "median_end_tick"),
            ("cut", "mean_cut_tick_T"),
            ("pocket", "mean_pocket_tick_T"),
        ]:
            vals = [per_level_metrics[lv][mkey] for lv in levels]
            vals = [v for v in vals if v is not None]
            if not vals:
                continue
            if max(vals) - min(vals) <= TOL:
                no_effect_metrics.append(mlabel)

        # Duplication-pattern check against other-factor slices.
        other_keys = [k for _, k in factors if k != fk]
        signatures: dict[int, list[tuple]] = {}
        for lv in levels:
            rows = [r for r in run_rows if r[fk] == lv]
            sig_map: dict[tuple, list[dict]] = defaultdict(list)
            for r in rows:
                sig_map[(r[other_keys[0]], r[other_keys[1]])].append(r)
            signature = []
            for ok in _safe_sorted_keys(list(sig_map.keys())):
                rr = sig_map[ok]
                signature.append((ok, _rate_true(rr, lambda x: str(x["winner"]).upper() == "A")))
            signatures[lv] = signature

        duplication_detected = True
        base_sig = signatures.get(levels[0], [])
        for lv in levels[1:]:
            if not _signature_close(base_sig, signatures.get(lv, []), tol=1e-6):
                duplication_detected = False
                break

        if no_effect_metrics:
            md.append(f"- No observable main effect metrics: `{', '.join(no_effect_metrics)}`")
        else:
            md.append("- No observable main effect metrics: `none`")
        md.append(f"- Duplication pattern detected across {factor_name} levels: `{duplication_detected}`")
        md.append("")

    # Section 3: Opponent hardness.
    md.append("## 3. Opponent Hardness Table")
    md.append("| Opponent | n | A win rate all (%) | A win rate v1 (%) | A win rate v3a (%) | Median end_tick | Mean survivors A | Mean survivors B |")
    md.append("| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
    opp_map: dict[str, list[dict]] = defaultdict(list)
    for row in run_rows:
        opp_map[row["opp"]].append(row)

    def _opp_sort_key(opp: str) -> tuple:
        rows = opp_map[opp]
        wr = _rate_true(rows, lambda r: str(r["winner"]).upper() == "A")
        return (wr if wr is not None else 999.0, opp)

    for opp in sorted(opp_map.keys(), key=_opp_sort_key):
        rows = opp_map[opp]
        rows_v1 = [r for r in rows if str(r["model"]).lower() == "v1"]
        rows_v3 = [r for r in rows if str(r["model"]).lower() == "v3a"]
        md.append(
            "| {opp} | {n} | {w_all} | {w1} | {w3} | {med_end} | {sa} | {sb} |".format(
                opp=opp,
                n=len(rows),
                w_all=_fmt(_rate_true(rows, lambda r: str(r["winner"]).upper() == "A"), 1),
                w1=_fmt(_rate_true(rows_v1, lambda r: str(r["winner"]).upper() == "A"), 1),
                w3=_fmt(_rate_true(rows_v3, lambda r: str(r["winner"]).upper() == "A"), 1),
                med_end=_fmt(_median([r["end_tick"] for r in rows])),
                sa=_fmt(_mean([r["remain_a"] for r in rows])),
                sb=_fmt(_mean([r["remain_b"] for r in rows])),
            )
        )
    md.append("")

    # Section 4: Censoring/cap sensitivity.
    md.append("## 4. Censoring/Cap Sensitivity Note")
    end_ticks = [r["end_tick"] for r in run_rows if r["end_tick"] is not None]
    if not end_ticks:
        md.append("- No valid end_tick values found.")
        md.append("- Duration sensitivity check: `unknown`.")
    else:
        max_end = max(end_ticks)
        cap_hits = [r for r in run_rows if r["end_tick"] is not None and abs(r["end_tick"] - max_end) <= TOL]
        cap_rate = (100.0 * len(cap_hits) / len(run_rows)) if run_rows else 0.0
        low_sensitivity = len(cap_hits) > 0
        md.append(f"- Observed max end_tick: `{_fmt(max_end)}`")
        md.append(f"- Runs at observed max end_tick: `{len(cap_hits)}/{len(run_rows)}` (`{_fmt(cap_rate, 1)}%`)")
        md.append(f"- Duration metrics low sensitivity: `{low_sensitivity}`")
        if low_sensitivity:
            md.append("- Recommendation: prioritize event-time metrics (contact/kill/cut/pocket) over duration-only comparisons.")

    return "\n".join(md) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-table", required=True, help="Path to DOE run table CSV.")
    parser.add_argument("--delta-table", default="", help="Path to DOE delta table CSV (optional).")
    parser.add_argument("--summary-out", required=True, help="Path to output summary markdown.")
    parser.add_argument("--title", default="DOE Summary", help="Summary document title.")
    parser.add_argument(
        "--standards-version",
        default="DOE_Report_Standard_v1.0 + BRF_Export_Standard_v1.0",
        help="Standards version note for compliance block.",
    )
    parser.add_argument(
        "--deviations",
        default="No deviations",
        help="Deviation note for compliance block.",
    )
    args = parser.parse_args()

    run_table_path = Path(args.run_table).resolve()
    summary_out_path = Path(args.summary_out).resolve()
    delta_table_path = Path(args.delta_table).resolve() if args.delta_table else None

    run_rows = _load_run_rows(run_table_path)
    if delta_table_path and delta_table_path.exists():
        delta_rows = _load_delta_rows(delta_table_path)
    else:
        delta_rows = []
    if not delta_rows:
        delta_rows = _infer_delta_rows(run_rows)

    content = build_summary_markdown(
        title=args.title,
        run_rows=run_rows,
        delta_rows=delta_rows,
        standards_version=args.standards_version,
        deviations=args.deviations,
    )
    summary_out_path.parent.mkdir(parents=True, exist_ok=True)
    summary_out_path.write_text(content, encoding="utf-8")

    print(f"[doe_postprocess] script_version={SCRIPT_VERSION}")
    print(f"[doe_postprocess] run_table={run_table_path}")
    print(f"[doe_postprocess] delta_table={delta_table_path if delta_table_path else 'N/A'}")
    print(f"[doe_postprocess] summary_out={summary_out_path}")


if __name__ == "__main__":
    main()
