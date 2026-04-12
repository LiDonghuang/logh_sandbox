# Step3 / PR6 Cleanup Stage Methodology and Lessons

Status: methodology record  
Scope: cleanup method, failure/repair lessons, and reusable operating rules  
Authority: local engineering record, not canonical governance authority

## 1. Why this record exists

This cleanup stage became the largest subtraction-first cleanup in the project so far.

It touched:

- runtime active movement ownership
- `test_run` maintained mainline ownership
- `battle` / `neutral` movement-family alignment
- public settings truth surfaces
- old `2D` / `v3a` / report / viz residue

The main value of the stage is not only the resulting code shrink.
It is also the method that finally worked after multiple failed rounds.

## 2. Highest-value method lessons

### A. Static owner audit must come before dynamic probing

The most important operational lesson is:

- first identify the active owner
- then identify transitional carriers
- then identify stale public surfaces
- only after that run dynamic tests

Dynamic reads were useful, but they repeatedly misled the thread when they were asked before code-path truth was established.

For this codebase, static audit must answer:

- which file actually owns the active behavior
- whether a value is active or merely legacy-named
- whether a bridge/carrier is transitional or semantic
- whether a comment/setting still tells the truth

### B. Human-confirmed good/bad windows are higher trust than guessed chronology

Chronology notes and commit timing were repeatedly over-read as causality.

What worked better:

- use the Human-confirmed regression window as the main anchor
- perform subtraction-first isolation one mechanism group at a time
- avoid “it must have started in that old note/commit” reasoning unless code-path verification exists

### C. Battle/neutral consistency must be treated as a design invariant

The cleanup made one principle much clearer:

- `battle` and `neutral` should share the same maintained `v4a` movement mechanism family
- the only allowed semantic difference is objective source

This principle was useful because it prevented two bad moves:

- “fixing” neutral by reviving neutral-only legacy movement
- “fixing” battle by spreading battle-only early shaping into a new shared doctrine without first proving it belongs

### D. Cleanup must prefer deletion over bridge-building

What actually worked was visible subtraction:

- delete legacy surfaces
- remove mixed-era settings keys
- narrow readout surfaces
- reroot honest owners
- keep the caller smaller

What repeatedly caused trouble was additive “cleanup”:

- helper layers that only move parameters
- silent fallback scaffolding
- temporary wrappers that become permanent
- duplicated owner logic in harness and runtime

### E. Truth-surface cleanup is part of mechanism cleanup

A mechanism is not really cleaned up if:

- settings still advertise the old path
- comments still describe retired behavior
- summary/debug surfaces still imply old ownership

This stage showed that owner cleanup must travel together with:

- settings comments
- settings reference text
- README/repo context/system map
- explicit mistake records when a cleanup deleted something still active

## 3. Most important technical lessons

### A. `restore_strength` had to become direct

The successful cleanup read for active `v4a` restore was:

- `restore_term = restore_strength * normalize(restore_vector)`

The key lesson was not “recover the old number.”
The key lesson was:

- do not reintroduce old personality multipliers
- do not hide a new internal scale
- make the public knob itself the honest definition

### B. Neutral old movement had to be deleted, not preserved

Neutral initially still carried:

- old fixture-only semantics
- neutral-specific relation semantics
- mode-gated runtime entry behavior

The useful move was:

- delete neutral’s old movement ownership
- let neutral use battle’s maintained movement family
- keep only a neutral-specific termination semantic (`stop_radius`)

### C. Shared carriers matter more than historical names

Several names looked old, but the real question was:

- is this still an active seam?

This matters because some “old-looking” paths were still active contracts and should not be silently deleted or renamed, while some newer-looking surfaces were already dead or misleading.

The lesson:

- judge by active ownership, not by naming age

### D. A cleanup slice should remove one mechanism family at a time

The best slices in this stage were bounded:

- direct restore seam cleanup
- neutral/battle movement-family alignment
- settings/readout narrowing
- `v3a` support-surface retirement
- removal of 2D viz / BRF / report artifacts
- removal of selector-driven `v2/v3_test` public switching

The worst moments were when several speculative theories were mixed in one move.

## 4. Mistakes that should be remembered

### A. Misdiagnosing by chronology

Earlier rounds repeatedly over-attributed root cause to older notes/commits without proving the active code path.

That should be treated as a known failure mode.

### B. Silent overreach during cleanup

Several wrong turns came from treating cleanup as permission to:

- change semantics while renaming
- add new shared meaning to old terms
- make neutral and battle meet “in the middle”

This stage worked only after cleanup returned to:

- subtraction-first
- honest owner rerooting
- one-group-at-a-time scope

### C. Deleting a surface without checking the active reader

`visualization.display_language` was incorrectly removed because it looked like a dead 2D/BRF surface.

In reality, 3D still used it through:

- `viz3d_panda/replay_source.py`

This should remain a standing warning:

- do not delete a settings surface until every active reader is checked

## 5. Reusable cleanup method for future rounds

For the next cleanup phases, the recommended default sequence is:

1. pick one mechanism family  
2. identify active owner(s)  
3. identify transitional carriers / bridges  
4. identify stale settings/readout/comment surfaces  
5. delete or reroot in the smallest honest slice  
6. update truth surfaces immediately  
7. run minimal relevant checks  
8. record what was deleted, what remained, and why

## 6. Guidance for future new mechanism development

Future mechanism work should take the opposite lesson from earlier failures:

- do not let harness-side experimentation silently become permanent ownership
- do not let new knobs arrive before owner truth is clear
- do not add battle-only shaping unless it is clearly intended as shared doctrine or clearly bounded as battle-only semantics
- prefer direct public semantics over hidden multiplier chains
- define where the mechanism lives before tuning it

## 7. Current cleanup-stage read

At the end of this stage:

- active maintained movement baseline is `v4a`
- active `v4a` restore is direct and single-owned
- `battle` / `neutral` now read through the same maintained movement family
- old 2D viz / BRF / maintained `v3a` execution surfaces are being retired in visible slices
- the project now has a workable cleanup methodology that is more reliable than the earlier ad hoc debugging style

That methodology should be reused for:

- remaining old-family retirement
- cohesion seam cleanup
- future mainline structural cleanup
- any later new mechanism line
