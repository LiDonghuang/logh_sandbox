#!/usr/bin/env python3
from __future__ import annotations

import copy
import csv
import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
OUT_DIR = Path(__file__).resolve().parent
DOE_SUPPORT_SRC = OUT_DIR / "run_fr_authority_doe.py"

BASELINE_VARIANT_ID = "baseline"
CANDIDATE_VARIANT_ID = "fr_centroid_decouple_candidate"
BASELINE_EXPERIMENT = "exp_precontact_centroid_probe"
CANDIDATE_EXPERIMENT = "exp_precontact_plus_fr_centroid_decouple_probe"
SEED_PROFILE_IDS = {"SP01", "SP09", "SP18"}
TITLE = "FR Centroid Decouple Paired Confirmation"

CELL_SPECS = [
    {"cell_id": "FR2_MB2_PD8_ODW8", "cell_FR": 2, "cell_MB": 2, "cell_PD": 8, "cell_ODW": 8},
    {"cell_id": "FR2_MB8_PD8_ODW8", "cell_FR": 2, "cell_MB": 8, "cell_PD": 8, "cell_ODW": 8},
    {"cell_id": "FR5_MB2_PD8_ODW8", "cell_FR": 5, "cell_MB": 2, "cell_PD": 8, "cell_ODW": 8},
    {"cell_id": "FR5_MB8_PD2_ODW8", "cell_FR": 5, "cell_MB": 8, "cell_PD": 2, "cell_ODW": 8},
    {"cell_id": "FR8_MB5_PD8_ODW2", "cell_FR": 8, "cell_MB": 5, "cell_PD": 8, "cell_ODW": 2},
    {"cell_id": "FR8_MB2_PD2_ODW8", "cell_FR": 8, "cell_MB": 2, "cell_PD": 2, "cell_ODW": 8},
]
VARIANTS = [
    {"variant_id": BASELINE_VARIANT_ID, "experiment": BASELINE_EXPERIMENT},
    {"variant_id": CANDIDATE_VARIANT_ID, "experiment": CANDIDATE_EXPERIMENT},
]


