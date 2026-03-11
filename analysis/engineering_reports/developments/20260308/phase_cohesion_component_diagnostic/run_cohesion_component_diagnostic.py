import copy
import csv
import hashlib
import importlib.util
import json
import math
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
ANALYSIS_SRC = ROOT / "test_run" / "test_run_v1_0.py"

spec = importlib.util.spec_from_file_location("test_run_module", ANALYSIS_SRC)
test_run = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(test_run)


OUT_DIR = Path(__file__).resolve().parent
SEED_PROFILE = {
    "seed_profile_id": "SP01",
    "random_seed_effective": 1981813971,
    "background_map_seed_effective": 897304369,
    "metatype_random_seed_effective": 3095987153,
}
OPPONENT_COUNT = 3
SOURCES = ["v2", "v3_test"]
CELLS = [
    (2, 2, 5),
    (2, 5, 5),
    (2, 8, 5),
    (5, 2, 5),
    (5, 5, 5),
    (5, 8, 5),
    (8, 2, 5),
    (8, 5, 5),
    (8, 8, 5),
    (5, 5, 2),
    (5, 5, 8),
]
REPRESENTATIVE_CASE = (5, 5, 5)
REPRESENTATIVE_OPPONENT_INDEX = 0
EPS = 1e-12
RHO_LOW = 0.35
RHO_HIGH = 1.15
PENALTY_K = 6.0


def finite(values):
    out = []
    for value in values:
        try:
            fv = float(value)
        except (TypeError, ValueError):
            continue
        if math.isfinite(fv):
            out.append(fv)
    return out


def mean_or_nan(values):
    vals = finite(values)
    if not vals:
        return float("nan")
    return sum(vals) / float(len(vals))


def quantile_or_nan(values, q):
    vals = sorted(finite(values))
    if not vals:
        return float("nan")
    if q <= 0.0:
        return vals[0]
    if q >= 1.0:
        return vals[-1]
    pos = (len(vals) - 1) * float(q)
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return vals[lo]
    frac = pos - lo
    return vals[lo] * (1.0 - frac) + vals[hi] * frac


def quantile_sorted(sorted_values, q):
    if not sorted_values:
        return 0.0
    if q <= 0.0:
        return sorted_values[0]
    if q >= 1.0:
        return sorted_values[-1]
    pos = (len(sorted_values) - 1) * q
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return sorted_values[lo]
    w = pos - lo
    return (sorted_values[lo] * (1.0 - w)) + (sorted_values[hi] * w)


def clamp01(value):
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return value


def first_positive_tick(values):
    for idx, value in enumerate(values, start=1):
        try:
            if float(value) > 0.0:
                return idx
        except (TypeError, ValueError):
            continue
    return None


def parse_tick(value):
    if value in (None, "", "N/A"):
        return None
    try:
        iv = int(value)
    except (TypeError, ValueError):
        return None
    return iv if iv >= 1 else None


def first_kill_tick_from_alive(alive_a, alive_b):
    n = max(len(alive_a), len(alive_b))
    if n <= 0:
        return None
    base_a = int(alive_a[0]) if alive_a else 0
    base_b = int(alive_b[0]) if alive_b else 0
    for idx in range(n):
        a = int(alive_a[idx]) if idx < len(alive_a) else (int(alive_a[-1]) if alive_a else 0)
        b = int(alive_b[idx]) if idx < len(alive_b) else (int(alive_b[-1]) if alive_b else 0)
        if a < base_a or b < base_b:
            return idx + 1
    return None


def select_canonical_opponents(archetypes: dict, count: int) -> list[str]:
    selected = []
    for archetype_id, data in archetypes.items():
        normalized = str(archetype_id).strip().lower()
        if normalized in {"default", "yang"}:
            continue
        if not isinstance(data, dict):
            continue
        try:
            for key in test_run.PERSONALITY_PARAM_KEYS:
                test_run._personality_value_from_data(data, key)
        except KeyError:
            continue
        selected.append(str(archetype_id))
        if len(selected) >= count:
            break
    if len(selected) < count:
        raise ValueError(f"Need {count} canonical opponents, found {len(selected)}")
    return selected


def build_test_vector(fr: float, mb: float, pd: float) -> dict:
    return {
        "force_concentration_ratio": 5.0,
        "formation_rigidity": float(fr),
        "mobility_bias": float(mb),
        "offense_defense_weight": 5.0,
        "perception_radius": 5.0,
        "pursuit_drive": float(pd),
        "retreat_threshold": 5.0,
        "risk_appetite": 5.0,
        "targeting_logic": 5.0,
        "time_preference": 5.0,
    }


def vector_to_archetype(name: str, vector: dict) -> dict:
    out = {
        "name": str(name),
        "disp_name_EN": str(name),
        "disp_name_ZH": str(name),
        "full_name_EN": f"{name} Fleet",
        "full_name_ZH": str(name),
    }
    for key in test_run.PERSONALITY_PARAM_KEYS:
        out[key] = float(vector[key])
    return out


