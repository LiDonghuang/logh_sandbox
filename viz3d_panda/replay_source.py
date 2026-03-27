from __future__ import annotations

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
VIEWER_SOURCE_AUTO = "auto"
VIEWER_SOURCE_ACTIVE_BATTLE = "active_battle"
VIEWER_SOURCE_NEUTRAL_TRANSIT_FIXTURE = "neutral_transit_fixture"
VIEWER_SOURCE_CHOICES = (
    VIEWER_SOURCE_AUTO,
    VIEWER_SOURCE_ACTIVE_BATTLE,
    VIEWER_SOURCE_NEUTRAL_TRANSIT_FIXTURE,
)
FIXED_VIEWER_FLEET_COLORS = {
    "A": "#2a63b8",
    "B": "#b6404a",
}
FRAME_CONTROL_KEYS = {"tick", "targets", "runtime_debug"}
VALID_VECTOR_DISPLAY_MODES = {"effective", "free", "attack", "composite", "radial_debug"}
VIEWER_DIRECTION_MODE_SETTINGS = "settings"
INTERNAL_DIRECTION_DISPLAY_MODES = VALID_VECTOR_DISPLAY_MODES | {"realistic"}
VIEWER_DIRECTION_MODE_CHOICES = (
    VIEWER_DIRECTION_MODE_SETTINGS,
    "effective",
    "free",
    "fire",
    "attack",
    "composite",
    "radial_debug",
    "realistic",
)
REALISTIC_MIN_DISPLACEMENT_FRACTION = 0.0005
REALISTIC_MIN_DISPLACEMENT_FLOOR = 0.10


@dataclass(frozen=True)
class ViewerUnitState:
    unit_id: str
    fleet_id: str
    x: float
    y: float
    z: float
    heading_x: float
    heading_y: float
    orientation_x: float
    orientation_y: float
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


def _parse_unit_point(raw_point: Any, *, fleet_id: str) -> ViewerUnitState:
    if not isinstance(raw_point, (list, tuple)) or len(raw_point) < 9:
        raise ValueError(
            "position_frames entries must be tuples of exactly "
            "(unit_id, x, y, heading_x, heading_y, velocity_x, velocity_y, hit_points, max_hit_points) "
            f"or longer; got {raw_point!r} for fleet {fleet_id!r}"
        )
    unit_id = str(raw_point[0])
    velocity_x = float(raw_point[5])
    velocity_y = float(raw_point[6])
    hit_points = float(raw_point[7])
    max_hit_points = float(raw_point[8])
    return ViewerUnitState(
        unit_id=unit_id,
        fleet_id=str(fleet_id),
        x=float(raw_point[1]),
        y=float(raw_point[2]),
        z=0.0,
        heading_x=float(raw_point[3]),
        heading_y=float(raw_point[4]),
        orientation_x=float(raw_point[3]),
        orientation_y=float(raw_point[4]),
        velocity_x=velocity_x,
        velocity_y=velocity_y,
        hit_points=hit_points,
        max_hit_points=max_hit_points,
    )


def _normalize_vector(dx: float, dy: float) -> tuple[float, float]:
    norm = math.sqrt((float(dx) * float(dx)) + (float(dy) * float(dy)))
    if norm <= 1e-12:
        return (0.0, 0.0)
    return (float(dx) / norm, float(dy) / norm)


def _resolve_vector_display_mode(settings: dict[str, Any]) -> str:
    raw_value = settings_api.get_visualization_setting(
        settings,
        "vector_display_mode",
        "effective",
    )
    mode = str(raw_value).strip().lower()
    if mode not in VALID_VECTOR_DISPLAY_MODES:
        allowed = ", ".join(sorted(VALID_VECTOR_DISPLAY_MODES))
        raise ValueError(
            f"visualization.vector_display_mode must be one of {{{allowed}}}, got {raw_value!r}."
        )
    return mode


