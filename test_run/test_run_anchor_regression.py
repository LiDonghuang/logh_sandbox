from __future__ import annotations

import json
import math
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from test_run import settings_accessor
from test_run import test_run_entry as entry_mod


TEST_RUN_DIR = PROJECT_ROOT / "test_run"
ANCHOR_PATH = (
    PROJECT_ROOT
    / "analysis"
    / "engineering_reports"
    / "developments"
    / "20260318"
    / "structural_cleanup"
    / "a5_iteration0_baseline_anchor_20260318.json"
)
ROUTINE_FIXTURE_ID = "neutral_close_100v100"
ROUTINE_ROW_COUNT = 3
ROUTINE_RANDOM_SEED = 12345
ROUTINE_BACKGROUND_SEED = 24680
ROUTINE_MOVEMENT_EXPERIMENT = "exp_precontact_centroid_probe"
ROUTINE_CENTROID_PROBE_SCALE = 0.5
ROUTINE_PRE_TL_TARGET_SUBSTRATE = "nearest5_centroid"
ROUTINE_MIN_UNIT_SPACING = 2.0
ROUTINE_METRICS = (
    "final_tick",
    "alive_a",
    "alive_b",
    "winner",
    "first_contact_tick",
    "intermix_coverage_t21_120_mean",
    "intermix_severity_t21_120_mean",
    "deep_ratio_t21_120_mean",
    "frontcurv_diff_t21_50_mean_abs",
    "cw_pshare_diff_t1_20_mean_abs",
)


def _as_float(value, default: float = float("nan")) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return default
    return result if math.isfinite(result) else default


def _mean_window(series: list, start_tick: int, end_tick: int) -> float:
    values = []
    for tick in range(max(1, start_tick), max(start_tick, end_tick) + 1):
        idx = tick - 1
        if idx >= len(series):
            continue
        value = _as_float(series[idx])
        if math.isfinite(value):
            values.append(value)
    return float("nan") if not values else sum(values) / float(len(values))


def _mean_abs_diff(series_a: list, series_b: list, start_tick: int, end_tick: int) -> float:
    values = []
    for tick in range(max(1, start_tick), max(start_tick, end_tick) + 1):
        idx = tick - 1
        if idx >= len(series_a) or idx >= len(series_b):
            continue
        value_a = _as_float(series_a[idx])
        value_b = _as_float(series_b[idx])
        if math.isfinite(value_a) and math.isfinite(value_b):
            values.append(abs(value_a - value_b))
    return float("nan") if not values else sum(values) / float(len(values))


def _first_contact_tick(combat_telemetry: dict) -> int | None:
    for idx, value in enumerate(combat_telemetry.get("in_contact_count", []), start=1):
        if int(value) > 0:
            return idx
    return None


def _resolve_winner(final_state) -> str:
    alive_a = len(final_state.fleets["A"].unit_ids)
    alive_b = len(final_state.fleets["B"].unit_ids)
    if alive_a > 0 and alive_b > 0:
        return "undecided"
    if alive_a > 0:
        return "A"
    if alive_b > 0:
        return "B"
    return "draw"


def _copy_settings(settings: dict) -> dict:
    return json.loads(json.dumps(settings))


def _build_routine_settings(base_settings: dict, fixture: dict, steps: int, contact_mode: str) -> dict:
    settings = _copy_settings(base_settings)

    run_control = settings.setdefault("run_control", {})
    run_control["test_mode"] = 2
    run_control["random_seed"] = ROUTINE_RANDOM_SEED
    run_control["max_time_steps"] = int(steps)

    fleet = settings.setdefault("fleet", {})
    fleet["fleet_a_archetype_id"] = "lobos"
    fleet["fleet_b_archetype_id"] = "lobos"
    fleet["initial_fleet_a_size"] = int(fixture["a_size"])
    fleet["initial_fleet_b_size"] = int(fixture["b_size"])
    fleet["initial_fleet_a_aspect_ratio"] = float(fixture["a_aspect"])
    fleet["initial_fleet_b_aspect_ratio"] = float(fixture["b_aspect"])
    fleet["initial_fleet_a_origin_xy"] = list(fixture["a_origin"])
    fleet["initial_fleet_b_origin_xy"] = list(fixture["b_origin"])
    fleet["initial_fleet_a_facing_angle_deg"] = 45.0
    fleet["initial_fleet_b_facing_angle_deg"] = 225.0

    battlefield = settings.setdefault("battlefield", {})
    battlefield["arena_size"] = 200.0
    battlefield["background_map_seed"] = ROUTINE_BACKGROUND_SEED

    runtime = settings.setdefault("runtime", {})
    runtime.setdefault("metatype", {})["random_seed"] = ROUTINE_RANDOM_SEED

    selectors = runtime.setdefault("selectors", {})
    selectors["movement_model"] = "v3a"
    selectors["cohesion_decision_source"] = "v3_test"

    movement_v3a = runtime.setdefault("movement", {}).setdefault("v3a", {}).setdefault("test_only", {})
    movement_v3a["experiment"] = ROUTINE_MOVEMENT_EXPERIMENT
    movement_v3a["centroid_probe_scale"] = ROUTINE_CENTROID_PROBE_SCALE
    movement_v3a["pre_tl_target_substrate"] = ROUTINE_PRE_TL_TARGET_SUBSTRATE
    movement_v3a["symmetric_movement_sync_enabled"] = True
    movement_v3a.setdefault("odw_posture_bias", {})["enabled"] = True
    movement_v3a["odw_posture_bias"]["k"] = 0.5
    movement_v3a["odw_posture_bias"]["clip_delta"] = 0.4

    physical = runtime.setdefault("physical", {})
    physical.setdefault("boundary", {})["enabled"] = False
    physical.setdefault("movement_low_level", {})["min_unit_spacing"] = ROUTINE_MIN_UNIT_SPACING
    physical.setdefault("contact_model", {}).setdefault("test_only", {}).setdefault(
        "hostile_contact_impedance", {}
    )["active_mode"] = contact_mode

    visualization = settings.setdefault("visualization", {})
    visualization["animate"] = False
    visualization["print_tick_summary"] = False
    visualization["show_attack_target_lines"] = False

    return settings


