# Step 3 3D Objective First Validation Note (2026-03-26)

Engine Version: `dev_v2.0`
Modified Layer: Step 3 implementation-planning validation note only
Affected Parameters: none
New Variables Introduced: none
Cross-Dimension Coupling: validation plan uses the bounded neutral-transit fixture only
Mapping Impact: planning only
Governance Impact: defines the minimum clean validation surface for a future bounded implementation turn
Backward Compatible: yes

Summary
- The first validation should stay harness-side and fixture-side; it does not require viewer changes.
- Validation should prove that the 3D objective contract can be carried and read without becoming formation / legality / combat.
- The smallest clean path is a single `neutral_transit_v1` run with contract echo/readout.
- Success means bounded objective ownership is visible and the fleet still trends toward the anchor.
- Failure means the contract starts growing into frame, legality, combat, or viewer-owned semantics.

## 1. Minimum Validation Shape

If a first code turn is later authorized, the smallest validation should be:

- one bounded `neutral_transit_v1` fixture run
- single fleet only
- no enemy
- no combat
- no firing
- point-anchor-only

The validation should remain harness-side:

- no viewer requirement
- no replay protocol requirement
- no battle-path widening

## 2. Minimum Required Readout

The first implementation should expose a small readout showing:

- `anchor_point_xyz`
- projected `anchor_point_xy`
- `source_owner`
- `objective_mode`
- `no_enemy_semantics`
- fixture `fleet_id`
- `objective_reached_tick`
- `centroid_to_objective_distance`

Best location for the first readout:

- `observer_telemetry['fixture']`
- concise fixture summary emitted by `test_run_entry._run_neutral_transit_fixture(...)`

## 3. What Counts as Success

The first validation counts as successful if all of the following hold:

1. the derived 3D contract is present on the bounded fixture carrier
2. the contract fields read back exactly as expected:
   - `source_owner = fixture`
   - `objective_mode = point_anchor`
   - `no_enemy_semantics = enemy_term_zero`
3. the implementation uses the current single-fleet / no-enemy fixture only
4. the fleet still trends toward the anchor and reaches the stop condition under the current bounded fixture rules
5. no new settings surface is required
6. no viewer code is required to prove the contract exists

## 4. What Counts as Failure

The first validation should be treated as failed if any of the following appears:

- contract fields are inferred rather than explicit
- viewer becomes necessary to define or repair objective meaning
- `transit_axis_hint_xyz` is used to smuggle in frame semantics
- the contract starts carrying formation extents, spacing, or posture meaning
- legality / feasibility data appears in the contract or its first carrier
- target preference or combat semantics appear in the carrier
- a new 3D settings subtree is needed just to validate the first carrier

## 5. Scope-Creep Warning Signals

The clearest signals that objective is starting to grow into other layers are:

- new secondary-axis or roll/bank fields
- new frame or slot-offset fields inside the objective contract
- new replay bundle ownership for objective meaning
- new viewer-local fallback rules
- new TL activation or pursuit / retreat switching
- any need to alter `runtime/runtime_v0_1.py` in the first implementation

## 6. Recommended Validation Order

1. fixture contract is assembled from current bounded settings input
2. execution validates the contract
3. runtime-facing fixture hook consumes projected `xy` only
4. fixture telemetry echoes contract + distance-to-objective progress
5. launcher summary confirms the run stayed inside neutral-transit hard bounds

That order is small enough to prove the contract is real without opening the rest of Step 3.
