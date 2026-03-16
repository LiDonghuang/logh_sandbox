# FR5 Authority-Space Release Validation Note

Date: 2026-03-11
Thread: `analysis/engineering_reports/developments/20260311/phase_fr_authority_audit`
Status: bounded engineering note

Question:

```text
Does the current FR5-centered candidate merely weaken FR,
or does it actually free authority space so ODW, PD, and MB become more readable on a cleaner substrate.
```

## 1. Scope

This note uses the current strongest candidate only:

- baseline: `exp_precontact_centroid_probe`
- candidate: `exp_precontact_plus_fr_centroid_midband_pdhigh_precontact_strong_probe`

No new candidate family is introduced here.

## 2. Validation Batch

Bounded paired batch executed this round:

- `18` FR5 cells:
  - `MB = {2,5,8}`
  - `PD = {2,5,8}`
  - `ODW = {2,8}`
- `4` nearby controls:
  - `FR2_MB2_PD8_ODW8`
  - `FR2_MB8_PD8_ODW8`
  - `FR8_MB2_PD2_ODW8`
  - `FR8_MB5_PD8_ODW2`
- seed profiles:
  - `SP01`
  - `SP09`
  - `SP18`

Total:

```text
22 cells x 2 variants x 3 seed profiles = 132 runs
```

Execution reused:

- `analysis/engineering_reports/developments/20260311/phase_fr_authority_audit/run_fr_authority_doe.py`
  - `build_seed_profiles()`
  - `run_single_case()`

## 3. High-Level Readout

### 3.1 FR5 overall

Baseline:

- `Win = 22.2%`
- `WedgePresent = 27.8%`
- `StructuralFragility = 83.3%`
- `c_conn = 0.8545`
- `collapse = 0.1455`
- `FireEff = 0.3061`
- `first_major_divergence_tick = 148.1`

Candidate:

- `Win = 44.4%`
- `WedgePresent = 11.1%`
- `StructuralFragility = 83.3%`
- `c_conn = 0.8388`
- `collapse = 0.1612`
- `FireEff = 0.3587`
- `first_major_divergence_tick = 202.8`

Immediate reading:

- the candidate is not acting like broad suppression
- wedge overreach decreases
- battle trajectory lengthens materially
- fire conversion improves

This already looks more like authority-space release than simple flat weakening.

## 4. ODW Readability

### 4.1 FR5 + ODW split

`ODW2` baseline:

- `Win = 0.0%`
- `WedgePresent = 0.0%`
- `StructuralFragility = 100.0%`
- `c_conn = 0.8097`
- `collapse = 0.1903`
- `FireEff = 0.2862`

`ODW2` candidate:

- `Win = 22.2%`
- `WedgePresent = 0.0%`
- `StructuralFragility = 100.0%`
- `c_conn = 0.7904`
- `collapse = 0.2096`
- `FireEff = 0.3480`

`ODW8` baseline:

- `Win = 44.4%`
- `WedgePresent = 55.6%`
- `StructuralFragility = 66.7%`
- `c_conn = 0.8993`
- `collapse = 0.1007`
- `FireEff = 0.3259`

`ODW8` candidate:

- `Win = 66.7%`
- `WedgePresent = 22.2%`
- `StructuralFragility = 66.7%`
- `c_conn = 0.8872`
- `collapse = 0.1128`
- `FireEff = 0.3695`

### 4.2 ODW interpretation

The key point is not that `ODW8` creates more wedge.

The more important point is:

- under the candidate, `ODW8` still retains better structural quality than `ODW2`
- but that quality is no longer expressed mainly as `FR`-carried wedge permission in the `PD8` subset

The clearest example is `FR5_PD8`:

`PD8 + ODW2` baseline:

- `Win = 0.0%`
- `WedgePresent = 0.0%`
- `c_conn = 0.8118`
- `collapse = 0.1882`

`PD8 + ODW2` candidate:

- `Win = 66.7%`
- `WedgePresent = 0.0%`
- `c_conn = 0.7539`
- `collapse = 0.2461`

`PD8 + ODW8` baseline:

- `Win = 0.0%`
- `WedgePresent = 100.0%`
- `c_conn = 0.8921`
- `collapse = 0.1079`

`PD8 + ODW8` candidate:

- `Win = 66.7%`
- `WedgePresent = 0.0%`
- `c_conn = 0.8559`
- `collapse = 0.1441`

Engineering reading:

- before correction, `ODW8` in the `PD8` subset looked partly attached to an FR-opened wedge channel
- after correction, `ODW8` still expresses better quality than `ODW2`, but no longer needs to express itself through automatic wedge permission

That is an improvement in ODW readability.

## 5. PD Separability

### 5.1 PD split under FR5

`PD2`:

- baseline and candidate are unchanged
- `Win = 50.0% -> 50.0%`
- `WedgePresent = 16.7% -> 16.7%`

`PD5`:

- baseline and candidate are unchanged
- `Win = 16.7% -> 16.7%`
- `WedgePresent = 16.7% -> 16.7%`

`PD8`:

- `Win = 0.0% -> 66.7%`
- `WedgePresent = 50.0% -> 0.0%`
- `FireEff = 0.3243 -> 0.4824`
- `first_major_divergence_tick = 140.8 -> 306.2`

### 5.2 PD interpretation

This is a strong separation result.

The candidate does not broadly perturb all FR5 cases.

Instead:

- `PD2` stays stable
- `PD5` stays stable
- `PD8` changes dramatically

Engineering reading:

- the candidate is not simply reducing FR everywhere in the middle band
- it is specifically releasing authority where high-PD cases were previously riding through an FR-preconditioned gate

So `PD` becomes more legible as a later conditional mechanism rather than an FR-enabled add-on.

## 6. MB Separability

### 6.1 MB pattern inside the `FR5 + PD8 + ODW8` slice

Baseline:

- `FR5_MB2_PD8_ODW8`: `Win 0`, `Wedge 100`
- `FR5_MB5_PD8_ODW8`: `Win 0`, `Wedge 100`
- `FR5_MB8_PD8_ODW8`: `Win 0`, `Wedge 100`

Candidate:

- `FR5_MB2_PD8_ODW8`: `Win 100`, `Wedge 0`
- `FR5_MB5_PD8_ODW8`: `Win 100`, `Wedge 0`
- `FR5_MB8_PD8_ODW8`: `Win 0`, `Wedge 0`

### 6.2 MB interpretation

Under baseline, the whole slice is flattened by the same FR-opened wedge pattern:

- all three MB levels look like the same failing wedge family

Under candidate:

- the universal wedge gate disappears
- `MB2` and `MB5` recover
- `MB8` remains structurally worse

Engineering reading:

- MB becomes more separable as a deformation-amplification cost factor
- it is no longer hidden under a single FR-led wedge regime across the whole slice

This is strong evidence that the candidate frees expressive space for later conditional mechanisms.

## 7. Does FR Still Have to Open the Door

This is the central root-cause question.

Current evidence says:

- baseline `FR5 + PD8 + ODW8` behaves as if FR has already opened a universal wedge-capable channel
- candidate removes that universal channel while leaving `PD2` and `PD5` largely untouched
- controls remain stable:
  - `FR2_MB2_PD8_ODW8`
  - `FR2_MB8_PD8_ODW8`
  - `FR8_MB2_PD2_ODW8`
  - `FR8_MB5_PD8_ODW2`

Engineering answer:

```text
Yes, the candidate begins to reduce the "FR must open the door first" phenomenon,
especially on the FR5 / PD8 subset.
```

This reduction is not yet proven for the entire FR5 band.
But it is already visible on the most suspicious slice.

## 8. Limits

Current limits remain:

- `PD5` shoulder is still weakly constrained
- this note does not prove fully neutral posture substrate recovery
- this note does not prove ODW has become the sole or complete posture-direction authority
- this note does not justify baseline replacement

So the result is bounded:

- good enough to support the reallocation hypothesis
- not yet broad enough to close the thread

## 9. Current Engineering Judgment

The strongest current candidate does more than weaken FR.

It begins to:

- reduce FR5 wedge-gate overreach
- preserve legitimate stabilization outside the target slice
- make ODW quality differences more readable
- make PD and MB conditional effects more separable
- reduce the appearance that FR must first authorize geometry before later mechanisms can express

That is why Engineering currently interprets it as:

```text
an authority-space release probe
```

rather than only:

```text
an FR suppression probe
```

## 10. Assumptions

- The previously observed DOE near-determinism remains sufficient reason to treat `SP01`, `SP09`, and `SP18` as adequate bounded confirmation seeds.
- The current strongest candidate remains a valid movement-local probe rather than a baseline correction.
- The batch is interpreted as a diagnostic validation set, not a replacement for later integration-gate validation.

## 11. PD5 Shoulder Trial

### 11.1 Trial scope

After the main batch, Engineering ran one bounded in-memory shoulder trial.

This trial did not modify repository code.

It temporarily widened the current strongest candidate's `PD` condition from:

```text
pd_norm > 0.5
```

to:

```text
pd_norm >= 0.5
```

So the trial tested whether the same `FR5` release logic could safely extend from the `PD8` subset into the `PD5` shoulder.

The trial kept the same core shape:

- strict pre-contact only
- `FR5` midband only
- same centroid-restoration target
- same `FR2` / `FR8` controls

Batch:

- `6` PD5 shoulder cells
- `2` PD8 sentinels
- `1` legitimate `PD2` sentinel
- `2` FR2 guardrails
- `1` healthy FR8 control
- `3` seed profiles

Total:

```text
12 cells x 2 variants x 3 seed profiles = 72 runs
```

### 11.2 High-level readout

`PD5 shoulder` overall:

- baseline:
  - `Win = 16.7%`
  - `WedgePresent = 16.7%`
  - `StructuralFragility = 83.3%`
  - `c_conn = 0.8557`
  - `collapse = 0.1443`
  - `FireEff = 0.2942`
  - `first_major_divergence_tick = 145.0`
- shoulder trial:
  - `Win = 33.3%`
  - `WedgePresent = 0.0%`
  - `StructuralFragility = 66.7%`
  - `c_conn = 0.8258`
  - `collapse = 0.1742`
  - `FireEff = 0.4854`
  - `first_major_divergence_tick = 205.2`

Interpretation:

- this is not a no-op
- the candidate begins to act on the `PD5` shoulder
- but the effect is mixed rather than uniformly healthy

### 11.3 PD5 shoulder cell pattern

Representative per-cell readout:

| Cell | Base Win% | Trial Win% | Base Wedge% | Trial Wedge% | Base Frag% | Trial Frag% | Base c_conn | Trial c_conn | Base Collapse | Trial Collapse | Base FireEff | Trial FireEff |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `FR5_MB2_PD5_ODW2` | 0 | 100 | 0 | 0 | 100 | 0 | 0.8278 | 0.9302 | 0.1722 | 0.0698 | 0.3161 | 0.5348 |
| `FR5_MB2_PD5_ODW8` | 0 | 0 | 0 | 0 | 0 | 0 | 0.9321 | 0.9483 | 0.0679 | 0.0517 | 0.3117 | 0.5102 |
| `FR5_MB5_PD5_ODW2` | 0 | 0 | 0 | 0 | 100 | 100 | 0.8048 | 0.8008 | 0.1952 | 0.1992 | 0.2660 | 0.4789 |
| `FR5_MB5_PD5_ODW8` | 100 | 100 | 0 | 0 | 100 | 100 | 0.8936 | 0.8941 | 0.1064 | 0.1059 | 0.2951 | 0.4789 |
| `FR5_MB8_PD5_ODW2` | 0 | 0 | 0 | 0 | 100 | 100 | 0.7932 | 0.6319 | 0.2068 | 0.3681 | 0.2585 | 0.4883 |
| `FR5_MB8_PD5_ODW8` | 0 | 0 | 100 | 0 | 100 | 100 | 0.8828 | 0.7498 | 0.1172 | 0.2502 | 0.3176 | 0.4213 |

