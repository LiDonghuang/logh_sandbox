# FR Runtime Authority Decomposition Note

Date: 2026-03-11
Thread: `analysis/engineering_reports/developments/20260311/phase_fr_authority_audit`
Status: bounded engineering note for governance review

Question:

```text
Which runtime paths currently carry FR authority,
which of those are legitimate persistence authority,
and which appear to have crossed into emergence-threshold control.
```

Working canonical position:

```text
FR = resistance to formation deformation
```

This note does not propose a semantic rewrite.
It proposes a bounded authority decomposition and one minimal correction candidate.

## 1. Evidence Baseline

This note uses two already-generated evidence sources:

- code audit in `fr_authority_audit_note.md`
- bounded DOE in `fr_authority_doe_run_table.csv` / `fr_authority_doe_summary.md`

Relevant DOE facts:

- total runs: `972`
- unique DOE cells: `54`
- unique final-state digests: `54`
- interpretation: under the current controlled synthetic setup, behavior collapses to cell-level determinism

Key readouts from the DOE:

- FR-level wedge presence:
  - `FR=2`: `0.0%`
  - `FR=5`: `27.8%`
  - `FR=8`: `88.9%`
- FR-level A win rate:
  - `FR=2`: `22.2%`
  - `FR=5`: `22.2%`
  - `FR=8`: `88.9%`
- FR-level wedge-capable cells:
  - `FR=2`: `0/18`
  - `FR=5`: `5/18`
  - `FR=8`: `16/18`
- ODW split:
  - `ODW=2`: `WedgePresent=25.9%`, `StructuralFragility=88.9%`, `runtime_c_conn_A=0.8172`
  - `ODW=8`: `WedgePresent=51.9%`, `StructuralFragility=44.4%`, `runtime_c_conn_A=0.9036`
- coherent A-side penetration wedges observed: `0` runs

Immediate implication:

- FR is not behaving like a direct wedge instruction
- but FR is strongly altering which cells can cross into wedge emergence at all
- ODW is clearly readable, but its effect is mostly conditional on FR already opening the geometric channel

## 2. Authority Decomposition

### 2.1 Legacy/debug cohesion carry-through

Location:

- `runtime/engine_skeleton.py:420`
- `runtime/engine_skeleton.py:422`

Observed role:

- updates legacy/debug `cohesion_v1` with an FR-coupled scalar drift

Authority reading:

- deformation resistance: negligible
- shape persistence: low
- emergence-threshold influence: none direct
- other suspicious authority: debug carry-through only

Governance label:

- `tolerated side effect`

Judgment:

- this is not the active source of the present defect hypothesis
- it should be documented, but not targeted first

### 2.2 Active v3a centroid-restoration term

Location:

- `runtime/engine_skeleton.py:757`
- `runtime/engine_skeleton.py:912`
- `runtime/engine_skeleton.py:913`

Observed role:

```text
cohesion_x = (kappa * cohesion_gain * cohesion_scale) * cohesion_dir[0]
cohesion_y = (kappa * cohesion_gain * cohesion_scale) * cohesion_dir[1]
```

Authority decomposition:

- deformation resistance:
  - yes
  - this is the most direct expression of FR as regroup / restore authority
- shape persistence:
  - yes
  - the term acts every tick and helps retain developing front asymmetry once it appears
- emergence-threshold influence:
  - yes, and this is the main current concern
  - because the same FR-scaled term is active pre-contact and continuously, it appears to help decide whether a weak forward protrusion survives long enough to become an observed wedge
- other suspicious coupled authority:
  - phase-unspecific authority
  - the same FR weight is applied before contact, during deformation buildup, and during later carry-through

Governance label:

- deformation resistance portion: `canonical-consistent`
- shape persistence portion: `canonical-consistent`
- emergence-threshold portion: `suspected over-coupling defect`
- phase-unspecific always-on application: `suspected over-coupling defect`

Why this is the primary suspect:

- DOE cell coverage changes sharply with FR:
  - `FR=2`: `0/18` wedge cells
  - `FR=5`: `5/18`
  - `FR=8`: `16/18`
- that pattern is much more consistent with gate authority than with pure stabilization authority
- ODW cannot create wedge at `FR=2`, but becomes legible at `FR=5/8`
- this implies FR is occupying more than persistence authority on the active path

### 2.3 Non-v3a cohesion-restoration path

Location:

- `runtime/engine_skeleton.py:991`
- `runtime/engine_skeleton.py:997`
- `runtime/engine_skeleton.py:1002`
- `runtime/engine_skeleton.py:1003`

Observed role:

- structurally similar FR-coupled cohesion restoration on the non-`v3a` path

Authority decomposition:

- deformation resistance: yes
- shape persistence: yes
- emergence-threshold influence: possible, but not the active mainline focus of this thread
- other suspicious authority: mirror-risk if legacy path is reopened

Governance label:

- active-thread status: `tolerated side effect`
- latent structural risk: `suspected over-coupling defect` if this path becomes mainline again

Judgment:

- this path supports the diagnosis that FR-overreach is not an isolated coding accident
- but it is not the first bounded correction target because it is not the current active mainline for this thread

### 2.4 FSR contraction scaling

Location:

- `runtime/engine_skeleton.py:1123`
- `runtime/engine_skeleton.py:1124`

Observed role:

```text
k_f = fsr_strength * (0.5 + (0.5 * kappa_f))
```

Authority decomposition:

- deformation resistance: indirect
- shape persistence: high
- emergence-threshold influence: secondary
- other suspicious authority: contact-phase carry-through amplifier

Governance label:

- primary reading: `canonical-consistent`
- secondary reading: `tolerated side effect`

Judgment:

