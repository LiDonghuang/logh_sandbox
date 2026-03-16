# FR5 Threshold Governance Request

Date: 2026-03-11
Status: Request for Governance Direction
Thread: `analysis/engineering_reports/developments/20260311/phase_fr_authority_audit`

Engine Version: current local test harness over frozen runtime baseline
Modified Layer: `test_run` harness only
Affected Parameters: `FR` suspect centroid-restoration path in active `v3a`
New Variables Introduced: test-only experiment labels only; no new runtime baseline variables
Cross-Dimension Coupling: existing `FR x PD x contact-phase window` only
Mapping Impact: none
Governance Impact: request bounded direction on `FR5`-centered correction candidate validation
Backward Compatible: yes; frozen runtime baseline unchanged

Summary

1. Governance priority was shifted to `FR5 threshold correction first`.
2. Engineering tested several `FR5`-centered probes inside the `test_run` harness only.
3. The strongest candidate so far is:
   - `exp_precontact_plus_fr_centroid_midband_pdhigh_precontact_strong_probe`
4. This candidate suppresses both tested `FR5/PD8/ODW8` wedge cases.
5. It preserves the tested legitimate `FR5/PD2/ODW8` winner.
6. It preserves both `FR2` guardrails.
7. It preserves the tested healthy `FR8` support control.
8. Current evidence is still bounded, but it is now stronger than the prior `FR5` probes and more aligned with governance's threshold-first priority.
9. Engineering is not requesting baseline replacement.
10. Engineering is requesting guidance on whether to run one bounded validation wave around this specific candidate.

## Candidate Formula

Definitions:

- raw `FR` in canonical 1..9 scale: `FR_raw`
- raw `PD` in canonical 1..9 scale: `PD_raw`
- normalized `FR`: `kappa = (FR_raw - 1) / 8`
- normalized `PD`: `pd_norm = (PD_raw - 1) / 8`
- engaged fraction from existing runtime signal:

```text
engaged_fraction = engaged_alive_count / alive_count
```

- current precontact centroid probe scale:

```text
s_pc = centroid_probe_scale
```

Baseline active centroid-restoration term in the paired setup:

```text
C_vec = s_pc * kappa * cohesion_gain * cohesion_scale * cohesion_dir
```

Strong `FR5`-centered candidate:

```text
if engaged_fraction <= 0.0
   and 0.125 < kappa <= 0.5
   and pd_norm > 0.5:
       kappa_eff = 0.125
else:
       kappa_eff = kappa
```

Candidate centroid-restoration term:

```text
C'_vec = s_pc * kappa_eff * cohesion_gain * cohesion_scale * cohesion_dir
```

Equivalent subtractive view:

```text
Delta_C_vec = s_pc * (kappa_eff - kappa) * cohesion_gain * cohesion_scale * cohesion_dir
```

Important properties:

- `FR2` is unchanged because `kappa = 0.125`
- `FR8` is unchanged because `kappa > 0.5`
- `PD2` is unchanged because `pd_norm <= 0.5`
- `FR5` with high `PD` is reduced only in strict precontact

For the exact `FR5` case:

```text
kappa = 0.5
kappa_eff = 0.125
centroid-term multiplier ratio = 0.125 / 0.5 = 0.25
```

So inside the affected window, the candidate reduces the centroid-restoration FR factor by 75% for `FR5`.

## Scope of This Round

- No frozen-layer modification
- No runtime baseline replacement
- No parameter semantic rewrite
- No new personality parameter
- All work stayed inside:
  - `test_run/test_run_v1_0.py`
  - `test_run/test_run_v1_0.settings.json`
  - `analysis/engineering_reports/developments/20260311/phase_fr_authority_audit`

## Validation Batch

Variants:
- baseline = `exp_precontact_centroid_probe`
- candidate = `exp_precontact_plus_fr_centroid_midband_pdhigh_precontact_strong_probe`

Seed profiles:
- `SP01`
- `SP09`
- `SP18`

Cells:
- `FR5_MB2_PD8_ODW2`
- `FR5_MB2_PD8_ODW8`
- `FR5_MB5_PD8_ODW2`
- `FR5_MB5_PD8_ODW8`
- `FR5_MB8_PD2_ODW2`
- `FR5_MB8_PD2_ODW8`
- `FR2_MB2_PD8_ODW8`
- `FR2_MB8_PD8_ODW8`
- `FR8_MB2_PD2_ODW8`

