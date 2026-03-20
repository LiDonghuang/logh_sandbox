import math
from collections.abc import Mapping

from runtime.runtime_v0_1 import BattleState


BRIDGE_EPSILON = 1e-9


def _clamp01(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return value


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
    if not isinstance(c_conn_a_series, list):
        c_conn_a_series = []
    if not isinstance(c_conn_b_series, list):
        c_conn_b_series = []
    if not isinstance(c_coh_a_series, list):
        c_coh_a_series = []
    if not isinstance(c_coh_b_series, list):
        c_coh_b_series = []

    attrition_window_effective = int(max(1, attrition_window))
    sustain_ticks_effective = int(max(1, sustain_ticks))
    min_conditions_effective = int(max(1, min_conditions))

    for side in sides:
        own_alive = alive_a if side == "A" else alive_b
        opp_alive = alive_b if side == "A" else alive_a
        c_conn_series = c_conn_a_series if side == "A" else c_conn_b_series
        c_coh_series = c_coh_a_series if side == "A" else c_coh_b_series
        force_ratio_series: list[float] = []
        attrition_momentum_series: list[float] = []
        for idx in range(n_ticks):
            own_value = own_alive[idx] if idx < len(own_alive) else float("nan")
            opp_value = opp_alive[idx] if idx < len(opp_alive) else float("nan")
            if own_value > 0.0 and math.isfinite(opp_value):
                force_ratio_series.append(float(opp_value) / float(own_value))
            else:
                force_ratio_series.append(float("nan"))

            if idx + 1 < attrition_window_effective:
                attrition_momentum_series.append(float("nan"))
                continue
            window_start = idx + 1 - attrition_window_effective
            own_prev = own_alive[window_start] if window_start < len(own_alive) else float("nan")
            opp_prev = opp_alive[window_start] if window_start < len(opp_alive) else float("nan")
            own_curr = own_alive[idx] if idx < len(own_alive) else float("nan")
            opp_curr = opp_alive[idx] if idx < len(opp_alive) else float("nan")
            if not all(math.isfinite(value) for value in (own_prev, opp_prev, own_curr, opp_curr)):
                attrition_momentum_series.append(float("nan"))
                continue
            own_loss = max(0.0, float(own_prev) - float(own_curr))
            opp_loss = max(0.0, float(opp_prev) - float(opp_curr))
            attrition_momentum_series.append(float(own_loss - opp_loss))

        out["C_conn_signal"][side] = [
            _safe_float_or_nan(c_conn_series[idx]) if idx < len(c_conn_series) else float("nan")
            for idx in range(n_ticks)
        ]
        out["C_coh_signal"][side] = [
            _safe_float_or_nan(c_coh_series[idx]) if idx < len(c_coh_series) else float("nan")
            for idx in range(n_ticks)
        ]
        out["ForceRatio"][side] = force_ratio_series
        out["AttritionMomentum"][side] = attrition_momentum_series

        finite_conn = [value for value in out["C_conn_signal"][side] if math.isfinite(value)]
        finite_coh = [value for value in out["C_coh_signal"][side] if math.isfinite(value)]
        finite_force = [value for value in out["ForceRatio"][side] if math.isfinite(value)]
        finite_attr = [value for value in out["AttritionMomentum"][side] if math.isfinite(value)]
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
            pressure = (
                int(cond_conn) + int(cond_coh) + int(cond_force) + int(cond_attr)
                >= min_conditions_effective
            )
            if pressure:
                counter += 1
                pressure_true_count += 1
            else:
                counter = 0
            collapse_shadow = counter >= sustain_ticks_effective
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
