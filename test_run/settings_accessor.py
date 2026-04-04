import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MISSING = object()
DEFAULT_TEST_RUN_RUNTIME_SETTINGS_PATH = "test_run/test_run_v1_0.runtime.settings.json"
DEFAULT_TEST_RUN_TESTONLY_SETTINGS_PATH = "test_run/test_run_v1_0.testonly.settings.json"

RUNTIME_SETTING_PATHS = {
    "movement_model": ("selectors", "movement_model"),
    "cohesion_decision_source": ("selectors", "cohesion_decision_source"),
    "v3_connect_radius_multiplier": ("semantics", "collapse_signal", "v3_connect_radius_multiplier"),
    "v3_r_ref_radius_multiplier": ("semantics", "collapse_signal", "v3_r_ref_radius_multiplier"),
    "fire_quality_alpha": ("physical", "fire_control", "fire_quality_alpha"),
    "alpha_safe_max": ("physical", "fire_control", "alpha_safe_max"),
    "contact_hysteresis_h": ("physical", "contact_model", "contact_hysteresis_h"),
    "fsr_strength": ("physical", "contact_model", "fsr_strength"),
    "boundary_enabled": ("physical", "boundary", "enabled"),
    "boundary_soft_strength": ("physical", "boundary", "soft_strength"),
    "boundary_hard_enabled": ("physical", "boundary", "hard_enabled"),
    "min_unit_spacing": ("physical", "movement_low_level", "min_unit_spacing"),
    "alpha_sep": ("physical", "movement_low_level", "alpha_sep"),
    "v4a_reference_surface_mode": ("movement", "v4a", "reference_surface_mode"),
    "v4a_soft_morphology_relaxation": ("movement", "v4a", "soft_morphology_relaxation"),
    "v4a_shape_vs_advance_strength": ("movement", "v4a", "shape_vs_advance_strength"),
    "v4a_heading_relaxation": ("movement", "v4a", "heading_relaxation"),
    "v4a_battle_standoff_hold_band_ratio": (
        "movement",
        "v4a",
        "battle_standoff_hold_band_ratio",
    ),
    "v4a_battle_target_front_strip_gap_bias": (
        "movement",
        "v4a",
        "battle_target_front_strip_gap_bias",
    ),
    "v4a_battle_hold_weight_strength": (
        "movement",
        "v4a",
        "battle_hold_weight_strength",
    ),
    "v4a_battle_relation_lead_ticks": (
        "movement",
        "v4a",
        "battle_relation_lead_ticks",
    ),
    "v4a_engaged_speed_scale": ("movement", "v4a", "engaged_speed_scale"),
    "v4a_attack_speed_lateral_scale": ("movement", "v4a", "attack_speed_lateral_scale"),
    "v4a_attack_speed_backward_scale": ("movement", "v4a", "attack_speed_backward_scale"),
    "movement_v3a_experiment": ("movement", "v3a", "experiment"),
    "centroid_probe_scale": ("movement", "v3a", "centroid_probe_scale"),
    "pre_tl_target_substrate": ("movement", "v3a", "pre_tl_target_substrate"),
    "odw_posture_bias_enabled": ("movement", "v3a", "odw_posture_bias", "enabled"),
    "odw_posture_bias_k": ("movement", "v3a", "odw_posture_bias", "k"),
    "odw_posture_bias_clip_delta": ("movement", "v3a", "odw_posture_bias", "clip_delta"),
    "symmetric_movement_sync_enabled": ("movement", "v3a", "symmetric_movement_sync_enabled"),
    "continuous_fr_shaping_enabled": ("movement", "v3a", "continuous_fr_shaping", "enabled"),
    "continuous_fr_shaping_mode": ("movement", "v3a", "continuous_fr_shaping", "mode"),
    "continuous_fr_shaping_a": ("movement", "v3a", "continuous_fr_shaping", "a"),
    "continuous_fr_shaping_sigma": ("movement", "v3a", "continuous_fr_shaping", "sigma"),
    "continuous_fr_shaping_p": ("movement", "v3a", "continuous_fr_shaping", "p"),
    "continuous_fr_shaping_q": ("movement", "v3a", "continuous_fr_shaping", "q"),
    "continuous_fr_shaping_beta": ("movement", "v3a", "continuous_fr_shaping", "beta"),
    "continuous_fr_shaping_gamma": ("movement", "v3a", "continuous_fr_shaping", "gamma"),
}

