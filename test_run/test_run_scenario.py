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
REFERENCE_LAYOUT_MODE_RECT_CENTERED_ROWS = "rect_centered_rows"
REFERENCE_LAYOUT_MODE_LABELS = {
    REFERENCE_LAYOUT_MODE_RECT_CENTERED_ROWS,
}
TEST_MODE_LABELS = {
    0: "default",
    1: "observe",
    2: "test",
}
COHESION_DECISION_SOURCE_LABELS = {
    "baseline": "baseline",
    "v2": "v2",
    "v3_test": "v3_test",
}
BASELINE_COHESION_DECISION_SOURCE = "v3_test"
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


def parse_test_mode(raw_value) -> int:
    if isinstance(raw_value, str):
        value_str = raw_value.strip().lower()
        if value_str in TEST_MODE_LABELS.values():
            for code, label in TEST_MODE_LABELS.items():
                if label == value_str:
                    return code
        if value_str.isdigit():
            raw_value = int(value_str)
    try:
        parsed = int(raw_value)
    except (TypeError, ValueError):
        return 0
    if parsed not in TEST_MODE_LABELS:
        return 0
    return parsed


def test_mode_label(mode_code: int) -> str:
    return TEST_MODE_LABELS.get(int(mode_code), TEST_MODE_LABELS[0])


def resolve_runtime_decision_source(raw_value, test_mode: int) -> tuple[str, str]:
    requested = str(raw_value).strip().lower()
    if requested not in COHESION_DECISION_SOURCE_LABELS:
        requested = "baseline"
    baseline_source = BASELINE_COHESION_DECISION_SOURCE
    effective = baseline_source if requested == "baseline" else requested
    if int(test_mode) < 2 and effective != baseline_source:
        print(
            f"[mode] cohesion_decision_source={requested} requested but test_mode={test_mode} only permits baseline runtime; remapping to {baseline_source}"
        )
        effective = baseline_source
    return requested, effective


def resolve_movement_model(raw_value, test_mode: int) -> tuple[str, str]:
    requested = str(raw_value).strip().lower()
    if requested == "v1":
        raise ValueError("runtime.selectors.movement_model=v1 has been retired; use baseline, v3a, or v4a")
    if requested not in {"baseline", "v3a", "v4a"}:
        allowed_text = ", ".join(sorted({"baseline", "v3a", "v4a"}))
        raise ValueError(
            f"runtime.selectors.movement_model must be one of {{{allowed_text}}}, got {raw_value!r}"
        )
    baseline_model = "v3a"
    if requested == "baseline":
        effective = baseline_model
    else:
        effective = requested
    if int(test_mode) < 2 and effective != baseline_model:
        print(
            f"[mode] movement_model={requested} requested but test_mode={test_mode} only permits baseline runtime; remapping to {baseline_model}"
        )
        effective = baseline_model
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
        REFERENCE_LAYOUT_MODE_LABELS,
    )
    if resolved_layout_mode != REFERENCE_LAYOUT_MODE_RECT_CENTERED_ROWS:
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
    get_runtime,
    *,
    max_time_steps_override: int | None = None,
    test_mode_name_override: str | None = None,
) -> dict:
    test_mode = parse_test_mode(get_run("test_mode", 0))
    runtime_decision_source_requested, runtime_decision_source_effective = resolve_runtime_decision_source(
        get_runtime("cohesion_decision_source", "baseline"),
        test_mode,
    )
    post_resolution_hold_steps = int(get_run("post_resolution_hold_steps", DEFAULT_POST_RESOLUTION_HOLD_STEPS))
    if post_resolution_hold_steps < 0:
        raise ValueError(
            "run_control.post_resolution_hold_steps must be >= 0, "
            f"got {post_resolution_hold_steps}"
        )
    return {
        "max_time_steps": (
            int(get_run("max_time_steps", -1))
            if max_time_steps_override is None
            else int(max_time_steps_override)
        ),
        "post_resolution_hold_steps": post_resolution_hold_steps,
        "test_mode": test_mode,
        "test_mode_name": (
            str(test_mode_name_override)
            if test_mode_name_override is not None
            else test_mode_label(test_mode)
        ),
        "observer_enabled": test_mode >= 1,
        "export_battle_report": False,
        "runtime_decision_source_requested": runtime_decision_source_requested,
        "runtime_decision_source_effective": runtime_decision_source_effective,
    }


