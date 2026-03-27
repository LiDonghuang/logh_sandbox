# dev_v2.0 Realistic Direction Mode Note (2026-03-26)

Engine Version: `dev_v2.0`
Modified Layer: additive `viz3d_panda/` viewer-local direction readout layer only
Affected Parameters: viewer-local `direction_mode` readout selection in the Panda3D viewer
New Variables Introduced: viewer-local `realistic` direction mode
Cross-Dimension Coupling: consumes already-owned replay positions to derive local realized-path tangent; does not change runtime ownership
Mapping Impact: none
Governance Impact: adds the authorized viewer-local `realistic` direction visualization mode alongside existing modes
Backward Compatible: yes

Summary
- Added `realistic` as a new viewer-local direction mode alongside existing settings-driven direction readouts.
- `realistic` is defined as a realized-path-oriented cue, not an upstream intent vector.
- It prefers centered local tangent from adjacent replay frames.
- When centered tangent is unavailable, it falls back to one-sided realized displacement.
- Near stall / near arrival, it holds the most recent non-degenerate realistic direction instead of amplifying tiny positional noise.
- Only bootstrap cases fall back to existing orientation/effective reading.
- No runtime, replay-ownership, or semantics-layer change was introduced.

## 1. Scope

This change is confined to `viz3d_panda/` readout consumption only.

It does not change:

- runtime movement semantics
- target logic
- restore/projection logic
- battle or fixture meaning
- replay ownership

## 2. Human-Facing Surface

The viewer now accepts:

- `--direction-mode settings`
- `--direction-mode effective`
- `--direction-mode free`
- `--direction-mode fire`
- `--direction-mode composite`
- `--direction-mode radial_debug`
- `--direction-mode realistic`

`fire` is exposed as the viewer-facing name for the existing attack-direction readout.

`settings` preserves the currently layered 2D `vector_display_mode`.

## 3. realistic Semantics

`realistic` is a:

- post-result
- realized-path oriented
- local trajectory tangent cue

Its purpose is to answer:

how does the unit look like it is actually moving through this local part of the replay?

It is not a claim that:

- runtime movement truth has changed
- intent vectors are wrong
- the viewer now owns canonical movement semantics

## 4. Calculation Rule

Per unit and per frame, the readout order is:

1. centered local tangent from adjacent replay frames
2. one-sided realized displacement when centered tangent is unavailable
3. hold the most recent non-degenerate realistic direction when local displacement is too small
4. use existing orientation/effective reading only as a bounded bootstrap fallback

This keeps realized-path reading primary and fallback secondary.

## 5. Near-Arrival Stability Rule

The `realistic` mode includes a small viewer-local displacement threshold before accepting a new tangent.

When the local replay displacement drops below that threshold:

- the viewer does not invent a new direction from tiny noise
- it reuses the last valid realistic direction for that unit

This is intended to reduce the late-stage visual jitter amplification that can appear when the carrier is already flattening near arrival.

## 6. Current Boundaries

The current `realistic` mode still does not authorize:

- runtime-side smoothing
- new replay protocol fields
- formation semantics changes
- legality changes
- viewer-owned fallback rules outside readout

It is a display clarification only.
