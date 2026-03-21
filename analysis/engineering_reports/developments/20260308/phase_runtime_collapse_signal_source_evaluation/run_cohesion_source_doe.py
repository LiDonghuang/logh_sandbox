
"""
Legacy collapse-signal source DOE helper.

Scope:
- runtime cohesion source comparison only
- controlled persona assumes non-factor personality parameters fixed at 5.0

Do not reuse this helper as a generic runner for new personality-mechanism reviews
such as ODW/TL. New mechanism lines must define their own bounded harness.
"""

import copy
import csv
import hashlib
import importlib.util
import json
import math
import random
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
ANALYSIS_SRC = ROOT / "test_run" / "test_run_v1_0.py"

spec = importlib.util.spec_from_file_location("test_run_module", ANALYSIS_SRC)
test_run = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(test_run)


OUT_DIR = Path(__file__).resolve().parent
BRF_DIR = OUT_DIR / "brf_samples"
PREFLIGHT_CELLS = [(2, 2, 2), (5, 5, 5), (8, 8, 8)]
FR_LEVELS = [2, 5, 8]
MB_LEVELS = [2, 5, 8]
PD_LEVELS = [2, 5, 8]
SOURCES = ["v2", "v3_test"]
PREFLIGHT_OPPONENT_COUNT = 2
MAIN_OPPONENT_COUNT = 6
EPS = 1e-6
BRF_SAMPLE_SEED = 2026030801
BRF_PAIR_COUNT = 6
SEED_PROFILES = [
    {
        "seed_profile_id": "SP01",
        "random_seed_effective": 1981813971,
        "background_map_seed_effective": 897304369,
        "metatype_random_seed_effective": 3095987153,
    },
    {
        "seed_profile_id": "SP02",
        "random_seed_effective": 104729,
        "background_map_seed_effective": 130363,
        "metatype_random_seed_effective": 181081,
    },
]


def finite(values):
    out = []
    for value in values:
        try:
            fv = float(value)
        except (TypeError, ValueError):
            continue
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
    if q <= 0:
        return vals[0]
    if q >= 1:
        return vals[-1]
    pos = (len(vals) - 1) * float(q)
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return vals[lo]
    frac = pos - lo
    return vals[lo] * (1.0 - frac) + vals[hi] * frac


def first_true_tick(flags):
    for idx, flag in enumerate(flags, start=1):
        if bool(flag):
            return idx
    return None


def first_positive_tick(values):
    for idx, value in enumerate(values, start=1):
        try:
            if float(value) > 0.0:
                return idx
        except (TypeError, ValueError):
            continue
    return None


def parse_tick(value):
    if value in (None, "", "N/A"):
        return None
    try:
        iv = int(value)
    except (TypeError, ValueError):
        return None
    return iv if iv >= 1 else None


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


def precontact_focus_slice(series, first_contact_tick, focus_end_tick=100):
    vals = list(series) if series is not None else []
    if not vals:
        return []
    stop_idx = len(vals)
    if first_contact_tick is not None:
        stop_idx = min(stop_idx, max(0, int(first_contact_tick) - 1))
    stop_idx = min(stop_idx, max(0, int(focus_end_tick)))
    return vals[:stop_idx]


def write_csv(path: Path, rows: list[dict]):
    if not rows:
        return
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def vector_to_archetype(name: str, vector: dict) -> dict:
    out = {
        "name": str(name),
        "disp_name_EN": str(name),
        "disp_name_ZH": str(name),
        "full_name_EN": f"{name} Fleet",
        "full_name_ZH": str(name),
    }
    for key in test_run.PERSONALITY_PARAM_KEYS:
        out[key] = float(vector[key])
    return out


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


def state_digest(final_state) -> str:
    h = hashlib.sha256()
    h.update(f"tick={int(final_state.tick)}|arena={float(final_state.arena_size):.6f}".encode("utf-8"))
    for fleet_id in sorted(final_state.fleets.keys()):
        fleet = final_state.fleets[fleet_id]
        h.update(f"|fleet={fleet_id}|alive={len(fleet.unit_ids)}".encode("utf-8"))
        cohesion_value = float(final_state.last_fleet_cohesion.get(fleet_id, 0.0))
        h.update(f"|cohesion={cohesion_value:.8f}".encode("utf-8"))
        for unit_id in sorted(fleet.unit_ids):
            unit = final_state.units[unit_id]
            h.update(
                (
                    f"|u={unit_id}|x={float(unit.position.x):.6f}|y={float(unit.position.y):.6f}"
                    f"|vx={float(unit.velocity.x):.6f}|vy={float(unit.velocity.y):.6f}"
                    f"|hp={float(unit.hit_points):.6f}"
                ).encode("utf-8")
            )
    return h.hexdigest()


def select_canonical_opponents(archetypes: dict, count: int) -> list[str]:
    selected = []
    for archetype_id, data in archetypes.items():
        normalized = str(archetype_id).strip().lower()
        if normalized in {"default", "yang"}:
            continue
        if not isinstance(data, dict):
            continue
        try:
            for key in test_run.PERSONALITY_PARAM_KEYS:
                test_run._personality_value_from_data(data, key)
        except KeyError:
            continue
        selected.append(str(archetype_id))
        if len(selected) >= count:
            break
    if len(selected) < count:
        raise ValueError(f"Need {count} canonical opponents, found {len(selected)}")
    return selected


def apply_seed_profile(settings: dict, seed_profile: dict) -> dict:
    run_control = settings.setdefault("run_control", {})
    battlefield = settings.setdefault("battlefield", {})
    visualization = settings.setdefault("visualization", {})
    export_video = visualization.setdefault("export_video", {})
    run_control["random_seed"] = int(seed_profile["random_seed_effective"])
    run_control["metatype_random_seed"] = int(seed_profile["metatype_random_seed_effective"])
    battlefield["background_map_seed"] = int(seed_profile["background_map_seed_effective"])
    run_control["animate"] = False
    run_control["test_mode"] = 2
    export_video["enabled"] = False
    return settings


def apply_doe_overrides(settings: dict, source: str) -> dict:
    runtime = settings.setdefault("runtime", {})
    selectors = runtime.setdefault("selectors", {})
    boundary = runtime.setdefault("boundary", {})
    selectors["movement_model"] = "baseline"
    selectors["cohesion_decision_source"] = str(source)
    boundary["enabled"] = False
    boundary["soft_strength"] = 1.0
    boundary["hard_enabled"] = False
    return settings


