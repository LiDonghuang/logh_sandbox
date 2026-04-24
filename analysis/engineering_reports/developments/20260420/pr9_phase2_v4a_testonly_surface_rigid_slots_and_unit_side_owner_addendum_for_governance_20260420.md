## PR9 Phase II - V4A Testonly Surface, `rigid_slots`, And Unit-Side Owner Addendum For Governance

Date: 2026-04-20  
Scope: detailed addendum for Human + Governance review only  
Status: document-only; no implementation in this note

### 1. Opening summary

This addendum answers three practical questions before any new movement or
`local_desire` slice is opened:

1. what the current `rigid_slots` branch really does on the active path, so
   Human + Governance can decide whether it should continue to exist
2. which current `v4a` mechanism families are no longer best read as
   fleet/reference owners and should instead be re-understood as Unit-side
   maneuver / restraint owners
3. whether still-experimental mechanism families such as `local_desire` should
   continue to live on the runtime public surface or first move into
   `testonly` under explicit switches

Shortest engineering read:

- `rigid_slots` is not dead code; it is still a real legacy reference-surface
  branch
- the most obvious Unit-side migration candidates are the current per-unit
  attack-direction speed and near-contact internal speed-restraint seams
- `testonly` policy now needs an explicit governance read, because some
  currently active surfaces are better described as experimental than
  maintained doctrine

### 2. Boundary and active-path reminder

This note does **not** propose or perform:

- a runtime slice
- a module split
- a settings migration
- a new Unit layer implementation
- a `local_desire` redesign implementation

It is only a code-path / owner review.

Relevant active path:

- public settings maps:
  [test_run/settings_accessor.py](<E:/logh_sandbox/test_run/settings_accessor.py:34>)
- scenario-side required reads:
  [test_run/test_run_scenario.py](<E:/logh_sandbox/test_run/test_run_scenario.py:526>)
- execution-side bundle wiring:
  [test_run/test_run_execution.py](<E:/logh_sandbox/test_run/test_run_execution.py:448>)
- runtime reference surface:
  [runtime/engine_skeleton.py](<E:/logh_sandbox/runtime/engine_skeleton.py:914>)
- runtime v4a bridge / transition speed:
  [runtime/engine_skeleton.py](<E:/logh_sandbox/runtime/engine_skeleton.py:1263>)
  and
  [runtime/engine_skeleton.py](<E:/logh_sandbox/runtime/engine_skeleton.py:1440>)
- runtime `local_desire`:
  [runtime/engine_skeleton.py](<E:/logh_sandbox/runtime/engine_skeleton.py:1662>)

### 3. `rigid_slots` - current mechanism, in plain language

#### 3.1 Where `rigid_slots` lives

Current public surface:

- `runtime.movement.v4a.reference.surface_mode`

Current test-only layer source:

- [test_run/test_run_v1_0.testonly.settings.json](<E:/logh_sandbox/test_run/test_run_v1_0.testonly.settings.json:1>)

Current validator / required read:

- [test_run/test_run_scenario.py](<E:/logh_sandbox/test_run/test_run_scenario.py:537>)

Current execution-side bundle carry:

- [test_run/test_run_execution.py](<E:/logh_sandbox/test_run/test_run_execution.py:449>)
  and
  [test_run/test_run_execution.py](<E:/logh_sandbox/test_run/test_run_execution.py:535>)

Current runtime owner:

- [runtime/engine_skeleton.py](<E:/logh_sandbox/runtime/engine_skeleton.py:1047>)

#### 3.2 What `rigid_slots` actually does

`rigid_slots` is not just a legacy label. It still selects a real reference
surface behavior.

Current read:

- runtime first computes the fleet centroid and a resolved forward axis
- it also computes current local offsets of alive units relative to that axis
- then it checks `reference_surface_mode`
- if the mode is **not** `soft_morphology_v1`, runtime immediately returns the
  precomputed `expected_slot_offsets_local`

Concrete owner branch:

- [runtime/engine_skeleton.py](<E:/logh_sandbox/runtime/engine_skeleton.py:1047>)
- [runtime/engine_skeleton.py](<E:/logh_sandbox/runtime/engine_skeleton.py:1050>)

In plain language:

- `rigid_slots` says:
  - "the fleet's reference shape is still the original reference slot pattern"
  - "alive units should still be judged against that fixed slot map"
  - "do not morph the reference body itself to follow casualties or shape
    shrinkage"

The slot map it returns comes from `expected_slot_offsets_local`, which is
built earlier from the reference layout:

- [test_run/test_run_execution.py](<E:/logh_sandbox/test_run/test_run_execution.py:814>)

So `rigid_slots` is a real "fixed reference slots" branch, not a no-op.

#### 3.3 What `rigid_slots` skips

If `rigid_slots` is chosen, runtime returns early before entering the
soft-morphology path.

That means it skips all of the following:

- alive-ratio-driven target scale shrink
- current vs target forward/lateral extent relaxation
- morphology-center relaxation
- center/wing differential update
- per-unit material phase relaxation
- updated expected offsets reconstructed from current morphology state

All of those only happen in the `soft_morphology_v1` branch:

- [runtime/engine_skeleton.py](<E:/logh_sandbox/runtime/engine_skeleton.py:1058>)
- [runtime/engine_skeleton.py](<E:/logh_sandbox/runtime/engine_skeleton.py:1102>)
- [runtime/engine_skeleton.py](<E:/logh_sandbox/runtime/engine_skeleton.py:1157>)
- [runtime/engine_skeleton.py](<E:/logh_sandbox/runtime/engine_skeleton.py:1193>)

So the real distinction is:

- `rigid_slots`
  - fixed slot reference geometry
- `soft_morphology_v1`
  - living reference surface that shrinks / relaxes / re-materializes with
    battle state

#### 3.4 Why Human + Governance may want to retire it

Reasons to retire `rigid_slots`:

- the maintained mainline has already moved conceptually toward soft
  morphology, not rigid slot preservation
- keeping both branches means reference-surface ownership is still exposed as a
  selector even if one branch is already the real maintained direction
- this creates an avoidable legacy selector on a very important seam

#### 3.5 Why Human + Governance may want to keep it for now

Reasons to keep `rigid_slots` a little longer:

- it is still a genuine fallback branch, not dead code
- it remains useful as a diagnostic contrast point for "fixed reference body"
  versus "living reference surface"
- removing it is not just key deletion; it is a governance decision that the
  maintained v4a family no longer needs the rigid reference interpretation at
  all

#### 3.6 Engineering recommendation on `rigid_slots`

Engineering recommendation:

- do **not** silently remove it
- let Human + Governance decide explicitly whether the project still wants to
  preserve a fixed-slot reference-surface interpretation

If the decision is:

- "`rigid_slots` is no longer wanted"

then the clean next move would be:

- retire the selector
- freeze reference-surface semantics to `soft_morphology_v1`

If the decision is:

- "`rigid_slots` should remain as a deliberate diagnostic / comparison branch"

then it should be described honestly as:

- legacy-but-still-live reference-surface branch

not as a dead leftover.

### 4. Which current `v4a` mechanisms look like Unit-side owners

#### 4.1 High-level classification

Current `v4a` surfaces fall into three conceptual groups:

1. Fleet/reference ownership
2. Mixed bridge / battle-context ownership
3. Per-unit maneuver / restraint ownership

The third group is the one that most strongly argues for Unit-side ownership.

#### 4.2 Fleet/reference ownership - should stay fleet-side

These are still best read as fleet/reference owners:

- `runtime.movement.v4a.restore.strength`
- `runtime.movement.v4a.reference.expected_reference_spacing`
- `runtime.movement.v4a.reference.layout_mode`
- `runtime.movement.v4a.reference.surface_mode`
- `runtime.movement.v4a.reference.soft_morphology_relaxation`
- `runtime.movement.v4a.transition.shape_vs_advance_strength`
- `runtime.movement.v4a.transition.heading_relaxation`
- `runtime.movement.v4a.battle.standoff_hold_band_ratio`
- `runtime.movement.v4a.battle.target_front_strip_gap_bias`
- `runtime.movement.v4a.battle.hold_weight_strength`
- `runtime.movement.v4a.battle.relation_lead_ticks`
- `runtime.movement.v4a.battle.hold_relaxation`
- `runtime.movement.v4a.battle.approach_drive_relaxation`

Why they should stay there:

- they define fleet body reference geometry
- they define fleet-to-fleet relation and standoff context
- they are upstream envelope/context producers
- they are not direct per-unit maneuver decisions

