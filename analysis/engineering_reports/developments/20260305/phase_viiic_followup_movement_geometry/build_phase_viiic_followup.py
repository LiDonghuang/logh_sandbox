import csv
import json
import math
from collections import defaultdict
from pathlib import Path

HAS_MATPLOTLIB = True
try:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except ModuleNotFoundError:
    HAS_MATPLOTLIB = False

PROJECT_ROOT = Path(__file__).resolve().parents[5]
ANALYSIS_DIR = PROJECT_ROOT / "analysis"

import sys

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(ANALYSIS_DIR) not in sys.path:
    sys.path.insert(0, str(ANALYSIS_DIR))

from test_run.test_run_v1_0 import (
    SimulationBoundaryConfig,
    SimulationContactConfig,
    SimulationExecutionConfig,
    SimulationMovementConfig,
    SimulationObserverConfig,
    SimulationRuntimeConfig,
    TestModeEngineTickSkeleton,
    build_initial_state,
    compute_formation_snapshot_metrics,
    get_battlefield_setting,
    get_fleet_setting,
    get_run_control_setting,
    get_runtime_setting,
    get_unit_setting,
    load_json_file,
    run_simulation,
    to_personality_parameters,
)


FR_LEVELS = [2, 5, 8]
MB_LEVELS = [2, 5, 8]
PARAM_KEYS = [
    "force_concentration_ratio",
    "formation_rigidity",
    "mobility_bias",
    "offense_defense_weight",
    "perception_radius",
    "pursuit_drive",
    "retreat_threshold",
    "risk_appetite",
    "targeting_logic",
    "time_preference",
]


def parse_float(value, default=float("nan")):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def parse_int_tick(value):
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.upper() == "N/A":
        return None
    try:
        tick = int(float(text))
    except (TypeError, ValueError):
        return None
    return tick if tick >= 1 else None


def finite(values):
    out = []
    for v in values:
        if v is None:
            continue
        if isinstance(v, float) and math.isnan(v):
            continue
        out.append(float(v))
    return out


def mean_or_nan(values):
    vals = finite(values)
    if not vals:
        return float("nan")
    return sum(vals) / float(len(vals))


def quantile(values, q):
    vals = sorted(finite(values))
    if not vals:
        return float("nan")
    if len(vals) == 1:
        return vals[0]
    q = max(0.0, min(1.0, float(q)))
    pos = (len(vals) - 1) * q
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return vals[lo]
    w = pos - lo
    return vals[lo] * (1.0 - w) + vals[hi] * w


def normalize_vector_dict(vector):
    out = {}
    for key in PARAM_KEYS:
        out[key] = float(vector[key])
    return out


def vector_to_archetype_dict(name, vector):
    vec = normalize_vector_dict(vector)
    out = {
        "name": str(name),
        "disp_name_EN": str(name),
        "disp_name_ZH": str(name),
        "full_name_EN": f"{name} Fleet",
        "full_name_ZH": str(name),
    }
    out.update(vec)
    return out


def extract_points(frame, fleet_id):
    points = []
    for item in frame.get(fleet_id, []):
        if len(item) >= 3:
            points.append((float(item[1]), float(item[2])))
    return points


def distance_stats(points):
    if not points:
        return (float("nan"), float("nan"), float("nan"), float("nan"))
    cx = sum(p[0] for p in points) / float(len(points))
    cy = sum(p[1] for p in points) / float(len(points))
    dists = []
    for x, y in points:
        dists.append(math.hypot(x - cx, y - cy))
    return (
        quantile(dists, 0.50),
        quantile(dists, 0.90),
        quantile(dists, 0.95),
        max(dists),
    )


def neighbor_and_connectivity(points, link_radius, low_neighbor_threshold=2):
    n = len(points)
    if n <= 1:
        return (0.0, 1.0 if n == 1 else float("nan"))
    r2 = float(link_radius) * float(link_radius)
    deg = [0] * n
    parent = list(range(n))
    size = [1] * n

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra = find(a)
        rb = find(b)
        if ra == rb:
            return
        if size[ra] < size[rb]:
            ra, rb = rb, ra
        parent[rb] = ra
        size[ra] += size[rb]

    for i in range(n):
        xi, yi = points[i]
        for j in range(i + 1, n):
            xj, yj = points[j]
            dx = xi - xj
            dy = yi - yj
            if (dx * dx) + (dy * dy) <= r2:
                deg[i] += 1
                deg[j] += 1
                union(i, j)

    low_neighbor = sum(1 for d in deg if d <= int(low_neighbor_threshold))
    root_sizes = defaultdict(int)
    for i in range(n):
        root_sizes[find(i)] += 1
    lcc = max(root_sizes.values()) if root_sizes else 0
    return (
        float(low_neighbor) / float(n),
        float(lcc) / float(n),
    )


