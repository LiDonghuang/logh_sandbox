import math
import time
from collections.abc import Mapping, Sequence
from dataclasses import replace
from typing import Any

from runtime.engine_skeleton import EngineTickSkeleton
from runtime.runtime_v0_1 import BattleState, UnitState, Vec2

from test_run.test_run_telemetry import (
    compute_bridge_metrics_per_side,
    compute_collapse_v2_shadow_telemetry,
    compute_formation_snapshot_metrics,
    compute_hostile_intermix_metrics,
    extract_runtime_debug_payload,
)


DEFAULT_FRAME_STRIDE = 1
BASELINE_V3_CONNECT_RADIUS_MULTIPLIER = 1.1
BASELINE_V3_R_REF_RADIUS_MULTIPLIER = 1.0
V3A_EXPERIMENT_BASE = "base"
V3A_EXPERIMENT_PRECONTACT_CENTROID_PROBE = "exp_precontact_centroid_probe"
V3A_EXPERIMENT_LABELS = {
    V3A_EXPERIMENT_BASE,
    V3A_EXPERIMENT_PRECONTACT_CENTROID_PROBE,
}
HOSTILE_CONTACT_IMPEDANCE_MODE_OFF = "off"
HOSTILE_CONTACT_IMPEDANCE_MODE_HYBRID_V2 = "hybrid_v2"
HOSTILE_CONTACT_IMPEDANCE_MODE_INTENT_UNIFIED_SPACING_V1 = "intent_unified_spacing_v1"
HOSTILE_CONTACT_IMPEDANCE_MODE_LABELS = {
    HOSTILE_CONTACT_IMPEDANCE_MODE_OFF,
    HOSTILE_CONTACT_IMPEDANCE_MODE_HYBRID_V2,
    HOSTILE_CONTACT_IMPEDANCE_MODE_INTENT_UNIFIED_SPACING_V1,
}
HOSTILE_CONTACT_IMPEDANCE_MODE_DEFAULT = "off"
HOSTILE_CONTACT_IMPEDANCE_V2_RADIUS_MULTIPLIER_DEFAULT = 1.50
HOSTILE_CONTACT_IMPEDANCE_V2_REPULSION_MAX_DISP_RATIO_DEFAULT = 0.20
HOSTILE_CONTACT_IMPEDANCE_V2_FORWARD_DAMPING_STRENGTH_DEFAULT = 0.50
HOSTILE_INTENT_UNIFIED_SPACING_SCALE_DEFAULT = 1.00
HOSTILE_INTENT_UNIFIED_SPACING_STRENGTH_DEFAULT = 1.00
BRIDGE_THETA_SPLIT_DEFAULT = 1.715
BRIDGE_THETA_ENV_DEFAULT = 0.583
BRIDGE_SUSTAIN_TICKS_DEFAULT = 20
COLLAPSE_V2_SHADOW_ATTRITION_WINDOW_DEFAULT = 20
COLLAPSE_V2_SHADOW_SUSTAIN_TICKS_DEFAULT = 10
COLLAPSE_V2_SHADOW_MIN_CONDITIONS_DEFAULT = 2
COLLAPSE_V2_SHADOW_THETA_CONN_DEFAULT = 0.10
COLLAPSE_V2_SHADOW_THETA_COH_DEFAULT = 0.98
COLLAPSE_V2_SHADOW_THETA_FORCE_DEFAULT = 0.95
COLLAPSE_V2_SHADOW_THETA_ATTR_DEFAULT = 0.10

SimulationExecutionConfig = dict
SimulationMovementConfig = dict
SimulationContactConfig = dict
SimulationBoundaryConfig = dict
SimulationRuntimeConfig = dict
SimulationObserverConfig = dict
FIXTURE_MODE_BATTLE = "battle"
FIXTURE_MODE_NEUTRAL_TRANSIT_V1 = "neutral_transit_v1"
FIXTURE_LINEAR_ARRIVAL_GAIN_MIN_STOP_RADIUS = 1e-12
FIXTURE_MODE_LABELS = {
    FIXTURE_MODE_BATTLE,
    FIXTURE_MODE_NEUTRAL_TRANSIT_V1,
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
V4A_SOFT_MORPHOLOGY_BAND_COUNT = 3
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


def _assign_soft_morphology_band_identity(
    offsets_by_id: Mapping[str, tuple[float, float]],
) -> dict[str, tuple[int, int]]:
    records = [
        (str(unit_id), float(offset_local[0]), float(offset_local[1]))
        for unit_id, offset_local in offsets_by_id.items()
    ]
    if not records:
        return {}
    band_identity_by_id: dict[str, list[int]] = {}
    sorted_forward = sorted(records, key=lambda item: (item[1], item[2], item[0]))
    sorted_lateral = sorted(records, key=lambda item: (item[2], item[1], item[0]))
    total_count = len(records)
    for index, (record_id, _, _) in enumerate(sorted_forward):
        band_identity_by_id.setdefault(str(record_id), [1, 1])[0] = min(
            V4A_SOFT_MORPHOLOGY_BAND_COUNT - 1,
            int((index * V4A_SOFT_MORPHOLOGY_BAND_COUNT) / float(total_count)),
        )
    for index, (record_id, _, _) in enumerate(sorted_lateral):
        band_identity_by_id.setdefault(str(record_id), [1, 1])[1] = min(
            V4A_SOFT_MORPHOLOGY_BAND_COUNT - 1,
            int((index * V4A_SOFT_MORPHOLOGY_BAND_COUNT) / float(total_count)),
        )
    return {
        str(record_id): (int(bands[0]), int(bands[1]))
        for record_id, bands in band_identity_by_id.items()
    }


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
            "neutral_transit_v1 execution_cfg['fixture']['objective_contract_3d'] must be a mapping"
        )
    if "transit_axis_hint_xyz" in contract_cfg:
        raise ValueError(
            "neutral_transit_v1 first implementation must not set "
            "execution_cfg['fixture']['objective_contract_3d']['transit_axis_hint_xyz']"
        )
    anchor_point_xyz = contract_cfg.get("anchor_point_xyz")
    if (
        not isinstance(anchor_point_xyz, Sequence)
        or isinstance(anchor_point_xyz, (str, bytes))
        or len(anchor_point_xyz) != 3
    ):
        raise TypeError(
            "neutral_transit_v1 execution_cfg['fixture']['objective_contract_3d']['anchor_point_xyz'] "
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
            "neutral_transit_v1 execution_cfg['fixture']['objective_contract_3d']['source_owner'] "
            f"must be {OBJECTIVE_CONTRACT_3D_SOURCE_OWNER_FIXTURE!r}, got {normalized_contract['source_owner']!r}"
        )
    if normalized_contract["objective_mode"] != OBJECTIVE_CONTRACT_3D_MODE_POINT_ANCHOR:
        raise ValueError(
            "neutral_transit_v1 execution_cfg['fixture']['objective_contract_3d']['objective_mode'] "
            f"must be {OBJECTIVE_CONTRACT_3D_MODE_POINT_ANCHOR!r}, got {normalized_contract['objective_mode']!r}"
        )
    if normalized_contract["no_enemy_semantics"] != OBJECTIVE_CONTRACT_3D_NO_ENEMY_SEMANTICS:
        raise ValueError(
            "neutral_transit_v1 execution_cfg['fixture']['objective_contract_3d']['no_enemy_semantics'] "
            f"must be {OBJECTIVE_CONTRACT_3D_NO_ENEMY_SEMANTICS!r}, got {normalized_contract['no_enemy_semantics']!r}"
        )
    return normalized_contract, (
        float(normalized_contract["anchor_point_xyz"][0]),
        float(normalized_contract["anchor_point_xyz"][1]),
    )


