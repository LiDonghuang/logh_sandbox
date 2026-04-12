# PR6 / dev_v2.1 Cleanup Opening and Governance Request

Status: governance request / cleanup opening memo  
Date: 2026-04-04  
Scope: subtraction-first cleanup planning after recovered `dev_v2.1` anchor  
Authority: discussion / sequencing request only; not merge approval, not default-switch approval

## I. Intent

This memo asks Governance to review and approve a dedicated cleanup line after the
current recovered `dev_v2.1` anchor.

The cleanup goal is not broad redesign.

The goal is:

- reduce mixed-era mechanism overlap
- shrink stale human-facing claims
- reconnect ownership honestly
- prepare later subtraction-first retirement of old `2D` / `v3a` / `v3_test` families

This cleanup line should remain distinct from:

- battle doctrine expansion
- richer fire-model redesign
- ship-class doctrine
- merge/default-switch discussion

## II. Current read before cleanup

Current accepted anchor:

- `dev_v2.1`

Current accepted ordering from Governance:

1. stabilize targeting  
2. decouple `restore_strength` from the old `v3_test` carrier  
3. then retire old `2D` / `v3a` / `v3_test` families by subtraction-first cleanup

Engineering accepts that order.

Current additional read:

- stale claims and ownership ambiguity are already obstructing reliable reasoning
- so a narrow cleanup-opening package should begin now at the documentation /
  ownership-map / stale-claim level
- major structural retirement still stays after the `restore_strength`
  decoupling step

## III. Immediate cleanup package

Engineering proposes the following immediate cleanup package.

### A. Stale comments / stale settings claims

Correct any active comments or settings reference text that still implies:

- `v4a` no longer depends on the old carrier
- `v4a` directly reads `v3a.centroid_probe_scale`
- older explanatory text still matches current active ownership

This package has already started locally with:

- `test_run/test_run_v1_0.settings.comments.json`
- `test_run/test_run_v1_0.settings.reference.md`

### B. Active ownership map

Maintain one short current-state ownership map that explicitly states:

- current targeting owner
- current `restore_strength` owner
- still-live transitional `v3a` / `v3_test` dependencies
- no-longer-active Layer-A local-enemy carriers

Current file:

- `analysis/engineering_reports/developments/20260404/step3_3d_pr6_active_ownership_map_20260404.md`

### C. No new doctrine during cleanup opening

This cleanup opening should not:

- widen targeting doctrine
- reopen battle hold semantics
- reopen formation doctrine
- silently move new runtime ownership

It should remain subtraction-first and map-first.

## IV. Proposed cleanup sequence

Engineering proposes the following detailed cleanup sequence.

### Phase 1. Documentation and ownership hygiene

Requested outcome:

- current human-facing surfaces stop lying about active ownership

Includes:

- stale comment cleanup
- ownership map maintenance
- retirement-status wording cleanup

Expected scope:

- docs / comments / settings reference only

### Phase 2. `restore_strength` decoupling

Requested outcome:

- `v4a.restore_strength` no longer depends on the old `v3_test`
  centroid-probe carrier

Engineering read:

- this is the first real structural cleanup step
- it must occur before `v3a` retirement

Expected work shape:

- establish one true `v4a` owner
- paired comparison against the recovered anchor
- only then remove the old carrier dependence

### Phase 3. Runtime / harness old-family retirement

Requested outcome:

- subtraction-first retirement of old `2D` / `v3a` / `v3_test` mechanism families

Expected targets:

- obsolete `v3a` movement-era carriers still left in active surface
- old `v3_test` bridge dependence once decoupling is complete
- stale harness compatibility branches
- legacy local-enemy Layer-A substrate family still carried only as historical material

### Phase 4. Historical preservation handling

Requested outcome:

- active default surfaces become smaller
- historical material stays accessible without polluting active ownership

Acceptable preservation options:

1. local retired folder  
2. older frozen branches

Engineering does not recommend indefinite silent mixed-era fallback.

## V. Boundaries

Engineering requests Governance to explicitly keep the following boundaries:

- no merge approval
- no default-switch approval
- no new battle doctrine expansion inside cleanup PRs
- no new fire-model complexity during cleanup opening
- no architecture-adjacent helper growth disguised as simplification

## VI. Parameter taxonomy note

Human has already identified a likely future need to classify `v4a` parameters
more cleanly, for example across:

- unit behavior
- formation specification
- battle-relationship / higher-level control

Engineering agrees this is likely needed.

But Engineering recommends deferring final parameter taxonomy until:

1. targeting is stabilized  
2. `restore_strength` is decoupled  
3. old mechanism families are reduced

Current read:

- taxonomy work before cleanup would likely freeze the wrong surface

## VII. Governance ask

Engineering requests Governance confirmation on the following:

1. accept this cleanup line as a dedicated PR-specific line  
2. accept the sequence:
   - docs / ownership hygiene
   - `restore_strength` decoupling
   - then old-family retirement
3. keep cleanup PRs subtraction-first and doctrine-light  
4. treat future parameter taxonomy as deferred until the old mechanism surface is smaller

## Bottom Line

Engineering proposes a dedicated cleanup PR line that is:

- subtraction-first
- ownership-first
- doctrine-light
- explicitly sequenced after the recovered `dev_v2.1` anchor

The requested cleanup order is:

1. stale claims + ownership map  
2. `restore_strength` decoupling from old carrier  
3. subtraction-first retirement of old `2D` / `v3a` / `v3_test` families
