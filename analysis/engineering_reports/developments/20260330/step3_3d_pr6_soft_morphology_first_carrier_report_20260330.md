# Step 3 3D PR #6 Soft Morphology First-Carrier Report (2026-03-30)

Engine Version: `dev_v2.0`  
Modified Layer: `test_run/` bounded candidate plumbing plus report/artifact package only  
Affected Parameters: test-only `runtime.movement.v4a.test_only.reference_surface_mode` and `runtime.movement.v4a.test_only.soft_morphology_relaxation`; existing split/restore settings retained  
Mapping Impact: none  
Frozen Layer Impact: none; `runtime/engine_skeleton.py` untouched  
Governance Read: keeps PR #6 on the formation-substrate main line; replaces rigid dead-slot expected-surface generation with a bounded planar soft-morphology carrier while preserving the existing spacing split and restore bridge

## Summary

- This turn stops treating PR #6's next carrier as a restore-strength problem and moves the main seam to the formation-reference surface generator.
- The new bounded carrier leaves the `2.0 / 1.0` split intact and leaves the existing restore bridge intact.
- What changes is the reference-surface ownership: the branch now supports a test-only `rigid_slots` legacy path and a new `soft_morphology_v1` path.
- `soft_morphology_v1` is planar-first, alive-ratio-aware, and uses a fleet-level morphology state (`forward_extent_current/target`, `lateral_extent_current/target`) rather than exact dead-slot continuation as the primary ownership read.
- Band membership now has a stable source-of-truth from the initial generator (`front/mid/rear` plus `left/center/right` terciles), while within-band placement is emitted from a soft local-envelope rule instead of direct dead-slot reuse.
- Primary neutral-transit evidence shows the carrier is semantically real: exact-slot zero-error lock is gone, but the candidate still stays much closer to the target shape than the coupled baseline.
- The same evidence also shows the current carrier is not yet merge-ready: the new read is softer than rigid slots, but it still looks too clean/tight to count as a settled "living formation" substrate.
- Secondary battle sanity was rechecked only to confirm the bridge still remains visible on maintained battle; hostile-contact issues were intentionally not allowed to dominate this turn.

## Files Changed

- `test_run/settings_accessor.py`
- `test_run/test_run_scenario.py`
- `test_run/test_run_execution.py`
- `test_run/test_run_v1_0.testonly.settings.json`
- `test_run/test_run_v1_0.settings.comments.json`
- `test_run/test_run_v1_0.settings.reference.md`
- `analysis/engineering_reports/developments/20260330/step3_3d_pr6_soft_morphology_first_carrier_report_20260330.md`
- `analysis/engineering_reports/developments/20260330/step3_3d_pr6_soft_morphology_neutral_transit_comparison_20260330.csv`
- `analysis/engineering_reports/developments/20260330/step3_3d_pr6_soft_morphology_neutral_transit_plot_20260330.png`
- `analysis/engineering_reports/developments/20260330/step3_3d_turning_cost_implementation_prep_note_20260330.md`
- `analysis/engineering_reports/developments/20260330/step3_3d_first_honest_formation_ownership_opening_note_20260330.md`
- `repo_context.md`
- `system_map.md`

## Carrier Chosen

This turn follows the current governance answer directly:

- do not rewrite `integrate_movement` first
- do not continue scalar restore-strength tuning as the main line
- instead replace the reference surface generator first

The implemented first carrier is:

- fleet-level
- planar-first
- alive-ratio-driven
- relaxed
- source-of-truth-clean

### New test-only reference-surface seam

Under `runtime.movement.v4a.test_only`:

- `reference_surface_mode`
  - `rigid_slots`
  - `soft_morphology_v1`
- `soft_morphology_relaxation`

This remains branch-local and test-only.  
No public runtime surface was widened.

## Soft Morphology Carrier: Current Honest Shape

### What stays the same

The branch still preserves:

- expected/reference spacing
- physical minimum spacing
- restore bridge
- maintained battle visibility of the restore line

