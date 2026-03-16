# FR Authority Governance Request

Date: 2026-03-11
Status: Request for Governance Direction
Thread: `analysis/engineering_reports/developments/20260311/phase_fr_authority_audit`

Engine Version: current local test harness over frozen runtime baseline
Modified Layer: `test_run` harness only
Affected Parameters: `FR` suspect centroid-restoration path in active `v3a`
New Variables Introduced: test-only experiment labels only; no new runtime baseline variables
Cross-Dimension Coupling: none beyond existing `FR` coupling under audit
Mapping Impact: none
Governance Impact: request bounded next-step direction for FR authority correction preparation
Backward Compatible: yes; frozen runtime baseline unchanged

Summary

1. Current evidence still supports: `FR` is carrying excess wedge-emergence authority on the active `v3a` centroid-restoration path.
2. Full decouple probe was too aggressive: it immediately broke both `FR2` guardrails.
3. Earlier piecewise compression probe preserved `FR2`, but harmed at least one healthy `FR8` support case.
4. New subtractive probes were tested to avoid raw remapping and stay closer to "subtract excess authority".
5. Best-performing family so far is a low-contact centroid cap using only existing thresholds: `kappa_eff = min(kappa, 0.5)` when engaged fraction is below `0.25`.
6. That family preserves both `FR2` guardrails and suppresses unhealthy high-`FR` wedge emergence.
7. However, on the current targeted `FR=5` threshold batch it has zero effect, because `FR5` already maps to `kappa = 0.5`, exactly at the cap.
8. Therefore the current best subtractive family is a high-`FR` authority cap, not yet a true `FR5` threshold correction.
9. Engineering is now at a bounded decision point: keep probing toward the `FR5` threshold, or stop this line and reinterpret the authority diagnosis.

## Scope of This Round

- No frozen-layer modification
- No runtime baseline replacement
- No parameter semantic rewrite
- No new large DOE
- All work stayed inside:
  - `test_run/test_run_v1_0.py`
  - `test_run/test_run_v1_0.settings.json`
  - `analysis/engineering_reports/developments/20260311/phase_fr_authority_audit`

## Prior Probe Status

### 1. Piecewise Compression Probe

Artifact status:
- Prior paired result recorded during this engineering thread
- Not preserved under a unique standalone artifact filename

Clean paired readout:
- `Cells with reduced A-side wedge gate: 1/6`
- `FR2 guardrails still wedge-free: 2/2`
- `FR8 support cells still fully wedge-capable: 1/2`

Engineering reading:
- Better than full decouple
- Still too blunt
- Damages at least one healthy high-`FR` support case

### 2. Full Decouple Probe

Reference:
- `analysis/engineering_reports/developments/20260311/phase_fr_authority_audit/fr_centroid_compression_paired_summary.md`

Clean paired readout after decouple run:
- `Cells with reduced A-side wedge gate: 0/6`
- `FR2 guardrails still wedge-free: 0/2`
- `FR8 support cells still fully wedge-capable: 2/2`

Engineering reading:
- Confirms the suspect path has real authority
- But direct removal of `FR` from the centroid term is too aggressive
- Not suitable as a minimal correction candidate

## New Subtractive Probe Family

This round tested three test-only subtractive probes using existing runtime landmarks only:

1. `exp_precontact_plus_fr_centroid_cap5_probe`
2. `exp_precontact_plus_fr_centroid_cap5_lowcontact_probe`
3. `exp_precontact_plus_fr_centroid_cap5_highfr_lowcontact_probe`

Shared idea:
- Do not remap all `FR`
- Do not fully decouple `FR`
- Only cap the suspect centroid-term `kappa` at the canonical midpoint (`0.5`, i.e. `FR=5`)

Probe definitions:

### A. `cap5_all`

Rule:
- `kappa_eff = min(kappa, 0.5)` on every tick

Observed behavior:
- Preserves both `FR2` guardrails
- Suppresses both tested `FR8` wedge cases
- Also suppresses at least one healthy `FR8` support case too strongly

Engineering reading:
- Too strong for minimal correction

### B. `cap5_lowcontact`

Rule:
- `kappa_eff = min(kappa, 0.5)` only when engaged fraction `< 0.25`

Observed behavior on prior 6-cell paired set:
- Preserves `FR2` guardrails: `2/2`
- Reduces wedge gate on `FR8_MB5_PD8_ODW2`: `100% -> 0%`
- Also removes wedge from healthy `FR8_MB2_PD2_ODW8` while that case still wins

Engineering reading:
- Best current subtractive family
- More phase-appropriate than `cap5_all`
- Still not clearly acceptable as a correction candidate

### C. `cap5_highfr_lowcontact`

Rule:
- Same as `cap5_lowcontact`, but only when `kappa > 0.5`

