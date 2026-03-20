import random
from collections.abc import Sequence
from datetime import datetime
from pathlib import Path

from test_run import battle_report_builder as report_builder
from test_run import settings_accessor as settings_api
from test_run import test_run_experiments as experiments
from test_run import test_run_v1_0 as core


# Launcher-side validation patterns live here on purpose:
# keep them stdlib-only, close to settings consumption, and out of engine logic.
def _require_choice(name: str, raw_value, allowed: set[str]) -> str:
    value = str(raw_value).strip().lower()
    if value not in allowed:
        allowed_text = ", ".join(sorted(allowed))
        raise ValueError(f"{name} must be one of {{{allowed_text}}}, got {raw_value!r}")
    return value


def _require_positive_float(name: str, raw_value) -> float:
    value = float(raw_value)
    if value <= 0.0:
        raise ValueError(f"{name} must be > 0, got {value}")
    return value


def _require_nonnegative_float(name: str, raw_value) -> float:
    value = float(raw_value)
    if value < 0.0:
        raise ValueError(f"{name} must be >= 0, got {value}")
    return value


def _require_unit_interval_float(name: str, raw_value) -> float:
    value = float(raw_value)
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"{name} must be within [0, 1], got {value}")
    return value


def _require_int_at_least(name: str, raw_value, minimum: int) -> int:
    value = int(raw_value)
    if value < minimum:
        raise ValueError(f"{name} must be >= {minimum}, got {value}")
    return value


def _require_int_between(name: str, raw_value, minimum: int, maximum: int) -> int:
    value = int(raw_value)
    if not minimum <= value <= maximum:
        raise ValueError(f"{name} must be within [{minimum}, {maximum}], got {value}")
    return value


def _raise_if_invalid_initial_geometry(
    *,
    fleet_a_size: int,
    fleet_b_size: int,
    fleet_a_aspect_ratio: float,
    fleet_b_aspect_ratio: float,
    unit_spacing: float,
) -> None:
    errors: list[str] = []
    if fleet_a_size < 1:
        errors.append(f"initial_fleet_a_size must be >= 1, got {fleet_a_size}")
    if fleet_b_size < 1:
        errors.append(f"initial_fleet_b_size must be >= 1, got {fleet_b_size}")
    if fleet_a_aspect_ratio <= 0.0:
        errors.append(
            f"initial_fleet_a_aspect_ratio must be > 0, got {fleet_a_aspect_ratio}"
        )
    if fleet_b_aspect_ratio <= 0.0:
        errors.append(
            f"initial_fleet_b_aspect_ratio must be > 0, got {fleet_b_aspect_ratio}"
        )
    if unit_spacing <= 0.0:
        errors.append(f"min_unit_spacing must be > 0, got {unit_spacing}")

    if errors:
        raise ValueError("Invalid initial geometry settings:\n- " + "\n- ".join(errors))


def _prepare_export_video_cfg(viz_settings: dict, base_dir, run_export_stem: str) -> dict:
    export_video_cfg = viz_settings.get("export_video", {})
    if not isinstance(export_video_cfg, dict):
        export_video_cfg = {}
    else:
        export_video_cfg = dict(export_video_cfg)

    export_video_enabled = bool(
        viz_settings.get("export_video_enabled", export_video_cfg.get("enabled", False))
    )
    export_video_enabled_override = core.get_env_bool("LOGH_EXPORT_VIDEO_ENABLED")
    if export_video_enabled_override is not None:
        export_video_enabled = export_video_enabled_override

    export_video_cfg["enabled"] = export_video_enabled
    raw_video_output_path = str(
        export_video_cfg.get("output_path", core.DEFAULT_VIDEO_EXPORT_DIR)
    )
    resolved_video_output_path = core.resolve_timestamped_video_output_path(
        raw_video_output_path,
        base_dir=base_dir,
        export_stem=f"{run_export_stem}_video",
    )
    export_video_cfg["output_path"] = str(resolved_video_output_path)
    export_video_cfg["output_path_is_final"] = True
    return export_video_cfg


def _first_contact_tick_from_combat(combat_data) -> int | None:
    series = combat_data.get("in_contact_count", [])
    if not isinstance(series, Sequence):
        return None

    for idx, value in enumerate(series, start=1):
        try:
            in_contact = int(value)
        except (TypeError, ValueError):
            continue
        if in_contact > 0:
            return idx
    return None


def _maybe_export_battle_report(
    *,
    export_battle_report: bool,
    final_state,
    alive_trajectory: dict,
    run_export_timestamp: str,
    run_export_stem: str,
    base_dir,
    settings_source_path: str,
    display_language: str,
    effective_random_seed: int,
    fleet_a_data: dict,
    fleet_b_data: dict,
    initial_fleet_sizes: dict,
    fleet_size_trajectory: dict,
    observer_telemetry: dict,
    combat_telemetry: dict,
    bridge_telemetry: dict,
    collapse_shadow_telemetry: dict,
    run_config_snapshot: dict,
) -> None:
    remaining_units_a_final = int(alive_trajectory.get("A", [0])[-1]) if alive_trajectory.get("A") else 0
    remaining_units_b_final = int(alive_trajectory.get("B", [0])[-1]) if alive_trajectory.get("B") else 0
    winner_decided = (remaining_units_a_final <= 0) != (remaining_units_b_final <= 0)
    battle_report_export_allowed = (
        bool(export_battle_report)
        and int(final_state.tick) >= 100
        and winner_decided
    )

    if export_battle_report and (not battle_report_export_allowed):
        skip_reasons = []
        if int(final_state.tick) < 100:
            skip_reasons.append(f"ticks<{100} ({int(final_state.tick)})")
        if not winner_decided:
            skip_reasons.append(
                f"winner_undecided (remaining A/B={remaining_units_a_final}/{remaining_units_b_final})"
            )
        print(f"[report] battle_report_skipped={'; '.join(skip_reasons)}")
        return

    if not battle_report_export_allowed:
        return

    report_markdown = report_builder.build_battle_report_markdown(
        settings_source_path=settings_source_path,
        display_language=display_language,
        random_seed_effective=effective_random_seed,
        fleet_a_data=fleet_a_data,
        fleet_b_data=fleet_b_data,
        initial_fleet_sizes=initial_fleet_sizes,
        alive_trajectory=alive_trajectory,
        fleet_size_trajectory=fleet_size_trajectory,
        observer_telemetry=observer_telemetry,
        combat_telemetry=combat_telemetry,
        bridge_telemetry=bridge_telemetry,
        collapse_shadow_telemetry=collapse_shadow_telemetry,
        final_state=final_state,
        run_config_snapshot=run_config_snapshot,
    )
    report_date_dir = run_export_timestamp[:8]
    report_export_dir = (
        base_dir.parent / core.DEFAULT_BATTLE_REPORT_EXPORT_DIR / report_date_dir
    ).resolve()
    report_export_dir.mkdir(parents=True, exist_ok=True)
    report_filename = f"{run_export_stem}_Battle_Report_Framework_v1.0.md"
    report_output_path = report_export_dir / report_filename
    report_output_path.write_text(report_markdown, encoding="utf-8")
    print(f"[report] battle_report_exported={report_output_path}")


