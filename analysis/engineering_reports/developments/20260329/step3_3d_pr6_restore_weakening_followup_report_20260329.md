# Step 3 3D PR #6 Restore Weakening Follow-Up Report (2026-03-29)

Engine Version: `dev_v2.0`  
Modified Layer: `test_run/` candidate plumbing plus report/artifact package only  
Affected Parameters: test-only `runtime.movement.v4a.test_only.restore_strength` only; no public runtime surface expansion  
New Variables Introduced: one bounded `v4a` restore-strength control routed through the existing harness movement surface  
Cross-Dimension Coupling: none beyond the existing `v4a` battle/fixture restore bridge already active on PR #6  
Mapping Impact: none  
Governance Impact: keeps PR #6 on the formation-substrate main line; proves the next issue is more basic than restore-strength tuning alone  
Backward Compatible: yes; `v3a` remains retained and no default switch is made

## Summary

- This turn keeps the current two-layer spacing split and restore bridge intact, then tests the preferred first relaxation direction: continuous weaker restore.
- A new bounded test-only `v4a` restore-strength control is added on the PR branch without touching the frozen runtime core.
- The primary neutral-transit result is unexpectedly hard: once the split is active, weakening restore from `1.0` down to `0.25` and even `0.05` does not materially change the formation read.
- So the current "too close to hard lock" read is not mainly a restore-strength problem in the present primary scene.
- The line still preserves semantically real expected/reference spacing, real restore, and real physical minimum spacing.
- But the intended first formation read `X-forward`, `XYZ = 4 / 5 / 4` is only partially represented today: the maintained path honestly carries a projected planar `X-forward` reference read, not full 3D runtime formation ownership.
- Secondary hostile-contact read remains unchanged: interleaving is still a later contact-substrate problem, not a reason to roll back formation-side gains.

## Files Changed

- `test_run/settings_accessor.py`
- `test_run/test_run_scenario.py`
- `test_run/test_run_execution.py`
- `test_run/test_run_v1_0.testonly.settings.json`
- `test_run/test_run_v1_0.settings.comments.json`
- `test_run/test_run_v1_0.settings.reference.md`
- `analysis/engineering_reports/developments/20260329/step3_3d_pr6_restore_weakening_followup_report_20260329.md`
- `analysis/engineering_reports/developments/20260329/step3_3d_pr6_restore_weakening_neutral_transit_comparison_20260329.csv`
- `analysis/engineering_reports/developments/20260329/step3_3d_pr6_restore_weakening_neutral_transit_plot_20260329.png`
- `repo_context.md`
- `system_map.md`

## Weakening Seam Chosen

This turn follows Governance's preferred order:

- continuous weaker restore first
- no pulse-based sparse restore
- no runtime-core rewrite

The chosen seam is the smallest currently available branch-local weakening point:

1. expose test-only `runtime.movement.v4a.test_only.restore_strength`
2. validate it in `test_run/test_run_scenario.py`
3. route it in `test_run/test_run_execution.py` through the existing harness-consumed movement surface by scaling the current centroid/restore probe path for `v4a`

This keeps the change bounded:

- no `runtime/engine_skeleton.py` edits
- no new public parameter surface
- no cadence-based restore behavior
- no turning-cost implementation

## Primary Validation Path

Primary scene:

- `neutral_transit_v1`

Compared modes:

- coupled baseline:
  - `expected_reference_spacing = 2.0`
  - `min_unit_spacing = 2.0`
  - `restore_strength = 1.0`
- split candidate, full restore:
  - `expected_reference_spacing = 2.0`
  - `min_unit_spacing = 1.0`
  - `restore_strength = 1.0`
- split candidate, weakened restore:
  - `expected_reference_spacing = 2.0`
  - `min_unit_spacing = 1.0`
  - `restore_strength = 0.25`
- split candidate, extreme probe:
  - `expected_reference_spacing = 2.0`
  - `min_unit_spacing = 1.0`
  - `restore_strength = 0.05`

Shared read:

- `movement_model_effective = v4a`
- `reference_layout_mode = rect_centered_rows`
- aspect ratios:
  - `1.0`
  - `4.0`

Primary human-readable artifact set:

- `analysis/engineering_reports/developments/20260329/step3_3d_pr6_restore_weakening_neutral_transit_comparison_20260329.csv`
- `analysis/engineering_reports/developments/20260329/step3_3d_pr6_restore_weakening_neutral_transit_plot_20260329.png`

## Primary Finding

### The substrate semantics remain real

After this turn, PR #6 still preserves:

