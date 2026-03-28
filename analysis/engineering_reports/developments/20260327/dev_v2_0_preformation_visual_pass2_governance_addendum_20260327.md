## dev_v2.0 Pre-Formation Visual Pass 2 Governance Addendum

Date: 2026-03-27
Scope: `viz3d_panda/` viewer-local only
Status: active local viewer state recorded for Governance reading

### Purpose

This addendum closes the recent viewer-local visual refinement rounds after the accepted late-terminal bounded candidate.

It records the current active visual state, the subtraction-first cleanup that followed, and the remaining boundaries.

No runtime, replay schema, movement semantics, combat semantics, or formation ownership are changed here.

### Current Active Viewer-Local State

1. Low-speed playback uses transform-only smoothing.
   - Display smoothing now applies only to motion-facing presentation surfaces.
   - Exact-frame semantics remain for HP bucket, inner-cluster count, HUD text, and fire-link target semantics.

2. Tracked camera focus now has its own gear-aware anti-jitter profile.
   - The camera uses a bounded deadband / blend / snap profile keyed only by playback gear.
   - This stabilizer is playback-only and camera-only.
   - Pause / step inspection stays exact.

3. Fleet avatars now have a separate gear-aware anti-jitter profile.
   - Avatar screen-space motion uses the same bounded logic family: deadband / blend / snap keyed by gear.
   - Avatar smoothing is independent from unit, halo, and fire-link rendering logic.
   - Pause / step inspection stays exact.

4. Fleet halos are now lighter and slower.
   - Halo radius remains HP-scaled from the first-frame baseline.
   - Halo motion now follows the smoothed fleet positions during playback.
   - The pulse uses a slow independent clock.
   - Halo shape is reduced to two rings.
   - Halo hides when the camera is close to level with the `XY` plane.

5. Inner cluster presentation now reads by fixed-size count reduction.
   - Cuboid size stays fixed.
   - HP bucket changes visible count only.
   - Visible-count reduction now follows an outer-to-inner removal read rather than always leaving the nose pair.
   - Near / mid / far distance logic now reads:
     - near: fully visible
     - mid: progressively transparent
     - far: hidden

6. Fire links now use one lightweight pulse-train family across gears.
   - Surface is reduced to `enabled` / `disabled` only.
   - Pulse shape remains `0.75` line segment with `0.25` gap.
   - Within each tick, pulse advance is bounded and visually stable rather than gear-linearly exploding.
   - Speed now follows viewer time with a `sqrt(gear)` scaling law.
   - Outer beams alternate on an independent slow real-time clock rather than per-tick flashing.
   - Low-speed playback smooths only fire-link endpoint positions, not fire-link target semantics.
   - Fire links render only at near / mid camera ranges; far-range fire links are hidden.

7. Unit origin and fire-link anchors stay geometry-correct.
   - Unit rendered origin matches rendered geometry center in `x / y / z`.
   - Fire-link anchors are computed from corrected geometry center, then apply only the bounded `+/- 0.5` safety offset along the firing axis.
   - No secondary visual-center helper is active.

### Cleanup / Lean Outcome

This final local cleanup pass kept the recent viewer-local additions bounded and subtraction-first:

- removed the old whole-frame smoothed-frame build path and kept transform-only smoothing as the only active low-speed path
- removed the old `minimal / full` fire-link family and kept `enabled / disabled` only
- removed the old high-speed static fire-link branch and kept one unified pulse-train family across gears
- removed one duplicate fleet-summary pass from tracked camera initialization
- kept camera and avatar anti-jitter bounded to small gear-aware deadband / blend / snap profiles rather than widening viewer settings

### Current Read

The current local visual state is acceptable as a pre-Formation viewer-only surface:

- lighter than the earlier straight-beam / whole-frame smoothing stage
- more coherent under low-speed playback
- less eye-straining than the older all-on close-range fire-link presentation

This is still not a claim that close-range battle eye-load is fully solved.

The remaining burden still appears strongly tied to inherited dense 2D-style close combat geometry, which should be expected to ease further once 3D formation and more stable engagement spacing exist upstream.

### Governance Reading Reminder

Read this state as:

- viewer-local only
- consumer-only
- pre-Formation only
- readability / stability refinement only

Do not read it as:

- movement semantics work
- combat semantics work
- replay protocol widening
- formation semantics work
