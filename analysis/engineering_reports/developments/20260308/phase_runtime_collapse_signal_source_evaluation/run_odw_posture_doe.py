"""
Dedicated ODW posture-bias DOE runner.

Scope:
- movement v3a ODW posture-bias prototype only
- runtime collapse-signal baseline frozen at v3_test @ 1.1
- Side A varies only offense_defense_weight and prototype gain k
- all other Side A personality dimensions are fixed at 5.0

This runner must not reuse the legacy collapse-signal DOE helper assumptions.
"""

import copy
import csv
import hashlib
import importlib.util
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
TEST_RUN_SRC = ROOT / "test_run" / "test_run_v1_0.py"
BRF_BUILDER_SRC = ROOT / "test_run" / "battle_report_builder.py"
SETTINGS_PATH = ROOT / "test_run" / "test_run_v1_0.settings.json"
ARCHETYPES_PATH = ROOT / "archetypes" / "archetypes_v1_5.json"
OUT_DIR = Path(__file__).resolve().parent

ODW_LEVELS = [2, 5, 8]
K_LEVELS = [0.0, 0.25, 0.5, 0.75, 1.0]
OPPONENT_IDS = ["reinhard", "kircheis", "reuenthal", "mittermeyer", "bittenfeld", "muller"]
FIXED_SEED_PROFILE = {
    "seed_profile_id": "SP01",
    "random_seed_effective": 1981813971,
    "background_map_seed_effective": 897304369,
    "metatype_random_seed_effective": 3095987153,
}


