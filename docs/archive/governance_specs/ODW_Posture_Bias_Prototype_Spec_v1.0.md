# ODW Posture Bias Prototype Spec v1.0

Status: Engineering prototype specification  
Scope: First-cut bounded ODW runtime prototype  
Authority Context: Governance-authorized review-to-prototype transition  
Implementation: Not authorized by this document

## I. Purpose

This document specifies the first bounded ODW prototype implied by:

- `docs/archive/governance_specs/ODW_Runtime_Mapping_Review_v1.0.md`
- `docs/archive/governance_specs/ODW_Prototype_Insertion_Note_v1.0.md`

The goal is to define one implementation-ready prototype path without broadening scope.

## II. Prototype Role

`ODW` is used as:

```text
offense / defense posture bias
inside movement-layer pressure distribution
```

The prototype does not treat `ODW` as:

- combat strength
- target selection
- pursuit threshold
- retreat threshold
- formation selector

## III. Insertion Point

The insertion point is:

```text
movement-layer target-axis decomposition
inside per-unit forward-pressure recomposition
```

This refers to the runtime region where:

- `m_parallel`
- `m_tangent`

already exist as explicit components of the maneuver vector, and where a unit's lateral offset
within fleet width can be evaluated.

This is currently the cleanest place to express posture bias while preserving geometry emergence.

## IV. Prototype Variable

The prototype introduces one derived runtime coefficient:

```text
odw_centered = clip((ODW - 5) / 4, -1, 1)
```

Under canonical 1..9 interpretation:

- `ODW = 1 -> odw_centered = -1.0`
- `ODW = 5 -> odw_centered =  0.0`
- `ODW = 9 -> odw_centered = +1.0`

The important requirement is that the coefficient is:

- centered at `5`
- symmetric around the midpoint
- bounded and small

## V. Prototype Formula

Define one small prototype gain:

```text
k_odw > 0
```

Recommended first-cut range:

```text
k_odw in [0.2, 0.4]
```

Define one bounded clip half-width:

```text
clip_delta_odw >= 0
```

Interpretation:

- `clip_delta_odw = 0.2 -> parallel_scale in [0.8, 1.2]`
- `clip_delta_odw = 1.0 -> parallel_scale in [0.0, 2.0]`

Derived scale:

```text
lateral_norm = clip(abs(lateral_offset) / lateral_span_ref, 0, 1)
width_profile = 1 - 2 * lateral_norm
parallel_scale = clip(1.0 + k_odw * odw_centered * width_profile, 1 - clip_delta_odw, 1 + clip_delta_odw)
```

Recomposition:

```text
maneuver = parallel_scale * m_parallel
         + m_tangent
```

Interpretation:

- center units (`lateral_norm ~= 0`) get positive `width_profile`
- wing units (`lateral_norm ~= 1`) get negative `width_profile`
- offensive ODW increases center forward pressure and reduces wing forward pressure
- defensive ODW does the inverse

This is the entire first-cut behavior change.

## VI. Intended Interpretation

### Higher offensive ODW

Higher ODW produces:

- slightly stronger centerline forward pressure
- slightly weaker wing forward pressure
- more center-led attack posture

### Higher defensive ODW

Lower ODW produces:

- slightly weaker centerline forward pressure
- slightly stronger wing forward pressure
- broader, more holding posture

These are movement redistributions only.

They do not directly encode tactics or formation templates.

## VII. Non-Goals

The first prototype must not:

- modify `deep_pursuit_mode`
- modify pursuit confirmation threshold
- modify retreat gating
- modify combat damage scale
- modify targeting semantics
- inject direct curvature templates

If any of those changes appear in the same prototype, the prototype is out of scope.

## VIII. Why This Preserves Orthogonality

### Versus `PD`

`PD` still governs pursuit willingness.

The prototype only changes posture while moving.

### Versus `RT`

`RT` still governs retreat willingness.

The prototype does not alter retreat entry or retreat thresholds.

### Versus `MB`

`MB` still controls mobility redistribution semantics.

`ODW` only adds offense/defense posture pressure bias inside the already-existing decomposition layer.

### Versus `FR`

`FR` still governs resistance to deformation.

`ODW` does not alter rigidity or centroid-restoration semantics.

## IX. Minimal Validation Batch

The first validation batch should be small.

Recommended design:

- fixed:
  - movement baseline = `v3a`
  - collapse source baseline unchanged
  - `PD = 5`
  - `RT = 5`
  - `MB = 5`
  - `FR = 5`
- vary only:
  - `ODW = {2, 5, 8}`
- opponents:
  - 2 to 3 canonical anchors
- one deterministic seed profile

The first question is only:

```text
Does ODW create interpretable posture difference
without acting like PD, RT, MB, or FR?
```

## X. Readout Focus

The initial prototype should be evaluated using:

- approach geometry
- front width / concentration tendency
- first-contact posture
- event topology side effects

Primary qualitative question:

```text
Does ODW redistribute forward pressure across fleet width
in an interpretable way, without hidden threshold substitution?
```

## XI. Recommendation

The next engineering step should implement exactly this bounded prototype and nothing more:

```text
ODW -> width-wise forward-pressure redistribution
inside movement decomposition
```

This is the smallest first prototype that is:

- interpretable
- orthogonal
- bounded
- compatible with canonical doctrine
