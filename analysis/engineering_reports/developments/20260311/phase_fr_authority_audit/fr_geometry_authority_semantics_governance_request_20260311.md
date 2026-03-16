# FR Geometry Authority Semantics Governance Request

Date: 2026-03-11
Status: Request for Governance Adjudication
Thread: `analysis/engineering_reports/developments/20260311/phase_fr_authority_audit`

Engine Version: current local test harness over frozen runtime baseline
Modified Layer: none in this request; interpretive request only
Affected Parameters: `FR`, `ODW`, `MB`, `PD`
New Variables Introduced: none
Cross-Dimension Coupling: concerns possible runtime over-coupling of `FR` into front-geometry emergence
Mapping Impact: none
Governance Impact: request adjudication on intended authority split for front-geometry formation
Backward Compatible: yes

Summary

1. Human and Engineering are now closely aligned on the main concern: `FR` appears to be carrying authority beyond its intended role.
2. The remaining need is not another broad DOE, but a governance ruling on the intended semantic split among `FR`, `ODW`, `MB`, and `PD`.
3. The concrete focus is front-geometry posture authority, especially `FrontCurv` trend formation.
4. Engineering requests a ruling on whether `FR` may affect posture direction at all, or only rate / persistence / resistance.
5. This ruling is needed so subsequent bounded validation can be judged against a stable semantic target.

## Context

Current FR authority audit and bounded validation work has already produced evidence that:

- current runtime behavior makes `FR` look too influential in wedge-emergence and front-geometry selection
- this is especially visible around the `FR=5` threshold band
- `ODW` currently reads more like a support / quality signal than a clear primary posture-direction driver

That evidence is documented in:

- `analysis/engineering_reports/developments/20260311/phase_fr_authority_audit/fr_authority_doe_summary.md`
- `analysis/engineering_reports/developments/20260311/phase_fr_authority_audit/fr_runtime_authority_decomposition_note_20260311.md`
- `analysis/engineering_reports/developments/20260311/phase_fr_authority_audit/fr5_threshold_governance_request_20260311_round3.md`

This request is narrower.

It asks governance to adjudicate the intended semantic authority split behind front-geometry formation, so engineering can judge future correction candidates against the right target.

## Human Position

Human current understanding can be restated as:

1. `FR` should not influence front-geometry posture direction.
2. Concretely, `FR` should not decide the formation trend of `FrontCurv`.
3. `ODW` should be the primary driver of `FrontCurv` trend formation.
4. `MB` and `PD` may influence instantaneous geometric bias, but should not replace `ODW` as the main posture-direction authority.
5. Therefore, for personalities with:
   - `FR = {2, 5, 8}`
   - `ODW = {2, 5, 8}`
   - all other parameters fixed at `5`
   the long-run `FrontCurv` trend should track `ODW`, not `FR`.
6. In that setup, `FR` may change response speed or how strongly a formed posture resists deformation, but should not change the sign or family of the trend itself.

## Engineering Position

Engineering agrees with the direction of the above, but proposes a slightly tighter wording:

1. `FR` should not hold posture-selection authority.
2. `FR` may legitimately hold:
   - deformation resistance authority
   - shape persistence authority
   - carry-through / recovery-speed authority
3. `FR` should not legitimately hold:
   - posture-direction authority
   - `FrontCurv` sign-selection authority
   - wedge-emergence gate authority
4. `ODW` should be the primary posture-direction authority for front geometry.
5. `MB` and `PD` should be read as transient bias / exploitation modifiers:
   - `MB` as transient deformation bias or lateral redistribution pressure
   - `PD` as forward exploitation / conversion pressure
6. Therefore Engineering would phrase the intended split as:

```text
ODW decides posture direction.
FR decides resistance, persistence, and recovery speed.
MB and PD modulate transient deformation / conversion pressure.
```

## Shared Ground

Human and Engineering appear already aligned on these points:

- `FR` should not be the main generator of wedge tendency
- `FR` should not be the main selector of `FrontCurv` trend
- `ODW` should matter more directly for front posture direction
- `MB` and `PD` should not replace `ODW` as the main posture-direction gate
- current runtime behavior likely overstates `FR` authority in geometry emergence

## Remaining Ambiguity Requiring Governance Ruling

The remaining ambiguity is subtle but important:

### Option A: Strict Separation

`FR` should have zero authority over front-geometry trend direction.

Interpretation:

- once posture direction is controlled for, varying `FR` should not change the sign or family tendency of `FrontCurv`
- `FR` may only change rate, smoothness, persistence, and resistance after the direction has already been set by other mechanisms

### Option B: Weak Indirect Influence Allowed

`FR` should not be a primary posture-direction authority, but weak indirect influence on observed `FrontCurv` trend may be tolerated through stability dynamics.

Interpretation:

- `FR` still should not act as a wedge gate
- but governance may tolerate some secondary effect on observed geometry because more stable formations can preserve an already-emerging posture more clearly

Engineering currently leans toward Option A as the cleaner target for correction design, but requests governance to decide explicitly.

## Proposed Testable Semantic Constraint

Engineering proposes the following candidate governance statement for approval or correction:

```text
When MB, PD, and the remaining parameters are held neutral,
front-geometry posture trend should be ordered primarily by ODW.
FR may affect response speed, persistence, and resistance to deformation,
but should not determine the direction family of FrontCurv.
```

A stricter experimental restatement would be:

```text
With MB=5, PD=5, and other non-target parameters fixed,
the ordering of FrontCurv tendency across ODW={2,5,8}
should be materially stronger than any ordering across FR={2,5,8}.
FR should not flip the posture family that ODW selects.
```

## Why This Ruling Matters

Without a governance ruling on the intended semantic split, engineering cannot cleanly decide whether a candidate probe is:

- correctly removing excess `FR` authority
- over-suppressing legitimate `FR` stabilization behavior
- or merely shifting readout noise between `FR`, `ODW`, `MB`, and `PD`

This is especially important because current `FR5`-centered correction work depends on knowing whether the target is:

- "FR should have no posture-direction authority at all"

or:

- "FR may have weak secondary carry-through influence, but not gate-level authority"

## Governance Questions

Engineering requests governance to adjudicate the following:

1. Should `FR` be treated as having zero intended authority over front-posture direction, including `FrontCurv` trend family?
2. Is `ODW` the intended primary authority for front-posture direction?
3. Should `MB` and `PD` be treated only as transient bias / exploitation modifiers rather than posture-direction gates?
4. In a neutralized test regime with `MB=5`, `PD=5`, and other parameters fixed, should variation in `FR` be expected to leave `FrontCurv` trend family unchanged?
5. Is Engineering correct to use the distinction below as the semantic boundary?

```text
FR = deformation resistance / persistence authority
ODW = posture-direction authority
MB/PD = transient deformation / conversion modifiers
```

## Engineering Recommendation

Engineering recommends that governance issue an explicit semantic ruling closest to:

```text
FR must not serve as a posture-direction selector or wedge-emergence gate.
ODW should be the primary authority on front-posture direction.
MB and PD may modulate transient shape bias and exploitation,
but not replace ODW as the dominant front-posture trend selector.
FR may affect speed, persistence, and resistance only.
```

If governance agrees, this would provide a precise target for the next bounded validation stage.

## Reproducibility Notes

This request does not introduce new experiments.

It is based on the existing thread artifacts under:

- `analysis/engineering_reports/developments/20260311/phase_fr_authority_audit`

Most relevant references:

- `fr_authority_doe_summary.md`
- `fr_runtime_authority_decomposition_note_20260311.md`
- `fr5_threshold_governance_request_20260311_round3.md`
