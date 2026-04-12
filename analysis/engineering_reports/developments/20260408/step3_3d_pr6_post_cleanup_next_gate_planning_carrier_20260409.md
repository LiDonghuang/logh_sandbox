# Step3 / PR6 Post-Cleanup Next Gate Planning Carrier

Status: planning carrier  
Scope: next governance-aligned retirement gate after the large cleanup stage  
Authority: local engineering planning note, not canonical governance authority

## 1. Why this note exists

PR #8 governance comment 1 identified the next major gate as:

- `test_mode` retirement planning
- broader `v3a` support-path retirement planning

The cleanup stage since then has already gone materially further than the state described in that comment:

- maintained movement baseline is now `v4a`
- maintained explicit `v3a` movement execution is retired
- old 2D viz / BRF / report carriers are removed from the maintained mainline
- `restore_strength` is already native `v4a`
- multiple public old-family settings/readout surfaces are already narrowed or removed

Therefore the next gate should no longer be read as “begin cleanup.”
It should be read as:

- perform a truthful residual support-path audit
- decide the next bounded retirement slices
- keep further deletion aligned to that truth

## 2. Current truthful residual read

### A. `test_mode`

Current owners:

- `test_run/test_run_scenario.py::parse_test_mode`
- `test_run/test_run_scenario.py::_build_run_cfg`
- `test_run/test_run_entry.py`
- `test_run/test_run_v1_0.runtime.settings.json::run_control.test_mode`

Current real behavior:

- `test_mode` no longer gates movement-model experimentation
- it no longer enables maintained `v3a` execution
- it currently does two practical things:
  - labels the run
  - turns observer/diagnostic output on for `mode >= 1`

Current wording still overstates legacy support:

- comments still say `mode=2` permits explicit legacy/experimental selectors where such surfaces remain

That is now only partially true and is increasingly misleading.

### B. Maintained runtime cohesion seam still has old-family naming

Current owners:

- `runtime/engine_skeleton.py::_compute_cohesion_v3_geometry`
- `runtime/engine_skeleton.py::evaluate_cohesion`
- `runtime/runtime_v0_1.py::BattleState.last_fleet_cohesion`
- `test_run/test_run_execution.py` trajectory export of `last_fleet_cohesion`

Current truthful read:

- this is still an active maintained seam
- it is no longer publicly selector-switchable
- but its naming remains old-family / `v3` flavored

This means:

- it is **not** ready for silent deletion
- it **is** ready for explicit truth/owner review and a bounded retirement-or-reroot decision

### C. FSR remains as a residual support surface

Current owners:

- `runtime/engine_skeleton.py` still contains FSR implementation
- `test_run/test_run_scenario.py` still builds `fsr_strength`
- `test_run/test_run_execution.py` forces `fsr_enabled = False` for `movement_model == "v4a"`
- runtime settings/comments/reference still expose `fsr_strength`

Current truthful read:

- FSR is no longer active on the maintained `v4a` path
- but it still exists as a preserved non-`v4a` / legacy support surface

This is exactly the kind of residue the next support-path retirement gate should address.

### D. `symmetric_movement_sync_enabled` is no longer part of this gate

Current owner:

- `run_control.symmetric_movement_sync_enabled`

Current read:

- already rerooted honestly
- still active
- not a legacy support-path retirement target for the immediate next slice

## 3. Current cleanup has already advanced beyond the old PR #8 wording

Engineering read:

- Governance comment 1 was directionally correct
- but the codebase has already advanced materially past that checkpoint

The most important consequence is:

- the next gate should **not** reopen old broad questions such as “should `v4a` replace `v3a`?”
- that question is already practically settled in the maintained mainline

The real remaining questions are narrower:

1. how to retire `test_mode` honestly
2. how to retire preserved legacy support surfaces such as FSR
3. how to handle the active old-named cohesion seam without either:
   - silently deleting it
   - or leaving it indefinitely as mixed-era truth confusion

## 4. Recommended next bounded retirement slices

### Slice 1 — `test_mode` retirement / reroot

Target question:

- should `test_mode` be retired entirely in favor of explicit maintained flags, or reduced to a simpler observer/diagnostic toggle?

Recommended direction:

- remove its misleading “legacy selector permission” meaning
- either:
  - replace it with explicit maintained observer/diagnostic controls
  - or reduce it to a much smaller maintained run/observer mode owner

Reason:

- current mainline no longer needs it for movement support-path branching

### Slice 2 — FSR support-path retirement

Target question:

- should FSR now be fully retired from the maintained tree, given active `v4a` no longer consumes it and maintained non-`v4a` movement execution is already gone?

Recommended direction:

- yes, this looks like the next clean deletion candidate

Reason:

- it is now mostly a support-path shell
- its public surface is increasingly misleading

### Slice 3 — active cohesion seam truth / reroot plan

Target question:

- should the active old-named cohesion seam be:
  - retained but renamed/re-described honestly
  - rerooted into a more neutral maintained owner
  - or later replaced by a cleaner maintained cohesion carrier?

Recommended direction for the immediate next turn:

- planning / truth map first
- no silent rename or broad redesign yet

Reason:

- this seam is still active and exported in trajectory/readout
- deleting or renaming it casually would violate ownership truth

## 5. Explicit non-goals for the next gate

The next gate should **not** be widened into:

- compute optimization
- targeting redesign
- broad Formation redesign
- locomotion redesign
- silent runtime architecture rewrite

It should stay:

- support-path retirement
- mainline truth tightening
- bounded owner rerooting

## 6. Recommended execution order

1. `test_mode` retirement planning and bounded implementation  
2. FSR support-path retirement  
3. active cohesion seam truth/reroot planning  
4. only after that, decide whether the cohesion seam becomes the next real cleanup carrier

## 7. Bottom line

The largest cleanup phase has already moved the project beyond the older PR #8 checkpoint.

The next honest gate is not “more generic cleanup.”
It is:

- retire `test_mode` honestly
- retire remaining preserved support surfaces such as FSR
- then handle the still-active old-named cohesion seam with a separate bounded truth/reroot decision