def compute_runtime_signal_metrics(trajectory: dict, pd_a: float, pd_b: float) -> tuple[dict, dict]:
    cohesion_a = [float(v) for v in trajectory.get("A", [])]
    cohesion_b = [float(v) for v in trajectory.get("B", [])]
    n_ticks = max(len(cohesion_a), len(cohesion_b))
    pd_norm_a = (float(pd_a) - 1.0) / 9.0
    pd_norm_b = (float(pd_b) - 1.0) / 9.0
    threshold_a = 1.0 - pd_norm_a
    threshold_b = 1.0 - pd_norm_b
    series = {
        "enemy_collapse_signal": {"A": [], "B": []},
        "deep_pursuit": {"A": [], "B": []},
        "pursuit_intensity": {"A": [], "B": []},
    }
    for idx in range(n_ticks):
        coh_a = cohesion_a[idx] if idx < len(cohesion_a) else float("nan")
        coh_b = cohesion_b[idx] if idx < len(cohesion_b) else float("nan")
        signal_a = 1.0 - coh_b if math.isfinite(coh_b) else float("nan")
        signal_b = 1.0 - coh_a if math.isfinite(coh_a) else float("nan")
        for side, signal, threshold in (
            ("A", signal_a, threshold_a),
            ("B", signal_b, threshold_b),
        ):
            if not math.isfinite(signal):
                series["enemy_collapse_signal"][side].append(float("nan"))
                series["deep_pursuit"][side].append(False)
                series["pursuit_intensity"][side].append(float("nan"))
                continue
            deep = bool(signal > threshold)
            if deep:
                span = 1.0 - threshold
                if span <= 1e-12:
                    intensity = 1.0
                else:
                    intensity = (signal - threshold) / span
                intensity = min(1.0, max(0.0, intensity))
            else:
                intensity = 0.0
            series["enemy_collapse_signal"][side].append(signal)
            series["deep_pursuit"][side].append(deep)
            series["pursuit_intensity"][side].append(intensity)

    metrics = {}
    for side in ("A", "B"):
        deep_flags = list(series["deep_pursuit"][side])
        signal_vals = list(series["enemy_collapse_signal"][side])
        intensity_vals = list(series["pursuit_intensity"][side])
        metrics[side] = {
            "first_deep_pursuit_tick": first_true_tick(deep_flags),
            "pct_ticks_deep_pursuit": (100.0 * sum(1 for flag in deep_flags if flag) / float(len(deep_flags))) if deep_flags else float("nan"),
            "mean_pursuit_intensity": mean_or_nan(intensity_vals),
            "mean_enemy_collapse_signal": mean_or_nan(signal_vals),
            "p95_enemy_collapse_signal": quantile_or_nan(signal_vals, 0.95),
        }
    return metrics, series


def compute_event_flags(first_contact_tick, first_kill_tick, cut_tick, pocket_tick) -> dict:
    missing_cut = cut_tick is None
    pocket_without_cut = pocket_tick is not None and cut_tick is None
    event_order_anomaly = False
    if first_contact_tick is not None and first_kill_tick is not None and first_kill_tick < first_contact_tick:
        event_order_anomaly = True
    if first_kill_tick is not None and cut_tick is not None and cut_tick < first_kill_tick:
        event_order_anomaly = True
    if first_contact_tick is not None and cut_tick is not None and cut_tick < first_contact_tick:
        event_order_anomaly = True
    if cut_tick is not None and pocket_tick is not None and pocket_tick < cut_tick:
        event_order_anomaly = True
    return {
        "missing_cut": missing_cut,
        "pocket_without_cut": pocket_without_cut,
        "event_order_anomaly": event_order_anomaly,
    }


def compute_source_gap_metrics(v2_series: list, v3_series: list) -> dict:
    pairs = []
    for idx in range(max(len(v2_series), len(v3_series))):
        v2 = float(v2_series[idx]) if idx < len(v2_series) else float("nan")
        v3 = float(v3_series[idx]) if idx < len(v3_series) else float("nan")
        if math.isfinite(v2) and math.isfinite(v3):
            pairs.append(abs(v2 - v3))
    return {
        "mean_abs_gap": mean_or_nan(pairs),
        "max_abs_gap": max(pairs) if pairs else float("nan"),
        "differs": any(val > EPS for val in pairs),
    }


