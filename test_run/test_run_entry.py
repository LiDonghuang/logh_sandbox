import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from test_run import test_run_execution as execution
from test_run import test_run_scenario as scenario


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
        f"[run] mode={test_mode_name} "
        f"movement={movement_model_effective} "
        f"cohesion={runtime_decision_source_effective} "
        f"contact_model={hostile_contact_impedance_mode} "
        f"animate={animate} observer={observer_enabled} report={export_battle_report} "
        f"seeds={effective_random_seed}/{effective_metatype_random_seed}/{effective_background_map_seed}"
    )


def run_active_surface(
    *,
    base_dir: Path | None = None,
    settings_override: dict | None = None,
    emit_summary: bool = True,
) -> dict:
    active_base_dir = base_dir or Path(__file__).resolve().parent
    prepared = scenario.prepare_active_scenario(
        active_base_dir,
        settings_override=settings_override,
    )
    if emit_summary:
        _print_run_summary(**prepared["summary"])
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
        execution_cfg=prepared["execution_cfg"],
        runtime_cfg=prepared["runtime_cfg"],
        observer_cfg=prepared["observer_cfg"],
    )
    return {
        "prepared": prepared,
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
    run_active_surface()


if __name__ == "__main__":
    main()
