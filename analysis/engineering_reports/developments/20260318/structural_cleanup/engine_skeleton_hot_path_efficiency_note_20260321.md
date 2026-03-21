# Engine Skeleton Hot-Path Efficiency Note

Status: Round 2 delivery  
Scope: `runtime/engine_skeleton.py` only  
Date: 2026-03-21

## Reduced Unnecessary Work

Round 2 reduced hot-path work in the following ways:

- removed per-tick compatibility alias remap for movement experiment names
- removed per-tick fallback lookup for `PRECONTACT_CENTROID_PROBE_SCALE`
- reduced repeated hot-path `getattr(...)` normalization on active knobs by switching to direct attribute reads
- pulled shared ODW posture-bias knob reads out of the fleet loop
- pulled cohesion decision-source and debug-v1 cache lookup out of the fleet loop
- removed duplicated numeric-rank parsing logic by using one shared same-file helper
- moved internal diagnostic state bookkeeping off the top-level attribute surface into `_debug_state`

## Debug-Off Path

With diagnostics disabled, the following no longer happen in the old style:

- compatibility alias/fallback checks inside movement hot path
- repeated attribute fallback resolution for core movement/combat knobs
- duplicated numeric-rank helper setup in both movement and combat

The diagnostic payload blocks themselves still remain gated behind `diag_enabled` / `diag4_enabled`.

## What Was Not Optimized In Round 2

Round 2 did not attempt to benchmark or re-architect core runtime loops. It did not change:

- enemy-centroid and geometry recomputation structure inside `integrate_movement(...)`
- per-attacker enemy scan shape inside `resolve_combat(...)`
- larger diagnostic payload assembly when debug is enabled
- the retained `v1` / `v1_debug` reference branches

## Honest Remaining Efficiency Burden

Remaining likely burden centers are still:

- movement fleet geometry math
- combat target-assignment scanning
- diag-heavy post-processing when diagnostics are on

So Round 2 reduces hot-path waste, but it does not complete performance cleanup of the skeleton.