def load_module(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


test_run = load_module(TEST_RUN_SRC, "test_run_odw_module")
brf_builder = load_module(BRF_BUILDER_SRC, "battle_report_builder_odw_module")


def load_json_file(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_csv(path: Path, rows: list[dict]):
    if not rows:
        return
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


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


def compute_event_flags(first_contact_tick, first_kill_tick, cut_tick, pocket_tick):
    missing_cut = cut_tick is None
    pocket_without_cut = pocket_tick is not None and cut_tick is None
    event_order_anomaly = False
    anomaly_label = ""
    if first_kill_tick is not None and first_contact_tick is not None and first_kill_tick < first_contact_tick:
        event_order_anomaly = True
        anomaly_label = "kill_before_contact"
    elif cut_tick is not None and first_contact_tick is not None and cut_tick < first_contact_tick:
        event_order_anomaly = True
        anomaly_label = "cut_before_contact"
    elif cut_tick is not None and first_kill_tick is not None and cut_tick < first_kill_tick:
        event_order_anomaly = True
        anomaly_label = "cut_before_kill"
    elif pocket_tick is not None and cut_tick is not None and pocket_tick < cut_tick:
        event_order_anomaly = True
        anomaly_label = "pocket_before_cut"
    return {
        "missing_cut": missing_cut,
        "pocket_without_cut": pocket_without_cut,
        "event_order_anomaly": event_order_anomaly,
        "event_order_anomaly_label": anomaly_label,
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


def compute_runtime_signal_metrics(trajectory: dict, pd_a: float, pd_b: float) -> dict:
    cohesion_a = [float(v) for v in trajectory.get("A", [])]
    cohesion_b = [float(v) for v in trajectory.get("B", [])]
    n_ticks = max(len(cohesion_a), len(cohesion_b))
    pd_norm_a = (float(pd_a) - 1.0) / 8.0
    pd_norm_b = (float(pd_b) - 1.0) / 8.0
    threshold_a = 1.0 - pd_norm_a
    threshold_b = 1.0 - pd_norm_b

    result = {}
    for side, enemy_series, threshold in (
        ("A", cohesion_b, threshold_a),
        ("B", cohesion_a, threshold_b),
    ):
        enemy_collapse_signal = []
        deep_pursuit_flags = []
        pursuit_intensity_values = []
        for idx in range(n_ticks):
            enemy_cohesion = enemy_series[idx] if idx < len(enemy_series) else (enemy_series[-1] if enemy_series else 1.0)
            signal = 1.0 - float(enemy_cohesion)
            if signal < 0.0:
                signal = 0.0
            elif signal > 1.0:
                signal = 1.0
            enemy_collapse_signal.append(signal)
            deep = signal > threshold
            deep_pursuit_flags.append(deep)
            if deep and threshold < 1.0:
                pursuit_intensity = (signal - threshold) / max(1e-12, 1.0 - threshold)
                if pursuit_intensity < 0.0:
                    pursuit_intensity = 0.0
                elif pursuit_intensity > 1.0:
                    pursuit_intensity = 1.0
            else:
                pursuit_intensity = 0.0
            pursuit_intensity_values.append(pursuit_intensity)
        first_deep_pursuit_tick = None
        for idx, flag in enumerate(deep_pursuit_flags, start=1):
            if flag:
                first_deep_pursuit_tick = idx
                break
        result[side] = {
            "first_deep_pursuit_tick": first_deep_pursuit_tick,
            "pct_ticks_deep_pursuit": ((100.0 * sum(1 for flag in deep_pursuit_flags if flag) / float(len(deep_pursuit_flags))) if deep_pursuit_flags else float("nan")),
            "mean_pursuit_intensity": mean_or_nan(pursuit_intensity_values),
            "mean_enemy_collapse_signal": mean_or_nan(enemy_collapse_signal),
            "p95_enemy_collapse_signal": quantile_or_nan(enemy_collapse_signal, 0.95),
        }
    return result


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


def build_side_a_vector(odw: float) -> dict:
    return {
        "force_concentration_ratio": 5.0,
        "mobility_bias": 5.0,
        "offense_defense_weight": float(odw),
        "risk_appetite": 5.0,
        "time_preference": 5.0,
        "targeting_logic": 5.0,
        "formation_rigidity": 5.0,
        "perception_radius": 5.0,
        "pursuit_drive": 5.0,
        "retreat_threshold": 5.0,
    }

def load_inputs():
    settings = load_json_file(SETTINGS_PATH)
    archetypes = load_json_file(ARCHETYPES_PATH)
    return settings, archetypes


def build_run_settings(base_settings: dict, k: float) -> dict:
    settings = copy.deepcopy(base_settings)
    visualization = settings.setdefault("visualization", {})
    export_video = visualization.setdefault("export_video", {})
    runtime = settings.setdefault("runtime", {})
    selectors = runtime.setdefault("selectors", {})
    movement = runtime.setdefault("movement", {}).setdefault("v3a", {})
    semantics = runtime.setdefault("semantics", {}).setdefault("collapse_signal", {})
    run_control = settings.setdefault("run_control", {})

    selectors["movement_model"] = "baseline"
    selectors["cohesion_decision_source"] = "baseline"
    movement["odw_posture_bias_enabled"] = bool(k > 0.0)
    movement["odw_posture_bias_k"] = float(k)
    semantics["v3_connect_radius_multiplier"] = 1.1
    semantics["v3_r_ref_radius_multiplier"] = 1.0

    run_control["animate"] = False
    run_control["test_mode"] = 2
    run_control["random_seed"] = int(FIXED_SEED_PROFILE["random_seed_effective"])
    run_control["metatype_random_seed"] = int(FIXED_SEED_PROFILE["metatype_random_seed_effective"])
    settings.setdefault("battlefield", {})["background_map_seed"] = int(FIXED_SEED_PROFILE["background_map_seed_effective"])
    export_video["enabled"] = False
    return settings


def run_single_case(base_settings: dict, archetypes: dict, opponent_id: str, odw: int, k: float) -> dict:
    settings = build_run_settings(base_settings, k)

    opponent_data = dict(archetypes[opponent_id])
    side_a_vector = build_side_a_vector(odw)

    fleet_size = int(test_run.get_fleet_setting(settings, "initial_fleet_size", 100))
    aspect_ratio = float(test_run.get_fleet_setting(settings, "initial_fleet_aspect_ratio", 2.0))
    unit_spacing = float(test_run.get_runtime_setting(settings, "min_unit_spacing", 2.0))
    unit_speed = float(test_run.get_unit_setting(settings, "unit_speed", 1.0))
    unit_hp = float(test_run.get_unit_setting(settings, "unit_max_hit_points", 100.0))
    arena_size = float(test_run.get_battlefield_setting(settings, "arena_size", 200.0))
    attack_range = float(test_run.get_unit_setting(settings, "attack_range", 5.0))
    damage_per_tick = float(test_run.get_unit_setting(settings, "damage_per_tick", 1.0))
    fire_quality_alpha = float(test_run.get_runtime_setting(settings, "fire_quality_alpha", 0.1))
    contact_hysteresis_h = float(test_run.get_runtime_setting(settings, "contact_hysteresis_h", 0.1))
    fsr_strength = float(test_run.get_runtime_setting(settings, "fsr_strength", 0.1))
    boundary_enabled = bool(test_run.get_runtime_setting(settings, "boundary_enabled", True))
    boundary_hard_enabled = bool(test_run.get_runtime_setting(settings, "boundary_hard_enabled", False))
    boundary_soft_strength = float(test_run.get_runtime_setting(settings, "boundary_soft_strength", 0.1))
    alpha_sep = float(test_run.get_runtime_setting(settings, "alpha_sep", 0.6))
    movement_model_requested, movement_model_effective = test_run.resolve_movement_model(
        test_run.get_runtime_setting(settings, "movement_model", "baseline")
    )
    movement_v3a_experiment = str(test_run.get_runtime_setting(settings, "movement_v3a_experiment", "base")).strip().lower() or "base"
    centroid_probe_scale = float(test_run.get_runtime_setting(settings, "centroid_probe_scale", 1.0))
    cohesion_source_requested, cohesion_source_effective = test_run.resolve_runtime_decision_source(
        str(test_run.get_runtime_setting(settings, "cohesion_decision_source", "baseline")).strip().lower() or "baseline",
        int(test_run.get_run_control_setting(settings, "test_mode", 2)),
    )
    v3_connect_radius_multiplier = float(test_run.get_runtime_setting(settings, "v3_connect_radius_multiplier", 1.1))
    v3_r_ref_radius_multiplier = float(test_run.get_runtime_setting(settings, "v3_r_ref_radius_multiplier", 1.0))
    odw_enabled = bool(test_run.get_runtime_setting(settings, "odw_posture_bias_enabled", False))
    odw_k = float(test_run.get_runtime_setting(settings, "odw_posture_bias_k", 0.0))

    state = test_run.build_initial_state(
        fleet_a_params=test_run.to_personality_parameters(vector_to_archetype(f"odw_probe_{odw}", side_a_vector)),
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
        decision_source=cohesion_source_effective,
        movement_model=movement_model_effective,
        movement=test_run.SimulationMovementConfig(
            v3a_experiment=movement_v3a_experiment,
            centroid_probe_scale=centroid_probe_scale,
            odw_posture_bias_enabled=odw_enabled,
            odw_posture_bias_k=odw_k,
            v3_connect_radius_multiplier=v3_connect_radius_multiplier,
            v3_r_ref_radius_multiplier=v3_r_ref_radius_multiplier,
        ),
        contact=test_run.SimulationContactConfig(
            attack_range=attack_range,
            damage_per_tick=damage_per_tick,
            separation_radius=unit_spacing,
            fire_quality_alpha=fire_quality_alpha,
            contact_hysteresis_h=contact_hysteresis_h,
            ch_enabled=(contact_hysteresis_h > 0.0),
            fsr_enabled=(fsr_strength > 0.0),
            fsr_strength=fsr_strength,
            alpha_sep=alpha_sep,
        ),
        boundary=test_run.SimulationBoundaryConfig(
            enabled=boundary_enabled,
            hard_enabled=boundary_hard_enabled,
            soft_strength=boundary_soft_strength,
        ),
    )
    observer_cfg = test_run.SimulationObserverConfig(
        enabled=True,
        bridge_theta_split=float(test_run.get_runtime_setting(settings, "bridge_theta_split", 1.7)),
        bridge_theta_env=float(test_run.get_runtime_setting(settings, "bridge_theta_env", 0.5)),
        bridge_sustain_ticks=int(test_run.get_runtime_setting(settings, "bridge_sustain_ticks", 20)),
        collapse_shadow_theta_conn_default=float(test_run.get_runtime_setting(settings, "collapse_shadow_theta_conn_default", 0.10)),
        collapse_shadow_theta_coh_default=float(test_run.get_runtime_setting(settings, "collapse_shadow_theta_coh_default", 0.98)),
        collapse_shadow_theta_force_default=float(test_run.get_runtime_setting(settings, "collapse_shadow_theta_force_default", 0.95)),
        collapse_shadow_theta_attr_default=float(test_run.get_runtime_setting(settings, "collapse_shadow_theta_attr_default", 0.10)),
        collapse_shadow_attrition_window=int(test_run.get_runtime_setting(settings, "collapse_shadow_attrition_window", 20)),
        collapse_shadow_sustain_ticks=int(test_run.get_runtime_setting(settings, "collapse_shadow_sustain_ticks", 10)),
        collapse_shadow_min_conditions=int(test_run.get_runtime_setting(settings, "collapse_shadow_min_conditions", 2)),
    )
    (
        final_state,
        trajectory,
        alive_trajectory,
        _fleet_size_trajectory,
        observer_telemetry,
        combat_telemetry,
        bridge_telemetry,
        _collapse_shadow_telemetry,
        _position_frames,
    ) = test_run.run_simulation(
        initial_state=state,
        engine_cls=test_run.TestModeEngineTickSkeleton,
        execution_cfg=execution_cfg,
        runtime_cfg=runtime_cfg,
        observer_cfg=observer_cfg,
    )

    first_contact_tick = first_positive_tick(combat_telemetry.get("in_contact_count", []))
    first_damage_tick = first_positive_tick(combat_telemetry.get("damage_events_count", []))
    first_kill_tick = first_kill_tick_from_alive(alive_trajectory.get("A", []), alive_trajectory.get("B", []))
    if first_kill_tick is None:
        first_kill_tick = first_damage_tick

    bridge_ticks = brf_builder.compute_bridge_event_ticks(bridge_telemetry)
    cut_tick = parse_tick(bridge_ticks.get("formation_cut_tick"))
    pocket_tick = parse_tick(bridge_ticks.get("pocket_formation_tick"))
    event_flags = compute_event_flags(first_contact_tick, first_kill_tick, cut_tick, pocket_tick)

    ar_a = list(bridge_telemetry.get("AR", {}).get("A", []))
    wedge_a = list(bridge_telemetry.get("wedge_ratio", {}).get("A", []))
    split_a = list(bridge_telemetry.get("split_separation", {}).get("A", []))
    net_push = list(observer_telemetry.get("net_axis_push", {}).get("net", []))

    pre_ar_a = precontact_focus_slice(ar_a, first_contact_tick)
    pre_wedge_a = precontact_focus_slice(wedge_a, first_contact_tick)
    pre_split_a = precontact_focus_slice(split_a, first_contact_tick)
    pre_net_push = precontact_focus_slice(net_push, first_contact_tick)
    pre_net_push_abs = [abs(v) for v in finite(pre_net_push)]

    runtime_signal_metrics = compute_runtime_signal_metrics(
        trajectory,
        pd_a=side_a_vector["pursuit_drive"],
        pd_b=float(test_run._personality_value_from_data(opponent_data, "pursuit_drive")),
    )

    fleet_a_final = final_state.fleets.get("A")
    fleet_b_final = final_state.fleets.get("B")
    alive_a_final = len(fleet_a_final.unit_ids) if fleet_a_final else 0
    alive_b_final = len(fleet_b_final.unit_ids) if fleet_b_final else 0

    c_conn_a = precontact_focus_slice(observer_telemetry.get("c_conn", {}).get("A", []), first_contact_tick)
    rho_a = precontact_focus_slice(observer_telemetry.get("rho", {}).get("A", []), first_contact_tick)
    c_scale_a = precontact_focus_slice(observer_telemetry.get("c_scale", {}).get("A", []), first_contact_tick)

    row = {
        "run_id": f"ODW{odw}_K{str(k).replace('.', 'p')}_{opponent_id}",
        "seed_profile_id": FIXED_SEED_PROFILE["seed_profile_id"],
        "random_seed_effective": FIXED_SEED_PROFILE["random_seed_effective"],
        "background_map_seed_effective": FIXED_SEED_PROFILE["background_map_seed_effective"],
        "metatype_random_seed_effective": FIXED_SEED_PROFILE["metatype_random_seed_effective"],
        "opponent_archetype_id": opponent_id,
        "runtime_decision_source_requested": cohesion_source_requested,
        "runtime_decision_source_effective": cohesion_source_effective,
        "movement_model_requested": movement_model_requested,
        "movement_model_effective": movement_model_effective,
        "movement_v3a_experiment_effective": movement_v3a_experiment if movement_model_effective == "v3a" else "N/A",
        "centroid_probe_scale_effective": centroid_probe_scale if movement_model_effective == "v3a" else "N/A",
        "odw_posture_bias_enabled_effective": odw_enabled,
        "odw_posture_bias_k_effective": odw_k,
        "side_a_odw": float(odw),
        "side_a_fixed_vector": json.dumps(side_a_vector, sort_keys=True),
        "opponent_vector": json.dumps({k2: float(test_run._personality_value_from_data(opponent_data, k2)) for k2 in test_run.PERSONALITY_PARAM_KEYS}, sort_keys=True),
        "end_tick": int(final_state.tick),
        "remaining_units_A": int(alive_a_final),
        "remaining_units_B": int(alive_b_final),
        "first_contact_tick": first_contact_tick,
        "first_kill_tick": first_kill_tick,
        "cut_tick": cut_tick,
        "pocket_tick": pocket_tick,
        "missing_cut": event_flags["missing_cut"],
        "pocket_without_cut": event_flags["pocket_without_cut"],
        "event_order_anomaly": event_flags["event_order_anomaly"],
        "event_order_anomaly_label": event_flags["event_order_anomaly_label"],
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
        "precontact_ar_forward_p90_A": quantile_or_nan(pre_ar_a, 0.90),
        "precontact_wedge_ratio_p10_A": quantile_or_nan(pre_wedge_a, 0.10),
        "precontact_split_separation_p90_A": quantile_or_nan(pre_split_a, 0.90),
        "precontact_net_axis_push_mean": mean_or_nan(pre_net_push),
        "precontact_net_axis_push_abs_mean": mean_or_nan(pre_net_push_abs),
        "precontact_net_axis_push_abs_p90": quantile_or_nan(pre_net_push_abs, 0.90),
        "precontact_net_axis_push_abs_max": max(pre_net_push_abs) if pre_net_push_abs else float("nan"),
        "precontact_c_conn_mean_A": mean_or_nan(c_conn_a),
        "precontact_rho_mean_A": mean_or_nan(rho_a),
        "precontact_c_scale_mean_A": mean_or_nan(c_scale_a),
        "determinism_digest": state_digest(final_state),
    }
    return row

def pearson_or_nan(xs, ys):
    x_vals = []
    y_vals = []
    for x, y in zip(xs, ys):
        try:
            xf = float(x)
            yf = float(y)
        except (TypeError, ValueError):
            continue
        if math.isfinite(xf) and math.isfinite(yf):
            x_vals.append(xf)
            y_vals.append(yf)
    n = len(x_vals)
    if n < 3:
        return float("nan")
    mx = sum(x_vals) / n
    my = sum(y_vals) / n
    cov = sum((x - mx) * (y - my) for x, y in zip(x_vals, y_vals))
    vx = sum((x - mx) * (x - mx) for x in x_vals)
    vy = sum((y - my) * (y - my) for y in y_vals)
    if vx <= 0.0 or vy <= 0.0:
        return float("nan")
    return cov / math.sqrt(vx * vy)


def main():
    base_settings, archetypes = load_inputs()
    missing = [opponent_id for opponent_id in OPPONENT_IDS if opponent_id not in archetypes]
    if missing:
        raise KeyError(f"Missing canonical opponents: {missing}")

    run_rows = []
    for opponent_id in OPPONENT_IDS:
        for odw in ODW_LEVELS:
            for k in K_LEVELS:
                row = run_single_case(base_settings, archetypes, opponent_id, odw, k)
                run_rows.append(row)
                print(
                    f"[odw-doe] opponent={opponent_id} ODW={odw} k={k:.2f} "
                    f"contact={row['first_contact_tick']} cut={row['cut_tick']} pocket={row['pocket_tick']}"
                )

    baseline_lookup = {
        (row["opponent_archetype_id"], int(row["side_a_odw"])): row
        for row in run_rows
        if abs(float(row["odw_posture_bias_k_effective"])) <= 1e-12
    }
    delta_rows = []
    for row in run_rows:
        if abs(float(row["odw_posture_bias_k_effective"])) <= 1e-12:
            continue
        key = (row["opponent_archetype_id"], int(row["side_a_odw"]))
        base_row = baseline_lookup[key]
        delta_rows.append(
            {
                "run_id": row["run_id"],
                "opponent_archetype_id": row["opponent_archetype_id"],
                "side_a_odw": row["side_a_odw"],
                "odw_posture_bias_k_effective": row["odw_posture_bias_k_effective"],
                "delta_first_contact_tick": ((row["first_contact_tick"] - base_row["first_contact_tick"]) if row["first_contact_tick"] is not None and base_row["first_contact_tick"] is not None else None),
                "delta_cut_tick": ((row["cut_tick"] - base_row["cut_tick"]) if row["cut_tick"] is not None and base_row["cut_tick"] is not None else None),
                "delta_pocket_tick": ((row["pocket_tick"] - base_row["pocket_tick"]) if row["pocket_tick"] is not None and base_row["pocket_tick"] is not None else None),
                "delta_first_deep_pursuit_tick_A": ((row["first_deep_pursuit_tick_A"] - base_row["first_deep_pursuit_tick_A"]) if row["first_deep_pursuit_tick_A"] is not None and base_row["first_deep_pursuit_tick_A"] is not None else None),
                "delta_precontact_ar_forward_p90_A": row["precontact_ar_forward_p90_A"] - base_row["precontact_ar_forward_p90_A"],
                "delta_precontact_wedge_ratio_p10_A": row["precontact_wedge_ratio_p10_A"] - base_row["precontact_wedge_ratio_p10_A"],
                "delta_precontact_split_separation_p90_A": row["precontact_split_separation_p90_A"] - base_row["precontact_split_separation_p90_A"],
                "delta_precontact_net_axis_push_mean": row["precontact_net_axis_push_mean"] - base_row["precontact_net_axis_push_mean"],
                "delta_precontact_net_axis_push_abs_p90": row["precontact_net_axis_push_abs_p90"] - base_row["precontact_net_axis_push_abs_p90"],
                "delta_mean_enemy_collapse_signal_A": row["mean_enemy_collapse_signal_A"] - base_row["mean_enemy_collapse_signal_A"],
                "delta_pct_ticks_deep_pursuit_A": row["pct_ticks_deep_pursuit_A"] - base_row["pct_ticks_deep_pursuit_A"],
            }
        )

    summary_by_k = []
    for k in K_LEVELS:
        bucket = [row for row in run_rows if abs(float(row["odw_posture_bias_k_effective"]) - float(k)) <= 1e-12]
        summary_by_k.append(
            {
                "odw_posture_bias_k_effective": k,
                "run_count": len(bucket),
                "first_contact_tick_mean": mean_or_nan([row["first_contact_tick"] for row in bucket]),
                "cut_tick_mean": mean_or_nan([row["cut_tick"] for row in bucket]),
                "pocket_tick_mean": mean_or_nan([row["pocket_tick"] for row in bucket]),
                "first_deep_pursuit_tick_A_mean": mean_or_nan([row["first_deep_pursuit_tick_A"] for row in bucket]),
                "pct_ticks_deep_pursuit_A_mean": mean_or_nan([row["pct_ticks_deep_pursuit_A"] for row in bucket]),
                "mean_enemy_collapse_signal_A_mean": mean_or_nan([row["mean_enemy_collapse_signal_A"] for row in bucket]),
                "precontact_ar_forward_p90_A_mean": mean_or_nan([row["precontact_ar_forward_p90_A"] for row in bucket]),
                "precontact_wedge_ratio_p10_A_mean": mean_or_nan([row["precontact_wedge_ratio_p10_A"] for row in bucket]),
                "precontact_split_separation_p90_A_mean": mean_or_nan([row["precontact_split_separation_p90_A"] for row in bucket]),
                "precontact_net_axis_push_abs_p90_mean": mean_or_nan([row["precontact_net_axis_push_abs_p90"] for row in bucket]),
                "event_order_anomaly_rate": mean_or_nan([1.0 if row["event_order_anomaly"] else 0.0 for row in bucket]),
            }
        )

    summary_by_odw = []
    for odw in ODW_LEVELS:
        bucket = [row for row in run_rows if int(row["side_a_odw"]) == int(odw)]
        summary_by_odw.append(
            {
                "side_a_odw": odw,
                "run_count": len(bucket),
                "first_contact_tick_mean": mean_or_nan([row["first_contact_tick"] for row in bucket]),
                "cut_tick_mean": mean_or_nan([row["cut_tick"] for row in bucket]),
                "pocket_tick_mean": mean_or_nan([row["pocket_tick"] for row in bucket]),
                "first_deep_pursuit_tick_A_mean": mean_or_nan([row["first_deep_pursuit_tick_A"] for row in bucket]),
                "pct_ticks_deep_pursuit_A_mean": mean_or_nan([row["pct_ticks_deep_pursuit_A"] for row in bucket]),
                "mean_enemy_collapse_signal_A_mean": mean_or_nan([row["mean_enemy_collapse_signal_A"] for row in bucket]),
                "precontact_ar_forward_p90_A_mean": mean_or_nan([row["precontact_ar_forward_p90_A"] for row in bucket]),
                "precontact_wedge_ratio_p10_A_mean": mean_or_nan([row["precontact_wedge_ratio_p10_A"] for row in bucket]),
                "precontact_split_separation_p90_A_mean": mean_or_nan([row["precontact_split_separation_p90_A"] for row in bucket]),
                "precontact_net_axis_push_abs_p90_mean": mean_or_nan([row["precontact_net_axis_push_abs_p90"] for row in bucket]),
            }
        )

    summary_by_opponent = []
    for opponent_id in OPPONENT_IDS:
        bucket = [row for row in run_rows if row["opponent_archetype_id"] == opponent_id]
        summary_by_opponent.append(
            {
                "opponent_archetype_id": opponent_id,
                "run_count": len(bucket),
                "first_contact_tick_mean": mean_or_nan([row["first_contact_tick"] for row in bucket]),
                "first_deep_pursuit_tick_A_mean": mean_or_nan([row["first_deep_pursuit_tick_A"] for row in bucket]),
                "precontact_ar_forward_p90_A_mean": mean_or_nan([row["precontact_ar_forward_p90_A"] for row in bucket]),
                "precontact_wedge_ratio_p10_A_mean": mean_or_nan([row["precontact_wedge_ratio_p10_A"] for row in bucket]),
                "precontact_net_axis_push_abs_p90_mean": mean_or_nan([row["precontact_net_axis_push_abs_p90"] for row in bucket]),
                "event_order_anomaly_rate": mean_or_nan([1.0 if row["event_order_anomaly"] else 0.0 for row in bucket]),
            }
        )

    relation_summary = [
        {
            "metric_x": "precontact_net_axis_push_abs_p90",
            "metric_y": "precontact_ar_forward_p90_A",
            "pearson_r": pearson_or_nan([row["precontact_net_axis_push_abs_p90"] for row in run_rows], [row["precontact_ar_forward_p90_A"] for row in run_rows]),
        },
        {
            "metric_x": "precontact_net_axis_push_abs_p90",
            "metric_y": "precontact_wedge_ratio_p10_A",
            "pearson_r": pearson_or_nan([row["precontact_net_axis_push_abs_p90"] for row in run_rows], [row["precontact_wedge_ratio_p10_A"] for row in run_rows]),
        },
        {
            "metric_x": "precontact_net_axis_push_abs_p90",
            "metric_y": "first_deep_pursuit_tick_A",
            "pearson_r": pearson_or_nan([row["precontact_net_axis_push_abs_p90"] for row in run_rows], [row["first_deep_pursuit_tick_A"] for row in run_rows]),
        },
        {
            "metric_x": "precontact_net_axis_push_abs_p90",
            "metric_y": "mean_enemy_collapse_signal_A",
            "pearson_r": pearson_or_nan([row["precontact_net_axis_push_abs_p90"] for row in run_rows], [row["mean_enemy_collapse_signal_A"] for row in run_rows]),
        },
    ]

    write_csv(OUT_DIR / "odw_posture_doe_run_table.csv", run_rows)
    write_csv(OUT_DIR / "odw_posture_doe_delta_from_k0.csv", delta_rows)
    write_csv(OUT_DIR / "odw_posture_doe_summary_by_k.csv", summary_by_k)
    write_csv(OUT_DIR / "odw_posture_doe_summary_by_odw.csv", summary_by_odw)
    write_csv(OUT_DIR / "odw_posture_doe_summary_by_opponent.csv", summary_by_opponent)
    write_csv(OUT_DIR / "odw_posture_doe_relation_summary.csv", relation_summary)

    anomaly_count = sum(1 for row in run_rows if row["event_order_anomaly"])
    pocket_before_cut_count = sum(1 for row in run_rows if row["event_order_anomaly_label"] == "pocket_before_cut")
    baseline_bucket = [row for row in run_rows if abs(float(row["odw_posture_bias_k_effective"])) <= 1e-12]
    strongest_bucket = [row for row in run_rows if abs(float(row["odw_posture_bias_k_effective"]) - 1.0) <= 1e-12]

    report_lines = [
        "# ODW Posture DOE Report",
        "",
        "Status: engineering exploratory DOE",
        "Scope: bounded ODW posture-bias prototype only",
        "",
        "## Batch",
        "",
        f"- Runs: `{len(run_rows)}`",
        f"- Side-A ODW levels: `{ODW_LEVELS}`",
        f"- Prototype gains k: `{K_LEVELS}`",
        f"- Opponents: `{', '.join(OPPONENT_IDS)}`",
        f"- Seed policy: single fixed seed `{FIXED_SEED_PROFILE['seed_profile_id']}` (deterministic path; no metatype sampling)",
        "",
        "## Frozen Context",
        "",
        "- movement baseline = `v3a`",
        "- movement_v3a_experiment = `exp_precontact_centroid_probe`",
        "- centroid_probe_scale = `0.5`",
        "- runtime collapse signal source baseline = `v3_test @ 1.1`",
        "- physical spacing / boundary / combat / targeting unchanged from active test-run baseline",
        "",
        "## Key Readout",
        "",
        f"- Event-order anomaly count: `{anomaly_count}`",
        f"- `pocket_before_cut` count: `{pocket_before_cut_count}`",
        f"- Baseline (`k=0`) precontact `NetAxisPush abs p90` mean: `{mean_or_nan([row['precontact_net_axis_push_abs_p90'] for row in baseline_bucket]):.4f}`",
        f"- Strongest (`k=1.0`) precontact `NetAxisPush abs p90` mean: `{mean_or_nan([row['precontact_net_axis_push_abs_p90'] for row in strongest_bucket]):.4f}`",
        f"- Baseline (`k=0`) precontact `AR_forward p90` mean: `{mean_or_nan([row['precontact_ar_forward_p90_A'] for row in baseline_bucket]):.4f}`",
        f"- Strongest (`k=1.0`) precontact `AR_forward p90` mean: `{mean_or_nan([row['precontact_ar_forward_p90_A'] for row in strongest_bucket]):.4f}`",
        f"- Baseline (`k=0`) precontact `WedgeRatio p10` mean: `{mean_or_nan([row['precontact_wedge_ratio_p10_A'] for row in baseline_bucket]):.4f}`",
        f"- Strongest (`k=1.0`) precontact `WedgeRatio p10` mean: `{mean_or_nan([row['precontact_wedge_ratio_p10_A'] for row in strongest_bucket]):.4f}`",
        "",
        "## Relation Hints",
        "",
    ]
    for rel in relation_summary:
        report_lines.append(f"- `{rel['metric_x']}` vs `{rel['metric_y']}` Pearson r: `{rel['pearson_r']:.4f}`")

    report_lines.extend(
        [
            "",
            "## Engineering Reading",
            "",
            "- This batch is large enough to expose whether ODW posture bias produces stable geometry/topology shifts across multiple canonical opponents without opening new mechanism layers.",
            "- `NetAxisPush` is included as a supporting indicator only. It can suggest relative axial pressure asymmetry, but it is not ODW-specific and must not be read as direct shape meaning.",
            "- The main question is whether higher `k` and different `ODW` levels produce interpretable movement/topology differences while keeping event integrity acceptable.",
            "",
            "## Files",
            "",
            "- `odw_posture_doe_run_table.csv`",
            "- `odw_posture_doe_delta_from_k0.csv`",
            "- `odw_posture_doe_summary_by_k.csv`",
            "- `odw_posture_doe_summary_by_odw.csv`",
            "- `odw_posture_doe_summary_by_opponent.csv`",
            "- `odw_posture_doe_relation_summary.csv`",
        ]
    )
    (OUT_DIR / "odw_posture_doe_report.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
