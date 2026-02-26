import json
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.lines import Line2D

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
arena_size = float(settings["arena_size"])
spawn_margin_ratio = float(settings.get("spawn_margin_ratio", 0.05))
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
        max_speed=unit_speed,
    )
    fleet_b_unit_ids.append(unit_b_id)

fleets = {
    "A": FleetState(fleet_id="A", parameters=fleet_a_params, unit_ids=tuple(fleet_a_unit_ids)),
    "B": FleetState(fleet_id="B", parameters=fleet_b_params, unit_ids=tuple(fleet_b_unit_ids)),
}

state = BattleState(
    tick=0,
    dt=float(settings["dt"]),
    arena_size=arena_size,
    units=units,
    fleets=fleets,
    last_fleet_cohesion=build_initial_cohesion_map(fleets.keys()),
)
state = initialize_unit_orientations(state)

animate = bool(settings.get("animate", True))
frame_stride = int(settings.get("frame_stride", 10))
frame_interval_ms = max(1, 100 * frame_stride)
attack_range = float(settings.get("attack_range", 3.0))
export_2d_video = bool(settings.get("export_2d_video", False))

if animate:
    _, trajectory, alive_trajectory, position_frames = run_dummy_ticks(
        state,
        steps=int(settings["max_time_steps"]),
        capture_positions=True,
        frame_stride=frame_stride,
        attack_range=attack_range,
        separation_radius=unit_spacing,
    )
else:
    _, trajectory, alive_trajectory = run_dummy_ticks(
        state,
        steps=int(settings["max_time_steps"]),
        attack_range=attack_range,
        separation_radius=unit_spacing,
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


def make_quiver(points_a, points_b):
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
    def update_frame(frame):
        global quiver_all
        points_a = frame.get("A", [])
        points_b = frame.get("B", [])
        quiver_all.remove()
        quiver_all = make_quiver(points_a, points_b)
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
if export_2d_video and anim is not None:
    mp4_path = base_dir / "test_run_v1_0_battlefield.mp4"
    try:
        anim.save(str(mp4_path), writer="ffmpeg", fps=1000.0 / frame_interval_ms)
        print(f"2D animation exported: {mp4_path}")
    except Exception:
        gif_path = base_dir / "test_run_v1_0_battlefield.gif"
        anim.save(str(gif_path), writer="pillow", fps=1000.0 / frame_interval_ms)
        print(f"2D animation exported (GIF fallback): {gif_path}")
plt.show()
