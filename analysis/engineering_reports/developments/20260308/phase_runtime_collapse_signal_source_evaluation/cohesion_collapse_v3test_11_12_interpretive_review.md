# v3_test 1.1 / 1.2 Interpretive Review

## Scope

- Source under review: `v3_test`
- Frozen movement baseline: `v3a`
- Frozen semantics outside this review:
  - `v3_r_ref_radius_multiplier = 1.0`
  - physical spacing / separation / projection unchanged
- Evidence source:
  - `cohesion_collapse_semantics_microbatch_run_table.csv`
  - `cohesion_collapse_semantics_microbatch_cell_summary.csv`

## Comparison Focus

This review compares:

- `v3_test @ 1.0` (current semantics baseline inside the review)
- `v3_test @ 1.1`
- `v3_test @ 1.2`

The objective is not baseline replacement.
The objective is to determine whether `1.1` or `1.2` is the better next-stage semantics candidate.

## Key Runtime Path Findings

### 1.0

- `first_deep_pursuit_tick_A mean = 1.0`
- `%ticks_deep_pursuit_A mean = 74.13`
- `mean_enemy_collapse_signal_A = 0.6837`
- `A_v3_mean = 0.2394`
- `A_c_conn_mean = 0.2394`

Interpretation:

- Runtime collapse pressure is heavily saturated from the start.
- This is the defective reference condition.

### 1.1

- `first_deep_pursuit_tick_A mean = 260.44`
- `%ticks_deep_pursuit_A mean = 8.78`
- `mean_enemy_collapse_signal_A = 0.2766`
- `A_v3_mean = 0.8745`
- `A_c_conn_mean = 0.8745`
- `event_order_anomaly_count = 0`
- `never_deep_pursuit_count = 0`

Interpretation:

- `1.1` clearly breaks the `t=1` saturation.
- Runtime collapse pressure is still present, but no longer dominates the entire fight.
- All nine cells still enter deep pursuit eventually, which makes the behavior easier to interpret as a delayed mode rather than a disabled mode.

### 1.2

- `first_deep_pursuit_tick_A mean = 393.13` over finite cases
- `%ticks_deep_pursuit_A mean = 2.38`
- `mean_enemy_collapse_signal_A = 0.1497`
- `A_v3_mean = 0.9747`
- `A_c_conn_mean = 0.9747`
- `event_order_anomaly_count = 0`
- `never_deep_pursuit_count = 1`

Interpretation:

- `1.2` also breaks the `t=1` saturation.
- However, it pushes the runtime path much closer to "deep pursuit almost never matters".
- One of nine cells already loses deep pursuit entirely.

## Event Timing Read

Mean event timings:

- `1.0`
  - `first_contact = 109.0`
  - `cut = 136.11`
  - `pocket = 144.44`

- `1.1`
  - `first_contact = 107.78`
  - `cut = 126.78`
  - `pocket = 155.44`

- `1.2`
  - `first_contact = 107.78`
  - `cut = 126.78`
  - `pocket = 161.44`

Interpretation:

- Both `1.1` and `1.2` pull `First Contact` and `Cut` slightly earlier.
- Both also push `Pocket` later.
- `1.2` increases the pocket delay more strongly than `1.1`.

Important cell-level note:

- The strongest timing distortion is not broad-based contact drift.
- It is selective late-pocket behavior in a subset of cells.
- Therefore the main caution signal is not "events disappear".
- The main caution signal is "encirclement / late-phase tactical structure is being re-timed".

## Human-Sanity Read

From an interpretability perspective:

- `1.1` is the more plausible candidate.
- It preserves a meaningful runtime collapse pathway while removing immediate saturation.
- `1.2` is still coherent, but it already starts to look like over-correction because the mode becomes sparse enough to disappear in some cells.

In short:

- `1.1` looks like a delayed, still-active collapse interpretation.
- `1.2` looks like a delayed, partly suppressed collapse interpretation.

## Multiplier Meaning

For `v3_test`, the active knob in this review is:

`v3_connect_radius_multiplier`

Its mathematical meaning is narrow:

- it rescales the graph radius used by `c_conn`
- it does **not** rescale `rho`
- it does **not** rescale `c_scale`
- it does **not** affect physical spacing or separation behavior

Therefore:

- `1.1` means "slightly more permissive semantic connectivity"
- `1.2` means "more aggressively more permissive semantic connectivity"

Because `c_conn` is the dominant term in this phase, this knob has a disproportionately strong runtime effect.

## Should `v3_r_ref_radius_multiplier` Enter Stage 2?

Current answer: **not yet**

Reason:

- In the micro-batch, `A_c_scale_mean = 1.0` throughout the reviewed band.
- The main movement in the signal comes from `c_conn`, not from `rho / c_scale`.
- Introducing `v3_r_ref_radius_multiplier` now would add a second degree of freedom before the first one is properly bounded.

So the cleaner next step is:

1. keep `v3_r_ref_radius_multiplier = 1.0`
2. treat `v3_connect_radius_multiplier` as the only active knob
3. if needed, later introduce `v3_r_ref_radius_multiplier` as a true second-stage variable

## Recommendation

For the next bounded follow-up:

- prefer `v3_test @ 1.1` as the primary candidate
- keep `v3_test @ 1.2` as the upper-bound comparison
- do not introduce `v3_r_ref_radius_multiplier` yet

Engineering judgment:

- `1.1` is currently the best balance between desaturating the collapse path and preserving a still-active runtime mode.
- `1.2` is useful as a cautionary upper bound, not as the leading candidate.
