# Governance Submit - Phase VII-3 Tactical Event Robustness Sweep (MB Axis)
Engine Version: v5.0-alpha5
Scope: Observer/Event/Report layer only (runtime behavior unchanged)

## Determinism Spot-check
- Case: FR8_MB8_PD5 (double run)
- Digest run1: `a972ee888e75f4c88bf1783ca161a178fdcdbe2244d5c1137ade06dca0b986b1`
- Digest run2: `a972ee888e75f4c88bf1783ca161a178fdcdbe2244d5c1137ade06dca0b986b1`
- Result: PASS

## Cases Run
- MB sweep: FR5_PD5_MB2/MB5/MB8
- Control: FR8_MB8_PD5

## MB Sweep Qualitative Summary (earliest-side event ticks)
- FR5_MB2_PD5: Cut(G/T)=(75/126), Pocket(G/T)=(226/226)
- FR5_MB5_PD5: Cut(G/T)=(85/125), Pocket(G/T)=(162/162)
- FR5_MB8_PD5: Cut(G/T)=(75/126), Pocket(G/T)=(202/202)

## Interpretation
- Across MB sweep, Cut occurs earlier than Pocket in both channels.
- Tactical Cut is stable around t=125-126; Tactical Pocket shifts with MB regime (earliest at MB5, latest at MB2).
- Pocket tactical events are post-contact in the sweep: `true`.

## cut_geom_only Count (MB sweep)
- side-level `cut_geom_only` count: `1`
- observed mismatch case: `FR5_MB2_PD5, side B` (diagnosed in dedicated root-cause file)

## Guardrails Reconfirmed
- No runtime movement/combat/PD/collapse changes.
- BRF Tier-2 mapping remains Channel T only.
- Tick semantics unchanged: `t=0` snapshot only, events `t>=1`.
