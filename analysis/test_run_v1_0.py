import json
import math
import random
import sys
from dataclasses import replace
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from runtime_v0_1 import (
    PersonalityParameters,
    Vec2,
    UnitState,
    FleetState,
    BattleState,
    build_initial_cohesion_map,
    initialize_unit_orientations,
)
from runtime.engine_skeleton import EngineTickSkeleton


DEFAULT_DT = 1.0
DEFAULT_SPAWN_MARGIN_RATIO = 0.05
DEFAULT_FRAME_STRIDE = 1
DEFAULT_PLOT_COLORS = ("#1f77b4", "#ff7f0e")
DEFAULT_BATTLE_REPORT_TOPIC = "test_run_v1_0"
DEFAULT_BATTLE_REPORT_EXPORT_DIR = "analysis/exports/battle_reports"
DEFAULT_VIDEO_EXPORT_DIR = "analysis/exports/videos"
DEFAULT_VIDEO_EXPORT_TOPIC = "test_run_v1_0"
ENDGAME_HP_RATIO_DEFAULT = 0.20
BRIDGE_THETA_SPLIT_DEFAULT = 1.715
BRIDGE_THETA_ENV_DEFAULT = 0.583
BRIDGE_SUSTAIN_TICKS_DEFAULT = 20
BRIDGE_EPSILON = 1e-9


def resolve_archetype(archetypes: dict, archetype_ref: str):
    if archetype_ref == "default":
        return {
            "name": "default",
            "disp_name_EN": "Default",
            "disp_name_ZH": "默认",
            "full_name_EN": "Default Archetype",
            "full_name_ZH": "默认原型",
            "force_concentration_ratio": 5.0,
            "mobility_bias": 5.0,
            "offense_defense_weight": 5.0,
            "risk_appetite": 5.0,
            "time_preference": 5.0,
            "targeting_logic": 5.0,
            "formation_rigidity": 5.0,
            "perception_radius": 5.0,
            "pursuit_drive": 5.0,
            "retreat_threshold": 5.0,
        }
    if archetype_ref in archetypes:
        return archetypes[archetype_ref]
    raise KeyError(archetype_ref)


def resolve_legacy_pursuit_drive(data: dict) -> float:
    if "pursuit_drive" in data:
        return float(data["pursuit_drive"])
    if "pursuit_threshold" in data:
        return float(data["pursuit_threshold"])
    if "PT" in data:
        return float(data["PT"])
    raise KeyError("pursuit_drive")


def to_personality_parameters(data: dict) -> PersonalityParameters:
    return PersonalityParameters(
        archetype_id=data["name"],
        force_concentration_ratio=float(data["force_concentration_ratio"]),
        mobility_bias=float(data["mobility_bias"]),
        offense_defense_weight=float(data["offense_defense_weight"]),
        risk_appetite=float(data["risk_appetite"]),
        time_preference=float(data["time_preference"]),
        targeting_logic=float(data["targeting_logic"]),
        formation_rigidity=float(data["formation_rigidity"]),
        perception_radius=float(data["perception_radius"]),
        pursuit_drive=resolve_legacy_pursuit_drive(data),
        retreat_threshold=float(data["retreat_threshold"]),
    )


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


def to_plot_color(data: dict, fallback: str) -> str:
    code = str(data.get("color_code", "")).strip()
    if not code:
        code = fallback
    if code.startswith("#"):
        return code
    return f"#{code}"


def resolve_display_name(data: dict, language: str) -> str:
    if language == "ZH":
        value = data.get("disp_name_ZH")
    else:
        value = data.get("disp_name_EN")
    if value:
        return str(value)
    if data.get("name"):
        return str(data["name"])
    return ""


def get_section_setting(settings: dict, section: str, key: str, default):
    section_data = settings.get(section, {})
    if isinstance(section_data, dict) and key in section_data:
        return section_data[key]
    return settings.get(key, default)


def get_visualization_setting(settings: dict, key: str, default):
    return get_section_setting(settings, "visualization", key, default)


def get_visualization_section(settings: dict) -> dict:
    section = settings.get("visualization", {})
    if isinstance(section, dict):
        return section
    return {}


def get_runtime_setting(settings: dict, key: str, default):
    return get_section_setting(settings, "runtime", key, default)


def get_fleet_setting(settings: dict, key: str, default):
    return get_section_setting(settings, "fleet", key, default)


def get_unit_setting(settings: dict, key: str, default):
    return get_section_setting(settings, "unit", key, default)


def get_battlefield_setting(settings: dict, key: str, default):
    return get_section_setting(settings, "battlefield", key, default)


def get_run_control_setting(settings: dict, key: str, default):
    return get_section_setting(settings, "run_control", key, default)


def get_seed_setting(settings: dict, key: str, default):
    return get_section_setting(settings, "seeds", key, default)


def clamp(v: float, lo: float, hi: float) -> float:
    if v < lo:
        return lo
    if v > hi:
        return hi
    return v


def resolve_effective_seed(seed_value: int) -> int:
    if seed_value < 0:
        return random.SystemRandom().randrange(0, 2**32)
    return seed_value


def seed_word_from_int(seed_value: int, length: int = 6) -> str:
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    rng = random.Random(int(seed_value) & 0xFFFFFFFF)
    return "".join(rng.choice(letters) for _ in range(max(1, length)))


