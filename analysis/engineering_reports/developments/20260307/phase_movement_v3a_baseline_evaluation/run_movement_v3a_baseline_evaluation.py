import copy
import csv
import importlib.util
import json
import math
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
SRC = ROOT / "analysis" / "engineering_reports" / "developments" / "20260305" / "phase_viiid2_movement_precontact_explore" / "run_movement_precontact_explore.py"
spec = importlib.util.spec_from_file_location("movement_precontact_base", SRC)
base = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(base)

FR = [2, 5, 8]
MB = [2, 5, 8]
PD = [2, 5, 8]
MODELS = ["v1", "v3a"]
EXP = "exp_precontact_centroid_probe"
SCALE = 0.5
THETA_SPLIT = 1.7
THETA_ENV = 0.5
SEEDS = {
    "random_seed_effective": 1981813971,
    "background_map_seed_effective": 897304369,
    "metatype_random_seed_effective": 3095987153,
}


def write_csv(path, rows):
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def mean(vals):
    return base.mean_or_nan(vals)


def q(vals, p):
    return base.quantile_or_nan(vals, p)


def fin(vals):
    return base.finite(vals)


def delta(a, b, key):
    try:
        return float(a[key]) - float(b[key])
    except Exception:
        return float("nan")


def load_inputs():
    settings = base.load_json_file(ROOT / "analysis" / "test_run_v1_0.settings.json")
    archetypes = base.load_json_file(ROOT / "analysis" / "archetypes_v1_5.json")
    s = copy.deepcopy(settings)
    rt = s.setdefault("runtime", {})
    rt["boundary_enabled"] = False
    rt["boundary_soft_strength"] = 1.0
    rt["boundary_hard_enabled"] = False
    rt["bridge_theta_split"] = THETA_SPLIT
    rt["bridge_theta_env"] = THETA_ENV
    rt["movement_v3a_experiment"] = EXP
    rt["centroid_probe_scale"] = SCALE
    return settings, s, archetypes, list(archetypes.keys())[:6]


def run_case(settings_eval, archetypes, opp, opp_idx, fr, mb, pd, model):
    base.MOVEMENT_MODEL = model
    exp = EXP if model == "v3a" else "base"
    scale = SCALE if model == "v3a" else 1.0
    row = base.run_single_case(
        settings=settings_eval,
        archetypes=archetypes,
        opponent_name=opp,
        opponent_index=opp_idx,
        fr=float(fr),
        mb=float(mb),
        pd=float(pd),
        experiment=exp,
        probe_scale=scale,
        rep_index=1,
    )
    row["movement_model_effective"] = model
    row["movement_v3a_experiment_effective"] = exp if model == "v3a" else "N/A"
    row["centroid_probe_scale_effective"] = scale if model == "v3a" else "N/A"
    row["cut_exists"] = row["tactical_cut_tick_T"] is not None
    row["pocket_exists"] = row["tactical_pocket_tick_T"] is not None
    row["hit_runtime_cap"] = int(row["end_tick"]) >= 999 and int(row["remaining_units_A"]) > 0 and int(row["remaining_units_B"]) > 0
    row["boundary_enabled_effective"] = False
    row["boundary_soft_strength_effective"] = 1.0
    row["boundary_hard_enabled_effective"] = False
    row.update(SEEDS)
    return row


