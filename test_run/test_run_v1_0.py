import math
import os
import random
import re
import sys
from collections.abc import Sequence
from dataclasses import replace
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Core runtime / engine types used directly by the v1_0 test harness core.
from runtime.runtime_v0_1 import (
    PersonalityParameters,
    Vec2,
    UnitState,
    BattleState,
)
from runtime.engine_skeleton import EngineTickSkeleton

# Core keeps only the settings helpers it uses directly. Launcher/report/
# experiment wiring now imports its own modules explicitly.
from test_run.settings_accessor import (
    get_battlefield_setting,
    get_collapse_shadow_setting,
    get_event_bridge_setting,
    get_fleet_setting,
    get_run_control_setting,
    get_runtime_setting,
    get_runtime_metatype_setting,
    get_unit_setting,
    load_json_file,
    resolve_optional_json_path,
)
from test_run.test_run_execution import (
    SimulationBoundaryConfig,
    SimulationContactConfig,
    SimulationExecutionConfig,
    SimulationMovementConfig,
    SimulationObserverConfig,
    SimulationRuntimeConfig,
    run_simulation,
)
from test_run.test_run_scenario import build_initial_state
from test_run.test_run_telemetry import compute_formation_snapshot_metrics


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
HOSTILE_CONTACT_IMPEDANCE_MODE_HYBRID_V2 = "hybrid_v2"
HOSTILE_CONTACT_IMPEDANCE_MODE_INTENT_UNIFIED_SPACING_V1 = "intent_unified_spacing_v1"
HOSTILE_CONTACT_IMPEDANCE_MODE_LABELS = {
    HOSTILE_CONTACT_IMPEDANCE_MODE_OFF,
    HOSTILE_CONTACT_IMPEDANCE_MODE_HYBRID_V2,
    HOSTILE_CONTACT_IMPEDANCE_MODE_INTENT_UNIFIED_SPACING_V1,
}
HOSTILE_CONTACT_IMPEDANCE_MODE_DEFAULT = HOSTILE_CONTACT_IMPEDANCE_MODE_OFF
HOSTILE_CONTACT_IMPEDANCE_V2_RADIUS_MULTIPLIER_DEFAULT = 1.50
HOSTILE_CONTACT_IMPEDANCE_V2_REPULSION_MAX_DISP_RATIO_DEFAULT = 0.20
HOSTILE_CONTACT_IMPEDANCE_V2_FORWARD_DAMPING_STRENGTH_DEFAULT = 0.50
HOSTILE_INTENT_UNIFIED_SPACING_SCALE_DEFAULT = 1.00
HOSTILE_INTENT_UNIFIED_SPACING_STRENGTH_DEFAULT = 1.00
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
DEFAULT_AVATAR_A = "avatar_reinhard"
DEFAULT_AVATAR_B = "avatar_yang"
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
        if mode != HOSTILE_CONTACT_IMPEDANCE_MODE_INTENT_UNIFIED_SPACING_V1:
            return state

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
        if mode != HOSTILE_CONTACT_IMPEDANCE_MODE_INTENT_UNIFIED_SPACING_V1:
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
            if mode == HOSTILE_CONTACT_IMPEDANCE_MODE_HYBRID_V2 and forward_disp > 0.0:
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
        if mode == HOSTILE_CONTACT_IMPEDANCE_MODE_INTENT_UNIFIED_SPACING_V1:
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


# Launcher-facing helper surface.
# These remain in core for now because the maintained scenario/entry layer
# still uses this module as the stable engine/helper anchor.
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


# Runtime-adjacent utility helpers used by the launcher layer.
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


def main() -> None:
    from test_run.test_run_entry import main as launcher_main

    launcher_main()


if __name__ == "__main__":
    main()
