import math
from collections.abc import Mapping
from dataclasses import replace
from typing import Any

from runtime.runtime_v0_1 import BattleState

from test_run.test_run_telemetry import (
    compute_bridge_metrics_per_side,
    compute_collapse_v2_shadow_telemetry,
    compute_hostile_intermix_metrics,
    extract_runtime_debug_payload,
)


PRE_TL_TARGET_SUBSTRATE_DEFAULT = "nearest5_centroid"
HOSTILE_CONTACT_IMPEDANCE_MODE_DEFAULT = "off"
HOSTILE_CONTACT_IMPEDANCE_V2_RADIUS_MULTIPLIER_DEFAULT = 1.50
HOSTILE_CONTACT_IMPEDANCE_V2_REPULSION_MAX_DISP_RATIO_DEFAULT = 0.20
HOSTILE_CONTACT_IMPEDANCE_V2_FORWARD_DAMPING_STRENGTH_DEFAULT = 0.50
HOSTILE_INTENT_UNIFIED_SPACING_SCALE_DEFAULT = 1.00
HOSTILE_INTENT_UNIFIED_SPACING_STRENGTH_DEFAULT = 1.00
CONTINUOUS_FR_SHAPING_OFF = "off"

SimulationExecutionConfig = dict
SimulationMovementConfig = dict
SimulationContactConfig = dict
SimulationBoundaryConfig = dict
SimulationRuntimeConfig = dict
SimulationObserverConfig = dict