def build_delta_rows(run_rows):
    keyed, out = defaultdict(dict), []
    for row in run_rows:
        keyed[(row["cell_FR"], row["cell_MB"], row["cell_PD"], row["opponent_archetype_name"])][row["movement_model"]] = row
    for (fr, mb, pd, opp), bucket in sorted(keyed.items()):
        if "v1" not in bucket or "v3a" not in bucket:
            continue
        v1, v3a = bucket["v1"], bucket["v3a"]
        out.append({
            "cell_FR": fr, "cell_MB": mb, "cell_PD": pd, "opponent_archetype_name": opp,
            "delta_end_tick": delta(v3a, v1, "end_tick"),
            "delta_first_contact_tick": delta(v3a, v1, "first_contact_tick"),
            "delta_cut_tick": delta(v3a, v1, "tactical_cut_tick_T"),
            "delta_pocket_tick": delta(v3a, v1, "tactical_pocket_tick_T"),
            "delta_ar_p90_A": delta(v3a, v1, "precontact_ar_p90_A"),
            "delta_wedge_p10_A": delta(v3a, v1, "precontact_wedge_p10_A"),
            "delta_split_p90_A": delta(v3a, v1, "precontact_split_p90_A"),
            "delta_persistent_outlier_p90": delta(v3a, v1, "precontact_persistent_outlier_p90"),
            "delta_max_persistence": delta(v3a, v1, "precontact_max_persistence_max"),
            "delta_mirror_ar_gap": delta(v3a, v1, "precontact_ar_p90_gap_AB"),
            "delta_mirror_wedge_gap": delta(v3a, v1, "precontact_wedge_p10_gap_AB"),
            "delta_jitter_ar_A": delta(v3a, v1, "precontact_ar_jitter_A"),
            "delta_jitter_wedge_A": delta(v3a, v1, "precontact_wedge_jitter_A"),
            "cut_exists_v1": bool(v1["cut_exists"]), "cut_exists_v3a": bool(v3a["cut_exists"]),
            "pocket_exists_v1": bool(v1["pocket_exists"]), "pocket_exists_v3a": bool(v3a["pocket_exists"]),
        })
    return out


def agg(run_rows, keys):
    grouped, out = defaultdict(list), []
    for row in run_rows:
        grouped[tuple(row[k] for k in keys)].append(row)
    for key in sorted(grouped):
        bucket = grouped[key]
        item = {k: v for k, v in zip(keys, key)}
        item.update({
            "n_runs": len(bucket),
            "win_rate_A": mean([1 if r["winner"] == "A" else 0 for r in bucket]),
            "mean_survivors_A": mean([r["remaining_units_A"] for r in bucket]),
            "median_end_tick": q([r["end_tick"] for r in bucket], 0.5),
            "first_contact_tick_mean": mean([r["first_contact_tick"] for r in bucket]),
            "cut_exists_rate": mean([1 if r["cut_exists"] else 0 for r in bucket]),
            "pocket_exists_rate": mean([1 if r["pocket_exists"] else 0 for r in bucket]),
            "cut_tick_p50": q([r["tactical_cut_tick_T"] for r in bucket], 0.5),
            "pocket_tick_p50": q([r["tactical_pocket_tick_T"] for r in bucket], 0.5),
            "precontact_ar_p90_A_mean": mean([r["precontact_ar_p90_A"] for r in bucket]),
            "precontact_wedge_p10_A_mean": mean([r["precontact_wedge_p10_A"] for r in bucket]),
            "precontact_split_p90_A_mean": mean([r["precontact_split_p90_A"] for r in bucket]),
            "precontact_persistent_outlier_p90_mean": mean([r["precontact_persistent_outlier_p90"] for r in bucket]),
            "precontact_max_persistence_max_mean": mean([r["precontact_max_persistence_max"] for r in bucket]),
            "mirror_ar_gap_mean": mean([r["precontact_ar_p90_gap_AB"] for r in bucket]),
            "mirror_wedge_gap_mean": mean([r["precontact_wedge_p10_gap_AB"] for r in bucket]),
            "jitter_ar_A_mean": mean([r["precontact_ar_jitter_A"] for r in bucket]),
            "jitter_wedge_A_mean": mean([r["precontact_wedge_jitter_A"] for r in bucket]),
            "runtime_cap_hit_count": sum(1 for r in bucket if r["hit_runtime_cap"]),
        })
        out.append(item)
    return out


def delta_cell_summary(delta_rows):
    grouped, out = defaultdict(list), []
    for row in delta_rows:
        grouped[(row["cell_FR"], row["cell_MB"], row["cell_PD"])].append(row)
    for fr, mb, pd in sorted(grouped):
        bucket = grouped[(fr, mb, pd)]
        out.append({
            "cell_FR": fr, "cell_MB": mb, "cell_PD": pd, "n_pairs": len(bucket),
            "delta_persistent_outlier_p90_mean": mean([r["delta_persistent_outlier_p90"] for r in bucket]),
            "delta_max_persistence_mean": mean([r["delta_max_persistence"] for r in bucket]),
            "delta_wedge_p10_A_mean": mean([r["delta_wedge_p10_A"] for r in bucket]),
            "delta_ar_p90_A_mean": mean([r["delta_ar_p90_A"] for r in bucket]),
            "delta_split_p90_A_mean": mean([r["delta_split_p90_A"] for r in bucket]),
            "delta_first_contact_tick_mean": mean([r["delta_first_contact_tick"] for r in bucket]),
        })
    return out


