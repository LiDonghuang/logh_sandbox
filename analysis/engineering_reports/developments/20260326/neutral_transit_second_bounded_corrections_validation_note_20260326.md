# Neutral Transit Second Bounded Corrections Validation Note (2026-03-26)

Engine Version: `dev_v2.0`
Modified Layer: bounded neutral-transit validation note only
Affected Parameters: none
New Variables Introduced: none
Cross-Dimension Coupling: none
Mapping Impact: none
Governance Impact: records validation of the authorized second bounded correction turn only
Backward Compatible: yes

Summary
- Validation stayed on one bounded `neutral_transit_v1` run only.
- Late-side behavior was frozen at the already active A1-only state.
- Early-side E2 regressed formation geometry materially.
- The net result remains below the current human-visible threshold.
- This turn should not be read as neutral-transit closure.

## 1. Validation Scope

Validation used:

- one bounded `neutral_transit_v1` run
- harness-side readout only
- existing fixture telemetry

Validation did not use:

- new settings surfaces
- new replay protocol fields
- viewer-owned proof

## 2. Comparison Anchor

Comparison anchor for this note is the already accepted first bounded correction state (`A1 + B1`):

- `objective_reached_tick = 425`
- `distance_final = 0.271`
- `distance_min = 0.248`
- `formation_rms_radius_ratio_peak = 1.0209`
- `front_extent_ratio_peak = 1.9109`
- `front_extent_ratio_final = 1.9109`

## 3. Second-Turn Readout

With `A1 + B1 + E2` active, and late-side behavior frozen at A1:

- `objective_reached_tick = 647`
- `distance_final = 0.066`
- `distance_min = 0.048`
- `formation_rms_radius_ratio_peak = 1.0525`
- `front_extent_ratio_peak = 4.7762`
- `front_extent_ratio_final = 4.1007`

Near-target readout:

- `(647, 1.809, +1.0)`
- `(648, 1.317, +1.0)`
- `(649, 0.758, +1.0)`
- `(650, 0.126, +1.0)`
- `(651, 0.069, +1.0)`
- `(652, 0.061, +1.0)`
- `(653, 0.048, +1.0)`
- `(654, 0.050, -1.0)`
- `(655, 0.058, -1.0)`
- `(656, 0.063, -1.0)`
- `(657, 0.066, -1.0)`

## 4. Late-Side Reading

Late-side behavior was not extended in this revised turn.

Any calmer near-target read therefore must be read only as a byproduct of the changed early-side transit behavior, not as a new late-side mechanism result.

## 5. Early-Side Reading

Early-side behavior regresses materially:

- `objective_reached_tick` becomes much later
- `formation_rms_radius_ratio_peak` rises noticeably
- `front_extent_ratio_peak` and `front_extent_ratio_final` both rise sharply

So the slot-error-aware attenuation, as currently written, appears too strong on the bounded carrier.

## 6. Human Read

Current honest read:

- still below human-visible threshold

More specifically:

- the broader transit/formation read is not visibly better overall
- early / mid-phase geometry now looks worse rather than better
- the much later arrival timing would itself be obvious to a human observer

## 7. Bottom Line

This turn is still valid as an authorized bounded mechanism probe because:

- it stayed inside the approved touchpoints
- it added no new parameter surface
- it clearly separated late-family and early-family effects

But the net result should be reported as:

- late side frozen at A1
- early-side regression
- no human-visible success
