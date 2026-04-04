# LOGH Sandbox

## PR #6 Fire Model Structure Design Note
## Battle Fire-Semantics Structuring Clarification

Status: design note only  
Scope: PR `#6` battle fire-semantics structuring before implementation  
Authority: engineering design note for Human review  
Non-scope: implementation approval, merge approval, default switch approval, runtime-core rewrite

---

## I. Purpose

This note refines the earlier:

- `fire angle vs targeting`

discussion into a cleaner structural proposal.

The narrower question is:

- should the next bounded battle correction continue as scattered score terms,
  or should it first be organized as an explicit **fire model** structure?

Current Human + Engineering read is:

- a dedicated `fire_model` structure is the cleaner direction

This note exists to explain why.

---

## II. Current Problem With the Existing Read

The previous bounded correction note already improved the battle read from:

- `hp_term + crowd_term + angle_term`

toward:

- `hp_term + expected_damage_term`

with:

- `expected_damage = base_damage * angle_quality * range_quality`

That is already a better merit read.

But if this is implemented only as a few extra terms added into scoring, the
repo will still have a structural weakness:

- selection semantics in one place
- realized damage semantics in another place
- range meaning partly implicit
- angle meaning partly duplicated

So the next refinement should not only be:

- "better score terms"

It should be:

- "one explicit fire-semantics owner"

---

## III. Proposed Structural Read

Introduce a bounded `fire_model` structure, conceptually parallel to how the
repo already distinguishes movement models such as:

- `v3a`
- `v4a`

The point is not model proliferation.
The point is:

- do not let battle fire semantics remain a pile of ad hoc score tweaks

The cleaner read is:

- one active fire model
- one shared semantics owner for:
  - target merit
  - realized fire quality

---

## IV. Minimum Candidate Models

The first structure can remain very small.

### A. `legacy_attack_range_only`

This model means:

- retain the old read where `attack_range` is the only public range term
- no explicit range-quality curve beyond current legacy semantics
- angle may still participate only in realized fire quality, as today

This model exists mainly for:

- fallback
- baseline preservation
- explicit naming of current legacy semantics

### B. `angle_range_v1`

This is the first bounded improvement model.

It should own:

- `max_range`
- `optimal_range`
- `angle_quality`
- `range_quality`
- `expected_damage`

with:

- `expected_damage = base_damage * angle_quality * range_quality`

This is the first honest model that lets:

- angle
- and distance

participate in a unified fire read.

---

## V. `attack_range` Fallback Rule

`attack_range` must remain valid as a fallback.

This is important because the repo already has active semantics built around
that field.

So the next structure should **not** silently reinterpret `attack_range`.

Preferred bounded read:

1. if a fire model explicitly defines:
   - `max_range`
   - `optimal_range`
   then use them
2. otherwise:
   - `max_range = attack_range`
   - `optimal_range = attack_range`

This means:

- old content still works
- old configs do not silently break
- the richer model can be introduced without pretending all ships already have
  richer weapon semantics

The important boundary is:

- `attack_range` remains fallback-compatible
- it does **not** silently become "optimal range" by default unless the active
  model says so

---

## VI. Why a `fire_model` Is Cleaner Than Loose Terms

### 1. Shared semantics for selection and damage

Without an explicit model, the repo risks drifting into:

- one angle meaning in target selection
- another angle meaning in damage
- implicit range logic in one path
- explicit range logic in another

With a `fire_model`, the cleaner read is:

- one directional/range semantics
- two bounded consumers

Consumer A:

- target merit

Consumer B:

- realized damage quality

That is much easier to reason about and maintain.

### 2. Easier bounded extension later

If future ship classes or richer weapon lines are added, the repo will likely
need a cleaner place to put:

- different range profiles
- different angle sensitivities
- different falloff rules

`fire_model` gives that expansion path without forcing those features now.

### 3. Cleaner separation from allocation logic

This structure also helps keep:

- primary target merit

separate from:

- later fire-allocation / diversification logic

So `crowd_term`, if still needed later, does not have to pollute the first
merit layer.

---

## VII. Suggested First `angle_range_v1` Read

This note recommends the smallest honest first read:

### A. `angle_quality`

Keep the existing broad semantics:

- attacker orientation vs attacker-to-target direction

Do not invent a second unrelated angle meaning.

### B. `range_quality`

Use a simple bounded first curve:

- full quality at or inside `optimal_range`
- linear falloff toward `0` at `max_range`

This is intentionally simple.

It is not a full doctrine of weapon performance.

### C. `expected_damage`

Compute:

- `base_damage * angle_quality * range_quality`

This then becomes available to both:

- target selection
- realized fire quality

with potentially different bounded weights

---

## VIII. How Selection Should Read Under This Structure

The next primary merit read should be:

- `target_merit = hp_term + expected_damage_term`

not:

- nearest-target pursuit
- crowding term mixed into first merit
- a large tactical target-selection doctrine

This remains intentionally narrow.

The first honest comparison should simply be:

1. how vulnerable is the target
2. how much damage do I expect to do to it

Only after that should the repo ask whether additional allocation control is
still needed.

---

## IX. What This Structure Should Not Become

This line should not immediately become:

- a broad ship-class redesign
- a rich weapon taxonomy
- repeated short-cycle retuning
- a hidden rewrite of battle doctrine

It should remain:

- bounded
- explicit
- fallback-compatible
- stabilizable after acceptance

---

## X. Touchpoint Judgment

This line is structurally closer to frozen runtime than `test_run`.

Reason:

- the true owner of target selection and realized fire quality is the active
  battle hot path

So while this note is design-only, the eventual honest implementation almost
certainly touches runtime semantics more directly than recent harness-side
carrier work.

That is not a reason to avoid the structure.
It is a reason to define it clearly before implementation.

---

## XI. Bottom Line

The earlier correction:

- `hp_term + expected_damage_term`

is still the right direction.

But the cleaner structural next step is:

- do not implement that as loose score tweaks alone
- instead introduce a bounded `fire_model` structure

with a first pair such as:

- `legacy_attack_range_only`
- `angle_range_v1`

and with:

- `attack_range` preserved as fallback

This gives the repo one explicit owner for battle fire semantics, keeps
selection and realized damage aligned, and creates a cleaner path for later
extension without forcing that extension now.

