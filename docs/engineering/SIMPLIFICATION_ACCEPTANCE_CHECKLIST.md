# Simplification Acceptance Checklist

Status: Working engineering checklist  
Scope: cleanup / simplification turns, especially launcher / harness cleanup  
Authority: engineering acceptance aid, not canonical semantics authority

---

## 1. Purpose

This checklist exists to prevent additive indirection from being misreported as simplification.

It is especially intended for Phase A / A5 cleanup work in:

- `test_run/`
- launcher / harness entrypoints
- settings access plumbing
- report / viz handoff plumbing

---

## 2. Required Evidence Before Claiming Simplification

A cleanup turn should provide enough evidence to answer the following:

### A. Entrypoint Reduction
- Did the touched human-facing entrypoint become visibly smaller?
- If yes, which one?
- If no, simplification claim is weakened immediately.

### B. Interface Narrowing
- Did any public or launcher-facing interface become narrower?
- Did parameter passthrough decrease?
- Did a wide call become materially less wide?

### C. Indirection Count
- How many helper / wrapper / builder functions were added?
- How many were removed?
- Did call graph depth increase?

### D. Stdout Reduction
- Did default successful stdout become quieter?
- Were noisy narration prints removed?
- Was debug output moved behind opt-in behavior?

### E. Failure Behavior
- Did launcher-consumed settings become more fail-fast?
- Were silent fallback / continue behaviors removed rather than added?

### F. Scope Containment
- Was the cleanup limited to cleanup?
- Or did it silently drift into runtime / observer / doctrine redesign?

### G. Validation
- Was the appropriate regression gate used?
- Routine cleanup: 3-run anchor
- Major change: full 9-run matrix

---

## 3. Pass Criteria

A cleanup turn may be accepted as genuine simplification only if the answer is broadly “yes” to most of the following:

- The main touched entrypoint is visibly lighter
- Interface width is narrower or at least meaningfully cleaner
- New helper/wrapper growth does not outweigh actual reduction
- Default stdout is quieter or no noisier than before
- Fail-fast behavior improved for required launcher-consumed settings
- Reading burden is lower for a human reviewing the hot path
- No cross-layer scope creep occurred
- Appropriate regression validation was performed

---

## 4. Failure Indicators

Any of the following should trigger rejection or downgrade of the simplification claim unless explicitly justified and approved:

- Code was moved into more helpers, but human-facing weight did not go down
- New passthrough wrappers or builder layers were added
- Parameter transport remained equally wide, just redistributed
- Default stdout became noisier or remained unnecessarily verbose
- Silent fallback / warning-and-continue behavior was added or preserved for required launcher settings
- Cleanup opened runtime-core, observer-boundary, or doctrine-level topics without explicit authorization
- The result is more “formal” but not meaningfully easier to read or maintain

---

## 5. Classification Output

At review time, classify the result as one of:

### A. Accepted Simplification
Visible subtraction occurred and the checklist is satisfied.

### B. Partial Cleanup
Some local cleanup value exists, but visible subtraction is incomplete.

### C. Boundary Clarification Only
File/layer roles are clearer, but reading burden and weight did not materially improve.

### D. Refactor Without Accepted Simplification
Code was reorganized, but simplification claim is not accepted.

### E. Scope Drift
The change exceeded cleanup scope and should be reviewed as a different class of turn.

---

## 6. Special Note for `test_run/`

For `test_run/`, the default review bias should be strict.

Reason:

- this area already experienced repeated turns where boundary clarity improved
- but visible launcher weight, parameter passthrough, or stdout noise did not improve enough

Therefore, in `test_run/`, additive indirection must not be given the benefit of the doubt.

---

## 7. One-Line Standard

If a human cannot quickly see what became smaller, quieter, narrower, or simpler, the change should not be reported as successful simplification.