def run_single_case(
    settings: dict,
    archetypes: dict,
    opponent_name: str,
    opponent_index: int,
    fr: float,
    mb: float,
    pd: float,
    source: str,
    seed_profile: dict,
) -> tuple[dict, dict]:
    fleet_size = int(test_run.get_fleet_setting(settings, "initial_fleet_size", 100))
    aspect_ratio = float(test_run.get_fleet_setting(settings, "initial_fleet_aspect_ratio", 2.0))
    unit_spacing = float(test_run.get_battlefield_setting(settings, "min_unit_spacing", 2.0))
    unit_speed = float(test_run.get_unit_setting(settings, "unit_speed", 1.0))
    unit_hp = float(test_run.get_unit_setting(settings, "unit_max_hit_points", 100.0))
    arena_size = float(test_run.get_battlefield_setting(settings, "arena_size", 200.0))
    attack_range = float(test_run.get_unit_setting(settings, "attack_range", test_run.get_runtime_setting(settings, "attack_range", 5.0)))
    damage_per_tick = float(test_run.get_unit_setting(settings, "damage_per_tick", test_run.get_runtime_setting(settings, "damage_per_tick", 1.0)))
    fire_quality_alpha = float(test_run.get_runtime_setting(settings, "fire_quality_alpha", 0.1))
    contact_hysteresis_h = float(test_run.get_runtime_setting(settings, "contact_hysteresis_h", 0.1))
    fsr_strength = float(test_run.get_runtime_setting(settings, "fsr_strength", 0.1))
    boundary_enabled = bool(test_run.get_runtime_setting(settings, "boundary_enabled", False))
    boundary_hard_enabled = bool(test_run.get_runtime_setting(settings, "boundary_hard_enabled", False))
    boundary_soft_strength = float(test_run.get_runtime_setting(settings, "boundary_soft_strength", 1.0))
    bridge_theta_split = float(test_run.get_runtime_setting(settings, "bridge_theta_split", 1.7))
    bridge_theta_env = float(test_run.get_runtime_setting(settings, "bridge_theta_env", 0.5))
    bridge_sustain_ticks = max(1, int(test_run.get_runtime_setting(settings, "bridge_sustain_ticks", 20)))
    collapse_shadow_theta_conn_default = float(test_run.get_runtime_setting(settings, "collapse_shadow_theta_conn_default", 0.10))
    collapse_shadow_theta_coh_default = float(test_run.get_runtime_setting(settings, "collapse_shadow_theta_coh_default", 0.98))
    collapse_shadow_theta_force_default = float(test_run.get_runtime_setting(settings, "collapse_shadow_theta_force_default", 0.95))
    collapse_shadow_theta_attr_default = float(test_run.get_runtime_setting(settings, "collapse_shadow_theta_attr_default", 0.10))
    collapse_shadow_attrition_window = max(1, int(test_run.get_runtime_setting(settings, "collapse_shadow_attrition_window", 20)))
    collapse_shadow_sustain_ticks = max(1, int(test_run.get_runtime_setting(settings, "collapse_shadow_sustain_ticks", 10)))
    collapse_shadow_min_conditions = min(4, max(1, int(test_run.get_runtime_setting(settings, "collapse_shadow_min_conditions", 2))))
    ch_enabled = contact_hysteresis_h > 0.0
    fsr_enabled = fsr_strength > 0.0

    movement_model_requested, movement_model_effective = test_run.resolve_movement_model(
        test_run.get_runtime_setting(settings, "movement_model", "baseline")
    )
    movement_v3a_experiment_effective = str(test_run.get_runtime_setting(settings, "movement_v3a_experiment", "base")).strip().lower() or "base"
    centroid_probe_scale_effective = float(test_run.get_runtime_setting(settings, "centroid_probe_scale", 1.0))

    test_vector = build_test_vector(fr=fr, mb=mb, pd=pd)
    opponent_data = dict(archetypes[opponent_name])
    opponent_vector = {key: float(test_run._personality_value_from_data(opponent_data, key)) for key in test_run.PERSONALITY_PARAM_KEYS}

    state = test_run.build_initial_state(
        fleet_a_params=test_run.to_personality_parameters(vector_to_archetype(f"test_FR{fr}_MB{mb}_PD{pd}", test_vector)),
        fleet_b_params=test_run.to_personality_parameters(opponent_data),
        fleet_size=fleet_size,
        aspect_ratio=aspect_ratio,
        unit_spacing=unit_spacing,
        unit_speed=unit_speed,
        unit_max_hit_points=unit_hp,
        arena_size=arena_size,
    )

    execution_cfg = test_run.SimulationExecutionConfig(
        steps=-1,
        capture_positions=False,
        frame_stride=1,
        include_target_lines=False,
        print_tick_summary=False,
        plot_diagnostics_enabled=False,
    )
    runtime_cfg = test_run.SimulationRuntimeConfig(
        decision_source=source,
        movement_model=movement_model_effective,
        movement=test_run.SimulationMovementConfig(
            v3a_experiment=movement_v3a_experiment_effective,
            centroid_probe_scale=centroid_probe_scale_effective,
        ),
        contact=test_run.SimulationContactConfig(
            attack_range=attack_range,
            damage_per_tick=damage_per_tick,
            separation_radius=unit_spacing,
            fire_quality_alpha=fire_quality_alpha,
            contact_hysteresis_h=contact_hysteresis_h,
            ch_enabled=ch_enabled,
            fsr_enabled=fsr_enabled,
            fsr_strength=fsr_strength,
        ),
        boundary=test_run.SimulationBoundaryConfig(
            enabled=boundary_enabled,
            hard_enabled=boundary_hard_enabled,
            soft_strength=boundary_soft_strength,
        ),
    )
    observer_cfg = test_run.SimulationObserverConfig(
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
        trajectory,
        alive_trajectory,
        fleet_size_trajectory,
        observer_telemetry,
        combat_telemetry,
        bridge_telemetry,
        collapse_shadow_telemetry,
        _position_frames,
    ) = test_run.run_simulation(
        initial_state=state,
        engine_cls=test_run.TestModeEngineTickSkeleton,
        execution_cfg=execution_cfg,
        runtime_cfg=runtime_cfg,
        observer_cfg=observer_cfg,
    )

    runtime_signal_metrics, runtime_signal_series = compute_runtime_signal_metrics(trajectory, pd_a=pd, pd_b=opponent_vector["pursuit_drive"])
    first_contact_tick = first_positive_tick(combat_telemetry.get("in_contact_count", []))
    first_damage_tick = first_positive_tick(combat_telemetry.get("damage_events_count", []))
    first_kill_tick = first_kill_tick_from_alive(alive_trajectory.get("A", []), alive_trajectory.get("B", []))
    if first_kill_tick is None:
        first_kill_tick = first_damage_tick

    bridge_ticks = test_run.compute_bridge_event_ticks(bridge_telemetry)
    cut_tick = parse_tick(bridge_ticks.get("formation_cut_tick"))
    pocket_tick = parse_tick(bridge_ticks.get("pocket_formation_tick"))
    event_flags = compute_event_flags(first_contact_tick, first_kill_tick, cut_tick, pocket_tick)

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

    first_deep_pursuit_tick = min(
        [tick for tick in (runtime_signal_metrics["A"]["first_deep_pursuit_tick"], runtime_signal_metrics["B"]["first_deep_pursuit_tick"]) if tick is not None],
        default=None,
    )
    collapse_prediction_error = None
    if first_deep_pursuit_tick is not None and pocket_tick is not None:
        collapse_prediction_error = int(first_deep_pursuit_tick) - int(pocket_tick)

    fleet_a_final = final_state.fleets.get("A")
    fleet_b_final = final_state.fleets.get("B")
    alive_a_final = len(fleet_a_final.unit_ids) if fleet_a_final else 0
    alive_b_final = len(fleet_b_final.unit_ids) if fleet_b_final else 0
    winner = "draw"
    if alive_a_final > alive_b_final:
        winner = "A"
    elif alive_b_final > alive_a_final:
        winner = "B"

    v2_series_a = list(trajectory.get("A", []))
    v2_series_b = list(trajectory.get("B", []))
    v3_series_a = list(observer_telemetry.get("cohesion_v3", {}).get("A", []))
    v3_series_b = list(observer_telemetry.get("cohesion_v3", {}).get("B", []))
    source_gap_a = compute_source_gap_metrics(v2_series_a, v3_series_a)
    source_gap_b = compute_source_gap_metrics(v2_series_b, v3_series_b)

    row = {
        "run_id": f"FR{fr}_MB{mb}_PD{pd}_{opponent_name}_{seed_profile['seed_profile_id']}_{source}",
        "seed_profile_id": seed_profile["seed_profile_id"],
        "runtime_decision_source_requested": source,
        "runtime_decision_source_effective": source,
        "movement_model_requested": movement_model_requested,
        "movement_model_effective": movement_model_effective,
        "movement_v3a_experiment_effective": movement_v3a_experiment_effective if movement_model_effective == "v3a" else "N/A",
        "centroid_probe_scale_effective": centroid_probe_scale_effective if movement_model_effective == "v3a" else "N/A",
        "cell_FR": int(fr),
        "cell_MB": int(mb),
        "cell_PD": int(pd),
        "opponent_archetype_name": opponent_name,
        "opponent_archetype_index": int(opponent_index),
        "injected_test_vector": json.dumps(test_vector, sort_keys=True),
        "injected_opponent_vector": json.dumps(opponent_vector, sort_keys=True),
        "random_seed_effective": int(seed_profile["random_seed_effective"]),
        "background_map_seed_effective": int(seed_profile["background_map_seed_effective"]),
        "metatype_random_seed_effective": int(seed_profile["metatype_random_seed_effective"]),
        "winner": winner,
        "end_tick": int(final_state.tick),
        "remaining_units_A": int(alive_a_final),
        "remaining_units_B": int(alive_b_final),
        "first_contact_tick": first_contact_tick,
        "first_kill_tick": first_kill_tick,
        "cut_tick": cut_tick,
        "pocket_tick": pocket_tick,
        "first_deep_pursuit_tick": first_deep_pursuit_tick,
        "first_deep_pursuit_tick_A": runtime_signal_metrics["A"]["first_deep_pursuit_tick"],
        "first_deep_pursuit_tick_B": runtime_signal_metrics["B"]["first_deep_pursuit_tick"],
        "pct_ticks_deep_pursuit_A": runtime_signal_metrics["A"]["pct_ticks_deep_pursuit"],
        "pct_ticks_deep_pursuit_B": runtime_signal_metrics["B"]["pct_ticks_deep_pursuit"],
        "mean_pursuit_intensity_A": runtime_signal_metrics["A"]["mean_pursuit_intensity"],
        "mean_pursuit_intensity_B": runtime_signal_metrics["B"]["mean_pursuit_intensity"],
        "mean_enemy_collapse_signal_A": runtime_signal_metrics["A"]["mean_enemy_collapse_signal"],
        "mean_enemy_collapse_signal_B": runtime_signal_metrics["B"]["mean_enemy_collapse_signal"],
        "p95_enemy_collapse_signal_A": runtime_signal_metrics["A"]["p95_enemy_collapse_signal"],
        "p95_enemy_collapse_signal_B": runtime_signal_metrics["B"]["p95_enemy_collapse_signal"],
        "collapse_prediction_error": collapse_prediction_error,
        "ar_forward_p90_A": quantile_or_nan(pre_ar_a, 0.90),
        "ar_forward_p90_B": quantile_or_nan(pre_ar_b, 0.90),
        "wedge_ratio_p10_A": quantile_or_nan(pre_wedge_a, 0.10),
        "wedge_ratio_p10_B": quantile_or_nan(pre_wedge_b, 0.10),
        "split_separation_p90_A": quantile_or_nan(pre_split_a, 0.90),
        "split_separation_p90_B": quantile_or_nan(pre_split_b, 0.90),
        "missing_cut": event_flags["missing_cut"],
        "pocket_without_cut": event_flags["pocket_without_cut"],
        "event_order_anomaly": event_flags["event_order_anomaly"],
        "determinism_digest": state_digest(final_state),
        "cohesion_gap_mean_abs_A": source_gap_a["mean_abs_gap"],
        "cohesion_gap_mean_abs_B": source_gap_b["mean_abs_gap"],
        "cohesion_gap_max_abs_A": source_gap_a["max_abs_gap"],
        "cohesion_gap_max_abs_B": source_gap_b["max_abs_gap"],
        "cohesion_gap_differs_A": source_gap_a["differs"],
        "cohesion_gap_differs_B": source_gap_b["differs"],
    }

    initial_hp_total = float(fleet_size) * float(unit_hp)
    context = {
        "fleet_a_data": vector_to_archetype(f"test_FR{fr}_MB{mb}_PD{pd}", test_vector),
        "fleet_b_data": opponent_data,
        "alive_trajectory": alive_trajectory,
        "fleet_size_trajectory": fleet_size_trajectory,
        "combat_telemetry": combat_telemetry,
        "bridge_telemetry": bridge_telemetry,
        "collapse_shadow_telemetry": collapse_shadow_telemetry,
        "final_state": final_state,
        "run_config_snapshot": {
            "initial_units_per_side": int(fleet_size),
            "test_mode": 2,
            "test_mode_label": "test",
            "random_seed_effective": int(seed_profile["random_seed_effective"]),
            "background_map_seed_effective": int(seed_profile["background_map_seed_effective"]),
            "metatype_random_seed_effective": int(seed_profile["metatype_random_seed_effective"]),
            "runtime_decision_source_effective": source,
            "collapse_decision_source_effective": "legacy_v2",
            "movement_model_effective": movement_model_effective,
            "movement_v3a_experiment_effective": movement_v3a_experiment_effective if movement_model_effective == "v3a" else "N/A",
            "centroid_probe_scale_effective": centroid_probe_scale_effective if movement_model_effective == "v3a" else "N/A",
            "precontact_centroid_probe_scale_effective": centroid_probe_scale_effective if movement_model_effective == "v3a" else "N/A",
            "attack_range": attack_range,
            "min_unit_spacing": unit_spacing,
            "arena_size": arena_size,
            "max_time_steps_effective": int(final_state.tick),
            "unit_speed": unit_speed,
            "damage_per_tick": damage_per_tick,
            "ch_enabled": ch_enabled,
            "contact_hysteresis_h": contact_hysteresis_h,
            "fsr_enabled": fsr_enabled,
            "fsr_strength": fsr_strength,
            "boundary_enabled": boundary_enabled,
            "boundary_soft_strength": boundary_soft_strength,
            "boundary_hard_enabled": boundary_hard_enabled,
            "boundary_hard_enabled_effective": boundary_hard_enabled,
            "bridge_theta_split": bridge_theta_split,
            "bridge_theta_env": bridge_theta_env,
            "bridge_sustain_ticks": bridge_sustain_ticks,
            "strategic_inflection_sustain_ticks": int(test_run.get_report_inference_setting(settings, "strategic_inflection_sustain_ticks", 12)),
            "tactical_swing_sustain_ticks": int(test_run.get_report_inference_setting(settings, "tactical_swing_sustain_ticks", 8)),
            "tactical_swing_min_amplitude": float(test_run.get_report_inference_setting(settings, "tactical_swing_min_amplitude", 2.0)),
            "tactical_swing_min_gap_ticks": int(test_run.get_report_inference_setting(settings, "tactical_swing_min_gap_ticks", 10)),
            "collapse_shadow_theta_conn_default": collapse_shadow_theta_conn_default,
            "collapse_shadow_theta_coh_default": collapse_shadow_theta_coh_default,
            "collapse_shadow_theta_force_default": collapse_shadow_theta_force_default,
            "collapse_shadow_theta_attr_default": collapse_shadow_theta_attr_default,
            "collapse_shadow_attrition_window": collapse_shadow_attrition_window,
            "collapse_shadow_sustain_ticks": collapse_shadow_sustain_ticks,
            "collapse_shadow_min_conditions": collapse_shadow_min_conditions,
        },
        "initial_fleet_sizes": {"A": initial_hp_total, "B": initial_hp_total},
    }
    return row, context


