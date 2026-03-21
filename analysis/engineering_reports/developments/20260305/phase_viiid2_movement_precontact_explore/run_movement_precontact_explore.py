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

from test_run.test_run_v1_0 import (  # noqa: E402
    SimulationBoundaryConfig,
    SimulationContactConfig,
    SimulationExecutionConfig,
    SimulationMovementConfig,
    SimulationObserverConfig,
    SimulationRuntimeConfig,
    TestModeEngineTickSkeleton,
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
MOVEMENT_MODEL = "v3a"
RUNTIME_DECISION_SOURCE = "v2"
PHASE2_PROBE_SCALES = [1.00, 0.80, 0.60, 0.40]
CV2_SCALES = [0.75, 0.70, 0.65]
PRECONTACT_FOCUS_END_TICK = 100
MILD_CONTACT_DRIFT_MAX = 5.0
MILD_CUT_DRIFT_P50_MAX = 40.0
MILD_POCKET_DRIFT_P50_MAX = 40.0

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


def mean_abs_diff(values):
    vals = finite(values)
    if len(vals) <= 1:
        return float("nan")
    diffs = []
    for idx in range(1, len(vals)):
        diffs.append(abs(vals[idx] - vals[idx - 1]))
    return mean_or_nan(diffs)


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


def precontact_focus_slice(series, first_contact_tick, focus_end_tick=PRECONTACT_FOCUS_END_TICK):
    vals = list(series) if series is not None else []
    if not vals:
        return []
    stop_idx = len(vals)
    if first_contact_tick is not None:
        stop_idx = min(stop_idx, max(0, int(first_contact_tick) - 1))
    stop_idx = min(stop_idx, max(0, int(focus_end_tick)))
    return vals[:stop_idx]


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]):
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def build_test_vector(fr: float, mb: float, pd: float) -> dict:
    return {
        "force_concentration_ratio": 5.0,
        "formation_rigidity": float(fr),
        "mobility_bias": float(mb),
        "offense_defense_weight": 5.0,
        "perception_radius": 5.0,
        "pursuit_drive": float(pd),
        "retreat_threshold": 5.0,
        "risk_appetite": 5.0,
        "targeting_logic": 5.0,
        "time_preference": 5.0,
    }


