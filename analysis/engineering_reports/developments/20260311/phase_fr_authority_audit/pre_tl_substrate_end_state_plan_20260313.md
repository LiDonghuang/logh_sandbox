# Pre-TL Substrate End-State Plan

Date: 2026-03-13
Status: Engineering end-state plan
Scope: Define the bounded `test_run` end state for selectable pre-TL target substrate candidates, without freezing future `TL` semantics.

## 1. Purpose

The current line remains inside pre-TL substrate preparation.

The end-state goal is not to choose a permanent doctrinal winner.
It is to leave:

- one practical default
- one or two retained future candidates
- a clean `test_run` selector for bounded comparison

## 2. Current end-state decision

For `test_run`, the current bounded end state is:

- default: `nearest5_centroid`
- retained future candidate: `weighted_local`
- retained future candidate: `local_cluster`

These three are made setting-selectable inside `test_run`.

## 3. Why this is the current bounded end state

### `nearest5_centroid`

Current engineering reading:

- strongest tested balance candidate among explicitly local smooth families
- clearly less sharp than raw `nearest-enemy`
- more local-contact preserving than the more global weighted/centroid family

So it is the current best practical default for pre-TL substrate work.

### `weighted_local`

Current engineering reading:

- strongest symmetry/smoothness candidate among the local families tested
- useful retained candidate because it may define the "too global" shoulder of acceptable local smoothness

So it should remain available for comparison, but not as the present default.

### `local_cluster`

Current engineering reading:

- still admissible as a future candidate
- remains more governance-sensitive than `nearest5_centroid` or `weighted_local`
- should stay under stricter scrutiny because cluster logic can drift toward implicit semantic preference

So it remains available, but not as the preferred default.

## 4. What is not part of the end-state selector set

The following are kept as comparison references in notes, not as long-lived default/candidate selections:

- raw `nearest-enemy`
- pure `enemy centroid`

Reason:

- `nearest-enemy` is retained conceptually as a sharp lower-bound endpoint
- pure centroid is retained conceptually as a symmetry-clean upper reference

They remain useful for framing, but are not part of the bounded `test_run` end-state selector set.

## 5. Setting interface intent

The selector exists only as a `test_run` / harness-side control for bounded low-level comparison.

It must not be interpreted as:

- future `TL`
- partial `TL`
- frozen runtime doctrine
- permanent target-selection semantics

## 6. Boundary reminder

Even with a selectable pre-TL substrate:

- low-level field remains only a weighting/biasing structure
- future `TL` still owns targeting horizon and targeting preference semantics
- battlefield target-selection patterns remain emergent outputs, not guaranteed signatures of one substrate choice
