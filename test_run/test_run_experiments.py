import math
from collections.abc import Mapping, Sequence
from dataclasses import replace
from typing import Any

from runtime.runtime_v0_1 import (
    BattleState,
    FleetState,
    PersonalityParameters,
    UnitState,
    Vec2,
    build_initial_cohesion_map,
)


DEFAULT_DT = 1.0
DEFAULT_SPAWN_MARGIN_RATIO = 0.05
PRE_TL_TARGET_SUBSTRATE_DEFAULT = "nearest5_centroid"
HOSTILE_CONTACT_IMPEDANCE_MODE_DEFAULT = "off"
HOSTILE_CONTACT_IMPEDANCE_V2_RADIUS_MULTIPLIER_DEFAULT = 1.50
HOSTILE_CONTACT_IMPEDANCE_V2_REPULSION_MAX_DISP_RATIO_DEFAULT = 0.20
HOSTILE_CONTACT_IMPEDANCE_V2_FORWARD_DAMPING_STRENGTH_DEFAULT = 0.50
HOSTILE_INTENT_UNIFIED_SPACING_SCALE_DEFAULT = 1.00
HOSTILE_INTENT_UNIFIED_SPACING_STRENGTH_DEFAULT = 1.00
CONTINUOUS_FR_SHAPING_OFF = "off"
BRIDGE_EPSILON = 1e-9


