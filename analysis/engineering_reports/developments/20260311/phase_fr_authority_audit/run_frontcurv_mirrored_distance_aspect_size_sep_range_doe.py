import csv
import json
import math
import sys
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[5]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from test_run.test_run_v1_0 import (
    build_initial_state,
    get_runtime_setting,
    load_json_file,
    resolve_archetype,
    resolve_movement_model,
    run_simulation,
    to_personality_parameters,
)


SETTINGS_PATH = ROOT / "test_run" / "test_run_v1_0.settings.json"
ARCHETYPES_PATH = ROOT / "archetypes" / "archetypes_v1_5.json"
OUTPUT_DIR = Path(__file__).resolve().parent
CSV_PATH = OUTPUT_DIR / "frontcurv_mirrored_distance_aspect_size_sep_range_doe_20260313.csv"
SUMMARY_PATH = OUTPUT_DIR / "frontcurv_mirrored_distance_aspect_size_sep_range_doe_20260313.md"

ORIGINS = [10.0, 30.0, 50.0, 70.0, 90.0]
ASPECT_RATIOS = [1.0, 1.5, 2.0, 2.5, 3.0]
FLEET_SIZES = [50, 75, 100, 125, 150]
MIN_SEPARATIONS = [1.0, 2.0, 3.0]
ATTACK_RANGES = [3.0, 5.0, 7.0]
STEPS = 120

FIELDNAMES = [
    "origin_a",
    "origin_b",
    "aspect_ratio",
    "fleet_size",
    "min_separation",
    "attack_range",
    "first_contact_tick",
    "frontcurve_diff_t1_20",
    "frontcurve_diff_t21_50",
    "frontcurve_diff_t51_120",
    "cws_diff_t1_20",
    "cws_diff_t21_50",
    "cws_diff_t51_120",
    "remaining_a",
    "remaining_b",
    "remaining_gap_pct_initial",
    "end_tick",
]


def mean_abs_diff(a, b, lo, hi):
    vals = []
    for i in range(lo - 1, min(hi, len(a), len(b))):
        av = float(a[i])
        bv = float(b[i])
        if math.isfinite(av) and math.isfinite(bv):
            vals.append(abs(av - bv))
    return mean(vals) if vals else float("nan")


def first_positive(series):
    for idx, value in enumerate(series, start=1):
        if float(value) > 0.0:
            return idx
    return None


def load_existing_rows():
    rows = []
    seen = set()
    if not CSV_PATH.exists():
        return rows, seen
    with CSV_PATH.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
            seen.add(
                (
                    float(row["origin_a"]),
                    float(row["aspect_ratio"]),
                    int(row["fleet_size"]),
                    float(row["min_separation"]),
                    float(row["attack_range"]),
                )
            )
    return rows, seen


def ensure_csv_header():
    if CSV_PATH.exists():
        return
    with CSV_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()


def append_row(row):
    with CSV_PATH.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writerow(row)


