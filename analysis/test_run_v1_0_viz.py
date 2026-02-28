import math
import random
import textwrap
from typing import Any, Mapping, Sequence

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.lines import Line2D
from matplotlib.patches import Circle, Ellipse, Rectangle

from runtime_v0_1 import BattleState


plt.rcParams["font.sans-serif"] = [
    "Microsoft YaHei",
    "SimHei",
    "Noto Sans CJK SC",
    "Arial Unicode MS",
    "DejaVu Sans",
]
plt.rcParams["axes.unicode_minus"] = False


def _cfg(d: Mapping[str, Any], key: str, default: Any) -> Any:
    value = d.get(key, default)
    if value is None:
        return default
    return value


def render_test_run(
    arena_size: float,
    trajectory: Mapping[str, Sequence[float]],
    alive_trajectory: Mapping[str, Sequence[int]],
    fleet_size_trajectory: Mapping[str, Sequence[float]],
    initial_fleet_sizes: Mapping[str, float],
    position_frames: list[dict],
    final_state: BattleState,
    fleet_a_label: str,
    fleet_b_label: str,
    fleet_a_color: str,
    fleet_b_color: str,
    auto_zoom_2d: bool,
    frame_interval_ms: int,
    background_seed: int,
    viz_settings: Mapping[str, Any],
) -> None:
    fig_size = _cfg(viz_settings, "figure_size", [20, 8])
    width_ratios = _cfg(viz_settings, "layout_width_ratios", [100.0, 35.0, 35.0])
    height_ratios = _cfg(viz_settings, "layout_height_ratios", [1.0, 1.0, 0.2])
    if isinstance(width_ratios, Sequence) and len(width_ratios) >= 3:
        battle_col_ratio = float(width_ratios[0])
        debug_col_ratio = float(width_ratios[1])
        plot_col_ratio = float(width_ratios[2])
    else:
        battle_col_ratio = 100.0
        debug_col_ratio = 35.0
        plot_col_ratio = 35.0
    if battle_col_ratio <= 0.0:
        battle_col_ratio = 100.0
    if debug_col_ratio <= 0.0:
        debug_col_ratio = 35.0
    if plot_col_ratio <= 0.0:
        plot_col_ratio = 35.0
    if isinstance(height_ratios, Sequence) and len(height_ratios) >= 3:
        plot_top_height_ratio = float(height_ratios[0])
        plot_bottom_height_ratio = float(height_ratios[1])
        plot_spacer_height_ratio = float(height_ratios[2])
    else:
        plot_top_height_ratio = 1.0
        plot_bottom_height_ratio = 1.0
        plot_spacer_height_ratio = 0.2
    if plot_top_height_ratio <= 0.0:
        plot_top_height_ratio = 1.0
    if plot_bottom_height_ratio <= 0.0:
        plot_bottom_height_ratio = 1.0
    if plot_spacer_height_ratio <= 0.0:
        plot_spacer_height_ratio = 0.001
    battlefield_bg_color = str(_cfg(viz_settings, "battlefield_bg_color", "#F0F0F0"))
    grid_line_style = str(_cfg(viz_settings, "grid_line_style", "-"))
    grid_line_width = float(_cfg(viz_settings, "grid_line_width", 0.4))
    grid_alpha = float(_cfg(viz_settings, "grid_alpha", 0.35))
    tick_step_thresholds = _cfg(viz_settings, "tick_step_thresholds", {})
    quiver_geometry = _cfg(viz_settings, "quiver_geometry", {})
    death_linger_cfg = _cfg(viz_settings, "death_linger", {})
    auto_zoom_cfg = _cfg(viz_settings, "auto_zoom", {})
    haze_cfg = _cfg(viz_settings, "background_haze", {})
    major_star_cfg = _cfg(viz_settings, "background_major_star", {})
    asteroids_cfg = _cfg(viz_settings, "background_asteroids", {})
    belts_cfg = _cfg(viz_settings, "background_belts", {})

    ticks = list(range(len(trajectory["A"])))
    fig = plt.figure(figsize=(float(fig_size[0]), float(fig_size[1])))
    outer_grid = fig.add_gridspec(
        1,
        3,
        width_ratios=[battle_col_ratio, debug_col_ratio, plot_col_ratio],
        wspace=0.20,
    )
    right_grid = outer_grid[0, 2].subgridspec(
        3,
        1,
        height_ratios=[plot_top_height_ratio, plot_bottom_height_ratio, plot_spacer_height_ratio],
        hspace=0.26,
    )

    battle_ax = fig.add_subplot(outer_grid[0, 0])
    debug_ax = fig.add_subplot(outer_grid[0, 1])
    cohesion_ax = fig.add_subplot(right_grid[0, 0])
    alive_ax = fig.add_subplot(right_grid[1, 0])

    battle_ax.set_title("Battlefield")
    battle_ax.set_xlim(0.0, arena_size)
    battle_ax.set_ylim(0.0, arena_size)
    battle_ax.set_xlabel("X")
    battle_ax.set_ylabel("Y")
    battle_ax.set_aspect("equal", adjustable="box", anchor="E")
    battle_ax.set_box_aspect(1)
    battle_ax.set_facecolor(battlefield_bg_color)

    debug_ax.set_title("DEBUG", loc="left")
    debug_ax.set_xlim(0.0, 1.0)
    debug_ax.set_ylim(0.0, 1.0)
    debug_ax.set_xticks([])
    debug_ax.set_yticks([])
    debug_ax.set_facecolor("#ffffff")
    for spine in debug_ax.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(1.2)
        spine.set_edgecolor("#444444")

    def draw_space_background(ax, size: float, rng: random.Random):
        # 1) Galaxy haze fixed at battlefield center, fixed size, fixed 135deg.
        haze_center_ratio = _cfg(haze_cfg, "center_ratio", [0.5, 0.5])
        haze_center_x = size * float(haze_center_ratio[0])
        haze_center_y = size * float(haze_center_ratio[1])
        haze_angle = float(_cfg(haze_cfg, "angle_deg", 135.0))
        # New haze sizing model:
        # - inner_size_ratio controls inner major-axis scale
        # - outer_inner_ratio controls outer/inner size ratio
        # - axis_ratio controls minor/major shape ratio
        # Legacy fallback from size_ratio remains for compatibility.
        haze_inner_size_ratio = float(_cfg(haze_cfg, "inner_size_ratio", 0.735))
        haze_outer_inner_ratio = float(_cfg(haze_cfg, "outer_inner_ratio", 1.3333333333))
        haze_axis_ratio = float(_cfg(haze_cfg, "axis_ratio", 0.3061224489))
        legacy_size_ratio = _cfg(haze_cfg, "size_ratio", None)
        if isinstance(legacy_size_ratio, list) and len(legacy_size_ratio) >= 2:
            legacy_outer_major = float(legacy_size_ratio[0])
            legacy_outer_minor = float(legacy_size_ratio[1])
            if legacy_outer_major > 0.0:
                if "inner_size_ratio" not in haze_cfg:
                    haze_inner_size_ratio = legacy_outer_major * 0.75
                if "outer_inner_ratio" not in haze_cfg:
                    haze_outer_inner_ratio = 1.0 / 0.75
                if "axis_ratio" not in haze_cfg:
                    haze_axis_ratio = legacy_outer_minor / legacy_outer_major
        if haze_inner_size_ratio <= 0.0:
            haze_inner_size_ratio = 0.735
        if haze_outer_inner_ratio <= 0.0:
            haze_outer_inner_ratio = 1.3333333333
        if haze_axis_ratio <= 0.0:
            haze_axis_ratio = 0.3061224489
        inner_major = size * haze_inner_size_ratio
        inner_minor = inner_major * haze_axis_ratio
        outer_major = inner_major * haze_outer_inner_ratio
        outer_minor = inner_minor * haze_outer_inner_ratio
        haze_outer_color = str(_cfg(haze_cfg, "outer_color", "#d7deea"))
        haze_inner_color = str(_cfg(haze_cfg, "inner_color", "#c7d3e5"))
        haze_outer_alpha = float(_cfg(haze_cfg, "outer_alpha", 0.13))
        haze_inner_alpha = float(_cfg(haze_cfg, "inner_alpha", 0.10))
        ax.add_patch(
            Ellipse(
                (haze_center_x, haze_center_y),
                outer_major,
                outer_minor,
                angle=haze_angle,
                color=haze_outer_color,
                alpha=haze_outer_alpha,
                zorder=0.02,
            )
        )
        ax.add_patch(
            Ellipse(
                (haze_center_x, haze_center_y),
                inner_major,
                inner_minor,
                angle=haze_angle,
                color=haze_inner_color,
                alpha=haze_inner_alpha,
                zorder=0.03,
            )
        )
        # 2) One major star. Diameter 60~90 -> radius 30~45. Center must be inside map.
        major_star_radius_range = _cfg(major_star_cfg, "radius_range", [30.0, 45.0])
        major_star_colors = _cfg(major_star_cfg, "colors", ["#fff9dc", "#ffe38a", "#ff9a7a"])
        major_star_glow_scale = float(_cfg(major_star_cfg, "glow_scale", 1.22))
        major_star_glow_alpha = float(_cfg(major_star_cfg, "glow_alpha", 0.10))
        major_star_core_alpha = float(_cfg(major_star_cfg, "core_alpha", 0.36))
        major_star_x = rng.uniform(0.0, size)
        major_star_y = rng.uniform(0.0, size)
        major_star_r = rng.uniform(float(major_star_radius_range[0]), float(major_star_radius_range[1]))
        major_star_color = str(rng.choice(major_star_colors))
        ax.add_patch(
            Circle(
                (major_star_x, major_star_y),
                major_star_r * major_star_glow_scale,
                color=major_star_color,
                alpha=major_star_glow_alpha,
                zorder=0.06,
            )
        )
        ax.add_patch(
            Circle(
                (major_star_x, major_star_y),
                major_star_r,
                color=major_star_color,
                alpha=major_star_core_alpha,
                zorder=0.07,
            )
        )

        # 3) Independent asteroids (no glow). Count 0~3, radius 5~10.
        asteroid_count_range = _cfg(asteroids_cfg, "count_range", [0, 3])
        asteroid_radius_range = _cfg(asteroids_cfg, "radius_range", [5.0, 10.0])
        asteroid_colors = _cfg(asteroids_cfg, "colors", ["#8f969f", "#9aa1ab", "#8a939c"])
        asteroid_alpha = float(_cfg(asteroids_cfg, "alpha", 0.72))
        gas_giant_ring_cfg = _cfg(asteroids_cfg, "gas_giant_ring", {})
        ring_enabled = bool(_cfg(gas_giant_ring_cfg, "enabled", True))
        trigger_percentile = float(_cfg(gas_giant_ring_cfg, "trigger_percentile", 0.75))
        if trigger_percentile < 0.0:
            trigger_percentile = 0.0
        elif trigger_percentile > 1.0:
            trigger_percentile = 1.0
        ring_diameter_scale_range = _cfg(gas_giant_ring_cfg, "diameter_scale_range", [2.1, 3.4])
        ring_axis_ratio_range = _cfg(gas_giant_ring_cfg, "axis_ratio_range", [0.2, 0.55])
        ring_angle_deg_range = _cfg(gas_giant_ring_cfg, "angle_deg_range", [0.0, 180.0])
        # Use a single filled ellipse instead of a geometric line ring.
        ring_color = str(_cfg(gas_giant_ring_cfg, "color", "#c6ccd6"))
        ring_alpha = float(_cfg(gas_giant_ring_cfg, "alpha", 0.65))
        asteroid_r_min = float(asteroid_radius_range[0])
        asteroid_r_max = float(asteroid_radius_range[1])
        ring_trigger_radius = asteroid_r_min + (trigger_percentile * (asteroid_r_max - asteroid_r_min))
        asteroid_count = rng.randint(int(asteroid_count_range[0]), int(asteroid_count_range[1]))
        for _ in range(asteroid_count):
            asteroid_x = rng.uniform(0.0, size)
            asteroid_y = rng.uniform(0.0, size)
            asteroid_r = rng.uniform(asteroid_r_min, asteroid_r_max)
            if ring_enabled and asteroid_r >= ring_trigger_radius:
                ring_major_diameter = (2.0 * asteroid_r) * rng.uniform(
                    float(ring_diameter_scale_range[0]),
                    float(ring_diameter_scale_range[1]),
                )
                ring_minor_diameter = ring_major_diameter * rng.uniform(
                    float(ring_axis_ratio_range[0]),
                    float(ring_axis_ratio_range[1]),
                )
                ring_angle = rng.uniform(
                    float(ring_angle_deg_range[0]),
                    float(ring_angle_deg_range[1]),
                )
                ax.add_patch(
                    Ellipse(
                        (asteroid_x, asteroid_y),
                        ring_major_diameter,
                        ring_minor_diameter,
                        angle=ring_angle,
                        color=ring_color,
                        alpha=ring_alpha,
                        zorder=0.093,
                    )
                )
            ax.add_patch(
                Circle(
                    (asteroid_x, asteroid_y),
                    asteroid_r,
                    color=str(rng.choice(asteroid_colors)),
                    alpha=asteroid_alpha,
                    zorder=0.10,
                )
            )

        # 4) Asteroid belts as low-curvature belt-shaped clusters. Count 0~10.
        belt_cluster_count_range = _cfg(belts_cfg, "cluster_count_range", [0, 10])
        belt_points_per_cluster_range = _cfg(belts_cfg, "points_per_cluster_range", [10, 30])
        belt_major_range = _cfg(belts_cfg, "major_range", [16.0, 30.0])
        belt_minor_range = _cfg(belts_cfg, "minor_range", [0.6, 1.8])
        belt_curvature_range = _cfg(belts_cfg, "curvature_range", [-0.08, 0.08])
        belt_angle_range = _cfg(belts_cfg, "angle_range", [-0.55, 0.55])
        belt_asteroid_radius_range = _cfg(belts_cfg, "asteroid_radius_range", [0.1, 0.2])
        belt_color = str(_cfg(belts_cfg, "color", "#8e96a3"))
        belt_alpha = float(_cfg(belts_cfg, "alpha", 0.55))
        belt_body_count = rng.randint(int(belt_cluster_count_range[0]), int(belt_cluster_count_range[1]))
        for _ in range(belt_body_count):
            belt_center_x = rng.uniform(0.0, size)
            belt_center_y = rng.uniform(0.0, size)
            belt_angle = rng.uniform(float(belt_angle_range[0]), float(belt_angle_range[1]))
            belt_count = rng.randint(int(belt_points_per_cluster_range[0]), int(belt_points_per_cluster_range[1]))
            belt_major = rng.uniform(float(belt_major_range[0]), float(belt_major_range[1]))
            belt_minor = rng.uniform(float(belt_minor_range[0]), float(belt_minor_range[1]))
            belt_curvature = rng.uniform(float(belt_curvature_range[0]), float(belt_curvature_range[1]))
            for _ in range(belt_count):
                u = rng.uniform(-belt_major, belt_major)
                v = rng.uniform(-belt_minor, belt_minor)
                curve = belt_curvature * ((u * u) / max(belt_major, 1e-9) - (0.25 * belt_major))
                px = u
                py = v + curve
                rx = (px * math.cos(belt_angle)) - (py * math.sin(belt_angle))
                ry = (px * math.sin(belt_angle)) + (py * math.cos(belt_angle))
                asteroid_r = rng.uniform(
                    float(belt_asteroid_radius_range[0]),
                    float(belt_asteroid_radius_range[1]),
                )
                ax.add_patch(
                    Circle(
                        (belt_center_x + rx, belt_center_y + ry),
                        asteroid_r,
                        color=belt_color,
                        alpha=belt_alpha,
                        zorder=0.11,
                    )
                )

    draw_space_background(battle_ax, arena_size, random.Random(background_seed))
    grid_clip_patch = Rectangle(
        (0.0, 0.0),
        arena_size,
        arena_size,
        fill=False,
        edgecolor="none",
        linewidth=0.0,
        zorder=0.0,
    )
    battle_ax.add_patch(grid_clip_patch)
    battle_ax.grid(
        True,
        which="major",
        linestyle=grid_line_style,
        linewidth=grid_line_width,
        alpha=grid_alpha,
    )

    def apply_grid_clip():
        for grid_line in battle_ax.get_xgridlines():
            grid_line.set_clip_path(grid_clip_patch)
        for grid_line in battle_ax.get_ygridlines():
            grid_line.set_clip_path(grid_clip_patch)

    apply_grid_clip()
    boundary_line_width = 3.0
    battle_ax.add_patch(
        Rectangle(
            (0.0, 0.0),
            arena_size,
            arena_size,
            fill=False,
            edgecolor="#000000",
            linewidth=boundary_line_width,
            zorder=0.01,
        )
    )

    def choose_tick_step(span: float) -> int:
        if span > 140.0:
            return int(_cfg(tick_step_thresholds, "gt_140", 20))
        if span > 80.0:
            return int(_cfg(tick_step_thresholds, "gt_80", 10))
        if span > 40.0:
            return int(_cfg(tick_step_thresholds, "gt_40", 5))
        return int(_cfg(tick_step_thresholds, "else", 2))

    tick_state = {"step": None, "x_start": None, "y_start": None}

    def apply_adaptive_ticks(ax, xlim: tuple[float, float], ylim: tuple[float, float], force: bool = False):
        span = max(xlim[1] - xlim[0], ylim[1] - ylim[0])
        step = choose_tick_step(span)
        x_start = int(max(0.0, xlim[0]) // step) * step
        x_end = int(min(arena_size, xlim[1])) + step
        y_start = int(max(0.0, ylim[0]) // step) * step
        y_end = int(min(arena_size, ylim[1])) + step
        if (
            (not force)
            and tick_state["step"] == step
            and tick_state["x_start"] == x_start
            and tick_state["y_start"] == y_start
        ):
            apply_grid_clip()
            return
        ax.set_xticks(list(range(x_start, x_end, step)))
        ax.set_yticks(list(range(y_start, y_end, step)))
        tick_state["step"] = step
        tick_state["x_start"] = x_start
        tick_state["y_start"] = y_start
        apply_grid_clip()

    apply_adaptive_ticks(battle_ax, (0.0, arena_size), (0.0, arena_size), force=True)

    def build_quiver_style(geometry: dict):
        shaft_width = float(_cfg(geometry, "shaft_width", 0.8))
        head_base = float(_cfg(geometry, "head_base", 1.2))
        head_height = float(_cfg(geometry, "head_height", 0.8))
        shaft_length = float(_cfg(geometry, "shaft_length", 0.4))
        return {
            "arrow_len": shaft_length + head_height,
            "width": shaft_width,
            "headwidth": head_base / shaft_width,
            "headlength": head_height / shaft_width,
            "headaxislength": head_height / shaft_width,
            "pivot": "tail",
        }

    quiver_style = build_quiver_style(quiver_geometry)
    vector_display_mode = str(_cfg(viz_settings, "vector_display_mode", "effective")).strip().lower()
    if vector_display_mode not in {"effective", "free", "radial_debug"}:
        vector_display_mode = "effective"
    radial_debug_neutral_band = 0.05
    radial_debug_len_ratio = 0.75
    radial_debug_inward_color = "#2ca02c"
    radial_debug_outward_color = "#d62728"
    radial_debug_neutral_color = "#ffbf00"
    auto_zoom_tick_interval = int(_cfg(auto_zoom_cfg, "tick_interval", 50))
    auto_zoom_center_deadband = float(_cfg(auto_zoom_cfg, "center_deadband", 0.5))
    auto_zoom_min_factor = float(_cfg(auto_zoom_cfg, "min_factor", 4.0))
    auto_zoom_offscreen_trigger_ratio = float(_cfg(auto_zoom_cfg, "offscreen_trigger_ratio", 0.2))
    auto_zoom_centroid_trigger_ratio = float(_cfg(auto_zoom_cfg, "centroid_trigger_ratio", 0.3))
    auto_zoom_follow_out_of_bounds = bool(_cfg(auto_zoom_cfg, "follow_out_of_bounds", True))
    auto_zoom_transition_ms = int(_cfg(auto_zoom_cfg, "transition_ms", 1000))
    auto_zoom_zoomin_trigger_ratio = float(_cfg(auto_zoom_cfg, "zoomin_trigger_ratio", 0.8))
    if auto_zoom_centroid_trigger_ratio < 0.0:
        auto_zoom_centroid_trigger_ratio = 0.0
    death_linger_ticks = int(_cfg(death_linger_cfg, "ticks", 3))
    death_ring_radius = float(_cfg(death_linger_cfg, "ring_radius", 1.0))
    death_ring_color = str(_cfg(death_linger_cfg, "ring_color", "#ff0000"))
    death_ring_linewidth = 1.2
    death_ring_alpha = 0.9

    def normalize_frame_points(raw_points, fleet_prefix: str):
        normalized = []
        for idx, point in enumerate(raw_points):
            if len(point) >= 7:
                unit_id, x, y, ox, oy, vx, vy = point[:7]
            elif len(point) == 6:
                unit_id, x, y, ox, oy, vx = point
                vy = 0.0
            elif len(point) == 5:
                unit_id, x, y, ox, oy = point
                vx = ox
                vy = oy
            else:
                x, y, ox, oy = point
                unit_id = f"{fleet_prefix}_{idx}"
                vx = ox
                vy = oy
            normalized.append((str(unit_id), float(x), float(y), float(ox), float(oy), float(vx), float(vy)))
        return normalized

    def interleave_points(points_a, points_b):
        merged = []
        max_len = max(len(points_a), len(points_b))
        for idx in range(max_len):
            if idx < len(points_a):
                point_a = points_a[idx]
                x, y, ux, uy = point_a[:4]
                color = point_a[4] if len(point_a) >= 5 else fleet_a_color
                merged.append((x, y, ux, uy, color))
            if idx < len(points_b):
                point_b = points_b[idx]
                x, y, ux, uy = point_b[:4]
                color = point_b[4] if len(point_b) >= 5 else fleet_b_color
                merged.append((x, y, ux, uy, color))
        return merged

    def build_quiver_data(points_a, points_b):
        merged = interleave_points(points_a, points_b)
        if merged:
            xs = [x for (x, _, _, _, _) in merged]
            ys = [y for (_, y, _, _, _) in merged]
            us = [ux * quiver_style["arrow_len"] for (_, _, ux, _, _) in merged]
            vs = [uy * quiver_style["arrow_len"] for (_, _, _, uy, _) in merged]
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
            width=quiver_style["width"],
            headwidth=quiver_style["headwidth"],
            headlength=quiver_style["headlength"],
            headaxislength=quiver_style["headaxislength"],
            pivot=quiver_style["pivot"],
            zorder=10.0,
        )

    quiver_all = make_quiver([], [])
    battle_legend = battle_ax.legend(
        handles=[
            Line2D([], [], marker="o", linestyle="", color=fleet_a_color, label=f"A [{fleet_a_label}]"),
            Line2D([], [], marker="o", linestyle="", color=fleet_b_color, label=f"B [{fleet_b_label}]"),
        ],
        loc="upper right",
        fontsize=9,
    )
    battle_legend.set_zorder(30.0)
    legend_fontsize = 9
    if battle_legend.get_texts():
        legend_fontsize = battle_legend.get_texts()[0].get_fontsize()

    initial_size_a = float(initial_fleet_sizes.get("A", 0.0))
    initial_size_b = float(initial_fleet_sizes.get("B", 0.0))

    def to_size_int(value: float) -> int:
        return max(0, int(math.ceil(value)))

    initial_size_a_int = to_size_int(initial_size_a)
    initial_size_b_int = to_size_int(initial_size_b)
    max_alive_value = 0
    if alive_trajectory.get("A"):
        max_alive_value = max(max_alive_value, max(int(v) for v in alive_trajectory["A"]))
    if alive_trajectory.get("B"):
        max_alive_value = max(max_alive_value, max(int(v) for v in alive_trajectory["B"]))
    alive_count_width = max(2, len(str(max_alive_value)))
    max_fleet_size_value = max(initial_size_a_int, initial_size_b_int)
    if fleet_size_trajectory.get("A"):
        max_fleet_size_value = max(
            max_fleet_size_value,
            max(to_size_int(float(v)) for v in fleet_size_trajectory["A"]),
        )
    if fleet_size_trajectory.get("B"):
        max_fleet_size_value = max(
            max_fleet_size_value,
            max(to_size_int(float(v)) for v in fleet_size_trajectory["B"]),
        )
    fleet_size_width = max(2, len(str(max_fleet_size_value)))

    def format_count_text(
        alive_a: int,
        alive_b: int,
        curr_size_a: float,
        curr_size_b: float,
        pct_a: float,
        pct_b: float,
    ) -> str:
        curr_size_a_int = to_size_int(curr_size_a)
        curr_size_b_int = to_size_int(curr_size_b)
        return (
            f"A - [Alive: {alive_a:>{alive_count_width}d} | Fleet Size: {curr_size_a_int:>{fleet_size_width}d} / {initial_size_a_int:>{fleet_size_width}d} ({pct_a:>5.1f}%)]\n"
            f"B - [Alive: {alive_b:>{alive_count_width}d} | Fleet Size: {curr_size_b_int:>{fleet_size_width}d} / {initial_size_b_int:>{fleet_size_width}d} ({pct_b:>5.1f}%)]"
        )

    def format_debug_text(mode: str, outliers: int) -> str:
        raw_lines = [
            f"vector_display_mode: {mode}",
            f"outliers: {outliers}",
        ]
        wrapped_lines = []
        for raw in raw_lines:
            lines = textwrap.wrap(
                raw,
                width=26,
                break_long_words=False,
                break_on_hyphens=False,
            )
            if lines:
                wrapped_lines.extend(lines)
            else:
                wrapped_lines.append("")
        return "\n".join(wrapped_lines)

    count_text = battle_ax.text(
        0.02,
        0.98,
        "",
        transform=battle_ax.transAxes,
        va="top",
        ha="left",
        fontsize=legend_fontsize,
        fontfamily="monospace",
        bbox={"facecolor": "white", "alpha": 0.7, "edgecolor": "none"},
    )
    count_text.set_zorder(30.0)
    debug_text = debug_ax.text(
        0.04,
        0.95,
        "",
        transform=debug_ax.transAxes,
        va="top",
        ha="left",
        fontsize=max(8, int(round(legend_fontsize)) - 1),
        family="monospace",
    )
    debug_text.set_text(format_debug_text(vector_display_mode, 0))

    if position_frames:
        first_tick = position_frames[0]["tick"]
        auto_zoom_transition_frames = max(1, int(round(auto_zoom_transition_ms / frame_interval_ms)))
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
        death_linger = {"A": {}, "B": {}}
        last_alive_by_fleet = {"A": {}, "B": {}}
        last_positions_for_effective = {"A": {}, "B": {}}
        death_ring_patches = []

        def fleet_centroid_norm(points_norm):
            if not points_norm:
                return None
            sum_x = 0.0
            sum_y = 0.0
            for _, x, y, _, _, _, _ in points_norm:
                sum_x += x
                sum_y += y
            count = float(len(points_norm))
            return (sum_x / count, sum_y / count)

        def build_render_points_for_mode(points_norm, fleet_id: str, commit_positions: bool = True):
            if fleet_id == "A":
                base_color = fleet_a_color
            else:
                base_color = fleet_b_color
            prev_positions = last_positions_for_effective[fleet_id]
            centroid = fleet_centroid_norm(points_norm)
            next_positions = {}
            render_points = []
            radial_outward_count = 0
            radial_eps = 1e-12
            vector_eps = 1e-12
            for unit_id, x, y, ox, oy, vx, vy in points_norm:
                next_positions[unit_id] = (x, y)
                if vector_display_mode == "effective":
                    prev = prev_positions.get(unit_id)
                    if prev is None:
                        raw_x = ox
                        raw_y = oy
                    else:
                        raw_x = x - prev[0]
                        raw_y = y - prev[1]
                    raw_norm = math.sqrt((raw_x * raw_x) + (raw_y * raw_y))
                    if raw_norm > vector_eps:
                        ux = raw_x / raw_norm
                        uy = raw_y / raw_norm
                    else:
                        ux = 0.0
                        uy = 0.0
                    color = base_color
                elif vector_display_mode == "free":
                    raw_norm = math.sqrt((vx * vx) + (vy * vy))
                    if raw_norm > vector_eps:
                        ux = vx / raw_norm
                        uy = vy / raw_norm
                    else:
                        ux = 0.0
                        uy = 0.0
                    color = base_color
                else:
                    if centroid is None:
                        inward_x = 0.0
                        inward_y = 0.0
                    else:
                        inward_x = centroid[0] - x
                        inward_y = centroid[1] - y
                    inward_norm = math.sqrt((inward_x * inward_x) + (inward_y * inward_y))
                    if inward_norm > radial_eps:
                        inward_x /= inward_norm
                        inward_y /= inward_norm
                    else:
                        inward_x = 0.0
                        inward_y = 0.0
                    radial_component = (vx * inward_x) + (vy * inward_y)
                    if radial_component > radial_debug_neutral_band:
                        color = radial_debug_inward_color
                    elif radial_component < -radial_debug_neutral_band:
                        color = radial_debug_outward_color
                        radial_outward_count += 1
                    else:
                        color = radial_debug_neutral_color
                    ux = inward_x * radial_debug_len_ratio
                    uy = inward_y * radial_debug_len_ratio
                render_points.append((x, y, ux, uy, color))
            if commit_positions:
                last_positions_for_effective[fleet_id] = next_positions
            return render_points, radial_outward_count

        # Pre-render first frame so units are arrows at initialization (no first-frame dots).
        initial_points_a_norm = normalize_frame_points(position_frames[0].get("A", []), "A")
        initial_points_b_norm = normalize_frame_points(position_frames[0].get("B", []), "B")
        initial_render_points_a, _ = build_render_points_for_mode(
            initial_points_a_norm,
            "A",
            commit_positions=False,
        )
        initial_render_points_b, _ = build_render_points_for_mode(
            initial_points_b_norm,
            "B",
            commit_positions=False,
        )
        quiver_all.remove()
        quiver_all = make_quiver(initial_render_points_a, initial_render_points_b)
        init_xs, _, _, _, _ = build_quiver_data(initial_render_points_a, initial_render_points_b)
        quiver_point_count["value"] = len(init_xs)

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
            last_positions_for_effective["A"] = {}
            last_positions_for_effective["B"] = {}
            battle_ax.set_xlim(0.0, arena_size)
            battle_ax.set_ylim(0.0, arena_size)
            apply_adaptive_ticks(battle_ax, (0.0, arena_size), (0.0, arena_size), force=True)

        def compute_auto_zoom_target(points_a, points_b):
            merged = points_a + points_b
            if not merged:
                return None
            xs = [p[0] for p in merged]
            ys = [p[1] for p in merged]
            center_x = sum(xs) / len(xs)
            center_y = sum(ys) / len(ys)
            farthest_half = 0.0
            for x, y, _, _ in merged:
                dx = abs(x - center_x)
                dy = abs(y - center_y)
                local_half = dx if dx > dy else dy
                if local_half > farthest_half:
                    farthest_half = local_half
            half_1x = arena_size * 0.5
            half_2x = arena_size * 0.25
            half_4x = arena_size / (2.0 * auto_zoom_min_factor)
            required_half = min(max(farthest_half + 1.0, half_4x), half_1x)
            if required_half <= half_4x:
                half = half_4x
            elif required_half <= half_2x:
                half = half_2x
            else:
                half = half_1x
            if not auto_zoom_follow_out_of_bounds:
                center_x = min(max(center_x, half), arena_size - half)
                center_y = min(max(center_y, half), arena_size - half)
            if abs(center_x - auto_zoom_state["target_x"]) < auto_zoom_center_deadband:
                center_x = auto_zoom_state["target_x"]
            if abs(center_y - auto_zoom_state["target_y"]) < auto_zoom_center_deadband:
                center_y = auto_zoom_state["target_y"]
            return (center_x, center_y, half)

        def offscreen_ratio(points_a, points_b):
            merged = points_a + points_b
            if not merged:
                return 0.0
            xlim = battle_ax.get_xlim()
            ylim = battle_ax.get_ylim()
            span_x = xlim[1] - xlim[0]
            span_y = ylim[1] - ylim[0]
            # Trigger region is the central 5%~95% square area of current canvas.
            # With square camera this equals 90% of current view on both axes.
            side = span_x if span_x < span_y else span_y
            cx = (xlim[0] + xlim[1]) * 0.5
            cy = (ylim[0] + ylim[1]) * 0.5
            half_inner = side * 0.45  # 90% side length -> [5%, 95%] equivalent
            inner_x_min = cx - half_inner
            inner_x_max = cx + half_inner
            inner_y_min = cy - half_inner
            inner_y_max = cy + half_inner
            out_count = 0
            for x, y, _, _ in merged:
                if x < inner_x_min or x > inner_x_max or y < inner_y_min or y > inner_y_max:
                    out_count += 1
            return out_count / len(merged)

        def fleet_centroid(points):
            if not points:
                return None
            sum_x = 0.0
            sum_y = 0.0
            for x, y, _, _ in points:
                sum_x += x
                sum_y += y
            count = float(len(points))
            return (sum_x / count, sum_y / count)

        def total_centroid(points_a, points_b):
            centroid_a = fleet_centroid(points_a)
            centroid_b = fleet_centroid(points_b)
            count_a = len(points_a)
            count_b = len(points_b)
            if centroid_a is None and centroid_b is None:
                return None
            if centroid_a is None:
                return centroid_b
            if centroid_b is None:
                return centroid_a
            total_count = float(count_a + count_b)
            cx = ((centroid_a[0] * count_a) + (centroid_b[0] * count_b)) / total_count
            cy = ((centroid_a[1] * count_a) + (centroid_b[1] * count_b)) / total_count
            return (cx, cy)

        def centroid_offset_ratio(points_a, points_b):
            centroid = total_centroid(points_a, points_b)
            if centroid is None:
                return 0.0
            xlim = battle_ax.get_xlim()
            ylim = battle_ax.get_ylim()
            span_x = xlim[1] - xlim[0]
            span_y = ylim[1] - ylim[0]
            side = span_x if span_x < span_y else span_y
            half_view = side * 0.5
            if half_view <= 0.0:
                return 0.0
            center_x = (xlim[0] + xlim[1]) * 0.5
            center_y = (ylim[0] + ylim[1]) * 0.5
            dx = centroid[0] - center_x
            dy = centroid[1] - center_y
            return math.sqrt((dx * dx) + (dy * dy)) / half_view

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
            nonlocal quiver_all
            xs, ys, us, vs, colors = build_quiver_data(points_a, points_b)
            next_count = len(xs)
            if next_count != quiver_point_count["value"]:
                quiver_all.remove()
                quiver_all = make_quiver(points_a, points_b)
                quiver_point_count["value"] = next_count
                return
            quiver_all.set_offsets(list(zip(xs, ys)))
            quiver_all.set_UVC(us, vs)
            quiver_all.set_color(colors)

        def update_death_linger(frame_tick: int, alive_points_norm, fleet_id: str):
            prev_map = last_alive_by_fleet[fleet_id]
            current_map = {
                unit_id: (x, y, ox, oy)
                for unit_id, x, y, ox, oy, _, _ in alive_points_norm
            }
            current_ids = set(current_map.keys())

            for unit_id, prev in prev_map.items():
                if unit_id not in current_ids:
                    x, y, ox, oy = prev
                    death_linger[fleet_id][unit_id] = (x, y, ox, oy, frame_tick + death_linger_ticks - 1)

            for unit_id in current_ids:
                if unit_id in death_linger[fleet_id]:
                    del death_linger[fleet_id][unit_id]

            expired = [
                unit_id
                for unit_id, (_, _, _, _, expire_tick) in death_linger[fleet_id].items()
                if frame_tick > expire_tick
            ]
            for unit_id in expired:
                del death_linger[fleet_id][unit_id]

            last_alive_by_fleet[fleet_id] = current_map

        def clear_death_ring_patches():
            for patch in death_ring_patches:
                patch.remove()
            death_ring_patches.clear()

        def draw_death_rings():
            clear_death_ring_patches()
            for fleet_id in ("A", "B"):
                for unit_id in sorted(death_linger[fleet_id].keys()):
                    x, y, _, _, _ = death_linger[fleet_id][unit_id]
                    patch = Circle(
                        (x, y),
                        death_ring_radius,
                        fill=False,
                        edgecolor=death_ring_color,
                        linewidth=death_ring_linewidth,
                        alpha=death_ring_alpha,
                        zorder=5.0,
                    )
                    battle_ax.add_patch(patch)
                    death_ring_patches.append(patch)

        def update_frame(frame):
            alive_points_a_norm = normalize_frame_points(frame.get("A", []), "A")
            alive_points_b_norm = normalize_frame_points(frame.get("B", []), "B")
            alive_points_a = [(x, y, ox, oy) for _, x, y, ox, oy, _, _ in alive_points_a_norm]
            alive_points_b = [(x, y, ox, oy) for _, x, y, ox, oy, _, _ in alive_points_b_norm]
            render_points_a, radial_outward_a = build_render_points_for_mode(alive_points_a_norm, "A")
            render_points_b, radial_outward_b = build_render_points_for_mode(alive_points_b_norm, "B")

            update_death_linger(frame["tick"], alive_points_a_norm, "A")
            update_death_linger(frame["tick"], alive_points_b_norm, "B")
            if vector_display_mode != "radial_debug":
                for unit_id in sorted(death_linger["A"].keys()):
                    x, y, ox, oy, _ = death_linger["A"][unit_id]
                    render_points_a.append((x, y, ox, oy, fleet_a_color))
                for unit_id in sorted(death_linger["B"].keys()):
                    x, y, ox, oy, _ = death_linger["B"][unit_id]
                    render_points_b.append((x, y, ox, oy, fleet_b_color))

            update_quiver(render_points_a, render_points_b)
            draw_death_rings()
            if auto_zoom_2d:
                if frame["tick"] == first_tick:
                    reset_to_full_view()
                    auto_zoom_initialized["value"] = False
                if frame["tick"] % auto_zoom_tick_interval == 0:
                    ratio = offscreen_ratio(alive_points_a, alive_points_b)
                    centroid_ratio = centroid_offset_ratio(alive_points_a, alive_points_b)
                    target = compute_auto_zoom_target(alive_points_a, alive_points_b)
                    if target is not None:
                        _, _, target_half = target
                        current_half = auto_zoom_state["current_half"]
                        zoom_trigger = (
                            (not auto_zoom_initialized["value"])
                            or (target_half < (current_half * auto_zoom_zoomin_trigger_ratio))
                        )
                        pan_trigger = (
                            ratio > auto_zoom_offscreen_trigger_ratio
                            or centroid_ratio > auto_zoom_centroid_trigger_ratio
                        )
                        if zoom_trigger:
                            begin_camera_transition(target, mode="zoom")
                            auto_zoom_initialized["value"] = True
                        elif pan_trigger:
                            begin_camera_transition(target, mode="pan")
                apply_auto_zoom_step()
            tick_index = int(frame["tick"]) - 1
            a_series = fleet_size_trajectory.get("A", [])
            b_series = fleet_size_trajectory.get("B", [])
            if tick_index < 0:
                tick_index = 0
            if a_series:
                tick_index_a = min(tick_index, len(a_series) - 1)
                curr_size_a = float(a_series[tick_index_a])
            else:
                curr_size_a = 0.0
            if b_series:
                tick_index_b = min(tick_index, len(b_series) - 1)
                curr_size_b = float(b_series[tick_index_b])
            else:
                curr_size_b = 0.0
            pct_a = (curr_size_a / initial_size_a * 100.0) if initial_size_a > 0.0 else 0.0
            pct_b = (curr_size_b / initial_size_b * 100.0) if initial_size_b > 0.0 else 0.0
            battle_ax.set_title(f"Battlefield (tick={frame['tick']})")
            if vector_display_mode == "radial_debug":
                mode_outliers = radial_outward_a + radial_outward_b
            else:
                mode_outliers = 0
            debug_text.set_text(format_debug_text(vector_display_mode, mode_outliers))
            count_text.set_text(format_count_text(len(alive_points_a), len(alive_points_b), curr_size_a, curr_size_b, pct_a, pct_b))
            return (quiver_all, count_text, debug_text, *death_ring_patches)

        anim = FuncAnimation(
            fig,
            update_frame,
            frames=position_frames,
            interval=frame_interval_ms,
            blit=False,
            repeat=True,
        )
    else:
        final_a = [
            (
                final_state.units[uid].position.x,
                final_state.units[uid].position.y,
                final_state.units[uid].orientation_vector.x,
                final_state.units[uid].orientation_vector.y,
            )
            for uid in final_state.fleets["A"].unit_ids
            if uid in final_state.units
        ]
        final_b = [
            (
                final_state.units[uid].position.x,
                final_state.units[uid].position.y,
                final_state.units[uid].orientation_vector.x,
                final_state.units[uid].orientation_vector.y,
            )
            for uid in final_state.fleets["B"].unit_ids
            if uid in final_state.units
        ]
        quiver_all.remove()
        quiver_all = make_quiver(final_a, final_b)
        curr_size_a = 0.0
        curr_size_b = 0.0
        if fleet_size_trajectory.get("A"):
            curr_size_a = float(fleet_size_trajectory["A"][-1])
        if fleet_size_trajectory.get("B"):
            curr_size_b = float(fleet_size_trajectory["B"][-1])
        pct_a = (curr_size_a / initial_size_a * 100.0) if initial_size_a > 0.0 else 0.0
        pct_b = (curr_size_b / initial_size_b * 100.0) if initial_size_b > 0.0 else 0.0
        debug_text.set_text(format_debug_text(vector_display_mode, 0))
        count_text.set_text(format_count_text(len(final_a), len(final_b), curr_size_a, curr_size_b, pct_a, pct_b))
        anim = None

    cohesion_ax.plot(ticks, trajectory["A"], label=f"A ({fleet_a_label})", color=fleet_a_color)
    cohesion_ax.plot(ticks, trajectory["B"], label=f"B ({fleet_b_label})", color=fleet_b_color)
    cohesion_ax.set_xlabel("Tick")
    cohesion_ax.set_ylabel("Cohesion")
    cohesion_ax.legend()

    alive_ax.plot(ticks, alive_trajectory["A"], label=f"A ({fleet_a_label})", color=fleet_a_color)
    alive_ax.plot(ticks, alive_trajectory["B"], label=f"B ({fleet_b_label})", color=fleet_b_color)
    alive_ax.set_xlabel("Tick")
    alive_ax.set_ylabel("Alive Units")
    alive_ax.legend()

    fig.subplots_adjust(left=0.02, right=0.98, top=0.93, bottom=0.07)
    plt.show()
