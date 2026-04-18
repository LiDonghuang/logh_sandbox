from __future__ import annotations

from dataclasses import dataclass, field, replace
import hashlib
import random
from typing import Dict, Iterable, Mapping, Tuple


def _normalize_1_to_9(value: float) -> float:
    if value < 1.0 or value > 9.0:
        raise ValueError(f"parameter value {value} is outside canonical domain [1, 9]")
    return (value - 1.0) / 8.0


@dataclass(frozen=True)
class PersonalityParameters:
    archetype_id: str
    force_concentration_ratio: float
    mobility_bias: float
    offense_defense_weight: float
    risk_appetite: float
    time_preference: float
    targeting_logic: float
    formation_rigidity: float
    perception_radius: float
    pursuit_drive: float
    retreat_threshold: float

    def normalized(self) -> Dict[str, float]:
        return {
            "force_concentration_ratio": _normalize_1_to_9(self.force_concentration_ratio),
            "mobility_bias": _normalize_1_to_9(self.mobility_bias),
            "offense_defense_weight": _normalize_1_to_9(self.offense_defense_weight),
            "risk_appetite": _normalize_1_to_9(self.risk_appetite),
            "time_preference": _normalize_1_to_9(self.time_preference),
            "targeting_logic": _normalize_1_to_9(self.targeting_logic),
            "formation_rigidity": _normalize_1_to_9(self.formation_rigidity),
            "perception_radius": _normalize_1_to_9(self.perception_radius),
            "pursuit_drive": _normalize_1_to_9(self.pursuit_drive),
            "retreat_threshold": _normalize_1_to_9(self.retreat_threshold),
        }


@dataclass(frozen=True)
class Vec2:
    x: float
    y: float


@dataclass(frozen=True)
class UnitState:
    unit_id: str
    fleet_id: str
    position: Vec2
    velocity: Vec2
    hit_points: float = 100.0
    max_hit_points: float = 100.0
    max_speed: float = 5.0
    reference_max_speed: float = 5.0
    hold_reference_max_speed: float | None = None
    offense_defense_weight: float = 0.5
    orientation_vector: Vec2 = field(default_factory=lambda: Vec2(x=1.0, y=0.0))
    engaged: bool = False
    engaged_target_id: str | None = None


@dataclass(frozen=True)
class FleetState:
    fleet_id: str
    unit_ids: tuple[str, ...]


@dataclass(frozen=True)
class BattleState:
    tick: int
    dt: float
    arena_size: float
    units: Mapping[str, UnitState]
    fleets: Mapping[str, FleetState]
    last_fleet_cohesion_score: Mapping[str, float] = field(default_factory=dict)
    last_target_direction: Dict[str, Tuple[float, float]] = field(default_factory=dict)
    last_engagement_intensity: Dict[str, float] = field(default_factory=dict)
    coarse_body_heading_current: Dict[str, Tuple[float, float]] = field(default_factory=dict)
    movement_command_direction: Dict[str, Tuple[float, float]] = field(default_factory=dict)


class SeedManager:
    def __init__(self, root_seed: int) -> None:
        self.root_seed = int(root_seed)

    def derive_seed(self, stream_key: str) -> int:
        payload = f"{self.root_seed}:{stream_key}".encode("utf-8")
        digest = hashlib.sha256(payload).digest()
        seed_u32 = int.from_bytes(digest[:4], byteorder="big", signed=False)
        return seed_u32 % (2**31 - 1)

    def rng(self, stream_key: str) -> random.Random:
        return random.Random(self.derive_seed(stream_key))


def build_initial_cohesion_map(fleet_ids: Iterable[str], default_value: float = 1.0) -> Dict[str, float]:
    return {fleet_id: float(default_value) for fleet_id in fleet_ids}


def initialize_unit_orientations(state: BattleState) -> BattleState:
    updated_units = dict(state.units)
    for fleet_id, fleet in state.fleets.items():
        enemy_units = [
            unit
            for unit in state.units.values()
            if unit.fleet_id != fleet_id and unit.hit_points > 0.0
        ]
        if not enemy_units:
            continue
        enemy_center_x = sum(unit.position.x for unit in enemy_units) / len(enemy_units)
        enemy_center_y = sum(unit.position.y for unit in enemy_units) / len(enemy_units)

        for unit_id in fleet.unit_ids:
            if unit_id not in updated_units:
                continue
            unit = updated_units[unit_id]
            dx = enemy_center_x - unit.position.x
            dy = enemy_center_y - unit.position.y
            norm = (dx * dx + dy * dy) ** 0.5
            if norm > 0.0:
                orientation = Vec2(x=dx / norm, y=dy / norm)
            else:
                orientation = unit.orientation_vector
            updated_units[unit_id] = replace(unit, orientation_vector=orientation)

    return replace(state, units=updated_units)
