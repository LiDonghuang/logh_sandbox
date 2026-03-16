# Governance Report - Post DOE Stop Work Summary

Date: 2026-03-12
Status: Engineering report to Governance
Thread: `analysis/engineering_reports/developments/20260311/phase_fr_authority_audit`

## 1. Scope of this report

This report covers the work completed after the point where the current bounded-correction line stopped expanding DOE.

It summarizes:

- what was implemented
- what was learned
- which candidate directions were closed
- what changed in `test_run`
- what interpretation constraints now apply before further personality-mechanism validation

This is not a baseline-replacement request.

## 2. Bounded-correction line status

The bounded `FR` correction search was closed as a search line.

Key conclusion:

- the tested continuous candidate family did not yield a promotable bounded correction candidate
- therefore the current bounded-correction search was stopped rather than expanded

Important distinction:

- this does **not** invalidate the `FR authority audit`
- it invalidates the specific correction family that was tested

## 3. Major engineering actions completed after DOE stop

### 3.1 Discrete probe retirement

- discrete `FR` correction probes were removed from active `test_run`
- they remain diagnostic history only

### 3.2 Historical analysis protection rule

Engineering and human direction converged on a new handling rule:

- historical `analysis` should not be rewritten to match later mechanism reality
- major later changes should be recorded independently

This is now reflected in:

- `AGENTS.md`
- `docs/architecture/major_changes/Major_Change_Record_20260312.md`

### 3.3 `test_run` initial formation interface cleanup

`test_run` was migrated to side-specific formation keys:

- `initial_fleet_a_size`
- `initial_fleet_b_size`
- `initial_fleet_a_aspect_ratio`
- `initial_fleet_b_aspect_ratio`
- `initial_fleet_a_origin_xy`
- `initial_fleet_b_origin_xy`
- `initial_fleet_a_facing_angle_deg`
- `initial_fleet_b_facing_angle_deg`

And the shared legacy `test_run` keys were removed:

- `initial_fleet_size`
- `initial_fleet_aspect_ratio`

This cleanup was intentionally restricted to `test_run`.
Historical `analysis` paths were not back-edited.

### 3.4 Initial formation geometry corrections

The following were implemented in `test_run`:

- final partial row centering
- full-formation center-anchor semantics for `origin_xy`
- side-specific aspect ratio support
- side-specific facing support

This materially reduced geometry misinterpretation caused by the old placement logic.

### 3.5 Observer symmetry corrections

Observer geometry metrics were corrected to use fleet-local enemy-facing axes instead of a single global A->B axis.

This materially changed the interpretation boundary for:

- `FrontCurv`
- `C_W_SPhere`
- `posture_persistence_time`

### 3.6 Harness-side movement symmetry mitigation

A test-only harness-side `symmetric_movement_sync_enabled` path was added to reduce cross-fleet sequential-update bias without editing frozen runtime.

This remains:

- `test_run` only
- diagnostic / mitigation only
- not a baseline replacement

## 4. Neutral mirrored close-contact diagnostic work

A neutral mirrored close-contact diagnostic window was established using:

- equal-force setup
- mirrored deployment
- identical all-5 personality vectors

Purpose:

- isolate low-level asymmetry before attributing differences to personality mechanisms

### 4.1 What was learned

Engineering now judges:

- the early large `FrontCurv` mismatch was substantially observer-induced and is now largely corrected
- `C_W_SPhere` pre-contact asymmetry is now much lower
- the strongest remaining asymmetry appears mainly in the post-contact phase

### 4.2 What was not confirmed

The post-contact audit did **not** support a simple target-tie explanation.

Specifically:

- fleet-level nearest-enemy tie behavior was not sufficient to explain the residual asymmetry
- per-attacker combat best-target ties were effectively absent in the audited window

So the remaining post-contact asymmetry should not currently be described as a simple target-tie bug.

### 4.3 Failed extra probes

Several additional shallow test-only probes were tried and rejected:

- continuous weighted center-vs-wing observer share
- combat-time geometric reordering of `fleet.unit_ids`
- symmetric two-pass combat merge

These did not produce a clean improvement and were not promoted into code.

## 5. Current interpretation consequence for personality DOE

A new interpretation constraint now follows from the symmetry findings:

Under same-force mirrored DOE, end-state outcome should not be treated as primary personality-mechanism evidence.

Engineering has written this as a dedicated note:

- `analysis/engineering_reports/developments/20260311/phase_fr_authority_audit/neutral_mirrored_doe_outcome_interpretation_rule_20260312.md`

Working engineering position:

- mechanism validation should still rely mainly on mechanism-specific indicators
- end-state gap should be treated as conversion evidence, not primary existence evidence
- for mirrored same-force DOE, a provisional neutral-noise threshold candidate such as `<10% of initial force` is reasonable as a caution rule, not yet as a hard law

## 6. Current engineering judgment

At this stage, engineering judgment is:

1. the `FR` audit thread has produced valid structural findings
2. the bounded correction search line has been cleanly stopped
3. several low-level geometry/observer/interface defects have been corrected in `test_run`
4. low-level residual asymmetry still exists, mainly after contact
5. further personality-mechanism validation must be interpreted more cautiously until post-contact asymmetry is better understood

## 7. Requests / direction needed from Governance

Engineering requests governance guidance on three points.

### 7.1 Outcome interpretation rule

Does Governance accept the restricted interpretation rule that:

- under same-force mirrored DOE
- end-state outcome should not be treated as decisive primary evidence
- and should instead be subordinated to mechanism-specific indicators and trajectory structure

### 7.2 Provisional neutral-noise threshold framing

Does Governance accept using a provisional threshold candidate such as:

```text
remaining-force gap < 10% of initial force
```

as a caution boundary for mirrored DOE only?

Engineering is **not** asking to canonize the exact number yet.
Only to allow it as a bounded interpretation aid.

### 7.3 Sequencing

Does Governance agree that the next engineering priority should remain:

- post-contact low-level symmetry audit

rather than reopening broad personality DOE immediately?

## 8. Bottom line

The work since DOE stop has not been idle cleanup.

It has established:

- cleaner `test_run` formation interfaces
- corrected observer symmetry
- reduced pre-contact symmetry artifacts
- a clearer separation between low-level asymmetry and personality evidence
- a new rule for preserving historical `analysis` while independently recording major later changes

Engineering judgment is that this was necessary groundwork.
Without it, later personality-mechanism readouts would continue to risk over-interpreting low-level artifacts as semantic effects.

