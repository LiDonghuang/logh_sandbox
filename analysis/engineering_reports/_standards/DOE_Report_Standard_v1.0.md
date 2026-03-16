# DOE Report Standard v1.0

## 1. Scope
This standard defines mandatory report structure and minimum table schema for DOE packages.
It applies to observer/event/reporting outputs only and does not authorize runtime behavior changes.

## 2. Mandatory Summary Sections
Every DOE summary markdown must contain all sections below.

1. Cell-level main effects table.
2. Factor main-effect check (minimum: FR, MB, PD).
3. Opponent hardness table.
4. Censoring/cap sensitivity note.
5. Standards Compliance block.

## 3. Cell-level Main Effects (Required Columns)
At minimum, each cell row must include:

1. Cell key fields: FR, MB, PD (or equivalent cell_* names).
2. Run count.
3. A-side win rate (all models).
4. Mean survivors for A and B.
5. Median end_tick.
6. Tactical Cut and Pocket timing metrics (Channel T).
7. Paired deltas (v3a-v1) when a paired model comparison exists.

## 4. Factor Main-Effect Check (Required)
At minimum:

1. Per-level aggregates for FR, MB, PD.
2. Automatic detection of no-observable-main-effect pattern.
3. Automatic duplication-pattern check (for example row/column duplication across grid slices).

If a factor has only one tested level, mark as "not testable in this DOE".

## 5. Opponent Hardness (Required)
At minimum:

1. Opponent identifier and run count.
2. A-side win rate (overall).
3. A-side win rate split by model when model comparison exists.
4. At least one timing metric (for example median end_tick).

## 6. Censoring/Cap Sensitivity (Required)
Summary must explicitly check whether duration metrics are censored by caps/timeouts.

At minimum report:

1. Number and percentage of runs that hit observed max end_tick or explicit cap.
2. If censoring exists, mark duration metrics as low sensitivity and prioritize event-time metrics.

## 7. Required CSV Schema
Minimum fields for DOE run table:

1. `run_id`
2. `movement_model` (if applicable)
3. `FR`, `MB`, `PD` or `cell_FR`, `cell_MB`, `cell_PD`
4. opponent identifier (`opponent_archetype_id` or equivalent)
5. `random_seed_effective`
6. `background_map_seed_effective`
7. `metatype_random_seed_effective` (when metatype generation is active)
8. `winner`
9. `end_tick`
10. `remaining_units_A`
11. `remaining_units_B`
12. `first_contact_tick`
13. `first_kill_tick`
14. `tactical_cut_tick_T`
15. `tactical_pocket_tick_T`

Minimum fields for DOE delta table (paired model comparison):

1. Cell key (`FR/MB/PD` or `cell_*`)
2. Opponent identifier
3. `run_id_v1`
4. `run_id_v3a`
5. `delta_end_tick_v3a_minus_v1`
6. `delta_tactical_cut_tick_T_v3a_minus_v1`
7. `delta_tactical_pocket_tick_T_v3a_minus_v1`

## 8. Seed Consistency Rule
DOE execution must use fixed and auditable seeds unless seed itself is the explicit experimental factor.

1. Do not run DOE with implicit randomness (`-1`) for any seed that can affect compared outputs.
2. At minimum, fix and record:
   `random_seed_effective`, `background_map_seed_effective`, and `metatype_random_seed_effective` when applicable.
3. For paired comparisons, the compared runs must use identical effective seeds.
4. If seed variation is itself the experiment, state that explicitly in the DOE objective and report.
5. Standards Compliance block must state whether fixed-seed discipline was enforced.

## 8A. Mechanism DOE Design Preference
For new mechanism-mapping and orthogonality studies, DOE design should prefer controlled symmetry before archetype-anchor coverage.

1. Default first-pass design should use controlled Side A versus controlled Side B when the objective is mechanism isolation rather than archetype-anchor validation.
2. Fixed canonical opponents remain appropriate for anchor checks, external-validity checks, or explicit opponent-interaction studies.
3. When factor count grows, prefer fractional factorial or other bounded screening designs over full Cartesian expansion unless a full grid is itself the stated objective.
4. Reports must state which role the opponent design serves:
   isolation, anchor check, or interaction study.
5. If asymmetrical fixed-opponent design is chosen, the summary should state why symmetric controlled design was not used.

## 8B. Boundary Default Rule
For DOE execution, `runtime.physical.boundary.enabled` should default to `false` unless boundary behavior itself is an explicit experimental factor.

1. DOE defaults should use `boundary_enabled = false`.
2. If boundary is enabled in a DOE, the objective and summary must state why.
3. If boundary is itself a DOE factor, boundary-on and boundary-off results must be reported as a separate comparison axis.
4. Boundary behavior must not be left implicitly on in mirrored or mechanism-isolation DOE runs.

## 9. Naming Convention
DOE package should use a stable prefix in one folder.

Recommended:

1. `<topic>_run_table.csv`
2. `<topic>_delta_table.csv` (if paired)
3. `<topic>_summary.md`
4. `<topic>_binned_distributions.csv` (optional but recommended)
5. `<topic>_determinism_check.md` (recommended)

## 10. Runtime Length Policy Reminder
Do not hardcode fixed duration limits as policy.
Preferred run-control is `max_time_steps = -1` with post-elimination grace termination as implemented in harness.
Each report must state effective runtime length behavior in configuration snapshot or summary note.
