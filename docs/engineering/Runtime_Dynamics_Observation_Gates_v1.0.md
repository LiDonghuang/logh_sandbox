# Runtime Dynamics Observation Gates v1.0

Status: active engineering standard  
Scope: motion / formation / targeting / hold-terminal / battle-geometry development and validation

## Purpose

This standard defines the minimum observation gates for runtime-dynamics work.

These gates are not "human-only" review aids. They are basic runtime-development requirements because they describe:

- where the fleet body is actually going
- whether a coherent alive-unit body still exists

Both are already lightweight and already tracked by the harness, so they must be treated as routine validation surfaces rather than optional extras.

## Required Gates

Any candidate that materially affects motion, formation, targeting, hold/terminal, or battle engagement geometry must explicitly check:

1. fleet-centroid trajectory
2. alive-unit body observation
3. fire-efficiency observation for battle-facing cases

## Gate 1. Fleet-Centroid Trajectory

Minimum read:

- are fleet centroids still approaching, holding, separating, or drifting in the intended way?
- did a candidate accidentally zero or misroute ownership and cause centroids to stall, rebound, or retreat?
- does the centroid path still describe one coherent battle/transition body?

It is not enough for local unit motion or scalar indicators to look cleaner if centroid behavior is clearly wrong.

## Gate 2. Alive-Unit Body Observation

Minimum read:

- do alive units still form one coherent body?
- are units being squeezed out, scattered, or split into misleading shell-only success?
- is the candidate preserving a believable active body rather than only improving an external outline?

It is not enough for the outer silhouette to look correct if the alive-unit interior has become chaotic or incoherent.

## Gate 3. Fire-Efficiency Observation

Minimum read for battle-facing cases:

- how much actual damage per tick is being realized relative to theoretical per-tick damage potential?
- is the battle body entering a relation that only produces edge-contact or low-efficiency grazing?
- did a candidate improve outline or spacing while silently collapsing combat effectiveness?

Current default read:

- `fire_efficiency = actual_damage / theoretical_damage_potential`
- per fleet, per tick
- using the already-established 2D/report-side definition

This gate is not applicable to pure neutral/no-enemy validation runs, but it is mandatory on battle authority surfaces.

## Acceptance Rule

A candidate is not acceptable if either gate clearly fails, even when:

- local scalar metrics improve
- ownership logic looks cleaner
- one surface indicator appears to support the change

When Human motion read and scalar neatness diverge, the motion/body read remains authoritative.

## Current Mandatory Use

These gates are currently mandatory for:

- formation-transition carrier work
- battle-first hold / terminal semantics
- battle engagement geometry changes
- targeting / fire-distribution correction work

## Reporting Expectation

Reports and local notes for the lines above should explicitly state:

- what centroid behavior was observed
- what alive-unit body behavior was observed
- what fire-efficiency behavior was observed on battle runs
- which gate or gates failed

Do not collapse both into a single vague "looked chaotic" judgment.
