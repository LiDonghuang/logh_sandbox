# ODW Runtime Mapping Governance Report

Status: engineering review update  
Scope: ODW prototype mathematics and bounded DOE interpretation

## 1. Executive Reading

Current ODW prototype is active, but its total effect is weak and not cleanly monotonic at fleet-level aggregate readouts.

This is explainable from the current mathematics.

Primary recommendation:

- keep the prototype bounded and exploratory
- freeze `odw_posture_bias_clip_delta = 0.4`
- do not expand to larger DOE yet
- treat current observer readouts as engineering diagnostics, not long-term governance indicators

## 2. Current Runtime Formula

Insertion point:

```text
movement v3a
-> target-axis decomposition
-> per-unit recomposition of m_parallel / m_tangent
```

Current active ODW terms:

```text
odw_centered = clip((ODW - 5) / 4, -1, 1)

lateral_norm = clip(abs(lateral_offset) / lateral_span_ref, 0, 1)
width_profile = 1 - 2 * lateral_norm

odw_parallel_scale_raw =
    1 + k_odw * odw_centered * width_profile

odw_parallel_scale =
    clip(odw_parallel_scale_raw, 1 - clip_delta_odw, 1 + clip_delta_odw)

maneuver =
    ((1 - mb) * odw_parallel_scale * m_parallel)
  + (tangent_scale * m_tangent)
```

Interpretation:

- center units: `width_profile > 0`
- wing units: `width_profile < 0`
- high offensive ODW increases center forward pressure and reduces wing forward pressure
- low offensive / more defensive ODW does the inverse

This remains:

```text
ODW
-> pressure redistribution bias
-> geometry tendency through emergence
```

It is not direct shape selection.

## 3. Why The Effect Is Weak

The weak total effect is structural, not surprising.

### A. ODW acts on only one subcomponent

ODW only scales `m_parallel`.

It does not directly modify:

- `m_tangent`
- centroid restoration
- enemy attraction
- separation
- boundary
- pursuit threshold
- retreat threshold
- combat
- targeting

So the prototype acts late and locally inside a much larger movement sum.

### B. The redistribution is antisymmetric across fleet width

`width_profile` is positive at the center and negative at the wings.

That means ODW mostly performs an internal width-wise redistribution:

- center gets a little more forward pressure
- wings get a little less

At whole-fleet aggregate level, those changes partially cancel.

This is the main reason why:

- `AR_forward`
- `WedgeRatio`
- `SplitSeparation`

move only slightly even when the prototype is active.

### C. Fleet-level observer metrics compress the signal

The prototype changes a width-wise distribution.

But most current readouts are fleet-level aggregates.

That mismatch suppresses visible signal.

In other words:

```text
local redistribution
-> global aggregate readout
```

is a lossy measurement path.

## 4. 90-Run DOE Reading

Batch:

- `ODW = {2, 5, 8}`
- `k = {0, 0.25, 0.5, 0.75, 1.0}`
- 6 canonical opponents
- one deterministic seed
- total `90` runs

Main findings:

1. `k = 0` shows exact invariance across ODW levels.
   This confirms the baseline path is not silently consuming ODW when the prototype is off.

2. Once `k > 0`, the prototype is clearly active.
   Geometry and runtime-path metrics do move.

3. However the response across `k` is weak and non-monotonic.
   This is consistent with the mathematics above:
   redistribution is real, but partially cancels in aggregate.

4. Event integrity remains mostly stable.
   Only one anomaly appeared in the large batch:

```text
ODW8_K1p0_muller -> pocket_before_cut
```

So the current prototype is not broadly destabilizing the event layer.

## 5. Clip-Delta Micro DOE Reading

Micro batch:

- controlled neutral Side B
- Side A varies only `ODW = {2, 8}`
- fixed `k = 0.5`
- `clip_delta = {0.2, 0.4, 0.6, 0.8, 1.0}`
- total `10` runs

Finding:

- `clip_delta = 0.2` still constrains the prototype
- `clip_delta >= 0.4` produces identical results

This is mathematically expected.

With current bounded terms:

```text
|odw_centered| <= 0.75   for ODW = 2 or 8
|width_profile| <= 1
k = 0.5
```

Maximum raw shift is:

```text
0.5 * 0.75 * 1 = 0.375
```

Therefore once:

```text
clip_delta >= 0.375
```

the clip no longer binds.

Engineering conclusion:

- `clip_delta = 0.4` is sufficient
- larger values add no current information

## 6. Observer Readout Note

`CenterWingAdvanceGap` was introduced because the previous `NetAxisPush` metric was measuring the wrong layer.

Current `CenterWingAdvanceGap` is more faithful to the runtime formula because it asks:

```text
are center-band units advancing more than wing-band units?
```

However, the current normalized values are small (often within roughly `+-0.05`).

This does not imply the metric is wrong.

It means:

- the measured quantity is a second-order differential
- taken over a short `10`-tick interval
- then normalized by `max_unit_speed * interval`

So it should be read as a subtle distribution-bias indicator, not a large tactical-state meter.

Current recommendation:

- keep `CenterWingAdvanceGap` as an engineering observer readout
- do not yet promote it into a long-term governance indicator

## 7. Recommendation

Current engineering recommendation is:

1. freeze the active clip setting at:

```text
odw_posture_bias_clip_delta = 0.4
```

2. stop expanding DOE size for this prototype for now

3. keep the prototype in bounded exploratory status

4. if work continues, prioritize:

```text
better posture-specific readout
before larger parameter sweeps
```

The present result is not “ODW failed”.

The more precise conclusion is:

```text
ODW prototype has signal,
but current insertion strength and observer aggregation
do not yet produce a clean fleet-level posture signature.
```
