import random
from collections.abc import Sequence
from functools import partial
from pathlib import Path

from runtime.runtime_v0_1 import (
    BattleState,
    FleetState,
    PersonalityParameters,
    UnitState,
    Vec2,
    build_initial_cohesion_map,
)

from test_run import settings_accessor as settings_api


DEFAULT_DT = 1.0
DEFAULT_SPAWN_MARGIN_RATIO = 0.05
ACTIVE_POST_ELIMINATION_EXTRA_TICKS = 10


def clamp(v: float, lo: float, hi: float) -> float:
    if v < lo:
        return lo
    if v > hi:
        return hi
    return v


def _direction_from_angle_deg(angle_deg: float) -> tuple[float, float]:
    import math

    theta = math.radians(float(angle_deg))
    return (math.cos(theta), math.sin(theta))


def _resolve_initial_formation_layout(unit_count: int, aspect_ratio: float) -> list[int]:
    grid_columns = max(1, int((unit_count * aspect_ratio) ** 0.5))
    grid_rows = (unit_count + grid_columns - 1) // grid_columns
    while grid_columns / max(1, grid_rows) < aspect_ratio and grid_columns < unit_count:
        grid_columns += 1
        grid_rows = (unit_count + grid_columns - 1) // grid_columns
    row_counts = []
    remaining = int(unit_count)
    for _ in range(grid_rows):
        row_count = min(grid_columns, remaining)
        row_counts.append(int(row_count))
        remaining -= row_count
    return row_counts


def _require_choice(name: str, raw_value, allowed: set[str]) -> str:
    value = str(raw_value).strip().lower()
    if value not in allowed:
        allowed_text = ", ".join(sorted(allowed))
        raise ValueError(f"{name} must be one of {{{allowed_text}}}, got {raw_value!r}")
    return value


def _resolve_point_setting(
    settings: dict,
    *,
    array_key: str,
    x_key: str,
    y_key: str,
    default_x: float,
    default_y: float,
) -> tuple[float, float]:
    raw = settings_api.get_fleet_setting(settings, array_key, None)
    if isinstance(raw, Sequence) and not isinstance(raw, (str, bytes)) and len(raw) >= 2:
        return float(raw[0]), float(raw[1])
    return (
        float(settings_api.get_fleet_setting(settings, x_key, default_x)),
        float(settings_api.get_fleet_setting(settings, y_key, default_y)),
    )


def resolve_effective_seed(seed_value: int) -> int:
    if seed_value < 0:
        return random.SystemRandom().randrange(0, 2**32)
    return seed_value