def tick_to_std_time(tick: int | None) -> str:
    if tick is None or tick < 0:
        return "--:--"
    hh = tick // 60
    mm = tick % 60
    return f"{hh:02d}:{mm:02d}"


def resolve_timestamped_video_output_path(raw_output_path: str, base_dir: Path) -> Path:
    candidate = Path(str(raw_output_path).strip()) if str(raw_output_path).strip() else Path(DEFAULT_VIDEO_EXPORT_DIR)
    if not candidate.is_absolute():
        candidate = (base_dir.parent / candidate).resolve()
    if candidate.suffix:
        target_dir = candidate.parent
        base_stem = candidate.stem or DEFAULT_VIDEO_EXPORT_TOPIC
        suffix = candidate.suffix
    else:
        target_dir = candidate
        base_stem = DEFAULT_VIDEO_EXPORT_TOPIC
        suffix = ".mp4"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return (target_dir / f"{base_stem}_{timestamp}{suffix}").resolve()


def first_tick_true(values, predicate) -> int | None:
    for idx, value in enumerate(values, start=1):
        if predicate(value):
            return idx
    return None


def to_ships_ceil(value: float) -> int:
    v = int(value)
    if float(v) == float(value):
        return max(0, v)
    if value > 0.0:
        return max(0, v + 1)
    return 0


def resolve_name_with_fallback(
    side_data: dict,
    language: str,
    prefer_full_name: bool,
    fallback: str,
) -> str:
    if prefer_full_name:
        key = "full_name_ZH" if language == "ZH" else "full_name_EN"
    else:
        key = "disp_name_ZH" if language == "ZH" else "disp_name_EN"
    value = side_data.get(key)
    if value:
        return str(value)
    if prefer_full_name:
        alt_key = "full_name_EN"
    else:
        alt_key = "disp_name_EN"
    alt = side_data.get(alt_key)
    if alt:
        return str(alt)
    return fallback


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
        "AreaScale": 0.0,
        "orientation_theta": 0.0,
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

    n_units = len(u_values)
    if n_units > 0:
        group_size = max(1, int(math.ceil(0.3 * float(n_units))))
        sorted_indices = sorted(range(n_units), key=lambda i: u_values[i])
        rear_indices = sorted_indices[:group_size]
        front_indices = sorted_indices[-group_size:]
        v_rear = [v_values[i] for i in rear_indices]
        v_front = [v_values[i] for i in front_indices]
        width_front = _std_population(v_front)
        width_back = _std_population(v_rear)
        result["wedge_ratio"] = width_front / (width_back + BRIDGE_EPSILON)

    return result


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


def compute_bridge_event_ticks(bridge_telemetry: dict | None) -> dict:
    result = {
        "cut_per_side": {"A": None, "B": None},
        "pocket_per_side": {"A": None, "B": None},
        "formation_cut_tick": None,
        "pocket_formation_tick": None,
    }
    if not isinstance(bridge_telemetry, dict):
        return result

    split_ticks = bridge_telemetry.get("first_tick_split_sustain", {})
    env_ticks = bridge_telemetry.get("first_tick_env_sustain", {})
    if not isinstance(split_ticks, dict):
        split_ticks = {}
    if not isinstance(env_ticks, dict):
        env_ticks = {}

    def normalize_tick(raw):
        try:
            tick = int(raw)
        except (TypeError, ValueError):
            return None
        if tick < 1:
            return None
        return tick

    for side in ("A", "B"):
        result["cut_per_side"][side] = normalize_tick(split_ticks.get(side))
        result["pocket_per_side"][side] = normalize_tick(env_ticks.get(side))

    cut_candidates = [v for v in result["cut_per_side"].values() if isinstance(v, int)]
    env_candidates = [v for v in result["pocket_per_side"].values() if isinstance(v, int)]
    result["formation_cut_tick"] = min(cut_candidates) if cut_candidates else None
    result["pocket_formation_tick"] = min(env_candidates) if env_candidates else None
    return result


