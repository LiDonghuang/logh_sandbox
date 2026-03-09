import json
import math
import random
import sys
from dataclasses import replace
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from runtime_v0_1 import (
    PersonalityParameters,
    Vec2,
    UnitState,
    FleetState,
    BattleState,
    build_initial_cohesion_map,
    initialize_unit_orientations,
)
from runtime.engine_skeleton import EngineTickSkeleton
from test_run.battle_report_builder import build_battle_report_markdown, resolve_name_with_fallback


DEFAULT_DT = 1.0
DEFAULT_SPAWN_MARGIN_RATIO = 0.05
DEFAULT_FRAME_STRIDE = 1
DEFAULT_PLOT_COLORS = ("#1f77b4", "#ff7f0e")
DEFAULT_BATTLE_REPORT_TOPIC = "test_run_v1_0"
DEFAULT_BATTLE_REPORT_EXPORT_DIR = "analysis/exports/battle_reports"
DEFAULT_VIDEO_EXPORT_DIR = "analysis/exports/videos"
DEFAULT_VIDEO_EXPORT_TOPIC = "test_run_v1_0"
TEST_MODE_LABELS = {
    0: "default",
    1: "observe",
    2: "test",
}
PLOT_PROFILE_LABELS = {
    "auto": "auto",
    "baseline": "baseline",
    "extended": "extended",
}
COHESION_DECISION_SOURCE_LABELS = {
    "baseline": "baseline",
    "v2": "v2",
    "v3_test": "v3_test",
}
BASELINE_COHESION_DECISION_SOURCE = "v3_test"
BASELINE_V3_CONNECT_RADIUS_MULTIPLIER = 1.1
BASELINE_V3_R_REF_RADIUS_MULTIPLIER = 1.0
_MISSING = object()
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
    "movement_v3a_experiment": ("movement", "v3a", "experiment"),
    "centroid_probe_scale": ("movement", "v3a", "centroid_probe_scale"),
}
OBSERVER_SETTING_PATHS = {
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
DEFAULT_AVATAR_A = "avatar_09162"
DEFAULT_AVATAR_B = "avatar_09195"
ENDGAME_HP_RATIO_DEFAULT = 0.20
BRIDGE_THETA_SPLIT_DEFAULT = 1.715
BRIDGE_THETA_ENV_DEFAULT = 0.583
BRIDGE_SUSTAIN_TICKS_DEFAULT = 20
BRIDGE_EPSILON = 1e-9
COLLAPSE_V2_SHADOW_ATTRITION_WINDOW_DEFAULT = 20
COLLAPSE_V2_SHADOW_SUSTAIN_TICKS_DEFAULT = 10
COLLAPSE_V2_SHADOW_MIN_CONDITIONS_DEFAULT = 2
COLLAPSE_V2_SHADOW_THETA_CONN_DEFAULT = 0.10
COLLAPSE_V2_SHADOW_THETA_COH_DEFAULT = 0.98
COLLAPSE_V2_SHADOW_THETA_FORCE_DEFAULT = 0.95
COLLAPSE_V2_SHADOW_THETA_ATTR_DEFAULT = 0.10
STRATEGIC_INFLECTION_SUSTAIN_TICKS = 12
TACTICAL_SWING_SUSTAIN_TICKS = 8
TACTICAL_SWING_MIN_AMPLITUDE = 2.0
TACTICAL_SWING_MIN_GAP_TICKS = 10
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


def load_json_file(path: Path) -> dict:
    # utf-8-sig is compatible with both BOM and non-BOM UTF-8 JSON files.
    return json.loads(path.read_text(encoding="utf-8-sig"))


def resolve_optional_json_path(base_dir: Path, configured_path: str, default_path: str) -> Path:
    raw = str(configured_path).strip()
    candidate = Path(raw if raw else default_path)
    if not candidate.is_absolute():
        candidate = (PROJECT_ROOT / candidate).resolve()
    return candidate


def load_metatype_settings(base_dir: Path, settings: dict) -> dict:
    configured_path = str(
        get_run_control_setting(settings, "metatype_settings_path", DEFAULT_METATYPE_SETTINGS_PATH)
    )
    metatype_path = resolve_optional_json_path(base_dir, configured_path, DEFAULT_METATYPE_SETTINGS_PATH)
    if not metatype_path.exists():
        return {}
    data = load_json_file(metatype_path)
    if isinstance(data, dict):
        return data
    return {}


class TestModeEngineTickSkeleton(EngineTickSkeleton):
    def _compute_cohesion_v2_geometry(self, state: BattleState, fleet_id: str) -> tuple[float, dict]:
        eps = 1e-12
        fleet = state.fleets.get(fleet_id)
        if fleet is None:
            return 1.0, {
                "n_alive": 0,
                "centroid_x": 0.0,
                "centroid_y": 0.0,
                "fragmentation": 0.0,
                "dispersion": 0.0,
                "outlier_mass": 0.0,
                "elongation": 0.0,
                "exploitability": 0.0,
                "cohesion_v2": 1.0,
                "lcc_ratio": 1.0,
                "dispersion_ratio_q90_q50": 1.0,
                "outlier_count": 0,
                "outlier_threshold": 0.0,
                "q50_radius": 0.0,
                "q90_radius": 0.0,
                "connect_radius_effective": 0.0,
                "connect_radius_multiplier": 1.0,
            }

        alive_positions = []
        for unit_id in fleet.unit_ids:
            unit = state.units.get(unit_id)
            if unit is None or unit.hit_points <= 0.0:
                continue
            alive_positions.append((unit.position.x, unit.position.y))
        n_alive = len(alive_positions)

        v2_connect_multiplier = float(getattr(self, "V2_CONNECT_RADIUS_MULTIPLIER", 1.0))
        if v2_connect_multiplier <= 0.0:
            v2_connect_multiplier = 1.0

        if n_alive == 0:
            return 0.0, {
                "n_alive": 0,
                "centroid_x": 0.0,
                "centroid_y": 0.0,
                "fragmentation": 1.0,
                "dispersion": 0.0,
                "outlier_mass": 0.0,
                "elongation": 0.0,
                "exploitability": 1.0,
                "cohesion_v2": 0.0,
                "lcc_ratio": 0.0,
                "dispersion_ratio_q90_q50": 1.0,
                "outlier_count": 0,
                "outlier_threshold": 0.0,
                "q50_radius": 0.0,
                "q90_radius": 0.0,
                "connect_radius_effective": float(self.separation_radius) * v2_connect_multiplier,
                "connect_radius_multiplier": v2_connect_multiplier,
            }

        sum_x = 0.0
        sum_y = 0.0
        for x, y in alive_positions:
            sum_x += x
            sum_y += y
        centroid_x = sum_x / n_alive
        centroid_y = sum_y / n_alive

        radii = []
        cov_xx = 0.0
        cov_xy = 0.0
        cov_yy = 0.0
        for x, y in alive_positions:
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
        q25 = self._quantile_sorted(sorted_radii, 0.25)
        q50 = self._quantile_sorted(sorted_radii, 0.50)
        q75 = self._quantile_sorted(sorted_radii, 0.75)
        q90 = self._quantile_sorted(sorted_radii, 0.90)
        iqr = q75 - q25
        if iqr < 0.0:
            iqr = 0.0

        if q90 <= eps and q50 <= eps:
            dispersion_ratio = 1.0
            f_disp = 0.0
        else:
            dispersion_ratio = q90 / (q50 + eps)
            if dispersion_ratio < 1.0:
                dispersion_ratio = 1.0
            f_disp = 1.0 - (1.0 / dispersion_ratio)
            f_disp = self._clamp01(f_disp)

        outlier_threshold = q75 + (1.5 * iqr)
        outlier_count = 0
        for r in radii:
            if r > outlier_threshold:
                outlier_count += 1
        f_out = self._clamp01(outlier_count / n_alive)

        trace = cov_xx + cov_yy
        det = (cov_xx * cov_yy) - (cov_xy * cov_xy)
        disc = (trace * trace) - (4.0 * det)
        if disc < 0.0:
            disc = 0.0
        sqrt_disc = math.sqrt(disc)
        lambda_1 = 0.5 * (trace + sqrt_disc)
        lambda_2 = 0.5 * (trace - sqrt_disc)
        if lambda_1 < eps:
            f_elong = 0.0
        else:
            f_elong = 1.0 - (lambda_2 / (lambda_1 + eps))
            f_elong = self._clamp01(f_elong)

        if n_alive == 1:
            lcc_ratio = 1.0
            connect_radius_effective = float(self.separation_radius) * v2_connect_multiplier
        else:
            connect_radius = float(self.separation_radius) * v2_connect_multiplier
            if connect_radius < eps:
                connect_radius = eps
            connect_radius_effective = connect_radius
            connect_radius_sq = connect_radius * connect_radius
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
                    nx, ny = alive_positions[node]
                    for j in range(n_alive):
                        if visited[j] or j == node:
                            continue
                        px, py = alive_positions[j]
                        ddx = nx - px
                        ddy = ny - py
                        if (ddx * ddx) + (ddy * ddy) <= connect_radius_sq:
                            visited[j] = True
                            stack.append(j)
                if component_size > largest_component_size:
                    largest_component_size = component_size
            lcc_ratio = largest_component_size / n_alive
        f_frag = self._clamp01(1.0 - lcc_ratio)

        exploitability = 1.0 - (
            (1.0 - f_frag)
            * (1.0 - f_disp)
            * (1.0 - f_out)
            * (1.0 - f_elong)
        )
        cohesion_v2 = self._clamp01(1.0 - exploitability)

        return cohesion_v2, {
            "n_alive": n_alive,
            "centroid_x": centroid_x,
            "centroid_y": centroid_y,
            "fragmentation": f_frag,
            "dispersion": f_disp,
            "outlier_mass": f_out,
            "elongation": f_elong,
            "exploitability": exploitability,
            "cohesion_v2": cohesion_v2,
            "lcc_ratio": lcc_ratio,
            "dispersion_ratio_q90_q50": dispersion_ratio,
            "outlier_count": outlier_count,
            "outlier_threshold": outlier_threshold,
            "q50_radius": q50,
            "q90_radius": q90,
            "connect_radius_effective": connect_radius_effective,
            "connect_radius_multiplier": v2_connect_multiplier,
        }

    def _compute_cohesion_v3_shadow_geometry(self, state: BattleState, fleet_id: str) -> tuple[float, dict]:
        eps = 1e-12
        rho_low = 0.35
        rho_high = 1.15
        penalty_k = 6.0

        fleet = state.fleets.get(fleet_id)
        if fleet is None:
            return 1.0, {
                "n_alive": 0,
                "lcc": 0,
                "c_conn": 1.0,
                "centroid_x": 0.0,
                "centroid_y": 0.0,
                "r": 0.0,
                "r_ref": 0.0,
                "rho": 0.0,
                "c_scale": 1.0,
                "c_v3": 1.0,
                "rho_low": rho_low,
                "rho_high": rho_high,
                "k": penalty_k,
                "connect_radius_effective": 0.0,
                "connect_radius_multiplier": 1.0,
                "r_ref_multiplier": 1.0,
            }

        alive_positions = []
        for unit_id in fleet.unit_ids:
            unit = state.units.get(unit_id)
            if unit is None or unit.hit_points <= 0.0:
                continue
            alive_positions.append((unit.position.x, unit.position.y))
        n_alive = len(alive_positions)

        v3_connect_multiplier = float(getattr(self, "V3_CONNECT_RADIUS_MULTIPLIER", 1.0))
        if v3_connect_multiplier <= 0.0:
            v3_connect_multiplier = 1.0
        v3_r_ref_multiplier = float(getattr(self, "V3_R_REF_RADIUS_MULTIPLIER", 1.0))
        if v3_r_ref_multiplier <= 0.0:
            v3_r_ref_multiplier = 1.0

        if n_alive == 0:
            return 0.0, {
                "n_alive": 0,
                "lcc": 0,
                "c_conn": 0.0,
                "centroid_x": 0.0,
                "centroid_y": 0.0,
                "r": 0.0,
                "r_ref": 0.0,
                "rho": 0.0,
                "c_scale": 1.0,
                "c_v3": 0.0,
                "rho_low": rho_low,
                "rho_high": rho_high,
                "k": penalty_k,
                "connect_radius_effective": float(self.separation_radius) * v3_connect_multiplier,
                "connect_radius_multiplier": v3_connect_multiplier,
                "r_ref_multiplier": v3_r_ref_multiplier,
            }

        sum_x = 0.0
        sum_y = 0.0
        for x, y in alive_positions:
            sum_x += x
            sum_y += y
        centroid_x = sum_x / n_alive
        centroid_y = sum_y / n_alive

        radius_sq_sum = 0.0
        for x, y in alive_positions:
            dx = x - centroid_x
            dy = y - centroid_y
            radius_sq_sum += (dx * dx) + (dy * dy)
        r = math.sqrt(radius_sq_sum / n_alive)
        r_ref = float(self.separation_radius) * v3_r_ref_multiplier * math.sqrt(float(n_alive))
        if r_ref <= eps:
            rho = 0.0
        else:
            rho = r / r_ref

        if rho < rho_low:
            c_scale = math.exp(-penalty_k * ((rho_low - rho) ** 2))
        elif rho <= rho_high:
            c_scale = 1.0
        else:
            c_scale = math.exp(-penalty_k * ((rho - rho_high) ** 2))

        if n_alive == 1:
            lcc = 1
            c_conn = 1.0
            connect_radius_effective = float(self.separation_radius) * v3_connect_multiplier
        else:
            connect_radius = float(self.separation_radius) * v3_connect_multiplier
            if connect_radius < eps:
                connect_radius = eps
            connect_radius_effective = connect_radius
            connect_radius_sq = connect_radius * connect_radius
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
                    nx, ny = alive_positions[node]
                    for j in range(n_alive):
                        if visited[j] or j == node:
                            continue
                        px, py = alive_positions[j]
                        ddx = nx - px
                        ddy = ny - py
                        if (ddx * ddx) + (ddy * ddy) <= connect_radius_sq:
                            visited[j] = True
                            stack.append(j)
                if component_size > largest_component_size:
                    largest_component_size = component_size
            lcc = largest_component_size
            c_conn = largest_component_size / n_alive

        c_v3 = self._clamp01(c_conn * c_scale)
        return c_v3, {
            "n_alive": n_alive,
            "lcc": lcc,
            "c_conn": c_conn,
            "centroid_x": centroid_x,
            "centroid_y": centroid_y,
            "r": r,
            "r_ref": r_ref,
            "rho": rho,
            "c_scale": c_scale,
            "c_v3": c_v3,
            "rho_low": rho_low,
            "rho_high": rho_high,
            "k": penalty_k,
            "connect_radius_effective": connect_radius_effective,
            "connect_radius_multiplier": v3_connect_multiplier,
            "r_ref_multiplier": v3_r_ref_multiplier,
        }

    def evaluate_cohesion(self, state: BattleState) -> BattleState:
        next_state = super().evaluate_cohesion(state)
        decision_source = str(getattr(self, "COHESION_DECISION_SOURCE", "v2")).lower()
        if decision_source != "v3_test":
            return next_state
        shadow_v3 = getattr(self, "debug_last_cohesion_v3", {})
        if not isinstance(shadow_v3, dict) or not shadow_v3:
            return next_state
        # Isolation guarantee: only substitute runtime cohesion signal.
        runtime_cohesion = {}
        for fleet_id in next_state.fleets:
            runtime_cohesion[fleet_id] = float(
                shadow_v3.get(fleet_id, next_state.last_fleet_cohesion.get(fleet_id, 1.0))
            )
        return replace(next_state, last_fleet_cohesion=runtime_cohesion)


def resolve_archetype(archetypes: dict, archetype_ref: str):
    if archetype_ref == "default":
        return {
            "name": "default",
            "disp_name_EN": "Default",
            "disp_name_ZH": "默认",
            "full_name_EN": "Default Archetype",
            "full_name_ZH": "默认原型",
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
            template_cfg.get("avatar", archetype_template.get("avatar", "avatar_09154"))
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


def extract_runtime_debug_payload(diag_tick: dict) -> dict:
    if not isinstance(diag_tick, dict):
        return {}
    outliers = diag_tick.get("outliers", {})
    if not isinstance(outliers, dict):
        outliers = {}
    projection = diag_tick.get("projection", {})
    if not isinstance(projection, dict):
        projection = {}
    combat = diag_tick.get("combat", {})
    if not isinstance(combat, dict):
        combat = {}
    boundary_soft = diag_tick.get("boundary_soft", {})
    if not isinstance(boundary_soft, dict):
        boundary_soft = {}
    persistent_ids = diag_tick.get("persistent_outlier_unit_ids", [])
    if not isinstance(persistent_ids, list):
        persistent_ids = []

    payload = {
        "tick": int(diag_tick.get("tick", 0)),
        "outlier_total": 0,
        "persistent_outlier_total": int(len(persistent_ids)),
        "max_outlier_persistence": int(diag_tick.get("max_outlier_persistence", 0)),
        "projection_max_displacement": float(projection.get("max_projection_displacement", 0.0)),
        "projection_mean_displacement": float(projection.get("mean_projection_displacement", 0.0)),
        "projection_pairs_count": int(projection.get("projection_pairs_count", 0)),
        "in_contact_count": int(combat.get("in_contact_count", 0)),
        "damage_events_count": int(combat.get("damage_events_count", 0)),
        "boundary_force_events_tick": int(boundary_soft.get("boundary_force_events_count_tick", 0)),
        "fleets": {},
    }

    for fleet_id in ("A", "B"):
        fleet_payload = outliers.get(fleet_id, {})
        if not isinstance(fleet_payload, dict):
            fleet_payload = {}
        outlier_count = int(fleet_payload.get("outlier_count", 0))
        payload["outlier_total"] += outlier_count
        payload["fleets"][fleet_id] = {
            "outlier_count": outlier_count,
            "max_outlier_persistence": int(fleet_payload.get("max_outlier_persistence", 0)),
            "r_rms": float(fleet_payload.get("r_rms", 0.0)),
            "outlier_threshold": float(fleet_payload.get("outlier_threshold", 0.0)),
        }
    return payload


def to_plot_color(data: dict, fallback: str) -> str:
    code = str(data.get("color_code", "")).strip()
    if not code:
        code = fallback
    if code.startswith("#"):
        return code
    return f"#{code}"


def resolve_display_name(data: dict, language: str) -> str:
    if language == "ZH":
        value = data.get("disp_name_ZH")
    else:
        value = data.get("disp_name_EN")
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


def get_section_setting(settings: dict, section: str, key: str, default):
    section_data = settings.get(section, {})
    if isinstance(section_data, dict) and key in section_data:
        return section_data[key]
    return settings.get(key, default)


def get_nested_mapping_value(data: dict, path: tuple[str, ...], default=_MISSING):
    current = data
    for part in path:
        if not isinstance(current, dict) or part not in current:
            return default
        current = current[part]
    return current


def get_visualization_setting(settings: dict, key: str, default):
    return get_section_setting(settings, "visualization", key, default)


def get_visualization_section(settings: dict) -> dict:
    section = settings.get("visualization", {})
    if isinstance(section, dict):
        return section
    return {}


def get_runtime_setting(settings: dict, key: str, default):
    runtime_section = settings.get("runtime", {})
    if isinstance(runtime_section, dict):
        nested_path = RUNTIME_SETTING_PATHS.get(key)
        if nested_path is not None:
            nested_value = get_nested_mapping_value(runtime_section, nested_path, _MISSING)
            if nested_value is not _MISSING:
                return nested_value
    return get_section_setting(settings, "runtime", key, default)


def get_event_bridge_setting(settings: dict, key: str, default):
    runtime_section = settings.get("runtime", {})
    if isinstance(runtime_section, dict):
        nested_path = OBSERVER_SETTING_PATHS["event_bridge"].get(key)
        if nested_path is not None:
            nested_value = get_nested_mapping_value(runtime_section, nested_path, _MISSING)
            if nested_value is not _MISSING:
                return nested_value
    return default


def get_collapse_shadow_setting(settings: dict, key: str, default):
    runtime_section = settings.get("runtime", {})
    if isinstance(runtime_section, dict):
        nested_path = OBSERVER_SETTING_PATHS["collapse_shadow"].get(key)
        if nested_path is not None:
            nested_value = get_nested_mapping_value(runtime_section, nested_path, _MISSING)
            if nested_value is not _MISSING:
                return nested_value
    return default


def get_report_inference_setting(settings: dict, key: str, default):
    runtime_section = settings.get("runtime", {})
    if isinstance(runtime_section, dict):
        nested_path = OBSERVER_SETTING_PATHS["report_inference"].get(key)
        if nested_path is not None:
            nested_value = get_nested_mapping_value(runtime_section, nested_path, _MISSING)
            if nested_value is not _MISSING:
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
    return get_section_setting(settings, "run_control", key, default)


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


def resolve_plot_profile(
    raw_value,
    test_mode: int,
    cohesion_decision_source_requested: str,
    cohesion_decision_source_effective: str,
) -> tuple[str, str]:
    requested = str(raw_value).strip().lower()
    if requested not in PLOT_PROFILE_LABELS:
        requested = "auto"
    requested_cohesion = str(cohesion_decision_source_requested).strip().lower()
    effective_cohesion = str(cohesion_decision_source_effective).strip().lower()
    v3_plot_permitted = effective_cohesion == "v3_test"
    if requested == "auto":
        effective = "extended" if v3_plot_permitted else "baseline"
    elif requested == "extended" and not v3_plot_permitted:
        effective = "baseline"
    else:
        effective = requested
    if requested == "extended" and effective != "extended":
        print(
            f"[mode] plot_profile={requested} requested but test_mode={test_mode} with cohesion_decision_source={requested_cohesion} only permits baseline plots; remapping to baseline"
        )
    return requested, effective


def resolve_runtime_decision_source(raw_value, test_mode: int) -> tuple[str, str]:
    requested = str(raw_value).strip().lower()
    if requested not in COHESION_DECISION_SOURCE_LABELS:
        requested = "baseline"
    baseline_source = BASELINE_COHESION_DECISION_SOURCE
    if requested == "baseline":
        effective = baseline_source
    else:
        effective = requested
    if int(test_mode) < 2 and effective != baseline_source:
        print(
            f"[mode] cohesion_decision_source={requested} requested but test_mode={test_mode} only permits baseline runtime; remapping to {baseline_source}"
        )
        effective = baseline_source
    return requested, effective


def resolve_movement_model(raw_value) -> tuple[str, str]:
    requested = str(raw_value).strip().lower()
    if requested not in {"baseline", "v1", "v3a"}:
        requested = "baseline"
    baseline_model = "v3a"
    if requested == "baseline":
        effective = baseline_model
    elif requested == "v1":
        print("[mode] movement_model=v1 requested in standard test run; remapping to v3a after baseline activation")
        effective = baseline_model
    else:
        effective = requested
    return requested, effective


def clamp(v: float, lo: float, hi: float) -> float:
    if v < lo:
        return lo
    if v > hi:
        return hi
    return v


def resolve_effective_seed(seed_value: int) -> int:
    if seed_value < 0:
        return random.SystemRandom().randrange(0, 2**32)
    return seed_value


def resolve_timestamped_video_output_path(raw_output_path: str, base_dir: Path) -> Path:
    candidate = Path(str(raw_output_path).strip()) if str(raw_output_path).strip() else Path(DEFAULT_VIDEO_EXPORT_DIR)
    if not candidate.is_absolute():
        candidate = (base_dir.parent / candidate).resolve()
    if candidate.suffix:
        target_dir = candidate.parent
        base_stem = candidate.stem or DEFAULT_VIDEO_EXPORT_TOPIC
        suffix = candidate.suffix
    else:
        target_dir = candidate
        base_stem = DEFAULT_VIDEO_EXPORT_TOPIC
        suffix = ".mp4"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return (target_dir / f"{base_stem}_{timestamp}{suffix}").resolve()


def _mean_xy(points: list[tuple[float, float]]) -> tuple[float, float]:
    if not points:
        return (0.0, 0.0)
    sx = 0.0
    sy = 0.0
    for x, y in points:
        sx += float(x)
        sy += float(y)
    n = float(len(points))
    return (sx / n, sy / n)


def _std_population(values: list[float]) -> float:
    if not values:
        return 0.0
    n = float(len(values))
    mean_v = sum(values) / n
    var = sum((float(v) - mean_v) ** 2 for v in values) / n
    return math.sqrt(max(0.0, var))


def _deterministic_kmeans_1d(values: list[float], max_iters: int = 32) -> tuple[list[float], list[float]]:
    if len(values) <= 1:
        return (list(values), [])
    c1 = min(values)
    c2 = max(values)
    if abs(c2 - c1) <= BRIDGE_EPSILON:
        ordered = sorted(values)
        mid = max(1, len(ordered) // 2)
        return (ordered[:mid], ordered[mid:])
    group1: list[float] = []
    group2: list[float] = []
    for _ in range(max_iters):
        group1 = []
        group2 = []
        for v in values:
            d1 = abs(v - c1)
            d2 = abs(v - c2)
            if d1 <= d2:
                group1.append(float(v))
            else:
                group2.append(float(v))
        if not group1 or not group2:
            ordered = sorted(values)
            mid = max(1, len(ordered) // 2)
            return (ordered[:mid], ordered[mid:])
        new_c1 = sum(group1) / float(len(group1))
        new_c2 = sum(group2) / float(len(group2))
        if abs(new_c1 - c1) <= BRIDGE_EPSILON and abs(new_c2 - c2) <= BRIDGE_EPSILON:
            break
        c1 = new_c1
        c2 = new_c2
    return (group1, group2)


def compute_formation_snapshot_metrics(
    side_points: list[tuple[float, float]],
    enemy_points: list[tuple[float, float]],
    angle_bins: int = 12,
) -> dict:
    result = {
        "AR": 1.0,
        "AR_forward": 1.0,
        "AreaScale": 0.0,
        "orientation_theta": 0.0,
        "major_axis_alignment": 0.0,
        "split_separation": 0.0,
        "angle_coverage": 0.0,
        "wedge_ratio": 1.0,
        "centroid_x": 0.0,
        "centroid_y": 0.0,
    }
    if not side_points:
        return result
    cx, cy = _mean_xy(side_points)
    result["centroid_x"] = cx
    result["centroid_y"] = cy

    if len(side_points) == 1:
        if enemy_points:
            ex, ey = _mean_xy(enemy_points)
            angle = math.atan2(side_points[0][1] - ey, side_points[0][0] - ex)
            if angle < 0.0:
                angle += 2.0 * math.pi
            if angle_bins > 0:
                result["angle_coverage"] = 1.0 / float(angle_bins)
        return result

    n = float(len(side_points))
    var_x = 0.0
    var_y = 0.0
    cov_xy = 0.0
    for x, y in side_points:
        dx = float(x) - cx
        dy = float(y) - cy
        var_x += dx * dx
        var_y += dy * dy
        cov_xy += dx * dy
    var_x /= n
    var_y /= n
    cov_xy /= n

    trace = var_x + var_y
    delta_sq = (var_x - var_y) ** 2 + 4.0 * (cov_xy ** 2)
    delta = math.sqrt(max(0.0, delta_sq))
    lam1 = max(0.0, 0.5 * (trace + delta))
    lam2 = max(0.0, 0.5 * (trace - delta))

    if abs(cov_xy) > BRIDGE_EPSILON or abs(lam1 - var_y) > BRIDGE_EPSILON:
        evx = lam1 - var_y
        evy = cov_xy
    else:
        evx = 1.0
        evy = 0.0
    norm = math.sqrt(evx * evx + evy * evy)
    if norm <= BRIDGE_EPSILON:
        ux = 1.0
        uy = 0.0
    else:
        ux = evx / norm
        uy = evy / norm
    vx = -uy
    vy = ux

    sigma1 = math.sqrt(lam1)
    sigma2 = math.sqrt(lam2)
    result["AR"] = sigma1 / (sigma2 + BRIDGE_EPSILON)
    result["AreaScale"] = sigma1 * sigma2
    result["orientation_theta"] = math.atan2(uy, ux)

    u_values: list[float] = []
    v_values: list[float] = []
    for x, y in side_points:
        dx = float(x) - cx
        dy = float(y) - cy
        u = (dx * ux) + (dy * uy)
        v = (dx * vx) + (dy * vy)
        u_values.append(float(u))
        v_values.append(float(v))

    g1, g2 = _deterministic_kmeans_1d(u_values)
    if g1 and g2:
        mean1 = sum(g1) / float(len(g1))
        mean2 = sum(g2) / float(len(g2))
        std_u = _std_population(u_values)
        result["split_separation"] = abs(mean1 - mean2) / (std_u + BRIDGE_EPSILON)

    if enemy_points and angle_bins > 0:
        ex, ey = _mean_xy(enemy_points)
        occupied_bins = set()
        full_circle = 2.0 * math.pi
        for x, y in side_points:
            phi = math.atan2(float(y) - ey, float(x) - ex)
            if phi < 0.0:
                phi += full_circle
            idx = int((phi / full_circle) * angle_bins)
            if idx >= angle_bins:
                idx = angle_bins - 1
            if idx < 0:
                idx = 0
            occupied_bins.add(idx)
        result["angle_coverage"] = float(len(occupied_bins)) / float(angle_bins)

    if enemy_points:
        ex, ey = _mean_xy(enemy_points)
        fx = ex - cx
        fy = ey - cy
        f_norm = math.sqrt((fx * fx) + (fy * fy))
        if f_norm > BRIDGE_EPSILON:
            fx /= f_norm
            fy /= f_norm
            lx = -fy
            ly = fx
            forward_values: list[float] = []
            lateral_values: list[float] = []
            for x, y in side_points:
                dx = float(x) - cx
                dy = float(y) - cy
                forward_values.append((dx * fx) + (dy * fy))
                lateral_values.append((dx * lx) + (dy * ly))
            sigma_forward = _std_population(forward_values)
            sigma_lateral = _std_population(lateral_values)
            result["AR_forward"] = sigma_forward / (sigma_lateral + BRIDGE_EPSILON)
            result["major_axis_alignment"] = abs((ux * fx) + (uy * fy))

    n_units = len(u_values)
    if n_units > 0:
        group_size = max(1, int(math.ceil(0.3 * float(n_units))))
        sorted_indices = sorted(range(n_units), key=lambda i: u_values[i])
        rear_indices = sorted_indices[:group_size]
        front_indices = sorted_indices[-group_size:]
        v_rear = [v_values[i] for i in rear_indices]
        v_front = [v_values[i] for i in front_indices]
        width_front = _std_population(v_front)
        width_back = _std_population(v_rear)
        result["wedge_ratio"] = width_front / (width_back + BRIDGE_EPSILON)

    return result


def compute_bridge_metrics_per_side(state: BattleState) -> dict:
    positions_by_fleet: dict[str, list[tuple[float, float]]] = {}
    for fleet_id, fleet in state.fleets.items():
        side_points: list[tuple[float, float]] = []
        for unit_id in fleet.unit_ids:
            unit = state.units.get(unit_id)
            if unit is None:
                continue
            side_points.append((float(unit.position.x), float(unit.position.y)))
        positions_by_fleet[str(fleet_id)] = side_points

    metrics_by_fleet: dict[str, dict] = {}
    for fleet_id in state.fleets:
        enemy_points: list[tuple[float, float]] = []
        for other_id, points in positions_by_fleet.items():
            if other_id != fleet_id:
                enemy_points.extend(points)
        metrics_by_fleet[fleet_id] = compute_formation_snapshot_metrics(
            side_points=positions_by_fleet.get(fleet_id, []),
            enemy_points=enemy_points,
            angle_bins=12,
        )
    return metrics_by_fleet


def _quantile(sorted_values: list[float], q: float) -> float:
    if not sorted_values:
        return float("nan")
    if len(sorted_values) == 1:
        return float(sorted_values[0])
    if q <= 0.0:
        return float(sorted_values[0])
    if q >= 1.0:
        return float(sorted_values[-1])
    pos = (len(sorted_values) - 1) * q
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return float(sorted_values[lo])
    w = pos - lo
    return float(sorted_values[lo] * (1.0 - w) + sorted_values[hi] * w)


def _safe_float_or_nan(value) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float("nan")


def compute_collapse_v2_shadow_telemetry(
    *,
    observer_enabled: bool,
    observer_telemetry: dict,
    alive_trajectory: dict,
    theta_conn_default: float,
    theta_coh_default: float,
    theta_force_default: float,
    theta_attr_default: float,
    attrition_window: int,
    sustain_ticks: int,
    min_conditions: int,
) -> dict:
    sides = ("A", "B")
    n_ticks = max(
        len(alive_trajectory.get("A", [])) if isinstance(alive_trajectory.get("A", []), (list, tuple)) else 0,
        len(alive_trajectory.get("B", [])) if isinstance(alive_trajectory.get("B", []), (list, tuple)) else 0,
    )
    ticks = list(range(1, n_ticks + 1))
    out = {
        "tick": ticks,
        "thresholds": {
            "A": {
                "theta_conn": float(theta_conn_default),
                "theta_coh": float(theta_coh_default),
                "theta_force": float(theta_force_default),
                "theta_attr": float(theta_attr_default),
            },
            "B": {
                "theta_conn": float(theta_conn_default),
                "theta_coh": float(theta_coh_default),
                "theta_force": float(theta_force_default),
                "theta_attr": float(theta_attr_default),
            },
        },
        "pressure_v2_shadow": {side: [] for side in sides},
        "collapse_v2_shadow": {side: [] for side in sides},
        "pressure_sustain_counter": {side: [] for side in sides},
        "C_conn_signal": {side: [] for side in sides},
        "C_coh_signal": {side: [] for side in sides},
        "ForceRatio": {side: [] for side in sides},
        "AttritionMomentum": {side: [] for side in sides},
        "first_tick_pressure_v2_shadow": {side: None for side in sides},
        "first_tick_collapse_v2_shadow": {side: None for side in sides},
        "pct_ticks_pressure_true": {side: 0.0 for side in sides},
        "pct_ticks_collapse_true": {side: 0.0 for side in sides},
        "notes": {side: "" for side in sides},
        "config": {
            "attrition_window": int(max(1, attrition_window)),
            "sustain_ticks": int(max(1, sustain_ticks)),
            "min_conditions": int(max(1, min_conditions)),
            "theta_defaults": {
                "theta_conn": float(theta_conn_default),
                "theta_coh": float(theta_coh_default),
                "theta_force": float(theta_force_default),
                "theta_attr": float(theta_attr_default),
            },
        },
    }
    if n_ticks <= 0:
        return out

    if not bool(observer_enabled):
        for side in sides:
            out["C_conn_signal"][side] = [float("nan")] * n_ticks
            out["C_coh_signal"][side] = [float("nan")] * n_ticks
            out["ForceRatio"][side] = [float("nan")] * n_ticks
            out["AttritionMomentum"][side] = [float("nan")] * n_ticks
            out["pressure_v2_shadow"][side] = [False] * n_ticks
            out["collapse_v2_shadow"][side] = [False] * n_ticks
            out["pressure_sustain_counter"][side] = [0] * n_ticks
            out["pct_ticks_pressure_true"][side] = 0.0
            out["pct_ticks_collapse_true"][side] = 0.0
            out["notes"][side] = "observer_disabled"
        return out

    alive_a = [float(v) for v in alive_trajectory.get("A", [])]
    alive_b = [float(v) for v in alive_trajectory.get("B", [])]
    c_conn_raw = observer_telemetry.get("c_conn", {}) if isinstance(observer_telemetry, dict) else {}
    c_coh_raw = observer_telemetry.get("cohesion_v3", {}) if isinstance(observer_telemetry, dict) else {}
    if not isinstance(c_conn_raw, dict):
        c_conn_raw = {}
    if not isinstance(c_coh_raw, dict):
        c_coh_raw = {}
    c_conn_a_series = c_conn_raw.get("A", [])
    c_conn_b_series = c_conn_raw.get("B", [])
    c_coh_a_series = c_coh_raw.get("A", [])
    c_coh_b_series = c_coh_raw.get("B", [])
    if not isinstance(c_conn_a_series, (list, tuple)):
        c_conn_a_series = []
    if not isinstance(c_conn_b_series, (list, tuple)):
        c_conn_b_series = []
    if not isinstance(c_coh_a_series, (list, tuple)):
        c_coh_a_series = []
    if not isinstance(c_coh_b_series, (list, tuple)):
        c_coh_b_series = []

    # Build side-level raw signals first.
    for idx in range(n_ticks):
        tick = idx + 1
        w_eff = min(max(1, int(attrition_window)), tick)
        prev_idx = idx - w_eff
        if prev_idx < 0:
            prev_idx = 0

        alive_curr_a = float(alive_a[idx]) if idx < len(alive_a) else (float(alive_a[-1]) if alive_a else 0.0)
        alive_curr_b = float(alive_b[idx]) if idx < len(alive_b) else (float(alive_b[-1]) if alive_b else 0.0)
        alive_prev_a = float(alive_a[prev_idx]) if prev_idx < len(alive_a) else alive_curr_a
        alive_prev_b = float(alive_b[prev_idx]) if prev_idx < len(alive_b) else alive_curr_b

        loss_rate_a = (alive_prev_a - alive_curr_a) / float(w_eff)
        loss_rate_b = (alive_prev_b - alive_curr_b) / float(w_eff)
        attr_momentum_a = float(loss_rate_a - loss_rate_b)
        attr_momentum_b = float(loss_rate_b - loss_rate_a)

        force_ratio_a = float(alive_curr_a / alive_curr_b) if alive_curr_b > 0.0 else float("inf")
        force_ratio_b = float(alive_curr_b / alive_curr_a) if alive_curr_a > 0.0 else float("inf")

        c_conn_a = _safe_float_or_nan(c_conn_a_series[idx] if idx < len(c_conn_a_series) else float("nan"))
        c_conn_b = _safe_float_or_nan(c_conn_b_series[idx] if idx < len(c_conn_b_series) else float("nan"))
        c_coh_a = _safe_float_or_nan(c_coh_a_series[idx] if idx < len(c_coh_a_series) else float("nan"))
        c_coh_b = _safe_float_or_nan(c_coh_b_series[idx] if idx < len(c_coh_b_series) else float("nan"))

        out["C_conn_signal"]["A"].append(c_conn_a)
        out["C_conn_signal"]["B"].append(c_conn_b)
        out["C_coh_signal"]["A"].append(c_coh_a)
        out["C_coh_signal"]["B"].append(c_coh_b)
        out["ForceRatio"]["A"].append(force_ratio_a)
        out["ForceRatio"]["B"].append(force_ratio_b)
        out["AttritionMomentum"]["A"].append(attr_momentum_a)
        out["AttritionMomentum"]["B"].append(attr_momentum_b)

    # Per-side quantile thresholds (fallback to defaults if signal missing).
    for side in sides:
        finite_conn = sorted(v for v in out["C_conn_signal"][side] if math.isfinite(v))
        finite_coh = sorted(v for v in out["C_coh_signal"][side] if math.isfinite(v))
        finite_force = sorted(v for v in out["ForceRatio"][side] if math.isfinite(v))
        finite_attr = sorted(v for v in out["AttritionMomentum"][side] if math.isfinite(v))
        theta_conn = _quantile(finite_conn, 0.20) if finite_conn else float(theta_conn_default)
        theta_coh = _quantile(finite_coh, 0.20) if finite_coh else float(theta_coh_default)
        theta_force = _quantile(finite_force, 0.30) if finite_force else float(theta_force_default)
        theta_attr = _quantile(finite_attr, 0.70) if finite_attr else float(theta_attr_default)
        out["thresholds"][side] = {
            "theta_conn": float(theta_conn),
            "theta_coh": float(theta_coh),
            "theta_force": float(theta_force),
            "theta_attr": float(theta_attr),
        }

    # Pressure/collapse state machine (observer-only).
    for side in sides:
        theta_conn = float(out["thresholds"][side]["theta_conn"])
        theta_coh = float(out["thresholds"][side]["theta_coh"])
        theta_force = float(out["thresholds"][side]["theta_force"])
        theta_attr = float(out["thresholds"][side]["theta_attr"])
        counter = 0
        pressure_true_count = 0
        collapse_true_count = 0
        for idx in range(n_ticks):
            c_conn = float(out["C_conn_signal"][side][idx])
            c_coh = float(out["C_coh_signal"][side][idx])
            force_ratio = float(out["ForceRatio"][side][idx])
            attr_momentum = float(out["AttritionMomentum"][side][idx])
            cond_conn = math.isfinite(c_conn) and (c_conn < theta_conn)
            cond_coh = math.isfinite(c_coh) and (c_coh < theta_coh)
            cond_force = math.isfinite(force_ratio) and (force_ratio < theta_force)
            cond_attr = math.isfinite(attr_momentum) and (attr_momentum > theta_attr)
            pressure = int(cond_conn) + int(cond_coh) + int(cond_force) + int(cond_attr) >= int(min_conditions)
            if pressure:
                counter += 1
                pressure_true_count += 1
            else:
                counter = 0
            collapse_shadow = counter >= int(sustain_ticks)
            if collapse_shadow:
                collapse_true_count += 1

            out["pressure_v2_shadow"][side].append(bool(pressure))
            out["pressure_sustain_counter"][side].append(int(counter))
            out["collapse_v2_shadow"][side].append(bool(collapse_shadow))

            tick = idx + 1
            if pressure and out["first_tick_pressure_v2_shadow"][side] is None:
                out["first_tick_pressure_v2_shadow"][side] = int(tick)
            if collapse_shadow and out["first_tick_collapse_v2_shadow"][side] is None:
                out["first_tick_collapse_v2_shadow"][side] = int(tick)

        out["pct_ticks_pressure_true"][side] = (float(pressure_true_count) / float(n_ticks)) * 100.0
        out["pct_ticks_collapse_true"][side] = (float(collapse_true_count) / float(n_ticks)) * 100.0
        if out["first_tick_collapse_v2_shadow"][side] is None:
            out["notes"][side] = "never-trigger"
        else:
            out["notes"][side] = "triggered"

    return out


def build_initial_state(
    fleet_a_params: PersonalityParameters,
    fleet_b_params: PersonalityParameters,
    fleet_size: int,
    aspect_ratio: float,
    unit_spacing: float,
    unit_speed: float,
    unit_max_hit_points: float,
    arena_size: float,
) -> BattleState:
    grid_columns = max(1, int((fleet_size * aspect_ratio) ** 0.5))
    grid_rows = (fleet_size + grid_columns - 1) // grid_columns
    while grid_columns / max(1, grid_rows) < aspect_ratio and grid_columns < fleet_size:
        grid_columns += 1
        grid_rows = (fleet_size + grid_columns - 1) // grid_columns

    spawn_margin = max(1.0, arena_size * DEFAULT_SPAWN_MARGIN_RATIO)
    fleet_a_origin_x = spawn_margin
    fleet_a_origin_y = spawn_margin
    fleet_b_origin_x = arena_size - spawn_margin
    fleet_b_origin_y = arena_size - spawn_margin

    dx_ab = fleet_b_origin_x - fleet_a_origin_x
    dy_ab = fleet_b_origin_y - fleet_a_origin_y
    norm_ab = (dx_ab * dx_ab + dy_ab * dy_ab) ** 0.5
    if norm_ab > 0.0:
        dir_a = (dx_ab / norm_ab, dy_ab / norm_ab)
    else:
        dir_a = (1.0, 0.0)
    dir_b = (-dir_a[0], -dir_a[1])

    perp_a = (-dir_a[1], dir_a[0])
    perp_b = (-dir_b[1], dir_b[0])
    half_width = (grid_columns - 1) / 2.0

    units = {}
    fleet_a_unit_ids = []
    fleet_b_unit_ids = []

    for i in range(fleet_size):
        row = i // grid_columns
        col = i % grid_columns
        lateral = col - half_width

        unit_a_id = f"A{i + 1}"
        ax = fleet_a_origin_x + (dir_a[0] * row * unit_spacing) + (perp_a[0] * lateral * unit_spacing)
        ay = fleet_a_origin_y + (dir_a[1] * row * unit_spacing) + (perp_a[1] * lateral * unit_spacing)
        units[unit_a_id] = UnitState(
            unit_id=unit_a_id,
            fleet_id="A",
            position=Vec2(x=clamp(ax, 0.0, arena_size), y=clamp(ay, 0.0, arena_size)),
            velocity=Vec2(x=0.0, y=0.0),
            hit_points=unit_max_hit_points,
            max_hit_points=unit_max_hit_points,
            max_speed=unit_speed,
        )
        fleet_a_unit_ids.append(unit_a_id)

        unit_b_id = f"B{i + 1}"
        bx = fleet_b_origin_x + (dir_b[0] * row * unit_spacing) + (perp_b[0] * lateral * unit_spacing)
        by = fleet_b_origin_y + (dir_b[1] * row * unit_spacing) + (perp_b[1] * lateral * unit_spacing)
        units[unit_b_id] = UnitState(
            unit_id=unit_b_id,
            fleet_id="B",
            position=Vec2(x=clamp(bx, 0.0, arena_size), y=clamp(by, 0.0, arena_size)),
            velocity=Vec2(x=0.0, y=0.0),
            hit_points=unit_max_hit_points,
            max_hit_points=unit_max_hit_points,
            max_speed=unit_speed,
        )
        fleet_b_unit_ids.append(unit_b_id)

    fleets = {
        "A": FleetState(fleet_id="A", parameters=fleet_a_params, unit_ids=tuple(fleet_a_unit_ids)),
        "B": FleetState(fleet_id="B", parameters=fleet_b_params, unit_ids=tuple(fleet_b_unit_ids)),
    }

    state = BattleState(
        tick=0,
        dt=DEFAULT_DT,
        arena_size=arena_size,
        units=units,
        fleets=fleets,
        last_fleet_cohesion=build_initial_cohesion_map(fleets.keys()),
    )
    return initialize_unit_orientations(state)


def run_simulation(
    initial_state: BattleState,
    steps: int,
    capture_positions: bool,
    observer_enabled: bool,
    runtime_decision_source: str,
    movement_model: str,
    bridge_theta_split: float,
    bridge_theta_env: float,
    bridge_sustain_ticks: int,
    collapse_shadow_theta_conn_default: float,
    collapse_shadow_theta_coh_default: float,
    collapse_shadow_theta_force_default: float,
    collapse_shadow_theta_attr_default: float,
    collapse_shadow_attrition_window: int,
    collapse_shadow_sustain_ticks: int,
    collapse_shadow_min_conditions: int,
    frame_stride: int,
    attack_range: float,
    damage_per_tick: float,
    separation_radius: float,
    fire_quality_alpha: float,
    contact_hysteresis_h: float,
    ch_enabled: bool,
    fsr_enabled: bool,
    fsr_strength: float,
    boundary_enabled: bool,
    boundary_hard_enabled: bool,
    include_target_lines: bool,
    print_tick_summary: bool,
    plot_diagnostics_enabled: bool,
    boundary_soft_strength: float = 1.0,
    alpha_sep: float = 0.6,
    movement_v3a_experiment: str = "base",
    centroid_probe_scale: float = 1.0,
    v2_connect_radius_multiplier: float = 1.0,
    v3_connect_radius_multiplier: float = 1.0,
    v3_r_ref_radius_multiplier: float = 1.0,
    runtime_diag_enabled: bool = False,
):
    engine = TestModeEngineTickSkeleton(
        attack_range=attack_range,
        damage_per_tick=damage_per_tick,
        separation_radius=separation_radius,
    )
    engine.COHESION_DECISION_SOURCE = str(runtime_decision_source).strip().lower() or "v2"
    engine.MOVEMENT_MODEL = str(movement_model).strip().lower() or "v3a"
    engine.MOVEMENT_V3A_EXPERIMENT = str(movement_v3a_experiment).strip().lower() or "base"
    engine.CENTROID_PROBE_SCALE = float(centroid_probe_scale)
    engine.V2_CONNECT_RADIUS_MULTIPLIER = max(1e-12, float(v2_connect_radius_multiplier))
    engine.V3_CONNECT_RADIUS_MULTIPLIER = max(1e-12, float(v3_connect_radius_multiplier))
    engine.V3_R_REF_RADIUS_MULTIPLIER = max(1e-12, float(v3_r_ref_radius_multiplier))
    engine.fire_quality_alpha = float(fire_quality_alpha)
    engine.contact_hysteresis_h = float(contact_hysteresis_h)
    engine.CH_ENABLED = bool(ch_enabled)
    engine.FSR_ENABLED = bool(fsr_enabled)
    engine.fsr_strength = float(fsr_strength)
    engine.BOUNDARY_SOFT_ENABLED = bool(boundary_enabled)
    engine.BOUNDARY_HARD_ENABLED = bool(boundary_enabled) and bool(boundary_hard_enabled)
    engine.boundary_soft_strength = max(0.0, float(boundary_soft_strength))
    engine.alpha_sep = max(0.0, float(alpha_sep))
    # Plot/runtime diagnostics can be enabled without observer/export pipeline.
    diagnostics_enabled = bool(observer_enabled) or bool(plot_diagnostics_enabled)
    observer_active = bool(diagnostics_enabled) and (bool(capture_positions) or bool(runtime_diag_enabled))
    # Visualization debug panel consumes these runtime diagnostics per frame.
    engine.debug_fsr_diag_enabled = observer_active
    engine.debug_diag4_enabled = observer_active
    engine.debug_diag4_rpg_enabled = False
    engine.debug_cohesion_v3_shadow_enabled = bool(diagnostics_enabled)

    state = replace(
        initial_state,
        last_target_direction={
            fleet_id: initial_state.last_target_direction.get(fleet_id, (0.0, 0.0))
            for fleet_id in initial_state.fleets
        },
        last_engagement_intensity={
            fleet_id: initial_state.last_engagement_intensity.get(fleet_id, 0.0)
            for fleet_id in initial_state.fleets
        },
    )

    trajectory = {fleet_id: [] for fleet_id in state.fleets}
    alive_trajectory = {fleet_id: [] for fleet_id in state.fleets}
    fleet_size_trajectory = {fleet_id: [] for fleet_id in state.fleets}
    observer_telemetry = {
        "cohesion_v3": {fleet_id: [] for fleet_id in state.fleets},
        "c_conn": {fleet_id: [] for fleet_id in state.fleets},
        "c_scale": {fleet_id: [] for fleet_id in state.fleets},
        "rho": {fleet_id: [] for fleet_id in state.fleets},
    }
    combat_telemetry = {
        "in_contact_count": [],
        "damage_events_count": [],
        "outlier_total": [],
        "persistent_outlier_total": [],
        "max_outlier_persistence": [],
    }
    bridge_telemetry = {
        "theta_split": float(bridge_theta_split),
        "theta_env": float(bridge_theta_env),
        "sustain_ticks": int(bridge_sustain_ticks),
        "AR": {fleet_id: [] for fleet_id in state.fleets},
        "wedge_ratio": {fleet_id: [] for fleet_id in state.fleets},
        "split_separation": {fleet_id: [] for fleet_id in state.fleets},
        "angle_coverage": {fleet_id: [] for fleet_id in state.fleets},
        "split_cond": {fleet_id: [] for fleet_id in state.fleets},
        "env_cond": {fleet_id: [] for fleet_id in state.fleets},
        "split_sustain_counter": {fleet_id: [] for fleet_id in state.fleets},
        "env_sustain_counter": {fleet_id: [] for fleet_id in state.fleets},
        "bridge_event_cut": {fleet_id: [] for fleet_id in state.fleets},
        "bridge_event_pocket": {fleet_id: [] for fleet_id in state.fleets},
        "first_tick_split_sustain": {fleet_id: None for fleet_id in state.fleets},
        "first_tick_env_sustain": {fleet_id: None for fleet_id in state.fleets},
    }
    split_counter_state = {fleet_id: 0 for fleet_id in state.fleets}
    env_counter_state = {fleet_id: 0 for fleet_id in state.fleets}
    position_frames = []

    if steps <= 0:
        tick_limit = 999
        elimination_tick = None
        post_elimination_stop_tick = None
    else:
        tick_limit = steps
        elimination_tick = None
        post_elimination_stop_tick = None

    while state.tick < tick_limit:
        state = engine.step(state)
        combat_stats = getattr(engine, "debug_last_combat_stats", {})
        if not isinstance(combat_stats, dict):
            combat_stats = {}
        combat_telemetry["in_contact_count"].append(int(combat_stats.get("in_contact_count", 0)))
        combat_telemetry["damage_events_count"].append(int(combat_stats.get("damage_events_count", 0)))
        runtime_debug_payload = extract_runtime_debug_payload(
            getattr(engine, "debug_diag_last_tick", {}) if diagnostics_enabled else {}
        )
        combat_telemetry["outlier_total"].append(int(runtime_debug_payload.get("outlier_total", 0)))
        combat_telemetry["persistent_outlier_total"].append(int(runtime_debug_payload.get("persistent_outlier_total", 0)))
        combat_telemetry["max_outlier_persistence"].append(int(runtime_debug_payload.get("max_outlier_persistence", 0)))
        contact_active_tick = int(combat_stats.get("in_contact_count", 0)) > 0
        if print_tick_summary:
            ordered_fleet_ids = [fleet_id for fleet_id in ("A", "B") if fleet_id in state.fleets]
            if not ordered_fleet_ids:
                ordered_fleet_ids = sorted(state.fleets.keys())
            if len(ordered_fleet_ids) >= 2:
                fleet_a = state.fleets[ordered_fleet_ids[0]]
                fleet_b = state.fleets[ordered_fleet_ids[1]]
                name_a = str(getattr(fleet_a.parameters, "archetype_id", "") or ordered_fleet_ids[0])
                name_b = str(getattr(fleet_b.parameters, "archetype_id", "") or ordered_fleet_ids[1])
                print(f"t={state.tick}, [{name_a}] vs [{name_b}], {len(fleet_a.unit_ids)}/{len(fleet_b.unit_ids)}")
            elif len(ordered_fleet_ids) == 1:
                fleet = state.fleets[ordered_fleet_ids[0]]
                name = str(getattr(fleet.parameters, "archetype_id", "") or ordered_fleet_ids[0])
                print(f"t={state.tick}, [{name}], {len(fleet.unit_ids)}")
        for fleet_id, fleet in state.fleets.items():
            trajectory[fleet_id].append(state.last_fleet_cohesion.get(fleet_id, 1.0))
            alive_trajectory[fleet_id].append(len(fleet.unit_ids))
            fleet_size = 0.0
            for unit_id in fleet.unit_ids:
                if unit_id in state.units:
                    fleet_size += max(0.0, float(state.units[unit_id].hit_points))
            fleet_size_trajectory[fleet_id].append(fleet_size)
        shadow_v3 = getattr(engine, "debug_last_cohesion_v3", {})
        if not isinstance(shadow_v3, dict):
            shadow_v3 = {}
        shadow_v3_components = getattr(engine, "debug_last_cohesion_v3_components", {})
        if not isinstance(shadow_v3_components, dict):
            shadow_v3_components = {}
        for fleet_id in state.fleets:
            fallback_v2 = float(state.last_fleet_cohesion.get(fleet_id, 1.0))
            if diagnostics_enabled:
                cohesion_v3 = float(shadow_v3.get(fleet_id, fallback_v2))
            else:
                cohesion_v3 = float("nan")
            comp = shadow_v3_components.get(fleet_id, {})
            if not isinstance(comp, dict):
                comp = {}
            observer_telemetry["cohesion_v3"][fleet_id].append(cohesion_v3)
            observer_telemetry["c_conn"][fleet_id].append(float(comp.get("c_conn", float("nan"))))
            observer_telemetry["c_scale"][fleet_id].append(float(comp.get("c_scale", float("nan"))))
            observer_telemetry["rho"][fleet_id].append(float(comp.get("rho", float("nan"))))

        bridge_metrics = compute_bridge_metrics_per_side(state)
        for fleet_id in state.fleets:
            if diagnostics_enabled:
                metric = bridge_metrics.get(fleet_id, {})
                ar_value = float(metric.get("AR", float("nan")))
                wedge_value = float(metric.get("wedge_ratio", float("nan")))
                split_value = float(metric.get("split_separation", 0.0))
                env_value = float(metric.get("angle_coverage", 0.0))
                split_cond = bool(
                    state.tick >= 1 and contact_active_tick and split_value >= float(bridge_theta_split)
                )
                env_cond = bool(
                    state.tick >= 1 and contact_active_tick and env_value >= float(bridge_theta_env)
                )
            else:
                ar_value = float("nan")
                wedge_value = float("nan")
                split_value = float("nan")
                env_value = float("nan")
                split_cond = False
                env_cond = False

            if split_cond:
                split_counter_state[fleet_id] = int(split_counter_state.get(fleet_id, 0)) + 1
            else:
                split_counter_state[fleet_id] = 0
            if env_cond:
                env_counter_state[fleet_id] = int(env_counter_state.get(fleet_id, 0)) + 1
            else:
                env_counter_state[fleet_id] = 0

            cut_event_tick = False
            pocket_event_tick = False
            if (
                split_counter_state[fleet_id] >= int(bridge_sustain_ticks)
                and bridge_telemetry["first_tick_split_sustain"].get(fleet_id) is None
            ):
                bridge_telemetry["first_tick_split_sustain"][fleet_id] = int(state.tick)
                cut_event_tick = True
            if (
                env_counter_state[fleet_id] >= int(bridge_sustain_ticks)
                and bridge_telemetry["first_tick_env_sustain"].get(fleet_id) is None
            ):
                bridge_telemetry["first_tick_env_sustain"][fleet_id] = int(state.tick)
                pocket_event_tick = True

            bridge_telemetry["AR"][fleet_id].append(ar_value)
            bridge_telemetry["wedge_ratio"][fleet_id].append(wedge_value)
            bridge_telemetry["split_separation"][fleet_id].append(split_value)
            bridge_telemetry["angle_coverage"][fleet_id].append(env_value)
            bridge_telemetry["split_cond"][fleet_id].append(bool(split_cond))
            bridge_telemetry["env_cond"][fleet_id].append(bool(env_cond))
            bridge_telemetry["split_sustain_counter"][fleet_id].append(int(split_counter_state[fleet_id]))
            bridge_telemetry["env_sustain_counter"][fleet_id].append(int(env_counter_state[fleet_id]))
            bridge_telemetry["bridge_event_cut"][fleet_id].append(bool(cut_event_tick))
            bridge_telemetry["bridge_event_pocket"][fleet_id].append(bool(pocket_event_tick))

        if capture_positions and frame_stride > 0 and state.tick % frame_stride == 0:
            frame = {"tick": state.tick}
            targets = {}
            for fleet_id, fleet in state.fleets.items():
                points = []
                for unit_id in fleet.unit_ids:
                    if unit_id in state.units:
                        unit = state.units[unit_id]
                        points.append(
                            (
                                unit_id,
                                unit.position.x,
                                unit.position.y,
                                unit.orientation_vector.x,
                                unit.orientation_vector.y,
                                unit.velocity.x,
                                unit.velocity.y,
                            )
                        )
                        if include_target_lines and unit.engaged and unit.engaged_target_id:
                            target_id = str(unit.engaged_target_id)
                            if target_id in state.units and state.units[target_id].hit_points > 0.0:
                                targets[str(unit_id)] = target_id
                frame[fleet_id] = points
            if include_target_lines:
                frame["targets"] = targets
            frame["runtime_debug"] = extract_runtime_debug_payload(
                getattr(engine, "debug_diag_last_tick", {}) if observer_active else {}
            )
            position_frames.append(frame)

        any_fleet_eliminated = any(len(fleet.unit_ids) == 0 for fleet in state.fleets.values())
        if steps <= 0:
            if any_fleet_eliminated and elimination_tick is None:
                elimination_tick = state.tick
                post_elimination_stop_tick = min(999, elimination_tick + 10)
            if post_elimination_stop_tick is not None and state.tick >= post_elimination_stop_tick:
                break
        else:
            if any_fleet_eliminated:
                break

    collapse_shadow_telemetry = compute_collapse_v2_shadow_telemetry(
        observer_enabled=diagnostics_enabled,
        observer_telemetry=observer_telemetry,
        alive_trajectory=alive_trajectory,
        theta_conn_default=float(collapse_shadow_theta_conn_default),
        theta_coh_default=float(collapse_shadow_theta_coh_default),
        theta_force_default=float(collapse_shadow_theta_force_default),
        theta_attr_default=float(collapse_shadow_theta_attr_default),
        attrition_window=int(collapse_shadow_attrition_window),
        sustain_ticks=int(collapse_shadow_sustain_ticks),
        min_conditions=int(collapse_shadow_min_conditions),
    )

    return (
        state,
        trajectory,
        alive_trajectory,
        fleet_size_trajectory,
        observer_telemetry,
        combat_telemetry,
        bridge_telemetry,
        collapse_shadow_telemetry,
        position_frames,
    )


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    settings = load_json_file(base_dir / "test_run_v1_0.settings.json")
    viz_settings = load_json_file(base_dir / "test_run_v1_0.viz.settings.json")
    archetypes = load_json_file(PROJECT_ROOT / "archetypes" / "archetypes_v1_5.json")
    metatype_settings = load_metatype_settings(base_dir, settings)
    random_seed = int(get_run_control_setting(settings, "random_seed", -1))
    metatype_random_seed = int(get_run_control_setting(settings, "metatype_random_seed", random_seed))
    background_map_seed = int(get_battlefield_setting(settings, "background_map_seed", -1))
    effective_random_seed = resolve_effective_seed(random_seed)
    effective_metatype_random_seed = resolve_effective_seed(metatype_random_seed)
    effective_background_map_seed = resolve_effective_seed(background_map_seed)
    archetype_rng = random.Random(int(effective_metatype_random_seed))

    fleet_a_data = resolve_fleet_archetype_data(
        archetypes,
        metatype_settings,
        get_fleet_setting(settings, "fleet_a_archetype_id", "default"),
        rng=archetype_rng,
    )
    fleet_b_data = resolve_fleet_archetype_data(
        archetypes,
        metatype_settings,
        get_fleet_setting(settings, "fleet_b_archetype_id", "default"),
        rng=archetype_rng,
    )
    fleet_a_params = to_personality_parameters(fleet_a_data)
    fleet_b_params = to_personality_parameters(fleet_b_data)
    fleet_a_color = to_plot_color(fleet_a_data, DEFAULT_PLOT_COLORS[0])
    fleet_b_color = to_plot_color(fleet_b_data, DEFAULT_PLOT_COLORS[1])

    display_language = str(get_run_control_setting(settings, "display_language", "EN")).upper()
    if display_language not in ("EN", "ZH"):
        display_language = "EN"
    fleet_a_display_name = resolve_display_name(fleet_a_data, display_language)
    fleet_b_display_name = resolve_display_name(fleet_b_data, display_language)
    fleet_a_full_name = resolve_name_with_fallback(fleet_a_data, display_language, True, "A")
    fleet_b_full_name = resolve_name_with_fallback(fleet_b_data, display_language, True, "B")
    fleet_a_avatar = resolve_avatar_with_fallback(fleet_a_data, DEFAULT_AVATAR_A)
    fleet_b_avatar = resolve_avatar_with_fallback(fleet_b_data, DEFAULT_AVATAR_B)

    fleet_size = int(get_fleet_setting(settings, "initial_fleet_size", 100))
    aspect_ratio = float(get_fleet_setting(settings, "initial_fleet_aspect_ratio", 2.0))
    unit_spacing = float(get_runtime_setting(settings, "min_unit_spacing", 1.0))
    if fleet_size < 1:
        raise ValueError(f"initial_fleet_size must be >= 1, got {fleet_size}")
    if aspect_ratio <= 0.0:
        raise ValueError(f"initial_fleet_aspect_ratio must be > 0, got {aspect_ratio}")
    if unit_spacing <= 0.0:
        raise ValueError(f"min_unit_spacing must be > 0, got {unit_spacing}")

    unit_speed = float(get_unit_setting(settings, "unit_speed", 1.0))
    unit_max_hit_points = float(get_unit_setting(settings, "unit_max_hit_points", 100.0))
    arena_size = float(get_battlefield_setting(settings, "arena_size", 200.0))
    state = build_initial_state(
        fleet_a_params=fleet_a_params,
        fleet_b_params=fleet_b_params,
        fleet_size=fleet_size,
        aspect_ratio=aspect_ratio,
        unit_spacing=unit_spacing,
        unit_speed=unit_speed,
        unit_max_hit_points=unit_max_hit_points,
        arena_size=arena_size,
    )

    initial_fleet_sizes = {}
    for fleet_id, fleet in state.fleets.items():
        fleet_size_hp = 0.0
        for unit_id in fleet.unit_ids:
            if unit_id in state.units:
                fleet_size_hp += max(0.0, float(state.units[unit_id].hit_points))
        initial_fleet_sizes[fleet_id] = fleet_size_hp

    animate = bool(get_run_control_setting(settings, "animate", True))
    visualization_section = get_visualization_section(settings)
    auto_zoom_2d = bool(get_visualization_setting(settings, "auto_zoom_2d", False))
    frame_stride = DEFAULT_FRAME_STRIDE
    base_frame_interval_ms = max(1, int(get_visualization_setting(settings, "animation_frame_interval_ms", 100)))
    animation_play_speed = float(get_visualization_setting(settings, "animation_play_speed", 1.0))
    if animation_play_speed <= 0.0:
        animation_play_speed = 1.0
    frame_interval_ms = max(1, int(round(base_frame_interval_ms / animation_play_speed)))
    attack_range = float(get_unit_setting(settings, "attack_range", get_runtime_setting(settings, "attack_range", 3.0)))
    damage_per_tick = float(get_unit_setting(settings, "damage_per_tick", get_runtime_setting(settings, "damage_per_tick", 1.0)))
    fire_quality_alpha = float(get_runtime_setting(settings, "fire_quality_alpha", 0.1))
    contact_hysteresis_h = float(get_runtime_setting(settings, "contact_hysteresis_h", 0.1))
    fsr_strength = float(get_runtime_setting(settings, "fsr_strength", 0.0))
    alpha_sep = float(get_runtime_setting(settings, "alpha_sep", 0.6))
    if alpha_sep < 0.0:
        alpha_sep = 0.0
    movement_model_requested, movement_model_effective = resolve_movement_model(
        get_runtime_setting(settings, "movement_model", "baseline")
    )
    movement_v3a_experiment_raw = str(get_runtime_setting(settings, "movement_v3a_experiment", "base")).strip().lower()
    if movement_v3a_experiment_raw not in {"base", "exp_precontact_centroid_probe"}:
        movement_v3a_experiment_raw = "base"
    movement_v3a_experiment_effective = movement_v3a_experiment_raw
    centroid_probe_scale = float(get_runtime_setting(settings, "centroid_probe_scale", 1.0))
    if centroid_probe_scale < 0.0:
        centroid_probe_scale = 0.0
    elif centroid_probe_scale > 1.0:
        centroid_probe_scale = 1.0
    if movement_model_effective != "v3a" or movement_v3a_experiment_effective != "exp_precontact_centroid_probe":
        centroid_probe_scale_effective = 1.0
    else:
        centroid_probe_scale_effective = centroid_probe_scale
    bridge_theta_split = float(get_event_bridge_setting(settings, "theta_split", BRIDGE_THETA_SPLIT_DEFAULT))
    bridge_theta_env = float(get_event_bridge_setting(settings, "theta_env", BRIDGE_THETA_ENV_DEFAULT))
    bridge_sustain_ticks = max(1, int(get_event_bridge_setting(settings, "sustain_ticks", BRIDGE_SUSTAIN_TICKS_DEFAULT)))
    collapse_shadow_theta_conn_default = float(
        get_collapse_shadow_setting(settings, "theta_conn_default", COLLAPSE_V2_SHADOW_THETA_CONN_DEFAULT)
    )
    collapse_shadow_theta_coh_default = float(
        get_collapse_shadow_setting(settings, "theta_coh_default", COLLAPSE_V2_SHADOW_THETA_COH_DEFAULT)
    )
    collapse_shadow_theta_force_default = float(
        get_collapse_shadow_setting(settings, "theta_force_default", COLLAPSE_V2_SHADOW_THETA_FORCE_DEFAULT)
    )
    collapse_shadow_theta_attr_default = float(
        get_collapse_shadow_setting(settings, "theta_attr_default", COLLAPSE_V2_SHADOW_THETA_ATTR_DEFAULT)
    )
    collapse_shadow_attrition_window = max(
        1,
        int(get_collapse_shadow_setting(settings, "attrition_window", COLLAPSE_V2_SHADOW_ATTRITION_WINDOW_DEFAULT)),
    )
    collapse_shadow_sustain_ticks = max(
        1,
        int(get_collapse_shadow_setting(settings, "sustain_ticks", COLLAPSE_V2_SHADOW_SUSTAIN_TICKS_DEFAULT)),
    )
    collapse_shadow_min_conditions = min(
        4,
        max(
            1,
            int(get_collapse_shadow_setting(settings, "min_conditions", COLLAPSE_V2_SHADOW_MIN_CONDITIONS_DEFAULT)),
        ),
    )
    strategic_inflection_sustain_ticks = max(
        1,
        int(get_report_inference_setting(settings, "strategic_inflection_sustain_ticks", STRATEGIC_INFLECTION_SUSTAIN_TICKS)),
    )
    tactical_swing_sustain_ticks = max(
        1,
        int(get_report_inference_setting(settings, "tactical_swing_sustain_ticks", TACTICAL_SWING_SUSTAIN_TICKS)),
    )
    tactical_swing_min_amplitude = max(
        0.0,
        float(get_report_inference_setting(settings, "tactical_swing_min_amplitude", TACTICAL_SWING_MIN_AMPLITUDE)),
    )
    tactical_swing_min_gap_ticks = max(
        0,
        int(get_report_inference_setting(settings, "tactical_swing_min_gap_ticks", TACTICAL_SWING_MIN_GAP_TICKS)),
    )
    # Canonical runtime toggle rule (strength-only):
    # - contact_hysteresis_h <= 0 => CH disabled
    # - fsr_strength <= 0 => FSR disabled
    ch_enabled = contact_hysteresis_h > 0.0
    fsr_enabled = fsr_strength > 0.0
    boundary_enabled = bool(get_runtime_setting(settings, "boundary_enabled", False))
    boundary_hard_enabled = bool(get_runtime_setting(settings, "boundary_hard_enabled", True))
    boundary_soft_strength = float(get_runtime_setting(settings, "boundary_soft_strength", 1.0))
    if boundary_soft_strength < 0.0:
        boundary_soft_strength = 0.0
    boundary_hard_enabled_effective = bool(boundary_enabled) and bool(boundary_hard_enabled)
    unit_direction_mode = str(
        get_visualization_setting(
            settings,
            "vector_display_mode",
            get_visualization_setting(settings, "unit_direction_mode", "effective"),
        )
    ).strip().lower()
    if unit_direction_mode not in {"effective", "free", "attack", "composite"}:
        unit_direction_mode = "effective"
    show_attack_target_lines = bool(get_visualization_setting(settings, "show_attack_target_lines", False))
    tick_plots_follow_battlefield_tick = bool(get_visualization_setting(settings, "tick_plots_follow_battlefield_tick", False))
    print_tick_summary = bool(get_visualization_setting(settings, "print_tick_summary", True))
    test_mode = parse_test_mode(get_run_control_setting(settings, "test_mode", 0))
    test_mode_name = test_mode_label(test_mode)
    observer_enabled = test_mode >= 1
    export_battle_report = test_mode >= 1
    runtime_decision_source_requested, runtime_decision_source_effective = resolve_runtime_decision_source(
        get_runtime_setting(settings, "cohesion_decision_source", "baseline"),
        test_mode,
    )
    v3_connect_radius_multiplier = float(
        get_runtime_setting(settings, "v3_connect_radius_multiplier", BASELINE_V3_CONNECT_RADIUS_MULTIPLIER)
    )
    if v3_connect_radius_multiplier <= 0.0:
        v3_connect_radius_multiplier = BASELINE_V3_CONNECT_RADIUS_MULTIPLIER
    v3_r_ref_radius_multiplier = float(
        get_runtime_setting(settings, "v3_r_ref_radius_multiplier", BASELINE_V3_R_REF_RADIUS_MULTIPLIER)
    )
    if v3_r_ref_radius_multiplier <= 0.0:
        v3_r_ref_radius_multiplier = BASELINE_V3_R_REF_RADIUS_MULTIPLIER
    if runtime_decision_source_effective == "v3_test":
        v3_connect_radius_multiplier_effective = v3_connect_radius_multiplier
        v3_r_ref_radius_multiplier_effective = v3_r_ref_radius_multiplier
    else:
        v3_connect_radius_multiplier_effective = 1.0
        v3_r_ref_radius_multiplier_effective = 1.0
    plot_profile_requested, plot_profile_effective = resolve_plot_profile(
        get_visualization_setting(settings, "plot_profile", "auto"),
        test_mode,
        runtime_decision_source_requested,
        runtime_decision_source_effective,
    )
    plot_diagnostics_enabled = bool(animate) or bool(observer_enabled)
    print(f"[viz] random_seed_effective={effective_random_seed}")
    print(f"[mode] metatype_random_seed_effective={effective_metatype_random_seed}")
    print(f"[viz] background_map_seed_effective={effective_background_map_seed}")
    print(
        f"[viz] animation_play_speed={animation_play_speed:.2f}, "
        f"base_interval_ms={base_frame_interval_ms}, frame_interval_ms={frame_interval_ms}"
    )
    print(f"[mode] test_mode={test_mode} ({test_mode_name})")
    print(f"[mode] plot_profile_requested={plot_profile_requested}")
    print(f"[mode] plot_profile_effective={plot_profile_effective}")
    print(f"[mode] movement_model_requested={movement_model_requested}")
    print(f"[mode] cohesion_decision_source_requested={runtime_decision_source_requested}")
    print(f"[mode] runtime_decision_source_effective={runtime_decision_source_effective}")
    if runtime_decision_source_effective == "v3_test":
        print(f"[runtime] v3_connect_radius_multiplier_effective={v3_connect_radius_multiplier_effective:.3f}")
        print(f"[runtime] v3_r_ref_radius_multiplier_effective={v3_r_ref_radius_multiplier_effective:.3f}")
    print(f"[mode] movement_model_effective={movement_model_effective}")
    print(f"[runtime] alpha_sep={alpha_sep:.3f}")
    if movement_model_effective == "v3a":
        print(f"[mode] movement_v3a_experiment_effective={movement_v3a_experiment_effective}")
        print(f"[mode] centroid_probe_scale_effective={centroid_probe_scale_effective:.3f}")
    print(f"[viz] vector_display_mode={unit_direction_mode}")
    print(
        f"[runtime] boundary soft={boundary_enabled} "
        f"strength={boundary_soft_strength:.3f} "
        f"hard_requested={boundary_hard_enabled} hard_effective={boundary_hard_enabled_effective}"
    )
    print(f"[viz] avatars A={fleet_a_avatar} B={fleet_b_avatar}")
    print(f"[observer] enabled={observer_enabled}")
    print(f"[plot] diagnostics_enabled={plot_diagnostics_enabled}")
    print(f"[report] enabled={export_battle_report}")
    export_video_cfg = visualization_section.get("export_video", {})
    if not isinstance(export_video_cfg, dict):
        export_video_cfg = {}
    else:
        export_video_cfg = dict(export_video_cfg)
    raw_video_output_path = str(export_video_cfg.get("output_path", DEFAULT_VIDEO_EXPORT_DIR))
    resolved_video_output_path = resolve_timestamped_video_output_path(raw_video_output_path, base_dir=base_dir)
    export_video_cfg["output_path"] = str(resolved_video_output_path)

    capture_target_directions = show_attack_target_lines or (unit_direction_mode in {"attack", "composite"})
    (
        final_state,
        trajectory,
        alive_trajectory,
        fleet_size_trajectory,
        observer_telemetry,
        combat_telemetry,
        bridge_telemetry,
        collapse_shadow_telemetry,
        position_frames,
    ) = run_simulation(
        initial_state=state,
        steps=int(get_run_control_setting(settings, "max_time_steps", -1)),
        capture_positions=animate,
        observer_enabled=observer_enabled,
        runtime_decision_source=runtime_decision_source_effective,
        movement_model=movement_model_effective,
        bridge_theta_split=bridge_theta_split,
        bridge_theta_env=bridge_theta_env,
        bridge_sustain_ticks=bridge_sustain_ticks,
        collapse_shadow_theta_conn_default=collapse_shadow_theta_conn_default,
        collapse_shadow_theta_coh_default=collapse_shadow_theta_coh_default,
        collapse_shadow_theta_force_default=collapse_shadow_theta_force_default,
        collapse_shadow_theta_attr_default=collapse_shadow_theta_attr_default,
        collapse_shadow_attrition_window=collapse_shadow_attrition_window,
        collapse_shadow_sustain_ticks=collapse_shadow_sustain_ticks,
        collapse_shadow_min_conditions=collapse_shadow_min_conditions,
        frame_stride=frame_stride,
        attack_range=attack_range,
        damage_per_tick=damage_per_tick,
        separation_radius=unit_spacing,
        fire_quality_alpha=fire_quality_alpha,
        contact_hysteresis_h=contact_hysteresis_h,
        ch_enabled=ch_enabled,
        fsr_enabled=fsr_enabled,
        fsr_strength=fsr_strength,
        boundary_enabled=boundary_enabled,
        boundary_hard_enabled=boundary_hard_enabled,
        alpha_sep=alpha_sep,
        boundary_soft_strength=boundary_soft_strength,
        include_target_lines=capture_target_directions,
        print_tick_summary=print_tick_summary,
        plot_diagnostics_enabled=plot_diagnostics_enabled,
        movement_v3a_experiment=movement_v3a_experiment_effective,
        centroid_probe_scale=centroid_probe_scale_effective,
        v3_connect_radius_multiplier=v3_connect_radius_multiplier_effective,
        v3_r_ref_radius_multiplier=v3_r_ref_radius_multiplier_effective,
    )
    if not animate:
        position_frames = []

    max_time_steps_effective = int(final_state.tick)
    run_config_snapshot = {
        "initial_units_per_side": int(fleet_size),
        "test_mode": test_mode,
        "test_mode_label": test_mode_name,
        "metatype_settings_path": str(
            get_run_control_setting(settings, "metatype_settings_path", DEFAULT_METATYPE_SETTINGS_PATH)
        ),
        "random_seed_effective": int(effective_random_seed),
        "background_map_seed_effective": int(effective_background_map_seed),
        "metatype_random_seed_effective": int(effective_metatype_random_seed),
        "runtime_decision_source_effective": runtime_decision_source_effective,
        "collapse_decision_source_effective": runtime_decision_source_effective,
        "movement_model_effective": movement_model_effective,
        "movement_v3a_experiment_effective": movement_v3a_experiment_effective if movement_model_effective == "v3a" else "N/A",
        "centroid_probe_scale_effective": (
            centroid_probe_scale_effective if movement_model_effective == "v3a" else "N/A"
        ),
        "attack_range": attack_range,
        "min_unit_spacing": unit_spacing,
        "arena_size": arena_size,
        "max_time_steps_effective": max_time_steps_effective,
        "unit_speed": unit_speed,
        "damage_per_tick": damage_per_tick,
        "ch_enabled": ch_enabled,
        "contact_hysteresis_h": contact_hysteresis_h,
        "fsr_enabled": fsr_enabled,
        "fsr_strength": fsr_strength,
        "boundary_enabled": boundary_enabled,
        "boundary_soft_strength": boundary_soft_strength,
        "boundary_hard_enabled": boundary_hard_enabled,
        "boundary_hard_enabled_effective": boundary_hard_enabled_effective,
        "alpha_sep": alpha_sep,
        "v3_connect_radius_multiplier_effective": v3_connect_radius_multiplier_effective,
        "v3_r_ref_radius_multiplier_effective": v3_r_ref_radius_multiplier_effective,
        "bridge_theta_split": bridge_theta_split,
        "bridge_theta_env": bridge_theta_env,
        "bridge_sustain_ticks": bridge_sustain_ticks,
        "strategic_inflection_sustain_ticks": strategic_inflection_sustain_ticks,
        "tactical_swing_sustain_ticks": tactical_swing_sustain_ticks,
        "tactical_swing_min_amplitude": tactical_swing_min_amplitude,
        "tactical_swing_min_gap_ticks": tactical_swing_min_gap_ticks,
        "collapse_shadow_theta_conn_default": collapse_shadow_theta_conn_default,
        "collapse_shadow_theta_coh_default": collapse_shadow_theta_coh_default,
        "collapse_shadow_theta_force_default": collapse_shadow_theta_force_default,
        "collapse_shadow_theta_attr_default": collapse_shadow_theta_attr_default,
        "collapse_shadow_attrition_window": collapse_shadow_attrition_window,
        "collapse_shadow_sustain_ticks": collapse_shadow_sustain_ticks,
        "collapse_shadow_min_conditions": collapse_shadow_min_conditions,
    }

    if export_battle_report:
        report_markdown = build_battle_report_markdown(
            settings_source_path=str((base_dir / "test_run_v1_0.settings.json").as_posix()),
            display_language=display_language,
            random_seed_effective=effective_random_seed,
            fleet_a_data=fleet_a_data,
            fleet_b_data=fleet_b_data,
            initial_fleet_sizes=initial_fleet_sizes,
            alive_trajectory=alive_trajectory,
            fleet_size_trajectory=fleet_size_trajectory,
            combat_telemetry=combat_telemetry,
            bridge_telemetry=bridge_telemetry,
            collapse_shadow_telemetry=collapse_shadow_telemetry,
            final_state=final_state,
            run_config_snapshot=run_config_snapshot,
        )
        report_date_dir = datetime.now().strftime("%Y%m%d")
        report_export_dir = (base_dir.parent / DEFAULT_BATTLE_REPORT_EXPORT_DIR / report_date_dir).resolve()
        report_export_dir.mkdir(parents=True, exist_ok=True)
        report_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"{DEFAULT_BATTLE_REPORT_TOPIC}_{report_timestamp}_Battle_Report_Framework_v1.0.md"
        report_output_path = report_export_dir / report_filename
        report_output_path.write_text(report_markdown, encoding="utf-8")
        print(f"[report] battle_report_exported={report_output_path}")

    if not animate:
        return

    try:
        from test_run.test_run_v1_0_viz import render_test_run
    except ModuleNotFoundError as exc:
        print(f"[viz] skipped: {exc}")
        return

    render_test_run(
        arena_size=arena_size,
        trajectory=trajectory,
        alive_trajectory=alive_trajectory,
        fleet_size_trajectory=fleet_size_trajectory,
        initial_fleet_sizes=initial_fleet_sizes,
        position_frames=position_frames,
        final_state=final_state,
        fleet_a_label=fleet_a_display_name,
        fleet_b_label=fleet_b_display_name,
        fleet_a_full_name=fleet_a_full_name,
        fleet_b_full_name=fleet_b_full_name,
        fleet_a_avatar=fleet_a_avatar,
        fleet_b_avatar=fleet_b_avatar,
        fleet_a_color=fleet_a_color,
        fleet_b_color=fleet_b_color,
        auto_zoom_2d=auto_zoom_2d,
        frame_interval_ms=frame_interval_ms,
        background_seed=effective_background_map_seed,
        viz_settings=viz_settings,
        tick_plots_follow_battlefield_tick=tick_plots_follow_battlefield_tick,
        display_language=display_language,
        unit_direction_mode=unit_direction_mode,
        show_attack_target_lines=show_attack_target_lines,
        observer_telemetry=observer_telemetry,
        observer_enabled=observer_enabled,
        plot_profile=plot_profile_effective,
        export_video_cfg=export_video_cfg,
        boundary_enabled=boundary_enabled,
        boundary_hard_enabled=boundary_hard_enabled,
    )


if __name__ == "__main__":
    main()
