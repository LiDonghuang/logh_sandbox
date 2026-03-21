# Engine Skeleton Retired Mechanism Kill List

Status: Phase 0 Preparation  
Date: 2026-03-21  
Scope: deletion-first candidate list for future bounded rounds

## Already Completed Before This Kill List

These items were on the human deletion agenda, but are already gone in current `HEAD`:

- movement alias remap for `exp_a_reduced_centroid`
- `PRECONTACT_CENTROID_PROBE_SCALE` fallback

They should stay deleted and must not be reintroduced.

## Immediate Delete Candidates

### Dead / zero-placeholder locals

- `major_hat_x`
- `major_hat_y`
- `ar_ratio`
- `ar_forward_ratio`
- `precontact_gate`
- `axial_pull_x`
- `axial_pull_y`
- `attackers_to_target`

Why treated as retired:

- they are assigned
- they do not drive maintained runtime output
- they do not appear to feed maintained diagnostics output
- they behave like stale scaffolding or zero placeholders

Risk:

- low, but each should still be diff-reviewed in isolation because some were originally introduced for observer diagnostics

### Duplicate local tooling already normalized

- numeric-rank parsing duplicate copies

Status:

- already normalized to a single same-file helper
- future rounds should delete any reintroduced copies immediately

## Retirement-Decision Candidates

These should not be silently deleted before an explicit round target is approved.

### `MOVEMENT_MODEL == "v1"` branch

Why on kill list:

- it behaves like a legacy/reference path adjacent to maintained hot path
- it is the closest movement-side equivalent of a retired host still kept alive

Risk:

- may still count as canonical reference path
- deleting without explicit retirement decision could silently change acceptable debug/reference coverage

### `COHESION_DECISION_SOURCE == "v1_debug"` family

Includes:

- `v1_debug` branch logic
- `debug_cohesion_v1_enabled`
- `_debug_prev_cohesion_v1`
- internal `debug_last_cohesion_v1` cache

Why on kill list:

- legacy/reference burden still attached to movement path

Risk:

- governance history still references it as debug baseline comparison path

### `diag4` legacy family

Includes:

- `debug_diag4_enabled`
- `debug_diag4_topk`
- `debug_diag4_contact_window`
- `debug_diag4_return_sector_deg`
- `debug_diag4_neighbor_k`
- associated history/payload assembly

Why on kill list:

- large debug payload family still entangled with maintained hot path

Risk:

- unclear whether human daily diagnostics still depend on it

### RPG diagnostics family

Includes:

- `debug_diag4_rpg_enabled`
- `debug_diag4_rpg_window`
- associated `_debug_diag4_rpg_*` bookkeeping

Why on kill list:

- product-sized debug surface with unclear maintained value

Risk:

- unclear whether it is still part of accepted maintained diagnostic surface

### combat assert family

Includes:

- `debug_contact_assert`
- `debug_contact_sample_ticks`
- combat assert branch in `resolve_combat(...)`

Why on kill list:

- gate-only assertion path embedded in maintained combat hot path

Risk:

- if still used for human debugging, deletion should be explicit rather than silent

## Do Not Put On Kill List

Do not treat these as retired unless a later governance round says otherwise:

- active runtime knobs such as `attack_range`, `damage_per_tick`, `separation_radius`
- active combat/contact/boundary/FSR/ODW knobs
- active v2 movement/combat main path
- maintained debug outputs still read by `test_run`:
  - `debug_last_combat_stats`
  - `debug_diag_last_tick`
  - `debug_last_cohesion_v3`
  - `debug_last_cohesion_v3_components`