def build_battle_report_markdown(
    *,
    settings_source_path: str,
    display_language: str,
    random_seed_effective: int,
    fleet_a_data: dict,
    fleet_b_data: dict,
    initial_fleet_sizes: dict,
    alive_trajectory: dict,
    fleet_size_trajectory: dict,
    combat_telemetry: dict,
    bridge_telemetry: dict,
    final_state: BattleState,
    run_config_snapshot: dict,
) -> str:
    ticks = list(range(1, len(alive_trajectory.get("A", [])) + 1))
    alive_a = [int(v) for v in alive_trajectory.get("A", [])]
    alive_b = [int(v) for v in alive_trajectory.get("B", [])]
    size_a = [float(v) for v in fleet_size_trajectory.get("A", [])]
    size_b = [float(v) for v in fleet_size_trajectory.get("B", [])]
    in_contact = [int(v) for v in combat_telemetry.get("in_contact_count", [])]
    bridge_ticks = compute_bridge_event_ticks(bridge_telemetry)

    has_names = bool(
        fleet_a_data.get("disp_name_EN")
        and fleet_b_data.get("disp_name_EN")
        and fleet_a_data.get("full_name_EN")
        and fleet_b_data.get("full_name_EN")
    )

    if has_names:
        commander_a_zh = resolve_name_with_fallback(fleet_a_data, "ZH", True, "A")
        commander_b_zh = resolve_name_with_fallback(fleet_b_data, "ZH", True, "B")
        fleet_a_zh = resolve_name_with_fallback(fleet_a_data, "ZH", False, "A")
        fleet_b_zh = resolve_name_with_fallback(fleet_b_data, "ZH", False, "B")
        commander_a_en = resolve_name_with_fallback(fleet_a_data, "EN", True, "A")
        commander_b_en = resolve_name_with_fallback(fleet_b_data, "EN", True, "B")
        fleet_a_en = resolve_name_with_fallback(fleet_a_data, "EN", False, "A")
        fleet_b_en = resolve_name_with_fallback(fleet_b_data, "EN", False, "B")
    else:
        commander_a_zh = "A"
        commander_b_zh = "B"
        fleet_a_zh = "A"
        fleet_b_zh = "B"
        commander_a_en = "A"
        commander_b_en = "B"
        fleet_a_en = "A"
        fleet_b_en = "B"

    first_contact_tick = first_tick_true(in_contact, lambda v: int(v) > 0)
    first_kill_tick = first_tick_true(
        ticks,
        lambda i: (
            (alive_a[i - 1] < alive_a[i - 2]) if i > 1 else (alive_a[i - 1] < int(run_config_snapshot["initial_units_per_side"]))
        )
        or (
            (alive_b[i - 1] < alive_b[i - 2]) if i > 1 else (alive_b[i - 1] < int(run_config_snapshot["initial_units_per_side"]))
        ),
    )

    inflection_tick = None
    prev_sign = 0
    for i in ticks:
        delta = size_a[i - 1] - size_b[i - 1]
        if delta > 1e-9:
            sign = 1
        elif delta < -1e-9:
            sign = -1
        else:
            sign = 0
        if sign == 0:
            continue
        if prev_sign == 0:
            prev_sign = sign
            continue
        if sign != prev_sign:
            inflection_tick = i
            break

    initial_hp_a = float(initial_fleet_sizes.get("A", 0.0))
    initial_hp_b = float(initial_fleet_sizes.get("B", 0.0))
    endgame_tick = first_tick_true(
        ticks,
        lambda i: (
            size_a[i - 1] <= (initial_hp_a * ENDGAME_HP_RATIO_DEFAULT)
            or size_b[i - 1] <= (initial_hp_b * ENDGAME_HP_RATIO_DEFAULT)
        ),
    )

    end_tick = int(final_state.tick)
    final_hp_a = float(size_a[-1]) if size_a else 0.0
    final_hp_b = float(size_b[-1]) if size_b else 0.0
    final_units_a = int(alive_a[-1]) if alive_a else 0
    final_units_b = int(alive_b[-1]) if alive_b else 0
    final_ships_a = to_ships_ceil(final_hp_a)
    final_ships_b = to_ships_ceil(final_hp_b)

    winner = "A"
    if final_hp_b > final_hp_a:
        winner = "B"
    elif abs(final_hp_a - final_hp_b) <= 1e-9:
        winner = "Draw"

    if winner == "A":
        final_outcome_zh = (
            f"至标准时{tick_to_std_time(end_tick)} (t={end_tick})，{fleet_b_zh}舰队全灭，"
            f"{fleet_a_zh}舰队残余{final_ships_a}艘 (A units={final_units_a})。"
        )
        final_outcome_en = (
            f"By ST {tick_to_std_time(end_tick)} (t={end_tick}), {fleet_b_en} Fleet was eliminated, "
            f"and {fleet_a_en} Fleet retained {final_ships_a} ships (A units={final_units_a})."
        )
    elif winner == "B":
        final_outcome_zh = (
            f"至标准时{tick_to_std_time(end_tick)} (t={end_tick})，{fleet_a_zh}舰队全灭，"
            f"{fleet_b_zh}舰队残余{final_ships_b}艘 (B units={final_units_b})。"
        )
        final_outcome_en = (
            f"By ST {tick_to_std_time(end_tick)} (t={end_tick}), {fleet_a_en} Fleet was eliminated, "
            f"and {fleet_b_en} Fleet retained {final_ships_b} ships (B units={final_units_b})."
        )
    else:
        final_outcome_zh = (
            f"至标准时{tick_to_std_time(end_tick)} (t={end_tick})，战斗结束为平局，"
            f"A残余{final_ships_a}艘 (A units={final_units_a})，"
            f"B残余{final_ships_b}艘 (B units={final_units_b})。"
        )
        final_outcome_en = (
            f"By ST {tick_to_std_time(end_tick)} (t={end_tick}), the battle ended in a draw: "
            f"A retained {final_ships_a} ships (A units={final_units_a}), "
            f"B retained {final_ships_b} ships (B units={final_units_b})."
        )

    events_zh = []
    if first_contact_tick is not None:
        events_zh.append(
            (
                int(first_contact_tick),
                f"双方在标准时{tick_to_std_time(first_contact_tick)} (t={first_contact_tick}) 开始交火。",
            )
        )
    if inflection_tick is not None:
        if size_a[inflection_tick - 1] > size_b[inflection_tick - 1]:
            side_zh = f"{fleet_a_zh}舰队"
        else:
            side_zh = f"{fleet_b_zh}舰队"

        if first_kill_tick is not None and inflection_tick < first_kill_tick:
            prefix_zh = "在首批建制伤亡前"
        elif first_contact_tick is not None and (inflection_tick - first_contact_tick) <= 10:
            prefix_zh = "在初段接触后"
        elif first_kill_tick is not None and (inflection_tick - first_kill_tick) <= 20:
            prefix_zh = "在早段拉扯后"
        else:
            prefix_zh = "在中段拉扯后"

        events_zh.append(
            (
                int(inflection_tick),
                (
                    f"战线{prefix_zh}，于标准时{tick_to_std_time(inflection_tick)} (t={inflection_tick}) "
                    f"出现优势拐点，{side_zh}逐步掌握主动。"
                ),
            )
        )
    if first_kill_tick is not None:
        events_zh.append(
            (
                int(first_kill_tick),
                f"双方在标准时{tick_to_std_time(first_kill_tick)} (t={first_kill_tick}) 出现成建制伤亡。",
            )
        )
    if endgame_tick is not None:
        events_zh.append(
            (
                int(endgame_tick),
                f"标准时{tick_to_std_time(endgame_tick)} (t={endgame_tick}) 后，战局进入终盘压制。",
            )
        )
    events_zh.sort(key=lambda item: item[0])

    events_en = []
    if first_contact_tick is not None:
        events_en.append(
            (
                int(first_contact_tick),
                f"The fleets started exchanging fire at ST {tick_to_std_time(first_contact_tick)} (t={first_contact_tick}).",
            )
        )
    if inflection_tick is not None:
        if size_a[inflection_tick - 1] > size_b[inflection_tick - 1]:
            side_en = f"{fleet_a_en} Fleet"
        else:
            side_en = f"{fleet_b_en} Fleet"

        if first_kill_tick is not None and inflection_tick < first_kill_tick:
            prefix_en = "Before the first organized losses"
        elif first_contact_tick is not None and (inflection_tick - first_contact_tick) <= 10:
            prefix_en = "Shortly after first contact"
        elif first_kill_tick is not None and (inflection_tick - first_kill_tick) <= 20:
            prefix_en = "After early-phase exchanges"
        else:
            prefix_en = "After a mid-line tug of war"

        events_en.append(
            (
                int(inflection_tick),
                (
                    f"{prefix_en}, an advantage inflection appeared at ST "
                    f"{tick_to_std_time(inflection_tick)} (t={inflection_tick}), and {side_en} gradually took initiative."
                ),
            )
        )
    if first_kill_tick is not None:
        events_en.append(
            (
                int(first_kill_tick),
                f"Organized losses appeared at ST {tick_to_std_time(first_kill_tick)} (t={first_kill_tick}).",
            )
        )
    if endgame_tick is not None:
        events_en.append(
            (
                int(endgame_tick),
                f"After ST {tick_to_std_time(endgame_tick)} (t={endgame_tick}), the battle entered endgame suppression.",
            )
        )
    events_en.sort(key=lambda item: item[0])

    seed_word = seed_word_from_int(random_seed_effective, length=6)
    initial_units_per_side = int(run_config_snapshot["initial_units_per_side"])
    initial_ships_a = to_ships_ceil(initial_hp_a)
    initial_ships_b = to_ships_ceil(initial_hp_b)

    fixed_lead_zh_lines = [
        f"{seed_word} 星域会战",
        f"{commander_a_zh}(A) vs {commander_b_zh}(B)",
        f"{fleet_a_zh}舰队: {initial_ships_a}艘 (A: {initial_units_per_side} units); {fleet_b_zh}舰队: {initial_ships_b}艘 (B: {initial_units_per_side} units)",
    ]
    fixed_lead_en_lines = [
        f"{seed_word} Starfield Engagement",
        f"{commander_a_en}(A) vs {commander_b_en}(B)",
        f"{fleet_a_en} Fleet: {initial_ships_a} ships (A: {initial_units_per_side} units); {fleet_b_en} Fleet: {initial_ships_b} ships (B: {initial_units_per_side} units)",
    ]

    narrative_zh_body = " ".join(item[1] for item in events_zh) if events_zh else "双方全程未形成有效交火。"
    narrative_en_body = " ".join(item[1] for item in events_en) if events_en else "No effective fire exchange occurred."

    tactical_narrative_zh = "\n".join(fixed_lead_zh_lines) + "\n\n" + narrative_zh_body + f" {final_outcome_zh}"
    tactical_narrative_en = "\n".join(fixed_lead_en_lines) + "\n\n" + narrative_en_body + f" {final_outcome_en}"

    param_keys = [
        "force_concentration_ratio",
        "mobility_bias",
        "offense_defense_weight",
        "risk_appetite",
        "time_preference",
        "targeting_logic",
        "formation_rigidity",
        "perception_radius",
        "pursuit_drive",
        "retreat_threshold",
    ]

    def format_param_value(v):
        if isinstance(v, (int, float)):
            return f"{float(v):.1f}"
        return "n/a"

    table_header = ["Side", "Archetype", *param_keys]
    archetype_lines = [
        "| " + " | ".join(table_header) + " |",
        "| " + " | ".join(["---"] * len(table_header)) + " |",
        "| " + " | ".join([
            "A",
            str(fleet_a_data.get("name", "A")),
            *[format_param_value(fleet_a_data.get(k)) for k in param_keys],
        ]) + " |",
        "| " + " | ".join([
            "B",
            str(fleet_b_data.get("name", "B")),
            *[format_param_value(fleet_b_data.get(k)) for k in param_keys],
        ]) + " |",
    ]

    report_date = datetime.now().strftime("%Y-%m-%d")
    report_lines = [
        "# Battle Report Framework v1.0",
        "",
        "## 0. Run Configuration Snapshot",
        f"- Source settings path: `{settings_source_path}`",
        f"- display_language: `{display_language}`",
        f"- attack_range: `{run_config_snapshot['attack_range']}`",
        f"- min_unit_spacing: `{run_config_snapshot['min_unit_spacing']}`",
        f"- arena_size: `{run_config_snapshot['arena_size']}`",
        f"- max_time_steps_effective: `{run_config_snapshot['max_time_steps_effective']}`",
        f"- unit_speed: `{run_config_snapshot['unit_speed']}`",
        f"- damage_per_tick: `{run_config_snapshot['damage_per_tick']}`",
        f"- ch_enabled / contact_hysteresis_h: `{run_config_snapshot['ch_enabled']}` / `{run_config_snapshot['contact_hysteresis_h']}`",
        f"- fsr_enabled / fsr_strength: `{run_config_snapshot['fsr_enabled']}` / `{run_config_snapshot['fsr_strength']}`",
        f"- boundary_enabled: `{run_config_snapshot['boundary_enabled']}`",
        "- overrides_applied: none",
        "",
        "## 1. Header",
        "- Engine Version: v5.0-alpha5",
        (
            "- Grid Parameters: "
            f"A={fleet_a_data.get('name', 'A')} vs B={fleet_b_data.get('name', 'B')}, "
            f"units_per_side={initial_units_per_side}"
        ),
        "- Determinism Status: Not checked in this single-run export",
        f"- Date: {report_date}",
        "",
        "## 2. Operational Timeline",
        "| Event | Tick |",
        "| --- | --- |",
        f"| First Contact | {first_contact_tick if first_contact_tick is not None else 'N/A'} |",
        f"| First Kill | {first_kill_tick if first_kill_tick is not None else 'N/A'} |",
        f"| Formation Cut | {bridge_ticks['formation_cut_tick'] if bridge_ticks['formation_cut_tick'] is not None else 'N/A'} |",
        f"| Pocket Formation | {bridge_ticks['pocket_formation_tick'] if bridge_ticks['pocket_formation_tick'] is not None else 'N/A'} |",
        "| Pursuit Mode | N/A |",
        f"| Inflection | {inflection_tick if inflection_tick is not None else 'N/A'} |",
        f"| Endgame Onset | {endgame_tick if endgame_tick is not None else 'N/A'} |",
        f"| End | {end_tick} |",
        "",
        "## 3. Tactical Narrative (Auto-generated)",
        "### 3.1 Archetypes",
        *archetype_lines,
        "",
        "### 3.2 ZH Narrative",
        tactical_narrative_zh,
        "",
        "### 3.3 EN Narrative",
        tactical_narrative_en,
        "",
        "## 4. Structural Metrics Summary",
        "- Mirror delta: N/A",
        "- Jitter delta: N/A",
        "- Runtime delta: N/A",
        "- Cohesion behavior summary: Runtime path unchanged; this export is observer/report-layer only.",
        "",
        "## 5. Collapse Analysis",
        "- Collapse occurred before contact: N/A",
        "- Collapse preceded or aligned with pursuit mode: N/A",
        "- Collapse aligned with formation cut (|delta_tick|<=1): N/A",
        "",
    ]
    return "\n".join(report_lines)

