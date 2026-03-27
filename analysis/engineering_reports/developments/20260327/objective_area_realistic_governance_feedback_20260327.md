# Objective-Area realistic Governance Feedback (2026-03-27)

Status: debug-only feedback
Carrier: `neutral_transit_v1`

## Direct answers

1. Effective does flip in the `objective_reached_tick +/- 5` window: yes.
2. Realistic flips more often than effective in the same window: no; it flips much less often in this window.
3. The realistic window is still mainly being driven by these candidate sources near arrival:
- `prev_next`: 1
- `prev_window_next_window`: 1099
4. `REALISTIC_WINDOW_RADIUS = 3` does not show clear evidence of being too short in this exact window, because the widest centered candidate already dominates almost every choice.
5. `smooth=on` is not the root source of the residual; in this window it neither adds large midpoint flips nor triggers interpolation hard-switches.
6. Current best attribution: **the remaining disorder in this objective window is driven more by the underlying arrival/path residual than by app interpolation, and the current realistic estimator is only a secondary contributor.**

## Governance read

- This turn supports continuing to treat the objective-area residual as a viewer-local issue first.
- It does **not** support claiming that smoothing alone is the cause.
- It also does **not** support claiming that the current realistic estimator is the main amplifier inside this exact `t* +/- 5` window.
- It does support separating the problem into: strong raw arrival/path residual, plus a smaller remaining realistic readout residual.
- The separate HP-driven inner-cluster-count query should remain deferred during this investigation line.
