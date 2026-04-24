import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MISSING = object()
DEFAULT_TEST_RUN_RUNTIME_SETTINGS_PATH = "test_run/test_run_v1_0.runtime.settings.json"
DEFAULT_TEST_RUN_TESTONLY_SETTINGS_PATH = "test_run/test_run_v1_0.testonly.settings.json"

# 1. Runtime-facing path maps used by the public accessor surface.
RUNTIME_SETTING_PATHS = {
    "movement_model": ("selectors", "movement_model"),
    "fire_angle_quality_alpha": ("physical", "fire_control", "fire_angle_quality_alpha"),
    "fire_optimal_range_ratio": ("physical", "fire_control", "fire_optimal_range_ratio"),
    "fire_cone_half_angle_deg": ("physical", "fire_control", "fire_cone_half_angle_deg"),
    "local_desire_turn_need_onset": ("physical", "local_desire", "turn_need_onset"),
    "local_desire_heading_bias_cap": ("physical", "local_desire", "heading_bias_cap"),
    "local_desire_speed_brake_strength": ("physical", "local_desire", "speed_brake_strength"),
    "local_desire_experimental_signal_read_realignment_enabled": (
        "physical",
        "local_desire",
        "experimental_signal_read_realignment_enabled",
    ),
    "signed_longitudinal_backpedal_enabled": (
        "physical",
        "locomotion",
        "experimental_signed_longitudinal_backpedal_enabled",
    ),
    "signed_longitudinal_backpedal_reverse_authority_scale": (
        "physical",
        "locomotion",
        "signed_longitudinal_backpedal_reverse_authority_scale",
    ),
    "contact_hysteresis_h": ("physical", "contact", "contact_hysteresis_h"),
    "boundary_enabled": ("physical", "boundary", "enabled"),
    "boundary_soft_strength": ("physical", "boundary", "soft_strength"),
    "boundary_hard_enabled": ("physical", "boundary", "hard_enabled"),
    "min_unit_spacing": ("physical", "movement_low_level", "min_unit_spacing"),
    "alpha_sep": ("physical", "movement_low_level", "alpha_sep"),
    "max_accel_per_tick": ("physical", "movement_low_level", "max_accel_per_tick"),
    "max_decel_per_tick": ("physical", "movement_low_level", "max_decel_per_tick"),
    "max_turn_deg_per_tick": ("physical", "movement_low_level", "max_turn_deg_per_tick"),
    "turn_speed_min_scale": ("physical", "movement_low_level", "turn_speed_min_scale"),
    "v4a_restore_strength": ("movement", "v4a", "restore", "strength"),
    "v4a_expected_reference_spacing": (
        "movement",
        "v4a",
        "reference",
        "expected_reference_spacing",
    ),
    "v4a_reference_layout_mode": ("movement", "v4a", "reference", "layout_mode"),
    "v4a_reference_surface_mode": ("movement", "v4a", "reference", "surface_mode"),
    "v4a_soft_morphology_relaxation": (
        "movement",
        "v4a",
        "reference",
        "soft_morphology_relaxation",
    ),
    "v4a_shape_vs_advance_strength": (
        "movement",
        "v4a",
        "transition",
        "shape_vs_advance_strength",
    ),
    "v4a_heading_relaxation": ("movement", "v4a", "transition", "heading_relaxation"),
    "v4a_battle_standoff_hold_band_ratio": (
        "movement",
        "v4a",
        "battle",
        "standoff_hold_band_ratio",
    ),
    "v4a_battle_target_front_strip_gap_bias": (
        "movement",
        "v4a",
        "battle",
        "target_front_strip_gap_bias",
    ),
    "v4a_battle_hold_weight_strength": (
        "movement",
        "v4a",
        "battle",
        "hold_weight_strength",
    ),
    "v4a_battle_relation_lead_ticks": (
        "movement",
        "v4a",
        "battle",
        "relation_lead_ticks",
    ),
    "v4a_battle_hold_relaxation": (
        "movement",
        "v4a",
        "battle",
        "hold_relaxation",
    ),
    "v4a_battle_approach_drive_relaxation": (
        "movement",
        "v4a",
        "battle",
        "approach_drive_relaxation",
    ),
    "v4a_battle_near_contact_internal_stability_blend": (
        "movement",
        "v4a",
        "battle",
        "near_contact_internal_stability_blend",
    ),
    "v4a_battle_near_contact_speed_relaxation": (
        "movement",
        "v4a",
        "battle",
        "near_contact_speed_relaxation",
    ),
    "engaged_speed_scale": ("movement", "v4a", "engagement", "engaged_speed_scale"),
    "attack_speed_lateral_scale": ("movement", "v4a", "engagement", "attack_speed_lateral_scale"),
    "attack_speed_backward_scale": ("movement", "v4a", "engagement", "attack_speed_backward_scale"),
}

OBSERVER_SETTING_PATHS = {
    "runtime": {
        "tick_timing_enabled": ("observer", "tick_timing_enabled"),
    },
}


