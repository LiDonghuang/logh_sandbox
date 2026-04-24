# LOGH Sandbox

## 3D VIZ Debug Block Reference v1.0

Status: maintained viewer reference  
Scope: `viz3d_panda/app.py` left-bottom debug block  
Authority: viewer-side reference only, not runtime doctrine

---

## Purpose

This note records the meaning of the 3D viewer debug block.

The block is intentionally allowed to change over time.
The last one or two lines may be repurposed as current focus indicators
for the mechanism currently under investigation.

When indicators are added, removed, shown, or hidden, this document should be
updated together with the viewer change.

---

## Layout Rule

The left-bottom debug block and the right-bottom control block share one common
bottom inset parameter in `viz3d_panda/app.py`:

- `HUD_BOTTOM_INSET`

This keeps:

- the debug block's last line above the bottom edge
- the right-side control block aligned to the same bottom margin

The current layout rule is:

- first build the full text content
- then count lines
- then place each block so its bottom edge respects `HUD_BOTTOM_INSET`

The two blocks therefore share a bottom edge margin rather than a top edge margin.

---

## Always-Shown Lines

### Line 1

- content: fleet alive counts + playback state
- example: `A=100 B=100  state=playing`
- shown in HUD: yes

### Line 2

- content: frame / tps / gear
- example: `frame=120/600  tps=2.0  gear=3/5`
- shown in HUD: yes

### Line 3

- content: fleet centroids
- example: `A=(12.4, 48.1)  B=(87.7, 49.3)`
- shown in HUD: yes

### Line 4

- content: fleet kinetics snapshot
- definition:
  - `v` = absolute fleet-centroid displacement from frame `t-1` to frame `t`
  - `h` = current bounded battle-hold weight when available from runtime-debug focus indicators
- example: `Kinetics: A: v=0.73 h=0.42 | B: v=0.68 h=0.39`
- shown in HUD: yes

### Line 5

- content: fleet fire efficiency
- definition:
  - `e` = current per-tick fire-efficiency read for each fleet
  - formula: actual damage this tick / theoretical damage potential this tick
- example: `FireEff: A: e=0.12 | B: e=0.09`
- shown in HUD: yes

### Line 6

- content: viewer mode tail
- current fields:
  - direction mode
  - fire-link mode
  - smoothing state
  - fixture readout when present
- shown in HUD: yes

---

## Focus Indicators

These lines are intentionally temporary/replaceable.
They are the preferred place to expose the current mechanism-level indicators
that Human and Engineering are actively using.

The current HUD keeps only two replaceable focus groups:

- near-contact relation
- battle geometry

Older transport / shaping diagnostics remain available in payload only.

### `focus <fleet_id>@`

- shown in HUD: yes when current battle gap indicators are finite
- source: `runtime_debug.focus_indicators[<fleet_id>]`

Current field:

- `strip_gap`
  - source field: `front_strip_gap`
  - meaning: centroid distance minus the sum of both fleets' front-strip depths along the centroid axis
  - front-strip depth is computed from the leading strip of alive units rather than the full body half-extent
  - current harness read:
    - leading strip = top 20 percent of alive units by forward projection
    - clamped to 4..16 units
  - current read:
    - positive = battle bodies still separated under a front-line entry proxy
    - near zero = front strips are approaching effective battle entry distance
    - negative = front-strip overlap / pass-through proxy

- `front_gap`
  - source field: `front_gap`
  - meaning: centroid distance minus both fleets' full forward half-extents along the centroid axis
  - current read:
    - positive = fronts are still separated under the broader body read
    - near zero = broad front contact is imminent
    - negative = forward-body overlap / crossing proxy

- `rel_gap`
  - source field: `relation_gap`
  - meaning: maintained battle relation-gap scalar currently used by the battle bundle
  - current read:
    - higher positive = more standoff room remains
    - near zero = standoff room is being consumed
    - negative = relation state is already compressed / violated

### `focus <fleet_id>+`

- shown in HUD: yes when current maneuver-envelope indicators are finite
- source: `runtime_debug.focus_indicators[<fleet_id>]`

Current fields:

