# Engineering Report v1.0 - Phase V.2 FRxMB Extreme Stress Validation
Engine Version: v5.0-alpha4
Modified Layer: None (Diagnostic only)
New Variables Introduced: None
Cross-Dimension Coupling: No
Mapping Impact: None
Governance Impact: None
Backward Compatible: Yes

## Validation Scope
- Grid: FR in {2,5,8,10}, MB in {2,5,8,10} (Fleet A variant, Fleet B neutral FR=5 MB=5).
- Fixed settings: attack_range=5, FSR=0.1 on, CH on, boundary off, max_time_steps=300.
- Determinism: dual-run digest check on all 16 primary cases.
- Mirror: mirrored companion run for each case, metric |M_ab + M_ba|.

## Gate Snapshot
- Determinism: PASS
- MB=5 dual-run bitwise (intra-run): PASS
- MB=5 behavioral regression vs 20260301 (FR2/5/8 survivors): PASS
- No new attractor proxy: PASS

### Macro vs Current 3x3 (same formula)
- Mirror degradation: -29.0783%
- Jitter degradation: 4.8144%
- Runtime overhead: 1.8780%
- Mirror <= +5%: PASS
- Jitter <= +10%: PASS
- Overhead <= +10%: PASS

### Macro vs Historical 20260301 Baseline
- Mirror degradation: -29.0783%
- Jitter degradation: 0.7263%
- Runtime overhead: 36.1400%
- Mirror <= +5%: PASS
- Jitter <= +10%: PASS
- Overhead <= +10%: FAIL

## FR=10 Pocket Lifetime Distribution (Combined)
- FR10_MB10: count=38, mean=29.79, p50=4.0, p90=101.3, max=295, persistent>=20=8
- FR10_MB2: count=26, mean=66.42, p50=30.5, p90=163.0, max=281, persistent>=20=16
- FR10_MB5: count=69, mean=23.90, p50=2.0, p90=91.6, max=296, persistent>=20=17
- FR10_MB8: count=61, mean=19.93, p50=1.0, p90=91.0, max=296, persistent>=20=10

## Metric Note
- Jitter formula is explicitly declared in JSON summary (`jitter_metric_definition`) to avoid hidden ownership drift.
- Historical cross-report digest equality cannot be guaranteed without the original serializer implementation; dual-run bitwise determinism is preserved in this run.

Artifacts:
- mb_v2_1_stress_metrics_v5_0_alpha4.csv
- mb_v2_1_stress_summary_v5_0_alpha4.json
- mb_v2_1_stress_fr10_pocket_lifetime.csv