def _normalize_viewer_direction_mode(requested_mode: str) -> str:
    normalized = str(requested_mode).strip().lower()
    if normalized == "fire":
        return "attack"
    if normalized == VIEWER_DIRECTION_MODE_SETTINGS:
        return VIEWER_DIRECTION_MODE_SETTINGS
    if normalized not in INTERNAL_DIRECTION_DISPLAY_MODES:
        allowed = ", ".join(VIEWER_DIRECTION_MODE_CHOICES)
        raise ValueError(f"direction_mode must be one of {{{allowed}}}, got {requested_mode!r}.")
    return normalized


def _public_direction_mode_label(mode: str) -> str:
    normalized = str(mode).strip().lower()
    if normalized == "attack":
        return "fire"
    return normalized


def _resolve_direction_mode(settings: dict[str, Any], requested_mode: str) -> tuple[str, str, str]:
    settings_mode = _resolve_vector_display_mode(settings)
    normalized_requested = _normalize_viewer_direction_mode(requested_mode)
    if normalized_requested == VIEWER_DIRECTION_MODE_SETTINGS:
        return (settings_mode, _public_direction_mode_label(settings_mode), "settings")
    return (normalized_requested, _public_direction_mode_label(normalized_requested), "override")


def _resolve_viewer_source(settings: dict[str, Any], requested_source: str) -> str:
    normalized = str(requested_source).strip().lower()
    if normalized not in VIEWER_SOURCE_CHOICES:
        allowed = ", ".join(VIEWER_SOURCE_CHOICES)
        raise ValueError(f"viewer source must be one of {{{allowed}}}, got {requested_source!r}.")
    if normalized != VIEWER_SOURCE_AUTO:
        return normalized
    fixture_mode = str(settings_api.get_fixture_setting(settings, ("active_mode",), "battle")).strip().lower()
    if fixture_mode == "neutral_transit_v1":
        return VIEWER_SOURCE_NEUTRAL_TRANSIT_FIXTURE
    return VIEWER_SOURCE_ACTIVE_BATTLE


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


def _unit_key(unit: ViewerUnitState) -> str:
    return f"{unit.fleet_id}:{unit.unit_id}"


def _build_frame_position_lookup(frame: ViewerFrame) -> dict[str, tuple[float, float]]:
    return {
        _unit_key(unit): (float(unit.x), float(unit.y))
        for unit in frame.units
    }


def _resolve_realistic_direction(
    unit: ViewerUnitState,
    *,
    previous_position: tuple[float, float] | None,
    next_position: tuple[float, float] | None,
    last_valid_directions: dict[str, tuple[float, float]],
    fallback_direction: tuple[float, float],
    min_displacement: float,
) -> tuple[float, float]:
    unit_key = _unit_key(unit)
    current_position = (float(unit.x), float(unit.y))
    candidate_displacements: list[tuple[float, float]] = []
    if previous_position is not None and next_position is not None:
        candidate_displacements.append(
            (
                float(next_position[0]) - float(previous_position[0]),
                float(next_position[1]) - float(previous_position[1]),
            )
        )
    if next_position is not None:
        candidate_displacements.append(
            (
                float(next_position[0]) - float(current_position[0]),
                float(next_position[1]) - float(current_position[1]),
            )
        )
    if previous_position is not None:
        candidate_displacements.append(
            (
                float(current_position[0]) - float(previous_position[0]),
                float(current_position[1]) - float(previous_position[1]),
            )
        )

    for dx_value, dy_value in candidate_displacements:
        displacement_norm = math.sqrt((float(dx_value) * float(dx_value)) + (float(dy_value) * float(dy_value)))
        if displacement_norm < float(min_displacement):
            continue
        realistic_direction = _normalize_vector(dx_value, dy_value)
        if realistic_direction != (0.0, 0.0):
            last_valid_directions[unit_key] = realistic_direction
            return realistic_direction

    last_valid = last_valid_directions.get(unit_key)
    if last_valid is not None:
        return last_valid
    if fallback_direction != (0.0, 0.0):
        return fallback_direction
    return _normalize_vector(unit.orientation_x, unit.orientation_y)