def state_digest(final_state) -> str:
    h = hashlib.sha256()
    h.update(f"tick={int(final_state.tick)}|arena={float(final_state.arena_size):.6f}".encode("utf-8"))
    for fleet_id in sorted(final_state.fleets.keys()):
        fleet = final_state.fleets[fleet_id]
        h.update(f"|fleet={fleet_id}|alive={len(fleet.unit_ids)}".encode("utf-8"))
        cohesion_value = float(final_state.last_fleet_cohesion.get(fleet_id, 0.0))
        h.update(f"|cohesion={cohesion_value:.8f}".encode("utf-8"))
    return h.hexdigest()


def compute_v2_components(positions: list[tuple[float, float]], separation_radius: float) -> dict:
    n_alive = len(positions)
    if n_alive == 0:
        return {
            "cohesion_v2": 0.0,
            "fragmentation": 1.0,
            "dispersion": 0.0,
            "outlier_mass": 0.0,
            "elongation": 0.0,
            "lcc_ratio": 0.0,
            "dispersion_ratio_q90_q50": 1.0,
        }
    centroid_x = sum(x for x, _ in positions) / n_alive
    centroid_y = sum(y for _, y in positions) / n_alive
    radii = []
    cov_xx = 0.0
    cov_xy = 0.0
    cov_yy = 0.0
    for x, y in positions:
        dx = x - centroid_x
        dy = y - centroid_y
        radii.append(math.sqrt((dx * dx) + (dy * dy)))
        cov_xx += dx * dx
        cov_xy += dx * dy
        cov_yy += dy * dy
    cov_xx /= n_alive
    cov_xy /= n_alive
    cov_yy /= n_alive

    sorted_radii = sorted(radii)
    q25 = quantile_sorted(sorted_radii, 0.25)
    q50 = quantile_sorted(sorted_radii, 0.50)
    q75 = quantile_sorted(sorted_radii, 0.75)
    q90 = quantile_sorted(sorted_radii, 0.90)
    iqr = max(0.0, q75 - q25)

    if q90 <= EPS and q50 <= EPS:
        dispersion_ratio = 1.0
        f_disp = 0.0
    else:
        dispersion_ratio = max(1.0, q90 / (q50 + EPS))
        f_disp = clamp01(1.0 - (1.0 / dispersion_ratio))

    outlier_threshold = q75 + (1.5 * iqr)
    outlier_count = sum(1 for r in radii if r > outlier_threshold)
    f_out = clamp01(outlier_count / n_alive)

    trace = cov_xx + cov_yy
    det = (cov_xx * cov_yy) - (cov_xy * cov_xy)
    disc = max(0.0, (trace * trace) - (4.0 * det))
    sqrt_disc = math.sqrt(disc)
    lambda_1 = 0.5 * (trace + sqrt_disc)
    lambda_2 = 0.5 * (trace - sqrt_disc)
    if lambda_1 < EPS:
        f_elong = 0.0
    else:
        f_elong = clamp01(1.0 - (lambda_2 / (lambda_1 + EPS)))

    if n_alive == 1:
        lcc_ratio = 1.0
    else:
        connect_radius_sq = max(EPS, separation_radius) ** 2
        visited = [False] * n_alive
        largest_component_size = 0
        for i in range(n_alive):
            if visited[i]:
                continue
            visited[i] = True
            stack = [i]
            component_size = 0
            while stack:
                node = stack.pop()
                component_size += 1
                nx, ny = positions[node]
                for j in range(n_alive):
                    if visited[j] or j == node:
                        continue
                    px, py = positions[j]
                    ddx = nx - px
                    ddy = ny - py
                    if (ddx * ddx) + (ddy * ddy) <= connect_radius_sq:
                        visited[j] = True
                        stack.append(j)
            largest_component_size = max(largest_component_size, component_size)
        lcc_ratio = largest_component_size / n_alive
    f_frag = clamp01(1.0 - lcc_ratio)

    exploitability = 1.0 - ((1.0 - f_frag) * (1.0 - f_disp) * (1.0 - f_out) * (1.0 - f_elong))
    cohesion_v2 = clamp01(1.0 - exploitability)
    return {
        "cohesion_v2": cohesion_v2,
        "fragmentation": f_frag,
        "dispersion": f_disp,
        "outlier_mass": f_out,
        "elongation": f_elong,
        "lcc_ratio": lcc_ratio,
        "dispersion_ratio_q90_q50": dispersion_ratio,
    }


