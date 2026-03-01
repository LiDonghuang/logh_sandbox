# Phase V.2 Chronicle --- Mobility Bias Canonical Mapping Activation (v5.0-alpha4)

## Governance Anchor
- Phase V default combat baseline is fixed to `attack_range = 5.0`.
- This default is stage-scoped and not bound to arena size, spacing, or unit class.
- No targeting logic upgrade is included in this phase.

## Activated Change (Movement Layer Only)
- `mobility_bias` is promoted from experimental knob to canonical runtime mapping.
- Canonical mapping:
  - `MB_eff = 0.2 * (mobility_bias - 5) / 5`
  - clipped to `[-0.2, +0.2]`
- Insertion point remains pre-normalization inside movement composition.
- Only the non-cohesion maneuver vector is reweighted.

## Preserved Constraints
- Cohesion logic unchanged.
- FSR logic unchanged.
- Targeting logic unchanged.
- Combat resolution unchanged.
- Projection remains single-pass and unchanged.
- No stochastic branch added.

## Regression Contract
- `mobility_bias = 5` must remain baseline-equivalent.
- Determinism remains required.
- Mirror / jitter / attractor proxy / runtime overhead gates apply per Governance V2.1.
