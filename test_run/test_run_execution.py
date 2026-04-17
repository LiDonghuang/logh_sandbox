import math
import time
from collections.abc import Mapping, Sequence
from dataclasses import replace
from typing import Any

from runtime.engine_skeleton import EngineTickSkeleton
from runtime.runtime_v0_1 import BattleState, UnitState, Vec2

from test_run.test_run_telemetry import (
    compute_hostile_intermix_metrics,
    extract_runtime_debug_payload,
)


DEFAULT_FRAME_STRIDE = 1
HOSTILE_CONTACT_IMPEDANCE_MODE_OFF = "off"
HOSTILE_CONTACT_IMPEDANCE_MODE_HYBRID_V2 = "hybrid_v2"
HOSTILE_CONTACT_IMPEDANCE_MODE_LABELS = {
    HOSTILE_CONTACT_IMPEDANCE_MODE_OFF,
    HOSTILE_CONTACT_IMPEDANCE_MODE_HYBRID_V2,
}
HOSTILE_CONTACT_IMPEDANCE_MODE_DEFAULT = "off"
HOSTILE_CONTACT_IMPEDANCE_V2_RADIUS_MULTIPLIER_DEFAULT = 1.50
HOSTILE_CONTACT_IMPEDANCE_V2_REPULSION_MAX_DISP_RATIO_DEFAULT = 0.20
HOSTILE_CONTACT_IMPEDANCE_V2_FORWARD_DAMPING_STRENGTH_DEFAULT = 0.50
SimulationExecutionConfig = dict
SimulationMovementConfig = dict
SimulationContactConfig = dict
SimulationBoundaryConfig = dict
SimulationRuntimeConfig = dict
SimulationObserverConfig = dict
FIXTURE_MODE_BATTLE = "battle"
FIXTURE_MODE_NEUTRAL = "neutral"
FIXTURE_MODE_LABELS = {
    FIXTURE_MODE_BATTLE,
    FIXTURE_MODE_NEUTRAL,
}
OBJECTIVE_CONTRACT_3D_SOURCE_OWNER_FIXTURE = "fixture"
OBJECTIVE_CONTRACT_3D_MODE_POINT_ANCHOR = "point_anchor"
OBJECTIVE_CONTRACT_3D_NO_ENEMY_SEMANTICS = "enemy_term_zero"
V4A_REFERENCE_SURFACE_MODE_RIGID_SLOTS = "rigid_slots"
V4A_REFERENCE_SURFACE_MODE_SOFT_MORPHOLOGY_V1 = "soft_morphology_v1"
V4A_REFERENCE_SURFACE_MODE_LABELS = {
    V4A_REFERENCE_SURFACE_MODE_RIGID_SLOTS,
    V4A_REFERENCE_SURFACE_MODE_SOFT_MORPHOLOGY_V1,
}
V4A_REFERENCE_LAYOUT_MODE_RECT_CENTERED_1_0 = "rect_centered_1.0"
V4A_REFERENCE_LAYOUT_MODE_RECT_CENTERED_4_0 = "rect_centered_4.0"
V4A_SOFT_MORPHOLOGY_RELAXATION_DEFAULT = 0.20
V4A_MORPHOLOGY_AXIS_RELAXATION_DEFAULT = 0.12
V4A_CENTER_WING_DIFFERENTIAL_DEFAULT = 0.0
V4A_HOLD_AWAIT_SPEED_SCALE_DEFAULT = 0.35
V4A_SHAPE_VS_ADVANCE_STRENGTH_DEFAULT = 0.65
V4A_HEADING_RELAXATION_DEFAULT = 0.18
V4A_BATTLE_STANDOFF_HOLD_BAND_RATIO_DEFAULT = 0.10
V4A_BATTLE_TARGET_FRONT_STRIP_GAP_BIAS_DEFAULT = 0.0
V4A_BATTLE_HOLD_WEIGHT_STRENGTH_DEFAULT = 0.5
V4A_ENGAGEMENT_GEOMETRY_FULL_ENGAGED_FRACTION_DEFAULT = 0.08
V4A_FRONT_REORIENTATION_MAX_WEIGHT_DEFAULT = 0.35
V4A_ENGAGEMENT_GEOMETRY_RELAXATION_DEFAULT = 0.18
V4A_EFFECTIVE_FIRE_AXIS_RELAXATION_DEFAULT = 0.16
V4A_FIRE_AXIS_COHERENCE_RELAXATION_DEFAULT = 0.18
V4A_FRONT_REORIENTATION_RELAXATION_DEFAULT = 0.18
V4A_BATTLE_RELATION_LEAD_TICKS_DEFAULT = 18.0
V4A_BATTLE_HOLD_RELAXATION_DEFAULT = 0.20
V4A_BATTLE_APPROACH_DRIVE_RELAXATION_DEFAULT = 0.22
V4A_NEAR_CONTACT_INTERNAL_STABILITY_BLEND_DEFAULT = 0.55
V4A_NEAR_CONTACT_SPEED_RELAXATION_DEFAULT = 0.28
V4A_ENGAGED_SPEED_SCALE_DEFAULT = 0.70
V4A_ATTACK_SPEED_LATERAL_SCALE_DEFAULT = 0.65
V4A_ATTACK_SPEED_BACKWARD_SCALE_DEFAULT = 0.35
V4A_HOLD_AWAIT_SHAPE_ERROR_THRESHOLD = 0.12
V4A_SHAPE_VS_ADVANCE_MIN_SHARE = 0.20
V4A_TRANSITION_IDLE_SPEED_FLOOR = 0.45
V4A_TURN_SPEED_FLOOR = 0.35
V4A_FORWARD_TRANSPORT_BRAKE_STRENGTH_DEFAULT = 0.75
V4A_FORWARD_TRANSPORT_BOOST_STRENGTH_DEFAULT = 0.55
V4A_FORWARD_TRANSPORT_BRAKE_FLOOR = 0.15
V4A_FORWARD_TRANSPORT_MAX_SPEED_SCALE = 1.20


def _clamp01(value: float) -> float:
    return min(1.0, max(0.0, value))


def _direction_delta_degrees(
    lhs_hat_xy: Sequence[float] | tuple[float, float],
    rhs_hat_xy: Sequence[float] | tuple[float, float],
) -> float:
    if len(lhs_hat_xy) < 2 or len(rhs_hat_xy) < 2:
        return float("nan")
    lhs_dx = float(lhs_hat_xy[0])
    lhs_dy = float(lhs_hat_xy[1])
    rhs_dx = float(rhs_hat_xy[0])
    rhs_dy = float(rhs_hat_xy[1])
    lhs_norm = math.sqrt((lhs_dx * lhs_dx) + (lhs_dy * lhs_dy))
    rhs_norm = math.sqrt((rhs_dx * rhs_dx) + (rhs_dy * rhs_dy))
    if lhs_norm <= 1e-12 or rhs_norm <= 1e-12:
        return float("nan")
    dot_value = max(
        -1.0,
        min(
            1.0,
            ((lhs_dx * rhs_dx) + (lhs_dy * rhs_dy)) / max(lhs_norm * rhs_norm, 1e-12),
        ),
    )
    return math.degrees(math.acos(dot_value))