def _clamp01(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return value

def _compute_hostile_intermix_metrics(
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
    outliers = diag_tick.get("outliers", {})
    if not isinstance(outliers, dict):
        outliers = {}
    projection = diag_tick.get("projection", {})
    if not isinstance(projection, dict):
        projection = {}
    combat = diag_tick.get("combat", {})
    if not isinstance(combat, dict):
        combat = {}
    boundary_soft = diag_tick.get("boundary_soft", {})
    if not isinstance(boundary_soft, dict):
        boundary_soft = {}
    persistent_ids = diag_tick.get("persistent_outlier_unit_ids", [])
    if not isinstance(persistent_ids, list):
        persistent_ids = []

    payload = {
        "tick": int(diag_tick.get("tick", 0)),
        "outlier_total": 0,
        "persistent_outlier_total": int(len(persistent_ids)),
        "max_outlier_persistence": int(diag_tick.get("max_outlier_persistence", 0)),
        "projection_max_displacement": float(projection.get("max_projection_displacement", 0.0)),
        "projection_mean_displacement": float(projection.get("mean_projection_displacement", 0.0)),
        "projection_pairs_count": int(projection.get("projection_pairs_count", 0)),
        "in_contact_count": int(combat.get("in_contact_count", 0)),
        "damage_events_count": int(combat.get("damage_events_count", 0)),
        "boundary_force_events_tick": int(boundary_soft.get("boundary_force_events_count_tick", 0)),
        "fleets": {},
    }

    for fleet_id in ("A", "B"):
        fleet_payload = outliers.get(fleet_id, {})
        if not isinstance(fleet_payload, dict):
            fleet_payload = {}
        outlier_count = int(fleet_payload.get("outlier_count", 0))
        payload["outlier_total"] += outlier_count
        payload["fleets"][fleet_id] = {
            "outlier_count": outlier_count,
            "max_outlier_persistence": int(fleet_payload.get("max_outlier_persistence", 0)),
            "r_rms": float(fleet_payload.get("r_rms", 0.0)),
            "outlier_threshold": float(fleet_payload.get("outlier_threshold", 0.0)),
        }
    return payload

def clamp(v: float, lo: float, hi: float) -> float:
    if v < lo:
        return lo
    if v > hi:
        return hi
    return v

def _direction_from_angle_deg(angle_deg: float) -> tuple[float, float]:
    theta = math.radians(float(angle_deg))
    return (math.cos(theta), math.sin(theta))

def _resolve_initial_formation_layout(unit_count: int, aspect_ratio: float) -> list[int]:
    grid_columns = max(1, int((unit_count * aspect_ratio) ** 0.5))
    grid_rows = (unit_count + grid_columns - 1) // grid_columns
    while grid_columns / max(1, grid_rows) < aspect_ratio and grid_columns < unit_count:
        grid_columns += 1
        grid_rows = (unit_count + grid_columns - 1) // grid_columns
    row_counts = []
    remaining = int(unit_count)
    for _ in range(grid_rows):
        row_count = min(grid_columns, remaining)
        row_counts.append(int(row_count))
        remaining -= row_count
    return row_counts

def _mean_xy(points: list[tuple[float, float]]) -> tuple[float, float]:
    if not points:
        return (0.0, 0.0)
    sx = 0.0
    sy = 0.0
    for x, y in points:
        sx += float(x)
        sy += float(y)
    n = float(len(points))
    return (sx / n, sy / n)

def _std_population(values: list[float]) -> float:
    if not values:
        return 0.0
    n = float(len(values))
    mean_v = sum(values) / n
    var = sum((float(v) - mean_v) ** 2 for v in values) / n
    return math.sqrt(max(0.0, var))

def _deterministic_kmeans_1d(values: list[float], max_iters: int = 32) -> tuple[list[float], list[float]]:
    if len(values) <= 1:
        return (list(values), [])
    c1 = min(values)
    c2 = max(values)
    if abs(c2 - c1) <= BRIDGE_EPSILON:
        ordered = sorted(values)
        mid = max(1, len(ordered) // 2)
        return (ordered[:mid], ordered[mid:])
    group1: list[float] = []
    group2: list[float] = []
    for _ in range(max_iters):
        group1 = []
        group2 = []
        for v in values:
            d1 = abs(v - c1)
            d2 = abs(v - c2)
            if d1 <= d2:
                group1.append(float(v))
            else:
                group2.append(float(v))
        if not group1 or not group2:
            ordered = sorted(values)
            mid = max(1, len(ordered) // 2)
            return (ordered[:mid], ordered[mid:])
        new_c1 = sum(group1) / float(len(group1))
        new_c2 = sum(group2) / float(len(group2))
        if abs(new_c1 - c1) <= BRIDGE_EPSILON and abs(new_c2 - c2) <= BRIDGE_EPSILON:
            break
        c1 = new_c1
        c2 = new_c2
    return (group1, group2)

def compute_formation_snapshot_metrics(
    side_points: list[tuple[float, float]],
    enemy_points: list[tuple[float, float]],
    angle_bins: int = 12,
) -> dict:
    result = {
        "AR": 1.0,
        "AR_forward": 1.0,
        "AreaScale": 0.0,
        "orientation_theta": 0.0,
        "major_axis_alignment": 0.0,
        "split_separation": 0.0,
        "angle_coverage": 0.0,
        "wedge_ratio": 1.0,
        "centroid_x": 0.0,
        "centroid_y": 0.0,
    }
    if not side_points:
        return result
    cx, cy = _mean_xy(side_points)
    result["centroid_x"] = cx
    result["centroid_y"] = cy

    if len(side_points) == 1:
        if enemy_points:
            ex, ey = _mean_xy(enemy_points)
            angle = math.atan2(side_points[0][1] - ey, side_points[0][0] - ex)
            if angle < 0.0:
                angle += 2.0 * math.pi
            if angle_bins > 0:
                result["angle_coverage"] = 1.0 / float(angle_bins)
        return result

    n = float(len(side_points))
    var_x = 0.0
    var_y = 0.0
    cov_xy = 0.0
    for x, y in side_points:
        dx = float(x) - cx
        dy = float(y) - cy
        var_x += dx * dx
        var_y += dy * dy
        cov_xy += dx * dy
    var_x /= n
    var_y /= n
    cov_xy /= n

    trace = var_x + var_y
    delta_sq = (var_x - var_y) ** 2 + 4.0 * (cov_xy ** 2)
    delta = math.sqrt(max(0.0, delta_sq))
    lam1 = max(0.0, 0.5 * (trace + delta))
    lam2 = max(0.0, 0.5 * (trace - delta))

    if abs(cov_xy) > BRIDGE_EPSILON or abs(lam1 - var_y) > BRIDGE_EPSILON:
        evx = lam1 - var_y
        evy = cov_xy
    else:
        evx = 1.0
        evy = 0.0
    norm = math.sqrt(evx * evx + evy * evy)
    if norm <= BRIDGE_EPSILON:
        ux = 1.0
        uy = 0.0
    else:
        ux = evx / norm
        uy = evy / norm
    vx = -uy
    vy = ux

    sigma1 = math.sqrt(lam1)
    sigma2 = math.sqrt(lam2)
    result["AR"] = sigma1 / (sigma2 + BRIDGE_EPSILON)
    result["AreaScale"] = sigma1 * sigma2
    result["orientation_theta"] = math.atan2(uy, ux)

    u_values: list[float] = []
    v_values: list[float] = []
    for x, y in side_points:
        dx = float(x) - cx
        dy = float(y) - cy
        u = (dx * ux) + (dy * uy)
        v = (dx * vx) + (dy * vy)
        u_values.append(float(u))
        v_values.append(float(v))

    g1, g2 = _deterministic_kmeans_1d(u_values)
    if g1 and g2:
        mean1 = sum(g1) / float(len(g1))
        mean2 = sum(g2) / float(len(g2))
        std_u = _std_population(u_values)
        result["split_separation"] = abs(mean1 - mean2) / (std_u + BRIDGE_EPSILON)

    if enemy_points and angle_bins > 0:
        ex, ey = _mean_xy(enemy_points)
        occupied_bins = set()
        full_circle = 2.0 * math.pi
        for x, y in side_points:
            phi = math.atan2(float(y) - ey, float(x) - ex)
            if phi < 0.0:
                phi += full_circle
            idx = int((phi / full_circle) * angle_bins)
            if idx >= angle_bins:
                idx = angle_bins - 1
            if idx < 0:
                idx = 0
            occupied_bins.add(idx)
        result["angle_coverage"] = float(len(occupied_bins)) / float(angle_bins)

    forward_values: list[float] | None = None
    lateral_values: list[float] | None = None
    if enemy_points:
        ex, ey = _mean_xy(enemy_points)
        fx = ex - cx
        fy = ey - cy
        f_norm = math.sqrt((fx * fx) + (fy * fy))
        if f_norm > BRIDGE_EPSILON:
            fx /= f_norm
            fy /= f_norm
            lx = -fy
            ly = fx
            forward_values = []
            lateral_values = []
            for x, y in side_points:
                dx = float(x) - cx
                dy = float(y) - cy
                forward_values.append((dx * fx) + (dy * fy))
                lateral_values.append((dx * lx) + (dy * ly))
            sigma_forward = _std_population(forward_values)
            sigma_lateral = _std_population(lateral_values)
            result["AR_forward"] = sigma_forward / (sigma_lateral + BRIDGE_EPSILON)
            result["major_axis_alignment"] = abs((ux * fx) + (uy * fy))

    n_units = len(side_points)
    if n_units > 0 and forward_values is not None and lateral_values is not None:
        group_size = max(1, int(math.ceil(0.3 * float(n_units))))
        sorted_indices = sorted(range(n_units), key=lambda i: forward_values[i])
        rear_indices = sorted_indices[:group_size]
        front_indices = sorted_indices[-group_size:]
        v_rear = [lateral_values[i] for i in rear_indices]
        v_front = [lateral_values[i] for i in front_indices]
        width_front = _std_population(v_front)
        width_back = _std_population(v_rear)
        result["wedge_ratio"] = width_front / (width_back + BRIDGE_EPSILON)

    return result

def _quantile(sorted_values: list[float], q: float) -> float:
    if not sorted_values:
        return float("nan")
    if len(sorted_values) == 1:
        return float(sorted_values[0])
    if q <= 0.0:
        return float(sorted_values[0])
    if q >= 1.0:
        return float(sorted_values[-1])
    pos = (len(sorted_values) - 1) * q
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return float(sorted_values[lo])
    w = pos - lo
    return float(sorted_values[lo] * (1.0 - w) + sorted_values[hi] * w)

def _safe_float_or_nan(value) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float("nan")

def compute_bridge_metrics_per_side(state: BattleState) -> dict:
    positions_by_fleet: dict[str, list[tuple[float, float]]] = {}
    for fleet_id, fleet in state.fleets.items():
        side_points: list[tuple[float, float]] = []
        for unit_id in fleet.unit_ids:
            unit = state.units.get(unit_id)
            if unit is None:
                continue
            side_points.append((float(unit.position.x), float(unit.position.y)))
        positions_by_fleet[str(fleet_id)] = side_points

    metrics_by_fleet: dict[str, dict] = {}
    for fleet_id in state.fleets:
        enemy_points: list[tuple[float, float]] = []
        for other_id, points in positions_by_fleet.items():
            if other_id != fleet_id:
                enemy_points.extend(points)
        metrics_by_fleet[fleet_id] = compute_formation_snapshot_metrics(
            side_points=positions_by_fleet.get(fleet_id, []),
            enemy_points=enemy_points,
            angle_bins=12,
        )
    return metrics_by_fleet

def compute_collapse_v2_shadow_telemetry(
    *,
    observer_enabled: bool,
    observer_telemetry: dict,
    alive_trajectory: dict,
    theta_conn_default: float,
    theta_coh_default: float,
    theta_force_default: float,
    theta_attr_default: float,
    attrition_window: int,
    sustain_ticks: int,
    min_conditions: int,
) -> dict:
    sides = ("A", "B")
    n_ticks = max(
        len(alive_trajectory.get("A", [])) if isinstance(alive_trajectory.get("A", []), (list, tuple)) else 0,
        len(alive_trajectory.get("B", [])) if isinstance(alive_trajectory.get("B", []), (list, tuple)) else 0,
    )
    ticks = list(range(1, n_ticks + 1))
    out = {
        "tick": ticks,
        "thresholds": {
            "A": {
                "theta_conn": float(theta_conn_default),
                "theta_coh": float(theta_coh_default),
                "theta_force": float(theta_force_default),
                "theta_attr": float(theta_attr_default),
            },
            "B": {
                "theta_conn": float(theta_conn_default),
                "theta_coh": float(theta_coh_default),
                "theta_force": float(theta_force_default),
                "theta_attr": float(theta_attr_default),
            },
        },
        "pressure_v2_shadow": {side: [] for side in sides},
        "collapse_v2_shadow": {side: [] for side in sides},
        "pressure_sustain_counter": {side: [] for side in sides},
        "C_conn_signal": {side: [] for side in sides},
        "C_coh_signal": {side: [] for side in sides},
        "ForceRatio": {side: [] for side in sides},
        "AttritionMomentum": {side: [] for side in sides},
        "first_tick_pressure_v2_shadow": {side: None for side in sides},
        "first_tick_collapse_v2_shadow": {side: None for side in sides},
        "pct_ticks_pressure_true": {side: 0.0 for side in sides},
        "pct_ticks_collapse_true": {side: 0.0 for side in sides},
        "notes": {side: "" for side in sides},
        "config": {
            "attrition_window": int(max(1, attrition_window)),
            "sustain_ticks": int(max(1, sustain_ticks)),
            "min_conditions": int(max(1, min_conditions)),
            "theta_defaults": {
                "theta_conn": float(theta_conn_default),
                "theta_coh": float(theta_coh_default),
                "theta_force": float(theta_force_default),
                "theta_attr": float(theta_attr_default),
            },
        },
    }
    if n_ticks <= 0:
        return out

    if not bool(observer_enabled):
        for side in sides:
            out["C_conn_signal"][side] = [float("nan")] * n_ticks
            out["C_coh_signal"][side] = [float("nan")] * n_ticks
            out["ForceRatio"][side] = [float("nan")] * n_ticks
            out["AttritionMomentum"][side] = [float("nan")] * n_ticks
            out["pressure_v2_shadow"][side] = [False] * n_ticks
            out["collapse_v2_shadow"][side] = [False] * n_ticks
            out["pressure_sustain_counter"][side] = [0] * n_ticks
            out["pct_ticks_pressure_true"][side] = 0.0
            out["pct_ticks_collapse_true"][side] = 0.0
            out["notes"][side] = "observer_disabled"
        return out

    alive_a = [float(v) for v in alive_trajectory.get("A", [])]
    alive_b = [float(v) for v in alive_trajectory.get("B", [])]
    c_conn_raw = observer_telemetry.get("c_conn", {}) if isinstance(observer_telemetry, dict) else {}
    c_coh_raw = observer_telemetry.get("cohesion_v3", {}) if isinstance(observer_telemetry, dict) else {}
    if not isinstance(c_conn_raw, dict):
        c_conn_raw = {}
    if not isinstance(c_coh_raw, dict):
        c_coh_raw = {}
    c_conn_a_series = c_conn_raw.get("A", [])
    c_conn_b_series = c_conn_raw.get("B", [])
    c_coh_a_series = c_coh_raw.get("A", [])
    c_coh_b_series = c_coh_raw.get("B", [])
    if not isinstance(c_conn_a_series, (list, tuple)):
        c_conn_a_series = []
    if not isinstance(c_conn_b_series, (list, tuple)):
        c_conn_b_series = []
    if not isinstance(c_coh_a_series, (list, tuple)):
        c_coh_a_series = []
    if not isinstance(c_coh_b_series, (list, tuple)):
        c_coh_b_series = []

    # Build side-level raw signals first.
    for idx in range(n_ticks):
        tick = idx + 1
        w_eff = min(max(1, int(attrition_window)), tick)
        prev_idx = idx - w_eff
        if prev_idx < 0:
            prev_idx = 0

        alive_curr_a = float(alive_a[idx]) if idx < len(alive_a) else (float(alive_a[-1]) if alive_a else 0.0)
        alive_curr_b = float(alive_b[idx]) if idx < len(alive_b) else (float(alive_b[-1]) if alive_b else 0.0)
        alive_prev_a = float(alive_a[prev_idx]) if prev_idx < len(alive_a) else alive_curr_a
        alive_prev_b = float(alive_b[prev_idx]) if prev_idx < len(alive_b) else alive_curr_b

        loss_rate_a = (alive_prev_a - alive_curr_a) / float(w_eff)
        loss_rate_b = (alive_prev_b - alive_curr_b) / float(w_eff)
        attr_momentum_a = float(loss_rate_a - loss_rate_b)
        attr_momentum_b = float(loss_rate_b - loss_rate_a)

        force_ratio_a = float(alive_curr_a / alive_curr_b) if alive_curr_b > 0.0 else float("inf")
        force_ratio_b = float(alive_curr_b / alive_curr_a) if alive_curr_a > 0.0 else float("inf")

        c_conn_a = _safe_float_or_nan(c_conn_a_series[idx] if idx < len(c_conn_a_series) else float("nan"))
        c_conn_b = _safe_float_or_nan(c_conn_b_series[idx] if idx < len(c_conn_b_series) else float("nan"))
        c_coh_a = _safe_float_or_nan(c_coh_a_series[idx] if idx < len(c_coh_a_series) else float("nan"))
        c_coh_b = _safe_float_or_nan(c_coh_b_series[idx] if idx < len(c_coh_b_series) else float("nan"))

        out["C_conn_signal"]["A"].append(c_conn_a)
        out["C_conn_signal"]["B"].append(c_conn_b)
        out["C_coh_signal"]["A"].append(c_coh_a)
        out["C_coh_signal"]["B"].append(c_coh_b)
        out["ForceRatio"]["A"].append(force_ratio_a)
        out["ForceRatio"]["B"].append(force_ratio_b)
        out["AttritionMomentum"]["A"].append(attr_momentum_a)
        out["AttritionMomentum"]["B"].append(attr_momentum_b)

    # Per-side quantile thresholds (fallback to defaults if signal missing).
    for side in sides:
        finite_conn = sorted(v for v in out["C_conn_signal"][side] if math.isfinite(v))
        finite_coh = sorted(v for v in out["C_coh_signal"][side] if math.isfinite(v))
        finite_force = sorted(v for v in out["ForceRatio"][side] if math.isfinite(v))
        finite_attr = sorted(v for v in out["AttritionMomentum"][side] if math.isfinite(v))
        theta_conn = _quantile(finite_conn, 0.20) if finite_conn else float(theta_conn_default)
        theta_coh = _quantile(finite_coh, 0.20) if finite_coh else float(theta_coh_default)
        theta_force = _quantile(finite_force, 0.30) if finite_force else float(theta_force_default)
        theta_attr = _quantile(finite_attr, 0.70) if finite_attr else float(theta_attr_default)
        out["thresholds"][side] = {
            "theta_conn": float(theta_conn),
            "theta_coh": float(theta_coh),
            "theta_force": float(theta_force),
            "theta_attr": float(theta_attr),
        }

    # Pressure/collapse state machine (observer-only).
    for side in sides:
        theta_conn = float(out["thresholds"][side]["theta_conn"])
        theta_coh = float(out["thresholds"][side]["theta_coh"])
        theta_force = float(out["thresholds"][side]["theta_force"])
        theta_attr = float(out["thresholds"][side]["theta_attr"])
        counter = 0
        pressure_true_count = 0
        collapse_true_count = 0
        for idx in range(n_ticks):
            c_conn = float(out["C_conn_signal"][side][idx])
            c_coh = float(out["C_coh_signal"][side][idx])
            force_ratio = float(out["ForceRatio"][side][idx])
            attr_momentum = float(out["AttritionMomentum"][side][idx])
            cond_conn = math.isfinite(c_conn) and (c_conn < theta_conn)
            cond_coh = math.isfinite(c_coh) and (c_coh < theta_coh)
            cond_force = math.isfinite(force_ratio) and (force_ratio < theta_force)
            cond_attr = math.isfinite(attr_momentum) and (attr_momentum > theta_attr)
            pressure = int(cond_conn) + int(cond_coh) + int(cond_force) + int(cond_attr) >= int(min_conditions)
            if pressure:
                counter += 1
                pressure_true_count += 1
            else:
                counter = 0
            collapse_shadow = counter >= int(sustain_ticks)
            if collapse_shadow:
                collapse_true_count += 1

            out["pressure_v2_shadow"][side].append(bool(pressure))
            out["pressure_sustain_counter"][side].append(int(counter))
            out["collapse_v2_shadow"][side].append(bool(collapse_shadow))

            tick = idx + 1
            if pressure and out["first_tick_pressure_v2_shadow"][side] is None:
                out["first_tick_pressure_v2_shadow"][side] = int(tick)
            if collapse_shadow and out["first_tick_collapse_v2_shadow"][side] is None:
                out["first_tick_collapse_v2_shadow"][side] = int(tick)

        out["pct_ticks_pressure_true"][side] = (float(pressure_true_count) / float(n_ticks)) * 100.0
        out["pct_ticks_collapse_true"][side] = (float(collapse_true_count) / float(n_ticks)) * 100.0
        if out["first_tick_collapse_v2_shadow"][side] is None:
            out["notes"][side] = "never-trigger"
        else:
            out["notes"][side] = "triggered"

    return out

def build_initial_state(
    fleet_a_params: PersonalityParameters,
    fleet_b_params: PersonalityParameters,
    fleet_a_size: int,
    fleet_b_size: int,
    fleet_a_aspect_ratio: float,
    fleet_b_aspect_ratio: float,
    unit_spacing: float,
    unit_speed: float,
    unit_max_hit_points: float,
    arena_size: float,
    fleet_a_origin_x: float | None = None,
    fleet_a_origin_y: float | None = None,
    fleet_b_origin_x: float | None = None,
    fleet_b_origin_y: float | None = None,
    fleet_a_facing_angle_deg: float | None = None,
    fleet_b_facing_angle_deg: float | None = None,
) -> BattleState:
    fleet_a_size_effective = int(fleet_a_size)
    fleet_b_size_effective = int(fleet_b_size)
    if fleet_a_size_effective < 1:
        raise ValueError(f"fleet_a_size must be >= 1, got {fleet_a_size_effective}")
    if fleet_b_size_effective < 1:
        raise ValueError(f"fleet_b_size must be >= 1, got {fleet_b_size_effective}")
    fleet_a_aspect_ratio_effective = float(fleet_a_aspect_ratio)
    fleet_b_aspect_ratio_effective = float(fleet_b_aspect_ratio)
    if fleet_a_aspect_ratio_effective <= 0.0:
        raise ValueError(f"fleet_a_aspect_ratio must be > 0, got {fleet_a_aspect_ratio_effective}")
    if fleet_b_aspect_ratio_effective <= 0.0:
        raise ValueError(f"fleet_b_aspect_ratio must be > 0, got {fleet_b_aspect_ratio_effective}")

    spawn_margin = max(1.0, arena_size * DEFAULT_SPAWN_MARGIN_RATIO)
    fleet_a_origin_x_effective = spawn_margin if fleet_a_origin_x is None else float(fleet_a_origin_x)
    fleet_a_origin_y_effective = spawn_margin if fleet_a_origin_y is None else float(fleet_a_origin_y)
    fleet_b_origin_x_effective = (arena_size - spawn_margin) if fleet_b_origin_x is None else float(fleet_b_origin_x)
    fleet_b_origin_y_effective = (arena_size - spawn_margin) if fleet_b_origin_y is None else float(fleet_b_origin_y)
    fleet_a_facing_angle_deg_effective = 45.0 if fleet_a_facing_angle_deg is None else float(fleet_a_facing_angle_deg)
    fleet_b_facing_angle_deg_effective = 225.0 if fleet_b_facing_angle_deg is None else float(fleet_b_facing_angle_deg)

    dir_a = _direction_from_angle_deg(fleet_a_facing_angle_deg_effective)
    dir_b = _direction_from_angle_deg(fleet_b_facing_angle_deg_effective)

    perp_a = (-dir_a[1], dir_a[0])
    perp_b = (-dir_b[1], dir_b[0])

    units = {}

    def _spawn_side(
        *,
        fleet_id: str,
        unit_count: int,
        aspect_ratio_local: float,
        origin_x: float,
        origin_y: float,
        dir_xy: tuple[float, float],
        perp_xy: tuple[float, float],
    ) -> list[str]:
        unit_ids = []
        row_counts = _resolve_initial_formation_layout(unit_count, aspect_ratio_local)
        half_depth = (len(row_counts) - 1) / 2.0
        unit_index = 0
        for row, row_count in enumerate(row_counts):
            row_offset = row - half_depth
            half_width = (row_count - 1) / 2.0
            for col in range(row_count):
                lateral = col - half_width
                unit_id = f"{fleet_id}{unit_index + 1}"
                px = origin_x + (dir_xy[0] * row_offset * unit_spacing) + (perp_xy[0] * lateral * unit_spacing)
                py = origin_y + (dir_xy[1] * row_offset * unit_spacing) + (perp_xy[1] * lateral * unit_spacing)
                units[unit_id] = UnitState(
                    unit_id=unit_id,
                    fleet_id=fleet_id,
                    position=Vec2(x=clamp(px, 0.0, arena_size), y=clamp(py, 0.0, arena_size)),
                    velocity=Vec2(x=0.0, y=0.0),
                    hit_points=unit_max_hit_points,
                    max_hit_points=unit_max_hit_points,
                    max_speed=unit_speed,
                    orientation_vector=Vec2(x=dir_xy[0], y=dir_xy[1]),
                )
                unit_ids.append(unit_id)
                unit_index += 1
        return unit_ids

    fleet_a_unit_ids = _spawn_side(
        fleet_id="A",
        unit_count=fleet_a_size_effective,
        aspect_ratio_local=fleet_a_aspect_ratio_effective,
        origin_x=fleet_a_origin_x_effective,
        origin_y=fleet_a_origin_y_effective,
        dir_xy=dir_a,
        perp_xy=perp_a,
    )
    fleet_b_unit_ids = _spawn_side(
        fleet_id="B",
        unit_count=fleet_b_size_effective,
        aspect_ratio_local=fleet_b_aspect_ratio_effective,
        origin_x=fleet_b_origin_x_effective,
        origin_y=fleet_b_origin_y_effective,
        dir_xy=dir_b,
        perp_xy=perp_b,
    )

    fleets = {
        "A": FleetState(fleet_id="A", parameters=fleet_a_params, unit_ids=tuple(fleet_a_unit_ids)),
        "B": FleetState(fleet_id="B", parameters=fleet_b_params, unit_ids=tuple(fleet_b_unit_ids)),
    }

    state = BattleState(
        tick=0,
        dt=DEFAULT_DT,
        arena_size=arena_size,
        units=units,
        fleets=fleets,
        last_fleet_cohesion=build_initial_cohesion_map(fleets.keys()),
    )
    return state

def run_simulation(
    initial_state: BattleState,
    steps: int,
    capture_positions: bool,
    observer_enabled: bool,
    runtime_decision_source: str,
    movement_model: str,
    bridge_theta_split: float,
    bridge_theta_env: float,
    bridge_sustain_ticks: int,
    collapse_shadow_theta_conn_default: float,
    collapse_shadow_theta_coh_default: float,
    collapse_shadow_theta_force_default: float,
    collapse_shadow_theta_attr_default: float,
    collapse_shadow_attrition_window: int,
    collapse_shadow_sustain_ticks: int,
    collapse_shadow_min_conditions: int,
    frame_stride: int,
    attack_range: float,
    damage_per_tick: float,
    separation_radius: float,
    fire_quality_alpha: float,
    contact_hysteresis_h: float,
    ch_enabled: bool,
    fsr_enabled: bool,
    fsr_strength: float,
    boundary_enabled: bool,
    boundary_hard_enabled: bool,
    include_target_lines: bool,
    print_tick_summary: bool,
    plot_diagnostics_enabled: bool,
    boundary_soft_strength: float = 1.0,
    alpha_sep: float = 0.6,
    movement_v3a_experiment: str = "base",
    centroid_probe_scale: float = 1.0,
    pre_tl_target_substrate: str = PRE_TL_TARGET_SUBSTRATE_DEFAULT,
    odw_posture_bias_enabled: bool = False,
    odw_posture_bias_k: float = 0.3,
    odw_posture_bias_clip_delta: float = 0.2,
    symmetric_movement_sync_enabled: bool = True,
    hostile_contact_impedance_mode: str = HOSTILE_CONTACT_IMPEDANCE_MODE_DEFAULT,
    hostile_contact_impedance_v2_radius_multiplier: float = HOSTILE_CONTACT_IMPEDANCE_V2_RADIUS_MULTIPLIER_DEFAULT,
    hostile_contact_impedance_v2_repulsion_max_disp_ratio: float = HOSTILE_CONTACT_IMPEDANCE_V2_REPULSION_MAX_DISP_RATIO_DEFAULT,
    hostile_contact_impedance_v2_forward_damping_strength: float = HOSTILE_CONTACT_IMPEDANCE_V2_FORWARD_DAMPING_STRENGTH_DEFAULT,
    hostile_intent_unified_spacing_scale: float = HOSTILE_INTENT_UNIFIED_SPACING_SCALE_DEFAULT,
    hostile_intent_unified_spacing_strength: float = HOSTILE_INTENT_UNIFIED_SPACING_STRENGTH_DEFAULT,
    continuous_fr_shaping_enabled: bool = False,
    continuous_fr_shaping_mode: str = CONTINUOUS_FR_SHAPING_OFF,
    continuous_fr_shaping_a: float = 0.0,
    continuous_fr_shaping_sigma: float = 0.15,
    continuous_fr_shaping_p: float = 1.0,
    continuous_fr_shaping_q: float = 1.0,
    continuous_fr_shaping_beta: float = 0.0,
    continuous_fr_shaping_gamma: float = 0.0,
    v2_connect_radius_multiplier: float = 1.0,
    v3_connect_radius_multiplier: float = 1.0,
    v3_r_ref_radius_multiplier: float = 1.0,
    runtime_diag_enabled: bool = False,
    post_elimination_extra_ticks: int = 10,
    engine_cls: Any | None = None,
):
    if engine_cls is None:
        raise ValueError("run_simulation requires an explicit engine_cls")

    post_elimination_extra_ticks = max(0, int(post_elimination_extra_ticks))
    engine = engine_cls(
        attack_range=attack_range,
        damage_per_tick=damage_per_tick,
        separation_radius=separation_radius,
    )
    engine.COHESION_DECISION_SOURCE = str(runtime_decision_source).strip().lower() or "v2"
    engine.MOVEMENT_MODEL = str(movement_model).strip().lower() or "v3a"
    engine.MOVEMENT_V3A_EXPERIMENT = str(movement_v3a_experiment).strip().lower() or "base"
    engine.CENTROID_PROBE_SCALE = float(centroid_probe_scale)
    engine.PRE_TL_TARGET_SUBSTRATE = str(pre_tl_target_substrate).strip().lower() or PRE_TL_TARGET_SUBSTRATE_DEFAULT
    engine.ODW_POSTURE_BIAS_ENABLED = bool(odw_posture_bias_enabled)
    engine.ODW_POSTURE_BIAS_K = max(0.0, float(odw_posture_bias_k))
    engine.ODW_POSTURE_BIAS_CLIP_DELTA = max(0.0, float(odw_posture_bias_clip_delta))
    engine.SYMMETRIC_MOVEMENT_SYNC_ENABLED = bool(symmetric_movement_sync_enabled)
    engine.HOSTILE_CONTACT_IMPEDANCE_MODE = (
        str(hostile_contact_impedance_mode).strip().lower() or HOSTILE_CONTACT_IMPEDANCE_MODE_DEFAULT
    )
    engine.HOSTILE_CONTACT_IMPEDANCE_V2_RADIUS_MULTIPLIER = max(
        1e-6, float(hostile_contact_impedance_v2_radius_multiplier)
    )
    engine.HOSTILE_CONTACT_IMPEDANCE_V2_REPULSION_MAX_DISP_RATIO = max(
        0.0, float(hostile_contact_impedance_v2_repulsion_max_disp_ratio)
    )
    engine.HOSTILE_CONTACT_IMPEDANCE_V2_FORWARD_DAMPING_STRENGTH = _clamp01(
        float(hostile_contact_impedance_v2_forward_damping_strength)
    )
    engine.HOSTILE_INTENT_UNIFIED_SPACING_SCALE = max(1e-6, float(hostile_intent_unified_spacing_scale))
    engine.HOSTILE_INTENT_UNIFIED_SPACING_STRENGTH = _clamp01(float(hostile_intent_unified_spacing_strength))
    engine.CONTINUOUS_FR_SHAPING_ENABLED = bool(continuous_fr_shaping_enabled)
    engine.CONTINUOUS_FR_SHAPING_MODE = str(continuous_fr_shaping_mode).strip().lower() or CONTINUOUS_FR_SHAPING_OFF
    engine.CONTINUOUS_FR_SHAPING_A = max(0.0, float(continuous_fr_shaping_a))
    engine.CONTINUOUS_FR_SHAPING_SIGMA = max(1e-6, float(continuous_fr_shaping_sigma))
    engine.CONTINUOUS_FR_SHAPING_P = max(0.0, float(continuous_fr_shaping_p))
    engine.CONTINUOUS_FR_SHAPING_Q = max(0.0, float(continuous_fr_shaping_q))
    engine.CONTINUOUS_FR_SHAPING_BETA = max(0.0, float(continuous_fr_shaping_beta))
    engine.CONTINUOUS_FR_SHAPING_GAMMA = max(0.0, float(continuous_fr_shaping_gamma))
    engine.V2_CONNECT_RADIUS_MULTIPLIER = max(1e-12, float(v2_connect_radius_multiplier))
    engine.V3_CONNECT_RADIUS_MULTIPLIER = max(1e-12, float(v3_connect_radius_multiplier))
    engine.V3_R_REF_RADIUS_MULTIPLIER = max(1e-12, float(v3_r_ref_radius_multiplier))
    engine.fire_quality_alpha = float(fire_quality_alpha)
    engine.contact_hysteresis_h = float(contact_hysteresis_h)
    engine.CH_ENABLED = bool(ch_enabled)
    engine.FSR_ENABLED = bool(fsr_enabled)
    engine.fsr_strength = float(fsr_strength)
    engine.BOUNDARY_SOFT_ENABLED = bool(boundary_enabled)
    engine.BOUNDARY_HARD_ENABLED = bool(boundary_enabled) and bool(boundary_hard_enabled)
    engine.boundary_soft_strength = max(0.0, float(boundary_soft_strength))
    engine.alpha_sep = max(0.0, float(alpha_sep))
    # Plot/runtime diagnostics can be enabled without observer/export pipeline.
    diagnostics_enabled = bool(observer_enabled) or bool(plot_diagnostics_enabled)
    observer_active = bool(diagnostics_enabled) and (bool(capture_positions) or bool(runtime_diag_enabled))
    # Visualization debug panel consumes these runtime diagnostics per frame.
    engine.debug_fsr_diag_enabled = observer_active
    engine.debug_diag4_enabled = observer_active
    engine.debug_diag4_rpg_enabled = False
    engine.debug_cohesion_v3_shadow_enabled = bool(diagnostics_enabled)

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

    trajectory = {fleet_id: [] for fleet_id in state.fleets}
    alive_trajectory = {fleet_id: [] for fleet_id in state.fleets}
    fleet_size_trajectory = {fleet_id: [] for fleet_id in state.fleets}
    observer_telemetry = {
        "cohesion_v3": {fleet_id: [] for fleet_id in state.fleets},
        "c_conn": {fleet_id: [] for fleet_id in state.fleets},
        "c_scale": {fleet_id: [] for fleet_id in state.fleets},
        "rho": {fleet_id: [] for fleet_id in state.fleets},
        "centroid_x": {fleet_id: [] for fleet_id in state.fleets},
        "centroid_y": {fleet_id: [] for fleet_id in state.fleets},
        "net_axis_push": {"net": []},
        "net_axis_push_interval_ticks": 10,
        "center_wing_advance_gap": {fleet_id: [] for fleet_id in state.fleets},
        "center_wing_advance_gap_interval_ticks": 10,
        "front_curvature_index": {fleet_id: [] for fleet_id in state.fleets},
        "center_wing_parallel_share": {fleet_id: [] for fleet_id in state.fleets},
        "posture_persistence_time": {fleet_id: [] for fleet_id in state.fleets},
        "hostile_overlap_pairs": [],
        "hostile_deep_pairs": [],
        "hostile_deep_intermix_ratio": [],
        "hostile_intermix_severity": [],
        "hostile_intermix_coverage": [],
    }
    combat_telemetry = {
        "in_contact_count": [],
        "damage_events_count": [],
        "outlier_total": [],
        "persistent_outlier_total": [],
        "max_outlier_persistence": [],
    }
    bridge_telemetry = {
        "theta_split": float(bridge_theta_split),
        "theta_env": float(bridge_theta_env),
        "sustain_ticks": int(bridge_sustain_ticks),
        "AR": {fleet_id: [] for fleet_id in state.fleets},
        "wedge_ratio": {fleet_id: [] for fleet_id in state.fleets},
        "split_separation": {fleet_id: [] for fleet_id in state.fleets},
        "angle_coverage": {fleet_id: [] for fleet_id in state.fleets},
        "split_cond": {fleet_id: [] for fleet_id in state.fleets},
        "env_cond": {fleet_id: [] for fleet_id in state.fleets},
        "split_sustain_counter": {fleet_id: [] for fleet_id in state.fleets},
        "env_sustain_counter": {fleet_id: [] for fleet_id in state.fleets},
        "bridge_event_cut": {fleet_id: [] for fleet_id in state.fleets},
        "bridge_event_pocket": {fleet_id: [] for fleet_id in state.fleets},
        "first_tick_split_sustain": {fleet_id: None for fleet_id in state.fleets},
        "first_tick_env_sustain": {fleet_id: None for fleet_id in state.fleets},
    }
    split_counter_state = {fleet_id: 0 for fleet_id in state.fleets}
    env_counter_state = {fleet_id: 0 for fleet_id in state.fleets}
    position_frames = []
    center_wing_interval_ticks = int(observer_telemetry.get("center_wing_advance_gap_interval_ticks", 10))
    center_wing_position_history = {fleet_id: [] for fleet_id in state.fleets}
    posture_persistence_state = {
        fleet_id: {"sign": 0, "length": 0}
        for fleet_id in state.fleets
    }
    if steps <= 0:
        tick_limit = 999
        elimination_tick = None
        post_elimination_stop_tick = None
    else:
        tick_limit = steps
        elimination_tick = None
        post_elimination_stop_tick = None

    while state.tick < tick_limit:
        state = engine.step(state)
        combat_stats = getattr(engine, "debug_last_combat_stats", {})
        if not isinstance(combat_stats, dict):
            combat_stats = {}
        combat_telemetry["in_contact_count"].append(int(combat_stats.get("in_contact_count", 0)))
        combat_telemetry["damage_events_count"].append(int(combat_stats.get("damage_events_count", 0)))
        runtime_debug_payload = extract_runtime_debug_payload(
            getattr(engine, "debug_diag_last_tick", {}) if diagnostics_enabled else {}
        )
        combat_telemetry["outlier_total"].append(int(runtime_debug_payload.get("outlier_total", 0)))
        combat_telemetry["persistent_outlier_total"].append(int(runtime_debug_payload.get("persistent_outlier_total", 0)))
        combat_telemetry["max_outlier_persistence"].append(int(runtime_debug_payload.get("max_outlier_persistence", 0)))
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
            center_wing_position_history[fleet_id].append(unit_position_map)
            if centroid_count > 0:
                observer_telemetry["centroid_x"][fleet_id].append(centroid_sum_x / float(centroid_count))
                observer_telemetry["centroid_y"][fleet_id].append(centroid_sum_y / float(centroid_count))
            else:
                observer_telemetry["centroid_x"][fleet_id].append(float("nan"))
                observer_telemetry["centroid_y"][fleet_id].append(float("nan"))
        hostile_intermix_metrics = _compute_hostile_intermix_metrics(state, float(separation_radius))
        observer_telemetry["hostile_overlap_pairs"].append(
            float(hostile_intermix_metrics.get("hostile_overlap_pairs", 0.0))
        )
        observer_telemetry["hostile_deep_pairs"].append(
            float(hostile_intermix_metrics.get("hostile_deep_pairs", 0.0))
        )
        observer_telemetry["hostile_deep_intermix_ratio"].append(
            float(hostile_intermix_metrics.get("hostile_deep_intermix_ratio", 0.0))
        )
        observer_telemetry["hostile_intermix_severity"].append(
            float(hostile_intermix_metrics.get("hostile_intermix_severity", 0.0))
        )
        observer_telemetry["hostile_intermix_coverage"].append(
            float(hostile_intermix_metrics.get("hostile_intermix_coverage", 0.0))
        )
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
                series.append(float("nan"))
                observer_telemetry["front_curvature_index"][fleet_id].append(float("nan"))
                observer_telemetry["center_wing_parallel_share"][fleet_id].append(float("nan"))
                observer_telemetry["posture_persistence_time"][fleet_id].append(0.0)
                posture_persistence_state[fleet_id]["sign"] = 0
                posture_persistence_state[fleet_id]["length"] = 0
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
                series.append(float("nan"))
                observer_telemetry["front_curvature_index"][fleet_id].append(float("nan"))
                observer_telemetry["center_wing_parallel_share"][fleet_id].append(float("nan"))
                observer_telemetry["posture_persistence_time"][fleet_id].append(0.0)
                posture_persistence_state[fleet_id]["sign"] = 0
                posture_persistence_state[fleet_id]["length"] = 0
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
                    center_band = center_advances
                    wing_band = wing_advances
                    if not center_band or not wing_band:
                        series.append(float("nan"))
                        interval_parallel_share_gap = float("nan")
                    else:
                        center_mean = sum(center_band) / float(len(center_band))
                        wing_mean = sum(wing_band) / float(len(wing_band))
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
                front_curvature_norm = float(front_curvature_raw) / max(float(separation_radius), 1e-12)
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
        shadow_v3 = getattr(engine, "debug_last_cohesion_v3", {})
        if not isinstance(shadow_v3, dict):
            shadow_v3 = {}
        shadow_v3_components = getattr(engine, "debug_last_cohesion_v3_components", {})
        if not isinstance(shadow_v3_components, dict):
            shadow_v3_components = {}
        for fleet_id in state.fleets:
            fallback_v2 = float(state.last_fleet_cohesion.get(fleet_id, 1.0))
            if diagnostics_enabled:
                cohesion_v3 = float(shadow_v3.get(fleet_id, fallback_v2))
            else:
                cohesion_v3 = float("nan")
            comp = shadow_v3_components.get(fleet_id, {})
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
                    state.tick >= 1 and contact_active_tick and split_value >= float(bridge_theta_split)
                )
                env_cond = bool(
                    state.tick >= 1 and contact_active_tick and env_value >= float(bridge_theta_env)
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
                split_counter_state[fleet_id] >= int(bridge_sustain_ticks)
                and bridge_telemetry["first_tick_split_sustain"].get(fleet_id) is None
            ):
                bridge_telemetry["first_tick_split_sustain"][fleet_id] = int(state.tick)
                cut_event_tick = True
            if (
                env_counter_state[fleet_id] >= int(bridge_sustain_ticks)
                and bridge_telemetry["first_tick_env_sustain"].get(fleet_id) is None
            ):
                bridge_telemetry["first_tick_env_sustain"][fleet_id] = int(state.tick)
                pocket_event_tick = True

            bridge_telemetry["AR"][fleet_id].append(ar_value)
            bridge_telemetry["wedge_ratio"][fleet_id].append(wedge_value)
            bridge_telemetry["split_separation"][fleet_id].append(split_value)
            bridge_telemetry["angle_coverage"][fleet_id].append(env_value)
            bridge_telemetry["split_cond"][fleet_id].append(bool(split_cond))
            bridge_telemetry["env_cond"][fleet_id].append(bool(env_cond))
            bridge_telemetry["split_sustain_counter"][fleet_id].append(int(split_counter_state[fleet_id]))
            bridge_telemetry["env_sustain_counter"][fleet_id].append(int(env_counter_state[fleet_id]))
            bridge_telemetry["bridge_event_cut"][fleet_id].append(bool(cut_event_tick))
            bridge_telemetry["bridge_event_pocket"][fleet_id].append(bool(pocket_event_tick))

        if capture_positions and frame_stride > 0 and state.tick % frame_stride == 0:
            frame = {"tick": state.tick}
            targets = {}
            for fleet_id, fleet in state.fleets.items():
                points = []
                for unit_id in fleet.unit_ids:
                    if unit_id in state.units:
                        unit = state.units[unit_id]
                        points.append(
                            (
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
                            if target_id in state.units and state.units[target_id].hit_points > 0.0:
                                targets[str(unit_id)] = target_id
                frame[fleet_id] = points
            if include_target_lines:
                frame["targets"] = targets
            frame["runtime_debug"] = extract_runtime_debug_payload(
                getattr(engine, "debug_diag_last_tick", {}) if observer_active else {}
            )
            position_frames.append(frame)

        any_fleet_eliminated = any(len(fleet.unit_ids) == 0 for fleet in state.fleets.values())
        if steps <= 0:
            if any_fleet_eliminated and elimination_tick is None:
                elimination_tick = state.tick
                post_elimination_stop_tick = min(999, elimination_tick + post_elimination_extra_ticks)
            if post_elimination_stop_tick is not None and state.tick >= post_elimination_stop_tick:
                break
        else:
            if any_fleet_eliminated:
                break

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
    front_curvature_normalization_scale = max(float(separation_radius), 1e-12)
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
        if (
            not axis_initialized
            or not valid_pair
            or idx < net_axis_push_interval_ticks
        ):
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
    for fleet_id in state.fleets:
        normalized_gap_series: list[float] = []
        for raw_value in observer_telemetry["center_wing_advance_gap"][fleet_id]:
            if math.isfinite(float(raw_value)):
                normalized_gap_series.append(float(raw_value) / center_wing_normalization_scale)
            else:
                normalized_gap_series.append(float("nan"))
        observer_telemetry["center_wing_advance_gap"][fleet_id] = normalized_gap_series
        normalized_front_curvature_series: list[float] = []
        for raw_value in observer_telemetry["front_curvature_index"][fleet_id]:
            if math.isfinite(float(raw_value)):
                normalized_front_curvature_series.append(float(raw_value) / front_curvature_normalization_scale)
            else:
                normalized_front_curvature_series.append(float("nan"))
        observer_telemetry["front_curvature_index"][fleet_id] = normalized_front_curvature_series
    observer_telemetry["center_wing_advance_gap_normalization_scale"] = center_wing_normalization_scale
    observer_telemetry["front_curvature_index_normalization_scale"] = front_curvature_normalization_scale

    collapse_shadow_telemetry = compute_collapse_v2_shadow_telemetry(
        observer_enabled=diagnostics_enabled,
        observer_telemetry=observer_telemetry,
        alive_trajectory=alive_trajectory,
        theta_conn_default=float(collapse_shadow_theta_conn_default),
        theta_coh_default=float(collapse_shadow_theta_coh_default),
        theta_force_default=float(collapse_shadow_theta_force_default),
        theta_attr_default=float(collapse_shadow_theta_attr_default),
        attrition_window=int(collapse_shadow_attrition_window),
        sustain_ticks=int(collapse_shadow_sustain_ticks),
        min_conditions=int(collapse_shadow_min_conditions),
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
