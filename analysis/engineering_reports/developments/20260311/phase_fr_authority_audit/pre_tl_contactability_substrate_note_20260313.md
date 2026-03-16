# Pre-TL Contactability Substrate Note

Date: 2026-03-13
Status: Engineering concept / boundary note
Scope: Clarify what kind of low-level target substrate can be prepared before future `TL` activation, without pre-committing future `TL` semantics.

## 1. Why this note exists

The post-contact low-level symmetry audit has now reached the fleet-level enemy-reference problem.

Current evidence indicates:

- raw `nearest-enemy` is too sharp for mirrored diagnostic neutrality
- smoother local surrogate families look more promising
- a fully global surrogate such as pure `enemy centroid` is cleaner on symmetry, but may be too global to stand as the long-term neutral default without further design judgment

This creates a boundary problem:

- engineering still needs some low-level direction substrate now
- but future `TL` must retain ownership of targeting-preference semantics later

So the present task is not to define future `TL` behavior.
It is to define what a better **pre-TL substrate** should look like.

## 2. Required boundary

Current engineering boundary should be:

- future `TL` owns targeting horizon and targeting preference semantics
- current low-level audit owns only the neutrality, smoothness, and symmetry-safety of the pre-TL substrate

The current default pre-TL substrate should therefore be interpreted as:

```text
the future TL=5 baseline reference
```

Meaning:

- the substrate exists at the shared low level
- it is not itself future `TL`
- it provides the neutral reference that a future `TL` may later modulate away from

So the current task is not to predefine future targeting preference.
It is to establish what the shared baseline should look like before future `TL` bias is applied.

That means current low-level work may answer:

- how sharp is the current default surrogate?
- how mirror-sensitive is it?
- how smooth should the low-level field be?
- how local should the low-level field be?

But current low-level work may **not** answer:

- which target type is doctrinally correct
- what kind of target future `TL` should prefer
- whether the fleet should prefer nearest enemy, main cluster, weak point, high-value target, tempo node, or any other higher-semantic objective

## 3. Recommended concept direction

Governance has recommended moving away from a discrete "fire-coverable enemy set" framing and toward a more continuous concept.

Engineering agrees.

The most useful current concept is:

**short-horizon contactable threat field**

or equivalently:

**short-horizon contactability weight map**

This means the low-level substrate should not primarily answer:

- "which exact enemy should I target?"

Instead, it should estimate a smoother low-level structure such as:

- which enemy directions are more contactable in the short horizon
- which nearby enemy regions are more reachable / pressurable / contactable
- how strongly different local enemy regions should contribute to a current fleet-level direction reference

## 4. What the field may use

At the current low-level stage, the field should remain physically grounded and semantically light.

Acceptable low-level inputs include:

- current enemy positions
- distance / local proximity
- short-horizon approach geometry
- very light contactability or spacing-feasibility approximations
- very light range-based contactability effects

These are still substrate-level quantities.

## 5. What the field must not silently encode

The pre-TL substrate should **not** silently encode higher target-value semantics.

It should not directly encode:

- who is more valuable
- who is more fragile
- who is the main cluster in the doctrinal sense
- who is more worth attacking
- what a given personality would strategically prefer

Those belong to future `TL` or higher mechanism layers.

## 6. Why raw `nearest-enemy` is not a good neutral pre-TL default

Current engineering evidence suggests raw `nearest-enemy` is too sharp because:

- it is a single-point selector
- it sits on top of very thin local candidate margins
- it can amplify tiny geometric perturbations into fleet-level direction changes
- in mirrored close-contact openings it behaves more like an asymmetry amplifier than a neutral substrate

So `nearest-enemy` remains useful as:

- a lower-bound / sharp-end reference

But not as:

- the preferred neutral pre-TL substrate candidate

## 7. Why pure global centroid is not a full answer either

Pure `enemy centroid` is attractive because:

- it is very smooth
- it is highly mirror-stable

But it also risks being too global because:

- it can wash out local contact structure
- it may remove too much local encounter character
- it can alter contact timing and local interaction style

So pure centroid is better understood as:

- a symmetry-clean upper reference

not automatically as:

- the future doctrinal answer

## 8. Why continuous local/contactability-based field is more promising

A continuous local field sits between the two extremes:

- less sharp than single nearest-unit selection
- less global than full enemy-centroid reference
- more local-contact preserving
- more extensible for future `TL`

This is why local smooth families such as:

- nearest-k centroid
- local weighted centroid
- local cluster reference
- more general short-horizon contactability maps

are currently the most plausible pre-TL substrate candidates.

## 8.0 Tie-break by iteration order is a real low-level risk

One additional bounded audit finding should be made explicit.

Current fleet-level enemy-reference logic still contains a low-level tie-break risk:

- when multiple enemy units are equally good, or nearly equally good, under the current geometric criterion
- the selected result can still depend on stable iteration order rather than on a more neutral physical secondary rule

In practice this appears in two closely related forms:

1. raw `nearest-enemy`
   - exact distance ties fall back to the first encountered enemy in iteration order

2. smoothed local families such as `nearest-k`
   - the boundary of the selected local set can still depend on stable sort order when several enemies sit at effectively equal local distance

This matters most in mirrored openings, where:

- multiple candidates may be geometrically equivalent
- the low-level list order then becomes an unintended hidden selector

So the current pre-TL problem is not only:

- "is the surrogate too sharp?"

It is also:

- "when geometric preference is degenerate, does the substrate fall back to arbitrary ordering rather than to a neutral physical continuation rule?"

