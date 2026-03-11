from __future__ import annotations

from datetime import datetime
import random
import math
from statistics import mean
from typing import Any

from test_run.brf_narrative_messages import BRF_NARRATIVE_MESSAGES, BRF_NARRATIVE_PRIORITIES

ENDGAME_HP_RATIO_DEFAULT = 0.20
STRATEGIC_INFLECTION_SUSTAIN_TICKS = 12
TACTICAL_SWING_SUSTAIN_TICKS = 8
TACTICAL_SWING_MIN_AMPLITUDE = 2.0
TACTICAL_SWING_MIN_GAP_TICKS = 10


def tick_to_std_time(tick: int | None) -> str:
    if tick is None or tick < 0:
        return "--:--"
    hh = tick // 60
    mm = tick % 60
    return f"{hh:02d}:{mm:02d}"


def seed_word_from_int(seed_value: int, length: int = 6) -> str:
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    rng = random.Random(int(seed_value) & 0xFFFFFFFF)
    return "".join(rng.choice(letters) for _ in range(max(1, length)))


def first_tick_true(values, predicate) -> int | None:
    for idx, value in enumerate(values, start=1):
        if predicate(value):
            return idx
    return None


def to_ships_ceil(value: float) -> int:
    v = int(value)
    if float(v) == float(value):
        return max(0, v)
    if value > 0.0:
        return max(0, v + 1)
    return 0


def sign_of(value: float, eps: float = 1e-9) -> int:
    fv = float(value)
    if fv > eps:
        return 1
    if fv < -eps:
        return -1
    return 0


def build_sign_segments(values: list[float], start_tick: int = 1) -> list[dict]:
    if not values:
        return []
    start_idx = max(0, int(start_tick) - 1)
    if start_idx >= len(values):
        return []
    segments: list[dict] = []
    cur_sign = sign_of(values[start_idx])
    cur_start = start_idx
    for idx in range(start_idx + 1, len(values)):
        s = sign_of(values[idx])
        if s != cur_sign:
            seg_values = values[cur_start:idx]
            segments.append(
                {
                    "sign": cur_sign,
                    "start_tick": cur_start + 1,
                    "end_tick": idx,
                    "length": idx - cur_start,
                    "peak_abs": max((abs(float(v)) for v in seg_values), default=0.0),
                }
            )
            cur_sign = s
            cur_start = idx
    seg_values = values[cur_start:]
    segments.append(
        {
            "sign": cur_sign,
            "start_tick": cur_start + 1,
            "end_tick": len(values),
            "length": len(values) - cur_start,
            "peak_abs": max((abs(float(v)) for v in seg_values), default=0.0),
        }
    )
    return segments


def detect_strategic_inflection(
    diff_series: list[float],
    *,
    start_tick: int = 1,
    sustain_ticks: int = STRATEGIC_INFLECTION_SUSTAIN_TICKS,
) -> tuple[int | None, int]:
    segments = build_sign_segments(diff_series, start_tick=start_tick)
    baseline_sign = 0
    for seg in segments:
        seg_sign = int(seg["sign"])
        if seg_sign != 0:
            baseline_sign = seg_sign
            break
    if baseline_sign == 0:
        return (None, 0)

    inflection_tick: int | None = None
    inflection_sign = 0
    for seg in segments:
        seg_sign = int(seg["sign"])
        seg_len = int(seg["length"])
        if seg_sign == 0:
            continue
        if seg_sign == baseline_sign:
            continue
        if seg_len >= int(sustain_ticks):
            inflection_tick = int(seg["start_tick"])
            inflection_sign = seg_sign
            break
    return (inflection_tick, inflection_sign)


def detect_tactical_swing_clusters(
    diff_series: list[float],
    *,
    start_tick: int = 1,
    sustain_ticks: int = TACTICAL_SWING_SUSTAIN_TICKS,
    min_amplitude: float = TACTICAL_SWING_MIN_AMPLITUDE,
    min_gap_ticks: int = TACTICAL_SWING_MIN_GAP_TICKS,
) -> dict:
    segments = build_sign_segments(diff_series, start_tick=start_tick)
    stable_segments = []
    for seg in segments:
        seg_sign = int(seg["sign"])
        seg_len = int(seg["length"])
        seg_amp = float(seg["peak_abs"])
        if seg_sign == 0:
            continue
        if seg_len < int(sustain_ticks):
            continue
        if seg_amp < float(min_amplitude):
            continue
        stable_segments.append(seg)

    swing_ticks: list[int] = []
    last_sign = 0
    for seg in stable_segments:
        seg_sign = int(seg["sign"])
        if last_sign == 0:
            last_sign = seg_sign
            continue
        if seg_sign != last_sign:
            swing_ticks.append(int(seg["start_tick"]))
            last_sign = seg_sign

    clusters: list[dict] = []
    for tick in swing_ticks:
        if not clusters:
            clusters.append({"start_tick": int(tick), "end_tick": int(tick), "count": 1})
            continue
        last = clusters[-1]
        if int(tick) - int(last["end_tick"]) < int(min_gap_ticks):
            last["end_tick"] = int(tick)
            last["count"] = int(last["count"]) + 1
        else:
            clusters.append({"start_tick": int(tick), "end_tick": int(tick), "count": 1})

    return {
        "stable_segments": stable_segments,
        "swing_ticks": swing_ticks,
        "clusters": clusters,
        "cluster_count": len(clusters),
        "first_tick": int(clusters[0]["start_tick"]) if clusters else None,
        "last_tick": int(clusters[-1]["end_tick"]) if clusters else None,
    }


def resolve_name_with_fallback(
    side_data: dict,
    language: str,
    prefer_full_name: bool,
    fallback: str,
) -> str:
    if prefer_full_name:
        key = "full_name_ZH" if language == "ZH" else "full_name_EN"
    else:
        key = "disp_name_ZH" if language == "ZH" else "disp_name_EN"
    value = side_data.get(key)
    if value:
        return str(value)
    if prefer_full_name:
        alt_key = "full_name_EN"
    else:
        alt_key = "disp_name_EN"
    alt = side_data.get(alt_key)
    if alt:
        return str(alt)
    return fallback


PARAMETER_KEYS = [
    "force_concentration_ratio",
    "mobility_bias",
    "offense_defense_weight",
    "risk_appetite",
    "time_preference",
    "targeting_logic",
    "formation_rigidity",
    "perception_radius",
    "pursuit_drive",
    "retreat_threshold",
]


def _format_param_value(value: Any) -> str:
    if isinstance(value, (int, float)):
        return f"{float(value):.1f}"
    return "n/a"


def _resolve_report_names(fleet_a_data: dict, fleet_b_data: dict) -> dict[str, str]:
    has_names = bool(
        fleet_a_data.get("disp_name_EN")
        and fleet_b_data.get("disp_name_EN")
        and fleet_a_data.get("full_name_EN")
        and fleet_b_data.get("full_name_EN")
    )
    if not has_names:
        return {
            "commander_a_zh": "A",
            "commander_b_zh": "B",
            "fleet_a_zh": "A",
            "fleet_b_zh": "B",
            "commander_a_en": "A",
            "commander_b_en": "B",
            "fleet_a_en": "A",
            "fleet_b_en": "B",
        }
    return {
        "commander_a_zh": resolve_name_with_fallback(fleet_a_data, "ZH", True, "A"),
        "commander_b_zh": resolve_name_with_fallback(fleet_b_data, "ZH", True, "B"),
        "fleet_a_zh": resolve_name_with_fallback(fleet_a_data, "ZH", False, "A"),
        "fleet_b_zh": resolve_name_with_fallback(fleet_b_data, "ZH", False, "B"),
        "commander_a_en": resolve_name_with_fallback(fleet_a_data, "EN", True, "A"),
        "commander_b_en": resolve_name_with_fallback(fleet_b_data, "EN", True, "B"),
        "fleet_a_en": resolve_name_with_fallback(fleet_a_data, "EN", False, "A"),
        "fleet_b_en": resolve_name_with_fallback(fleet_b_data, "EN", False, "B"),
    }


