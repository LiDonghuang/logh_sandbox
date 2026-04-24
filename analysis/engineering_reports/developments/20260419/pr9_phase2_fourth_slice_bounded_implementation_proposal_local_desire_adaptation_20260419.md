# PR9 Phase II Fourth Slice Bounded Implementation Proposal - Local Desire Adaptation

Status: proposal only
Date: 2026-04-19
Scope: bounded implementation proposal after the accepted three-slice owner/path cleanup wave
Authority: engineering proposal for Human + governance review before any fourth runtime slice

## Purpose

This proposal defines the next smallest honest implementation slice after the accepted:

- first slice: same-tick target selection reroot
- second slice: upstream unit-intent bridge reroot
- third slice: explicit locomotion desire-carrier reroot

Current accepted read is:

- same-tick target identity already exists
- same-tick desire carrier already exists
- desire content is still placeholder-only

So the next seam is no longer ownership.
It is local desire content.

This proposal does not authorize implementation by itself.

## Input Anchors

- [analysis/engineering_reports/developments/20260419/pr9_phase2_combat_adaptation_seam_note_20260419.md](E:/logh_sandbox/analysis/engineering_reports/developments/20260419/pr9_phase2_combat_adaptation_seam_note_20260419.md)
- [analysis/engineering_reports/developments/20260419/pr9_phase2_unit_desire_bridge_third_bounded_implementation_report_20260419.md](E:/logh_sandbox/analysis/engineering_reports/developments/20260419/pr9_phase2_unit_desire_bridge_third_bounded_implementation_report_20260419.md)
- [analysis/engineering_reports/developments/20260419/pr9_phase2_unit_desire_bridge_bounded_implementation_slice_proposal_20260419.md](E:/logh_sandbox/analysis/engineering_reports/developments/20260419/pr9_phase2_unit_desire_bridge_bounded_implementation_slice_proposal_20260419.md)
- [analysis/engineering_reports/developments/20260419/pr9_phase2_simplified_unit_targeting_note_20260419.md](E:/logh_sandbox/analysis/engineering_reports/developments/20260419/pr9_phase2_simplified_unit_targeting_note_20260419.md)
- [analysis/reference_notes/eng_dev_v2_1_formation_only_a4b5ce2b7dba_dirty_baseline_capture_manifest_20260419.json](E:/logh_sandbox/analysis/reference_notes/eng_dev_v2_1_formation_only_a4b5ce2b7dba_dirty_baseline_capture_manifest_20260419.json)

Governance read carried into this proposal:

- fourth slice is not yet authorized
- proposal must stay on the same-tick local desire content seam only
- no widening into doctrine expansion, locomotion rewrite, or tactical state machinery
- scalar / vector output remains preferred over named mode

## Assumptions

1. The current active starting point is the accepted third slice.
2. The fourth slice should remain inside `runtime/engine_skeleton.py` unless a narrower option proves impossible.
3. The existing `unit_desire_by_unit` carrier shape should remain unchanged by default:
   - `desired_heading_xy`
   - `desired_speed_scale`
4. The fourth slice should not alter accepted target-selection, combat-execution, or locomotion-realization ownership.

## Exact Owner / Path Proposed For Change

Exact owner/path proposed for change:

- only same-tick local desire content generation in
  `runtime/engine_skeleton.py`
- specifically:
  - `EngineTickSkeleton._compute_unit_desire_by_unit(...)`

Concrete active references:

- current placeholder desire generation begins at
  [runtime/engine_skeleton.py](E:/logh_sandbox/runtime/engine_skeleton.py:1659)
- locomotion consumes the carrier at
  [runtime/engine_skeleton.py](E:/logh_sandbox/runtime/engine_skeleton.py:2928)

What this proposal does **not** change:

- not target-selection ownership
- not `resolve_combat(...)` ownership
- not broad locomotion-family ownership
- not the carrier shape consumed by `integrate_movement(...)`

Shortest implementation read:

- change who computes desire content
- do not change who owns selection, combat, or realization

## Verified Current Placeholder State

Current active behavior is:

- `desired_heading_xy` mirrors fleet movement direction
- `desired_speed_scale` is fixed at `1.0`

Current active evidence:

- [runtime/engine_skeleton.py](E:/logh_sandbox/runtime/engine_skeleton.py:1679)
- [runtime/engine_skeleton.py](E:/logh_sandbox/runtime/engine_skeleton.py:1690)

So the fourth slice does not need a new carrier.
It needs a bounded content update inside the existing carrier.

## Smallest Honest Local-Geometry Inputs

This proposal recommends exactly three local signals for the first adaptation cut.

### 1. Target bearing relative to fleet front

Purpose:

- lets unit desire know whether the selected target sits near the fleet advance axis
  or laterally off that axis
