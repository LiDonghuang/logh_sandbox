# Step 3 3D PR #6 Visual / Terminal / Targeting / Export Update
## Governance Report

Status: governance report  
Scope: current active PR `#6` review / learning line plus bounded 3D viewer support work  
Authority: Engineering report for Human + Governance discussion  
Non-scope: merge approval, default switch approval, runtime-core rewrite

---

## I. Human-Approved Scope Before This Push

This push was prepared under explicit Human approval for the following scope:

1. report the current Human read of the new 3D `posture` mode
2. remove old 3D `composite` from the active 3D review surface
3. include the recent harness-only removal of terminal hard regularization
4. report the current `attack_range = 10` targeting / fire-angle concern and request Governance discussion
5. include the separate Panda3D video-export sub-thread handoff and scoped files

Human additionally approved that this push may include the currently dirty
runtime/test-only settings JSON files for reproducibility of the current local
observation line.

---

## II. 3D Direction-Mode Update

### A. Current Human read of `posture`

Human read after local review is:

- `posture` already looks reasonable as a bounded viewer-side mode
- it is visibly better than the older alternatives for the question:
  - "what visible maneuvering posture does this ship currently seem to have?"

Engineering agrees with that read.

Current local `posture` is still bounded and incomplete, but it is already a
more honest read than:

- the old 3D `movement`-only travel read
- the older `composite` angle-bisector style read

### B. 3D interface simplification

Following the latest Human direction:

- old `realistic` remains fully retired
- active 3D review modes are now reduced to:
  - `movement`
  - `posture`
- old `composite` is removed from the active 3D viewer surface and from the
  primary mode-cycle path

This does **not** claim that all historical references to `composite` are gone
from the repo.
It means:

- current 3D Human review should no longer treat `composite` as part of the
  active direction-mode interface

Current read:

- `movement` remains the main travel-direction review mode
- `posture` remains a bounded but now meaningful viewer-side maneuver-posture
  mode

---

## III. Terminal Hard-Regularization Removal

Engineering locally disabled the harness-only morphology-level terminal/hold
latching path inside `test_run/test_run_execution.py`.

The reason was explicit Human rejection of the previous arrival behavior:

- too hard
- too discrete
- too visibly forced

The current local read after removing that hard regularization is:

### Neutral

- neutral arrival no longer produces the previous obvious forced terminal snap
- however, neutral vs battle disagreement on forward compression remains open

### Battle

- contact onset still reads as highly chaotic
- so disabling terminal hard regularization did **not** solve the larger battle
  motion problem

### Governance question

Engineering requests Governance guidance on better terminal semantics.

Possible reads include:

1. a temporary bounded terminal read for the current carrier
2. deferring a cleaner terminal/hold answer until the Governance-side
   formation-fork completes its next proposal

Engineering does **not** currently recommend restoring the old hard latch path.

---

## IV. Targeting / Fire-Angle Concern at `attack_range = 10`

Human has recently been testing with:

- `attack_range = 10`

This has proven useful because it exposes mechanism problems more clearly and
is also closer to the intended source-material battle read.

### A. Current hot-path reality

The current hot-path unit-level target assignment lives in frozen runtime:

- `runtime/engine_skeleton.py::resolve_combat()`

Current read:

1. target selection is almost entirely:
   - low-HP target preference within attack range
2. distance is only a very weak tie-break
3. current fire-angle logic does **not** choose the target
4. instead, fire angle only modifies damage quality after a target has already
   been chosen

So the current hot path is not:

- angle-aware target selection

It is closer to:

- low-HP target picking plus post-selection directional damage adjustment

### B. Human read

Human now reads the result as:

- fire direction is often too concentrated
- too many units focus the same target in the same tick
- this makes the current "fire-angle penalty" line feel insufficient or
  structurally misplaced

### C. Current bounded Engineering suggestion

Engineering does **not** recommend a broad redesign in this report.

The current bounded suggestion is only:

- consider a simple weight-and-score extension to target selection

Candidate bounded read:

- keep an HP term
- add a crowding / already-targeted term
- add an angle-quality term

So a first bounded target score could become something like:

- `score = hp_term + crowd_term + angle_term`

This would not be a full doctrine change.
It would just test whether:

- slightly less concentrated fire allocation
- plus angle-aware target preference

already produces a more plausible battle surface at `attack_range = 10`.

### D. Governance ask

Because this hot path lives in frozen runtime, Engineering is **not**
requesting implementation approval in this report.

Engineering is asking Governance to judge:

1. whether the current diagnosis is correct
2. whether a simple weight-and-score extension is the right next bounded read
3. whether the current fire-angle line should remain:
   - post-selection damage quality only
   or begin to participate in:
   - target selection itself

Cold-path historical local-enemy experiments are intentionally omitted here.
The question now is about the active hot path only.

---

## V. Battle / Transition Read Reminder

This report does **not** claim that the larger formation-transition problem is
solved.

Current accepted read remains:

- target morphology
- transport / topology continuity
- movement realization

still co-own the main unresolved problem on PR `#6`.

This report only narrows several adjacent support lines:

- visual direction semantics
- arrival regularization read
- battle target allocation concern

---

## VI. Video Export Sub-Thread Inclusion

This push also includes the separate Panda3D offline-export engineering thread.

Handoff memo:

- `archive/ts_handoff_archive/TS_HANDOFF_20260402_154545/TS_HANDOFF_20260402_154545.md`

Key delivered files:

- `viz3d_panda/export_video.py`
- `launch_dev_v2_0_offline_render.bat`
- associated `viz3d_panda/app.py` / `viz3d_panda/camera_controller.py` support
- `.vscode/launch.json` export launch config

Current engineering read:

- this export line is useful and bounded
- it stays inside viewer/export scope
- it should be preserved as support tooling for future Human motion review

---

## VII. Bottom Line

Current Engineering/Human read for Governance:

1. `posture` is already a meaningful viewer-side gain and currently reads
   better than the older alternatives for visible maneuver posture
2. old `composite` should no longer remain on the active 3D review surface
3. disabling harness-side terminal hard regularization was the correct move;
   it removed a visibly dishonest arrival behavior, even though broader battle /
   neutral transition disagreement remains
4. at `attack_range = 10`, current hot-path target selection now looks too
   concentrated, and the present fire-angle line appears too weak or too late
   in the pipeline
5. Engineering therefore requests Governance discussion on:
   - better terminal semantics
   - and whether a first simple target `weight + score` extension should be the
     next bounded targeting read
