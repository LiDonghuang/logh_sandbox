# ODW Unstable Wedge Case Report for Governance

Status: Engineering Case Report  
Scope: ODW posture-bias prototype readout under a mixed high-FR / high-MB / high-PD vs low-ODW configuration  
Date: 2026-03-10

## 1. Purpose

This note records one specifically interesting runtime case observed during ODW posture-bias exploration.

The case is noteworthy because Side B produces a visually obvious wedge-like pre-contact deformation, but the wedge appears unstable and ultimately loses despite creating strong local penetration pressure.

The purpose of this note is not baseline evaluation.  
The purpose is to clarify what this case implies about:

- ODW posture bias
- FR as shape stabilizer
- MB as lateral redistribution amplifier
- PD as forward extension pressure
- the limits of current fleet-level readouts

## 2. Accepted Reproduction Case

The originally referenced BRF was:

- `analysis/exports/battle_reports/20260310/test_run_v1_0_20260310_012530_Battle_Report_Framework_v1.0.md`

During reproduction, archetype drift was detected in the current runtime JSON.  
An initial rerun under current archetype values was rejected.

The accepted same-config reproduction is:

- `analysis/exports/battle_reports/20260310/test_run_v1_0_20260310_025110_Battle_Report_Framework_v1.0.md`

This accepted rerun restored the original intended archetype parameters for this case:

- Side A (`grillparzer`): `MB=2, FR=2, PD=2, ODW=8`
- Side B (`knappstein`): `MB=8, FR=8, PD=8, ODW=2`
- all other personality parameters held at `5`

The accepted rerun also matched the original event timeline exactly:

- `First Contact = 108`
- `First Kill = 116`
- `Formation Cut = 127`
- `Pocket Formation = 141`
- `Endgame Onset = 320`
- `End = 436`

## 3. Human Observation Summary

Human review of animation for this case can be summarized as follows:

- Side A maintains a relatively stable rectangular 2:1 approach posture.
- Side B develops a wedge-like front during the first ~100 ticks.
- However, this is not a clean or stable wedge.
- The front appears to oscillate and deform while still retaining a visible center-led protrusion.
- Side B then penetrates aggressively, but later loses decisively.

Engineering agrees that this is an informative case because the geometry is visually strong, but the quality of the posture is poor.

## 4. BRF Geometry / Collapse Readout

Source:

- `analysis/exports/battle_reports/20260310/test_run_v1_0_20260310_025110_Battle_Report_Framework_v1.0.md`

### 4.1 Pre-contact summary

Window:

- `t=1..107`

Side A:

- `Wedge p10/p50/p90 = 1.058 / 1.123 / 1.149`
- `FrontCurv p10/p50/p90 = 0.037 / 0.205 / 0.324`
- `C_W_PShare p10/p50/p90 = -0.003 / -0.000 / 0.003`
- `PosPersist max_abs = 0.0`
- `Tendency = mixed/unstable`

Side B:

- `Wedge p10/p50/p90 = 0.842 / 1.251 / 1.661`
- `FrontCurv p10/p50/p90 = 0.049 / 0.289 / 0.560`
- `C_W_PShare p10/p50/p90 = 0.000 / 0.000 / 1.000`
- `PosPersist max_abs = 2.0`
- `Tendency = mixed/unstable`

Interpretation:

- Side B clearly carries the stronger wedge-like deformation signal.
- Side B also shows stronger positive front curvature.
- However, `C_W_PShare` and `PosPersist` do not yet provide a clean stable posture readout in this case.
- This supports the view that the wedge is visually real, but not yet well characterized by the current pressure-distribution summaries.

### 4.2 Event-aligned snapshots

At `First Contact`:

- Side A: `Wedge=1.063`, `FrontCurv=-0.069`, `CollapseSig=0.110`
- Side B: `Wedge=1.608`, `FrontCurv=0.390`, `CollapseSig=0.150`

At `Formation Cut`:

- Side A: `Wedge=1.063`, `FrontCurv=-0.170`, `CollapseSig=0.130`
- Side B: `Wedge=1.520`, `FrontCurv=0.324`, `CollapseSig=0.103`

At `Pocket Formation`:

- Side A: `Wedge=1.009`, `FrontCurv=0.099`, `CollapseSig=0.521`
- Side B: `Wedge=1.297`, `FrontCurv=0.496`, `CollapseSig=0.141`

Interpretation:

- Side B reaches contact and cut with a much stronger wedge / center-led front than Side A.
- This is not a late-fight artifact; it is already present at contact.
- The wedge-like shape persists through cut and pocket, though still with unstable posture readout support.

