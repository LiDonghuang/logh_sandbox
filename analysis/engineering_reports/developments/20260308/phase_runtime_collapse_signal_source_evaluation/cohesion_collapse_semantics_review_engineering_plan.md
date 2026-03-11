# Cohesion-Collapse Semantics Review - Engineering Plan

## Objective

Run a narrow semantics review to test one specific hypothesis:

`semantic connectivity radius should not be automatically identical to physical spacing radius`

This phase is:

- diagnostic
- bounded
- auditable

It is not yet a baseline replacement phase.

## Frozen Boundaries

Do not change:

- movement `v3a` baseline
- archetype semantics
- combat / targeting
- BRF schema
- event bridge semantics

Keep:

- runtime cohesion decision source baseline = `v2`
- `v3_test` as experimental candidate only

## Working Problem Statement

Recent evidence suggests:

1. `v2` low early cohesion is driven mainly by `fragmentation`
2. `v3_test` low early cohesion is driven mainly by `c_conn`
3. both depend on the same `separation_radius`-derived connectivity graph

Therefore the current phase should ask:

`What semantic connectivity radius best represents intact fleet-scale geometry before and around first contact?`

## Minimal Prototype Knobs

The first prototype should introduce only semantic multipliers.

Do not modify physical spacing behavior in round 1.

### Physical Layer (held fixed in round 1)

```text
r_sep_phys = separation_radius
projection_min_spacing = separation_radius
alpha_sep = current baseline
```

### Semantics Layer (new prototype knobs)

```text
v2_connect_radius_multiplier
v3_connect_radius_multiplier
```

Optional second-step knob only if needed:

```text
v3_r_ref_radius_multiplier
```

## Minimal Prototype Formulas

### `v2`

Current:

```text
connect_radius_v2 = r_sep_phys
```

Prototype:

```text
connect_radius_v2 = r_sep_phys * m_v2_conn
```

where:

```text
m_v2_conn = v2_connect_radius_multiplier
```

### `v3_test`

Current:

```text
connect_radius_v3 = r_sep_phys
r_ref_v3 = r_sep_phys * sqrt(n_alive)
```

Prototype step 1:

```text
connect_radius_v3 = r_sep_phys * m_v3_conn
r_ref_v3 = r_sep_phys * sqrt(n_alive)
```

Prototype step 2 only if step 1 is insufficient:

```text
r_ref_v3 = r_sep_phys * m_v3_ref * sqrt(n_alive)
```

## Why This Is The Right Minimal Cut

This is the smallest intervention that directly tests the confirmed semantic issue.

It does **not**:

- retune movement geometry
- change physical collision behavior
- reinterpret archetype parameters

It tests only whether semantic connectivity is currently too strict.

## Parameter Sweep Proposal

Round 1 should remain small.

### Fixed Context

- movement baseline: `v3a`
- `movement_v3a_experiment = exp_precontact_centroid_probe`
- `centroid_probe_scale = 0.5`
- bridge thresholds frozen:
  - `theta_split = 1.7`
  - `theta_env = 0.5`
- boundary disabled for DOE
- paired fixed seeds

### Factors

```text
runtime_decision_source ∈ {v2, v3_test}
m_v2_conn ∈ {1.0, 1.5, 2.0}
m_v3_conn ∈ {1.0, 1.5, 2.0}
```

But to keep scope controlled:

- when source = `v2`, only vary `m_v2_conn`
- when source = `v3_test`, only vary `m_v3_conn`

So the practical levels are:

```text
semantic_connect_multiplier ∈ {1.0, 1.5, 2.0}
```

per source.

### Controlled Scenario Grid

Use a compact grid:

- `FR ∈ {2,5,8}`
- `MB ∈ {2,5,8}`
- `PD = 5`

Opponents:

- first 3 canonical archetypes

Seeds:

- 2 paired seed profiles

### Total Runs

```text
3 FR x 3 MB x 3 opponents x 2 seeds x 2 sources x 3 multiplier levels
= 324 runs
```

This is large enough to be credible but still bounded.

If governance/human wants a smaller pre-prototype first pass, run:

```text
9 cells x 1 opponent x 1 seed x 2 sources x 3 levels = 54 runs
```

## Required Metrics

Primary metrics:

- pre-contact `cohesion_v2` / `cohesion_v3_shadow`
- `first_deep_pursuit_tick`
- `%ticks_deep_pursuit`
- `mean_enemy_collapse_signal`

Constraint metrics:

- `first_contact_tick`
- `cut_tick`
- `pocket_tick`
- `missing_cut`
- `pocket_without_cut`
- `event_order_anomaly`

Secondary geometry metrics:

- `AR_forward`
- `wedge_ratio`
- `split_separation`

Component diagnostics:

- `lcc_ratio` / `fragmentation`
- `c_conn`
- for `v3_test`, `rho` and `c_scale`

## Acceptance / Reject Logic

### Good Signal

If a larger semantic connectivity radius causes:

- higher early cohesion into a plausible range
- `first_deep_pursuit_tick` no longer saturating at `1`
- reduced collapse-signal overactivation
- event integrity preserved

then the semantic decoupling hypothesis is supported.

### Ambiguous Signal

If early cohesion rises, but:

- event order destabilizes
- or contact timing shifts strongly
- or geometry degrades materially

then the multiplier is likely masking a deeper issue.

### Negative Signal

If multipliers do not materially change:

- early cohesion
- pursuit activation timing

then the problem is not mainly the semantic connectivity radius.

## Deliverables

Recommended outputs:

- `cohesion_collapse_semantics_review_run_table.csv`
- `cohesion_collapse_semantics_review_cell_summary.csv`
- `cohesion_collapse_semantics_review_delta_summary.csv`
- `cohesion_collapse_semantics_review_report.md`

The report should answer:

1. Does semantic connectivity decoupling move early cohesion into a more reasonable range?
2. Does it desaturate `deep_pursuit` timing?
3. Does it preserve event integrity?
4. Is the effect similar for `v2` and `v3_test`, or asymmetric?

## Recommended Execution Order

1. Introduce observer-auditable prototype knobs
2. Run a 54-run micro-batch
3. If the signal is real, expand to the 324-run bounded DOE
4. Only then return to governance with a semantics-review synthesis

## Engineering Recommendation

Do not jump directly into a new full cohesion mechanism.

The next clean test is:

`semantic connectivity radius decoupling`

because it directly targets the shared defect identified by the recent DOE evidence.