def compute_v3_components(positions: list[tuple[float, float]], separation_radius: float) -> dict:
    n_alive = len(positions)
    if n_alive == 0:
        return {
            "c_v3": 0.0,
            "c_conn": 0.0,
            "c_scale": 1.0,
            "rho": 0.0,
            "lcc_ratio": 0.0,
        }
    centroid_x = sum(x for x, _ in positions) / n_alive
    centroid_y = sum(y for _, y in positions) / n_alive
    radius_sq_sum = 0.0
    for x, y in positions:
        dx = x - centroid_x
        dy = y - centroid_y
        radius_sq_sum += (dx * dx) + (dy * dy)
    r = math.sqrt(radius_sq_sum / n_alive)
    r_ref = float(separation_radius) * math.sqrt(float(n_alive))
    rho = 0.0 if r_ref <= EPS else r / r_ref

    if rho < RHO_LOW:
        c_scale = math.exp(-PENALTY_K * ((RHO_LOW - rho) ** 2))
    elif rho <= RHO_HIGH:
        c_scale = 1.0
    else:
        c_scale = math.exp(-PENALTY_K * ((rho - RHO_HIGH) ** 2))

    if n_alive == 1:
        c_conn = 1.0
    else:
        connect_radius_sq = max(EPS, separation_radius) ** 2
        visited = [False] * n_alive
        largest_component_size = 0
        for i in range(n_alive):
            if visited[i]:
                continue
            visited[i] = True
            stack = [i]
            component_size = 0
            while stack:
                node = stack.pop()
                component_size += 1
                nx, ny = positions[node]
                for j in range(n_alive):
                    if visited[j] or j == node:
                        continue
                    px, py = positions[j]
                    ddx = nx - px
                    ddy = ny - py
                    if (ddx * ddx) + (ddy * ddy) <= connect_radius_sq:
                        visited[j] = True
                        stack.append(j)
            largest_component_size = max(largest_component_size, component_size)
        c_conn = largest_component_size / n_alive
    return {
        "c_v3": clamp01(c_conn * c_scale),
        "c_conn": c_conn,
        "c_scale": c_scale,
        "rho": rho,
        "lcc_ratio": c_conn,
    }


def positions_by_tick(position_frames: list[dict], side: str) -> list[tuple[int, list[tuple[float, float]]]]:
    out = []
    for frame in position_frames:
        tick = int(frame.get("tick", 0))
        raw_points = frame.get(side, [])
        positions = [(float(p[1]), float(p[2])) for p in raw_points if len(p) >= 3]
        out.append((tick, positions))
    out.sort(key=lambda item: item[0])
    return out


def summarize_side(prefix: str, component_rows: list[dict]) -> dict:
    penalties = {
        "fragmentation": mean_or_nan([r["fragmentation"] for r in component_rows]),
        "dispersion": mean_or_nan([r["dispersion"] for r in component_rows]),
        "outlier_mass": mean_or_nan([r["outlier_mass"] for r in component_rows]),
        "elongation": mean_or_nan([r["elongation"] for r in component_rows]),
    }
    dominant_v2_penalty = max(penalties.items(), key=lambda item: item[1])[0] if component_rows else "N/A"
    rho_vals = [r["rho"] for r in component_rows]
    n = len(component_rows)
    rho_low_pct = (100.0 * sum(1 for v in rho_vals if math.isfinite(v) and v < RHO_LOW) / float(n)) if n else float("nan")
    rho_band_pct = (100.0 * sum(1 for v in rho_vals if math.isfinite(v) and RHO_LOW <= v <= RHO_HIGH) / float(n)) if n else float("nan")
    rho_high_pct = (100.0 * sum(1 for v in rho_vals if math.isfinite(v) and v > RHO_HIGH) / float(n)) if n else float("nan")
    return {
        f"{prefix}_precontact_ticks": n,
        f"{prefix}_v2_mean": mean_or_nan([r["cohesion_v2"] for r in component_rows]),
        f"{prefix}_v2_p10": quantile_or_nan([r["cohesion_v2"] for r in component_rows], 0.10),
        f"{prefix}_v2_p90": quantile_or_nan([r["cohesion_v2"] for r in component_rows], 0.90),
        f"{prefix}_fragmentation_mean": penalties["fragmentation"],
        f"{prefix}_dispersion_mean": penalties["dispersion"],
        f"{prefix}_outlier_mass_mean": penalties["outlier_mass"],
        f"{prefix}_elongation_mean": penalties["elongation"],
        f"{prefix}_dominant_v2_penalty": dominant_v2_penalty,
        f"{prefix}_v3_mean": mean_or_nan([r["c_v3"] for r in component_rows]),
        f"{prefix}_v3_p10": quantile_or_nan([r["c_v3"] for r in component_rows], 0.10),
        f"{prefix}_v3_p90": quantile_or_nan([r["c_v3"] for r in component_rows], 0.90),
        f"{prefix}_c_conn_mean": mean_or_nan([r["c_conn"] for r in component_rows]),
        f"{prefix}_c_scale_mean": mean_or_nan([r["c_scale"] for r in component_rows]),
        f"{prefix}_rho_mean": mean_or_nan(rho_vals),
        f"{prefix}_rho_lt_low_pct": rho_low_pct,
        f"{prefix}_rho_in_band_pct": rho_band_pct,
        f"{prefix}_rho_gt_high_pct": rho_high_pct,
    }