def _build_archetype_lines(fleet_a_data: dict, fleet_b_data: dict) -> list[str]:
    table_header = ["Side", "Archetype", *PARAMETER_KEYS]
    return [
        "| " + " | ".join(table_header) + " |",
        "| " + " | ".join(["---"] * len(table_header)) + " |",
        "| " + " | ".join([
            "A",
            str(fleet_a_data.get("name", "A")),
            *[_format_param_value(fleet_a_data.get(k)) for k in PARAMETER_KEYS],
        ]) + " |",
        "| " + " | ".join([
            "B",
            str(fleet_b_data.get("name", "B")),
            *[_format_param_value(fleet_b_data.get(k)) for k in PARAMETER_KEYS],
        ]) + " |",
    ]


def _render_run_configuration_section(
    *,
    settings_source_path: str,
    display_language: str,
    run_config_snapshot: dict[str, Any],
) -> list[str]:
    return [
        "## 0. Run Configuration Snapshot",
        f"- Source settings path: `{settings_source_path}`",
        f"- test_mode: `{run_config_snapshot['test_mode']}` ({run_config_snapshot['test_mode_label']})",
        f"- runtime_decision_source_effective: `{run_config_snapshot.get('runtime_decision_source_effective', 'v2')}`",
        f"- collapse_decision_source_effective: `{run_config_snapshot.get('collapse_decision_source_effective', 'legacy_v2')}`",
        f"- movement_model_effective: `{run_config_snapshot.get('movement_model_effective', 'v3a')}`",
        f"- movement_v3a_experiment_effective: `{run_config_snapshot.get('movement_v3a_experiment_effective', 'base')}`",
        f"- centroid_probe_scale_effective: `{run_config_snapshot.get('centroid_probe_scale_effective', 'N/A')}`",
        f"- random_seed_effective: `{run_config_snapshot.get('random_seed_effective', 'N/A')}`",
        f"- background_map_seed_effective: `{run_config_snapshot.get('background_map_seed_effective', 'N/A')}`",
        f"- metatype_random_seed_effective: `{run_config_snapshot.get('metatype_random_seed_effective', 'N/A')}`",
        f"- display_language: `{display_language}`",
        f"- attack_range: `{run_config_snapshot['attack_range']}`",
        f"- min_unit_spacing: `{run_config_snapshot['min_unit_spacing']}`",
        f"- arena_size: `{run_config_snapshot['arena_size']}`",
        f"- max_time_steps_effective: `{run_config_snapshot['max_time_steps_effective']}`",
        f"- unit_speed: `{run_config_snapshot['unit_speed']}`",
        f"- damage_per_tick: `{run_config_snapshot['damage_per_tick']}`",
        f"- ch_enabled / contact_hysteresis_h: `{run_config_snapshot['ch_enabled']}` / `{run_config_snapshot['contact_hysteresis_h']}`",
        f"- fsr_enabled / fsr_strength: `{run_config_snapshot['fsr_enabled']}` / `{run_config_snapshot['fsr_strength']}`",
        f"- boundary_enabled: `{run_config_snapshot['boundary_enabled']}`",
        f"- boundary_soft_strength: `{run_config_snapshot.get('boundary_soft_strength', 1.0)}`",
        f"- boundary_hard_enabled (requested/effective): "
        f"`{run_config_snapshot.get('boundary_hard_enabled', True)}` / "
        f"`{run_config_snapshot.get('boundary_hard_enabled_effective', run_config_snapshot['boundary_enabled'])}`",
        f"- alpha_sep: `{run_config_snapshot.get('alpha_sep', 0.6)}`",
        "- overrides_applied: none",
        "",
    ]


def _render_header_section(
    *,
    fleet_a_data: dict,
    fleet_b_data: dict,
    initial_units_per_side: int,
    report_date: str,
) -> list[str]:
    return [
        "## 1. Header",
        "- Engine Version: v5.0-alpha5",
        (
            "- Grid Parameters: "
            f"A={fleet_a_data.get('name', 'A')} vs B={fleet_b_data.get('name', 'B')}, "
            f"units_per_side={initial_units_per_side}"
        ),
        "- Determinism Status: Not checked in this single-run export",
        f"- Date: {report_date}",
        "",
    ]


def _render_operational_timeline_section(
    *,
    first_contact_tick: int | None,
    first_kill_tick: int | None,
    formation_cut_tick: int | None,
    pocket_formation_tick: int | None,
    inflection_tick: int | None,
    endgame_tick: int | None,
    end_tick: int,
) -> list[str]:
    return [
        "## 2. Operational Timeline",
        "| Event | Tick |",
        "| --- | --- |",
        f"| First Contact | {first_contact_tick if first_contact_tick is not None else 'N/A'} |",
        f"| First Kill | {first_kill_tick if first_kill_tick is not None else 'N/A'} |",
        f"| Formation Cut | {formation_cut_tick if formation_cut_tick is not None else 'N/A'} |",
        f"| Pocket Formation | {pocket_formation_tick if pocket_formation_tick is not None else 'N/A'} |",
        "| Pursuit Mode | N/A |",
        f"| Inflection | {inflection_tick if inflection_tick is not None else 'N/A'} |",
        f"| Endgame Onset | {endgame_tick if endgame_tick is not None else 'N/A'} |",
        f"| End | {end_tick} |",
        "",
    ]


def _render_precontact_geometry_section(
    precontact_geometry_summary: dict[str, dict[str, Any]],
    first_contact_tick: int | None,
    total_ticks: int,
) -> list[str]:
    return [
        "## 4A. Pre-Contact Geometry / Posture Summary",
        f"- Window: `t=1..{max(1, first_contact_tick - 1) if first_contact_tick is not None else total_ticks}`",
        (
            f"- Side A: Wedge p10/p50/p90=`{_fmt_stat(precontact_geometry_summary['A']['wedge_p10'])}` / "
            f"`{_fmt_stat(precontact_geometry_summary['A']['wedge_p50'])}` / "
            f"`{_fmt_stat(precontact_geometry_summary['A']['wedge_p90'])}`; "
            f"FrontCurv p10/p50/p90=`{_fmt_stat(precontact_geometry_summary['A']['frontcurv_p10'])}` / "
            f"`{_fmt_stat(precontact_geometry_summary['A']['frontcurv_p50'])}` / "
            f"`{_fmt_stat(precontact_geometry_summary['A']['frontcurv_p90'])}`; "
            f"C_W_PShare p10/p50/p90=`{_fmt_stat(precontact_geometry_summary['A']['cw_pshare_p10'])}` / "
            f"`{_fmt_stat(precontact_geometry_summary['A']['cw_pshare_p50'])}` / "
            f"`{_fmt_stat(precontact_geometry_summary['A']['cw_pshare_p90'])}`; "
            f"PosPersist max_abs=`{_fmt_stat(precontact_geometry_summary['A']['pospersist_max_abs'], 1)}`; "
            f"Tendency=`{precontact_geometry_summary['A']['geometry_tendency']}`"
        ),
        (
            f"- Side B: Wedge p10/p50/p90=`{_fmt_stat(precontact_geometry_summary['B']['wedge_p10'])}` / "
            f"`{_fmt_stat(precontact_geometry_summary['B']['wedge_p50'])}` / "
            f"`{_fmt_stat(precontact_geometry_summary['B']['wedge_p90'])}`; "
            f"FrontCurv p10/p50/p90=`{_fmt_stat(precontact_geometry_summary['B']['frontcurv_p10'])}` / "
            f"`{_fmt_stat(precontact_geometry_summary['B']['frontcurv_p50'])}` / "
            f"`{_fmt_stat(precontact_geometry_summary['B']['frontcurv_p90'])}`; "
            f"C_W_PShare p10/p50/p90=`{_fmt_stat(precontact_geometry_summary['B']['cw_pshare_p10'])}` / "
            f"`{_fmt_stat(precontact_geometry_summary['B']['cw_pshare_p50'])}` / "
            f"`{_fmt_stat(precontact_geometry_summary['B']['cw_pshare_p90'])}`; "
            f"PosPersist max_abs=`{_fmt_stat(precontact_geometry_summary['B']['pospersist_max_abs'], 1)}`; "
            f"Tendency=`{precontact_geometry_summary['B']['geometry_tendency']}`"
        ),
        "",
    ]


