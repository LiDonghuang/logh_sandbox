# PR9 Phase II Combat Adaptation Seam Note 20260419

Status: note only
Date: 2026-04-19
Scope: post-third-slice document-first continuation read
Authority: engineering-side design/review note for Human + governance review before any fourth runtime slice

## Purpose

This note records the next mechanism-content seam after the accepted three-slice
owner/path cleanup wave.

Current accepted read is now:

- same-tick target selection ownership is rerooted out of `resolve_combat(...)`
- upstream bridge / transition-speed shaping no longer practically depend on post-resolution `engaged*`
- locomotion consumes an explicit same-tick per-unit desire carrier

The next seam is no longer a pure owner/path reroot.
It is the smallest honest content seam where same-tick unit desire would begin to
carry actual combat-adaptation meaning.

This note does not implement that seam.
This note does not authorize a fourth slice.

## Input Anchors

- [docs/governance/PR9_Phase2_Unit_Solving_Layer_Governance_Direction_20260419.md](E:/logh_sandbox/docs/governance/PR9_Phase2_Unit_Solving_Layer_Governance_Direction_20260419.md)
- [analysis/engineering_reports/developments/20260419/pr9_phase2_unit_structure_contract_note_20260419.md](E:/logh_sandbox/analysis/engineering_reports/developments/20260419/pr9_phase2_unit_structure_contract_note_20260419.md)
- [analysis/engineering_reports/developments/20260419/pr9_phase2_simplified_unit_targeting_note_20260419.md](E:/logh_sandbox/analysis/engineering_reports/developments/20260419/pr9_phase2_simplified_unit_targeting_note_20260419.md)
- [analysis/engineering_reports/developments/20260419/pr9_phase2_locomotion_followup_note_20260419.md](E:/logh_sandbox/analysis/engineering_reports/developments/20260419/pr9_phase2_locomotion_followup_note_20260419.md)
- [analysis/engineering_reports/developments/20260419/pr9_phase2_unit_desire_bridge_bounded_implementation_slice_proposal_20260419.md](E:/logh_sandbox/analysis/engineering_reports/developments/20260419/pr9_phase2_unit_desire_bridge_bounded_implementation_slice_proposal_20260419.md)
- [analysis/engineering_reports/developments/20260419/pr9_phase2_unit_desire_bridge_third_bounded_implementation_report_20260419.md](E:/logh_sandbox/analysis/engineering_reports/developments/20260419/pr9_phase2_unit_desire_bridge_third_bounded_implementation_report_20260419.md)
- [analysis/reference_notes/eng_dev_v2_1_formation_only_a4b5ce2b7dba_dirty_baseline_capture_manifest_20260419.json](E:/logh_sandbox/analysis/reference_notes/eng_dev_v2_1_formation_only_a4b5ce2b7dba_dirty_baseline_capture_manifest_20260419.json)

Additional governance read carried into this note:

- the three-slice wave is accepted as an owner/path cleanup wave
- the next step must return to document-first
- the next seam is now a mechanism-content gate rather than a simple reroot gate
- no fourth slice is authorized before governance review of this note

## Assumptions

1. The accepted third slice is the current active starting point.
2. The current `unit_desire_by_unit` carrier remains runtime-local, tick-local,
   non-persistent, and schema-light.
3. The next honest seam should stay bounded to desire-generation semantics and
   should not broaden into doctrine-scale behavior authoring.

## Verified Current Active State

Current active truth in [runtime/engine_skeleton.py](E:/logh_sandbox/runtime/engine_skeleton.py):

- same-tick target identity is owned by `_compute_unit_intent_target_by_unit(...)`
  at [runtime/engine_skeleton.py](E:/logh_sandbox/runtime/engine_skeleton.py:3270)
- locomotion consumes `unit_desire_by_unit` inside `integrate_movement(...)` at
  [runtime/engine_skeleton.py](E:/logh_sandbox/runtime/engine_skeleton.py:2928)
- current desire content is intentionally placeholder-only:
  - `desired_heading_xy` mirrors fleet-level movement direction at
    [runtime/engine_skeleton.py](E:/logh_sandbox/runtime/engine_skeleton.py:1679)
  - `desired_speed_scale` remains `1.0` at
    [runtime/engine_skeleton.py](E:/logh_sandbox/runtime/engine_skeleton.py:1690)
- combat execution still begins only at `resolve_combat(...)` at
  [runtime/engine_skeleton.py](E:/logh_sandbox/runtime/engine_skeleton.py:3382)

Shortest plain-language read:

- target choice is already same-tick and explicit
- desire input is already same-tick and explicit
- desire content is not yet meaningfully adaptive

## Main Seam

The main seam is now:

- how same-tick target identity and local contact geometry should influence
  `desired_heading_xy` and `desired_speed_scale`
- without turning unit desire generation into a doctrine-scale mode system
- and without moving low-level realization or combat execution ownership