def build_initial_state(
    fleet_a_params: PersonalityParameters,
    fleet_b_params: PersonalityParameters,
    fleet_size: int,
    aspect_ratio: float,
    unit_spacing: float,
    unit_speed: float,
    unit_max_hit_points: float,
    arena_size: float,
) -> BattleState:
    grid_columns = max(1, int((fleet_size * aspect_ratio) ** 0.5))
    grid_rows = (fleet_size + grid_columns - 1) // grid_columns
    while grid_columns / max(1, grid_rows) < aspect_ratio and grid_columns < fleet_size:
        grid_columns += 1
        grid_rows = (fleet_size + grid_columns - 1) // grid_columns

    spawn_margin = max(1.0, arena_size * DEFAULT_SPAWN_MARGIN_RATIO)
    fleet_a_origin_x = spawn_margin
    fleet_a_origin_y = spawn_margin
    fleet_b_origin_x = arena_size - spawn_margin
    fleet_b_origin_y = arena_size - spawn_margin

    dx_ab = fleet_b_origin_x - fleet_a_origin_x
    dy_ab = fleet_b_origin_y - fleet_a_origin_y
    norm_ab = (dx_ab * dx_ab + dy_ab * dy_ab) ** 0.5
    if norm_ab > 0.0:
        dir_a = (dx_ab / norm_ab, dy_ab / norm_ab)
    else:
        dir_a = (1.0, 0.0)
    dir_b = (-dir_a[0], -dir_a[1])

    perp_a = (-dir_a[1], dir_a[0])
    perp_b = (-dir_b[1], dir_b[0])
    half_width = (grid_columns - 1) / 2.0

    units = {}
    fleet_a_unit_ids = []
    fleet_b_unit_ids = []

    for i in range(fleet_size):
        row = i // grid_columns
        col = i % grid_columns
        lateral = col - half_width

        unit_a_id = f"A{i + 1}"
        ax = fleet_a_origin_x + (dir_a[0] * row * unit_spacing) + (perp_a[0] * lateral * unit_spacing)
        ay = fleet_a_origin_y + (dir_a[1] * row * unit_spacing) + (perp_a[1] * lateral * unit_spacing)
        units[unit_a_id] = UnitState(
            unit_id=unit_a_id,
            fleet_id="A",
            position=Vec2(x=clamp(ax, 0.0, arena_size), y=clamp(ay, 0.0, arena_size)),
            velocity=Vec2(x=0.0, y=0.0),
            hit_points=unit_max_hit_points,
            max_hit_points=unit_max_hit_points,
            max_speed=unit_speed,
        )
        fleet_a_unit_ids.append(unit_a_id)

        unit_b_id = f"B{i + 1}"
        bx = fleet_b_origin_x + (dir_b[0] * row * unit_spacing) + (perp_b[0] * lateral * unit_spacing)
        by = fleet_b_origin_y + (dir_b[1] * row * unit_spacing) + (perp_b[1] * lateral * unit_spacing)
        units[unit_b_id] = UnitState(
            unit_id=unit_b_id,
            fleet_id="B",
            position=Vec2(x=clamp(bx, 0.0, arena_size), y=clamp(by, 0.0, arena_size)),
            velocity=Vec2(x=0.0, y=0.0),
            hit_points=unit_max_hit_points,
            max_hit_points=unit_max_hit_points,
            max_speed=unit_speed,
        )
        fleet_b_unit_ids.append(unit_b_id)

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
    return initialize_unit_orientations(state)


