ODW Posture Readout Refinement Note

Date: 2026-03-09
Scope: Observer / analysis only

Purpose

Refine ODW prototype readouts so the observer layer measures width-wise posture effects more directly than whole-fleet aggregate geometry summaries.

Implemented readouts

1. Front Curvature Index

- Per fleet, project unit positions onto the initial A->B battle axis and its lateral axis.
- Select the current front band as the most forward 30% of units.
- Split that front band into center vs wings by absolute lateral offset.
- Metric:
  - `FrontCurvatureIndex = mean(front_center_advance) - mean(front_wing_advance)`
- Exported normalized by `min_unit_spacing`.
- Interpretation:
  - positive: center protrudes ahead of wings
  - near zero: flatter front
  - negative: wing-leading / concave tendency

2. Center / Wing Parallel Pressure Share

- Per fleet, split all alive units into center vs wings by absolute lateral offset.
- Compute positive parallel velocity along the initial A->B battle axis.
- Metric:
  - `C_W_PShare = (center_parallel_total - wing_parallel_total) / (center_parallel_total + wing_parallel_total)`
- Range:
  - `[-1, +1]`
- Interpretation:
  - positive: forward pressure concentrated toward center
  - near zero: balanced width-wise pressure
  - negative: forward pressure weighted toward wings

3. Posture Persistence Time

- Use the sign of normalized `FrontCurvatureIndex` and `C_W_PShare`.
- Coherent center-led posture:
  - `FrontCurvatureIndex >= 0.10`
  - `C_W_PShare >= 0.05`
- Coherent wing-led posture:
  - `FrontCurvatureIndex <= -0.10`
  - `C_W_PShare <= -0.05`
- Metric:
  - signed consecutive-tick run length of the current coherent posture state
- Interpretation:
  - positive: sustained center-led posture
  - negative: sustained wing-led posture
  - zero: no stable posture state

Plot layout

- `slot_03`: `Wedge`
- `slot_04`: `C_W_PShare`
- `slot_05`: `SplitSep`
- `slot_06`: `LossRate`
- `slot_07`: `Coh_v2` / `Coh_v3`
- `slot_08`: `ColSignal`
- `slot_09`: `FrontCurv`
- `slot_10`: `PosPersist`

Why this refinement

- The ODW prototype acts primarily through width-wise redistribution of parallel pressure.
- Whole-fleet aggregates such as `AR_forward`, `Wedge`, and `NetAxisPush` compress that local redistribution and therefore under-read the mechanism.
- The new readouts separate:
  - geometry tendency (`FrontCurv`)
  - pressure redistribution (`C_W_PShare`)
  - temporal stability (`PosPersist`)

Boundary

- Observer-only
- No runtime behavior change
- No new parameter semantics
- No pursuit / retreat / targeting remapping
