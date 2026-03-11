# Analysis Scripts Index v1.0

## 1. Scope
Index of reusable analysis/reporting scripts under `analysis/engineering_reports/_standards/`.

## 2. Scripts

### 2.1 `doe_postprocess.py`
Purpose:

1. Generate mandatory DOE summary sections.
2. Produce cell-level, factor-level, and opponent-level aggregate tables.
3. Add censoring/cap sensitivity diagnostics.
4. Write standards compliance block.

Inputs:

1. DOE run table CSV (`--run-table`).
2. Optional DOE delta table CSV (`--delta-table`).

Outputs:

1. Summary markdown (`--summary-out`).

Invocation example:

```powershell
python analysis/engineering_reports/_standards/doe_postprocess.py `
  --run-table analysis/engineering_reports/developments/20260304/phase_viiiB_movement_3a_doe_validation/doe_b2_run_table.csv `
  --delta-table analysis/engineering_reports/developments/20260304/phase_viiiB_movement_3a_doe_validation/doe_b2_delta_table.csv `
  --summary-out analysis/engineering_reports/developments/20260304/phase_viiiB_movement_3a_doe_validation/doe_b2_summary.md `
  --title "DOE B2 Summary - Controlled Cell Persona Override"
```

## 3. Versioning Rule
When script behavior changes materially, update:

1. script internal version constant.
2. this index document if input/output contract changed.

## 4. Mandatory DOE Auto-Sections (Governance Alignment)
`doe_postprocess.py` is the default generator for mandatory DOE summary sections:

1. Cell-level main effects.
2. Factor sensitivity checks (minimum FR/MB/PD).
3. Opponent hardness ranking.
4. Runtime duration censoring/cap sensitivity notes.
5. Event timing statistics (Cut/Pocket and related deltas when available).

## 5. DOE Seed Discipline
All DOE runners and report packs must follow fixed-seed discipline unless seed is the explicit experimental factor.

1. Keep `random_seed_effective` consistent across compared runs.
2. Keep `background_map_seed_effective` consistent across compared runs.
3. Keep `metatype_random_seed_effective` consistent across compared runs when metatype generation is active.
4. Record these effective seeds in run tables so paired comparisons remain auditable.
