# LOGH Sandbox

## 3D VIZ Cluster Micro Sway Reference v1.0

Status: maintained viewer reference  
Scope: `viz3d_panda/unit_renderer.py` cluster-only micro motion  
Authority: viewer-side reference only, not runtime doctrine

---

## Purpose

This note records the small local sway applied to visible `CLUSTER` ships inside
the 3D Panda3D viewer.

The effect is decorative only.
It does not modify replay data, runtime state, unit positions, or export semantics.

---

## Mechanism Rule

The micro sway applies only to the inner `CLUSTER` ships.

It does not apply to:

- the outer `TOKEN`
- the unit root transform
- replay source positions
- targeting / fire-link geometry

The sway is added on top of each ship's base local offset from
`CLUSTER_LAYOUT_OFFSETS`.

---

## Time Base

The animation is driven by viewer replay time:

- `playback_seconds = (current_frame.tick + pulse_phase) / playback_fps`

The sway then uses a slower viewer-local clock derived from that replay time:

- `cluster_sway_seconds = playback_seconds * CLUSTER_SWAY_CLOCK_SCALE`

This keeps the motion deterministic across:

- normal playback
- slowed / accelerated playback gears
- offline export

Wall-clock time is intentionally not used.

---

## Activation Rule

The sway is intentionally not always-on.

It is enabled only when:

- playback is currently running
- playback gear is `1`, `2`, or `3`

It is disabled when:

- playback is paused
- playback gear is `4` or `5`

When disabled, visible cluster ships return to their base local layout offsets
instead of holding a residual sway pose.

---

## Phase Rule

Each cluster ship gets a stable phase seed from:

- `unit_key`
- `ship_index`

The implementation uses a small deterministic string hash.
It must not use Python's built-in `hash(...)`, because that is process-randomized.

This keeps neighboring ships visually staggered without introducing randomness
between runs.

---

## Motion Shape

Each visible cluster ship receives a small sinusoidal offset on all three axes:

- `X`: slight side-to-side drift
- `Y`: slight fore-aft drift
- `Z`: slight vertical bob

All three axes share one base sway frequency.
The visible staggering comes from different axis phase mixes and from the stable
per-unit / per-ship phase seeds, so the motion still avoids synchronized pulsing.

---

## Tuning Surface

The current human-facing tuning constants live near the cluster geometry block in
`viz3d_panda/unit_renderer.py`:

- `CLUSTER_SWAY_AMPLITUDE_X`
- `CLUSTER_SWAY_AMPLITUDE_Y`
- `CLUSTER_SWAY_AMPLITUDE_Z`
- `CLUSTER_SWAY_FREQUENCY`

Preferred tuning order:

1. adjust amplitudes first
2. adjust the shared frequency second
3. only then change phase mixing if the motion still feels too synchronized

---

## Visibility Rule

The sway is only updated while `CLUSTER` is currently visible.

This keeps the mechanism lightweight and aligned with the distance-rendering rule
that already fades or hides the cluster at farther camera distances.

---

## Maintenance Rule

If the cluster motion rule changes materially, update this note together with the
viewer code change.
