import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[5]
ANALYSIS_DIR = PROJECT_ROOT / "analysis"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(ANALYSIS_DIR) not in sys.path:
    sys.path.insert(0, str(ANALYSIS_DIR))

from test_run_v1_0 import (  # noqa: E402
    build_initial_state,
    compute_bridge_event_ticks,
    get_battlefield_setting,
    get_fleet_setting,
    get_runtime_setting,
    get_unit_setting,
    load_json_file,
    run_simulation,
    to_personality_parameters,
)

FR_LEVELS = [8]
MB_LEVELS = [2, 5, 8]
PD_FIXED = 5.0
MODELS = ["v3a", "v3b1"]
PARAM_KEYS = [
    "force_concentration_ratio",
    "formation_rigidity",
    "mobility_bias",
    "offense_defense_weight",
    "perception_radius",
    "pursuit_drive",
    "retreat_threshold",
    "risk_appetite",
    "targeting_logic",
    "time_preference",
]


def finite(values):
    out = []
    for v in values:
        if v is None:
            continue
        fv = float(v)
        if math.isfinite(fv):
            out.append(fv)
    return out


def mean_or_nan(values):
    vals = finite(values)
    if not vals:
        return float("nan")
    return sum(vals) / float(len(vals))


def quantile_or_nan(values, q):
    vals = sorted(finite(values))
    if not vals:
        return float("nan")
    if len(vals) == 1:
        return vals[0]
    q = max(0.0, min(1.0, float(q)))
    pos = (len(vals) - 1) * q
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return vals[lo]
    w = pos - lo
    return vals[lo] * (1.0 - w) + vals[hi] * w


def parse_tick(value):
    if value is None:
        return None
    try:
        iv = int(value)
    except (TypeError, ValueError):
        return None
    return iv if iv >= 1 else None


def vector_to_archetype(name, vector):
    out = {
        "name": str(name),
        "disp_name_EN": str(name),
        "disp_name_ZH": str(name),
        "full_name_EN": f"{name} Fleet",
        "full_name_ZH": str(name),
    }
    for key in PARAM_KEYS:
        out[key] = float(vector[key])
    return out


def state_digest(final_state) -> str:
    h = hashlib.sha256()
    h.update(f"tick={int(final_state.tick)}|arena={float(final_state.arena_size):.6f}".encode("utf-8"))
    for fleet_id in sorted(final_state.fleets.keys()):
        fleet = final_state.fleets[fleet_id]
        h.update(f"|fleet={fleet_id}|alive={len(fleet.unit_ids)}".encode("utf-8"))
    for unit_id in sorted(final_state.units.keys()):
        u = final_state.units[unit_id]
        h.update(
            (
                f"|{unit_id}|{u.fleet_id}|{u.hit_points:.6f}|{u.position.x:.6f}|{u.position.y:.6f}|"
                f"{u.velocity.x:.6f}|{u.velocity.y:.6f}|{u.orientation_vector.x:.6f}|{u.orientation_vector.y:.6f}"
            ).encode("utf-8")
        )
    return h.hexdigest()


def first_positive_tick(values):
    for idx, value in enumerate(values, start=1):
        try:
            if float(value) > 0.0:
                return idx
        except (TypeError, ValueError):
            continue
    return None


