# Minimal Hostile Penetration Cost Validation Preparation Note

Date: 2026-03-14  
Status: Validation preparation note  
Scope: Limited validation preparation only. No implementation authorization.

## 1. Purpose

This note prepares the smallest valid comparison frame for a future test-only prototype of:

```text
minimal hostile-side penetration cost / non-penetration bias
```

It does not add a new family now.
It does not authorize code changes.
It does not reopen Phase 1 DOE.

Its only purpose is to make the next implementation step small, auditable, and governance-compatible.

## 2. Assumptions

This preparation note assumes:

1. `hybrid_v2_r125_d035_p020` remains the current Phase 1 working reference.
2. `support_weighted_v3` remains stopped.
3. `IntermixSeverity` remains a diagnostic only, not an acceptance proxy.
4. the next prototype must stay test-only inside `test_run`.
5. the next prototype must use only two new parameters:
   - one scale parameter
   - one strength parameter

## 3. Proposed Future Prototype Identity

For future implementation, the cleanest provisional family name would be:

```text
penetration_cost_v1
```

Reason:

- it states the mechanism role directly
- it does not imply doctrine
- it does not imply personality
- it distinguishes the new family from `hybrid_v2`

This note does not require that exact name, but any future implementation should keep the same level of semantic restraint.

## 4. Future Target Files

If later authorized, the prototype should stay within:

- `test_run/test_run_v1_0.py`
- `test_run/test_run_v1_0.settings.json`

No frozen-layer edits.
No observer slot changes.
No firing geometry or turning changes.

## 5. Proposed Prototype Surface

The future prototype should expose only:

1. `hostile_penetration_cost_scale`
- local occupancy field radius relative to `min_unit_spacing`

2. `hostile_penetration_cost_strength`
- continuous rollback or damping strength applied to deeper hostile embedding

No third shaping parameter.
No support-aware input.
No force-ratio input.
No angle semantics.

## 6. Comparison Set

The first bounded comparison should include exactly three configs:

1. `off`
2. `hybrid_v2_r125_d035_p020`
3. `penetration_cost_v1` prototype

That is the smallest comparison set that still answers a useful engineering question:

```text
is the new minimal penetration-cost family meaningfully better than both no impedance and the current working reference?
```

## 7. Fixture Set

Use the same three-fixture discipline already established for Phase 1.

### A. Exception fixture

`exception_2to1_close`

- A size `200`
- B size `100`
- aspect `2.0 / 2.0`
- origins `[80, 80] / [120, 120]`
- close-contact

### B. Neutral close-contact fixture

`neutral_close`

- A size `100`
- B size `100`
- aspect `2.0 / 2.0`
- origins `[80, 80] / [120, 120]`

### C. Neutral long-range fixture

`neutral_long`

- A size `100`
- B size `100`
- aspect `2.0 / 2.0`
- origins `[10, 10] / [190, 190]`

Common conditions:

- all-5 personality
- `boundary_enabled = false`
- pre-TL substrate unchanged

## 8. Initial Parameter Discipline

The first prototype validation should not open a grid.

Recommended initial comparison:

- one prototype point only
- if needed, at most one follow-up adjustment round

That means:

- first run the single planned point
- inspect exception suppression and neutral safety
- only then decide whether one bounded parameter adjustment is justified

No large DOE before the first prototype point is reviewed.

## 9. Evaluation Signals

The future comparison should use:

### Primary diagnostics

- `hostile_intermix_severity`
- `hostile_deep_intermix_ratio`

### Safety diagnostics

- `FrontCurv diff`
- `C_W_PShare diff`
- `first_contact_tick`

### Human review requirement

Human animation review remains mandatory.

Interpretation rule:

- numerical improvement is not enough by itself
- visual geometry must also look more credible

## 10. Minimal Acceptance Frame

The next prototype should only be considered promising if it shows both:

1. exception improvement  
Better penetration suppression than `hybrid_v2` in the `2:1` close-contact exception.

2. neutral safety  
No obvious regression against `hybrid_v2` on:
- neutral close-contact
- neutral long-range

This note intentionally avoids setting new numeric thresholds.
Those should be inherited from the current Phase 1 discipline unless later revised.

## 11. Bottom Line

The next legal step is not implementation sprawl.

It is a tightly bounded future comparison with:

- one new minimal family
- two parameters only
- three fixtures only
- `off` and `hybrid_v2` as references

That is the smallest valid validation frame for the next hostile penetration prototype.