In short:

- these are things the fleet body should know first
- Unit logic may consume their outputs later, but should not own them directly

#### 4.3 Strong Unit-side migration candidates

These are the strongest Unit-side migration candidates:

- `runtime.movement.v4a.engagement.engaged_speed_scale`
- `runtime.movement.v4a.engagement.attack_speed_lateral_scale`
- `runtime.movement.v4a.engagement.attack_speed_backward_scale`
- `runtime.movement.v4a.battle.near_contact_internal_stability_blend`
- `runtime.movement.v4a.battle.near_contact_speed_relaxation`

Current active consumer:

- [runtime/engine_skeleton.py](<E:/logh_sandbox/runtime/engine_skeleton.py:1474>)
- [runtime/engine_skeleton.py](<E:/logh_sandbox/runtime/engine_skeleton.py:1492>)
- [runtime/engine_skeleton.py](<E:/logh_sandbox/runtime/engine_skeleton.py:1597>)
- [runtime/engine_skeleton.py](<E:/logh_sandbox/runtime/engine_skeleton.py:1622>)

#### 4.4 Why these look Unit-side

These parameters are already used in a per-unit read:

- for each unit, runtime checks the selected target
- computes target direction relative to that unit
- compares target direction to that unit's current facing
- computes that unit's attack-direction-aware speed allowance
- then smooths that unit's max-speed target

That is not reference geometry anymore.

That is already:

- unit-local maneuver allowance
- unit-local speed restraint
- unit-local near-contact stabilization

In human terms:

- this is no longer "what shape should the fleet want to hold?"
- this is "how much freedom should this particular unit have to move while
  engaging its target under current battle restraint?"

That is exactly why these look mis-housed under a generic `v4a.engagement` or
`v4a.battle` umbrella.

### 5. Initial bounded plan for Unit-side migration

This is **not** a request to implement now. It is only an initial ownership
plan.

#### 5.1 What should stay unchanged initially

Stay unchanged for the first bounded migration step:

- no file/module split
- no new Unit layer file
- no second target source
- no mode / no retreat / no persistent memory
- fleet-side battle/context signals remain produced where they are today

#### 5.2 What should change conceptually first

The first move should be an owner clarification, not a physical extraction.

Conceptual read:

- fleet/battle side continues to compute:
  - standoff relation
  - hold pressure
  - approach / brake context
  - reference geometry
- Unit side should consume:
  - `selected_target_by_unit`
  - unit facing
  - fleet-provided battle context
  - then produce per-unit speed restraint / attack-direction allowance

In other words:

- fleet side produces the envelope
- Unit side produces the actual local maneuver response inside that envelope

#### 5.3 What a first bounded migration slice could look like later

If later authorized, a bounded migration slice could be framed like this:

1. keep current files and carriers
2. reclassify the following functionally as Unit-side responsibilities:
   - attack-direction speed allowance
   - near-contact speed restraint smoothing
3. stop describing those knobs as generic `v4a.engagement` doctrine knobs
4. treat them as the first Unit maneuver/restraint seam, even if they still
   temporarily live in the same file

That would let the project move ownership first without violating the current
"no module split yet" boundary.

#### 5.4 Why this is the right first migration target

Reason:

- these mechanisms are already active, already behavior-bearing, and already
  reading unit-local geometry
- so the migration is not speculative; it is aligning owner language to current
  runtime reality

Compared with trying to move reference/morphology first:

- reference/morphology is still fundamentally fleet-body work
- forcing that down to Unit side too early would blur the architecture

### 6. `testonly` question - especially for `local_desire`

#### 6.1 Current state

Current layering rule:

- base settings file loads:
  1. runtime layer
  2. test-only layer

Owner:

- [test_run/settings_accessor.py](<E:/logh_sandbox/test_run/settings_accessor.py:149>)

Current reality is mixed:

- many `v4a` mainline knobs still live in `testonly`
- but `local_desire` currently lives in runtime settings:
  - [test_run/test_run_v1_0.runtime.settings.json](<E:/logh_sandbox/test_run/test_run_v1_0.runtime.settings.json:64>)

And `local_desire` is not fully settled maintained doctrine:

- it is currently frozen behind an explicit temporary switch
- owner record:
  [pr9_phase2_local_desire_temporary_freeze_switch_record_20260420.md](<E:/logh_sandbox/analysis/engineering_reports/developments/20260420/pr9_phase2_local_desire_temporary_freeze_switch_record_20260420.md:1>)

#### 6.2 Why this deserves a governance question

The current situation is architecturally awkward in both directions:

- some mature-enough active v4a mechanism surfaces still look "test-only"
- some still-experimental mechanism surfaces already look "runtime-maintained"

That creates surface-honesty drift.

Your suggestion is directionally reasonable:

- mechanisms still under active concept review, such as `local_desire`, may
  belong in `testonly` first
- and future new mechanism families may likewise start in `testonly` with
  explicit switches and safe defaults

#### 6.3 Engineering read on `local_desire`

Engineering view:

- yes, `local_desire` is a good candidate for governance review on whether it
  should live in `testonly` while concept work is still open
- but this should be a governance call, not a silent cleanup move

Reason for caution:

- the current maintained working anchor still runs through the existing
  `local_desire` layer/carrier
- so moving the whole surface now would not be a cosmetic config cleanup
- it would be a public settings-boundary change during an already sensitive
  mechanism review phase

#### 6.4 Governance questions worth asking explicitly

Suggested governance questions:

1. Should still-experimental mechanism families default to `testonly` until
   they are accepted as maintained doctrine?
2. Should future new mechanism families enter first through `testonly` with:
   - explicit public switch
   - safe default
   - no silent fallback
3. For the already-existing `local_desire` family:
   - should it now be rehomed into `testonly`
   - or should that wait until the next concept-reset cycle is resolved, to
     avoid unnecessary public-surface churn?

#### 6.5 Engineering recommendation on this policy question

Engineering recommendation:

- ask Governance explicitly
- do **not** move `local_desire` preemptively

My preferred policy direction is:

- new experimental behavior-bearing mechanism families should generally start in
  `testonly`
- they should ship with explicit switches and safe defaults
- they should be promoted to runtime public surface only after governance
  acceptance of a working maintained read

For the already-existing `local_desire` family, I would still ask Governance
whether to:

- move it now for honesty
- or leave it where it is temporarily, because the freeze switch already makes
  the experimental branch explicit and safe

### 7. Step-by-step sequencing recommendation

I agree with your boundary rule:

- finish one step before opening the next

Recommended sequence:

1. Human + Governance decide whether `rigid_slots` remains a live supported
   reference-surface branch
2. Human + Governance decide whether experimental mechanism families should
   default to `testonly`, and whether `local_desire` should be moved there now
3. only after those settings-boundary decisions are made:
   - write one bounded owner-clarification proposal for the Unit-side migration
     candidates
4. only after that:
   - consider a bounded implementation slice

What I would avoid:

- deciding `rigid_slots`
- rehoming `local_desire`
- and opening a Unit-side migration slice

all in the same turn or same governance bundle.

### 8. Additional engineering suggestions

#### 8.1 Suggestion A - classify public knobs by status, not just by layer

Right now the real confusion is not only path location. It is status clarity.

I recommend a simple governance-level classification for public knobs:

- maintained runtime
- experimental behind explicit switch
- legacy branch pending retirement

That would make future cleanup and promotion decisions much easier.

#### 8.2 Suggestion B - treat owner migration before file migration

For the Unit-side candidates, do not start with file extraction.

Start with:

- owner declaration
- public-surface classification
- one bounded proposal

Only later, if still justified, discuss physical split.

#### 8.3 Suggestion C - be careful with partial `testonly` migration

If Governance decides "new experimental families should first live in
`testonly`", I would still avoid a rushed half-move where:

- some `local_desire` keys move
- some stay in runtime
- and the meaning of the switch gets muddier

If `local_desire` is moved, it should be done as one deliberate surface
reclassification, not piecemeal.

### 9. Short closing read for Governance

Shortest governance-facing read:

- `rigid_slots` is still a real legacy reference-surface branch, not dead code
- the strongest Unit-side migration candidates are the current per-unit
  attack-direction speed and near-contact restraint seams
- the project should explicitly decide whether still-experimental mechanism
  families like `local_desire` belong in `testonly` first, with explicit
  switches and safe defaults
- sequencing should stay one decision at a time

No runtime or settings files were changed for this addendum.
