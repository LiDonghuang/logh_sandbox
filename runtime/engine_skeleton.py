from collections.abc import Mapping, Sequence
from dataclasses import replace
import math

from runtime.runtime_v0_1 import BattleState, UnitState, Vec2


NEUTRAL_TRANSIT_FIXTURE_RESTORE_DEADBAND_RATIO = 0.28
V4A_SHAPE_VS_ADVANCE_MIN_SHARE = 0.20
V4A_TRANSITION_IDLE_SPEED_FLOOR = 0.45
V4A_TURN_SPEED_FLOOR = 0.35
V4A_FORWARD_TRANSPORT_BRAKE_STRENGTH_DEFAULT = 0.75
V4A_FORWARD_TRANSPORT_BOOST_STRENGTH_DEFAULT = 0.55
V4A_FORWARD_TRANSPORT_BRAKE_FLOOR = 0.15
V4A_FORWARD_TRANSPORT_MAX_SPEED_SCALE = 1.20
V4A_HOLD_AWAIT_SPEED_SCALE_DEFAULT = 0.35
V4A_REFERENCE_SURFACE_MODE_RIGID_SLOTS = "rigid_slots"
V4A_REFERENCE_SURFACE_MODE_SOFT_MORPHOLOGY_V1 = "soft_morphology_v1"
V4A_SOFT_MORPHOLOGY_RELAXATION_DEFAULT = 0.20
V4A_MORPHOLOGY_AXIS_RELAXATION_DEFAULT = 0.12
V4A_CENTER_WING_DIFFERENTIAL_DEFAULT = 0.0
FIXTURE_MODE_NEUTRAL = "neutral"
HOSTILE_CONTACT_IMPEDANCE_MODE_OFF = "off"
HOSTILE_CONTACT_IMPEDANCE_MODE_HYBRID_V2 = "hybrid_v2"
HOSTILE_CONTACT_IMPEDANCE_MODE_LABELS = {
    HOSTILE_CONTACT_IMPEDANCE_MODE_OFF,
    HOSTILE_CONTACT_IMPEDANCE_MODE_HYBRID_V2,
}
HOSTILE_CONTACT_IMPEDANCE_MODE_DEFAULT = HOSTILE_CONTACT_IMPEDANCE_MODE_OFF
HOSTILE_CONTACT_IMPEDANCE_V2_RADIUS_MULTIPLIER_DEFAULT = 1.50
HOSTILE_CONTACT_IMPEDANCE_V2_REPULSION_MAX_DISP_RATIO_DEFAULT = 0.20
HOSTILE_CONTACT_IMPEDANCE_V2_FORWARD_DAMPING_STRENGTH_DEFAULT = 0.50
V4A_ENGAGEMENT_GEOMETRY_FULL_ENGAGED_FRACTION_DEFAULT = 0.08
V4A_FRONT_REORIENTATION_MAX_WEIGHT_DEFAULT = 0.35
V4A_ENGAGEMENT_GEOMETRY_RELAXATION_DEFAULT = 0.18
V4A_EFFECTIVE_FIRE_AXIS_RELAXATION_DEFAULT = 0.16
V4A_FIRE_AXIS_COHERENCE_RELAXATION_DEFAULT = 0.18
V4A_FRONT_REORIENTATION_RELAXATION_DEFAULT = 0.18
MOVEMENT_LOW_LEVEL_MAX_ACCEL_PER_TICK_DEFAULT = 0.25
MOVEMENT_LOW_LEVEL_MAX_DECEL_PER_TICK_DEFAULT = 0.35
MOVEMENT_LOW_LEVEL_MAX_TURN_DEG_PER_TICK_DEFAULT = 18.0
MOVEMENT_LOW_LEVEL_TURN_SPEED_MIN_SCALE_DEFAULT = 0.35


def _direction_delta_degrees(
    lhs_hat_xy: Sequence[float] | tuple[float, float],
    rhs_hat_xy: Sequence[float] | tuple[float, float],
) -> float:
    if len(lhs_hat_xy) < 2 or len(rhs_hat_xy) < 2:
        return float("nan")
    lhs_dx = float(lhs_hat_xy[0])
    lhs_dy = float(lhs_hat_xy[1])
    rhs_dx = float(rhs_hat_xy[0])
    rhs_dy = float(rhs_hat_xy[1])
    lhs_norm = math.sqrt((lhs_dx * lhs_dx) + (lhs_dy * lhs_dy))
    rhs_norm = math.sqrt((rhs_dx * rhs_dx) + (rhs_dy * rhs_dy))
    if lhs_norm <= 1e-12 or rhs_norm <= 1e-12:
        return float("nan")
    dot_value = max(
        -1.0,
        min(
            1.0,
            ((lhs_dx * rhs_dx) + (lhs_dy * rhs_dy)) / max(lhs_norm * rhs_norm, 1e-12),
        ),
    )
    return math.degrees(math.acos(dot_value))


