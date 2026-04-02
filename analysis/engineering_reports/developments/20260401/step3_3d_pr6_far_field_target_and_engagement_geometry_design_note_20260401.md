# Step 3 3D PR #6 Design Note
## Far-Field Battle Target and Engagement Geometry Stack

Status: design / governance-alignment note only  
Scope: PR `#6` next carrier clarification before implementation  
Authority: engineering design note for Human + Governance review  
Non-scope: implementation approval, merge approval, default switch approval, runtime-core rewrite

---

## I. Purpose

This note defines the next design correction on PR `#6` after the latest Human + Governance discussion.

The branch should still be read as:

- an active review / learning line
- not a solved formation line
- not a merge-ready baseline

The current purpose is narrower:

- clarify the next carrier structure
- set implementation priority honestly
- prevent further patch-stacking on top of the wrong battle target read

This note therefore does **not** propose immediate code changes.

It defines what should be corrected first, what should remain later, and where the current seams now belong.

---

## II. Current Accepted Read

The following should now be treated as accepted background.

### 1. Two current seams are directionally correct

The following should not be casually rolled back:

- fleet-level battle standoff distance `d*`
- unit-level attack-direction-aware speed envelope

These seams are now read as:

- valuable
- directionally correct
- still bounded and incomplete

They mainly exposed the next battle problem more clearly rather than failing on their own.

### 2. Far-field battle target is still being read too locally

Human + Governance now accept that far-field battle target should first read as:

- global enemy relation
- plus standoff distance `d*`

and **not** as:

- early local enemy reference

The early stable divergence between battle and neutral long before contact strongly supports this read.

### 3. The main post-contact problem has also become clearer

The current post-contact battle problem should now be read as:

- post-contact front ownership failure

More precisely:

- the effective fire plane drifts
- the formation continues to preserve a pre-contact front too faithfully
- no honest front redefinition occurs
- no bounded shared local range-entry correction exists

This is why battle can settle into:

- wing-localized contact
- then persistent rotation around a local junction

### 4. `1 -> 4` is no longer enough as the only mismatch-critical read

Human's new `2 -> 4` observation matters.

It suggests:

- the current relative neatness of `1 -> 4` may contain symmetry luck
- the transition carrier still does not honestly own expansive transition continuity

So future mismatch-critical sanity should explicitly include:

- `1 -> 4`
- `2 -> 4`
- `4 -> 1`

not only the old pair.

---

## III. Priority Order

The next design priority should be:

### Priority 1. Fix far-field battle target semantics

Reason:

- this is already strongly diagnosed
- it is structurally earlier than the post-contact problem
- it risks contaminating every later read if left dirty

### Priority 2. Clarify the post-contact engagement geometry stack

Reason:

- this is the next real battle problem now exposed
- but it should not be implemented first while far-field target is still impure

### Priority 3. Re-observe transition cases after far-field cleanup

Especially:

- neutral `1 -> 4`
- battle `1 -> 4`
- battle `2 -> 4`
- battle `4 -> 1`

This step is necessary to distinguish:

- target-substrate false improvement
from
- real transition-carrier improvement

---

## IV. Layer A / B / C Stack

The battle line should now be organized explicitly as one stack with three layers.

### Layer A. Far-field pre-TL movement

Owns:

- global enemy relation
- fleet-level desired engagement distance `d*`
- approach / hold / pressure before local contact geometry matters

Does **not** own:

- local enemy selection
- nearest local cluster semantics
- post-contact fire-plane correction

### Layer B. TL / engagement geometry layer

Owns:

- locally relevant enemy geometry
- effective fire plane
- front reorientation signal
- bounded local range-entry reference

This layer is not just "who attacks whom."

It is the engagement-geometry layer that tells movement what battle geometry currently matters locally.

### Layer C. Movement realization

Owns:

- turning
- slowing
- approach realization
- hold realization
- consumption of Layer B signals

It does **not** own:

- a third local enemy logic
- independent nearest-enemy target invention

This stack is the current cleanest battle-geometry organization read.

---

## V. Far-Field Battle Target Correction

### A. Correct far-field read

Far-field battle target should now be read as:

- one global enemy relation
- one fleet-level desired standoff `d*`

The far-field target should no longer be driven primarily by:

- `nearest5_centroid`
- `weighted_local`
- `local_cluster`
- `soft_local_weighted`
- `soft_local_weighted_tight`

These are all local enemy semantics and should not remain active in far-field movement.

### B. What should remain in far-field

A minimal honest far-field battle read may still use:

- own fleet centroid / morphology axis
- enemy fleet centroid / body relation
- own formation scale
- enemy formation scale
- `attack_range`
- `d*`

This still allows:

- approach
- hold
- pressure

without prematurely localizing the target semantics.

### C. Where local enemy semantics should move

They should move behind an explicit later gate.

Provisional design read:

- local enemy semantics are disabled in Layer A
- they become available only after engagement geometry activates

### D. Provisional activation gate

The smallest honest gate should not yet be personality-driven.

A bounded first activation read can be:

