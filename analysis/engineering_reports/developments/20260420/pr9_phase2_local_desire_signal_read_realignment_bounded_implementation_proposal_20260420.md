## PR9 Phase II - Local Desire Signal Read Realignment Bounded Implementation Proposal

Date: 2026-04-20  
Scope: bounded implementation proposal only  
Status: document-first; no implementation in this round

### 1. One-sentence conclusion

This proposal changes only the signal read inside `local_desire`: heading-side
local bias should be driven primarily by `fleet front -> selected target
bearing`, while speed-side brake-only adaptation should be driven primarily by
`unit facing -> selected target bearing`, with the existing carrier, owner/path,
and single target source left in place.

### 2. Exact owner/path to change

Only this owner/path is proposed to change:

- `runtime/engine_skeleton.py`
  - `EngineTickSkeleton._compute_unit_desire_by_unit(...)`

More narrowly, only the same-tick signal read used to build:

- `desired_heading_xy`
- `desired_speed_scale`

This proposal does **not** change:

- target-selection ownership
- `resolve_combat(...)` ownership
- locomotion-family ownership
- carrier ownership

### 3. Keep vs replace

Keep:

- `local_desire` carrier
- owner/path in `_compute_unit_desire_by_unit(...)`
- same-tick single target source:
  - `selected_target_by_unit`
- carrier shape:
  - `desired_heading_xy`
  - `desired_speed_scale`
- same pre-movement placement
- brake-only speed adaptation
- no new persistent state

Replace:

- heading-side dependence on the current shared `unit facing -> selected target
  bearing` turn signal
- the current shared-read pattern where heading-side and speed-side both derive
  their main activation from the same facing-relative turn-need path

Bounded intent of the replacement:

- heading-side should no longer treat current unit-facing turn-need as the main
  activator
- speed-side should continue to treat current unit-facing turn burden as its
  main activator

### 4. Heading-side signal plan

Proposed exact primary signal:

- `fleet front -> selected target bearing`

Minimal active-path expression:

- keep the current same-tick selected target
- compute target bearing from unit position to `selected_target_by_unit`
- compare that bearing against the current fleet front axis
- use the lateral / off-front component as the primary heading-side bias signal

Why this is less collapsed than the current heading read:

- the maintained target-selection path already cone-filters around current unit
  facing
- that makes `unit facing -> selected target bearing` too narrow to serve as the
  main heading activator
- by contrast, `fleet front -> selected target bearing` remains broad and
  behavior-bearing on the same maintained path

Near-contact gate read:

- for the first bounded slice, keep the current near-contact gate shared
- reason:
  - this slice is about signal-read realignment, not regime-family expansion
  - keeping the proximity gate unchanged keeps the slice smaller than a broader
    combat-adaptation proposal

Minimal heading-side implementation read:

- retain the current base heading source
- relax `desired_heading_xy` from fleet base heading toward target bearing
- drive the bias primarily from fleet-front-relative target bearing rather than
  current unit-facing turn need

### 5. Speed-side signal plan

Proposed exact primary signal:

- `unit facing -> selected target bearing`

Why this remains appropriate on the speed side:

- brake-only speed adaptation is about actual local turning burden of the unit
- that burden is still best represented by current facing relative to the chosen
  target
- speed should remain later, weaker, and conservative, so the narrower signal is
  acceptable here

Why this does not require a second target source:

- the existing `selected_target_by_unit` already supplies the needed target
  identity
- speed-side only needs a same-tick local bearing from the currently selected
  target
- no guide target or parallel target semantics are needed for this slice

Minimal speed-side read:

- keep brake-only adaptation
- keep speed-side weaker than heading-side
- continue to derive the brake trigger from facing-relative target geometry
- do not widen into advance boost, sprint, lunge, or new maneuver families

### 6. Minimal implementation shape

This slice can be expressed without changing carrier shape and without adding a
new owner.

Minimal shape:

1. Keep current same-tick target lookup in `_compute_unit_desire_by_unit(...)`
2. Keep current target-bearing computation
3. Split the angular read into two local signals:
   - heading-side signal from `fleet front -> selected target bearing`
   - speed-side signal from `unit facing -> selected target bearing`
4. Use the heading-side signal as the primary bias input for
   `desired_heading_xy`
5. Use the speed-side signal as the primary brake input for
   `desired_speed_scale`
6. Leave `unit_desire_by_unit` shape unchanged

Minimal code-read change implied by this proposal:

- current heading-side `local_heading_bias_weight` should stop being primarily
  gated by the shared facing-relative turn signal
- current speed-side can continue to use a later / weaker facing-relative read
- the slice should remain within `_compute_unit_desire_by_unit(...)`

### 7. What still does not change

Still unchanged if this slice is later authorized:

- no mode
- no retreat
- no persistent target memory
- no second target owner
- no guide target / parallel target semantics
- no broad locomotion rewrite
- no module split
- no target-owner reroot
- no combat-execution reroot
- no coupling redesign

Current accepted separations remain intact:

- fleet front axis != unit facing != actual velocity
- target selection != combat execution
- local desire adaptation != Formation / FR owner flow-back

### 8. Validation posture if later authorized

If this bounded slice is later authorized, validation should include:

- static owner/path audit
- compile check
- narrow smoke
- paired comparison against the current Phase II primary baselines
- targeted human-readable evidence focused on local desire read change

The human-readable evidence should focus on:

- whether heading-side bias now activates on fleet-front-relative off-axis
  target opportunities that were previously silent
- whether speed-side remains later, weaker, and brake-only
- whether the slice stays within local-desire read realignment rather than
  drifting into mode, retreat, or broader locomotion redesign

### 9. Why this remains smaller than a doctrine wave

This proposal is intentionally smaller than:

- a combat-adaptation family proposal
- a locomotion rewrite proposal
- a combat-coupling redesign proposal

Reason:

- it keeps the current carrier
- it keeps the current owner/path
- it keeps one same-tick target source
- it only changes which geometry read primarily feeds heading-side versus
  speed-side local desire

Therefore this proposal should not be read as:

- fleet-level combat scalar redesign
- fire-quality redesign
- target-owner redesign
- broader combat doctrine redesign