- `raw_gap`
  - source field: `relation_gap_raw`
  - meaning: unsmoothed maintained battle relation-gap scalar
  - plain-language read:
    - think of this as "the fleet still has how much immediate room before the fronts are too compressed"
  - current read:
    - higher positive = more immediate standoff room remains before smoothing
    - near zero = early no-crossing release owner is nearing its handoff zone
    - negative = early relation state is already compressed before smoothing
  - runtime owner/write:
    - `runtime/engine_skeleton.py`
    - `EngineTickSkeleton._prepare_v4a_bridge_state(...)`
    - written into the maintained battle bundle as `battle_relation_gap_raw`
  - runtime use:
    - `runtime/engine_skeleton.py`
    - `EngineTickSkeleton._compute_unit_desire_by_unit(...)`
    - read as the early no-crossing / early restraint owner before the local controller decides how much heading freedom to allow
  - observer/export path:
    - `test_run/test_run_execution.py`
    - `_build_focus_indicator_payload(...)`
    - exported to `runtime_debug.focus_indicators[*].relation_gap_raw`

- `embg`
  - source field: `early_embargo_permission`
  - meaning: current early-release permission for unit-local heading freedom under the precontact no-crossing branch
  - plain-language read:
    - think of this as "how much permission the Unit currently has to peel out early"
  - current read:
    - low = early local peel-out should stay constrained
    - high = early no-crossing embargo is mostly released
  - runtime owner/write:
    - `runtime/engine_skeleton.py`
    - `EngineTickSkeleton._compute_unit_desire_by_unit(...)`
    - derived from `battle_relation_gap_raw` inside the same-tick local maneuver controller and written to local-desire diagnostics as `early_embargo_permission`
  - runtime use:
    - `runtime/engine_skeleton.py`
    - `EngineTickSkeleton._compute_unit_desire_by_unit(...)`
    - directly multiplies the heading-side local bias weight; when it is low, the Unit may see an opportunity but is still not allowed much local heading freedom
  - observer/export path:
    - `runtime/engine_skeleton.py`
    - `_MovementDiagSupport.flush_pending(...)`
    - emitted through pending `local_desire` diagnostics and then exported by `test_run/test_run_execution.py::_build_focus_indicator_payload(...)`

- `reopen`
  - source field: `late_reopen_persistence`
  - meaning: current late reopen-space persistence read for the experimental behavior-line branch
  - plain-language read:
    - think of this as "the worst compression is past, but the line is still not reopened enough, so keep a mild reopen-space response alive"
  - current read:
    - low = no late reopen-space persistence is active
    - high = the late sticky-contact / not-yet-reopened band is active
  - runtime owner/write:
    - `runtime/engine_skeleton.py`
    - `EngineTickSkeleton._compute_unit_desire_by_unit(...)`
    - derived from `battle_relation_gap_current` inside the same-tick local maneuver controller and written to local-desire diagnostics as `late_reopen_persistence`
  - runtime use:
    - `runtime/engine_skeleton.py`
    - `EngineTickSkeleton._compute_unit_desire_by_unit(...)`
    - used only inside the experimental behavior-line branch to keep bounded speed restraint / heading suppression alive a little longer in the late reopen-space band
  - observer/export path:
    - `runtime/engine_skeleton.py`
    - `_MovementDiagSupport.flush_pending(...)`
    - emitted through pending `local_desire` diagnostics and then exported by `test_run/test_run_execution.py::_build_focus_indicator_payload(...)`

- `lng`
  - source field: `desired_longitudinal_travel_scale_min`
  - meaning: minimum signed longitudinal travel ask for the fleet in the current tick
  - plain-language read:
    - negative means the enabled signed-longitudinal capability is asking for bounded backward travel along realized facing
    - positive means forward longitudinal travel remains requested
  - observer/export path:
    - `runtime/engine_skeleton.py`
    - `_MovementDiagSupport.flush_pending(...)`
    - emitted through pending `local_desire` diagnostics and then exported by `test_run/test_run_execution.py::_build_focus_indicator_payload(...)`

- `vspd`
  - source field: `realized_signed_longitudinal_speed_min`
  - meaning: minimum realized signed longitudinal speed for the fleet in the current tick
  - plain-language read:
    - negative means actual backward travel along realized facing occurred
    - values near zero mean the signed speed is being braked or crossing through zero
  - observer/export path:
    - `runtime/engine_skeleton.py`
    - `_MovementDiagSupport.flush_pending(...)`
    - emitted through pending `local_desire` diagnostics and then exported by `test_run/test_run_execution.py::_build_focus_indicator_payload(...)`