This seam sits exactly between:

1. target identity
2. unit desire generation
3. locomotion realization

That is the smallest honest combat-adaptation seam now remaining.

## What Would Make Unit Desire Meaningful

Current placeholder desire means:

- every unit in a fleet receives the same heading input
- every unit receives the same unity speed-scale input

For desire to become meaningfully same-tick and unit-local later, the next seam
would need to let unit desire respond to bounded local geometry such as:

- target bearing relative to fleet front axis
- target bearing relative to current unit facing
- target range / strip-gap / near-contact geometry
- local shape recovery need
- local lateral offset or broadside tendency

The key point is not to add many new signals.
It is to let the existing desire carrier stop being a mirror and start being a
bounded local read.

Smallest honest future content change:

- `desired_heading_xy` becomes a unit-local maneuver heading rather than a fleet copy
- `desired_speed_scale` becomes a bounded unit-local intent scalar rather than fixed `1.0`

## Smallest Honest Adaptation Boundary

The next seam should be read as a three-stage chain:

1. target identity
2. local adaptation read
3. locomotion realization

Meaning:

- target identity answers only "which enemy is this unit currently solving around?"
- local adaptation read answers only "how should this unit bias heading and speed this tick?"
- locomotion realization answers only "what facing / speed / velocity can actually be realized under turn-rate, accel, separation, boundary, and legality constraints?"

This separation keeps:

- target selection out of locomotion math
- locomotion realization out of doctrine authoring
- combat execution out of pre-movement adaptation choice

## Whether A Minimal Solving-Assist Vocabulary Is Needed

Current engineering read:

- a vocabulary is not strictly required for the next seam
- the preferred first read is still scalar / vector output, not named behavior states

Preferred minimal read:

- keep the runtime output carrier as:
  - `desired_heading_xy`
  - `desired_speed_scale`
- derive them from bounded local geometry directly

If a tiny human-readable vocabulary later proves necessary for code clarity or
diagnostic readability, it should remain:

- optional
- runtime-local
- tick-local
- non-persistent
- descriptive rather than authoritative

Maximum honest size for such a vocabulary:

- at most 2 or 3 ephemeral solving-assist labels

Examples of acceptable descriptive labels, if ever needed:

- `advance`
- `align_fire`
- `hold_or_slide`

These labels would only describe which weighting family produced the current
desire output.
They must not become long-lived states, planners, or trees.

## How To Prevent Vocabulary Growth Into A Behavior Tree

The next seam must keep the following guardrails:

- no persistence across ticks by default
- no transition table
- no multi-step planner
- no nested branch family that owns combat doctrine
- no label-specific sub-engines
- no carrying of retreat, morale, or doctrine memory into the same seam

Allowed read:

- same-tick geometry -> tiny bounded adaptation read -> desire carrier

Rejected read:

- same-tick geometry -> named tactical state machine -> locomotion / combat / retreat orchestration

## Separation That Must Stay Intact

The next seam must preserve the already accepted separation:

- fleet front axis != unit facing != actual velocity
- target selection != combat execution
- local combat adaptation != Formation / FR owner flow-back

Current clean read should remain:

- fleet front axis is the coarse-body / formation-facing reference
- unit facing is the realized per-unit heading
- actual velocity is the realized motion result after low-level constraints

The next seam may bias unit desire relative to fleet front.
It may not turn fleet front or Formation / FR back into the combat-adaptation owner.

## Why This Still Prepares For 3D Rather Than Accumulating 2D Patchwork

The right next seam is still preparation work for later 3D architecture because:

- it clarifies a local intention layer between target identity and motion realization
- it does not hard-code Formation or FR as combat-time doctrine carriers
- it encourages expressing local adaptation in terms of relative geometry and
  bounded desire outputs rather than ad hoc 2D patches

In later 3D work, the same conceptual seam can map onto:

- local body frame / principal-axis relations
- anisotropy-style body measures
- 3D target-bearing / closure / strip-gap equivalents

So the next seam should be designed as:

- local geometry in
- bounded desire out

not as:

- more 2D-specific combat patches stuffed into fleet movement

## Explicitly Out Of Scope

Still not authorized here:

- mode implementation
- retreat activation
- persistent target memory
- broad locomotion redesign
- Formation / FR combat-adaptation owner flow-back
- harness-owned doctrine growth
- automatic opening of a fourth slice

Also out of scope for this note:

- formula selection
- parameter naming
- threshold tuning
- multi-file implementation planning beyond the smallest seam statement

## Bottom Line

The newly identified main seam is:

- making same-tick unit desire meaningfully local without turning that seam into
  a doctrine-scale behavior system

The current clean boundary should be kept as:

- target identity chooses who
- unit desire generation biases how to move this tick
- locomotion realizes what is physically achieved

Anything beyond that remains out of scope until a new governance review opens a
fourth slice.