def build_delta_row(v2_row: dict, v3_row: dict) -> dict:
    def delta(key):
        try:
            return float(v3_row[key]) - float(v2_row[key])
        except (TypeError, ValueError):
            return float("nan")

    observable_runtime_difference = any(
        (
            (v2_row["first_deep_pursuit_tick_A"] != v3_row["first_deep_pursuit_tick_A"]),
            (v2_row["first_deep_pursuit_tick_B"] != v3_row["first_deep_pursuit_tick_B"]),
            abs(delta("mean_enemy_collapse_signal_A")) > EPS if math.isfinite(delta("mean_enemy_collapse_signal_A")) else False,
            abs(delta("mean_enemy_collapse_signal_B")) > EPS if math.isfinite(delta("mean_enemy_collapse_signal_B")) else False,
        )
    )
    return {
        "seed_profile_id": v2_row["seed_profile_id"],
        "cell_FR": v2_row["cell_FR"],
        "cell_MB": v2_row["cell_MB"],
        "cell_PD": v2_row["cell_PD"],
        "opponent_archetype_name": v2_row["opponent_archetype_name"],
        "delta_first_contact_tick": delta("first_contact_tick"),
        "delta_first_kill_tick": delta("first_kill_tick"),
        "delta_cut_tick": delta("cut_tick"),
        "delta_pocket_tick": delta("pocket_tick"),
        "delta_first_deep_pursuit_tick_A": delta("first_deep_pursuit_tick_A"),
        "delta_first_deep_pursuit_tick_B": delta("first_deep_pursuit_tick_B"),
        "delta_pct_ticks_deep_pursuit_A": delta("pct_ticks_deep_pursuit_A"),
        "delta_pct_ticks_deep_pursuit_B": delta("pct_ticks_deep_pursuit_B"),
        "delta_mean_pursuit_intensity_A": delta("mean_pursuit_intensity_A"),
        "delta_mean_pursuit_intensity_B": delta("mean_pursuit_intensity_B"),
        "delta_mean_enemy_collapse_signal_A": delta("mean_enemy_collapse_signal_A"),
        "delta_mean_enemy_collapse_signal_B": delta("mean_enemy_collapse_signal_B"),
        "delta_p95_enemy_collapse_signal_A": delta("p95_enemy_collapse_signal_A"),
        "delta_p95_enemy_collapse_signal_B": delta("p95_enemy_collapse_signal_B"),
        "delta_collapse_prediction_error": delta("collapse_prediction_error"),
        "delta_ar_forward_p90_A": delta("ar_forward_p90_A"),
        "delta_ar_forward_p90_B": delta("ar_forward_p90_B"),
        "delta_wedge_ratio_p10_A": delta("wedge_ratio_p10_A"),
        "delta_wedge_ratio_p10_B": delta("wedge_ratio_p10_B"),
        "delta_split_separation_p90_A": delta("split_separation_p90_A"),
        "delta_split_separation_p90_B": delta("split_separation_p90_B"),
        "missing_cut_v2": bool(v2_row["missing_cut"]),
        "missing_cut_v3_test": bool(v3_row["missing_cut"]),
        "pocket_without_cut_v2": bool(v2_row["pocket_without_cut"]),
        "pocket_without_cut_v3_test": bool(v3_row["pocket_without_cut"]),
        "event_order_anomaly_v2": bool(v2_row["event_order_anomaly"]),
        "event_order_anomaly_v3_test": bool(v3_row["event_order_anomaly"]),
        "observable_runtime_difference": bool(observable_runtime_difference),
    }


