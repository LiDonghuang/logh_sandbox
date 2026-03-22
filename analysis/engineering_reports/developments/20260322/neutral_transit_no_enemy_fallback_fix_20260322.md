# Neutral Transit No-Enemy Fallback Fix (2026-03-22)

Status: Limited Authorization  
Scope: immediate no-enemy semantics bug fix plus very bounded neutral-transit validation

## 1. Bug Statement

In the current movement path, the no-enemy branch allowed an enemy-derived direction term to fall back into an own-centroid pull.

Pre-fix behavior:

- if `enemy_alive_count == 0`, runtime first set:
  - `enemy_centroid_x = centroid_x`
  - `enemy_centroid_y = centroid_y`
- later, each unit constructed:
  - `enemy_vec = enemy_centroid - unit.position`
- in a no-enemy scene, that becomes:
  - `enemy_vec = own_centroid - unit.position`

So a nominally enemy-derived attract ingredient silently became an extra inward self-centering term in neutral transit.

## 2. Why It Is a Bug

This is a semantics bug because:

- it is not a real enemy-derived direction
- it is not a neutral fallback
- it injects hidden inward shaping into a no-enemy scene

Correct no-enemy behavior is:

- enemy-derived contribution = `0`

not:

- enemy-derived contribution = own-centroid pull

## 3. Minimal Code Correction

Minimal fix location:

- `runtime/engine_skeleton.py`

Correction:

- preserve the existing real-enemy branch
- add `has_enemy_alive = enemy_alive_count > 0`
- when `has_enemy_alive == false`, set:
  - `enemy_dir_x = 0.0`
  - `enemy_dir_y = 0.0`

This is intentionally narrower than a broader movement change.
It does not rewrite FR, MB, ODW, cohesion architecture, or `v4b`.

## 4. Validation Scope

Validation was deliberately small:

1. `python -m py_compile runtime/engine_skeleton.py test_run/test_run_scenario.py test_run/test_run_execution.py test_run/test_run_entry.py`
2. `python test_run/test_run_anchor_regression.py`
3. one pre-fix vs post-fix neutral-transit paired check on the current super-long-distance fixture:
   - `arena_size = 400`
   - `origin = [50,50]`
   - `objective = [350,350]`
   - `movement_model = v3a`

For front stretching, the validation used one bounded proxy:

- objective-axis front extent from fleet centroid, normalized by the initial front extent

This is a validation-only reading, not a new canonical metric.

## 5. Result Summary

### Pre-fix

- arrival tick: `445`
- final RMS radius ratio: `0.684`
- mean corrected-unit ratio: `0.899`
- peak projection pairs: `147`
- peak projection mean displacement: `0.285`
- peak projection max displacement: `0.863`
- peak front-extent ratio: `3.819`
- final front-extent ratio: `3.676`

### Post-fix

- arrival tick: `440`
- final RMS radius ratio: `0.829`
- mean corrected-unit ratio: `0.817`
- peak projection pairs: `115`
- peak projection mean displacement: `0.284`
- peak projection max displacement: `0.856`
- peak front-extent ratio: `5.491`
- final front-extent ratio: `5.480`

### Reading

- no-enemy hidden inward pull was removed
- front stretching increased noticeably
- projection burden decreased
- end-state compaction decreased
- arrival became slightly faster in this long-distance case

This is consistent with the bug hypothesis:

- the old fallback was masking forward extension by adding unintended inward recovery

## 6. Explicit Non-Authorizations

This turn did **not** do any of the following:

- no expected-position restoration
- no reference-formation system
- no FR semantic rewrite in code
- no broad `v4b` implementation
- no reintroduction of MB / ODW / stray / FSR family work
- no baseline replacement

## 7. v4b Principle Reminder

This fix does **not** complete `v4b`.

The frozen `v4b` principle remains:

- fleet objective trend should stay fleet-level and shared
- formation restoration should not continue to be represented by centroid pull
- FR should eventually act on expected-position / reference-formation restoration
- FR should not continue to amplify centroid-directed inward pull
- same-fleet separation may remain low-level spacing, but expected spacing belongs to formation logic rather than legality cleanup

## 8. Bottom Line

Immediate action was correct:

- remove the no-enemy fallback that converted an enemy-derived term into own-centroid pull

Frozen follow-up principle also remains correct:

- future `v4b` should move FR away from centroid pull and toward expected-position / reference-formation restoration, but that rebuild is not part of this bug-fix turn.
