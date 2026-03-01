# Governance Submission - Phase V.2 MB-DIAG0

Engine Version: v5.0-alpha3
Modified Layer: Movement composition (`integrate_movement`, pre-normalization, non-cohesion maneuver only)
Affected Parameters: MB
New Variables: none
Cross-Dimension Coupling: none (combat/target/contact unchanged)
Mapping Impact: none
Governance Impact: none
Backward Compatible: yes (MB=0 exact legacy path)

Validation Summary:
1. Determinism (MB=0/0.1/0.2): True
2. MB=0 bitwise regression vs pre-change engine: True
3. Mirror gate (<= +15% baseline): True
4. Jitter gate (<= +50% baseline): False
5. Attractor proxy gate: True
6. Runtime overhead <= +10%: True (3.65%)

MB Level Comparison (Reference Scenario Alpha):
- MB=0.0: tangential=0.2048, parallel=0.9472, mirror=0.000000, jitter=2604, survivors A/B=0/27, first_contact=99, orbit_proxy(mean_closure)=0.686846
- MB=0.1: tangential=0.2288, parallel=0.9316, mirror=0.000000, jitter=3820, survivors A/B=0/33, first_contact=99, orbit_proxy(mean_closure)=0.740174
- MB=0.2: tangential=0.2621, parallel=0.9083, mirror=0.000000, jitter=4973, survivors A/B=0/29, first_contact=100, orbit_proxy(mean_closure)=0.703234

Artifacts:
- mb_diag0_summary_v5_0_alpha3.json
- mb_diag0_metrics_v5_0_alpha3.csv

Notes:
- Mirror gate in DIAG0 uses Reference Alpha anti-symmetry pair (A/B FR swap) as minimal macro check.
- Full FR 11x11 mirror sweep deferred unless Governance requests MB-DIAG0b expansion.
