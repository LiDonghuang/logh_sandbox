# Step 3 3D Standard Rectangle Expected Spacing Governance Request

- Engine Version: `dev_v2.0`
- Modified Layer: `analysis / governance-request record only`
- Affected Parameters: none in runtime
- New Variables Introduced: none
- Cross-Dimension Coupling: none
- Mapping Impact: none
- Governance Impact: requests bounded review of a possible future spacing-surface opening
- Backward Compatible: yes
- Summary: records recent engineering/human analysis and requests governance guidance on whether to open a distinct expected-formation-spacing line, separate from low-level `min_unit_spacing`

## Purpose

This note is a governance-facing request, not an implementation note.

It records the recent human + engineering investigation around early standard-rectangle stretching during `neutral_transit_v1`, and asks whether governance wants to explicitly open a bounded spacing-surface line before further runtime probing continues.

## Current Engineering Read

Current bounded evidence supports the following read:

- standard rectangle generation itself is clean for `aspect_ratio = 1.0` and `4.0`
- the distortion is real in headless runtime, not viewer-only
- the distortion correlates strongly with ordinary forward transit
- the distortion does not appear in the strict `objective == origin` static-hold case
- legality/projection does not currently read as the primary cause
- the issue currently reads more as ordinary-transit movement-vs-restore asymmetry

In practical terms:

- when the fleet is advancing, front ranks continue to run ahead of their expected forward slot positions
- rear ranks continue to lag behind
- the resulting rank split stretches the formation along the current advance axis

## Why This Request Exists

The current runtime already owns a low-level spacing floor through:

- `runtime.physical.movement_low_level.min_unit_spacing`

That surface is currently doing low-level physical / separation work.

However, the recent analysis suggests that the project may soon need a distinct, higher-level concept for:

- expected formation spacing / intended slot separation

This would be structurally different from:

- hard low-level minimum collision / separation spacing

The human specifically asked whether governance should be consulted before engineering keeps probing in that direction.

## Governance Question

Should Engineering be allowed to open a bounded `expected formation spacing` line that is explicitly distinct from low-level `min_unit_spacing`?

Requested bounded reading if governance chooses to open it later:

- expected formation spacing would describe intended formation-slot spacing
- it would not automatically replace `min_unit_spacing`
- it would not be read as a geometry-hardcoding rule
- it would not silently widen into legality redesign or viewer ownership

## What Is Not Being Requested Here

This note does **not** request immediate implementation.

This note does **not** add a new runtime parameter.

This note does **not** claim the correct future parameter name, storage site, or ownership layer yet.

This note only asks governance whether that bounded line may be opened deliberately instead of being allowed to leak in implicitly through repeated runtime probing.
