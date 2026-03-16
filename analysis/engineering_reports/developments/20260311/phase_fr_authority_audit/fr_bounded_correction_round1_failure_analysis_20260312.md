# FR Bounded Correction Round-1 Failure Analysis

Date: 2026-03-12
Status: Engineering closeout note
Thread: `analysis/engineering_reports/developments/20260311/phase_fr_authority_audit`

Engine Version: current local test harness over frozen runtime baseline
Modified Layer: none in this note
Active Evidence Base:
- `continuous_fr_authority_round1_single_seed_summary.md`
- `continuous_fr_authority_round1_single_seed_hard_constraints.csv`
- `continuous_fr_authority_round1_single_seed_candidate_summary.csv`
- `continuous_fr_authority_round1_single_seed_ranked_candidates.csv`

## 1. Batch Scope and Decisive Outcome

This note closes the current bounded-correction round-1 continuous shaping search.

Batch scope:

- single-seed
- `SP01`
- `126` candidates
- `22` cells
- `2772` runs

Decisive outcome:

```text
hard_constraint_pass = 0 / 126
```

Engineering judgment:

```text
The bounded-correction objective was valid.
The locked suspect path remains a credible target.
But the currently tested continuous shaping family failed to deliver a viable bounded correction.
```

This result does not invalidate the authority-audit diagnosis.

It invalidates the currently tested correction family.

## 2. Core Failure Question

Question:

```text
Why did the current continuous shaping family fail as bounded correction?
```

Engineering answer:

```text
Because the family was structurally subtractive in the wrong way.
It attenuated the same pre-contact centroid-restoration authority across broad FR5-centered slices,
but did not reallocate that authority into a cleaner geometry or support channel.
```

So the family could sometimes reduce a local sentinel symptom, but it did so by making the overall structure less readable and less connected.

In short:

- it suppressed authority
- it did not reorganize authority

That is why it behaved like degradation pressure more often than true authority-space release.

## 3. Family-Level Comparison

### Family A

Family A was the most aggressive pure attenuation family.

Observed round-1 pattern:

- `54` candidates
- `0` hard passes
- `28` control harms
- `37` protected-cell harms
- `54 / 54` worse `ODW readability`
- `54 / 54` worse `runtime_c_conn`
- `54 / 54` worse `runtime_collapse`

Interpretation:

- A produces the clearest evidence that pure FR-path attenuation is too blunt
- it can create local sentinel gains
- but it does so by broadly weakening structure

### Family B

Family B added continuous `MB` taper.

Observed round-1 pattern:

- `36` candidates
- `0` hard passes
- `14` control harms
- `20` protected-cell harms
- `36 / 36` worse `ODW readability`
- `35 / 36` worse `runtime_c_conn`
- `35 / 36` worse `runtime_collapse`

Interpretation:

- B is less blunt than A
- but the `MB` taper still acts mainly as selective subtraction
- it does not solve the core problem that the family is shrinking centroid-restoration authority without creating a healthier replacement geometry

### Family C

Family C added smooth `PD` shoulder plus continuous `MB` taper.

Observed round-1 pattern:

- `36` candidates
- `0` hard passes
- `15` control harms
- `19` protected-cell harms
- `36 / 36` worse `ODW readability`
- `33 / 36` worse `runtime_c_conn`
- `33 / 36` worse `runtime_collapse`

Interpretation:

- C is the most semantically refined family in this batch
- but even here the same failure remains
- smoothing the trigger is not enough if the action itself is still mainly subtractive

## 4. Control-Damage Analysis

Dominant harmed control:

- `FR2_MB2_PD8_ODW8`

Damage frequency:

- harmed in `51 / 126` candidates

Secondary harmed control:

- `FR8_MB2_PD2_ODW8`
- harmed in `7 / 126` candidates

The other two controls were not the main failure site.

### Why `FR2_MB2_PD8_ODW8` dominates

Baseline anchor for `FR2_MB2_PD8_ODW8`:

- win rate: `100%`
- `wedge_present`: `0%`
- `structural_fragility`: `0%`
- `runtime_c_conn`: `0.9646`
- `runtime_collapse`: `0.0354`
- `fire_eff_contact_to_cut`: `0.5497`