### What changes

The old expected surface primarily meant:

- survivors continue to hold their original local slot offsets

The new `soft_morphology_v1` surface primarily means:

- the fleet owns a planar morphology envelope
- the envelope contracts continuously from alive-ratio target state
- units preserve broad topology first
- within-band placement is emitted from soft local compaction instead of exact dead-slot continuation

### Minimum runtime-owned state in this carrier

The carrier keeps the fleet-level morphology state intentionally small:

- `forward_extent_current`
- `lateral_extent_current`
- `forward_extent_target`
- `lateral_extent_target`

No separate `front_extent_target` was added in this turn, to avoid duplicating `forward_extent_target` semantics.

### Alive-ratio rule used here

The first-carrier compaction read uses:

- `r = N / N0`
- `target_scale = sqrt(r)`

So:

- `forward_extent_target = forward_extent_base * sqrt(r)`
- `lateral_extent_target = lateral_extent_base * sqrt(r)`

This is a planar-first carrier assumption only.  
It is not a long-term doctrine claim.

### Broad topology ownership

Band identity is now a stable source-of-truth derived from the initial generator:

- forward terciles: `front / mid / rear`
- lateral terciles: `left / center / right`

Units keep their broad band first.  
This turn does not open free every-tick reclassification and does not do global optimal reassignment.

### Within-band softness

Within-band placement now uses:

- current local positions
- current band-local centroid
- target band envelope
- bounded envelope compression only when the current spread exceeds the target spread

So the carrier no longer reuses the same exact per-unit slot map under a new name.

## Primary Validation Path

Primary scene:

- `neutral_transit_v1`

Compared modes:

1. `coupled_rigid`
   - `expected_reference_spacing = 2.0`
   - `physical_min_spacing = 2.0`
   - `reference_surface_mode = rigid_slots`

2. `split_rigid`
   - `expected_reference_spacing = 2.0`
   - `physical_min_spacing = 1.0`
   - `reference_surface_mode = rigid_slots`

3. `split_soft`
   - `expected_reference_spacing = 2.0`
   - `physical_min_spacing = 1.0`
   - `reference_surface_mode = soft_morphology_v1`
   - `soft_morphology_relaxation = 0.2`

Shared read:

- `movement_model_effective = v4a`
- `restore_strength = 0.25`
- `reference_layout_mode = rect_centered_rows`
- `fleet_size = 100`
- aspect ratios:
  - `1.0`
  - `4.0`

Primary human-readable artifacts:

- `analysis/engineering_reports/developments/20260330/step3_3d_pr6_soft_morphology_neutral_transit_comparison_20260330.csv`
- `analysis/engineering_reports/developments/20260330/step3_3d_pr6_soft_morphology_neutral_transit_plot_20260330.png`

## Primary Findings

### 1. The new carrier is semantically real

At `tick = 100`, the old split-rigid path is still exact-slot clean:

- `aspect_ratio = 1.0`
  - `width_depth_ratio = 1.000000`
  - `front_extent_ratio = 1.000000`
  - `expected_position_rms_error ≈ 0.000000`
- `aspect_ratio = 4.0`
  - `width_depth_ratio = 4.750000`
  - `front_extent_ratio = 1.000000`
  - `expected_position_rms_error ≈ 0.000000`

The new split-soft path breaks that exact-slot read:

- `aspect_ratio = 1.0`
  - `width_depth_ratio = 0.999023`
  - `front_extent_ratio = 1.006225`
  - `expected_position_rms_error = 0.356232`
- `aspect_ratio = 4.0`
  - `width_depth_ratio = 4.695521`
  - `front_extent_ratio = 1.008247`
  - `expected_position_rms_error = 0.359229`

That means the branch now carries:

- real expected/reference spacing
- real restore
- real physical minimum spacing
- and now also a semantically real soft-reference carrier rather than only a rigid slot-map bridge

### 2. The new carrier is still too close to a rigid read

Even after the carrier shift, the neutral-transit curves remain very tight:

