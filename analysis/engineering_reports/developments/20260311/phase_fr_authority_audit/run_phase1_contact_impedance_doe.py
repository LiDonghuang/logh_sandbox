#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from test_run.test_run_v1_0 import (  # noqa: E402
    PRE_TL_TARGET_SUBSTRATE_NEAREST5,
    SimulationBoundaryConfig,
    SimulationContactConfig,
    SimulationExecutionConfig,
    SimulationMovementConfig,
    SimulationObserverConfig,
    SimulationRuntimeConfig,
    TestModeEngineTickSkeleton,
    build_initial_state,
    get_runtime_setting,
    load_json_file,
    resolve_archetype,
    resolve_movement_model,
    run_simulation,
    to_personality_parameters,
)

HOSTILE_CONTACT_IMPEDANCE_MODE_OFF = "off"
HOSTILE_CONTACT_IMPEDANCE_MODE_REPULSION_V1 = "repulsion_v1"
HOSTILE_CONTACT_IMPEDANCE_MODE_DAMPING_V2 = "damping_v2"
HOSTILE_CONTACT_IMPEDANCE_MODE_HYBRID_V2 = "hybrid_v2"


SETTINGS_PATH = ROOT / "test_run" / "test_run_v1_0.settings.json"
ARCHETYPES_PATH = ROOT / "archetypes" / "archetypes_v1_5.json"
OUT_DIR = Path(__file__).resolve().parent
RUN_TABLE_PATH = OUT_DIR / "phase1_contact_impedance_doe_run_table.csv"
SUMMARY_CSV_PATH = OUT_DIR / "phase1_contact_impedance_doe_config_summary.csv"
SUMMARY_MD_PATH = OUT_DIR / "phase1_contact_impedance_doe_summary.md"

STEPS = 120
ATTACK_RANGE_FIXED = 5.0
MIN_SEPARATIONS = [1.0, 2.0]

FIXTURES = [
    {
        "fixture_id": "exception_2to1_close",
        "fleet_a_size": 200,
        "fleet_b_size": 100,
        "fleet_a_aspect_ratio": 2.0,
        "fleet_b_aspect_ratio": 2.0,
        "fleet_a_origin_xy": (80.0, 80.0),
        "fleet_b_origin_xy": (120.0, 120.0),
        "fleet_a_facing_angle_deg": 45.0,
        "fleet_b_facing_angle_deg": 225.0,
    },
    {
        "fixture_id": "neutral_close",
        "fleet_a_size": 100,
        "fleet_b_size": 100,
        "fleet_a_aspect_ratio": 2.0,
        "fleet_b_aspect_ratio": 2.0,
        "fleet_a_origin_xy": (80.0, 80.0),
        "fleet_b_origin_xy": (120.0, 120.0),
        "fleet_a_facing_angle_deg": 45.0,
        "fleet_b_facing_angle_deg": 225.0,
    },
    {
        "fixture_id": "neutral_long",
        "fleet_a_size": 100,
        "fleet_b_size": 100,
        "fleet_a_aspect_ratio": 2.0,
        "fleet_b_aspect_ratio": 2.0,
        "fleet_a_origin_xy": (10.0, 10.0),
        "fleet_b_origin_xy": (190.0, 190.0),
        "fleet_a_facing_angle_deg": 45.0,
        "fleet_b_facing_angle_deg": 225.0,
    },
]

REPULSION_V1_STRENGTHS = [0.20, 0.35, 0.50]
REPULSION_V1_RADII = [1.25, 1.50, 2.00]
V2_RADII = [1.00, 1.25, 1.50, 1.75, 2.00]
V2_DAMPING_STRENGTHS = [0.20, 0.35, 0.50, 0.65, 0.80, 0.95]
V2_REPULSION_MAX_DISP = [0.05, 0.10, 0.15, 0.20]

