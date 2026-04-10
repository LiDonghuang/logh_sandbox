import math
import random
import re
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
from test_run import test_run_execution as execution


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DT = 1.0
DEFAULT_SPAWN_MARGIN_RATIO = 0.05
DEFAULT_POST_RESOLUTION_HOLD_STEPS = 10
DEFAULT_PLOT_COLORS = ("#1f77b4", "#ff7f0e")
FORMATION_LAYOUT_MODE_RECT_CENTERED_ROWS = "rect_centered_rows"
REFERENCE_LAYOUT_MODE_RECT_CENTERED_1_0 = "rect_centered_1.0"
REFERENCE_LAYOUT_MODE_RECT_CENTERED_4_0 = "rect_centered_4.0"
REFERENCE_LAYOUT_MODE_LABELS = {
    REFERENCE_LAYOUT_MODE_RECT_CENTERED_1_0,
    REFERENCE_LAYOUT_MODE_RECT_CENTERED_4_0,
}
FORMATION_LAYOUT_MODE_LABELS = {
    FORMATION_LAYOUT_MODE_RECT_CENTERED_ROWS,
    *REFERENCE_LAYOUT_MODE_LABELS,
}
PERSONALITY_PARAM_KEYS = (
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
)
DEFAULT_METATYPE_SETTINGS_PATH = "archetypes/metatype_settings.json"


def load_metatype_settings(base_dir: Path, settings: dict) -> dict:
    configured_path = str(
        settings_api.get_runtime_metatype_setting(settings, "settings_path", DEFAULT_METATYPE_SETTINGS_PATH)
    )
    metatype_path = settings_api.resolve_optional_json_path(
        base_dir,
        configured_path,
        DEFAULT_METATYPE_SETTINGS_PATH,
    )
    if not metatype_path.exists():
        return {}
    data = settings_api.load_json_file(metatype_path)
    if isinstance(data, dict):
        return data
    return {}


def resolve_archetype(archetypes: dict, archetype_ref: str) -> dict:
    if archetype_ref == "default":
        return {
            "name": "default",
            "disp_name_EN": "Default",
            "disp_name_ZH": "榛樿",
            "full_name_EN": "Default Archetype",
            "full_name_ZH": "榛樿鍘熷瀷",
            "force_concentration_ratio": 5.0,
            "mobility_bias": 5.0,
            "offense_defense_weight": 5.0,
            "risk_appetite": 5.0,
            "time_preference": 5.0,
            "targeting_logic": 5.0,
            "formation_rigidity": 5.0,
            "perception_radius": 5.0,
            "pursuit_drive": 5.0,
            "retreat_threshold": 5.0,
        }
    if archetype_ref in archetypes:
        return dict(archetypes[archetype_ref])
    raise KeyError(archetype_ref)


def _personality_value_from_data(data: dict, key: str) -> float:
    if key not in data:
        raise KeyError(key)
    return float(data[key])


def _select_yang_source_ids(archetypes: dict, configured_source_ids: list[str] | None = None) -> list[str]:
    selected_ids = configured_source_ids if configured_source_ids else []
    source_ids = [archetype_id for archetype_id in selected_ids if archetype_id in archetypes]
    if source_ids:
        return source_ids

    fallback_ids = []
    for archetype_id, data in archetypes.items():
        normalized = str(archetype_id).strip().lower()
        if normalized in {"yang", "default"}:
            continue
        try:
            for key in PERSONALITY_PARAM_KEYS:
                _personality_value_from_data(data, key)
        except KeyError:
            continue
        fallback_ids.append(str(archetype_id))
        if len(fallback_ids) >= 6:
            break
    if fallback_ids:
        return fallback_ids
    raise ValueError("No valid source archetypes available for dynamic yang parameter generation.")


def generate_yang_parameters(
    archetypes: dict,
    yang_template: dict,
    rng: random.Random | None = None,
    source_ids: list[str] | None = None,
    jitter: int = 1,
    value_min: float = 1.0,
    value_max: float = 9.0,
) -> dict:
    generator = rng if rng is not None else random.Random(resolve_effective_seed(-1))
    candidate_ids = _select_yang_source_ids(archetypes, configured_source_ids=source_ids)
    source_id = generator.choice(candidate_ids)
    source_data = archetypes[source_id]

    generated = dict(yang_template)
    generated["name"] = str(yang_template.get("name", "yang") or "yang")
    jitter = max(0, int(jitter))
    lo = float(min(value_min, value_max))
    hi = float(max(value_min, value_max))
    for key in PERSONALITY_PARAM_KEYS:
        base_value = _personality_value_from_data(source_data, key)
        jitter_delta = generator.randint(-jitter, jitter) if jitter > 0 else 0
        jittered_value = base_value + float(jitter_delta)
        generated[key] = float(clamp(jittered_value, lo, hi))
    return generated


def resolve_fleet_archetype_data(
    archetypes: dict,
    metatype_settings: dict | None,
    archetype_ref: str,
    rng: random.Random | None = None,
) -> dict:
    ref = str(archetype_ref).strip()
    if ref.lower() != "yang":
        return resolve_archetype(archetypes, ref)

    yang_meta = {}
    if isinstance(metatype_settings, dict):
        candidate_meta = metatype_settings.get("yang", {})
        if isinstance(candidate_meta, dict):
            yang_meta = candidate_meta
    generation_cfg = yang_meta.get("generation", {}) if isinstance(yang_meta.get("generation", {}), dict) else {}
    template_cfg = yang_meta.get("template", {}) if isinstance(yang_meta.get("template", {}), dict) else {}
    archetype_template = {}
    if isinstance(archetypes.get("yang"), dict):
        archetype_template = dict(archetypes["yang"])

    source_ids_raw = generation_cfg.get("source_archetype_ids")
    source_ids = []
    if isinstance(source_ids_raw, list):
        source_ids = [str(v).strip() for v in source_ids_raw if str(v).strip()]

    jitter = int(generation_cfg.get("jitter", 1))
    value_min = float(generation_cfg.get("param_min", 1.0))
    value_max = float(generation_cfg.get("param_max", 9.0))

    yang_template = {
        "name": str(template_cfg.get("name", archetype_template.get("name", "yang"))),
        "disp_name_EN": str(
            template_cfg.get(
                "disp_name_EN",
                archetype_template.get("disp_name_EN", "Yang"),
            )
        ),
        "disp_name_ZH": str(
            template_cfg.get(
                "disp_name_ZH",
                archetype_template.get("disp_name_ZH", "Yang"),
            )
        ),
        "full_name_EN": str(
            template_cfg.get(
                "full_name_EN",
                archetype_template.get("full_name_EN", "Yang Wen-li"),
            )
        ),
        "full_name_ZH": str(
            template_cfg.get(
                "full_name_ZH",
                archetype_template.get("full_name_ZH", "Yang Wen-li"),
            )
        ),
        "avatar": str(
            template_cfg.get("avatar", archetype_template.get("avatar", "avatar_yang"))
        ),
        "color_code": str(
            template_cfg.get(
                "color_code",
                archetype_template.get("color_code", "008080"),
            )
        ),
    }
    return generate_yang_parameters(
        archetypes=archetypes,
        yang_template=yang_template,
        rng=rng,
        source_ids=source_ids,
        jitter=jitter,
        value_min=value_min,
        value_max=value_max,
    )


