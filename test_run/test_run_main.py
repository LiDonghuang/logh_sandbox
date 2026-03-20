import random
import sys
from datetime import datetime
from functools import partial
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

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


def _prepare_export_video_cfg(viz_settings: dict, base_dir, run_export_stem: str) -> dict:
    export_video_cfg = viz_settings.get("export_video", {})
    export_video_cfg = dict(export_video_cfg) if isinstance(export_video_cfg, dict) else {}
    export_video_enabled = bool(
        export_video_cfg.get("enabled", viz_settings.get("export_video_enabled", False))
    )
    export_video_enabled_override = core.get_env_bool("LOGH_EXPORT_VIDEO_ENABLED")
    if export_video_enabled_override is not None:
        export_video_enabled = export_video_enabled_override

    raw_video_output_path = str(export_video_cfg.get("output_path", core.DEFAULT_VIDEO_EXPORT_DIR))
    export_video_cfg.update(
        enabled=export_video_enabled,
        output_path=str(
            core.resolve_timestamped_video_output_path(
                raw_video_output_path,
                base_dir=base_dir,
                export_stem=f"{run_export_stem}_video",
            )
        ),
        output_path_is_final=True,
    )
    return export_video_cfg

def _maybe_export_battle_report(
    *,
    export_battle_report: bool,
    final_state,
    alive_trajectory: dict,
    run_export_timestamp: str,
    run_export_stem: str,
    base_dir,
    report_context: dict,
) -> None:
    remaining_units_a_final = int(alive_trajectory.get("A", [0])[-1]) if alive_trajectory.get("A") else 0
    remaining_units_b_final = int(alive_trajectory.get("B", [0])[-1]) if alive_trajectory.get("B") else 0
    winner_decided = (remaining_units_a_final <= 0) != (remaining_units_b_final <= 0)
    battle_report_export_allowed = (
        bool(export_battle_report)
        and int(final_state.tick) >= 100
        and winner_decided
    )

    if not battle_report_export_allowed:
        return

    report_markdown = report_builder.build_battle_report_markdown(
        final_state=final_state,
        alive_trajectory=alive_trajectory,
        **report_context,
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
    render_context: dict,
    combat_telemetry: dict,
    bridge_telemetry: dict,
    debug_context: dict,
) -> None:
    bridge_ticks_debug = report_builder.compute_bridge_event_ticks(
        bridge_telemetry if isinstance(bridge_telemetry, dict) else None
    )
    first_contact_tick_debug = None
    for idx, value in enumerate(combat_telemetry.get("in_contact_count", []), start=1):
        try:
            if int(value) > 0:
                first_contact_tick_debug = idx
                break
        except (TypeError, ValueError):
            continue

    try:
        from test_run.test_run_v1_0_viz import render_test_run
    except ModuleNotFoundError as exc:
        print(f"[viz] skipped: {exc}")
        return

    render_test_run(
        **render_context,
        combat_telemetry=combat_telemetry,
        bridge_telemetry=bridge_telemetry,
        debug_context={
            **debug_context,
            "first_contact_tick": first_contact_tick_debug,
            "formation_cut_tick": bridge_ticks_debug.get("formation_cut_tick"),
            "pocket_formation_tick": bridge_ticks_debug.get("pocket_formation_tick"),
        },
    )