FIELDNAMES = [
    "run_id",
    "fixture_id",
    "min_separation",
    "config_id",
    "mode",
    "attack_range",
    "repulsion_v1_enabled",
    "repulsion_v1_strength",
    "repulsion_v1_radius_multiplier",
    "v2_radius_multiplier",
    "v2_repulsion_max_disp_ratio",
    "v2_forward_damping_strength",
    "first_contact_tick",
    "fc_diff_t1_20",
    "fc_diff_t21_50",
    "fc_diff_t51_120",
    "cws_diff_t1_20",
    "cws_diff_t21_50",
    "hostile_overlap_pairs_t21_120",
    "hostile_deep_pairs_t21_120",
    "hostile_deep_intermix_ratio_t21_120",
    "hostile_intermix_severity_t21_120",
    "remaining_a",
    "remaining_b",
    "remaining_gap_pct_initial",
    "end_tick",
]

FILE_IO_RETRY_ATTEMPTS = 20
FILE_IO_RETRY_SLEEP_SEC = 0.25


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-runs", type=int, default=None)
    return parser.parse_args()


def as_float(value: Any, default: float = float("nan")) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return default
    return result if math.isfinite(result) else default


def mean_window(series: list[Any], start_tick: int, end_tick: int) -> float:
    values = []
    for tick in range(max(1, start_tick), max(start_tick, end_tick) + 1):
        idx = tick - 1
        if idx >= len(series):
            continue
        v = as_float(series[idx])
        if math.isfinite(v):
            values.append(v)
    if not values:
        return float("nan")
    return sum(values) / float(len(values))


def mean_abs_diff(series_a: list[Any], series_b: list[Any], start_tick: int, end_tick: int) -> float:
    values = []
    for tick in range(max(1, start_tick), max(start_tick, end_tick) + 1):
        idx = tick - 1
        if idx >= len(series_a) or idx >= len(series_b):
            continue
        a = as_float(series_a[idx])
        b = as_float(series_b[idx])
        if math.isfinite(a) and math.isfinite(b):
            values.append(abs(a - b))
    if not values:
        return float("nan")
    return sum(values) / float(len(values))


def first_contact_tick(combat_telemetry: dict[str, Any]) -> int | None:
    for idx, value in enumerate(combat_telemetry.get("in_contact_count", []), start=1):
        if int(value) > 0:
            return idx
    return None


def with_file_retry(fn, path: Path):
    last_error: OSError | None = None
    for attempt in range(FILE_IO_RETRY_ATTEMPTS):
        try:
            return fn()
        except PermissionError as exc:
            last_error = exc
            if attempt >= FILE_IO_RETRY_ATTEMPTS - 1:
                raise
            time.sleep(FILE_IO_RETRY_SLEEP_SEC)
        except OSError as exc:
            last_error = exc
            if attempt >= FILE_IO_RETRY_ATTEMPTS - 1:
                raise
            time.sleep(FILE_IO_RETRY_SLEEP_SEC)
    if last_error is not None:
        raise last_error
    raise RuntimeError(f"unexpected file retry failure for {path}")


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    def _write():
        with path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    with_file_retry(_write, path)