def build_delta_row(v2_row: dict, v3_row: dict) -> dict:
    def delta(key):
        try:
            return float(v3_row[key]) - float(v2_row[key])
        except (TypeError, ValueError):
            return float("nan")

    return {
        "cell_FR": v2_row["cell_FR"],
        "cell_MB": v2_row["cell_MB"],
        "cell_PD": v2_row["cell_PD"],
        "opponent_archetype_name": v2_row["opponent_archetype_name"],
        "delta_first_contact_tick": delta("first_contact_tick"),
        "delta_first_kill_tick": delta("first_kill_tick"),
        "delta_cut_tick": delta("cut_tick"),
        "delta_pocket_tick": delta("pocket_tick"),
        "delta_A_v2_mean": delta("A_v2_mean"),
        "delta_A_fragmentation_mean": delta("A_fragmentation_mean"),
        "delta_A_dispersion_mean": delta("A_dispersion_mean"),
        "delta_A_outlier_mass_mean": delta("A_outlier_mass_mean"),
        "delta_A_elongation_mean": delta("A_elongation_mean"),
        "delta_A_v3_mean": delta("A_v3_mean"),
        "delta_A_c_conn_mean": delta("A_c_conn_mean"),
        "delta_A_c_scale_mean": delta("A_c_scale_mean"),
        "delta_A_rho_mean": delta("A_rho_mean"),
        "delta_B_v2_mean": delta("B_v2_mean"),
        "delta_B_v3_mean": delta("B_v3_mean"),
        "delta_B_c_scale_mean": delta("B_c_scale_mean"),
        "delta_B_rho_mean": delta("B_rho_mean"),
    }