def _build_movement_cfg(get_runtime, *, runtime_decision_source_effective: str, test_mode: int) -> dict:
    v4a_restore_strength = float(get_runtime("v4a_restore_strength", 1.0))
    if not 0.0 <= v4a_restore_strength <= 1.0:
        raise ValueError(
            "runtime.movement.v4a.test_only.restore_strength must be within [0.0, 1.0], "
            f"got {v4a_restore_strength}"
        )
    v4a_reference_surface_mode = _require_choice(
        "runtime.movement.v4a.test_only.reference_surface_mode",
        get_runtime("v4a_reference_surface_mode", execution.V4A_REFERENCE_SURFACE_MODE_RIGID_SLOTS),
        execution.V4A_REFERENCE_SURFACE_MODE_LABELS,
    )
    v4a_soft_morphology_relaxation = float(
        get_runtime("v4a_soft_morphology_relaxation", execution.V4A_SOFT_MORPHOLOGY_RELAXATION_DEFAULT)
    )
    if not 0.0 < v4a_soft_morphology_relaxation <= 1.0:
        raise ValueError(
            "runtime.movement.v4a.test_only.soft_morphology_relaxation must be within (0.0, 1.0], "
            f"got {v4a_soft_morphology_relaxation}"
        )
    movement_cfg = {
        "model_effective": resolve_movement_model(get_runtime("movement_model", "baseline"), test_mode)[1],
        "experiment_effective": _require_choice(
            "runtime.movement_v3a_experiment",
            get_runtime("movement_v3a_experiment", execution.V3A_EXPERIMENT_BASE),
            execution.V3A_EXPERIMENT_LABELS,
        ),
        "centroid_probe_scale": float(get_runtime("centroid_probe_scale", 1.0)),
        "pre_tl_target_substrate": _require_choice(
            "runtime.pre_tl_target_substrate",
            get_runtime("pre_tl_target_substrate", execution.PRE_TL_TARGET_SUBSTRATE_DEFAULT),
            execution.PRE_TL_TARGET_SUBSTRATE_LABELS,
        ),
        "symmetric_movement_sync_enabled": bool(get_runtime("symmetric_movement_sync_enabled", True)),
        "continuous_fr_shaping": {
            "enabled": bool(get_runtime("continuous_fr_shaping_enabled", False)),
            "mode": _require_choice(
                "runtime.continuous_fr_shaping_mode",
                get_runtime("continuous_fr_shaping_mode", execution.CONTINUOUS_FR_SHAPING_OFF),
                execution.CONTINUOUS_FR_SHAPING_LABELS,
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
        "v2_connect_radius_multiplier": 1.0,
        "v3_connect_radius_multiplier_effective": (
            float(get_runtime("v3_connect_radius_multiplier", execution.BASELINE_V3_CONNECT_RADIUS_MULTIPLIER))
            if runtime_decision_source_effective == "v3_test"
            else 1.0
        ),
        "v3_r_ref_radius_multiplier_effective": (
            float(get_runtime("v3_r_ref_radius_multiplier", execution.BASELINE_V3_R_REF_RADIUS_MULTIPLIER))
            if runtime_decision_source_effective == "v3_test"
            else 1.0
        ),
        "v4a_restore_strength": v4a_restore_strength,
        "v4a_reference_surface_mode": v4a_reference_surface_mode,
        "v4a_soft_morphology_relaxation": v4a_soft_morphology_relaxation,
    }
    movement_cfg["centroid_probe_scale_effective"] = (
        movement_cfg["centroid_probe_scale"]
        if movement_cfg["model_effective"] in {"v3a", "v4a"}
        and movement_cfg["experiment_effective"] == execution.V3A_EXPERIMENT_PRECONTACT_CENTROID_PROBE
        else 1.0
    )
    movement_cfg["continuous_fr_shaping"]["effective"] = (
        movement_cfg["model_effective"] == "v3a"
        and movement_cfg["experiment_effective"] == execution.V3A_EXPERIMENT_PRECONTACT_CENTROID_PROBE
        and movement_cfg["continuous_fr_shaping"]["enabled"]
        and movement_cfg["continuous_fr_shaping"]["mode"] != execution.CONTINUOUS_FR_SHAPING_OFF
        and movement_cfg["continuous_fr_shaping"]["a"] > 0.0
    )
    movement_cfg["continuous_fr_shaping"]["mode_effective"] = (
        movement_cfg["continuous_fr_shaping"]["mode"]
        if movement_cfg["continuous_fr_shaping"]["effective"]
        else execution.CONTINUOUS_FR_SHAPING_OFF
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
    reference_layout_mode = REFERENCE_LAYOUT_MODE_RECT_CENTERED_ROWS
    if movement_model_effective != "v4a":
        return {
            "expected_reference_spacing": expected_reference_spacing,
            "physical_min_spacing": physical_min_spacing,
            "reference_layout_mode": reference_layout_mode,
        }
    runtime_section = settings.get("runtime", {})
    if not isinstance(runtime_section, dict):
        runtime_section = {}
    v4a_testonly_cfg = settings_api.get_nested_mapping_value(
        runtime_section,
        ("movement", "v4a", "test_only"),
        {},
    )
    if not isinstance(v4a_testonly_cfg, dict):
        v4a_testonly_cfg = {}
    if "expected_reference_spacing" not in v4a_testonly_cfg:
        raise ValueError(
            "runtime.movement.v4a.test_only.expected_reference_spacing must be provided when movement_model=v4a"
        )
    expected_reference_spacing = float(v4a_testonly_cfg["expected_reference_spacing"])
    if expected_reference_spacing <= 0.0:
        raise ValueError(
            "runtime.movement.v4a.test_only.expected_reference_spacing must be > 0, "
            f"got {expected_reference_spacing}"
        )
    if "reference_layout_mode" not in v4a_testonly_cfg:
        raise ValueError(
            "runtime.movement.v4a.test_only.reference_layout_mode must be provided when movement_model=v4a"
        )
    reference_layout_mode = _require_choice(
        "runtime.movement.v4a.test_only.reference_layout_mode",
        v4a_testonly_cfg["reference_layout_mode"],
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
    layout_mode: str = REFERENCE_LAYOUT_MODE_RECT_CENTERED_ROWS,
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
        last_fleet_cohesion=build_initial_cohesion_map(fleets.keys()),
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
    layout_mode: str = REFERENCE_LAYOUT_MODE_RECT_CENTERED_ROWS,
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
        last_fleet_cohesion=build_initial_cohesion_map(fleets.keys()),
    )


def prepare_active_scenario(base_dir: Path, *, settings_override: dict | None = None) -> dict:
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
    run_cfg = _build_run_cfg(get_run, get_runtime)
    movement_cfg = _build_movement_cfg(
        get_runtime,
        runtime_decision_source_effective=run_cfg["runtime_decision_source_effective"],
        test_mode=run_cfg["test_mode"],
    )
    boundary_cfg = _build_boundary_cfg(get_runtime)
    v4a_reference_cfg = _resolve_v4a_reference_cfg(
        settings,
        get_runtime,
        movement_model_effective=movement_cfg["model_effective"],
    )
    battle_restore_bridge_active = movement_cfg["model_effective"] == "v4a"
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
        "contact_hysteresis_h": float(get_runtime("contact_hysteresis_h", 0.1)),
        "fsr_strength": float(get_runtime("fsr_strength", 0.0)),
        "alpha_sep": float(get_runtime("alpha_sep", 0.6)),
        "hostile_contact_impedance_mode": _require_choice(
            "runtime.test_only.hostile_contact_impedance.active_mode",
            get_contact_model(("active_mode",), execution.HOSTILE_CONTACT_IMPEDANCE_MODE_DEFAULT),
            execution.HOSTILE_CONTACT_IMPEDANCE_MODE_LABELS,
        ),
        "hybrid_v2": {
            key: float(get_contact_model(("hybrid_v2", key), default))
            for key, default in {
                "radius_multiplier": execution.HOSTILE_CONTACT_IMPEDANCE_V2_RADIUS_MULTIPLIER_DEFAULT,
                "repulsion_max_disp_ratio": execution.HOSTILE_CONTACT_IMPEDANCE_V2_REPULSION_MAX_DISP_RATIO_DEFAULT,
                "forward_damping_strength": execution.HOSTILE_CONTACT_IMPEDANCE_V2_FORWARD_DAMPING_STRENGTH_DEFAULT,
            }.items()
        },
        "intent_unified_spacing_v1": {
            key: float(get_contact_model(("intent_unified_spacing_v1", key), default))
            for key, default in {
                "scale": execution.HOSTILE_INTENT_UNIFIED_SPACING_SCALE_DEFAULT,
                "strength": execution.HOSTILE_INTENT_UNIFIED_SPACING_STRENGTH_DEFAULT,
            }.items()
        },
    }
    contact_cfg["ch_enabled"] = contact_cfg["contact_hysteresis_h"] > 0.0
    contact_cfg["fsr_enabled"] = contact_cfg["fsr_strength"] > 0.0

    observer_cfg = {
        "bridge": {
            "theta_split": float(get_event_bridge("theta_split", execution.BRIDGE_THETA_SPLIT_DEFAULT)),
            "theta_env": float(get_event_bridge("theta_env", execution.BRIDGE_THETA_ENV_DEFAULT)),
            "sustain_ticks": int(get_event_bridge("sustain_ticks", execution.BRIDGE_SUSTAIN_TICKS_DEFAULT)),
        },
        "collapse_shadow": {
            key: cast(get_collapse_shadow(key, default))
            for key, (cast, default) in {
                "theta_conn_default": (float, execution.COLLAPSE_V2_SHADOW_THETA_CONN_DEFAULT),
                "theta_coh_default": (float, execution.COLLAPSE_V2_SHADOW_THETA_COH_DEFAULT),
                "theta_force_default": (float, execution.COLLAPSE_V2_SHADOW_THETA_FORCE_DEFAULT),
                "theta_attr_default": (float, execution.COLLAPSE_V2_SHADOW_THETA_ATTR_DEFAULT),
                "attrition_window": (int, execution.COLLAPSE_V2_SHADOW_ATTRITION_WINDOW_DEFAULT),
                "sustain_ticks": (int, execution.COLLAPSE_V2_SHADOW_SUSTAIN_TICKS_DEFAULT),
                "min_conditions": (int, execution.COLLAPSE_V2_SHADOW_MIN_CONDITIONS_DEFAULT),
            }.items()
        },
    }

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
        "decision_source": run_cfg["runtime_decision_source_effective"],
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
        "bridge": observer_cfg["bridge"],
        "collapse_shadow": observer_cfg["collapse_shadow"],
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
            "test_mode": run_cfg["test_mode"],
            "test_mode_name": run_cfg["test_mode_name"],
            "runtime_decision_source_requested": run_cfg["runtime_decision_source_requested"],
            "runtime_decision_source_effective": run_cfg["runtime_decision_source_effective"],
            "movement_model_effective": movement_cfg["model_effective"],
            "v4a_restore_strength_effective": float(movement_cfg["v4a_restore_strength_effective"]),
            "v4a_reference_surface_mode_effective": str(movement_cfg["v4a_reference_surface_mode_effective"]),
            "v4a_soft_morphology_relaxation_effective": float(
                movement_cfg["v4a_soft_morphology_relaxation_effective"]
            ),
            "battle_restore_bridge_active": bool(battle_restore_bridge_active),
            "expected_reference_spacing_effective": float(v4a_reference_cfg["expected_reference_spacing"]),
            "physical_min_spacing_effective": float(v4a_reference_cfg["physical_min_spacing"]),
            "reference_layout_mode_effective": str(v4a_reference_cfg["reference_layout_mode"]),
            "hostile_contact_impedance_mode": contact_cfg["hostile_contact_impedance_mode"],
            "animate": False,
            "observer_enabled": run_cfg["observer_enabled"],
            "export_battle_report": False,
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
    get_run = partial(settings_api.get_run_control_setting, settings)
    get_runtime = partial(settings_api.get_runtime_setting, settings)
    get_runtime_metatype = partial(settings_api.get_runtime_metatype_setting, settings)
    get_unit = partial(settings_api.get_unit_setting, settings)

    active_mode = _require_choice(
        "fixture.active_mode",
        get_fixture(("active_mode",), execution.FIXTURE_MODE_BATTLE),
        execution.FIXTURE_MODE_LABELS,
    )
    if active_mode != execution.FIXTURE_MODE_NEUTRAL_TRANSIT_V1:
        raise ValueError(
            "prepare_neutral_transit_fixture requires fixture.active_mode=neutral_transit_v1, "
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
        str(get_fixture((execution.FIXTURE_MODE_NEUTRAL_TRANSIT_V1, "fleet_archetype_id"), "default")),
        rng=archetype_rng,
    )
    fleet_params = to_personality_parameters(fleet_data)

    battlefield_cfg = common_context["battlefield_cfg"]
    default_origin_x = max(1.0, battlefield_cfg["arena_size"] * DEFAULT_SPAWN_MARGIN_RATIO)
    default_origin_y = battlefield_cfg["arena_size"] * 0.5
    origin_x, origin_y = (
        float(value)
        for value in get_fixture(
            (execution.FIXTURE_MODE_NEUTRAL_TRANSIT_V1, "origin_xy"),
            (default_origin_x, default_origin_y),
        )
    )
    objective_x, objective_y = (
        float(value)
        for value in get_fixture(
            (execution.FIXTURE_MODE_NEUTRAL_TRANSIT_V1, "objective_point_xy"),
            (battlefield_cfg["arena_size"] - default_origin_x, default_origin_y),
        )
    )
    fleet_size = int(get_fixture((execution.FIXTURE_MODE_NEUTRAL_TRANSIT_V1, "fleet_size"), 100))
    fleet_aspect_ratio = float(get_fixture((execution.FIXTURE_MODE_NEUTRAL_TRANSIT_V1, "aspect_ratio"), 4.0))
    stop_radius = float(get_fixture((execution.FIXTURE_MODE_NEUTRAL_TRANSIT_V1, "stop_radius"), 2.0))
    facing_angle_deg = float(get_fixture((execution.FIXTURE_MODE_NEUTRAL_TRANSIT_V1, "facing_angle_deg"), 0.0))

    if stop_radius < 0.0:
        raise ValueError(f"fixture.neutral_transit_v1.stop_radius must be >= 0, got {stop_radius}")

    run_cfg = _build_run_cfg(
        get_run,
        get_runtime,
        test_mode_name_override=execution.FIXTURE_MODE_NEUTRAL_TRANSIT_V1,
    )
    movement_cfg = _build_movement_cfg(
        get_runtime,
        runtime_decision_source_effective=run_cfg["runtime_decision_source_effective"],
        test_mode=run_cfg["test_mode"],
    )
    v4a_reference_cfg = _resolve_v4a_reference_cfg(
        settings,
        get_runtime,
        movement_model_effective=movement_cfg["model_effective"],
    )

    unit_cfg = _build_unit_cfg(get_unit, get_runtime)
    unit_spacing = float(v4a_reference_cfg["expected_reference_spacing"])
    if fleet_aspect_ratio <= 0.0 or unit_spacing <= 0.0:
        raise ValueError(
            "fixture.neutral_transit_v1.aspect_ratio and expected reference spacing must be > 0, "
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
            "active_mode": execution.FIXTURE_MODE_NEUTRAL_TRANSIT_V1,
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
        "decision_source": run_cfg["runtime_decision_source_effective"],
        "movement_model": movement_cfg["model_effective"],
        "movement": movement_cfg,
        "contact": {
            "attack_range": unit_cfg["attack_range"],
            "damage_per_tick": unit_cfg["damage_per_tick"],
            "fire_quality_alpha": 0.0,
            "contact_hysteresis_h": 0.0,
            "fsr_strength": 0.0,
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
            "fsr_enabled": False,
            "separation_radius": float(v4a_reference_cfg["physical_min_spacing"]),
        },
        "boundary": _build_boundary_cfg(get_runtime),
    }
    simulation_observer_cfg = {
        "enabled": run_cfg["observer_enabled"],
        "bridge": {
            "theta_split": execution.BRIDGE_THETA_SPLIT_DEFAULT,
            "theta_env": execution.BRIDGE_THETA_ENV_DEFAULT,
            "sustain_ticks": execution.BRIDGE_SUSTAIN_TICKS_DEFAULT,
        },
        "collapse_shadow": {
            "theta_conn_default": execution.COLLAPSE_V2_SHADOW_THETA_CONN_DEFAULT,
            "theta_coh_default": execution.COLLAPSE_V2_SHADOW_THETA_COH_DEFAULT,
            "theta_force_default": execution.COLLAPSE_V2_SHADOW_THETA_FORCE_DEFAULT,
            "theta_attr_default": execution.COLLAPSE_V2_SHADOW_THETA_ATTR_DEFAULT,
            "attrition_window": execution.COLLAPSE_V2_SHADOW_ATTRITION_WINDOW_DEFAULT,
            "sustain_ticks": execution.COLLAPSE_V2_SHADOW_SUSTAIN_TICKS_DEFAULT,
            "min_conditions": execution.COLLAPSE_V2_SHADOW_MIN_CONDITIONS_DEFAULT,
        },
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
            "test_mode": run_cfg["test_mode"],
            "test_mode_name": execution.FIXTURE_MODE_NEUTRAL_TRANSIT_V1,
            "runtime_decision_source_requested": run_cfg["runtime_decision_source_requested"],
            "runtime_decision_source_effective": run_cfg["runtime_decision_source_effective"],
            "movement_model_effective": movement_cfg["model_effective"],
            "v4a_restore_strength_effective": float(movement_cfg["v4a_restore_strength_effective"]),
            "v4a_reference_surface_mode_effective": str(movement_cfg["v4a_reference_surface_mode_effective"]),
            "v4a_soft_morphology_relaxation_effective": float(
                movement_cfg["v4a_soft_morphology_relaxation_effective"]
            ),
            "expected_reference_spacing_effective": float(v4a_reference_cfg["expected_reference_spacing"]),
            "physical_min_spacing_effective": float(v4a_reference_cfg["physical_min_spacing"]),
            "reference_layout_mode_effective": str(v4a_reference_cfg["reference_layout_mode"]),
            "hostile_contact_impedance_mode": simulation_runtime_cfg["contact"]["hostile_contact_impedance_mode"],
            "animate": False,
            "observer_enabled": run_cfg["observer_enabled"],
            "export_battle_report": False,
            "active_mode": execution.FIXTURE_MODE_NEUTRAL_TRANSIT_V1,
        },
    }