def to_personality_parameters(data: dict) -> PersonalityParameters:
    return PersonalityParameters(
        archetype_id=data["name"],
        force_concentration_ratio=float(data["force_concentration_ratio"]),
        mobility_bias=float(data["mobility_bias"]),
        offense_defense_weight=float(data["offense_defense_weight"]),
        risk_appetite=float(data["risk_appetite"]),
        time_preference=float(data["time_preference"]),
        targeting_logic=float(data["targeting_logic"]),
        formation_rigidity=float(data["formation_rigidity"]),
        perception_radius=float(data["perception_radius"]),
        pursuit_drive=float(data["pursuit_drive"]),
        retreat_threshold=float(data["retreat_threshold"]),
    )


def to_plot_color(data: dict, fallback: str) -> str:
    code = str(data.get("color_code", "")).strip()
    if not code:
        code = fallback
    if code.startswith("#"):
        return code
    return f"#{code}"


def _hex_color_to_rgb(color: str) -> tuple[int, int, int] | None:
    normalized = str(color).strip()
    if normalized.startswith("#"):
        normalized = normalized[1:]
    if re.fullmatch(r"[0-9A-Fa-f]{6}", normalized) is None:
        return None
    return (
        int(normalized[0:2], 16),
        int(normalized[2:4], 16),
        int(normalized[4:6], 16),
    )


def _color_distance_sq(color_a: str, color_b: str) -> float:
    rgb_a = _hex_color_to_rgb(color_a)
    rgb_b = _hex_color_to_rgb(color_b)
    if rgb_a is None or rgb_b is None:
        return -1.0
    dr = float(rgb_a[0] - rgb_b[0])
    dg = float(rgb_a[1] - rgb_b[1])
    db = float(rgb_a[2] - rgb_b[2])
    return (dr * dr) + (dg * dg) + (db * db)


def choose_max_contrast_default_color(reference_color: str, candidates: Sequence[str]) -> str:
    best_color = str(candidates[0])
    best_distance = _color_distance_sq(reference_color, best_color)
    for candidate in candidates[1:]:
        distance = _color_distance_sq(reference_color, str(candidate))
        if distance > best_distance:
            best_color = str(candidate)
            best_distance = distance
    return best_color


def resolve_fleet_plot_colors(fleet_a_data: dict, fleet_b_data: dict) -> tuple[str, str]:
    fleet_a_has_explicit = bool(str(fleet_a_data.get("color_code", "")).strip())
    fleet_b_has_explicit = bool(str(fleet_b_data.get("color_code", "")).strip())
    fleet_a_color = to_plot_color(fleet_a_data, DEFAULT_PLOT_COLORS[0])
    fleet_b_color = to_plot_color(fleet_b_data, DEFAULT_PLOT_COLORS[1])
    if fleet_a_has_explicit and (not fleet_b_has_explicit):
        fleet_b_color = choose_max_contrast_default_color(fleet_a_color, DEFAULT_PLOT_COLORS)
    elif fleet_b_has_explicit and (not fleet_a_has_explicit):
        fleet_a_color = choose_max_contrast_default_color(fleet_b_color, DEFAULT_PLOT_COLORS)
    return fleet_a_color, fleet_b_color


def resolve_display_name(data: dict, language: str) -> str:
    value = data.get("disp_name_ZH") if language == "ZH" else data.get("disp_name_EN")
    if value:
        return str(value)
    if data.get("name"):
        return str(data["name"])
    return ""


def resolve_avatar_with_fallback(side_data: dict, fallback_avatar: str) -> str:
    value = side_data.get("avatar")
    if value is not None:
        avatar_id = str(value).strip()
        if avatar_id:
            return avatar_id
    return fallback_avatar


def resolve_movement_model(raw_value) -> tuple[str, str]:
    requested = str(raw_value).strip().lower()
    if requested == "v1":
        raise ValueError("runtime.selectors.movement_model=v1 has been retired; use baseline or v4a")
    if requested == "v3a":
        raise ValueError(
            "runtime.selectors.movement_model=v3a has been retired from the maintained test_run mainline; "
            "use baseline or v4a"
        )
    if requested not in {"baseline", "v4a"}:
        allowed_text = ", ".join(sorted({"baseline", "v4a"}))
        raise ValueError(
            f"runtime.selectors.movement_model must be one of {{{allowed_text}}}, got {raw_value!r}"
        )
    baseline_model = "v4a"
    if requested == "baseline":
        effective = baseline_model
    else:
        effective = requested
    return requested, effective


def clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _direction_from_angle_deg(angle_deg: float) -> tuple[float, float]:
    import math

    theta = math.radians(float(angle_deg))
    return (math.cos(theta), math.sin(theta))


def _resolve_initial_formation_layout(unit_count: int, aspect_ratio: float, layout_mode: str) -> list[int]:
    resolved_layout_mode = _require_choice(
        "reference_layout_mode",
        layout_mode,
        FORMATION_LAYOUT_MODE_LABELS,
    )
    if resolved_layout_mode not in FORMATION_LAYOUT_MODE_LABELS:
        raise ValueError(
            f"unsupported reference_layout_mode={resolved_layout_mode!r}"
        )
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


def _load_common_scenario_context(
    base_dir: Path,
    settings: dict,
    *,
    get_battlefield,
    get_run,
    get_runtime_metatype,
) -> dict:
    archetypes = settings_api.load_json_file(PROJECT_ROOT / "archetypes" / "archetypes_v1_5.json")
    metatype_settings = load_metatype_settings(base_dir, settings)
    random_seed = int(get_run("random_seed", -1))
    metatype_random_seed = int(get_runtime_metatype("random_seed", random_seed))
    background_map_seed = int(get_battlefield("background_map_seed", -1))
    effective_random_seed = resolve_effective_seed(random_seed)
    effective_metatype_random_seed = resolve_effective_seed(metatype_random_seed)
    effective_background_map_seed = resolve_effective_seed(background_map_seed)
    return {
        "archetypes": archetypes,
        "metatype_settings": metatype_settings,
        "effective_random_seed": effective_random_seed,
        "effective_metatype_random_seed": effective_metatype_random_seed,
        "effective_background_map_seed": effective_background_map_seed,
        "battlefield_cfg": {
            "arena_size": float(get_battlefield("arena_size", 200.0)),
            "effective_background_map_seed": effective_background_map_seed,
        },
    }


def _build_unit_cfg(get_unit, get_runtime) -> dict:
    return {
        "speed": float(get_unit("unit_speed", 1.0)),
        "max_hit_points": float(get_unit("unit_max_hit_points", 100.0)),
        "attack_range": float(get_unit("attack_range", get_runtime("attack_range", 3.0))),
        "damage_per_tick": float(get_unit("damage_per_tick", get_runtime("damage_per_tick", 1.0))),
    }


