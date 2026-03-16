# FR Authority Audit Note

Date: 2026-03-11
Thread: `analysis/engineering_reports/developments/20260311/phase_fr_authority_audit`
Question:

```text
Is FR currently acting only as a deformation stabilizer,
or has it become an unintended wedge-emergence gate?
```

Working governance target:

```text
FR = deformation stabilizer
```

Not:

```text
FR = direct geometry generator
```

## 1. Scope

This note is a code-level authority audit only.

- No runtime coefficient changes are made here.
- No semantic reinterpretation is authorized here.
- This note only identifies where `formation_rigidity` enters runtime control and what those terms appear to do.

Primary files reviewed:

- `runtime/engine_skeleton.py`
- `runtime/runtime_v0_1.py`

## 2. Normalization Reminder

`formation_rigidity` is normalized from canonical `1..9` to `0..1` in `runtime/runtime_v0_1.py:37`.

So in practical terms:

- `FR=2 -> 0.125`
- `FR=5 -> 0.500`
- `FR=8 -> 0.875`

This means a high/low FR comparison is not a tiny perturbation. It is a strong change in every runtime term that multiplies normalized FR.

## 3. FR-Coupled Runtime Terms

### 3.1 Cohesion v1 debug carry-through

Location:

- `runtime/engine_skeleton.py:420`
- `runtime/engine_skeleton.py:422`

Code role:

- updates legacy/debug `cohesion_v1` by
  - `+ (kappa * 0.01)`
  - `- ((1.0 - kappa) * 0.005)`

Likely authority classification:

- `shape persistence`: low
- `shape emergence`: none direct
- `contact-phase carry-through`: conditional / debug-only

Interpretation:

- This term does not directly drive geometry.
- It changes the fleet-level cohesion scalar used by the old debug decision path.
- It matters only if the runtime decision source is switched to `v1_debug` or the debug path is explicitly retained.
- So this is not the primary source of the current FR-over-authority concern.

### 3.2 V3A centroid restoration term

Location:

- `runtime/engine_skeleton.py:757`
- `runtime/engine_skeleton.py:912`
- `runtime/engine_skeleton.py:913`

Code role:

- computes `kappa = normalized()["formation_rigidity"]`
- applies FR directly to centroid-restoration:

```text
cohesion_x = (kappa * cohesion_gain * cohesion_scale) * cohesion_dir[0]
cohesion_y = (kappa * cohesion_gain * cohesion_scale) * cohesion_dir[1]
```

Likely authority classification:

- `shape persistence`: high
- `shape emergence`: medium to high
- `contact-phase carry-through`: high

Interpretation:

- This is the main active FR term on the current movement mainline.
- It acts every tick.
- It is not limited to post-contact stabilization.
- Because it continuously restores units toward the fleet centroid, it helps preserve any developing forward asymmetry instead of merely damping noise.
- In practice, that can convert an initially weak forward protrusion into a more coherent wedge-like front.

Governance relevance:

- This is the strongest candidate for FR leaking from "deformation resistance" into "geometry emergence authority".

### 3.3 Legacy / non-v3a cohesion restoration term

Location:

- `runtime/engine_skeleton.py:991`
- `runtime/engine_skeleton.py:997`
- `runtime/engine_skeleton.py:1002`
- `runtime/engine_skeleton.py:1003`

Code role:

- on the non-`v3a` path, FR also multiplies cohesion restoration directly

Likely authority classification:

- `shape persistence`: high
- `shape emergence`: medium
- `contact-phase carry-through`: high

Interpretation:

- This is structurally similar to the `v3a` FR term.
- It is not the current primary path for this thread if the movement mainline is pinned to `v3a`.
- Still, it confirms that FR authority is not isolated to one experimental branch; it exists in both movement paths.

### 3.4 FSR contraction scaling

Location:

- `runtime/engine_skeleton.py:1123`
- `runtime/engine_skeleton.py:1124`

Code role:

- FR amplifies fleet shape restoration:

```text
k_f = fsr_strength * (0.5 + (0.5 * kappa_f))
```

Likely authority classification:

- `shape persistence`: high
- `shape emergence`: medium
- `contact-phase carry-through`: medium

Interpretation:

- FSR is intended to preserve an equilibrium-scale formation envelope.
- But because FR increases FSR gain, higher FR not only keeps the fleet tighter; it also helps retain any already-forming front geometry.
- So FSR is likely a secondary FR-over-authority channel:
  - not the original source of a wedge
  - but a multiplier on how hard that wedge survives once it starts appearing

## 4. What FR Does Not Directly Control

From this audit, FR does not appear to be a direct explicit generator of:

- target-axis posture bias
- center-vs-wing pressure redistribution
- combat damage bias
- observer-only wedge classification logic

Those authorities live elsewhere.

So the current concern is not:

```text
FR explicitly says "make a wedge"
```

It is:

```text
FR multiplies restoration/contraction strongly enough
that it may be acting like a wedge-emergence gate in observed behavior.
```

## 5. Provisional Authority Judgment

Current provisional judgment:

### 5.1 Shape persistence authority

FR clearly has legitimate authority here.

- centroid restoration
- post-deformation regrouping
- FSR-assisted retention of compact structure

This matches governance intent.

### 5.2 Shape emergence authority

FR likely has too much authority here on the active runtime path.

Reason:

- the main `v3a` restoration term is active every tick, not only after deformation
- the gain difference between low and high FR is large because of `1..9 -> 0..1` normalization
- the same FR also amplifies FSR
- empirical evidence already showed wedge-like emergence appearing only at high FR under otherwise aggressive but low-ODW conditions

So the live suspicion is coherent:

```text
FR is not only preserving shape.
FR is helping decide whether wedge-like geometry appears at all.
```

### 5.3 Contact-phase carry-through

FR retains meaningful authority here.

- because centroid restoration persists into contact and pursuit phases
- because FSR acts after movement update

This part is not obviously a bug by itself.
The question is whether too much carry-through is arriving too early and therefore affecting emergence rather than only persistence.

## 6. Immediate DOE Implication

The next DOE should test this narrow hypothesis:

```text
If FR is reduced, does wedge-like geometry stop appearing,
while persistence/stability effects remain measurable?
```

That DOE should therefore distinguish:

- geometry appearance
- geometry stability
- geometry-to-attrition conversion

and should not rely on final winner alone.

## 7. Audit Conclusion

This audit does not support the claim that FR is a cleanly isolated "stabilizer only".

It supports a narrower but important concern:

```text
FR currently enters active runtime shape control through
multiple restoration/contraction channels,
and the main V3A centroid-restoration term is the strongest candidate
for unintended shape-emergence authority.
```

Therefore the next step is justified:

- bounded DOE support
- fixed seeds
- time-resolved alive-unit readouts
- interpretation centered on
  - `shape persistence`
  - versus `shape emergence`