def append_rows(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    if not rows:
        return
    def _append():
        file_exists = path.exists()
        with path.open("a", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exists or path.stat().st_size == 0:
                writer.writeheader()
            writer.writerows(rows)

    with_file_retry(_append, path)


def load_existing_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    def _read():
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            return [dict(row) for row in csv.DictReader(f)]

    return with_file_retry(_read, path)


def build_config_grid() -> list[dict[str, Any]]:
    configs: list[dict[str, Any]] = [
        {
            "config_id": "off",
            "mode": HOSTILE_CONTACT_IMPEDANCE_MODE_OFF,
            "repulsion_v1_enabled": False,
            "repulsion_v1_strength": 0.35,
            "repulsion_v1_radius_multiplier": 1.50,
            "v2_radius_multiplier": 1.50,
            "v2_repulsion_max_disp_ratio": 0.0,
            "v2_forward_damping_strength": 0.50,
        }
    ]
    for strength in REPULSION_V1_STRENGTHS:
        for radius in REPULSION_V1_RADII:
            configs.append(
                {
                    "config_id": f"repulsion_v1_s{int(round(strength * 100)):03d}_r{int(round(radius * 100)):03d}",
                    "mode": HOSTILE_CONTACT_IMPEDANCE_MODE_REPULSION_V1,
                    "repulsion_v1_enabled": True,
                    "repulsion_v1_strength": strength,
                    "repulsion_v1_radius_multiplier": radius,
                    "v2_radius_multiplier": 1.50,
                    "v2_repulsion_max_disp_ratio": 0.0,
                    "v2_forward_damping_strength": 0.50,
                }
            )
    for radius in V2_RADII:
        for damping in V2_DAMPING_STRENGTHS:
            configs.append(
                {
                    "config_id": f"damping_v2_r{int(round(radius * 100)):03d}_d{int(round(damping * 100)):03d}",
                    "mode": HOSTILE_CONTACT_IMPEDANCE_MODE_DAMPING_V2,
                    "repulsion_v1_enabled": False,
                    "repulsion_v1_strength": 0.35,
                    "repulsion_v1_radius_multiplier": 1.50,
                    "v2_radius_multiplier": radius,
                    "v2_repulsion_max_disp_ratio": 0.0,
                    "v2_forward_damping_strength": damping,
                }
            )
    for radius in V2_RADII:
        for damping in V2_DAMPING_STRENGTHS:
            for repulsion in V2_REPULSION_MAX_DISP:
                configs.append(
                    {
                        "config_id": (
                            f"hybrid_v2_r{int(round(radius * 100)):03d}_"
                            f"d{int(round(damping * 100)):03d}_"
                            f"p{int(round(repulsion * 100)):03d}"
                        ),
                        "mode": HOSTILE_CONTACT_IMPEDANCE_MODE_HYBRID_V2,
                        "repulsion_v1_enabled": False,
                        "repulsion_v1_strength": 0.35,
                        "repulsion_v1_radius_multiplier": 1.50,
                        "v2_radius_multiplier": radius,
                        "v2_repulsion_max_disp_ratio": repulsion,
                        "v2_forward_damping_strength": damping,
                    }
                )
    assert len(configs) == 160, len(configs)
    return configs


def build_run_matrix() -> list[dict[str, Any]]:
    configs = build_config_grid()
    runs = []
    for fixture in FIXTURES:
        for min_sep in MIN_SEPARATIONS:
            for config in configs:
                run_id = f"{fixture['fixture_id']}__sep{int(round(min_sep * 100)):03d}__{config['config_id']}"
                runs.append(
                    {
                        "run_id": run_id,
                        "fixture": fixture,
                        "min_separation": min_sep,
                        "config": config,
                    }
                )
    assert len(runs) == 960, len(runs)
    return runs


def build_params_from_settings(settings: dict[str, Any]):
    archetypes = json.loads(ARCHETYPES_PATH.read_text(encoding="utf-8-sig"))
    fleet_settings = settings["fleet"]
    pa = to_personality_parameters(resolve_archetype(archetypes, str(fleet_settings["fleet_a_archetype_id"])))
    pb = to_personality_parameters(resolve_archetype(archetypes, str(fleet_settings["fleet_b_archetype_id"])))
    return pa, pb


def run_one(
    settings: dict[str, Any],
    pa,
    pb,
    fixture: dict[str, Any],
    min_separation: float,
    config: dict[str, Any],
) -> dict[str, Any]:
    _, movement_model_effective = resolve_movement_model(get_runtime_setting(settings, "movement_model", "baseline"))
    initial_state = build_initial_state(
        fleet_a_params=pa,
        fleet_b_params=pb,
        fleet_a_size=int(fixture["fleet_a_size"]),
        fleet_b_size=int(fixture["fleet_b_size"]),
        fleet_a_aspect_ratio=float(fixture["fleet_a_aspect_ratio"]),
        fleet_b_aspect_ratio=float(fixture["fleet_b_aspect_ratio"]),
        unit_spacing=float(min_separation),
        unit_speed=float(settings["unit"]["unit_speed"]),
        unit_max_hit_points=float(settings["unit"]["unit_max_hit_points"]),
        arena_size=float(settings["battlefield"]["arena_size"]),
        fleet_a_origin_x=float(fixture["fleet_a_origin_xy"][0]),
        fleet_a_origin_y=float(fixture["fleet_a_origin_xy"][1]),
        fleet_b_origin_x=float(fixture["fleet_b_origin_xy"][0]),
        fleet_b_origin_y=float(fixture["fleet_b_origin_xy"][1]),
        fleet_a_facing_angle_deg=float(fixture["fleet_a_facing_angle_deg"]),
        fleet_b_facing_angle_deg=float(fixture["fleet_b_facing_angle_deg"]),
    )
    execution_cfg = SimulationExecutionConfig(
        steps=STEPS,
        capture_positions=False,
        frame_stride=1,
        include_target_lines=False,
        print_tick_summary=False,
        plot_diagnostics_enabled=False,
    )
    runtime_cfg = SimulationRuntimeConfig(
        decision_source="v3_test",
        movement_model=movement_model_effective,
        movement=SimulationMovementConfig(
            v3a_experiment=str(get_runtime_setting(settings, "movement_v3a_experiment", "base")),
            centroid_probe_scale=float(get_runtime_setting(settings, "centroid_probe_scale", 1.0)),
            pre_tl_target_substrate=PRE_TL_TARGET_SUBSTRATE_NEAREST5,
            symmetric_movement_sync_enabled=bool(get_runtime_setting(settings, "symmetric_movement_sync_enabled", True)),
            odw_posture_bias_enabled=bool(get_runtime_setting(settings, "odw_posture_bias_enabled", False)),
            odw_posture_bias_k=float(get_runtime_setting(settings, "odw_posture_bias_k", 0.0)),
            odw_posture_bias_clip_delta=float(get_runtime_setting(settings, "odw_posture_bias_clip_delta", 0.2)),
            v2_connect_radius_multiplier=float(settings["runtime"]["semantics"]["collapse_signal"]["v3_connect_radius_multiplier"]),
            v3_connect_radius_multiplier=float(settings["runtime"]["semantics"]["collapse_signal"]["v3_connect_radius_multiplier"]),
            v3_r_ref_radius_multiplier=float(settings["runtime"]["semantics"]["collapse_signal"]["v3_r_ref_radius_multiplier"]),
        ),
        contact=SimulationContactConfig(
            attack_range=ATTACK_RANGE_FIXED,
            damage_per_tick=float(settings["unit"]["damage_per_tick"]),
            separation_radius=float(min_separation),
            fire_quality_alpha=float(get_runtime_setting(settings, "fire_quality_alpha", 0.1)),
            contact_hysteresis_h=float(get_runtime_setting(settings, "contact_hysteresis_h", 0.1)),
            ch_enabled=float(get_runtime_setting(settings, "contact_hysteresis_h", 0.1)) > 0.0,
            fsr_enabled=float(get_runtime_setting(settings, "fsr_strength", 0.1)) > 0.0,
            fsr_strength=float(get_runtime_setting(settings, "fsr_strength", 0.1)),
            alpha_sep=float(get_runtime_setting(settings, "alpha_sep", 0.6)),
            hostile_contact_impedance_mode=str(config["mode"]),
            hostile_contact_impedance_v2_radius_multiplier=float(config["v2_radius_multiplier"]),
            hostile_contact_impedance_v2_repulsion_max_disp_ratio=float(config["v2_repulsion_max_disp_ratio"]),
            hostile_contact_impedance_v2_forward_damping_strength=float(config["v2_forward_damping_strength"]),
        ),
        boundary=SimulationBoundaryConfig(
            enabled=False,
            hard_enabled=False,
            soft_strength=float(get_runtime_setting(settings, "boundary_soft_strength", 0.0)),
        ),
    )
    observer_cfg = SimulationObserverConfig(
        enabled=True,
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
    )
    final_state, _traj, _alive_trajectory, _fleet_size_trajectory, observer_telemetry, combat_telemetry, _bridge, _collapse, _frames = run_simulation(
        initial_state=initial_state,
        engine_cls=TestModeEngineTickSkeleton,
        execution_cfg=execution_cfg,
        runtime_cfg=runtime_cfg,
        observer_cfg=observer_cfg,
    )

    initial_total = float(fixture["fleet_a_size"] + fixture["fleet_b_size"])
    remaining_a = len(final_state.fleets["A"].unit_ids)
    remaining_b = len(final_state.fleets["B"].unit_ids)
    remaining_gap_pct_initial = 100.0 * abs(float(remaining_a - remaining_b)) / max(1.0, initial_total)

    row = {
        "run_id": f"{fixture['fixture_id']}__sep{int(round(min_separation * 100)):03d}__{config['config_id']}",
        "fixture_id": fixture["fixture_id"],
        "min_separation": float(min_separation),
        "config_id": config["config_id"],
        "mode": config["mode"],
        "attack_range": ATTACK_RANGE_FIXED,
        "repulsion_v1_enabled": int(bool(config["repulsion_v1_enabled"])),
        "repulsion_v1_strength": float(config["repulsion_v1_strength"]),
        "repulsion_v1_radius_multiplier": float(config["repulsion_v1_radius_multiplier"]),
        "v2_radius_multiplier": float(config["v2_radius_multiplier"]),
        "v2_repulsion_max_disp_ratio": float(config["v2_repulsion_max_disp_ratio"]),
        "v2_forward_damping_strength": float(config["v2_forward_damping_strength"]),
        "first_contact_tick": first_contact_tick(combat_telemetry),
        "fc_diff_t1_20": mean_abs_diff(
            observer_telemetry["front_curvature_index"]["A"],
            observer_telemetry["front_curvature_index"]["B"],
            1,
            20,
        ),
        "fc_diff_t21_50": mean_abs_diff(
            observer_telemetry["front_curvature_index"]["A"],
            observer_telemetry["front_curvature_index"]["B"],
            21,
            50,
        ),
        "fc_diff_t51_120": mean_abs_diff(
            observer_telemetry["front_curvature_index"]["A"],
            observer_telemetry["front_curvature_index"]["B"],
            51,
            120,
        ),
        "cws_diff_t1_20": mean_abs_diff(
            observer_telemetry["center_wing_parallel_share"]["A"],
            observer_telemetry["center_wing_parallel_share"]["B"],
            1,
            20,
        ),
        "cws_diff_t21_50": mean_abs_diff(
            observer_telemetry["center_wing_parallel_share"]["A"],
            observer_telemetry["center_wing_parallel_share"]["B"],
            21,
            50,
        ),
        "hostile_overlap_pairs_t21_120": mean_window(observer_telemetry["hostile_overlap_pairs"], 21, 120),
        "hostile_deep_pairs_t21_120": mean_window(observer_telemetry["hostile_deep_pairs"], 21, 120),
        "hostile_deep_intermix_ratio_t21_120": mean_window(observer_telemetry["hostile_deep_intermix_ratio"], 21, 120),
        "hostile_intermix_severity_t21_120": mean_window(observer_telemetry["hostile_intermix_severity"], 21, 120),
        "remaining_a": remaining_a,
        "remaining_b": remaining_b,
        "remaining_gap_pct_initial": remaining_gap_pct_initial,
        "end_tick": int(final_state.tick),
    }
    return row


def summarize(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], str]:
    rows_sorted = sorted(
        rows,
        key=lambda r: (
            str(r["fixture_id"]),
            as_float(r["min_separation"]),
            str(r["config_id"]),
        ),
    )
    baseline_by_cell: dict[tuple[str, float], dict[str, Any]] = {}
    for row in rows_sorted:
        if str(row["config_id"]) == "off":
            baseline_by_cell[(str(row["fixture_id"]), as_float(row["min_separation"]))] = row

    summary_rows = []
    config_ids = sorted({str(row["config_id"]) for row in rows_sorted})
    for config_id in config_ids:
        config_rows = [row for row in rows_sorted if str(row["config_id"]) == config_id]
        exception_pass = True
        neutral_close_pass = True
        neutral_long_pass = True
        severity_delta_pcts = []
        deep_ratio_delta_pcts = []
        for row in config_rows:
            fixture_id = str(row["fixture_id"])
            min_sep = as_float(row["min_separation"])
            base = baseline_by_cell.get((fixture_id, min_sep))
            if base is None:
                continue
            base_sev = as_float(base["hostile_intermix_severity_t21_120"])
            cur_sev = as_float(row["hostile_intermix_severity_t21_120"])
            sev_delta_pct = float("nan")
            if math.isfinite(base_sev) and base_sev > 0.0 and math.isfinite(cur_sev):
                sev_delta_pct = 100.0 * (base_sev - cur_sev) / base_sev
            base_deep_ratio = as_float(base["hostile_deep_intermix_ratio_t21_120"])
            cur_deep_ratio = as_float(row["hostile_deep_intermix_ratio_t21_120"])
            deep_delta_pct = float("nan")
            if math.isfinite(base_deep_ratio) and base_deep_ratio > 0.0 and math.isfinite(cur_deep_ratio):
                deep_delta_pct = 100.0 * (base_deep_ratio - cur_deep_ratio) / base_deep_ratio
            if math.isfinite(sev_delta_pct):
                severity_delta_pcts.append(sev_delta_pct)
            if math.isfinite(deep_delta_pct):
                deep_ratio_delta_pcts.append(deep_delta_pct)

            if fixture_id == "exception_2to1_close":
                if not (math.isfinite(sev_delta_pct) and sev_delta_pct >= 30.0):
                    exception_pass = False
                if not (math.isfinite(deep_delta_pct) and deep_delta_pct >= 20.0):
                    exception_pass = False
            elif fixture_id == "neutral_close":
                if as_float(row["fc_diff_t21_50"]) > (as_float(base["fc_diff_t21_50"]) * 1.15):
                    neutral_close_pass = False
                if as_float(row["cws_diff_t1_20"]) > (as_float(base["cws_diff_t1_20"]) * 1.15):
                    neutral_close_pass = False
            elif fixture_id == "neutral_long":
                if as_float(row["fc_diff_t1_20"]) > (as_float(base["fc_diff_t1_20"]) * 1.10):
                    neutral_long_pass = False
                base_contact = base["first_contact_tick"]
                row_contact = row["first_contact_tick"]
                if base_contact not in {"", None} and row_contact not in {"", None}:
                    if int(row_contact) < (int(base_contact) - 2):
                        neutral_long_pass = False
                elif base_contact not in {"", None} and row_contact in {"", None}:
                    neutral_long_pass = False

        phase1_pass = exception_pass and neutral_close_pass and neutral_long_pass
        example = config_rows[0]
        summary_rows.append(
            {
                "config_id": config_id,
                "mode": example["mode"],
                "repulsion_v1_strength": example["repulsion_v1_strength"],
                "repulsion_v1_radius_multiplier": example["repulsion_v1_radius_multiplier"],
                "v2_radius_multiplier": example["v2_radius_multiplier"],
                "v2_repulsion_max_disp_ratio": example["v2_repulsion_max_disp_ratio"],
                "v2_forward_damping_strength": example["v2_forward_damping_strength"],
                "mean_severity_delta_pct": (
                    sum(severity_delta_pcts) / float(len(severity_delta_pcts))
                    if severity_delta_pcts else float("nan")
                ),
                "mean_deep_ratio_delta_pct": (
                    sum(deep_ratio_delta_pcts) / float(len(deep_ratio_delta_pcts))
                    if deep_ratio_delta_pcts else float("nan")
                ),
                "exception_pass_all_minsep": int(exception_pass),
                "neutral_close_pass_all_minsep": int(neutral_close_pass),
                "neutral_long_pass_all_minsep": int(neutral_long_pass),
                "phase1_pass": int(phase1_pass),
            }
        )

    total_rows = len(rows_sorted)
    total_configs = len(summary_rows)
    total_phase1_pass = sum(int(row["phase1_pass"]) for row in summary_rows)
    lines = [
        "# Phase 1 Contact Impedance DOE Summary",
        "",
        f"- run rows: {total_rows}",
        f"- configs: {total_configs}",
        f"- fixtures: {len(FIXTURES)}",
        f"- min_separation axis: {MIN_SEPARATIONS}",
        f"- fixed attack_range: {ATTACK_RANGE_FIXED}",
        f"- phase1_pass configs: {total_phase1_pass}",
        "",
    ]
    top_rows = sorted(
        summary_rows,
        key=lambda row: (
            -int(row["phase1_pass"]),
            -(as_float(row["mean_severity_delta_pct"], default=-1e9)),
            -(as_float(row["mean_deep_ratio_delta_pct"], default=-1e9)),
        ),
    )[:10]
    lines.append("## Top configs")
    lines.append("")
    for row in top_rows:
        lines.append(
            "- "
            f"{row['config_id']}: phase1_pass={row['phase1_pass']}, "
            f"mean_severity_delta_pct={as_float(row['mean_severity_delta_pct']):.2f}, "
            f"mean_deep_ratio_delta_pct={as_float(row['mean_deep_ratio_delta_pct']):.2f}"
        )
    return summary_rows, "\n".join(lines) + "\n"


def main() -> None:
    args = parse_args()
    settings = load_json_file(SETTINGS_PATH)
    pa, pb = build_params_from_settings(settings)

    existing_rows = load_existing_rows(RUN_TABLE_PATH)
    existing_run_ids = {str(row["run_id"]) for row in existing_rows}
    run_matrix = build_run_matrix()
    pending_runs = [item for item in run_matrix if item["run_id"] not in existing_run_ids]
    if args.max_runs is not None and args.max_runs >= 0:
        pending_runs = pending_runs[: args.max_runs]

    print(f"[phase1_doe] existing_rows={len(existing_rows)}")
    print(f"[phase1_doe] pending_runs_selected={len(pending_runs)}")

    new_rows: list[dict[str, Any]] = []
    for idx, item in enumerate(pending_runs, start=1):
        print(
            "[phase1_doe] "
            f"{idx}/{len(pending_runs)} run_id={item['run_id']}"
        )
        row = run_one(
            settings=settings,
            pa=pa,
            pb=pb,
            fixture=item["fixture"],
            min_separation=float(item["min_separation"]),
            config=item["config"],
        )
        new_rows.append(row)
        append_rows(RUN_TABLE_PATH, [row], FIELDNAMES)

    all_rows = existing_rows + new_rows
    if RUN_TABLE_PATH.exists():
        all_rows = load_existing_rows(RUN_TABLE_PATH)
    summary_rows, summary_md = summarize(all_rows)
    write_csv(SUMMARY_CSV_PATH, summary_rows, list(summary_rows[0].keys()) if summary_rows else ["config_id"])
    with_file_retry(lambda: SUMMARY_MD_PATH.write_text(summary_md, encoding="utf-8"), SUMMARY_MD_PATH)
    print(f"[phase1_doe] total_rows_after={len(all_rows)}")
    print(f"[phase1_doe] run_table={RUN_TABLE_PATH}")
    print(f"[phase1_doe] summary_csv={SUMMARY_CSV_PATH}")
    print(f"[phase1_doe] summary_md={SUMMARY_MD_PATH}")


if __name__ == "__main__":
    main()
