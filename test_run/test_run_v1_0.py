import json
import math
import os
import random
import re
import sys
from collections.abc import Mapping, Sequence
from dataclasses import replace
from datetime import datetime
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from runtime.runtime_v0_1 import (
    PersonalityParameters,
    Vec2,
    UnitState,
    FleetState,
    BattleState,
    build_initial_cohesion_map,
    initialize_unit_orientations,
)
from runtime.engine_skeleton import EngineTickSkeleton
from test_run.battle_report_builder import (
    build_battle_report_markdown,
    compute_bridge_event_ticks,
    resolve_name_with_fallback,
)


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
V3A_EXPERIMENT_BASE = "base"
V3A_EXPERIMENT_PRECONTACT_CENTROID_PROBE = "exp_precontact_centroid_probe"
V3A_EXPERIMENT_LABELS = {
    V3A_EXPERIMENT_BASE,
    V3A_EXPERIMENT_PRECONTACT_CENTROID_PROBE,
}
PRE_TL_TARGET_SUBSTRATE_NEAREST5 = "nearest5_centroid"
PRE_TL_TARGET_SUBSTRATE_WEIGHTED_LOCAL = "weighted_local"
PRE_TL_TARGET_SUBSTRATE_LOCAL_CLUSTER = "local_cluster"
PRE_TL_TARGET_SUBSTRATE_SOFT_LOCAL_WEIGHTED = "soft_local_weighted"
PRE_TL_TARGET_SUBSTRATE_SOFT_LOCAL_WEIGHTED_TIGHT = "soft_local_weighted_tight"
PRE_TL_TARGET_SUBSTRATE_LABELS = {
    PRE_TL_TARGET_SUBSTRATE_NEAREST5,
    PRE_TL_TARGET_SUBSTRATE_WEIGHTED_LOCAL,
    PRE_TL_TARGET_SUBSTRATE_LOCAL_CLUSTER,
    PRE_TL_TARGET_SUBSTRATE_SOFT_LOCAL_WEIGHTED,
    PRE_TL_TARGET_SUBSTRATE_SOFT_LOCAL_WEIGHTED_TIGHT,
}
PRE_TL_TARGET_SUBSTRATE_DEFAULT = PRE_TL_TARGET_SUBSTRATE_NEAREST5
HOSTILE_CONTACT_IMPEDANCE_MODE_OFF = "off"
HOSTILE_CONTACT_IMPEDANCE_MODE_REPULSION_V1 = "repulsion_v1"
HOSTILE_CONTACT_IMPEDANCE_MODE_DAMPING_V2 = "damping_v2"
HOSTILE_CONTACT_IMPEDANCE_MODE_HYBRID_V2 = "hybrid_v2"
HOSTILE_CONTACT_IMPEDANCE_MODE_INTENT_UNIFIED_SPACING_V1 = "intent_unified_spacing_v1"
HOSTILE_CONTACT_IMPEDANCE_MODE_INTENT_OCCUPANCY_ONLY_V1 = "intent_occupancy_only_v1"
HOSTILE_CONTACT_IMPEDANCE_MODE_LABELS = {
    HOSTILE_CONTACT_IMPEDANCE_MODE_OFF,
    HOSTILE_CONTACT_IMPEDANCE_MODE_REPULSION_V1,
    HOSTILE_CONTACT_IMPEDANCE_MODE_DAMPING_V2,
    HOSTILE_CONTACT_IMPEDANCE_MODE_HYBRID_V2,
    HOSTILE_CONTACT_IMPEDANCE_MODE_INTENT_UNIFIED_SPACING_V1,
    HOSTILE_CONTACT_IMPEDANCE_MODE_INTENT_OCCUPANCY_ONLY_V1,
}
HOSTILE_CONTACT_IMPEDANCE_MODE_DEFAULT = HOSTILE_CONTACT_IMPEDANCE_MODE_OFF
HOSTILE_CONTACT_IMPEDANCE_STRENGTH_DEFAULT = 0.50
HOSTILE_CONTACT_IMPEDANCE_RADIUS_MULTIPLIER_DEFAULT = 1.50
HOSTILE_CONTACT_IMPEDANCE_V2_RADIUS_MULTIPLIER_DEFAULT = 1.50
HOSTILE_CONTACT_IMPEDANCE_V2_REPULSION_MAX_DISP_RATIO_DEFAULT = 0.20
HOSTILE_CONTACT_IMPEDANCE_V2_FORWARD_DAMPING_STRENGTH_DEFAULT = 0.50
HOSTILE_SPACING_FLOOR_SCALE_DEFAULT = 0.00
HOSTILE_SPACING_FLOOR_STRENGTH_DEFAULT = 0.00
HOSTILE_SPACING_FLOOR_V2_SCALE_DEFAULT = 0.00
HOSTILE_SPACING_FLOOR_V2_STRENGTH_DEFAULT = 0.00
HOSTILE_SPACING_CO_RESOLUTION_SCALE_DEFAULT = 0.00
HOSTILE_SPACING_CO_RESOLUTION_STRENGTH_DEFAULT = 0.00
HOSTILE_GATED_COHERENCE_REGULARIZATION_SCALE_DEFAULT = 0.00
HOSTILE_GATED_COHERENCE_REGULARIZATION_STRENGTH_DEFAULT = 0.00
HOSTILE_INTENT_UNIFIED_SPACING_SCALE_DEFAULT = 1.00
HOSTILE_INTENT_UNIFIED_SPACING_STRENGTH_DEFAULT = 1.00
HOSTILE_INTENT_OCCUPANCY_ONLY_SCALE_DEFAULT = 1.00
HOSTILE_INTENT_OCCUPANCY_ONLY_STRENGTH_DEFAULT = 1.00
CONTINUOUS_FR_SHAPING_OFF = "off"
CONTINUOUS_FR_SHAPING_CANDIDATE_A = "candidate_a"
CONTINUOUS_FR_SHAPING_CANDIDATE_B = "candidate_b"
CONTINUOUS_FR_SHAPING_CANDIDATE_C = "candidate_c"
CONTINUOUS_FR_SHAPING_LABELS = {
    CONTINUOUS_FR_SHAPING_OFF,
    CONTINUOUS_FR_SHAPING_CANDIDATE_A,
    CONTINUOUS_FR_SHAPING_CANDIDATE_B,
    CONTINUOUS_FR_SHAPING_CANDIDATE_C,
}
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
    "movement_v3a_experiment": ("movement", "v3a", "test_only", "experiment"),
    "centroid_probe_scale": ("movement", "v3a", "test_only", "centroid_probe_scale"),
    "pre_tl_target_substrate": ("movement", "v3a", "test_only", "pre_tl_target_substrate"),
    "odw_posture_bias_enabled": ("movement", "v3a", "test_only", "odw_posture_bias", "enabled"),
    "odw_posture_bias_k": ("movement", "v3a", "test_only", "odw_posture_bias", "k"),
    "odw_posture_bias_clip_delta": ("movement", "v3a", "test_only", "odw_posture_bias", "clip_delta"),
    "symmetric_movement_sync_enabled": ("movement", "v3a", "test_only", "symmetric_movement_sync_enabled"),
    "continuous_fr_shaping_enabled": ("movement", "v3a", "test_only", "continuous_fr_shaping", "enabled"),
    "continuous_fr_shaping_mode": ("movement", "v3a", "test_only", "continuous_fr_shaping", "mode"),
    "continuous_fr_shaping_a": ("movement", "v3a", "test_only", "continuous_fr_shaping", "a"),
    "continuous_fr_shaping_sigma": ("movement", "v3a", "test_only", "continuous_fr_shaping", "sigma"),
    "continuous_fr_shaping_p": ("movement", "v3a", "test_only", "continuous_fr_shaping", "p"),
    "continuous_fr_shaping_q": ("movement", "v3a", "test_only", "continuous_fr_shaping", "q"),
    "continuous_fr_shaping_beta": ("movement", "v3a", "test_only", "continuous_fr_shaping", "beta"),
    "continuous_fr_shaping_gamma": ("movement", "v3a", "test_only", "continuous_fr_shaping", "gamma"),
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
        get_runtime_metatype_setting(settings, "settings_path", DEFAULT_METATYPE_SETTINGS_PATH)
    )
    metatype_path = resolve_optional_json_path(base_dir, configured_path, DEFAULT_METATYPE_SETTINGS_PATH)
    if not metatype_path.exists():
        return {}
    data = load_json_file(metatype_path)
    if isinstance(data, dict):
        return data
    return {}


