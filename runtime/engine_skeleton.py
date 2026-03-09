from dataclasses import replace
import math

from runtime.runtime_v0_1 import BattleState, Vec2


class EngineTickSkeleton:
    def __init__(
        self,
        attack_range: float = 3.0,
        damage_per_tick: float = 1.0,
        separation_radius: float = 1.0,
    ) -> None:
        self.attack_range = float(attack_range)
        self.damage_per_tick = float(damage_per_tick)
        self.separation_radius = float(separation_radius)
        self.last_damage_clamp_triggered = False
        self.debug_contact_assert = False
        self.debug_contact_sample_ticks = 50
        self.debug_last_combat_stats = {}
        self.FSR_ENABLED = False
        self.BOUNDARY_SOFT_ENABLED = True
        self.BOUNDARY_HARD_ENABLED = False
        self.boundary_soft_strength = 1.0
        self.alpha_sep = 0.6
        self.fsr_strength = 0.0
        self.fsr_lambda_delta = 0.10
        self._fsr_reference = {}
        self.debug_last_fsr_stats = {}
        self.debug_fsr_diag_enabled = False
        self.debug_outlier_eta = 1.8
        self.debug_outlier_persistence_ticks = 20
        self.debug_diag4_enabled = False
        self.debug_diag4_topk = 10
        self.debug_diag4_contact_window = 20
        self.debug_diag4_return_sector_deg = 30.0
        self.debug_diag4_neighbor_k = 3
        self.debug_diag4_rpg_enabled = False
        self.debug_diag4_rpg_window = 20
        self._debug_outlier_streaks = {}
        self._debug_diag_pending = None
        self.debug_diag_timeseries = []
        self.debug_diag_last_tick = {}
        self._debug_diag4_contact_history = {}
        self._debug_diag4_prev_unit_state = {}
        self._debug_diag4_prev_unit_radius = {}
        self._debug_diag4_transition_counts = {}
        self._debug_diag4_first_outlier_tick = {}
        self._debug_diag4_return_attempt_count = {}
        self._debug_diag4_outlier_return_count = {}
        self._debug_diag4_outlier_duration = {}
        self._debug_diag4_max_outlier_duration = {}
        self._debug_diag4_disp_history = {}
        self._debug_diag4_persistent_records = {}
        self._debug_diag4_outlier_streaks = {}
        self._debug_diag4_rpg_outlier_entry = {}
        self._debug_diag4_rpg_return_stats = {}
        self._debug_boundary_force_events_total = 0
        # Phase V.4-b: canonical decision source switches to cohesion_v2.
        # "v1_debug" is retained only for baseline comparison / diagnostics.
        self.COHESION_DECISION_SOURCE = "v2"
        self.debug_cohesion_v1_enabled = False
        self.debug_last_cohesion_v1 = {}
        self.debug_last_cohesion_v2 = {}
        self.debug_last_cohesion_v2_components = {}
        self.debug_cohesion_v3_shadow_enabled = False
        self.debug_last_cohesion_v3 = {}
        self.debug_last_cohesion_v3_components = {}
        self._debug_prev_cohesion_v1 = {}
        self.MOVEMENT_MODEL = "v3a"

    def step(self, state: BattleState) -> BattleState:
        snapshot = replace(state, tick=state.tick + 1)
        next_state = self.evaluate_cohesion(snapshot)
        next_state = self.evaluate_target(next_state)
        next_state = self.evaluate_utility(next_state)
        next_state = self.integrate_movement(next_state)
        next_state = self.resolve_combat(next_state)
        return next_state

    @staticmethod
    def _clamp01(value: float) -> float:
        if value < 0.0:
            return 0.0
        if value > 1.0:
            return 1.0
        return value

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
            }

        alive_positions = []
        for unit_id in fleet.unit_ids:
            unit = state.units.get(unit_id)
            if unit is None or unit.hit_points <= 0.0:
                continue
            alive_positions.append((unit.position.x, unit.position.y))
        n_alive = len(alive_positions)

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
            # 0 at ratio=1, approaches 1 as q90/q50 grows.
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
        else:
            connect_radius = float(self.separation_radius)
            if connect_radius < eps:
                connect_radius = eps
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
            }

        alive_positions = []
        for unit_id in fleet.unit_ids:
            unit = state.units.get(unit_id)
            if unit is None or unit.hit_points <= 0.0:
                continue
            alive_positions.append((unit.position.x, unit.position.y))
        n_alive = len(alive_positions)

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
        r_ref = float(self.separation_radius) * math.sqrt(float(n_alive))
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
        else:
            connect_radius = float(self.separation_radius)
            if connect_radius < eps:
                connect_radius = eps
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
        }

    def evaluate_cohesion(self, state: BattleState) -> BattleState:
        updated_cohesion_v1 = {}
        updated_cohesion_v2 = {}
        shadow_cohesion = {}
        shadow_components = {}
        shadow_cohesion_v3 = {}
        shadow_components_v3 = {}
        decision_source = str(getattr(self, "COHESION_DECISION_SOURCE", "v2")).lower()
        keep_v1_debug = bool(getattr(self, "debug_cohesion_v1_enabled", False)) or (decision_source == "v1_debug")
        keep_v3_shadow = bool(getattr(self, "debug_cohesion_v3_shadow_enabled", False))
        prev_cohesion_v1 = getattr(self, "_debug_prev_cohesion_v1", None)
        if not isinstance(prev_cohesion_v1, dict):
            prev_cohesion_v1 = {}
        for fleet_id, fleet in state.fleets.items():
            normalized = fleet.parameters.normalized()
            kappa = normalized["formation_rigidity"]
            old_cohesion_v1 = float(prev_cohesion_v1.get(fleet_id, 1.0))
            new_cohesion = old_cohesion_v1 + (kappa * 0.01) - ((1.0 - kappa) * 0.005)
            if new_cohesion < 0.0:
                new_cohesion = 0.0
            elif new_cohesion > 1.0:
                new_cohesion = 1.0
            updated_cohesion_v1[fleet_id] = new_cohesion
            cohesion_v2, v2_components = self._compute_cohesion_v2_geometry(state, fleet_id)
            updated_cohesion_v2[fleet_id] = cohesion_v2
            shadow_cohesion[fleet_id] = cohesion_v2
            shadow_components[fleet_id] = v2_components
            if keep_v3_shadow:
                cohesion_v3, v3_components = self._compute_cohesion_v3_shadow_geometry(state, fleet_id)
                shadow_cohesion_v3[fleet_id] = cohesion_v3
                shadow_components_v3[fleet_id] = v3_components

        self._debug_prev_cohesion_v1 = dict(updated_cohesion_v1)
        if keep_v1_debug:
            self.debug_last_cohesion_v1 = dict(updated_cohesion_v1)
        else:
            self.debug_last_cohesion_v1 = {}
        self.debug_last_cohesion_v2 = shadow_cohesion
        self.debug_last_cohesion_v2_components = shadow_components
        if keep_v3_shadow:
            self.debug_last_cohesion_v3 = dict(shadow_cohesion_v3)
            self.debug_last_cohesion_v3_components = dict(shadow_components_v3)
        else:
            self.debug_last_cohesion_v3 = {}
            self.debug_last_cohesion_v3_components = {}

        # Canonical active cohesion is v2; v1 is debug-only.
        return replace(state, last_fleet_cohesion=updated_cohesion_v2)

    def evaluate_target(self, state: BattleState) -> BattleState:
        last_target_direction = {}
        last_engagement_intensity = {}

        for fleet_id, fleet in state.fleets.items():
            own_units = [state.units[uid] for uid in fleet.unit_ids if uid in state.units]
            enemy_units = [unit for unit in state.units.values() if unit.fleet_id != fleet_id]

            if not own_units or not enemy_units:
                last_target_direction[fleet_id] = (0.0, 0.0)
                last_engagement_intensity[fleet_id] = 0.0
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
                intensity = 0.0

            last_target_direction[fleet_id] = direction
            last_engagement_intensity[fleet_id] = intensity

        return replace(
            state,
            last_target_direction=last_target_direction,
            last_engagement_intensity=last_engagement_intensity,
        )

    def evaluate_utility(self, state: BattleState) -> BattleState:
        return state

    def integrate_movement(self, state: BattleState) -> BattleState:
        r_sep = self.separation_radius
        r_sep_sq = r_sep * r_sep
        sep_branch_eps = 1e-14
        sep_threshold_sq = r_sep_sq - sep_branch_eps
        alpha_sep = float(getattr(self, "alpha_sep", 0.6))
        if alpha_sep < 0.0:
            alpha_sep = 0.0
        min_unit_spacing = self.separation_radius
        min_unit_spacing_sq = min_unit_spacing * min_unit_spacing
        attack_range_sq = self.attack_range * self.attack_range
        diag_enabled = bool(getattr(self, "debug_fsr_diag_enabled", False))
        diag4_enabled = diag_enabled and bool(getattr(self, "debug_diag4_enabled", False))
        diag4_rpg_enabled = diag_enabled and bool(getattr(self, "debug_diag4_rpg_enabled", False))
        diag4_legacy_enabled = diag4_enabled and not diag4_rpg_enabled
        arena_linear_size = float(state.arena_size)
        if arena_linear_size < 0.0:
            arena_linear_size = 0.0
        boundary_band_width = r_sep
        boundary_band_limit = 0.05 * arena_linear_size
        if boundary_band_limit < boundary_band_width:
            boundary_band_width = boundary_band_limit
        if boundary_band_width < 0.0:
            boundary_band_width = 0.0
        boundary_band_fraction = (boundary_band_width / arena_linear_size) if arena_linear_size > 0.0 else 0.0
        boundary_force_events_count_tick = 0
        boundary_soft_strength = float(getattr(self, "boundary_soft_strength", 1.0))
        if boundary_soft_strength < 0.0:
            boundary_soft_strength = 0.0

        def _quantile(sorted_values: list[float], q: float) -> float:
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
                "p10": _quantile(vals, 0.10),
                "p50": _quantile(vals, 0.50),
                "p90": _quantile(vals, 0.90),
                "max": vals[-1],
            }

        snapshot_positions = {
            unit_id: (unit.position.x, unit.position.y)
            for unit_id, unit in state.units.items()
            if unit.hit_points > 0.0
        }

        movement_model = str(getattr(self, "MOVEMENT_MODEL", "v3a")).strip().lower()
        if movement_model not in {"v1", "v3a"}:
            movement_model = "v3a"
        movement_v3a_experiment = str(getattr(self, "MOVEMENT_V3A_EXPERIMENT", "base")).strip().lower()
        # One-cycle compatibility: legacy A-line name maps to canonical probe name.
        if movement_v3a_experiment == "exp_a_reduced_centroid":
            movement_v3a_experiment = "exp_precontact_centroid_probe"
        allowed_v3a_experiments = {"base", "exp_precontact_centroid_probe"}
        if movement_v3a_experiment not in allowed_v3a_experiments:
            movement_v3a_experiment = "base"
        # Canonical probe knob (neutral naming): CENTROID_PROBE_SCALE.
        # One-cycle compatibility: fallback to legacy PRECONTACT_CENTROID_PROBE_SCALE.
        centroid_probe_scale = float(
            getattr(
                self,
                "CENTROID_PROBE_SCALE",
                getattr(self, "PRECONTACT_CENTROID_PROBE_SCALE", 1.0),
            )
        )
        if centroid_probe_scale < 0.0:
            centroid_probe_scale = 0.0
        elif centroid_probe_scale > 1.0:
            centroid_probe_scale = 1.0

        updated_units = dict(state.units)
        for fleet_id, fleet in state.fleets.items():
            target_direction = state.last_target_direction.get(fleet_id, (0.0, 0.0))
            _intensity = state.last_engagement_intensity.get(fleet_id, 0.0)

            alive_units = [
                updated_units[unit_id]
                for unit_id in fleet.unit_ids
                if unit_id in updated_units and updated_units[unit_id].hit_points > 0.0
            ]
            alive_unit_ids = [unit.unit_id for unit in alive_units]
            if alive_units:
                centroid_x = sum(unit.position.x for unit in alive_units) / len(alive_units)
                centroid_y = sum(unit.position.y for unit in alive_units) / len(alive_units)
            else:
                centroid_x = 0.0
                centroid_y = 0.0

            enemy_alive_units = [
                unit
                for other_fleet_id, other_fleet in state.fleets.items()
                if other_fleet_id != fleet_id
                for unit_id in other_fleet.unit_ids
                if unit_id in updated_units and updated_units[unit_id].hit_points > 0.0
                for unit in [updated_units[unit_id]]
            ]
            if enemy_alive_units:
                enemy_centroid_x = sum(unit.position.x for unit in enemy_alive_units) / len(enemy_alive_units)
                enemy_centroid_y = sum(unit.position.y for unit in enemy_alive_units) / len(enemy_alive_units)
            else:
                enemy_centroid_x = centroid_x
                enemy_centroid_y = centroid_y

            radius_sq_sum = 0.0
            for unit in alive_units:
                dx0 = unit.position.x - centroid_x
                dy0 = unit.position.y - centroid_y
                radius_sq_sum += (dx0 * dx0) + (dy0 * dy0)
            if alive_units:
                fleet_rms_radius = math.sqrt(radius_sq_sum / len(alive_units))
            else:
                fleet_rms_radius = 0.0

            # Fleet major-axis geometry metrics for observer diagnostics.
            major_hat_x = 1.0
            major_hat_y = 0.0
            ar_ratio = 1.0
            ar_forward_ratio = 1.0
            if len(alive_units) >= 2:
                n_alive_f = float(len(alive_units))
                var_x = 0.0
                var_y = 0.0
                cov_xy = 0.0
                for unit in alive_units:
                    dxm = unit.position.x - centroid_x
                    dym = unit.position.y - centroid_y
                    var_x += dxm * dxm
                    var_y += dym * dym
                    cov_xy += dxm * dym
                var_x /= n_alive_f
                var_y /= n_alive_f
                cov_xy /= n_alive_f
                trace = var_x + var_y
                delta_sq = ((var_x - var_y) * (var_x - var_y)) + (4.0 * cov_xy * cov_xy)
                if delta_sq < 0.0:
                    delta_sq = 0.0
                delta = math.sqrt(delta_sq)
                lam1 = max(0.0, 0.5 * (trace + delta))
                lam2 = max(0.0, 0.5 * (trace - delta))
                sigma1 = math.sqrt(lam1)
                sigma2 = math.sqrt(lam2)
                ar_ratio = sigma1 / (sigma2 + 1e-12)
                if abs(cov_xy) > 1e-12 or abs(lam1 - var_y) > 1e-12:
                    evx = lam1 - var_y
                    evy = cov_xy
                else:
                    evx = 1.0
                    evy = 0.0
                ev_norm = math.sqrt((evx * evx) + (evy * evy))
                if ev_norm > 1e-12:
                    major_hat_x = evx / ev_norm
                    major_hat_y = evy / ev_norm

                # Forward-axis AR: anisotropy in enemy-facing frame.
                fdx = enemy_centroid_x - centroid_x
                fdy = enemy_centroid_y - centroid_y
                f_norm = math.sqrt((fdx * fdx) + (fdy * fdy))
                if f_norm > 1e-12:
                    fx = fdx / f_norm
                    fy = fdy / f_norm
                    lx = -fy
                    ly = fx
                    forward_values = []
                    lateral_values = []
                    for unit in alive_units:
                        dxm = unit.position.x - centroid_x
                        dym = unit.position.y - centroid_y
                        forward_values.append((dxm * fx) + (dym * fy))
                        lateral_values.append((dxm * lx) + (dym * ly))
                    if forward_values and lateral_values:
                        n_ff = float(len(forward_values))
                        mean_f = sum(forward_values) / n_ff
                        mean_l = sum(lateral_values) / n_ff
                        var_f = 0.0
                        var_l = 0.0
                        for idx in range(len(forward_values)):
                            df = forward_values[idx] - mean_f
                            dl = lateral_values[idx] - mean_l
                            var_f += (df * df)
                            var_l += (dl * dl)
                        var_f /= n_ff
                        var_l /= n_ff
                        sigma_f = math.sqrt(max(0.0, var_f))
                        sigma_l = math.sqrt(max(0.0, var_l))
                        ar_forward_ratio = sigma_f / (sigma_l + 1e-12)

            engaged_alive_count = 0
            for unit in alive_units:
                if bool(unit.engaged) and bool(unit.engaged_target_id):
                    engaged_alive_count += 1
            if alive_units:
                engaged_fraction = engaged_alive_count / float(len(alive_units))
            else:
                engaged_fraction = 0.0
            contact_gate = engaged_fraction / 0.25
            if contact_gate < 0.0:
                contact_gate = 0.0
            elif contact_gate > 1.0:
                contact_gate = 1.0
            precontact_gate = 1.0 - contact_gate

            separation_accumulator = {unit_id: [0.0, 0.0] for unit_id in alive_unit_ids}
            for i in range(len(alive_unit_ids)):
                unit_i = alive_unit_ids[i]
                if unit_i not in snapshot_positions:
                    continue
                pos_i = snapshot_positions[unit_i]
                for j in range(i + 1, len(alive_unit_ids)):
                    unit_j = alive_unit_ids[j]
                    if unit_j not in snapshot_positions:
                        continue
                    pos_j = snapshot_positions[unit_j]
                    dx = pos_i[0] - pos_j[0]
                    dy = pos_i[1] - pos_j[1]
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

            kappa = fleet.parameters.normalized()["formation_rigidity"]
            pd_norm = fleet.parameters.normalized().get("pursuit_drive", 0.5)
            mobility_raw = float(fleet.parameters.mobility_bias)
            # Canonical 1-9 mapping:
            # MB_eff = 0.2 * (mobility_bias - 5) / 4, clipped to [-0.2, +0.2].
            mb = 0.2 * (mobility_raw - 5.0) / 4.0
            if mb < -0.2:
                mb = -0.2
            elif mb > 0.2:
                mb = 0.2

            # Phase V3 canonical PD activation:
            # EnemyCollapseSignal = 1 - EnemyCohesion
            # PursuitConfirmThreshold = 1 - PD_norm
            enemy_cohesion_values = []
            cohesion_decision_source = str(getattr(self, "COHESION_DECISION_SOURCE", "v2")).lower()
            debug_cohesion_v1 = getattr(self, "debug_last_cohesion_v1", {})
            if not isinstance(debug_cohesion_v1, dict):
                debug_cohesion_v1 = {}
            for other_fleet_id, other_fleet in state.fleets.items():
                if other_fleet_id == fleet_id:
                    continue
                if len(other_fleet.unit_ids) == 0:
                    continue
                if cohesion_decision_source == "v1_debug":
                    cohesion_value = float(debug_cohesion_v1.get(other_fleet_id, state.last_fleet_cohesion.get(other_fleet_id, 1.0)))
                else:
                    cohesion_value = float(state.last_fleet_cohesion.get(other_fleet_id, 1.0))
                enemy_cohesion_values.append(cohesion_value)
            if enemy_cohesion_values:
                enemy_cohesion = sum(enemy_cohesion_values) / len(enemy_cohesion_values)
            else:
                enemy_cohesion = 1.0
            enemy_collapse_signal = 1.0 - enemy_cohesion
            pursuit_confirm_threshold = 1.0 - pd_norm
            deep_pursuit_mode = enemy_collapse_signal > pursuit_confirm_threshold
            if deep_pursuit_mode:
                collapse_excess = enemy_collapse_signal - pursuit_confirm_threshold
                collapse_span = 1.0 - pursuit_confirm_threshold
                if collapse_span <= 1e-12:
                    pursuit_intensity = 1.0
                else:
                    pursuit_intensity = collapse_excess / collapse_span
                if pursuit_intensity < 0.0:
                    pursuit_intensity = 0.0
                elif pursuit_intensity > 1.0:
                    pursuit_intensity = 1.0
            else:
                pursuit_intensity = 0.0
            # DeepPursuitMode effects are movement-only:
            # - stronger forward weighting
            # - weaker cohesion restoration
            # - stronger extension tendency on non-cohesion maneuver
            forward_gain = 1.0 + (0.35 * pursuit_intensity)
            cohesion_gain = 1.0 - (0.35 * pursuit_intensity)
            extension_gain = 1.0 + (0.25 * pursuit_intensity)
            mb_is_zero = abs(mb) <= 1e-12
            tx = target_direction[0]
            ty = target_direction[1]
            target_norm = 0.0
            t_hat_x = 0.0
            t_hat_y = 0.0
            has_target_axis = False
            if not mb_is_zero:
                target_norm = math.sqrt((tx * tx) + (ty * ty))
                if target_norm > 1e-12:
                    t_hat_x = tx / target_norm
                    t_hat_y = ty / target_norm
                    has_target_axis = True

            # Movement 3A constants (observer-audited switch path only).
            attract_gain_base = 0.35
            attract_gain_max = 0.85
            stray_threshold_ratio = 1.15
            lateral_damping_base = 0.25
            enemy_pull_floor = 0.15
            for unit_id in fleet.unit_ids:
                if unit_id not in updated_units:
                    continue
                unit = updated_units[unit_id]
                cohesion_vector_x = centroid_x - unit.position.x
                cohesion_vector_y = centroid_y - unit.position.y
                cohesion_norm = math.sqrt((cohesion_vector_x * cohesion_vector_x) + (cohesion_vector_y * cohesion_vector_y))
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
                    bool(getattr(self, "BOUNDARY_SOFT_ENABLED", True))
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

                if movement_model == "v3a":
                    enemy_vec_x = enemy_centroid_x - unit.position.x
                    enemy_vec_y = enemy_centroid_y - unit.position.y
                    enemy_vec_norm = math.sqrt((enemy_vec_x * enemy_vec_x) + (enemy_vec_y * enemy_vec_y))
                    if enemy_vec_norm > 1e-12:
                        enemy_dir_x = enemy_vec_x / enemy_vec_norm
                        enemy_dir_y = enemy_vec_y / enemy_vec_norm
                    else:
                        enemy_dir_x = target_direction[0]
                        enemy_dir_y = target_direction[1]

                    if fleet_rms_radius > 1e-12:
                        stray_ratio_raw = (cohesion_norm / fleet_rms_radius)
                    else:
                        stray_ratio_raw = 0.0
                    if stray_ratio_raw <= stray_threshold_ratio:
                        stray_factor = 0.0
                    else:
                        stray_factor = (stray_ratio_raw - stray_threshold_ratio) / max(1e-12, 2.0 - stray_threshold_ratio)
                    if stray_factor < 0.0:
                        stray_factor = 0.0
                    elif stray_factor > 1.0:
                        stray_factor = 1.0

                    anti_stretch = 0.0

                    attract_gain = attract_gain_base + ((attract_gain_max - attract_gain_base) * stray_factor)
                    cohesion_scale = 1.0 + (0.40 * anti_stretch)
                    cohesion_x = (kappa * cohesion_gain * cohesion_scale) * cohesion_dir[0]
                    cohesion_y = (kappa * cohesion_gain * cohesion_scale) * cohesion_dir[1]
                    if movement_v3a_experiment == "exp_precontact_centroid_probe":
                        # A-line causal probe: only scale centroid restoration term.
                        cohesion_x *= centroid_probe_scale
                        cohesion_y *= centroid_probe_scale
                    enemy_pull_gain = enemy_pull_floor + ((1.0 - enemy_pull_floor) * stray_factor)
                    attract_x = attract_gain * (
                        (enemy_pull_gain * enemy_dir_x) + ((1.0 - enemy_pull_gain) * target_direction[0])
                    )
                    attract_y = attract_gain * (
                        (enemy_pull_gain * enemy_dir_y) + ((1.0 - enemy_pull_gain) * target_direction[1])
                    )
                    maneuver_x = (
                        (forward_gain * target_direction[0])
                        + attract_x
                        + (alpha_sep * separation_dir[0])
                        + (alpha_sep * boundary_x)
                    )
                    maneuver_y = (
                        (forward_gain * target_direction[1])
                        + attract_y
                        + (alpha_sep * separation_dir[1])
                        + (alpha_sep * boundary_y)
                    )
                    if has_target_axis:
                        dot_mt = (maneuver_x * t_hat_x) + (maneuver_y * t_hat_y)
                        m_parallel_x = dot_mt * t_hat_x
                        m_parallel_y = dot_mt * t_hat_y
                        m_tangent_x = maneuver_x - m_parallel_x
                        m_tangent_y = maneuver_y - m_parallel_y
                        tangent_scale = 1.0 + mb
                        tangent_scale -= (lateral_damping_base * stray_factor)
                        parallel_scale = 1.0
                        if tangent_scale < 0.05:
                            tangent_scale = 0.05
                        maneuver_x = ((1.0 - mb) * parallel_scale * m_parallel_x) + (tangent_scale * m_tangent_x)
                        maneuver_y = ((1.0 - mb) * parallel_scale * m_parallel_y) + (tangent_scale * m_tangent_y)
                    if deep_pursuit_mode:
                        extension_gain_effective = extension_gain
                        maneuver_x *= extension_gain_effective
                        maneuver_y *= extension_gain_effective
                    axial_pull_x = 0.0
                    axial_pull_y = 0.0
                    total_x = cohesion_x + maneuver_x + axial_pull_x
                    total_y = cohesion_y + maneuver_y + axial_pull_y
                else:
                    # Keep MB=0 on the exact legacy path for bitwise regression.
                    if mb_is_zero and not deep_pursuit_mode:
                        total_x = (
                            target_direction[0]
                            + (kappa * cohesion_dir[0])
                            + (alpha_sep * separation_dir[0])
                            + (alpha_sep * boundary_x)
                        )
                        total_y = (
                            target_direction[1]
                            + (kappa * cohesion_dir[1])
                            + (alpha_sep * separation_dir[1])
                            + (alpha_sep * boundary_y)
                        )
                    else:
                        cohesion_x = (kappa * cohesion_gain) * cohesion_dir[0]
                        cohesion_y = (kappa * cohesion_gain) * cohesion_dir[1]
                        maneuver_x = (forward_gain * target_direction[0]) + (alpha_sep * separation_dir[0]) + (alpha_sep * boundary_x)
                        maneuver_y = (forward_gain * target_direction[1]) + (alpha_sep * separation_dir[1]) + (alpha_sep * boundary_y)
                        if has_target_axis:
                            dot_mt = (maneuver_x * t_hat_x) + (maneuver_y * t_hat_y)
                            m_parallel_x = dot_mt * t_hat_x
                            m_parallel_y = dot_mt * t_hat_y
                            m_tangent_x = maneuver_x - m_parallel_x
                            m_tangent_y = maneuver_y - m_parallel_y
                            maneuver_x = ((1.0 - mb) * m_parallel_x) + ((1.0 + mb) * m_tangent_x)
                            maneuver_y = ((1.0 - mb) * m_parallel_y) + ((1.0 + mb) * m_tangent_y)
                        if deep_pursuit_mode:
                            maneuver_x *= extension_gain
                            maneuver_y *= extension_gain
                        total_x = cohesion_x + maneuver_x
                        total_y = cohesion_y + maneuver_y
                total_norm = math.sqrt((total_x * total_x) + (total_y * total_y))
                if total_norm > 0.0:
                    total_direction = (total_x / total_norm, total_y / total_norm)
                else:
                    total_direction = (0.0, 0.0)

                movement_eps = 1e-12
                if total_norm > movement_eps:
                    orientation = Vec2(x=total_direction[0], y=total_direction[1])
                    velocity = Vec2(
                        x=total_direction[0] * unit.max_speed,
                        y=total_direction[1] * unit.max_speed,
                    )
                else:
                    orientation = unit.orientation_vector
                    velocity = Vec2(x=0.0, y=0.0)

                new_position = Vec2(
                    x=unit.position.x + (total_direction[0] * unit.max_speed * state.dt),
                    y=unit.position.y + (total_direction[1] * unit.max_speed * state.dt),
                )
                updated_units[unit_id] = replace(
                    unit,
                    position=new_position,
                    velocity=velocity,
                    orientation_vector=orientation,
                )

        if diag4_enabled or diag4_rpg_enabled:
            post_move_positions = {
                unit_id: (unit.position.x, unit.position.y)
                for unit_id, unit in updated_units.items()
                if unit.hit_points > 0.0
            }
        else:
            post_move_positions = {}

        fsr_enabled = bool(getattr(self, "FSR_ENABLED", False))
        fsr_strength_raw = float(getattr(self, "fsr_strength", 0.0))
        if fsr_strength_raw < 0.0:
            fsr_strength = 0.0
        elif fsr_strength_raw > 0.3:
            fsr_strength = 0.3
        else:
            fsr_strength = fsr_strength_raw

        # FSR block: one centroid + one lambda + one isotropic scale per fleet per tick.
        if fsr_enabled and fsr_strength > 0.0:
            delta_raw = float(getattr(self, "fsr_lambda_delta", 0.10))
            if delta_raw < 0.0:
                delta_lambda = 0.0
            elif delta_raw > 0.5:
                delta_lambda = 0.5
            else:
                delta_lambda = delta_raw
            fsr_eps = 1e-12

            fsr_reference = getattr(self, "_fsr_reference", None)
            if fsr_reference is None:
                fsr_reference = {}
                self._fsr_reference = fsr_reference

            fsr_tick_stats = {}
            for fleet_id, fleet in state.fleets.items():
                alive_unit_ids = [
                    unit_id
                    for unit_id in fleet.unit_ids
                    if unit_id in updated_units and updated_units[unit_id].hit_points > 0.0
                ]
                n_alive = len(alive_unit_ids)
                if n_alive == 0:
                    continue

                sum_x = 0.0
                sum_y = 0.0
                for unit_id in alive_unit_ids:
                    unit = updated_units[unit_id]
                    sum_x += unit.position.x
                    sum_y += unit.position.y
                centroid_x = sum_x / n_alive
                centroid_y = sum_y / n_alive

                radius_sq_sum = 0.0
                for unit_id in alive_unit_ids:
                    unit = updated_units[unit_id]
                    dx = unit.position.x - centroid_x
                    dy = unit.position.y - centroid_y
                    radius_sq_sum += (dx * dx) + (dy * dy)
                r_cur = math.sqrt(radius_sq_sum / n_alive)

                if fleet_id in fsr_reference:
                    n0, r_eq_n0 = fsr_reference[fleet_id]
                else:
                    n0 = n_alive
                    r_eq_n0 = r_cur
                    fsr_reference[fleet_id] = (n0, r_eq_n0)

                if n0 > 0 and r_eq_n0 > 0.0:
                    r_eq = r_eq_n0 * math.sqrt(n_alive / n0)
                    s_f = r_eq / (r_cur + fsr_eps)
                else:
                    r_eq = r_cur
                    s_f = 1.0

                kappa_f = fleet.parameters.normalized()["formation_rigidity"]
                k_f = fsr_strength * (0.5 + (0.5 * kappa_f))
                lambda_raw = 1.0 + (k_f * (s_f - 1.0))
                lambda_min = 1.0 - delta_lambda
                lambda_max = 1.0 + delta_lambda
                if lambda_raw < lambda_min:
                    lambda_f = lambda_min
                elif lambda_raw > lambda_max:
                    lambda_f = lambda_max
                else:
                    lambda_f = lambda_raw

                for unit_id in alive_unit_ids:
                    unit = updated_units[unit_id]
                    dx = unit.position.x - centroid_x
                    dy = unit.position.y - centroid_y
                    updated_units[unit_id] = replace(
                        unit,
                        position=Vec2(
                            x=centroid_x + (lambda_f * dx),
                            y=centroid_y + (lambda_f * dy),
                        ),
                    )

                fsr_tick_stats[fleet_id] = {
                    "n_alive": n_alive,
                    "n0": n0,
                    "r_cur": r_cur,
                    "r_eq": r_eq,
                    "s_f": s_f,
                    "k_f": k_f,
                    "lambda_raw": lambda_raw,
                    "lambda_f": lambda_f,
                }
            self.debug_last_fsr_stats = fsr_tick_stats

        if diag4_enabled or diag4_rpg_enabled:
            post_fsr_positions = {
                unit_id: (unit.position.x, unit.position.y)
                for unit_id, unit in updated_units.items()
                if unit.hit_points > 0.0
            }
        else:
            post_fsr_positions = {}

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
                if not seen_digit:
                    numeric_index = fleet_order + 1
                fleet_local_sorted.append((numeric_index, fleet_order, unit_id))
            fleet_local_sorted.sort(key=lambda x: (x[0], x[1]))
            for rank, (_, _, unit_id) in enumerate(fleet_local_sorted, start=1):
                rank_by_unit[unit_id] = rank
            global_alive_ids.extend(alive_ids)

        for i in range(len(global_alive_ids)):
            unit_i = global_alive_ids[i]
            pos_i = tentative_positions[unit_i]
            for j in range(i + 1, len(global_alive_ids)):
                unit_j = global_alive_ids[j]
                pos_j = tentative_positions[unit_j]
                dx = pos_i[0] - pos_j[0]
                dy = pos_i[1] - pos_j[1]
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
                updated_units[unit_id] = replace(unit, position=Vec2(x=base_x + dx_proj, y=base_y + dy_proj))

        # Optional hard boundary: clamp units into map domain [0, arena_size].
        if bool(getattr(self, "BOUNDARY_HARD_ENABLED", False)):
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

        if diag4_enabled or diag4_rpg_enabled:
            final_positions = {
                unit_id: (unit.position.x, unit.position.y)
                for unit_id, unit in updated_units.items()
                if unit.hit_points > 0.0
            }
        else:
            final_positions = {}

        if diag_enabled:
            projection_displacement_sum = 0.0
            projection_displacement_max = 0.0
            projection_displacement_count = 0
            for unit_id in tentative_positions:
                dx_proj, dy_proj = delta_position[unit_id]
                displacement = math.sqrt((dx_proj * dx_proj) + (dy_proj * dy_proj))
                projection_displacement_sum += displacement
                projection_displacement_count += 1
                if displacement > projection_displacement_max:
                    projection_displacement_max = displacement
            if projection_displacement_count > 0:
                projection_displacement_mean = projection_displacement_sum / projection_displacement_count
            else:
                projection_displacement_mean = 0.0
            diag4_payload = None

            eta_raw = float(getattr(self, "debug_outlier_eta", 1.8))
            if eta_raw < 1.5:
                outlier_eta = 1.5
            elif eta_raw > 2.2:
                outlier_eta = 2.2
            else:
                outlier_eta = eta_raw

            persistence_ticks_raw = int(getattr(self, "debug_outlier_persistence_ticks", 20))
            if persistence_ticks_raw < 1:
                persistence_ticks = 1
            else:
                persistence_ticks = persistence_ticks_raw

            outlier_streaks = getattr(self, "_debug_outlier_streaks", None)
            if outlier_streaks is None:
                outlier_streaks = {}
                self._debug_outlier_streaks = outlier_streaks

            outlier_stats = {}
            persistent_outlier_units = []
            max_outlier_persistence = 0
            for fleet_id, fleet in state.fleets.items():
                alive_unit_ids = [
                    unit_id
                    for unit_id in fleet.unit_ids
                    if unit_id in updated_units and updated_units[unit_id].hit_points > 0.0
                ]
                if not alive_unit_ids:
                    outlier_streaks[fleet_id] = {}
                    outlier_stats[fleet_id] = {
                        "outlier_count": 0,
                        "max_outlier_persistence": 0,
                        "persistent_outlier_unit_ids": [],
                        "centroid_x": 0.0,
                        "centroid_y": 0.0,
                        "r_rms": 0.0,
                        "outlier_threshold": 0.0,
                    }
                    continue

                centroid_x = sum(updated_units[unit_id].position.x for unit_id in alive_unit_ids) / len(alive_unit_ids)
                centroid_y = sum(updated_units[unit_id].position.y for unit_id in alive_unit_ids) / len(alive_unit_ids)
                radius_sq_sum = 0.0
                for unit_id in alive_unit_ids:
                    unit = updated_units[unit_id]
                    dx = unit.position.x - centroid_x
                    dy = unit.position.y - centroid_y
                    radius_sq_sum += (dx * dx) + (dy * dy)
                r_rms = math.sqrt(radius_sq_sum / len(alive_unit_ids))
                outlier_threshold = outlier_eta * r_rms

                current_outliers = []
                for unit_id in alive_unit_ids:
                    unit = updated_units[unit_id]
                    dx = unit.position.x - centroid_x
                    dy = unit.position.y - centroid_y
                    if math.sqrt((dx * dx) + (dy * dy)) > outlier_threshold:
                        current_outliers.append(unit_id)

                prev_streaks = outlier_streaks.get(fleet_id, {})
                next_streaks = {}
                for unit_id in current_outliers:
                    next_streaks[unit_id] = prev_streaks.get(unit_id, 0) + 1
                outlier_streaks[fleet_id] = next_streaks

                fleet_max_persistence = 0
                for value in next_streaks.values():
                    if value > fleet_max_persistence:
                        fleet_max_persistence = value
                if fleet_max_persistence > max_outlier_persistence:
                    max_outlier_persistence = fleet_max_persistence

                persistent_ids = sorted(
                    unit_id
                    for unit_id, streak in next_streaks.items()
                    if streak >= persistence_ticks
                )
                persistent_outlier_units.extend(persistent_ids)

                outlier_stats[fleet_id] = {
                    "outlier_count": len(current_outliers),
                    "max_outlier_persistence": fleet_max_persistence,
                    "persistent_outlier_unit_ids": persistent_ids,
                    "centroid_x": centroid_x,
                    "centroid_y": centroid_y,
                    "r_rms": r_rms,
                    "outlier_threshold": outlier_threshold,
                }

            if diag4_enabled or diag4_rpg_enabled:
                top_k_raw = int(getattr(self, "debug_diag4_topk", 10))
                if diag4_legacy_enabled:
                    if top_k_raw < 1:
                        top_k = 1
                    elif top_k_raw > 50:
                        top_k = 50
                    else:
                        top_k = top_k_raw
                else:
                    top_k = 0

                sector_deg_raw = float(getattr(self, "debug_diag4_return_sector_deg", 30.0))
                if diag4_legacy_enabled:
                    if sector_deg_raw < 5.0:
                        sector_deg = 5.0
                    elif sector_deg_raw > 85.0:
                        sector_deg = 85.0
                    else:
                        sector_deg = sector_deg_raw
                else:
                    sector_deg = 30.0
                sector_cos = math.cos(math.radians(sector_deg))

                neighbor_k_raw = int(getattr(self, "debug_diag4_neighbor_k", 3))
                if diag4_legacy_enabled:
                    if neighbor_k_raw < 1:
                        neighbor_k = 1
                    elif neighbor_k_raw > 10:
                        neighbor_k = 10
                    else:
                        neighbor_k = neighbor_k_raw
                else:
                    neighbor_k = 3

                rpg_window_raw = int(getattr(self, "debug_diag4_rpg_window", 20))
                if rpg_window_raw < 5:
                    rpg_window = 5
                elif rpg_window_raw > 200:
                    rpg_window = 200
                else:
                    rpg_window = rpg_window_raw
                rpg_eps = 1e-12
                rpg_delta = 0.1 * min_unit_spacing

                rpg_outlier_entry = getattr(self, "_debug_diag4_rpg_outlier_entry", None)
                if rpg_outlier_entry is None:
                    rpg_outlier_entry = {}
                    self._debug_diag4_rpg_outlier_entry = rpg_outlier_entry

                rpg_return_stats = getattr(self, "_debug_diag4_rpg_return_stats", None)
                if not isinstance(rpg_return_stats, dict):
                    rpg_return_stats = {}
                if not isinstance(rpg_return_stats.get("overall"), dict):
                    rpg_return_stats["overall"] = {"success": 0, "fail": 0}
                if not isinstance(rpg_return_stats.get("by_fleet"), dict):
                    rpg_return_stats["by_fleet"] = {}
                if not isinstance(rpg_return_stats.get("by_class"), dict):
                    rpg_return_stats["by_class"] = {}
                for _cls in (
                    "inward_intent",
                    "outward_bias",
                    "tangential_neutral",
                    "suppressed_inward",
                ):
                    if not isinstance(rpg_return_stats["by_class"].get(_cls), dict):
                        rpg_return_stats["by_class"][_cls] = {"success": 0, "fail": 0}
                self._debug_diag4_rpg_return_stats = rpg_return_stats

                tau = 0.0
                if diag4_rpg_enabled:
                    free_speed_samples = []
                    for unit_id, (final_x, final_y) in final_positions.items():
                        start_x, start_y = snapshot_positions.get(unit_id, (final_x, final_y))
                        fsr_x, fsr_y = post_fsr_positions.get(unit_id, (start_x, start_y))
                        dx_free = fsr_x - start_x
                        dy_free = fsr_y - start_y
                        free_speed_samples.append(math.sqrt((dx_free * dx_free) + (dy_free * dy_free)))
                    if free_speed_samples:
                        tau = 0.05 * _quantile(sorted(free_speed_samples), 0.50)

                prev_unit_state = getattr(self, "_debug_diag4_prev_unit_state", None)
                if prev_unit_state is None:
                    prev_unit_state = {}
                    self._debug_diag4_prev_unit_state = prev_unit_state

                prev_unit_radius = getattr(self, "_debug_diag4_prev_unit_radius", None)
                if prev_unit_radius is None:
                    prev_unit_radius = {}
                    self._debug_diag4_prev_unit_radius = prev_unit_radius

                transition_counts = getattr(self, "_debug_diag4_transition_counts", None)
                if transition_counts is None:
                    transition_counts = {}
                    self._debug_diag4_transition_counts = transition_counts

                first_outlier_tick = getattr(self, "_debug_diag4_first_outlier_tick", None)
                if first_outlier_tick is None:
                    first_outlier_tick = {}
                    self._debug_diag4_first_outlier_tick = first_outlier_tick

                return_attempt_count = getattr(self, "_debug_diag4_return_attempt_count", None)
                if return_attempt_count is None:
                    return_attempt_count = {}
                    self._debug_diag4_return_attempt_count = return_attempt_count

                outlier_return_count = getattr(self, "_debug_diag4_outlier_return_count", None)
                if outlier_return_count is None:
                    outlier_return_count = {}
                    self._debug_diag4_outlier_return_count = outlier_return_count

                outlier_duration = getattr(self, "_debug_diag4_outlier_duration", None)
                if outlier_duration is None:
                    outlier_duration = {}
                    self._debug_diag4_outlier_duration = outlier_duration

                max_outlier_duration = getattr(self, "_debug_diag4_max_outlier_duration", None)
                if max_outlier_duration is None:
                    max_outlier_duration = {}
                    self._debug_diag4_max_outlier_duration = max_outlier_duration

                disp_history = getattr(self, "_debug_diag4_disp_history", None)
                if disp_history is None:
                    disp_history = {}
                    self._debug_diag4_disp_history = disp_history

                persistent_records = getattr(self, "_debug_diag4_persistent_records", None)
                if persistent_records is None:
                    persistent_records = {}
                    self._debug_diag4_persistent_records = persistent_records

                diag4_outlier_streaks = getattr(self, "_debug_diag4_outlier_streaks", None)
                if diag4_outlier_streaks is None:
                    diag4_outlier_streaks = {}
                    self._debug_diag4_outlier_streaks = diag4_outlier_streaks

                # Module C: per-tick displacement decomposition (movement / fsr / projection).
                for unit_id, (final_x, final_y) in final_positions.items():
                    start_x, start_y = snapshot_positions.get(unit_id, (final_x, final_y))
                    move_x, move_y = post_move_positions.get(unit_id, (start_x, start_y))
                    fsr_x, fsr_y = post_fsr_positions.get(unit_id, (move_x, move_y))
                    proj_x = final_x
                    proj_y = final_y

                    dx_move = move_x - start_x
                    dy_move = move_y - start_y
                    dx_fsr = fsr_x - move_x
                    dy_fsr = fsr_y - move_y
                    dx_proj = proj_x - fsr_x
                    dy_proj = proj_y - fsr_y
                    dx_total = proj_x - start_x
                    dy_total = proj_y - start_y

                    history = disp_history.get(unit_id, [])
                    history.append(
                        (
                            state.tick,
                            math.sqrt((dx_move * dx_move) + (dy_move * dy_move)),
                            math.sqrt((dx_fsr * dx_fsr) + (dy_fsr * dy_fsr)),
                            math.sqrt((dx_proj * dx_proj) + (dy_proj * dy_proj)),
                            math.sqrt((dx_total * dx_total) + (dy_total * dy_total)),
                        )
                    )
                    if len(history) > 96:
                        history = history[-96:]
                    disp_history[unit_id] = history

                module_a_topk = {}
                module_b_fleet = {}
                module_d_persistent = []
                persistent_diag4_units = []
                module_rpg_payload = None
                module_rpg_fleet = {}
                rpg_kappa_all = []
                rpg_gap_all = []
                rpg_gap_zero_like_count = 0
                rpg_gap_no_inward_neighbor_count = 0

                for fleet_id, fleet in state.fleets.items():
                    alive_unit_ids = [
                        unit_id
                        for unit_id in fleet.unit_ids
                        if unit_id in final_positions
                    ]
                    if not alive_unit_ids:
                        diag4_outlier_streaks[fleet_id] = {}
                        module_a_topk[fleet_id] = []
                        module_b_fleet[fleet_id] = {
                            "core_count": 0,
                            "shell_count": 0,
                            "outlier_count": 0,
                            "r_rms": 0.0,
                            "r_p50": 0.0,
                            "r_p90": 0.0,
                            "outlier_threshold": 0.0,
                            "margin": min_unit_spacing,
                        }
                        if diag4_rpg_enabled:
                            module_rpg_fleet[fleet_id] = {
                                "r_shell": 0.0,
                                "delta": rpg_delta,
                                "outlier_threshold": rpg_delta,
                                "outlier_count": 0,
                                "projection_suppression_candidate_count": 0,
                                "movement_outward_bias_count": 0,
                                "inward_free_and_effective_count": 0,
                                "kappa_distribution": _dist_summary([]),
                                "g_distribution": _dist_summary([]),
                                "g_zero_like_ratio": 0.0,
                                "no_inward_neighbor_ratio": 0.0,
                            }
                        continue

                    cx = sum(final_positions[unit_id][0] for unit_id in alive_unit_ids) / len(alive_unit_ids)
                    cy = sum(final_positions[unit_id][1] for unit_id in alive_unit_ids) / len(alive_unit_ids)

                    radius_by_unit = {}
                    radii = []
                    for unit_id in alive_unit_ids:
                        ux, uy = final_positions[unit_id]
                        dx = ux - cx
                        dy = uy - cy
                        radius = math.sqrt((dx * dx) + (dy * dy))
                        radius_by_unit[unit_id] = radius
                        radii.append(radius)

                    radii_sorted = sorted(radii)
                    r_p50 = _quantile(radii_sorted, 0.50)
                    r_p90 = _quantile(radii_sorted, 0.90)
                    r_rms = math.sqrt(sum(r * r for r in radii) / len(radii))
                    outlier_threshold_diag4 = max(r_p90 + min_unit_spacing, outlier_eta * r_rms)

                    current_states = {}
                    current_outliers = []
                    core_count = 0
                    shell_count = 0
                    outlier_count = 0
                    transitions = transition_counts.get(fleet_id, {})
                    if not isinstance(transitions, dict):
                        transitions = {}
                    for unit_id in alive_unit_ids:
                        radius = radius_by_unit[unit_id]
                        if radius <= r_p50:
                            state_class = "CORE"
                            core_count += 1
                        elif radius > outlier_threshold_diag4:
                            state_class = "OUTLIER"
                            outlier_count += 1
                            current_outliers.append(unit_id)
                        else:
                            state_class = "SHELL"
                            shell_count += 1
                        current_states[unit_id] = state_class

                        prev_state = prev_unit_state.get(unit_id)
                        if prev_state is not None and prev_state != state_class:
                            key = f"{prev_state}->{state_class}"
                            transitions[key] = transitions.get(key, 0) + 1

                        prev_radius = prev_unit_radius.get(unit_id, radius)
                        if prev_state == "OUTLIER" and state_class == "OUTLIER" and radius < (prev_radius - 1e-9):
                            return_attempt_count[unit_id] = return_attempt_count.get(unit_id, 0) + 1
                        if prev_state == "OUTLIER" and state_class == "SHELL":
                            outlier_return_count[unit_id] = outlier_return_count.get(unit_id, 0) + 1

                        prev_duration = outlier_duration.get(unit_id, 0)
                        if state_class == "OUTLIER":
                            next_duration = prev_duration + 1
                            outlier_duration[unit_id] = next_duration
                            if next_duration > max_outlier_duration.get(unit_id, 0):
                                max_outlier_duration[unit_id] = next_duration
                            if unit_id not in first_outlier_tick:
                                first_outlier_tick[unit_id] = state.tick
                        else:
                            outlier_duration[unit_id] = 0
                            if unit_id not in max_outlier_duration:
                                max_outlier_duration[unit_id] = max_outlier_duration.get(unit_id, 0)

                        prev_unit_state[unit_id] = state_class
                        prev_unit_radius[unit_id] = radius

                    transition_counts[fleet_id] = transitions

                    prev_streaks = diag4_outlier_streaks.get(fleet_id, {})
                    next_streaks = {}
                    for unit_id in current_outliers:
                        next_streaks[unit_id] = prev_streaks.get(unit_id, 0) + 1
                    diag4_outlier_streaks[fleet_id] = next_streaks

                    persistent_ids = sorted(
                        unit_id
                        for unit_id, streak in next_streaks.items()
                        if streak >= persistence_ticks
                    )
                    persistent_diag4_units.extend(persistent_ids)

                    if diag4_legacy_enabled:
                        # Module A: top-K candidate outliers and neighborhood/contact opportunity.
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
                                    "state": current_states.get(unit_id, "SHELL"),
                                    "radius": radius_by_unit.get(unit_id, 0.0),
                                    "neighbor_count_sep": neighbor_sep,
                                    "neighbor_count_contact": neighbor_contact,
                                    "rolling_in_contact_ratio": 0.0,
                                }
                            )
                        module_a_topk[fleet_id] = candidates
                    else:
                        module_a_topk[fleet_id] = []

                    module_b_fleet[fleet_id] = {
                        "core_count": core_count,
                        "shell_count": shell_count,
                        "outlier_count": outlier_count,
                        "r_rms": r_rms,
                        "r_p50": r_p50,
                        "r_p90": r_p90,
                        "outlier_threshold": outlier_threshold_diag4,
                        "margin": min_unit_spacing,
                        "first_outlier_tick": min(
                            (first_outlier_tick.get(unit_id, state.tick) for unit_id in current_outliers),
                            default=None,
                        ),
                        "persistent_outlier_unit_ids": persistent_ids,
                    }

                    if diag4_rpg_enabled:
                        overall_stats = rpg_return_stats.get("overall", {})
                        if not isinstance(overall_stats, dict):
                            overall_stats = {"success": 0, "fail": 0}
                            rpg_return_stats["overall"] = overall_stats
                        fleet_stats = rpg_return_stats["by_fleet"].get(fleet_id)
                        if not isinstance(fleet_stats, dict):
                            fleet_stats = {"success": 0, "fail": 0}
                            rpg_return_stats["by_fleet"][fleet_id] = fleet_stats
                        class_stats_map = rpg_return_stats.get("by_class", {})

                        snapshot_cx = (
                            sum(snapshot_positions.get(unit_id, final_positions[unit_id])[0] for unit_id in alive_unit_ids)
                            / len(alive_unit_ids)
                        )
                        snapshot_cy = (
                            sum(snapshot_positions.get(unit_id, final_positions[unit_id])[1] for unit_id in alive_unit_ids)
                            / len(alive_unit_ids)
                        )

                        rpg_outlier_count = 0
                        rpg_projection_suppression_count = 0
                        rpg_outward_bias_count = 0
                        rpg_inward_effective_count = 0
                        rpg_tangential_count = 0
                        rpg_suppressed_count = 0
                        rpg_kappa_values = []
                        rpg_gap_values = []
                        rpg_gap_zero_like_fleet = 0
                        rpg_gap_no_inward_fleet = 0
                        rpg_gap_probe_units = []
                        rpg_gap_sample_cap = 0
                        rpg_outlier_threshold = r_rms + rpg_delta

                        for unit_id in alive_unit_ids:
                            final_x, final_y = final_positions[unit_id]
                            radius = radius_by_unit.get(unit_id, 0.0)
                            is_rpg_outlier = radius > rpg_outlier_threshold
                            entry = rpg_outlier_entry.get(unit_id)

                            if not is_rpg_outlier:
                                if isinstance(entry, dict):
                                    entry_tick = int(entry.get("tick", state.tick))
                                    entry_class = str(entry.get("class", "tangential_neutral"))
                                    entry_class_stats = class_stats_map.get(entry_class, {"success": 0, "fail": 0})
                                    if (state.tick - entry_tick) <= rpg_window:
                                        overall_stats["success"] = int(overall_stats.get("success", 0)) + 1
                                        fleet_stats["success"] = int(fleet_stats.get("success", 0)) + 1
                                        entry_class_stats["success"] = int(entry_class_stats.get("success", 0)) + 1
                                    else:
                                        overall_stats["fail"] = int(overall_stats.get("fail", 0)) + 1
                                        fleet_stats["fail"] = int(fleet_stats.get("fail", 0)) + 1
                                        entry_class_stats["fail"] = int(entry_class_stats.get("fail", 0)) + 1
                                    class_stats_map[entry_class] = entry_class_stats
                                    del rpg_outlier_entry[unit_id]
                                continue

                            start_x, start_y = snapshot_positions.get(unit_id, (final_x, final_y))
                            fsr_x, fsr_y = post_fsr_positions.get(unit_id, (start_x, start_y))

                            dir_x = snapshot_cx - start_x
                            dir_y = snapshot_cy - start_y
                            dir_norm = math.sqrt((dir_x * dir_x) + (dir_y * dir_y))
                            if dir_norm <= rpg_eps:
                                dir_x = cx - final_x
                                dir_y = cy - final_y
                                dir_norm = math.sqrt((dir_x * dir_x) + (dir_y * dir_y))
                            if dir_norm > rpg_eps:
                                d_hat_x = dir_x / dir_norm
                                d_hat_y = dir_y / dir_norm
                            else:
                                d_hat_x = 0.0
                                d_hat_y = 0.0

                            v_tilde_x = fsr_x - start_x
                            v_tilde_y = fsr_y - start_y
                            v_x = final_x - start_x
                            v_y = final_y - start_y
                            v_tilde_r = (v_tilde_x * d_hat_x) + (v_tilde_y * d_hat_y)
                            v_r = (v_x * d_hat_x) + (v_y * d_hat_y)
                            if v_tilde_r > tau and v_r <= tau:
                                current_class = "suppressed_inward"
                            elif v_tilde_r > tau:
                                current_class = "inward_intent"
                            elif v_tilde_r < -tau:
                                current_class = "outward_bias"
                            else:
                                current_class = "tangential_neutral"

                            if not isinstance(entry, dict):
                                rpg_outlier_entry[unit_id] = {
                                    "tick": state.tick,
                                    "fleet_id": fleet_id,
                                    "class": current_class,
                                }
                            else:
                                entry_tick = int(entry.get("tick", state.tick))
                                entry_class = str(entry.get("class", "tangential_neutral"))
                                entry_class_stats = class_stats_map.get(entry_class, {"success": 0, "fail": 0})
                                if (state.tick - entry_tick) >= rpg_window:
                                    overall_stats["fail"] = int(overall_stats.get("fail", 0)) + 1
                                    fleet_stats["fail"] = int(fleet_stats.get("fail", 0)) + 1
                                    entry_class_stats["fail"] = int(entry_class_stats.get("fail", 0)) + 1
                                    class_stats_map[entry_class] = entry_class_stats
                                    rpg_outlier_entry[unit_id] = {
                                        "tick": state.tick,
                                        "fleet_id": fleet_id,
                                        "class": current_class,
                                    }

                            rpg_outlier_count += 1
                            if current_class == "suppressed_inward":
                                rpg_projection_suppression_count += 1
                                rpg_suppressed_count += 1
                            elif current_class == "outward_bias":
                                rpg_outward_bias_count += 1
                            elif current_class == "tangential_neutral":
                                rpg_tangential_count += 1
                            else:
                                rpg_inward_effective_count += 1

                            if abs(v_tilde_r) > rpg_eps and current_class != "tangential_neutral":
                                kappa_i = v_r / (v_tilde_r + rpg_eps)
                                rpg_kappa_values.append(kappa_i)

                            rpg_gap_probe_units.append(
                                (
                                    unit_id,
                                    final_x,
                                    final_y,
                                    d_hat_x,
                                    d_hat_y,
                                    radius,
                                )
                            )

                        if rpg_gap_probe_units:
                            rpg_gap_sample_cap = top_k_raw // 3
                            if rpg_gap_sample_cap < 1:
                                rpg_gap_sample_cap = 1
                            elif rpg_gap_sample_cap > 8:
                                rpg_gap_sample_cap = 8
                            # Deterministic probe set: farthest outliers first.
                            probe_units = sorted(
                                rpg_gap_probe_units,
                                key=lambda row: row[5],
                                reverse=True,
                            )[:rpg_gap_sample_cap]
                            for unit_id, final_x, final_y, d_hat_x, d_hat_y, _radius in probe_units:
                                gap_candidates = []
                                for ally_id in alive_unit_ids:
                                    if ally_id == unit_id:
                                        continue
                                    ax, ay = final_positions[ally_id]
                                    proj = ((ax - final_x) * d_hat_x) + ((ay - final_y) * d_hat_y)
                                    if proj > 0.0:
                                        gap_candidates.append(proj)
                                if gap_candidates:
                                    g_i = min(gap_candidates)
                                    rpg_gap_values.append(g_i)
                                    if g_i <= rpg_eps:
                                        rpg_gap_zero_like_fleet += 1
                                else:
                                    rpg_gap_no_inward_fleet += 1

                        if rpg_outlier_count > 0:
                            g_zero_like_ratio = rpg_gap_zero_like_fleet / max(1, len(rpg_gap_values))
                            no_inward_neighbor_ratio = rpg_gap_no_inward_fleet / rpg_outlier_count
                        else:
                            g_zero_like_ratio = 0.0
                            no_inward_neighbor_ratio = 0.0

                        module_rpg_fleet[fleet_id] = {
                            "r_shell": r_rms,
                            "delta": rpg_delta,
                            "tau": tau,
                            "outlier_threshold": rpg_outlier_threshold,
                            "outlier_count": rpg_outlier_count,
                            "projection_suppression_candidate_count": rpg_projection_suppression_count,
                            "movement_outward_bias_count": rpg_outward_bias_count,
                            "tangential_neutral_count": rpg_tangential_count,
                            "inward_free_and_effective_count": rpg_inward_effective_count,
                            "suppressed_inward_count": rpg_suppressed_count,
                            "outward_ratio": (rpg_outward_bias_count / rpg_outlier_count) if rpg_outlier_count > 0 else 0.0,
                            "tangential_ratio": (rpg_tangential_count / rpg_outlier_count) if rpg_outlier_count > 0 else 0.0,
                            "suppressed_ratio": (rpg_suppressed_count / rpg_outlier_count) if rpg_outlier_count > 0 else 0.0,
                            "g_probe_cap": rpg_gap_sample_cap,
                            "g_probe_count": len(rpg_gap_values) + rpg_gap_no_inward_fleet,
                            "kappa_distribution": _dist_summary(rpg_kappa_values),
                            "g_distribution": _dist_summary(rpg_gap_values),
                            "g_zero_like_ratio": g_zero_like_ratio,
                            "no_inward_neighbor_ratio": no_inward_neighbor_ratio,
                        }
                        rpg_kappa_all.extend(rpg_kappa_values)
                        rpg_gap_all.extend(rpg_gap_values)
                        rpg_gap_zero_like_count += rpg_gap_zero_like_fleet
                        rpg_gap_no_inward_neighbor_count += rpg_gap_no_inward_fleet

                    if diag4_legacy_enabled:
                        # Module D: re-entry obstruction for persistent outliers.
                        for unit_id in persistent_ids:
                            ux, uy = final_positions[unit_id]
                            dx_c = cx - ux
                            dy_c = cy - uy
                            norm_c = math.sqrt((dx_c * dx_c) + (dy_c * dy_c))
                            if norm_c > 0.0:
                                rx = dx_c / norm_c
                                ry = dy_c / norm_c
                            else:
                                rx = 0.0
                                ry = 0.0
                            radius_u = radius_by_unit.get(unit_id, 0.0)

                            sector_count = 0
                            sector_distances = []
                            inner_neighbors = 0
                            outer_neighbors = 0
                            for ally_id in alive_unit_ids:
                                if ally_id == unit_id:
                                    continue
                                ax, ay = final_positions[ally_id]
                                vx = ax - ux
                                vy = ay - uy
                                dist_sq = (vx * vx) + (vy * vy)
                                if dist_sq <= 0.0:
                                    continue
                                dist = math.sqrt(dist_sq)
                                dot = (vx * rx) + (vy * ry)
                                if dot > 0.0:
                                    cosang = dot / dist
                                    if cosang >= sector_cos:
                                        sector_count += 1
                                        sector_distances.append(dist)

                                radius_ally = radius_by_unit.get(ally_id, 0.0)
                                if (radius_u - self.attack_range) <= radius_ally < radius_u:
                                    inner_neighbors += 1
                                elif radius_u < radius_ally <= (radius_u + self.attack_range):
                                    outer_neighbors += 1

                            sector_distances.sort()
                            nearest_k = sector_distances[:neighbor_k]
                            if nearest_k:
                                nearest_k_mean = sum(nearest_k) / len(nearest_k)
                            else:
                                nearest_k_mean = 0.0

                            denom = inner_neighbors + outer_neighbors
                            if denom > 0:
                                radial_density_gradient = (inner_neighbors - outer_neighbors) / denom
                            else:
                                radial_density_gradient = 0.0

                            module_d_persistent.append(
                                {
                                    "fleet_id": fleet_id,
                                    "unit_id": unit_id,
                                    "sector_neighbor_count": sector_count,
                                    "nearest_k_distance_return_dir": nearest_k_mean,
                                    "radial_density_gradient": radial_density_gradient,
                                    "inner_neighbor_count": inner_neighbors,
                                    "outer_neighbor_count": outer_neighbors,
                                    "return_attempt_count": return_attempt_count.get(unit_id, 0),
                                    "consecutive_outlier_duration": outlier_duration.get(unit_id, 0),
                                    "max_outlier_duration": max_outlier_duration.get(unit_id, 0),
                                    "rolling_in_contact_ratio": 0.0,
                                }
                            )

                if diag4_rpg_enabled:
                    alive_final_ids = set(final_positions.keys())
                    for unit_id in list(rpg_outlier_entry.keys()):
                        if unit_id not in alive_final_ids:
                            del rpg_outlier_entry[unit_id]

                    total_rpg_outliers = 0
                    total_rpg_projection_suppression = 0
                    total_rpg_outward_bias = 0
                    total_rpg_inward_effective = 0
                    total_rpg_tangential = 0
                    total_rpg_suppressed = 0
                    by_fleet_return = {}
                    for fleet_id, fleet_payload in module_rpg_fleet.items():
                        total_rpg_outliers += int(fleet_payload.get("outlier_count", 0))
                        total_rpg_projection_suppression += int(
                            fleet_payload.get("projection_suppression_candidate_count", 0)
                        )
                        total_rpg_outward_bias += int(fleet_payload.get("movement_outward_bias_count", 0))
                        total_rpg_tangential += int(fleet_payload.get("tangential_neutral_count", 0))
                        total_rpg_inward_effective += int(
                            fleet_payload.get("inward_free_and_effective_count", 0)
                        )
                        total_rpg_suppressed += int(fleet_payload.get("suppressed_inward_count", 0))
                        fleet_stats = rpg_return_stats["by_fleet"].get(fleet_id, {})
                        fleet_success = int(fleet_stats.get("success", 0))
                        fleet_fail = int(fleet_stats.get("fail", 0))
                        fleet_eval = fleet_success + fleet_fail
                        fleet_payload["p_return_window"] = {
                            "window": rpg_window,
                            "success_events": fleet_success,
                            "fail_events": fleet_fail,
                            "evaluated_events": fleet_eval,
                            "p_return": (fleet_success / fleet_eval) if fleet_eval > 0 else 0.0,
                        }
                        by_fleet_return[fleet_id] = fleet_payload["p_return_window"]

                    overall_stats = rpg_return_stats.get("overall", {})
                    overall_success = int(overall_stats.get("success", 0))
                    overall_fail = int(overall_stats.get("fail", 0))
                    overall_eval = overall_success + overall_fail
                    by_class_return = {}
                    class_stats_map = rpg_return_stats.get("by_class", {})
                    if isinstance(class_stats_map, dict):
                        for cls_name, cls_stats in class_stats_map.items():
                            if not isinstance(cls_stats, dict):
                                continue
                            cls_success = int(cls_stats.get("success", 0))
                            cls_fail = int(cls_stats.get("fail", 0))
                            cls_eval = cls_success + cls_fail
                            by_class_return[cls_name] = {
                                "success_events": cls_success,
                                "fail_events": cls_fail,
                                "evaluated_events": cls_eval,
                                "p_return": (cls_success / cls_eval) if cls_eval > 0 else 0.0,
                            }
                    g_zero_like_ratio_global = (
                        rpg_gap_zero_like_count / len(rpg_gap_all)
                        if rpg_gap_all
                        else 0.0
                    )
                    no_inward_neighbor_ratio_global = (
                        rpg_gap_no_inward_neighbor_count / total_rpg_outliers
                        if total_rpg_outliers > 0
                        else 0.0
                    )

                    module_rpg_payload = {
                        "canonical": {
                            "radial_direction": "d_hat=(C_f-x_i)/||C_f-x_i|| (inward)",
                            "inward_definition": "v_tilde_r_i > 0",
                            "r_shell_definition": "R_shell=R_rms",
                        },
                        "constants": {
                            "epsilon": rpg_eps,
                            "delta": rpg_delta,
                            "tau": tau,
                            "p_return_window": rpg_window,
                        },
                        "separation_counts": {
                            "projection_suppression_candidate_count": total_rpg_projection_suppression,
                            "movement_outward_bias_count": total_rpg_outward_bias,
                            "tangential_neutral_count": total_rpg_tangential,
                            "inward_free_and_effective_count": total_rpg_inward_effective,
                            "suppressed_inward_count": total_rpg_suppressed,
                            "rpg_outlier_count": total_rpg_outliers,
                        },
                        "category_ratios": {
                            "outward_ratio": (total_rpg_outward_bias / total_rpg_outliers) if total_rpg_outliers > 0 else 0.0,
                            "tangential_ratio": (total_rpg_tangential / total_rpg_outliers) if total_rpg_outliers > 0 else 0.0,
                            "suppressed_ratio": (total_rpg_suppressed / total_rpg_outliers) if total_rpg_outliers > 0 else 0.0,
                        },
                        "kappa_distribution": _dist_summary(rpg_kappa_all),
                        "g_distribution": _dist_summary(rpg_gap_all),
                        "g_zero_like_ratio": g_zero_like_ratio_global,
                        "no_inward_neighbor_ratio": no_inward_neighbor_ratio_global,
                        "p_return": {
                            "window": rpg_window,
                            "overall": {
                                "success_events": overall_success,
                                "fail_events": overall_fail,
                                "evaluated_events": overall_eval,
                                "p_return": (overall_success / overall_eval) if overall_eval > 0 else 0.0,
                            },
                            "by_fleet": by_fleet_return,
                            "by_class": by_class_return,
                        },
                        "fleet_stats": module_rpg_fleet,
                    }

                module_c_records = []
                if diag4_legacy_enabled:
                    # Module C window attribution for persistent outlier emergence.
                    for unit_id in sorted(set(persistent_diag4_units)):
                        if unit_id in persistent_records:
                            continue
                        emergence_tick = first_outlier_tick.get(unit_id, state.tick)
                        history = disp_history.get(unit_id, [])
                        window_start = emergence_tick - 3
                        window_end = emergence_tick + 3
                        window = [
                            sample
                            for sample in history
                            if window_start <= sample[0] <= window_end
                        ]
                        cum_move = sum(sample[1] for sample in window)
                        cum_fsr = sum(sample[2] for sample in window)
                        cum_proj = sum(sample[3] for sample in window)
                        total = cum_move + cum_fsr + cum_proj
                        dominant = "move"
                        dominant_val = cum_move
                        if cum_fsr > dominant_val:
                            dominant = "fsr"
                            dominant_val = cum_fsr
                        if cum_proj > dominant_val:
                            dominant = "projection"
                        persistent_records[unit_id] = {
                            "unit_id": unit_id,
                            "emergence_tick": emergence_tick,
                            "window_start_tick": window_start,
                            "window_end_tick": window_end,
                            "window_samples": len(window),
                            "cum_delta_move_norm": cum_move,
                            "cum_delta_fsr_norm": cum_fsr,
                            "cum_delta_projection_norm": cum_proj,
                            "cum_delta_total_norm": total,
                            "dominant_component": dominant,
                            "delta_separation_component_available": False,
                        }

                    for unit_id in sorted(set(persistent_diag4_units)):
                        record = persistent_records.get(unit_id)
                        if isinstance(record, dict):
                            module_c_records.append(record)

                diag4_payload = {
                    "module_a": {
                        "top_k": top_k,
                        "neighbor_radius_sep": r_sep,
                        "neighbor_radius_contact": self.attack_range,
                        "topk_candidates": module_a_topk,
                    },
                    "module_b": {
                        "state_def": {
                            "core": "r <= R_p50",
                            "shell": "R_p50 < r <= max(R_p90 + margin, eta*R_rms)",
                            "outlier": "r > max(R_p90 + margin, eta*R_rms)",
                        },
                        "margin": min_unit_spacing,
                        "eta": outlier_eta,
                        "fleet_state_stats": module_b_fleet,
                        "transition_counts_cumulative": transition_counts,
                        "return_attempt_count": return_attempt_count,
                        "outlier_return_count": outlier_return_count,
                    },
                    "module_c": {
                        "displacement_note": "delta_move/fsr/projection are directly measured from stage boundaries in the single-pass pipeline.",
                        "separation_component_available": False,
                        "persistent_emergence_records": module_c_records,
                    },
                    "module_d": {
                        "return_sector_deg": sector_deg,
                        "nearest_k": neighbor_k,
                        "persistent_reentry": module_d_persistent,
                    },
                }
                if module_rpg_payload is not None:
                    diag4_payload["module_rpg"] = module_rpg_payload

            self._debug_diag_pending = {
                "tick": state.tick,
                "projection": {
                    "max_projection_displacement": projection_displacement_max,
                    "mean_projection_displacement": projection_displacement_mean,
                    "projection_pairs_count": projection_pairs_count,
                    "collision_pairs_count": projection_pairs_count,
                },
                "boundary_soft": {
                    "boundary_band_width_w": boundary_band_width,
                    "boundary_band_fraction": boundary_band_fraction,
                    "boundary_soft_strength": boundary_soft_strength,
                    "boundary_force_events_count_tick": boundary_force_events_count_tick,
                },
                "outliers": outlier_stats,
                "max_outlier_persistence": max_outlier_persistence,
                "persistent_outlier_unit_ids": sorted(set(persistent_outlier_units)),
            }
            boundary_force_total = getattr(self, "_debug_boundary_force_events_total", 0)
            boundary_force_total += boundary_force_events_count_tick
            self._debug_boundary_force_events_total = boundary_force_total
            self._debug_diag_pending["boundary_soft"]["boundary_force_events_count_total"] = boundary_force_total
            if diag4_payload is not None:
                self._debug_diag_pending["diag4"] = diag4_payload
        else:
            self._debug_diag_pending = None

        return replace(state, units=updated_units)

    def resolve_combat(self, state: BattleState) -> BattleState:
        combat_cmp_eps = 1e-14
        attack_range_sq = self.attack_range * self.attack_range
        odw_alpha = 0.6
        geom_gamma = 0.3
        CH_ENABLED = bool(getattr(self, "CH_ENABLED", True))
        h_raw = float(getattr(self, "contact_hysteresis_h", 0.10))
        if h_raw < 0.0:
            h = 0.0
        elif h_raw > 0.2:
            h = 0.2
        else:
            h = h_raw
        r_exit = self.attack_range
        r_enter = self.attack_range * (1.0 - h)
        r_exit_sq = r_exit * r_exit
        r_enter_sq = r_enter * r_enter
        alpha_raw = float(getattr(self, "fire_quality_alpha", 0.0))
        if alpha_raw < 0.0:
            fire_quality_alpha = 0.0
        elif alpha_raw > 0.2:
            fire_quality_alpha = 0.2
        else:
            fire_quality_alpha = alpha_raw
        diag_enabled = bool(getattr(self, "debug_fsr_diag_enabled", False))
        diag4_enabled = diag_enabled and bool(getattr(self, "debug_diag4_enabled", False))

        def fleet_local_numeric_index(unit_id: str, default_rank: int) -> int:
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

        snapshot_positions = {unit_id: (unit.position.x, unit.position.y) for unit_id, unit in state.units.items()}
        snapshot_hp = {unit_id: unit.hit_points for unit_id, unit in state.units.items()}
        snapshot_alive = {unit_id: (unit.hit_points > 0.0) for unit_id, unit in state.units.items()}
        snapshot_engaged = {
            unit_id: (unit.engaged, unit.engaged_target_id)
            for unit_id, unit in state.units.items()
        }

        target_local_rank = {}
        for fleet in state.fleets.values():
            for rank, unit_id in enumerate(fleet.unit_ids, start=1):
                target_local_rank[unit_id] = fleet_local_numeric_index(unit_id, rank)

        alive_units = {unit_id: unit for unit_id, unit in state.units.items() if snapshot_alive[unit_id]}
        incoming_damage = {unit_id: 0.0 for unit_id in alive_units}
        self.last_damage_clamp_triggered = False
        total_hp_before = sum(snapshot_hp[uid] for uid in alive_units)
        in_contact_count = 0
        damage_events_count = 0
        sample_contact_debug = None
        engaged_updates = {}
        in_contact_units_by_fleet = {}

        # Snapshot target assignment (no HP writeback dependence).
        w_hp = 1.0
        w_dist = 1e-12
        assigned_target = {}
        orientation_override = {}
        for attacker_id, attacker in alive_units.items():
            attacker_pos = snapshot_positions[attacker_id]
            enemy_ids = [
                enemy_id
                for enemy_id, enemy in state.units.items()
                if snapshot_alive[enemy_id] and enemy.fleet_id != attacker.fleet_id
            ]
            if not enemy_ids:
                assigned_target[attacker_id] = None
                continue

            in_range = []
            for enemy_id in enemy_ids:
                enemy_pos = snapshot_positions[enemy_id]
                dx = enemy_pos[0] - attacker_pos[0]
                dy = enemy_pos[1] - attacker_pos[1]
                distance_sq = (dx * dx) + (dy * dy)
                if distance_sq <= (attack_range_sq - combat_cmp_eps):
                    in_range.append((enemy_id, snapshot_hp[enemy_id], distance_sq, target_local_rank.get(enemy_id, 0)))

            if in_range:
                best_enemy_id = None
                best_score = 0.0
                best_dist_sq = 0.0
                best_rank = 0
                for enemy_id, hp, dist_sq, rank in in_range:
                    enemy_max_hp = state.units[enemy_id].max_hit_points
                    if enemy_max_hp > 0.0:
                        normalized_hp = hp / enemy_max_hp
                    else:
                        normalized_hp = 0.0
                    normalized_distance = dist_sq / attack_range_sq if attack_range_sq > 0.0 else 0.0
                    score = (w_hp * normalized_hp) + (w_dist * normalized_distance)

                    if best_enemy_id is None:
                        best_enemy_id = enemy_id
                        best_score = score
                        best_dist_sq = dist_sq
                        best_rank = rank
                        continue
                    if score < (best_score - combat_cmp_eps):
                        best_enemy_id = enemy_id
                        best_score = score
                        best_dist_sq = dist_sq
                        best_rank = rank
                        continue
                    if abs(score - best_score) <= combat_cmp_eps:
                        if dist_sq < (best_dist_sq - combat_cmp_eps):
                            best_enemy_id = enemy_id
                            best_score = score
                            best_dist_sq = dist_sq
                            best_rank = rank
                            continue
                        if abs(dist_sq - best_dist_sq) <= combat_cmp_eps and rank < best_rank:
                            best_enemy_id = enemy_id
                            best_score = score
                            best_dist_sq = dist_sq
                            best_rank = rank
                assigned_target[attacker_id] = best_enemy_id
            else:
                assigned_target[attacker_id] = None

        attackers_to_target = {unit_id: 0 for unit_id in alive_units}
        attackers_by_fleet = {}
        alive_by_fleet = {}
        for unit in alive_units.values():
            alive_by_fleet[unit.fleet_id] = alive_by_fleet.get(unit.fleet_id, 0) + 1

        for attacker_id, target_id in assigned_target.items():
            if target_id is not None:
                attackers_to_target[target_id] += 1
                attacker_fleet = alive_units[attacker_id].fleet_id
                attackers_by_fleet[attacker_fleet] = attackers_by_fleet.get(attacker_fleet, 0) + 1

        participation_by_fleet = {}
        for fleet_id, alive_count in alive_by_fleet.items():
            if alive_count > 0:
                participation_by_fleet[fleet_id] = attackers_by_fleet.get(fleet_id, 0) / alive_count
            else:
                participation_by_fleet[fleet_id] = 0.0

        for attacker_id, target_id in assigned_target.items():
            attacker = alive_units[attacker_id]
            if target_id is None:
                engaged_updates[attacker_id] = (False, None)
                continue
            attacker_pos = snapshot_positions[attacker_id]
            target_pos = snapshot_positions[target_id]
            dx_contact = target_pos[0] - attacker_pos[0]
            dy_contact = target_pos[1] - attacker_pos[1]
            d_sq = (dx_contact * dx_contact) + (dy_contact * dy_contact)
            prev_engaged, prev_target_id = snapshot_engaged.get(attacker_id, (False, None))

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
                in_contact_units_by_fleet.setdefault(attacker.fleet_id, set()).add(attacker_id)
                in_contact_units_by_fleet.setdefault(alive_units[target_id].fleet_id, set()).add(target_id)
            attacker = replace(
                attacker,
                engaged=engaged_updates[attacker_id][0],
                engaged_target_id=engaged_updates[attacker_id][1],
            )
            target = alive_units[target_id]
            p_attacker = participation_by_fleet.get(attacker.fleet_id, 0.0)
            p_target = participation_by_fleet.get(target.fleet_id, 0.0)
            coupling = 1.0 + (geom_gamma * (p_attacker - p_target))

            bias_attacker = odw_alpha * (attacker.offense_defense_weight - 0.5)
            bias_target = odw_alpha * (target.offense_defense_weight - 0.5)
            damage_scale = 1.0 + bias_attacker - bias_target
            if damage_scale < 0.0:
                damage_scale = 0.0
                self.last_damage_clamp_triggered = True
            q = 1.0
            if fire_quality_alpha > 0.0:
                attacker_pos = snapshot_positions[attacker_id]
                target_pos = snapshot_positions[target_id]
                vx = target_pos[0] - attacker_pos[0]
                vy = target_pos[1] - attacker_pos[1]
                v_norm_sq = (vx * vx) + (vy * vy)
                if v_norm_sq > 0.0:
                    v_norm = math.sqrt(v_norm_sq)
                    ux = vx / v_norm
                    uy = vy / v_norm

                    orient = attacker.orientation_vector
                    ox = orient.x
                    oy = orient.y
                    o_norm_sq = (ox * ox) + (oy * oy)
                    if o_norm_sq > 0.0:
                        o_norm = math.sqrt(o_norm_sq)
                        nox = ox / o_norm
                        noy = oy / o_norm
                        phi_i = math.atan2(noy, nox)
                        _ = phi_i
                        cos_theta = (nox * ux) + (noy * uy)
                        if cos_theta > 1.0:
                            cos_theta = 1.0
                        elif cos_theta < -1.0:
                            cos_theta = -1.0
                        q = 1.0 + (fire_quality_alpha * cos_theta)
                if q < 0.0:
                    q = 0.0

            event_damage = self.damage_per_tick * damage_scale * coupling * q
            incoming_damage[target_id] += event_damage
            damage_events_count += 1
            if sample_contact_debug is None:
                sample_contact_debug = {
                    "attacker_id": attacker_id,
                    "target_id": target_id,
                    "distance_sq": d_sq,
                    "r_enter_sq": r_enter_sq,
                    "r_exit_sq": r_exit_sq,
                    "damage": event_damage,
                }

            velocity_norm_sq = (attacker.velocity.x * attacker.velocity.x) + (attacker.velocity.y * attacker.velocity.y)
            if velocity_norm_sq <= 1e-12:
                attacker_pos = snapshot_positions[attacker_id]
                target_pos = snapshot_positions[target_id]
                orient_x = target_pos[0] - attacker_pos[0]
                orient_y = target_pos[1] - attacker_pos[1]
                orient_norm = math.sqrt((orient_x * orient_x) + (orient_y * orient_y))
                if orient_norm > 0.0:
                    orientation_override[attacker_id] = Vec2(
                        x=orient_x / orient_norm,
                        y=orient_y / orient_norm,
                    )

        updated_units = {}
        for unit_id, unit in alive_units.items():
            new_hp = unit.hit_points - incoming_damage.get(unit_id, 0.0)
            if new_hp > 0.0:
                engaged_state = engaged_updates.get(unit_id, snapshot_engaged.get(unit_id, (False, None)))
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
        if (
            self.debug_contact_assert
            and state.tick <= self.debug_contact_sample_ticks
            and in_contact_count > 0
            and not (total_hp_after < total_hp_before)
        ):
            raise RuntimeError(
                f"Combat assert failed at tick={state.tick}: "
                f"in_contact_count={in_contact_count}, "
                f"damage_events_count={damage_events_count}, "
                f"total_hp_before={total_hp_before}, total_hp_after={total_hp_after}, "
                f"sample={sample_contact_debug}"
            )
        if diag_enabled:
            fleet_centroids = {}
            for fleet_id, fleet in state.fleets.items():
                alive_ids = [
                    unit_id
                    for unit_id in fleet.unit_ids
                    if unit_id in snapshot_positions and snapshot_alive.get(unit_id, False)
                ]
                if not alive_ids:
                    continue
                centroid_x = sum(snapshot_positions[unit_id][0] for unit_id in alive_ids) / len(alive_ids)
                centroid_y = sum(snapshot_positions[unit_id][1] for unit_id in alive_ids) / len(alive_ids)
                fleet_centroids[fleet_id] = (centroid_x, centroid_y)

            sorted_fleet_ids = sorted(fleet_centroids.keys())
            if len(sorted_fleet_ids) >= 2:
                cax, cay = fleet_centroids[sorted_fleet_ids[0]]
                cbx, cby = fleet_centroids[sorted_fleet_ids[1]]
                axis_x = cbx - cax
                axis_y = cby - cay
                axis_norm = math.sqrt((axis_x * axis_x) + (axis_y * axis_y))
                if axis_norm > 0.0:
                    axis_x /= axis_norm
                    axis_y /= axis_norm
                else:
                    axis_x = 1.0
                    axis_y = 0.0
                mid_x = 0.5 * (cax + cbx)
                mid_y = 0.5 * (cay + cby)
            else:
                axis_x = 1.0
                axis_y = 0.0
                mid_x = 0.0
                mid_y = 0.0
            ortho_x = -axis_y
            ortho_y = axis_x

            def _span_std(values: list[float]) -> tuple[float, float]:
                if not values:
                    return 0.0, 0.0
                if len(values) == 1:
                    return 0.0, 0.0
                vmin = min(values)
                vmax = max(values)
                mean_v = sum(values) / len(values)
                var_v = sum((v - mean_v) * (v - mean_v) for v in values) / len(values)
                if var_v < 0.0:
                    var_v = 0.0
                return vmax - vmin, math.sqrt(var_v)

            frontline_per_fleet = {}
            combined_offsets = []
            for fleet_id, contact_ids in in_contact_units_by_fleet.items():
                cx, cy = fleet_centroids.get(fleet_id, (0.0, 0.0))
                fleet_offsets = []
                for unit_id in contact_ids:
                    if unit_id not in snapshot_positions:
                        continue
                    ux, uy = snapshot_positions[unit_id]
                    fleet_offsets.append(((ux - cx) * ortho_x) + ((uy - cy) * ortho_y))
                    combined_offsets.append(((ux - mid_x) * ortho_x) + ((uy - mid_y) * ortho_y))
                width, width_std = _span_std(fleet_offsets)
                frontline_per_fleet[fleet_id] = {
                    "in_contact_unit_count": len(fleet_offsets),
                    "frontline_width": width,
                    "frontline_width_std": width_std,
                }

            combined_width, combined_width_std = _span_std(combined_offsets)
            pending_diag = getattr(self, "_debug_diag_pending", None)
            if pending_diag is not None and pending_diag.get("tick") == state.tick:
                tick_diag = pending_diag
            else:
                tick_diag = {"tick": state.tick}
            if diag4_enabled:
                contact_window_raw = int(getattr(self, "debug_diag4_contact_window", 20))
                if contact_window_raw < 20:
                    contact_window = 20
                elif contact_window_raw > 200:
                    contact_window = 200
                else:
                    contact_window = contact_window_raw
                contact_history = getattr(self, "_debug_diag4_contact_history", None)
                if contact_history is None:
                    contact_history = {}
                    self._debug_diag4_contact_history = contact_history

                in_contact_units = set()
                for contact_ids in in_contact_units_by_fleet.values():
                    in_contact_units.update(contact_ids)
                alive_diag_units = {
                    unit_id
                    for unit_id, is_alive in snapshot_alive.items()
                    if is_alive
                }
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
                                    history = contact_history.get(unit_id, [])
                                    if history:
                                        row["rolling_in_contact_ratio"] = sum(history) / len(history)
                                    else:
                                        row["rolling_in_contact_ratio"] = 0.0
                                    neighbor_sep = int(row.get("neighbor_count_sep", 0))
                                    neighbor_contact = int(row.get("neighbor_count_contact", 0))
                                    if neighbor_sep <= 0:
                                        isolated_candidates += 1
                                    elif neighbor_contact <= 0:
                                        blocked_candidates += 1
                            module_a["isolated_candidate_count"] = isolated_candidates
                            module_a["blocked_candidate_count"] = blocked_candidates
                            module_a["rolling_contact_window"] = contact_window

                    module_d = diag4_tick.get("module_d")
                    if isinstance(module_d, dict):
                        persistent_reentry = module_d.get("persistent_reentry")
                        if isinstance(persistent_reentry, list):
                            for row in persistent_reentry:
                                if not isinstance(row, dict):
                                    continue
                                unit_id = row.get("unit_id")
                                history = contact_history.get(unit_id, [])
                                if history:
                                    row["rolling_in_contact_ratio"] = sum(history) / len(history)
                                else:
                                    row["rolling_in_contact_ratio"] = 0.0
            tick_diag["combat"] = {
                "in_contact_count": in_contact_count,
                "damage_events_count": damage_events_count,
            }
            tick_diag["frontline"] = {
                "in_contact_unit_count_total": len(combined_offsets),
                "frontline_width": combined_width,
                "frontline_width_std": combined_width_std,
                "per_fleet": frontline_per_fleet,
            }
            self.debug_diag_last_tick = tick_diag
            self.debug_diag_timeseries.append(tick_diag)

        updated_fleets = {}
        for fleet_id, fleet in state.fleets.items():
            alive_ids = tuple(unit_id for unit_id in fleet.unit_ids if unit_id in updated_units)
            updated_fleets[fleet_id] = replace(fleet, unit_ids=alive_ids)

        return replace(state, units=updated_units, fleets=updated_fleets)
