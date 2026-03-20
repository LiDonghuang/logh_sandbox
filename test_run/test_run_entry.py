import os
import sys
from datetime import datetime
from functools import partial
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from test_run import battle_report_builder as report_builder
from test_run import settings_accessor as settings_api
from test_run import test_run_execution as execution
from test_run import test_run_scenario as scenario


DEFAULT_BATTLE_REPORT_TOPIC = "test_run_v1_0"
DEFAULT_BATTLE_REPORT_EXPORT_DIR = "analysis/exports/battle_reports"
DEFAULT_VIDEO_EXPORT_DIR = "analysis/exports/videos"
DEFAULT_VIDEO_EXPORT_TOPIC = "test_run_v1_0"
DEFAULT_AVATAR_A = "avatar_reinhard"
DEFAULT_AVATAR_B = "avatar_yang"
PLOT_PROFILE_LABELS = {
    "auto": "auto",
    "baseline": "baseline",
    "extended": "extended",
}


def _require_choice(name: str, raw_value, allowed: set[str]) -> str:
    value = str(raw_value).strip().lower()
    if value not in allowed:
        allowed_text = ", ".join(sorted(allowed))
        raise ValueError(f"{name} must be one of {{{allowed_text}}}, got {raw_value!r}")
    return value


def _get_env_bool(name: str) -> bool | None:
    raw = os.environ.get(name)
    if raw is None:
        return None
    value = str(raw).strip().lower()
    if value in {"1", "true", "yes", "on"}:
        return True
    if value in {"0", "false", "no", "off"}:
        return False
    return None


def _resolve_timestamped_video_output_path(
    raw_output_path: str,
    base_dir: Path,
    *,
    export_stem: str | None = None,
) -> Path:
    candidate = Path(str(raw_output_path).strip()) if str(raw_output_path).strip() else Path(DEFAULT_VIDEO_EXPORT_DIR)
    if not candidate.is_absolute():
        candidate = (base_dir.parent / candidate).resolve()
    if candidate.suffix:
        target_dir = candidate.parent
        suffix = candidate.suffix
    else:
        target_dir = candidate
        suffix = ".mp4"
    final_stem = str(export_stem).strip() if export_stem else DEFAULT_VIDEO_EXPORT_TOPIC
    return (target_dir / f"{final_stem}{suffix}").resolve()


def _resolve_plot_profile(
    raw_value,
    test_mode: int,
    cohesion_decision_source_requested: str,
    cohesion_decision_source_effective: str,
) -> tuple[str, str]:
    requested = str(raw_value).strip().lower()
    if requested not in PLOT_PROFILE_LABELS:
        requested = "auto"
    requested_cohesion = str(cohesion_decision_source_requested).strip().lower()
    effective_cohesion = str(cohesion_decision_source_effective).strip().lower()
    v3_plot_permitted = effective_cohesion == "v3_test"
    if requested == "auto":
        effective = "extended" if v3_plot_permitted else "baseline"
    elif requested == "extended" and not v3_plot_permitted:
        effective = "baseline"
    else:
        effective = requested
    if requested == "extended" and effective != "extended":
        print(
            f"[mode] plot_profile={requested} requested but test_mode={test_mode} with cohesion_decision_source={requested_cohesion} only permits baseline plots; remapping to baseline"
        )
    return requested, effective


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
    **_ignored,
) -> None:
    print(
        f"[run] mode={test_mode_name} "
        f"movement={movement_model_effective} "
        f"cohesion={runtime_decision_source_effective} "
        f"contact_model={hostile_contact_impedance_mode} "
        f"animate={animate} observer={observer_enabled} report={export_battle_report} "
        f"seeds={effective_random_seed}/{effective_metatype_random_seed}/{effective_background_map_seed}"
    )