def _clamp01(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return value


def _sigmoid(value: float) -> float:
    if value >= 0.0:
        z = math.exp(-value)
        return 1.0 / (1.0 + z)
    z = math.exp(value)
    return z / (1.0 + z)


def _continuous_fr_midband_gate(kappa: float, sigma: float) -> float:
    sigma_eff = max(1e-6, float(sigma))
    delta = float(kappa) - 0.5
    exponent = -((delta * delta) / (2.0 * sigma_eff * sigma_eff))
    return math.exp(exponent)


def _compute_continuous_fr_shaping(
    *,
    mode: str,
    kappa: float,
    pd_norm: float,
    engaged_fraction: float,
    mobility_raw: float,
    a: float,
    sigma: float,
    p: float,
    q: float,
    beta: float,
    gamma: float,
) -> dict[str, float | bool | str]:
    mode_effective = str(mode).strip().lower()
    kappa_base = _clamp01(float(kappa))
    pd_norm_base = _clamp01(float(pd_norm))
    engaged_fraction_base = _clamp01(float(engaged_fraction))
    precontact_gate = _clamp01(1.0 - engaged_fraction_base)
    influence = 0.0
    midband_gate = _continuous_fr_midband_gate(kappa_base, sigma)
    pd_factor = pd_norm_base ** max(0.0, float(p))
    precontact_factor = precontact_gate ** max(0.0, float(q))
    mb_taper = 1.0
    pd_shoulder = pd_factor

    if mode_effective == CONTINUOUS_FR_SHAPING_CANDIDATE_A:
        influence = float(a) * midband_gate * pd_factor * precontact_factor
    elif mode_effective == CONTINUOUS_FR_SHAPING_CANDIDATE_B:
        mb_taper = 1.0 / (1.0 + math.exp(max(0.0, float(beta)) * (float(mobility_raw) - 5.0)))
        influence = float(a) * midband_gate * pd_factor * precontact_factor * mb_taper
    elif mode_effective == CONTINUOUS_FR_SHAPING_CANDIDATE_C:
        mb_taper = 1.0 / (1.0 + math.exp(max(0.0, float(beta)) * (float(mobility_raw) - 5.0)))
        pd_shoulder = _sigmoid(max(0.0, float(gamma)) * (pd_norm_base - 0.5))
        influence = float(a) * midband_gate * pd_shoulder * precontact_factor * mb_taper

    influence = _clamp01(influence)
    attenuation = _clamp01(1.0 - influence)
    return {
        "mode": mode_effective,
        "active": mode_effective in CONTINUOUS_FR_SHAPING_LABELS and mode_effective != CONTINUOUS_FR_SHAPING_OFF,
        "kappa_base": kappa_base,
        "kappa_eff": kappa_base * attenuation,
        "attenuation": attenuation,
        "influence": influence,
        "midband_gate": midband_gate,
        "pd_factor": pd_factor,
        "pd_shoulder": pd_shoulder,
        "precontact_factor": precontact_factor,
        "mb_taper": mb_taper,
        "engaged_fraction": engaged_fraction_base,
        "pd_norm": pd_norm_base,
        "mobility_raw": float(mobility_raw),
    }


def _compute_hostile_intermix_metrics(
    state: BattleState,
    separation_radius: float,
) -> dict[str, float]:
    alive_units = [
        unit for unit in state.units.values() if float(unit.hit_points) > 0.0
    ]
    if len(alive_units) <= 1 or separation_radius <= 1e-12:
        return {
            "hostile_overlap_pairs": 0.0,
            "hostile_deep_pairs": 0.0,
            "hostile_deep_intermix_ratio": 0.0,
            "hostile_intermix_severity": 0.0,
            "hostile_intermix_coverage": 0.0,
        }

    alive_counts_by_fleet: dict[str, int] = {}
    overlapped_units_by_fleet: dict[str, set[str]] = {}
    for unit in alive_units:
        fleet_id = str(unit.fleet_id)
        alive_counts_by_fleet[fleet_id] = alive_counts_by_fleet.get(fleet_id, 0) + 1
        overlapped_units_by_fleet.setdefault(fleet_id, set())
    overlap_pairs = 0
    deep_pairs = 0
    severity_sum = 0.0
    deep_threshold = 0.5 * float(separation_radius)
    radius_sq = float(separation_radius) * float(separation_radius)
    for i in range(len(alive_units)):
        unit_i = alive_units[i]
        for j in range(i + 1, len(alive_units)):
            unit_j = alive_units[j]
            if unit_i.fleet_id == unit_j.fleet_id:
                continue
            dx = float(unit_i.position.x) - float(unit_j.position.x)
            dy = float(unit_i.position.y) - float(unit_j.position.y)
            distance_sq = (dx * dx) + (dy * dy)
            if distance_sq >= radius_sq:
                continue
            distance = math.sqrt(max(0.0, distance_sq))
            overlap_pairs += 1
            overlapped_units_by_fleet.setdefault(str(unit_i.fleet_id), set()).add(str(unit_i.unit_id))
            overlapped_units_by_fleet.setdefault(str(unit_j.fleet_id), set()).add(str(unit_j.unit_id))
            if distance < deep_threshold:
                deep_pairs += 1
            penetration = _clamp01((float(separation_radius) - distance) / float(separation_radius))
            severity_sum += penetration * penetration

    coverage_components: list[float] = []
    for fleet_id, alive_count in alive_counts_by_fleet.items():
        if alive_count <= 0:
            continue
        overlapped_count = len(overlapped_units_by_fleet.get(fleet_id, set()))
        coverage_components.append(float(overlapped_count) / float(alive_count))

    return {
        "hostile_overlap_pairs": float(overlap_pairs),
        "hostile_deep_pairs": float(deep_pairs),
        "hostile_deep_intermix_ratio": float(deep_pairs) / float(max(1, overlap_pairs)),
        "hostile_intermix_severity": severity_sum / float(max(1, overlap_pairs)),
        "hostile_intermix_coverage": (
            sum(coverage_components) / float(len(coverage_components))
            if coverage_components
            else 0.0
        ),
    }


class FormationRigidityFirstReadProxy:
    def __init__(self, base_parameters: PersonalityParameters, kappa_eff: float) -> None:
        self._base_parameters = base_parameters
        self._kappa_eff = _clamp01(float(kappa_eff))
        self._first_normalized_pending = True

    def normalized(self) -> dict[str, float]:
        normalized = dict(self._base_parameters.normalized())
        if self._first_normalized_pending:
            normalized["formation_rigidity"] = self._kappa_eff
            self._first_normalized_pending = False
        return normalized

    def __getattr__(self, name: str):
        return getattr(self._base_parameters, name)


class TestModeEngineTickSkeleton(EngineTickSkeleton):
    @staticmethod
    def _compute_position_centroid(units: Sequence[UnitState]) -> tuple[float, float]:
        if not units:
            return 0.0, 0.0
        inv_n = 1.0 / float(len(units))
        return (
            sum(unit.position.x for unit in units) * inv_n,
            sum(unit.position.y for unit in units) * inv_n,
        )

    @staticmethod
    def _normalize_direction(dx: float, dy: float) -> tuple[tuple[float, float], float]:
        norm = math.sqrt((dx * dx) + (dy * dy))
        if norm > 0.0:
            return (dx / norm, dy / norm), 1.0
        return (0.0, 0.0), 0.0

    def _evaluate_target_with_pre_tl_substrate(self, state: BattleState) -> BattleState:
        substrate = str(
            getattr(self, "PRE_TL_TARGET_SUBSTRATE", PRE_TL_TARGET_SUBSTRATE_DEFAULT)
        ).strip().lower()
        if substrate not in PRE_TL_TARGET_SUBSTRATE_LABELS:
            substrate = PRE_TL_TARGET_SUBSTRATE_DEFAULT

        last_target_direction = {}
        last_engagement_intensity = {}

        for fleet_id, fleet in state.fleets.items():
            own_units = [
                state.units[uid]
                for uid in fleet.unit_ids
                if uid in state.units and float(state.units[uid].hit_points) > 0.0
            ]
            enemy_units = [
                unit
                for unit in state.units.values()
                if unit.fleet_id != fleet_id and float(unit.hit_points) > 0.0
            ]

            if not own_units or not enemy_units:
                last_target_direction[fleet_id] = (0.0, 0.0)
                last_engagement_intensity[fleet_id] = 0.0
                continue

            centroid_x, centroid_y = self._compute_position_centroid(own_units)

            def _distance_sq(unit: UnitState) -> float:
                dx = unit.position.x - centroid_x
                dy = unit.position.y - centroid_y
                return (dx * dx) + (dy * dy)

            sorted_enemy_units = sorted(enemy_units, key=_distance_sq)

            if substrate == PRE_TL_TARGET_SUBSTRATE_NEAREST5:
                reference_units = sorted_enemy_units[: min(5, len(sorted_enemy_units))]
                ref_x, ref_y = self._compute_position_centroid(reference_units)
            elif substrate in {
                PRE_TL_TARGET_SUBSTRATE_SOFT_LOCAL_WEIGHTED,
                PRE_TL_TARGET_SUBSTRATE_SOFT_LOCAL_WEIGHTED_TIGHT,
            }:
                local_units = sorted_enemy_units[: min(8, len(sorted_enemy_units))]
                if not local_units:
                    local_units = sorted_enemy_units[:1]
                distances = [math.sqrt(max(0.0, _distance_sq(unit))) for unit in local_units]
                local_scale = max(1.0, sum(distances) / float(len(distances)))
                boundary_index = min(4, len(distances) - 1)
                boundary_distance = max(1e-9, distances[boundary_index])
                envelope_factor = 0.20 if substrate == PRE_TL_TARGET_SUBSTRATE_SOFT_LOCAL_WEIGHTED_TIGHT else 0.35
                envelope_width = max(0.5, local_scale * envelope_factor)
                weight_sum = 0.0
                ref_x = 0.0
                ref_y = 0.0
                for unit, distance in zip(local_units, distances, strict=False):
                    radial_weight = math.exp(-((distance / local_scale) ** 2))
                    envelope_weight = 1.0 / (
                        1.0 + math.exp((distance - boundary_distance) / envelope_width)
                    )
                    weight = radial_weight * envelope_weight
                    ref_x += unit.position.x * weight
                    ref_y += unit.position.y * weight
                    weight_sum += weight
                if weight_sum > 0.0:
                    ref_x /= weight_sum
                    ref_y /= weight_sum
                else:
                    ref_x, ref_y = self._compute_position_centroid(local_units)
            elif substrate == PRE_TL_TARGET_SUBSTRATE_WEIGHTED_LOCAL:
                local_units = sorted_enemy_units[: min(8, len(sorted_enemy_units))]
                if not local_units:
                    local_units = sorted_enemy_units[:1]
                distances = [math.sqrt(max(0.0, _distance_sq(unit))) for unit in local_units]
                local_scale = max(1.0, sum(distances) / float(len(distances)))
                weight_sum = 0.0
                ref_x = 0.0
                ref_y = 0.0
                for unit, distance in zip(local_units, distances, strict=False):
                    weight = math.exp(-((distance / local_scale) ** 2))
                    ref_x += unit.position.x * weight
                    ref_y += unit.position.y * weight
                    weight_sum += weight
                if weight_sum > 0.0:
                    ref_x /= weight_sum
                    ref_y /= weight_sum
                else:
                    ref_x, ref_y = self._compute_position_centroid(local_units)
            else:
                local_units = sorted_enemy_units[: min(8, len(sorted_enemy_units))]
                if not local_units:
                    local_units = sorted_enemy_units[:1]
                cluster_size = min(3, len(local_units))
                best_cluster_score = None
                best_cluster_units = local_units[:cluster_size]
                for anchor in local_units:
                    cluster_units = sorted(
                        local_units,
                        key=lambda candidate: (
                            (candidate.position.x - anchor.position.x) ** 2
                            + (candidate.position.y - anchor.position.y) ** 2
                        ),
                    )[:cluster_size]
                    cluster_centroid_x, cluster_centroid_y = self._compute_position_centroid(cluster_units)
                    cluster_score = sum(
                        ((unit.position.x - cluster_centroid_x) ** 2)
                        + ((unit.position.y - cluster_centroid_y) ** 2)
                        for unit in cluster_units
                    ) / float(cluster_size)
                    if best_cluster_score is None or cluster_score < best_cluster_score:
                        best_cluster_score = cluster_score
                        best_cluster_units = cluster_units
                ref_x, ref_y = self._compute_position_centroid(best_cluster_units)

            direction, intensity = self._normalize_direction(ref_x - centroid_x, ref_y - centroid_y)
            last_target_direction[fleet_id] = direction
            last_engagement_intensity[fleet_id] = intensity

        return replace(
            state,
            last_target_direction=last_target_direction,
            last_engagement_intensity=last_engagement_intensity,
        )

    def evaluate_target(self, state: BattleState) -> BattleState:
        return self._evaluate_target_with_pre_tl_substrate(state)

    def _integrate_movement_symmetric_merge(self, state: BattleState) -> BattleState:
        fleet_ids = list(state.fleets.keys())
        if len(fleet_ids) <= 1:
            return self.integrate_movement(state)

        base_fleets = state.fleets
        merged_units = dict(state.units)
        first_debug_snapshot = None
        for lead_fleet_id in fleet_ids:
            ordered_fleets = {lead_fleet_id: base_fleets[lead_fleet_id]}
            for other_fleet_id in fleet_ids:
                if other_fleet_id != lead_fleet_id:
                    ordered_fleets[other_fleet_id] = base_fleets[other_fleet_id]
            moved_variant = self.integrate_movement(replace(state, fleets=ordered_fleets))
            if first_debug_snapshot is None:
                first_debug_snapshot = {
                    "debug_diag_last_tick": getattr(self, "debug_diag_last_tick", None),
                    "debug_last_cohesion_v3": getattr(self, "debug_last_cohesion_v3", None),
                    "debug_last_cohesion_v3_components": getattr(self, "debug_last_cohesion_v3_components", None),
                }
            for unit_id in base_fleets[lead_fleet_id].unit_ids:
                moved_unit = moved_variant.units.get(unit_id)
                if moved_unit is not None:
                    merged_units[unit_id] = moved_unit
        if first_debug_snapshot is not None:
            self.debug_diag_last_tick = first_debug_snapshot["debug_diag_last_tick"]
            self.debug_last_cohesion_v3 = first_debug_snapshot["debug_last_cohesion_v3"]
            self.debug_last_cohesion_v3_components = first_debug_snapshot["debug_last_cohesion_v3_components"]
        return replace(state, units=merged_units)

    @staticmethod
    def _stable_pair_direction(unit_i: str, unit_j: str) -> tuple[float, float]:
        low, high = (unit_i, unit_j) if unit_i < unit_j else (unit_j, unit_i)
        acc_x = 0
        acc_y = 0
        for idx, ch in enumerate(low + "|" + high, start=1):
            code = ord(ch)
            acc_x = (acc_x * 131) + (code * idx)
            acc_y = (acc_y * 137) + (code * (idx + 17))
        sx = float((acc_x % 1024) - 512)
        sy = float((acc_y % 1024) - 512)
        if sx == 0.0 and sy == 0.0:
            sy = 1.0
        norm = math.sqrt((sx * sx) + (sy * sy))
        return (sx / norm, sy / norm)

    def _resolve_hostile_contact_impedance_mode(self) -> str:
        raw_mode = str(
            getattr(
                self,
                "HOSTILE_CONTACT_IMPEDANCE_MODE",
                HOSTILE_CONTACT_IMPEDANCE_MODE_DEFAULT,
            )
        ).strip().lower()
        if raw_mode not in HOSTILE_CONTACT_IMPEDANCE_MODE_LABELS:
            raw_mode = HOSTILE_CONTACT_IMPEDANCE_MODE_DEFAULT
        return raw_mode

    def _compute_fleet_enemy_axes(self, state: BattleState) -> dict[str, tuple[float, float]]:
        axes: dict[str, tuple[float, float]] = {}
        fleet_centroids: dict[str, tuple[float, float]] = {}
        for fleet_id, fleet in state.fleets.items():
            alive_units = [
                state.units[uid]
                for uid in fleet.unit_ids
                if uid in state.units and float(state.units[uid].hit_points) > 0.0
            ]
            fleet_centroids[fleet_id] = self._compute_position_centroid(alive_units)
        for fleet_id, (cx, cy) in fleet_centroids.items():
            enemy_centroids = [
                pos for other_fleet_id, pos in fleet_centroids.items() if other_fleet_id != fleet_id
            ]
            if not enemy_centroids:
                axes[fleet_id] = (0.0, 0.0)
                continue
            enemy_cx = sum(pos[0] for pos in enemy_centroids) / float(len(enemy_centroids))
            enemy_cy = sum(pos[1] for pos in enemy_centroids) / float(len(enemy_centroids))
            axis, _ = self._normalize_direction(enemy_cx - cx, enemy_cy - cy)
            axes[fleet_id] = axis
        return axes

    def _compute_unit_hostile_proximity(
        self,
        state: BattleState,
        impedance_radius: float,
    ) -> tuple[dict[str, float], dict[str, list[tuple[str, float, float, float, float]]]]:
        alive_units = [
            unit for unit in state.units.values() if float(unit.hit_points) > 0.0
        ]
        proximity_by_unit = {unit.unit_id: 0.0 for unit in alive_units}
        pair_terms_by_unit = {unit.unit_id: [] for unit in alive_units}
        radius_sq = impedance_radius * impedance_radius
        for i in range(len(alive_units)):
            unit_i = alive_units[i]
            for j in range(i + 1, len(alive_units)):
                unit_j = alive_units[j]
                if unit_i.fleet_id == unit_j.fleet_id:
                    continue
                dx = float(unit_i.position.x) - float(unit_j.position.x)
                dy = float(unit_i.position.y) - float(unit_j.position.y)
                distance_sq = (dx * dx) + (dy * dy)
                if distance_sq > radius_sq:
                    continue
                if distance_sq > 1e-12:
                    distance = math.sqrt(distance_sq)
                    nx = dx / distance
                    ny = dy / distance
                else:
                    nx, ny = self._stable_pair_direction(unit_i.unit_id, unit_j.unit_id)
                    distance = 0.0
                proximity = _clamp01(1.0 - (distance / impedance_radius))
                weight = proximity * proximity
                proximity_by_unit[unit_i.unit_id] = _clamp01(proximity_by_unit[unit_i.unit_id] + weight)
                proximity_by_unit[unit_j.unit_id] = _clamp01(proximity_by_unit[unit_j.unit_id] + weight)
                pair_terms_by_unit[unit_i.unit_id].append((unit_j.unit_id, nx, ny, proximity, weight))
                pair_terms_by_unit[unit_j.unit_id].append((unit_i.unit_id, -nx, -ny, proximity, weight))
        return proximity_by_unit, pair_terms_by_unit

    @staticmethod
    def _hostile_spacing_depth(distance: float, envelope_radius: float) -> float:
        if envelope_radius <= 1e-12:
            return 0.0
        return _clamp01((envelope_radius - distance) / envelope_radius)

    def _compute_hostile_spacing_value(
        self,
        state: BattleState,
        *,
        own_fleet_id: str,
        x: float,
        y: float,
        envelope_radius: float,
    ) -> float:
        if envelope_radius <= 1e-12:
            return 0.0
        remaining_clearance = 1.0
        radius_sq = envelope_radius * envelope_radius
        for unit in state.units.values():
            if unit.fleet_id == own_fleet_id or float(unit.hit_points) <= 0.0:
                continue
            dx = x - float(unit.position.x)
            dy = y - float(unit.position.y)
            distance_sq = (dx * dx) + (dy * dy)
            if distance_sq >= radius_sq:
                continue
            distance = math.sqrt(max(0.0, distance_sq))
            depth = self._hostile_spacing_depth(distance, envelope_radius)
            if depth <= 0.0:
                continue
            remaining_clearance *= (1.0 - (depth * depth))
            if remaining_clearance <= 1e-9:
                return 1.0
        return _clamp01(1.0 - remaining_clearance)

    def _apply_hostile_intent_penetration_bias(self, state: BattleState) -> BattleState:
        mode = self._resolve_hostile_contact_impedance_mode()
        if mode not in {
            HOSTILE_CONTACT_IMPEDANCE_MODE_INTENT_UNIFIED_SPACING_V1,
            HOSTILE_CONTACT_IMPEDANCE_MODE_INTENT_OCCUPANCY_ONLY_V1,
        }:
            return state

        if mode == HOSTILE_CONTACT_IMPEDANCE_MODE_INTENT_UNIFIED_SPACING_V1:
            scale = max(
                1e-6,
                float(
                    getattr(
                        self,
                        "HOSTILE_INTENT_UNIFIED_SPACING_SCALE",
                        HOSTILE_INTENT_UNIFIED_SPACING_SCALE_DEFAULT,
                    )
                ),
            )
            strength = _clamp01(
                float(
                    getattr(
                        self,
                        "HOSTILE_INTENT_UNIFIED_SPACING_STRENGTH",
                        HOSTILE_INTENT_UNIFIED_SPACING_STRENGTH_DEFAULT,
                    )
                )
            )
        else:
            scale = max(
                1e-6,
                float(
                    getattr(
                        self,
                        "HOSTILE_INTENT_OCCUPANCY_ONLY_SCALE",
                        HOSTILE_INTENT_OCCUPANCY_ONLY_SCALE_DEFAULT,
                    )
                ),
            )
            strength = _clamp01(
                float(
                    getattr(
                        self,
                        "HOSTILE_INTENT_OCCUPANCY_ONLY_STRENGTH",
                        HOSTILE_INTENT_OCCUPANCY_ONLY_STRENGTH_DEFAULT,
                    )
                )
            )

        envelope_radius = scale * float(self.separation_radius)
        alive_units = [unit for unit in state.units.values() if float(unit.hit_points) > 0.0]
        if len(alive_units) <= 1 or envelope_radius <= 1e-12 or strength <= 0.0:
            self.debug_last_hostile_contact_impedance = {
                "mode": mode,
                "enabled": True,
                "active": False,
                "layer": "intent",
                "radius": envelope_radius,
                "mean_signal": 0.0,
                "mean_speed_scale": 1.0,
                "strength": strength,
            }
            return state

        fallback_axes = self._compute_fleet_enemy_axes(state)
        updated_units = dict(state.units)
        signal_sum = 0.0
        speed_scale_sum = 0.0
        active_count = 0
        for unit in alive_units:
            pre_x = float(unit.position.x)
            pre_y = float(unit.position.y)
            pre_occ = self._compute_hostile_spacing_value(
                state,
                own_fleet_id=unit.fleet_id,
                x=pre_x,
                y=pre_y,
                envelope_radius=envelope_radius,
            )
            if mode == HOSTILE_CONTACT_IMPEDANCE_MODE_INTENT_OCCUPANCY_ONLY_V1:
                signal = pre_occ
            else:
                dir_x, dir_y = state.last_target_direction.get(unit.fleet_id, (0.0, 0.0))
                dir_norm = math.sqrt((dir_x * dir_x) + (dir_y * dir_y))
                if dir_norm <= 1e-12:
                    dir_x, dir_y = fallback_axes.get(unit.fleet_id, (0.0, 0.0))
                    dir_norm = math.sqrt((dir_x * dir_x) + (dir_y * dir_y))
                if dir_norm > 1e-12:
                    dir_x /= dir_norm
                    dir_y /= dir_norm
                projected_x = pre_x + (dir_x * float(unit.max_speed) * float(state.dt))
                projected_y = pre_y + (dir_y * float(unit.max_speed) * float(state.dt))
                post_occ = self._compute_hostile_spacing_value(
                    state,
                    own_fleet_id=unit.fleet_id,
                    x=projected_x,
                    y=projected_y,
                    envelope_radius=envelope_radius,
                )
                signal = max(0.0, post_occ - pre_occ)
            speed_scale = 1.0 - (strength * signal)
            if speed_scale < 0.0:
                speed_scale = 0.0
            if speed_scale >= 0.999999:
                continue
            updated_units[unit.unit_id] = replace(unit, max_speed=float(unit.max_speed) * speed_scale)
            signal_sum += signal
            speed_scale_sum += speed_scale
            active_count += 1

        self.debug_last_hostile_contact_impedance = {
            "mode": mode,
            "enabled": True,
            "active": active_count > 0,
            "layer": "intent",
            "radius": envelope_radius,
            "mean_signal": (signal_sum / float(active_count)) if active_count > 0 else 0.0,
            "mean_speed_scale": (speed_scale_sum / float(active_count)) if active_count > 0 else 1.0,
            "strength": strength,
        }
        return replace(state, units=updated_units)

    def _restore_intent_penetration_bias_units(
        self,
        reference_state: BattleState,
        moved_state: BattleState,
    ) -> BattleState:
        mode = self._resolve_hostile_contact_impedance_mode()
        if mode not in {
            HOSTILE_CONTACT_IMPEDANCE_MODE_INTENT_UNIFIED_SPACING_V1,
            HOSTILE_CONTACT_IMPEDANCE_MODE_INTENT_OCCUPANCY_ONLY_V1,
        }:
            return moved_state

        updated_units = dict(moved_state.units)
        changed = False
        for unit_id, unit in moved_state.units.items():
            reference_unit = reference_state.units.get(unit_id)
            if reference_unit is None:
                continue
            if float(unit.max_speed) == float(reference_unit.max_speed):
                continue
            updated_units[unit_id] = replace(unit, max_speed=float(reference_unit.max_speed))
            changed = True
        if not changed:
            return moved_state
        return replace(moved_state, units=updated_units)

    def _apply_hostile_contact_impedance_v1(self, state: BattleState) -> BattleState:
        strength = max(
            0.0,
            float(
                getattr(
                    self,
                    "HOSTILE_CONTACT_IMPEDANCE_STRENGTH",
                    HOSTILE_CONTACT_IMPEDANCE_STRENGTH_DEFAULT,
                )
            ),
        )
        radius_multiplier = max(
            1e-6,
            float(
                getattr(
                    self,
                    "HOSTILE_CONTACT_IMPEDANCE_RADIUS_MULTIPLIER",
                    HOSTILE_CONTACT_IMPEDANCE_RADIUS_MULTIPLIER_DEFAULT,
                )
            ),
        )
        impedance_radius = float(self.separation_radius) * radius_multiplier
        if strength <= 0.0 or impedance_radius <= 1e-12:
            self.debug_last_hostile_contact_impedance = {
                "mode": HOSTILE_CONTACT_IMPEDANCE_MODE_REPULSION_V1,
                "active": False,
                "pair_count": 0,
                "radius": impedance_radius,
                "strength": strength,
                "mean_displacement": 0.0,
                "max_displacement": 0.0,
            }
            return state

        alive_units = [
            unit for unit in state.units.values() if float(unit.hit_points) > 0.0
        ]
        if len(alive_units) <= 1:
            self.debug_last_hostile_contact_impedance = {
                "mode": HOSTILE_CONTACT_IMPEDANCE_MODE_REPULSION_V1,
                "active": False,
                "pair_count": 0,
                "radius": impedance_radius,
                "strength": strength,
                "mean_displacement": 0.0,
                "max_displacement": 0.0,
            }
            return state

        radius_sq = impedance_radius * impedance_radius
        delta = {unit.unit_id: [0.0, 0.0] for unit in alive_units}
        pair_count = 0
        for i in range(len(alive_units)):
            unit_i = alive_units[i]
            for j in range(i + 1, len(alive_units)):
                unit_j = alive_units[j]
                if unit_i.fleet_id == unit_j.fleet_id:
                    continue
                dx = float(unit_i.position.x) - float(unit_j.position.x)
                dy = float(unit_i.position.y) - float(unit_j.position.y)
                distance_sq = (dx * dx) + (dy * dy)
                if distance_sq > radius_sq:
                    continue
                pair_count += 1
                if distance_sq > 1e-12:
                    distance = math.sqrt(distance_sq)
                    nx = dx / distance
                    ny = dy / distance
                else:
                    nx, ny = self._stable_pair_direction(unit_i.unit_id, unit_j.unit_id)
                    distance = 0.0
                proximity = 1.0 - (distance / impedance_radius)
                if proximity <= 0.0:
                    continue
                correction_mag = 0.25 * float(self.separation_radius) * strength * (proximity * proximity)
                correction_x = nx * correction_mag
                correction_y = ny * correction_mag
                delta[unit_i.unit_id][0] += 0.5 * correction_x
                delta[unit_i.unit_id][1] += 0.5 * correction_y
                delta[unit_j.unit_id][0] -= 0.5 * correction_x
                delta[unit_j.unit_id][1] -= 0.5 * correction_y

        updated_units = dict(state.units)
        displacement_sum = 0.0
        displacement_max = 0.0
        displacement_count = 0
        max_unit_displacement = 0.35 * float(self.separation_radius) * strength
        for unit in alive_units:
            dx, dy = delta[unit.unit_id]
            disp = math.sqrt((dx * dx) + (dy * dy))
            if disp > max_unit_displacement > 0.0:
                scale = max_unit_displacement / disp
                dx *= scale
                dy *= scale
                disp = max_unit_displacement
            if disp <= 0.0:
                continue
            displacement_sum += disp
            displacement_count += 1
            if disp > displacement_max:
                displacement_max = disp
            new_position = Vec2(x=float(unit.position.x) + dx, y=float(unit.position.y) + dy)
            updated_units[unit.unit_id] = replace(unit, position=new_position)

        self.debug_last_hostile_contact_impedance = {
            "mode": HOSTILE_CONTACT_IMPEDANCE_MODE_REPULSION_V1,
            "active": pair_count > 0,
            "pair_count": pair_count,
            "radius": impedance_radius,
            "strength": strength,
            "mean_displacement": (displacement_sum / displacement_count) if displacement_count > 0 else 0.0,
            "max_displacement": displacement_max,
        }
        return replace(state, units=updated_units)

    def _apply_hostile_contact_impedance_v2(
        self,
        pre_state: BattleState,
        moved_state: BattleState,
        *,
        mode: str,
    ) -> BattleState:
        radius_multiplier = max(
            1e-6,
            float(
                getattr(
                    self,
                    "HOSTILE_CONTACT_IMPEDANCE_V2_RADIUS_MULTIPLIER",
                    HOSTILE_CONTACT_IMPEDANCE_V2_RADIUS_MULTIPLIER_DEFAULT,
                )
            ),
        )
        repulsion_max_disp_ratio = max(
            0.0,
            float(
                getattr(
                    self,
                    "HOSTILE_CONTACT_IMPEDANCE_V2_REPULSION_MAX_DISP_RATIO",
                    HOSTILE_CONTACT_IMPEDANCE_V2_REPULSION_MAX_DISP_RATIO_DEFAULT,
                )
            ),
        )
        forward_damping_strength = _clamp01(
            float(
                getattr(
                    self,
                    "HOSTILE_CONTACT_IMPEDANCE_V2_FORWARD_DAMPING_STRENGTH",
                    HOSTILE_CONTACT_IMPEDANCE_V2_FORWARD_DAMPING_STRENGTH_DEFAULT,
                )
            )
        )
        impedance_radius = float(self.separation_radius) * radius_multiplier
        if impedance_radius <= 1e-12:
            self.debug_last_hostile_contact_impedance = {
                "mode": mode,
                "enabled": False,
                "active": False,
                "pair_count": 0,
                "radius": impedance_radius,
                "mean_proximity": 0.0,
                "mean_forward_damping": 0.0,
                "mean_repulsion_displacement": 0.0,
                "max_repulsion_displacement": 0.0,
            }
            return moved_state

        alive_units = [
            unit for unit in moved_state.units.values() if float(unit.hit_points) > 0.0
        ]
        if len(alive_units) <= 1:
            self.debug_last_hostile_contact_impedance = {
                "mode": mode,
                "enabled": True,
                "active": False,
                "pair_count": 0,
                "radius": impedance_radius,
                "mean_proximity": 0.0,
                "mean_forward_damping": 0.0,
                "mean_repulsion_displacement": 0.0,
                "max_repulsion_displacement": 0.0,
            }
            return moved_state

        fleet_axes = self._compute_fleet_enemy_axes(moved_state)
        proximity_by_unit, pair_terms_by_unit = self._compute_unit_hostile_proximity(moved_state, impedance_radius)
        updated_units = dict(moved_state.units)
        repulsion_sum = 0.0
        repulsion_max = 0.0
        repulsion_count = 0
        damping_sum = 0.0
        damping_count = 0
        max_repulsion_disp = float(self.separation_radius) * repulsion_max_disp_ratio
        pair_count = sum(len(terms) for terms in pair_terms_by_unit.values()) // 2

        for unit in alive_units:
            pre_unit = pre_state.units.get(unit.unit_id)
            if pre_unit is None:
                continue
            axis_x, axis_y = fleet_axes.get(unit.fleet_id, (0.0, 0.0))
            dx_move = float(unit.position.x) - float(pre_unit.position.x)
            dy_move = float(unit.position.y) - float(pre_unit.position.y)
            forward_disp = (dx_move * axis_x) + (dy_move * axis_y)
            residual_x = dx_move
            residual_y = dy_move
            if abs(forward_disp) > 1e-12:
                residual_x -= forward_disp * axis_x
                residual_y -= forward_disp * axis_y

            local_proximity = _clamp01(proximity_by_unit.get(unit.unit_id, 0.0))
            damping_factor = 1.0
            if mode in {
                HOSTILE_CONTACT_IMPEDANCE_MODE_DAMPING_V2,
                HOSTILE_CONTACT_IMPEDANCE_MODE_HYBRID_V2,
            } and forward_disp > 0.0:
                damping_factor = 1.0 - (_clamp01(forward_damping_strength * local_proximity))
                forward_disp *= damping_factor
                damping_sum += (1.0 - damping_factor)
                damping_count += 1

            repulsion_x = 0.0
            repulsion_y = 0.0
            if (
                mode == HOSTILE_CONTACT_IMPEDANCE_MODE_HYBRID_V2
                and max_repulsion_disp > 0.0
                and local_proximity > 0.0
            ):
                for _, nx, ny, _, weight in pair_terms_by_unit.get(unit.unit_id, []):
                    repulsion_x += nx * weight
                    repulsion_y += ny * weight
                repulsion_norm = math.sqrt((repulsion_x * repulsion_x) + (repulsion_y * repulsion_y))
                if repulsion_norm > 1e-12:
                    scale = max_repulsion_disp * local_proximity / repulsion_norm
                    repulsion_x *= scale
                    repulsion_y *= scale
                    repulsion_disp = math.sqrt((repulsion_x * repulsion_x) + (repulsion_y * repulsion_y))
                    repulsion_sum += repulsion_disp
                    repulsion_count += 1
                    if repulsion_disp > repulsion_max:
                        repulsion_max = repulsion_disp

            new_dx = (forward_disp * axis_x) + residual_x + repulsion_x
            new_dy = (forward_disp * axis_y) + residual_y + repulsion_y
            updated_units[unit.unit_id] = replace(
                unit,
                position=Vec2(
                    x=float(pre_unit.position.x) + new_dx,
                    y=float(pre_unit.position.y) + new_dy,
                ),
            )

        self.debug_last_hostile_contact_impedance = {
            "mode": mode,
            "enabled": True,
            "active": pair_count > 0,
            "pair_count": pair_count,
            "radius": impedance_radius,
            "mean_proximity": (
                sum(proximity_by_unit.values()) / float(max(1, len(proximity_by_unit)))
            ),
            "mean_forward_damping": (damping_sum / damping_count) if damping_count > 0 else 0.0,
            "mean_repulsion_displacement": (repulsion_sum / repulsion_count) if repulsion_count > 0 else 0.0,
            "max_repulsion_displacement": repulsion_max,
            "repulsion_max_disp_ratio": repulsion_max_disp_ratio,
            "forward_damping_strength": forward_damping_strength,
        }
        return replace(moved_state, units=updated_units)

    def _apply_hostile_spacing_floor_v1(
        self,
        pre_state: BattleState,
        moved_state: BattleState,
    ) -> BattleState:
        scale = max(
            1e-6,
            float(getattr(self, "HOSTILE_SPACING_FLOOR_SCALE", HOSTILE_SPACING_FLOOR_SCALE_DEFAULT)),
        )
        strength = _clamp01(
            float(getattr(self, "HOSTILE_SPACING_FLOOR_STRENGTH", HOSTILE_SPACING_FLOOR_STRENGTH_DEFAULT))
        )
        envelope_radius = scale * float(self.separation_radius)
        alive_units = [unit for unit in moved_state.units.values() if float(unit.hit_points) > 0.0]
        if len(alive_units) <= 1 or envelope_radius <= 1e-12 or strength <= 0.0:
            self.debug_last_hostile_contact_impedance = {
                "mode": HOSTILE_CONTACT_IMPEDANCE_MODE_SPACING_FLOOR_V1,
                "enabled": True,
                "active": False,
                "pair_count": 0,
                "radius": envelope_radius,
                "mean_penetration_delta": 0.0,
                "mean_clip_fraction": 0.0,
                "max_clip_fraction": 0.0,
                "strength": strength,
            }
            return moved_state

        _, pair_terms_by_unit = self._compute_unit_hostile_proximity(moved_state, envelope_radius)
        updated_units = dict(moved_state.units)
        penetration_delta_sum = 0.0
        clip_fraction_sum = 0.0
        clip_fraction_max = 0.0
        active_count = 0
        pair_count = sum(len(terms) for terms in pair_terms_by_unit.values()) // 2
        for unit in alive_units:
            pre_unit = pre_state.units.get(unit.unit_id)
            if pre_unit is None:
                continue
            pre_x = float(pre_unit.position.x)
            pre_y = float(pre_unit.position.y)
            post_x = float(unit.position.x)
            post_y = float(unit.position.y)
            dx_move = post_x - pre_x
            dy_move = post_y - pre_y
            pair_terms = pair_terms_by_unit.get(unit.unit_id, [])
            inward_x = 0.0
            inward_y = 0.0
            total_weight = 0.0
            for _, nx, ny, _, weight in pair_terms:
                inward_x += -nx * weight
                inward_y += -ny * weight
                total_weight += weight
            inward_norm = math.sqrt((inward_x * inward_x) + (inward_y * inward_y))
            if total_weight <= 1e-12 or inward_norm <= 1e-12:
                continue
            inward_x /= inward_norm
            inward_y /= inward_norm
            inward_disp = (dx_move * inward_x) + (dy_move * inward_y)
            if inward_disp <= 1e-12:
                continue
            residual_x = dx_move - (inward_disp * inward_x)
            residual_y = dy_move - (inward_disp * inward_y)

            pre_value = self._compute_hostile_spacing_value(
                moved_state,
                own_fleet_id=unit.fleet_id,
                x=pre_x,
                y=pre_y,
                envelope_radius=envelope_radius,
            )
            post_value = self._compute_hostile_spacing_value(
                moved_state,
                own_fleet_id=unit.fleet_id,
                x=post_x,
                y=post_y,
                envelope_radius=envelope_radius,
            )
            penetration_delta = max(0.0, post_value - pre_value)
            if penetration_delta <= 0.0:
                continue
            target_value = pre_value + ((1.0 - strength) * penetration_delta)
            low = 0.0
            high = 1.0
            for _ in range(12):
                mid = 0.5 * (low + high)
                cand_x = pre_x + residual_x + (inward_x * inward_disp * mid)
                cand_y = pre_y + residual_y + (inward_y * inward_disp * mid)
                cand_value = self._compute_hostile_spacing_value(
                    moved_state,
                    own_fleet_id=unit.fleet_id,
                    x=cand_x,
                    y=cand_y,
                    envelope_radius=envelope_radius,
                )
                if cand_value <= target_value:
                    low = mid
                else:
                    high = mid
            inward_progress = low
            clip_fraction = _clamp01(1.0 - inward_progress)
            new_x = pre_x + residual_x + (inward_x * inward_disp * inward_progress)
            new_y = pre_y + residual_y + (inward_y * inward_disp * inward_progress)
            updated_units[unit.unit_id] = replace(
                unit,
                position=Vec2(x=new_x, y=new_y),
            )
            penetration_delta_sum += penetration_delta
            clip_fraction_sum += clip_fraction
            active_count += 1
            if clip_fraction > clip_fraction_max:
                clip_fraction_max = clip_fraction

        self.debug_last_hostile_contact_impedance = {
            "mode": HOSTILE_CONTACT_IMPEDANCE_MODE_SPACING_FLOOR_V1,
            "enabled": True,
            "active": active_count > 0,
            "pair_count": pair_count,
            "radius": envelope_radius,
            "mean_penetration_delta": (
                penetration_delta_sum / float(active_count)
                if active_count > 0
                else 0.0
            ),
            "mean_clip_fraction": (
                clip_fraction_sum / float(active_count)
                if active_count > 0
                else 0.0
            ),
            "max_clip_fraction": clip_fraction_max,
            "strength": strength,
        }
        return replace(moved_state, units=updated_units)

    def _apply_hostile_spacing_floor_v2(
        self,
        pre_state: BattleState,
        moved_state: BattleState,
    ) -> BattleState:
        scale = max(
            1e-6,
            float(
                getattr(
                    self,
                    "HOSTILE_SPACING_FLOOR_V2_SCALE",
                    HOSTILE_SPACING_FLOOR_V2_SCALE_DEFAULT,
                )
            ),
        )
        strength = _clamp01(
            float(
                getattr(
                    self,
                    "HOSTILE_SPACING_FLOOR_V2_STRENGTH",
                    HOSTILE_SPACING_FLOOR_V2_STRENGTH_DEFAULT,
                )
            )
        )
        envelope_radius = scale * float(self.separation_radius)
        alive_units = [unit for unit in moved_state.units.values() if float(unit.hit_points) > 0.0]
        if len(alive_units) <= 1 or envelope_radius <= 1e-12 or strength <= 0.0:
            self.debug_last_hostile_contact_impedance = {
                "mode": HOSTILE_CONTACT_IMPEDANCE_MODE_SPACING_FLOOR_V2,
                "enabled": True,
                "active": False,
                "pair_count": 0,
                "radius": envelope_radius,
                "mean_penetration_delta": 0.0,
                "mean_resolution_displacement": 0.0,
                "max_resolution_displacement": 0.0,
                "mean_source_count": 0.0,
                "strength": strength,
            }
            return moved_state

        pair_terms_by_unit: dict[str, list[tuple[str, float, float]]] = {}
        pair_count = 0
        radius_sq = envelope_radius * envelope_radius
        for unit in alive_units:
            pair_terms_by_unit[unit.unit_id] = []
        for i in range(len(alive_units)):
            unit_i = alive_units[i]
            for j in range(i + 1, len(alive_units)):
                unit_j = alive_units[j]
                if unit_i.fleet_id == unit_j.fleet_id:
                    continue
                dx = float(unit_i.position.x) - float(unit_j.position.x)
                dy = float(unit_i.position.y) - float(unit_j.position.y)
                distance_sq = (dx * dx) + (dy * dy)
                if distance_sq > radius_sq:
                    continue
                pair_count += 1
                pair_terms_by_unit[unit_i.unit_id].append(
                    (unit_j.unit_id, float(unit_j.position.x), float(unit_j.position.y))
                )
                pair_terms_by_unit[unit_j.unit_id].append(
                    (unit_i.unit_id, float(unit_i.position.x), float(unit_i.position.y))
                )

        updated_units = dict(moved_state.units)
        penetration_delta_sum = 0.0
        resolution_disp_sum = 0.0
        resolution_disp_max = 0.0
        source_count_sum = 0.0
        active_count = 0
        for unit in alive_units:
            pre_unit = pre_state.units.get(unit.unit_id)
            if pre_unit is None:
                continue
            pair_terms = pair_terms_by_unit.get(unit.unit_id, [])
            if not pair_terms:
                continue
            pre_x = float(pre_unit.position.x)
            pre_y = float(pre_unit.position.y)
            cand_x = float(unit.position.x)
            cand_y = float(unit.position.y)
            resolution_x = 0.0
            resolution_y = 0.0
            penetration_delta_total = 0.0
            source_count = 0
            for _ in range(3):
                iter_dx = 0.0
                iter_dy = 0.0
                iter_sources = 0
                for hostile_id, hostile_x, hostile_y in pair_terms:
                    del hostile_id
                    pre_dx = pre_x - hostile_x
                    pre_dy = pre_y - hostile_y
                    pre_dist = math.sqrt((pre_dx * pre_dx) + (pre_dy * pre_dy))
                    pre_depth = self._hostile_spacing_depth(pre_dist, envelope_radius)

                    cand_dx = cand_x - hostile_x
                    cand_dy = cand_y - hostile_y
                    cand_dist = math.sqrt((cand_dx * cand_dx) + (cand_dy * cand_dy))
                    cand_depth = self._hostile_spacing_depth(cand_dist, envelope_radius)
                    penetration_delta = max(0.0, cand_depth - pre_depth)
                    if penetration_delta <= 1e-12:
                        continue
                    if cand_dist > 1e-12:
                        nx = cand_dx / cand_dist
                        ny = cand_dy / cand_dist
                    else:
                        nx, ny = self._stable_pair_direction(unit.unit_id, "hostile")
                    correction_mag = strength * penetration_delta * envelope_radius
                    iter_dx += nx * correction_mag
                    iter_dy += ny * correction_mag
                    penetration_delta_total += penetration_delta
                    iter_sources += 1
                if iter_sources <= 0:
                    break
                cand_x += iter_dx
                cand_y += iter_dy
                resolution_x += iter_dx
                resolution_y += iter_dy
                source_count += iter_sources

            resolution_disp = math.sqrt((resolution_x * resolution_x) + (resolution_y * resolution_y))
            if resolution_disp <= 1e-12 or source_count <= 0:
                continue
            updated_units[unit.unit_id] = replace(
                unit,
                position=Vec2(x=cand_x, y=cand_y),
            )
            penetration_delta_sum += penetration_delta_total / float(max(1, source_count))
            resolution_disp_sum += resolution_disp
            source_count_sum += float(source_count)
            active_count += 1
            if resolution_disp > resolution_disp_max:
                resolution_disp_max = resolution_disp

        self.debug_last_hostile_contact_impedance = {
            "mode": HOSTILE_CONTACT_IMPEDANCE_MODE_SPACING_FLOOR_V2,
            "enabled": True,
            "active": active_count > 0,
            "pair_count": pair_count,
            "radius": envelope_radius,
            "mean_penetration_delta": (
                penetration_delta_sum / float(active_count)
                if active_count > 0
                else 0.0
            ),
            "mean_resolution_displacement": (
                resolution_disp_sum / float(active_count)
                if active_count > 0
                else 0.0
            ),
            "max_resolution_displacement": resolution_disp_max,
            "mean_source_count": (
                source_count_sum / float(active_count)
                if active_count > 0
                else 0.0
            ),
            "strength": strength,
        }
        return replace(moved_state, units=updated_units)

    def _apply_hostile_spacing_co_resolution_v1(
        self,
        pre_state: BattleState,
        moved_state: BattleState,
    ) -> BattleState:
        scale = max(
            1e-6,
            float(
                getattr(
                    self,
                    "HOSTILE_SPACING_CO_RESOLUTION_SCALE",
                    HOSTILE_SPACING_CO_RESOLUTION_SCALE_DEFAULT,
                )
            ),
        )
        strength = _clamp01(
            float(
                getattr(
                    self,
                    "HOSTILE_SPACING_CO_RESOLUTION_STRENGTH",
                    HOSTILE_SPACING_CO_RESOLUTION_STRENGTH_DEFAULT,
                )
            )
        )
        envelope_radius = scale * float(self.separation_radius)
        alive_units = [unit for unit in moved_state.units.values() if float(unit.hit_points) > 0.0]
        if len(alive_units) <= 1 or envelope_radius <= 1e-12 or strength <= 0.0:
            self.debug_last_hostile_contact_impedance = {
                "mode": HOSTILE_CONTACT_IMPEDANCE_MODE_SPACING_CO_RESOLUTION_V1,
                "enabled": True,
                "active": False,
                "hostile_pair_count": 0,
                "friendly_pair_count": 0,
                "radius": envelope_radius,
                "mean_displacement": 0.0,
                "max_displacement": 0.0,
                "strength": strength,
            }
            return moved_state

        delta = {unit.unit_id: [0.0, 0.0] for unit in alive_units}
        hostile_pair_count = 0
        friendly_pair_count = 0
        envelope_radius_sq = envelope_radius * envelope_radius
        local_pair_radius = max(float(self.separation_radius), envelope_radius)
        local_pair_radius_sq = local_pair_radius * local_pair_radius

        for i in range(len(alive_units)):
            unit_i = alive_units[i]
            pre_i = pre_state.units.get(unit_i.unit_id)
            if pre_i is None:
                continue
            for j in range(i + 1, len(alive_units)):
                unit_j = alive_units[j]
                pre_j = pre_state.units.get(unit_j.unit_id)
                if pre_j is None:
                    continue

                post_dx = float(unit_i.position.x) - float(unit_j.position.x)
                post_dy = float(unit_i.position.y) - float(unit_j.position.y)
                post_dist_sq = (post_dx * post_dx) + (post_dy * post_dy)
                pre_dx = float(pre_i.position.x) - float(pre_j.position.x)
                pre_dy = float(pre_i.position.y) - float(pre_j.position.y)
                pre_dist_sq = (pre_dx * pre_dx) + (pre_dy * pre_dy)

                if unit_i.fleet_id != unit_j.fleet_id:
                    if post_dist_sq > envelope_radius_sq and pre_dist_sq > envelope_radius_sq:
                        continue
                    hostile_pair_count += 1
                    post_dist = math.sqrt(max(0.0, post_dist_sq))
                    pre_dist = math.sqrt(max(0.0, pre_dist_sq))
                    pre_depth = self._hostile_spacing_depth(pre_dist, envelope_radius)
                    post_depth = self._hostile_spacing_depth(post_dist, envelope_radius)
                    penetration_delta = max(0.0, post_depth - pre_depth)
                    if penetration_delta <= 1e-12:
                        continue
                    if post_dist > 1e-12:
                        nx = post_dx / post_dist
                        ny = post_dy / post_dist
                    else:
                        nx, ny = self._stable_pair_direction(unit_i.unit_id, unit_j.unit_id)
                    correction_mag = 0.5 * strength * penetration_delta * envelope_radius
                    delta[unit_i.unit_id][0] += nx * correction_mag
                    delta[unit_i.unit_id][1] += ny * correction_mag
                    delta[unit_j.unit_id][0] -= nx * correction_mag
                    delta[unit_j.unit_id][1] -= ny * correction_mag
                    continue

                if post_dist_sq > local_pair_radius_sq and pre_dist_sq > local_pair_radius_sq:
                    continue
                friendly_pair_count += 1
                post_dist = math.sqrt(max(0.0, post_dist_sq))
                pre_dist = math.sqrt(max(0.0, pre_dist_sq))
                if post_dist > 1e-12:
                    nx = post_dx / post_dist
                    ny = post_dy / post_dist
                else:
                    nx, ny = self._stable_pair_direction(unit_i.unit_id, unit_j.unit_id)

                # Friendly crowding: keep same-fleet spacing from collapsing below the base floor.
                crowd_depth = self._hostile_spacing_depth(post_dist, float(self.separation_radius))
                if crowd_depth > 1e-12:
                    crowd_mag = 0.5 * strength * crowd_depth * float(self.separation_radius)
                    delta[unit_i.unit_id][0] += nx * crowd_mag
                    delta[unit_i.unit_id][1] += ny * crowd_mag
                    delta[unit_j.unit_id][0] -= nx * crowd_mag
                    delta[unit_j.unit_id][1] -= ny * crowd_mag

                # Friendly tearing: preserve local neighborhood integrity relative to the pre-state.
                if pre_dist < envelope_radius and post_dist > pre_dist:
                    stretch_delta = _clamp01((post_dist - pre_dist) / envelope_radius)
                    if stretch_delta > 1e-12:
                        stretch_mag = 0.5 * strength * stretch_delta * envelope_radius
                        delta[unit_i.unit_id][0] -= nx * stretch_mag
                        delta[unit_i.unit_id][1] -= ny * stretch_mag
                        delta[unit_j.unit_id][0] += nx * stretch_mag
                        delta[unit_j.unit_id][1] += ny * stretch_mag

        updated_units = dict(moved_state.units)
        displacement_sum = 0.0
        displacement_max = 0.0
        displacement_count = 0
        max_unit_displacement = 0.5 * float(self.separation_radius) * strength
        for unit in alive_units:
            dx, dy = delta[unit.unit_id]
            disp = math.sqrt((dx * dx) + (dy * dy))
            if disp > max_unit_displacement > 0.0:
                scale_factor = max_unit_displacement / disp
                dx *= scale_factor
                dy *= scale_factor
                disp = max_unit_displacement
            if disp <= 1e-12:
                continue
            updated_units[unit.unit_id] = replace(
                unit,
                position=Vec2(
                    x=float(unit.position.x) + dx,
                    y=float(unit.position.y) + dy,
                ),
            )
            displacement_sum += disp
            displacement_count += 1
            if disp > displacement_max:
                displacement_max = disp

        self.debug_last_hostile_contact_impedance = {
            "mode": HOSTILE_CONTACT_IMPEDANCE_MODE_SPACING_CO_RESOLUTION_V1,
            "enabled": True,
            "active": displacement_count > 0,
            "hostile_pair_count": hostile_pair_count,
            "friendly_pair_count": friendly_pair_count,
            "radius": envelope_radius,
            "mean_displacement": (
                displacement_sum / float(displacement_count)
                if displacement_count > 0
                else 0.0
            ),
            "max_displacement": displacement_max,
            "strength": strength,
        }
        return replace(moved_state, units=updated_units)

    def _apply_hostile_gated_coherence_regularization_v1(
        self,
        pre_state: BattleState,
        moved_state: BattleState,
    ) -> BattleState:
        scale = max(
            1e-6,
            float(
                getattr(
                    self,
                    "HOSTILE_GATED_COHERENCE_REGULARIZATION_SCALE",
                    HOSTILE_GATED_COHERENCE_REGULARIZATION_SCALE_DEFAULT,
                )
            ),
        )
        strength = _clamp01(
            float(
                getattr(
                    self,
                    "HOSTILE_GATED_COHERENCE_REGULARIZATION_STRENGTH",
                    HOSTILE_GATED_COHERENCE_REGULARIZATION_STRENGTH_DEFAULT,
                )
            )
        )
        envelope_radius = scale * float(self.separation_radius)
        alive_units = [unit for unit in moved_state.units.values() if float(unit.hit_points) > 0.0]
        if len(alive_units) <= 1 or envelope_radius <= 1e-12 or strength <= 0.0:
            self.debug_last_hostile_contact_impedance = {
                "mode": HOSTILE_CONTACT_IMPEDANCE_MODE_GATED_COHERENCE_REGULARIZATION_V1,
                "enabled": True,
                "active": False,
                "hostile_pair_count": 0,
                "friendly_link_count": 0,
                "radius": envelope_radius,
                "mean_hostile_displacement": 0.0,
                "mean_regularized_displacement": 0.0,
                "strength": strength,
            }
            return moved_state

        hostile_delta = {unit.unit_id: [0.0, 0.0] for unit in alive_units}
        hostile_pair_count = 0
        envelope_radius_sq = envelope_radius * envelope_radius
        for i in range(len(alive_units)):
            unit_i = alive_units[i]
            pre_i = pre_state.units.get(unit_i.unit_id)
            if pre_i is None:
                continue
            for j in range(i + 1, len(alive_units)):
                unit_j = alive_units[j]
                if unit_i.fleet_id == unit_j.fleet_id:
                    continue
                pre_j = pre_state.units.get(unit_j.unit_id)
                if pre_j is None:
                    continue
                post_dx = float(unit_i.position.x) - float(unit_j.position.x)
                post_dy = float(unit_i.position.y) - float(unit_j.position.y)
                post_dist_sq = (post_dx * post_dx) + (post_dy * post_dy)
                pre_dx = float(pre_i.position.x) - float(pre_j.position.x)
                pre_dy = float(pre_i.position.y) - float(pre_j.position.y)
                pre_dist_sq = (pre_dx * pre_dx) + (pre_dy * pre_dy)
                if post_dist_sq > envelope_radius_sq and pre_dist_sq > envelope_radius_sq:
                    continue
                hostile_pair_count += 1
                post_dist = math.sqrt(max(0.0, post_dist_sq))
                pre_dist = math.sqrt(max(0.0, pre_dist_sq))
                pre_depth = self._hostile_spacing_depth(pre_dist, envelope_radius)
                post_depth = self._hostile_spacing_depth(post_dist, envelope_radius)
                penetration_delta = max(0.0, post_depth - pre_depth)
                if penetration_delta <= 1e-12:
                    continue
                if post_dist > 1e-12:
                    nx = post_dx / post_dist
                    ny = post_dy / post_dist
                else:
                    nx, ny = self._stable_pair_direction(unit_i.unit_id, unit_j.unit_id)
                correction_mag = 0.5 * strength * penetration_delta * envelope_radius
                hostile_delta[unit_i.unit_id][0] += nx * correction_mag
                hostile_delta[unit_i.unit_id][1] += ny * correction_mag
                hostile_delta[unit_j.unit_id][0] -= nx * correction_mag
                hostile_delta[unit_j.unit_id][1] -= ny * correction_mag

        friendly_links_by_unit: dict[str, list[str]] = {unit.unit_id: [] for unit in alive_units}
        local_radius_sq = envelope_radius_sq
        friendly_link_count = 0
        for i in range(len(alive_units)):
            unit_i = alive_units[i]
            pre_i = pre_state.units.get(unit_i.unit_id)
            if pre_i is None:
                continue
            for j in range(i + 1, len(alive_units)):
                unit_j = alive_units[j]
                if unit_i.fleet_id != unit_j.fleet_id:
                    continue
                pre_j = pre_state.units.get(unit_j.unit_id)
                if pre_j is None:
                    continue
                pre_dx = float(pre_i.position.x) - float(pre_j.position.x)
                pre_dy = float(pre_i.position.y) - float(pre_j.position.y)
                pre_dist_sq = (pre_dx * pre_dx) + (pre_dy * pre_dy)
                if pre_dist_sq > local_radius_sq:
                    continue
                friendly_links_by_unit[unit_i.unit_id].append(unit_j.unit_id)
                friendly_links_by_unit[unit_j.unit_id].append(unit_i.unit_id)
                friendly_link_count += 1

        updated_units = dict(moved_state.units)
        hostile_disp_sum = 0.0
        regularized_disp_sum = 0.0
        active_count = 0
        max_unit_displacement = 0.5 * float(self.separation_radius) * strength
        for unit in alive_units:
            raw_dx, raw_dy = hostile_delta[unit.unit_id]
            raw_disp = math.sqrt((raw_dx * raw_dx) + (raw_dy * raw_dy))
            if raw_disp <= 1e-12:
                continue
            neighbors = friendly_links_by_unit.get(unit.unit_id, [])
            if neighbors:
                avg_dx = raw_dx
                avg_dy = raw_dy
                count = 1.0
                for other_id in neighbors:
                    odx, ody = hostile_delta.get(other_id, (0.0, 0.0))
                    avg_dx += odx
                    avg_dy += ody
                    count += 1.0
                avg_dx /= count
                avg_dy /= count
                blend = 0.5 * strength
                reg_dx = ((1.0 - blend) * raw_dx) + (blend * avg_dx)
                reg_dy = ((1.0 - blend) * raw_dy) + (blend * avg_dy)
            else:
                reg_dx, reg_dy = raw_dx, raw_dy

            reg_disp = math.sqrt((reg_dx * reg_dx) + (reg_dy * reg_dy))
            if reg_disp > max_unit_displacement > 0.0:
                scale_factor = max_unit_displacement / reg_disp
                reg_dx *= scale_factor
                reg_dy *= scale_factor
                reg_disp = max_unit_displacement
            if reg_disp <= 1e-12:
                continue

            updated_units[unit.unit_id] = replace(
                unit,
                position=Vec2(
                    x=float(unit.position.x) + reg_dx,
                    y=float(unit.position.y) + reg_dy,
                ),
            )
            hostile_disp_sum += raw_disp
            regularized_disp_sum += reg_disp
            active_count += 1

        self.debug_last_hostile_contact_impedance = {
            "mode": HOSTILE_CONTACT_IMPEDANCE_MODE_GATED_COHERENCE_REGULARIZATION_V1,
            "enabled": True,
            "active": active_count > 0,
            "hostile_pair_count": hostile_pair_count,
            "friendly_link_count": friendly_link_count,
            "radius": envelope_radius,
            "mean_hostile_displacement": (
                hostile_disp_sum / float(active_count)
                if active_count > 0
                else 0.0
            ),
            "mean_regularized_displacement": (
                regularized_disp_sum / float(active_count)
                if active_count > 0
                else 0.0
            ),
            "strength": strength,
        }
        return replace(moved_state, units=updated_units)

    def _apply_hostile_contact_impedance(
        self,
        pre_state: BattleState,
        moved_state: BattleState,
    ) -> BattleState:
        mode = self._resolve_hostile_contact_impedance_mode()
        if mode == HOSTILE_CONTACT_IMPEDANCE_MODE_OFF:
            self.debug_last_hostile_contact_impedance = {
                "mode": mode,
                "enabled": False,
                "active": False,
                "pair_count": 0,
                "radius": 0.0,
            }
            return moved_state
        if mode == HOSTILE_CONTACT_IMPEDANCE_MODE_REPULSION_V1:
            return self._apply_hostile_contact_impedance_v1(moved_state)
        if mode in {
            HOSTILE_CONTACT_IMPEDANCE_MODE_INTENT_UNIFIED_SPACING_V1,
            HOSTILE_CONTACT_IMPEDANCE_MODE_INTENT_OCCUPANCY_ONLY_V1,
        }:
            return moved_state
        return self._apply_hostile_contact_impedance_v2(pre_state, moved_state, mode=mode)

    def _build_continuous_fr_proxy_state(
        self, state: BattleState
    ) -> tuple[BattleState, dict[str, dict[str, float | bool | str]]]:
        movement_model = str(getattr(self, "MOVEMENT_MODEL", "v3a")).strip().lower()
        movement_v3a_experiment = str(getattr(self, "MOVEMENT_V3A_EXPERIMENT", "base")).strip().lower()
        shaping_enabled = bool(getattr(self, "CONTINUOUS_FR_SHAPING_ENABLED", False))
        shaping_mode = str(
            getattr(self, "CONTINUOUS_FR_SHAPING_MODE", CONTINUOUS_FR_SHAPING_OFF)
        ).strip().lower()
        if (
            not shaping_enabled
            or movement_model != "v3a"
            or movement_v3a_experiment != V3A_EXPERIMENT_PRECONTACT_CENTROID_PROBE
            or shaping_mode not in CONTINUOUS_FR_SHAPING_LABELS
            or shaping_mode == CONTINUOUS_FR_SHAPING_OFF
        ):
            return state, {}

        shaping_a = max(0.0, float(getattr(self, "CONTINUOUS_FR_SHAPING_A", 0.0)))
        shaping_sigma = max(1e-6, float(getattr(self, "CONTINUOUS_FR_SHAPING_SIGMA", 0.15)))
        shaping_p = max(0.0, float(getattr(self, "CONTINUOUS_FR_SHAPING_P", 1.0)))
        shaping_q = max(0.0, float(getattr(self, "CONTINUOUS_FR_SHAPING_Q", 1.0)))
        shaping_beta = max(0.0, float(getattr(self, "CONTINUOUS_FR_SHAPING_BETA", 0.0)))
        shaping_gamma = max(0.0, float(getattr(self, "CONTINUOUS_FR_SHAPING_GAMMA", 0.0)))

        proxy_fleets = {}
        debug_payload = {}
        proxy_active = False
        for fleet_id, fleet in state.fleets.items():
            alive_count = 0
            engaged_alive_count = 0
            for unit_id in fleet.unit_ids:
                unit = state.units.get(unit_id)
                if unit is None or float(unit.hit_points) <= 0.0:
                    continue
                alive_count += 1
                if bool(unit.engaged):
                    engaged_alive_count += 1
            engaged_fraction = (engaged_alive_count / float(alive_count)) if alive_count > 0 else 0.0

            normalized = fleet.parameters.normalized()
            shaping = _compute_continuous_fr_shaping(
                mode=shaping_mode,
                kappa=float(normalized.get("formation_rigidity", 0.0)),
                pd_norm=float(normalized.get("pursuit_drive", 0.5)),
                engaged_fraction=engaged_fraction,
                mobility_raw=float(fleet.parameters.mobility_bias),
                a=shaping_a,
                sigma=shaping_sigma,
                p=shaping_p,
                q=shaping_q,
                beta=shaping_beta,
                gamma=shaping_gamma,
            )
            debug_payload[fleet_id] = shaping
            proxy_parameters = FormationRigidityFirstReadProxy(fleet.parameters, float(shaping["kappa_eff"]))
            proxy_fleets[fleet_id] = replace(fleet, parameters=proxy_parameters)
            proxy_active = True

        if not proxy_active:
            return state, debug_payload
        return replace(state, fleets=proxy_fleets), debug_payload

    def step(self, state: BattleState) -> BattleState:
        snapshot = replace(state, tick=state.tick + 1)
        next_state = self.evaluate_cohesion(snapshot)
        next_state = self.evaluate_target(next_state)
        next_state = self.evaluate_utility(next_state)
        proxy_state, proxy_debug = self._build_continuous_fr_proxy_state(next_state)
        movement_input_state = self._apply_hostile_intent_penetration_bias(proxy_state)
        if bool(getattr(self, "SYMMETRIC_MOVEMENT_SYNC_ENABLED", False)):
            moved_state = self._integrate_movement_symmetric_merge(movement_input_state)
        else:
            moved_state = self.integrate_movement(movement_input_state)
        if proxy_state is not next_state:
            moved_state = replace(moved_state, fleets=next_state.fleets)
        moved_state = self._restore_intent_penetration_bias_units(proxy_state, moved_state)
        moved_state = self._apply_hostile_contact_impedance(next_state, moved_state)
        self.debug_last_continuous_fr_shaping = proxy_debug
        return self.resolve_combat(moved_state)

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
        nested_value = get_nested_mapping_value(runtime_section, ("metatype", key), _MISSING)
        if nested_value is not _MISSING:
            return nested_value
    return default


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
    section = settings.get("run_control", {})
    if isinstance(section, dict) and key in section:
        return section[key]
    return default


def get_contact_model_test_setting(settings: dict, path: tuple[str, ...], default):
    runtime_section = settings.get("runtime", {})
    if isinstance(runtime_section, dict):
        nested_value = get_nested_mapping_value(
            runtime_section,
            ("physical", "contact_model", "test_only", "hostile_contact_impedance", *path),
            _MISSING,
        )
        if nested_value is not _MISSING:
            return nested_value
    return default


def get_env_bool(name: str) -> bool | None:
    raw = os.environ.get(name)
    if raw is None:
        return None
    value = str(raw).strip().lower()
    if value in {"1", "true", "yes", "on"}:
        return True
    if value in {"0", "false", "no", "off"}:
        return False
    return None


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


def _direction_from_angle_deg(angle_deg: float) -> tuple[float, float]:
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


def _resolve_point_setting(
    settings: dict,
    *,
    array_key: str,
    x_key: str,
    y_key: str,
    default_x: float,
    default_y: float,
) -> tuple[float, float]:
    raw = get_fleet_setting(settings, array_key, None)
    if isinstance(raw, Sequence) and not isinstance(raw, (str, bytes)) and len(raw) >= 2:
        return float(raw[0]), float(raw[1])
    return (
        float(get_fleet_setting(settings, x_key, default_x)),
        float(get_fleet_setting(settings, y_key, default_y)),
    )


def resolve_effective_seed(seed_value: int) -> int:
    if seed_value < 0:
        return random.SystemRandom().randrange(0, 2**32)
    return seed_value


def resolve_timestamped_video_output_path(
    raw_output_path: str,
    base_dir: Path,
    *,
    export_stem: str | None = None,
) -> Path:
    candidate = Path(str(raw_output_path).strip()) if str(raw_output_path).strip() else Path(DEFAULT_VIDEO_EXPORT_DIR)
    if not candidate.is_absolute():
        candidate = (base_dir.parent / candidate).resolve()
    if candidate.suffix:
        target_dir = candidate.parent
        suffix = candidate.suffix
    else:
        target_dir = candidate
        suffix = ".mp4"
    final_stem = str(export_stem).strip() if export_stem else DEFAULT_VIDEO_EXPORT_TOPIC
    return (target_dir / f"{final_stem}{suffix}").resolve()


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

    forward_values: list[float] | None = None
    lateral_values: list[float] | None = None
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
            forward_values = []
            lateral_values = []
            for x, y in side_points:
                dx = float(x) - cx
                dy = float(y) - cy
                forward_values.append((dx * fx) + (dy * fy))
                lateral_values.append((dx * lx) + (dy * ly))
            sigma_forward = _std_population(forward_values)
            sigma_lateral = _std_population(lateral_values)
            result["AR_forward"] = sigma_forward / (sigma_lateral + BRIDGE_EPSILON)
            result["major_axis_alignment"] = abs((ux * fx) + (uy * fy))

    n_units = len(side_points)
    if n_units > 0 and forward_values is not None and lateral_values is not None:
        group_size = max(1, int(math.ceil(0.3 * float(n_units))))
        sorted_indices = sorted(range(n_units), key=lambda i: forward_values[i])
        rear_indices = sorted_indices[:group_size]
        front_indices = sorted_indices[-group_size:]
        v_rear = [lateral_values[i] for i in rear_indices]
        v_front = [lateral_values[i] for i in front_indices]
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

    state = BattleState(
        tick=0,
        dt=DEFAULT_DT,
        arena_size=arena_size,
        units=units,
        fleets=fleets,
        last_fleet_cohesion=build_initial_cohesion_map(fleets.keys()),
    )
    return state


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
    pre_tl_target_substrate: str = PRE_TL_TARGET_SUBSTRATE_DEFAULT,
    odw_posture_bias_enabled: bool = False,
    odw_posture_bias_k: float = 0.3,
    odw_posture_bias_clip_delta: float = 0.2,
    symmetric_movement_sync_enabled: bool = True,
    hostile_contact_impedance_mode: str = HOSTILE_CONTACT_IMPEDANCE_MODE_DEFAULT,
    hostile_contact_impedance_strength: float = HOSTILE_CONTACT_IMPEDANCE_STRENGTH_DEFAULT,
    hostile_contact_impedance_radius_multiplier: float = HOSTILE_CONTACT_IMPEDANCE_RADIUS_MULTIPLIER_DEFAULT,
    hostile_contact_impedance_v2_radius_multiplier: float = HOSTILE_CONTACT_IMPEDANCE_V2_RADIUS_MULTIPLIER_DEFAULT,
    hostile_contact_impedance_v2_repulsion_max_disp_ratio: float = HOSTILE_CONTACT_IMPEDANCE_V2_REPULSION_MAX_DISP_RATIO_DEFAULT,
    hostile_contact_impedance_v2_forward_damping_strength: float = HOSTILE_CONTACT_IMPEDANCE_V2_FORWARD_DAMPING_STRENGTH_DEFAULT,
    hostile_spacing_floor_scale: float = HOSTILE_SPACING_FLOOR_SCALE_DEFAULT,
    hostile_spacing_floor_strength: float = HOSTILE_SPACING_FLOOR_STRENGTH_DEFAULT,
    hostile_spacing_floor_v2_scale: float = HOSTILE_SPACING_FLOOR_V2_SCALE_DEFAULT,
    hostile_spacing_floor_v2_strength: float = HOSTILE_SPACING_FLOOR_V2_STRENGTH_DEFAULT,
    hostile_spacing_co_resolution_scale: float = HOSTILE_SPACING_CO_RESOLUTION_SCALE_DEFAULT,
    hostile_spacing_co_resolution_strength: float = HOSTILE_SPACING_CO_RESOLUTION_STRENGTH_DEFAULT,
    hostile_gated_coherence_regularization_scale: float = HOSTILE_GATED_COHERENCE_REGULARIZATION_SCALE_DEFAULT,
    hostile_gated_coherence_regularization_strength: float = HOSTILE_GATED_COHERENCE_REGULARIZATION_STRENGTH_DEFAULT,
    hostile_intent_unified_spacing_scale: float = HOSTILE_INTENT_UNIFIED_SPACING_SCALE_DEFAULT,
    hostile_intent_unified_spacing_strength: float = HOSTILE_INTENT_UNIFIED_SPACING_STRENGTH_DEFAULT,
    hostile_intent_occupancy_only_scale: float = HOSTILE_INTENT_OCCUPANCY_ONLY_SCALE_DEFAULT,
    hostile_intent_occupancy_only_strength: float = HOSTILE_INTENT_OCCUPANCY_ONLY_STRENGTH_DEFAULT,
    continuous_fr_shaping_enabled: bool = False,
    continuous_fr_shaping_mode: str = CONTINUOUS_FR_SHAPING_OFF,
    continuous_fr_shaping_a: float = 0.0,
    continuous_fr_shaping_sigma: float = 0.15,
    continuous_fr_shaping_p: float = 1.0,
    continuous_fr_shaping_q: float = 1.0,
    continuous_fr_shaping_beta: float = 0.0,
    continuous_fr_shaping_gamma: float = 0.0,
    v2_connect_radius_multiplier: float = 1.0,
    v3_connect_radius_multiplier: float = 1.0,
    v3_r_ref_radius_multiplier: float = 1.0,
    runtime_diag_enabled: bool = False,
    post_elimination_extra_ticks: int = 10,
):
    post_elimination_extra_ticks = max(0, int(post_elimination_extra_ticks))
    engine = TestModeEngineTickSkeleton(
        attack_range=attack_range,
        damage_per_tick=damage_per_tick,
        separation_radius=separation_radius,
    )
    engine.COHESION_DECISION_SOURCE = str(runtime_decision_source).strip().lower() or "v2"
    engine.MOVEMENT_MODEL = str(movement_model).strip().lower() or "v3a"
    engine.MOVEMENT_V3A_EXPERIMENT = str(movement_v3a_experiment).strip().lower() or "base"
    engine.CENTROID_PROBE_SCALE = float(centroid_probe_scale)
    engine.PRE_TL_TARGET_SUBSTRATE = str(pre_tl_target_substrate).strip().lower() or PRE_TL_TARGET_SUBSTRATE_DEFAULT
    engine.ODW_POSTURE_BIAS_ENABLED = bool(odw_posture_bias_enabled)
    engine.ODW_POSTURE_BIAS_K = max(0.0, float(odw_posture_bias_k))
    engine.ODW_POSTURE_BIAS_CLIP_DELTA = max(0.0, float(odw_posture_bias_clip_delta))
    engine.SYMMETRIC_MOVEMENT_SYNC_ENABLED = bool(symmetric_movement_sync_enabled)
    engine.HOSTILE_CONTACT_IMPEDANCE_MODE = (
        str(hostile_contact_impedance_mode).strip().lower() or HOSTILE_CONTACT_IMPEDANCE_MODE_DEFAULT
    )
    engine.HOSTILE_CONTACT_IMPEDANCE_STRENGTH = max(0.0, float(hostile_contact_impedance_strength))
    engine.HOSTILE_CONTACT_IMPEDANCE_RADIUS_MULTIPLIER = max(
        1e-6, float(hostile_contact_impedance_radius_multiplier)
    )
    engine.HOSTILE_CONTACT_IMPEDANCE_V2_RADIUS_MULTIPLIER = max(
        1e-6, float(hostile_contact_impedance_v2_radius_multiplier)
    )
    engine.HOSTILE_CONTACT_IMPEDANCE_V2_REPULSION_MAX_DISP_RATIO = max(
        0.0, float(hostile_contact_impedance_v2_repulsion_max_disp_ratio)
    )
    engine.HOSTILE_CONTACT_IMPEDANCE_V2_FORWARD_DAMPING_STRENGTH = _clamp01(
        float(hostile_contact_impedance_v2_forward_damping_strength)
    )
    engine.HOSTILE_SPACING_FLOOR_SCALE = max(1e-6, float(hostile_spacing_floor_scale))
    engine.HOSTILE_SPACING_FLOOR_STRENGTH = _clamp01(float(hostile_spacing_floor_strength))
    engine.HOSTILE_SPACING_FLOOR_V2_SCALE = max(1e-6, float(hostile_spacing_floor_v2_scale))
    engine.HOSTILE_SPACING_FLOOR_V2_STRENGTH = _clamp01(float(hostile_spacing_floor_v2_strength))
    engine.HOSTILE_SPACING_CO_RESOLUTION_SCALE = max(1e-6, float(hostile_spacing_co_resolution_scale))
    engine.HOSTILE_SPACING_CO_RESOLUTION_STRENGTH = _clamp01(float(hostile_spacing_co_resolution_strength))
    engine.HOSTILE_GATED_COHERENCE_REGULARIZATION_SCALE = max(
        1e-6, float(hostile_gated_coherence_regularization_scale)
    )
    engine.HOSTILE_GATED_COHERENCE_REGULARIZATION_STRENGTH = _clamp01(
        float(hostile_gated_coherence_regularization_strength)
    )
    engine.HOSTILE_INTENT_UNIFIED_SPACING_SCALE = max(1e-6, float(hostile_intent_unified_spacing_scale))
    engine.HOSTILE_INTENT_UNIFIED_SPACING_STRENGTH = _clamp01(float(hostile_intent_unified_spacing_strength))
    engine.HOSTILE_INTENT_OCCUPANCY_ONLY_SCALE = max(1e-6, float(hostile_intent_occupancy_only_scale))
    engine.HOSTILE_INTENT_OCCUPANCY_ONLY_STRENGTH = _clamp01(float(hostile_intent_occupancy_only_strength))
    engine.CONTINUOUS_FR_SHAPING_ENABLED = bool(continuous_fr_shaping_enabled)
    engine.CONTINUOUS_FR_SHAPING_MODE = str(continuous_fr_shaping_mode).strip().lower() or CONTINUOUS_FR_SHAPING_OFF
    engine.CONTINUOUS_FR_SHAPING_A = max(0.0, float(continuous_fr_shaping_a))
    engine.CONTINUOUS_FR_SHAPING_SIGMA = max(1e-6, float(continuous_fr_shaping_sigma))
    engine.CONTINUOUS_FR_SHAPING_P = max(0.0, float(continuous_fr_shaping_p))
    engine.CONTINUOUS_FR_SHAPING_Q = max(0.0, float(continuous_fr_shaping_q))
    engine.CONTINUOUS_FR_SHAPING_BETA = max(0.0, float(continuous_fr_shaping_beta))
    engine.CONTINUOUS_FR_SHAPING_GAMMA = max(0.0, float(continuous_fr_shaping_gamma))
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
        "centroid_x": {fleet_id: [] for fleet_id in state.fleets},
        "centroid_y": {fleet_id: [] for fleet_id in state.fleets},
        "net_axis_push": {"net": []},
        "net_axis_push_interval_ticks": 10,
        "center_wing_advance_gap": {fleet_id: [] for fleet_id in state.fleets},
        "center_wing_advance_gap_interval_ticks": 10,
        "front_curvature_index": {fleet_id: [] for fleet_id in state.fleets},
        "center_wing_parallel_share": {fleet_id: [] for fleet_id in state.fleets},
        "posture_persistence_time": {fleet_id: [] for fleet_id in state.fleets},
        "hostile_overlap_pairs": [],
        "hostile_deep_pairs": [],
        "hostile_deep_intermix_ratio": [],
        "hostile_intermix_severity": [],
        "hostile_intermix_coverage": [],
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
    center_wing_interval_ticks = int(observer_telemetry.get("center_wing_advance_gap_interval_ticks", 10))
    center_wing_position_history = {fleet_id: [] for fleet_id in state.fleets}
    posture_persistence_state = {
        fleet_id: {"sign": 0, "length": 0}
        for fleet_id in state.fleets
    }
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
            centroid_sum_x = 0.0
            centroid_sum_y = 0.0
            centroid_count = 0
            unit_position_map: dict[str, tuple[float, float]] = {}
            for unit_id in fleet.unit_ids:
                if unit_id in state.units:
                    unit_state = state.units[unit_id]
                    fleet_size += max(0.0, float(unit_state.hit_points))
                    centroid_sum_x += float(unit_state.position.x)
                    centroid_sum_y += float(unit_state.position.y)
                    centroid_count += 1
                    unit_position_map[str(unit_id)] = (float(unit_state.position.x), float(unit_state.position.y))
            fleet_size_trajectory[fleet_id].append(fleet_size)
            center_wing_position_history[fleet_id].append(unit_position_map)
            if centroid_count > 0:
                observer_telemetry["centroid_x"][fleet_id].append(centroid_sum_x / float(centroid_count))
                observer_telemetry["centroid_y"][fleet_id].append(centroid_sum_y / float(centroid_count))
            else:
                observer_telemetry["centroid_x"][fleet_id].append(float("nan"))
                observer_telemetry["centroid_y"][fleet_id].append(float("nan"))
        hostile_intermix_metrics = _compute_hostile_intermix_metrics(state, float(separation_radius))
        observer_telemetry["hostile_overlap_pairs"].append(
            float(hostile_intermix_metrics.get("hostile_overlap_pairs", 0.0))
        )
        observer_telemetry["hostile_deep_pairs"].append(
            float(hostile_intermix_metrics.get("hostile_deep_pairs", 0.0))
        )
        observer_telemetry["hostile_deep_intermix_ratio"].append(
            float(hostile_intermix_metrics.get("hostile_deep_intermix_ratio", 0.0))
        )
        observer_telemetry["hostile_intermix_severity"].append(
            float(hostile_intermix_metrics.get("hostile_intermix_severity", 0.0))
        )
        observer_telemetry["hostile_intermix_coverage"].append(
            float(hostile_intermix_metrics.get("hostile_intermix_coverage", 0.0))
        )
        for fleet_id in state.fleets:
            series = observer_telemetry["center_wing_advance_gap"][fleet_id]
            history = center_wing_position_history.get(fleet_id, [])
            current_positions = history[-1] if history else {}
            current_unit_ids = list(current_positions.keys())
            enemy_centroids = []
            for other_fleet_id in state.fleets:
                if other_fleet_id == fleet_id:
                    continue
                enemy_x = float(observer_telemetry["centroid_x"].get(other_fleet_id, [float("nan")])[-1])
                enemy_y = float(observer_telemetry["centroid_y"].get(other_fleet_id, [float("nan")])[-1])
                if math.isfinite(enemy_x) and math.isfinite(enemy_y):
                    enemy_centroids.append((enemy_x, enemy_y))
            if len(current_unit_ids) < 6 or not enemy_centroids:
                series.append(float("nan"))
                observer_telemetry["front_curvature_index"][fleet_id].append(float("nan"))
                observer_telemetry["center_wing_parallel_share"][fleet_id].append(float("nan"))
                observer_telemetry["posture_persistence_time"][fleet_id].append(0.0)
                posture_persistence_state[fleet_id]["sign"] = 0
                posture_persistence_state[fleet_id]["length"] = 0
                continue

            curr_xs_now = [current_positions[unit_id][0] for unit_id in current_unit_ids]
            curr_ys_now = [current_positions[unit_id][1] for unit_id in current_unit_ids]
            centroid_x_now = sum(curr_xs_now) / float(len(curr_xs_now))
            centroid_y_now = sum(curr_ys_now) / float(len(curr_ys_now))
            enemy_centroid_x = sum(item[0] for item in enemy_centroids) / float(len(enemy_centroids))
            enemy_centroid_y = sum(item[1] for item in enemy_centroids) / float(len(enemy_centroids))
            axis_dx = enemy_centroid_x - centroid_x_now
            axis_dy = enemy_centroid_y - centroid_y_now
            axis_norm = math.sqrt((axis_dx * axis_dx) + (axis_dy * axis_dy))
            if axis_norm <= 1e-12:
                series.append(float("nan"))
                observer_telemetry["front_curvature_index"][fleet_id].append(float("nan"))
                observer_telemetry["center_wing_parallel_share"][fleet_id].append(float("nan"))
                observer_telemetry["posture_persistence_time"][fleet_id].append(0.0)
                posture_persistence_state[fleet_id]["sign"] = 0
                posture_persistence_state[fleet_id]["length"] = 0
                continue
            axis_dir_x = axis_dx / axis_norm
            axis_dir_y = axis_dy / axis_norm

            projected_units: list[tuple[float, float, str]] = []
            for unit_id in current_unit_ids:
                curr_x, curr_y = current_positions[unit_id]
                lateral_offset_now = ((curr_x - centroid_x_now) * (-axis_dir_y)) + ((curr_y - centroid_y_now) * axis_dir_x)
                advance_now = ((curr_x - centroid_x_now) * axis_dir_x) + ((curr_y - centroid_y_now) * axis_dir_y)
                projected_units.append((float(advance_now), abs(float(lateral_offset_now)), str(unit_id)))

            projected_units.sort(key=lambda item: item[0])
            projected_units_by_width = sorted(
                ((item[1], item[2]) for item in projected_units),
                key=lambda item: item[0],
            )
            width_split_index = len(projected_units_by_width) // 2
            center_unit_ids = {unit_id for _, unit_id in projected_units_by_width[:width_split_index]}
            wing_unit_ids = {unit_id for _, unit_id in projected_units_by_width[width_split_index:]}

            if len(history) <= center_wing_interval_ticks:
                series.append(float("nan"))
                interval_parallel_share_gap = float("nan")
            else:
                prev_positions = history[-(center_wing_interval_ticks + 1)]
                common_unit_ids = [unit_id for unit_id in current_positions if unit_id in prev_positions]
                if len(common_unit_ids) < 4:
                    series.append(float("nan"))
                    interval_parallel_share_gap = float("nan")
                else:
                    center_advances: list[float] = []
                    wing_advances: list[float] = []
                    center_interval_total = 0.0
                    wing_interval_total = 0.0
                    for unit_id in common_unit_ids:
                        curr_x, curr_y = current_positions[unit_id]
                        prev_x, prev_y = prev_positions[unit_id]
                        advance = ((curr_x - prev_x) * axis_dir_x) + ((curr_y - prev_y) * axis_dir_y)
                        if unit_id in center_unit_ids:
                            center_advances.append(float(advance))
                            center_interval_total += advance
                        elif unit_id in wing_unit_ids:
                            wing_advances.append(float(advance))
                            wing_interval_total += advance
                    center_band = center_advances
                    wing_band = wing_advances
                    if not center_band or not wing_band:
                        series.append(float("nan"))
                        interval_parallel_share_gap = float("nan")
                    else:
                        center_mean = sum(center_band) / float(len(center_band))
                        wing_mean = sum(wing_band) / float(len(wing_band))
                        series.append(0.5 * float(center_mean - wing_mean))
                        interval_parallel_total = abs(center_interval_total) + abs(wing_interval_total)
                        if interval_parallel_total > 1e-12:
                            interval_parallel_share_gap = float(
                                (center_interval_total - wing_interval_total) / interval_parallel_total
                            )
                        else:
                            interval_parallel_share_gap = 0.0

            front_group_size = max(3, int(math.ceil(len(projected_units) * 0.30)))
            front_group = projected_units[-front_group_size:]
            front_group.sort(key=lambda item: item[1])
            front_split_index = len(front_group) // 2
            front_center_band = front_group[:front_split_index]
            front_wing_band = front_group[front_split_index:]
            if front_center_band and front_wing_band:
                front_center_mean = sum(item[0] for item in front_center_band) / float(len(front_center_band))
                front_wing_mean = sum(item[0] for item in front_wing_band) / float(len(front_wing_band))
                front_curvature_raw = float(front_center_mean - front_wing_mean)
            else:
                front_curvature_raw = float("nan")
            observer_telemetry["front_curvature_index"][fleet_id].append(front_curvature_raw)
            center_parallel_total = 0.0
            wing_parallel_total = 0.0
            for unit_id in current_unit_ids:
                unit_state = state.units.get(unit_id)
                if unit_state is None:
                    continue
                parallel_velocity = (
                    float(unit_state.velocity.x) * axis_dir_x
                    + float(unit_state.velocity.y) * axis_dir_y
                )
                if unit_id in center_unit_ids:
                    center_parallel_total += parallel_velocity
                elif unit_id in wing_unit_ids:
                    wing_parallel_total += parallel_velocity
            total_parallel = abs(center_parallel_total) + abs(wing_parallel_total)
            if total_parallel > 1e-12:
                instantaneous_parallel_share_gap = float(
                    (center_parallel_total - wing_parallel_total) / total_parallel
                )
            else:
                instantaneous_parallel_share_gap = 0.0
            if math.isfinite(interval_parallel_share_gap):
                center_wing_parallel_share_gap = interval_parallel_share_gap
            else:
                center_wing_parallel_share_gap = instantaneous_parallel_share_gap
            observer_telemetry["center_wing_parallel_share"][fleet_id].append(center_wing_parallel_share_gap)

            posture_sign = 0
            if math.isfinite(front_curvature_raw):
                front_curvature_norm = float(front_curvature_raw) / max(float(separation_radius), 1e-12)
                if front_curvature_norm >= 0.10 and center_wing_parallel_share_gap >= 0.05:
                    posture_sign = 1
                elif front_curvature_norm <= -0.10 and center_wing_parallel_share_gap <= -0.05:
                    posture_sign = -1
            prior_sign = int(posture_persistence_state[fleet_id]["sign"])
            prior_length = int(posture_persistence_state[fleet_id]["length"])
            if posture_sign == 0:
                next_length = 0
            elif posture_sign == prior_sign:
                next_length = prior_length + 1
            else:
                next_length = 1
            posture_persistence_state[fleet_id]["sign"] = posture_sign
            posture_persistence_state[fleet_id]["length"] = next_length
            observer_telemetry["posture_persistence_time"][fleet_id].append(float(posture_sign * next_length))
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
                post_elimination_stop_tick = min(999, elimination_tick + post_elimination_extra_ticks)
            if post_elimination_stop_tick is not None and state.tick >= post_elimination_stop_tick:
                break
        else:
            if any_fleet_eliminated:
                break

    net_axis_push_interval_ticks = int(observer_telemetry.get("net_axis_push_interval_ticks", 10))
    center_wing_interval_ticks = int(observer_telemetry.get("center_wing_advance_gap_interval_ticks", 10))
    max_unit_speed = 1.0
    if isinstance(state.units, Mapping) and state.units:
        unit_speed_values = []
        for unit_state in state.units.values():
            try:
                unit_speed_values.append(float(getattr(unit_state, "max_speed", 0.0)))
            except (TypeError, ValueError):
                continue
        finite_unit_speed_values = [value for value in unit_speed_values if math.isfinite(value) and value > 0.0]
        if finite_unit_speed_values:
            max_unit_speed = max(finite_unit_speed_values)
    net_axis_push_normalization_scale = float(max_unit_speed) * float(net_axis_push_interval_ticks)
    if net_axis_push_normalization_scale <= 0.0 or not math.isfinite(net_axis_push_normalization_scale):
        net_axis_push_normalization_scale = 1.0
    center_wing_normalization_scale = float(max_unit_speed) * float(center_wing_interval_ticks)
    if center_wing_normalization_scale <= 0.0 or not math.isfinite(center_wing_normalization_scale):
        center_wing_normalization_scale = 1.0
    front_curvature_normalization_scale = max(float(separation_radius), 1e-12)
    centroid_x_a = observer_telemetry.get("centroid_x", {}).get("A", [])
    centroid_y_a = observer_telemetry.get("centroid_y", {}).get("A", [])
    centroid_x_b = observer_telemetry.get("centroid_x", {}).get("B", [])
    centroid_y_b = observer_telemetry.get("centroid_y", {}).get("B", [])
    net_axis_push_series: list[float] = []
    axis_initialized = False
    axis_dir_x = 0.0
    axis_dir_y = 0.0
    for idx in range(len(trajectory.get("A", []))):
        ax = float(centroid_x_a[idx]) if idx < len(centroid_x_a) else float("nan")
        ay = float(centroid_y_a[idx]) if idx < len(centroid_y_a) else float("nan")
        bx = float(centroid_x_b[idx]) if idx < len(centroid_x_b) else float("nan")
        by = float(centroid_y_b[idx]) if idx < len(centroid_y_b) else float("nan")
        valid_pair = all(math.isfinite(value) for value in (ax, ay, bx, by))
        if valid_pair and not axis_initialized:
            dx0 = bx - ax
            dy0 = by - ay
            norm0 = math.sqrt((dx0 * dx0) + (dy0 * dy0))
            if norm0 > 1e-12:
                axis_dir_x = dx0 / norm0
                axis_dir_y = dy0 / norm0
                axis_initialized = True
        if (
            not axis_initialized
            or not valid_pair
            or idx < net_axis_push_interval_ticks
        ):
            net_axis_push_series.append(float("nan"))
            continue
        prev_idx = idx - net_axis_push_interval_ticks
        ax_prev = float(centroid_x_a[prev_idx]) if prev_idx < len(centroid_x_a) else float("nan")
        ay_prev = float(centroid_y_a[prev_idx]) if prev_idx < len(centroid_y_a) else float("nan")
        bx_prev = float(centroid_x_b[prev_idx]) if prev_idx < len(centroid_x_b) else float("nan")
        by_prev = float(centroid_y_b[prev_idx]) if prev_idx < len(centroid_y_b) else float("nan")
        if not all(math.isfinite(value) for value in (ax_prev, ay_prev, bx_prev, by_prev)):
            net_axis_push_series.append(float("nan"))
            continue
        advance_a = ((ax - ax_prev) * axis_dir_x) + ((ay - ay_prev) * axis_dir_y)
        advance_b = ((bx_prev - bx) * axis_dir_x) + ((by_prev - by) * axis_dir_y)
        net_axis_push_value = 0.5 * float(advance_a - advance_b)
        net_axis_push_series.append(float(net_axis_push_value / net_axis_push_normalization_scale))
    observer_telemetry["net_axis_push"]["net"] = net_axis_push_series
    observer_telemetry["net_axis_push_normalization_scale"] = net_axis_push_normalization_scale
    for fleet_id in state.fleets:
        normalized_gap_series: list[float] = []
        for raw_value in observer_telemetry["center_wing_advance_gap"][fleet_id]:
            if math.isfinite(float(raw_value)):
                normalized_gap_series.append(float(raw_value) / center_wing_normalization_scale)
            else:
                normalized_gap_series.append(float("nan"))
        observer_telemetry["center_wing_advance_gap"][fleet_id] = normalized_gap_series
        normalized_front_curvature_series: list[float] = []
        for raw_value in observer_telemetry["front_curvature_index"][fleet_id]:
            if math.isfinite(float(raw_value)):
                normalized_front_curvature_series.append(float(raw_value) / front_curvature_normalization_scale)
            else:
                normalized_front_curvature_series.append(float("nan"))
        observer_telemetry["front_curvature_index"][fleet_id] = normalized_front_curvature_series
    observer_telemetry["center_wing_advance_gap_normalization_scale"] = center_wing_normalization_scale
    observer_telemetry["front_curvature_index_normalization_scale"] = front_curvature_normalization_scale

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
    post_elimination_extra_ticks = max(0, int(viz_settings.get("post_elimination_extra_ticks", 10)))
    archetypes = load_json_file(PROJECT_ROOT / "archetypes" / "archetypes_v1_5.json")
    metatype_settings = load_metatype_settings(base_dir, settings)
    random_seed = int(get_run_control_setting(settings, "random_seed", -1))
    metatype_random_seed = int(get_runtime_metatype_setting(settings, "random_seed", random_seed))
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
    fleet_a_color, fleet_b_color = resolve_fleet_plot_colors(fleet_a_data, fleet_b_data)

    display_language = str(get_visualization_setting(settings, "display_language", "EN")).upper()
    if display_language not in ("EN", "ZH"):
        display_language = "EN"
    fleet_a_display_name = resolve_display_name(fleet_a_data, display_language)
    fleet_b_display_name = resolve_display_name(fleet_b_data, display_language)
    fleet_a_full_name = resolve_name_with_fallback(fleet_a_data, display_language, True, "A")
    fleet_b_full_name = resolve_name_with_fallback(fleet_b_data, display_language, True, "B")
    fleet_a_avatar = resolve_avatar_with_fallback(fleet_a_data, DEFAULT_AVATAR_A)
    fleet_b_avatar = resolve_avatar_with_fallback(fleet_b_data, DEFAULT_AVATAR_B)

    fleet_a_size = int(get_fleet_setting(settings, "initial_fleet_a_size", 100))
    fleet_b_size = int(get_fleet_setting(settings, "initial_fleet_b_size", 100))
    fleet_a_aspect_ratio = float(get_fleet_setting(settings, "initial_fleet_a_aspect_ratio", 2.0))
    fleet_b_aspect_ratio = float(get_fleet_setting(settings, "initial_fleet_b_aspect_ratio", 2.0))
    unit_spacing = float(get_runtime_setting(settings, "min_unit_spacing", 1.0))
    arena_size = float(get_battlefield_setting(settings, "arena_size", 200.0))
    spawn_margin = max(1.0, arena_size * DEFAULT_SPAWN_MARGIN_RATIO)
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
        default_x=arena_size - spawn_margin,
        default_y=arena_size - spawn_margin,
    )
    fleet_a_facing_angle_deg = float(get_fleet_setting(settings, "initial_fleet_a_facing_angle_deg", 45.0))
    fleet_b_facing_angle_deg = float(get_fleet_setting(settings, "initial_fleet_b_facing_angle_deg", 225.0))
    if fleet_a_size < 1:
        raise ValueError(f"initial_fleet_a_size must be >= 1, got {fleet_a_size}")
    if fleet_b_size < 1:
        raise ValueError(f"initial_fleet_b_size must be >= 1, got {fleet_b_size}")
    if fleet_a_aspect_ratio <= 0.0:
        raise ValueError(f"initial_fleet_a_aspect_ratio must be > 0, got {fleet_a_aspect_ratio}")
    if fleet_b_aspect_ratio <= 0.0:
        raise ValueError(f"initial_fleet_b_aspect_ratio must be > 0, got {fleet_b_aspect_ratio}")
    if unit_spacing <= 0.0:
        raise ValueError(f"min_unit_spacing must be > 0, got {unit_spacing}")

    unit_speed = float(get_unit_setting(settings, "unit_speed", 1.0))
    unit_max_hit_points = float(get_unit_setting(settings, "unit_max_hit_points", 100.0))
    state = build_initial_state(
        fleet_a_params=fleet_a_params,
        fleet_b_params=fleet_b_params,
        fleet_a_size=fleet_a_size,
        fleet_b_size=fleet_b_size,
        fleet_a_aspect_ratio=fleet_a_aspect_ratio,
        fleet_b_aspect_ratio=fleet_b_aspect_ratio,
        unit_spacing=unit_spacing,
        unit_speed=unit_speed,
        unit_max_hit_points=unit_max_hit_points,
        arena_size=arena_size,
        fleet_a_origin_x=fleet_a_origin_x,
        fleet_a_origin_y=fleet_a_origin_y,
        fleet_b_origin_x=fleet_b_origin_x,
        fleet_b_origin_y=fleet_b_origin_y,
        fleet_a_facing_angle_deg=fleet_a_facing_angle_deg,
        fleet_b_facing_angle_deg=fleet_b_facing_angle_deg,
    )

    initial_fleet_sizes = {}
    for fleet_id, fleet in state.fleets.items():
        fleet_size_hp = 0.0
        for unit_id in fleet.unit_ids:
            if unit_id in state.units:
                fleet_size_hp += max(0.0, float(state.units[unit_id].hit_points))
        initial_fleet_sizes[fleet_id] = fleet_size_hp

    animate = bool(get_visualization_setting(settings, "animate", True))
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
    movement_v3a_experiment_raw = str(get_runtime_setting(settings, "movement_v3a_experiment", V3A_EXPERIMENT_BASE)).strip().lower()
    if movement_v3a_experiment_raw not in V3A_EXPERIMENT_LABELS:
        movement_v3a_experiment_raw = V3A_EXPERIMENT_BASE
    movement_v3a_experiment_effective = movement_v3a_experiment_raw
    symmetric_movement_sync_enabled = bool(get_runtime_setting(settings, "symmetric_movement_sync_enabled", True))
    hostile_contact_impedance_mode = str(
        get_contact_model_test_setting(
            settings,
            ("active_mode",),
            HOSTILE_CONTACT_IMPEDANCE_MODE_DEFAULT,
        )
    ).strip().lower()
    if hostile_contact_impedance_mode not in HOSTILE_CONTACT_IMPEDANCE_MODE_LABELS:
        hostile_contact_impedance_mode = HOSTILE_CONTACT_IMPEDANCE_MODE_OFF
    hostile_contact_impedance_strength = max(
        0.0,
        float(
            get_contact_model_test_setting(
                settings,
                ("repulsion_v1", "strength"),
                HOSTILE_CONTACT_IMPEDANCE_STRENGTH_DEFAULT,
            )
        ),
    )
    hostile_contact_impedance_radius_multiplier = max(
        1e-6,
        float(
            get_contact_model_test_setting(
                settings,
                ("repulsion_v1", "radius_multiplier"),
                HOSTILE_CONTACT_IMPEDANCE_RADIUS_MULTIPLIER_DEFAULT,
            )
        ),
    )
    if hostile_contact_impedance_mode == HOSTILE_CONTACT_IMPEDANCE_MODE_DAMPING_V2:
        v2_branch = "damping_v2"
    else:
        v2_branch = "hybrid_v2"
    hostile_contact_impedance_v2_radius_multiplier = max(
        1e-6,
        float(
            get_contact_model_test_setting(
                settings,
                (v2_branch, "radius_multiplier"),
                HOSTILE_CONTACT_IMPEDANCE_V2_RADIUS_MULTIPLIER_DEFAULT,
            )
        ),
    )
    hostile_contact_impedance_v2_repulsion_max_disp_ratio = max(
        0.0,
        float(
            get_contact_model_test_setting(
                settings,
                ("hybrid_v2", "repulsion_max_disp_ratio"),
                HOSTILE_CONTACT_IMPEDANCE_V2_REPULSION_MAX_DISP_RATIO_DEFAULT,
            )
        ),
    )
    hostile_contact_impedance_v2_forward_damping_strength = _clamp01(
        float(
            get_contact_model_test_setting(
                settings,
                (v2_branch, "forward_damping_strength"),
                HOSTILE_CONTACT_IMPEDANCE_V2_FORWARD_DAMPING_STRENGTH_DEFAULT,
            )
        )
    )
    hostile_intent_unified_spacing_scale = max(
        1e-6,
        float(
            get_contact_model_test_setting(
                settings,
                ("intent_unified_spacing_v1", "scale"),
                HOSTILE_INTENT_UNIFIED_SPACING_SCALE_DEFAULT,
            )
        ),
    )
    hostile_intent_unified_spacing_strength = _clamp01(
        float(
            get_contact_model_test_setting(
                settings,
                ("intent_unified_spacing_v1", "strength"),
                HOSTILE_INTENT_UNIFIED_SPACING_STRENGTH_DEFAULT,
            )
        )
    )
    hostile_intent_occupancy_only_scale = max(
        1e-6,
        float(
            get_contact_model_test_setting(
                settings,
                ("intent_occupancy_only_v1", "scale"),
                HOSTILE_INTENT_OCCUPANCY_ONLY_SCALE_DEFAULT,
            )
        ),
    )
    hostile_intent_occupancy_only_strength = _clamp01(
        float(
            get_contact_model_test_setting(
                settings,
                ("intent_occupancy_only_v1", "strength"),
                HOSTILE_INTENT_OCCUPANCY_ONLY_STRENGTH_DEFAULT,
            )
        )
    )
    centroid_probe_scale = float(get_runtime_setting(settings, "centroid_probe_scale", 1.0))
    pre_tl_target_substrate = str(
        get_runtime_setting(settings, "pre_tl_target_substrate", PRE_TL_TARGET_SUBSTRATE_DEFAULT)
    ).strip().lower()
    if pre_tl_target_substrate not in PRE_TL_TARGET_SUBSTRATE_LABELS:
        pre_tl_target_substrate = PRE_TL_TARGET_SUBSTRATE_DEFAULT
    if centroid_probe_scale < 0.0:
        centroid_probe_scale = 0.0
    elif centroid_probe_scale > 1.0:
        centroid_probe_scale = 1.0
    if movement_model_effective != "v3a" or movement_v3a_experiment_effective not in {
        V3A_EXPERIMENT_PRECONTACT_CENTROID_PROBE,
    }:
        centroid_probe_scale_effective = 1.0
    else:
        centroid_probe_scale_effective = centroid_probe_scale
    continuous_fr_shaping_enabled = bool(get_runtime_setting(settings, "continuous_fr_shaping_enabled", False))
    continuous_fr_shaping_mode = str(
        get_runtime_setting(settings, "continuous_fr_shaping_mode", CONTINUOUS_FR_SHAPING_OFF)
    ).strip().lower()
    if continuous_fr_shaping_mode not in CONTINUOUS_FR_SHAPING_LABELS:
        continuous_fr_shaping_mode = CONTINUOUS_FR_SHAPING_OFF
    continuous_fr_shaping_a = max(0.0, float(get_runtime_setting(settings, "continuous_fr_shaping_a", 0.0)))
    continuous_fr_shaping_sigma = max(
        1e-6, float(get_runtime_setting(settings, "continuous_fr_shaping_sigma", 0.15))
    )
    continuous_fr_shaping_p = max(0.0, float(get_runtime_setting(settings, "continuous_fr_shaping_p", 1.0)))
    continuous_fr_shaping_q = max(0.0, float(get_runtime_setting(settings, "continuous_fr_shaping_q", 1.0)))
    continuous_fr_shaping_beta = max(0.0, float(get_runtime_setting(settings, "continuous_fr_shaping_beta", 0.0)))
    continuous_fr_shaping_gamma = max(0.0, float(get_runtime_setting(settings, "continuous_fr_shaping_gamma", 0.0)))
    continuous_fr_shaping_effective = (
        movement_model_effective == "v3a"
        and movement_v3a_experiment_effective == V3A_EXPERIMENT_PRECONTACT_CENTROID_PROBE
        and continuous_fr_shaping_enabled
        and continuous_fr_shaping_mode != CONTINUOUS_FR_SHAPING_OFF
        and continuous_fr_shaping_a > 0.0
    )
    continuous_fr_shaping_mode_effective = (
        continuous_fr_shaping_mode if continuous_fr_shaping_effective else CONTINUOUS_FR_SHAPING_OFF
    )
    odw_posture_bias_enabled = bool(get_runtime_setting(settings, "odw_posture_bias_enabled", False))
    odw_posture_bias_k = float(get_runtime_setting(settings, "odw_posture_bias_k", 0.3))
    odw_posture_bias_clip_delta = float(get_runtime_setting(settings, "odw_posture_bias_clip_delta", 0.2))
    if odw_posture_bias_k < 0.0:
        odw_posture_bias_k = 0.0
    if odw_posture_bias_clip_delta < 0.0:
        odw_posture_bias_clip_delta = 0.0
    if movement_model_effective != "v3a":
        odw_posture_bias_enabled_effective = False
        odw_posture_bias_k_effective = 0.0
        odw_posture_bias_clip_delta_effective = 0.2
    else:
        odw_posture_bias_enabled_effective = odw_posture_bias_enabled
        odw_posture_bias_k_effective = odw_posture_bias_k if odw_posture_bias_enabled_effective else 0.0
        odw_posture_bias_clip_delta_effective = odw_posture_bias_clip_delta if odw_posture_bias_enabled_effective else 0.2
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
    plot_smoothing_ticks = int(get_visualization_setting(settings, "plot_smoothing_ticks", 5))
    if plot_smoothing_ticks < 1:
        plot_smoothing_ticks = 1
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
    print(f"[mode] plot_profile_effective={plot_profile_effective}")
    print(f"[mode] runtime_decision_source_effective={runtime_decision_source_effective}")
    if runtime_decision_source_effective == "v3_test":
        print(f"[runtime] v3_connect_radius_multiplier_effective={v3_connect_radius_multiplier_effective:.3f}")
        print(f"[runtime] v3_r_ref_radius_multiplier_effective={v3_r_ref_radius_multiplier_effective:.3f}")
    print(f"[mode] movement_model_effective={movement_model_effective}")
    print(f"[runtime] alpha_sep={alpha_sep:.3f}")
    if movement_model_effective == "v3a":
        print(f"[mode] movement_v3a_experiment_effective={movement_v3a_experiment_effective}")
        print(f"[mode] centroid_probe_scale_effective={centroid_probe_scale_effective:.3f}")
        print(f"[mode] pre_tl_target_substrate={pre_tl_target_substrate}")
        if symmetric_movement_sync_enabled:
            print(f"[mode] symmetric_movement_sync_enabled={symmetric_movement_sync_enabled}")
        if hostile_contact_impedance_mode != "off" or hostile_contact_impedance_strength > 0.0:
            print(f"[mode] hostile_contact_impedance_mode={hostile_contact_impedance_mode}")
            print(f"[mode] hostile_contact_impedance_strength={hostile_contact_impedance_strength:.3f}")
            print(
                "[mode] hostile_contact_impedance_radius_multiplier="
                f"{hostile_contact_impedance_radius_multiplier:.3f}"
            )
            print(
                "[mode] hostile_contact_impedance_v2="
                f"radius_multiplier={hostile_contact_impedance_v2_radius_multiplier:.3f}, "
                f"repulsion_max_disp_ratio={hostile_contact_impedance_v2_repulsion_max_disp_ratio:.3f}, "
                f"forward_damping_strength={hostile_contact_impedance_v2_forward_damping_strength:.3f}"
            )
        if hostile_intent_unified_spacing_strength > 0.0:
            print(
                "[mode] intent_unified_spacing_v1="
                f"scale={hostile_intent_unified_spacing_scale:.3f}, "
                f"strength={hostile_intent_unified_spacing_strength:.3f}"
            )
        if hostile_intent_occupancy_only_strength > 0.0:
            print(
                "[mode] intent_occupancy_only_v1="
                f"scale={hostile_intent_occupancy_only_scale:.3f}, "
                f"strength={hostile_intent_occupancy_only_strength:.3f}"
            )
        if continuous_fr_shaping_effective:
            print(f"[mode] continuous_fr_shaping_mode_effective={continuous_fr_shaping_mode_effective}")
            print(
                "[mode] continuous_fr_shaping_params="
                f"a={continuous_fr_shaping_a:.3f}, sigma={continuous_fr_shaping_sigma:.3f}, "
                f"p={continuous_fr_shaping_p:.3f}, q={continuous_fr_shaping_q:.3f}, "
                f"beta={continuous_fr_shaping_beta:.3f}, gamma={continuous_fr_shaping_gamma:.3f}"
            )
        if odw_posture_bias_enabled_effective:
            print(f"[mode] odw_posture_bias_k_effective={odw_posture_bias_k_effective:.3f}")
            print(f"[mode] odw_posture_bias_clip_delta_effective={odw_posture_bias_clip_delta_effective:.3f}")
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
    run_export_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_export_stem = f"{DEFAULT_BATTLE_REPORT_TOPIC}_{run_export_timestamp}"
    export_video_cfg = viz_settings.get("export_video", {})
    if not isinstance(export_video_cfg, dict):
        export_video_cfg = {}
    else:
        export_video_cfg = dict(export_video_cfg)
    export_video_enabled = bool(viz_settings.get("export_video_enabled", export_video_cfg.get("enabled", False)))
    export_video_enabled_override = get_env_bool("LOGH_EXPORT_VIDEO_ENABLED")
    if export_video_enabled_override is not None:
        export_video_enabled = export_video_enabled_override
    export_video_cfg["enabled"] = export_video_enabled
    raw_video_output_path = str(export_video_cfg.get("output_path", DEFAULT_VIDEO_EXPORT_DIR))
    resolved_video_output_path = resolve_timestamped_video_output_path(
        raw_video_output_path,
        base_dir=base_dir,
        export_stem=f"{run_export_stem}_video",
    )
    export_video_cfg["output_path"] = str(resolved_video_output_path)
    export_video_cfg["output_path_is_final"] = True

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
        pre_tl_target_substrate=pre_tl_target_substrate,
        symmetric_movement_sync_enabled=symmetric_movement_sync_enabled,
        hostile_contact_impedance_mode=hostile_contact_impedance_mode,
        hostile_contact_impedance_strength=hostile_contact_impedance_strength,
        hostile_contact_impedance_radius_multiplier=hostile_contact_impedance_radius_multiplier,
        hostile_contact_impedance_v2_radius_multiplier=hostile_contact_impedance_v2_radius_multiplier,
        hostile_contact_impedance_v2_repulsion_max_disp_ratio=hostile_contact_impedance_v2_repulsion_max_disp_ratio,
        hostile_contact_impedance_v2_forward_damping_strength=hostile_contact_impedance_v2_forward_damping_strength,
        hostile_intent_unified_spacing_scale=hostile_intent_unified_spacing_scale,
        hostile_intent_unified_spacing_strength=hostile_intent_unified_spacing_strength,
        hostile_intent_occupancy_only_scale=hostile_intent_occupancy_only_scale,
        hostile_intent_occupancy_only_strength=hostile_intent_occupancy_only_strength,
        continuous_fr_shaping_enabled=continuous_fr_shaping_effective,
        continuous_fr_shaping_mode=continuous_fr_shaping_mode_effective,
        continuous_fr_shaping_a=continuous_fr_shaping_a,
        continuous_fr_shaping_sigma=continuous_fr_shaping_sigma,
        continuous_fr_shaping_p=continuous_fr_shaping_p,
        continuous_fr_shaping_q=continuous_fr_shaping_q,
        continuous_fr_shaping_beta=continuous_fr_shaping_beta,
        continuous_fr_shaping_gamma=continuous_fr_shaping_gamma,
        odw_posture_bias_enabled=odw_posture_bias_enabled_effective,
        odw_posture_bias_k=odw_posture_bias_k_effective,
        odw_posture_bias_clip_delta=odw_posture_bias_clip_delta_effective,
        v3_connect_radius_multiplier=v3_connect_radius_multiplier_effective,
        v3_r_ref_radius_multiplier=v3_r_ref_radius_multiplier_effective,
        post_elimination_extra_ticks=post_elimination_extra_ticks,
    )
    if not animate:
        position_frames = []

    max_time_steps_effective = int(final_state.tick)
    run_config_snapshot = {
        "initial_units_per_side": int(fleet_a_size) if fleet_a_size == fleet_b_size else int(max(fleet_a_size, fleet_b_size)),
        "initial_units_a": int(fleet_a_size),
        "initial_units_b": int(fleet_b_size),
        "initial_fleet_a_aspect_ratio": fleet_a_aspect_ratio,
        "initial_fleet_b_aspect_ratio": fleet_b_aspect_ratio,
        "initial_fleet_a_origin_x": fleet_a_origin_x,
        "initial_fleet_a_origin_y": fleet_a_origin_y,
        "initial_fleet_b_origin_x": fleet_b_origin_x,
        "initial_fleet_b_origin_y": fleet_b_origin_y,
        "initial_fleet_a_facing_angle_deg": fleet_a_facing_angle_deg,
        "initial_fleet_b_facing_angle_deg": fleet_b_facing_angle_deg,
        "test_mode": test_mode,
        "test_mode_label": test_mode_name,
        "metatype_settings_path": str(
            get_runtime_metatype_setting(settings, "settings_path", DEFAULT_METATYPE_SETTINGS_PATH)
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
        "pre_tl_target_substrate": pre_tl_target_substrate if movement_model_effective == "v3a" else "N/A",
        "symmetric_movement_sync_enabled": (
            symmetric_movement_sync_enabled if movement_model_effective == "v3a" else "N/A"
        ),
        "hostile_contact_impedance_mode": hostile_contact_impedance_mode,
        "hostile_contact_impedance_strength": hostile_contact_impedance_strength,
        "hostile_contact_impedance_radius_multiplier": hostile_contact_impedance_radius_multiplier,
        "hostile_contact_impedance_v2_radius_multiplier": hostile_contact_impedance_v2_radius_multiplier,
        "hostile_contact_impedance_v2_repulsion_max_disp_ratio": hostile_contact_impedance_v2_repulsion_max_disp_ratio,
        "hostile_contact_impedance_v2_forward_damping_strength": hostile_contact_impedance_v2_forward_damping_strength,
        "hostile_intent_unified_spacing_scale": hostile_intent_unified_spacing_scale,
        "hostile_intent_unified_spacing_strength": hostile_intent_unified_spacing_strength,
        "hostile_intent_occupancy_only_scale": hostile_intent_occupancy_only_scale,
        "hostile_intent_occupancy_only_strength": hostile_intent_occupancy_only_strength,
        "continuous_fr_shaping_enabled_effective": (
            continuous_fr_shaping_effective if movement_model_effective == "v3a" else "N/A"
        ),
        "continuous_fr_shaping_mode_effective": (
            continuous_fr_shaping_mode_effective if movement_model_effective == "v3a" else "N/A"
        ),
        "continuous_fr_shaping_a_effective": (
            continuous_fr_shaping_a if continuous_fr_shaping_effective else 0.0
        ),
        "continuous_fr_shaping_sigma_effective": (
            continuous_fr_shaping_sigma if continuous_fr_shaping_effective else 0.0
        ),
        "continuous_fr_shaping_p_effective": (
            continuous_fr_shaping_p if continuous_fr_shaping_effective else 0.0
        ),
        "continuous_fr_shaping_q_effective": (
            continuous_fr_shaping_q if continuous_fr_shaping_effective else 0.0
        ),
        "continuous_fr_shaping_beta_effective": (
            continuous_fr_shaping_beta if continuous_fr_shaping_effective else 0.0
        ),
        "continuous_fr_shaping_gamma_effective": (
            continuous_fr_shaping_gamma if continuous_fr_shaping_effective else 0.0
        ),
        "odw_posture_bias_enabled_effective": (
            odw_posture_bias_enabled_effective if movement_model_effective == "v3a" else "N/A"
        ),
        "odw_posture_bias_k_effective": (
            odw_posture_bias_k_effective if movement_model_effective == "v3a" else "N/A"
        ),
        "odw_posture_bias_clip_delta_effective": (
            odw_posture_bias_clip_delta_effective if movement_model_effective == "v3a" else "N/A"
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

    remaining_units_a_final = int(alive_trajectory.get("A", [0])[-1]) if alive_trajectory.get("A") else 0
    remaining_units_b_final = int(alive_trajectory.get("B", [0])[-1]) if alive_trajectory.get("B") else 0
    winner_decided = ((remaining_units_a_final <= 0) != (remaining_units_b_final <= 0))
    battle_report_export_allowed = bool(export_battle_report) and int(final_state.tick) >= 100 and winner_decided

    if export_battle_report and not battle_report_export_allowed:
        skip_reasons = []
        if int(final_state.tick) < 100:
            skip_reasons.append(f"ticks<{100} ({int(final_state.tick)})")
        if not winner_decided:
            skip_reasons.append(
                f"winner_undecided (remaining A/B={remaining_units_a_final}/{remaining_units_b_final})"
            )
        print(f"[report] battle_report_skipped={'; '.join(skip_reasons)}")

    if battle_report_export_allowed:
        report_markdown = build_battle_report_markdown(
            settings_source_path=str((base_dir / "test_run_v1_0.settings.json").as_posix()),
            display_language=display_language,
            random_seed_effective=effective_random_seed,
            fleet_a_data=fleet_a_data,
            fleet_b_data=fleet_b_data,
            initial_fleet_sizes=initial_fleet_sizes,
            alive_trajectory=alive_trajectory,
            fleet_size_trajectory=fleet_size_trajectory,
            observer_telemetry=observer_telemetry,
            combat_telemetry=combat_telemetry,
            bridge_telemetry=bridge_telemetry,
            collapse_shadow_telemetry=collapse_shadow_telemetry,
            final_state=final_state,
            run_config_snapshot=run_config_snapshot,
        )
        report_date_dir = run_export_timestamp[:8]
        report_export_dir = (base_dir.parent / DEFAULT_BATTLE_REPORT_EXPORT_DIR / report_date_dir).resolve()
        report_export_dir.mkdir(parents=True, exist_ok=True)
        report_filename = f"{run_export_stem}_Battle_Report_Framework_v1.0.md"
        report_output_path = report_export_dir / report_filename
        report_output_path.write_text(report_markdown, encoding="utf-8")
        print(f"[report] battle_report_exported={report_output_path}")

    if not animate:
        return

    def _first_contact_tick_from_combat(combat_data: Mapping[str, Any]) -> int | None:
        series = combat_data.get("in_contact_count", [])
        if not isinstance(series, Sequence):
            return None
        for idx, value in enumerate(series, start=1):
            try:
                in_contact = int(value)
            except (TypeError, ValueError):
                continue
            if in_contact > 0:
                return idx
        return None

    bridge_ticks_debug = compute_bridge_event_ticks(bridge_telemetry if isinstance(bridge_telemetry, dict) else None)
    first_contact_tick_debug = _first_contact_tick_from_combat(combat_telemetry if isinstance(combat_telemetry, Mapping) else {})

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
        plot_smoothing_ticks=plot_smoothing_ticks,
        damage_per_tick=damage_per_tick,
        combat_telemetry=combat_telemetry,
        debug_context={
            "test_mode_label": TEST_MODE_LABELS.get(test_mode, "default"),
            "movement_model_effective": movement_model_effective,
            "cohesion_decision_source_effective": runtime_decision_source_effective,
            "pre_tl_target_substrate": pre_tl_target_substrate,
            "symmetric_movement_sync_enabled": symmetric_movement_sync_enabled,
            "continuous_fr_shaping_effective": continuous_fr_shaping_effective,
            "continuous_fr_shaping_mode_effective": continuous_fr_shaping_mode_effective,
            "odw_posture_bias_enabled_effective": odw_posture_bias_enabled_effective,
            "odw_posture_bias_k_effective": odw_posture_bias_k_effective,
            "odw_posture_bias_clip_delta_effective": odw_posture_bias_clip_delta_effective,
            "v3_connect_radius_multiplier_effective": v3_connect_radius_multiplier_effective,
            "plot_smoothing_ticks": plot_smoothing_ticks,
            "first_contact_tick": first_contact_tick_debug,
            "formation_cut_tick": bridge_ticks_debug.get("formation_cut_tick"),
            "pocket_formation_tick": bridge_ticks_debug.get("pocket_formation_tick"),
        },
        export_video_cfg=export_video_cfg,
        boundary_enabled=boundary_enabled,
        boundary_hard_enabled=boundary_hard_enabled,
    )


if __name__ == "__main__":
    main()
