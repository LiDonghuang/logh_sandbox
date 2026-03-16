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


def _mean_xy(points: Sequence[tuple[float, float]]) -> tuple[float, float]:
    if not points:
        return (0.0, 0.0)
    sx = 0.0
    sy = 0.0
    for x, y in points:
        sx += float(x)
        sy += float(y)
    n = float(len(points))
    return (sx / n, sy / n)


def _std_population(values: Sequence[float]) -> float:
    if not values:
        return 0.0
    mean = sum(float(v) for v in values) / float(len(values))
    var = sum((float(v) - mean) ** 2 for v in values) / float(len(values))
    if var < 0.0:
        var = 0.0
    return math.sqrt(var)


def _deterministic_kmeans_1d(values: Sequence[float], max_iters: int = 12) -> tuple[list[float], list[float]]:
    if len(values) <= 1:
        return (list(values), [])
    c1 = min(values)
    c2 = max(values)
    if abs(c2 - c1) <= 1e-9:
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
        nc1 = sum(group1) / float(len(group1))
        nc2 = sum(group2) / float(len(group2))
        if abs(nc1 - c1) <= 1e-9 and abs(nc2 - c2) <= 1e-9:
            break
        c1 = nc1
        c2 = nc2
    return (group1, group2)


def _compute_formation_metrics_xy(
    side_points: Sequence[tuple[float, float]],
    enemy_points: Sequence[tuple[float, float]],
    angle_bins: int = 12,
) -> dict[str, float]:
    out = {
        "AR": 1.0,
        "AR_forward": 1.0,
        "major_axis_alignment": 0.0,
        "wedge_ratio": 1.0,
        "split_separation": 0.0,
        "angle_coverage": 0.0,
    }
    if not side_points:
        return out
    cx, cy = _mean_xy(side_points)
    if len(side_points) == 1:
        return out

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

    if abs(cov_xy) > 1e-9 or abs(lam1 - var_y) > 1e-9:
        evx = lam1 - var_y
        evy = cov_xy
    else:
        evx = 1.0
        evy = 0.0
    norm = math.sqrt(evx * evx + evy * evy)
    if norm <= 1e-9:
        ux = 1.0
        uy = 0.0
    else:
        ux = evx / norm
        uy = evy / norm
    vx = -uy
    vy = ux

    sigma1 = math.sqrt(lam1)
    sigma2 = math.sqrt(lam2)
    out["AR"] = sigma1 / (sigma2 + 1e-9)

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
        out["split_separation"] = abs(mean1 - mean2) / (std_u + 1e-9)

    if enemy_points and angle_bins > 0:
        ex, ey = _mean_xy(enemy_points)
        occupied = set()
        full = 2.0 * math.pi
        for x, y in side_points:
            phi = math.atan2(float(y) - ey, float(x) - ex)
            if phi < 0.0:
                phi += full
            idx = int((phi / full) * angle_bins)
            if idx < 0:
                idx = 0
            if idx >= angle_bins:
                idx = angle_bins - 1
            occupied.add(idx)
        out["angle_coverage"] = float(len(occupied)) / float(angle_bins)

    if enemy_points:
        ex, ey = _mean_xy(enemy_points)
        fx = ex - cx
        fy = ey - cy
        fn = math.sqrt((fx * fx) + (fy * fy))
        if fn > 1e-9:
            fx /= fn
            fy /= fn
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
            out["AR_forward"] = sigma_forward / (sigma_lateral + 1e-9)
            out["major_axis_alignment"] = abs((ux * fx) + (uy * fy))

    n_units = len(side_points)
    if n_units > 0 and enemy_points:
        group_size = max(1, int(math.ceil(0.3 * float(n_units))))
        ex, ey = _mean_xy(enemy_points)
        fx = ex - cx
        fy = ey - cy
        fn = math.sqrt((fx * fx) + (fy * fy))
        if fn > 1e-9:
            fx /= fn
            fy /= fn
            lx = -fy
            ly = fx
            forward_values = []
            lateral_values = []
            for x, y in side_points:
                dx = float(x) - cx
                dy = float(y) - cy
                forward_values.append((dx * fx) + (dy * fy))
                lateral_values.append((dx * lx) + (dy * ly))
            sorted_idx = sorted(range(n_units), key=lambda i: forward_values[i])
            rear_idx = sorted_idx[:group_size]
            front_idx = sorted_idx[-group_size:]
            lateral_rear = [lateral_values[i] for i in rear_idx]
            lateral_front = [lateral_values[i] for i in front_idx]
            width_front = _std_population(lateral_front)
            width_back = _std_population(lateral_rear)
            out["wedge_ratio"] = width_front / (width_back + 1e-9)
    return out


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
    unit_direction_mode = str(unit_direction_mode).strip().lower()
    if unit_direction_mode not in {"effective", "free", "attack", "composite"}:
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

    def has_finite_value(series: Sequence[float]) -> bool:
        for value in series:
            if math.isfinite(float(value)):
                return True
        return False

    shadow_cohesion_a = extract_observer_series("cohesion_v3", "A", len(ticks))
    shadow_cohesion_b = extract_observer_series("cohesion_v3", "B", len(ticks))
    observer_shadow_ready = bool(plot_panel_enabled) and has_finite_value(shadow_cohesion_a) and has_finite_value(shadow_cohesion_b)
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
        if export_video_enabled_layout:
            return
        if fig_manager is None:
            return
        effective_window_width_px = None
        effective_window_height_px = None
        manager_window = None
        try:
            manager_window = getattr(fig_manager, "window", None)
            if manager_window is not None:
                # Maximize at figure creation stage.
                if hasattr(manager_window, "state"):
                    manager_window.state("zoomed")
                elif hasattr(manager_window, "showMaximized"):
                    manager_window.showMaximized()
                if hasattr(manager_window, "update_idletasks"):
                    manager_window.update_idletasks()
                # Tk path.
                if hasattr(manager_window, "winfo_width") and hasattr(manager_window, "winfo_height"):
                    ww = int(manager_window.winfo_width())
                    hh = int(manager_window.winfo_height())
                    if ww > 100 and hh > 100:
                        effective_window_width_px = ww
                        effective_window_height_px = hh
                # Qt path.
                if (
                    (effective_window_width_px is None or effective_window_height_px is None)
                    and hasattr(manager_window, "size")
                ):
                    qsize = manager_window.size()
                    if qsize is not None and hasattr(qsize, "width") and hasattr(qsize, "height"):
                        ww = int(qsize.width())
                        hh = int(qsize.height())
                        if ww > 100 and hh > 100:
                            effective_window_width_px = ww
                            effective_window_height_px = hh
        except Exception:
            pass
        if effective_window_width_px is not None and effective_window_height_px is not None:
            try:
                figure_dpi = max(72.0, float(fig.get_dpi()))
                fig.set_size_inches(
                    effective_window_width_px / figure_dpi,
                    effective_window_height_px / figure_dpi,
                    forward=True,
                )
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
        # 1) Galaxy haze fixed at battlefield center, fixed size, fixed 135deg.
        haze_center_ratio = _cfg(haze_cfg, "center_ratio", [0.5, 0.5])
        haze_center_x = size * float(haze_center_ratio[0])
        haze_center_y = size * float(haze_center_ratio[1])
        haze_angle = float(_cfg(haze_cfg, "angle_deg", 135.0))
        # Haze sizing model:
        # - inner_size_ratio controls inner major-axis scale
        # - outer_inner_ratio controls outer/inner size ratio
        # - axis_ratio controls minor/major shape ratio
        haze_inner_size_ratio = float(_cfg(haze_cfg, "inner_size_ratio", 0.735))
        haze_outer_inner_ratio = float(_cfg(haze_cfg, "outer_inner_ratio", 1.3333333333))
        haze_axis_ratio = float(_cfg(haze_cfg, "axis_ratio", 0.3061224489))
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
        # 2) Primary major star.
        major_star_radius_range = _cfg(major_star_cfg, "radius_range", [30.0, 45.0])
        major_star_colors = _cfg(major_star_cfg, "colors", ["#fff9dc", "#ffe38a", "#ff9a7a"])
        major_star_glow_scale = float(_cfg(major_star_cfg, "glow_scale", 1.22))
        major_star_glow_alpha = float(_cfg(major_star_cfg, "glow_alpha", 0.10))
        major_star_core_alpha = float(_cfg(major_star_cfg, "core_alpha", 0.36))
        major_star_x = rng.uniform(0.0, size)
        major_star_y = rng.uniform(0.0, size)
        major_star_r = rng.uniform(float(major_star_radius_range[0]), float(major_star_radius_range[1]))
        major_star_color = str(rng.choice(major_star_colors))
        primary_visual_r = major_star_r * major_star_glow_scale
        ax.add_patch(
            Circle(
                (major_star_x, major_star_y),
                primary_visual_r,
                color=major_star_color,
                alpha=major_star_glow_alpha,
                zorder=0.074,
            )
        )
        ax.add_patch(
            Circle(
                (major_star_x, major_star_y),
                major_star_r,
                color=major_star_color,
                alpha=major_star_core_alpha,
                zorder=0.075,
            )
        )
        occupied_celestial_fields: list[tuple[float, float, float]] = [
            (major_star_x, major_star_y, primary_visual_r),
        ]

        def register_celestial_occupancy(x: float, y: float, radius: float) -> None:
            if radius <= 0.0:
                return
            occupied_celestial_fields.append((x, y, radius))

        secondary_star_count_range = _cfg(major_star_cfg, "secondary_count_range", [0, 2])
        secondary_scale_raw = _cfg(major_star_cfg, "secondary_scale", 0.5)
        if isinstance(secondary_scale_raw, (list, tuple)) and len(secondary_scale_raw) >= 2:
            secondary_scale_low = float(secondary_scale_raw[0])
            secondary_scale_high = float(secondary_scale_raw[1])
            if secondary_scale_high < secondary_scale_low:
                secondary_scale_low, secondary_scale_high = secondary_scale_high, secondary_scale_low
            secondary_scale_low = max(0.01, secondary_scale_low)
            secondary_scale_high = max(secondary_scale_low, secondary_scale_high)
            secondary_star_scale = rng.uniform(secondary_scale_low, secondary_scale_high)
        else:
            secondary_star_scale = float(secondary_scale_raw)
        if secondary_star_scale <= 0.0:
            secondary_star_scale = 0.5
        secondary_min_sep_ratio = float(_cfg(major_star_cfg, "secondary_min_separation_ratio", 0.55))
        # Secondary stars are constrained to far-distance orbits from primary star.
        if secondary_min_sep_ratio < 0.45:
            secondary_min_sep_ratio = 0.45
        secondary_glow_alpha_scale = float(_cfg(major_star_cfg, "secondary_glow_alpha_scale", 0.85))
        secondary_core_alpha_scale = float(_cfg(major_star_cfg, "secondary_core_alpha_scale", 0.85))
        secondary_count = rng.randint(int(secondary_star_count_range[0]), int(secondary_star_count_range[1]))
        secondary_min_sep = size * secondary_min_sep_ratio
        secondary_non_overlap_margin = size * 0.03
        secondary_star_fields: list[tuple[float, float, float]] = []

        # 3) Planet-like bodies: size correlates with primary-star relative distance.
        asteroid_count_range = _cfg(asteroids_cfg, "count_range", [0, 3])
        asteroid_radius_range = _cfg(asteroids_cfg, "radius_range", [5.0, 10.0])
        asteroid_colors = _cfg(asteroids_cfg, "colors", ["#8f969f", "#9aa1ab", "#8a939c"])
        asteroid_alpha = float(_cfg(asteroids_cfg, "alpha", 0.72))
        orbit_ratio_range = _cfg(asteroids_cfg, "orbit_ratio_range", [0.18, 0.95])
        orbit_jitter_range = _cfg(asteroids_cfg, "orbit_jitter_range", [0.92, 1.08])
        orbit_radius_base_ratio = float(_cfg(orbit_cfg, "orbit_radius_base_ratio", 0.5))
        draw_orbits_enabled = bool(_cfg(orbit_cfg, "draw_orbits_enabled", False))
        orbit_line_color = str(_cfg(orbit_cfg, "orbit_line_color", "#6f7784"))
        orbit_line_alpha = float(_cfg(orbit_cfg, "orbit_line_alpha", 0.22))
        orbit_line_width = float(_cfg(orbit_cfg, "orbit_line_width", 0.55))
        orbital_draw_ratio_max = float(_cfg(orbit_cfg, "draw_extent_ratio_max", 1.25))
        planet_orbit_gap_ratio_min = float(_cfg(orbit_cfg, "planet_orbit_gap_ratio_min", 0.01))
        angle_jitter_deg = float(_cfg(asteroids_cfg, "angle_jitter_deg", 12.0))
        min_separation_ratio = float(_cfg(asteroids_cfg, "min_separation_ratio", 0.11))
        small_zone_max_ratio = float(_cfg(asteroids_cfg, "small_zone_max_ratio", 0.42))
        mid_zone_max_ratio = float(_cfg(asteroids_cfg, "mid_zone_max_ratio", 0.72))
        if small_zone_max_ratio < 0.0:
            small_zone_max_ratio = 0.0
        if mid_zone_max_ratio < small_zone_max_ratio:
            mid_zone_max_ratio = small_zone_max_ratio
        if mid_zone_max_ratio > 1.0:
            mid_zone_max_ratio = 1.0
        moon_cfg = _cfg(asteroids_cfg, "moons", {})
        moon_enabled = bool(_cfg(moon_cfg, "enabled", True))
        moon_size_ratio_range = _cfg(moon_cfg, "size_ratio_range", [0.1, 0.2])
        moon_orbit_scale_range = _cfg(moon_cfg, "orbit_scale_range", [2.2, 4.5])
        moon_count_range_medium = _cfg(moon_cfg, "count_range_medium", [0, 1])
        moon_count_range_large = _cfg(moon_cfg, "count_range_large", [1, 2])
        moon_color = str(_cfg(moon_cfg, "color", "#cfd5df"))
        moon_alpha = float(_cfg(moon_cfg, "alpha", 0.75))
        # Orbital celestial objects are allowed to extend slightly beyond map border.
        # Domain with draw_extent_ratio_max=1.25: [-0.25*arena, 1.25*arena] on both axes.
        orbital_draw_ratio_max = max(1.0, min(2.0, orbital_draw_ratio_max))
        orbital_draw_min = size * (1.0 - orbital_draw_ratio_max)
        orbital_draw_max = size * orbital_draw_ratio_max

        def in_orbital_draw_bounds(x: float, y: float) -> bool:
            return (orbital_draw_min <= x <= orbital_draw_max) and (orbital_draw_min <= y <= orbital_draw_max)

        def in_canvas_bounds(x: float, y: float) -> bool:
            return (0.0 <= x <= size) and (0.0 <= y <= size)

        def draw_orbit_path(orbit_shell: Mapping[str, float]) -> None:
            orbit_semi_major = float(orbit_shell.get("semi_major", 0.0))
            orbit_semi_minor = float(orbit_shell.get("semi_minor", 0.0))
            orbit_center_x = float(orbit_shell.get("center_x", major_star_x))
            orbit_center_y = float(orbit_shell.get("center_y", major_star_y))
            orbit_angle_deg = float(orbit_shell.get("angle_deg", 0.0))
            if (not draw_orbits_enabled) or orbit_semi_major <= 1e-9 or orbit_semi_minor <= 1e-9:
                return
            ax.add_patch(
                Ellipse(
                    (orbit_center_x, orbit_center_y),
                    2.0 * orbit_semi_major,
                    2.0 * orbit_semi_minor,
                    angle=orbit_angle_deg,
                    fill=False,
                    edgecolor=orbit_line_color,
                    linewidth=max(0.1, orbit_line_width),
                    linestyle="--",
                    alpha=max(0.0, min(1.0, orbit_line_alpha)),
                    zorder=0.076,
                )
            )

        gas_giant_ring_cfg = _cfg(asteroids_cfg, "gas_giant_ring", {})
        ring_enabled = bool(_cfg(gas_giant_ring_cfg, "enabled", True))
        ring_diameter_scale_range = _cfg(gas_giant_ring_cfg, "diameter_scale_range", [2.1, 3.4])
        ring_axis_ratio_range = _cfg(gas_giant_ring_cfg, "axis_ratio_range", [0.2, 0.55])
        ring_angle_deg_range = _cfg(gas_giant_ring_cfg, "angle_deg_range", [0.0, 180.0])
        ring_color = str(_cfg(gas_giant_ring_cfg, "color", "#c6ccd6"))
        ring_alpha = float(_cfg(gas_giant_ring_cfg, "alpha", 0.65))
        ring_band_width_ratio = 0.24
        asteroid_r_min = float(asteroid_radius_range[0])
        asteroid_r_max = float(asteroid_radius_range[1])
        if asteroid_r_max < asteroid_r_min:
            asteroid_r_min, asteroid_r_max = asteroid_r_max, asteroid_r_min
        asteroid_r_span = max(0.0, asteroid_r_max - asteroid_r_min)
        orbit_radius_base_ratio = max(0.05, min(1.2, orbit_radius_base_ratio))
        orbit_radius_base = size * orbit_radius_base_ratio * math.sqrt(2.0)
        planet_orbit_gap_ratio_min = max(0.0, min(1.0, planet_orbit_gap_ratio_min))
        orbit_ratio_low = max(0.0, min(1.0, float(orbit_ratio_range[0])))
        orbit_ratio_high = max(0.0, min(1.0, float(orbit_ratio_range[1])))
        if orbit_ratio_high < orbit_ratio_low:
            orbit_ratio_low, orbit_ratio_high = orbit_ratio_high, orbit_ratio_low
        if orbit_ratio_high - orbit_ratio_low < 1e-9:
            orbit_ratio_high = min(1.0, orbit_ratio_low + 0.01)
        angle_jitter_rad = math.radians(max(0.0, angle_jitter_deg))
        min_planet_sep = max(0.0, orbit_radius_base * min_separation_ratio)
        asteroid_count = rng.randint(int(asteroid_count_range[0]), int(asteroid_count_range[1]))
        planet_orbit_ratios: list[float] = []
        planet_orbit_thetas: list[float] = []
        planet_target_angle_gap_rad = (2.0 * math.pi) / float(max(8, asteroid_count * 2))

        def classify_planet_size_band(orbit_ratio: float) -> tuple[float, str]:
            if asteroid_r_span <= 1e-9:
                return (asteroid_r_min, "small")
            if orbit_ratio < small_zone_max_ratio:
                small_max = asteroid_r_min + (0.45 * asteroid_r_span)
                return (rng.uniform(asteroid_r_min, small_max), "small")
            if orbit_ratio < mid_zone_max_ratio:
                medium_min = asteroid_r_min + (0.30 * asteroid_r_span)
                medium_max = asteroid_r_min + (0.75 * asteroid_r_span)
                return (rng.uniform(medium_min, medium_max), "medium")
            large_min = asteroid_r_min + (0.55 * asteroid_r_span)
            return (rng.uniform(large_min, asteroid_r_max), "large")

        def draw_planet_ring_band(
            asteroid_x: float,
            asteroid_y: float,
            ring_major_diameter: float,
            ring_minor_diameter: float,
            ring_angle: float,
        ) -> None:
            def sample_ellipse_points(
                major_diameter: float,
                minor_diameter: float,
                angle_deg: float,
                point_count: int,
                reverse: bool = False,
            ) -> list[tuple[float, float]]:
                if point_count < 8:
                    point_count = 8
                angle_rad = math.radians(angle_deg)
                cos_a = math.cos(angle_rad)
                sin_a = math.sin(angle_rad)
                rx = 0.5 * major_diameter
                ry = 0.5 * minor_diameter
                points: list[tuple[float, float]] = []
                for idx in range(point_count):
                    theta = (2.0 * math.pi * idx) / float(point_count)
                    if reverse:
                        theta = (2.0 * math.pi) - theta
                    px = rx * math.cos(theta)
                    py = ry * math.sin(theta)
                    points.append(
                        (
                            asteroid_x + (px * cos_a) - (py * sin_a),
                            asteroid_y + (px * sin_a) + (py * cos_a),
                        )
                    )
                return points

            inner_scale = max(0.05, 1.0 - ring_band_width_ratio)
            inner_major_diameter = ring_major_diameter * inner_scale
            inner_minor_diameter = ring_minor_diameter * inner_scale
            outer_points = sample_ellipse_points(
                ring_major_diameter,
                ring_minor_diameter,
                ring_angle,
                point_count=96,
                reverse=False,
            )
            inner_points = sample_ellipse_points(
                inner_major_diameter,
                inner_minor_diameter,
                ring_angle,
                point_count=96,
                reverse=True,
            )
            vertices = [outer_points[0]]
            codes = [mpl.path.Path.MOVETO]
            for point in outer_points[1:]:
                vertices.append(point)
                codes.append(mpl.path.Path.LINETO)
            vertices.append(outer_points[0])
            codes.append(mpl.path.Path.CLOSEPOLY)
            vertices.append(inner_points[0])
            codes.append(mpl.path.Path.MOVETO)
            for point in inner_points[1:]:
                vertices.append(point)
                codes.append(mpl.path.Path.LINETO)
            vertices.append(inner_points[0])
            codes.append(mpl.path.Path.CLOSEPOLY)
            ring_path = mpl.path.Path(vertices, codes)
            ax.add_patch(
                PathPatch(
                    ring_path,
                    facecolor=ring_color,
                    edgecolor="none",
                    alpha=ring_alpha,
                    fill=True,
                    zorder=0.098,
                )
            )

        def draw_planet_body(asteroid_x: float, asteroid_y: float, asteroid_r: float, size_band: str) -> None:
            if ring_enabled and size_band in {"medium", "large"}:
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
                draw_planet_ring_band(
                    asteroid_x,
                    asteroid_y,
                    ring_major_diameter,
                    ring_minor_diameter,
                    ring_angle,
                )
                register_celestial_occupancy(asteroid_x, asteroid_y, ring_major_diameter * 0.5)
            ax.add_patch(
                Circle(
                    (asteroid_x, asteroid_y),
                    asteroid_r,
                    color=str(rng.choice(asteroid_colors)),
                    alpha=asteroid_alpha,
                    zorder=0.10,
                )
            )
            register_celestial_occupancy(asteroid_x, asteroid_y, asteroid_r)
            if moon_enabled and size_band in {"medium", "large"}:
                if size_band == "large":
                    moon_count = rng.randint(int(moon_count_range_large[0]), int(moon_count_range_large[1]))
                else:
                    moon_count = rng.randint(int(moon_count_range_medium[0]), int(moon_count_range_medium[1]))
                for _moon_idx in range(max(0, moon_count)):
                    moon_r = asteroid_r * rng.uniform(
                        float(moon_size_ratio_range[0]),
                        float(moon_size_ratio_range[1]),
                    )
                    moon_orbit = asteroid_r * rng.uniform(
                        float(moon_orbit_scale_range[0]),
                        float(moon_orbit_scale_range[1]),
                    )
                    moon_theta = rng.uniform(0.0, 2.0 * math.pi)
                    moon_x = asteroid_x + (moon_orbit * math.cos(moon_theta))
                    moon_y = asteroid_y + (moon_orbit * math.sin(moon_theta))
                    if in_orbital_draw_bounds(moon_x, moon_y):
                        moon_z = 0.099 if rng.random() < 0.5 else 0.101
                        ax.add_patch(
                            Circle(
                                (moon_x, moon_y),
                                moon_r,
                                color=moon_color,
                                alpha=moon_alpha,
                                zorder=moon_z,
                            )
                        )
                        register_celestial_occupancy(moon_x, moon_y, moon_r)

        def overlaps_occupied_celestial(x: float, y: float, radius: float, pad: float = 0.0) -> bool:
            clearance_pad = max(0.0, pad)
            for ox, oy, oradius in occupied_celestial_fields:
                if math.hypot(x - ox, y - oy) < (radius + oradius + clearance_pad):
                    return True
            return False

        def estimate_planet_visual_radius(asteroid_r: float, size_band: str) -> float:
            visual_radius = asteroid_r
            if ring_enabled and size_band in {"medium", "large"}:
                visual_radius = max(
                    visual_radius,
                    asteroid_r * max(
                        float(ring_diameter_scale_range[0]),
                        float(ring_diameter_scale_range[1]),
                    ),
                )
            return visual_radius

        def try_place_planet(
            orbit_shell: Mapping[str, float],
            theta_base: float,
            visual_radius: float,
            attempts: int = 24,
            require_in_canvas: bool = False,
        ) -> tuple[float, float, float] | None:
            best_candidate: tuple[float, float, float] | None = None
            best_angle_gap = -1.0
            for _attempt in range(attempts):
                orbit_theta = theta_base + rng.uniform(-angle_jitter_rad, angle_jitter_rad)
                candidate_x, candidate_y, _ = orbit_shell_point(orbit_shell, orbit_theta, radial_scale=1.0)
                if not in_orbital_draw_bounds(candidate_x, candidate_y):
                    continue
                if require_in_canvas and (not in_canvas_bounds(candidate_x, candidate_y)):
                    continue
                if overlaps_occupied_celestial(candidate_x, candidate_y, visual_radius, pad=min_planet_sep * 0.25):
                    continue
                theta_norm = orbit_theta % (2.0 * math.pi)
                if planet_orbit_thetas:
                    min_angle_gap = min(
                        min(abs(theta_norm - pt), (2.0 * math.pi) - abs(theta_norm - pt))
                        for pt in planet_orbit_thetas
                    )
                else:
                    min_angle_gap = 2.0 * math.pi
                candidate = (candidate_x, candidate_y, theta_norm)
                if min_angle_gap >= planet_target_angle_gap_rad:
                    return candidate
                if min_angle_gap > best_angle_gap:
                    best_angle_gap = min_angle_gap
                    best_candidate = candidate
            return best_candidate

        # 4) Asteroid belts: mid/far orbits around the primary star.
        belt_cluster_count_range = _cfg(belts_cfg, "cluster_count_range", [0, 10])
        belt_points_per_360_degree_range = _cfg(belts_cfg, "points_per_360_degree_range", [120.0, 120.0])
        belt_orbit_ratio_range = _cfg(belts_cfg, "orbit_ratio_range", [0.55, 0.95])
        belt_orbit_exclusion_gap_ratio = float(_cfg(orbit_cfg, "belt_planet_exclusion_gap_ratio", 0.06))
        belt_to_belt_exclusion_scale = float(_cfg(orbit_cfg, "belt_belt_exclusion_scale", 0.5))
        belt_thickness_ratio_range = _cfg(belts_cfg, "thickness_ratio_range", [0.05, 0.12])
        belt_arc_span_deg_range = _cfg(belts_cfg, "arc_span_deg_range", [20.0, 55.0])
        belt_curve_strength_range = _cfg(belts_cfg, "curve_strength_range", [-0.06, 0.06])
        belt_asteroid_radius_range = _cfg(belts_cfg, "asteroid_radius_range", [0.1, 0.2])
        belt_color = str(_cfg(belts_cfg, "color", "#8e96a3"))
        belt_alpha = float(_cfg(belts_cfg, "alpha", 0.55))
        belt_body_count = rng.randint(int(belt_cluster_count_range[0]), int(belt_cluster_count_range[1]))
        belt_ratio_low = max(0.0, min(1.0, float(belt_orbit_ratio_range[0])))
        belt_ratio_high = max(0.0, min(1.0, float(belt_orbit_ratio_range[1])))
        if belt_ratio_high < belt_ratio_low:
            belt_ratio_low, belt_ratio_high = belt_ratio_high, belt_ratio_low
        belt_orbit_exclusion_gap_ratio = max(0.0, min(1.0, belt_orbit_exclusion_gap_ratio))
        belt_to_belt_exclusion_scale = max(0.0, min(2.0, belt_to_belt_exclusion_scale))
        if isinstance(belt_points_per_360_degree_range, (list, tuple)) and len(belt_points_per_360_degree_range) >= 2:
            belt_points_per_360_low = float(belt_points_per_360_degree_range[0])
            belt_points_per_360_high = float(belt_points_per_360_degree_range[1])
        else:
            belt_points_per_360_low = 120.0
            belt_points_per_360_high = 120.0
        belt_points_per_360_low = max(1.0, belt_points_per_360_low)
        belt_points_per_360_high = max(1.0, belt_points_per_360_high)
        if belt_points_per_360_high < belt_points_per_360_low:
            belt_points_per_360_low, belt_points_per_360_high = belt_points_per_360_high, belt_points_per_360_low
        belt_orbit_ratios: list[float] = []
        orbit_count_range = _cfg(orbit_cfg, "orbit_count_range", [8, 14])
        orbit_slot_count_low = 8
        orbit_slot_count_high = 14
        if isinstance(orbit_count_range, (list, tuple)) and len(orbit_count_range) >= 2:
            orbit_slot_count_low = max(1, int(orbit_count_range[0]))
            orbit_slot_count_high = max(1, int(orbit_count_range[1]))
        if orbit_slot_count_high < orbit_slot_count_low:
            orbit_slot_count_low, orbit_slot_count_high = orbit_slot_count_high, orbit_slot_count_low
        orbit_pool_ratio_low = min(orbit_ratio_low, belt_ratio_low)
        orbit_pool_ratio_high = max(orbit_ratio_high, belt_ratio_high)
        orbit_shell_soft_gap_ratio = max(
            0.0,
            planet_orbit_gap_ratio_min,
            belt_orbit_exclusion_gap_ratio,
            belt_to_belt_exclusion_scale * belt_orbit_exclusion_gap_ratio,
        )
        orbit_jitter_low = float(orbit_jitter_range[0])
        orbit_jitter_high = float(orbit_jitter_range[1])
        if orbit_jitter_high < orbit_jitter_low:
            orbit_jitter_low, orbit_jitter_high = orbit_jitter_high, orbit_jitter_low
        orbit_shell_jitter_ratio = min(
            0.45,
            max(abs(1.0 - orbit_jitter_low), abs(orbit_jitter_high - 1.0)),
        )
        orbit_eccentricity_near = float(_cfg(orbit_cfg, "eccentricity_near", 0.02))
        orbit_eccentricity_far = float(_cfg(orbit_cfg, "eccentricity_far", 0.24))
        orbit_eccentricity_near = max(0.0, min(0.85, orbit_eccentricity_near))
        orbit_eccentricity_far = max(0.0, min(0.85, orbit_eccentricity_far))
        if orbit_eccentricity_far < orbit_eccentricity_near:
            orbit_eccentricity_far = orbit_eccentricity_near
        orbit_major_axis_angle_deg = rng.uniform(0.0, 180.0)
        orbit_major_axis_angle_rad = math.radians(orbit_major_axis_angle_deg)
        orbit_major_axis_cos = math.cos(orbit_major_axis_angle_rad)
        orbit_major_axis_sin = math.sin(orbit_major_axis_angle_rad)

        def build_orbit_ratio_pool(required_count: int) -> list[float]:
            orbit_slot_count = max(required_count, rng.randint(orbit_slot_count_low, orbit_slot_count_high))
            if orbit_slot_count <= 1:
                return [0.5 * (orbit_pool_ratio_low + orbit_pool_ratio_high)]
            orbit_span = max(1e-6, orbit_pool_ratio_high - orbit_pool_ratio_low)
            base_step = orbit_span / float(orbit_slot_count - 1)
            effective_soft_gap = min(max(0.0, orbit_shell_soft_gap_ratio), base_step * 0.9)
            orbit_ratios: list[float] = []
            for orbit_idx in range(orbit_slot_count):
                base_ratio = orbit_pool_ratio_low + (base_step * orbit_idx)
                ratio_jitter = rng.uniform(-orbit_shell_jitter_ratio, orbit_shell_jitter_ratio) * base_step
                candidate_ratio = base_ratio + ratio_jitter
                left_bound = orbit_pool_ratio_low if orbit_idx == 0 else (orbit_ratios[-1] + effective_soft_gap)
                remaining_slots = orbit_slot_count - orbit_idx - 1
                right_bound = orbit_pool_ratio_high - (remaining_slots * effective_soft_gap)
                if right_bound < left_bound:
                    right_bound = left_bound
                candidate_ratio = max(left_bound, min(right_bound, candidate_ratio))
                orbit_ratios.append(candidate_ratio)
            return orbit_ratios

        def orbit_ratio_progress(orbit_ratio: float) -> float:
            span = max(1e-9, orbit_pool_ratio_high - orbit_pool_ratio_low)
            progress = (float(orbit_ratio) - orbit_pool_ratio_low) / span
            return max(0.0, min(1.0, progress))

        def build_orbit_shell(orbit_ratio: float) -> dict[str, float]:
            semi_major = orbit_radius_base * float(orbit_ratio)
            eccentricity = orbit_eccentricity_near + (
                (orbit_eccentricity_far - orbit_eccentricity_near) * orbit_ratio_progress(orbit_ratio)
            )
            eccentricity = max(0.0, min(0.85, eccentricity))
            semi_minor = semi_major * math.sqrt(max(0.0, 1.0 - (eccentricity * eccentricity)))
            focus_offset = semi_major * eccentricity
            center_x = major_star_x - (focus_offset * orbit_major_axis_cos)
            center_y = major_star_y - (focus_offset * orbit_major_axis_sin)
            return {
                "orbit_ratio": float(orbit_ratio),
                "semi_major": semi_major,
                "semi_minor": semi_minor,
                "eccentricity": eccentricity,
                "center_x": center_x,
                "center_y": center_y,
                "angle_deg": orbit_major_axis_angle_deg,
            }

        def orbit_shell_point(
            orbit_shell: Mapping[str, float],
            theta: float,
            radial_scale: float = 1.0,
        ) -> tuple[float, float, float]:
            center_x = float(orbit_shell.get("center_x", major_star_x))
            center_y = float(orbit_shell.get("center_y", major_star_y))
            semi_major = float(orbit_shell.get("semi_major", 0.0)) * radial_scale
            semi_minor = float(orbit_shell.get("semi_minor", 0.0)) * radial_scale
            px = semi_major * math.cos(theta)
            py = semi_minor * math.sin(theta)
            x = center_x + (px * orbit_major_axis_cos) - (py * orbit_major_axis_sin)
            y = center_y + (px * orbit_major_axis_sin) + (py * orbit_major_axis_cos)
            local_radius = math.sqrt((px * px) + (py * py))
            return (x, y, local_radius)

        def draw_belt_object(
            orbit_shell: Mapping[str, float],
            belt_center_theta: float,
            require_in_canvas: bool = False,
        ) -> bool:
            belt_major = float(orbit_shell.get("semi_major", 0.0))
            belt_minor = belt_major * rng.uniform(
                float(belt_thickness_ratio_range[0]),
                float(belt_thickness_ratio_range[1]),
            )
            if belt_major <= 1e-9 or belt_minor <= 1e-9:
                return False
            arc_span_deg = rng.uniform(
                float(belt_arc_span_deg_range[0]),
                float(belt_arc_span_deg_range[1]),
            )
            points_per_360 = rng.uniform(belt_points_per_360_low, belt_points_per_360_high)
            belt_count = max(1, int(round((points_per_360 * arc_span_deg) / 360.0)))
            arc_span_rad = math.radians(max(6.0, arc_span_deg))
            curve_strength = rng.uniform(
                float(belt_curve_strength_range[0]),
                float(belt_curve_strength_range[1]),
            )
            belt_points: list[tuple[float, float, float]] = []
            in_canvas_count = 0
            for _ in range(belt_count):
                t = rng.uniform(-0.5, 0.5)
                theta = belt_center_theta + (t * arc_span_rad)
                radial_jitter = rng.uniform(-belt_minor, belt_minor)
                inward_bow = 1.0 - (curve_strength * (1.0 - (4.0 * t * t)))
                _, _, base_local_radius = orbit_shell_point(orbit_shell, theta, radial_scale=1.0)
                if base_local_radius <= 1e-9:
                    continue
                radial_scale = max(0.1, ((base_local_radius + radial_jitter) * inward_bow) / base_local_radius)
                asteroid_x, asteroid_y, _ = orbit_shell_point(orbit_shell, theta, radial_scale=radial_scale)
                if not in_orbital_draw_bounds(asteroid_x, asteroid_y):
                    continue
                asteroid_r = rng.uniform(
                    float(belt_asteroid_radius_range[0]),
                    float(belt_asteroid_radius_range[1]),
                )
                belt_points.append((asteroid_x, asteroid_y, asteroid_r))
                if in_canvas_bounds(asteroid_x, asteroid_y):
                    in_canvas_count += 1
            if not belt_points:
                return False
            if require_in_canvas and in_canvas_count <= 0:
                return False
            for asteroid_x, asteroid_y, asteroid_r in belt_points:
                ax.add_patch(
                    Circle(
                        (asteroid_x, asteroid_y),
                        asteroid_r,
                        color=belt_color,
                        alpha=belt_alpha,
                        zorder=0.12,
                    )
                )
                register_celestial_occupancy(asteroid_x, asteroid_y, asteroid_r)
            return True

        def try_add_planet(
            available_orbit_indices: set[int],
            used_orbit_indices: set[int],
            orbit_pool_ratios: list[float],
            orbit_pool_shells: list[Mapping[str, float]],
            orbit_try_count: int = 10,
            place_attempts: int = 18,
            require_in_canvas: bool = False,
        ) -> bool:
            candidate_indices = [
                orbit_idx
                for orbit_idx in available_orbit_indices
                if orbit_ratio_low <= orbit_pool_ratios[orbit_idx] <= orbit_ratio_high
            ]
            if not candidate_indices:
                return False
            rng.shuffle(candidate_indices)
            for orbit_idx in candidate_indices[: max(1, orbit_try_count)]:
                orbit_ratio = orbit_pool_ratios[orbit_idx]
                orbit_shell = orbit_pool_shells[orbit_idx]
                asteroid_r, size_band = classify_planet_size_band(orbit_ratio)
                visual_radius = estimate_planet_visual_radius(asteroid_r, size_band)
                orbit_theta_base = rng.uniform(0.0, 2.0 * math.pi)
                placed_xy = try_place_planet(
                    orbit_shell,
                    orbit_theta_base,
                    visual_radius,
                    attempts=place_attempts,
                    require_in_canvas=require_in_canvas,
                )
                if placed_xy is None:
                    continue
                asteroid_x, asteroid_y, asteroid_theta = placed_xy
                available_orbit_indices.remove(orbit_idx)
                used_orbit_indices.add(orbit_idx)
                planet_orbit_ratios.append(orbit_ratio)
                planet_orbit_thetas.append(asteroid_theta)
                draw_planet_body(asteroid_x, asteroid_y, asteroid_r, size_band)
                return True
            return False

        def try_add_belt(
            available_orbit_indices: set[int],
            used_orbit_indices: set[int],
            orbit_pool_ratios: list[float],
            orbit_pool_shells: list[Mapping[str, float]],
            orbit_try_count: int = 12,
            require_in_canvas: bool = False,
        ) -> bool:
            candidate_indices = [
                orbit_idx
                for orbit_idx in available_orbit_indices
                if belt_ratio_low <= orbit_pool_ratios[orbit_idx] <= belt_ratio_high
            ]
            if not candidate_indices:
                return False
            rng.shuffle(candidate_indices)
            for orbit_idx in candidate_indices[: max(1, orbit_try_count)]:
                orbit_ratio = orbit_pool_ratios[orbit_idx]
                orbit_shell = orbit_pool_shells[orbit_idx]
                belt_center_theta = rng.uniform(0.0, 2.0 * math.pi)
                if draw_belt_object(orbit_shell, belt_center_theta, require_in_canvas=require_in_canvas):
                    available_orbit_indices.remove(orbit_idx)
                    used_orbit_indices.add(orbit_idx)
                    belt_orbit_ratios.append(orbit_ratio)
                    return True
            return False

        def build_weighted_round_robin_order(planet_count: int, belt_count: int) -> list[str]:
            remaining_planets = max(0, int(planet_count))
            remaining_belts = max(0, int(belt_count))
            total_count = remaining_planets + remaining_belts
            if total_count <= 0:
                return []
            score_planet = 0
            score_belt = 0
            order: list[str] = []
            for _ in range(total_count):
                if remaining_planets > 0:
                    score_planet += remaining_planets
                if remaining_belts > 0:
                    score_belt += remaining_belts
                if remaining_planets <= 0:
                    chosen_kind = "belt"
                elif remaining_belts <= 0:
                    chosen_kind = "planet"
                elif score_planet >= score_belt:
                    chosen_kind = "planet"
                else:
                    chosen_kind = "belt"
                order.append(chosen_kind)
                if chosen_kind == "planet":
                    score_planet -= total_count
                else:
                    score_belt -= total_count
            return order

        def fill_orbit_population_round_robin(
            *,
            planet_target_count: int,
            belt_target_count: int,
            require_in_canvas: bool,
            attempt_scale: int = 120,
        ) -> None:
            placement_order = build_weighted_round_robin_order(planet_target_count, belt_target_count)
            if not placement_order:
                return
            attempt_limit = max(120, max(1, len(placement_order)) * max(1, int(attempt_scale)))
            attempts = 0
            turn_idx = 0
            baseline_planets = len(planet_orbit_ratios)
            baseline_belts = len(belt_orbit_ratios)
            while attempts < attempt_limit:
                placed_planets = len(planet_orbit_ratios) - baseline_planets
                placed_belts = len(belt_orbit_ratios) - baseline_belts
                if placed_planets >= planet_target_count and placed_belts >= belt_target_count:
                    return
                chosen_kind = placement_order[turn_idx % len(placement_order)]
                turn_idx += 1
                if chosen_kind == "planet":
                    if placed_planets >= planet_target_count:
                        continue
                    try_add_planet(
                        available_orbit_indices,
                        used_orbit_indices,
                        orbit_ratio_pool,
                        orbit_shell_pool,
                        orbit_try_count=12,
                        place_attempts=20,
                        require_in_canvas=require_in_canvas,
                    )
                else:
                    if placed_belts >= belt_target_count:
                        continue
                    try_add_belt(
                        available_orbit_indices,
                        used_orbit_indices,
                        orbit_ratio_pool,
                        orbit_shell_pool,
                        orbit_try_count=12,
                        require_in_canvas=require_in_canvas,
                    )
                attempts += 1

        # Sample counts first, then fill shared orbit slots via weighted round-robin.
        # Keep the existing two-pass policy: first guarantee in-canvas minimum, then fill remaining target count.
        target_planets = asteroid_count
        target_belts = belt_body_count
        min_belts_in_canvas = min(target_belts, max(0, int(belt_cluster_count_range[0])))
        min_planets_in_canvas = min(target_planets, max(0, int(asteroid_count_range[0])))
        orbit_ratio_pool = build_orbit_ratio_pool(target_planets + target_belts)
        orbit_shell_pool = [build_orbit_shell(orbit_ratio) for orbit_ratio in orbit_ratio_pool]
        available_orbit_indices: set[int] = set(range(len(orbit_ratio_pool)))
        used_orbit_indices: set[int] = set()

        fill_orbit_population_round_robin(
            planet_target_count=min_planets_in_canvas,
            belt_target_count=min_belts_in_canvas,
            require_in_canvas=True,
        )
        fill_orbit_population_round_robin(
            planet_target_count=max(0, target_planets - len(planet_orbit_ratios)),
            belt_target_count=max(0, target_belts - len(belt_orbit_ratios)),
            require_in_canvas=False,
        )

        if draw_orbits_enabled:
            for orbit_idx in sorted(used_orbit_indices):
                draw_orbit_path(orbit_shell_pool[orbit_idx])

        # 5) Secondary stars: place after belts/planets, prefer emptier corners near edges.

        def score_secondary_candidate(x: float, y: float, sec_visual_r: float) -> float | None:
            if not in_canvas_bounds(x, y):
                return None
            if math.hypot(x - major_star_x, y - major_star_y) < secondary_min_sep:
                return None
            if overlaps_occupied_celestial(x, y, sec_visual_r, pad=secondary_non_overlap_margin):
                return None
            for ox, oy, oradius in secondary_star_fields:
                if math.hypot(x - ox, y - oy) < (sec_visual_r + oradius + secondary_non_overlap_margin):
                    return None
            min_clearance = float("inf")
            for ox, oy, oradius in occupied_celestial_fields:
                clearance = math.hypot(x - ox, y - oy) - (sec_visual_r + oradius)
                if clearance < min_clearance:
                    min_clearance = clearance
            for ox, oy, oradius in secondary_star_fields:
                clearance = math.hypot(x - ox, y - oy) - (sec_visual_r + oradius)
                if clearance < min_clearance:
                    min_clearance = clearance
            if not math.isfinite(min_clearance):
                min_clearance = 0.0
            edge_dist = min(x, size - x, y, size - y)
            return min_clearance - (0.15 * edge_dist)

        for _ in range(secondary_count):
            sec_r = rng.uniform(float(major_star_radius_range[0]), float(major_star_radius_range[1])) * secondary_star_scale
            sec_visual_r = sec_r * major_star_glow_scale
            corner_inset = max(1.0, sec_visual_r + (secondary_non_overlap_margin * 0.25))
            if (corner_inset * 2.0) >= size:
                continue
            corners = [
                (corner_inset, corner_inset, +1.0, +1.0),
                (size - corner_inset, corner_inset, -1.0, +1.0),
                (corner_inset, size - corner_inset, +1.0, -1.0),
                (size - corner_inset, size - corner_inset, -1.0, -1.0),
            ]
            jitter_span = min(size * 0.08, max(sec_visual_r, size * 0.02))
            candidate_points: list[tuple[float, float]] = []
            for cx, cy, sx, sy in corners:
                candidate_points.append((cx, cy))
                for _ in range(4):
                    jx = rng.uniform(0.0, jitter_span)
                    jy = rng.uniform(0.0, jitter_span)
                    candidate_points.append((cx + (sx * jx), cy + (sy * jy)))

            best_candidate: tuple[float, float] | None = None
            best_score = float("-inf")
            for cand_x, cand_y in candidate_points:
                score = score_secondary_candidate(cand_x, cand_y, sec_visual_r)
                if score is None:
                    continue
                if score > best_score:
                    best_score = score
                    best_candidate = (cand_x, cand_y)

            if best_candidate is None:
                for _attempt in range(48):
                    side = rng.randint(0, 3)
                    t = rng.uniform(corner_inset, size - corner_inset)
                    if side == 0:
                        cand_x, cand_y = corner_inset, t
                    elif side == 1:
                        cand_x, cand_y = size - corner_inset, t
                    elif side == 2:
                        cand_x, cand_y = t, corner_inset
                    else:
                        cand_x, cand_y = t, size - corner_inset
                    score = score_secondary_candidate(cand_x, cand_y, sec_visual_r)
                    if score is None:
                        continue
                    if score > best_score:
                        best_score = score
                        best_candidate = (cand_x, cand_y)

            if best_candidate is None:
                continue

            sec_x, sec_y = best_candidate
            sec_color = str(rng.choice(major_star_colors))
            ax.add_patch(
                Circle(
                    (sec_x, sec_y),
                    sec_visual_r,
                    color=sec_color,
                    alpha=max(0.0, min(1.0, major_star_glow_alpha * secondary_glow_alpha_scale)),
                    zorder=0.064,
                )
            )
            ax.add_patch(
                Circle(
                    (sec_x, sec_y),
                    sec_r,
                    color=sec_color,
                    alpha=max(0.0, min(1.0, major_star_core_alpha * secondary_core_alpha_scale)),
                    zorder=0.065,
                )
            )
            secondary_star_fields.append((sec_x, sec_y, sec_visual_r))
            register_celestial_occupancy(sec_x, sec_y, sec_visual_r)

        return {
            "belts_generated": len(belt_orbit_ratios),
            "belts_target": target_belts,
            "planets_generated": len(planet_orbit_ratios),
            "planets_target": target_planets,
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
    boundary_line_width = 3.0 if boundary_soft_effective else 2.2
    boundary_edge_color = "#000000" if boundary_soft_effective else "#555555"
    boundary_linestyle = "-" if boundary_soft_effective else ":"
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
    vector_display_mode = str(_cfg(viz_settings, "vector_display_mode", "effective")).strip().lower()
    if vector_display_mode not in {"effective", "free", "radial_debug"}:
        vector_display_mode = "effective"
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
    if auto_zoom_start_delay_ticks < 0:
        auto_zoom_start_delay_ticks = 0
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

    def resolve_avatar_image(avatar_id: str):
        stem = str(avatar_id).strip() if avatar_id is not None else ""
        if not stem:
            return None
        avatar_dir = Path(__file__).resolve().parent.parent / "visual" / "avatars"
        if "." in stem:
            candidates = [avatar_dir / stem]
        else:
            candidates = [avatar_dir / f"{stem}.bmp", avatar_dir / f"{stem}.png"]
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

    def estimate_avatar_axes_size(image) -> tuple[float, float] | None:
        if image is None or not hasattr(image, "shape") or len(image.shape) < 2:
            return None
        axes_pos = battle_ax.get_position()
        fig_width_in, fig_height_in = fig.get_size_inches()
        ax_w_px = fig_width_in * fig.dpi * axes_pos.width
        ax_h_px = fig_height_in * fig.dpi * axes_pos.height
        if ax_w_px <= 1e-9 or ax_h_px <= 1e-9:
            return None
        img_h_px = float(image.shape[0]) * float(avatar_zoom)
        img_w_px = float(image.shape[1]) * float(avatar_zoom)
        return (img_w_px / ax_w_px, img_h_px / ax_h_px)

    avatar_a_img = resolve_avatar_image(fleet_a_avatar)
    avatar_b_img = resolve_avatar_image(fleet_b_avatar)
    avatar_images = {
        "A": {
            "color": avatar_a_img,
            "gray": build_grayscale_avatar_image(avatar_a_img),
        },
        "B": {
            "color": avatar_b_img,
            "gray": build_grayscale_avatar_image(avatar_b_img),
        },
    }
    avatar_offset_images: dict[str, OffsetImage] = {}
    avatar_visual_state = {"A": "color", "B": "color"}
    avatar_a_size_axes = estimate_avatar_axes_size(avatar_a_img)
    avatar_b_size_axes = estimate_avatar_axes_size(avatar_b_img)
    avatar_a_h_axes = avatar_a_size_axes[1] if avatar_a_size_axes is not None else 0.105
    avatar_b_h_axes = avatar_b_size_axes[1] if avatar_b_size_axes is not None else 0.105
    marker_side_points = max(8.0, float(full_name_fontsize) * 1.25)
    marker_w_axes = points_to_axes_fraction(marker_side_points, "x")
    marker_h_axes = points_to_axes_fraction(marker_side_points, "y")
    marker_gap_axes = points_to_axes_fraction(max(1.0, float(full_name_fontsize) * 0.2), "x")
    name_horizontal_tune_axes = points_to_axes_fraction(2.0, "x")
    label_touch_gap_axes = points_to_axes_fraction(1.0, "y")
    name_vertical_tune_axes = points_to_axes_fraction(16.0, "y")
    a_name_shift_x_axes = -(0.2 * marker_w_axes)
    b_name_shift_x_axes = 0.2 * marker_w_axes
    a_name_shift_y_axes = marker_h_axes
    b_name_shift_y_axes = -marker_h_axes
    label_bbox = {
        "facecolor": "white",
        "alpha": 0.78,
        "edgecolor": "none",
        "boxstyle": "square,pad=0.16",
    }

    if avatar_a_img is not None:
        avatar_a_artist = OffsetImage(avatar_images["A"]["color"], zoom=avatar_zoom)
        avatar_offset_images["A"] = avatar_a_artist
        avatar_a_box = AnnotationBbox(
            avatar_a_artist,
            (avatar_inset, avatar_inset),
            xycoords="axes fraction",
            box_alignment=(0.0, 0.0),
            pad=0.0,
            frameon=True,
            bboxprops={
                "edgecolor": fleet_a_color,
                "linewidth": avatar_border_linewidth,
                "facecolor": "none",
                "boxstyle": "square,pad=0.0",
            },
            zorder=29.0,
        )
        battle_ax.add_artist(avatar_a_box)
    if avatar_b_img is not None:
        avatar_b_artist = OffsetImage(avatar_images["B"]["color"], zoom=avatar_zoom)
        avatar_offset_images["B"] = avatar_b_artist
        avatar_b_box = AnnotationBbox(
            avatar_b_artist,
            (1.0 - avatar_inset, 1.0 - avatar_inset),
            xycoords="axes fraction",
            box_alignment=(1.0, 1.0),
            pad=0.0,
            frameon=True,
            bboxprops={
                "edgecolor": fleet_b_color,
                "linewidth": avatar_border_linewidth,
                "facecolor": "none",
                "boxstyle": "square,pad=0.0",
            },
            zorder=29.0,
        )
        battle_ax.add_artist(avatar_b_box)

    def set_defeated_avatar(defeated_fleet_id: str | None) -> None:
        for fleet_id in ("A", "B"):
            artist = avatar_offset_images.get(fleet_id)
            if artist is None:
                continue
            next_state = "gray" if defeated_fleet_id == fleet_id else "color"
            if avatar_visual_state[fleet_id] == next_state:
                continue
            artist.set_data(avatar_images[fleet_id][next_state])
            avatar_visual_state[fleet_id] = next_state

    a_name_bottom = min(0.96, avatar_inset + avatar_a_h_axes + label_touch_gap_axes + name_vertical_tune_axes + a_name_shift_y_axes)
    b_name_top = max(0.04, 1.0 - avatar_inset - avatar_b_h_axes - label_touch_gap_axes - name_vertical_tune_axes + b_name_shift_y_axes)
    a_marker_x = avatar_inset + a_name_shift_x_axes
    b_marker_x = 1.0 - avatar_inset - marker_w_axes + b_name_shift_x_axes

    display_name_a = f"{fleet_a_full_name} (A)"
    display_name_b = f"{fleet_b_full_name} (B)"

    a_mark = Rectangle(
        (a_marker_x, a_name_bottom),
        marker_w_axes,
        marker_h_axes,
        transform=battle_ax.transAxes,
        facecolor=fleet_a_color,
        edgecolor="none",
        zorder=30.0,
    )
    battle_ax.add_patch(a_mark)
    battle_ax.text(
        a_marker_x + marker_w_axes + marker_gap_axes + name_horizontal_tune_axes,
        a_name_bottom,
        display_name_a,
        transform=battle_ax.transAxes,
        va="bottom",
        ha="left",
        fontsize=full_name_fontsize,
        fontfamily="sans-serif",
        bbox=label_bbox,
        clip_on=True,
        zorder=30.0,
    )

    b_mark = Rectangle(
        (b_marker_x, b_name_top - marker_h_axes),
        marker_w_axes,
        marker_h_axes,
        transform=battle_ax.transAxes,
        facecolor=fleet_b_color,
        edgecolor="none",
        zorder=30.0,
    )
    battle_ax.add_patch(b_mark)
    battle_ax.text(
        b_marker_x - marker_gap_axes - name_horizontal_tune_axes,
        b_name_top,
        display_name_b,
        transform=battle_ax.transAxes,
        va="top",
        ha="right",
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

    def build_frame_point_map(points_a_norm, points_b_norm) -> dict[str, tuple[float, float]]:
        point_map: dict[str, tuple[float, float]] = {}
        for unit_id, x, y, _, _, _, _ in points_a_norm:
            point_map[str(unit_id)] = (float(x), float(y))
        for unit_id, x, y, _, _, _, _ in points_b_norm:
            point_map[str(unit_id)] = (float(x), float(y))
        return point_map

    def build_attack_direction_map_from_point_map(
        frame_targets: Mapping[str, str],
        point_map: Mapping[str, tuple[float, float]],
    ) -> dict[str, tuple[float, float]]:
        if not frame_targets:
            return {}
        direction_map: dict[str, tuple[float, float]] = {}
        for attacker_id, defender_id in frame_targets.items():
            attacker = point_map.get(str(attacker_id))
            defender = point_map.get(str(defender_id))
            if attacker is None or defender is None:
                continue
            dx = defender[0] - attacker[0]
            dy = defender[1] - attacker[1]
            norm = math.sqrt((dx * dx) + (dy * dy))
            if norm <= 1e-12:
                continue
            direction_map[str(attacker_id)] = (dx / norm, dy / norm)
        return direction_map

    def build_target_segments_from_point_map(
        frame_targets: Mapping[str, str],
        point_map: Mapping[str, tuple[float, float]],
    ) -> list[tuple[tuple[float, float], tuple[float, float]]]:
        if not frame_targets:
            return []
        segments: list[tuple[tuple[float, float], tuple[float, float]]] = []
        for attacker_id, defender_id in frame_targets.items():
            attacker = point_map.get(str(attacker_id))
            defender = point_map.get(str(defender_id))
            if attacker is None or defender is None:
                continue
            dx = defender[0] - attacker[0]
            dy = defender[1] - attacker[1]
            if (dx * dx) + (dy * dy) <= 1e-12:
                continue
            segments.append(((attacker[0], attacker[1]), (defender[0], defender[1])))
        return segments

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
        point_map = build_frame_point_map(points_a_norm, points_b_norm) if needs_target_geometry and target_map else {}
        attack_direction_map = (
            build_attack_direction_map_from_point_map(target_map, point_map)
            if (needs_attack_direction_map and point_map)
            else {}
        )
        target_segments = (
            build_target_segments_from_point_map(target_map, point_map)
            if (needs_target_segments and point_map)
            else []
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
            if value > 1.0:
                value = 1.0
            elif value < -1.0:
                value = -1.0
        return value

    canonical_cohesion_series_a = [float(v) for v in trajectory.get("A", [])]
    canonical_cohesion_series_b = [float(v) for v in trajectory.get("B", [])]
    if extended_plot_mode and observer_shadow_ready:
        cohesion_series_a = shadow_cohesion_a
        cohesion_series_b = shadow_cohesion_b
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

    # Formation diagnostics derived from battlefield geometry per frame.
    ar_series_a = [float("nan")] * len(ticks)
    ar_series_b = [float("nan")] * len(ticks)
    wedge_series_a = [float("nan")] * len(ticks)
    wedge_series_b = [float("nan")] * len(ticks)
    split_series_a = [float("nan")] * len(ticks)
    split_series_b = [float("nan")] * len(ticks)
    if plot_panel_enabled and prepared_frames:
        for frame in prepared_frames:
            tick_value = int(frame.get("tick", 0))
            if tick_value < 1 or tick_value > len(ticks):
                continue
            idx = tick_value - 1
            points_a_xy = [(float(x), float(y)) for _, x, y, _, _, _, _ in frame.get("A_norm", [])]
            points_b_xy = [(float(x), float(y)) for _, x, y, _, _, _, _ in frame.get("B_norm", [])]
            m_a = _compute_formation_metrics_xy(points_a_xy, points_b_xy, angle_bins=12)
            m_b = _compute_formation_metrics_xy(points_b_xy, points_a_xy, angle_bins=12)
            ar_series_a[idx] = float(m_a.get("AR_forward", m_a.get("AR", float("nan"))))
            ar_series_b[idx] = float(m_b.get("AR_forward", m_b.get("AR", float("nan"))))
            wedge_series_a[idx] = float(m_a.get("wedge_ratio", float("nan")))
            wedge_series_b[idx] = float(m_b.get("wedge_ratio", float("nan")))
            split_series_a[idx] = float(m_a.get("split_separation", float("nan")))
            split_series_b[idx] = float(m_b.get("split_separation", float("nan")))

    shape_metric_alive_floor_raw = _cfg(viz_settings, "shape_metric_alive_floor", 0)
    try:
        shape_metric_alive_floor = int(shape_metric_alive_floor_raw)
    except (TypeError, ValueError):
        shape_metric_alive_floor = 0
    if shape_metric_alive_floor < 0:
        shape_metric_alive_floor = 0
    if shape_metric_alive_floor > 0:
        for idx in range(len(ticks)):
            alive_a_tick = int(alive_trajectory["A"][idx]) if idx < len(alive_trajectory["A"]) else 0
            alive_b_tick = int(alive_trajectory["B"][idx]) if idx < len(alive_trajectory["B"]) else 0
            if alive_a_tick < shape_metric_alive_floor:
                ar_series_a[idx] = float("nan")
                wedge_series_a[idx] = float("nan")
            if alive_b_tick < shape_metric_alive_floor:
                ar_series_b[idx] = float("nan")
                wedge_series_b[idx] = float("nan")

    shape_clip_enabled = bool(_cfg(viz_settings, "shape_metric_clip_enabled", True))
    shape_clip_bounds_raw = _cfg(
        viz_settings,
        "shape_metric_clip_bounds",
        {
            "ar": [0.0, 5.0],
            "wedge_ratio": [0.0, 3.0],
        },
    )
    if not isinstance(shape_clip_bounds_raw, Mapping):
        shape_clip_bounds_raw = {}

    def _parse_clip_bounds(key: str, default_low: float, default_high: float) -> tuple[float, float]:
        raw = shape_clip_bounds_raw.get(key, [default_low, default_high])
        if isinstance(raw, Sequence) and len(raw) >= 2:
            try:
                low = float(raw[0])
                high = float(raw[1])
            except (TypeError, ValueError):
                low, high = default_low, default_high
        else:
            low, high = default_low, default_high
        if not (math.isfinite(low) and math.isfinite(high) and low < high):
            return (default_low, default_high)
        return (low, high)

    ar_clip_low, ar_clip_high = _parse_clip_bounds("ar", 0.0, 3.0)
    wedge_clip_low, wedge_clip_high = _parse_clip_bounds("wedge_ratio", 0.0, 3.0)

    def _clip_series(values: Sequence[float], low: float, high: float) -> list[float]:
        out: list[float] = []
        for value in values:
            fv = float(value)
            if not math.isfinite(fv):
                out.append(float("nan"))
                continue
            if fv < low:
                out.append(low)
            elif fv > high:
                out.append(high)
            else:
                out.append(fv)
        return out

    if shape_clip_enabled:
        ar_plot_a = _clip_series(ar_series_a, ar_clip_low, ar_clip_high)
        ar_plot_b = _clip_series(ar_series_b, ar_clip_low, ar_clip_high)
        wedge_plot_a = _clip_series(wedge_series_a, wedge_clip_low, wedge_clip_high)
        wedge_plot_b = _clip_series(wedge_series_b, wedge_clip_low, wedge_clip_high)
    else:
        ar_plot_a = list(ar_series_a)
        ar_plot_b = list(ar_series_b)
        wedge_plot_a = list(wedge_series_a)
        wedge_plot_b = list(wedge_series_b)

    shape_axis_quantiles_raw = _cfg(viz_settings, "shape_metric_axis_quantiles", [0.0, 1.0])
    if (
        isinstance(shape_axis_quantiles_raw, Sequence)
        and len(shape_axis_quantiles_raw) >= 2
    ):
        try:
            shape_q_low = float(shape_axis_quantiles_raw[0])
            shape_q_high = float(shape_axis_quantiles_raw[1])
        except (TypeError, ValueError):
            shape_q_low = 0.0
            shape_q_high = 1.0
    else:
        shape_q_low = 0.0
        shape_q_high = 1.0
    if not (0.0 <= shape_q_low < shape_q_high <= 1.0):
        shape_q_low = 0.0
        shape_q_high = 1.0

    runtime_series = {
        "ar_a": _smooth_plot_series(ar_plot_a),
        "ar_b": _smooth_plot_series(ar_plot_b),
        "wedge_a": _smooth_plot_series(wedge_plot_a),
        "wedge_b": _smooth_plot_series(wedge_plot_b),
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

    if extended_plot_mode and observer_shadow_ready:
        cohesion_axis_ylabel = "Coh_v3"
    else:
        cohesion_axis_ylabel = "Coh_v2"
    wedge_axis_ylabel = "IntermixCov"
    front_curvature_axis_ylabel = "FrontCurv"
    center_wing_parallel_share_axis_ylabel = "C_W_PShare"
    split_axis_ylabel = "SplitSep"
    fire_efficiency_axis_ylabel = "FireEff"
    loss_rate_axis_ylabel = "LossRate"
    collapse_signal_axis_ylabel = "CollapseSig"

    def apply_time_axis_label(ax: plt.Axes) -> None:
        ax.set_xlabel("t", fontsize=plot_label_fontsize, labelpad=0.0)
        ax.xaxis.set_label_coords(1.015, -0.035)
        ax.xaxis.label.set_horizontalalignment("left")

    plot_legend_axes: list[plt.Axes] = []

    def apply_plot_legend(ax: plt.Axes) -> None:
        ax.legend(fontsize=plot_legend_fontsize, loc="best")
        plot_legend_axes.append(ax)

    alive_line_a, = alive_ax.plot(ticks, alive_trajectory["A"], label="A", color=fleet_a_color)
    alive_line_b, = alive_ax.plot(ticks, alive_trajectory["B"], label="B", color=fleet_b_color)
    apply_time_axis_label(alive_ax)
    alive_ax.set_ylabel("Alive", fontsize=plot_label_fontsize)
    alive_ax.tick_params(axis="both", which="major", labelsize=plot_tick_fontsize)
    apply_plot_legend(alive_ax)

    fire_efficiency_line_a, = fire_efficiency_ax.plot(
        ticks,
        runtime_series["fire_efficiency_a"],
        label="A",
        color=fleet_a_color,
    )
    fire_efficiency_line_b, = fire_efficiency_ax.plot(
        ticks,
        runtime_series["fire_efficiency_b"],
        label="B",
        color=fleet_b_color,
    )
    apply_time_axis_label(fire_efficiency_ax)
    fire_efficiency_ax.set_ylabel(fire_efficiency_axis_ylabel, fontsize=plot_label_fontsize)
    fire_efficiency_ax.tick_params(axis="both", which="major", labelsize=plot_tick_fontsize)
    apply_plot_legend(fire_efficiency_ax)

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
    collapse_signal_line_a, = collapse_signal_ax.plot(
        ticks,
        collapse_signal_series_a,
        label="A",
        color=fleet_a_color,
    )
    collapse_signal_line_b, = collapse_signal_ax.plot(
        ticks,
        collapse_signal_series_b,
        label="B",
        color=fleet_b_color,
    )
    apply_time_axis_label(collapse_signal_ax)
    collapse_signal_ax.set_ylabel(collapse_signal_axis_ylabel, fontsize=plot_label_fontsize)
    collapse_signal_ax.tick_params(axis="both", which="major", labelsize=plot_tick_fontsize)
    apply_plot_legend(collapse_signal_ax)

    split_line_a, = split_ax.plot(ticks, runtime_series["split_a"], label="A", color=fleet_a_color)
    split_line_b, = split_ax.plot(ticks, runtime_series["split_b"], label="B", color=fleet_b_color)
    apply_time_axis_label(split_ax)
    split_ax.set_ylabel(split_axis_ylabel, fontsize=plot_label_fontsize)
    split_ax.tick_params(axis="both", which="major", labelsize=plot_tick_fontsize)
    apply_plot_legend(split_ax)

    loss_rate_line_a, = loss_rate_ax.plot(ticks, runtime_series["loss_rate_a"], label="A", color=fleet_a_color)
    loss_rate_line_b, = loss_rate_ax.plot(ticks, runtime_series["loss_rate_b"], label="B", color=fleet_b_color)
    apply_time_axis_label(loss_rate_ax)
    loss_rate_ax.set_ylabel(loss_rate_axis_ylabel, fontsize=plot_label_fontsize)
    loss_rate_ax.tick_params(axis="both", which="major", labelsize=plot_tick_fontsize)
    apply_plot_legend(loss_rate_ax)

    cohesion_line_a, = cohesion_ax.plot(ticks, cohesion_plot_series_a, label="A", color=fleet_a_color)
    cohesion_line_b, = cohesion_ax.plot(ticks, cohesion_plot_series_b, label="B", color=fleet_b_color)
    apply_time_axis_label(cohesion_ax)
    cohesion_ax.set_ylabel(cohesion_axis_ylabel, fontsize=plot_label_fontsize)
    cohesion_ax.tick_params(axis="both", which="major", labelsize=plot_tick_fontsize)
    apply_plot_legend(cohesion_ax)

    front_curvature_line_a, = front_curvature_ax.plot(
        ticks, runtime_series["front_curvature_a"], label="A", color=fleet_a_color
    )
    front_curvature_line_b, = front_curvature_ax.plot(
        ticks, runtime_series["front_curvature_b"], label="B", color=fleet_b_color
    )
    apply_time_axis_label(front_curvature_ax)
    front_curvature_ax.set_ylabel(front_curvature_axis_ylabel, fontsize=plot_label_fontsize)
    front_curvature_ax.tick_params(axis="both", which="major", labelsize=plot_tick_fontsize)
    apply_plot_legend(front_curvature_ax)

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

    center_wing_parallel_share_line_a, = center_wing_parallel_share_ax.plot(
        ticks, runtime_series["center_wing_parallel_share_a"], label="A", color=fleet_a_color
    )
    center_wing_parallel_share_line_b, = center_wing_parallel_share_ax.plot(
        ticks, runtime_series["center_wing_parallel_share_b"], label="B", color=fleet_b_color
    )
    apply_time_axis_label(center_wing_parallel_share_ax)
    center_wing_parallel_share_ax.set_ylabel(center_wing_parallel_share_axis_ylabel, fontsize=plot_label_fontsize)
    center_wing_parallel_share_ax.tick_params(axis="both", which="major", labelsize=plot_tick_fontsize)
    apply_plot_legend(center_wing_parallel_share_ax)

    observer_series_lines = [
        fire_efficiency_line_a,
        fire_efficiency_line_b,
        wedge_line_a,
        center_wing_parallel_share_line_a,
        center_wing_parallel_share_line_b,
        split_line_a,
        split_line_b,
        loss_rate_line_a,
        loss_rate_line_b,
        cohesion_line_a,
        cohesion_line_b,
        collapse_signal_line_a,
        collapse_signal_line_b,
        front_curvature_line_a,
        front_curvature_line_b,
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
        apply_observer_axis_disabled_style(fire_efficiency_ax, "slot_03")
        apply_observer_axis_disabled_style(loss_rate_ax, "slot_04")
        apply_observer_axis_disabled_style(cohesion_ax, "slot_05")
        apply_observer_axis_disabled_style(collapse_signal_ax, "slot_06")
        apply_observer_axis_disabled_style(split_ax, "slot_07")
        apply_observer_axis_disabled_style(front_curvature_ax, "slot_08")
        apply_observer_axis_disabled_style(wedge_ax, "slot_09")
        apply_observer_axis_disabled_style(center_wing_parallel_share_ax, "slot_10")

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

    freeze_plot_legends()

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
    loss_rate_ax.set_ylim(*compute_axis_limits_many(runtime_series["loss_rate_a"], runtime_series["loss_rate_b"]))
    cohesion_ax.set_ylim(*compute_axis_limits_many(cohesion_series_a, cohesion_series_b))
    collapse_signal_ax.set_ylim(*compute_axis_limits_many(collapse_signal_series_a, collapse_signal_series_b))
    split_ax.set_ylim(1.5, 2.5)
    front_curvature_ax.set_ylim(*compute_axis_limits_many(runtime_series["front_curvature_a"], runtime_series["front_curvature_b"]))
    # IntermixCoverage is a prototype-grade diagnostic for broad hostile overlap.
    # Keep the full fraction range so different fixtures remain directly comparable.
    wedge_ax.set_ylim(0.0, 1.0)
    center_wing_parallel_share_ax.set_ylim(-1.0, 1.0)

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
        (alive_line_a, alive_trajectory["A"]),
        (alive_line_b, alive_trajectory["B"]),
        (fire_efficiency_line_a, runtime_series["fire_efficiency_a"]),
        (fire_efficiency_line_b, runtime_series["fire_efficiency_b"]),
        (loss_rate_line_a, runtime_series["loss_rate_a"]),
        (loss_rate_line_b, runtime_series["loss_rate_b"]),
        (cohesion_line_a, cohesion_series_a),
        (cohesion_line_b, cohesion_series_b),
        (collapse_signal_line_a, collapse_signal_series_a),
        (collapse_signal_line_b, collapse_signal_series_b),
        (split_line_a, runtime_series["split_a"]),
        (split_line_b, runtime_series["split_b"]),
        (front_curvature_line_a, runtime_series["front_curvature_a"]),
        (front_curvature_line_b, runtime_series["front_curvature_b"]),
        (wedge_line_a, runtime_series["hostile_intermix_coverage"]),
        (center_wing_parallel_share_line_a, runtime_series["center_wing_parallel_share_a"]),
        (center_wing_parallel_share_line_b, runtime_series["center_wing_parallel_share_b"]),
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

    export_video_cfg_local = export_video_cfg_layout
    export_video_enabled = export_video_enabled_layout
    if export_video_enabled:
        if anim is None:
            raise RuntimeError("Video export requires captured animation frames (animate=true).")
        ffmpeg_path = _resolve_ffmpeg_path()
        if not ffmpeg_path:
            raise RuntimeError(
                "Video export enabled but ffmpeg not found. Install ffmpeg or imageio-ffmpeg."
            )
        raw_output_path = str(_cfg(export_video_cfg_local, "output_path", "analysis/exports/videos"))
        output_path = Path(raw_output_path)
        if not output_path.is_absolute():
            output_path = (Path.cwd() / output_path).resolve()
        output_path_is_final = bool(_cfg(export_video_cfg_local, "output_path_is_final", False))
        if not output_path_is_final:
            stem_has_timestamp = re.search(r"_\d{8}_\d{6}$", output_path.stem) is not None
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if output_path.suffix:
                if not stem_has_timestamp:
                    output_path = output_path.with_name(f"{output_path.stem}_{timestamp}{output_path.suffix}")
            else:
                output_path = output_path / f"test_run_v1_0_{timestamp}.mp4"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        default_fps = max(1, int(round(1000.0 / max(1, frame_interval_ms))))
        fps = max(1, int(_cfg(export_video_cfg_local, "fps", default_fps)))
        codec = str(_cfg(export_video_cfg_local, "codec", "libx264"))
        bitrate_kbps = max(200, int(_cfg(export_video_cfg_local, "bitrate_kbps", 2400)))
        full_plot = export_full_plot_layout
        width_px = export_width_px_layout
        height_px = export_height_px_layout
        dpi = export_dpi_layout

        mpl.rcParams["animation.ffmpeg_path"] = ffmpeg_path
        extra_args = [
            "-pix_fmt",
            "yuv420p",
            "-vf",
            f"scale={width_px}:{height_px}:flags=lanczos",
        ]
        writer = FFMpegWriter(
            fps=fps,
            codec=codec,
            bitrate=bitrate_kbps,
            extra_args=extra_args,
        )
        original_size_inches = tuple(fig.get_size_inches())
        if not full_plot:
            for ax in fig.axes:
                if ax is battle_ax:
                    continue
                ax.set_visible(False)
            battle_ax.set_position([0.0, 0.0, 1.0, 1.0])
        print(f"[viz] export_video enabled: {output_path}")
        print(
            f"[viz] export writer=ffmpeg, fps={fps}, codec={codec}, bitrate_kbps={bitrate_kbps}, "
            f"size={width_px}x{height_px}, dpi={dpi}, full_plot={full_plot}"
        )
        try:
            fig.set_size_inches(width_px / dpi, height_px / dpi, forward=True)
            try:
                fig.canvas.draw()
            except Exception:
                pass
            anim.save(
                str(output_path),
                writer=writer,
                dpi=dpi,
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
