# test_run - Harness / Launcher / Experiment Discipline

This directory is the harness / launcher / experiment-plumbing layer.

It is not the place to silently broaden runtime semantics, silently redesign observer meaning, or disguise additive indirection as simplification.

The purpose of these local rules is to harden Phase A / A5 cleanup discipline.

---

## T-01 - Directory Identity

`test_run/` is responsible for:

- launcher / harness entry
- experiment plumbing
- scenario execution support
- settings access for harness use
- battle report assembly handoff
- visualization handoff

`test_run/` is **not** the canonical runtime core.

Do not use harness cleanup to silently rewrite:

- runtime semantics
- movement core
- combat semantics
- observer ontology
- battle report doctrine

---

## T-02 - Simplification Means Visible Subtraction

In `test_run/`, simplification must produce visible human-facing reduction.

Valid simplification outcomes include:

- smaller launcher entrypoints
- narrower interfaces
- fewer layers between settings consumption and execution
- quieter default stdout
- fewer dead compatibility paths
- fewer wrappers/builders/helpers in the hot path

The following do **not** count as simplification by default:

- moving code into more helper functions while caller size remains materially unchanged
- replacing direct logic with orchestration glue
- creating `_build_*` functions whose main role is parameter shuttling
- adding wrappers so that code only looks more modular
- preserving old compatibility branches during a subtraction-focused cleanup turn

---

## T-03 - No Single-Use Passthrough Wrappers

Do not add a new helper, builder, or wrapper if its main role is:

- forwarding arguments unchanged
- repackaging scalars into another wide call without reducing interface width
- moving visible weight out of the caller without reducing total reading burden

A helper is allowed only if it clearly does at least one of the following:

- removes substantial repeated logic
- enforces a real local invariant
- materially shrinks the caller
- becomes a stable reused unit across multiple call sites

Single-use passthrough wrappers are discouraged by default.

---

## T-04 - Validation Discipline for Launcher-Consumed Settings

Launcher-consumed settings must prefer explicit failure over tolerant continuation.

Required rule:

- missing or invalid settings that are required for launcher execution should fail fast

Not allowed by default:

- silent fallback to defaults
- broad try/except that hides invalid config
- warning + continue behavior for required config
- continuing after malformed layered settings for required launcher inputs

Allowed exception:

- explicit normalization/clamping already defined by runtime semantics or explicitly requested behavior

---

## T-05 - Stdout Must Stay Quiet by Default

Default successful execution in `test_run/` should be quiet.

By default, allowed stdout should be limited to a small human-readable set such as:

- short run summary
- explicit failure
- final export/report path
- explicitly requested validation summary

Not allowed by default:

- mode-remap narration spam
- verbose explanatory print for successful normal paths
- per-tick stdout in ordinary cleanup turns
- “helpful” debug narration that was not explicitly requested

Debug logging must be opt-in.

---

## T-06 - No Cleanup-Driven Scope Creep

A cleanup turn in `test_run/` must not silently become:

- runtime mechanism redesign
- observer interpretation redesign
- battle report semantics redesign
- movement-core review
- next-phase architecture activation

If cleanup work starts pulling on one of those topics, stop and report instead of continuing automatically.

---

## T-07 - Prefer Direct Narrowing Over Plumbing Growth

When a launcher or harness function becomes too wide, preferred options are:

- delete obsolete branches
- collapse unnecessary intermediate layers
- keep values in a smaller local scope
- group truly cohesive launcher-only values if that materially narrows interfaces

Discouraged options:

- adding a new builder function only to transfer many scalars elsewhere
- preserving every historical parameter surface during cleanup
- converting one wide function into several equally wide functions

The goal is narrower human-facing orchestration, not prettier parameter transport.

---

## T-08 - Regression Rule for Routine Cleanup

For routine `test_run/` harness cleanup, use the established anchor policy:

- default: 3-run anchor regression
- escalate to full 9-run only for major changes

Do not silently escalate every cleanup turn into a high-cost protocol event.

Use the dedicated regression policy document as operational reference.

---

## T-09 - Acceptance Rule

Any claimed simplification in `test_run/` must be judged against:

- `docs/engineering/SIMPLIFICATION_ACCEPTANCE_CHECKLIST.md`

If the checklist is not clearly passed, do not describe the result as successful simplification.

Report it as one of:

- partial cleanup
- boundary clarification only
- refactor without visible subtraction
- not accepted as simplification

---

## T-10 - Human Trust Rule

This directory is currently under heightened scrutiny because repeated cleanup turns improved boundary clarity without improving visible maintainability enough.

Therefore, when working in `test_run/`, Codex must optimize for:

- visible reduction
- honest reporting
- smaller default surface area
- lower noise
- lower reading burden

Do not trade human trust for formal-looking indirection.