### 11.4 PD5 shoulder interpretation

This shoulder trial shows a three-way split:

- `MB2`:
  - clear improvement
  - authority-space release looks plausible and healthy
- `MB5`:
  - mostly neutral in outcome and fragility
  - improved fire conversion but little structural change
- `MB8`:
  - wedge overreach does drop in the `ODW8` case
  - but structure degrades sharply
  - `c_conn` falls and `collapse` rises heavily

Engineering reading:

- `PD5` is not completely blocked behind FR preemption
- but the shoulder is not as cleanly releasable as the `PD8` slice
- the main risk appears to be that widening the gate to include `PD5` begins to destabilize the high-`MB` edge

### 11.5 Sentinel and control behavior

`PD8` sentinels remain strongly positive:

- `FR5_MB2_PD8_ODW8`
  - `Win 0 -> 100`
  - `Wedge 100 -> 0`
- `FR5_MB5_PD8_ODW8`
  - `Win 0 -> 100`
  - `Wedge 100 -> 0`

Legitimate `PD2` sentinel remains preserved:

- `FR5_MB8_PD2_ODW8`
  - unchanged

Controls remain preserved:

- `FR2_MB2_PD8_ODW8`
- `FR2_MB8_PD8_ODW8`
- `FR8_MB2_PD2_ODW8`

So the widened trial does not become a broad suppressor.
Its problem is narrower:

- it appears to overreach on the `PD5 + MB8` shoulder

### 11.6 Trial judgment

Engineering judgment:

```text
The current strongest candidate does show extension potential into the PD5 shoulder,
but not safely across the whole shoulder.
```

More specifically:

- `PD5` shoulder release appears plausible for `MB2`
- potentially tolerable for `MB5`
- not acceptable for `MB8` in the current widened form

So the current best reading is:

```text
the shoulder should not be opened wholesale by simply changing
pd_norm > 0.5
to
pd_norm >= 0.5
```

If the thread continues, the `PD5` shoulder should be treated as a separate bounded subproblem rather than as an automatic extension of the current strongest candidate.

## 12. PD5 Shoulder Refinement Trial

### 12.1 Trial purpose

Because the wholesale shoulder opening was too blunt, Engineering ran one further bounded in-memory refinement trial.

This trial compared three shoulder logics against baseline:

1. `current_strong`
   - existing strongest candidate
   - affects `PD8` only
2. `pd5_soft`
   - extends to `PD5`
   - but uses a softer midband reduction instead of the full anchor
3. `pd5_mb_le5`
   - extends to `PD5`
   - but only when `MB <= 5`
   - keeps the existing strong `PD8` behavior unchanged

This trial also did not modify repository code.

Batch:

- same `6` PD5 shoulder cells
- same `2` PD8 sentinels
- same legitimate `PD2` sentinel
- same `FR2` guardrails
- same healthy `FR8` control
- `3` seed profiles

Total:

```text
12 cells x 4 variants x 3 seed profiles = 144 runs
```

### 12.2 High-level comparison

`PD5 shoulder` overall:

- baseline:
  - `Win = 16.7%`
  - `WedgePresent = 16.7%`
  - `StructuralFragility = 83.3%`
  - `c_conn = 0.8557`
  - `collapse = 0.1443`
  - `FireEff = 0.2942`
  - `first_major_divergence_tick = 145.0`
- `current_strong`:
  - unchanged from baseline
