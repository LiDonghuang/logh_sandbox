import math
import random
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Mapping, Sequence

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection
from matplotlib.animation import FFMpegWriter, FuncAnimation
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
from matplotlib.patches import Circle, Ellipse, PathPatch, Rectangle
from matplotlib.path import Path as MplPath

from runtime.runtime_v0_1 import BattleState


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


def _resolve_export_video_spec(export_video_cfg: Mapping[str, Any] | None) -> dict[str, Any]:
    cfg = export_video_cfg if isinstance(export_video_cfg, Mapping) else {}
    enabled = bool(_cfg(cfg, "enabled", False))
    full_plot = bool(_cfg(cfg, "full_plot", True))
    width_px = max(16, int(_cfg(cfg, "width_px", 1920)))
    height_px = max(16, int(_cfg(cfg, "height_px", 1080)))
    if not full_plot:
        width_px = height_px
    if width_px % 2 != 0:
        width_px += 1
    if height_px % 2 != 0:
        height_px += 1
    dpi = max(72, int(_cfg(cfg, "dpi", 120)))
    return {
        "cfg": cfg,
        "enabled": enabled,
        "full_plot": full_plot,
        "width_px": width_px,
        "height_px": height_px,
        "dpi": dpi,
    }


def _resolve_ffmpeg_path() -> str | None:
    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path:
        return ffmpeg_path
    try:
        import imageio_ffmpeg  # type: ignore

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return None


