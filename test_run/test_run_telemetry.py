import math
from collections.abc import Mapping

from runtime.runtime_v0_1 import BattleState


def _clamp01(value: float) -> float:
    return min(1.0, max(0.0, value))


def compute_hostile_intermix_metrics(
    state: BattleState,
    separation_radius: float,
) -> dict[str, float]:
    alive_units = [
        unit for unit in state.units.values() if float(unit.hit_points) > 0.0
    ]
    if len(alive_units) <= 1 or separation_radius <= 1e-12:
        return {
            "hostile_overlap_pairs": 0.0,
            "hostile_deep_pairs": 0.0,
            "hostile_deep_intermix_ratio": 0.0,
            "hostile_intermix_severity": 0.0,
            "hostile_intermix_coverage": 0.0,
        }

    alive_counts_by_fleet: dict[str, int] = {}
    overlapped_units_by_fleet: dict[str, set[str]] = {}
    for unit in alive_units:
        fleet_id = str(unit.fleet_id)
        alive_counts_by_fleet[fleet_id] = alive_counts_by_fleet.get(fleet_id, 0) + 1
        overlapped_units_by_fleet.setdefault(fleet_id, set())
    overlap_pairs = 0
    deep_pairs = 0
    severity_sum = 0.0
    deep_threshold = 0.5 * float(separation_radius)
    radius_sq = float(separation_radius) * float(separation_radius)
    for i in range(len(alive_units)):
        unit_i = alive_units[i]
        for j in range(i + 1, len(alive_units)):
            unit_j = alive_units[j]
            if unit_i.fleet_id == unit_j.fleet_id:
                continue
            dx = float(unit_i.position.x) - float(unit_j.position.x)
            dy = float(unit_i.position.y) - float(unit_j.position.y)
            distance_sq = (dx * dx) + (dy * dy)
            if distance_sq >= radius_sq:
                continue
            distance = math.sqrt(max(0.0, distance_sq))
            overlap_pairs += 1
            overlapped_units_by_fleet.setdefault(str(unit_i.fleet_id), set()).add(str(unit_i.unit_id))
            overlapped_units_by_fleet.setdefault(str(unit_j.fleet_id), set()).add(str(unit_j.unit_id))
            if distance < deep_threshold:
                deep_pairs += 1
            penetration = _clamp01((float(separation_radius) - distance) / float(separation_radius))
            severity_sum += penetration * penetration

    coverage_components: list[float] = []
    for fleet_id, alive_count in alive_counts_by_fleet.items():
        if alive_count <= 0:
            continue
        overlapped_count = len(overlapped_units_by_fleet.get(fleet_id, set()))
        coverage_components.append(float(overlapped_count) / float(alive_count))

    return {
        "hostile_overlap_pairs": float(overlap_pairs),
        "hostile_deep_pairs": float(deep_pairs),
        "hostile_deep_intermix_ratio": float(deep_pairs) / float(max(1, overlap_pairs)),
        "hostile_intermix_severity": severity_sum / float(max(1, overlap_pairs)),
        "hostile_intermix_coverage": (
            sum(coverage_components) / float(len(coverage_components))
            if coverage_components
            else 0.0
        ),
    }


def extract_runtime_debug_payload(diag_tick: dict) -> dict:
    if not isinstance(diag_tick, dict):
        return {}
    projection = diag_tick.get("projection", {})
    if not isinstance(projection, dict):
        projection = {}
    combat = diag_tick.get("combat", {})
    if not isinstance(combat, dict):
        combat = {}
    boundary_soft = diag_tick.get("boundary_soft", {})
    if not isinstance(boundary_soft, dict):
        boundary_soft = {}
    legality = diag_tick.get("legality", {})
    if not isinstance(legality, dict):
        legality = {}

    payload = {
        "tick": int(diag_tick.get("tick", 0)),
        "projection_max_displacement": float(projection.get("max_projection_displacement", 0.0)),
        "projection_mean_displacement": float(projection.get("mean_projection_displacement", 0.0)),
        "corrected_unit_ratio": float(projection.get("corrected_unit_ratio", 0.0)),
        "projection_pairs_count": int(projection.get("projection_pairs_count", 0)),
        "in_contact_count": int(combat.get("in_contact_count", 0)),
        "damage_events_count": int(combat.get("damage_events_count", 0)),
        "boundary_force_events_tick": int(boundary_soft.get("boundary_force_events_count_tick", 0)),
        "legality_reference_surface_count": int(legality.get("reference_surface_count", 0)),
        "legality_feasible_surface_count": int(legality.get("feasible_surface_count", 0)),
        "legality_middle_stage_active": bool(legality.get("middle_stage_active", False)),
        "legality_handoff_ready": bool(legality.get("handoff_ready", False)),
    }
    return payload