def run_simulation(
    initial_state: BattleState,
    steps: int,
    capture_positions: bool,
    observer_enabled: bool,
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
    include_target_lines: bool,
    print_tick_summary: bool,
):
    engine = EngineTickSkeleton(
        attack_range=attack_range,
        damage_per_tick=damage_per_tick,
        separation_radius=separation_radius,
    )
    engine.fire_quality_alpha = float(fire_quality_alpha)
    engine.contact_hysteresis_h = float(contact_hysteresis_h)
    engine.CH_ENABLED = bool(ch_enabled)
    engine.FSR_ENABLED = bool(fsr_enabled)
    engine.fsr_strength = float(fsr_strength)
    engine.BOUNDARY_SOFT_ENABLED = bool(boundary_enabled)
    engine.BOUNDARY_HARD_ENABLED = bool(boundary_enabled)
    # Observer diagnostics are explicitly gated by run setting.
    observer_active = bool(capture_positions) and bool(observer_enabled)
    # Visualization debug panel consumes these runtime diagnostics per frame.
    engine.debug_fsr_diag_enabled = observer_active
    engine.debug_diag4_enabled = observer_active
    engine.debug_diag4_rpg_enabled = False
    engine.debug_cohesion_v3_shadow_enabled = bool(observer_enabled)

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
    }
    combat_telemetry = {
        "in_contact_count": [],
        "damage_events_count": [],
    }
    bridge_telemetry = {
        "theta_split": BRIDGE_THETA_SPLIT_DEFAULT,
        "theta_env": BRIDGE_THETA_ENV_DEFAULT,
        "sustain_ticks": BRIDGE_SUSTAIN_TICKS_DEFAULT,
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
            for unit_id in fleet.unit_ids:
                if unit_id in state.units:
                    fleet_size += max(0.0, float(state.units[unit_id].hit_points))
            fleet_size_trajectory[fleet_id].append(fleet_size)
        shadow_v3 = getattr(engine, "debug_last_cohesion_v3", {})
        if not isinstance(shadow_v3, dict):
            shadow_v3 = {}
        shadow_v3_components = getattr(engine, "debug_last_cohesion_v3_components", {})
        if not isinstance(shadow_v3_components, dict):
            shadow_v3_components = {}
        for fleet_id in state.fleets:
            fallback_v2 = float(state.last_fleet_cohesion.get(fleet_id, 1.0))
            if observer_enabled:
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
            if observer_enabled:
                metric = bridge_metrics.get(fleet_id, {})
                split_value = float(metric.get("split_separation", 0.0))
                env_value = float(metric.get("angle_coverage", 0.0))
                split_cond = bool(
                    state.tick >= 1 and contact_active_tick and split_value >= BRIDGE_THETA_SPLIT_DEFAULT
                )
                env_cond = bool(
                    state.tick >= 1 and contact_active_tick and env_value >= BRIDGE_THETA_ENV_DEFAULT
                )
            else:
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
                split_counter_state[fleet_id] >= BRIDGE_SUSTAIN_TICKS_DEFAULT
                and bridge_telemetry["first_tick_split_sustain"].get(fleet_id) is None
            ):
                bridge_telemetry["first_tick_split_sustain"][fleet_id] = int(state.tick)
                cut_event_tick = True
            if (
                env_counter_state[fleet_id] >= BRIDGE_SUSTAIN_TICKS_DEFAULT
                and bridge_telemetry["first_tick_env_sustain"].get(fleet_id) is None
            ):
                bridge_telemetry["first_tick_env_sustain"][fleet_id] = int(state.tick)
                pocket_event_tick = True

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
                post_elimination_stop_tick = min(999, elimination_tick + 10)
            if post_elimination_stop_tick is not None and state.tick >= post_elimination_stop_tick:
                break
        else:
            if any_fleet_eliminated:
                break

    return (
        state,
        trajectory,
        alive_trajectory,
        fleet_size_trajectory,
        observer_telemetry,
        combat_telemetry,
        bridge_telemetry,
        position_frames,
    )


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    settings = json.loads((base_dir / "test_run_v1_0.settings.json").read_text(encoding="utf-8"))
    viz_settings = json.loads((base_dir / "test_run_v1_0.viz.settings.json").read_text(encoding="utf-8"))
    archetypes = json.loads((base_dir / "archetypes_v1_5.json").read_text(encoding="utf-8"))

    fleet_a_data = resolve_archetype(archetypes, get_fleet_setting(settings, "fleet_a_archetype_id", "default"))
    fleet_b_data = resolve_archetype(archetypes, get_fleet_setting(settings, "fleet_b_archetype_id", "default"))
    fleet_a_params = to_personality_parameters(fleet_a_data)
    fleet_b_params = to_personality_parameters(fleet_b_data)
    fleet_a_color = to_plot_color(fleet_a_data, DEFAULT_PLOT_COLORS[0])
    fleet_b_color = to_plot_color(fleet_b_data, DEFAULT_PLOT_COLORS[1])

    display_language = str(get_run_control_setting(settings, "display_language", "EN")).upper()
    if display_language not in ("EN", "ZH"):
        display_language = "EN"
    fleet_a_display_name = resolve_display_name(fleet_a_data, display_language)
    fleet_b_display_name = resolve_display_name(fleet_b_data, display_language)

    fleet_size = int(get_fleet_setting(settings, "initial_fleet_size", 100))
    aspect_ratio = float(get_fleet_setting(settings, "initial_fleet_aspect_ratio", 2.0))
    unit_spacing = float(get_battlefield_setting(settings, "min_unit_spacing", 1.0))
    if fleet_size < 1:
        raise ValueError(f"initial_fleet_size must be >= 1, got {fleet_size}")
    if aspect_ratio <= 0.0:
        raise ValueError(f"initial_fleet_aspect_ratio must be > 0, got {aspect_ratio}")
    if unit_spacing <= 0.0:
        raise ValueError(f"min_unit_spacing must be > 0, got {unit_spacing}")

    unit_speed = float(get_unit_setting(settings, "unit_speed", 1.0))
    unit_max_hit_points = float(get_unit_setting(settings, "unit_max_hit_points", 100.0))
    arena_size = float(get_battlefield_setting(settings, "arena_size", 200.0))
    state = build_initial_state(
        fleet_a_params=fleet_a_params,
        fleet_b_params=fleet_b_params,
        fleet_size=fleet_size,
        aspect_ratio=aspect_ratio,
        unit_spacing=unit_spacing,
        unit_speed=unit_speed,
        unit_max_hit_points=unit_max_hit_points,
        arena_size=arena_size,
    )

    initial_fleet_sizes = {}
    for fleet_id, fleet in state.fleets.items():
        fleet_size_hp = 0.0
        for unit_id in fleet.unit_ids:
            if unit_id in state.units:
                fleet_size_hp += max(0.0, float(state.units[unit_id].hit_points))
        initial_fleet_sizes[fleet_id] = fleet_size_hp

    animate = bool(get_run_control_setting(settings, "animate", True))
    visualization_section = get_visualization_section(settings)
    auto_zoom_2d = bool(get_visualization_setting(settings, "auto_zoom_2d", False))
    frame_stride = DEFAULT_FRAME_STRIDE
    base_frame_interval_ms = max(1, int(get_visualization_setting(settings, "animation_frame_interval_ms", 100)))
    animation_play_speed = float(get_visualization_setting(settings, "animation_play_speed", 1.0))
    if animation_play_speed <= 0.0:
        animation_play_speed = 1.0
    frame_interval_ms = max(1, int(round(base_frame_interval_ms / animation_play_speed)))
    attack_range = float(get_unit_setting(settings, "attack_range", get_runtime_setting(settings, "attack_range", 3.0)))
    damage_per_tick = float(get_unit_setting(settings, "damage_per_tick", get_runtime_setting(settings, "damage_per_tick", 1.0)))
    fire_quality_alpha = float(get_runtime_setting(settings, "fire_quality_alpha", 0.1))
    contact_hysteresis_h = float(get_runtime_setting(settings, "contact_hysteresis_h", 0.1))
    fsr_strength = float(get_runtime_setting(settings, "fsr_strength", 0.0))
    # Canonical runtime toggle rule (strength-only):
    # - contact_hysteresis_h <= 0 => CH disabled
    # - fsr_strength <= 0 => FSR disabled
    ch_enabled = contact_hysteresis_h > 0.0
    fsr_enabled = fsr_strength > 0.0
    boundary_enabled = bool(get_runtime_setting(settings, "boundary_enabled", False))
    unit_direction_mode = str(get_visualization_setting(settings, "unit_direction_mode", "effective")).strip().lower()
    if unit_direction_mode not in {"effective", "free", "attack", "composite"}:
        unit_direction_mode = "effective"
    show_attack_target_lines = bool(get_visualization_setting(settings, "show_attack_target_lines", False))
    tick_plots_follow_battlefield_tick = bool(get_visualization_setting(settings, "tick_plots_follow_battlefield_tick", False))
    print_tick_summary = bool(get_visualization_setting(settings, "print_tick_summary", True))
    observer_enabled = bool(get_run_control_setting(settings, "observer_enabled", True))
    export_battle_report = bool(get_run_control_setting(settings, "export_battle_report", True))
    random_seed = int(get_run_control_setting(settings, "random_seed", get_seed_setting(settings, "random_seed", -1)))
    background_map_seed = int(
        get_battlefield_setting(settings, "background_map_seed", get_seed_setting(settings, "background_map_seed", -1))
    )
    effective_random_seed = resolve_effective_seed(random_seed)
    effective_background_map_seed = resolve_effective_seed(background_map_seed)
    print(f"[viz] random_seed_effective={effective_random_seed}")
    print(f"[viz] background_map_seed_effective={effective_background_map_seed}")
    print(
        f"[viz] animation_play_speed={animation_play_speed:.2f}, "
        f"base_interval_ms={base_frame_interval_ms}, frame_interval_ms={frame_interval_ms}"
    )
    print(f"[viz] unit_direction_mode={unit_direction_mode}")
    print(f"[observer] enabled={observer_enabled}")
    export_video_cfg = visualization_section.get("export_video", {})
    if not isinstance(export_video_cfg, dict):
        export_video_cfg = {}
    else:
        export_video_cfg = dict(export_video_cfg)
    raw_video_output_path = str(export_video_cfg.get("output_path", DEFAULT_VIDEO_EXPORT_DIR))
    resolved_video_output_path = resolve_timestamped_video_output_path(raw_video_output_path, base_dir=base_dir)
    export_video_cfg["output_path"] = str(resolved_video_output_path)

    capture_target_directions = show_attack_target_lines or (unit_direction_mode in {"attack", "composite"})
    (
        final_state,
        trajectory,
        alive_trajectory,
        fleet_size_trajectory,
        observer_telemetry,
        combat_telemetry,
        bridge_telemetry,
        position_frames,
    ) = run_simulation(
        initial_state=state,
        steps=int(get_run_control_setting(settings, "max_time_steps", -1)),
        capture_positions=animate,
        observer_enabled=observer_enabled,
        frame_stride=frame_stride,
        attack_range=attack_range,
        damage_per_tick=damage_per_tick,
        separation_radius=unit_spacing,
        fire_quality_alpha=fire_quality_alpha,
        contact_hysteresis_h=contact_hysteresis_h,
        ch_enabled=ch_enabled,
        fsr_enabled=fsr_enabled,
        fsr_strength=fsr_strength,
        boundary_enabled=boundary_enabled,
        include_target_lines=capture_target_directions,
        print_tick_summary=print_tick_summary,
    )
    if not animate:
        position_frames = []

    max_time_steps_effective = int(final_state.tick)
    run_config_snapshot = {
        "initial_units_per_side": int(fleet_size),
        "attack_range": attack_range,
        "min_unit_spacing": unit_spacing,
        "arena_size": arena_size,
        "max_time_steps_effective": max_time_steps_effective,
        "unit_speed": unit_speed,
        "damage_per_tick": damage_per_tick,
        "ch_enabled": ch_enabled,
        "contact_hysteresis_h": contact_hysteresis_h,
        "fsr_enabled": fsr_enabled,
        "fsr_strength": fsr_strength,
        "boundary_enabled": boundary_enabled,
    }

    if export_battle_report:
        report_markdown = build_battle_report_markdown(
            settings_source_path=str((base_dir / "test_run_v1_0.settings.json").as_posix()),
            display_language=display_language,
            random_seed_effective=effective_background_map_seed,
            fleet_a_data=fleet_a_data,
            fleet_b_data=fleet_b_data,
            initial_fleet_sizes=initial_fleet_sizes,
            alive_trajectory=alive_trajectory,
            fleet_size_trajectory=fleet_size_trajectory,
            combat_telemetry=combat_telemetry,
            bridge_telemetry=bridge_telemetry,
            final_state=final_state,
            run_config_snapshot=run_config_snapshot,
        )
        report_date_dir = datetime.now().strftime("%Y%m%d")
        report_export_dir = (base_dir.parent / DEFAULT_BATTLE_REPORT_EXPORT_DIR / report_date_dir).resolve()
        report_export_dir.mkdir(parents=True, exist_ok=True)
        report_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"{DEFAULT_BATTLE_REPORT_TOPIC}_{report_timestamp}_Battle_Report_Framework_v1.0.md"
        report_output_path = report_export_dir / report_filename
        report_output_path.write_text(report_markdown, encoding="utf-8")
        print(f"[report] battle_report_exported={report_output_path}")

    if not animate:
        return

    try:
        from test_run_v1_0_viz import render_test_run
    except ModuleNotFoundError as exc:
        print(f"[viz] skipped: {exc}")
        return

    render_test_run(
        arena_size=arena_size,
        trajectory=trajectory,
        alive_trajectory=alive_trajectory,
        fleet_size_trajectory=fleet_size_trajectory,
        initial_fleet_sizes=initial_fleet_sizes,
        position_frames=position_frames,
        final_state=final_state,
        fleet_a_label=fleet_a_display_name,
        fleet_b_label=fleet_b_display_name,
        fleet_a_color=fleet_a_color,
        fleet_b_color=fleet_b_color,
        auto_zoom_2d=auto_zoom_2d,
        frame_interval_ms=frame_interval_ms,
        background_seed=effective_background_map_seed,
        viz_settings=viz_settings,
        tick_plots_follow_battlefield_tick=tick_plots_follow_battlefield_tick,
        display_language=display_language,
        unit_direction_mode=unit_direction_mode,
        show_attack_target_lines=show_attack_target_lines,
        observer_telemetry=observer_telemetry,
        observer_enabled=observer_enabled,
        export_video_cfg=export_video_cfg,
    )


if __name__ == "__main__":
    main()
