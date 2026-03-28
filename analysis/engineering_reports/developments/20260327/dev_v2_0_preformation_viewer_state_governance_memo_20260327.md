## dev_v2.0 Pre-Formation Viewer State Governance Memo

Date: 2026-03-27
Scope: `viz3d_panda/` viewer-local only
Status: stage governance memo

### Accepted Status

Governance accepts the current state as an:

- accepted pre-Formation viewer-only surface
- viewer-local only
- consumer-only
- readability / stability refinement only

It must not be read as:

- formation semantics activation
- runtime authority
- replay protocol authority
- movement / combat semantic work

### Accepted Active Visual State

Governance accepts the following active viewer-local state:

1. Unit geometry origin is corrected at the rendering source.
   - Rendered unit origin and rendered geometry center now align in `x / y / z`.
   - No separate visual-center helper is accepted.

2. Inner cluster now uses fixed-size cuboids with HP-driven count reduction.
   - Outer wedge bucket scaling may remain.
   - Inner cluster size does not read by shrink.
   - Inner scale now reads by visible count.

3. Fire-link surface is reduced to `enabled` / `disabled` only.
   - The active family is a lightweight pulse-train multi-beam read.
   - It remains viewer-local only.

4. Low-speed playback uses transform-only smoothing.
   - Motion-facing presentation surfaces may smooth.
   - Semantic state should remain exact where possible.

5. Small gear-aware stabilizers are accepted for motion-facing viewer surfaces.
   - This includes tracked camera motion.
   - This includes fleet avatar motion.
   - This does not widen the viewer into a generalized motion framework.

6. The current viewer state is read together with subtraction-first cleanup after local exploration.
   - Heavier earlier variants were tried, narrowed, and reduced.
   - The accepted state is not the most elaborate state; it is the lighter accepted one.

### Retired / Rejected / Not to Be Misread

The following lines are explicitly not current doctrine:

1. The old whole-frame smoothing path is retired.
   - It is not the accepted low-speed playback direction.

2. The old `minimal / full` straight-beam fire-link family is retired.
   - It is not the accepted fire-link surface.

3. "Solve eye-load by richer FX" is not accepted as the preferred direction.
   - Heavier stylization is not the current governance preference.
   - Density reduction and bounded readability controls are preferred.

4. Viewer-local work must not be misread as movement / combat / formation semantic work.
   - The accepted visual state remains observer-side only.
   - No pre-Formation viewer result should be reinterpreted as upstream semantic authority.

### Methodological Absorption

Governance absorbs the following lessons from this stage:

1. Fix source alignment first.
   - Correct geometry origin at the source is preferable to downstream helper correction.

2. Reduce density before adding stylization.
   - Lower simultaneous visual burden is preferable to richer visual effect families.

3. Smooth transforms; keep semantic state exact where possible.
   - Motion-facing presentation may smooth.
   - Semantic state should remain exact unless a stronger reason exists.

4. Use subtraction-first cleanup after local exploration.
   - Exploration may temporarily widen.
   - The accepted maintained state should then be narrowed and simplified.

5. This pattern is likely reusable once Formation visibility becomes the next mainline topic.
   - The present memo does not authorize Formation work.
   - It records a method that may be reused when that later turn opens deliberately.

### Boundary Reminder

This memo is:

- a stage governance memo
- a dev_v2.0 local-state record
- a pre-Formation viewer-only conclusion

It is not:

- a generalized governance framework
- a canonical architecture rule
- a movement / combat / formation semantics authority