- `aspect_ratio = 1.0`
  - `width_depth_ratio` stays near `1.0`
  - `front_extent_ratio` stays near `1.0`
- `aspect_ratio = 4.0`
  - `width_depth_ratio` stays near `4.70`
  - `front_extent_ratio` stays near `1.0`

This is much better than the coupled baseline, but it still reads visually closer to:

- "highly disciplined surface preservation"

than to:

- "stable but living morphology"

So this turn succeeds structurally, but not yet aesthetically/behaviorally enough for merge discussion.

### 3. The coupled baseline remains clearly worse

At `tick = 100`:

- `aspect_ratio = 1.0`
  - coupled:
    - `width_depth_ratio = 0.787162`
    - `front_extent_ratio = 1.327087`
    - `expected_position_rms_error = 1.672401`
- `aspect_ratio = 4.0`
  - coupled:
    - `width_depth_ratio = 2.881522`
    - `front_extent_ratio = 1.720626`
    - `expected_position_rms_error = 1.250441`

So the new carrier does not collapse back into the old stretched baseline.

## Attrition-Aware Compaction: Honest Status

This carrier is now structurally attrition-aware:

- alive ratio drives target extent contraction
- the extent state relaxes continuously
- broad band ownership is stable
- within-band compaction is soft and local

However, the primary validation scene in this turn is still neutral transit with no attrition event.  
So the current validation strength is:

- structural and code-level confidence: yes
- direct human-readable casualty-driven compaction confirmation: not yet the main evidence of this turn

That should be treated honestly.  
This turn proves the carrier exists and is semantically clean; it does not yet claim that casualty-driven compaction has already been fully human-validated.

## Secondary Battle Read

This turn intentionally does not let hostile-contact work swallow PR #6.

Secondary battle sanity only confirmed:

- `movement_model_effective = v4a`
- `reference_surface_mode_effective = soft_morphology_v1`
- `expected_reference_spacing_effective = 2.0`
- `physical_min_spacing_effective = 1.0`
- `battle_restore_bridge_active = True`

So maintained battle still sees the branch semantics.  
But no new hostile-contact carrier is opened in this batch.

## `X-forward`, `XYZ = 4 / 5 / 4`: Honest Read

Current honest maintained read after this turn:

- `X-forward` planar reference ownership is real
- `Y` lateral target now participates in runtime-owned planar morphology
- `Z` is still a forward-looking intent only

So the branch can now honestly claim:

- first credible soft planar formation substrate candidate

It still cannot honestly claim:

- full `XYZ = 4 / 5 / 4` runtime-owned formation
- solved volumetric 3D formation semantics

## What Improved

- PR #6 now has a true reference-surface carrier shift, not just more restore tuning
- exact-slot zero-error rigid lock is no longer the only available v4a read
- broad topology now has a stable source-of-truth
- the carrier is deterministic, bounded, and keeps the existing split/restore semantics intact

## What Remains Unclear or Incomplete

- neutral-transit still reads too clean/tight for merge discussion
- the main remaining issue no longer looks like simple restore-strength tuning
- the next formation-side iteration should likely focus on further loosening within-band / within-envelope behavior rather than reopening hostile contact or returning to scalar restore tuning

## Recommendation

Recommendation:

- `B`

Interpretation:

- restore-line reality is preserved
- soft morphology carrier reality is now established
- but one more bounded formation-side iteration is still needed before merge discussion quality

The reason is formation-side incompleteness:

- the new carrier is real
- but its current neutral-transit read is still too close to an over-clean planar hold

## Bottom Line

PR #6 now carries more than a rigid slot-map bridge.

The branch now has:

- real expected/reference spacing
- real physical minimum spacing
- real restore bridge
- and a first bounded soft planar morphology carrier

That is meaningful progress.  
But the current carrier still reads more "disciplined and compressed" than "stable and alive".

So this turn should be read as:

- first soft-carrier success
- not yet final formation-substrate completion
