# Governance Brief - PR6 Cleanup Rounds (2026-04-05)

## Bottom Line

1. PR `#7` remains the accepted docs / ownership-only cleanup opening, but the real mechanism cleanup now lives on a separate carrier.
2. The current mechanism package contains three real lines: targeting local package disposition, native `v4a.restore_strength` decoupling, and subtraction-first old-family surface retirement.
3. Active-path truth is now: current launcher/settings run `movement=v4a`, `cohesion=v3_test`, and `v4a.restore_strength` is a native `v4a` seam rather than the old `v3_test` centroid-probe bridge.
4. Old-family cleanup is real but partial: stale bridge truth surfaces, `continuous_fr_shaping`, and `pre_tl_target_substrate` have been retired from the current public harness/settings path; full `v3a` retirement has **not** happened yet.
5. Human direction is now explicit that only mechanisms actually used by the current launcher + current layered settings should be kept, that settings/comments must stay synchronized with deletions, that simplicity has priority, and that `test_mode != 2` plus `test_mode` itself should later be retired.

## Governance-Relevant Read

1. This package should be read as a successful ownership/cleanup tightening round, not as a baseline replacement.
2. The next meaningful gate is `test_mode` retirement planning plus broader `v3a` support-path retirement planning.
3. Engineering does **not** recommend immediate whole-`v3a` deletion until that support-path / baseline relationship is handled honestly.

