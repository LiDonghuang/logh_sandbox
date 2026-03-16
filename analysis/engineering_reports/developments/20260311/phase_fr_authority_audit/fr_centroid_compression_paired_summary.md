# FR Centroid Decouple Paired Confirmation

## Scope
- Variant A: current baseline `exp_precontact_centroid_probe`
- Variant B: test-only `exp_precontact_plus_fr_centroid_decouple_probe` in `test_run` harness
- Candidate change scope: movement-only FR decouple probe; no runtime baseline edit

## Batch
- Cells: `6`
- Variants: `2`
- Seed profiles: `3`
- Total runs: `36`

## High-Level Readout
- Cells with reduced A-side wedge gate: `0/6`
- FR2 guardrails still wedge-free: `0/2`
- FR8 support cells still fully wedge-capable: `2/2`

## Cell Summary
| Cell | Base Win% | Cand Win% | Base Wedge% | Cand Wedge% | Base Frag% | Cand Frag% | Base c_conn | Cand c_conn | Base Collapse | Cand Collapse | Base Div T | Cand Div T | Base Profile | Cand Profile |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| FR2_MB2_PD8_ODW8 | 100.0 | 0.0 | 0.0 | 100.0 | 0.0 | 0.0 | 0.9646 | 0.9883 | 0.0354 | 0.0117 | 536.0 | 298.0 | mixed_front | unstable_penetration_wedge |
| FR2_MB8_PD8_ODW8 | 0.0 | 0.0 | 0.0 | 100.0 | 100.0 | 0.0 | 0.7169 | 0.9385 | 0.2831 | 0.0615 | 155.0 | 288.0 | mixed_front | unstable_penetration_wedge |
| FR5_MB2_PD8_ODW8 | 0.0 | 0.0 | 100.0 | 100.0 | 0.0 | 0.0 | 0.9179 | 0.9785 | 0.0821 | 0.0215 | 131.0 | 328.0 | unstable_penetration_wedge | unstable_penetration_wedge |
| FR5_MB8_PD2_ODW8 | 100.0 | 0.0 | 100.0 | 100.0 | 100.0 | 0.0 | 0.8828 | 0.9327 | 0.1172 | 0.0673 | 187.0 | 190.0 | unstable_penetration_wedge | unstable_penetration_wedge |
| FR8_MB5_PD8_ODW2 | 0.0 | 0.0 | 100.0 | 100.0 | 100.0 | 100.0 | 0.8356 | 0.8419 | 0.1644 | 0.1581 | 135.0 | 123.0 | unstable_penetration_wedge | unstable_penetration_wedge |
| FR8_MB2_PD2_ODW8 | 100.0 | 0.0 | 100.0 | 100.0 | 0.0 | 0.0 | 0.9625 | 0.9668 | 0.0375 | 0.0332 | 277.0 | 164.0 | unstable_penetration_wedge | unstable_penetration_wedge |