def _clamp01(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return value


def _require_mapping(cfg: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    section = cfg.get(key)
    if not isinstance(section, Mapping):
        raise TypeError(f"run_simulation requires '{key}' to be a mapping, got {type(section).__name__}")
    return section


def run_simulation(
    initial_state: BattleState,
    *,
    engine_cls: Any | None,
    execution_cfg: Mapping[str, Any],
    runtime_cfg: Mapping[str, Any],
    observer_cfg: Mapping[str, Any],
):
    if engine_cls is None:
        raise ValueError("run_simulation requires an explicit engine_cls")

    movement_cfg = _require_mapping(runtime_cfg, "movement")
    contact_cfg = _require_mapping(runtime_cfg, "contact")
    boundary_cfg = _require_mapping(runtime_cfg, "boundary")
    bridge_cfg = _require_mapping(observer_cfg, "bridge")
    collapse_shadow_cfg = _require_mapping(observer_cfg, "collapse_shadow")
    continuous_fr_shaping_cfg = movement_cfg.get("continuous_fr_shaping", {})
    if not isinstance(continuous_fr_shaping_cfg, Mapping):
        continuous_fr_shaping_cfg = {}
    odw_posture_bias_cfg = movement_cfg.get("odw_posture_bias", {})
    if not isinstance(odw_posture_bias_cfg, Mapping):
        odw_posture_bias_cfg = {}
    hybrid_v2_cfg = contact_cfg.get("hybrid_v2", {})
    if not isinstance(hybrid_v2_cfg, Mapping):
        hybrid_v2_cfg = {}
    intent_unified_spacing_cfg = contact_cfg.get("intent_unified_spacing_v1", {})
    if not isinstance(intent_unified_spacing_cfg, Mapping):
        intent_unified_spacing_cfg = {}
    steps = int(execution_cfg["steps"])
    capture_positions = bool(execution_cfg["capture_positions"])
    frame_stride = int(execution_cfg["frame_stride"])
    include_target_lines = bool(execution_cfg["include_target_lines"])
    print_tick_summary = bool(execution_cfg["print_tick_summary"])
    observer_enabled = bool(observer_cfg["enabled"])
    post_elimination_extra_ticks = max(0, int(execution_cfg.get("post_elimination_extra_ticks", 10)))

    engine = engine_cls(
        attack_range=float(contact_cfg["attack_range"]),
        damage_per_tick=float(contact_cfg["damage_per_tick"]),
        separation_radius=float(contact_cfg["separation_radius"]),
    )
    for attr, value in (
        ("COHESION_DECISION_SOURCE", str(runtime_cfg["decision_source"]).strip().lower() or "v2"),
        ("MOVEMENT_MODEL", str(runtime_cfg["movement_model"]).strip().lower() or "v3a"),
        ("MOVEMENT_V3A_EXPERIMENT", str(movement_cfg.get("experiment_effective", "base")).strip().lower() or "base"),
        ("CENTROID_PROBE_SCALE", float(movement_cfg.get("centroid_probe_scale_effective", 1.0))),
        (
            "PRE_TL_TARGET_SUBSTRATE",
            str(movement_cfg.get("pre_tl_target_substrate", PRE_TL_TARGET_SUBSTRATE_DEFAULT)).strip().lower()
            or PRE_TL_TARGET_SUBSTRATE_DEFAULT,
        ),
        ("ODW_POSTURE_BIAS_ENABLED", bool(odw_posture_bias_cfg.get("enabled_effective", False))),
        ("ODW_POSTURE_BIAS_K", max(0.0, float(odw_posture_bias_cfg.get("k_effective", 0.0)))),
        ("ODW_POSTURE_BIAS_CLIP_DELTA", max(0.0, float(odw_posture_bias_cfg.get("clip_delta_effective", 0.2)))),
        ("SYMMETRIC_MOVEMENT_SYNC_ENABLED", bool(movement_cfg.get("symmetric_movement_sync_enabled", True))),
        (
            "HOSTILE_CONTACT_IMPEDANCE_MODE",
            str(contact_cfg.get("hostile_contact_impedance_mode", HOSTILE_CONTACT_IMPEDANCE_MODE_DEFAULT)).strip().lower()
            or HOSTILE_CONTACT_IMPEDANCE_MODE_DEFAULT,
        ),
        (
            "HOSTILE_CONTACT_IMPEDANCE_V2_RADIUS_MULTIPLIER",
            max(1e-6, float(hybrid_v2_cfg.get("radius_multiplier", HOSTILE_CONTACT_IMPEDANCE_V2_RADIUS_MULTIPLIER_DEFAULT))),
        ),
        (
            "HOSTILE_CONTACT_IMPEDANCE_V2_REPULSION_MAX_DISP_RATIO",
            max(
                0.0,
                float(hybrid_v2_cfg.get("repulsion_max_disp_ratio", HOSTILE_CONTACT_IMPEDANCE_V2_REPULSION_MAX_DISP_RATIO_DEFAULT)),
            ),
        ),
        (
            "HOSTILE_CONTACT_IMPEDANCE_V2_FORWARD_DAMPING_STRENGTH",
            _clamp01(
                float(hybrid_v2_cfg.get("forward_damping_strength", HOSTILE_CONTACT_IMPEDANCE_V2_FORWARD_DAMPING_STRENGTH_DEFAULT))
            ),
        ),
        (
            "HOSTILE_INTENT_UNIFIED_SPACING_SCALE",
            max(1e-6, float(intent_unified_spacing_cfg.get("scale", HOSTILE_INTENT_UNIFIED_SPACING_SCALE_DEFAULT))),
        ),
        (
            "HOSTILE_INTENT_UNIFIED_SPACING_STRENGTH",
            _clamp01(float(intent_unified_spacing_cfg.get("strength", HOSTILE_INTENT_UNIFIED_SPACING_STRENGTH_DEFAULT))),
        ),
        ("CONTINUOUS_FR_SHAPING_ENABLED", bool(continuous_fr_shaping_cfg.get("effective", False))),
        (
            "CONTINUOUS_FR_SHAPING_MODE",
            str(continuous_fr_shaping_cfg.get("mode_effective", CONTINUOUS_FR_SHAPING_OFF)).strip().lower()
            or CONTINUOUS_FR_SHAPING_OFF,
        ),
        ("CONTINUOUS_FR_SHAPING_A", max(0.0, float(continuous_fr_shaping_cfg.get("a", 0.0)))),
        ("CONTINUOUS_FR_SHAPING_SIGMA", max(1e-6, float(continuous_fr_shaping_cfg.get("sigma", 0.15)))),
        ("CONTINUOUS_FR_SHAPING_P", max(0.0, float(continuous_fr_shaping_cfg.get("p", 1.0)))),
        ("CONTINUOUS_FR_SHAPING_Q", max(0.0, float(continuous_fr_shaping_cfg.get("q", 1.0)))),
        ("CONTINUOUS_FR_SHAPING_BETA", max(0.0, float(continuous_fr_shaping_cfg.get("beta", 0.0)))),
        ("CONTINUOUS_FR_SHAPING_GAMMA", max(0.0, float(continuous_fr_shaping_cfg.get("gamma", 0.0)))),
        ("V2_CONNECT_RADIUS_MULTIPLIER", max(1e-12, float(movement_cfg.get("v2_connect_radius_multiplier", 1.0)))),
        ("V3_CONNECT_RADIUS_MULTIPLIER", max(1e-12, float(movement_cfg.get("v3_connect_radius_multiplier_effective", 1.0)))),
        ("V3_R_REF_RADIUS_MULTIPLIER", max(1e-12, float(movement_cfg.get("v3_r_ref_radius_multiplier_effective", 1.0)))),
        ("fire_quality_alpha", float(contact_cfg["fire_quality_alpha"])),
        ("contact_hysteresis_h", float(contact_cfg["contact_hysteresis_h"])),
        ("CH_ENABLED", bool(contact_cfg["ch_enabled"])),
        ("FSR_ENABLED", bool(contact_cfg["fsr_enabled"])),
        ("fsr_strength", float(contact_cfg["fsr_strength"])),
        ("BOUNDARY_SOFT_ENABLED", bool(boundary_cfg["enabled"])),
        ("BOUNDARY_HARD_ENABLED", bool(boundary_cfg["enabled"]) and bool(boundary_cfg["hard_enabled"])),
        ("boundary_soft_strength", max(0.0, float(boundary_cfg["soft_strength"]))),
        ("alpha_sep", max(0.0, float(contact_cfg["alpha_sep"]))),
    ):
        setattr(engine, attr, value)

    diagnostics_enabled = bool(observer_enabled) or bool(execution_cfg["plot_diagnostics_enabled"])
    observer_active = bool(diagnostics_enabled) and (
        bool(capture_positions) or bool(observer_cfg.get("runtime_diag_enabled", False))
    )
    engine.debug_fsr_diag_enabled = observer_active
    engine.debug_diag4_enabled = observer_active
    engine.debug_diag4_rpg_enabled = False
    engine.debug_cohesion_v3_shadow_enabled = bool(diagnostics_enabled)

    state = replace(
        initial_state,
        last_target_direction={
            fleet_id: initial_state.last_target_direction.get(fleet_id, (0.0, 0.0))
            for fleet_id in initial_state.fleets
        },
        last_engagement_intensity={
            fleet_id: initial_state.last_engagement_intensity.get(fleet_id, 0.0)
            for fleet_id in initial_state.fleets
        },
    )
    fleet_ids = tuple(state.fleets)

    def _per_fleet_series() -> dict[str, list]:
        return {fleet_id: [] for fleet_id in fleet_ids}

    trajectory = _per_fleet_series()
    alive_trajectory = _per_fleet_series()
    fleet_size_trajectory = _per_fleet_series()
    observer_telemetry = {
        **{
            key: _per_fleet_series()
            for key in (
                "cohesion_v3",
                "c_conn",
                "c_scale",
                "rho",
                "centroid_x",
                "centroid_y",
                "center_wing_advance_gap",
                "front_curvature_index",
                "center_wing_parallel_share",
                "posture_persistence_time",
            )
        },
        "net_axis_push": {"net": []},
        "net_axis_push_interval_ticks": 10,
        "center_wing_advance_gap_interval_ticks": 10,
        "hostile_overlap_pairs": [],
        "hostile_deep_pairs": [],
        "hostile_deep_intermix_ratio": [],
        "hostile_intermix_severity": [],
        "hostile_intermix_coverage": [],
    }
    combat_telemetry = {
        "in_contact_count": [],
        "damage_events_count": [],
        "outlier_total": [],
        "persistent_outlier_total": [],
        "max_outlier_persistence": [],
    }
    bridge_telemetry = {
        "theta_split": float(bridge_cfg["theta_split"]),
        "theta_env": float(bridge_cfg["theta_env"]),
        "sustain_ticks": int(bridge_cfg["sustain_ticks"]),
        **{
            key: _per_fleet_series()
            for key in (
                "AR",
                "wedge_ratio",
                "split_separation",
                "angle_coverage",
                "split_cond",
                "env_cond",
                "split_sustain_counter",
                "env_sustain_counter",
                "bridge_event_cut",
                "bridge_event_pocket",
            )
        },
        "first_tick_split_sustain": {fleet_id: None for fleet_id in fleet_ids},
        "first_tick_env_sustain": {fleet_id: None for fleet_id in fleet_ids},
    }
    split_counter_state = {fleet_id: 0 for fleet_id in fleet_ids}
    env_counter_state = {fleet_id: 0 for fleet_id in fleet_ids}
    position_frames = []
    center_wing_interval_ticks = int(observer_telemetry.get("center_wing_advance_gap_interval_ticks", 10))
    center_wing_position_history = _per_fleet_series()
    posture_persistence_state = {fleet_id: {"sign": 0, "length": 0} for fleet_id in fleet_ids}

    def _append_empty_shape_metrics(fleet_id: str, series: list[float]) -> None:
        series.append(float("nan"))
        observer_telemetry["front_curvature_index"][fleet_id].append(float("nan"))
        observer_telemetry["center_wing_parallel_share"][fleet_id].append(float("nan"))
        observer_telemetry["posture_persistence_time"][fleet_id].append(0.0)
        posture_persistence_state[fleet_id]["sign"] = 0
        posture_persistence_state[fleet_id]["length"] = 0

    if steps <= 0:
        tick_limit = 999
        elimination_tick = None
        post_elimination_stop_tick = None
    else:
        tick_limit = steps
        elimination_tick = None
        post_elimination_stop_tick = None

    while state.tick < tick_limit:
        state = engine.step(state)
        combat_stats = getattr(engine, "debug_last_combat_stats", {})
        if not isinstance(combat_stats, dict):
            combat_stats = {}
        combat_telemetry["in_contact_count"].append(int(combat_stats.get("in_contact_count", 0)))
        combat_telemetry["damage_events_count"].append(int(combat_stats.get("damage_events_count", 0)))
        runtime_debug_payload = extract_runtime_debug_payload(
            getattr(engine, "debug_diag_last_tick", {}) if diagnostics_enabled else {}
        )
        combat_telemetry["outlier_total"].append(int(runtime_debug_payload.get("outlier_total", 0)))
        combat_telemetry["persistent_outlier_total"].append(int(runtime_debug_payload.get("persistent_outlier_total", 0)))
        combat_telemetry["max_outlier_persistence"].append(int(runtime_debug_payload.get("max_outlier_persistence", 0)))
        contact_active_tick = int(combat_stats.get("in_contact_count", 0)) > 0

        if print_tick_summary:
            ordered_fleet_ids = [fleet_id for fleet_id in ("A", "B") if fleet_id in state.fleets]
            if not ordered_fleet_ids:
                ordered_fleet_ids = sorted(state.fleets.keys())
            if len(ordered_fleet_ids) >= 2:
                fleet_a = state.fleets[ordered_fleet_ids[0]]
                fleet_b = state.fleets[ordered_fleet_ids[1]]
                name_a = str(getattr(fleet_a.parameters, "archetype_id", "") or ordered_fleet_ids[0])
                name_b = str(getattr(fleet_b.parameters, "archetype_id", "") or ordered_fleet_ids[1])
                print(f"t={state.tick}, [{name_a}] vs [{name_b}], {len(fleet_a.unit_ids)}/{len(fleet_b.unit_ids)}")
            elif len(ordered_fleet_ids) == 1:
                fleet = state.fleets[ordered_fleet_ids[0]]
                name = str(getattr(fleet.parameters, "archetype_id", "") or ordered_fleet_ids[0])
                print(f"t={state.tick}, [{name}], {len(fleet.unit_ids)}")

        for fleet_id, fleet in state.fleets.items():
            trajectory[fleet_id].append(state.last_fleet_cohesion.get(fleet_id, 1.0))
            alive_trajectory[fleet_id].append(len(fleet.unit_ids))
            fleet_size = 0.0
            centroid_sum_x = 0.0
            centroid_sum_y = 0.0
            centroid_count = 0
            unit_position_map: dict[str, tuple[float, float]] = {}
            for unit_id in fleet.unit_ids:
                if unit_id in state.units:
                    unit_state = state.units[unit_id]
                    fleet_size += max(0.0, float(unit_state.hit_points))
                    centroid_sum_x += float(unit_state.position.x)
                    centroid_sum_y += float(unit_state.position.y)
                    centroid_count += 1
                    unit_position_map[str(unit_id)] = (float(unit_state.position.x), float(unit_state.position.y))
            fleet_size_trajectory[fleet_id].append(fleet_size)
            center_wing_position_history[fleet_id].append(unit_position_map)
            if centroid_count > 0:
                observer_telemetry["centroid_x"][fleet_id].append(centroid_sum_x / float(centroid_count))
                observer_telemetry["centroid_y"][fleet_id].append(centroid_sum_y / float(centroid_count))
            else:
                observer_telemetry["centroid_x"][fleet_id].append(float("nan"))
                observer_telemetry["centroid_y"][fleet_id].append(float("nan"))

        hostile_intermix_metrics = compute_hostile_intermix_metrics(
            state,
            float(contact_cfg["separation_radius"]),
        )
        for metric_key in (
            "hostile_overlap_pairs",
            "hostile_deep_pairs",
            "hostile_deep_intermix_ratio",
            "hostile_intermix_severity",
            "hostile_intermix_coverage",
        ):
            observer_telemetry[metric_key].append(float(hostile_intermix_metrics.get(metric_key, 0.0)))

        for fleet_id in state.fleets:
            series = observer_telemetry["center_wing_advance_gap"][fleet_id]
            history = center_wing_position_history.get(fleet_id, [])
            current_positions = history[-1] if history else {}
            current_unit_ids = list(current_positions.keys())
            enemy_centroids = []
            for other_fleet_id in state.fleets:
                if other_fleet_id == fleet_id:
                    continue
                enemy_x = float(observer_telemetry["centroid_x"].get(other_fleet_id, [float("nan")])[-1])
                enemy_y = float(observer_telemetry["centroid_y"].get(other_fleet_id, [float("nan")])[-1])
                if math.isfinite(enemy_x) and math.isfinite(enemy_y):
                    enemy_centroids.append((enemy_x, enemy_y))
            if len(current_unit_ids) < 6 or not enemy_centroids:
                _append_empty_shape_metrics(fleet_id, series)
                continue

            curr_xs_now = [current_positions[unit_id][0] for unit_id in current_unit_ids]
            curr_ys_now = [current_positions[unit_id][1] for unit_id in current_unit_ids]
            centroid_x_now = sum(curr_xs_now) / float(len(curr_xs_now))
            centroid_y_now = sum(curr_ys_now) / float(len(curr_ys_now))
            enemy_centroid_x = sum(item[0] for item in enemy_centroids) / float(len(enemy_centroids))
            enemy_centroid_y = sum(item[1] for item in enemy_centroids) / float(len(enemy_centroids))
            axis_dx = enemy_centroid_x - centroid_x_now
            axis_dy = enemy_centroid_y - centroid_y_now
            axis_norm = math.sqrt((axis_dx * axis_dx) + (axis_dy * axis_dy))
            if axis_norm <= 1e-12:
                _append_empty_shape_metrics(fleet_id, series)
                continue
            axis_dir_x = axis_dx / axis_norm
            axis_dir_y = axis_dy / axis_norm

            projected_units: list[tuple[float, float, str]] = []
            for unit_id in current_unit_ids:
                curr_x, curr_y = current_positions[unit_id]
                lateral_offset_now = ((curr_x - centroid_x_now) * (-axis_dir_y)) + ((curr_y - centroid_y_now) * axis_dir_x)
                advance_now = ((curr_x - centroid_x_now) * axis_dir_x) + ((curr_y - centroid_y_now) * axis_dir_y)
                projected_units.append((float(advance_now), abs(float(lateral_offset_now)), str(unit_id)))

            projected_units.sort(key=lambda item: item[0])
            projected_units_by_width = sorted(
                ((item[1], item[2]) for item in projected_units),
                key=lambda item: item[0],
            )
            width_split_index = len(projected_units_by_width) // 2
            center_unit_ids = {unit_id for _, unit_id in projected_units_by_width[:width_split_index]}
            wing_unit_ids = {unit_id for _, unit_id in projected_units_by_width[width_split_index:]}

            if len(history) <= center_wing_interval_ticks:
                series.append(float("nan"))
                interval_parallel_share_gap = float("nan")
            else:
                prev_positions = history[-(center_wing_interval_ticks + 1)]
                common_unit_ids = [unit_id for unit_id in current_positions if unit_id in prev_positions]
                if len(common_unit_ids) < 4:
                    series.append(float("nan"))
                    interval_parallel_share_gap = float("nan")
                else:
                    center_advances: list[float] = []
                    wing_advances: list[float] = []
                    center_interval_total = 0.0
                    wing_interval_total = 0.0
                    for unit_id in common_unit_ids:
                        curr_x, curr_y = current_positions[unit_id]
                        prev_x, prev_y = prev_positions[unit_id]
                        advance = ((curr_x - prev_x) * axis_dir_x) + ((curr_y - prev_y) * axis_dir_y)
                        if unit_id in center_unit_ids:
                            center_advances.append(float(advance))
                            center_interval_total += advance
                        elif unit_id in wing_unit_ids:
                            wing_advances.append(float(advance))
                            wing_interval_total += advance
                    if not center_advances or not wing_advances:
                        series.append(float("nan"))
                        interval_parallel_share_gap = float("nan")
                    else:
                        center_mean = sum(center_advances) / float(len(center_advances))
                        wing_mean = sum(wing_advances) / float(len(wing_advances))
                        series.append(0.5 * float(center_mean - wing_mean))
                        interval_parallel_total = abs(center_interval_total) + abs(wing_interval_total)
                        if interval_parallel_total > 1e-12:
                            interval_parallel_share_gap = float(
                                (center_interval_total - wing_interval_total) / interval_parallel_total
                            )
                        else:
                            interval_parallel_share_gap = 0.0

            front_group_size = max(3, int(math.ceil(len(projected_units) * 0.30)))
            front_group = projected_units[-front_group_size:]
            front_group.sort(key=lambda item: item[1])
            front_split_index = len(front_group) // 2
            front_center_band = front_group[:front_split_index]
            front_wing_band = front_group[front_split_index:]
            if front_center_band and front_wing_band:
                front_center_mean = sum(item[0] for item in front_center_band) / float(len(front_center_band))
                front_wing_mean = sum(item[0] for item in front_wing_band) / float(len(front_wing_band))
                front_curvature_raw = float(front_center_mean - front_wing_mean)
            else:
                front_curvature_raw = float("nan")
            observer_telemetry["front_curvature_index"][fleet_id].append(front_curvature_raw)

            center_parallel_total = 0.0
            wing_parallel_total = 0.0
            for unit_id in current_unit_ids:
                unit_state = state.units.get(unit_id)
                if unit_state is None:
                    continue
                parallel_velocity = (
                    float(unit_state.velocity.x) * axis_dir_x
                    + float(unit_state.velocity.y) * axis_dir_y
                )
                if unit_id in center_unit_ids:
                    center_parallel_total += parallel_velocity
                elif unit_id in wing_unit_ids:
                    wing_parallel_total += parallel_velocity
            total_parallel = abs(center_parallel_total) + abs(wing_parallel_total)
            if total_parallel > 1e-12:
                instantaneous_parallel_share_gap = float(
                    (center_parallel_total - wing_parallel_total) / total_parallel
                )
            else:
                instantaneous_parallel_share_gap = 0.0
            if math.isfinite(interval_parallel_share_gap):
                center_wing_parallel_share_gap = interval_parallel_share_gap
            else:
                center_wing_parallel_share_gap = instantaneous_parallel_share_gap
            observer_telemetry["center_wing_parallel_share"][fleet_id].append(center_wing_parallel_share_gap)

            posture_sign = 0
            if math.isfinite(front_curvature_raw):
                front_curvature_norm = float(front_curvature_raw) / max(float(contact_cfg["separation_radius"]), 1e-12)
                if front_curvature_norm >= 0.10 and center_wing_parallel_share_gap >= 0.05:
                    posture_sign = 1
                elif front_curvature_norm <= -0.10 and center_wing_parallel_share_gap <= -0.05:
                    posture_sign = -1
            prior_sign = int(posture_persistence_state[fleet_id]["sign"])
            prior_length = int(posture_persistence_state[fleet_id]["length"])
            if posture_sign == 0:
                next_length = 0
            elif posture_sign == prior_sign:
                next_length = prior_length + 1
            else:
                next_length = 1
            posture_persistence_state[fleet_id]["sign"] = posture_sign
            posture_persistence_state[fleet_id]["length"] = next_length
            observer_telemetry["posture_persistence_time"][fleet_id].append(float(posture_sign * next_length))

        shadow_v3 = getattr(engine, "debug_last_cohesion_v3", {})
        if not isinstance(shadow_v3, dict):
            shadow_v3 = {}
        shadow_v3_components = getattr(engine, "debug_last_cohesion_v3_components", {})
        if not isinstance(shadow_v3_components, dict):
            shadow_v3_components = {}
        for fleet_id in state.fleets:
            fallback_v2 = float(state.last_fleet_cohesion.get(fleet_id, 1.0))
            cohesion_v3 = float(shadow_v3.get(fleet_id, fallback_v2)) if diagnostics_enabled else float("nan")
            comp = shadow_v3_components.get(fleet_id, {})
            if not isinstance(comp, dict):
                comp = {}
            observer_telemetry["cohesion_v3"][fleet_id].append(cohesion_v3)
            observer_telemetry["c_conn"][fleet_id].append(float(comp.get("c_conn", float("nan"))))
            observer_telemetry["c_scale"][fleet_id].append(float(comp.get("c_scale", float("nan"))))
            observer_telemetry["rho"][fleet_id].append(float(comp.get("rho", float("nan"))))

        bridge_metrics = compute_bridge_metrics_per_side(state)
        for fleet_id in state.fleets:
            if diagnostics_enabled:
                metric = bridge_metrics.get(fleet_id, {})
                ar_value = float(metric.get("AR", float("nan")))
                wedge_value = float(metric.get("wedge_ratio", float("nan")))
                split_value = float(metric.get("split_separation", 0.0))
                env_value = float(metric.get("angle_coverage", 0.0))
                split_cond = bool(
                    state.tick >= 1 and contact_active_tick and split_value >= float(bridge_cfg["theta_split"])
                )
                env_cond = bool(
                    state.tick >= 1 and contact_active_tick and env_value >= float(bridge_cfg["theta_env"])
                )
            else:
                ar_value = float("nan")
                wedge_value = float("nan")
                split_value = float("nan")
                env_value = float("nan")
                split_cond = False
                env_cond = False

            if split_cond:
                split_counter_state[fleet_id] = int(split_counter_state.get(fleet_id, 0)) + 1
            else:
                split_counter_state[fleet_id] = 0
            if env_cond:
                env_counter_state[fleet_id] = int(env_counter_state.get(fleet_id, 0)) + 1
            else:
                env_counter_state[fleet_id] = 0

            cut_event_tick = False
            pocket_event_tick = False
            if (
                split_counter_state[fleet_id] >= int(bridge_cfg["sustain_ticks"])
                and bridge_telemetry["first_tick_split_sustain"].get(fleet_id) is None
            ):
                bridge_telemetry["first_tick_split_sustain"][fleet_id] = int(state.tick)
                cut_event_tick = True
            if (
                env_counter_state[fleet_id] >= int(bridge_cfg["sustain_ticks"])
                and bridge_telemetry["first_tick_env_sustain"].get(fleet_id) is None
            ):
                bridge_telemetry["first_tick_env_sustain"][fleet_id] = int(state.tick)
                pocket_event_tick = True

            for metric_key, metric_value in (
                ("AR", ar_value),
                ("wedge_ratio", wedge_value),
                ("split_separation", split_value),
                ("angle_coverage", env_value),
                ("split_cond", bool(split_cond)),
                ("env_cond", bool(env_cond)),
                ("split_sustain_counter", int(split_counter_state[fleet_id])),
                ("env_sustain_counter", int(env_counter_state[fleet_id])),
                ("bridge_event_cut", bool(cut_event_tick)),
                ("bridge_event_pocket", bool(pocket_event_tick)),
            ):
                bridge_telemetry[metric_key][fleet_id].append(metric_value)

        if capture_positions and frame_stride > 0 and state.tick % frame_stride == 0:
            frame = {"tick": state.tick}
            targets = {}
            for fleet_id, fleet in state.fleets.items():
                points = []
                for unit_id in fleet.unit_ids:
                    if unit_id in state.units:
                        unit = state.units[unit_id]
                        points.append(
                            (
                                unit_id,
                                unit.position.x,
                                unit.position.y,
                                unit.orientation_vector.x,
                                unit.orientation_vector.y,
                                unit.velocity.x,
                                unit.velocity.y,
                            )
                        )
                        if include_target_lines and unit.engaged and unit.engaged_target_id:
                            target_id = str(unit.engaged_target_id)
                            if target_id in state.units and state.units[target_id].hit_points > 0.0:
                                targets[str(unit_id)] = target_id
                frame[fleet_id] = points
            if include_target_lines:
                frame["targets"] = targets
            frame["runtime_debug"] = extract_runtime_debug_payload(
                getattr(engine, "debug_diag_last_tick", {}) if observer_active else {}
            )
            position_frames.append(frame)

        any_fleet_eliminated = any(len(fleet.unit_ids) == 0 for fleet in state.fleets.values())
        if steps <= 0:
            if any_fleet_eliminated and elimination_tick is None:
                elimination_tick = state.tick
                post_elimination_stop_tick = min(999, elimination_tick + post_elimination_extra_ticks)
            if post_elimination_stop_tick is not None and state.tick >= post_elimination_stop_tick:
                break
        elif any_fleet_eliminated:
            break

    net_axis_push_interval_ticks = int(observer_telemetry.get("net_axis_push_interval_ticks", 10))
    center_wing_interval_ticks = int(observer_telemetry.get("center_wing_advance_gap_interval_ticks", 10))
    max_unit_speed = 1.0
    if isinstance(state.units, Mapping) and state.units:
        unit_speed_values = []
        for unit_state in state.units.values():
            try:
                unit_speed_values.append(float(getattr(unit_state, "max_speed", 0.0)))
            except (TypeError, ValueError):
                continue
        finite_unit_speed_values = [value for value in unit_speed_values if math.isfinite(value) and value > 0.0]
        if finite_unit_speed_values:
            max_unit_speed = max(finite_unit_speed_values)
    net_axis_push_normalization_scale = float(max_unit_speed) * float(net_axis_push_interval_ticks)
    if net_axis_push_normalization_scale <= 0.0 or not math.isfinite(net_axis_push_normalization_scale):
        net_axis_push_normalization_scale = 1.0
    center_wing_normalization_scale = float(max_unit_speed) * float(center_wing_interval_ticks)
    if center_wing_normalization_scale <= 0.0 or not math.isfinite(center_wing_normalization_scale):
        center_wing_normalization_scale = 1.0
    front_curvature_normalization_scale = max(float(contact_cfg["separation_radius"]), 1e-12)

    def _normalize_series(values: list[float], scale: float) -> list[float]:
        return [
            (float(raw_value) / scale) if math.isfinite(float(raw_value)) else float("nan")
            for raw_value in values
        ]

    centroid_x_a = observer_telemetry.get("centroid_x", {}).get("A", [])
    centroid_y_a = observer_telemetry.get("centroid_y", {}).get("A", [])
    centroid_x_b = observer_telemetry.get("centroid_x", {}).get("B", [])
    centroid_y_b = observer_telemetry.get("centroid_y", {}).get("B", [])
    net_axis_push_series: list[float] = []
    axis_initialized = False
    axis_dir_x = 0.0
    axis_dir_y = 0.0
    for idx in range(len(trajectory.get("A", []))):
        ax = float(centroid_x_a[idx]) if idx < len(centroid_x_a) else float("nan")
        ay = float(centroid_y_a[idx]) if idx < len(centroid_y_a) else float("nan")
        bx = float(centroid_x_b[idx]) if idx < len(centroid_x_b) else float("nan")
        by = float(centroid_y_b[idx]) if idx < len(centroid_y_b) else float("nan")
        valid_pair = all(math.isfinite(value) for value in (ax, ay, bx, by))
        if valid_pair and not axis_initialized:
            dx0 = bx - ax
            dy0 = by - ay
            norm0 = math.sqrt((dx0 * dx0) + (dy0 * dy0))
            if norm0 > 1e-12:
                axis_dir_x = dx0 / norm0
                axis_dir_y = dy0 / norm0
                axis_initialized = True
        if (not axis_initialized) or (not valid_pair) or idx < net_axis_push_interval_ticks:
            net_axis_push_series.append(float("nan"))
            continue
        prev_idx = idx - net_axis_push_interval_ticks
        ax_prev = float(centroid_x_a[prev_idx]) if prev_idx < len(centroid_x_a) else float("nan")
        ay_prev = float(centroid_y_a[prev_idx]) if prev_idx < len(centroid_y_a) else float("nan")
        bx_prev = float(centroid_x_b[prev_idx]) if prev_idx < len(centroid_x_b) else float("nan")
        by_prev = float(centroid_y_b[prev_idx]) if prev_idx < len(centroid_y_b) else float("nan")
        if not all(math.isfinite(value) for value in (ax_prev, ay_prev, bx_prev, by_prev)):
            net_axis_push_series.append(float("nan"))
            continue
        advance_a = ((ax - ax_prev) * axis_dir_x) + ((ay - ay_prev) * axis_dir_y)
        advance_b = ((bx_prev - bx) * axis_dir_x) + ((by_prev - by) * axis_dir_y)
        net_axis_push_value = 0.5 * float(advance_a - advance_b)
        net_axis_push_series.append(float(net_axis_push_value / net_axis_push_normalization_scale))
    observer_telemetry["net_axis_push"]["net"] = net_axis_push_series
    observer_telemetry["net_axis_push_normalization_scale"] = net_axis_push_normalization_scale
    for fleet_id in fleet_ids:
        observer_telemetry["center_wing_advance_gap"][fleet_id] = _normalize_series(
            observer_telemetry["center_wing_advance_gap"][fleet_id],
            center_wing_normalization_scale,
        )
        observer_telemetry["front_curvature_index"][fleet_id] = _normalize_series(
            observer_telemetry["front_curvature_index"][fleet_id],
            front_curvature_normalization_scale,
        )
    observer_telemetry["center_wing_advance_gap_normalization_scale"] = center_wing_normalization_scale
    observer_telemetry["front_curvature_index_normalization_scale"] = front_curvature_normalization_scale

    collapse_shadow_telemetry = compute_collapse_v2_shadow_telemetry(
        observer_enabled=diagnostics_enabled,
        observer_telemetry=observer_telemetry,
        alive_trajectory=alive_trajectory,
        theta_conn_default=float(collapse_shadow_cfg["theta_conn_default"]),
        theta_coh_default=float(collapse_shadow_cfg["theta_coh_default"]),
        theta_force_default=float(collapse_shadow_cfg["theta_force_default"]),
        theta_attr_default=float(collapse_shadow_cfg["theta_attr_default"]),
        attrition_window=int(collapse_shadow_cfg["attrition_window"]),
        sustain_ticks=int(collapse_shadow_cfg["sustain_ticks"]),
        min_conditions=int(collapse_shadow_cfg["min_conditions"]),
    )

    return (
        state,
        trajectory,
        alive_trajectory,
        fleet_size_trajectory,
        observer_telemetry,
        combat_telemetry,
        bridge_telemetry,
        collapse_shadow_telemetry,
        position_frames,
    )