def build_signal_audit_row(v2_row: dict, v3_row: dict) -> dict:
    delta_first_a = (
        float(v3_row["first_deep_pursuit_tick_A"]) - float(v2_row["first_deep_pursuit_tick_A"])
        if v2_row["first_deep_pursuit_tick_A"] is not None and v3_row["first_deep_pursuit_tick_A"] is not None
        else float("nan")
    )
    delta_first_b = (
        float(v3_row["first_deep_pursuit_tick_B"]) - float(v2_row["first_deep_pursuit_tick_B"])
        if v2_row["first_deep_pursuit_tick_B"] is not None and v3_row["first_deep_pursuit_tick_B"] is not None
        else float("nan")
    )
    delta_mean_signal_a = float(v3_row["mean_enemy_collapse_signal_A"]) - float(v2_row["mean_enemy_collapse_signal_A"])
    delta_mean_signal_b = float(v3_row["mean_enemy_collapse_signal_B"]) - float(v2_row["mean_enemy_collapse_signal_B"])
    delta_pct_a = float(v3_row["pct_ticks_deep_pursuit_A"]) - float(v2_row["pct_ticks_deep_pursuit_A"])
    delta_pct_b = float(v3_row["pct_ticks_deep_pursuit_B"]) - float(v2_row["pct_ticks_deep_pursuit_B"])
    observable_runtime_difference = bool(
        v2_row["first_deep_pursuit_tick_A"] != v3_row["first_deep_pursuit_tick_A"]
        or v2_row["first_deep_pursuit_tick_B"] != v3_row["first_deep_pursuit_tick_B"]
        or abs(delta_mean_signal_a) > EPS
        or abs(delta_mean_signal_b) > EPS
    )
    return {
        "seed_profile_id": v2_row["seed_profile_id"],
        "cell_FR": v2_row["cell_FR"],
        "cell_MB": v2_row["cell_MB"],
        "cell_PD": v2_row["cell_PD"],
        "opponent_archetype_name": v2_row["opponent_archetype_name"],
        "runtime_decision_source_requested_v2": v2_row["runtime_decision_source_requested"],
        "runtime_decision_source_effective_v2": v2_row["runtime_decision_source_effective"],
        "runtime_decision_source_requested_v3_test": v3_row["runtime_decision_source_requested"],
        "runtime_decision_source_effective_v3_test": v3_row["runtime_decision_source_effective"],
        "effective_source_match_pair": (
            v2_row["runtime_decision_source_requested"] == v2_row["runtime_decision_source_effective"]
            and v3_row["runtime_decision_source_requested"] == v3_row["runtime_decision_source_effective"]
        ),
        "cohesion_gap_mean_abs_A": v2_row["cohesion_gap_mean_abs_A"],
        "cohesion_gap_mean_abs_B": v2_row["cohesion_gap_mean_abs_B"],
        "cohesion_gap_max_abs_A": v2_row["cohesion_gap_max_abs_A"],
        "cohesion_gap_max_abs_B": v2_row["cohesion_gap_max_abs_B"],
        "cohesion_gap_differs_A": bool(v2_row["cohesion_gap_differs_A"]),
        "cohesion_gap_differs_B": bool(v2_row["cohesion_gap_differs_B"]),
        "delta_first_deep_pursuit_tick_A": delta_first_a,
        "delta_first_deep_pursuit_tick_B": delta_first_b,
        "delta_mean_enemy_collapse_signal_A": delta_mean_signal_a,
        "delta_mean_enemy_collapse_signal_B": delta_mean_signal_b,
        "delta_pct_ticks_deep_pursuit_A": delta_pct_a,
        "delta_pct_ticks_deep_pursuit_B": delta_pct_b,
        "observable_runtime_difference": observable_runtime_difference,
    }


