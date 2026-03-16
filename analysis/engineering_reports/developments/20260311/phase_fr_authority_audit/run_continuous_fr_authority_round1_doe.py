#!/usr/bin/env python3
from __future__ import annotations

import copy
import csv
import importlib.util
import math
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
OUT_DIR = Path(__file__).resolve().parent
SETTINGS_PATH = ROOT / "test_run" / "test_run_v1_0.settings.json"
BASELINE_ANCHOR_RUN_TABLE = OUT_DIR / "fr_authority_doe_run_table.csv"
BASE_DOE_SRC = OUT_DIR / "run_fr_authority_doe.py"

SELECTED_SEED_PROFILE_IDS = {"SP01", "SP09", "SP18"}
ROUND1_CONTROL_CELLS = [
    (2, 2, 8, 8),
    (2, 8, 8, 8),
    (8, 2, 2, 8),
    (8, 5, 8, 2),
]
ROUND1_FR5_CELLS = [(5, mb, pd, odw) for mb in (2, 5, 8) for pd in (2, 5, 8) for odw in (2, 8)]
ROUND1_CELLS = ROUND1_FR5_CELLS + ROUND1_CONTROL_CELLS
ROUND1_CELL_IDS = {
    f"FR{fr}_MB{mb}_PD{pd}_ODW{odw}"
    for fr, mb, pd, odw in ROUND1_CELLS
}
PD8_SENTINEL_CELL_IDS = {
    "FR5_MB2_PD8_ODW8",
    "FR5_MB5_PD8_ODW8",
}
PROTECTED_CELL_ID = "FR5_MB8_PD2_ODW8"
PD5_MB8_SHOULDER_CELL_IDS = {
    "FR5_MB8_PD5_ODW2",
    "FR5_MB8_PD5_ODW8",
}
CANDIDATE_C_FIXED_BETA = 1.5
TITLE = "Continuous FR Authority Shaping Round 1 DOE"
RUN_TABLE_PATH = OUT_DIR / "continuous_fr_authority_round1_run_table.csv"
SUMMARY_CSV_PATH = OUT_DIR / "continuous_fr_authority_round1_candidate_summary.csv"
RANKED_CSV_PATH = OUT_DIR / "continuous_fr_authority_round1_ranked_candidates.csv"
CONSTRAINT_CSV_PATH = OUT_DIR / "continuous_fr_authority_round1_hard_constraints.csv"
SUMMARY_MD_PATH = OUT_DIR / "continuous_fr_authority_round1_summary.md"
CHECKPOINT_FLUSH_INTERVAL = 25