def _render_animation(
    *,
    arena_size: float,
    trajectory,
    alive_trajectory: dict,
    fleet_size_trajectory: dict,
    initial_fleet_sizes: dict,
    position_frames: list,
    final_state,
    fleet_a_display_name: str,
    fleet_b_display_name: str,
    fleet_a_full_name: str,
    fleet_b_full_name: str,
    fleet_a_avatar: str,
    fleet_b_avatar: str,
    fleet_a_color: str,
    fleet_b_color: str,
    auto_zoom_2d: bool,
    frame_interval_ms: int,
    effective_background_map_seed: int,
    viz_settings: dict,
    tick_plots_follow_battlefield_tick: bool,
    display_language: str,
    unit_direction_mode: str,
    show_attack_target_lines: bool,
    observer_telemetry: dict,
    observer_enabled: bool,
    plot_profile_effective: str,
    plot_smoothing_ticks: int,
    damage_per_tick: float,
    combat_telemetry: dict,
    test_mode: int,
    movement_model_effective: str,
    runtime_decision_source_effective: str,
    pre_tl_target_substrate: str,
    symmetric_movement_sync_enabled: bool,
    continuous_fr_shaping_effective: bool,
    continuous_fr_shaping_mode_effective: str,
    odw_posture_bias_enabled_effective: bool,
    odw_posture_bias_k_effective,
    odw_posture_bias_clip_delta_effective,
    v3_connect_radius_multiplier_effective: float,
    export_video_cfg: dict,
    boundary_enabled: bool,
    boundary_hard_enabled: bool,
    bridge_telemetry: dict,
) -> None:
    bridge_ticks_debug = report_builder.compute_bridge_event_ticks(
        bridge_telemetry if isinstance(bridge_telemetry, dict) else None
    )
    first_contact_tick_debug = _first_contact_tick_from_combat(
        combat_telemetry if isinstance(combat_telemetry, dict) else {}
    )

    try:
        from test_run.test_run_v1_0_viz import render_test_run
    except ModuleNotFoundError as exc:
        print(f"[viz] skipped: {exc}")
        return

    render_test_run(
        arena_size=arena_size,
        trajectory=trajectory,
        alive_trajectory=alive_trajectory,
        fleet_size_trajectory=fleet_size_trajectory,
        initial_fleet_sizes=initial_fleet_sizes,
        position_frames=position_frames,
        final_state=final_state,
        fleet_a_label=fleet_a_display_name,
        fleet_b_label=fleet_b_display_name,
        fleet_a_full_name=fleet_a_full_name,
        fleet_b_full_name=fleet_b_full_name,
        fleet_a_avatar=fleet_a_avatar,
        fleet_b_avatar=fleet_b_avatar,
        fleet_a_color=fleet_a_color,
        fleet_b_color=fleet_b_color,
        auto_zoom_2d=auto_zoom_2d,
        frame_interval_ms=frame_interval_ms,
        background_seed=effective_background_map_seed,
        viz_settings=viz_settings,
        tick_plots_follow_battlefield_tick=tick_plots_follow_battlefield_tick,
        display_language=display_language,
        unit_direction_mode=unit_direction_mode,
        show_attack_target_lines=show_attack_target_lines,
        observer_telemetry=observer_telemetry,
        observer_enabled=observer_enabled,
        plot_profile=plot_profile_effective,
        plot_smoothing_ticks=plot_smoothing_ticks,
        damage_per_tick=damage_per_tick,
        combat_telemetry=combat_telemetry,
        debug_context={
            "test_mode_label": core.TEST_MODE_LABELS.get(test_mode, "default"),
            "movement_model_effective": movement_model_effective,
            "cohesion_decision_source_effective": runtime_decision_source_effective,
            "pre_tl_target_substrate": pre_tl_target_substrate,
            "symmetric_movement_sync_enabled": symmetric_movement_sync_enabled,
            "continuous_fr_shaping_effective": continuous_fr_shaping_effective,
            "continuous_fr_shaping_mode_effective": continuous_fr_shaping_mode_effective,
            "odw_posture_bias_enabled_effective": odw_posture_bias_enabled_effective,
            "odw_posture_bias_k_effective": odw_posture_bias_k_effective,
            "odw_posture_bias_clip_delta_effective": odw_posture_bias_clip_delta_effective,
            "v3_connect_radius_multiplier_effective": v3_connect_radius_multiplier_effective,
            "plot_smoothing_ticks": plot_smoothing_ticks,
            "first_contact_tick": first_contact_tick_debug,
            "formation_cut_tick": bridge_ticks_debug.get("formation_cut_tick"),
            "pocket_formation_tick": bridge_ticks_debug.get("pocket_formation_tick"),
        },
        export_video_cfg=export_video_cfg,
        boundary_enabled=boundary_enabled,
        boundary_hard_enabled=boundary_hard_enabled,
    )


def _print_run_summary(
    *,
    effective_random_seed: int,
    effective_metatype_random_seed: int,
    effective_background_map_seed: int,
    test_mode_name: str,
    plot_profile_effective: str,
    runtime_decision_source_effective: str,
    movement_model_effective: str,
    pre_tl_target_substrate: str,
    hostile_contact_impedance_mode: str,
    animate: bool,
    observer_enabled: bool,
    export_battle_report: bool,
) -> None:
    print(
        f'[run] mode={test_mode_name} '
        f'movement={movement_model_effective} '
        f'cohesion={runtime_decision_source_effective} '
        f'plot={plot_profile_effective}'
    )
    print(
        f'[run] pre_tl={pre_tl_target_substrate} '
        f'contact_model={hostile_contact_impedance_mode} '
        f'animate={animate} observer={observer_enabled} report={export_battle_report}'
    )
    print(
        f'[run] seeds=random:{effective_random_seed} '
        f'metatype:{effective_metatype_random_seed} '
        f'background:{effective_background_map_seed}'
    )


