# step3_3d_pr6_cleanup_phase_closeout_and_governance_next_gate_20260410

Status: cleanup phase closeout  
Scope: phase classification, governance-facing completion read, and next gate  
Authority: local engineering closeout memo; not merge approval, not canonical governance replacement

## 1. Closeout read

This thread now reads the large subtraction-first cleanup line as **phase-complete**.

That phase should be read as:

- old-family mainline cleanup
- ownership-truth cleanup
- public-surface narrowing
- `battle` / `neutral` maintained-family alignment
- `fleet_body_summary` viewer-facing contract Phase 1
- active old-named cohesion seam reroot

It should **not** be read as:

- full repo cleanup completion
- compute optimization
- hot-path structural tightening completion
- formation-line implementation

## 2. What was materially completed in this phase

### A. Old-family mainline retirement moved from planning to execution

This phase retired or narrowed a large set of maintained old-family surfaces:

- maintained `v3a` execution path retired from `test_run` mainline
- baseline replaced from `v3a` to `v4a`
- old selector switching for `v2 / v3_test` retired from maintained public surface
- 2D viz / BRF / launcher-era artifacts removed from maintained mainline
- stale `v3a` settings and readout surfaces heavily narrowed
- `test_mode` retired

### B. Active `v4a` ownership became materially cleaner

- `restore_strength` is now direct and single-owned on the active `v4a` line
- active `v4a` no longer consumes old personality multipliers on the restore seam
- neutral now uses the maintained `battle` movement family rather than its own retained legacy movement owner
- `fire_optimal_range` now anchors battle standoff gap semantics instead of raw `attack_range`

### C. Residual legacy mechanism lines were cut or rerooted honestly

- FSR actuator retired from maintained `v4a`
- FSR kept only as passive radius-diagnostic geometry during the transition period
- old-named active cohesion seam rerooted to:
  - `_compute_fleet_cohesion_score_geometry()`
  - `last_fleet_cohesion_score`
- old `_compute_cohesion_v3_geometry()` retained only as cold-path historical reference

### D. Viewer-facing fleet geometry gained a maintained contract

`fleet_body_summary` Phase 1 is now active as the maintained export for:

- camera framing
- halo baseline placement
- HUD fleet-body reads
- replay-frame fleet body consumption

Viewer-side maintained centroid/radius recomputation was cut over to this export.

## 3. Why this now counts as phase-complete

This phase was intended to be subtraction-first cleanup.

That objective has now been satisfied at meaningful scale:

- major old-family maintained surfaces were retired
- active ownership truth is much clearer
- public settings/comments/reference surfaces were rerooted
- the remaining work is no longer primarily "delete more old code"

The next meaningful work is different in character:

- structure tightening of active hot paths

That is a new phase, not just "more cleanup of the same kind".

## 4. Important residuals that remain

The following are still real, but are no longer the core of the subtraction-cleanup phase:

1. large maintained hot-path functions still need structural tightening
   - `runtime/engine_skeleton.py::integrate_movement()`
   - `runtime/engine_skeleton.py::resolve_combat()`
   - `test_run/test_run_execution.py::run_simulation()`
   - `test_run/test_run_execution.py::_resolve_v4a_reference_surface()`
   - `test_run/test_run_execution.py::_evaluate_target_with_pre_tl_substrate()`

2. maintained runtime taxonomy is still only partially cleaned
   - current `v4a` candidate parameter subtree is now structured
   - but longer-term runtime-vs-candidate taxonomy remains a future design question

3. active fleet-body summary is only Phase 1 complete
   - viewer-facing maintained contract is in place
   - deeper harness/runtime internal geometry unification is not yet done

4. some cold-path historical functions remain intentionally retained
   - these are not mainline cleanup failures
   - they are explicit historical-reference holds

## 5. Governance-facing next gate

The next gate should now be read as:

- **continued structure tightening**

not:

- further broad old-family retirement by default
- compute optimization
- formation implementation

More specifically, the next execution thread should begin with:

1. hot-path structural-tightening planning
2. one bounded refactor slice that visibly reduces total reading burden
3. only after that, consider the next slice

## 6. Explicit non-goals for the next thread

The next thread should **not** begin by:

- reopening broad old-family deletion
- reopening `restore_strength`
- reopening battle/neutral movement-family unification
- widening targeting doctrine
- starting formation implementation
- treating helper extraction alone as simplification

## 7. Method lesson carried forward

This phase also established a clearer engineering boundary:

- subtraction-cleanup and structure-tightening are different phases

The immediate consequence is:

- this thread should close out cleanup and report to governance
- a fresh thread should take over hot-path structural tightening
- formation work should begin only after that tightening line is better prepared

## 8. Requested governance read

Engineering requests Governance to read the current local project state as:

1. the largest subtraction-first cleanup phase to date is now materially complete  
2. the repo is ready to leave old-family mainline retirement as its primary work mode  
3. the next justified phase is continued structure tightening on active maintained hot paths  
4. formation-line implementation should remain deferred until after that tightening phase
