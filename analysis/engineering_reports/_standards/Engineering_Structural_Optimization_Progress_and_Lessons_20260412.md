# Engineering Structural Optimization Progress and Lessons 20260412

Status: Governance-facing engineering summary  
Scope: post-cleanup structural tightening and readability/layering work after owner recovery  
Authority: Engineering summary only, not canonical semantics authority

## 1. Intent

This document summarizes the structural optimization work completed after the accepted cleanup closeout and records the main engineering lessons from that phase.

The goal of this wave was not mechanism redesign.

The goal was:

- owner recovery on the maintained hot path
- reading-burden reduction for Human review
- interface narrowing where real subtraction was available
- same-file structural layering where subtraction was not the honest tool

## 2. Main Outcomes

### A. Maintained runtime ownership was recovered

The maintained tick hot path is again runtime-owned:

- `runtime/engine_skeleton.py::step()`
- `runtime/engine_skeleton.py::evaluate_target()`
- `runtime/engine_skeleton.py::integrate_movement()`
- `runtime/engine_skeleton.py::resolve_combat()`

`test_run/test_run_execution.py` no longer acts as the maintained shadow engine owner.

`TestModeEngineTickSkeleton` was reduced to compatibility-shell status and removed from the maintained execution hot path.

### B. `test_run` was narrowed as orchestration / preparation / observation host

The main `test_run` line was tightened so that:

- `run_simulation()` remains the execution/orchestration owner
- execution-side bundle preparation stays in `test_run`
- runtime semantic ownership does not silently drift back into `test_run`

Notable narrowing work included:

- fail-fast layered settings loading
- `summary` shrinkage to real maintained readers
- removal of long-lived raw + `*_effective` movement carrier duplication
- retirement of hostile-contact mode `intent_unified_spacing_v1`
- retirement of movement selector alias `baseline`

### C. High-level personality/metatype interfaces were corrected

`PersonalityParameters` and Yang/metatype sampling were restored at the scenario/high-level interface, while being kept out of active runtime state evolution.

This preserved future interface value without polluting maintained runtime truth.

### D. VIZ cleanup stayed bounded and viewer-local

The viewer/replay path remained replay/view only.

The VIZ structural-hygiene pass completed:

- same-file readability/layering cleanup in `viz3d_panda/*`
- light ownership clarification for app / replay / renderer / camera
- removal of `app.py` direct dependence on `UnitRenderer` private internals
- light bounded clarification of `UnitRenderer` public app-facing surface

This remained structural hygiene only, not viewer modernization.

## 3. Structural Shape Now Achieved

The current maintained shape is:

- `runtime/engine_skeleton.py`
  - canonical runtime owner
- `test_run/test_run_execution.py`
  - execution/orchestration owner
- `viz3d_panda/*`
  - replay/view consumer layer only

This is the main structural gain of the phase:

- runtime owns maintained state evolution
- execution prepares inputs and packages observations
- viewer consumes replay output and does not own simulation semantics

## 4. Methods That Worked

### A. Owner-truth audit before editing

The most reliable cleanup steps came from first identifying:

- active owner
- active consumer
- transitional carrier
- cold residue

This consistently produced better cleanup than line-count-driven reshaping.

### B. Subtraction-first when truth allowed it

Real gains came from:

- deleting no-reader diagnostics
- shrinking dead payload fields
- retiring public selectors/modes that no longer deserved maintained visibility
- narrowing interfaces instead of adding wrappers

### C. Same-file internal layering when subtraction was not the honest tool

Once the main owner recovery was completed, several files still remained too heavy for Human review.

In those cases, the correct move was not broad file fan-out.

The correct move was:

- preserve the owner file
- keep the main execution chain visible
- add light sectioning / internal support grouping / review-oriented comments

This improved Human readability without reopening cross-file ownership ambiguity.

### D. Keep semantics near runtime, keep packaging near execution

The most stable boundary rule was:

- runtime produces maintained facts and semantics
- execution validates, prepares, and packages
- viewer consumes replay output and stays viewer-local

This boundary prevented shadow ownership from returning.

## 5. Lessons for Future Engineering Work

1. Cleanup and mechanism redesign should not be mixed once ownership debt is high.
2. Human-readable structure is a real deliverable, not cosmetic overhead.
3. Helper extraction is only a win when it reduces real reading burden; line motion alone is not simplification.
4. Same-file layering is safer than premature module proliferation while ownership is still settling.
5. High-level future-facing interfaces may be retained, but active runtime state should remain truthful.
6. Viewer-local cleanup should stay viewer-local and should not quietly absorb simulation semantics.

## 6. Current Read of What Remains

The large owner-recovery / structural-tightening wave is substantially complete enough to support a phase transition.

What remains open is not another generic cleanup pass.

The main remaining open design/governance topic is the separate Formation line.

That line should be treated as a new scoped carrier rather than mixed back into the just-finished structural optimization wave.
