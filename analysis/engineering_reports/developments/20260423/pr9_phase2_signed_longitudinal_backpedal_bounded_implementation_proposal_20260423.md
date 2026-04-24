# PR9 Phase II - `signed_longitudinal_backpedal` Bounded Implementation Proposal

Date: 2026-04-23
Scope: document-first / design-first bounded implementation proposal only
Status: proposal only; no runtime implementation in this note

**Line classification:** Locomotion capability line
**Owner classification:** capability-layer proposal; fleet authorization unchanged
**Honest claim boundary:** first bounded reverse/backpedal realization only

## 1. Battle Read First

The intended first capability is narrow:

- a Unit keeps its facing / front orientation toward the battle
- while its longitudinal travel along that facing axis may become signed
- so a permitted give-ground ask can be realized as bounded backward travel
- without turning the Unit away from the battle

The intended visible improvement is also narrow:

- less rotational pullback during `back_off_keep_front` windows
- less arc-like give-ground when the Unit should preserve front
- clearer separation between "the behavior line asks to give ground" and
  "locomotion can physically realize that ask"

This proposal does not claim:

- retreat
- turn-away retirement
- arbitrary free translation
- broad facing / translation decoupling
- target-owner redesign
- combat-owner redesign
- module split
- full 3D locomotion redesign

Current runtime cannot honestly claim this capability yet. The current
implementation still couples facing and velocity through one realized heading.

## 2. Engineering Assumptions

- The active runtime owner remains `runtime/engine_skeleton.py`.
- The active Unit desire seam remains `unit_desire_by_unit`.
- Current behavior-line `back_off_keep_front` remains the experimental reference
  and is not being optimized in this proposal.
- The first implementation, if later authorized, should be test-only /
  experimental and default-off.
- No frozen canonical, mapping, Engine v2.0 Skeleton, or governance file is
  modified by this proposal.

## 3. Exact Carrier Design

### Proposed New Carrier

Name:

- `desired_longitudinal_travel_scale`

Semantic meaning:

- signed Unit-local longitudinal travel intent along the Unit's realized facing
  axis
- positive values ask locomotion to travel forward along the facing axis
- zero asks for no longitudinal travel along the facing axis
- negative values ask locomotion to travel backward along the facing axis while
  preserving facing

Numeric range:

- `[-1.0, 1.0]`

Validation rule:

- value must be finite
- value must be within `[-1.0, 1.0]`
- when the experimental capability gate is enabled, locomotion should fail fast
  if the carrier is missing or invalid

### Relationship To Existing Carriers

`desired_heading_xy` remains:

- facing / heading intent
- the input to the turn-rate-limited facing realization path
- not a backward travel instruction

`desired_speed_scale` remains:

- unsigned speed magnitude envelope / cap
- finite and non-negative
- not overloaded with negative meaning

`desired_longitudinal_travel_scale` adds:

- the forward/backward longitudinal sign and requested fraction within the cap
- no owner claim over whether give-ground is authorized

Shortest design read:

- `desired_heading_xy` says where the Unit should face
- `desired_speed_scale` says how much speed budget is available
- `desired_longitudinal_travel_scale` says whether that budget is spent forward,
  held near zero, or spent backward along the facing axis

Candidate target signed speed, if later authorized:

```text
unsigned_speed_cap =
    unit.max_speed
    * fixture_step_magnitude_gain
    * desired_speed_scale
    * turn_limited_speed_scale

target_signed_longitudinal_speed =
    unsigned_speed_cap
    * desired_longitudinal_travel_scale
    * reverse_authority_factor_when_negative
```

Where:

- `reverse_authority_factor_when_negative = 1.0` for forward or zero travel
- `reverse_authority_factor_when_negative < 1.0` is recommended for negative
  travel in the first gate

This is not a parameter tweak. It adds an explicit signed locomotion carrier.

## 4. Exact Locomotion Realization Rule

### Battle-Language Rule

The Unit first turns its face toward the permitted facing intent under the
existing turn-rate limit. Then locomotion moves it forward or backward along
that realized facing axis according to the signed longitudinal ask.

For backward travel:

- the Unit does not turn its face away from the battle
- the realized facing remains the fire-facing / front-preserving direction
- the velocity points opposite the realized facing axis
- acceleration and deceleration move through zero rather than snapping from
  forward to backward

### Proposed Runtime Realization Shape

Current runtime shape:

- computes `realized_heading_hat`
- writes `orientation = realized_heading_hat`
- writes `velocity = realized_heading_hat * step_speed`
- clamps `step_speed >= 0`

Proposed first-gate shape:

- keep `realized_heading_hat` as the facing owner
- write `orientation = realized_heading_hat`
- compute a signed longitudinal target speed
- accelerate / decelerate current signed longitudinal speed toward the target
- write velocity as:

```text
velocity = realized_heading_hat * realized_signed_longitudinal_speed
```

When `realized_signed_longitudinal_speed` is negative, actual travel is
backward while facing remains forward.

### Across-Zero Handling

Current speed handling uses unsigned speed magnitude. The first gate needs a
signed longitudinal speed state for the current tick:

```text
current_signed_longitudinal_speed =
    dot(current_velocity, current_heading_hat)
```

Then:

- if target signed speed is greater than current signed speed, apply
  `max_accel_per_tick * dt`
- if target signed speed is lower than current signed speed, apply
  `max_decel_per_tick * dt`
- crossing zero is just a bounded step through the same signed scalar
- no instant sign flip is allowed

This preserves the current acceleration / deceleration discipline while making
the longitudinal scalar signed.

### Turn-Rate Limits

Turn-rate limits still apply to facing:

- `desired_heading_xy` and the usual maneuver/cohesion/separation/boundary terms
  still produce a desired facing direction
- `realized_heading_hat` is still rotated toward that desired direction by
  `max_turn_deg_per_tick`
- backward travel does not bypass turn-rate

The first gate should not allow a Unit to face one way arbitrarily and translate
in any unrelated direction. It only allows signed travel along the realized
facing axis.

### Reverse Authority

Reverse authority should be weaker than forward authority in the first gate.

Reason:

- backpedaling while preserving facing should read as controlled give-ground,
  not as full-speed reverse driving
- weaker reverse authority reduces the risk of accidental retreat semantics
- it keeps the first gate honest as a bounded capability experiment

Recommended first-gate limiter:

- add a test-only reverse authority cap such as
  `signed_longitudinal_backpedal_reverse_authority_scale`
- range: `(0.0, 1.0]`
- recommended first review value: `0.45`

This limiter is not the primary carrier. The primary carrier remains
`desired_longitudinal_travel_scale`.

## 5. Exact Boundary Of The First Experiment

Allowed in this first gate:

- bounded signed longitudinal motion along the facing axis
- first literal backward travel while preserving front-facing orientation
- reduced rotating pullback during give-ground windows
- clearer distinction between behavior-line authorization and locomotion
  realization
- minimal diagnostics needed to verify that negative longitudinal travel was
  actually requested and realized

Not allowed in this first gate:

- retreat implementation
- turn-away retirement
- target-owner redesign
- combat-owner redesign
- broad facing / translation decoupling
- arbitrary strafing
- module split
- full 3D locomotion redesign
- behavior-line optimization
- promotion of the current experimental behavior line to maintained doctrine

## 6. Owner Split Preserved

Fleet / reference side still owns:

- fleet front axis
- standoff / hold / terminal truth
- higher-level movement envelope
- whether back-off or retreat is authorized

Unit / behavior side still owns:

- local perception and target-facing read
- the bounded behavior-line ask such as `back_off_keep_front`
- whether a local Unit ask should suppress over-commit or reopen space

Unit / locomotion side only owns:

- physical realization of a permitted ask
- turn-rate-limited facing realization
- acceleration / deceleration discipline
- signed longitudinal realization when explicitly enabled

Locomotion capability must not swallow battle intent.

Plain split:

- fleet/reference answers "is give-ground allowed?"
- behavior asks "what local response is being requested?"
- locomotion answers "can the Unit physically realize the permitted ask while
  preserving facing?"

## 7. Interaction With Current Behavior Line

The current experimental `back_off_keep_front` line already computes a
behavior-semantic give-ground / reopen-space response. It currently feeds that
response through:

- `desired_heading_xy`
- `desired_speed_scale`

Because current locomotion only moves along realized heading, the behavior line
can only approximate give-ground by:

- suppressing over-commit
- slowing forward travel
- bending heading toward a local firing / spacing opportunity

With `desired_longitudinal_travel_scale`, the same behavior-line family could
feed a permitted signed longitudinal ask:

- ordinary forward movement: positive carrier
- hold / brake-like restraint: near-zero carrier
- authorized give-ground / back-off window: negative carrier

What remains unchanged:

- fleet authorization remains upstream
- current `back_off_keep_front` remains experimental
- target choice does not move
- combat execution does not move
- retreat is not opened

What becomes less rotational:

- when the Unit should preserve facing but give ground, the behavior line no
  longer has to approximate backward motion by rotating the desired heading away
  from the battle
- the Unit can maintain a battle-facing orientation while translating backward
  along that facing axis

Residuals that will still remain:

- deep overlap recovery may still fragment if compression has already happened
- blocked Units may still need separation and boundary terms
- lateral firing opportunity is not solved by a longitudinal-only carrier
- retreat / retirement remains absent
- no full independent facing / translation system exists yet

## 8. Minimal Implementation Surface If Later Authorized

This section is not implementation authorization. It identifies the smallest
likely touch surface for a later authorized slice.

Likely runtime functions:

- `runtime/engine_skeleton.py::_compute_unit_desire_by_unit(...)`
  - produce `desired_longitudinal_travel_scale` through the existing Unit desire
    seam when the experimental capability is enabled
  - keep ordinary forward intent explicit, not hidden as a consumer fallback
- `runtime/engine_skeleton.py` low-level locomotion realization block around the
  current `unit_desire_by_unit` read and `realized_heading_hat` velocity write
  - validate the signed carrier
  - compute signed target speed
  - apply bounded acceleration/deceleration across zero
  - write velocity from signed speed along realized facing
- `test_run/test_run_scenario.py`
  - load and validate the explicit experimental enablement surface if added
- `test_run/test_run_execution.py`
  - pass the enablement surface into runtime movement config if needed

Existing Unit desire seam:

- yes, the new carrier should pass through `unit_desire_by_unit`
- do not create a second target owner
- do not create a parallel locomotion schema in the harness
- do not overload `desired_speed_scale`

Minimal debug / VIZ extension:

- a small extension is likely needed so Human can verify the capability was
  actually active
- proposed minimal debug field:
  - `signed_longitudinal_travel_scale_min`
  - fleet-level minimum over alive Units for the tick
- optional realized companion:
  - `signed_longitudinal_speed_min`
- VIZ should not grow a broad catalog; if exposed, the focus row should show a
  single compact signed-longitudinal read only for this capability review

Smallest experimental enablement surface:

- `runtime.physical.locomotion.experimental_signed_longitudinal_backpedal_enabled`
  - boolean
  - default `false`
  - enablement only, not the carrier
- optional first-gate cap:
  - `runtime.physical.locomotion.signed_longitudinal_backpedal_reverse_authority_scale`
  - finite in `(0.0, 1.0]`
  - suggested first review value `0.45`

The boolean is acceptable only as an enablement gate. It is not accepted as the
primary backpedal design.

## 9. No-Silent-Fallback Requirements

If this gate is later implemented:

- do not infer backward travel from negative `desired_speed_scale`
- do not treat missing `desired_longitudinal_travel_scale` as zero or forward
  when the gate is enabled
- do not silently clamp illegal signed carrier values without reporting the
  invalid value
- do not let the harness supply a fallback that hides a missing runtime setting
- keep any normalization or clamping explicit and bounded by the declared
  carrier range

Producer-side ordinary forward intent may be explicit `+1.0`; that is not a
consumer fallback if it is written intentionally by the Unit desire owner.

## 10. What This Gate Solves And Does Not Solve

This gate solves:

- the first literal bounded backward longitudinal travel capability
- the ability to preserve battle-facing orientation while giving ground
- the current over-reliance on rotational pullback for keep-front back-off reads
- the carrier truth problem caused by trying to express signed movement through
  unsigned speed

This gate does not solve:

- retreat doctrine
- turn-away retirement
- lateral strafe
- arbitrary facing / translation decoupling
- target selection
- combat resolution
- already-deep overlap by itself
- broad module ownership cleanup
- stable promotion of the experimental behavior-line family

## 11. Recommended Later Implementation Slice

If Governance later authorizes implementation, the smallest honest slice should
be:

1. Add explicit experimental enablement and signed carrier validation.
2. Write `desired_longitudinal_travel_scale` through the existing Unit desire
   seam.
3. Update locomotion realization so signed longitudinal speed is realized along
   `realized_heading_hat`.
4. Add one minimal diagnostic proving negative ask / negative realization.
5. Validate default-off no-drift before any experimental battle-read comparison.

That future slice should remain locomotion-capability work. It should not reopen
behavior-line optimization or retreat doctrine in the same carrier.
