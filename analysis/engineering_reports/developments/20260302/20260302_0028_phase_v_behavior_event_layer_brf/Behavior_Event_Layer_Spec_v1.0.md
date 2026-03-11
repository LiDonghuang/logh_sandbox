# Behavior Event Layer Spec v1.0

## Scope
Diagnostic/observer layer only. No runtime behavior modification.

## Parameter Capture Contract
- This report pack persists an execution-parameter snapshot in:
  - `analysis/engineering_reports/20260302_0028_phase_v_behavior_event_layer_brf/behavior_event_layer_summary_v1_0.json`
- Required keys include:
  - `attack_range`, `min_unit_spacing`, `arena_size`, `max_time_steps_effective`, `unit_speed`, `damage_per_tick`
  - `ch_enabled`, `contact_hysteresis_h`, `fsr_enabled`, `fsr_strength`, `boundary_enabled`
- Fields with execution override record both `settings_value` and `effective_value`.

## Timeline Log Contract (Per Tick, Per Side)
- Required columns:
  - `tick`
  - `side`
  - `alive_units`
  - `fleet_size_hp` (sum of alive unit HP)
  - `fleet_size_ships_ceil` (`ceil(fleet_size_hp)`)
  - `LCC_ratio`
  - `cohesion_v2`
  - `cohesion_v1_shadow_enemy` (if shadow path is enabled)
  - `collapse_event_v2`
  - `collapse_event_vuln_shadow`
  - `deep_pursuit`
  - `damage_events_count`
  - `event_flags`

## Narrative Output Contract (CN)
- Use battle title line first: `<SeedWord> 星域会战`.
- Use English punctuation in CN output: `:` and `()`.
- Commander line format: `<CommanderA>(A) vs <CommanderB>(B)`.
- Initial force line format: `<FleetA>舰队: <ships_A>艘 (A: <units_A> units); <FleetB>舰队: <ships_B>艘 (B: <units_B> units)`.
- Final outcome line must reference rounded-up ship counts:
  - `ceil(fleet_size_hp)` and append unit count in parentheses, e.g. `(B units=15)`.

## Tier 1 Events
- `FirstContactTick`: first tick with `damage_events_count > 0`.
- `FirstKillTick`: first tick where total alive units decreases.
- `InflectionTick`: first sign change of 20-tick rolling average of `(AliveA - AliveB)`.
- `EndgameOnsetTick`: first tick where either side alive <= 20% of initial alive.
- `EndTick`: final tick.
- `Winner`: side with higher final alive (or `Draw`).

## Tier 2 Events
- `FormationCutEvent`:
  - window `Delta = 10` ticks.
  - trigger when `LCC_ratio` drop >= `epsilon = 0.20` within window.
  - output: `CutStartTick`, `MaxDrop`, `Duration`.
- `PocketEncirclementEvent`:
  - secondary component size >= 3 persists >= 20 ticks.
  - isolation condition: secondary centroid distance from main centroid >= `2 * separation_radius`.
  - output: `PocketStartTick`, `PocketDuration`, `PocketResolutionType` (`Reintegration`/`Destroyed`/`Persistent`).
- `DeepPenetrationEvent`:
  - penetration ratio >= 0.10 for >= 10 ticks.
  - penetration ratio: fraction of own units crossing enemy-centroid line along own->enemy centroid axis.
  - output: `PenetrationStartTick`, `PenetrationDuration`.

## Tier 3 Observables
- `PursuitModeOnsetTick`: first tick with collapse condition true.
- `CollapseEventTick_v2`: first tick with `enemy_cohesion_v2 < PD_norm`.
- `CollapseEventTick_vuln_shadow`: first tick with `enemy_cohesion_v1_shadow < PD_norm`.

## Determinism Considerations
- Observer computes from deterministic runtime state.
- No random branch, no smoothing, no future-state peeking.

## Known Limitations
- Pocket identity is component-level, not persistent per-unit topology tracking.
- Formation-cut duration uses recovery threshold `base_lcc - epsilon/2`.
- Timeline outputs are generated for required representative cases by default.
