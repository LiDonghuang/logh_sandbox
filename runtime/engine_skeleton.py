from dataclasses import replace
import math

from runtime_v0_1 import BattleState, Vec2


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

    def step(self, state: BattleState) -> BattleState:
        snapshot = replace(state, tick=state.tick + 1)
        next_state = self.evaluate_cohesion(snapshot)
        next_state = self.evaluate_target(next_state)
        next_state = self.evaluate_utility(next_state)
        next_state = self.integrate_movement(next_state)
        next_state = self.resolve_combat(next_state)
        return next_state

    def evaluate_cohesion(self, state: BattleState) -> BattleState:
        updated_cohesion = {}
        for fleet_id, fleet in state.fleets.items():
            normalized = fleet.parameters.normalized()
            kappa = normalized["formation_rigidity"]
            old_cohesion = state.last_fleet_cohesion.get(fleet_id, 1.0)
            new_cohesion = old_cohesion + (kappa * 0.01) - ((1.0 - kappa) * 0.005)
            if new_cohesion < 0.0:
                new_cohesion = 0.0
            elif new_cohesion > 1.0:
                new_cohesion = 1.0
            updated_cohesion[fleet_id] = new_cohesion

        return replace(state, last_fleet_cohesion=updated_cohesion)

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
        alpha_sep = 0.6
        min_unit_spacing = self.separation_radius
        min_unit_spacing_sq = min_unit_spacing * min_unit_spacing

        snapshot_positions = {
            unit_id: (unit.position.x, unit.position.y)
            for unit_id, unit in state.units.items()
            if unit.hit_points > 0.0
        }

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

                total_x = target_direction[0] + (kappa * cohesion_dir[0]) + (alpha_sep * separation_dir[0])
                total_y = target_direction[1] + (kappa * cohesion_dir[1]) + (alpha_sep * separation_dir[1])
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

        # Single-pass post-movement projection using tentative snapshot positions.
        tentative_positions = {
            unit_id: (unit.position.x, unit.position.y)
            for unit_id, unit in updated_units.items()
            if unit.hit_points > 0.0
        }
        delta_position = {unit_id: [0.0, 0.0] for unit_id in tentative_positions}
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
                updated_attacker = replace(attacker, engaged=False, engaged_target_id=None)
                alive_units[attacker_id] = updated_attacker
                continue
            attacker_pos = snapshot_positions[attacker_id]
            target_pos = snapshot_positions[target_id]
            dx_contact = target_pos[0] - attacker_pos[0]
            dy_contact = target_pos[1] - attacker_pos[1]
            d_sq = (dx_contact * dx_contact) + (dy_contact * dy_contact)

            if CH_ENABLED:
                if attacker.engaged and attacker.engaged_target_id == target_id:
                    in_contact = d_sq <= (r_exit_sq - combat_cmp_eps)
                else:
                    in_contact = d_sq <= (r_enter_sq - combat_cmp_eps)
            else:
                in_contact = d_sq <= (r_exit_sq - combat_cmp_eps)

            if in_contact:
                updated_attacker = replace(attacker, engaged=True, engaged_target_id=target_id)
            else:
                updated_attacker = replace(attacker, engaged=False, engaged_target_id=None)
            alive_units[attacker_id] = updated_attacker

            if not in_contact:
                continue

            in_contact_count += 1
            attacker = alive_units[attacker_id]
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
                if unit_id in orientation_override:
                    updated_units[unit_id] = replace(
                        unit,
                        hit_points=new_hp,
                        orientation_vector=orientation_override[unit_id],
                    )
                else:
                    updated_units[unit_id] = replace(unit, hit_points=new_hp)
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

        updated_fleets = {}
        for fleet_id, fleet in state.fleets.items():
            alive_ids = tuple(unit_id for unit_id in fleet.unit_ids if unit_id in updated_units)
            updated_fleets[fleet_id] = replace(fleet, unit_ids=alive_ids)

        return replace(state, units=updated_units, fleets=updated_fleets)
