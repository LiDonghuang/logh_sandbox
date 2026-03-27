# Late Terminal Residual Governance Feedback (2026-03-27)

Status: debug-only feedback
Carrier: `neutral_transit_v1`

## Direct answers

1. In the terminal window, the per-unit residual is **mixed**, not single-source from the first tick.
2. Before the centroid enters stop radius, target pull still dominates completely.
3. Once the fleet is inside the stop-radius window, restore/cohesion rises sharply and then overtakes target.
4. By the last two ticks of the window, separation becomes a major secondary contributor and is dominant on many rows.
5. Projection is not the main pre-projection driver, but it is the exact source of `realized - pre_projection` residual together with the late clamp.
6. Boundary is effectively zero in this carrier/window.

## Strongest current suspicion chain

Current best ordering is:
1. moving expected-position restore
2. separation + post-movement projection reshaping
3. residual target pull
4. late clamp as a smaller correction layer
5. boundary negligible

## Governance read

- The objective-area residual should now be read primarily as a late terminal solver-layer issue, not a viewer issue.
- The evidence does **not** support reopening early-side `E2`.
- The evidence does **not** support treating projection as the sole root; it looks more like a second-layer reshaper acting on motion that restore is still generating.
- If a later mechanism turn is opened, the narrowest first cut should likely examine how fixture expected-position restore behaves once centroid-level arrival has already occurred.