### 4.3 Collapse signal summary

Side A:

- `collapse_sig mean/p95 = 0.027 / 0.100`
- `c_conn = 0.973`
- `rho = 0.458`
- `c_scale = 1.000`

Side B:

- `collapse_sig mean/p95 = 0.166 / 0.257`
- `c_conn = 0.834`
- `rho = 0.434`
- `c_scale = 1.000`

Interpretation:

- Side B carries materially higher pre-contact collapse pressure than Side A.
- The difference is coming from `c_conn`, not from `rho/c_scale`.
- Therefore this case is not a `rho`-driven collapse artifact.
- The wedge-like geometry forms while Side B is already structurally more fragile in connectivity terms.

## 5. Fire Efficiency Audit

Engineering also computed a direct `FireEff` summary from the reproduced run using the same fixed seeds and configuration.

Definition:

- per-tick actual inflicted damage
- divided by current theoretical maximum damage for the surviving units on that tick

### 5.1 Summary

Pre-contact:

- Side A: `mean/p90/peak = 0.000 / 0.000 / 0.000`
- Side B: `mean/p90/peak = 0.000 / 0.000 / 0.000`

Contact to cut (`108..127`):

- Side A: `0.100 / 0.180 / 0.236`
- Side B: `0.283 / 0.436 / 0.470`

Cut to pocket (`127..141`):

- Side A: `0.453 / 0.589 / 0.666`
- Side B: `0.576 / 0.668 / 0.753`

Post-pocket first 40 ticks (`141..181`):

- Side A: `0.616 / 0.711 / 0.759`
- Side B: `0.746 / 0.834 / 0.931`

### 5.2 Interpretation

This is the most important non-obvious finding in the case.

The unstable wedge is not simply "bad geometry with low engagement efficiency."

Instead:

- Side B's deformed wedge produces higher local fire efficiency through contact, cut, pocket, and the immediate post-pocket window.
- Side B therefore gains a real local penetration / engagement advantage.
- However, that advantage does not translate into strategic survival.

Engineering interpretation:

- the wedge is locally efficient
- but globally unstable
- and structurally more fragile in connectivity terms

## 6. Mechanism Interpretation

The current best engineering reading of this case is:

### 6.1 FR still appears to be the dominant shape stabilizer

This case does not suggest that ODW alone is generating the wedge.

Rather:

- `FR=8` preserves deformed shape strongly once the front has been biased away from a flat rectangle
- `FR=2` on Side A allows a simpler, flatter, lower-tension rectangle to remain comparatively unforced

### 6.2 MB amplifies lateral redistribution

With `MB=8`, Side B is more willing to express lateral / tangent redistribution.

This makes the front easier to distort away from a stable flat rectangle.

### 6.3 ODW in the current prototype biases pressure distribution, not direct shape

`ODW=2` does not directly mean "wedge."

Under the current prototype it biases pressure redistribution away from center-dominant stable forward pressure and toward a more wing-assertive / less coherent center profile.

That can still produce a wedge-like front through emergence, but not necessarily a good one.

### 6.4 PD pushes the malformed front into contact

`PD=8` does not create the wedge, but it helps carry an already deformed aggressive front into contact rather than allowing it to relax back into a flatter hold posture.

## 7. Engineering Judgment

This case is interesting precisely because it is not a success case.

It shows that:

- a visually strong wedge-like front can be produced
- the wedge can be locally combat-efficient
- and still be strategically poor

This supports three current working conclusions:

1. FR remains the main factor preserving large-scale geometry.
2. ODW is beginning to matter as a posture-bias modifier, but it is not yet a clean independent geometry driver.
3. Current posture readouts still under-measure the distinction between:
   - visually obvious wedge emergence
   - stable center-led pressure posture
   - unstable but locally efficient penetration shape

## 8. Recommendation to Governance

Engineering does not recommend any baseline decision based on this single case.

Engineering does recommend Governance treat this case as evidence that:

- ODW posture bias is real enough to create meaningful geometric consequences
- but current observer readouts remain weaker than animation evidence for distinguishing good posture from bad posture
- and FR still appears to dominate shape persistence even when ODW / MB / PD contribute to how the deformation develops

Recommended next posture-readout focus:

- improve readouts that separate
  - shape presence
  - pressure coherence
  - local combat efficiency
  - structural fragility

This case should therefore be treated as:

- a useful diagnostic anchor
- not a proof that the current ODW prototype is already sufficient