def _build_run_cfg(
    get_run,
    *,
    max_time_steps_override: int | None = None,
) -> dict:
    post_resolution_hold_steps = int(get_run("post_resolution_hold_steps", DEFAULT_POST_RESOLUTION_HOLD_STEPS))
    if post_resolution_hold_steps < 0:
        raise ValueError(
            "run_control.post_resolution_hold_steps must be >= 0, "
            f"got {post_resolution_hold_steps}"
        )
    observer_enabled = bool(get_run("observer_enabled", True))
    return {
        "max_time_steps": (
            int(get_run("max_time_steps", -1))
            if max_time_steps_override is None
            else int(max_time_steps_override)
        ),
        "post_resolution_hold_steps": post_resolution_hold_steps,
        "observer_enabled": observer_enabled,
        "export_battle_report": False,
    }


def _build_movement_cfg(get_runtime, get_run) -> dict:
    v4a_restore_strength = float(get_runtime("v4a_restore_strength", 0.25))
    if not 0.0 <= v4a_restore_strength <= 1.0:
        raise ValueError(
            "runtime.movement.v4a.restore.strength must be within [0.0, 1.0], "
            f"got {v4a_restore_strength}"
        )
    v4a_reference_surface_mode = _require_choice(
        "runtime.movement.v4a.reference.surface_mode",
        get_runtime("v4a_reference_surface_mode", execution.V4A_REFERENCE_SURFACE_MODE_RIGID_SLOTS),
        execution.V4A_REFERENCE_SURFACE_MODE_LABELS,
    )
    v4a_soft_morphology_relaxation = float(
        get_runtime("v4a_soft_morphology_relaxation", execution.V4A_SOFT_MORPHOLOGY_RELAXATION_DEFAULT)
    )
    if not 0.0 < v4a_soft_morphology_relaxation <= 1.0:
        raise ValueError(
            "runtime.movement.v4a.reference.soft_morphology_relaxation must be within (0.0, 1.0], "
            f"got {v4a_soft_morphology_relaxation}"
        )
    v4a_shape_vs_advance_strength = float(
        get_runtime("v4a_shape_vs_advance_strength", execution.V4A_SHAPE_VS_ADVANCE_STRENGTH_DEFAULT)
    )
    if not 0.0 <= v4a_shape_vs_advance_strength <= 1.0:
        raise ValueError(
            "runtime.movement.v4a.transition.shape_vs_advance_strength must be within [0.0, 1.0], "
            f"got {v4a_shape_vs_advance_strength}"
        )
    v4a_heading_relaxation = float(
        get_runtime("v4a_heading_relaxation", execution.V4A_HEADING_RELAXATION_DEFAULT)
    )
    if not 0.0 < v4a_heading_relaxation <= 1.0:
        raise ValueError(
            "runtime.movement.v4a.transition.heading_relaxation must be within (0.0, 1.0], "
            f"got {v4a_heading_relaxation}"
        )
    v4a_battle_standoff_hold_band_ratio = float(
        get_runtime(
            "v4a_battle_standoff_hold_band_ratio",
            execution.V4A_BATTLE_STANDOFF_HOLD_BAND_RATIO_DEFAULT,
        )
    )
    if not 0.0 <= v4a_battle_standoff_hold_band_ratio <= 1.0:
        raise ValueError(
            "runtime.movement.v4a.battle.standoff_hold_band_ratio must be within [0.0, 1.0], "
            f"got {v4a_battle_standoff_hold_band_ratio}"
        )
    v4a_battle_target_front_strip_gap_bias = float(
        get_runtime(
            "v4a_battle_target_front_strip_gap_bias",
            execution.V4A_BATTLE_TARGET_FRONT_STRIP_GAP_BIAS_DEFAULT,
        )
    )
    if not math.isfinite(v4a_battle_target_front_strip_gap_bias):
        raise ValueError(
            "runtime.movement.v4a.battle.target_front_strip_gap_bias must be finite, "
            f"got {v4a_battle_target_front_strip_gap_bias}"
        )
    v4a_battle_hold_weight_strength = float(
        get_runtime(
            "v4a_battle_hold_weight_strength",
            execution.V4A_BATTLE_HOLD_WEIGHT_STRENGTH_DEFAULT,
        )
    )
    if not 0.0 <= v4a_battle_hold_weight_strength <= 1.0:
        raise ValueError(
            "runtime.movement.v4a.battle.hold_weight_strength must be within [0.0, 1.0], "
            f"got {v4a_battle_hold_weight_strength}"
        )
    v4a_battle_relation_lead_ticks = float(
        get_runtime(
            "v4a_battle_relation_lead_ticks",
            execution.V4A_BATTLE_RELATION_LEAD_TICKS_DEFAULT,
        )
    )
    if not math.isfinite(v4a_battle_relation_lead_ticks) or v4a_battle_relation_lead_ticks <= 0.0:
        raise ValueError(
            "runtime.movement.v4a.battle.relation_lead_ticks must be finite and > 0, "
            f"got {v4a_battle_relation_lead_ticks}"
        )
    v4a_battle_hold_relaxation = float(
        get_runtime(
            "v4a_battle_hold_relaxation",
            execution.V4A_BATTLE_HOLD_RELAXATION_DEFAULT,
        )
    )
    if not 0.0 < v4a_battle_hold_relaxation <= 1.0:
        raise ValueError(
            "runtime.movement.v4a.battle.hold_relaxation must be within (0.0, 1.0], "
            f"got {v4a_battle_hold_relaxation}"
        )
    v4a_battle_approach_drive_relaxation = float(
        get_runtime(
            "v4a_battle_approach_drive_relaxation",
            execution.V4A_BATTLE_APPROACH_DRIVE_RELAXATION_DEFAULT,
        )
    )
    if not 0.0 < v4a_battle_approach_drive_relaxation <= 1.0:
        raise ValueError(
            "runtime.movement.v4a.battle.approach_drive_relaxation must be within (0.0, 1.0], "
            f"got {v4a_battle_approach_drive_relaxation}"
        )
    v4a_battle_near_contact_internal_stability_blend = float(
        get_runtime(
            "v4a_battle_near_contact_internal_stability_blend",
            execution.V4A_NEAR_CONTACT_INTERNAL_STABILITY_BLEND_DEFAULT,
        )
    )
    if not 0.0 <= v4a_battle_near_contact_internal_stability_blend <= 1.0:
        raise ValueError(
            "runtime.movement.v4a.battle.near_contact_internal_stability_blend must be within [0.0, 1.0], "
            f"got {v4a_battle_near_contact_internal_stability_blend}"
        )
    v4a_battle_near_contact_speed_relaxation = float(
        get_runtime(
            "v4a_battle_near_contact_speed_relaxation",
            execution.V4A_NEAR_CONTACT_SPEED_RELAXATION_DEFAULT,
        )
    )
    if not 0.0 < v4a_battle_near_contact_speed_relaxation <= 1.0:
        raise ValueError(
            "runtime.movement.v4a.battle.near_contact_speed_relaxation must be within (0.0, 1.0], "
            f"got {v4a_battle_near_contact_speed_relaxation}"
        )
    engaged_speed_scale = float(
        get_runtime("engaged_speed_scale", execution.V4A_ENGAGED_SPEED_SCALE_DEFAULT)
    )
    if not 0.0 < engaged_speed_scale <= 1.0:
        raise ValueError(
            "runtime.movement.v4a.engagement.engaged_speed_scale must be within (0.0, 1.0], "
            f"got {engaged_speed_scale}"
        )
    attack_speed_lateral_scale = float(
        get_runtime(
            "attack_speed_lateral_scale",
            execution.V4A_ATTACK_SPEED_LATERAL_SCALE_DEFAULT,
        )
    )
    if not 0.0 < attack_speed_lateral_scale <= 1.0:
        raise ValueError(
            "runtime.movement.v4a.engagement.attack_speed_lateral_scale must be within (0.0, 1.0], "
            f"got {attack_speed_lateral_scale}"
        )
    attack_speed_backward_scale = float(
        get_runtime(
            "attack_speed_backward_scale",
            execution.V4A_ATTACK_SPEED_BACKWARD_SCALE_DEFAULT,
        )
    )
    if not 0.0 <= attack_speed_backward_scale <= attack_speed_lateral_scale:
        raise ValueError(
            "runtime.movement.v4a.engagement.attack_speed_backward_scale must be within "
            f"[0.0, attack_speed_lateral_scale], got backward={attack_speed_backward_scale}, "
            f"lateral={attack_speed_lateral_scale}"
        )
    movement_model_effective = resolve_movement_model(get_runtime("movement_model", "baseline"))[1]
    movement_cfg = {
        "model_effective": movement_model_effective,
        "symmetric_movement_sync_enabled": bool(get_run("symmetric_movement_sync_enabled", True)),
        "v4a_restore_strength": v4a_restore_strength,
        "v4a_reference_surface_mode": v4a_reference_surface_mode,
        "v4a_soft_morphology_relaxation": v4a_soft_morphology_relaxation,
        "v4a_shape_vs_advance_strength": v4a_shape_vs_advance_strength,
        "v4a_heading_relaxation": v4a_heading_relaxation,
        "v4a_battle_standoff_hold_band_ratio": v4a_battle_standoff_hold_band_ratio,
        "v4a_battle_target_front_strip_gap_bias": v4a_battle_target_front_strip_gap_bias,
        "v4a_battle_hold_weight_strength": v4a_battle_hold_weight_strength,
        "v4a_battle_relation_lead_ticks": v4a_battle_relation_lead_ticks,
        "v4a_battle_hold_relaxation": v4a_battle_hold_relaxation,
        "v4a_battle_approach_drive_relaxation": v4a_battle_approach_drive_relaxation,
        "v4a_battle_near_contact_internal_stability_blend": v4a_battle_near_contact_internal_stability_blend,
        "v4a_battle_near_contact_speed_relaxation": v4a_battle_near_contact_speed_relaxation,
        "engaged_speed_scale": engaged_speed_scale,
        "attack_speed_lateral_scale": attack_speed_lateral_scale,
        "attack_speed_backward_scale": attack_speed_backward_scale,
    }
    movement_cfg["v4a_restore_strength_effective"] = (
        movement_cfg["v4a_restore_strength"]
        if movement_cfg["model_effective"] == "v4a"
        else 1.0
    )
    movement_cfg["v4a_reference_surface_mode_effective"] = (
        movement_cfg["v4a_reference_surface_mode"]
        if movement_cfg["model_effective"] == "v4a"
        else execution.V4A_REFERENCE_SURFACE_MODE_RIGID_SLOTS
    )
    movement_cfg["v4a_soft_morphology_relaxation_effective"] = (
        movement_cfg["v4a_soft_morphology_relaxation"]
        if movement_cfg["model_effective"] == "v4a"
        else execution.V4A_SOFT_MORPHOLOGY_RELAXATION_DEFAULT
    )
    movement_cfg["v4a_shape_vs_advance_strength_effective"] = (
        movement_cfg["v4a_shape_vs_advance_strength"]
        if movement_cfg["model_effective"] == "v4a"
        else execution.V4A_SHAPE_VS_ADVANCE_STRENGTH_DEFAULT
    )
    movement_cfg["v4a_heading_relaxation_effective"] = (
        movement_cfg["v4a_heading_relaxation"]
        if movement_cfg["model_effective"] == "v4a"
        else execution.V4A_HEADING_RELAXATION_DEFAULT
    )
    movement_cfg["v4a_battle_standoff_hold_band_ratio_effective"] = (
        movement_cfg["v4a_battle_standoff_hold_band_ratio"]
        if movement_cfg["model_effective"] == "v4a"
        else execution.V4A_BATTLE_STANDOFF_HOLD_BAND_RATIO_DEFAULT
    )
    movement_cfg["v4a_battle_target_front_strip_gap_bias_effective"] = (
        movement_cfg["v4a_battle_target_front_strip_gap_bias"]
        if movement_cfg["model_effective"] == "v4a"
        else execution.V4A_BATTLE_TARGET_FRONT_STRIP_GAP_BIAS_DEFAULT
    )
    movement_cfg["v4a_battle_hold_weight_strength_effective"] = (
        movement_cfg["v4a_battle_hold_weight_strength"]
        if movement_cfg["model_effective"] == "v4a"
        else execution.V4A_BATTLE_HOLD_WEIGHT_STRENGTH_DEFAULT
    )
    movement_cfg["v4a_battle_relation_lead_ticks_effective"] = (
        movement_cfg["v4a_battle_relation_lead_ticks"]
        if movement_cfg["model_effective"] == "v4a"
        else execution.V4A_BATTLE_RELATION_LEAD_TICKS_DEFAULT
    )
    movement_cfg["v4a_battle_hold_relaxation_effective"] = (
        movement_cfg["v4a_battle_hold_relaxation"]
        if movement_cfg["model_effective"] == "v4a"
        else execution.V4A_BATTLE_HOLD_RELAXATION_DEFAULT
    )
    movement_cfg["v4a_battle_approach_drive_relaxation_effective"] = (
        movement_cfg["v4a_battle_approach_drive_relaxation"]
        if movement_cfg["model_effective"] == "v4a"
        else execution.V4A_BATTLE_APPROACH_DRIVE_RELAXATION_DEFAULT
    )
    movement_cfg["v4a_battle_near_contact_internal_stability_blend_effective"] = (
        movement_cfg["v4a_battle_near_contact_internal_stability_blend"]
        if movement_cfg["model_effective"] == "v4a"
        else execution.V4A_NEAR_CONTACT_INTERNAL_STABILITY_BLEND_DEFAULT
    )
    movement_cfg["v4a_battle_near_contact_speed_relaxation_effective"] = (
        movement_cfg["v4a_battle_near_contact_speed_relaxation"]
        if movement_cfg["model_effective"] == "v4a"
        else execution.V4A_NEAR_CONTACT_SPEED_RELAXATION_DEFAULT
    )
    movement_cfg["engaged_speed_scale_effective"] = (
        movement_cfg["engaged_speed_scale"]
        if movement_cfg["model_effective"] == "v4a"
        else execution.V4A_ENGAGED_SPEED_SCALE_DEFAULT
    )
    movement_cfg["attack_speed_lateral_scale_effective"] = (
        movement_cfg["attack_speed_lateral_scale"]
        if movement_cfg["model_effective"] == "v4a"
        else execution.V4A_ATTACK_SPEED_LATERAL_SCALE_DEFAULT
    )
    movement_cfg["attack_speed_backward_scale_effective"] = (
        movement_cfg["attack_speed_backward_scale"]
        if movement_cfg["model_effective"] == "v4a"
        else execution.V4A_ATTACK_SPEED_BACKWARD_SCALE_DEFAULT
    )
    movement_cfg.setdefault("expected_reference_spacing_effective", None)
    movement_cfg.setdefault("reference_layout_mode_effective", None)
    return movement_cfg