def _float_metric_equal(expected, actual) -> bool:
    return round(float(expected), 6) == round(float(actual), 6)


def _run_case(base_settings: dict, fixture: dict, steps: int, contact_mode: str) -> dict:
    result = entry_mod.run_active_surface(
        base_dir=TEST_RUN_DIR,
        settings_override=_build_routine_settings(base_settings, fixture, steps, contact_mode),
        emit_summary=False,
    )
    final_state = result["final_state"]
    observer_telemetry = result["observer_telemetry"]
    combat_telemetry = result["combat_telemetry"]

    return {
        "final_tick": int(final_state.tick),
        "alive_a": len(final_state.fleets["A"].unit_ids),
        "alive_b": len(final_state.fleets["B"].unit_ids),
        "winner": _resolve_winner(final_state),
        "first_contact_tick": _first_contact_tick(combat_telemetry),
        "intermix_coverage_t21_120_mean": _mean_window(observer_telemetry["hostile_intermix_coverage"], 21, 120),
        "intermix_severity_t21_120_mean": _mean_window(observer_telemetry["hostile_intermix_severity"], 21, 120),
        "deep_ratio_t21_120_mean": _mean_window(observer_telemetry["hostile_deep_intermix_ratio"], 21, 120),
        "frontcurv_diff_t21_50_mean_abs": _mean_abs_diff(
            observer_telemetry["front_curvature_index"]["A"],
            observer_telemetry["front_curvature_index"]["B"],
            21,
            50,
        ),
        "cw_pshare_diff_t1_20_mean_abs": _mean_abs_diff(
            observer_telemetry["center_wing_parallel_share"]["A"],
            observer_telemetry["center_wing_parallel_share"]["B"],
            1,
            20,
        ),
    }


def main() -> int:
    anchor = json.loads(ANCHOR_PATH.read_text(encoding="utf-8"))
    fixture = anchor["fixtures"][ROUTINE_FIXTURE_ID]
    routine_rows = [row for row in anchor["rows"] if row["fixture"] == ROUTINE_FIXTURE_ID][:ROUTINE_ROW_COUNT]
    if len(routine_rows) != ROUTINE_ROW_COUNT:
        raise ValueError(
            f"expected {ROUTINE_ROW_COUNT} routine rows for fixture {ROUTINE_FIXTURE_ID}, got {len(routine_rows)}"
        )
    base_settings = settings_accessor.load_layered_test_run_settings(TEST_RUN_DIR)

    mismatch_count = 0
    for expected in routine_rows:
        mode = str(expected["mode"])
        actual = _run_case(base_settings, fixture, int(anchor["steps"]), mode)
        mismatches = []
        for key in ROUTINE_METRICS:
            expected_value = expected[key]
            actual_value = actual[key]
            matches = (
                _float_metric_equal(expected_value, actual_value)
                if isinstance(expected_value, float)
                else expected_value == actual_value
            )
            if not matches:
                mismatches.append((key, expected_value, actual_value))

        print(f"[{mode}] {'ok' if not mismatches else 'mismatch'}")
        for key, expected_value, actual_value in mismatches:
            print(f"  {key}: expected={expected_value!r} actual={actual_value!r}")
        mismatch_count += len(mismatches)

    print(f"mismatch_count={mismatch_count}")
    return 0 if mismatch_count == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