def build_initial_state(
    fleet_a_params: PersonalityParameters,
    fleet_b_params: PersonalityParameters,
    fleet_a_size: int,
    fleet_b_size: int,
    fleet_a_aspect_ratio: float,
    fleet_b_aspect_ratio: float,
    unit_spacing: float,
    unit_speed: float,
    unit_max_hit_points: float,
    arena_size: float,
    fleet_a_origin_x: float | None = None,
    fleet_a_origin_y: float | None = None,
    fleet_b_origin_x: float | None = None,
    fleet_b_origin_y: float | None = None,
    fleet_a_facing_angle_deg: float | None = None,
    fleet_b_facing_angle_deg: float | None = None,
) -> BattleState:
    fleet_a_size_effective = int(fleet_a_size)
    fleet_b_size_effective = int(fleet_b_size)
    if fleet_a_size_effective < 1:
        raise ValueError(f"fleet_a_size must be >= 1, got {fleet_a_size_effective}")
    if fleet_b_size_effective < 1:
        raise ValueError(f"fleet_b_size must be >= 1, got {fleet_b_size_effective}")
    fleet_a_aspect_ratio_effective = float(fleet_a_aspect_ratio)
    fleet_b_aspect_ratio_effective = float(fleet_b_aspect_ratio)
    if fleet_a_aspect_ratio_effective <= 0.0:
        raise ValueError(f"fleet_a_aspect_ratio must be > 0, got {fleet_a_aspect_ratio_effective}")
    if fleet_b_aspect_ratio_effective <= 0.0:
        raise ValueError(f"fleet_b_aspect_ratio must be > 0, got {fleet_b_aspect_ratio_effective}")

    spawn_margin = max(1.0, arena_size * DEFAULT_SPAWN_MARGIN_RATIO)
    fleet_a_origin_x_effective = spawn_margin if fleet_a_origin_x is None else float(fleet_a_origin_x)
    fleet_a_origin_y_effective = spawn_margin if fleet_a_origin_y is None else float(fleet_a_origin_y)
    fleet_b_origin_x_effective = (arena_size - spawn_margin) if fleet_b_origin_x is None else float(fleet_b_origin_x)
    fleet_b_origin_y_effective = (arena_size - spawn_margin) if fleet_b_origin_y is None else float(fleet_b_origin_y)
    fleet_a_facing_angle_deg_effective = 45.0 if fleet_a_facing_angle_deg is None else float(fleet_a_facing_angle_deg)
    fleet_b_facing_angle_deg_effective = 225.0 if fleet_b_facing_angle_deg is None else float(fleet_b_facing_angle_deg)

    dir_a = _direction_from_angle_deg(fleet_a_facing_angle_deg_effective)
    dir_b = _direction_from_angle_deg(fleet_b_facing_angle_deg_effective)
    perp_a = (-dir_a[1], dir_a[0])
    perp_b = (-dir_b[1], dir_b[0])
    units = {}

    def _spawn_side(
        *,
        fleet_id: str,
        unit_count: int,
        aspect_ratio_local: float,
        origin_x: float,
        origin_y: float,
        dir_xy: tuple[float, float],
        perp_xy: tuple[float, float],
    ) -> list[str]:
        unit_ids = []
        row_counts = _resolve_initial_formation_layout(unit_count, aspect_ratio_local)
        half_depth = (len(row_counts) - 1) / 2.0
        unit_index = 0
        for row, row_count in enumerate(row_counts):
            row_offset = row - half_depth
            half_width = (row_count - 1) / 2.0
            for col in range(row_count):
                lateral = col - half_width
                unit_id = f"{fleet_id}{unit_index + 1}"
                px = origin_x + (dir_xy[0] * row_offset * unit_spacing) + (perp_xy[0] * lateral * unit_spacing)
                py = origin_y + (dir_xy[1] * row_offset * unit_spacing) + (perp_xy[1] * lateral * unit_spacing)
                units[unit_id] = UnitState(
                    unit_id=unit_id,
                    fleet_id=fleet_id,
                    position=Vec2(x=clamp(px, 0.0, arena_size), y=clamp(py, 0.0, arena_size)),
                    velocity=Vec2(x=0.0, y=0.0),
                    hit_points=unit_max_hit_points,
                    max_hit_points=unit_max_hit_points,
                    max_speed=unit_speed,
                    orientation_vector=Vec2(x=dir_xy[0], y=dir_xy[1]),
                )
                unit_ids.append(unit_id)
                unit_index += 1
        return unit_ids

    fleet_a_unit_ids = _spawn_side(
        fleet_id="A",
        unit_count=fleet_a_size_effective,
        aspect_ratio_local=fleet_a_aspect_ratio_effective,
        origin_x=fleet_a_origin_x_effective,
        origin_y=fleet_a_origin_y_effective,
        dir_xy=dir_a,
        perp_xy=perp_a,
    )
    fleet_b_unit_ids = _spawn_side(
        fleet_id="B",
        unit_count=fleet_b_size_effective,
        aspect_ratio_local=fleet_b_aspect_ratio_effective,
        origin_x=fleet_b_origin_x_effective,
        origin_y=fleet_b_origin_y_effective,
        dir_xy=dir_b,
        perp_xy=perp_b,
    )

    fleets = {
        "A": FleetState(fleet_id="A", parameters=fleet_a_params, unit_ids=tuple(fleet_a_unit_ids)),
        "B": FleetState(fleet_id="B", parameters=fleet_b_params, unit_ids=tuple(fleet_b_unit_ids)),
    }
    return BattleState(
        tick=0,
        dt=DEFAULT_DT,
        arena_size=arena_size,
        units=units,
        fleets=fleets,
        last_fleet_cohesion=build_initial_cohesion_map(fleets.keys()),
    )