def first_kill_tick_from_alive(alive_a, alive_b):
    n = max(len(alive_a), len(alive_b))
    if n <= 0:
        return None
    base_a = int(alive_a[0]) if alive_a else 0
    base_b = int(alive_b[0]) if alive_b else 0
    for idx in range(n):
        a = int(alive_a[idx]) if idx < len(alive_a) else (int(alive_a[-1]) if alive_a else 0)
        b = int(alive_b[idx]) if idx < len(alive_b) else (int(alive_b[-1]) if alive_b else 0)
        if a < base_a or b < base_b:
            return idx + 1
    return None


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]):
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def main():
    out_dir = Path(__file__).resolve().parent
    out_dir.mkdir(parents=True, exist_ok=True)
    settings_path = PROJECT_ROOT / "analysis" / "test_run_v1_0.settings.json"
    archetypes_path = PROJECT_ROOT / "analysis" / "archetypes_v1_5.json"
    settings = load_json_file(settings_path)
    archetypes = load_json_file(archetypes_path)

    first_six_names = list(archetypes.keys())[:6]

    fleet_size = int(get_fleet_setting(settings, "initial_fleet_size", 100))
    aspect_ratio = float(get_fleet_setting(settings, "initial_fleet_aspect_ratio", 2.0))
    unit_spacing = float(get_battlefield_setting(settings, "min_unit_spacing", 2.0))
    unit_speed = float(get_unit_setting(settings, "unit_speed", 1.0))
    unit_hp = float(get_unit_setting(settings, "unit_max_hit_points", 100.0))
    arena_size = float(get_battlefield_setting(settings, "arena_size", 200.0))
    attack_range = float(get_unit_setting(settings, "attack_range", get_runtime_setting(settings, "attack_range", 5.0)))
    damage_per_tick = float(
        get_unit_setting(settings, "damage_per_tick", get_runtime_setting(settings, "damage_per_tick", 1.0))
    )
    fire_quality_alpha = float(get_runtime_setting(settings, "fire_quality_alpha", 0.1))
    contact_hysteresis_h = float(get_runtime_setting(settings, "contact_hysteresis_h", 0.1))
    fsr_strength = float(get_runtime_setting(settings, "fsr_strength", 0.1))
    boundary_enabled = bool(get_runtime_setting(settings, "boundary_enabled", False))
    bridge_theta_split = float(get_runtime_setting(settings, "bridge_theta_split", 1.715))
    bridge_theta_env = float(get_runtime_setting(settings, "bridge_theta_env", 0.583))
    bridge_sustain_ticks = max(1, int(get_runtime_setting(settings, "bridge_sustain_ticks", 20)))
    collapse_shadow_theta_conn_default = float(get_runtime_setting(settings, "collapse_shadow_theta_conn_default", 0.10))
    collapse_shadow_theta_coh_default = float(get_runtime_setting(settings, "collapse_shadow_theta_coh_default", 0.98))
    collapse_shadow_theta_force_default = float(get_runtime_setting(settings, "collapse_shadow_theta_force_default", 0.95))
    collapse_shadow_theta_attr_default = float(get_runtime_setting(settings, "collapse_shadow_theta_attr_default", 0.10))
    collapse_shadow_attrition_window = max(1, int(get_runtime_setting(settings, "collapse_shadow_attrition_window", 20)))
    collapse_shadow_sustain_ticks = max(1, int(get_runtime_setting(settings, "collapse_shadow_sustain_ticks", 10)))
    collapse_shadow_min_conditions = min(4, max(1, int(get_runtime_setting(settings, "collapse_shadow_min_conditions", 2))))
    ch_enabled = contact_hysteresis_h > 0.0
    fsr_enabled = fsr_strength > 0.0

    run_rows: list[dict] = []
    run_counter = 0
    run_total = len(FR_LEVELS) * len(MB_LEVELS) * len(first_six_names) * len(MODELS)

    for fr in FR_LEVELS:
        for mb in MB_LEVELS:
            test_vector = {
                "force_concentration_ratio": 5.0,
                "formation_rigidity": float(fr),
                "mobility_bias": float(mb),
                "offense_defense_weight": 5.0,
                "perception_radius": 5.0,
                "pursuit_drive": float(PD_FIXED),
                "retreat_threshold": 5.0,
                "risk_appetite": 5.0,
                "targeting_logic": 5.0,
                "time_preference": 5.0,
            }
            for opp_idx, opp_name in enumerate(first_six_names, start=1):
                base = archetypes[opp_name]
                opponent_vector = {
                    "force_concentration_ratio": 5.0,
                    "formation_rigidity": float(base["formation_rigidity"]),
                    "mobility_bias": float(base["mobility_bias"]),
                    "offense_defense_weight": 5.0,
                    "perception_radius": 5.0,
                    "pursuit_drive": float(base["pursuit_drive"]),
                    "retreat_threshold": 5.0,
                    "risk_appetite": 5.0,
                    "targeting_logic": 5.0,
                    "time_preference": 5.0,
                }

                # Preflight identity assertions.
                if float(test_vector["formation_rigidity"]) != float(fr):
                    raise RuntimeError("Preflight failed: cell_FR mismatch in injected test persona.")
                if float(test_vector["mobility_bias"]) != float(mb):
                    raise RuntimeError("Preflight failed: cell_MB mismatch in injected test persona.")
                if float(test_vector["force_concentration_ratio"]) != 5.0:
                    raise RuntimeError("Preflight failed: test FCR must remain fixed at 5.")

                for model in MODELS:
                    run_counter += 1
                    run_id = f"doe_3b1_FR{fr}_MB{mb}_PD5_vs_{opp_name}_{model}"
                    fleet_a_data = vector_to_archetype(f"test_FR{fr}_MB{mb}_PD5", test_vector)
                    fleet_b_data = vector_to_archetype(opp_name, opponent_vector)
                    state = build_initial_state(
                        fleet_a_params=to_personality_parameters(fleet_a_data),
                        fleet_b_params=to_personality_parameters(fleet_b_data),
                        fleet_size=fleet_size,
                        aspect_ratio=aspect_ratio,
                        unit_spacing=unit_spacing,
                        unit_speed=unit_speed,
                        unit_max_hit_points=unit_hp,
                        arena_size=arena_size,
                    )
                    (
                        final_state,
                        _trajectory,
                        alive_trajectory,
                        _fleet_size_trajectory,
                        _observer_telemetry,
                        combat_telemetry,
                        bridge_telemetry,
                        _collapse_shadow,
                        _position_frames,
                    ) = run_simulation(
                        initial_state=state,
                        steps=-1,
                        capture_positions=False,
                        observer_enabled=True,
                        runtime_decision_source="v2",
                        movement_model=model,
                        bridge_theta_split=bridge_theta_split,
                        bridge_theta_env=bridge_theta_env,
                        bridge_sustain_ticks=bridge_sustain_ticks,
                        collapse_shadow_theta_conn_default=collapse_shadow_theta_conn_default,
                        collapse_shadow_theta_coh_default=collapse_shadow_theta_coh_default,
                        collapse_shadow_theta_force_default=collapse_shadow_theta_force_default,
                        collapse_shadow_theta_attr_default=collapse_shadow_theta_attr_default,
                        collapse_shadow_attrition_window=collapse_shadow_attrition_window,
                        collapse_shadow_sustain_ticks=collapse_shadow_sustain_ticks,
                        collapse_shadow_min_conditions=collapse_shadow_min_conditions,
                        frame_stride=1,
                        attack_range=attack_range,
                        damage_per_tick=damage_per_tick,
                        separation_radius=unit_spacing,
                        fire_quality_alpha=fire_quality_alpha,
                        contact_hysteresis_h=contact_hysteresis_h,
                        ch_enabled=ch_enabled,
                        fsr_enabled=fsr_enabled,
                        fsr_strength=fsr_strength,
                        boundary_enabled=boundary_enabled,
                        include_target_lines=False,
                        print_tick_summary=False,
                    )

                    fleet_a_final = final_state.fleets.get("A")
                    fleet_b_final = final_state.fleets.get("B")
                    alive_a_final = len(fleet_a_final.unit_ids) if fleet_a_final else 0
                    alive_b_final = len(fleet_b_final.unit_ids) if fleet_b_final else 0
                    winner = "draw"
                    if alive_a_final > alive_b_final:
                        winner = "A"
                    elif alive_b_final > alive_a_final:
                        winner = "B"

                    first_contact_tick = first_positive_tick(combat_telemetry.get("in_contact_count", []))
                    first_damage_tick = first_positive_tick(combat_telemetry.get("damage_events_count", []))
                    first_kill_tick = first_kill_tick_from_alive(
                        alive_trajectory.get("A", []),
                        alive_trajectory.get("B", []),
                    )
                    if first_kill_tick is None:
                        first_kill_tick = first_damage_tick

                    bridge_ticks = compute_bridge_event_ticks(bridge_telemetry)
                    cut_tick_t = parse_tick(bridge_ticks.get("formation_cut_tick"))
                    pocket_tick_t = parse_tick(bridge_ticks.get("pocket_formation_tick"))
                    ar_series_a = bridge_telemetry.get("AR", {}).get("A", [])
                    wedge_series_a = bridge_telemetry.get("wedge_ratio", {}).get("A", [])
                    split_series_a = bridge_telemetry.get("split_separation", {}).get("A", [])
                    ar_p90_a = quantile_or_nan(ar_series_a, 0.90)
                    ar_p99_a = quantile_or_nan(ar_series_a, 0.99)
                    wedge_p50_a = quantile_or_nan(wedge_series_a, 0.50)
                    split_p90_a = quantile_or_nan(split_series_a, 0.90)

                    run_rows.append(
                        {
                            "run_id": run_id,
                            "cell_FR": fr,
                            "cell_MB": mb,
                            "cell_PD": int(PD_FIXED),
                            "movement_model": model,
                            "runtime_decision_source_effective": "v2",
                            "opponent_archetype_name": opp_name,
                            "opponent_archetype_index": opp_idx,
                            "injected_test_persona_vector": json.dumps(test_vector, ensure_ascii=False, sort_keys=True),
                            "injected_opponent_vector": json.dumps(opponent_vector, ensure_ascii=False, sort_keys=True),
                            "winner": winner,
                            "end_tick": int(final_state.tick),
                            "remaining_units_A": int(alive_a_final),
                            "remaining_units_B": int(alive_b_final),
                            "first_contact_tick": first_contact_tick,
                            "first_kill_tick": first_kill_tick,
                            "tactical_cut_tick_T": cut_tick_t,
                            "tactical_pocket_tick_T": pocket_tick_t,
                            "ar_p90_A": ar_p90_a,
                            "ar_p99_A": ar_p99_a,
                            "wedge_p50_A": wedge_p50_a,
                            "split_p90_A": split_p90_a,
                            "determinism_digest": state_digest(final_state),
                        }
                    )
                    if run_counter % 12 == 0:
                        print(f"[progress] runs {run_counter}/{run_total}")

    run_table_path = out_dir / "movement_3b1_targeted_run_table.csv"
    run_fields = list(run_rows[0].keys()) if run_rows else []
    write_csv(run_table_path, run_rows, run_fields)

    keyed = defaultdict(dict)
    for row in run_rows:
        key = (row["cell_FR"], row["cell_MB"], row["cell_PD"], row["opponent_archetype_name"])
        keyed[key][row["movement_model"]] = row
    delta_rows = []
    for key in sorted(keyed.keys()):
        fr, mb, pd, opp = key
        bucket = keyed[key]
        if not all(m in bucket for m in MODELS):
            continue
        r3a = bucket["v3a"]
        r3b1 = bucket["v3b1"]

        def d(a, b, k):
            va = a.get(k)
            vb = b.get(k)
            if va is None or vb is None:
                return ""
            try:
                return float(va) - float(vb)
            except (TypeError, ValueError):
                return ""

        delta_rows.append(
            {
                "cell_FR": fr,
                "cell_MB": mb,
                "cell_PD": pd,
                "opponent_archetype_name": opp,
                "delta_end_tick_v3b1_minus_v3a": d(r3b1, r3a, "end_tick"),
                "delta_win_A_v3b1_minus_v3a": (1 if r3b1["winner"] == "A" else 0) - (1 if r3a["winner"] == "A" else 0),
                "delta_ar_p90_A_v3b1_minus_v3a": d(r3b1, r3a, "ar_p90_A"),
                "delta_ar_p99_A_v3b1_minus_v3a": d(r3b1, r3a, "ar_p99_A"),
                "delta_wedge_p50_A_v3b1_minus_v3a": d(r3b1, r3a, "wedge_p50_A"),
                "delta_cut_tick_T_v3b1_minus_v3a": d(r3b1, r3a, "tactical_cut_tick_T"),
            }
        )
    delta_table_path = out_dir / "movement_3b1_targeted_delta_table.csv"
    delta_fields = list(delta_rows[0].keys()) if delta_rows else []
    write_csv(delta_table_path, delta_rows, delta_fields)

    grouped = defaultdict(list)
    for row in run_rows:
        grouped[(row["movement_model"], row["cell_FR"], row["cell_MB"], row["cell_PD"])].append(row)
    cell_rows = []
    for key in sorted(grouped.keys()):
        model, fr, mb, pd = key
        rows = grouped[key]
        n = len(rows)
        cell_rows.append(
            {
                "movement_model": model,
                "cell_FR": fr,
                "cell_MB": mb,
                "cell_PD": pd,
                "n_runs": n,
                "win_rate_A": sum(1 for r in rows if r["winner"] == "A") / float(n),
                "end_tick_mean": mean_or_nan([r["end_tick"] for r in rows]),
                "ar_p90_A_mean": mean_or_nan([r["ar_p90_A"] for r in rows]),
                "ar_p99_A_mean": mean_or_nan([r["ar_p99_A"] for r in rows]),
                "wedge_p50_A_mean": mean_or_nan([r["wedge_p50_A"] for r in rows]),
                "cut_tick_T_mean": mean_or_nan([r["tactical_cut_tick_T"] for r in rows]),
            }
        )
    cell_summary_path = out_dir / "movement_3b1_targeted_cell_summary.csv"
    cell_fields = list(cell_rows[0].keys()) if cell_rows else []
    write_csv(cell_summary_path, cell_rows, cell_fields)

    det_rows = []
    first_opp = first_six_names[0]
    test_vector_det = {
        "force_concentration_ratio": 5.0,
        "formation_rigidity": 8.0,
        "mobility_bias": 8.0,
        "offense_defense_weight": 5.0,
        "perception_radius": 5.0,
        "pursuit_drive": float(PD_FIXED),
        "retreat_threshold": 5.0,
        "risk_appetite": 5.0,
        "targeting_logic": 5.0,
        "time_preference": 5.0,
    }
    base_opp = archetypes[first_opp]
    opp_vec_det = {
        "force_concentration_ratio": 5.0,
        "formation_rigidity": float(base_opp["formation_rigidity"]),
        "mobility_bias": float(base_opp["mobility_bias"]),
        "offense_defense_weight": 5.0,
        "perception_radius": 5.0,
        "pursuit_drive": float(base_opp["pursuit_drive"]),
        "retreat_threshold": 5.0,
        "risk_appetite": 5.0,
        "targeting_logic": 5.0,
        "time_preference": 5.0,
    }
    for model in MODELS:
        digests = []
        for rep in (1, 2):
            state = build_initial_state(
                fleet_a_params=to_personality_parameters(vector_to_archetype("det_A", test_vector_det)),
                fleet_b_params=to_personality_parameters(vector_to_archetype(first_opp, opp_vec_det)),
                fleet_size=fleet_size,
                aspect_ratio=aspect_ratio,
                unit_spacing=unit_spacing,
                unit_speed=unit_speed,
                unit_max_hit_points=unit_hp,
                arena_size=arena_size,
            )
            final_state, *_rest = run_simulation(
                initial_state=state,
                steps=-1,
                capture_positions=False,
                observer_enabled=True,
                runtime_decision_source="v2",
                movement_model=model,
                bridge_theta_split=bridge_theta_split,
                bridge_theta_env=bridge_theta_env,
                bridge_sustain_ticks=bridge_sustain_ticks,
                collapse_shadow_theta_conn_default=collapse_shadow_theta_conn_default,
                collapse_shadow_theta_coh_default=collapse_shadow_theta_coh_default,
                collapse_shadow_theta_force_default=collapse_shadow_theta_force_default,
                collapse_shadow_theta_attr_default=collapse_shadow_theta_attr_default,
                collapse_shadow_attrition_window=collapse_shadow_attrition_window,
                collapse_shadow_sustain_ticks=collapse_shadow_sustain_ticks,
                collapse_shadow_min_conditions=collapse_shadow_min_conditions,
                frame_stride=1,
                attack_range=attack_range,
                damage_per_tick=damage_per_tick,
                separation_radius=unit_spacing,
                fire_quality_alpha=fire_quality_alpha,
                contact_hysteresis_h=contact_hysteresis_h,
                ch_enabled=ch_enabled,
                fsr_enabled=fsr_enabled,
                fsr_strength=fsr_strength,
                boundary_enabled=boundary_enabled,
                include_target_lines=False,
                print_tick_summary=False,
            )
            digests.append(state_digest(final_state))
        det_rows.append({"movement_model": model, "rep1": digests[0], "rep2": digests[1], "pass": digests[0] == digests[1]})

    det_path = out_dir / "movement_3b1_targeted_determinism_check.md"
    det_lines = [
        "# Movement 3B.1 Targeted DOE Determinism Check",
        "",
        "- Case: FR8_MB8_PD5 vs first opponent (normalized-vector setup)",
        "- Runtime decision source fixed: `v2`",
        "",
        "| model | rep1 | rep2 | pass |",
        "| --- | --- | --- | --- |",
    ]
    for row in det_rows:
        det_lines.append(f"| {row['movement_model']} | `{row['rep1']}` | `{row['rep2']}` | {row['pass']} |")
    det_path.write_text("\n".join(det_lines), encoding="utf-8")

    # Brief report with focused deltas.
    delta_ar90 = mean_or_nan([row["delta_ar_p90_A_v3b1_minus_v3a"] for row in delta_rows])
    delta_ar99 = mean_or_nan([row["delta_ar_p99_A_v3b1_minus_v3a"] for row in delta_rows])
    delta_end = mean_or_nan([row["delta_end_tick_v3b1_minus_v3a"] for row in delta_rows])
    delta_cut = mean_or_nan([row["delta_cut_tick_T_v3b1_minus_v3a"] for row in delta_rows])
    report_path = out_dir / "movement_3b1_targeted_summary.md"
    report_lines = [
        "# Movement 3B.1 Targeted DOE Summary",
        "",
        "## Scope",
        "- Grid: FR fixed 8, MB in {2,5,8}, PD=5, opponents=first six archetypes.",
        "- Models: v3a vs v3b1.",
        "- Total runs: 36 (3 cells x 6 opponents x 2 models).",
        "- Runtime decision source fixed: `v2` (movement-only isolation).",
        "",
        "## Primary Deltas (v3b1 - v3a)",
        f"- mean delta AR_p90_A: {delta_ar90:.4f}",
        f"- mean delta AR_p99_A: {delta_ar99:.4f}",
        f"- mean delta end_tick: {delta_end:.4f}",
        f"- mean delta cut_tick_T: {delta_cut:.4f}",
        "",
        "## Artifacts",
        "- movement_3b1_targeted_run_table.csv",
        "- movement_3b1_targeted_delta_table.csv",
        "- movement_3b1_targeted_cell_summary.csv",
        "- movement_3b1_targeted_determinism_check.md",
    ]
    report_path.write_text("\n".join(report_lines), encoding="utf-8")

    print("[done] movement 3B.1 targeted DOE complete")
    print(f"[out] {out_dir}")


if __name__ == "__main__":
    main()
