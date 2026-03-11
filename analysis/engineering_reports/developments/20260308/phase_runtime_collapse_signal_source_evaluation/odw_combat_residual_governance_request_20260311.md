# ODW Combat Residual Governance Request

Engine Version: v5.0-alpha5
Modified Layer: Runtime Engine (`runtime/engine_skeleton.py`, explicit exception approved for this cleanup only)
Affected Parameters: ODW (combat residual path removal only); no approved semantic change to MB / FR / PD
New Variables Introduced: none
Cross-Dimension Coupling: legacy ODW -> combat damage coupling removed; current active ODW effect remains movement posture-bias only
Mapping Impact: none
Governance Impact: runtime cleanup completed; mechanism interpretation now needs Governance direction on FR vs ODW authority boundary
Backward Compatible: yes for active runtime behavior under current data path; validated anchor case did not drift

Summary (<=5 lines)
- Mechanism audit found legacy ODW combat bias code still present in `resolve_combat`, but dormant under the current data path because unit-level `offense_defense_weight` remains `0.5`.
- The dormant combat residual was removed from `runtime/engine_skeleton.py` under explicit one-file exception approval.
- Fixed-seed anchor-case replay remained identical after cleanup: `end_tick=436`, `First Contact=108`, `Formation Cut=127`, `Pocket Formation=141`.
- Prior FR/ODW sweep therefore stands as a pure shape-layer result, not a mixed movement/combat result.
- Current evidence indicates FR is acting as the wedge-emergence gate, which conflicts with Governance doctrine that FR is a deformation stabilizer rather than a geometry generator.

## 1. Scope Executed

- Reviewed authority references:
  - `canonical/Sandbox_CrossThread_Protocol_v1.2.md`
  - `docs/architecture/Canonical_Authority_Alignment_v1.2.md`
  - `canonical/Ten_Parameters_Canonical_Index_v1.1.md`
  - `canonical/Strategic_Archetype_Layer_v1.5.md`
  - `docs/architecture/Formation_Geometry_Doctrine_v1.0.md`
- Reviewed topic note:
  - `analysis/engineering_reports/developments/20260308/phase_runtime_collapse_signal_source_evaluation/plot_surface_and_debug_block_governance_note_20260310.md`
- Browsed current topic folder contents for local continuity.
- Removed only the dormant ODW combat residual path from `runtime/engine_skeleton.py`.

## 2. Executed Cleanup

Removed from `runtime/engine_skeleton.py`:

- legacy `odw_alpha` combat constant
- per-contact `bias_attacker / bias_target / damage_scale` branch
- associated dead clamp state `last_damage_clamp_triggered`

Resulting combat damage path is now:

```text
event_damage = damage_per_tick * coupling * q
```

This cleanup does not touch:

- movement-layer ODW posture bias
- archetype semantics
- BRF schema
- observer telemetry semantics

## 3. Validation Evidence

### Commands

- `python -m py_compile runtime/engine_skeleton.py`
- fixed-seed replay of the anchor case after cleanup

### Key validation result

Anchor case after cleanup remained:

- `end_tick = 436`
- `alive_A_end = 27`
- `alive_B_end = 0`
- `First Contact = 108`
- `Formation Cut = 127`
- `Pocket Formation = 141`
- `B_profile = wedge_like_deformation`
- `B_wedge_p50 = 0.802`
- `B_collapse_mean = 0.166`

Interpretation:

- cleanup removed dead code, not active behavior

## 4. Mechanism Analysis

### 4.1 ODW combat path status

The removed combat residual was non-authoritative and dormant because:

- `UnitState.offense_defense_weight` stays at `0.5` in the active data path
- combat bias code therefore contributed no real differential effect

This confirms the earlier FR / ODW sweep was already a shape-layer experiment.

### 4.2 Current shape-layer result

Under fixed seed with Side A fixed at `MB2 / FR2 / PD2 / ODW8` and Side B varied:

- with `B = MB8 / PD8 / ODW2 / FR2` -> `mixed_front`
- with `B = MB8 / PD8 / ODW2 / FR5` -> `mixed_front`
- with `B = MB8 / PD8 / ODW2 / FR8` -> `wedge_like_deformation`

Interpretation:

- FR is currently acting as the threshold for wedge emergence
- this exceeds the doctrinal role described in `Formation_Geometry_Doctrine_v1.0`

### 4.3 Governance tension

Doctrine states:

- FR = resistance to deformation
- no single parameter should directly determine formation shape

Current engineering evidence indicates:

- FR is not merely preserving an already-formed posture
- FR is materially controlling whether wedge-like geometry appears at all

## 5. Requested Governance Instruction

Engineering requests Governance direction on the following:

1. Confirm whether the active interpretation target remains:
   - `FR = deformation stabilizer only`
   - not `FR = wedge-emergence gate`
2. Confirm whether Engineering should treat the current FR dominance as:
   - a bug / over-coupling defect to be corrected
   - or a tolerated temporary artifact during stabilization
3. Confirm whether the next engineering step should be:
   - bounded runtime coefficient audit and reduction of FR shape authority
   - or additional DOE only, without runtime adjustment

## 6. Recommended Next Step Plan

If Governance authorizes continued engineering work, recommended next sequence is:

1. Perform a code-level FR authority audit in `runtime/engine_skeleton.py` only:
   - isolate every term where `formation_rigidity` directly scales movement restoration or shape-preserving contraction
2. Build a bounded adjustment proposal:
   - reduce FR from geometry-emergence authority back toward deformation-resistance authority
3. Re-run the same fixed-seed FR sweep:
   - verify that wedge emergence no longer depends primarily on FR alone
   - while retaining FR influence on shape persistence / stability

## 7. Assumptions

- `archetypes/archetypes_v1_5.json` is treated as an experimental configuration source, not as canonical authority.
- Canonical semantics are taken from the non-archive authority documents listed above.
- This report requests instruction; it does not itself authorize further runtime redesign.
