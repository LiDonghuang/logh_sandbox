## PR9 Phase II - Unit-Side Owner Language and Settings-Surface Cleanup Record

Date: 2026-04-22  
Scope: owner-language / settings-surface cleanup only  
Status: applied without runtime rewiring

**Line classification:** Owner-language / surface-cleanup line  
**Owner classification:** mixed-layer clarification; runtime wiring unchanged  
**Honest claim boundary:** this record may claim owner-language correction and settings/surface reclassification; it may not claim runtime rewiring, target-owner redesign, locomotion redesign, or module split

### 1. Battle read first

This cleanup was not done to make the code look tidier.

It was done because battle behavior was being misread.

Before this cleanup, two kinds of confusion were still easy:

- Human could read some live Unit-local maneuver surfaces as if they were still
  fleet/reference-side doctrine owners
- Human could also over-read names like `attack_speed_backward_scale` as though
  the runtime already had literal backward-with-front-preserved motion

That language drift matters because it confuses the battle picture:

- what is fleet authorization
- what is Unit-side realization
- what is only a transitional carrier or settings surface

### 2. One-sentence conclusion

The cleanup now makes two things explicit:

- the current `local_desire` experimental family is a test-only Unit-local
  maneuver / `back_off_keep_front` behavior-line family
- the `runtime.movement.v4a.engagement.*` family is still under a historical
  name, but its practical job is transitional Unit-side engaged maneuver-speed
  shaping, not fleet/reference-side doctrine ownership

### 3. Exact owner-language changes made

Changed files:

- [test_run/test_run_v1_0.settings.reference.md](/E:/logh_sandbox/test_run/test_run_v1_0.settings.reference.md)
- [test_run/test_run_v1_0.settings.comments.json](/E:/logh_sandbox/test_run/test_run_v1_0.settings.comments.json)

Applied owner-language changes:

1. `runtime.physical.local_desire.*`

- now described as:
  - test-only
  - experimental
  - Unit-local maneuver / `back_off_keep_front` behavior-line family
- explicitly not described as:
  - maintained doctrine
  - literal backward-with-front-preserved locomotion capability

2. `runtime.movement.v4a.engagement.*`

- now described as:
  - historical surface name
  - practical transitional Unit-side engaged maneuver-speed shaping
- explicitly not described as:
  - fleet/reference-side doctrine ownership

3. `attack_speed_backward_scale`

- now explicitly documented as:
  - bounded speed allowance when attack direction lies behind current facing
- explicitly not documented as:
  - true backward-motion capability

### 4. Exact settings/surface reclassifications made

The reclassification in this cleanup is language/surface-level rather than key
path migration.

Reclassified surfaces:

1. `runtime.physical.local_desire.*`

- reclassified in wording from a generic local-desire experimental branch to a
  clearer test-only Unit-local maneuver / behavior-line family

2. `runtime.movement.v4a.engagement.engaged_speed_scale`
3. `runtime.movement.v4a.engagement.attack_speed_lateral_scale`
4. `runtime.movement.v4a.engagement.attack_speed_backward_scale`

- reclassified in wording from a surface that can be casually read as
  fleet-side `v4a engagement doctrine`
- to a surface that should now be read as:
  - transitional Unit-side engaged maneuver-speed shaping

### 5. Explicit confirmation of what did not change

Runtime wiring stayed unchanged.

Not changed in this cleanup:

- no key path move
- no settings loader rewiring
- no scenario-builder rewiring
- no target-owner redesign
- no locomotion redesign
- no module split

### 6. How this cleanup reduces misreading

This cleanup should reduce three recurring misreads.

#### 6.1 Misreading Unit-local maneuver as fleet doctrine

What changed:

- the experimental `local_desire` surfaces are now described as test-only
  Unit-local maneuver surfaces

Why that helps:

- Human can more accurately separate:
  - fleet-authorized back-off envelope
  - Unit-realized maneuver response

#### 6.2 Misreading historical `v4a.engagement` naming as proof of current owner

What changed:

- the reference and comments now state plainly that this family lives under a
  historical surface name but does Unit-side engaged maneuver-speed work

Why that helps:

- Engineering and Governance can discuss these knobs as transitional Unit-side
  surfaces without pretending the current key path is already the final public
  classification

#### 6.3 Misreading `attack_speed_backward_scale` as true backward locomotion

What changed:

- the comments now explicitly say this is not literal backward-motion
  capability

Why that helps:

- it keeps the current behavior line separate from the future locomotion
  capability gate

### 7. Shortest conclusion

This cleanup made the public reading of the active path more honest:

- `local_desire` experimental surfaces are now clearly test-only Unit-local
  maneuver / behavior-line surfaces
- `runtime.movement.v4a.engagement.*` is now clearly documented as a
  transitional Unit-side maneuver-speed family under a historical name
- runtime wiring did not change

That should make Human, Engineering, and Governance more likely to read the
same battle behavior through the same layer boundaries.