def _render_front_profile_section(front_profile_quality_summary: dict[str, dict[str, Any]]) -> list[str]:
    return [
        "## 4B. Front Profile Quality Summary",
        (
            f"- Side A: Profile=`{_describe_front_profile(front_profile_quality_summary['A']['profile'])}`; "
            f"FireEff(contact->cut) mean/p90=`{_fmt_stat(front_profile_quality_summary['A']['fire_eff_contact_to_cut_mean'])}` / "
            f"`{_fmt_stat(front_profile_quality_summary['A']['fire_eff_contact_to_cut_p90'])}`; "
            f"WedgePresent=`{'Yes' if front_profile_quality_summary['A']['wedge_present'] else 'No'}`; "
            f"PostureCoherence=`{'Yes' if front_profile_quality_summary['A']['posture_coherence'] else 'No'}`; "
            f"StructuralFragility=`{'Yes' if front_profile_quality_summary['A']['structural_fragility'] else 'No'}`"
        ),
        (
            f"- Side B: Profile=`{_describe_front_profile(front_profile_quality_summary['B']['profile'])}`; "
            f"FireEff(contact->cut) mean/p90=`{_fmt_stat(front_profile_quality_summary['B']['fire_eff_contact_to_cut_mean'])}` / "
            f"`{_fmt_stat(front_profile_quality_summary['B']['fire_eff_contact_to_cut_p90'])}`; "
            f"WedgePresent=`{'Yes' if front_profile_quality_summary['B']['wedge_present'] else 'No'}`; "
            f"PostureCoherence=`{'Yes' if front_profile_quality_summary['B']['posture_coherence'] else 'No'}`; "
            f"StructuralFragility=`{'Yes' if front_profile_quality_summary['B']['structural_fragility'] else 'No'}`"
        ),
        "",
    ]