def _require_mapping(cfg: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    section = cfg.get(key)
    if not isinstance(section, Mapping):
        raise TypeError(f"run_simulation requires '{key}' to be a mapping, got {type(section).__name__}")
    return section


def _require_engine_surface_dict(engine: Any, attr_name: str) -> dict[str, Any]:
    surface = getattr(engine, attr_name, None)
    if not isinstance(surface, dict):
        raise TypeError(f"EngineTickSkeleton.{attr_name} missing or invalid")
    return surface


def _resolve_fixture_execution_context(
    initial_state: BattleState,
    fixture_cfg: Mapping[str, Any] | None,
) -> dict[str, Any]:
    if fixture_cfg is None:
        fixture_cfg = {}
    if not isinstance(fixture_cfg, Mapping):
        raise TypeError(
            "run_simulation requires execution_cfg['fixture'] to be a mapping, "
            f"got {type(fixture_cfg).__name__}"
        )

    fixture_active_mode = str(fixture_cfg.get("active_mode", FIXTURE_MODE_BATTLE)).strip().lower() or FIXTURE_MODE_BATTLE
    if fixture_active_mode not in FIXTURE_MODE_LABELS:
        raise ValueError(
            f"run_simulation execution_cfg['fixture']['active_mode'] must be one of {sorted(FIXTURE_MODE_LABELS)}, "
            f"got {fixture_active_mode!r}"
        )

    fixture_active = fixture_active_mode == FIXTURE_MODE_NEUTRAL
    fixture_fleet_id = ""
    fixture_objective_point_xy = (0.0, 0.0)
    fixture_objective_contract_3d: dict[str, Any] = {}
    fixture_stop_radius = 0.0
    if fixture_active:
        if len(initial_state.fleets) != 1:
            raise ValueError(
                "neutral requires a single-fleet initial_state, "
                f"got fleet_ids={list(initial_state.fleets.keys())}"
            )
        fixture_fleet_id = str(fixture_cfg.get("fleet_id", next(iter(initial_state.fleets.keys())))).strip()
        if fixture_fleet_id not in initial_state.fleets:
            raise ValueError(
                "neutral fixture fleet_id must exist in initial_state.fleets, "
                f"got {fixture_fleet_id!r}"
            )
        fixture_objective_contract_3d, fixture_objective_point_xy = _normalize_fixture_objective_contract_3d(
            fixture_cfg.get("objective_contract_3d")
        )
        fixture_stop_radius = float(fixture_cfg.get("stop_radius", 0.0))
        if fixture_stop_radius < 0.0:
            raise ValueError(
                "neutral execution_cfg['fixture']['stop_radius'] must be >= 0, "
                f"got {fixture_stop_radius}"
            )

    return {
        "active_mode": fixture_active_mode,
        "active": fixture_active,
        "fleet_id": fixture_fleet_id,
        "objective_point_xy": fixture_objective_point_xy,
        "objective_contract_3d": fixture_objective_contract_3d,
        "stop_radius": fixture_stop_radius,
    }


def _relax_scalar(current_value: float, target_value: float, weight: float) -> float:
    current_f = float(current_value)
    target_f = float(target_value)
    if not math.isfinite(current_f):
        return target_f
    if not math.isfinite(target_f):
        return current_f
    blend = _clamp01(float(weight))
    return current_f + ((target_f - current_f) * blend)


def _resolve_reference_layout_target_aspect(layout_mode: str) -> float:
    normalized = str(layout_mode).strip().lower()
    if normalized == V4A_REFERENCE_LAYOUT_MODE_RECT_CENTERED_1_0:
        return 1.0
    if normalized == V4A_REFERENCE_LAYOUT_MODE_RECT_CENTERED_4_0:
        return 4.0
    raise ValueError(
        "v4a reference_layout_mode must be one of "
        f"{{{V4A_REFERENCE_LAYOUT_MODE_RECT_CENTERED_1_0}, {V4A_REFERENCE_LAYOUT_MODE_RECT_CENTERED_4_0}}}, "
        f"got {layout_mode!r}"
    )


def _build_centered_rect_row_counts(unit_count: int, aspect_ratio: float) -> list[int]:
    grid_columns = max(1, int((int(unit_count) * float(aspect_ratio)) ** 0.5))
    grid_rows = (int(unit_count) + grid_columns - 1) // grid_columns
    while grid_columns / max(1, grid_rows) < float(aspect_ratio) and grid_columns < int(unit_count):
        grid_columns += 1
        grid_rows = (int(unit_count) + grid_columns - 1) // grid_columns
    row_counts: list[int] = []
    remaining = int(unit_count)
    for _ in range(grid_rows):
        row_count = min(grid_columns, remaining)
        row_counts.append(int(row_count))
        remaining -= row_count
    return row_counts


def _build_reference_slot_offsets_local(
    ordered_unit_ids: Sequence[str],
    *,
    expected_reference_spacing: float,
    reference_layout_mode: str,
) -> dict[str, tuple[float, float]]:
    target_aspect_ratio = _resolve_reference_layout_target_aspect(reference_layout_mode)
    row_counts = _build_centered_rect_row_counts(len(ordered_unit_ids), target_aspect_ratio)
    offsets_local: dict[str, tuple[float, float]] = {}
    half_depth = (len(row_counts) - 1) / 2.0
    unit_index = 0
    for row, row_count in enumerate(row_counts):
        row_offset = row - half_depth
        half_width = (row_count - 1) / 2.0
        for col in range(row_count):
            if unit_index >= len(ordered_unit_ids):
                break
            lateral = col - half_width
            unit_id = str(ordered_unit_ids[unit_index])
            offsets_local[unit_id] = (
                float(row_offset * expected_reference_spacing),
                float(lateral * expected_reference_spacing),
            )
            unit_index += 1
    return offsets_local


def _compute_morphology_material_phase(
    offsets_by_id: Mapping[str, tuple[float, float]],
) -> tuple[dict[str, float], dict[str, float], float, float]:
    if not offsets_by_id:
        return {}, {}, 1.0, 1.0
    forward_extent = max(1e-9, max(abs(float(offset[0])) for offset in offsets_by_id.values()))
    lateral_extent = max(1e-9, max(abs(float(offset[1])) for offset in offsets_by_id.values()))
    forward_phase_by_id: dict[str, float] = {}
    lateral_phase_by_id: dict[str, float] = {}
    for unit_id, (forward_offset, lateral_offset) in offsets_by_id.items():
        forward_phase_by_id[str(unit_id)] = max(
            -1.0,
            min(1.0, float(forward_offset) / forward_extent),
        )
        lateral_phase_by_id[str(unit_id)] = max(
            -1.0,
            min(1.0, float(lateral_offset) / lateral_extent),
        )
    return forward_phase_by_id, lateral_phase_by_id, float(forward_extent), float(lateral_extent)


def _compute_projected_half_extents(
    units: Sequence[UnitState],
    primary_hat_xy: tuple[float, float],
) -> tuple[float, float]:
    if not units:
        return (0.0, 0.0)
    primary_dx = float(primary_hat_xy[0])
    primary_dy = float(primary_hat_xy[1])
    primary_norm = math.sqrt((primary_dx * primary_dx) + (primary_dy * primary_dy))
    if primary_norm <= 1e-12:
        primary_hat_xy = (1.0, 0.0)
    else:
        primary_hat_xy = (primary_dx / primary_norm, primary_dy / primary_norm)
    secondary_hat_xy = (-float(primary_hat_xy[1]), float(primary_hat_xy[0]))
    centroid_x = sum(float(unit.position.x) for unit in units) / float(len(units))
    centroid_y = sum(float(unit.position.y) for unit in units) / float(len(units))
    forward_values: list[float] = []
    lateral_values: list[float] = []
    for unit in units:
        rel_x = float(unit.position.x) - centroid_x
        rel_y = float(unit.position.y) - centroid_y
        forward_values.append((rel_x * float(primary_hat_xy[0])) + (rel_y * float(primary_hat_xy[1])))
        lateral_values.append((rel_x * float(secondary_hat_xy[0])) + (rel_y * float(secondary_hat_xy[1])))
    forward_extent = 0.5 * (max(forward_values) - min(forward_values)) if forward_values else 0.0
    lateral_extent = 0.5 * (max(lateral_values) - min(lateral_values)) if lateral_values else 0.0
    return (float(max(0.0, forward_extent)), float(max(0.0, lateral_extent)))


def _compute_front_strip_depth(
    units: Sequence[UnitState],
    primary_hat_xy: tuple[float, float],
    *,
    toward_positive: bool,
    strip_fraction: float = 0.20,
    min_count: int = 4,
    max_count: int = 16,
) -> float:
    if not units:
        return 0.0
    primary_dx = float(primary_hat_xy[0])
    primary_dy = float(primary_hat_xy[1])
    primary_norm = math.sqrt((primary_dx * primary_dx) + (primary_dy * primary_dy))
    if primary_norm <= 1e-12:
        axis_hat_xy = (1.0, 0.0)
    else:
        axis_hat_xy = (primary_dx / primary_norm, primary_dy / primary_norm)
    centroid_x = sum(float(unit.position.x) for unit in units) / float(len(units))
    centroid_y = sum(float(unit.position.y) for unit in units) / float(len(units))
    signed_values: list[float] = []
    sign = 1.0 if bool(toward_positive) else -1.0
    for unit in units:
        rel_x = float(unit.position.x) - centroid_x
        rel_y = float(unit.position.y) - centroid_y
        projected = (rel_x * float(axis_hat_xy[0])) + (rel_y * float(axis_hat_xy[1]))
        signed_values.append(sign * float(projected))
    if not signed_values:
        return 0.0
    sorted_values = sorted(signed_values, reverse=True)
    strip_count = max(int(min_count), int(round(len(sorted_values) * float(strip_fraction))))
    strip_count = min(int(max_count), min(int(len(sorted_values)), strip_count))
    strip_slice = sorted_values[: max(1, strip_count)]
    strip_mean = sum(float(value) for value in strip_slice) / float(len(strip_slice))
    return float(max(0.0, strip_mean))


def _compute_attack_direction_speed_scale(
    cos_theta: float,
    *,
    lateral_scale: float,
    backward_scale: float,
) -> float:
    cos_clamped = max(-1.0, min(1.0, float(cos_theta)))
    lateral = max(0.0, min(1.0, float(lateral_scale)))
    backward = max(0.0, min(lateral, float(backward_scale)))
    if cos_clamped >= 0.0:
        return float(lateral + ((1.0 - lateral) * cos_clamped))
    return float(lateral + ((lateral - backward) * cos_clamped))


def _compute_fire_efficiency_series(
    size_a: Sequence[float],
    size_b: Sequence[float],
    alive_a: Sequence[int | float],
    alive_b: Sequence[int | float],
    *,
    per_unit_damage: float,
) -> tuple[list[float], list[float]]:
    n = max(len(size_a), len(size_b), len(alive_a), len(alive_b))
    if n <= 0:
        return ([], [])
    out_a: list[float] = []
    out_b: list[float] = []
    damage_floor = max(0.0, float(per_unit_damage))
    last_size_a = float(size_a[-1]) if size_a else 0.0
    last_size_b = float(size_b[-1]) if size_b else 0.0
    last_alive_a = float(alive_a[-1]) if alive_a else 0.0
    last_alive_b = float(alive_b[-1]) if alive_b else 0.0
    for idx in range(n):
        curr_size_a = float(size_a[idx]) if idx < len(size_a) else last_size_a
        curr_size_b = float(size_b[idx]) if idx < len(size_b) else last_size_b
        curr_alive_a = float(alive_a[idx]) if idx < len(alive_a) else last_alive_a
        curr_alive_b = float(alive_b[idx]) if idx < len(alive_b) else last_alive_b
        if idx <= 0:
            prev_size_a = curr_size_a
            prev_size_b = curr_size_b
            prev_alive_a = curr_alive_a
            prev_alive_b = curr_alive_b
        else:
            prev_size_a = float(size_a[idx - 1]) if (idx - 1) < len(size_a) else curr_size_a
            prev_size_b = float(size_b[idx - 1]) if (idx - 1) < len(size_b) else curr_size_b
            prev_alive_a = float(alive_a[idx - 1]) if (idx - 1) < len(alive_a) else curr_alive_a
            prev_alive_b = float(alive_b[idx - 1]) if (idx - 1) < len(alive_b) else curr_alive_b
        actual_damage_by_a = max(0.0, prev_size_b - curr_size_b)
        actual_damage_by_b = max(0.0, prev_size_a - curr_size_a)
        max_damage_a = max(0.0, prev_alive_a) * damage_floor
        max_damage_b = max(0.0, prev_alive_b) * damage_floor
        eff_a = actual_damage_by_a / max_damage_a if max_damage_a > 0.0 else 0.0
        eff_b = actual_damage_by_b / max_damage_b if max_damage_b > 0.0 else 0.0
        out_a.append(_clamp01(float(eff_a)))
        out_b.append(_clamp01(float(eff_b)))
    return (out_a, out_b)


def _normalize_fixture_objective_contract_3d(contract_cfg: Any) -> tuple[dict[str, Any], tuple[float, float]]:
    if not isinstance(contract_cfg, Mapping):
        raise TypeError(
            "neutral execution_cfg['fixture']['objective_contract_3d'] must be a mapping"
        )
    if "transit_axis_hint_xyz" in contract_cfg:
        raise ValueError(
            "neutral first implementation must not set "
            "execution_cfg['fixture']['objective_contract_3d']['transit_axis_hint_xyz']"
        )
    anchor_point_xyz = contract_cfg.get("anchor_point_xyz")
    if (
        not isinstance(anchor_point_xyz, Sequence)
        or isinstance(anchor_point_xyz, (str, bytes))
        or len(anchor_point_xyz) != 3
    ):
        raise TypeError(
            "neutral execution_cfg['fixture']['objective_contract_3d']['anchor_point_xyz'] "
            "must be a 3-item sequence"
        )
    normalized_contract = {
        "anchor_point_xyz": (
            float(anchor_point_xyz[0]),
            float(anchor_point_xyz[1]),
            float(anchor_point_xyz[2]),
        ),
        "source_owner": str(contract_cfg.get("source_owner", "")).strip(),
        "objective_mode": str(contract_cfg.get("objective_mode", "")).strip(),
        "no_enemy_semantics": str(contract_cfg.get("no_enemy_semantics", "")).strip(),
    }
    if normalized_contract["source_owner"] != OBJECTIVE_CONTRACT_3D_SOURCE_OWNER_FIXTURE:
        raise ValueError(
            "neutral execution_cfg['fixture']['objective_contract_3d']['source_owner'] "
            f"must be {OBJECTIVE_CONTRACT_3D_SOURCE_OWNER_FIXTURE!r}, got {normalized_contract['source_owner']!r}"
        )
    if normalized_contract["objective_mode"] != OBJECTIVE_CONTRACT_3D_MODE_POINT_ANCHOR:
        raise ValueError(
            "neutral execution_cfg['fixture']['objective_contract_3d']['objective_mode'] "
            f"must be {OBJECTIVE_CONTRACT_3D_MODE_POINT_ANCHOR!r}, got {normalized_contract['objective_mode']!r}"
        )
    if normalized_contract["no_enemy_semantics"] != OBJECTIVE_CONTRACT_3D_NO_ENEMY_SEMANTICS:
        raise ValueError(
            "neutral execution_cfg['fixture']['objective_contract_3d']['no_enemy_semantics'] "
            f"must be {OBJECTIVE_CONTRACT_3D_NO_ENEMY_SEMANTICS!r}, got {normalized_contract['no_enemy_semantics']!r}"
        )
    return normalized_contract, (
        float(normalized_contract["anchor_point_xyz"][0]),
        float(normalized_contract["anchor_point_xyz"][1]),
    )


class _ExecutionWiringSupport:
    """Internal-only execution support for cfg validation and engine wiring."""

    @staticmethod
    def _build_v4a_bundle_profile(movement_cfg: Mapping[str, Any]) -> dict[str, Any]:
        v4a_reference_surface_mode = str(
            movement_cfg.get("v4a_reference_surface_mode", V4A_REFERENCE_SURFACE_MODE_RIGID_SLOTS)
        ).strip().lower()
        if v4a_reference_surface_mode not in V4A_REFERENCE_SURFACE_MODE_LABELS:
            raise ValueError(
                "run_simulation movement_cfg['v4a_reference_surface_mode'] must be one of "
                f"{sorted(V4A_REFERENCE_SURFACE_MODE_LABELS)}, got {v4a_reference_surface_mode!r}"
            )

        def _require_unit_interval(name: str, default: float, *, left_open: bool) -> float:
            value = float(movement_cfg.get(name, default))
            lower_ok = value > 0.0 if left_open else value >= 0.0
            if not (lower_ok and value <= 1.0):
                left_text = "(0.0, 1.0]" if left_open else "[0.0, 1.0]"
                raise ValueError(
                    f"run_simulation movement_cfg[{name!r}] must be within {left_text}, got {value}"
                )
            return value

        v4a_soft_morphology_relaxation = _require_unit_interval(
            "v4a_soft_morphology_relaxation",
            V4A_SOFT_MORPHOLOGY_RELAXATION_DEFAULT,
            left_open=True,
        )
        v4a_shape_vs_advance_strength = _require_unit_interval(
            "v4a_shape_vs_advance_strength",
            V4A_SHAPE_VS_ADVANCE_STRENGTH_DEFAULT,
            left_open=False,
        )
        v4a_heading_relaxation = _require_unit_interval(
            "v4a_heading_relaxation",
            V4A_HEADING_RELAXATION_DEFAULT,
            left_open=True,
        )
        v4a_battle_standoff_hold_band_ratio = _require_unit_interval(
            "v4a_battle_standoff_hold_band_ratio",
            V4A_BATTLE_STANDOFF_HOLD_BAND_RATIO_DEFAULT,
            left_open=False,
        )
        v4a_battle_hold_weight_strength = _require_unit_interval(
            "v4a_battle_hold_weight_strength",
            V4A_BATTLE_HOLD_WEIGHT_STRENGTH_DEFAULT,
            left_open=False,
        )
        v4a_battle_hold_relaxation = _require_unit_interval(
            "v4a_battle_hold_relaxation",
            V4A_BATTLE_HOLD_RELAXATION_DEFAULT,
            left_open=True,
        )
        v4a_battle_approach_drive_relaxation = _require_unit_interval(
            "v4a_battle_approach_drive_relaxation",
            V4A_BATTLE_APPROACH_DRIVE_RELAXATION_DEFAULT,
            left_open=True,
        )
        v4a_battle_near_contact_internal_stability_blend = _require_unit_interval(
            "v4a_battle_near_contact_internal_stability_blend",
            V4A_NEAR_CONTACT_INTERNAL_STABILITY_BLEND_DEFAULT,
            left_open=False,
        )
        v4a_battle_near_contact_speed_relaxation = _require_unit_interval(
            "v4a_battle_near_contact_speed_relaxation",
            V4A_NEAR_CONTACT_SPEED_RELAXATION_DEFAULT,
            left_open=True,
        )
        engaged_speed_scale = _require_unit_interval(
            "engaged_speed_scale",
            V4A_ENGAGED_SPEED_SCALE_DEFAULT,
            left_open=True,
        )
        attack_speed_lateral_scale = _require_unit_interval(
            "attack_speed_lateral_scale",
            V4A_ATTACK_SPEED_LATERAL_SCALE_DEFAULT,
            left_open=True,
        )
        attack_speed_backward_scale = float(
            movement_cfg.get(
                "attack_speed_backward_scale",
                V4A_ATTACK_SPEED_BACKWARD_SCALE_DEFAULT,
            )
        )
        if not 0.0 <= attack_speed_backward_scale <= attack_speed_lateral_scale:
            raise ValueError(
                "run_simulation movement_cfg['attack_speed_backward_scale'] must be within "
                f"[0.0, attack_speed_lateral_scale], got backward={attack_speed_backward_scale}, "
                f"lateral={attack_speed_lateral_scale}"
            )
        v4a_battle_target_front_strip_gap_bias = float(
            movement_cfg.get(
                "v4a_battle_target_front_strip_gap_bias",
                V4A_BATTLE_TARGET_FRONT_STRIP_GAP_BIAS_DEFAULT,
            )
        )
        if not math.isfinite(v4a_battle_target_front_strip_gap_bias):
            raise ValueError(
                "run_simulation movement_cfg['v4a_battle_target_front_strip_gap_bias'] must be finite, "
                f"got {v4a_battle_target_front_strip_gap_bias}"
            )
        v4a_battle_relation_lead_ticks = float(
            movement_cfg.get(
                "v4a_battle_relation_lead_ticks",
                V4A_BATTLE_RELATION_LEAD_TICKS_DEFAULT,
            )
        )
        if not math.isfinite(v4a_battle_relation_lead_ticks) or v4a_battle_relation_lead_ticks <= 0.0:
            raise ValueError(
                "run_simulation movement_cfg['v4a_battle_relation_lead_ticks'] must be finite and > 0, "
                f"got {v4a_battle_relation_lead_ticks}"
            )

        return {
            "restore_strength": float(movement_cfg.get("v4a_restore_strength", 0.25)),
            "shape": {
                "expected_reference_spacing": float(
                    movement_cfg.get("expected_reference_spacing", 1.0)
                ),
                "reference_layout_mode": str(
                    movement_cfg.get(
                        "reference_layout_mode",
                        V4A_REFERENCE_LAYOUT_MODE_RECT_CENTERED_4_0,
                    )
                ),
                "reference_surface_mode": str(v4a_reference_surface_mode),
                "soft_morphology_relaxation": float(v4a_soft_morphology_relaxation),
                "shape_vs_advance_strength": float(v4a_shape_vs_advance_strength),
                "heading_relaxation": float(v4a_heading_relaxation),
            },
            "battle": {
                "battle_standoff_hold_band_ratio": float(v4a_battle_standoff_hold_band_ratio),
                "battle_target_front_strip_gap_bias": float(v4a_battle_target_front_strip_gap_bias),
                "battle_hold_weight_strength": float(v4a_battle_hold_weight_strength),
                "battle_relation_lead_ticks": float(v4a_battle_relation_lead_ticks),
                "battle_hold_relaxation": float(v4a_battle_hold_relaxation),
                "battle_approach_drive_relaxation": float(v4a_battle_approach_drive_relaxation),
                "battle_near_contact_internal_stability_blend": float(
                    v4a_battle_near_contact_internal_stability_blend
                ),
                "battle_near_contact_speed_relaxation": float(
                    v4a_battle_near_contact_speed_relaxation
                ),
            },
            "motion": {
                "engaged_speed_scale": float(engaged_speed_scale),
                "attack_speed_lateral_scale": float(attack_speed_lateral_scale),
                "attack_speed_backward_scale": float(attack_speed_backward_scale),
            },
        }

    @staticmethod
    def prepare_runtime_context(
        *,
        execution_cfg: Mapping[str, Any],
        runtime_cfg: Mapping[str, Any],
        observer_cfg: Mapping[str, Any],
        fixture_context: Mapping[str, Any],
    ) -> dict[str, Any]:
        movement_cfg = _require_mapping(runtime_cfg, "movement")
        contact_cfg = _require_mapping(runtime_cfg, "contact")
        boundary_cfg = _require_mapping(runtime_cfg, "boundary")
        fixture_active_mode = str(fixture_context["active_mode"])
        fixture_active = bool(fixture_context["active"])
        fixture_fleet_id = str(fixture_context["fleet_id"])
        fixture_objective_point_xy = tuple(fixture_context["objective_point_xy"])
        fixture_objective_contract_3d = dict(fixture_context["objective_contract_3d"])
        fixture_stop_radius = float(fixture_context["stop_radius"])
        v4a_bundle_profile = _ExecutionWiringSupport._build_v4a_bundle_profile(movement_cfg)

        hybrid_v2_cfg = contact_cfg.get("hybrid_v2", {})
        if not isinstance(hybrid_v2_cfg, Mapping):
            hybrid_v2_cfg = {}
        steps = int(execution_cfg["steps"])
        capture_positions = bool(execution_cfg["capture_positions"])
        capture_hit_points = bool(execution_cfg.get("capture_hit_points", False))
        frame_stride = int(execution_cfg["frame_stride"])
        include_target_lines = bool(execution_cfg["include_target_lines"])
        print_tick_summary = bool(execution_cfg["print_tick_summary"])
        tick_timing_enabled = bool(observer_cfg.get("tick_timing_enabled", True))
        post_elimination_extra_ticks = max(0, int(execution_cfg.get("post_elimination_extra_ticks", 10)))
        if str(runtime_cfg["movement_model"]).strip().lower() != "v4a":
            raise ValueError(
                "test_run maintained path only supports runtime_cfg['movement_model']='v4a', "
                f"got {runtime_cfg['movement_model']!r}"
            )
        hostile_contact_impedance_mode = (
            str(contact_cfg.get("hostile_contact_impedance_mode", HOSTILE_CONTACT_IMPEDANCE_MODE_DEFAULT)).strip().lower()
            or HOSTILE_CONTACT_IMPEDANCE_MODE_DEFAULT
        )
        if hostile_contact_impedance_mode not in HOSTILE_CONTACT_IMPEDANCE_MODE_LABELS:
            allowed_text = ", ".join(sorted(HOSTILE_CONTACT_IMPEDANCE_MODE_LABELS))
            raise ValueError(
                "run_simulation contact_cfg['hostile_contact_impedance_mode'] must be one of "
                f"{{{allowed_text}}}, got {contact_cfg.get('hostile_contact_impedance_mode')!r}"
            )

        observer_active = (bool(observer_cfg["enabled"]) or bool(execution_cfg["plot_diagnostics_enabled"])) and (
            bool(capture_positions) or bool(observer_cfg.get("runtime_diag_enabled", False))
        )
        engine = EngineTickSkeleton(
            attack_range=float(contact_cfg["attack_range"]),
            damage_per_tick=float(contact_cfg["damage_per_tick"]),
            separation_radius=float(contact_cfg["separation_radius"]),
        )
        if fixture_active:
            engine.TEST_RUN_FIXTURE_CFG = {
                "active_mode": fixture_active_mode,
                "fleet_id": fixture_fleet_id,
                "objective_contract_3d": dict(fixture_objective_contract_3d),
                "stop_radius": fixture_stop_radius,
            }
        for attr, value in (
            ("SYMMETRIC_MOVEMENT_SYNC_ENABLED", bool(movement_cfg.get("symmetric_movement_sync_enabled", True))),
            ("HOSTILE_CONTACT_IMPEDANCE_MODE", hostile_contact_impedance_mode),
            (
                "HOSTILE_CONTACT_IMPEDANCE_V2_RADIUS_MULTIPLIER",
                max(1e-6, float(hybrid_v2_cfg.get("radius_multiplier", HOSTILE_CONTACT_IMPEDANCE_V2_RADIUS_MULTIPLIER_DEFAULT))),
            ),
            (
                "HOSTILE_CONTACT_IMPEDANCE_V2_REPULSION_MAX_DISP_RATIO",
                max(
                    0.0,
                    float(hybrid_v2_cfg.get("repulsion_max_disp_ratio", HOSTILE_CONTACT_IMPEDANCE_V2_REPULSION_MAX_DISP_RATIO_DEFAULT)),
                ),
            ),
            (
                "HOSTILE_CONTACT_IMPEDANCE_V2_FORWARD_DAMPING_STRENGTH",
                _clamp01(
                    float(hybrid_v2_cfg.get("forward_damping_strength", HOSTILE_CONTACT_IMPEDANCE_V2_FORWARD_DAMPING_STRENGTH_DEFAULT))
                ),
            ),
        ):
            setattr(engine, attr, value)

        movement_surface = _require_engine_surface_dict(engine, "_movement_surface")
        movement_surface["alpha_sep"] = max(0.0, float(contact_cfg["alpha_sep"]))
        movement_surface["model"] = "v4a"
        movement_surface["v4a_restore_strength"] = float(v4a_bundle_profile["restore_strength"])
        combat_surface = _require_engine_surface_dict(engine, "_combat_surface")
        combat_surface["fire_quality_alpha"] = float(contact_cfg["fire_quality_alpha"])
        combat_surface["fire_optimal_range_ratio"] = float(contact_cfg["fire_optimal_range_ratio"])
        combat_surface["fire_cone_half_angle_deg"] = float(contact_cfg["fire_cone_half_angle_deg"])
        combat_surface["contact_hysteresis_h"] = float(contact_cfg["contact_hysteresis_h"])
        combat_surface["ch_enabled"] = bool(contact_cfg["ch_enabled"])
        boundary_surface = _require_engine_surface_dict(engine, "_boundary_surface")
        boundary_surface["soft_enabled"] = bool(boundary_cfg["enabled"])
        boundary_surface["hard_enabled"] = bool(boundary_cfg["enabled"]) and bool(boundary_cfg["hard_enabled"])
        boundary_surface["soft_strength"] = max(0.0, float(boundary_cfg["soft_strength"]))
        diag_surface = _require_engine_surface_dict(engine, "_diag_surface")
        diag_surface["runtime_diag_enabled"] = observer_active
        diag_surface["diag4_enabled"] = observer_active

        return {
            "contact_cfg": contact_cfg,
            "fixture_active_mode": fixture_active_mode,
            "fixture_active": fixture_active,
            "fixture_fleet_id": fixture_fleet_id,
            "fixture_objective_point_xy": fixture_objective_point_xy,
            "fixture_objective_contract_3d": fixture_objective_contract_3d,
            "fixture_stop_radius": fixture_stop_radius,
            "steps": steps,
            "capture_positions": capture_positions,
            "capture_hit_points": capture_hit_points,
            "frame_stride": frame_stride,
            "include_target_lines": include_target_lines,
            "print_tick_summary": print_tick_summary,
            "tick_timing_enabled": tick_timing_enabled,
            "post_elimination_extra_ticks": post_elimination_extra_ticks,
            "observer_active": observer_active,
            "engine": engine,
            "v4a_bundle_profile": v4a_bundle_profile,
        }


class _FixtureExecutionSupport:
    """Internal-only execution support for fixture/reference bundle preparation."""

    @staticmethod
    def compute_centroid_and_rms_radius(
        position_map: Mapping[str, tuple[float, float]],
    ) -> tuple[float, float, float]:
        if not position_map:
            return (float("nan"), float("nan"), 0.0)
        xs = [float(position[0]) for position in position_map.values()]
        ys = [float(position[1]) for position in position_map.values()]
        centroid_x = sum(xs) / float(len(xs))
        centroid_y = sum(ys) / float(len(ys))
        radius_sq_mean = sum(
            ((x - centroid_x) * (x - centroid_x)) + ((y - centroid_y) * (y - centroid_y))
            for x, y in zip(xs, ys, strict=False)
        ) / float(len(xs))
        return (centroid_x, centroid_y, math.sqrt(max(0.0, radius_sq_mean)))

    @staticmethod
    def build_fixture_expected_reference_bundle(
        position_map: Mapping[str, tuple[float, float]],
        objective_point_xy: tuple[float, float],
        *,
        ordered_unit_ids: Sequence[str] | None = None,
        v4a_profile: Mapping[str, Any],
        fallback_axis_xy: tuple[float, float] = (1.0, 0.0),
    ) -> dict[str, Any]:
        shape_cfg = _require_mapping(v4a_profile, "shape")
        battle_cfg = _require_mapping(v4a_profile, "battle")
        motion_cfg = _require_mapping(v4a_profile, "motion")
        expected_reference_spacing = float(shape_cfg["expected_reference_spacing"])
        reference_layout_mode = str(shape_cfg["reference_layout_mode"])
        centroid_x, centroid_y, _ = _FixtureExecutionSupport.compute_centroid_and_rms_radius(position_map)
        if not math.isfinite(centroid_x) or not math.isfinite(centroid_y):
            raise ValueError("neutral expected-position reference requires at least one alive unit")
        primary_dx = float(objective_point_xy[0]) - centroid_x
        primary_dy = float(objective_point_xy[1]) - centroid_y
        primary_norm = math.sqrt((primary_dx * primary_dx) + (primary_dy * primary_dy))
        if primary_norm <= 1e-12:
            fallback_dx = float(fallback_axis_xy[0]) if len(fallback_axis_xy) >= 1 else 1.0
            fallback_dy = float(fallback_axis_xy[1]) if len(fallback_axis_xy) >= 2 else 0.0
            fallback_norm = math.sqrt((fallback_dx * fallback_dx) + (fallback_dy * fallback_dy))
            if fallback_norm <= 1e-12:
                fallback_dx, fallback_dy, fallback_norm = 1.0, 0.0, 1.0
            primary_axis_xy = (fallback_dx / fallback_norm, fallback_dy / fallback_norm)
        else:
            primary_axis_xy = (primary_dx / primary_norm, primary_dy / primary_norm)
        secondary_axis_xy = (-primary_axis_xy[1], primary_axis_xy[0])
        actual_offsets_local: dict[str, tuple[float, float]] = {}
        for unit_id, position in position_map.items():
            rel_x = float(position[0]) - centroid_x
            rel_y = float(position[1]) - centroid_y
            forward_offset = (rel_x * primary_axis_xy[0]) + (rel_y * primary_axis_xy[1])
            lateral_offset = (rel_x * secondary_axis_xy[0]) + (rel_y * secondary_axis_xy[1])
            actual_offsets_local[str(unit_id)] = (float(forward_offset), float(lateral_offset))
        ordered_reference_unit_ids = [
            str(unit_id)
            for unit_id in (
                ordered_unit_ids
                if ordered_unit_ids is not None
                else tuple(position_map.keys())
            )
            if str(unit_id) in position_map
        ]
        if len(ordered_reference_unit_ids) != len(position_map):
            ordered_reference_unit_ids = [str(unit_id) for unit_id in position_map.keys()]
        reference_offsets_local = _build_reference_slot_offsets_local(
            ordered_reference_unit_ids,
            expected_reference_spacing=float(expected_reference_spacing),
            reference_layout_mode=str(reference_layout_mode),
        )
        initial_front_extent = max(
            (float(offset_local[0]) for offset_local in reference_offsets_local.values()),
            default=0.0,
        )
        initial_forward_phase_by_unit, initial_lateral_phase_by_unit, forward_extent_initial, lateral_extent_initial = (
            _compute_morphology_material_phase(actual_offsets_local)
        )
        forward_extent_base = max(
            (abs(float(offset_local[0])) for offset_local in reference_offsets_local.values()),
            default=0.0,
        )
        lateral_extent_base = max(
            (abs(float(offset_local[1])) for offset_local in reference_offsets_local.values()),
            default=0.0,
        )
        target_forward_phase_by_unit, target_lateral_phase_by_unit, _, _ = _compute_morphology_material_phase(
            reference_offsets_local
        )
        return {
            "initial_forward_hat_xy": primary_axis_xy,
            "initial_secondary_hat_xy": secondary_axis_xy,
            "expected_slot_offsets_local": {
                str(unit_id): tuple(reference_offsets_local[str(unit_id)])
                for unit_id in ordered_reference_unit_ids
            },
            "reference_slot_offsets_local": {
                str(unit_id): tuple(reference_offsets_local[str(unit_id)])
                for unit_id in ordered_reference_unit_ids
            },
            "initial_front_extent": float(initial_front_extent),
            "initial_alive_count": int(len(position_map)),
            "forward_extent_initial": float(forward_extent_initial),
            "lateral_extent_initial": float(lateral_extent_initial),
            "forward_extent_base": float(forward_extent_base),
            "lateral_extent_base": float(lateral_extent_base),
            "forward_extent_current": float(forward_extent_initial),
            "lateral_extent_current": float(lateral_extent_initial),
            "forward_extent_target": float(forward_extent_base),
            "lateral_extent_target": float(lateral_extent_base),
            "morphology_axis_current_xy": primary_axis_xy,
            "morphology_center_current_xy": (float(centroid_x), float(centroid_y)),
            "formation_terminal_active": False,
            "formation_terminal_axis_xy": None,
            "formation_terminal_center_xy": None,
            "formation_terminal_latched_tick": None,
            "formation_hold_active": False,
            "formation_hold_axis_xy": None,
            "formation_hold_center_xy": None,
            "formation_hold_latched_tick": None,
            "formation_hold_forward_extent": None,
            "formation_hold_lateral_extent": None,
            "formation_hold_center_wing_differential": None,
            **shape_cfg,
            **battle_cfg,
            "battle_relation_gap_raw": 1.0,
            "battle_relation_gap_current": 1.0,
            "battle_close_drive_raw": 0.0,
            "battle_close_drive_current": 0.0,
            "battle_brake_drive_raw": 0.0,
            "battle_brake_drive_current": 0.0,
            "battle_hold_weight_raw": 0.0,
            "battle_hold_weight_current": 0.0,
            "battle_approach_drive_raw": 0.0,
            "battle_approach_drive_current": 0.0,
            "effective_fire_axis_raw_xy": primary_axis_xy,
            "effective_fire_axis_xy": primary_axis_xy,
            "effective_fire_axis_current_xy": primary_axis_xy,
            "engagement_geometry_active_raw": 0.0,
            "engagement_geometry_active": 0.0,
            "engagement_geometry_active_current": 0.0,
            "front_reorientation_weight_raw": 0.0,
            "front_reorientation_weight": 0.0,
            "front_reorientation_weight_current": 0.0,
            "effective_fire_axis_coherence_raw": 0.0,
            "effective_fire_axis_coherence": 0.0,
            "effective_fire_axis_coherence_current": 0.0,
            "front_axis_delta_deg": 0.0,
            **motion_cfg,
            "center_wing_differential_target": float(V4A_CENTER_WING_DIFFERENTIAL_DEFAULT),
            "center_wing_differential_current": float(V4A_CENTER_WING_DIFFERENTIAL_DEFAULT),
            "shape_error_current": 0.0,
            "actual_forward_extent": float(forward_extent_initial),
            "actual_lateral_extent": float(lateral_extent_initial),
            "stop_within_radius": False,
            "target_material_forward_phase_by_unit": {
                str(unit_id): float(phase)
                for unit_id, phase in target_forward_phase_by_unit.items()
            },
            "target_material_lateral_phase_by_unit": {
                str(unit_id): float(phase)
                for unit_id, phase in target_lateral_phase_by_unit.items()
            },
            "current_material_forward_phase_by_unit": {
                str(unit_id): float(phase)
                for unit_id, phase in initial_forward_phase_by_unit.items()
            },
            "current_material_lateral_phase_by_unit": {
                str(unit_id): float(phase)
                for unit_id, phase in initial_lateral_phase_by_unit.items()
            },
        }

    @staticmethod
    def compute_expected_position_rms_error(
        position_map: Mapping[str, tuple[float, float]],
        expected_position_map: Mapping[str, tuple[float, float]],
    ) -> float:
        if not position_map or not expected_position_map:
            return float("nan")
        error_sq_sum = 0.0
        count = 0
        for unit_id, position in position_map.items():
            expected_position = expected_position_map.get(str(unit_id))
            if not isinstance(expected_position, tuple) or len(expected_position) < 2:
                continue
            dx = float(position[0]) - float(expected_position[0])
            dy = float(position[1]) - float(expected_position[1])
            error_sq_sum += (dx * dx) + (dy * dy)
            count += 1
        if count <= 0:
            return float("nan")
        return math.sqrt(error_sq_sum / float(count))

    @staticmethod
    def compute_front_extent_ratio(
        position_map: Mapping[str, tuple[float, float]],
        objective_point_xy: tuple[float, float],
        initial_front_extent: float,
        fallback_axis_xy: tuple[float, float],
    ) -> float:
        if not position_map:
            return float("nan")
        centroid_x, centroid_y, _ = _FixtureExecutionSupport.compute_centroid_and_rms_radius(position_map)
        if not math.isfinite(centroid_x) or not math.isfinite(centroid_y):
            return float("nan")
        axis_dx = float(objective_point_xy[0]) - centroid_x
        axis_dy = float(objective_point_xy[1]) - centroid_y
        axis_norm = math.sqrt((axis_dx * axis_dx) + (axis_dy * axis_dy))
        if axis_norm > 1e-12:
            axis_x = axis_dx / axis_norm
            axis_y = axis_dy / axis_norm
        else:
            axis_x = float(fallback_axis_xy[0])
            axis_y = float(fallback_axis_xy[1])
        front_extent = max(
            (((float(position[0]) - centroid_x) * axis_x) + ((float(position[1]) - centroid_y) * axis_y))
            for position in position_map.values()
        )
        if initial_front_extent <= 1e-12:
            return float("nan")
        return float(front_extent) / float(initial_front_extent)


class TestModeEngineTickSkeleton(EngineTickSkeleton):
    """Compatibility shell retained only for cold-path imports."""

    pass

def run_simulation(
    initial_state: BattleState,
    *,
    execution_cfg: Mapping[str, Any],
    runtime_cfg: Mapping[str, Any],
    observer_cfg: Mapping[str, Any],
):
    # 1. Validate cfg and build the maintained runtime execution context.
    fixture_context = _resolve_fixture_execution_context(
        initial_state,
        execution_cfg.get("fixture", {}),
    )
    execution_context = _ExecutionWiringSupport.prepare_runtime_context(
        execution_cfg=execution_cfg,
        runtime_cfg=runtime_cfg,
        observer_cfg=observer_cfg,
        fixture_context=fixture_context,
    )
    contact_cfg = execution_context["contact_cfg"]
    fixture_active_mode = execution_context["fixture_active_mode"]
    fixture_active = execution_context["fixture_active"]
    fixture_fleet_id = execution_context["fixture_fleet_id"]
    fixture_objective_point_xy = execution_context["fixture_objective_point_xy"]
    fixture_objective_contract_3d = execution_context["fixture_objective_contract_3d"]
    fixture_stop_radius = execution_context["fixture_stop_radius"]
    steps = execution_context["steps"]
    capture_positions = execution_context["capture_positions"]
    capture_hit_points = execution_context["capture_hit_points"]
    frame_stride = execution_context["frame_stride"]
    include_target_lines = execution_context["include_target_lines"]
    print_tick_summary = execution_context["print_tick_summary"]
    tick_timing_enabled = execution_context["tick_timing_enabled"]
    post_elimination_extra_ticks = execution_context["post_elimination_extra_ticks"]
    observer_active = execution_context["observer_active"]
    engine = execution_context["engine"]
    v4a_bundle_profile = execution_context["v4a_bundle_profile"]

    state = replace(
        initial_state,
        last_target_direction={
            fleet_id: initial_state.last_target_direction.get(fleet_id, (0.0, 0.0))
            for fleet_id in initial_state.fleets
        },
    )
    fleet_ids = tuple(state.fleets)

    def _per_fleet_series() -> dict[str, list]:
        return {fleet_id: [] for fleet_id in fleet_ids}

    def _build_fleet_body_summary_for_state(current_state: BattleState) -> dict[str, dict[str, float]]:
        summary: dict[str, dict[str, float]] = {}
        for fleet_id, fleet in current_state.fleets.items():
            alive_units = [
                current_state.units[unit_id]
                for unit_id in fleet.unit_ids
                if unit_id in current_state.units and float(current_state.units[unit_id].hit_points) > 0.0
            ]
            if not alive_units:
                summary[str(fleet_id)] = {
                    "centroid_x": 0.0,
                    "centroid_y": 0.0,
                    "rms_radius": 0.0,
                    "max_radius": 0.0,
                    "heading_x": 0.0,
                    "heading_y": 1.0,
                    "alive_unit_count": 0,
                    "alive_total_hp": 0.0,
                }
                continue
            centroid_x = sum(float(unit.position.x) for unit in alive_units) / float(len(alive_units))
            centroid_y = sum(float(unit.position.y) for unit in alive_units) / float(len(alive_units))
            radius_sq_values = [
                ((float(unit.position.x) - centroid_x) * (float(unit.position.x) - centroid_x))
                + ((float(unit.position.y) - centroid_y) * (float(unit.position.y) - centroid_y))
                for unit in alive_units
            ]
            heading_sum_x = sum(float(unit.orientation_vector.x) for unit in alive_units)
            heading_sum_y = sum(float(unit.orientation_vector.y) for unit in alive_units)
            heading_hat_xy, heading_norm = EngineTickSkeleton._normalize_direction(
                heading_sum_x,
                heading_sum_y,
            )
            if heading_norm <= 0.0:
                heading_hat_xy = (0.0, 1.0)
            summary[str(fleet_id)] = {
                "centroid_x": float(centroid_x),
                "centroid_y": float(centroid_y),
                "rms_radius": float(
                    math.sqrt(max(0.0, sum(radius_sq_values) / float(len(radius_sq_values))))
                ),
                "max_radius": float(
                    math.sqrt(max(0.0, max(radius_sq_values, default=0.0)))
                ),
                "heading_x": float(heading_hat_xy[0]),
                "heading_y": float(heading_hat_xy[1]),
                "alive_unit_count": int(len(alive_units)),
                "alive_total_hp": float(sum(float(unit.hit_points) for unit in alive_units)),
            }
        return summary

    # 2. Build prepared fixture and restore bundles.
    battle_restore_bundles_by_fleet: dict[str, dict[str, Any]] = {}
    for fleet_id, fleet in initial_state.fleets.items():
        fleet_positions = {
            str(unit_id): (
                float(initial_state.units[unit_id].position.x),
                float(initial_state.units[unit_id].position.y),
            )
            for unit_id in fleet.unit_ids
            if unit_id in initial_state.units and float(initial_state.units[unit_id].hit_points) > 0.0
        }
        if not fleet_positions:
            continue
        enemy_positions = {
            str(unit_id): (
                float(initial_state.units[unit_id].position.x),
                float(initial_state.units[unit_id].position.y),
            )
            for other_fleet_id, other_fleet in initial_state.fleets.items()
            if other_fleet_id != fleet_id
            for unit_id in other_fleet.unit_ids
            if unit_id in initial_state.units and float(initial_state.units[unit_id].hit_points) > 0.0
        }
        initial_forward_sum_x = 0.0
        initial_forward_sum_y = 0.0
        for unit_id in fleet.unit_ids:
            unit = initial_state.units.get(unit_id)
            if unit is None or float(unit.hit_points) <= 0.0:
                continue
            initial_forward_sum_x += float(unit.orientation_vector.x)
            initial_forward_sum_y += float(unit.orientation_vector.y)
        fleet_centroid_x, fleet_centroid_y, _ = _FixtureExecutionSupport.compute_centroid_and_rms_radius(fleet_positions)
        enemy_centroid_x, enemy_centroid_y, _ = _FixtureExecutionSupport.compute_centroid_and_rms_radius(enemy_positions)
        if math.isfinite(enemy_centroid_x) and math.isfinite(enemy_centroid_y):
            objective_point_xy = (float(enemy_centroid_x), float(enemy_centroid_y))
        else:
            fallback_axis_norm = math.sqrt(
                (initial_forward_sum_x * initial_forward_sum_x) + (initial_forward_sum_y * initial_forward_sum_y)
            )
            if fallback_axis_norm <= 1e-12:
                fallback_axis_x, fallback_axis_y = 1.0, 0.0
            else:
                fallback_axis_x = initial_forward_sum_x / fallback_axis_norm
                fallback_axis_y = initial_forward_sum_y / fallback_axis_norm
            objective_point_xy = (
                float(fleet_centroid_x) + float(fallback_axis_x),
                float(fleet_centroid_y) + float(fallback_axis_y),
            )
        bundle = _FixtureExecutionSupport.build_fixture_expected_reference_bundle(
            fleet_positions,
            objective_point_xy,
            ordered_unit_ids=tuple(fleet.unit_ids),
            v4a_profile=v4a_bundle_profile,
            fallback_axis_xy=(initial_forward_sum_x, initial_forward_sum_y),
        )
        bundle["objective_point_xy"] = (
            float(objective_point_xy[0]),
            float(objective_point_xy[1]),
        )
        battle_restore_bundles_by_fleet[str(fleet_id)] = bundle
    if battle_restore_bundles_by_fleet:
        engine.TEST_RUN_BATTLE_RESTORE_BUNDLES_BY_FLEET = battle_restore_bundles_by_fleet

    # 3. Initialize observer state and local packaging helpers.
    trajectory = _per_fleet_series()
    alive_trajectory = _per_fleet_series()
    fleet_size_trajectory = _per_fleet_series()
    observer_telemetry = {
        **{
            key: _per_fleet_series()
            for key in (
                "centroid_x",
                "centroid_y",
                "center_wing_advance_gap",
                "front_curvature_index",
                "center_wing_parallel_share",
                "posture_persistence_time",
                "fire_efficiency",
            )
        },
        "net_axis_push": {"net": []},
        "net_axis_push_interval_ticks": 10,
        "center_wing_advance_gap_interval_ticks": 10,
        "hostile_overlap_pairs": [],
        "hostile_deep_pairs": [],
        "hostile_deep_intermix_ratio": [],
        "hostile_intermix_severity": [],
        "hostile_intermix_coverage": [],
        "tick_timing_enabled": bool(tick_timing_enabled),
        "tick_elapsed_ms": [],
    }
    if fixture_active:
        initial_positions = {
            str(unit_id): (
                float(initial_state.units[unit_id].position.x),
                float(initial_state.units[unit_id].position.y),
            )
            for unit_id in initial_state.fleets[fixture_fleet_id].unit_ids
            if unit_id in initial_state.units and float(initial_state.units[unit_id].hit_points) > 0.0
        }
        initial_forward_sum_x = 0.0
        initial_forward_sum_y = 0.0
        for unit_id in initial_state.fleets[fixture_fleet_id].unit_ids:
            unit = initial_state.units.get(unit_id)
            if unit is None or float(unit.hit_points) <= 0.0:
                continue
            initial_forward_sum_x += float(unit.orientation_vector.x)
            initial_forward_sum_y += float(unit.orientation_vector.y)
        fixture_reference_bundle = _FixtureExecutionSupport.build_fixture_expected_reference_bundle(
            initial_positions,
            fixture_objective_point_xy,
            ordered_unit_ids=tuple(initial_state.fleets[fixture_fleet_id].unit_ids),
            v4a_profile=v4a_bundle_profile,
            fallback_axis_xy=(initial_forward_sum_x, initial_forward_sum_y),
        )
        fixture_reference_bundle["objective_point_xy"] = (
            float(fixture_objective_point_xy[0]),
            float(fixture_objective_point_xy[1]),
        )
        fixture_reference_bundle["stop_radius"] = float(fixture_stop_radius)
        engine.TEST_RUN_FIXTURE_REFERENCE_BUNDLE = fixture_reference_bundle
        initial_centroid_x, initial_centroid_y, initial_rms_radius = _FixtureExecutionSupport.compute_centroid_and_rms_radius(initial_positions)
        initial_distance = math.sqrt(
            ((initial_centroid_x - fixture_objective_point_xy[0]) ** 2)
            + ((initial_centroid_y - fixture_objective_point_xy[1]) ** 2)
        ) if math.isfinite(initial_centroid_x) and math.isfinite(initial_centroid_y) else float("nan")
        fixture_candidate_a_active = True
        engine.TEST_RUN_FIXTURE_CFG["expected_position_candidate_active"] = fixture_candidate_a_active
        engine.TEST_RUN_FIXTURE_CFG["initial_forward_hat_xy"] = fixture_reference_bundle["initial_forward_hat_xy"]
        engine.TEST_RUN_FIXTURE_CFG["expected_slot_offsets_local"] = fixture_reference_bundle["expected_slot_offsets_local"]
        engine.TEST_RUN_FIXTURE_CFG["frozen_terminal_frame_active"] = False
        engine.TEST_RUN_FIXTURE_CFG["frozen_terminal_primary_axis_xy"] = None
        engine.TEST_RUN_FIXTURE_CFG["frozen_terminal_secondary_axis_xy"] = None
        engine.TEST_RUN_FIXTURE_CFG["frozen_terminal_latched_tick"] = None
        observer_telemetry["fixture"] = {
            "active_mode": fixture_active_mode,
            "fleet_id": fixture_fleet_id,
            "anchor_point_xyz": [
                float(fixture_objective_contract_3d["anchor_point_xyz"][0]),
                float(fixture_objective_contract_3d["anchor_point_xyz"][1]),
                float(fixture_objective_contract_3d["anchor_point_xyz"][2]),
            ],
            "projected_anchor_point_xy": [fixture_objective_point_xy[0], fixture_objective_point_xy[1]],
            "source_owner": str(fixture_objective_contract_3d["source_owner"]),
            "objective_mode": str(fixture_objective_contract_3d["objective_mode"]),
            "no_enemy_semantics": str(fixture_objective_contract_3d["no_enemy_semantics"]),
            "stop_radius": fixture_stop_radius,
            "initial_centroid_to_objective_distance": float(initial_distance),
            "initial_rms_radius": float(initial_rms_radius),
            "initial_front_extent": float(fixture_reference_bundle["initial_front_extent"]),
            "expected_position_candidate_active": bool(fixture_candidate_a_active),
            "objective_reached_tick": None,
            "frozen_terminal_frame_active": False,
            "frozen_terminal_latched_tick": None,
            "frozen_terminal_primary_axis_xy": None,
            "centroid_to_objective_distance": [],
            "formation_rms_radius": [],
            "formation_rms_radius_ratio": [],
            "expected_position_rms_error": [],
            "front_extent_ratio": [],
            "corrected_unit_ratio": [],
            "projection_pairs_count": [],
            "projection_mean_displacement": [],
            "projection_max_displacement": [],
            "shape_error_current": [],
            "transition_advance_share": [],
            "legality_reference_surface_count": [],
            "legality_feasible_surface_count": [],
            "legality_middle_stage_active": [],
            "legality_handoff_ready": [],
            "late_terminal_decomposition_trace": [],
        }
        battle_restore_bundles_by_fleet[str(fixture_fleet_id)] = fixture_reference_bundle
    if battle_restore_bundles_by_fleet:
        engine.TEST_RUN_BATTLE_RESTORE_BUNDLES_BY_FLEET = battle_restore_bundles_by_fleet
    combat_telemetry = {
        "in_contact_count": [],
        "damage_events_count": [],
    }
    position_frames = []
    center_wing_interval_ticks = int(observer_telemetry.get("center_wing_advance_gap_interval_ticks", 10))
    center_wing_position_history = _per_fleet_series()
    posture_persistence_state = {fleet_id: {"sign": 0, "length": 0} for fleet_id in fleet_ids}

    def _read_v4a_bridge_float(
        diag_tick: Mapping[str, Any],
        fleet_id: str,
        key: str,
        fallback: float,
    ) -> float:
        bridge_diag = diag_tick.get("v4a_bridge", {}) if isinstance(diag_tick, Mapping) else {}
        if not isinstance(bridge_diag, Mapping):
            return float(fallback)
        bridge_fleets = bridge_diag.get("fleets", {})
        if not isinstance(bridge_fleets, Mapping):
            return float(fallback)
        fleet_diag = bridge_fleets.get(str(fleet_id), {})
        if not isinstance(fleet_diag, Mapping):
            return float(fallback)
        return float(fleet_diag.get(key, fallback))

    # Observer/frame packaging stays local to the orchestrator.
    def _build_focus_indicator_payload(
        current_state: BattleState,
        runtime_diag_tick: Mapping[str, Any],
    ) -> dict[str, dict[str, float]]:
        focus_payload: dict[str, dict[str, float]] = {}
        bundle_entries: dict[str, Mapping[str, Any]] = {}
        if fixture_active and fixture_active_mode == FIXTURE_MODE_NEUTRAL:
            fixture_bundle = getattr(engine, "TEST_RUN_FIXTURE_REFERENCE_BUNDLE", None)
            if isinstance(fixture_bundle, Mapping):
                bundle_entries[str(fixture_fleet_id)] = fixture_bundle
        else:
            battle_bundles = getattr(engine, "TEST_RUN_BATTLE_RESTORE_BUNDLES_BY_FLEET", None)
            if isinstance(battle_bundles, Mapping):
                for fleet_id, bundle in battle_bundles.items():
                    if isinstance(bundle, Mapping):
                        bundle_entries[str(fleet_id)] = bundle
        fire_efficiency_current: dict[str, float] = {}
        fire_eff_a_series, fire_eff_b_series = _compute_fire_efficiency_series(
            fleet_size_trajectory.get("A", []),
            fleet_size_trajectory.get("B", []),
            alive_trajectory.get("A", []),
            alive_trajectory.get("B", []),
            per_unit_damage=float(contact_cfg.get("damage_per_tick", 0.0)),
        )
        fire_efficiency_current["A"] = float(fire_eff_a_series[-1]) if fire_eff_a_series else float("nan")
        fire_efficiency_current["B"] = float(fire_eff_b_series[-1]) if fire_eff_b_series else float("nan")
        battle_gap_metrics: dict[str, float] = {}
        if (not fixture_active) and len(current_state.fleets) == 2:
            fleet_ids_local = [str(fleet_id) for fleet_id in current_state.fleets.keys()]
            if len(fleet_ids_local) == 2:
                fleet_a_id, fleet_b_id = fleet_ids_local
                units_a = [
                    current_state.units[unit_id]
                    for unit_id in current_state.fleets[fleet_a_id].unit_ids
                    if unit_id in current_state.units and float(current_state.units[unit_id].hit_points) > 0.0
                ]
                units_b = [
                    current_state.units[unit_id]
                    for unit_id in current_state.fleets[fleet_b_id].unit_ids
                    if unit_id in current_state.units and float(current_state.units[unit_id].hit_points) > 0.0
                ]
                if units_a and units_b:
                    centroid_a_x, centroid_a_y, rms_a = _FixtureExecutionSupport.compute_centroid_and_rms_radius(
                        {
                            str(unit.unit_id): (float(unit.position.x), float(unit.position.y))
                            for unit in units_a
                        }
                    )
                    centroid_b_x, centroid_b_y, rms_b = _FixtureExecutionSupport.compute_centroid_and_rms_radius(
                        {
                            str(unit.unit_id): (float(unit.position.x), float(unit.position.y))
                            for unit in units_b
                        }
                    )
                    axis_dx = float(centroid_b_x) - float(centroid_a_x)
                    axis_dy = float(centroid_b_y) - float(centroid_a_y)
                    centroid_distance = math.sqrt((axis_dx * axis_dx) + (axis_dy * axis_dy))
                    if centroid_distance > 0.0:
                        axis_hat_xy = (
                            float(axis_dx / centroid_distance),
                            float(axis_dy / centroid_distance),
                        )
                        front_a, _ = _compute_projected_half_extents(units_a, axis_hat_xy)
                        front_b, _ = _compute_projected_half_extents(units_b, axis_hat_xy)
                        strip_a = _compute_front_strip_depth(
                            units_a,
                            axis_hat_xy,
                            toward_positive=True,
                        )
                        strip_b = _compute_front_strip_depth(
                            units_b,
                            axis_hat_xy,
                            toward_positive=False,
                        )
                        battle_gap_metrics = {
                            "centroid_distance": float(centroid_distance),
                            "rms_gap": float(centroid_distance - (float(rms_a) + float(rms_b))),
                            "front_gap": float(centroid_distance - (float(front_a) + float(front_b))),
                            "front_strip_gap": float(centroid_distance - (float(strip_a) + float(strip_b))),
                            "front_strip_depth_a": float(strip_a),
                            "front_strip_depth_b": float(strip_b),
                        }
        for fleet_id, bundle in bundle_entries.items():
            target_direction = current_state.last_target_direction.get(str(fleet_id), (0.0, 0.0))
            td_x = float(target_direction[0]) if len(target_direction) >= 1 else 0.0
            td_y = float(target_direction[1]) if len(target_direction) >= 2 else 0.0
            focus_payload[str(fleet_id)] = {
                "td_norm": math.sqrt((td_x * td_x) + (td_y * td_y)),
                "forward_current": float(bundle.get("forward_extent_current", float("nan"))),
                "actual_forward": float(bundle.get("actual_forward_extent", float("nan"))),
                "lateral_current": float(bundle.get("lateral_extent_current", float("nan"))),
                "actual_lateral": float(bundle.get("actual_lateral_extent", float("nan"))),
                "shape_err": float(bundle.get("shape_error_current", float("nan"))),
                "advance_share": _read_v4a_bridge_float(
                    runtime_diag_tick,
                    fleet_id,
                    "transition_advance_share",
                    float("nan"),
                ),
                "relation_gap": float(bundle.get("battle_relation_gap_current", float("nan"))),
                "approach_drive": float(bundle.get("battle_approach_drive_current", float("nan"))),
                "close_drive": float(bundle.get("battle_close_drive_current", float("nan"))),
                "brake_drive": float(bundle.get("battle_brake_drive_current", float("nan"))),
                "hold_weight": float(bundle.get("battle_hold_weight_current", float("nan"))),
                "hold_weight_raw": float(bundle.get("battle_hold_weight_raw", float("nan"))),
                "engagement_geometry_active_raw": float(
                    bundle.get("engagement_geometry_active_raw", float("nan"))
                ),
                "engagement_geometry_active": float(
                    bundle.get("engagement_geometry_active", float("nan"))
                ),
                "effective_fire_axis_coherence": float(
                    bundle.get("effective_fire_axis_coherence", float("nan"))
                ),
                "front_reorientation_weight": float(
                    bundle.get("front_reorientation_weight", float("nan"))
                ),
                "front_axis_delta_deg": float(bundle.get("front_axis_delta_deg", float("nan"))),
                "centroid_distance": float(
                    battle_gap_metrics.get("centroid_distance", float("nan"))
                ),
                "rms_gap": float(battle_gap_metrics.get("rms_gap", float("nan"))),
                "front_gap": float(battle_gap_metrics.get("front_gap", float("nan"))),
                "front_strip_gap": float(battle_gap_metrics.get("front_strip_gap", float("nan"))),
                "front_strip_depth_a": float(battle_gap_metrics.get("front_strip_depth_a", float("nan"))),
                "front_strip_depth_b": float(battle_gap_metrics.get("front_strip_depth_b", float("nan"))),
                "fire_eff": float(fire_efficiency_current.get(str(fleet_id), float("nan"))),
                "center_forward_offset": float(bundle.get("center_delta_forward", float("nan"))),
                "phase_forward_mean": float(bundle.get("phase_forward_delta_mean", float("nan"))),
                "forward_align": float(
                    bundle.get("forward_transport_alignment", float("nan"))
                ),
                "forward_neg_frac": float(
                    bundle.get("forward_transport_negative_fraction", float("nan"))
                ),
                "forward_pos_frac": float(
                    bundle.get("forward_transport_positive_fraction", float("nan"))
                ),
            }
        return focus_payload

    def _append_empty_shape_metrics(fleet_id: str, series: list[float]) -> None:
        series.append(float("nan"))
        observer_telemetry["front_curvature_index"][fleet_id].append(float("nan"))
        observer_telemetry["center_wing_parallel_share"][fleet_id].append(float("nan"))
        observer_telemetry["posture_persistence_time"][fleet_id].append(0.0)
        posture_persistence_state[fleet_id]["sign"] = 0
        posture_persistence_state[fleet_id]["length"] = 0

    def _capture_position_frame(current_state: BattleState) -> None:
        if not capture_positions or frame_stride <= 0 or current_state.tick % frame_stride != 0:
            return
        frame = {"tick": current_state.tick}
        targets = {}
        for fleet_id, fleet in current_state.fleets.items():
            points = []
            for unit_id in fleet.unit_ids:
                if unit_id in current_state.units:
                    unit = current_state.units[unit_id]
                    points.append(
                        (
                            unit_id,
                            unit.position.x,
                            unit.position.y,
                            unit.orientation_vector.x,
                            unit.orientation_vector.y,
                            unit.velocity.x,
                            unit.velocity.y,
                            unit.hit_points,
                            unit.max_hit_points,
                        )
                        if capture_hit_points
                        else (
                            unit_id,
                            unit.position.x,
                            unit.position.y,
                            unit.orientation_vector.x,
                            unit.orientation_vector.y,
                            unit.velocity.x,
                            unit.velocity.y,
                        )
                    )
                    if include_target_lines and unit.engaged and unit.engaged_target_id:
                        target_id = str(unit.engaged_target_id)
                        if target_id in current_state.units and current_state.units[target_id].hit_points > 0.0:
                            targets[str(unit_id)] = target_id
            frame[fleet_id] = points
        if include_target_lines:
            frame["targets"] = targets
        runtime_diag_tick = getattr(engine, "debug_diag_last_tick", {}) if observer_active else {}
        runtime_debug = extract_runtime_debug_payload(runtime_diag_tick)
        focus_indicators = _build_focus_indicator_payload(current_state, runtime_diag_tick)
        if focus_indicators:
            runtime_debug["focus_indicators"] = focus_indicators
        frame["fleet_body_summary"] = _build_fleet_body_summary_for_state(current_state)
        frame["runtime_debug"] = runtime_debug
        position_frames.append(frame)

    # 4. Main tick loop.
    tick_limit = 999 if steps <= 0 else steps
    elimination_tick = None
    post_elimination_stop_tick = None

    while state.tick < tick_limit:
        tick_start_time = time.perf_counter() if tick_timing_enabled else None
        state = engine.step(state)
        runtime_diag_tick = getattr(engine, "debug_diag_last_tick", {}) if observer_active else {}
        if tick_timing_enabled and tick_start_time is not None:
            observer_telemetry["tick_elapsed_ms"].append((time.perf_counter() - tick_start_time) * 1000.0)
        combat_stats = getattr(engine, "debug_last_combat_stats", {})
        if not isinstance(combat_stats, dict):
            combat_stats = {}
        combat_telemetry["in_contact_count"].append(int(combat_stats.get("in_contact_count", 0)))
        combat_telemetry["damage_events_count"].append(int(combat_stats.get("damage_events_count", 0)))

        if print_tick_summary:
            ordered_fleet_ids = [fleet_id for fleet_id in ("A", "B") if fleet_id in state.fleets]
            if not ordered_fleet_ids:
                ordered_fleet_ids = sorted(state.fleets.keys())
            if len(ordered_fleet_ids) >= 2:
                fleet_a = state.fleets[ordered_fleet_ids[0]]
                fleet_b = state.fleets[ordered_fleet_ids[1]]
                name_a = str(ordered_fleet_ids[0])
                name_b = str(ordered_fleet_ids[1])
                print(f"t={state.tick}, [{name_a}] vs [{name_b}], {len(fleet_a.unit_ids)}/{len(fleet_b.unit_ids)}")
            elif len(ordered_fleet_ids) == 1:
                fleet = state.fleets[ordered_fleet_ids[0]]
                name = str(ordered_fleet_ids[0])
                print(f"t={state.tick}, [{name}], {len(fleet.unit_ids)}")

        current_unit_position_maps: dict[str, dict[str, tuple[float, float]]] = {}
        for fleet_id, fleet in state.fleets.items():
            trajectory[fleet_id].append(state.last_fleet_cohesion_score.get(fleet_id, 1.0))
            alive_trajectory[fleet_id].append(len(fleet.unit_ids))
            fleet_size = 0.0
            centroid_sum_x = 0.0
            centroid_sum_y = 0.0
            centroid_count = 0
            unit_position_map: dict[str, tuple[float, float]] = {}
            for unit_id in fleet.unit_ids:
                if unit_id in state.units:
                    unit_state = state.units[unit_id]
                    fleet_size += max(0.0, float(unit_state.hit_points))
                    centroid_sum_x += float(unit_state.position.x)
                    centroid_sum_y += float(unit_state.position.y)
                    centroid_count += 1
                    unit_position_map[str(unit_id)] = (float(unit_state.position.x), float(unit_state.position.y))
            fleet_size_trajectory[fleet_id].append(fleet_size)
            current_unit_position_maps[fleet_id] = unit_position_map
            center_wing_position_history[fleet_id].append(unit_position_map)
            if centroid_count > 0:
                observer_telemetry["centroid_x"][fleet_id].append(centroid_sum_x / float(centroid_count))
                observer_telemetry["centroid_y"][fleet_id].append(centroid_sum_y / float(centroid_count))
            else:
                observer_telemetry["centroid_x"][fleet_id].append(float("nan"))
                observer_telemetry["centroid_y"][fleet_id].append(float("nan"))

        if fixture_active:
            fixture_metrics = observer_telemetry.get("fixture", {})
            fixture_positions = current_unit_position_maps.get(fixture_fleet_id, {})
            centroid_x, centroid_y, rms_radius = _FixtureExecutionSupport.compute_centroid_and_rms_radius(fixture_positions)
            if math.isfinite(centroid_x) and math.isfinite(centroid_y):
                distance_to_objective = math.sqrt(
                    ((centroid_x - fixture_objective_point_xy[0]) ** 2)
                    + ((centroid_y - fixture_objective_point_xy[1]) ** 2)
                )
            else:
                distance_to_objective = float("nan")
            fixture_runtime_debug = extract_runtime_debug_payload(runtime_diag_tick)
            if isinstance(runtime_diag_tick, dict):
                fixture_decomposition_trace = runtime_diag_tick.get("fixture_terminal_trace")
                if isinstance(fixture_decomposition_trace, dict):
                    trace_units = fixture_decomposition_trace.get("units")
                    if isinstance(trace_units, dict):
                        fixture_metrics["late_terminal_decomposition_trace"].append(
                            {
                                "tick": int(runtime_diag_tick.get("tick", state.tick)),
                                "fleet_id": str(fixture_decomposition_trace.get("fleet_id", fixture_fleet_id)),
                                "units": {
                                    str(unit_id): dict(row)
                                    for unit_id, row in trace_units.items()
                                    if isinstance(row, dict)
                                },
                            }
                        )
            expected_position_payload = engine._build_fixture_expected_position_map(
                state=state,
                fleet_id=fixture_fleet_id,
                centroid_x=centroid_x if math.isfinite(centroid_x) else 0.0,
                centroid_y=centroid_y if math.isfinite(centroid_y) else 0.0,
                target_direction=state.movement_command_direction.get(
                    fixture_fleet_id,
                    state.last_target_direction.get(fixture_fleet_id, (0.0, 0.0)),
                ),
            )
            expected_position_map = (
                expected_position_payload.get("expected_positions", {})
                if isinstance(expected_position_payload, Mapping)
                else {}
            )
            initial_rms_radius = float(fixture_metrics.get("initial_rms_radius", 0.0))
            fixture_metrics["centroid_to_objective_distance"].append(float(distance_to_objective))
            fixture_metrics["formation_rms_radius"].append(float(rms_radius))
            fixture_metrics["formation_rms_radius_ratio"].append(
                (float(rms_radius) / initial_rms_radius)
                if initial_rms_radius > 1e-12
                else 1.0
            )
            fixture_metrics["expected_position_rms_error"].append(
                _FixtureExecutionSupport.compute_expected_position_rms_error(fixture_positions, expected_position_map)
            )
            fixture_metrics["front_extent_ratio"].append(
                _FixtureExecutionSupport.compute_front_extent_ratio(
                    fixture_positions,
                    fixture_objective_point_xy,
                    float(fixture_metrics.get("initial_front_extent", 0.0)),
                    tuple(fixture_reference_bundle["initial_forward_hat_xy"]),
                )
            )
            fixture_metrics["corrected_unit_ratio"].append(
                float(fixture_runtime_debug.get("corrected_unit_ratio", 0.0))
            )
            fixture_metrics["projection_pairs_count"].append(int(fixture_runtime_debug.get("projection_pairs_count", 0)))
            fixture_metrics["projection_mean_displacement"].append(
                float(fixture_runtime_debug.get("projection_mean_displacement", 0.0))
            )
            fixture_metrics["projection_max_displacement"].append(
                float(fixture_runtime_debug.get("projection_max_displacement", 0.0))
            )
            fixture_metrics["shape_error_current"].append(
                float(fixture_reference_bundle.get("shape_error_current", 0.0))
            )
            fixture_metrics["transition_advance_share"].append(
                _read_v4a_bridge_float(
                    runtime_diag_tick,
                    fixture_fleet_id,
                    "transition_advance_share",
                    0.0,
                )
            )
            fixture_metrics["legality_reference_surface_count"].append(
                int(fixture_runtime_debug.get("legality_reference_surface_count", 0))
            )
            fixture_metrics["legality_feasible_surface_count"].append(
                int(fixture_runtime_debug.get("legality_feasible_surface_count", 0))
            )
            fixture_metrics["legality_middle_stage_active"].append(
                bool(fixture_runtime_debug.get("legality_middle_stage_active", False))
            )
            fixture_metrics["legality_handoff_ready"].append(
                bool(fixture_runtime_debug.get("legality_handoff_ready", False))
            )
            engine.TEST_RUN_FIXTURE_REFERENCE_BUNDLE = fixture_reference_bundle
            if (
                fixture_metrics.get("objective_reached_tick") is None
                and math.isfinite(distance_to_objective)
                and distance_to_objective <= fixture_stop_radius
            ):
                fixture_metrics["objective_reached_tick"] = int(state.tick)
                elimination_tick = int(state.tick)
                post_elimination_stop_tick = min(999, elimination_tick + post_elimination_extra_ticks)
            _capture_position_frame(state)
            if (
                fixture_metrics.get("objective_reached_tick") is not None
                and post_elimination_stop_tick is not None
                and state.tick >= post_elimination_stop_tick
            ):
                break
            continue

        hostile_intermix_metrics = compute_hostile_intermix_metrics(
            state,
            float(contact_cfg["separation_radius"]),
        )
        for metric_key in (
            "hostile_overlap_pairs",
            "hostile_deep_pairs",
            "hostile_deep_intermix_ratio",
            "hostile_intermix_severity",
            "hostile_intermix_coverage",
        ):
            observer_telemetry[metric_key].append(float(hostile_intermix_metrics.get(metric_key, 0.0)))

        for fleet_id in state.fleets:
            series = observer_telemetry["center_wing_advance_gap"][fleet_id]
            history = center_wing_position_history.get(fleet_id, [])
            current_positions = history[-1] if history else {}
            current_unit_ids = list(current_positions.keys())
            enemy_centroids = []
            for other_fleet_id in state.fleets:
                if other_fleet_id == fleet_id:
                    continue
                enemy_x = float(observer_telemetry["centroid_x"].get(other_fleet_id, [float("nan")])[-1])
                enemy_y = float(observer_telemetry["centroid_y"].get(other_fleet_id, [float("nan")])[-1])
                if math.isfinite(enemy_x) and math.isfinite(enemy_y):
                    enemy_centroids.append((enemy_x, enemy_y))
            if len(current_unit_ids) < 6 or not enemy_centroids:
                _append_empty_shape_metrics(fleet_id, series)
                continue

            curr_xs_now = [current_positions[unit_id][0] for unit_id in current_unit_ids]
            curr_ys_now = [current_positions[unit_id][1] for unit_id in current_unit_ids]
            centroid_x_now = sum(curr_xs_now) / float(len(curr_xs_now))
            centroid_y_now = sum(curr_ys_now) / float(len(curr_ys_now))
            enemy_centroid_x = sum(item[0] for item in enemy_centroids) / float(len(enemy_centroids))
            enemy_centroid_y = sum(item[1] for item in enemy_centroids) / float(len(enemy_centroids))
            axis_dx = enemy_centroid_x - centroid_x_now
            axis_dy = enemy_centroid_y - centroid_y_now
            axis_norm = math.sqrt((axis_dx * axis_dx) + (axis_dy * axis_dy))
            if axis_norm <= 1e-12:
                _append_empty_shape_metrics(fleet_id, series)
                continue
            axis_dir_x = axis_dx / axis_norm
            axis_dir_y = axis_dy / axis_norm

            projected_units: list[tuple[float, float, str]] = []
            for unit_id in current_unit_ids:
                curr_x, curr_y = current_positions[unit_id]
                lateral_offset_now = ((curr_x - centroid_x_now) * (-axis_dir_y)) + ((curr_y - centroid_y_now) * axis_dir_x)
                advance_now = ((curr_x - centroid_x_now) * axis_dir_x) + ((curr_y - centroid_y_now) * axis_dir_y)
                projected_units.append((float(advance_now), abs(float(lateral_offset_now)), str(unit_id)))

            projected_units.sort(key=lambda item: item[0])
            projected_units_by_width = sorted(
                ((item[1], item[2]) for item in projected_units),
                key=lambda item: item[0],
            )
            width_split_index = len(projected_units_by_width) // 2
            center_unit_ids = {unit_id for _, unit_id in projected_units_by_width[:width_split_index]}
            wing_unit_ids = {unit_id for _, unit_id in projected_units_by_width[width_split_index:]}

            if len(history) <= center_wing_interval_ticks:
                series.append(float("nan"))
                interval_parallel_share_gap = float("nan")
            else:
                prev_positions = history[-(center_wing_interval_ticks + 1)]
                common_unit_ids = [unit_id for unit_id in current_positions if unit_id in prev_positions]
                if len(common_unit_ids) < 4:
                    series.append(float("nan"))
                    interval_parallel_share_gap = float("nan")
                else:
                    center_advances: list[float] = []
                    wing_advances: list[float] = []
                    center_interval_total = 0.0
                    wing_interval_total = 0.0
                    for unit_id in common_unit_ids:
                        curr_x, curr_y = current_positions[unit_id]
                        prev_x, prev_y = prev_positions[unit_id]
                        advance = ((curr_x - prev_x) * axis_dir_x) + ((curr_y - prev_y) * axis_dir_y)
                        if unit_id in center_unit_ids:
                            center_advances.append(float(advance))
                            center_interval_total += advance
                        elif unit_id in wing_unit_ids:
                            wing_advances.append(float(advance))
                            wing_interval_total += advance
                    if not center_advances or not wing_advances:
                        series.append(float("nan"))
                        interval_parallel_share_gap = float("nan")
                    else:
                        center_mean = sum(center_advances) / float(len(center_advances))
                        wing_mean = sum(wing_advances) / float(len(wing_advances))
                        series.append(0.5 * float(center_mean - wing_mean))
                        interval_parallel_total = abs(center_interval_total) + abs(wing_interval_total)
                        if interval_parallel_total > 1e-12:
                            interval_parallel_share_gap = float(
                                (center_interval_total - wing_interval_total) / interval_parallel_total
                            )
                        else:
                            interval_parallel_share_gap = 0.0

            front_group_size = max(3, int(math.ceil(len(projected_units) * 0.30)))
            front_group = projected_units[-front_group_size:]
            front_group.sort(key=lambda item: item[1])
            front_split_index = len(front_group) // 2
            front_center_band = front_group[:front_split_index]
            front_wing_band = front_group[front_split_index:]
            if front_center_band and front_wing_band:
                front_center_mean = sum(item[0] for item in front_center_band) / float(len(front_center_band))
                front_wing_mean = sum(item[0] for item in front_wing_band) / float(len(front_wing_band))
                front_curvature_raw = float(front_center_mean - front_wing_mean)
            else:
                front_curvature_raw = float("nan")
            observer_telemetry["front_curvature_index"][fleet_id].append(front_curvature_raw)

            center_parallel_total = 0.0
            wing_parallel_total = 0.0
            for unit_id in current_unit_ids:
                unit_state = state.units.get(unit_id)
                if unit_state is None:
                    continue
                parallel_velocity = (
                    float(unit_state.velocity.x) * axis_dir_x
                    + float(unit_state.velocity.y) * axis_dir_y
                )
                if unit_id in center_unit_ids:
                    center_parallel_total += parallel_velocity
                elif unit_id in wing_unit_ids:
                    wing_parallel_total += parallel_velocity
            total_parallel = abs(center_parallel_total) + abs(wing_parallel_total)
            if total_parallel > 1e-12:
                instantaneous_parallel_share_gap = float(
                    (center_parallel_total - wing_parallel_total) / total_parallel
                )
            else:
                instantaneous_parallel_share_gap = 0.0
            if math.isfinite(interval_parallel_share_gap):
                center_wing_parallel_share_gap = interval_parallel_share_gap
            else:
                center_wing_parallel_share_gap = instantaneous_parallel_share_gap
            observer_telemetry["center_wing_parallel_share"][fleet_id].append(center_wing_parallel_share_gap)

            posture_sign = 0
            if math.isfinite(front_curvature_raw):
                front_curvature_norm = float(front_curvature_raw) / max(float(contact_cfg["separation_radius"]), 1e-12)
                if front_curvature_norm >= 0.10 and center_wing_parallel_share_gap >= 0.05:
                    posture_sign = 1
                elif front_curvature_norm <= -0.10 and center_wing_parallel_share_gap <= -0.05:
                    posture_sign = -1
            prior_sign = int(posture_persistence_state[fleet_id]["sign"])
            prior_length = int(posture_persistence_state[fleet_id]["length"])
            if posture_sign == 0:
                next_length = 0
            elif posture_sign == prior_sign:
                next_length = prior_length + 1
            else:
                next_length = 1
            posture_persistence_state[fleet_id]["sign"] = posture_sign
            posture_persistence_state[fleet_id]["length"] = next_length
            observer_telemetry["posture_persistence_time"][fleet_id].append(float(posture_sign * next_length))

        _capture_position_frame(state)

        any_fleet_eliminated = any(len(fleet.unit_ids) == 0 for fleet in state.fleets.values())
        if steps <= 0:
            if any_fleet_eliminated and elimination_tick is None:
                elimination_tick = state.tick
                post_elimination_stop_tick = min(999, elimination_tick + post_elimination_extra_ticks)
            if post_elimination_stop_tick is not None and state.tick >= post_elimination_stop_tick:
                break
        elif any_fleet_eliminated:
            break

    # 5. Finalize observer outputs.
    if fixture_active:
        return (
            state,
            trajectory,
            alive_trajectory,
            fleet_size_trajectory,
            observer_telemetry,
            combat_telemetry,
            position_frames,
        )

    net_axis_push_interval_ticks = int(observer_telemetry.get("net_axis_push_interval_ticks", 10))
    center_wing_interval_ticks = int(observer_telemetry.get("center_wing_advance_gap_interval_ticks", 10))
    max_unit_speed = 1.0
    if isinstance(state.units, Mapping) and state.units:
        unit_speed_values = []
        for unit_state in state.units.values():
            try:
                unit_speed_values.append(float(getattr(unit_state, "max_speed", 0.0)))
            except (TypeError, ValueError):
                continue
        finite_unit_speed_values = [value for value in unit_speed_values if math.isfinite(value) and value > 0.0]
        if finite_unit_speed_values:
            max_unit_speed = max(finite_unit_speed_values)
    net_axis_push_normalization_scale = float(max_unit_speed) * float(net_axis_push_interval_ticks)
    if net_axis_push_normalization_scale <= 0.0 or not math.isfinite(net_axis_push_normalization_scale):
        net_axis_push_normalization_scale = 1.0
    center_wing_normalization_scale = float(max_unit_speed) * float(center_wing_interval_ticks)
    if center_wing_normalization_scale <= 0.0 or not math.isfinite(center_wing_normalization_scale):
        center_wing_normalization_scale = 1.0
    front_curvature_normalization_scale = max(float(contact_cfg["separation_radius"]), 1e-12)

    def _normalize_series(values: list[float], scale: float) -> list[float]:
        return [
            (float(raw_value) / scale) if math.isfinite(float(raw_value)) else float("nan")
            for raw_value in values
        ]

    centroid_x_a = observer_telemetry.get("centroid_x", {}).get("A", [])
    centroid_y_a = observer_telemetry.get("centroid_y", {}).get("A", [])
    centroid_x_b = observer_telemetry.get("centroid_x", {}).get("B", [])
    centroid_y_b = observer_telemetry.get("centroid_y", {}).get("B", [])
    net_axis_push_series: list[float] = []
    axis_initialized = False
    axis_dir_x = 0.0
    axis_dir_y = 0.0
    for idx in range(len(trajectory.get("A", []))):
        ax = float(centroid_x_a[idx]) if idx < len(centroid_x_a) else float("nan")
        ay = float(centroid_y_a[idx]) if idx < len(centroid_y_a) else float("nan")
        bx = float(centroid_x_b[idx]) if idx < len(centroid_x_b) else float("nan")
        by = float(centroid_y_b[idx]) if idx < len(centroid_y_b) else float("nan")
        valid_pair = all(math.isfinite(value) for value in (ax, ay, bx, by))
        if valid_pair and not axis_initialized:
            dx0 = bx - ax
            dy0 = by - ay
            norm0 = math.sqrt((dx0 * dx0) + (dy0 * dy0))
            if norm0 > 1e-12:
                axis_dir_x = dx0 / norm0
                axis_dir_y = dy0 / norm0
                axis_initialized = True
        if (not axis_initialized) or (not valid_pair) or idx < net_axis_push_interval_ticks:
            net_axis_push_series.append(float("nan"))
            continue
        prev_idx = idx - net_axis_push_interval_ticks
        ax_prev = float(centroid_x_a[prev_idx]) if prev_idx < len(centroid_x_a) else float("nan")
        ay_prev = float(centroid_y_a[prev_idx]) if prev_idx < len(centroid_y_a) else float("nan")
        bx_prev = float(centroid_x_b[prev_idx]) if prev_idx < len(centroid_x_b) else float("nan")
        by_prev = float(centroid_y_b[prev_idx]) if prev_idx < len(centroid_y_b) else float("nan")
        if not all(math.isfinite(value) for value in (ax_prev, ay_prev, bx_prev, by_prev)):
            net_axis_push_series.append(float("nan"))
            continue
        advance_a = ((ax - ax_prev) * axis_dir_x) + ((ay - ay_prev) * axis_dir_y)
        advance_b = ((bx_prev - bx) * axis_dir_x) + ((by_prev - by) * axis_dir_y)
        net_axis_push_value = 0.5 * float(advance_a - advance_b)
        net_axis_push_series.append(float(net_axis_push_value / net_axis_push_normalization_scale))
    observer_telemetry["net_axis_push"]["net"] = net_axis_push_series
    observer_telemetry["net_axis_push_normalization_scale"] = net_axis_push_normalization_scale
    for fleet_id in fleet_ids:
        observer_telemetry["center_wing_advance_gap"][fleet_id] = _normalize_series(
            observer_telemetry["center_wing_advance_gap"][fleet_id],
            center_wing_normalization_scale,
        )
        observer_telemetry["front_curvature_index"][fleet_id] = _normalize_series(
            observer_telemetry["front_curvature_index"][fleet_id],
            front_curvature_normalization_scale,
        )
    observer_telemetry["center_wing_advance_gap_normalization_scale"] = center_wing_normalization_scale
    observer_telemetry["front_curvature_index_normalization_scale"] = front_curvature_normalization_scale
    fire_efficiency_series_a, fire_efficiency_series_b = _compute_fire_efficiency_series(
        fleet_size_trajectory.get("A", []),
        fleet_size_trajectory.get("B", []),
        alive_trajectory.get("A", []),
        alive_trajectory.get("B", []),
        per_unit_damage=float(contact_cfg.get("damage_per_tick", 0.0)),
    )
    observer_telemetry["fire_efficiency"]["A"] = fire_efficiency_series_a
    observer_telemetry["fire_efficiency"]["B"] = fire_efficiency_series_b

    return (
        state,
        trajectory,
        alive_trajectory,
        fleet_size_trajectory,
        observer_telemetry,
        combat_telemetry,
        position_frames,
    )