def prepare_active_scenario(base_dir: Path, *, settings_override: dict | None = None) -> dict:
    from test_run import test_run_v1_0 as core

    settings = (
        settings_override
        if settings_override is not None
        else settings_api.load_layered_test_run_settings(base_dir)
    )
    get_battlefield = partial(settings_api.get_battlefield_setting, settings)
    get_collapse_shadow = partial(settings_api.get_collapse_shadow_setting, settings)
    get_contact_model = partial(settings_api.get_contact_model_test_setting, settings)
    get_event_bridge = partial(settings_api.get_event_bridge_setting, settings)
    get_fleet = partial(settings_api.get_fleet_setting, settings)
    get_run = partial(settings_api.get_run_control_setting, settings)
    get_runtime = partial(settings_api.get_runtime_setting, settings)
    get_runtime_metatype = partial(settings_api.get_runtime_metatype_setting, settings)
    get_unit = partial(settings_api.get_unit_setting, settings)

    archetypes = settings_api.load_json_file(core.PROJECT_ROOT / "archetypes" / "archetypes_v1_5.json")
    metatype_settings = core.load_metatype_settings(base_dir, settings)
    random_seed = int(get_run("random_seed", -1))
    metatype_random_seed = int(get_runtime_metatype("random_seed", random_seed))
    background_map_seed = int(get_battlefield("background_map_seed", -1))
    effective_random_seed = resolve_effective_seed(random_seed)
    effective_metatype_random_seed = resolve_effective_seed(metatype_random_seed)
    effective_background_map_seed = resolve_effective_seed(background_map_seed)

    archetype_rng = random.Random(int(effective_metatype_random_seed))
    fleet_a_data = core.resolve_fleet_archetype_data(
        archetypes,
        metatype_settings,
        get_fleet("fleet_a_archetype_id", "default"),
        rng=archetype_rng,
    )
    fleet_b_data = core.resolve_fleet_archetype_data(
        archetypes,
        metatype_settings,
        get_fleet("fleet_b_archetype_id", "default"),
        rng=archetype_rng,
    )
    fleet_a_params = core.to_personality_parameters(fleet_a_data)
    fleet_b_params = core.to_personality_parameters(fleet_b_data)

    battlefield_cfg = {
        "arena_size": float(get_battlefield("arena_size", 200.0)),
        "effective_background_map_seed": effective_background_map_seed,
    }
    spawn_margin = max(1.0, battlefield_cfg["arena_size"] * core.DEFAULT_SPAWN_MARGIN_RATIO)
    fleet_a_origin_x, fleet_a_origin_y = _resolve_point_setting(
        settings,
        array_key="initial_fleet_a_origin_xy",
        x_key="initial_fleet_a_origin_x",
        y_key="initial_fleet_a_origin_y",
        default_x=spawn_margin,
        default_y=spawn_margin,
    )
    fleet_b_origin_x, fleet_b_origin_y = _resolve_point_setting(
        settings,
        array_key="initial_fleet_b_origin_xy",
        x_key="initial_fleet_b_origin_x",
        y_key="initial_fleet_b_origin_y",
        default_x=battlefield_cfg["arena_size"] - spawn_margin,
        default_y=battlefield_cfg["arena_size"] - spawn_margin,
    )
    fleet_cfg = {
        "sizes": {
            "A": int(get_fleet("initial_fleet_a_size", 100)),
            "B": int(get_fleet("initial_fleet_b_size", 100)),
        },
        "aspect_ratios": {
            "A": float(get_fleet("initial_fleet_a_aspect_ratio", 2.0)),
            "B": float(get_fleet("initial_fleet_b_aspect_ratio", 2.0)),
        },
        "origins": {
            "A": (fleet_a_origin_x, fleet_a_origin_y),
            "B": (fleet_b_origin_x, fleet_b_origin_y),
        },
        "facing_angles_deg": {
            "A": float(get_fleet("initial_fleet_a_facing_angle_deg", 45.0)),
            "B": float(get_fleet("initial_fleet_b_facing_angle_deg", 225.0)),
        },
        "unit_spacing": float(get_runtime("min_unit_spacing", 1.0)),
    }
    if min(fleet_cfg["sizes"].values()) < 1:
        raise ValueError(f"initial fleet sizes must be >= 1, got {fleet_cfg['sizes']}")
    if min(fleet_cfg["aspect_ratios"].values()) <= 0.0 or fleet_cfg["unit_spacing"] <= 0.0:
        raise ValueError(
            "initial geometry aspect ratios and min_unit_spacing must be > 0, "
            f"got {fleet_cfg['aspect_ratios']}, spacing={fleet_cfg['unit_spacing']}"
        )

    unit_cfg = {
        "speed": float(get_unit("unit_speed", 1.0)),
        "max_hit_points": float(get_unit("unit_max_hit_points", 100.0)),
        "attack_range": float(get_unit("attack_range", get_runtime("attack_range", 3.0))),
        "damage_per_tick": float(get_unit("damage_per_tick", get_runtime("damage_per_tick", 1.0))),
    }
    initial_state = build_initial_state(
        fleet_a_params=fleet_a_params,
        fleet_b_params=fleet_b_params,
        fleet_a_size=fleet_cfg["sizes"]["A"],
        fleet_b_size=fleet_cfg["sizes"]["B"],
        fleet_a_aspect_ratio=fleet_cfg["aspect_ratios"]["A"],
        fleet_b_aspect_ratio=fleet_cfg["aspect_ratios"]["B"],
        unit_spacing=fleet_cfg["unit_spacing"],
        unit_speed=unit_cfg["speed"],
        unit_max_hit_points=unit_cfg["max_hit_points"],
        arena_size=battlefield_cfg["arena_size"],
        fleet_a_origin_x=fleet_cfg["origins"]["A"][0],
        fleet_a_origin_y=fleet_cfg["origins"]["A"][1],
        fleet_b_origin_x=fleet_cfg["origins"]["B"][0],
        fleet_b_origin_y=fleet_cfg["origins"]["B"][1],
        fleet_a_facing_angle_deg=fleet_cfg["facing_angles_deg"]["A"],
        fleet_b_facing_angle_deg=fleet_cfg["facing_angles_deg"]["B"],
    )

    contact_cfg = {
        "attack_range": unit_cfg["attack_range"],
        "damage_per_tick": unit_cfg["damage_per_tick"],
        "fire_quality_alpha": float(get_runtime("fire_quality_alpha", 0.1)),
        "contact_hysteresis_h": float(get_runtime("contact_hysteresis_h", 0.1)),
        "fsr_strength": float(get_runtime("fsr_strength", 0.0)),
        "alpha_sep": float(get_runtime("alpha_sep", 0.6)),
        "hostile_contact_impedance_mode": _require_choice(
            "runtime.test_only.hostile_contact_impedance.active_mode",
            get_contact_model(("active_mode",), core.HOSTILE_CONTACT_IMPEDANCE_MODE_DEFAULT),
            core.HOSTILE_CONTACT_IMPEDANCE_MODE_LABELS,
        ),
        "hybrid_v2": {
            key: float(get_contact_model(("hybrid_v2", key), default))
            for key, default in {
                "radius_multiplier": core.HOSTILE_CONTACT_IMPEDANCE_V2_RADIUS_MULTIPLIER_DEFAULT,
                "repulsion_max_disp_ratio": core.HOSTILE_CONTACT_IMPEDANCE_V2_REPULSION_MAX_DISP_RATIO_DEFAULT,
                "forward_damping_strength": core.HOSTILE_CONTACT_IMPEDANCE_V2_FORWARD_DAMPING_STRENGTH_DEFAULT,
            }.items()
        },
        "intent_unified_spacing_v1": {
            key: float(get_contact_model(("intent_unified_spacing_v1", key), default))
            for key, default in {
                "scale": core.HOSTILE_INTENT_UNIFIED_SPACING_SCALE_DEFAULT,
                "strength": core.HOSTILE_INTENT_UNIFIED_SPACING_STRENGTH_DEFAULT,
            }.items()
        },
    }
    contact_cfg["ch_enabled"] = contact_cfg["contact_hysteresis_h"] > 0.0
    contact_cfg["fsr_enabled"] = contact_cfg["fsr_strength"] > 0.0

    movement_cfg = {
        "model_effective": core.resolve_movement_model(get_runtime("movement_model", "baseline"))[1],
        "experiment_effective": _require_choice(
            "runtime.movement_v3a_experiment",
            get_runtime("movement_v3a_experiment", core.V3A_EXPERIMENT_BASE),
            core.V3A_EXPERIMENT_LABELS,
        ),
        "centroid_probe_scale": float(get_runtime("centroid_probe_scale", 1.0)),
        "pre_tl_target_substrate": _require_choice(
            "runtime.pre_tl_target_substrate",
            get_runtime("pre_tl_target_substrate", core.PRE_TL_TARGET_SUBSTRATE_DEFAULT),
            core.PRE_TL_TARGET_SUBSTRATE_LABELS,
        ),
        "symmetric_movement_sync_enabled": bool(get_runtime("symmetric_movement_sync_enabled", True)),
        "continuous_fr_shaping": {
            "enabled": bool(get_runtime("continuous_fr_shaping_enabled", False)),
            "mode": _require_choice(
                "runtime.continuous_fr_shaping_mode",
                get_runtime("continuous_fr_shaping_mode", core.CONTINUOUS_FR_SHAPING_OFF),
                core.CONTINUOUS_FR_SHAPING_LABELS,
            ),
            **{
                key: float(get_runtime(f"continuous_fr_shaping_{key}", default))
                for key, default in {
                    "a": 0.0,
                    "sigma": 0.15,
                    "p": 1.0,
                    "q": 1.0,
                    "beta": 0.0,
                    "gamma": 0.0,
                }.items()
            },
        },
        "odw_posture_bias": {
            "enabled": bool(get_runtime("odw_posture_bias_enabled", False)),
            "k": float(get_runtime("odw_posture_bias_k", 0.3)),
            "clip_delta": float(get_runtime("odw_posture_bias_clip_delta", 0.2)),
        },
    }
    movement_cfg["centroid_probe_scale_effective"] = (
        movement_cfg["centroid_probe_scale"]
        if movement_cfg["model_effective"] == "v3a"
        and movement_cfg["experiment_effective"] == core.V3A_EXPERIMENT_PRECONTACT_CENTROID_PROBE
        else 1.0
    )
    movement_cfg["continuous_fr_shaping"]["effective"] = (
        movement_cfg["model_effective"] == "v3a"
        and movement_cfg["experiment_effective"] == core.V3A_EXPERIMENT_PRECONTACT_CENTROID_PROBE
        and movement_cfg["continuous_fr_shaping"]["enabled"]
        and movement_cfg["continuous_fr_shaping"]["mode"] != core.CONTINUOUS_FR_SHAPING_OFF
        and movement_cfg["continuous_fr_shaping"]["a"] > 0.0
    )
    movement_cfg["continuous_fr_shaping"]["mode_effective"] = (
        movement_cfg["continuous_fr_shaping"]["mode"]
        if movement_cfg["continuous_fr_shaping"]["effective"]
        else core.CONTINUOUS_FR_SHAPING_OFF
    )
    movement_cfg["odw_posture_bias"]["enabled_effective"] = (
        movement_cfg["model_effective"] == "v3a"
        and movement_cfg["odw_posture_bias"]["enabled"]
    )
    movement_cfg["odw_posture_bias"]["k_effective"] = (
        movement_cfg["odw_posture_bias"]["k"]
        if movement_cfg["odw_posture_bias"]["enabled_effective"]
        else 0.0
    )
    movement_cfg["odw_posture_bias"]["clip_delta_effective"] = (
        movement_cfg["odw_posture_bias"]["clip_delta"]
        if movement_cfg["odw_posture_bias"]["enabled_effective"]
        else 0.2
    )

    observer_cfg = {
        "bridge": {
            "theta_split": float(get_event_bridge("theta_split", core.BRIDGE_THETA_SPLIT_DEFAULT)),
            "theta_env": float(get_event_bridge("theta_env", core.BRIDGE_THETA_ENV_DEFAULT)),
            "sustain_ticks": int(get_event_bridge("sustain_ticks", core.BRIDGE_SUSTAIN_TICKS_DEFAULT)),
        },
        "collapse_shadow": {
            key: cast(get_collapse_shadow(key, default))
            for key, (cast, default) in {
                "theta_conn_default": (float, core.COLLAPSE_V2_SHADOW_THETA_CONN_DEFAULT),
                "theta_coh_default": (float, core.COLLAPSE_V2_SHADOW_THETA_COH_DEFAULT),
                "theta_force_default": (float, core.COLLAPSE_V2_SHADOW_THETA_FORCE_DEFAULT),
                "theta_attr_default": (float, core.COLLAPSE_V2_SHADOW_THETA_ATTR_DEFAULT),
                "attrition_window": (int, core.COLLAPSE_V2_SHADOW_ATTRITION_WINDOW_DEFAULT),
                "sustain_ticks": (int, core.COLLAPSE_V2_SHADOW_SUSTAIN_TICKS_DEFAULT),
                "min_conditions": (int, core.COLLAPSE_V2_SHADOW_MIN_CONDITIONS_DEFAULT),
            }.items()
        },
    }

    boundary_cfg = {
        "enabled": bool(get_runtime("boundary_enabled", False)),
        "hard_enabled": bool(get_runtime("boundary_hard_enabled", True)),
        "soft_strength": float(get_runtime("boundary_soft_strength", 1.0)),
    }

    run_cfg = {
        "max_time_steps": int(get_run("max_time_steps", -1)),
        "test_mode": core.parse_test_mode(get_run("test_mode", 0)),
    }
    run_cfg["test_mode_name"] = core.test_mode_label(run_cfg["test_mode"])
    run_cfg["observer_enabled"] = run_cfg["test_mode"] >= 1
    run_cfg["export_battle_report"] = False
    (
        run_cfg["runtime_decision_source_requested"],
        run_cfg["runtime_decision_source_effective"],
    ) = core.resolve_runtime_decision_source(
        get_runtime("cohesion_decision_source", "baseline"),
        run_cfg["test_mode"],
    )
    movement_cfg["v2_connect_radius_multiplier"] = 1.0
    movement_cfg["v3_connect_radius_multiplier_effective"] = (
        float(get_runtime("v3_connect_radius_multiplier", core.BASELINE_V3_CONNECT_RADIUS_MULTIPLIER))
        if run_cfg["runtime_decision_source_effective"] == "v3_test"
        else 1.0
    )
    movement_cfg["v3_r_ref_radius_multiplier_effective"] = (
        float(get_runtime("v3_r_ref_radius_multiplier", core.BASELINE_V3_R_REF_RADIUS_MULTIPLIER))
        if run_cfg["runtime_decision_source_effective"] == "v3_test"
        else 1.0
    )

    execution_cfg = {
        "steps": run_cfg["max_time_steps"],
        "capture_positions": False,
        "frame_stride": core.DEFAULT_FRAME_STRIDE,
        "include_target_lines": False,
        "print_tick_summary": False,
        "plot_diagnostics_enabled": run_cfg["observer_enabled"],
        "post_elimination_extra_ticks": ACTIVE_POST_ELIMINATION_EXTRA_TICKS,
    }
    simulation_runtime_cfg = {
        "decision_source": run_cfg["runtime_decision_source_effective"],
        "movement_model": movement_cfg["model_effective"],
        "movement": movement_cfg,
        "contact": {
            **contact_cfg,
            "separation_radius": fleet_cfg["unit_spacing"],
        },
        "boundary": boundary_cfg,
    }
    simulation_observer_cfg = {
        "enabled": run_cfg["observer_enabled"],
        "bridge": observer_cfg["bridge"],
        "collapse_shadow": observer_cfg["collapse_shadow"],
        "runtime_diag_enabled": False,
    }

    return {
        "initial_state": initial_state,
        "engine_cls": core.TestModeEngineTickSkeleton,
        "execution_cfg": execution_cfg,
        "runtime_cfg": simulation_runtime_cfg,
        "observer_cfg": simulation_observer_cfg,
        "summary": {
            "effective_random_seed": effective_random_seed,
            "effective_metatype_random_seed": effective_metatype_random_seed,
            "effective_background_map_seed": effective_background_map_seed,
            "test_mode_name": run_cfg["test_mode_name"],
            "runtime_decision_source_effective": run_cfg["runtime_decision_source_effective"],
            "movement_model_effective": movement_cfg["model_effective"],
            "hostile_contact_impedance_mode": contact_cfg["hostile_contact_impedance_mode"],
            "animate": False,
            "observer_enabled": run_cfg["observer_enabled"],
            "export_battle_report": False,
        },
    }
