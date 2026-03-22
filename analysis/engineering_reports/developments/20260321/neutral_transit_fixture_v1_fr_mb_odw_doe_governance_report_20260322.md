# Neutral Transit Fixture v1 FR x MB x ODW DOE Governance Report (2026-03-22)

Status: engineering evidence update  
Scope: bounded long-diagonal neutral-transit DOE on the existing shared movement path

Engine Version:
current local maintained `test_run` path over shared frozen runtime `v3a`

Modified Layer:
none in this postprocess/report turn; completed DOE interpretation only

Affected Parameters:
`formation_rigidity (FR)` in `[1,3,5,7,9]`  
`mobility_bias (MB)` in `[1,3,5,7,9]`  
`offense_defense_weight (ODW)` in `[1,3,5,7,9]`  
geometry frozen to `[50,50] -> [150,150]`

New Variables Introduced:
none in this turn

Cross-Dimension Coupling:
evidence suggests:
- FR couples most strongly to projection pair burden and final compaction
- MB couples most strongly to delay and correction intensity
- low ODW is the clearest adverse lever for both delay and projection burden

Mapping Impact:
none yet; this report does not request a mapping change

Governance Impact:
supports continued use of the long-diagonal neutral-transit fixture as a bounded diagnostic surface; does not support baseline replacement

Backward Compatible:
yes; no mechanism code changed in this DOE/report round

## Summary

1. All `125` runs reached the objective.
2. No cap censoring was observed.
3. The long diagonal remains a good default observation window for this fixture.
4. FR is not the strongest speed lever here.
5. FR is the strongest projection-pair / compaction lever here.
6. MB increases delay and correction intensity more than it changes pair count.
7. Low ODW is the clearest adverse lever for transit burden in this grid.
8. The worst corner is `FR=9, MB=9, ODW=1`.
9. That corner is simultaneously the slowest, the most projection-heavy, and the most compacted.
10. The fixture therefore continues to expose shared-path burden cleanly without invoking battle semantics.
11. This remains evidence for bounded diagnosis, not evidence for baseline replacement.

## 1. DOE Envelope

- Long-diagonal geometry fixed:
  `origin=[50,50]`, `objective=[150,150]`, `facing=45 deg`
- Archetype anchor:
  `lobos`
- Non-DOE personality dimensions fixed at `5`
- Seeds fixed:
  `20260321 / 20260322 / 20260323`
- Boundary disabled
- Shared `integrate_movement` reused unchanged

Merged run table:
[neutral_transit_fixture_v1_fr_mb_odw_doe_run_table_20260322.csv](e:/logh_sandbox/analysis/engineering_reports/developments/20260321/neutral_transit_fixture_v1_fr_mb_odw_doe_run_table_20260322.csv)

Detailed analysis:
[neutral_transit_fixture_v1_fr_mb_odw_doe_analysis_20260322.md](e:/logh_sandbox/analysis/engineering_reports/developments/20260321/neutral_transit_fixture_v1_fr_mb_odw_doe_analysis_20260322.md)

## 2. Governance-Relevant Findings

### 2.1 FR Reading

- FR monotonically increases arrival time, but only moderately relative to the other axes.
- FR is the dominant driver of projection pair burden.
- FR is also the dominant driver of final geometry compaction.

Governance reading:

FR should currently be interpreted as a geometry/projection-load lever in this fixture more than as a primary transit-speed lever.

### 2.2 MB Reading

- MB monotonically slows arrival.
- MB raises projection displacement intensity.
- MB does not strongly change projection pair count.

Governance reading:

MB is acting more like a movement-intensity / delay lever than a broad contact-pair lever in this fixture.

### 2.3 ODW Reading

- ODW has the strongest monotonic arrival effect in this grid.
- Low ODW is consistently associated with higher projection burden and stronger compaction.
- Higher ODW reduces burden and reaches the objective sooner.

Governance reading:

ODW is currently the clearest adverse/good transit-burden axis among the three when read on this long-diagonal fixture.

## 3. Most Important Adverse Corner

The strongest adverse corner in this DOE is:

`FR=9, MB=9, ODW=1`

That single corner is:

- slowest arrival: `193`
- highest projection pair burden: `317`
- highest peak correction displacement: `2.937`
- strongest compaction: `final_rms_radius_ratio = 0.467`

This is decision-relevant because it gives Governance a very clear “stress corner” for future bounded comparisons.

## 4. Recommended Governance Posture

- Keep the long diagonal as the default frozen distance factor for the next bounded neutral-transit DOE.
- Keep `neutral_transit_v1` in test-only diagnostic status.
- Permit follow-up bounded work that focuses on:
  `FR x MB x ODW` stress corners
  or paired comparisons against alternative shared-path candidates.
- Do not treat this DOE as justification for a movement baseline replacement.
- Do not reopen broad runtime/movement rewrite from this evidence alone.

## 5. Explicit Non-Changes

- battle default path remains unchanged
- fixture settings path remains `fixture.neutral_transit_v1`
- objective injection hook remains bounded to the fixture path
- `integrate_movement` was not changed in this DOE/report turn
- no new runtime selector was introduced
- no new settings layer was introduced

## 6. Current Not-Done Items

- no paired model comparison
- no multi-waypoint transit
- no enemy-present transit DOE
- no baseline-replacement request
- no governance request for broader movement semantics rewrite
