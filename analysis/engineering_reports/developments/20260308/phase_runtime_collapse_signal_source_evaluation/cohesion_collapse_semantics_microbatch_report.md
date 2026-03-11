# Cohesion-Collapse Semantics Review Micro-Batch

## Scope

- Prototype type: semantics-only connectivity-radius decoupling
- Movement baseline frozen: `v3a`
- Opponent: `reinhard`
- Seed profile: `SP01`
- Runs: `99`

## Design

- Cells: `FR x MB = 3 x 3`, `PD = 5`
- Sources: `v2`, `v3_test`
- Multiplier levels:
  - `v2`: `1.0`, `1.5`, `2.0`, `2.5`, `3.0`
  - `v3_test`: `1.0`, `1.1`, `1.2`, `1.3`, `1.4`, `1.5`
- Isolation rule:
  - when source=`v2`, only `v2_connect_radius_multiplier` varies
  - when source=`v3_test`, only `v3_connect_radius_multiplier` varies

## v2

- `first_contact_tick` mean: `109.4889`
- `first_deep_pursuit_tick_A` mean: `1.0000`
- `%ticks_deep_pursuit_A` mean: `74.5025`
- `mean_enemy_collapse_signal_A` mean: `0.6865`
- `A_v2_mean` mean: `0.2084`
- `A_fragmentation_mean` mean: `0.1574`
- `A_v3_mean` mean: `0.2852`
- `A_c_conn_mean` mean: `0.2852`
- `event_order_anomaly` count: `3`

## v3_test

- `first_contact_tick` mean: `107.9815`
- `first_deep_pursuit_tick_A` mean: `287.6923`
- `%ticks_deep_pursuit_A` mean: `14.7171`
- `mean_enemy_collapse_signal_A` mean: `0.2172`
- `A_v2_mean` mean: `0.0835`
- `A_fragmentation_mean` mean: `0.6762`
- `A_v3_mean` mean: `0.8427`
- `A_c_conn_mean` mean: `0.8472`
- `event_order_anomaly` count: `1`

## Multiplier Semantics

- `v2_connect_radius_multiplier` rescales only the LCC/fragmentation graph radius used by `cohesion_v2`.
- It does not modify physical spacing, soft separation force, hard projection, or the other `v2` penalties (`dispersion`, `elongation`, `outlier_mass`).
- Therefore for `v2`, this multiplier is a pure `fragmentation semantics` knob.
- `v3_connect_radius_multiplier` rescales only the connectivity graph radius used by `c_conn` inside `cohesion_v3_shadow`.
- In this batch, `v3_r_ref_radius_multiplier` remains `1.0`, so the `rho / c_scale` scale semantics are intentionally frozen.
- Therefore for `v3_test`, this multiplier is a pure `c_conn semantics` knob rather than a full `v3` rescaling knob.

## Mean Deltas vs Multiplier 1.0

- `v2` mean delta `%ticks_deep_pursuit_A`: `-30.0409`
- `v2` mean delta `mean_enemy_collapse_signal_A`: `-0.2558`
- `v2` mean delta `A_fragmentation_mean`: `-0.7867`
- `v3_test` mean delta `%ticks_deep_pursuit_A`: `-71.2899`
- `v3_test` mean delta `mean_enemy_collapse_signal_A`: `-0.5598`
- `v3_test` mean delta `A_c_conn_mean`: `0.7294`

## Engineering Read

- `v2` confirms the semantics-review hypothesis only partially: widening the graph radius removes `fragmentation`, but it does not move `first_deep_pursuit_tick_A` off `t=1`.
- Therefore `v2_connect_radius_multiplier` behaves like a value-calibration knob, not a robust gate-timing knob, in this domain.
- `v3_test` is much more sensitive: `1.1` already lifts `c_conn`, reduces `%ticks_deep_pursuit_A`, and pushes `first_deep_pursuit_tick_A` far away from `t=1`.
- Therefore `v3_connect_radius_multiplier` is the more promising substrate for continued semantics optimization, but `1.5` is already close to over-correction.
- The likely candidate band for follow-up is `v3_test` around `1.1` to `1.2`, not further fine-tuning of `v2`.
