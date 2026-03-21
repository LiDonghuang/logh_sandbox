"""
Legacy collapse-signal semantics micro-batch helper.

Scope:
- semantic connectivity radius review for collapse-signal runtime source
- controlled persona assumes non-factor personality parameters fixed at 5.0

Do not reuse this helper as a generic runner for new personality-mechanism reviews
such as ODW/TL. New mechanism lines must define their own bounded harness.
"""

import copy
import csv
import importlib.util
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
ANALYSIS_SRC = ROOT / "test_run" / "test_run_v1_0.py"
SOURCE_DOE_SRC = Path(__file__).resolve().parent / "run_cohesion_source_doe.py"
COMP_DIAG_SRC = ROOT / "analysis" / "engineering_reports" / "developments" / "20260308" / "phase_cohesion_component_diagnostic" / "run_cohesion_component_diagnostic.py"


def load_module(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


test_run = load_module(ANALYSIS_SRC, "test_run_module")
source_doe = load_module(SOURCE_DOE_SRC, "cohesion_source_doe_module")
comp_diag = load_module(COMP_DIAG_SRC, "cohesion_component_diag_module")


OUT_DIR = Path(__file__).resolve().parent
FR_LEVELS = [2, 5, 8]
MB_LEVELS = [2, 5, 8]
PD_FIXED = 5
SOURCES = ["v2", "v3_test"]
SEMANTIC_CONNECTIVITY_LEVELS = {
    "v2": [1.0, 1.5, 2.0, 2.5, 3.0],
    "v3_test": [1.0, 1.1, 1.2, 1.3, 1.4, 1.5],
}
SEED_PROFILE = {
    "seed_profile_id": "SP01",
    "random_seed_effective": 1981813971,
    "background_map_seed_effective": 897304369,
    "metatype_random_seed_effective": 3095987153,
}


def load_json_file(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_csv(path: Path, rows: list[dict]):
    if not rows:
        return
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def select_first_canonical_opponent(archetypes: dict) -> str:
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
        return str(archetype_id)
    raise ValueError("No canonical opponent found")


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


def run_single_case(settings: dict, archetypes: dict, opponent_name: str, fr: int, mb: int, pd: int, source: str, semantic_multiplier: float) -> dict:
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
    movement_model_requested, movement_model_effective = test_run.resolve_movement_model(
        test_run.get_runtime_setting(settings, "movement_model", "baseline")
    )
    movement_v3a_experiment = str(test_run.get_runtime_setting(settings, "movement_v3a_experiment", "base")).strip().lower() or "base"
    centroid_probe_scale = float(test_run.get_runtime_setting(settings, "centroid_probe_scale", 1.0))

    v2_multiplier = float(semantic_multiplier if source == "v2" else 1.0)
    v3_multiplier = float(semantic_multiplier if source == "v3_test" else 1.0)
    v3_ref_multiplier = 1.0

    test_vector = build_test_vector(fr=float(fr), mb=float(mb), pd=float(pd))
    opponent_data = dict(archetypes[opponent_name])
    opponent_pd = float(test_run._personality_value_from_data(opponent_data, "pursuit_drive"))

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

    execution_cfg = test_run.SimulationExecutionConfig(
        steps=-1,
        capture_positions=True,
        frame_stride=1,
        include_target_lines=False,
        print_tick_summary=False,
        plot_diagnostics_enabled=False,
    )
    runtime_cfg = test_run.SimulationRuntimeConfig(
        decision_source=source,
        movement_model=movement_model_effective,
        movement=test_run.SimulationMovementConfig(
            v3a_experiment=movement_v3a_experiment,
            centroid_probe_scale=centroid_probe_scale,
            v2_connect_radius_multiplier=v2_multiplier,
            v3_connect_radius_multiplier=v3_multiplier,
            v3_r_ref_radius_multiplier=v3_ref_multiplier,
        ),
        contact=test_run.SimulationContactConfig(
            attack_range=attack_range,
            damage_per_tick=damage_per_tick,
            separation_radius=unit_spacing,
            fire_quality_alpha=fire_quality_alpha,
            contact_hysteresis_h=contact_hysteresis_h,
            ch_enabled=(contact_hysteresis_h > 0.0),
            fsr_enabled=(fsr_strength > 0.0),
            fsr_strength=fsr_strength,
        ),
        boundary=test_run.SimulationBoundaryConfig(
            enabled=False,
            hard_enabled=False,
            soft_strength=1.0,
        ),
    )
    observer_cfg = test_run.SimulationObserverConfig(
        enabled=True,
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
        engine_cls=test_run.TestModeEngineTickSkeleton,
        execution_cfg=execution_cfg,
        runtime_cfg=runtime_cfg,
        observer_cfg=observer_cfg,
    )

    first_contact_tick = source_doe.first_positive_tick(combat_telemetry.get("in_contact_count", []))
    first_kill_tick = source_doe.first_kill_tick_from_alive(alive_trajectory.get("A", []), alive_trajectory.get("B", []))
    bridge_ticks = test_run.compute_bridge_event_ticks(bridge_telemetry)
    cut_tick = source_doe.parse_tick(bridge_ticks.get("formation_cut_tick"))
    pocket_tick = source_doe.parse_tick(bridge_ticks.get("pocket_formation_tick"))
    precontact_end_tick = min(100, (first_contact_tick - 1) if first_contact_tick is not None else 100)
    runtime_signal_metrics, _ = source_doe.compute_runtime_signal_metrics(trajectory, pd_a=pd, pd_b=opponent_pd)

    side_metrics = {}
    for side in ("A", "B"):
        v2_rows = []
        v3_rows = []
        for tick, positions in comp_diag.positions_by_tick(position_frames, side):
            if tick < 1 or tick > precontact_end_tick:
                continue
            v2_rows.append(comp_diag.compute_v2_components(positions, separation_radius=unit_spacing * v2_multiplier))
            v3_rows.append(comp_diag.compute_v3_components(positions, separation_radius=unit_spacing * v3_multiplier * v3_ref_multiplier))
        side_metrics[side] = {
            "v2_mean": comp_diag.mean_or_nan([r["cohesion_v2"] for r in v2_rows]),
            "fragmentation_mean": comp_diag.mean_or_nan([r["fragmentation"] for r in v2_rows]),
            "dispersion_mean": comp_diag.mean_or_nan([r["dispersion"] for r in v2_rows]),
            "elongation_mean": comp_diag.mean_or_nan([r["elongation"] for r in v2_rows]),
            "v3_mean": comp_diag.mean_or_nan([r["c_v3"] for r in v3_rows]),
            "c_conn_mean": comp_diag.mean_or_nan([r["c_conn"] for r in v3_rows]),
            "c_scale_mean": comp_diag.mean_or_nan([r["c_scale"] for r in v3_rows]),
            "rho_mean": comp_diag.mean_or_nan([r["rho"] for r in v3_rows]),
        }

    ar_a = source_doe.precontact_focus_slice(bridge_telemetry.get("AR", {}).get("A", []), first_contact_tick)
    wedge_a = source_doe.precontact_focus_slice(bridge_telemetry.get("wedge_ratio", {}).get("A", []), first_contact_tick)
    split_a = source_doe.precontact_focus_slice(bridge_telemetry.get("split_separation", {}).get("A", []), first_contact_tick)

    return {
        "run_id": f"FR{fr}_MB{mb}_PD{pd}_{opponent_name}_{source}_m{semantic_multiplier:.1f}",
        "seed_profile_id": SEED_PROFILE["seed_profile_id"],
        "opponent_archetype_name": opponent_name,
        "runtime_decision_source_effective": source,
        "semantic_connectivity_multiplier": semantic_multiplier,
        "v2_connect_radius_multiplier": v2_multiplier,
        "v3_connect_radius_multiplier": v3_multiplier,
        "v3_r_ref_radius_multiplier": v3_ref_multiplier,
        "movement_model_requested": movement_model_requested,
        "movement_model_effective": movement_model_effective,
        "movement_v3a_experiment_effective": movement_v3a_experiment if movement_model_effective == "v3a" else "N/A",
        "centroid_probe_scale_effective": centroid_probe_scale if movement_model_effective == "v3a" else "N/A",
        "cell_FR": fr,
        "cell_MB": mb,
        "cell_PD": pd,
        "random_seed_effective": SEED_PROFILE["random_seed_effective"],
        "background_map_seed_effective": SEED_PROFILE["background_map_seed_effective"],
        "metatype_random_seed_effective": SEED_PROFILE["metatype_random_seed_effective"],
        "first_contact_tick": first_contact_tick,
        "first_kill_tick": first_kill_tick,
        "cut_tick": cut_tick,
        "pocket_tick": pocket_tick,
        "first_deep_pursuit_tick_A": runtime_signal_metrics["A"]["first_deep_pursuit_tick"],
        "first_deep_pursuit_tick_B": runtime_signal_metrics["B"]["first_deep_pursuit_tick"],
        "pct_ticks_deep_pursuit_A": runtime_signal_metrics["A"]["pct_ticks_deep_pursuit"],
        "pct_ticks_deep_pursuit_B": runtime_signal_metrics["B"]["pct_ticks_deep_pursuit"],
        "mean_pursuit_intensity_A": runtime_signal_metrics["A"]["mean_pursuit_intensity"],
        "mean_pursuit_intensity_B": runtime_signal_metrics["B"]["mean_pursuit_intensity"],
        "mean_enemy_collapse_signal_A": runtime_signal_metrics["A"]["mean_enemy_collapse_signal"],
        "mean_enemy_collapse_signal_B": runtime_signal_metrics["B"]["mean_enemy_collapse_signal"],
        "p95_enemy_collapse_signal_A": runtime_signal_metrics["A"]["p95_enemy_collapse_signal"],
        "p95_enemy_collapse_signal_B": runtime_signal_metrics["B"]["p95_enemy_collapse_signal"],
        "ar_forward_p90_A": source_doe.quantile_or_nan(ar_a, 0.90),
        "wedge_ratio_p10_A": source_doe.quantile_or_nan(wedge_a, 0.10),
        "split_separation_p90_A": source_doe.quantile_or_nan(split_a, 0.90),
        "missing_cut": cut_tick is None,
        "pocket_without_cut": pocket_tick is not None and cut_tick is None,
        "event_order_anomaly": (
            (first_contact_tick is not None and cut_tick is not None and cut_tick < first_contact_tick)
            or (cut_tick is not None and pocket_tick is not None and pocket_tick < cut_tick)
        ),
        "A_v2_mean": side_metrics["A"]["v2_mean"],
        "A_fragmentation_mean": side_metrics["A"]["fragmentation_mean"],
        "A_dispersion_mean": side_metrics["A"]["dispersion_mean"],
        "A_elongation_mean": side_metrics["A"]["elongation_mean"],
        "A_v3_mean": side_metrics["A"]["v3_mean"],
        "A_c_conn_mean": side_metrics["A"]["c_conn_mean"],
        "A_c_scale_mean": side_metrics["A"]["c_scale_mean"],
        "A_rho_mean": side_metrics["A"]["rho_mean"],
        "B_v2_mean": side_metrics["B"]["v2_mean"],
        "B_fragmentation_mean": side_metrics["B"]["fragmentation_mean"],
        "B_dispersion_mean": side_metrics["B"]["dispersion_mean"],
        "B_elongation_mean": side_metrics["B"]["elongation_mean"],
        "B_v3_mean": side_metrics["B"]["v3_mean"],
        "B_c_conn_mean": side_metrics["B"]["c_conn_mean"],
        "B_c_scale_mean": side_metrics["B"]["c_scale_mean"],
        "B_rho_mean": side_metrics["B"]["rho_mean"],
        "determinism_digest": source_doe.state_digest(final_state),
    }


def aggregate_cell_summary(run_rows: list[dict]) -> list[dict]:
    grouped = defaultdict(list)
    for row in run_rows:
        key = (
            row["runtime_decision_source_effective"],
            float(row["semantic_connectivity_multiplier"]),
            int(row["cell_FR"]),
            int(row["cell_MB"]),
            int(row["cell_PD"]),
        )
        grouped[key].append(row)
    out = []
    for key in sorted(grouped.keys()):
        source, mult, fr, mb, pd = key
        rows = grouped[key]
        out.append(
            {
                "runtime_decision_source_effective": source,
                "semantic_connectivity_multiplier": mult,
                "cell_FR": fr,
                "cell_MB": mb,
                "cell_PD": pd,
                "runs": len(rows),
                "first_contact_tick_mean": comp_diag.mean_or_nan([r["first_contact_tick"] for r in rows]),
                "cut_tick_mean": comp_diag.mean_or_nan([r["cut_tick"] for r in rows]),
                "pocket_tick_mean": comp_diag.mean_or_nan([r["pocket_tick"] for r in rows]),
                "first_deep_pursuit_tick_A_mean": comp_diag.mean_or_nan([r["first_deep_pursuit_tick_A"] for r in rows]),
                "pct_ticks_deep_pursuit_A_mean": comp_diag.mean_or_nan([r["pct_ticks_deep_pursuit_A"] for r in rows]),
                "mean_enemy_collapse_signal_A_mean": comp_diag.mean_or_nan([r["mean_enemy_collapse_signal_A"] for r in rows]),
                "A_v2_mean_mean": comp_diag.mean_or_nan([r["A_v2_mean"] for r in rows]),
                "A_fragmentation_mean_mean": comp_diag.mean_or_nan([r["A_fragmentation_mean"] for r in rows]),
                "A_v3_mean_mean": comp_diag.mean_or_nan([r["A_v3_mean"] for r in rows]),
                "A_c_conn_mean_mean": comp_diag.mean_or_nan([r["A_c_conn_mean"] for r in rows]),
                "anomaly_count": sum(1 for r in rows if r["event_order_anomaly"]),
            }
        )
    return out


def build_delta_rows(run_rows: list[dict]) -> list[dict]:
    grouped = defaultdict(dict)
    for row in run_rows:
        key = (
            row["runtime_decision_source_effective"],
            int(row["cell_FR"]),
            int(row["cell_MB"]),
            int(row["cell_PD"]),
            row["opponent_archetype_name"],
        )
        grouped[key][float(row["semantic_connectivity_multiplier"])] = row
    out = []
    for key, level_map in grouped.items():
        source, fr, mb, pd, opponent = key
        base = level_map.get(1.0)
        if base is None:
            continue
        for mult in sorted(level_map.keys()):
            if mult == 1.0:
                continue
            row = level_map[mult]
            out.append(
                {
                    "runtime_decision_source_effective": source,
                    "cell_FR": fr,
                    "cell_MB": mb,
                    "cell_PD": pd,
                    "opponent_archetype_name": opponent,
                    "multiplier_level": mult,
                    "delta_first_contact_tick": (float(row["first_contact_tick"]) - float(base["first_contact_tick"])) if row["first_contact_tick"] is not None and base["first_contact_tick"] is not None else float("nan"),
                    "delta_cut_tick": (float(row["cut_tick"]) - float(base["cut_tick"])) if row["cut_tick"] is not None and base["cut_tick"] is not None else float("nan"),
                    "delta_pocket_tick": (float(row["pocket_tick"]) - float(base["pocket_tick"])) if row["pocket_tick"] is not None and base["pocket_tick"] is not None else float("nan"),
                    "delta_first_deep_pursuit_tick_A": (float(row["first_deep_pursuit_tick_A"]) - float(base["first_deep_pursuit_tick_A"])) if row["first_deep_pursuit_tick_A"] is not None and base["first_deep_pursuit_tick_A"] is not None else float("nan"),
                    "delta_pct_ticks_deep_pursuit_A": float(row["pct_ticks_deep_pursuit_A"]) - float(base["pct_ticks_deep_pursuit_A"]),
                    "delta_mean_enemy_collapse_signal_A": float(row["mean_enemy_collapse_signal_A"]) - float(base["mean_enemy_collapse_signal_A"]),
                    "delta_A_v2_mean": float(row["A_v2_mean"]) - float(base["A_v2_mean"]),
                    "delta_A_fragmentation_mean": float(row["A_fragmentation_mean"]) - float(base["A_fragmentation_mean"]),
                    "delta_A_v3_mean": float(row["A_v3_mean"]) - float(base["A_v3_mean"]),
                    "delta_A_c_conn_mean": float(row["A_c_conn_mean"]) - float(base["A_c_conn_mean"]),
                }
            )
    return out


def build_report(run_rows: list[dict], delta_rows: list[dict], opponent_name: str) -> str:
    by_source = defaultdict(list)
    for row in run_rows:
        by_source[row["runtime_decision_source_effective"]].append(row)
    lines = [
        "# Cohesion-Collapse Semantics Review Micro-Batch",
        "",
        "## Scope",
        "",
        "- Prototype type: semantics-only connectivity-radius decoupling",
        "- Movement baseline frozen: `v3a`",
        f"- Opponent: `{opponent_name}`",
        f"- Seed profile: `{SEED_PROFILE['seed_profile_id']}`",
        f"- Runs: `{len(run_rows)}`",
        "",
        "## Design",
        "",
        "- Cells: `FR x MB = 3 x 3`, `PD = 5`",
        "- Sources: `v2`, `v3_test`",
        "- Multiplier levels:",
        "  - `v2`: `1.0`, `1.5`, `2.0`, `2.5`, `3.0`",
        "  - `v3_test`: `1.0`, `1.1`, `1.2`, `1.3`, `1.4`, `1.5`",
        "- Isolation rule:",
        "  - when source=`v2`, only `v2_connect_radius_multiplier` varies",
        "  - when source=`v3_test`, only `v3_connect_radius_multiplier` varies",
        "",
    ]
    for source in SOURCES:
        subset = by_source[source]
        lines.extend(
            [
                f"## {source}",
                "",
                f"- `first_contact_tick` mean: `{comp_diag.mean_or_nan([r['first_contact_tick'] for r in subset]):.4f}`",
                f"- `first_deep_pursuit_tick_A` mean: `{comp_diag.mean_or_nan([r['first_deep_pursuit_tick_A'] for r in subset]):.4f}`",
                f"- `%ticks_deep_pursuit_A` mean: `{comp_diag.mean_or_nan([r['pct_ticks_deep_pursuit_A'] for r in subset]):.4f}`",
                f"- `mean_enemy_collapse_signal_A` mean: `{comp_diag.mean_or_nan([r['mean_enemy_collapse_signal_A'] for r in subset]):.4f}`",
                f"- `A_v2_mean` mean: `{comp_diag.mean_or_nan([r['A_v2_mean'] for r in subset]):.4f}`",
                f"- `A_fragmentation_mean` mean: `{comp_diag.mean_or_nan([r['A_fragmentation_mean'] for r in subset]):.4f}`",
                f"- `A_v3_mean` mean: `{comp_diag.mean_or_nan([r['A_v3_mean'] for r in subset]):.4f}`",
                f"- `A_c_conn_mean` mean: `{comp_diag.mean_or_nan([r['A_c_conn_mean'] for r in subset]):.4f}`",
                f"- `event_order_anomaly` count: `{sum(1 for r in subset if r['event_order_anomaly'])}`",
                "",
            ]
        )
    lines.extend(
        [
            "## Multiplier Semantics",
            "",
            "- `v2_connect_radius_multiplier` rescales only the LCC/fragmentation graph radius used by `cohesion_v2`.",
            "- It does not modify physical spacing, soft separation force, hard projection, or the other `v2` penalties (`dispersion`, `elongation`, `outlier_mass`).",
            "- Therefore for `v2`, this multiplier is a pure `fragmentation semantics` knob.",
            "- `v3_connect_radius_multiplier` rescales only the connectivity graph radius used by `c_conn` inside `cohesion_v3_shadow`.",
            "- In this batch, `v3_r_ref_radius_multiplier` remains `1.0`, so the `rho / c_scale` scale semantics are intentionally frozen.",
            "- Therefore for `v3_test`, this multiplier is a pure `c_conn semantics` knob rather than a full `v3` rescaling knob.",
            "",
            "## Mean Deltas vs Multiplier 1.0",
            "",
            f"- `v2` mean delta `%ticks_deep_pursuit_A`: `{comp_diag.mean_or_nan([r['delta_pct_ticks_deep_pursuit_A'] for r in delta_rows if r['runtime_decision_source_effective']=='v2']):.4f}`",
            f"- `v2` mean delta `mean_enemy_collapse_signal_A`: `{comp_diag.mean_or_nan([r['delta_mean_enemy_collapse_signal_A'] for r in delta_rows if r['runtime_decision_source_effective']=='v2']):.4f}`",
            f"- `v2` mean delta `A_fragmentation_mean`: `{comp_diag.mean_or_nan([r['delta_A_fragmentation_mean'] for r in delta_rows if r['runtime_decision_source_effective']=='v2']):.4f}`",
            f"- `v3_test` mean delta `%ticks_deep_pursuit_A`: `{comp_diag.mean_or_nan([r['delta_pct_ticks_deep_pursuit_A'] for r in delta_rows if r['runtime_decision_source_effective']=='v3_test']):.4f}`",
            f"- `v3_test` mean delta `mean_enemy_collapse_signal_A`: `{comp_diag.mean_or_nan([r['delta_mean_enemy_collapse_signal_A'] for r in delta_rows if r['runtime_decision_source_effective']=='v3_test']):.4f}`",
            f"- `v3_test` mean delta `A_c_conn_mean`: `{comp_diag.mean_or_nan([r['delta_A_c_conn_mean'] for r in delta_rows if r['runtime_decision_source_effective']=='v3_test']):.4f}`",
            "",
            "## Engineering Read",
            "",
            "- `v2` confirms the semantics-review hypothesis only partially: widening the graph radius removes `fragmentation`, but it does not move `first_deep_pursuit_tick_A` off `t=1`.",
            "- Therefore `v2_connect_radius_multiplier` behaves like a value-calibration knob, not a robust gate-timing knob, in this domain.",
            "- `v3_test` is much more sensitive: `1.1` already lifts `c_conn`, reduces `%ticks_deep_pursuit_A`, and pushes `first_deep_pursuit_tick_A` far away from `t=1`.",
            "- Therefore `v3_connect_radius_multiplier` is the more promising substrate for continued semantics optimization, but `1.5` is already close to over-correction.",
            "- The likely candidate band for follow-up is `v3_test` around `1.1` to `1.2`, not further fine-tuning of `v2`.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    settings = load_json_file(ROOT / "test_run" / "test_run_v1_0.settings.json")
    archetypes = load_json_file(ROOT / "archetypes" / "archetypes_v1_5.json")
    opponent_name = select_first_canonical_opponent(archetypes)

    base_settings = copy.deepcopy(settings)
    run_control = base_settings.setdefault("run_control", {})
    run_control["random_seed"] = int(SEED_PROFILE["random_seed_effective"])
    run_control["metatype_random_seed"] = int(SEED_PROFILE["metatype_random_seed_effective"])
    battlefield = base_settings.setdefault("battlefield", {})
    battlefield["background_map_seed"] = int(SEED_PROFILE["background_map_seed_effective"])
    runtime = base_settings.setdefault("runtime", {})
    selectors = runtime.setdefault("selectors", {})
    selectors["movement_model"] = "baseline"
    boundary = runtime.setdefault("boundary", {})
    boundary["enabled"] = False
    boundary["soft_strength"] = 1.0
    boundary["hard_enabled"] = False

    run_rows = []
    for fr in FR_LEVELS:
        for mb in MB_LEVELS:
            for source in SOURCES:
                for multiplier in SEMANTIC_CONNECTIVITY_LEVELS[source]:
                    run_rows.append(
                        run_single_case(
                            settings=copy.deepcopy(base_settings),
                            archetypes=archetypes,
                            opponent_name=opponent_name,
                            fr=fr,
                            mb=mb,
                            pd=PD_FIXED,
                            source=source,
                            semantic_multiplier=multiplier,
                        )
                    )

    run_rows.sort(key=lambda r: (r["runtime_decision_source_effective"], float(r["semantic_connectivity_multiplier"]), int(r["cell_FR"]), int(r["cell_MB"])))
    delta_rows = build_delta_rows(run_rows)
    delta_rows.sort(key=lambda r: (r["runtime_decision_source_effective"], float(r["multiplier_level"]), int(r["cell_FR"]), int(r["cell_MB"])))
    cell_summary_rows = aggregate_cell_summary(run_rows)
    cell_summary_rows.sort(key=lambda r: (r["runtime_decision_source_effective"], float(r["semantic_connectivity_multiplier"]), int(r["cell_FR"]), int(r["cell_MB"])))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_csv(OUT_DIR / "cohesion_collapse_semantics_microbatch_run_table.csv", run_rows)
    write_csv(OUT_DIR / "cohesion_collapse_semantics_microbatch_delta_table.csv", delta_rows)
    write_csv(OUT_DIR / "cohesion_collapse_semantics_microbatch_cell_summary.csv", cell_summary_rows)
    (OUT_DIR / "cohesion_collapse_semantics_microbatch_report.md").write_text(
        build_report(run_rows, delta_rows, opponent_name),
        encoding="utf-8",
    )

    print(f"Completed semantics micro-batch runs: {len(run_rows)}")
    print(f"Opponent: {opponent_name}")
    print(f"Outputs: {OUT_DIR}")


if __name__ == "__main__":
    main()