class TestModeEngineTickSkeleton(EngineTickSkeleton):
    @staticmethod
    def _compute_position_centroid(units: Sequence[UnitState]) -> tuple[float, float]:
        if not units:
            return 0.0, 0.0
        inv_n = 1.0 / float(len(units))
        return (
            sum(unit.position.x for unit in units) * inv_n,
            sum(unit.position.y for unit in units) * inv_n,
        )

    @staticmethod
    def _normalize_direction(dx: float, dy: float) -> tuple[tuple[float, float], float]:
        norm = math.sqrt((dx * dx) + (dy * dy))
        if norm > 0.0:
            return (dx / norm, dy / norm), 1.0
        return (0.0, 0.0), 0.0

    @staticmethod
    def _relax_direction(
        current_hat: tuple[float, float],
        desired_hat: tuple[float, float],
        relaxation: float,
    ) -> tuple[float, float]:
        relaxed_x = ((1.0 - relaxation) * float(current_hat[0])) + (relaxation * float(desired_hat[0]))
        relaxed_y = ((1.0 - relaxation) * float(current_hat[1])) + (relaxation * float(desired_hat[1]))
        normalized_hat, normalized_norm = TestModeEngineTickSkeleton._normalize_direction(relaxed_x, relaxed_y)
        if normalized_norm <= 0.0:
            return current_hat
        return normalized_hat

    @staticmethod
    def _resolve_v4a_reference_surface(
        state: BattleState,
        *,
        fleet_id: str,
        bundle: Mapping[str, Any],
    ) -> tuple[dict[str, tuple[float, float]], tuple[float, float]]:
        fallback_forward = bundle.get("initial_forward_hat_xy", (1.0, 0.0))
        fallback_forward_x = float(fallback_forward[0]) if len(fallback_forward) >= 1 else 1.0
        fallback_forward_y = float(fallback_forward[1]) if len(fallback_forward) >= 2 else 0.0
        resolved_forward_hat, resolved_norm = TestModeEngineTickSkeleton._normalize_direction(
            fallback_forward_x,
            fallback_forward_y,
        )
        if resolved_norm <= 0.0:
            resolved_forward_hat = (1.0, 0.0)

        target_direction = state.last_target_direction.get(fleet_id, resolved_forward_hat)
        target_x = float(target_direction[0]) if len(target_direction) >= 1 else 0.0
        target_y = float(target_direction[1]) if len(target_direction) >= 2 else 0.0
        target_forward_hat, target_norm = TestModeEngineTickSkeleton._normalize_direction(target_x, target_y)
        if target_norm > 0.0:
            resolved_forward_hat = target_forward_hat
        secondary_hat = (-resolved_forward_hat[1], resolved_forward_hat[0])

        fleet = state.fleets.get(fleet_id)
        if fleet is None:
            return {}, resolved_forward_hat
        alive_units = [
            state.units[unit_id]
            for unit_id in fleet.unit_ids
            if unit_id in state.units and float(state.units[unit_id].hit_points) > 0.0
        ]
        if not alive_units:
            return {}, resolved_forward_hat

        centroid_x, centroid_y = TestModeEngineTickSkeleton._compute_position_centroid(alive_units)
        current_axis = bundle.get("morphology_axis_current_xy", resolved_forward_hat)
        if not isinstance(current_axis, Sequence) or len(current_axis) < 2:
            current_axis = resolved_forward_hat
        current_axis_hat, current_axis_norm = TestModeEngineTickSkeleton._normalize_direction(
            float(current_axis[0]) if len(current_axis) >= 1 else float(resolved_forward_hat[0]),
            float(current_axis[1]) if len(current_axis) >= 2 else float(resolved_forward_hat[1]),
        )
        if current_axis_norm <= 0.0:
            current_axis_hat = resolved_forward_hat
        # Current local read: terminal/hold morphology latching over-regularizes arrival
        # into a visibly discrete end-state. Keep arrival detection, but disable the
        # harness-side terminal/hold reshape path for now.
        terminal_active = False
        hold_active = False
        hold_axis = bundle.get("formation_hold_axis_xy", current_axis_hat)
        if not isinstance(hold_axis, Sequence) or len(hold_axis) < 2:
            hold_axis = current_axis_hat
        hold_axis_hat, hold_axis_norm = TestModeEngineTickSkeleton._normalize_direction(
            float(hold_axis[0]) if len(hold_axis) >= 1 else float(current_axis_hat[0]),
            float(hold_axis[1]) if len(hold_axis) >= 2 else float(current_axis_hat[1]),
        )
        if hold_axis_norm <= 0.0:
            hold_axis_hat = current_axis_hat
        terminal_axis = bundle.get("formation_terminal_axis_xy", current_axis_hat)
        if not isinstance(terminal_axis, Sequence) or len(terminal_axis) < 2:
            terminal_axis = current_axis_hat
        terminal_axis_hat, terminal_axis_norm = TestModeEngineTickSkeleton._normalize_direction(
            float(terminal_axis[0]) if len(terminal_axis) >= 1 else float(current_axis_hat[0]),
            float(terminal_axis[1]) if len(terminal_axis) >= 2 else float(current_axis_hat[1]),
        )
        if terminal_axis_norm <= 0.0:
            terminal_axis_hat = current_axis_hat
        desired_axis_hat = current_axis_hat
        if target_norm > 0.0:
            desired_axis_hat = target_forward_hat
        effective_fire_axis = bundle.get("effective_fire_axis_xy", desired_axis_hat)
        if not isinstance(effective_fire_axis, Sequence) or len(effective_fire_axis) < 2:
            effective_fire_axis = desired_axis_hat
        effective_fire_axis_hat, effective_fire_axis_norm = TestModeEngineTickSkeleton._normalize_direction(
            float(effective_fire_axis[0]) if len(effective_fire_axis) >= 1 else float(desired_axis_hat[0]),
            float(effective_fire_axis[1]) if len(effective_fire_axis) >= 2 else float(desired_axis_hat[1]),
        )
        if effective_fire_axis_norm <= 0.0:
            effective_fire_axis_hat = desired_axis_hat
        if not hold_active and not terminal_active:
            current_axis_hat = TestModeEngineTickSkeleton._relax_direction(
                current_axis_hat,
                desired_axis_hat,
                V4A_MORPHOLOGY_AXIS_RELAXATION_DEFAULT,
            )
        objective_point_xy = bundle.get("objective_point_xy")
        hold_stop_radius = float(bundle.get("hold_stop_radius", 0.0))
        within_hold_radius = False
        if isinstance(objective_point_xy, Sequence) and len(objective_point_xy) >= 2 and hold_stop_radius > 0.0:
            objective_dx = float(objective_point_xy[0]) - float(centroid_x)
            objective_dy = float(objective_point_xy[1]) - float(centroid_y)
            objective_distance = math.sqrt((objective_dx * objective_dx) + (objective_dy * objective_dy))
            within_hold_radius = objective_distance <= hold_stop_radius
        if hold_active:
            current_axis_hat = hold_axis_hat
        elif terminal_active:
            current_axis_hat = terminal_axis_hat
        bundle["morphology_axis_current_xy"] = current_axis_hat
        bundle["front_axis_delta_deg"] = float(
            _direction_delta_degrees(current_axis_hat, effective_fire_axis_hat)
        )
        resolved_forward_hat = current_axis_hat
        secondary_hat = (-resolved_forward_hat[1], resolved_forward_hat[0])
        current_center = bundle.get("morphology_center_current_xy", (centroid_x, centroid_y))
        if not isinstance(current_center, Sequence) or len(current_center) < 2:
            current_center = (centroid_x, centroid_y)
        current_center_x = float(current_center[0]) if len(current_center) >= 1 else float(centroid_x)
        current_center_y = float(current_center[1]) if len(current_center) >= 2 else float(centroid_y)
        hold_center = bundle.get("formation_hold_center_xy", (current_center_x, current_center_y))
        if not isinstance(hold_center, Sequence) or len(hold_center) < 2:
            hold_center = (current_center_x, current_center_y)
        hold_center_x = float(hold_center[0]) if len(hold_center) >= 1 else float(current_center_x)
        hold_center_y = float(hold_center[1]) if len(hold_center) >= 2 else float(current_center_y)
        terminal_center = bundle.get("formation_terminal_center_xy", (current_center_x, current_center_y))
        if not isinstance(terminal_center, Sequence) or len(terminal_center) < 2:
            terminal_center = (current_center_x, current_center_y)
        terminal_center_x = float(terminal_center[0]) if len(terminal_center) >= 1 else float(current_center_x)
        terminal_center_y = float(terminal_center[1]) if len(terminal_center) >= 2 else float(current_center_y)
        current_offsets_local: dict[str, tuple[float, float]] = {}
        for unit in alive_units:
            rel_x = float(unit.position.x) - centroid_x
            rel_y = float(unit.position.y) - centroid_y
            forward_offset = (rel_x * resolved_forward_hat[0]) + (rel_y * resolved_forward_hat[1])
            lateral_offset = (rel_x * secondary_hat[0]) + (rel_y * secondary_hat[1])
            current_offsets_local[str(unit.unit_id)] = (float(forward_offset), float(lateral_offset))

        reference_surface_mode = str(
            bundle.get("reference_surface_mode", V4A_REFERENCE_SURFACE_MODE_RIGID_SLOTS)
        ).strip().lower()
        if reference_surface_mode != V4A_REFERENCE_SURFACE_MODE_SOFT_MORPHOLOGY_V1:
            rigid_offsets = bundle.get("expected_slot_offsets_local", {})
            if not isinstance(rigid_offsets, Mapping):
                rigid_offsets = {}
            return (
                {
                    str(unit_id): tuple(rigid_offsets.get(str(unit_id), current_offsets_local[str(unit_id)]))
                    for unit_id in current_offsets_local
                },
                resolved_forward_hat,
            )

        initial_alive_count = max(1, int(bundle.get("initial_alive_count", len(current_offsets_local))))
        alive_ratio = max(0.0, min(1.0, float(len(current_offsets_local)) / float(initial_alive_count)))
        target_scale = math.sqrt(alive_ratio)
        forward_extent_initial = max(1e-9, float(bundle.get("forward_extent_initial", 0.0)))
        lateral_extent_initial = max(1e-9, float(bundle.get("lateral_extent_initial", 0.0)))
        forward_extent_base = max(1e-9, float(bundle.get("forward_extent_base", forward_extent_initial)))
        lateral_extent_base = max(1e-9, float(bundle.get("lateral_extent_base", lateral_extent_initial)))
        forward_extent_target = forward_extent_base * target_scale
        lateral_extent_target = lateral_extent_base * target_scale
        actual_forward_extent = max(
            1e-9,
            max((abs(float(offset_local[0])) for offset_local in current_offsets_local.values()), default=0.0),
        )
        actual_lateral_extent = max(
            1e-9,
            max((abs(float(offset_local[1])) for offset_local in current_offsets_local.values()), default=0.0),
        )
        relaxation = max(
            1e-6,
            min(1.0, float(bundle.get("soft_morphology_relaxation", V4A_SOFT_MORPHOLOGY_RELAXATION_DEFAULT))),
        )
        if hold_active:
            current_center_x = hold_center_x
            current_center_y = hold_center_y
        elif terminal_active:
            current_center_x += (float(terminal_center_x) - float(current_center_x)) * relaxation
            current_center_y += (float(terminal_center_y) - float(current_center_y)) * relaxation
        else:
            current_center_x = float(centroid_x)
            current_center_y = float(centroid_y)
        bundle["morphology_center_current_xy"] = (float(current_center_x), float(current_center_y))
        hold_forward_extent = bundle.get("formation_hold_forward_extent", None)
        hold_lateral_extent = bundle.get("formation_hold_lateral_extent", None)
        hold_center_wing_differential = bundle.get("formation_hold_center_wing_differential", None)
        if hold_active and hold_forward_extent is not None and hold_lateral_extent is not None:
            forward_extent_current = max(1e-9, float(hold_forward_extent))
            lateral_extent_current = max(1e-9, float(hold_lateral_extent))
            forward_extent_target = forward_extent_current
            lateral_extent_target = lateral_extent_current
        else:
            forward_extent_current = float(bundle.get("forward_extent_current", forward_extent_initial))
            lateral_extent_current = float(bundle.get("lateral_extent_current", lateral_extent_initial))
            forward_extent_current += (forward_extent_target - forward_extent_current) * relaxation
            lateral_extent_current += (lateral_extent_target - lateral_extent_current) * relaxation
        center_wing_differential_target = float(
            bundle.get("center_wing_differential_target", V4A_CENTER_WING_DIFFERENTIAL_DEFAULT)
        )
        if hold_active and hold_center_wing_differential is not None:
            center_wing_differential_current = float(hold_center_wing_differential)
            center_wing_differential_target = center_wing_differential_current
        else:
            center_wing_differential_current = float(
                bundle.get("center_wing_differential_current", V4A_CENTER_WING_DIFFERENTIAL_DEFAULT)
            )
            center_wing_differential_current += (
                center_wing_differential_target - center_wing_differential_current
            ) * relaxation
        bundle["forward_extent_target"] = float(forward_extent_target)
        bundle["lateral_extent_target"] = float(lateral_extent_target)
        bundle["forward_extent_current"] = float(forward_extent_current)
        bundle["lateral_extent_current"] = float(lateral_extent_current)
        bundle["center_wing_differential_target"] = float(center_wing_differential_target)
        bundle["center_wing_differential_current"] = float(center_wing_differential_current)
        bundle["actual_forward_extent"] = float(actual_forward_extent)
        bundle["actual_lateral_extent"] = float(actual_lateral_extent)
        forward_shape_error = abs(actual_forward_extent - forward_extent_target) / max(1e-9, forward_extent_base)
        lateral_shape_error = abs(actual_lateral_extent - lateral_extent_target) / max(1e-9, lateral_extent_base)
        shape_error_current = min(1.0, max(0.0, max(forward_shape_error, lateral_shape_error)))
        bundle["shape_error_current"] = float(shape_error_current)
        bundle["hold_within_stop_radius"] = bool(within_hold_radius)
        bundle["formation_terminal_active"] = False
        bundle["formation_hold_active"] = False
        bundle["formation_terminal_latched_tick"] = None
        bundle["formation_hold_latched_tick"] = None
        bundle["formation_terminal_axis_xy"] = None
        bundle["formation_terminal_center_xy"] = None
        bundle["formation_hold_axis_xy"] = None
        bundle["formation_hold_center_xy"] = None
        bundle["formation_hold_forward_extent"] = None
        bundle["formation_hold_lateral_extent"] = None
        bundle["formation_hold_center_wing_differential"] = None
        current_material_forward_phase_by_unit = bundle.get("current_material_forward_phase_by_unit", {})
        if not isinstance(current_material_forward_phase_by_unit, Mapping):
            current_material_forward_phase_by_unit = {}
        current_material_lateral_phase_by_unit = bundle.get("current_material_lateral_phase_by_unit", {})
        if not isinstance(current_material_lateral_phase_by_unit, Mapping):
            current_material_lateral_phase_by_unit = {}
        target_material_forward_phase_by_unit = bundle.get("target_material_forward_phase_by_unit", {})
        if not isinstance(target_material_forward_phase_by_unit, Mapping):
            target_material_forward_phase_by_unit = {}
        target_material_lateral_phase_by_unit = bundle.get("target_material_lateral_phase_by_unit", {})
        if not isinstance(target_material_lateral_phase_by_unit, Mapping):
            target_material_lateral_phase_by_unit = {}
        if not hold_active:
            updated_forward_phases: dict[str, float] = {}
            updated_lateral_phases: dict[str, float] = {}
            for unit_id in current_offsets_local:
                current_forward_phase = current_material_forward_phase_by_unit.get(str(unit_id), 0.0)
                if not isinstance(current_forward_phase, (int, float)):
                    current_forward_phase = 0.0
                current_lateral_phase = current_material_lateral_phase_by_unit.get(str(unit_id), 0.0)
                if not isinstance(current_lateral_phase, (int, float)):
                    current_lateral_phase = 0.0
                target_forward_phase = target_material_forward_phase_by_unit.get(str(unit_id), current_forward_phase)
                if not isinstance(target_forward_phase, (int, float)):
                    target_forward_phase = current_forward_phase
                target_lateral_phase = target_material_lateral_phase_by_unit.get(str(unit_id), current_lateral_phase)
                if not isinstance(target_lateral_phase, (int, float)):
                    target_lateral_phase = current_lateral_phase
                next_forward_phase = float(current_forward_phase) + (
                    (float(target_forward_phase) - float(current_forward_phase)) * relaxation
                )
                next_lateral_phase = float(current_lateral_phase) + (
                    (float(target_lateral_phase) - float(current_lateral_phase)) * relaxation
                )
                updated_forward_phases[str(unit_id)] = max(-1.0, min(1.0, float(next_forward_phase)))
                updated_lateral_phases[str(unit_id)] = max(-1.0, min(1.0, float(next_lateral_phase)))
            bundle["current_material_forward_phase_by_unit"] = dict(updated_forward_phases)
            bundle["current_material_lateral_phase_by_unit"] = dict(updated_lateral_phases)
            current_material_forward_phase_by_unit = updated_forward_phases
            current_material_lateral_phase_by_unit = updated_lateral_phases
        expected_offsets_local: dict[str, tuple[float, float]] = {}
        center_delta_x = float(current_center_x) - float(centroid_x)
        center_delta_y = float(current_center_y) - float(centroid_y)
        center_delta_forward = (
            (center_delta_x * resolved_forward_hat[0]) + (center_delta_y * resolved_forward_hat[1])
        )
        center_delta_lateral = (
            (center_delta_x * secondary_hat[0]) + (center_delta_y * secondary_hat[1])
        )
        forward_transport_deltas_local: list[float] = []
        phase_forward_deltas_local: list[float] = []
        forward_transport_alignment_count = 0
        forward_transport_alignment_matches = 0
        for unit_id, (forward_offset, lateral_offset) in current_offsets_local.items():
            material_forward = current_material_forward_phase_by_unit.get(str(unit_id))
            if not isinstance(material_forward, (int, float)):
                material_forward = float(forward_offset) / max(1e-9, forward_extent_current)
            material_lateral = current_material_lateral_phase_by_unit.get(str(unit_id))
            if not isinstance(material_lateral, (int, float)):
                material_lateral = float(lateral_offset) / max(1e-9, lateral_extent_current)
            material_forward = max(-1.0, min(1.0, float(material_forward)))
            material_lateral = max(-1.0, min(1.0, float(material_lateral)))
            center_wing_profile = 1.0 - (2.0 * abs(material_lateral))
            target_forward_offset = (
                material_forward * float(forward_extent_current)
                + (center_wing_profile * float(center_wing_differential_current))
            )
            target_lateral_offset = material_lateral * float(lateral_extent_current)
            expected_offsets_local[str(unit_id)] = (
                float(target_forward_offset + center_delta_forward),
                float(target_lateral_offset + center_delta_lateral),
            )
            forward_transport_delta = float(target_forward_offset + center_delta_forward - float(forward_offset))
            phase_forward_delta = float(target_forward_offset - float(forward_offset))
            forward_transport_deltas_local.append(forward_transport_delta)
            phase_forward_deltas_local.append(phase_forward_delta)
            if abs(float(forward_offset)) > 1e-9 and abs(forward_transport_delta) > 1e-9:
                forward_transport_alignment_count += 1
                if float(forward_offset) * float(forward_transport_delta) < 0.0:
                    forward_transport_alignment_matches += 1
        if forward_transport_deltas_local:
            bundle["center_delta_forward"] = float(center_delta_forward)
            bundle["forward_transport_delta_mean"] = (
                sum(forward_transport_deltas_local) / float(len(forward_transport_deltas_local))
            )
            bundle["forward_transport_negative_fraction"] = (
                sum(1 for value in forward_transport_deltas_local if value < -1e-9)
                / float(len(forward_transport_deltas_local))
            )
            bundle["forward_transport_positive_fraction"] = (
                sum(1 for value in forward_transport_deltas_local if value > 1e-9)
                / float(len(forward_transport_deltas_local))
            )
        if phase_forward_deltas_local:
            bundle["phase_forward_delta_mean"] = (
                sum(phase_forward_deltas_local) / float(len(phase_forward_deltas_local))
            )
        if forward_transport_alignment_count > 0:
            bundle["forward_transport_alignment"] = (
                float(forward_transport_alignment_matches) / float(forward_transport_alignment_count)
            )

        return expected_offsets_local, resolved_forward_hat

    def _evaluate_target_with_fixture_objective(self, state: BattleState) -> BattleState | None:
        fixture_cfg = getattr(self, "TEST_RUN_FIXTURE_CFG", None)
        if not isinstance(fixture_cfg, Mapping):
            return None
        active_mode = str(fixture_cfg.get("active_mode", FIXTURE_MODE_BATTLE)).strip().lower()
        if active_mode != FIXTURE_MODE_NEUTRAL_TRANSIT_V1:
            return None
        if len(state.fleets) != 1:
            return None

        fleet_id, fleet = next(iter(state.fleets.items()))
        objective_contract_3d = fixture_cfg.get("objective_contract_3d")
        if not isinstance(objective_contract_3d, Mapping):
            raise TypeError("neutral_transit_v1 engine fixture config requires objective_contract_3d mapping")
        anchor_point_xyz = objective_contract_3d.get("anchor_point_xyz")
        objective_point_xy = (
            float(anchor_point_xyz[0]),
            float(anchor_point_xyz[1]),
        )
        own_units = [
            state.units[uid]
            for uid in fleet.unit_ids
            if uid in state.units and float(state.units[uid].hit_points) > 0.0
        ]
        enemy_units = [
            unit
            for unit in state.units.values()
            if unit.fleet_id != fleet_id and float(unit.hit_points) > 0.0
        ]
        if enemy_units:
            return None
        fixture_bundle = getattr(self, "TEST_RUN_FIXTURE_REFERENCE_BUNDLE", None)
        terminal_hold_active = (
            isinstance(fixture_bundle, Mapping)
            and (
                bool(fixture_bundle.get("formation_terminal_active", False))
                or bool(fixture_bundle.get("formation_hold_active", False))
            )
        )
        if terminal_hold_active:
            return replace(
                state,
                last_target_direction={fleet_id: (0.0, 0.0)},
                last_engagement_intensity={fleet_id: 0.0},
            )
        if not own_units:
            direction = (0.0, 0.0)
            intensity = 0.0
        else:
            centroid_x, centroid_y = self._compute_position_centroid(own_units)
            stop_radius = float(fixture_cfg.get("stop_radius", 0.0))
            if stop_radius > 0.0:
                distance_to_objective = math.sqrt(
                    ((float(objective_point_xy[0]) - centroid_x) ** 2)
                    + ((float(objective_point_xy[1]) - centroid_y) ** 2)
                )
            normalized_direction, _ = self._normalize_direction(
                float(objective_point_xy[0]) - centroid_x,
                float(objective_point_xy[1]) - centroid_y,
            )
            if stop_radius > FIXTURE_LINEAR_ARRIVAL_GAIN_MIN_STOP_RADIUS:
                arrival_gain = max(0.0, min(1.0, distance_to_objective / stop_radius))
            else:
                arrival_gain = 1.0
            direction = (
                float(normalized_direction[0]) * arrival_gain,
                float(normalized_direction[1]) * arrival_gain,
            )
            intensity = float(arrival_gain)
        return replace(
            state,
            last_target_direction={fleet_id: direction},
            last_engagement_intensity={fleet_id: intensity},
        )

    def _evaluate_target_with_pre_tl_substrate(self, state: BattleState) -> BattleState:
        last_target_direction = {}
        last_engagement_intensity = {}

        for fleet_id, fleet in state.fleets.items():
            own_units = [
                state.units[uid]
                for uid in fleet.unit_ids
                if uid in state.units and float(state.units[uid].hit_points) > 0.0
            ]
            enemy_units = [
                unit
                for unit in state.units.values()
                if unit.fleet_id != fleet_id and float(unit.hit_points) > 0.0
            ]

            if not own_units or not enemy_units:
                last_target_direction[fleet_id] = (0.0, 0.0)
                last_engagement_intensity[fleet_id] = 0.0
                continue

            centroid_x, centroid_y = self._compute_position_centroid(own_units)

            def _distance_sq(unit: UnitState) -> float:
                dx = unit.position.x - centroid_x
                dy = unit.position.y - centroid_y
                return (dx * dx) + (dy * dy)

            battle_restore_bundles = getattr(self, "TEST_RUN_BATTLE_RESTORE_BUNDLES_BY_FLEET", None)
            battle_bundle = (
                battle_restore_bundles.get(str(fleet_id))
                if isinstance(battle_restore_bundles, Mapping)
                else None
            )
            reference_units: list[UnitState]
            if isinstance(battle_bundle, Mapping):
                # v4a far-field battle target now reads as global enemy relation + d*.
                reference_units = list(enemy_units)
                ref_x, ref_y = self._compute_position_centroid(reference_units)
            else:
                sorted_enemy_units = sorted(enemy_units, key=_distance_sq)
                reference_units = sorted_enemy_units[: min(5, len(sorted_enemy_units))]
                ref_x, ref_y = self._compute_position_centroid(reference_units)

            ref_dx = float(ref_x) - float(centroid_x)
            ref_dy = float(ref_y) - float(centroid_y)
            reference_direction_hat, _ = self._normalize_direction(ref_dx, ref_dy)
            reference_distance = math.sqrt((ref_dx * ref_dx) + (ref_dy * ref_dy))
            if isinstance(battle_bundle, Mapping):
                engaged_attack_vectors: list[tuple[float, float]] = []
                for unit in own_units:
                    engaged_target_id = (
                        str(unit.engaged_target_id).strip()
                        if unit.engaged_target_id is not None
                        else ""
                    )
                    if not bool(unit.engaged) or not engaged_target_id:
                        continue
                    target_unit = state.units.get(engaged_target_id)
                    if target_unit is None or float(target_unit.hit_points) <= 0.0:
                        continue
                    attack_hat_xy, attack_norm = self._normalize_direction(
                        float(target_unit.position.x) - float(unit.position.x),
                        float(target_unit.position.y) - float(unit.position.y),
                    )
                    if attack_norm > 0.0:
                        engaged_attack_vectors.append(
                            (float(attack_hat_xy[0]), float(attack_hat_xy[1]))
                        )
                engaged_fraction = (
                    float(len(engaged_attack_vectors)) / float(max(1, len(own_units)))
                )
                attack_sum_x = sum(float(vector[0]) for vector in engaged_attack_vectors)
                attack_sum_y = sum(float(vector[1]) for vector in engaged_attack_vectors)
                attack_sum_norm = math.sqrt((attack_sum_x * attack_sum_x) + (attack_sum_y * attack_sum_y))
                effective_fire_axis_raw_hat = reference_direction_hat
                fire_axis_coherence_raw = 0.0
                if engaged_attack_vectors and attack_sum_norm > 1e-12:
                    effective_fire_axis_raw_hat = (
                        float(attack_sum_x) / float(attack_sum_norm),
                        float(attack_sum_y) / float(attack_sum_norm),
                    )
                    fire_axis_coherence_raw = min(
                        1.0,
                        float(attack_sum_norm) / float(len(engaged_attack_vectors)),
                    )
                engagement_geometry_active_raw = _clamp01(
                    float(engaged_fraction) / V4A_ENGAGEMENT_GEOMETRY_FULL_ENGAGED_FRACTION_DEFAULT
                )
                prior_engagement_geometry_active = float(
                    battle_bundle.get(
                        "engagement_geometry_active_current",
                        battle_bundle.get("engagement_geometry_active", 0.0),
                    )
                )
                engagement_geometry_active = _relax_scalar(
                    prior_engagement_geometry_active,
                    engagement_geometry_active_raw,
                    V4A_ENGAGEMENT_GEOMETRY_RELAXATION_DEFAULT,
                )
                prior_fire_axis = battle_bundle.get(
                    "effective_fire_axis_current_xy",
                    battle_bundle.get("effective_fire_axis_xy", reference_direction_hat),
                )
                if not isinstance(prior_fire_axis, Sequence) or len(prior_fire_axis) < 2:
                    prior_fire_axis = reference_direction_hat
                prior_fire_axis_hat, prior_fire_axis_norm = self._normalize_direction(
                    float(prior_fire_axis[0]) if len(prior_fire_axis) >= 1 else float(reference_direction_hat[0]),
                    float(prior_fire_axis[1]) if len(prior_fire_axis) >= 2 else float(reference_direction_hat[1]),
                )
                if prior_fire_axis_norm <= 0.0:
                    prior_fire_axis_hat = reference_direction_hat
                effective_fire_axis_hat = self._relax_direction(
                    prior_fire_axis_hat,
                    effective_fire_axis_raw_hat,
                    V4A_EFFECTIVE_FIRE_AXIS_RELAXATION_DEFAULT,
                )
                prior_fire_axis_coherence = float(
                    battle_bundle.get(
                        "effective_fire_axis_coherence_current",
                        battle_bundle.get("effective_fire_axis_coherence", 0.0),
                    )
                )
                fire_axis_coherence = _relax_scalar(
                    prior_fire_axis_coherence,
                    fire_axis_coherence_raw,
                    V4A_FIRE_AXIS_COHERENCE_RELAXATION_DEFAULT,
                )
                front_reorientation_weight_raw = (
                    V4A_FRONT_REORIENTATION_MAX_WEIGHT_DEFAULT
                    * float(engagement_geometry_active)
                    * float(fire_axis_coherence)
                )
                prior_front_reorientation_weight = float(
                    battle_bundle.get(
                        "front_reorientation_weight_current",
                        battle_bundle.get("front_reorientation_weight", 0.0),
                    )
                )
                front_reorientation_weight = _relax_scalar(
                    prior_front_reorientation_weight,
                    front_reorientation_weight_raw,
                    V4A_FRONT_REORIENTATION_RELAXATION_DEFAULT,
                )
                own_front_strip_depth = _compute_front_strip_depth(
                    own_units,
                    reference_direction_hat,
                    toward_positive=True,
                )
                enemy_front_strip_depth = _compute_front_strip_depth(
                    enemy_units,
                    reference_direction_hat,
                    toward_positive=False,
                )
                fire_entry_margin = max(
                    0.0,
                    float(battle_bundle.get("expected_reference_spacing", self.separation_radius)),
                )
                target_front_strip_gap_base = max(
                    0.0,
                    float(self.attack_range) - float(fire_entry_margin),
                )
                target_front_strip_gap_bias = float(
                    battle_bundle.get(
                        "battle_target_front_strip_gap_bias",
                        V4A_BATTLE_TARGET_FRONT_STRIP_GAP_BIAS_DEFAULT,
                    )
                )
                if not math.isfinite(target_front_strip_gap_bias):
                    target_front_strip_gap_bias = V4A_BATTLE_TARGET_FRONT_STRIP_GAP_BIAS_DEFAULT
                target_front_strip_gap = max(
                    0.0,
                    float(target_front_strip_gap_base) + float(target_front_strip_gap_bias),
                )
                hold_band = max(
                    0.1,
                    float(self.attack_range)
                    * max(0.0, float(battle_bundle.get("battle_standoff_hold_band_ratio", 0.0))),
                )
                hold_weight_strength = _clamp01(
                    float(
                        battle_bundle.get(
                            "battle_hold_weight_strength",
                            V4A_BATTLE_HOLD_WEIGHT_STRENGTH_DEFAULT,
                        )
                    )
                )
                current_front_strip_gap = float(reference_distance) - (
                    float(own_front_strip_depth) + float(enemy_front_strip_depth)
                )
                distance_gap = float(current_front_strip_gap) - float(target_front_strip_gap)
                reference_speed_values = [
                    float(unit.max_speed)
                    for unit in own_units
                    if math.isfinite(float(unit.max_speed)) and float(unit.max_speed) > 0.0
                ]
                if reference_speed_values:
                    relation_reference_speed = sum(reference_speed_values) / float(
                        len(reference_speed_values)
                    )
                else:
                    relation_reference_speed = 1.0
                battle_relation_lead_ticks = float(
                    battle_bundle.get(
                        "battle_relation_lead_ticks",
                        V4A_BATTLE_RELATION_LEAD_TICKS_DEFAULT,
                    )
                )
                if not math.isfinite(battle_relation_lead_ticks) or battle_relation_lead_ticks <= 0.0:
                    battle_relation_lead_ticks = V4A_BATTLE_RELATION_LEAD_TICKS_DEFAULT
                battle_hold_relaxation = float(
                    battle_bundle.get(
                        "battle_hold_relaxation",
                        V4A_BATTLE_HOLD_RELAXATION_DEFAULT,
                    )
                )
                if not math.isfinite(battle_hold_relaxation) or not 0.0 < battle_hold_relaxation <= 1.0:
                    battle_hold_relaxation = V4A_BATTLE_HOLD_RELAXATION_DEFAULT
                battle_approach_drive_relaxation = float(
                    battle_bundle.get(
                        "battle_approach_drive_relaxation",
                        V4A_BATTLE_APPROACH_DRIVE_RELAXATION_DEFAULT,
                    )
                )
                if (
                    not math.isfinite(battle_approach_drive_relaxation)
                    or not 0.0 < battle_approach_drive_relaxation <= 1.0
                ):
                    battle_approach_drive_relaxation = (
                        V4A_BATTLE_APPROACH_DRIVE_RELAXATION_DEFAULT
                    )
                relation_scale = max(
                    float(relation_reference_speed) * battle_relation_lead_ticks,
                    float(hold_band),
                    1e-9,
                )
                relation_gap_raw = max(
                    -1.0,
                    min(1.0, float(distance_gap) / relation_scale),
                )
                prior_relation_gap_current = float(
                    battle_bundle.get(
                        "battle_relation_gap_current",
                        battle_bundle.get("battle_relation_gap_raw", relation_gap_raw),
                    )
                )
                relation_gap_current = _relax_scalar(
                    prior_relation_gap_current,
                    float(relation_gap_raw),
                    battle_hold_relaxation,
                )
                close_drive_raw = _clamp01(-relation_gap_raw)
                prior_close_drive = float(
                    battle_bundle.get(
                        "battle_close_drive_current",
                        battle_bundle.get("battle_close_drive_raw", close_drive_raw),
                    )
                )
                close_drive = _relax_scalar(
                    prior_close_drive,
                    float(close_drive_raw),
                    battle_hold_relaxation,
                )
                brake_drive_raw = hold_weight_strength * close_drive_raw
                prior_brake_drive = float(
                    battle_bundle.get(
                        "battle_brake_drive_current",
                        battle_bundle.get("battle_brake_drive_raw", brake_drive_raw),
                    )
                )
                brake_drive = _relax_scalar(
                    prior_brake_drive,
                    float(brake_drive_raw),
                    battle_hold_relaxation,
                )
                hold_weight_raw = hold_weight_strength * _clamp01(
                    1.0 - min(1.0, abs(relation_gap_raw))
                )
                prior_hold_weight = float(
                    battle_bundle.get(
                        "battle_hold_weight_current",
                        battle_bundle.get("battle_hold_weight_raw", hold_weight_raw),
                    )
                )
                hold_weight = _relax_scalar(
                    prior_hold_weight,
                    float(hold_weight_raw),
                    battle_hold_relaxation,
                )
                approach_drive_raw = _clamp01(relation_gap_raw)
                prior_approach_drive = float(
                    battle_bundle.get(
                        "battle_approach_drive_current",
                        battle_bundle.get("battle_approach_drive_raw", approach_drive_raw),
                    )
                )
                approach_drive = _relax_scalar(
                    prior_approach_drive,
                    float(approach_drive_raw),
                    battle_approach_drive_relaxation,
                )
                if isinstance(battle_bundle, dict):
                    battle_bundle["effective_fire_axis_raw_xy"] = (
                        float(effective_fire_axis_raw_hat[0]),
                        float(effective_fire_axis_raw_hat[1]),
                    )
                    battle_bundle["effective_fire_axis_xy"] = (
                        float(effective_fire_axis_hat[0]),
                        float(effective_fire_axis_hat[1]),
                    )
                    battle_bundle["effective_fire_axis_current_xy"] = (
                        float(effective_fire_axis_hat[0]),
                        float(effective_fire_axis_hat[1]),
                    )
                    battle_bundle["engagement_geometry_active_raw"] = float(engagement_geometry_active_raw)
                    battle_bundle["engagement_geometry_active"] = float(engagement_geometry_active)
                    battle_bundle["engagement_geometry_active_current"] = float(engagement_geometry_active)
                    battle_bundle["front_reorientation_weight_raw"] = float(front_reorientation_weight_raw)
                    battle_bundle["front_reorientation_weight"] = float(front_reorientation_weight)
                    battle_bundle["front_reorientation_weight_current"] = float(front_reorientation_weight)
                    battle_bundle["effective_fire_axis_coherence_raw"] = float(
                        fire_axis_coherence_raw
                    )
                    battle_bundle["effective_fire_axis_coherence"] = float(fire_axis_coherence)
                    battle_bundle["effective_fire_axis_coherence_current"] = float(fire_axis_coherence)
                    battle_bundle["battle_relation_gap_raw"] = float(relation_gap_raw)
                    battle_bundle["battle_relation_gap_current"] = float(relation_gap_current)
                    battle_bundle["battle_fire_entry_margin"] = float(fire_entry_margin)
                    battle_bundle["battle_target_front_strip_gap_base"] = float(
                        target_front_strip_gap_base
                    )
                    battle_bundle["battle_target_front_strip_gap_bias"] = float(
                        target_front_strip_gap_bias
                    )
                    battle_bundle["battle_target_front_strip_gap"] = float(target_front_strip_gap)
                    battle_bundle["battle_current_front_strip_gap"] = float(current_front_strip_gap)
                    battle_bundle["battle_own_front_strip_depth"] = float(own_front_strip_depth)
                    battle_bundle["battle_enemy_front_strip_depth"] = float(enemy_front_strip_depth)
                    battle_bundle["battle_relation_scale"] = float(relation_scale)
                    battle_bundle["battle_relation_lead_ticks"] = float(battle_relation_lead_ticks)
                    battle_bundle["battle_hold_relaxation"] = float(battle_hold_relaxation)
                    battle_bundle["battle_approach_drive_relaxation"] = float(
                        battle_approach_drive_relaxation
                    )
                    battle_bundle["battle_close_drive_raw"] = float(close_drive_raw)
                    battle_bundle["battle_close_drive_current"] = float(close_drive)
                    battle_bundle["battle_brake_drive_raw"] = float(brake_drive_raw)
                    battle_bundle["battle_brake_drive_current"] = float(brake_drive)
                    battle_bundle["battle_hold_weight_raw"] = float(hold_weight_raw)
                    battle_bundle["battle_hold_weight_current"] = float(hold_weight)
                    battle_bundle["battle_approach_drive_raw"] = float(approach_drive_raw)
                    battle_bundle["battle_approach_drive_current"] = float(approach_drive)
                relation_drive = float(approach_drive - brake_drive)
                direction = (
                    float(reference_direction_hat[0]) * relation_drive,
                    float(reference_direction_hat[1]) * relation_drive,
                )
                intensity = float(abs(relation_drive))
            else:
                direction, intensity = reference_direction_hat, reference_distance
            last_target_direction[fleet_id] = direction
            last_engagement_intensity[fleet_id] = intensity

        return replace(
            state,
            last_target_direction=last_target_direction,
            last_engagement_intensity=last_engagement_intensity,
        )

    def evaluate_target(self, state: BattleState) -> BattleState:
        fixture_state = self._evaluate_target_with_fixture_objective(state)
        if fixture_state is not None:
            return fixture_state
        return self._evaluate_target_with_pre_tl_substrate(state)

    def _integrate_movement_symmetric_merge(self, state: BattleState) -> BattleState:
        fleet_ids = list(state.fleets.keys())
        if len(fleet_ids) <= 1:
            return self.integrate_movement(state)

        base_fleets = state.fleets
        merged_units = dict(state.units)
        merged_last_target_direction = dict(state.last_target_direction)
        merged_last_engagement_intensity = dict(state.last_engagement_intensity)
        first_debug_snapshot = None
        for lead_fleet_id in fleet_ids:
            ordered_fleets = {lead_fleet_id: base_fleets[lead_fleet_id]}
            for other_fleet_id in fleet_ids:
                if other_fleet_id != lead_fleet_id:
                    ordered_fleets[other_fleet_id] = base_fleets[other_fleet_id]
            moved_variant = self.integrate_movement(replace(state, fleets=ordered_fleets))
            if first_debug_snapshot is None:
                first_debug_snapshot = {
                    "debug_diag_last_tick": getattr(self, "debug_diag_last_tick", None),
                    "debug_last_cohesion_v3": getattr(self, "debug_last_cohesion_v3", None),
                    "debug_last_cohesion_v3_components": getattr(self, "debug_last_cohesion_v3_components", None),
                }
            for unit_id in base_fleets[lead_fleet_id].unit_ids:
                moved_unit = moved_variant.units.get(unit_id)
                if moved_unit is not None:
                    merged_units[unit_id] = moved_unit
            if lead_fleet_id in moved_variant.last_target_direction:
                merged_last_target_direction[lead_fleet_id] = moved_variant.last_target_direction[lead_fleet_id]
            if lead_fleet_id in moved_variant.last_engagement_intensity:
                merged_last_engagement_intensity[lead_fleet_id] = moved_variant.last_engagement_intensity[lead_fleet_id]
        if first_debug_snapshot is not None:
            self.debug_diag_last_tick = first_debug_snapshot["debug_diag_last_tick"]
            self.debug_last_cohesion_v3 = first_debug_snapshot["debug_last_cohesion_v3"]
            self.debug_last_cohesion_v3_components = first_debug_snapshot["debug_last_cohesion_v3_components"]
        return replace(
            state,
            units=merged_units,
            last_target_direction=merged_last_target_direction,
            last_engagement_intensity=merged_last_engagement_intensity,
        )

    def integrate_movement(self, state: BattleState) -> BattleState:
        movement_surface = getattr(self, "_movement_surface", {})
        movement_model = str(movement_surface.get("model", "v3a")).strip().lower()
        if movement_model != "v4a" or len(state.fleets) <= 0:
            return super().integrate_movement(state)
        if len(state.fleets) > 1 and not bool(getattr(self, "SYMMETRIC_MOVEMENT_SYNC_ENABLED", False)):
            return super().integrate_movement(state)
        previous_fixture_cfg = getattr(self, "TEST_RUN_FIXTURE_CFG", None)
        had_previous_fixture_cfg = isinstance(previous_fixture_cfg, dict)
        fixture_active_mode = (
            str(previous_fixture_cfg.get("active_mode", FIXTURE_MODE_BATTLE)).strip().lower()
            if had_previous_fixture_cfg
            else FIXTURE_MODE_BATTLE
        )
        fixture_bundle = getattr(self, "TEST_RUN_FIXTURE_REFERENCE_BUNDLE", None)
        battle_bundles_by_fleet = getattr(self, "TEST_RUN_BATTLE_RESTORE_BUNDLES_BY_FLEET", None)
        lead_fleet_id = str(next(iter(state.fleets.keys()), "")).strip()
        bundle: Mapping[str, Any] | None = None
        using_fixture_bundle = (
            fixture_active_mode == FIXTURE_MODE_NEUTRAL_TRANSIT_V1
            and had_previous_fixture_cfg
            and isinstance(fixture_bundle, Mapping)
        )
        if using_fixture_bundle:
            lead_fleet_id = str(previous_fixture_cfg.get("fleet_id", lead_fleet_id)).strip() or lead_fleet_id
            bundle = fixture_bundle
        elif isinstance(battle_bundles_by_fleet, Mapping):
            bundle = battle_bundles_by_fleet.get(lead_fleet_id)
        if not isinstance(bundle, Mapping):
            return super().integrate_movement(state)
        expected_slot_offsets_local, current_forward_hat_xy = self._resolve_v4a_reference_surface(
            state,
            fleet_id=lead_fleet_id,
            bundle=bundle,
        )
        if not expected_slot_offsets_local:
            return super().integrate_movement(state)
        movement_state = state
        terminal_active = bool(bundle.get("formation_terminal_active", False))
        hold_active = bool(bundle.get("formation_hold_active", False))
        engagement_geometry_active_current = _clamp01(
            float(bundle.get("engagement_geometry_active_current", 0.0))
        )
        if not hold_active:
            if terminal_active:
                raw_target_direction = (0.0, 0.0)
            else:
                raw_target_direction = state.last_target_direction.get(lead_fleet_id, (0.0, 0.0))
            raw_target_dx = float(raw_target_direction[0]) if len(raw_target_direction) >= 1 else 0.0
            raw_target_dy = float(raw_target_direction[1]) if len(raw_target_direction) >= 2 else 0.0
            raw_target_hat, raw_target_norm = self._normalize_direction(
                raw_target_dx,
                raw_target_dy,
            )
            raw_target_magnitude = math.sqrt((raw_target_dx * raw_target_dx) + (raw_target_dy * raw_target_dy))
            current_heading = bundle.get("movement_heading_current_xy", current_forward_hat_xy)
            if not isinstance(current_heading, Sequence) or len(current_heading) < 2:
                current_heading = current_forward_hat_xy
            current_heading_hat, current_heading_norm = self._normalize_direction(
                float(current_heading[0]) if len(current_heading) >= 1 else float(current_forward_hat_xy[0]),
                float(current_heading[1]) if len(current_heading) >= 2 else float(current_forward_hat_xy[1]),
            )
            if current_heading_norm <= 0.0:
                current_heading_hat = current_forward_hat_xy
            desired_heading_hat = raw_target_hat if raw_target_norm > 0.0 else current_forward_hat_xy
            heading_relaxation = max(
                1e-6,
                min(1.0, float(bundle.get("heading_relaxation", V4A_HEADING_RELAXATION_DEFAULT))),
            )
            current_heading_hat = self._relax_direction(
                current_heading_hat,
                desired_heading_hat,
                heading_relaxation,
            )
            bundle["movement_heading_current_xy"] = current_heading_hat
            shape_vs_advance_strength = max(
                0.0,
                min(1.0, float(bundle.get("shape_vs_advance_strength", V4A_SHAPE_VS_ADVANCE_STRENGTH_DEFAULT))),
            )
            shape_error_current = max(
                0.0,
                min(1.0, float(bundle.get("shape_error_current", 0.0))),
            )
            if raw_target_norm > 0.0:
                advance_share = max(
                    V4A_SHAPE_VS_ADVANCE_MIN_SHARE,
                    1.0 - (shape_vs_advance_strength * shape_error_current),
                )
            else:
                advance_share = 0.0
            if float(bundle.get("battle_relation_gap_current", float("nan"))) <= 0.0 and raw_target_magnitude > 0.0:
                advance_share = 1.0
            bundle["transition_advance_share"] = float(advance_share)
            updated_last_target_direction = dict(state.last_target_direction)
            if float(bundle.get("battle_relation_gap_current", float("nan"))) <= 0.0 and raw_target_magnitude > 0.0:
                updated_last_target_direction[lead_fleet_id] = (
                    float(raw_target_dx) * advance_share,
                    float(raw_target_dy) * advance_share,
                )
            else:
                updated_last_target_direction[lead_fleet_id] = (
                    float(current_heading_hat[0]) * raw_target_magnitude * advance_share,
                    float(current_heading_hat[1]) * raw_target_magnitude * advance_share,
                )
            updated_last_engagement_intensity = dict(state.last_engagement_intensity)
            updated_last_engagement_intensity[lead_fleet_id] = (
                float(updated_last_engagement_intensity.get(lead_fleet_id, 0.0)) * advance_share
            )
            movement_state = replace(
                state,
                last_target_direction=updated_last_target_direction,
                last_engagement_intensity=updated_last_engagement_intensity,
            )

            transition_reference_max_speed_by_unit = bundle.get("transition_reference_max_speed_by_unit", {})
            if not isinstance(transition_reference_max_speed_by_unit, Mapping):
                transition_reference_max_speed_by_unit = {
                    str(unit_id): float(movement_state.units[unit_id].max_speed)
                    for unit_id in state.fleets[lead_fleet_id].unit_ids
                    if unit_id in movement_state.units
                }
                bundle["transition_reference_max_speed_by_unit"] = dict(transition_reference_max_speed_by_unit)
            alive_units = [
                movement_state.units[unit_id]
                for unit_id in state.fleets[lead_fleet_id].unit_ids
                if unit_id in movement_state.units and float(movement_state.units[unit_id].hit_points) > 0.0
            ]
            if alive_units:
                centroid_x, centroid_y = self._compute_position_centroid(alive_units)
                secondary_hat_xy = (-float(current_forward_hat_xy[1]), float(current_forward_hat_xy[0]))
                expected_world_positions: dict[str, tuple[float, float]] = {}
                for unit_id, offset_local in expected_slot_offsets_local.items():
                    expected_world_positions[str(unit_id)] = (
                        float(centroid_x)
                        + (float(offset_local[0]) * float(current_forward_hat_xy[0]))
                        + (float(offset_local[1]) * float(secondary_hat_xy[0])),
                        float(centroid_y)
                        + (float(offset_local[0]) * float(current_forward_hat_xy[1]))
                        + (float(offset_local[1]) * float(secondary_hat_xy[1])),
                    )
                expected_reference_spacing = max(
                    1e-9,
                    float(bundle.get("expected_reference_spacing", self.separation_radius)),
                )
                engaged_speed_scale = max(
                    1e-6,
                    min(1.0, float(bundle.get("engaged_speed_scale", V4A_ENGAGED_SPEED_SCALE_DEFAULT))),
                )
                attack_speed_lateral_scale = max(
                    1e-6,
                    min(1.0, float(bundle.get("attack_speed_lateral_scale", V4A_ATTACK_SPEED_LATERAL_SCALE_DEFAULT))),
                )
                attack_speed_backward_scale = max(
                    0.0,
                    min(
                        attack_speed_lateral_scale,
                        float(bundle.get("attack_speed_backward_scale", V4A_ATTACK_SPEED_BACKWARD_SCALE_DEFAULT)),
                    ),
                )
                updated_units = dict(movement_state.units)
                changed = False
                for unit_id, reference_speed in transition_reference_max_speed_by_unit.items():
                    unit = updated_units.get(str(unit_id))
                    if unit is None:
                        continue
                    expected_position = expected_world_positions.get(str(unit_id))
                    forward_transport_delta = 0.0
                    if expected_position is None:
                        shape_need = 0.0
                    else:
                        dx = float(expected_position[0]) - float(unit.position.x)
                        dy = float(expected_position[1]) - float(unit.position.y)
                        shape_distance = math.sqrt((dx * dx) + (dy * dy))
                        shape_need = max(0.0, min(1.0, shape_distance / expected_reference_spacing))
                        forward_transport_delta = (
                            (dx * float(current_forward_hat_xy[0]))
                            + (dy * float(current_forward_hat_xy[1]))
                        )
                    unit_heading_hat, unit_heading_norm = self._normalize_direction(
                        float(unit.orientation_vector.x),
                        float(unit.orientation_vector.y),
                    )
                    if unit_heading_norm <= 0.0:
                        unit_heading_hat = current_heading_hat
                    heading_alignment = max(
                        0.0,
                        (float(unit_heading_hat[0]) * float(current_heading_hat[0]))
                        + (float(unit_heading_hat[1]) * float(current_heading_hat[1])),
                    )
                    turn_speed_scale_raw = V4A_TURN_SPEED_FLOOR + (
                        (1.0 - V4A_TURN_SPEED_FLOOR) * heading_alignment
                    )
                    battle_hold_weight_current = _clamp01(
                        float(bundle.get("battle_hold_weight_current", 0.0))
                    )
                    turn_speed_scale = turn_speed_scale_raw
                    shape_speed_scale = max(
                        V4A_TRANSITION_IDLE_SPEED_FLOOR,
                        max(advance_share, shape_need),
                    )
                    forward_transport_need = max(
                        0.0,
                        min(1.0, abs(float(forward_transport_delta)) / expected_reference_spacing),
                    )
                    forward_transport_speed_scale = 1.0
                    if forward_transport_delta < 0.0:
                        forward_transport_speed_scale = max(
                            V4A_FORWARD_TRANSPORT_BRAKE_FLOOR,
                            1.0 - (
                                V4A_FORWARD_TRANSPORT_BRAKE_STRENGTH_DEFAULT
                                * forward_transport_need
                            ),
                        )
                    elif forward_transport_delta > 0.0:
                        forward_transport_speed_scale = min(
                            V4A_FORWARD_TRANSPORT_MAX_SPEED_SCALE,
                            1.0 + (
                                V4A_FORWARD_TRANSPORT_BOOST_STRENGTH_DEFAULT
                                * forward_transport_need
                            ),
                        )
                    near_contact_stability = _clamp01(
                        battle_hold_weight_current
                        * max(
                            0.0,
                            min(
                                1.0,
                                float(
                                    bundle.get(
                                        "battle_near_contact_internal_stability_blend",
                                        V4A_NEAR_CONTACT_INTERNAL_STABILITY_BLEND_DEFAULT,
                                    )
                                ),
                            ),
                        )
                    )
                    if near_contact_stability > 0.0:
                        forward_transport_speed_scale = _relax_scalar(
                            float(forward_transport_speed_scale),
                            1.0,
                            near_contact_stability,
                        )
                        shape_speed_scale = _relax_scalar(
                            float(shape_speed_scale),
                            max(V4A_TRANSITION_IDLE_SPEED_FLOOR, advance_share),
                            near_contact_stability,
                        )
                    attack_speed_scale = 1.0
                    engaged_target_id = str(unit.engaged_target_id).strip() if unit.engaged_target_id is not None else ""
                    if bool(unit.engaged) and engaged_target_id:
                        target_unit = movement_state.units.get(engaged_target_id)
                        if target_unit is not None and float(target_unit.hit_points) > 0.0:
                            attack_hat_xy, attack_norm = self._normalize_direction(
                                float(target_unit.position.x) - float(unit.position.x),
                                float(target_unit.position.y) - float(unit.position.y),
                            )
                            if attack_norm > 0.0:
                                attack_cos_theta = (
                                    (float(unit_heading_hat[0]) * float(attack_hat_xy[0]))
                                    + (float(unit_heading_hat[1]) * float(attack_hat_xy[1]))
                                )
                                attack_direction_scale = _compute_attack_direction_speed_scale(
                                    attack_cos_theta,
                                    lateral_scale=attack_speed_lateral_scale,
                                    backward_scale=attack_speed_backward_scale,
                                )
                                attack_speed_scale = float(engaged_speed_scale) * float(attack_direction_scale)
                    if engagement_geometry_active_current > 0.0:
                        fleet_contact_speed_scale = _relax_scalar(
                            1.0,
                            float(engaged_speed_scale),
                            engagement_geometry_active_current,
                        )
                        attack_speed_scale = _relax_scalar(
                            attack_speed_scale,
                            fleet_contact_speed_scale,
                            engagement_geometry_active_current,
                        )
                    transition_speed_target = (
                        float(reference_speed)
                        * shape_speed_scale
                        * float(forward_transport_speed_scale)
                        * turn_speed_scale
                        * float(attack_speed_scale)
                    )
                    battle_near_contact_speed_relaxation = max(
                        1e-6,
                        min(
                            1.0,
                            float(
                                bundle.get(
                                    "battle_near_contact_speed_relaxation",
                                    V4A_NEAR_CONTACT_SPEED_RELAXATION_DEFAULT,
                                )
                            ),
                        ),
                    )
                    transition_speed = _relax_scalar(
                        float(unit.max_speed),
                        float(transition_speed_target),
                        battle_near_contact_speed_relaxation,
                    )
                    if abs(float(unit.max_speed) - transition_speed) <= 1e-9:
                        continue
                    updated_units[str(unit_id)] = replace(unit, max_speed=float(transition_speed))
                    changed = True
                if changed:
                    movement_state = replace(movement_state, units=updated_units)
        if hold_active:
            updated_last_target_direction = dict(state.last_target_direction)
            updated_last_target_direction[lead_fleet_id] = (0.0, 0.0)
            updated_last_engagement_intensity = dict(state.last_engagement_intensity)
            updated_last_engagement_intensity[lead_fleet_id] = 0.0
            movement_state = replace(
                state,
                last_target_direction=updated_last_target_direction,
                last_engagement_intensity=updated_last_engagement_intensity,
            )
            hold_reference_max_speed_by_unit = bundle.get("formation_hold_reference_max_speed_by_unit", {})
            if not isinstance(hold_reference_max_speed_by_unit, Mapping):
                hold_reference_max_speed_by_unit = {
                    str(unit_id): float(movement_state.units[unit_id].max_speed)
                    for unit_id in state.fleets[lead_fleet_id].unit_ids
                    if unit_id in movement_state.units
                }
                bundle["formation_hold_reference_max_speed_by_unit"] = dict(hold_reference_max_speed_by_unit)
            updated_units = dict(movement_state.units)
            changed = False
            for unit_id, reference_speed in hold_reference_max_speed_by_unit.items():
                unit = updated_units.get(str(unit_id))
                if unit is None:
                    continue
                held_speed = float(reference_speed) * V4A_HOLD_AWAIT_SPEED_SCALE_DEFAULT
                if abs(float(unit.max_speed) - held_speed) <= 1e-9:
                    continue
                updated_units[str(unit_id)] = replace(unit, max_speed=float(held_speed))
                changed = True
            if changed:
                movement_state = replace(movement_state, units=updated_units)

        if using_fixture_bundle and had_previous_fixture_cfg:
            previous_fixture_cfg["initial_forward_hat_xy"] = tuple(current_forward_hat_xy)
            previous_fixture_cfg["expected_slot_offsets_local"] = dict(expected_slot_offsets_local)
            previous_fixture_cfg["expected_position_candidate_active"] = True
            previous_fixture_cfg["formation_hold_active"] = bool(bundle.get("formation_hold_active", False))
            return super().integrate_movement(movement_state)
        if had_previous_fixture_cfg:
            previous_fixture_cfg["initial_forward_hat_xy"] = tuple(current_forward_hat_xy)
            previous_fixture_cfg["expected_slot_offsets_local"] = dict(expected_slot_offsets_local)
        temp_fixture_cfg = dict(previous_fixture_cfg) if had_previous_fixture_cfg else {}
        temp_fixture_cfg.update(
            {
                "active_mode": FIXTURE_MODE_NEUTRAL_TRANSIT_V1,
                "fleet_id": lead_fleet_id,
                "expected_position_candidate_active": True,
                "initial_forward_hat_xy": tuple(current_forward_hat_xy),
                "expected_slot_offsets_local": dict(expected_slot_offsets_local),
                "frozen_terminal_frame_active": False,
                "frozen_terminal_primary_axis_xy": None,
                "frozen_terminal_secondary_axis_xy": None,
                "objective_contract_3d": None,
                "stop_radius": 0.0,
            }
        )
        self.TEST_RUN_FIXTURE_CFG = temp_fixture_cfg
        try:
            return super().integrate_movement(movement_state)
        finally:
            if had_previous_fixture_cfg:
                self.TEST_RUN_FIXTURE_CFG = previous_fixture_cfg
            elif hasattr(self, "TEST_RUN_FIXTURE_CFG"):
                delattr(self, "TEST_RUN_FIXTURE_CFG")

    @staticmethod
    def _stable_pair_direction(unit_i: str, unit_j: str) -> tuple[float, float]:
        low, high = (unit_i, unit_j) if unit_i < unit_j else (unit_j, unit_i)
        acc_x = 0
        acc_y = 0
        for idx, ch in enumerate(low + "|" + high, start=1):
            code = ord(ch)
            acc_x = (acc_x * 131) + (code * idx)
            acc_y = (acc_y * 137) + (code * (idx + 17))
        sx = float((acc_x % 1024) - 512)
        sy = float((acc_y % 1024) - 512)
        if sx == 0.0 and sy == 0.0:
            sy = 1.0
        norm = math.sqrt((sx * sx) + (sy * sy))
        return (sx / norm, sy / norm)

    def _resolve_hostile_contact_impedance_mode(self) -> str:
        raw_mode = str(
            getattr(
                self,
                "HOSTILE_CONTACT_IMPEDANCE_MODE",
                HOSTILE_CONTACT_IMPEDANCE_MODE_DEFAULT,
            )
        ).strip().lower()
        if raw_mode not in HOSTILE_CONTACT_IMPEDANCE_MODE_LABELS:
            raw_mode = HOSTILE_CONTACT_IMPEDANCE_MODE_DEFAULT
        return raw_mode

    def _compute_fleet_enemy_axes(self, state: BattleState) -> dict[str, tuple[float, float]]:
        axes: dict[str, tuple[float, float]] = {}
        fleet_centroids: dict[str, tuple[float, float]] = {}
        for fleet_id, fleet in state.fleets.items():
            alive_units = [
                state.units[uid]
                for uid in fleet.unit_ids
                if uid in state.units and float(state.units[uid].hit_points) > 0.0
            ]
            fleet_centroids[fleet_id] = self._compute_position_centroid(alive_units)
        for fleet_id, (cx, cy) in fleet_centroids.items():
            enemy_centroids = [
                pos for other_fleet_id, pos in fleet_centroids.items() if other_fleet_id != fleet_id
            ]
            if not enemy_centroids:
                axes[fleet_id] = (0.0, 0.0)
                continue
            enemy_cx = sum(pos[0] for pos in enemy_centroids) / float(len(enemy_centroids))
            enemy_cy = sum(pos[1] for pos in enemy_centroids) / float(len(enemy_centroids))
            axis, _ = self._normalize_direction(enemy_cx - cx, enemy_cy - cy)
            axes[fleet_id] = axis
        return axes

    def _compute_unit_hostile_proximity(
        self,
        state: BattleState,
        impedance_radius: float,
    ) -> tuple[dict[str, float], dict[str, list[tuple[str, float, float, float, float]]]]:
        alive_units = [
            unit for unit in state.units.values() if float(unit.hit_points) > 0.0
        ]
        proximity_by_unit = {unit.unit_id: 0.0 for unit in alive_units}
        pair_terms_by_unit = {unit.unit_id: [] for unit in alive_units}
        radius_sq = impedance_radius * impedance_radius
        for i in range(len(alive_units)):
            unit_i = alive_units[i]
            for j in range(i + 1, len(alive_units)):
                unit_j = alive_units[j]
                if unit_i.fleet_id == unit_j.fleet_id:
                    continue
                dx = float(unit_i.position.x) - float(unit_j.position.x)
                dy = float(unit_i.position.y) - float(unit_j.position.y)
                distance_sq = (dx * dx) + (dy * dy)
                if distance_sq > radius_sq:
                    continue
                if distance_sq > 1e-12:
                    distance = math.sqrt(distance_sq)
                    nx = dx / distance
                    ny = dy / distance
                else:
                    nx, ny = self._stable_pair_direction(unit_i.unit_id, unit_j.unit_id)
                    distance = 0.0
                proximity = _clamp01(1.0 - (distance / impedance_radius))
                weight = proximity * proximity
                proximity_by_unit[unit_i.unit_id] = _clamp01(proximity_by_unit[unit_i.unit_id] + weight)
                proximity_by_unit[unit_j.unit_id] = _clamp01(proximity_by_unit[unit_j.unit_id] + weight)
                pair_terms_by_unit[unit_i.unit_id].append((unit_j.unit_id, nx, ny, proximity, weight))
                pair_terms_by_unit[unit_j.unit_id].append((unit_i.unit_id, -nx, -ny, proximity, weight))
        return proximity_by_unit, pair_terms_by_unit

    @staticmethod
    def _hostile_spacing_depth(distance: float, envelope_radius: float) -> float:
        if envelope_radius <= 1e-12:
            return 0.0
        return _clamp01((envelope_radius - distance) / envelope_radius)

    def _compute_hostile_spacing_value(
        self,
        state: BattleState,
        *,
        own_fleet_id: str,
        x: float,
        y: float,
        envelope_radius: float,
    ) -> float:
        if envelope_radius <= 1e-12:
            return 0.0
        remaining_clearance = 1.0
        radius_sq = envelope_radius * envelope_radius
        for unit in state.units.values():
            if unit.fleet_id == own_fleet_id or float(unit.hit_points) <= 0.0:
                continue
            dx = x - float(unit.position.x)
            dy = y - float(unit.position.y)
            distance_sq = (dx * dx) + (dy * dy)
            if distance_sq >= radius_sq:
                continue
            distance = math.sqrt(max(0.0, distance_sq))
            depth = self._hostile_spacing_depth(distance, envelope_radius)
            if depth <= 0.0:
                continue
            remaining_clearance *= (1.0 - (depth * depth))
            if remaining_clearance <= 1e-9:
                return 1.0
        return _clamp01(1.0 - remaining_clearance)

    def _apply_hostile_intent_penetration_bias(self, state: BattleState) -> BattleState:
        mode = self._resolve_hostile_contact_impedance_mode()
        if mode != HOSTILE_CONTACT_IMPEDANCE_MODE_INTENT_UNIFIED_SPACING_V1:
            return state

        scale = max(
            1e-6,
            float(
                getattr(
                    self,
                    "HOSTILE_INTENT_UNIFIED_SPACING_SCALE",
                    HOSTILE_INTENT_UNIFIED_SPACING_SCALE_DEFAULT,
                )
            ),
        )
        strength = _clamp01(
            float(
                getattr(
                    self,
                    "HOSTILE_INTENT_UNIFIED_SPACING_STRENGTH",
                    HOSTILE_INTENT_UNIFIED_SPACING_STRENGTH_DEFAULT,
                )
            )
        )

        envelope_radius = scale * float(self.separation_radius)
        alive_units = [unit for unit in state.units.values() if float(unit.hit_points) > 0.0]
        if len(alive_units) <= 1 or envelope_radius <= 1e-12 or strength <= 0.0:
            self.debug_last_hostile_contact_impedance = {
                "mode": mode,
                "enabled": True,
                "active": False,
                "layer": "intent",
                "radius": envelope_radius,
                "mean_signal": 0.0,
                "mean_speed_scale": 1.0,
                "strength": strength,
            }
            return state

        fallback_axes = self._compute_fleet_enemy_axes(state)
        updated_units = dict(state.units)
        signal_sum = 0.0
        speed_scale_sum = 0.0
        active_count = 0
        for unit in alive_units:
            pre_x = float(unit.position.x)
            pre_y = float(unit.position.y)
            pre_occ = self._compute_hostile_spacing_value(
                state,
                own_fleet_id=unit.fleet_id,
                x=pre_x,
                y=pre_y,
                envelope_radius=envelope_radius,
            )
            dir_x, dir_y = state.last_target_direction.get(unit.fleet_id, (0.0, 0.0))
            dir_norm = math.sqrt((dir_x * dir_x) + (dir_y * dir_y))
            if dir_norm <= 1e-12:
                dir_x, dir_y = fallback_axes.get(unit.fleet_id, (0.0, 0.0))
                dir_norm = math.sqrt((dir_x * dir_x) + (dir_y * dir_y))
            if dir_norm > 1e-12:
                dir_x /= dir_norm
                dir_y /= dir_norm
            projected_x = pre_x + (dir_x * float(unit.max_speed) * float(state.dt))
            projected_y = pre_y + (dir_y * float(unit.max_speed) * float(state.dt))
            post_occ = self._compute_hostile_spacing_value(
                state,
                own_fleet_id=unit.fleet_id,
                x=projected_x,
                y=projected_y,
                envelope_radius=envelope_radius,
            )
            signal = max(0.0, post_occ - pre_occ)
            speed_scale = max(0.0, 1.0 - (strength * signal))
            if speed_scale >= 0.999999:
                continue
            updated_units[unit.unit_id] = replace(unit, max_speed=float(unit.max_speed) * speed_scale)
            signal_sum += signal
            speed_scale_sum += speed_scale
            active_count += 1

        self.debug_last_hostile_contact_impedance = {
            "mode": mode,
            "enabled": True,
            "active": active_count > 0,
            "layer": "intent",
            "radius": envelope_radius,
            "mean_signal": (signal_sum / float(active_count)) if active_count > 0 else 0.0,
            "mean_speed_scale": (speed_scale_sum / float(active_count)) if active_count > 0 else 1.0,
            "strength": strength,
        }
        return replace(state, units=updated_units)

    def _restore_intent_penetration_bias_units(
        self,
        reference_state: BattleState,
        moved_state: BattleState,
    ) -> BattleState:
        mode = self._resolve_hostile_contact_impedance_mode()
        if mode != HOSTILE_CONTACT_IMPEDANCE_MODE_INTENT_UNIFIED_SPACING_V1:
            return moved_state

        updated_units = dict(moved_state.units)
        changed = False
        for unit_id, unit in moved_state.units.items():
            reference_unit = reference_state.units.get(unit_id)
            if reference_unit is None:
                continue
            if float(unit.max_speed) == float(reference_unit.max_speed):
                continue
            updated_units[unit_id] = replace(unit, max_speed=float(reference_unit.max_speed))
            changed = True
        if not changed:
            return moved_state
        return replace(moved_state, units=updated_units)

    def _apply_hostile_contact_impedance_v2(
        self,
        pre_state: BattleState,
        moved_state: BattleState,
        *,
        mode: str,
    ) -> BattleState:
        radius_multiplier = max(
            1e-6,
            float(
                getattr(
                    self,
                    "HOSTILE_CONTACT_IMPEDANCE_V2_RADIUS_MULTIPLIER",
                    HOSTILE_CONTACT_IMPEDANCE_V2_RADIUS_MULTIPLIER_DEFAULT,
                )
            ),
        )
        repulsion_max_disp_ratio = max(
            0.0,
            float(
                getattr(
                    self,
                    "HOSTILE_CONTACT_IMPEDANCE_V2_REPULSION_MAX_DISP_RATIO",
                    HOSTILE_CONTACT_IMPEDANCE_V2_REPULSION_MAX_DISP_RATIO_DEFAULT,
                )
            ),
        )
        forward_damping_strength = _clamp01(
            float(
                getattr(
                    self,
                    "HOSTILE_CONTACT_IMPEDANCE_V2_FORWARD_DAMPING_STRENGTH",
                    HOSTILE_CONTACT_IMPEDANCE_V2_FORWARD_DAMPING_STRENGTH_DEFAULT,
                )
            )
        )
        impedance_radius = float(self.separation_radius) * radius_multiplier
        if impedance_radius <= 1e-12:
            self.debug_last_hostile_contact_impedance = {
                "mode": mode,
                "enabled": False,
                "active": False,
                "pair_count": 0,
                "radius": impedance_radius,
                "mean_proximity": 0.0,
                "mean_forward_damping": 0.0,
                "mean_repulsion_displacement": 0.0,
                "max_repulsion_displacement": 0.0,
            }
            return moved_state

        alive_units = [
            unit for unit in moved_state.units.values() if float(unit.hit_points) > 0.0
        ]
        if len(alive_units) <= 1:
            self.debug_last_hostile_contact_impedance = {
                "mode": mode,
                "enabled": True,
                "active": False,
                "pair_count": 0,
                "radius": impedance_radius,
                "mean_proximity": 0.0,
                "mean_forward_damping": 0.0,
                "mean_repulsion_displacement": 0.0,
                "max_repulsion_displacement": 0.0,
            }
            return moved_state

        fleet_axes = self._compute_fleet_enemy_axes(moved_state)
        proximity_by_unit, pair_terms_by_unit = self._compute_unit_hostile_proximity(moved_state, impedance_radius)
        updated_units = dict(moved_state.units)
        repulsion_sum = 0.0
        repulsion_max = 0.0
        repulsion_count = 0
        damping_sum = 0.0
        damping_count = 0
        max_repulsion_disp = float(self.separation_radius) * repulsion_max_disp_ratio
        pair_count = sum(len(terms) for terms in pair_terms_by_unit.values()) // 2

        for unit in alive_units:
            pre_unit = pre_state.units.get(unit.unit_id)
            if pre_unit is None:
                continue
            axis_x, axis_y = fleet_axes.get(unit.fleet_id, (0.0, 0.0))
            dx_move = float(unit.position.x) - float(pre_unit.position.x)
            dy_move = float(unit.position.y) - float(pre_unit.position.y)
            forward_disp = (dx_move * axis_x) + (dy_move * axis_y)
            residual_x = dx_move
            residual_y = dy_move
            if abs(forward_disp) > 1e-12:
                residual_x -= forward_disp * axis_x
                residual_y -= forward_disp * axis_y

            local_proximity = _clamp01(proximity_by_unit.get(unit.unit_id, 0.0))
            damping_factor = 1.0
            if mode == HOSTILE_CONTACT_IMPEDANCE_MODE_HYBRID_V2 and forward_disp > 0.0:
                damping_factor = 1.0 - (_clamp01(forward_damping_strength * local_proximity))
                forward_disp *= damping_factor
                damping_sum += (1.0 - damping_factor)
                damping_count += 1

            repulsion_x = 0.0
            repulsion_y = 0.0
            if (
                mode == HOSTILE_CONTACT_IMPEDANCE_MODE_HYBRID_V2
                and max_repulsion_disp > 0.0
                and local_proximity > 0.0
            ):
                for _, nx, ny, _, weight in pair_terms_by_unit.get(unit.unit_id, []):
                    repulsion_x += nx * weight
                    repulsion_y += ny * weight
                repulsion_norm = math.sqrt((repulsion_x * repulsion_x) + (repulsion_y * repulsion_y))
                if repulsion_norm > 1e-12:
                    scale = max_repulsion_disp * local_proximity / repulsion_norm
                    repulsion_x *= scale
                    repulsion_y *= scale
                    repulsion_disp = math.sqrt((repulsion_x * repulsion_x) + (repulsion_y * repulsion_y))
                    repulsion_sum += repulsion_disp
                    repulsion_count += 1
                    if repulsion_disp > repulsion_max:
                        repulsion_max = repulsion_disp

            new_dx = (forward_disp * axis_x) + residual_x + repulsion_x
            new_dy = (forward_disp * axis_y) + residual_y + repulsion_y
            updated_units[unit.unit_id] = replace(
                unit,
                position=Vec2(
                    x=float(pre_unit.position.x) + new_dx,
                    y=float(pre_unit.position.y) + new_dy,
                ),
            )

        self.debug_last_hostile_contact_impedance = {
            "mode": mode,
            "enabled": True,
            "active": pair_count > 0,
            "pair_count": pair_count,
            "radius": impedance_radius,
            "mean_proximity": (
                sum(proximity_by_unit.values()) / float(max(1, len(proximity_by_unit)))
            ),
            "mean_forward_damping": (damping_sum / damping_count) if damping_count > 0 else 0.0,
            "mean_repulsion_displacement": (repulsion_sum / repulsion_count) if repulsion_count > 0 else 0.0,
            "max_repulsion_displacement": repulsion_max,
            "repulsion_max_disp_ratio": repulsion_max_disp_ratio,
            "forward_damping_strength": forward_damping_strength,
        }
        return replace(moved_state, units=updated_units)

    def _apply_hostile_contact_impedance(
        self,
        pre_state: BattleState,
        moved_state: BattleState,
    ) -> BattleState:
        mode = self._resolve_hostile_contact_impedance_mode()
        if mode == HOSTILE_CONTACT_IMPEDANCE_MODE_OFF:
            self.debug_last_hostile_contact_impedance = {
                "mode": mode,
                "enabled": False,
                "active": False,
                "pair_count": 0,
                "radius": 0.0,
            }
            return moved_state
        if mode == HOSTILE_CONTACT_IMPEDANCE_MODE_INTENT_UNIFIED_SPACING_V1:
            return moved_state
        return self._apply_hostile_contact_impedance_v2(pre_state, moved_state, mode=mode)

    def step(self, state: BattleState) -> BattleState:
        snapshot = replace(state, tick=state.tick + 1)
        next_state = self.evaluate_cohesion(snapshot)
        next_state = self.evaluate_target(next_state)
        next_state = self.evaluate_utility(next_state)
        movement_input_state = self._apply_hostile_intent_penetration_bias(next_state)
        if bool(getattr(self, "SYMMETRIC_MOVEMENT_SYNC_ENABLED", False)):
            moved_state = self._integrate_movement_symmetric_merge(movement_input_state)
        else:
            moved_state = self.integrate_movement(movement_input_state)
        moved_state = self._restore_intent_penetration_bias_units(next_state, moved_state)
        moved_state = self._apply_hostile_contact_impedance(next_state, moved_state)
        fixture_cfg = getattr(self, "TEST_RUN_FIXTURE_CFG", None)
        if isinstance(fixture_cfg, dict) and str(fixture_cfg.get("active_mode", "")).strip().lower() == FIXTURE_MODE_NEUTRAL_TRANSIT_V1:
            fixture_fleet_id = str(fixture_cfg.get("fleet_id", "")).strip()
            objective_contract_3d = fixture_cfg.get("objective_contract_3d")
            stop_radius = float(fixture_cfg.get("stop_radius", 0.0))
            late_clamp_active_for_tick = False
            late_clamp_overshoot = 0.0
            late_clamp_dx = 0.0
            late_clamp_dy = 0.0
            if fixture_fleet_id and isinstance(objective_contract_3d, Mapping) and stop_radius > 0.0:
                anchor_point_xyz = objective_contract_3d.get("anchor_point_xyz")
                if isinstance(anchor_point_xyz, (list, tuple)) and len(anchor_point_xyz) >= 2:
                    _, pre_centroid_x, pre_centroid_y = self._collect_alive_fleet_positions(next_state, fixture_fleet_id)
                    alive_rows, post_centroid_x, post_centroid_y = self._collect_alive_fleet_positions(moved_state, fixture_fleet_id)
                    axis_dx = float(anchor_point_xyz[0]) - float(pre_centroid_x)
                    axis_dy = float(anchor_point_xyz[1]) - float(pre_centroid_y)
                    remaining_distance = math.sqrt((axis_dx * axis_dx) + (axis_dy * axis_dy))
                    if alive_rows and remaining_distance > 1e-12 and remaining_distance <= stop_radius:
                        late_clamp_active_for_tick = True
                        axis_x = axis_dx / remaining_distance
                        axis_y = axis_dy / remaining_distance
                        realized_forward_advance = (
                            ((float(post_centroid_x) - float(pre_centroid_x)) * axis_x)
                            + ((float(post_centroid_y) - float(pre_centroid_y)) * axis_y)
                        )
                        if realized_forward_advance > remaining_distance:
                            overshoot = realized_forward_advance - remaining_distance
                            late_clamp_overshoot = float(overshoot)
                            late_clamp_dx = float(-(overshoot * axis_x))
                            late_clamp_dy = float(-(overshoot * axis_y))
                            corrected_units = dict(moved_state.units)
                            for unit_id in moved_state.fleets[fixture_fleet_id].unit_ids:
                                unit = corrected_units.get(unit_id)
                                if unit is None or float(unit.hit_points) <= 0.0:
                                    continue
                                corrected_units[unit_id] = replace(
                                    unit,
                                    position=Vec2(
                                        x=float(unit.position.x) - (overshoot * axis_x),
                                        y=float(unit.position.y) - (overshoot * axis_y),
                                    ),
                                )
                            moved_state = replace(moved_state, units=corrected_units)
            pending_diag = self._debug_state.get("diag_pending")
            if isinstance(pending_diag, dict) and int(pending_diag.get("tick", -1)) == int(next_state.tick):
                fixture_trace = pending_diag.get("fixture_terminal_trace")
                if isinstance(fixture_trace, dict):
                    trace_units = fixture_trace.get("units")
                    if isinstance(trace_units, dict):
                        for unit_id, row in trace_units.items():
                            if not isinstance(row, dict):
                                continue
                            unit = moved_state.units.get(unit_id)
                            if unit is None:
                                continue
                            x_pre = float(row.get("x_pre", unit.position.x))
                            y_pre = float(row.get("y_pre", unit.position.y))
                            x_post = float(unit.position.x)
                            y_post = float(unit.position.y)
                            realized_dx = x_post - x_pre
                            realized_dy = y_post - y_pre
                            row["x_post"] = x_post
                            row["y_post"] = y_post
                            row["realized_dx"] = float(realized_dx)
                            row["realized_dy"] = float(realized_dy)
                            row["realized_disp_norm"] = float(math.sqrt((realized_dx * realized_dx) + (realized_dy * realized_dy)))
                            row["late_clamp_active_for_tick"] = bool(late_clamp_active_for_tick)
                            row["late_clamp_overshoot"] = float(late_clamp_overshoot)
                            row["late_clamp_dx"] = float(late_clamp_dx)
                            row["late_clamp_dy"] = float(late_clamp_dy)
        return self.resolve_combat(moved_state)

    def _compute_cohesion_v2_geometry(self, state: BattleState, fleet_id: str) -> tuple[float, dict]:
        eps = 1e-12
        fleet = state.fleets.get(fleet_id)
        if fleet is None:
            return 1.0, {
                "n_alive": 0,
                "centroid_x": 0.0,
                "centroid_y": 0.0,
                "fragmentation": 0.0,
                "dispersion": 0.0,
                "outlier_mass": 0.0,
                "elongation": 0.0,
                "exploitability": 0.0,
                "cohesion_v2": 1.0,
                "lcc_ratio": 1.0,
                "dispersion_ratio_q90_q50": 1.0,
                "outlier_count": 0,
                "outlier_threshold": 0.0,
                "q50_radius": 0.0,
                "q90_radius": 0.0,
                "connect_radius_effective": 0.0,
                "connect_radius_multiplier": 1.0,
            }

        alive_positions = []
        for unit_id in fleet.unit_ids:
            unit = state.units.get(unit_id)
            if unit is None or unit.hit_points <= 0.0:
                continue
            alive_positions.append((unit.position.x, unit.position.y))
        n_alive = len(alive_positions)

        v2_connect_multiplier = float(getattr(self, "V2_CONNECT_RADIUS_MULTIPLIER", 1.0))
        if v2_connect_multiplier <= 0.0:
            v2_connect_multiplier = 1.0

        if n_alive == 0:
            return 0.0, {
                "n_alive": 0,
                "centroid_x": 0.0,
                "centroid_y": 0.0,
                "fragmentation": 1.0,
                "dispersion": 0.0,
                "outlier_mass": 0.0,
                "elongation": 0.0,
                "exploitability": 1.0,
                "cohesion_v2": 0.0,
                "lcc_ratio": 0.0,
                "dispersion_ratio_q90_q50": 1.0,
                "outlier_count": 0,
                "outlier_threshold": 0.0,
                "q50_radius": 0.0,
                "q90_radius": 0.0,
                "connect_radius_effective": float(self.separation_radius) * v2_connect_multiplier,
                "connect_radius_multiplier": v2_connect_multiplier,
            }

        sum_x = 0.0
        sum_y = 0.0
        for x, y in alive_positions:
            sum_x += x
            sum_y += y
        centroid_x = sum_x / n_alive
        centroid_y = sum_y / n_alive

        radii = []
        cov_xx = 0.0
        cov_xy = 0.0
        cov_yy = 0.0
        for x, y in alive_positions:
            dx = x - centroid_x
            dy = y - centroid_y
            radii.append(math.sqrt((dx * dx) + (dy * dy)))
            cov_xx += dx * dx
            cov_xy += dx * dy
            cov_yy += dy * dy
        cov_xx /= n_alive
        cov_xy /= n_alive
        cov_yy /= n_alive

        sorted_radii = sorted(radii)
        q25 = self._quantile_sorted(sorted_radii, 0.25)
        q50 = self._quantile_sorted(sorted_radii, 0.50)
        q75 = self._quantile_sorted(sorted_radii, 0.75)
        q90 = self._quantile_sorted(sorted_radii, 0.90)
        iqr = max(0.0, q75 - q25)

        if q90 <= eps and q50 <= eps:
            dispersion_ratio = 1.0
            f_disp = 0.0
        else:
            dispersion_ratio = q90 / (q50 + eps)
            if dispersion_ratio < 1.0:
                dispersion_ratio = 1.0
            f_disp = 1.0 - (1.0 / dispersion_ratio)
            f_disp = self._clamp01(f_disp)

        outlier_threshold = q75 + (1.5 * iqr)
        outlier_count = 0
        for r in radii:
            if r > outlier_threshold:
                outlier_count += 1
        f_out = self._clamp01(outlier_count / n_alive)

        trace = cov_xx + cov_yy
        det = (cov_xx * cov_yy) - (cov_xy * cov_xy)
        disc = max(0.0, (trace * trace) - (4.0 * det))
        sqrt_disc = math.sqrt(disc)
        lambda_1 = 0.5 * (trace + sqrt_disc)
        lambda_2 = 0.5 * (trace - sqrt_disc)
        if lambda_1 < eps:
            f_elong = 0.0
        else:
            f_elong = 1.0 - (lambda_2 / (lambda_1 + eps))
            f_elong = self._clamp01(f_elong)

        if n_alive == 1:
            lcc_ratio = 1.0
            connect_radius_effective = float(self.separation_radius) * v2_connect_multiplier
        else:
            connect_radius = float(self.separation_radius) * v2_connect_multiplier
            if connect_radius < eps:
                connect_radius = eps
            connect_radius_effective = connect_radius
            connect_radius_sq = connect_radius * connect_radius
            visited = [False] * n_alive
            largest_component_size = 0
            for i in range(n_alive):
                if visited[i]:
                    continue
                visited[i] = True
                stack = [i]
                component_size = 0
                while stack:
                    node = stack.pop()
                    component_size += 1
                    nx, ny = alive_positions[node]
                    for j in range(n_alive):
                        if visited[j] or j == node:
                            continue
                        px, py = alive_positions[j]
                        ddx = nx - px
                        ddy = ny - py
                        if (ddx * ddx) + (ddy * ddy) <= connect_radius_sq:
                            visited[j] = True
                            stack.append(j)
                if component_size > largest_component_size:
                    largest_component_size = component_size
            lcc_ratio = largest_component_size / n_alive
        f_frag = self._clamp01(1.0 - lcc_ratio)

        exploitability = 1.0 - (
            (1.0 - f_frag)
            * (1.0 - f_disp)
            * (1.0 - f_out)
            * (1.0 - f_elong)
        )
        cohesion_v2 = self._clamp01(1.0 - exploitability)

        return cohesion_v2, {
            "n_alive": n_alive,
            "centroid_x": centroid_x,
            "centroid_y": centroid_y,
            "fragmentation": f_frag,
            "dispersion": f_disp,
            "outlier_mass": f_out,
            "elongation": f_elong,
            "exploitability": exploitability,
            "cohesion_v2": cohesion_v2,
            "lcc_ratio": lcc_ratio,
            "dispersion_ratio_q90_q50": dispersion_ratio,
            "outlier_count": outlier_count,
            "outlier_threshold": outlier_threshold,
            "q50_radius": q50,
            "q90_radius": q90,
            "connect_radius_effective": connect_radius_effective,
            "connect_radius_multiplier": v2_connect_multiplier,
        }

    def evaluate_cohesion(self, state: BattleState) -> BattleState:
        return super().evaluate_cohesion(state)

