import os
import random
import sys
from dataclasses import replace
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


def _get_env_int(name: str) -> int | None:
    raw = os.environ.get(name)
    if raw is None:
        return None
    try:
        return int(str(raw).strip())
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be an integer, got {raw!r}") from exc


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


def _prepare_viz_cfg(
    *,
    base_dir: Path,
    settings: dict,
    summary: dict,
    run_export_stem: str,
) -> tuple[dict, dict, dict, str]:
    viz_settings = settings_api.load_json_file(base_dir / "test_run_v1_0.viz.settings.json")
    get_viz = partial(settings_api.get_visualization_setting, settings)
    display_language = str(get_viz("display_language", "EN")).upper()
    display_language = display_language if display_language in {"EN", "ZH"} else "EN"
    viz_cfg = {
        "animate_requested": bool(get_viz("animate", True)),
        "auto_zoom_2d": bool(get_viz("auto_zoom_2d", False)),
        "frame_stride": execution.DEFAULT_FRAME_STRIDE,
        "base_frame_interval_ms": int(get_viz("animation_frame_interval_ms", 100)),
        "animation_play_speed": float(get_viz("animation_play_speed", 1.0)),
        "unit_direction_mode": _require_choice(
            "visualization.vector_display_mode",
            get_viz("vector_display_mode", "effective"),
            {"effective", "free", "attack", "composite", "radial_debug"},
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

    export_video_cfg = _prepare_export_video_cfg(viz_settings, base_dir, run_export_stem)
    viz_cfg["animate"] = bool(viz_cfg["animate_requested"] or export_video_cfg["enabled"])
    viz_cfg["plot_diagnostics_enabled"] = bool(viz_cfg["animate"] or summary["observer_enabled"])
    _, viz_cfg["plot_profile"] = _resolve_plot_profile(
        viz_cfg["plot_profile_requested"],
        int(summary["test_mode"]),
        str(summary["runtime_decision_source_requested"]),
        str(summary["runtime_decision_source_effective"]),
    )
    return viz_settings, viz_cfg, export_video_cfg, display_language


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


def _export_map_batch(
    *,
    base_dir: Path,
    settings: dict,
    batch_count: int,
    batch_seed: int,
) -> None:
    import matplotlib.pyplot as plt
    from runtime.runtime_v0_1 import BattleState, FleetState, PersonalityParameters
    from test_run.test_run_v1_0_viz import render_test_run

    if batch_count <= 0:
        raise ValueError(f"LOGH_VIZ_EXPORT_MAP_COUNT must be > 0, got {batch_count}")

    viz_settings = settings_api.load_json_file(base_dir / "test_run_v1_0.viz.settings.json")
    arena_size = float(settings_api.get_battlefield_setting(settings, "arena_size", 200.0))
    boundary_enabled = bool(settings_api.get_runtime_setting(settings, "boundary_enabled", False))
    boundary_hard_enabled = bool(settings_api.get_runtime_setting(settings, "boundary_hard_enabled", True))
    output_root = (base_dir.parent / "analysis" / "exports" / "viz_maps" / datetime.now().strftime("%Y%m%d")).resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    vector_display_mode = _require_choice(
        "visualization.vector_display_mode",
        settings_api.get_visualization_setting(settings, "vector_display_mode", "effective"),
        {"effective", "free", "attack", "composite", "radial_debug"},
    )

    dummy_params = PersonalityParameters(
        archetype_id="map_export",
        force_concentration_ratio=5.0,
        mobility_bias=5.0,
        offense_defense_weight=5.0,
        risk_appetite=5.0,
        time_preference=5.0,
        targeting_logic=5.0,
        formation_rigidity=5.0,
        perception_radius=5.0,
        pursuit_drive=5.0,
        retreat_threshold=5.0,
    )
    empty_state = BattleState(
        tick=0,
        dt=1.0,
        arena_size=arena_size,
        units={},
        fleets={
            "A": FleetState(fleet_id="A", parameters=dummy_params, unit_ids=()),
            "B": FleetState(fleet_id="B", parameters=dummy_params, unit_ids=()),
        },
        last_fleet_cohesion={"A": 0.0, "B": 0.0},
        last_target_direction={"A": (0.0, 0.0), "B": (0.0, 0.0)},
        last_engagement_intensity={"A": 0.0, "B": 0.0},
    )
    seed_rng = random.Random(batch_seed)
    map_seeds = [seed_rng.randrange(0, 2**32) for _ in range(batch_count)]

    original_show = plt.show
    plt.ioff()
    plt.show = lambda *args, **kwargs: None
    try:
        print(f"[viz-map-batch] exporting count={batch_count} base_seed={batch_seed} output_dir={output_root}")
        for index, map_seed in enumerate(map_seeds, start=1):
            plt.close("all")
            render_test_run(
                arena_size=arena_size,
                trajectory={"A": [0.0], "B": [0.0]},
                alive_trajectory={"A": [0], "B": [0]},
                fleet_size_trajectory={"A": [0.0], "B": [0.0]},
                initial_fleet_sizes={"A": 0.0, "B": 0.0},
                position_frames=[],
                final_state=empty_state,
                fleet_a_label="",
                fleet_b_label="",
                fleet_a_full_name="",
                fleet_b_full_name="",
                fleet_a_avatar="",
                fleet_b_avatar="",
                fleet_a_color="#4f6cff",
                fleet_b_color="#ff6b6b",
                auto_zoom_2d=False,
                frame_interval_ms=100,
                background_seed=int(map_seed),
                viz_settings=viz_settings,
                tick_plots_follow_battlefield_tick=False,
                display_language="EN",
                unit_direction_mode=vector_display_mode,
                show_attack_target_lines=False,
                observer_telemetry={},
                bridge_telemetry={},
                observer_enabled=False,
                plot_profile="baseline",
                plot_smoothing_ticks=5,
                combat_telemetry={"in_contact_count": [0]},
                debug_context={"map_export_only": True},
                export_video_cfg={"enabled": False},
                boundary_enabled=boundary_enabled,
                boundary_hard_enabled=boundary_hard_enabled,
                damage_per_tick=1.0,
            )
            output_path = output_root / f"viz_map_runtime_{index:02d}_seed_{map_seed}.png"
            plt.gcf().savefig(output_path, dpi=120, bbox_inches="tight")
            print(f"[viz-map-batch] exported={output_path}")
        plt.close("all")
    finally:
        plt.show = original_show


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


def _run_neutral_transit_fixture(*, base_dir: Path, settings: dict) -> None:
    prepared = scenario.prepare_neutral_transit_fixture(base_dir, settings_override=settings)
    summary = prepared["summary"]
    runtime_cfg = prepared["runtime_cfg"]
    fleet_data = prepared["fleet_data"]
    run_export_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_export_stem = f"{DEFAULT_BATTLE_REPORT_TOPIC}_{run_export_timestamp}"
    viz_settings, viz_cfg, export_video_cfg, display_language = _prepare_viz_cfg(
        base_dir=base_dir,
        settings=settings,
        summary=summary,
        run_export_stem=run_export_stem,
    )
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
            "post_elimination_extra_ticks": int(prepared["execution_cfg"]["post_elimination_extra_ticks"]),
        },
        summary_override={
            "animate": viz_cfg["animate"],
            "export_battle_report": False,
        },
        emit_summary=False,
    )
    summary = result["prepared"]["summary"]
    fixture_metrics = result["observer_telemetry"].get("fixture", {})
    anchor_point_xyz = fixture_metrics.get("anchor_point_xyz", [0.0, 0.0, 0.0])
    projected_anchor_point_xy = fixture_metrics.get("projected_anchor_point_xy", [0.0, 0.0])
    source_owner = str(fixture_metrics.get("source_owner", ""))
    objective_mode = str(fixture_metrics.get("objective_mode", ""))
    no_enemy_semantics = str(fixture_metrics.get("no_enemy_semantics", ""))
    stop_radius = float(fixture_metrics.get("stop_radius", 0.0))
    objective_reached_tick = fixture_metrics.get("objective_reached_tick")
    distances = [float(value) for value in fixture_metrics.get("centroid_to_objective_distance", [])]
    radius_ratios = [float(value) for value in fixture_metrics.get("formation_rms_radius_ratio", [])]
    projection_pairs = [int(value) for value in fixture_metrics.get("projection_pairs_count", [])]
    projection_mean = [float(value) for value in fixture_metrics.get("projection_mean_displacement", [])]
    projection_max = [float(value) for value in fixture_metrics.get("projection_max_displacement", [])]
    print(
        f"[fixture] mode={execution.FIXTURE_MODE_NEUTRAL} "
        f"movement={summary['movement_model_effective']} "
        f"arrival_tick={objective_reached_tick} "
        f"final_tick={int(result['final_state'].tick)} "
        f"objective=({float(projected_anchor_point_xy[0]):.2f},{float(projected_anchor_point_xy[1]):.2f}) "
        f"stop_radius={stop_radius:.2f}"
    )
    print(
        f"[fixture] objective_contract_3d "
        f"anchor_xyz=({float(anchor_point_xyz[0]):.2f},{float(anchor_point_xyz[1]):.2f},{float(anchor_point_xyz[2]):.2f}) "
        f"projected_xy=({float(projected_anchor_point_xy[0]):.2f},{float(projected_anchor_point_xy[1]):.2f}) "
        f"owner={source_owner} mode={objective_mode} no_enemy={no_enemy_semantics} "
        f"fleet_id={fixture_metrics.get('fleet_id', 'A')}"
    )
    if distances:
        print(
            f"[fixture] centroid_to_objective_distance "
            f"initial={float(fixture_metrics.get('initial_centroid_to_objective_distance', float('nan'))):.3f} "
            f"final={distances[-1]:.3f} "
            f"min={min(distances):.3f}"
        )
    if radius_ratios:
        print(
            f"[fixture] formation_rms_radius_ratio "
            f"final={radius_ratios[-1]:.3f} "
            f"max={max(radius_ratios):.3f}"
        )
    if projection_pairs or projection_mean or projection_max:
        print(
            f"[fixture] projection_activity "
            f"pairs_peak={max(projection_pairs) if projection_pairs else 0} "
            f"mean_disp_peak={max(projection_mean) if projection_mean else 0.0:.3f} "
            f"max_disp_peak={max(projection_max) if projection_max else 0.0:.3f}"
        )
    if not viz_cfg["animate"]:
        return

    movement_cfg = runtime_cfg["movement"]
    boundary_cfg = runtime_cfg["boundary"]
    contact_cfg = runtime_cfg["contact"]
    initial_state = prepared["initial_state"]
    fleet_a_color, _ = scenario.resolve_fleet_plot_colors(fleet_data, {})
    fleet_b_color = "#b8b8b8"
    fleet_a_label = scenario.resolve_display_name(fleet_data, display_language) or "A"
    fleet_a_full_name = report_builder.resolve_name_with_fallback(
        fleet_data,
        display_language,
        True,
        "A",
    )
    fleet_a_avatar = scenario.resolve_avatar_with_fallback(fleet_data, DEFAULT_AVATAR_A)
    fleet_b_label = "No Enemy"
    fleet_b_full_name = fleet_b_label
    tick_count = len(result["alive_trajectory"].get("A", []))
    cohesion_tick_count = len(result["trajectory"].get("A", []))
    render_final_state = replace(
        result["final_state"],
        fleets={
            **dict(result["final_state"].fleets),
            "B": type(initial_state.fleets["A"])(
                fleet_id="B",
                parameters=initial_state.fleets["A"].parameters,
                unit_ids=(),
            ),
        },
        last_fleet_cohesion={
            **dict(result["final_state"].last_fleet_cohesion),
            "B": 0.0,
        },
    )
    render_context = {
        "arena_size": float(initial_state.arena_size),
        "trajectory": {
            "A": list(result["trajectory"].get("A", [])),
            "B": [float("nan")] * cohesion_tick_count,
        },
        "alive_trajectory": {
            "A": list(result["alive_trajectory"].get("A", [])),
            "B": [0] * tick_count,
        },
        "fleet_size_trajectory": {
            "A": list(result["fleet_size_trajectory"].get("A", [])),
            "B": [0.0] * tick_count,
        },
        "initial_fleet_sizes": {
            "A": float(len(initial_state.fleets["A"].unit_ids)),
            "B": 0.0,
        },
        "position_frames": result["position_frames"],
        "final_state": render_final_state,
        "fleet_a_label": fleet_a_label,
        "fleet_b_label": fleet_b_label,
        "fleet_a_full_name": fleet_a_full_name,
        "fleet_b_full_name": fleet_b_full_name,
        "fleet_a_avatar": fleet_a_avatar,
        "fleet_b_avatar": "",
        "fleet_a_color": fleet_a_color,
        "fleet_b_color": fleet_b_color,
        "display_language": display_language,
        "auto_zoom_2d": viz_cfg["auto_zoom_2d"],
        "frame_interval_ms": viz_cfg["frame_interval_ms"],
        "tick_plots_follow_battlefield_tick": viz_cfg["tick_plots_follow_battlefield_tick"],
        "unit_direction_mode": viz_cfg["unit_direction_mode"],
        "show_attack_target_lines": viz_cfg["show_attack_target_lines"],
        "background_seed": int(summary["effective_background_map_seed"]),
        "viz_settings": viz_settings,
        "observer_telemetry": result["observer_telemetry"],
        "observer_enabled": bool(summary["observer_enabled"]),
        "plot_profile": viz_cfg["plot_profile"],
        "plot_smoothing_ticks": viz_cfg["plot_smoothing_ticks"],
        "export_video_cfg": export_video_cfg,
        "boundary_enabled": bool(boundary_cfg["enabled"]),
        "boundary_hard_enabled": bool(boundary_cfg["hard_enabled"]),
        "damage_per_tick": float(contact_cfg["damage_per_tick"]),
    }
    render_debug_context = {
        "test_mode_label": summary["test_mode_name"],
        "movement_model_effective": summary["movement_model_effective"],
        "cohesion_decision_source_effective": summary["runtime_decision_source_effective"],
        "symmetric_movement_sync_enabled": movement_cfg["symmetric_movement_sync_enabled"],
        "v3_connect_radius_multiplier_effective": movement_cfg["v3_connect_radius_multiplier_effective"],
        "plot_smoothing_ticks": viz_cfg["plot_smoothing_ticks"],
        "fixture_mode": execution.FIXTURE_MODE_NEUTRAL,
    }
    if movement_cfg["model_effective"] == "v3a":
        render_debug_context["odw_posture_bias_enabled_effective"] = movement_cfg["odw_posture_bias"]["enabled_effective"]
        render_debug_context["odw_posture_bias_k_effective"] = movement_cfg["odw_posture_bias"]["k_effective"]
        render_debug_context["odw_posture_bias_clip_delta_effective"] = movement_cfg["odw_posture_bias"]["clip_delta_effective"]
    _render_animation(
        render_context=render_context,
        combat_telemetry=result["combat_telemetry"],
        bridge_telemetry=result["bridge_telemetry"],
        debug_context=render_debug_context,
    )


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    settings = settings_api.load_layered_test_run_settings(base_dir)
    map_batch_count = _get_env_int("LOGH_VIZ_EXPORT_MAP_COUNT")
    map_batch_seed_override = _get_env_int("LOGH_VIZ_EXPORT_MAP_BASE_SEED")
    if map_batch_count is not None:
        configured_background_map_seed = int(settings_api.get_battlefield_setting(settings, "background_map_seed", -1))
        _export_map_batch(
            base_dir=base_dir,
            settings=settings,
            batch_count=map_batch_count,
            batch_seed=(
                map_batch_seed_override
                if map_batch_seed_override is not None
                else scenario.resolve_effective_seed(configured_background_map_seed)
            ),
        )
        return
    active_mode = _require_choice(
        "fixture.active_mode",
        settings_api.get_fixture_setting(settings, ("active_mode",), execution.FIXTURE_MODE_BATTLE),
        execution.FIXTURE_MODE_LABELS,
    )
    if active_mode == execution.FIXTURE_MODE_NEUTRAL:
        _run_neutral_transit_fixture(base_dir=base_dir, settings=settings)
        return
    prepared = scenario.prepare_active_scenario(base_dir, settings_override=settings)
    summary = prepared["summary"]
    runtime_cfg = prepared["runtime_cfg"]
    initial_state = prepared["initial_state"]
    fleet_a_data = prepared["fleet_a_data"]
    fleet_b_data = prepared["fleet_b_data"]

    effective_random_seed = int(summary["effective_random_seed"])
    effective_metatype_random_seed = int(summary["effective_metatype_random_seed"])
    effective_background_map_seed = int(summary["effective_background_map_seed"])
    run_export_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_export_stem = f"{DEFAULT_BATTLE_REPORT_TOPIC}_{run_export_timestamp}"
    (
        viz_settings,
        viz_cfg,
        export_video_cfg,
        display_language,
    ) = _prepare_viz_cfg(
        base_dir=base_dir,
        settings=settings,
        summary=summary,
        run_export_stem=run_export_stem,
    )
    fleet_a_color, fleet_b_color = scenario.resolve_fleet_plot_colors(fleet_a_data, fleet_b_data)
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
    test_mode = int(summary["test_mode"])
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
            "post_elimination_extra_ticks": int(prepared["execution_cfg"]["post_elimination_extra_ticks"]),
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
    if movement_cfg["model_effective"] == "v3a":
        run_config_snapshot["movement_v3a_experiment_effective"] = movement_cfg["experiment_effective"]
        run_config_snapshot["centroid_probe_scale_effective"] = movement_cfg["centroid_probe_scale_effective"]
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
        "symmetric_movement_sync_enabled": movement_cfg["symmetric_movement_sync_enabled"],
        "v3_connect_radius_multiplier_effective": movement_cfg["v3_connect_radius_multiplier_effective"],
        "plot_smoothing_ticks": viz_cfg["plot_smoothing_ticks"],
    }
    if movement_cfg["model_effective"] == "v3a":
        render_debug_context["odw_posture_bias_enabled_effective"] = movement_cfg["odw_posture_bias"]["enabled_effective"]
        render_debug_context["odw_posture_bias_k_effective"] = movement_cfg["odw_posture_bias"]["k_effective"]
        render_debug_context["odw_posture_bias_clip_delta_effective"] = movement_cfg["odw_posture_bias"]["clip_delta_effective"]
    _render_animation(
        render_context=render_context,
        combat_telemetry=result["combat_telemetry"],
        bridge_telemetry=result["bridge_telemetry"],
        debug_context=render_debug_context,
    )


if __name__ == "__main__":
    main()