Observed behavior:
- On the tested `FR={2,5,8}` cell set, behavior is identical to `cap5_lowcontact`

Engineering reading:
- Currently redundant with `cap5_lowcontact`
- Not independently informative on the tested set

## New Targeted FR5 Threshold Evidence

To test whether the best current family actually corrects the `FR=5` threshold band, Engineering ran a targeted paired batch on these six cells:

- `FR5_MB2_PD8_ODW2`
- `FR5_MB2_PD8_ODW8`
- `FR5_MB5_PD8_ODW2`
- `FR5_MB5_PD8_ODW8`
- `FR5_MB8_PD2_ODW2`
- `FR5_MB8_PD2_ODW8`

Variants:
- baseline = `exp_precontact_centroid_probe`
- candidate = `exp_precontact_plus_fr_centroid_cap5_lowcontact_probe`

Seed profiles:
- `SP01`
- `SP09`
- `SP18`

Key result:
- The candidate produced **no change** on all six `FR5` cells

Representative readout:

| Cell | Base Wedge% | Cand Wedge% | Base Win% | Cand Win% | Base c_conn | Cand c_conn | Base Collapse | Cand Collapse |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `FR5_MB2_PD8_ODW2` | 0 | 0 | 0 | 0 | 0.8263 | 0.8263 | 0.1737 | 0.1737 |
| `FR5_MB2_PD8_ODW8` | 100 | 100 | 0 | 0 | 0.9179 | 0.9179 | 0.0821 | 0.0821 |
| `FR5_MB5_PD8_ODW2` | 0 | 0 | 0 | 0 | 0.8065 | 0.8065 | 0.1935 | 0.1935 |
| `FR5_MB5_PD8_ODW8` | 100 | 100 | 0 | 0 | 0.8989 | 0.8989 | 0.1011 | 0.1011 |
| `FR5_MB8_PD2_ODW2` | 0 | 0 | 0 | 0 | 0.7932 | 0.7932 | 0.2068 | 0.2068 |
| `FR5_MB8_PD2_ODW8` | 100 | 100 | 100 | 100 | 0.8828 | 0.8828 | 0.1172 | 0.1172 |

Engineering reading:
- This is not a runtime no-op bug
- It is a design consequence
- `FR5` already maps to `kappa = 0.5`
- Therefore a `cap5` family cannot move the `FR=5` threshold band by construction

## Current Engineering Interpretation

1. The suspect centroid-restoration path remains the right authority target.
2. Full decouple is disproven as a minimal candidate.
3. Piecewise compression is interpretable as a probe, but too blunt as a correction candidate.
4. The best subtractive family so far is `low-contact cap5`, but it only constrains `FR > 5`.
5. Therefore current evidence is sufficient to say:

```text
We now have a plausible high-FR authority cap,
but we do not yet have a validated FR5-threshold correction.
```

## Governance Request

Engineering requests governance direction on the next bounded move.

### Requested Decision

Please indicate which path should be preferred:

1. Authorize one more bounded probe aimed below the `FR5` midpoint
Reason:
- Needed if governance wants engineering to directly challenge the `FR5` emergence threshold
- This would require a new test-only cutoff below `kappa = 0.5`

2. Authorize a phase-window probe instead of a lower `FR` cap
Reason:
- Keeps the correction focused on emergence timing rather than `FR` magnitude remapping
- Example target: only early emergence window / pre-contact carry-through window

3. Stop further probe design and treat current evidence as sufficient for governance-level interpretation
Reason:
- Current evidence already establishes:
  - suspect path identified
  - full decouple rejected
  - high-`FR` cap family characterized
  - `FR5` threshold still unresolved

### Engineering Recommendation

Engineering recommends option `2` if governance wants one more bounded exploration step.

Reason:
- It stays closer to "remove excess emergence authority" than to "remap FR by another cutoff"
- It avoids immediately introducing a new lower-`FR` cap constant
- It is structurally easier to justify as authority-shaping rather than parameter reinterpretation

## Reproducibility Notes

Persisted references:
- `analysis/engineering_reports/developments/20260311/phase_fr_authority_audit/fr_authority_audit_note.md`
- `analysis/engineering_reports/developments/20260311/phase_fr_authority_audit/fr_authority_doe_summary.md`
- `analysis/engineering_reports/developments/20260311/phase_fr_authority_audit/fr_runtime_authority_decomposition_note_20260311.md`
- `analysis/engineering_reports/developments/20260311/phase_fr_authority_audit/fr_centroid_compression_paired_summary.md`
  - current contents = latest decouple paired run under a legacy filename

This round's targeted `FR5` threshold batch was executed by reusing:
- `analysis/engineering_reports/developments/20260311/phase_fr_authority_audit/run_fr_authority_doe.py`
  - `build_run_settings()`
  - `run_single_case()`

No frozen runtime files were modified.
No baseline replacement was attempted.
