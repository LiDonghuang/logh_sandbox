import json
import random
from dataclasses import replace
from pathlib import Path

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
from test_run_v1_0_viz import render_test_run


DEFAULT_DT = 1.0
DEFAULT_SPAWN_MARGIN_RATIO = 0.05
DEFAULT_FRAME_STRIDE = 1
DEFAULT_PLOT_COLORS = ("#1f77b4", "#ff7f0e")


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
            "pursuit_threshold": 5.0,
            "retreat_threshold": 5.0,
        }
    if archetype_ref in archetypes:
        return archetypes[archetype_ref]
    raise KeyError(archetype_ref)


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
        pursuit_threshold=float(data["pursuit_threshold"]),
        retreat_threshold=float(data["retreat_threshold"]),
    )


def to_archetype_debug_payload(params: PersonalityParameters) -> dict:
    return {
        "id": params.archetype_id,
        "fcr": float(params.force_concentration_ratio),
        "mb": float(params.mobility_bias),
        "odw": float(params.offense_defense_weight),
        "ra": float(params.risk_appetite),
        "tp": float(params.time_preference),
        "tl": float(params.targeting_logic),
        "fr": float(params.formation_rigidity),
        "pr": float(params.perception_radius),
        "pt": float(params.pursuit_threshold),
        "rt": float(params.retreat_threshold),
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
    # Visualization debug panel consumes these runtime diagnostics per frame.
    engine.debug_fsr_diag_enabled = bool(capture_positions)
    engine.debug_diag4_enabled = bool(capture_positions)
    engine.debug_diag4_rpg_enabled = False

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
        for fleet_id, fleet in state.fleets.items():
            print(
                f"tick={state.tick}, fleet_id={fleet.parameters.archetype_id}, alive_units={len(fleet.unit_ids)}"
            )
        for fleet_id, fleet in state.fleets.items():
            trajectory[fleet_id].append(state.last_fleet_cohesion.get(fleet_id, 1.0))
            alive_trajectory[fleet_id].append(len(fleet.unit_ids))
            fleet_size = 0.0
            for unit_id in fleet.unit_ids:
                if unit_id in state.units:
                    fleet_size += max(0.0, float(state.units[unit_id].hit_points))
            fleet_size_trajectory[fleet_id].append(fleet_size)

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
                getattr(engine, "debug_diag_last_tick", {})
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

    return state, trajectory, alive_trajectory, fleet_size_trajectory, position_frames


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    settings = json.loads((base_dir / "test_run_v1_0.settings.json").read_text(encoding="utf-8"))
    viz_settings = json.loads((base_dir / "test_run_v1_0.viz.settings.json").read_text(encoding="utf-8"))
    archetypes = json.loads((base_dir / "archetypes_v1_5.json").read_text(encoding="utf-8"))

    fleet_a_data = resolve_archetype(archetypes, settings["fleet_a_archetype_id"])
    fleet_b_data = resolve_archetype(archetypes, settings["fleet_b_archetype_id"])
    fleet_a_params = to_personality_parameters(fleet_a_data)
    fleet_b_params = to_personality_parameters(fleet_b_data)
    fleet_a_color = to_plot_color(fleet_a_data, DEFAULT_PLOT_COLORS[0])
    fleet_b_color = to_plot_color(fleet_b_data, DEFAULT_PLOT_COLORS[1])

    display_language = str(settings.get("display_language", "EN")).upper()
    if display_language not in ("EN", "ZH"):
        display_language = "EN"
    fleet_a_display_name = resolve_display_name(fleet_a_data, display_language)
    fleet_b_display_name = resolve_display_name(fleet_b_data, display_language)

    fleet_size = int(settings["initial_fleet_size"])
    aspect_ratio = float(settings.get("initial_fleet_aspect_ratio", 2.0))
    unit_spacing = float(settings.get("min_unit_spacing", 1.0))
    if fleet_size < 1:
        raise ValueError(f"initial_fleet_size must be >= 1, got {fleet_size}")
    if aspect_ratio <= 0.0:
        raise ValueError(f"initial_fleet_aspect_ratio must be > 0, got {aspect_ratio}")
    if unit_spacing <= 0.0:
        raise ValueError(f"min_unit_spacing must be > 0, got {unit_spacing}")

    unit_speed = float(settings.get("unit_speed", 1.0))
    unit_max_hit_points = float(settings.get("unit_max_hit_points", 100.0))
    arena_size = float(settings["arena_size"])
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

    animate = bool(settings.get("animate", True))
    auto_zoom_2d = bool(settings.get("auto_zoom_2d", False))
    frame_stride = DEFAULT_FRAME_STRIDE
    frame_interval_ms = max(1, 100 * frame_stride)
    attack_range = float(settings.get("attack_range", 3.0))
    damage_per_tick = float(settings.get("damage_per_tick", 1.0))
    fire_quality_alpha = float(settings.get("fire_quality_alpha", 0.1))
    contact_hysteresis_h = float(settings.get("contact_hysteresis_h", 0.1))
    ch_enabled = bool(settings.get("ch_enabled", True))
    fsr_enabled = bool(settings.get("fsr_enabled", False))
    fsr_strength = float(settings.get("fsr_strength", 0.0))
    boundary_enabled = bool(settings.get("boundary_enabled", False))
    show_attack_target_lines = bool(settings.get("show_attack_target_lines", False))
    random_seed = int(settings.get("random_seed", -1))
    background_map_seed = int(settings.get("background_map_seed", -1))
    effective_random_seed = resolve_effective_seed(random_seed)
    effective_background_map_seed = resolve_effective_seed(background_map_seed)
    print(f"[viz] random_seed_effective={effective_random_seed}")
    print(f"[viz] background_map_seed_effective={effective_background_map_seed}")

    final_state, trajectory, alive_trajectory, fleet_size_trajectory, position_frames = run_simulation(
        initial_state=state,
        steps=int(settings["max_time_steps"]),
        capture_positions=animate,
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
        include_target_lines=show_attack_target_lines,
    )
    if not animate:
        position_frames = []

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
        fleet_a_archetype_debug=to_archetype_debug_payload(fleet_a_params),
        fleet_b_archetype_debug=to_archetype_debug_payload(fleet_b_params),
        show_attack_target_lines=show_attack_target_lines,
    )


if __name__ == "__main__":
    main()
