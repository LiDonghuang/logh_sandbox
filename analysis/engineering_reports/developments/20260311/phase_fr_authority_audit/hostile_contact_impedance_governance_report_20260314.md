# Hostile Contact Impedance Governance Report

Date: 2026-03-14  
Status: Engineering report  
Scope: Phase 1 hostile contact impedance work summary and current judgment

## 1. Scope Completed

This report covers the bounded Phase 1 hostile contact impedance work completed so far inside `test_run`.

Included:

- `repulsion_v1` prototype
- `damping_v2` prototype
- `hybrid_v2` family
- Phase 1 contact-impedance DOE
- intermix diagnostic introduction
- attempted `support_weighted_v3` follow-up family

Not included:

- firing geometry modernization
- turning delay / heading-rate limit
- TL semantics
- personality mechanism expansion

## 2. Main Findings

### 2.1 Problem definition remains valid

The original diagnosis still stands:

```text
the current system lacks a sufficiently convincing hostile contact-impedance layer
```

Human close-contact review remains consistent with this diagnosis.

### 2.2 `repulsion_v1` is not enough

Pure local hostile repulsion does not produce an acceptable result.

Observed pattern:

- can reduce some deep penetration
- tends to worsen contact geometry / observer safety
- does not become a credible Phase 1 prototype

Judgment:

- keep only as a reference family
- do not treat as a leading candidate

### 2.3 `damping_v2` is safe but insufficient

Pure forward damping behaves better on neutral safety, but does not suppress the exception fixture strongly enough.

Observed pattern:

- safety usually acceptable
- penetration suppression too weak in the `2:1` close-contact exception

Judgment:

- useful as ablation/reference
- not sufficient as a standalone answer

### 2.4 `hybrid_v2` is the only family that passed the current gate

The Phase 1 DOE found a single globally acceptable prototype:

```text
hybrid_v2_r125_d035_p020
```

That is:

- `radius_multiplier = 1.25`
- `forward_damping_strength = 0.35`
- `repulsion_max_disp_ratio = 0.20`

Judgment:

- this remains the current leading Phase 1 prototype
- it is the best candidate found so far under the existing gate structure

### 2.5 But `hybrid_v2` has not passed human visual acceptance cleanly

This is a critical distinction.

Engineering judgment now is:

- `hybrid_v2` passes the current quantitative screen
- it does **not** yet convincingly solve the animation-level impression of "units still weaving / penetrating too freely"

Therefore:

- `leading prototype` does **not** mean `problem solved`

### 2.6 `support_weighted_v3` has now been retired

The support-weighted / front-support-aware attempt was a valid next hypothesis.

However:

- it required an extra parameter
- it did not produce a stable improvement over `hybrid_v2`
- once safety was recovered, penetration suppression advantage largely disappeared

Judgment:

- `support_weighted_v3` is now formally stopped
- it has been removed from active `test_run` code and settings
- no further parameter accretion is recommended on that family

## 3. Intermix Diagnostic Judgment

`IntermixSeverity` remains worth keeping as a diagnostic direction.

But current judgment is:

- useful
- not yet sufficient as a full human-acceptance proxy

Why:

- it measures average penetration severity over overlapping hostile pairs
- it can understate runs with widespread but not extremely deep intermixing

Interpretation:

- low `IntermixSeverity` does **not** guarantee that human observers will feel the geometry is clean

Therefore:

- keep it as a substrate diagnostic
- do not overinterpret it as a full acceptance metric

## 4. Structural Cleanup Completed

As part of this line, two cleanup decisions have now been applied:

1. `support_weighted_v3` removed from active code/settings
2. `repulsion_v1.enabled` removed from the `test_run` settings interface

Current hostile impedance structure is now cleaner:

- `active_mode`
- `repulsion_v1.{strength, radius_multiplier}`
- `damping_v2.{radius_multiplier, forward_damping_strength}`
- `hybrid_v2.{radius_multiplier, repulsion_max_disp_ratio, forward_damping_strength}`

This is a better representation than the previous mixed mode-plus-enabled pattern.

## 5. Current Engineering Judgment

Current best interpretation is:

1. Phase 1 diagnosis is still correct
2. `hybrid_v2` remains the only acceptable working prototype so far
3. `hybrid_v2` is still not visually convincing enough
4. parameter growth alone is no longer a good next move
5. the next viable advance, if any, must come from a genuinely different mechanism hypothesis

## 6. Recommendation for Next Step

Engineering does **not** recommend:

- further parameter growth on the current `support-weighted` line
- reopening large DOE immediately
- treating `hybrid_v2` as a settled baseline replacement

Engineering **does** recommend:

1. keep `hybrid_v2_r125_d035_p020` as the working Phase 1 reference
2. stop the `support_weighted_v3` family
3. maintain intermix diagnostics, but continue treating them as diagnostic rather than decisive
4. if Phase 1 continues, require a new mechanism hypothesis before more DOE

That next hypothesis should be:

- qualitatively different from `support_weighted_v3`
- still continuous-cost based
- still non-doctrinal
- still test-only

Possible future direction, only after review:

- a more explicit contact-entry non-penetration bias
- or another front-presence mechanism that does not simply add more parameters to `hybrid_v2`

## 7. Bottom Line

The hostile contact impedance line produced one real result:

```text
hybrid_v2 is currently the best available Phase 1 working prototype
```

But it also produced an equally important negative result:

```text
support_weighted_v3 did not justify further continuation
```

So the correct current stance is:

- keep `hybrid_v2` as working reference
- stop the failed support-weighted branch
- do not continue parameter accretion
- only proceed further if a genuinely new mechanism idea is approved