def write_csv(path: Path, rows: list[dict]):
    if not rows:
        return
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def run_single_case(settings: dict, archetypes: dict, opponent_name: str, opponent_index: int, fr: int, mb: int, pd: int, source: str):
    fleet_size = int(test_run.get_fleet_setting(settings, "initial_fleet_size", 100))
    aspect_ratio = float(test_run.get_fleet_setting(settings, "initial_fleet_aspect_ratio", 2.0))
    unit_spacing = float(test_run.get_battlefield_setting(settings, "min_unit_spacing", 2.0))
    unit_speed = float(test_run.get_unit_setting(settings, "unit_speed", 1.0))
    unit_hp = float(test_run.get_unit_setting(settings, "unit_max_hit_points", 100.0))
    arena_size = float(test_run.get_battlefield_setting(settings, "arena_size", 200.0))
    attack_range = float(test_run.get_unit_setting(settings, "attack_range", test_run.get_runtime_setting(settings, "attack_range", 5.0)))
    damage_per_tick = float(test_run.get_unit_setting(settings, "damage_per_tick", test_run.get_runtime_setting(settings, "damage_per_tick", 1.0)))
    fire_quality_alpha = float(test_run.get_runtime_setting(settings, "fire_quality_alpha", 0.1))
    contact_hysteresis_h = float(test_run.get_runtime_setting(settings, "contact_hysteresis_h", 0.1))
    fsr_strength = float(test_run.get_runtime_setting(settings, "fsr_strength", 0.1))
    movement_model_requested, movement_model_effective = test_run.resolve_movement_model(test_run.get_runtime_setting(settings, "movement_model", "baseline"))
    movement_v3a_experiment = str(test_run.get_runtime_setting(settings, "movement_v3a_experiment", "base")).strip().lower() or "base"
    centroid_probe_scale = float(test_run.get_runtime_setting(settings, "centroid_probe_scale", 1.0))

    test_vector = build_test_vector(fr=float(fr), mb=float(mb), pd=float(pd))
    opponent_data = dict(archetypes[opponent_name])

    state = test_run.build_initial_state(
        fleet_a_params=test_run.to_personality_parameters(vector_to_archetype(f"test_FR{fr}_MB{mb}_PD{pd}", test_vector)),
        fleet_b_params=test_run.to_personality_parameters(opponent_data),
        fleet_size=fleet_size,
        aspect_ratio=aspect_ratio,
        unit_spacing=unit_spacing,
        unit_speed=unit_speed,
        unit_max_hit_points=unit_hp,
        arena_size=arena_size,
    )

    (
        final_state,
        trajectory,
        alive_trajectory,
        _fleet_size_trajectory,
        _observer_telemetry,
        combat_telemetry,
        bridge_telemetry,
        _collapse_shadow_telemetry,
        position_frames,
    ) = test_run.run_simulation(
        initial_state=state,
        steps=-1,
        capture_positions=True,
        observer_enabled=True,
        runtime_decision_source=source,
        movement_model=movement_model_effective,
        bridge_theta_split=float(test_run.get_runtime_setting(settings, "bridge_theta_split", 1.7)),
        bridge_theta_env=float(test_run.get_runtime_setting(settings, "bridge_theta_env", 0.5)),
        bridge_sustain_ticks=int(test_run.get_runtime_setting(settings, "bridge_sustain_ticks", 20)),
        collapse_shadow_theta_conn_default=float(test_run.get_runtime_setting(settings, "collapse_shadow_theta_conn_default", 0.10)),
        collapse_shadow_theta_coh_default=float(test_run.get_runtime_setting(settings, "collapse_shadow_theta_coh_default", 0.98)),
        collapse_shadow_theta_force_default=float(test_run.get_runtime_setting(settings, "collapse_shadow_theta_force_default", 0.95)),
        collapse_shadow_theta_attr_default=float(test_run.get_runtime_setting(settings, "collapse_shadow_theta_attr_default", 0.10)),
        collapse_shadow_attrition_window=int(test_run.get_runtime_setting(settings, "collapse_shadow_attrition_window", 20)),
        collapse_shadow_sustain_ticks=int(test_run.get_runtime_setting(settings, "collapse_shadow_sustain_ticks", 10)),
        collapse_shadow_min_conditions=int(test_run.get_runtime_setting(settings, "collapse_shadow_min_conditions", 2)),
        frame_stride=1,
        attack_range=attack_range,
        damage_per_tick=damage_per_tick,
        separation_radius=unit_spacing,
        fire_quality_alpha=fire_quality_alpha,
        contact_hysteresis_h=contact_hysteresis_h,
        ch_enabled=(contact_hysteresis_h > 0.0),
        fsr_enabled=(fsr_strength > 0.0),
        fsr_strength=fsr_strength,
        boundary_enabled=False,
        boundary_hard_enabled=False,
        include_target_lines=False,
        print_tick_summary=False,
        plot_diagnostics_enabled=False,
        boundary_soft_strength=1.0,
        movement_v3a_experiment=movement_v3a_experiment,
        centroid_probe_scale=centroid_probe_scale,
        runtime_diag_enabled=False,
    )

    first_contact_tick = first_positive_tick(combat_telemetry.get("in_contact_count", []))
    first_kill_tick = first_kill_tick_from_alive(alive_trajectory.get("A", []), alive_trajectory.get("B", []))
    bridge_ticks = test_run.compute_bridge_event_ticks(bridge_telemetry)
    cut_tick = parse_tick(bridge_ticks.get("formation_cut_tick"))
    pocket_tick = parse_tick(bridge_ticks.get("pocket_formation_tick"))
    precontact_end_tick = min(100, (first_contact_tick - 1) if first_contact_tick is not None else 100)

    side_rows = {"A": [], "B": []}
    for side in ("A", "B"):
        for tick, positions in positions_by_tick(position_frames, side):
            if tick < 1 or tick > precontact_end_tick:
                continue
            row_v2 = compute_v2_components(positions, separation_radius=unit_spacing)
            row_v3 = compute_v3_components(positions, separation_radius=unit_spacing)
            side_rows[side].append({"tick": tick, **row_v2, **row_v3})

    run_row = {
        "run_id": f"FR{fr}_MB{mb}_PD{pd}_{opponent_name}_{source}",
        "runtime_decision_source_effective": source,
        "movement_model_requested": movement_model_requested,
        "movement_model_effective": movement_model_effective,
        "movement_v3a_experiment_effective": movement_v3a_experiment if movement_model_effective == "v3a" else "N/A",
        "centroid_probe_scale_effective": centroid_probe_scale if movement_model_effective == "v3a" else "N/A",
        "seed_profile_id": SEED_PROFILE["seed_profile_id"],
        "random_seed_effective": SEED_PROFILE["random_seed_effective"],
        "background_map_seed_effective": SEED_PROFILE["background_map_seed_effective"],
        "metatype_random_seed_effective": SEED_PROFILE["metatype_random_seed_effective"],
        "cell_FR": fr,
        "cell_MB": mb,
        "cell_PD": pd,
        "opponent_archetype_name": opponent_name,
        "opponent_archetype_index": opponent_index,
        "first_contact_tick": first_contact_tick,
        "first_kill_tick": first_kill_tick,
        "cut_tick": cut_tick,
        "pocket_tick": pocket_tick,
        "precontact_end_tick": precontact_end_tick,
        "determinism_digest": state_digest(final_state),
    }
    run_row.update(summarize_side("A", side_rows["A"]))
    run_row.update(summarize_side("B", side_rows["B"]))
    return run_row, side_rows


def load_json_file(path: Path):
    with path.open("r", encoding="utf-8-sig") as f:
        return json.load(f)


def paired_key(row: dict) -> tuple:
    return (
        int(row["cell_FR"]),
        int(row["cell_MB"]),
        int(row["cell_PD"]),
        str(row["opponent_archetype_name"]),
        str(row["seed_profile_id"]),
    )


