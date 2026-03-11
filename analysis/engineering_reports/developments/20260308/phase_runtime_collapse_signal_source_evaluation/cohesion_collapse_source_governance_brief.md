# Governance Brief - Cohesion Collapse Source Evaluation

## Decision Posture

Recommended governance posture:

`HOLD replacement`

This brief integrates:

- the 648-run source DOE
- the 66-run component diagnostic DOE
- human animation observations

## Why HOLD

### 1. `v3_test` is behaviorally meaningful

It is not a null branch.

Compared with `v2`, it materially reduced:

- `mean_enemy_collapse_signal`
- `mean_pursuit_intensity`

and reduced event-order anomalies:

- `50 -> 28`

### 2. Event integrity is still preserved

Both sources kept:

- `cut_exists_rate = 1.0`
- `pocket_exists_rate = 1.0`
- `missing_cut = 0`
- `pocket_without_cut = 0`

### 3. But the replacement gate is still contaminated

The 648-run DOE showed:

- `first_deep_pursuit_tick = 1.0` under both sources

So the runtime gate is already effectively saturated at the very start.

### 4. The 66-run diagnostic explains why

It disproved both prior working guesses:

- `v2` low values are not mainly caused by `elongation`
- `v3_test` low values are not mainly caused by `rho / c_scale`

Instead:

- `v2` is dominated by `fragmentation`
- `v3_test` is dominated by `c_conn`
- in practice these are the same connectivity issue

The shared defect is:

`largest-component connectivity semantics are too harsh in early fleet geometry`

## Human Observation Alignment

Human supervised animation observations match the DOE evidence:

- `v2` appears extremely low during `t=1..100`
- `v3_test` starts higher, then still drops strongly in the same phase

This is consistent with a shared low-connectivity interpretation, not a purely source-specific plot artifact.

## Governance-Relevant Conclusion

The next step should not be a source replacement decision.

The next step should be:

`cohesion-collapse semantics review`

Specifically:

- what should count as meaningful fragmentation in pre-contact fleet geometry
- whether current LCC adjacency semantics are too strict
- whether runtime collapse signal should be more conservative than observer geometry stress

## Bottom Line

`v3_test` remains a credible candidate

but:

`the current evidence does not justify baseline replacement yet`

because the deeper problem is shared connectivity semantics, not simply `v2` vs `v3_test`.
