import math
from collections.abc import Mapping, Sequence
from dataclasses import replace
from typing import Any

from runtime.engine_skeleton import EngineTickSkeleton
from runtime.runtime_v0_1 import BattleState, PersonalityParameters, UnitState, Vec2

from test_run.test_run_telemetry import (
    compute_bridge_metrics_per_side,
    compute_collapse_v2_shadow_telemetry,
    compute_formation_snapshot_metrics,
    compute_hostile_intermix_metrics,
    extract_runtime_debug_payload,
)


DEFAULT_FRAME_STRIDE = 1
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
PRE_TL_TARGET_SUBSTRATE_DEFAULT = "nearest5_centroid"
HOSTILE_CONTACT_IMPEDANCE_MODE_OFF = "off"
HOSTILE_CONTACT_IMPEDANCE_MODE_HYBRID_V2 = "hybrid_v2"
HOSTILE_CONTACT_IMPEDANCE_MODE_INTENT_UNIFIED_SPACING_V1 = "intent_unified_spacing_v1"
HOSTILE_CONTACT_IMPEDANCE_MODE_LABELS = {
    HOSTILE_CONTACT_IMPEDANCE_MODE_OFF,
    HOSTILE_CONTACT_IMPEDANCE_MODE_HYBRID_V2,
    HOSTILE_CONTACT_IMPEDANCE_MODE_INTENT_UNIFIED_SPACING_V1,
}
HOSTILE_CONTACT_IMPEDANCE_MODE_DEFAULT = "off"
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
BRIDGE_THETA_SPLIT_DEFAULT = 1.715
BRIDGE_THETA_ENV_DEFAULT = 0.583
BRIDGE_SUSTAIN_TICKS_DEFAULT = 20
COLLAPSE_V2_SHADOW_ATTRITION_WINDOW_DEFAULT = 20
COLLAPSE_V2_SHADOW_SUSTAIN_TICKS_DEFAULT = 10
COLLAPSE_V2_SHADOW_MIN_CONDITIONS_DEFAULT = 2
COLLAPSE_V2_SHADOW_THETA_CONN_DEFAULT = 0.10
COLLAPSE_V2_SHADOW_THETA_COH_DEFAULT = 0.98
COLLAPSE_V2_SHADOW_THETA_FORCE_DEFAULT = 0.95
COLLAPSE_V2_SHADOW_THETA_ATTR_DEFAULT = 0.10

SimulationExecutionConfig = dict
SimulationMovementConfig = dict
SimulationContactConfig = dict
SimulationBoundaryConfig = dict
SimulationRuntimeConfig = dict
SimulationObserverConfig = dict
FIXTURE_MODE_BATTLE = "battle"
FIXTURE_MODE_NEUTRAL_TRANSIT_V1 = "neutral_transit_v1"
FIXTURE_LINEAR_ARRIVAL_GAIN_MIN_STOP_RADIUS = 1e-12
FIXTURE_MODE_LABELS = {
    FIXTURE_MODE_BATTLE,
    FIXTURE_MODE_NEUTRAL_TRANSIT_V1,
}
OBJECTIVE_CONTRACT_3D_SOURCE_OWNER_FIXTURE = "fixture"
OBJECTIVE_CONTRACT_3D_MODE_POINT_ANCHOR = "point_anchor"
OBJECTIVE_CONTRACT_3D_NO_ENEMY_SEMANTICS = "enemy_term_zero"


def _clamp01(value: float) -> float:
    return min(1.0, max(0.0, value))


