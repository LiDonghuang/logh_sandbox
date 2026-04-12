# PR6 / dev_v2.1 `v4a` Movement Owner Truth Map

Status: current-state truth map  
Date: 2026-04-05  
Scope: `v4a` movement only  
Authority: working truth map; not final cleanup completion

## 1. `v4a` runtime hot path: remaining personality parameters

After the current first cut:

- active `v4a` runtime movement restore term no longer reads:
  - `formation_rigidity`
  - `pursuit_drive`
  - `mobility_bias`

Current runtime read for `v4a` movement restore is now:

- `restore_term = restore_strength * normalize(restore_vector)`

with:

- `restore_vector = expected_position - unit.position`
  - or `centroid - unit.position` when no expected position is active

Still true outside this narrow `v4a` movement read:

- older/non-`v4a` runtime lines still use personality parameters
- `formation_rigidity` still exists elsewhere in the repo surface
- this map only states the current `v4a` movement hot-path truth

## 2. What battle currently has that neutral does not

Current `battle` transition realization still carries extra pre-runtime
movement modulation that `neutral` does not materially share:

- `battle_relation_gap_current` override on `advance_share`
- `battle_relation_gap_current` override on `last_target_direction`
- near-contact internal stability blending:
  - `battle_near_contact_internal_stability_blend`
  - `battle_near_contact_speed_relaxation`
- engagement / attack-direction speed modulation:
  - `engaged_speed_scale`
  - `attack_speed_lateral_scale`
  - `attack_speed_backward_scale`
  - `engagement_geometry_active_current`

That meant `battle` transition realization was not just:

- expected-position geometry
- shape error
- forward transport need
- heading realization

It still carries extra battle-only speed authority.

## 3. Current truthful read

This round does **not** remove those battle-only transition-speed modifiers.

So current truthful read is:

- `battle` and `neutral` do not yet share fully identical transition mechanics
- `restore_strength` decoupling and `formation_rigidity` removal are separate
  from the still-live battle-only transition family

## 4. What remains to audit after this cut

This truth map does **not** finish the whole `v4a` movement cleanup.

Still pending:

- how neutral should honestly inherit the same transition-mechanism family
  without deleting the established battle line
- whether any remaining battle/neutral opening difference comes from
  upstream bundle generation, not just the transition block
- later old-family retirement after ownership truth is stable