def load_module(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


base_doe = load_module(BASE_DOE_SRC, "continuous_fr_authority_base_doe")
test_run = base_doe.test_run


def cell_id(fr: int, mb: int, pd: int, odw: int) -> str:
    return f"FR{int(fr)}_MB{int(mb)}_PD{int(pd)}_ODW{int(odw)}"


def cell_id_from_row(row: dict[str, Any]) -> str:
    return cell_id(int(row["cell_FR"]), int(row["cell_MB"]), int(row["cell_PD"]), int(row["cell_ODW"]))


def as_float(value: Any, default: float = float("nan")) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return default
    return result if math.isfinite(result) else default


def as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    text = str(value).strip().lower()
    if text in {"1", "true", "yes"}:
        return True
    if text in {"0", "false", "no", "", "n/a", "nan"}:
        return False
    return bool(value)


def mean_or_nan(values: list[Any]) -> float:
    vals = [as_float(value) for value in values if math.isfinite(as_float(value))]
    if not vals:
        return float("nan")
    return sum(vals) / float(len(vals))


def true_rate(rows: list[dict[str, Any]], key: str) -> float:
    if not rows:
        return float("nan")
    hits = sum(1 for row in rows if as_bool(row.get(key)))
    return 100.0 * float(hits) / float(len(rows))


def a_win_rate(rows: list[dict[str, Any]]) -> float:
    if not rows:
        return float("nan")
    wins = sum(1 for row in rows if str(row.get("winner", "")).upper() == "A")
    return 100.0 * float(wins) / float(len(rows))


def build_round1_candidates() -> list[dict[str, Any]]:
    candidates = []
    for a in (0.25, 0.45, 0.65):
        for sigma in (0.10, 0.15, 0.20):
            for q in (1.0, 2.0):
                candidates.append(
                    {
                        "candidate_id": f"A_a{int(round(a * 100)):03d}_s{int(round(sigma * 100)):03d}_q{int(q)}",
                        "family": "A",
                        "mode": test_run.CONTINUOUS_FR_SHAPING_CANDIDATE_A,
                        "a": a,
                        "sigma": sigma,
                        "p": 1.0,
                        "q": q,
                        "beta": 0.0,
                        "gamma": 0.0,
                    }
                )
    for a in (0.25, 0.45, 0.65):
        for sigma in (0.10, 0.15):
            for beta in (1.5, 3.0):
                candidates.append(
                    {
                        "candidate_id": (
                            f"B_a{int(round(a * 100)):03d}_s{int(round(sigma * 100)):03d}_"
                            f"b{int(round(beta * 10)):02d}"
                        ),
                        "family": "B",
                        "mode": test_run.CONTINUOUS_FR_SHAPING_CANDIDATE_B,
                        "a": a,
                        "sigma": sigma,
                        "p": 1.0,
                        "q": 1.0,
                        "beta": beta,
                        "gamma": 0.0,
                    }
                )
    for a in (0.25, 0.45, 0.65):
        for sigma in (0.10, 0.15):
            for gamma in (4.0, 8.0):
                candidates.append(
                    {
                        "candidate_id": (
                            f"C_a{int(round(a * 100)):03d}_s{int(round(sigma * 100)):03d}_"
                            f"g{int(round(gamma)):02d}_b{int(round(CANDIDATE_C_FIXED_BETA * 10)):02d}"
                        ),
                        "family": "C",
                        "mode": test_run.CONTINUOUS_FR_SHAPING_CANDIDATE_C,
                        "a": a,
                        "sigma": sigma,
                        "p": 0.0,
                        "q": 1.0,
                        "beta": CANDIDATE_C_FIXED_BETA,
                        "gamma": gamma,
                    }
                )
    return candidates


def load_seed_profiles() -> list[dict[str, Any]]:
    return [
        profile
        for profile in base_doe.build_seed_profiles()
        if str(profile["seed_profile_id"]) in SELECTED_SEED_PROFILE_IDS
    ]


def load_baseline_anchor_rows() -> list[dict[str, Any]]:
    if not BASELINE_ANCHOR_RUN_TABLE.exists():
        raise FileNotFoundError(f"Baseline anchor run table not found: {BASELINE_ANCHOR_RUN_TABLE}")
    rows = []
    with BASELINE_ANCHOR_RUN_TABLE.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if str(row.get("seed_profile_id", "")) not in SELECTED_SEED_PROFILE_IDS:
                continue
            if cell_id_from_row(row) not in ROUND1_CELL_IDS:
                continue
            rows.append(dict(row))
    expected_rows = len(ROUND1_CELLS) * len(SELECTED_SEED_PROFILE_IDS)
    if len(rows) != expected_rows:
        raise RuntimeError(
            f"Baseline anchor row count mismatch: expected {expected_rows}, found {len(rows)} in {BASELINE_ANCHOR_RUN_TABLE}"
        )
    return rows


def load_existing_run_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return [dict(row) for row in reader]


def append_run_rows(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    file_exists = path.exists()
    with path.open("a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists or path.stat().st_size == 0:
            writer.writeheader()
        writer.writerows(rows)


def build_candidate_settings(base_settings: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    settings = copy.deepcopy(base_settings)
    runtime = settings.setdefault("runtime", {})
    movement = runtime.setdefault("movement", {}).setdefault("v3a", {})
    movement["experiment"] = test_run.V3A_EXPERIMENT_PRECONTACT_CENTROID_PROBE
    movement["centroid_probe_scale"] = 0.5
    movement["odw_posture_bias_enabled"] = True
    movement["odw_posture_bias_k"] = 0.5
    movement["odw_posture_bias_clip_delta"] = 0.4
    shaping = movement.setdefault("continuous_fr_shaping", {})
    shaping["enabled"] = True
    shaping["mode"] = str(candidate["mode"])
    shaping["a"] = float(candidate["a"])
    shaping["sigma"] = float(candidate["sigma"])
    shaping["p"] = float(candidate["p"])
    shaping["q"] = float(candidate["q"])
    shaping["beta"] = float(candidate["beta"])
    shaping["gamma"] = float(candidate["gamma"])
    return settings


def summarize_cell_bucket(rows: list[dict[str, Any]]) -> dict[str, float]:
    return {
        "n_runs": float(len(rows)),
        "A_win_rate_pct": a_win_rate(rows),
        "wedge_present_rate_A_pct": true_rate(rows, "wedge_present_A"),
        "structural_fragility_rate_A_pct": true_rate(rows, "structural_fragility_A"),
        "mean_runtime_c_conn_A": mean_or_nan([row.get("runtime_c_conn_mean_A") for row in rows]),
        "mean_runtime_collapse_sig_A": mean_or_nan([row.get("runtime_collapse_sig_mean_A") for row in rows]),
        "mean_fire_eff_contact_to_cut_A": mean_or_nan([row.get("fire_eff_contact_to_cut_mean_A") for row in rows]),
        "mean_first_major_divergence_tick": mean_or_nan([row.get("first_major_divergence_tick") for row in rows]),
    }


def build_candidate_cell_summary(rows: list[dict[str, Any]]) -> dict[str, dict[str, dict[str, float]]]:
    buckets: dict[str, dict[str, list[dict[str, Any]]]] = {}
    for row in rows:
        candidate_id = str(row["candidate_id"])
        bucket = buckets.setdefault(candidate_id, {})
        bucket.setdefault(cell_id_from_row(row), []).append(row)
    out: dict[str, dict[str, dict[str, float]]] = {}
    for candidate_id, cell_buckets in buckets.items():
        out[candidate_id] = {
            cell_key: summarize_cell_bucket(cell_rows)
            for cell_key, cell_rows in cell_buckets.items()
        }
    return out


def build_baseline_cell_summary(rows: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    buckets: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        buckets.setdefault(cell_id_from_row(row), []).append(row)
    return {
        cell_key: summarize_cell_bucket(cell_rows)
        for cell_key, cell_rows in buckets.items()
    }


def mean_metric_delta(
    candidate_cell_summary: dict[str, dict[str, float]],
    baseline_cell_summary: dict[str, dict[str, float]],
    cells: list[str],
    metric: str,
) -> float:
    deltas = []
    for cell_key in cells:
        candidate_value = as_float(candidate_cell_summary.get(cell_key, {}).get(metric))
        baseline_value = as_float(baseline_cell_summary.get(cell_key, {}).get(metric))
        if math.isfinite(candidate_value) and math.isfinite(baseline_value):
            deltas.append(candidate_value - baseline_value)
    return mean_or_nan(deltas)


def mean_odw_fire_eff_gap(cell_summary: dict[str, dict[str, float]]) -> float:
    gaps = []
    for mb in (2, 5, 8):
        for pd in (2, 5, 8):
            low = cell_summary.get(cell_id(5, mb, pd, 2), {})
            high = cell_summary.get(cell_id(5, mb, pd, 8), {})
            low_value = as_float(low.get("mean_fire_eff_contact_to_cut_A"))
            high_value = as_float(high.get("mean_fire_eff_contact_to_cut_A"))
            if math.isfinite(low_value) and math.isfinite(high_value):
                gaps.append(high_value - low_value)
    return mean_or_nan(gaps)


def mean_pd_win_contrast(cell_summary: dict[str, dict[str, float]]) -> float:
    contrasts = []
    for mb in (2, 5, 8):
        for odw in (2, 8):
            low = cell_summary.get(cell_id(5, mb, 2, odw), {})
            high = cell_summary.get(cell_id(5, mb, 8, odw), {})
            low_value = as_float(low.get("A_win_rate_pct"))
            high_value = as_float(high.get("A_win_rate_pct"))
            if math.isfinite(low_value) and math.isfinite(high_value):
                contrasts.append(high_value - low_value)
    return mean_or_nan(contrasts)


def mean_pd5_mb_shoulder_contrast(cell_summary: dict[str, dict[str, float]]) -> float:
    contrasts = []
    for odw in (2, 8):
        low = cell_summary.get(cell_id(5, 2, 5, odw), {})
        high = cell_summary.get(cell_id(5, 8, 5, odw), {})
        low_value = as_float(low.get("A_win_rate_pct"))
        high_value = as_float(high.get("A_win_rate_pct"))
        if math.isfinite(low_value) and math.isfinite(high_value):
            contrasts.append(low_value - high_value)
    return mean_or_nan(contrasts)


def smoothness_score(candidate: dict[str, Any]) -> float:
    return (
        float(candidate["sigma"])
        - float(candidate["a"])
        - (0.02 * float(candidate["beta"]))
        - (0.01 * float(candidate["gamma"]))
    )


def candidate_failures(
    candidate_cell_summary: dict[str, dict[str, float]],
    baseline_cell_summary: dict[str, dict[str, float]],
) -> tuple[list[str], list[str]]:
    failed_controls = []
    failed_sentinels = []
    for fr, mb, pd, odw in ROUND1_CONTROL_CELLS:
        cell_key = cell_id(fr, mb, pd, odw)
        candidate_value = as_float(candidate_cell_summary[cell_key]["A_win_rate_pct"])
        baseline_value = as_float(baseline_cell_summary[cell_key]["A_win_rate_pct"])
        if candidate_value + 1e-9 < baseline_value:
            failed_controls.append(cell_key)
    for cell_key in sorted(PD8_SENTINEL_CELL_IDS):
        candidate_value = as_float(candidate_cell_summary[cell_key]["A_win_rate_pct"])
        baseline_value = as_float(baseline_cell_summary[cell_key]["A_win_rate_pct"])
        if candidate_value <= baseline_value + 1e-9:
            failed_sentinels.append(cell_key)
    return failed_controls, failed_sentinels


def build_candidate_summary_rows(
    run_rows: list[dict[str, Any]],
    candidates: list[dict[str, Any]],
    baseline_cell_summary: dict[str, dict[str, float]],
) -> list[dict[str, Any]]:
    candidate_by_id = {str(candidate["candidate_id"]): candidate for candidate in candidates}
    candidate_cell_summary = build_candidate_cell_summary(run_rows)
    summary_rows = []
    control_cell_ids = [cell_id(fr, mb, pd, odw) for fr, mb, pd, odw in ROUND1_CONTROL_CELLS]
    shoulder_cell_ids = sorted(PD5_MB8_SHOULDER_CELL_IDS)

    for candidate_id in sorted(candidate_cell_summary.keys()):
        candidate = candidate_by_id[candidate_id]
        cell_summary = candidate_cell_summary[candidate_id]
        failed_controls, failed_sentinels = candidate_failures(cell_summary, baseline_cell_summary)
        protected_delta = (
            as_float(cell_summary[PROTECTED_CELL_ID]["A_win_rate_pct"])
            - as_float(baseline_cell_summary[PROTECTED_CELL_ID]["A_win_rate_pct"])
        )
        controls_all_preserved = not failed_controls
        pd8_sentinels_improved = not failed_sentinels
        protected_cell_not_harmed = protected_delta >= -1e-9
        row = {
            "candidate_id": candidate_id,
            "candidate_family": candidate["family"],
            "candidate_mode": candidate["mode"],
            "a": float(candidate["a"]),
            "sigma": float(candidate["sigma"]),
            "p": float(candidate["p"]),
            "q": float(candidate["q"]),
            "beta": float(candidate["beta"]),
            "gamma": float(candidate["gamma"]),
            "ranking_advisory_only": True,
            "controls_all_preserved": controls_all_preserved,
            "pd8_sentinels_improved": pd8_sentinels_improved,
            "protected_cell_not_harmed": protected_cell_not_harmed,
            "hard_constraint_pass": controls_all_preserved and pd8_sentinels_improved and protected_cell_not_harmed,
            "failed_controls": ",".join(failed_controls),
            "failed_pd8_sentinels": ",".join(failed_sentinels),
            "mean_control_win_delta": mean_metric_delta(
                cell_summary, baseline_cell_summary, control_cell_ids, "A_win_rate_pct"
            ),
            "mean_pd8_sentinel_win_delta": mean_metric_delta(
                cell_summary, baseline_cell_summary, sorted(PD8_SENTINEL_CELL_IDS), "A_win_rate_pct"
            ),
            "protected_cell_win_delta": protected_delta,
            "odw_readability_delta": mean_odw_fire_eff_gap(cell_summary) - mean_odw_fire_eff_gap(baseline_cell_summary),
            "pd_selectivity_delta": mean_pd_win_contrast(cell_summary) - mean_pd_win_contrast(baseline_cell_summary),
            "pd5_mb_shoulder_contrast_delta": (
                mean_pd5_mb_shoulder_contrast(cell_summary) - mean_pd5_mb_shoulder_contrast(baseline_cell_summary)
            ),
            "mb8_pd5_win_delta": mean_metric_delta(
                cell_summary, baseline_cell_summary, shoulder_cell_ids, "A_win_rate_pct"
            ),
            "mean_runtime_c_conn_delta": mean_metric_delta(
                cell_summary, baseline_cell_summary, sorted(ROUND1_CELL_IDS), "mean_runtime_c_conn_A"
            ),
            "mean_runtime_collapse_delta": mean_metric_delta(
                cell_summary, baseline_cell_summary, sorted(ROUND1_CELL_IDS), "mean_runtime_collapse_sig_A"
            ),
            "smoothness_score": smoothness_score(candidate),
        }
        summary_rows.append(row)
    return summary_rows


def rank_candidate_rows(summary_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    def sort_key(row: dict[str, Any]):
        return (
            int(bool(row["controls_all_preserved"])),
            int(bool(row["pd8_sentinels_improved"])),
            int(bool(row["protected_cell_not_harmed"])),
            as_float(row["mean_pd8_sentinel_win_delta"], -1e9),
            as_float(row["mean_control_win_delta"], -1e9),
            as_float(row["odw_readability_delta"], -1e9),
            as_float(row["pd_selectivity_delta"], -1e9),
            as_float(row["pd5_mb_shoulder_contrast_delta"], -1e9),
            as_float(row["mb8_pd5_win_delta"], -1e9),
            as_float(row["smoothness_score"], -1e9),
        )

    ranked = []
    for idx, row in enumerate(sorted(summary_rows, key=sort_key, reverse=True), start=1):
        ranked_row = dict(row)
        ranked_row["rank"] = int(idx)
        ranked_row["ranking_advisory_only"] = True
        ranked.append(ranked_row)
    return ranked


def build_constraint_rows(summary_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for row in summary_rows:
        out.append(
            {
                "candidate_id": row["candidate_id"],
                "ranking_advisory_only": True,
                "controls_all_preserved": row["controls_all_preserved"],
                "pd8_sentinels_improved": row["pd8_sentinels_improved"],
                "protected_cell_not_harmed": row["protected_cell_not_harmed"],
                "hard_constraint_pass": row["hard_constraint_pass"],
                "failed_controls": row["failed_controls"],
                "failed_pd8_sentinels": row["failed_pd8_sentinels"],
                "protected_cell_win_delta": row["protected_cell_win_delta"],
            }
        )
    return out


def write_summary_markdown(
    path: Path,
    *,
    run_rows: list[dict[str, Any]],
    summary_rows: list[dict[str, Any]],
    ranked_rows: list[dict[str, Any]],
):
    total_candidate_runs = len(run_rows)
    hard_pass_count = sum(1 for row in summary_rows if bool(row["hard_constraint_pass"]))
    top_rows = ranked_rows[:10]
    lines = [
        f"# {TITLE}",
        "",
        "- Scope: first-round continuous shaping screen on the locked v3a centroid-restoration suspect path.",
        "- Frozen layer impact: none.",
        "- Baseline anchor: `fr_authority_doe_run_table.csv` filtered to the 22 round-1 cells and `SP01/SP09/SP18`.",
        "- Candidate count: `42`.",
        f"- Candidate runs written: `{total_candidate_runs}`.",
        f"- Hard-constraint passes: `{hard_pass_count}`.",
        "- Seeds: `SP01`, `SP09`, `SP18`.",
        "- Assumption: candidate C keeps `beta=1.5` fixed so the round-1 grid remains `42` candidates while preserving a smooth MB taper.",
        "- Ranking status: `advisory-only`; no automatic finalist decision is made by this script.",
        "",
        "## Output Files",
        f"- `{RUN_TABLE_PATH.name}`",
        f"- `{SUMMARY_CSV_PATH.name}`",
        f"- `{RANKED_CSV_PATH.name}`",
        f"- `{CONSTRAINT_CSV_PATH.name}`",
        f"- `{path.name}`",
        "",
        "## Resume Behavior",
        "",
        f"- `{RUN_TABLE_PATH.name}` also serves as the checkpoint file.",
        "- Re-running the script resumes from existing `run_id` rows and skips completed cases.",
        "- To force a fresh round-1 rerun, remove the existing round-1 output CSVs first.",
        "",
        "## Ranking Discipline",
        "1. preserve all controls",
        "2. improve the two FR5/PD8 sentinels",
        "3. avoid harming FR5_MB8_PD2_ODW8",
        "4. prefer stronger ODW readability and PD/MB separability",
        "5. break ties toward smoother and weaker candidates",
        "",
        "## Top Ranked Candidates",
        "",
        "| Rank | Candidate | Pass | Sentinel dWin | ODW dFireEff | PD Selectivity | MB Shoulder | Smoothness |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in top_rows:
        lines.append(
            "| "
            f"{int(row['rank'])} | {row['candidate_id']} | {row['hard_constraint_pass']} | "
            f"{as_float(row['mean_pd8_sentinel_win_delta']):.2f} | "
            f"{as_float(row['odw_readability_delta']):.4f} | "
            f"{as_float(row['pd_selectivity_delta']):.2f} | "
            f"{as_float(row['pd5_mb_shoulder_contrast_delta']):.2f} | "
            f"{as_float(row['smoothness_score']):.4f} |"
        )
    lines.extend(
        [
            "",
            "## Reproduction Command",
            "",
            "```powershell",
            "python analysis/engineering_reports/developments/20260311/phase_fr_authority_audit/run_continuous_fr_authority_round1_doe.py",
            "```",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main():
    base_settings = base_doe.load_json_file(SETTINGS_PATH)
    seed_profiles = load_seed_profiles()
    candidates = build_round1_candidates()
    baseline_rows = load_baseline_anchor_rows()
    baseline_cell_summary = build_baseline_cell_summary(baseline_rows)
    existing_rows = load_existing_run_rows(RUN_TABLE_PATH)
    run_rows = list(existing_rows)
    completed_run_ids = {str(row.get("run_id", "")) for row in existing_rows}
    pending_flush_rows = []
    total_runs = len(candidates) * len(seed_profiles) * len(ROUND1_CELLS)
    completed = len(completed_run_ids)

    if completed > 0:
        print(
            f"[continuous_fr_round1] resume checkpoint found: "
            f"{completed}/{total_runs} runs already present in {RUN_TABLE_PATH.name}"
        )

    for candidate in candidates:
        candidate_settings = build_candidate_settings(base_settings, candidate)
        for seed_profile in seed_profiles:
            for fr, mb, pd, odw in ROUND1_CELLS:
                base_run_id = f"{seed_profile['seed_profile_id']}_FR{fr}_MB{mb}_PD{pd}_ODW{odw}"
                run_id = f"{candidate['candidate_id']}__{base_run_id}"
                if run_id in completed_run_ids:
                    continue
                row, _alive_rows = base_doe.run_single_case(candidate_settings, seed_profile, fr, mb, pd, odw)
                row["run_id"] = run_id
                row["candidate_id"] = str(candidate["candidate_id"])
                row["candidate_family"] = str(candidate["family"])
                row["candidate_mode"] = str(candidate["mode"])
                row["candidate_a"] = float(candidate["a"])
                row["candidate_sigma"] = float(candidate["sigma"])
                row["candidate_p"] = float(candidate["p"])
                row["candidate_q"] = float(candidate["q"])
                row["candidate_beta"] = float(candidate["beta"])
                row["candidate_gamma"] = float(candidate["gamma"])
                row["baseline_anchor_source"] = BASELINE_ANCHOR_RUN_TABLE.name
                run_rows.append(row)
                pending_flush_rows.append(row)
                completed_run_ids.add(run_id)
                completed += 1
                if len(pending_flush_rows) >= CHECKPOINT_FLUSH_INTERVAL:
                    append_run_rows(RUN_TABLE_PATH, pending_flush_rows)
                    pending_flush_rows = []
                if completed % 25 == 0 or completed == total_runs:
                    print(
                        f"[continuous_fr_round1] completed={completed}/{total_runs} "
                        f"candidate={candidate['candidate_id']} seed={seed_profile['seed_profile_id']} "
                        f"FR={fr} MB={mb} PD={pd} ODW={odw}"
                    )

    if pending_flush_rows:
        append_run_rows(RUN_TABLE_PATH, pending_flush_rows)

    summary_rows = build_candidate_summary_rows(run_rows, candidates, baseline_cell_summary)
    ranked_rows = rank_candidate_rows(summary_rows)
    constraint_rows = build_constraint_rows(summary_rows)
    base_doe.write_csv(RUN_TABLE_PATH, run_rows)
    base_doe.write_csv(SUMMARY_CSV_PATH, sorted(summary_rows, key=lambda row: str(row["candidate_id"])))
    base_doe.write_csv(RANKED_CSV_PATH, ranked_rows)
    base_doe.write_csv(CONSTRAINT_CSV_PATH, constraint_rows)
    write_summary_markdown(SUMMARY_MD_PATH, run_rows=run_rows, summary_rows=summary_rows, ranked_rows=ranked_rows)

    print(f"[continuous_fr_round1] run_table={RUN_TABLE_PATH}")
    print(f"[continuous_fr_round1] ranked={RANKED_CSV_PATH}")
    print(f"[continuous_fr_round1] summary={SUMMARY_MD_PATH}")


if __name__ == "__main__":
    sys.exit(main())