def _print_run_summary(
    *,
    effective_random_seed: int,
    effective_metatype_random_seed: int,
    effective_background_map_seed: int,
    test_mode_name: str,
    runtime_decision_source_effective: str,
    movement_model_effective: str,
    hostile_contact_impedance_mode: str,
    animate: bool,
    observer_enabled: bool,
    export_battle_report: bool,
) -> None:
    print(
        f'[run] mode={test_mode_name} '
        f'movement={movement_model_effective} '
        f'cohesion={runtime_decision_source_effective} '
        f'contact_model={hostile_contact_impedance_mode} '
        f'animate={animate} observer={observer_enabled} report={export_battle_report} '
        f'seeds={effective_random_seed}/{effective_metatype_random_seed}/{effective_background_map_seed}'
    )


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    settings = settings_api.load_layered_test_run_settings(base_dir)
    viz_settings = settings_api.load_json_file(base_dir / 'test_run_v1_0.viz.settings.json')
    get_battlefield = partial(settings_api.get_battlefield_setting, settings)
    get_collapse_shadow = partial(settings_api.get_collapse_shadow_setting, settings)
    get_contact_model = partial(settings_api.get_contact_model_test_setting, settings)
    get_event_bridge = partial(settings_api.get_event_bridge_setting, settings)
    get_fleet = partial(settings_api.get_fleet_setting, settings)
    get_report_inference = partial(settings_api.get_report_inference_setting, settings)
    get_run = partial(settings_api.get_run_control_setting, settings)
    get_runtime = partial(settings_api.get_runtime_setting, settings)
    get_runtime_metatype = partial(settings_api.get_runtime_metatype_setting, settings)
    get_unit = partial(settings_api.get_unit_setting, settings)
    get_viz = partial(settings_api.get_visualization_setting, settings)
    post_elimination_extra_ticks = max(0, int(viz_settings.get('post_elimination_extra_ticks', 10)))
    archetypes = settings_api.load_json_file(core.PROJECT_ROOT / 'archetypes' / 'archetypes_v1_5.json')
    metatype_settings = core.load_metatype_settings(base_dir, settings)
    random_seed = int(get_run('random_seed', -1))
    metatype_random_seed = int(get_runtime_metatype('random_seed', random_seed))
    background_map_seed = int(get_battlefield('background_map_seed', -1))
    effective_random_seed = core.resolve_effective_seed(random_seed)
    effective_metatype_random_seed = core.resolve_effective_seed(metatype_random_seed)
    effective_background_map_seed = core.resolve_effective_seed(background_map_seed)
    archetype_rng = random.Random(int(effective_metatype_random_seed))
    fleet_a_data = core.resolve_fleet_archetype_data(
        archetypes,
        metatype_settings,
        get_fleet('fleet_a_archetype_id', 'default'),
        rng=archetype_rng,
    )
    fleet_b_data = core.resolve_fleet_archetype_data(
        archetypes,
        metatype_settings,
        get_fleet('fleet_b_archetype_id', 'default'),
        rng=archetype_rng,
    )
    fleet_a_params = core.to_personality_parameters(fleet_a_data)
    fleet_b_params = core.to_personality_parameters(fleet_b_data)
    fleet_a_color, fleet_b_color = core.resolve_fleet_plot_colors(fleet_a_data, fleet_b_data)
    display_language = str(get_viz('display_language', 'EN')).upper()
    display_language = display_language if display_language in {'EN', 'ZH'} else 'EN'
    fleet_a_label = core.resolve_display_name(fleet_a_data, display_language)
    fleet_b_label = core.resolve_display_name(fleet_b_data, display_language)
    fleet_a_full_name = report_builder.resolve_name_with_fallback(fleet_a_data, display_language, True, 'A')
    fleet_b_full_name = report_builder.resolve_name_with_fallback(fleet_b_data, display_language, True, 'B')
    fleet_a_avatar = core.resolve_avatar_with_fallback(fleet_a_data, core.DEFAULT_AVATAR_A)
    fleet_b_avatar = core.resolve_avatar_with_fallback(fleet_b_data, core.DEFAULT_AVATAR_B)
    battlefield_cfg = {
        'arena_size': float(get_battlefield('arena_size', 200.0)),
        'effective_background_map_seed': effective_background_map_seed,
    }
    spawn_margin = max(1.0, battlefield_cfg['arena_size'] * core.DEFAULT_SPAWN_MARGIN_RATIO)
    fleet_a_origin_x, fleet_a_origin_y = core._resolve_point_setting(settings, array_key='initial_fleet_a_origin_xy', x_key='initial_fleet_a_origin_x', y_key='initial_fleet_a_origin_y', default_x=spawn_margin, default_y=spawn_margin)
    fleet_b_origin_x, fleet_b_origin_y = core._resolve_point_setting(settings, array_key='initial_fleet_b_origin_xy', x_key='initial_fleet_b_origin_x', y_key='initial_fleet_b_origin_y', default_x=battlefield_cfg['arena_size'] - spawn_margin, default_y=battlefield_cfg['arena_size'] - spawn_margin)
    fleet_cfg = {
        'sizes': {
            'A': int(get_fleet('initial_fleet_a_size', 100)),
            'B': int(get_fleet('initial_fleet_b_size', 100)),
        },
        'aspect_ratios': {
            'A': float(get_fleet('initial_fleet_a_aspect_ratio', 2.0)),
            'B': float(get_fleet('initial_fleet_b_aspect_ratio', 2.0)),
        },
        'origins': {
            'A': (fleet_a_origin_x, fleet_a_origin_y),
            'B': (fleet_b_origin_x, fleet_b_origin_y),
        },
        'facing_angles_deg': {
            'A': float(get_fleet('initial_fleet_a_facing_angle_deg', 45.0)),
            'B': float(get_fleet('initial_fleet_b_facing_angle_deg', 225.0)),
        },
        'unit_spacing': float(get_runtime('min_unit_spacing', 1.0)),
    }
    if min(fleet_cfg['sizes'].values()) < 1:
        raise ValueError(f"initial fleet sizes must be >= 1, got {fleet_cfg['sizes']}")
    if min(fleet_cfg['aspect_ratios'].values()) <= 0.0 or fleet_cfg['unit_spacing'] <= 0.0:
        raise ValueError(
            f"initial geometry aspect ratios and min_unit_spacing must be > 0, got {fleet_cfg['aspect_ratios']}, spacing={fleet_cfg['unit_spacing']}"
        )
    unit_cfg = {
        'speed': float(get_unit('unit_speed', 1.0)),
        'max_hit_points': float(get_unit('unit_max_hit_points', 100.0)),
        'attack_range': float(get_unit('attack_range', get_runtime('attack_range', 3.0))),
        'damage_per_tick': float(get_unit('damage_per_tick', get_runtime('damage_per_tick', 1.0))),
    }
    state = experiments.build_initial_state(
        fleet_a_params=fleet_a_params,
        fleet_b_params=fleet_b_params,
        fleet_a_size=fleet_cfg['sizes']['A'],
        fleet_b_size=fleet_cfg['sizes']['B'],
        fleet_a_aspect_ratio=fleet_cfg['aspect_ratios']['A'],
        fleet_b_aspect_ratio=fleet_cfg['aspect_ratios']['B'],
        unit_spacing=fleet_cfg['unit_spacing'],
        unit_speed=unit_cfg['speed'],
        unit_max_hit_points=unit_cfg['max_hit_points'],
        arena_size=battlefield_cfg['arena_size'],
        fleet_a_origin_x=fleet_cfg['origins']['A'][0],
        fleet_a_origin_y=fleet_cfg['origins']['A'][1],
        fleet_b_origin_x=fleet_cfg['origins']['B'][0],
        fleet_b_origin_y=fleet_cfg['origins']['B'][1],
        fleet_a_facing_angle_deg=fleet_cfg['facing_angles_deg']['A'],
        fleet_b_facing_angle_deg=fleet_cfg['facing_angles_deg']['B'],
    )
    initial_fleet_sizes = {
        fleet_id: sum(
            max(0.0, float(state.units[unit_id].hit_points))
            for unit_id in fleet.unit_ids
            if unit_id in state.units
        )
        for fleet_id, fleet in state.fleets.items()
    }
    viz_cfg = {
        'animate': bool(get_viz('animate', True)),
        'auto_zoom_2d': bool(get_viz('auto_zoom_2d', False)),
        'frame_stride': core.DEFAULT_FRAME_STRIDE,
        'base_frame_interval_ms': int(get_viz('animation_frame_interval_ms', 100)),
        'animation_play_speed': float(get_viz('animation_play_speed', 1.0)),
        'unit_direction_mode': _require_choice(
            'visualization.vector_display_mode',
            get_viz('vector_display_mode', get_viz('unit_direction_mode', 'effective')),
            {'effective', 'free', 'attack', 'composite'},
        ),
        'show_attack_target_lines': bool(get_viz('show_attack_target_lines', False)),
        'tick_plots_follow_battlefield_tick': bool(get_viz('tick_plots_follow_battlefield_tick', False)),
        'print_tick_summary': bool(get_viz('print_tick_summary', True)),
        'plot_smoothing_ticks': int(get_viz('plot_smoothing_ticks', 5)),
        'plot_profile_requested': get_viz('plot_profile', 'auto'),
    }
    if viz_cfg['base_frame_interval_ms'] < 1:
        raise ValueError(
            f"visualization.animation_frame_interval_ms must be >= 1, got {viz_cfg['base_frame_interval_ms']}"
        )
    if viz_cfg['animation_play_speed'] <= 0.0:
        raise ValueError(
            f"visualization.animation_play_speed must be > 0, got {viz_cfg['animation_play_speed']}"
        )
    viz_cfg['frame_interval_ms'] = max(
        1,
        int(round(viz_cfg['base_frame_interval_ms'] / viz_cfg['animation_play_speed'])),
    )

    contact_cfg = {
        'attack_range': unit_cfg['attack_range'],
        'damage_per_tick': unit_cfg['damage_per_tick'],
        'fire_quality_alpha': float(get_runtime('fire_quality_alpha', 0.1)),
        'contact_hysteresis_h': float(get_runtime('contact_hysteresis_h', 0.1)),
        'fsr_strength': float(get_runtime('fsr_strength', 0.0)),
        'alpha_sep': float(get_runtime('alpha_sep', 0.6)),
        'hostile_contact_impedance_mode': _require_choice(
            'runtime.test_only.hostile_contact_impedance.active_mode',
            get_contact_model(('active_mode',), core.HOSTILE_CONTACT_IMPEDANCE_MODE_DEFAULT),
            core.HOSTILE_CONTACT_IMPEDANCE_MODE_LABELS,
        ),
        'hybrid_v2': {
            key: float(get_contact_model(('hybrid_v2', key), default))
            for key, default in {
                'radius_multiplier': core.HOSTILE_CONTACT_IMPEDANCE_V2_RADIUS_MULTIPLIER_DEFAULT,
                'repulsion_max_disp_ratio': core.HOSTILE_CONTACT_IMPEDANCE_V2_REPULSION_MAX_DISP_RATIO_DEFAULT,
                'forward_damping_strength': core.HOSTILE_CONTACT_IMPEDANCE_V2_FORWARD_DAMPING_STRENGTH_DEFAULT,
            }.items()
        },
        'intent_unified_spacing_v1': {
            key: float(get_contact_model(('intent_unified_spacing_v1', key), default))
            for key, default in {
                'scale': core.HOSTILE_INTENT_UNIFIED_SPACING_SCALE_DEFAULT,
                'strength': core.HOSTILE_INTENT_UNIFIED_SPACING_STRENGTH_DEFAULT,
            }.items()
        },
    }
    contact_cfg['ch_enabled'] = contact_cfg['contact_hysteresis_h'] > 0.0
    contact_cfg['fsr_enabled'] = contact_cfg['fsr_strength'] > 0.0

    movement_cfg = {
        'model_effective': core.resolve_movement_model(get_runtime('movement_model', 'baseline'))[1],
        'experiment_effective': _require_choice(
            'runtime.movement_v3a_experiment',
            get_runtime('movement_v3a_experiment', core.V3A_EXPERIMENT_BASE),
            core.V3A_EXPERIMENT_LABELS,
        ),
        'centroid_probe_scale': float(get_runtime('centroid_probe_scale', 1.0)),
        'pre_tl_target_substrate': _require_choice(
            'runtime.pre_tl_target_substrate',
            get_runtime('pre_tl_target_substrate', core.PRE_TL_TARGET_SUBSTRATE_DEFAULT),
            core.PRE_TL_TARGET_SUBSTRATE_LABELS,
        ),
        'symmetric_movement_sync_enabled': bool(get_runtime('symmetric_movement_sync_enabled', True)),
        'continuous_fr_shaping': {
            'enabled': bool(get_runtime('continuous_fr_shaping_enabled', False)),
            'mode': _require_choice(
                'runtime.continuous_fr_shaping_mode',
                get_runtime('continuous_fr_shaping_mode', core.CONTINUOUS_FR_SHAPING_OFF),
                core.CONTINUOUS_FR_SHAPING_LABELS,
            ),
            **{
                key: float(get_runtime(f'continuous_fr_shaping_{key}', default))
                for key, default in {
                    'a': 0.0,
                    'sigma': 0.15,
                    'p': 1.0,
                    'q': 1.0,
                    'beta': 0.0,
                    'gamma': 0.0,
                }.items()
            },
        },
        'odw_posture_bias': {
            'enabled': bool(get_runtime('odw_posture_bias_enabled', False)),
            'k': float(get_runtime('odw_posture_bias_k', 0.3)),
            'clip_delta': float(get_runtime('odw_posture_bias_clip_delta', 0.2)),
        },
    }
    movement_cfg['centroid_probe_scale_effective'] = (
        movement_cfg['centroid_probe_scale']
        if movement_cfg['model_effective'] == 'v3a'
        and movement_cfg['experiment_effective'] == core.V3A_EXPERIMENT_PRECONTACT_CENTROID_PROBE
        else 1.0
    )
    movement_cfg['continuous_fr_shaping']['effective'] = (
        movement_cfg['model_effective'] == 'v3a'
        and movement_cfg['experiment_effective'] == core.V3A_EXPERIMENT_PRECONTACT_CENTROID_PROBE
        and movement_cfg['continuous_fr_shaping']['enabled']
        and movement_cfg['continuous_fr_shaping']['mode'] != core.CONTINUOUS_FR_SHAPING_OFF
        and movement_cfg['continuous_fr_shaping']['a'] > 0.0
    )
    movement_cfg['continuous_fr_shaping']['mode_effective'] = (
        movement_cfg['continuous_fr_shaping']['mode']
        if movement_cfg['continuous_fr_shaping']['effective']
        else core.CONTINUOUS_FR_SHAPING_OFF
    )
    movement_cfg['odw_posture_bias']['enabled_effective'] = (
        movement_cfg['model_effective'] == 'v3a'
        and movement_cfg['odw_posture_bias']['enabled']
    )
    movement_cfg['odw_posture_bias']['k_effective'] = (
        movement_cfg['odw_posture_bias']['k']
        if movement_cfg['odw_posture_bias']['enabled_effective']
        else 0.0
    )
    movement_cfg['odw_posture_bias']['clip_delta_effective'] = (
        movement_cfg['odw_posture_bias']['clip_delta']
        if movement_cfg['odw_posture_bias']['enabled_effective']
        else 0.2
    )

    observer_cfg = {
        'bridge': {
            'theta_split': float(get_event_bridge('theta_split', core.BRIDGE_THETA_SPLIT_DEFAULT)),
            'theta_env': float(get_event_bridge('theta_env', core.BRIDGE_THETA_ENV_DEFAULT)),
            'sustain_ticks': int(get_event_bridge('sustain_ticks', core.BRIDGE_SUSTAIN_TICKS_DEFAULT)),
        },
        'collapse_shadow': {
            key: cast(get_collapse_shadow(key, default))
            for key, (cast, default) in {
                'theta_conn_default': (float, core.COLLAPSE_V2_SHADOW_THETA_CONN_DEFAULT),
                'theta_coh_default': (float, core.COLLAPSE_V2_SHADOW_THETA_COH_DEFAULT),
                'theta_force_default': (float, core.COLLAPSE_V2_SHADOW_THETA_FORCE_DEFAULT),
                'theta_attr_default': (float, core.COLLAPSE_V2_SHADOW_THETA_ATTR_DEFAULT),
                'attrition_window': (int, core.COLLAPSE_V2_SHADOW_ATTRITION_WINDOW_DEFAULT),
                'sustain_ticks': (int, core.COLLAPSE_V2_SHADOW_SUSTAIN_TICKS_DEFAULT),
                'min_conditions': (int, core.COLLAPSE_V2_SHADOW_MIN_CONDITIONS_DEFAULT),
            }.items()
        },
        'report_inference': {
            'strategic_inflection_sustain_ticks': int(
                get_report_inference('strategic_inflection_sustain_ticks', core.STRATEGIC_INFLECTION_SUSTAIN_TICKS)
            ),
            'tactical_swing_sustain_ticks': int(
                get_report_inference('tactical_swing_sustain_ticks', core.TACTICAL_SWING_SUSTAIN_TICKS)
            ),
            'tactical_swing_min_amplitude': float(
                get_report_inference('tactical_swing_min_amplitude', core.TACTICAL_SWING_MIN_AMPLITUDE)
            ),
            'tactical_swing_min_gap_ticks': int(
                get_report_inference('tactical_swing_min_gap_ticks', core.TACTICAL_SWING_MIN_GAP_TICKS)
            ),
        },
    }

    boundary_cfg = {
        'enabled': bool(get_runtime('boundary_enabled', False)),
        'hard_enabled': bool(get_runtime('boundary_hard_enabled', True)),
        'soft_strength': float(get_runtime('boundary_soft_strength', 1.0)),
    }
    boundary_cfg['hard_enabled_effective'] = boundary_cfg['enabled'] and boundary_cfg['hard_enabled']

    run_cfg = {
        'max_time_steps': int(get_run('max_time_steps', -1)),
        'test_mode': core.parse_test_mode(get_run('test_mode', 0)),
    }
    run_cfg['test_mode_name'] = core.test_mode_label(run_cfg['test_mode'])
    run_cfg['observer_enabled'] = run_cfg['test_mode'] >= 1
    run_cfg['export_battle_report'] = run_cfg['test_mode'] >= 1
    (
        run_cfg['runtime_decision_source_requested'],
        run_cfg['runtime_decision_source_effective'],
    ) = core.resolve_runtime_decision_source(
        get_runtime('cohesion_decision_source', 'baseline'),
        run_cfg['test_mode'],
    )
    movement_cfg['v2_connect_radius_multiplier'] = 1.0
    movement_cfg['v3_connect_radius_multiplier_effective'] = (
        float(get_runtime('v3_connect_radius_multiplier', core.BASELINE_V3_CONNECT_RADIUS_MULTIPLIER))
        if run_cfg['runtime_decision_source_effective'] == 'v3_test'
        else 1.0
    )
    movement_cfg['v3_r_ref_radius_multiplier_effective'] = (
        float(get_runtime('v3_r_ref_radius_multiplier', core.BASELINE_V3_R_REF_RADIUS_MULTIPLIER))
        if run_cfg['runtime_decision_source_effective'] == 'v3_test'
        else 1.0
    )

    _, viz_cfg['plot_profile'] = core.resolve_plot_profile(
        viz_cfg['plot_profile_requested'],
        run_cfg['test_mode'],
        run_cfg['runtime_decision_source_requested'],
        run_cfg['runtime_decision_source_effective'],
    )
    viz_cfg['plot_diagnostics_enabled'] = viz_cfg['animate'] or run_cfg['observer_enabled']
    _print_run_summary(
        effective_random_seed=effective_random_seed,
        effective_metatype_random_seed=effective_metatype_random_seed,
        effective_background_map_seed=battlefield_cfg['effective_background_map_seed'],
        test_mode_name=run_cfg['test_mode_name'],
        runtime_decision_source_effective=run_cfg['runtime_decision_source_effective'],
        movement_model_effective=movement_cfg['model_effective'],
        hostile_contact_impedance_mode=contact_cfg['hostile_contact_impedance_mode'],
        animate=viz_cfg['animate'],
        observer_enabled=run_cfg['observer_enabled'],
        export_battle_report=run_cfg['export_battle_report'],
    )
    run_export_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    run_export_stem = f'{core.DEFAULT_BATTLE_REPORT_TOPIC}_{run_export_timestamp}'
    export_video_cfg = _prepare_export_video_cfg(
        viz_settings,
        base_dir,
        run_export_stem,
    )
    capture_target_directions = (
        viz_cfg['show_attack_target_lines']
        or viz_cfg['unit_direction_mode'] in {'attack', 'composite'}
    )
    execution_cfg = {
        'steps': run_cfg['max_time_steps'],
        'capture_positions': viz_cfg['animate'],
        'frame_stride': viz_cfg['frame_stride'],
        'include_target_lines': capture_target_directions,
        'print_tick_summary': viz_cfg['print_tick_summary'],
        'plot_diagnostics_enabled': viz_cfg['plot_diagnostics_enabled'],
        'post_elimination_extra_ticks': post_elimination_extra_ticks,
    }
    simulation_runtime_cfg = {
        'decision_source': run_cfg['runtime_decision_source_effective'],
        'movement_model': movement_cfg['model_effective'],
        'movement': movement_cfg,
        'contact': {
            **contact_cfg,
            'separation_radius': fleet_cfg['unit_spacing'],
        },
        'boundary': boundary_cfg,
    }
    simulation_observer_cfg = {
        'enabled': run_cfg['observer_enabled'],
        'bridge': observer_cfg['bridge'],
        'collapse_shadow': observer_cfg['collapse_shadow'],
        'runtime_diag_enabled': False,
    }
    final_state, trajectory, alive_trajectory, fleet_size_trajectory, observer_telemetry, combat_telemetry, bridge_telemetry, collapse_shadow_telemetry, position_frames = experiments.run_simulation(
        initial_state=state,
        engine_cls=core.TestModeEngineTickSkeleton,
        execution_cfg=execution_cfg,
        runtime_cfg=simulation_runtime_cfg,
        observer_cfg=simulation_observer_cfg,
    )
    position_frames = position_frames if viz_cfg['animate'] else []
    max_time_steps_effective = int(final_state.tick)
    movement_is_v3a = movement_cfg['model_effective'] == 'v3a'
    run_config_snapshot = {
        'initial_units_per_side': (
            int(fleet_cfg['sizes']['A'])
            if fleet_cfg['sizes']['A'] == fleet_cfg['sizes']['B']
            else int(max(fleet_cfg['sizes']['A'], fleet_cfg['sizes']['B']))
        ),
        'initial_units_a': int(fleet_cfg['sizes']['A']),
        'initial_units_b': int(fleet_cfg['sizes']['B']),
        'test_mode': run_cfg['test_mode'],
        'test_mode_label': run_cfg['test_mode_name'],
        'random_seed_effective': int(effective_random_seed),
        'background_map_seed_effective': int(battlefield_cfg['effective_background_map_seed']),
        'metatype_random_seed_effective': int(effective_metatype_random_seed),
        'runtime_decision_source_effective': run_cfg['runtime_decision_source_effective'],
        'collapse_decision_source_effective': run_cfg['runtime_decision_source_effective'],
        'movement_model_effective': movement_cfg['model_effective'],
        'arena_size': battlefield_cfg['arena_size'],
        'max_time_steps_effective': max_time_steps_effective,
        'unit_speed': unit_cfg['speed'],
        'min_unit_spacing': fleet_cfg['unit_spacing'],
        'movement_v3a_experiment_effective': movement_cfg['experiment_effective'] if movement_is_v3a else 'N/A',
        'centroid_probe_scale_effective': movement_cfg['centroid_probe_scale_effective'] if movement_is_v3a else 'N/A',
        **{key: contact_cfg[key] for key in (
            'attack_range',
            'damage_per_tick',
            'ch_enabled',
            'contact_hysteresis_h',
            'fsr_enabled',
            'fsr_strength',
            'alpha_sep',
        )},
        **{
            key: boundary_cfg[source]
            for key, source in (
                ('boundary_enabled', 'enabled'),
                ('boundary_soft_strength', 'soft_strength'),
                ('boundary_hard_enabled', 'hard_enabled'),
                ('boundary_hard_enabled_effective', 'hard_enabled_effective'),
            )
        },
        **observer_cfg['report_inference'],
    }
    report_context = {
        'settings_source_path': (base_dir / 'test_run_v1_0.settings.json').as_posix(),
        'display_language': display_language,
        'random_seed_effective': effective_random_seed,
        'fleet_a_data': fleet_a_data,
        'fleet_b_data': fleet_b_data,
        'initial_fleet_sizes': initial_fleet_sizes,
        'fleet_size_trajectory': fleet_size_trajectory,
        'observer_telemetry': observer_telemetry,
        'combat_telemetry': combat_telemetry,
        'bridge_telemetry': bridge_telemetry,
        'collapse_shadow_telemetry': collapse_shadow_telemetry,
        'run_config_snapshot': run_config_snapshot,
    }
    _maybe_export_battle_report(
        export_battle_report=run_cfg['export_battle_report'],
        final_state=final_state,
        alive_trajectory=alive_trajectory,
        run_export_timestamp=run_export_timestamp,
        run_export_stem=run_export_stem,
        base_dir=base_dir,
        report_context=report_context,
    )
    if not viz_cfg['animate']:
        return

    render_context = {
        **{
            key: value
            for key, value in (
                ('arena_size', battlefield_cfg['arena_size']),
                ('trajectory', trajectory),
                ('alive_trajectory', alive_trajectory),
                ('fleet_size_trajectory', fleet_size_trajectory),
                ('initial_fleet_sizes', initial_fleet_sizes),
                ('position_frames', position_frames),
                ('final_state', final_state),
                ('fleet_a_label', fleet_a_label),
                ('fleet_b_label', fleet_b_label),
                ('fleet_a_full_name', fleet_a_full_name),
                ('fleet_b_full_name', fleet_b_full_name),
                ('fleet_a_avatar', fleet_a_avatar),
                ('fleet_b_avatar', fleet_b_avatar),
                ('fleet_a_color', fleet_a_color),
                ('fleet_b_color', fleet_b_color),
                ('display_language', display_language),
            )
        },
        **{
            key: viz_cfg[key]
            for key in (
                'auto_zoom_2d',
                'frame_interval_ms',
                'tick_plots_follow_battlefield_tick',
                'unit_direction_mode',
                'show_attack_target_lines',
                'plot_profile',
                'plot_smoothing_ticks',
            )
        },
        'background_seed': battlefield_cfg['effective_background_map_seed'],
        'viz_settings': viz_settings,
        'observer_telemetry': observer_telemetry,
        'observer_enabled': run_cfg['observer_enabled'],
        'damage_per_tick': contact_cfg['damage_per_tick'],
        'export_video_cfg': export_video_cfg,
        'boundary_enabled': boundary_cfg['enabled'],
        'boundary_hard_enabled': boundary_cfg['hard_enabled'],
    }
    render_debug_context = {
        'test_mode_label': run_cfg['test_mode_name'],
        'movement_model_effective': movement_cfg['model_effective'],
        'cohesion_decision_source_effective': run_cfg['runtime_decision_source_effective'],
        'pre_tl_target_substrate': movement_cfg['pre_tl_target_substrate'],
        'symmetric_movement_sync_enabled': movement_cfg['symmetric_movement_sync_enabled'],
        'continuous_fr_shaping_effective': movement_cfg['continuous_fr_shaping']['effective'],
        'continuous_fr_shaping_mode_effective': movement_cfg['continuous_fr_shaping']['mode_effective'],
        'odw_posture_bias_enabled_effective': movement_cfg['odw_posture_bias']['enabled_effective'],
        'odw_posture_bias_k_effective': movement_cfg['odw_posture_bias']['k_effective'],
        'odw_posture_bias_clip_delta_effective': movement_cfg['odw_posture_bias']['clip_delta_effective'],
        'v3_connect_radius_multiplier_effective': movement_cfg['v3_connect_radius_multiplier_effective'],
        'plot_smoothing_ticks': viz_cfg['plot_smoothing_ticks'],
    }

    _render_animation(
        render_context=render_context,
        combat_telemetry=combat_telemetry,
        bridge_telemetry=bridge_telemetry,
        debug_context=render_debug_context,
    )


if __name__ == '__main__':
    main()