def _build_boundary_cfg(get_runtime) -> dict:
    return {
        "enabled": bool(get_runtime("boundary_enabled", False)),
        "hard_enabled": bool(get_runtime("boundary_hard_enabled", True)),
        "soft_strength": float(get_runtime("boundary_soft_strength", 1.0)),
    }


def _resolve_v4a_reference_cfg(settings: dict, get_runtime, *, movement_model_effective: str) -> dict:
    physical_min_spacing = float(get_runtime("min_unit_spacing", 1.0))
    if physical_min_spacing <= 0.0:
        raise ValueError(
            "runtime.physical.movement_low_level.min_unit_spacing must be > 0, "
            f"got {physical_min_spacing}"
        )
    expected_reference_spacing = float(physical_min_spacing)
    reference_layout_mode = REFERENCE_LAYOUT_MODE_RECT_CENTERED_4_0
    if movement_model_effective != "v4a":
        return {
            "expected_reference_spacing": expected_reference_spacing,
            "physical_min_spacing": physical_min_spacing,
            "reference_layout_mode": reference_layout_mode,
        }
    expected_reference_spacing_raw = get_runtime(
        "v4a_expected_reference_spacing",
        settings_api.MISSING,
    )
    if expected_reference_spacing_raw is settings_api.MISSING:
        raise ValueError(
            "runtime.movement.v4a.reference.expected_reference_spacing must be provided when movement_model=v4a"
        )
    expected_reference_spacing = float(expected_reference_spacing_raw)
    if expected_reference_spacing <= 0.0:
        raise ValueError(
            "runtime.movement.v4a.reference.expected_reference_spacing must be > 0, "
            f"got {expected_reference_spacing}"
        )
    reference_layout_mode_raw = get_runtime(
        "v4a_reference_layout_mode",
        settings_api.MISSING,
    )
    if reference_layout_mode_raw is settings_api.MISSING:
        raise ValueError(
            "runtime.movement.v4a.reference.layout_mode must be provided when movement_model=v4a"
        )
    reference_layout_mode = _require_choice(
        "runtime.movement.v4a.reference.layout_mode",
        reference_layout_mode_raw,
        REFERENCE_LAYOUT_MODE_LABELS,
    )
    return {
        "expected_reference_spacing": expected_reference_spacing,
        "physical_min_spacing": physical_min_spacing,
        "reference_layout_mode": reference_layout_mode,
    }


