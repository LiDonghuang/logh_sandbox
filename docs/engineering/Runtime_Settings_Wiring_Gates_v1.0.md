# LOGH Sandbox

## Runtime Settings Wiring Gates v1.0

Status: maintained engineering standard  
Scope: runtime / harness / test-only settings wiring discipline  
Authority: engineering development standard

---

## Purpose

This note defines the minimum wiring gates for any public runtime setting or
test-only setting that can affect:

- motion read
- formation behavior
- targeting behavior
- hold / terminal behavior
- Human-observed battle outcome

The purpose is simple:

- a setting is not "wired correctly" merely because the path exists
- a setting is not "safe" merely because code reads it somewhere
- if a setting can alter Human-observed behavior, incorrect wiring can directly
  contaminate Human judgment and Governance judgment

Therefore, settings wiring must be treated as a development gate, not as a
casual plumbing detail.

---

## Core Principle

For any public/runtime-facing or test-only setting:

**Path existence is not enough.**

The setting is accepted as correctly wired only when:

1. the configuration path exists
2. comments/reference documentation exist
3. scenario/runtime preparation validates and publishes an effective value
4. execution consumes the effective value consistently
5. Human-facing observation can confirm that the value actually took effect
6. explicit override smoke checks have passed

If any one of these is missing, the setting is not considered safely wired.

---

## Required Wiring Gates

### Gate 1. Config Path Gate

The setting must exist in the intended config surface.

Examples:

- layered runtime settings
- layered test-only settings
- visualization settings

The path must be explicit and readable.
No hidden environment-only ownership for normal review parameters.

### Gate 2. Documentation Gate

The setting must be recorded in:

- `settings.comments.json`
- `settings.reference.md`

for the active settings surface.

The description must say:

- what the setting means
- valid range / domain
- whether it is baseline/runtime or test-only/harness-only

### Gate 3. Validation Gate

The scenario/runtime-preparation layer must:

- read the setting explicitly
- validate it
- fail fast if invalid unless bounded normalization is part of the semantics
- publish an `*_effective` value where that pattern is already used

This prevents silent drift between raw config and runtime behavior.

### Gate 4. Single Effective Owner Gate

Execution code must consume the validated/effective setting consistently.

It must not silently split ownership between:

- config value
- old code default
- hidden fallback constant
- special-path override

If a code default remains necessary, it must be clearly bounded and must not
quietly disagree with the configured working default for the active line.

### Gate 5. Observation Gate

If a setting can change Human-observed motion or battle behavior, it must be
visible somewhere in at least one of:

- run summary
- debug payload
- HUD/debug overlay
- report/readout note

This does not mean every scalar needs permanent HUD presence.
It means Human and Engineering must have a practical way to verify that the
setting actually took effect.

### Gate 6. Override Smoke-Check Gate

Before a setting is treated as safely wired, it must pass explicit override
smoke checks.

Minimum expectation:

- run at least two materially different values
- confirm the override reaches the effective value
- confirm the runtime/debug/summary surface reflects the override

Recommended for bounded `[0, 1]` weights:

- low
- middle
- high

Example:

- `0.0 / 0.5 / 1.0`

The purpose is not full DOE.
The purpose is proving that the setting is not silently ignored, shadowed, or
partially bypassed.

---

## Human-Review Safety Rule

Any setting that materially affects Human review must not be treated as safely
wired until the override smoke-check gate passes.

Reason:

- a miswired setting can produce false Human observations
- false observations can then mislead design judgment
- this contaminates both Engineering and Governance review

So, for Human-critical settings:

**wiring failure is not a minor plumbing bug; it is a review-integrity bug**

---

## No-Silent-Fallback Interpretation

For settings wiring, the No Silent Fall Back rule applies strongly.

Not allowed:

- config says one thing while a hidden code default still wins on an active path
- one path uses the configured value while another path quietly uses the old default
- Human review proceeds without noticing the mismatch

Allowed:

- clearly bounded defaults for paths where the setting is genuinely absent
- only if the active settings surface has not claimed ownership already

---

## Review Checklist

Before a push that introduces or changes an active setting path, Engineering
should be able to answer:

1. Where is the setting defined?
2. Where is it documented?
3. Where is it validated?
4. What is the single effective owner?
5. Where can Human/Engineering see that it actually took effect?
6. What override smoke check was run?

If those answers are not concrete, the setting is not ready to be trusted.

---

## Current Motivation

This standard is being recorded because a recent active parameter path appeared
to be wired, but a conflicting code-side default remained in place.

Even though the observed behavior did not immediately show a catastrophic
difference, the wiring defect was serious because it could have contaminated
Human interpretation of battle behavior.

That class of error should not rely on luck or Human frustration to be found.

