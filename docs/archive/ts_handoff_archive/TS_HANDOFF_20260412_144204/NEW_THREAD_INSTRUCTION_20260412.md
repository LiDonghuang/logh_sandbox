# New Thread Instruction - PR #9 Formation-Only

## Purpose

This instruction is for the next thread that will continue `PR #9` on branch
`eng/dev-v2.1-formation-only`.

The new thread is **not** a cleanup thread.
It is a **formation-only mechanism optimization and boundary-clarification thread**.

Use this document together with:

- [TS_HANDOFF_20260412_144204.md](/e:/logh_sandbox/docs/archive/ts_handoff_archive/TS_HANDOFF_20260412_144204/TS_HANDOFF_20260412_144204.md)
- [Formation_Owner_Path_Audit_20260412.md](/e:/logh_sandbox/analysis/engineering_reports/developments/20260412/Formation_Owner_Path_Audit_20260412.md)
- [pr9_formation_cold_shell_subtraction_shortlist_note_20260412.md](/e:/logh_sandbox/analysis/engineering_reports/developments/20260412/pr9_formation_cold_shell_subtraction_shortlist_note_20260412.md)
- [pr9_formation_coarse_body_boundary_lock_note_20260412.md](/e:/logh_sandbox/analysis/engineering_reports/developments/20260412/pr9_formation_coarse_body_boundary_lock_note_20260412.md)
- PR #9 governance comment:
  `Governance instruction - Formation-only direction on PR #9`

## 1. Current Formation Reality

The maintained active path already moved past cleanup and owner recovery.
`PR #9` now deals with a narrower but harder question:

- what Formation should still own
- what Formation should stop owning
- what should later become locomotion responsibility instead

### Active maintained owner reality

The main active Formation burden is currently in [engine_skeleton.py](/e:/logh_sandbox/runtime/engine_skeleton.py), especially:

- `_resolve_v4a_reference_surface(...)`
- `_prepare_v4a_bridge_state(...)`
- `_evaluate_target_with_v4a_bridge(...)`

These areas currently mix together:

- coarse-body geometry
- unit-level shaping carriers
- transition budgeting
- partial movement compensation
- terminal / hold residue

`test_run` currently acts mainly as carrier / preparation surface, not primary runtime owner:

- [test_run_execution.py](/e:/logh_sandbox/test_run/test_run_execution.py)
- [test_run_scenario.py](/e:/logh_sandbox/test_run/test_run_scenario.py)

### Governance-aligned coarse-body target

Formation should trend toward a simpler coarse-body owner that keeps only:

- body center
- front axis
- forward extent
- lateral extent

Future thickness is only a reserved possibility, not an active current target.

### What is still overloaded today

Current Formation still appears to own too much:

- exact slot / expected-position ontology
- band identity remnants
- center-wing shaping baggage
- terminal / hold residue
- transition-budget layers
- partial speed / movement compensation

This is why the next thread should not think in terms of "small cleanup".
The real task is boundary correction.

## 2. Latest Audit Conclusions

### Strong deletion candidates

These have no verified maintained reader and match the intended shrinkage direction:

- `band_identity_by_unit`
- `initial_material_forward_phase_by_unit`
- `initial_material_lateral_phase_by_unit`

### Keep for now

These should stay for now:

- `formation_terminal_latched_tick`
- `formation_hold_latched_tick`
- `formation_hold_*`

Reason:

- Human explicitly wants hold preserved as a future mechanism family
- `formation_hold_*` still has deeper runtime branches and is not safely classifiable as dead

### Important interpretation

Do **not** treat these as the same thing:

- `formation_hold_*`
- `frozen_terminal_*`

More accurate read:

- `formation_hold_*` = runtime formation-state shell
- `frozen_terminal_*` = fixture expected-position frame-freeze shell

They are related in family, but not simple battle-vs-neutral mirrors.

## 3. Recommended Next Work

Follow governance order strictly.

### Step 1. Finish the cold-shell truth audit as a concise note

Do this before deleting code.

Goal:

- make the subtraction shortlist explicit
- separate "safe deletion candidate" from "inactive shell pending decision"

Reason:

- this keeps the thread grounded in code-path truth
- it avoids prematurely deleting hold / terminal structure that may still be needed conceptually

### Step 2. Write the coarse-body boundary lock

Make the boundary explicit in code terms:

- what Formation should continue to own
- what is no longer acceptable as Formation-owned baggage

Reason:

- without this boundary, later edits will drift into local cleanup or accidental doctrine

### Step 3. Only then propose locomotion separation

After the boundary is explicit, propose how current transition / compensation burden should move out of Formation.

Reason:

- otherwise the thread will collapse back into "Formation keeps everything and grows another helper layer"

### First likely code slice after approval

