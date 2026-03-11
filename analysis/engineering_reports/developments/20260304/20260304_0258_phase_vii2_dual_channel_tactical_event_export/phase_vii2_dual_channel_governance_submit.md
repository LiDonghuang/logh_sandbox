# Governance Submit - Phase VII-2 Dual-Channel Tactical Event Export
Engine Version: v5.0-alpha5
Scope: Observer/Event/Report layer only (runtime behavior unchanged)

## Determinism Spot-check
- Case: FR8_MB8_PD5
- Digest run1: `2d048ddd55be21c648ee3e328ac4030b80d0ca07be026eb687a6e89275116a24`
- Digest run2: `2d048ddd55be21c648ee3e328ac4030b80d0ca07be026eb687a6e89275116a24`
- Result: PASS

## Cases Run
- FR8_MB8_PD5: FR=8.0, MB=8.0, PD=5.0
- reference_alpha_AB: FR=4.0, MB=5.0, PD=5.0
- FR5_MB2_PD5: FR=5.0, MB=2.0, PD=5.0
- FR5_MB5_PD5: FR=5.0, MB=5.0, PD=5.0
- FR5_MB8_PD5: FR=5.0, MB=8.0, PD=5.0

## Dual-channel Configuration
- `theta_split = 1.715`
- `theta_env = 0.583`
- `S = 20` ticks
- Channel G: geometry-only, no contact gate, `t>=1`
- Channel T: contact-gated (`in_contact_count > 0`), `t>=1`

## Channel G Pre-contact Trigger Counts
- Formation Cut (geom) pre-contact occurrences: 10
- Pocket Formation (geom) pre-contact occurrences: 0

## BRF Mapping Contract Check
- BRF Tier-2 fields are mapped from Channel T earliest-side ticks only: PASS

## Notable Mismatches
- Cases where `cut_tick_geom` exists but `pocket_tick_tactical` never triggers (side-level count): 0
- Cases where `pocket_tick_geom` exists but `cut_tick_tactical` never triggers (side-level count): 1

## Guardrails Reconfirmed
- No runtime movement/combat/PD/collapse changes.
- BRF schema unchanged (Operational Timeline rows unchanged).
- Tick semantics preserved: `t=0` snapshot only; events use `t>=1`.
