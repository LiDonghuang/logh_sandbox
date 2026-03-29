from dataclasses import replace
import math

from runtime.runtime_v0_1 import BattleState, Vec2


NEUTRAL_TRANSIT_FIXTURE_RESTORE_DEADBAND_RATIO = 0.28


class EngineTickSkeleton:
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
            "fire_quality_alpha": 0.0,
        }

        self._boundary_surface = {
            "soft_enabled": True,
            "hard_enabled": False,
            "soft_strength": 1.0,
        }

        self._fsr_surface = {
            "enabled": False,
            "strength": 0.0,
            "lambda_delta": 0.10,
        }

        # Active movement surface retained after v1 retirement.
        self._movement_surface = {
            "alpha_sep": 0.6,
            "model": "v3a",
            "v3a_experiment": "base",
            "centroid_probe_scale": 1.0,
            "odw_posture_bias_enabled": False,
            "odw_posture_bias_k": 0.0,
            "odw_posture_bias_clip_delta": 0.2,
        }

        # Active debug/reference knobs still used by maintained diagnostics.
        self._diag_surface = {
            "fsr_diag_enabled": False,
            "diag4_enabled": False,
            "diag4_topk": 10,
            "diag4_contact_window": 20,
        }

        # Internal-only state is kept behind a single host instead of top-level sprawl.
        self._debug_state = {
            "fsr_reference": {},
            "diag_pending": None,
            "diag_timeseries": [],
        }

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
        return min(1.0, max(0.0, value))

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
        if str(fixture_cfg.get("active_mode", "")).strip().lower() != "neutral_transit_v1":
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

    def _compute_cohesion_v2_geometry(self, state: BattleState, fleet_id: str) -> tuple[float, dict]:
        eps = 1e-12
        alive_positions, centroid_x, centroid_y = self._collect_alive_fleet_positions(state, fleet_id)
        if alive_positions is None:
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
        if not alive_positions:
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
        n_alive = len(alive_positions)

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
        else:
            connect_radius = float(self.separation_radius)
            if connect_radius < eps:
                connect_radius = eps
            connect_radius_sq = connect_radius * connect_radius
            largest_component_size = self._largest_connected_component_size(alive_positions, connect_radius_sq)
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

    def _compute_cohesion_v3_geometry(self, state: BattleState, fleet_id: str) -> tuple[float, dict]:
        eps = 1e-12
        rho_low = 0.35
        rho_high = 1.15
        penalty_k = 6.0
        v3_connect_multiplier = max(1e-12, float(getattr(self, "V3_CONNECT_RADIUS_MULTIPLIER", 1.0)))
        v3_r_ref_multiplier = max(1e-12, float(getattr(self, "V3_R_REF_RADIUS_MULTIPLIER", 1.0)))

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

    def evaluate_cohesion(self, state: BattleState) -> BattleState:
        decision_source = str(getattr(self, "runtime_cohesion_decision_source", "v2")).strip().lower() or "v2"
        if decision_source not in {"v2", "v3_test"}:
            raise ValueError(f"Unsupported runtime_cohesion_decision_source={decision_source!r}")

        runtime_cohesion = {}
        runtime_components = {}
        for fleet_id, fleet in state.fleets.items():
            if decision_source == "v3_test":
                cohesion_v3, v3_components = self._compute_cohesion_v3_geometry(state, fleet_id)
                runtime_cohesion[fleet_id] = cohesion_v3
                runtime_components[fleet_id] = v3_components
            else:
                cohesion_v2, v2_components = self._compute_cohesion_v2_geometry(state, fleet_id)
                runtime_cohesion[fleet_id] = cohesion_v2
                runtime_components[fleet_id] = v2_components

        if decision_source == "v3_test":
            self.debug_last_cohesion_v3 = dict(runtime_cohesion)
            self.debug_last_cohesion_v3_components = dict(runtime_components)
        else:
            self.debug_last_cohesion_v3 = {}
            self.debug_last_cohesion_v3_components = {}

        return replace(state, last_fleet_cohesion=runtime_cohesion)

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

    def _build_movement_diag4_payload(
        self,
        *,
        state: BattleState,
        updated_units: dict,
        final_positions: dict,
        r_sep: float,
        r_sep_sq: float,
        attack_range_sq: float,
    ) -> dict:
        diag_surface = self._diag_surface
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
                "neighbor_radius_contact": self.attack_range,
                "topk_candidates": module_a_topk,
            },
        }

    def _build_movement_diag_pending(
        self,
        *,
        state: BattleState,
        updated_units: dict,
        tentative_positions: dict,
        delta_position: dict,
        projection_pairs_count: int,
        boundary_band_width: float,
        boundary_band_fraction: float,
        boundary_soft_strength: float,
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
                "collision_pairs_count": projection_pairs_count,
            },
            "boundary_soft": {
                "boundary_band_width_w": boundary_band_width,
                "boundary_band_fraction": boundary_band_fraction,
                "boundary_soft_strength": boundary_soft_strength,
                "boundary_force_events_count_tick": boundary_force_events_count_tick,
            },
            "legality": {
                "reference_surface_count": int(legality_reference_surface_count),
                "feasible_surface_count": int(legality_feasible_surface_count),
                "middle_stage_active": bool(legality_middle_stage_active),
                "handoff_ready": bool(legality_handoff_ready),
            },
        }
        boundary_force_total = int(self._debug_state.get("_debug_boundary_force_events_total", 0))
        boundary_force_total += boundary_force_events_count_tick
        self._debug_state["_debug_boundary_force_events_total"] = boundary_force_total
        pending["boundary_soft"]["boundary_force_events_count_total"] = boundary_force_total

        if diag4_enabled:
            pending["diag4"] = self._build_movement_diag4_payload(
                state=state,
                updated_units=updated_units,
                final_positions=final_positions,
                r_sep=r_sep,
                r_sep_sq=r_sep_sq,
                attack_range_sq=attack_range_sq,
            )
        return pending

    def integrate_movement(self, state: BattleState) -> BattleState:
        movement_surface = self._movement_surface
        diag_surface = self._diag_surface
        boundary_surface = self._boundary_surface
        fsr_surface = self._fsr_surface
        r_sep = self.separation_radius
        r_sep_sq = r_sep * r_sep
        sep_branch_eps = 1e-14
        sep_threshold_sq = r_sep_sq - sep_branch_eps
        alpha_sep = max(0.0, float(movement_surface["alpha_sep"]))
        min_unit_spacing = self.separation_radius
        min_unit_spacing_sq = min_unit_spacing * min_unit_spacing
        attack_range_sq = self.attack_range * self.attack_range
        diag_enabled = bool(diag_surface["fsr_diag_enabled"])
        diag4_enabled = diag_enabled and bool(diag_surface["diag4_enabled"])
        fixture_cfg = getattr(self, "TEST_RUN_FIXTURE_CFG", None)
        fixture_terminal_step_gate_enabled = (
            isinstance(fixture_cfg, dict)
            and str(fixture_cfg.get("active_mode", "")).strip().lower() == "neutral_transit_v1"
            and bool(fixture_cfg.get("expected_position_candidate_active", False))
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
        fixture_trace_stop_radius = (
            fixture_terminal_step_gate_stop_radius
            if fixture_trace_enabled
            else 0.0
        )
        arena_linear_size = max(0.0, float(state.arena_size))
        boundary_band_limit = 0.05 * arena_linear_size
        boundary_band_width = max(0.0, min(r_sep, boundary_band_limit))
        boundary_band_fraction = (boundary_band_width / arena_linear_size) if arena_linear_size > 0.0 else 0.0
        boundary_force_events_count_tick = 0
        boundary_soft_enabled = bool(boundary_surface["soft_enabled"])
        boundary_soft_strength = max(0.0, float(boundary_surface["soft_strength"]))

        snapshot_positions = {
            unit_id: (unit.position.x, unit.position.y)
            for unit_id, unit in state.units.items()
            if unit.hit_points > 0.0
        }

        movement_model = str(movement_surface.get("model", "v3a")).strip().lower()
        if movement_model not in {"v3a", "v4a"}:
            movement_model = "v3a"
        v4a_active = movement_model == "v4a"
        movement_v3a_experiment = str(movement_surface["v3a_experiment"]).strip().lower()
        allowed_v3a_experiments = {"base", "exp_precontact_centroid_probe"}
        if movement_v3a_experiment not in allowed_v3a_experiments:
            movement_v3a_experiment = "base"
        centroid_probe_scale = min(1.0, max(0.0, float(movement_surface["centroid_probe_scale"])))
        odw_posture_bias_fleet_enabled = bool(movement_surface["odw_posture_bias_enabled"])
        odw_posture_bias_k_fleet = max(0.0, float(movement_surface["odw_posture_bias_k"]))
        odw_posture_bias_clip_delta_fleet = max(0.0, float(movement_surface["odw_posture_bias_clip_delta"]))

        updated_units = dict(state.units)
        fixture_trace_units_pending = None
        normalized_params_by_fleet = {
            fleet_id: fleet.parameters.normalized()
            for fleet_id, fleet in state.fleets.items()
        }
        for fleet_id, fleet in state.fleets.items():
            target_direction = state.last_target_direction.get(fleet_id, (0.0, 0.0))
            normalized_params = normalized_params_by_fleet[fleet_id]

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

            enemy_sum_x = 0.0
            enemy_sum_y = 0.0
            enemy_alive_count = 0
            for other_fleet_id, other_fleet in state.fleets.items():
                if other_fleet_id == fleet_id:
                    continue
                for unit_id in other_fleet.unit_ids:
                    unit = updated_units.get(unit_id)
                    if unit is None or unit.hit_points <= 0.0:
                        continue
                    enemy_sum_x += unit.position.x
                    enemy_sum_y += unit.position.y
                    enemy_alive_count += 1
            if enemy_alive_count > 0:
                enemy_centroid_x = enemy_sum_x / enemy_alive_count
                enemy_centroid_y = enemy_sum_y / enemy_alive_count
            else:
                enemy_centroid_x = centroid_x
                enemy_centroid_y = centroid_y
            has_enemy_alive = enemy_alive_count > 0

            radius_sq_sum = 0.0
            for unit_id in alive_unit_ids:
                unit = updated_units[unit_id]
                dx0 = unit.position.x - centroid_x
                dy0 = unit.position.y - centroid_y
                radius_sq_sum += (dx0 * dx0) + (dy0 * dy0)
            if alive_count > 0:
                fleet_rms_radius = math.sqrt(radius_sq_sum / alive_count)
            else:
                fleet_rms_radius = 0.0

            if alive_count >= 2:
                # Enemy-facing lateral span reference for ODW width redistribution.
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
                    for unit_id in alive_unit_ids:
                        unit = updated_units[unit_id]
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
                    lateral_span_ref = max((abs(value) for value in lateral_values), default=0.0)
                else:
                    lateral_span_ref = 0.0
            else:
                lateral_span_ref = 0.0

            engaged_alive_count = 0
            for unit_id in alive_unit_ids:
                unit = updated_units[unit_id]
                if bool(unit.engaged) and bool(unit.engaged_target_id):
                    engaged_alive_count += 1
            if alive_count > 0:
                engaged_fraction = engaged_alive_count / float(alive_count)
            else:
                engaged_fraction = 0.0
            contact_gate = engaged_fraction / 0.25
            contact_gate = min(1.0, max(0.0, contact_gate))

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

            kappa = normalized_params["formation_rigidity"]
            pd_norm = normalized_params.get("pursuit_drive", 0.5)
            mobility_raw = float(fleet.parameters.mobility_bias)
            # Canonical 1-9 mapping:
            # MB_eff = 0.2 * (mobility_bias - 5) / 4, clipped to [-0.2, +0.2].
            mb = 0.2 * (mobility_raw - 5.0) / 4.0
            if mb < -0.2:
                mb = -0.2
            elif mb > 0.2:
                mb = 0.2
            if v4a_active:
                mb = 0.0

            # Phase V3 canonical PD activation:
            # EnemyCollapseSignal = 1 - EnemyCohesion
            # PursuitConfirmThreshold = 1 - PD_norm
            enemy_cohesion_values = []
            for other_fleet_id, other_fleet in state.fleets.items():
                if other_fleet_id == fleet_id:
                    continue
                if len(other_fleet.unit_ids) == 0:
                    continue
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
                pursuit_intensity = min(1.0, max(0.0, pursuit_intensity))
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
            odw_posture_bias_active = (not v4a_active) and odw_posture_bias_fleet_enabled and odw_posture_bias_k_fleet > 0.0
            tx = target_direction[0]
            ty = target_direction[1]
            target_norm = 0.0
            t_hat_x = 0.0
            t_hat_y = 0.0
            has_target_axis = False
            if (not mb_is_zero) or odw_posture_bias_active:
                target_norm = math.sqrt((tx * tx) + (ty * ty))
                if target_norm > 1e-12:
                    t_hat_x = tx / target_norm
                    t_hat_y = ty / target_norm
                    has_target_axis = True

            fixture_expected_reference = self._build_fixture_expected_position_map(
                state=state,
                fleet_id=fleet_id,
                centroid_x=centroid_x,
                centroid_y=centroid_y,
                target_direction=target_direction,
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
                and str(fixture_cfg.get("active_mode", "")).strip().lower() == "neutral_transit_v1"
                and bool(fixture_cfg.get("expected_position_candidate_active", False))
            ):
                fixture_restore_deadband = (
                    float(self.separation_radius) * NEUTRAL_TRANSIT_FIXTURE_RESTORE_DEADBAND_RATIO
                )

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
                    and fixture_step_magnitude_gate_active
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
                    if cohesion_axial_raw < 0.0:
                        one_sided_axial_restore_gate_active = True
                        cohesion_axial_gated = cohesion_axial_raw * fixture_step_magnitude_gain
                        cohesion_vector_x = (
                            (cohesion_axial_gated * restore_axis_x)
                            + (cohesion_lateral_raw * restore_lateral_x)
                        )
                        cohesion_vector_y = (
                            (cohesion_axial_gated * restore_axis_y)
                            + (cohesion_lateral_raw * restore_lateral_y)
                        )
                    else:
                        cohesion_axial_gated = cohesion_axial_raw
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

                if not has_enemy_alive:
                    enemy_dir_x = 0.0
                    enemy_dir_y = 0.0
                else:
                    enemy_vec_x = enemy_centroid_x - unit.position.x
                    enemy_vec_y = enemy_centroid_y - unit.position.y
                    enemy_vec_norm = math.sqrt((enemy_vec_x * enemy_vec_x) + (enemy_vec_y * enemy_vec_y))
                    if enemy_vec_norm > 1e-12:
                        enemy_dir_x = enemy_vec_x / enemy_vec_norm
                        enemy_dir_y = enemy_vec_y / enemy_vec_norm
                    else:
                        enemy_dir_x = target_direction[0]
                        enemy_dir_y = target_direction[1]

                if v4a_active:
                    stray_factor = 0.0
                else:
                    if fleet_rms_radius > 1e-12:
                        stray_ratio_raw = (cohesion_norm / fleet_rms_radius)
                    else:
                        stray_ratio_raw = 0.0
                    if stray_ratio_raw <= stray_threshold_ratio:
                        stray_factor = 0.0
                    else:
                        stray_factor = (stray_ratio_raw - stray_threshold_ratio) / max(1e-12, 2.0 - stray_threshold_ratio)
                    stray_factor = min(1.0, max(0.0, stray_factor))

                anti_stretch = 0.0

                cohesion_scale = 1.0 + (0.40 * anti_stretch)
                cohesion_x = (kappa * cohesion_gain * cohesion_scale) * cohesion_dir[0]
                cohesion_y = (kappa * cohesion_gain * cohesion_scale) * cohesion_dir[1]
                if movement_v3a_experiment == "exp_precontact_centroid_probe":
                    # A-line causal probe: only scale centroid restoration term.
                    cohesion_x *= centroid_probe_scale
                    cohesion_y *= centroid_probe_scale
                if v4a_active:
                    attract_x = 0.0
                    attract_y = 0.0
                else:
                    attract_gain = attract_gain_base + ((attract_gain_max - attract_gain_base) * stray_factor)
                    enemy_pull_gain = enemy_pull_floor + ((1.0 - enemy_pull_floor) * stray_factor)
                    attract_x = attract_gain * (
                        (enemy_pull_gain * enemy_dir_x) + ((1.0 - enemy_pull_gain) * target_direction[0])
                    )
                    attract_y = attract_gain * (
                        (enemy_pull_gain * enemy_dir_y) + ((1.0 - enemy_pull_gain) * target_direction[1])
                    )
                target_term_x = (forward_gain * target_direction[0]) + attract_x
                target_term_y = (forward_gain * target_direction[1]) + attract_y
                separation_term_x = alpha_sep * separation_dir[0]
                separation_term_y = alpha_sep * separation_dir[1]
                boundary_term_x = alpha_sep * boundary_x
                boundary_term_y = alpha_sep * boundary_y
                maneuver_x = target_term_x + separation_term_x + boundary_term_x
                maneuver_y = target_term_y + separation_term_y + boundary_term_y
                if has_target_axis:
                    dot_mt = (maneuver_x * t_hat_x) + (maneuver_y * t_hat_y)
                    m_parallel_x = dot_mt * t_hat_x
                    m_parallel_y = dot_mt * t_hat_y
                    m_tangent_x = maneuver_x - m_parallel_x
                    m_tangent_y = maneuver_y - m_parallel_y
                    if odw_posture_bias_active:
                        odw_raw = float(fleet.parameters.offense_defense_weight)
                        odw_centered = (odw_raw - 5.0) / 4.0
                        odw_centered = min(1.0, max(-1.0, odw_centered))
                        if lateral_span_ref > 1e-12:
                            lateral_offset = ((unit.position.x - centroid_x) * (-t_hat_y)) + (
                                (unit.position.y - centroid_y) * t_hat_x
                            )
                            lateral_norm = abs(lateral_offset) / lateral_span_ref
                            lateral_norm = min(1.0, lateral_norm)
                        else:
                            lateral_norm = 0.0
                        # ODW redistributes forward pressure across the fleet width:
                        # center-heavy for offensive posture, wing-heavy for defensive posture.
                        width_profile = 1.0 - (2.0 * lateral_norm)
                        odw_parallel_scale = 1.0 + (odw_posture_bias_k_fleet * odw_centered * width_profile)
                        odw_parallel_scale_min = max(0.0, 1.0 - odw_posture_bias_clip_delta_fleet)
                        odw_parallel_scale_max = 1.0 + odw_posture_bias_clip_delta_fleet
                        if odw_parallel_scale < odw_parallel_scale_min:
                            odw_parallel_scale = odw_parallel_scale_min
                        elif odw_parallel_scale > odw_parallel_scale_max:
                            odw_parallel_scale = odw_parallel_scale_max
                    else:
                        odw_parallel_scale = 1.0
                    tangent_scale = 1.0 + mb
                    tangent_scale -= (lateral_damping_base * stray_factor)
                    parallel_scale = 1.0
                    if tangent_scale < 0.05:
                        tangent_scale = 0.05
                    maneuver_x = ((1.0 - mb) * parallel_scale * odw_parallel_scale * m_parallel_x) + (tangent_scale * m_tangent_x)
                    maneuver_y = ((1.0 - mb) * parallel_scale * odw_parallel_scale * m_parallel_y) + (tangent_scale * m_tangent_y)
                    target_term_x = maneuver_x - separation_term_x - boundary_term_x
                    target_term_y = maneuver_y - separation_term_y - boundary_term_y
                if deep_pursuit_mode:
                    extension_gain_effective = extension_gain
                    maneuver_x *= extension_gain_effective
                    maneuver_y *= extension_gain_effective
                    target_term_x *= extension_gain_effective
                    target_term_y *= extension_gain_effective
                    separation_term_x *= extension_gain_effective
                    separation_term_y *= extension_gain_effective
                    boundary_term_x *= extension_gain_effective
                    boundary_term_y *= extension_gain_effective
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
                if total_norm > movement_eps:
                    step_distance = (unit.max_speed * state.dt) * fixture_step_magnitude_gain
                    step_speed = unit.max_speed * fixture_step_magnitude_gain
                if total_norm > movement_eps and step_distance > movement_eps:
                    pre_projection_step_scale = step_distance / total_norm
                    pre_projection_total_dx = total_direction[0] * step_distance
                    pre_projection_total_dy = total_direction[1] * step_distance
                    pre_projection_total_norm = math.sqrt(
                        (pre_projection_total_dx * pre_projection_total_dx)
                        + (pre_projection_total_dy * pre_projection_total_dy)
                    )
                    orientation = Vec2(x=total_direction[0], y=total_direction[1])
                    velocity = Vec2(
                        x=total_direction[0] * step_speed,
                        y=total_direction[1] * step_speed,
                    )
                else:
                    orientation = unit.orientation_vector
                    velocity = Vec2(x=0.0, y=0.0)

                new_position = Vec2(
                    x=unit.position.x + pre_projection_total_dx,
                    y=unit.position.y + pre_projection_total_dy,
                )
                if fixture_trace_units is not None:
                    target_norm_raw = math.sqrt((target_term_x * target_term_x) + (target_term_y * target_term_y))
                    base_target_norm = math.sqrt(
                        (float(target_direction[0]) * float(target_direction[0]))
                        + (float(target_direction[1]) * float(target_direction[1]))
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
                        "target_dir_x": float(target_direction[0]),
                        "target_dir_y": float(target_direction[1]),
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

        if diag4_enabled:
            post_move_positions = {
                unit_id: (unit.position.x, unit.position.y)
                for unit_id, unit in updated_units.items()
                if unit.hit_points > 0.0
            }
        else:
            post_move_positions = {}

        fsr_enabled = bool(fsr_surface["enabled"])
        fsr_strength_raw = float(fsr_surface["strength"])
        fsr_strength = min(0.3, max(0.0, fsr_strength_raw))

        # FSR block: one centroid + one lambda + one isotropic scale per fleet per tick.
        if fsr_enabled and fsr_strength > 0.0:
            delta_raw = float(fsr_surface["lambda_delta"])
            delta_lambda = min(0.5, max(0.0, delta_raw))
            fsr_eps = 1e-12

            fsr_reference = self._debug_state.get("fsr_reference")
            if not isinstance(fsr_reference, dict):
                fsr_reference = {}
                self._debug_state["fsr_reference"] = fsr_reference

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

                kappa_f = normalized_params_by_fleet[fleet_id]["formation_rigidity"]
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
            self._debug_state["debug_last_fsr_stats"] = fsr_tick_stats

        if diag4_enabled:
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

        if diag_enabled:
            pending_diag = self._build_movement_diag_pending(
                state=state,
                updated_units=updated_units,
                tentative_positions=tentative_positions,
                delta_position=delta_position,
                projection_pairs_count=projection_pairs_count,
                boundary_band_width=boundary_band_width,
                boundary_band_fraction=boundary_band_fraction,
                boundary_soft_strength=boundary_soft_strength,
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
            )
            if fixture_trace_units_pending is not None:
                pending_diag["fixture_terminal_trace"] = {
                    "fleet_id": str(fixture_trace_fleet_id),
                    "units": fixture_trace_units_pending,
                }
            self._debug_state["diag_pending"] = pending_diag
        else:
            self._debug_state["diag_pending"] = None

        return replace(state, units=updated_units)

    def resolve_combat(self, state: BattleState) -> BattleState:
        combat_surface = self._combat_surface
        diag_surface = self._diag_surface
        combat_cmp_eps = 1e-14
        attack_range_sq = self.attack_range * self.attack_range
        attack_range_sq_inv = (1.0 / attack_range_sq) if attack_range_sq > 0.0 else 0.0
        geom_gamma = 0.3
        CH_ENABLED = bool(combat_surface["ch_enabled"])
        h_raw = float(combat_surface["contact_hysteresis_h"])
        h = min(0.2, max(0.0, h_raw))
        r_exit = self.attack_range
        r_enter = self.attack_range * (1.0 - h)
        r_exit_sq = r_exit * r_exit
        r_enter_sq = r_enter * r_enter
        alpha_raw = float(combat_surface["fire_quality_alpha"])
        fire_quality_alpha = min(0.2, max(0.0, alpha_raw))
        diag_enabled = bool(diag_surface["fsr_diag_enabled"])
        diag4_enabled = diag_enabled and bool(diag_surface["diag4_enabled"])

        snapshot_positions = {}
        alive_units = {}
        alive_by_fleet = {}
        for unit_id, unit in state.units.items():
            if unit.hit_points <= 0.0:
                continue
            alive_units[unit_id] = unit
            snapshot_positions[unit_id] = (unit.position.x, unit.position.y)
            fleet_id = unit.fleet_id
            alive_by_fleet[fleet_id] = alive_by_fleet.get(fleet_id, 0) + 1

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
        incoming_damage = {unit_id: 0.0 for unit_id in alive_units}
        total_hp_before = sum(unit.hit_points for unit in alive_units.values())
        in_contact_count = 0
        damage_events_count = 0
        sample_contact_debug = None
        engaged_updates = {}
        in_contact_units = set()
        attackers_by_fleet = {}

        # Snapshot target assignment (no HP writeback dependence).
        w_hp = 1.0
        w_dist = 1e-12
        assigned_target = {}
        orientation_override = {}
        for attacker_id, attacker in alive_units.items():
            attacker_pos_x, attacker_pos_y = snapshot_positions[attacker_id]

            best_enemy_id = None
            best_score = 0.0
            best_dist_sq = 0.0
            best_rank = 0
            best_dx = 0.0
            best_dy = 0.0
            best_scan_order = 0
            for enemy_x, enemy_y, scan_order, enemy_id, enemy_fleet_id, normalized_hp, rank in self._iter_spatial_hash_neighbors(
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
                normalized_distance = distance_sq * attack_range_sq_inv
                score = (w_hp * normalized_hp) + (w_dist * normalized_distance)

                if best_enemy_id is None:
                    best_enemy_id = enemy_id
                    best_score = score
                    best_dist_sq = distance_sq
                    best_rank = rank
                    best_dx = dx
                    best_dy = dy
                    best_scan_order = scan_order
                    continue
                if score < (best_score - combat_cmp_eps):
                    best_enemy_id = enemy_id
                    best_score = score
                    best_dist_sq = distance_sq
                    best_rank = rank
                    best_dx = dx
                    best_dy = dy
                    best_scan_order = scan_order
                    continue
                if abs(score - best_score) <= combat_cmp_eps:
                    if distance_sq < (best_dist_sq - combat_cmp_eps):
                        best_enemy_id = enemy_id
                        best_score = score
                        best_dist_sq = distance_sq
                        best_rank = rank
                        best_dx = dx
                        best_dy = dy
                        best_scan_order = scan_order
                        continue
                    if abs(distance_sq - best_dist_sq) <= combat_cmp_eps:
                        if rank < best_rank or (rank == best_rank and scan_order < best_scan_order):
                            best_enemy_id = enemy_id
                            best_score = score
                            best_dist_sq = distance_sq
                            best_rank = rank
                            best_dx = dx
                            best_dy = dy
                            best_scan_order = scan_order
            if best_enemy_id is None:
                assigned_target[attacker_id] = None
            else:
                assigned_target[attacker_id] = (best_enemy_id, best_dx, best_dy, best_dist_sq)
            if best_enemy_id is not None:
                attacker_fleet = alive_units[attacker_id].fleet_id
                attackers_by_fleet[attacker_fleet] = attackers_by_fleet.get(attacker_fleet, 0) + 1

        participation_by_fleet = {}
        for fleet_id, alive_count in alive_by_fleet.items():
            if alive_count > 0:
                participation_by_fleet[fleet_id] = attackers_by_fleet.get(fleet_id, 0) / alive_count
            else:
                participation_by_fleet[fleet_id] = 0.0

        for attacker_id, target_payload in assigned_target.items():
            attacker = alive_units[attacker_id]
            if target_payload is None:
                engaged_updates[attacker_id] = (False, None)
                continue
            target_id, dx_contact, dy_contact, d_sq = target_payload
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
            target = alive_units[target_id]
            if diag_enabled:
                in_contact_units.add(attacker_id)
                in_contact_units.add(target_id)
            p_attacker = participation_by_fleet.get(attacker.fleet_id, 0.0)
            p_target = participation_by_fleet.get(target.fleet_id, 0.0)
            coupling = 1.0 + (geom_gamma * (p_attacker - p_target))

            q = 1.0
            if fire_quality_alpha > 0.0 and d_sq > 0.0:
                v_norm = math.sqrt(d_sq)
                ux = dx_contact / v_norm
                uy = dy_contact / v_norm

                orient = attacker.orientation_vector
                ox = orient.x
                oy = orient.y
                o_norm_sq = (ox * ox) + (oy * oy)
                if o_norm_sq > 0.0:
                    o_norm = math.sqrt(o_norm_sq)
                    nox = ox / o_norm
                    noy = oy / o_norm
                    cos_theta = max(-1.0, min(1.0, (nox * ux) + (noy * uy)))
                    q = 1.0 + (fire_quality_alpha * cos_theta)
                q = max(0.0, q)

            event_damage = self.damage_per_tick * coupling * q
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
