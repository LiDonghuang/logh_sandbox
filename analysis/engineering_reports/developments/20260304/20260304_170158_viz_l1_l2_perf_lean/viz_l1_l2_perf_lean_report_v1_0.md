# Visualization L1 + L2 Performance Lean Report v1.0

Status: Completed (Visualization-only)
Date: 2026-03-04
Scope: `analysis/test_run_v1_0_viz.py` only
Behavior Change: None (simulation/runtime semantics unchanged)

## 1. Objective

Implement agreed performance lean package:

- L1: eliminate per-frame duplicate geometry builds in animation hot path.
- L2: add static-side-plot fast path and reduce per-frame artist churn.

## 2. Boundaries

- No engine/runtime decision logic changes.
- No canonical/mapping changes.
- No parameter meaning changes.
- `show_attack_target_lines=true` remains fully supported.

## 3. Implemented Changes

### 3.1 L1 - Precompute Target Geometry Per Frame

Added precompute at `prepared_frames` stage:

- `attack_direction_map` (only when `vector_display_mode in {attack, composite}`)
- `target_segments` (only when `show_attack_target_lines=true`)
- `A_alive` / `B_alive` flattened tuples for direct use in frame update

Result:

- Removed per-frame repeated point-map construction for target lines and attack-direction vectors.
- Reduced Python object churn in `update_frame`.

### 3.2 L1 - Quiver Artist Reuse (No Count-Triggered Recreate)

Changed quiver update model:

- Introduced fixed `quiver_capacity` (max alive units across prepared frames).
- `build_quiver_data(..., pad_to_count=quiver_capacity)` pads inactive slots with transparent entries.
- `update_quiver` now only does `set_offsets + set_UVC + set_color`.

Result:

- Removed per-frame `quiver.remove() + make_quiver(...)` rebuild path.
- Stabilized artist identity and reduced draw overhead.

### 3.3 L2 - Static Side Plot Blit Fast Path

Added conditional blit path:

- `blit_enabled = (not tick_plots_follow_battlefield_tick) and (not auto_zoom_2d)`
- Dynamic artists marked animated and returned from frame callback.
- `FuncAnimation(..., blit=blit_enabled, init_func=..., cache_frame_data=False)`

Result:

- When side plots are static and camera is static, redraw scope is limited to dynamic battlefield/debug artists.

### 3.4 L2 - Tick Text Decoupled from Axes Title

- Replaced per-frame `battle_ax.set_title(...)` updates with dedicated `battle_tick_text` artist update.

Result:

- Avoided repeated title layout/reflow overhead on each tick.

## 4. Why L2 Is Conditional

`auto_zoom_2d` changes axis limits/ticks during playback. In matplotlib, this invalidates blit background assumptions and can cause artifacts/regression. Therefore blit fast path is intentionally enabled only when camera is not auto-zooming.

This keeps correctness while still providing a true fast path for static-camera runs.

## 5. Validation

### 5.1 Syntax

Executed:

```powershell
python -m py_compile analysis/test_run_v1_0_viz.py analysis/test_run_v1_0.py
```

Result: PASS

### 5.2 Semantics Guard

- Simulation inputs/outputs and runtime decision source untouched.
- Vector mode behavior unchanged (`effective/free/attack/composite`).
- Target line semantics unchanged (still post-tick center-to-center linkage).

## 6. Operational Guidance

For daily faster interactive runs:

- Keep `show_attack_target_lines=true` (supported).
- Use `tick_plots_follow_battlefield_tick=false`.
- If acceptable for the session, set `auto_zoom_2d=false` to activate blit fast path.

## 7. Next Optimization Candidates (No Semantics Change)

1. Optional: precompute + cache death-ring artist signatures per frame to further reduce patch churn.
2. Optional: skip `set_segments` when target segment list unchanged from prior frame.
3. Optional: split "render battlefield" and "debug text refresh" cadence (battlefield still each tick).