After Human review of steps 1-2, the most bounded first code slice is:

- delete `band_identity_by_unit`
- delete `initial_material_forward_phase_by_unit`
- delete `initial_material_lateral_phase_by_unit`

Do not mix that slice with hold / terminal restructuring.

## 4. Why This Order Matters

The old thread was good at cleanup, deletion, and owner recovery.
This new phase is different.

If the next thread jumps directly into implementation:

- it may blur mechanism doctrine with cleanup habit
- it may delete shells that should stay as future seams
- it may move responsibility without first naming the target owner clearly

This is why the next thread should be explicit, slower in framing, and smaller in each mechanism move.

## 5. Collaboration Method With Human

Human is system architect.
The next thread should work as supervised engineering support.

Recommended collaboration style:

1. Start each substantial turn by restating the exact slice.
2. Always name:
   - active owner
   - target file
   - fields / branches / formulas involved
3. Prefer static owner analysis before dynamic testing.
4. Keep suggestions concrete and narrow.
5. When a choice has doctrine consequences, stop and surface the tradeoff instead of auto-deciding.

### Response depth expectation

The next thread should not become too terse when speaking to Human.

If a note, audit, or shortlist is produced, the thread must not stop at:

- "document created"
- "see note"
- "this is aligned"

Instead, after creating or reading any document, explain in plain language:

1. what the note actually concludes
2. what changed in the current understanding
3. what is safe to do next
4. what is still not safe to touch yet

The Human should not need to reverse-engineer the real conclusion from the document alone.

### Mechanism explanation protocol

When Human asks what a mechanism or field means, answer in this order:

1. plain-language mechanism meaning
2. active owner / code-path truth
3. why it matters for the current decision
4. whether it is:
   - active core
   - transitional baggage
   - inactive shell
   - safe deletion candidate

Do not answer only with code references.
Do not answer only with abstract architecture language.
Combine both.

### Document handoff protocol

Whenever the thread writes a review note or audit note, follow it with a short spoken briefing to Human.

That briefing should include:

- the 2-4 most important conclusions
- one sentence on why those conclusions matter now
- one bounded next action recommendation

The point of the document is to anchor precision, not to replace explanation.

### Decision-support protocol

When a decision is needed from Human or Governance:

- present the decision in bounded terms
- explain the consequence of each reasonable option
- state your recommendation and why

Do not offload the whole analysis burden back to Human.
The thread should narrow the decision first.

### Tone and supervision protocol

The thread should behave like a careful engineering partner, not a detached summarizer.

That means:

- explain enough for Human to inspect confidently
- say explicitly what is verified versus inferred
- avoid hiding uncertainty behind compressed language
- keep the pace calm and structured
- do not confuse brevity with usefulness

Short answers are fine only when the question is truly short.
Mechanism-boundary questions usually need a little more explanation.

In practice:

- do not say "I cleaned this up"
- say exactly what becomes smaller or what ownership becomes truer
- do not call something dead unless the active maintained path was verified
- do not mix formation doctrine decisions with unrelated runtime/test_run/VIZ cleanup

## 6. Code Work Norms For PR #9

### Scope discipline

- Stay on `eng/dev-v2.1-formation-only`
- Work only in `E:/logh_sandbox`
- Do not create extra worktrees
- Keep `PR #9` as the review carrier

### Structural discipline

- Prefer subtraction over additive helper layering
- Avoid parameter-shuttling wrappers
- Do not broaden into general engine modernization
- Do not slip into viewer doctrine or unrelated test harness refactors

### Frozen-layer discipline

Do not edit frozen layers without explicit Human file-level approval.

### Testing discipline

Use dynamic runs only as validation of a narrowed hypothesis.
Do not treat smoke runs as a substitute for owner/path truth.

### Comments discipline

If comments are added:

- keep them light
- make ownership or seam status clearer
- avoid narrating history or governance inside code

## 7. Local Workspace Reality

Current local default experiment setting:

- [test_run_v1_0.runtime.settings.json](/e:/logh_sandbox/test_run/test_run_v1_0.runtime.settings.json)
  uses `36 / 36` initial fleet size

Treat this as current Human-approved local default for ongoing experiments.
Do not silently reinterpret it as a permanent baseline.

## 8. Success Standard

The thread succeeds if it produces:

- a clearer statement of what Formation still owns
- a bounded first subtraction slice
- a cleaner path toward locomotion responsibility separation

The thread does **not** need to finish the whole formation redesign in one pass.

## 9. Final Guidance To The New Thread

Do not inherit the old thread's cleanup reflex blindly.

Use the old thread's strengths:

- careful owner truth
- subtraction-first discipline
- explicit scope control

But apply them to a different job:

- mechanism boundary clarification
- formation scope reduction
- preparation for later locomotion separation