# 2. Layered settings loading and fail-fast path resolution.
def load_json_file(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def merge_mapping_deep(base: dict, overlay: dict) -> dict:
    merged = dict(base)
    for key, overlay_value in overlay.items():
        base_value = merged.get(key)
        if isinstance(base_value, dict) and isinstance(overlay_value, dict):
            merged[key] = merge_mapping_deep(base_value, overlay_value)
        else:
            merged[key] = overlay_value
    return merged


def resolve_optional_json_path(configured_path: str, default_path: str) -> Path:
    raw = str(configured_path).strip()
    candidate = Path(raw if raw else default_path)
    if not candidate.is_absolute():
        candidate = (PROJECT_ROOT / candidate).resolve()
    return candidate


def load_layered_test_run_settings(base_dir: Path) -> dict:
    """Load base + required layer files without silent fallback."""
    base_settings_path = base_dir / "test_run_v1_0.settings.json"
    settings = load_json_file(base_settings_path)
    if not isinstance(settings, dict):
        raise TypeError(
            f"Base test_run settings file must contain a JSON object: {base_settings_path}"
        )
    layers_cfg = settings.get("settings_layers", {})
    if not isinstance(layers_cfg, dict):
        raise TypeError(
            f"'settings_layers' must be a JSON object in base test_run settings: {base_settings_path}"
        )
    runtime_layer_path = resolve_optional_json_path(
        str(layers_cfg.get("runtime_path", DEFAULT_TEST_RUN_RUNTIME_SETTINGS_PATH)),
        DEFAULT_TEST_RUN_RUNTIME_SETTINGS_PATH,
    )
    testonly_layer_path = resolve_optional_json_path(
        str(layers_cfg.get("testonly_path", DEFAULT_TEST_RUN_TESTONLY_SETTINGS_PATH)),
        DEFAULT_TEST_RUN_TESTONLY_SETTINGS_PATH,
    )
    for layer_name, layer_path in (
        ("runtime", runtime_layer_path),
        ("test-only", testonly_layer_path),
    ):
        if not layer_path.exists():
            raise FileNotFoundError(
                f"Required {layer_name} test_run settings layer not found: {layer_path}"
            )
        layer_data = load_json_file(layer_path)
        if not isinstance(layer_data, dict):
            raise TypeError(
                f"{layer_name.capitalize()} test_run settings layer must contain a JSON object: {layer_path}"
            )
        settings = merge_mapping_deep(settings, layer_data)
    return settings


# 3. Shared nested lookup helpers for the public accessors below.
def get_section_setting(settings: dict, section: str, key: str, default):
    section_data = settings.get(section, {})
    if isinstance(section_data, dict) and key in section_data:
        return section_data[key]
    return settings.get(key, default)


def get_nested_mapping_value(data: dict, path: tuple[str, ...], default=MISSING):
    current = data
    for part in path:
        if not isinstance(current, dict) or part not in current:
            return default
        current = current[part]
    return current


# 4. Public accessor surface for harness/scenario callers.
def get_visualization_setting(settings: dict, key: str, default):
    section = settings.get("visualization", {})
    if isinstance(section, dict) and key in section:
        return section[key]
    return default


def get_runtime_metatype_setting(settings: dict, key: str, default):
    runtime_section = settings.get("runtime", {})
    if isinstance(runtime_section, dict):
        nested_value = get_nested_mapping_value(runtime_section, ("metatype", key), MISSING)
        if nested_value is not MISSING:
            return nested_value
    return default


def get_runtime_setting(settings: dict, key: str, default):
    runtime_section = settings.get("runtime", {})
    if isinstance(runtime_section, dict):
        nested_path = RUNTIME_SETTING_PATHS.get(key)
        if nested_path is not None:
            nested_value = get_nested_mapping_value(runtime_section, nested_path, MISSING)
            if nested_value is not MISSING:
                return nested_value
    return get_section_setting(settings, "runtime", key, default)


def get_observer_setting(settings: dict, key: str, default):
    runtime_section = settings.get("runtime", {})
    if isinstance(runtime_section, dict):
        nested_path = OBSERVER_SETTING_PATHS["runtime"].get(key)
        if nested_path is not None:
            nested_value = get_nested_mapping_value(runtime_section, nested_path, MISSING)
            if nested_value is not MISSING:
                return nested_value
    return default


def get_fleet_setting(settings: dict, key: str, default):
    return get_section_setting(settings, "fleet", key, default)


def get_unit_setting(settings: dict, key: str, default):
    return get_section_setting(settings, "unit", key, default)


def get_battlefield_setting(settings: dict, key: str, default):
    if key == "min_unit_spacing":
        return get_runtime_setting(settings, "min_unit_spacing", default)
    return get_section_setting(settings, "battlefield", key, default)


def get_run_control_setting(settings: dict, key: str, default):
    section = settings.get("run_control", {})
    if isinstance(section, dict) and key in section:
        return section[key]
    return default


def get_fixture_setting(settings: dict, path: tuple[str, ...], default=MISSING):
    nested_value = get_nested_mapping_value(settings, ("fixture", *path), MISSING)
    if nested_value is not MISSING:
        return nested_value
    if default is MISSING:
        return None
    return default


def get_contact_test_setting(settings: dict, path: tuple[str, ...], default):
    runtime_section = settings.get("runtime", {})
    if isinstance(runtime_section, dict):
        nested_value = get_nested_mapping_value(
            runtime_section,
            ("physical", "contact", "hostile_contact_impedance", *path),
            MISSING,
        )
        if nested_value is not MISSING:
            return nested_value
    return default