- `brk`
  - source field: `brake_drive`
  - meaning: bounded current brake-drive scalar from the maintained battle bundle
  - plain-language read:
    - think of this as "how much the fleet-level battle bundle is already asking movement to stop pushing in so hard"
  - current read:
    - low = little fleet-side brake pressure
    - high = stronger restorative / anti-overrun brake pressure is active
  - runtime owner/write:
    - `runtime/engine_skeleton.py`
    - `EngineTickSkeleton._prepare_v4a_bridge_state(...)`
    - written into the maintained battle bundle as `battle_brake_drive_current`
  - runtime use:
    - `runtime/engine_skeleton.py`
    - `EngineTickSkeleton._compute_unit_desire_by_unit(...)`
    - reused as later restorative brake context for speed restraint and restore-line weighting; it is not the early no-crossing owner
  - observer/export path:
    - `test_run/test_run_execution.py`
    - `_build_focus_indicator_payload(...)`
    - exported to `runtime_debug.focus_indicators[*].brake_drive`

### Payload-Only Diagnostics

The following indicators remain available in the harness payload for local
debugging, but they are not currently shown in the HUD:

- `td_norm`
- `advance_share`
- `shape_err`
- `forward_current`
- `actual_forward`
- `lateral_current`
- `actual_lateral`
- `relation_gap`
- `engagement_geometry_active`
- `close_drive`
- `brake_drive`
- `front_reorientation_weight`
- `front_axis_delta_deg`
- `centroid_distance`
- `front_gap`
- `rms_gap`
- `center_forward_offset`
- `phase_forward_mean`
- `forward_align`
- `forward_neg_frac`
- `forward_pos_frac`
- `forward_delta_mean`

These remain useful for local analysis, but they currently add too much HUD noise
for battle-first review.

---

## Display Status Table

| Field / line | Shown in HUD | Notes |
| --- | --- | --- |
| alive counts + playback state | yes | stable line |
| frame / tps / gear | yes | stable line |
| fleet centroids | yes | stable line |
| kinetics line (`v` + `h`) | yes | stable line |
| fire-efficiency line (`e`) | yes | stable line |
| direction / fire-links / smoothing / fixture tail | yes | stable line |
| `fire_eff` | no | consumed by the stable fire-efficiency line instead |
| `hold_weight` | no | consumed by the stable kinetics line instead |
| `front_strip_gap` | yes | current near-contact relation focus line |
| `front_gap` | yes | current near-contact relation focus line |
| `relation_gap` | yes | current near-contact relation focus line |
| `relation_gap_raw` | yes | current maneuver-envelope focus line |
| `early_embargo_permission` | yes | current maneuver-envelope focus line |
| `late_reopen_persistence` | yes | current maneuver-envelope focus line |
| `desired_longitudinal_travel_scale_min` | yes | current signed-longitudinal capability focus line |
| `realized_signed_longitudinal_speed_min` | yes | current signed-longitudinal capability focus line |
| `brake_drive` | yes | current maneuver-envelope focus line |
| `td_norm` | no | payload-only |
| `advance_share` | no | payload-only |
| `shape_err` | no | payload-only |
| `forward_current` | no | payload-only |
| `actual_forward` | no | payload-only |
| `lateral_current` | no | payload-only |
| `actual_lateral` | no | payload-only |
| `engagement_geometry_active` | no | payload-only |
| `close_drive` | no | payload-only |
| `front_reorientation_weight` | no | payload-only |
| `front_axis_delta_deg` | no | payload-only |
| `centroid_distance` | no | payload-only |
| `rms_gap` | no | payload-only |
| `center_forward_offset` | no | payload-only |
| `phase_forward_mean` | no | payload-only |
| `forward_align` | no | payload-only |
| `forward_neg_frac` | no | payload-only |
| `forward_pos_frac` | no | payload-only |
| `forward_delta_mean` | no | payload-only |
| additional future temporary indicators | maybe | must be added here when introduced |

---

## Maintenance Rule

When the current focus indicators change:

1. update `viz3d_panda/app.py`
2. update this document
3. mark whether each indicator is currently shown in HUD

This avoids repeated re-explanation in thread and keeps Human-readable viewer
semantics synchronized with the active investigation line.
