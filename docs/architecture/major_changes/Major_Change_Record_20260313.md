# Major Change Record

Date: 2026-03-13
Status: Active independent record
Purpose: Record major mechanism/interface changes without rewriting historical `analysis`.

## Item 1 - Background celestial generation migrated to a discrete shared orbit-pool

Date: 2026-03-13
Scope: `test_run` harness only / visualization background layer
Status: Implemented

Summary:
- The battlefield background planet/belt generator no longer uses continuous per-object orbit sampling as its primary placement model.
- It now builds a discrete shared orbit pool around the primary star, optionally renders those orbit lines first, and then assigns at most one major object (`planet` or `belt`) to each orbit slot.
- Generation order remains staged as:
  - belt in-canvas minimum
  - planet in-canvas minimum
  - belt fill
  - planet fill

Effect boundary:
- `test_run/test_run_v1_0_viz.py`
- `test_run/test_run_v1_0.viz.settings.json`
- No runtime / canonical / governance / BRF change

Interface effect:
- New visualization setting:
  - `background_orbits.orbit_count_range`
- Existing visualization parameters were retained but their role changed:
  - `background_asteroids.orbit_jitter_range`
    - now shapes discrete orbit-slot spread
    - no longer acts as per-planet radial orbit jitter
  - `background_orbits.planet_orbit_gap_ratio_min`
  - `background_orbits.belt_planet_exclusion_gap_ratio`
  - `background_orbits.belt_belt_exclusion_scale`
    - now act as soft orbit-pool spacing hints rather than hard continuous-sampling exclusion rules

Behavior intent:
- Make the background orbit mechanism legible from the picture itself
- Support direct visual interpretation of the one-orbit-one-object rule
- Preserve minimal visual non-overlap checks so the background does not degenerate into obvious overlap artifacts

## Item 2 - Orbit-line retention and dead setting cleanup

Date: 2026-03-13
Scope: `test_run` harness only / visualization background layer
Status: Implemented

Summary:
- Orbit lines are now retained only for orbit slots actually occupied by a generated `planet` or `belt`.
- Unused orbit slots remain part of the internal allocation pool but are no longer rendered in the final picture.
- The dead visualization setting `background_asteroids.gas_giant_ring.trigger_percentile` was removed because it was no longer read by the renderer.

Effect boundary:
- `test_run/test_run_v1_0_viz.py`
- `test_run/test_run_v1_0.viz.settings.json`
- No runtime / canonical / governance / BRF change