def first_contact_tick(combat_telemetry):
    contact = combat_telemetry.get("in_contact_count", [])
    for idx, value in enumerate(contact, start=1):
        if int(value) > 0:
            return idx
    return None


def to_heatmap_matrix(rows_by_cell):
    matrix = []
    for mb in MB_LEVELS:
        row = []
        for fr in FR_LEVELS:
            row.append(rows_by_cell.get((fr, mb), float("nan")))
        matrix.append(row)
    return matrix


def save_heatmap(matrix, title, out_path, cbar_label, fmt="{:.1f}", vmin=None, vmax=None):
    if not HAS_MATPLOTLIB:
        return
    fig, ax = plt.subplots(figsize=(6.0, 4.8), dpi=140)
    im = ax.imshow(matrix, origin="lower", aspect="auto", vmin=vmin, vmax=vmax)
    ax.set_xticks(range(len(FR_LEVELS)))
    ax.set_yticks(range(len(MB_LEVELS)))
    ax.set_xticklabels([f"FR={v}" for v in FR_LEVELS])
    ax.set_yticklabels([f"MB={v}" for v in MB_LEVELS])
    ax.set_title(title)
    for y in range(len(MB_LEVELS)):
        for x in range(len(FR_LEVELS)):
            val = matrix[y][x]
            if not (isinstance(val, float) and math.isnan(val)):
                ax.text(x, y, fmt.format(val), ha="center", va="center", color="white", fontsize=9)
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label(cbar_label)
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def save_matrix_csv(matrix, out_path):
    with out_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["MB\\FR"] + [str(v) for v in FR_LEVELS])
        for row_idx, mb in enumerate(MB_LEVELS):
            values = []
            for val in matrix[row_idx]:
                if isinstance(val, float) and math.isnan(val):
                    values.append("")
                else:
                    values.append(f"{val:.6f}")
            writer.writerow([str(mb)] + values)


