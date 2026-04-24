## PR9 Phase II - Combat Damage Scalar Freeze-to-One Correction

Date: 2026-04-20  
Scope: runtime combat correction  
Status: local correction candidate after post-change battle review

### 1. What changed

This correction withdraws the temporary `hp_fire_scale` damage substitution from
the active combat path and freezes the combat damage scalar to `1.0`.

Active owner/path:

- `runtime/engine_skeleton.py`
  - `EngineTickSkeleton.resolve_combat(...)`

Current active damage read after this correction:

- `event_damage = damage_per_tick * angle_quality * range_quality`

### 2. Why this correction was needed

The immediately previous local candidate replaced the legacy fleet-level
`coupling` term with:

- `hp_fire_scale = clamp(current_hp / max_hp, 0.0, 1.0)`
- `event_damage = damage_per_tick * hp_fire_scale * angle_quality * range_quality`

Post-change review on `battle_36v36` showed that this created a maintained-path
behavior problem in the later combat window.

Engineering read:

- units kept occupying contact / geometry space
- but damaged units lost outgoing fire power directly through HP scaling
- this produced a one-sided reciprocal-engagement collapse in the mid-to-late
  battle rather than a clean or symmetric degradation

This means the `hp_fire_scale` candidate is **not** accepted as the maintained
mainline fire model.

### 3. Correction read

The current correction keeps:

- removal of the legacy fleet participation `coupling` term
- the public rename to `fire_angle_quality_alpha`

The current correction removes:

- `hp_fire_scale` from active damage

This leaves the active scalar path intentionally minimal:

- base damage
- angle quality
- range quality

### 4. What did not change

This correction does not change:

- target-selection ownership
- `resolve_combat(...)` stage ownership
- `fire_angle_quality_alpha` naming
- `fire_optimal_range_ratio`
- `fire_cone_half_angle_deg`
- locomotion / local desire
- `BattleState` schema

### 5. Relationship to the prior record

This document supersedes the active-runtime recommendation in:

- `pr9_phase2_combat_coupling_replacement_hp_scaled_fire_and_angle_quality_rename_record_20260420.md`

Historical note:

- that earlier record remains useful as an implementation trace of the tested
  candidate
- it should **not** be read as the accepted maintained combat-model outcome

### 6. Validation

Static check:

- `python -m py_compile runtime/engine_skeleton.py`

Narrow smoke:

- maintained active path, `steps=120`
- result:
  - `final_tick = 120`
  - `first_contact_tick = 61`
  - `first_damage_tick = 61`
  - `engaged_count_final = 14`

Paired baseline review:

- anchor:
  - `analysis/reference_notes/eng_dev_v2_1_formation_only_a4b5ce2b7dba_dirty_*.json`
- replay note:
  - baseline captures predate explicit `local_desire_*` storage
  - comparison replay explicitly injected the current maintained accepted
    `local_desire_*` values

Summary result:

- `neutral_36`
  - exact match
- `neutral_100`
  - exact match
- `battle_36v36`
  - drift remains
  - final:
    - baseline `A alive=25 hp=1779.327760`, `B alive=27 hp=1844.239022`
    - current `A alive=28 hp=2106.809046`, `B alive=27 hp=2200.015838`
- `battle_100v100`
  - drift remains
  - final:
    - baseline `A alive=72 hp=5534.064357`, `B alive=67 hp=5277.515490`
    - current `A alive=68 hp=5344.369009`, `B alive=65 hp=5181.952767`

Late-window battle read for `battle_36v36`:

- in the `tick 190..205` window, current contact collapses to near-zero
  much earlier than baseline
- representative example:
  - `tick 190`
    - baseline `in_contact_count = 15`
    - current `in_contact_count = 0`
  - `tick 200`
    - baseline `in_contact_count = 18`
    - current `in_contact_count = 0`

### 7. Current read

This correction is mechanically valid but is **not yet accepted** as the
maintained combat-model outcome.

Engineering read after validation:

- freezing the scalar to `1.0` removes both the old fleet-level `coupling` and
  the temporary `hp_fire_scale`
- but on the current maintained battle path it also collapses late contact too
  aggressively relative to the accepted baseline
- so this candidate should currently be read as an investigated correction path,
  not as the new maintained baseline