def det_rows(settings_eval, archetypes, first_opp):
    out = []
    for model in MODELS:
        d1 = run_case(settings_eval, archetypes, first_opp, 1, 8, 8, 5, model)["determinism_digest"]
        d2 = run_case(settings_eval, archetypes, first_opp, 1, 8, 8, 5, model)["determinism_digest"]
        out.append({"movement_model": model, "rep1": d1, "rep2": d2, "pass": d1 == d2})
    return out


def report(path, settings_base, run_rows, delta_rows, cell_rows, delta_cells, factor_rows, opp_rows, det):
    ov = {m: agg([r for r in run_rows if r["movement_model"] == m], ["movement_model"])[0] for m in MODELS}
    d = {
        "outlier": mean([r["delta_persistent_outlier_p90"] for r in delta_rows]),
        "persist": mean([r["delta_max_persistence"] for r in delta_rows]),
        "wedge": mean([r["delta_wedge_p10_A"] for r in delta_rows]),
        "ar": mean([r["delta_ar_p90_A"] for r in delta_rows]),
        "split": mean([r["delta_split_p90_A"] for r in delta_rows]),
        "contact": mean([r["delta_first_contact_tick"] for r in delta_rows]),
        "cut": mean([r["delta_cut_tick"] for r in delta_rows]),
        "pocket": mean([r["delta_pocket_tick"] for r in delta_rows]),
        "mar": mean([r["delta_mirror_ar_gap"] for r in delta_rows]),
        "mwg": mean([r["delta_mirror_wedge_gap"] for r in delta_rows]),
        "jar": mean([r["delta_jitter_ar_A"] for r in delta_rows]),
        "jwg": mean([r["delta_jitter_wedge_A"] for r in delta_rows]),
    }
    flags = []
    for factor in ("FR", "MB", "PD"):
        v1 = [r["precontact_persistent_outlier_p90_mean"] for r in factor_rows if r["movement_model"] == "v1" and r["factor"] == factor]
        v3a = [r["precontact_persistent_outlier_p90_mean"] for r in factor_rows if r["movement_model"] == "v3a" and r["factor"] == factor]
        flags.append((factor, max(fin(v1)) - min(fin(v1)) > 1e-9, max(fin(v3a)) - min(fin(v3a)) > 1e-9))
    rec = "HOLD"
    if d["outlier"] < 0 and d["persist"] < 0 and ov["v3a"]["cut_exists_rate"] > 0 and ov["v3a"]["pocket_exists_rate"] > 0 and all(r["pass"] for r in det):
        rec = "RECOMMEND V3A FOR BASELINE REPLACEMENT GATE"
    lines = [
        "# Movement v3a Baseline Evaluation Report", "",
        "## Scope",
        "- Candidate: `movement_model=v3a`, `movement_v3a_experiment=exp_precontact_centroid_probe`, `centroid_probe_scale=0.5`, `bridge_theta_split=1.7`, `bridge_theta_env=0.5`",
        "- Grid: FR x MB x PD = 3 x 3 x 3, opponents = first six canonical archetypes, models = v1/v3a",
        "- Total runs: 324",
        "- Yang not used",
        "", "## Runtime Alignment",
        "- Source settings: `test_run/test_run_v1_0.settings.json`",
        f"- DOE overrides only: `boundary_enabled=false`, `boundary_soft_strength=1.0`, `boundary_hard_enabled=false`, `runtime_decision_source_effective=v2`",
        f"- Fixed paired seeds: random=`{SEEDS['random_seed_effective']}`, background=`{SEEDS['background_map_seed_effective']}`, metatype=`{SEEDS['metatype_random_seed_effective']}`",
        "", "## Standards Compliance",
        "- Standards version: `DOE_Report_Standard_v1.0 / BRF_Export_Standard_v1.0`",
        "- Script version: `movement_v3a_baseline_evaluation_v1`",
        "- Deviations: none",
        "", "## Determinism Check", "| model | rep1 | rep2 | pass |", "| --- | --- | --- | --- |",
    ]
    for r in det: lines.append(f"| {r['movement_model']} | `{r['rep1']}` | `{r['rep2']}` | {r['pass']} |")
    lines += [
        "", "## Overall Comparison", "| metric | v1 | v3a | delta |", "| --- | ---: | ---: | ---: |",
        f"| precontact_persistent_outlier_p90_mean | {ov['v1']['precontact_persistent_outlier_p90_mean']:.4f} | {ov['v3a']['precontact_persistent_outlier_p90_mean']:.4f} | {d['outlier']:.4f} |",
        f"| precontact_max_persistence_max_mean | {ov['v1']['precontact_max_persistence_max_mean']:.4f} | {ov['v3a']['precontact_max_persistence_max_mean']:.4f} | {d['persist']:.4f} |",
        f"| precontact_wedge_p10_A_mean | {ov['v1']['precontact_wedge_p10_A_mean']:.4f} | {ov['v3a']['precontact_wedge_p10_A_mean']:.4f} | {d['wedge']:.4f} |",
        f"| precontact_ar_p90_A_mean | {ov['v1']['precontact_ar_p90_A_mean']:.4f} | {ov['v3a']['precontact_ar_p90_A_mean']:.4f} | {d['ar']:.4f} |",
        f"| precontact_split_p90_A_mean | {ov['v1']['precontact_split_p90_A_mean']:.4f} | {ov['v3a']['precontact_split_p90_A_mean']:.4f} | {d['split']:.4f} |",
        f"| first_contact_tick_mean | {ov['v1']['first_contact_tick_mean']:.4f} | {ov['v3a']['first_contact_tick_mean']:.4f} | {d['contact']:.4f} |",
        f"| cut_exists_rate | {ov['v1']['cut_exists_rate']:.4f} | {ov['v3a']['cut_exists_rate']:.4f} | {ov['v3a']['cut_exists_rate']-ov['v1']['cut_exists_rate']:.4f} |",
        f"| pocket_exists_rate | {ov['v1']['pocket_exists_rate']:.4f} | {ov['v3a']['pocket_exists_rate']:.4f} | {ov['v3a']['pocket_exists_rate']-ov['v1']['pocket_exists_rate']:.4f} |",
        "", "## Cell-Level Main Effects", "| FR | MB | PD | d_outlier | d_persist | d_wedge | d_AR | d_split | d_contact |", "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for r in delta_cells: lines.append(f"| {r['cell_FR']} | {r['cell_MB']} | {r['cell_PD']} | {r['delta_persistent_outlier_p90_mean']:.4f} | {r['delta_max_persistence_mean']:.4f} | {r['delta_wedge_p10_A_mean']:.4f} | {r['delta_ar_p90_A_mean']:.4f} | {r['delta_split_p90_A_mean']:.4f} | {r['delta_first_contact_tick_mean']:.4f} |")
    lines += ["", "## Factor Main-Effect Check", "| factor | v1 variation | v3a variation |", "| --- | --- | --- |"]
    for factor, a, b in flags: lines.append(f"| {factor} | {a} | {b} |")
    lines += ["", "## Opponent Hardness", "| opponent | v1 win_rate_A | v3a win_rate_A | v1 median_end_tick | v3a median_end_tick |", "| --- | ---: | ---: | ---: | ---: |"]
    om = defaultdict(dict)
    for r in opp_rows: om[r["opponent_archetype_name"]][r["movement_model"]] = r
    for opp in sorted(om):
        a, b = om[opp].get("v1", {}), om[opp].get("v3a", {})
        lines.append(f"| {opp} | {float(a.get('win_rate_A', float('nan'))):.4f} | {float(b.get('win_rate_A', float('nan'))):.4f} | {float(a.get('median_end_tick', float('nan'))):.4f} | {float(b.get('median_end_tick', float('nan'))):.4f} |")
    lines += [
        "", "## Mirror / Jitter Watch", "| metric | v1 | v3a | delta |", "| --- | ---: | ---: | ---: |",
        f"| mirror_ar_gap_mean | {ov['v1']['mirror_ar_gap_mean']:.4f} | {ov['v3a']['mirror_ar_gap_mean']:.4f} | {d['mar']:.4f} |",
        f"| mirror_wedge_gap_mean | {ov['v1']['mirror_wedge_gap_mean']:.4f} | {ov['v3a']['mirror_wedge_gap_mean']:.4f} | {d['mwg']:.4f} |",
        f"| jitter_ar_A_mean | {ov['v1']['jitter_ar_A_mean']:.4f} | {ov['v3a']['jitter_ar_A_mean']:.4f} | {d['jar']:.4f} |",
        f"| jitter_wedge_A_mean | {ov['v1']['jitter_wedge_A_mean']:.4f} | {ov['v3a']['jitter_wedge_A_mean']:.4f} | {d['jwg']:.4f} |",
        "", "## Censoring / Cap Sensitivity",
        f"- Runtime cap hits: v1=`{ov['v1']['runtime_cap_hit_count']}`, v3a=`{ov['v3a']['runtime_cap_hit_count']}`",
        "- Effective runtime policy: `max_time_steps=-1`, terminate 10 ticks after elimination, hard cap 999",
        "", "## Recommendation", f"- {rec}",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main():
    _, settings_eval, archetypes, opponents = load_inputs()
    run_rows, total = [], len(FR) * len(MB) * len(PD) * len(opponents) * len(MODELS)
    idx = 0
    for fr in FR:
        for mb in MB:
            for pd in PD:
                for opp_idx, opp in enumerate(opponents, start=1):
                    for model in MODELS:
                        idx += 1
                        run_rows.append(run_case(settings_eval, archetypes, opp, opp_idx, fr, mb, pd, model))
                        if idx % 24 == 0 or idx == total:
                            print(f"[baseline_eval] runs {idx}/{total}")
    delta_rows = build_delta_rows(run_rows)
    cell_rows = agg(run_rows, ["movement_model", "cell_FR", "cell_MB", "cell_PD"])
    delta_cells = delta_cell_summary(delta_rows)
    factor_rows = agg(run_rows, ["movement_model", "cell_FR"]) + agg(run_rows, ["movement_model", "cell_MB"]) + agg(run_rows, ["movement_model", "cell_PD"])
    for r in factor_rows:
        if "cell_FR" in r: r["factor"], r["level"] = "FR", r.pop("cell_FR")
        elif "cell_MB" in r: r["factor"], r["level"] = "MB", r.pop("cell_MB")
        else: r["factor"], r["level"] = "PD", r.pop("cell_PD")
    opp_rows = agg(run_rows, ["movement_model", "opponent_archetype_name"])
    det = det_rows(settings_eval, archetypes, opponents[0])
    out = Path(__file__).resolve().parent
    write_csv(out / "movement_v3a_baseline_evaluation_run_table.csv", run_rows)
    write_csv(out / "movement_v3a_baseline_evaluation_delta_table.csv", delta_rows)
    write_csv(out / "movement_v3a_baseline_evaluation_cell_summary.csv", cell_rows)
    write_csv(out / "movement_v3a_baseline_evaluation_delta_cell_summary.csv", delta_cells)
    write_csv(out / "movement_v3a_baseline_evaluation_factor_summary.csv", factor_rows)
    write_csv(out / "movement_v3a_baseline_evaluation_opponent_summary.csv", opp_rows)
    report(out / "Movement_v3a_Baseline_Evaluation_Report.md", settings_eval, run_rows, delta_rows, cell_rows, delta_cells, factor_rows, opp_rows, det)
    det_lines = ["# Movement v3a Baseline Evaluation Determinism Check", "", "| model | rep1 | rep2 | pass |", "| --- | --- | --- | --- |"]
    for r in det: det_lines.append(f"| {r['movement_model']} | `{r['rep1']}` | `{r['rep2']}` | {r['pass']} |")
    (out / "movement_v3a_baseline_evaluation_determinism_check.md").write_text("\n".join(det_lines), encoding="utf-8")
    print("[done] movement v3a baseline evaluation complete")
    print(f"[out] {out}")


if __name__ == "__main__":
    main()
