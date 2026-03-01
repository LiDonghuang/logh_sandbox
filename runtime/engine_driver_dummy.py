from dataclasses import replace

from runtime_v0_1 import BattleState
from runtime.engine_skeleton import EngineTickSkeleton


def run_dummy_ticks(
    initial_state: BattleState,
    steps: int,
    capture_positions: bool = False,
    frame_stride: int = 1,
    attack_range: float = 3.0,
    damage_per_tick: float = 1.0,
    separation_radius: float = 1.0,
    fire_quality_alpha: float = 0.1,
    contact_hysteresis_h: float = 0.1,
    ch_enabled: bool = True,
    fsr_enabled: bool = False,
    fsr_strength: float = 0.0,
    boundary_enabled: bool = False,
):
    engine = EngineTickSkeleton(
        attack_range=attack_range,
        damage_per_tick=damage_per_tick,
        separation_radius=separation_radius,
    )
    engine.fire_quality_alpha = float(fire_quality_alpha)
    engine.contact_hysteresis_h = float(contact_hysteresis_h)
    engine.CH_ENABLED = bool(ch_enabled)
    engine.FSR_ENABLED = bool(fsr_enabled)
    engine.fsr_strength = float(fsr_strength)
    engine.BOUNDARY_SOFT_ENABLED = bool(boundary_enabled)
    engine.BOUNDARY_HARD_ENABLED = bool(boundary_enabled)
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
    position_frames = []
    for _ in range(steps):
        state = engine.step(state)
        for fleet_id, fleet in state.fleets.items():
            print(
                f"tick={state.tick}, fleet_id={fleet.parameters.archetype_id}, alive_units={len(fleet.unit_ids)}"
            )
        for fleet_id in trajectory:
            trajectory[fleet_id].append(state.last_fleet_cohesion.get(fleet_id, 1.0))
            alive_trajectory[fleet_id].append(len(state.fleets[fleet_id].unit_ids))
        if capture_positions and frame_stride > 0 and state.tick % frame_stride == 0:
            frame = {"tick": state.tick}
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
                            )
                        )
                frame[fleet_id] = points
            position_frames.append(frame)
        if any(len(fleet.unit_ids) == 0 for fleet in state.fleets.values()):
            break
    if capture_positions:
        return state, trajectory, alive_trajectory, position_frames
    return state, trajectory, alive_trajectory