def load_module(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


fr_doe = load_module(DOE_SUPPORT_SRC, "fr_authority_doe_paired_support")


def write_csv(path: Path, rows: list[dict]):
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def bool_like(value) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def mean_or_nan(values) -> float:
    return fr_doe.mean_or_nan(values)


def pick_seed_profiles():
    return [row for row in fr_doe.build_seed_profiles() if row["seed_profile_id"] in SEED_PROFILE_IDS]


def build_variant_settings(base_settings: dict, seed_profile: dict, experiment: str) -> dict:
    settings = copy.deepcopy(base_settings)
    settings.setdefault("run_control", {})["test_mode"] = 2
    settings.setdefault("runtime", {}).setdefault("movement", {}).setdefault("v3a", {})["experiment"] = str(experiment)
    return fr_doe.build_run_settings(settings, seed_profile)


def aggregate_variant(rows: list[dict]) -> dict:
    return {
        "n_runs": len(rows),
        "A_win_rate_pct": fr_doe.a_win_rate(rows),
        "wedge_present_rate_A_pct": fr_doe._true_rate(rows, "wedge_present_A"),
        "structural_fragility_rate_A_pct": fr_doe._true_rate(rows, "structural_fragility_A"),
        "posture_coherence_rate_A_pct": fr_doe._true_rate(rows, "posture_coherence_A"),
        "mean_runtime_c_conn_A": mean_or_nan(row["runtime_c_conn_mean_A"] for row in rows),
        "mean_runtime_collapse_A": mean_or_nan(row["runtime_collapse_sig_mean_A"] for row in rows),
        "mean_fire_eff_A": mean_or_nan(row["fire_eff_contact_to_cut_mean_A"] for row in rows),
        "mean_first_major_divergence_tick": mean_or_nan(row["first_major_divergence_tick"] for row in rows),
        "first_major_divergence_side_A_rate_pct": (
            100.0 * sum(1 for row in rows if str(row.get("first_major_divergence_side")) == "A") / float(len(rows))
            if rows
            else float("nan")
        ),
        "profile_set_A": ",".join(sorted({str(row["front_profile_A"]) for row in rows})),
    }


def build_paired_summary_rows(run_rows: list[dict]) -> list[dict]:
    out = []
    for cell in CELL_SPECS:
        bucket_baseline = [
            row for row in run_rows
            if row["cell_id"] == cell["cell_id"] and row["variant_id"] == BASELINE_VARIANT_ID
        ]
        bucket_candidate = [
            row for row in run_rows
            if row["cell_id"] == cell["cell_id"] and row["variant_id"] == CANDIDATE_VARIANT_ID
        ]
        base = aggregate_variant(bucket_baseline)
        cand = aggregate_variant(bucket_candidate)
        out.append(
            {
                "cell_id": cell["cell_id"],
                "cell_FR": cell["cell_FR"],
                "cell_MB": cell["cell_MB"],
                "cell_PD": cell["cell_PD"],
                "cell_ODW": cell["cell_ODW"],
                "baseline_A_win_rate_pct": base["A_win_rate_pct"],
                "candidate_A_win_rate_pct": cand["A_win_rate_pct"],
                "delta_A_win_rate_pct": cand["A_win_rate_pct"] - base["A_win_rate_pct"],
                "baseline_wedge_present_rate_A_pct": base["wedge_present_rate_A_pct"],
                "candidate_wedge_present_rate_A_pct": cand["wedge_present_rate_A_pct"],
                "delta_wedge_present_rate_A_pct": cand["wedge_present_rate_A_pct"] - base["wedge_present_rate_A_pct"],
                "baseline_structural_fragility_rate_A_pct": base["structural_fragility_rate_A_pct"],
                "candidate_structural_fragility_rate_A_pct": cand["structural_fragility_rate_A_pct"],
                "delta_structural_fragility_rate_A_pct": (
                    cand["structural_fragility_rate_A_pct"] - base["structural_fragility_rate_A_pct"]
                ),
                "baseline_posture_coherence_rate_A_pct": base["posture_coherence_rate_A_pct"],
                "candidate_posture_coherence_rate_A_pct": cand["posture_coherence_rate_A_pct"],
                "baseline_runtime_c_conn_A": base["mean_runtime_c_conn_A"],
                "candidate_runtime_c_conn_A": cand["mean_runtime_c_conn_A"],
                "delta_runtime_c_conn_A": cand["mean_runtime_c_conn_A"] - base["mean_runtime_c_conn_A"],
                "baseline_runtime_collapse_A": base["mean_runtime_collapse_A"],
                "candidate_runtime_collapse_A": cand["mean_runtime_collapse_A"],
                "delta_runtime_collapse_A": cand["mean_runtime_collapse_A"] - base["mean_runtime_collapse_A"],
                "baseline_fire_eff_A": base["mean_fire_eff_A"],
                "candidate_fire_eff_A": cand["mean_fire_eff_A"],
                "delta_fire_eff_A": cand["mean_fire_eff_A"] - base["mean_fire_eff_A"],
                "baseline_first_major_divergence_tick": base["mean_first_major_divergence_tick"],
                "candidate_first_major_divergence_tick": cand["mean_first_major_divergence_tick"],
                "delta_first_major_divergence_tick": (
                    cand["mean_first_major_divergence_tick"] - base["mean_first_major_divergence_tick"]
                ),
                "baseline_first_major_divergence_side_A_rate_pct": base["first_major_divergence_side_A_rate_pct"],
                "candidate_first_major_divergence_side_A_rate_pct": cand["first_major_divergence_side_A_rate_pct"],
                "baseline_profile_set_A": base["profile_set_A"],
                "candidate_profile_set_A": cand["profile_set_A"],
            }
        )
    return out


def build_summary_markdown(summary_rows: list[dict]) -> str:
    reduced_gate_cells = sum(
        1
        for row in summary_rows
        if float(row["candidate_wedge_present_rate_A_pct"]) < float(row["baseline_wedge_present_rate_A_pct"])
    )
    fr2_guardrails_preserved = sum(
        1
        for row in summary_rows
        if int(row["cell_FR"]) == 2 and float(row["candidate_wedge_present_rate_A_pct"]) == 0.0
    )
    fr8_support_cells_preserved = sum(
        1
        for row in summary_rows
        if int(row["cell_FR"]) == 8 and float(row["candidate_wedge_present_rate_A_pct"]) >= 100.0
    )

    lines = [
        f"# {TITLE}",
        "",
        "## Scope",
        "- Variant A: current baseline `exp_precontact_centroid_probe`",
        "- Variant B: test-only `exp_precontact_plus_fr_centroid_decouple_probe` in `test_run` harness",
        "- Candidate change scope: movement-only FR decouple probe; no runtime baseline edit",
        "",
        "## Batch",
        f"- Cells: `{len(CELL_SPECS)}`",
        f"- Variants: `{len(VARIANTS)}`",
        f"- Seed profiles: `{len(SEED_PROFILE_IDS)}`",
        f"- Total runs: `{len(CELL_SPECS) * len(VARIANTS) * len(SEED_PROFILE_IDS)}`",
        "",
        "## High-Level Readout",
        f"- Cells with reduced A-side wedge gate: `{reduced_gate_cells}/{len(summary_rows)}`",
        f"- FR2 guardrails still wedge-free: `{fr2_guardrails_preserved}/2`",
        f"- FR8 support cells still fully wedge-capable: `{fr8_support_cells_preserved}/2`",
        "",
        "## Cell Summary",
        "| Cell | Base Win% | Cand Win% | Base Wedge% | Cand Wedge% | Base Frag% | Cand Frag% | Base c_conn | Cand c_conn | Base Collapse | Cand Collapse | Base Div T | Cand Div T | Base Profile | Cand Profile |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for row in summary_rows:
        lines.append(
            "| {cell} | {bw:.1f} | {cw:.1f} | {bwed:.1f} | {cwed:.1f} | {bfrag:.1f} | {cfrag:.1f} | {bcc:.4f} | {ccc:.4f} | {bcol:.4f} | {ccol:.4f} | {bdiv:.1f} | {cdiv:.1f} | {bprof} | {cprof} |".format(
                cell=row["cell_id"],
                bw=float(row["baseline_A_win_rate_pct"]),
                cw=float(row["candidate_A_win_rate_pct"]),
                bwed=float(row["baseline_wedge_present_rate_A_pct"]),
                cwed=float(row["candidate_wedge_present_rate_A_pct"]),
                bfrag=float(row["baseline_structural_fragility_rate_A_pct"]),
                cfrag=float(row["candidate_structural_fragility_rate_A_pct"]),
                bcc=float(row["baseline_runtime_c_conn_A"]),
                ccc=float(row["candidate_runtime_c_conn_A"]),
                bcol=float(row["baseline_runtime_collapse_A"]),
                ccol=float(row["candidate_runtime_collapse_A"]),
                bdiv=float(row["baseline_first_major_divergence_tick"]),
                cdiv=float(row["candidate_first_major_divergence_tick"]),
                bprof=row["baseline_profile_set_A"],
                cprof=row["candidate_profile_set_A"],
            )
        )
    lines.append("")
    return "\n".join(lines) + "\n"


def main():
    base_settings = fr_doe.load_inputs()
    seed_profiles = pick_seed_profiles()
    run_rows = []
    alive_rows = []

    for cell in CELL_SPECS:
        for variant in VARIANTS:
            for seed_profile in seed_profiles:
                variant_settings = build_variant_settings(base_settings, seed_profile, variant["experiment"])
                row, alive_chunk = fr_doe.run_single_case(
                    variant_settings,
                    seed_profile,
                    cell["cell_FR"],
                    cell["cell_MB"],
                    cell["cell_PD"],
                    cell["cell_ODW"],
                )
                row["cell_id"] = cell["cell_id"]
                row["variant_id"] = variant["variant_id"]
                row["variant_experiment"] = variant["experiment"]
                run_rows.append(row)
                for alive_row in alive_chunk:
                    alive_row["cell_id"] = cell["cell_id"]
                    alive_row["variant_id"] = variant["variant_id"]
                    alive_row["variant_experiment"] = variant["experiment"]
                    alive_rows.append(alive_row)

    run_table_path = OUT_DIR / "fr_centroid_compression_paired_run_table.csv"
    alive_path = OUT_DIR / "fr_centroid_compression_paired_alive_trajectory.csv"
    summary_csv_path = OUT_DIR / "fr_centroid_compression_paired_summary.csv"
    summary_md_path = OUT_DIR / "fr_centroid_compression_paired_summary.md"

    write_csv(run_table_path, run_rows)
    write_csv(alive_path, alive_rows)
    summary_rows = build_paired_summary_rows(run_rows)
    write_csv(summary_csv_path, summary_rows)
    summary_md_path.write_text(build_summary_markdown(summary_rows), encoding="utf-8")

    print(f"[fr_centroid_paired] run_table={run_table_path}")
    print(f"[fr_centroid_paired] summary_csv={summary_csv_path}")
    print(f"[fr_centroid_paired] summary_md={summary_md_path}")


if __name__ == "__main__":
    main()
