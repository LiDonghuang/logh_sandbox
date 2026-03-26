from __future__ import annotations

import copy
import math
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

from test_run import test_run_entry
from test_run import test_run_scenario as scenario
from test_run import settings_accessor as settings_api


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEST_RUN_BASE_DIR = PROJECT_ROOT / "test_run"
DEFAULT_FRAME_STRIDE = 1
DEFAULT_FLEET_PALETTE = ("#4f8cff", "#ff7b52", "#59d38c", "#f3c84b")
FRAME_CONTROL_KEYS = {"tick", "targets", "runtime_debug"}
VALID_VECTOR_DISPLAY_MODES = {"effective", "free", "attack", "composite", "radial_debug"}


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
    hit_points: float
    max_hit_points: float


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
    hit_points = float(raw_point[7]) if len(raw_point) >= 9 else 100.0
    max_hit_points = float(raw_point[8]) if len(raw_point) >= 9 else max(1.0, hit_points)
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
        hit_points=hit_points,
        max_hit_points=max_hit_points,
    )


def _default_fleet_colors(fleet_ids: list[str]) -> dict[str, str]:
    palette = list(DEFAULT_FLEET_PALETTE)
    colors: dict[str, str] = {}
    for index, fleet_id in enumerate(fleet_ids):
        colors[fleet_id] = palette[index % len(palette)]
    return colors


def _normalize_vector(dx: float, dy: float) -> tuple[float, float]:
    norm = math.sqrt((float(dx) * float(dx)) + (float(dy) * float(dy)))
    if norm <= 1e-12:
        return (0.0, 0.0)
    return (float(dx) / norm, float(dy) / norm)


def _resolve_vector_display_mode(settings: dict[str, Any]) -> str:
    raw_value = settings_api.get_visualization_setting(
        settings,
        "vector_display_mode",
        settings_api.get_visualization_setting(settings, "unit_direction_mode", "effective"),
    )
    mode = str(raw_value).strip().lower()
    if mode not in VALID_VECTOR_DISPLAY_MODES:
        return "effective"
    return mode


def _build_attack_direction_map(
    units: tuple[ViewerUnitState, ...],
    targets: dict[str, str],
) -> dict[str, tuple[float, float]]:
    if not targets:
        return {}
    point_map = {str(unit.unit_id): (float(unit.x), float(unit.y)) for unit in units}
    direction_map: dict[str, tuple[float, float]] = {}
    for attacker_id, defender_id in targets.items():
        attacker = point_map.get(str(attacker_id))
        defender = point_map.get(str(defender_id))
        if attacker is None or defender is None:
            continue
        direction_map[str(attacker_id)] = _normalize_vector(
            float(defender[0]) - float(attacker[0]),
            float(defender[1]) - float(attacker[1]),
        )
    return direction_map


def _fleet_centroids(units: tuple[ViewerUnitState, ...]) -> dict[str, tuple[float, float]]:
    accum: dict[str, tuple[float, float, int]] = {}
    for unit in units:
        sx, sy, count = accum.get(unit.fleet_id, (0.0, 0.0, 0))
        accum[unit.fleet_id] = (sx + float(unit.x), sy + float(unit.y), count + 1)
    return {
        fleet_id: (sx / float(count), sy / float(count))
        for fleet_id, (sx, sy, count) in accum.items()
        if count > 0
    }


