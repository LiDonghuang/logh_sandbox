import json
import math
import random
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.lines import Line2D
from matplotlib.patches import Circle, Ellipse

from runtime_v0_1 import (
    PersonalityParameters,
    Vec2,
    UnitState,
    FleetState,
    BattleState,
    build_initial_cohesion_map,
    initialize_unit_orientations,
)
from runtime.engine_driver_dummy import run_dummy_ticks


base_dir = Path(__file__).resolve().parent
settings = json.loads((base_dir / "test_run_v1_0.settings.json").read_text(encoding="utf-8"))
archetypes = json.loads((base_dir / "archetypes_v1_5.json").read_text(encoding="utf-8"))
DEFAULT_DT = 1.0
DEFAULT_SPAWN_MARGIN_RATIO = 0.05
DEFAULT_FRAME_STRIDE = 1


def resolve_archetype(archetype_ref: str):
    if archetype_ref == "default":
        return {
            "archetype_id": "default",
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
    for data in archetypes.values():
        if data.get("archetype_id") == archetype_ref:
            return data
    raise KeyError(archetype_ref)


def to_personality_parameters(data: dict) -> PersonalityParameters:
    return PersonalityParameters(
        archetype_id=data["archetype_id"],
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


def to_plot_color(data: dict, fallback: str) -> str:
    code = str(data.get("color_code", "")).strip()
    if not code:
        code = fallback
    if code.startswith("#"):
        return code
    return f"#{code}"


fleet_a_data = resolve_archetype(settings["fleet_a_archetype_id"])
fleet_b_data = resolve_archetype(settings["fleet_b_archetype_id"])

fleet_a_params = to_personality_parameters(fleet_a_data)
fleet_b_params = to_personality_parameters(fleet_b_data)
default_colors = plt.rcParams["axes.prop_cycle"].by_key().get("color", ["#1f77b4", "#ff7f0e"])
fleet_a_color = to_plot_color(fleet_a_data, default_colors[0])
fleet_b_color = to_plot_color(fleet_b_data, default_colors[1 if len(default_colors) > 1 else 0])

fleet_size = int(settings["initial_fleet_size"])
aspect_ratio = float(settings.get("initial_fleet_aspect_ratio", 2.0))
unit_spacing = float(settings.get("min_unit_spacing", 1.0))

if fleet_size < 1:
    raise ValueError(f"initial_fleet_size must be >= 1, got {fleet_size}")
if aspect_ratio <= 0.0:
    raise ValueError(f"initial_fleet_aspect_ratio must be > 0, got {aspect_ratio}")
if unit_spacing <= 0.0:
    raise ValueError(f"min_unit_spacing must be > 0, got {unit_spacing}")

grid_columns = max(1, int((fleet_size * aspect_ratio) ** 0.5))
grid_rows = (fleet_size + grid_columns - 1) // grid_columns
while grid_columns / max(1, grid_rows) < aspect_ratio and grid_columns < fleet_size:
    grid_columns += 1
    grid_rows = (fleet_size + grid_columns - 1) // grid_columns

unit_speed = float(settings.get("unit_speed", 1.0))
unit_max_hit_points = float(settings.get("unit_max_hit_points", 100.0))
arena_size = float(settings["arena_size"])
spawn_margin_ratio = DEFAULT_SPAWN_MARGIN_RATIO
spawn_margin = max(1.0, arena_size * spawn_margin_ratio)

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


def clamp(v: float, lo: float, hi: float) -> float:
    if v < lo:
        return lo
    if v > hi:
        return hi
    return v


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
state = initialize_unit_orientations(state)

animate = bool(settings.get("animate", True))
auto_zoom_2d = bool(settings.get("auto_zoom_2d", False))
frame_stride = DEFAULT_FRAME_STRIDE
frame_interval_ms = max(1, 100 * frame_stride)
attack_range = float(settings.get("attack_range", 3.0))
damage_per_tick = float(settings.get("damage_per_tick", 1.0))
fire_quality_alpha = float(settings.get("fire_quality_alpha", 0.1))
contact_hysteresis_h = float(settings.get("contact_hysteresis_h", 0.1))
ch_enabled = bool(settings.get("ch_enabled", True))
random_seed = int(settings.get("random_seed", -1))
background_map_seed = int(settings.get("background_map_seed", -1))


def resolve_effective_seed(seed_value: int) -> int:
    if seed_value < 0:
        return random.SystemRandom().randrange(0, 2**32)
    return seed_value


effective_random_seed = resolve_effective_seed(random_seed)
effective_background_map_seed = resolve_effective_seed(background_map_seed)
_visual_rng = random.Random(effective_random_seed)
background_rng = random.Random(effective_background_map_seed)
print(f"[viz] random_seed_effective={effective_random_seed}")
print(f"[viz] background_map_seed_effective={effective_background_map_seed}")

if animate:
    _, trajectory, alive_trajectory, position_frames = run_dummy_ticks(
        state,
        steps=int(settings["max_time_steps"]),
        capture_positions=True,
        frame_stride=frame_stride,
        attack_range=attack_range,
        damage_per_tick=damage_per_tick,
        separation_radius=unit_spacing,
        fire_quality_alpha=fire_quality_alpha,
        contact_hysteresis_h=contact_hysteresis_h,
        ch_enabled=ch_enabled,
    )
else:
    _, trajectory, alive_trajectory = run_dummy_ticks(
        state,
        steps=int(settings["max_time_steps"]),
        attack_range=attack_range,
        damage_per_tick=damage_per_tick,
        separation_radius=unit_spacing,
        fire_quality_alpha=fire_quality_alpha,
        contact_hysteresis_h=contact_hysteresis_h,
        ch_enabled=ch_enabled,
    )
    position_frames = []

ticks = list(range(len(trajectory["A"])))
fig = plt.figure(figsize=(20, 8))
grid = fig.add_gridspec(2, 2, width_ratios=[3.2, 1.2], height_ratios=[1.0, 1.0])

battle_ax = fig.add_subplot(grid[:, 0])
cohesion_ax = fig.add_subplot(grid[0, 1])
alive_ax = fig.add_subplot(grid[1, 1])

battle_ax.set_title("Battlefield")
battle_ax.set_xlim(0.0, arena_size)
battle_ax.set_ylim(0.0, arena_size)
battle_ax.set_xlabel("X")
battle_ax.set_ylabel("Y")
battle_ax.set_aspect("equal", adjustable="box", anchor="SW")
battle_ax.set_box_aspect(1)
battle_ax.set_facecolor("#F0F0F0")


def draw_space_background(ax, size: float, rng: random.Random):
    # 1) Galaxy haze (center must be inside map).
    haze_center_x = rng.uniform(0.0, size)
    haze_center_y = rng.uniform(0.0, size)
    haze_angle = rng.uniform(-36.0, -18.0)
    ax.add_patch(
        Ellipse(
            (haze_center_x, haze_center_y),
            size * rng.uniform(0.88, 1.02),
            size * rng.uniform(0.24, 0.34),
            angle=haze_angle,
            color="#d7deea",
            alpha=0.13,
            zorder=0.02,
        )
    )
    ax.add_patch(
        Ellipse(
            (haze_center_x, haze_center_y),
            size * rng.uniform(0.70, 0.84),
            size * rng.uniform(0.18, 0.24),
            angle=haze_angle,
            color="#c7d3e5",
            alpha=0.10,
            zorder=0.03,
        )
    )

    # Background star points (white/yellow; avoid dense red noise).
    star_count = rng.randint(140, 220)
    star_x = [rng.uniform(0.0, size) for _ in range(star_count)]
    star_y = [rng.uniform(0.0, size) for _ in range(star_count)]
    star_s = [rng.uniform(1.2, 9.0) for _ in range(star_count)]
    star_c = [rng.choice(("#ffffff", "#ffd84d")) for _ in range(star_count)]
    star_a = [rng.uniform(0.08, 0.28) for _ in range(star_count)]
    ax.scatter(star_x, star_y, s=star_s, c=star_c, alpha=star_a, linewidths=0, zorder=0.05)

    # 2) One major star. Diameter 60~90 -> radius 30~45. Center must be inside map.
    major_star_x = rng.uniform(0.0, size)
    major_star_y = rng.uniform(0.0, size)
    major_star_r = rng.uniform(30.0, 45.0)
    major_star_color = rng.choice(("#fff9dc", "#ffe38a", "#ff9a7a"))
    ax.add_patch(Circle((major_star_x, major_star_y), major_star_r * 1.22, color=major_star_color, alpha=0.10, zorder=0.06))
    ax.add_patch(Circle((major_star_x, major_star_y), major_star_r, color=major_star_color, alpha=0.36, zorder=0.07))

    # 3) Independent asteroids (no glow). Count 0~3, radius 5~10.
    asteroid_count = rng.randint(0, 3)
    for _ in range(asteroid_count):
        ax.add_patch(
            Circle(
                (rng.uniform(0.0, size), rng.uniform(0.0, size)),
                rng.uniform(5.0, 10.0),
                color=rng.choice(("#8f969f", "#9aa1ab", "#8a939c")),
                alpha=0.72,
                zorder=0.10,
            )
        )

    # 4) Asteroid belts as belt-shaped clusters. Count 0~10.
    belt_body_count = rng.randint(0, 10)
    for _ in range(belt_body_count):
        belt_center_x = rng.uniform(0.0, size)
        belt_center_y = rng.uniform(0.0, size)
        belt_angle = rng.uniform(-0.55, 0.55)
        belt_count = rng.randint(10, 30)
        belt_major = rng.uniform(14.0, 26.0)
        belt_minor = rng.uniform(4.0, 9.0)
        for _ in range(belt_count):
            t = rng.uniform(-1.05, 1.05)
            jitter = rng.uniform(-1.5, 1.5)
            px = (belt_major + jitter) * math.cos(t)
            py = (belt_minor + 0.35 * jitter) * math.sin(t)
            rx = (px * math.cos(belt_angle)) - (py * math.sin(belt_angle))
            ry = (px * math.sin(belt_angle)) + (py * math.cos(belt_angle))
            asteroid_r = rng.uniform(0.1, 0.2)
            ax.add_patch(
                Circle(
                    (belt_center_x + rx, belt_center_y + ry),
                    asteroid_r,
                    color="#8e96a3",
                    alpha=0.55,
                    zorder=0.11,
                )
            )


draw_space_background(battle_ax, arena_size, background_rng)
battle_ax.grid(True, which="major", linestyle="-", linewidth=0.4, alpha=0.35)


def choose_tick_step(span: float) -> int:
    if span > 140.0:
        return 20
    if span > 80.0:
        return 10
    if span > 40.0:
        return 5
    return 2


tick_state = {"step": None}


def apply_adaptive_ticks(ax, xlim: tuple[float, float], ylim: tuple[float, float], force: bool = False):
    span = max(xlim[1] - xlim[0], ylim[1] - ylim[0])
    step = choose_tick_step(span)
    if (not force) and tick_state["step"] == step:
        return
    x_start = int(max(0.0, xlim[0]) // step) * step
    x_end = int(min(arena_size, xlim[1])) + step
    y_start = int(max(0.0, ylim[0]) // step) * step
    y_end = int(min(arena_size, ylim[1])) + step
    ax.set_xticks(list(range(x_start, x_end, step)))
    ax.set_yticks(list(range(y_start, y_end, step)))
    tick_state["step"] = step


apply_adaptive_ticks(battle_ax, (0.0, arena_size), (0.0, arena_size), force=True)

QUIVER_GEOMETRY = {
    "head_base": 1.2,
    "head_height": 0.8,
    "shaft_length": 0.4,
    "shaft_width": 0.8,
}


def build_quiver_style(geometry: dict):
    shaft_width = float(geometry["shaft_width"])
    head_base = float(geometry["head_base"])
    head_height = float(geometry["head_height"])
    shaft_length = float(geometry["shaft_length"])
    return {
        "arrow_len": shaft_length + head_height,
        "width": shaft_width,
        "headwidth": head_base / shaft_width,
        "headlength": head_height / shaft_width,
        "headaxislength": head_height / shaft_width,
        "pivot": "tail",
    }


QUIVER_STYLE = build_quiver_style(QUIVER_GEOMETRY)
AUTO_ZOOM_TICK_INTERVAL = 50
AUTO_ZOOM_CENTER_DEADBAND = 0.5
AUTO_ZOOM_MIN_FACTOR = 4.0
AUTO_ZOOM_OFFSCREEN_TRIGGER_RATIO = 0.2
AUTO_ZOOM_TRANSITION_MS = 1000

def interleave_points(points_a, points_b):
    merged = []
    max_len = max(len(points_a), len(points_b))
    for idx in range(max_len):
        if idx < len(points_a):
            x, y, ox, oy = points_a[idx]
            merged.append((x, y, ox, oy, fleet_a_color))
        if idx < len(points_b):
            x, y, ox, oy = points_b[idx]
            merged.append((x, y, ox, oy, fleet_b_color))
    return merged


def build_quiver_data(points_a, points_b):
    merged = interleave_points(points_a, points_b)
    if merged:
        xs = [x for (x, _, _, _, _) in merged]
        ys = [y for (_, y, _, _, _) in merged]
        us = [ox * QUIVER_STYLE["arrow_len"] for (_, _, ox, _, _) in merged]
        vs = [oy * QUIVER_STYLE["arrow_len"] for (_, _, _, oy, _) in merged]
        colors = [c for (_, _, _, _, c) in merged]
    else:
        xs = [float("nan")]
        ys = [float("nan")]
        us = [0.0]
        vs = [0.0]
        colors = [fleet_a_color]
    return xs, ys, us, vs, colors


def make_quiver(points_a, points_b):
    xs, ys, us, vs, colors = build_quiver_data(points_a, points_b)
    return battle_ax.quiver(
        xs,
        ys,
        us,
        vs,
        color=colors,
        angles="xy",
        units="xy",
        scale_units="xy",
        scale=1.0,
        width=QUIVER_STYLE["width"],
        headwidth=QUIVER_STYLE["headwidth"],
        headlength=QUIVER_STYLE["headlength"],
        headaxislength=QUIVER_STYLE["headaxislength"],
        pivot=QUIVER_STYLE["pivot"],
    )


quiver_all = make_quiver([], [])
battle_ax.legend(
    handles=[
        Line2D([], [], marker="o", linestyle="", color=fleet_a_color, label=f"A ({fleet_a_params.archetype_id})"),
        Line2D([], [], marker="o", linestyle="", color=fleet_b_color, label=f"B ({fleet_b_params.archetype_id})"),
    ],
    loc="upper right",
)
count_text = battle_ax.text(
    0.02,
    0.98,
    "",
    transform=battle_ax.transAxes,
    va="top",
    ha="left",
    fontsize=12,
    bbox={"facecolor": "white", "alpha": 0.7, "edgecolor": "none"},
)

if position_frames:
    first_tick = position_frames[0]["tick"]
    auto_zoom_transition_frames = max(1, int(round(AUTO_ZOOM_TRANSITION_MS / frame_interval_ms)))
    auto_zoom_initialized = {"value": False}
    auto_zoom_state = {
        "current_x": arena_size * 0.5,
        "current_y": arena_size * 0.5,
        "current_half": arena_size * 0.5,
        "start_x": arena_size * 0.5,
        "start_y": arena_size * 0.5,
        "start_half": arena_size * 0.5,
        "target_x": arena_size * 0.5,
        "target_y": arena_size * 0.5,
        "target_half": arena_size * 0.5,
        "transition_mode": "none",  # "zoom" or "pan"
        "transition_total_frames": auto_zoom_transition_frames,
        "transition_remaining_frames": 0,
    }
    quiver_point_count = {"value": 1}
    auto_zoom_zoomin_trigger_ratio = 0.8

    def reset_to_full_view():
        auto_zoom_state["current_x"] = arena_size * 0.5
        auto_zoom_state["current_y"] = arena_size * 0.5
        auto_zoom_state["current_half"] = arena_size * 0.5
        auto_zoom_state["start_x"] = arena_size * 0.5
        auto_zoom_state["start_y"] = arena_size * 0.5
        auto_zoom_state["start_half"] = arena_size * 0.5
        auto_zoom_state["target_x"] = arena_size * 0.5
        auto_zoom_state["target_y"] = arena_size * 0.5
        auto_zoom_state["target_half"] = arena_size * 0.5
        auto_zoom_state["transition_mode"] = "none"
        auto_zoom_state["transition_remaining_frames"] = 0
        battle_ax.set_xlim(0.0, arena_size)
        battle_ax.set_ylim(0.0, arena_size)
        apply_adaptive_ticks(battle_ax, (0.0, arena_size), (0.0, arena_size), force=True)

    def compute_auto_zoom_target(points_a, points_b):
        merged = points_a + points_b
        if not merged:
            return None
        xs = [p[0] for p in merged]
        ys = [p[1] for p in merged]
        # Use centroid + most peripheral unit to define the current view.
        center_x = sum(xs) / len(xs)
        center_y = sum(ys) / len(ys)
        farthest_half = 0.0
        for x, y, _, _ in merged:
            dx = abs(x - center_x)
            dy = abs(y - center_y)
            local_half = dx if dx > dy else dy
            if local_half > farthest_half:
                farthest_half = local_half
        # Zoom scale is strictly discrete: 1x, 2x, 4x.
        half_1x = arena_size * 0.5
        half_2x = arena_size * 0.25
        half_4x = arena_size / (2.0 * AUTO_ZOOM_MIN_FACTOR)  # 4x when factor=4
        required_half = clamp(farthest_half + 1.0, half_4x, half_1x)
        if required_half <= half_4x:
            half = half_4x
        elif required_half <= half_2x:
            half = half_2x
        else:
            half = half_1x
        center_x = clamp(center_x, half, arena_size - half)
        center_y = clamp(center_y, half, arena_size - half)
        if abs(center_x - auto_zoom_state["target_x"]) < AUTO_ZOOM_CENTER_DEADBAND:
            center_x = auto_zoom_state["target_x"]
        if abs(center_y - auto_zoom_state["target_y"]) < AUTO_ZOOM_CENTER_DEADBAND:
            center_y = auto_zoom_state["target_y"]
        return (center_x, center_y, half)

    def offscreen_ratio(points_a, points_b):
        merged = points_a + points_b
        if not merged:
            return 0.0
        xlim = battle_ax.get_xlim()
        ylim = battle_ax.get_ylim()
        out_count = 0
        for x, y, _, _ in merged:
            if x < xlim[0] or x > xlim[1] or y < ylim[0] or y > ylim[1]:
                out_count += 1
        return out_count / len(merged)

    def begin_camera_transition(target, mode: str):
        if target is None:
            return
        cx, cy, ch = target
        auto_zoom_state["start_x"] = auto_zoom_state["current_x"]
        auto_zoom_state["start_y"] = auto_zoom_state["current_y"]
        auto_zoom_state["start_half"] = auto_zoom_state["current_half"]
        auto_zoom_state["target_x"] = cx
        auto_zoom_state["target_y"] = cy
        auto_zoom_state["target_half"] = ch if mode == "zoom" else auto_zoom_state["current_half"]
        auto_zoom_state["transition_mode"] = mode
        auto_zoom_state["transition_total_frames"] = auto_zoom_transition_frames
        auto_zoom_state["transition_remaining_frames"] = auto_zoom_transition_frames
        target_half_for_ticks = auto_zoom_state["target_half"]
        target_xlim = (cx - target_half_for_ticks, cx + target_half_for_ticks)
        target_ylim = (cy - target_half_for_ticks, cy + target_half_for_ticks)
        apply_adaptive_ticks(battle_ax, target_xlim, target_ylim)

    def apply_auto_zoom_step():
        remaining = auto_zoom_state["transition_remaining_frames"]
        tx = auto_zoom_state["target_x"]
        ty = auto_zoom_state["target_y"]
        th = auto_zoom_state["target_half"]
        if remaining > 0:
            total = auto_zoom_state["transition_total_frames"]
            elapsed = total - remaining + 1
            t = elapsed / total
            if t > 1.0:
                t = 1.0
            # Smoothstep interpolation for center motion over fixed duration.
            e = t * t * (3.0 - (2.0 * t))
            sx = auto_zoom_state["start_x"]
            sy = auto_zoom_state["start_y"]
            sh = auto_zoom_state["start_half"]
            cx = sx + ((tx - sx) * e)
            cy = sy + ((ty - sy) * e)
            if auto_zoom_state["transition_mode"] == "zoom":
                ch = sh + ((th - sh) * e)
            else:
                ch = sh
            auto_zoom_state["transition_remaining_frames"] = remaining - 1
        elif auto_zoom_state["current_x"] != tx or auto_zoom_state["current_y"] != ty:
            cx = tx
            cy = ty
            ch = th
        else:
            # No trigger and no active transition: keep camera fully still.
            cx = auto_zoom_state["current_x"]
            cy = auto_zoom_state["current_y"]
            ch = auto_zoom_state["current_half"]
        auto_zoom_state["current_x"] = cx
        auto_zoom_state["current_y"] = cy
        auto_zoom_state["current_half"] = ch
        target_xlim = (cx - ch, cx + ch)
        target_ylim = (cy - ch, cy + ch)
        curr_xlim = battle_ax.get_xlim()
        curr_ylim = battle_ax.get_ylim()
        lim_eps = 1e-9
        if (
            abs(curr_xlim[0] - target_xlim[0]) > lim_eps
            or abs(curr_xlim[1] - target_xlim[1]) > lim_eps
            or abs(curr_ylim[0] - target_ylim[0]) > lim_eps
            or abs(curr_ylim[1] - target_ylim[1]) > lim_eps
        ):
            battle_ax.set_xlim(*target_xlim)
            battle_ax.set_ylim(*target_ylim)

    def update_quiver(points_a, points_b):
        global quiver_all
        xs, ys, us, vs, colors = build_quiver_data(points_a, points_b)
        next_count = len(xs)
        if next_count != quiver_point_count["value"]:
            quiver_all.remove()
            quiver_all = make_quiver(points_a, points_b)
            quiver_point_count["value"] = next_count
            return
        offsets = list(zip(xs, ys))
        quiver_all.set_offsets(offsets)
        quiver_all.set_UVC(us, vs)
        quiver_all.set_color(colors)

    def update_frame(frame):
        points_a = frame.get("A", [])
        points_b = frame.get("B", [])
        update_quiver(points_a, points_b)
        if auto_zoom_2d:
            if frame["tick"] == first_tick:
                reset_to_full_view()
                auto_zoom_initialized["value"] = False
            if frame["tick"] % AUTO_ZOOM_TICK_INTERVAL == 0:
                ratio = offscreen_ratio(points_a, points_b)
                target = compute_auto_zoom_target(points_a, points_b)
                if target is not None:
                    _, _, target_half = target
                    current_half = auto_zoom_state["current_half"]
                    zoom_trigger = (
                        (not auto_zoom_initialized["value"])
                        or (target_half < (current_half * auto_zoom_zoomin_trigger_ratio))
                    )
                    pan_trigger = ratio > AUTO_ZOOM_OFFSCREEN_TRIGGER_RATIO
                    if zoom_trigger:
                        begin_camera_transition(target, mode="zoom")
                        auto_zoom_initialized["value"] = True
                    elif pan_trigger:
                        begin_camera_transition(target, mode="pan")
            apply_auto_zoom_step()
        battle_ax.set_title(f"Battlefield (tick={frame['tick']})")
        count_text.set_text(
            f"A ({fleet_a_params.archetype_id}): {len(points_a)}\n"
            f"B ({fleet_b_params.archetype_id}): {len(points_b)}"
        )
        return quiver_all, count_text

    anim = FuncAnimation(fig, update_frame, frames=position_frames, interval=frame_interval_ms, blit=False, repeat=True)
else:
    final_a = [
        (
            state.units[uid].position.x,
            state.units[uid].position.y,
            state.units[uid].orientation_vector.x,
            state.units[uid].orientation_vector.y,
        )
        for uid in fleets["A"].unit_ids
        if uid in state.units
    ]
    final_b = [
        (
            state.units[uid].position.x,
            state.units[uid].position.y,
            state.units[uid].orientation_vector.x,
            state.units[uid].orientation_vector.y,
        )
        for uid in fleets["B"].unit_ids
        if uid in state.units
    ]
    quiver_all.remove()
    quiver_all = make_quiver(final_a, final_b)
    count_text.set_text(
        f"A ({fleet_a_params.archetype_id}): {len(final_a)}\n"
        f"B ({fleet_b_params.archetype_id}): {len(final_b)}"
    )
    anim = None

cohesion_ax.plot(ticks, trajectory["A"], label=f"A ({fleet_a_params.archetype_id})", color=fleet_a_color)
cohesion_ax.plot(ticks, trajectory["B"], label=f"B ({fleet_b_params.archetype_id})", color=fleet_b_color)
cohesion_ax.set_xlabel("Tick")
cohesion_ax.set_ylabel("Cohesion")
cohesion_ax.legend()

alive_ax.plot(ticks, alive_trajectory["A"], label=f"A ({fleet_a_params.archetype_id})", color=fleet_a_color)
alive_ax.plot(ticks, alive_trajectory["B"], label=f"B ({fleet_b_params.archetype_id})", color=fleet_b_color)
alive_ax.set_xlabel("Tick")
alive_ax.set_ylabel("Alive Units")
alive_ax.legend()

plt.tight_layout()
plt.show()