def aggregate_cell_summary(run_rows: list[dict], delta_rows: list[dict]) -> list[dict]:
    by_source = defaultdict(list)
    for row in run_rows:
        by_source[(row["cell_FR"], row["cell_MB"], row["cell_PD"], row["runtime_decision_source_effective"])].append(row)
    by_delta = defaultdict(list)
    for row in delta_rows:
        by_delta[(row["cell_FR"], row["cell_MB"], row["cell_PD"])].append(row)

    out = []
    for cell in sorted(by_delta.keys()):
        fr, mb, pd = cell
        v2_bucket = by_source.get((fr, mb, pd, "v2"), [])
        v3_bucket = by_source.get((fr, mb, pd, "v3_test"), [])
        delta_bucket = by_delta[cell]
        out.append(
            {
                "cell_FR": fr,
                "cell_MB": mb,
                "cell_PD": pd,
                "n_pairs": len(delta_bucket),
                "v2_first_contact_tick_mean": mean_or_nan([r["first_contact_tick"] for r in v2_bucket]),
                "v3_test_first_contact_tick_mean": mean_or_nan([r["first_contact_tick"] for r in v3_bucket]),
                "delta_first_contact_tick_mean": mean_or_nan([r["delta_first_contact_tick"] for r in delta_bucket]),
                "v2_cut_exists_rate": mean_or_nan([0 if r["missing_cut"] else 1 for r in v2_bucket]),
                "v3_test_cut_exists_rate": mean_or_nan([0 if r["missing_cut"] else 1 for r in v3_bucket]),
                "v2_pocket_exists_rate": mean_or_nan([1 if r["pocket_tick"] is not None else 0 for r in v2_bucket]),
                "v3_test_pocket_exists_rate": mean_or_nan([1 if r["pocket_tick"] is not None else 0 for r in v3_bucket]),
                "delta_mean_enemy_collapse_signal_A": mean_or_nan([r["delta_mean_enemy_collapse_signal_A"] for r in delta_bucket]),
                "delta_mean_enemy_collapse_signal_B": mean_or_nan([r["delta_mean_enemy_collapse_signal_B"] for r in delta_bucket]),
                "delta_pct_ticks_deep_pursuit_A": mean_or_nan([r["delta_pct_ticks_deep_pursuit_A"] for r in delta_bucket]),
                "delta_pct_ticks_deep_pursuit_B": mean_or_nan([r["delta_pct_ticks_deep_pursuit_B"] for r in delta_bucket]),
                "delta_mean_pursuit_intensity_A": mean_or_nan([r["delta_mean_pursuit_intensity_A"] for r in delta_bucket]),
                "delta_mean_pursuit_intensity_B": mean_or_nan([r["delta_mean_pursuit_intensity_B"] for r in delta_bucket]),
                "delta_ar_forward_p90_A": mean_or_nan([r["delta_ar_forward_p90_A"] for r in delta_bucket]),
                "delta_wedge_ratio_p10_A": mean_or_nan([r["delta_wedge_ratio_p10_A"] for r in delta_bucket]),
                "delta_split_separation_p90_A": mean_or_nan([r["delta_split_separation_p90_A"] for r in delta_bucket]),
                "event_order_anomaly_rate_v2": mean_or_nan([1 if r["event_order_anomaly"] else 0 for r in v2_bucket]),
                "event_order_anomaly_rate_v3_test": mean_or_nan([1 if r["event_order_anomaly"] else 0 for r in v3_bucket]),
            }
        )
    return out


def aggregate_pursuit_summary(run_rows: list[dict]) -> list[dict]:
    grouped = defaultdict(list)
    for row in run_rows:
        grouped[(row["runtime_decision_source_effective"], row["cell_PD"])].append(row)
    out = []
    for (source, pd), bucket in sorted(grouped.items()):
        out.append(
            {
                "runtime_decision_source_effective": source,
                "cell_PD": pd,
                "n_runs": len(bucket),
                "first_deep_pursuit_tick_A_mean": mean_or_nan([r["first_deep_pursuit_tick_A"] for r in bucket]),
                "first_deep_pursuit_tick_B_mean": mean_or_nan([r["first_deep_pursuit_tick_B"] for r in bucket]),
                "pct_ticks_deep_pursuit_A_mean": mean_or_nan([r["pct_ticks_deep_pursuit_A"] for r in bucket]),
                "pct_ticks_deep_pursuit_B_mean": mean_or_nan([r["pct_ticks_deep_pursuit_B"] for r in bucket]),
                "mean_pursuit_intensity_A_mean": mean_or_nan([r["mean_pursuit_intensity_A"] for r in bucket]),
                "mean_pursuit_intensity_B_mean": mean_or_nan([r["mean_pursuit_intensity_B"] for r in bucket]),
                "mean_enemy_collapse_signal_A_mean": mean_or_nan([r["mean_enemy_collapse_signal_A"] for r in bucket]),
                "mean_enemy_collapse_signal_B_mean": mean_or_nan([r["mean_enemy_collapse_signal_B"] for r in bucket]),
                "p95_enemy_collapse_signal_A_mean": mean_or_nan([r["p95_enemy_collapse_signal_A"] for r in bucket]),
                "p95_enemy_collapse_signal_B_mean": mean_or_nan([r["p95_enemy_collapse_signal_B"] for r in bucket]),
            }
        )
    return out


def export_brf_sample(sample_row: dict, context: dict):
    topic = (
        f"cohesion_source_{sample_row['runtime_decision_source_effective']}_"
        f"FR{sample_row['cell_FR']}_MB{sample_row['cell_MB']}_PD{sample_row['cell_PD']}_"
        f"{sample_row['opponent_archetype_name']}_{sample_row['seed_profile_id']}"
    )
    report_markdown = test_run.build_battle_report_markdown(
        settings_source_path="test_run/test_run_v1_0.settings.json",
        display_language="EN",
        random_seed_effective=int(sample_row["random_seed_effective"]),
        fleet_a_data=context["fleet_a_data"],
        fleet_b_data=context["fleet_b_data"],
        initial_fleet_sizes=context["initial_fleet_sizes"],
        alive_trajectory=context["alive_trajectory"],
        fleet_size_trajectory=context["fleet_size_trajectory"],
        combat_telemetry=context["combat_telemetry"],
        bridge_telemetry=context["bridge_telemetry"],
        collapse_shadow_telemetry=context["collapse_shadow_telemetry"],
        final_state=context["final_state"],
        run_config_snapshot=context["run_config_snapshot"],
    )
    output_path = BRF_DIR / f"{topic}_Battle_Report_Framework_v1.0.md"
    output_path.write_text(report_markdown, encoding="utf-8")
    return output_path


