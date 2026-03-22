# Neutral Transit Exposure Result - Decoupling Decision Record (2026-03-22)

Status: Governance Decision  
Scope: current `neutral_transit_v1` findings, old-factor DOE stopping point, and next-step bounded engineering posture

## 1. Governance Decision

`neutral_transit_v1` has now completed the most important task of this stage:

- it exposes the current shared movement path cleanly under single-fleet / single-objective / no-enemy conditions
- it shows that several legacy movement-path factors are not behaving like clean neutral-baseline controls
- it therefore supports mechanism review more strongly than continued tuning inside the current shared path

Governance decision:

- stop old-factor `FR x MB x ODW` interaction-oriented DOE on the current shared path
- do not keep treating these factors as normal neutral-baseline main effects to be optimized in-place
- switch engineering focus to bounded decoupling review and cut-candidate clarification
- do not treat this decision as authorization for broad runtime rewrite

This file is the repo-side fixed record of that decision.

## 2. Why Old-Factor DOE Should Stop Here

Existing neutral-transit evidence is already sufficient for the higher-priority question.

Evidence base:

- FR-only neutral-transit DOE:
  `analysis/engineering_reports/developments/20260321/neutral_transit_fixture_v1_fr_doe_analysis_20260321.md`
- long-diagonal `FR x MB x ODW` DOE:
  `analysis/engineering_reports/developments/20260321/neutral_transit_fixture_v1_fr_mb_odw_doe_analysis_20260322.md`
- corresponding governance interpretation:
  `analysis/engineering_reports/developments/20260321/neutral_transit_fixture_v1_fr_mb_odw_doe_governance_report_20260322.md`

The key reason to stop is not lack of DOE detail. It is that the current DOE already shows several old factors behaving like burden amplifiers or posture injections, not like clean neutral-baseline knobs.

Current evidence already shows:

- FR acts primarily as a projection-breadth / burden amplifier and a final-compaction amplifier in this fixture, not as a clean transit-speed knob
- MB acts more like a delay / correction-intensity amplifier than a pair-count amplifier
- low ODW is a systematic adverse lever for slower arrival and heavier projection burden
- `mean_corrected_unit_ratio` remains high across the grid, which means projection is a broad intervention surface here rather than a rare legality cleanup layer

The earlier FR-only DOE also showed that longer objective distance mainly stretches duration while leaving the projection-burden pattern broadly intact. That means the fixture is already isolating shared-path movement/projection behavior well enough.

Continuing ANOVA-style or interaction-oriented DOE would implicitly preserve the wrong working assumption:

- that these legacy mechanisms should continue to coexist in the current neutral-baseline path and only need finer tuning

Governance no longer accepts that assumption.

## 3. Why This Is Now a Decoupling Problem, Not a Tuning Problem

The current canonical and doctrine constraints point away from continued in-path tuning.

From `canonical/Engine_v2.0_Skeleton_Canonical.md`:

- movement consumes `CohesionForce`, `TargetVector / TargetForce`, current velocity, and `MobilityBias`
- `MobilityBias` is frozen as a mobility-constraint parameter only
- movement should not reweight upstream force semantics or blend cross-layer meaning back into the substrate

From `docs/architecture/Formation_Geometry_Doctrine_v1.0.md`:

- `FR = resistance to formation deformation`
- formation geometry should emerge from the combined vector field, not from one parameter acting like a direct formation generator
- current stray detection still relies mainly on centroid distance
- future better reading is closer to `distance_from_expected formation surface`, not simple centroid restoration

Within that frame, the neutral-transit result is no longer best read as a request for more tuning. It is a request to review whether several current mechanisms belong in the neutral baseline at all.

The present shared path appears to expose at least these structural issues:

- direct cohesion still behaves mainly like centroid restoration, not expected/reference-formation restoration
- stray-dependent attract can collapse into an extra centripetal mechanism in neutral transit
- MB and ODW still inject low-level vector reshaping more like posture logic than neutral substrate logic
- FSR still reads like an early correction family member rather than an obviously necessary neutral-baseline default

So the next question is not:

- "what is the best interaction mix inside the current path?"

It is:

- "which mechanisms should be cut, migrated upward, or replaced by cleaner upstream semantics?"

## 4. Current Candidate Mechanisms Under Review

### 4.1 Centroid Restoration vs Expected-Position Restoration

Observed issue:

- neutral transit still reads as cohesion toward centroid recovery more than restoration toward an expected/reference formation surface

Why it is under review:

- this makes FR look like an in-path compaction and projection-burden lever
- that reading is not fully aligned with the frozen canonical/doctrine meaning of FR

### 4.2 MB Movement-Layer Injection

Observed issue:

- MB currently behaves in this fixture more like a low-level delay / reshaping lever than a narrow mobility-constraint parameter

Why it is under review:

- canonical movement freeze constrains MB to mobility-scope governance, not broad substrate reshaping

### 4.3 ODW Movement-Layer Injection

Observed issue:

- ODW currently influences neutral-transit movement burden through low-level forward/parallel redistribution

Why it is under review:

- this reads more like tactical posture injection than neutral-baseline substrate behavior

### 4.4 Stray-Dependent Attract

Observed issue:

- the current stray-dependent attract path can operate as an extra centripetal recovery term under neutral transit

Why it is under review:

- the current stray reading is still centroid-distance dependent
- doctrine already identifies that centroid-only stray detection is structurally limited for formation interpretation

### 4.5 FSR

Observed issue:

- FSR still appears as part of a legacy correction family that affects rendered movement outcome before projection is interpreted

Why it is under review:

- it is not yet clear that FSR belongs in a neutral-baseline default path rather than a removable or migratable correction layer

## 5. Explicit Non-Authorizations

This decision does **not** authorize:

- broad runtime rewrite
- silent change to canonical parameter semantics
- silent change to baseline movement behavior
- continued expansion of old-factor interaction DOE on the current polluted path
- reframing current neutral-transit results as evidence that the shared path is already a valid replacement baseline

## 6. Recommended Next Bounded Engineering Step

The next bounded step should be:

1. produce a very bounded decoupling review memo
2. clarify which of the current candidates are best treated as cut candidates vs migrate candidates
3. ask Governance to choose the first very small cut candidate
4. after that cut only, run very small confirmation checks

Recommended order of attention:

- centroid-restoration vs expected-position restoration review first
- then MB / ODW movement-layer injection review
- then explicit review of stray-dependent attract and FSR

This keeps the work in inspect/review mode and avoids silently turning the decision into rewrite authorization.

## 7. Backward-Compatibility / Canonical-Discipline Note

This record changes no runtime behavior.

- battle path remains unchanged
- current neutral-transit fixture remains a diagnostic surface, not a new baseline
- no canonical documents are modified here
- no movement semantics are reinterpreted in code here
- this decision should be read as a governance stop-signal on further old-factor DOE expansion, plus a bounded authorization for documentation and decoupling review only

## 8. Compressed Conclusion

`neutral_transit_v1` has already done enough to show that several current shared-path mechanisms should no longer be treated as normal neutral-baseline tuning factors. The correct next step is not more `FR x MB x ODW` interaction DOE, but bounded decoupling review that clarifies which mechanisms should be cut, migrated, or replaced by cleaner upstream semantics.
