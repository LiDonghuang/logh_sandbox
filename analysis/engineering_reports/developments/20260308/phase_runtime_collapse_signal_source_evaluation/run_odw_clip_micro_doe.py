"""
Small ODW clip-delta micro DOE.

Scope:
- fixed ODW prototype gain k
- controlled neutral Side B
- vary only Side A ODW and clip delta
"""

import csv
import importlib.util
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
TEST_RUN_SRC = ROOT / "test_run" / "test_run_v1_0.py"
BRF_BUILDER_SRC = ROOT / "test_run" / "battle_report_builder.py"
SETTINGS_PATH = ROOT / "test_run" / "test_run_v1_0.settings.json"
OUT_DIR = Path(__file__).resolve().parent

ODW_LEVELS = [2.0, 8.0]
CLIP_DELTAS = [0.2, 0.4, 0.6, 0.8, 1.0]
FIXED_RANDOM_SEED = 1981813971
FIXED_METATYPE_SEED = 3095987153
FIXED_BACKGROUND_MAP_SEED = 897304369


def load_module(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


test_run = load_module(TEST_RUN_SRC, "test_run_odw_clip_module")
brf_builder = load_module(BRF_BUILDER_SRC, "battle_report_builder_odw_clip_module")


def write_csv(path: Path, rows: list[dict]) -> None:
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


def quantile_or_nan(values, q: float):
    vals = sorted(finite(values))
    if not vals:
        return float("nan")
    if q <= 0.0:
        return vals[0]
    if q >= 1.0:
        return vals[-1]
    pos = (len(vals) - 1) * q
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return vals[lo]
    frac = pos - lo
    return vals[lo] * (1.0 - frac) + vals[hi] * frac


def mean_or_nan(values):
    vals = finite(values)
    if not vals:
        return float("nan")
    return sum(vals) / float(len(vals))


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


def precontact_slice(series, first_contact_tick, focus_end_tick=100):
    vals = list(series) if series is not None else []
    if not vals:
        return []
    stop_idx = len(vals)
    if first_contact_tick is not None:
        stop_idx = min(stop_idx, max(0, int(first_contact_tick) - 1))
    stop_idx = min(stop_idx, max(0, int(focus_end_tick)))
    return vals[:stop_idx]


def first_positive_tick(values):
    for idx, value in enumerate(values, start=1):
        try:
            if float(value) > 0.0:
                return idx
        except (TypeError, ValueError):
            continue
    return None


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
        for idx in range(n_ticks):
            enemy_cohesion = enemy_series[idx] if idx < len(enemy_series) else (enemy_series[-1] if enemy_series else 1.0)
            signal = 1.0 - float(enemy_cohesion)
            if signal < 0.0:
                signal = 0.0
            elif signal > 1.0:
                signal = 1.0
            enemy_collapse_signal.append(signal)
            deep_pursuit_flags.append(signal > threshold)
        result[f"first_deep_pursuit_tick_{side}"] = first_positive_tick([1.0 if flag else 0.0 for flag in deep_pursuit_flags])
        result[f"pct_ticks_deep_pursuit_{side}"] = (
            100.0 * sum(1 for flag in deep_pursuit_flags if flag) / float(len(deep_pursuit_flags))
            if deep_pursuit_flags else float("nan")
        )
        result[f"mean_enemy_collapse_signal_{side}"] = mean_or_nan(enemy_collapse_signal)
    return result


def event_flags(first_contact_tick, first_kill_tick, cut_tick, pocket_tick):
    anomaly = False
    label = ""
    if first_kill_tick is not None and first_contact_tick is not None and first_kill_tick < first_contact_tick:
        anomaly = True
        label = "kill_before_contact"
    elif cut_tick is not None and first_contact_tick is not None and cut_tick < first_contact_tick:
        anomaly = True
        label = "cut_before_contact"
    elif cut_tick is not None and first_kill_tick is not None and cut_tick < first_kill_tick:
        anomaly = True
        label = "cut_before_kill"
    elif pocket_tick is not None and cut_tick is not None and pocket_tick < cut_tick:
        anomaly = True
        label = "pocket_before_cut"
    return anomaly, label


def main():
    settings = test_run.load_json_file(SETTINGS_PATH)

    unit_spacing = float(test_run.get_runtime_setting(settings, "min_unit_spacing", 2.0))
    unit_speed = float(test_run.get_unit_setting(settings, "unit_speed", 1.0))
    unit_hp = float(test_run.get_unit_setting(settings, "unit_max_hit_points", 100.0))
    arena_size = float(test_run.get_battlefield_setting(settings, "arena_size", 200.0))
    fleet_size = int(test_run.get_fleet_setting(settings, "initial_fleet_size", 100))
    aspect_ratio = float(test_run.get_fleet_setting(settings, "initial_fleet_aspect_ratio", 2.0))
    attack_range = float(test_run.get_unit_setting(settings, "attack_range", 5.0))
    damage_per_tick = float(test_run.get_unit_setting(settings, "damage_per_tick", 1.0))
    movement_model_effective, _ = test_run.resolve_movement_model(
        test_run.get_runtime_setting(settings, "movement_model", "baseline")
    )
    fire_quality_alpha = float(test_run.get_runtime_setting(settings, "fire_quality_alpha", 0.1))
    contact_hysteresis_h = float(test_run.get_runtime_setting(settings, "contact_hysteresis_h", 0.1))
    fsr_strength = float(test_run.get_runtime_setting(settings, "fsr_strength", 0.1))
    boundary_enabled = bool(test_run.get_runtime_setting(settings, "boundary_enabled", True))
    boundary_hard_enabled = bool(test_run.get_runtime_setting(settings, "boundary_hard_enabled", False))
    boundary_soft_strength = float(test_run.get_runtime_setting(settings, "boundary_soft_strength", 0.1))
    alpha_sep = float(test_run.get_runtime_setting(settings, "alpha_sep", 0.6))
    movement_v3a_experiment = str(test_run.get_runtime_setting(settings, "movement_v3a_experiment", "base"))
    centroid_probe_scale = float(test_run.get_runtime_setting(settings, "centroid_probe_scale", 1.0))
    bridge_theta_split = float(test_run.get_event_bridge_setting(settings, "theta_split", 1.7))
    bridge_theta_env = float(test_run.get_event_bridge_setting(settings, "theta_env", 0.5))
    bridge_sustain_ticks = int(test_run.get_event_bridge_setting(settings, "sustain_ticks", 20))
    collapse_shadow_theta_conn_default = float(test_run.get_collapse_shadow_setting(settings, "theta_conn_default", 0.1))
    collapse_shadow_theta_coh_default = float(test_run.get_collapse_shadow_setting(settings, "theta_coh_default", 0.98))
    collapse_shadow_theta_force_default = float(test_run.get_collapse_shadow_setting(settings, "theta_force_default", 0.95))
    collapse_shadow_theta_attr_default = float(test_run.get_collapse_shadow_setting(settings, "theta_attr_default", 0.1))
    collapse_shadow_attrition_window = int(test_run.get_collapse_shadow_setting(settings, "attrition_window", 20))
    collapse_shadow_sustain_ticks = int(test_run.get_collapse_shadow_setting(settings, "sustain_ticks", 10))
    collapse_shadow_min_conditions = int(test_run.get_collapse_shadow_setting(settings, "min_conditions", 2))

    fixed_k = float(test_run.get_runtime_setting(settings, "odw_posture_bias_k", 0.5))
    fixed_v3_connect = float(test_run.get_runtime_setting(settings, "v3_connect_radius_multiplier", 1.1))
    fixed_v3_r_ref = float(test_run.get_runtime_setting(settings, "v3_r_ref_radius_multiplier", 1.0))

    def make_params(odw: float, archetype_id: str):
        return test_run.PersonalityParameters(
            archetype_id=archetype_id,
            force_concentration_ratio=5.0,
            mobility_bias=5.0,
            offense_defense_weight=float(odw),
            risk_appetite=5.0,
            time_preference=5.0,
            targeting_logic=5.0,
            formation_rigidity=5.0,
            perception_radius=5.0,
            pursuit_drive=5.0,
            retreat_threshold=5.0,
        )

    neutral_b = make_params(5.0, "odw_clip_neutral_b")
    rows = []

    for odw in ODW_LEVELS:
        for clip_delta in CLIP_DELTAS:
            state = test_run.build_initial_state(
                fleet_a_params=make_params(odw, f"odw_clip_a_{int(odw)}"),
                fleet_b_params=neutral_b,
                fleet_size=fleet_size,
                aspect_ratio=aspect_ratio,
                unit_spacing=unit_spacing,
                unit_speed=unit_speed,
                unit_max_hit_points=unit_hp,
                arena_size=arena_size,
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
                _frames,
            ) = test_run.run_simulation(
                initial_state=state,
                steps=-1,
                capture_positions=False,
                observer_enabled=True,
                runtime_decision_source="v3_test",
                movement_model=movement_model_effective,
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
                ch_enabled=contact_hysteresis_h > 0.0,
                fsr_enabled=fsr_strength > 0.0,
                fsr_strength=fsr_strength,
                boundary_enabled=boundary_enabled,
                boundary_hard_enabled=boundary_hard_enabled,
                boundary_soft_strength=boundary_soft_strength,
                alpha_sep=alpha_sep,
                include_target_lines=False,
                print_tick_summary=False,
                plot_diagnostics_enabled=False,
                movement_v3a_experiment=movement_v3a_experiment,
                centroid_probe_scale=centroid_probe_scale,
                odw_posture_bias_enabled=True,
                odw_posture_bias_k=fixed_k,
                odw_posture_bias_clip_delta=clip_delta,
                v3_connect_radius_multiplier=fixed_v3_connect,
                v3_r_ref_radius_multiplier=fixed_v3_r_ref,
            )

            event_ticks = brf_builder.compute_bridge_event_ticks(bridge_telemetry)
            first_contact_tick = brf_builder.first_tick_true(combat_telemetry.get("in_contact_count", []), lambda v: int(v) > 0)
            first_kill_tick = first_kill_tick_from_alive(
                alive_trajectory.get("A", []),
                alive_trajectory.get("B", []),
            )
            cut_tick = parse_tick(event_ticks.get("tactical_cut_tick_T"))
            pocket_tick = parse_tick(event_ticks.get("tactical_pocket_tick_T"))
            anomaly, anomaly_label = event_flags(first_contact_tick, first_kill_tick, cut_tick, pocket_tick)

            pre_ar_a = precontact_slice(bridge_telemetry["AR"].get("A", []), first_contact_tick)
            pre_wedge_a = precontact_slice(bridge_telemetry["wedge_ratio"].get("A", []), first_contact_tick)
            pre_split_a = precontact_slice(bridge_telemetry["split_separation"].get("A", []), first_contact_tick)
            pre_gap_a = precontact_slice(observer_telemetry["center_wing_advance_gap"].get("A", []), first_contact_tick)

            runtime_metrics = compute_runtime_signal_metrics(trajectory, 5.0, 5.0)

            rows.append(
                {
                    "odw_a": odw,
                    "odw_b": 5.0,
                    "odw_posture_bias_k": fixed_k,
                    "odw_posture_bias_clip_delta": clip_delta,
                    "random_seed_effective": FIXED_RANDOM_SEED,
                    "background_map_seed_effective": FIXED_BACKGROUND_MAP_SEED,
                    "metatype_random_seed_effective": FIXED_METATYPE_SEED,
                    "first_contact_tick": first_contact_tick,
                    "first_kill_tick": first_kill_tick,
                    "cut_tick": cut_tick,
                    "pocket_tick": pocket_tick,
                    "event_order_anomaly": int(anomaly),
                    "event_order_anomaly_label": anomaly_label,
                    "first_deep_pursuit_tick_A": runtime_metrics.get("first_deep_pursuit_tick_A"),
                    "pct_ticks_deep_pursuit_A": runtime_metrics.get("pct_ticks_deep_pursuit_A"),
                    "mean_enemy_collapse_signal_A": runtime_metrics.get("mean_enemy_collapse_signal_A"),
                    "precontact_ar_forward_p90_A": quantile_or_nan(pre_ar_a, 0.9),
                    "precontact_wedge_ratio_p10_A": quantile_or_nan(pre_wedge_a, 0.1),
                    "precontact_split_separation_p90_A": quantile_or_nan(pre_split_a, 0.9),
                    "precontact_center_wing_gap_abs_p90_A": quantile_or_nan([abs(float(v)) for v in pre_gap_a if math.isfinite(float(v))], 0.9),
                    "precontact_center_wing_gap_mean_A": mean_or_nan(pre_gap_a),
                    "end_tick": int(final_state.tick),
                }
            )

    write_csv(OUT_DIR / "odw_clip_micro_doe_results.csv", rows)

    def rows_for(odw):
        return [row for row in rows if float(row["odw_a"]) == float(odw)]

    lines = [
        "# ODW Clip Micro DOE Summary",
        "",
        "Scope:",
        "- controlled neutral Side B (all parameters fixed at 5)",
        "- Side A varies only `ODW in {2, 8}`",
        f"- fixed `odw_posture_bias_k = {fixed_k}`",
        "- vary only `odw_posture_bias_clip_delta in {0.2, 0.4, 0.6, 0.8, 1.0}`",
        "",
        "## Table",
        "",
        "| ODW_A | ClipDelta | first_deep_pursuit_A | pct_deep_pursuit_A | mean_enemy_collapse_signal_A | AR_p90_A | Wedge_p10_A | CenterWingGapAbs_p90_A | anomaly |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {int(row['odw_a'])} | {row['odw_posture_bias_clip_delta']:.1f} | "
            f"{row['first_deep_pursuit_tick_A']} | {float(row['pct_ticks_deep_pursuit_A']):.2f} | "
            f"{float(row['mean_enemy_collapse_signal_A']):.4f} | {float(row['precontact_ar_forward_p90_A']):.4f} | "
            f"{float(row['precontact_wedge_ratio_p10_A']):.4f} | {float(row['precontact_center_wing_gap_abs_p90_A']):.4f} | "
            f"{row['event_order_anomaly_label'] or 'none'} |"
        )
    (OUT_DIR / "odw_clip_micro_doe_summary.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
