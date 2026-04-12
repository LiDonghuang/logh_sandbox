# test_run - Harness / Launcher / Experiment Discipline

This directory is the harness / launcher / experiment-plumbing layer.

It is not the place to silently broaden runtime semantics, silently redesign observer meaning, or disguise additive indirection as simplification.

The purpose of these local rules is to harden cleanup and stabilization discipline in `test_run/`.

---

## T-01 - Directory Identity and Ownership Boundary

`test_run/` is responsible for:

- launcher / harness entry
- experiment plumbing
- scenario execution support
- settings access for harness use
- battle report assembly handoff
- visualization handoff

`test_run/` is **not** the canonical runtime core.

Do not use harness work to silently rewrite:

- runtime semantics
- movement core
- combat semantics
- observer ontology
- battle report doctrine

If runtime already owns a line of behavior such as:

- targeting
- cohesion
- damage quality
- unit-level combat decision logic

`test_run/` must not grow a second parallel owner for that same line unless the Human explicitly approves the duplication for a bounded purpose.

Preferred pattern:

- pass truth to the active owner
- keep the bridge honest

For `v4a` movement, `battle` and `neutral` must share the same movement
mechanism family. The only allowed semantic difference is objective source,
unless Human explicitly approves a narrower exception.

---

## T-02 - Simplification Means Visible Subtraction

In `test_run/`, simplification must produce visible human-facing reduction.

Valid simplification outcomes include:

- smaller launcher entrypoints
- narrower interfaces
- fewer layers between settings consumption and execution
- quieter default stdout
- fewer dead compatibility paths
- fewer wrappers, builders, or helpers in the hot path

The following do **not** count as simplification by default:

- moving code into more helper functions while caller size remains materially unchanged
- replacing direct logic with orchestration glue
- creating `_build_*` functions whose main role is parameter shuttling
- adding wrappers so that code only looks more modular
- preserving old compatibility branches during a subtraction-focused cleanup turn

Preferred cleanup moves are deleting obsolete branches, collapsing unnecessary intermediate layers, and keeping values in a smaller local scope instead of redistributing the same wide parameter flow.

Do not add a new helper, builder, or wrapper if its main role is:

- forwarding arguments unchanged
- repackaging scalars into another wide call without reducing interface width
- moving visible weight out of the caller without reducing total reading burden

A helper is justified only when it removes substantial repeated logic, enforces a real local invariant, materially shrinks the caller, or becomes a stable reused unit across multiple call sites.

The goal is narrower human-facing orchestration, not prettier parameter transport.

---

## T-03 - Validation and Failure Discipline for Launcher Settings

Launcher-consumed settings must prefer explicit failure over tolerant continuation.

Required rule:

- missing or invalid settings that are required for launcher execution should fail fast

Not allowed by default:

- silent fallback to defaults
- broad try/except that hides invalid config
- warning plus continue behavior for required config
- continuing after malformed layered settings for required launcher inputs

Allowed exception:

- explicit normalization or clamping already defined by runtime semantics or explicitly requested behavior

---

## T-04 - Stdout Must Stay Quiet by Default

Default successful execution in `test_run/` should be quiet.

By default, allowed stdout should be limited to a small human-readable set such as:

- short run summary
- explicit failure
- final export or report path
- explicitly requested validation summary

Not allowed by default:

- mode-remap narration spam
- verbose explanatory print for successful normal paths
- per-tick stdout in ordinary cleanup turns
- "helpful" debug narration that was not explicitly requested

Debug logging must be opt-in.

---

## T-05 - Cleanup Scope and Hot-Path Isolation

A cleanup turn in `test_run/` must not silently become:

- runtime mechanism redesign
- observer interpretation redesign
- battle report semantics redesign
- movement-core review
- next-phase architecture activation

If cleanup work starts pulling on one of those topics, stop and report instead of continuing automatically.

For regressions centered in `test_run/test_run_execution.py`, Codex must use:

- the Human-confirmed good/bad window as the highest-trust anchor
- subtraction-first A/B isolation
- one mechanism group at a time
- static owner / code-path audit before relying on dynamic test sweeps

Codex must not stack multiple battle probes, smoothers, or temporary branches into the same active hot path before one bad path has been isolated.

Chronology notes are attachments, not proof of causality.

---

## T-06 - Acceptance and Regression Discipline

For routine `test_run/` cleanup, use the established anchor policy:

- default: 3-run anchor regression
- escalate to full 9-run only for major changes

Do not silently escalate every cleanup turn into a high-cost protocol event.

Any claimed simplification in `test_run/` must be judged against:

- `docs/engineering/SIMPLIFICATION_ACCEPTANCE_CHECKLIST.md`

If the checklist is not clearly passed, do not describe the result as successful simplification.

Report it as one of:

- partial cleanup
- boundary clarification only
- refactor without visible subtraction
- not accepted as simplification

---

## T-07 - Ownership Truth and Active Surface Honesty

Before adding or changing harness-side mechanism logic, Codex must identify whether the active owner is:

- harness-native
- runtime-native
- transitional bridge or carrier

If a harness surface acts through an older runtime carrier, Codex must describe it as transitional rather than native.

`test_run/` must not claim retirement, native ownership, or dead-path status without current code-path verification.

Retired or invalidated probes must be removed from the active harness surface promptly.

Do not leave behind:

- dormant public knobs
- stale comments
- silently bypassed branches
- legacy compatibility paths that still look active

If a bridge still depends on an older carrier, keep that dependency explicit until true decoupling is complete.

---

## T-08 - Human Trust Rule

This directory is under heightened scrutiny because repeated cleanup turns improved boundary clarity without improving visible maintainability enough.

Therefore, when working in `test_run/`, Codex must optimize for:

- visible reduction
- honest reporting
- smaller default surface area
- lower noise
- lower reading burden

Do not trade human trust for formal-looking indirection.
