# FR5 Threshold Paired Check

Date: 2026-03-11
Status: Targeted engineering note
Scope: Response to Governance Addendum on `FR=5` threshold priority

## Candidate

Test-only experiment:
- `exp_precontact_plus_fr_centroid_midband_lowcontact_probe`

Rule:
- Only active on the suspect centroid-restoration path inside `test_run` harness
- Only active when engaged fraction `< 0.25`
- Only active for mid-band `FR`: `0.125 < kappa <= 0.5`
- Override rule:

```text
kappa_eff = 0.5 * (kappa + 0.125)
```

Interpretation:
- `FR2` unchanged
- `FR8` unchanged
- `FR5` low-contact centroid authority pulled partway toward the `FR2` anchor

No frozen runtime files were modified.

## Batch

Variants:
- baseline = `exp_precontact_centroid_probe`
- candidate = `exp_precontact_plus_fr_centroid_midband_lowcontact_probe`

Seed profiles:
- `SP01`
- `SP09`
- `SP18`

Cells:
- FR5 threshold cells:
  - `FR5_MB2_PD8_ODW2`
  - `FR5_MB2_PD8_ODW8`
  - `FR5_MB5_PD8_ODW2`
  - `FR5_MB5_PD8_ODW8`
  - `FR5_MB8_PD2_ODW2`
  - `FR5_MB8_PD2_ODW8`
- Controls:
  - `FR2_MB2_PD8_ODW8`
  - `FR2_MB8_PD8_ODW8`
  - `FR8_MB2_PD2_ODW8`

Total runs:
- `9 cells x 2 variants x 3 seed profiles = 54`

## Readout Summary

| Cell | Base Win% | Cand Win% | Base Wedge% | Cand Wedge% | Base c_conn | Cand c_conn | Base Collapse | Cand Collapse | Base FireEff | Cand FireEff | Base Profile | Cand Profile |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| `FR5_MB2_PD8_ODW2` | 0 | 0 | 0 | 0 | 0.8263 | 0.7985 | 0.1737 | 0.2015 | 0.3211 | 0.4177 | flat_holding_front | mixed_front |
| `FR5_MB2_PD8_ODW8` | 0 | 0 | 100 | 0 | 0.9179 | 0.9046 | 0.0821 | 0.0954 | 0.3308 | 0.3709 | unstable_penetration_wedge | mixed_front |
| `FR5_MB5_PD8_ODW2` | 0 | 0 | 0 | 0 | 0.8065 | 0.7833 | 0.1935 | 0.2167 | 0.2916 | 0.3772 | flat_holding_front | flat_holding_front |
| `FR5_MB5_PD8_ODW8` | 0 | 0 | 100 | 100 | 0.8989 | 0.8503 | 0.1011 | 0.1497 | 0.3549 | 0.3565 | unstable_penetration_wedge | unstable_penetration_wedge |
| `FR5_MB8_PD2_ODW2` | 0 | 0 | 0 | 0 | 0.7932 | 0.7112 | 0.2068 | 0.2888 | 0.2585 | 0.3988 | flat_holding_front | flat_holding_front |
| `FR5_MB8_PD2_ODW8` | 100 | 0 | 100 | 100 | 0.8828 | 0.7864 | 0.1172 | 0.2136 | 0.3253 | 0.3799 | unstable_penetration_wedge | unstable_penetration_wedge |
| `FR2_MB2_PD8_ODW8` | 100 | 100 | 0 | 0 | 0.9646 | 0.9646 | 0.0354 | 0.0354 | 0.5497 | 0.5497 | mixed_front | mixed_front |
| `FR2_MB8_PD8_ODW8` | 0 | 0 | 0 | 0 | 0.7169 | 0.7169 | 0.2831 | 0.2831 | 0.4431 | 0.4431 | mixed_front | mixed_front |
| `FR8_MB2_PD2_ODW8` | 100 | 100 | 100 | 100 | 0.9625 | 0.9625 | 0.0375 | 0.0375 | 0.3189 | 0.3189 | unstable_penetration_wedge | unstable_penetration_wedge |

## Findings

### 1. Does it reduce wedge-gate overreach at FR5?

Partially, yes.

Most informative success:
- `FR5_MB2_PD8_ODW8`
  - `Wedge 100% -> 0%`
  - `unstable_penetration_wedge -> mixed_front`
  - `first_major_divergence_tick 131 -> 147`

But the effect is not broad enough:
- `FR5_MB5_PD8_ODW8` remains `Wedge 100%`
- `FR5_MB8_PD2_ODW8` remains `Wedge 100%`

Engineering reading:
- The candidate can move at least one true `FR5` threshold wedge cell back below the gate
- It does not yet generalize across the full `FR5` wedge subset

### 2. Does it preserve legitimate deformation resistance?

Mixed.

Good:
- Both `FR2` controls are exactly preserved
- `FR8` healthy support control is exactly preserved

Bad:
- `FR5_MB8_PD2_ODW8`
  - `A win 100% -> 0%`
  - `c_conn 0.8828 -> 0.7864`
  - `collapse 0.1172 -> 0.2136`

Engineering reading:
- The probe avoids collapsing into `FR2` suppression
- But it can over-penalize some legitimate `FR5` support-capable cases

### 3. Does ODW support readability improve at FR5?

Not cleanly.