def _resolve_frame_display_units(
    frame: ViewerFrame,
    *,
    vector_display_mode: str,
    previous_positions: dict[str, tuple[float, float]],
    next_positions: dict[str, tuple[float, float]],
    last_realistic_directions: dict[str, tuple[float, float]],
    realistic_min_displacement: float,
) -> tuple[ViewerUnitState, ...]:
    units = frame.units
    targets = frame.targets
    attack_direction_map = _build_attack_direction_map(units, targets)
    centroids = _fleet_centroids(units)
    resolved_units: list[ViewerUnitState] = []

    for unit in units:
        unit_key = _unit_key(unit)
        previous = previous_positions.get(unit_key)
        next_position = next_positions.get(unit_key)
        if previous is None:
            effective_x = float(unit.orientation_x)
            effective_y = float(unit.orientation_y)
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
        elif vector_display_mode == "realistic":
            display_direction = _resolve_realistic_direction(
                unit,
                previous_position=previous,
                next_position=next_position,
                last_valid_directions=last_realistic_directions,
                fallback_direction=effective_direction,
                min_displacement=realistic_min_displacement,
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
    return tuple(resolved_units)


def _resolve_display_frames(
    frames: list[ViewerFrame],
    *,
    vector_display_mode: str,
    arena_size: float,
) -> tuple[ViewerFrame, ...]:
    if vector_display_mode not in INTERNAL_DIRECTION_DISPLAY_MODES:
        raise ValueError(f"unsupported internal direction mode {vector_display_mode!r}.")
    position_lookups = [_build_frame_position_lookup(frame) for frame in frames]
    last_realistic_directions: dict[str, tuple[float, float]] = {}
    realistic_min_displacement = max(
        REALISTIC_MIN_DISPLACEMENT_FLOOR,
        float(arena_size) * REALISTIC_MIN_DISPLACEMENT_FRACTION,
    )
    resolved_frames: list[ViewerFrame] = []
    for frame_index, frame in enumerate(frames):
        previous_positions = position_lookups[frame_index - 1] if frame_index > 0 else {}
        next_positions = position_lookups[frame_index + 1] if (frame_index + 1) < len(position_lookups) else {}
        resolved_frames.append(
            replace(
                frame,
                units=_resolve_frame_display_units(
                    frame,
                    vector_display_mode=vector_display_mode,
                    previous_positions=previous_positions,
                    next_positions=next_positions,
                    last_realistic_directions=last_realistic_directions,
                    realistic_min_displacement=realistic_min_displacement,
                ),
            )
        )
    return tuple(resolved_frames)


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

    raw_frames: list[ViewerFrame] = []
    seen_fleet_ids: list[str] = []
    for raw_frame in position_frames:
        if not isinstance(raw_frame, dict):
            raise ValueError(f"Each position frame must be a mapping, got {type(raw_frame).__name__}.")
        tick = int(raw_frame.get("tick", len(raw_frames)))
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
        raw_frames.append(
            ViewerFrame(
                tick=tick,
                units=tuple(units),
                targets={str(key): str(value) for key, value in dict(raw_targets).items()},
            )
        )

    frames = _resolve_display_frames(
        raw_frames,
        vector_display_mode=str(vector_display_mode),
        arena_size=float(arena_size),
    )

    resolved_labels = dict(fleet_labels or {})
    for fleet_id in seen_fleet_ids:
        label = str(resolved_labels.get(fleet_id, "")).strip()
        if not label:
            raise ValueError(f"viewer replay requires an explicit fleet label for {fleet_id!r}.")
        resolved_labels[fleet_id] = label

    resolved_colors = {str(key): str(value) for key, value in dict(fleet_colors or {}).items()}
    for fleet_id in seen_fleet_ids:
        color = str(resolved_colors.get(fleet_id, "")).strip()
        if not color:
            raise ValueError(f"viewer replay requires an explicit fleet color for {fleet_id!r}.")
        resolved_colors[fleet_id] = color

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


def load_viewer_replay(
    *,
    source: str = VIEWER_SOURCE_AUTO,
    max_steps: int | None = None,
    frame_stride: int = DEFAULT_FRAME_STRIDE,
    direction_mode: str = VIEWER_DIRECTION_MODE_SETTINGS,
) -> ReplayBundle:
    if frame_stride < 1:
        raise ValueError(f"frame_stride must be >= 1, got {frame_stride}.")
    if max_steps is not None and not isinstance(max_steps, int):
        raise TypeError(f"max_steps must be an int or None, got {type(max_steps).__name__}.")

    settings = settings_api.load_layered_test_run_settings(TEST_RUN_BASE_DIR)
    settings_vector_display_mode = _resolve_vector_display_mode(settings)
    active_direction_mode, active_direction_label, direction_mode_source = _resolve_direction_mode(
        settings,
        direction_mode,
    )
    resolved_source = _resolve_viewer_source(settings, source)
    run_control = settings.setdefault("run_control", {})
    if not isinstance(run_control, dict):
        raise ValueError("run_control must be a mapping in layered test_run settings.")
    effective_max_steps = int(run_control.get("max_time_steps", -1))
    max_steps_source = "settings"
    if max_steps is not None:
        run_control["max_time_steps"] = int(max_steps)
        effective_max_steps = int(max_steps)
        max_steps_source = "override"

    if resolved_source == VIEWER_SOURCE_NEUTRAL_TRANSIT_FIXTURE:
        prepared = scenario.prepare_neutral_transit_fixture(TEST_RUN_BASE_DIR, settings_override=settings)
        result = test_run_entry.run_active_surface(
            base_dir=TEST_RUN_BASE_DIR,
            prepared_override=prepared,
            settings_override=settings,
            execution_overrides={
                "capture_positions": True,
                "capture_hit_points": True,
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
        fleet_data = prepared["fleet_data"]
        metadata = {
            "summary": dict(result["prepared"]["summary"]),
            "fixture_readout": dict(result["observer_telemetry"].get("fixture", {})),
            "max_steps_effective": int(effective_max_steps),
            "max_steps_source": max_steps_source,
            "frame_stride": int(frame_stride),
            "vector_display_mode": active_direction_label,
            "settings_vector_display_mode": _public_direction_mode_label(settings_vector_display_mode),
            "direction_mode_source": direction_mode_source,
        }
        return build_replay_bundle(
            source_kind="test_run_neutral_transit_fixture",
            arena_size=float(prepared["initial_state"].arena_size),
            position_frames=result["position_frames"],
            fleet_labels={
                "A": scenario.resolve_display_name(fleet_data, "EN") or "A",
            },
            fleet_colors={
                "A": FIXED_VIEWER_FLEET_COLORS["A"],
            },
            metadata=metadata,
            vector_display_mode=active_direction_mode,
        )

    capture_target_lines = bool(settings_api.get_visualization_setting(settings, "show_attack_target_lines", False))
    if settings_vector_display_mode in {"attack", "composite"} or active_direction_mode in {"attack", "composite"}:
        capture_target_lines = True
    prepared = scenario.prepare_active_scenario(TEST_RUN_BASE_DIR, settings_override=settings)
    result = test_run_entry.run_active_surface(
        base_dir=TEST_RUN_BASE_DIR,
        prepared_override=prepared,
        settings_override=settings,
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
    metadata = {
        "summary": dict(result["prepared"]["summary"]),
        "max_steps_effective": int(effective_max_steps),
        "max_steps_source": max_steps_source,
        "frame_stride": int(frame_stride),
        "vector_display_mode": active_direction_label,
        "settings_vector_display_mode": _public_direction_mode_label(settings_vector_display_mode),
        "direction_mode_source": direction_mode_source,
    }
    return build_replay_bundle(
        source_kind="test_run_active_surface",
        arena_size=float(prepared["initial_state"].arena_size),
        position_frames=result["position_frames"],
        fleet_labels={
            "A": scenario.resolve_display_name(fleet_a_data, "EN"),
            "B": scenario.resolve_display_name(fleet_b_data, "EN"),
        },
        fleet_colors={
            "A": FIXED_VIEWER_FLEET_COLORS["A"],
            "B": FIXED_VIEWER_FLEET_COLORS["B"],
        },
        metadata=metadata,
        vector_display_mode=active_direction_mode,
    )
