# Plot Surface And Debug Block Governance Note

Status: Engineering note for Governance  
Date: 2026-03-10  
Scope: Visualization surface and debug-panel refinement only

## 1. Scope Boundary

This note covers:

- active plot surface layout in `test_run/test_run_v1_0_viz.py`
- currently retained but non-active indicators
- debug block payload refinement

This note does **not** cover:

- runtime behavior changes
- observer telemetry semantics changes
- BRF schema changes

All changes described here are visualization-layer only.

## 2. Current Active Plot Surface

Current active slots:

- `slot_01 + slot_02`: `Alive`
- `slot_03`: `FireEff`
- `slot_04`: `LossRate`
- `slot_05`: `Coh_v2` / `Coh_v3`
- `slot_06`: `CollapseSig`
- `slot_07`: `SplitSep`
- `slot_08`: `FrontCurv`
- `slot_09`: `Wedge`
- `slot_10`: `C_W_PShare`

Engineering judgment:

- `Alive`, `FireEff`, `CollapseSig` remain high-value operational indicators.
- `FrontCurv` and `Wedge` currently form the most useful pair for front-shape reading.
- `SplitSep` remains active, but is treated as a supporting separation indicator rather than a primary geometry classifier.
- `C_W_PShare` remains active for now because it still points toward the ODW insertion logic, even though it is visibly noisier than the other posture plots.

## 3. Retained But Non-Active Indicators

The following indicators remain available in telemetry or local helper logic but are not currently assigned to active slots:

- `AR_Fwd`
- `CollapseMargin`
- `c_conn`
- `rho`
- `c_scale`
- `NetAxisPush`
- `C_W_AdvGap`
- `PosPersist`

Engineering judgment:

- these should be treated as retained diagnostic assets, not current primary observer plots;
- their continued existence does not imply active interpretive priority;
- future promotion should require a clearer, narrower use case.

## 4. Debug Block Refinement

The debug block was reduced to high-value operational context.

Current intended payload:

- side archetype IDs and parameter rows
- `mode / movement / cohesion source`
- ODW prototype summary:
  - `on/off`
  - `k`
  - `clip`
- collapse baseline summary:
  - effective collapse source
  - active multiplier
  - plot smoothing window
- event anchors:
  - `ct`
  - `cut`
  - `pkt`

Removed from normal debug payload:

- per-tick contact / damage counters
- projection displacement diagnostics
- movement experiment subselector text

Engineering judgment:

- these removed fields were either already represented by plots or were too low-level for routine human review;
- the new debug block is intended to preserve battle-readability while keeping the most decision-relevant context visible.

## 5. Visualization Techniques vs Mechanism Semantics

The following are explicitly treated as visualization techniques only:

- plot smoothing via `visualization.plot_smoothing_ticks`
- narrowed display windows (for example, `SplitSep` shown in `[1.5, 2.5]`)
- plot-axis centering or clipping for readability

These techniques:

- do not alter raw observer telemetry
- do not alter BRF numeric summaries
- do not alter runtime mechanism behavior

Governance should therefore treat them as display-layer interpretation aids rather than semantic mechanism changes.

## 6. Current Engineering Position

Engineering considers the current plot surface materially improved:

- active slots are now concentrated on battle-readable indicators;
- dormant or low-yield indicators are no longer occupying prime visual space;
- the debug block is less crowded and more decision-relevant;
- display-only techniques are now more explicitly separated from mechanism interpretation.

No governance gate is requested for this note.