def _spawn_formation_units(
    *,
    units: dict[str, UnitState],
    fleet_id: str,
    unit_count: int,
    aspect_ratio_local: float,
    origin_x: float,
    origin_y: float,
    dir_xy: tuple[float, float],
    perp_xy: tuple[float, float],
    unit_spacing: float,
    layout_mode: str,
    unit_speed: float,
    unit_max_hit_points: float,
    arena_size: float,
) -> list[str]:
    unit_ids = []
    row_counts = _resolve_initial_formation_layout(unit_count, aspect_ratio_local, layout_mode)
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
    layout_mode: str = FORMATION_LAYOUT_MODE_RECT_CENTERED_ROWS,
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

    fleet_a_unit_ids = _spawn_formation_units(
        units=units,
        fleet_id="A",
        unit_count=fleet_a_size_effective,
        aspect_ratio_local=fleet_a_aspect_ratio_effective,
        origin_x=fleet_a_origin_x_effective,
        origin_y=fleet_a_origin_y_effective,
        dir_xy=dir_a,
        perp_xy=perp_a,
        unit_spacing=unit_spacing,
        layout_mode=layout_mode,
        unit_speed=unit_speed,
        unit_max_hit_points=unit_max_hit_points,
        arena_size=arena_size,
    )
    fleet_b_unit_ids = _spawn_formation_units(
        units=units,
        fleet_id="B",
        unit_count=fleet_b_size_effective,
        aspect_ratio_local=fleet_b_aspect_ratio_effective,
        origin_x=fleet_b_origin_x_effective,
        origin_y=fleet_b_origin_y_effective,
        dir_xy=dir_b,
        perp_xy=perp_b,
        unit_spacing=unit_spacing,
        layout_mode=layout_mode,
        unit_speed=unit_speed,
        unit_max_hit_points=unit_max_hit_points,
        arena_size=arena_size,
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
        last_fleet_cohesion_score=build_initial_cohesion_map(fleets.keys()),
    )


def build_single_fleet_initial_state(
    *,
    fleet_params: PersonalityParameters,
    fleet_size: int,
    fleet_aspect_ratio: float,
    unit_spacing: float,
    unit_speed: float,
    unit_max_hit_points: float,
    arena_size: float,
    layout_mode: str = FORMATION_LAYOUT_MODE_RECT_CENTERED_ROWS,
    fleet_origin_x: float | None = None,
    fleet_origin_y: float | None = None,
    fleet_facing_angle_deg: float | None = None,
) -> BattleState:
    fleet_size_effective = int(fleet_size)
    if fleet_size_effective < 1:
        raise ValueError(f"fleet_size must be >= 1, got {fleet_size_effective}")
    fleet_aspect_ratio_effective = float(fleet_aspect_ratio)
    if fleet_aspect_ratio_effective <= 0.0:
        raise ValueError(f"fleet_aspect_ratio must be > 0, got {fleet_aspect_ratio_effective}")

    spawn_margin = max(1.0, arena_size * DEFAULT_SPAWN_MARGIN_RATIO)
    fleet_origin_x_effective = spawn_margin if fleet_origin_x is None else float(fleet_origin_x)
    fleet_origin_y_effective = spawn_margin if fleet_origin_y is None else float(fleet_origin_y)
    fleet_facing_angle_deg_effective = 0.0 if fleet_facing_angle_deg is None else float(fleet_facing_angle_deg)
    dir_a = _direction_from_angle_deg(fleet_facing_angle_deg_effective)
    perp_a = (-dir_a[1], dir_a[0])

    units: dict[str, UnitState] = {}
    fleet_unit_ids = _spawn_formation_units(
        units=units,
        fleet_id="A",
        unit_count=fleet_size_effective,
        aspect_ratio_local=fleet_aspect_ratio_effective,
        origin_x=fleet_origin_x_effective,
        origin_y=fleet_origin_y_effective,
        dir_xy=dir_a,
        perp_xy=perp_a,
        unit_spacing=unit_spacing,
        layout_mode=layout_mode,
        unit_speed=unit_speed,
        unit_max_hit_points=unit_max_hit_points,
        arena_size=arena_size,
    )
    fleets = {
        "A": FleetState(fleet_id="A", parameters=fleet_params, unit_ids=tuple(fleet_unit_ids)),
    }
    return BattleState(
        tick=0,
        dt=DEFAULT_DT,
        arena_size=arena_size,
        units=units,
        fleets=fleets,
        last_fleet_cohesion_score=build_initial_cohesion_map(fleets.keys()),
    )