Interpretation:

- this is already a healthy low-`FR` control
- it does not exhibit the FR5 preemption defect that the thread is trying to release
- but it still depends on enough pre-contact centroid-restoration authority to remain legible under high `PD`

So when the candidate family subtracts from the same centroid-restoration channel, the family is not "releasing blocked authority" here.

It is simply taking away legitimate structural support from a healthy case.

That is why this control becomes the dominant damage site.

This strongly suggests the current family does not isolate the pathological FR5 overreach cleanly enough.

## 5. Protected-Cell Analysis

Protected cell:

- `FR5_MB8_PD2_ODW8`

Observed round-1 result:

- improved in `0 / 126`
- unchanged in `50 / 126`
- harmed in `76 / 126`
- minimum delta: `-100`
- maximum delta: `0`

Interpretation:

- the family never helps this legitimate case
- at best it leaves it unchanged
- more often it strips away valid FR authority

This is decisive.

It means the current shaping family cannot distinguish:

- pathological FR overreach
- from healthy FR support

So even when the suspect path is correct, the current corrective action is not selective enough.

## 6. Structural Failure Pattern

### 6.1 ODW readability

Observed result:

```text
ODW readability worsened in 126 / 126 candidates
```

Engineering interpretation:

- the family acts on a shared centroid-restoration term
- it does not add any new ODW-specific differentiation
- so it reduces the common structural signal that both ODW states are reading from
- the result is weaker posture distinction, not cleaner posture distinction

Put differently:

```text
the family changes support magnitude,
not support legibility
```

### 6.2 runtime_c_conn

Observed result:

- worse in `122 / 126` candidates

Interpretation:

- continuous attenuation lowers the same path that was helping hold pre-contact structural connectivity
- therefore connectivity softens before a healthier alternative geometry has formed

### 6.3 runtime_collapse

Observed result:

- worse in `122 / 126` candidates

Interpretation:

- once pre-contact connectivity is weakened, collapse pressure rises almost mechanically
- this is why `runtime_c_conn` falls and `runtime_collapse` rises together

This pairing is one of the cleanest signals that the family is producing structural weakening, not healthy release.

## 7. Sentinel Pattern and False Positives

Two required sentinels:

- `FR5_MB2_PD8_ODW8`
- `FR5_MB5_PD8_ODW8`

Observed result:

- `FR5_MB2_PD8_ODW8` improved in `10` candidates
- `FR5_MB5_PD8_ODW8` improved in `18` candidates
- both improved together in `0` candidates

This matters.

It means some candidates can create a local win on one slice, but the family does not produce a stable release shape across the required FR5 window.

The improvement is therefore not robust enough to count as bounded correction.

False-positive pattern:

- `28` candidates showed positive sentinel gain while still carrying structural worsening underneath

Typical pattern:

- one sentinel gets better
- controls or protected cell get worse
- `ODW readability` gets worse
- `runtime_c_conn` gets worse
- `runtime_collapse` gets worse

This is the exact pattern Engineering needed to detect.

It shows why win-gain alone is not a valid readout here.

## 8. Implication for Geometry-Release Logic

The current family was built on the right suspect path but the wrong release logic.

It assumed:

```text
if centroid-restoration authority is too strong in the bad slice,
then smoothly subtracting from that path should release authority space
```

Round-1 falsifies that assumption for bounded correction.

Why:

- the path is real
- but the path is not serving only pathological authority
- it is also carrying healthy structural support
- broad continuous attenuation therefore damages healthy support faster than it creates clean release

So the geometry-release logic fails because:

```text
it is subtractive without being reallocative
```

This thread therefore ends with a clear stop-point:

- suspect path diagnosis survives
- current continuous family fails
- bounded candidate screening should stop here

## 9. Closeout Judgment

Engineering closeout judgment:

```text
The current bounded-correction family should not be expanded further in this thread.
No candidate from the current continuous family justifies second-round finalist validation.
The completed batch is more valuable as a failure map than as a candidate source.
```
