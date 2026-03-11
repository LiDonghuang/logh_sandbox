# Movement Micro-Iteration Watch Report (v3b7)
Engine Version: v5.0-alpha5  
Date: 2026-03-06  
Scope: movement experimental branch only (`v3b5/v3b6/v3b7`)  
Policy: single-rule, auditable, no cross-layer coupling

## 1. Guardrail Compliance
1. No FR/MB semantic changes.
2. No targeting/combat/PD/cohesion/collapse edits.
3. Changes restricted to movement branch behavior selection and one localized correction rule.
4. BRF/Event schema untouched.

## 2. Micro-Iteration Target
Primary objective:
1. Reduce pre-contact persistent outliers (window tick 80-100), including persistence severity.

Secondary constraint:
1. Monitor split side-effects.

Required watch metrics included:
1. Symptom metrics.
2. Split side-effect metrics.
3. Contact timing changes.
4. Mirror/jitter watch metrics.

## 3. Comparison (Current Test Settings)
Scenario source:
1. `analysis/test_run_v1_0.settings.json` (current local test profile)
2. `A=grillparzer`, `B=knappstein`, `test_mode=2`, runtime decision source `v3_test`

Window:
1. pre-contact watch window fixed at tick `80..100`

### 3.1 Metrics Table
| Model | persist_mean_80_100 | persist_max_80_100 | max_persist_mean_80_100 | split_mean_A_80_100 | split_mean_B_80_100 | split_hi_A_80_100 | split_hi_B_80_100 | first_contact_tick | first_kill_tick | mirror_gap_outlier_mean_80_100 | mirror_gap_split_mean_80_100 | jitter_persist_total_80_100 | jitter_split_A_80_100 | jitter_split_B_80_100 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| v3b5 | 6.4286 | 7 | 61.0000 | 1.6539 | 1.7348 | 1 | 13 | 106 | 106 | 0.9524 | 0.2082 | 0.0500 | 0.1724 | 0.0093 |
| v3b6 | 4.1429 | 7 | 49.8571 | 1.7337 | 1.7317 | 13 | 21 | 109 | 109 | 1.5238 | 0.0289 | 0.2500 | 0.0114 | 0.0083 |
| v3b7 | 5.0476 | 6 | 61.0000 | 1.6612 | 1.7355 | 0 | 21 | 112 | 112 | 0.9048 | 0.0743 | 0.1000 | 0.0123 | 0.0036 |

### 3.2 Delta vs v3b5
`v3b6 - v3b5`:
1. Symptom improvement stronger (`persist_mean` down by 2.2857; `max_persist_mean` down by 11.1429).
2. Split side-effect increased (`split_hi_A: +12`, `split_hi_B: +8`).
3. Contact timing delayed (+3 ticks).
4. Mirror/jitter watch less stable on outlier/jitter dimensions.

`v3b7 - v3b5`:
1. Symptom improved moderately (`persist_mean` down by 1.3810, `persist_max` down by 1).
2. A-side split constraint improved (`split_hi_A: -1`), B-side worsened (`split_hi_B: +8`).
3. Contact timing delayed more (+6 ticks).
4. Mirror/jitter watch mostly improved or neutral except contact delay.

## 4. Determinism Spot-Check (v3b7)
Two-run digest check (same inputs):
1. rep1: `c6d9c2b74a9127a4b4db633b93336f015b302f010da9dc45e162af2f97bf13ed`
2. rep2: `c6d9c2b74a9127a4b4db633b93336f015b302f010da9dc45e162af2f97bf13ed`
3. result: `PASS`

## 5. Interim Engineering Read
1. `v3b6` is symptom-first but produces larger split side-effects.
2. `v3b7` is a compromise: symptom still better than `v3b5`, A-side split controlled, but contact timing shifts later.
3. Metrics are not yet jointly stable across all watch dimensions.

## 6. Recommendation Before Any Baseline Gate
1. Continue at most one additional micro-iteration in movement experimental branch.
2. Keep the same watch dashboard (symptom/split/contact/mirror-jitter) and require non-regression envelope before escalation.
3. Do not enter baseline decision gate until contact timing shift and B-side split side-effect are jointly constrained.