This is one reason raw `nearest-enemy` remains a poor neutral substrate candidate.
It is also a reason to keep even `nearest-k` families under bounded scrutiny.

## 8.1 Refined quality criteria for a neutral pre-TL substrate

Governance has now clarified that the next step should not be "pick a winner," but refine the comparison criteria for neutral substrate quality.

Engineering therefore treats the following as the current core quality criteria:

1. **symmetry safety**
   - under mirrored same-force diagnostic conditions, the substrate should not amplify tiny local perturbations into early directional asymmetry

2. **smoothness**
   - the substrate should vary continuously under small geometric changes
   - it should avoid brittle single-point jumps where a thin nearest-candidate margin can abruptly rotate the fleet-level direction reference

3. **locality / contact relevance**
   - the substrate should still reflect nearby short-horizon contact structure
   - it should not become so global that local encounter geometry disappears

4. **extensibility for future TL**
   - the substrate should be easy for future `TL` to bias or weight
   - it should not silently lock in one future targeting doctrine

5. **degeneracy safety**
   - when multiple local enemies are equally plausible under mirrored geometry
   - the substrate should degrade gracefully
   - it should not silently hand control to arbitrary unit ordering

These criteria are intentionally about substrate quality, not about tactical cleverness.

## 8.2 Current bounded comparison readout

A bounded in-memory comparison was run under the active mirrored close-contact diagnostic fixture across:

- `nearest-1`
- `nearest-5`
- `weighted_local`
- `local_cluster`
- `centroid`

The comparison remained intentionally limited to substrate-quality readouts:

- target-direction symmetry safety
- direction smoothness
- early contact relevance
- early orientation skew
- movement-phase mirror error

Current engineering reading is:

### `weighted_local`

Strengths:

- strongest symmetry safety among the local families tested
- strongest smoothness among the local families tested
- low early orientation skew

Limitation:

- it sits extremely close to pure global centroid behavior in the current fixture
- so its neutrality is strong, but its locality may already be too diluted

Current reading:

- promising as a symmetry-clean local-weight family
- but at risk of becoming too global to serve as the preferred local pre-TL default

### `nearest-5`

Strengths:

- much smoother and more symmetry-safe than raw `nearest-enemy`
- remains more local-contact preserving than pure centroid
- delays the first engaged-count split relative to raw `nearest-enemy`

Limitation:

- not as symmetry-clean as `weighted_local` or pure centroid
- still needs comparison against richer local-weight families

Current reading:

- strongest current balance candidate among the explicitly local families tested so far

### `local_cluster`

Strengths:

- better than raw `nearest-enemy` on several symmetry/smoothness dimensions
- retains local structure more than pure centroid

Limitation:

- clearly less smooth than `nearest-5` and `weighted_local`
- still close enough to cluster-selection semantics that it needs continued boundary scrutiny

Current reading:

- still admissible as a candidate family
- but remains more governance-sensitive than `nearest-5` or plain local weighting

### `centroid`

Strengths:

- cleanest upper reference on symmetry and smoothness

Limitation:

- too global to treat as an unqualified local substrate answer

Current reading:

- keep as symmetry-clean upper reference
- do not promote as doctrinal default

### `nearest-enemy`

Current reading:

- remains a useful sharp lower-bound reference
- but is not an acceptable ideal neutral pre-TL default under mirrored contact-entry diagnostics

## 9. Future TL interface

Future `TL` should later be allowed to write semantics onto this substrate.

That future layer may legitimately own:

- targeting horizon semantics
- targeting preference semantics
- selective emphasis among local field components

Examples of future `TL`-level semantics may later include:

- preferring nearer local contactable regions
- preferring denser local enemy structure
- preferring main-cluster direction
- preferring weak points
- preferring tempo / continuation opportunities

Current low-level substrate should provide only:

- a smoother
- more neutral
- more symmetry-safe
- more auditable

contactability structure on top of which those later semantics can be added.

## 9.1 Why local cluster reference needs stricter scrutiny

`local cluster reference` remains inside the acceptable candidate region only under stricter discipline.

The reason is simple:

- clustering can stay low-semantic if it only stabilizes local contact geometry
- but it can also drift upward very quickly into implicit doctrinal judgment

The following are acceptable cluster-like roles at the current pre-TL stage:

- smoothing noisy local enemy geometry
- stabilizing short-horizon contactable regions
- aggregating nearby enemy structure into a less brittle local field reference

The following are **not** acceptable inside current pre-TL cluster logic:

- deciding which cluster is the "real" main body in a doctrinal sense
- preferring a weak or valuable cluster
- preferring a strategically important cluster
- silently selecting a cluster because it "should" be attacked

So cluster-based substrate work is permitted only if it remains:

- physically grounded
- continuous
- locally contactability-centered
- semantically light

Otherwise it stops being substrate preparation and starts becoming early `TL`.

## 10. Required discipline statement

The following discipline should apply to this whole line:

> A single parameter, a single mechanism bias, or a single intermediate target substrate must be understood only as a tendency / bias / weighting structure, not as a guaranteed battlefield signature.
> Observable target-selection patterns, formation changes, event topology, and battle outcomes remain emergent outputs of multiple parameters and runtime mechanisms interacting together.

This prevents the pre-TL substrate from being misread as future `TL` behavior.

## 11. Bottom line

Current work should proceed only as:

- pre-TL substrate preparation

It should not proceed as:

- early `TL` activation
- surrogate freeze
- doctrinal targeting definition

The correct current direction is a smoother, more local, more continuous contactability field that future `TL` may later use, bias, and reinterpret without finding that its authority has already been silently pre-occupied.
