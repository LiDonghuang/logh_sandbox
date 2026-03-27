# Governance Feedback - Late Terminal Step-Magnitude + One-Sided Axial Restore

Date: 2026-03-27
Status: engineering feedback for Governance review
Scope: bounded `neutral_transit_v1` late-terminal candidate only

## Summary

Engineering now has a stronger bounded local candidate than the prior freeze-only cuts:

- orientation-freeze / live-centroid split cut
- plus terminal step-magnitude gate
- plus one-sided axial restore gate

Current local read is:

- this is the best late-terminal candidate so far
- it preserves arrival timing
- it reduces terminal motion heavily
- it survives human 3D review much better than the earlier cuts

## What should be read as accepted

The currently accepted local candidate is:

- orientation frozen
- expected-position center still live
- step magnitude reduced inside the terminal window
- only backward axial restore softened

Human review currently accepts this as the correct local version.

## What should be read as rejected

The stricter local follow-up:

- `no-net-backward axial clamp`

should be read as locally disproven.

It removed the last two backward units, but created a worse visible side effect:

- prolonged left rotation of the same frontmost units
- then a snap-back one tick later

Engineering explicitly rejected that branch and reverted it locally.

## Why this matters beyond the late terminal case

Engineering also asks Governance to think about one broader implication:

- this late-terminal result may matter for the early restoration problem too

The reason is structural:

- deadband-only thinking was not enough
- frame-freeze variants were not enough
- the successful bounded improvement came from treating restore as a directional/component-wise problem

That does not mean early restoration should now be silently changed.
It means the late-terminal investigation has produced a useful design hint:

- early restoration trouble may also be partly about backward-vs-forward or axial-vs-lateral compatibility, not only scalar tolerance

## Recommended Governance reading order

1. `analysis/engineering_reports/developments/20260327/late_terminal_orientation_freeze_live_centroid_validation_note_20260327.md`
2. `analysis/engineering_reports/developments/20260327/late_terminal_step_magnitude_one_sided_restore_validation_note_20260327.md`
3. `analysis/engineering_reports/developments/20260327/late_terminal_step_magnitude_one_sided_restore_engineering_read_20260327.md`

## Current engineering stance

Current stance is not:

- generalized closure claimed

Current stance is:

- best bounded late-terminal candidate so far
- third stricter clamp rejected
- early-restoration implication worth future Governance thought
