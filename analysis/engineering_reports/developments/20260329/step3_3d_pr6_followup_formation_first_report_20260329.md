# Step 3 3D PR #6 Follow-Up Formation-First Report (2026-03-29)

Engine Version: `dev_v2.0`  
Modified Layer: report / artifact package only on top of the existing PR #6 candidate branch  
Primary Read: formation substrate validation first  
Secondary Read: hostile-contact exposure only  
Governance Impact: no new implementation surface; this turn tightens the review read of the existing candidate

## Purpose

This follow-up keeps PR #6 focused on the formation substrate question:

- does the current `v4a + restore bridge + two-layer spacing split` line now form the first genuinely credible formation substrate candidate?

Hostile penetration is carried only as a secondary bounded probe:

- useful future 3D contact-substrate groundwork
- not the dominant objective of the turn

## Files / Artifacts

Main report:

- `analysis/engineering_reports/developments/20260329/step3_3d_pr6_followup_formation_first_report_20260329.md`

Primary neutral-transit artifact set:

- `analysis/engineering_reports/developments/20260329/step3_3d_pr6_followup_neutral_transit_compact_comparison_20260329.csv`
- `analysis/engineering_reports/developments/20260329/step3_3d_pr6_followup_neutral_transit_comparison_plot_20260329.png`

Secondary hostile-contact probe artifact:

- `analysis/engineering_reports/developments/20260329/step3_3d_pr6_followup_hostile_contact_probe_frames_20260329.png`

## Validation Setup

Primary scene:

- `neutral_transit_v1`

Compared modes:

- coupled baseline:
  - `expected_reference_spacing = 2.0`
  - `min_unit_spacing = 2.0`
- candidate split:
  - `expected_reference_spacing = 2.0`
  - `min_unit_spacing = 1.0`

Common conditions:

- `movement_model_effective = v4a`
- `reference_layout_mode = rect_centered_rows`
- fixed seeds:
  - `run_control.random_seed = 20260329`
  - `runtime.metatype.random_seed = 20260329`
  - `battlefield.background_map_seed = 20260329`
- aspect ratios compared:
  - `1.0`
  - `4.0`

Secondary scene:

- maintained battle path
- same active branch candidate
- bounded contact-window frame sheet around ticks:
  - `208`
  - `211`
  - `214`
  - `215`

## Primary Finding: Semantics Are Real

The current branch now supports a semantically real split between:

- expected/reference spacing
- physical minimum spacing

and a semantically real restore line for `v4a`:

- `expected_reference_spacing` now lives on the direct `v4a` test-only surface
- `min_unit_spacing` now reads as the physical-layer floor
- `neutral_transit_v1` and maintained battle both consume the same `v4a` reference meaning

So the line has passed the earlier question:

- this is no longer just a label or a fixture-only reading

## Primary Finding: Neutral Transit Is Clear but Too Strong

The neutral-transit validation is strong enough to show that the candidate is readable, stable, and repeatable.

For the candidate split:

- `aspect_ratio = 1.0`
  - `tick 1 / 20 / 50 / 100 / 200 / 300 / 443`
  - `width_depth_ratio = 1.000000`
  - `front_extent_ratio = 1.000000`
  - `expected_position_rms_error = 0.000000`
  - `projection_pairs_count = 0`
  - `corrected_unit_ratio = 0.000000`

- `aspect_ratio = 4.0`
  - `tick 1 / 20 / 50 / 100 / 200 / 300 / 443`
  - `width_depth_ratio = 4.750000`
  - `front_extent_ratio = 1.000000`
  - `expected_position_rms_error = 0.000000`
  - `projection_pairs_count = 0`
  - `corrected_unit_ratio = 0.000000`

Against that, the coupled baseline still shows the earlier stretch:

- `aspect_ratio = 1.0 @ tick 300`
  - `width_depth_ratio = 0.720149`
  - `front_extent_ratio = 1.393291`
  - `expected_position_rms_error = 1.852895`

- `aspect_ratio = 4.0 @ tick 300`
  - `width_depth_ratio = 2.902100`
  - `front_extent_ratio = 1.692733`
  - `expected_position_rms_error = 1.099898`

This proves:

- the split is semantically real
- the restore line is semantically real
- the candidate is readable and repeatable

But it also shows:

- the current neutral-transit result is too strong to read as an emergent formation substrate
- it currently reads as a hard geometry lock rather than a merely credible substrate foundation

So the branch has not yet passed the merge-read test on the primary line.

## Secondary Finding: Hostile Contact Is Exposed More Clearly

The secondary hostile-contact probe continues to support the current layered read:

- formation-side gains should not be rolled back
- hostile interleaving is a later contact-substrate problem

The contact-window frame sheet shows that once fleets meet, the current branch makes the old penetration/interleaving behavior easier to see.

Runtime debug from the sampled contact window also rises sharply:

- `tick 208`
  - `projection_pairs_count = 5`
  - `corrected_unit_ratio = 0.05`
- `tick 211`
  - `projection_pairs_count = 17`
  - `corrected_unit_ratio = 0.17`
- `tick 214`
  - `projection_pairs_count = 56`
  - `corrected_unit_ratio = 0.5628`
- `tick 215`
  - `projection_pairs_count = 62`
  - `corrected_unit_ratio = 0.6212`

Engineering read:

- this is an important exposure
- but it remains secondary in this turn
- it should not be used to collapse the formation-substrate line back into the old overloaded spacing regime

## What Improved

- PR #6 now supports a real expected/reference spacing meaning
- PR #6 now supports a real restore line that is visible in both neutral-transit and maintained battle
- the spacing split is now semantically real rather than implicit
- neutral-transit evidence is strong enough to count as the first convincing formation-substrate evidence package
- hostile penetration now reads more clearly as a future contact-substrate problem rather than a reason to deny the spacing split

## What Remains Incomplete

- the current neutral-transit candidate is too rigid
- the branch does not yet show the desired "readable but not locked" formation behavior
- contact-side interleaving remains unresolved
- the branch therefore still needs one more bounded iteration before merge discussion

## Recommendation

Recommendation target:

- `C`

Interpretation:

- PR #6 should not merge yet
- the reason is formation-side validation incompleteness
- the current neutral-transit result is still too close to hard geometry lock
- hostile-contact issues remain important, but they are not the primary reason to hold the branch

## Bottom Line

PR #6 has now crossed an important threshold:

- it is the first branch on this line that makes expected/reference spacing, restore, and spacing split all semantically real together

But it has not yet reached merge discussion quality:

- the next bounded round should keep formation substrate first
- and specifically weaken or relax the current hard-lock read in neutral transit before merge discussion is reopened
