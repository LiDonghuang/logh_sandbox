#!/usr/bin/env python3
from __future__ import annotations

import copy
import csv
import hashlib
import importlib.util
import json
import math
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
TEST_RUN_SRC = ROOT / "test_run" / "test_run_v1_0.py"
BRF_BUILDER_SRC = ROOT / "test_run" / "battle_report_builder.py"
SETTINGS_PATH = ROOT / "test_run" / "test_run_v1_0.settings.json"
OUT_DIR = Path(__file__).resolve().parent
DOE_POSTPROCESS = ROOT / "analysis" / "engineering_reports" / "_standards" / "doe_postprocess.py"

FR_LEVELS = [2, 5, 8]
MB_LEVELS = [2, 5, 8]
PD_LEVELS = [2, 5, 8]
ODW_LEVELS = [2, 8]
SEED_ROOTS = list(range(1001, 1019))
BASELINE_OPPONENT_ID = "controlled_baseline_B"
TITLE = "FR Authority DOE Summary - Controlled Isolation Baseline"


def load_module(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


test_run = load_module(TEST_RUN_SRC, "test_run_fr_audit_module")
brf_builder = load_module(BRF_BUILDER_SRC, "battle_report_builder_fr_audit_module")


def load_json_file(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_csv(path: Path, rows: list[dict]):
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
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


def median_or_nan(values):
    vals = sorted(finite(values))
    if not vals:
        return float("nan")
    n = len(vals)
    mid = n // 2
    if n % 2 == 1:
        return vals[mid]
    return 0.5 * (vals[mid - 1] + vals[mid])


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


def parse_tick(value):
    if value in (None, "", "N/A"):
        return None
    try:
        iv = int(value)
    except (TypeError, ValueError):
        return None
    return iv if iv >= 1 else None


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


def derive_seed(root: int, label: str) -> int:
    payload = f"{int(root)}:{label}".encode("utf-8")
    digest = hashlib.sha256(payload).digest()
    return int.from_bytes(digest[:4], byteorder="big", signed=False) % (2**31 - 1)


def build_seed_profiles():
    profiles = []
    for idx, root_seed in enumerate(SEED_ROOTS, start=1):
        profiles.append(
            {
                "seed_profile_id": f"SP{idx:02d}",
                "seed_root": int(root_seed),
                "random_seed_effective": derive_seed(root_seed, "random_seed"),
                "background_map_seed_effective": derive_seed(root_seed, "background_map_seed"),
                "metatype_random_seed_effective": derive_seed(root_seed, "metatype_random_seed"),
            }
        )
    return profiles


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


def build_variable_vector(fr: float, mb: float, pd: float, odw: float) -> dict:
    return {
        "force_concentration_ratio": 5.0,
        "mobility_bias": float(mb),
        "offense_defense_weight": float(odw),
        "risk_appetite": 5.0,
        "time_preference": 5.0,
        "targeting_logic": 5.0,
        "formation_rigidity": float(fr),
        "perception_radius": 5.0,
        "pursuit_drive": float(pd),
        "retreat_threshold": 5.0,
    }


def build_baseline_opponent_vector() -> dict:
    return {
        "force_concentration_ratio": 5.0,
        "mobility_bias": 2.0,
        "offense_defense_weight": 8.0,
        "risk_appetite": 5.0,
        "time_preference": 5.0,
        "targeting_logic": 5.0,
        "formation_rigidity": 2.0,
        "perception_radius": 5.0,
        "pursuit_drive": 2.0,
        "retreat_threshold": 5.0,
    }


def load_inputs():
    return load_json_file(SETTINGS_PATH)


def build_run_settings(base_settings: dict, seed_profile: dict) -> dict:
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
    movement["experiment"] = str(movement.get("experiment", "exp_precontact_centroid_probe"))
    movement["centroid_probe_scale"] = float(movement.get("centroid_probe_scale", 0.5))
    movement["odw_posture_bias_enabled"] = bool(movement.get("odw_posture_bias_enabled", True))
    movement["odw_posture_bias_k"] = float(movement.get("odw_posture_bias_k", 0.5))
    movement["odw_posture_bias_clip_delta"] = float(movement.get("odw_posture_bias_clip_delta", 0.4))
    semantics["v3_connect_radius_multiplier"] = float(semantics.get("v3_connect_radius_multiplier", 1.1))
    semantics["v3_r_ref_radius_multiplier"] = float(semantics.get("v3_r_ref_radius_multiplier", 1.0))

    run_control["animate"] = False
    run_control["test_mode"] = 2
    run_control["display_language"] = "ZH"
    run_control["random_seed"] = int(seed_profile["random_seed_effective"])
    run_control["metatype_random_seed"] = int(seed_profile["metatype_random_seed_effective"])
    settings.setdefault("battlefield", {})["background_map_seed"] = int(seed_profile["background_map_seed_effective"])

    visualization["print_tick_summary"] = False
    export_video["enabled"] = False
    return settings


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
            "pct_ticks_deep_pursuit": (
                (100.0 * sum(1 for flag in deep_pursuit_flags if flag) / float(len(deep_pursuit_flags)))
                if deep_pursuit_flags
                else float("nan")
            ),
            "mean_pursuit_intensity": mean_or_nan(pursuit_intensity_values),
            "mean_enemy_collapse_signal": mean_or_nan(enemy_collapse_signal),
            "p95_enemy_collapse_signal": quantile_or_nan(enemy_collapse_signal, 0.95),
        }
    return result


def compute_alive_metrics(alive_trajectory: dict[str, list[int]], divergence_threshold: int = 5) -> dict[str, Any]:
    alive_a = [int(v) for v in alive_trajectory.get("A", [])]
    alive_b = [int(v) for v in alive_trajectory.get("B", [])]
    n = max(len(alive_a), len(alive_b))
    lead = []
    for idx in range(n):
        a = alive_a[idx] if idx < len(alive_a) else (alive_a[-1] if alive_a else 0)
        b = alive_b[idx] if idx < len(alive_b) else (alive_b[-1] if alive_b else 0)
        lead.append(int(a) - int(b))

    first_lead_tick = None
    first_lead_side = "N/A"
    first_major_divergence_tick = None
    first_major_divergence_side = "N/A"
    first_lead_change_tick = None
    first_lead_sign = 0

    for idx, value in enumerate(lead, start=1):
        sign = 1 if value > 0 else (-1 if value < 0 else 0)
        if first_lead_tick is None and sign != 0:
            first_lead_tick = idx
            first_lead_side = "A" if sign > 0 else "B"
            first_lead_sign = sign
        if first_major_divergence_tick is None and abs(value) >= int(divergence_threshold):
            first_major_divergence_tick = idx
            first_major_divergence_side = "A" if value > 0 else ("B" if value < 0 else "N/A")
        if first_lead_tick is not None and first_lead_change_tick is None and sign != 0 and sign != first_lead_sign:
            first_lead_change_tick = idx

    max_alive_lead_a = max([v for v in lead if v > 0], default=0)
    max_alive_lead_b = max([-v for v in lead if v < 0], default=0)

    return {
        "first_alive_lead_tick": first_lead_tick,
        "first_alive_lead_side": first_lead_side,
        "first_alive_lead_change_tick": first_lead_change_tick,
        "first_major_divergence_tick": first_major_divergence_tick,
        "first_major_divergence_side": first_major_divergence_side,
        "max_alive_lead_A": int(max_alive_lead_a),
        "max_alive_lead_B": int(max_alive_lead_b),
    }


def build_alive_rows(run_id: str, alive_trajectory: dict[str, list[int]]) -> list[dict]:
    alive_a = [int(v) for v in alive_trajectory.get("A", [])]
    alive_b = [int(v) for v in alive_trajectory.get("B", [])]
    n = max(len(alive_a), len(alive_b))
    rows = []
    for idx in range(n):
        a = alive_a[idx] if idx < len(alive_a) else (alive_a[-1] if alive_a else 0)
        b = alive_b[idx] if idx < len(alive_b) else (alive_b[-1] if alive_b else 0)
        rows.append(
            {
                "run_id": run_id,
                "tick": idx + 1,
                "alive_A": int(a),
                "alive_B": int(b),
                "alive_lead_A_minus_B": int(a) - int(b),
            }
        )
    return rows


def contact_proxy_metrics(combat_telemetry: dict) -> dict[str, float]:
    in_contact = [int(v) for v in combat_telemetry.get("in_contact_count", [])]
    damage_events = [int(v) for v in combat_telemetry.get("damage_events_count", [])]
    contact_pairs = [v for v in in_contact if v > 0]
    contact_damage = [
        damage_events[idx]
        for idx in range(min(len(in_contact), len(damage_events)))
        if in_contact[idx] > 0
    ]
    sum_contact_pairs = sum(contact_pairs)
    sum_contact_damage = sum(contact_damage)
    proxy = (float(sum_contact_damage) / float(sum_contact_pairs)) if sum_contact_pairs > 0 else float("nan")
    return {
        "contact_ticks": sum(1 for v in in_contact if v > 0),
        "mean_in_contact_count_contact_phase": mean_or_nan(contact_pairs),
        "mean_damage_events_count_contact_phase": mean_or_nan(contact_damage),
        "damage_events_per_contact_pair_proxy": proxy,
    }


def winner_from_final(alive_a_final: int, alive_b_final: int) -> str:
    if alive_a_final > alive_b_final:
        return "A"
    if alive_b_final > alive_a_final:
        return "B"
    return "Draw"


def run_single_case(base_settings: dict, seed_profile: dict, fr: int, mb: int, pd: int, odw: int) -> tuple[dict, list[dict]]:
    settings = build_run_settings(base_settings, seed_profile)
    side_a_vector = build_variable_vector(fr=fr, mb=mb, pd=pd, odw=odw)
    opponent_vector = build_baseline_opponent_vector()
    opponent_data = vector_to_archetype(BASELINE_OPPONENT_ID, opponent_vector)

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
    continuous_fr_shaping_enabled = bool(test_run.get_runtime_setting(settings, "continuous_fr_shaping_enabled", False))
    continuous_fr_shaping_mode = str(
        test_run.get_runtime_setting(settings, "continuous_fr_shaping_mode", test_run.CONTINUOUS_FR_SHAPING_OFF)
    ).strip().lower()
    if continuous_fr_shaping_mode not in test_run.CONTINUOUS_FR_SHAPING_LABELS:
        continuous_fr_shaping_mode = test_run.CONTINUOUS_FR_SHAPING_OFF
    continuous_fr_shaping_a = max(0.0, float(test_run.get_runtime_setting(settings, "continuous_fr_shaping_a", 0.0)))
    continuous_fr_shaping_sigma = max(
        1e-6, float(test_run.get_runtime_setting(settings, "continuous_fr_shaping_sigma", 0.15))
    )
    continuous_fr_shaping_p = max(0.0, float(test_run.get_runtime_setting(settings, "continuous_fr_shaping_p", 1.0)))
    continuous_fr_shaping_q = max(0.0, float(test_run.get_runtime_setting(settings, "continuous_fr_shaping_q", 1.0)))
    continuous_fr_shaping_beta = max(0.0, float(test_run.get_runtime_setting(settings, "continuous_fr_shaping_beta", 0.0)))
    continuous_fr_shaping_gamma = max(
        0.0, float(test_run.get_runtime_setting(settings, "continuous_fr_shaping_gamma", 0.0))
    )
    cohesion_source_requested, cohesion_source_effective = test_run.resolve_runtime_decision_source(
        str(test_run.get_runtime_setting(settings, "cohesion_decision_source", "baseline")).strip().lower() or "baseline",
        int(test_run.get_run_control_setting(settings, "test_mode", 2)),
    )
    v3_connect_radius_multiplier = float(test_run.get_runtime_setting(settings, "v3_connect_radius_multiplier", 1.1))
    v3_r_ref_radius_multiplier = float(test_run.get_runtime_setting(settings, "v3_r_ref_radius_multiplier", 1.0))
    odw_enabled = bool(test_run.get_runtime_setting(settings, "odw_posture_bias_enabled", False))
    odw_k = float(test_run.get_runtime_setting(settings, "odw_posture_bias_k", 0.0))
    odw_clip_delta = float(test_run.get_runtime_setting(settings, "odw_posture_bias_clip_delta", 0.2))

    state = test_run.build_initial_state(
        fleet_a_params=test_run.to_personality_parameters(vector_to_archetype(f"fr_probe_FR{fr}_MB{mb}_PD{pd}_ODW{odw}", side_a_vector)),
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
            continuous_fr_shaping_enabled=continuous_fr_shaping_enabled,
            continuous_fr_shaping_mode=continuous_fr_shaping_mode,
            continuous_fr_shaping_a=continuous_fr_shaping_a,
            continuous_fr_shaping_sigma=continuous_fr_shaping_sigma,
            continuous_fr_shaping_p=continuous_fr_shaping_p,
            continuous_fr_shaping_q=continuous_fr_shaping_q,
            continuous_fr_shaping_beta=continuous_fr_shaping_beta,
            continuous_fr_shaping_gamma=continuous_fr_shaping_gamma,
            odw_posture_bias_enabled=odw_enabled,
            odw_posture_bias_k=odw_k,
            odw_posture_bias_clip_delta=odw_clip_delta,
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
        bridge_theta_split=float(
            test_run.get_event_bridge_setting(settings, "theta_split", test_run.BRIDGE_THETA_SPLIT_DEFAULT)
        ),
        bridge_theta_env=float(
            test_run.get_event_bridge_setting(settings, "theta_env", test_run.BRIDGE_THETA_ENV_DEFAULT)
        ),
        bridge_sustain_ticks=int(
            test_run.get_event_bridge_setting(settings, "sustain_ticks", test_run.BRIDGE_SUSTAIN_TICKS_DEFAULT)
        ),
        collapse_shadow_theta_conn_default=float(
            test_run.get_collapse_shadow_setting(
                settings, "theta_conn_default", test_run.COLLAPSE_V2_SHADOW_THETA_CONN_DEFAULT
            )
        ),
        collapse_shadow_theta_coh_default=float(
            test_run.get_collapse_shadow_setting(
                settings, "theta_coh_default", test_run.COLLAPSE_V2_SHADOW_THETA_COH_DEFAULT
            )
        ),
        collapse_shadow_theta_force_default=float(
            test_run.get_collapse_shadow_setting(
                settings, "theta_force_default", test_run.COLLAPSE_V2_SHADOW_THETA_FORCE_DEFAULT
            )
        ),
        collapse_shadow_theta_attr_default=float(
            test_run.get_collapse_shadow_setting(
                settings, "theta_attr_default", test_run.COLLAPSE_V2_SHADOW_THETA_ATTR_DEFAULT
            )
        ),
        collapse_shadow_attrition_window=int(
            test_run.get_collapse_shadow_setting(
                settings, "attrition_window", test_run.COLLAPSE_V2_SHADOW_ATTRITION_WINDOW_DEFAULT
            )
        ),
        collapse_shadow_sustain_ticks=int(
            test_run.get_collapse_shadow_setting(
                settings, "sustain_ticks", test_run.COLLAPSE_V2_SHADOW_SUSTAIN_TICKS_DEFAULT
            )
        ),
        collapse_shadow_min_conditions=int(
            test_run.get_collapse_shadow_setting(
                settings, "min_conditions", test_run.COLLAPSE_V2_SHADOW_MIN_CONDITIONS_DEFAULT
            )
        ),
    )
    (
        final_state,
        trajectory,
        alive_trajectory,
        fleet_size_trajectory,
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

    alive_a_series = [int(v) for v in alive_trajectory.get("A", [])]
    alive_b_series = [int(v) for v in alive_trajectory.get("B", [])]
    size_a_series = [float(v) for v in fleet_size_trajectory.get("A", [])]
    size_b_series = [float(v) for v in fleet_size_trajectory.get("B", [])]

    first_contact_tick = first_positive_tick(combat_telemetry.get("in_contact_count", []))
    first_damage_tick = first_positive_tick(combat_telemetry.get("damage_events_count", []))
    first_kill_tick = first_kill_tick_from_alive(alive_a_series, alive_b_series)
    if first_kill_tick is None:
        first_kill_tick = first_damage_tick

    bridge_ticks = brf_builder.compute_bridge_event_ticks(bridge_telemetry)
    cut_tick = parse_tick(bridge_ticks.get("formation_cut_tick"))
    pocket_tick = parse_tick(bridge_ticks.get("pocket_formation_tick"))
    event_flags = compute_event_flags(first_contact_tick, first_kill_tick, cut_tick, pocket_tick)

    fire_efficiency_series_a, fire_efficiency_series_b = brf_builder._compute_fire_efficiency_series(
        size_a_series,
        size_b_series,
        alive_a_series,
        alive_b_series,
        per_unit_damage=damage_per_tick,
    )
    report_summaries = brf_builder._build_report_summaries(
        observer_telemetry=observer_telemetry,
        bridge_telemetry=bridge_telemetry,
        first_contact_tick=first_contact_tick,
        bridge_ticks=bridge_ticks,
        fire_efficiency_series_a=fire_efficiency_series_a,
        fire_efficiency_series_b=fire_efficiency_series_b,
        formation_cut_tick=cut_tick,
    )
    precontact_geometry_summary = report_summaries["precontact_geometry_summary"]
    runtime_collapse_summary = report_summaries["runtime_collapse_summary"]
    front_profile_quality_summary = report_summaries["front_profile_quality_summary"]

    ar_a = list(bridge_telemetry.get("AR", {}).get("A", []))
    wedge_a = list(bridge_telemetry.get("wedge_ratio", {}).get("A", []))
    split_a = list(bridge_telemetry.get("split_separation", {}).get("A", []))
    pre_ar_a = precontact_focus_slice(ar_a, first_contact_tick)
    pre_wedge_a = precontact_focus_slice(wedge_a, first_contact_tick)
    pre_split_a = precontact_focus_slice(split_a, first_contact_tick)

    c_conn_a = precontact_focus_slice(observer_telemetry.get("c_conn", {}).get("A", []), first_contact_tick)
    rho_a = precontact_focus_slice(observer_telemetry.get("rho", {}).get("A", []), first_contact_tick)
    c_scale_a = precontact_focus_slice(observer_telemetry.get("c_scale", {}).get("A", []), first_contact_tick)

    runtime_signal_metrics = compute_runtime_signal_metrics(
        trajectory,
        pd_a=side_a_vector["pursuit_drive"],
        pd_b=opponent_vector["pursuit_drive"],
    )
    alive_metrics = compute_alive_metrics(alive_trajectory)
    contact_metrics = contact_proxy_metrics(combat_telemetry)

    fleet_a_final = final_state.fleets.get("A")
    fleet_b_final = final_state.fleets.get("B")
    alive_a_final = len(fleet_a_final.unit_ids) if fleet_a_final else 0
    alive_b_final = len(fleet_b_final.unit_ids) if fleet_b_final else 0
    winner = winner_from_final(alive_a_final, alive_b_final)
    run_id = f"{seed_profile['seed_profile_id']}_FR{fr}_MB{mb}_PD{pd}_ODW{odw}"

    row = {
        "run_id": run_id,
        "seed_profile_id": seed_profile["seed_profile_id"],
        "cell_FR": int(fr),
        "cell_MB": int(mb),
        "cell_PD": int(pd),
        "cell_ODW": int(odw),
        "movement_model": movement_model_effective,
        "movement_model_requested": movement_model_requested,
        "movement_model_effective": movement_model_effective,
        "runtime_decision_source_requested": cohesion_source_requested,
        "runtime_decision_source_effective": cohesion_source_effective,
        "movement_v3a_experiment_effective": movement_v3a_experiment if movement_model_effective == "v3a" else "N/A",
        "centroid_probe_scale_effective": centroid_probe_scale if movement_model_effective == "v3a" else "N/A",
        "odw_posture_bias_enabled_effective": odw_enabled if movement_model_effective == "v3a" else "N/A",
        "odw_posture_bias_k_effective": odw_k if movement_model_effective == "v3a" else "N/A",
        "odw_posture_bias_clip_delta_effective": odw_clip_delta if movement_model_effective == "v3a" else "N/A",
        "random_seed_effective": seed_profile["random_seed_effective"],
        "background_map_seed_effective": seed_profile["background_map_seed_effective"],
        "metatype_random_seed_effective": seed_profile["metatype_random_seed_effective"],
        "opponent_archetype_id": BASELINE_OPPONENT_ID,
        "side_a_vector": json.dumps(side_a_vector, sort_keys=True),
        "opponent_vector": json.dumps(opponent_vector, sort_keys=True),
        "winner": winner,
        "end_tick": int(final_state.tick),
        "remaining_units_A": int(alive_a_final),
        "remaining_units_B": int(alive_b_final),
        "first_contact_tick": first_contact_tick,
        "first_kill_tick": first_kill_tick,
        "tactical_cut_tick_T": cut_tick,
        "tactical_pocket_tick_T": pocket_tick,
        "first_damage_tick": first_damage_tick,
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
        "precontact_c_conn_mean_A": mean_or_nan(c_conn_a),
        "precontact_rho_mean_A": mean_or_nan(rho_a),
        "precontact_c_scale_mean_A": mean_or_nan(c_scale_a),
        "front_profile_A": front_profile_quality_summary["A"]["profile"],
        "wedge_present_A": front_profile_quality_summary["A"]["wedge_present"],
        "local_penetration_A": front_profile_quality_summary["A"]["local_penetration"],
        "structural_fragility_A": front_profile_quality_summary["A"]["structural_fragility"],
        "posture_coherence_A": front_profile_quality_summary["A"]["posture_coherence"],
        "fire_eff_contact_to_cut_mean_A": front_profile_quality_summary["A"]["fire_eff_contact_to_cut_mean"],
        "fire_eff_contact_to_cut_p90_A": front_profile_quality_summary["A"]["fire_eff_contact_to_cut_p90"],
        "front_profile_B": front_profile_quality_summary["B"]["profile"],
        "wedge_present_B": front_profile_quality_summary["B"]["wedge_present"],
        "local_penetration_B": front_profile_quality_summary["B"]["local_penetration"],
        "structural_fragility_B": front_profile_quality_summary["B"]["structural_fragility"],
        "posture_coherence_B": front_profile_quality_summary["B"]["posture_coherence"],
        "fire_eff_contact_to_cut_mean_B": front_profile_quality_summary["B"]["fire_eff_contact_to_cut_mean"],
        "fire_eff_contact_to_cut_p90_B": front_profile_quality_summary["B"]["fire_eff_contact_to_cut_p90"],
        "runtime_collapse_sig_mean_A": runtime_collapse_summary["A"]["collapse_sig_mean"],
        "runtime_collapse_sig_p95_A": runtime_collapse_summary["A"]["collapse_sig_p95"],
        "runtime_c_conn_mean_A": runtime_collapse_summary["A"]["c_conn_mean"],
        "runtime_rho_mean_A": runtime_collapse_summary["A"]["rho_mean"],
        "runtime_c_scale_mean_A": runtime_collapse_summary["A"]["c_scale_mean"],
        "runtime_collapse_sig_mean_B": runtime_collapse_summary["B"]["collapse_sig_mean"],
        "runtime_collapse_sig_p95_B": runtime_collapse_summary["B"]["collapse_sig_p95"],
        "runtime_c_conn_mean_B": runtime_collapse_summary["B"]["c_conn_mean"],
        "runtime_rho_mean_B": runtime_collapse_summary["B"]["rho_mean"],
        "runtime_c_scale_mean_B": runtime_collapse_summary["B"]["c_scale_mean"],
        "precontact_wedge_p50_A": precontact_geometry_summary["A"]["wedge_p50"],
        "precontact_frontcurv_p50_A": precontact_geometry_summary["A"]["frontcurv_p50"],
        "precontact_cw_pshare_p50_A": precontact_geometry_summary["A"]["cw_pshare_p50"],
        "precontact_pospersist_max_abs_A": precontact_geometry_summary["A"]["pospersist_max_abs"],
        "first_alive_lead_tick": alive_metrics["first_alive_lead_tick"],
        "first_alive_lead_side": alive_metrics["first_alive_lead_side"],
        "first_alive_lead_change_tick": alive_metrics["first_alive_lead_change_tick"],
        "first_major_divergence_tick": alive_metrics["first_major_divergence_tick"],
        "first_major_divergence_side": alive_metrics["first_major_divergence_side"],
        "max_alive_lead_A": alive_metrics["max_alive_lead_A"],
        "max_alive_lead_B": alive_metrics["max_alive_lead_B"],
        "contact_ticks": contact_metrics["contact_ticks"],
        "mean_in_contact_count_contact_phase": contact_metrics["mean_in_contact_count_contact_phase"],
        "mean_damage_events_count_contact_phase": contact_metrics["mean_damage_events_count_contact_phase"],
        "damage_events_per_contact_pair_proxy": contact_metrics["damage_events_per_contact_pair_proxy"],
        "determinism_digest": state_digest(final_state),
    }

    alive_rows = build_alive_rows(run_id, alive_trajectory)
    for alive_row in alive_rows:
        alive_row["seed_profile_id"] = seed_profile["seed_profile_id"]
        alive_row["cell_FR"] = int(fr)
        alive_row["cell_MB"] = int(mb)
        alive_row["cell_PD"] = int(pd)
        alive_row["cell_ODW"] = int(odw)
        alive_row["winner"] = winner
    return row, alive_rows


def a_win_rate(rows: list[dict]) -> float:
    if not rows:
        return float("nan")
    wins = sum(1 for row in rows if str(row.get("winner", "")).upper() == "A")
    return 100.0 * float(wins) / float(len(rows))


def _is_true_like(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    text = str(value).strip().lower()
    if text in {"true", "1", "yes"}:
        return True
    if text in {"false", "0", "no", "", "n/a", "nan"}:
        return False
    return bool(value)


def _true_rate(rows: list[dict], key: str) -> float:
    if not rows:
        return float("nan")
    hits = sum(1 for row in rows if _is_true_like(row.get(key)))
    return 100.0 * float(hits) / float(len(rows))


def build_odw_split_summary(run_rows: list[dict]) -> list[dict]:
    out = []
    for odw in ODW_LEVELS:
        bucket = [row for row in run_rows if int(row["cell_ODW"]) == int(odw)]
        out.append(
            {
                "cell_ODW": int(odw),
                "n_runs": len(bucket),
                "A_win_rate_pct": a_win_rate(bucket),
                "mean_remaining_units_A": mean_or_nan([row["remaining_units_A"] for row in bucket]),
                "mean_remaining_units_B": mean_or_nan([row["remaining_units_B"] for row in bucket]),
                "median_end_tick": median_or_nan([row["end_tick"] for row in bucket]),
                "mean_first_major_divergence_tick": mean_or_nan([row["first_major_divergence_tick"] for row in bucket]),
                "mean_precontact_ar_forward_p90_A": mean_or_nan([row["precontact_ar_forward_p90_A"] for row in bucket]),
                "mean_precontact_wedge_ratio_p10_A": mean_or_nan([row["precontact_wedge_ratio_p10_A"] for row in bucket]),
                "mean_runtime_c_conn_A": mean_or_nan([row["runtime_c_conn_mean_A"] for row in bucket]),
                "mean_runtime_collapse_sig_A": mean_or_nan([row["runtime_collapse_sig_mean_A"] for row in bucket]),
                "wedge_present_rate_A_pct": _true_rate(bucket, "wedge_present_A"),
                "structural_fragility_rate_A_pct": _true_rate(bucket, "structural_fragility_A"),
                "posture_coherence_rate_A_pct": _true_rate(bucket, "posture_coherence_A"),
                "mean_fire_eff_contact_to_cut_A": mean_or_nan([row["fire_eff_contact_to_cut_mean_A"] for row in bucket]),
            }
        )
    return out


def build_fr_odw_summary(run_rows: list[dict]) -> list[dict]:
    out = []
    for fr in FR_LEVELS:
        for odw in ODW_LEVELS:
            bucket = [
                row
                for row in run_rows
                if int(row["cell_FR"]) == int(fr) and int(row["cell_ODW"]) == int(odw)
            ]
            out.append(
                {
                    "cell_FR": int(fr),
                    "cell_ODW": int(odw),
                    "n_runs": len(bucket),
                    "A_win_rate_pct": a_win_rate(bucket),
                    "mean_remaining_units_A": mean_or_nan([row["remaining_units_A"] for row in bucket]),
                    "mean_remaining_units_B": mean_or_nan([row["remaining_units_B"] for row in bucket]),
                    "median_end_tick": median_or_nan([row["end_tick"] for row in bucket]),
                    "mean_first_alive_lead_tick": mean_or_nan([row["first_alive_lead_tick"] for row in bucket]),
                    "mean_first_major_divergence_tick": mean_or_nan([row["first_major_divergence_tick"] for row in bucket]),
                    "mean_precontact_ar_forward_p90_A": mean_or_nan([row["precontact_ar_forward_p90_A"] for row in bucket]),
                    "mean_precontact_wedge_ratio_p10_A": mean_or_nan([row["precontact_wedge_ratio_p10_A"] for row in bucket]),
                    "mean_runtime_c_conn_A": mean_or_nan([row["runtime_c_conn_mean_A"] for row in bucket]),
                    "mean_runtime_collapse_sig_A": mean_or_nan([row["runtime_collapse_sig_mean_A"] for row in bucket]),
                    "wedge_present_rate_A_pct": _true_rate(bucket, "wedge_present_A"),
                    "structural_fragility_rate_A_pct": _true_rate(bucket, "structural_fragility_A"),
                    "posture_coherence_rate_A_pct": _true_rate(bucket, "posture_coherence_A"),
                    "mean_fire_eff_contact_to_cut_A": mean_or_nan([row["fire_eff_contact_to_cut_mean_A"] for row in bucket]),
                }
            )
    return out


def write_determinism_note(path: Path, run_rows: list[dict], seed_profiles: list[dict]):
    combo_counts: dict[tuple[int, int, int, int, str], int] = {}
    unique_cells = set()
    for row in run_rows:
        key = (
            int(row["cell_FR"]),
            int(row["cell_MB"]),
            int(row["cell_PD"]),
            int(row["cell_ODW"]),
            str(row["seed_profile_id"]),
        )
        combo_counts[key] = combo_counts.get(key, 0) + 1
        unique_cells.add((int(row["cell_FR"]), int(row["cell_MB"]), int(row["cell_PD"]), int(row["cell_ODW"])))
    duplicate_combos = sum(1 for count in combo_counts.values() if count > 1)
    unique_digests = len({str(row["determinism_digest"]) for row in run_rows})
    expected_runs = len(FR_LEVELS) * len(MB_LEVELS) * len(PD_LEVELS) * len(ODW_LEVELS) * len(seed_profiles)
    unique_cell_count = len(unique_cells)
    if unique_digests == unique_cell_count:
        digest_interpretation = (
            "Unique digests equal unique DOE cells, which indicates seed profile variation is behaviorally inert "
            "under this controlled synthetic setup."
        )
    else:
        digest_interpretation = (
            "Unique digest count does not collapse exactly to cell count; inspect whether seed profile variation "
            "or hidden stochasticity is entering runtime behavior."
        )

    lines = [
        "# FR Authority DOE Determinism Check",
        "",
        f"- Expected runs: `{expected_runs}`",
        f"- Actual runs: `{len(run_rows)}`",
        f"- Seed profiles: `{len(seed_profiles)}`",
        f"- Fixed-seed discipline: `random_seed`, `background_map_seed`, and `metatype_random_seed` are explicit for every run.",
        f"- Duplicate `(FR, MB, PD, ODW, seed_profile_id)` combos: `{duplicate_combos}`",
        f"- Unique DOE cells: `{unique_cell_count}`",
        f"- Unique final-state digests: `{unique_digests}`",
        f"- Digest interpretation: `{digest_interpretation}`",
        "- Interpretation: this is a fixed-seed coverage check, not a repeated-rerun determinism proof.",
        "",
        "## Reproduction Command",
        "",
        "```powershell",
        "python analysis/engineering_reports/developments/20260311/phase_fr_authority_audit/run_fr_authority_doe.py",
        "```",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def append_interpretable_note(summary_path: Path, run_rows: list[dict], odw_split_rows: list[dict], fr_odw_rows: list[dict]):
    fr_lines = []
    for fr in FR_LEVELS:
        bucket = [row for row in run_rows if int(row["cell_FR"]) == int(fr)]
        fr_lines.append(
            (
                f"- FR={fr}: A win rate=`{a_win_rate(bucket):.1f}%`, "
                f"WedgePresent rate=`{_true_rate(bucket, 'wedge_present_A'):.1f}%`, "
                f"StructuralFragility rate=`{_true_rate(bucket, 'structural_fragility_A'):.1f}%`, "
                f"PostureCoherence rate=`{_true_rate(bucket, 'posture_coherence_A'):.1f}%`, "
                f"mean `first_major_divergence_tick`=`{mean_or_nan([row['first_major_divergence_tick'] for row in bucket]):.1f}`, "
                f"mean `fire_eff_contact_to_cut_A`=`{mean_or_nan([row['fire_eff_contact_to_cut_mean_A'] for row in bucket]):.4f}`"
            )
        )

    odw_lines = []
    for row in odw_split_rows:
        odw_lines.append(
            (
                f"- ODW={row['cell_ODW']}: A win rate=`{float(row['A_win_rate_pct']):.1f}%`, "
                f"WedgePresent rate=`{float(row['wedge_present_rate_A_pct']):.1f}%`, "
                f"StructuralFragility rate=`{float(row['structural_fragility_rate_A_pct']):.1f}%`, "
                f"PostureCoherence rate=`{float(row['posture_coherence_rate_A_pct']):.1f}%`, "
                f"mean `runtime_c_conn_A`=`{float(row['mean_runtime_c_conn_A']):.4f}`"
            )
        )

    fr_odw_focus = []
    for fr in FR_LEVELS:
        low = next((row for row in fr_odw_rows if int(row["cell_FR"]) == int(fr) and int(row["cell_ODW"]) == 2), None)
        high = next((row for row in fr_odw_rows if int(row["cell_FR"]) == int(fr) and int(row["cell_ODW"]) == 8), None)
        if low is None or high is None:
            continue
        fr_odw_focus.append(
            (
                f"- FR={fr}: `ODW 2 -> 8` changes A-side WedgePresent rate from "
                f"`{float(low['wedge_present_rate_A_pct']):.1f}%` to `{float(high['wedge_present_rate_A_pct']):.1f}%`, "
                f"StructuralFragility rate from `{float(low['structural_fragility_rate_A_pct']):.1f}%` to "
                f"`{float(high['structural_fragility_rate_A_pct']):.1f}%`, "
                f"PostureCoherence rate from `{float(low['posture_coherence_rate_A_pct']):.1f}%` to "
                f"`{float(high['posture_coherence_rate_A_pct']):.1f}%`, "
                f"mean `first_major_divergence_tick` from `{float(low['mean_first_major_divergence_tick']):.1f}` to "
                f"`{float(high['mean_first_major_divergence_tick']):.1f}`"
            )
        )

    coherent_wedge_count = sum(1 for row in run_rows if str(row.get("front_profile_A")) == "coherent_penetration_wedge")
    extra = [
        "",
        "## 5. Interpretable Readout Addendum",
        "- Variable side is `A`; opponent `B` is the controlled isolation baseline.",
        "- Time-resolved alive-unit trajectories are stored separately in `fr_authority_doe_alive_trajectory.csv`.",
        "- Readout emphasis follows governance: `outcome + time-resolved battle trajectory`, not outcome alone.",
        f"- Coherent A-side penetration wedges observed: `{coherent_wedge_count}` runs.",
        "",
        "### FR Readout",
        *fr_lines,
        "",
        "### ODW Support Split",
        *odw_lines,
        "",
        "### FR x ODW Interaction Focus",
        *fr_odw_focus,
        "",
    ]
    current = summary_path.read_text(encoding="utf-8")
    summary_path.write_text(current.rstrip() + "\n" + "\n".join(extra), encoding="utf-8")


def main():
    base_settings = load_inputs()
    seed_profiles = build_seed_profiles()
    run_rows = []
    alive_rows = []
    total_runs = len(FR_LEVELS) * len(MB_LEVELS) * len(PD_LEVELS) * len(ODW_LEVELS) * len(seed_profiles)
    completed = 0

    for seed_profile in seed_profiles:
        for fr in FR_LEVELS:
            for mb in MB_LEVELS:
                for pd in PD_LEVELS:
                    for odw in ODW_LEVELS:
                        row, alive_chunk = run_single_case(base_settings, seed_profile, fr, mb, pd, odw)
                        run_rows.append(row)
                        alive_rows.extend(alive_chunk)
                        completed += 1
                        if completed % 25 == 0 or completed == total_runs:
                            print(
                                f"[fr_authority_doe] completed={completed}/{total_runs} "
                                f"seed={seed_profile['seed_profile_id']} FR={fr} MB={mb} PD={pd} ODW={odw}"
                            )

    run_table_path = OUT_DIR / "fr_authority_doe_run_table.csv"
    alive_path = OUT_DIR / "fr_authority_doe_alive_trajectory.csv"
    odw_split_path = OUT_DIR / "fr_authority_doe_odw_split_summary.csv"
    fr_odw_path = OUT_DIR / "fr_authority_doe_fr_odw_summary.csv"
    determinism_path = OUT_DIR / "fr_authority_doe_determinism_check.md"
    summary_path = OUT_DIR / "fr_authority_doe_summary.md"

    write_csv(run_table_path, run_rows)
    write_csv(alive_path, alive_rows)
    odw_split_rows = build_odw_split_summary(run_rows)
    fr_odw_rows = build_fr_odw_summary(run_rows)
    write_csv(odw_split_path, odw_split_rows)
    write_csv(fr_odw_path, fr_odw_rows)
    write_determinism_note(determinism_path, run_rows, seed_profiles)

    subprocess.run(
        [
            sys.executable,
            str(DOE_POSTPROCESS),
            "--run-table",
            str(run_table_path),
            "--summary-out",
            str(summary_path),
            "--title",
            TITLE,
            "--deviations",
            "ODW is retained only as a support split; time-resolved alive trajectories are stored in a companion CSV.",
        ],
        check=True,
        cwd=str(ROOT),
    )
    append_interpretable_note(summary_path, run_rows, odw_split_rows, fr_odw_rows)
    print(f"[fr_authority_doe] run_table={run_table_path}")
    print(f"[fr_authority_doe] summary={summary_path}")


if __name__ == "__main__":
    main()