def _build_simulation_kwargs(
    *,
    settings: dict,
    animate: bool,
    observer_enabled: bool,
    runtime_decision_source_effective: str,
    movement_model_effective: str,
    bridge_theta_split: float,
    bridge_theta_env: float,
    bridge_sustain_ticks: int,
    collapse_shadow_theta_conn_default: float,
    collapse_shadow_theta_coh_default: float,
    collapse_shadow_theta_force_default: float,
    collapse_shadow_theta_attr_default: float,
    collapse_shadow_attrition_window: int,
    collapse_shadow_sustain_ticks: int,
    collapse_shadow_min_conditions: int,
    frame_stride: int,
    attack_range: float,
    damage_per_tick: float,
    unit_spacing: float,
    fire_quality_alpha: float,
    contact_hysteresis_h: float,
    ch_enabled: bool,
    fsr_enabled: bool,
    fsr_strength: float,
    boundary_enabled: bool,
    boundary_hard_enabled: bool,
    alpha_sep: float,
    boundary_soft_strength: float,
    capture_target_directions: bool,
    print_tick_summary: bool,
    plot_diagnostics_enabled: bool,
    movement_v3a_experiment_effective: str,
    centroid_probe_scale_effective: float,
    pre_tl_target_substrate: str,
    symmetric_movement_sync_enabled: bool,
    hostile_contact_impedance_mode: str,
    hostile_contact_impedance_v2_radius_multiplier: float,
    hostile_contact_impedance_v2_repulsion_max_disp_ratio: float,
    hostile_contact_impedance_v2_forward_damping_strength: float,
    hostile_intent_unified_spacing_scale: float,
    hostile_intent_unified_spacing_strength: float,
    continuous_fr_shaping_effective: bool,
    continuous_fr_shaping_mode_effective: str,
    continuous_fr_shaping_a: float,
    continuous_fr_shaping_sigma: float,
    continuous_fr_shaping_p: float,
    continuous_fr_shaping_q: float,
    continuous_fr_shaping_beta: float,
    continuous_fr_shaping_gamma: float,
    odw_posture_bias_enabled_effective: bool,
    odw_posture_bias_k_effective: float,
    odw_posture_bias_clip_delta_effective: float,
    v3_connect_radius_multiplier_effective: float,
    v3_r_ref_radius_multiplier_effective: float,
    post_elimination_extra_ticks: int,
) -> dict:
    return {
        'steps': int(settings_api.get_run_control_setting(settings, 'max_time_steps', -1)),
        'capture_positions': animate,
        'observer_enabled': observer_enabled,
        'engine_cls': core.TestModeEngineTickSkeleton,
        'runtime_decision_source': runtime_decision_source_effective,
        'movement_model': movement_model_effective,
        'bridge_theta_split': bridge_theta_split,
        'bridge_theta_env': bridge_theta_env,
        'bridge_sustain_ticks': bridge_sustain_ticks,
        'collapse_shadow_theta_conn_default': collapse_shadow_theta_conn_default,
        'collapse_shadow_theta_coh_default': collapse_shadow_theta_coh_default,
        'collapse_shadow_theta_force_default': collapse_shadow_theta_force_default,
        'collapse_shadow_theta_attr_default': collapse_shadow_theta_attr_default,
        'collapse_shadow_attrition_window': collapse_shadow_attrition_window,
        'collapse_shadow_sustain_ticks': collapse_shadow_sustain_ticks,
        'collapse_shadow_min_conditions': collapse_shadow_min_conditions,
        'frame_stride': frame_stride,
        'attack_range': attack_range,
        'damage_per_tick': damage_per_tick,
        'separation_radius': unit_spacing,
        'fire_quality_alpha': fire_quality_alpha,
        'contact_hysteresis_h': contact_hysteresis_h,
        'ch_enabled': ch_enabled,
        'fsr_enabled': fsr_enabled,
        'fsr_strength': fsr_strength,
        'boundary_enabled': boundary_enabled,
        'boundary_hard_enabled': boundary_hard_enabled,
        'alpha_sep': alpha_sep,
        'boundary_soft_strength': boundary_soft_strength,
        'include_target_lines': capture_target_directions,
        'print_tick_summary': print_tick_summary,
        'plot_diagnostics_enabled': plot_diagnostics_enabled,
        'movement_v3a_experiment': movement_v3a_experiment_effective,
        'centroid_probe_scale': centroid_probe_scale_effective,
        'pre_tl_target_substrate': pre_tl_target_substrate,
        'symmetric_movement_sync_enabled': symmetric_movement_sync_enabled,
        'hostile_contact_impedance_mode': hostile_contact_impedance_mode,
        'hostile_contact_impedance_v2_radius_multiplier': hostile_contact_impedance_v2_radius_multiplier,
        'hostile_contact_impedance_v2_repulsion_max_disp_ratio': hostile_contact_impedance_v2_repulsion_max_disp_ratio,
        'hostile_contact_impedance_v2_forward_damping_strength': hostile_contact_impedance_v2_forward_damping_strength,
        'hostile_intent_unified_spacing_scale': hostile_intent_unified_spacing_scale,
        'hostile_intent_unified_spacing_strength': hostile_intent_unified_spacing_strength,
        'continuous_fr_shaping_enabled': continuous_fr_shaping_effective,
        'continuous_fr_shaping_mode': continuous_fr_shaping_mode_effective,
        'continuous_fr_shaping_a': continuous_fr_shaping_a,
        'continuous_fr_shaping_sigma': continuous_fr_shaping_sigma,
        'continuous_fr_shaping_p': continuous_fr_shaping_p,
        'continuous_fr_shaping_q': continuous_fr_shaping_q,
        'continuous_fr_shaping_beta': continuous_fr_shaping_beta,
        'continuous_fr_shaping_gamma': continuous_fr_shaping_gamma,
        'odw_posture_bias_enabled': odw_posture_bias_enabled_effective,
        'odw_posture_bias_k': odw_posture_bias_k_effective,
        'odw_posture_bias_clip_delta': odw_posture_bias_clip_delta_effective,
        'v3_connect_radius_multiplier': v3_connect_radius_multiplier_effective,
        'v3_r_ref_radius_multiplier': v3_r_ref_radius_multiplier_effective,
        'post_elimination_extra_ticks': post_elimination_extra_ticks,
    }


