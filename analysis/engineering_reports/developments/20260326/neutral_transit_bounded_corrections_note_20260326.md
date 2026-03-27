# Neutral Transit Bounded Corrections Note (2026-03-26)

Engine Version: `dev_v2.0`
Modified Layer: bounded neutral-transit fixture mechanism only
Affected Parameters: no user-facing parameters; internal use of existing `stop_radius` and `separation_radius`
New Variables Introduced: internal fixed `restore_deadband = 0.28 * separation_radius`
Cross-Dimension Coupling: none
Mapping Impact: none
Governance Impact: implements the authorized bounded neutral-transit corrections only
Backward Compatible: yes, outside `neutral_transit_v1`

Summary
- Implemented A1 late-phase linear arrival gain on the bounded fixture objective path.
- A1 uses only the existing `stop_radius`.
- No extra radius, taper family, or fallback mode was introduced.
- Implemented B1 hard restore deadband on the bounded fixture expected-position cohesion path.
- B1 uses only the existing `separation_radius` through one fixed internal ratio.
- No settings growth, no user parameter, and no generalized framework work was introduced.

## 1. Scope

This change is limited to the current bounded `neutral_transit_v1` path.

Touched code paths:

- `test_run/test_run_execution.py`
- `runtime/engine_skeleton.py`

Untouched:

- viewer-local direction modes
- replay protocol
- mapping / legality / combat
- generalized formation runtime

## 2. A1 Late-Phase Linear Arrival Gain

The fixture objective path now applies:

- `gain = clamp(d / stop_radius, 0, 1)` when `stop_radius > 0`
- existing behavior when `stop_radius <= 0`

where:

- `d = centroid_to_objective_distance`

The bounded fixture target output now becomes:

- `target_direction = normalized_direction_to_objective * gain`

This uses only the already existing `stop_radius`.

No additional:

- taper radius
- second radius
- latch family
- mode switch

was introduced.

## 3. B1 Early-Phase Hard Restore Deadband

The bounded fixture expected-position restore path now applies one hard deadband before consuming the expected-position cohesion term.

Rule:

- when `cohesion_norm < restore_deadband`, the fixture expected-position cohesion term is zeroed
- otherwise the existing cohesion term path is preserved

Binding:

- `restore_deadband = 0.28 * separation_radius`

This is:

- internal only
- fixed
- not exposed through settings
- not paired with a second threshold or taper band

## 4. Why This Stays Bounded

These corrections do not create:

- a generalized objective-arrival family
- a generalized restore smoothing family
- a new settings surface
- a new strategy registry

They are narrow corrections on the already active bounded neutral-transit carrier only.

## 5. Implementation Reading

The intended reading of this turn is:

- A1 reduces objective pull magnitude inside the already existing stop radius
- B1 suppresses very small expected-position corrections on the bounded fixture path

That is all.

This turn does not claim the neutral-transit line is fully solved.