def _resolve_frame_display_units(
    units: tuple[ViewerUnitState, ...],
    *,
    targets: dict[str, str],
    vector_display_mode: str,
    previous_positions_by_fleet: dict[str, dict[str, tuple[float, float]]],
) -> tuple[ViewerUnitState, ...]:
    attack_direction_map = _build_attack_direction_map(units, targets)
    centroids = _fleet_centroids(units)
    resolved_units: list[ViewerUnitState] = []
    next_positions_by_fleet: dict[str, dict[str, tuple[float, float]]] = {}

    for unit in units:
        prev_positions = previous_positions_by_fleet.get(unit.fleet_id, {})
        previous = prev_positions.get(unit.unit_id)
        if previous is None:
            effective_x = float(unit.heading_x)
            effective_y = float(unit.heading_y)
        else:
            effective_x = float(unit.x) - float(previous[0])
            effective_y = float(unit.y) - float(previous[1])
        effective_direction = _normalize_vector(effective_x, effective_y)
        free_direction = _normalize_vector(unit.velocity_x, unit.velocity_y)
        attack_direction = attack_direction_map.get(unit.unit_id)

        if vector_display_mode == "free":
            display_direction = free_direction
        elif vector_display_mode == "attack":
            display_direction = attack_direction if attack_direction is not None else effective_direction
        elif vector_display_mode == "composite":
            if attack_direction is None:
                display_direction = effective_direction
            else:
                display_direction = _normalize_vector(
                    float(attack_direction[0]) + float(effective_direction[0]),
                    float(attack_direction[1]) + float(effective_direction[1]),
                )
                if display_direction == (0.0, 0.0):
                    display_direction = effective_direction
        elif vector_display_mode == "radial_debug":
            centroid = centroids.get(unit.fleet_id)
            if centroid is None:
                display_direction = (0.0, 0.0)
            else:
                display_direction = _normalize_vector(
                    float(centroid[0]) - float(unit.x),
                    float(centroid[1]) - float(unit.y),
                )
        else:
            display_direction = effective_direction

        resolved_units.append(
            replace(
                unit,
                heading_x=float(display_direction[0]),
                heading_y=float(display_direction[1]),
            )
        )
        next_positions_by_fleet.setdefault(unit.fleet_id, {})[unit.unit_id] = (float(unit.x), float(unit.y))

    previous_positions_by_fleet.clear()
    previous_positions_by_fleet.update(next_positions_by_fleet)
    return tuple(resolved_units)


def build_replay_bundle(
    *,
    source_kind: str,
    arena_size: float,
    position_frames: list[dict[str, Any]],
    fleet_labels: dict[str, str] | None = None,
    fleet_colors: dict[str, str] | None = None,
    metadata: dict[str, Any] | None = None,
    vector_display_mode: str = "effective",
) -> ReplayBundle:
    if not position_frames:
        raise ValueError("position_frames is empty; viewer bootstrap requires captured frame data.")

    frames: list[ViewerFrame] = []
    seen_fleet_ids: list[str] = []
    previous_positions_by_fleet: dict[str, dict[str, tuple[float, float]]] = {}
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
                units=_resolve_frame_display_units(
                    tuple(units),
                    targets={str(key): str(value) for key, value in dict(raw_targets).items()},
                    vector_display_mode=str(vector_display_mode),
                    previous_positions_by_fleet=previous_positions_by_fleet,
                ),
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
    max_steps: int | None = None,
    frame_stride: int = DEFAULT_FRAME_STRIDE,
) -> ReplayBundle:
    if frame_stride < 1:
        raise ValueError(f"frame_stride must be >= 1, got {frame_stride}.")
    if max_steps is not None and not isinstance(max_steps, int):
        raise TypeError(f"max_steps must be an int or None, got {type(max_steps).__name__}.")

    settings = settings_api.load_layered_test_run_settings(TEST_RUN_BASE_DIR)
    active_settings = _deep_clone_settings(settings)
    vector_display_mode = _resolve_vector_display_mode(active_settings)
    capture_target_lines = bool(settings_api.get_visualization_setting(active_settings, "show_attack_target_lines", False))
    if vector_display_mode in {"attack", "composite"}:
        capture_target_lines = True
    run_control = active_settings.setdefault("run_control", {})
    if not isinstance(run_control, dict):
        raise ValueError("run_control must be a mapping in layered test_run settings.")
    effective_max_steps = int(run_control.get("max_time_steps", -1))
    max_steps_source = "settings"
    if max_steps is not None:
        run_control["max_time_steps"] = int(max_steps)
        effective_max_steps = int(max_steps)
        max_steps_source = "override"

    prepared = scenario.prepare_active_scenario(TEST_RUN_BASE_DIR, settings_override=active_settings)
    result = test_run_entry.run_active_surface(
        base_dir=TEST_RUN_BASE_DIR,
        prepared_override=prepared,
        settings_override=active_settings,
        execution_overrides={
            "capture_positions": True,
            "capture_hit_points": True,
            "frame_stride": int(frame_stride),
            "include_target_lines": capture_target_lines,
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
            "max_steps_effective": int(effective_max_steps),
            "max_steps_source": max_steps_source,
            "frame_stride": int(frame_stride),
            "vector_display_mode": vector_display_mode,
        },
        vector_display_mode=vector_display_mode,
    )
