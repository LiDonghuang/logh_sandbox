# Late Terminal Settle - Step-Magnitude + One-Sided Axial Restore

Date: 2026-03-27
Status: local bounded candidate
Scope: bounded `neutral_transit_v1` late-terminal correction only

## Scope

This record describes the current best local late-terminal candidate on the bounded:

- `fixture.active_mode = neutral_transit_v1`
- single-fleet fixture path
- `expected_position_candidate_active = True`
- maintained `movement_model = v4a`

This is not a generalized runtime terminal framework turn.

## Current accepted candidate

The current local candidate keeps the prior:

- orientation-freeze / live-centroid split cut

and adds two narrower terminal-zone corrections:

1. terminal step-magnitude gate
   - inside the existing `stop_radius` window, actual per-unit step magnitude is scaled by the same existing `distance_to_objective / stop_radius` ratio
   - this uses only existing bounded quantities
   - no new user parameter, settings surface, or helper family is added

2. one-sided axial restore gate
   - inside the same bounded terminal window, fixture expected-position cohesion is decomposed into axial and lateral parts
   - only the negative axial restore component is attenuated
   - positive axial restore and lateral restore are left untouched

The resulting local candidate is therefore:

- orientation frozen
- expected-position center live
- terminal per-unit step magnitude reduced continuously near the anchor
- only backward axial restore softened

## What this replaces

This candidate supersedes the weaker local split-cut-only state where:

- expected-position orientation was frozen
- expected-position center followed the live centroid
- but per-unit step magnitude still remained effectively full in the terminal zone

That earlier state restored arrival integrity but still left a strong late tail.

## What this candidate does not add

This candidate does not add:

- new user parameters
- new settings surface
- restore taper family
- generalized terminal framework
- viewer / realistic / smoothing changes

## Important local rejection

A narrower-looking third follow-up was also tested locally and then rejected:

- `no-net-backward axial clamp`

That extra clamp removed the last two backward units at `tick 428`, but introduced a new visible artifact:

- the same two frontmost units kept rotating left from `tick 425 .. 430`
- and then snapped back at `tick 431`

That local branch was therefore reverted.

## Current read

The current accepted candidate is the first local late-terminal version that:

- keeps arrival timing intact
- compresses terminal per-unit motion by a large factor
- removes the mass backward settle after `tick 428`
- survives human 3D inspection as the best current version

It should be read as a bounded candidate only, not as a silent generalized policy.
