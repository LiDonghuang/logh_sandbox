# Hostile Spacing and Coherence Co-Resolution Framing Note

Date: 2026-03-14  
Status: Engineering note  
Scope: Mechanism framing only. No implementation authorization.

## 1. Purpose

This note defines the next mechanism framing after the clear failure of `hostile_spacing_floor_v2`.

This is not:

- a baseline proposal
- a DOE plan
- an implementation request

It is only a new bounded mechanism framing note.

## 2. Current Diagnosis

`hostile_spacing_floor_v2` failed because it improved overlap partly by resolving multiple hostile spacing conflicts **without preserving same-fleet spacing/coherence at the same effective layer**.

So the key failure is no longer:

```text
the hostile-side spacing idea is wrong
```

It is:

```text
multi-hostile local spacing resolution cannot stand alone;
it must be co-resolved with same-fleet spacing/coherence
at the same effective layer
```

## 3. Proposed Direction

The next direction should be framed as:

```text
local spacing-and-coherence co-resolution
```

The core idea is:

- keep hostile-side spacing conflict as a same-layer local constraint source
- keep same-fleet spacing/coherence as a same-layer local constraint source
- resolve both together on the tentative local displacement

This is meant to prevent the previous failure mode:

```text
reduce overlap by tearing fleet geometry apart
```

## 4. What This Tries to Preserve

The next mechanism should attempt to preserve two facts together:

1. hostile-side spacing is not air
2. same-fleet spacing/coherence does not become disposable under contact

So the next question is no longer only:

```text
how much of this movement deepens hostile spacing violation?
```

It becomes:

```text
how much of this movement can be kept
while reducing hostile-side spacing violation
without destroying same-fleet spacing/coherence?
```

## 5. Why This Is Still Low-Semantic

This direction can still remain inside current phase boundaries, because it does not require:

- support-aware semantics
- force-ratio logic
- breakthrough-worthiness logic
- doctrine-like behavior selection
- target-value logic

It still only works with:

- local hostile spacing conflict
- local same-fleet spacing/coherence conflict
- tentative displacement correction

So it can remain:

- continuous
- local
- symmetric
- low-semantic
- test-only

## 6. Why This Is Not Yet a Movement Rewrite

This framing still operates only on the local tentative displacement after the current movement intent has been formed.

It does not redefine:

- fleet-level closing logic
- target substrate
- posture semantics
- higher-layer movement ownership

So the intended scope remains:

```text
local same-layer displacement correction,
not broader movement-core rewrite
```

## 7. One-Line Conclusion

```text
the next viable direction is not stronger hostile spacing alone, but same-layer local co-resolution of hostile-side spacing and same-fleet spacing/coherence, so overlap is not reduced by tearing fleets apart.
```
