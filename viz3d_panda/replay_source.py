from __future__ import annotations

import copy
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from test_run import test_run_entry
from test_run import test_run_scenario as scenario
from test_run import settings_accessor as settings_api


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEST_RUN_BASE_DIR = PROJECT_ROOT / "test_run"
DEFAULT_VIEWER_MAX_STEPS = 240
DEFAULT_FRAME_STRIDE = 1
DEFAULT_FLEET_PALETTE = ("#4f8cff", "#ff7b52", "#59d38c", "#f3c84b")
FRAME_CONTROL_KEYS = {"tick", "targets", "runtime_debug"}


@dataclass(frozen=True)
class ViewerUnitState:
    unit_id: str
    fleet_id: str
    x: float
    y: float
    z: float
    heading_x: float
    heading_y: float
    velocity_x: float
    velocity_y: float


@dataclass(frozen=True)
class ViewerFrame:
    tick: int
    units: tuple[ViewerUnitState, ...]
    targets: dict[str, str]


@dataclass(frozen=True)
class ReplayBundle:
    source_kind: str
    arena_size: float
    frames: tuple[ViewerFrame, ...]
    fleet_labels: dict[str, str]
    fleet_colors: dict[str, str]
    metadata: dict[str, Any]


def _deep_clone_settings(settings: dict[str, Any]) -> dict[str, Any]:
    return copy.deepcopy(settings)


def _parse_unit_point(raw_point: Any, *, fleet_id: str) -> ViewerUnitState:
    if not isinstance(raw_point, (list, tuple)) or len(raw_point) < 5:
        raise ValueError(
            "position_frames entries must be tuples of at least "
            f"(unit_id, x, y, heading_x, heading_y); got {raw_point!r} for fleet {fleet_id!r}"
        )
    unit_id = str(raw_point[0])
    velocity_x = float(raw_point[5]) if len(raw_point) >= 7 else 0.0
    velocity_y = float(raw_point[6]) if len(raw_point) >= 7 else 0.0
    return ViewerUnitState(
        unit_id=unit_id,
        fleet_id=str(fleet_id),
        x=float(raw_point[1]),
        y=float(raw_point[2]),
        z=0.0,
        heading_x=float(raw_point[3]),
        heading_y=float(raw_point[4]),
        velocity_x=velocity_x,
        velocity_y=velocity_y,
    )


def _default_fleet_colors(fleet_ids: list[str]) -> dict[str, str]:
    palette = list(DEFAULT_FLEET_PALETTE)
    colors: dict[str, str] = {}
    for index, fleet_id in enumerate(fleet_ids):
        colors[fleet_id] = palette[index % len(palette)]
    return colors


def build_replay_bundle(
    *,
    source_kind: str,
    arena_size: float,
    position_frames: list[dict[str, Any]],
    fleet_labels: dict[str, str] | None = None,
    fleet_colors: dict[str, str] | None = None,
    metadata: dict[str, Any] | None = None,
) -> ReplayBundle:
    if not position_frames:
        raise ValueError("position_frames is empty; viewer bootstrap requires captured frame data.")

    frames: list[ViewerFrame] = []
    seen_fleet_ids: list[str] = []
    for raw_frame in position_frames:
        if not isinstance(raw_frame, dict):
            raise ValueError(f"Each position frame must be a mapping, got {type(raw_frame).__name__}.")
        tick = int(raw_frame.get("tick", len(frames)))
        units: list[ViewerUnitState] = []
        for fleet_id, points in raw_frame.items():
            if fleet_id in FRAME_CONTROL_KEYS:
                continue
            if not isinstance(points, list):
                raise ValueError(
                    f"Frame fleet bucket {fleet_id!r} must be a list of unit tuples, got {type(points).__name__}."
                )
            if fleet_id not in seen_fleet_ids:
                seen_fleet_ids.append(str(fleet_id))
            for raw_point in points:
                units.append(_parse_unit_point(raw_point, fleet_id=str(fleet_id)))
        raw_targets = raw_frame.get("targets", {})
        if raw_targets and not isinstance(raw_targets, dict):
            raise ValueError(f"frame['targets'] must be a dict when present, got {type(raw_targets).__name__}.")
        frames.append(
            ViewerFrame(
                tick=tick,
                units=tuple(units),
                targets={str(key): str(value) for key, value in dict(raw_targets).items()},
            )
        )

    resolved_labels = dict(fleet_labels or {})
    for fleet_id in seen_fleet_ids:
        resolved_labels.setdefault(fleet_id, str(fleet_id))

    resolved_colors = _default_fleet_colors(seen_fleet_ids)
    if fleet_colors:
        resolved_colors.update({str(key): str(value) for key, value in fleet_colors.items()})

    replay_metadata = dict(metadata or {})
    replay_metadata.setdefault("frame_count", len(frames))
    replay_metadata.setdefault("fleet_ids", tuple(seen_fleet_ids))
    return ReplayBundle(
        source_kind=str(source_kind),
        arena_size=float(arena_size),
        frames=tuple(frames),
        fleet_labels=resolved_labels,
        fleet_colors=resolved_colors,
        metadata=replay_metadata,
    )


def load_active_battle_replay(
    *,
    max_steps: int = DEFAULT_VIEWER_MAX_STEPS,
    frame_stride: int = DEFAULT_FRAME_STRIDE,
) -> ReplayBundle:
    if frame_stride < 1:
        raise ValueError(f"frame_stride must be >= 1, got {frame_stride}.")
    if max_steps != -1 and max_steps < 1:
        raise ValueError(f"max_steps must be -1 or >= 1, got {max_steps}.")

    settings = settings_api.load_layered_test_run_settings(TEST_RUN_BASE_DIR)
    active_settings = _deep_clone_settings(settings)
    run_control = active_settings.setdefault("run_control", {})
    if not isinstance(run_control, dict):
        raise ValueError("run_control must be a mapping in layered test_run settings.")
    run_control["max_time_steps"] = int(max_steps)

    prepared = scenario.prepare_active_scenario(TEST_RUN_BASE_DIR, settings_override=active_settings)
    result = test_run_entry.run_active_surface(
        base_dir=TEST_RUN_BASE_DIR,
        prepared_override=prepared,
        settings_override=active_settings,
        execution_overrides={
            "capture_positions": True,
            "frame_stride": int(frame_stride),
            "include_target_lines": False,
            "print_tick_summary": False,
        },
        summary_override={
            "animate": False,
            "export_battle_report": False,
        },
        emit_summary=False,
    )

    fleet_a_data = prepared["fleet_a_data"]
    fleet_b_data = prepared["fleet_b_data"]
    fleet_a_color, fleet_b_color = scenario.resolve_fleet_plot_colors(fleet_a_data, fleet_b_data)

    return build_replay_bundle(
        source_kind="test_run_active_surface",
        arena_size=float(prepared["initial_state"].arena_size),
        position_frames=result["position_frames"],
        fleet_labels={
            "A": scenario.resolve_display_name(fleet_a_data, "EN"),
            "B": scenario.resolve_display_name(fleet_b_data, "EN"),
        },
        fleet_colors={
            "A": fleet_a_color,
            "B": fleet_b_color,
        },
        metadata={
            "summary": dict(result["prepared"]["summary"]),
            "max_steps": int(max_steps),
            "frame_stride": int(frame_stride),
        },
    )