- fleet-to-fleet distance has entered a bounded engagement corridor
or
- any unit-level engaged state now exists
or
- a contact / overlap / range-entry condition says local geometry is now physically relevant

The exact gate is still an implementation question.

But the semantic point is now fixed:

- local enemy semantics must be gated later
- not available during far-field approach by default

---

## VI. `d*` Read After the Correction

The correct way to preserve the new standoff seam is:

- keep `d*`
- clean the far-field target around it

The current preferred bounded read remains:

`d* = attack_range + self_w * own_scale + enemy_w * enemy_scale`

The precise scale term may continue to use current forward extent in the first bounded implementation cut.

The key point is not the exact scalar function.

The key point is:

- larger fleets should not be read as point masses charging one point

So the next implementation should preserve:

- `d*` as a fleet-level relation

while removing:

- far-field local substrate contamination

---

## VII. Post-Contact Front Ownership

### A. The corrected doctrine read

After contact begins, front should no longer remain loyal only to:

- pre-contact geometry
- pre-contact approach frame

Instead, front should gradually become responsible to:

- formation
- multiplied by effective fire plane

This is the current best long-term battle doctrine read.

### B. Why this is not a temporary patch

This should not be treated as:

- a case-specific correction
- or a cosmetic battle fix

It is more fundamental:

- once battle geometry becomes local and directional,
  front ownership must move with the battle geometry

Otherwise:

- only one wing continues to exchange fire
- the battle body remains misaligned with real engagement opportunity

### C. Dynamics requirement

Future front reorientation must be:

- bounded
- low-jump
- continuous
- not a high-frequency pivot

That is already a hard design boundary.

---

## VIII. Post-Contact Local Relaxation Re-Read

### A. What it should not be

It should not become:

- unrestricted nearest-enemy pursuit
- a third independent local enemy logic
- a hidden swarm fallback

### B. What it should be

It should be read as:

- a bounded local range-entry correction
- computed by Layer B
- consumed by Layer C

Meaning:

- engagement geometry decides where local range-entry pressure exists
- movement realization executes only a bounded correction toward that locally relevant engagement geometry

### C. Why this matters structurally

Runtime already has its own contact / target-assignment logic.

If post-contact local relaxation grows a third local enemy mechanism inside movement, the stack becomes:

- duplicated
- contradictory
- very hard to debug

So this line must be unified under Layer B rather than grown independently.

---

## IX. Reuse and Cleanup Principle

Future implementation should follow two explicit engineering rules.

### 1. Reuse existing seams before inventing new ones

Prefer reusing:

- current `d*` seam
- current engaged-target semantics
- current attack-direction-aware speed envelope
- existing combat-angle directional semantics

before adding new parallel logic.

### 2. Clean up replaced logic quickly

Once far-field target is redefined honestly:

- old early local substrate logic should not remain active by habit

Once Layer B becomes the engagement-geometry owner:

- movement-side duplicated local enemy logic should not remain hanging around

This is important for PR `#6`, because the branch already contains many valuable experiments and should not become a graveyard of half-retired semantics.

---

## X. Honest Touchpoint Assessment

### A. What can still stay in `test_run/`

The first far-field battle-target correction still looks honestly expressible in `test_run/`.

Reason:

- current battle target evaluation is already harness-owned there
- removing far-field local substrate usage is a harness-level carrier correction

So the next bounded implementation step can likely remain in:

- `test_run/settings_accessor.py`
- `test_run/test_run_scenario.py`
- `test_run/test_run_execution.py`
- `test_run` settings docs

### B. What may no longer stay honestly in `test_run/`

Once Layer B becomes real, the answer is less comfortable.

Reason:

- locally relevant enemy geometry
- effective fire plane
- engaged target semantics

already touch logic that lives close to runtime contact / combat organization.

So a fully honest Layer B may eventually require deeper touchpoints than `test_run/` alone.

This should be stated plainly now:

- `test_run-only` may remain honest for the next far-field correction
- it may stop being honest once engagement geometry becomes a real owned layer

That is not an implementation request yet.

It is simply the current most honest structural read.

---

## XI. Recommended Next Execution Order

### Round 1

Keep this note as the design alignment asset.

### Round 2

If Human approves implementation, first do only:

- far-field battle target cleanup
- preserve `d*`
- remove local enemy semantics from Layer A

### Round 3

Then re-observe:

- neutral `1 -> 4`
- battle `1 -> 4`
- battle `2 -> 4`
- battle `4 -> 1`

### Round 4

Only after that, if Human read still supports it, proceed to:

1. front reorientation
2. bounded local range-entry correction

in that order.

---

## XII. Bottom Line

The next carrier should be read as:

- keep `d*`
- clean far-field battle target first
- treat post-contact battle under one engagement geometry stack
- keep front reorientation as long-term doctrine
- treat local relaxation as a bounded Layer-B-to-Layer-C correction, not an independent targeting line

And the new Human `2 -> 4` read should now be treated as a mandatory sanity case, because it strongly suggests the current apparent partial success of `1 -> 4` may be partly accidental rather than evidence that expansive transition continuity is already owned honestly.
