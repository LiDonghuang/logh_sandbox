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

- content: frame / fps / gear
- example: `frame=120/600  fps=6.0  gear=3/5`
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

### `focus <fleet_id>+`

- shown in HUD: yes when current battle engagement indicators are finite
- source: `runtime_debug.focus_indicators[<fleet_id>]`

Current fields:

- `eng_act`
  - source field: `engagement_geometry_active`
  - meaning: how active the battle engagement-geometry owner currently is
  - current read:
    - low = battle is still mostly far-field owned
    - high = Layer B engagement geometry is now materially active

- `front_rw`
  - source field: `front_reorientation_weight`
  - meaning: bounded fleet-level weight shifting front responsibility toward the effective fire axis
  - current read:
    - low = front still mostly owned by pre-contact geometry
    - higher = front is being more strongly reoriented toward the current fire plane

- `fire_da`
  - source field: `front_axis_delta_deg`
  - meaning: angle difference in degrees between current formation front and current effective fire axis
  - current read:
    - lower = formation front is closer to the active fire plane
    - higher = formation front is still lagging or diverging

The underlying `effective_fire_axis_xy` vector is carried in the harness bundle,
but it is not currently printed directly in the HUD.
For Human review, the angle delta is easier to read than a raw vector pair.

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
- `close_drive`
- `brake_drive`
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
| frame / fps / gear | yes | stable line |
| fleet centroids | yes | stable line |
| kinetics line (`v` + `h`) | yes | stable line |
| fire-efficiency line (`e`) | yes | stable line |
| direction / fire-links / smoothing / fixture tail | yes | stable line |
| `fire_eff` | no | consumed by the stable fire-efficiency line instead |
| `hold_weight` | no | consumed by the stable kinetics line instead |
| `front_strip_gap` | yes | current near-contact relation focus line |
| `engagement_geometry_active` | yes | current battle-geometry focus line |
| `front_reorientation_weight` | yes | current battle-geometry focus line |
| `front_axis_delta_deg` | yes | current battle-geometry focus line |
| `td_norm` | no | payload-only |
| `advance_share` | no | payload-only |
| `shape_err` | no | payload-only |
| `forward_current` | no | payload-only |
| `actual_forward` | no | payload-only |
| `lateral_current` | no | payload-only |
| `actual_lateral` | no | payload-only |
| `relation_gap` | no | payload-only |
| `close_drive` | no | payload-only |
| `brake_drive` | no | payload-only |
| `centroid_distance` | no | payload-only |
| `front_gap` | no | payload-only |
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