def prepare_active_scenario(base_dir: Path, *, settings_override: dict | None = None) -> dict:
    settings = (
        settings_override
        if settings_override is not None
        else settings_api.load_layered_test_run_settings(base_dir)
    )
    get_battlefield = partial(settings_api.get_battlefield_setting, settings)
    get_contact = partial(settings_api.get_contact_test_setting, settings)
    get_fleet = partial(settings_api.get_fleet_setting, settings)
    get_observer = partial(settings_api.get_observer_setting, settings)
    get_run = partial(settings_api.get_run_control_setting, settings)
    get_runtime = partial(settings_api.get_runtime_setting, settings)
    get_runtime_metatype = partial(settings_api.get_runtime_metatype_setting, settings)
    get_unit = partial(settings_api.get_unit_setting, settings)

    common_context = _load_common_scenario_context(
        base_dir,
        settings,
        get_battlefield=get_battlefield,
        get_run=get_run,
        get_runtime_metatype=get_runtime_metatype,
    )
    archetypes = common_context["archetypes"]
    metatype_settings = common_context["metatype_settings"]
    effective_random_seed = common_context["effective_random_seed"]
    effective_metatype_random_seed = common_context["effective_metatype_random_seed"]
    effective_background_map_seed = common_context["effective_background_map_seed"]

    archetype_rng = random.Random(int(effective_metatype_random_seed))
    fleet_a_data = resolve_fleet_archetype_data(
        archetypes,
        metatype_settings,
        get_fleet("fleet_a_archetype_id", "default"),
        rng=archetype_rng,
    )
    fleet_b_data = resolve_fleet_archetype_data(
        archetypes,
        metatype_settings,
        get_fleet("fleet_b_archetype_id", "default"),
        rng=archetype_rng,
    )
    fleet_a_params = to_personality_parameters(fleet_a_data)
    fleet_b_params = to_personality_parameters(fleet_b_data)

    battlefield_cfg = common_context["battlefield_cfg"]
    run_cfg = _build_run_cfg(get_run)
    movement_cfg = _build_movement_cfg(
        get_runtime,
        get_run,
    )
    boundary_cfg = _build_boundary_cfg(get_runtime)
    v4a_reference_cfg = _resolve_v4a_reference_cfg(
        settings,
        get_runtime,
        movement_model_effective=movement_cfg["model_effective"],
    )
    movement_cfg["expected_reference_spacing_effective"] = float(v4a_reference_cfg["expected_reference_spacing"])
    movement_cfg["reference_layout_mode_effective"] = str(v4a_reference_cfg["reference_layout_mode"])
    spawn_margin = max(1.0, battlefield_cfg["arena_size"] * DEFAULT_SPAWN_MARGIN_RATIO)
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
        "unit_spacing": float(v4a_reference_cfg["expected_reference_spacing"]),
        "reference_layout_mode": str(v4a_reference_cfg["reference_layout_mode"]),
    }
    if min(fleet_cfg["sizes"].values()) < 1:
        raise ValueError(f"initial fleet sizes must be >= 1, got {fleet_cfg['sizes']}")
    if (
        min(fleet_cfg["aspect_ratios"].values()) <= 0.0
        or fleet_cfg["unit_spacing"] <= 0.0
        or float(v4a_reference_cfg["physical_min_spacing"]) <= 0.0
    ):
        raise ValueError(
            "initial geometry aspect ratios, expected reference spacing, and runtime min_unit_spacing must be > 0, "
            f"got {fleet_cfg['aspect_ratios']}, expected_reference_spacing={fleet_cfg['unit_spacing']}, "
            f"min_unit_spacing={v4a_reference_cfg['physical_min_spacing']}"
        )

    unit_cfg = _build_unit_cfg(get_unit, get_runtime)
    initial_state = build_initial_state(
        fleet_a_params=fleet_a_params,
        fleet_b_params=fleet_b_params,
        fleet_a_size=fleet_cfg["sizes"]["A"],
        fleet_b_size=fleet_cfg["sizes"]["B"],
        fleet_a_aspect_ratio=fleet_cfg["aspect_ratios"]["A"],
        fleet_b_aspect_ratio=fleet_cfg["aspect_ratios"]["B"],
        unit_spacing=fleet_cfg["unit_spacing"],
        layout_mode=fleet_cfg["reference_layout_mode"],
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
        "fire_optimal_range_ratio": float(get_runtime("fire_optimal_range_ratio", 1.0)),
        "contact_hysteresis_h": float(get_runtime("contact_hysteresis_h", 0.1)),
        "alpha_sep": float(get_runtime("alpha_sep", 0.6)),
        "hostile_contact_impedance_mode": _require_choice(
            "runtime.physical.contact.hostile_contact_impedance.active_mode",
            get_contact(("active_mode",), execution.HOSTILE_CONTACT_IMPEDANCE_MODE_DEFAULT),
            execution.HOSTILE_CONTACT_IMPEDANCE_MODE_LABELS,
        ),
        "hybrid_v2": {
            key: float(get_contact(("hybrid_v2", key), default))
            for key, default in {
                "radius_multiplier": execution.HOSTILE_CONTACT_IMPEDANCE_V2_RADIUS_MULTIPLIER_DEFAULT,
                "repulsion_max_disp_ratio": execution.HOSTILE_CONTACT_IMPEDANCE_V2_REPULSION_MAX_DISP_RATIO_DEFAULT,
                "forward_damping_strength": execution.HOSTILE_CONTACT_IMPEDANCE_V2_FORWARD_DAMPING_STRENGTH_DEFAULT,
            }.items()
        },
        "intent_unified_spacing_v1": {
            key: float(get_contact(("intent_unified_spacing_v1", key), default))
            for key, default in {
                "scale": execution.HOSTILE_INTENT_UNIFIED_SPACING_SCALE_DEFAULT,
                "strength": execution.HOSTILE_INTENT_UNIFIED_SPACING_STRENGTH_DEFAULT,
            }.items()
        },
    }
    if not 0.0 <= contact_cfg["fire_optimal_range_ratio"] <= 1.0:
        raise ValueError(
            "runtime.physical.fire_control.fire_optimal_range_ratio must be within [0.0, 1.0], "
            f"got {contact_cfg['fire_optimal_range_ratio']}"
        )
    contact_cfg["ch_enabled"] = contact_cfg["contact_hysteresis_h"] > 0.0

    execution_cfg = {
        "steps": run_cfg["max_time_steps"],
        "capture_positions": False,
        "frame_stride": execution.DEFAULT_FRAME_STRIDE,
        "include_target_lines": False,
        "print_tick_summary": False,
        "plot_diagnostics_enabled": run_cfg["observer_enabled"],
        "post_elimination_extra_ticks": run_cfg["post_resolution_hold_steps"],
    }
    simulation_runtime_cfg = {
        "movement_model": movement_cfg["model_effective"],
        "movement": movement_cfg,
        "contact": {
            **contact_cfg,
            "separation_radius": float(v4a_reference_cfg["physical_min_spacing"]),
        },
        "boundary": boundary_cfg,
    }
    simulation_observer_cfg = {
        "enabled": run_cfg["observer_enabled"],
        "tick_timing_enabled": bool(get_observer("tick_timing_enabled", True)),
        "runtime_diag_enabled": False,
    }

    return {
        "initial_state": initial_state,
        "engine_cls": execution.TestModeEngineTickSkeleton,
        "execution_cfg": execution_cfg,
        "runtime_cfg": simulation_runtime_cfg,
        "observer_cfg": simulation_observer_cfg,
        "fleet_a_data": fleet_a_data,
        "fleet_b_data": fleet_b_data,
        "summary": {
            "effective_random_seed": effective_random_seed,
            "effective_metatype_random_seed": effective_metatype_random_seed,
            "effective_background_map_seed": effective_background_map_seed,
            "movement_model_effective": movement_cfg["model_effective"],
            "v4a_restore_strength_effective": float(movement_cfg["v4a_restore_strength_effective"]),
            "v4a_reference_surface_mode_effective": str(movement_cfg["v4a_reference_surface_mode_effective"]),
            "v4a_soft_morphology_relaxation_effective": float(
                movement_cfg["v4a_soft_morphology_relaxation_effective"]
            ),
            "v4a_shape_vs_advance_strength_effective": float(
                movement_cfg["v4a_shape_vs_advance_strength_effective"]
            ),
            "v4a_heading_relaxation_effective": float(
                movement_cfg["v4a_heading_relaxation_effective"]
            ),
            "v4a_battle_standoff_hold_band_ratio_effective": float(
                movement_cfg["v4a_battle_standoff_hold_band_ratio_effective"]
            ),
            "v4a_battle_target_front_strip_gap_bias_effective": float(
                movement_cfg["v4a_battle_target_front_strip_gap_bias_effective"]
            ),
            "v4a_battle_hold_weight_strength_effective": float(
                movement_cfg["v4a_battle_hold_weight_strength_effective"]
            ),
            "v4a_battle_relation_lead_ticks_effective": float(
                movement_cfg["v4a_battle_relation_lead_ticks_effective"]
            ),
            "v4a_battle_hold_relaxation_effective": float(
                movement_cfg["v4a_battle_hold_relaxation_effective"]
            ),
            "v4a_battle_approach_drive_relaxation_effective": float(
                movement_cfg["v4a_battle_approach_drive_relaxation_effective"]
            ),
            "v4a_battle_near_contact_internal_stability_blend_effective": float(
                movement_cfg["v4a_battle_near_contact_internal_stability_blend_effective"]
            ),
            "v4a_battle_near_contact_speed_relaxation_effective": float(
                movement_cfg["v4a_battle_near_contact_speed_relaxation_effective"]
            ),
            "engaged_speed_scale_effective": float(
                movement_cfg["engaged_speed_scale_effective"]
            ),
            "attack_speed_lateral_scale_effective": float(
                movement_cfg["attack_speed_lateral_scale_effective"]
            ),
            "attack_speed_backward_scale_effective": float(
                movement_cfg["attack_speed_backward_scale_effective"]
            ),
            "expected_reference_spacing_effective": float(v4a_reference_cfg["expected_reference_spacing"]),
            "physical_min_spacing_effective": float(v4a_reference_cfg["physical_min_spacing"]),
            "reference_layout_mode_effective": str(v4a_reference_cfg["reference_layout_mode"]),
            "hostile_contact_impedance_mode": contact_cfg["hostile_contact_impedance_mode"],
            "fire_quality_alpha_effective": float(contact_cfg["fire_quality_alpha"]),
            "fire_optimal_range_ratio_effective": float(contact_cfg["fire_optimal_range_ratio"]),
            "observer_enabled": run_cfg["observer_enabled"],
        },
    }