Total runs:
- `9 cells x 2 variants x 3 seed profiles = 54`

## Key Readout

| Cell | Base Win% | Cand Win% | Base Wedge% | Cand Wedge% | Base c_conn | Cand c_conn | Base Collapse | Cand Collapse | Base FireEff | Cand FireEff |
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

## Engineering Interpretation

### 1. FR5 Threshold Overreach

This candidate reduces wedge-gate overreach on both tested `FR5/PD8/ODW8` cases:

- `FR5_MB2_PD8_ODW8`
  - `Wedge 100% -> 0%`
  - `Win 0% -> 100%`
- `FR5_MB5_PD8_ODW8`
  - `Wedge 100% -> 0%`
  - `Win 0% -> 100%`

This is the clearest positive result obtained so far on the `FR5` threshold question.

### 2. Preservation of Legitimate Deformation Resistance

The strongest internal check is:

- `FR5_MB8_PD2_ODW8`
  - remains `Win 100%`
  - remains `Wedge 100%`
  - runtime structure metrics remain unchanged

Engineering reading:
- the candidate does not simply suppress all `FR5` wedge cases
- it selectively acts on the high-`PD` subset that currently appears over-coupled

### 3. ODW Readability

For `FR5_MB2_PD8` and `FR5_MB5_PD8`:

- `ODW2` remains non-wedge
- `ODW8` baseline was wedge
- `ODW8` candidate becomes non-wedge

This indicates that in the tested high-`PD` subset, prior `ODW8` wedge emergence was at least partly being carried by excessive FR centroid authority.

Engineering reading:
- ODW support signal is not fully solved
- but this candidate makes the `FR5/PD8` overreach story more readable

### 4. Guardrails

Controls remain unchanged:

- `FR2_MB2_PD8_ODW8`
- `FR2_MB8_PD8_ODW8`
- `FR8_MB2_PD2_ODW8`

Engineering reading:
- the candidate is not acting like a broad suppressor
- it is tightly localized to the intended `FR5` high-`PD` precontact window

## Current Engineering Judgment

This is now the strongest `FR5`-centered correction candidate tested in this thread.

Why:

- It addresses the governance priority directly
- It improves both tested problematic `FR5/PD8/ODW8` wedge cases
- It preserves the tested legitimate `FR5/PD2/ODW8` winner
- It preserves both `FR2` guardrails
- It preserves the tested healthy `FR8` support control

Limit:

- evidence is still bounded to a compact validation set
- this is not yet enough for baseline replacement

## Governance Request

Engineering requests governance direction on one bounded next step:

1. Authorize a compact validation wave centered on this exact candidate
Reason:
- candidate is now specific enough to validate, not just probe
- validation can remain inside `FR5` and nearby controls

2. Request one more refinement before validation
Reason:
- if governance believes the current `PD-high` gate is too specific or semantically risky

3. Stop here and treat this result as sufficient for governance interpretation only
Reason:
- if governance wants no further candidate development in this thread

## Engineering Recommendation

Engineering recommends option `1`.

Recommended validation boundary:
- keep the exact candidate unchanged
- expand only to a compact `FR5`-centered validation batch
- do not reopen high-`FR` cap work as the primary line
- do not move to baseline replacement yet

## Reproducibility Notes

Related files:
- `analysis/engineering_reports/developments/20260311/phase_fr_authority_audit/fr_authority_audit_note.md`
- `analysis/engineering_reports/developments/20260311/phase_fr_authority_audit/fr_runtime_authority_decomposition_note_20260311.md`
- `analysis/engineering_reports/developments/20260311/phase_fr_authority_audit/fr_authority_governance_request_20260311_round2.md`
- `analysis/engineering_reports/developments/20260311/phase_fr_authority_audit/fr5_threshold_paired_check_20260311.md`

Execution support reused:
- `analysis/engineering_reports/developments/20260311/phase_fr_authority_audit/run_fr_authority_doe.py`
  - `build_run_settings()`
  - `run_single_case()`

No frozen runtime files were modified.
No baseline replacement was attempted.
