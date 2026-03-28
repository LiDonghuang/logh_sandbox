## dev_v2.0 Visual Improvement Reflection

Date: 2026-03-27
Scope: `viz3d_panda/` viewer-local reflection only
Status: engineering reflection / lessons learned

### What Worked

1. Fixing geometry origin at the source was better than layering viewer-side correction helpers.
   - Once unit coordinates and rendered geometry center matched in `x / y / z`, several downstream problems became simpler at the same time:
   - fire-link anchors
   - cluster placement
   - perceived `z` correctness

2. Count reduction worked better than shrink reduction for close-range inner clusters.
   - Shrinking the whole cluster with HP made the read muddy.
   - Keeping per-cuboid size fixed and reducing visible count preserved the "fleet made of ships" read better.

3. Eye-load reduction came more from reducing simultaneous moving brightness than from making each element more elaborate.
   - Lower alpha helped.
   - Slow independent clocks helped.
   - Deterministic beam alternation helped more than adding richer FX would have.
   - This argues for density control before stylization.

4. Transform-only smoothing was the right direction.
   - Smoothing all semantic state by rebuilding synthetic frames was more expensive and not actually necessary.
   - Smoothing only motion-facing presentation surfaces gave most of the visual benefit while preserving exact-frame semantics where they mattered.

5. Camera and avatar stability needed their own treatment.
   - Unit smoothing alone was not enough.
   - Tracked camera focus and screen-space avatar placement each needed their own small stabilizer.
   - Gear-aware deadband / blend / snap profiles were enough; no large viewer framework was needed.

### What Did Not Work

1. Static or all-on beam presentation was visually expensive.
   - Dense close-range combat with many simultaneously visible beams fatigued the eye quickly.

2. Solving eye-load by "more FX" never looked promising.
   - Blur, sparkle, or heavier VFX would likely have increased both reading burden and implementation burden.

3. Whole-frame smoothing was too broad.
   - It made the implementation heavier without a proportional gain in readability.

### Practical Heuristic Going Forward

For viewer-local readability work, the better default question is not:

`How can this effect become richer?`

It is:

`How can simultaneous visual burden be reduced while keeping the semantic read intact?`

That usually points toward:

- fewer concurrently active bright elements
- slower independent presentation clocks
- exact semantics plus smoothed transforms
- source-correct geometry rather than downstream correction helpers

### Relevance Beyond This Turn

This visual round also reinforces a broader engineering habit:

- fix source alignment first
- smooth only the part humans actually perceive as motion
- keep semantic state exact unless there is a strong reason not to
- reduce density before adding sophistication

That pattern is likely reusable in future viewer-local work, especially once 3D formation visibility becomes the next mainline topic.
