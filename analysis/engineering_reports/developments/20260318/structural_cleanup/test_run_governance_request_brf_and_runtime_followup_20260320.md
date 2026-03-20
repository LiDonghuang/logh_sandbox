# Test Run Governance Request: BRF Simplification / Core Helper Exit / Runtime Freeze Clarification (2026-03-20)

Status: governance request  
Scope: `test_run` structural cleanup follow-up / battle report simplification / runtime frozen-layer clarification  
Classification: request only / non-runtime-semantic / non-canonical

## 1. Reason For This Request

This request is being submitted after several `Phase A` cleanup and reset rounds.

Real progress has been made, but the current state still leaves two unresolved questions:

- how far `battle_report_builder.py` should continue to be simplified while remaining attached to the maintained launcher path
- whether the next cleanup frontier may open runtime-side files such as `runtime/engine_skeleton.py`, which is currently frozen by repo rules

This document does not claim a new cleanup success.

It requests governance direction before further structural work.

## 2. Current Repo Facts

The current factual state is:

- `test_run/test_run_entry.py` is now the maintained launcher ground truth for routine run, daily animation path, and video-export path
- `.vscode/launch.json` points maintained daily configs to `test_run/test_run_entry.py`
- `test_run/test_run_v1_0_viz.py` remains the renderer; it has not been rewritten in the launcher reset rounds
- `test_run/test_run_main.py` has been physically deleted and is no longer part of the maintained path
- `test_run/battle_report_builder.py` has been reattached to the maintained launcher path through `test_run/test_run_entry.py`
- `test_run/brf_narrative_messages.py` is currently unchanged by request
- `test_run/test_run_v1_0.py` is no longer the daily launcher, but it is still a maintained hot-path helper host

Current hot-path dependency evidence:

- `test_run/test_run_entry.py` imports `test_run/test_run_v1_0.py` as `core`
- `test_run/test_run_scenario.py` imports `test_run/test_run_v1_0.py` as `core`

Current file-weight snapshot:

- `test_run/battle_report_builder.py`: `1322` lines
- `test_run/test_run_v1_0.py`: `1530` lines
- `runtime/engine_skeleton.py`: `2496` lines

## 3. What Engineering Has Actually Done Across Recent Rounds

Recent work has not stayed at the level of one small local cleanup.

Across the recent rounds, engineering completed the following:

1. stabilized the routine `3-run` anchor path so it no longer depends on ad hoc comparator rebuilding
2. normalized the maintained launcher path around `test_run/test_run_entry.py`
3. kept `test_run/test_run_v1_0_viz.py` as the renderer instead of duplicating or rewriting visual logic
4. removed the old daily launcher shell by deleting `test_run/test_run_main.py`
5. reattached battle-report export to the maintained launcher path through `test_run/test_run_entry.py`
6. continued subtraction inside `test_run/battle_report_builder.py`

This means the current request is not asking governance to judge a hypothetical plan only.

Governance is being asked to judge the next boundary after real reset work has already landed.

## 4. Current Engineering Assessment

### 4.1 Battle Report Path

The battle-report path is now back on the maintained launcher route.

That part is working:

- maintained launcher smoke can export BRF successfully
- `test_run/brf_narrative_messages.py` remains unchanged
- `battle_report_builder.py` has been cut further by deletion-first work

However, the current result is still only a modest simplification.

Engineering judgment:

- `battle_report_builder.py` is independent enough to keep simplifying
- but the remaining weight is no longer mainly launcher glue; it is report assembly weight
- further meaningful cuts may require governance guidance on what BRF capabilities are still considered active surface versus optional or legacy

### 4.2 `test_run_v1_0.py`

`test_run/test_run_v1_0.py` is no longer justified as a daily launcher.

However, it cannot yet be physically deleted because maintained hot-path modules still depend on it for core/helper content.

Current blocker:

- the active helper surface has not yet been migrated out of `test_run/test_run_v1_0.py`

Engineering judgment:

- deleting `test_run/test_run_v1_0.py` now would break maintained hot path
- keeping it forever would undermine the reset goal
- the real next decision is whether governance authorizes an explicit helper-surface migration round

### 4.3 Recent Splits And Coupling

Recent separation work created:

- `test_run/test_run_entry.py`
- `test_run/test_run_scenario.py`
- `test_run/test_run_execution.py`
- `test_run/test_run_telemetry.py`

Current engineering judgment is mixed:

- `execution` vs `telemetry` remains a good and justified boundary
- `entry` vs `scenario` is still acceptable
- but the overall reset is not complete while both still rely on `test_run/test_run_v1_0.py`

So the current issue is not that every split was wrong.

The issue is that one major historical helper host still sits under the new spine.

### 4.4 Runtime-Side Files

The human request now clearly extends beyond `test_run` alone and includes runtime-side simplification pressure, especially around:

- `runtime/engine_skeleton.py`

