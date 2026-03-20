# Test Run A5 Follow-Up Governance Report (2026-03-20)

Status: governance follow-up request  
Scope: test_run harness cleanup / public interface normalization follow-up  
Branch state reviewed: `dev_v1.1` at pushed commit `61fb8ea`

## 1. Reason For This Follow-Up

The current pushed state includes multiple A5 cleanup rounds plus one approved `A5.1` public harness interface normalization round.

However, the human owner remains dissatisfied with the visible outcome.

Current human judgment:

- too many rounds have been spent for too little visible simplification
- the net maintainability gain is not convincing enough
- confidence in future cleanup efficiency is now low

This report is not asking governance to re-read summaries only.

It is asking governance to inspect the pushed repo paths directly and judge whether the current `test_run` state is an acceptable Phase A outcome or whether the cleanup approach needs correction.

## 2. What Engineering Actually Tried

Across the current thread, engineering attempted the following sequence:

1. launcher-only subtraction on `test_run_main.py`
2. stdout reduction and wrapper/passthrough removal
3. grouped settings preparation inside `test_run_main.py`
4. fixed `3-run` anchor regression workflow so routine validation no longer depends on ad hoc comparator rebuilding
5. approved `A5.1` normalization of `run_simulation(...)` public surface
6. removal of the short-lived typed grouped surface in favor of lighter grouped mappings

This means the approach did not stay stuck at one idea only.

It already moved through:

- local subtraction
- grouped config preparation
- public interface narrowing
- validation workflow stabilization

## 3. Visible Progress Achieved

The pushed repo state does include real progress:

- `test_run/test_run_main.py` is much smaller than the original thread baseline
- routine `3-run` anchor regression is now stable and reusable
- `run_simulation(...)` no longer exposes the old wide scalar public signature
- `test_run_main.py` no longer needs the previous wide scalar shuttle into `run_simulation(...)`

Relevant supporting records:

- `docs/test_run_a5_governance_request_20260320.md`
- `docs/test_run_public_interface_normalization_20260320.md`

## 4. Why Human Dissatisfaction Is Still Reasonable

Despite the progress above, the human dissatisfaction is understandable.

The main reasons are:

- too many iterations were required to get here
- a large share of the work improved boundary clarity more than it improved felt maintainability
- `test_run/test_run_experiments.py` still carries heavy execution/telemetry weight
- `test_run/test_run_main.py` is smaller than before, but still does not feel clean enough relative to the effort spent

In short:

- engineering can point to real changes
- but human-visible simplification still feels weaker than the round count would justify

That gap is the real governance issue.

## 5. Current Honest Classification

Current engineering classification remains:

- `Partial Cleanup`

It is **not** being reported as:

- `Accepted Simplification`

Reason:

- there is real subtraction and interface narrowing
- but the current `test_run` hot path still does not feel light enough to claim full simplification success

## 6. Main Structural Blocker Still Remaining

The remaining difficulty is no longer just “too many scalar args”.

The harder remaining problem is:

- `test_run/test_run_experiments.py` still combines execution, telemetry assembly, and several observer-side metric collection responsibilities in one heavy hot path

This creates a governance-relevant question:

- should Phase A continue trying to simplify this file by bounded subtraction only
- or should governance authorize a stronger structural split inside harness-only scope

Engineering has already spent several rounds trying to avoid premature structure growth.

The result is that some safe subtraction happened, but the remaining weight is now harder to remove without a more explicit governance stance on acceptable harness-only restructuring.

## 7. Validation State

The pushed state is at least stable under current routine gates:

- `python -m py_compile test_run/test_run_experiments.py test_run/test_run_main.py test_run/test_run_v1_0.py test_run/test_run_anchor_regression.py`
- `python test_run/test_run_anchor_regression.py`

Current anchor result:

```text
[off] ok
[hybrid_v2] ok
[intent_unified_spacing_v1] ok
mismatch_count=0
```

So the concern is not “the harness is currently broken”.

The concern is:

- the cleanup efficiency and simplification payoff are not convincing enough

## 8. Paths Governance Should Inspect Directly

### Rules / discipline

- `AGENTS.md`
- `test_run/AGENTS.md`
- `docs/engineering/SIMPLIFICATION_ACCEPTANCE_CHECKLIST.md`

### Repo orientation

- `repo_context.md`
- `system_map.md`

### Current A5 records

- `docs/test_run_a5_governance_request_20260320.md`
- `docs/test_run_public_interface_normalization_20260320.md`
- `docs/test_run_governance_followup_20260320.md`

### Core files under dispute

- `test_run/test_run_main.py`
- `test_run/test_run_experiments.py`
- `test_run/test_run_v1_0.py`
- `test_run/settings_accessor.py`
- `test_run/test_run_anchor_regression.py`

### Settings / structure reference

- `test_run/test_run_v1_0.settings.json`
- `test_run/test_run_v1_0.runtime.settings.json`
- `test_run/test_run_v1_0.testonly.settings.json`
- `test_run/test_run_v1_0.settings.comments.json`

### De-scoped historical temporary scripts

These are no longer considered a maintained compatibility target:

- `analysis/engineering_reports/developments/...`

Governance may inspect them historically if useful, but engineering is no longer treating them as an active constraint on `test_run` cleanup.

## 9. Specific Governance Questions

Engineering requests a concrete governance judgment on the following:

1. Is the current pushed state an acceptable `Phase A / A5` stopping point for now, or not?
2. If not, should the next round remain subtraction-only, or is a stronger harness-only structural split now authorized?
3. If a stronger split is authorized, which boundary is acceptable:
   - execution vs telemetry collection
   - observer metric assembly vs battle execution
   - launcher snapshot/report assembly vs runtime-facing orchestration
4. What evidence threshold should count as enough visible gain before governance will accept future A5 progress as meaningful?

## 10. Bottom Line

Engineering can no longer honestly claim that more rounds of the same local cleanup style are obviously enough.

The pushed repo state is better than before.
But the human dissatisfaction is justified.

Governance should inspect the repo paths above directly and decide whether:

- the current result is acceptable for Phase A,
- or a sharper harness-only restructuring mandate is now required.