def _seed_word_from_int(seed_value: int, length: int = 6) -> str:
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    rng = random.Random(int(seed_value) & 0xFFFFFFFF)
    return "".join(rng.choice(letters) for _ in range(max(1, length)))


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
    fleet_a_full_name: str,
    fleet_b_full_name: str,
    fleet_a_avatar: str,
    fleet_b_avatar: str,
    fleet_a_color: str,
    fleet_b_color: str,
    auto_zoom_2d: bool,
    frame_interval_ms: int,
    background_seed: int,
    viz_settings: Mapping[str, Any],
    tick_plots_follow_battlefield_tick: bool = False,
    display_language: str = "EN",
    unit_direction_mode: str = "effective",
    show_attack_target_lines: bool = False,
    observer_telemetry: Mapping[str, Any] | None = None,
    bridge_telemetry: Mapping[str, Any] | None = None,
    observer_enabled: bool = True,
    plot_profile: str = "extended",
    plot_smoothing_ticks: int = 5,
    combat_telemetry: Mapping[str, Sequence[int | float]] | None = None,
    debug_context: Mapping[str, Any] | None = None,
    export_video_cfg: Mapping[str, Any] | None = None,
    boundary_enabled: bool = True,
    boundary_hard_enabled: bool = True,
    damage_per_tick: float = 1.0,
) -> None:
    export_video_spec = _resolve_export_video_spec(export_video_cfg)
    export_video_cfg_layout = export_video_spec["cfg"]
    export_video_enabled_layout = bool(export_video_spec["enabled"])
    export_full_plot_layout = bool(export_video_spec["full_plot"])
    export_width_px_layout = int(export_video_spec["width_px"])
    export_height_px_layout = int(export_video_spec["height_px"])
    export_dpi_layout = int(export_video_spec["dpi"])
    interactive_state_before_render = plt.isinteractive()
    if export_video_enabled_layout:
        # Export-only path should not spawn interactive GUI windows.
        plt.ioff()

    fig_size = _cfg(viz_settings, "figure_size", [20, 8])
    width_ratios = _cfg(viz_settings, "layout_width_ratios", [100.0, 45.0, 45.0])
    if isinstance(width_ratios, Sequence) and len(width_ratios) >= 3:
        battle_col_ratio = float(width_ratios[0])
        plot_col_ratio = float(width_ratios[1])
        aux_col_ratio = float(width_ratios[2])
    else:
        battle_col_ratio = 100.0
        plot_col_ratio = 35.0
        aux_col_ratio = 35.0
    if battle_col_ratio <= 0.0:
        battle_col_ratio = 100.0
    if plot_col_ratio <= 0.0:
        plot_col_ratio = 35.0
    if aux_col_ratio <= 0.0:
        aux_col_ratio = 35.0
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
    orbit_cfg = _cfg(viz_settings, "background_orbits", {})
    asteroids_cfg = _cfg(viz_settings, "background_asteroids", {})
    belts_cfg = _cfg(viz_settings, "background_belts", {})
    battle_overlay_fontsize = float(_cfg(viz_settings, "battle_overlay_fontsize", 10.0))
    if battle_overlay_fontsize < 8.0:
        battle_overlay_fontsize = 8.0

    display_language = str(display_language).upper()
    if display_language not in {"EN", "ZH"}:
        display_language = "EN"
    show_attack_target_lines = bool(show_attack_target_lines)
    settings_vector_display_mode = str(
        _cfg(viz_settings, "vector_display_mode", unit_direction_mode)
    ).strip().lower()
    unit_direction_mode = str(unit_direction_mode).strip().lower()
    valid_vector_display_modes = {"effective", "free", "attack", "composite", "radial_debug"}
    if unit_direction_mode not in valid_vector_display_modes:
        unit_direction_mode = settings_vector_display_mode
    if unit_direction_mode not in valid_vector_display_modes:
        unit_direction_mode = "effective"
    needs_attack_direction_map = unit_direction_mode in {"attack", "composite"}
    needs_target_segments = bool(show_attack_target_lines)
    needs_target_geometry = bool(needs_attack_direction_map or needs_target_segments)
    plot_profile = str(plot_profile).strip().lower()
    if plot_profile not in {"baseline", "extended"}:
        plot_profile = "extended"
    plot_panel_enabled = plot_profile in {"baseline", "extended"}
    extended_plot_mode = plot_profile == "extended"
    zh_battle_title_suffix = "\u661f\u57df\u4f1a\u6218"
    zh_standard_time_prefix = "\u6807\u51c6\u65f6"

    seed_word = _seed_word_from_int(background_seed, length=6)
    if display_language == "ZH":
        battle_title_base = f"{seed_word} {zh_battle_title_suffix}"
    else:
        battle_title_base = f"{seed_word} Starfield Engagement"

    ticks = list(range(len(trajectory["A"])))

    def extract_observer_series(metric_key: str, side: str, length: int) -> list[float]:
        result: list[float] = []
        if isinstance(observer_telemetry, Mapping):
            metric_bucket = observer_telemetry.get(metric_key, {})
            if isinstance(metric_bucket, Mapping):
                raw = metric_bucket.get(side, [])
                if isinstance(raw, (list, tuple)):
                    for value in raw[:length]:
                        try:
                            result.append(float(value))
                        except (TypeError, ValueError):
                            result.append(float("nan"))
        if len(result) < length:
            result.extend([float("nan")] * (length - len(result)))
        return result

    def extract_global_observer_series(metric_key: str, length: int) -> list[float]:
        result: list[float] = []
        if isinstance(observer_telemetry, Mapping):
            raw = observer_telemetry.get(metric_key, [])
            if isinstance(raw, (list, tuple)):
                for value in raw[:length]:
                    try:
                        result.append(float(value))
                    except (TypeError, ValueError):
                        result.append(float("nan"))
        if len(result) < length:
            result.extend([float("nan")] * (length - len(result)))
        return result

    def extract_fixture_series(metric_key: str, length: int) -> list[float]:
        result: list[float] = []
        if isinstance(observer_telemetry, Mapping):
            fixture_bucket = observer_telemetry.get("fixture", {})
            if isinstance(fixture_bucket, Mapping):
                raw = fixture_bucket.get(metric_key, [])
                if isinstance(raw, (list, tuple)):
                    for value in raw[:length]:
                        try:
                            result.append(float(value))
                        except (TypeError, ValueError):
                            result.append(float("nan"))
        if len(result) < length:
            result.extend([float("nan")] * (length - len(result)))
        return result

    def has_finite_value(series: Sequence[float]) -> bool:
        for value in series:
            if math.isfinite(float(value)):
                return True
        return False

    runtime_cohesion_a = extract_observer_series("cohesion_v3", "A", len(ticks))
    runtime_cohesion_b = extract_observer_series("cohesion_v3", "B", len(ticks))
    observer_runtime_cohesion_ready = (
        bool(plot_panel_enabled)
        and has_finite_value(runtime_cohesion_a)
        and has_finite_value(runtime_cohesion_b)
    )
    # Color consistency rule:
    # whenever a subplot encodes side A/B, it must reuse battlefield fleet colors.
    fig = plt.figure(figsize=(float(fig_size[0]), float(fig_size[1])))
    if export_video_enabled_layout:
        # Lock final export geometry before any overlay metrics are computed.
        fig.set_size_inches(
            export_width_px_layout / export_dpi_layout,
            export_height_px_layout / export_dpi_layout,
            forward=True,
        )
    fig_manager = getattr(fig.canvas, "manager", None)
    if fig_manager is not None and (not export_video_enabled_layout):
        try:
            fig_manager.set_window_title("BATTLEFIELD")
        except Exception:
            pass

    def apply_window_maximize_and_sync() -> None:
        if export_video_enabled_layout or fig_manager is None:
            return
        try:
            manager_window = getattr(fig_manager, "window", None)
            if manager_window is None:
                return
            if hasattr(manager_window, "state"):
                manager_window.state("zoomed")
            elif hasattr(manager_window, "showMaximized"):
                manager_window.showMaximized()
            if hasattr(manager_window, "update_idletasks"):
                manager_window.update_idletasks()
            window_sizes = []
            if hasattr(manager_window, "winfo_width") and hasattr(manager_window, "winfo_height"):
                window_sizes.append((int(manager_window.winfo_width()), int(manager_window.winfo_height())))
            if hasattr(manager_window, "size"):
                qsize = manager_window.size()
                if qsize is not None and hasattr(qsize, "width") and hasattr(qsize, "height"):
                    window_sizes.append((int(qsize.width()), int(qsize.height())))
            for ww, hh in window_sizes:
                if ww > 100 and hh > 100:
                    figure_dpi = max(72.0, float(fig.get_dpi()))
                    fig.set_size_inches(ww / figure_dpi, hh / figure_dpi, forward=True)
                    return
        except Exception:
            pass
    apply_window_maximize_and_sync()

    outer_grid = fig.add_gridspec(
        1,
        3,
        width_ratios=[battle_col_ratio, plot_col_ratio, aux_col_ratio],
        wspace=0.20,
    )
    column2_grid = outer_grid[0, 1].subgridspec(
        6,
        1,
        hspace=0.34,
    )
    column3_grid = outer_grid[0, 2].subgridspec(
        6,
        1,
        hspace=0.30,
    )

    battle_ax = fig.add_subplot(outer_grid[0, 0])
    slot01_02_merged_ax = fig.add_subplot(column2_grid[0:2, 0])
    plot_slot_axes = {
        "slot_01": slot01_02_merged_ax,
        "slot_02": slot01_02_merged_ax,
        "slot_03": fig.add_subplot(column2_grid[2, 0]),
        "slot_04": fig.add_subplot(column2_grid[3, 0]),
        "slot_05": fig.add_subplot(column2_grid[4, 0]),
        "slot_06": fig.add_subplot(column2_grid[5, 0]),
        "slot_07": fig.add_subplot(column3_grid[0, 0]),
        "slot_08": fig.add_subplot(column3_grid[1, 0]),
        "slot_09": fig.add_subplot(column3_grid[2, 0]),
        "slot_10": fig.add_subplot(column3_grid[3, 0]),
    }
    # Active slot map:
    # slot_01+02 Alive, slot_03 FireEff, slot_04 LossRate,
    # slot_05 Coh_v2/Coh_v3, slot_06 CollapseSig, slot_07 SplitSep,
    # slot_08 FrontCurv, slot_09 Intermix, slot_10 C_W_PShare.
    alive_ax = plot_slot_axes["slot_01"]  # occupies slot_01 + slot_02
    fire_efficiency_ax = plot_slot_axes["slot_03"]
    loss_rate_ax = plot_slot_axes["slot_04"]
    cohesion_ax = plot_slot_axes["slot_05"]
    collapse_signal_ax = plot_slot_axes["slot_06"]
    split_ax = plot_slot_axes["slot_07"]
    front_curvature_ax = plot_slot_axes["slot_08"]
    wedge_ax = plot_slot_axes["slot_09"]
    center_wing_parallel_share_ax = plot_slot_axes["slot_10"]
    debug_ax = fig.add_subplot(column3_grid[4:, 0])

    battle_ax.set_title(battle_title_base)
    battle_ax.set_xlim(0.0, arena_size)
    battle_ax.set_ylim(0.0, arena_size)
    battle_ax.set_xlabel("X")
    battle_ax.set_ylabel("Y")
    battle_ax.set_aspect("equal", adjustable="box", anchor="E")
    battle_ax.set_box_aspect(1)
    battle_ax.set_facecolor(battlefield_bg_color)

    debug_ax.set_xlim(0.0, 1.0)
    debug_ax.set_ylim(0.0, 1.0)
    debug_ax.set_xticks([])
    debug_ax.set_yticks([])
    debug_ax.set_facecolor("#ffffff")
    for spine in debug_ax.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(1.2)
        spine.set_edgecolor("#444444")
    # Lock layout margins before any overlay geometry converts points -> axes fractions.
    fig.subplots_adjust(left=0.02, right=0.98, top=0.93, bottom=0.07)
    if export_video_enabled_layout and (not export_full_plot_layout):
        for ax in fig.axes:
            if ax is battle_ax:
                continue
            ax.set_visible(False)
        battle_ax.set_position([0.0, 0.0, 1.0, 1.0])
    elif plot_panel_enabled:
        battle_ax_pos = battle_ax.get_position()
        battle_shift_right = 0.015
        max_shift = max(0.0, battle_ax_pos.width - 0.05)
        battle_shift_right = min(battle_shift_right, max_shift)
        battle_ax.set_position(
            [
                battle_ax_pos.x0 + battle_shift_right,
                battle_ax_pos.y0,
                battle_ax_pos.width - battle_shift_right,
                battle_ax_pos.height,
            ]
        )

    def draw_space_background(ax, size: float, rng: random.Random) -> dict[str, int]:
        def float_range(raw: Any, default: Sequence[float]) -> tuple[float, float]:
            if isinstance(raw, (list, tuple)) and len(raw) >= 2:
                low = float(raw[0])
                high = float(raw[1])
            else:
                low = float(default[0])
                high = float(default[1])
            if high < low:
                low, high = high, low
            return low, high

        def int_range(raw: Any, default: Sequence[int]) -> tuple[int, int]:
            low, high = float_range(raw, default)
            return int(round(low)), int(round(high))

        def clamp(value: Any, low: float, high: float, default: float) -> float:
            try:
                numeric = float(value)
            except (TypeError, ValueError):
                numeric = default
            return max(low, min(high, numeric))

        def sample_float(raw: Any, default: Sequence[float]) -> float:
            low, high = float_range(raw, default)
            return rng.uniform(low, high)

        def sample_int(raw: Any, default: Sequence[int]) -> int:
            low, high = int_range(raw, default)
            return rng.randint(low, high)

        def add_circle(x: float, y: float, radius: float, color: str, alpha: float, zorder: float) -> None:
            if radius <= 0.0:
                return
            ax.add_patch(Circle((x, y), radius, color=color, alpha=alpha, zorder=zorder))

        def add_ellipse_ring(
            center_x: float,
            center_y: float,
            outer_width: float,
            outer_height: float,
            inner_width: float,
            inner_height: float,
            angle_deg: float,
            color: str,
            alpha: float,
            zorder: float,
            segments: int = 128,
        ) -> None:
            if outer_width <= 0.0 or outer_height <= 0.0:
                return
            if inner_width <= 0.0 or inner_height <= 0.0:
                return
            if inner_width >= outer_width or inner_height >= outer_height:
                return

            angle_rad = math.radians(angle_deg)
            cos_angle = math.cos(angle_rad)
            sin_angle = math.sin(angle_rad)

            def ellipse_points(width: float, height: float, reverse: bool = False) -> list[tuple[float, float]]:
                theta_values = np.linspace(0.0, 2.0 * math.pi, max(16, segments), endpoint=False)
                if reverse:
                    theta_values = theta_values[::-1]
                points: list[tuple[float, float]] = []
                half_w = 0.5 * width
                half_h = 0.5 * height
                for theta in theta_values:
                    local_x = half_w * math.cos(float(theta))
                    local_y = half_h * math.sin(float(theta))
                    points.append(
                        (
                            center_x + (local_x * cos_angle) - (local_y * sin_angle),
                            center_y + (local_x * sin_angle) + (local_y * cos_angle),
                        )
                    )
                return points

            outer_points = ellipse_points(outer_width, outer_height)
            inner_points = ellipse_points(inner_width, inner_height, reverse=True)
            vertices = (
                [outer_points[0]]
                + outer_points[1:]
                + [outer_points[0]]
                + [inner_points[0]]
                + inner_points[1:]
                + [inner_points[0]]
            )
            codes = (
                [MplPath.MOVETO]
                + [MplPath.LINETO] * (len(outer_points) - 1)
                + [MplPath.CLOSEPOLY]
                + [MplPath.MOVETO]
                + [MplPath.LINETO] * (len(inner_points) - 1)
                + [MplPath.CLOSEPOLY]
            )
            ax.add_patch(
                PathPatch(
                    MplPath(vertices, codes),
                    facecolor=color,
                    edgecolor="none",
                    alpha=alpha,
                    zorder=zorder,
                )
            )

        haze_center_ratio = _cfg(haze_cfg, 'center_ratio', [0.5, 0.5])
        haze_center_x = size * float(haze_center_ratio[0])
        haze_center_y = size * float(haze_center_ratio[1])
        haze_angle = float(_cfg(haze_cfg, 'angle_deg', 135.0))
        inner_major = size * max(0.05, float(_cfg(haze_cfg, 'inner_size_ratio', 0.735)))
        outer_major = inner_major * max(1.0, float(_cfg(haze_cfg, 'outer_inner_ratio', 1.3333333333)))
        axis_ratio = max(0.05, float(_cfg(haze_cfg, 'axis_ratio', 0.3061224489)))
        for major, color, alpha, zorder in (
            (outer_major, str(_cfg(haze_cfg, 'outer_color', '#d7deea')), float(_cfg(haze_cfg, 'outer_alpha', 0.13)), 0.02),
            (inner_major, str(_cfg(haze_cfg, 'inner_color', '#c7d3e5')), float(_cfg(haze_cfg, 'inner_alpha', 0.10)), 0.03),
        ):
            ax.add_patch(
                Ellipse(
                    (haze_center_x, haze_center_y),
                    major,
                    major * axis_ratio,
                    angle=haze_angle,
                    color=color,
                    alpha=alpha,
                    zorder=zorder,
                )
            )

        major_star_colors = list(_cfg(major_star_cfg, 'colors', ['#fff9dc', '#ffe38a', '#ff9a7a']))
        major_star_radius = sample_float(_cfg(major_star_cfg, 'radius_range', [30.0, 45.0]), [30.0, 45.0])
        major_star_color = str(rng.choice(major_star_colors))
        major_star_glow_scale = max(1.0, float(_cfg(major_star_cfg, 'glow_scale', 1.22)))
        major_star_glow_alpha = clamp(_cfg(major_star_cfg, 'glow_alpha', 0.10), 0.0, 1.0, 0.10)
        major_star_core_alpha = clamp(_cfg(major_star_cfg, 'core_alpha', 0.36), 0.0, 1.0, 0.36)
        major_star_x = rng.uniform(0.0, size)
        major_star_y = rng.uniform(0.0, size)
        primary_visual_r = major_star_radius * major_star_glow_scale
        add_circle(major_star_x, major_star_y, primary_visual_r, major_star_color, major_star_glow_alpha, 0.074)
        add_circle(major_star_x, major_star_y, major_star_radius, major_star_color, major_star_core_alpha, 0.075)

        orbital_draw_ratio_max = clamp(_cfg(orbit_cfg, 'draw_extent_ratio_max', 1.25), 1.0, 2.0, 1.25)
        orbital_draw_min = size * (1.0 - orbital_draw_ratio_max)
        orbital_draw_max = size * orbital_draw_ratio_max
        occupied_fields: list[tuple[float, float, float]] = [(major_star_x, major_star_y, primary_visual_r)]

        def in_draw_bounds(x: float, y: float) -> bool:
            return orbital_draw_min <= x <= orbital_draw_max and orbital_draw_min <= y <= orbital_draw_max

        def in_canvas_bounds(x: float, y: float, margin: float = 0.0) -> bool:
            return margin <= x <= (size - margin) and margin <= y <= (size - margin)

        def register_occupied(x: float, y: float, radius: float) -> None:
            if radius > 0.0:
                occupied_fields.append((x, y, radius))

        def overlaps_occupied(x: float, y: float, radius: float, pad: float = 0.0) -> bool:
            return any(math.hypot(x - ox, y - oy) < (radius + oradius + pad) for ox, oy, oradius in occupied_fields)

        orbit_radius_base_ratio = clamp(_cfg(orbit_cfg, 'orbit_radius_base_ratio', 0.5), 0.05, 1.2, 0.5)
        orbit_radius_base = size * orbit_radius_base_ratio * math.sqrt(2.0)
        draw_orbits_enabled = bool(_cfg(orbit_cfg, 'draw_orbits_enabled', False))
        orbit_line_color = str(_cfg(orbit_cfg, 'orbit_line_color', '#6f7784'))
        orbit_line_alpha = clamp(_cfg(orbit_cfg, 'orbit_line_alpha', 0.22), 0.0, 1.0, 0.22)
        orbit_line_width = max(0.1, float(_cfg(orbit_cfg, 'orbit_line_width', 0.55)))
        orbit_eccentricity_near = clamp(_cfg(orbit_cfg, 'eccentricity_near', 0.02), 0.0, 0.85, 0.02)
        orbit_eccentricity_far = clamp(_cfg(orbit_cfg, 'eccentricity_far', 0.24), orbit_eccentricity_near, 0.85, orbit_eccentricity_near)
        orbit_axis_angle_deg = rng.uniform(0.0, 180.0)
        orbit_axis_angle_rad = math.radians(orbit_axis_angle_deg)
        orbit_axis_cos = math.cos(orbit_axis_angle_rad)
        orbit_axis_sin = math.sin(orbit_axis_angle_rad)
        belt_gap_ratio = clamp(_cfg(orbit_cfg, 'belt_planet_exclusion_gap_ratio', 0.06), 0.0, 1.0, 0.06)
        belt_belt_gap_scale = clamp(_cfg(orbit_cfg, 'belt_belt_exclusion_scale', 0.5), 0.0, 2.0, 0.5)

        def build_orbit_shell(orbit_ratio: float) -> dict[str, float]:
            progress = clamp(orbit_ratio, 0.0, 1.0, orbit_ratio)
            eccentricity = orbit_eccentricity_near + ((orbit_eccentricity_far - orbit_eccentricity_near) * progress)
            semi_major = max(1.0, orbit_radius_base * orbit_ratio)
            semi_minor = semi_major * math.sqrt(max(0.05, 1.0 - (eccentricity * eccentricity)))
            center_offset = semi_major * eccentricity
            return {
                'semi_major': semi_major,
                'semi_minor': semi_minor,
                'center_x': major_star_x - (center_offset * orbit_axis_cos),
                'center_y': major_star_y - (center_offset * orbit_axis_sin),
                'angle_deg': orbit_axis_angle_deg,
            }

        def draw_orbit_path(shell: Mapping[str, float]) -> None:
            if not draw_orbits_enabled:
                return
            ax.add_patch(
                Ellipse(
                    (float(shell['center_x']), float(shell['center_y'])),
                    2.0 * float(shell['semi_major']),
                    2.0 * float(shell['semi_minor']),
                    angle=float(shell['angle_deg']),
                    fill=False,
                    edgecolor=orbit_line_color,
                    linewidth=orbit_line_width,
                    linestyle='--',
                    alpha=orbit_line_alpha,
                    zorder=0.076,
                )
            )

        def orbit_point(shell: Mapping[str, float], theta: float, radial_scale: float = 1.0) -> tuple[float, float]:
            local_x = float(shell['semi_major']) * radial_scale * math.cos(theta)
            local_y = float(shell['semi_minor']) * radial_scale * math.sin(theta)
            return (
                float(shell['center_x']) + (local_x * orbit_axis_cos) - (local_y * orbit_axis_sin),
                float(shell['center_y']) + (local_x * orbit_axis_sin) + (local_y * orbit_axis_cos),
            )

        asteroid_count_range = _cfg(asteroids_cfg, 'count_range', [0, 3])
        orbit_ratio_range = _cfg(asteroids_cfg, 'orbit_ratio_range', [0.18, 0.95])
        orbit_jitter_range = _cfg(asteroids_cfg, 'orbit_jitter_range', [0.92, 1.08])
        angle_jitter_deg = max(0.0, float(_cfg(asteroids_cfg, 'angle_jitter_deg', 12.0)))
        planet_angle_jitter_rad = math.radians(angle_jitter_deg)
        planet_orbit_gap_ratio = clamp(_cfg(orbit_cfg, 'planet_orbit_gap_ratio_min', 0.01), 0.0, 1.0, 0.01)
        min_separation_ratio = max(0.0, float(_cfg(asteroids_cfg, 'min_separation_ratio', 0.11)))
        asteroid_radius_range = float_range(_cfg(asteroids_cfg, 'radius_range', [5.0, 10.0]), [5.0, 10.0])
        asteroid_colors = list(_cfg(asteroids_cfg, 'colors', ['#8f969f', '#9aa1ab', '#8a939c']))
        asteroid_alpha = clamp(_cfg(asteroids_cfg, 'alpha', 0.72), 0.0, 1.0, 0.72)
        small_zone_max_ratio = clamp(_cfg(asteroids_cfg, 'small_zone_max_ratio', 0.42), 0.0, 1.0, 0.42)
        mid_zone_max_ratio = clamp(_cfg(asteroids_cfg, 'mid_zone_max_ratio', 0.72), small_zone_max_ratio, 1.0, 0.72)
        moon_cfg = _cfg(asteroids_cfg, 'moons', {})
        moon_enabled = bool(_cfg(moon_cfg, 'enabled', True))
        moon_size_ratio_range = float_range(_cfg(moon_cfg, 'size_ratio_range', [0.1, 0.2]), [0.1, 0.2])
        moon_orbit_scale_range = float_range(_cfg(moon_cfg, 'orbit_scale_range', [2.2, 4.5]), [2.2, 4.5])
        moon_count_range_medium = _cfg(moon_cfg, 'count_range_medium', [0, 1])
        moon_count_range_large = _cfg(moon_cfg, 'count_range_large', [1, 2])
        moon_color = str(_cfg(moon_cfg, 'color', '#cfd5df'))
        moon_alpha = clamp(_cfg(moon_cfg, 'alpha', 0.75), 0.0, 1.0, 0.75)
        ring_cfg = _cfg(asteroids_cfg, 'gas_giant_ring', {})
        ring_enabled = bool(_cfg(ring_cfg, 'enabled', True))
        ring_diameter_scale_range = float_range(_cfg(ring_cfg, 'diameter_scale_range', [2.1, 3.4]), [2.1, 3.4])
        ring_axis_ratio_range = float_range(_cfg(ring_cfg, 'axis_ratio_range', [0.2, 0.55]), [0.2, 0.55])
        ring_angle_deg_range = float_range(_cfg(ring_cfg, 'angle_deg_range', [0.0, 180.0]), [0.0, 180.0])
        ring_color = str(_cfg(ring_cfg, 'color', '#c6ccd6'))
        ring_alpha = clamp(_cfg(ring_cfg, 'alpha', 0.65), 0.0, 1.0, 0.65)
        ring_band_width_ratio = 0.24
        orbit_jitter_low, orbit_jitter_high = float_range(orbit_jitter_range, [0.92, 1.08])
        belt_cluster_count_range = _cfg(belts_cfg, 'cluster_count_range', [0, 10])
        belt_points_per_360 = float_range(_cfg(belts_cfg, 'points_per_360_degree_range', [120.0, 120.0]), [120.0, 120.0])
        belt_ratio_range = _cfg(belts_cfg, 'orbit_ratio_range', [0.55, 0.95])
        belt_thickness_ratio = float_range(_cfg(belts_cfg, 'thickness_ratio_range', [0.05, 0.12]), [0.05, 0.12])
        belt_arc_span_deg = float_range(_cfg(belts_cfg, 'arc_span_deg_range', [20.0, 55.0]), [20.0, 55.0])
        belt_curve_strength = float_range(_cfg(belts_cfg, 'curve_strength_range', [-0.06, 0.06]), [-0.06, 0.06])
        belt_asteroid_radius = float_range(_cfg(belts_cfg, 'asteroid_radius_range', [0.1, 0.2]), [0.1, 0.2])
        belt_color = str(_cfg(belts_cfg, 'color', '#8e96a3'))
        belt_alpha = clamp(_cfg(belts_cfg, 'alpha', 0.55), 0.0, 1.0, 0.55)
        target_planets = sample_int(asteroid_count_range, [0, 3])
        target_belts = sample_int(belt_cluster_count_range, [0, 10])
        orbit_count_range = _cfg(orbit_cfg, 'orbit_count_range', [8, 12])
        orbit_pool_low = min(float_range(orbit_ratio_range, [0.18, 0.95])[0], float_range(belt_ratio_range, [0.55, 0.95])[0])
        orbit_pool_high = max(float_range(orbit_ratio_range, [0.18, 0.95])[1], float_range(belt_ratio_range, [0.55, 0.95])[1])
        shared_orbit_pool: list[float] = []
        assigned_orbit_ratios: list[float] = []

        def build_orbit_pool(pool_count: int, low: float, high: float) -> list[float]:
            if pool_count <= 0:
                return []
            low = clamp(low, 0.0, 1.0, low)
            high = clamp(high, low, 1.0, high)
            if pool_count == 1 or abs(high - low) <= 1e-9:
                return [0.5 * (low + high)]
            spacing = (high - low) / float(pool_count - 1)
            pool: list[float] = []
            for idx in range(pool_count):
                base_ratio = low + (idx * spacing)
                jitter = (rng.uniform(orbit_jitter_low, orbit_jitter_high) - 1.0) * 0.5 * spacing
                pool.append(clamp(base_ratio + jitter, low, high, base_ratio))
            pool.sort()
            return pool

        shared_pool_count = max(
            sample_int(orbit_count_range, [8, 12]),
            target_planets + target_belts,
        )
        shared_orbit_pool = build_orbit_pool(shared_pool_count, orbit_pool_low, orbit_pool_high)

        def ensure_shared_orbit_pool(ratio_range: Sequence[float], required_count: int) -> None:
            nonlocal shared_orbit_pool
            if required_count <= 0:
                return
            low, high = float_range(ratio_range, [0.15, 0.85])
            low = clamp(low, 0.0, 1.0, low)
            high = clamp(high, low, 1.0, high)
            eligible = [ratio for ratio in shared_orbit_pool if low <= ratio <= high]
            if len(eligible) >= required_count:
                return
            supplemental = build_orbit_pool(required_count + 2, low, high)
            existing = {round(ratio, 6) for ratio in shared_orbit_pool}
            for candidate in supplemental:
                key = round(candidate, 6)
                if key in existing:
                    continue
                shared_orbit_pool.append(candidate)
                existing.add(key)
            shared_orbit_pool.sort()

        def choose_orbit_ratios(target_count: int, ratio_range: Sequence[float], min_gap: float) -> list[float]:
            if target_count <= 0:
                return []
            low, high = float_range(ratio_range, [0.15, 0.85])
            low = clamp(low, 0.0, 1.0, low)
            high = clamp(high, low, 1.0, high)
            ensure_shared_orbit_pool((low, high), target_count)
            ratios: list[float] = []
            for candidate in shared_orbit_pool:
                if candidate < low or candidate > high:
                    continue
                if (
                    all(abs(candidate - existing) >= min_gap for existing in ratios)
                    and all(abs(candidate - existing) >= min_gap for existing in assigned_orbit_ratios)
                ):
                    ratios.append(candidate)
                    if len(ratios) >= target_count:
                        break
            if len(ratios) < target_count:
                supplemental = build_orbit_pool(target_count * 2, low, high)
                for candidate in supplemental:
                    if (
                        all(abs(candidate - existing) >= min_gap for existing in ratios)
                        and all(abs(candidate - existing) >= min_gap for existing in assigned_orbit_ratios)
                    ):
                        ratios.append(candidate)
                        if len(ratios) >= target_count:
                            break
            ratios.sort()
            assigned_orbit_ratios.extend(ratios)
            return ratios[:target_count]

        min_planet_sep = orbit_radius_base * min_separation_ratio

        def classify_planet(orbit_ratio: float) -> tuple[float, str]:
            radius_low, radius_high = asteroid_radius_range
            radius_span = max(0.0, radius_high - radius_low)
            if radius_span <= 1e-9:
                return radius_low, 'small'
            if orbit_ratio < small_zone_max_ratio:
                return rng.uniform(radius_low, radius_low + (0.45 * radius_span)), 'small'
            if orbit_ratio < mid_zone_max_ratio:
                return rng.uniform(radius_low + (0.30 * radius_span), radius_low + (0.75 * radius_span)), 'medium'
            return rng.uniform(radius_low + (0.55 * radius_span), radius_high), 'large'

        def draw_planet(x: float, y: float, orbit_ratio: float) -> None:
            radius, size_band = classify_planet(orbit_ratio)
            visual_radius = radius
            if ring_enabled and size_band in {'medium', 'large'}:
                ring_major = max((2.0 * radius) * sample_float(ring_diameter_scale_range, [2.1, 3.4]), radius * 2.0)
                ring_minor = ring_major * sample_float(ring_axis_ratio_range, [0.2, 0.55])
                ring_angle = sample_float(ring_angle_deg_range, [0.0, 180.0])
                inner_scale = max(0.05, 1.0 - ring_band_width_ratio)
                add_ellipse_ring(
                    x,
                    y,
                    ring_major,
                    ring_minor,
                    ring_major * inner_scale,
                    ring_minor * inner_scale,
                    ring_angle,
                    ring_color,
                    ring_alpha,
                    0.098,
                )
                visual_radius = max(visual_radius, 0.5 * ring_major)
            add_circle(x, y, radius, str(rng.choice(asteroid_colors)), asteroid_alpha, 0.10)
            register_occupied(x, y, visual_radius)
            if moon_enabled and size_band in {'medium', 'large'}:
                moon_count = sample_int(
                    moon_count_range_large if size_band == 'large' else moon_count_range_medium,
                    [0, 1] if size_band == 'medium' else [1, 2],
                )
                for _ in range(max(0, moon_count)):
                    moon_radius = radius * sample_float(moon_size_ratio_range, [0.1, 0.2])
                    moon_orbit = radius * sample_float(moon_orbit_scale_range, [2.2, 4.5])
                    moon_theta = rng.uniform(0.0, 2.0 * math.pi)
                    moon_x = x + (moon_orbit * math.cos(moon_theta))
                    moon_y = y + (moon_orbit * math.sin(moon_theta))
                    if in_draw_bounds(moon_x, moon_y):
                        add_circle(moon_x, moon_y, moon_radius, moon_color, moon_alpha, 0.099)

        planet_ratios = choose_orbit_ratios(target_planets, orbit_ratio_range, planet_orbit_gap_ratio)
        drawn_orbit_ratios: set[float] = set()
        planet_angles: list[float] = []
        generated_planets = 0
        for orbit_ratio in planet_ratios:
            shell = build_orbit_shell(orbit_ratio)
            orbit_key = round(orbit_ratio, 4)
            for _ in range(32):
                theta = rng.uniform(0.0, 2.0 * math.pi) + rng.uniform(-planet_angle_jitter_rad, planet_angle_jitter_rad)
                theta_norm = theta % (2.0 * math.pi)
                if planet_angles:
                    angle_gap = min(
                        min(abs(theta_norm - existing), (2.0 * math.pi) - abs(theta_norm - existing))
                        for existing in planet_angles
                    )
                    if angle_gap < ((2.0 * math.pi) / float(max(8, target_planets * 2))):
                        continue
                radius, size_band = classify_planet(orbit_ratio)
                visual_radius = radius if not (ring_enabled and size_band in {'medium', 'large'}) else radius * max(ring_diameter_scale_range)
                radial_scale = max(0.1, rng.uniform(orbit_jitter_low, orbit_jitter_high))
                planet_x, planet_y = orbit_point(shell, theta, radial_scale=radial_scale)
                if not in_draw_bounds(planet_x, planet_y):
                    continue
                if overlaps_occupied(planet_x, planet_y, visual_radius, pad=min_planet_sep * 0.25):
                    continue
                if orbit_key not in drawn_orbit_ratios:
                    draw_orbit_path(shell)
                    drawn_orbit_ratios.add(orbit_key)
                draw_planet(planet_x, planet_y, orbit_ratio)
                planet_angles.append(theta_norm)
                generated_planets += 1
                break

        secondary_count = sample_int(_cfg(major_star_cfg, 'secondary_count_range', [0, 2]), [0, 2])
        secondary_scale = _cfg(major_star_cfg, 'secondary_scale', [0.3, 0.5])
        secondary_min_sep = size * max(0.45, float(_cfg(major_star_cfg, 'secondary_min_separation_ratio', 0.55)))
        secondary_glow_scale = clamp(_cfg(major_star_cfg, 'secondary_glow_alpha_scale', 0.85), 0.0, 2.0, 0.85)
        secondary_core_scale = clamp(_cfg(major_star_cfg, 'secondary_core_alpha_scale', 0.85), 0.0, 2.0, 0.85)
        for _ in range(max(0, secondary_count)):
            scale = sample_float(secondary_scale, [0.3, 0.5])
            sec_radius = max(1.0, major_star_radius * scale)
            sec_visual_radius = sec_radius * major_star_glow_scale
            for _ in range(32):
                theta = rng.uniform(0.0, 2.0 * math.pi)
                distance = rng.uniform(secondary_min_sep, size * 1.1)
                sec_x = major_star_x + (distance * math.cos(theta))
                sec_y = major_star_y + (distance * math.sin(theta))
                if not in_draw_bounds(sec_x, sec_y) or not in_canvas_bounds(sec_x, sec_y, margin=sec_visual_radius):
                    continue
                if overlaps_occupied(sec_x, sec_y, sec_visual_radius, pad=size * 0.03):
                    continue
                add_circle(sec_x, sec_y, sec_visual_radius, major_star_color, major_star_glow_alpha * secondary_glow_scale, 0.064)
                add_circle(sec_x, sec_y, sec_radius, major_star_color, major_star_core_alpha * secondary_core_scale, 0.065)
                register_occupied(sec_x, sec_y, sec_visual_radius)
                break

        belt_ratios = choose_orbit_ratios(target_belts, belt_ratio_range, belt_gap_ratio * max(0.25, belt_belt_gap_scale))
        generated_belts = 0
        for orbit_ratio in belt_ratios:
            shell = build_orbit_shell(orbit_ratio)
            orbit_key = round(orbit_ratio, 4)
            span_deg = sample_float(belt_arc_span_deg, [20.0, 55.0])
            point_count = max(12, int(round(sample_float(belt_points_per_360, [120.0, 120.0]) * span_deg / 360.0)))
            thickness = sample_float(belt_thickness_ratio, [0.05, 0.12])
            curvature = sample_float(belt_curve_strength, [-0.06, 0.06])
            theta_start = rng.uniform(0.0, 2.0 * math.pi)
            span_rad = math.radians(span_deg)
            any_drawn = False
            for index in range(point_count):
                progress = index / float(max(1, point_count - 1))
                theta = theta_start + (progress * span_rad)
                radial_scale = max(0.05, 1.0 + rng.uniform(-thickness, thickness) + (curvature * math.sin(math.pi * (progress - 0.5))))
                belt_x, belt_y = orbit_point(shell, theta, radial_scale=radial_scale)
                if not in_draw_bounds(belt_x, belt_y):
                    continue
                radius = sample_float(belt_asteroid_radius, [0.1, 0.2])
                add_circle(belt_x, belt_y, radius, belt_color, belt_alpha, 0.09)
                any_drawn = True
            if any_drawn:
                if orbit_key not in drawn_orbit_ratios:
                    draw_orbit_path(shell)
                    drawn_orbit_ratios.add(orbit_key)
                generated_belts += 1

        return {
            'belts_generated': generated_belts,
            'belts_target': target_belts,
            'planets_generated': generated_planets,
            'planets_target': target_planets,
        }

    boundary_soft_effective = bool(boundary_enabled)
    boundary_hard_effective = bool(boundary_soft_effective and boundary_hard_enabled)

    background_gen_stats = draw_space_background(battle_ax, arena_size, random.Random(background_seed))
    print(
        f"[viz-bg] generated "
        f"belts={background_gen_stats['belts_generated']}/{background_gen_stats['belts_target']} "
        f"planets={background_gen_stats['planets_generated']}/{background_gen_stats['planets_target']}"
    )
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
    if boundary_hard_effective:
        curtain_color = str(_cfg(viz_settings, "boundary_outside_curtain_color", "#b8bcc2"))
        curtain_alpha = float(_cfg(viz_settings, "boundary_outside_curtain_alpha", 0.92))
        curtain_extent = arena_size * 4.0
        outside_curtain_rects = [
            Rectangle(
                (-curtain_extent, -curtain_extent),
                curtain_extent,
                arena_size + (2.0 * curtain_extent),
                facecolor=curtain_color,
                edgecolor="none",
                alpha=curtain_alpha,
                zorder=0.16,
            ),
            Rectangle(
                (arena_size, -curtain_extent),
                curtain_extent,
                arena_size + (2.0 * curtain_extent),
                facecolor=curtain_color,
                edgecolor="none",
                alpha=curtain_alpha,
                zorder=0.16,
            ),
            Rectangle(
                (0.0, -curtain_extent),
                arena_size,
                curtain_extent,
                facecolor=curtain_color,
                edgecolor="none",
                alpha=curtain_alpha,
                zorder=0.16,
            ),
            Rectangle(
                (0.0, arena_size),
                arena_size,
                curtain_extent,
                facecolor=curtain_color,
                edgecolor="none",
                alpha=curtain_alpha,
                zorder=0.16,
            ),
        ]
        for curtain_rect in outside_curtain_rects:
            battle_ax.add_patch(curtain_rect)

    def apply_grid_clip():
        if boundary_hard_effective:
            for grid_line in battle_ax.get_xgridlines():
                grid_line.set_clip_path(grid_clip_patch)
            for grid_line in battle_ax.get_ygridlines():
                grid_line.set_clip_path(grid_clip_patch)
        else:
            for grid_line in battle_ax.get_xgridlines():
                grid_line.set_clip_path(None)
            for grid_line in battle_ax.get_ygridlines():
                grid_line.set_clip_path(None)

    apply_grid_clip()
    boundary_line_width = 3.0 if boundary_soft_effective else 1.5
    boundary_edge_color = "#000000" if boundary_soft_effective else "#555555"
    boundary_linestyle = "-" if boundary_soft_effective else "--"
    battle_ax.add_patch(
        Rectangle(
            (0.0, 0.0),
            arena_size,
            arena_size,
            fill=False,
            edgecolor=boundary_edge_color,
            linewidth=boundary_line_width,
            linestyle=boundary_linestyle,
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
        if boundary_hard_effective:
            x_start = int(max(0.0, xlim[0]) // step) * step
            x_end = int(min(arena_size, xlim[1])) + step
            y_start = int(max(0.0, ylim[0]) // step) * step
            y_end = int(min(arena_size, ylim[1])) + step
        else:
            x_start = int(math.floor(float(xlim[0]) / step)) * step
            x_end = int(math.ceil(float(xlim[1]) / step)) * step + step
            y_start = int(math.floor(float(ylim[0]) / step)) * step
            y_end = int(math.ceil(float(ylim[1]) / step)) * step + step
        if (
            (not force)
            and tick_state["step"] == step
            and tick_state["x_start"] == x_start
            and tick_state["y_start"] == y_start
        ):
            ax.set_xlim(*xlim)
            ax.set_ylim(*ylim)
            apply_grid_clip()
            return
        ax.set_xticks(list(range(x_start, x_end, step)))
        ax.set_yticks(list(range(y_start, y_end, step)))
        # Matplotlib may expand view limits to include all ticks; restore the
        # requested camera window so grid refresh does not introduce a snap.
        ax.set_xlim(*xlim)
        ax.set_ylim(*ylim)
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
            "pivot": "middle",
        }

    quiver_style = build_quiver_style(quiver_geometry)
    vector_display_mode = unit_direction_mode
    radial_debug_neutral_band = 0.05
    radial_debug_len_ratio = 0.75
    radial_debug_inward_color = "#2ca02c"
    radial_debug_outward_color = "#d62728"
    radial_debug_neutral_color = "#ffbf00"
    auto_zoom_tick_interval = int(_cfg(auto_zoom_cfg, "tick_interval", 50))
    auto_zoom_start_delay_ticks = int(_cfg(auto_zoom_cfg, "start_delay_ticks", 50))
    auto_zoom_center_deadband = float(_cfg(auto_zoom_cfg, "center_deadband", 0.5))
    auto_zoom_min_factor = float(_cfg(auto_zoom_cfg, "min_factor", 4.0))
    auto_zoom_offscreen_trigger_ratio = float(_cfg(auto_zoom_cfg, "offscreen_trigger_ratio", 0.2))
    auto_zoom_centroid_trigger_ratio = float(_cfg(auto_zoom_cfg, "centroid_trigger_ratio", 0.3))
    auto_zoom_follow_out_of_bounds = bool(_cfg(auto_zoom_cfg, "follow_out_of_bounds", True))
    auto_zoom_transition_ms = int(_cfg(auto_zoom_cfg, "transition_ms", 1000))
    auto_zoom_zoomin_trigger_ratio = float(_cfg(auto_zoom_cfg, "zoomin_trigger_ratio", 0.8))
    auto_zoom_start_delay_ticks = max(0, auto_zoom_start_delay_ticks)
    auto_zoom_centroid_trigger_ratio = max(0.0, auto_zoom_centroid_trigger_ratio)
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

    quiver_capacity = 1

    def build_quiver_data(points_a, points_b, pad_to_count: int | None = None):
        merged = interleave_points(points_a, points_b)
        if merged:
            xs = [x for (x, _, _, _, _) in merged]
            ys = [y for (_, y, _, _, _) in merged]
            us = [ux * quiver_style["arrow_len"] for (_, _, ux, _, _) in merged]
            vs = [uy * quiver_style["arrow_len"] for (_, _, _, uy, _) in merged]
            colors = [c for (_, _, _, _, c) in merged]
        else:
            xs = []
            ys = []
            us = []
            vs = []
            colors = []
        target_count = int(pad_to_count) if pad_to_count is not None else len(xs)
        if target_count <= 0:
            target_count = max(1, len(xs))
        if len(xs) < target_count:
            pad_count = target_count - len(xs)
            xs.extend([float("nan")] * pad_count)
            ys.extend([float("nan")] * pad_count)
            us.extend([0.0] * pad_count)
            vs.extend([0.0] * pad_count)
            colors.extend([(0.0, 0.0, 0.0, 0.0)] * pad_count)
        offsets = list(zip(xs, ys))
        return xs, ys, us, vs, colors, offsets

    def make_quiver(points_a, points_b):
        xs, ys, us, vs, colors, _ = build_quiver_data(points_a, points_b, pad_to_count=quiver_capacity)
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

    avatar_dir = Path(__file__).resolve().parent.parent / "visual" / "avatars"

    def resolve_avatar_image(avatar_id: str):
        stem = str(avatar_id).strip() if avatar_id is not None else ""
        if not stem:
            return None
        suffixes = ("", ".bmp", ".png", ".jpg", ".jpeg", ".webp")
        candidates = [avatar_dir / stem] if "." in stem else [avatar_dir / f"{stem}{suffix}" for suffix in suffixes[1:]]
        for path in candidates:
            if path.exists():
                try:
                    return plt.imread(str(path))
                except Exception:
                    return None
        return None

    def build_grayscale_avatar_image(image):
        if image is None:
            return None
        src = np.asarray(image)
        if src.ndim < 2:
            return image
        if src.ndim == 2:
            return np.array(src, copy=True)
        if src.shape[2] < 3:
            return np.array(src, copy=True)
        gray = np.array(src, dtype=np.float32, copy=True)
        luminance = (
            (gray[..., 0] * 0.299)
            + (gray[..., 1] * 0.587)
            + (gray[..., 2] * 0.114)
        )
        gray[..., 0] = luminance
        gray[..., 1] = luminance
        gray[..., 2] = luminance
        if np.issubdtype(src.dtype, np.integer):
            dtype_info = np.iinfo(src.dtype)
            gray = np.clip(np.rint(gray), dtype_info.min, dtype_info.max).astype(src.dtype)
        else:
            gray = gray.astype(src.dtype, copy=False)
        return gray

    quiver_all = make_quiver([], [])
    target_line_collection = LineCollection(
        [],
        colors="#c40000",
        linewidths=0.3,
        alpha=0.8,
        zorder=6.0,  # keep below unit arrows (zorder=10)
    )
    target_line_collection.set_visible(bool(show_attack_target_lines))
    battle_ax.add_collection(target_line_collection)
    death_ring_collection = LineCollection(
        [],
        colors=death_ring_color,
        linewidths=death_ring_linewidth,
        alpha=death_ring_alpha,
        zorder=5.0,  # below unit arrows (zorder=10)
    )
    battle_ax.add_collection(death_ring_collection)
    legend_fontsize = battle_overlay_fontsize

    avatar_zoom = 0.75
    # Target the new small-avatar baseline (~80x100 @ zoom 0.75) so battlefield
    # avatars scale up from legacy size while still capping oversized source art.
    avatar_reference_height_px = 100.0
    full_name_fontsize = max(7, int(round(legend_fontsize)) - 1)
    avatar_inset = 0.012
    avatar_border_linewidth = 5.0

    def points_to_axes_fraction(points: float, axis: str) -> float:
        axes_pos = battle_ax.get_position()
        fig_width_in, fig_height_in = fig.get_size_inches()
        if axis == "x":
            axis_in = fig_width_in * axes_pos.width
        else:
            axis_in = fig_height_in * axes_pos.height
        if axis_in <= 1e-9:
            return 0.0
        return (points / 72.0) / axis_in

    def resolve_avatar_zoom(image) -> float:
        if image is None or not hasattr(image, "shape") or len(image.shape) < 2:
            return avatar_zoom
        img_h = float(image.shape[0])
        if img_h <= 1e-9:
            return avatar_zoom
        return avatar_zoom * (avatar_reference_height_px / img_h)

    def estimate_avatar_axes_size(image, zoom_value: float) -> tuple[float, float] | None:
        if image is None or not hasattr(image, "shape") or len(image.shape) < 2:
            return None
        axes_pos = battle_ax.get_position()
        fig_width_in, fig_height_in = fig.get_size_inches()
        ax_w_px = fig_width_in * fig.dpi * axes_pos.width
        ax_h_px = fig_height_in * fig.dpi * axes_pos.height
        if ax_w_px <= 1e-9 or ax_h_px <= 1e-9:
            return None
        img_h_px = float(image.shape[0]) * float(zoom_value)
        img_w_px = float(image.shape[1]) * float(zoom_value)
        return (img_w_px / ax_w_px, img_h_px / ax_h_px)

    avatar_specs = {
        "A": {
            "avatar": fleet_a_avatar,
            "color": fleet_a_color,
            "full_name": fleet_a_full_name,
            "anchor": (avatar_inset, avatar_inset),
            "alignment": (0.0, 0.0),
        },
        "B": {
            "avatar": fleet_b_avatar,
            "color": fleet_b_color,
            "full_name": fleet_b_full_name,
            "anchor": (1.0 - avatar_inset, 1.0 - avatar_inset),
            "alignment": (1.0, 1.0),
        },
    }
    avatar_images: dict[str, dict[str, Any]] = {}
    avatar_offset_images: dict[str, OffsetImage] = {}
    avatar_visual_state = {fleet_id: "color" for fleet_id in avatar_specs}
    avatar_heights = {"A": 0.105, "B": 0.105}
    for fleet_id, spec in avatar_specs.items():
        image = resolve_avatar_image(spec["avatar"])
        avatar_images[fleet_id] = {
            "color": image,
            "gray": build_grayscale_avatar_image(image),
        }
        zoom_value = resolve_avatar_zoom(image)
        size_axes = estimate_avatar_axes_size(image, zoom_value)
        if size_axes is not None:
            avatar_heights[fleet_id] = size_axes[1]
        if image is None:
            continue
        artist = OffsetImage(
            avatar_images[fleet_id]["color"],
            zoom=zoom_value,
            interpolation="lanczos",
            resample=True,
        )
        avatar_offset_images[fleet_id] = artist
        battle_ax.add_artist(
            AnnotationBbox(
                artist,
                spec["anchor"],
                xycoords="axes fraction",
                box_alignment=spec["alignment"],
                pad=0.0,
                frameon=True,
                bboxprops={
                    "edgecolor": spec["color"],
                    "linewidth": avatar_border_linewidth,
                    "facecolor": "none",
                    "boxstyle": "square,pad=0.0",
                },
                zorder=29.0,
            )
        )

    marker_side_points = max(8.0, float(full_name_fontsize) * 1.25)
    marker_w_axes = points_to_axes_fraction(marker_side_points, "x")
    marker_h_axes = points_to_axes_fraction(marker_side_points, "y")
    marker_gap_axes = points_to_axes_fraction(max(1.0, float(full_name_fontsize) * 0.2), "x")
    name_horizontal_tune_axes = points_to_axes_fraction(2.0, "x")
    label_touch_gap_axes = points_to_axes_fraction(1.0, "y")
    name_vertical_tune_axes = points_to_axes_fraction(16.0, "y")
    label_bbox = {
        "facecolor": "white",
        "alpha": 0.78,
        "edgecolor": "none",
        "boxstyle": "square,pad=0.16",
    }

    def set_defeated_avatar(defeated_fleet_id: str | None) -> None:
        for fleet_id, artist in avatar_offset_images.items():
            next_state = "gray" if defeated_fleet_id == fleet_id else "color"
            if avatar_visual_state[fleet_id] == next_state:
                continue
            artist.set_data(avatar_images[fleet_id][next_state])
            avatar_visual_state[fleet_id] = next_state

    label_specs = {
        "A": {
            "marker_x": avatar_inset - (0.2 * marker_w_axes),
            "marker_y": min(0.96, avatar_inset + avatar_heights["A"] + label_touch_gap_axes + name_vertical_tune_axes + marker_h_axes),
            "text_x": avatar_inset + (0.8 * marker_w_axes) + marker_gap_axes + name_horizontal_tune_axes,
            "text_y": min(0.96, avatar_inset + avatar_heights["A"] + label_touch_gap_axes + name_vertical_tune_axes + marker_h_axes),
            "va": "bottom",
            "ha": "left",
        },
        "B": {
            "marker_x": 1.0 - avatar_inset - (0.8 * marker_w_axes),
            "marker_y": max(0.04, 1.0 - avatar_inset - avatar_heights["B"] - label_touch_gap_axes - name_vertical_tune_axes - (2.0 * marker_h_axes)),
            "text_x": 1.0 - avatar_inset - (0.8 * marker_w_axes) - marker_gap_axes - name_horizontal_tune_axes,
            "text_y": max(0.04, 1.0 - avatar_inset - avatar_heights["B"] - label_touch_gap_axes - name_vertical_tune_axes - marker_h_axes),
            "va": "top",
            "ha": "right",
        },
    }
    for fleet_id, spec in label_specs.items():
        battle_ax.add_patch(
            Rectangle(
                (spec["marker_x"], spec["marker_y"]),
                marker_w_axes,
                marker_h_axes,
                transform=battle_ax.transAxes,
                facecolor=avatar_specs[fleet_id]["color"],
                edgecolor="none",
                zorder=30.0,
            )
        )
        battle_ax.text(
            spec["text_x"],
            spec["text_y"],
            f"{avatar_specs[fleet_id]['full_name']} ({fleet_id})",
            transform=battle_ax.transAxes,
            va=spec["va"],
            ha=spec["ha"],
            fontsize=full_name_fontsize,
            fontfamily="sans-serif",
            bbox=label_bbox,
            clip_on=True,
            zorder=30.0,
        )

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

    # Debug panel text layout is intentionally constrained:
    # - fixed 5-column archetype table width
    # - fixed max characters per row
    # This prevents right-edge overflow when debug rows are extended later.
    debug_param_col_count = 5
    debug_param_cell_width = 7
    debug_max_row_chars = 42

    debug_context = debug_context if isinstance(debug_context, Mapping) else {}
    combat_telemetry = combat_telemetry if isinstance(combat_telemetry, Mapping) else {}
    fixture_mode = str(_cfg(debug_context, "fixture_mode", "")).strip().lower()
    fixture_plot_mode = fixture_mode == "neutral_transit_v1"

    def format_runtime_diag_lines(
        tick_index: int,
        runtime_debug: Mapping[str, Any] | None,
    ) -> list[str]:
        if not plot_panel_enabled:
            return [
                "plot_panel: OFF",
                "baseline/extended plots hidden by profile rule",
            ]
        if not runtime_debug:
            return [
                "runtime_diag: n/a",
                "tip: debug data requires frame runtime_debug payload",
            ]
        mode_label = str(_cfg(debug_context, "test_mode_label", "n/a"))
        movement_label = str(_cfg(debug_context, "movement_model_effective", "n/a"))
        cohesion_label = str(_cfg(debug_context, "cohesion_decision_source_effective", "n/a"))
        odw_on = bool(_cfg(debug_context, "odw_posture_bias_enabled_effective", False))
        odw_k = float(_cfg(debug_context, "odw_posture_bias_k_effective", 0.0))
        odw_clip = float(_cfg(debug_context, "odw_posture_bias_clip_delta_effective", 0.0))
        v3_connect = float(_cfg(debug_context, "v3_connect_radius_multiplier_effective", 1.0))
        plot_smoothing = int(_cfg(debug_context, "plot_smoothing_ticks", 5))
        first_contact_tick = _cfg(debug_context, "first_contact_tick", "n/a")
        formation_cut_tick = _cfg(debug_context, "formation_cut_tick", "n/a")
        pocket_tick = _cfg(debug_context, "pocket_formation_tick", "n/a")
        selector_line = f"mode={mode_label} mov={movement_label} coh={cohesion_label}"
        odw_line = (
            f"odw={'on' if odw_on else 'off'} "
            f"k={odw_k:.2f} clip={odw_clip:.2f}"
        )
        collapse_line = f"csrc={cohesion_label}@{v3_connect:.2f} sm={plot_smoothing}"
        event_line = f"ct={first_contact_tick} cut={formation_cut_tick} pkt={pocket_tick}"
        return [
            selector_line,
            odw_line,
            collapse_line,
            event_line,
        ]

    def format_archetype_param_lines(fleet_id: str) -> list[str]:
        fleet_state = final_state.fleets.get(fleet_id) if isinstance(final_state.fleets, Mapping) else None
        params = getattr(fleet_state, "parameters", None)
        if params is None:
            return [f"{fleet_id}[n/a]"]
        archetype_id_raw = str(getattr(params, "archetype_id", "n/a"))
        archetype_id = archetype_id_raw if len(archetype_id_raw) <= 18 else f"{archetype_id_raw[:15]}..."
        specs = (
            ("fcr", "force_concentration_ratio"),
            ("mb", "mobility_bias"),
            ("odw", "offense_defense_weight"),
            ("ra", "risk_appetite"),
            ("tp", "time_preference"),
            ("tl", "targeting_logic"),
            ("fr", "formation_rigidity"),
            ("pr", "perception_radius"),
            ("pd", "pursuit_drive"),
            ("rt", "retreat_threshold"),
        )

        def format_cell(short_key: str, attr_name: str) -> str:
            value = getattr(params, attr_name, None)
            if isinstance(value, (int, float)):
                label = short_key.upper().ljust(3)
                return f"{label}:{float(value):.1f}"
            return f"{short_key.upper().ljust(3)}:n/a"

        cells = [format_cell(short_key, attr_name) for short_key, attr_name in specs]
        lines = [f"{fleet_id}[{archetype_id}]"]
        for idx in range(0, len(cells), debug_param_col_count):
            row = " ".join(
                cell.ljust(debug_param_cell_width)
                for cell in cells[idx:idx + debug_param_col_count]
            )
            lines.append(row)
        return lines

    archetype_param_lines = []
    archetype_param_lines.extend(format_archetype_param_lines("A"))
    archetype_param_lines.extend(format_archetype_param_lines("B"))

    def format_debug_text(
        mode: str,
        radial_outliers: int,
        tick_index: int,
        runtime_debug: Mapping[str, Any] | None,
    ) -> str:
        def clip_line(raw: str) -> str:
            if len(raw) <= debug_max_row_chars:
                return raw
            if debug_max_row_chars <= 1:
                return raw[:debug_max_row_chars]
            return raw[: debug_max_row_chars - 1] + "..."

        raw_lines = [*archetype_param_lines]
        if mode == "radial_debug":
            raw_lines.append(f"radial_outward_count: {radial_outliers}")
        raw_lines.extend([*format_runtime_diag_lines(tick_index, runtime_debug)])
        normalized_lines = [clip_line(raw) if raw else "" for raw in raw_lines]
        return "\n".join(normalized_lines)

    count_text = battle_ax.text(
        0.042,
        0.98,
        "",
        transform=battle_ax.transAxes,
        va="top",
        ha="left",
        fontsize=legend_fontsize,
        fontfamily="monospace",
        bbox={"facecolor": "white", "alpha": 0.7, "edgecolor": "none"},
    )
    count_text.set_zorder(31.0)
    count_marker_x = 0.010
    count_marker_top_y = 0.985
    count_marker_line_step = points_to_axes_fraction(float(legend_fontsize) * 1.20, "y")
    count_marker_line_center_offset = points_to_axes_fraction(float(legend_fontsize) * 0.54, "y")
    marker_side = points_to_axes_fraction(float(legend_fontsize) * 0.84, "y")
    marker_half = marker_side * 0.5
    count_marker_a_center_y = count_marker_top_y - count_marker_line_center_offset
    count_marker_b_center_y = count_marker_a_center_y - count_marker_line_step
    count_marker_a = Rectangle(
        (
            count_marker_x,
            count_marker_a_center_y - marker_half,
        ),
        marker_side,
        marker_side,
        transform=battle_ax.transAxes,
        facecolor=fleet_a_color,
        edgecolor="none",
        zorder=31.2,
    )
    count_marker_b = Rectangle(
        (
            count_marker_x,
            count_marker_b_center_y - marker_half,
        ),
        marker_side,
        marker_side,
        transform=battle_ax.transAxes,
        facecolor=fleet_b_color,
        edgecolor="none",
        zorder=31.2,
    )
    battle_ax.add_patch(count_marker_a)
    battle_ax.add_patch(count_marker_b)

    def format_battle_tick_text(tick_value: int) -> str:
        tick_int = int(tick_value)
        if tick_int < 0:
            tick_int = 0
        hh = tick_int // 60
        mm = tick_int % 60
        if display_language == "ZH":
            return f"{zh_standard_time_prefix}{hh:02d}:{mm:02d} (t={tick_int})"
        return f"ST {hh:02d}:{mm:02d} (t={tick_int})"

    tick_text_fontfamily = "sans-serif" if display_language == "ZH" else "monospace"
    battle_tick_text = battle_ax.text(
        0.98,
        0.02,
        "",
        transform=battle_ax.transAxes,
        va="bottom",
        ha="right",
        fontsize=legend_fontsize,
        fontfamily=tick_text_fontfamily,
        bbox={"facecolor": "white", "alpha": 0.7, "edgecolor": "none"},
    )
    battle_tick_text.set_zorder(30.0)
    debug_text_box = Rectangle(
        (0.01, 0.01),
        0.98,
        0.98,
        transform=debug_ax.transAxes,
        facecolor="#f7f7f7",
        edgecolor="#dddddd",
        linewidth=0.8,
        zorder=0.2,
    )
    debug_ax.add_patch(debug_text_box)
    debug_text = debug_ax.text(
        0.015,
        0.985,
        "",
        transform=debug_ax.transAxes,
        va="top",
        ha="left",
        fontsize=max(7, int(round(legend_fontsize)) - 2),
        family="monospace",
        linespacing=1.12,
        clip_on=True,
        zorder=0.3,
    )
    debug_text.set_text(format_debug_text(vector_display_mode, 0, 0, {}))
    count_text_cache = {"value": ""}
    debug_text_cache = {"value": debug_text.get_text()}
    tick_text_cache = {"value": ""}
    target_segments_empty = {"value": True}

    def build_target_geometry(
        frame_targets: Mapping[str, str],
        points_a_norm,
        points_b_norm,
    ) -> tuple[dict[str, tuple[float, float]], list[tuple[tuple[float, float], tuple[float, float]]]]:
        if not frame_targets:
            return {}, []
        point_map = {
            str(unit_id): (float(x), float(y))
            for unit_id, x, y, _, _, _, _ in [*points_a_norm, *points_b_norm]
        }
        direction_map: dict[str, tuple[float, float]] = {}
        segments: list[tuple[tuple[float, float], tuple[float, float]]] = []
        for attacker_id, defender_id in frame_targets.items():
            attacker = point_map.get(str(attacker_id))
            defender = point_map.get(str(defender_id))
            if attacker is None or defender is None:
                continue
            dx = defender[0] - attacker[0]
            dy = defender[1] - attacker[1]
            norm_sq = (dx * dx) + (dy * dy)
            if norm_sq <= 1e-12:
                continue
            if needs_attack_direction_map:
                norm = math.sqrt(norm_sq)
                direction_map[str(attacker_id)] = (dx / norm, dy / norm)
            if needs_target_segments:
                segments.append(((attacker[0], attacker[1]), (defender[0], defender[1])))
        return direction_map, segments

    prepared_frames = []
    for raw_frame in position_frames:
        runtime_debug = raw_frame.get("runtime_debug", {})
        if not isinstance(runtime_debug, Mapping):
            runtime_debug = {}
        raw_targets = raw_frame.get("targets", {})
        if not isinstance(raw_targets, Mapping):
            raw_targets = {}
        target_map = {str(attacker): str(defender) for attacker, defender in raw_targets.items()}
        points_a_norm = normalize_frame_points(raw_frame.get("A", []), "A")
        points_b_norm = normalize_frame_points(raw_frame.get("B", []), "B")
        alive_points_a = [(x, y, ox, oy) for _, x, y, ox, oy, _, _ in points_a_norm]
        alive_points_b = [(x, y, ox, oy) for _, x, y, ox, oy, _, _ in points_b_norm]
        attack_direction_map, target_segments = (
            build_target_geometry(target_map, points_a_norm, points_b_norm)
            if (needs_target_geometry and target_map)
            else ({}, [])
        )
        prepared_frames.append(
            {
                "tick": int(raw_frame.get("tick", 0)),
                "A_norm": points_a_norm,
                "B_norm": points_b_norm,
                "A_alive": alive_points_a,
                "B_alive": alive_points_b,
                "targets": target_map,
                "attack_direction_map": attack_direction_map,
                "target_segments": target_segments,
                "runtime_debug": runtime_debug,
            }
        )
        total_alive = len(points_a_norm) + len(points_b_norm)
        if total_alive > quiver_capacity:
            quiver_capacity = total_alive

    plot_label_fontsize = 9
    plot_tick_fontsize = 8
    plot_legend_fontsize = 7

    def _quantile_sorted(sorted_values: Sequence[float], q: float) -> float:
        if not sorted_values:
            return 0.0
        if len(sorted_values) == 1:
            return float(sorted_values[0])
        q = max(0.0, min(1.0, float(q)))
        pos = (len(sorted_values) - 1) * q
        lo = int(math.floor(pos))
        hi = int(math.ceil(pos))
        if lo == hi:
            return float(sorted_values[lo])
        w = pos - lo
        return float(sorted_values[lo]) * (1.0 - w) + float(sorted_values[hi]) * w

    def compute_axis_limits_many(
        *series_list: Sequence[float],
        q_low: float = 0.0,
        q_high: float = 1.0,
    ):
        combined = []
        for series in series_list:
            for value in series:
                fv = float(value)
                if math.isfinite(fv):
                    combined.append(fv)
        if not combined:
            return (0.0, 1.0)
        if 0.0 < q_low < q_high < 1.0 and len(combined) >= 8:
            sorted_vals = sorted(combined)
            y_min = _quantile_sorted(sorted_vals, q_low)
            y_max = _quantile_sorted(sorted_vals, q_high)
            if not math.isfinite(y_min) or not math.isfinite(y_max) or y_max <= y_min:
                y_min = min(combined)
                y_max = max(combined)
        else:
            y_min = min(combined)
            y_max = max(combined)
        if abs(y_max - y_min) < 1e-12:
            pad = max(1.0, abs(y_max) * 0.05)
            return (y_min - pad, y_max + pad)
        pad = (y_max - y_min) * 0.05
        return (y_min - pad, y_max + pad)

    def resolve_theta_collapse(fleet_id: str) -> float:
        fleet_state = final_state.fleets.get(fleet_id) if isinstance(final_state.fleets, Mapping) else None
        params = getattr(fleet_state, "parameters", None)
        if params is None:
            return 0.0
        normalized = params.normalized()
        if isinstance(normalized, Mapping):
            return float(normalized.get("pursuit_drive", 0.0))
        return 0.0

    theta_a = resolve_theta_collapse("A")
    theta_b = resolve_theta_collapse("B")

    collapse_margin_clip = True

    def collapse_margin(theta: float, enemy_cohesion: float) -> float:
        base = max(theta, 1e-12)
        value = (theta - enemy_cohesion) / base
        if collapse_margin_clip:
            value = min(1.0, max(-1.0, value))
        return value

    canonical_cohesion_series_a = [float(v) for v in trajectory.get("A", [])]
    canonical_cohesion_series_b = [float(v) for v in trajectory.get("B", [])]
    if extended_plot_mode and observer_runtime_cohesion_ready:
        cohesion_series_a = runtime_cohesion_a
        cohesion_series_b = runtime_cohesion_b
    else:
        cohesion_series_a = canonical_cohesion_series_a
        cohesion_series_b = canonical_cohesion_series_b

    def compute_loss_rate_series(
        alive_a: Sequence[float],
        alive_b: Sequence[float],
        window: int = 20,
    ) -> tuple[list[float], list[float]]:
        n = max(len(alive_a), len(alive_b))
        if n <= 0:
            return ([], [])
        out_a: list[float] = []
        out_b: list[float] = []
        last_a = float(alive_a[-1]) if alive_a else 0.0
        last_b = float(alive_b[-1]) if alive_b else 0.0
        for idx in range(n):
            curr_a = float(alive_a[idx]) if idx < len(alive_a) else last_a
            curr_b = float(alive_b[idx]) if idx < len(alive_b) else last_b
            tick = idx + 1
            w_eff = min(max(1, window), tick)
            prev_idx = idx - w_eff
            if prev_idx < 0:
                prev_idx = 0
            prev_a = float(alive_a[prev_idx]) if prev_idx < len(alive_a) else curr_a
            prev_b = float(alive_b[prev_idx]) if prev_idx < len(alive_b) else curr_b
            loss_rate_a = (prev_a - curr_a) / float(w_eff)
            loss_rate_b = (prev_b - curr_b) / float(w_eff)
            out_a.append(float(loss_rate_a))
            out_b.append(float(loss_rate_b))
        return (out_a, out_b)

    loss_rate_series_a, loss_rate_series_b = compute_loss_rate_series(
        [float(v) for v in alive_trajectory.get("A", [])],
        [float(v) for v in alive_trajectory.get("B", [])],
        window=20,
    )

    def compute_fire_efficiency_series(
        size_a: Sequence[float],
        size_b: Sequence[float],
        alive_a: Sequence[float],
        alive_b: Sequence[float],
        *,
        per_unit_damage: float,
    ) -> tuple[list[float], list[float]]:
        n = max(len(size_a), len(size_b), len(alive_a), len(alive_b))
        if n <= 0:
            return ([], [])
        out_a: list[float] = []
        out_b: list[float] = []
        last_size_a = float(size_a[-1]) if size_a else 0.0
        last_size_b = float(size_b[-1]) if size_b else 0.0
        last_alive_a = float(alive_a[-1]) if alive_a else 0.0
        last_alive_b = float(alive_b[-1]) if alive_b else 0.0
        damage_floor = max(0.0, float(per_unit_damage))
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
            out_a.append(max(0.0, min(1.0, float(eff_a))))
            out_b.append(max(0.0, min(1.0, float(eff_b))))
        return (out_a, out_b)

    fire_efficiency_series_a_raw, fire_efficiency_series_b_raw = compute_fire_efficiency_series(
        [float(v) for v in fleet_size_trajectory.get("A", [])],
        [float(v) for v in fleet_size_trajectory.get("B", [])],
        [float(v) for v in alive_trajectory.get("A", [])],
        [float(v) for v in alive_trajectory.get("B", [])],
        per_unit_damage=float(damage_per_tick),
    )

    collapse_margin_series_a = [
        collapse_margin(theta_a, cohesion_series_b[idx] if idx < len(cohesion_series_b) else 1.0)
        for idx in range(len(ticks))
    ]
    collapse_margin_series_b = [
        collapse_margin(theta_b, cohesion_series_a[idx] if idx < len(cohesion_series_a) else 1.0)
        for idx in range(len(ticks))
    ]
    front_curvature_series_a = extract_observer_series("front_curvature_index", "A", len(ticks))
    front_curvature_series_b = extract_observer_series("front_curvature_index", "B", len(ticks))
    center_wing_parallel_share_series_a = extract_observer_series("center_wing_parallel_share", "A", len(ticks))
    center_wing_parallel_share_series_b = extract_observer_series("center_wing_parallel_share", "B", len(ticks))
    hostile_intermix_severity_series = extract_global_observer_series("hostile_intermix_severity", len(ticks))
    hostile_intermix_coverage_series = extract_global_observer_series("hostile_intermix_coverage", len(ticks))

    def _ema_series(values: Sequence[float], span: int) -> list[float]:
        out: list[float] = []
        alpha = 2.0 / float(max(2, span) + 1)
        ema_value: float | None = None
        for value in values:
            fv = float(value)
            if not math.isfinite(fv):
                out.append(float("nan"))
                continue
            if ema_value is None or not math.isfinite(ema_value):
                ema_value = fv
            else:
                ema_value = (alpha * fv) + ((1.0 - alpha) * ema_value)
            out.append(float(ema_value))
        return out

    def _center_against_early_baseline(values: Sequence[float], baseline_count: int = 10) -> list[float]:
        baseline_values: list[float] = []
        for value in values:
            fv = float(value)
            if math.isfinite(fv):
                baseline_values.append(fv)
            if len(baseline_values) >= baseline_count:
                break
        if not baseline_values:
            return [float(v) for v in values]
        baseline = sum(baseline_values) / float(len(baseline_values))
        out: list[float] = []
        for value in values:
            fv = float(value)
            if math.isfinite(fv):
                out.append(float(fv - baseline))
            else:
                out.append(float("nan"))
        return out

    def _fill_nonfinite_with_zero(values: Sequence[float]) -> list[float]:
        out: list[float] = []
        for value in values:
            fv = float(value)
            out.append(fv if math.isfinite(fv) else 0.0)
        return out

    smoothing_span = max(1, int(plot_smoothing_ticks))

    def _smooth_plot_series(values: Sequence[float]) -> list[float]:
        if smoothing_span <= 1:
            return [float(v) if math.isfinite(float(v)) else float("nan") for v in values]
        return _ema_series(values, span=smoothing_span)

    front_curvature_plot_a = _smooth_plot_series(
        _fill_nonfinite_with_zero(_center_against_early_baseline(front_curvature_series_a, baseline_count=10))
    )
    front_curvature_plot_b = _smooth_plot_series(
        _fill_nonfinite_with_zero(_center_against_early_baseline(front_curvature_series_b, baseline_count=10))
    )
    center_wing_parallel_share_plot_a = _smooth_plot_series(
        _fill_nonfinite_with_zero(center_wing_parallel_share_series_a)
    )
    center_wing_parallel_share_plot_b = _smooth_plot_series(
        _fill_nonfinite_with_zero(center_wing_parallel_share_series_b)
    )
    hostile_intermix_severity_plot = _smooth_plot_series(
        _fill_nonfinite_with_zero(hostile_intermix_severity_series)
    )
    hostile_intermix_coverage_plot = _smooth_plot_series(
        _fill_nonfinite_with_zero(hostile_intermix_coverage_series)
    )
    fixture_objective_distance_plot = _smooth_plot_series(
        extract_fixture_series("centroid_to_objective_distance", len(ticks))
    )
    fixture_rms_radius_ratio_plot = _smooth_plot_series(
        extract_fixture_series("formation_rms_radius_ratio", len(ticks))
    )
    fixture_corrected_unit_ratio_plot = _smooth_plot_series(
        extract_fixture_series("corrected_unit_ratio", len(ticks))
    )
    fixture_projection_pairs_plot = _smooth_plot_series(
        extract_fixture_series("projection_pairs_count", len(ticks))
    )
    fixture_projection_mean_disp_plot = _smooth_plot_series(
        extract_fixture_series("projection_mean_displacement", len(ticks))
    )
    fixture_projection_max_disp_plot = _smooth_plot_series(
        extract_fixture_series("projection_max_displacement", len(ticks))
    )

    split_series_a = [float("nan")] * len(ticks)
    split_series_b = [float("nan")] * len(ticks)
    if plot_panel_enabled:
        split_source = bridge_telemetry if isinstance(bridge_telemetry, Mapping) else observer_telemetry
        if isinstance(split_source, Mapping):
            split_bucket = split_source.get("split_separation", {})
            if isinstance(split_bucket, Mapping):
                for side, series_out in (("A", split_series_a), ("B", split_series_b)):
                    raw = split_bucket.get(side, [])
                    if isinstance(raw, (list, tuple)):
                        for idx, value in enumerate(raw[: len(ticks)]):
                            try:
                                series_out[idx] = float(value)
                            except (TypeError, ValueError):
                                series_out[idx] = float("nan")

    runtime_series = {
        "split_a": _smooth_plot_series(split_series_a),
        "split_b": _smooth_plot_series(split_series_b),
        "fire_efficiency_a": _smooth_plot_series(fire_efficiency_series_a_raw),
        "fire_efficiency_b": _smooth_plot_series(fire_efficiency_series_b_raw),
        "loss_rate_a": _smooth_plot_series(loss_rate_series_a),
        "loss_rate_b": _smooth_plot_series(loss_rate_series_b),
        "collapse_margin_a": _smooth_plot_series(collapse_margin_series_a),
        "collapse_margin_b": _smooth_plot_series(collapse_margin_series_b),
        "front_curvature_a": front_curvature_plot_a,
        "front_curvature_b": front_curvature_plot_b,
        "hostile_intermix_severity": hostile_intermix_severity_plot,
        "hostile_intermix_coverage": hostile_intermix_coverage_plot,
        "center_wing_parallel_share_a": center_wing_parallel_share_plot_a,
        "center_wing_parallel_share_b": center_wing_parallel_share_plot_b,
    }

    if extended_plot_mode and observer_runtime_cohesion_ready:
        cohesion_axis_ylabel = "Coh_v3"
    else:
        cohesion_axis_ylabel = "Coh_v2"
    wedge_axis_ylabel = "ProjMean" if fixture_plot_mode else "IntermixCov"
    front_curvature_axis_ylabel = "ProjPairs" if fixture_plot_mode else "FrontCurv"
    center_wing_parallel_share_axis_ylabel = "ProjMax" if fixture_plot_mode else "C_W_PShare"
    split_axis_ylabel = "ProjCURatio" if fixture_plot_mode else "SplitSep"
    fire_efficiency_axis_ylabel = "FireEff"
    loss_rate_axis_ylabel = "RMSRad" if fixture_plot_mode else "LossRate"
    collapse_signal_axis_ylabel = "ObjDist" if fixture_plot_mode else "CollapseSig"

    def apply_time_axis_label(ax: plt.Axes) -> None:
        ax.set_xlabel("t", fontsize=plot_label_fontsize, labelpad=0.0)
        ax.xaxis.set_label_coords(1.015, -0.035)
        ax.xaxis.label.set_horizontalalignment("left")

    plot_legend_axes: list[plt.Axes] = []

    def apply_plot_legend(ax: plt.Axes) -> None:
        ax.legend(fontsize=plot_legend_fontsize, loc="best")
        plot_legend_axes.append(ax)

    def setup_side_plot(
        ax: plt.Axes,
        series_a: Sequence[float | int],
        series_b: Sequence[float | int],
        ylabel: str,
    ):
        line_a, = ax.plot(ticks, series_a, label="A", color=fleet_a_color)
        line_b, = ax.plot(ticks, series_b, label="B", color=fleet_b_color)
        apply_time_axis_label(ax)
        ax.set_ylabel(ylabel, fontsize=plot_label_fontsize)
        ax.tick_params(axis="both", which="major", labelsize=plot_tick_fontsize)
        apply_plot_legend(ax)
        return (line_a, line_b)

    def setup_single_plot(
        ax: plt.Axes,
        series: Sequence[float | int],
        ylabel: str,
        *,
        label: str,
        color: str,
    ):
        line_a, = ax.plot(ticks, series, label=label, color=color)
        line_b, = ax.plot([], [], label="_nolegend_", color=color)
        apply_time_axis_label(ax)
        ax.set_ylabel(ylabel, fontsize=plot_label_fontsize)
        ax.tick_params(axis="both", which="major", labelsize=plot_tick_fontsize)
        apply_plot_legend(ax)
        return (line_a, line_b)

    collapse_signal_series_a_raw = [
        (1.0 - float(cohesion_series_b[idx])) if idx < len(cohesion_series_b) and math.isfinite(float(cohesion_series_b[idx])) else float("nan")
        for idx in range(len(ticks))
    ]
    collapse_signal_series_b_raw = [
        (1.0 - float(cohesion_series_a[idx])) if idx < len(cohesion_series_a) and math.isfinite(float(cohesion_series_a[idx])) else float("nan")
        for idx in range(len(ticks))
    ]
    collapse_signal_series_a = _smooth_plot_series(collapse_signal_series_a_raw)
    collapse_signal_series_b = _smooth_plot_series(collapse_signal_series_b_raw)
    cohesion_plot_series_a = _smooth_plot_series(cohesion_series_a)
    cohesion_plot_series_b = _smooth_plot_series(cohesion_series_b)
    plot_lines: dict[str, tuple[Any, ...]] = {}
    for key, axis, series_a, series_b, ylabel in (
        ("alive", alive_ax, alive_trajectory["A"], alive_trajectory["B"], "Alive"),
        ("fire_efficiency", fire_efficiency_ax, runtime_series["fire_efficiency_a"], runtime_series["fire_efficiency_b"], fire_efficiency_axis_ylabel),
        ("cohesion", cohesion_ax, cohesion_plot_series_a, cohesion_plot_series_b, cohesion_axis_ylabel),
    ):
        plot_lines[key] = setup_side_plot(axis, series_a, series_b, ylabel)
    if not fixture_plot_mode:
        plot_lines["loss_rate"] = setup_side_plot(
            loss_rate_ax,
            runtime_series["loss_rate_a"],
            runtime_series["loss_rate_b"],
            loss_rate_axis_ylabel,
        )

    if fixture_plot_mode:
        plot_lines["loss_rate"] = setup_single_plot(
            loss_rate_ax,
            fixture_rms_radius_ratio_plot,
            loss_rate_axis_ylabel,
            label="RMS Ratio",
            color="#6c757d",
        )
        plot_lines["collapse_signal"] = setup_single_plot(
            collapse_signal_ax,
            fixture_objective_distance_plot,
            collapse_signal_axis_ylabel,
            label="Distance",
            color="#2d6a4f",
        )
        plot_lines["split"] = setup_single_plot(
            split_ax,
            fixture_corrected_unit_ratio_plot,
            split_axis_ylabel,
            label="Corrected Ratio",
            color="#4a4e69",
        )
        plot_lines["front_curvature"] = setup_single_plot(
            front_curvature_ax,
            fixture_projection_pairs_plot,
            front_curvature_axis_ylabel,
            label="Pairs",
            color="#1d3557",
        )
        plot_lines["wedge"] = setup_single_plot(
            wedge_ax,
            fixture_projection_mean_disp_plot,
            wedge_axis_ylabel,
            label="Mean Disp",
            color="#7f5539",
        )
        plot_lines["center_wing_parallel_share"] = setup_single_plot(
            center_wing_parallel_share_ax,
            fixture_projection_max_disp_plot,
            center_wing_parallel_share_axis_ylabel,
            label="Max Disp",
            color="#bc6c25",
        )
    else:
        for key, axis, series_a, series_b, ylabel in (
            ("collapse_signal", collapse_signal_ax, collapse_signal_series_a, collapse_signal_series_b, collapse_signal_axis_ylabel),
            ("split", split_ax, runtime_series["split_a"], runtime_series["split_b"], split_axis_ylabel),
            ("front_curvature", front_curvature_ax, runtime_series["front_curvature_a"], runtime_series["front_curvature_b"], front_curvature_axis_ylabel),
            (
                "center_wing_parallel_share",
                center_wing_parallel_share_ax,
                runtime_series["center_wing_parallel_share_a"],
                runtime_series["center_wing_parallel_share_b"],
                center_wing_parallel_share_axis_ylabel,
            ),
        ):
            plot_lines[key] = setup_side_plot(axis, series_a, series_b, ylabel)

        wedge_line_a, = wedge_ax.plot(
            ticks,
            runtime_series["hostile_intermix_coverage"],
            label="Coverage",
            color="#333333",
        )
        wedge_line_b, = wedge_ax.plot([], [], label="_nolegend_", color="#333333")
        apply_time_axis_label(wedge_ax)
        wedge_ax.set_ylabel(wedge_axis_ylabel, fontsize=plot_label_fontsize)
        wedge_ax.tick_params(axis="both", which="major", labelsize=plot_tick_fontsize)
        apply_plot_legend(wedge_ax)
        plot_lines["wedge"] = (wedge_line_a, wedge_line_b)

    observer_series_lines = [
        line
        for key in (
            "fire_efficiency",
            "wedge",
            "center_wing_parallel_share",
            "split",
            "loss_rate",
            "cohesion",
            "collapse_signal",
            "front_curvature",
        )
        for line in plot_lines[key]
        if line.get_label() != "_nolegend_"
    ]

    def apply_observer_axis_disabled_style(ax, slot_name: str) -> None:
        ax.set_facecolor("#f8f8f8")
        ax.set_xticks([])
        ax.set_yticks([])
        ax.grid(False)
        ax.set_xlabel("")
        ax.set_ylabel("")
        ax.set_title("")
        for spine in ax.spines.values():
            spine.set_visible(False)
        legend = ax.get_legend()
        if legend is not None:
            legend.remove()
        ax.text(
            0.5,
            0.5,
            f"{slot_name}\nobserver diagnostics hidden",
            transform=ax.transAxes,
            ha="center",
            va="center",
            fontsize=8,
            color="#666666",
        )

    # Plot profile rule:
    # - baseline/extended: keep plot slots visible
    # - any future off profile: hide diagnostic slots
    if not plot_panel_enabled:
        for line in observer_series_lines:
            line.set_visible(False)
        for ax_local, slot_name in (
            (fire_efficiency_ax, "slot_03"),
            (loss_rate_ax, "slot_04"),
            (cohesion_ax, "slot_05"),
            (collapse_signal_ax, "slot_06"),
            (split_ax, "slot_07"),
            (front_curvature_ax, "slot_08"),
            (wedge_ax, "slot_09"),
            (center_wing_parallel_share_ax, "slot_10"),
        ):
            apply_observer_axis_disabled_style(ax_local, slot_name)

    def freeze_plot_legends() -> None:
        active_axes = [ax for ax in plot_legend_axes if ax.get_legend() is not None]
        if not active_axes:
            return
        try:
            fig.canvas.draw()
            renderer = fig.canvas.get_renderer()
        except Exception:
            return
        for ax in active_axes:
            legend = ax.get_legend()
            if legend is None:
                continue
            try:
                bbox_axes = legend.get_window_extent(renderer=renderer).transformed(ax.transAxes.inverted())
                handles, labels = ax.get_legend_handles_labels()
                legend.remove()
                ax.legend(
                    handles,
                    labels,
                    fontsize=plot_legend_fontsize,
                    loc="upper left",
                    bbox_to_anchor=(float(bbox_axes.x0), float(bbox_axes.y1)),
                    bbox_transform=ax.transAxes,
                    borderaxespad=0.0,
                )
            except Exception:
                continue

    x_limit_right = max(1, len(ticks) - 1)
    for ax in (
        alive_ax,
        fire_efficiency_ax,
        loss_rate_ax,
        cohesion_ax,
        collapse_signal_ax,
        split_ax,
        front_curvature_ax,
        wedge_ax,
        center_wing_parallel_share_ax,
    ):
        ax.set_xlim(0.0, float(x_limit_right))

    alive_ax.set_ylim(*compute_axis_limits_many(alive_trajectory["A"], alive_trajectory["B"]))
    fire_efficiency_ax.set_ylim(0.0, 1.0)
    if fixture_plot_mode:
        loss_rate_ax.set_ylim(*compute_axis_limits_many(fixture_rms_radius_ratio_plot))
    else:
        loss_rate_ax.set_ylim(*compute_axis_limits_many(runtime_series["loss_rate_a"], runtime_series["loss_rate_b"]))
    cohesion_ax.set_ylim(*compute_axis_limits_many(cohesion_series_a, cohesion_series_b))
    if fixture_plot_mode:
        collapse_signal_ax.set_ylim(*compute_axis_limits_many(fixture_objective_distance_plot))
        split_ax.set_ylim(0.0, 1.0)
        front_curvature_ax.set_ylim(*compute_axis_limits_many(fixture_projection_pairs_plot))
        wedge_ax.set_ylim(*compute_axis_limits_many(fixture_projection_mean_disp_plot))
        center_wing_parallel_share_ax.set_ylim(*compute_axis_limits_many(fixture_projection_max_disp_plot))
    else:
        collapse_signal_ax.set_ylim(*compute_axis_limits_many(collapse_signal_series_a, collapse_signal_series_b))
        split_ax.set_ylim(1.5, 2.5)
        front_curvature_ax.set_ylim(*compute_axis_limits_many(runtime_series["front_curvature_a"], runtime_series["front_curvature_b"]))
        # IntermixCoverage is a prototype-grade diagnostic for broad hostile overlap.
        # Keep the full fraction range so different fixtures remain directly comparable.
        wedge_ax.set_ylim(0.0, 1.0)
        center_wing_parallel_share_ax.set_ylim(-1.0, 1.0)

    # Freeze plot labels only after final axis limits are in place so the
    # legend anchor reflects the actual rendered curve geometry.
    freeze_plot_legends()

    tick_cursor_style = {
        "color": "#4a4a4a",
        "linestyle": ":",
        "linewidth": 0.9,
        "alpha": 0.85,
        "zorder": 2.6,
    }
    initial_cursor_x = 0.0
    tick_cursor_lines = [
        alive_ax.axvline(initial_cursor_x, **tick_cursor_style),
        fire_efficiency_ax.axvline(initial_cursor_x, **tick_cursor_style),
        loss_rate_ax.axvline(initial_cursor_x, **tick_cursor_style),
        cohesion_ax.axvline(initial_cursor_x, **tick_cursor_style),
        collapse_signal_ax.axvline(initial_cursor_x, **tick_cursor_style),
        split_ax.axvline(initial_cursor_x, **tick_cursor_style),
        front_curvature_ax.axvline(initial_cursor_x, **tick_cursor_style),
        wedge_ax.axvline(initial_cursor_x, **tick_cursor_style),
        center_wing_parallel_share_ax.axvline(initial_cursor_x, **tick_cursor_style),
    ]
    if not plot_panel_enabled:
        for line in tick_cursor_lines[1:]:
            line.set_visible(False)

    tick_plot_lines = [
        (plot_lines["alive"][0], alive_trajectory["A"]),
        (plot_lines["alive"][1], alive_trajectory["B"]),
        (plot_lines["fire_efficiency"][0], runtime_series["fire_efficiency_a"]),
        (plot_lines["fire_efficiency"][1], runtime_series["fire_efficiency_b"]),
        (
            plot_lines["loss_rate"][0],
            fixture_rms_radius_ratio_plot if fixture_plot_mode else runtime_series["loss_rate_a"],
        ),
        (
            plot_lines["loss_rate"][1],
            [] if fixture_plot_mode else runtime_series["loss_rate_b"],
        ),
        (plot_lines["cohesion"][0], cohesion_series_a),
        (plot_lines["cohesion"][1], cohesion_series_b),
        (
            plot_lines["collapse_signal"][0],
            fixture_objective_distance_plot if fixture_plot_mode else collapse_signal_series_a,
        ),
        (
            plot_lines["collapse_signal"][1],
            [] if fixture_plot_mode else collapse_signal_series_b,
        ),
        (
            plot_lines["split"][0],
            fixture_corrected_unit_ratio_plot if fixture_plot_mode else runtime_series["split_a"],
        ),
        (
            plot_lines["split"][1],
            [] if fixture_plot_mode else runtime_series["split_b"],
        ),
        (
            plot_lines["front_curvature"][0],
            fixture_projection_pairs_plot if fixture_plot_mode else runtime_series["front_curvature_a"],
        ),
        (
            plot_lines["front_curvature"][1],
            [] if fixture_plot_mode else runtime_series["front_curvature_b"],
        ),
        (
            plot_lines["wedge"][0],
            fixture_projection_mean_disp_plot if fixture_plot_mode else runtime_series["hostile_intermix_coverage"],
        ),
        (
            plot_lines["center_wing_parallel_share"][0],
            fixture_projection_max_disp_plot if fixture_plot_mode else runtime_series["center_wing_parallel_share_a"],
        ),
        (
            plot_lines["center_wing_parallel_share"][1],
            [] if fixture_plot_mode else runtime_series["center_wing_parallel_share_b"],
        ),
    ]

    tick_plots_follow_enabled = bool(tick_plots_follow_battlefield_tick and len(prepared_frames) > 0)
    last_reveal_count = {"value": 0}
    if tick_plots_follow_enabled:
        for line, _ in tick_plot_lines:
            line.set_data([], [])
    # L2 fast path: blit only when side plots are static and camera does not auto-pan/zoom.
    blit_enabled = bool((not tick_plots_follow_enabled) and (not auto_zoom_2d))
    quiver_all.set_animated(blit_enabled)
    target_line_collection.set_animated(blit_enabled)
    death_ring_collection.set_animated(blit_enabled)
    count_text.set_animated(blit_enabled)
    debug_text.set_animated(blit_enabled)
    battle_tick_text.set_animated(blit_enabled)
    for line in tick_cursor_lines:
        line.set_animated(blit_enabled)
    avatar_animated_artists = tuple(avatar_offset_images.values())
    for artist in avatar_animated_artists:
        artist.set_animated(blit_enabled)

    if prepared_frames:
        first_tick = prepared_frames[0]["tick"]
        auto_zoom_transition_frames = max(1, int(round(auto_zoom_transition_ms / frame_interval_ms)))
        auto_zoom_initialized = {"value": False}
        battle_end_full_view_locked = {"value": False}
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
            "pending_tick_xlim": None,
            "pending_tick_ylim": None,
        }

        def resolve_zoom_transition_frames(start_half: float, target_half: float) -> int:
            min_half = min(start_half, target_half)
            max_half = max(start_half, target_half)
            if min_half <= 1e-9:
                return auto_zoom_transition_frames
            zoom_ratio = max_half / min_half
            if zoom_ratio <= 2.0:
                zoom_time_scale = 1.0
            else:
                # Anchor rules:
                # 2x <-> 1x => 1.0x base duration
                # 4x <-> 2x => 1.0x base duration
                # 4x <-> 1x => 4/3 base duration (1.5x faster than the prior 2.0x scale)
                octave_span = math.log2(zoom_ratio)
                zoom_time_scale = 1.0 + max(0.0, octave_span - 1.0) / 3.0
            return max(
                auto_zoom_transition_frames,
                int(round(auto_zoom_transition_frames * zoom_time_scale)),
            )

        death_linger = {"A": {}, "B": {}}
        last_alive_by_fleet = {"A": {}, "B": {}}
        last_positions_for_effective = {"A": {}, "B": {}}
        death_ring_signature = {"value": None}
        death_ring_resolution = 20
        death_ring_template = [
            (
                math.cos((2.0 * math.pi * idx) / death_ring_resolution),
                math.sin((2.0 * math.pi * idx) / death_ring_resolution),
            )
            for idx in range(death_ring_resolution + 1)
        ]

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

        def build_render_points_for_mode(
            points_norm,
            fleet_id: str,
            attack_direction_map: Mapping[str, tuple[float, float]] | None = None,
            commit_positions: bool = True,
        ):
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
            attack_direction_map = attack_direction_map or {}

            def resolve_effective_direction(
                unit_id_local: str,
                x_local: float,
                y_local: float,
                ox_local: float,
                oy_local: float,
            ) -> tuple[float, float]:
                prev = prev_positions.get(unit_id_local)
                if prev is None:
                    raw_x = ox_local
                    raw_y = oy_local
                else:
                    raw_x = x_local - prev[0]
                    raw_y = y_local - prev[1]
                raw_norm = math.sqrt((raw_x * raw_x) + (raw_y * raw_y))
                if raw_norm > vector_eps:
                    return (raw_x / raw_norm, raw_y / raw_norm)
                return (0.0, 0.0)

            def resolve_free_direction(vx_local: float, vy_local: float) -> tuple[float, float]:
                raw_norm = math.sqrt((vx_local * vx_local) + (vy_local * vy_local))
                if raw_norm > vector_eps:
                    return (vx_local / raw_norm, vy_local / raw_norm)
                return (0.0, 0.0)

            for unit_id, x, y, ox, oy, vx, vy in points_norm:
                next_positions[unit_id] = (x, y)
                if vector_display_mode == "radial_debug":
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
                elif unit_direction_mode == "effective":
                    ux, uy = resolve_effective_direction(unit_id, x, y, ox, oy)
                    color = base_color
                elif unit_direction_mode == "free":
                    ux, uy = resolve_free_direction(vx, vy)
                    color = base_color
                elif unit_direction_mode == "attack":
                    attack_vec = attack_direction_map.get(unit_id)
                    if attack_vec is not None:
                        ux = float(attack_vec[0])
                        uy = float(attack_vec[1])
                    else:
                        ux, uy = resolve_effective_direction(unit_id, x, y, ox, oy)
                    color = base_color
                else:
                    attack_vec = attack_direction_map.get(unit_id)
                    eff_x, eff_y = resolve_effective_direction(unit_id, x, y, ox, oy)
                    if attack_vec is None:
                        ux, uy = eff_x, eff_y
                    else:
                        comp_x = float(attack_vec[0]) + eff_x
                        comp_y = float(attack_vec[1]) + eff_y
                        comp_norm = math.sqrt((comp_x * comp_x) + (comp_y * comp_y))
                        if comp_norm > vector_eps:
                            ux = comp_x / comp_norm
                            uy = comp_y / comp_norm
                        else:
                            ux, uy = eff_x, eff_y
                    color = base_color
                render_points.append((x, y, ux, uy, color))
            if commit_positions:
                last_positions_for_effective[fleet_id] = next_positions
            return render_points, radial_outward_count

        # Pre-render first frame so units are arrows at initialization (no first-frame dots).
        initial_points_a_norm = prepared_frames[0]["A_norm"]
        initial_points_b_norm = prepared_frames[0]["B_norm"]
        initial_attack_direction_map = prepared_frames[0]["attack_direction_map"]
        initial_render_points_a, initial_radial_outward_a = build_render_points_for_mode(
            initial_points_a_norm,
            "A",
            attack_direction_map=initial_attack_direction_map,
            commit_positions=False,
        )
        initial_render_points_b, initial_radial_outward_b = build_render_points_for_mode(
            initial_points_b_norm,
            "B",
            attack_direction_map=initial_attack_direction_map,
            commit_positions=False,
        )
        quiver_all.remove()
        quiver_all = make_quiver(initial_render_points_a, initial_render_points_b)
        quiver_all.set_animated(blit_enabled)

        def prime_first_frame_overlays() -> None:
            first_frame = prepared_frames[0]
            first_tick_value = int(first_frame["tick"])
            first_tick_index = max(0, first_tick_value - 1)
            a_series_local = fleet_size_trajectory.get("A", [])
            b_series_local = fleet_size_trajectory.get("B", [])
            if a_series_local:
                curr_size_a_local = float(a_series_local[min(first_tick_index, len(a_series_local) - 1)])
            else:
                curr_size_a_local = 0.0
            if b_series_local:
                curr_size_b_local = float(b_series_local[min(first_tick_index, len(b_series_local) - 1)])
            else:
                curr_size_b_local = 0.0
            pct_a_local = (curr_size_a_local / initial_size_a * 100.0) if initial_size_a > 0.0 else 0.0
            pct_b_local = (curr_size_b_local / initial_size_b * 100.0) if initial_size_b > 0.0 else 0.0
            first_tick_text = format_battle_tick_text(first_tick_value)
            battle_tick_text.set_text(first_tick_text)
            tick_text_cache["value"] = first_tick_text
            if vector_display_mode == "radial_debug":
                first_mode_outliers = initial_radial_outward_a + initial_radial_outward_b
            else:
                first_mode_outliers = 0
            first_debug_text = format_debug_text(
                vector_display_mode,
                first_mode_outliers,
                first_tick_index,
                first_frame["runtime_debug"],
            )
            debug_text.set_text(first_debug_text)
            debug_text_cache["value"] = first_debug_text
            first_count_text = format_count_text(
                len(first_frame["A_alive"]),
                len(first_frame["B_alive"]),
                curr_size_a_local,
                curr_size_b_local,
                pct_a_local,
                pct_b_local,
            )
            count_text.set_text(first_count_text)
            count_text_cache["value"] = first_count_text
            if show_attack_target_lines:
                first_segments = first_frame["target_segments"]
                target_line_collection.set_segments(first_segments)
                target_segments_empty["value"] = len(first_segments) == 0
            cursor_x_local = float(min(max(first_tick_value - 1, 0), x_limit_right))
            for line in tick_cursor_lines:
                line.set_xdata([cursor_x_local, cursor_x_local])
            if tick_plots_follow_enabled:
                reveal_count_local = min(max(first_tick_value, 0), len(ticks))
                reveal_x_local = ticks[:reveal_count_local]
                for line, series in tick_plot_lines:
                    line.set_data(reveal_x_local, series[:reveal_count_local])
                last_reveal_count["value"] = reveal_count_local

        prime_first_frame_overlays()

        def reset_to_full_view(clear_effective_cache: bool = True):
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
            auto_zoom_state["pending_tick_xlim"] = None
            auto_zoom_state["pending_tick_ylim"] = None
            if clear_effective_cache:
                last_positions_for_effective["A"] = {}
                last_positions_for_effective["B"] = {}
            battle_ax.set_xlim(0.0, arena_size)
            battle_ax.set_ylim(0.0, arena_size)
            apply_adaptive_ticks(battle_ax, (0.0, arena_size), (0.0, arena_size), force=True)

        def full_view_target() -> tuple[float, float, float]:
            return (arena_size * 0.5, arena_size * 0.5, arena_size * 0.5)

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
            half_4x = arena_size / (2.0 * auto_zoom_min_factor)
            # Use a continuous zoom target between 1x and max zoom so 1x <-> 4x
            # can complete in one natural transition instead of stepping through 2x.
            half = min(max(farthest_half + 1.0, half_4x), half_1x)
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
            start_half = auto_zoom_state["current_half"]
            auto_zoom_state["start_x"] = auto_zoom_state["current_x"]
            auto_zoom_state["start_y"] = auto_zoom_state["current_y"]
            auto_zoom_state["start_half"] = start_half
            auto_zoom_state["target_x"] = cx
            auto_zoom_state["target_y"] = cy
            auto_zoom_state["target_half"] = ch if mode == "zoom" else auto_zoom_state["current_half"]
            auto_zoom_state["transition_mode"] = mode
            transition_frames = auto_zoom_transition_frames
            if mode == "zoom":
                transition_frames = resolve_zoom_transition_frames(
                    start_half,
                    auto_zoom_state["target_half"],
                )
            auto_zoom_state["transition_total_frames"] = transition_frames
            auto_zoom_state["transition_remaining_frames"] = transition_frames
            target_half_for_ticks = auto_zoom_state["target_half"]
            target_xlim = (cx - target_half_for_ticks, cx + target_half_for_ticks)
            target_ylim = (cy - target_half_for_ticks, cy + target_half_for_ticks)
            auto_zoom_state["pending_tick_xlim"] = target_xlim
            auto_zoom_state["pending_tick_ylim"] = target_ylim

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
            pending_tick_xlim = auto_zoom_state["pending_tick_xlim"]
            pending_tick_ylim = auto_zoom_state["pending_tick_ylim"]
            transition_complete = (
                auto_zoom_state["transition_remaining_frames"] <= 0
                and abs(cx - tx) <= lim_eps
                and abs(cy - ty) <= lim_eps
                and abs(ch - th) <= lim_eps
            )
            if transition_complete and pending_tick_xlim is not None and pending_tick_ylim is not None:
                apply_adaptive_ticks(battle_ax, pending_tick_xlim, pending_tick_ylim)
                auto_zoom_state["pending_tick_xlim"] = None
                auto_zoom_state["pending_tick_ylim"] = None

        def update_quiver(points_a, points_b):
            _, _, us, vs, colors, offsets = build_quiver_data(points_a, points_b, pad_to_count=quiver_capacity)
            quiver_all.set_offsets(offsets)
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

        def update_death_ring_collection():
            current_signature = []
            for fleet_id in ("A", "B"):
                for unit_id in sorted(death_linger[fleet_id].keys()):
                    x, y, _, _, _ = death_linger[fleet_id][unit_id]
                    current_signature.append((fleet_id, unit_id, round(float(x), 6), round(float(y), 6)))
            signature_tuple = tuple(current_signature)
            if signature_tuple == death_ring_signature["value"]:
                return
            death_ring_signature["value"] = signature_tuple
            segments = []
            for fleet_id in ("A", "B"):
                for unit_id in sorted(death_linger[fleet_id].keys()):
                    x, y, _, _, _ = death_linger[fleet_id][unit_id]
                    segments.append(
                        [
                            (
                                x + (death_ring_radius * px),
                                y + (death_ring_radius * py),
                            )
                            for px, py in death_ring_template
                        ]
                    )
            death_ring_collection.set_segments(segments)

        def update_frame(frame):
            alive_points_a_norm = frame["A_norm"]
            alive_points_b_norm = frame["B_norm"]
            alive_points_a = frame["A_alive"]
            alive_points_b = frame["B_alive"]
            defeated_fleet_id = None
            if (len(alive_points_a) == 0) and (len(alive_points_b) > 0):
                defeated_fleet_id = "A"
            elif (len(alive_points_b) == 0) and (len(alive_points_a) > 0):
                defeated_fleet_id = "B"
            set_defeated_avatar(defeated_fleet_id)
            attack_direction_map = frame["attack_direction_map"] if needs_attack_direction_map else {}
            render_points_a, radial_outward_a = build_render_points_for_mode(
                alive_points_a_norm,
                "A",
                attack_direction_map=attack_direction_map,
            )
            render_points_b, radial_outward_b = build_render_points_for_mode(
                alive_points_b_norm,
                "B",
                attack_direction_map=attack_direction_map,
            )

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
            if show_attack_target_lines:
                target_segments = frame["target_segments"]
                is_empty = len(target_segments) == 0
                if (not is_empty) or (not target_segments_empty["value"]):
                    target_line_collection.set_segments(target_segments)
                target_segments_empty["value"] = is_empty
            else:
                if not target_segments_empty["value"]:
                    target_line_collection.set_segments([])
                    target_segments_empty["value"] = True
            update_death_ring_collection()
            if auto_zoom_2d:
                frame_tick_value = int(frame["tick"])
                if frame_tick_value == first_tick:
                    reset_to_full_view()
                    auto_zoom_initialized["value"] = False
                    battle_end_full_view_locked["value"] = False
                if frame_tick_value < auto_zoom_start_delay_ticks:
                    reset_to_full_view(clear_effective_cache=False)
                    auto_zoom_initialized["value"] = False
                    battle_end_full_view_locked["value"] = False
                    apply_auto_zoom_step()
                else:
                    battle_resolved = (len(alive_points_a) == 0) or (len(alive_points_b) == 0)
                    if battle_resolved:
                        if not battle_end_full_view_locked["value"]:
                            begin_camera_transition(full_view_target(), mode="zoom")
                            battle_end_full_view_locked["value"] = True
                        apply_auto_zoom_step()
                    else:
                        battle_end_full_view_locked["value"] = False
                        if frame_tick_value % auto_zoom_tick_interval == 0:
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
            next_tick_text = format_battle_tick_text(int(frame["tick"]))
            if next_tick_text != tick_text_cache["value"]:
                battle_tick_text.set_text(next_tick_text)
                tick_text_cache["value"] = next_tick_text
            if vector_display_mode == "radial_debug":
                mode_outliers = radial_outward_a + radial_outward_b
            else:
                mode_outliers = 0
            runtime_debug = frame["runtime_debug"]
            next_debug_text = format_debug_text(
                vector_display_mode,
                mode_outliers,
                tick_index,
                runtime_debug,
            )
            if next_debug_text != debug_text_cache["value"]:
                debug_text.set_text(next_debug_text)
                debug_text_cache["value"] = next_debug_text
            next_count_text = format_count_text(len(alive_points_a), len(alive_points_b), curr_size_a, curr_size_b, pct_a, pct_b)
            if next_count_text != count_text_cache["value"]:
                count_text.set_text(next_count_text)
                count_text_cache["value"] = next_count_text
            if tick_plots_follow_enabled:
                frame_tick = int(frame["tick"])
                reveal_count = min(max(frame_tick, 0), len(ticks))
                if reveal_count != last_reveal_count["value"]:
                    reveal_x = ticks[:reveal_count]
                    for line, series in tick_plot_lines:
                        line.set_data(reveal_x, series[:reveal_count])
                    last_reveal_count["value"] = reveal_count
            cursor_x = float(min(max(int(frame["tick"]) - 1, 0), x_limit_right))
            for line in tick_cursor_lines:
                line.set_xdata([cursor_x, cursor_x])
            if blit_enabled:
                return (
                    quiver_all,
                    target_line_collection,
                    death_ring_collection,
                    count_text,
                    debug_text,
                    battle_tick_text,
                    *tick_cursor_lines,
                    *avatar_animated_artists,
                )
            return ()

        def init_frame():
            return (
                quiver_all,
                target_line_collection,
                death_ring_collection,
                count_text,
                debug_text,
                battle_tick_text,
                *tick_cursor_lines,
                *avatar_animated_artists,
            )

        anim = FuncAnimation(
            fig,
            update_frame,
            frames=prepared_frames,
            interval=frame_interval_ms,
            blit=blit_enabled,
            repeat=True,
            init_func=init_frame if blit_enabled else None,
            cache_frame_data=False,
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
        target_line_collection.set_segments([])
        death_ring_collection.set_segments([])
        curr_size_a = 0.0
        curr_size_b = 0.0
        if fleet_size_trajectory.get("A"):
            curr_size_a = float(fleet_size_trajectory["A"][-1])
        if fleet_size_trajectory.get("B"):
            curr_size_b = float(fleet_size_trajectory["B"][-1])
        pct_a = (curr_size_a / initial_size_a * 100.0) if initial_size_a > 0.0 else 0.0
        pct_b = (curr_size_b / initial_size_b * 100.0) if initial_size_b > 0.0 else 0.0
        defeated_fleet_id = None
        if (len(final_a) == 0) and (len(final_b) > 0):
            defeated_fleet_id = "A"
        elif (len(final_b) == 0) and (len(final_a) > 0):
            defeated_fleet_id = "B"
        set_defeated_avatar(defeated_fleet_id)
        debug_text.set_text(format_debug_text(vector_display_mode, 0, len(ticks) - 1, {}))
        battle_tick_text.set_text(format_battle_tick_text(int(final_state.tick)))
        count_text.set_text(format_count_text(len(final_a), len(final_b), curr_size_a, curr_size_b, pct_a, pct_b))
        anim = None

    if export_video_enabled_layout:
        if anim is None:
            raise RuntimeError("Video export requires captured animation frames (animate=true).")
        ffmpeg_path = _resolve_ffmpeg_path()
        if not ffmpeg_path:
            raise RuntimeError(
                "Video export enabled but ffmpeg not found. Install ffmpeg or imageio-ffmpeg."
            )
        output_path = Path(str(_cfg(export_video_cfg_layout, "output_path", "analysis/exports/videos")))
        if not output_path.is_absolute():
            output_path = (Path.cwd() / output_path).resolve()
        if not bool(_cfg(export_video_cfg_layout, "output_path_is_final", False)):
            stem_has_timestamp = re.search(r"_\d{8}_\d{6}$", output_path.stem) is not None
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if output_path.suffix:
                if not stem_has_timestamp:
                    output_path = output_path.with_name(f"{output_path.stem}_{timestamp}{output_path.suffix}")
            else:
                output_path = output_path / f"test_run_v1_0_{timestamp}.mp4"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        mpl.rcParams["animation.ffmpeg_path"] = ffmpeg_path
        fps = max(1, int(_cfg(export_video_cfg_layout, "fps", max(1, int(round(1000.0 / max(1, frame_interval_ms)))))))
        codec = str(_cfg(export_video_cfg_layout, "codec", "libx264"))
        bitrate_kbps = max(200, int(_cfg(export_video_cfg_layout, "bitrate_kbps", 2400)))
        writer = FFMpegWriter(
            fps=fps,
            codec=codec,
            bitrate=bitrate_kbps,
            extra_args=[
                "-pix_fmt",
                "yuv420p",
                "-vf",
                f"scale={export_width_px_layout}:{export_height_px_layout}:flags=lanczos",
            ],
        )
        original_size_inches = tuple(fig.get_size_inches())
        if not export_full_plot_layout:
            for ax in fig.axes:
                if ax is battle_ax:
                    continue
                ax.set_visible(False)
            battle_ax.set_position([0.0, 0.0, 1.0, 1.0])
        print(f"[viz] export_video enabled: {output_path}")
        print(
            f"[viz] export writer=ffmpeg, fps={fps}, codec={codec}, bitrate_kbps={bitrate_kbps}, "
            f"size={export_width_px_layout}x{export_height_px_layout}, dpi={export_dpi_layout}, "
            f"full_plot={export_full_plot_layout}"
        )
        try:
            fig.set_size_inches(export_width_px_layout / export_dpi_layout, export_height_px_layout / export_dpi_layout, forward=True)
            try:
                fig.canvas.draw()
            except Exception:
                pass
            anim.save(
                str(output_path),
                writer=writer,
                dpi=export_dpi_layout,
            )
        finally:
            fig.set_size_inches(original_size_inches[0], original_size_inches[1], forward=True)
        print(f"[viz] export complete: {output_path}")
        # Export-only mode: skip interactive preview window in workspace.
        plt.close(fig)
        if interactive_state_before_render:
            plt.ion()
        return

    def stop_animation_callbacks() -> None:
        if anim is None:
            return
        try:
            anim.event_source.stop()
        except Exception:
            pass
        try:
            anim._stop()  # type: ignore[attr-defined]
        except Exception:
            pass

    try:
        fig.canvas.mpl_connect("close_event", lambda _evt: stop_animation_callbacks())
    except Exception:
        pass

    try:
        manager_window = getattr(getattr(fig.canvas, "manager", None), "window", None)
        if manager_window is not None and hasattr(manager_window, "protocol"):
            def _on_wm_delete():
                stop_animation_callbacks()
                try:
                    manager_window.destroy()
                except Exception:
                    pass
            manager_window.protocol("WM_DELETE_WINDOW", _on_wm_delete)
    except Exception:
        pass
    try:
        fig.canvas.draw()
    except Exception:
        pass
    plt.show()