OBSERVER_SETTING_PATHS = {
    "runtime": {
        "tick_timing_enabled": ("observer", "tick_timing_enabled"),
    },
    "event_bridge": {
        "theta_split": ("observer", "event_bridge", "theta_split"),
        "theta_env": ("observer", "event_bridge", "theta_env"),
        "sustain_ticks": ("observer", "event_bridge", "sustain_ticks"),
    },
    "collapse_shadow": {
        "theta_conn_default": ("observer", "collapse_shadow", "theta_conn_default"),
        "theta_coh_default": ("observer", "collapse_shadow", "theta_coh_default"),
        "theta_force_default": ("observer", "collapse_shadow", "theta_force_default"),
        "theta_attr_default": ("observer", "collapse_shadow", "theta_attr_default"),
        "attrition_window": ("observer", "collapse_shadow", "attrition_window"),
        "sustain_ticks": ("observer", "collapse_shadow", "sustain_ticks"),
        "min_conditions": ("observer", "collapse_shadow", "min_conditions"),
    },
    "report_inference": {
        "strategic_inflection_sustain_ticks": ("observer", "report_inference", "strategic_inflection_sustain_ticks"),
        "tactical_swing_sustain_ticks": ("observer", "report_inference", "tactical_swing_sustain_ticks"),
        "tactical_swing_min_amplitude": ("observer", "report_inference", "tactical_swing_min_amplitude"),
        "tactical_swing_min_gap_ticks": ("observer", "report_inference", "tactical_swing_min_gap_ticks"),
    },
}


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


def resolve_optional_json_path(base_dir: Path, configured_path: str, default_path: str) -> Path:
    raw = str(configured_path).strip()
    candidate = Path(raw if raw else default_path)
    if not candidate.is_absolute():
        candidate = (PROJECT_ROOT / candidate).resolve()
    return candidate


def load_layered_test_run_settings(base_dir: Path) -> dict:
    base_settings_path = base_dir / "test_run_v1_0.settings.json"
    settings = load_json_file(base_settings_path)
    if not isinstance(settings, dict):
        return {}
    layers_cfg = settings.get("settings_layers", {})
    if not isinstance(layers_cfg, dict):
        layers_cfg = {}
    runtime_layer_path = resolve_optional_json_path(
        base_dir,
        str(layers_cfg.get("runtime_path", DEFAULT_TEST_RUN_RUNTIME_SETTINGS_PATH)),
        DEFAULT_TEST_RUN_RUNTIME_SETTINGS_PATH,
    )
    testonly_layer_path = resolve_optional_json_path(
        base_dir,
        str(layers_cfg.get("testonly_path", DEFAULT_TEST_RUN_TESTONLY_SETTINGS_PATH)),
        DEFAULT_TEST_RUN_TESTONLY_SETTINGS_PATH,
    )
    for layer_path in (runtime_layer_path, testonly_layer_path):
        if not layer_path.exists():
            continue
        layer_data = load_json_file(layer_path)
        if not isinstance(layer_data, dict):
            continue
        settings = merge_mapping_deep(settings, layer_data)
    return settings


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


def get_visualization_setting(settings: dict, key: str, default):
    section = settings.get("visualization", {})
    if isinstance(section, dict) and key in section:
        return section[key]
    return default


def get_visualization_section(settings: dict) -> dict:
    section = settings.get("visualization", {})
    if isinstance(section, dict):
        return section
    return {}


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


def get_event_bridge_setting(settings: dict, key: str, default):
    runtime_section = settings.get("runtime", {})
    if isinstance(runtime_section, dict):
        nested_path = OBSERVER_SETTING_PATHS["event_bridge"].get(key)
        if nested_path is not None:
            nested_value = get_nested_mapping_value(runtime_section, nested_path, MISSING)
            if nested_value is not MISSING:
                return nested_value
    return default


def get_observer_setting(settings: dict, key: str, default):
    runtime_section = settings.get("runtime", {})
    if isinstance(runtime_section, dict):
        nested_path = OBSERVER_SETTING_PATHS["runtime"].get(key)
        if nested_path is not None:
            nested_value = get_nested_mapping_value(runtime_section, nested_path, MISSING)
            if nested_value is not MISSING:
                return nested_value
    return default


def get_collapse_shadow_setting(settings: dict, key: str, default):
    runtime_section = settings.get("runtime", {})
    if isinstance(runtime_section, dict):
        nested_path = OBSERVER_SETTING_PATHS["collapse_shadow"].get(key)
        if nested_path is not None:
            nested_value = get_nested_mapping_value(runtime_section, nested_path, MISSING)
            if nested_value is not MISSING:
                return nested_value
    return default


def get_report_inference_setting(settings: dict, key: str, default):
    runtime_section = settings.get("runtime", {})
    if isinstance(runtime_section, dict):
        nested_path = OBSERVER_SETTING_PATHS["report_inference"].get(key)
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


def get_contact_model_test_setting(settings: dict, path: tuple[str, ...], default):
    runtime_section = settings.get("runtime", {})
    if isinstance(runtime_section, dict):
        nested_value = get_nested_mapping_value(
            runtime_section,
            ("physical", "contact_model", "hostile_contact_impedance", *path),
            MISSING,
        )
        if nested_value is not MISSING:
            return nested_value
    return default
