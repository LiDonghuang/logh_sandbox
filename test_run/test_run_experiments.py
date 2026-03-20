"""Transitional shell for the former mixed execution host.

The maintained spine now lives in:
- test_run_scenario.py
- test_run_execution.py
- test_run_telemetry.py
"""

from test_run.test_run_execution import (
    SimulationBoundaryConfig,
    SimulationContactConfig,
    SimulationExecutionConfig,
    SimulationMovementConfig,
    SimulationObserverConfig,
    SimulationRuntimeConfig,
    run_simulation,
)
from test_run.test_run_scenario import build_initial_state
from test_run.test_run_telemetry import (
    compute_bridge_metrics_per_side,
    compute_collapse_v2_shadow_telemetry,
    compute_formation_snapshot_metrics,
    compute_hostile_intermix_metrics,
    extract_runtime_debug_payload,
)


__all__ = [
    "SimulationBoundaryConfig",
    "SimulationContactConfig",
    "SimulationExecutionConfig",
    "SimulationMovementConfig",
    "SimulationObserverConfig",
    "SimulationRuntimeConfig",
    "build_initial_state",
    "compute_bridge_metrics_per_side",
    "compute_collapse_v2_shadow_telemetry",
    "compute_formation_snapshot_metrics",
    "compute_hostile_intermix_metrics",
    "extract_runtime_debug_payload",
    "run_simulation",
]
