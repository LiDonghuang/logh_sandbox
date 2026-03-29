# Step 3 3D Two-Layer Spacing Implementation-Prep Discussion Note

- Engine Version: `dev_v2.0`
- Modified Layer: `analysis / implementation-prep discussion only`
- Affected Parameters: none in committed runtime
- New Variables Introduced: none
- Cross-Dimension Coupling: clarifies a possible future spacing split without opening implementation
- Mapping Impact: none
- Governance Impact: advances the two-layer spacing line from concept opening into bounded implementation-prep discussion
- Backward Compatible: yes
- Summary: discusses the smallest meaningful future distinction between `expected/reference spacing` and `low-level physical minimum spacing`, suggests current ownership candidates, and states what evidence would still be needed before any implementation opening could be recommended

## Purpose

This note follows the accepted two-layer spacing concept opening.

Its purpose is not to implement a new mechanism.

Its purpose is to define, as narrowly as possible:

- what the future distinction would mean if later implemented
- which layer each spacing role most likely belongs to
- what still blocks implementation opening

## 1. Smallest Meaningful Distinction

If the line later advances, the smallest meaningful distinction appears to be:

### A. Expected / reference spacing

- the intended spacing of reference / expected formation slots
- the spacing that restore logic should read against when judging whether the formation is stretched or compressed relative to its intended reference geometry

### B. Low-level physical minimum spacing

- the physical non-overlap floor used by local separation and projection
- the spacing below which runtime-local spacing protection should actively intervene

That is the smallest clean split currently visible in repo language.

Anything larger than this risks over-designing the line too early.

## 2. Best Current Ownership Candidates

### A. Expected / reference spacing

Best current ownership candidate:

- formation-reference / restore-policy boundary

Reason:

- it belongs to intended reference geometry
- it should remain slot-relative and geometry-emergent rather than becoming a collision control or viewer attribute

### B. Low-level physical minimum spacing

Best current ownership candidate:

- movement runtime / low-level physical layer

Reason:

- it is used by local separation and projection protection
- it behaves like a physical floor, not like a reference-geometry statement

## 3. What Should Remain Outside This Line

Even if this line later advances, the following should remain outside it:

- legality redesign
- viewer ownership
- geometry hardcoding / rectangle locking
- doctrine / personality recoupling
- mapping redesign

The current evidence still points to a narrow spacing/restore/runtime discussion, not a broader cross-layer rewrite.

## 4. Minimal Evidence Still Needed Before Implementation Opening

Before any implementation opening could be recommended, the minimum remaining evidence should include:

1. at least one more bounded discriminating probe where spacing roles are decoupled one at a time
2. human-readable evidence showing the effect directly, not only aggregate metrics
3. a bounded read on whether the decoupling result remains stable under both:
   - neutral-transit fixture path
   - maintained battle-path review context
4. explicit proof that a future split would not silently hardcode formation geometry

## 5. Current Recommendation on the Next Step

At the current evidence level, the next correct step still reads as:

- implementation-prep hardening discussion

not:

- direct implementation authorization

and not:

- a return to concept-only ambiguity

So the line has legitimately advanced, but it has not yet crossed into runtime rollout readiness.

## Bottom Line

The current best bounded recommendation is:

- keep two-layer spacing open in implementation-prep discussion
- keep implementation closed
- require one more bounded evidence step before recommending implementation authorization