- FSR is probably not the first source of wedge emergence
- but once a protrusion starts, FR-coupled FSR likely helps it survive
- this makes FSR a secondary amplifier, not the first correction candidate

## 3. Authority Classification Summary

### 3.1 Canonical-consistent authorities

- FR contributing to regroup / resistance to deformation
- FR contributing to shape persistence after deformation begins
- FR participating in compactness retention through FSR

These are all consistent with:

```text
FR = resistance to formation deformation
```

### 3.2 Tolerated side effects

- debug `cohesion_v1` carry-through
- non-mainline FR restoration paths that are not active in the current thread
- secondary FSR carry-through amplification

These are not ideal, but they are not the first place to intervene.

### 3.3 Suspected over-coupling defects

- active `v3a` centroid-restoration term carrying too much emergence-threshold authority
- the same active term applying FR with too much pre-contact, always-on influence

This is the central current defect hypothesis.

The defect hypothesis is not:

```text
FR explicitly generates wedge geometry
```

It is:

```text
FR currently stabilizes and restores strongly enough, early enough,
that it is helping determine whether wedge-like geometry emerges at all.
```

## 4. Minimal Correction Candidate

### 4.1 Proposed first target

Target only the active `v3a` centroid-restoration FR coupling:

- `runtime/engine_skeleton.py:912`
- `runtime/engine_skeleton.py:913`

Do not first-touch:

- ODW
- MB
- PD
- FSR
- TL
- observer taxonomies

### 4.2 Proposed bounded correction

Replace the raw FR multiplier on this path with a compressed monotonic internal map.

Conceptually:

```text
current:  cohesion_restore ~ kappa
proposal: cohesion_restore ~ kappa_eff
where kappa_eff preserves FR ordering but compresses low/high spread
```

Example paired-test candidate:

```text
kappa_eff = 0.25 + (0.50 * kappa)
```

Reason for choosing this type of correction:

- it touches one active path only
- it does not add a new user-facing parameter
- it does not rewrite canonical FR semantics
- it reduces the present `FR=2 -> 5 -> 8` authority spread on the most suspicious path
- it leaves ODW untouched, so ODW readability can improve only if FR truly stops over-occupying the gate

### 4.3 Why this path is the best first downgrade

- it is the active mainline path
- it acts every tick
- it acts before contact
- it is the path most aligned with the DOE gate pattern
- it is the smallest correction that can directly test the over-authority hypothesis

### 4.4 Expected outcome of the correction

The expected outcome is not:

```text
eliminate wedges
```

The expected outcome is:

- reduce FR control over whether wedge appears at all
- keep FR meaningful as deformation resistance / persistence authority
- return more wedge-emergence voice to movement / posture-side drivers
- make ODW posture support more readable in the threshold band

## 5. Paired Confirmation Plan

This plan is intentionally small.

It is not a new large DOE.

### 5.1 Variant pair

- Variant A: current baseline
- Variant B: compressed-FR centroid-restoration candidate

### 5.2 Cell set

Use six paired cells, chosen to cover guardrail, threshold, and high-authority regimes:

1. `FR2_MB2_PD8_ODW8`
   - low-FR guardrail
   - current behavior: wins without wedge

2. `FR2_MB8_PD8_ODW8`
   - low-FR high-pressure guardrail
   - current behavior: loses without wedge

3. `FR5_MB2_PD8_ODW8`
   - threshold-band wedge-but-lose case
   - current behavior: wedge present, non-fragile by current readout, but B takes the alive-lead trajectory early

4. `FR5_MB8_PD2_ODW8`
   - threshold-band wedge-and-win case
   - useful to test whether the candidate correction over-suppresses viable penetration

5. `FR8_MB5_PD8_ODW2`
   - high-FR fragile wedge-but-lose case
   - useful to test whether FR over-authority is masking structural weakness

6. `FR8_MB2_PD2_ODW8`
   - high-FR non-fragile wedge-and-win case
   - useful to confirm that strong wedges are not simply erased

Because the current controlled setup is behaviorally deterministic by cell, the paired plan does not need another large seed sweep.

Recommended run count:

- `6 cells x 2 variants x 3 seed profiles = 36 runs`

Use three seed profiles only as a guardrail check:

- `SP01`
- `SP09`
- `SP18`

### 5.3 Required readout

For each paired cell, compare:

- `wedge_present_A`
- `front_profile_A`
- `structural_fragility_A`
- `runtime_c_conn_mean_A`
- `runtime_collapse_sig_mean_A`
- `first_alive_lead_side`
- `first_major_divergence_side`
- `first_major_divergence_tick`
- `alive trajectory`
- posture-family readout:
  - `precontact_wedge_p50_A`
  - `precontact_frontcurv_p50_A`
  - `precontact_cw_pshare_p50_A`
  - `precontact_pospersist_max_abs_A`

### 5.4 What the paired test should confirm

Desired direction:

- wedge gate should relax in the threshold band, especially around `FR=5`
- ODW support signal should become more interpretable
- alive-curve divergence should look less like FR-only gate control
- no obvious new bad effect should appear in low-FR guardrail cells

Undesired result:

- widespread new wedge emergence at `FR=2`
- total collapse of high-FR penetration capability
- large new instability in alive curves

## 6. Engineering Judgment

My current engineering judgment is:

- FR canonical semantics should remain unchanged
- the current issue is runtime authority distribution, not semantic definition
- the active `v3a` centroid-restoration path is the first place to intervene
- FSR should not be the first correction target
- ODW should not be "promoted" to solve this problem

So the next correct action is:

```text
prepare one bounded correction on the active FR centroid-restoration path,
then verify it with a small paired confirmation plan.
```
