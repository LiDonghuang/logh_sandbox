# Cohesion Collapse Baseline v1.0

Status: Active  
Scope: Runtime collapse-signal baseline  
Authority Context: Post-replacement stabilization

## Baseline Declaration

The active runtime collapse-signal baseline is:

```text
cohesion_v3 (v3_test)
with connect_radius_multiplier = 1.1
and r_ref_radius_multiplier = 1.0
```

This baseline applies to normal `test_run` execution through:

- `test_run/test_run_v1_0.py`
- `test_run/test_run_v1_0.settings.json`

with:

```text
runtime.selectors.cohesion_decision_source = baseline
baseline -> v3_test
runtime.semantics.collapse_signal.v3_connect_radius_multiplier = 1.1
runtime.semantics.collapse_signal.v3_r_ref_radius_multiplier = 1.0
```

## Mechanism Definition

The baseline replaces only the runtime collapse-signal input source.

It does not redesign the full cohesion layer.

Operationally:

1. `runtime/engine_skeleton.py` still computes canonical `cohesion_v2`.
2. `test_run/test_run_v1_0.py` enables `cohesion_v3_shadow` telemetry.
3. When runtime decision source is `v3_test`, the harness substitutes:

```text
state.last_fleet_cohesion := cohesion_v3_shadow
```

for runtime movement/collapse decisions only.

## Relationship to v2

`v2` remains in the repository as:

- legacy reference mechanism
- comparative baseline for diagnostics
- future hybrid/reference candidate

It is not removed or declared meaningless.

What changed is the preferred runtime interpretation of enemy collapse pressure.

## Reason for Replacement

The confirmed failure mode in the old runtime source was early saturation:

```text
first_deep_pursuit_tick ~= 1
```

under representative controlled runs.

Replacement confirmation showed that `v3_test @ 1.1`:

- avoids the old early-saturation failure
- preserves `First Contact -> Formation Cut -> Pocket Formation`
- removes confirmation-batch event-order anomalies
- preserves determinism in paired checks

The replacement therefore improves collapse-signal timing without introducing a new mechanism family.

## Boundaries

This baseline declaration does not authorize:

- new collapse hysteresis
- connectivity semantics redesign
- new movement mechanisms
- archetype semantic reinterpretation

Those remain future-phase topics.

## Residual Note

Post-normalization signal audit still observed one localized residual event-order outlier family:

```text
FR8_MB5_PD5 vs muller
```

under both paired seeds, where `Pocket Formation` precedes a very late `Formation Cut`.

This residual is treated as a bridge/event-edge case, not as a blocker to the collapse-signal baseline declaration.