def aggregate_cell_summary(run_rows: list[dict]) -> list[dict]:
    grouped: dict[tuple, list[dict]] = defaultdict(list)
    for row in run_rows:
        key = (
            str(row["runtime_decision_source_effective"]),
            int(row["cell_FR"]),
            int(row["cell_MB"]),
            int(row["cell_PD"]),
        )
        grouped[key].append(row)

    out = []
    for key in sorted(grouped.keys()):
        source, fr, mb, pd = key
        rows = grouped[key]
        dominant_counts = defaultdict(int)
        rho_driver_counts = defaultdict(int)
        for row in rows:
            dominant_counts[str(row["A_dominant_v2_penalty"])] += 1
            lt_low = float(row["A_rho_lt_low_pct"])
            in_band = float(row["A_rho_in_band_pct"])
            gt_high = float(row["A_rho_gt_high_pct"])
            if math.isfinite(in_band) and in_band >= max(lt_low, gt_high):
                rho_driver_counts["in_band"] += 1
            elif math.isfinite(gt_high) and gt_high > lt_low:
                rho_driver_counts["gt_high"] += 1
            else:
                rho_driver_counts["lt_low"] += 1
        out.append(
            {
                "runtime_decision_source_effective": source,
                "cell_FR": fr,
                "cell_MB": mb,
                "cell_PD": pd,
                "runs": len(rows),
                "first_contact_tick_mean": mean_or_nan([r["first_contact_tick"] for r in rows]),
                "first_kill_tick_mean": mean_or_nan([r["first_kill_tick"] for r in rows]),
                "cut_tick_mean": mean_or_nan([r["cut_tick"] for r in rows]),
                "pocket_tick_mean": mean_or_nan([r["pocket_tick"] for r in rows]),
                "A_v2_mean_mean": mean_or_nan([r["A_v2_mean"] for r in rows]),
                "A_fragmentation_mean_mean": mean_or_nan([r["A_fragmentation_mean"] for r in rows]),
                "A_dispersion_mean_mean": mean_or_nan([r["A_dispersion_mean"] for r in rows]),
                "A_outlier_mass_mean_mean": mean_or_nan([r["A_outlier_mass_mean"] for r in rows]),
                "A_elongation_mean_mean": mean_or_nan([r["A_elongation_mean"] for r in rows]),
                "A_v3_mean_mean": mean_or_nan([r["A_v3_mean"] for r in rows]),
                "A_c_conn_mean_mean": mean_or_nan([r["A_c_conn_mean"] for r in rows]),
                "A_c_scale_mean_mean": mean_or_nan([r["A_c_scale_mean"] for r in rows]),
                "A_rho_mean_mean": mean_or_nan([r["A_rho_mean"] for r in rows]),
                "A_rho_lt_low_pct_mean": mean_or_nan([r["A_rho_lt_low_pct"] for r in rows]),
                "A_rho_in_band_pct_mean": mean_or_nan([r["A_rho_in_band_pct"] for r in rows]),
                "A_rho_gt_high_pct_mean": mean_or_nan([r["A_rho_gt_high_pct"] for r in rows]),
                "dominant_v2_penalty_fragmentation": dominant_counts["fragmentation"],
                "dominant_v2_penalty_dispersion": dominant_counts["dispersion"],
                "dominant_v2_penalty_outlier_mass": dominant_counts["outlier_mass"],
                "dominant_v2_penalty_elongation": dominant_counts["elongation"],
                "rho_driver_lt_low": rho_driver_counts["lt_low"],
                "rho_driver_in_band": rho_driver_counts["in_band"],
                "rho_driver_gt_high": rho_driver_counts["gt_high"],
            }
        )
    return out


def build_timeline_rows(source_side_rows: dict[str, dict[str, list[dict]]]) -> list[dict]:
    ticks = set()
    for source_map in source_side_rows.values():
        for rows in source_map.values():
            ticks.update(int(r["tick"]) for r in rows)
    out = []
    for tick in sorted(ticks):
        row = {"tick": tick}
        for source in SOURCES:
            for side in ("A", "B"):
                source_rows = source_side_rows.get(source, {}).get(side, [])
                tick_row = next((r for r in source_rows if int(r["tick"]) == tick), None)
                prefix = f"{source}_{side}"
                if tick_row is None:
                    values = {
                        "cohesion_v2": float("nan"),
                        "fragmentation": float("nan"),
                        "dispersion": float("nan"),
                        "outlier_mass": float("nan"),
                        "elongation": float("nan"),
                        "c_v3": float("nan"),
                        "c_conn": float("nan"),
                        "c_scale": float("nan"),
                        "rho": float("nan"),
                    }
                else:
                    values = tick_row
                row[f"{prefix}_cohesion_v2"] = values["cohesion_v2"]
                row[f"{prefix}_fragmentation"] = values["fragmentation"]
                row[f"{prefix}_dispersion"] = values["dispersion"]
                row[f"{prefix}_outlier_mass"] = values["outlier_mass"]
                row[f"{prefix}_elongation"] = values["elongation"]
                row[f"{prefix}_c_v3"] = values["c_v3"]
                row[f"{prefix}_c_conn"] = values["c_conn"]
                row[f"{prefix}_c_scale"] = values["c_scale"]
                row[f"{prefix}_rho"] = values["rho"]
        out.append(row)
    return out