def run_phase(settings_base: dict, archetypes: dict, opponents: list[str], cells: list[tuple[int, int, int]], seed_profiles: list[dict], phase_label: str) -> tuple[list[dict], dict]:
    rows = []
    contexts = {}
    total_runs = len(cells) * len(opponents) * len(seed_profiles) * len(SOURCES)
    run_idx = 0
    for fr, mb, pd in cells:
        for opponent_index, opponent_name in enumerate(opponents, start=1):
            for seed_profile in seed_profiles:
                for source in SOURCES:
                    settings_eval = apply_doe_overrides(apply_seed_profile(copy.deepcopy(settings_base), seed_profile), source)
                    row, context = run_single_case(
                        settings=settings_eval,
                        archetypes=archetypes,
                        opponent_name=opponent_name,
                        opponent_index=opponent_index,
                        fr=fr,
                        mb=mb,
                        pd=pd,
                        source=source,
                        seed_profile=seed_profile,
                    )
                    row["phase_label"] = phase_label
                    rows.append(row)
                    contexts[row["run_id"]] = context
                    run_idx += 1
                    if run_idx % 24 == 0 or run_idx == total_runs:
                        print(f"[{phase_label}] runs {run_idx}/{total_runs}")
    return rows, contexts


def pair_rows(run_rows: list[dict]) -> tuple[list[dict], list[dict]]:
    keyed = defaultdict(dict)
    for row in run_rows:
        key = (
            row["phase_label"],
            row["seed_profile_id"],
            row["cell_FR"],
            row["cell_MB"],
            row["cell_PD"],
            row["opponent_archetype_name"],
        )
        keyed[key][row["runtime_decision_source_effective"]] = row

    delta_rows = []
    audit_rows = []
    for key in sorted(keyed.keys()):
        bucket = keyed[key]
        if "v2" not in bucket or "v3_test" not in bucket:
            continue
        v2_row = bucket["v2"]
        v3_row = bucket["v3_test"]
        delta_rows.append(build_delta_row(v2_row, v3_row))
        audit_rows.append(build_signal_audit_row(v2_row, v3_row))
    return delta_rows, audit_rows


def preflight_pass(preflight_rows: list[dict], preflight_audit: list[dict]) -> tuple[bool, dict]:
    cond1 = all(
        row["runtime_decision_source_requested"] == row["runtime_decision_source_effective"]
        for row in preflight_rows
    )
    cond2 = any(bool(row["cohesion_gap_differs_A"]) or bool(row["cohesion_gap_differs_B"]) for row in preflight_rows if row["runtime_decision_source_effective"] == "v2")
    cond3 = any(bool(row["observable_runtime_difference"]) for row in preflight_audit)
    return (cond1 and cond2 and cond3), {"cond1": cond1, "cond2": cond2, "cond3": cond3}


def sample_brf_pairs(delta_rows: list[dict]) -> list[tuple[str, int, int, int, str]]:
    pair_keys = sorted(
        {
            (
                row["seed_profile_id"],
                row["cell_FR"],
                row["cell_MB"],
                row["cell_PD"],
                row["opponent_archetype_name"],
            )
            for row in delta_rows
        }
    )
    rng = random.Random(BRF_SAMPLE_SEED)
    rng.shuffle(pair_keys)
    return pair_keys[:BRF_PAIR_COUNT]