- `pd5_soft`:
  - `Win = 16.7%`
  - `WedgePresent = 16.7%`
  - `StructuralFragility = 100.0%`
  - `c_conn = 0.8089`
  - `collapse = 0.1911`
  - `FireEff = 0.3819`
  - `first_major_divergence_tick = 185.7`
- `pd5_mb_le5`:
  - `Win = 33.3%`
  - `WedgePresent = 16.7%`
  - `StructuralFragility = 66.7%`
  - `c_conn = 0.8749`
  - `collapse = 0.1251`
  - `FireEff = 0.4298`
  - `first_major_divergence_tick = 207.8`

Interpretation:

- `pd5_soft` is not a good shoulder extension
- `pd5_mb_le5` is materially better and is the first shoulder variant that improves the shoulder while avoiding the known `MB8` failure mode

### 12.3 Sentinel and control check

All three refinement variants preserve the key non-shoulder anchors:

- `PD8` sentinels remain strongly positive under both `pd5_soft` and `pd5_mb_le5`
- legitimate `PD2` sentinel remains unchanged
- `FR2` guardrails remain unchanged
- healthy `FR8` control remains unchanged

This means the comparison is really about shoulder quality, not control failure.

### 12.4 Cell-level judgment

Most important `PD5` cell outcomes:

#### A. `pd5_soft`

This variant is not acceptable.

It introduces new instability without creating clean shoulder release:

- `FR5_MB2_PD5_ODW8`
  - `Win 0 -> 100`
  - but `Fragility 0 -> 100`
  - `c_conn 0.9321 -> 0.8703`
  - `collapse 0.0679 -> 0.1297`
- `FR5_MB5_PD5_ODW8`
  - `Win 100 -> 0`
- `FR5_MB8_PD5_ODW8`
  - remains bad and becomes structurally worse

Engineering reading:

- a softer shoulder reduction is not enough by itself
- it degrades quality while failing to produce a clean conditional release

#### B. `pd5_mb_le5`

This variant is materially more promising.

Representative cells:

- `FR5_MB2_PD5_ODW2`
  - `Win 0 -> 100`
  - `Fragility 100 -> 0`
  - `c_conn 0.8278 -> 0.9302`
  - `collapse 0.1722 -> 0.0698`
- `FR5_MB2_PD5_ODW8`
  - `Win 0 -> 0`
  - but quality still improves:
  - `c_conn 0.9321 -> 0.9483`
  - `collapse 0.0679 -> 0.0517`
- `FR5_MB5_PD5_ODW8`
  - preserves the legitimate winner:
  - `Win 100 -> 100`
  - `c_conn 0.8936 -> 0.8941`
  - `collapse 0.1064 -> 0.1059`
- `FR5_MB8_PD5_ODW2`
  - unchanged
- `FR5_MB8_PD5_ODW8`
  - unchanged

Engineering reading:

- restricting shoulder release to `MB <= 5` avoids the known `MB8` destabilization
- the shoulder begins to open where conditional release looks healthy
- the high-`MB` edge is left untouched instead of being made worse

### 12.5 Refinement judgment

Current bounded ranking for the `PD5` shoulder:

1. `pd5_mb_le5`
   - promising bounded shoulder extension
2. `current_strong`
   - safe, but leaves the shoulder unopened
3. `pd5_soft`
   - not acceptable

So the strongest updated reading is:

```text
If the thread continues into PD5,
the most defensible next shoulder candidate is not a broad PD5 opening,
but a conditional shoulder release limited to MB <= 5.
```

### 12.6 Updated engineering interpretation

This refinement strengthens the authority-space release hypothesis.

Why:

- it suggests the shoulder is not governed by PD alone
- the bad behavior is specifically concentrated at the `MB8` edge
- once that edge is excluded, the `PD5` shoulder begins to look more readable and less like a hidden extension of the FR-opened gate

That makes the next bounded question sharper:

```text
Can PD5 shoulder release be treated as a low-to-mid MB conditional extension,
while leaving the MB8 edge outside the current correction window.
```
