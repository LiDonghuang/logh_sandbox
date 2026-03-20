# A5 Iteration 0 Baseline Anchor (2026-03-18)

- Purpose: lock pre-refactor baseline for A5 comparisons.
- Determinism policy for this anchor: non-`yang` only (`lobos` vs `lobos`), no seed sweep.
- Tick horizon: 240
- Runtime mode: movement=v3a, cohesion_source=v3_test, boundary_enabled=False, pre_tl=nearest5_centroid

## Anchor Matrix

| fixture | mode | tick_end | alive(A/B) | winner | first_contact | IntermixCoverage t21-120 | IntermixSeverity t21-120 | DeepRatio t21-120 | FrontCurvDiff t21-50 | C_W_PShareDiff t1-20 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| neutral_close_100v100 | off | 240 | 14/16 | undecided | 20 | 0.6888 | 0.0681 | 0.0518 | 0.2949 | 0.0031 |
| neutral_close_100v100 | hybrid_v2 | 240 | 18/12 | undecided | 20 | 0.7030 | 0.0342 | 0.0132 | 0.2800 | 0.0031 |
| neutral_close_100v100 | intent_unified_spacing_v1 | 240 | 16/15 | undecided | 20 | 0.6368 | 0.0674 | 0.0555 | 0.2717 | 0.0031 |
| neutral_long_100v100 | off | 240 | 26/30 | undecided | 61 | 0.2711 | 0.0144 | 0.0060 | 0.1259 | 0.0069 |
| neutral_long_100v100 | hybrid_v2 | 240 | 22/25 | undecided | 61 | 0.2722 | 0.0125 | 0.0027 | 0.1259 | 0.0069 |
| neutral_long_100v100 | intent_unified_spacing_v1 | 240 | 21/27 | undecided | 61 | 0.2717 | 0.0217 | 0.0103 | 0.1259 | 0.0069 |
| exception_2to1_close_200v100 | off | 184 | 147/0 | A | 18 | 0.6563 | 0.0785 | 0.0696 | 0.3923 | 0.0065 |
| exception_2to1_close_200v100 | hybrid_v2 | 197 | 146/0 | A | 18 | 0.5955 | 0.0414 | 0.0170 | 0.5069 | 0.0065 |
| exception_2to1_close_200v100 | intent_unified_spacing_v1 | 195 | 148/0 | A | 18 | 0.5866 | 0.0689 | 0.0569 | 0.5546 | 0.0064 |

## Reuse Rule for A5

- Every structural refactor iteration must rerun this exact matrix and compare against the JSON anchor.
- If deviations appear, classify as expected wiring change vs unintended semantic drift before continuing.