def run_simulation(
    initial_state: BattleState,
    *,
    engine_cls: Any | None,
    execution_cfg: Mapping[str, Any],
    runtime_cfg: Mapping[str, Any],
    observer_cfg: Mapping[str, Any],
):
    if engine_cls is None:
        raise ValueError("run_simulation requires an explicit engine_cls")

    movement_cfg = _require_mapping(runtime_cfg, "movement")
    contact_cfg = _require_mapping(runtime_cfg, "contact")
    boundary_cfg = _require_mapping(runtime_cfg, "boundary")
    bridge_cfg = _require_mapping(observer_cfg, "bridge")
    collapse_shadow_cfg = _require_mapping(observer_cfg, "collapse_shadow")
    fixture_cfg = execution_cfg.get("fixture", {})
    if fixture_cfg is None:
        fixture_cfg = {}
    if not isinstance(fixture_cfg, Mapping):
        raise TypeError(f"run_simulation requires execution_cfg['fixture'] to be a mapping, got {type(fixture_cfg).__name__}")
    fixture_active_mode = str(fixture_cfg.get("active_mode", FIXTURE_MODE_BATTLE)).strip().lower() or FIXTURE_MODE_BATTLE
    if fixture_active_mode not in FIXTURE_MODE_LABELS:
        raise ValueError(
            f"run_simulation execution_cfg['fixture']['active_mode'] must be one of {sorted(FIXTURE_MODE_LABELS)}, "
            f"got {fixture_active_mode!r}"
        )
    fixture_active = fixture_active_mode == FIXTURE_MODE_NEUTRAL_TRANSIT_V1
    v4a_reference_surface_mode = str(
        movement_cfg.get("v4a_reference_surface_mode_effective", V4A_REFERENCE_SURFACE_MODE_RIGID_SLOTS)
    ).strip().lower()
    if v4a_reference_surface_mode not in V4A_REFERENCE_SURFACE_MODE_LABELS:
        raise ValueError(
            "run_simulation movement_cfg['v4a_reference_surface_mode_effective'] must be one of "
            f"{sorted(V4A_REFERENCE_SURFACE_MODE_LABELS)}, got {v4a_reference_surface_mode!r}"
        )
    v4a_soft_morphology_relaxation = float(
        movement_cfg.get("v4a_soft_morphology_relaxation_effective", V4A_SOFT_MORPHOLOGY_RELAXATION_DEFAULT)
    )
    if not 0.0 < v4a_soft_morphology_relaxation <= 1.0:
        raise ValueError(
            "run_simulation movement_cfg['v4a_soft_morphology_relaxation_effective'] must be within (0.0, 1.0], "
            f"got {v4a_soft_morphology_relaxation}"
        )
    v4a_shape_vs_advance_strength = float(
        movement_cfg.get("v4a_shape_vs_advance_strength_effective", V4A_SHAPE_VS_ADVANCE_STRENGTH_DEFAULT)
    )
    if not 0.0 <= v4a_shape_vs_advance_strength <= 1.0:
        raise ValueError(
            "run_simulation movement_cfg['v4a_shape_vs_advance_strength_effective'] must be within [0.0, 1.0], "
            f"got {v4a_shape_vs_advance_strength}"
        )
    v4a_heading_relaxation = float(
        movement_cfg.get("v4a_heading_relaxation_effective", V4A_HEADING_RELAXATION_DEFAULT)
    )
    if not 0.0 < v4a_heading_relaxation <= 1.0:
        raise ValueError(
            "run_simulation movement_cfg['v4a_heading_relaxation_effective'] must be within (0.0, 1.0], "
            f"got {v4a_heading_relaxation}"
        )
    v4a_battle_standoff_hold_band_ratio = float(
        movement_cfg.get(
            "v4a_battle_standoff_hold_band_ratio_effective",
            V4A_BATTLE_STANDOFF_HOLD_BAND_RATIO_DEFAULT,
        )
    )
    if not 0.0 <= v4a_battle_standoff_hold_band_ratio <= 1.0:
        raise ValueError(
            "run_simulation movement_cfg['v4a_battle_standoff_hold_band_ratio_effective'] must be within [0.0, 1.0], "
            f"got {v4a_battle_standoff_hold_band_ratio}"
        )
    v4a_battle_target_front_strip_gap_bias = float(
        movement_cfg.get(
            "v4a_battle_target_front_strip_gap_bias_effective",
            V4A_BATTLE_TARGET_FRONT_STRIP_GAP_BIAS_DEFAULT,
        )
    )
    if not math.isfinite(v4a_battle_target_front_strip_gap_bias):
        raise ValueError(
            "run_simulation movement_cfg['v4a_battle_target_front_strip_gap_bias_effective'] must be finite, "
            f"got {v4a_battle_target_front_strip_gap_bias}"
        )
    v4a_battle_hold_weight_strength = float(
        movement_cfg.get(
            "v4a_battle_hold_weight_strength_effective",
            V4A_BATTLE_HOLD_WEIGHT_STRENGTH_DEFAULT,
        )
    )
    if not 0.0 <= v4a_battle_hold_weight_strength <= 1.0:
        raise ValueError(
            "run_simulation movement_cfg['v4a_battle_hold_weight_strength_effective'] must be within [0.0, 1.0], "
            f"got {v4a_battle_hold_weight_strength}"
        )
    v4a_battle_relation_lead_ticks = float(
        movement_cfg.get(
            "v4a_battle_relation_lead_ticks_effective",
            V4A_BATTLE_RELATION_LEAD_TICKS_DEFAULT,
        )
    )
    if not math.isfinite(v4a_battle_relation_lead_ticks) or v4a_battle_relation_lead_ticks <= 0.0:
        raise ValueError(
            "run_simulation movement_cfg['v4a_battle_relation_lead_ticks_effective'] must be finite and > 0, "
            f"got {v4a_battle_relation_lead_ticks}"
        )
    v4a_battle_hold_relaxation = float(
        movement_cfg.get(
            "v4a_battle_hold_relaxation_effective",
            V4A_BATTLE_HOLD_RELAXATION_DEFAULT,
        )
    )
    if not 0.0 < v4a_battle_hold_relaxation <= 1.0:
        raise ValueError(
            "run_simulation movement_cfg['v4a_battle_hold_relaxation_effective'] must be within (0.0, 1.0], "
            f"got {v4a_battle_hold_relaxation}"
        )
    v4a_battle_approach_drive_relaxation = float(
        movement_cfg.get(
            "v4a_battle_approach_drive_relaxation_effective",
            V4A_BATTLE_APPROACH_DRIVE_RELAXATION_DEFAULT,
        )
    )
    if not 0.0 < v4a_battle_approach_drive_relaxation <= 1.0:
        raise ValueError(
            "run_simulation movement_cfg['v4a_battle_approach_drive_relaxation_effective'] must be within (0.0, 1.0], "
            f"got {v4a_battle_approach_drive_relaxation}"
        )
    v4a_battle_near_contact_internal_stability_blend = float(
        movement_cfg.get(
            "v4a_battle_near_contact_internal_stability_blend_effective",
            V4A_NEAR_CONTACT_INTERNAL_STABILITY_BLEND_DEFAULT,
        )
    )
    if not 0.0 <= v4a_battle_near_contact_internal_stability_blend <= 1.0:
        raise ValueError(
            "run_simulation movement_cfg['v4a_battle_near_contact_internal_stability_blend_effective'] must be within [0.0, 1.0], "
            f"got {v4a_battle_near_contact_internal_stability_blend}"
        )
    v4a_battle_near_contact_speed_relaxation = float(
        movement_cfg.get(
            "v4a_battle_near_contact_speed_relaxation_effective",
            V4A_NEAR_CONTACT_SPEED_RELAXATION_DEFAULT,
        )
    )
    if not 0.0 < v4a_battle_near_contact_speed_relaxation <= 1.0:
        raise ValueError(
            "run_simulation movement_cfg['v4a_battle_near_contact_speed_relaxation_effective'] must be within (0.0, 1.0], "
            f"got {v4a_battle_near_contact_speed_relaxation}"
        )
    v4a_engaged_speed_scale = float(
        movement_cfg.get("v4a_engaged_speed_scale_effective", V4A_ENGAGED_SPEED_SCALE_DEFAULT)
    )
    if not 0.0 < v4a_engaged_speed_scale <= 1.0:
        raise ValueError(
            "run_simulation movement_cfg['v4a_engaged_speed_scale_effective'] must be within (0.0, 1.0], "
            f"got {v4a_engaged_speed_scale}"
        )
    v4a_attack_speed_lateral_scale = float(
        movement_cfg.get(
            "v4a_attack_speed_lateral_scale_effective",
            V4A_ATTACK_SPEED_LATERAL_SCALE_DEFAULT,
        )
    )
    if not 0.0 < v4a_attack_speed_lateral_scale <= 1.0:
        raise ValueError(
            "run_simulation movement_cfg['v4a_attack_speed_lateral_scale_effective'] must be within (0.0, 1.0], "
            f"got {v4a_attack_speed_lateral_scale}"
        )
    v4a_attack_speed_backward_scale = float(
        movement_cfg.get(
            "v4a_attack_speed_backward_scale_effective",
            V4A_ATTACK_SPEED_BACKWARD_SCALE_DEFAULT,
        )
    )
    if not 0.0 <= v4a_attack_speed_backward_scale <= v4a_attack_speed_lateral_scale:
        raise ValueError(
            "run_simulation movement_cfg['v4a_attack_speed_backward_scale_effective'] must be within "
            f"[0.0, v4a_attack_speed_lateral_scale_effective], got backward={v4a_attack_speed_backward_scale}, "
            f"lateral={v4a_attack_speed_lateral_scale}"
        )
    fixture_fleet_id = ""
    fixture_objective_point_xy = (0.0, 0.0)
    fixture_objective_contract_3d: dict[str, Any] = {}
    fixture_stop_radius = 0.0
    if fixture_active:
        if len(initial_state.fleets) != 1:
            raise ValueError(
                "neutral_transit_v1 requires a single-fleet initial_state, "
                f"got fleet_ids={list(initial_state.fleets.keys())}"
            )
        fixture_fleet_id = str(fixture_cfg.get("fleet_id", next(iter(initial_state.fleets.keys())))).strip()
        if fixture_fleet_id not in initial_state.fleets:
            raise ValueError(
                "neutral_transit_v1 fixture fleet_id must exist in initial_state.fleets, "
                f"got {fixture_fleet_id!r}"
            )
        fixture_objective_contract_3d, projected_anchor_point_xy = _normalize_fixture_objective_contract_3d(
            fixture_cfg.get("objective_contract_3d")
        )
        fixture_objective_point_xy = projected_anchor_point_xy
        fixture_stop_radius = float(fixture_cfg.get("stop_radius", 0.0))
        if fixture_stop_radius < 0.0:
            raise ValueError(
                "neutral_transit_v1 execution_cfg['fixture']['stop_radius'] must be >= 0, "
                f"got {fixture_stop_radius}"
            )
    odw_posture_bias_cfg = movement_cfg.get("odw_posture_bias", {})
    if not isinstance(odw_posture_bias_cfg, Mapping):
        odw_posture_bias_cfg = {}
    hybrid_v2_cfg = contact_cfg.get("hybrid_v2", {})
    if not isinstance(hybrid_v2_cfg, Mapping):
        hybrid_v2_cfg = {}
    intent_unified_spacing_cfg = contact_cfg.get("intent_unified_spacing_v1", {})
    if not isinstance(intent_unified_spacing_cfg, Mapping):
        intent_unified_spacing_cfg = {}
    steps = int(execution_cfg["steps"])
    capture_positions = bool(execution_cfg["capture_positions"])
    capture_hit_points = bool(execution_cfg.get("capture_hit_points", False))
    frame_stride = int(execution_cfg["frame_stride"])
    include_target_lines = bool(execution_cfg["include_target_lines"])
    print_tick_summary = bool(execution_cfg["print_tick_summary"])
    observer_enabled = bool(observer_cfg["enabled"])
    tick_timing_enabled = bool(observer_cfg.get("tick_timing_enabled", True))
    post_elimination_extra_ticks = max(0, int(execution_cfg.get("post_elimination_extra_ticks", 10)))
    movement_model = str(runtime_cfg["movement_model"]).strip().lower() or "v3a"
    if movement_model not in {"v3a", "v4a"}:
        raise ValueError(
            "test_run maintained path only supports runtime_cfg['movement_model'] in {'v3a', 'v4a'}, "
            f"got {runtime_cfg['movement_model']!r}"
        )
    engine = engine_cls(
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
        (
            "HOSTILE_CONTACT_IMPEDANCE_MODE",
            str(contact_cfg.get("hostile_contact_impedance_mode", HOSTILE_CONTACT_IMPEDANCE_MODE_DEFAULT)).strip().lower()
            or HOSTILE_CONTACT_IMPEDANCE_MODE_DEFAULT,
        ),
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
        (
            "HOSTILE_INTENT_UNIFIED_SPACING_SCALE",
            max(1e-6, float(intent_unified_spacing_cfg.get("scale", HOSTILE_INTENT_UNIFIED_SPACING_SCALE_DEFAULT))),
        ),
        (
            "HOSTILE_INTENT_UNIFIED_SPACING_STRENGTH",
            _clamp01(float(intent_unified_spacing_cfg.get("strength", HOSTILE_INTENT_UNIFIED_SPACING_STRENGTH_DEFAULT))),
        ),
        ("V2_CONNECT_RADIUS_MULTIPLIER", max(1e-12, float(movement_cfg.get("v2_connect_radius_multiplier", 1.0)))),
        ("V3_CONNECT_RADIUS_MULTIPLIER", max(1e-12, float(movement_cfg.get("v3_connect_radius_multiplier_effective", 1.0)))),
        ("V3_R_REF_RADIUS_MULTIPLIER", max(1e-12, float(movement_cfg.get("v3_r_ref_radius_multiplier_effective", 1.0)))),
    ):
        setattr(engine, attr, value)

    engine.runtime_cohesion_decision_source = str(runtime_cfg["decision_source"]).strip().lower() or "v2"
    movement_surface = getattr(engine, "_movement_surface", None)
    if not isinstance(movement_surface, dict):
        raise TypeError("EngineTickSkeleton._movement_surface missing or invalid")
    movement_surface["alpha_sep"] = max(0.0, float(contact_cfg["alpha_sep"]))
    movement_surface["model"] = movement_model
    if movement_model == "v4a":
        v4a_restore_strength = float(movement_cfg.get("v4a_restore_strength_effective", 0.25))
        movement_surface["v4a_restore_strength"] = v4a_restore_strength
        movement_surface["v3a_experiment"] = V3A_EXPERIMENT_BASE
        movement_surface["centroid_probe_scale"] = 1.0
    else:
        movement_surface["v4a_restore_strength"] = 1.0
        movement_surface["v3a_experiment"] = (
            str(movement_cfg.get("experiment_effective", "base")).strip().lower() or "base"
        )
        movement_surface["centroid_probe_scale"] = float(movement_cfg.get("centroid_probe_scale_effective", 1.0))
    movement_surface["odw_posture_bias_enabled"] = bool(odw_posture_bias_cfg.get("enabled_effective", False))
    movement_surface["odw_posture_bias_k"] = max(0.0, float(odw_posture_bias_cfg.get("k_effective", 0.0)))
    movement_surface["odw_posture_bias_clip_delta"] = max(
        0.0,
        float(odw_posture_bias_cfg.get("clip_delta_effective", 0.2)),
    )

    combat_surface = getattr(engine, "_combat_surface", None)
    if not isinstance(combat_surface, dict):
        raise TypeError("EngineTickSkeleton._combat_surface missing or invalid")
    combat_surface["fire_quality_alpha"] = float(contact_cfg["fire_quality_alpha"])
    combat_surface["fire_optimal_range_ratio"] = float(contact_cfg["fire_optimal_range_ratio"])
    combat_surface["contact_hysteresis_h"] = float(contact_cfg["contact_hysteresis_h"])
    combat_surface["ch_enabled"] = bool(contact_cfg["ch_enabled"])

    fsr_surface = getattr(engine, "_fsr_surface", None)
    if not isinstance(fsr_surface, dict):
        raise TypeError("EngineTickSkeleton._fsr_surface missing or invalid")
    fsr_surface["enabled"] = bool(contact_cfg["fsr_enabled"]) and not (fixture_active and movement_model == "v4a")
    fsr_surface["strength"] = float(contact_cfg["fsr_strength"])

    boundary_surface = getattr(engine, "_boundary_surface", None)
    if not isinstance(boundary_surface, dict):
        raise TypeError("EngineTickSkeleton._boundary_surface missing or invalid")
    boundary_surface["soft_enabled"] = bool(boundary_cfg["enabled"])
    boundary_surface["hard_enabled"] = bool(boundary_cfg["enabled"]) and bool(boundary_cfg["hard_enabled"])
    boundary_surface["soft_strength"] = max(0.0, float(boundary_cfg["soft_strength"]))

    diagnostics_enabled = bool(observer_enabled) or bool(execution_cfg["plot_diagnostics_enabled"])
    observer_active = bool(diagnostics_enabled) and (
        bool(capture_positions) or bool(observer_cfg.get("runtime_diag_enabled", False))
    )
    diag_surface = getattr(engine, "_diag_surface", None)
    if not isinstance(diag_surface, dict):
        raise TypeError("EngineTickSkeleton._diag_surface missing or invalid")
    diag_surface["fsr_diag_enabled"] = observer_active
    diag_surface["diag4_enabled"] = observer_active

    state = replace(
        initial_state,
        last_target_direction={
            fleet_id: initial_state.last_target_direction.get(fleet_id, (0.0, 0.0))
            for fleet_id in initial_state.fleets
        },
        last_engagement_intensity={
            fleet_id: initial_state.last_engagement_intensity.get(fleet_id, 0.0)
            for fleet_id in initial_state.fleets
        },
    )
    fleet_ids = tuple(state.fleets)

    def _per_fleet_series() -> dict[str, list]:
        return {fleet_id: [] for fleet_id in fleet_ids}

    def _compute_centroid_and_rms_radius(position_map: Mapping[str, tuple[float, float]]) -> tuple[float, float, float]:
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

    v4a_bundle_profile = {
        "shape": {
            "expected_reference_spacing": float(
                movement_cfg.get("expected_reference_spacing_effective", 1.0)
            ),
            "reference_layout_mode": str(
                movement_cfg.get(
                    "reference_layout_mode_effective",
                    V4A_REFERENCE_LAYOUT_MODE_RECT_CENTERED_4_0,
                )
            ),
            "reference_surface_mode": str(v4a_reference_surface_mode),
            "soft_morphology_relaxation": float(v4a_soft_morphology_relaxation),
            "shape_vs_advance_strength": float(v4a_shape_vs_advance_strength),
            "heading_relaxation": float(v4a_heading_relaxation),
        },
        "battle": {
            "battle_standoff_hold_band_ratio": float(
                v4a_battle_standoff_hold_band_ratio
            ),
            "battle_target_front_strip_gap_bias": float(
                v4a_battle_target_front_strip_gap_bias
            ),
            "battle_hold_weight_strength": float(v4a_battle_hold_weight_strength),
            "battle_relation_lead_ticks": float(v4a_battle_relation_lead_ticks),
            "battle_hold_relaxation": float(v4a_battle_hold_relaxation),
            "battle_approach_drive_relaxation": float(
                v4a_battle_approach_drive_relaxation
            ),
            "battle_near_contact_internal_stability_blend": float(
                v4a_battle_near_contact_internal_stability_blend
            ),
            "battle_near_contact_speed_relaxation": float(
                v4a_battle_near_contact_speed_relaxation
            ),
        },
        "motion": {
            "engaged_speed_scale": float(v4a_engaged_speed_scale),
            "attack_speed_lateral_scale": float(v4a_attack_speed_lateral_scale),
            "attack_speed_backward_scale": float(v4a_attack_speed_backward_scale),
        },
    }

    def _build_fixture_expected_reference_bundle(
        position_map: Mapping[str, tuple[float, float]],
        objective_point_xy: tuple[float, float],
        *,
        ordered_unit_ids: Sequence[str] | None = None,
        v4a_profile: Mapping[str, Any],
        fallback_axis_xy: tuple[float, float] = (1.0, 0.0),
    ) -> dict:
        shape_cfg = _require_mapping(v4a_profile, "shape")
        battle_cfg = _require_mapping(v4a_profile, "battle")
        motion_cfg = _require_mapping(v4a_profile, "motion")
        expected_reference_spacing = float(shape_cfg["expected_reference_spacing"])
        reference_layout_mode = str(shape_cfg["reference_layout_mode"])
        centroid_x, centroid_y, _ = _compute_centroid_and_rms_radius(position_map)
        if not math.isfinite(centroid_x) or not math.isfinite(centroid_y):
            raise ValueError("neutral_transit_v1 expected-position reference requires at least one alive unit")
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
        band_identity_by_unit = _assign_soft_morphology_band_identity(actual_offsets_local)
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
            "movement_heading_current_xy": primary_axis_xy,
            "shape_error_current": 0.0,
            "actual_forward_extent": float(forward_extent_initial),
            "actual_lateral_extent": float(lateral_extent_initial),
            "hold_within_stop_radius": False,
            "initial_material_forward_phase_by_unit": {
                str(unit_id): float(phase)
                for unit_id, phase in initial_forward_phase_by_unit.items()
            },
            "initial_material_lateral_phase_by_unit": {
                str(unit_id): float(phase)
                for unit_id, phase in initial_lateral_phase_by_unit.items()
            },
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
            "band_identity_by_unit": {
                str(unit_id): (int(bands[0]), int(bands[1]))
                for unit_id, bands in band_identity_by_unit.items()
            },
        }

    def _compute_expected_position_rms_error(
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

    def _compute_front_extent_ratio(
        position_map: Mapping[str, tuple[float, float]],
        objective_point_xy: tuple[float, float],
        initial_front_extent: float,
        fallback_axis_xy: tuple[float, float],
    ) -> float:
        if not position_map:
            return float("nan")
        centroid_x, centroid_y, _ = _compute_centroid_and_rms_radius(position_map)
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

    battle_restore_bundles_by_fleet: dict[str, dict[str, Any]] = {}
    if movement_model == "v4a":
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
            fleet_centroid_x, fleet_centroid_y, _ = _compute_centroid_and_rms_radius(fleet_positions)
            enemy_centroid_x, enemy_centroid_y, _ = _compute_centroid_and_rms_radius(enemy_positions)
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
            bundle = _build_fixture_expected_reference_bundle(
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
            bundle["hold_stop_radius"] = 0.0
            battle_restore_bundles_by_fleet[str(fleet_id)] = bundle
    if battle_restore_bundles_by_fleet:
        engine.TEST_RUN_BATTLE_RESTORE_BUNDLES_BY_FLEET = battle_restore_bundles_by_fleet

    trajectory = _per_fleet_series()
    alive_trajectory = _per_fleet_series()
    fleet_size_trajectory = _per_fleet_series()
    observer_telemetry = {
        **{
            key: _per_fleet_series()
            for key in (
                "cohesion_v3",
                "c_conn",
                "c_scale",
                "rho",
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
        fixture_reference_bundle = _build_fixture_expected_reference_bundle(
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
        fixture_reference_bundle["hold_stop_radius"] = float(fixture_stop_radius)
        engine.TEST_RUN_FIXTURE_REFERENCE_BUNDLE = fixture_reference_bundle
        initial_centroid_x, initial_centroid_y, initial_rms_radius = _compute_centroid_and_rms_radius(initial_positions)
        initial_distance = math.sqrt(
            ((initial_centroid_x - fixture_objective_point_xy[0]) ** 2)
            + ((initial_centroid_y - fixture_objective_point_xy[1]) ** 2)
        ) if math.isfinite(initial_centroid_x) and math.isfinite(initial_centroid_y) else float("nan")
        fixture_candidate_a_active = movement_model == "v4a"
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
        if movement_model == "v4a":
            battle_restore_bundles_by_fleet[str(fixture_fleet_id)] = fixture_reference_bundle
    if battle_restore_bundles_by_fleet:
        engine.TEST_RUN_BATTLE_RESTORE_BUNDLES_BY_FLEET = battle_restore_bundles_by_fleet
    combat_telemetry = {
        "in_contact_count": [],
        "damage_events_count": [],
    }
    bridge_telemetry = {
        "theta_split": float(bridge_cfg["theta_split"]),
        "theta_env": float(bridge_cfg["theta_env"]),
        "sustain_ticks": int(bridge_cfg["sustain_ticks"]),
        **{
            key: _per_fleet_series()
            for key in (
                "AR",
                "wedge_ratio",
                "split_separation",
                "angle_coverage",
                "split_cond",
                "env_cond",
                "split_sustain_counter",
                "env_sustain_counter",
                "bridge_event_cut",
                "bridge_event_pocket",
            )
        },
        "first_tick_split_sustain": {fleet_id: None for fleet_id in fleet_ids},
        "first_tick_env_sustain": {fleet_id: None for fleet_id in fleet_ids},
    }
    split_counter_state = {fleet_id: 0 for fleet_id in fleet_ids}
    env_counter_state = {fleet_id: 0 for fleet_id in fleet_ids}
    position_frames = []
    center_wing_interval_ticks = int(observer_telemetry.get("center_wing_advance_gap_interval_ticks", 10))
    center_wing_position_history = _per_fleet_series()
    posture_persistence_state = {fleet_id: {"sign": 0, "length": 0} for fleet_id in fleet_ids}

    def _build_focus_indicator_payload(current_state: BattleState) -> dict[str, dict[str, float]]:
        if movement_model != "v4a":
            return {}
        focus_payload: dict[str, dict[str, float]] = {}
        bundle_entries: dict[str, Mapping[str, Any]] = {}
        if fixture_active and fixture_active_mode == FIXTURE_MODE_NEUTRAL_TRANSIT_V1:
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
                    centroid_a_x, centroid_a_y, rms_a = _compute_centroid_and_rms_radius(
                        {
                            str(unit.unit_id): (float(unit.position.x), float(unit.position.y))
                            for unit in units_a
                        }
                    )
                    centroid_b_x, centroid_b_y, rms_b = _compute_centroid_and_rms_radius(
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
                "advance_share": float(bundle.get("transition_advance_share", float("nan"))),
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
        runtime_debug = extract_runtime_debug_payload(
            getattr(engine, "debug_diag_last_tick", {}) if observer_active else {}
        )
        focus_indicators = _build_focus_indicator_payload(current_state)
        if focus_indicators:
            runtime_debug["focus_indicators"] = focus_indicators
        frame["runtime_debug"] = runtime_debug
        position_frames.append(frame)

    if steps <= 0:
        tick_limit = 999
        elimination_tick = None
        post_elimination_stop_tick = None
    else:
        tick_limit = steps
        elimination_tick = None
        post_elimination_stop_tick = None

    while state.tick < tick_limit:
        tick_start_time = time.perf_counter() if tick_timing_enabled else None
        state = engine.step(state)
        if tick_timing_enabled and tick_start_time is not None:
            observer_telemetry["tick_elapsed_ms"].append((time.perf_counter() - tick_start_time) * 1000.0)
        combat_stats = getattr(engine, "debug_last_combat_stats", {})
        if not isinstance(combat_stats, dict):
            combat_stats = {}
        combat_telemetry["in_contact_count"].append(int(combat_stats.get("in_contact_count", 0)))
        combat_telemetry["damage_events_count"].append(int(combat_stats.get("damage_events_count", 0)))
        contact_active_tick = int(combat_stats.get("in_contact_count", 0)) > 0

        if print_tick_summary:
            ordered_fleet_ids = [fleet_id for fleet_id in ("A", "B") if fleet_id in state.fleets]
            if not ordered_fleet_ids:
                ordered_fleet_ids = sorted(state.fleets.keys())
            if len(ordered_fleet_ids) >= 2:
                fleet_a = state.fleets[ordered_fleet_ids[0]]
                fleet_b = state.fleets[ordered_fleet_ids[1]]
                name_a = str(getattr(fleet_a.parameters, "archetype_id", "") or ordered_fleet_ids[0])
                name_b = str(getattr(fleet_b.parameters, "archetype_id", "") or ordered_fleet_ids[1])
                print(f"t={state.tick}, [{name_a}] vs [{name_b}], {len(fleet_a.unit_ids)}/{len(fleet_b.unit_ids)}")
            elif len(ordered_fleet_ids) == 1:
                fleet = state.fleets[ordered_fleet_ids[0]]
                name = str(getattr(fleet.parameters, "archetype_id", "") or ordered_fleet_ids[0])
                print(f"t={state.tick}, [{name}], {len(fleet.unit_ids)}")

        current_unit_position_maps: dict[str, dict[str, tuple[float, float]]] = {}
        for fleet_id, fleet in state.fleets.items():
            trajectory[fleet_id].append(state.last_fleet_cohesion.get(fleet_id, 1.0))
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
            centroid_x, centroid_y, rms_radius = _compute_centroid_and_rms_radius(fixture_positions)
            if math.isfinite(centroid_x) and math.isfinite(centroid_y):
                distance_to_objective = math.sqrt(
                    ((centroid_x - fixture_objective_point_xy[0]) ** 2)
                    + ((centroid_y - fixture_objective_point_xy[1]) ** 2)
                )
            else:
                distance_to_objective = float("nan")
            fixture_runtime_debug = extract_runtime_debug_payload(
                getattr(engine, "debug_diag_last_tick", {}) if observer_active else {}
            )
            fixture_runtime_diag_tick = getattr(engine, "debug_diag_last_tick", {}) if observer_active else {}
            if isinstance(fixture_runtime_diag_tick, dict):
                fixture_decomposition_trace = fixture_runtime_diag_tick.get("fixture_terminal_trace")
                if isinstance(fixture_decomposition_trace, dict):
                    trace_units = fixture_decomposition_trace.get("units")
                    if isinstance(trace_units, dict):
                        fixture_metrics["late_terminal_decomposition_trace"].append(
                            {
                                "tick": int(fixture_runtime_diag_tick.get("tick", state.tick)),
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
                target_direction=state.last_target_direction.get(fixture_fleet_id, (0.0, 0.0)),
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
                _compute_expected_position_rms_error(fixture_positions, expected_position_map)
            )
            fixture_metrics["front_extent_ratio"].append(
                _compute_front_extent_ratio(
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
                float(fixture_reference_bundle.get("transition_advance_share", 1.0))
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
            fixture_reference_bundle["formation_terminal_active"] = False
            fixture_reference_bundle["formation_terminal_latched_tick"] = None
            fixture_reference_bundle["formation_terminal_axis_xy"] = None
            fixture_reference_bundle["formation_terminal_center_xy"] = None
            fixture_reference_bundle["formation_hold_active"] = False
            fixture_reference_bundle["formation_hold_latched_tick"] = None
            fixture_reference_bundle["formation_hold_axis_xy"] = None
            fixture_reference_bundle["formation_hold_center_xy"] = None
            fixture_reference_bundle["formation_hold_forward_extent"] = None
            fixture_reference_bundle["formation_hold_lateral_extent"] = None
            fixture_reference_bundle["formation_hold_center_wing_differential"] = None
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

        runtime_v3 = getattr(engine, "debug_last_cohesion_v3", {})
        if not isinstance(runtime_v3, dict):
            runtime_v3 = {}
        runtime_v3_components = getattr(engine, "debug_last_cohesion_v3_components", {})
        if not isinstance(runtime_v3_components, dict):
            runtime_v3_components = {}
        for fleet_id in state.fleets:
            fallback_v2 = float(state.last_fleet_cohesion.get(fleet_id, 1.0))
            cohesion_v3 = float(runtime_v3.get(fleet_id, fallback_v2)) if diagnostics_enabled else float("nan")
            comp = runtime_v3_components.get(fleet_id, {})
            if not isinstance(comp, dict):
                comp = {}
            observer_telemetry["cohesion_v3"][fleet_id].append(cohesion_v3)
            observer_telemetry["c_conn"][fleet_id].append(float(comp.get("c_conn", float("nan"))))
            observer_telemetry["c_scale"][fleet_id].append(float(comp.get("c_scale", float("nan"))))
            observer_telemetry["rho"][fleet_id].append(float(comp.get("rho", float("nan"))))

        bridge_metrics = compute_bridge_metrics_per_side(state)
        for fleet_id in state.fleets:
            if diagnostics_enabled:
                metric = bridge_metrics.get(fleet_id, {})
                ar_value = float(metric.get("AR", float("nan")))
                wedge_value = float(metric.get("wedge_ratio", float("nan")))
                split_value = float(metric.get("split_separation", 0.0))
                env_value = float(metric.get("angle_coverage", 0.0))
                split_cond = bool(
                    state.tick >= 1 and contact_active_tick and split_value >= float(bridge_cfg["theta_split"])
                )
                env_cond = bool(
                    state.tick >= 1 and contact_active_tick and env_value >= float(bridge_cfg["theta_env"])
                )
            else:
                ar_value = float("nan")
                wedge_value = float("nan")
                split_value = float("nan")
                env_value = float("nan")
                split_cond = False
                env_cond = False

            if split_cond:
                split_counter_state[fleet_id] = int(split_counter_state.get(fleet_id, 0)) + 1
            else:
                split_counter_state[fleet_id] = 0
            if env_cond:
                env_counter_state[fleet_id] = int(env_counter_state.get(fleet_id, 0)) + 1
            else:
                env_counter_state[fleet_id] = 0

            cut_event_tick = False
            pocket_event_tick = False
            if (
                split_counter_state[fleet_id] >= int(bridge_cfg["sustain_ticks"])
                and bridge_telemetry["first_tick_split_sustain"].get(fleet_id) is None
            ):
                bridge_telemetry["first_tick_split_sustain"][fleet_id] = int(state.tick)
                cut_event_tick = True
            if (
                env_counter_state[fleet_id] >= int(bridge_cfg["sustain_ticks"])
                and bridge_telemetry["first_tick_env_sustain"].get(fleet_id) is None
            ):
                bridge_telemetry["first_tick_env_sustain"][fleet_id] = int(state.tick)
                pocket_event_tick = True

            for metric_key, metric_value in (
                ("AR", ar_value),
                ("wedge_ratio", wedge_value),
                ("split_separation", split_value),
                ("angle_coverage", env_value),
                ("split_cond", bool(split_cond)),
                ("env_cond", bool(env_cond)),
                ("split_sustain_counter", int(split_counter_state[fleet_id])),
                ("env_sustain_counter", int(env_counter_state[fleet_id])),
                ("bridge_event_cut", bool(cut_event_tick)),
                ("bridge_event_pocket", bool(pocket_event_tick)),
            ):
                bridge_telemetry[metric_key][fleet_id].append(metric_value)

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

    if fixture_active:
        return (
            state,
            trajectory,
            alive_trajectory,
            fleet_size_trajectory,
            observer_telemetry,
            combat_telemetry,
            bridge_telemetry,
            {},
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

    collapse_shadow_telemetry = compute_collapse_v2_shadow_telemetry(
        observer_enabled=diagnostics_enabled,
        observer_telemetry=observer_telemetry,
        alive_trajectory=alive_trajectory,
        theta_conn_default=float(collapse_shadow_cfg["theta_conn_default"]),
        theta_coh_default=float(collapse_shadow_cfg["theta_coh_default"]),
        theta_force_default=float(collapse_shadow_cfg["theta_force_default"]),
        theta_attr_default=float(collapse_shadow_cfg["theta_attr_default"]),
        attrition_window=int(collapse_shadow_cfg["attrition_window"]),
        sustain_ticks=int(collapse_shadow_cfg["sustain_ticks"]),
        min_conditions=int(collapse_shadow_cfg["min_conditions"]),
    )

    return (
        state,
        trajectory,
        alive_trajectory,
        fleet_size_trajectory,
        observer_telemetry,
        combat_telemetry,
        bridge_telemetry,
        collapse_shadow_telemetry,
        position_frames,
    )
