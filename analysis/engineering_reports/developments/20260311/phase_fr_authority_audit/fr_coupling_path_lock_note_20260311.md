# FR Coupling Path Lock Note

Date: 2026-03-11
Thread: `analysis/engineering_reports/developments/20260311/phase_fr_authority_audit`
Status: bounded engineering note

Question:

```text
Which concrete runtime path is most likely carrying FR's over-strong emergence-threshold authority,
and which paths are better understood as secondary persistence or carry-through amplifiers.
```

## 1. Scope

This note does not introduce a new mechanism.

It only locks the most likely coupling path using:

- code inspection of `runtime/engine_skeleton.py`
- code inspection of `test_run/test_run_v1_0.py`
- existing `FR5` strongest-candidate validation evidence

No frozen-layer modification is proposed here.

## 2. Key Code Facts

### 2.1 First active FR read on the `v3a` path

In `runtime/engine_skeleton.py` the first active `FR` read on the `v3a` movement path is:

- `runtime/engine_skeleton.py:757`

```text
kappa = fleet.parameters.normalized()["formation_rigidity"]
```

That `kappa` immediately feeds the active centroid-restoration term:

- `runtime/engine_skeleton.py:912`
- `runtime/engine_skeleton.py:913`

```text
cohesion_x = (kappa * cohesion_gain * cohesion_scale) * cohesion_dir[0]
cohesion_y = (kappa * cohesion_gain * cohesion_scale) * cohesion_dir[1]
```

This is the direct FR-to-geometry path currently under audit.

### 2.2 Later FR-coupled paths in the same movement tick

There are later FR-coupled reads, but they sit downstream:

- non-`v3a` restoration fallback:
  - `runtime/engine_skeleton.py:991`
  - `runtime/engine_skeleton.py:997`
  - `runtime/engine_skeleton.py:1002`
  - `runtime/engine_skeleton.py:1003`
- FSR contraction scaling:
  - `runtime/engine_skeleton.py:1123`
  - `runtime/engine_skeleton.py:1124`

These are real FR carriers, but they are not the earliest active `v3a` geometry entry point.

## 3. Why the Test Harness Is Informative

The strongest current probe is implemented through:

- `test_run/test_run_v1_0.py:_FirstNormalizedFormationRigidityProxy`
- `test_run/test_run_v1_0.py:integrate_movement()`

Important harness behavior:

1. `_FirstNormalizedFormationRigidityProxy.normalized()` overrides only the first `normalized()["formation_rigidity"]` read.
2. During probe execution, `integrate_movement()` temporarily rewrites the experiment label to `exp_precontact_centroid_probe`.
3. Fleet parameters are restored after movement, so the probe is movement-local and tick-local.

Engineering interpretation:

- the probe is designed to hit the first FR read on the active movement path
- in practice, that means the centroid-restoration `kappa` path is what gets modified first
- later FR uses, including FSR, are not the primary target of the strongest probe

This makes the current strongest candidate useful for path locking, not just for threshold testing.

## 4. Path Lock Judgment

### 4.1 Primary suspect

Primary suspect:

```text
pre-contact segment of the active v3a centroid-restoration path
```

Reason:

- it is the earliest active FR geometry entry point
- it acts before later posture and conversion families have fully expressed
- bounded `FR5` probes that act only on this path already produce large changes in outcome

Most important evidence:

- strongest candidate only alters the pre-contact / midband / PD-high subset on this path
- yet it still flips the key `FR5/PD8` cells from over-strong gate behavior to much cleaner readouts

Representative evidence from the bounded validation:

- `FR5_MB2_PD8_ODW8`
  - `Wedge 100% -> 0%`
  - `Win 0% -> 100%`
- `FR5_MB5_PD8_ODW8`
  - `Wedge 100% -> 0%`
  - `Win 0% -> 100%`

This is too strong to explain as a tertiary downstream effect.

### 4.2 Secondary suspect

Secondary suspect:

```text
always-on persistence carried by the same centroid-restoration path after the initial pre-contact phase
```

Reason:

- the same centroid term is continuously present, not only at emergence onset
- therefore it may still help carry forward geometry that was initially privileged upstream

But current engineering reading is:

- it is more likely a persistence amplifier than the root source of threshold overreach

Why:

- pre-contact-only intervention already changes the key `FR5` cases strongly
- this suggests later persistence is helping maintain a geometry choice that was already privileged earlier
- it does not look like the first place where the choice is made

### 4.3 Tertiary suspect

Tertiary suspect:

```text
FR-coupled FSR carry-through
```

Reason:

- FSR is clearly FR-coupled
- but the strongest current candidate does not directly alter the FSR read
- despite that, major `FR5` wedge-gate changes already appear

Engineering reading:

- FSR is better understood as secondary carry-through amplification
- not as the main root-cause gate path

## 5. Practical Lock Result

Current path ranking:

1. `Primary`
   - pre-contact active `v3a` centroid-restoration FR path
2. `Secondary`
   - always-on persistence on the same path after emergence onset
3. `Tertiary`
   - FSR-based FR carry-through amplifier

This means the thread should continue to interpret current strongest-candidate behavior primarily as evidence about:

```text
the early centroid-restoration path
```

not as evidence that FSR is the main root cause.

## 6. Root-Cause Reading

Under the current governance framing, the most plausible root-cause statement is:

```text
FR preempts geometry authority chiefly by entering early through the active centroid-restoration path,
thereby preconditioning which protrusions survive long enough to become later readable geometry.
```

Then:

- always-on persistence helps preserve that early advantage
- FSR helps carry some of it through later

But the preemption appears to begin earlier than those later amplifiers.

## 7. Recommended Next Use of This Lock

This path lock supports the next validation question:

```text
When the pre-contact centroid-restoration overreach is selectively reduced at FR5,
do ODW, PD, and MB become more readable as themselves,
rather than continuing to speak through an FR-opened gate.
```

That is the right question for the next `FR5`-centered validation note.

## 8. Assumptions

- The existing strongest probe is accepted as a valid movement-local probe rather than a baseline correction.
- The first overridden `normalized()["formation_rigidity"]` read is treated as the relevant early centroid-restoration read on the active `v3a` path.
- The prior DOE determinism result remains a valid reason to rely on bounded paired evidence rather than large repeated seed expansion.
