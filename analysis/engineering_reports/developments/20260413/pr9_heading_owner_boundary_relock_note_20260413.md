# PR9 Heading-Owner Boundary Relock Note

Status: current review note
Date: 2026-04-13
Scope: formation-only heading-owner relock for `eng/dev-v2.1-formation-only` after governance review
Authority: engineering review note only; not canonical semantics authority

## Purpose

This note locks the current target read for fleet heading ownership on `PR #9`.

It does not implement the relock.
It does not yet redesign locomotion.
It does not yet simplify unit targeting.

Its job is to make the acceptable heading-owner boundary explicit before any further implementation slice.

## Governance anchor

This note follows:

- `Governance instruction — integrated Formation direction lock on PR #9`
- comment URL:
  - `https://github.com/LiDonghuang/logh_sandbox/pull/9#issuecomment-4233754282`

Most important locked read from that instruction:

- fleet heading should remain fleet-level and upstream
- fleet heading should be runtime-owned coarse-body state
- fleet heading should not be directly defined by average live unit orientation
- cold-shell subtraction remains accepted
- observer/debug reroot of `transition_advance_share` remains accepted

## Active owner baseline

The maintained active path involved in heading ownership is still runtime-owned in:

- `runtime/engine_skeleton.py::_evaluate_target_with_v4a_bridge(...)`
- `runtime/engine_skeleton.py::_resolve_v4a_reference_surface(...)`
- `runtime/engine_skeleton.py::_prepare_v4a_bridge_state(...)`
- `runtime/engine_skeleton.py::integrate_movement(...)`

The harness only seeds opening bundle state and observer packaging in:

- `test_run/test_run_execution.py::_FixtureExecutionSupport.build_fixture_expected_reference_bundle(...)`
- `test_run/test_run_execution.py::run_simulation(...)`

The active owner remains runtime, even if a transitional carrier still passes through bundle/state surfaces.

## Current collapse that must be relocked

The currently rejected landing point is not just "a different heading formula."

The sharper active-path problem is:

1. `_evaluate_target_with_v4a_bridge(...)` produces fleet-level target direction
2. `_prepare_v4a_bridge_state(...)` now derives current heading from average live unit orientation
3. `_prepare_v4a_bridge_state(...)` then relaxes toward target direction and overwrites `last_target_direction`
4. `_resolve_v4a_reference_surface(...)` reads `last_target_direction` back into the coarse-body axis path

This means the following were collapsed too tightly:

- upstream fleet heading / reference direction
- downstream realized unit orientation
- transition-carried movement direction

That collapse is too downstream and too contact-sensitive for the intended Formation boundary.

## Boundary relock

### A. Fleet heading should be runtime-owned coarse-body state

The acceptable target read is:

- heading is fleet-level
- heading is upstream
- heading is runtime-owned
- heading belongs with the coarse-body state family rather than realized unit motion

In current code terms, heading should live near the coarse-body family, not near per-unit realized orientation.

### B. Unit realized orientation is not the direct heading owner

`unit.orientation_vector` may still be useful as:

- debug signal
- observer signal
- weak secondary reference

But it should not be the direct owner of fleet heading.

Average live unit orientation is therefore not an acceptable long-term landing point.

### C. `last_target_direction` is currently an overloaded transitional carrier

Current read:

- `last_target_direction` is not just "targeting output"
- it is also being used as a transition-carried movement vector
- and it is indirectly steering coarse-body axis selection

That overloading should be treated as transitional, not doctrinal.

This note does not yet require the full final split, but later edits should not silently normalize this mixed role as correct long-term architecture.

### D. Transitional carrier is acceptable; ownership collapse is not

The immediate relock does **not** require a full runtime schema redesign first.

A bounded next slice may still use an existing runtime-side carrier surface if:

- runtime is the sole per-tick writer
- the carried state is explicitly treated as coarse-body heading
- the state is no longer directly sourced from realized unit orientation average

Carrier convenience is acceptable.
Ownership collapse is not.

## Preferred immediate bounded implementation target

The next implementation slice should stay limited to:

- `runtime/engine_skeleton.py`

Primary target seams:

- `_evaluate_target_with_v4a_bridge(...)`
- `_resolve_v4a_reference_surface(...)`
- `_prepare_v4a_bridge_state(...)`

Required outcome:

- explicit heading-owner boundary relock as runtime-owned coarse-body state

Not yet required in that slice:

- real locomotion implementation
- expected-position retirement
- hold / terminal / frozen-terminal redesign
- unit-targeting simplification implementation

## Relationship to the coarse-body boundary note

This heading-owner relock note is upstream-compatible with the existing coarse-body boundary read:

- body center
- front / heading axis
- forward extent
- lateral extent

But it adds one sharper constraint:

- front / heading axis must not be silently redefined by downstream unit realized orientation

## Decision rule for later PR #9 edits

Later edits should be judged by this rule:

- acceptable: runtime-owned fleet-level heading that remains upstream of realized unit orientation
- not acceptable: direct use of average live unit orientation as the settled fleet-heading owner
- acceptable: bounded transitional carrier while runtime remains the owner
- not acceptable: silently treating `last_target_direction` overload as final doctrine

## Boundary of this note

This note locks only the heading-owner boundary.

It does not yet define:

- the final permanent field name for runtime-owned fleet heading
- whether front axis and heading axis should stay identical or later split
- the final locomotion state surface
- the targeting simplification implementation order