- real expected/reference spacing meaning
- real restore-line meaning
- real split from physical minimum spacing

The new weakening seam does not collapse those meanings.

### But weakening restore does not materially change the primary scene

For `aspect_ratio = 1.0` at `tick = 100`:

- coupled `2.0 / 2.0`:
  - `width_depth_ratio = 0.793689`
  - `front_extent_ratio = 1.501920`
  - `expected_position_rms_error = 1.169338`
- split `2.0 / 1.0`, `restore_strength = 1.0`:
  - `width_depth_ratio = 1.000000`
  - `front_extent_ratio = 1.000000`
  - `expected_position_rms_error = 0.000000`
- split `2.0 / 1.0`, `restore_strength = 0.25`:
  - identical to `restore_strength = 1.0`
- split `2.0 / 1.0`, `restore_strength = 0.05`:
  - identical to `restore_strength = 1.0`

For `aspect_ratio = 4.0` at `tick = 100`:

- coupled `2.0 / 2.0`:
  - `width_depth_ratio = 2.696451`
  - `front_extent_ratio = 2.219583`
  - `expected_position_rms_error = 1.252447`
- split `2.0 / 1.0`, `restore_strength = 1.0`:
  - `width_depth_ratio = 4.750000`
  - `front_extent_ratio = 1.000000`
  - `expected_position_rms_error = 0.000000`
- split `2.0 / 1.0`, `restore_strength = 0.25`:
  - identical to `restore_strength = 1.0`
- split `2.0 / 1.0`, `restore_strength = 0.05`:
  - identical to `restore_strength = 1.0`

The plot shows the same read visually:

- the coupled baseline stretches strongly
- all split/restore-strength curves lie exactly on top of one another

Engineering read:

- the current neutral-transit "hard-lock" impression is more basic than restore-strength tuning alone
- once the split is active, the primary scene carries effectively zero slot error, so weakening restore does not get meaningful room to act

## Intended First Formation Read: What Is Expressed vs Not Yet Expressed

Governance asked this turn to use:

- `X-forward`
- `XYZ = 4 / 5 / 4`

as the intended first formation-reference read.

Current honest runtime expression:

- `X-forward` is expressed as a projected planar forward-axis reference read
- reference layout is expressed as `rect_centered_rows`
- expected/reference spacing is expressed explicitly through `expected_reference_spacing`
- formation preservation is expressed in the current maintained path only as a bounded planar restore/substrate behavior

What is not honestly carried yet:

- full 3D volumetric `XYZ = 4 / 5 / 4` runtime ownership
- explicit `Y/Z` formation-depth / vertical-substrate ownership
- true 3D shape maintenance semantics

So the branch can honestly claim:

- first credible planar formation-reference substrate candidate

but not yet:

- solved first full 3D formation runtime

## Secondary Hostile-Contact Read

No new hostile-contact implementation work is added in this turn.

Current read remains the same as the earlier PR #6 follow-up package:

- hostile interleaving remains a later contact-substrate issue
- it is not a reason to roll back the formation-side gains
- it also does not change the primary conclusion of this turn, which is formation-side: restore weakening does not materially relax the current neutral-transit substrate read

## What Improved

- PR #6 now has a bounded test-only restore-strength control instead of only a fixed full-strength bridge
- the branch can now answer the "weaken restore first" question directly rather than by conjecture
- the answer is clean: current primary-scene rigidity is not mainly caused by restore strength itself

## What Remains Incomplete

- the neutral-transit candidate still reads too close to hard geometry lock
- the intended first formation read is only partially represented because the branch still expresses a planar projected substrate, not full `XYZ = 4 / 5 / 4` ownership
- the next formation-side question is therefore more basic than scalar restore weakening

## Recommendation

Recommendation target:

- `D`

Interpretation:

- current maintained path cannot yet honestly carry the intended first formation read in the stronger `XYZ = 4 / 5 / 4` sense
- restore weakening did not solve the present formation-side incompleteness
- the next bounded iteration should therefore clarify the more basic substrate read rather than immediately continuing scalar restore tuning

## Bottom Line

This turn does not roll back PR #6's core gains:

- expected/reference spacing remains real
- restore remains real
- physical minimum spacing remains real

But it does sharpen the branch diagnosis:

- the current neutral-transit hard-lock read is not materially improved by weaker continuous restore alone
- so the remaining problem sits deeper than the first restore-strength knob
- PR #6 should continue, but the next step should be a more basic formation-substrate clarification rather than another simple scalar weakening pass
