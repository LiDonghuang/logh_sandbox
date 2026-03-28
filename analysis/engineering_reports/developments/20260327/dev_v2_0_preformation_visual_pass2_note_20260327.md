## dev_v2.0 Pre-Formation Visual Pass 2

Date: 2026-03-27  
Scope: `viz3d_panda/` viewer-local only  
Status: active local viewer state recorded

### Summary

This note records the current accepted viewer-local visual state after the bounded pre-Formation visual pass and follow-up cleanup/lean round.

No runtime, replay schema, movement semantics, combat semantics, or formation ownership are changed here.

### Active Viewer-Local State

1. Unit geometry origin is corrected at the geometry source.
   - The unit root origin now matches the rendered geometry center in `x / y / z`.
   - Fire-link anchors use this corrected geometry center directly, then apply only the bounded `+/- 0.5` firing-axis safety offset.
   - No secondary "visual center" helper mechanism is active.

2. Inner cluster now reads fleet scale by visible count, not by shrinking cuboids.
   - Outer wedge token still uses HP bucket scaling.
   - Inner cuboid size stays fixed.
   - Visible cuboid count now follows:
     - bucket 5 -> 10
     - bucket 4 -> 8
     - bucket 3 -> 6
     - bucket 2 -> 4
     - bucket 1 -> 2

3. Fire links are reduced to two viewer-local modes only.
   - `enabled`
   - `disabled`
   - The earlier `minimal / full` family is no longer active.

4. Fire links now use a lightweight pulse-train multi-beam style.
   - Base pulse shape remains `0.75` segment and `0.25` gap.
   - Endpoints are corrected-geometry-center based.
   - Multi-beam layouts use center/corner-style offsets with `z` staggering.

5. Low-speed playback now uses transform-only smoothing.
   - Smoothing no longer builds a synthetic whole-frame `ViewerFrame`.
   - Active smoothing covers displayed unit transforms, tracked camera focus, halo anchor motion, avatar anchor motion, and fire-link endpoint positions.
   - HP bucket, visible inner-cluster count, HUD text, and fire-link target semantics remain exact-frame.

6. Fire-link eye-load has been reduced without widening the mechanism.
   - Fire-link alpha is lowered.
   - Outer beams now alternate deterministically instead of remaining all-on at once.
   - Fire-link visual speed now follows viewer time, not direct tick-driven linear speed.
   - Current speed scaling is `sqrt(gear)`, so Gear 5 vs Gear 1 is approximately `2.236x`.
   - Beam alternation now follows an independent slow real-time clock rather than per-tick flipping.

7. Fleet halo has been reduced to a lighter read.
   - Halo now uses two rings instead of three.
   - Halo pulse uses a slow independent clock.
   - Ring separation is now a small fixed offset rather than a percentage fan-out that grows near-camera.
   - Halo hides when the camera is close to level with the `XY` plane.

### Cleanup / Lean Outcome

This round also records visible subtraction-first cleanup:

- removed the inactive whole-frame smoothing build path from `viz3d_panda/app.py`
- removed stale default `fire_link_mode=\"minimal\"` from `viz3d_panda/unit_renderer.py`
- removed the old high-speed static fire-link special branch; current fire-link behavior is one unified pulse-train family across gears
- updated repo high-level reading to stop describing fire links as `minimal / full` straight beams

### Current Read

The current viewer state is materially lighter and more coherent than the earlier straight-beam / whole-frame smoothing stage, but close-range battle eye-load is not claimed as fully solved.

The remaining discomfort still appears strongly related to dense inherited 2D-style close combat geometry, not just to one isolated viewer-local effect.