def _build_run_config_snapshot(
    *,
    settings: dict,
    fleet_a_size: int,
    fleet_b_size: int,
    fleet_a_aspect_ratio: float,
    fleet_b_aspect_ratio: float,
    fleet_a_origin_x: float,
    fleet_a_origin_y: float,
    fleet_b_origin_x: float,
    fleet_b_origin_y: float,
    fleet_a_facing_angle_deg: float,
    fleet_b_facing_angle_deg: float,
    test_mode: int,
    test_mode_name: str,
    effective_random_seed: int,
    effective_background_map_seed: int,
    effective_metatype_random_seed: int,
    runtime_decision_source_effective: str,
    movement_model_effective: str,
    movement_v3a_experiment_effective: str,
    centroid_probe_scale_effective: float,
    pre_tl_target_substrate: str,
    symmetric_movement_sync_enabled: bool,
    hostile_contact_impedance_mode: str,
    hostile_contact_impedance_v2_radius_multiplier: float,
    hostile_contact_impedance_v2_repulsion_max_disp_ratio: float,
    hostile_contact_impedance_v2_forward_damping_strength: float,
    hostile_intent_unified_spacing_scale: float,
    hostile_intent_unified_spacing_strength: float,
    continuous_fr_shaping_effective: bool,
    continuous_fr_shaping_mode_effective: str,
    continuous_fr_shaping_a: float,
    continuous_fr_shaping_sigma: float,
    continuous_fr_shaping_p: float,
    continuous_fr_shaping_q: float,
    continuous_fr_shaping_beta: float,
    continuous_fr_shaping_gamma: float,
    odw_posture_bias_enabled_effective: bool,
    odw_posture_bias_k_effective: float,
    odw_posture_bias_clip_delta_effective: float,
    attack_range: float,
    unit_spacing: float,
    arena_size: float,
    max_time_steps_effective: int,
    unit_speed: float,
    damage_per_tick: float,
    ch_enabled: bool,
    contact_hysteresis_h: float,
    fsr_enabled: bool,
    fsr_strength: float,
    boundary_enabled: bool,
    boundary_soft_strength: float,
    boundary_hard_enabled: bool,
    boundary_hard_enabled_effective: bool,
    alpha_sep: float,
    v3_connect_radius_multiplier_effective: float,
    v3_r_ref_radius_multiplier_effective: float,
    bridge_theta_split: float,
    bridge_theta_env: float,
    bridge_sustain_ticks: int,
    strategic_inflection_sustain_ticks: int,
    tactical_swing_sustain_ticks: int,
    tactical_swing_min_amplitude: float,
    tactical_swing_min_gap_ticks: int,
    collapse_shadow_theta_conn_default: float,
    collapse_shadow_theta_coh_default: float,
    collapse_shadow_theta_force_default: float,
    collapse_shadow_theta_attr_default: float,
    collapse_shadow_attrition_window: int,
    collapse_shadow_sustain_ticks: int,
    collapse_shadow_min_conditions: int,
) -> dict:
    return {
        'initial_units_per_side': int(fleet_a_size) if fleet_a_size == fleet_b_size else int(max(fleet_a_size, fleet_b_size)),
        'initial_units_a': int(fleet_a_size),
        'initial_units_b': int(fleet_b_size),
        'initial_fleet_a_aspect_ratio': fleet_a_aspect_ratio,
        'initial_fleet_b_aspect_ratio': fleet_b_aspect_ratio,
        'initial_fleet_a_origin_x': fleet_a_origin_x,
        'initial_fleet_a_origin_y': fleet_a_origin_y,
        'initial_fleet_b_origin_x': fleet_b_origin_x,
        'initial_fleet_b_origin_y': fleet_b_origin_y,
        'initial_fleet_a_facing_angle_deg': fleet_a_facing_angle_deg,
        'initial_fleet_b_facing_angle_deg': fleet_b_facing_angle_deg,
        'test_mode': test_mode,
        'test_mode_label': test_mode_name,
        'metatype_settings_path': str(
            settings_api.get_runtime_metatype_setting(
                settings, 'settings_path', core.DEFAULT_METATYPE_SETTINGS_PATH
            )
        ),
        'random_seed_effective': int(effective_random_seed),
        'background_map_seed_effective': int(effective_background_map_seed),
        'metatype_random_seed_effective': int(effective_metatype_random_seed),
        'runtime_decision_source_effective': runtime_decision_source_effective,
        'collapse_decision_source_effective': runtime_decision_source_effective,
        'movement_model_effective': movement_model_effective,
        'movement_v3a_experiment_effective': movement_v3a_experiment_effective if movement_model_effective == 'v3a' else 'N/A',
        'centroid_probe_scale_effective': centroid_probe_scale_effective if movement_model_effective == 'v3a' else 'N/A',
        'pre_tl_target_substrate': pre_tl_target_substrate if movement_model_effective == 'v3a' else 'N/A',
        'symmetric_movement_sync_enabled': symmetric_movement_sync_enabled if movement_model_effective == 'v3a' else 'N/A',
        'hostile_contact_impedance_mode': hostile_contact_impedance_mode,
        'hostile_contact_impedance_v2_radius_multiplier': hostile_contact_impedance_v2_radius_multiplier,
        'hostile_contact_impedance_v2_repulsion_max_disp_ratio': hostile_contact_impedance_v2_repulsion_max_disp_ratio,
        'hostile_contact_impedance_v2_forward_damping_strength': hostile_contact_impedance_v2_forward_damping_strength,
        'hostile_intent_unified_spacing_scale': hostile_intent_unified_spacing_scale,
        'hostile_intent_unified_spacing_strength': hostile_intent_unified_spacing_strength,
        'continuous_fr_shaping_enabled_effective': continuous_fr_shaping_effective if movement_model_effective == 'v3a' else 'N/A',
        'continuous_fr_shaping_mode_effective': continuous_fr_shaping_mode_effective if movement_model_effective == 'v3a' else 'N/A',
        'continuous_fr_shaping_a_effective': continuous_fr_shaping_a if continuous_fr_shaping_effective else 0.0,
        'continuous_fr_shaping_sigma_effective': continuous_fr_shaping_sigma if continuous_fr_shaping_effective else 0.0,
        'continuous_fr_shaping_p_effective': continuous_fr_shaping_p if continuous_fr_shaping_effective else 0.0,
        'continuous_fr_shaping_q_effective': continuous_fr_shaping_q if continuous_fr_shaping_effective else 0.0,
        'continuous_fr_shaping_beta_effective': continuous_fr_shaping_beta if continuous_fr_shaping_effective else 0.0,
        'continuous_fr_shaping_gamma_effective': continuous_fr_shaping_gamma if continuous_fr_shaping_effective else 0.0,
        'odw_posture_bias_enabled_effective': odw_posture_bias_enabled_effective if movement_model_effective == 'v3a' else 'N/A',
        'odw_posture_bias_k_effective': odw_posture_bias_k_effective if movement_model_effective == 'v3a' else 'N/A',
        'odw_posture_bias_clip_delta_effective': odw_posture_bias_clip_delta_effective if movement_model_effective == 'v3a' else 'N/A',
        'attack_range': attack_range,
        'min_unit_spacing': unit_spacing,
        'arena_size': arena_size,
        'max_time_steps_effective': max_time_steps_effective,
        'unit_speed': unit_speed,
        'damage_per_tick': damage_per_tick,
        'ch_enabled': ch_enabled,
        'contact_hysteresis_h': contact_hysteresis_h,
        'fsr_enabled': fsr_enabled,
        'fsr_strength': fsr_strength,
        'boundary_enabled': boundary_enabled,
        'boundary_soft_strength': boundary_soft_strength,
        'boundary_hard_enabled': boundary_hard_enabled,
        'boundary_hard_enabled_effective': boundary_hard_enabled_effective,
        'alpha_sep': alpha_sep,
        'v3_connect_radius_multiplier_effective': v3_connect_radius_multiplier_effective,
        'v3_r_ref_radius_multiplier_effective': v3_r_ref_radius_multiplier_effective,
        'bridge_theta_split': bridge_theta_split,
        'bridge_theta_env': bridge_theta_env,
        'bridge_sustain_ticks': bridge_sustain_ticks,
        'strategic_inflection_sustain_ticks': strategic_inflection_sustain_ticks,
        'tactical_swing_sustain_ticks': tactical_swing_sustain_ticks,
        'tactical_swing_min_amplitude': tactical_swing_min_amplitude,
        'tactical_swing_min_gap_ticks': tactical_swing_min_gap_ticks,
        'collapse_shadow_theta_conn_default': collapse_shadow_theta_conn_default,
        'collapse_shadow_theta_coh_default': collapse_shadow_theta_coh_default,
        'collapse_shadow_theta_force_default': collapse_shadow_theta_force_default,
        'collapse_shadow_theta_attr_default': collapse_shadow_theta_attr_default,
        'collapse_shadow_attrition_window': collapse_shadow_attrition_window,
        'collapse_shadow_sustain_ticks': collapse_shadow_sustain_ticks,
        'collapse_shadow_min_conditions': collapse_shadow_min_conditions,
    }


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    settings = settings_api.load_layered_test_run_settings(base_dir)
    viz_settings = settings_api.load_json_file(base_dir / 'test_run_v1_0.viz.settings.json')
    post_elimination_extra_ticks = max(0, int(viz_settings.get('post_elimination_extra_ticks', 10)))
    archetypes = settings_api.load_json_file(core.PROJECT_ROOT / 'archetypes' / 'archetypes_v1_5.json')
    metatype_settings = core.load_metatype_settings(base_dir, settings)
    random_seed = int(settings_api.get_run_control_setting(settings, 'random_seed', -1))
    metatype_random_seed = int(settings_api.get_runtime_metatype_setting(settings, 'random_seed', random_seed))
    background_map_seed = int(settings_api.get_battlefield_setting(settings, 'background_map_seed', -1))
    effective_random_seed = core.resolve_effective_seed(random_seed)
    effective_metatype_random_seed = core.resolve_effective_seed(metatype_random_seed)
    effective_background_map_seed = core.resolve_effective_seed(background_map_seed)
    archetype_rng = random.Random(int(effective_metatype_random_seed))
    fleet_a_data = core.resolve_fleet_archetype_data(archetypes, metatype_settings, settings_api.get_fleet_setting(settings, 'fleet_a_archetype_id', 'default'), rng=archetype_rng)
    fleet_b_data = core.resolve_fleet_archetype_data(archetypes, metatype_settings, settings_api.get_fleet_setting(settings, 'fleet_b_archetype_id', 'default'), rng=archetype_rng)
    fleet_a_params = core.to_personality_parameters(fleet_a_data)
    fleet_b_params = core.to_personality_parameters(fleet_b_data)
    fleet_a_color, fleet_b_color = core.resolve_fleet_plot_colors(fleet_a_data, fleet_b_data)
    display_language = str(settings_api.get_visualization_setting(settings, 'display_language', 'EN')).upper()
    if display_language not in ('EN', 'ZH'):
        display_language = 'EN'
    fleet_a_display_name = core.resolve_display_name(fleet_a_data, display_language)
    fleet_b_display_name = core.resolve_display_name(fleet_b_data, display_language)
    fleet_a_full_name = report_builder.resolve_name_with_fallback(fleet_a_data, display_language, True, 'A')
    fleet_b_full_name = report_builder.resolve_name_with_fallback(fleet_b_data, display_language, True, 'B')
    fleet_a_avatar = core.resolve_avatar_with_fallback(fleet_a_data, core.DEFAULT_AVATAR_A)
    fleet_b_avatar = core.resolve_avatar_with_fallback(fleet_b_data, core.DEFAULT_AVATAR_B)
    fleet_a_size = int(settings_api.get_fleet_setting(settings, 'initial_fleet_a_size', 100))
    fleet_b_size = int(settings_api.get_fleet_setting(settings, 'initial_fleet_b_size', 100))
    fleet_a_aspect_ratio = float(settings_api.get_fleet_setting(settings, 'initial_fleet_a_aspect_ratio', 2.0))
    fleet_b_aspect_ratio = float(settings_api.get_fleet_setting(settings, 'initial_fleet_b_aspect_ratio', 2.0))
    unit_spacing = float(settings_api.get_runtime_setting(settings, 'min_unit_spacing', 1.0))
    arena_size = float(settings_api.get_battlefield_setting(settings, 'arena_size', 200.0))
    spawn_margin = max(1.0, arena_size * core.DEFAULT_SPAWN_MARGIN_RATIO)
    fleet_a_origin_x, fleet_a_origin_y = core._resolve_point_setting(settings, array_key='initial_fleet_a_origin_xy', x_key='initial_fleet_a_origin_x', y_key='initial_fleet_a_origin_y', default_x=spawn_margin, default_y=spawn_margin)
    fleet_b_origin_x, fleet_b_origin_y = core._resolve_point_setting(settings, array_key='initial_fleet_b_origin_xy', x_key='initial_fleet_b_origin_x', y_key='initial_fleet_b_origin_y', default_x=arena_size - spawn_margin, default_y=arena_size - spawn_margin)
    fleet_a_facing_angle_deg = float(settings_api.get_fleet_setting(settings, 'initial_fleet_a_facing_angle_deg', 45.0))
    fleet_b_facing_angle_deg = float(settings_api.get_fleet_setting(settings, 'initial_fleet_b_facing_angle_deg', 225.0))
    _raise_if_invalid_initial_geometry(
        fleet_a_size=fleet_a_size,
        fleet_b_size=fleet_b_size,
        fleet_a_aspect_ratio=fleet_a_aspect_ratio,
        fleet_b_aspect_ratio=fleet_b_aspect_ratio,
        unit_spacing=unit_spacing,
    )
    unit_speed = float(settings_api.get_unit_setting(settings, 'unit_speed', 1.0))
    unit_max_hit_points = float(settings_api.get_unit_setting(settings, 'unit_max_hit_points', 100.0))
    state = experiments.build_initial_state(fleet_a_params=fleet_a_params, fleet_b_params=fleet_b_params, fleet_a_size=fleet_a_size, fleet_b_size=fleet_b_size, fleet_a_aspect_ratio=fleet_a_aspect_ratio, fleet_b_aspect_ratio=fleet_b_aspect_ratio, unit_spacing=unit_spacing, unit_speed=unit_speed, unit_max_hit_points=unit_max_hit_points, arena_size=arena_size, fleet_a_origin_x=fleet_a_origin_x, fleet_a_origin_y=fleet_a_origin_y, fleet_b_origin_x=fleet_b_origin_x, fleet_b_origin_y=fleet_b_origin_y, fleet_a_facing_angle_deg=fleet_a_facing_angle_deg, fleet_b_facing_angle_deg=fleet_b_facing_angle_deg)
    initial_fleet_sizes = {}
    for fleet_id, fleet in state.fleets.items():
        fleet_size_hp = 0.0
        for unit_id in fleet.unit_ids:
            if unit_id in state.units:
                fleet_size_hp += max(0.0, float(state.units[unit_id].hit_points))
        initial_fleet_sizes[fleet_id] = fleet_size_hp
    animate = bool(settings_api.get_visualization_setting(settings, 'animate', True))
    auto_zoom_2d = bool(settings_api.get_visualization_setting(settings, 'auto_zoom_2d', False))
    frame_stride = core.DEFAULT_FRAME_STRIDE
    base_frame_interval_ms = _require_int_at_least(
        'visualization.animation_frame_interval_ms',
        settings_api.get_visualization_setting(settings, 'animation_frame_interval_ms', 100),
        1,
    )
    animation_play_speed = _require_positive_float(
        'visualization.animation_play_speed',
        settings_api.get_visualization_setting(settings, 'animation_play_speed', 1.0),
    )
    frame_interval_ms = max(1, int(round(base_frame_interval_ms / animation_play_speed)))
    attack_range = float(settings_api.get_unit_setting(settings, 'attack_range', settings_api.get_runtime_setting(settings, 'attack_range', 3.0)))
    damage_per_tick = float(settings_api.get_unit_setting(settings, 'damage_per_tick', settings_api.get_runtime_setting(settings, 'damage_per_tick', 1.0)))
    fire_quality_alpha = float(settings_api.get_runtime_setting(settings, 'fire_quality_alpha', 0.1))
    contact_hysteresis_h = float(settings_api.get_runtime_setting(settings, 'contact_hysteresis_h', 0.1))
    fsr_strength = float(settings_api.get_runtime_setting(settings, 'fsr_strength', 0.0))
    alpha_sep = _require_nonnegative_float(
        'runtime.alpha_sep',
        settings_api.get_runtime_setting(settings, 'alpha_sep', 0.6),
    )
    movement_model_requested, movement_model_effective = core.resolve_movement_model(settings_api.get_runtime_setting(settings, 'movement_model', 'baseline'))
    movement_v3a_experiment_effective = _require_choice(
        'runtime.movement_v3a_experiment',
        settings_api.get_runtime_setting(settings, 'movement_v3a_experiment', core.V3A_EXPERIMENT_BASE),
        core.V3A_EXPERIMENT_LABELS,
    )
    symmetric_movement_sync_enabled = bool(settings_api.get_runtime_setting(settings, 'symmetric_movement_sync_enabled', True))
    hostile_contact_impedance_mode = _require_choice(
        'runtime.test_only.hostile_contact_impedance.active_mode',
        settings_api.get_contact_model_test_setting(settings, ('active_mode',), core.HOSTILE_CONTACT_IMPEDANCE_MODE_DEFAULT),
        core.HOSTILE_CONTACT_IMPEDANCE_MODE_LABELS,
    )
    hostile_contact_impedance_v2_radius_multiplier = _require_positive_float(
        'runtime.test_only.hostile_contact_impedance.hybrid_v2.radius_multiplier',
        settings_api.get_contact_model_test_setting(settings, ('hybrid_v2', 'radius_multiplier'), core.HOSTILE_CONTACT_IMPEDANCE_V2_RADIUS_MULTIPLIER_DEFAULT),
    )
    hostile_contact_impedance_v2_repulsion_max_disp_ratio = _require_nonnegative_float(
        'runtime.test_only.hostile_contact_impedance.hybrid_v2.repulsion_max_disp_ratio',
        settings_api.get_contact_model_test_setting(settings, ('hybrid_v2', 'repulsion_max_disp_ratio'), core.HOSTILE_CONTACT_IMPEDANCE_V2_REPULSION_MAX_DISP_RATIO_DEFAULT),
    )
    hostile_contact_impedance_v2_forward_damping_strength = _require_unit_interval_float(
        'runtime.test_only.hostile_contact_impedance.hybrid_v2.forward_damping_strength',
        settings_api.get_contact_model_test_setting(settings, ('hybrid_v2', 'forward_damping_strength'), core.HOSTILE_CONTACT_IMPEDANCE_V2_FORWARD_DAMPING_STRENGTH_DEFAULT),
    )
    hostile_intent_unified_spacing_scale = _require_positive_float(
        'runtime.test_only.hostile_contact_impedance.intent_unified_spacing_v1.scale',
        settings_api.get_contact_model_test_setting(settings, ('intent_unified_spacing_v1', 'scale'), core.HOSTILE_INTENT_UNIFIED_SPACING_SCALE_DEFAULT),
    )
    hostile_intent_unified_spacing_strength = _require_unit_interval_float(
        'runtime.test_only.hostile_contact_impedance.intent_unified_spacing_v1.strength',
        settings_api.get_contact_model_test_setting(settings, ('intent_unified_spacing_v1', 'strength'), core.HOSTILE_INTENT_UNIFIED_SPACING_STRENGTH_DEFAULT),
    )
    centroid_probe_scale = _require_unit_interval_float(
        'runtime.centroid_probe_scale',
        settings_api.get_runtime_setting(settings, 'centroid_probe_scale', 1.0),
    )
    pre_tl_target_substrate = _require_choice(
        'runtime.pre_tl_target_substrate',
        settings_api.get_runtime_setting(settings, 'pre_tl_target_substrate', core.PRE_TL_TARGET_SUBSTRATE_DEFAULT),
        core.PRE_TL_TARGET_SUBSTRATE_LABELS,
    )
    if movement_model_effective != 'v3a' or movement_v3a_experiment_effective not in {core.V3A_EXPERIMENT_PRECONTACT_CENTROID_PROBE}:
        centroid_probe_scale_effective = 1.0
    else:
        centroid_probe_scale_effective = centroid_probe_scale
    continuous_fr_shaping_enabled = bool(settings_api.get_runtime_setting(settings, 'continuous_fr_shaping_enabled', False))
    continuous_fr_shaping_mode = _require_choice(
        'runtime.continuous_fr_shaping_mode',
        settings_api.get_runtime_setting(settings, 'continuous_fr_shaping_mode', core.CONTINUOUS_FR_SHAPING_OFF),
        core.CONTINUOUS_FR_SHAPING_LABELS,
    )
    continuous_fr_shaping_a = _require_nonnegative_float(
        'runtime.continuous_fr_shaping_a',
        settings_api.get_runtime_setting(settings, 'continuous_fr_shaping_a', 0.0),
    )
    continuous_fr_shaping_sigma = _require_positive_float(
        'runtime.continuous_fr_shaping_sigma',
        settings_api.get_runtime_setting(settings, 'continuous_fr_shaping_sigma', 0.15),
    )
    continuous_fr_shaping_p = _require_nonnegative_float(
        'runtime.continuous_fr_shaping_p',
        settings_api.get_runtime_setting(settings, 'continuous_fr_shaping_p', 1.0),
    )
    continuous_fr_shaping_q = _require_nonnegative_float(
        'runtime.continuous_fr_shaping_q',
        settings_api.get_runtime_setting(settings, 'continuous_fr_shaping_q', 1.0),
    )
    continuous_fr_shaping_beta = _require_nonnegative_float(
        'runtime.continuous_fr_shaping_beta',
        settings_api.get_runtime_setting(settings, 'continuous_fr_shaping_beta', 0.0),
    )
    continuous_fr_shaping_gamma = _require_nonnegative_float(
        'runtime.continuous_fr_shaping_gamma',
        settings_api.get_runtime_setting(settings, 'continuous_fr_shaping_gamma', 0.0),
    )
    continuous_fr_shaping_effective = movement_model_effective == 'v3a' and movement_v3a_experiment_effective == core.V3A_EXPERIMENT_PRECONTACT_CENTROID_PROBE and continuous_fr_shaping_enabled and (continuous_fr_shaping_mode != core.CONTINUOUS_FR_SHAPING_OFF) and (continuous_fr_shaping_a > 0.0)
    continuous_fr_shaping_mode_effective = continuous_fr_shaping_mode if continuous_fr_shaping_effective else core.CONTINUOUS_FR_SHAPING_OFF
    odw_posture_bias_enabled = bool(settings_api.get_runtime_setting(settings, 'odw_posture_bias_enabled', False))
    odw_posture_bias_k = _require_nonnegative_float(
        'runtime.odw_posture_bias_k',
        settings_api.get_runtime_setting(settings, 'odw_posture_bias_k', 0.3),
    )
    odw_posture_bias_clip_delta = _require_nonnegative_float(
        'runtime.odw_posture_bias_clip_delta',
        settings_api.get_runtime_setting(settings, 'odw_posture_bias_clip_delta', 0.2),
    )
    if movement_model_effective != 'v3a':
        odw_posture_bias_enabled_effective = False
        odw_posture_bias_k_effective = 0.0
        odw_posture_bias_clip_delta_effective = 0.2
    else:
        odw_posture_bias_enabled_effective = odw_posture_bias_enabled
        odw_posture_bias_k_effective = odw_posture_bias_k if odw_posture_bias_enabled_effective else 0.0
        odw_posture_bias_clip_delta_effective = odw_posture_bias_clip_delta if odw_posture_bias_enabled_effective else 0.2
    bridge_theta_split = float(settings_api.get_event_bridge_setting(settings, 'theta_split', core.BRIDGE_THETA_SPLIT_DEFAULT))
    bridge_theta_env = float(settings_api.get_event_bridge_setting(settings, 'theta_env', core.BRIDGE_THETA_ENV_DEFAULT))
    bridge_sustain_ticks = _require_int_at_least(
        'runtime.events.bridge.sustain_ticks',
        settings_api.get_event_bridge_setting(settings, 'sustain_ticks', core.BRIDGE_SUSTAIN_TICKS_DEFAULT),
        1,
    )
    collapse_shadow_theta_conn_default = float(settings_api.get_collapse_shadow_setting(settings, 'theta_conn_default', core.COLLAPSE_V2_SHADOW_THETA_CONN_DEFAULT))
    collapse_shadow_theta_coh_default = float(settings_api.get_collapse_shadow_setting(settings, 'theta_coh_default', core.COLLAPSE_V2_SHADOW_THETA_COH_DEFAULT))
    collapse_shadow_theta_force_default = float(settings_api.get_collapse_shadow_setting(settings, 'theta_force_default', core.COLLAPSE_V2_SHADOW_THETA_FORCE_DEFAULT))
    collapse_shadow_theta_attr_default = float(settings_api.get_collapse_shadow_setting(settings, 'theta_attr_default', core.COLLAPSE_V2_SHADOW_THETA_ATTR_DEFAULT))
    collapse_shadow_attrition_window = _require_int_at_least(
        'runtime.collapse_shadow.attrition_window',
        settings_api.get_collapse_shadow_setting(settings, 'attrition_window', core.COLLAPSE_V2_SHADOW_ATTRITION_WINDOW_DEFAULT),
        1,
    )
    collapse_shadow_sustain_ticks = _require_int_at_least(
        'runtime.collapse_shadow.sustain_ticks',
        settings_api.get_collapse_shadow_setting(settings, 'sustain_ticks', core.COLLAPSE_V2_SHADOW_SUSTAIN_TICKS_DEFAULT),
        1,
    )
    collapse_shadow_min_conditions = _require_int_between(
        'runtime.collapse_shadow.min_conditions',
        settings_api.get_collapse_shadow_setting(settings, 'min_conditions', core.COLLAPSE_V2_SHADOW_MIN_CONDITIONS_DEFAULT),
        1,
        4,
    )
    strategic_inflection_sustain_ticks = _require_int_at_least(
        'runtime.report_inference.strategic_inflection_sustain_ticks',
        settings_api.get_report_inference_setting(settings, 'strategic_inflection_sustain_ticks', core.STRATEGIC_INFLECTION_SUSTAIN_TICKS),
        1,
    )
    tactical_swing_sustain_ticks = _require_int_at_least(
        'runtime.report_inference.tactical_swing_sustain_ticks',
        settings_api.get_report_inference_setting(settings, 'tactical_swing_sustain_ticks', core.TACTICAL_SWING_SUSTAIN_TICKS),
        1,
    )
    tactical_swing_min_amplitude = _require_nonnegative_float(
        'runtime.report_inference.tactical_swing_min_amplitude',
        settings_api.get_report_inference_setting(settings, 'tactical_swing_min_amplitude', core.TACTICAL_SWING_MIN_AMPLITUDE),
    )
    tactical_swing_min_gap_ticks = _require_int_at_least(
        'runtime.report_inference.tactical_swing_min_gap_ticks',
        settings_api.get_report_inference_setting(settings, 'tactical_swing_min_gap_ticks', core.TACTICAL_SWING_MIN_GAP_TICKS),
        0,
    )
    ch_enabled = contact_hysteresis_h > 0.0
    fsr_enabled = fsr_strength > 0.0
    boundary_enabled = bool(settings_api.get_runtime_setting(settings, 'boundary_enabled', False))
    boundary_hard_enabled = bool(settings_api.get_runtime_setting(settings, 'boundary_hard_enabled', True))
    boundary_soft_strength = _require_nonnegative_float(
        'runtime.boundary_soft_strength',
        settings_api.get_runtime_setting(settings, 'boundary_soft_strength', 1.0),
    )
    boundary_hard_enabled_effective = bool(boundary_enabled) and bool(boundary_hard_enabled)
    unit_direction_mode = _require_choice(
        'visualization.vector_display_mode',
        settings_api.get_visualization_setting(settings, 'vector_display_mode', settings_api.get_visualization_setting(settings, 'unit_direction_mode', 'effective')),
        {'effective', 'free', 'attack', 'composite'},
    )
    show_attack_target_lines = bool(settings_api.get_visualization_setting(settings, 'show_attack_target_lines', False))
    tick_plots_follow_battlefield_tick = bool(settings_api.get_visualization_setting(settings, 'tick_plots_follow_battlefield_tick', False))
    print_tick_summary = bool(settings_api.get_visualization_setting(settings, 'print_tick_summary', True))
    plot_smoothing_ticks = _require_int_at_least(
        'visualization.plot_smoothing_ticks',
        settings_api.get_visualization_setting(settings, 'plot_smoothing_ticks', 5),
        1,
    )
    test_mode = core.parse_test_mode(settings_api.get_run_control_setting(settings, 'test_mode', 0))
    test_mode_name = core.test_mode_label(test_mode)
    observer_enabled = test_mode >= 1
    export_battle_report = test_mode >= 1
    runtime_decision_source_requested, runtime_decision_source_effective = core.resolve_runtime_decision_source(settings_api.get_runtime_setting(settings, 'cohesion_decision_source', 'baseline'), test_mode)
    v3_connect_radius_multiplier = _require_positive_float(
        'runtime.v3_connect_radius_multiplier',
        settings_api.get_runtime_setting(settings, 'v3_connect_radius_multiplier', core.BASELINE_V3_CONNECT_RADIUS_MULTIPLIER),
    )
    v3_r_ref_radius_multiplier = _require_positive_float(
        'runtime.v3_r_ref_radius_multiplier',
        settings_api.get_runtime_setting(settings, 'v3_r_ref_radius_multiplier', core.BASELINE_V3_R_REF_RADIUS_MULTIPLIER),
    )
    if runtime_decision_source_effective == 'v3_test':
        v3_connect_radius_multiplier_effective = v3_connect_radius_multiplier
        v3_r_ref_radius_multiplier_effective = v3_r_ref_radius_multiplier
    else:
        v3_connect_radius_multiplier_effective = 1.0
        v3_r_ref_radius_multiplier_effective = 1.0
    plot_profile_requested, plot_profile_effective = core.resolve_plot_profile(settings_api.get_visualization_setting(settings, 'plot_profile', 'auto'), test_mode, runtime_decision_source_requested, runtime_decision_source_effective)
    plot_diagnostics_enabled = bool(animate) or bool(observer_enabled)
    _print_run_summary(
        effective_random_seed=effective_random_seed,
        effective_metatype_random_seed=effective_metatype_random_seed,
        effective_background_map_seed=effective_background_map_seed,
        test_mode_name=test_mode_name,
        plot_profile_effective=plot_profile_effective,
        runtime_decision_source_effective=runtime_decision_source_effective,
        movement_model_effective=movement_model_effective,
        pre_tl_target_substrate=pre_tl_target_substrate,
        hostile_contact_impedance_mode=hostile_contact_impedance_mode,
        animate=animate,
        observer_enabled=observer_enabled,
        export_battle_report=export_battle_report,
    )
    run_export_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    run_export_stem = f'{core.DEFAULT_BATTLE_REPORT_TOPIC}_{run_export_timestamp}'
    export_video_cfg = _prepare_export_video_cfg(
        viz_settings,
        base_dir,
        run_export_stem,
    )
    capture_target_directions = show_attack_target_lines or unit_direction_mode in {'attack', 'composite'}
    simulation_kwargs = _build_simulation_kwargs(
        settings=settings,
        animate=animate,
        observer_enabled=observer_enabled,
        runtime_decision_source_effective=runtime_decision_source_effective,
        movement_model_effective=movement_model_effective,
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
        frame_stride=frame_stride,
        attack_range=attack_range,
        damage_per_tick=damage_per_tick,
        unit_spacing=unit_spacing,
        fire_quality_alpha=fire_quality_alpha,
        contact_hysteresis_h=contact_hysteresis_h,
        ch_enabled=ch_enabled,
        fsr_enabled=fsr_enabled,
        fsr_strength=fsr_strength,
        boundary_enabled=boundary_enabled,
        boundary_hard_enabled=boundary_hard_enabled,
        alpha_sep=alpha_sep,
        boundary_soft_strength=boundary_soft_strength,
        capture_target_directions=capture_target_directions,
        print_tick_summary=print_tick_summary,
        plot_diagnostics_enabled=plot_diagnostics_enabled,
        movement_v3a_experiment_effective=movement_v3a_experiment_effective,
        centroid_probe_scale_effective=centroid_probe_scale_effective,
        pre_tl_target_substrate=pre_tl_target_substrate,
        symmetric_movement_sync_enabled=symmetric_movement_sync_enabled,
        hostile_contact_impedance_mode=hostile_contact_impedance_mode,
        hostile_contact_impedance_v2_radius_multiplier=hostile_contact_impedance_v2_radius_multiplier,
        hostile_contact_impedance_v2_repulsion_max_disp_ratio=hostile_contact_impedance_v2_repulsion_max_disp_ratio,
        hostile_contact_impedance_v2_forward_damping_strength=hostile_contact_impedance_v2_forward_damping_strength,
        hostile_intent_unified_spacing_scale=hostile_intent_unified_spacing_scale,
        hostile_intent_unified_spacing_strength=hostile_intent_unified_spacing_strength,
        continuous_fr_shaping_effective=continuous_fr_shaping_effective,
        continuous_fr_shaping_mode_effective=continuous_fr_shaping_mode_effective,
        continuous_fr_shaping_a=continuous_fr_shaping_a,
        continuous_fr_shaping_sigma=continuous_fr_shaping_sigma,
        continuous_fr_shaping_p=continuous_fr_shaping_p,
        continuous_fr_shaping_q=continuous_fr_shaping_q,
        continuous_fr_shaping_beta=continuous_fr_shaping_beta,
        continuous_fr_shaping_gamma=continuous_fr_shaping_gamma,
        odw_posture_bias_enabled_effective=odw_posture_bias_enabled_effective,
        odw_posture_bias_k_effective=odw_posture_bias_k_effective,
        odw_posture_bias_clip_delta_effective=odw_posture_bias_clip_delta_effective,
        v3_connect_radius_multiplier_effective=v3_connect_radius_multiplier_effective,
        v3_r_ref_radius_multiplier_effective=v3_r_ref_radius_multiplier_effective,
        post_elimination_extra_ticks=post_elimination_extra_ticks,
    )
    final_state, trajectory, alive_trajectory, fleet_size_trajectory, observer_telemetry, combat_telemetry, bridge_telemetry, collapse_shadow_telemetry, position_frames = experiments.run_simulation(
        initial_state=state,
        **simulation_kwargs,
    )
    if not animate:
        position_frames = []
    max_time_steps_effective = int(final_state.tick)
    run_config_snapshot = _build_run_config_snapshot(
        settings=settings,
        fleet_a_size=fleet_a_size,
        fleet_b_size=fleet_b_size,
        fleet_a_aspect_ratio=fleet_a_aspect_ratio,
        fleet_b_aspect_ratio=fleet_b_aspect_ratio,
        fleet_a_origin_x=fleet_a_origin_x,
        fleet_a_origin_y=fleet_a_origin_y,
        fleet_b_origin_x=fleet_b_origin_x,
        fleet_b_origin_y=fleet_b_origin_y,
        fleet_a_facing_angle_deg=fleet_a_facing_angle_deg,
        fleet_b_facing_angle_deg=fleet_b_facing_angle_deg,
        test_mode=test_mode,
        test_mode_name=test_mode_name,
        effective_random_seed=effective_random_seed,
        effective_background_map_seed=effective_background_map_seed,
        effective_metatype_random_seed=effective_metatype_random_seed,
        runtime_decision_source_effective=runtime_decision_source_effective,
        movement_model_effective=movement_model_effective,
        movement_v3a_experiment_effective=movement_v3a_experiment_effective,
        centroid_probe_scale_effective=centroid_probe_scale_effective,
        pre_tl_target_substrate=pre_tl_target_substrate,
        symmetric_movement_sync_enabled=symmetric_movement_sync_enabled,
        hostile_contact_impedance_mode=hostile_contact_impedance_mode,
        hostile_contact_impedance_v2_radius_multiplier=hostile_contact_impedance_v2_radius_multiplier,
        hostile_contact_impedance_v2_repulsion_max_disp_ratio=hostile_contact_impedance_v2_repulsion_max_disp_ratio,
        hostile_contact_impedance_v2_forward_damping_strength=hostile_contact_impedance_v2_forward_damping_strength,
        hostile_intent_unified_spacing_scale=hostile_intent_unified_spacing_scale,
        hostile_intent_unified_spacing_strength=hostile_intent_unified_spacing_strength,
        continuous_fr_shaping_effective=continuous_fr_shaping_effective,
        continuous_fr_shaping_mode_effective=continuous_fr_shaping_mode_effective,
        continuous_fr_shaping_a=continuous_fr_shaping_a,
        continuous_fr_shaping_sigma=continuous_fr_shaping_sigma,
        continuous_fr_shaping_p=continuous_fr_shaping_p,
        continuous_fr_shaping_q=continuous_fr_shaping_q,
        continuous_fr_shaping_beta=continuous_fr_shaping_beta,
        continuous_fr_shaping_gamma=continuous_fr_shaping_gamma,
        odw_posture_bias_enabled_effective=odw_posture_bias_enabled_effective,
        odw_posture_bias_k_effective=odw_posture_bias_k_effective,
        odw_posture_bias_clip_delta_effective=odw_posture_bias_clip_delta_effective,
        attack_range=attack_range,
        unit_spacing=unit_spacing,
        arena_size=arena_size,
        max_time_steps_effective=max_time_steps_effective,
        unit_speed=unit_speed,
        damage_per_tick=damage_per_tick,
        ch_enabled=ch_enabled,
        contact_hysteresis_h=contact_hysteresis_h,
        fsr_enabled=fsr_enabled,
        fsr_strength=fsr_strength,
        boundary_enabled=boundary_enabled,
        boundary_soft_strength=boundary_soft_strength,
        boundary_hard_enabled=boundary_hard_enabled,
        boundary_hard_enabled_effective=boundary_hard_enabled_effective,
        alpha_sep=alpha_sep,
        v3_connect_radius_multiplier_effective=v3_connect_radius_multiplier_effective,
        v3_r_ref_radius_multiplier_effective=v3_r_ref_radius_multiplier_effective,
        bridge_theta_split=bridge_theta_split,
        bridge_theta_env=bridge_theta_env,
        bridge_sustain_ticks=bridge_sustain_ticks,
        strategic_inflection_sustain_ticks=strategic_inflection_sustain_ticks,
        tactical_swing_sustain_ticks=tactical_swing_sustain_ticks,
        tactical_swing_min_amplitude=tactical_swing_min_amplitude,
        tactical_swing_min_gap_ticks=tactical_swing_min_gap_ticks,
        collapse_shadow_theta_conn_default=collapse_shadow_theta_conn_default,
        collapse_shadow_theta_coh_default=collapse_shadow_theta_coh_default,
        collapse_shadow_theta_force_default=collapse_shadow_theta_force_default,
        collapse_shadow_theta_attr_default=collapse_shadow_theta_attr_default,
        collapse_shadow_attrition_window=collapse_shadow_attrition_window,
        collapse_shadow_sustain_ticks=collapse_shadow_sustain_ticks,
        collapse_shadow_min_conditions=collapse_shadow_min_conditions,
    )
    # Launcher report/export section stays here, but the dense tail work now lives
    # in small local helpers so orchestration remains readable.
    _maybe_export_battle_report(
        export_battle_report=export_battle_report,
        final_state=final_state,
        alive_trajectory=alive_trajectory,
        run_export_timestamp=run_export_timestamp,
        run_export_stem=run_export_stem,
        base_dir=base_dir,
        settings_source_path=str((base_dir / 'test_run_v1_0.settings.json').as_posix()),
        display_language=display_language,
        effective_random_seed=effective_random_seed,
        fleet_a_data=fleet_a_data,
        fleet_b_data=fleet_b_data,
        initial_fleet_sizes=initial_fleet_sizes,
        fleet_size_trajectory=fleet_size_trajectory,
        observer_telemetry=observer_telemetry,
        combat_telemetry=combat_telemetry,
        bridge_telemetry=bridge_telemetry,
        collapse_shadow_telemetry=collapse_shadow_telemetry,
        run_config_snapshot=run_config_snapshot,
    )
    if not animate:
        return

    _render_animation(
        arena_size=arena_size,
        trajectory=trajectory,
        alive_trajectory=alive_trajectory,
        fleet_size_trajectory=fleet_size_trajectory,
        initial_fleet_sizes=initial_fleet_sizes,
        position_frames=position_frames,
        final_state=final_state,
        fleet_a_display_name=fleet_a_display_name,
        fleet_b_display_name=fleet_b_display_name,
        fleet_a_full_name=fleet_a_full_name,
        fleet_b_full_name=fleet_b_full_name,
        fleet_a_avatar=fleet_a_avatar,
        fleet_b_avatar=fleet_b_avatar,
        fleet_a_color=fleet_a_color,
        fleet_b_color=fleet_b_color,
        auto_zoom_2d=auto_zoom_2d,
        frame_interval_ms=frame_interval_ms,
        effective_background_map_seed=effective_background_map_seed,
        viz_settings=viz_settings,
        tick_plots_follow_battlefield_tick=tick_plots_follow_battlefield_tick,
        display_language=display_language,
        unit_direction_mode=unit_direction_mode,
        show_attack_target_lines=show_attack_target_lines,
        observer_telemetry=observer_telemetry,
        observer_enabled=observer_enabled,
        plot_profile_effective=plot_profile_effective,
        plot_smoothing_ticks=plot_smoothing_ticks,
        damage_per_tick=damage_per_tick,
        combat_telemetry=combat_telemetry,
        test_mode=test_mode,
        movement_model_effective=movement_model_effective,
        runtime_decision_source_effective=runtime_decision_source_effective,
        pre_tl_target_substrate=pre_tl_target_substrate,
        symmetric_movement_sync_enabled=symmetric_movement_sync_enabled,
        continuous_fr_shaping_effective=continuous_fr_shaping_effective,
        continuous_fr_shaping_mode_effective=continuous_fr_shaping_mode_effective,
        odw_posture_bias_enabled_effective=odw_posture_bias_enabled_effective,
        odw_posture_bias_k_effective=odw_posture_bias_k_effective,
        odw_posture_bias_clip_delta_effective=odw_posture_bias_clip_delta_effective,
        v3_connect_radius_multiplier_effective=v3_connect_radius_multiplier_effective,
        export_video_cfg=export_video_cfg,
        boundary_enabled=boundary_enabled,
        boundary_hard_enabled=boundary_hard_enabled,
        bridge_telemetry=bridge_telemetry,
    )


if __name__ == '__main__':
    main()