def _render_event_aligned_section(event_aligned_geometry: dict[str, dict[str, dict[str, float]]]) -> list[str]:
    rows = [
        "## 4C. Event-Aligned Geometry Snapshots",
        "| Event | Side | Wedge | FrontCurv | C_W_PShare | CollapseSig |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for event_label in ("First Contact", "Formation Cut", "Pocket Formation"):
        for side in ("A", "B"):
            event_side = event_aligned_geometry.get(event_label, {}).get(side, {})
            rows.append(
                f"| {event_label} | {side} | "
                f"{_fmt_stat(event_side.get('wedge', float('nan')))} | "
                f"{_fmt_stat(event_side.get('frontcurv', float('nan')))} | "
                f"{_fmt_stat(event_side.get('cw_pshare', float('nan')))} | "
                f"{_fmt_stat(event_side.get('collapse_sig', float('nan')))} |"
            )
    rows.append("")
    return rows


def _render_collapse_analysis_section(
    *,
    collapse_before_contact: str,
    collapse_aligned_with_cut: str,
    runtime_collapse_summary: dict[str, dict[str, float]],
) -> list[str]:
    return [
        "## 5. Collapse Analysis",
        f"- Collapse shadow occurred before contact (observer-only, any side): {collapse_before_contact}",
        "- Collapse shadow preceded or aligned with pursuit mode: N/A",
        f"- Collapse shadow aligned with formation cut (|delta_tick|<=1, earliest side): {collapse_aligned_with_cut}",
        f"- Runtime collapse signal summary A: mean/p95=`{_fmt_stat(runtime_collapse_summary['A']['collapse_sig_mean'])}` / `{_fmt_stat(runtime_collapse_summary['A']['collapse_sig_p95'])}`, c_conn=`{_fmt_stat(runtime_collapse_summary['A']['c_conn_mean'])}`, rho=`{_fmt_stat(runtime_collapse_summary['A']['rho_mean'])}`, c_scale=`{_fmt_stat(runtime_collapse_summary['A']['c_scale_mean'])}`",
        f"- Runtime collapse signal summary B: mean/p95=`{_fmt_stat(runtime_collapse_summary['B']['collapse_sig_mean'])}` / `{_fmt_stat(runtime_collapse_summary['B']['collapse_sig_p95'])}`, c_conn=`{_fmt_stat(runtime_collapse_summary['B']['c_conn_mean'])}`, rho=`{_fmt_stat(runtime_collapse_summary['B']['rho_mean'])}`, c_scale=`{_fmt_stat(runtime_collapse_summary['B']['c_scale_mean'])}`",
        "",
    ]
def compute_bridge_event_ticks(bridge_telemetry: dict | None) -> dict:
    result = {
        "cut_per_side": {"A": None, "B": None},
        "pocket_per_side": {"A": None, "B": None},
        "formation_cut_tick": None,
        "pocket_formation_tick": None,
    }
    if not isinstance(bridge_telemetry, dict):
        return result

    split_ticks = bridge_telemetry.get("first_tick_split_sustain", {})
    env_ticks = bridge_telemetry.get("first_tick_env_sustain", {})
    if not isinstance(split_ticks, dict):
        split_ticks = {}
    if not isinstance(env_ticks, dict):
        env_ticks = {}

    def normalize_tick(raw):
        try:
            tick = int(raw)
        except (TypeError, ValueError):
            return None
        if tick < 1:
            return None
        return tick

    for side in ("A", "B"):
        result["cut_per_side"][side] = normalize_tick(split_ticks.get(side))
        result["pocket_per_side"][side] = normalize_tick(env_ticks.get(side))

    cut_candidates = [v for v in result["cut_per_side"].values() if isinstance(v, int)]
    env_candidates = [v for v in result["pocket_per_side"].values() if isinstance(v, int)]
    result["formation_cut_tick"] = min(cut_candidates) if cut_candidates else None
    result["pocket_formation_tick"] = min(env_candidates) if env_candidates else None
    return result


def _safe_float_or_nan(value: Any) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return float("nan")
    return out


def _finite_values(values: list[Any]) -> list[float]:
    out: list[float] = []
    for value in values:
        fv = _safe_float_or_nan(value)
        if math.isfinite(fv):
            out.append(fv)
    return out


def _quantile(values: list[float], q: float) -> float:
    if not values:
        return float("nan")
    if len(values) == 1:
        return float(values[0])
    qq = min(1.0, max(0.0, float(q)))
    sorted_values = sorted(float(v) for v in values)
    pos = qq * (len(sorted_values) - 1)
    lower = int(math.floor(pos))
    upper = int(math.ceil(pos))
    if lower == upper:
        return float(sorted_values[lower])
    frac = pos - lower
    return float(sorted_values[lower] * (1.0 - frac) + sorted_values[upper] * frac)


def _slice_precontact(series: list[Any], first_contact_tick: int | None) -> list[float]:
    if not series:
        return []
    if isinstance(first_contact_tick, int) and first_contact_tick > 1:
        end_idx = min(len(series), first_contact_tick - 1)
    else:
        end_idx = len(series)
    return _finite_values(list(series[:end_idx]))


def _series_value_at_tick(series: list[Any], tick: int | None) -> float:
    if not isinstance(tick, int) or tick < 1 or tick > len(series):
        return float("nan")
    return _safe_float_or_nan(series[tick - 1])


def _fmt_stat(value: float, digits: int = 3) -> str:
    if not math.isfinite(float(value)):
        return "N/A"
    return f"{float(value):.{digits}f}"


def _describe_geometry_tendency(front_curv_p50: float, cw_pshare_p50: float, pospersist_max_abs: float) -> str:
    if not (math.isfinite(front_curv_p50) and math.isfinite(cw_pshare_p50)):
        return "undetermined"
    if abs(front_curv_p50) < 0.03 and abs(cw_pshare_p50) < 0.03:
        return "flat/neutral"
    if front_curv_p50 >= 0.03 and cw_pshare_p50 >= 0.03:
        return "center-led"
    if front_curv_p50 <= -0.03 and cw_pshare_p50 <= -0.03:
        return "wing-led"
    if math.isfinite(pospersist_max_abs) and pospersist_max_abs >= 10.0:
        return "mixed but persistent"
    return "mixed/unstable"


def _build_precontact_geometry_summary(
    observer_telemetry: dict | None,
    bridge_telemetry: dict | None,
    first_contact_tick: int | None,
) -> dict[str, dict[str, Any]]:
    empty = {
        side: {
            "wedge_p10": float("nan"),
            "wedge_p50": float("nan"),
            "wedge_p90": float("nan"),
            "frontcurv_p10": float("nan"),
            "frontcurv_p50": float("nan"),
            "frontcurv_p90": float("nan"),
            "cw_pshare_p10": float("nan"),
            "cw_pshare_p50": float("nan"),
            "cw_pshare_p90": float("nan"),
            "pospersist_max_abs": float("nan"),
            "geometry_tendency": "undetermined",
        }
        for side in ("A", "B")
    }
    if not isinstance(observer_telemetry, dict) or not isinstance(bridge_telemetry, dict):
        return empty

    front_curv = observer_telemetry.get("front_curvature_index", {})
    cw_pshare = observer_telemetry.get("center_wing_parallel_share", {})
    pospersist = observer_telemetry.get("posture_persistence_time", {})
    wedge = bridge_telemetry.get("wedge_ratio", {})
    if not isinstance(front_curv, dict):
        front_curv = {}
    if not isinstance(cw_pshare, dict):
        cw_pshare = {}
    if not isinstance(pospersist, dict):
        pospersist = {}
    if not isinstance(wedge, dict):
        wedge = {}

    out: dict[str, dict[str, Any]] = {}
    for side in ("A", "B"):
        wedge_pre = _slice_precontact(list(wedge.get(side, [])), first_contact_tick)
        front_pre = _slice_precontact(list(front_curv.get(side, [])), first_contact_tick)
        share_pre = _slice_precontact(list(cw_pshare.get(side, [])), first_contact_tick)
        persist_pre = _slice_precontact(list(pospersist.get(side, [])), first_contact_tick)
        pospersist_max_abs = max((abs(v) for v in persist_pre), default=float("nan"))
        front_p50 = _quantile(front_pre, 0.50)
        share_p50 = _quantile(share_pre, 0.50)
        out[side] = {
            "wedge_p10": _quantile(wedge_pre, 0.10),
            "wedge_p50": _quantile(wedge_pre, 0.50),
            "wedge_p90": _quantile(wedge_pre, 0.90),
            "frontcurv_p10": _quantile(front_pre, 0.10),
            "frontcurv_p50": front_p50,
            "frontcurv_p90": _quantile(front_pre, 0.90),
            "cw_pshare_p10": _quantile(share_pre, 0.10),
            "cw_pshare_p50": share_p50,
            "cw_pshare_p90": _quantile(share_pre, 0.90),
            "pospersist_max_abs": pospersist_max_abs,
            "geometry_tendency": _describe_geometry_tendency(front_p50, share_p50, pospersist_max_abs),
        }
    return out


def _build_event_aligned_snapshots(
    observer_telemetry: dict | None,
    bridge_telemetry: dict | None,
    first_contact_tick: int | None,
    bridge_ticks: dict,
) -> dict[str, dict[str, dict[str, float]]]:
    out = {}
    if not isinstance(observer_telemetry, dict) or not isinstance(bridge_telemetry, dict):
        return out
    front_curv = observer_telemetry.get("front_curvature_index", {})
    cw_pshare = observer_telemetry.get("center_wing_parallel_share", {})
    collapse_sig = observer_telemetry.get("cohesion_v3", {})
    wedge = bridge_telemetry.get("wedge_ratio", {})
    if not isinstance(front_curv, dict):
        front_curv = {}
    if not isinstance(cw_pshare, dict):
        cw_pshare = {}
    if not isinstance(collapse_sig, dict):
        collapse_sig = {}
    if not isinstance(wedge, dict):
        wedge = {}
    event_ticks = {
        "First Contact": first_contact_tick,
        "Formation Cut": bridge_ticks.get("formation_cut_tick"),
        "Pocket Formation": bridge_ticks.get("pocket_formation_tick"),
    }
    for label, tick in event_ticks.items():
        snapshot = {}
        for side in ("A", "B"):
            coh_value = _series_value_at_tick(list(collapse_sig.get(side, [])), tick)
            snapshot[side] = {
                "wedge": _series_value_at_tick(list(wedge.get(side, [])), tick),
                "frontcurv": _series_value_at_tick(list(front_curv.get(side, [])), tick),
                "cw_pshare": _series_value_at_tick(list(cw_pshare.get(side, [])), tick),
                "collapse_sig": (1.0 - coh_value) if math.isfinite(coh_value) else float("nan"),
            }
        out[label] = snapshot
    return out


def _build_runtime_collapse_summary(
    observer_telemetry: dict | None,
    first_contact_tick: int | None,
) -> dict[str, dict[str, float]]:
    empty = {
        side: {
            "collapse_sig_mean": float("nan"),
            "collapse_sig_p95": float("nan"),
            "c_conn_mean": float("nan"),
            "rho_mean": float("nan"),
            "c_scale_mean": float("nan"),
        }
        for side in ("A", "B")
    }
    if not isinstance(observer_telemetry, dict):
        return empty
    cohesion = observer_telemetry.get("cohesion_v3", {})
    c_conn = observer_telemetry.get("c_conn", {})
    rho = observer_telemetry.get("rho", {})
    c_scale = observer_telemetry.get("c_scale", {})
    if not isinstance(cohesion, dict):
        cohesion = {}
    if not isinstance(c_conn, dict):
        c_conn = {}
    if not isinstance(rho, dict):
        rho = {}
    if not isinstance(c_scale, dict):
        c_scale = {}
    out = {}
    for side in ("A", "B"):
        coh_pre = _slice_precontact(list(cohesion.get(side, [])), first_contact_tick)
        collapse_pre = [1.0 - float(v) for v in coh_pre if math.isfinite(float(v))]
        c_conn_pre = _slice_precontact(list(c_conn.get(side, [])), first_contact_tick)
        rho_pre = _slice_precontact(list(rho.get(side, [])), first_contact_tick)
        c_scale_pre = _slice_precontact(list(c_scale.get(side, [])), first_contact_tick)
        out[side] = {
            "collapse_sig_mean": mean(collapse_pre) if collapse_pre else float("nan"),
            "collapse_sig_p95": _quantile(collapse_pre, 0.95),
            "c_conn_mean": mean(c_conn_pre) if c_conn_pre else float("nan"),
            "rho_mean": mean(rho_pre) if rho_pre else float("nan"),
            "c_scale_mean": mean(c_scale_pre) if c_scale_pre else float("nan"),
        }
    return out


def _compute_fire_efficiency_series(
    size_a: list[float],
    size_b: list[float],
    alive_a: list[int],
    alive_b: list[int],
    *,
    per_unit_damage: float,
) -> tuple[list[float], list[float]]:
    n = max(len(size_a), len(size_b), len(alive_a), len(alive_b))
    if n <= 0:
        return ([], [])
    out_a: list[float] = []
    out_b: list[float] = []
    damage_floor = max(0.0, float(per_unit_damage))
    last_size_a = float(size_a[-1]) if size_a else 0.0
    last_size_b = float(size_b[-1]) if size_b else 0.0
    last_alive_a = float(alive_a[-1]) if alive_a else 0.0
    last_alive_b = float(alive_b[-1]) if alive_b else 0.0
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


def _slice_tick_window(series: list[Any], start_tick: int | None, end_tick: int | None) -> list[float]:
    if not series:
        return []
    start_idx = 0 if not isinstance(start_tick, int) or start_tick < 1 else start_tick - 1
    end_idx = len(series) if not isinstance(end_tick, int) or end_tick < 1 else min(len(series), end_tick)
    if end_idx <= start_idx:
        return []
    return _finite_values(list(series[start_idx:end_idx]))


def _compute_front_profile_features(
    *,
    geometry: dict[str, Any],
    collapse: dict[str, float],
    fire_window: list[float],
) -> dict[str, float]:
    return {
        "wedge_p10": _safe_float_or_nan(geometry.get("wedge_p10")),
        "wedge_p50": _safe_float_or_nan(geometry.get("wedge_p50")),
        "wedge_p90": _safe_float_or_nan(geometry.get("wedge_p90")),
        "frontcurv_p50": _safe_float_or_nan(geometry.get("frontcurv_p50")),
        "cw_pshare_p50": _safe_float_or_nan(geometry.get("cw_pshare_p50")),
        "pospersist_max_abs": _safe_float_or_nan(geometry.get("pospersist_max_abs")),
        "collapse_sig_mean": _safe_float_or_nan(collapse.get("collapse_sig_mean")),
        "c_conn_mean": _safe_float_or_nan(collapse.get("c_conn_mean")),
        "fire_eff_mean": mean(fire_window) if fire_window else float("nan"),
        "fire_eff_p90": _quantile(fire_window, 0.90),
    }


def _classify_front_profile(features: dict[str, float]) -> dict[str, Any]:
    wedge_p10 = float(features["wedge_p10"])
    wedge_p50 = float(features["wedge_p50"])
    frontcurv_p50 = float(features["frontcurv_p50"])
    cw_pshare_p50 = float(features["cw_pshare_p50"])
    pospersist = float(features["pospersist_max_abs"])
    collapse_mean = float(features["collapse_sig_mean"])
    c_conn_mean = float(features["c_conn_mean"])
    fire_mean = float(features["fire_eff_mean"])
    fire_p90 = float(features["fire_eff_p90"])

    wedge_present = (
        (math.isfinite(wedge_p10) and wedge_p10 <= 0.70)
        or (
            math.isfinite(wedge_p50)
            and math.isfinite(frontcurv_p50)
            and wedge_p50 <= 0.90
            and frontcurv_p50 >= 0.22
        )
    )
    flat_front = (
        math.isfinite(wedge_p50)
        and math.isfinite(frontcurv_p50)
        and wedge_p50 >= 0.95
        and abs(frontcurv_p50) <= 0.25
    )
    local_penetration = math.isfinite(fire_mean) and fire_mean >= 0.18
    structural_fragility = (
        (math.isfinite(collapse_mean) and collapse_mean >= 0.12)
        or (math.isfinite(c_conn_mean) and c_conn_mean <= 0.90)
    )
    posture_coherence = (
        math.isfinite(cw_pshare_p50)
        and cw_pshare_p50 >= 0.03
        and math.isfinite(pospersist)
        and pospersist >= 5.0
    )

    if wedge_present and local_penetration and posture_coherence and not structural_fragility:
        profile = "coherent_penetration_wedge"
    elif wedge_present and local_penetration and (structural_fragility or not posture_coherence):
        profile = "unstable_penetration_wedge"
    elif wedge_present:
        profile = "wedge_like_deformation"
    elif flat_front:
        profile = "flat_holding_front"
    else:
        profile = "mixed_front"

    return {
        "profile": profile,
        "wedge_present": wedge_present,
        "local_penetration": local_penetration,
        "structural_fragility": structural_fragility,
        "posture_coherence": posture_coherence,
        "fire_eff_contact_to_cut_mean": fire_mean,
        "fire_eff_contact_to_cut_p90": fire_p90,
    }


def _build_front_profile_quality_summary(
    precontact_geometry_summary: dict[str, dict[str, Any]],
    runtime_collapse_summary: dict[str, dict[str, float]],
    *,
    fire_efficiency_series_a: list[float],
    fire_efficiency_series_b: list[float],
    first_contact_tick: int | None,
    formation_cut_tick: int | None,
) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    fire_windows = {
        "A": _slice_tick_window(fire_efficiency_series_a, first_contact_tick, formation_cut_tick),
        "B": _slice_tick_window(fire_efficiency_series_b, first_contact_tick, formation_cut_tick),
    }
    for side in ("A", "B"):
        features = _compute_front_profile_features(
            geometry=precontact_geometry_summary.get(side, {}),
            collapse=runtime_collapse_summary.get(side, {}),
            fire_window=fire_windows.get(side, []),
        )
        out[side] = _classify_front_profile(features)
    return out


def _describe_front_profile(profile: str) -> str:
    mapping = {
        "coherent_penetration_wedge": "coherent penetration wedge",
        "unstable_penetration_wedge": "unstable penetration wedge",
        "wedge_like_deformation": "wedge-like deformation",
        "flat_holding_front": "flat holding front",
        "mixed_front": "mixed front",
    }
    return mapping.get(str(profile), "mixed front")


def _semantic_slot(slot: str, **params: Any) -> dict[str, Any]:
    return {
        "slot": str(slot),
        "priority": int(BRF_NARRATIVE_PRIORITIES.get(str(slot), 999)),
        "params": dict(params),
    }


def _message(language: str, key: str, **params: Any) -> str:
    language_key = "ZH" if str(language).upper() == "ZH" else "EN"
    template = BRF_NARRATIVE_MESSAGES[language_key][key]
    return template.format(**params)


def _message_exists(language: str, key: str) -> bool:
    language_key = "ZH" if str(language).upper() == "ZH" else "EN"
    return key in BRF_NARRATIVE_MESSAGES[language_key]


def _fleet_name(identity: dict[str, Any], side: str, language: str) -> str:
    return str(identity["sides"][side]["fleet"][language])


def _fleet_force_name(identity: dict[str, Any], side: str, language: str) -> str:
    fleet_name = _fleet_name(identity, side, language)
    if language == "ZH":
        return f"{fleet_name}舰队"
    return f"{fleet_name} Fleet"


def _commander_name(identity: dict[str, Any], side: str, language: str) -> str:
    return str(identity["sides"][side]["commander"][language])


def _build_narrative_identity(
    *,
    seed_word: str,
    commander_a_zh: str,
    commander_b_zh: str,
    commander_a_en: str,
    commander_b_en: str,
    fleet_a_zh: str,
    fleet_b_zh: str,
    fleet_a_en: str,
    fleet_b_en: str,
    initial_ships_a: int,
    initial_ships_b: int,
    initial_units_per_side: int,
) -> dict[str, Any]:
    return {
        "seed_word": seed_word,
        "initial_ships": {"A": int(initial_ships_a), "B": int(initial_ships_b)},
        "initial_units_per_side": int(initial_units_per_side),
        "sides": {
            "A": {
                "commander": {"ZH": commander_a_zh, "EN": commander_a_en},
                "fleet": {"ZH": fleet_a_zh, "EN": fleet_a_en},
            },
            "B": {
                "commander": {"ZH": commander_b_zh, "EN": commander_b_en},
                "fleet": {"ZH": fleet_b_zh, "EN": fleet_b_en},
            },
        },
    }


def _build_structural_readout_slots(
    precontact_geometry_summary: dict[str, dict[str, Any]],
    runtime_collapse_summary: dict[str, dict[str, float]],
    front_profile_quality_summary: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    slots: list[dict[str, Any]] = []
    wedge_slot = _build_structural_wedge_slot(precontact_geometry_summary, front_profile_quality_summary)
    if wedge_slot is not None:
        slots.append(wedge_slot)
    slots.extend(_build_structural_profile_slots(front_profile_quality_summary))
    collapse_slot = _build_structural_collapse_slot(runtime_collapse_summary)
    if collapse_slot is not None:
        slots.append(collapse_slot)
    return slots


def _build_structural_wedge_slot(
    precontact_geometry_summary: dict[str, dict[str, Any]],
    front_profile_quality_summary: dict[str, dict[str, Any]],
) -> dict[str, Any] | None:
    wedge_a = _safe_float_or_nan(precontact_geometry_summary.get("A", {}).get("wedge_p50"))
    wedge_b = _safe_float_or_nan(precontact_geometry_summary.get("B", {}).get("wedge_p50"))
    profile_a = str(front_profile_quality_summary.get("A", {}).get("profile", ""))
    profile_b = str(front_profile_quality_summary.get("B", {}).get("profile", ""))
    if math.isfinite(wedge_a) and math.isfinite(wedge_b):
        wedge_delta = wedge_a - wedge_b
        if abs(wedge_delta) >= 0.15:
            lead_side = "A" if wedge_delta < 0 else "B"
            trail_side = "B" if wedge_delta < 0 else "A"
            lead_profile = profile_a if lead_side == "A" else profile_b
            if lead_profile not in {"coherent_penetration_wedge", "unstable_penetration_wedge"}:
                return _semantic_slot("structural_wedge_advantage", lead_side=lead_side, trail_side=trail_side)
    return None


def _build_structural_profile_slots(
    front_profile_quality_summary: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    slots: list[dict[str, Any]] = []
    profile_a = str(front_profile_quality_summary.get("A", {}).get("profile", ""))
    profile_b = str(front_profile_quality_summary.get("B", {}).get("profile", ""))
    if profile_a != profile_b:
        if profile_a == "flat_holding_front":
            slots.append(_semantic_slot("structural_flat_holding_front", side="A"))
        elif profile_b == "flat_holding_front":
            slots.append(_semantic_slot("structural_flat_holding_front", side="B"))

        if profile_a == "coherent_penetration_wedge":
            slots.append(_semantic_slot("structural_coherent_penetration", side="A"))
        elif profile_b == "coherent_penetration_wedge":
            slots.append(_semantic_slot("structural_coherent_penetration", side="B"))

        if profile_a == "unstable_penetration_wedge":
            slots.append(_semantic_slot("structural_unstable_penetration", side="A"))
        elif profile_b == "unstable_penetration_wedge":
            slots.append(_semantic_slot("structural_unstable_penetration", side="B"))
    return slots


def _build_structural_collapse_slot(
    runtime_collapse_summary: dict[str, dict[str, float]],
) -> dict[str, Any] | None:
    collapse_a = _safe_float_or_nan(runtime_collapse_summary.get("A", {}).get("collapse_sig_mean"))
    collapse_b = _safe_float_or_nan(runtime_collapse_summary.get("B", {}).get("collapse_sig_mean"))
    if math.isfinite(collapse_a) and math.isfinite(collapse_b):
        collapse_delta = collapse_a - collapse_b
        if abs(collapse_delta) >= 0.05:
            pressured_side = "A" if collapse_delta > 0 else "B"
            return _semantic_slot("structural_collapse_pressure", pressured_side=pressured_side)
    return None


def _build_tactical_event_slots(
    *,
    first_contact_tick: int | None,
    inflection_tick: int | None,
    inflection_sign: int,
    first_kill_tick: int | None,
    tactical_swing_summary: dict[str, Any],
    endgame_tick: int | None,
) -> list[dict[str, Any]]:
    event_slots: list[dict[str, Any]] = []
    if first_contact_tick is not None:
        event_slots.append(_semantic_slot("event_first_contact", tick=int(first_contact_tick)))
    if inflection_tick is not None:
        if first_kill_tick is not None and inflection_tick < first_kill_tick:
            phase_slot = "phase_before_first_losses"
        elif first_contact_tick is not None and (inflection_tick - first_contact_tick) <= 10:
            phase_slot = "phase_shortly_after_contact"
        elif first_kill_tick is not None and (inflection_tick - first_kill_tick) <= 20:
            phase_slot = "phase_after_early_exchanges"
        else:
            phase_slot = "phase_after_mid_tug"
        event_slots.append(
            _semantic_slot(
                "event_advantage_inflection",
                tick=int(inflection_tick),
                advantaged_side="A" if inflection_sign > 0 else "B",
                phase_slot=phase_slot,
            )
        )
    if tactical_swing_summary.get("cluster_count", 0) > 0:
        swing_count = int(tactical_swing_summary.get("cluster_count", 0))
        swing_first = int(tactical_swing_summary.get("first_tick"))
        swing_last = int(tactical_swing_summary.get("last_tick"))
        if swing_count == 1:
            event_slots.append(_semantic_slot("event_tactical_swing_once", tick=swing_first))
        else:
            event_slots.append(
                _semantic_slot(
                    "event_tactical_swing_multi",
                    tick_start=swing_first,
                    tick_end=swing_last,
                    count=swing_count,
                )
            )
    if first_kill_tick is not None:
        event_slots.append(_semantic_slot("event_organized_losses", tick=int(first_kill_tick)))
    if endgame_tick is not None:
        endgame_narrative_tick = int(endgame_tick)
        if isinstance(inflection_tick, int):
            endgame_narrative_tick = max(endgame_narrative_tick, int(inflection_tick) + 1)
        if tactical_swing_summary.get("cluster_count", 0) > 0 and tactical_swing_summary.get("last_tick") is not None:
            endgame_narrative_tick = max(endgame_narrative_tick, int(tactical_swing_summary.get("last_tick")) + 1)
        event_slots.append(_semantic_slot("event_endgame", tick=endgame_narrative_tick))
    event_slots.sort(key=lambda item: int(item["params"].get("tick", item["params"].get("tick_start", 10**9))))
    return event_slots


def _build_outcome_slot(
    *,
    winner: str,
    end_tick: int,
    final_ships_a: int,
    final_ships_b: int,
    final_units_a: int,
    final_units_b: int,
    initial_units_per_side: int,
) -> dict[str, Any]:
    def _victory_grade(side_units: int) -> str:
        baseline = max(1, int(initial_units_per_side))
        ratio = float(side_units) / float(baseline)
        if ratio >= 0.30:
            return "大胜"
        if ratio >= 0.20:
            return "胜利"
        return "惨胜"

    def _victory_grade_en(side_units: int) -> str:
        baseline = max(1, int(initial_units_per_side))
        ratio = float(side_units) / float(baseline)
        if ratio >= 0.30:
            return "decisive victory"
        if ratio >= 0.20:
            return "victory"
        return "costly victory"

    if winner == "A":
        return _semantic_slot(
            "outcome_a_win",
            tick=end_tick,
            winner_side="A",
            loser_side="B",
            ships=final_ships_a,
            units=final_units_a,
            victory_grade_zh=_victory_grade(final_units_a),
            victory_grade_en=_victory_grade_en(final_units_a),
        )
    if winner == "B":
        return _semantic_slot(
            "outcome_b_win",
            tick=end_tick,
            winner_side="B",
            loser_side="A",
            ships=final_ships_b,
            units=final_units_b,
            victory_grade_zh=_victory_grade(final_units_b),
            victory_grade_en=_victory_grade_en(final_units_b),
        )
    return _semantic_slot(
        "outcome_draw",
        tick=end_tick,
        ships_a=final_ships_a,
        ships_b=final_ships_b,
        units_a=final_units_a,
        units_b=final_units_b,
    )


def _build_battle_narrative_semantics(
    *,
    identity: dict[str, Any],
    event_slots: list[dict[str, Any]],
    structural_slots: list[dict[str, Any]],
    outcome_slot: dict[str, Any],
) -> dict[str, Any]:
    return {
        "identity": identity,
        "opening_state": None if event_slots else _semantic_slot("body_no_effective_fire"),
        "events": event_slots,
        "structural_notes": structural_slots,
        "outcome_summary": outcome_slot,
    }


def _sort_narrative_slots(slots: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ordered_slots = list(slots)
    ordered_slots.sort(
        key=lambda item: (
            int(item.get("priority", 999)),
            int(item.get("params", {}).get("tick", item.get("params", {}).get("tick_start", 10**9))),
        )
    )
    return ordered_slots


def _build_narrative_body_segments(
    *,
    model: dict[str, Any],
    identity: dict[str, Any],
    language: str,
) -> list[str]:
    opening_state = model.get("opening_state")
    if opening_state is not None:
        return [_render_narrative_slot(opening_state, identity, language)]

    body_segments: list[str] = []
    prev_priority: int | None = None
    ordered_slots = _sort_narrative_slots(list(model.get("structural_notes", [])) + list(model.get("events", [])))
    for slot in ordered_slots:
        current_priority = int(slot.get("priority", 999))
        compact = prev_priority == current_priority
        body_segments.append(_render_narrative_slot(slot, identity, language, compact=compact))
        prev_priority = current_priority
    return body_segments


def _render_narrative_slot(slot_data: dict[str, Any], identity: dict[str, Any], language: str, *, compact: bool = False) -> str:
    slot = str(slot_data["slot"])
    params = dict(slot_data.get("params", {}))
    rendered_params: dict[str, Any] = dict(params)
    if "tick" in params:
        rendered_params["time"] = tick_to_std_time(int(params["tick"]))
    if "tick_start" in params:
        rendered_params["time_start"] = tick_to_std_time(int(params["tick_start"]))
    if "tick_end" in params:
        rendered_params["time_end"] = tick_to_std_time(int(params["tick_end"]))
    if slot == "event_advantage_inflection":
        rendered_params["phase_prefix"] = _message(language, str(params["phase_slot"]))
        rendered_params["advantaged_fleet"] = _fleet_name(identity, str(params["advantaged_side"]), language)
        rendered_params["advantaged_force"] = _fleet_force_name(identity, str(params["advantaged_side"]), language)
    elif slot == "event_tactical_swing_once":
        rendered_params["fleet_a"] = _fleet_name(identity, "A", language)
        rendered_params["fleet_b"] = _fleet_name(identity, "B", language)
        rendered_params["force_a"] = _fleet_force_name(identity, "A", language)
        rendered_params["force_b"] = _fleet_force_name(identity, "B", language)
    elif slot == "event_tactical_swing_multi":
        rendered_params["fleet_a"] = _fleet_name(identity, "A", language)
        rendered_params["fleet_b"] = _fleet_name(identity, "B", language)
        rendered_params["force_a"] = _fleet_force_name(identity, "A", language)
        rendered_params["force_b"] = _fleet_force_name(identity, "B", language)
    elif slot == "structural_wedge_advantage":
        rendered_params["lead_fleet"] = _fleet_name(identity, str(params["lead_side"]), language)
        rendered_params["trail_fleet"] = _fleet_name(identity, str(params["trail_side"]), language)
    elif slot == "structural_flat_holding_front":
        rendered_params["fleet_name"] = _fleet_name(identity, str(params["side"]), language)
    elif slot == "structural_coherent_penetration":
        rendered_params["fleet_name"] = _fleet_name(identity, str(params["side"]), language)
    elif slot == "structural_collapse_pressure":
        rendered_params["pressured_fleet"] = _fleet_name(identity, str(params["pressured_side"]), language)
    elif slot == "structural_unstable_penetration":
        rendered_params["fleet_name"] = _fleet_name(identity, str(params["side"]), language)
    elif slot in {"outcome_a_win", "outcome_b_win"}:
        rendered_params["winner_force"] = _fleet_force_name(identity, str(params["winner_side"]), language)
        rendered_params["loser_force"] = _fleet_force_name(identity, str(params["loser_side"]), language)
        rendered_params["time"] = tick_to_std_time(int(params["tick"]))
        rendered_params["victory_grade"] = (
            str(params.get("victory_grade_zh", "胜利"))
            if str(language).upper() == "ZH"
            else str(params.get("victory_grade_en", "victory"))
        )
    elif slot == "outcome_draw":
        rendered_params["time"] = tick_to_std_time(int(params["tick"]))
    compact_key = f"{slot}_compact"
    message_key = compact_key if compact and _message_exists(language, compact_key) else slot
    return _message(language, message_key, **rendered_params)


def _render_narrative_headers(identity: dict[str, Any], language: str) -> list[str]:
    return [
        _message(language, "title", seed_word=identity["seed_word"]),
        _message(
            language,
            "header_matchup",
            commander_a=_commander_name(identity, "A", language),
            commander_b=_commander_name(identity, "B", language),
        ),
        _message(
            language,
            "header_initial_forces",
            fleet_a=_fleet_name(identity, "A", language),
            fleet_b=_fleet_name(identity, "B", language),
            initial_ships_a=identity["initial_ships"]["A"],
            initial_ships_b=identity["initial_ships"]["B"],
            initial_units_per_side=identity["initial_units_per_side"],
        ),
    ]


def _render_battle_narrative(model: dict[str, Any], language: str) -> str:
    identity = model["identity"]
    header_lines = _render_narrative_headers(identity, language)
    body_segments = _build_narrative_body_segments(model=model, identity=identity, language=language)
    outcome_text = _render_narrative_slot(model["outcome_summary"], identity, language)
    body_text = " ".join(segment for segment in body_segments if segment).strip()
    if body_text:
        body_text = f"{body_text} {outcome_text}".strip()
    else:
        body_text = outcome_text
    return "\n".join(header_lines) + "\n\n" + body_text


def _build_report_summaries(
    *,
    observer_telemetry: dict | None,
    bridge_telemetry: dict,
    first_contact_tick: int | None,
    bridge_ticks: dict,
    fire_efficiency_series_a: list[float],
    fire_efficiency_series_b: list[float],
    formation_cut_tick: int | None,
) -> dict[str, Any]:
    precontact_geometry_summary = _build_precontact_geometry_summary(
        observer_telemetry,
        bridge_telemetry,
        first_contact_tick,
    )
    event_aligned_geometry = _build_event_aligned_snapshots(
        observer_telemetry,
        bridge_telemetry,
        first_contact_tick,
        bridge_ticks,
    )
    runtime_collapse_summary = _build_runtime_collapse_summary(observer_telemetry, first_contact_tick)
    front_profile_quality_summary = _build_front_profile_quality_summary(
        precontact_geometry_summary,
        runtime_collapse_summary,
        fire_efficiency_series_a=fire_efficiency_series_a,
        fire_efficiency_series_b=fire_efficiency_series_b,
        first_contact_tick=first_contact_tick,
        formation_cut_tick=formation_cut_tick,
    )
    return {
        "precontact_geometry_summary": precontact_geometry_summary,
        "event_aligned_geometry": event_aligned_geometry,
        "runtime_collapse_summary": runtime_collapse_summary,
        "front_profile_quality_summary": front_profile_quality_summary,
    }


def build_battle_report_markdown(
    *,
    settings_source_path: str,
    display_language: str,
    random_seed_effective: int,
    fleet_a_data: dict,
    fleet_b_data: dict,
    initial_fleet_sizes: dict,
    alive_trajectory: dict,
    fleet_size_trajectory: dict,
    observer_telemetry: dict | None = None,
    combat_telemetry: dict,
    bridge_telemetry: dict,
    collapse_shadow_telemetry: dict,
    final_state: Any,
    run_config_snapshot: dict,
) -> str:
    ticks = list(range(1, len(alive_trajectory.get("A", [])) + 1))
    alive_a = [int(v) for v in alive_trajectory.get("A", [])]
    alive_b = [int(v) for v in alive_trajectory.get("B", [])]
    size_a = [float(v) for v in fleet_size_trajectory.get("A", [])]
    size_b = [float(v) for v in fleet_size_trajectory.get("B", [])]
    in_contact = [int(v) for v in combat_telemetry.get("in_contact_count", [])]
    bridge_ticks = compute_bridge_event_ticks(bridge_telemetry)
    first_contact_tick = first_tick_true(in_contact, lambda v: int(v) > 0)
    fire_efficiency_series_a, fire_efficiency_series_b = _compute_fire_efficiency_series(
        size_a,
        size_b,
        alive_a,
        alive_b,
        per_unit_damage=float(run_config_snapshot.get("damage_per_tick", 1.0)),
    )
    report_summaries = _build_report_summaries(
        observer_telemetry=observer_telemetry,
        bridge_telemetry=bridge_telemetry,
        first_contact_tick=first_contact_tick,
        bridge_ticks=bridge_ticks,
        fire_efficiency_series_a=fire_efficiency_series_a,
        fire_efficiency_series_b=fire_efficiency_series_b,
        formation_cut_tick=bridge_ticks.get("formation_cut_tick"),
    )
    precontact_geometry_summary = report_summaries["precontact_geometry_summary"]
    event_aligned_geometry = report_summaries["event_aligned_geometry"]
    runtime_collapse_summary = report_summaries["runtime_collapse_summary"]
    front_profile_quality_summary = report_summaries["front_profile_quality_summary"]
    strategic_inflection_sustain_ticks = max(
        1,
        int(run_config_snapshot.get("strategic_inflection_sustain_ticks", STRATEGIC_INFLECTION_SUSTAIN_TICKS)),
    )
    tactical_swing_sustain_ticks = max(
        1,
        int(run_config_snapshot.get("tactical_swing_sustain_ticks", TACTICAL_SWING_SUSTAIN_TICKS)),
    )
    tactical_swing_min_amplitude = max(
        0.0,
        float(run_config_snapshot.get("tactical_swing_min_amplitude", TACTICAL_SWING_MIN_AMPLITUDE)),
    )
    tactical_swing_min_gap_ticks = max(
        0,
        int(run_config_snapshot.get("tactical_swing_min_gap_ticks", TACTICAL_SWING_MIN_GAP_TICKS)),
    )

    names = _resolve_report_names(fleet_a_data, fleet_b_data)

    first_kill_tick = first_tick_true(
        ticks,
        lambda i: (
            (alive_a[i - 1] < alive_a[i - 2]) if i > 1 else (alive_a[i - 1] < int(run_config_snapshot["initial_units_per_side"]))
        )
        or (
            (alive_b[i - 1] < alive_b[i - 2]) if i > 1 else (alive_b[i - 1] < int(run_config_snapshot["initial_units_per_side"]))
        ),
    )
    size_diff = [float(a) - float(b) for a, b in zip(size_a, size_b)]
    inflection_scan_start = first_contact_tick if first_contact_tick is not None else 1
    inflection_tick, inflection_sign = detect_strategic_inflection(
        size_diff,
        start_tick=inflection_scan_start,
        sustain_ticks=strategic_inflection_sustain_ticks,
    )
    alive_diff = [float(a) - float(b) for a, b in zip(alive_a, alive_b)]
    tactical_scan_start = first_kill_tick if first_kill_tick is not None else (first_contact_tick if first_contact_tick is not None else 1)
    tactical_swing_summary = detect_tactical_swing_clusters(
        alive_diff,
        start_tick=tactical_scan_start,
        sustain_ticks=tactical_swing_sustain_ticks,
        min_amplitude=tactical_swing_min_amplitude,
        min_gap_ticks=tactical_swing_min_gap_ticks,
    )

    initial_hp_a = float(initial_fleet_sizes.get("A", 0.0))
    initial_hp_b = float(initial_fleet_sizes.get("B", 0.0))
    endgame_tick = first_tick_true(
        ticks,
        lambda i: (
            size_a[i - 1] <= (initial_hp_a * ENDGAME_HP_RATIO_DEFAULT)
            or size_b[i - 1] <= (initial_hp_b * ENDGAME_HP_RATIO_DEFAULT)
        ),
    )

    end_tick = int(final_state.tick)
    final_hp_a = float(size_a[-1]) if size_a else 0.0
    final_hp_b = float(size_b[-1]) if size_b else 0.0
    final_units_a = int(alive_a[-1]) if alive_a else 0
    final_units_b = int(alive_b[-1]) if alive_b else 0
    final_ships_a = to_ships_ceil(final_hp_a)
    final_ships_b = to_ships_ceil(final_hp_b)

    winner = "A"
    if final_hp_b > final_hp_a:
        winner = "B"
    elif abs(final_hp_a - final_hp_b) <= 1e-9:
        winner = "Draw"

    collapse_first_ticks = []
    if isinstance(collapse_shadow_telemetry, dict):
        first_tick_map = collapse_shadow_telemetry.get("first_tick_collapse_v2_shadow", {})
        if isinstance(first_tick_map, dict):
            raw_a = first_tick_map.get("A")
            raw_b = first_tick_map.get("B")
            if isinstance(raw_a, int):
                collapse_first_ticks.append(int(raw_a))
            if isinstance(raw_b, int):
                collapse_first_ticks.append(int(raw_b))
    collapse_first_tick_any = min(collapse_first_ticks) if collapse_first_ticks else None
    collapse_before_contact = "N/A"
    if collapse_first_tick_any is not None and first_contact_tick is not None:
        collapse_before_contact = "Yes" if collapse_first_tick_any < first_contact_tick else "No"
    formation_cut_tick = bridge_ticks.get("formation_cut_tick")
    collapse_aligned_with_cut = "N/A"
    if collapse_first_tick_any is not None and isinstance(formation_cut_tick, int):
        collapse_aligned_with_cut = "Yes" if abs(int(collapse_first_tick_any) - int(formation_cut_tick)) <= 1 else "No"

    initial_units_per_side = int(run_config_snapshot["initial_units_per_side"])
    identity = _build_narrative_identity(
        seed_word=seed_word_from_int(random_seed_effective, length=6),
        commander_a_zh=names["commander_a_zh"],
        commander_b_zh=names["commander_b_zh"],
        commander_a_en=names["commander_a_en"],
        commander_b_en=names["commander_b_en"],
        fleet_a_zh=names["fleet_a_zh"],
        fleet_b_zh=names["fleet_b_zh"],
        fleet_a_en=names["fleet_a_en"],
        fleet_b_en=names["fleet_b_en"],
        initial_ships_a=to_ships_ceil(initial_hp_a),
        initial_ships_b=to_ships_ceil(initial_hp_b),
        initial_units_per_side=initial_units_per_side,
    )
    structural_slots = _build_structural_readout_slots(
        precontact_geometry_summary,
        runtime_collapse_summary,
        front_profile_quality_summary,
    )
    event_slots = _build_tactical_event_slots(
        first_contact_tick=first_contact_tick,
        inflection_tick=inflection_tick,
        inflection_sign=inflection_sign,
        first_kill_tick=first_kill_tick,
        tactical_swing_summary=tactical_swing_summary,
        endgame_tick=endgame_tick,
    )
    outcome_slot = _build_outcome_slot(
        winner=winner,
        end_tick=end_tick,
        final_ships_a=final_ships_a,
        final_ships_b=final_ships_b,
        final_units_a=final_units_a,
        final_units_b=final_units_b,
        initial_units_per_side=initial_units_per_side,
    )
    narrative_model = _build_battle_narrative_semantics(
        identity=identity,
        event_slots=event_slots,
        structural_slots=structural_slots,
        outcome_slot=outcome_slot,
    )
    tactical_narrative_zh = _render_battle_narrative(narrative_model, "ZH")
    tactical_narrative_en = _render_battle_narrative(narrative_model, "EN")

    report_lines = [
        "# Battle Report Framework v1.0",
        "",
        *_render_run_configuration_section(
            settings_source_path=settings_source_path,
            display_language=display_language,
            run_config_snapshot=run_config_snapshot,
        ),
        *_render_header_section(
            fleet_a_data=fleet_a_data,
            fleet_b_data=fleet_b_data,
            initial_units_per_side=initial_units_per_side,
            report_date=datetime.now().strftime("%Y-%m-%d"),
        ),
        *_render_operational_timeline_section(
            first_contact_tick=first_contact_tick,
            first_kill_tick=first_kill_tick,
            formation_cut_tick=formation_cut_tick,
            pocket_formation_tick=bridge_ticks.get("pocket_formation_tick"),
            inflection_tick=inflection_tick,
            endgame_tick=endgame_tick,
            end_tick=end_tick,
        ),
        "## 3. Tactical Narrative (Auto-generated)",
        "### 3.1 Archetypes",
        *_build_archetype_lines(fleet_a_data, fleet_b_data),
        "",
        "### 3.2 ZH Narrative",
        tactical_narrative_zh,
        "",
        "### 3.3 EN Narrative",
        tactical_narrative_en,
        "",
        "## 4. Structural Metrics Summary",
        "- Mirror delta: N/A",
        "- Jitter delta: N/A",
        "- Runtime delta: N/A",
        "- Cohesion behavior summary: Runtime path unchanged; this export is observer/report-layer only.",
        "",
        *_render_precontact_geometry_section(precontact_geometry_summary, first_contact_tick, len(ticks)),
        *_render_front_profile_section(front_profile_quality_summary),
        *_render_event_aligned_section(event_aligned_geometry),
        *_render_collapse_analysis_section(
            collapse_before_contact=collapse_before_contact,
            collapse_aligned_with_cut=collapse_aligned_with_cut,
            runtime_collapse_summary=runtime_collapse_summary,
        ),
    ]
    return "\n".join(report_lines)