def main():
    out_dir = Path(__file__).resolve().parent
    base_run_table = (
        PROJECT_ROOT
        / "analysis"
        / "engineering_reports"
        / "developments"
        / "20260305"
        / "phase_viiiB3_FR_MB_doe_rerun"
        / "doe_b3_run_table.csv"
    )
    settings_path = PROJECT_ROOT / "analysis" / "test_run_v1_0.settings.json"
    archetypes_path = PROJECT_ROOT / "analysis" / "archetypes_v1_5.json"

    settings = load_json_file(settings_path)
    archetypes = load_json_file(archetypes_path)

    with base_run_table.open("r", encoding="utf-8", newline="") as f:
        run_rows = list(csv.DictReader(f))

    # Runtime constants from current test settings (analysis-only replay).
    fleet_size = int(get_fleet_setting(settings, "initial_fleet_size", 100))
    aspect_ratio = float(get_fleet_setting(settings, "initial_fleet_aspect_ratio", 2.0))
    unit_spacing = float(get_battlefield_setting(settings, "min_unit_spacing", 2.0))
    unit_speed = float(get_unit_setting(settings, "unit_speed", 1.0))
    unit_max_hp = float(get_unit_setting(settings, "unit_max_hit_points", 100.0))
    arena_size = float(get_battlefield_setting(settings, "arena_size", 200.0))
    attack_range = float(get_unit_setting(settings, "attack_range", get_runtime_setting(settings, "attack_range", 5.0)))
    damage_per_tick = float(
        get_unit_setting(settings, "damage_per_tick", get_runtime_setting(settings, "damage_per_tick", 1.0))
    )
    fire_quality_alpha = float(get_runtime_setting(settings, "fire_quality_alpha", 0.1))
    contact_hysteresis_h = float(get_runtime_setting(settings, "contact_hysteresis_h", 0.1))
    fsr_strength = float(get_runtime_setting(settings, "fsr_strength", 0.1))
    ch_enabled = contact_hysteresis_h > 0.0
    fsr_enabled = fsr_strength > 0.0
    boundary_enabled = bool(get_runtime_setting(settings, "boundary_enabled", False))
    bridge_theta_split = float(get_runtime_setting(settings, "bridge_theta_split", 1.715))
    bridge_theta_env = float(get_runtime_setting(settings, "bridge_theta_env", 0.583))
    bridge_sustain_ticks = max(1, int(get_runtime_setting(settings, "bridge_sustain_ticks", 20)))
    collapse_shadow_theta_conn_default = float(get_runtime_setting(settings, "collapse_shadow_theta_conn_default", 0.10))
    collapse_shadow_theta_coh_default = float(get_runtime_setting(settings, "collapse_shadow_theta_coh_default", 0.98))
    collapse_shadow_theta_force_default = float(get_runtime_setting(settings, "collapse_shadow_theta_force_default", 0.95))
    collapse_shadow_theta_attr_default = float(get_runtime_setting(settings, "collapse_shadow_theta_attr_default", 0.10))
    collapse_shadow_attrition_window = max(1, int(get_runtime_setting(settings, "collapse_shadow_attrition_window", 20)))
    collapse_shadow_sustain_ticks = max(1, int(get_runtime_setting(settings, "collapse_shadow_sustain_ticks", 10)))
    collapse_shadow_min_conditions = min(4, max(1, int(get_runtime_setting(settings, "collapse_shadow_min_conditions", 2))))

    geometry_rows = []
    stray_rows = []
    link_radius = 3.0 * unit_spacing

    for idx, row in enumerate(run_rows, start=1):
        test_vec = json.loads(row["injected_test_vector"])
        opp_vec = json.loads(row["injected_opponent_vector"])

        fleet_a_data = vector_to_archetype_dict(str(row["run_id"]) + "_A", test_vec)
        fleet_b_data = vector_to_archetype_dict(str(row["opponent_name"]), opp_vec)

        state = build_initial_state(
            fleet_a_params=to_personality_parameters(fleet_a_data),
            fleet_b_params=to_personality_parameters(fleet_b_data),
            fleet_size=fleet_size,
            aspect_ratio=aspect_ratio,
            unit_spacing=unit_spacing,
            unit_speed=unit_speed,
            unit_max_hit_points=unit_max_hp,
            arena_size=arena_size,
        )

        execution_cfg = SimulationExecutionConfig(
            steps=-1,
            capture_positions=True,
            frame_stride=10,
            include_target_lines=False,
            print_tick_summary=False,
            plot_diagnostics_enabled=False,
        )
        runtime_cfg = SimulationRuntimeConfig(
            decision_source=str(row.get("runtime_decision_source_effective", "v2")),
            movement_model=str(row.get("movement_model", "v1")),
            movement=SimulationMovementConfig(),
            contact=SimulationContactConfig(
                attack_range=attack_range,
                damage_per_tick=damage_per_tick,
                separation_radius=unit_spacing,
                fire_quality_alpha=fire_quality_alpha,
                contact_hysteresis_h=contact_hysteresis_h,
                ch_enabled=ch_enabled,
                fsr_enabled=fsr_enabled,
                fsr_strength=fsr_strength,
            ),
            boundary=SimulationBoundaryConfig(enabled=boundary_enabled),
        )
        observer_cfg = SimulationObserverConfig(
            enabled=True,
            bridge_theta_split=bridge_theta_split,
            bridge_theta_env=bridge_theta_env,
            bridge_sustain_ticks=bridge_sustain_ticks,
            collapse_shadow_theta_conn_default=collapse_shadow_theta_conn_default,
            collapse_shadow_theta_coh_default=collapse_shadow_theta_coh_default,
            collapse_shadow_theta_force_default=collapse_shadow_theta_force_default,
            collapse_shadow_theta_attr_default=collapse_shadow_theta_attr_default,
            collapse_shadow_attrition_window=collapse_shadow_attrition_window,
            collapse_shadow_sustain_ticks=collapse_shadow_sustain_ticks,
            collapse_shadow_min_conditions=collapse_shadow_min_conditions,
        )
        (
            final_state,
            _trajectory,
            _alive_trajectory,
            _fleet_size_trajectory,
            _observer_telemetry,
            combat_telemetry,
            _bridge_telemetry,
            _collapse_shadow_telemetry,
            position_frames,
        ) = run_simulation(
            initial_state=state,
            engine_cls=TestModeEngineTickSkeleton,
            execution_cfg=execution_cfg,
            runtime_cfg=runtime_cfg,
            observer_cfg=observer_cfg,
        )

        ar_a = []
        wedge_a = []
        split_a = []
        env_a = []

        dist_p95_a = []
        low_neighbor_ratio_a = []
        lcc_ratio_a = []

        for frame in position_frames:
            points_a = extract_points(frame, "A")
            points_b = extract_points(frame, "B")
            m_a = compute_formation_snapshot_metrics(points_a, points_b, angle_bins=12)
            ar_a.append(float(m_a.get("AR", float("nan"))))
            wedge_a.append(float(m_a.get("wedge_ratio", float("nan"))))
            split_a.append(float(m_a.get("split_separation", float("nan"))))
            env_a.append(float(m_a.get("angle_coverage", float("nan"))))

            if int(float(row["cell_FR"])) == 8:
                _, _, p95, _ = distance_stats(points_a)
                low_ratio, lcc_ratio = neighbor_and_connectivity(points_a, link_radius=link_radius)
                dist_p95_a.append(p95)
                low_neighbor_ratio_a.append(low_ratio)
                lcc_ratio_a.append(lcc_ratio)

        run_metric = {
            "run_id": row["run_id"],
            "movement_model": row["movement_model"],
            "cell_FR": int(float(row["cell_FR"])),
            "cell_MB": int(float(row["cell_MB"])),
            "cell_PD": int(float(row["cell_PD"])),
            "opponent_name": row["opponent_name"],
            "winner": row["winner"],
            "end_tick_replay": int(final_state.tick),
            "first_contact_tick_replay": first_contact_tick(combat_telemetry),
            "first_contact_tick_b3": parse_int_tick(row.get("first_contact_tick")),
            "first_kill_tick_b3": parse_int_tick(row.get("first_kill_tick")),
            "tactical_cut_tick_T_b3": parse_int_tick(row.get("tactical_cut_tick_T")),
            "tactical_pocket_tick_T_b3": parse_int_tick(row.get("tactical_pocket_tick_T")),
            "ar_p50_A": quantile(ar_a, 0.50),
            "ar_p90_A": quantile(ar_a, 0.90),
            "ar_max_A": quantile(ar_a, 1.00),
            "wedge_p10_A": quantile(wedge_a, 0.10),
            "wedge_p50_A": quantile(wedge_a, 0.50),
            "wedge_p90_A": quantile(wedge_a, 0.90),
            "split_p90_A": quantile(split_a, 0.90),
            "angle_coverage_p90_A": quantile(env_a, 0.90),
        }
        geometry_rows.append(run_metric)

        if int(float(row["cell_FR"])) == 8:
            stray_rows.append(
                {
                    "run_id": row["run_id"],
                    "movement_model": row["movement_model"],
                    "cell_FR": int(float(row["cell_FR"])),
                    "cell_MB": int(float(row["cell_MB"])),
                    "opponent_name": row["opponent_name"],
                    "distance_p95_A_mean": mean_or_nan(dist_p95_a),
                    "distance_p95_A_p90": quantile(dist_p95_a, 0.90),
                    "low_neighbor_ratio_A_mean": mean_or_nan(low_neighbor_ratio_a),
                    "lcc_ratio_A_p10": quantile(lcc_ratio_a, 0.10),
                }
            )

        if idx % 12 == 0:
            print(f"[progress] replay {idx}/{len(run_rows)}")

    geometry_csv = out_dir / "movement_v1_vs_v3a_geometry_comparison.csv"
    with geometry_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "movement_model",
                "cell_FR",
                "cell_MB",
                "cell_PD",
                "n_runs",
                "win_rate_A",
                "first_contact_tick_mean",
                "tactical_cut_tick_T_mean",
                "tactical_pocket_tick_T_mean",
                "ar_p90_A_mean",
                "wedge_p50_A_mean",
                "split_p90_A_mean",
                "angle_coverage_p90_A_mean",
            ],
        )
        writer.writeheader()
        grouped = defaultdict(list)
        for row in geometry_rows:
            grouped[(row["movement_model"], row["cell_FR"], row["cell_MB"], row["cell_PD"])].append(row)
        for key in sorted(grouped.keys()):
            model, fr, mb, pd = key
            rows = grouped[key]
            n = len(rows)
            writer.writerow(
                {
                    "movement_model": model,
                    "cell_FR": fr,
                    "cell_MB": mb,
                    "cell_PD": pd,
                    "n_runs": n,
                    "win_rate_A": sum(1 for r in rows if str(r["winner"]) == "A") / float(n),
                    "first_contact_tick_mean": mean_or_nan([r["first_contact_tick_b3"] for r in rows]),
                    "tactical_cut_tick_T_mean": mean_or_nan([r["tactical_cut_tick_T_b3"] for r in rows]),
                    "tactical_pocket_tick_T_mean": mean_or_nan([r["tactical_pocket_tick_T_b3"] for r in rows]),
                    "ar_p90_A_mean": mean_or_nan([r["ar_p90_A"] for r in rows]),
                    "wedge_p50_A_mean": mean_or_nan([r["wedge_p50_A"] for r in rows]),
                    "split_p90_A_mean": mean_or_nan([r["split_p90_A"] for r in rows]),
                    "angle_coverage_p90_A_mean": mean_or_nan([r["angle_coverage_p90_A"] for r in rows]),
                }
            )

    stray_csv = out_dir / "high_fr_stray_diagnostics.csv"
    with stray_csv.open("w", encoding="utf-8", newline="") as f:
        if stray_rows:
            writer = csv.DictWriter(f, fieldnames=list(stray_rows[0].keys()))
            writer.writeheader()
            writer.writerows(stray_rows)

    # Heatmap prep from geometry rows and original B3 event ticks.
    by_model_cell = defaultdict(list)
    for row in geometry_rows:
        by_model_cell[(row["movement_model"], row["cell_FR"], row["cell_MB"])].append(row)

    def cell_metric_map(model, metric_name):
        out = {}
        for fr in FR_LEVELS:
            for mb in MB_LEVELS:
                rows = by_model_cell.get((model, fr, mb), [])
                if not rows:
                    out[(fr, mb)] = float("nan")
                    continue
                if metric_name == "win_rate":
                    out[(fr, mb)] = (
                        sum(1 for r in rows if str(r["winner"]) == "A") / float(len(rows)) * 100.0
                    )
                elif metric_name == "cut_tick":
                    out[(fr, mb)] = mean_or_nan([r["tactical_cut_tick_T_b3"] for r in rows])
                elif metric_name == "ar_p90":
                    out[(fr, mb)] = mean_or_nan([r["ar_p90_A"] for r in rows])
                else:
                    out[(fr, mb)] = float("nan")
        return out

    win_v1 = to_heatmap_matrix(cell_metric_map("v1", "win_rate"))
    win_v3a = to_heatmap_matrix(cell_metric_map("v3a", "win_rate"))
    cut_v1 = to_heatmap_matrix(cell_metric_map("v1", "cut_tick"))
    cut_v3a = to_heatmap_matrix(cell_metric_map("v3a", "cut_tick"))
    ar_v1 = to_heatmap_matrix(cell_metric_map("v1", "ar_p90"))
    ar_v3a = to_heatmap_matrix(cell_metric_map("v3a", "ar_p90"))

    def matrix_delta(a, b):
        out = []
        for y in range(len(a)):
            row = []
            for x in range(len(a[0])):
                va = a[y][x]
                vb = b[y][x]
                if (
                    isinstance(va, float)
                    and math.isnan(va)
                    or isinstance(vb, float)
                    and math.isnan(vb)
                ):
                    row.append(float("nan"))
                else:
                    row.append(vb - va)
            out.append(row)
        return out

    win_delta = matrix_delta(win_v1, win_v3a)
    cut_delta = matrix_delta(cut_v1, cut_v3a)
    ar_delta = matrix_delta(ar_v1, ar_v3a)

    save_heatmap(
        win_v1,
        "Win Rate Heatmap (A win %, v1)",
        out_dir / "heatmap_win_rate_A_v1.png",
        "A win rate (%)",
        fmt="{:.1f}",
        vmin=0.0,
        vmax=100.0,
    )
    save_heatmap(
        win_v3a,
        "Win Rate Heatmap (A win %, v3a)",
        out_dir / "heatmap_win_rate_A_v3a.png",
        "A win rate (%)",
        fmt="{:.1f}",
        vmin=0.0,
        vmax=100.0,
    )
    save_heatmap(
        win_delta,
        "Win Rate Delta Heatmap (v3a - v1)",
        out_dir / "heatmap_win_rate_delta_v3a_minus_v1.png",
        "Delta win rate (pp)",
        fmt="{:+.1f}",
    )
    save_heatmap(
        cut_v1,
        "Event Timing Heatmap (Cut_T mean, v1)",
        out_dir / "heatmap_cut_tick_T_v1.png",
        "Cut tick (mean)",
        fmt="{:.0f}",
    )
    save_heatmap(
        cut_v3a,
        "Event Timing Heatmap (Cut_T mean, v3a)",
        out_dir / "heatmap_cut_tick_T_v3a.png",
        "Cut tick (mean)",
        fmt="{:.0f}",
    )
    save_heatmap(
        cut_delta,
        "Event Timing Delta Heatmap (Cut_T, v3a - v1)",
        out_dir / "heatmap_cut_tick_T_delta_v3a_minus_v1.png",
        "Delta cut tick",
        fmt="{:+.0f}",
    )
    save_heatmap(
        ar_v1,
        "Geometry Heatmap (AR p90, A side, v1)",
        out_dir / "heatmap_ar_p90_A_v1.png",
        "AR p90",
        fmt="{:.2f}",
    )
    save_heatmap(
        ar_v3a,
        "Geometry Heatmap (AR p90, A side, v3a)",
        out_dir / "heatmap_ar_p90_A_v3a.png",
        "AR p90",
        fmt="{:.2f}",
    )
    save_heatmap(
        ar_delta,
        "Geometry Delta Heatmap (AR p90, v3a - v1)",
        out_dir / "heatmap_ar_p90_A_delta_v3a_minus_v1.png",
        "Delta AR p90",
        fmt="{:+.2f}",
    )

    # Always export matrix CSVs so diagnostics remain usable without matplotlib.
    save_matrix_csv(win_v1, out_dir / "heatmap_win_rate_A_v1.matrix.csv")
    save_matrix_csv(win_v3a, out_dir / "heatmap_win_rate_A_v3a.matrix.csv")
    save_matrix_csv(win_delta, out_dir / "heatmap_win_rate_delta_v3a_minus_v1.matrix.csv")
    save_matrix_csv(cut_v1, out_dir / "heatmap_cut_tick_T_v1.matrix.csv")
    save_matrix_csv(cut_v3a, out_dir / "heatmap_cut_tick_T_v3a.matrix.csv")
    save_matrix_csv(cut_delta, out_dir / "heatmap_cut_tick_T_delta_v3a_minus_v1.matrix.csv")
    save_matrix_csv(ar_v1, out_dir / "heatmap_ar_p90_A_v1.matrix.csv")
    save_matrix_csv(ar_v3a, out_dir / "heatmap_ar_p90_A_v3a.matrix.csv")
    save_matrix_csv(ar_delta, out_dir / "heatmap_ar_p90_A_delta_v3a_minus_v1.matrix.csv")

    # Anchor drift review for first six archetypes.
    first_six_names = list(archetypes.keys())[:6]
    b3_opp_vectors = {}
    for row in run_rows:
        name = row["opponent_name"]
        if name not in b3_opp_vectors:
            b3_opp_vectors[name] = normalize_vector_dict(json.loads(row["injected_opponent_vector"]))

    anchor_md_path = out_dir / "anchor_drift_review_first6.md"
    lines = []
    lines.append("# Anchor Drift Review - First Six Archetypes")
    lines.append("")
    lines.append("- Baseline for comparison: B3 injected opponent vectors (from `doe_b3_run_table.csv`).")
    lines.append("- Method note: B3 normalized opponent `FCR + other7` to `5`; only `FR/MB/PD` are valid drift anchors.")
    lines.append("- Current source: `archetypes/archetypes_v1_5.json`.")
    lines.append("")
    lines.append("| archetype | FR status | MB status | PD status | note |")
    lines.append("| --- | --- | --- | --- | --- |")
    for name in first_six_names:
        current = normalize_vector_dict(archetypes[name])
        baseline = b3_opp_vectors.get(name)
        if baseline is None:
            lines.append(f"| {name} | missing_in_b3 | missing_in_b3 | missing_in_b3 | baseline not found |")
            continue
        fr_ok = abs(float(current["formation_rigidity"]) - float(baseline["formation_rigidity"])) <= 1e-9
        mb_ok = abs(float(current["mobility_bias"]) - float(baseline["mobility_bias"])) <= 1e-9
        pd_ok = abs(float(current["pursuit_drive"]) - float(baseline["pursuit_drive"])) <= 1e-9
        lines.append(
            f"| {name} | {'stable' if fr_ok else 'changed'} | {'stable' if mb_ok else 'changed'} | "
            f"{'stable' if pd_ok else 'changed'} | B3-valid check on FR/MB/PD only |"
        )
    lines.append("")
    anchor_md_path.write_text("\n".join(lines), encoding="utf-8")

    maps_md = out_dir / "fr_mb_interaction_maps.md"
    maps_md.write_text(
        "\n".join(
            [
                "# FR x MB Interaction Maps (B3 Follow-up)",
                "",
                "## Win-rate Heatmaps",
                "- `heatmap_win_rate_A_v1.png`",
                "- `heatmap_win_rate_A_v3a.png`",
                "- `heatmap_win_rate_delta_v3a_minus_v1.png`",
                "",
                "## Event Timing Heatmaps (Cut_T)",
                "- `heatmap_cut_tick_T_v1.png`",
                "- `heatmap_cut_tick_T_v3a.png`",
                "- `heatmap_cut_tick_T_delta_v3a_minus_v1.png`",
                "",
                "## Geometry Heatmaps (AR p90, A side)",
                "- `heatmap_ar_p90_A_v1.png`",
                "- `heatmap_ar_p90_A_v3a.png`",
                "- `heatmap_ar_p90_A_delta_v3a_minus_v1.png`",
                "",
                "## CSV Fallback (always exported)",
                "- `*.matrix.csv` files mirror all heatmaps in numeric matrix form.",
                "",
                "Data source:",
                "- outcome/event: `doe_b3_run_table.csv`",
                "- geometry: replayed runs from B3 injection vectors via `run_simulation` (observer-only)",
            ]
        ),
        encoding="utf-8",
    )

    summary_md = out_dir / "phase_viiic_followup_summary.md"
    summary_md.write_text(
        "\n".join(
            [
                "# Phase VIII-C Follow-up Summary",
                "",
                "## Scope",
                "- FR x MB interaction maps from B3.",
                "- Movement geometry diagnostics (v1 vs v3a).",
                "- High-FR stray diagnostics (observer-only).",
                "- First-six archetype anchor drift review.",
                "",
                "## Outputs",
                "- `fr_mb_interaction_maps.md`",
                "- `movement_v1_vs_v3a_geometry_comparison.csv`",
                "- `high_fr_stray_diagnostics.csv`",
                "- `anchor_drift_review_first6.md`",
                "",
                "## Run Notes",
                f"- Replayed runs: {len(run_rows)}",
                "- Replay mode: observer-enabled, frame_stride=10, no BRF export.",
                f"- Runtime baseline settings source: `{settings_path.as_posix()}`",
                "",
                "## Key quick read",
                "- Use `movement_v1_vs_v3a_geometry_comparison.csv` for cell-level v1/v3a geometry means.",
                "- Use `high_fr_stray_diagnostics.csv` for FR=8 outlier proxies (distance/neighbor/connectivity).",
                "- Use heatmap PNGs for FR x MB structural interaction visualization.",
            ]
        ),
        encoding="utf-8",
    )

    print("[done] phase_viiic follow-up artifacts generated")
    print(f"[out] {out_dir}")


if __name__ == "__main__":
    main()
