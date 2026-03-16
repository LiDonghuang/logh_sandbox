# Neutral Mirrored DOE Outcome Interpretation Rule

Date: 2026-03-12
Status: Engineering interpretation note
Scope: Same-force, mirrored-geometry DOE interpretation only

## 1. Purpose

This note defines a restricted interpretation rule for personality-mechanism DOE runs performed under:

- equal initial force size
- mirrored starting geometry
- symmetric geographic placement
- neutral or mirrored opening protocol

It does not apply automatically to:

- unequal-force runs
- asymmetric deployment scenarios
- flank / rear-attack setups
- scenario-design tests where geometry asymmetry is intentional

## 2. Core principle

Under a same-force, mirrored-geometry DOE, end-state outcome alone should not be treated as primary evidence of personality-mechanism effectiveness.

Reason:

- recent neutral mirrored close-contact diagnostics showed that visible end-state divergence can still emerge even when:
  - personality vectors are numerically identical
  - initial deployment is mirrored
  - observer symmetry has been substantially corrected

Therefore:

```text
winner / remaining-units gap
is a conversion readout,
not a primary mechanism-existence readout.
```

## 3. Primary and secondary evidence

### 3.1 Primary evidence for personality-mechanism validation

Personality-mechanism validation should continue to rely primarily on mechanism-specific readouts such as:

- `FrontCurv`
- `C_W_SPhere`
- `c_conn`
- collapse-family signals
- `FireEff`
- event anchors
- alive trajectory shape
- divergence timing
- posture-family readout

### 3.2 Secondary evidence

End-state result should be read as a secondary conversion signal:

- whether an earlier geometric / structural difference eventually converted into durable battlefield advantage

This means:

- strong outcome alone is not enough
- and moderate outcome difference should not be over-read when low-level residual asymmetry is known to exist

## 4. Provisional neutral-noise threshold candidate

For same-force mirrored DOE only, a provisional neutral-noise threshold candidate is introduced:

```text
remaining-force gap < 10% of initial force
```

Interpretation:

- if each side starts with `N` units
- and final remaining-force gap is `< 0.10 * N`
- then that gap should not, by itself, be treated as decisive evidence of a personality-mechanism split

Example:

- initial `100 vs 100`
- final `13 vs 0`

This is visually large enough to matter, but under the current low-level asymmetry findings it should still be interpreted cautiously:

- not as a clean mechanism verdict by itself
- only in combination with trajectory and mechanism-specific signals

## 5. Restriction on use

This rule is restricted to mirrored DOE interpretation and should not be generalized outside that context.

It should not be used to suppress genuine scenario-level outcomes in:

- intentionally asymmetric openings
- operational scenario tests
- doctrine stress tests

## 6. Current engineering judgment

Engineering judgment is:

- the principle is sound
- the exact `10%` value should be treated as provisional
- future neutral mirrored baseline work should help calibrate whether this threshold remains appropriate

Until such calibration is improved, this note should be applied as:

```text
a caution rule for outcome interpretation,
not a hard law of battle evaluation.
```

## 7. Practical rule

For same-force mirrored personality DOE:

1. read mechanism-specific indicators first
2. read alive-trajectory divergence second
3. read final outcome last
4. avoid declaring a clean personality winner purely from end-state gap unless the broader mechanism picture also agrees