def build_report(
    run_rows: list[dict],
    delta_rows: list[dict],
    cell_summary_rows: list[dict],
    opponents: list[str],
    timeline_filename: str,
) -> str:
    by_source = defaultdict(list)
    for row in run_rows:
        by_source[str(row["runtime_decision_source_effective"])].append(row)

    def penalty_counts(source: str) -> str:
        counts = defaultdict(int)
        for row in by_source.get(source, []):
            counts[str(row["A_dominant_v2_penalty"])] += 1
        ordered = ["elongation", "dispersion", "outlier_mass", "fragmentation"]
        return ", ".join(f"{name}={counts[name]}" for name in ordered)

    def source_mean(source: str, key: str) -> float:
        return mean_or_nan([row[key] for row in by_source.get(source, [])])

    delta_contact = mean_or_nan([row["delta_first_contact_tick"] for row in delta_rows])
    delta_cut = mean_or_nan([row["delta_cut_tick"] for row in delta_rows])
    delta_pocket = mean_or_nan([row["delta_pocket_tick"] for row in delta_rows])
    top_cases = sorted(
        delta_rows,
        key=lambda row: abs(float(row["delta_A_v2_mean"])) if math.isfinite(float(row["delta_A_v2_mean"])) else -1.0,
        reverse=True,
    )[:5]
    top_case_lines = []
    for row in top_cases:
        top_case_lines.append(
            f"- FR{row['cell_FR']}_MB{row['cell_MB']}_PD{row['cell_PD']} vs {row['opponent_archetype_name']}: "
            f"ΔA_v2_mean={float(row['delta_A_v2_mean']):+.4f}, "
            f"ΔA_v3_mean={float(row['delta_A_v3_mean']):+.4f}, "
            f"Δcontact={float(row['delta_first_contact_tick']):+.1f}"
        )

    return "\n".join(
        [
            "# Cohesion Component Diagnostic Report",
            "",
            f"- Runs: {len(run_rows)}",
            f"- Cells: {len(CELLS)}",
            f"- Opponents: {', '.join(opponents)}",
            f"- Sources: {', '.join(SOURCES)}",
            f"- Seed profile: {SEED_PROFILE['seed_profile_id']} "
            f"(random={SEED_PROFILE['random_seed_effective']}, "
            f"background={SEED_PROFILE['background_map_seed_effective']}, "
            f"metatype={SEED_PROFILE['metatype_random_seed_effective']})",
            "",
            "## Global Findings",
            "",
            f"- `v2` pre-contact mean (Side A): {source_mean('v2', 'A_v2_mean'):.4f}",
            f"- `v3_test-run` pre-contact mean `v2` score on realized geometry (Side A): {source_mean('v3_test', 'A_v2_mean'):.4f}",
            f"- `v2` dominant penalty counts (Side A): {penalty_counts('v2')}",
            f"- `v3_test-run` dominant penalty counts (Side A): {penalty_counts('v3_test')}",
            f"- `v2` Side A mean `c_conn`: {source_mean('v2', 'A_c_conn_mean'):.4f}",
            f"- `v2` Side A mean `c_scale`: {source_mean('v2', 'A_c_scale_mean'):.4f}",
            f"- `v2` Side A mean rho band percentages: "
            f"lt_low={source_mean('v2', 'A_rho_lt_low_pct'):.2f}%, "
            f"in_band={source_mean('v2', 'A_rho_in_band_pct'):.2f}%, "
            f"gt_high={source_mean('v2', 'A_rho_gt_high_pct'):.2f}%",
            f"- `v3_test-run` Side A mean `c_conn`: {source_mean('v3_test', 'A_c_conn_mean'):.4f}",
            f"- `v3_test-run` Side A mean `c_scale`: {source_mean('v3_test', 'A_c_scale_mean'):.4f}",
            f"- `v3_test-run` Side A mean rho band percentages: "
            f"lt_low={source_mean('v3_test', 'A_rho_lt_low_pct'):.2f}%, "
            f"in_band={source_mean('v3_test', 'A_rho_in_band_pct'):.2f}%, "
            f"gt_high={source_mean('v3_test', 'A_rho_gt_high_pct'):.2f}%",
            "",
            "## Paired Source Effects",
            "",
            f"- Mean Δ first_contact_tick (v3_test - v2): {delta_contact:+.3f}",
            f"- Mean Δ cut_tick (v3_test - v2): {delta_cut:+.3f}",
            f"- Mean Δ pocket_tick (v3_test - v2): {delta_pocket:+.3f}",
            f"- Mean Δ A_v2_mean on realized geometry: {mean_or_nan([row['delta_A_v2_mean'] for row in delta_rows]):+.4f}",
            f"- Mean Δ A_fragmentation_mean: {mean_or_nan([row['delta_A_fragmentation_mean'] for row in delta_rows]):+.4f}",
            f"- Mean Δ A_dispersion_mean: {mean_or_nan([row['delta_A_dispersion_mean'] for row in delta_rows]):+.4f}",
            f"- Mean Δ A_outlier_mass_mean: {mean_or_nan([row['delta_A_outlier_mass_mean'] for row in delta_rows]):+.4f}",
            f"- Mean Δ A_elongation_mean: {mean_or_nan([row['delta_A_elongation_mean'] for row in delta_rows]):+.4f}",
            f"- Mean Δ A_v3_mean on realized geometry: {mean_or_nan([row['delta_A_v3_mean'] for row in delta_rows]):+.4f}",
            f"- Mean Δ A_c_scale_mean: {mean_or_nan([row['delta_A_c_scale_mean'] for row in delta_rows]):+.4f}",
            f"- Mean Δ A_rho_mean: {mean_or_nan([row['delta_A_rho_mean'] for row in delta_rows]):+.4f}",
            "",
            "## Interpretation",
            "",
            "- If `elongation` dominates the v2 penalty counts, low early `cohesion_v2` is mainly a shape-semantics issue rather than fragmentation.",
            "- If `c_conn` stays near 1.0 while `c_scale` is materially below 1.0, low `cohesion_v3_shadow` is driven mainly by scale mismatch (`rho`), not by connectivity failure.",
            "- The paired deltas above indicate whether switching the runtime source materially reshapes pre-contact geometry or mostly changes collapse/pursuit interpretation.",
            "",
            "## Largest Paired Cases",
            "",
            *(top_case_lines or ["- None"]),
            "",
            "## Representative Timeline",
            "",
            f"- `{timeline_filename}`",
        ]
    )