def build_report(preflight_gate: dict, main_rows: list[dict], main_delta: list[dict], sample_paths: list[Path]):
    by_source = defaultdict(list)
    for row in main_rows:
        by_source[row["runtime_decision_source_effective"]].append(row)

    lines = [
        "# Cohesion Runtime Decision Source Evaluation Report",
        "",
        "## Scope",
        "- Evaluation type: runtime collapse signal source replacement only (`v2` vs `v3_test`)",
        "- Movement baseline frozen: `v3a` + `exp_precontact_centroid_probe` + `centroid_probe_scale=0.5`",
        "- Event bridge frozen: `theta_split=1.7`, `theta_env=0.5`",
        "- Boundary override for DOE: `enabled=false`, `soft_strength=1.0`, `hard_enabled=false`",
        "- Opponents: first six canonical archetypes (excluding `yang` / `default`)",
        "- Controlled persona: FR/MB/PD cell injection; other seven parameters fixed at 5; FCR fixed at 5",
        "",
        "## Fixed Seed Discipline",
        f"- `SP01`: random={SEED_PROFILES[0]['random_seed_effective']}, background={SEED_PROFILES[0]['background_map_seed_effective']}, metatype={SEED_PROFILES[0]['metatype_random_seed_effective']}",
        f"- `SP02`: random={SEED_PROFILES[1]['random_seed_effective']}, background={SEED_PROFILES[1]['background_map_seed_effective']}, metatype={SEED_PROFILES[1]['metatype_random_seed_effective']}",
        "",
        "## Preflight",
        "- Cells: `FR2_MB2_PD2`, `FR5_MB5_PD5`, `FR8_MB8_PD8`",
        "- Opponents: first two canonical archetypes",
        "- Sources: `v2` vs `v3_test`",
        "- Total runs: 12",
        "",
        f"- Condition 1 (`effective == requested`): **{preflight_gate['cond1']}**",
        f"- Condition 2 (`cohesion_v2` differs from `cohesion_v3_shadow`): **{preflight_gate['cond2']}**",
        f"- Condition 3 (observable runtime-path difference exists): **{preflight_gate['cond3']}**",
    ]
    if not main_rows:
        lines += ["", "## Main DOE", "- Skipped due to preflight failure."]
    else:
        lines += [
            "",
            "## Main DOE",
            f"- Total runs: {len(main_rows)}",
            "- Grid: FR x MB x PD = 3 x 3 x 3",
            "- Opponents: 6",
            "- Sources: 2",
            "- Seed profiles: 2",
            "",
            "## Overall Source Comparison",
            "| source | n_runs | first_contact_mean | cut_exists_rate | pocket_exists_rate | first_deep_pursuit_A_mean | first_deep_pursuit_B_mean | mean_enemy_collapse_signal_A | mean_enemy_collapse_signal_B |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
        for source in ("v2", "v3_test"):
            bucket = by_source.get(source, [])
            lines.append(
                f"| {source} | {len(bucket)} | {mean_or_nan([r['first_contact_tick'] for r in bucket]):.4f} | "
                f"{mean_or_nan([0 if r['missing_cut'] else 1 for r in bucket]):.4f} | "
                f"{mean_or_nan([1 if r['pocket_tick'] is not None else 0 for r in bucket]):.4f} | "
                f"{mean_or_nan([r['first_deep_pursuit_tick_A'] for r in bucket]):.4f} | "
                f"{mean_or_nan([r['first_deep_pursuit_tick_B'] for r in bucket]):.4f} | "
                f"{mean_or_nan([r['mean_enemy_collapse_signal_A'] for r in bucket]):.4f} | "
                f"{mean_or_nan([r['mean_enemy_collapse_signal_B'] for r in bucket]):.4f} |"
            )
        lines += [
            "",
            "## Runtime-Path Delta Summary (`v3_test - v2`)",
            f"- `first_contact_tick` mean delta: {mean_or_nan([r['delta_first_contact_tick'] for r in main_delta]):.4f}",
            f"- `first_kill_tick` mean delta: {mean_or_nan([r['delta_first_kill_tick'] for r in main_delta]):.4f}",
            f"- `first_deep_pursuit_tick_A` mean delta: {mean_or_nan([r['delta_first_deep_pursuit_tick_A'] for r in main_delta]):.4f}",
            f"- `first_deep_pursuit_tick_B` mean delta: {mean_or_nan([r['delta_first_deep_pursuit_tick_B'] for r in main_delta]):.4f}",
            f"- `mean_enemy_collapse_signal_A` mean delta: {mean_or_nan([r['delta_mean_enemy_collapse_signal_A'] for r in main_delta]):.4f}",
            f"- `mean_enemy_collapse_signal_B` mean delta: {mean_or_nan([r['delta_mean_enemy_collapse_signal_B'] for r in main_delta]):.4f}",
            f"- `mean_pursuit_intensity_A` mean delta: {mean_or_nan([r['delta_mean_pursuit_intensity_A'] for r in main_delta]):.4f}",
            f"- `mean_pursuit_intensity_B` mean delta: {mean_or_nan([r['delta_mean_pursuit_intensity_B'] for r in main_delta]):.4f}",
            "",
            "## Event Integrity",
            f"- Missing cut count: `{sum(1 for r in main_rows if r['missing_cut'])}`",
            f"- Pocket without cut count: `{sum(1 for r in main_rows if r['pocket_without_cut'])}`",
            f"- Event order anomaly count: `{sum(1 for r in main_rows if r['event_order_anomaly'])}`",
            "",
            "## Geometry Delta Summary (`v3_test - v2`)",
            f"- `AR_forward p90 A` mean delta: {mean_or_nan([r['delta_ar_forward_p90_A'] for r in main_delta]):.4f}",
            f"- `WedgeRatio p10 A` mean delta: {mean_or_nan([r['delta_wedge_ratio_p10_A'] for r in main_delta]):.4f}",
            f"- `SplitSeparation p90 A` mean delta: {mean_or_nan([r['delta_split_separation_p90_A'] for r in main_delta]):.4f}",
            "",
            "## Human Sample BRFs",
            f"- Deterministic sample seed: `{BRF_SAMPLE_SEED}`",
        ]
        for path in sample_paths:
            lines.append(f"- `{path.relative_to(ROOT).as_posix()}`")
        lines += [
            "",
            "## Engineering Recommendation",
            "- Use the attached DOE evidence to decide whether `v3_test` should replace `v2` as runtime collapse signal source.",
            "- This report does not treat the change as a full cohesion mechanism replacement.",
        ]

    (OUT_DIR / "Cohesion_Runtime_Decision_Source_Evaluation_Report.md").write_text("\n".join(lines), encoding="utf-8")


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    BRF_DIR.mkdir(parents=True, exist_ok=True)

    settings_base = test_run.load_json_file(ROOT / "test_run" / "test_run_v1_0.settings.json")
    archetypes = test_run.load_json_file(ROOT / "archetypes" / "archetypes_v1_5.json")
    preflight_opponents = select_canonical_opponents(archetypes, PREFLIGHT_OPPONENT_COUNT)
    main_opponents = select_canonical_opponents(archetypes, MAIN_OPPONENT_COUNT)

    preflight_rows, _ = run_phase(
        settings_base=settings_base,
        archetypes=archetypes,
        opponents=preflight_opponents,
        cells=PREFLIGHT_CELLS,
        seed_profiles=[SEED_PROFILES[0]],
        phase_label="preflight",
    )
    preflight_delta, preflight_audit = pair_rows(preflight_rows)
    preflight_ok, preflight_gate = preflight_pass(preflight_rows, preflight_audit)

    main_rows = []
    main_contexts = {}
    main_delta = []
    main_audit = []
    cell_summary = []
    pursuit_summary = []
    sample_paths = []

    if preflight_ok:
        main_rows, main_contexts = run_phase(
            settings_base=settings_base,
            archetypes=archetypes,
            opponents=main_opponents,
            cells=[(fr, mb, pd) for fr in FR_LEVELS for mb in MB_LEVELS for pd in PD_LEVELS],
            seed_profiles=SEED_PROFILES,
            phase_label="main",
        )
        main_delta, main_audit = pair_rows(main_rows)
        cell_summary = aggregate_cell_summary(main_rows, main_delta)
        pursuit_summary = aggregate_pursuit_summary(main_rows)

        pair_sample_keys = sample_brf_pairs(main_delta)
        keyed_rows = {
            (
                row["seed_profile_id"],
                row["cell_FR"],
                row["cell_MB"],
                row["cell_PD"],
                row["opponent_archetype_name"],
                row["runtime_decision_source_effective"],
            ): row
            for row in main_rows
        }
        for seed_profile_id, fr, mb, pd, opponent_name in pair_sample_keys:
            for source in SOURCES:
                row = keyed_rows[(seed_profile_id, fr, mb, pd, opponent_name, source)]
                sample_paths.append(export_brf_sample(row, main_contexts[row["run_id"]]))

    run_rows = preflight_rows + main_rows
    delta_rows = preflight_delta + main_delta
    audit_rows = preflight_audit + main_audit

    write_csv(OUT_DIR / "cohesion_source_doe_run_table.csv", run_rows)
    write_csv(OUT_DIR / "cohesion_source_doe_delta_table.csv", delta_rows)
    write_csv(OUT_DIR / "cohesion_source_doe_cell_summary.csv", cell_summary if cell_summary else [{"preflight_failed": True}])
    write_csv(OUT_DIR / "cohesion_source_doe_pursuit_summary.csv", pursuit_summary if pursuit_summary else [{"preflight_failed": True}])
    write_csv(OUT_DIR / "cohesion_source_doe_signal_audit.csv", audit_rows)
    build_report(preflight_gate, main_rows, main_delta, sample_paths)

    status = "PASS" if preflight_ok else "FAIL"
    print(f"[preflight] {status} cond1={preflight_gate['cond1']} cond2={preflight_gate['cond2']} cond3={preflight_gate['cond3']}")
    if preflight_ok:
        print(f"[main] completed runs={len(main_rows)}")
    else:
        print("[main] skipped due to preflight failure")


if __name__ == "__main__":
    main()
