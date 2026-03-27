# Late Terminal Settle - Orientation Freeze / Live-Centroid Engineering Read

Date: 2026-03-27
Status: engineering read after bounded split cut

## Main read

The current split cut appears to answer the prior first-cut question correctly:

- freezing the terminal centroid together with the terminal axis was too much
- freezing only the terminal axis while letting the expected-position center follow the live centroid is materially better

The strongest evidence is:

- `centroid_to_objective_distance final` returns from `0.428314` to `0.055162`
- `tick 430` no longer shows whole-frame-freeze-style cohesion resurgence
- `mean_cohesion_norm` drops sharply relative to the prior frozen-centroid cut

So the prior suspicion was directionally right:

- the first-cut whole-frame freeze introduced a wrong-center tug-of-war
- this split cut removes most of that specific mismatch

## What the split cut did not close

The residual did not disappear; it changed shape.

Current tail read:

- `tick 428`: still mixed `target + cohesion`
- `tick 429`: mostly `separation`
- `tick 430`: overwhelmingly `separation`

That suggests the strongest remaining late-tail path is no longer:

- frozen centroid mismatch

but more likely:

- unit-level spacing / projection reshaping after centroid-level arrival is already effectively established

In other words:

- the restore-center problem was real
- but it was not the last remaining root

## Current best next suspicion chain

After this split cut, the current strongest ordering looks like:

1. separation residual in the terminal zone
2. projection reshaping coupled to that spacing residual
3. smaller leftover target pull
4. restore/cohesion as a reduced secondary effect

This is narrower than the prior root-cause state.

## Recommendation

Engineering should not reopen viewer work from this result.

The current best next bounded question is:

- why unit-level separation/projection remains so active after centroid-level arrival has effectively settled

not:

- whether the frozen terminal reference center should still be adjusted again

and not:

- whether realistic / smoothing needs to be reopened

## Honest boundary

This note does not claim the late-terminal problem is solved.

Current best statement is:

- the whole-frame freeze hypothesis has been successfully narrowed
- the split cut is structurally better
- the remaining root path now looks more like late terminal spacing/projection residual than restore-center mismatch

Later human 3D review also confirmed that this split cut remained visibly broken in the terminal window, so this document should be read as an intermediate narrowing result, not as an accepted fix.