def main() -> None:
    settings = load_json_file(ROOT / "test_run" / "test_run_v1_0.settings.json")
    archetypes = load_json_file(ROOT / "archetypes" / "archetypes_v1_5.json")
    opponents = select_canonical_opponents(archetypes, OPPONENT_COUNT)

    base_settings = copy.deepcopy(settings)
    run_control = base_settings.setdefault("run_control", {})
    run_control["random_seed"] = int(SEED_PROFILE["random_seed_effective"])
    run_control["metatype_random_seed"] = int(SEED_PROFILE["metatype_random_seed_effective"])
    battlefield = base_settings.setdefault("battlefield", {})
    battlefield["background_map_seed"] = int(SEED_PROFILE["background_map_seed_effective"])
    runtime = base_settings.setdefault("runtime", {})
    selectors = runtime.setdefault("selectors", {})
    selectors["movement_model"] = "baseline"
    selectors["cohesion_decision_source"] = "baseline"
    boundary = runtime.setdefault("boundary", {})
    boundary["enabled"] = False
    boundary["soft_strength"] = 1.0
    boundary["hard_enabled"] = False

    run_rows = []
    representative_side_rows: dict[str, dict[str, list[dict]]] = {}
    for fr, mb, pd in CELLS:
        for opponent_index, opponent_name in enumerate(opponents, start=1):
            for source in SOURCES:
                row, side_rows = run_single_case(
                    settings=copy.deepcopy(base_settings),
                    archetypes=archetypes,
                    opponent_name=opponent_name,
                    opponent_index=opponent_index,
                    fr=fr,
                    mb=mb,
                    pd=pd,
                    source=source,
                )
                run_rows.append(row)
                if (fr, mb, pd) == REPRESENTATIVE_CASE and opponent_index == REPRESENTATIVE_OPPONENT_INDEX + 1:
                    representative_side_rows[source] = side_rows

    run_rows.sort(key=lambda r: (int(r["cell_FR"]), int(r["cell_MB"]), int(r["cell_PD"]), int(r["opponent_archetype_index"]), str(r["runtime_decision_source_effective"])))
    by_key = {}
    for row in run_rows:
        by_key[(paired_key(row), str(row["runtime_decision_source_effective"]))] = row
    delta_rows = []
    for row in run_rows:
        if str(row["runtime_decision_source_effective"]) != "v2":
            continue
        key = paired_key(row)
        partner = by_key.get((key, "v3_test"))
        if partner is None:
            continue
        delta_rows.append(build_delta_row(row, partner))
    delta_rows.sort(key=lambda r: (int(r["cell_FR"]), int(r["cell_MB"]), int(r["cell_PD"]), str(r["opponent_archetype_name"])))

    cell_summary_rows = aggregate_cell_summary(run_rows)
    cell_summary_rows.sort(key=lambda r: (str(r["runtime_decision_source_effective"]), int(r["cell_FR"]), int(r["cell_MB"]), int(r["cell_PD"])))

    timeline_rows = build_timeline_rows(representative_side_rows)
    timeline_filename = f"cohesion_component_diagnostic_timeline_FR{REPRESENTATIVE_CASE[0]}_MB{REPRESENTATIVE_CASE[1]}_PD{REPRESENTATIVE_CASE[2]}_{opponents[REPRESENTATIVE_OPPONENT_INDEX]}.csv"

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_csv(OUT_DIR / "cohesion_component_diagnostic_run_table.csv", run_rows)
    write_csv(OUT_DIR / "cohesion_component_diagnostic_delta_table.csv", delta_rows)
    write_csv(OUT_DIR / "cohesion_component_diagnostic_cell_summary.csv", cell_summary_rows)
    write_csv(OUT_DIR / timeline_filename, timeline_rows)

    report_text = build_report(run_rows, delta_rows, cell_summary_rows, opponents, timeline_filename)
    (OUT_DIR / "cohesion_component_diagnostic_report.md").write_text(report_text, encoding="utf-8")

    print(f"Completed cohesion component diagnostic runs: {len(run_rows)}")
    print(f"Opponents: {', '.join(opponents)}")
    print(f"Outputs: {OUT_DIR}")


if __name__ == "__main__":
    main()
