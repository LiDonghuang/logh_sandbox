import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from test_run import settings_accessor as settings_api
from test_run import test_run_execution as execution
from test_run import test_run_scenario as scenario


def _require_choice(name: str, raw_value, allowed: set[str]) -> str:
    value = str(raw_value).strip().lower()
    if value not in allowed:
        allowed_text = ", ".join(sorted(allowed))
        raise ValueError(f"{name} must be one of {{{allowed_text}}}, got {raw_value!r}")
    return value


def _print_run_summary(
    *,
    effective_random_seed: int,
    effective_metatype_random_seed: int,
    effective_background_map_seed: int,
    movement_model_effective: str,
    hostile_contact_impedance_mode: str,
    observer_enabled: bool = False,
    **_ignored,
) -> None:
    print(
        f"[run] movement={movement_model_effective} "
        f"contact={hostile_contact_impedance_mode} "
        f"observer={observer_enabled} "
        f"seeds={effective_random_seed}/{effective_metatype_random_seed}/{effective_background_map_seed}"
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
        "position_frames": position_frames,
    }


def _run_neutral_fixture(*, base_dir: Path, settings: dict) -> None:
    prepared = scenario.prepare_neutral_transit_fixture(base_dir, settings_override=settings)
    print_tick_summary = bool(settings_api.get_visualization_setting(settings, "print_tick_summary", True))
    result = run_active_surface(
        base_dir=base_dir,
        prepared_override=prepared,
        settings_override=settings,
        execution_overrides={
            "print_tick_summary": print_tick_summary,
            "post_elimination_extra_ticks": int(prepared["execution_cfg"]["post_elimination_extra_ticks"]),
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


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    settings = settings_api.load_layered_test_run_settings(base_dir)
    active_mode = _require_choice(
        "fixture.active_mode",
        settings_api.get_fixture_setting(settings, ("active_mode",), execution.FIXTURE_MODE_BATTLE),
        execution.FIXTURE_MODE_LABELS,
    )
    if active_mode == execution.FIXTURE_MODE_NEUTRAL:
        _run_neutral_fixture(base_dir=base_dir, settings=settings)
        return

    prepared = scenario.prepare_active_scenario(base_dir, settings_override=settings)
    print_tick_summary = bool(settings_api.get_visualization_setting(settings, "print_tick_summary", True))
    run_active_surface(
        base_dir=base_dir,
        prepared_override=prepared,
        settings_override=settings,
        execution_overrides={
            "print_tick_summary": print_tick_summary,
            "post_elimination_extra_ticks": int(prepared["execution_cfg"]["post_elimination_extra_ticks"]),
        },
    )


if __name__ == "__main__":
    main()