def write_summary(rows, substrate_label):
    rows_sorted = sorted(
        rows,
        key=lambda r: (
            float(r["origin_a"]),
            float(r["aspect_ratio"]),
            int(r["fleet_size"]),
            float(r["min_separation"]),
            float(r["attack_range"]),
        ),
    )
    lines = []
    lines.append("# FrontCurv Mirrored Distance-Aspect-Size-Sep-Range DOE")
    lines.append("")
    lines.append(f"- cells: {len(rows_sorted)}")
    lines.append(f"- substrate: {substrate_label}")
    lines.append(f"- steps: {STEPS}")
    lines.append("")

    for key in [
        "frontcurve_diff_t1_20",
        "frontcurve_diff_t21_50",
        "frontcurve_diff_t51_120",
        "cws_diff_t1_20",
        "cws_diff_t21_50",
        "remaining_gap_pct_initial",
    ]:
        vals = [float(r[key]) for r in rows_sorted if math.isfinite(float(r[key]))]
        lines.append(f"- mean {key}: {sum(vals) / len(vals):.4f}")

    lines.append("")
    for origin in ORIGINS:
        subset = [r for r in rows_sorted if float(r["origin_a"]) == origin]
        vals = [float(r["frontcurve_diff_t1_20"]) for r in subset if math.isfinite(float(r["frontcurve_diff_t1_20"]))]
        lines.append(f"- mean fc_t1_20 @ origin {origin:.0f}: {sum(vals) / len(vals):.4f}")

    lines.append("")
    for aspect in ASPECT_RATIOS:
        subset = [r for r in rows_sorted if float(r["aspect_ratio"]) == aspect]
        vals = [float(r["frontcurve_diff_t1_20"]) for r in subset if math.isfinite(float(r["frontcurve_diff_t1_20"]))]
        lines.append(f"- mean fc_t1_20 @ aspect {aspect:.1f}: {sum(vals) / len(vals):.4f}")

    lines.append("")
    for fleet_size in FLEET_SIZES:
        subset = [r for r in rows_sorted if int(r["fleet_size"]) == fleet_size]
        vals = [float(r["frontcurve_diff_t1_20"]) for r in subset if math.isfinite(float(r["frontcurve_diff_t1_20"]))]
        lines.append(f"- mean fc_t1_20 @ size {fleet_size}: {sum(vals) / len(vals):.4f}")

    lines.append("")
    for min_sep in MIN_SEPARATIONS:
        subset = [r for r in rows_sorted if float(r["min_separation"]) == min_sep]
        vals = [float(r["frontcurve_diff_t1_20"]) for r in subset if math.isfinite(float(r["frontcurve_diff_t1_20"]))]
        lines.append(f"- mean fc_t1_20 @ min_separation {min_sep:.1f}: {sum(vals) / len(vals):.4f}")

    lines.append("")
    for attack_range in ATTACK_RANGES:
        subset = [r for r in rows_sorted if float(r["attack_range"]) == attack_range]
        vals = [float(r["frontcurve_diff_t1_20"]) for r in subset if math.isfinite(float(r["frontcurve_diff_t1_20"]))]
        lines.append(f"- mean fc_t1_20 @ attack_range {attack_range:.1f}: {sum(vals) / len(vals):.4f}")

    SUMMARY_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    settings = load_json_file(SETTINGS_PATH)
    archetypes = json.loads(ARCHETYPES_PATH.read_text(encoding="utf-8-sig"))
    pa = to_personality_parameters(resolve_archetype(archetypes, str(settings["fleet"]["fleet_a_archetype_id"])))
    pb = to_personality_parameters(resolve_archetype(archetypes, str(settings["fleet"]["fleet_b_archetype_id"])))
    _, movement_model_effective = resolve_movement_model(get_runtime_setting(settings, "movement_model", "baseline"))
    substrate_label = str(get_runtime_setting(settings, "pre_tl_target_substrate", "nearest5_centroid"))

    rows, seen = load_existing_rows()
    ensure_csv_header()
    total = len(ORIGINS) * len(ASPECT_RATIOS) * len(FLEET_SIZES) * len(MIN_SEPARATIONS) * len(ATTACK_RANGES)
    completed = len(rows)

    for origin in ORIGINS:
        ax = ay = origin
        bx = by = 200.0 - origin
        for aspect in ASPECT_RATIOS:
            for fleet_size in FLEET_SIZES:
                for min_sep in MIN_SEPARATIONS:
                    for attack_range in ATTACK_RANGES:
                        key = (origin, aspect, fleet_size, min_sep, attack_range)
                        if key in seen:
                            continue

                        state = build_initial_state(
                            pa,
                            pb,
                            fleet_size,
                            fleet_size,
                            aspect,
                            aspect,
                            unit_spacing=min_sep,
                            unit_speed=float(settings["unit"]["unit_speed"]),
                            unit_max_hit_points=float(settings["unit"]["unit_max_hit_points"]),
                            arena_size=float(settings["battlefield"]["arena_size"]),
                            fleet_a_origin_x=ax,
                            fleet_a_origin_y=ay,
                            fleet_b_origin_x=bx,
                            fleet_b_origin_y=by,
                            fleet_a_facing_angle_deg=45.0,
                            fleet_b_facing_angle_deg=225.0,
                        )
                        (
                            final_state,
                            _traj,
                            alive_trajectory,
                            _fleet_size_trajectory,
                            observer_telemetry,
                            combat_telemetry,
                            _bridge,
                            _collapse,
                            _frames,
                        ) = run_simulation(
                            initial_state=state,
                            steps=STEPS,
                            capture_positions=False,
                            observer_enabled=True,
                            runtime_decision_source="v3_test",
                            movement_model=movement_model_effective,
                            bridge_theta_split=float(settings["runtime"]["observer"]["event_bridge"]["theta_split"]),
                            bridge_theta_env=float(settings["runtime"]["observer"]["event_bridge"]["theta_env"]),
                            bridge_sustain_ticks=int(settings["runtime"]["observer"]["event_bridge"]["sustain_ticks"]),
                            collapse_shadow_theta_conn_default=float(settings["runtime"]["observer"]["collapse_shadow"]["theta_conn_default"]),
                            collapse_shadow_theta_coh_default=float(settings["runtime"]["observer"]["collapse_shadow"]["theta_coh_default"]),
                            collapse_shadow_theta_force_default=float(settings["runtime"]["observer"]["collapse_shadow"]["theta_force_default"]),
                            collapse_shadow_theta_attr_default=float(settings["runtime"]["observer"]["collapse_shadow"]["theta_attr_default"]),
                            collapse_shadow_attrition_window=int(settings["runtime"]["observer"]["collapse_shadow"]["attrition_window"]),
                            collapse_shadow_sustain_ticks=int(settings["runtime"]["observer"]["collapse_shadow"]["sustain_ticks"]),
                            collapse_shadow_min_conditions=int(settings["runtime"]["observer"]["collapse_shadow"]["min_conditions"]),
                            frame_stride=1,
                            attack_range=attack_range,
                            damage_per_tick=float(settings["unit"]["damage_per_tick"]),
                            separation_radius=min_sep,
                            fire_quality_alpha=float(get_runtime_setting(settings, "fire_quality_alpha", 0.1)),
                            contact_hysteresis_h=float(get_runtime_setting(settings, "contact_hysteresis_h", 0.1)),
                            ch_enabled=True,
                            fsr_enabled=True,
                            fsr_strength=float(get_runtime_setting(settings, "fsr_strength", 0.1)),
                            boundary_enabled=bool(get_runtime_setting(settings, "boundary_enabled", True)),
                            boundary_hard_enabled=bool(get_runtime_setting(settings, "boundary_hard_enabled", False)),
                            include_target_lines=False,
                            print_tick_summary=False,
                            plot_diagnostics_enabled=False,
                            boundary_soft_strength=float(get_runtime_setting(settings, "boundary_soft_strength", 0.1)),
                            alpha_sep=float(get_runtime_setting(settings, "alpha_sep", 0.6)),
                            movement_v3a_experiment=str(get_runtime_setting(settings, "movement_v3a_experiment", "base")),
                            centroid_probe_scale=float(get_runtime_setting(settings, "centroid_probe_scale", 1.0)),
                            pre_tl_target_substrate=substrate_label,
                            symmetric_movement_sync_enabled=bool(get_runtime_setting(settings, "symmetric_movement_sync_enabled", True)),
                            odw_posture_bias_enabled=bool(get_runtime_setting(settings, "odw_posture_bias_enabled", False)),
                            odw_posture_bias_k=float(get_runtime_setting(settings, "odw_posture_bias_k", 0.3)),
                            odw_posture_bias_clip_delta=float(get_runtime_setting(settings, "odw_posture_bias_clip_delta", 0.2)),
                            v2_connect_radius_multiplier=1.0,
                            v3_connect_radius_multiplier=1.1,
                            v3_r_ref_radius_multiplier=1.0,
                            runtime_diag_enabled=False,
                        )
                        fc = observer_telemetry["front_curvature_index"]
                        cws = observer_telemetry["center_wing_parallel_share"]
                        rem_a = int(alive_trajectory["A"][-1])
                        rem_b = int(alive_trajectory["B"][-1])
                        row = {
                            "origin_a": ax,
                            "origin_b": bx,
                            "aspect_ratio": aspect,
                            "fleet_size": fleet_size,
                            "min_separation": min_sep,
                            "attack_range": attack_range,
                            "first_contact_tick": first_positive(combat_telemetry["in_contact_count"]),
                            "frontcurve_diff_t1_20": mean_abs_diff(fc["A"], fc["B"], 1, 20),
                            "frontcurve_diff_t21_50": mean_abs_diff(fc["A"], fc["B"], 21, 50),
                            "frontcurve_diff_t51_120": mean_abs_diff(fc["A"], fc["B"], 51, 120),
                            "cws_diff_t1_20": mean_abs_diff(cws["A"], cws["B"], 1, 20),
                            "cws_diff_t21_50": mean_abs_diff(cws["A"], cws["B"], 21, 50),
                            "cws_diff_t51_120": mean_abs_diff(cws["A"], cws["B"], 51, 120),
                            "remaining_a": rem_a,
                            "remaining_b": rem_b,
                            "remaining_gap_pct_initial": abs(rem_a - rem_b) / float(fleet_size) * 100.0,
                            "end_tick": int(final_state.tick),
                        }
                        rows.append(row)
                        append_row(row)
                        seen.add(key)
                        completed += 1
                        print(
                            f"done origin={origin:.0f} aspect={aspect:.1f} size={fleet_size} "
                            f"sep={min_sep:.1f} range={attack_range:.1f} ({completed}/{total})"
                        )

    write_summary(rows, substrate_label)
    print(f"WROTE {CSV_PATH}")
    print(f"WROTE {SUMMARY_PATH}")


if __name__ == "__main__":
    main()