def prepare_neutral_transit_fixture(base_dir: Path, *, settings_override: dict | None = None) -> dict:
    settings = (
        settings_override
        if settings_override is not None
        else settings_api.load_layered_test_run_settings(base_dir)
    )
    get_battlefield = partial(settings_api.get_battlefield_setting, settings)
    get_fixture = partial(settings_api.get_fixture_setting, settings)
    get_observer = partial(settings_api.get_observer_setting, settings)
    get_run = partial(settings_api.get_run_control_setting, settings)
    get_runtime = partial(settings_api.get_runtime_setting, settings)
    get_runtime_metatype = partial(settings_api.get_runtime_metatype_setting, settings)
    get_unit = partial(settings_api.get_unit_setting, settings)

    active_mode = _require_choice(
        "fixture.active_mode",
        get_fixture(("active_mode",), execution.FIXTURE_MODE_BATTLE),
        execution.FIXTURE_MODE_LABELS,
    )
    if active_mode != execution.FIXTURE_MODE_NEUTRAL:
        raise ValueError(
            "prepare_neutral_transit_fixture requires fixture.active_mode=neutral, "
            f"got {active_mode!r}"
        )
    common_context = _load_common_scenario_context(
        base_dir,
        settings,
        get_battlefield=get_battlefield,
        get_run=get_run,
        get_runtime_metatype=get_runtime_metatype,
    )
    archetypes = common_context["archetypes"]
    metatype_settings = common_context["metatype_settings"]
    effective_random_seed = common_context["effective_random_seed"]
    effective_metatype_random_seed = common_context["effective_metatype_random_seed"]
    effective_background_map_seed = common_context["effective_background_map_seed"]

    archetype_rng = random.Random(int(effective_metatype_random_seed))
    fleet_data = resolve_fleet_archetype_data(
        archetypes,
        metatype_settings,
        str(get_fixture((execution.FIXTURE_MODE_NEUTRAL, "fleet_archetype_id"), "default")),
        rng=archetype_rng,
    )
    fleet_params = to_personality_parameters(fleet_data)

    battlefield_cfg = common_context["battlefield_cfg"]
    default_origin_x = max(1.0, battlefield_cfg["arena_size"] * DEFAULT_SPAWN_MARGIN_RATIO)
    default_origin_y = battlefield_cfg["arena_size"] * 0.5
    origin_x, origin_y = (
        float(value)
        for value in get_fixture(
            (execution.FIXTURE_MODE_NEUTRAL, "origin_xy"),
            (default_origin_x, default_origin_y),
        )
    )
    objective_x, objective_y = (
        float(value)
        for value in get_fixture(
            (execution.FIXTURE_MODE_NEUTRAL, "objective_point_xy"),
            (battlefield_cfg["arena_size"] - default_origin_x, default_origin_y),
        )
    )
    fleet_size = int(get_fixture((execution.FIXTURE_MODE_NEUTRAL, "fleet_size"), 100))
    fleet_aspect_ratio = float(get_fixture((execution.FIXTURE_MODE_NEUTRAL, "aspect_ratio"), 4.0))
    stop_radius = float(get_fixture((execution.FIXTURE_MODE_NEUTRAL, "stop_radius"), 2.0))
    facing_angle_deg = float(get_fixture((execution.FIXTURE_MODE_NEUTRAL, "facing_angle_deg"), 0.0))

    if stop_radius < 0.0:
        raise ValueError(f"fixture.neutral.stop_radius must be >= 0, got {stop_radius}")

    run_cfg = _build_run_cfg(get_run)
    movement_cfg = _build_movement_cfg(
        get_runtime,
        get_run,
    )
    v4a_reference_cfg = _resolve_v4a_reference_cfg(
        settings,
        get_runtime,
        movement_model_effective=movement_cfg["model_effective"],
    )
    movement_cfg["expected_reference_spacing_effective"] = float(v4a_reference_cfg["expected_reference_spacing"])
    movement_cfg["reference_layout_mode_effective"] = str(v4a_reference_cfg["reference_layout_mode"])

    unit_cfg = _build_unit_cfg(get_unit, get_runtime)
    unit_spacing = float(v4a_reference_cfg["expected_reference_spacing"])
    if fleet_aspect_ratio <= 0.0 or unit_spacing <= 0.0:
        raise ValueError(
            "fixture.neutral.aspect_ratio and expected reference spacing must be > 0, "
            f"got aspect_ratio={fleet_aspect_ratio}, spacing={unit_spacing}"
        )

    initial_state = build_single_fleet_initial_state(
        fleet_params=fleet_params,
        fleet_size=fleet_size,
        fleet_aspect_ratio=fleet_aspect_ratio,
        unit_spacing=unit_spacing,
        layout_mode=str(v4a_reference_cfg["reference_layout_mode"]),
        unit_speed=unit_cfg["speed"],
        unit_max_hit_points=unit_cfg["max_hit_points"],
        arena_size=battlefield_cfg["arena_size"],
        fleet_origin_x=origin_x,
        fleet_origin_y=origin_y,
        fleet_facing_angle_deg=facing_angle_deg,
    )

    execution_cfg = {
        "steps": run_cfg["max_time_steps"],
        "capture_positions": False,
        "frame_stride": execution.DEFAULT_FRAME_STRIDE,
        "include_target_lines": False,
        "print_tick_summary": False,
        "plot_diagnostics_enabled": True,
        "post_elimination_extra_ticks": run_cfg["post_resolution_hold_steps"],
        "fixture": {
            "active_mode": execution.FIXTURE_MODE_NEUTRAL,
            "fleet_id": "A",
            "objective_contract_3d": {
                "anchor_point_xyz": (objective_x, objective_y, 0.0),
                "source_owner": "fixture",
                "objective_mode": "point_anchor",
                "no_enemy_semantics": "enemy_term_zero",
            },
            "stop_radius": stop_radius,
        },
    }
    simulation_runtime_cfg = {
        "movement_model": movement_cfg["model_effective"],
        "movement": movement_cfg,
        "contact": {
            "attack_range": unit_cfg["attack_range"],
            "damage_per_tick": unit_cfg["damage_per_tick"],
            "fire_quality_alpha": 0.0,
            "fire_optimal_range_ratio": float(get_runtime("fire_optimal_range_ratio", 1.0)),
            "contact_hysteresis_h": 0.0,
            "alpha_sep": float(get_runtime("alpha_sep", 0.6)),
            "hostile_contact_impedance_mode": execution.HOSTILE_CONTACT_IMPEDANCE_MODE_OFF,
            "hybrid_v2": {
                "radius_multiplier": execution.HOSTILE_CONTACT_IMPEDANCE_V2_RADIUS_MULTIPLIER_DEFAULT,
                "repulsion_max_disp_ratio": execution.HOSTILE_CONTACT_IMPEDANCE_V2_REPULSION_MAX_DISP_RATIO_DEFAULT,
                "forward_damping_strength": execution.HOSTILE_CONTACT_IMPEDANCE_V2_FORWARD_DAMPING_STRENGTH_DEFAULT,
            },
            "intent_unified_spacing_v1": {
                "scale": execution.HOSTILE_INTENT_UNIFIED_SPACING_SCALE_DEFAULT,
                "strength": execution.HOSTILE_INTENT_UNIFIED_SPACING_STRENGTH_DEFAULT,
            },
            "ch_enabled": False,
            "separation_radius": float(v4a_reference_cfg["physical_min_spacing"]),
        },
        "boundary": _build_boundary_cfg(get_runtime),
    }
    simulation_observer_cfg = {
        "enabled": run_cfg["observer_enabled"],
        "tick_timing_enabled": bool(get_observer("tick_timing_enabled", True)),
        "runtime_diag_enabled": True,
    }

    return {
        "initial_state": initial_state,
        "engine_cls": execution.TestModeEngineTickSkeleton,
        "execution_cfg": execution_cfg,
        "runtime_cfg": simulation_runtime_cfg,
        "observer_cfg": simulation_observer_cfg,
        "fleet_data": fleet_data,
        "summary": {
            "effective_random_seed": effective_random_seed,
            "effective_metatype_random_seed": effective_metatype_random_seed,
            "effective_background_map_seed": effective_background_map_seed,
            "movement_model_effective": movement_cfg["model_effective"],
            "v4a_restore_strength_effective": float(movement_cfg["v4a_restore_strength_effective"]),
            "v4a_reference_surface_mode_effective": str(movement_cfg["v4a_reference_surface_mode_effective"]),
            "v4a_soft_morphology_relaxation_effective": float(
                movement_cfg["v4a_soft_morphology_relaxation_effective"]
            ),
            "v4a_shape_vs_advance_strength_effective": float(
                movement_cfg["v4a_shape_vs_advance_strength_effective"]
            ),
            "v4a_heading_relaxation_effective": float(
                movement_cfg["v4a_heading_relaxation_effective"]
            ),
            "v4a_battle_standoff_hold_band_ratio_effective": float(
                movement_cfg["v4a_battle_standoff_hold_band_ratio_effective"]
            ),
            "v4a_battle_target_front_strip_gap_bias_effective": float(
                movement_cfg["v4a_battle_target_front_strip_gap_bias_effective"]
            ),
            "v4a_battle_hold_weight_strength_effective": float(
                movement_cfg["v4a_battle_hold_weight_strength_effective"]
            ),
            "v4a_battle_relation_lead_ticks_effective": float(
                movement_cfg["v4a_battle_relation_lead_ticks_effective"]
            ),
            "v4a_battle_hold_relaxation_effective": float(
                movement_cfg["v4a_battle_hold_relaxation_effective"]
            ),
            "v4a_battle_approach_drive_relaxation_effective": float(
                movement_cfg["v4a_battle_approach_drive_relaxation_effective"]
            ),
            "v4a_battle_near_contact_internal_stability_blend_effective": float(
                movement_cfg["v4a_battle_near_contact_internal_stability_blend_effective"]
            ),
            "v4a_battle_near_contact_speed_relaxation_effective": float(
                movement_cfg["v4a_battle_near_contact_speed_relaxation_effective"]
            ),
            "engaged_speed_scale_effective": float(
                movement_cfg["engaged_speed_scale_effective"]
            ),
            "attack_speed_lateral_scale_effective": float(
                movement_cfg["attack_speed_lateral_scale_effective"]
            ),
            "attack_speed_backward_scale_effective": float(
                movement_cfg["attack_speed_backward_scale_effective"]
            ),
            "expected_reference_spacing_effective": float(v4a_reference_cfg["expected_reference_spacing"]),
            "physical_min_spacing_effective": float(v4a_reference_cfg["physical_min_spacing"]),
            "reference_layout_mode_effective": str(v4a_reference_cfg["reference_layout_mode"]),
            "hostile_contact_impedance_mode": simulation_runtime_cfg["contact"]["hostile_contact_impedance_mode"],
            "fire_quality_alpha_effective": float(simulation_runtime_cfg["contact"]["fire_quality_alpha"]),
            "fire_optimal_range_ratio_effective": float(simulation_runtime_cfg["contact"]["fire_optimal_range_ratio"]),
            "observer_enabled": run_cfg["observer_enabled"],
            "active_mode": execution.FIXTURE_MODE_NEUTRAL,
        },
    }