Best pair:
- `MB2/PD8`
  - baseline:
    - `ODW2 = no wedge`
    - `ODW8 = wedge`
  - candidate:
    - `ODW2 = no wedge`
    - `ODW8 = no wedge`

This removes one form of apparent FR overreach, but it also collapses the clearest ODW wedge/no-wedge separation.

Other pairs:
- `MB5/PD8`
  - ODW separation remains wedge/no-wedge
- `MB8/PD2`
  - ODW separation remains wedge/no-wedge, but the ODW8 winner is lost

Engineering reading:
- ODW readability is not clearly improved overall
- The candidate shifts some cells away from wedge emergence, but does not yet yield a consistently cleaner posture-support readout

### 4. Does it avoid obvious collapse into FR2-like suppression?

Yes, on the chosen controls.

Evidence:
- `FR2_MB2_PD8_ODW8`: exact match baseline/candidate
- `FR2_MB8_PD8_ODW8`: exact match baseline/candidate
- `FR8_MB2_PD2_ODW8`: exact match baseline/candidate

Engineering reading:
- The probe is genuinely centered on the `FR5` mid-band
- It is not simply a broad suppressor

## Engineering Conclusion

This is the first probe in this thread that is genuinely aligned with the governance addendum:

- It targets `FR5` directly
- It preserves both `FR2` guardrails
- It preserves the healthy `FR8` support control
- It demonstrates that at least part of the `FR5` wedge subset can be pushed back below the emergence gate

However, it is not yet a validated minimal correction candidate.

Reason:
- It succeeds on `FR5_MB2_PD8_ODW8`
- It fails to move two other `FR5` wedge cells
- It breaks at least one legitimate `FR5` winner (`FR5_MB8_PD2_ODW8`)
- ODW readability remains mixed rather than clearly improved

## Current Recommendation

Engineering recommendation:
- keep this candidate family as the new leading `FR5`-centered probe
- do not elevate it to correction candidate yet
- next bounded step should stay inside the `FR5` band and refine phase targeting, not reopen high-`FR` cap work as the primary action

## Follow-up Stronger Variant

Follow-up test-only experiment:
- `exp_precontact_plus_fr_centroid_midband_pdhigh_precontact_strong_probe`

Rule:
- Same phase window and scope as the prior `PD-high precontact` probe
- But instead of a half-step pull, it applies the full `FR2` anchor on the suspect centroid term:

```text
kappa_eff = 0.125
```

Only when:
- `engaged_fraction <= 0.0`
- `0.125 < kappa <= 0.5`
- `PD_norm > 0.5`

### Stronger Variant Readout

| Cell | Base Win% | Strong Win% | Base Wedge% | Strong Wedge% | Base c_conn | Strong c_conn | Base Collapse | Strong Collapse | Base FireEff | Strong FireEff |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `FR5_MB2_PD8_ODW2` | 0 | 100 | 0 | 0 | 0.8263 | 0.8913 | 0.1737 | 0.1087 | 0.3211 | 0.5153 |
| `FR5_MB2_PD8_ODW8` | 0 | 100 | 100 | 0 | 0.9179 | 0.9397 | 0.0821 | 0.0603 | 0.3308 | 0.5288 |
| `FR5_MB5_PD8_ODW2` | 0 | 100 | 0 | 0 | 0.8065 | 0.7510 | 0.1935 | 0.2490 | 0.2916 | 0.4958 |
| `FR5_MB5_PD8_ODW8` | 0 | 100 | 100 | 0 | 0.8989 | 0.8855 | 0.1011 | 0.1145 | 0.3549 | 0.4603 |
| `FR5_MB8_PD2_ODW2` | 0 | 0 | 0 | 0 | 0.7932 | 0.7932 | 0.2068 | 0.2068 | 0.2585 | 0.2585 |
| `FR5_MB8_PD2_ODW8` | 100 | 100 | 100 | 100 | 0.8828 | 0.8828 | 0.1172 | 0.1172 | 0.3253 | 0.3253 |
| `FR2_MB2_PD8_ODW8` | 100 | 100 | 0 | 0 | 0.9646 | 0.9646 | 0.0354 | 0.0354 | 0.5497 | 0.5497 |
| `FR2_MB8_PD8_ODW8` | 0 | 0 | 0 | 0 | 0.7169 | 0.7169 | 0.2831 | 0.2831 | 0.4431 | 0.4431 |
| `FR8_MB2_PD2_ODW8` | 100 | 100 | 100 | 100 | 0.9625 | 0.9625 | 0.0375 | 0.0375 | 0.3189 | 0.3189 |

### Stronger Variant Engineering Reading

- This variant resolves the previously stubborn `FR5_MB5_PD8_ODW8` case:
  - `Wedge 100% -> 0%`
  - `A win 0% -> 100%`
- It also keeps the legitimate `FR5_MB8_PD2_ODW8` winner intact:
  - `A win 100% -> 100%`
  - `Wedge 100% -> 100%`
- `FR2` guardrails remain untouched
- The healthy `FR8` support control remains untouched

Current engineering reading:
- This is now the strongest `FR5`-centered correction candidate tested in this thread
- It is still limited evidence, but it is the first candidate that:
  - suppresses both tested `FR5/PD8/ODW8` wedge cases
  - preserves the tested `FR5/PD2/ODW8` winner
  - preserves `FR2` and `FR8` controls
