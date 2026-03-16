# Continuous FR Authority Shaping Note

Date: 2026-03-12
Status: Test-only implementation note
Thread: `analysis/engineering_reports/developments/20260311/phase_fr_authority_audit`

Engine Version: current local test harness over frozen runtime baseline
Modified Layer: `test_run` harness only
Affected Parameters: `FR`, `PD`, `MB`
New Variables Introduced: continuous shaping coefficients on the locked `v3a` centroid-restoration path
Mapping Impact: none
Governance Impact: none in this note; this remains experimental candidate work only
Backward Compatible: yes

Summary

1. Continuous correction preparation now moves off the retired discrete `if` probes and onto a test-only continuous shaping path.
2. The implementation target remains the already locked suspect path: active `v3a` centroid-restoration authority.
3. The harness implementation uses a proxy-first method in `test_run/test_run_v1_0.py`, not a frozen movement-block copy.
4. The first-round DOE is scoped to `42` continuous candidates across the established `22`-cell validation window.
5. Ranking remains advisory only; no automatic finalist selection is introduced.
6. The round-1 run table now doubles as a minimal checkpoint file so interrupted overnight batches can resume.

## 1. Scope and Boundary

This note records the first continuous correction-preparation step after discrete diagnostic probes were retired.

The goal is:

```text
keep the same suspect path,
but express release through continuous influence instead of discrete gating
```

This work does not:

- modify `runtime/engine_skeleton.py`
- rewrite canonical semantics
- open baseline replacement

This remains test-only experimental candidate work.

Governance workflow reference:

- `docs/governance/Baseline_Replacement_Protocol_v1.0.md`

## 2. Implementation Shape

The approved implementation path is:

```text
proxy-first, no frozen copy
```

Concretely:

1. `test_run/test_run_v1_0.py` computes a per-fleet continuous
   `kappa_eff = f(kappa, pd_norm, engaged_fraction, MB_raw)`
2. that adjusted value is injected only through a temporary fleet-parameter proxy
3. the proxy changes only the first `formation_rigidity` read inside `integrate_movement()`
4. the proxy is used only when routing through `exp_precontact_centroid_probe`
5. fleet parameters are restored immediately after movement integration

Why this matters:

- centroid-restoration path is targeted directly
- the later `FSR` use of `formation_rigidity` is not rebound
- no frozen movement block is duplicated in the harness

## 3. Continuous Candidate Families

Candidate A:

```text
kappa_eff = kappa * [1 - a * G_FR(kappa) * pd_norm^p * (1 - engaged_fraction)^q]
G_FR(kappa) = exp(-((kappa - 0.5)^2) / (2 * sigma^2))
```

Candidate B:

```text
kappa_eff = kappa * [1 - a * G_FR(kappa) * pd_norm^p * (1 - engaged_fraction)^q * S_MB(MB)]
S_MB(MB) = 1 / (1 + exp(beta * (MB_raw - 5)))
```

Candidate C:

```text
kappa_eff = kappa * [1 - a * G_FR(kappa) * S_PD(pd_norm) * (1 - engaged_fraction)^q * S_MB(MB)]
S_PD(pd_norm) = 1 / (1 + exp(-gamma * (pd_norm - 0.5)))
```

Candidate C implementation assumption:

- `beta` is held fixed at `1.5`

Reason:

- preserves the approved `42`-candidate round-1 grid
- keeps the MB taper on the smoother side
- does not re-open the candidate count or add an unapproved axis

## 4. Round-1 DOE Design

Validation window:

- `18` `FR5` cells:
  - `MB = {2,5,8}`
  - `PD = {2,5,8}`
  - `ODW = {2,8}`
- `4` controls:
  - `FR2_MB2_PD8_ODW8`
  - `FR2_MB8_PD8_ODW8`
  - `FR8_MB2_PD2_ODW8`
  - `FR8_MB5_PD8_ODW2`

Seeds:

- `SP01`
- `SP09`
- `SP18`

Candidate grid:

- A: `18`
- B: `12`
- C: `12`

Total candidate runs:

```text
22 cells x 3 seeds x 42 candidates = 2772 runs
```

Ranking discipline:

1. preserve all controls
2. improve `FR5/PD8` sentinels
3. avoid harming `FR5_MB8_PD2_ODW8`
4. improve `ODW` readability
5. improve `PD/MB` separability
6. break ties toward smoother and less invasive candidates

No automatic `top 4` decision is encoded.

## 5. Baseline Anchor

To avoid silently expanding round-1 execution budget with a new baseline batch, the first-round scoring script uses the existing historical anchor:

- `analysis/engineering_reports/developments/20260311/phase_fr_authority_audit/fr_authority_doe_run_table.csv`

Anchor use:

- filter to the same `22` cells
- filter to `SP01`, `SP09`, `SP18`
- compare continuous candidates against that fixed anchor

Current implementation assumption:

- round-1 candidate runs stay aligned to the same probe route:
  - `exp_precontact_centroid_probe`
  - `centroid_probe_scale = 0.5`

This keeps first-round candidate scoring comparable to the established local evidence anchor without adding an extra unapproved baseline block.

## 6. Round-1 Outputs

Script:

- `analysis/engineering_reports/developments/20260311/phase_fr_authority_audit/run_continuous_fr_authority_round1_doe.py`

Planned outputs:

- `continuous_fr_authority_round1_run_table.csv`
- `continuous_fr_authority_round1_candidate_summary.csv`
- `continuous_fr_authority_round1_ranked_candidates.csv`
- `continuous_fr_authority_round1_hard_constraints.csv`
- `continuous_fr_authority_round1_summary.md`

Checkpoint / resume behavior:

- `continuous_fr_authority_round1_run_table.csv` also serves as the checkpoint file
- rerunning the same script resumes from existing `run_id` rows
- ranking outputs remain advisory-only and are regenerated from the accumulated run table

## 7. Current Status

Implemented in this step:

- continuous proxy injection path in `test_run/test_run_v1_0.py`
- first-round DOE script scaffold and artifact writers
- this note

Not executed in this note:

- full `2772`-run round-1 batch
- finalist selection
- second-round validation
