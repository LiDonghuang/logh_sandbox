# Engineering Diagnostic Note - Shared Connectivity Defect

## Purpose

Record the concrete engineering interpretation from the two DOE rounds, so later cohesion-collapse redesign work starts from the corrected premise.

## Corrected Premise

The earlier provisional read was:

- `v2` low early because of elongation
- `v3_test` low early because of rho-scale penalty

That read is no longer defensible.

## What The Data Actually Says

### From the 66-run component diagnostic

For Side A pre-contact:

- `v2`
  - `A_v2_mean = 0.0391`
  - dominant penalty: `fragmentation` in `33 / 33` runs

- `v3_test`
  - `A_v3_mean = 0.2460`
  - `A_c_conn_mean = 0.2460`
  - `A_c_scale_mean = 1.0000`
  - `rho` remained in-band in all runs

Therefore:

- `v2` low value = mainly low LCC ratio
- `v3_test` low value = mainly low connectivity ratio
- scale penalty did not meaningfully activate in this diagnostic domain

### From the 648-run source DOE

The practical runtime symptom is:

- `first_deep_pursuit_tick = 1.0` under both sources

That is exactly what should happen if both source signals are already numerically low enough at the start.

## Strong Engineering Inference

The problem is not merely "which source is better."

The likely structural defect is:

`the current adjacency / LCC connectivity definition is too strict for fleet-scale pre-contact formations`

This inference is justified because:

1. both sources share the same connectivity backbone
2. both become low very early
3. the scale term did not activate
4. outlier mass did not dominate
5. elongation did not dominate

## Practical Consequences

1. Any future collapse-signal design that keeps the same harsh connectivity backbone may reproduce the same low-value problem even if the top-level formula changes.
2. Replacing `v2` with `v3_test` now would likely change runtime intensity, but would not solve the deeper semantic defect.
3. Human-facing plots are currently telling the truth: early low cohesion is not a plotting bug.

## What To Preserve

The current investigation should preserve:

- movement baseline `v3a`
- bridge thresholds as working defaults
- paired seed discipline
- observer/report separation

## What To Revisit Next

If governance authorizes a new cohesion-collapse design phase, the first engineering target should be:

`connectivity semantics`

Candidate questions:

1. Should connectivity use a more permissive graph radius?
2. Should it use local-neighbor robustness instead of a single LCC ratio?
3. Should runtime collapse signal distinguish:
   - geometry stress
   - true fragmentation
4. Should pre-contact fleets be evaluated with a more conservative collapse interpretation than post-contact fleets?

## Current Status

Use this note as the engineering anchor for upcoming cohesion-collapse mechanism discussion.

It replaces the earlier informal hypothesis that blamed `elongation` and `rho` first.
