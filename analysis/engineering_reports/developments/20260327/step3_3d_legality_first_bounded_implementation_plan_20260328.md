# Step 3 3D Legality First Bounded Implementation Plan (2026-03-28)

Engine Version: `dev_v2.0`
Modified Layer: Step 3 legality line local pre-implementation first-bounded-implementation planning
Affected Parameters: none
New Variables Introduced: none
Cross-Dimension Coupling: turns the already-completed legality contract/interface/placement/data-surface/order decisions into one bounded first implementation plan without authorizing implementation yet
Mapping Impact: preserves mapping ownership by reusing the existing mapping-produced reference surface rather than redesigning mapping
Governance Impact: compresses the legality-prep document line into one first-cut implementation plan that is concrete enough for execution but still explicitly pre-implementation
Backward Compatible: yes

Summary
- This plan defines the smallest believable first legality implementation cut.
- The first cut should reuse the existing map-like reference-position surface, introduce one explicit legality-owned middle stage, and emit one feasible-position surface before downstream consumption.
- The plan should prefer local seam insertion over broad refactor.
- The first cut should not redesign mapping, downstream consumers, telemetry, or viewer semantics.
- The first cut should also avoid algorithm rewrites; it should first expose legality as an explicit bounded stage around already-existing correction surfaces.

## 1. Plan Goal

The goal of the first bounded legality implementation is:

- make legality visible as one explicit runtime stage
- without widening into full legality redesign

The first cut should prove only that:

- legality can consume an upstream reference-position surface
- legality can own one bounded middle-stage resolution seam
- legality can emit one feasible-position surface before downstream consumption

It should not attempt to solve the entire future legality layer in one turn.

## 2. Agreed Inputs To Use

The first cut should reuse the already-bounded upstream surface pattern now visible in repo code:

- `runtime/engine_skeleton.py` `_build_fixture_expected_position_map()`
- the core `expected_positions` map-like surface it returns

That makes the first cut smaller because it can start from an existing:

- unit-addressable
- position-centered
- mapping-like upstream surface

The first cut should read this as the bounded predecessor of:

- `reference_positions_by_unit`

It should not redesign how mapping itself is produced.

## 3. Agreed Middle Stage To Expose

The first cut should expose one explicit legality-owned middle stage around the already-existing post-movement correction region in:

- `runtime/engine_skeleton.py`

The current repo anchor for that bounded region is the existing:

- tentative position build
- post-movement separation/projection correction
- hard-boundary clamp

The plan does not claim that current code is already the final legality design.

It only says:

- this region is the smallest believable bounded starting seam for first legality exposure

## 4. Agreed Output To Expose

The first cut should emit one bounded post-legality feasible surface before downstream consumption.

The smallest useful output is:

- the identity-preserving feasible-position map-like surface decided in the data-surface note

That surface is the bounded predecessor of:

- `feasible_positions_by_unit`

The first cut should keep this output weak:

- no observer/report bundle inside the core surface
- no viewer-facing fields
- no downstream policy fields

## 5. Candidate Minimal Touchpoints

The candidate minimal touchpoints for the first cut are:

- `runtime/engine_skeleton.py`
  - bounded legality intake seam
  - bounded legality-owned middle stage
  - bounded feasible-outcome handoff seam

- `test_run/test_run_execution.py`
  - bounded harness-side validation reuse where `expected_position_map` and projection metrics are already read

- `test_run/test_run_telemetry.py`
  - only if a minimal non-core echo is actually needed; otherwise avoid in the first cut

This is a candidate touchpoint set, not a frozen hook decision.

## 6. First-Cut Implementation Shape

The first cut should be subtraction-first and seam-first:

1. name the legality intake surface explicitly
2. name the legality-owned middle stage explicitly
3. name the feasible-outcome handoff surface explicitly
4. keep the stage local to the current bounded path
5. avoid broad helper proliferation or cross-file abstraction unless strictly needed

The first cut should prefer:

- local explicit seams
- bounded variable/surface naming
- existing data flow reuse

over:

- architecture rewrite
- helper-layer explosion
- early generalization

## 7. Validation Strategy For The First Cut

The first cut should validate on the current bounded fixture/harness path first.

The most useful existing anchors already present in repo code are:

- expected-position RMS error in `test_run/test_run_execution.py`
- projection activity metrics in `test_run/test_run_execution.py`
- existing runtime debug/telemetry surfaces in `runtime/engine_skeleton.py` and `test_run/test_run_telemetry.py`

The first cut should aim to show:

- legality seams are explicit
- upstream/downstream surfaces are traceable
- existing bounded metrics still work

It should not introduce a new viewer or report protocol as part of first validation.

## 8. What The First Cut Must Not Do

The first cut must not do any of the following:

- mapping redesign
- downstream consumer redesign
- observer/report pipeline redesign
- viewer semantic ownership
- projection algorithm rewrite
- collision / boundary algorithm rewrite
- broad runtime refactor
- new public settings surface expansion

It should also avoid:

- freezing exact touchpoint locations beyond the bounded files actually needed
- claiming the first cut is the final legality architecture

## 9. Exit Condition

The first bounded legality implementation plan is complete when the future implementation can be framed as:

- consume existing mapping-like reference positions
- run one explicit legality-owned middle stage
- emit one explicit feasible-position handoff
- validate on the bounded harness path
- leave richer algorithm and consumer decisions for later carriers

That is sufficient for this plan carrier.

## 10. Human-Trackable Validation Option

For substantive runtime-facing modifications, engineering should try to provide at least one human-trackable validation option that can be inspected without stepping through the code.

The option may stay minimal. Good bounded forms include:

- a small variable dump
- a bounded long-form CSV keyed by `tick + unit_id`
- a compact delta/error summary

When there are multiple reasonable readout shapes, engineering may suggest the lightest one first and let the human choose whether a richer dump is needed.

For the current legality first-bounded-implementation discussion, the concrete example is:

- `analysis/engineering_reports/developments/20260328/step3_3d_legality_expected_positions_first50_ticks_longform_20260328.csv`

That artifact is saved as a single long-form CSV so the human can filter by:

- tick
- unit
- expected world position
- actual world position
- actual relative forward/lateral position
- expected slot-local forward/lateral offset
- forward/lateral deltas

This validation option is for human/governance tracing only.

It does not change runtime semantics, and it does not by itself authorize broader telemetry or reporting-surface expansion.
