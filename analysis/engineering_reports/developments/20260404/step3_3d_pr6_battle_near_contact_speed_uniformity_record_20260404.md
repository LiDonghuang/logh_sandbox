Scope: test-only / harness-only

Summary
- Reduced battle near-contact unit-level speed-envelope asymmetry in the active `v4a` line.
- During near-contact / engagement-geometry-active phases, per-unit `turn_speed_scale` is now relaxed toward `1.0`.
- During engagement-geometry-active phases, per-unit `attack_speed_scale` is now relaxed toward a fleet-level contact speed envelope derived from `engaged_speed_scale`.

Why this was recorded
- This is a major item under R-11 because it materially changes active battle motion behavior in the current harness line.
- The intent is subtraction-first: reduce battle-only per-unit speed divergence that was acting as an extra morphology/arc owner during near-contact.

Code touchpoint
- `test_run/test_run_execution.py`

Operational read
- Battle near-contact shape should be less strongly driven by center-vs-wing unit speed divergence from attack-angle and turn-alignment differences.
- No new public parameter surface was added.