def build_opponent_vector(base: dict) -> dict:
    return {
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


def canonical_variant_id(experiment: str, probe_scale: float) -> str:
    if experiment == "base":
        return "base"
    return f"probe_{probe_scale:.2f}"


def run_single_case(
    settings: dict,
    archetypes: dict,
    opponent_name: str,
    opponent_index: int,
    fr: float,
    mb: float,
    pd: float,
    experiment: str,
    probe_scale: float,
    rep_index: int = 1,
):
    fleet_size = int(get_fleet_setting(settings, "initial_fleet_size", 100))
    aspect_ratio = float(get_fleet_setting(settings, "initial_fleet_aspect_ratio", 2.0))
    unit_spacing = float(get_battlefield_setting(settings, "min_unit_spacing", 2.0))
    unit_speed = float(get_unit_setting(settings, "unit_speed", 1.0))
    unit_hp = float(get_unit_setting(settings, "unit_max_hit_points", 100.0))
    arena_size = float(get_battlefield_setting(settings, "arena_size", 200.0))
    attack_range = float(get_unit_setting(settings, "attack_range", get_runtime_setting(settings, "attack_range", 5.0)))
    damage_per_tick = float(get_unit_setting(settings, "damage_per_tick", get_runtime_setting(settings, "damage_per_tick", 1.0)))
    fire_quality_alpha = float(get_runtime_setting(settings, "fire_quality_alpha", 0.1))
    contact_hysteresis_h = float(get_runtime_setting(settings, "contact_hysteresis_h", 0.1))
    fsr_strength = float(get_runtime_setting(settings, "fsr_strength", 0.1))
    boundary_enabled = bool(get_runtime_setting(settings, "boundary_enabled", False))
    boundary_hard_enabled = bool(get_runtime_setting(settings, "boundary_hard_enabled", True))
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

    test_vector = build_test_vector(fr=fr, mb=mb, pd=pd)
    opponent_vector = build_opponent_vector(archetypes[opponent_name])

    state = build_initial_state(
        fleet_a_params=to_personality_parameters(vector_to_archetype(f"test_FR{fr}_MB{mb}_PD{int(pd)}", test_vector)),
        fleet_b_params=to_personality_parameters(vector_to_archetype(opponent_name, opponent_vector)),
        fleet_size=fleet_size,
        aspect_ratio=aspect_ratio,
        unit_spacing=unit_spacing,
        unit_speed=unit_speed,
        unit_max_hit_points=unit_hp,
        arena_size=arena_size,
    )

    execution_cfg = SimulationExecutionConfig(
        steps=-1,
        capture_positions=False,
        frame_stride=1,
        include_target_lines=False,
        print_tick_summary=False,
        plot_diagnostics_enabled=False,
    )
    runtime_cfg = SimulationRuntimeConfig(
        decision_source=RUNTIME_DECISION_SOURCE,
        movement_model=MOVEMENT_MODEL,
        movement=SimulationMovementConfig(
            v3a_experiment=experiment,
            centroid_probe_scale=probe_scale,
        ),
        contact=SimulationContactConfig(
            attack_range=attack_range,
            damage_per_tick=damage_per_tick,
            separation_radius=unit_spacing,
            fire_quality_alpha=fire_quality_alpha,
            contact_hysteresis_h=contact_hysteresis_h,
            ch_enabled=ch_enabled,
            fsr_enabled=fsr_enabled,
            fsr_strength=fsr_strength,
        ),
        boundary=SimulationBoundaryConfig(
            enabled=boundary_enabled,
            hard_enabled=boundary_hard_enabled,
        ),
    )
    observer_cfg = SimulationObserverConfig(
        enabled=True,
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
        runtime_diag_enabled=True,
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
        engine_cls=TestModeEngineTickSkeleton,
        execution_cfg=execution_cfg,
        runtime_cfg=runtime_cfg,
        observer_cfg=observer_cfg,
    )

    first_contact_tick = first_positive_tick(combat_telemetry.get("in_contact_count", []))
    first_damage_tick = first_positive_tick(combat_telemetry.get("damage_events_count", []))
    first_kill_tick = first_kill_tick_from_alive(alive_trajectory.get("A", []), alive_trajectory.get("B", []))
    if first_kill_tick is None:
        first_kill_tick = first_damage_tick
    bridge_ticks = compute_bridge_event_ticks(bridge_telemetry)
    cut_tick_t = parse_tick(bridge_ticks.get("formation_cut_tick"))
    pocket_tick_t = parse_tick(bridge_ticks.get("pocket_formation_tick"))

    ar_a = list(bridge_telemetry.get("AR", {}).get("A", []))
    ar_b = list(bridge_telemetry.get("AR", {}).get("B", []))
    wedge_a = list(bridge_telemetry.get("wedge_ratio", {}).get("A", []))
    wedge_b = list(bridge_telemetry.get("wedge_ratio", {}).get("B", []))
    split_a = list(bridge_telemetry.get("split_separation", {}).get("A", []))
    split_b = list(bridge_telemetry.get("split_separation", {}).get("B", []))

    pre_ar_a = precontact_focus_slice(ar_a, first_contact_tick)
    pre_ar_b = precontact_focus_slice(ar_b, first_contact_tick)
    pre_wedge_a = precontact_focus_slice(wedge_a, first_contact_tick)
    pre_wedge_b = precontact_focus_slice(wedge_b, first_contact_tick)
    pre_split_a = precontact_focus_slice(split_a, first_contact_tick)
    pre_split_b = precontact_focus_slice(split_b, first_contact_tick)

    outlier_total = list(combat_telemetry.get("outlier_total", []))
    persistent_outlier_total = list(combat_telemetry.get("persistent_outlier_total", []))
    max_outlier_persistence = list(combat_telemetry.get("max_outlier_persistence", []))
    pre_persistent_total = precontact_focus_slice(persistent_outlier_total, first_contact_tick)
    pre_max_persistence = precontact_focus_slice(max_outlier_persistence, first_contact_tick)

    fleet_a_final = final_state.fleets.get("A")
    fleet_b_final = final_state.fleets.get("B")
    alive_a_final = len(fleet_a_final.unit_ids) if fleet_a_final else 0
    alive_b_final = len(fleet_b_final.unit_ids) if fleet_b_final else 0
    winner = "draw"
    if alive_a_final > alive_b_final:
        winner = "A"
    elif alive_b_final > alive_a_final:
        winner = "B"

    variant_id = canonical_variant_id(experiment=experiment, probe_scale=probe_scale)
    run_id = (
        f"FR{int(fr)}_MB{int(mb)}_PD{int(pd)}_vs_{opponent_name}_"
        f"{variant_id}_rep{rep_index:02d}"
    )
    cut_before_contact = False
    if cut_tick_t is not None and first_contact_tick is not None and cut_tick_t < first_contact_tick:
        cut_before_contact = True
    pocket_before_contact = False
    if pocket_tick_t is not None and first_contact_tick is not None and pocket_tick_t < first_contact_tick:
        pocket_before_contact = True

    return {
        "run_id": run_id,
        "movement_model": MOVEMENT_MODEL,
        "movement_v3a_experiment": experiment,
        "movement_v3a_variant_id": variant_id,
        "centroid_probe_scale": float(probe_scale),
        "runtime_decision_source_effective": RUNTIME_DECISION_SOURCE,
        "cell_FR": int(fr),
        "cell_MB": int(mb),
        "cell_PD": int(pd),
        "opponent_archetype_name": opponent_name,
        "opponent_archetype_index": int(opponent_index),
        "injected_test_vector": json.dumps(test_vector, sort_keys=True),
        "injected_opponent_vector": json.dumps(opponent_vector, sort_keys=True),
        "winner": winner,
        "end_tick": int(final_state.tick),
        "remaining_units_A": int(alive_a_final),
        "remaining_units_B": int(alive_b_final),
        "first_contact_tick": first_contact_tick,
        "first_kill_tick": first_kill_tick,
        "tactical_cut_tick_T": cut_tick_t,
        "tactical_pocket_tick_T": pocket_tick_t,
        "precontact_window_last_tick": len(pre_ar_a),
        "precontact_ar_p90_A": quantile_or_nan(pre_ar_a, 0.90),
        "precontact_ar_p90_B": quantile_or_nan(pre_ar_b, 0.90),
        "precontact_wedge_p10_A": quantile_or_nan(pre_wedge_a, 0.10),
        "precontact_wedge_p10_B": quantile_or_nan(pre_wedge_b, 0.10),
        "precontact_split_p90_A": quantile_or_nan(pre_split_a, 0.90),
        "precontact_split_p90_B": quantile_or_nan(pre_split_b, 0.90),
        "precontact_persistent_outlier_p90": quantile_or_nan(pre_persistent_total, 0.90),
        "precontact_max_persistence_max": max(finite(pre_max_persistence)) if finite(pre_max_persistence) else float("nan"),
        "precontact_ar_p90_gap_AB": abs(
            quantile_or_nan(pre_ar_a, 0.90) - quantile_or_nan(pre_ar_b, 0.90)
        ),
        "precontact_wedge_p10_gap_AB": abs(
            quantile_or_nan(pre_wedge_a, 0.10) - quantile_or_nan(pre_wedge_b, 0.10)
        ),
        "precontact_split_p90_gap_AB": abs(
            quantile_or_nan(pre_split_a, 0.90) - quantile_or_nan(pre_split_b, 0.90)
        ),
        "precontact_ar_jitter_A": mean_abs_diff(pre_ar_a),
        "precontact_ar_jitter_B": mean_abs_diff(pre_ar_b),
        "precontact_wedge_jitter_A": mean_abs_diff(pre_wedge_a),
        "precontact_wedge_jitter_B": mean_abs_diff(pre_wedge_b),
        "precontact_split_jitter_A": mean_abs_diff(pre_split_a),
        "precontact_split_jitter_B": mean_abs_diff(pre_split_b),
        "cut_before_contact": cut_before_contact,
        "pocket_before_contact": pocket_before_contact,
        "determinism_digest": state_digest(final_state),
        "rep_index": int(rep_index),
        "precontact_outlier_total_p90": quantile_or_nan(precontact_focus_slice(outlier_total, first_contact_tick), 0.90),
    }


def aggregate_by_mb(rows: list[dict]) -> list[dict]:
    grouped = defaultdict(list)
    for row in rows:
        grouped[(row["movement_v3a_variant_id"], row["cell_MB"])].append(row)
    out = []
    for (variant_id, mb), bucket in sorted(grouped.items()):
        n = len(bucket)
        out.append(
            {
                "movement_model": MOVEMENT_MODEL,
                "movement_v3a_variant_id": variant_id,
                "cell_MB": mb,
                "n_runs": n,
                "win_rate_A": sum(1 for r in bucket if r["winner"] == "A") / float(n),
                "precontact_ar_p90_A_mean": mean_or_nan([r["precontact_ar_p90_A"] for r in bucket]),
                "precontact_wedge_p10_A_mean": mean_or_nan([r["precontact_wedge_p10_A"] for r in bucket]),
                "precontact_split_p90_A_mean": mean_or_nan([r["precontact_split_p90_A"] for r in bucket]),
                "precontact_persistent_outlier_p90_mean": mean_or_nan([r["precontact_persistent_outlier_p90"] for r in bucket]),
                "precontact_max_persistence_max_mean": mean_or_nan([r["precontact_max_persistence_max"] for r in bucket]),
                "first_contact_tick_mean": mean_or_nan([r["first_contact_tick"] for r in bucket]),
                "tactical_cut_tick_T_mean": mean_or_nan([r["tactical_cut_tick_T"] for r in bucket]),
                "tactical_pocket_tick_T_mean": mean_or_nan([r["tactical_pocket_tick_T"] for r in bucket]),
                "precontact_ar_p90_gap_AB_mean": mean_or_nan([r["precontact_ar_p90_gap_AB"] for r in bucket]),
                "precontact_wedge_p10_gap_AB_mean": mean_or_nan([r["precontact_wedge_p10_gap_AB"] for r in bucket]),
                "precontact_ar_jitter_A_mean": mean_or_nan([r["precontact_ar_jitter_A"] for r in bucket]),
                "precontact_wedge_jitter_A_mean": mean_or_nan([r["precontact_wedge_jitter_A"] for r in bucket]),
                "precontact_split_jitter_A_mean": mean_or_nan([r["precontact_split_jitter_A"] for r in bucket]),
            }
        )
    return out


def build_phase2_delta_table(rows: list[dict]) -> list[dict]:
    keyed = defaultdict(dict)
    for row in rows:
        key = (
            row["cell_FR"],
            row["cell_MB"],
            row["cell_PD"],
            row["opponent_archetype_name"],
        )
        keyed[key][row["movement_v3a_variant_id"]] = row

    delta_rows = []
    for key, bucket in sorted(keyed.items()):
        base = bucket.get("base")
        if not base:
            continue
        for variant_id, row in sorted(bucket.items()):
            if variant_id == "base":
                continue

            def d(metric):
                try:
                    return float(row[metric]) - float(base[metric])
                except Exception:
                    return float("nan")

            delta_cut = d("tactical_cut_tick_T")
            delta_pocket = d("tactical_pocket_tick_T")
            delta_rows.append(
                {
                    "cell_FR": key[0],
                    "cell_MB": key[1],
                    "cell_PD": key[2],
                    "opponent_archetype_name": key[3],
                    "candidate_variant_id": variant_id,
                    "candidate_probe_scale": row["centroid_probe_scale"],
                    "delta_precontact_ar_p90_A": d("precontact_ar_p90_A"),
                    "delta_precontact_wedge_p10_A": d("precontact_wedge_p10_A"),
                    "delta_precontact_persistent_outlier_p90": d("precontact_persistent_outlier_p90"),
                    "delta_precontact_max_persistence_max": d("precontact_max_persistence_max"),
                    "delta_precontact_split_p90_A": d("precontact_split_p90_A"),
                    "delta_first_contact_tick": d("first_contact_tick"),
                    "delta_tactical_cut_tick_T": delta_cut,
                    "delta_tactical_pocket_tick_T": delta_pocket,
                    "abs_delta_first_contact_tick": abs(d("first_contact_tick")),
                    "abs_delta_tactical_cut_tick_T": abs(delta_cut) if math.isfinite(delta_cut) else float("nan"),
                    "abs_delta_tactical_pocket_tick_T": abs(delta_pocket) if math.isfinite(delta_pocket) else float("nan"),
                    "delta_precontact_ar_p90_gap_AB": d("precontact_ar_p90_gap_AB"),
                    "delta_precontact_wedge_p10_gap_AB": d("precontact_wedge_p10_gap_AB"),
                    "delta_precontact_ar_jitter_A": d("precontact_ar_jitter_A"),
                    "delta_precontact_wedge_jitter_A": d("precontact_wedge_jitter_A"),
                    "delta_precontact_split_jitter_A": d("precontact_split_jitter_A"),
                }
            )
    return delta_rows


def summarize_scale_trend(rows: list[dict], scale: float) -> dict:
    bucket = [r for r in rows if r["centroid_probe_scale"] == scale]
    if not bucket:
        return {}
    return {
        "scale": scale,
        "precontact_ar_p90_A_mean": mean_or_nan([r["precontact_ar_p90_A"] for r in bucket]),
        "precontact_wedge_p10_A_mean": mean_or_nan([r["precontact_wedge_p10_A"] for r in bucket]),
        "precontact_persistent_outlier_p90_mean": mean_or_nan([r["precontact_persistent_outlier_p90"] for r in bucket]),
        "precontact_max_persistence_max_mean": mean_or_nan([r["precontact_max_persistence_max"] for r in bucket]),
        "precontact_split_p90_A_mean": mean_or_nan([r["precontact_split_p90_A"] for r in bucket]),
        "first_contact_tick_mean": mean_or_nan([r["first_contact_tick"] for r in bucket]),
        "tactical_cut_tick_T_mean": mean_or_nan([r["tactical_cut_tick_T"] for r in bucket]),
        "tactical_pocket_tick_T_mean": mean_or_nan([r["tactical_pocket_tick_T"] for r in bucket]),
    }


def monotonic_flags(scale_summary: list[dict]) -> dict:
    def as_list(metric):
        ordered = sorted(scale_summary, key=lambda x: x["scale"], reverse=True)
        return [row[metric] for row in ordered]

    def nonincreasing(vals):
        ok = True
        for idx in range(1, len(vals)):
            if vals[idx] > vals[idx - 1]:
                ok = False
        return ok

    def nondecreasing(vals):
        ok = True
        for idx in range(1, len(vals)):
            if vals[idx] < vals[idx - 1]:
                ok = False
        return ok

    return {
        "ar_nonincreasing": nonincreasing(as_list("precontact_ar_p90_A_mean")),
        "wedge_nondecreasing": nondecreasing(as_list("precontact_wedge_p10_A_mean")),
        "persistent_nonincreasing": nonincreasing(as_list("precontact_persistent_outlier_p90_mean")),
        "max_persistence_nonincreasing": nonincreasing(as_list("precontact_max_persistence_max_mean")),
    }


def mild_timing_gate_for_scale(delta_rows: list[dict], scale: float) -> dict:
    bucket = [r for r in delta_rows if float(r["candidate_probe_scale"]) == float(scale)]
    if not bucket:
        return {
            "scale": scale,
            "mean_abs_delta_first_contact": float("nan"),
            "p50_abs_delta_cut": float("nan"),
            "p50_abs_delta_pocket": float("nan"),
            "pass": False,
        }
    mean_abs_delta_first_contact = mean_or_nan([r["abs_delta_first_contact_tick"] for r in bucket])
    p50_abs_delta_cut = quantile_or_nan([r["abs_delta_tactical_cut_tick_T"] for r in bucket], 0.50)
    p50_abs_delta_pocket = quantile_or_nan([r["abs_delta_tactical_pocket_tick_T"] for r in bucket], 0.50)
    gate_pass = (
        math.isfinite(mean_abs_delta_first_contact)
        and math.isfinite(p50_abs_delta_cut)
        and math.isfinite(p50_abs_delta_pocket)
        and mean_abs_delta_first_contact <= MILD_CONTACT_DRIFT_MAX
        and p50_abs_delta_cut <= MILD_CUT_DRIFT_P50_MAX
        and p50_abs_delta_pocket <= MILD_POCKET_DRIFT_P50_MAX
    )
    return {
        "scale": scale,
        "mean_abs_delta_first_contact": mean_abs_delta_first_contact,
        "p50_abs_delta_cut": p50_abs_delta_cut,
        "p50_abs_delta_pocket": p50_abs_delta_pocket,
        "pass": gate_pass,
    }


def geometry_score_from_delta(bucket: list[dict]) -> float:
    return (
        mean_or_nan([r["delta_precontact_ar_p90_A"] for r in bucket])
        - mean_or_nan([r["delta_precontact_wedge_p10_A"] for r in bucket])
        + mean_or_nan([r["delta_precontact_persistent_outlier_p90"] for r in bucket])
        + mean_or_nan([r["delta_precontact_max_persistence_max"] for r in bucket])
    )


def run_phase_block(
    settings: dict,
    archetypes: dict,
    opponents: list[str],
    phase_name: str,
    probe_scales: list[float],
    include_base: bool,
    repeats: int = 1,
):
    rows = []
    variants = []
    if include_base:
        variants.append(("base", 1.0))
    for scale in probe_scales:
        variants.append(("exp_precontact_centroid_probe", float(scale)))

    total_runs = len(FR_LEVELS) * len(MB_LEVELS) * len(opponents) * len(variants) * repeats
    run_idx = 0
    for fr in FR_LEVELS:
        for mb in MB_LEVELS:
            for opponent_index, opponent_name in enumerate(opponents, start=1):
                for experiment, scale in variants:
                    for rep in range(1, repeats + 1):
                        run_idx += 1
                        row = run_single_case(
                            settings=settings,
                            archetypes=archetypes,
                            opponent_name=opponent_name,
                            opponent_index=opponent_index,
                            fr=fr,
                            mb=mb,
                            pd=PD_FIXED,
                            experiment=experiment,
                            probe_scale=scale,
                            rep_index=rep,
                        )
                        row["phase_label"] = phase_name
                        rows.append(row)
                        if run_idx % 24 == 0 or run_idx == total_runs:
                            print(f"[{phase_name}] runs {run_idx}/{total_runs}")
    return rows


def main():
    out_dir = Path(__file__).resolve().parent
    out_dir.mkdir(parents=True, exist_ok=True)
    settings = load_json_file(PROJECT_ROOT / "analysis" / "test_run_v1_0.settings.json")
    archetypes = load_json_file(PROJECT_ROOT / "analysis" / "archetypes_v1_5.json")
    opponents = list(archetypes.keys())[:6]

    phase2_rows = run_phase_block(
        settings=settings,
        archetypes=archetypes,
        opponents=opponents,
        phase_name="phase2_causal_sweep",
        probe_scales=PHASE2_PROBE_SCALES,
        include_base=True,
        repeats=1,
    )

    phase2_run_table_path = out_dir / "movement_precontact_causal_sweep_run_table.csv"
    write_csv(phase2_run_table_path, phase2_rows, list(phase2_rows[0].keys()))

    phase2_delta_rows = build_phase2_delta_table(phase2_rows)
    phase2_delta_table_path = out_dir / "movement_precontact_causal_sweep_delta_table.csv"
    write_csv(phase2_delta_table_path, phase2_delta_rows, list(phase2_delta_rows[0].keys()))

    phase2_summary_rows = aggregate_by_mb(phase2_rows)
    phase2_summary_path = out_dir / "movement_precontact_causal_sweep_summary_by_mb.csv"
    write_csv(phase2_summary_path, phase2_summary_rows, list(phase2_summary_rows[0].keys()))

    det_rows = []
    first_opp = opponents[0]
    det_variants = [("base", 1.0)] + [("exp_precontact_centroid_probe", s) for s in PHASE2_PROBE_SCALES]
    for experiment, scale in det_variants:
        digests = []
        for rep in (1, 2):
            row = run_single_case(
                settings=settings,
                archetypes=archetypes,
                opponent_name=first_opp,
                opponent_index=1,
                fr=8.0,
                mb=8.0,
                pd=5.0,
                experiment=experiment,
                probe_scale=scale,
                rep_index=rep,
            )
            digests.append(row["determinism_digest"])
        det_rows.append(
            {
                "variant_id": canonical_variant_id(experiment=experiment, probe_scale=scale),
                "experiment": experiment,
                "scale": scale,
                "rep1": digests[0],
                "rep2": digests[1],
                "pass": digests[0] == digests[1],
            }
        )

    det_path = out_dir / "movement_precontact_causal_sweep_determinism_check.md"
    det_lines = [
        "# Movement Pre-contact Causal Sweep Determinism Check",
        "",
        "- Case: FR8_MB8_PD5 vs first opponent archetype",
        "- Runtime decision source fixed: `v2`",
        "- Movement model fixed: `v3a`",
        "",
        "| variant_id | experiment | scale | rep1 | rep2 | pass |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in det_rows:
        det_lines.append(
            f"| {row['variant_id']} | {row['experiment']} | {row['scale']:.2f} | `{row['rep1']}` | `{row['rep2']}` | {row['pass']} |"
        )
    det_path.write_text("\n".join(det_lines), encoding="utf-8")

    scale_summary = [
        summarize_scale_trend(
            [r for r in phase2_rows if r["movement_v3a_variant_id"] != "base"],
            scale=s,
        )
        for s in PHASE2_PROBE_SCALES
    ]
    scale_summary = [row for row in scale_summary if row]
    monotonic = monotonic_flags(scale_summary)
    timing_gate_rows = [mild_timing_gate_for_scale(phase2_delta_rows, scale=s) for s in PHASE2_PROBE_SCALES]

    precontact_reorder_counts = {}
    for scale in PHASE2_PROBE_SCALES:
        bucket = [
            r
            for r in phase2_rows
            if r["movement_v3a_variant_id"] == canonical_variant_id("exp_precontact_centroid_probe", scale)
        ]
        if not bucket:
            continue
        cut_precontact_count = sum(1 for r in bucket if r["cut_before_contact"])
        pocket_precontact_count = sum(1 for r in bucket if r["pocket_before_contact"])
        precontact_reorder_counts[scale] = (cut_precontact_count, pocket_precontact_count, len(bucket))

    geom_scores = {}
    for scale in PHASE2_PROBE_SCALES:
        bucket = [r for r in phase2_delta_rows if float(r["candidate_probe_scale"]) == float(scale)]
        geom_scores[scale] = geometry_score_from_delta(bucket) if bucket else float("nan")

    phase2_report_path = out_dir / "movement_precontact_causal_sweep_report.md"
    lines = [
        "# Movement Pre-Contact Geometry - Causal Validation Phase (A-line only)",
        "",
        "## Scope",
        "- Movement model: `v3a`",
        "- Runtime decision source: `v2` (frozen)",
        "- Variant set: `base` + `exp_precontact_centroid_probe` with scales 1.00 / 0.80 / 0.60 / 0.40",
        "- Grid: FR=8, MB in {2,5,8}, PD=5, opponents=first six archetypes",
        f"- Pre-contact window: `min(first_contact_tick-1, {PRECONTACT_FOCUS_END_TICK})`",
        "",
        "## Phase 2 Monotonic Trend Check (scale 1.00 -> 0.40)",
        f"- AR non-increasing: **{monotonic['ar_nonincreasing']}**",
        f"- WedgeRatio p10 non-decreasing: **{monotonic['wedge_nondecreasing']}**",
        f"- Persistent outlier p90 non-increasing: **{monotonic['persistent_nonincreasing']}**",
        f"- Max persistence non-increasing: **{monotonic['max_persistence_nonincreasing']}**",
        "",
        "| scale | mean AR p90 A | mean Wedge p10 A | mean persistent p90 | mean max persistence | geometry_score (lower better) |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in sorted(scale_summary, key=lambda x: x["scale"], reverse=True):
        score = geom_scores.get(row["scale"], float("nan"))
        lines.append(
            f"| {row['scale']:.2f} | {row['precontact_ar_p90_A_mean']:.4f} | {row['precontact_wedge_p10_A_mean']:.4f} | "
            f"{row['precontact_persistent_outlier_p90_mean']:.4f} | {row['precontact_max_persistence_max_mean']:.4f} | {score:.4f} |"
        )

    lines.extend(
        [
            "",
            "## Constraint Drift (Mild Timing Gate)",
            f"- Gate thresholds: `|delta first_contact| <= {MILD_CONTACT_DRIFT_MAX:.0f}`, "
            f"`p50|delta cut| <= {MILD_CUT_DRIFT_P50_MAX:.0f}`, `p50|delta pocket| <= {MILD_POCKET_DRIFT_P50_MAX:.0f}`",
            "",
            "| scale | mean |delta first_contact| | p50 |delta cut| | p50 |delta pocket| | pass |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    timing_gate_by_scale = {row["scale"]: row for row in timing_gate_rows}
    for scale in PHASE2_PROBE_SCALES:
        row = timing_gate_by_scale.get(scale)
        lines.append(
            f"| {scale:.2f} | {row['mean_abs_delta_first_contact']:.4f} | {row['p50_abs_delta_cut']:.4f} | "
            f"{row['p50_abs_delta_pocket']:.4f} | {row['pass']} |"
        )

    lines.extend(
        [
            "",
            "## Geometry Improvement + Event-Reorder Risk Watch",
            "| scale | cut_precontact_count | pocket_precontact_count | total_runs | risk_flag |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for scale in PHASE2_PROBE_SCALES:
        cut_pre, pocket_pre, n_total = precontact_reorder_counts.get(scale, (0, 0, 0))
        gate_pass = timing_gate_by_scale.get(scale, {}).get("pass", False)
        score = geom_scores.get(scale, float("nan"))
        risk_flag = "LOW"
        if math.isfinite(score) and score < 0.0 and not gate_pass:
            risk_flag = "GEOMETRY_IMPROVES_BUT_TIMING_DRIFT_RISK"
        if cut_pre > 0 or pocket_pre > 0:
            risk_flag = "STRUCTURAL_EVENT_REORDER_RISK"
        lines.append(f"| {scale:.2f} | {cut_pre} | {pocket_pre} | {n_total} | {risk_flag} |")

    lines.extend(
        [
            "",
            "## Artifacts",
            "- movement_precontact_causal_sweep_run_table.csv",
            "- movement_precontact_causal_sweep_delta_table.csv",
            "- movement_precontact_causal_sweep_summary_by_mb.csv",
            "- movement_precontact_causal_sweep_determinism_check.md",
            "- movement_precontact_causal_sweep_report.md",
            "",
            "## Standards Compliance",
            "- standards_version: `DOE_Report_Standard_v1.0`",
            "- script: `run_movement_precontact_explore.py`",
            "- deviations: `No deviations`",
        ]
    )
    phase2_report_path.write_text("\n".join(lines), encoding="utf-8")

    cv2_rows = run_phase_block(
        settings=settings,
        archetypes=archetypes,
        opponents=opponents,
        phase_name="phase3_cv2_local_dense",
        probe_scales=CV2_SCALES,
        include_base=False,
        repeats=1,
    )
    cv2_run_table_path = out_dir / "movement_precontact_cv2_run_table.csv"
    write_csv(cv2_run_table_path, cv2_rows, list(cv2_rows[0].keys()))

    baseline_lookup = {}
    for row in phase2_rows:
        if row["movement_v3a_variant_id"] != "base":
            continue
        key = (row["cell_FR"], row["cell_MB"], row["cell_PD"], row["opponent_archetype_name"])
        baseline_lookup[key] = row

    cv2_score_rows = []
    for scale in CV2_SCALES:
        bucket = [r for r in cv2_rows if float(r["centroid_probe_scale"]) == float(scale)]
        delta_bucket = []
        for row in bucket:
            key = (row["cell_FR"], row["cell_MB"], row["cell_PD"], row["opponent_archetype_name"])
            base = baseline_lookup.get(key)
            if not base:
                continue
            delta_bucket.append(
                {
                    "delta_precontact_ar_p90_A": float(row["precontact_ar_p90_A"]) - float(base["precontact_ar_p90_A"]),
                    "delta_precontact_wedge_p10_A": float(row["precontact_wedge_p10_A"]) - float(base["precontact_wedge_p10_A"]),
                    "delta_precontact_persistent_outlier_p90": float(row["precontact_persistent_outlier_p90"]) - float(base["precontact_persistent_outlier_p90"]),
                    "delta_precontact_max_persistence_max": float(row["precontact_max_persistence_max"]) - float(base["precontact_max_persistence_max"]),
                    "delta_first_contact_tick": float(row["first_contact_tick"]) - float(base["first_contact_tick"]),
                    "delta_tactical_cut_tick_T": float(row["tactical_cut_tick_T"]) - float(base["tactical_cut_tick_T"]),
                    "delta_tactical_pocket_tick_T": float(row["tactical_pocket_tick_T"]) - float(base["tactical_pocket_tick_T"]),
                }
            )
        cv2_score_rows.append(
            {
                "scale": scale,
                "n_runs": len(bucket),
                "geometry_score": geometry_score_from_delta(delta_bucket),
                "mean_delta_ar_p90_A": mean_or_nan([d["delta_precontact_ar_p90_A"] for d in delta_bucket]),
                "mean_delta_wedge_p10_A": mean_or_nan([d["delta_precontact_wedge_p10_A"] for d in delta_bucket]),
                "mean_delta_persistent_p90": mean_or_nan([d["delta_precontact_persistent_outlier_p90"] for d in delta_bucket]),
                "mean_delta_max_persistence": mean_or_nan([d["delta_precontact_max_persistence_max"] for d in delta_bucket]),
                "mean_abs_delta_first_contact": mean_or_nan([abs(d["delta_first_contact_tick"]) for d in delta_bucket]),
                "p50_abs_delta_cut": quantile_or_nan([abs(d["delta_tactical_cut_tick_T"]) for d in delta_bucket], 0.50),
                "p50_abs_delta_pocket": quantile_or_nan([abs(d["delta_tactical_pocket_tick_T"]) for d in delta_bucket], 0.50),
            }
        )
    cv2_score_rows_sorted = sorted(cv2_score_rows, key=lambda x: x["geometry_score"])
    cv2_score_path = out_dir / "movement_precontact_cv2_score_table.csv"
    write_csv(cv2_score_path, cv2_score_rows_sorted, list(cv2_score_rows_sorted[0].keys()))

    cv2_summary_path = out_dir / "movement_precontact_cv2_summary.md"
    cv2_lines = [
        "# Movement Pre-Contact Geometry - CV-2 Local Densification",
        "",
        "- Candidate scales: 0.75 / 0.70 / 0.65",
        "- Objective: geometry_score (lower is better)",
        "",
        "| scale | n_runs | geometry_score | mean delta AR | mean delta Wedge | mean delta persistent | mean delta max persistence | mean |delta first_contact| | p50|delta cut| | p50|delta pocket| |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in cv2_score_rows_sorted:
        cv2_lines.append(
            f"| {row['scale']:.2f} | {row['n_runs']} | {row['geometry_score']:.4f} | {row['mean_delta_ar_p90_A']:.4f} | "
            f"{row['mean_delta_wedge_p10_A']:.4f} | {row['mean_delta_persistent_p90']:.4f} | {row['mean_delta_max_persistence']:.4f} | "
            f"{row['mean_abs_delta_first_contact']:.4f} | {row['p50_abs_delta_cut']:.4f} | {row['p50_abs_delta_pocket']:.4f} |"
        )
    cv2_summary_path.write_text("\n".join(cv2_lines), encoding="utf-8")

    candidate_scales = [row["scale"] for row in cv2_score_rows_sorted[:2]]
    cv3_probe_scales = candidate_scales
    cv3_rows = run_phase_block(
        settings=settings,
        archetypes=archetypes,
        opponents=opponents,
        phase_name="phase3_cv3_stability_recheck",
        probe_scales=cv3_probe_scales,
        include_base=True,
        repeats=2,
    )
    cv3_run_table_path = out_dir / "movement_precontact_cv3_run_table.csv"
    write_csv(cv3_run_table_path, cv3_rows, list(cv3_rows[0].keys()))

    cv3_group = defaultdict(list)
    for row in cv3_rows:
        key = (
            row["movement_v3a_variant_id"],
            row["cell_FR"],
            row["cell_MB"],
            row["cell_PD"],
            row["opponent_archetype_name"],
        )
        cv3_group[key].append(row)

    det_pass = 0
    det_total = 0
    for _key, bucket in cv3_group.items():
        if len(bucket) < 2:
            continue
        det_total += 1
        digests = sorted([r["determinism_digest"] for r in bucket])
        if digests[0] == digests[-1]:
            det_pass += 1

    cv3_rep1_lookup = {}
    for row in cv3_rows:
        if row["rep_index"] != 1:
            continue
        key = (row["cell_FR"], row["cell_MB"], row["cell_PD"], row["opponent_archetype_name"], row["movement_v3a_variant_id"])
        cv3_rep1_lookup[key] = row

    cv3_drift_rows = []
    for scale in cv3_probe_scales:
        variant_id = canonical_variant_id("exp_precontact_centroid_probe", scale)
        deltas = []
        for fr in FR_LEVELS:
            for mb in MB_LEVELS:
                for opp in opponents:
                    cand = cv3_rep1_lookup.get((fr, mb, int(PD_FIXED), opp, variant_id))
                    base = cv3_rep1_lookup.get((fr, mb, int(PD_FIXED), opp, "base"))
                    if not cand or not base:
                        continue
                    deltas.append(
                        {
                            "delta_first_contact_tick": float(cand["first_contact_tick"]) - float(base["first_contact_tick"]),
                            "delta_cut_tick": float(cand["tactical_cut_tick_T"]) - float(base["tactical_cut_tick_T"]),
                            "delta_pocket_tick": float(cand["tactical_pocket_tick_T"]) - float(base["tactical_pocket_tick_T"]),
                            "delta_mirror_ar_gap": float(cand["precontact_ar_p90_gap_AB"]) - float(base["precontact_ar_p90_gap_AB"]),
                            "delta_mirror_wedge_gap": float(cand["precontact_wedge_p10_gap_AB"]) - float(base["precontact_wedge_p10_gap_AB"]),
                            "delta_jitter_ar_A": float(cand["precontact_ar_jitter_A"]) - float(base["precontact_ar_jitter_A"]),
                            "delta_jitter_wedge_A": float(cand["precontact_wedge_jitter_A"]) - float(base["precontact_wedge_jitter_A"]),
                            "delta_jitter_split_A": float(cand["precontact_split_jitter_A"]) - float(base["precontact_split_jitter_A"]),
                        }
                    )
        cv3_drift_rows.append(
            {
                "scale": scale,
                "n_pairs": len(deltas),
                "mean_abs_delta_first_contact": mean_or_nan([abs(d["delta_first_contact_tick"]) for d in deltas]),
                "p50_abs_delta_cut": quantile_or_nan([abs(d["delta_cut_tick"]) for d in deltas], 0.50),
                "p50_abs_delta_pocket": quantile_or_nan([abs(d["delta_pocket_tick"]) for d in deltas], 0.50),
                "mean_delta_mirror_ar_gap": mean_or_nan([d["delta_mirror_ar_gap"] for d in deltas]),
                "mean_delta_mirror_wedge_gap": mean_or_nan([d["delta_mirror_wedge_gap"] for d in deltas]),
                "mean_delta_jitter_ar_A": mean_or_nan([d["delta_jitter_ar_A"] for d in deltas]),
                "mean_delta_jitter_wedge_A": mean_or_nan([d["delta_jitter_wedge_A"] for d in deltas]),
                "mean_delta_jitter_split_A": mean_or_nan([d["delta_jitter_split_A"] for d in deltas]),
            }
        )
    cv3_drift_path = out_dir / "movement_precontact_cv3_watch_drift.csv"
    write_csv(cv3_drift_path, cv3_drift_rows, list(cv3_drift_rows[0].keys()))

    cv3_summary_path = out_dir / "movement_precontact_cv3_summary.md"
    cv3_lines = [
        "# Movement Pre-Contact Geometry - CV-3 Stability Recheck",
        "",
        f"- Candidate scales from CV-2: {', '.join(f'{s:.2f}' for s in cv3_probe_scales)}",
        "- Paired control: `base`",
        "- Repeats per variant/case: 2",
        "",
        f"- Determinism (digest equality within identical variant/case): {det_pass}/{det_total} PASS",
        "",
        "| scale | n_pairs | mean |delta first_contact| | p50|delta cut| | p50|delta pocket| | mean delta mirror_AR_gap | mean delta mirror_Wedge_gap | mean delta jitter_AR_A | mean delta jitter_Wedge_A | mean delta jitter_Split_A |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in cv3_drift_rows:
        cv3_lines.append(
            f"| {row['scale']:.2f} | {row['n_pairs']} | {row['mean_abs_delta_first_contact']:.4f} | "
            f"{row['p50_abs_delta_cut']:.4f} | {row['p50_abs_delta_pocket']:.4f} | {row['mean_delta_mirror_ar_gap']:.4f} | "
            f"{row['mean_delta_mirror_wedge_gap']:.4f} | {row['mean_delta_jitter_ar_A']:.4f} | "
            f"{row['mean_delta_jitter_wedge_A']:.4f} | {row['mean_delta_jitter_split_A']:.4f} |"
        )
    cv3_summary_path.write_text("\n".join(cv3_lines), encoding="utf-8")

    print("[done] A-line causal validation package generated")
    print(f"[out] {out_dir}")


if __name__ == "__main__":
    main()
