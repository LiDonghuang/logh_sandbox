# Behavior Event Layer Spec v1.0

## Scope
Diagnostic and observer layer only. No runtime behavior modification is authorized.

## Normative References
- `analysis/engineering_reports/_standards/Battle_Report_Framework_v1.0.template.md`
- `analysis/engineering_reports/_standards/BRF_Export_Standard_v1.0.md`

## Report Pack Storage Rule
- Engineering report packs must be archived under:
  - `analysis/engineering_reports/developments/YYYYMMDD/<pack>/`
- `analysis/engineering_reports/_standards/` is for templates and reusable standards only.

## Parameter Capture Contract
Each report pack summary JSON must include:
- `settings_path`
- `attack_range`
- `min_unit_spacing`
- `arena_size`
- `max_time_steps_effective`
- `unit_speed`
- `damage_per_tick`
- `ch_enabled`
- `contact_hysteresis_h`
- `fsr_enabled`
- `fsr_strength`
- `boundary_enabled`

If runtime applies overrides, include both `settings_value` and `effective_value` for each overridden field.

## Timeline Log Contract (Per Tick, Per Side)
Required columns:
- `tick`
- `side`
- `alive_units`
- `fleet_size_hp` (sum of alive unit HP)
- `fleet_size_ships_ceil` (`ceil(fleet_size_hp)`)
- `LCC_ratio`
- `cohesion_v2`
- `cohesion_v3_shadow` (when enabled)
- `collapse_event_v2`
- `collapse_v2_shadow`
- `deep_pursuit`
- `damage_events_count`
- `event_flags`

## Tier 1 Events
- `FirstContactTick`: first tick where contact condition is true.
- `FirstKillTick`: first tick where total alive units decreases.
- `InflectionTick`: first strategic advantage reversal tick after persistence filtering.
- `EndgameOnsetTick`: first tick where either side reaches endgame ratio threshold.
- `EndTick`: final tick.
- `Winner`: side with higher final alive units (or `Draw`).

## Tier 2 Events
- `FormationCutEvent`: split/formation-cut event derived from approved event detector policy.
- `PocketEncirclementEvent`: pocket/envelopment event derived from approved event detector policy.
- `DeepPenetrationEvent`: deep-penetration event if enabled by current observer/event contract.

## Tier 3 Observables
- `PursuitModeOnsetTick`
- `CollapseEventTick_v2`
- `CollapseEventTick_shadow`

## Determinism Considerations
- Observer/event computation must be deterministic and derived from deterministic runtime state.
- No random branch and no future-state peeking.

## Tick Semantics
- `t=0` is snapshot only.
- Event detection uses `t>=1`.