def _prepare_export_video_cfg(viz_settings: dict, base_dir: Path, run_export_stem: str) -> dict:
    export_video_cfg = viz_settings.get("export_video", {})
    export_video_cfg = dict(export_video_cfg) if isinstance(export_video_cfg, dict) else {}
    export_video_enabled = bool(
        export_video_cfg.get("enabled", viz_settings.get("export_video_enabled", False))
    )
    export_video_enabled_override = _get_env_bool("LOGH_EXPORT_VIDEO_ENABLED")
    if export_video_enabled_override is not None:
        export_video_enabled = export_video_enabled_override

    raw_video_output_path = str(export_video_cfg.get("output_path", DEFAULT_VIDEO_EXPORT_DIR))
    export_video_cfg.update(
        enabled=export_video_enabled,
        output_path=str(
            _resolve_timestamped_video_output_path(
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
    base_dir: Path,
    report_context: dict,
) -> None:
    remaining_units_a_final = int(alive_trajectory.get("A", [0])[-1]) if alive_trajectory.get("A") else 0
    remaining_units_b_final = int(alive_trajectory.get("B", [0])[-1]) if alive_trajectory.get("B") else 0
    winner_decided = (remaining_units_a_final <= 0) != (remaining_units_b_final <= 0)
    battle_report_export_allowed = bool(export_battle_report) and int(final_state.tick) >= 100 and winner_decided
    if not battle_report_export_allowed:
        return

    report_markdown = report_builder.build_battle_report_markdown(
        final_state=final_state,
        alive_trajectory=alive_trajectory,
        **report_context,
    )
    report_date_dir = run_export_timestamp[:8]
    report_export_dir = (
        base_dir.parent / DEFAULT_BATTLE_REPORT_EXPORT_DIR / report_date_dir
    ).resolve()
    report_export_dir.mkdir(parents=True, exist_ok=True)
    report_output_path = report_export_dir / f"{run_export_stem}_Battle_Report_Framework_v1.0.md"
    report_output_path.write_text(report_markdown, encoding="utf-8")
    print(f"[report] battle_report_exported={report_output_path}")


def _render_animation(
    *,
    render_context: dict,
    combat_telemetry: dict,
    bridge_telemetry: dict,
    debug_context: dict,
) -> None:
    bridge_ticks_debug = report_builder.compute_bridge_event_ticks(bridge_telemetry)
    first_contact_tick_debug = None
    for idx, value in enumerate(combat_telemetry.get("in_contact_count", []), start=1):
        try:
            if int(value) > 0:
                first_contact_tick_debug = idx
                break
        except (TypeError, ValueError):
            continue

    from test_run.test_run_v1_0_viz import render_test_run

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


def run_active_surface(
    *,
    base_dir: Path | None = None,
    prepared_override: dict | None = None,
    settings_override: dict | None = None,
    execution_overrides: dict | None = None,
    summary_override: dict | None = None,
    emit_summary: bool = True,
) -> dict:
    active_base_dir = base_dir or Path(__file__).resolve().parent
    prepared = (
        prepared_override
        if prepared_override is not None
        else scenario.prepare_active_scenario(
            active_base_dir,
            settings_override=settings_override,
        )
    )
    execution_cfg = dict(prepared["execution_cfg"])
    if isinstance(execution_overrides, dict):
        execution_cfg.update(execution_overrides)
    summary = dict(prepared["summary"])
    if isinstance(summary_override, dict):
        summary.update(summary_override)
    if emit_summary:
        _print_run_summary(**summary)
    (
        final_state,
        trajectory,
        alive_trajectory,
        fleet_size_trajectory,
        observer_telemetry,
        combat_telemetry,
        bridge_telemetry,
        collapse_shadow_telemetry,
        position_frames,
    ) = execution.run_simulation(
        initial_state=prepared["initial_state"],
        engine_cls=prepared["engine_cls"],
        execution_cfg=execution_cfg,
        runtime_cfg=prepared["runtime_cfg"],
        observer_cfg=prepared["observer_cfg"],
    )
    effective_prepared = dict(prepared)
    effective_prepared["execution_cfg"] = execution_cfg
    effective_prepared["summary"] = summary
    return {
        "prepared": effective_prepared,
        "final_state": final_state,
        "trajectory": trajectory,
        "alive_trajectory": alive_trajectory,
        "fleet_size_trajectory": fleet_size_trajectory,
        "observer_telemetry": observer_telemetry,
        "combat_telemetry": combat_telemetry,
        "bridge_telemetry": bridge_telemetry,
        "collapse_shadow_telemetry": collapse_shadow_telemetry,
        "position_frames": position_frames,
    }


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    settings = settings_api.load_layered_test_run_settings(base_dir)
    viz_settings = settings_api.load_json_file(base_dir / "test_run_v1_0.viz.settings.json")
    prepared = scenario.prepare_active_scenario(base_dir, settings_override=settings)
    summary = prepared["summary"]
    runtime_cfg = prepared["runtime_cfg"]
    initial_state = prepared["initial_state"]
    fleet_a_data = prepared["fleet_a_data"]
    fleet_b_data = prepared["fleet_b_data"]

    get_viz = partial(settings_api.get_visualization_setting, settings)

    effective_random_seed = int(summary["effective_random_seed"])
    effective_metatype_random_seed = int(summary["effective_metatype_random_seed"])
    effective_background_map_seed = int(summary["effective_background_map_seed"])
    fleet_a_color, fleet_b_color = scenario.resolve_fleet_plot_colors(fleet_a_data, fleet_b_data)
    display_language = str(get_viz("display_language", "EN")).upper()
    display_language = display_language if display_language in {"EN", "ZH"} else "EN"
    fleet_a_label = scenario.resolve_display_name(fleet_a_data, display_language)
    fleet_b_label = scenario.resolve_display_name(fleet_b_data, display_language)
    fleet_a_full_name = report_builder.resolve_name_with_fallback(
        fleet_a_data,
        display_language,
        True,
        "A",
    )
    fleet_b_full_name = report_builder.resolve_name_with_fallback(
        fleet_b_data,
        display_language,
        True,
        "B",
    )
    fleet_a_avatar = scenario.resolve_avatar_with_fallback(fleet_a_data, DEFAULT_AVATAR_A)
    fleet_b_avatar = scenario.resolve_avatar_with_fallback(fleet_b_data, DEFAULT_AVATAR_B)

    viz_cfg = {
        "animate_requested": bool(get_viz("animate", True)),
        "auto_zoom_2d": bool(get_viz("auto_zoom_2d", False)),
        "frame_stride": execution.DEFAULT_FRAME_STRIDE,
        "base_frame_interval_ms": int(get_viz("animation_frame_interval_ms", 100)),
        "animation_play_speed": float(get_viz("animation_play_speed", 1.0)),
        "unit_direction_mode": _require_choice(
            "visualization.vector_display_mode",
            get_viz("vector_display_mode", get_viz("unit_direction_mode", "effective")),
            {"effective", "free", "attack", "composite"},
        ),
        "show_attack_target_lines": bool(get_viz("show_attack_target_lines", False)),
        "tick_plots_follow_battlefield_tick": bool(get_viz("tick_plots_follow_battlefield_tick", False)),
        "print_tick_summary": bool(get_viz("print_tick_summary", True)),
        "plot_smoothing_ticks": int(get_viz("plot_smoothing_ticks", 5)),
        "plot_profile_requested": get_viz("plot_profile", "auto"),
    }
    if viz_cfg["base_frame_interval_ms"] < 1:
        raise ValueError(
            f"visualization.animation_frame_interval_ms must be >= 1, got {viz_cfg['base_frame_interval_ms']}"
        )
    if viz_cfg["animation_play_speed"] <= 0.0:
        raise ValueError(
            f"visualization.animation_play_speed must be > 0, got {viz_cfg['animation_play_speed']}"
        )
    viz_cfg["frame_interval_ms"] = max(
        1,
        int(round(viz_cfg["base_frame_interval_ms"] / viz_cfg["animation_play_speed"])),
    )

    run_export_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_export_stem = f"{DEFAULT_BATTLE_REPORT_TOPIC}_{run_export_timestamp}"
    export_video_cfg = _prepare_export_video_cfg(viz_settings, base_dir, run_export_stem)
    viz_cfg["animate"] = bool(viz_cfg["animate_requested"] or export_video_cfg["enabled"])
    viz_cfg["plot_diagnostics_enabled"] = bool(viz_cfg["animate"] or summary["observer_enabled"])

    test_mode = int(summary["test_mode"])
    runtime_decision_source_requested = str(summary["runtime_decision_source_requested"])
    runtime_decision_source_effective = str(summary["runtime_decision_source_effective"])
    _, viz_cfg["plot_profile"] = _resolve_plot_profile(
        viz_cfg["plot_profile_requested"],
        test_mode,
        runtime_decision_source_requested,
        runtime_decision_source_effective,
    )
    export_battle_report = int(test_mode) >= 1

    capture_target_directions = (
        viz_cfg["show_attack_target_lines"]
        or viz_cfg["unit_direction_mode"] in {"attack", "composite"}
    )
    result = run_active_surface(
        base_dir=base_dir,
        prepared_override=prepared,
        settings_override=settings,
        execution_overrides={
            "capture_positions": viz_cfg["animate"],
            "frame_stride": viz_cfg["frame_stride"],
            "include_target_lines": capture_target_directions,
            "print_tick_summary": viz_cfg["print_tick_summary"],
            "plot_diagnostics_enabled": viz_cfg["plot_diagnostics_enabled"],
            "post_elimination_extra_ticks": max(
                0,
                int(viz_settings.get("post_elimination_extra_ticks", 10)),
            ),
        },
        summary_override={
            "animate": viz_cfg["animate"],
            "export_battle_report": export_battle_report,
        },
    )
    movement_cfg = runtime_cfg["movement"]
    boundary_cfg = runtime_cfg["boundary"]
    contact_cfg = runtime_cfg["contact"]
    prepared_summary = result["prepared"]["summary"]
    initial_fleet_sizes = {
        fleet_id: sum(
            max(0.0, float(initial_state.units[unit_id].hit_points))
            for unit_id in fleet.unit_ids
            if unit_id in initial_state.units
        )
        for fleet_id, fleet in initial_state.fleets.items()
    }
    run_config_snapshot = {
        "initial_units_per_side": (
            int(len(initial_state.fleets["A"].unit_ids))
            if len(initial_state.fleets["A"].unit_ids) == len(initial_state.fleets["B"].unit_ids)
            else int(max(len(initial_state.fleets["A"].unit_ids), len(initial_state.fleets["B"].unit_ids)))
        ),
        "initial_units_a": int(len(initial_state.fleets["A"].unit_ids)),
        "initial_units_b": int(len(initial_state.fleets["B"].unit_ids)),
        "test_mode": int(test_mode),
        "test_mode_label": prepared_summary["test_mode_name"],
        "random_seed_effective": effective_random_seed,
        "background_map_seed_effective": effective_background_map_seed,
        "metatype_random_seed_effective": effective_metatype_random_seed,
        "runtime_decision_source_effective": prepared_summary["runtime_decision_source_effective"],
        "collapse_decision_source_effective": prepared_summary["runtime_decision_source_effective"],
        "movement_model_effective": prepared_summary["movement_model_effective"],
        "arena_size": float(initial_state.arena_size),
        "max_time_steps_effective": int(result["final_state"].tick),
        "unit_speed": float(next(iter(initial_state.units.values())).max_speed),
        "min_unit_spacing": float(contact_cfg["separation_radius"]),
        "movement_v3a_experiment_effective": movement_cfg["experiment_effective"],
        "centroid_probe_scale_effective": movement_cfg["centroid_probe_scale_effective"],
        "attack_range": float(contact_cfg["attack_range"]),
        "damage_per_tick": float(contact_cfg["damage_per_tick"]),
        "ch_enabled": bool(contact_cfg["ch_enabled"]),
        "contact_hysteresis_h": float(contact_cfg["contact_hysteresis_h"]),
        "fsr_enabled": bool(contact_cfg["fsr_enabled"]),
        "fsr_strength": float(contact_cfg["fsr_strength"]),
        "alpha_sep": float(contact_cfg["alpha_sep"]),
        "boundary_enabled": bool(boundary_cfg["enabled"]),
        "boundary_soft_strength": float(boundary_cfg["soft_strength"]),
        "boundary_hard_enabled": bool(boundary_cfg["hard_enabled"]),
        "boundary_hard_enabled_effective": bool(boundary_cfg["enabled"]) and bool(boundary_cfg["hard_enabled"]),
    }
    _maybe_export_battle_report(
        export_battle_report=export_battle_report,
        final_state=result["final_state"],
        alive_trajectory=result["alive_trajectory"],
        run_export_timestamp=run_export_timestamp,
        run_export_stem=run_export_stem,
        base_dir=base_dir,
        report_context={
            "settings_source_path": (base_dir / "test_run_v1_0.settings.json").as_posix(),
            "display_language": display_language,
            "random_seed_effective": effective_random_seed,
            "fleet_a_data": fleet_a_data,
            "fleet_b_data": fleet_b_data,
            "initial_fleet_sizes": initial_fleet_sizes,
            "fleet_size_trajectory": result["fleet_size_trajectory"],
            "observer_telemetry": result["observer_telemetry"],
            "combat_telemetry": result["combat_telemetry"],
            "bridge_telemetry": result["bridge_telemetry"],
            "collapse_shadow_telemetry": result["collapse_shadow_telemetry"],
            "run_config_snapshot": run_config_snapshot,
        },
    )
    if not viz_cfg["animate"]:
        return

    render_context = {
        "arena_size": float(initial_state.arena_size),
        "trajectory": result["trajectory"],
        "alive_trajectory": result["alive_trajectory"],
        "fleet_size_trajectory": result["fleet_size_trajectory"],
        "initial_fleet_sizes": initial_fleet_sizes,
        "position_frames": result["position_frames"],
        "final_state": result["final_state"],
        "fleet_a_label": fleet_a_label,
        "fleet_b_label": fleet_b_label,
        "fleet_a_full_name": fleet_a_full_name,
        "fleet_b_full_name": fleet_b_full_name,
        "fleet_a_avatar": fleet_a_avatar,
        "fleet_b_avatar": fleet_b_avatar,
        "fleet_a_color": fleet_a_color,
        "fleet_b_color": fleet_b_color,
        "display_language": display_language,
        "auto_zoom_2d": viz_cfg["auto_zoom_2d"],
        "frame_interval_ms": viz_cfg["frame_interval_ms"],
        "tick_plots_follow_battlefield_tick": viz_cfg["tick_plots_follow_battlefield_tick"],
        "unit_direction_mode": viz_cfg["unit_direction_mode"],
        "show_attack_target_lines": viz_cfg["show_attack_target_lines"],
        "background_seed": effective_background_map_seed,
        "viz_settings": viz_settings,
        "observer_telemetry": result["observer_telemetry"],
        "observer_enabled": prepared_summary["observer_enabled"],
        "plot_profile": viz_cfg["plot_profile"],
        "plot_smoothing_ticks": viz_cfg["plot_smoothing_ticks"],
        "export_video_cfg": export_video_cfg,
        "boundary_enabled": bool(boundary_cfg["enabled"]),
        "boundary_hard_enabled": bool(boundary_cfg["hard_enabled"]),
        "damage_per_tick": float(contact_cfg["damage_per_tick"]),
    }
    render_debug_context = {
        "test_mode_label": prepared_summary["test_mode_name"],
        "movement_model_effective": prepared_summary["movement_model_effective"],
        "cohesion_decision_source_effective": prepared_summary["runtime_decision_source_effective"],
        "pre_tl_target_substrate": movement_cfg["pre_tl_target_substrate"],
        "symmetric_movement_sync_enabled": movement_cfg["symmetric_movement_sync_enabled"],
        "continuous_fr_shaping_effective": movement_cfg["continuous_fr_shaping"]["effective"],
        "continuous_fr_shaping_mode_effective": movement_cfg["continuous_fr_shaping"]["mode_effective"],
        "odw_posture_bias_enabled_effective": movement_cfg["odw_posture_bias"]["enabled_effective"],
        "odw_posture_bias_k_effective": movement_cfg["odw_posture_bias"]["k_effective"],
        "odw_posture_bias_clip_delta_effective": movement_cfg["odw_posture_bias"]["clip_delta_effective"],
        "v3_connect_radius_multiplier_effective": movement_cfg["v3_connect_radius_multiplier_effective"],
        "plot_smoothing_ticks": viz_cfg["plot_smoothing_ticks"],
    }
    _render_animation(
        render_context=render_context,
        combat_telemetry=result["combat_telemetry"],
        bridge_telemetry=result["bridge_telemetry"],
        debug_context=render_debug_context,
    )


if __name__ == "__main__":
    main()