Engineering cannot proceed directly there under current repo rules.

Current blocker:

- root `AGENTS.md` treats the engine skeleton as a frozen layer

Engineering judgment:

- direct simplification of `runtime/engine_skeleton.py` is not authorized in the current rule set
- the maximum safe next step without governance approval is read-only analysis and burden inventory

## 5. Human Intent To Be Represented Clearly

The human owner's current intent is:

1. continue cutting `test_run/battle_report_builder.py`
2. keep `test_run/brf_narrative_messages.py` unchanged for now
3. physically delete `test_run/test_run_v1_0.py` once it is no longer on maintained hot path
4. re-evaluate recent separations honestly; if a split only moved complexity and increased coupling, it should be reconsidered
5. begin thinking about runtime-side simplification next, especially `runtime/engine_skeleton.py`

The human owner's concern is not only local code style.

The concern is broader:

- whether recent separation work produced a truly cleaner maintained structure
- whether cleanup is still buying enough future development leverage
- whether the next major bottleneck has moved from `test_run` into frozen runtime surfaces

## 6. Requested Governance Decisions

Governance guidance is requested on the following points.

### A. Battle Report Scope

Please clarify whether the intended direction is:

- continue simplifying `test_run/battle_report_builder.py` while preserving current BRF feature surface

or:

- explicitly demote parts of the BRF assembly surface so that more aggressive deletion is authorized

The practical question is whether further BRF simplification should remain mostly internal reduction, or whether active surface can be narrowed.

### B. `test_run_v1_0.py` Exit Plan

Please clarify whether governance authorizes a bounded migration round whose purpose is:

- move the maintained helper surface out of `test_run/test_run_v1_0.py`
- make `test_run/test_run_v1_0.py` physically deletable afterward

Without that authorization, the file remains in an awkward state:

- not a launcher anymore
- but still not removable

### C. Split Validation Standard

Please clarify the governance acceptance rule for recent and future separation work.

Requested standard:

- a split should be kept only if it reduces maintained hot-path burden or sharpens an approved structural boundary
- a split that only relocates complexity while increasing coupling should not be preserved by default

### D. Runtime Frozen-Layer Clarification

Please clarify whether the next phase may open a runtime-side preparatory round focused on:

- read-only burden inventory for `runtime/engine_skeleton.py`
- explicit candidate simplification targets
- governance request for any later authorized runtime cleanup

Engineering is not asking for silent permission to edit `runtime/engine_skeleton.py` now.

Engineering is asking whether governance wants:

- continued full freeze

or:

- a preparatory review round that could later support a separately authorized runtime simplification effort

## 7. Repo Paths For Governance Inspection

The following repo paths are the most relevant for governance review:

### Structural Records

- `analysis/engineering_reports/developments/20260318/structural_cleanup/test_run_structural_reset_preparation_20260320.md`
- `analysis/engineering_reports/developments/20260318/structural_cleanup/test_run_active_surface_reset_round1_20260320.md`
- `analysis/engineering_reports/developments/20260318/structural_cleanup/test_run_governance_followup_20260320.md`

### Maintained Launcher / Reset Spine

- `test_run/test_run_entry.py`
- `test_run/test_run_scenario.py`
- `test_run/test_run_execution.py`
- `test_run/test_run_telemetry.py`
- `test_run/test_run_anchor_regression.py`
- `.vscode/launch.json`

### Legacy / Transitional / Remaining Heavy Paths

- `test_run/test_run_v1_0.py`
- `test_run/test_run_v1_0_viz.py`
- `test_run/battle_report_builder.py`
- `test_run/brf_narrative_messages.py`
- `runtime/engine_skeleton.py`

### Example Maintained Output

- `analysis/exports/battle_reports/20260320/test_run_v1_0_20260320_173109_Battle_Report_Framework_v1.0.md`

## 8. Validation State

The current maintained path is stable under the validations already run:

- `python -m py_compile test_run/test_run_entry.py test_run/battle_report_builder.py test_run/test_run_v1_0.py`
- `python test_run/test_run_anchor_regression.py`
- maintained launcher smoke through `test_run/test_run_entry.py`

Current routine anchor state:

```text
[off] ok
[hybrid_v2] ok
[intent_unified_spacing_v1] ok
mismatch_count=0
```

Current maintained launcher state:

- battle-report export is functioning through `test_run/test_run_entry.py`
- `test_run/test_run_v1_0_viz.py` remains the renderer
- no runtime semantics change was introduced in this reporting turn

## 9. Requested Outcome

Engineering requests governance instruction on:

- BRF active-surface expectations
- the authorization boundary for making `test_run/test_run_v1_0.py` removable
- the acceptance test for recent separations that may have improved boundaries but not yet reduced enough hot-path burden
- whether runtime frozen-layer preparatory review may begin, especially for `runtime/engine_skeleton.py`

No runtime semantics changed in this turn.

Awaiting governance instruction.
