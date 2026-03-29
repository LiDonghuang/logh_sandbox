# Step 3 3D Two-Layer Spacing Opening Scope Note

- Engine Version: `dev_v2.0`
- Modified Layer: `analysis / structural opening note only`
- Affected Parameters: none in committed runtime
- New Variables Introduced: none
- Cross-Dimension Coupling: clarifies a possible future spacing split without opening implementation
- Mapping Impact: none
- Governance Impact: opens the two-layer spacing line in structural / diagnostic form only
- Backward Compatible: yes
- Summary: defines the opening scope for discussing `expected/reference spacing` versus `low-level physical minimum spacing`, clarifies current maintained-path overload points, and keeps implementation explicitly closed

## Purpose

This note responds to the governance opening memo for the Step 3 3D two-layer spacing discussion line.

Its role is narrow:

- define what the new discussion line means
- clarify what is currently overloaded
- identify likely ownership candidates
- state what remains closed

It is **not** an implementation proposal.

It is **not** a runtime parameter approval.

## 1. Current Repo Read of `expected/reference spacing`

In current repo language, `expected/reference spacing` should be read as:

- the intended spacing implied by the reference formation slots
- the spacing that the runtime is trying to preserve or restore relative to `expected_position` / slot offsets
- a formation-side / restore-side concept, not simply a collision floor

In the present maintained path, this concept is only implicit.

It is currently expressed indirectly through:

- initial slot placement geometry in `test_run/test_run_scenario.py`
- the expected-position fixture surface
- restore behavior relative to those expected slots inside `runtime/engine_skeleton.py`

So the concept already exists in practice, but it is not yet represented as a deliberately separated surface.

## 2. How It Differs From Low-Level Physical Minimum Spacing

`low-level physical minimum spacing` should be read as:

- the minimum non-overlap / local separation floor
- the spacing used by local separation and post-movement projection protection
- a physical-runtime floor, not a direct statement of intended formation geometry

So the intended distinction is:

- expected/reference spacing = what the formation is trying to mean
- low-level physical minimum spacing = what the runtime must not physically violate

That distinction is now opened for discussion, but not yet implemented.

## 3. What Is Currently Overloaded Into the Same Radius

The maintained path currently overloads one spacing radius across several jobs.

### A. Initial formation spawn spacing

`test_run/test_run_scenario.py`

- `build_initial_state(...)`
- `build_single_fleet_initial_state(...)`
- both consume `unit_spacing`
- that `unit_spacing` currently comes from `runtime min_unit_spacing`

### B. Runtime low-level separation / projection floor

`test_run/test_run_scenario.py`
- passes the same value into `runtime_cfg["contact"]["separation_radius"]`

`test_run/test_run_execution.py`
- constructs `EngineTickSkeleton(..., separation_radius=...)`

`runtime/engine_skeleton.py`
- uses `self.separation_radius` for:
  - ally separation accumulation
  - post-movement projection minimum spacing

### C. Cohesion / connectivity scale

`runtime/engine_skeleton.py`

- v2/v3 cohesion/connectivity radii use `self.separation_radius` or multipliers of it

### D. Fixture restore deadband

`runtime/engine_skeleton.py`

- `fixture_restore_deadband = self.separation_radius * ratio`

So the current maintained path is not using one clean spacing role.

It is using one overloaded radius for:

- reference spawn spacing
- physical non-overlap floor
- cohesion/connectivity scale
- restore deadband scale

## 4. Ownership Candidates If This Line Advances Later

If the line advances later, the strongest current ownership candidates appear to be:

### A. `expected/reference spacing`

Best current ownership candidate:

- formation reference / restore-policy boundary

Why:

- it describes intended slot geometry
- it should remain tied to expected slots, not to collision floor
- it should not silently become a legality-owned or viewer-owned field

### B. `low-level physical minimum spacing`

Best current ownership candidate:

- movement runtime / low-level physical layer

Why:

- it is directly used for local non-overlap and spacing protection
- it behaves like a physical floor, not a reference-geometry statement

### C. What does **not** currently look right

- mapping ownership
- legality ownership
- viewer ownership

Current evidence still points earlier than those layers.

## 5. Minimal Diagnostic Work Still Needed Before Any Implementation Opening

Before any implementation opening, the following remain necessary:

1. keep at least one discriminating probe where the spacing roles are decoupled one at a time
2. preserve human-readable evidence for each substantive probe
3. confirm whether the decoupling effect remains strong under at least one more bounded comparison path
4. continue separating:
   - movement-vs-restore asymmetry
   - overloaded spacing-radius amplification

The current evidence is already strong enough for discussion, but still not enough for unconditional mechanism rollout.

## 6. What Remains Explicitly Closed

Even with this line now opened, the following remain closed:

- immediate committed runtime implementation
- new public spacing parameter rollout
- two-layer spacing mechanism merge
- geometry hardcoding or rectangle locking
- legality redesign through the back door
- viewer ownership widening
- doctrine / personality recoupling
- broad movement rewrite justified only by this opening

## 7. Current Recommended Read

The current best bounded read is:

1. early standard-rectangle stretching still primarily reads as an ordinary-transit movement-vs-restore issue
2. the overloaded spacing radius now also reads as a major amplifier
3. expected/reference spacing and low-level physical minimum spacing are now legitimately open as distinct concepts
4. the line should stay structural and diagnostic-first until a later governance decision explicitly opens implementation-prep or implementation

## Bottom Line

This opening note should be read as:

- the project now has enough evidence to discuss two-layer spacing **deliberately**
- the project does **not** yet have authorization to implement two-layer spacing by momentum

So the next correct posture remains:

- separate the concepts clearly
- probe carefully
- keep implementation closed until explicitly reopened
