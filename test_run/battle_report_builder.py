from __future__ import annotations

from datetime import datetime
import random
from typing import Any

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

    has_names = bool(
        fleet_a_data.get("disp_name_EN")
        and fleet_b_data.get("disp_name_EN")
        and fleet_a_data.get("full_name_EN")
        and fleet_b_data.get("full_name_EN")
    )

    if has_names:
        commander_a_zh = resolve_name_with_fallback(fleet_a_data, "ZH", True, "A")
        commander_b_zh = resolve_name_with_fallback(fleet_b_data, "ZH", True, "B")
        fleet_a_zh = resolve_name_with_fallback(fleet_a_data, "ZH", False, "A")
        fleet_b_zh = resolve_name_with_fallback(fleet_b_data, "ZH", False, "B")
        commander_a_en = resolve_name_with_fallback(fleet_a_data, "EN", True, "A")
        commander_b_en = resolve_name_with_fallback(fleet_b_data, "EN", True, "B")
        fleet_a_en = resolve_name_with_fallback(fleet_a_data, "EN", False, "A")
        fleet_b_en = resolve_name_with_fallback(fleet_b_data, "EN", False, "B")
    else:
        commander_a_zh = "A"
        commander_b_zh = "B"
        fleet_a_zh = "A"
        fleet_b_zh = "B"
        commander_a_en = "A"
        commander_b_en = "B"
        fleet_a_en = "A"
        fleet_b_en = "B"

    first_contact_tick = first_tick_true(in_contact, lambda v: int(v) > 0)
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

    if winner == "A":
        final_outcome_zh = (
            f"至标准时{tick_to_std_time(end_tick)} (t={end_tick})，{fleet_b_zh}舰队全灭，"
            f"{fleet_a_zh}舰队残余{final_ships_a}艘 (A units={final_units_a})。"
        )
        final_outcome_en = (
            f"By ST {tick_to_std_time(end_tick)} (t={end_tick}), {fleet_b_en} Fleet was eliminated, "
            f"and {fleet_a_en} Fleet retained {final_ships_a} ships (A units={final_units_a})."
        )
    elif winner == "B":
        final_outcome_zh = (
            f"至标准时{tick_to_std_time(end_tick)} (t={end_tick})，{fleet_a_zh}舰队全灭，"
            f"{fleet_b_zh}舰队残余{final_ships_b}艘 (B units={final_units_b})。"
        )
        final_outcome_en = (
            f"By ST {tick_to_std_time(end_tick)} (t={end_tick}), {fleet_a_en} Fleet was eliminated, "
            f"and {fleet_b_en} Fleet retained {final_ships_b} ships (B units={final_units_b})."
        )
    else:
        final_outcome_zh = (
            f"至标准时{tick_to_std_time(end_tick)} (t={end_tick})，战斗结束为平局，"
            f"A残余{final_ships_a}艘 (A units={final_units_a})，"
            f"B残余{final_ships_b}艘 (B units={final_units_b})。"
        )
        final_outcome_en = (
            f"By ST {tick_to_std_time(end_tick)} (t={end_tick}), the battle ended in a draw: "
            f"A retained {final_ships_a} ships (A units={final_units_a}), "
            f"B retained {final_ships_b} ships (B units={final_units_b})."
        )

    events_zh = []
    if first_contact_tick is not None:
        events_zh.append(
            (
                int(first_contact_tick),
                f"双方在标准时{tick_to_std_time(first_contact_tick)} (t={first_contact_tick}) 开始交火。",
            )
        )
    if inflection_tick is not None:
        if inflection_sign > 0:
            side_zh = f"{fleet_a_zh}舰队"
        else:
            side_zh = f"{fleet_b_zh}舰队"

        if first_kill_tick is not None and inflection_tick < first_kill_tick:
            prefix_zh = "在首批建制伤亡前"
        elif first_contact_tick is not None and (inflection_tick - first_contact_tick) <= 10:
            prefix_zh = "在初段接触后"
        elif first_kill_tick is not None and (inflection_tick - first_kill_tick) <= 20:
            prefix_zh = "在早段拉扯后"
        else:
            prefix_zh = "在中段拉扯后"

        events_zh.append(
            (
                int(inflection_tick),
                (
                    f"战线{prefix_zh}，于标准时{tick_to_std_time(inflection_tick)} (t={inflection_tick}) "
                    f"出现优势拐点，{side_zh}逐步掌握主动。"
                ),
            )
        )
    if tactical_swing_summary.get("cluster_count", 0) > 0:
        swing_count = int(tactical_swing_summary.get("cluster_count", 0))
        swing_first = int(tactical_swing_summary.get("first_tick"))
        swing_last = int(tactical_swing_summary.get("last_tick"))
        if swing_count == 1:
            swing_text_zh = (
                f"{fleet_a_zh}舰队与{fleet_b_zh}舰队在标准时{tick_to_std_time(swing_first)} "
                f"(t={swing_first}) 附近出现一次战术拉扯（Alive优势易手）。"
            )
        else:
            swing_text_zh = (
                f"{fleet_a_zh}舰队与{fleet_b_zh}舰队在标准时{tick_to_std_time(swing_first)} (t={swing_first}) "
                f"到 {tick_to_std_time(swing_last)} (t={swing_last}) 间出现{swing_count}次战术拉扯（Alive优势多次易手）。"
            )
        events_zh.append((swing_first, swing_text_zh))
    if first_kill_tick is not None:
        events_zh.append(
            (
                int(first_kill_tick),
                f"双方在标准时{tick_to_std_time(first_kill_tick)} (t={first_kill_tick}) 出现成建制伤亡。",
            )
        )
    if endgame_tick is not None:
        events_zh.append(
            (
                int(endgame_tick),
                f"标准时{tick_to_std_time(endgame_tick)} (t={endgame_tick}) 后，战局进入终盘压制。",
            )
        )
    events_zh.sort(key=lambda item: item[0])

    events_en = []
    if first_contact_tick is not None:
        events_en.append(
            (
                int(first_contact_tick),
                f"The fleets started exchanging fire at ST {tick_to_std_time(first_contact_tick)} (t={first_contact_tick}).",
            )
        )
    if inflection_tick is not None:
        if inflection_sign > 0:
            side_en = f"{fleet_a_en} Fleet"
        else:
            side_en = f"{fleet_b_en} Fleet"

        if first_kill_tick is not None and inflection_tick < first_kill_tick:
            prefix_en = "Before the first organized losses"
        elif first_contact_tick is not None and (inflection_tick - first_contact_tick) <= 10:
            prefix_en = "Shortly after first contact"
        elif first_kill_tick is not None and (inflection_tick - first_kill_tick) <= 20:
            prefix_en = "After early-phase exchanges"
        else:
            prefix_en = "After a mid-line tug of war"

        events_en.append(
            (
                int(inflection_tick),
                (
                    f"{prefix_en}, an advantage inflection appeared at ST "
                    f"{tick_to_std_time(inflection_tick)} (t={inflection_tick}), and {side_en} gradually took initiative."
                ),
            )
        )
    if tactical_swing_summary.get("cluster_count", 0) > 0:
        swing_count = int(tactical_swing_summary.get("cluster_count", 0))
        swing_first = int(tactical_swing_summary.get("first_tick"))
        swing_last = int(tactical_swing_summary.get("last_tick"))
        if swing_count == 1:
            swing_text_en = (
                f"{fleet_a_en} Fleet and {fleet_b_en} Fleet traded local tactical initiative once near "
                f"ST {tick_to_std_time(swing_first)} (t={swing_first}) based on alive-unit lead."
            )
        else:
            swing_text_en = (
                f"{fleet_a_en} Fleet and {fleet_b_en} Fleet traded local tactical initiative {swing_count} times "
                f"between ST {tick_to_std_time(swing_first)} (t={swing_first}) and "
                f"ST {tick_to_std_time(swing_last)} (t={swing_last}) based on alive-unit lead."
            )
        events_en.append((swing_first, swing_text_en))
    if first_kill_tick is not None:
        events_en.append(
            (
                int(first_kill_tick),
                f"Organized losses appeared at ST {tick_to_std_time(first_kill_tick)} (t={first_kill_tick}).",
            )
        )
    if endgame_tick is not None:
        events_en.append(
            (
                int(endgame_tick),
                f"After ST {tick_to_std_time(endgame_tick)} (t={endgame_tick}), the battle entered endgame suppression.",
            )
        )
    events_en.sort(key=lambda item: item[0])

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
    collapse_aligned_with_cut = "N/A"
    formation_cut_tick = bridge_ticks.get("formation_cut_tick")
    if collapse_first_tick_any is not None and isinstance(formation_cut_tick, int):
        collapse_aligned_with_cut = "Yes" if abs(int(collapse_first_tick_any) - int(formation_cut_tick)) <= 1 else "No"

    seed_word = seed_word_from_int(random_seed_effective, length=6)
    initial_units_per_side = int(run_config_snapshot["initial_units_per_side"])
    initial_ships_a = to_ships_ceil(initial_hp_a)
    initial_ships_b = to_ships_ceil(initial_hp_b)

    fixed_lead_zh_lines = [
        f"{seed_word} 星域会战",
        f"{commander_a_zh}(A) vs {commander_b_zh}(B)",
        f"{fleet_a_zh}舰队: {initial_ships_a}艘 (A: {initial_units_per_side} units); {fleet_b_zh}舰队: {initial_ships_b}艘 (B: {initial_units_per_side} units)",
    ]
    fixed_lead_en_lines = [
        f"{seed_word} Starfield Engagement",
        f"{commander_a_en}(A) vs {commander_b_en}(B)",
        f"{fleet_a_en} Fleet: {initial_ships_a} ships (A: {initial_units_per_side} units); {fleet_b_en} Fleet: {initial_ships_b} ships (B: {initial_units_per_side} units)",
    ]

    narrative_zh_body = " ".join(item[1] for item in events_zh) if events_zh else "双方全程未形成有效交火。"
    narrative_en_body = " ".join(item[1] for item in events_en) if events_en else "No effective fire exchange occurred."

    tactical_narrative_zh = "\n".join(fixed_lead_zh_lines) + "\n\n" + narrative_zh_body + f" {final_outcome_zh}"
    tactical_narrative_en = "\n".join(fixed_lead_en_lines) + "\n\n" + narrative_en_body + f" {final_outcome_en}"

    param_keys = [
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

    def format_param_value(v):
        if isinstance(v, (int, float)):
            return f"{float(v):.1f}"
        return "n/a"

    table_header = ["Side", "Archetype", *param_keys]
    archetype_lines = [
        "| " + " | ".join(table_header) + " |",
        "| " + " | ".join(["---"] * len(table_header)) + " |",
        "| " + " | ".join([
            "A",
            str(fleet_a_data.get("name", "A")),
            *[format_param_value(fleet_a_data.get(k)) for k in param_keys],
        ]) + " |",
        "| " + " | ".join([
            "B",
            str(fleet_b_data.get("name", "B")),
            *[format_param_value(fleet_b_data.get(k)) for k in param_keys],
        ]) + " |",
    ]

    report_date = datetime.now().strftime("%Y-%m-%d")
    report_lines = [
        "# Battle Report Framework v1.0",
        "",
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
        "## 2. Operational Timeline",
        "| Event | Tick |",
        "| --- | --- |",
        f"| First Contact | {first_contact_tick if first_contact_tick is not None else 'N/A'} |",
        f"| First Kill | {first_kill_tick if first_kill_tick is not None else 'N/A'} |",
        f"| Formation Cut | {bridge_ticks['formation_cut_tick'] if bridge_ticks['formation_cut_tick'] is not None else 'N/A'} |",
        f"| Pocket Formation | {bridge_ticks['pocket_formation_tick'] if bridge_ticks['pocket_formation_tick'] is not None else 'N/A'} |",
        "| Pursuit Mode | N/A |",
        f"| Inflection | {inflection_tick if inflection_tick is not None else 'N/A'} |",
        f"| Endgame Onset | {endgame_tick if endgame_tick is not None else 'N/A'} |",
        f"| End | {end_tick} |",
        "",
        "## 3. Tactical Narrative (Auto-generated)",
        "### 3.1 Archetypes",
        *archetype_lines,
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
        "## 5. Collapse Analysis",
        f"- Collapse shadow occurred before contact (observer-only, any side): {collapse_before_contact}",
        "- Collapse shadow preceded or aligned with pursuit mode: N/A",
        f"- Collapse shadow aligned with formation cut (|delta_tick|<=1, earliest side): {collapse_aligned_with_cut}",
        "",
    ]
    return "\n".join(report_lines)
