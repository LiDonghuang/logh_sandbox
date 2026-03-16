#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


BASE_SCRIPT_PATH = Path(__file__).resolve().parent / "run_continuous_fr_authority_round1_doe.py"


def load_module(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


base = load_module(BASE_SCRIPT_PATH, "continuous_fr_round1_multi_seed_base")

base.SELECTED_SEED_PROFILE_IDS = {"SP01"}
base.TITLE = "Continuous FR Authority Shaping Round 1 Single-Seed DOE"
base.RUN_TABLE_PATH = base.OUT_DIR / "continuous_fr_authority_round1_single_seed_run_table.csv"
base.SUMMARY_CSV_PATH = base.OUT_DIR / "continuous_fr_authority_round1_single_seed_candidate_summary.csv"
base.RANKED_CSV_PATH = base.OUT_DIR / "continuous_fr_authority_round1_single_seed_ranked_candidates.csv"
base.CONSTRAINT_CSV_PATH = base.OUT_DIR / "continuous_fr_authority_round1_single_seed_hard_constraints.csv"
base.SUMMARY_MD_PATH = base.OUT_DIR / "continuous_fr_authority_round1_single_seed_summary.md"


def build_round1_candidates():
    candidates = []
    a_values = (0.15, 0.25, 0.35, 0.45, 0.55, 0.65)
    sigma_values = (0.10, 0.15, 0.20)

    for a in a_values:
        for sigma in sigma_values:
            for q in (1.0, 2.0, 3.0):
                candidates.append(
                    {
                        "candidate_id": (
                            f"A_a{int(round(a * 100)):03d}_s{int(round(sigma * 100)):03d}_q{int(q)}"
                        ),
                        "family": "A",
                        "mode": base.test_run.CONTINUOUS_FR_SHAPING_CANDIDATE_A,
                        "a": a,
                        "sigma": sigma,
                        "p": 1.0,
                        "q": q,
                        "beta": 0.0,
                        "gamma": 0.0,
                    }
                )

    for a in a_values:
        for sigma in sigma_values:
            for beta_value in (1.5, 3.0):
                candidates.append(
                    {
                        "candidate_id": (
                            f"B_a{int(round(a * 100)):03d}_s{int(round(sigma * 100)):03d}_"
                            f"b{int(round(beta_value * 10)):02d}"
                        ),
                        "family": "B",
                        "mode": base.test_run.CONTINUOUS_FR_SHAPING_CANDIDATE_B,
                        "a": a,
                        "sigma": sigma,
                        "p": 1.0,
                        "q": 1.0,
                        "beta": beta_value,
                        "gamma": 0.0,
                    }
                )

    for a in a_values:
        for sigma in sigma_values:
            for gamma_value in (4.0, 8.0):
                candidates.append(
                    {
                        "candidate_id": (
                            f"C_a{int(round(a * 100)):03d}_s{int(round(sigma * 100)):03d}_"
                            f"g{int(round(gamma_value)):02d}_b{int(round(base.CANDIDATE_C_FIXED_BETA * 10)):02d}"
                        ),
                        "family": "C",
                        "mode": base.test_run.CONTINUOUS_FR_SHAPING_CANDIDATE_C,
                        "a": a,
                        "sigma": sigma,
                        "p": 0.0,
                        "q": 1.0,
                        "beta": base.CANDIDATE_C_FIXED_BETA,
                        "gamma": gamma_value,
                    }
                )
    return candidates


def write_summary_markdown(path: Path, *, run_rows, summary_rows, ranked_rows):
    total_candidate_runs = len(run_rows)
    hard_pass_count = sum(1 for row in summary_rows if bool(row["hard_constraint_pass"]))
    top_rows = ranked_rows[:10]
    seed_label = ", ".join(sorted(base.SELECTED_SEED_PROFILE_IDS))
    lines = [
        f"# {base.TITLE}",
        "",
        "- Scope: single-seed expanded continuous shaping screen on the locked v3a centroid-restoration suspect path.",
        "- Frozen layer impact: none.",
        "- Independence: this batch is isolated from the aborted multi-seed partial outputs.",
        "- Baseline anchor: `fr_authority_doe_run_table.csv` filtered to the round-1 cells and `SP01` only.",
        f"- Candidate count: `{len(build_round1_candidates())}`.",
        f"- Candidate runs written: `{total_candidate_runs}`.",
        f"- Hard-constraint passes: `{hard_pass_count}`.",
        f"- Seeds: `{seed_label}`.",
        "- Candidate C keeps `beta=1.5` fixed.",
        "- Ranking status: `advisory-only`; no automatic finalist decision is made by this script.",
        "",
        "## Output Files",
        f"- `{base.RUN_TABLE_PATH.name}`",
        f"- `{base.SUMMARY_CSV_PATH.name}`",
        f"- `{base.RANKED_CSV_PATH.name}`",
        f"- `{base.CONSTRAINT_CSV_PATH.name}`",
        f"- `{path.name}`",
        "",
        "## Resume Behavior",
        "",
        f"- `{base.RUN_TABLE_PATH.name}` also serves as the checkpoint file.",
        "- Re-running the script resumes from existing `run_id` rows in the single-seed family only.",
        "- The aborted multi-seed run table is not read by this script and does not participate in scoring.",
        "",
        "## Expanded Grid",
        "- Family A: `a x sigma x q = 6 x 3 x 3 = 54`",
        "- Family B: `a x sigma x beta = 6 x 3 x 2 = 36`",
        "- Family C: `a x sigma x gamma = 6 x 3 x 2 = 36`",
        "- Total: `126` candidates",
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
            f"{base.as_float(row['mean_pd8_sentinel_win_delta']):.2f} | "
            f"{base.as_float(row['odw_readability_delta']):.4f} | "
            f"{base.as_float(row['pd_selectivity_delta']):.2f} | "
            f"{base.as_float(row['pd5_mb_shoulder_contrast_delta']):.2f} | "
            f"{base.as_float(row['smoothness_score']):.4f} |"
        )
    lines.extend(
        [
            "",
            "## Reproduction Command",
            "",
            "```powershell",
            "python analysis/engineering_reports/developments/20260311/phase_fr_authority_audit/run_continuous_fr_authority_round1_single_seed_doe.py",
            "```",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


base.build_round1_candidates = build_round1_candidates
base.write_summary_markdown = write_summary_markdown


if __name__ == "__main__":
    sys.exit(base.main())