class _ContactImpedanceSupport:
    """Internal runtime support for hostile-contact impedance bookkeeping."""

    @staticmethod
    def resolve_mode(engine: "EngineTickSkeleton") -> str:
        raw_mode = str(
            getattr(
                engine,
                "HOSTILE_CONTACT_IMPEDANCE_MODE",
                HOSTILE_CONTACT_IMPEDANCE_MODE_DEFAULT,
            )
        ).strip().lower()
        if raw_mode not in HOSTILE_CONTACT_IMPEDANCE_MODE_LABELS:
            allowed_text = ", ".join(sorted(HOSTILE_CONTACT_IMPEDANCE_MODE_LABELS))
            raise ValueError(
                "HOSTILE_CONTACT_IMPEDANCE_MODE must be one of "
                f"{{{allowed_text}}}, got {raw_mode!r}"
            )
        return raw_mode

    @staticmethod
    def _compute_fleet_enemy_axes(
        engine: "EngineTickSkeleton",
        state: BattleState,
    ) -> dict[str, tuple[float, float]]:
        axes: dict[str, tuple[float, float]] = {}
        fleet_centroids: dict[str, tuple[float, float]] = {}
        for fleet_id, fleet in state.fleets.items():
            alive_units = [
                state.units[uid]
                for uid in fleet.unit_ids
                if uid in state.units and float(state.units[uid].hit_points) > 0.0
            ]
            fleet_centroids[fleet_id] = engine._compute_position_centroid(alive_units)
        for fleet_id, (cx, cy) in fleet_centroids.items():
            enemy_centroids = [
                pos for other_fleet_id, pos in fleet_centroids.items() if other_fleet_id != fleet_id
            ]
            if not enemy_centroids:
                axes[fleet_id] = (0.0, 0.0)
                continue
            enemy_cx = sum(pos[0] for pos in enemy_centroids) / float(len(enemy_centroids))
            enemy_cy = sum(pos[1] for pos in enemy_centroids) / float(len(enemy_centroids))
            axis, _ = engine._normalize_direction(enemy_cx - cx, enemy_cy - cy)
            axes[fleet_id] = axis
        return axes

    @staticmethod
    def _compute_unit_hostile_proximity(
        engine: "EngineTickSkeleton",
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
                    nx, ny = EngineTickSkeleton._stable_pair_direction(unit_i.unit_id, unit_j.unit_id)
                    distance = 0.0
                proximity = engine._clamp01(1.0 - (distance / impedance_radius))
                weight = proximity * proximity
                proximity_by_unit[unit_i.unit_id] = engine._clamp01(proximity_by_unit[unit_i.unit_id] + weight)
                proximity_by_unit[unit_j.unit_id] = engine._clamp01(proximity_by_unit[unit_j.unit_id] + weight)
                pair_terms_by_unit[unit_i.unit_id].append((unit_j.unit_id, nx, ny, proximity, weight))
                pair_terms_by_unit[unit_j.unit_id].append((unit_i.unit_id, -nx, -ny, proximity, weight))
        return proximity_by_unit, pair_terms_by_unit

    @staticmethod
    def apply(
        engine: "EngineTickSkeleton",
        pre_state: BattleState,
        moved_state: BattleState,
    ) -> BattleState:
        mode = _ContactImpedanceSupport.resolve_mode(engine)
        if mode == HOSTILE_CONTACT_IMPEDANCE_MODE_OFF:
            engine.debug_last_hostile_contact_impedance = {
                "mode": mode,
                "enabled": False,
                "active": False,
                "pair_count": 0,
                "radius": 0.0,
            }
            return moved_state
        radius_multiplier = max(
            1e-6,
            float(
                getattr(
                    engine,
                    "HOSTILE_CONTACT_IMPEDANCE_V2_RADIUS_MULTIPLIER",
                    HOSTILE_CONTACT_IMPEDANCE_V2_RADIUS_MULTIPLIER_DEFAULT,
                )
            ),
        )
        repulsion_max_disp_ratio = max(
            0.0,
            float(
                getattr(
                    engine,
                    "HOSTILE_CONTACT_IMPEDANCE_V2_REPULSION_MAX_DISP_RATIO",
                    HOSTILE_CONTACT_IMPEDANCE_V2_REPULSION_MAX_DISP_RATIO_DEFAULT,
                )
            ),
        )
        forward_damping_strength = engine._clamp01(
            float(
                getattr(
                    engine,
                    "HOSTILE_CONTACT_IMPEDANCE_V2_FORWARD_DAMPING_STRENGTH",
                    HOSTILE_CONTACT_IMPEDANCE_V2_FORWARD_DAMPING_STRENGTH_DEFAULT,
                )
            )
        )
        impedance_radius = float(engine.separation_radius) * radius_multiplier
        if impedance_radius <= 1e-12:
            engine.debug_last_hostile_contact_impedance = {
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
            engine.debug_last_hostile_contact_impedance = {
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

        fleet_axes = _ContactImpedanceSupport._compute_fleet_enemy_axes(engine, moved_state)
        proximity_by_unit, pair_terms_by_unit = _ContactImpedanceSupport._compute_unit_hostile_proximity(
            engine,
            moved_state,
            impedance_radius,
        )
        updated_units = dict(moved_state.units)
        repulsion_sum = 0.0
        repulsion_max = 0.0
        repulsion_count = 0
        damping_sum = 0.0
        damping_count = 0
        max_repulsion_disp = float(engine.separation_radius) * repulsion_max_disp_ratio
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

            local_proximity = engine._clamp01(proximity_by_unit.get(unit.unit_id, 0.0))
            damping_factor = 1.0
            if mode == HOSTILE_CONTACT_IMPEDANCE_MODE_HYBRID_V2 and forward_disp > 0.0:
                damping_factor = 1.0 - (engine._clamp01(forward_damping_strength * local_proximity))
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

        engine.debug_last_hostile_contact_impedance = {
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


class _MovementDiagSupport:
    """Internal runtime support for observer-facing movement diagnostics."""

    @staticmethod
    def build_diag4_payload(
        engine: "EngineTickSkeleton",
        *,
        state: BattleState,
        updated_units: dict,
        final_positions: dict,
        r_sep: float,
        r_sep_sq: float,
        attack_range_sq: float,
    ) -> dict:
        diag_surface = engine._diag_surface
        top_k_raw = int(diag_surface["diag4_topk"])
        if top_k_raw < 1:
            top_k = 1
        elif top_k_raw > 50:
            top_k = 50
        else:
            top_k = top_k_raw

        module_a_topk = {}
        for fleet_id, fleet in state.fleets.items():
            alive_unit_ids = [
                unit_id
                for unit_id in fleet.unit_ids
                if unit_id in final_positions
            ]
            if not alive_unit_ids:
                module_a_topk[fleet_id] = []
                continue

            cx = sum(final_positions[unit_id][0] for unit_id in alive_unit_ids) / len(alive_unit_ids)
            cy = sum(final_positions[unit_id][1] for unit_id in alive_unit_ids) / len(alive_unit_ids)

            radius_by_unit = {}
            for unit_id in alive_unit_ids:
                ux, uy = final_positions[unit_id]
                dx = ux - cx
                dy = uy - cy
                radius_by_unit[unit_id] = math.sqrt((dx * dx) + (dy * dy))

            ranked_units = sorted(
                alive_unit_ids,
                key=lambda uid: radius_by_unit.get(uid, 0.0),
                reverse=True,
            )
            candidates = []
            for unit_id in ranked_units[:top_k]:
                ux, uy = final_positions[unit_id]
                neighbor_sep = 0
                neighbor_contact = 0
                for ally_id in alive_unit_ids:
                    if ally_id == unit_id:
                        continue
                    vx, vy = final_positions[ally_id]
                    dx = vx - ux
                    dy = vy - uy
                    if (dx * dx) + (dy * dy) <= r_sep_sq:
                        neighbor_sep += 1
                for enemy_id, (ex, ey) in final_positions.items():
                    enemy_unit = updated_units.get(enemy_id)
                    if enemy_unit is None or enemy_unit.fleet_id == fleet_id:
                        continue
                    dx = ex - ux
                    dy = ey - uy
                    if (dx * dx) + (dy * dy) <= attack_range_sq:
                        neighbor_contact += 1
                candidates.append(
                    {
                        "unit_id": unit_id,
                        "radius": radius_by_unit.get(unit_id, 0.0),
                        "neighbor_count_sep": neighbor_sep,
                        "neighbor_count_contact": neighbor_contact,
                        "rolling_in_contact_ratio": 0.0,
                    }
                )
            module_a_topk[fleet_id] = candidates

        return {
            "module_a": {
                "top_k": top_k,
                "neighbor_radius_sep": r_sep,
                "neighbor_radius_contact": engine.attack_range,
                "topk_candidates": module_a_topk,
            },
        }

    @staticmethod
    def build_pending(
        engine: "EngineTickSkeleton",
        *,
        state: BattleState,
        updated_units: dict,
        tentative_positions: dict,
        delta_position: dict,
        projection_pairs_count: int,
        boundary_force_events_count_tick: int,
        r_sep: float,
        r_sep_sq: float,
        attack_range_sq: float,
        final_positions: dict,
        diag4_enabled: bool,
        legality_reference_surface_count: int,
        legality_feasible_surface_count: int,
        legality_middle_stage_active: bool,
        legality_handoff_ready: bool,
    ) -> dict:
        projection_eps = 1e-9
        projection_displacement_sum = 0.0
        projection_displacement_max = 0.0
        projection_displacement_count = 0
        corrected_unit_count = 0
        for unit_id in tentative_positions:
            dx_proj, dy_proj = delta_position[unit_id]
            displacement = math.sqrt((dx_proj * dx_proj) + (dy_proj * dy_proj))
            projection_displacement_sum += displacement
            projection_displacement_count += 1
            if displacement > projection_displacement_max:
                projection_displacement_max = displacement
            if displacement > projection_eps:
                corrected_unit_count += 1
        if projection_displacement_count > 0:
            projection_displacement_mean = projection_displacement_sum / projection_displacement_count
            corrected_unit_ratio = corrected_unit_count / projection_displacement_count
        else:
            projection_displacement_mean = 0.0
            corrected_unit_ratio = 0.0

        pending = {
            "tick": state.tick,
            "projection": {
                "max_projection_displacement": projection_displacement_max,
                "mean_projection_displacement": projection_displacement_mean,
                "corrected_unit_ratio": corrected_unit_ratio,
                "projection_pairs_count": projection_pairs_count,
            },
            "boundary_soft": {
                "boundary_force_events_count_tick": boundary_force_events_count_tick,
            },
            "legality": {
                "reference_surface_count": int(legality_reference_surface_count),
                "feasible_surface_count": int(legality_feasible_surface_count),
                "middle_stage_active": bool(legality_middle_stage_active),
                "handoff_ready": bool(legality_handoff_ready),
            },
        }
        bridge_diag_by_fleet = engine._debug_state.get("v4a_bridge_diag", {})
        if isinstance(bridge_diag_by_fleet, Mapping) and bridge_diag_by_fleet:
            pending["v4a_bridge"] = {
                "fleets": {
                    str(fleet_id): {
                        "transition_advance_share": float(
                            row.get("transition_advance_share", 0.0)
                        ),
                    }
                    for fleet_id, row in bridge_diag_by_fleet.items()
                    if isinstance(row, Mapping)
                }
            }
        local_desire_diag_by_fleet = engine._debug_state.get("local_desire_diag_by_fleet", {})
        if isinstance(local_desire_diag_by_fleet, Mapping) and local_desire_diag_by_fleet:
            local_desire_fleets = {}
            for fleet_id, row in local_desire_diag_by_fleet.items():
                if not isinstance(row, Mapping):
                    continue
                local_desire_row = {
                    "early_embargo_permission": float(
                        row.get("early_embargo_permission", float("nan"))
                    ),
                    "late_reopen_persistence": float(
                        row.get("late_reopen_persistence", float("nan"))
                    ),
                }
                if "desired_longitudinal_travel_scale_min" in row:
                    local_desire_row["desired_longitudinal_travel_scale_min"] = float(
                        row.get("desired_longitudinal_travel_scale_min", float("nan"))
                    )
                if "realized_signed_longitudinal_speed_min" in row:
                    local_desire_row["realized_signed_longitudinal_speed_min"] = float(
                        row.get("realized_signed_longitudinal_speed_min", float("nan"))
                    )
                local_desire_fleets[str(fleet_id)] = local_desire_row
            pending["local_desire"] = {
                "fleets": local_desire_fleets
            }

        if diag4_enabled:
            pending["diag4"] = _MovementDiagSupport.build_diag4_payload(
                engine,
                state=state,
                updated_units=updated_units,
                final_positions=final_positions,
                r_sep=r_sep,
                r_sep_sq=r_sep_sq,
                attack_range_sq=attack_range_sq,
            )
        return pending

    @staticmethod
    def flush_pending(
        engine: "EngineTickSkeleton",
        *,
        diag_enabled: bool,
        state: BattleState,
        updated_units: dict,
        tentative_positions: dict,
        delta_position: dict,
        projection_pairs_count: int,
        boundary_force_events_count_tick: int,
        r_sep: float,
        r_sep_sq: float,
        attack_range_sq: float,
        final_positions: dict,
        diag4_enabled: bool,
        legality_reference_surface_count: int,
        legality_feasible_surface_count: int,
        legality_middle_stage_active: bool,
        legality_handoff_ready: bool,
        fixture_trace_fleet_id: str,
        fixture_trace_units_pending: dict | None,
    ) -> None:
        # Diagnostics flush is passive bookkeeping, not maintained movement math.
        if not diag_enabled:
            engine._debug_state["diag_pending"] = None
            return

        pending_diag = _MovementDiagSupport.build_pending(
            engine,
            state=state,
            updated_units=updated_units,
            tentative_positions=tentative_positions,
            delta_position=delta_position,
            projection_pairs_count=projection_pairs_count,
            boundary_force_events_count_tick=boundary_force_events_count_tick,
            r_sep=r_sep,
            r_sep_sq=r_sep_sq,
            attack_range_sq=attack_range_sq,
            final_positions=final_positions,
            diag4_enabled=diag4_enabled,
            legality_reference_surface_count=legality_reference_surface_count,
            legality_feasible_surface_count=legality_feasible_surface_count,
            legality_middle_stage_active=legality_middle_stage_active,
            legality_handoff_ready=legality_handoff_ready,
        )
        if fixture_trace_units_pending is not None:
            pending_diag["fixture_terminal_trace"] = {
                "fleet_id": str(fixture_trace_fleet_id),
                "units": fixture_trace_units_pending,
            }
        engine._debug_state["diag_pending"] = pending_diag


class EngineTickSkeleton:
    """Maintained runtime canonical owner."""

    # A. Runtime surfaces and debug host.
    def __init__(
        self,
        attack_range: float = 3.0,
        damage_per_tick: float = 1.0,
        separation_radius: float = 1.0,
    ) -> None:
        # Active runtime knobs consumed by the maintained execution path.
        self.attack_range = float(attack_range)
        self.damage_per_tick = float(damage_per_tick)
        self.separation_radius = float(separation_radius)

        self._combat_surface = {
            "ch_enabled": True,
            "contact_hysteresis_h": 0.10,
            "fire_angle_quality_alpha": 0.0,
            "fire_cone_half_angle_deg": 30.0,
        }

        self._boundary_surface = {
            "soft_enabled": True,
            "hard_enabled": False,
            "soft_strength": 1.0,
        }

        # Active movement surface retained after v1 retirement.
        self._movement_surface = {
            "alpha_sep": 0.6,
            "model": "v4a",
            "max_accel_per_tick": MOVEMENT_LOW_LEVEL_MAX_ACCEL_PER_TICK_DEFAULT,
            "max_decel_per_tick": MOVEMENT_LOW_LEVEL_MAX_DECEL_PER_TICK_DEFAULT,
            "max_turn_deg_per_tick": MOVEMENT_LOW_LEVEL_MAX_TURN_DEG_PER_TICK_DEFAULT,
            "turn_speed_min_scale": MOVEMENT_LOW_LEVEL_TURN_SPEED_MIN_SCALE_DEFAULT,
            "signed_longitudinal_backpedal_enabled": False,
            "signed_longitudinal_backpedal_reverse_authority_scale": 0.45,
        }

        # Active debug/reference knobs still used by maintained diagnostics.
        self._diag_surface = {
            "runtime_diag_enabled": False,
            "diag4_enabled": False,
            "diag4_topk": 10,
            "diag4_contact_window": 20,
        }

        # Internal-only state is kept behind a single host instead of top-level sprawl.
        self._debug_state = {
            "diag_pending": None,
            "diag_timeseries": [],
            "v4a_bridge_diag": {},
            "unit_intent_target_by_unit": {},
            "unit_desire_by_unit": {},
            "local_desire_diag_by_fleet": {},
        }

    # B. Visible stage pipeline.
    def step(self, state: BattleState) -> BattleState:
        snapshot = replace(state, tick=state.tick + 1)
        self._debug_state["unit_intent_target_by_unit"] = {}
        self._debug_state["unit_desire_by_unit"] = {}
        self._debug_state["local_desire_diag_by_fleet"] = {}
        next_state = self.evaluate_cohesion(snapshot)
        next_state = self.evaluate_target(next_state)
        next_state = self.evaluate_utility(next_state)
        if bool(getattr(self, "SYMMETRIC_MOVEMENT_SYNC_ENABLED", False)):
            moved_state = EngineTickSkeleton._integrate_movement_symmetric_merge(self, next_state)
        else:
            moved_state = self.integrate_movement(next_state)
        moved_state = _ContactImpedanceSupport.apply(self, next_state, moved_state)
        moved_state = EngineTickSkeleton._apply_fixture_terminal_late_clamp(self, next_state, moved_state)
        selected_target_by_unit = self._compute_unit_intent_target_by_unit(moved_state)
        return self.resolve_combat(moved_state, selected_target_by_unit)

    @staticmethod
    def _clamp01(value: float) -> float:
        return min(1.0, max(0.0, value))

    @staticmethod
    def _smoothstep01(value: float) -> float:
        x = EngineTickSkeleton._clamp01(float(value))
        return x * x * (3.0 - (2.0 * x))

    @staticmethod
    def _quantile_sorted(sorted_values: list[float], q: float) -> float:
        if not sorted_values:
            return 0.0
        if len(sorted_values) == 1:
            return sorted_values[0]
        if q <= 0.0:
            return sorted_values[0]
        if q >= 1.0:
            return sorted_values[-1]
        pos = (len(sorted_values) - 1) * q
        lo = int(math.floor(pos))
        hi = int(math.ceil(pos))
        if lo == hi:
            return sorted_values[lo]
        w = pos - lo
        return (sorted_values[lo] * (1.0 - w)) + (sorted_values[hi] * w)

    @staticmethod
    def _dist_summary(values: list[float]) -> dict:
        if not values:
            return {
                "count": 0,
                "mean": 0.0,
                "min": 0.0,
                "p10": 0.0,
                "p50": 0.0,
                "p90": 0.0,
                "max": 0.0,
            }
        vals = sorted(values)
        return {
            "count": len(vals),
            "mean": sum(vals) / len(vals),
            "min": vals[0],
            "p10": EngineTickSkeleton._quantile_sorted(vals, 0.10),
            "p50": EngineTickSkeleton._quantile_sorted(vals, 0.50),
            "p90": EngineTickSkeleton._quantile_sorted(vals, 0.90),
            "max": vals[-1],
        }

    # Keep the indexing helper narrowly localized to the current 2D runtime so a
    # later 3D migration only has one obvious place to swap the bucket logic.
    @staticmethod
    def _build_spatial_hash(rows: list[tuple], cell_size: float) -> dict[tuple[int, int], list[tuple]]:
        buckets = {}
        if cell_size <= 0.0:
            buckets[(0, 0)] = list(rows)
            return buckets
        inv_cell_size = 1.0 / cell_size
        for row in rows:
            cell_x = math.floor(row[0] * inv_cell_size)
            cell_y = math.floor(row[1] * inv_cell_size)
            cell = (cell_x, cell_y)
            bucket = buckets.get(cell)
            if bucket is None:
                bucket = []
                buckets[cell] = bucket
            bucket.append(row)
        return buckets

    @staticmethod
    def _iter_spatial_hash_neighbors(
        spatial_hash: dict[tuple[int, int], list[tuple]],
        x: float,
        y: float,
        cell_size: float,
    ):
        if cell_size <= 0.0:
            yield from spatial_hash.get((0, 0), ())
            return
        inv_cell_size = 1.0 / cell_size
        cell_x = math.floor(x * inv_cell_size)
        cell_y = math.floor(y * inv_cell_size)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                yield from spatial_hash.get((cell_x + dx, cell_y + dy), ())

    @staticmethod
    def _fleet_local_numeric_index(unit_id: str, default_rank: int) -> int:
        numeric_index = 0
        place = 1
        seen_digit = False
        for ch in reversed(unit_id):
            digit = ord(ch) - ord("0")
            if 0 <= digit <= 9:
                numeric_index += digit * place
                place *= 10
                seen_digit = True
            elif seen_digit:
                break
        if seen_digit:
            return numeric_index
        return default_rank

    def _ensure_debug_dict(self, attr_name: str) -> dict:
        debug_state = getattr(self, "_debug_state", None)
        if not isinstance(debug_state, dict):
            debug_state = {}
            self._debug_state = debug_state
        value = debug_state.get(attr_name)
        if not isinstance(value, dict):
            value = {}
            debug_state[attr_name] = value
        return value

    @staticmethod
    def _collect_alive_fleet_positions(
        state: BattleState,
        fleet_id: str,
    ) -> tuple[list[tuple[float, float]] | None, float, float]:
        fleet = state.fleets.get(fleet_id)
        if fleet is None:
            return None, 0.0, 0.0

        alive_positions = []
        sum_x = 0.0
        sum_y = 0.0
        for unit_id in fleet.unit_ids:
            unit = state.units.get(unit_id)
            if unit is None or unit.hit_points <= 0.0:
                continue
            pos_x = unit.position.x
            pos_y = unit.position.y
            alive_positions.append((pos_x, pos_y))
            sum_x += pos_x
            sum_y += pos_y

        if not alive_positions:
            return [], 0.0, 0.0

        n_alive = len(alive_positions)
        return alive_positions, (sum_x / n_alive), (sum_y / n_alive)

    @staticmethod
    def _normalize_direction_with_fallback(
        dx: float,
        dy: float,
        fallback_x: float,
        fallback_y: float,
    ) -> tuple[float, float]:
        norm = math.sqrt((dx * dx) + (dy * dy))
        if norm > 1e-12:
            return (dx / norm, dy / norm)
        fallback_norm = math.sqrt((fallback_x * fallback_x) + (fallback_y * fallback_y))
        if fallback_norm > 1e-12:
            return (fallback_x / fallback_norm, fallback_y / fallback_norm)
        return (1.0, 0.0)

    @staticmethod
    def _relax_scalar(current_value: float, target_value: float, weight: float) -> float:
        current_f = float(current_value)
        target_f = float(target_value)
        if not math.isfinite(current_f):
            return target_f
        if not math.isfinite(target_f):
            return current_f
        blend = EngineTickSkeleton._clamp01(float(weight))
        return current_f + ((target_f - current_f) * blend)

    @staticmethod
    def _compute_attack_direction_speed_scale(
        cos_theta: float,
        *,
        lateral_scale: float,
        backward_scale: float,
    ) -> float:
        cos_clamped = max(-1.0, min(1.0, float(cos_theta)))
        lateral = max(0.0, min(1.0, float(lateral_scale)))
        backward = max(0.0, min(lateral, float(backward_scale)))
        if cos_clamped >= 0.0:
            return float(lateral + ((1.0 - lateral) * cos_clamped))
        return float(lateral + ((lateral - backward) * cos_clamped))

    @staticmethod
    def _compute_position_centroid(units: Sequence[UnitState]) -> tuple[float, float]:
        if not units:
            return 0.0, 0.0
        inv_n = 1.0 / float(len(units))
        return (
            sum(float(unit.position.x) for unit in units) * inv_n,
            sum(float(unit.position.y) for unit in units) * inv_n,
        )

    @staticmethod
    def _normalize_direction(dx: float, dy: float) -> tuple[tuple[float, float], float]:
        norm = math.sqrt((dx * dx) + (dy * dy))
        if norm > 0.0:
            return (dx / norm, dy / norm), 1.0
        return (0.0, 0.0), 0.0

    @staticmethod
    def _relax_direction(
        current_hat: tuple[float, float],
        desired_hat: tuple[float, float],
        relaxation: float,
    ) -> tuple[float, float]:
        relaxed_x = ((1.0 - relaxation) * float(current_hat[0])) + (relaxation * float(desired_hat[0]))
        relaxed_y = ((1.0 - relaxation) * float(current_hat[1])) + (relaxation * float(desired_hat[1]))
        normalized_hat, normalized_norm = EngineTickSkeleton._normalize_direction(relaxed_x, relaxed_y)
        if normalized_norm <= 0.0:
            return current_hat
        return normalized_hat

    @staticmethod
    def _rotate_direction_toward(
        current_hat: tuple[float, float],
        desired_hat: tuple[float, float],
        max_turn_deg: float,
    ) -> tuple[float, float]:
        current_hat_norm, current_norm = EngineTickSkeleton._normalize_direction(
            float(current_hat[0]),
            float(current_hat[1]),
        )
        desired_hat_norm, desired_norm = EngineTickSkeleton._normalize_direction(
            float(desired_hat[0]),
            float(desired_hat[1]),
        )
        if desired_norm <= 0.0:
            return current_hat_norm if current_norm > 0.0 else (1.0, 0.0)
        if current_norm <= 0.0:
            return desired_hat_norm
        max_turn_rad = math.radians(max(0.0, min(180.0, float(max_turn_deg))))
        if max_turn_rad >= (math.pi - 1e-12):
            return desired_hat_norm
        current_angle = math.atan2(float(current_hat_norm[1]), float(current_hat_norm[0]))
        desired_angle = math.atan2(float(desired_hat_norm[1]), float(desired_hat_norm[0]))
        delta_angle = (desired_angle - current_angle + math.pi) % (2.0 * math.pi) - math.pi
        if abs(delta_angle) <= max_turn_rad:
            return desired_hat_norm
        next_angle = current_angle + (max_turn_rad if delta_angle > 0.0 else -max_turn_rad)
        return (math.cos(next_angle), math.sin(next_angle))

    @staticmethod
    def _compute_front_strip_depth(
        units: Sequence[UnitState],
        primary_hat_xy: tuple[float, float],
        *,
        toward_positive: bool,
        strip_fraction: float = 0.20,
        min_count: int = 4,
        max_count: int = 16,
    ) -> float:
        if not units:
            return 0.0
        primary_dx = float(primary_hat_xy[0])
        primary_dy = float(primary_hat_xy[1])
        primary_norm = math.sqrt((primary_dx * primary_dx) + (primary_dy * primary_dy))
        if primary_norm <= 1e-12:
            axis_hat_xy = (1.0, 0.0)
        else:
            axis_hat_xy = (primary_dx / primary_norm, primary_dy / primary_norm)
        centroid_x, centroid_y = EngineTickSkeleton._compute_position_centroid(units)
        signed_values: list[float] = []
        sign = 1.0 if bool(toward_positive) else -1.0
        for unit in units:
            rel_x = float(unit.position.x) - centroid_x
            rel_y = float(unit.position.y) - centroid_y
            projected = (rel_x * float(axis_hat_xy[0])) + (rel_y * float(axis_hat_xy[1]))
            signed_values.append(sign * float(projected))
        if not signed_values:
            return 0.0
        sorted_values = sorted(signed_values, reverse=True)
        strip_count = max(int(min_count), int(round(len(sorted_values) * float(strip_fraction))))
        strip_count = min(int(max_count), min(int(len(sorted_values)), strip_count))
        strip_slice = sorted_values[: max(1, strip_count)]
        strip_mean = sum(float(value) for value in strip_slice) / float(len(strip_slice))
        return float(max(0.0, strip_mean))

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

    # C. Runtime-side bridge/reference support.
    @staticmethod
    def _resolve_v4a_reference_surface(
        state: BattleState,
        *,
        fleet_id: str,
        bundle: Mapping[str, object],
    ) -> tuple[dict[str, tuple[float, float]], tuple[float, float]]:
        fallback_forward = bundle.get("initial_forward_hat_xy", (1.0, 0.0))
        fallback_forward_x = float(fallback_forward[0]) if len(fallback_forward) >= 1 else 1.0
        fallback_forward_y = float(fallback_forward[1]) if len(fallback_forward) >= 2 else 0.0
        resolved_forward_hat, resolved_norm = EngineTickSkeleton._normalize_direction(
            fallback_forward_x,
            fallback_forward_y,
        )
        if resolved_norm <= 0.0:
            resolved_forward_hat = (1.0, 0.0)

        target_direction = state.last_target_direction.get(fleet_id, resolved_forward_hat)
        target_x = float(target_direction[0]) if len(target_direction) >= 1 else 0.0
        target_y = float(target_direction[1]) if len(target_direction) >= 2 else 0.0
        target_forward_hat, target_norm = EngineTickSkeleton._normalize_direction(target_x, target_y)
        if target_norm > 0.0:
            resolved_forward_hat = target_forward_hat
        secondary_hat = (-resolved_forward_hat[1], resolved_forward_hat[0])

        fleet = state.fleets.get(fleet_id)
        if fleet is None:
            return {}, resolved_forward_hat
        alive_units = [
            state.units[unit_id]
            for unit_id in fleet.unit_ids
            if unit_id in state.units and float(state.units[unit_id].hit_points) > 0.0
        ]
        if not alive_units:
            return {}, resolved_forward_hat

        centroid_x, centroid_y = EngineTickSkeleton._compute_position_centroid(alive_units)
        current_axis = bundle.get("morphology_axis_current_xy", resolved_forward_hat)
        if not isinstance(current_axis, Sequence) or len(current_axis) < 2:
            current_axis = resolved_forward_hat
        current_axis_hat, current_axis_norm = EngineTickSkeleton._normalize_direction(
            float(current_axis[0]) if len(current_axis) >= 1 else float(resolved_forward_hat[0]),
            float(current_axis[1]) if len(current_axis) >= 2 else float(resolved_forward_hat[1]),
        )
        if current_axis_norm <= 0.0:
            current_axis_hat = resolved_forward_hat
        terminal_active = bool(bundle.get("formation_terminal_active", False))
        hold_active = bool(bundle.get("formation_hold_active", False))
        hold_axis = bundle.get("formation_hold_axis_xy", current_axis_hat)
        if not isinstance(hold_axis, Sequence) or len(hold_axis) < 2:
            hold_axis = current_axis_hat
        hold_axis_hat, hold_axis_norm = EngineTickSkeleton._normalize_direction(
            float(hold_axis[0]) if len(hold_axis) >= 1 else float(current_axis_hat[0]),
            float(hold_axis[1]) if len(hold_axis) >= 2 else float(current_axis_hat[1]),
        )
        if hold_axis_norm <= 0.0:
            hold_axis_hat = current_axis_hat
        terminal_axis = bundle.get("formation_terminal_axis_xy", current_axis_hat)
        if not isinstance(terminal_axis, Sequence) or len(terminal_axis) < 2:
            terminal_axis = current_axis_hat
        terminal_axis_hat, terminal_axis_norm = EngineTickSkeleton._normalize_direction(
            float(terminal_axis[0]) if len(terminal_axis) >= 1 else float(current_axis_hat[0]),
            float(terminal_axis[1]) if len(terminal_axis) >= 2 else float(current_axis_hat[1]),
        )
        if terminal_axis_norm <= 0.0:
            terminal_axis_hat = current_axis_hat
        objective_point_xy = bundle.get("objective_point_xy")
        stop_radius = float(bundle.get("stop_radius", 0.0))
        within_stop_radius = False
        if isinstance(objective_point_xy, Sequence) and len(objective_point_xy) >= 2 and stop_radius > 0.0:
            objective_dx = float(objective_point_xy[0]) - float(centroid_x)
            objective_dy = float(objective_point_xy[1]) - float(centroid_y)
            objective_distance = math.sqrt((objective_dx * objective_dx) + (objective_dy * objective_dy))
            within_stop_radius = objective_distance <= stop_radius
        if within_stop_radius:
            terminal_active = True
            hold_active = False
            terminal_axis_hat = current_axis_hat
            terminal_center_x = float(centroid_x)
            terminal_center_y = float(centroid_y)
        desired_axis_hat = current_axis_hat
        if target_norm > 0.0:
            desired_axis_hat = target_forward_hat
        effective_fire_axis = bundle.get("effective_fire_axis_xy", desired_axis_hat)
        if not isinstance(effective_fire_axis, Sequence) or len(effective_fire_axis) < 2:
            effective_fire_axis = desired_axis_hat
        effective_fire_axis_hat, effective_fire_axis_norm = EngineTickSkeleton._normalize_direction(
            float(effective_fire_axis[0]) if len(effective_fire_axis) >= 1 else float(desired_axis_hat[0]),
            float(effective_fire_axis[1]) if len(effective_fire_axis) >= 2 else float(desired_axis_hat[1]),
        )
        if effective_fire_axis_norm <= 0.0:
            effective_fire_axis_hat = desired_axis_hat
        if not hold_active and not terminal_active:
            current_axis_hat = EngineTickSkeleton._relax_direction(
                current_axis_hat,
                desired_axis_hat,
                V4A_MORPHOLOGY_AXIS_RELAXATION_DEFAULT,
            )
        if hold_active:
            current_axis_hat = hold_axis_hat
        elif terminal_active:
            current_axis_hat = terminal_axis_hat
        bundle["morphology_axis_current_xy"] = current_axis_hat
        bundle["front_axis_delta_deg"] = float(
            _direction_delta_degrees(current_axis_hat, effective_fire_axis_hat)
        )
        resolved_forward_hat = current_axis_hat
        secondary_hat = (-resolved_forward_hat[1], resolved_forward_hat[0])
        current_center = bundle.get("morphology_center_current_xy", (centroid_x, centroid_y))
        if not isinstance(current_center, Sequence) or len(current_center) < 2:
            current_center = (centroid_x, centroid_y)
        current_center_x = float(current_center[0]) if len(current_center) >= 1 else float(centroid_x)
        current_center_y = float(current_center[1]) if len(current_center) >= 2 else float(centroid_y)
        hold_center = bundle.get("formation_hold_center_xy", (current_center_x, current_center_y))
        if not isinstance(hold_center, Sequence) or len(hold_center) < 2:
            hold_center = (current_center_x, current_center_y)
        hold_center_x = float(hold_center[0]) if len(hold_center) >= 1 else float(current_center_x)
        hold_center_y = float(hold_center[1]) if len(hold_center) >= 2 else float(current_center_y)
        terminal_center = bundle.get("formation_terminal_center_xy", (current_center_x, current_center_y))
        if not isinstance(terminal_center, Sequence) or len(terminal_center) < 2:
            terminal_center = (current_center_x, current_center_y)
        terminal_center_x = float(terminal_center[0]) if len(terminal_center) >= 1 else float(current_center_x)
        terminal_center_y = float(terminal_center[1]) if len(terminal_center) >= 2 else float(current_center_y)
        if within_stop_radius:
            terminal_center_x = float(centroid_x)
            terminal_center_y = float(centroid_y)
        current_offsets_local: dict[str, tuple[float, float]] = {}
        for unit in alive_units:
            rel_x = float(unit.position.x) - centroid_x
            rel_y = float(unit.position.y) - centroid_y
            forward_offset = (rel_x * resolved_forward_hat[0]) + (rel_y * resolved_forward_hat[1])
            lateral_offset = (rel_x * secondary_hat[0]) + (rel_y * secondary_hat[1])
            current_offsets_local[str(unit.unit_id)] = (float(forward_offset), float(lateral_offset))

        reference_surface_mode = str(
            bundle.get("reference_surface_mode", V4A_REFERENCE_SURFACE_MODE_RIGID_SLOTS)
        ).strip().lower()
        if reference_surface_mode != V4A_REFERENCE_SURFACE_MODE_SOFT_MORPHOLOGY_V1:
            rigid_offsets = bundle.get("expected_slot_offsets_local", {})
            if not isinstance(rigid_offsets, Mapping):
                rigid_offsets = {}
            return (
                {
                    str(unit_id): tuple(rigid_offsets.get(str(unit_id), current_offsets_local[str(unit_id)]))
                    for unit_id in current_offsets_local
                },
                resolved_forward_hat,
            )

        initial_alive_count = max(1, int(bundle.get("initial_alive_count", len(current_offsets_local))))
        alive_ratio = max(0.0, min(1.0, float(len(current_offsets_local)) / float(initial_alive_count)))
        target_scale = math.sqrt(alive_ratio)
        forward_extent_initial = max(1e-9, float(bundle.get("forward_extent_initial", 0.0)))
        lateral_extent_initial = max(1e-9, float(bundle.get("lateral_extent_initial", 0.0)))
        forward_extent_base = max(1e-9, float(bundle.get("forward_extent_base", forward_extent_initial)))
        lateral_extent_base = max(1e-9, float(bundle.get("lateral_extent_base", lateral_extent_initial)))
        forward_extent_target = forward_extent_base * target_scale
        lateral_extent_target = lateral_extent_base * target_scale
        actual_forward_extent = max(
            1e-9,
            max((abs(float(offset_local[0])) for offset_local in current_offsets_local.values()), default=0.0),
        )
        actual_lateral_extent = max(
            1e-9,
            max((abs(float(offset_local[1])) for offset_local in current_offsets_local.values()), default=0.0),
        )
        relaxation = max(
            1e-6,
            min(1.0, float(bundle.get("soft_morphology_relaxation", V4A_SOFT_MORPHOLOGY_RELAXATION_DEFAULT))),
        )
        if hold_active:
            current_center_x = hold_center_x
            current_center_y = hold_center_y
        elif terminal_active:
            current_center_x += (float(terminal_center_x) - float(current_center_x)) * relaxation
            current_center_y += (float(terminal_center_y) - float(current_center_y)) * relaxation
        else:
            current_center_x = float(centroid_x)
            current_center_y = float(centroid_y)
        bundle["morphology_center_current_xy"] = (float(current_center_x), float(current_center_y))
        hold_forward_extent = bundle.get("formation_hold_forward_extent", None)
        hold_lateral_extent = bundle.get("formation_hold_lateral_extent", None)
        hold_center_wing_differential = bundle.get("formation_hold_center_wing_differential", None)
        if hold_active and hold_forward_extent is not None and hold_lateral_extent is not None:
            forward_extent_current = max(1e-9, float(hold_forward_extent))
            lateral_extent_current = max(1e-9, float(hold_lateral_extent))
            forward_extent_target = forward_extent_current
            lateral_extent_target = lateral_extent_current
        else:
            forward_extent_current = float(bundle.get("forward_extent_current", forward_extent_initial))
            lateral_extent_current = float(bundle.get("lateral_extent_current", lateral_extent_initial))
            forward_extent_current += (forward_extent_target - forward_extent_current) * relaxation
            lateral_extent_current += (lateral_extent_target - lateral_extent_current) * relaxation
        center_wing_differential_target = float(
            bundle.get("center_wing_differential_target", V4A_CENTER_WING_DIFFERENTIAL_DEFAULT)
        )
        if hold_active and hold_center_wing_differential is not None:
            center_wing_differential_current = float(hold_center_wing_differential)
            center_wing_differential_target = center_wing_differential_current
        else:
            center_wing_differential_current = float(
                bundle.get("center_wing_differential_current", V4A_CENTER_WING_DIFFERENTIAL_DEFAULT)
            )
            center_wing_differential_current += (
                center_wing_differential_target - center_wing_differential_current
            ) * relaxation
        bundle["forward_extent_target"] = float(forward_extent_target)
        bundle["lateral_extent_target"] = float(lateral_extent_target)
        bundle["forward_extent_current"] = float(forward_extent_current)
        bundle["lateral_extent_current"] = float(lateral_extent_current)
        bundle["center_wing_differential_target"] = float(center_wing_differential_target)
        bundle["center_wing_differential_current"] = float(center_wing_differential_current)
        bundle["actual_forward_extent"] = float(actual_forward_extent)
        bundle["actual_lateral_extent"] = float(actual_lateral_extent)
        forward_shape_error = abs(actual_forward_extent - forward_extent_target) / max(1e-9, forward_extent_base)
        lateral_shape_error = abs(actual_lateral_extent - lateral_extent_target) / max(1e-9, lateral_extent_base)
        shape_error_current = min(1.0, max(0.0, max(forward_shape_error, lateral_shape_error)))
        bundle["shape_error_current"] = float(shape_error_current)
        bundle["stop_within_radius"] = bool(within_stop_radius)
        bundle["formation_terminal_active"] = bool(terminal_active)
        bundle["formation_hold_active"] = bool(hold_active)
        bundle["formation_terminal_latched_tick"] = 0 if terminal_active else None
        bundle["formation_hold_latched_tick"] = None
        bundle["formation_terminal_axis_xy"] = (
            (float(current_axis_hat[0]), float(current_axis_hat[1])) if terminal_active else None
        )
        bundle["formation_terminal_center_xy"] = (
            (float(current_center_x), float(current_center_y)) if terminal_active else None
        )
        bundle["formation_hold_axis_xy"] = (
            (float(hold_axis_hat[0]), float(hold_axis_hat[1])) if hold_active else None
        )
        bundle["formation_hold_center_xy"] = (
            (float(hold_center_x), float(hold_center_y)) if hold_active else None
        )
        bundle["formation_hold_forward_extent"] = (
            float(forward_extent_current) if hold_active else None
        )
        bundle["formation_hold_lateral_extent"] = (
            float(lateral_extent_current) if hold_active else None
        )
        bundle["formation_hold_center_wing_differential"] = (
            float(center_wing_differential_current) if hold_active else None
        )
        current_material_forward_phase_by_unit = bundle.get("current_material_forward_phase_by_unit", {})
        if not isinstance(current_material_forward_phase_by_unit, Mapping):
            current_material_forward_phase_by_unit = {}
        current_material_lateral_phase_by_unit = bundle.get("current_material_lateral_phase_by_unit", {})
        if not isinstance(current_material_lateral_phase_by_unit, Mapping):
            current_material_lateral_phase_by_unit = {}
        target_material_forward_phase_by_unit = bundle.get("target_material_forward_phase_by_unit", {})
        if not isinstance(target_material_forward_phase_by_unit, Mapping):
            target_material_forward_phase_by_unit = {}
        target_material_lateral_phase_by_unit = bundle.get("target_material_lateral_phase_by_unit", {})
        if not isinstance(target_material_lateral_phase_by_unit, Mapping):
            target_material_lateral_phase_by_unit = {}
        if not hold_active:
            updated_forward_phases: dict[str, float] = {}
            updated_lateral_phases: dict[str, float] = {}
            for unit_id in current_offsets_local:
                current_forward_phase = current_material_forward_phase_by_unit.get(str(unit_id), 0.0)
                if not isinstance(current_forward_phase, (int, float)):
                    current_forward_phase = 0.0
                current_lateral_phase = current_material_lateral_phase_by_unit.get(str(unit_id), 0.0)
                if not isinstance(current_lateral_phase, (int, float)):
                    current_lateral_phase = 0.0
                target_forward_phase = target_material_forward_phase_by_unit.get(str(unit_id), current_forward_phase)
                if not isinstance(target_forward_phase, (int, float)):
                    target_forward_phase = current_forward_phase
                target_lateral_phase = target_material_lateral_phase_by_unit.get(str(unit_id), current_lateral_phase)
                if not isinstance(target_lateral_phase, (int, float)):
                    target_lateral_phase = current_lateral_phase
                next_forward_phase = float(current_forward_phase) + (
                    (float(target_forward_phase) - float(current_forward_phase)) * relaxation
                )
                next_lateral_phase = float(current_lateral_phase) + (
                    (float(target_lateral_phase) - float(current_lateral_phase)) * relaxation
                )
                updated_forward_phases[str(unit_id)] = max(-1.0, min(1.0, float(next_forward_phase)))
                updated_lateral_phases[str(unit_id)] = max(-1.0, min(1.0, float(next_lateral_phase)))
            bundle["current_material_forward_phase_by_unit"] = dict(updated_forward_phases)
            bundle["current_material_lateral_phase_by_unit"] = dict(updated_lateral_phases)
            current_material_forward_phase_by_unit = updated_forward_phases
            current_material_lateral_phase_by_unit = updated_lateral_phases
        expected_offsets_local: dict[str, tuple[float, float]] = {}
        center_delta_x = float(current_center_x) - float(centroid_x)
        center_delta_y = float(current_center_y) - float(centroid_y)
        center_delta_forward = (
            (center_delta_x * resolved_forward_hat[0]) + (center_delta_y * resolved_forward_hat[1])
        )
        center_delta_lateral = (
            (center_delta_x * secondary_hat[0]) + (center_delta_y * secondary_hat[1])
        )
        forward_transport_deltas_local: list[float] = []
        phase_forward_deltas_local: list[float] = []
        forward_transport_alignment_count = 0
        forward_transport_alignment_matches = 0
        for unit_id, (forward_offset, lateral_offset) in current_offsets_local.items():
            material_forward = current_material_forward_phase_by_unit.get(str(unit_id))
            if not isinstance(material_forward, (int, float)):
                material_forward = float(forward_offset) / max(1e-9, forward_extent_current)
            material_lateral = current_material_lateral_phase_by_unit.get(str(unit_id))
            if not isinstance(material_lateral, (int, float)):
                material_lateral = float(lateral_offset) / max(1e-9, lateral_extent_current)
            material_forward = max(-1.0, min(1.0, float(material_forward)))
            material_lateral = max(-1.0, min(1.0, float(material_lateral)))
            center_wing_profile = 1.0 - (2.0 * abs(material_lateral))
            target_forward_offset = (
                material_forward * float(forward_extent_current)
                + (center_wing_profile * float(center_wing_differential_current))
            )
            target_lateral_offset = material_lateral * float(lateral_extent_current)
            expected_offsets_local[str(unit_id)] = (
                float(target_forward_offset + center_delta_forward),
                float(target_lateral_offset + center_delta_lateral),
            )
            forward_transport_delta = float(target_forward_offset + center_delta_forward - float(forward_offset))
            phase_forward_delta = float(target_forward_offset - float(forward_offset))
            forward_transport_deltas_local.append(forward_transport_delta)
            phase_forward_deltas_local.append(phase_forward_delta)
            if abs(float(forward_offset)) > 1e-9 and abs(forward_transport_delta) > 1e-9:
                forward_transport_alignment_count += 1
                if float(forward_offset) * float(forward_transport_delta) < 0.0:
                    forward_transport_alignment_matches += 1
        if forward_transport_deltas_local:
            bundle["center_delta_forward"] = float(center_delta_forward)
            bundle["forward_transport_delta_mean"] = (
                sum(forward_transport_deltas_local) / float(len(forward_transport_deltas_local))
            )
            bundle["forward_transport_negative_fraction"] = (
                sum(1 for value in forward_transport_deltas_local if value < -1e-9)
                / float(len(forward_transport_deltas_local))
            )
            bundle["forward_transport_positive_fraction"] = (
                sum(1 for value in forward_transport_deltas_local if value > 1e-9)
                / float(len(forward_transport_deltas_local))
            )
        if phase_forward_deltas_local:
            bundle["phase_forward_delta_mean"] = (
                sum(phase_forward_deltas_local) / float(len(phase_forward_deltas_local))
            )
        if forward_transport_alignment_count > 0:
            bundle["forward_transport_alignment"] = (
                float(forward_transport_alignment_matches) / float(forward_transport_alignment_count)
            )

        return expected_offsets_local, resolved_forward_hat

    # Harness still prepares battle/fixture bundles, but the maintained v4a
    # movement pre-shaping now runs inside the runtime owner before movement.
    def _prepare_v4a_bridge_state(self, state: BattleState) -> BattleState:
        self._debug_state["v4a_bridge_diag"] = {}
        movement_surface = self._movement_surface
        movement_model = str(movement_surface["model"]).strip().lower()
        if movement_model != "v4a" or len(state.fleets) <= 0:
            return state
        if len(state.fleets) > 1 and not bool(getattr(self, "SYMMETRIC_MOVEMENT_SYNC_ENABLED", False)):
            return state

        fixture_cfg = getattr(self, "TEST_RUN_FIXTURE_CFG", None)
        had_fixture_cfg = isinstance(fixture_cfg, dict)
        fixture_active_mode = (
            str(fixture_cfg.get("active_mode", "battle")).strip().lower()
            if had_fixture_cfg
            else "battle"
        )
        fixture_bundle = getattr(self, "TEST_RUN_FIXTURE_REFERENCE_BUNDLE", None)
        battle_bundles_by_fleet = getattr(self, "TEST_RUN_BATTLE_RESTORE_BUNDLES_BY_FLEET", None)
        lead_fleet_id = str(next(iter(state.fleets.keys()), "")).strip()
        bundle = None
        using_fixture_bundle = (
            fixture_active_mode == "neutral"
            and had_fixture_cfg
            and isinstance(fixture_bundle, Mapping)
        )
        if using_fixture_bundle:
            lead_fleet_id = str(fixture_cfg.get("fleet_id", lead_fleet_id)).strip() or lead_fleet_id
            bundle = fixture_bundle
        elif isinstance(battle_bundles_by_fleet, Mapping):
            bundle = battle_bundles_by_fleet.get(lead_fleet_id)
        if not isinstance(bundle, Mapping):
            if isinstance(fixture_cfg, dict):
                fixture_cfg["expected_position_candidate_active"] = False
                fixture_cfg["disable_terminal_step_gate"] = False
            return state
        expected_slot_offsets_local, current_forward_hat_xy = EngineTickSkeleton._resolve_v4a_reference_surface(
            state,
            fleet_id=lead_fleet_id,
            bundle=bundle,
        )
        if not expected_slot_offsets_local:
            if isinstance(fixture_cfg, dict):
                fixture_cfg["expected_position_candidate_active"] = False
                fixture_cfg["disable_terminal_step_gate"] = False
            return state

        movement_state = state
        bridge_diag_by_fleet = self._debug_state["v4a_bridge_diag"]
        terminal_active = bool(bundle.get("formation_terminal_active", False))
        hold_active = bool(bundle.get("formation_hold_active", False))
        engagement_geometry_active_current = self._clamp01(
            float(bundle.get("engagement_geometry_active_current", 0.0))
        )
        unit_intent_target_by_unit = self._debug_state.get("unit_intent_target_by_unit")
        if not isinstance(unit_intent_target_by_unit, Mapping):
            raise RuntimeError(
                "runtime unit_intent_target_by_unit must be a Mapping before v4a bridge state"
            )
        state_heading = state.coarse_body_heading_current.get(
            lead_fleet_id,
            bundle.get("movement_heading_current_xy", current_forward_hat_xy),
        )
        if not isinstance(state_heading, (list, tuple)) or len(state_heading) < 2:
            state_heading = current_forward_hat_xy
        state_heading_hat, state_heading_norm = EngineTickSkeleton._normalize_direction(
            float(state_heading[0]) if len(state_heading) >= 1 else float(current_forward_hat_xy[0]),
            float(state_heading[1]) if len(state_heading) >= 2 else float(current_forward_hat_xy[1]),
        )
        if state_heading_norm <= 0.0:
            state_heading_hat = current_forward_hat_xy
        updated_coarse_body_heading_current = dict(state.coarse_body_heading_current)
        if not hold_active:
            if terminal_active:
                raw_target_direction = (0.0, 0.0)
            else:
                raw_target_direction = state.movement_command_direction.get(
                    lead_fleet_id,
                    state.last_target_direction.get(lead_fleet_id, (0.0, 0.0)),
                )
            raw_target_dx = float(raw_target_direction[0]) if len(raw_target_direction) >= 1 else 0.0
            raw_target_dy = float(raw_target_direction[1]) if len(raw_target_direction) >= 2 else 0.0
            raw_target_hat, raw_target_norm = EngineTickSkeleton._normalize_direction(
                raw_target_dx,
                raw_target_dy,
            )
            raw_target_magnitude = math.sqrt((raw_target_dx * raw_target_dx) + (raw_target_dy * raw_target_dy))
            current_heading_hat = state_heading_hat
            desired_heading_hat = raw_target_hat if raw_target_norm > 0.0 else current_forward_hat_xy
            heading_relaxation = max(1e-6, min(1.0, float(bundle["heading_relaxation"])))
            current_heading_hat = EngineTickSkeleton._relax_direction(
                current_heading_hat,
                desired_heading_hat,
                heading_relaxation,
            )
            updated_coarse_body_heading_current[lead_fleet_id] = current_heading_hat
            bundle["movement_heading_current_xy"] = current_heading_hat
            shape_vs_advance_strength = max(0.0, min(1.0, float(bundle["shape_vs_advance_strength"])))
            shape_error_current = max(
                0.0,
                min(1.0, float(bundle.get("shape_error_current", 0.0))),
            )
            if raw_target_norm > 0.0:
                advance_share = max(
                    V4A_SHAPE_VS_ADVANCE_MIN_SHARE,
                    1.0 - (shape_vs_advance_strength * shape_error_current),
                )
            else:
                advance_share = 0.0
            if float(bundle.get("battle_relation_gap_current", float("nan"))) <= 0.0 and raw_target_magnitude > 0.0:
                advance_share = 1.0
            bundle["transition_advance_share"] = float(advance_share)
            bridge_diag_by_fleet[lead_fleet_id] = {
                "transition_advance_share": float(advance_share),
            }
            updated_movement_command_direction = dict(state.movement_command_direction)
            if float(bundle.get("battle_relation_gap_current", float("nan"))) <= 0.0 and raw_target_magnitude > 0.0:
                updated_movement_command_direction[lead_fleet_id] = (
                    float(raw_target_dx) * advance_share,
                    float(raw_target_dy) * advance_share,
                )
            else:
                updated_movement_command_direction[lead_fleet_id] = (
                    float(current_heading_hat[0]) * raw_target_magnitude * advance_share,
                    float(current_heading_hat[1]) * raw_target_magnitude * advance_share,
                )
            updated_last_engagement_intensity = dict(state.last_engagement_intensity)
            updated_last_engagement_intensity[lead_fleet_id] = (
                float(updated_last_engagement_intensity.get(lead_fleet_id, 0.0)) * advance_share
            )
            movement_state = replace(
                state,
                coarse_body_heading_current=updated_coarse_body_heading_current,
                movement_command_direction=updated_movement_command_direction,
                last_engagement_intensity=updated_last_engagement_intensity,
            )
            movement_state = self._apply_v4a_transition_speed_realization(
                movement_state,
                fleet_id=lead_fleet_id,
                bundle=bundle,
                expected_slot_offsets_local=expected_slot_offsets_local,
                current_forward_hat_xy=current_forward_hat_xy,
                current_heading_hat=current_heading_hat,
                advance_share=advance_share,
                engagement_geometry_active_current=engagement_geometry_active_current,
                unit_intent_target_by_unit=unit_intent_target_by_unit,
            )
        if hold_active:
            updated_coarse_body_heading_current[lead_fleet_id] = state_heading_hat
            bundle["movement_heading_current_xy"] = state_heading_hat
            updated_movement_command_direction = dict(state.movement_command_direction)
            updated_movement_command_direction[lead_fleet_id] = (0.0, 0.0)
            updated_last_engagement_intensity = dict(state.last_engagement_intensity)
            updated_last_engagement_intensity[lead_fleet_id] = 0.0
            movement_state = replace(
                state,
                coarse_body_heading_current=updated_coarse_body_heading_current,
                movement_command_direction=updated_movement_command_direction,
                last_engagement_intensity=updated_last_engagement_intensity,
            )
            movement_state = self._apply_v4a_hold_speed_realization(
                movement_state,
                fleet_id=lead_fleet_id,
                bundle=bundle,
            )

        active_fixture_cfg = fixture_cfg if had_fixture_cfg else {}
        active_fixture_cfg["active_mode"] = (
            str(active_fixture_cfg.get("active_mode", "battle")).strip().lower() or "battle"
        )
        active_fixture_cfg["fleet_id"] = lead_fleet_id
        active_fixture_cfg["expected_position_candidate_active"] = True
        active_fixture_cfg["initial_forward_hat_xy"] = tuple(current_forward_hat_xy)
        active_fixture_cfg["expected_slot_offsets_local"] = dict(expected_slot_offsets_local)
        active_fixture_cfg["formation_terminal_active"] = bool(bundle.get("formation_terminal_active", False))
        active_fixture_cfg["formation_hold_active"] = bool(bundle.get("formation_hold_active", False))
        active_fixture_cfg["disable_terminal_step_gate"] = True
        self.TEST_RUN_FIXTURE_CFG = active_fixture_cfg
        return movement_state

    def _apply_v4a_transition_speed_realization(
        self,
        state: BattleState,
        *,
        fleet_id: str,
        bundle: Mapping[str, object],
        expected_slot_offsets_local: Mapping[str, tuple[float, float]],
        current_forward_hat_xy: tuple[float, float],
        current_heading_hat: tuple[float, float],
        advance_share: float,
        engagement_geometry_active_current: float,
        unit_intent_target_by_unit: Mapping[str, str | None],
    ) -> BattleState:
        alive_units = [
            state.units[unit_id]
            for unit_id in state.fleets[fleet_id].unit_ids
            if unit_id in state.units and float(state.units[unit_id].hit_points) > 0.0
        ]
        if not alive_units:
            return state

        centroid_x, centroid_y = EngineTickSkeleton._compute_position_centroid(alive_units)
        secondary_hat_xy = (-float(current_forward_hat_xy[1]), float(current_forward_hat_xy[0]))
        expected_world_positions = {}
        for unit_id, offset_local in expected_slot_offsets_local.items():
            expected_world_positions[str(unit_id)] = (
                float(centroid_x)
                + (float(offset_local[0]) * float(current_forward_hat_xy[0]))
                + (float(offset_local[1]) * float(secondary_hat_xy[0])),
                float(centroid_y)
                + (float(offset_local[0]) * float(current_forward_hat_xy[1]))
                + (float(offset_local[1]) * float(secondary_hat_xy[1])),
            )
        expected_reference_spacing = max(1e-9, float(bundle["expected_reference_spacing"]))
        engaged_speed_scale = max(1e-6, min(1.0, float(bundle["engaged_speed_scale"])))
        attack_speed_lateral_scale = max(
            1e-6,
            min(1.0, float(bundle["attack_speed_lateral_scale"])),
        )
        attack_speed_backward_scale = max(
            0.0,
            min(attack_speed_lateral_scale, float(bundle["attack_speed_backward_scale"])),
        )
        battle_hold_weight_current = self._clamp01(
            float(bundle.get("battle_hold_weight_current", 0.0))
        )
        near_contact_stability = self._clamp01(
            battle_hold_weight_current
            * max(
                0.0,
                min(
                    1.0,
                    float(bundle["battle_near_contact_internal_stability_blend"]),
                ),
            )
        )
        battle_near_contact_speed_relaxation = max(
            1e-6,
            min(1.0, float(bundle["battle_near_contact_speed_relaxation"])),
        )
        transition_reference_max_speed_by_unit = bundle.get("transition_reference_max_speed_by_unit", {})
        if not isinstance(transition_reference_max_speed_by_unit, Mapping):
            transition_reference_max_speed_by_unit = {
                str(unit_id): float(state.units[unit_id].max_speed)
                for unit_id in state.fleets[fleet_id].unit_ids
                if unit_id in state.units
            }
            bundle["transition_reference_max_speed_by_unit"] = dict(transition_reference_max_speed_by_unit)
        updated_units = dict(state.units)
        changed = False
        for unit_id, reference_speed in transition_reference_max_speed_by_unit.items():
            unit = updated_units.get(str(unit_id))
            if unit is None:
                continue
            expected_position = expected_world_positions.get(str(unit_id))
            forward_transport_delta = 0.0
            if expected_position is None:
                shape_need = 0.0
            else:
                dx = float(expected_position[0]) - float(unit.position.x)
                dy = float(expected_position[1]) - float(unit.position.y)
                shape_distance = math.sqrt((dx * dx) + (dy * dy))
                shape_need = max(0.0, min(1.0, shape_distance / expected_reference_spacing))
                forward_transport_delta = (
                    (dx * float(current_forward_hat_xy[0]))
                    + (dy * float(current_forward_hat_xy[1]))
                )
            unit_heading_hat, unit_heading_norm = EngineTickSkeleton._normalize_direction(
                float(unit.orientation_vector.x),
                float(unit.orientation_vector.y),
            )
            if unit_heading_norm <= 0.0:
                unit_heading_hat = current_heading_hat
            heading_alignment = max(
                0.0,
                (float(unit_heading_hat[0]) * float(current_heading_hat[0]))
                + (float(unit_heading_hat[1]) * float(current_heading_hat[1])),
            )
            turn_speed_scale = V4A_TURN_SPEED_FLOOR + (
                (1.0 - V4A_TURN_SPEED_FLOOR) * heading_alignment
            )
            shape_speed_scale = max(
                V4A_TRANSITION_IDLE_SPEED_FLOOR,
                max(advance_share, shape_need),
            )
            forward_transport_need = max(
                0.0,
                min(1.0, abs(float(forward_transport_delta)) / expected_reference_spacing),
            )
            forward_transport_speed_scale = 1.0
            if forward_transport_delta < 0.0:
                forward_transport_speed_scale = max(
                    V4A_FORWARD_TRANSPORT_BRAKE_FLOOR,
                    1.0 - (
                        V4A_FORWARD_TRANSPORT_BRAKE_STRENGTH_DEFAULT
                        * forward_transport_need
                    ),
                )
            elif forward_transport_delta > 0.0:
                forward_transport_speed_scale = min(
                    V4A_FORWARD_TRANSPORT_MAX_SPEED_SCALE,
                    1.0 + (
                        V4A_FORWARD_TRANSPORT_BOOST_STRENGTH_DEFAULT
                        * forward_transport_need
                    ),
                )
            if near_contact_stability > 0.0:
                forward_transport_speed_scale = self._relax_scalar(
                    float(forward_transport_speed_scale),
                    1.0,
                    near_contact_stability,
                )
                shape_speed_scale = self._relax_scalar(
                    float(shape_speed_scale),
                    max(V4A_TRANSITION_IDLE_SPEED_FLOOR, advance_share),
                    near_contact_stability,
                )
            attack_speed_scale = 1.0
            unit_key = str(unit_id)
            if unit_key not in unit_intent_target_by_unit:
                raise KeyError(
                    f"runtime unit_intent_target_by_unit missing key for unit {unit_key!r} "
                    "in v4a transition speed realization"
                )
            raw_selected_target_id = unit_intent_target_by_unit[unit_key]
            selected_target_id = (
                str(raw_selected_target_id).strip()
                if raw_selected_target_id is not None
                else ""
            )
            if selected_target_id:
                target_unit = state.units.get(selected_target_id)
                if target_unit is not None and float(target_unit.hit_points) > 0.0:
                    attack_hat_xy, attack_norm = EngineTickSkeleton._normalize_direction(
                        float(target_unit.position.x) - float(unit.position.x),
                        float(target_unit.position.y) - float(unit.position.y),
                    )
                    if attack_norm > 0.0:
                        attack_cos_theta = (
                            (float(unit_heading_hat[0]) * float(attack_hat_xy[0]))
                            + (float(unit_heading_hat[1]) * float(attack_hat_xy[1]))
                        )
                        attack_direction_scale = self._compute_attack_direction_speed_scale(
                            attack_cos_theta,
                            lateral_scale=attack_speed_lateral_scale,
                            backward_scale=attack_speed_backward_scale,
                        )
                        attack_speed_scale = float(engaged_speed_scale) * float(attack_direction_scale)
            if engagement_geometry_active_current > 0.0:
                fleet_contact_speed_scale = self._relax_scalar(
                    1.0,
                    float(engaged_speed_scale),
                    engagement_geometry_active_current,
                )
                attack_speed_scale = self._relax_scalar(
                    attack_speed_scale,
                    fleet_contact_speed_scale,
                    engagement_geometry_active_current,
                )
            transition_speed_target = (
                float(reference_speed)
                * shape_speed_scale
                * float(forward_transport_speed_scale)
                * turn_speed_scale
                * float(attack_speed_scale)
            )
            transition_speed = self._relax_scalar(
                float(unit.max_speed),
                float(transition_speed_target),
                battle_near_contact_speed_relaxation,
            )
            if abs(float(unit.max_speed) - transition_speed) <= 1e-9:
                continue
            updated_units[str(unit_id)] = replace(unit, max_speed=float(transition_speed))
            changed = True
        if changed:
            return replace(state, units=updated_units)
        return state

    def _apply_v4a_hold_speed_realization(
        self,
        state: BattleState,
        *,
        fleet_id: str,
        bundle: Mapping[str, object],
    ) -> BattleState:
        hold_reference_max_speed_by_unit = bundle.get("formation_hold_reference_max_speed_by_unit", {})
        if not isinstance(hold_reference_max_speed_by_unit, Mapping):
            hold_reference_max_speed_by_unit = {
                str(unit_id): float(state.units[unit_id].max_speed)
                for unit_id in state.fleets[fleet_id].unit_ids
                if unit_id in state.units
            }
            bundle["formation_hold_reference_max_speed_by_unit"] = dict(hold_reference_max_speed_by_unit)
        updated_units = dict(state.units)
        changed = False
        for unit_id, reference_speed in hold_reference_max_speed_by_unit.items():
            unit = updated_units.get(str(unit_id))
            if unit is None:
                continue
            held_speed = float(reference_speed) * V4A_HOLD_AWAIT_SPEED_SCALE_DEFAULT
            if abs(float(unit.max_speed) - held_speed) <= 1e-9:
                continue
            updated_units[str(unit_id)] = replace(unit, max_speed=float(held_speed))
            changed = True
        if changed:
            return replace(state, units=updated_units)
        return state

    def _compute_unit_desire_by_unit(
        self,
        state: BattleState,
        *,
        movement_direction_by_fleet: Mapping[str, tuple[float, float]],
        movement_bundle_by_fleet: Mapping[str, Mapping[str, object] | None],
        unit_intent_target_by_unit: Mapping[str, str | None],
    ) -> dict[str, dict[str, object]]:
        unit_desire_by_unit: dict[str, dict[str, object]] = {}
        local_desire_diag_by_fleet = self._debug_state.get("local_desire_diag_by_fleet", {})
        if not isinstance(local_desire_diag_by_fleet, dict):
            local_desire_diag_by_fleet = {}
            self._debug_state["local_desire_diag_by_fleet"] = local_desire_diag_by_fleet
        # Current bounded experimental family remains within the same owner/path
        # and carrier, but this slice now reads as a behavior-line
        # `back_off_keep_front` response: first keep early local opportunity from
        # breaking fleet hold, then let fleet-authorized give-ground suppress
        # continued over-commit and reopen some space.
        movement_surface = self._movement_surface
        experimental_signal_read_realignment_enabled = movement_surface[
            "local_desire_experimental_signal_read_realignment_enabled"
        ]
        if not isinstance(experimental_signal_read_realignment_enabled, bool):
            raise ValueError(
                "runtime local_desire_experimental_signal_read_realignment_enabled "
                "must be a boolean"
            )
        signed_longitudinal_backpedal_enabled = movement_surface[
            "signed_longitudinal_backpedal_enabled"
        ]
        local_desire_turn_need_onset = float(movement_surface["local_desire_turn_need_onset"])
        if (
            not math.isfinite(local_desire_turn_need_onset)
            or not 0.0 <= local_desire_turn_need_onset <= 0.95
        ):
            raise ValueError(
                "runtime local_desire_turn_need_onset must be finite and within [0.0, 0.95], "
                f"got {local_desire_turn_need_onset}"
            )
        local_desire_heading_bias_cap = float(movement_surface["local_desire_heading_bias_cap"])
        if (
            not math.isfinite(local_desire_heading_bias_cap)
            or not 0.0 <= local_desire_heading_bias_cap <= 0.15
        ):
            raise ValueError(
                "runtime local_desire_heading_bias_cap must be finite and within [0.0, 0.15], "
                f"got {local_desire_heading_bias_cap}"
            )
        local_desire_speed_brake_strength = float(movement_surface["local_desire_speed_brake_strength"])
        if (
            not math.isfinite(local_desire_speed_brake_strength)
            or not 0.0 <= local_desire_speed_brake_strength <= 0.10
        ):
            raise ValueError(
                "runtime local_desire_speed_brake_strength must be finite and within [0.0, 0.10], "
                f"got {local_desire_speed_brake_strength}"
            )
        LOCAL_DESIRE_MANEUVER_CONTEXT_GATE_START_RATIO = 0.75
        LOCAL_DESIRE_MANEUVER_CONTEXT_GATE_FULL_RATIO = 0.35
        LOCAL_DESIRE_NEAR_CONTACT_GATE_START_RATIO = 0.35
        LOCAL_DESIRE_NEAR_CONTACT_GATE_FULL_RATIO = 0.20
        LOCAL_DESIRE_EARLY_EMBARGO_FULL_CLOSE_RELATION_GAP = 0.05
        LOCAL_DESIRE_EARLY_EMBARGO_FULL_OPEN_RELATION_GAP = 0.22
        LOCAL_DESIRE_SPEED_BRAKE_FLOOR = 0.97
        LOCAL_DESIRE_BACKOFF_SPEED_BRAKE_FLOOR = 0.76
        LOCAL_DESIRE_BACKOFF_SPEED_RESTRAINT_STRENGTH_MULTIPLIER = 8.0
        LOCAL_DESIRE_BACKOFF_OVERCOMMIT_SUPPRESSION_COHERENCE_WEIGHT = 0.35
        LOCAL_DESIRE_BACKOFF_OVERCOMMIT_SUPPRESSION_SEVERITY_WEIGHT = 0.85
        LOCAL_DESIRE_VIOLATION_RESPONSE_FULL_CLOSE_RELATION_GAP = 0.0
        LOCAL_DESIRE_VIOLATION_RESPONSE_FULL_OPEN_RELATION_GAP = -0.18
        LOCAL_DESIRE_LATE_REOPEN_PERSISTENCE_FULL_RELATION_GAP = 0.08
        LOCAL_DESIRE_LATE_REOPEN_PERSISTENCE_CLEAR_RELATION_GAP = 0.26
        LOCAL_DESIRE_LATE_REOPEN_SPEED_RESTRAINT_STRENGTH = 0.12
        LOCAL_DESIRE_LATE_REOPEN_HEADING_SUPPRESSION_WEIGHT = 0.55
        LOCAL_DESIRE_LATE_REOPEN_EARLY_PERMISSION_ONSET = 0.65
        LOCAL_DESIRE_LATE_REOPEN_CONTACT_GATE_START_RATIO = 1.00
        LOCAL_DESIRE_LATE_REOPEN_CONTACT_GATE_FULL_RATIO = 0.75
        for fleet_id, fleet in state.fleets.items():
            movement_direction = movement_direction_by_fleet.get(
                str(fleet_id),
                state.last_target_direction.get(str(fleet_id), (0.0, 0.0)),
            )
            base_heading_x = float(movement_direction[0]) if len(movement_direction) >= 1 else 0.0
            base_heading_y = float(movement_direction[1]) if len(movement_direction) >= 2 else 0.0
            base_heading_hat, base_heading_magnitude = EngineTickSkeleton._normalize_direction(
                float(base_heading_x),
                float(base_heading_y),
            )
            fleet_front = state.coarse_body_heading_current.get(str(fleet_id), movement_direction)
            if not isinstance(fleet_front, Sequence) or len(fleet_front) < 2:
                fleet_front = movement_direction
            fleet_front_hat, fleet_front_norm = EngineTickSkeleton._normalize_direction(
                float(fleet_front[0]) if len(fleet_front) >= 1 else float(base_heading_x),
                float(fleet_front[1]) if len(fleet_front) >= 2 else float(base_heading_y),
            )
            if fleet_front_norm <= 0.0:
                if base_heading_magnitude > 0.0:
                    fleet_front_hat = base_heading_hat
                else:
                    fleet_front_hat = (1.0, 0.0)
            fleet_bundle = movement_bundle_by_fleet.get(str(fleet_id))
            experimental_back_off_behavior_active = (
                experimental_signal_read_realignment_enabled
                and isinstance(fleet_bundle, Mapping)
            )
            if experimental_back_off_behavior_active:
                battle_relation_gap_raw = float(fleet_bundle["battle_relation_gap_raw"])
                battle_relation_gap_current = float(fleet_bundle["battle_relation_gap_current"])
                battle_hold_weight_current = self._clamp01(
                    float(fleet_bundle["battle_hold_weight_current"])
                )
                battle_brake_drive_current = self._clamp01(
                    float(fleet_bundle["battle_brake_drive_current"])
                )
                if not math.isfinite(battle_relation_gap_raw):
                    raise ValueError(
                        "runtime experimental local_desire branch requires finite "
                        f"battle_relation_gap_raw for fleet {fleet_id!r}, got {battle_relation_gap_raw}"
                    )
                if not math.isfinite(battle_relation_gap_current):
                    raise ValueError(
                        "runtime experimental local_desire branch requires finite "
                        f"battle_relation_gap_current for fleet {fleet_id!r}, got {battle_relation_gap_current}"
                    )
                if (
                    battle_relation_gap_raw
                    >= float(LOCAL_DESIRE_EARLY_EMBARGO_FULL_OPEN_RELATION_GAP)
                ):
                    early_embargo_permission_fleet = 1.0
                elif (
                    battle_relation_gap_raw
                    <= float(LOCAL_DESIRE_EARLY_EMBARGO_FULL_CLOSE_RELATION_GAP)
                ):
                    early_embargo_permission_fleet = 0.0
                else:
                    early_embargo_permission_fleet = self._smoothstep01(
                        (
                            float(battle_relation_gap_raw)
                            - float(LOCAL_DESIRE_EARLY_EMBARGO_FULL_CLOSE_RELATION_GAP)
                        )
                        / max(
                            float(LOCAL_DESIRE_EARLY_EMBARGO_FULL_OPEN_RELATION_GAP)
                            - float(LOCAL_DESIRE_EARLY_EMBARGO_FULL_CLOSE_RELATION_GAP),
                            1e-9,
                        )
                    )
                early_embargo_severity_fleet = self._clamp01(
                    1.0 - float(early_embargo_permission_fleet)
                )
                if (
                    battle_relation_gap_current
                    >= float(LOCAL_DESIRE_VIOLATION_RESPONSE_FULL_CLOSE_RELATION_GAP)
                ):
                    relation_violation_severity_fleet = 0.0
                elif (
                    battle_relation_gap_current
                    <= float(LOCAL_DESIRE_VIOLATION_RESPONSE_FULL_OPEN_RELATION_GAP)
                ):
                    relation_violation_severity_fleet = 1.0
                else:
                    relation_violation_severity_fleet = self._smoothstep01(
                        (
                            float(LOCAL_DESIRE_VIOLATION_RESPONSE_FULL_CLOSE_RELATION_GAP)
                            - float(battle_relation_gap_current)
                        )
                        / max(
                            float(LOCAL_DESIRE_VIOLATION_RESPONSE_FULL_CLOSE_RELATION_GAP)
                            - float(LOCAL_DESIRE_VIOLATION_RESPONSE_FULL_OPEN_RELATION_GAP),
                            1e-9,
                        )
                    )
                if battle_relation_gap_current <= 0.0:
                    late_reopen_persistence_fleet = 0.0
                elif (
                    battle_relation_gap_current
                    >= float(LOCAL_DESIRE_LATE_REOPEN_PERSISTENCE_CLEAR_RELATION_GAP)
                ):
                    late_reopen_persistence_fleet = 0.0
                elif (
                    battle_relation_gap_current
                    <= float(LOCAL_DESIRE_LATE_REOPEN_PERSISTENCE_FULL_RELATION_GAP)
                ):
                    late_reopen_persistence_fleet = 1.0
                else:
                    late_reopen_persistence_fleet = self._smoothstep01(
                        (
                            float(LOCAL_DESIRE_LATE_REOPEN_PERSISTENCE_CLEAR_RELATION_GAP)
                            - float(battle_relation_gap_current)
                        )
                        / max(
                            float(LOCAL_DESIRE_LATE_REOPEN_PERSISTENCE_CLEAR_RELATION_GAP)
                            - float(LOCAL_DESIRE_LATE_REOPEN_PERSISTENCE_FULL_RELATION_GAP),
                            1e-9,
                        )
                    )
            else:
                battle_relation_gap_raw = 0.0
                battle_relation_gap_current = 0.0
                battle_hold_weight_current = 0.0
                battle_brake_drive_current = 0.0
                early_embargo_permission_fleet = float("nan")
                early_embargo_severity_fleet = float("nan")
                relation_violation_severity_fleet = float("nan")
                late_reopen_persistence_fleet = float("nan")
            for unit_id in fleet.unit_ids:
                unit = state.units.get(unit_id)
                if unit is None or float(unit.hit_points) <= 0.0:
                    continue
                desired_heading_x = float(base_heading_x)
                desired_heading_y = float(base_heading_y)
                desired_heading_hat = base_heading_hat if base_heading_magnitude > 0.0 else fleet_front_hat
                if signed_longitudinal_backpedal_enabled and base_heading_magnitude <= 0.0:
                    desired_heading_x = float(desired_heading_hat[0])
                    desired_heading_y = float(desired_heading_hat[1])
                desired_speed_scale = 1.0
                desired_longitudinal_travel_scale = 1.0
                unit_key = str(unit_id)
                if unit_key not in unit_intent_target_by_unit:
                    raise KeyError(
                        f"runtime unit_intent_target_by_unit missing key for unit {unit_key!r} "
                        "in local desire generation"
                    )
                raw_selected_target_id = unit_intent_target_by_unit[unit_key]
                selected_target_id = (
                    str(raw_selected_target_id).strip()
                    if raw_selected_target_id is not None
                    else ""
                )
                if selected_target_id:
                    target_unit = state.units.get(selected_target_id)
                    if (
                        target_unit is not None
                        and float(target_unit.hit_points) > 0.0
                        and str(target_unit.fleet_id) != str(unit.fleet_id)
                    ):
                        attack_hat_xy, attack_distance = EngineTickSkeleton._normalize_direction(
                            float(target_unit.position.x) - float(unit.position.x),
                            float(target_unit.position.y) - float(unit.position.y),
                        )
                        if attack_distance > 0.0 and float(self.attack_range) > 1e-12:
                            maneuver_context_start = (
                                float(self.attack_range)
                                * float(LOCAL_DESIRE_MANEUVER_CONTEXT_GATE_START_RATIO)
                            )
                            maneuver_context_full = (
                                float(self.attack_range)
                                * float(LOCAL_DESIRE_MANEUVER_CONTEXT_GATE_FULL_RATIO)
                            )
                            if attack_distance >= maneuver_context_start:
                                maneuver_context_gate = 0.0
                            elif attack_distance <= maneuver_context_full:
                                maneuver_context_gate = 1.0
                            else:
                                maneuver_context_gate = self._clamp01(
                                    (float(maneuver_context_start) - float(attack_distance))
                                    / max(
                                        float(maneuver_context_start) - float(maneuver_context_full),
                                        1e-9,
                                    )
                                )
                            near_contact_start = (
                                float(self.attack_range)
                                * float(LOCAL_DESIRE_NEAR_CONTACT_GATE_START_RATIO)
                            )
                            near_contact_full = (
                                float(self.attack_range)
                                * float(LOCAL_DESIRE_NEAR_CONTACT_GATE_FULL_RATIO)
                            )
                            if attack_distance >= near_contact_start:
                                near_contact_gate = 0.0
                            elif attack_distance <= near_contact_full:
                                near_contact_gate = 1.0
                            else:
                                near_contact_gate = self._clamp01(
                                    (float(near_contact_start) - float(attack_distance))
                                    / max(
                                        float(near_contact_start) - float(near_contact_full),
                                        1e-9,
                                    )
                                )
                            late_reopen_contact_start = (
                                float(self.attack_range)
                                * float(LOCAL_DESIRE_LATE_REOPEN_CONTACT_GATE_START_RATIO)
                            )
                            late_reopen_contact_full = (
                                float(self.attack_range)
                                * float(LOCAL_DESIRE_LATE_REOPEN_CONTACT_GATE_FULL_RATIO)
                            )
                            if attack_distance >= late_reopen_contact_start:
                                late_reopen_contact_gate = 0.0
                            elif attack_distance <= late_reopen_contact_full:
                                late_reopen_contact_gate = 1.0
                            else:
                                late_reopen_contact_gate = self._smoothstep01(
                                    (
                                        float(late_reopen_contact_start)
                                        - float(attack_distance)
                                    )
                                    / max(
                                        float(late_reopen_contact_start)
                                        - float(late_reopen_contact_full),
                                        1e-9,
                                    )
                                )
                            unit_facing_hat, unit_facing_norm = EngineTickSkeleton._normalize_direction(
                                float(unit.orientation_vector.x),
                                float(unit.orientation_vector.y),
                            )
                            if unit_facing_norm <= 0.0:
                                unit_facing_hat = desired_heading_hat
                            fleet_front_lateralness = abs(
                                (float(fleet_front_hat[0]) * float(attack_hat_xy[1]))
                                - (float(fleet_front_hat[1]) * float(attack_hat_xy[0]))
                            )
                            front_bearing_need = self._clamp01(float(fleet_front_lateralness))
                            fleet_front_target_forwardness = self._clamp01(
                                (float(fleet_front_hat[0]) * float(attack_hat_xy[0]))
                                + (float(fleet_front_hat[1]) * float(attack_hat_xy[1]))
                            )
                            unit_facing_alignment = max(
                                -1.0,
                                min(
                                    1.0,
                                    (float(unit_facing_hat[0]) * float(attack_hat_xy[0]))
                                    + (float(unit_facing_hat[1]) * float(attack_hat_xy[1])),
                                ),
                            )
                            turn_need_raw = self._clamp01(
                                (1.0 - float(unit_facing_alignment)) * 0.50
                            )
                            heading_turn_need = self._smoothstep01(
                                (
                                    float(turn_need_raw)
                                    - float(local_desire_turn_need_onset)
                                )
                                / max(
                                    1.0 - float(local_desire_turn_need_onset),
                                    1e-9,
                                )
                            )
                            speed_turn_need = self._clamp01(
                                float(heading_turn_need) * float(heading_turn_need)
                            )
                            if experimental_back_off_behavior_active:
                                early_embargo_permission = float(early_embargo_permission_fleet)
                                early_embargo_severity = float(early_embargo_severity_fleet)
                                relation_violation_severity = float(
                                    relation_violation_severity_fleet
                                )
                                compressed_line_truth = self._clamp01(
                                    float(relation_violation_severity)
                                )
                                give_ground_severity = self._clamp01(
                                    max(
                                        float(compressed_line_truth),
                                        float(battle_brake_drive_current),
                                    )
                                )
                                coherence_cap = self._clamp01(
                                    float(battle_hold_weight_current)
                                )
                                heading_localizer = self._clamp01(
                                    (0.70 * float(maneuver_context_gate))
                                    + (0.30 * float(near_contact_gate))
                                )
                                late_reopen_release_gate = self._smoothstep01(
                                    (
                                        float(early_embargo_permission)
                                        - float(LOCAL_DESIRE_LATE_REOPEN_EARLY_PERMISSION_ONSET)
                                    )
                                    / max(
                                        1.0
                                        - float(LOCAL_DESIRE_LATE_REOPEN_EARLY_PERMISSION_ONSET),
                                        1e-9,
                                    )
                                )
                                late_reopen_heading_suppression = self._clamp01(
                                    float(late_reopen_contact_gate)
                                    * float(late_reopen_persistence_fleet)
                                    * float(late_reopen_release_gate)
                                )
                                local_heading_overcommit_suppression = self._clamp01(
                                    (
                                        float(
                                            LOCAL_DESIRE_BACKOFF_OVERCOMMIT_SUPPRESSION_COHERENCE_WEIGHT
                                        )
                                        * float(coherence_cap)
                                    )
                                    + (
                                        float(
                                            LOCAL_DESIRE_BACKOFF_OVERCOMMIT_SUPPRESSION_SEVERITY_WEIGHT
                                        )
                                        * float(give_ground_severity)
                                    )
                                    + (
                                        float(
                                            LOCAL_DESIRE_LATE_REOPEN_HEADING_SUPPRESSION_WEIGHT
                                        )
                                        * float(late_reopen_heading_suppression)
                                    )
                                )
                                local_heading_opportunity_permission = self._clamp01(
                                    float(early_embargo_permission)
                                    * (
                                        1.0
                                        - float(local_heading_overcommit_suppression)
                                    )
                                )
                                local_heading_bias_weight = self._clamp01(
                                    float(local_desire_heading_bias_cap)
                                    * float(front_bearing_need)
                                    * float(heading_turn_need)
                                    * float(heading_localizer)
                                    * float(local_heading_opportunity_permission)
                                )
                                speed_localizer = self._clamp01(
                                    (0.65 * float(maneuver_context_gate))
                                    + (0.35 * float(near_contact_gate))
                                )
                                early_embargo_response = self._clamp01(
                                    float(speed_localizer)
                                    * float(early_embargo_severity)
                                )
                                standoff_violation_response = self._clamp01(
                                    float(speed_localizer)
                                    * float(give_ground_severity)
                                )
                                late_reopen_persistence_response = self._clamp01(
                                    float(LOCAL_DESIRE_LATE_REOPEN_SPEED_RESTRAINT_STRENGTH)
                                    * float(late_reopen_contact_gate)
                                    * float(late_reopen_persistence_fleet)
                                    * float(late_reopen_release_gate)
                                    * float(fleet_front_target_forwardness)
                                )
                                speed_restraint_weight = self._clamp01(
                                    max(
                                        float(early_embargo_response),
                                        float(standoff_violation_response),
                                        float(late_reopen_persistence_response),
                                    )
                                )
                                if signed_longitudinal_backpedal_enabled:
                                    backpedal_response = self._clamp01(
                                        max(
                                            float(standoff_violation_response),
                                            float(late_reopen_persistence_response),
                                        )
                                    )
                                    if backpedal_response > 0.0:
                                        desired_longitudinal_travel_scale = -float(
                                            backpedal_response
                                        )
                                    elif early_embargo_response > 0.0:
                                        desired_longitudinal_travel_scale = max(
                                            0.0,
                                            1.0 - float(early_embargo_response),
                                        )
                                speed_brake_floor = float(
                                    LOCAL_DESIRE_BACKOFF_SPEED_BRAKE_FLOOR
                                )
                                speed_restraint_strength_multiplier = float(
                                    LOCAL_DESIRE_BACKOFF_SPEED_RESTRAINT_STRENGTH_MULTIPLIER
                                )
                            else:
                                local_heading_bias_weight = self._clamp01(
                                    float(local_desire_heading_bias_cap)
                                    * float(near_contact_gate)
                                    * float(front_bearing_need)
                                    * float(heading_turn_need)
                                )
                                speed_restraint_weight = self._clamp01(
                                    float(near_contact_gate) * float(speed_turn_need)
                                )
                                speed_brake_floor = float(LOCAL_DESIRE_SPEED_BRAKE_FLOOR)
                                speed_restraint_strength_multiplier = 1.0
                            if local_heading_bias_weight > 0.0 and base_heading_magnitude > 0.0:
                                desired_heading_hat = EngineTickSkeleton._relax_direction(
                                    desired_heading_hat,
                                    attack_hat_xy,
                                    local_heading_bias_weight,
                                )
                                desired_heading_x = (
                                    float(desired_heading_hat[0]) * float(base_heading_magnitude)
                                )
                                desired_heading_y = (
                                    float(desired_heading_hat[1]) * float(base_heading_magnitude)
                                )
                            desired_speed_scale = max(
                                float(speed_brake_floor),
                                1.0
                                - (
                                    float(local_desire_speed_brake_strength)
                                    * float(speed_restraint_strength_multiplier)
                                    * float(speed_restraint_weight)
                                ),
                            )
                unit_desire = {
                    "desired_heading_xy": (float(desired_heading_x), float(desired_heading_y)),
                    "desired_speed_scale": float(desired_speed_scale),
                }
                if signed_longitudinal_backpedal_enabled:
                    unit_desire["desired_longitudinal_travel_scale"] = float(
                        desired_longitudinal_travel_scale
                    )
                unit_desire_by_unit[str(unit_id)] = unit_desire
            if experimental_back_off_behavior_active:
                local_desire_diag_by_fleet[str(fleet_id)] = {
                    "early_embargo_permission": float(early_embargo_permission_fleet),
                    "late_reopen_persistence": float(late_reopen_persistence_fleet),
                }
        return unit_desire_by_unit

    def _build_fixture_expected_position_map(
        self,
        *,
        state: BattleState,
        fleet_id: str,
        centroid_x: float,
        centroid_y: float,
        target_direction: tuple[float, float],
    ) -> dict | None:
        fixture_cfg = getattr(self, "TEST_RUN_FIXTURE_CFG", None)
        if not isinstance(fixture_cfg, dict):
            return None
        if not bool(fixture_cfg.get("expected_position_candidate_active", False)):
            return None
        if str(fixture_cfg.get("fleet_id", "")).strip() != str(fleet_id):
            return None
        local_offsets = fixture_cfg.get("expected_slot_offsets_local")
        if not isinstance(local_offsets, dict):
            return None
        fallback_axis = fixture_cfg.get("initial_forward_hat_xy", (1.0, 0.0))
        if not isinstance(fallback_axis, (list, tuple)) or len(fallback_axis) < 2:
            fallback_axis = (1.0, 0.0)
        frozen_frame_active = bool(fixture_cfg.get("frozen_terminal_frame_active", False))
        frozen_primary_axis_xy = fixture_cfg.get("frozen_terminal_primary_axis_xy")
        frozen_secondary_axis_xy = fixture_cfg.get("frozen_terminal_secondary_axis_xy")
        use_frozen_orientation = (
            frozen_frame_active
            and isinstance(frozen_primary_axis_xy, (list, tuple))
            and len(frozen_primary_axis_xy) >= 2
        )
        if use_frozen_orientation:
            primary_axis_x, primary_axis_y = self._normalize_direction_with_fallback(
                float(frozen_primary_axis_xy[0]),
                float(frozen_primary_axis_xy[1]),
                float(fallback_axis[0]),
                float(fallback_axis[1]),
            )
            if isinstance(frozen_secondary_axis_xy, (list, tuple)) and len(frozen_secondary_axis_xy) >= 2:
                secondary_axis_x, secondary_axis_y = self._normalize_direction_with_fallback(
                    float(frozen_secondary_axis_xy[0]),
                    float(frozen_secondary_axis_xy[1]),
                    -primary_axis_y,
                    primary_axis_x,
                )
            else:
                secondary_axis_x = -primary_axis_y
                secondary_axis_y = primary_axis_x
        else:
            primary_axis_x, primary_axis_y = self._normalize_direction_with_fallback(
                float(target_direction[0]),
                float(target_direction[1]),
                float(fallback_axis[0]),
                float(fallback_axis[1]),
            )
            secondary_axis_x = -primary_axis_y
            secondary_axis_y = primary_axis_x
        expected_positions = {}
        for unit_id, offsets in local_offsets.items():
            unit = state.units.get(str(unit_id))
            if unit is None or unit.hit_points <= 0.0 or str(unit.fleet_id) != str(fleet_id):
                continue
            if not isinstance(offsets, (list, tuple)) or len(offsets) < 2:
                continue
            forward_offset = float(offsets[0])
            lateral_offset = float(offsets[1])
            expected_positions[str(unit_id)] = (
                centroid_x + (forward_offset * primary_axis_x) + (lateral_offset * secondary_axis_x),
                centroid_y + (forward_offset * primary_axis_y) + (lateral_offset * secondary_axis_y),
            )
        return {
            "expected_positions": expected_positions,
            "primary_axis_xy": (primary_axis_x, primary_axis_y),
            "secondary_axis_xy": (secondary_axis_x, secondary_axis_y),
        }

    @staticmethod
    def _largest_connected_component_size(
        alive_positions: list[tuple[float, float]],
        connect_radius_sq: float,
    ) -> int:
        n_alive = len(alive_positions)
        if n_alive <= 1:
            return n_alive
        if connect_radius_sq <= 0.0:
            return 1

        connect_radius = math.sqrt(connect_radius_sq)
        position_rows = [
            (pos_x, pos_y, idx)
            for idx, (pos_x, pos_y) in enumerate(alive_positions)
        ]
        position_hash = EngineTickSkeleton._build_spatial_hash(position_rows, connect_radius)

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
                for px, py, j in EngineTickSkeleton._iter_spatial_hash_neighbors(
                    position_hash,
                    nx,
                    ny,
                    connect_radius,
                ):
                    if visited[j] or j == node:
                        continue
                    ddx = nx - px
                    ddy = ny - py
                    if (ddx * ddx) + (ddy * ddy) <= connect_radius_sq:
                        visited[j] = True
                        stack.append(j)
            if component_size > largest_component_size:
                largest_component_size = component_size
        return largest_component_size

    def _compute_fleet_cohesion_score_geometry(self, state: BattleState, fleet_id: str) -> tuple[float, dict]:
        eps = 1e-12
        rho_low = 0.35
        rho_high = 1.15
        penalty_k = 6.0
        v3_connect_multiplier = 1.1
        v3_r_ref_multiplier = 1.0

        alive_positions, centroid_x, centroid_y = self._collect_alive_fleet_positions(state, fleet_id)
        if alive_positions is None:
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
                "connect_radius_multiplier": v3_connect_multiplier,
                "r_ref_multiplier": v3_r_ref_multiplier,
            }
        if not alive_positions:
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
        n_alive = len(alive_positions)

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
            largest_component_size = self._largest_connected_component_size(alive_positions, connect_radius_sq)
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

    # Historical 2D-era reference retained on a cold path for later conceptual
    # revisit. The maintained mainline no longer uses the v3-named seam; active
    # code should call _compute_fleet_cohesion_score_geometry() instead.
    def _compute_cohesion_v3_geometry(self, state: BattleState, fleet_id: str) -> tuple[float, dict]:
        return self._compute_fleet_cohesion_score_geometry(state, fleet_id)

    def evaluate_cohesion(self, state: BattleState) -> BattleState:
        runtime_cohesion_score = {}
        for fleet_id, fleet in state.fleets.items():
            cohesion_score, _ = self._compute_fleet_cohesion_score_geometry(state, fleet_id)
            runtime_cohesion_score[fleet_id] = cohesion_score

        return replace(state, last_fleet_cohesion_score=runtime_cohesion_score)

    def _evaluate_target_with_v4a_bridge(self, state: BattleState) -> BattleState:
        last_target_direction = {}
        movement_command_direction = {}
        unit_intent_target_by_unit = self._compute_unit_intent_target_by_unit(state)
        self._debug_state["unit_intent_target_by_unit"] = dict(unit_intent_target_by_unit)
        fixture_cfg = getattr(self, "TEST_RUN_FIXTURE_CFG", None)
        fixture_active_mode = (
            str(fixture_cfg.get("active_mode", "battle")).strip().lower()
            if isinstance(fixture_cfg, Mapping)
            else "battle"
        )
        fixture_bundle = getattr(self, "TEST_RUN_FIXTURE_REFERENCE_BUNDLE", None)
        fixture_fleet_id = (
            str(fixture_cfg.get("fleet_id", "")).strip()
            if isinstance(fixture_cfg, Mapping)
            else ""
        )
        fixture_objective_active = (
            fixture_active_mode == FIXTURE_MODE_NEUTRAL
            and isinstance(fixture_bundle, Mapping)
            and bool(fixture_fleet_id)
        )

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
            neutral_fixture_objective_active = (
                fixture_objective_active
                and str(fleet_id) == fixture_fleet_id
                and not enemy_units
            )
            neutral_fixture_terminal_hold_active = (
                neutral_fixture_objective_active
                and isinstance(fixture_bundle, Mapping)
                and (
                    bool(fixture_bundle.get("formation_terminal_active", False))
                    or bool(fixture_bundle.get("formation_hold_active", False))
                )
            )

            if not own_units:
                last_target_direction[fleet_id] = (0.0, 0.0)
                movement_command_direction[fleet_id] = (0.0, 0.0)
                continue
            if neutral_fixture_terminal_hold_active:
                last_target_direction[fleet_id] = (0.0, 0.0)
                movement_command_direction[fleet_id] = (0.0, 0.0)
                continue
            if (not neutral_fixture_objective_active) and (not enemy_units):
                last_target_direction[fleet_id] = (0.0, 0.0)
                movement_command_direction[fleet_id] = (0.0, 0.0)
                continue

            centroid_x, centroid_y = self._compute_position_centroid(own_units)

            def _distance_sq(unit: UnitState) -> float:
                dx = float(unit.position.x) - centroid_x
                dy = float(unit.position.y) - centroid_y
                return (dx * dx) + (dy * dy)

            battle_restore_bundles = getattr(self, "TEST_RUN_BATTLE_RESTORE_BUNDLES_BY_FLEET", None)
            if neutral_fixture_objective_active:
                battle_bundle = fixture_bundle
            else:
                battle_bundle = (
                    battle_restore_bundles.get(str(fleet_id))
                    if isinstance(battle_restore_bundles, Mapping)
                    else None
                )
            if neutral_fixture_objective_active:
                objective_point_xy = fixture_bundle.get("objective_point_xy", None) if isinstance(fixture_bundle, Mapping) else None
                if not isinstance(objective_point_xy, Sequence) or len(objective_point_xy) < 2:
                    objective_contract_3d = fixture_cfg.get("objective_contract_3d") if isinstance(fixture_cfg, Mapping) else None
                    anchor_point_xyz = objective_contract_3d.get("anchor_point_xyz") if isinstance(objective_contract_3d, Mapping) else None
                    if not isinstance(anchor_point_xyz, Sequence) or len(anchor_point_xyz) < 2:
                        raise TypeError(
                            "neutral v4a path requires objective_point_xy or objective_contract_3d anchor"
                        )
                    objective_point_xy = (
                        float(anchor_point_xyz[0]),
                        float(anchor_point_xyz[1]),
                    )
                ref_x = float(objective_point_xy[0])
                ref_y = float(objective_point_xy[1])
            elif isinstance(battle_bundle, Mapping):
                ref_x, ref_y = self._compute_position_centroid(list(enemy_units))
            else:
                sorted_enemy_units = sorted(enemy_units, key=_distance_sq)
                reference_units = sorted_enemy_units[: min(5, len(sorted_enemy_units))]
                ref_x, ref_y = self._compute_position_centroid(reference_units)

            ref_dx = float(ref_x) - float(centroid_x)
            ref_dy = float(ref_y) - float(centroid_y)
            reference_direction_hat, _ = self._normalize_direction(ref_dx, ref_dy)
            reference_distance = math.sqrt((ref_dx * ref_dx) + (ref_dy * ref_dy))
            if isinstance(battle_bundle, Mapping):
                engaged_attack_vectors: list[tuple[float, float]] = []
                for unit in own_units:
                    unit_key = str(unit.unit_id)
                    if unit_key not in unit_intent_target_by_unit:
                        raise KeyError(
                            f"runtime unit_intent_target_by_unit missing key for unit {unit_key!r} "
                            "in v4a bridge target-vector aggregation"
                        )
                    raw_selected_target_id = unit_intent_target_by_unit[unit_key]
                    selected_target_id = (
                        str(raw_selected_target_id).strip()
                        if raw_selected_target_id is not None
                        else ""
                    )
                    if not selected_target_id:
                        continue
                    target_unit = state.units.get(selected_target_id)
                    if target_unit is None or float(target_unit.hit_points) <= 0.0:
                        continue
                    attack_hat_xy, attack_norm = self._normalize_direction(
                        float(target_unit.position.x) - float(unit.position.x),
                        float(target_unit.position.y) - float(unit.position.y),
                    )
                    if attack_norm > 0.0:
                        engaged_attack_vectors.append(
                            (float(attack_hat_xy[0]), float(attack_hat_xy[1]))
                        )
                attack_sum_x = sum(float(vector[0]) for vector in engaged_attack_vectors)
                attack_sum_y = sum(float(vector[1]) for vector in engaged_attack_vectors)
                attack_sum_norm = math.sqrt((attack_sum_x * attack_sum_x) + (attack_sum_y * attack_sum_y))
                effective_fire_axis_raw_hat = reference_direction_hat
                fire_axis_coherence_raw = 0.0
                if engaged_attack_vectors and attack_sum_norm > 1e-12:
                    effective_fire_axis_raw_hat = (
                        float(attack_sum_x) / float(attack_sum_norm),
                        float(attack_sum_y) / float(attack_sum_norm),
                    )
                    fire_axis_coherence_raw = min(
                        1.0,
                        float(attack_sum_norm) / float(len(engaged_attack_vectors)),
                    )
                prior_fire_axis = battle_bundle.get(
                    "effective_fire_axis_current_xy",
                    battle_bundle.get("effective_fire_axis_xy", reference_direction_hat),
                )
                if not isinstance(prior_fire_axis, Sequence) or len(prior_fire_axis) < 2:
                    prior_fire_axis = reference_direction_hat
                prior_fire_axis_hat, prior_fire_axis_norm = self._normalize_direction(
                    float(prior_fire_axis[0]) if len(prior_fire_axis) >= 1 else float(reference_direction_hat[0]),
                    float(prior_fire_axis[1]) if len(prior_fire_axis) >= 2 else float(reference_direction_hat[1]),
                )
                if prior_fire_axis_norm <= 0.0:
                    prior_fire_axis_hat = reference_direction_hat
                effective_fire_axis_hat = self._relax_direction(
                    prior_fire_axis_hat,
                    effective_fire_axis_raw_hat,
                    V4A_EFFECTIVE_FIRE_AXIS_RELAXATION_DEFAULT,
                )
                prior_fire_axis_coherence = float(
                    battle_bundle.get(
                        "effective_fire_axis_coherence_current",
                        battle_bundle.get("effective_fire_axis_coherence", 0.0),
                    )
                )
                fire_axis_coherence = self._relax_scalar(
                    prior_fire_axis_coherence,
                    fire_axis_coherence_raw,
                    V4A_FIRE_AXIS_COHERENCE_RELAXATION_DEFAULT,
                )
                own_front_strip_depth = self._compute_front_strip_depth(
                    own_units,
                    reference_direction_hat,
                    toward_positive=True,
                )
                fire_entry_margin = max(0.0, float(battle_bundle["expected_reference_spacing"]))
                hold_band = max(
                    0.1,
                    float(self.attack_range)
                    * max(0.0, float(battle_bundle["battle_standoff_hold_band_ratio"])),
                )
                hold_weight_strength = self._clamp01(float(battle_bundle["battle_hold_weight_strength"]))
                reference_speed_values = [
                    float(unit.max_speed)
                    for unit in own_units
                    if math.isfinite(float(unit.max_speed)) and float(unit.max_speed) > 0.0
                ]
                if reference_speed_values:
                    relation_reference_speed = sum(reference_speed_values) / float(
                        len(reference_speed_values)
                    )
                else:
                    relation_reference_speed = 1.0
                battle_relation_lead_ticks = float(battle_bundle["battle_relation_lead_ticks"])
                battle_hold_relaxation = float(battle_bundle["battle_hold_relaxation"])
                battle_approach_drive_relaxation = float(battle_bundle["battle_approach_drive_relaxation"])
                relation_scale = max(
                    float(relation_reference_speed) * battle_relation_lead_ticks,
                    float(hold_band),
                    1e-9,
                )
                if neutral_fixture_objective_active:
                    enemy_front_strip_depth = 0.0
                    enemy_front_strip_activation = 0.0
                    target_front_strip_gap_base = 0.0
                    target_front_strip_gap_bias = 0.0
                    target_front_strip_gap = 0.0
                    current_front_strip_gap = float(reference_distance)
                    distance_gap = float(reference_distance)
                else:
                    raw_enemy_front_strip_depth = self._compute_front_strip_depth(
                        enemy_units,
                        reference_direction_hat,
                        toward_positive=False,
                    )
                    combat_surface = getattr(self, "_combat_surface", None)
                    if not isinstance(combat_surface, Mapping):
                        raise TypeError("EngineTickSkeleton._combat_surface missing or invalid")
                    fire_optimal_range_ratio = float(combat_surface["fire_optimal_range_ratio"])
                    if not 0.0 <= fire_optimal_range_ratio <= 1.0:
                        raise ValueError(
                            "active v4a battle gap read requires fire_optimal_range_ratio within [0.0, 1.0], "
                            f"got {fire_optimal_range_ratio}"
                        )
                    fire_optimal_range = float(self.attack_range) * float(fire_optimal_range_ratio)
                    target_front_strip_gap_base = max(
                        0.0,
                        float(fire_optimal_range) - float(fire_entry_margin),
                    )
                    target_front_strip_gap_bias = float(battle_bundle["battle_target_front_strip_gap_bias"])
                    target_front_strip_gap = max(
                        0.0,
                        float(target_front_strip_gap_base) + float(target_front_strip_gap_bias),
                    )
                    enemy_strip_activation_start = (
                        float(target_front_strip_gap)
                        + float(own_front_strip_depth)
                        + float(raw_enemy_front_strip_depth)
                        + (2.0 * float(relation_scale))
                    )
                    enemy_front_strip_activation = self._clamp01(
                        (float(enemy_strip_activation_start) - float(reference_distance))
                        / max(1e-9, float(relation_scale))
                    )
                    enemy_front_strip_depth = (
                        float(raw_enemy_front_strip_depth) * float(enemy_front_strip_activation)
                    )
                    current_front_strip_gap = float(reference_distance) - (
                        float(own_front_strip_depth) + float(enemy_front_strip_depth)
                    )
                    distance_gap = float(current_front_strip_gap) - float(target_front_strip_gap)
                    if isinstance(battle_bundle, dict):
                        battle_bundle["battle_fire_optimal_range"] = float(fire_optimal_range)
                        battle_bundle["battle_enemy_front_strip_depth_raw"] = float(
                            raw_enemy_front_strip_depth
                        )
                        battle_bundle["battle_enemy_front_strip_activation"] = float(
                            enemy_front_strip_activation
                        )
                # Contact-geometry activation should follow front-strip proximity,
                # not whether current fire-control happened to assign a target.
                engagement_geometry_active_raw = self._clamp01(
                    float(enemy_front_strip_activation)
                )
                prior_engagement_geometry_active = float(
                    battle_bundle.get(
                        "engagement_geometry_active_current",
                        battle_bundle.get("engagement_geometry_active", 0.0),
                    )
                )
                engagement_geometry_active = self._relax_scalar(
                    prior_engagement_geometry_active,
                    engagement_geometry_active_raw,
                    V4A_ENGAGEMENT_GEOMETRY_RELAXATION_DEFAULT,
                )
                front_reorientation_weight_raw = (
                    V4A_FRONT_REORIENTATION_MAX_WEIGHT_DEFAULT
                    * float(engagement_geometry_active)
                    * float(fire_axis_coherence)
                )
                prior_front_reorientation_weight = float(
                    battle_bundle.get(
                        "front_reorientation_weight_current",
                        battle_bundle.get("front_reorientation_weight", 0.0),
                    )
                )
                front_reorientation_weight = self._relax_scalar(
                    prior_front_reorientation_weight,
                    front_reorientation_weight_raw,
                    V4A_FRONT_REORIENTATION_RELAXATION_DEFAULT,
                )
                relation_gap_raw = max(
                    -1.0,
                    min(1.0, float(distance_gap) / relation_scale),
                )
                prior_relation_gap_current = float(
                    battle_bundle.get(
                        "battle_relation_gap_current",
                        battle_bundle.get("battle_relation_gap_raw", relation_gap_raw),
                    )
                )
                relation_gap_current = self._relax_scalar(
                    prior_relation_gap_current,
                    float(relation_gap_raw),
                    battle_hold_relaxation,
                )
                close_drive_raw = self._clamp01(-relation_gap_raw)
                prior_close_drive = float(
                    battle_bundle.get(
                        "battle_close_drive_current",
                        battle_bundle.get("battle_close_drive_raw", close_drive_raw),
                    )
                )
                close_drive = self._relax_scalar(
                    prior_close_drive,
                    float(close_drive_raw),
                    battle_hold_relaxation,
                )
                brake_drive_raw = hold_weight_strength * close_drive_raw
                prior_brake_drive = float(
                    battle_bundle.get(
                        "battle_brake_drive_current",
                        battle_bundle.get("battle_brake_drive_raw", brake_drive_raw),
                    )
                )
                brake_drive = self._relax_scalar(
                    prior_brake_drive,
                    float(brake_drive_raw),
                    battle_hold_relaxation,
                )
                hold_weight_raw = hold_weight_strength * self._clamp01(
                    1.0 - min(1.0, abs(relation_gap_raw))
                )
                prior_hold_weight = float(
                    battle_bundle.get(
                        "battle_hold_weight_current",
                        battle_bundle.get("battle_hold_weight_raw", hold_weight_raw),
                    )
                )
                hold_weight = self._relax_scalar(
                    prior_hold_weight,
                    float(hold_weight_raw),
                    battle_hold_relaxation,
                )
                approach_drive_raw = self._clamp01(relation_gap_raw)
                prior_approach_drive = float(
                    battle_bundle.get(
                        "battle_approach_drive_current",
                        battle_bundle.get("battle_approach_drive_raw", approach_drive_raw),
                    )
                )
                approach_drive = self._relax_scalar(
                    prior_approach_drive,
                    float(approach_drive_raw),
                    battle_approach_drive_relaxation,
                )
                if isinstance(battle_bundle, dict):
                    battle_bundle["effective_fire_axis_raw_xy"] = (
                        float(effective_fire_axis_raw_hat[0]),
                        float(effective_fire_axis_raw_hat[1]),
                    )
                    battle_bundle["effective_fire_axis_xy"] = (
                        float(effective_fire_axis_hat[0]),
                        float(effective_fire_axis_hat[1]),
                    )
                    battle_bundle["effective_fire_axis_current_xy"] = (
                        float(effective_fire_axis_hat[0]),
                        float(effective_fire_axis_hat[1]),
                    )
                    battle_bundle["engagement_geometry_active_raw"] = float(engagement_geometry_active_raw)
                    battle_bundle["engagement_geometry_active"] = float(engagement_geometry_active)
                    battle_bundle["engagement_geometry_active_current"] = float(engagement_geometry_active)
                    battle_bundle["front_reorientation_weight_raw"] = float(front_reorientation_weight_raw)
                    battle_bundle["front_reorientation_weight"] = float(front_reorientation_weight)
                    battle_bundle["front_reorientation_weight_current"] = float(front_reorientation_weight)
                    battle_bundle["effective_fire_axis_coherence_raw"] = float(
                        fire_axis_coherence_raw
                    )
                    battle_bundle["effective_fire_axis_coherence"] = float(fire_axis_coherence)
                    battle_bundle["effective_fire_axis_coherence_current"] = float(fire_axis_coherence)
                    battle_bundle["battle_relation_gap_raw"] = float(relation_gap_raw)
                    battle_bundle["battle_relation_gap_current"] = float(relation_gap_current)
                    battle_bundle["battle_fire_entry_margin"] = float(fire_entry_margin)
                    battle_bundle["battle_target_front_strip_gap_base"] = float(
                        target_front_strip_gap_base
                    )
                    battle_bundle["battle_target_front_strip_gap_bias"] = float(
                        target_front_strip_gap_bias
                    )
                    battle_bundle["battle_target_front_strip_gap"] = float(target_front_strip_gap)
                    battle_bundle["battle_current_front_strip_gap"] = float(current_front_strip_gap)
                    battle_bundle["battle_own_front_strip_depth"] = float(own_front_strip_depth)
                    battle_bundle["battle_enemy_front_strip_depth"] = float(enemy_front_strip_depth)
                    battle_bundle["battle_relation_scale"] = float(relation_scale)
                    battle_bundle["battle_relation_lead_ticks"] = float(battle_relation_lead_ticks)
                    battle_bundle["battle_hold_relaxation"] = float(battle_hold_relaxation)
                    battle_bundle["battle_approach_drive_relaxation"] = float(
                        battle_approach_drive_relaxation
                    )
                    battle_bundle["battle_close_drive_raw"] = float(close_drive_raw)
                    battle_bundle["battle_close_drive_current"] = float(close_drive)
                    battle_bundle["battle_brake_drive_raw"] = float(brake_drive_raw)
                    battle_bundle["battle_brake_drive_current"] = float(brake_drive)
                    battle_bundle["battle_hold_weight_raw"] = float(hold_weight_raw)
                    battle_bundle["battle_hold_weight_current"] = float(hold_weight)
                    battle_bundle["battle_approach_drive_raw"] = float(approach_drive_raw)
                    battle_bundle["battle_approach_drive_current"] = float(approach_drive)
                relation_drive = float(approach_drive - brake_drive)
                forward_relation_drive = relation_drive
                direction = (
                    float(reference_direction_hat[0]) * float(forward_relation_drive),
                    float(reference_direction_hat[1]) * float(forward_relation_drive),
                )
                intensity = float(abs(relation_drive))
            else:
                nearest_enemy = min(
                    enemy_units,
                    key=lambda u: (u.position.x - centroid_x) ** 2 + (u.position.y - centroid_y) ** 2,
                )

                dx = nearest_enemy.position.x - centroid_x
                dy = nearest_enemy.position.y - centroid_y
                norm = math.sqrt((dx * dx) + (dy * dy))

                if norm > 0.0:
                    direction = (dx / norm, dy / norm)
                    intensity = 1.0
                else:
                    direction = (0.0, 0.0)
                    intensity = 0.0

            last_target_direction[fleet_id] = (
                float(reference_direction_hat[0]),
                float(reference_direction_hat[1]),
            )
            movement_command_direction[fleet_id] = direction

        return replace(
            state,
            last_target_direction=last_target_direction,
            movement_command_direction=movement_command_direction,
        )

    def evaluate_target(self, state: BattleState) -> BattleState:
        battle_restore_bundles = getattr(self, "TEST_RUN_BATTLE_RESTORE_BUNDLES_BY_FLEET", None)
        fixture_cfg = getattr(self, "TEST_RUN_FIXTURE_CFG", None)
        fixture_bundle = getattr(self, "TEST_RUN_FIXTURE_REFERENCE_BUNDLE", None)
        if (
            isinstance(battle_restore_bundles, Mapping)
            or isinstance(fixture_cfg, Mapping)
            or isinstance(fixture_bundle, Mapping)
        ):
            return self._evaluate_target_with_v4a_bridge(state)

        last_target_direction = {}
        movement_command_direction = {}

        for fleet_id, fleet in state.fleets.items():
            own_units = [state.units[uid] for uid in fleet.unit_ids if uid in state.units]
            enemy_units = [unit for unit in state.units.values() if unit.fleet_id != fleet_id]

            if not own_units or not enemy_units:
                last_target_direction[fleet_id] = (0.0, 0.0)
                movement_command_direction[fleet_id] = (0.0, 0.0)
                continue

            centroid_x = sum(unit.position.x for unit in own_units) / len(own_units)
            centroid_y = sum(unit.position.y for unit in own_units) / len(own_units)

            nearest_enemy = min(
                enemy_units,
                key=lambda u: (u.position.x - centroid_x) ** 2 + (u.position.y - centroid_y) ** 2,
            )

            dx = nearest_enemy.position.x - centroid_x
            dy = nearest_enemy.position.y - centroid_y
            norm = math.sqrt((dx * dx) + (dy * dy))

            if norm > 0.0:
                direction = (dx / norm, dy / norm)
                intensity = 1.0
            else:
                direction = (0.0, 0.0)

            last_target_direction[fleet_id] = direction
            movement_command_direction[fleet_id] = direction

        return replace(
            state,
            last_target_direction=last_target_direction,
            movement_command_direction=movement_command_direction,
        )

    # Retained as the canonical utility-layer seam after target evaluation; maintained mainline keeps it as a no-op.
    def evaluate_utility(self, state: BattleState) -> BattleState:
        return state

    # Short stage-private runtime helpers stay close to the stage owner.
    def _integrate_movement_symmetric_merge(self, state: BattleState) -> BattleState:
        fleet_ids = list(state.fleets.keys())
        if len(fleet_ids) <= 1:
            return self.integrate_movement(state)

        base_fleets = state.fleets
        merged_units = dict(state.units)
        merged_last_target_direction = dict(state.last_target_direction)
        merged_coarse_body_heading_current = dict(state.coarse_body_heading_current)
        merged_movement_command_direction = dict(state.movement_command_direction)
        first_debug_snapshot = None
        for lead_fleet_id in fleet_ids:
            ordered_fleets = {lead_fleet_id: base_fleets[lead_fleet_id]}
            for other_fleet_id in fleet_ids:
                if other_fleet_id != lead_fleet_id:
                    ordered_fleets[other_fleet_id] = base_fleets[other_fleet_id]
            moved_variant = self.integrate_movement(replace(state, fleets=ordered_fleets))
            variant_debug_tick = getattr(self, "debug_diag_last_tick", None)
            if isinstance(variant_debug_tick, dict):
                if first_debug_snapshot is None:
                    first_debug_snapshot = {
                        "debug_diag_last_tick": dict(variant_debug_tick),
                    }
                    base_tick = first_debug_snapshot["debug_diag_last_tick"]
                    v4a_bridge_tick = variant_debug_tick.get("v4a_bridge", {})
                    if isinstance(v4a_bridge_tick, Mapping):
                        base_tick["v4a_bridge"] = {"fleets": {}}
                        v4a_bridge_fleets = v4a_bridge_tick.get("fleets", {})
                        if isinstance(v4a_bridge_fleets, Mapping):
                            base_tick["v4a_bridge"]["fleets"] = {
                                str(fleet_id): dict(row)
                                for fleet_id, row in v4a_bridge_fleets.items()
                                if isinstance(row, Mapping)
                            }
                    local_desire_tick = variant_debug_tick.get("local_desire", {})
                    if isinstance(local_desire_tick, Mapping):
                        base_tick["local_desire"] = {"fleets": {}}
                        local_desire_fleets = local_desire_tick.get("fleets", {})
                        if isinstance(local_desire_fleets, Mapping):
                            base_tick["local_desire"]["fleets"] = {
                                str(fleet_id): dict(row)
                                for fleet_id, row in local_desire_fleets.items()
                                if isinstance(row, Mapping)
                            }
                else:
                    base_tick = first_debug_snapshot.get("debug_diag_last_tick")
                    if isinstance(base_tick, dict):
                        v4a_bridge_tick = variant_debug_tick.get("v4a_bridge", {})
                        if isinstance(v4a_bridge_tick, Mapping):
                            base_v4a_bridge = base_tick.setdefault("v4a_bridge", {"fleets": {}})
                            if not isinstance(base_v4a_bridge, dict):
                                base_v4a_bridge = {"fleets": {}}
                                base_tick["v4a_bridge"] = base_v4a_bridge
                            base_v4a_bridge_fleets = base_v4a_bridge.setdefault("fleets", {})
                            if not isinstance(base_v4a_bridge_fleets, dict):
                                base_v4a_bridge_fleets = {}
                                base_v4a_bridge["fleets"] = base_v4a_bridge_fleets
                            variant_v4a_bridge_fleets = v4a_bridge_tick.get("fleets", {})
                            if isinstance(variant_v4a_bridge_fleets, Mapping):
                                for fleet_id, row in variant_v4a_bridge_fleets.items():
                                    if isinstance(row, Mapping):
                                        base_v4a_bridge_fleets[str(fleet_id)] = dict(row)
                        local_desire_tick = variant_debug_tick.get("local_desire", {})
                        if isinstance(local_desire_tick, Mapping):
                            base_local_desire = base_tick.setdefault("local_desire", {"fleets": {}})
                            if not isinstance(base_local_desire, dict):
                                base_local_desire = {"fleets": {}}
                                base_tick["local_desire"] = base_local_desire
                            base_local_desire_fleets = base_local_desire.setdefault("fleets", {})
                            if not isinstance(base_local_desire_fleets, dict):
                                base_local_desire_fleets = {}
                                base_local_desire["fleets"] = base_local_desire_fleets
                            variant_local_desire_fleets = local_desire_tick.get("fleets", {})
                            if isinstance(variant_local_desire_fleets, Mapping):
                                for fleet_id, row in variant_local_desire_fleets.items():
                                    if isinstance(row, Mapping):
                                        base_local_desire_fleets[str(fleet_id)] = dict(row)
            for unit_id in base_fleets[lead_fleet_id].unit_ids:
                moved_unit = moved_variant.units.get(unit_id)
                if moved_unit is not None:
                    merged_units[unit_id] = moved_unit
            if lead_fleet_id in moved_variant.last_target_direction:
                merged_last_target_direction[lead_fleet_id] = moved_variant.last_target_direction[lead_fleet_id]
            if lead_fleet_id in moved_variant.coarse_body_heading_current:
                merged_coarse_body_heading_current[lead_fleet_id] = moved_variant.coarse_body_heading_current[
                    lead_fleet_id
                ]
            if lead_fleet_id in moved_variant.movement_command_direction:
                merged_movement_command_direction[lead_fleet_id] = moved_variant.movement_command_direction[
                    lead_fleet_id
                ]
        if first_debug_snapshot is not None:
            self.debug_diag_last_tick = first_debug_snapshot["debug_diag_last_tick"]
        return replace(
            state,
            units=merged_units,
            last_target_direction=merged_last_target_direction,
            coarse_body_heading_current=merged_coarse_body_heading_current,
            movement_command_direction=merged_movement_command_direction,
        )

    def _apply_fixture_terminal_late_clamp(
        self,
        pre_movement_state: BattleState,
        moved_state: BattleState,
    ) -> BattleState:
        fixture_cfg = getattr(self, "TEST_RUN_FIXTURE_CFG", None)
        if not (
            isinstance(fixture_cfg, dict)
            and str(fixture_cfg.get("active_mode", "")).strip().lower() == FIXTURE_MODE_NEUTRAL
        ):
            return moved_state

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
                _, pre_centroid_x, pre_centroid_y = self._collect_alive_fleet_positions(pre_movement_state, fixture_fleet_id)
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
        if isinstance(pending_diag, dict) and int(pending_diag.get("tick", -1)) == int(pre_movement_state.tick):
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
        return moved_state

    # D. Maintained runtime stage owners.
    def integrate_movement(self, state: BattleState) -> BattleState:
        state = self._prepare_v4a_bridge_state(state)
        movement_surface = self._movement_surface
        diag_surface = self._diag_surface
        boundary_surface = self._boundary_surface
        r_sep = self.separation_radius
        r_sep_sq = r_sep * r_sep
        sep_branch_eps = 1e-14
        sep_threshold_sq = r_sep_sq - sep_branch_eps
        alpha_sep = max(0.0, float(movement_surface["alpha_sep"]))
        max_accel_per_tick = float(movement_surface["max_accel_per_tick"])
        max_decel_per_tick = float(movement_surface["max_decel_per_tick"])
        max_turn_deg_per_tick = float(movement_surface["max_turn_deg_per_tick"])
        turn_speed_min_scale = float(movement_surface["turn_speed_min_scale"])
        signed_longitudinal_backpedal_enabled = movement_surface[
            "signed_longitudinal_backpedal_enabled"
        ]
        if not isinstance(signed_longitudinal_backpedal_enabled, bool):
            raise ValueError(
                "runtime signed_longitudinal_backpedal_enabled must be a boolean"
            )
        signed_longitudinal_reverse_authority_scale = float(
            movement_surface["signed_longitudinal_backpedal_reverse_authority_scale"]
        )
        if (
            not math.isfinite(signed_longitudinal_reverse_authority_scale)
            or not 0.0 < signed_longitudinal_reverse_authority_scale <= 1.0
        ):
            raise ValueError(
                "runtime signed_longitudinal_backpedal_reverse_authority_scale "
                "must be finite and within (0.0, 1.0], "
                f"got {signed_longitudinal_reverse_authority_scale}"
            )
        min_unit_spacing = self.separation_radius
        min_unit_spacing_sq = min_unit_spacing * min_unit_spacing
        attack_range_sq = self.attack_range * self.attack_range
        diag_enabled = bool(diag_surface["runtime_diag_enabled"])
        diag4_enabled = diag_enabled and bool(diag_surface["diag4_enabled"])
        fixture_cfg = getattr(self, "TEST_RUN_FIXTURE_CFG", None)
        fixture_terminal_step_gate_enabled = (
            isinstance(fixture_cfg, dict)
            and bool(fixture_cfg.get("expected_position_candidate_active", False))
            and not bool(fixture_cfg.get("disable_terminal_step_gate", False))
            and isinstance(fixture_cfg.get("objective_contract_3d"), dict)
            and bool(str(fixture_cfg.get("fleet_id", "")).strip())
        )
        fixture_terminal_step_gate_fleet_id = (
            str(fixture_cfg.get("fleet_id", "")).strip()
            if fixture_terminal_step_gate_enabled
            else ""
        )
        fixture_terminal_step_gate_anchor_xy = None
        fixture_terminal_step_gate_stop_radius = 0.0
        if fixture_terminal_step_gate_enabled:
            objective_contract_3d = fixture_cfg.get("objective_contract_3d")
            anchor_point_xyz = (
                objective_contract_3d.get("anchor_point_xyz")
                if isinstance(objective_contract_3d, dict)
                else None
            )
            if isinstance(anchor_point_xyz, (list, tuple)) and len(anchor_point_xyz) >= 2:
                fixture_terminal_step_gate_anchor_xy = (
                    float(anchor_point_xyz[0]),
                    float(anchor_point_xyz[1]),
                )
            fixture_terminal_step_gate_stop_radius = float(fixture_cfg.get("stop_radius", 0.0))
        fixture_trace_enabled = diag_enabled and fixture_terminal_step_gate_enabled
        fixture_trace_fleet_id = (
            fixture_terminal_step_gate_fleet_id
            if fixture_trace_enabled
            else ""
        )
        fixture_trace_anchor_xy = (
            fixture_terminal_step_gate_anchor_xy
            if fixture_trace_enabled
            else None
        )
        arena_linear_size = max(0.0, float(state.arena_size))
        boundary_band_limit = 0.05 * arena_linear_size
        boundary_band_width = max(0.0, min(r_sep, boundary_band_limit))
        boundary_force_events_count_tick = 0
        boundary_soft_enabled = bool(boundary_surface["soft_enabled"])
        boundary_soft_strength = max(0.0, float(boundary_surface["soft_strength"]))

        snapshot_positions = {
            unit_id: (unit.position.x, unit.position.y)
            for unit_id, unit in state.units.items()
            if unit.hit_points > 0.0
        }

        movement_model = str(movement_surface["model"]).strip().lower()
        if movement_model != "v4a":
            raise ValueError(
                f"maintained runtime movement model must be 'v4a', got {movement_model!r}"
            )
        v4a_restore_strength = min(1.0, max(0.0, float(movement_surface["v4a_restore_strength"])))
        fixture_cfg = getattr(self, "TEST_RUN_FIXTURE_CFG", None)
        fixture_active_mode = (
            str(fixture_cfg.get("active_mode", "battle")).strip().lower()
            if isinstance(fixture_cfg, Mapping)
            else "battle"
        )
        fixture_fleet_id = (
            str(fixture_cfg.get("fleet_id", "")).strip()
            if isinstance(fixture_cfg, Mapping)
            else ""
        )
        fixture_bundle = getattr(self, "TEST_RUN_FIXTURE_REFERENCE_BUNDLE", None)
        battle_bundles_by_fleet = getattr(self, "TEST_RUN_BATTLE_RESTORE_BUNDLES_BY_FLEET", None)
        bridge_lead_fleet_id = str(next(iter(state.fleets.keys()), "")).strip()
        unit_intent_target_by_unit = self._debug_state.get("unit_intent_target_by_unit")
        if not isinstance(unit_intent_target_by_unit, Mapping):
            raise RuntimeError(
                "runtime unit_intent_target_by_unit must be a Mapping before movement integration"
            )
        movement_direction_by_fleet: dict[str, tuple[float, float]] = {}
        movement_bundle_by_fleet: dict[str, Mapping[str, object] | None] = {}
        for fleet_id in state.fleets:
            reference_direction = state.last_target_direction.get(fleet_id, (0.0, 0.0))
            movement_direction = reference_direction
            movement_bundle = None
            if str(fleet_id) == bridge_lead_fleet_id:
                if (
                    fixture_active_mode == FIXTURE_MODE_NEUTRAL
                    and str(fleet_id) == fixture_fleet_id
                    and isinstance(fixture_bundle, Mapping)
                ):
                    movement_bundle = fixture_bundle
                elif isinstance(battle_bundles_by_fleet, Mapping):
                    movement_bundle = battle_bundles_by_fleet.get(str(fleet_id))
            if isinstance(movement_bundle, Mapping):
                bundle_direction = state.movement_command_direction.get(fleet_id, reference_direction)
                if isinstance(bundle_direction, Sequence) and len(bundle_direction) >= 2:
                    movement_direction = (
                        float(bundle_direction[0]) if len(bundle_direction) >= 1 else 0.0,
                        float(bundle_direction[1]) if len(bundle_direction) >= 2 else 0.0,
                    )
            movement_direction_by_fleet[str(fleet_id)] = (
                float(movement_direction[0]) if len(movement_direction) >= 1 else 0.0,
                float(movement_direction[1]) if len(movement_direction) >= 2 else 0.0,
            )
            movement_bundle_by_fleet[str(fleet_id)] = (
                movement_bundle if isinstance(movement_bundle, Mapping) else None
            )
        unit_desire_by_unit = self._compute_unit_desire_by_unit(
            state,
            movement_direction_by_fleet=movement_direction_by_fleet,
            movement_bundle_by_fleet=movement_bundle_by_fleet,
            unit_intent_target_by_unit=unit_intent_target_by_unit,
        )
        self._debug_state["unit_desire_by_unit"] = dict(unit_desire_by_unit)
        local_desire_diag_by_fleet = self._debug_state["local_desire_diag_by_fleet"]

        updated_units = dict(state.units)
        fixture_trace_units_pending = None
        for fleet_id, fleet in state.fleets.items():
            reference_direction = state.last_target_direction.get(fleet_id, (0.0, 0.0))
            movement_direction = movement_direction_by_fleet.get(str(fleet_id), reference_direction)

            alive_unit_ids = [
                unit_id
                for unit_id in fleet.unit_ids
                if unit_id in updated_units and updated_units[unit_id].hit_points > 0.0
            ]
            alive_count = len(alive_unit_ids)
            if alive_count > 0:
                sum_x = 0.0
                sum_y = 0.0
                for unit_id in alive_unit_ids:
                    unit = updated_units[unit_id]
                    sum_x += unit.position.x
                    sum_y += unit.position.y
                centroid_x = sum_x / alive_count
                centroid_y = sum_y / alive_count
            else:
                centroid_x = 0.0
                centroid_y = 0.0

            fixture_trace_units = None
            fixture_centroid_distance_pre = float("nan")
            fixture_within_stop_radius_pre = False
            fixture_axis_to_objective_x = 0.0
            fixture_axis_to_objective_y = 0.0
            fixture_step_magnitude_gate_active = False
            fixture_step_magnitude_gain = 1.0
            if (
                fixture_terminal_step_gate_enabled
                and str(fleet_id) == fixture_terminal_step_gate_fleet_id
                and fixture_terminal_step_gate_anchor_xy is not None
            ):
                axis_to_objective_dx = float(fixture_terminal_step_gate_anchor_xy[0]) - float(centroid_x)
                axis_to_objective_dy = float(fixture_terminal_step_gate_anchor_xy[1]) - float(centroid_y)
                fixture_centroid_distance_pre = math.sqrt(
                    (axis_to_objective_dx * axis_to_objective_dx)
                    + (axis_to_objective_dy * axis_to_objective_dy)
                )
                if fixture_centroid_distance_pre > 1e-12:
                    fixture_axis_to_objective_x = axis_to_objective_dx / fixture_centroid_distance_pre
                    fixture_axis_to_objective_y = axis_to_objective_dy / fixture_centroid_distance_pre
                fixture_within_stop_radius_pre = (
                    fixture_terminal_step_gate_stop_radius > 0.0
                    and fixture_centroid_distance_pre <= fixture_terminal_step_gate_stop_radius
                )
                if fixture_within_stop_radius_pre and fixture_terminal_step_gate_stop_radius > 1e-12:
                    fixture_step_magnitude_gate_active = True
                    fixture_step_magnitude_gain = max(
                        0.0,
                        min(
                            1.0,
                            fixture_centroid_distance_pre / fixture_terminal_step_gate_stop_radius,
                        ),
                    )
            if (
                fixture_trace_enabled
                and str(fleet_id) == fixture_trace_fleet_id
                and fixture_trace_anchor_xy is not None
            ):
                fixture_trace_units = {}
            signed_longitudinal_travel_min = float("inf")
            signed_longitudinal_speed_min = float("inf")
            signed_longitudinal_count = 0

            separation_accumulator = {unit_id: [0.0, 0.0] for unit_id in alive_unit_ids}
            alive_snapshot_rows = [
                (snapshot_positions[unit_id][0], snapshot_positions[unit_id][1], idx, unit_id)
                for idx, unit_id in enumerate(alive_unit_ids)
            ]
            alive_snapshot_hash = self._build_spatial_hash(alive_snapshot_rows, r_sep)
            for pos_i_x, pos_i_y, idx_i, unit_i in alive_snapshot_rows:
                neighbor_rows = [
                    row
                    for row in self._iter_spatial_hash_neighbors(
                        alive_snapshot_hash,
                        pos_i_x,
                        pos_i_y,
                        r_sep,
                    )
                    if row[2] > idx_i
                ]
                neighbor_rows.sort(key=lambda row: row[2])
                for pos_j_x, pos_j_y, _, unit_j in neighbor_rows:
                    dx = pos_i_x - pos_j_x
                    dy = pos_i_y - pos_j_y
                    distance_sq = (dx * dx) + (dy * dy)
                    if 0.0 < distance_sq < sep_threshold_sq:
                        distance = math.sqrt(distance_sq)
                        decay = 1.0 - (distance / r_sep)
                        vx = (dx / distance) * decay
                        vy = (dy / distance) * decay
                        separation_accumulator[unit_i][0] += vx
                        separation_accumulator[unit_i][1] += vy
                        separation_accumulator[unit_j][0] -= vx
                        separation_accumulator[unit_j][1] -= vy

            fixture_expected_reference = self._build_fixture_expected_position_map(
                state=state,
                fleet_id=fleet_id,
                centroid_x=centroid_x,
                centroid_y=centroid_y,
                target_direction=movement_direction,
            )
            fixture_expected_positions = (
                fixture_expected_reference.get("expected_positions", {})
                if isinstance(fixture_expected_reference, dict)
                else {}
            )
            fixture_expected_primary_axis_xy = (
                fixture_expected_reference.get("primary_axis_xy")
                if isinstance(fixture_expected_reference, dict)
                else None
            )
            fixture_expected_secondary_axis_xy = (
                fixture_expected_reference.get("secondary_axis_xy")
                if isinstance(fixture_expected_reference, dict)
                else None
            )
            legality_reference_positions = (
                {
                    str(unit_id): (float(position[0]), float(position[1]))
                    for unit_id, position in fixture_expected_positions.items()
                    if isinstance(position, tuple) and len(position) >= 2
                }
                if fixture_expected_positions
                else {}
            )
            legality_middle_stage_active = bool(legality_reference_positions)
            fixture_restore_deadband = 0.0
            fixture_cfg = getattr(self, "TEST_RUN_FIXTURE_CFG", None)
            if (
                isinstance(fixture_cfg, dict)
                and bool(fixture_cfg.get("expected_position_candidate_active", False))
            ):
                fixture_restore_deadband = (
                    float(self.separation_radius) * NEUTRAL_TRANSIT_FIXTURE_RESTORE_DEADBAND_RATIO
                )

            for unit_id in fleet.unit_ids:
                if unit_id not in updated_units:
                    continue
                unit = updated_units[unit_id]
                expected_position = fixture_expected_positions.get(str(unit_id))
                using_fixture_expected_position = isinstance(expected_position, tuple) and len(expected_position) >= 2
                if using_fixture_expected_position:
                    cohesion_vector_x = float(expected_position[0]) - unit.position.x
                    cohesion_vector_y = float(expected_position[1]) - unit.position.y
                else:
                    cohesion_vector_x = centroid_x - unit.position.x
                    cohesion_vector_y = centroid_y - unit.position.y
                cohesion_axial_raw = 0.0
                cohesion_axial_gated = 0.0
                one_sided_axial_restore_gate_active = False
                if (
                    using_fixture_expected_position
                    and isinstance(fixture_expected_primary_axis_xy, (list, tuple))
                    and len(fixture_expected_primary_axis_xy) >= 2
                ):
                    restore_axis_x = float(fixture_expected_primary_axis_xy[0])
                    restore_axis_y = float(fixture_expected_primary_axis_xy[1])
                    if (
                        isinstance(fixture_expected_secondary_axis_xy, (list, tuple))
                        and len(fixture_expected_secondary_axis_xy) >= 2
                    ):
                        restore_lateral_x = float(fixture_expected_secondary_axis_xy[0])
                        restore_lateral_y = float(fixture_expected_secondary_axis_xy[1])
                    else:
                        restore_lateral_x = -restore_axis_y
                        restore_lateral_y = restore_axis_x
                    cohesion_axial_raw = (
                        (cohesion_vector_x * restore_axis_x)
                        + (cohesion_vector_y * restore_axis_y)
                    )
                    cohesion_lateral_raw = (
                        (cohesion_vector_x * restore_lateral_x)
                        + (cohesion_vector_y * restore_lateral_y)
                    )
                    cohesion_axial_gated = cohesion_axial_raw
                    if fixture_step_magnitude_gate_active and cohesion_axial_gated < 0.0:
                        one_sided_axial_restore_gate_active = True
                        cohesion_axial_gated = cohesion_axial_gated * fixture_step_magnitude_gain
                    cohesion_vector_x = (
                        (cohesion_axial_gated * restore_axis_x)
                        + (cohesion_lateral_raw * restore_lateral_x)
                    )
                    cohesion_vector_y = (
                        (cohesion_axial_gated * restore_axis_y)
                        + (cohesion_lateral_raw * restore_lateral_y)
                    )
                cohesion_norm_raw = math.sqrt((cohesion_vector_x * cohesion_vector_x) + (cohesion_vector_y * cohesion_vector_y))
                cohesion_deadband_triggered = False
                cohesion_norm = cohesion_norm_raw
                if using_fixture_expected_position and cohesion_norm < fixture_restore_deadband:
                    cohesion_deadband_triggered = True
                    cohesion_norm = 0.0
                    cohesion_vector_x = 0.0
                    cohesion_vector_y = 0.0
                if cohesion_norm > 0.0:
                    cohesion_dir = (cohesion_vector_x / cohesion_norm, cohesion_vector_y / cohesion_norm)
                else:
                    cohesion_dir = (0.0, 0.0)

                sep = separation_accumulator.get(unit_id, [0.0, 0.0])
                sep_norm = math.sqrt((sep[0] * sep[0]) + (sep[1] * sep[1]))
                if sep_norm > 0.0:
                    separation_dir = (sep[0] / sep_norm, sep[1] / sep_norm)
                else:
                    separation_dir = (0.0, 0.0)

                boundary_x = 0.0
                boundary_y = 0.0
                if (
                    boundary_soft_enabled
                    and boundary_band_width > 0.0
                    and boundary_soft_strength > 0.0
                ):
                    arena_max = float(state.arena_size)
                    d_left = unit.position.x
                    d_right = arena_max - unit.position.x
                    d_bottom = unit.position.y
                    d_top = arena_max - unit.position.y

                    def _phi_wall(d: float) -> float:
                        if d < boundary_band_width:
                            ratio = (boundary_band_width - d) / boundary_band_width
                            return ratio * ratio
                        return 0.0

                    phi_left = _phi_wall(d_left)
                    phi_right = _phi_wall(d_right)
                    phi_bottom = _phi_wall(d_bottom)
                    phi_top = _phi_wall(d_top)
                    boundary_x = (phi_left - phi_right) * boundary_soft_strength
                    boundary_y = (phi_bottom - phi_top) * boundary_soft_strength
                    if diag_enabled and (phi_left > 0.0 or phi_right > 0.0 or phi_bottom > 0.0 or phi_top > 0.0):
                        boundary_force_events_count_tick += 1

                # Maintained v4a restore is direct and single-owned:
                # restore_term = restore_strength * normalize(restore_vector)
                cohesion_x = v4a_restore_strength * cohesion_dir[0]
                cohesion_y = v4a_restore_strength * cohesion_dir[1]
                unit_desire = unit_desire_by_unit[str(unit_id)]
                desire_heading_xy = unit_desire["desired_heading_xy"]
                if not isinstance(desire_heading_xy, Sequence) or len(desire_heading_xy) < 2:
                    raise ValueError(
                        "runtime unit_desire_by_unit desired_heading_xy must be a length>=2 sequence, "
                        f"got {desire_heading_xy!r}"
                    )
                desire_heading_x = float(desire_heading_xy[0]) if len(desire_heading_xy) >= 1 else 0.0
                desire_heading_y = float(desire_heading_xy[1]) if len(desire_heading_xy) >= 2 else 0.0
                desired_speed_scale_input = self._clamp01(float(unit_desire["desired_speed_scale"]))
                desired_longitudinal_travel_scale = 1.0
                if signed_longitudinal_backpedal_enabled:
                    if "desired_longitudinal_travel_scale" not in unit_desire:
                        raise KeyError(
                            "runtime unit_desire_by_unit missing "
                            "desired_longitudinal_travel_scale while "
                            "signed_longitudinal_backpedal is enabled"
                        )
                    desired_longitudinal_travel_scale = float(
                        unit_desire["desired_longitudinal_travel_scale"]
                    )
                    if (
                        not math.isfinite(desired_longitudinal_travel_scale)
                        or not -1.0 <= desired_longitudinal_travel_scale <= 1.0
                    ):
                        raise ValueError(
                            "runtime desired_longitudinal_travel_scale must be "
                            "finite and within [-1.0, 1.0], "
                            f"got {desired_longitudinal_travel_scale}"
                        )
                target_term_x = float(desire_heading_x)
                target_term_y = float(desire_heading_y)
                separation_term_x = alpha_sep * separation_dir[0]
                separation_term_y = alpha_sep * separation_dir[1]
                boundary_term_x = alpha_sep * boundary_x
                boundary_term_y = alpha_sep * boundary_y
                maneuver_x = target_term_x + separation_term_x + boundary_term_x
                maneuver_y = target_term_y + separation_term_y + boundary_term_y
                total_x = cohesion_x + maneuver_x
                total_y = cohesion_y + maneuver_y
                total_norm = math.sqrt((total_x * total_x) + (total_y * total_y))
                if total_norm > 0.0:
                    total_direction = (total_x / total_norm, total_y / total_norm)
                else:
                    total_direction = (0.0, 0.0)

                movement_eps = 1e-12
                pre_projection_step_scale = 0.0
                pre_projection_total_dx = 0.0
                pre_projection_total_dy = 0.0
                pre_projection_total_norm = 0.0
                step_distance = 0.0
                step_speed = 0.0
                current_heading_hat, current_heading_norm = self._normalize_direction(
                    float(unit.orientation_vector.x),
                    float(unit.orientation_vector.y),
                )
                if current_heading_norm <= movement_eps:
                    current_heading_hat = self._normalize_direction_with_fallback(
                        float(desire_heading_x),
                        float(desire_heading_y),
                        1.0,
                        0.0,
                    )
                desired_heading_hat = total_direction if total_norm > movement_eps else current_heading_hat
                if signed_longitudinal_backpedal_enabled:
                    desired_heading_hat, desired_heading_norm = self._normalize_direction(
                        float(desire_heading_x),
                        float(desire_heading_y),
                    )
                    if desired_heading_norm <= movement_eps:
                        raise ValueError(
                            "runtime desired_heading_xy must provide a finite facing "
                            "axis while signed_longitudinal_backpedal is enabled"
                        )
                realized_heading_hat = self._rotate_direction_toward(
                    current_heading_hat,
                    desired_heading_hat,
                    max_turn_deg_per_tick,
                )
                heading_alignment_for_speed = 1.0
                if total_norm > movement_eps:
                    heading_alignment_for_speed = max(
                        0.0,
                        (float(realized_heading_hat[0]) * float(desired_heading_hat[0]))
                        + (float(realized_heading_hat[1]) * float(desired_heading_hat[1])),
                    )
                desired_speed_scale = float(turn_speed_min_scale)
                if total_norm > movement_eps:
                    desired_speed_scale = float(turn_speed_min_scale) + (
                        (1.0 - float(turn_speed_min_scale)) * float(heading_alignment_for_speed)
                    )
                desired_speed = (
                    float(unit.max_speed)
                    * float(fixture_step_magnitude_gain)
                    * float(desired_speed_scale_input)
                    * float(desired_speed_scale)
                )
                if (
                    signed_longitudinal_backpedal_enabled
                    and desired_longitudinal_travel_scale >= 0.0
                    and total_norm > movement_eps
                ):
                    desired_speed *= max(
                        0.0,
                        (float(total_direction[0]) * float(realized_heading_hat[0]))
                        + (float(total_direction[1]) * float(realized_heading_hat[1])),
                    )
                max_accel_delta = float(max_accel_per_tick) * float(state.dt)
                max_decel_delta = float(max_decel_per_tick) * float(state.dt)
                signed_step_distance = 0.0
                if signed_longitudinal_backpedal_enabled:
                    longitudinal_authority_scale = (
                        float(signed_longitudinal_reverse_authority_scale)
                        if desired_longitudinal_travel_scale < 0.0
                        else 1.0
                    )
                    desired_signed_longitudinal_speed = (
                        float(desired_speed)
                        * float(desired_longitudinal_travel_scale)
                        * float(longitudinal_authority_scale)
                    )
                    current_signed_longitudinal_speed = (
                        (float(unit.velocity.x) * float(current_heading_hat[0]))
                        + (float(unit.velocity.y) * float(current_heading_hat[1]))
                    )
                    if not math.isfinite(current_signed_longitudinal_speed):
                        raise ValueError(
                            "runtime current signed longitudinal speed must be finite "
                            "when signed_longitudinal_backpedal is enabled"
                        )
                    if desired_signed_longitudinal_speed >= current_signed_longitudinal_speed:
                        step_speed = min(
                            float(desired_signed_longitudinal_speed),
                            float(current_signed_longitudinal_speed)
                            + float(max_accel_delta),
                        )
                    else:
                        step_speed = max(
                            float(desired_signed_longitudinal_speed),
                            float(current_signed_longitudinal_speed)
                            - float(max_decel_delta),
                        )
                    signed_step_distance = float(step_speed) * float(state.dt)
                    step_distance = abs(float(signed_step_distance))
                    signed_longitudinal_travel_min = min(
                        float(signed_longitudinal_travel_min),
                        float(desired_longitudinal_travel_scale),
                    )
                    signed_longitudinal_speed_min = min(
                        float(signed_longitudinal_speed_min),
                        float(step_speed),
                    )
                    signed_longitudinal_count += 1
                else:
                    current_speed = math.sqrt(
                        (float(unit.velocity.x) * float(unit.velocity.x))
                        + (float(unit.velocity.y) * float(unit.velocity.y))
                    )
                    if not math.isfinite(current_speed):
                        current_speed = 0.0
                    if desired_speed >= current_speed:
                        step_speed = min(
                            float(desired_speed),
                            float(current_speed) + float(max_accel_delta),
                        )
                    else:
                        step_speed = max(
                            float(desired_speed),
                            float(current_speed) - float(max_decel_delta),
                        )
                    step_speed = max(0.0, float(step_speed))
                    step_distance = float(step_speed) * float(state.dt)
                    signed_step_distance = float(step_distance)
                if total_norm > movement_eps:
                    pre_projection_step_scale = (
                        signed_step_distance / total_norm
                        if step_distance > movement_eps
                        else 0.0
                    )
                if step_distance > movement_eps:
                    pre_projection_total_dx = float(realized_heading_hat[0]) * signed_step_distance
                    pre_projection_total_dy = float(realized_heading_hat[1]) * signed_step_distance
                    pre_projection_total_norm = math.sqrt(
                        (pre_projection_total_dx * pre_projection_total_dx)
                        + (pre_projection_total_dy * pre_projection_total_dy)
                    )
                    orientation = Vec2(x=float(realized_heading_hat[0]), y=float(realized_heading_hat[1]))
                    velocity = Vec2(
                        x=float(realized_heading_hat[0]) * step_speed,
                        y=float(realized_heading_hat[1]) * step_speed,
                    )
                else:
                    orientation = Vec2(x=float(current_heading_hat[0]), y=float(current_heading_hat[1]))
                    velocity = Vec2(x=0.0, y=0.0)

                new_position = Vec2(
                    x=unit.position.x + pre_projection_total_dx,
                    y=unit.position.y + pre_projection_total_dy,
                )
                if fixture_trace_units is not None:
                    target_norm_raw = math.sqrt((target_term_x * target_term_x) + (target_term_y * target_term_y))
                    base_target_norm = math.sqrt(
                        (float(movement_direction[0]) * float(movement_direction[0]))
                        + (float(movement_direction[1]) * float(movement_direction[1]))
                    )
                    if base_target_norm > 1e-12:
                        forward_gain_effective = target_norm_raw / base_target_norm
                    else:
                        forward_gain_effective = 0.0
                    fixture_trace_units[str(unit_id)] = {
                        "fleet_id": str(fleet_id),
                        "unit_id": str(unit_id),
                        "x_pre": float(unit.position.x),
                        "y_pre": float(unit.position.y),
                        "centroid_x_pre": float(centroid_x),
                        "centroid_y_pre": float(centroid_y),
                        "centroid_to_objective_distance_pre": float(fixture_centroid_distance_pre),
                        "within_stop_radius_pre": bool(fixture_within_stop_radius_pre),
                        "axis_to_objective_x": float(fixture_axis_to_objective_x),
                        "axis_to_objective_y": float(fixture_axis_to_objective_y),
                        "target_dir_x": float(desire_heading_x),
                        "target_dir_y": float(desire_heading_y),
                        "fleet_movement_dir_x": float(movement_direction[0]),
                        "fleet_movement_dir_y": float(movement_direction[1]),
                        "desired_speed_scale_input": float(desired_speed_scale_input),
                        "forward_gain_effective": float(forward_gain_effective),
                        "target_contrib_dx": float(target_term_x * pre_projection_step_scale),
                        "target_contrib_dy": float(target_term_y * pre_projection_step_scale),
                        "using_fixture_expected_position": bool(using_fixture_expected_position),
                        "expected_pos_x": float(expected_position[0]) if using_fixture_expected_position else None,
                        "expected_pos_y": float(expected_position[1]) if using_fixture_expected_position else None,
                        "cohesion_vector_x": float(
                            (float(expected_position[0]) - unit.position.x)
                            if using_fixture_expected_position
                            else (centroid_x - unit.position.x)
                        ),
                        "cohesion_vector_y": float(
                            (float(expected_position[1]) - unit.position.y)
                            if using_fixture_expected_position
                            else (centroid_y - unit.position.y)
                        ),
                        "cohesion_norm": float(cohesion_norm_raw),
                        "cohesion_axial_raw": float(cohesion_axial_raw),
                        "cohesion_axial_gated": float(cohesion_axial_gated),
                        "one_sided_axial_restore_gate_active": bool(one_sided_axial_restore_gate_active),
                        "cohesion_deadband_triggered": bool(cohesion_deadband_triggered),
                        "cohesion_contrib_dx": float(cohesion_x * pre_projection_step_scale),
                        "cohesion_contrib_dy": float(cohesion_y * pre_projection_step_scale),
                        "separation_dir_x": float(separation_dir[0]),
                        "separation_dir_y": float(separation_dir[1]),
                        "separation_norm": float(sep_norm),
                        "separation_contrib_dx": float(separation_term_x * pre_projection_step_scale),
                        "separation_contrib_dy": float(separation_term_y * pre_projection_step_scale),
                        "boundary_x": float(boundary_x),
                        "boundary_y": float(boundary_y),
                        "boundary_contrib_dx": float(boundary_term_x * pre_projection_step_scale),
                        "boundary_contrib_dy": float(boundary_term_y * pre_projection_step_scale),
                        "step_magnitude_gate_active": bool(fixture_step_magnitude_gate_active),
                        "step_magnitude_gain": float(fixture_step_magnitude_gain),
                        "locomotion_heading_alignment": float(heading_alignment_for_speed),
                        "locomotion_desired_speed": float(desired_speed),
                        "locomotion_realized_speed": float(step_speed),
                        "locomotion_heading_x": float(realized_heading_hat[0]),
                        "locomotion_heading_y": float(realized_heading_hat[1]),
                        "pre_projection_total_dx": float(pre_projection_total_dx),
                        "pre_projection_total_dy": float(pre_projection_total_dy),
                        "pre_projection_total_norm": float(pre_projection_total_norm),
                        "projection_dx": 0.0,
                        "projection_dy": 0.0,
                        "projection_disp_norm": 0.0,
                        "late_clamp_active_for_tick": False,
                        "late_clamp_overshoot": 0.0,
                        "late_clamp_dx": 0.0,
                        "late_clamp_dy": 0.0,
                    }
                updated_units[unit_id] = replace(
                    unit,
                    position=new_position,
                    velocity=velocity,
                    orientation_vector=orientation,
                )

            if fixture_trace_units is not None:
                fixture_trace_units_pending = fixture_trace_units
            if (
                signed_longitudinal_backpedal_enabled
                and signed_longitudinal_count > 0
            ):
                local_desire_row = local_desire_diag_by_fleet.setdefault(str(fleet_id), {})
                local_desire_row["desired_longitudinal_travel_scale_min"] = float(
                    signed_longitudinal_travel_min
                )
                local_desire_row["realized_signed_longitudinal_speed_min"] = float(
                    signed_longitudinal_speed_min
                )

        # Single-pass post-movement projection using tentative snapshot positions.
        tentative_positions = {
            unit_id: (unit.position.x, unit.position.y)
            for unit_id, unit in updated_units.items()
            if unit.hit_points > 0.0
        }
        delta_position = {unit_id: [0.0, 0.0] for unit_id in tentative_positions}
        projection_pairs_count = 0
        rank_by_unit = {}
        global_alive_ids = []
        for fleet in state.fleets.values():
            alive_ids = [
                unit_id
                for unit_id in fleet.unit_ids
                if unit_id in tentative_positions and updated_units[unit_id].hit_points > 0.0
            ]
            fleet_local_sorted = []
            for fleet_order, unit_id in enumerate(alive_ids):
                numeric_index = self._fleet_local_numeric_index(unit_id, fleet_order + 1)
                fleet_local_sorted.append((numeric_index, fleet_order, unit_id))
            fleet_local_sorted.sort(key=lambda x: (x[0], x[1]))
            for rank, (_, _, unit_id) in enumerate(fleet_local_sorted, start=1):
                rank_by_unit[unit_id] = rank
            global_alive_ids.extend(alive_ids)

        global_alive_rows = [
            (tentative_positions[unit_id][0], tentative_positions[unit_id][1], idx, unit_id)
            for idx, unit_id in enumerate(global_alive_ids)
        ]
        global_alive_hash = self._build_spatial_hash(global_alive_rows, min_unit_spacing)
        for pos_i_x, pos_i_y, idx_i, unit_i in global_alive_rows:
            neighbor_rows = [
                row
                for row in self._iter_spatial_hash_neighbors(
                    global_alive_hash,
                    pos_i_x,
                    pos_i_y,
                    min_unit_spacing,
                )
                if row[2] > idx_i
            ]
            neighbor_rows.sort(key=lambda row: row[2])
            for pos_j_x, pos_j_y, _, unit_j in neighbor_rows:
                dx = pos_i_x - pos_j_x
                dy = pos_i_y - pos_j_y
                distance_sq = (dx * dx) + (dy * dy)
                if distance_sq < (min_unit_spacing_sq - sep_branch_eps):
                    if diag_enabled:
                        projection_pairs_count += 1
                    if distance_sq > 0.0:
                        distance = math.sqrt(distance_sq)
                        nx = dx / distance
                        ny = dy / distance
                    else:
                        rank_i = rank_by_unit.get(unit_i, 1)
                        rank_j = rank_by_unit.get(unit_j, 1)
                        rank_low = rank_i if rank_i < rank_j else rank_j
                        rank_high = rank_j if rank_i < rank_j else rank_i

                        dx_seed = ((rank_low * 73856093) ^ (rank_high * 19349663)) % 1024
                        dy_seed = ((rank_low * 83492791) ^ (rank_high * 2971215073)) % 1024
                        sx = float(dx_seed - 512)
                        sy = float(dy_seed - 512)
                        if sx == 0.0 and sy == 0.0:
                            sy = 1.0
                        seed_norm = math.sqrt((sx * sx) + (sy * sy))
                        nx = sx / seed_norm
                        ny = sy / seed_norm

                    penetration = min_unit_spacing - math.sqrt(distance_sq)
                    correction_x = nx * penetration
                    correction_y = ny * penetration
                    delta_position[unit_i][0] += 0.5 * correction_x
                    delta_position[unit_i][1] += 0.5 * correction_y
                    delta_position[unit_j][0] -= 0.5 * correction_x
                    delta_position[unit_j][1] -= 0.5 * correction_y

        for unit_id, unit in updated_units.items():
            if unit_id in tentative_positions:
                base_x, base_y = tentative_positions[unit_id]
                dx_proj, dy_proj = delta_position[unit_id]
                if fixture_trace_units_pending is not None and str(unit_id) in fixture_trace_units_pending:
                    fixture_trace_units_pending[str(unit_id)]["projection_dx"] = float(dx_proj)
                    fixture_trace_units_pending[str(unit_id)]["projection_dy"] = float(dy_proj)
                    fixture_trace_units_pending[str(unit_id)]["projection_disp_norm"] = float(
                        math.sqrt((dx_proj * dx_proj) + (dy_proj * dy_proj))
                    )
                updated_units[unit_id] = replace(unit, position=Vec2(x=base_x + dx_proj, y=base_y + dy_proj))

        # Optional hard boundary: clamp units into map domain [0, arena_size].
        if bool(boundary_surface["hard_enabled"]):
            arena_min = 0.0
            arena_max = float(state.arena_size)
            if arena_max < arena_min:
                arena_max = arena_min
            for unit_id, unit in updated_units.items():
                if unit.hit_points <= 0.0:
                    continue
                px = unit.position.x
                py = unit.position.y
                if px < arena_min:
                    px = arena_min
                elif px > arena_max:
                    px = arena_max
                if py < arena_min:
                    py = arena_min
                elif py > arena_max:
                    py = arena_max
                if px != unit.position.x or py != unit.position.y:
                    updated_units[unit_id] = replace(unit, position=Vec2(x=px, y=py))

        if diag4_enabled:
            final_positions = {
                unit_id: (unit.position.x, unit.position.y)
                for unit_id, unit in updated_units.items()
                if unit.hit_points > 0.0
            }
        else:
            final_positions = {}
        if legality_middle_stage_active:
            legality_feasible_positions = {
                str(unit_id): (float(unit.position.x), float(unit.position.y))
                for unit_id, unit in updated_units.items()
                if unit.hit_points > 0.0 and str(unit_id) in legality_reference_positions
            }
        else:
            legality_feasible_positions = {}
        legality_handoff_ready = bool(legality_feasible_positions)

        _MovementDiagSupport.flush_pending(
            self,
            diag_enabled=diag_enabled,
            state=state,
            updated_units=updated_units,
            tentative_positions=tentative_positions,
            delta_position=delta_position,
            projection_pairs_count=projection_pairs_count,
            boundary_force_events_count_tick=boundary_force_events_count_tick,
            r_sep=r_sep,
            r_sep_sq=r_sep_sq,
            attack_range_sq=attack_range_sq,
            final_positions=final_positions,
            diag4_enabled=diag4_enabled,
            legality_reference_surface_count=len(legality_reference_positions),
            legality_feasible_surface_count=len(legality_feasible_positions),
            legality_middle_stage_active=legality_middle_stage_active,
            legality_handoff_ready=legality_handoff_ready,
            fixture_trace_fleet_id=fixture_trace_fleet_id,
            fixture_trace_units_pending=fixture_trace_units_pending,
        )

        return replace(state, units=updated_units)

    def _compute_unit_intent_target_by_unit(self, state: BattleState) -> dict[str, str | None]:
        combat_cmp_eps = 1e-14
        attack_range_sq = self.attack_range * self.attack_range
        combat_surface = self._combat_surface
        forward_fire_cone_half_angle_deg = float(combat_surface["fire_cone_half_angle_deg"])
        if not math.isfinite(forward_fire_cone_half_angle_deg):
            raise ValueError(
                "runtime fire-control fire_cone_half_angle_deg must be finite, "
                f"got {forward_fire_cone_half_angle_deg}"
            )
        if not 0.0 <= forward_fire_cone_half_angle_deg <= 180.0:
            raise ValueError(
                "runtime fire-control fire_cone_half_angle_deg must be within [0.0, 180.0], "
                f"got {forward_fire_cone_half_angle_deg}"
            )
        forward_fire_cone_cos_threshold = math.cos(
            math.radians(float(forward_fire_cone_half_angle_deg))
        )
        snapshot_positions = {}
        alive_units = {}
        for unit_id, unit in state.units.items():
            if unit.hit_points <= 0.0:
                continue
            alive_units[unit_id] = unit
            snapshot_positions[unit_id] = (unit.position.x, unit.position.y)

        combat_scan_rows = []
        scan_order = 0
        for fleet in state.fleets.values():
            for rank, unit_id in enumerate(fleet.unit_ids, start=1):
                unit = alive_units.get(unit_id)
                if unit is None:
                    continue
                ex, ey = snapshot_positions[unit_id]
                enemy_max_hp = unit.max_hit_points
                if enemy_max_hp > 0.0:
                    normalized_hp = unit.hit_points / enemy_max_hp
                else:
                    normalized_hp = 0.0
                combat_scan_rows.append(
                    (
                        ex,
                        ey,
                        scan_order,
                        unit_id,
                        unit.fleet_id,
                        normalized_hp,
                        self._fleet_local_numeric_index(unit_id, rank),
                    )
                )
                scan_order += 1
        combat_scan_hash = self._build_spatial_hash(combat_scan_rows, self.attack_range)

        # Runtime-local placement only; the same minimal selector contract is reused
        # across pre-movement unit intent and post-movement combat re-check, but this
        # does not settle the long-term shared spatial service owner.
        selected_target_by_unit = {}
        for attacker_id, attacker in alive_units.items():
            attacker_pos_x, attacker_pos_y = snapshot_positions[attacker_id]
            best_enemy_id = None
            best_dist_sq = 0.0
            best_rank = 0
            best_scan_order = 0
            for enemy_x, enemy_y, scan_order, enemy_id, enemy_fleet_id, _normalized_hp, rank in self._iter_spatial_hash_neighbors(
                combat_scan_hash,
                attacker_pos_x,
                attacker_pos_y,
                self.attack_range,
            ):
                if enemy_fleet_id == attacker.fleet_id:
                    continue
                dx = enemy_x - attacker_pos_x
                dy = enemy_y - attacker_pos_y
                distance_sq = (dx * dx) + (dy * dy)
                if distance_sq > (attack_range_sq - combat_cmp_eps):
                    continue
                distance = math.sqrt(distance_sq)
                ux = dx / max(distance, 1e-12)
                uy = dy / max(distance, 1e-12)
                orient = attacker.orientation_vector
                ox = float(orient.x)
                oy = float(orient.y)
                orientation_norm_sq = (ox * ox) + (oy * oy)
                if orientation_norm_sq > 1e-12:
                    orientation_norm = math.sqrt(orientation_norm_sq)
                    cos_theta = ((ox / orientation_norm) * ux) + ((oy / orientation_norm) * uy)
                    if cos_theta < forward_fire_cone_cos_threshold:
                        continue
                if best_enemy_id is None:
                    best_enemy_id = enemy_id
                    best_dist_sq = distance_sq
                    best_rank = rank
                    best_scan_order = scan_order
                    continue
                if distance_sq < (best_dist_sq - combat_cmp_eps):
                    best_enemy_id = enemy_id
                    best_dist_sq = distance_sq
                    best_rank = rank
                    best_scan_order = scan_order
                    continue
                if abs(distance_sq - best_dist_sq) <= combat_cmp_eps:
                    if rank < best_rank or (rank == best_rank and scan_order < best_scan_order):
                            best_enemy_id = enemy_id
                            best_dist_sq = distance_sq
                            best_rank = rank
                            best_scan_order = scan_order
            selected_target_by_unit[attacker_id] = best_enemy_id
        return selected_target_by_unit

    def resolve_combat(self, state: BattleState, selected_target_by_unit: Mapping[str, str | None]) -> BattleState:
        combat_surface = self._combat_surface
        diag_surface = self._diag_surface
        combat_cmp_eps = 1e-14
        attack_range_sq = self.attack_range * self.attack_range
        CH_ENABLED = bool(combat_surface["ch_enabled"])
        h_raw = float(combat_surface["contact_hysteresis_h"])
        h = min(0.2, max(0.0, h_raw))
        r_exit = self.attack_range
        r_enter = self.attack_range * (1.0 - h)
        r_exit_sq = r_exit * r_exit
        r_enter_sq = r_enter * r_enter
        alpha_raw = float(combat_surface["fire_angle_quality_alpha"])
        fire_angle_quality_alpha = min(1.0, max(0.0, alpha_raw))
        optimal_range_ratio_raw = float(combat_surface["fire_optimal_range_ratio"])
        fire_optimal_range_ratio = min(1.0, max(0.0, optimal_range_ratio_raw))
        optimal_range = self.attack_range * fire_optimal_range_ratio
        diag_enabled = bool(diag_surface["runtime_diag_enabled"])
        diag4_enabled = diag_enabled and bool(diag_surface["diag4_enabled"])
        forward_fire_cone_half_angle_deg = float(combat_surface["fire_cone_half_angle_deg"])
        if not math.isfinite(forward_fire_cone_half_angle_deg):
            raise ValueError(
                "runtime fire-control fire_cone_half_angle_deg must be finite, "
                f"got {forward_fire_cone_half_angle_deg}"
            )
        if not 0.0 <= forward_fire_cone_half_angle_deg <= 180.0:
            raise ValueError(
                "runtime fire-control fire_cone_half_angle_deg must be within [0.0, 180.0], "
                f"got {forward_fire_cone_half_angle_deg}"
            )
        forward_fire_cone_cos_threshold = math.cos(
            math.radians(float(forward_fire_cone_half_angle_deg))
        )

        def _compute_angle_quality(attacker, ux: float, uy: float) -> float:
            if fire_angle_quality_alpha <= 0.0:
                return 1.0
            orient = attacker.orientation_vector
            ox = orient.x
            oy = orient.y
            o_norm_sq = (ox * ox) + (oy * oy)
            if o_norm_sq <= 0.0:
                return 1.0
            o_norm = math.sqrt(o_norm_sq)
            nox = ox / o_norm
            noy = oy / o_norm
            cos_theta = max(-1.0, min(1.0, (nox * ux) + (noy * uy)))
            return max(0.0, 1.0 + (fire_angle_quality_alpha * cos_theta))

        def _compute_range_quality(distance: float) -> float:
            if self.attack_range <= 0.0:
                return 0.0
            if optimal_range >= (self.attack_range - 1e-12):
                return 1.0
            if distance <= optimal_range:
                return 1.0
            denom = max(self.attack_range - optimal_range, 1e-12)
            return max(0.0, min(1.0, (self.attack_range - distance) / denom))

        snapshot_positions = {}
        alive_units = {}
        for unit_id, unit in state.units.items():
            if unit.hit_points <= 0.0:
                continue
            alive_units[unit_id] = unit
            snapshot_positions[unit_id] = (unit.position.x, unit.position.y)

        incoming_damage = {unit_id: 0.0 for unit_id in alive_units}
        total_hp_before = sum(unit.hit_points for unit in alive_units.values())
        in_contact_count = 0
        damage_events_count = 0
        sample_contact_debug = None
        engaged_updates = {}
        in_contact_units = set()
        orientation_override = {}

        for attacker_id, attacker in alive_units.items():
            if attacker_id not in selected_target_by_unit:
                raise KeyError(
                    f"runtime selected_target_by_unit missing key for attacker {attacker_id!r} "
                    "in resolve_combat"
                )
            target_id = selected_target_by_unit[attacker_id]
            if target_id is None:
                engaged_updates[attacker_id] = (False, None)
                continue
            target = alive_units.get(target_id)
            if target is None or target.fleet_id == attacker.fleet_id:
                engaged_updates[attacker_id] = (False, None)
                continue
            attacker_pos_x, attacker_pos_y = snapshot_positions[attacker_id]
            target_pos_x, target_pos_y = snapshot_positions[target_id]
            dx_contact = target_pos_x - attacker_pos_x
            dy_contact = target_pos_y - attacker_pos_y
            d_sq = (dx_contact * dx_contact) + (dy_contact * dy_contact)
            if d_sq > (attack_range_sq - combat_cmp_eps):
                engaged_updates[attacker_id] = (False, None)
                continue
            distance = math.sqrt(d_sq)
            ux = dx_contact / max(distance, 1e-12)
            uy = dy_contact / max(distance, 1e-12)
            orient = attacker.orientation_vector
            ox = float(orient.x)
            oy = float(orient.y)
            orientation_norm_sq = (ox * ox) + (oy * oy)
            if orientation_norm_sq > 1e-12:
                orientation_norm = math.sqrt(orientation_norm_sq)
                cos_theta = ((ox / orientation_norm) * ux) + ((oy / orientation_norm) * uy)
                if cos_theta < forward_fire_cone_cos_threshold:
                    engaged_updates[attacker_id] = (False, None)
                    continue
            angle_quality_assigned = _compute_angle_quality(attacker, ux, uy)
            range_quality_assigned = _compute_range_quality(distance)
            expected_damage_ratio_assigned = max(1e-6, angle_quality_assigned * range_quality_assigned)
            prev_engaged = attacker.engaged
            prev_target_id = attacker.engaged_target_id

            if CH_ENABLED:
                if prev_engaged and prev_target_id == target_id:
                    in_contact = d_sq <= (r_exit_sq + combat_cmp_eps)
                else:
                    in_contact = d_sq <= (r_enter_sq + combat_cmp_eps)
            else:
                in_contact = d_sq <= (r_exit_sq + combat_cmp_eps)

            if in_contact:
                engaged_updates[attacker_id] = (True, target_id)
            else:
                engaged_updates[attacker_id] = (False, None)

            if not in_contact:
                continue

            in_contact_count += 1
            if diag_enabled:
                in_contact_units.add(attacker_id)
                in_contact_units.add(target_id)
            q = max(0.0, float(angle_quality_assigned))
            range_quality = max(0.0, min(1.0, float(range_quality_assigned)))
            event_damage = self.damage_per_tick * q * range_quality
            incoming_damage[target_id] += event_damage
            damage_events_count += 1
            if sample_contact_debug is None:
                sample_contact_debug = {
                    "attacker_id": attacker_id,
                    "target_id": target_id,
                    "distance_sq": d_sq,
                    "r_enter_sq": r_enter_sq,
                    "r_exit_sq": r_exit_sq,
                    "angle_quality": q,
                    "range_quality": range_quality,
                    "expected_damage_ratio": float(expected_damage_ratio_assigned),
                    "damage": event_damage,
                }

            velocity_norm_sq = (attacker.velocity.x * attacker.velocity.x) + (attacker.velocity.y * attacker.velocity.y)
            if velocity_norm_sq <= 1e-12 and d_sq > 0.0:
                orient_norm = math.sqrt(d_sq)
                if orient_norm > 0.0:
                    orientation_override[attacker_id] = Vec2(
                        x=dx_contact / orient_norm,
                        y=dy_contact / orient_norm,
                    )

        updated_units = {}
        for unit_id, unit in alive_units.items():
            new_hp = unit.hit_points - incoming_damage[unit_id]
            if new_hp > 0.0:
                engaged_state = engaged_updates.get(unit_id, (unit.engaged, unit.engaged_target_id))
                if unit_id in orientation_override:
                    updated_units[unit_id] = replace(
                        unit,
                        hit_points=new_hp,
                        engaged=engaged_state[0],
                        engaged_target_id=engaged_state[1],
                        orientation_vector=orientation_override[unit_id],
                    )
                else:
                    updated_units[unit_id] = replace(
                        unit,
                        hit_points=new_hp,
                        engaged=engaged_state[0],
                        engaged_target_id=engaged_state[1],
                    )
        total_hp_after = sum(unit.hit_points for unit in updated_units.values())
        self.debug_last_combat_stats = {
            "in_contact_count": in_contact_count,
            "damage_events_count": damage_events_count,
            "total_hp_before": total_hp_before,
            "total_hp_after": total_hp_after,
            "sample": sample_contact_debug,
            "tick": state.tick,
        }
        if diag_enabled:
            pending_diag = self._debug_state.get("diag_pending")
            if pending_diag is not None and pending_diag.get("tick") == state.tick:
                tick_diag = pending_diag
            else:
                tick_diag = {"tick": state.tick}
            if diag4_enabled:
                contact_window_raw = int(diag_surface["diag4_contact_window"])
                contact_window = min(200, max(20, contact_window_raw))
                contact_history = self._ensure_debug_dict("_debug_diag4_contact_history")

                alive_diag_units = set(alive_units.keys())
                for unit_id in alive_diag_units:
                    history = contact_history.get(unit_id, [])
                    if unit_id in in_contact_units:
                        history.append(1)
                    else:
                        history.append(0)
                    if len(history) > contact_window:
                        history = history[-contact_window:]
                    contact_history[unit_id] = history

                for unit_id in list(contact_history.keys()):
                    if unit_id not in alive_diag_units:
                        del contact_history[unit_id]

                rolling_contact_ratio_by_unit = {}
                for unit_id, history in contact_history.items():
                    if history:
                        rolling_contact_ratio_by_unit[unit_id] = sum(history) / len(history)
                    else:
                        rolling_contact_ratio_by_unit[unit_id] = 0.0

                diag4_tick = tick_diag.get("diag4")
                if isinstance(diag4_tick, dict):
                    module_a = diag4_tick.get("module_a")
                    if isinstance(module_a, dict):
                        topk_candidates = module_a.get("topk_candidates")
                        if isinstance(topk_candidates, dict):
                            isolated_candidates = 0
                            blocked_candidates = 0
                            for candidates in topk_candidates.values():
                                if not isinstance(candidates, list):
                                    continue
                                for row in candidates:
                                    if not isinstance(row, dict):
                                        continue
                                    unit_id = row.get("unit_id")
                                    row["rolling_in_contact_ratio"] = rolling_contact_ratio_by_unit.get(unit_id, 0.0)
                                    neighbor_sep = int(row.get("neighbor_count_sep", 0))
                                    neighbor_contact = int(row.get("neighbor_count_contact", 0))
                                    if neighbor_sep <= 0:
                                        isolated_candidates += 1
                                    elif neighbor_contact <= 0:
                                        blocked_candidates += 1
                            module_a["isolated_candidate_count"] = isolated_candidates
                            module_a["blocked_candidate_count"] = blocked_candidates
                            module_a["rolling_contact_window"] = contact_window

            tick_diag["combat"] = {
                "in_contact_count": in_contact_count,
                "damage_events_count": damage_events_count,
            }
            self.debug_diag_last_tick = tick_diag
            diag_timeseries = self._debug_state.get("diag_timeseries")
            if not isinstance(diag_timeseries, list):
                diag_timeseries = []
                self._debug_state["diag_timeseries"] = diag_timeseries
            diag_timeseries.append(tick_diag)

        updated_fleets = {}
        for fleet_id, fleet in state.fleets.items():
            alive_ids = tuple(unit_id for unit_id in fleet.unit_ids if unit_id in updated_units)
            updated_fleets[fleet_id] = replace(fleet, unit_ids=alive_ids)

        return replace(state, units=updated_units, fleets=updated_fleets)