def _require_mapping(cfg: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    section = cfg.get(key)
    if not isinstance(section, Mapping):
        raise TypeError(f"run_simulation requires '{key}' to be a mapping, got {type(section).__name__}")
    return section


def _sigmoid(value: float) -> float:
    if value >= 0.0:
        z = math.exp(-value)
        return 1.0 / (1.0 + z)
    z = math.exp(value)
    return z / (1.0 + z)


def _normalize_fixture_objective_contract_3d(contract_cfg: Any) -> tuple[dict[str, Any], tuple[float, float]]:
    if not isinstance(contract_cfg, Mapping):
        raise TypeError(
            "neutral_transit_v1 execution_cfg['fixture']['objective_contract_3d'] must be a mapping"
        )
    if "transit_axis_hint_xyz" in contract_cfg:
        raise ValueError(
            "neutral_transit_v1 first implementation must not set "
            "execution_cfg['fixture']['objective_contract_3d']['transit_axis_hint_xyz']"
        )
    anchor_point_xyz = contract_cfg.get("anchor_point_xyz")
    if (
        not isinstance(anchor_point_xyz, Sequence)
        or isinstance(anchor_point_xyz, (str, bytes))
        or len(anchor_point_xyz) != 3
    ):
        raise TypeError(
            "neutral_transit_v1 execution_cfg['fixture']['objective_contract_3d']['anchor_point_xyz'] "
            "must be a 3-item sequence"
        )
    normalized_contract = {
        "anchor_point_xyz": (
            float(anchor_point_xyz[0]),
            float(anchor_point_xyz[1]),
            float(anchor_point_xyz[2]),
        ),
        "source_owner": str(contract_cfg.get("source_owner", "")).strip(),
        "objective_mode": str(contract_cfg.get("objective_mode", "")).strip(),
        "no_enemy_semantics": str(contract_cfg.get("no_enemy_semantics", "")).strip(),
    }
    if normalized_contract["source_owner"] != OBJECTIVE_CONTRACT_3D_SOURCE_OWNER_FIXTURE:
        raise ValueError(
            "neutral_transit_v1 execution_cfg['fixture']['objective_contract_3d']['source_owner'] "
            f"must be {OBJECTIVE_CONTRACT_3D_SOURCE_OWNER_FIXTURE!r}, got {normalized_contract['source_owner']!r}"
        )
    if normalized_contract["objective_mode"] != OBJECTIVE_CONTRACT_3D_MODE_POINT_ANCHOR:
        raise ValueError(
            "neutral_transit_v1 execution_cfg['fixture']['objective_contract_3d']['objective_mode'] "
            f"must be {OBJECTIVE_CONTRACT_3D_MODE_POINT_ANCHOR!r}, got {normalized_contract['objective_mode']!r}"
        )
    if normalized_contract["no_enemy_semantics"] != OBJECTIVE_CONTRACT_3D_NO_ENEMY_SEMANTICS:
        raise ValueError(
            "neutral_transit_v1 execution_cfg['fixture']['objective_contract_3d']['no_enemy_semantics'] "
            f"must be {OBJECTIVE_CONTRACT_3D_NO_ENEMY_SEMANTICS!r}, got {normalized_contract['no_enemy_semantics']!r}"
        )
    return normalized_contract, (
        float(normalized_contract["anchor_point_xyz"][0]),
        float(normalized_contract["anchor_point_xyz"][1]),
    )


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

    def _evaluate_target_with_fixture_objective(self, state: BattleState) -> BattleState | None:
        fixture_cfg = getattr(self, "TEST_RUN_FIXTURE_CFG", None)
        if not isinstance(fixture_cfg, Mapping):
            return None
        active_mode = str(fixture_cfg.get("active_mode", FIXTURE_MODE_BATTLE)).strip().lower()
        if active_mode != FIXTURE_MODE_NEUTRAL_TRANSIT_V1:
            return None
        if len(state.fleets) != 1:
            return None

        fleet_id, fleet = next(iter(state.fleets.items()))
        objective_contract_3d = fixture_cfg.get("objective_contract_3d")
        if not isinstance(objective_contract_3d, Mapping):
            raise TypeError("neutral_transit_v1 engine fixture config requires objective_contract_3d mapping")
        anchor_point_xyz = objective_contract_3d.get("anchor_point_xyz")
        objective_point_xy = (
            float(anchor_point_xyz[0]),
            float(anchor_point_xyz[1]),
        )
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
        if enemy_units:
            return None
        if not own_units:
            direction = (0.0, 0.0)
            intensity = 0.0
        else:
            centroid_x, centroid_y = self._compute_position_centroid(own_units)
            normalized_direction, _ = self._normalize_direction(
                float(objective_point_xy[0]) - centroid_x,
                float(objective_point_xy[1]) - centroid_y,
            )
            stop_radius = float(fixture_cfg.get("stop_radius", 0.0))
            if stop_radius > FIXTURE_LINEAR_ARRIVAL_GAIN_MIN_STOP_RADIUS:
                distance_to_objective = math.sqrt(
                    ((float(objective_point_xy[0]) - centroid_x) ** 2)
                    + ((float(objective_point_xy[1]) - centroid_y) ** 2)
                )
                arrival_gain = max(0.0, min(1.0, distance_to_objective / stop_radius))
            else:
                arrival_gain = 1.0
            direction = (
                float(normalized_direction[0]) * arrival_gain,
                float(normalized_direction[1]) * arrival_gain,
            )
            intensity = float(arrival_gain)
        return replace(
            state,
            last_target_direction={fleet_id: direction},
            last_engagement_intensity={fleet_id: intensity},
        )

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
        fixture_state = self._evaluate_target_with_fixture_objective(state)
        if fixture_state is not None:
            return fixture_state
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
            speed_scale = max(0.0, 1.0 - (strength * signal))
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
        movement_surface = getattr(self, "_movement_surface", {})
        movement_v3a_experiment = str(movement_surface.get("v3a_experiment", "base")).strip().lower()
        shaping_enabled = bool(getattr(self, "CONTINUOUS_FR_SHAPING_ENABLED", False))
        shaping_mode = str(
            getattr(self, "CONTINUOUS_FR_SHAPING_MODE", CONTINUOUS_FR_SHAPING_OFF)
        ).strip().lower()
        if (
            not shaping_enabled
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
        fixture_cfg = getattr(self, "TEST_RUN_FIXTURE_CFG", None)
        if isinstance(fixture_cfg, dict) and str(fixture_cfg.get("active_mode", "")).strip().lower() == FIXTURE_MODE_NEUTRAL_TRANSIT_V1:
            fixture_fleet_id = str(fixture_cfg.get("fleet_id", "")).strip()
            objective_contract_3d = fixture_cfg.get("objective_contract_3d")
            stop_radius = float(fixture_cfg.get("stop_radius", 0.0))
            late_clamp_active_for_tick = False
            late_clamp_overshoot = 0.0
            late_clamp_dx = 0.0
            late_clamp_dy = 0.0
            if fixture_fleet_id and isinstance(objective_contract_3d, Mapping) and stop_radius > 0.0:
                anchor_point_xyz = objective_contract_3d.get("anchor_point_xyz")
                if isinstance(anchor_point_xyz, (list, tuple)) and len(anchor_point_xyz) >= 2:
                    _, pre_centroid_x, pre_centroid_y = self._collect_alive_fleet_positions(next_state, fixture_fleet_id)
                    alive_rows, post_centroid_x, post_centroid_y = self._collect_alive_fleet_positions(moved_state, fixture_fleet_id)
                    axis_dx = float(anchor_point_xyz[0]) - float(pre_centroid_x)
                    axis_dy = float(anchor_point_xyz[1]) - float(pre_centroid_y)
                    remaining_distance = math.sqrt((axis_dx * axis_dx) + (axis_dy * axis_dy))
                    if alive_rows and remaining_distance > 1e-12 and remaining_distance <= stop_radius:
                        late_clamp_active_for_tick = True
                        axis_x = axis_dx / remaining_distance
                        axis_y = axis_dy / remaining_distance
                        realized_forward_advance = (
                            ((float(post_centroid_x) - float(pre_centroid_x)) * axis_x)
                            + ((float(post_centroid_y) - float(pre_centroid_y)) * axis_y)
                        )
                        if realized_forward_advance > remaining_distance:
                            overshoot = realized_forward_advance - remaining_distance
                            late_clamp_overshoot = float(overshoot)
                            late_clamp_dx = float(-(overshoot * axis_x))
                            late_clamp_dy = float(-(overshoot * axis_y))
                            corrected_units = dict(moved_state.units)
                            for unit_id in moved_state.fleets[fixture_fleet_id].unit_ids:
                                unit = corrected_units.get(unit_id)
                                if unit is None or float(unit.hit_points) <= 0.0:
                                    continue
                                corrected_units[unit_id] = replace(
                                    unit,
                                    position=Vec2(
                                        x=float(unit.position.x) - (overshoot * axis_x),
                                        y=float(unit.position.y) - (overshoot * axis_y),
                                    ),
                                )
                            moved_state = replace(moved_state, units=corrected_units)
            pending_diag = self._debug_state.get("diag_pending")
            if isinstance(pending_diag, dict) and int(pending_diag.get("tick", -1)) == int(next_state.tick):
                fixture_trace = pending_diag.get("fixture_terminal_trace")
                if isinstance(fixture_trace, dict):
                    trace_units = fixture_trace.get("units")
                    if isinstance(trace_units, dict):
                        for unit_id, row in trace_units.items():
                            if not isinstance(row, dict):
                                continue
                            unit = moved_state.units.get(unit_id)
                            if unit is None:
                                continue
                            x_pre = float(row.get("x_pre", unit.position.x))
                            y_pre = float(row.get("y_pre", unit.position.y))
                            x_post = float(unit.position.x)
                            y_post = float(unit.position.y)
                            realized_dx = x_post - x_pre
                            realized_dy = y_post - y_pre
                            row["x_post"] = x_post
                            row["y_post"] = y_post
                            row["realized_dx"] = float(realized_dx)
                            row["realized_dy"] = float(realized_dy)
                            row["realized_disp_norm"] = float(math.sqrt((realized_dx * realized_dx) + (realized_dy * realized_dy)))
                            row["late_clamp_active_for_tick"] = bool(late_clamp_active_for_tick)
                            row["late_clamp_overshoot"] = float(late_clamp_overshoot)
                            row["late_clamp_dx"] = float(late_clamp_dx)
                            row["late_clamp_dy"] = float(late_clamp_dy)
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
        iqr = max(0.0, q75 - q25)

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
        disc = max(0.0, (trace * trace) - (4.0 * det))
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

    def evaluate_cohesion(self, state: BattleState) -> BattleState:
        return super().evaluate_cohesion(state)

def run_simulation(
    initial_state: BattleState,
    *,
    engine_cls: Any | None,
    execution_cfg: Mapping[str, Any],
    runtime_cfg: Mapping[str, Any],
    observer_cfg: Mapping[str, Any],
):
    if engine_cls is None:
        raise ValueError("run_simulation requires an explicit engine_cls")

    movement_cfg = _require_mapping(runtime_cfg, "movement")
    contact_cfg = _require_mapping(runtime_cfg, "contact")
    boundary_cfg = _require_mapping(runtime_cfg, "boundary")
    bridge_cfg = _require_mapping(observer_cfg, "bridge")
    collapse_shadow_cfg = _require_mapping(observer_cfg, "collapse_shadow")
    fixture_cfg = execution_cfg.get("fixture", {})
    if fixture_cfg is None:
        fixture_cfg = {}
    if not isinstance(fixture_cfg, Mapping):
        raise TypeError(f"run_simulation requires execution_cfg['fixture'] to be a mapping, got {type(fixture_cfg).__name__}")
    fixture_active_mode = str(fixture_cfg.get("active_mode", FIXTURE_MODE_BATTLE)).strip().lower() or FIXTURE_MODE_BATTLE
    if fixture_active_mode not in FIXTURE_MODE_LABELS:
        raise ValueError(
            f"run_simulation execution_cfg['fixture']['active_mode'] must be one of {sorted(FIXTURE_MODE_LABELS)}, "
            f"got {fixture_active_mode!r}"
        )
    fixture_active = fixture_active_mode == FIXTURE_MODE_NEUTRAL_TRANSIT_V1
    fixture_fleet_id = ""
    fixture_objective_point_xy = (0.0, 0.0)
    fixture_objective_contract_3d: dict[str, Any] = {}
    fixture_stop_radius = 0.0
    if fixture_active:
        if len(initial_state.fleets) != 1:
            raise ValueError(
                "neutral_transit_v1 requires a single-fleet initial_state, "
                f"got fleet_ids={list(initial_state.fleets.keys())}"
            )
        fixture_fleet_id = str(fixture_cfg.get("fleet_id", next(iter(initial_state.fleets.keys())))).strip()
        if fixture_fleet_id not in initial_state.fleets:
            raise ValueError(
                "neutral_transit_v1 fixture fleet_id must exist in initial_state.fleets, "
                f"got {fixture_fleet_id!r}"
            )
        fixture_objective_contract_3d, projected_anchor_point_xy = _normalize_fixture_objective_contract_3d(
            fixture_cfg.get("objective_contract_3d")
        )
        fixture_objective_point_xy = projected_anchor_point_xy
        fixture_stop_radius = float(fixture_cfg.get("stop_radius", 0.0))
        if fixture_stop_radius < 0.0:
            raise ValueError(
                "neutral_transit_v1 execution_cfg['fixture']['stop_radius'] must be >= 0, "
                f"got {fixture_stop_radius}"
            )
    continuous_fr_shaping_cfg = movement_cfg.get("continuous_fr_shaping", {})
    if not isinstance(continuous_fr_shaping_cfg, Mapping):
        continuous_fr_shaping_cfg = {}
    odw_posture_bias_cfg = movement_cfg.get("odw_posture_bias", {})
    if not isinstance(odw_posture_bias_cfg, Mapping):
        odw_posture_bias_cfg = {}
    hybrid_v2_cfg = contact_cfg.get("hybrid_v2", {})
    if not isinstance(hybrid_v2_cfg, Mapping):
        hybrid_v2_cfg = {}
    intent_unified_spacing_cfg = contact_cfg.get("intent_unified_spacing_v1", {})
    if not isinstance(intent_unified_spacing_cfg, Mapping):
        intent_unified_spacing_cfg = {}
    steps = int(execution_cfg["steps"])
    capture_positions = bool(execution_cfg["capture_positions"])
    capture_hit_points = bool(execution_cfg.get("capture_hit_points", False))
    frame_stride = int(execution_cfg["frame_stride"])
    include_target_lines = bool(execution_cfg["include_target_lines"])
    print_tick_summary = bool(execution_cfg["print_tick_summary"])
    observer_enabled = bool(observer_cfg["enabled"])
    post_elimination_extra_ticks = max(0, int(execution_cfg.get("post_elimination_extra_ticks", 10)))
    movement_model = str(runtime_cfg["movement_model"]).strip().lower() or "v3a"
    if movement_model not in {"v3a", "v4a"}:
        raise ValueError(
            "test_run maintained path only supports runtime_cfg['movement_model'] in {'v3a', 'v4a'}, "
            f"got {runtime_cfg['movement_model']!r}"
        )

    engine = engine_cls(
        attack_range=float(contact_cfg["attack_range"]),
        damage_per_tick=float(contact_cfg["damage_per_tick"]),
        separation_radius=float(contact_cfg["separation_radius"]),
    )
    if fixture_active:
        engine.TEST_RUN_FIXTURE_CFG = {
            "active_mode": fixture_active_mode,
            "fleet_id": fixture_fleet_id,
            "objective_contract_3d": dict(fixture_objective_contract_3d),
            "stop_radius": fixture_stop_radius,
        }
    for attr, value in (
        (
            "PRE_TL_TARGET_SUBSTRATE",
            str(movement_cfg.get("pre_tl_target_substrate", PRE_TL_TARGET_SUBSTRATE_DEFAULT)).strip().lower()
            or PRE_TL_TARGET_SUBSTRATE_DEFAULT,
        ),
        ("SYMMETRIC_MOVEMENT_SYNC_ENABLED", bool(movement_cfg.get("symmetric_movement_sync_enabled", True))),
        (
            "HOSTILE_CONTACT_IMPEDANCE_MODE",
            str(contact_cfg.get("hostile_contact_impedance_mode", HOSTILE_CONTACT_IMPEDANCE_MODE_DEFAULT)).strip().lower()
            or HOSTILE_CONTACT_IMPEDANCE_MODE_DEFAULT,
        ),
        (
            "HOSTILE_CONTACT_IMPEDANCE_V2_RADIUS_MULTIPLIER",
            max(1e-6, float(hybrid_v2_cfg.get("radius_multiplier", HOSTILE_CONTACT_IMPEDANCE_V2_RADIUS_MULTIPLIER_DEFAULT))),
        ),
        (
            "HOSTILE_CONTACT_IMPEDANCE_V2_REPULSION_MAX_DISP_RATIO",
            max(
                0.0,
                float(hybrid_v2_cfg.get("repulsion_max_disp_ratio", HOSTILE_CONTACT_IMPEDANCE_V2_REPULSION_MAX_DISP_RATIO_DEFAULT)),
            ),
        ),
        (
            "HOSTILE_CONTACT_IMPEDANCE_V2_FORWARD_DAMPING_STRENGTH",
            _clamp01(
                float(hybrid_v2_cfg.get("forward_damping_strength", HOSTILE_CONTACT_IMPEDANCE_V2_FORWARD_DAMPING_STRENGTH_DEFAULT))
            ),
        ),
        (
            "HOSTILE_INTENT_UNIFIED_SPACING_SCALE",
            max(1e-6, float(intent_unified_spacing_cfg.get("scale", HOSTILE_INTENT_UNIFIED_SPACING_SCALE_DEFAULT))),
        ),
        (
            "HOSTILE_INTENT_UNIFIED_SPACING_STRENGTH",
            _clamp01(float(intent_unified_spacing_cfg.get("strength", HOSTILE_INTENT_UNIFIED_SPACING_STRENGTH_DEFAULT))),
        ),
        ("CONTINUOUS_FR_SHAPING_ENABLED", bool(continuous_fr_shaping_cfg.get("effective", False))),
        (
            "CONTINUOUS_FR_SHAPING_MODE",
            str(continuous_fr_shaping_cfg.get("mode_effective", CONTINUOUS_FR_SHAPING_OFF)).strip().lower()
            or CONTINUOUS_FR_SHAPING_OFF,
        ),
        ("CONTINUOUS_FR_SHAPING_A", max(0.0, float(continuous_fr_shaping_cfg.get("a", 0.0)))),
        ("CONTINUOUS_FR_SHAPING_SIGMA", max(1e-6, float(continuous_fr_shaping_cfg.get("sigma", 0.15)))),
        ("CONTINUOUS_FR_SHAPING_P", max(0.0, float(continuous_fr_shaping_cfg.get("p", 1.0)))),
        ("CONTINUOUS_FR_SHAPING_Q", max(0.0, float(continuous_fr_shaping_cfg.get("q", 1.0)))),
        ("CONTINUOUS_FR_SHAPING_BETA", max(0.0, float(continuous_fr_shaping_cfg.get("beta", 0.0)))),
        ("CONTINUOUS_FR_SHAPING_GAMMA", max(0.0, float(continuous_fr_shaping_cfg.get("gamma", 0.0)))),
        ("V2_CONNECT_RADIUS_MULTIPLIER", max(1e-12, float(movement_cfg.get("v2_connect_radius_multiplier", 1.0)))),
        ("V3_CONNECT_RADIUS_MULTIPLIER", max(1e-12, float(movement_cfg.get("v3_connect_radius_multiplier_effective", 1.0)))),
        ("V3_R_REF_RADIUS_MULTIPLIER", max(1e-12, float(movement_cfg.get("v3_r_ref_radius_multiplier_effective", 1.0)))),
    ):
        setattr(engine, attr, value)

    engine.runtime_cohesion_decision_source = str(runtime_cfg["decision_source"]).strip().lower() or "v2"
    movement_surface = getattr(engine, "_movement_surface", None)
    if not isinstance(movement_surface, dict):
        raise TypeError("EngineTickSkeleton._movement_surface missing or invalid")
    movement_surface["alpha_sep"] = max(0.0, float(contact_cfg["alpha_sep"]))
    movement_surface["model"] = movement_model
    movement_surface["v3a_experiment"] = (
        str(movement_cfg.get("experiment_effective", "base")).strip().lower() or "base"
    )
    movement_surface["centroid_probe_scale"] = float(movement_cfg.get("centroid_probe_scale_effective", 1.0))
    movement_surface["odw_posture_bias_enabled"] = bool(odw_posture_bias_cfg.get("enabled_effective", False))
    movement_surface["odw_posture_bias_k"] = max(0.0, float(odw_posture_bias_cfg.get("k_effective", 0.0)))
    movement_surface["odw_posture_bias_clip_delta"] = max(
        0.0,
        float(odw_posture_bias_cfg.get("clip_delta_effective", 0.2)),
    )

    combat_surface = getattr(engine, "_combat_surface", None)
    if not isinstance(combat_surface, dict):
        raise TypeError("EngineTickSkeleton._combat_surface missing or invalid")
    combat_surface["fire_quality_alpha"] = float(contact_cfg["fire_quality_alpha"])
    combat_surface["contact_hysteresis_h"] = float(contact_cfg["contact_hysteresis_h"])
    combat_surface["ch_enabled"] = bool(contact_cfg["ch_enabled"])

    fsr_surface = getattr(engine, "_fsr_surface", None)
    if not isinstance(fsr_surface, dict):
        raise TypeError("EngineTickSkeleton._fsr_surface missing or invalid")
    fsr_surface["enabled"] = bool(contact_cfg["fsr_enabled"]) and not (fixture_active and movement_model == "v4a")
    fsr_surface["strength"] = float(contact_cfg["fsr_strength"])

    boundary_surface = getattr(engine, "_boundary_surface", None)
    if not isinstance(boundary_surface, dict):
        raise TypeError("EngineTickSkeleton._boundary_surface missing or invalid")
    boundary_surface["soft_enabled"] = bool(boundary_cfg["enabled"])
    boundary_surface["hard_enabled"] = bool(boundary_cfg["enabled"]) and bool(boundary_cfg["hard_enabled"])
    boundary_surface["soft_strength"] = max(0.0, float(boundary_cfg["soft_strength"]))

    diagnostics_enabled = bool(observer_enabled) or bool(execution_cfg["plot_diagnostics_enabled"])
    observer_active = bool(diagnostics_enabled) and (
        bool(capture_positions) or bool(observer_cfg.get("runtime_diag_enabled", False))
    )
    diag_surface = getattr(engine, "_diag_surface", None)
    if not isinstance(diag_surface, dict):
        raise TypeError("EngineTickSkeleton._diag_surface missing or invalid")
    diag_surface["fsr_diag_enabled"] = observer_active
    diag_surface["diag4_enabled"] = observer_active

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
    fleet_ids = tuple(state.fleets)

    def _per_fleet_series() -> dict[str, list]:
        return {fleet_id: [] for fleet_id in fleet_ids}

    def _compute_centroid_and_rms_radius(position_map: Mapping[str, tuple[float, float]]) -> tuple[float, float, float]:
        if not position_map:
            return (float("nan"), float("nan"), 0.0)
        xs = [float(position[0]) for position in position_map.values()]
        ys = [float(position[1]) for position in position_map.values()]
        centroid_x = sum(xs) / float(len(xs))
        centroid_y = sum(ys) / float(len(ys))
        radius_sq_mean = sum(
            ((x - centroid_x) * (x - centroid_x)) + ((y - centroid_y) * (y - centroid_y))
            for x, y in zip(xs, ys, strict=False)
        ) / float(len(xs))
        return (centroid_x, centroid_y, math.sqrt(max(0.0, radius_sq_mean)))

    def _build_fixture_expected_reference_bundle(
        position_map: Mapping[str, tuple[float, float]],
        objective_point_xy: tuple[float, float],
    ) -> dict:
        centroid_x, centroid_y, _ = _compute_centroid_and_rms_radius(position_map)
        if not math.isfinite(centroid_x) or not math.isfinite(centroid_y):
            raise ValueError("neutral_transit_v1 expected-position reference requires at least one alive unit")
        primary_dx = float(objective_point_xy[0]) - centroid_x
        primary_dy = float(objective_point_xy[1]) - centroid_y
        primary_norm = math.sqrt((primary_dx * primary_dx) + (primary_dy * primary_dy))
        if primary_norm <= 1e-12:
            raise ValueError(
                "neutral_transit_v1 expected-position reference requires objective_point_xy to differ from the initial fleet centroid"
            )
        primary_axis_xy = (primary_dx / primary_norm, primary_dy / primary_norm)
        secondary_axis_xy = (-primary_axis_xy[1], primary_axis_xy[0])
        expected_slot_offsets_local = {}
        initial_front_extent = 0.0
        for unit_id, position in position_map.items():
            rel_x = float(position[0]) - centroid_x
            rel_y = float(position[1]) - centroid_y
            forward_offset = (rel_x * primary_axis_xy[0]) + (rel_y * primary_axis_xy[1])
            lateral_offset = (rel_x * secondary_axis_xy[0]) + (rel_y * secondary_axis_xy[1])
            expected_slot_offsets_local[str(unit_id)] = (forward_offset, lateral_offset)
            if forward_offset > initial_front_extent:
                initial_front_extent = forward_offset
        return {
            "initial_forward_hat_xy": primary_axis_xy,
            "initial_secondary_hat_xy": secondary_axis_xy,
            "expected_slot_offsets_local": expected_slot_offsets_local,
            "initial_front_extent": float(initial_front_extent),
        }

    def _compute_expected_position_rms_error(
        position_map: Mapping[str, tuple[float, float]],
        expected_position_map: Mapping[str, tuple[float, float]],
    ) -> float:
        if not position_map or not expected_position_map:
            return float("nan")
        error_sq_sum = 0.0
        count = 0
        for unit_id, position in position_map.items():
            expected_position = expected_position_map.get(str(unit_id))
            if not isinstance(expected_position, tuple) or len(expected_position) < 2:
                continue
            dx = float(position[0]) - float(expected_position[0])
            dy = float(position[1]) - float(expected_position[1])
            error_sq_sum += (dx * dx) + (dy * dy)
            count += 1
        if count <= 0:
            return float("nan")
        return math.sqrt(error_sq_sum / float(count))

    def _compute_front_extent_ratio(
        position_map: Mapping[str, tuple[float, float]],
        objective_point_xy: tuple[float, float],
        initial_front_extent: float,
        fallback_axis_xy: tuple[float, float],
    ) -> float:
        if not position_map:
            return float("nan")
        centroid_x, centroid_y, _ = _compute_centroid_and_rms_radius(position_map)
        if not math.isfinite(centroid_x) or not math.isfinite(centroid_y):
            return float("nan")
        axis_dx = float(objective_point_xy[0]) - centroid_x
        axis_dy = float(objective_point_xy[1]) - centroid_y
        axis_norm = math.sqrt((axis_dx * axis_dx) + (axis_dy * axis_dy))
        if axis_norm > 1e-12:
            axis_x = axis_dx / axis_norm
            axis_y = axis_dy / axis_norm
        else:
            axis_x = float(fallback_axis_xy[0])
            axis_y = float(fallback_axis_xy[1])
        front_extent = max(
            (((float(position[0]) - centroid_x) * axis_x) + ((float(position[1]) - centroid_y) * axis_y))
            for position in position_map.values()
        )
        if initial_front_extent <= 1e-12:
            return float("nan")
        return float(front_extent) / float(initial_front_extent)

    trajectory = _per_fleet_series()
    alive_trajectory = _per_fleet_series()
    fleet_size_trajectory = _per_fleet_series()
    observer_telemetry = {
        **{
            key: _per_fleet_series()
            for key in (
                "cohesion_v3",
                "c_conn",
                "c_scale",
                "rho",
                "centroid_x",
                "centroid_y",
                "center_wing_advance_gap",
                "front_curvature_index",
                "center_wing_parallel_share",
                "posture_persistence_time",
            )
        },
        "net_axis_push": {"net": []},
        "net_axis_push_interval_ticks": 10,
        "center_wing_advance_gap_interval_ticks": 10,
        "hostile_overlap_pairs": [],
        "hostile_deep_pairs": [],
        "hostile_deep_intermix_ratio": [],
        "hostile_intermix_severity": [],
        "hostile_intermix_coverage": [],
    }
    if fixture_active:
        initial_positions = {
            str(unit_id): (
                float(initial_state.units[unit_id].position.x),
                float(initial_state.units[unit_id].position.y),
            )
            for unit_id in initial_state.fleets[fixture_fleet_id].unit_ids
            if unit_id in initial_state.units and float(initial_state.units[unit_id].hit_points) > 0.0
        }
        fixture_reference_bundle = _build_fixture_expected_reference_bundle(
            initial_positions,
            fixture_objective_point_xy,
        )
        initial_centroid_x, initial_centroid_y, initial_rms_radius = _compute_centroid_and_rms_radius(initial_positions)
        initial_distance = math.sqrt(
            ((initial_centroid_x - fixture_objective_point_xy[0]) ** 2)
            + ((initial_centroid_y - fixture_objective_point_xy[1]) ** 2)
        ) if math.isfinite(initial_centroid_x) and math.isfinite(initial_centroid_y) else float("nan")
        fixture_candidate_a_active = movement_model == "v4a"
        engine.TEST_RUN_FIXTURE_CFG["expected_position_candidate_active"] = fixture_candidate_a_active
        engine.TEST_RUN_FIXTURE_CFG["initial_forward_hat_xy"] = fixture_reference_bundle["initial_forward_hat_xy"]
        engine.TEST_RUN_FIXTURE_CFG["expected_slot_offsets_local"] = fixture_reference_bundle["expected_slot_offsets_local"]
        engine.TEST_RUN_FIXTURE_CFG["frozen_terminal_frame_active"] = False
        engine.TEST_RUN_FIXTURE_CFG["frozen_terminal_primary_axis_xy"] = None
        engine.TEST_RUN_FIXTURE_CFG["frozen_terminal_secondary_axis_xy"] = None
        engine.TEST_RUN_FIXTURE_CFG["frozen_terminal_latched_tick"] = None
        observer_telemetry["fixture"] = {
            "active_mode": fixture_active_mode,
            "fleet_id": fixture_fleet_id,
            "anchor_point_xyz": [
                float(fixture_objective_contract_3d["anchor_point_xyz"][0]),
                float(fixture_objective_contract_3d["anchor_point_xyz"][1]),
                float(fixture_objective_contract_3d["anchor_point_xyz"][2]),
            ],
            "projected_anchor_point_xy": [fixture_objective_point_xy[0], fixture_objective_point_xy[1]],
            "source_owner": str(fixture_objective_contract_3d["source_owner"]),
            "objective_mode": str(fixture_objective_contract_3d["objective_mode"]),
            "no_enemy_semantics": str(fixture_objective_contract_3d["no_enemy_semantics"]),
            "stop_radius": fixture_stop_radius,
            "initial_centroid_to_objective_distance": float(initial_distance),
            "initial_rms_radius": float(initial_rms_radius),
            "initial_front_extent": float(fixture_reference_bundle["initial_front_extent"]),
            "expected_position_candidate_active": bool(fixture_candidate_a_active),
            "objective_reached_tick": None,
            "frozen_terminal_frame_active": False,
            "frozen_terminal_latched_tick": None,
            "frozen_terminal_primary_axis_xy": None,
            "centroid_to_objective_distance": [],
            "formation_rms_radius": [],
            "formation_rms_radius_ratio": [],
            "expected_position_rms_error": [],
            "front_extent_ratio": [],
            "corrected_unit_ratio": [],
            "projection_pairs_count": [],
            "projection_mean_displacement": [],
            "projection_max_displacement": [],
            "legality_reference_surface_count": [],
            "legality_feasible_surface_count": [],
            "legality_middle_stage_active": [],
            "legality_handoff_ready": [],
            "late_terminal_decomposition_trace": [],
        }
    combat_telemetry = {
        "in_contact_count": [],
        "damage_events_count": [],
    }
    bridge_telemetry = {
        "theta_split": float(bridge_cfg["theta_split"]),
        "theta_env": float(bridge_cfg["theta_env"]),
        "sustain_ticks": int(bridge_cfg["sustain_ticks"]),
        **{
            key: _per_fleet_series()
            for key in (
                "AR",
                "wedge_ratio",
                "split_separation",
                "angle_coverage",
                "split_cond",
                "env_cond",
                "split_sustain_counter",
                "env_sustain_counter",
                "bridge_event_cut",
                "bridge_event_pocket",
            )
        },
        "first_tick_split_sustain": {fleet_id: None for fleet_id in fleet_ids},
        "first_tick_env_sustain": {fleet_id: None for fleet_id in fleet_ids},
    }
    split_counter_state = {fleet_id: 0 for fleet_id in fleet_ids}
    env_counter_state = {fleet_id: 0 for fleet_id in fleet_ids}
    position_frames = []
    center_wing_interval_ticks = int(observer_telemetry.get("center_wing_advance_gap_interval_ticks", 10))
    center_wing_position_history = _per_fleet_series()
    posture_persistence_state = {fleet_id: {"sign": 0, "length": 0} for fleet_id in fleet_ids}

    def _append_empty_shape_metrics(fleet_id: str, series: list[float]) -> None:
        series.append(float("nan"))
        observer_telemetry["front_curvature_index"][fleet_id].append(float("nan"))
        observer_telemetry["center_wing_parallel_share"][fleet_id].append(float("nan"))
        observer_telemetry["posture_persistence_time"][fleet_id].append(0.0)
        posture_persistence_state[fleet_id]["sign"] = 0
        posture_persistence_state[fleet_id]["length"] = 0

    def _capture_position_frame(current_state: BattleState) -> None:
        if not capture_positions or frame_stride <= 0 or current_state.tick % frame_stride != 0:
            return
        frame = {"tick": current_state.tick}
        targets = {}
        for fleet_id, fleet in current_state.fleets.items():
            points = []
            for unit_id in fleet.unit_ids:
                if unit_id in current_state.units:
                    unit = current_state.units[unit_id]
                    points.append(
                        (
                            unit_id,
                            unit.position.x,
                            unit.position.y,
                            unit.orientation_vector.x,
                            unit.orientation_vector.y,
                            unit.velocity.x,
                            unit.velocity.y,
                            unit.hit_points,
                            unit.max_hit_points,
                        )
                        if capture_hit_points
                        else (
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
                        if target_id in current_state.units and current_state.units[target_id].hit_points > 0.0:
                            targets[str(unit_id)] = target_id
            frame[fleet_id] = points
        if include_target_lines:
            frame["targets"] = targets
        frame["runtime_debug"] = extract_runtime_debug_payload(
            getattr(engine, "debug_diag_last_tick", {}) if observer_active else {}
        )
        position_frames.append(frame)

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

        current_unit_position_maps: dict[str, dict[str, tuple[float, float]]] = {}
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
            current_unit_position_maps[fleet_id] = unit_position_map
            center_wing_position_history[fleet_id].append(unit_position_map)
            if centroid_count > 0:
                observer_telemetry["centroid_x"][fleet_id].append(centroid_sum_x / float(centroid_count))
                observer_telemetry["centroid_y"][fleet_id].append(centroid_sum_y / float(centroid_count))
            else:
                observer_telemetry["centroid_x"][fleet_id].append(float("nan"))
                observer_telemetry["centroid_y"][fleet_id].append(float("nan"))

        if fixture_active:
            fixture_metrics = observer_telemetry.get("fixture", {})
            fixture_positions = current_unit_position_maps.get(fixture_fleet_id, {})
            centroid_x, centroid_y, rms_radius = _compute_centroid_and_rms_radius(fixture_positions)
            if math.isfinite(centroid_x) and math.isfinite(centroid_y):
                distance_to_objective = math.sqrt(
                    ((centroid_x - fixture_objective_point_xy[0]) ** 2)
                    + ((centroid_y - fixture_objective_point_xy[1]) ** 2)
                )
            else:
                distance_to_objective = float("nan")
            fixture_runtime_debug = extract_runtime_debug_payload(
                getattr(engine, "debug_diag_last_tick", {}) if observer_active else {}
            )
            fixture_runtime_diag_tick = getattr(engine, "debug_diag_last_tick", {}) if observer_active else {}
            if isinstance(fixture_runtime_diag_tick, dict):
                fixture_decomposition_trace = fixture_runtime_diag_tick.get("fixture_terminal_trace")
                if isinstance(fixture_decomposition_trace, dict):
                    trace_units = fixture_decomposition_trace.get("units")
                    if isinstance(trace_units, dict):
                        fixture_metrics["late_terminal_decomposition_trace"].append(
                            {
                                "tick": int(fixture_runtime_diag_tick.get("tick", state.tick)),
                                "fleet_id": str(fixture_decomposition_trace.get("fleet_id", fixture_fleet_id)),
                                "units": {
                                    str(unit_id): dict(row)
                                    for unit_id, row in trace_units.items()
                                    if isinstance(row, dict)
                                },
                            }
                        )
            expected_position_payload = engine._build_fixture_expected_position_map(
                state=state,
                fleet_id=fixture_fleet_id,
                centroid_x=centroid_x if math.isfinite(centroid_x) else 0.0,
                centroid_y=centroid_y if math.isfinite(centroid_y) else 0.0,
                target_direction=state.last_target_direction.get(fixture_fleet_id, (0.0, 0.0)),
            )
            expected_position_map = (
                expected_position_payload.get("expected_positions", {})
                if isinstance(expected_position_payload, Mapping)
                else {}
            )
            initial_rms_radius = float(fixture_metrics.get("initial_rms_radius", 0.0))
            fixture_metrics["centroid_to_objective_distance"].append(float(distance_to_objective))
            fixture_metrics["formation_rms_radius"].append(float(rms_radius))
            fixture_metrics["formation_rms_radius_ratio"].append(
                (float(rms_radius) / initial_rms_radius)
                if initial_rms_radius > 1e-12
                else 1.0
            )
            fixture_metrics["expected_position_rms_error"].append(
                _compute_expected_position_rms_error(fixture_positions, expected_position_map)
            )
            fixture_metrics["front_extent_ratio"].append(
                _compute_front_extent_ratio(
                    fixture_positions,
                    fixture_objective_point_xy,
                    float(fixture_metrics.get("initial_front_extent", 0.0)),
                    tuple(fixture_reference_bundle["initial_forward_hat_xy"]),
                )
            )
            fixture_metrics["corrected_unit_ratio"].append(
                float(fixture_runtime_debug.get("corrected_unit_ratio", 0.0))
            )
            fixture_metrics["projection_pairs_count"].append(int(fixture_runtime_debug.get("projection_pairs_count", 0)))
            fixture_metrics["projection_mean_displacement"].append(
                float(fixture_runtime_debug.get("projection_mean_displacement", 0.0))
            )
            fixture_metrics["projection_max_displacement"].append(
                float(fixture_runtime_debug.get("projection_max_displacement", 0.0))
            )
            fixture_metrics["legality_reference_surface_count"].append(
                int(fixture_runtime_debug.get("legality_reference_surface_count", 0))
            )
            fixture_metrics["legality_feasible_surface_count"].append(
                int(fixture_runtime_debug.get("legality_feasible_surface_count", 0))
            )
            fixture_metrics["legality_middle_stage_active"].append(
                bool(fixture_runtime_debug.get("legality_middle_stage_active", False))
            )
            fixture_metrics["legality_handoff_ready"].append(
                bool(fixture_runtime_debug.get("legality_handoff_ready", False))
            )
            if (
                fixture_metrics.get("objective_reached_tick") is None
                and math.isfinite(distance_to_objective)
                and distance_to_objective <= fixture_stop_radius
            ):
                fixture_metrics["objective_reached_tick"] = int(state.tick)
                if (
                    fixture_candidate_a_active
                    and not bool(engine.TEST_RUN_FIXTURE_CFG.get("frozen_terminal_frame_active", False))
                    and math.isfinite(centroid_x)
                    and math.isfinite(centroid_y)
                ):
                    fallback_axis = fixture_reference_bundle["initial_forward_hat_xy"]
                    objective_axis_dx = fixture_objective_point_xy[0] - centroid_x
                    objective_axis_dy = fixture_objective_point_xy[1] - centroid_y
                    frozen_primary_axis_xy = engine._normalize_direction_with_fallback(
                        float(objective_axis_dx),
                        float(objective_axis_dy),
                        float(fallback_axis[0]),
                        float(fallback_axis[1]),
                    )
                    frozen_secondary_axis_xy = (
                        -float(frozen_primary_axis_xy[1]),
                        float(frozen_primary_axis_xy[0]),
                    )
                    engine.TEST_RUN_FIXTURE_CFG["frozen_terminal_frame_active"] = True
                    engine.TEST_RUN_FIXTURE_CFG["frozen_terminal_primary_axis_xy"] = (
                        float(frozen_primary_axis_xy[0]),
                        float(frozen_primary_axis_xy[1]),
                    )
                    engine.TEST_RUN_FIXTURE_CFG["frozen_terminal_secondary_axis_xy"] = (
                        float(frozen_secondary_axis_xy[0]),
                        float(frozen_secondary_axis_xy[1]),
                    )
                    engine.TEST_RUN_FIXTURE_CFG["frozen_terminal_latched_tick"] = int(state.tick)
                    fixture_metrics["frozen_terminal_frame_active"] = True
                    fixture_metrics["frozen_terminal_latched_tick"] = int(state.tick)
                    fixture_metrics["frozen_terminal_primary_axis_xy"] = [
                        float(frozen_primary_axis_xy[0]),
                        float(frozen_primary_axis_xy[1]),
                    ]
                elimination_tick = int(state.tick)
                post_elimination_stop_tick = min(999, elimination_tick + post_elimination_extra_ticks)
            _capture_position_frame(state)
            if (
                fixture_metrics.get("objective_reached_tick") is not None
                and post_elimination_stop_tick is not None
                and state.tick >= post_elimination_stop_tick
            ):
                break
            continue

        hostile_intermix_metrics = compute_hostile_intermix_metrics(
            state,
            float(contact_cfg["separation_radius"]),
        )
        for metric_key in (
            "hostile_overlap_pairs",
            "hostile_deep_pairs",
            "hostile_deep_intermix_ratio",
            "hostile_intermix_severity",
            "hostile_intermix_coverage",
        ):
            observer_telemetry[metric_key].append(float(hostile_intermix_metrics.get(metric_key, 0.0)))

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
                _append_empty_shape_metrics(fleet_id, series)
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
                _append_empty_shape_metrics(fleet_id, series)
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
                    if not center_advances or not wing_advances:
                        series.append(float("nan"))
                        interval_parallel_share_gap = float("nan")
                    else:
                        center_mean = sum(center_advances) / float(len(center_advances))
                        wing_mean = sum(wing_advances) / float(len(wing_advances))
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
                front_curvature_norm = float(front_curvature_raw) / max(float(contact_cfg["separation_radius"]), 1e-12)
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

        runtime_v3 = getattr(engine, "debug_last_cohesion_v3", {})
        if not isinstance(runtime_v3, dict):
            runtime_v3 = {}
        runtime_v3_components = getattr(engine, "debug_last_cohesion_v3_components", {})
        if not isinstance(runtime_v3_components, dict):
            runtime_v3_components = {}
        for fleet_id in state.fleets:
            fallback_v2 = float(state.last_fleet_cohesion.get(fleet_id, 1.0))
            cohesion_v3 = float(runtime_v3.get(fleet_id, fallback_v2)) if diagnostics_enabled else float("nan")
            comp = runtime_v3_components.get(fleet_id, {})
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
                    state.tick >= 1 and contact_active_tick and split_value >= float(bridge_cfg["theta_split"])
                )
                env_cond = bool(
                    state.tick >= 1 and contact_active_tick and env_value >= float(bridge_cfg["theta_env"])
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
                split_counter_state[fleet_id] >= int(bridge_cfg["sustain_ticks"])
                and bridge_telemetry["first_tick_split_sustain"].get(fleet_id) is None
            ):
                bridge_telemetry["first_tick_split_sustain"][fleet_id] = int(state.tick)
                cut_event_tick = True
            if (
                env_counter_state[fleet_id] >= int(bridge_cfg["sustain_ticks"])
                and bridge_telemetry["first_tick_env_sustain"].get(fleet_id) is None
            ):
                bridge_telemetry["first_tick_env_sustain"][fleet_id] = int(state.tick)
                pocket_event_tick = True

            for metric_key, metric_value in (
                ("AR", ar_value),
                ("wedge_ratio", wedge_value),
                ("split_separation", split_value),
                ("angle_coverage", env_value),
                ("split_cond", bool(split_cond)),
                ("env_cond", bool(env_cond)),
                ("split_sustain_counter", int(split_counter_state[fleet_id])),
                ("env_sustain_counter", int(env_counter_state[fleet_id])),
                ("bridge_event_cut", bool(cut_event_tick)),
                ("bridge_event_pocket", bool(pocket_event_tick)),
            ):
                bridge_telemetry[metric_key][fleet_id].append(metric_value)

        _capture_position_frame(state)

        any_fleet_eliminated = any(len(fleet.unit_ids) == 0 for fleet in state.fleets.values())
        if steps <= 0:
            if any_fleet_eliminated and elimination_tick is None:
                elimination_tick = state.tick
                post_elimination_stop_tick = min(999, elimination_tick + post_elimination_extra_ticks)
            if post_elimination_stop_tick is not None and state.tick >= post_elimination_stop_tick:
                break
        elif any_fleet_eliminated:
            break

    if fixture_active:
        return (
            state,
            trajectory,
            alive_trajectory,
            fleet_size_trajectory,
            observer_telemetry,
            combat_telemetry,
            bridge_telemetry,
            {},
            position_frames,
        )

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
    front_curvature_normalization_scale = max(float(contact_cfg["separation_radius"]), 1e-12)

    def _normalize_series(values: list[float], scale: float) -> list[float]:
        return [
            (float(raw_value) / scale) if math.isfinite(float(raw_value)) else float("nan")
            for raw_value in values
        ]

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
        if (not axis_initialized) or (not valid_pair) or idx < net_axis_push_interval_ticks:
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
    for fleet_id in fleet_ids:
        observer_telemetry["center_wing_advance_gap"][fleet_id] = _normalize_series(
            observer_telemetry["center_wing_advance_gap"][fleet_id],
            center_wing_normalization_scale,
        )
        observer_telemetry["front_curvature_index"][fleet_id] = _normalize_series(
            observer_telemetry["front_curvature_index"][fleet_id],
            front_curvature_normalization_scale,
        )
    observer_telemetry["center_wing_advance_gap_normalization_scale"] = center_wing_normalization_scale
    observer_telemetry["front_curvature_index_normalization_scale"] = front_curvature_normalization_scale

    collapse_shadow_telemetry = compute_collapse_v2_shadow_telemetry(
        observer_enabled=diagnostics_enabled,
        observer_telemetry=observer_telemetry,
        alive_trajectory=alive_trajectory,
        theta_conn_default=float(collapse_shadow_cfg["theta_conn_default"]),
        theta_coh_default=float(collapse_shadow_cfg["theta_coh_default"]),
        theta_force_default=float(collapse_shadow_cfg["theta_force_default"]),
        theta_attr_default=float(collapse_shadow_cfg["theta_attr_default"]),
        attrition_window=int(collapse_shadow_cfg["attrition_window"]),
        sustain_ticks=int(collapse_shadow_cfg["sustain_ticks"]),
        min_conditions=int(collapse_shadow_cfg["min_conditions"]),
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
