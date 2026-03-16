# Contact Impedance Bounded Design Note

Date: 2026-03-13  
Status: Engineering note  
Scope: Low-level movement/contact interpretation only. No implementation authorization.

## 1. Problem Statement

Recent mirrored and close-contact animation review suggests that units from opposing fleets can intermix too freely once contact begins. The issue is most visible in "face-to-face" runs, where hostile units appear to pass through one another with limited local resistance before later geometric correction.

This note clarifies the current low-level structure and why the existing separation logic is not sufficient to produce strong contact impedance.

## 2. Current Structure

The current low-level behavior is not a single separation mechanism. It has two distinct layers.

### 2.1 Same-fleet steering separation

In `runtime/engine_skeleton.py:733`, `separation_accumulator` is computed only within the current fleet's `alive_unit_ids`.

Relevant points:

- `runtime/engine_skeleton.py:733`
- `runtime/engine_skeleton.py:752`
- `runtime/engine_skeleton.py:753`
- `runtime/engine_skeleton.py:754`
- `runtime/engine_skeleton.py:755`
- `runtime/engine_skeleton.py:928`
- `runtime/engine_skeleton.py:992`

Interpretation:

- this layer tells a fleet how not to crowd itself
- it does **not** create hostile-side steering repulsion
- a unit can still steer directly into enemy space if forward/targeting terms dominate

### 2.2 Global post-movement projection

After tentative movement, the runtime performs a single-pass global projection across all alive units.

Relevant points:

- `runtime/engine_skeleton.py:1168`
- `runtime/engine_skeleton.py:1214`
- `runtime/engine_skeleton.py:1237`

Interpretation:

- this layer corrects illegal overlap after movement has already been proposed
- it does act across fleets
- but it is geometric correction, not pre-emptive contact resistance

## 3. Why Intermixing Still Happens

The key issue is not "no separation exists." The issue is that the system currently lacks a genuine **inter-fleet contact impedance** layer.

Current behavior is effectively:

1. steer while avoiding friendly crowding
2. continue pushing toward enemy-facing objectives
3. only afterward, project apart if overlap violates minimum spacing

Consequences:

- enemy contact does not strongly resist forward intent at the steering stage
- opposing fronts can penetrate into one another before correction
- projection then resolves overlap geometrically, but too late to create a "holding line" feel
- the visual result is intermixing / weaving / pass-through-then-correction

## 4. Engineering Interpretation

This means the present weakness is more accurately described as:

```text
missing contact impedance
```

not simply:

```text
weak separation
```

That distinction matters because increasing same-fleet separation alone would not solve the observed cross-fleet intermixing.

## 5. Candidate Directions

This note does not recommend implementation yet, but the candidate space is already clearer.

### 5.1 Inter-fleet steering repulsion

Add a hostile-side local repulsion or exclusion term before final movement writeback.

Potential role:

- reduce direct cross-fleet penetration
- create earlier local resistance at contact entry

Main risk:

- can easily become over-repulsive and erase legitimate local penetration

### 5.2 Contact-phase forward damping

Apply a local reduction to forward drive once hostile proximity or engaged-state crosses a threshold.

Potential role:

- preserve forward intent before contact
- reduce "ghosting through" once contact has already formed

Main risk:

- can become too phase-hard if implemented as a discrete switch

### 5.3 Engaged non-penetration bias

Bias engaged units toward non-penetration geometry while preserving lateral sliding / local rearrangement.

Potential role:

- better front holding without requiring strong enemy repulsion everywhere

Main risk:

- can become sticky and suppress natural local flow

## 6. Design Guidance

Given current project direction, any future work here should prefer:

- continuous influence
- path-local shaping
- minimal new semantics

and should avoid:

- hard tactical mode switching
- discrete contact-state doctrine
- personality-driven contact locking

This issue belongs to low-level substrate quality, not to personality mechanism activation.

## 7. Current Recommendation

Do not treat this as a "tune alpha_sep" problem.

The more defensible next step is:

1. keep the current diagnosis explicit:
   - same-fleet separation exists
   - global projection exists
   - inter-fleet contact impedance is missing
2. if implementation is later approved, test one bounded candidate from the contact-impedance family rather than simply increasing same-fleet separation

## 8. Bottom Line

The observed hostile intermixing in close-contact runs is consistent with the present low-level structure.

The system currently has:

- friendly-side steering separation
- global overlap projection

but does **not** yet have a true hostile contact-impedance layer.

That is the most plausible low-level explanation for why opposing units can appear to pass into one another too easily before later correction.