- allows bounded lateral/firing alignment without making fleet front the combat owner

Representative read:

- use current fleet front / coarse heading as a reference frame only
- compare that reference with same-tick `attack_hat_xy`

### 2. Target bearing relative to current unit facing

Purpose:

- measures immediate turn need for this unit
- gives the smallest honest local signal for whether speed should stay high or be
  temporarily reduced while reorienting

Representative read:

- compare `attack_hat_xy` with current unit `orientation_vector`

### 3. Target range / near-contact relation

Purpose:

- keeps adaptation dormant when local contact geometry is not yet relevant
- prevents early broad adaptation during pure transit

Representative read:

- use selected-target distance relative to attack range
- or a same-tick near-contact gate derived from equivalent existing local geometry

Why only these three:

- one axis-reference signal
- one unit-turn signal
- one proximity gate

This is enough to open meaningful local desire adaptation without introducing a
large signal catalog.

## Minimal Output Change Proposed

### A. Desired heading

Proposed fourth-slice read:

- base heading remains the current fleet-mirrored desire heading
- if the unit has a same-tick selected target and near-contact gate is active,
  compute a bounded local heading bias toward the target bearing
- apply that bias as a small relax from base heading rather than a full replacement

Preferred bounded shape:

```text
desired_heading_xy =
    relax(base_fleet_heading_xy, attack_hat_xy, local_heading_bias_weight)
```

Where `local_heading_bias_weight` is:

- zero when no same-tick target exists
- zero when near-contact relation is inactive
- bounded above by a small cap

So the fourth slice changes:

- from fleet-copy heading
- to bounded target-aware local heading bias

It does not change:

- the downstream locomotion vector family
- turn-rate limiting
- separation / boundary / legality handling

### B. Desired speed scale

Proposed fourth-slice read:

- base `desired_speed_scale` remains `1.0`
- if same-tick target exists and near-contact gate is active, reduce speed only when
  unit-turn need is materially high

Preferred bounded shape:

```text
desired_speed_scale =
    1.0 - (near_contact_gate * turn_need * speed_brake_strength)
```

Then clamp into a bounded interval such as:

- `[speed_floor, 1.0]`

Preferred minimal read:

- speed adaptation is brake-only in the first content slice
- no upstream boost / sprint family is introduced

Why this stays small:

- heading gets a bounded local bias
- speed gets a bounded local brake
- both remain same-tick, local, scalar/vector outputs only

## What Still Does Not Change

The fourth-slice proposal keeps the following unchanged:

- no mode implementation by default
- no retreat activation
- no persistent target memory
- no broad locomotion redesign
- no Formation / FR combat-adaptation owner flow-back
- no harness-owned doctrine growth
- no carrier shape expansion by default
- no `BattleState` schema expansion by default
- no new owner for `resolve_combat(...)`
- no new owner for target selection

## Why This Slice Remains Smaller Than A Doctrine Wave

This slice remains below:

- combat-adaptation family implementation
- locomotion rewrite
- tactical state system

because it changes only:

- one helper's same-tick local content generation
- inside one existing carrier
- with three bounded local inputs
- and two existing scalar/vector outputs

It does not add:

- persistent state
- named tactical states
- multi-step planning
- cross-tick transitions
- retreat semantics
- additional owner reroots

Shortest plain-language read:

- this slice would make desire content slightly smarter
- it would not make the system doctrinally larger

## Named Vocabulary Position

Preferred proposal baseline remains:

- scalar / vector output first
- no named mode unless strictly necessary

So this proposal does **not** recommend a named solving-assist vocabulary for the
fourth slice by default.

If later review concludes that a tiny descriptive label is unavoidable for debug
readability, it must remain:

- optional
- runtime-local
- tick-local
- non-persistent
- descriptive only

and must not be consumed as a control owner.

## Proposed Validation Posture If Later Authorized

If governance later authorizes implementation, the fourth slice should report with:

- static owner/path audit
- compile check
- narrow smoke
- paired baseline review against the current Phase II primary baselines
- explicit explanation of any behavior drift before any fifth-slice discussion

Because this slice would begin to modify real desire content, battle and neutral
reviews should both be treated as required.

## Rejection Rule

Reject any implementation derived from this proposal if it silently widens from:

- bounded local desire adaptation

into:

- mode system introduction
- retreat pre-activation
- broad locomotion redesign
- new tactical state ownership
- Formation / FR combat-time owner flow-back

## Bottom Line

The fourth slice, if later authorized, should do only this:

- make `unit_desire_by_unit` locally meaningful using three bounded same-tick
  geometry signals
- bias `desired_heading_xy`
- brake `desired_speed_scale` when turn need near contact is high

and should do nothing larger than that.
