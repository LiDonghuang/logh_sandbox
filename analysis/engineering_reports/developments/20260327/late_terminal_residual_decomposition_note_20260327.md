# Late Terminal Residual Decomposition Note (2026-03-27)

Status: debug-only decomposition
Carrier: `neutral_transit_v1`
Window: `tick 420 .. 430` around `objective_reached_tick=425`

## Scope

This turn decomposes per-unit late-terminal movement only. No late mechanism, viewer mode, or visual system change is implemented here.

## Window facts

- `objective_reached_tick = 425`
- requested window = `t* +/- 5`
- actual window = `tick 420 .. 430`
- detailed rows exported = `1100`
- summary rows exported = `12`

## High-level split

Before the fleet centroid enters the stop-radius window (`tick 420 .. 425`):
- target pull dominates all `600 / 600` rows
- projection is zero
- separation is zero
- cohesion exists, but is secondary (`mean cohesion norm = 0.147` vs `mean target norm = 1.027`)

Inside the stop-radius window (`tick 426 .. 430`):
- the motion mix changes materially
- target is no longer the clear only driver
- mean norms become:
  - `target = 0.500922`
  - `cohesion = 0.638970`
  - `separation = 0.220888`
  - `projection = 0.121652`
  - `late_clamp = 0.068285`

## Per-tick terminal read

- `tick 426`: target still dominates (`100 / 100` rows)
- `tick 427`: target still dominates, but cohesion rises sharply and late clamp becomes active/nonzero for all rows
- `tick 428`: cohesion dominates all rows (`100 / 100`)
- `tick 429`: cohesion remains largest block, separation becomes strong, projection starts showing on many units
- `tick 430`: separation becomes the largest block, with cohesion still large and projection still active

## Projection / clamp relation

- inside the stop-radius window, `mean(realized_minus_pre_projection_norm) = 0.177766`
- that value matches `projection + late clamp` exactly in the exported rows
- this means the difference between tentative movement and realized unit displacement is being produced by post-movement correction, not by hidden viewer-side behavior

## Current read

The current best decomposition is:
- outside the terminal zone: target pull is still the sole practical driver
- just inside the terminal zone: target pull remains present, but moving expected-position restore rapidly grows to the same order or larger
- after centroid-level arrival: separation and projection become secondary but real reshapers of the still-moving unit field
- boundary contribution stays zero in this carrier/window

## Strongest root-path read

The single most actionable root path currently looks like:
- **moving expected-position restore remaining active after centroid-level arrival**

with the next layer being:
- separation + post-movement projection reshaping the resulting unit motion

That is stronger than a pure "projection-only" explanation, and also stronger than a pure "target pull never turned off" explanation.
